# Session 23 — Bhava classifications, prediction layers and Daśā linking: design

Status: **draft for review** (2026-10-08). No code has been written.
Source: Session 23 slides (42-page PDF, read visually), the Session 23 recording transcript, and the confirmations the user gave on 2026-10-08.

## 1. Purpose and success criteria

Add what Session 23 teaches to the horoscope report, identically in **index.html**, **Python** and **Excel**:

1. The **10 classifications of bhavas**, shown for the generated chart as tables in the teacher's own format (house · rāśi · planets in it · lord), plus Badhaka for the chart's Lagna.
2. The **prediction layers** — Graha + Bhava, Bhava + Bhava, Graha + Rāśi, Graha + Graha (conjunction **and aspect**) — with **dignity inputs** (exaltation, debilitation, own, friend/enemy, deep points, directional strength).
3. **Curated text for all nine grahas in all twelve bhavas** (the Sun is taught in class; the other eight are curated).
4. **Maraka and Badhaka lords linked to the running Mahādaśā / Bhukti**, and a visible **Daśā–Bhukti tab**.

Done means: the slides' own example chart (Simha Lagna) reproduces every table printed on the slides; the three implementations agree on thousands of generated charts; the rest of the page renders exactly as before; and a reader can see for every sentence whether it was *taught*, *curated* or a *method blend*.

## 2. Provenance and confirmed decisions

| Item | Decision | Source |
|---|---|---|
| Ten classes and their houses | As on slides 2–24 | Slides |
| Apachaya | **1, 2, 4, 7, 8** (the recording said 2, 4, 7, 8; the slide is correct) | User, 2026-10-08 |
| Kendra table, 10th house | **Mercury & Rahu** (slide table "Mars & Rahu" is a typo) | User |
| Apoklima wording | Keep as printed: "Planets placed in these signs are considered weak. Except 9th house, it is considered as bad position to the planets" | User |
| Other 8 grahas | **Curated text**, not "not yet taught" | User |
| Dasha linking | Maraka and Badhaka lords linked to running Mahādaśā / Bhukti | User |
| Daśā–Bhukti | Needs a visible tab (see §7.4) | User |
| Graha + Graha | Include **aspect-based** as well as conjunction | User |
| Excel / Python delivery | Standalone files in the repo, like Ashtakavarga | User |

**Worked oracle.** The slides' V1 chart — Simha Lagna; Moon Tula 2°; Ketu + Mandi Vṛścika 15°; Saturn (retro) Makara 18°; Jupiter Kumbha 8°; Mars Karka 11°; Sun Mithuna 4°; Venus Mithuna 27°; Mercury Vṛṣabha 22°; Rahu Vṛṣabha 15° — is the test oracle. Every lord and occupant table on slides 5, 8, 11, 13, 15, 18, 20, 22 and 24 was recomputed from it and matched, apart from the one slide typo above. The six Badhaka examples spoken on the recording (Mesha→Kumbha/Saturn, Tula→Simha/Sun, Dhanu→Mithuna/Mercury, Kumbha→Tula/Venus, Karka→Vṛṣabha/Venus, Simha→Mesha/Mars) also match.

## 3. Scope

**In:** everything in §1; the slide-25 five-step checklist for a chosen bhava; print and mobile layouts; tests; the data workbook.

**Out (can follow):** Moksha Trikona (4, 8, 12 — mentioned on the recording only), twins' Lagna rules, Budha-Āditya yoga text (but see §10), transit-based timing, varga charts, Shodhana / Ashtakavarga changes.

## 4. Architecture — rules as data, three engines

```
Session23_Rules.xlsx        ← the editable source of truth (data sheets) + live-formula calculator sheets
        │  build_session23.py
        ▼
session23_rules.json        ← generated; read by Python; mirrored into index.html
        ├── bhava_rules.py            Python engine + CLI
        ├── index.html                SESSION23-START … SESSION23-END block (data, generated)
        │                             + hand-written JS engine beside it
        └── Excel calculator sheets   same logic as formulas (LibreOffice-recalculated in tests)
```

