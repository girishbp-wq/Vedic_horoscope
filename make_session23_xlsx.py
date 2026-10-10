#!/usr/bin/env python3
"""The Session 23 calculator sheets, and how they get into the master workbook.

    python3 make_session23_xlsx.py --install              # add the S23_ sheets to Classification_for_Horoscope_Analysis_v7_1.xlsx
    python3 make_session23_xlsx.py --install --reset-data # ... and overwrite the S23_ data sheets from session23_rules.json
    python3 make_session23_xlsx.py --export [FILE]        # a standalone workbook (default Session23_Rules.xlsx)

--install keeps a backup of the master (…before-session23-DATE.xlsx), adds the data sheets only when they are not
there yet (your edits are never overwritten unless you say --reset-data) and rebuilds the calculator sheets.

Calculator sheets (all formulas — change the signs on S23_Chart and everything recalculates):

  S23_Chart         inputs: Lagna, the nine grahas' signs and degrees, birth date-time, "now"
  S23_Classes_Calc  the ten class tables (house, rāśi, planets, lord, where the lord sits), the house x class matrix,
                    the Badhaka block and the twelve house lords
  S23_Roles_Calc    Maraka / Badhaka / Dusthana / Trishadaya roles of the nine grahas
  S23_Dasha_Calc    Vimśottarī: nine Mahādaśās and 81 Bhuktis from the Moon's longitude, and the running pair
  S23_Predict_Calc  graha + bhāva: house, nature, the cell text, dignity, digbala, classes and class-rule texts
  S23_Ref_Calc      lookup tables copied from the page (rāśi table, dignity degrees and grid, daśā constants)

The text rows are looked up in the S23_ data sheets (GrahaInBhava, ClassRules, DignityEffect, Digbala), so editing a
curated text there changes the calculator at once.  Python (bhava_rules.py) and the page (index.html) are tested
against these formulas in test_session23_cross_impl.py.
"""
import datetime
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

import build_session23 as b23
import bhava_rules as br

ROOT = pathlib.Path(__file__).resolve().parent
PREFIX = b23.PREFIX
JSON_PATH = ROOT / "session23_rules.json"
CALC_NAMES = ["Chart", "Classes_Calc", "Roles_Calc", "Dasha_Calc", "Predict_Calc", "LifeArea_Calc", "Ref_Calc"]
CALC_SHEETS = [PREFIX + n for n in CALC_NAMES]

# ---- layout contract (used by the tests) -------------------------------------------------------
LAGNA_CELL, PLANET_ROW0 = "B3", 5            # Chart: Lagna sign; planets in rows 5-13 (name, sign, degree, sign #, house)
MOON_LON_CELL, SUN_LON_CELL, WAXING_CELL = "B15", "B16", "B17"
BIRTH_CELL, NOW_CELL = "B18", "B19"
GENDER_CELL, AGE_CELL = "B20", "B21"          # Chart: Male / Female / blank; age in years at "Now"
RETRO_COL = 6                                # Chart: column F, "yes" for a retrograde planet (rows 5-13)
DASHA_RUNNING_CELL = "B11"                   # Dasha_Calc: TRUE when "Now" falls inside the 120-year span
CLASS_ROW0, CLASS_ROWS = 4, 33               # Classes_Calc: class tables (header row 3)
BADHAKA_ROW = 40                             # B mode, C house, D rāśi, E lord, F occupants (header row 39)
MATRIX_ROW0 = 44                             # header row; houses 1-12 in the next twelve rows
HOUSELORD_ROW0 = 61                          # twelve rows: house, rāśi, lord (header row 57)
ROLES_ROW0 = 3                               # Roles_Calc (header row 2)
DASHA_ROW0, DASHA_CUR_ROW = 24, 8            # Dasha_Calc: 81 Bhukti rows; running Mahādaśā in B8, Bhukti in B9
PREDICT_ROW0 = 3                             # Predict_Calc (header row 2); 9 planets
PREDICT_COLS = dict(planet=1, house=2, nature=3, status=4, points=5, dignity=6, dignity_line=7,
                    digbala_line=8, classes=9, class_texts=10, extra=11,
                    moon_strength=15, nature_lines=16, twelfth_line=17, conditions=18, active=19)
COMBUST_COL, AFFLICTED_COL, MILD_COL = 20, 21, 22   # Predict_Calc helper columns
FLAG_ROW0 = 16                               # Predict_Calc: class-rule flags, one row per planet (header row 15)
NATURE_FLAG_ROW0 = 28                        # Predict_Calc: Session 26 line flags, one row per planet (header row 27)
COND_ROW0 = 40                               # Predict_Calc: conditional readings, one row per candidate (header row 39)
# LifeArea_Calc (Session 27's 7 steps for the area chosen in B2); life_area_from_sheet() reads it back.
AREA_CELL = "B2"
REF_SIGNLINE_COL, REF_BHAVA_COL0 = 39, 41    # Ref_Calc: sign line per sign; house, short name, significations, people, body
HELP_ROW0 = 3                                # LifeArea_Calc: per-planet helper table in columns AA.. (header row 2)
BLOCK_ROW0, BLOCK_ROWS = 20, 75              # LifeArea_Calc: one block of 75 rows per house of the area (two blocks)
KARAKA_ROW0 = BLOCK_ROW0 + 2 * BLOCK_ROWS + 1
PAC_ROW0 = KARAKA_ROW0 + 3
LINK_ROW0 = PAC_ROW0 + 9
SUPPORT_COL, PRESSURE_COL = 19, 20

HEAD_FILL = PatternFill("solid", fgColor="6B1D2B")
HEAD_FONT = Font(bold=True, color="FFFFFF")
INPUT_FILL = PatternFill("solid", fgColor="FFF3D6")
WRAP = Alignment(wrap_text=True, vertical="top")
DATE_FMT = "yyyy-mm-dd hh:mm"


def _rules(path=None):
    return br.load_rules(path or JSON_PATH)


def _head(ws, row, labels, col0=1):
    for j, text in enumerate(labels):
        c = ws.cell(row=row, column=col0 + j, value=text)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
        c.alignment = Alignment(wrap_text=True, vertical="center")


def _ord(x):
    """Excel text expression for the ordinal of cell/expression x (1st, 2nd, 3rd, 4th …)."""
    return (f'{x}&IF(AND(MOD({x},100)>=11,MOD({x},100)<=13),"th",'
            f'CHOOSE(MOD({x},10)+1,"th","st","nd","rd","th","th","th","th","th","th"))')


def _planet_cells(k):
    return dict(name=f"S23_Chart!$A${PLANET_ROW0 + k}", sign=f"S23_Chart!$D${PLANET_ROW0 + k}",
                deg=f"S23_Chart!$C${PLANET_ROW0 + k}", house=f"S23_Chart!$E${PLANET_ROW0 + k}")


def _planets_in(house_expr):
    """Excel text: the planets whose house equals house_expr, joined by ', ' (empty string when none)."""
    parts = "&".join(f'IF(S23_Chart!$E${PLANET_ROW0 + k}={house_expr},S23_Chart!$A${PLANET_ROW0 + k}&", ","")' for k in range(9))
    return parts


# ---- Ref_Calc ----------------------------------------------------------------------------------
def _ref_sheet(ws, rules):
    ref = rules["reference"]
    ws["A1"] = "Lookup tables copied from index.html (do not edit — rebuild with make_session23_xlsx.py)"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    _head(ws, 2, ["Sign #", "Rāśi", "English", "Lord", "Mode"])
    for i, r in enumerate(ref["RASHI"]):
        for j, v in enumerate([i, r["sanskrit"], r["english"], r["lord"], r["mode"]]):
            ws.cell(row=3 + i, column=1 + j, value=v)
    _head(ws, 2, ["Graha"], col0=7)
    for k, p in enumerate(br.PLANET_ORDER):
        ws.cell(row=3 + k, column=7, value=p)
    _head(ws, 2, ["Graha", "Exalt rāśi", "Exalt °", "Debil rāśi", "Debil °", "MT rāśi", "MT from °", "MT to °"], col0=9)
    for k, p in enumerate(br.PLANET_ORDER):
        ws.cell(row=3 + k, column=9, value=p)
        dd = ref["DIGNITY_DEG"].get(p)
        if dd:
            for j, v in enumerate([dd["exR"], dd["exD"], dd["deR"], dd["deD"], dd["mtR"], dd["mt"][0], dd["mt"][1]]):
                ws.cell(row=3 + k, column=10 + j, value=v)
    _head(ws, 2, [f"sign {s}" for s in range(12)], col0=18)
    for k, p in enumerate(br.PLANET_ORDER):
        for s in range(12):
            ws.cell(row=3 + k, column=18 + s, value=br.dignity(rules, p, s, None)["label"])
    _head(ws, 2, ["Class"], col0=31)
    for i, name in enumerate(br.CLASS_ORDER):
        ws.cell(row=3 + i, column=31, value=name)
    _head(ws, 2, ["Daśā order", "Years"], col0=33)
    for i, p in enumerate(ref["VORDER"]):
        ws.cell(row=3 + i, column=33, value=p)
        ws.cell(row=3 + i, column=34, value=ref["VYEARS"][p])
    _head(ws, 2, ["Nakṣatra", "Lord"], col0=36)
    for i, (name, lord) in enumerate(ref["NAKSHATRAS"]):
        ws.cell(row=3 + i, column=36, value=name)
        ws.cell(row=3 + i, column=37, value=lord)
    _head(ws, 2, ["Sign line (S27)"], col0=REF_SIGNLINE_COL)
    for i in range(12):
        ws.cell(row=3 + i, column=REF_SIGNLINE_COL, value=br.sign_line(rules, i))
    _head(ws, 2, ["House", "Name", "Significations", "People", "Body"], col0=REF_BHAVA_COL0)
    for h in range(1, 13):
        b = ref["BHAVA_INFO"][str(h)]
        for j, v in enumerate([h, br._short_name(b["nm"]), br._clean(b["sig"]), b["rel"], b["body"]]):
            ws.cell(row=2 + h, column=REF_BHAVA_COL0 + j, value=v)
    for c in range(1, 46):
        ws.column_dimensions[L(c)].width = 14


