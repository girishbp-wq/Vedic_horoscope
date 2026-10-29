# Session 25 class (29 Oct 2026) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the class of 29 Oct 2026 (Mercury and Jupiter in the 12 bhāvas, her placement remedies, her Q&A on
strength) into the rules, the page and the Excel calculator: items A–F of the review, as the user approved.

**Architecture:** As for the class of 22 Oct: the class content is data (`session25_class_texts.py`, applied by
`apply_teacher_slides.apply_s25_class()` as one more release step). Two sheets gain columns — `S23_GrahaInBhava`
(IfWeak, IfStrong) and `S23_Remedies` (Houses) — and two rules live in all three engines (Python, page, Excel), kept
equal by the parity tests: which remedy rows a planet's card lists, and the overall strength.

**Tech Stack:** Python 3 + openpyxl, the single-page `index.html`, Excel 2007 formulas, unittest + node + Playwright.

**Spec:** the review `session25_review.md` sent to the user on 29 Oct 2026, and the user's answer: "Build A-F, on D.
include session 29 which is already there plus the additional points captured from today". (The deck named "S25" in
source fields is a different thing: the slide deck of an earlier term.)

## Global Constraints

- The three engines must agree (Python `bhava_rules.py`, the page's `s23*` functions, the Excel calculator sheets).
- Excel formulas: Excel 2007 functions only, under 8,192 characters each.
- The shipped JSON equals the release chain applied to `session23_rules.previous.json` (test).
- `--install` upgrades rows still as shipped by any earlier release (now including the class of 22 Oct), keeps rows
  the user edited, adds new rows and the new columns.
- Every workbook text is escaped on the page; new blocks work at 375 px with no sideways scroll.
- Source of the class content: `Class 29 Oct 2026`.

## Decisions

- **D1 — class points (A, E).** `GRAHA_IN_BHAVA_EXTRA[(Mercury|Jupiter, house)]` = the review's points that hold
  whatever the planet's strength. The 1st-house rows open with the planet's general rule. Jupiter in the 2nd, 3rd,
  5th, 7th, 9th and 10th add her respect line for that bhāva's person (E).
- **D2 — strength points (C).** New `S23_GrahaInBhava` columns **IfWeak** and **IfStrong** (one line each, like
  Extra); rules rows gain `if_weak`, `if_strong` (lists, `[]` by default). The card shows them by the **overall**
  word (D4): weak → IfWeak under "As <planet> is weak:"; strong → IfStrong under "As <planet> is strong:"; mixed or
  depends → both, under "If <planet> is strong:" and "If <planet> is weak:".
- **D3 — remedies by house (B).** New `S23_Remedies` column **Houses** (a comma list; blank = a general remedy).
  A planet's card lists the rows whose Topic is that planet and whose Houses include its house. The Mars rows get
  `2, 7, 8, 12`, so `MARS_REMEDY_HOUSES` leaves the code; the Kuja rows stay in the Kuja Doṣa section. Rows with a
  condition say it in their text ("If Mercury is weak: …"). "Remedies to strengthen a graha" lists every planet row
  with the houses it is for.
- **D4 — strength (D).** The Session 29 word (`strength_detail`, unchanged) still chooses Session 29's own texts
  (the lord-in rows, the class rule "not weak", life-area kārakas): her S29 deck gives "strong" texts for a lord in
  the 6th, 8th or 12th, which a house penalty would make unreachable. New **overall** strength =
  `strength_overall(rules, ctx, planet)` → `{word, stronger, weaker}`:
  - weak outright: the S29 weak reasons (debilitated, enemy's sign, combust, with Rāhu), or **with Saturn, Mars or
    Ketu** (her class);
  - stronger: the S29 good sign (exalted, Mūlatrikoṇa, own, friend's), **in a Kendra or Trikoṇa**, **with a benefic**
    (Jupiter, Venus, Mercury, the Moon), **aspected by a benefic**;
  - weaker: **in a duṣthāna (6, 8, 12)**, aspected by a malefic (S29's list: Sun, Mars, Saturn, Rāhu, Ketu);
  - word: strong (stronger only), mixed (both), weak (weaker only), depends (neither; a neutral sign with nothing
    else). Phrases: "in the 1st (Kendra and Trikoṇa)", "in a Kendra (the 4th)", "in a Trikoṇa (the 5th)",
    "in a duṣthāna (the 6th)", "with Jupiter", "aspected by Venus"; lists in planet order.
  - Shown on the planet card and in the bhāva view's planet facts beside the S29 word: "Strength (S29): …" and
    "Overall, with the class of 29 Oct: …".
- **D5 — Kuja doṣa in a child (F).** One `Kuja` row: the child does the remedy themselves.
- **D6 — upgrade.** `shipped_versions()` adds the class-of-22-Oct release; rows from before the Houses column with
  Topic Mars and blank Houses get `2, 7, 8, 12` (what the code did for them); guide section "Session 25 class —
  one-time update"; build stamp.

## Review Focus

1. A user who edited a Mars remedy text before this release: after `--install` it still shows for Mars in the 2nd,
   7th, 8th and 12th (its Houses filled), and is listed as kept. Test in T1.
2. A planet with no factor at all (neutral sign, house 2, 3 or 11, alone, unaspected): overall "depends", both
   point lists labelled "If …". Test in T2.
3. Rāhu or Ketu as the subject (they take their exaltation signs, never "with" each other). Test in T2.
4. A user-added remedy row with Houses "6" for Venus: it shows on Venus in the 6th on the page and in Excel. Test in
   T4.
5. Point text with quotes or `<`: escaped. Phone width: the new blocks wrap. Tests in T3.

---

### Task 1: The data — class texts, two sheet columns, the release chain

**Files:** create `session25_class_texts.py`; modify `apply_teacher_slides.py`, `build_session23.py` (SHEETS,
rules_to_rows, read_workbook, validation, README), `make_session23_xlsx.py` (`shipped_versions`, Mars Houses
migration), `session23_rules.json`, `index.html` (data block); tests in `test_teacher_slides.py`,
`test_session23_data.py`, `test_session23_cross_impl.py`.

**Interfaces:** `session25_class_texts.GRAHA_IN_BHAVA_EXTRA / IF_WEAK / IF_STRONG: dict[(str, int), list[str]]`,
`REMEDIES: list[(topic, text, houses: list[int], source)]`; `apply_teacher_slides.apply_s25_class(rules)`; rules rows
`graha_in_bhava[].if_weak / if_strong`, `remedies[].houses`.

- [ ] Tests first: S25ClassTexts (24 keys Mercury/Jupiter × 1–12 in EXTRA; IF_WEAK/IF_STRONG keys within those;
  remedy houses within 1–12; Kuja child row; no "TODO"); the JSON equals the chain ending in `apply_s25_class`; sheets
  round-trip the new columns; a bad Houses cell is reported; upgrade from the class-of-22-Oct release (new columns
  added, Mercury rows take the points, an edited Mars remedy keeps showing — Houses filled). Run: FAIL.
- [ ] Implement; `python3 apply_teacher_slides.py`; run the three modules: PASS. Commit.

### Task 2: Python — remedies by house, overall strength, strength points

**Files:** `bhava_rules.py`; `test_bhava_rules.py`.
**Interfaces:** `planet_remedies(rules, planet, house)` (data-driven); `strength_overall(rules, ctx, planet) ->
{word, stronger, weaker}`; `strength_points(rules, ctx, planet, house) -> [{"when": "weak"|"strong", "text"}]`;
`graha_bhava(...)` adds `overall`, `strength_points`; `bhava_reading` occupants and `planet_facts` add the same.

- [ ] Tests first: Mars rows by Houses as before; a Mercury row with Houses 2 shows for Mercury in the 2nd only; overall
  word table (own sign in the 6th → mixed; neutral in the 10th → strong; friend's sign with Saturn → weak; neutral
  in the 3rd alone → depends; benefic aspect → stronger); phrases; Rāhu exalted with Saturn → weak; strength points
  by word. FAIL, implement, PASS. Commit.

### Task 3: Page — engine twins and display

**Files:** `index.html`; `test_session23_cross_impl.py` (JS = Python on 2,000 random charts), `test_page_fixes.py`.
- [ ] Tests first: parity of remedies, overall and strength points; the card shows both strength lines and the
  labelled points; the bhāva view likewise; "Remedies to strengthen a graha" lists houses; Kuja child row in the Kuja
  section; escaping; 375 px. FAIL, implement, PASS. Commit.

### Task 4: Excel — Predict_Calc and Bhava_Calc

**Files:** `make_session23_xlsx.py`; `test_session23_cross_impl.py`.
- [ ] Tests first: Predict_Calc overall word / stronger / weaker / strength points / remedies equal Python on the random
  charts; Bhava_Calc equals `bhava_sheet_view`; a user-added Venus row with Houses 6 reaches Excel. FAIL, implement,
  PASS. Commit.

### Task 5: Guide, stamp, full suite, review, push

- [ ] Guide "Session 25 class — one-time update"; README lines for the new columns; `build_session23.py --stamp`;
  full suite; fresh whole-branch review; fixes; push the branch; ask before main.
