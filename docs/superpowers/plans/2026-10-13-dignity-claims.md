# Her dignity sentences show only when true — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Six of her Session 28 sentences that state a planet's dignity show only when that dignity holds in the chart, identically on the page, in Python and in the Excel calculator.

**Architecture:** The six rules are code constants (user decision Y2), keyed by her row's key cells. Python (`bhava_rules.py`) owns them; the Excel builder imports them from `bhava_rules` and turns them into formulas; the page keeps a JS copy that a test compares with Python's. No data change.

**Tech Stack:** Python 3 (openpyxl, unittest), vanilla JS in `index.html`, Playwright/Node for page parity, LibreOffice headless for Excel recalculation.

**Spec:** `docs/superpowers/specs/2026-10-13-dignity-claims-design.md`

## Global Constraints

- Branch `claude/quirky-hawking-h3aaoy`; push it after Task 4. Never push `main` without the user's explicit yes; never open a PR.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_019v79NvxiFMCa67AXVpo3Hc`. No model identifiers anywhere else.
- Exalted = dignity flag `exalted` (labels Exalted, Deep Exalted); debilitated = flag `debilitated` (Debilitated, Deep Debilitated).
- A planet missing from the chart fails its rule.
- `session23_rules.json`, the workbook data sheets and her texts do not change.
- Excel 2007 functions only; every formula ≤ 8,192 characters (`ExcelFormulaLimits`).
- Her Chart 3 is unchanged (`test_every_lord_line_of_hers_shows` stays green).
- Full suite (~10 min): `python3 -m unittest test_ashtakavarga test_cross_impl test_session23_data test_teacher_slides test_bhava_rules test_teacher_charts test_session23_cross_impl test_page_fixes test_patch_master_workbook`

## Review Focus

