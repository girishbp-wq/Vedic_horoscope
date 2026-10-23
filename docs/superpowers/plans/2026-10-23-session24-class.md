# Session 24 class (22 Oct 2026) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the Session 24 class (the Moon and Mars in the 12 bhāvas, her Mars remedy, her Q&A) into the
rules, the page and the Excel calculator, as the user approved: items 1–4 of the review.

**Architecture:** The class points and remedies are data — a new module `session24_class_texts.py`, applied by
`apply_teacher_slides.apply_s24_class()` as one more step of the release chain that writes `session23_rules.json` and
the page's `SESSION23-DATA` block; on the user's PC `make_session23_xlsx.py --install` carries the rows into the master
workbook. The one new rule (when the Mars remedies apply) lives in the three engines, Python, page and Excel, kept
equal by the parity tests, exactly as the 12th-house line is.

**Tech Stack:** Python 3 + openpyxl, the single-page `index.html`, Excel 2007 formulas, unittest + node + Playwright.

**Spec:** the approved review `session24_review.md` (sent to the user 2026-10-23; items 1–4 approved, 5 not) and the
class transcript of 22 Oct 2026. Its decisions are restated below as D1–D6.

## Global Constraints

- The three engines must agree (Python `bhava_rules.py`, the page's `s23*` functions, the Excel calculator sheets).
- Excel formulas use Excel 2007 functions only (no TEXTJOIN) and stay under 8,192 characters.
- The shipped JSON must equal the release chain applied to `session23_rules.previous.json` (test).
- `--install` upgrades rows still as shipped (any earlier release), keeps rows the user edited, adds new rows.
- The page escapes every workbook text; a new page block works at 375 px with no sideways scroll.
- Sources: class points carry no per-point source (as the Sun's "From the recording"); the remedies' source is
  `Class 22 Oct 2026`.

## Decisions

- **D1 — class points.** `GRAHA_IN_BHAVA_EXTRA[(planet, house)]` = the review's draft points for the Moon 1–12 and
  Mars 1–12 (the general rule for each planet is the first point of its 1st-house row only where it is new; otherwise
  the points stand alone). They fill the `extra` list of those 24 rows; the Sun's 12 rows are untouched.
- **D2 — remedy rows.** `S23_Remedies` gains: topic `Moon` × 3 (her Q&A, an emotional mind) after the Moon rows;
  topic `Mars` × 7 and topic `Kuja` × 2 after them (planet order). Source `Class 22 Oct 2026`.
- **D3 — the rule.** `MARS_REMEDY_HOUSES = (2, 7, 8, 12)`: she gave the remedy for Mars in the 8th "irrespective of
  the planet with Mars", said the 2nd and 12th take the same, and gave the Kuja rows for Mars in the 7th. So for
  Mars in one of those houses `graha_bhava(...)["remedies"]` = the `Mars` rows' texts, plus the `Kuja` rows' texts
  when the house is the 7th; otherwise `[]` (every other planet: `[]` — "Moon in the 8th, it is okay").
- **D4 — page.** Layer 1 and the bhāva view show `remedies` under the planet as "Remedies (her class, 22 Oct 2026)".
  "Remedies to strengthen a graha" lists Mars (its rows, then the Kuja rows, with when they apply). The Kuja Doṣa
  section shows the Mars and Kuja rows when the doṣa is present and not cancelled.
- **D5 — Excel.** `S23_Predict_Calc` gets a `Remedies` column (planet rows) built from a helper block below the
  sheet's other blocks (one row per `S23_Remedies` slot, a running concatenation); `S23_Bhava_Calc` shows it for
  each planet; `bhava_from_sheet` / `bhava_sheet_view` carry it.
- **D6 — upgrade path.** `shipped_versions()` also lists the Sessions 28–29 release, so rows shipped then count as
  untouched; the guide gets a "Session 24 class — one-time update" (pull, `--install`, save, publish).

**Ruling after the final review (user, 23 Oct 2026):** the `Kuja` rows show only in the Kuja Doṣa section, when the
doṣa is present and not cancelled; the Mars card (all three engines) shows the `Mars` rows for the 2nd, 7th, 8th and
12th, never the `Kuja` rows — so the card never lists a Kuja remedy for a doṣa the section has cancelled. This
replaces "plus the `Kuja` rows' texts when the house is the 7th" in D3.

## Review Focus

1. A user who edited the Moon in the 1st on `S23_GrahaInBhava`: `--install` keeps the edit and lists it; the other
   23 rows take the class points. Test in T1.
2. Mars in the 7th from the Lagna: the Mars rows and the two Kuja rows; Mars in the 4th (a Kuja position she gave no
   remedy for): none in Layer 1. Tests in T2.
3. A user who adds a remedy row of topic `Mars` on the sheet: it shows on the page and in Excel too (the page and the
   Excel helper read the sheet's rows, not a fixed count up to the slot limit). Test in T4.
4. Text with quotes or `<`: the page escapes it. Covered by the existing escaping test pattern in T3.
5. Phone width: the new lists wrap, no sideways scroll. Test in T3.

---

### Task 1: The data — class points, remedy rows, the release chain

**Files:** Create `session24_class_texts.py`; modify `apply_teacher_slides.py`, `make_session23_xlsx.py`
(`shipped_versions`), `session23_rules.json`, `index.html` (data block via `apply_teacher_slides.main()`);
tests in `test_teacher_slides.py`, `test_session23_data.py`, `test_session23_cross_impl.py`.

**Interfaces:** Produces `session24_class_texts.GRAHA_IN_BHAVA_EXTRA: dict[(str, int), list[str]]`,
`session24_class_texts.REMEDIES: list[(topic, text, source)]`, `apply_teacher_slides.apply_s24_class(rules) -> rules`.

- [ ] Tests first: `S24ClassTexts` (24 keys = Moon/Mars × 1–12, each 1–8 non-empty points, no `[`/`TODO`; remedy
  topics Moon 3, Mars 7, Kuja 2, source `Class 22 Oct 2026`); `test_json_is_previous_plus_all_rounds` (the chain now
  ends with `apply_s24_class`); `test_upgrade_from_s28_29_release` (master as the S28–29 release → install → the 24
  extras and 12 remedy rows arrive; an edited Moon-1 row is kept and listed). Run: FAIL.
- [ ] Implement; run `python3 apply_teacher_slides.py`; run the three test modules: PASS. Commit.

### Task 2: Python — the remedy rule

**Files:** `bhava_rules.py`; `test_bhava_rules.py`.
**Interfaces:** `MARS_REMEDY_HOUSES = (2, 7, 8, 12)`; `planet_remedies(rules, planet, house) -> list[str]`;
`graha_bhava(...)["remedies"]`; `bhava_reading` occupants carry `remedies`.

- [ ] Tests first: Mars in 8 → the 7 Mars texts in order; Mars in 7 → those + the 2 Kuja texts; Mars in 4, 9 → [];
  Moon in 8 → []; a `Mars` row added to rules → it appears. FAIL, implement, PASS. Commit.

### Task 3: Page — engine twin and the three places it shows

**Files:** `index.html`; `test_session23_cross_impl.py` (JsEngine parity), `test_page_fixes.py`.
**Interfaces:** `s23PlanetRemedies(planet, house)`; `s23GrahaBhava(...).remedies`.

- [ ] Tests first: JS = Python for `remedies` on 2,000 random charts; page: Layer 1 and the bhāva view show the
  Mars remedies for a chart with Mars in the 8th and none for Mars in the 9th; "Remedies to strengthen a graha"
  lists Mars; the Kuja section lists them when the doṣa is present and not cancelled; 375 px no sideways scroll.
  FAIL, implement, PASS. Commit.

### Task 4: Excel — Predict_Calc and Bhava_Calc

**Files:** `make_session23_xlsx.py`; `test_session23_cross_impl.py`.
**Interfaces:** `PREDICT_COLS["remedies"] = 32`; `BV_FACT_COLS["remedies"] = 31`; occupant `remedies` in
`bhava_from_sheet` / `bhava_sheet_view` as "\n".join.

- [ ] Tests first: Predict_Calc `remedies` = "\n".join(Python) on the random charts; Bhava_Calc equals
  `bhava_sheet_view`; a user-added `Mars` remedy row reaches Excel. FAIL, implement, PASS. Commit.

### Task 5: Guide, stamp, full suite, review, push

- [ ] Guide section "Session 24 class — one-time update"; `S23_Remedies` line mentions the Mars and Kuja topics;
  `build_session23.py --stamp`; full suite in the background; fresh whole-branch review; fixes; push the branch.