* The workbook is the place to correct or extend text — the same habit as the existing Classification workbook → `build_data.py` → `index.html` flow. When a later session teaches a graha, replace the `curated` row; the page picks it up on the next build.
* `build_session23.py` regenerates `session23_rules.json` and the marked block in `index.html`. The block sits outside the blocks `scripts/build_data.py` owns, so `publish.bat` leaves it alone (same arrangement as `ASHTAKAVARGA-START/END`).
* Reuse, don't rebuild: the page's `BHAVA_INFO`, `RASHI`, `KARAKATWAS`, `PLANET_PROFILE`, `RASHI_DIGNITY`, `DIGNITY_DEG`, `NATURAL_FRIENDS`, `SPECIAL_ASPECTS`, `planetDignity()`, `buildDasha()` and the aspect computation stay the single copies for the page. Python gets a port of `planetDignity()` and the dasha engine, **tested equal to the JavaScript** over a full planet × rāśi × degree grid and many birth dates.

New files: `Session23_Rules.xlsx`, `session23_rules.json`, `build_session23.py`, `bhava_rules.py`, `test_bhava_rules.py`, `test_session23_cross_impl.py`.

## 5. Data model (workbook sheets → JSON)

| Sheet | Rows | Content |
|---|---|---|
| `Classes` | 10 | name, houses (Badhaka rule instead), other names, nature, rule for grahas, slide refs |
| `ClassRules` | ~25 | machine-readable rules: *(class, graha-nature, effect text)* — e.g. (Kendra, benefic) → "powerful manifestations with smaller efforts"; (Upachaya, malefic) → "good results in dasa"; (Apachaya, natural malefic) → "does not do well"; (Panapara, any) → "moderately strong"; (Apoklima, any except 9th) → "weak" |
| `Badhaka` | 3 | modality → house (Chara 11, Sthira 9, Dwiswabhava 7) |
| `GrahaInBhava` | 9 × 12 = 108 | graha, bhava, text (3–5 points), **status** = `taught` (Sun, slides 28–41 + recording) / `curated` (the other eight) , source note |
| `GrahaPair` | 36 | unordered pair, conjunction text, optional aspect-flavour sentence, status |
| `BhavaLordIn` | 144 (+ curated) | lord of bhava A in bhava B: blend template inputs; curated override for 2L-in-7 (taught) |
| `RashiFlavour` | 12 | tatwa, direction, varna, mode, notes — pulled from the existing rāśi classification |
| `DignityEffect` | ~9 | dignity label → strength wording ("full force" … "diminished"), per slide 31 |
| `Digbala` | 7 | graha → bhava of directional strength; Sun 10th and Saturn 7th are taught; the rest follow the standard table (**to confirm**, §11) |
| `DashaRoleText` | 5 | Maraka, Badhaka, Dusthana lord, Trishadaya lord, Trishadaya Mahādaśā — wording from slides 17, 19, 21, 23 and the recording |
| `OCRNotes` | — | the discrepancy log (kept for audit) |

Every text row carries `status`: **taught** | **curated** | **blend**. The page and Excel print a small tag beside each line so nothing is mistaken for the teacher's own words.

## 6. Engine behaviour

### 6.1 Classification tables
For the generated chart: Lagna rāśi → house rāśis → lords (existing sign-lord map) → occupants (Sun…Ketu by sign). For each class, a table `house · rāśi · planets · lord` in the slides' column order, plus the lord's own placement ("lord sits in house N") — the extra column the teacher asks students to add. A **house × class matrix** (12 × 10) and a "belongs to" column summarise overlaps.

Badhaka: `mode(Lagna rāśi)` → house → sign → lord → occupants; shown with the teacher's wording that it obstructs "a sign, not the horoscope".

### 6.2 Readings from class rules
For each graha, from its house: collect the classes of that house; apply `ClassRules` using natural benefic/malefic status. Benefic = Jupiter, Venus, **well-associated Mercury**, waxing Moon; malefic = Saturn, Mars, Rahu, Ketu and the Sun (the teacher calls the Sun a malefic planet; slide 23 lists Saturn, Mars or Sun). The five-step checklist (slide 25) is shown per bhava: the bhava, its lord's position, planets in it, planets aspecting it, the karaka's placement — reusing the existing bhava analysis.

