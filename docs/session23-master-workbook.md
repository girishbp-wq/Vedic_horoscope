# Session 23 inside the master workbook

The Session 23 rules (the ten bhāva classes, the prediction layers, the daśā roles) live in
`Classification_for_Horoscope_Analysis_v7_1.xlsx`, on sheets whose names start with **`S23_`**.
`publish.bat` rebuilds the page from them exactly as it does for the rest of the workbook.

## Python on the PC
The scripts need Python 3. In a Command Prompt, `python --version` should print `Python 3.…`.
If it prints "Python was not found; run without arguments to install from the Microsoft Store", that is only
a Windows shortcut, not Python:
- if `py --version` prints `Python 3.…`, Python is installed but not on PATH. Type `py` instead of `python`
  in the commands below (`publish.bat` finds `py` by itself);
- otherwise install Python 3 from <https://www.python.org/downloads/>, tick **Add python.exe to PATH** on the
  installer's first screen, then open a new Command Prompt. `publish.bat` installs `openpyxl` the first time;
  to do it by hand run `python -m pip install openpyxl`.

## One-time set-up (on the PC that has the workbook)
1. Pull the latest `main` in GitHub Desktop.
2. Close the workbook in Excel.
3. In the repo folder run `python make_session23_xlsx.py --install`.
   It makes a backup in the `backups` folder (`…v7_1.before-session23-DATE_TIME.xlsx`, a new one every run),
   adds the `S23_` sheets, and leaves every other sheet as it was.
