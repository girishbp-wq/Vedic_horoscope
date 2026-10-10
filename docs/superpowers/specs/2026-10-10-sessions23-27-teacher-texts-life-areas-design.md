# Sessions 23 (2024 deck) – 27: teacher's texts, new rules and Life areas — design

Date: 2026-10-10 · Status: approved in conversation, awaiting written-spec review

## 1. Purpose and success criteria

Bring the website (`index.html`), the master workbook (`S23_` sheets and calculator) and the Python engine
(`bhava_rules.py`) up to date with the teacher's slides for Sessions 23 (2024 edition) to 27, the same way
Session 23 was added:

- the teacher's own words replace every drafted ("curated") reading;
- the rules she teaches are applied to every chart, identically in page, Python and Excel;
- a new **Life areas** section runs her 7-step method for a chosen area of life.

Done means:
1. All 108 planet-in-house readings carry her text (`status: taught`), none curated.
2. Every rule in §6 is implemented in page, Python and Excel, with tests showing the three agree on random charts.
3. Her worked charts (§9.1) pass as fixed test cases: the page never contradicts what she concluded.
4. The user upgrades the workbook with one command; edits made in the workbook are never overwritten silently.
5. `publish.bat` after the upgrade reports no changes (the page already carries the regenerated data).

## 2. Provenance and decisions

### 2.1 Decks (labels used in every `source` field)
| Label | File | Content used |
|---|---|---|
| `S23-2024` | 23.vedic_astrology_session_-_23.pdf (01/08/2024, 45 pp.) | Moon, Mars, Mercury in houses 1-12; 4 example charts; 3 Moon-in-sign rules; Moon remedies; Mercury → Lord Vishnu; Mars digbala 10th |
| `S23` | the 08/10/2026 deck already implemented | unchanged (classes, roles, Sun in houses, layers) |
| `S24` | 24._vedic_astrology_session__24_bhavas_2.pdf (38 pp.) | Jupiter, Venus in houses 1-12; Jupiter's aspect from each house; timing, gender and affliction rules |
| `S25` | 25._vedic_astrology_25_planets_in_bhavas.pdf (42 pp.) | Saturn, Rahu, Ketu in houses 1-12; ~45 rules; remedy |
| `S26` | 26._Vedic_Astrology_SESSION_-_26.pdf (28 pp.) | benefic/malefic classes; benefic/malefic in each house; Lagna lord in houses 1-12; tip |
| `S27` | 27._Vedic_Astroogy__Session_27...pdf (25 pp.) | aspect meanings; 7-step method; Layer 2 method and dictum; Ready Reckoner; PAC; 2 worked charts; tip |

Slide-by-slide transcriptions are in the session scratchpad (`s24_27/*_notes.md`, `23_diff.md`); the
implementation copies texts from those transcriptions and the PDFs, never paraphrased.

### 2.2 Decisions confirmed by the user
1. **Benefic/malefic (S26):** Jupiter, Venus, Mercury, Moon benefic; Saturn, Mars, Rahu, Ketu malefic; Sun a
   *mild malefic*. The Moon's waxing/waning and Mercury's company no longer change its nature; waxing/waning is
   shown as the Moon's strength only.
2. **Life areas:** a new section running the 7-step method for each Ready Reckoner area, mirrored in Python and Excel.
3. **Approach A:** extend the Session 23 machinery (same `S23_` sheets, JSON, `publish.bat`).
4. Design Parts 1-4 (content, rules, Life areas, delivery) as presented in conversation, including the rulings in §2.3.

