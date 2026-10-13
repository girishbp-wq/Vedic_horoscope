# Prediction read bhāva by bhāva — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The Prediction section opens on a "By bhāva" view — twelve house panels, each with the four layers, classes, facts boxes, kāraka(s) and life areas — while "By layer" keeps today's view; Python, the page and a new Excel sheet `S23_Bhava_Calc` agree.

**Architecture:** Two new pure functions in `bhava_rules.py` (`planet_facts`, `bhava_reading`) are assembled only from the existing layer functions; the page gets JS twins kept equal by the parity tests, and a renderer that draws only from them. The Excel Life-areas house block is first extracted into shared builders (no formula changes), then reused by the new sheet. No data change.

**Tech Stack:** Python 3 (openpyxl, unittest), vanilla JS in `index.html`, Playwright/Node for page tests, LibreOffice headless for Excel recalculation.

**Spec:** `docs/superpowers/specs/2026-10-13-bhava-by-bhava-design.md`

## Global Constraints

- Branch `claude/quirky-hawking-h3aaoy`; push after each task. Never push `main` without the user's explicit yes; never open a PR.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_019v79NvxiFMCa67AXVpo3Hc`. No model identifiers anywhere else.
- No rule and none of her texts change; `session23_rules.json` and the workbook data sheets stay as they are.
- "By layer" is today's content, unchanged; its classes and ids (`.s23-gb`, `#s23-bb`, `#s23-gr`, `#s23-conj`, `#s23-asp`) stay; every new class or id starts with `s23-bv` or `s23-view`.
- New JS lives inside the SESSION23-ENGINE / SESSION23-RENDER blocks; no new external files; site colours and fonts.
- Excel 2007 functions only; every formula ≤ 8,192 characters (`ExcelFormulaLimits`). `S23_LifeArea_Calc` keeps its layout and formulas.
- Full suite (~13 min, run in the background): `python3 -m unittest test_ashtakavarga test_cross_impl test_session23_data test_teacher_slides test_bhava_rules test_teacher_charts test_session23_cross_impl test_page_fixes test_patch_master_workbook`

## Plan-level decisions (refining the spec; reported to the user with the plan)

- **P1 · Digbala wording.** For a planet that gains or loses digbala, the facts box uses the existing digbala line ("Jupiter gains directional strength (digbala) in the 1st house.") instead of new wording, so the By-layer sentence is not lost and Excel reuses `S23_Predict_Calc` column H. Otherwise: "neither — strongest in the {S}th, weakest in the {W}th"; for a node: "none — a node has no directional strength".
- **P2 · Class meaning** = the class's `Nature` up to and including its first ". ", or the whole text if it has none (same rule in Python, JS and Excel).
- **P3 · Excel view.** The sheet shows texts the way `S23_Predict_Calc` and `S23_LifeArea_Calc` already do (joined lines, the first four of her sentences, the dignity label without its note, no source references). The Excel test compares `bhava_from_sheet(ws)` with `bhava_sheet_view(bhava_reading(...))`, a projection defined once in `make_session23_xlsx.py` (Task 5).

## Review Focus

1. **Partial chart** (Moon or nodes unknown, no degrees): a house whose lord is missing shows "Its lord's sign is not known."; missing kārakas are left out; page = Python. Tests: `test_partial_chart` (Task 1), `test_partial_chart_bhava_equal_python` (Task 2).
2. **Parivartana:** both houses of an exchange show the lord, "Parivartana with the {K}th" and the same text; each house keeps its own dictum. Test: `test_parivartana_on_both_houses` (Task 1).
3. **Lord in its own house** (Simha chart, Mars in the 9th): placement "The lord sits in its own bhava…", the company excludes the lord. Test: `test_occupants_lord_and_karaka` (Task 1).
4. **A new chart while By layer is chosen:** the view stays By layer, the click handlers do not stack (one click toggles once). Test: `test_view_persists_and_toggles_once` (Task 3).
5. **Crowded chart** (all nine planets in one house): the 1st-house panel lists 36 conjunctions and the page still has no sideways scroll at 375 px. Test: `test_crowded_house` (Task 3).

