# Session 23 — Bhava classifications, prediction layers and Daśā linking: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Session 23 content as three matching implementations — `index.html`, Python and Excel — fed by one rules workbook.

**Architecture:** `Session23_Rules.xlsx` (data sheets) → `build_session23.py` → `session23_rules.json` (+ a generated data block in `index.html`). `bhava_rules.py` is the Python engine; a hand-written JS engine sits beside the generated block; Excel calculator sheets re-implement the same logic as formulas. Parity tests compare all three; the slides' Simha-Lagna chart is the oracle.

**Tech Stack:** Python 3.13 + openpyxl + `unittest` (no pytest installed), vanilla JS in `index.html`, node 22 + Playwright (global) for browser tests, LibreOffice for Excel recalculation. Same conventions as `ashtakavarga.py` / `test_cross_impl.py`.

**Spec:** `docs/superpowers/specs/2026-10-08-session23-bhava-classes-predictions-design.md`

## Global Constraints

- Class houses exactly: Kendra 1,4,7,10 · Trikona 1,5,9 · Panapara 2,5,8,11 · Apoklima 3,6,9,12 · Upachaya 3,6,10,11 · **Apachaya 1,2,4,7,8** · Maraka 2,7 · Dusthana 6,8,12 · Trishadaya 3,6,11 · Badhaka: Chara Lagna → 11th, Sthira → 9th, Dwiswabhava → 7th (house, then its sign and lord).
- Slide wording kept as printed, including the Apoklima line "Planets placed in these signs are considered weak. Except 9th house, it is considered as bad position to the planets."
- Natural nature: benefic = Jupiter, Venus, Mercury **unless conjunct Mars, Saturn, Rahu or Ketu**, Moon when Shukla paksha (`computeTithi(...).tithiNum <= 15`); malefic = Sun, Mars, Saturn, Rahu, Ketu, Moon when Krishna paksha.
- Digbala (house of directional strength): Sun 10, Saturn 7 (taught); Mercury 1, Jupiter 1, Moon 4, Venus 4, Mars 10 (standard — tagged `standard`). A graha in the opposite house "loses directional strength" (taught for the Sun in the 4th).
- Every text row has `status` ∈ `taught` | `curated` | `blend` and is shown with that tag. Curated lines may only blend fields already in the page's `PLANET_PROFILE`, `KARAKATWAS`, `BHAVA_INFO`; no outside rule enters silently.
- Role order everywhere: `Maraka lord`, `Maraka occupant`, `Badhakadhipati`, `Badhaka occupant`, `Dusthana lord`, `Trishadaya lord`. Rahu/Ketu hold occupant roles only.
- New JS identifiers are prefixed `s23` (the page already declares `renderClassificationSection` twice — do not add collisions). Generated block markers: `SESSION23-DATA-START/END`; hand-written: `SESSION23-ENGINE-START/END`. Both sit outside the `*-START/END` blocks owned by `scripts/build_data.py`.
- Files use LF line endings; tests must block all non-`file:` network traffic (the page POSTs charts to a Google Sheet).
- Work on branch `claude/quirky-hawking-h3aaoy`; commit trailers: `Co-Authored-By: Claude <noreply@anthropic.com>` and `Claude-Session: …` (no model name). No PR unless asked.

## Review Focus

1. **A planet that owns two houses** (Simha Lagna: Saturn owns 6th and 7th) must show every role once, in the fixed order — `test_roles_for_a_planet_with_two_houses`.
2. **Missing Lagna or birth time** → the new sections show a message, never wrong tables — `test_sections_explain_missing_lagna`.
3. **Crowded charts** (all planets in one house; empty Maraka houses; Rahu/Ketu in the 2nd/7th with no lords of their own) → tables still render, `NIL` shown — `test_all_planets_in_one_house`.
4. **"Now" at a dasha boundary or outside the 120-year span** → running pair never undefined — `test_running_pair_at_boundaries`.
5. **Moon on the Purnima/Amavasya boundary and Mercury beside a malefic** → nature is deterministic — `test_nature_edge_cases`.