### 2.3 Rulings (where the slides disagree or are silent)
| # | Ruling | Why |
|---|---|---|
| R1 | Later or more specific session wins; earlier statements are kept where not contradicted. | user-approved default |
| R2 | Malefics in Upachaya (3, 6, 10, 11): "results come through struggle and effort and grow with time — mostly in the 30s". | joins S23 ("good results in their daśā"), S26 ("struggle and effort"), S23-2024/S24 ("in the 30s") |
| R3 | Strong Lagna lord = exalted/deep exalted, Moolatrikona, own sign, friend's sign, or aspecting its own house; weak = debilitated, enemy's sign or combust; otherwise both of her lines show, marked "depends on strength". | S26 pp. 21, 23 do not define strength |
| R4 | Female chart: husband's karaka is Mars (S27 Ready Reckoner); Jupiter also signifies the husband (S24) and is named as a note. Male chart: wife's karaka Venus; Venus's house shows where he meets his wife (S24). Gender rules apply only when the form's gender is filled. | S24 and S27 differ |
| R5 | Afflicted (Venus, Saturn, Mercury, any planet named): debilitated, in an enemy's sign, or combust. | S24 p. 17, S25 p. 14 |
| R6 | Saturn "matures" at 36 (S25 gives 35 and 36); wording says "about 35–36". | S25 inconsistent |
| R7 | Rahu/Ketu aspects stay forward 5/9/12 (= teacher's 2nd/5th/9th anti-clockwise). S25's "5th and 9th, not the 7th" agrees. | no change |
| R8 | House tables (BHAVA_INFO, Sessions 21-22) are kept; S24/S25 additions are appended (no removals). Saturn is added as karaka of the 12th beside Ketu (S25). | user-approved default |
| R9 | `bhava_lord_in` combinations without her text keep a generated reading marked `blend`, now following S27's method (both houses + the sign). | 125 of 144 not taught |
| R10 | "Mild malefic" Sun takes the malefic lines, labelled "(mild)". | S26 gives no separate text |
| R11 | Her per-house Session 26 texts that she gives for one example planet ("a benefic in the 2nd…", told with Jupiter) apply to every planet of that nature; planet-specific sentences ("Here Saturn…") apply to that planet only. | S26 wording |

## 3. Scope

In: everything in §5-§8. Out: new astronomy; yogas not named in these decks (Lakshmi/Dhana yoga stays a note);
a numeric "strength score"; editing the teacher's wording (typos fixed only where meaning is unchanged, listed in the
plan); `scripts/build_data.py` (user-local).

## 4. Architecture

Unchanged shape: **master workbook `S23_` sheets → `build_session23.py` → `session23_rules.json` + the
`SESSION23-DATA` block of `index.html`**; three engines read the same data:
- page: `SESSION23-ENGINE` / `-RENDER` blocks in `index.html`;
- Python: `bhava_rules.py`;
- Excel: calculator sheets built by `make_session23_xlsx.py` (`S23_*_Calc`).

Sheets outside S23 that the page reads through `scripts/build_data.py` (Bhava Info, Planet Characteristics/Profile)
are changed with guarded edits in `patch_master_workbook.py`.

## 5. Data model (workbook sheets → JSON keys)

Existing sheets (rows change):
| Sheet → key | Change |
|---|---|
| `S23_GrahaInBhava` → `graha_in_bhava` | 96 curated rows → teacher text, `taught`, source `S23-2024 p.N` / `S24 p.N` / `S25 p.N`. Planet-specific conditional sentences move to `S23_Conditions` (§5.1). |
| `S23_BhavaLordIn` → `bhava_lord_in` | + 12 rows lord 1 in 1-12 (S26 pp. 16-27); + S27 rows 1→6, 3→3, 7→10, 10→7; + one Parivartana row 4↔11 (new column `Exchange` = yes). New column `Condition` (`strong`/`weak`/blank) for the S26 6th/8th lines. |
| `S23_GrahaRashi` → `graha_rashi` | + Moon in Vrishabha/Kanya/Makara (earth) and in Tula (S23-2024 pp. 5, 11). |
| `S23_Digbala` → `digbala` | Mars → `taught`, `S23-2024 p.29`. |
| `S23_ClassRules` → `class_rules` | Upachaya malefic text per R2; new Dusthana-occupant rule "Natural malefics in the 6th, 8th or 12th give good results" (S25 p.10). |

