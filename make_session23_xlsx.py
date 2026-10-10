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
CALC_NAMES = ["Chart", "Classes_Calc", "Roles_Calc", "Dasha_Calc", "Predict_Calc", "Ref_Calc"]
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
    for c in range(1, 38):
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
    sex = DataValidation(type="list", formula1='"Male,Female"', allow_blank=True)
    ws.add_data_validation(sex)
    sex.add(GENDER_CELL)
    yes = DataValidation(type="list", formula1='"yes"', allow_blank=True)
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
    for k, p in enumerate(br.PLANET_ORDER):
        fr, r = NATURE_FLAG_ROW0 + k, PREDICT_ROW0 + k
        ws.cell(row=fr, column=1, value=p)
        kind = f'IF($C{r}="benefic","benefic","malefic")'
        for m in range(n_bn):
            b = 2 + m
            h, nat, pl = f"S23_BhavaNature!$A${b}", f"S23_BhavaNature!$B${b}", f"S23_BhavaNature!$C${b}"
            ws.cell(row=fr, column=2 + m, value=(f'=IF(AND(OR({nat}={kind},{nat}="any"),OR({h}="",{h}=$B{r}),OR({pl}="",{pl}=$A{r})),'
                                                 f'IF({h}="",0,IF({pl}="",1,2)),-1)'))
    for k, p in enumerate(br.PLANET_ORDER):
        r, fr = PREDICT_ROW0 + k, NATURE_FLAG_ROW0 + k
        ws.cell(row=r, column=15, value=f'=IF($A{r}="Moon",IF(S23_Chart!{WAXING_CELL},"Shukla (waxing) — stronger","Krishna (waning) — weaker"),"")')
        passes = "&".join(f'IF({L(2 + m)}{fr}={g},CHAR(10)&${L(MILD_COL)}{r}&S23_BhavaNature!$D${2 + m},"")'
                          for g in range(3) for m in range(n_bn))
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


def install_in_master(master, rules=None, reset_data=False):
    """Add the S23_ sheets to the master workbook; returns a dict describing what was done.

    A backup copy is made first.  The data sheets are written only when missing (or with reset_data); the
    calculator sheets are always rebuilt.  Other sheets, merged cells, validations and formats are untouched."""
    master = pathlib.Path(master)
    rules = rules or _rules()
    backup = backup_master(master, "before-session23")
    wb = load_workbook(master)
    had_data = b23.has_session23_sheets(wb)
    wrote_data = reset_data or not had_data
    b23.write_readme_sheet(wb)
    build_calc_sheets(wb, rules)
    if wrote_data:
        b23.write_data_sheets(wb, rules)
    wb.save(master)
    return {"backup": backup, "wrote_data": wrote_data, "sheets": [n for n in wb.sheetnames if n.startswith(PREFIX)]}


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
        print("Data sheets " + ("written from session23_rules.json." if done["wrote_data"] else "already present — left as you edited them."))
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