---

### Task 1: Rules workbook skeleton, JSON build and reference extraction

**Files:**
- Create: `build_session23.py`, `Session23_Rules.xlsx` (generated), `session23_rules.json` (generated), `test_session23_data.py`

**Interfaces:**
- Produces: `build_session23.build(xlsx_path, json_path, index_path) -> dict` (writes both, returns the rules dict); `load_rules(path="session23_rules.json") -> dict` in `bhava_rules.py` (Task 2). JSON top-level keys: `classes`, `class_rules`, `badhaka`, `dignity_effect`, `digbala`, `dasha_role_text`, `graha_in_bhava`, `graha_pair`, `reference`, `meta`. `reference` is extracted from `index.html` through node (`BHAVA_INFO`, `RASHI` names/lord/mode/tatwa/direction/varna, `RASHI_DIGNITY`, `DIGNITY_DEG`, `PLANET_OWN_HOUSES`, `NATURAL_FRIENDS`, `KARAKATWAS`, `PLANET_PROFILE` subset, `SPECIAL_ASPECTS`, `VORDER`, `VYEARS`, `COMBUST_ORB`).

- [ ] **Step 1: Write failing tests** in `test_session23_data.py`: `test_classes_have_the_confirmed_houses` (the Global Constraints houses), `test_badhaka_modes` (`{"Chara":11,"Sthira":9,"Dwiswabhava":7}`), `test_reference_matches_the_page` (every `reference` table equals the value node evaluates from `index.html`), `test_every_text_row_has_status_and_source`, `test_json_matches_workbook` (re-reading the xlsx reproduces the JSON).
- [ ] **Step 2: Run** `python3 -m unittest test_session23_data` → FAIL (module missing).
- [ ] **Step 3: Implement `build_session23.py`** — data lives in the Python source as literals for the rule sheets (classes, class_rules, badhaka, dignity_effect, digbala, dasha_role_text) with wording from the slides; `graha_in_bhava` / `graha_pair` start with the Sun's 12 `taught` rows (slides 28–41 text verbatim, plus the recording's extra points as a second field) and the Jupiter+Mercury `taught` pair; other rows added by Task 6. Reference extraction runs `node -e` with `vm`, as the existing cross-impl tests do.
- [ ] **Step 4: Run tests** → PASS. **Step 5: Commit** (`git add build_session23.py Session23_Rules.xlsx session23_rules.json test_session23_data.py`).

### Task 2: Python classification engine (oracle = slides' chart)

**Files:**
- Create: `bhava_rules.py`, `test_bhava_rules.py`

