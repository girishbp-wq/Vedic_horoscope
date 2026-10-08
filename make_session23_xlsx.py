#!/usr/bin/env python3
"""Add the Session 23 calculator sheets to Session23_Rules.xlsx.

    python3 build_session23.py --seed     # (re)write the data sheets and the JSON, if you changed the rule data
    python3 make_session23_xlsx.py        # add the calculator sheets and store cached values

Sheets added (all formulas — change the signs on `Chart` and everything recalculates):

  Chart         inputs: Lagna, the nine grahas' signs and degrees, birth date-time, "now"
  Classes_Calc  the ten class tables (house, rāśi, planets, lord, where the lord sits), the house x class matrix,
                the Badhaka block and the twelve house lords
  Roles_Calc    Maraka / Badhaka / Dusthana / Trishadaya roles of the nine grahas
  Dasha_Calc    Vimśottarī: nine Mahādaśās and 81 Bhuktis from the Moon's longitude, and the running pair
  Predict_Calc  graha + bhāva: house, nature, the cell text, dignity, digbala, classes and class-rule texts
  Ref_Calc      lookup tables copied from the page (rāśi table, dignity degrees and grid, daśā constants)

The text rows are looked up in the data sheets (GrahaInBhava, ClassRules, DignityEffect, Digbala), so editing a
curated text there changes the calculator at once.  Python (bhava_rules.py) and the page (index.html) are tested
against these formulas in test_session23_cross_impl.py.
"""
import datetime
import pathlib
import shutil
import subprocess
import sys
import tempfile

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

import bhava_rules as br

ROOT = pathlib.Path(__file__).resolve().parent
XLSX = ROOT / "Session23_Rules.xlsx"
CALC_SHEETS = ["Chart", "Classes_Calc", "Roles_Calc", "Dasha_Calc", "Predict_Calc", "Ref_Calc"]

# ---- layout contract (used by the tests) -------------------------------------------------------
LAGNA_CELL, PLANET_ROW0 = "B3", 5            # Chart: Lagna sign; planets in rows 5-13 (name, sign, degree, sign #, house)
MOON_LON_CELL, SUN_LON_CELL, WAXING_CELL = "B15", "B16", "B17"
BIRTH_CELL, NOW_CELL = "B18", "B19"
CLASS_ROW0, CLASS_ROWS = 4, 33               # Classes_Calc: class tables (header row 3)
BADHAKA_ROW = 40                             # B mode, C house, D rāśi, E lord, F occupants (header row 39)
MATRIX_ROW0 = 44                             # header row; houses 1-12 in the next twelve rows
HOUSELORD_ROW0 = 61                          # twelve rows: house, rāśi, lord (header row 57)
ROLES_ROW0 = 3                               # Roles_Calc (header row 2)
DASHA_ROW0, DASHA_CUR_ROW = 24, 8            # Dasha_Calc: 81 Bhukti rows; running Mahādaśā in B8, Bhukti in B9
PREDICT_ROW0 = 3                             # Predict_Calc (header row 2); 9 planets
PREDICT_COLS = dict(planet=1, house=2, nature=3, status=4, points=5, dignity=6, dignity_line=7,
                    digbala_line=8, classes=9, class_texts=10)
FLAG_ROW0 = 16                               # Predict_Calc: class-rule flags, one row per planet (header row 15)

HEAD_FILL = PatternFill("solid", fgColor="6B1D2B")
HEAD_FONT = Font(bold=True, color="FFFFFF")
INPUT_FILL = PatternFill("solid", fgColor="FFF3D6")
WRAP = Alignment(wrap_text=True, vertical="top")
DATE_FMT = "yyyy-mm-dd hh:mm"


def _rules(path=None):
    return br.load_rules(path)


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
    return dict(name=f"Chart!$A${PLANET_ROW0 + k}", sign=f"Chart!$D${PLANET_ROW0 + k}",
                deg=f"Chart!$C${PLANET_ROW0 + k}", house=f"Chart!$E${PLANET_ROW0 + k}")