# ---- Chart ---------------------------------------------------------------------------------------
def _chart_sheet(ws, rules):
    ws["A1"] = "Session 23 calculator — set the Lagna and the grahas' signs and degrees; the other sheets recalculate"
    ws["A1"].font = Font(bold=True, size=13, color="6B1D2B")
    ws["A3"] = "Lagna (rising sign)"
    ws[LAGNA_CELL] = "Simha"
    ws["D3"] = '=MATCH(B3,S23_Ref_Calc!$B$3:$B$14,0)-1'
    _head(ws, 4, ["Graha", "Sign", "Degree in sign", "Sign # (0-11)", "House from Lagna"])
    sample = {"Moon": 6, "Ketu": 7, "Saturn": 9, "Jupiter": 10, "Mars": 3, "Sun": 2, "Venus": 2, "Mercury": 1, "Rahu": 1}
    names = [r["sanskrit"] for r in rules["reference"]["RASHI"]]
    for k, p in enumerate(br.PLANET_ORDER):
        r = PLANET_ROW0 + k
        ws.cell(row=r, column=1, value=p)
        ws.cell(row=r, column=2, value=names[sample[p]])
        ws.cell(row=r, column=3, value=15)
        ws.cell(row=r, column=4, value=f"=MATCH(B{r},S23_Ref_Calc!$B$3:$B$14,0)-1")
        ws.cell(row=r, column=5, value=f"=MOD(D{r}-$D$3,12)+1")
        for col in (2, 3):
            ws.cell(row=r, column=col).fill = INPUT_FILL
    ws["B3"].fill = INPUT_FILL
    moon, sun = PLANET_ROW0 + 1, PLANET_ROW0
    ws["A15"], ws[MOON_LON_CELL] = "Moon longitude (°)", f"=D{moon}*30+C{moon}"
    ws["A16"], ws[SUN_LON_CELL] = "Sun longitude (°)", f"=D{sun}*30+C{sun}"
    ws["A17"], ws[WAXING_CELL] = "Moon waxing (Shukla paksha)?", "=INT(MOD(B15-B16,360)/12)+1<=15"
    ws["A18"], ws[BIRTH_CELL] = "Born (date and time)", datetime.datetime(1990, 5, 15, 6, 30)
    ws["A19"], ws[NOW_CELL] = "Now (overwrite to freeze)", "=NOW()"
    for c in (BIRTH_CELL, NOW_CELL):
        ws[c].number_format, ws[c].fill = DATE_FMT, INPUT_FILL
    ws["A20"], ws[GENDER_CELL] = "Gender (Male / Female / blank)", None
    ws[GENDER_CELL].fill = INPUT_FILL
    ws["A21"], ws[AGE_CELL] = "Age at 'Now' (years)", f"=({NOW_CELL}-{BIRTH_CELL})/365.25"
    ws[AGE_CELL].number_format = "0.00"
    ws.cell(row=4, column=RETRO_COL, value="Retrograde? (yes / blank)").fill = HEAD_FILL
    ws.cell(row=4, column=RETRO_COL).font = HEAD_FONT
    for k in range(9):
        ws.cell(row=PLANET_ROW0 + k, column=RETRO_COL).fill = INPUT_FILL
    ws["A23"] = ("Yellow cells are inputs. The Lagna and signs have drop-downs (page spelling). "
                 "Houses count from the Lagna sign. Enter each degree as the degree within its sign (0 to under 30), "
                 "not the absolute longitude; degrees decide Deep Exalted / Deep Debilitated and Moolatrikona. "
                 "Gender and the retrograde column feed the Sessions 24-27 readings (S23_Predict_Calc, S23_LifeArea_Calc).")
    ws["A23"].alignment = WRAP
    sex = DataValidation(type="list", formula1='"Male,Female"', allow_blank=True, showErrorMessage=True,
                         errorTitle="Gender", error="Choose Male or Female, or leave the cell empty.")
    ws.add_data_validation(sex)
    sex.add(GENDER_CELL)
    yes = DataValidation(type="list", formula1='"yes"', allow_blank=True, showErrorMessage=True,
                         errorTitle="Retrograde", error="Type yes for a retrograde planet, or leave the cell empty.")
    ws.add_data_validation(yes)
    yes.add(f"{L(RETRO_COL)}{PLANET_ROW0}:{L(RETRO_COL)}{PLANET_ROW0 + 8}")
    dv = DataValidation(type="list", formula1="=S23_Ref_Calc!$B$3:$B$14", allow_blank=False,
                        showErrorMessage=True, errorTitle="Pick a rashi from the list",
                        error="Choose the sign from the drop-down — the list's spelling is the one the formulas look up.")
    ws.add_data_validation(dv)
    dv.add("B3")
    dv.add(f"B{PLANET_ROW0}:B{PLANET_ROW0 + 8}")
    deg = DataValidation(type="decimal", operator="between", formula1="0", formula2="29.999999", allow_blank=False,
                         showErrorMessage=True, errorTitle="Degree within the sign",
                         error="Enter the degree inside the sign: 0 up to (but not including) 30.")
    ws.add_data_validation(deg)
    deg.add(f"C{PLANET_ROW0}:C{PLANET_ROW0 + 8}")
    ws.column_dimensions["A"].width = 30
    for c in "BCDEF":
        ws.column_dimensions[c].width = 18


# ---- Classes_Calc ---------------------------------------------------------------------------------
def _classes_sheet(ws, rules):
    ref_names = "S23_Ref_Calc!$B$3:$B$14"
    _head(ws, 3, ["Class", "House", "Rāśi", "Planets in it", "Lord", "Lord sits in house"])
    ws["A1"] = "The ten classes for this chart — houses are counted from the Lagna on the Chart sheet"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    row = CLASS_ROW0
    for cls in rules["classes"]:
        houses = cls["houses"] if cls["houses"] else [None]
        for h in houses:
            ws.cell(row=row, column=1, value=cls["name"])
            ws.cell(row=row, column=2, value=h if h is not None else f"=$C${BADHAKA_ROW}")
            ws.cell(row=row, column=3, value=f"=INDEX({ref_names},MOD(S23_Chart!$D$3+B{row}-1,12)+1)")
            ws.cell(row=row, column=15, value=f"={_planets_in(f'$B{row}')}")
            ws.cell(row=row, column=4, value=f'=IF(O{row}="","",LEFT(O{row},LEN(O{row})-2))')
            ws.cell(row=row, column=5, value=f"=INDEX(S23_Ref_Calc!$D$3:$D$14,MOD(S23_Chart!$D$3+B{row}-1,12)+1)")
            ws.cell(row=row, column=6, value=f"=INDEX(S23_Chart!$E${PLANET_ROW0}:$E${PLANET_ROW0 + 8},MATCH(E{row},S23_Chart!$A${PLANET_ROW0}:$A${PLANET_ROW0 + 8},0))")
            row += 1
    assert row - CLASS_ROW0 == CLASS_ROWS, (row, CLASS_ROWS)
    ws.cell(row=CLASS_ROW0 - 1, column=15, value="(helper)")
    # Badhaka
    ws.cell(row=BADHAKA_ROW - 2, column=1, value="Badhaka for this Lagna").font = Font(bold=True, color="6B1D2B")
    _head(ws, BADHAKA_ROW - 1, ["", "Mode", "House", "Rāśi", "Badhakādhipati", "Planets in it"])
    r = BADHAKA_ROW
    ws.cell(row=r, column=1, value="Badhaka sthāna")
    ws.cell(row=r, column=2, value="=INDEX(S23_Ref_Calc!$E$3:$E$14,S23_Chart!$D$3+1)")
    ws.cell(row=r, column=3, value="=INDEX(S23_Badhaka!$B$2:$B$4,MATCH(B%d,S23_Badhaka!$A$2:$A$4,0))" % r)
    ws.cell(row=r, column=4, value=f"=INDEX({ref_names},MOD(S23_Chart!$D$3+C{r}-1,12)+1)")
    ws.cell(row=r, column=5, value=f"=INDEX(S23_Ref_Calc!$D$3:$D$14,MOD(S23_Chart!$D$3+C{r}-1,12)+1)")
    ws.cell(row=r, column=15, value=f"={_planets_in(f'$C{r}')}")
    ws.cell(row=r, column=6, value=f'=IF(O{r}="","",LEFT(O{r},LEN(O{r})-2))')
    # house x class matrix
    ws.cell(row=MATRIX_ROW0 - 1, column=1, value="House × class (1 = the house belongs to the class)").font = Font(bold=True, color="6B1D2B")
    _head(ws, MATRIX_ROW0, ["House", "Rāśi"] + br.CLASS_ORDER + ["Classes"])
    houses_of = {c["name"]: c["houses"] for c in rules["classes"]}
    for h in range(1, 13):
        r = MATRIX_ROW0 + h
        ws.cell(row=r, column=1, value=h)
        ws.cell(row=r, column=2, value=f"=INDEX({ref_names},MOD(S23_Chart!$D$3+A{r}-1,12)+1)")
        for k, name in enumerate(br.CLASS_ORDER):
            if name == "Badhaka":
                f = f"=IF($A{r}=$C${BADHAKA_ROW},1,0)"
            else:
                f = "=IF(OR(" + ",".join(f"$A{r}={x}" for x in houses_of[name]) + "),1,0)"
            ws.cell(row=r, column=3 + k, value=f)
        joined = "&".join(f'IF({L(3 + k)}{r}=1,", "&{L(3 + k)}${MATRIX_ROW0},"")' for k in range(10))
        ws.cell(row=r, column=13, value=f"=MID({joined},3,300)")
    # house lords
    ws.cell(row=HOUSELORD_ROW0 - 2, column=1, value="Lord of each house").font = Font(bold=True, color="6B1D2B")
    _head(ws, HOUSELORD_ROW0 - 1, ["House", "Rāśi", "Lord"])
    for h in range(1, 13):
        r = HOUSELORD_ROW0 + h - 1
        ws.cell(row=r, column=1, value=h)
        ws.cell(row=r, column=2, value=f"=INDEX({ref_names},MOD(S23_Chart!$D$3+A{r}-1,12)+1)")
        ws.cell(row=r, column=3, value=f"=INDEX(S23_Ref_Calc!$D$3:$D$14,MOD(S23_Chart!$D$3+A{r}-1,12)+1)")
    for c, w in zip("ABCDEFGH", (16, 8, 14, 30, 14, 18, 12, 12)):
        ws.column_dimensions[c].width = w
    for c in "IJKL":
        ws.column_dimensions[c].width = 12
    ws.column_dimensions["M"].width = 40
    ws.column_dimensions["O"].hidden = True


# ---- Roles_Calc ---------------------------------------------------------------------------------
def _roles_sheet(ws):
    ws["A1"] = "Roles of the grahas for the daśā linking (1 = holds the role); Rahu and Ketu can only occupy"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    _head(ws, 2, ["Graha"] + br.ROLE_ORDER + ["Roles"])
    hl = lambda h: f"S23_Classes_Calc!$C${HOUSELORD_ROW0 + h - 1}"
    bad_house, bad_lord = f"S23_Classes_Calc!$C${BADHAKA_ROW}", f"S23_Classes_Calc!$E${BADHAKA_ROW}"
    for k, p in enumerate(br.PLANET_ORDER):
        r = ROLES_ROW0 + k
        house = f"S23_Chart!$E${PLANET_ROW0 + k}"
        ws.cell(row=r, column=1, value=p)
        flags = [
            f"=IF(OR({hl(2)}=$A{r},{hl(7)}=$A{r}),1,0)",
            f"=IF(OR({house}=2,{house}=7),1,0)",
            f"=IF({bad_lord}=$A{r},1,0)",
            f"=IF({house}={bad_house},1,0)",
            f"=IF(OR({hl(6)}=$A{r},{hl(8)}=$A{r},{hl(12)}=$A{r}),1,0)",
            f"=IF(OR({hl(3)}=$A{r},{hl(6)}=$A{r},{hl(11)}=$A{r}),1,0)",
        ]
        for j, f in enumerate(flags):
            ws.cell(row=r, column=2 + j, value=f)
        joined = "&".join(f'IF({L(2 + j)}{r}=1,", "&{L(2 + j)}$2,"")' for j in range(6))
        ws.cell(row=r, column=8, value=f"=MID({joined},3,300)")
    ws.column_dimensions["A"].width = 12
    for j in range(2, 8):
        ws.column_dimensions[L(j)].width = 15
    ws.column_dimensions["H"].width = 60


