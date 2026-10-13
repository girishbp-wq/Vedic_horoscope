# Prediction read bhāva by bhāva — design

Date: 2026-10-13 · Status: approved in conversation, awaiting written-spec review

Follows the audit and draft of 2026-10-13 (the user's own chart, published as a private artifact, version 4), which
the user judged "far better and easier to interpret". It changes how the Prediction section is **shown**; no rule
and no text of hers changes.

## 1. Purpose and success criteria

Today the Prediction section shows the four layers one after the other (all planets in Layer 1, then all lords in
Layer 2, and so on), so reading one house means collecting pieces from four places. Session 28 reads a chart the
other way: one bhāva at a time, with everything that bears on it. This work adds that view.

Done means:
1. The Prediction section opens on **By bhāva**: twelve house panels, each holding the four layers, the house's
   classes, the dignity, digbala and strength of every planet that bears on it, its kāraka(s) and its life areas.
2. **By layer** — today's view — stays one click away, unchanged.
3. Nothing is lost: every text the By-layer view shows for a chart also appears in the By-bhāva view, under the
   house it belongs to.
4. Python (`bhava_rules.py`) and the page compute the same house readings on 2,000 random charts and on partial
   charts; the Excel calculator gains a sheet that fills the same headings for a house picked in B2 and equals Python.
5. No data change: `session23_rules.json` and the workbook data sheets stay as they are.

## 2. Decisions (the user's)

| # | Decision |
|---|---|
| B1 | **Layout (choice A):** "By bhāva" is the default tab of the Prediction section; today's layer view stays as a "By layer" tab. |
| B2 | **Scope (choice A):** page + Python + a new Excel sheet `S23_Bhava_Calc`. |
| B3 | Each panel carries the sub-headings **Graha + Bhāva, Bhāva + Bhāva, Graha + Rāśi, Graha + Graha** (draft v2). |
| B4 | Every planet shown in a panel carries its **dignity and digbala** with its strength (draft v3). |
| B5 | Each house shows its **classes** — Kendra, Trikona, Panapara, Apoklima, Upachaya, Apachaya, Maraka, Dusthana, Badhaka, Trishadaya — with what each means (draft v4). |
| B6 | The design in §3–§6 as presented ("yes, please go ahead"). |

## 3. The page

### 3.1 The two views
- The Prediction section (`#s23-predict-body`) opens with two buttons in the style of the Life-areas buttons:
  **By bhāva** (active on load) and **By layer**. One view shows at a time; the choice is kept while the page is
  open (a new chart keeps the view last chosen).
- **By layer** is today's content, unchanged, still built by today's code. Its cards, tables and ids
  (`.s23-gb`, `#s23-bb`, `#s23-gr`, …) stay as they are; the By-bhāva view uses its own class names (prefix
  `s23-bv`) so nothing that reads the By-layer view picks up the new one.
- The introduction paragraph and tag legend stay above both views.

### 3.2 By bhāva — the top
- **Planet table:** one row per planet — glyph and name (℞ when retrograde), rāśi, degree, house, dignity,
  digbala (gains / loses / —), strength (strong / weak / mixed / depends).
- **Jump bar:** twelve links, one per house (number and rāśi). It stays in view below the report's own navigation
  bar while the panels scroll; each panel ends with a link back to it. Hidden in print.

### 3.3 One panel per house (1st to 12th), in this order
1. **Header:** house number, short name and rāśi; the full name; the house's class chips.
2. **Classes:** one line per class of the house — its name, other names in brackets, and the first sentence of its
   `Nature` (S23_Classes). For the Badhaka house, add: "For a {movable / fixed / dual} ({mode}) Lagna the {N}th is
   the Badhaka sthāna; its lord {planet} is the Badhakādhipati."
3. **Signifies · People · Body** (BHAVA_INFO).
4. **Supports / Pressure:** Session 27's step 7 for this one house, with the house's kāraka(s) from BHAVA_INFO
   (the same rule as a one-house life area).
5. **Layer 1 · Graha + Bhāva**
   - *In the house:* each planet in it, with its **facts box** (§3.4, full form), the Moon's pakṣa note, her reading
     (first paragraph; the rest behind "Read the rest"), the recording's extra points, and in a side list: the
     Session 26 lines, the 12th-house line, the degree stage (with the age note), the conditions (marked "active
     now" when the running daśā triggers them), and her Session 28 sentences. "No planet sits here." when empty.
   - *Aspecting the house:* each planet whose aspect falls on it — name, nature, aspect, the houses it rules, the
     aspect meanings and her sentences. "No aspect falls on this house." when none.
6. **Layer 2 · Bhāva + Bhāva:** the house's lord with its facts box (short form), "The {N}th lord sits in the
   {M}th ({rāśi})." with "Parivartana with the {K}th" when it exchanges, the placement line, her text or the blend
   (status tag; "Read the rest"), and the dictum when the lord aspects its own house. A lord missing from a partial
   chart: "Its lord's sign is not known."
7. **Layer 3 · Graha + Rāśi:** the sign line of the house's rāśi; then, for each planet in the house, its Graha +
   Rāśi text (hers or the blend, with its tag), its tatwa · direction · varna · mode, and its dignity line.
8. **Layer 4 · Graha + Graha:** the conjunctions in this house (with the combustion note); the aspects that fall on
   a planet in this house; and the planets with or aspecting the house's lord (houses they rule, meanings, her
   sentences). "No planet meets or aspects another here." when all three are empty.
9. **Kāraka:** each kāraka of the house — where it sits (house, rāśi), the malefics that aspect it, and its facts
   box (short form). A kāraka missing from a partial chart is left out.
10. **Life areas that read this house:** one link per area whose houses include it; the link opens the Life-areas
    section on that area and scrolls to it.

Status tags (taught / curated / blend) and source references appear wherever the By-layer view shows them.

### 3.4 The facts box
For a planet, a short labelled list:
- **House:** its house with that house's class chips.
- **Roles:** its roles for this Lagna from the Roles tab (Maraka lord, Dusthana lord, Badhakādhipati, Badhaka
  occupant, Trishadaya lord, …), or "—".
- **Dignity:** the dignity label (chip), its note, and — full form only — the Dignity-effect text.
- **Digbala:** gains / loses / — and one line: "gains directional strength in the {N}th (its strongest house)";
  "loses directional strength in the {N}th, opposite its strongest house, the {S}th"; "neither — strongest in the
  {S}th, weakest in the {W}th"; for a node, "none — a node has no directional strength".
- **Strength:** the word and its reasons.
- **Class rules** — full form only: the class-rule texts that apply to it in its house.

The full form is used for a planet in the house (Layer 1); the short form for the lord and the kārakas, whose full
box is in the panel of the house they sit in.

### 3.5 Reading on any screen, and print
- At phone width nothing scrolls sideways: the planet table stacks into labelled rows, the facts box into one
  column, the jump bar wraps.
- "Read the rest" is a `<details>`; printing opens every one (and closes them again afterwards), as the page
  already does for its sections.
- Print shows the view chosen on screen, without the view buttons and the jump bar.
- The site's colours and fonts; no new external files.

### 3.6 What repeats (accepted)
A planet appears in full in the house it sits in, and again, briefly, wherever it aspects, rules, accompanies a
lord or acts as a kāraka. That is the cost of reading each house whole; the short form keeps the repeats brief.

## 4. Python and the page engine

Two new functions in `bhava_rules.py`, built only from the existing ones (`graha_bhava`, `_bhava_step`,
`bhava_bhava`, `graha_rashi`, `graha_graha`, `with_lord`, `_karakas`, `_summary`, `planet_roles`, `badhaka`,
`house_class_matrix`, `strength_detail`, `digbala`, `chart_conditions`):

- `planet_facts(rules, ctx, planet) -> dict | None` — None when the planet is not in the chart; else
  `{planet, sign, rashi, deg, house, retro, nature, classes, roles, dignity: {label, flag, note}, dignity_effect,
  digbala ("strong" | "lost" | "" ; None for a node), digbala_text, strength: {word, reasons}, class_texts}`.
- `bhava_reading(rules, ctx, house, layer2=None) -> dict` — `layer2` is `bhava_bhava(rules, ctx)`, computed once when
  the caller reads all twelve houses. Returns
  `{house, sign, rashi, name, full_name, significations, people, body, classes: [{name, other_names, meaning, note}],
  sign_line, supports, pressure, occupants, aspecting, lord, conjunctions, planet_aspects, lord_company, karakas,
  life_areas: [{no, area}]}`, where
  - each occupant is `{planet, facts, text, status, source, extra, moon_strength, nature_lines, twelfth_line,
    degree_stage, conditions, readings, graha_rashi: {text, status, tatwa, direction, varna, mode}, dignity_line}`;
  - `aspecting` is today's aspect list for the house (by, aspect, rules, meanings, readings);
  - `lord` is None for an unplaced lord, else `{planet, facts, house, sign, rashi, exchange, placement_line, text,
    status, source, dictum}` (`exchange` = the other house of a Parivartana, else None);
  - `conjunctions` / `planet_aspects` are the `graha_graha` entries whose house is this one;
  - `lord_company` is `with_lord` for the lord; `karakas` are today's kāraka entries plus `facts`.

The page gets the twins `s23PlanetFacts(ctx, planet)` and `s23BhavaReading(ctx, house, layer2)` in the `s23` engine,
and the renderer for §3. The By-bhāva view renders only from `s23BhavaReading` and the planet table only from
`s23PlanetFacts`.

## 5. Excel: `S23_Bhava_Calc`

A new calculator sheet, built by `make_session23_xlsx.py` like the others (Excel 2007 functions only; every formula
≤ 8,192 characters).

- **B2** picks the house (1–12, a drop-down). The headings of §3.3 follow, in the same order, as labelled rows:
  header, classes with meanings and the Badhaka note, significations / people / body, Supports, Pressure, the four
  layers, the kārakas, the life areas.
- **Reused, not copied:** the Life-areas house block (occupants, aspects, lord, Parivartana, company, and its
  Supports / Pressure columns) and its kāraka rows become one shared builder that both `S23_LifeArea_Calc` and
  `S23_Bhava_Calc` call; `S23_LifeArea_Calc` keeps its layout and results. Planet columns already on
  `S23_Predict_Calc` (reading, dignity, dignity line, digbala line, strength and reasons, Session 26 lines,
  degree stage, readings) and `S23_Roles_Calc` are referenced, not recomputed.
- **New:** the facts per planet (house classes, roles, digbala text); Graha + Rāśi (her row in `S23_GrahaRashi`,
  else the blend from the rāśi's tatwa, direction, varna, mode and traits); Graha + Graha (each pair's conjunction
  text from `S23_GrahaPair` with the combustion note; each aspect onto a planet in the house, from the two planets'
  karakatwas and the pair's aspect text); the house's kārakas from BHAVA_INFO; the life areas reading the house.
  The lookup tables these need (rāśi traits, karakatwas, house kārakas, class meanings) go on `S23_Ref_Calc`.
- `bhava_from_sheet(ws)` reads the sheet back into the shape of `bhava_reading`, for the tests. As on
  `S23_LifeArea_Calc`, her sentences show the first four, then "(more on the page)".

## 6. Checks

- **Python:** `bhava_reading` on her Chart 3 and on the user's chart (Simha Lagna) — each house's occupants,
  lord, Parivartana, kārakas, classes and Badhaka note as expected; an unplaced lord and kāraka in a partial chart;
  `planet_facts` digbala lines for strong, lost, neither and a node.
- **Nothing lost:** for random charts, every text of the By-layer data (graha_bhava points, extra, nature lines,
  dignity / digbala / 12th lines, degree stage, class texts, conditions, readings; each bhava_bhava entry; each
  graha_rashi text; each conjunction and aspect text) appears in the `bhava_reading` of its house.
- **Page = Python:** `s23BhavaReading` and `s23PlanetFacts` equal Python on the 2,000 random charts and the
  partial-chart test (`first_difference` is None).
- **Page:** By bhāva is the default; switching shows By layer unchanged (existing tests keep passing); twelve panels
  with the four layer headings; the jump bar links work; a life-area link opens that area; no horizontal scroll at
  375 px; print opens every "Read the rest" and hides the buttons and jump bar.
- **Excel = Python** through LibreOffice: every house on her Chart 3 and on the user's chart, and the probe charts
  already used for Life areas; `S23_LifeArea_Calc` results unchanged after the refactor; formula lengths.

## 7. Delivery

- No data change; the calculator gains `S23_Bhava_Calc`. After release: `py make_session23_xlsx.py --install`
  (rebuilds the calculator sheets, adding the new one), then `publish.bat`, which reports no changes.
- Guide (`docs/session23-master-workbook.md`): a "Bhāva by bhāva" section — the page's two views and how to use
  `S23_Bhava_Calc`.
- Build stamp: `build_session23.py --stamp "Prediction read bhāva by bhāva"`.

## 8. Not in scope

Any change to a rule or to her texts; reordering the Life-areas section; Round 2 (yogas) and Round 3 (Muhūrta).