## Test charts

- **SIMHA** (the chart of the draft): `lagna 4`; signs `Sun 0, Moon 11, Mars 0, Mercury 0, Jupiter 4, Venus 11, Saturn 11, Rahu 11, Ketu 5`; degrees `Sun 11.80, Moon 16.91, Mars 27.21, Mercury 12.31, Jupiter 2.45, Venus 26.86, Saturn 24.61, Rahu 24.47, Ketu 24.47`; waxing True. Page sidereal longitudes: `Sun 11.80, Moon 346.91, Mars 27.21, Mercury 12.31, Jupiter 122.45, Venus 356.86, Saturn 354.61, Rahu 354.47, Ketu 174.47`, `lagnaN 5`, retro Rahu and Ketu.
- **Chart 3** (S28): `test_teacher_charts.CHARTS["S28_CHART_3"]` — 4↔7 and 8↔12 Parivartanas; Jupiter loses digbala in the 7th.

---

### Task 1: Python `planet_facts` and `bhava_reading`

**Files:** Modify `bhava_rules.py` (after `life_areas`); Test `test_bhava_rules.py` (new class `BhavaReading`, constants `SIMHA_SIGNS`, `SIMHA_DEGS`)

**Interfaces:**
- Produces:
  - `first_sentence(text: str) -> str` (P2).
  - `planet_facts(rules, ctx, planet) -> dict | None` — None when `planet` is not in `ctx["signs"]`; else `{planet, sign, rashi, deg (None when unknown), house, retro (bool), nature, classes (house_class_matrix classes of its house), roles (planet_roles list), dignity (the dignity() dict), dignity_effect (DignityEffect text for the label, or ""), dignity_status, digbala ("strong" | "lost" | ""; None for a planet with no Digbala row), digbala_text (P1), digbala_status (the Digbala row's status when strong/lost, else None), strength (strength_detail), class_texts (graha_bhava class_texts)}`.
  - `bhava_reading(rules, ctx, house, layer2=None) -> dict` — `layer2` defaults to `bhava_bhava(rules, ctx)`. Keys:
    `house, sign, rashi, name (_short_name), full_name, significations (_clean(sig)), people, body, classes, sign_line, supports, pressure, occupants, aspecting, lord, conjunctions, planet_aspects, lord_company, karakas, life_areas`.
    - `classes`: `[{name, other_names, meaning (first_sentence(nature)), note}]` in CLASS_ORDER; `note` is "" except for Badhaka: `f"For a {MODE_WORD[mode]} ({mode}) Lagna the {ordinal(h)} is the Badhaka sthāna; its lord {lord} is the Badhakādhipati."` (from `badhaka()`).
    - `occupants`: per planet in the house (PLANET_ORDER), `{planet, nature, facts, text ("\n\n".join(points)), status, source, extra, moon_strength, nature_lines, twelfth_line, degree_stage, conditions (chart_conditions entries whose planet is this one), readings, graha_rashi ({text, status, tatwa, direction, varna, mode} from graha_rashi), dignity_line, dignity_status}` — the rest straight from `graha_bhava(..., ctx=ctx)`.
    - `aspecting`: `_aspect_items(rules, ctx, house)`.
    - `lord`: None when the lord is not placed; else `{planet, facts, house, sign, rashi, exchange (the other house when the layer2 entry is a Parivartana, else None), placement_line (placement(...)[1]), text, status, source (from the layer2 entry with lord_of == h or exchange == h), dictum (_dictum(rules, ctx, h))}`.
    - `conjunctions` / `planet_aspects`: `graha_graha(rules, lagna, signs, ctx["degs"])` conjunctions / aspects whose `house` is h.
    - `lord_company`: `with_lord(rules, ctx, lord)` when placed, else `[]`.
    - `karakas`: `_karakas(rules, ctx, {"karakas": BHAVA_INFO[h]["karaka"], "karaka_female": ""})`, each plus `facts`.
    - `supports, pressure = _summary([_bhava_step(rules, ctx, h, layer2)], karakas_without_facts, None, None)`.
    - `life_areas`: `[{no, area}]` for the rows of `rules["life_areas"]` whose houses include h.