# ---- Dasha_Calc ---------------------------------------------------------------------------------
def _dasha_sheet(ws):
    vo, vy, nk = "S23_Ref_Calc!$AG$3:$AG$11", "S23_Ref_Calc!$AH$3:$AH$11", "S23_Ref_Calc!$AK$3:$AK$29"
    ws["A1"] = "Vimśottarī daśā from the Moon's birth-star (365.25-day years, as on the page)"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    rows = [(2, "Moon longitude (°)", f"=S23_Chart!{MOON_LON_CELL}"),
            (3, "Nakṣatra # (0-26)", "=INT(MOD(B2,360)/(360/27))"),
            (4, "Nakṣatra lord", f"=INDEX({nk},B3+1)"),
            (5, "Part of the nakṣatra already gone", "=(MOD(B2,360)-B3*(360/27))/(360/27)"),
            (6, "Index of that lord in the daśā order", f"=MATCH(B4,{vo},0)-1"),
            (7, "Virtual start of the first Mahādaśā", f"=S23_Chart!{BIRTH_CELL}-B5*INDEX({vy},B6+1)*365.25")]
    for r, label, f in rows:
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=f)
    ws["B7"].number_format = DATE_FMT
    ws.cell(row=DASHA_CUR_ROW, column=1, value="Running Mahādaśā")
    ws.cell(row=DASHA_CUR_ROW + 1, column=1, value="Running Bhukti")
    ws.cell(row=DASHA_CUR_ROW + 2, column=1, value="Row of the running Bhukti (below)")
    last = DASHA_ROW0 + 80
    ws.cell(row=DASHA_CUR_ROW + 2, column=2, value=f"=IFERROR(MATCH(1,G{DASHA_ROW0}:G{last},0),1)")
    ws.cell(row=DASHA_CUR_ROW, column=2, value=f"=INDEX(C{DASHA_ROW0}:C{last},B{DASHA_CUR_ROW + 2})")
    ws.cell(row=DASHA_CUR_ROW + 1, column=2, value=f"=INDEX(D{DASHA_ROW0}:D{last},B{DASHA_CUR_ROW + 2})")
    ws.cell(row=DASHA_CUR_ROW + 3, column=1, value="A daśā is running at 'Now'?")
    ws.cell(row=DASHA_CUR_ROW + 3, column=2, value=f"=ISNUMBER(MATCH(1,G{DASHA_ROW0}:G{last},0))")
    # Mahādaśā table
    _head(ws, 12, ["#", "Mahādaśā lord", "Years", "Starts", "Ends"])
    for i in range(9):
        r = 13 + i
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=f"=INDEX({vo},MOD($B$6+A{r},9)+1)")
        ws.cell(row=r, column=3, value=f"=INDEX({vy},MATCH(B{r},{vo},0))")
        ws.cell(row=r, column=4, value="=$B$7" if i == 0 else f"=E{r - 1}")
        ws.cell(row=r, column=5, value=f"=D{r}+C{r}*365.25")
        for c in (4, 5):
            ws.cell(row=r, column=c).number_format = DATE_FMT
    # Bhukti table
    _head(ws, DASHA_ROW0 - 1, ["Mahādaśā #", "Bhukti #", "Mahādaśā", "Bhukti", "Starts", "Ends", "Running?"])
    for k in range(81):
        r = DASHA_ROW0 + k
        i, j = divmod(k, 9)
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=j)
        ws.cell(row=r, column=3, value=f"=INDEX($B$13:$B$21,A{r}+1)")
        ws.cell(row=r, column=4, value=f"=INDEX({vo},MOD(MATCH(C{r},{vo},0)-1+B{r},9)+1)")
        ws.cell(row=r, column=5, value=f"=INDEX($D$13:$D$21,A{r}+1)" if j == 0 else f"=F{r - 1}")
        ws.cell(row=r, column=6, value=(f"=E{r}+INDEX($C$13:$C$21,A{r}+1)*INDEX({vy},MATCH(D{r},{vo},0))/120*365.25"))
        ws.cell(row=r, column=7, value=f"=IF(AND(E{r}<=S23_Chart!{NOW_CELL},S23_Chart!{NOW_CELL}<F{r}),1,0)")
        for c in (5, 6):
            ws.cell(row=r, column=c).number_format = DATE_FMT
    ws.column_dimensions["A"].width = 38
    for c in "BCDEFG":
        ws.column_dimensions[c].width = 18


# ---- Predict_Calc -------------------------------------------------------------------------------
def _predict_sheet(ws, rules):
    n_rules = len(rules["class_rules"])
    ws["A1"] = "Graha + bhāva for this chart — the text is looked up in GrahaInBhava, ClassRules, DignityEffect and Digbala"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    _head(ws, 2, ["Graha", "House", "Nature", "Status", "Reading (taught / curated text)", "Dignity", "Dignity line",
                  "Digbala line", "Classes of the house", "Class-rule texts", "Recording extra points", "Row in GrahaInBhava", "Digbala house", "Digbala lost"])
    for k, p in enumerate(br.PLANET_ORDER):
        r = PREDICT_ROW0 + k
        pc = _planet_cells(k)
        n, d = f"({pc['sign']}+1)", pc["deg"]
        exR, exD, deR, deD, mtR, mt0, mt1 = (f"S23_Ref_Calc!${c}${3 + k}" for c in "JKLMNOP")
        base = f"INDEX(S23_Ref_Calc!$R${3 + k}:$AC${3 + k},{n})"
        dignity = (f'=IF({base}="Exalted",'
                   f'IF(AND({n}={mtR},{d}>{exD}),IF(AND({d}>={mt0},{d}<={mt1}),"Own (Moolatrikona)","Own House"),'
                   f'IF(AND({n}={exR},ABS({d}-{exD})<=1),"Deep Exalted","Exalted")),'
                   f'IF({base}="Debilitated",IF(AND({n}={deR},ABS({d}-{deD})<=1),"Deep Debilitated","Debilitated"),'
                   f'IF({base}="Own (Moolatrikona)",IF(AND({d}>={mt0},{d}<={mt1}),"Own (Moolatrikona)","Own House"),{base})))')
        # Session 26: Jupiter, Venus, Mercury, Moon benefic; the Sun a mild malefic; the rest malefic
        benefic = ",".join(f'$A{r}="{b}"' for b in br.BENEFICS)
        nature = f'=IF(OR({benefic}),"benefic",IF($A{r}="{br.MILD_MALEFIC}","mild malefic","malefic"))'
        ws.cell(row=r, column=1, value=p)
        ws.cell(row=r, column=2, value=f"={pc['house']}")
        ws.cell(row=r, column=3, value=nature)
        ws.cell(row=r, column=4, value=f"=INDEX(S23_GrahaInBhava!$E$1:$E$300,$L{r})")
        ws.cell(row=r, column=5, value=f"=INDEX(S23_GrahaInBhava!$C$1:$C$300,$L{r})")
        ws.cell(row=r, column=6, value=dignity)
        ws.cell(row=r, column=7, value=f'=IFERROR($F{r}&": "&INDEX(S23_DignityEffect!$C$2:$C$10,MATCH($F{r},S23_DignityEffect!$A$2:$A$10,0)),"")')
        ws.cell(row=r, column=8, value=(
            f'=IF($B{r}=$M{r},$A{r}&" gains directional strength (digbala) in the "&{_ord(f"$B{r}")}&" house.",'
            f'IF($B{r}=$N{r},$A{r}&" loses directional strength (digbala) in the "&{_ord(f"$B{r}")}&" house, '
            f'opposite its strongest house, the "&{_ord(f"$M{r}")}&".",""))'))
        ws.cell(row=r, column=9, value=f"=INDEX(S23_Classes_Calc!$M${MATRIX_ROW0 + 1}:$M${MATRIX_ROW0 + 12},$B{r})")
        fr = FLAG_ROW0 + k
        joined = "&".join(f'IF({L(2 + m)}{fr}=1,CHAR(10)&IF(AND($C{r}="mild malefic",S23_ClassRules!$B${2 + m}="malefic"),"(mild) ","")'
                          f'&S23_ClassRules!$D${2 + m},"")' for m in range(n_rules))
        ws.cell(row=r, column=10, value=f"=MID({joined},2,32000)")
        ws.cell(row=r, column=11, value=f"=INDEX(S23_GrahaInBhava!$D$1:$D$300,$L{r})")
        ws.cell(row=r, column=12, value=(f"=SUMPRODUCT((S23_GrahaInBhava!$A$2:$A$300=$A{r})*(S23_GrahaInBhava!$B$2:$B$300=$B{r})"
                                         f"*ROW(S23_GrahaInBhava!$A$2:$A$300))"))
        ws.cell(row=r, column=13, value=f"=IFERROR(INDEX(S23_Digbala!$B$2:$B$8,MATCH($A{r},S23_Digbala!$A$2:$A$8,0)),0)")
        ws.cell(row=r, column=14, value=f"=IFERROR(INDEX(S23_Digbala!$C$2:$C$8,MATCH($A{r},S23_Digbala!$A$2:$A$8,0)),0)")
    # class-rule flags
    ws.cell(row=FLAG_ROW0 - 2, column=1, value="Which ClassRules rows apply to each graha (1 = applies)").font = Font(bold=True, color="6B1D2B")
    _head(ws, FLAG_ROW0 - 1, ["Graha"] + [f"rule {m + 1}" for m in range(n_rules)])
    matrix = f"S23_Classes_Calc!$C${MATRIX_ROW0 + 1}:$L${MATRIX_ROW0 + 12}"
    for k, p in enumerate(br.PLANET_ORDER):
        fr, pr = FLAG_ROW0 + k, PREDICT_ROW0 + k
        ws.cell(row=fr, column=1, value=p)
        for m in range(n_rules):
            cr = 2 + m
            f = (f'=IF(AND(INDEX({matrix},$B{pr},MATCH(S23_ClassRules!$A${cr},S23_Ref_Calc!$AE$3:$AE$12,0))=1,'
                 f'OR(S23_ClassRules!$B${cr}="any",S23_ClassRules!$B${cr}=IF($C{pr}="mild malefic","malefic",$C{pr})),'
                 f'NOT(ISNUMBER(SEARCH(", "&$B{pr}&",",", "&S23_ClassRules!$C${cr}&",")))),1,0)')
            ws.cell(row=fr, column=2 + m, value=f)
    _predict_s24_27(ws, rules)
    for c, w in zip("ABCDEFGHIJK", (12, 7, 9, 10, 60, 20, 50, 50, 28, 60, 60)):
        ws.column_dimensions[c].width = w
    for c in "OPQRS":
        ws.column_dimensions[c].width = 50
    for r in range(PREDICT_ROW0, PREDICT_ROW0 + 9):
        for c in (5, 7, 8, 10, 11, 16, 17, 18):
            ws.cell(row=r, column=c).alignment = WRAP


