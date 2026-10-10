"""Tests for patch_master_workbook.py (the one-time fixes for the master workbook).

The master workbook is not in the repository, so these tests build stand-ins:
  - a workbook holding exactly the cells the audit found, to test the guarded patching;
  - a small workbook with the Input / Analysis / Reference Data cells the fixed formulas use,
    recalculated in LibreOffice, to test what the formulas compute.

Run:  python3 -m unittest test_patch_master_workbook
"""
import datetime
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import openpyxl

import patch_master_workbook as pm

SOFFICE = shutil.which("soffice") or shutil.which("libreoffice")


def audit_state_workbook():
    """Every patched cell holding what the audit found (other cells empty)."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    parts = {}
    for p in pm.PATCHES:
        ws = wb[p.sheet] if p.sheet in wb.sheetnames else wb.create_sheet(p.sheet)
        if p.part:
            parts.setdefault((p.sheet, p.cell), []).append(p.old)
        elif p.old is not None:
            ws[p.cell] = p.old
    for (sheet, cell), olds in parts.items():
        wb[sheet][cell] = "=IF(1," + " & ".join(olds) + ")" if olds[0].startswith(("AND(", "ROUND(")) else "x " + " … ".join(olds) + " y"
    return wb


class GuardedPatching(unittest.TestCase):
    def test_every_cell_is_fixed_once_and_a_rerun_changes_nothing(self):
        wb = audit_state_workbook()
        first = pm.apply_patches(wb)
        self.assertEqual({s for s, _, _ in first}, {"fixed"})
        for p in pm.PATCHES:
            v = wb[p.sheet][p.cell].value
            if p.part:
                self.assertIn(p.new, v)
                self.assertNotIn(p.old, v)
            else:
                self.assertEqual(v, p.new)
        again = pm.apply_patches(wb)
        self.assertEqual({s for s, _, _ in again}, {"already fixed"})

    def test_a_cell_you_changed_is_skipped_and_left_alone(self):
        wb = audit_state_workbook()
        wb["Reference Data"]["T6"] = "My own wording for Simha"
        res = {(p.sheet, p.cell): s for s, p, _ in pm.apply_patches(wb)}
        self.assertEqual(res[("Reference Data", "T6")], "skipped")
        self.assertEqual(wb["Reference Data"]["T6"].value, "My own wording for Simha")
        self.assertEqual(res[("Reference Data", "T5")], "fixed")

    def test_sessions_24_to_27_patches(self):
        wb = audit_state_workbook()
        pm.apply_patches(wb)
        bi, pp, pc, pl = wb["Bhava Info"], wb["Planet Profile"], wb["Planet Characteristics"], wb["Planets"]
        self.assertEqual(bi["D16"].value, "Ketu, Saturn")                                # S25: Saturn, karaka of the 12th
        self.assertTrue(bi["C7"].value.endswith(", hands"))
        self.assertEqual(bi["C13"].value, "Thighs, buttocks")
        self.assertEqual(bi["C15"].value, "Legs, calves, shins; left ear")
        self.assertTrue(bi["E11"].value.endswith(", maternal grandmother"))
        for ws, sun, moon, merc in ((pp, "X5", "X6", "X8"), (pc, "B35", "C35", "E35")):
            self.assertTrue(ws[sun].value.startswith("Mild malefic (S26)"))
            self.assertTrue(ws[moon].value.startswith("Natural benefic (S26); waxing = stronger"))
            self.assertTrue(ws[merc].value.startswith("Natural benefic (S26)"))
        self.assertIn("brothers and male friends", pp["Q7"].value)
        self.assertIn("Athlete", pc["D29"].value)
        self.assertIn("Astrologer", pp["R8"].value)
        self.assertIn("food, travel and change of place", pl["D6"].value)
        self.assertIn("astrology", pl["D8"].value)

    def test_missing_sheet_is_reported(self):
        wb = audit_state_workbook()
        del wb["Guide & Explanations"]
        res = [s for s, p, _ in pm.apply_patches(wb) if p.sheet == "Guide & Explanations"]
        self.assertEqual(res, ["no sheet"])

    def test_backup_dry_run_and_rerun_on_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d, "Classification_for_Horoscope_Analysis_v7_1.xlsx")
            audit_state_workbook().save(path)
            before = path.read_bytes()
            backup, res = pm.patch_master(path, dry_run=True)
            self.assertIsNone(backup)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(pathlib.Path(d, "backups").exists())
            backup, res = pm.patch_master(path)
            self.assertEqual(backup.parent, pathlib.Path(d, "backups"))
            self.assertEqual(backup.read_bytes(), before)
            self.assertTrue(all(s == "fixed" for s, _, _ in res))
            backup2, res2 = pm.patch_master(path)
            self.assertIsNone(backup2)                                   # nothing to change: no new backup
            self.assertEqual(len(list(pathlib.Path(d, "backups").iterdir())), 1)

    def test_array_formula_counts_become_plain_formulas(self):
        from openpyxl.worksheet.formula import ArrayFormula
        wb = audit_state_workbook()
        old = next(p for p in pm.PATCHES if p.cell == "B64")
        wb["Analysis"]["B64"] = ArrayFormula("B64", old.old)
        pm.apply_patches(wb)
        self.assertIsInstance(wb["Analysis"]["B64"].value, str)
        self.assertIn("COUNTIFS('Reference Data'!$A$2:$A$13,Input!C13:C21", wb["Analysis"]["B64"].value)


# ---- what the fixed formulas compute (LibreOffice) -------------------------------------------
SIGNS = [("Mesha", "Aries", "Chara", "Agni", "Kshatriya"), ("Vrishaba", "Taurus", "Sthira", "Prithvi", "Vysya"),
         ("Mithuna", "Gemini", "Dwisabhava", "Vayu", "Shudra"), ("Karkataka", "Cancer", "Chara", "Jala", "Brahmin"),
         ("Simha", "Leo", "Sthira", "Agni", "Kshatriya"), ("Kanya", "Virgo", "Dwisabhava", "Prithvi", "Vysya"),
         ("Tula", "Libra", "Chara", "Vayu", "Shudra"), ("Vrischika", "Scorpio", "Sthira", "Jala", "Brahmin"),
         ("Dhanur", "Sagittarius", "Dwisabhava", "Agni", "Kshatriya"), ("Makara", "Capricorn", "Chara", "Prithvi", "Vysya"),
         ("Kumbha", "Aquarius", "Sthira", "Vayu", "Shudra"), ("Meena", "Pisces", "Dwisabhava", "Jala", "Brahmin")]
NAKS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"]
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# The unchanged master formulas the fixed ones read (Analysis rows 37 and 84-93).
ORIGINAL = {
    "B37": "=IF(Input!C14=\"\",\"\",INDEX('Reference Data'!H$2:H$13,Input!C14))",
    "C37": '=IF(B37="","",IF(B37="Brahmin","Brahmin Moon: knowledge.",IF(B37="Kshatriya","Kshatriya Moon: leadership.",'
           'IF(B37="Vaishya","Vaishya Moon: trade.","Shudra Moon: service."))))',
    "B80": '=IF(Input!G14="","",IF(OR(Input!G14="⬇ Debilitated",ISNUMBER(SEARCH("Krishna",Tithi!G10))),"Remedy","—"))',
    "B84": '=IF(OR(Input!C12="",Input!C15=""),"",MOD(Input!C15-Input!C12,12)+1)',
    "B85": '=IF(OR(Input!C18="",Input!C15=""),"",MOD(Input!C15-Input!C18,12)+1)',
    "B86": '=IF(OR(Input!C14="",Input!C15=""),"",MOD(Input!C15-Input!C14,12)+1)',
    "C84": '=IF(B84="","",IF(OR(B84=2,B84=4,B84=7,B84=8,B84=12),"⚠ YES","— No"))',
    "C85": '=IF(B85="","",IF(OR(B85=2,B85=4,B85=7,B85=8,B85=12),"⚠ YES","— No"))',
    "C86": '=IF(B86="","",IF(OR(B86=2,B86=4,B86=7,B86=8,B86=12),"⚠ YES","— No"))',
    "B91": '=IF(Input!C12="","",IF(OR(Input!C12=4,Input!C12=5),"✅ Cancelled","❌ Not Met"))',
    "B93": '=IF(Input!B5="","",IF((TODAY()-Input!B5)/365.25>=28,"✅ Reduced","❌ Not Met (under 28)"))',
}


def calc_workbook(chart):
    """The cells the fixed formulas use, filled for `chart`, with the audit-state formulas, then patched."""
    wb = openpyxl.Workbook()
    inp = wb.active
    inp.title = "Input"
    ref, nak, tithi = wb.create_sheet("Reference Data"), wb.create_sheet("Nakshatras"), wb.create_sheet("Tithi")
    an = wb.create_sheet("Analysis")
    for i, (name, eng, mode, tatwa, varna) in enumerate(SIGNS, 2):
        ref[f"A{i}"], ref[f"B{i}"], ref[f"C{i}"], ref[f"E{i}"], ref[f"F{i}"], ref[f"H{i}"] = i - 1, name, eng, mode, tatwa, varna
    for i, n in enumerate(NAKS, 5):
        nak[f"B{i}"] = n
    tithi["G10"] = chart.get("paksha", "Shukla Paksha (Waxing) — Strong, Benefic")
    inp["B5"] = chart.get("dob", datetime.datetime(2015, 1, 1))
    for r, key in enumerate(["Lagna"] + PLANETS, 12):
        s = chart["signs"].get(key)
        inp[f"B{r}"] = f"{SIGNS[s - 1][0]} - {SIGNS[s - 1][1]}" if s else None
        inp[f"C{r}"] = f"=IF(B{r}=\"\",\"\",MATCH(LEFT(B{r},FIND(\" - \",B{r})-1),'Reference Data'!B$2:B$13,0))"
        inp[f"E{r}"] = chart.get("degs", {}).get(key, 10.0)
    inp["G14"], inp["G15"] = chart.get("G14", "—"), chart.get("G15", "—")
    for cell, f in ORIGINAL.items():
        an[cell] = f
    for p in pm.PATCHES:                        # the audit-state text of every cell these sheets hold
        if p.sheet in ("Analysis", "Input") and not p.part and p.old is not None and p.cell not in ("E11",) and not p.cell.startswith("G"):
            wb[p.sheet][p.cell] = p.old
    an["B46"] = '=IF(Input!C14="","","House "&Input!D14)'
    res = pm.apply_patches(wb, [p for p in pm.PATCHES if p.sheet in ("Analysis", "Input") and not p.cell.startswith(("G", "E"))])
    assert all(s == "fixed" for s, _, _ in res), [(s, p.cell) for s, p, _ in res if s != "fixed"]
    return wb


@unittest.skipUnless(SOFFICE, "LibreOffice not installed — formula results not checked")
class FixedFormulasCompute(unittest.TestCase):
    CHARTS = {
        # the audit's example: no dosha anywhere, though Mars is in its own sign (old verdict: CANCELLED)
        "no_dosha": {"signs": dict({p: 1 for p in PLANETS}, Lagna=1, Ketu=7)},
        # Mars 2nd from Vrishabha Lagna in Mercury's Mithuna; Saturn in Dhanus aspects it (7th): rule 3
        "saturn": {"signs": dict({p: 1 for p in PLANETS}, Lagna=2, Mars=3, Saturn=9, Venus=4, Moon=5, Ketu=7),
                   "degs": {"Moon": 20.0}},
        # Mars in Meena (Jupiter's, a friend), 12th from Mesha Lagna: rule 1
        "friend": {"signs": dict({p: 1 for p in PLANETS}, Lagna=1, Mars=12, Saturn=2, Venus=5, Moon=5, Ketu=7),
                   "degs": {"Moon": 20.0}},
        # Moon at 3° Mesha = Ashwini, an exempt nakshatra: rule 3
        "nakshatra": {"signs": dict({p: 1 for p in PLANETS}, Lagna=2, Mars=3, Saturn=2, Venus=4, Moon=1, Ketu=7),
                      "degs": {"Moon": 3.0}},
        # Saturn's aspect cancels even when no degrees are entered
        "saturn_no_degrees": {"signs": dict({p: 1 for p in PLANETS}, Lagna=2, Mars=3, Saturn=9, Venus=4, Moon=5, Ketu=7),
                              "degs": {p: None for p in ["Lagna"] + PLANETS}},
        # no cancellation, and the Moon's degree is missing: the verdict asks for it
        "present_no_degree": {"signs": dict({p: 1 for p in PLANETS}, Lagna=2, Mars=3, Saturn=2, Venus=4, Moon=5, Ketu=7),
                              "degs": {"Moon": None}},
        # dosha present, nothing cancels, native under 28
        "present": {"signs": dict({p: 1 for p in PLANETS}, Lagna=2, Mars=3, Saturn=2, Venus=4, Moon=5, Ketu=7),
                    "degs": {"Moon": 20.0}},
        # blank Lagna: no #VALUE! anywhere
        "blank_lagna": {"signs": dict({p: 1 for p in PLANETS}, Lagna=None, Ketu=7)},
        # Moon in Vrishabha, deep-debilitated Moon label
        "moon": {"signs": dict({p: 1 for p in PLANETS}, Lagna=1, Moon=2, Ketu=7), "G14": "💔 Deep Debilitated (3° Vrischika)"},
    }

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = pathlib.Path(cls.tmp.name)
        for name, chart in cls.CHARTS.items():
            calc_workbook(chart).save(d / f"{name}.xlsx")
        prof = (d / "profile").resolve()
        subprocess.run([SOFFICE, f"-env:UserInstallation={prof.as_uri()}", "--headless", "--convert-to", "xlsx",
                        "--outdir", str(d / "out")] + [str(d / f"{n}.xlsx") for n in cls.CHARTS],
                       capture_output=True, timeout=300)
        cls.v = {}
        for name in cls.CHARTS:
            wb = openpyxl.load_workbook(d / "out" / f"{name}.xlsx", data_only=True)
            cls.v[name] = {f"{s}!{c}": wb[s][c].value for s in ("Analysis", "Input")
                           for c in [f"{col}{r}" for col in "ABCD" for r in range(1, 100)]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_no_dosha_is_not_reported_as_cancelled(self):
        self.assertEqual(self.v["no_dosha"]["Analysis!B94"], "✅ No Kuja Dosha from any reference point.")

    def test_modality_and_element_counts(self):
        v = self.v["no_dosha"]
        self.assertEqual([v[f"Analysis!B{r}"] for r in (64, 65, 66, 68, 69, 70, 71)], [9, 0, 0, 8, 0, 1, 0])
        v = self.v["saturn"]          # Mesha x5, Vrishabha (Lagna not counted), Mithuna, Karka, Simha, Dhanus, Tula
        self.assertEqual([v[f"Analysis!B{r}"] for r in (64, 65, 66)], [6, 1, 2])

    def test_saturn_aspect_cancels(self):
        v = self.v["saturn"]
        self.assertEqual((v["Analysis!C84"], v["Analysis!B92"]), ("⚠ YES", "✅ Cancelled"))
        self.assertEqual(v["Analysis!B94"], "✅ Kuja Dosha present but CANCELLED by rule 2.")
        self.assertIn("casts its 7th aspect on Mars", v["Analysis!C92"])
        self.assertEqual(v["Analysis!D84"], "Strong (Lagna gives the strongest impact)")

    def test_friends_house_cancels(self):
        v = self.v["friend"]
        self.assertEqual(v["Analysis!B90"], "✅ Cancelled")
        self.assertEqual(v["Analysis!B94"], "✅ Kuja Dosha present but CANCELLED by rule 1.")
        self.assertIn("a friend's house", v["Analysis!C90"])

    def test_exempt_nakshatra_cancels(self):
        v = self.v["nakshatra"]
        self.assertEqual(v["Analysis!B92"], "✅ Cancelled")
        self.assertIn("Rule 4 — birth nakshatra: Ashwini — exempt", v["Analysis!C92"])
        self.assertEqual(v["Analysis!B94"], "✅ Kuja Dosha present but CANCELLED by rule 4.")

    def test_saturn_rule_does_not_need_the_moons_degree(self):
        v = self.v["saturn_no_degrees"]
        self.assertEqual(v["Analysis!B92"], "✅ Cancelled")
        self.assertEqual(v["Analysis!B94"], "✅ Kuja Dosha present but CANCELLED by rule 2.")
        self.assertIn("enter the Moon's sign and degree", v["Analysis!C92"])

    def test_missing_moon_degree_is_asked_for(self):
        v = self.v["present_no_degree"]
        self.assertEqual(v["Analysis!B92"], "ℹ Needs the Moon's degree")
        self.assertIn("Enter the Moon's degree to check rule 4", v["Analysis!B94"])

    def test_present_and_not_cancelled(self):
        v = self.v["present"]
        self.assertTrue(v["Analysis!B94"].startswith("⚠ Kuja Dosha present and not cancelled by rules 1–4."))
        self.assertIn("check rule 5", v["Analysis!B94"])
        self.assertIn("not exempt", v["Analysis!C92"])

    def test_blank_lagna_gives_blanks_not_errors(self):
        v = self.v["blank_lagna"]
        self.assertEqual({v[f"Input!D{r}"] or "" for r in range(13, 22)}, {""})       # blank, not #VALUE!
        self.assertEqual(v["Analysis!B46"] or "", "")
        self.assertEqual(v["Analysis!B94"] or "", "")

    def test_vysya_moon_and_deep_debilitated_moon(self):
        v = self.v["moon"]
        self.assertEqual(v["Analysis!C37"], "Vaishya Moon: trade.")
        self.assertEqual(v["Analysis!B80"], "Remedy")


if __name__ == "__main__":
    unittest.main()
