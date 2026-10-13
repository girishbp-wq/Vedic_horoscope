# Her sentences that state a dignity — design

Date: 2026-10-13. Follows the Sessions 28–29 spec (`2026-10-11-sessions28-29-chart-reading-dasha-design.md`),
whose final review raised the question.

## 1. Decisions (the user's)

| # | Decision |
|---|---|
| Y1 | A sentence of hers that states a planet's dignity shows only when that dignity holds in the chart being read. |
| Y2 | The rules are built into the code (option B), not a new workbook column. |
| Y3 | The "1st lord aspects the 1st" reading needs **both**: the 1st lord's aspects fall on the 1st house (as now) **and** the Sun is exalted. |

## 2. The six rules

Each rule belongs to one of her rows, found by the row's key cells (not its wording):

| Her row (sheet → key) | Source | Shows only when |
|---|---|---|
| `S23_ChartReadings`: Kind `aspects`, Planet `1st lord`, With blank, House 1, Condition blank | S28 p.2 | the Sun is exalted (in addition to the 1st lord aspecting the 1st) |
| `S23_BhavaLordIn`: LordOf 9, SitsIn 5, Condition blank, Exchange no | S28 p.12 | the 9th lord is exalted |
| `S23_BhavaLordIn`: LordOf 8, SitsIn 12, Condition blank, Exchange yes (8↔12 Parivartana) | S28 p.16 | the 12th lord is debilitated |
| `S23_BhavaLordIn`: LordOf 7, SitsIn 4, Condition weak, Exchange no | S28 pp.9-10 | the 7th lord is debilitated |
| `S23_BhavaLordIn`: LordOf 8, SitsIn 12, Condition weak, Exchange no | S28 p.11 | the 8th lord is debilitated |
| `S23_BhavaLordIn`: LordOf 10, SitsIn 4, Condition weak, Exchange no | S28 p.13 | the 10th lord is debilitated |

No Session 23–27 row states a dignity outside its own conditions (checked: `bhava_lord_in`, `conditions`,
`chart_readings`).

## 3. Behaviour

- **Exalted** means the dignity flag `exalted` (labels Exalted, Deep Exalted); **debilitated** means the flag
  `debilitated` (Debilitated, Deep Debilitated) — as the Condition column already reads them.
- A planet missing from the chart cannot be checked: the rule fails and the sentence does not show.
- **Chart reading:** a failed rule means the row matches nothing — no planet card, aspect list or Life-areas reading
  shows it.
- **Lord in a house:** a failed rule drops that row from her lines for the placement (Layer 2 entry, Life-areas
  step 4). Her other rows for the same placement still show; with none left, the existing blend of the two houses
  shows, as for any placement she did not read.
- **Parivartana row:** a failed rule drops the exchange text; her rows for either direction still show (each judged
  by its lord's strength and its own rule); with none, the existing exchange blend.
- Status and source come from the first line shown, as now.
- The rule follows the row's key cells. Editing her wording keeps the rule; changing a key cell (for example the
  Condition) means the rule no longer finds that row. The guide says so. The Parivartana row's rule follows the two
  houses (either order) and Exchange = yes, whatever its Condition — as the row itself is found (final review).
- Her Chart 3 (§9.1 of the Round 1 spec) is unchanged: all six claims are true there.

## 4. Where

The same six rules, written three times as for every rule, kept equal by the parity tests:
- Python (`bhava_rules.py`): two constants (chart-reading rules, lord-in-house rules) and one check used by
  `chart_readings`, the row choice for a lord in a house, and the Parivartana row lookup.
- Page (`index.html`, `s23*` engine): the same constants and check in the twins.
- Excel (`make_session23_xlsx.py`): the chart-reading block checks each row's own cells at run time (so reordering
  rows in `S23_ChartReadings` keeps it right); the Life-areas lord block gates each of its row lookups the same way.
  Excel 2007 functions only; formulas ≤ 8,192 characters.

## 5. Checks

- Python: for each rule, a chart where the placement matches but the dignity does not — the sentence is gone (and for
  the 9→5 row the blend shows instead; for the 8↔12 row her 8→12 line remains when the 8th lord is debilitated);
  her Chart 3 still shows all six; a chart with the Sun absent hides the 1st-lord reading.
- Page = Python on 2,000 random charts and the partial-chart test.
- Excel = Python through LibreOffice on probe charts for each rule (Predict, Life areas).

## 6. Delivery

No data change (`session23_rules.json` and the workbook data sheets stay as they are). The page and the Excel
calculator change: after release, `py make_session23_xlsx.py --install` rebuilds the calculator sheets; `publish.bat`
then reports no changes. The guide (`docs/session23-master-workbook.md`) lists the six rows. Build stamp:
`build_session23.py --stamp "Her dignity sentences show only when true"`.

## 7. Not in scope

A workbook column for such rules (option A, declined); Round 2 (yogas) and Round 3 (Muhūrta).