def _planets_in(house_expr):
    """Excel text: the planets whose house equals house_expr, joined by ', ' (empty string when none)."""
    parts = "&".join(f'IF(Chart!$E${PLANET_ROW0 + k}={house_expr},Chart!$A${PLANET_ROW0 + k}&", ","")' for k in range(9))
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
    for c in range(1, 38):
        ws.column_dimensions[L(c)].width = 14


# ---- Chart ---------------------------------------------------------------------------------------
def _chart_sheet(ws, rules):
    ws["A1"] = "Session 23 calculator — set the Lagna and the grahas' signs and degrees; the other sheets recalculate"
    ws["A1"].font = Font(bold=True, size=13, color="6B1D2B")
    ws["A3"] = "Lagna (rising sign)"
    ws[LAGNA_CELL] = "Simha"
    ws["D3"] = '=MATCH(B3,Ref_Calc!$B$3:$B$14,0)-1'
    _head(ws, 4, ["Graha", "Sign", "Degree in sign", "Sign # (0-11)", "House from Lagna"])
    sample = {"Moon": 6, "Ketu": 7, "Saturn": 9, "Jupiter": 10, "Mars": 3, "Sun": 2, "Venus": 2, "Mercury": 1, "Rahu": 1}
    names = [r["sanskrit"] for r in rules["reference"]["RASHI"]]
    for k, p in enumerate(br.PLANET_ORDER):
        r = PLANET_ROW0 + k
        ws.cell(row=r, column=1, value=p)
        ws.cell(row=r, column=2, value=names[sample[p]])
        ws.cell(row=r, column=3, value=15)
        ws.cell(row=r, column=4, value=f"=MATCH(B{r},Ref_Calc!$B$3:$B$14,0)-1")
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
    ws["A21"] = ("Yellow cells are inputs. The Lagna and signs have drop-downs (page spelling). "
                 "Houses count from the Lagna sign. Degrees decide Deep Exalted / Deep Debilitated and Moolatrikona.")
    ws["A21"].alignment = WRAP
    dv = DataValidation(type="list", formula1="=Ref_Calc!$B$3:$B$14", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B3")
    dv.add(f"B{PLANET_ROW0}:B{PLANET_ROW0 + 8}")
    ws.column_dimensions["A"].width = 30
    for c in "BCDE":
        ws.column_dimensions[c].width = 18


# ---- Classes_Calc ---------------------------------------------------------------------------------
def _classes_sheet(ws, rules):
    ref_names = "Ref_Calc!$B$3:$B$14"
    _head(ws, 3, ["Class", "House", "Rāśi", "Planets in it", "Lord", "Lord sits in house"])
    ws["A1"] = "The ten classes for this chart — houses are counted from the Lagna on the Chart sheet"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    row = CLASS_ROW0
    for cls in rules["classes"]:
        houses = cls["houses"] if cls["houses"] else [None]
        for h in houses:
            ws.cell(row=row, column=1, value=cls["name"])
            ws.cell(row=row, column=2, value=h if h is not None else f"=$C${BADHAKA_ROW}")
            ws.cell(row=row, column=3, value=f"=INDEX({ref_names},MOD(Chart!$D$3+B{row}-1,12)+1)")
            ws.cell(row=row, column=15, value=f"={_planets_in(f'$B{row}')}")
            ws.cell(row=row, column=4, value=f'=IF(O{row}="","",LEFT(O{row},LEN(O{row})-2))')
            ws.cell(row=row, column=5, value=f"=INDEX(Ref_Calc!$D$3:$D$14,MOD(Chart!$D$3+B{row}-1,12)+1)")
            ws.cell(row=row, column=6, value=f"=INDEX(Chart!$E${PLANET_ROW0}:$E${PLANET_ROW0 + 8},MATCH(E{row},Chart!$A${PLANET_ROW0}:$A${PLANET_ROW0 + 8},0))")
            row += 1
    assert row - CLASS_ROW0 == CLASS_ROWS, (row, CLASS_ROWS)
    ws.cell(row=CLASS_ROW0 - 1, column=15, value="(helper)")
    # Badhaka
    ws.cell(row=BADHAKA_ROW - 2, column=1, value="Badhaka for this Lagna").font = Font(bold=True, color="6B1D2B")
    _head(ws, BADHAKA_ROW - 1, ["", "Mode", "House", "Rāśi", "Badhakādhipati", "Planets in it"])
    r = BADHAKA_ROW
    ws.cell(row=r, column=1, value="Badhaka sthāna")
    ws.cell(row=r, column=2, value="=INDEX(Ref_Calc!$E$3:$E$14,Chart!$D$3+1)")
    ws.cell(row=r, column=3, value="=INDEX(Badhaka!$B$2:$B$4,MATCH(B%d,Badhaka!$A$2:$A$4,0))" % r)
    ws.cell(row=r, column=4, value=f"=INDEX({ref_names},MOD(Chart!$D$3+C{r}-1,12)+1)")
    ws.cell(row=r, column=5, value=f"=INDEX(Ref_Calc!$D$3:$D$14,MOD(Chart!$D$3+C{r}-1,12)+1)")
    ws.cell(row=r, column=15, value=f"={_planets_in(f'$C{r}')}")
    ws.cell(row=r, column=6, value=f'=IF(O{r}="","",LEFT(O{r},LEN(O{r})-2))')
    # house x class matrix
    ws.cell(row=MATRIX_ROW0 - 1, column=1, value="House × class (1 = the house belongs to the class)").font = Font(bold=True, color="6B1D2B")
    _head(ws, MATRIX_ROW0, ["House", "Rāśi"] + br.CLASS_ORDER + ["Classes"])
    houses_of = {c["name"]: c["houses"] for c in rules["classes"]}
    for h in range(1, 13):
        r = MATRIX_ROW0 + h
        ws.cell(row=r, column=1, value=h)
        ws.cell(row=r, column=2, value=f"=INDEX({ref_names},MOD(Chart!$D$3+A{r}-1,12)+1)")
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
        ws.cell(row=r, column=2, value=f"=INDEX({ref_names},MOD(Chart!$D$3+A{r}-1,12)+1)")
        ws.cell(row=r, column=3, value=f"=INDEX(Ref_Calc!$D$3:$D$14,MOD(Chart!$D$3+A{r}-1,12)+1)")
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
    hl = lambda h: f"Classes_Calc!$C${HOUSELORD_ROW0 + h - 1}"
    bad_house, bad_lord = f"Classes_Calc!$C${BADHAKA_ROW}", f"Classes_Calc!$E${BADHAKA_ROW}"
    for k, p in enumerate(br.PLANET_ORDER):
        r = ROLES_ROW0 + k
        house = f"Chart!$E${PLANET_ROW0 + k}"
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
    vo, vy, nk = "Ref_Calc!$AG$3:$AG$11", "Ref_Calc!$AH$3:$AH$11", "Ref_Calc!$AK$3:$AK$29"
    ws["A1"] = "Vimśottarī daśā from the Moon's birth-star (365.25-day years, as on the page)"
    ws["A1"].font = Font(bold=True, color="6B1D2B")
    rows = [(2, "Moon longitude (°)", f"=Chart!{MOON_LON_CELL}"),
            (3, "Nakṣatra # (0-26)", "=INT(MOD(B2,360)/(360/27))"),
            (4, "Nakṣatra lord", f"=INDEX({nk},B3+1)"),
            (5, "Part of the nakṣatra already gone", "=(MOD(B2,360)-B3*(360/27))/(360/27)"),
            (6, "Index of that lord in the daśā order", f"=MATCH(B4,{vo},0)-1"),
            (7, "Virtual start of the first Mahādaśā", f"=Chart!{BIRTH_CELL}-B5*INDEX({vy},B6+1)*365.25")]
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
        ws.cell(row=r, column=7, value=f"=IF(AND(E{r}<=Chart!{NOW_CELL},Chart!{NOW_CELL}<F{r}),1,0)")
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
                  "Digbala line", "Classes of the house", "Class-rule texts", "", "Row in GrahaInBhava", "Digbala house", "Digbala lost"])
    for k, p in enumerate(br.PLANET_ORDER):
        r = PREDICT_ROW0 + k
        pc = _planet_cells(k)
        n, d = f"({pc['sign']}+1)", pc["deg"]
        exR, exD, deR, deD, mtR, mt0, mt1 = (f"Ref_Calc!${c}${3 + k}" for c in "JKLMNOP")
        base = f"INDEX(Ref_Calc!$R${3 + k}:$AC${3 + k},{n})"
        dignity = (f'=IF({base}="Exalted",'
                   f'IF(AND({n}={mtR},{d}>{exD}),IF(AND({d}>={mt0},{d}<={mt1}),"Own (Moolatrikona)","Own House"),'
                   f'IF(AND({n}={exR},ABS({d}-{exD})<=1),"Deep Exalted","Exalted")),'
                   f'IF({base}="Debilitated",IF(AND({n}={deR},ABS({d}-{deD})<=1),"Deep Debilitated","Debilitated"),'
                   f'IF({base}="Own (Moolatrikona)",IF(AND({d}>={mt0},{d}<={mt1}),"Own (Moolatrikona)","Own House"),{base})))')
        mercury = PLANET_ROW0 + 3
        spoil = ",".join(f"Chart!$D${PLANET_ROW0 + br.PLANET_ORDER.index(o)}=Chart!$D${mercury}" for o in ("Mars", "Saturn", "Rahu", "Ketu"))
        nature = (f'=IF(OR($A{r}="Jupiter",$A{r}="Venus"),"benefic",IF($A{r}="Moon",IF(Chart!{WAXING_CELL},"benefic","malefic"),'
                  f'IF($A{r}="Mercury",IF(OR({spoil}),"malefic","benefic"),"malefic")))')
        ws.cell(row=r, column=1, value=p)
        ws.cell(row=r, column=2, value=f"={pc['house']}")
        ws.cell(row=r, column=3, value=nature)
        ws.cell(row=r, column=4, value=f"=INDEX(GrahaInBhava!$E$1:$E$300,$L{r})")
        ws.cell(row=r, column=5, value=f"=INDEX(GrahaInBhava!$C$1:$C$300,$L{r})")
        ws.cell(row=r, column=6, value=dignity)
        ws.cell(row=r, column=7, value=f'=IFERROR($F{r}&": "&INDEX(DignityEffect!$C$2:$C$10,MATCH($F{r},DignityEffect!$A$2:$A$10,0)),"")')
        ws.cell(row=r, column=8, value=(
            f'=IF($B{r}=$M{r},$A{r}&" gains directional strength (digbala) in the "&{_ord(f"$B{r}")}&" house.",'
            f'IF($B{r}=$N{r},$A{r}&" loses directional strength (digbala) in the "&{_ord(f"$B{r}")}&" house, '
            f'opposite its strongest house, the "&{_ord(f"$M{r}")}&".",""))'))
        ws.cell(row=r, column=9, value=f"=INDEX(Classes_Calc!$M${MATRIX_ROW0 + 1}:$M${MATRIX_ROW0 + 12},$B{r})")
        fr = FLAG_ROW0 + k
        joined = "&".join(f'IF({L(2 + m)}{fr}=1,CHAR(10)&ClassRules!$D${2 + m},"")' for m in range(n_rules))
        ws.cell(row=r, column=10, value=f"=MID({joined},2,32000)")
        ws.cell(row=r, column=12, value=(f"=SUMPRODUCT((GrahaInBhava!$A$2:$A$300=$A{r})*(GrahaInBhava!$B$2:$B$300=$B{r})"
                                         f"*ROW(GrahaInBhava!$A$2:$A$300))"))
        ws.cell(row=r, column=13, value=f"=IFERROR(INDEX(Digbala!$B$2:$B$8,MATCH($A{r},Digbala!$A$2:$A$8,0)),0)")
        ws.cell(row=r, column=14, value=f"=IFERROR(INDEX(Digbala!$C$2:$C$8,MATCH($A{r},Digbala!$A$2:$A$8,0)),0)")
    # class-rule flags
    ws.cell(row=FLAG_ROW0 - 2, column=1, value="Which ClassRules rows apply to each graha (1 = applies)").font = Font(bold=True, color="6B1D2B")
    _head(ws, FLAG_ROW0 - 1, ["Graha"] + [f"rule {m + 1}" for m in range(n_rules)])
    matrix = f"Classes_Calc!$C${MATRIX_ROW0 + 1}:$L${MATRIX_ROW0 + 12}"
    for k, p in enumerate(br.PLANET_ORDER):
        fr, pr = FLAG_ROW0 + k, PREDICT_ROW0 + k
        ws.cell(row=fr, column=1, value=p)
        for m in range(n_rules):
            cr = 2 + m
            f = (f'=IF(AND(INDEX({matrix},$B{pr},MATCH(ClassRules!$A${cr},Ref_Calc!$AE$3:$AE$12,0))=1,'
                 f'OR(ClassRules!$B${cr}="any",ClassRules!$B${cr}=$C{pr}),'
                 f'NOT(ISNUMBER(SEARCH(", "&$B{pr}&",",", "&ClassRules!$C${cr}&",")))),1,0)')
            ws.cell(row=fr, column=2 + m, value=f)
    for c, w in zip("ABCDEFGHIJ", (12, 7, 9, 10, 60, 20, 50, 50, 28, 60)):
        ws.column_dimensions[c].width = w
    for r in range(PREDICT_ROW0, PREDICT_ROW0 + 9):
        for c in (5, 7, 8, 10):
            ws.cell(row=r, column=c).alignment = WRAP