- [ ] **Step 1: Write the failing tests** (`BhavaReading`; `ctx = br.context(4, SIMHA_SIGNS, SIMHA_DEGS, True)`):
  - `test_classes_and_badhaka_note` — `[c["name"] for c in r9["classes"]] == ["Trikona", "Apoklima", "Badhaka"]`; Badhaka note `== "For a fixed (Sthira) Lagna the 9th is the Badhaka sthāna; its lord Mars is the Badhakādhipati."`; Trikona meaning `== "The most auspicious houses (and their lords) in the chart."`; Trikona note `== ""`; `br.first_sentence("No full stop") == "No full stop"`.
  - `test_occupants_lord_and_karaka` — house 9: occupants `["Sun", "Mars", "Mercury"]`; lord Mars, house 9, exchange None, placement_line starts "The lord sits in its own bhava"; "Mars" not in `[w["planet"] for w in lord_company]`; kārakas `["Sun", "Jupiter"]`; `life_areas == [{"no": 12, "area": "Father"}, {"no": 15, "area": "Foreign travel"}]`; conjunction pairs `[("Sun","Mars"), ("Sun","Mercury"), ("Mars","Mercury")]` with a non-empty combust note only on Sun–Mercury; planet_aspects `[("Jupiter","Sun"), ("Jupiter","Mars"), ("Jupiter","Mercury")]`; supports `== ['Mercury (benefic) in the 9th', 'Jupiter (benefic) aspects the 9th', 'The 9th lord Mars is strong', 'Mercury (benefic) is with the 9th lord', 'Jupiter (benefic) aspects the 9th lord', 'Karaka Sun is strong']`, pressure `== ['Sun (mild malefic) in the 9th', 'Mars (malefic) in the 9th', 'Sun (mild malefic) is with the 9th lord', 'Karaka Jupiter is aspected by Ketu']`.
  - `test_parivartana_on_both_houses` — Chart 3: `r8["lord"]["exchange"] == 12`, `r12["lord"]["exchange"] == 8`, both lord texts equal the `bhava_bhava` entry with `lord_of == 8`; `r4["lord"]["exchange"] == 7`; each `dictum == br._dictum(RULES, ctx, h)`.
  - `test_planet_facts` — SIMHA: Jupiter `digbala == "strong"`, `digbala_text == "Jupiter gains directional strength (digbala) in the 1st house."`, `digbala_status == RULES["digbala"]["Jupiter"]["status"]`; Sun `digbala == ""`, `digbala_text == "neither — strongest in the 10th, weakest in the 4th"`; Rahu `digbala is None`, `digbala_text == "none — a node has no directional strength"`; Mars roles `["Badhakadhipati", "Badhaka occupant"]`; Sun strength `{"word": "strong", "reasons": ["Exalted"]}`, `dignity_effect == RULES["dignity_effect"]["Exalted"]["text"]`; Chart 3 Jupiter `digbala == "lost"` and `digbala_text` equals its graha_bhava digbala_line; `planet_facts` of a missing planet is None.
  - `test_partial_chart` — SIMHA without Moon, Rahu, Ketu and with `degs={}`: `bhava_reading(..., 12)["lord"] is None` (12th lord Moon); house 4 kārakas `["Venus"]`; all twelve houses build.
  - `test_nothing_lost` — 200 random full charts (a local generator, seed 1313, the same shape as `test_session23_cross_impl.random_charts`, with age, maha and bhukti set so conditions fire): with `text(h)` = every string inside `bhava_reading(h)` joined by "\n", each of these is a substring of the house named: per planet p (house of p) — each `graha_bhava` point and extra, nature-line text, dignity_line, digbala_line, twelfth_line, degree-stage lines, class text, reading, condition text (`chart_conditions` with planet p), its `graha_rashi` text; per `bhava_bhava` entry — text (house lord_of, and the exchange house), placement_line and each `with_lord` reading and meaning (house lord_of); per conjunction (its house) — text and combust_note; per planet aspect (its house) — text. Empty strings are skipped.