New sheets:
| Sheet → key | Columns | Rows |
|---|---|---|
| `S23_BhavaNature` → `bhava_nature` | House, Nature (benefic/malefic), Planet (blank = any of that nature), Text, Status, Source | S26 pp. 2-14: general line + per-house lines + planet-specific lines |
| `S23_AspectMeaning` → `aspect_meaning` | Planet, Aspect (teacher's count: Jupiter 5/7/9, Saturn 3/7/10, Mars 4/7/8, Rahu/Ketu 2/5/9), FromHouse (blank = any), Text, Status, Source | S27 pp. 2-4 general meanings; S24 Jupiter-from-each-house (36); S27 p.18 "aspect: to see, to influence" default |
| `S23_LifeAreas` → `life_areas` | No, Area, Houses, Karaka, KarakaFemale, Link (e.g. `PAC 5-7`, `Mercury+Ketu`), Source | S27 pp. 12-13, 16 rows |
| `S23_Conditions` → `conditions` | Key, Planet, House, Text, Status, Source | conditional sentences (§6.6); `Key` is one of a fixed list the engines implement |
| `S23_Remedies` → `remedies` | Topic (planet name or "Tip"), Text, Source | S23-2024 p.45 (Moon ×8), p.36 (Mercury), S25 p.42 (Saturn/rice), S24 p.38, S26 p.28, S27 p.25 tips |

`build_session23.py` validation extends to every new sheet (allowed planets, houses 1-12, natures, statuses,
condition keys, one row per required combination, Life-area numbers 1-16).

### 5.1 Outside S23 (guarded patch)
- Bhava Info: 3rd body + "hands"; 9th body + "buttocks"; 11th body + "calves, shins"; 7th relations + "maternal
  grandmother"; 12th karaka + Saturn.
- Planet Characteristics / Planet Profile: Moon nature "Natural benefic (S26); waxing = stronger"; Sun nature "Mild
  malefic (S26)"; karakatwa additions from S23-2024 p.2, 20, 22, 40, 44 (Moon: food, travel, change of place…;
  Mars: brothers and male friends, athlete; Mercury: astrology, marketing, hobbies).

## 6. Engine behaviour

### 6.1 Nature (replaces `nature()` / `s23NatureAt`)
`benefic` for Jupiter, Venus, Mercury, Moon; `malefic` for Saturn, Mars, Rahu, Ketu; `mild malefic` for the Sun.
Class rules keyed on "malefic" also apply to the Sun, with "(mild)" in the label. The Moon card shows
"Shukla (waxing) — stronger" / "Krishna (waning) — weaker" as strength. `beneficMalefic()` (Session 12 table)
shows the Sun as "Mild malefic".

### 6.2 Layer 1 · Graha + Bhāva card (additions)
1. Her text (all 108 taught).
2. **Benefic/malefic line** from `bhava_nature`: the general line for the planet's nature, the house line, and any
   planet-specific line (R11).
3. **12th-house rule:** a planet in the 12th, of any dignity, adds "Even exalted, a planet in the 12th stays in the
   bucket of losses; gaining from it needs double effort in its matters" (S23-2024 p.19, S24 p.13, S25 p.29). Shown
   right after the dignity line, so "full force" never stands alone.
4. **Dusthana malefic rule** (S25 p.10) and the **Upachaya** wording (R2) through `class_rules`.
5. **Conditions** that hold for the chart (§6.6).

### 6.3 Layer 2 · Bhāva + Bhāva
For each house X: lord L sits in house Y, in sign S.
1. Her text when `bhava_lord_in` has (X, Y); for lord 1 in 6 or 8, the strong/weak line by R3.
2. Otherwise a `blend`: X's significations + Y's significations + a sign line.
3. **Sign line** (S27 pp. 9-10): S's element, mode and direction. A dual sign adds "the matter is continuous or
   repeated"; an earth (Prithvi) sign adds "it concerns property".
4. **Placement class** (S27 p.6): Y in Kendra / Trikona / Dusthana / Bādhaka house. Y in 6, 8 or 12 reads "a
   difficult placement" (replaces the wording written for lords *of* those houses).
5. **Dictum** (S27 p.11): if L aspects X, "the lord aspects its own house, so the Xth house is strong".
6. **Parivartana:** if the lords of X and Y occupy each other's signs, one combined entry (her 4↔11 text where
   it applies, else a blend of both houses).
7. With and aspecting the lord: planets conjoined with or aspecting L, each naming the houses it rules (S27 p.16).

### 6.4 Aspects
Every aspect line names the aspect her way (`aspectOrd`) and adds the meaning from `aspect_meaning`: Jupiter 5th
punya / 9th luck, Saturn 3rd effort / 10th karmic responsibility, Mars 4th protection / 8th transformation, plus
her Jupiter-from-house reading where one exists; other aspects use "to see, to influence; it brings the aspecting
planet's karakatwas".