# ---- assembly --------------------------------------------------------------------------------------
def build_workbook(path, source=None, rules=None):
    """Write `path`: the data sheets from `source` (default Session23_Rules.xlsx) plus the calculator sheets
    (formulas only; use `store_cached_values` to add the results)."""
    rules = rules or _rules()
    wb = load_workbook(source or XLSX)
    for name in CALC_SHEETS:
        if name in wb.sheetnames:
            del wb[name]
    sheets = {name: wb.create_sheet(name, 1 + i) for i, name in enumerate(CALC_SHEETS)}
    _chart_sheet(sheets["Chart"], rules)
    _classes_sheet(sheets["Classes_Calc"], rules)
    _roles_sheet(sheets["Roles_Calc"])
    _dasha_sheet(sheets["Dasha_Calc"])
    _predict_sheet(sheets["Predict_Calc"], rules)
    _ref_sheet(sheets["Ref_Calc"], rules)
    readme = wb["README"]
    if not any("calculator" in str(c.value).lower() for c in readme["A"]):
        for line in ("Calculator sheets (Chart, Classes_Calc, Roles_Calc, Dasha_Calc, Predict_Calc, Ref_Calc) are added by "
                     "python3 make_session23_xlsx.py — set the signs on Chart; everything else is formulas.",):
            readme.cell(row=readme.max_row + 1, column=1, value=line).alignment = WRAP
    wb.active = wb.sheetnames.index("Chart")
    wb.save(path)


