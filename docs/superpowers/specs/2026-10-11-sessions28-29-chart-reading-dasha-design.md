# Sessions 28–29 (Round 1 of 3): chart reading, strength and the deeper daśā periods — design

Date: 2026-10-11 · Status: approved in conversation (parts 1–3), awaiting written-spec review

Round 1 of the Sessions 28–32 work. Round 2 is the yogas (Sessions 29–30); Round 3 is Muhūrta (Sessions 31–32).
Each round gets its own spec, plan, build and release.

## 1. Purpose and success criteria

Bring the website (`index.html`), the master workbook (`S23_` sheets and calculator) and the Python engine
(`bhava_rules.py`) up to date with Session 28 (one chart read house by house; degree stages) and the daśā and
strength parts of Session 29, the same way Sessions 23–27 were added (spec `2026-10-10-sessions23-27-…-design.md`,
whose rulings R1–R11 stay in force).

Done means:
1. Every rule in §6 is implemented in page, Python and Excel, and the three agree on 2,000 random charts.
2. Her charts in §9.1 pass as fixed test cases: the site never contradicts a conclusion she drew.
3. The user upgrades the workbook with one command; edited rows are kept and listed (as in Sessions 23–27).
4. `publish.bat` after the upgrade reports no changes.

## 2. Provenance and decisions

### 2.1 Decks (labels used in every `source` field)
| Label | File | Content used |
|---|---|---|
| `S28` | 28_Vedic_Astrology_SESSION_-28.pdf (12/09/2024, 17 pp.) | Chart 3 read bhāva by bhāva (pp. 2–16); "Meaning Of Degrees in a Horoscope" (p. 17) |
| `S29` | SESSION_-_29.pdf (18/09/2024, 50 pp.) | Vimśottarī in depth (pp. 2–15); planet strength (p. 17, p. 29); S27 Chart 1 gender and birth time (p. 31); tip (p. 50). Its yogas (pp. 16–49) are Round 2. |

Slide-by-slide transcriptions: session scratchpad `s28_32/28_notes.md`, `29_notes.md` (text layer + every page viewed).
Texts are copied from them, never paraphrased; obvious misspellings are fixed only where the meaning is unchanged
and listed in the module docstring, as in Sessions 23–27.

### 2.2 Decisions confirmed by the user
| # | Decision |
|---|---|
| D1 | **Strength (choice B):** weak = debilitated, enemy's sign, combust, or with Rāhu; strong = exalted, Moolatrikona, own or friend's sign with no malefic aspect; **mixed** = strong by sign but aspected by a malefic (named); depends = otherwise. Aspecting its own house no longer makes a planet strong. |
| D2 | **Her Chart 3 is followed in all five places the site disagreed** ("keep it as she says"): §6.2. |
| D3 | **Degree stages (choice A):** shown on each planet card with her sentence; nothing else changes. |
| D4 | **Deeper daśā (choice A):** a running chain to Prāṇa and open-on-click tables; Python and Excel likewise. |
| D5 | Design parts 1–3 as presented (data, rules, page/Excel/delivery/checks). |