- [ ] **Step 2:** `python3 -m unittest test_bhava_rules.BhavaReading -v` → FAIL (`bhava_reading` not defined).
- [ ] **Step 3: Implement** `first_sentence`, `planet_facts`, `bhava_reading` in `bhava_rules.py`, only from existing functions.
- [ ] **Step 4:** `python3 -m unittest test_bhava_rules test_teacher_charts` → OK.
- [ ] **Step 5: Commit** "Python: planet_facts and bhava_reading" and push.

### Task 2: Page engine twins

**Files:** Modify `index.html` (SESSION23-ENGINE, after `s23GrahaGraha`); Test `test_session23_cross_impl.py` (`JsEngine`)

**Interfaces:**
- Consumes: Task 1's shapes, exactly.
- Produces: `s23FirstSentence(t)`, `s23PlanetFacts(ctx, planet)` (null when not placed; `deg` is `null` when unknown — use `?? null`), `s23BhavaReading(ctx, house, layer2)` (`layer2` defaults to `s23BhavaBhava(ctx)`).

- [ ] **Step 1: Failing tests** in `JsEngine`:
  - `test_bhava_reading_equals_python_on_random_charts` — `random_charts(2000, 1968)`; JS returns `fp({facts: placed→s23PlanetFacts, bhava: [1..12].map(h => s23BhavaReading(ctx, h, layer2))})` per chart (layer2 computed once); Python the same with `br.planet_facts` / `br.bhava_reading`; on a mismatch report `first_difference` for the first chart.
  - `test_partial_chart_bhava_equal_python` — `random_charts(300, 2812)` with `("Rahu","Ketu")`, `("Moon",)`, `("Sun","Moon","Rahu","Ketu")` removed in turn and `degs = {}` on odd charts; same comparison.
  - `test_simha_and_chart_3_equal_python` — the two test charts in full (`first_difference(...) is None`).
- [ ] **Step 2:** `timeout 900 python3 -m unittest test_session23_cross_impl.JsEngine -v` → the three new tests FAIL (`s23BhavaReading is not defined`).
- [ ] **Step 3: Implement** the twins (mirror Task 1 line by line).
- [ ] **Step 4:** `timeout 900 python3 -m unittest test_session23_cross_impl.JsEngine test_session23_cross_impl.PageBlocks` → OK.
- [ ] **Step 5: Commit** "Page engine: s23PlanetFacts and s23BhavaReading" and push.

### Task 3: The two views on the page

**Files:** Modify `index.html` (CSS block of the `.s23-` rules; SESSION23-RENDER: `s23BuildPredictions`, new `s23BuildLayerView`, `s23BuildBhavaView`, `s23WirePredictions`; `renderS23Sections`; the `beforeprint` / `afterprint` handlers; build stamp untouched); Test `test_page_fixes.py` (new class `BhavaView`), `test_session23_cross_impl.py` (`BROWSER_SCRIPT`, `test_crowded_chart_still_renders`)