### 6.3 The four layers
1. **Graha + Bhava** — for each graha: the curated 3–5 points for its house, then (a) **dignity line** from `planetDignity()` mapped through `DignityEffect` ("exalted: karakatwas given in full force" … "debilitated: karakatwas diminished"), (b) **digbala** note where it applies, (c) class readings from §6.2. The Sun uses the slide text and the recording's extra points.
2. **Bhava + Bhava** — for each bhava lord placed in a bhava: blend of the two bhavas' significations, relationships and body areas from `BHAVA_INFO` (template), with lord-in-own-house / kendra / trikona / dusthana wording from the class rules, and the taught 2L-in-7 text verbatim.
3. **Graha + Rāśi** — graha in rāśi: tatwa, direction, varna, mode and the rāśi's karakatwas + dignity strength (taught example: Sun in Mesha — fiery, east, Kshatriya, courage, exalted → full potential).
4. **Graha + Graha** —
   * **Conjunction** (same rāśi): pair text from `GrahaPair` (taught: Jupiter + Mercury — intelligent, business-minded, good communicator); Sun + another graha adds the combustion note linked to the existing Combustion section.
   * **Aspect**: from the existing special-aspect computation; for each aspecting → aspected pair, the aspecting graha's qualities fall on the aspected graha's karakatwas (pair text + aspect sentence); Jupiter's aspect is flagged as stronger than its placement, as the page already does.

### 6.4 Daśā linking
Planet roles for the chart: Maraka lord (owns 2 or 7), Maraka occupant (sits in 2 or 7), **Badhakādhipati**, occupant of Badhaka sthāna, Dusthana lord (6/8/12), Trishadaya lord (3/6/11). A planet may hold several roles (e.g. Saturn for Simha Lagna owns 6th and 7th). Rahu and Ketu own nothing, so they carry occupant roles only.

From `buildDasha()` take the running Mahādaśā and Bhukti. Output: (a) a **roles table** for all nine grahas; (b) the running pair with each lord's roles and the matching slide wording; (c) a **watch-periods table** — every Bhukti in the next 10 years whose Mahādaśā or Bhukti lord holds a Maraka / Badhaka role, with dates; (d) role chips beside the rows of the existing bhukti tables. Tone follows the slides: Maraka = health disturbance or death-like suffering *if it operates before the promised time*; Badhaka = obstruction, health issues, suffering; Trishadaya = material success in the Mahādaśā. Indicative wording, no certainty claims.

## 7. UI

1. **Bhāvas (Houses)** nav group gains two sections: *Bhāva Analysis — 10 Classifications* (matrix, ten class tables, Badhaka, readings, five-step checklist) and *Bhāva Analysis — Prediction Layers* (four layers, per graha and per bhava, with status tags). The group matches by the title text "Bhāva Analysis", so no nav code changes.
2. **Aspect-based Graha + Graha** appears in the Prediction Layers section and links to the existing *Graha Drishti* section.
3. Tables use the site's `.rtable` styling, scroll inside their box on phones, and are kept whole on A4 print with three-letter rāśi names (the Ashtakavarga approach).
4. **Daśā–Bhukti tab.** The pane exists today — it is the first pill inside *Predictive & Remedies* — but the top-level strip (Summary · Charts · …) added on 2026-09-11 (commit `aee4d9e`) buried it one level down. Proposal: add a top-level **Daśā–Bhukti** nav button containing the Vimśottarī pane plus §6.4, and remove the pill so the print shows it once. (Alternative: keep the pill as well — see §11.)
5. Print order stays the report's section order; every new section prints.

## 8. Curated content policy