### 2.3 Rulings (where the slides disagree, are silent, or my wording changed after approval)
| # | Ruling | Why |
|---|---|---|
| S1 | A sign of weakness wins over a good sign (exalted + combust, or exalted + with Rāhu → **weak**). Today R3 says "depends". | S29 p.29: "though Jupiter is exalted, it has become weak due to the influence of Rahu" |
| S2 | Only **Rāhu** in the same sign weakens; Ketu does not (not stated). Malefics for "mixed": Sun (mild), Mars, Saturn, Rāhu, Ketu, with the site's aspects (Rāhu/Ketu forward 5/9/12, R7). | S29 pp. 17, 29; R10 |
| S3 | **Fixes 1 and 2 of §6.2 test "debilitated", not "weak".** On her Chart 3 the Lagna lord Jupiter sits in an enemy's sign (weak under D1), yet she reads its aspect on the Lagna as good health (p. 2) and Jupiter in the 7th as a wise, advising spouse (p. 9). Her negative readings are for *debilitated* planets (p. 6 "though it is a benefic it is weak and debilitated"; p. 13). Fixes 3–5 stay as approved. | keeps every conclusion of Chart 3 (§9.1) |
| S4 | Her Chart 3 sentences apply to any chart with the same placement, marked "In her example chart (S28): …" — as the Session 27 examples are. A sentence that depends on dignity carries that condition. | S27 precedent (R11, review fix) |
| S5 | The 4↔7 exchange in Chart 3 is not named by her: no Parivartana row; the existing exchange logic shows both her 4→7 and 7→4 lines. Her 8↔12 exchange gets an `Exchange = yes` row. | S28 pp. 6, 10, 16 |
| S6 | "Could get inheritance" (p. 15, 8th lord aspects 11th lord) and "might lose his inheritance" (p. 16, 8↔12) both show as written. | she does not reconcile them |
| S7 | On the 11th her aspects are read through one lordship per planet; the site names **all** houses the aspecting planet rules. | p. 14 names one, without a rule for choosing |
| S8 | Degree bands are closed by whole degrees: infant 0°00′–0°59′, young 1°00′–5°59′, adult 6°00′–17°59′, mature 18°00′–25°59′, old 26°00′–29°59′. "At 0 degree" adds its own sentence for 0°00′–0°00′59″ (shown as 0°00′). Bands apply to Rāhu and Ketu too (she names them). | p. 17 overlaps at 1° and leaves gaps at 5–6, 17–18, 25–26 |
| S9 | Daśā dates come from the formula with the site's 365.25-day years (her software's dates match on the 1982 chart). Her hand-worked y-m-d figures (pp. 13–14) truncate and are not used. | S29 §4.3 of the notes |
| S10 | "Afflicted" (R5: debilitated, enemy's sign, combust) for the conditional sentences is unchanged. | S24/S25 definition; S29 defines strength, not affliction |
| S11 | Parentheses round a planet in her software charts mean retrograde (S30 p.16 confirms); used in the test fixtures only. | S28 notes §7 |
| S12 | The lineage statement of S29 p.2 is not published (by tradition Vasishtha is Parāśara's grandfather). | factually doubtful |

## 3. Scope

In: everything in §5–§8. Out: yogas (Round 2, including Mahā Bhāgya's day/night input); Muhūrta (Round 3);
the tips of Sessions 30–32; changes to the Kuja-doṣa section (S28 agrees with it); a numeric strength score.

## 4. Architecture

Unchanged: **master workbook `S23_` sheets → `build_session23.py` → `session23_rules.json` + the
`SESSION23-DATA` block of `index.html`**; page (`SESSION23-ENGINE` / `-RENDER`), Python (`bhava_rules.py`) and Excel
(`S23_*_Calc` built by `make_session23_xlsx.py`) read the same data. Tables outside S23 change through guarded
edits in `patch_master_workbook.py`. Teacher texts are kept in a module like `session23_teacher_slides.py`
(`session28_29_teacher_texts.py`) and applied to the previous JSON, so the release regenerates byte-identically.

## 5. Data model (workbook sheets → JSON keys)

Existing sheets (rows change):
| Sheet → key | Change |
|---|---|
| `S23_BhavaLordIn` → `bhava_lord_in` | + S28 rows 2→9, 3→9, 4→7, 5→8, 6→6, 9→5, 11→6 (`Condition` blank); 7→4, 8→12, 10→4 with `Condition = weak` (her text speaks of a debilitated lord); + 8↔12 with `Exchange = yes`. Each text starts "In her example chart (S28): ". 1→7 already holds her S26 text (p. 2 repeats it). |
| `S23_ClassRules` → `class_rules` | New column `When` (blank or `not weak`); the S25 p.10 Dusthana-malefic row gets `not weak` (§6.2 fix 5). |
| `S23_Remedies` → `remedies` | + S29 p.50 tip (Topic "Tip"). |

New sheets:
| Sheet → key | Columns | Rows |
|---|---|---|
| `S23_ChartReadings` → `chart_readings` | Kind (`in` / `aspects` / `aspects lord`), Planet, With, House, Condition, Text, Status, Source | Her Chart 3 sentences (S28 pp. 2–16; about 35 rows). **Planet / With:** a planet name, `benefic`, `malefic`, or `Nth lord` (e.g. `8th lord`); With blank = alone. **House:** the house the planet is in, aspects, or whose lord it aspects. **Condition:** blank, `exalted` or `debilitated` (of Planet). Examples: (`in`, Rahu, —, 10) professions; (`in`, Mercury, Ketu, 4, debilitated) break in education; (`aspects`, malefic, malefic, 2) no easy flow of money; (`aspects`, Saturn, —, 6) chronic disease; (`aspects lord`, Rahu, —, 11) gains from foreign sources. |
| `S23_DegreeStages` → `degree_stages` | From, To (degrees, To exclusive), Stage, Applies (`any` / `malefic`), AfterAge, Text, Source | The bands of S8 with her sentences; "At 0 degree" (0 to 1/60, AfterAge 30); infant (AfterAge 32, her "30-32"); her malefic sentence twice (0–1 and 26–30, Applies `malefic` = Mars, Saturn, Rāhu, Ketu as she names them). |

`build_session23.py` validation covers the new sheets: allowed kinds, planets/`benefic`/`malefic`/`Nth lord`,
houses 1–12, conditions, statuses; degree bands from 0 to 30 without overlap per `Applies`; unique keys
(Kind, Planet, With, House, Condition) and (From, Applies).

### 5.1 Outside S23 (guarded patch, appended only — R8)
- Bhava Info: 3rd body + "wrist".
- Planet Profile / Characteristics karakatwas: Ketu — critic, fault-finder, litigation, small; Rāhu — unconventional,
  dominating, foreign sources or outsiders, different cuisines, wide (eyes); Mars — red (eyes), spicy and hot food,
  commanding, impatient; Saturn — delay, chronic disease, traditional; Jupiter — satwik, big handwriting, friend
  circle, advice; Venus — karaka for relationships, daughter, hormonal imbalance; Moon — emotional disturbance
  leading to disease; Sun — government, administrator.

## 6. Engine behaviour (page = Python = Excel)

### 6.1 Strength (`strength()` / `s23Strength`; D1, S1, S2)
Returns `{word, reasons}` with word one of `strong`, `weak`, `mixed`, `depends`:
1. **weak** if debilitated / deep debilitated, in an enemy's sign, combust, or Rāhu in the same sign;
2. else **strong** if exalted, deep exalted, Moolatrikona, own or friend's sign, and no malefic aspects it;
3. else **mixed** if such a sign but a malefic aspects it — `reasons` names each aspecting malefic;
4. else **depends**.
Where her rows differ for a strong and a weak lord (`Condition`), `mixed` and `depends` show both. The page chip
reads e.g. "mixed — aspected by Saturn (S29)". Callers that compared the old string compare `word`.

### 6.2 Her Chart 3 corrections (D2, S3)
1. The dictum line ("The lord aspects its own house, so the Xth house is strong", and its Life-areas support) shows
   only when the lord is **not debilitated**.
2. A benefic in a house that is **debilitated** counts as **pressure** in the Life-areas summary, named
   "Mercury (benefic, debilitated) in the 4th".
3. A **kāraka** in the 6th, 8th or 12th, or aspected by a malefic, counts as **pressure** ("Karaka Venus is in the
   6th", "Karaka Venus is aspected by Rahu"); otherwise a strong kāraka is a support as now.
4. On the **11th house**, every aspecting planet counts as a **support**, named with the houses it rules ("Sun aspects
   the 11th (rules the 9th)"). On every other house the planet's nature decides, as now.
5. A class rule with `When = not weak` (the S25 Dusthana-malefic line) shows only when the planet is not weak.

### 6.3 Aspects carry the houses their planet rules (S28 p.14)
Every list of planets aspecting a house (Layer 2 entry, Life-areas step 3) gives each planet's ruled houses, as the
"with / aspecting the lord" list already does: `{by, aspect, rules, meanings}`.

### 6.4 Chart readings (`chart_readings(rules, ctx)`)
A row matches when:
- `in`: Planet (or a planet of that nature, or the `Nth lord`) is in House, With (if given) is in the same sign, and
  Condition (if given) holds for Planet;
- `aspects`: Planet aspects House and With (if given) also aspects it (two different planets for `malefic`+`malefic`);
- `aspects lord`: Planet aspects the planet that rules House.
Matches show: `in` on that planet's Layer-1 card; `aspects` with the house's aspects (Layer 2 entry and Life-areas
step 3); `aspects lord` with that lord (Layer 2 "with / aspecting the lord", Life-areas step 5). Each keeps her label.

### 6.5 Degree stage (`degree_stage(rules, planet, deg, age)`)
The band containing the planet's degree in its sign (S8), her sentence, and for Mars, Saturn, Rāhu, Ketu in 0–1° or
26–30° her malefic sentence. With an age and an AfterAge: "Age 34: past 32, so it now gives its results" or "Age 25:
results from about 32". Without a degree, nothing is shown. Nothing else depends on it (D3).

### 6.6 Deeper Vimśottarī periods (D4, S9)
`sub_periods(rules, lord, start, years)` → the nine children of a period (same order from its lord, each
`years × child_years / 120`). `dasha_chain(rules, dasha, now)` → the running Mahādaśā, Bhukti, Pratyantara, Sookshma
and Prāṇa, each with lord, start and end. Nine children always add up to the parent exactly. Outside the 120-year
span nothing is "running", as now.

## 7. UI

- **Graha + Bhāva cards:** strength chip with reasons (§6.1); degree-stage line (§6.5); "In her example chart
  (S28)" lines that match (§6.4); the S25 Dusthana line only when allowed (§6.2.5).
- **Layer 2 table:** each house's aspects with ruled houses and matching readings; mixed/depends show both of her
  lines; the dictum chip follows §6.2.1.
- **Life areas:** the corrected summary (§6.2) and ruled houses on every aspect.
- **Daśā–Bhukti tab:** a "Running now" line (Mahādaśā › Bhukti › Pratyantara › Sookshma › Prāṇa with dates); each
  Bhukti row opens to its nine Pratyantaras, each of those to its Sookshmas, each of those to its Prāṇas
  (built when opened). Print shows the running chain and the open rows. Phone width: no horizontal page scroll.
- **Remedies:** the S29 tip joins "Tips of the day".
- **Build stamp:** `build_session23.py --stamp` on release.

## 8. Workbook delivery

- `make_session23_xlsx.py --install` adds `S23_ChartReadings` and `S23_DegreeStages`, the `When` column, and
  upgrades the data sheets row by row (unchanged rows take the new text, edited rows are kept and listed).
- Calculator sheets:
  - `S23_Predict_Calc`: the new strength word and reasons; degree stage and malefic line; the first 4 matching `in`
    readings per planet (the page and Python show all; a fifth match adds "(more on the page)"); the S25 line by `When`.
  - `S23_LifeArea_Calc`: §6.2 summary rules; ruled houses on aspects; matching `aspects` / `aspects lord` readings
    (the first 4 per house, as above).
  - `S23_Dasha_Calc`: running Pratyantara, Sookshma, Prāṇa (lord, start, end) and the nine Pratyantaras of the
    running Bhukti.
  - Excel 2007 functions only (no TEXTJOIN); every formula under 8,192 characters.
- `patch_master_workbook.py`: §5.1, skipping cells the user changed.
- PC steps after release: pull; `py patch_master_workbook.py`; `py make_session23_xlsx.py --install`; open in Excel,
  save, close; `publish.bat` reports no changes.

## 9. Testing

### 9.1 Her charts as fixed cases
- **S28 Chart 3** (male, Dhanu Lagna; Sun Mesha 10°, Moon Vṛścika 1° waning, Mars Kataka 11°, Mercury Mīna 21°,
  Jupiter Mithuna 8°, Venus Vṛṣabha 3°, Saturn Siṁha 0° (R), Rāhu Kanyā 10°, Ketu Mīna 10°; Mercury retrograde):
  - 10th lord Mercury is weak; no "10th house is strong" line; her 10→4 line shows;
  - Lagna lord Jupiter aspects the Lagna: "1st house is strong" shows (not debilitated); Health support includes it;
  - Degree Education: "Mercury (benefic, debilitated) in the 4th" is pressure;
  - Marriage: "Karaka Venus is in the 6th" and "Karaka Venus is aspected by Rahu" are pressure; Venus is "mixed";
  - Elder sibling (11th): Sun, Mars, Jupiter, Saturn aspects are supports with ruled houses (Sun 9; Jupiter 1, 4;
    Mars 5, 12; Saturn 2, 3);
  - Mars in the 8th: no S25 "give good results" line;
  - her 2→9, 3→9, 4→7, 5→8, 6→6, 9→5, 11→6, 7→4, 8→12, 10→4 lines and the 8↔12 Parivartana line show;
  - matching chart readings: Rāhu in the 10th (professions), Venus in the 6th, Mars/Rāhu on the 2nd, Saturn/Moon/Rāhu
    on the 6th, Ketu on the 8th, Rāhu on the 11th lord, and every other `S23_ChartReadings` row whose placement matches;
  - degree stages: Saturn 0° "At 0 degree" + infant + malefic line; Moon 1° young.
- **S29 Chart A** (male, 8 June 1982, Moon Dhanu 13°36′37″): birth daśā Venus; Venus–Venus at birth; Bhukti
  boundaries on the days of her software (p. 8); on 18/09/2024 Mars–Moon, Moon Bhukti ending 07/01/2025; deeper
  levels: nine children sum to the parent; the chain on 18/09/2024 matches an independent calculation.
- **S27 Chart 1:** gender Male, birth 10:10 (day) added to the fixture; existing assertions unchanged.

### 9.2 Cross-implementation
Page vs Python on 2,000 random charts (strength word and reasons, chart readings, degree stages, Life-areas
summary, daśā chain); Excel vs Python through LibreOffice on the fixed charts and probe charts for every new rule.

### 9.3 Other
Workbook upgrade keeps edited rows of the new sheets; validation messages name sheet and row; `publish.bat`
reports no changes after the upgrade (byte-identical regeneration).

## 10. Phasing
1. Texts and data (sheets, JSON, validation, patch). 2. Strength and §6.2. 3. Aspects with ruled houses and chart
readings. 4. Degree stages. 5. Deeper daśā. 6. Page. 7. Excel. 8. Fixtures, full suite, independent review, release.

## 11. Risks
- The strength change moves many planets from strong to mixed (measured: 11% strong, 31% mixed, 34% weak, 23%
  depends, against 54% / 0 / 16% / 30% today); the page explains each word with its reasons.
- Excel formula length with chart-reading matches: helper columns, as for Life areas.
- Her chart sentences are specific to one chart; the label keeps that visible.