**Interfaces:**
- Consumes: `load_rules()`.
- Produces (all 0-based signs, Mesha = 0; planets named `Sun…Ketu`):
  - `house_sign(lagna:int, house:int)->int`, `house_lord(rules, lagna, house)->str`, `occupants(lagna, signs:dict[str,int])->dict[int,list[str]]` (planet order Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
  - `class_houses(rules, name, lagna)->list[int]` (Badhaka uses the Lagna's mode)
  - `classification_tables(rules, lagna, signs)->dict[str,list[dict]]` — rows `{house, sign, planets:list[str], lord, lord_house}`
  - `house_class_matrix(rules, lagna)->list[dict]` — `{house, sign, classes:list[str]}`
  - `badhaka(rules, lagna, signs)->dict` — `{mode, house, sign, lord, occupants}`

- [ ] **Step 1: Write failing tests** with the oracle `LAGNA=4`, `SIGNS={"Moon":6,"Ketu":7,"Saturn":9,"Jupiter":10,"Mars":3,"Sun":2,"Venus":2,"Mercury":1,"Rahu":1}`: `test_kendra_table_matches_slide` (rows `(1,[],"Sun")`, `(4,["Ketu"],"Mars")`, `(7,["Jupiter"],"Saturn")`, `(10,["Mercury","Rahu"],"Venus")`); the same style for `test_trikona_…`, `panapara` (11th = `["Sun","Venus"]`, lord Mercury), `apoklima` (3rd Moon/Venus, 6th Saturn/Saturn, 9th empty/Mars, 12th Mars/Moon), `upachaya`, `maraka` (2nd empty/Mercury, 7th Jupiter/Saturn), `dusthana`, `trishadaya` (lords Venus, Saturn, Mercury); `test_apachaya_is_1_2_4_7_8`; `test_badhaka_oracle` (`Sthira`, 9, Mesha, `Mars`, `[]`); `test_badhaka_for_every_lagna_and_the_six_spoken_examples` (Mesha→Kumbha/Saturn, Tula→Simha/Sun, Dhanu→Mithuna/Mercury, Kumbha→Tula/Venus, Karka→Vrishabha/Venus, Simha→Mesha/Mars); `test_matrix_belongs_to_column` (house 1 → Kendra, Trikona, Apachaya; house 6 → Apoklima, Upachaya, Dusthana, Trishadaya; house 9 → Trikona, Apoklima, Badhaka); `test_all_planets_in_one_house`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement** the signatures above (pure functions, no I/O besides `load_rules`). **Step 4: Run** → PASS. **Step 5: Commit.**

### Task 3: Nature, class readings, roles, dignity port, digbala

**Files:**
- Modify: `bhava_rules.py`; Test: `test_bhava_rules.py`

**Interfaces:**
- Produces:
  - `nature(planet, signs, moon_waxing:bool)->"benefic"|"malefic"` (Global Constraints rule)
  - `class_readings(rules, lagna, signs, moon_waxing)->list[dict]` — `{planet, house, classes, texts:list[str]}` using `class_rules`
  - `planet_roles(rules, lagna, signs)->dict[str,list[str]]`
  - `dignity(rules, planet, sign, deg=None)->dict` — port of the page's `planetDignity()`; returns `{label, flag, bala, note}`
  - `digbala(rules, planet, house)->"strong"|"lost"|None`

- [ ] **Step 1: Write failing tests**: `test_nature_edge_cases` (Mercury with Saturn → malefic; Mercury with Sun → benefic; Moon `tithiNum` 15 → benefic, 16 → malefic; Sun malefic); `test_roles_oracle` (Sun `[]`, Moon `["Dusthana lord"]`, Mars `["Badhakadhipati"]`, Mercury `["Maraka lord","Trishadaya lord"]`, Jupiter `["Maraka occupant","Dusthana lord"]`, Venus `["Trishadaya lord"]`, Saturn `["Maraka lord","Dusthana lord","Trishadaya lord"]`, Rahu `[]`, Ketu `[]`); `test_roles_for_a_planet_with_two_houses`; `test_rahu_ketu_occupant_roles_only` (Rahu in the 2nd → `["Maraka occupant"]`); `test_dignity_equals_the_page_on_the_full_grid` (node evaluates `planetDignity` for 9 planets × 12 rāśis × degrees 0–29; labels/flags/bala equal); `test_digbala_taught_cases` (Sun 10th strong, Sun 4th lost, Saturn 7th strong); `test_class_readings_rules` (Jupiter in a Kendra → text contains "smaller efforts"; Saturn in an Upachaya → "good results"; Saturn in an Apachaya → "do not do well"; a graha in the 9th gets no "weak" text).
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement** — `dignity` is a line-for-line port of `planetDignity()` (page lines ~3163–3200) reading `reference`. **Step 4: Run** → PASS. **Step 5: Commit.**

### Task 4: Python Vimśottarī and Daśā linking

**Files:**
- Modify: `bhava_rules.py`; Test: `test_bhava_rules.py`

**Interfaces:**
- Produces:
  - `vimshottari(rules, moon_lon:float, birth:datetime, now:datetime)->dict` — `{timeline:[{lord,start,end,bhuktis:[{lord,start,end}]}], cur_maha, cur_bhukti}`; 365.25-day years, same as `buildDasha()`
  - `running_roles(rules, dasha, roles)->dict` — `{maha:{lord,roles,text}, bhukti:{…}}`
  - `watch_periods(rules, dasha, roles, now, years=10)->list[dict]` — `{start,end,maha,bhukti,roles:list[str],kind:"caution"|"favourable"}`

- [ ] **Step 1: Write failing tests**: `test_vimshottari_equals_the_page` (node `buildDasha` under `TZ=UTC` vs Python for 25 birth dates; every period boundary within one day); `test_running_pair_at_boundaries` (now = exact boundary, now before birth+120y, now after span → pair defined); `test_watch_periods_flag_maraka_and_badhaka` (oracle chart: any bhukti whose maha or bhukti lord is Mercury/Saturn/Jupiter/Mars carries the matching role names; Trishadaya Mahādaśā periods are `favourable`); `test_dasha_role_text_uses_the_slide_wording` (Maraka text contains "before the time of death is promised").
- [ ] **Step 2–5:** Run → FAIL; implement; run → PASS; commit.

### Task 5: Curated content (96 graha-in-bhava rows, 36 pair rows)

**Files:**
- Modify: `build_session23.py`; regenerate `Session23_Rules.xlsx`, `session23_rules.json`; Test: `test_session23_data.py`

**Interfaces:** Produces rows `{planet, house, points:list[str], status, source}` for `graha_in_bhava` (108) and `{a, b, conjunction:str, aspect:str, status, source}` for `graha_pair` (36 unordered pairs, alphabetical `a<b` in the order Sun…Ketu).

- [ ] **Step 1: Write failing tests**: `test_every_graha_bhava_cell_exists_once` (9×12), `test_sun_rows_are_taught_and_equal_the_slide_text`, `test_other_rows_are_curated_with_3_to_5_points`, `test_no_two_rows_share_text`, `test_curated_rows_cite_their_source_fields` (`source` names the profile/bhava fields blended), `test_pair_rows_cover_all_36_and_jupiter_mercury_is_taught`, `test_tone_has_no_certainty_words` (no "will die", "certainly", "definitely").
- [ ] **Step 2: Run** → FAIL. **Step 3: Author the rows** in `build_session23.py` data modules (`curated_graha_bhava.py`, `curated_pairs.py` so the file stays readable) by blending each planet's `PLANET_PROFILE` fields (relationships, personality, profession, body parts, health, nature) with the bhava's `BHAVA_INFO` fields (signification, relatives, body), favourable and cautionary sides, Sun-slide register. **Step 4: Run** → PASS. **Step 5: Commit.**

### Task 6: Python prediction layers

**Files:**
- Modify: `bhava_rules.py`; Test: `test_bhava_rules.py`

**Interfaces:**
- Produces:
  - `graha_bhava(rules, lagna, signs, planet, deg, moon_waxing)->dict` — `{planet, house, status, points, dignity_line, digbala_line, class_texts}`
  - `bhava_bhava(rules, lagna, signs)->list[dict]` — one per lord: `{lord_of, sits_in, text, status}` (`blend`; 2nd lord in 7th is `taught` verbatim)
  - `graha_rashi(rules, lagna, signs, degs)->list[dict]` — tatwa, direction, varna, mode, dignity strength line
  - `graha_graha(rules, lagna, signs)->dict` — `{conjunctions:[{a,b,house,text,combust}], aspects:[{by,to,house_aspect,text,jupiter_flag}]}`; aspects follow `SPECIAL_ASPECTS` (Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10, Rahu/Ketu 5/9/12, others 7); conjunction with the Sun inside `COMBUST_ORB` adds the combustion note
  - `five_step(rules, lagna, signs, house)->dict` — slide 25 checklist (bhava, lord position, occupants, aspecting planets, karaka placement)

- [ ] **Step 1: Write failing tests**: `test_taught_examples_are_verbatim` (2L-in-7 text, Jupiter+Mercury, Sun in Mesha uses "exalted … full"); `test_dignity_line_for_sun_in_meena_lagna` (Sun in the 2nd → exalted wording; in the 8th → debilitated wording, per slide 31); `test_aspect_pairs_for_the_oracle_chart` (exactly: Mars→Moon 4th, Mars→Saturn 7th, Mars→Jupiter 8th, Mercury→Ketu 7th, Jupiter→Sun 5th, Jupiter→Venus 5th, Jupiter→Moon 9th, Saturn→Mars 7th, Saturn→Moon 10th, Rahu→Saturn 9th, Ketu→Mars 9th, Ketu→Moon 12th); `test_five_step_for_the_seventh_house` (lord Saturn in 7th, occupant Jupiter, karaka Venus); `test_every_status_tag_present`.
- [ ] **Step 2–5:** Run → FAIL; implement; run → PASS; commit.

### Task 7: JS engine block + parity with Python

**Files:**
- Modify: `index.html` (insert `SESSION23-DATA` block via `build_session23.py`, and a hand-written `SESSION23-ENGINE` block, both immediately before `function renderPredictive(){`); Test: `test_session23_cross_impl.py`

**Interfaces:**
- Produces (JS, mirrors Python 1:1 but 1-based houses/rāśis as the page uses): `s23Occupants(lagnaN, planetsByRashi)`, `s23ClassHouses(name, lagnaN)`, `s23ClassificationTables(lagnaN, pbr)`, `s23HouseClassMatrix(lagnaN)`, `s23Badhaka(lagnaN, pbr)`, `s23Nature(p, pbr, moonWaxing)`, `s23ClassReadings(lagnaN, pbr, moonWaxing)`, `s23Roles(lagnaN, pbr)`, `s23RunningRoles(D, roles)`, `s23WatchPeriods(D, roles, now, years)`, `s23GrahaBhava(...)`, `s23BhavaBhava(...)`, `s23GrahaRashi(...)`, `s23GrahaGraha(...)`, `s23FiveStep(...)`. Existing helpers reused: `planetDignity`, `rashiOf`, `getRashi`, `buildDasha`, `SPECIAL_ASPECTS`, `computeTithi`, `COMBUST_ORB`.

- [ ] **Step 1: Write failing tests**: `test_block_markers_once`, `test_generated_data_equals_json`, `test_js_equals_python_on_2000_random_charts` (classification tables, matrix, badhaka, roles, graha_bhava, bhava_bhava, graha_graha — exact JSON equality after normalising 1-based↔0-based), `test_no_duplicate_function_declarations_added` (new `function s23…` names are unique and no existing function name is redeclared).
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement** the engine block and generation hook in `build_session23.py` (replace text between markers). **Step 4: Run** → PASS. **Step 5: Commit.**

### Task 8: Page sections — "10 Classifications" and "Prediction Layers"

**Files:**
- Modify: `index.html` (two `<details class="section">` after `#bhavaBody`'s section, titles beginning `Bhāva Analysis —` so `GROUPS` puts them in the Bhāvas group; `renderS23Classes(...)`, `renderS23Predictions(...)` called from `generate()` after `renderBhavaAnalysis`; CSS `.s23-*` incl. print block); Test: `test_session23_cross_impl.py::BrowserSession23`

**Interfaces:** Consumes the Task 7 functions. Produces DOM: `#s23-classes-body`, `#s23-predict-body`; tables carry `data-class="Kendra"` etc.; status tags `.s23-tag.taught|curated|blend`.

- [ ] **Step 1: Write failing browser tests** (headless Chromium, network blocked; generate a real chart, then compare the DOM with `bhava_rules` run on `currentChart.chart.sidereal` and the Lagna): `test_ten_class_tables_equal_python`, `test_matrix_has_12_rows_10_classes`, `test_badhaka_block`, `test_prediction_layers_show_status_tags_and_dignity_lines`, `test_sections_explain_missing_lagna`, `test_phone_tables_scroll_in_their_box`, `test_print_fits_a4_without_clipped_headers` (viewport 695 px, `emulateMedia print`; reuse the Ashtakavarga check), `test_no_js_errors_and_no_network`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement** the renderers (tables in `.rtable`, three-letter rāśi names in print, `page-break-inside: avoid` on each class table). **Step 4: Run** → PASS. **Step 5: Regression check:** old-vs-new report render with a frozen clock; after removing the new sections the HTML is identical apart from whitespace. **Step 6: Commit.**

### Task 9: Daśā–Bhukti top-level tab with role linking

**Files:**
- Modify: `index.html` (new `<details class="section">` titled `Daśā–Bhukti — Vimśottarī` + `GROUPS` entry `["Daśā–Bhukti",["Daśā–Bhukti"]]` placed before "Predictive & Remedies"; render the existing dasha tables into it with role chips; remove the `data-tab="dasha"` pill and `#pane-dasha`, keep `buildDasha`/`renderDashaPane` logic; update the tab-switcher list and print comment; Test: `test_session23_cross_impl.py::BrowserDasha`

**Interfaces:** Produces `renderS23Dasha(D, roles, now)` writing `#s23-dasha-body`; the roles table, the running-pair readout (`.s23-running`) and the watch-periods table (`.s23-watch`).

- [ ] **Step 1: Write failing tests**: `test_top_level_nav_has_dasha_button`, `test_pill_removed_and_dasha_printed_once`, `test_running_pair_matches_python`, `test_roles_table_equals_python`, `test_watch_periods_equal_python`, `test_role_chips_on_bhukti_rows`, `test_indicative_wording_present` ("indicative").
- [ ] **Step 2–5:** Run → FAIL; implement; run → PASS (existing Ashtakavarga and cross-impl tests still pass); commit.

### Task 10: Excel calculator sheets and parity

**Files:**
- Create: `make_session23_xlsx.py` (adds calculator sheets to `Session23_Rules.xlsx`: `Chart` inputs with sign dropdowns + Moon longitude, birth date/time, "now"; `Classes_Calc`, `Roles_Calc`, `Dasha_Calc` (81 rows), `Predict_Calc`), Test: `test_session23_cross_impl.py::ExcelSession23`

**Interfaces:** Consumes `session23_rules.json`. Layout contract constants exported from `make_session23_xlsx.py` (`INPUT_ROW0`, `CLASS_ROW0`, …) used by tests. Dignity at sign level via a lookup grid from `bhava_rules.dignity`; deep/Moolatrikona by degree formulas.

- [ ] **Step 1: Write failing tests** (LibreOffice recalculation of 24 charts): `test_class_tables_equal_python`, `test_badhaka_equals_python`, `test_roles_equal_python`, `test_graha_bhava_text_equals_python` (exact string), `test_dignity_labels_equal_python`, `test_dasha_dates_equal_python`, `test_shipped_workbook_has_formulas_and_cached_values`, `test_row_labels_intact`.
- [ ] **Step 2–5:** Run → FAIL; implement; run → PASS; commit.

### Task 11: Audit and push

**Files:** none new.

- [ ] **Step 1:** `python3 -m unittest` — every module green (record the count).
- [ ] **Step 2: Mutation checks** on scratch copies: off-by-one house arithmetic in JS and Python, Apachaya without house 1, dropped `Badhakadhipati` role, wrong digbala house — each must fail at least one test.
- [ ] **Step 3: Visual checks:** desktop, phone and A4-print screenshots of both new sections and the Daśā tab; read them.
- [ ] **Step 4:** `git diff --check`, LF endings, `index.html` removed lines limited to the intended few (pill, tab-switcher entry, comment).
- [ ] **Step 5:** Commit and `git push -u origin claude/quirky-hawking-h3aaoy`; confirm `git rev-parse HEAD` equals the remote head.