**Interfaces:**
- Consumes: `s23BhavaReading`, `s23PlanetFacts` (Task 2).
- Produces (DOM contract the tests read):
  - `let s23ViewShown = "bhava"`; buttons `.s23-view-btn[data-view="bhava"|"layer"]` in `.s23-view-btns`; panes `#s23-view-bhava`, `#s23-view-layer` (`.s23-view-pane`; the hidden one has `style="display:none"`).
  - `#s23-view-layer` holds today's layer HTML, moved verbatim into `s23BuildLayerView(...)`.
  - `#s23-view-bhava`: `table.s23-bv-planets tr[data-planet]` (columns Planet, Rāśi, Degree, House, Dignity, Digbala, Strength); `nav.s23-bv-jump a[href="#s23-bv-h{h}"]`; twelve `section.s23-bv-house#s23-bv-h{h}[data-house]`, each with `.s23-bv-classes li[data-class]`, `.s23-bv-supports li`, `.s23-bv-pressure li`, `.s23-bv-layer[data-layer="1".."4"]` whose headings read "Layer 1 · Graha + Bhāva", "Layer 2 · Bhāva + Bhāva", "Layer 3 · Graha + Rāśi", "Layer 4 · Graha + Graha", then `.s23-bv-karaka`, then `a.s23-bv-area[data-area]` links, then a link back to the jump bar.
  - Planet blocks `.s23-bv-planet[data-planet][data-role="occupant"|"aspect"|"lord"|"karaka"|"company"]`; facts box `dl.s23-bv-facts` with `dt` House, Roles, Dignity, Digbala, Strength, and Class rules (full form, when there are any). Role names show with diacritics (Badhakādhipati).
  - "Read the rest": `details.s23-bv-rest`.
  - `s23WirePredictions(el)` assigns `el.onclick` (never `addEventListener`): view buttons toggle panes and set `s23ViewShown`; `a.s23-bv-area` clicks the Life-areas button `.s23-area-btn[data-area=no]`, opens its `details.section` and scrolls `#s23-area-{no}` into view. It also sets the CSS variable `--s23-bv-top` to `#reportNav`'s height + 8 px for the sticky jump bar.

- [ ] **Step 1: Failing tests.** `BhavaView` in `test_page_fixes.py` (one `run_page` in `setUpClass` like `Round1Page`: generate any chart, then `renderS23Sections(SIMHA_SID, 5, {retro: {Rahu: true, Ketu: true}})`):
  - `test_by_bhava_is_the_default` — bhava pane shown, layer pane `display:none`, bhava button `.active`.
  - `test_twelve_panels_with_four_layers` — 12 panels; each has the four layer headings in order and a `.s23-bv-karaka`.
  - `test_ninth_house_panel` — classes `["Trikona","Apoklima","Badhaka"]`, Badhaka text contains "its lord Mars is the Badhakādhipati"; occupants `["Sun","Mars","Mercury"]`; each occupant `dt` list starts `["House","Roles","Dignity","Digbala","Strength"]`; lord block Mars has no "Class rules" `dt`; area links `[12, 15]`.
  - `test_first_house_digbala` — Jupiter's Digbala `dd` contains "gains directional strength (digbala) in the 1st house".
  - `test_view_persists_and_toggles_once` — click By layer: layer pane shown, 9 `.s23-gb`; re-render the same chart: still By layer; one click on By bhāva shows it (handlers not stacked).
  - `test_area_link_opens_life_area` — click `#s23-bv-h9 a.s23-bv-area[data-area="12"]`: `#s23-area-12` displayed, `s23AreaShown === 12`, its section `open`.
  - `test_jump_bar_stays_in_view` — click the jump link to house 7, then the jump bar's top ≥ `#reportNav` bottom − 1 and < 300.
  - `test_phone_width` — viewport 375: `scrollWidth <= innerWidth + 1`.
  - `test_print` — `emulateMedia print`: `.s23-view-btns` and `.s23-bv-jump` `display:none`; after dispatching `beforeprint` every `details.s23-bv-rest` is open; after `afterprint` they are closed again.
  - `test_crowded_house` — all nine planets at 100°–100.8° with `lagnaN 4`: `#s23-bv-h1` lists 36 conjunctions; 375 px still has no sideways scroll.
  - In `BROWSER_SCRIPT`: click `.s23-view-btn[data-view="layer"]` before `EXTRACT` and before the layout/print measurements (the By-layer tests keep reading rendered text); `test_crowded_chart_still_renders` expects 16 tables (the planet table added).