1. **Parivartana claim fails, a direction's claim holds** (Tula Lagna, 8th lord Venus debilitated in Kanya, 12th lord Mercury in Vrishabha): the exchange text goes, her 8→12 line stays. Test: `test_parivartana_text_needs_the_12th_lord_debilitated` (Task 1), Excel probe T1 (Task 3).
2. **Deep dignity counts** (Chart 3's Sun at 10° Mesha is Deep Exalted): the Sun rule holds. Test: Chart 3 cases (Tasks 1, 3).
3. **The claimed planet missing** (partial chart without the Sun): the 1st-lord reading is hidden, page = Python. Test: `test_missing_planet_fails_the_rule` (Task 1), `test_dignity_claims_equal_python` (Task 2).
4. **A weak lord that is not debilitated** (enemy's sign, or with Rāhu): her "debilitated" line is gone and, with no other row, the blend shows. Test: `test_lord_lines_need_their_dignity` (Task 1).
5. **Rows reordered in `S23_ChartReadings`**: the Excel rule reads the row's own cells. Covered by construction (Task 3 formula reads columns A–E of its row).

## Probe charts (signs 0-based, Mesha = 0; all degrees 15 unless stated)

- **M1** Mesha Lagna: Sun 9, Moon 8, Mars 11, Mercury 9, Jupiter 4, Venus 3, Saturn 3, Rahu 11, Ketu 5 — 7th lord Venus and 10th lord Saturn weak in the 4th (enemy), 8th lord Mars weak in the 12th (with Rāhu), 9th lord Jupiter in the 5th (not exalted). All four of her lines hide.
- **M2** Mesha Lagna: Sun 9, Moon 6, Mars 11, Mercury 9, Jupiter 7, Venus 1, Saturn 2, Rahu 2, Ketu 8 — 8↔12 exchange, 12th lord Jupiter in Vrischika (friend): the exchange text hides; the exchange blend shows.
- **T1** Tula Lagna: Sun 9, Moon 3, Mars 0, Mercury 1, Jupiter 2, Venus 5, Saturn 10, Rahu 2, Ketu 8 — 8↔12 exchange, 8th lord Venus debilitated, 12th lord Mercury not: exchange text hides, her 8→12 line shows.
- **D1** her Chart 3 with the Sun in Vrishabha (1) — the 1st-lord reading hides; every other Chart 3 reading stays.

---

### Task 1: Python rules

**Files:** Modify `bhava_rules.py` (`chart_readings`, `_taught_rows`, `bhava_bhava`); Test `test_bhava_rules.py` (new class `DignityClaims`)

**Interfaces:**
- Produces:
  - `READING_CLAIMS: dict[(kind, planet, with_, house, condition)] -> (who, flag)` = `{("aspects", "1st lord", "", 1, ""): ("Sun", "exalted")}`
  - `LORD_IN_CLAIMS: dict[(lord_of, sits_in, condition, exchange)] -> (who, flag)` = `{(9, 5, "", False): ("lord", "exalted"), (8, 12, "", True): ("12th lord", "debilitated"), (7, 4, "weak", False): ("lord", "debilitated"), (8, 12, "weak", False): ("lord", "debilitated"), (10, 4, "weak", False): ("lord", "debilitated")}`
  - `claim_holds(rules, ctx, claim, lord_of=None) -> bool` — `claim` None → True; `who` is a planet name, `"Nth lord"`, or `"lord"` (the lord of `lord_of`); a planet not placed → False; else its dignity flag equals `flag`.
  - `_taught_rows(rules, ctx, x, y, strength_word)` (gains `ctx`; drops rows whose claim fails).

- [ ] **Step 1: Write the failing tests** (`DignityClaims`, helper `bb(lagna, signs)` → `{lord_of: entry}` from `br.bhava_bhava(RULES, br.context(lagna, signs, {p: 15.0 for p in signs}))`):
  - `test_lord_lines_need_their_dignity` — M1: entries 7, 8, 9, 10 contain none of "is debilitated and posited", "8th Lord Moon is debilitated", "9 th lord Sun is exalted", "10 th lord Mercury is debilitated"; entry 9 status `"blend"`.
  - `test_parivartana_text_needs_the_12th_lord_debilitated` — M2: entry 8 (`exchange` 12) text starts `"Parivartana: the lords of the 8th and 12th"` (status `"blend"`); T1: entry 8 has no "12 th lord Mars is debilitated" and contains "8th Lord Moon is debilitated".
  - `test_sun_claim_on_the_lagna_lord_reading` — D1 (Chart 3 degrees): no `chart_readings` text containing "bhava karaka Sun"; Chart 3 itself: one.
  - `test_missing_planet_fails_the_rule` — Chart 3 signs without the Sun: no "bhava karaka Sun" reading; `br.claim_holds(RULES, ctx, ("Sun", "exalted"))` is False.
  - `test_deep_exalted_counts` — Chart 3: `br.claim_holds(RULES, ctx, ("Sun", "exalted"))` is True (the Sun is Deep Exalted at 10° Mesha).
- [ ] **Step 2:** `python3 -m unittest test_bhava_rules.DignityClaims -v` → FAIL (`claim_holds` not defined / lines present).
- [ ] **Step 3: Implement** the constants, `claim_holds`, the claim filter in `chart_readings` (key from the row's five cells), in `_taught_rows` (`LORD_IN_CLAIMS.get((x, y, r["condition"], False))`, lord of `x`), and in the exchange-row lookup of `bhava_bhava` (`LORD_IN_CLAIMS.get((r["lord_of"], r["sits_in"], r["condition"], True))`, lord of `r["lord_of"]`).
- [ ] **Step 4:** `python3 -m unittest test_bhava_rules test_teacher_charts` → OK (Chart 3 unchanged). Page/Excel parity tests are expected red until Tasks 2–3.
- [ ] **Step 5: Commit** "Her dignity sentences show only when true (Python)".

### Task 2: Page twins

**Files:** Modify `index.html` (`s23ChartReadings`, `s23TaughtRows`, `s23BhavaBhava`); Test `test_session23_cross_impl.py` (`JsEngine.test_dignity_claims_equal_python`)

**Interfaces:** Produces `S23_READING_CLAIMS` (`[{kind, planet, with, house, condition, who, flag}]`), `S23_LORD_IN_CLAIMS` (`[{lord_of, sits_in, condition, exchange, who, flag}]`), `s23ClaimHolds(ctx, claim, lordOf)`, `s23TaughtRows(ctx, x, y, strength)`.

- [ ] **Step 1: Failing test** `test_dignity_claims_equal_python`: the two JS constants equal Python's (same keys and values); for M1, M2, T1, D1 and Chart 3 without the Sun, `s23BhavaBhava`, `s23ChartReadings` and `s23LifeAreas` equal Python (`first_difference(...) is None`).
- [ ] **Step 2:** `timeout 900 python3 -m unittest test_session23_cross_impl.JsEngine -v` → the new test FAILs (constants missing).
- [ ] **Step 3: Implement** the twins exactly as Task 1.
- [ ] **Step 4:** `timeout 900 python3 -m unittest test_session23_cross_impl.JsEngine test_session23_cross_impl.PageBlocks` → OK (2,000-chart and partial-chart parity included).
- [ ] **Step 5: Commit** "Page: her dignity sentences show only when true".

### Task 3: Excel calculator

**Files:** Modify `make_session23_xlsx.py` (`_chart_readings_block`, `_life_area_sheet` lord rows); Test `test_session23_cross_impl.py` (`ExcelLifeAreas` probes, `test_dignity_claims_in_excel`)

**Interfaces:** New Predict_Calc column `CR_CLAIM = 68` (TRUE when the row's rule holds or it has none), built from `br.READING_CLAIMS` by matching the row's cells A–E; every `a` cell ANDs it. In `S23_LifeArea_Calc` the lord-row lookups M (exchange), N/O/P (lord of this house there) and Y/Z/AA (the other direction) return 0 when `br.LORD_IN_CLAIMS` has a rule for that key and it fails (dignity label of the named planet; "lord" = the lord of the row's LordOf house).

- [ ] **Step 1: Failing tests:** add to `ExcelLifeAreas.setUpClass` the probes M1 (areas 11, 12, 13), M2 (15), T1 (15), D1 (1); new `test_dignity_claims_in_excel`: for those cases the lord texts and aspect readings of `life_area_from_sheet` contain none of the hidden sentences and equal Python; `test_every_area_equals_python` covers the rest.
- [ ] **Step 2:** `timeout 2400 python3 -m unittest test_session23_cross_impl.ExcelLifeAreas test_session23_cross_impl.ExcelFormulaLimits` → FAIL.
- [ ] **Step 3: Implement** the claim column and the lookup gates (generated from the Python constants).
- [ ] **Step 4:** `timeout 2400 python3 -m unittest test_session23_cross_impl.ExcelFormulaLimits test_session23_cross_impl.ExcelSession23 test_session23_cross_impl.ExcelLifeAreas` → OK.
- [ ] **Step 5: Commit** "Excel: her dignity sentences show only when true".

### Task 4: Guide, stamp, full suite, push

**Files:** Modify `docs/session23-master-workbook.md` (a short "Her sentences that state a dignity" section listing the six rows and that changing a key cell turns the rule off), `index.html` (stamp)

- [ ] **Step 1:** Write the guide section.
- [ ] **Step 2:** `python3 build_session23.py --stamp "Her dignity sentences show only when true"`.
- [ ] **Step 3:** Full suite → OK.
- [ ] **Step 4: Commit** "Guide and build date: her dignity sentences" and push the branch; then the final review (executing-plans) and the user's go-ahead before `main`.