* **Method:** the teacher's own — blend graha karakatwas with bhava karakatwas. Each curated line must be traceable to a field in the workbook: the planet's `PLANET_PROFILE` (relationships, profession, personality, body parts, health, nature) and the bhava's `BHAVA_INFO` (significations, relatives, body areas). No outside rule is introduced silently; anything beyond the teacher's tables (standard digbala, for example) is listed in §11 and tagged.
* **Voice and size:** 3–5 short points per graha-in-bhava, in the same register as the Sun slides; both the favourable and the cautionary side, never fatalistic.
* **Review gate:** the 96 curated graha-in-bhava rows and 36 pair rows are authored into `Session23_Rules.xlsx` first and handed to the user to edit **before** they are wired into the page. Status stays `curated` until the teacher covers the graha, then flips to `taught`.
* The Sun's slide paragraphs read like a general write-up; they are kept as the slide text, with the recording's additional points alongside.

## 9. Testing and verification

* **Unit (Python, test-first):** class membership for all houses; Badhaka for all 12 Lagnas incl. the six spoken examples; roles for the oracle chart; `planetDignity` port equal to JS on the full grid; Vimśottarī dates equal to the JS engine for many birth dates; template rendering; every JSON row has a status.
* **Oracle:** the slides' chart reproduces each slide table (with the confirmed Mercury & Rahu correction).
* **Cross-implementation:** JS block (node) vs Python on ≥ 2,000 random charts; Excel (LibreOffice-recalculated) vs Python on ≥ 24 charts; text outputs compared exactly.
* **Browser end-to-end (headless Chromium, all network blocked so nothing reaches the Google Sheet logger):** generate real charts, read the new sections, check phone scroll, A4 print fit with no clipped or overlapping headers, no JS errors.
* **Regression:** render old vs new `index.html` with a frozen clock; after removing the new sections the report must be identical.
* **Mutation checks** on the JS and Python engines (off-by-one house arithmetic, swapped class houses, dropped role) must fail the suite.
* **Content checks:** no empty graha × bhava cell; every row has status and source note; no row quotes another planet's text.

## 10. Phasing (each phase is pushed to the work branch, reviewed and merged before the next starts)

1. **Classifications** — data workbook (classes, Badhaka), engine in JS/Python/Excel, the *10 Classifications* section, tests.
2. **Daśā linking and tab** — roles, running-period readout, watch periods, top-level Daśā–Bhukti tab.
3. **Prediction layers** — content review gate first (curated workbook handed over), then Graha + Bhava, Bhava + Bhava, Graha + Rāśi, Graha + Graha (conjunction and aspect), dignity and digbala lines.
4. *(Optional follow-up)* Update the Yoga Rules callout: on the recording the teacher says Sun + Mercury makes Budha-Āditya yoga and an intelligent child — the first named yoga she has taught, while the page says none have been taught yet.

## 11. Open points for the user (defaults in bold)

1. **"Well-associated Mercury" as a benefic:** Mercury counts as benefic unless it is conjunct Mars, Saturn, Rahu or Ketu (the Sun does not spoil it).
2. **Waxing Moon:** Shukla-paksha Moon is benefic, Krishna-paksha Moon is treated as malefic (existing tithi data).
3. **Digbala:** Sun 10th and Saturn 7th (taught); Mercury and Jupiter 1st, Moon and Venus 4th, Mars 10th (standard table, tagged as such).
4. **Daśā–Bhukti pill:** **move to the top-level strip and remove the pill** (alternative: keep both and accept the duplicate on print).
5. **Dasha linking set:** **Maraka and Badhaka as asked, plus Dusthana lords and the Trishadaya Mahādaśā rule**, because the same slides (19, 23) state them in the same terms.
6. **Rahu / Ketu in curated text:** included as grahas; roles in dasha linking as occupants only.
7. **Teacher's material in a public repo:** the data workbook holds the Session 23 slide text (as `index.html` already holds other sessions' material). Confirm that is acceptable, or keep the workbook out of the repo and build from a local copy.

## 12. Risks

* **Scale of curated content** (≈ 130 rows): mitigated by the review gate and the `status` tags; wiring waits for the user's edits.
* **Three engines drifting:** mitigated by one data source, generated blocks, and exact-output parity tests.
* **Reading the slides by eye:** every OCR doubt is in the `OCRNotes` sheet and the confirmed ones are resolved above; the user corrects the workbook directly and that version wins.
* **Dasha wording sounding fatalistic:** mitigated by quoting the slides' conditional phrasing ("if they operate before the time of death is promised") and the "indicative" label.