- [ ] **Step 2:** `timeout 900 python3 -m unittest test_page_fixes.BhavaView -v` → FAIL (no `.s23-view-btn`).
- [ ] **Step 3: Implement** the render functions, CSS (phone: the planet table stacks into labelled rows, the facts box into one column, the jump bar wraps; print: buttons and jump bar hidden), the `beforeprint` / `afterprint` handlers also opening and restoring `details.s23-bv-rest`, and `renderS23Sections` calling `s23WirePredictions`. The intro paragraph adds one sentence: "By bhāva reads them house by house, as Session 28 does; By layer shows each layer for every planet."
- [ ] **Step 4:** `timeout 1800 python3 -m unittest test_page_fixes test_session23_cross_impl.BrowserSession23 test_session23_cross_impl.PageBlocks` → OK. Any other test that reads the By-layer view's rendered text and now fails because the pane is hidden clicks By layer first (ledger which).
- [ ] **Step 5: Commit** "Page: Prediction read bhāva by bhāva (default) or by layer" and push.

### Task 4: Excel — shared builders for the house block (no formula change)

**Files:** Modify `make_session23_xlsx.py` (`_life_area_sheet`)

**Interfaces:**
- Produces (module level; `S23_LifeArea_Calc` calls them with its own constants):
  - `_helper_table(ws, rules)` — the per-planet helper table (rows `HELP_ROW0`…, columns `H_*`) and the default aspect meaning.
  - `_reading_counts(ws, rules, lr_row0, block_rows)` — the running counts of her readings, one 18-column group per block start row in `block_rows`.
  - `_house_block(ws, rules, blk, b0, house_cell, lr_row0)` — the 75-row block (bhava, occupants, aspects, lord, Parivartana, company, Supports / Pressure columns) for the house in `house_cell`.
  - `_karaka_rows(ws, rules, row0, kline_row0, karaka_cells, note_cell)` — the kāraka rows and their summary lines.
  - The helper closures (`hf`, `gate`, `summary`, `readings`, `lr_col`, …) become module-level functions taking what they used to capture.

- [ ] **Step 1: Record the formulas before.** Build a workbook and dump every non-empty cell of `S23_LifeArea_Calc` (`{coordinate: value}`) to `<workspace>/la_before.json`.
- [ ] **Step 2: Refactor** into the four builders; `_life_area_sheet` calls them.
- [ ] **Step 3: Compare:** the same dump after the refactor equals `la_before.json` exactly. Expected: no difference.
- [ ] **Step 4:** `timeout 2400 python3 -m unittest test_session23_cross_impl.ExcelLifeAreas test_session23_cross_impl.ExcelFormulaLimits` → OK.
- [ ] **Step 5: Commit** "Excel: Life-areas house block as shared builders (no formula change)" and push.

### Task 5: Excel — `S23_Bhava_Calc`

**Files:** Modify `make_session23_xlsx.py` (`CALC_NAMES` gains `"Bhava_Calc"` before `"Ref_Calc"`; new `_bhava_sheet`, `bhava_from_sheet`, `bhava_sheet_view`; `_ref_sheet` gains lookup columns; `build_calc_sheets`); Test `test_session23_cross_impl.py` (new class `ExcelBhava`)