def _predict_s24_27(ws, rules):
    """Sessions 23 (2024) - 27 on S23_Predict_Calc: the Moon's paksha strength, the Session 26 lines for a benefic or
    malefic in the house, the 12th-house line and the conditional readings (bhava_rules.chart_conditions)."""
    P = lambda name: PREDICT_ROW0 + br.PLANET_ORDER.index(name)          # a planet's row on this sheet
    house = lambda name: f"$B${P(name)}"
    sign = lambda name: f"S23_Chart!$D${PLANET_ROW0 + br.PLANET_ORDER.index(name)}"
    aff = lambda name: f"${L(AFFLICTED_COL)}${P(name)}"
    retro = lambda name: f'S23_Chart!${L(RETRO_COL)}${PLANET_ROW0 + br.PLANET_ORDER.index(name)}="yes"'
    lord = lambda h: f"S23_Classes_Calc!$C${HOUSELORD_ROW0 + h - 1}"
    house_of = lambda expr: f"INDEX($B${PREDICT_ROW0}:$B${PREDICT_ROW0 + 8},MATCH({expr},$A${PREDICT_ROW0}:$A${PREDICT_ROW0 + 8},0))"
    sign_of = lambda expr: f"INDEX(S23_Chart!$D${PLANET_ROW0}:$D${PLANET_ROW0 + 8},MATCH({expr},S23_Chart!$A${PLANET_ROW0}:$A${PLANET_ROW0 + 8},0))"
    age, gender = f"S23_Chart!{AGE_CELL}", f"S23_Chart!{GENDER_CELL}"
    run = f"S23_Dasha_Calc!{DASHA_RUNNING_CELL}"
    maha, bhukti = f"S23_Dasha_Calc!$B${DASHA_CUR_ROW}", f"S23_Dasha_Calc!$B${DASHA_CUR_ROW + 1}"
    sun = br.PLANET_ORDER.index("Sun")
    combustible = ",".join(f'$A{{r}}="{p}"' for p in rules["reference"]["COMBUST_PLANETS"])
    for name, col in (("Moon strength", 15), ("Session 26 lines", 16), ("12th-house line", 17), ("When it applies (conditions)", 18),
                      ("Active now (keys)", 19), ("Combust?", COMBUST_COL), ("Afflicted? (R5)", AFFLICTED_COL), ("(mild) prefix", MILD_COL)):
        c = ws.cell(row=2, column=col, value=name)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    # Session 26 line flags: per planet and S23_BhavaNature row, the group the row falls in (0 general, 1 house, 2 planet) or -1
    n_bn = len(rules["bhava_nature"])
    ws.cell(row=NATURE_FLAG_ROW0 - 2, column=1, value="Which S23_BhavaNature rows apply (0 general, 1 this house, 2 this planet, -1 no)").font = Font(bold=True, color="6B1D2B")
    _head(ws, NATURE_FLAG_ROW0 - 1, ["Graha"] + [f"row {m + 2}" for m in range(n_bn)])
    line0 = 3 + n_bn                                   # then, to the right, each row's line as this planet shows it
    _head(ws, NATURE_FLAG_ROW0 - 1, [f"line {m + 2}" for m in range(n_bn)], col0=line0)
    for k, p in enumerate(br.PLANET_ORDER):
        fr, r = NATURE_FLAG_ROW0 + k, PREDICT_ROW0 + k
        ws.cell(row=fr, column=1, value=p)
        kind = f'IF($C{r}="benefic","benefic","malefic")'
        for m in range(n_bn):
            b = 2 + m
            h, nat, pl = f"S23_BhavaNature!$A${b}", f"S23_BhavaNature!$B${b}", f"S23_BhavaNature!$C${b}"
            ws.cell(row=fr, column=2 + m, value=(f'=IF(AND(OR({nat}={kind},{nat}="any"),OR({h}="",{h}=$B{r}),OR({pl}="",{pl}=$A{r})),'
                                                 f'IF({h}="",0,IF({pl}="",1,2)),-1)'))
            ws.cell(row=fr, column=line0 + m, value=f'=IF({nat}="malefic",${L(MILD_COL)}${r},"")&S23_BhavaNature!$D${b}')
    for k, p in enumerate(br.PLANET_ORDER):
        r, fr = PREDICT_ROW0 + k, NATURE_FLAG_ROW0 + k
        ws.cell(row=r, column=15, value=f'=IF($A{r}="Moon",IF(S23_Chart!{WAXING_CELL},"Shukla (waxing) — stronger","Krishna (waning) — weaker"),"")')
        passes = "&".join(f'IF({L(2 + m)}{fr}={g},CHAR(10)&{L(3 + n_bn + m)}{fr},"")' for g in range(3) for m in range(n_bn))
        ws.cell(row=r, column=16, value=f"=MID({passes},2,32000)")
        ws.cell(row=r, column=17, value=(f'=IF($B{r}=12,IFERROR(INDEX(S23_Conditions!$D$1:$D$300,MATCH("twelfth_house",'
                                         f'S23_Conditions!$A$1:$A$300,0)),""),"")'))
        ws.cell(row=r, column=COMBUST_COL, value=(f'=AND(OR({combustible.format(r=r)}),S23_Chart!$D${PLANET_ROW0 + k}=S23_Chart!$D${PLANET_ROW0 + sun},'
                                                  f'ABS(S23_Chart!$C${PLANET_ROW0 + k}-S23_Chart!$C${PLANET_ROW0 + sun})<={rules["reference"]["COMBUST_ORB"]})'))
        ws.cell(row=r, column=AFFLICTED_COL, value=f'=OR($F{r}="Debilitated",$F{r}="Deep Debilitated",$F{r}="Enemy\'s House",${L(COMBUST_COL)}{r})')
        ws.cell(row=r, column=MILD_COL, value=f'=IF($A{r}="Sun","(mild) ","")')
    # the candidate conditional readings, in bhava_rules.CONDITION_KEYS order (and planet order within a key)
    dasha = lambda test: f'IF({run},IF({test},"yes","no"),"")'
    young = lambda limit: f"{age}<{limit}"
    hin = lambda name, hs: "OR(" + ",".join(f"{house(name)}={h}" for h in hs) + ")"
    male = lambda s_expr: f"MOD({s_expr},2)=0"
    fifth_sign = "MOD(S23_Chart!$D$3+4,12)"
    rows = [("saturn_matures", '"Saturn"', house("Saturn"), f"AND({hin('Saturn', (1, 2, 3, 5, 7, 10))},{young(br.SATURN_MATURES_AGE)})", '""'),
            ("saturn_retro_1", '"Saturn"', "1", f"AND({house('Saturn')}=1,{retro('Saturn')})", '""'),
            ("saturn_afflicted_10_young", '"Saturn"', "10", f"AND({house('Saturn')}=10,{aff('Saturn')},{young(br.SATURN_MATURES_AGE)})", '""'),
            ("saturn_mars_12", '"Saturn"', "12", f"AND({house('Saturn')}=12,{house('Mars')}=12)", '""'),
            ("saturn_afflicted_6", '"Saturn"', "6", f"AND({house('Saturn')}=6,{aff('Saturn')})", '""'),
            ("saturn_afflicted_12", '"Saturn"', "12", f"AND({house('Saturn')}=12,{aff('Saturn')})", '""'),
            ("jupiter_md_8", '"Jupiter"', "8", f"{house('Jupiter')}=8", dasha(f'{maha}="Jupiter"')),
            ("jupiter_md_11", '"Jupiter"', "11", f"{house('Jupiter')}=11", dasha(f'{maha}="Jupiter"')),
            ("venus_dasha_9", '"Venus"', "9", f"{house('Venus')}=9", dasha(f'OR({maha}="Venus",{bhukti}="Venus")')),
            ("rahu_md_9", '"Rahu"', "9", f"{house('Rahu')}=9", dasha(f'{maha}="Rahu"'))]
    rows += [("twelfth_hidden_talent", f'"{p}"', "12", f"{house(p)}=12", dasha(f'OR({maha}="{p}",{bhukti}="{p}")')) for p in br.PLANET_ORDER]
    rows += [("upachaya_30s", f'"{p}"', house(p), hin(p, (3, 6, 10, 11)), '""') for p in br.PLANET_ORDER]
    rows += [("ketu_12_purpose", '"Ketu"', "12", f"AND({house('Ketu')}=12,{young(br.KETU_PURPOSE_AGE)})", '""'),
             ("venus_afflicted", '"Venus"', house("Venus"), f"AND({hin('Venus', (2, 8, 11))},{aff('Venus')})", '""'),
             ("venus_good", '"Venus"', house("Venus"), f"AND({hin('Venus', (2, 8, 11))},NOT({aff('Venus')}))", '""'),
             ("venus_mercury_5", '"Venus"', "5", f"AND({house('Venus')}=5,{house('Mercury')}=5)", '""'),
             ("seventh_lord_12", lord(7), "12", f"{house_of(lord(7))}=12", '""'),
             ("mercury_foreign_language", '"Mercury"', "2",
              f'AND({house("Mercury")}=2,OR({sign("Rahu")}={sign("Mercury")},AND({lord(12)}<>"Mercury",{sign_of(lord(12))}={sign("Mercury")})))', '""'),
             ("moon_dual_10", '"Moon"', "10", f'AND({house("Moon")}=10,INDEX(S23_Ref_Calc!$E$3:$E$14,{sign("Moon")}+1)="Dwisabhava")', '""'),
             ("venus_meets_wife", '"Venus"', house("Venus"), f'{gender}="Male"', '""'),
             ("jupiter_husband", '"Jupiter"', house("Jupiter"), f'{gender}="Female"', '""'),
             ("first_child_male", lord(5), "5",
              f"AND({male(fifth_sign)},OR({house('Sun')}=5,{house('Mars')}=5,{house('Jupiter')}=5),{male(sign_of(lord(5)))})", '""')]
    assert [k for k, *_ in rows] == sorted((k for k, *_ in rows), key=br.CONDITION_KEYS.index)
    ws.cell(row=COND_ROW0 - 2, column=1, value="Conditional readings (S23_Conditions): which hold for this chart").font = Font(bold=True, color="6B1D2B")
    _head(ws, COND_ROW0 - 1, ["Key", "Planet", "House", "Holds?", "Active now?", "Row in S23_Conditions", "Text"])
    K, Pl, H = "S23_Conditions!$A$2:$A$300", "S23_Conditions!$B$2:$B$300", "S23_Conditions!$C$2:$C$300"
    for i, (key, planet, h, holds, active) in enumerate(rows):
        r = COND_ROW0 + i
        ws.cell(row=r, column=1, value=key)
        ws.cell(row=r, column=2, value=f"={planet}")
        ws.cell(row=r, column=3, value=f"={h}")
        ws.cell(row=r, column=4, value=f"={holds}")
        ws.cell(row=r, column=5, value=f"={active}")
        best = [f"SUMPRODUCT(({K}=$A{r})*({Pl}={pl})*({H}={hh})*ROW({K}))"
                for pl, hh in ((f"$B{r}", f"$C{r}"), ('""', f"$C{r}"), (f"$B{r}", '""'), ('""', '""'))]
        ws.cell(row=r, column=6, value=f"=IF({best[0]}>0,{best[0]},IF({best[1]}>0,{best[1]},IF({best[2]}>0,{best[2]},{best[3]})))")
        ws.cell(row=r, column=7, value=f'=IF(F{r}>0,INDEX(S23_Conditions!$D$1:$D$300,F{r}),"")')
    last = COND_ROW0 + len(rows) - 1
    for k, p in enumerate(br.PLANET_ORDER):
        r = PREDICT_ROW0 + k
        texts = "&".join(f'IF(AND($B${c}=$A{r},$D${c},$F${c}>0),CHAR(10)&$G${c},"")' for c in range(COND_ROW0, last + 1))
        keys = "&".join(f'IF(AND($B${c}=$A{r},$D${c},$F${c}>0,$E${c}="yes"),", "&$A${c},"")' for c in range(COND_ROW0, last + 1))
        ws.cell(row=r, column=18, value=f"=MID({texts},2,32000)")
        ws.cell(row=r, column=19, value=f"=MID({keys},3,32000)")