### 6.5 Layer 3 · Graha + Rāśi
Adds the Moon rows of §5. The Moon-in-a-dual-sign-in-the-10th line is a condition (§6.6).

### 6.6 Conditions (fixed keys; wording in `S23_Conditions`)
Evaluated from the chart, the birth date (age), the running daśā and the form's gender:

| Key | Holds when | Source |
|---|---|---|
| `saturn_matures` | Saturn in 1, 2, 3, 5, 7 or 10 and age < 36 (text about delays until ~35-36) | S25 pp. 3-14 |
| `saturn_retro_1` | Saturn retrograde in the 1st (marriage not delayed) | S25 p.3 |
| `saturn_afflicted_10_young` | Saturn afflicted (R5) in the 10th and age < 36 | S25 p.14 |
| `saturn_mars_12` | Saturn and Mars both in the 12th | S25 p.16 |
| `saturn_afflicted_6` / `_12` | Saturn afflicted in the 6th / 12th | S25 pp. 10, 16 |
| `jupiter_md_8` / `_11` | Jupiter in 8th / 11th (marked "active now" in Jupiter Mahādaśā) | S24 pp. 9, 12 |
| `venus_dasha_9` | Venus in the 9th ("active now" in Venus daśā) | S24 p.30 |
| `rahu_md_9` | Rahu in the 9th ("active now" in Rahu Mahādaśā) | S25 p.26 |
| `twelfth_hidden_talent` | any planet in the 12th ("active now" in its daśā or bhukti) | S23-2024 p.44 |
| `upachaya_30s` | any planet in 3, 6, 10 or 11 (its results show mostly in the 30s) | S23-2024 pp. 22, 25; S24 pp. 4, 7 |
| `ketu_12_purpose` | Ketu in the 12th and age < 35 | S25 p.41 |
| `venus_afflicted` / `venus_good` | Venus in 2, 8, 11 afflicted / not afflicted | S24 pp. 17, 29, 35 |
| `venus_mercury_5` | Venus with Mercury in the 5th | S24 p.22 |
| `seventh_lord_12` | lord of the 7th in the 12th (foreign spouse) | S24 p.37 |
| `mercury_foreign_language` | Mercury in the 2nd with Rahu or the 12th lord | S23-2024 p.33 |
| `moon_dual_10` | Moon in a dual sign in the 10th (multiple professions) | S23-2024 p.17 |
| `venus_meets_wife` | male chart: Venus's house text (where he meets his wife) | S24 |
| `jupiter_husband` | female chart: Jupiter also signifies the husband | S24 |
| `first_child_male` | 5th sign male, a male planet in the 5th, and the 5th lord in a male sign | S27 p.24 |

### 6.7 Life areas (`life_area(area)`)
For a Ready Reckoner area with houses H (and, for Foreign travel, 9 and 12), in order:
1. **House:** number, sign, element/mode/direction.
2. **Occupants:** each planet's nature (§6.1), its Layer-1 text, and the S26 line.
3. **Aspecting the house:** each aspecting planet with aspect name and meaning (§6.4).
4. **House lord:** house and sign it sits in, placement class, dignity, Layer-2 entry, the dictum if it applies.
5. **With / aspecting the lord:** planets conjoined with or aspecting the lord, with the houses they rule.
6. **Karaka:** from `life_areas` (R4 by gender for Marriage), its house, sign, dignity, combustion, retrograde.
7. **Summary:** two short lists — "supports" (benefics in or aspecting the house or lord, strong lord, strong
   karaka, the dictum) and "pressure" (malefics there, lord or karaka weak/afflicted, lord in 6/8/12).
   No score.

Special: **Love marriage** reports a PAC link between the 5th and 7th — a lord in the other's house, an exchange,
the two lords conjoined, or either lord aspecting the other house or lord — and a Mercury–Ketu conjunction or
mutual aspect. **Foreign travel** covers the 9th and the 12th and their lords, karaka Rahu.

## 7. UI

- **Graha + Bhāva cards:** new benefic/malefic line, 12th-house line, condition lines (with "active now" chips
  when the daśā is running), and source chips (deck + page).