4. Open the workbook in Excel and save once (this stores the calculator's results).

Running `--install` again upgrades the `S23_` data sheets row by row and rebuilds the calculator sheets:
a row still as it was shipped takes the new text, a row **you edited is kept** (and listed under "Kept your edits"),
a shipped row you deleted stays deleted, rows new in the release are added, and rows you added stay where they were.
Running it twice changes nothing. A row listed under "Kept your edits" keeps your wording and so does **not** get the
release's new text — compare it with `session23_rules.json` and copy across what you want, or run `--install
--reset-data` to overwrite every data sheet from `session23_rules.json` (your edits are then only in the backup).

## One-time fixes from the October 2026 audit
1. Pull the latest `main` in GitHub Desktop and close the workbook in Excel.
2. Run `python patch_master_workbook.py` (add `--dry-run` first to see the list without saving).
   It backs the workbook up to `backups\`, then fixes the Analysis, Input and Tithi formulas and the data cells
   the audit found. A cell you changed since is **skipped** and listed — nothing of yours is overwritten.
3. Run `python make_session23_xlsx.py --install` again, so the `S23_` calculator sheets pick up the new
   "Node (no rulership)" label and the stricter sign drop-down (your `S23_` data sheets are kept).
4. Open the workbook in Excel, save once, close it, and run `publish.bat`. The page already carries the
   regenerated data, so this publish should report no changes (or only your own edits).

## Sessions 23 (2024 deck) to 27 — one-time update
1. Pull the latest `main` in GitHub Desktop and close the workbook in Excel.
2. Run `python patch_master_workbook.py`: house tables (hands, buttocks, calves and shins, the maternal grandmother,
   Saturn as a kāraka of the 12th) and the planets' natures (Session 26: the Sun a mild malefic, the Moon and
   Mercury natural benefics) and karakatwas. Cells you changed are skipped and listed.
3. Run `python make_session23_xlsx.py --install`. It upgrades your `S23_` data sheets as described above (the 96
   readings of the Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rāhu and Ketu become the teacher's own text) and adds
   five sheets: `S23_BhavaNature`, `S23_AspectMeaning`, `S23_LifeAreas`, `S23_Conditions`, `S23_Remedies`.
4. Open the workbook in Excel, save once, close it, and run `publish.bat` — it should report no changes.

## Sessions 28-29 — one-time update
1. Pull the latest `main` in GitHub Desktop and close the workbook in Excel.
2. Run `python patch_master_workbook.py`: the 3rd house's wrist, and the planets' Session 28 karakatwas (Mars
   commanding and impatient, Jupiter satwik, Saturn traditional, Rāhu unconventional and dominating, Ketu critic and
   fault-finder, Venus kāraka for relationships, the Moon's emotional disturbance, and the "signifies" lists on
   `Planets`). Cells you changed are skipped and listed.
3. Run `python make_session23_xlsx.py --install`. It adds `S23_ChartReadings` and `S23_DegreeStages`, gives
   `S23_ClassRules` its `When` column (the Session 25 "malefic planets in Dusthana houses" line now shows only for a
   planet that is not weak), adds her Chart 3 lord-in-house rows and the Session 29 tip, and rebuilds the calculator
   sheets (strength, degree stage, her readings, the daśā down to Prāṇa). Rows you edited are kept and listed.
4. Open the workbook in Excel, save once, close it, and run `publish.bat` — it should report no changes.

## Every day
Edit a text or rule on an `S23_` data sheet, save, close Excel, double-click `publish.bat`.
It checks that the folder is on `main` and pulls it, runs `scripts\build_data.py`, then `build_session23.py`
(which rewrites `session23_rules.json` and the `SESSION23-DATA` block of `index.html`), commits only those two
files and pushes. If a push failed earlier, running it again pushes the waiting commit.
When the rebuilt page differs from the one on GitHub, the build date the page shows ("build 2026-10-11 · …")
is set to today with the note "workbook update"; a publish with no changes leaves it as it was.

`build_session23.py` checks every `S23_` cell the page relies on (planet and class names, house numbers 1–12,
statuses, one row per graha × house and per graha pair). If something is wrong it lists each problem with its
sheet and row, for example `S23_GrahaInBhava row 50: Planet 'Saturnn' is not one of Sun, Moon, …`, and
publishes nothing — fix those cells, save, and run `publish.bat` again.

## Her sentences that state a dignity
Six of her Session 28 sentences say a planet is exalted or debilitated. They show only when that is true in the chart
being read (built into the page, Python and the calculator; the rows' wording can still be edited):

| Row | Shows only when |
|---|---|
| `S23_ChartReadings`: aspects · 1st lord · House 1 ("…the bhava karaka Sun … is exalted…") | the 1st lord aspects the 1st **and** the Sun is exalted |
| `S23_BhavaLordIn`: 9 → 5 (Condition blank) | the 9th lord is exalted |
| `S23_BhavaLordIn`: 8 ↔ 12 (Exchange yes) | the 12th lord is debilitated |
| `S23_BhavaLordIn`: 7 → 4, 8 → 12, 10 → 4 (Condition weak) | that lord is debilitated |

Exalted includes Deep Exalted; debilitated includes Deep Debilitated. The rule finds its row by the key cells shown
(Kind, Planet, With, House, Condition; LordOf, SitsIn, Condition, Exchange): change one of those and the rule no
longer applies to that row. The Parivartana row is the exception: like the row itself, its rule is found by the two
houses (8 and 12, either order) with Exchange = yes, whatever its Condition.

## The sheets
| Sheet | What it is |
|---|---|
| `S23_README` | short notes |
| `S23_Classes`, `S23_ClassRules`, `S23_Badhaka` | the ten classes, their houses and the effect texts (keep `S23_ClassRules` grouped in class order; `When` = blank, or `not weak` to show the line only for a planet that is not weak) |
| `S23_DignityEffect`, `S23_Digbala` | what each dignity means; the houses of directional strength |
| `S23_DashaRoleText` | Maraka / Badhaka / Dusthana / Trishadaya wording |
| `S23_GrahaInBhava` | 108 graha × house readings; `Status` = taught / curated / blend / standard |
| `S23_GrahaPair`, `S23_BhavaLordIn`, `S23_GrahaRashi` | conjunction/aspect texts, the lord of one house in another (`Condition` strong / weak, `Exchange` yes for a Parivartana) and the teacher's worked examples |
| `S23_BhavaNature` | Session 26: a benefic or malefic in each house (blank House or Planet = any) |
| `S23_AspectMeaning` | what an aspect means (Session 24: Jupiter from each house; Session 27: Jupiter, Saturn, Mars; the default) |
| `S23_LifeAreas` | the Ready Reckoner (Session 27): 16 areas, their houses (at most two) and kārakas (at most two) |
| `S23_Conditions` | sentences that hold only for some charts; `Key` is one of a fixed list (the calculator and the page evaluate it) |
| `S23_Remedies` | the teacher's remedies and tips of the day |
| `S23_ChartReadings` | Session 28: her Chart 3 sentences. `Kind` is `in` (Planet in House, With in the same sign), `aspects` (Planet aspects House, With too), `aspects lord` (Planet aspects the lord of House) or `aspects planet` (Planet aspects the planet in With; House blank). Planet / With: a planet, `benefic`, `malefic` or `Nth lord` (`8th lord`); `Condition` blank, `exalted` or `debilitated` |
| `S23_DegreeStages` | Session 28: the degree bands (From up to, not including, To), her sentence for each, `Applies` = `any` or `malefic` (Mars, Saturn, Rāhu, Ketu), `AfterAge` = the age from which the planet gives its results |
| `S23_Chart` + `S23_*_Calc` + `S23_Ref_Calc` | the live calculator: set the Lagna, signs, degrees, Gender and Retrograde on `S23_Chart`; pick an area of life in B2 of `S23_LifeArea_Calc`. `S23_Predict_Calc` shows each planet's strength (strong / weak / mixed / depends, and why), degree stage and the first 4 of her Chart 3 sentences that hold (the page shows them all); `S23_Dasha_Calc` the running Pratyantara, Sookshma and Prāṇa |

## Python
`bhava_rules.py` reads `session23_rules.json` (generated by the publish step). Its main functions are `classification_tables`, `badhaka`,
`planet_roles`, `graha_bhava`, `bhava_bhava`, `graha_rashi`, `graha_graha`, `vimshottari`, `watch_periods`, and for
Sessions 24-27 `context`, `chart_conditions`, `aspect_meaning`, `life_area` and `life_areas`, and for Sessions 28-29
`strength_detail`, `chart_readings`, `degree_stage`, `sub_periods` and `dasha_chain`.

## A standalone copy
`python make_session23_xlsx.py --export Session23_Rules.xlsx` writes a separate workbook with the same sheets
(handy for sharing); the master stays the source of truth.

## Checks
`python -m unittest test_session23_data test_teacher_slides test_bhava_rules test_teacher_charts test_session23_cross_impl`
— compares Python, the page and the Excel formulas on random charts and on the teacher's own example charts.