# ---- LifeArea_Calc ---------------------------------------------------------------------------------
H_NAME, H_SIGN, H_HOUSE, H_NATURE, H_CLASS, H_DIG, H_COMB, H_RETRO = range(27, 35)
H_COUNT, H_TARGET, H_ANAME, H_TC = 35, 38, 41, 44          # three aspect slots each
H_OWNHIT, H_STRENGTH, H_RULES = 47, 48, 49
H_ROWS, H_MEAN = 50, 59                                      # per slot: rows (specific, count, general), meanings m1-m3
H_DEFAULT = 68


def _life_area_sheet(ws, rules):
    """Session 27's 7-step method for the area chosen in B2 — equal to bhava_rules.life_area (see life_area_from_sheet)."""
    ref = rules["reference"]
    n_rules = len(rules["class_rules"])
    ws["A1"] = "Life areas (Session 27) — pick the area in B2; the 7 steps follow for the chart on S23_Chart"
    ws["A1"].font = Font(bold=True, color="6B1D2B", size=13)
    hr = lambda c: f"${L(c)}${HELP_ROW0}:${L(c)}${HELP_ROW0 + 8}"
    hf = lambda c, x: f"INDEX({hr(c)},MATCH({x},{hr(H_NAME)},0))"              # helper field of the planet named by x
    names = "S23_Ref_Calc!$B$3:$B$14"
    lords = f"S23_Classes_Calc!$C${HOUSELORD_ROW0}:$C${HOUSELORD_ROW0 + 11}"
    sign_of_house = lambda h: f"MOD(S23_Chart!$D$3+{h}-1,12)"
    bh = lambda j, h: f"INDEX(S23_Ref_Calc!${L(REF_BHAVA_COL0 + j)}$3:${L(REF_BHAVA_COL0 + j)}$14,{h})"   # 1 name, 2 sig, 3 people, 4 body
    gender = f"S23_Chart!{GENDER_CELL}"
    LA = lambda c: f"S23_LifeAreas!${c}$1:${c}$60"
    AM_P, AM_A, AM_F, AM_T = (f"S23_AspectMeaning!${c}$2:${c}$300" for c in "ABCD")
    AM_TEXT = "S23_AspectMeaning!$D$1:$D$300"
    CK, CP, CH, CT = (f"S23_Conditions!${c}$2:${c}$300" for c in "ABCD")
    C_TEXT = "S23_Conditions!$D$1:$D$300"
    LO, SI, LT, LS, LC, LX = (f"S23_BhavaLordIn!${c}$2:${c}$300" for c in "ABCDFG")
    L_TEXT, L_STATUS = "S23_BhavaLordIn!$C$1:$C$300", "S23_BhavaLordIn!$D$1:$D$300"
    matrix = f"S23_Classes_Calc!$C${MATRIX_ROW0 + 1}:$L${MATRIX_ROW0 + 12}"
    ci = {c: br.CLASS_ORDER.index(c) + 1 for c in ("Kendra", "Trikona", "Dusthana", "Badhaka")}
    cell = lambda r, c, v: ws.cell(row=r, column=c, value=v)

    # ---- the area
    top = [(2, "Area of life (pick)", None), (3, "Row in S23_LifeAreas", f'=MATCH({AREA_CELL},{LA("B")},0)'),
           (4, "No", f"=INDEX({LA('A')},$B$3)"), (5, "Houses", f'=INDEX({LA("C")},$B$3)&""'),
           (6, "Link", f'=INDEX({LA("F")},$B$3)&""'), (7, "Source", f'=INDEX({LA("G")},$B$3)&""'),
           (8, "House 1", '=VALUE(TRIM(LEFT($B$5,FIND(",",$B$5&",")-1)))'),
           (9, "House 2", '=IFERROR(VALUE(TRIM(MID($B$5,FIND(",",$B$5)+1,9))),"")'),
           (10, "Karakas (Ready Reckoner)", f'=INDEX({LA("D")},$B$3)&""'), (11, "Karaka for a woman's chart", f'=INDEX({LA("E")},$B$3)&""'),
           (12, "Karaka 1", f'=IF(AND($B$11<>"",{gender}="Female"),$B$11,TRIM(LEFT($B$10,FIND(",",$B$10&",")-1)))'),
           (13, "Karaka 2", f'=IF(AND($B$11<>"",{gender}="Female"),"",IFERROR(TRIM(MID($B$10,FIND(",",$B$10)+1,99)),""))')]
    for r, label, f in top:
        cell(r, 1, label)
        if f:
            cell(r, 2, f)
    ws[AREA_CELL] = rules["life_areas"][7]["area"]
    ws[AREA_CELL].fill = INPUT_FILL
    dv = DataValidation(type="list", formula1=f"=S23_LifeAreas!$B$2:$B${1 + len(rules['life_areas'])}", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(AREA_CELL)
    best = lambda key, planet, house: [f"SUMPRODUCT(({CK}={key})*({CP}={pl})*({CH}={hh})*ROW({CK}))"
                                       for pl, hh in ((planet, house), ('""', house), (planet, '""'), ('""', '""'))]
    jh = best('"jupiter_husband"', '"Jupiter"', '""')
    vm = best('"venus_meets_wife"', "$B$12", hf(H_HOUSE, "$B$12"))
    pick = lambda b: f"IF({b[0]}>0,{b[0]},IF({b[1]}>0,{b[1]},IF({b[2]}>0,{b[2]},{b[3]})))"
    cell(14, 1, "Karaka note")
    cell(14, 2, (f'=IF($B$11="","",IF({gender}="Female",IF({jh[2]}>0,INDEX({C_TEXT},{jh[2]}),IF({jh[3]}>0,INDEX({C_TEXT},{jh[3]}),"")),'
                 f'IF({gender}="Male",IF({pick(vm)}>0,INDEX({C_TEXT},{pick(vm)}),""),'
                 f'"For a woman\'s chart the husband\'s karaka is "&$B$11&".")))'))
    for r, label, col in ((15, "Supports", SUPPORT_COL), (16, "Pressure", PRESSURE_COL)):
        cell(r, 1, label)
        parts = "&".join(f'IF(${L(col)}${x}<>"",CHAR(10)&${L(col)}${x},"")' for x in range(BLOCK_ROW0, LINK_ROW0 + 3))
        cell(r, 2, f"=MID({parts},2,32000)").alignment = WRAP
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 60

    # ---- helper table: one row per planet
    _head(ws, HELP_ROW0 - 1, ["Graha", "Sign #", "House", "Nature", "Benefic / malefic", "Dignity", "Combust?", "Retro?",
                              "Aspect 1", "Aspect 2", "Aspect 3", "Falls on 1", "Falls on 2", "Falls on 3", "Name 1", "Name 2",
                              "Name 3", "Her count 1", "Her count 2", "Her count 3", "Aspects own sign?", "Strength (R3)",
                              "Rules houses"], col0=H_NAME)
    strong = ",".join(f'$' + L(H_DIG) + '{r}="' + x + '"' for x in br.STRONG_LABELS)
    weak = ",".join(f'$' + L(H_DIG) + '{r}="' + x + '"' for x in br.WEAK_LABELS)
    for k, p in enumerate(br.PLANET_ORDER):
        r, pr, cr = HELP_ROW0 + k, PREDICT_ROW0 + k, PLANET_ROW0 + k
        cell(r, H_NAME, p)
        cell(r, H_SIGN, f"=S23_Chart!$D${cr}")
        cell(r, H_HOUSE, f"=S23_Chart!$E${cr}")
        cell(r, H_NATURE, f"=S23_Predict_Calc!$C${pr}")
        cell(r, H_CLASS, f'=IF({L(H_NATURE)}{r}="benefic","benefic","malefic")')
        cell(r, H_DIG, f"=S23_Predict_Calc!$F${pr}")
        cell(r, H_COMB, f"=S23_Predict_Calc!${L(COMBUST_COL)}${pr}")
        cell(r, H_RETRO, f'=S23_Chart!${L(RETRO_COL)}${cr}="yes"')
        counts = ref["SPECIAL_ASPECTS"][p]
        for sl in range(3):
            if sl < len(counts):
                h = counts[sl]
                cell(r, H_COUNT + sl, h)
                cell(r, H_TARGET + sl, f"=MOD({L(H_SIGN)}{r}+{h}-1,12)")
                cell(r, H_ANAME + sl, br.aspect_name(p, h))
                cell(r, H_TC + sl, br.teacher_count(p, h))
            else:
                cell(r, H_TARGET + sl, '=""')
        own = ",".join(f'AND({L(H_TARGET + sl)}{r}<>"",INDEX(S23_Ref_Calc!$D$3:$D$14,N({L(H_TARGET + sl)}{r})+1)=${L(H_NAME)}{r})'
                       for sl in range(len(counts)))
        cell(r, H_OWNHIT, f"=OR({own})")
        sh, wh = f"OR({strong.format(r=r)},{L(H_OWNHIT)}{r})", f"OR({weak.format(r=r)},{L(H_COMB)}{r})"
        cell(r, H_STRENGTH, f'=IF(AND({sh},NOT({wh})),"strong",IF(AND({wh},NOT({sh})),"weak","depends"))')
        cell(r, H_RULES, "=MID(" + "&".join(f'IF(INDEX({lords},{h})=${L(H_NAME)}{r},", {h}","")' for h in range(1, 13)) + ",3,99)")
        for sl in range(3):
            if sl >= len(counts):
                for j in range(3):
                    cell(r, H_MEAN + 3 * sl + j, '=""')
                continue
            tc = f"{L(H_TC + sl)}{r}"
            rows_ = [f"SUMPRODUCT(({AM_P}=${L(H_NAME)}{r})*({AM_A}={tc})*({AM_F}={L(H_HOUSE)}{r})*ROW({AM_P}))",
                     f'SUMPRODUCT(({AM_P}=${L(H_NAME)}{r})*({AM_A}={tc})*({AM_F}="")*ROW({AM_P}))',
                     f'SUMPRODUCT(({AM_P}=${L(H_NAME)}{r})*({AM_A}="")*({AM_F}="")*ROW({AM_P}))']
            for j in range(3):
                cell(r, H_ROWS + 3 * sl + j, f"={rows_[j]}")
            sp, cn, gn = (f"{L(H_ROWS + 3 * sl + j)}{r}" for j in range(3))
            cell(r, H_MEAN + 3 * sl, f'=IF({sp}>0,INDEX({AM_TEXT},{sp}),IF(AND({cn}=0,{gn}=0),${L(H_DEFAULT)}${HELP_ROW0},""))')
            cell(r, H_MEAN + 3 * sl + 1, f'=IF({cn}>0,INDEX({AM_TEXT},{cn}),"")')
            cell(r, H_MEAN + 3 * sl + 2, f'=IF({gn}>0,INDEX({AM_TEXT},{gn}),"")')
    dflt = f'SUMPRODUCT(({AM_P}="any")*({AM_A}="")*({AM_F}="")*ROW({AM_P}))'
    cell(HELP_ROW0, H_DEFAULT, f'=IF({dflt}>0,INDEX({AM_TEXT},{dflt}),"")')
    cell(HELP_ROW0 - 1, H_DEFAULT, "Default aspect meaning")

    # ---- one block per house of the area
    def summary(r, cond_good, cond_bad, text):
        cell(r, SUPPORT_COL, f'=IF({cond_good},{text},"")')
        cell(r, PRESSURE_COL, f'=IF({cond_bad},{text},"")')

    _head(ws, BLOCK_ROW0 - 1, ["Step", "Planet / house", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                               "Supports", "Pressure"])
    for blk, hcell in enumerate(("$B$8", "$B$9")):
        b0 = BLOCK_ROW0 + blk * BLOCK_ROWS
        hb, sb = f"$B${b0}", f"$C${b0}"
        H = _ord(hb)
        cell(b0, 1, "bhava")
        cell(b0, 2, f'=IF({hcell}="","",{hcell})')
        cell(b0, 3, f'=IF($B${b0}="","",{sign_of_house(hb)})')
        cell(b0, 4, f'=IF($B${b0}="","",INDEX({names},$C${b0}+1))')
        cell(b0, 5, f'=IF($B${b0}="","",INDEX(S23_Ref_Calc!${L(REF_SIGNLINE_COL)}$3:${L(REF_SIGNLINE_COL)}$14,$C${b0}+1))')
        r = b0 + 1
        for k, p in enumerate(br.PLANET_ORDER):                                     # 2 · planets in the house
            hrow, pr = HELP_ROW0 + k, PREDICT_ROW0 + k
            cell(r, 1, "occupant")
            cell(r, 2, p)
            cell(r, 3, f'=AND({hb}<>"",${L(H_HOUSE)}${hrow}={hb})')
            cell(r, 4, f"=${L(H_NATURE)}${hrow}")
            cell(r, 5, f"=S23_Predict_Calc!$E${pr}")
            cell(r, 6, f"=S23_Predict_Calc!$D${pr}")
            cell(r, 7, f"=S23_Predict_Calc!$P${pr}")
            txt = f'$B{r}&" ("&$D{r}&") in the "&{H}'
            summary(r, f'AND($C{r},${L(H_CLASS)}${hrow}="benefic")', f'AND($C{r},${L(H_CLASS)}${hrow}="malefic")', txt)
            r += 1
        for k, p in enumerate(br.PLANET_ORDER):                                     # 3 · planets aspecting it
            hrow = HELP_ROW0 + k
            for sl in range(3):
                cell(r, 1, "aspect")
                cell(r, 2, p)
                cell(r, 3, f'=AND({hb}<>"",${L(H_TARGET + sl)}${hrow}<>"",${L(H_TARGET + sl)}${hrow}={sb})')
                cell(r, 4, f'=${L(H_ANAME + sl)}${hrow}&""')
                for j in range(3):
                    cell(r, 5 + j, f"=${L(H_MEAN + 3 * sl + j)}${hrow}")
                txt = f'$B{r}&" ("&${L(H_NATURE)}${hrow}&") aspects the "&{H}'
                summary(r, f'AND($C{r},${L(H_CLASS)}${hrow}="benefic")', f'AND($C{r},${L(H_CLASS)}${hrow}="malefic")', txt)
                r += 1
        lr = r                                                                      # 4 · the lord
        B, C = f"$B${lr}", f"$C${lr}"
        cell(lr, 1, "lord")
        cell(lr, 2, f'=IF({hb}="","",INDEX({lords},{hb}))')
        cell(lr, 3, f'=IF({B}="","",{hf(H_HOUSE, B)})')
        cell(lr, 4, f'=IF({B}="","",{hf(H_SIGN, B)})')
        cell(lr, 5, f'=IF({B}="","",INDEX({names},$D${lr}+1))')
        cls = "&".join(f'IF(INDEX({matrix},{C},{ci[c]})=1," and {c}","")' for c in ("Kendra", "Trikona", "Dusthana", "Badhaka"))
        cell(lr, 23, f'=IF({B}="","",MID({cls},6,99))')
        cell(lr, 32, f'=IF({B}="",FALSE,INDEX({matrix},{C},{ci["Kendra"]})=1)')        # the sits-in house is a Kendra?
        cell(lr, 33, f'=IF({B}="",FALSE,INDEX({matrix},{C},{ci["Trikona"]})=1)')       # … a Trikona?
        kt = "&".join(f'IF(AND(OR(AND(S23_ClassRules!$A${2 + m}="Kendra",$AF${lr}),AND(S23_ClassRules!$A${2 + m}="Trikona",$AG${lr})),'
                      f'S23_ClassRules!$B${2 + m}="any",NOT(ISNUMBER(SEARCH(", "&{C}&",",", "&S23_ClassRules!$C${2 + m}&",")))),'
                      f'" "&S23_ClassRules!$D${2 + m},"")'
                      for m in range(n_rules))
        cell(lr, 24, f'=IF({B}="","",{kt})')
        cell(lr, 6, (f'=IF({B}="","",IF({C}={hb},"The lord sits in its own bhava, so the matters of this house are protected and strengthened.",'
                     f'"Placed in the "&{_ord(C)}&" house"&IF($W${lr}<>"",", a "&$W${lr}&" bhava","")&"."'
                     f'&$X${lr}&IF(OR({C}=6,{C}=8,{C}=12)," A difficult placement.","")))'))
        cell(lr, 7, f'=IF({B}="","",{hf(H_DIG, B)})')
        cell(lr, 8, f'=IF({B}="","",{hf(H_STRENGTH, B)})')
        lord_y = f"INDEX({lords},{C})"
        cell(lr, 12, f'=IF({B}="",FALSE,AND({C}<>{hb},{hf(H_HOUSE, lord_y)}={hb},{lord_y}<>{B}))')
        lo_, hi_ = f"MIN({hb},{C})", f"MAX({hb},{C})"
        cell(lr, 13, f'=IF({B}="",0,SUMPRODUCT(({LX}="yes")*((({LO}={lo_})*({SI}={hi_}))+(({LO}={hi_})*({SI}={lo_})))*ROW({LO})))')
        for col, cond in ((14, '""'), (15, '"strong"'), (16, '"weak"')):
            cell(lr, col, f'=IF({B}="",0,SUMPRODUCT(({LO}={hb})*({SI}={C})*({LC}={cond})*({LX}<>"yes")*ROW({LO})))')
        st = f"$H${lr}"
        use_s, use_w = f'OR({st}="strong",{st}="depends")', f'OR({st}="weak",{st}="depends")'
        cell(lr, 22, (f'=MID(IF($N${lr}>0,CHAR(10)&CHAR(10)&INDEX({L_TEXT},$N${lr}),"")'
                      f'&IF(AND($O${lr}>0,{use_s}),CHAR(10)&CHAR(10)&INDEX({L_TEXT},$O${lr}),"")'
                      f'&IF(AND($P${lr}>0,{use_w}),CHAR(10)&CHAR(10)&INDEX({L_TEXT},$P${lr}),""),3,32000)'))
        cell(lr, 17, (f'=IF({B}="","","The lord of the "&{H}&" house ("&{bh(1, hb)}&") is placed in the "&{_ord(C)}&" house ("&{bh(1, C)}'
                      f'&"), in "&$E${lr}&". Blend their karakatwas — "&{H}&" house: "&{bh(2, hb)}&". "&{_ord(C)}&" house: "&{bh(2, C)}'
                      f'&". People: "&{bh(3, hb)}&" with "&{bh(3, C)}&". Body: "&{bh(4, hb)}&" with "&{bh(4, C)}&".")'))
        cell(lr, 18, (f'=IF({B}="","","Parivartana: the lords of the "&{_ord(lo_)}&" and "&{_ord(hi_)}&" houses have exchanged signs. '
                      f'Blend the two houses — "&{_ord(lo_)}&" house: "&{bh(2, lo_)}&". "&{_ord(hi_)}&" house: "&{bh(2, hi_)}&".")'))
        # the other direction of a Parivartana (lord of the sits-in house back in this house), its lord judged by R3
        for col, cond in ((25, '""'), (26, '"strong"'), (27, '"weak"')):
            cell(lr, col, f'=IF({B}="",0,SUMPRODUCT(({LO}={C})*({SI}={hb})*({LC}={cond})*({LX}<>"yes")*ROW({LO})))')
        cell(lr, 28, f'=IF({B}="","",{hf(H_STRENGTH, lord_y)})')
        st2 = f"$AB${lr}"
        use_s2, use_w2 = f'OR({st2}="strong",{st2}="depends")', f'OR({st2}="weak",{st2}="depends")'
        cell(lr, 29, (f'=MID(IF($Y${lr}>0,CHAR(10)&CHAR(10)&INDEX({L_TEXT},$Y${lr}),"")'
                      f'&IF(AND($Z${lr}>0,{use_s2}),CHAR(10)&CHAR(10)&INDEX({L_TEXT},$Z${lr}),"")'
                      f'&IF(AND($AA${lr}>0,{use_w2}),CHAR(10)&CHAR(10)&INDEX({L_TEXT},$AA${lr}),""),3,32000)'))
        for col, (rc, rs, rw, us, uw) in ((30, ("$N", "$O", "$P", use_s, use_w)), (31, ("$Y", "$Z", "$AA", use_s2, use_w2))):
            cell(lr, col, (f'=IF({rc}${lr}>0,INDEX({L_STATUS},{rc}${lr}),IF(AND({rs}${lr}>0,{us}),INDEX({L_STATUS},{rs}${lr}),'
                           f'IF(AND({rw}${lr}>0,{uw}),INDEX({L_STATUS},{rw}${lr}),"")))'))
        both = lambda a_, b_: f'MID(IF({a_}<>"",CHAR(10)&CHAR(10)&{a_},"")&IF({b_}<>"",CHAR(10)&CHAR(10)&{b_},""),3,32000)'
        V, AC = f"$V${lr}", f"$AC${lr}"
        cell(lr, 9, (f'=IF({B}="","",IF($L${lr},IF($M${lr}>0,INDEX({L_TEXT},$M${lr}),IF({V}&{AC}="",$R${lr},'
                     f'IF({hb}<{C},{both(V, AC)},{both(AC, V)}))),IF({V}<>"",{V},$Q${lr})))'))
        cell(lr, 10, (f'=IF({B}="","",IF($L${lr},IF($M${lr}>0,INDEX({L_STATUS},$M${lr}),IF({V}&{AC}="","blend",'
                      f'IF({hb}<{C},IF({V}<>"",$AD${lr},$AE${lr}),IF({AC}<>"",$AE${lr},$AD${lr})))),IF($AD${lr}<>"",$AD${lr},"blend")))'))
        hits = ",".join(f'{hf(H_TARGET + sl, B)}={sb}' for sl in range(3))
        cell(lr, 11, f'=IF({B}="","",IF(OR({hits}),"The lord aspects its own house, so the "&{H}&" house is strong.",""))')
        summary(lr, f'$H${lr}="strong"', f'$H${lr}="weak"', f'"The "&{H}&" lord "&{B}&" is "&$H${lr}')
        cell(lr + 1, 1, "lord (2)")
        cell(lr + 1, SUPPORT_COL, f'=IF(AND({B}<>"",$K${lr}<>""),"The "&{H}&" lord "&{B}&" aspects its own house","")')
        cell(lr + 1, PRESSURE_COL, f'=IF(AND({B}<>"",OR({C}=6,{C}=8,{C}=12)),"The "&{H}&" lord "&{B}&" is in the "&{_ord(C)}&", a difficult placement","")')
        r = lr + 2
        for k, p in enumerate(br.PLANET_ORDER):                                     # 5 · with the lord
            hrow = HELP_ROW0 + k
            cell(r, 1, "with")
            cell(r, 2, p)
            cell(r, 3, f'=AND({B}<>"",$B{r}<>{B},${L(H_SIGN)}${hrow}=$D${lr})')
            cell(r, 4, f'=${L(H_RULES)}${hrow}&""')
            txt = f'$B{r}&" ("&${L(H_NATURE)}${hrow}&") is with the "&{H}&" lord"'
            summary(r, f'AND($C{r},${L(H_CLASS)}${hrow}="benefic")', f'AND($C{r},${L(H_CLASS)}${hrow}="malefic")', txt)
            r += 1
        for k, p in enumerate(br.PLANET_ORDER):                                     # 5 · aspecting the lord
            hrow = HELP_ROW0 + k
            for sl in range(3):
                cell(r, 1, "with-aspect")
                cell(r, 2, p)
                cell(r, 3, f'=AND({B}<>"",$B{r}<>{B},${L(H_TARGET + sl)}${hrow}<>"",${L(H_TARGET + sl)}${hrow}=$D${lr})')
                cell(r, 4, f'=${L(H_ANAME + sl)}${hrow}&""')
                cell(r, 5, f'=${L(H_RULES)}${hrow}&""')
                for j in range(3):
                    cell(r, 6 + j, f"=${L(H_MEAN + 3 * sl + j)}${hrow}")
                txt = f'$B{r}&" ("&${L(H_NATURE)}${hrow}&") aspects the "&{H}&" lord"'
                summary(r, f'AND($C{r},${L(H_CLASS)}${hrow}="benefic")', f'AND($C{r},${L(H_CLASS)}${hrow}="malefic")', txt)
                r += 1
        assert r == b0 + BLOCK_ROWS, (r, b0)

    # ---- 6 · karakas
    for i, kc in enumerate(("$B$12", "$B$13")):
        r = KARAKA_ROW0 + i
        B = f"$B${r}"
        cell(r, 1, "karaka")
        cell(r, 2, f'=IF({kc}="","",{kc})')
        cell(r, 3, f'=IF({B}="","",{hf(H_HOUSE, B)})')
        cell(r, 4, f'=IF({B}="","",{hf(H_SIGN, B)})')
        cell(r, 5, f'=IF({B}="","",INDEX({names},$D${r}+1))')
        cell(r, 6, f'=IF({B}="","",{hf(H_DIG, B)})')
        cell(r, 7, f'=IF({B}="","",{hf(H_COMB, B)})')
        cell(r, 8, f'=IF({B}="","",{hf(H_RETRO, B)})')
        cell(r, 9, f'=IF({B}="","",{hf(H_STRENGTH, B)})')
        cell(r, 10, f'=IF({B}="","",$B$14)')
        summary(r, f'$I${r}="strong"', f'$I${r}="weak"', f'"Karaka "&{B}&" is "&$I${r}')

    # ---- PAC link (Love marriage) and the karakas' combination
    pac_on = '$B$6="PAC"'
    a, b = "$B$8", "$B$9"
    la, lb = f"INDEX({lords},{a})", f"INDEX({lords},{b})"
    A, Bo = _ord(a), _ord(b)
    at = lambda x: hf(H_HOUSE, x)
    hits_sign = lambda x, sgn: "OR(" + ",".join(f"{hf(H_TARGET + sl, x)}={sgn}" for sl in range(3)) + ")"
    items = [(f"{at(la)}={b}", f'{A}&" lord in the "&{Bo}'),
             (f"{at(lb)}={a}", f'{Bo}&" lord in the "&{A}'),
             (f"AND({at(la)}={b},{at(lb)}={a},{la}<>{lb})", f'"Exchange between the "&{A}&" and "&{Bo}&" lords"'),
             (f"AND({la}<>{lb},{hf(H_SIGN, la)}={hf(H_SIGN, lb)})", f'"The "&{A}&" and "&{Bo}&" lords are together"'),
             (hits_sign(la, sign_of_house(b)), f'"The "&{A}&" lord aspects the "&{Bo}&" house"'),
             (hits_sign(lb, sign_of_house(a)), f'"The "&{Bo}&" lord aspects the "&{A}&" house"'),
             (f"AND({la}<>{lb},{hits_sign(la, hf(H_SIGN, lb))})", f'"The "&{A}&" lord aspects the "&{Bo}&" lord"'),
             (f"AND({la}<>{lb},{hits_sign(lb, hf(H_SIGN, la))})", f'"The "&{Bo}&" lord aspects the "&{A}&" lord"')]
    for i, (cond, text) in enumerate(items):
        r = PAC_ROW0 + i
        cell(r, 1, "pac")
        cell(r, 2, f'=IF(AND({pac_on},{b}<>""),IF({cond},{text},""),"")')
        cell(r, SUPPORT_COL, f'=IF($B{r}<>"","PAC link: "&$B{r},"")')
    pp, qq = "$B$12", "$B$13"
    on = f'AND({pac_on},{qq}<>"")'
    name_hit = lambda x, y: (f'IF({hf(H_TARGET, x)}={hf(H_SIGN, y)},{hf(H_ANAME, x)},IF({hf(H_TARGET + 1, x)}={hf(H_SIGN, y)},'
                             f'{hf(H_ANAME + 1, x)},{hf(H_ANAME + 2, x)}))')
    links = [(f"{hf(H_SIGN, pp)}={hf(H_SIGN, qq)}", f'{pp}&" and "&{qq}&" are together in the "&{_ord(hf(H_HOUSE, pp))}'),
             (hits_sign(pp, hf(H_SIGN, qq)), f'{pp}&" aspects "&{qq}&" ("&{name_hit(pp, qq)}&" aspect)"'),
             (hits_sign(qq, hf(H_SIGN, pp)), f'{qq}&" aspects "&{pp}&" ("&{name_hit(qq, pp)}&" aspect)"')]
    for i, (cond, text) in enumerate(links):
        r = LINK_ROW0 + i
        cell(r, 1, "link")
        cell(r, 2, f'=IF({on},IF({cond},{text},""),"")')
        cell(r, SUPPORT_COL, f'=$B{r}&""')
    for c in range(3, 19):
        ws.column_dimensions[L(c)].width = 18
    for c in (SUPPORT_COL, PRESSURE_COL):
        ws.column_dimensions[L(c)].width = 40


def life_area_from_sheet(ws):
    """Read a recalculated S23_LifeArea_Calc back into the shape bhava_rules.life_area returns."""
    v = lambda r, c: ws.cell(row=r, column=c).value
    txt = lambda r, c: "" if v(r, c) is None else str(v(r, c))
    num = lambda r, c: int(round(float(v(r, c))))
    yes = lambda r, c: bool(v(r, c)) and v(r, c) not in ("FALSE", 0)
    rules_list = lambda s: [int(x) for x in s.split(",") if x.strip()]
    means = lambda r, c0: [txt(r, c0 + j) for j in range(3) if txt(r, c0 + j)]
    link = txt(6, 2)
    houses = [num(8, 2)] + ([num(9, 2)] if txt(9, 2) else [])
    bhavas, supports, pressure = [], [], []
    for blk in range(len(houses)):
        b0 = BLOCK_ROW0 + blk * BLOCK_ROWS
        r = b0 + 1
        occ = []
        for _ in range(9):
            if yes(r, 3):
                occ.append({"planet": txt(r, 2), "nature": txt(r, 4), "text": txt(r, 5), "status": txt(r, 6),
                            "nature_lines": txt(r, 7).split("\n") if txt(r, 7) else []})
            r += 1
        asp = []
        for _ in range(27):
            if yes(r, 3):
                asp.append({"by": txt(r, 2), "aspect": txt(r, 4), "meanings": means(r, 5)})
            r += 1
        lord = None
        if txt(r, 2):
            lord = {"planet": txt(r, 2), "house": num(r, 3), "sign": num(r, 4), "rashi": txt(r, 5), "placement_line": txt(r, 6),
                    "dignity": txt(r, 7), "strength": txt(r, 8), "text": txt(r, 9), "status": txt(r, 10), "dictum": txt(r, 11)}
        r += 2
        company = []
        for _ in range(9):
            if yes(r, 3):
                company.append({"planet": txt(r, 2), "how": "with", "aspect": "", "rules": rules_list(txt(r, 4)), "meanings": []})
            r += 1
        for _ in range(27):
            if yes(r, 3):
                company.append({"planet": txt(r, 2), "how": "aspect", "aspect": txt(r, 4), "rules": rules_list(txt(r, 5)),
                                "meanings": means(r, 6)})
            r += 1
        bhavas.append({"house": num(b0, 2), "sign": num(b0, 3), "rashi": txt(b0, 4), "sign_line": txt(b0, 5),
                       "occupants": occ, "aspecting": asp, "lord": lord, "with_lord": company})
    karakas = []
    for i in range(2):
        r = KARAKA_ROW0 + i
        if txt(r, 2):
            karakas.append({"planet": txt(r, 2), "house": num(r, 3), "sign": num(r, 4), "rashi": txt(r, 5), "dignity": txt(r, 6),
                            "combust": yes(r, 7), "retro": yes(r, 8), "strength": txt(r, 9), "note": txt(r, 10)})
    for r in range(BLOCK_ROW0, LINK_ROW0 + 3):
        if txt(r, SUPPORT_COL):
            supports.append(txt(r, SUPPORT_COL))
        if txt(r, PRESSURE_COL):
            pressure.append(txt(r, PRESSURE_COL))
    pac = [txt(PAC_ROW0 + i, 2) for i in range(8) if txt(PAC_ROW0 + i, 2)] if link == "PAC" else None
    plink = [txt(LINK_ROW0 + i, 2) for i in range(3) if txt(LINK_ROW0 + i, 2)] if link == "PAC" else None
    return {"no": num(4, 2), "area": txt(2, 2), "houses": houses, "link": link, "source": txt(7, 2), "bhavas": bhavas,
            "karakas": karakas, "pac": pac, "planet_link": plink, "supports": supports, "pressure": pressure}


# ---- assembly --------------------------------------------------------------------------------------
def build_calc_sheets(wb, rules):
    """(Re)create the six calculator sheets at the end of `wb`; the data sheets and everything else stay as they are."""
    for name in CALC_SHEETS:
        if name in wb.sheetnames:
            del wb[name]
    sheets = {n: wb.create_sheet(PREFIX + n) for n in CALC_NAMES}
    _chart_sheet(sheets["Chart"], rules)
    _classes_sheet(sheets["Classes_Calc"], rules)
    _roles_sheet(sheets["Roles_Calc"])
    _dasha_sheet(sheets["Dasha_Calc"])
    _predict_sheet(sheets["Predict_Calc"], rules)
    _life_area_sheet(sheets["LifeArea_Calc"], rules)
    _ref_sheet(sheets["Ref_Calc"], rules)
    for ws in sheets.values():
        ws.sheet_properties.tabColor = "2E7D78"
    return wb


def build_workbook(path, rules=None):
    """Write a standalone workbook: S23_ README, calculator and data sheets (formulas only, no cached values)."""
    rules = rules or _rules()
    wb = Workbook()
    del wb[wb.sheetnames[0]]
    b23.write_readme_sheet(wb)
    build_calc_sheets(wb, rules)
    b23.write_data_sheets(wb, rules)
    wb.active = wb.sheetnames.index(PREFIX + "Chart")
    wb.save(path)


def backup_master(master, tag):
    """Copy the workbook to backups/<name>.<tag>-YYYY-MM-DD_HHMMSS.xlsx next to it — a new file every run,
    so a second run on the same day (e.g. with --reset-data) never overwrites the earlier backup."""
    master = pathlib.Path(master)
    folder = master.parent / "backups"
    folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup, n = folder / f"{master.stem}.{tag}-{stamp}{master.suffix}", 1
    while backup.exists():
        n += 1
        backup = folder / f"{master.stem}.{tag}-{stamp}-{n}{master.suffix}"
    shutil.copy2(master, backup)
    return backup


PREVIOUS_JSON = ROOT / "session23_rules.previous.json"


def _norm_cell(v):
    if isinstance(v, str):
        v = v.strip()
        return int(v) if v.isdigit() else v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return "" if v is None else v


def _keyed(sheet, rows):
    """[(key, row)] — the key identifies a row across releases (n-th occurrence for sheets without a natural key)."""
    seen, out = {}, []
    pl = b23.PLANETS
    for row in rows:
        r = [_norm_cell(v) for v in row]
        short = sheet[len(PREFIX):]
        if short == "Classes":
            k = r[1]
        elif short in ("Badhaka", "DignityEffect", "Digbala", "DashaRoleText"):
            k = r[0]
        elif short in ("GrahaInBhava", "GrahaRashi"):
            k = (r[0], r[1])
        elif short == "GrahaPair":
            k = tuple(sorted((r[0], r[1]), key=lambda x: pl.index(x) if x in pl else 99))
        elif short == "BhavaLordIn":
            k = (r[0], r[1], r[5], str(r[6]).lower())
        elif short == "AspectMeaning":
            k = (r[0], r[1], r[2])
        elif short == "LifeAreas":
            k = r[0]
        elif short == "Conditions":
            k = (r[0], r[1], r[2])
        else:                                                    # ClassRules, BhavaNature, Remedies
            base = {"ClassRules": (r[0], r[1]), "BhavaNature": (r[0], r[1], r[2]), "Remedies": (r[0],)}[short]
            n = seen.get(base, 0)
            seen[base] = n + 1
            k = base + (n,)
        out.append((k, r))
    return out


def _sheet_rows(ws, width):
    return [list(r)[:width] + [None] * max(0, width - len(r)) for r in ws.iter_rows(min_row=2, values_only=True)
            if any(v not in (None, "") for v in r)]


def upgrade_data_sheets(wb, rules, previous):
    """Bring the S23_ data sheets of `wb` up to `rules`, keeping what the user changed.

    A row still equal to the version shipped before (`previous`) is replaced; a row the user edited is kept and
    listed; a shipped row the user deleted stays deleted; a row new in this release is added; a row the user added
    stays, after the row it followed. Missing sheets are written whole."""
    prev = dict(previous)
    for k in ("bhava_nature", "aspect_meaning", "life_areas", "conditions", "remedies"):
        prev.setdefault(k, [])
    prev["bhava_lord_in"] = [dict({"condition": "", "exchange": False}, **r) for r in prev["bhava_lord_in"]]
    new_rows, prev_rows = b23.rules_to_rows(rules), b23.rules_to_rows(prev)
    report = {"updated": 0, "added": 0, "kept": [], "deleted": [], "new_sheets": []}
    for name, header in b23.SHEETS.items():
        if name not in wb.sheetnames:
            report["new_sheets"].append(name)
            continue
        user = _keyed(name, _sheet_rows(wb[name], len(header)))
        raw = {k: row for (k, _), row in zip(user, _sheet_rows(wb[name], len(header)))}
        user_norm = dict((k, r) for k, r in reversed(user))
        shipped = dict(_keyed(name, prev_rows[name]))
        fresh = _keyed(name, new_rows[name])
        fresh_keys = {k for k, _ in fresh}
        out = []                                                   # [(key, values)]
        for (k, new), values in zip(fresh, new_rows[name]):
            if k in user_norm:
                u = user_norm[k]
                if u == new:
                    out.append((k, values))
                elif shipped.get(k) == u:
                    out.append((k, values))
                    report["updated"] += 1
                else:
                    out.append((k, raw[k]))
                    report["kept"].append((name, k))
            elif k in shipped:
                report["deleted"].append((name, k))
            else:
                out.append((k, values))
                report["added"] += 1
        before = None
        for k, u in user:
            if k not in fresh_keys and shipped.get(k) != u:       # added (or edited and since dropped) by the user
                at = next((i + 1 for i, (kk, _) in enumerate(out) if kk == before), len(out) if before else 0)
                out.insert(at, (k, raw[k]))
                if (name, k) not in report["kept"]:
                    report["kept"].append((name, k))
            before = k
        index = wb.sheetnames.index(name)
        del wb[name]
        b23.write_data_sheets(wb, {}, only={name: [v for _, v in out]}, index=index)
    if report["new_sheets"]:
        b23.write_data_sheets(wb, rules, only={n: new_rows[n] for n in report["new_sheets"]})
    return report


def install_in_master(master, rules=None, reset_data=False, previous=None):
    """Add or upgrade the S23_ sheets in the master workbook; returns a dict describing what was done.

    A backup copy is made first. A workbook without S23_ data sheets (or with reset_data) gets them written from the
    rules; one that has them is upgraded row by row (upgrade_data_sheets), so the user's edits stay. The calculator
    sheets are always rebuilt. Other sheets, merged cells, validations and formats are untouched."""
    master = pathlib.Path(master)
    rules = rules or _rules()
    backup = backup_master(master, "before-session23")
    wb = load_workbook(master)
    had_data = any(n in wb.sheetnames for n in b23.SHEETS)
    wrote_data = reset_data or not had_data
    upgrade = None
    b23.write_readme_sheet(wb)
    if wrote_data:
        b23.write_data_sheets(wb, rules)
    else:
        upgrade = upgrade_data_sheets(wb, rules, previous or json.loads(PREVIOUS_JSON.read_text(encoding="utf-8")))
    build_calc_sheets(wb, rules)
    wb.save(master)
    return {"backup": backup, "wrote_data": wrote_data, "upgrade": upgrade,
            "sheets": [n for n in wb.sheetnames if n.startswith(PREFIX)]}


def set_inputs(wb, chart, now):
    """Fill the S23_Chart sheet from a test/chart dict: {lagna, signs, degs, birth}; signs are 0-based."""
    names = [r["sanskrit"] for r in _rules()["reference"]["RASHI"]]
    ws = wb[PREFIX + "Chart"]
    ws[LAGNA_CELL] = names[chart["lagna"]]
    for k, p in enumerate(br.PLANET_ORDER):
        ws.cell(row=PLANET_ROW0 + k, column=2, value=names[chart["signs"][p]])
        ws.cell(row=PLANET_ROW0 + k, column=3, value=chart["degs"][p])
    for k, p in enumerate(br.PLANET_ORDER):
        ws.cell(row=PLANET_ROW0 + k, column=RETRO_COL, value="yes" if (chart.get("retro") or {}).get(p) else None)
    ws[GENDER_CELL] = chart.get("gender") or None
    ws[BIRTH_CELL] = chart["birth"]
    ws[NOW_CELL] = now


def store_cached_values(path):
    """Round-trip through LibreOffice so every formula's result is saved with it (previews show numbers).
    Used for the standalone export only — the master workbook is never round-tripped through LibreOffice."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("note: LibreOffice not found — saved without cached values (Excel recalculates on open).", file=sys.stderr)
        return False
    path = pathlib.Path(path)
    with tempfile.TemporaryDirectory() as tmp:
        profile = pathlib.Path(tmp) / "profile"
        out = pathlib.Path(tmp) / "out"
        out.mkdir()
        subprocess.run([soffice, f"-env:UserInstallation={profile.as_uri()}", "--headless", "--convert-to", "xlsx",
                        "--outdir", str(out), str(path)], check=True, capture_output=True, timeout=300)
        shutil.copyfile(out / path.name, path)
    return True


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    for stream in (sys.stdout, sys.stderr):      # never crash on a character the console's code page lacks
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    arg = lambda flag: argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) and not argv[argv.index(flag) + 1].startswith("--") else None
    if "--install" in argv:
        master = arg("--workbook") or b23.find_master()
        if not master:
            raise SystemExit("No Classification_for_Horoscope_Analysis_*.xlsx workbook found next to this script.")
        done = install_in_master(master, reset_data="--reset-data" in argv)
        print(f"Backup:  {done['backup']}")
        print(f"Sheets:  {', '.join(done['sheets'])}")
        up = done["upgrade"]
        if done["wrote_data"]:
            print("Data sheets written from session23_rules.json.")
        else:
            print(f"Data sheets upgraded: {up['updated']} rows updated, {up['added']} added"
                  + (f", new sheets {', '.join(up['new_sheets'])}" if up["new_sheets"] else "") + ".")
            for label, items in (("Kept your edits", up["kept"]), ("Rows you deleted stay deleted", up["deleted"])):
                if items:
                    print(f"{label}:")
                    for sheet, key in items:
                        print(f"  {sheet}: {key}")
        print("Open the workbook in Excel and save once, so the calculator results are stored with it.")
        return 0
    if "--export" in argv:
        out = pathlib.Path(arg("--export") or ROOT / "Session23_Rules.xlsx")
        build_workbook(out)
        stored = store_cached_values(out)
        print(f"wrote {out}" + ("" if stored else " (no cached values)"))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