- **Layer 2 table:** sign line, placement class, dictum chip, Parivartana entries, "with/aspecting the lord" line.
- **Life areas:** a top-level report tab between Daśā–Bhukti and Predictive. Sixteen area buttons; the chosen
  area shows the 7 steps as a numbered list with tags (taught / blend), then the two summary lists. The print/PDF
  shows all 16 areas. Phone width: one column, no horizontal page scroll.
- **Remedies:** her Moon, Mercury and Saturn remedies join the "Remedies to Strengthen a Graha" list; the three
  tips appear under "Tips of the day".

## 8. Workbook delivery

- `python make_session23_xlsx.py --install` (upgrade):
  1. backup to `backups\`;
  2. add missing sheets (new data sheets filled from `session23_rules.json`);
  3. for existing data sheets, replace a row only if it still equals the version shipped before this change
     (the previous rules are kept in the repo as `session23_rules.previous.json` for this comparison); rows the
     user changed are kept and listed;
  4. rebuild calculator sheets: `S23_Chart` gains a Gender cell; `S23_Predict_Calc` gains the new lines;
     new `S23_LifeArea_Calc` with an area drop-down and the 7 steps as formulas.
- `python patch_master_workbook.py`: the §5.1 edits, guarded as before.
- `publish.bat`: unchanged; its `--check` covers the new sheets.
- The repo's `index.html` and `session23_rules.json` are regenerated from a patched and upgraded copy of the
  master, so the next publish reports no changes.

## 9. Testing

### 9.1 Teacher's charts as fixed cases
- **S23-2024 A-D** (Makara, Vṛṣabha, Mesha, Dhanu Lagna): readings carry her points; with the Moon benefic no
  malefic-Moon lines appear; D shows `moon_dual_10`.
- **S27 Chart 1 = S23-2024 C** (Mesha Lagna): the p.8 lord list exactly; 1L Mars in 6th in Kanya with the dual
  and earth lines and the dictum ("Lagna strong"); Life area Mother: 4th in Karkataka, no occupants, aspected by
  Jupiter, Venus and Rahu, 4th lord Moon aspected by Saturn; Marriage: Tula movable/airy/west, Moon in the 7th,
  Saturn aspecting the 7th, 7L Venus in the 10th with Jupiter (9th and 12th lord), Ketu aspecting Venus.
- **S27 Chart 2** (Tula Lagna): 3L Jupiter in the 3rd (taught text); 4L↔11L Parivartana (taught text);
  `first_child_male`; Ketu in the Lagna aspected by Saturn.
- **S27 book chart (Sri Chaitanya):** Saturn–Mars exchange found; the listed aspects found.
- **S26 Lagna-lord series:** Karkataka Lagna, Moon in each house gives the matching taught text; Moon in the 11th
  is exalted.

### 9.2 Cross-implementation
Page vs Python on random charts (existing harness extended to the new outputs, including `life_area` for all 16
areas); Excel (LibreOffice recalculation) vs Python for `S23_Predict_Calc` and `S23_LifeArea_Calc`.

### 9.3 Other
Validation tests for each new sheet; upgrade tests (edited rows kept, shipped rows replaced, backup made);
browser tests for the Life areas tab, print and phone width; a fresh independent review before `main`.

## 10. Phasing (pushed to the work branch after each phase)
1. Data: all new rows and sheets, validation, JSON; nature change.
2. Layer 1 additions (§6.2), conditions (§6.6), remedies.
3. Layer 2, aspects, graha-rashi (§6.3-6.5).
4. Life areas (§6.7, §7) in page and Python.
5. Excel: calculator changes, `S23_LifeArea_Calc`, upgrade path; patch-script additions; regeneration.
6. Full suite, independent review, fixes; `main` after the user agrees.

## 11. Risks
- **Volume of text:** 96 texts + ~70 short lines copied from slides; mitigated by copying from transcriptions,
  spot-checking against PDF images, and a test that every taught row cites a page.
- **Excel formula size:** the Life-area sheet needs many lookups; kept to fixed-size blocks per step, tested
  against Python in LibreOffice.
- **Upgrade comparison:** a row the user re-typed identically counts as unchanged (harmless).
- **Teacher's wording that conflicts with dignity** (e.g. S26 calls Moon in the 5th for Karkataka "very
  auspicious" though debilitated): texts are shown as taught; dignity is shown alongside, unchanged.