**Interfaces:**
- Consumes: Task 4's builders; `S23_Predict_Calc` columns (`PREDICT_COLS`), `S23_Roles_Calc`, `S23_Classes_Calc` matrix.
- Produces:
  - `BHAVA_CELL = "B2"` (drop-down 1–12, default 1), with the sections in the spec's order: header rows (house, sign #, rāśi, name, full name, sign line, kārakas, Supports, Pressure); a classes table (one row per class: in-house flag, name, other names, meaning (P2), note); significations / people / body; a facts table (9 rows, one per planet: house, classes, roles, dignity label, dignity effect, digbala word, digbala text (P1), strength, reasons, class texts, Graha + Rāśi text, status, tatwa, direction, varna, mode); one `_house_block` and its `_reading_counts`; Layer 1 occupant extras from `S23_Predict_Calc` (points, extra, moon strength, Session 26 lines, 12th line, degree stage, age note, conditions, active, readings, dignity line); `_karaka_rows` for the house's kārakas (blank note cell); the 36 conjunction rows (flag: both in the house's sign; text from `S23_GrahaPair`; combust note when the Sun is within `COMBUST_ORB` of a combustible planet); the 216 planet-aspect rows (by, slot, to; flag: the aspect falls on the house's sign and `to` sits there; text built as `graha_graha` builds it, plus the pair's aspect text); the 16 life-area rows (flag: the area's Houses include B2).
  - `_ref_sheet` new columns after column 45 (constants `REF_…`): kārakas per house (", "-joined BHAVA_INFO karaka); tatwa, direction, varna, traits (", "-joined) per sign; qualities, signifies and combustion effect per planet.
  - `bhava_from_sheet(ws) -> dict` and `bhava_sheet_view(reading) -> dict` (P3): the view keeps `bhava_reading`'s keys and order with these changes — occupants `{planet, nature, facts, text, status, extra ("\n"-joined), moon_strength, nature_lines ("\n"-joined texts), twelfth_line, degree_stage (" "-joined lines or ""), age_note, conditions ("\n"-joined texts), active (", "-joined keys of active ones), readings, graha_rashi, dignity_line}`; lord without `source`; conjunctions `{a, b, text, status, combust_note}`; planet_aspects `{by, to, text, status}`; every `readings` list is the first `READINGS_SHOWN` plus `MORE_ON_PAGE` when longer; facts `{house, classes, roles, dignity (label), dignity_effect, digbala ("" for None), digbala_text, strength (word), reasons, class_texts ("\n"-joined)}`.

- [ ] **Step 1: Failing tests** — `ExcelBhava` (setUpClass as `ExcelLifeAreas`: one workbook per chart and house, `BHAVA_CELL` set, one `_lo_recalc`): charts SIMHA and Chart 3 (all twelve houses), `calc_charts(2, 919)` (all twelve), the `swap16` / `swap14` Parivartana probes of `ExcelLifeAreas` (houses 1, 4, 6) and `PROBE_M2` (houses 8, 12).
  - `test_every_house_equals_python` — `first_difference(bhava_sheet_view(br.bhava_reading(RULES, ctx, h)), bhava_from_sheet(ws)) is None` for every case.
  - `test_the_ninth_house_of_simha` — classes, Badhaka note, occupants, lord Mars, kārakas Sun and Jupiter, three conjunctions and three planet aspects (guards against an empty-equals-empty pass).
  - `S23_LifeArea_Calc` is guarded by the existing `ExcelLifeAreas` (run in Step 4).
- [ ] **Step 2:** `timeout 2400 python3 -m unittest test_session23_cross_impl.ExcelBhava -v` → FAIL (`BHAVA_CELL` missing).
- [ ] **Step 3: Implement** `_bhava_sheet`, the `Ref_Calc` columns, `bhava_from_sheet`, `bhava_sheet_view`.
- [ ] **Step 4:** `timeout 3600 python3 -m unittest test_session23_cross_impl.ExcelBhava test_session23_cross_impl.ExcelLifeAreas test_session23_cross_impl.ExcelSession23 test_session23_cross_impl.ExcelFormulaLimits test_session23_cross_impl.MasterWorkbookInstall` → OK.
- [ ] **Step 5: Commit** "Excel: S23_Bhava_Calc reads one house in the four layers" and push.

### Task 6: Guide, stamp, full suite, push

**Files:** Modify `docs/session23-master-workbook.md` (a "Bhāva by bhāva" section: the two views on the page; how to use `S23_Bhava_Calc` — pick the house in B2, what each block shows, that the facts and texts come from the same sheets as the other calculators; the one-time `py make_session23_xlsx.py --install` then `publish.bat`), `index.html` (stamp)

- [ ] **Step 1:** Write the guide section.
- [ ] **Step 2:** `python3 build_session23.py --stamp "Prediction read bhāva by bhāva"`.
- [ ] **Step 3:** Full suite (background) → OK.
- [ ] **Step 4: Commit** "Guide and build date: Prediction read bhāva by bhāva" and push; then the final review and the user's go-ahead before `main`.