def set_inputs(wb, chart, now):
    """Fill the Chart sheet from a test/chart dict: {lagna, signs, degs, birth}; signs are 0-based."""
    names = [r["sanskrit"] for r in _rules()["reference"]["RASHI"]]
    ws = wb["Chart"]
    ws[LAGNA_CELL] = names[chart["lagna"]]
    for k, p in enumerate(br.PLANET_ORDER):
        ws.cell(row=PLANET_ROW0 + k, column=2, value=names[chart["signs"][p]])
        ws.cell(row=PLANET_ROW0 + k, column=3, value=chart["degs"][p])
    ws[BIRTH_CELL] = chart["birth"]
    ws[NOW_CELL] = now


def store_cached_values(path):
    """Round-trip through LibreOffice so every formula's result is saved with it (previews show numbers)."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("note: LibreOffice not found — saved without cached values (Excel recalculates on open).", file=sys.stderr)
        return False
    path = pathlib.Path(path)
    with tempfile.TemporaryDirectory() as tmp:
        profile = pathlib.Path(tmp) / "profile"
        out = pathlib.Path(tmp) / "out"
        out.mkdir()
        subprocess.run([soffice, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "xlsx",
                        "--outdir", str(out), str(path)], check=True, capture_output=True, timeout=300)
        shutil.copyfile(out / path.name, path)
    return True


def main(argv=None):
    build_workbook(XLSX)
    stored = store_cached_values(XLSX)
    print(f"wrote {XLSX.name} with calculator sheets" + ("" if stored else " (no cached values)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
