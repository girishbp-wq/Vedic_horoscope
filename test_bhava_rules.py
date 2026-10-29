"""Unit tests for bhava_rules.py (python3 -m unittest -v test_bhava_rules).

Oracle: the example chart on the Session 23 slides — Simha Lagna; Moon Tula, Ketu Vrishchika,
Saturn Makara, Jupiter Kumbha, Mars Karka, Sun and Venus Mithuna, Mercury and Rahu Vrishabha.
Signs are 0-based (Mesha = 0)."""
import unittest

import bhava_rules as br

RULES = br.load_rules()
LAGNA = 4
SIGNS = {"Moon": 6, "Ketu": 7, "Saturn": 9, "Jupiter": 10, "Mars": 3, "Sun": 2, "Venus": 2,
         "Mercury": 1, "Rahu": 1}


def rows(table):
    return [(r["house"], r["planets"], r["lord"]) for r in table]


class HouseMaps(unittest.TestCase):
    def test_house_sign_and_lord(self):
        self.assertEqual([br.house_sign(LAGNA, h) for h in (1, 2, 12)], [4, 5, 3])
        self.assertEqual([br.house_lord(RULES, LAGNA, h) for h in range(1, 13)],
                         ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
                          "Mars", "Venus", "Mercury", "Moon"])

    def test_occupants_in_planet_order(self):
        occ = br.occupants(LAGNA, SIGNS)
        self.assertEqual(occ[10], ["Mercury", "Rahu"])
        self.assertEqual(occ[11], ["Sun", "Venus"])
        self.assertEqual(occ[1], [])

    def test_all_planets_in_one_house(self):
        crowded = {p: LAGNA for p in br.PLANET_ORDER}
        occ = br.occupants(LAGNA, crowded)
        self.assertEqual(occ[1], br.PLANET_ORDER)
        tables = br.classification_tables(RULES, LAGNA, crowded)
        self.assertEqual(rows(tables["Kendra"])[0], (1, br.PLANET_ORDER, "Sun"))
        self.assertTrue(all(r[1] == [] for r in rows(tables["Kendra"])[1:]))


class ClassTablesMatchTheSlides(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = br.classification_tables(RULES, LAGNA, SIGNS)

    def test_kendra_table_matches_slide(self):  # slide 5 (10th house planets: Mercury & Rahu, confirmed)
        self.assertEqual(rows(self.t["Kendra"]),
                         [(1, [], "Sun"), (4, ["Ketu"], "Mars"), (7, ["Jupiter"], "Saturn"),
                          (10, ["Mercury", "Rahu"], "Venus")])
        self.assertEqual([r["lord_house"] for r in self.t["Kendra"]], [11, 12, 6, 11])
        self.assertEqual([r["sign"] for r in self.t["Kendra"]], [4, 7, 10, 1])

    def test_trikona_table_matches_slide(self):  # slide 8
        self.assertEqual(rows(self.t["Trikona"]), [(1, [], "Sun"), (5, [], "Jupiter"), (9, [], "Mars")])

    def test_panapara_table_matches_slide(self):  # slide 11
        self.assertEqual(rows(self.t["Panapara"]),
                         [(2, [], "Mercury"), (5, [], "Jupiter"), (8, [], "Jupiter"),
                          (11, ["Sun", "Venus"], "Mercury")])

    def test_apoklima_table_matches_slide(self):  # slide 13 lords + chart occupants
        self.assertEqual(rows(self.t["Apoklima"]),
                         [(3, ["Moon"], "Venus"), (6, ["Saturn"], "Saturn"), (9, [], "Mars"), (12, ["Mars"], "Moon")])

    def test_upachaya_table_matches_slide(self):  # slide 15
        self.assertEqual(rows(self.t["Upachaya"]),
                         [(3, ["Moon"], "Venus"), (6, ["Saturn"], "Saturn"),
                          (10, ["Mercury", "Rahu"], "Venus"), (11, ["Sun", "Venus"], "Mercury")])

    def test_apachaya_is_1_2_4_7_8(self):  # slide 16, confirmed
        self.assertEqual([r["house"] for r in self.t["Apachaya"]], [1, 2, 4, 7, 8])
        self.assertEqual(rows(self.t["Apachaya"])[3], (7, ["Jupiter"], "Saturn"))

    def test_maraka_table_matches_slide(self):  # slide 18
        self.assertEqual(rows(self.t["Maraka"]), [(2, [], "Mercury"), (7, ["Jupiter"], "Saturn")])

    def test_dusthana_table_matches_slide(self):  # slide 20
        self.assertEqual(rows(self.t["Dusthana"]),
                         [(6, ["Saturn"], "Saturn"), (8, [], "Jupiter"), (12, ["Mars"], "Moon")])

    def test_trishadaya_table_matches_slide(self):  # slide 24 lords
        self.assertEqual([r["lord"] for r in self.t["Trishadaya"]], ["Venus", "Saturn", "Mercury"])
        self.assertEqual([r["house"] for r in self.t["Trishadaya"]], [3, 6, 11])

    def test_every_class_has_a_table(self):
        self.assertEqual(list(self.t), ["Kendra", "Trikona", "Panapara", "Apoklima", "Upachaya", "Apachaya",
                                        "Maraka", "Dusthana", "Badhaka", "Trishadaya"])


class Badhaka(unittest.TestCase):
    def test_badhaka_oracle(self):  # slide 22
        b = br.badhaka(RULES, LAGNA, SIGNS)
        self.assertEqual((b["mode"], b["house"], b["sign"], b["lord"], b["occupants"]),
                         ("Sthira", 9, 0, "Mars", []))

    def test_badhaka_table_has_the_one_house(self):
        t = br.classification_tables(RULES, LAGNA, SIGNS)["Badhaka"]
        self.assertEqual(rows(t), [(9, [], "Mars")])

    def test_badhaka_for_every_lagna_and_the_six_spoken_examples(self):
        chara, sthira, dwi = [0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]
        for lg in range(12):
            want = 11 if lg in chara else 9 if lg in sthira else 7
            self.assertEqual(br.badhaka(RULES, lg, SIGNS)["house"], want, lg)
        # (lagna, badhaka sign, badhakadhipati) spoken on the recording / shown on slide 22
        for lg, sign, lord in [(0, 10, "Saturn"), (6, 4, "Sun"), (8, 2, "Mercury"), (10, 6, "Venus"),
                               (3, 1, "Venus"), (4, 0, "Mars")]:
            b = br.badhaka(RULES, lg, SIGNS)
            self.assertEqual((b["sign"], b["lord"]), (sign, lord), lg)


class Matrix(unittest.TestCase):
    def test_matrix_belongs_to_column(self):
        m = {r["house"]: r["classes"] for r in br.house_class_matrix(RULES, LAGNA)}
        self.assertEqual(m[1], ["Kendra", "Trikona", "Apachaya"])
        self.assertEqual(m[6], ["Apoklima", "Upachaya", "Dusthana", "Trishadaya"])
        self.assertEqual(m[9], ["Trikona", "Apoklima", "Badhaka"])
        self.assertEqual(m[2], ["Panapara", "Apachaya", "Maraka"])
        self.assertEqual(len(m), 12)

    def test_class_houses(self):
        self.assertEqual(br.class_houses(RULES, "Kendra", LAGNA), [1, 4, 7, 10])
        self.assertEqual(br.class_houses(RULES, "Badhaka", 0), [11])
        self.assertEqual(br.class_houses(RULES, "Badhaka", 2), [7])


class NatureAndReadings(unittest.TestCase):
    def test_natures_follow_session_26(self):
        self.assertEqual({p: br.nature(p) for p in br.PLANET_ORDER},
                         {"Sun": "mild malefic", "Moon": "benefic", "Mars": "malefic", "Mercury": "benefic",
                          "Jupiter": "benefic", "Venus": "benefic", "Saturn": "malefic", "Rahu": "malefic", "Ketu": "malefic"})
        self.assertEqual(br.nature_class("Sun"), "malefic")
        self.assertEqual(br.nature_class("Moon"), "benefic")

    def test_mercury_with_saturn_stays_benefic(self):
        with_saturn = dict(SIGNS, Mercury=10, Saturn=10)              # both in the 7th (Kumbha) for Simha Lagna
        merc = next(r for r in br.class_readings(RULES, LAGNA, with_saturn) if r["planet"] == "Mercury")
        self.assertIn("smaller efforts", " | ".join(merc["texts"]))      # the benefic Kendra rule
        self.assertNotIn("do not do well", " | ".join(merc["texts"]))

    def test_waning_moon_stays_benefic(self):
        in_kendra = dict(SIGNS, Moon=1)                               # Moon in the 10th (Vrishabha)
        moon = next(r for r in br.class_readings(RULES, LAGNA, in_kendra) if r["planet"] == "Moon")
        self.assertIn("smaller efforts", " | ".join(moon["texts"]))
        g = br.graha_bhava(RULES, LAGNA, in_kendra, "Moon", 10.0, False)
        self.assertEqual(g["nature"], "benefic")
        self.assertNotIn("struggle", " | ".join(g["class_texts"]))

    def test_sun_takes_malefic_rules_marked_mild(self):
        sixth = dict(SIGNS, Sun=9)                                    # Sun in the 6th (Makara)
        sun = next(r for r in br.class_readings(RULES, LAGNA, sixth) if r["planet"] == "Sun")
        # the Sun in Makara is in an enemy's sign, so weak: the S25 'not weak' line is left out (spec §6.2.5)
        malefic = [r["text"] for c in sun["classes"] for r in RULES["class_rules"]
                   if r["class"] == c and r["applies"] == "malefic" and 6 not in r["exclude_houses"] and r["when"] != "not weak"]
        self.assertTrue(malefic)
        self.assertFalse([t for t in sun["texts"] if "give good results" in t])
        for t in malefic:
            self.assertIn("(mild) " + t, sun["texts"])
        anys = [t for t in sun["texts"] if not t.startswith("(mild) ")]
        self.assertTrue(anys)                                         # rules for any planet are not marked

    def test_moon_strength_line(self):
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Moon", 10.0, False)["moon_strength"], "Krishna (waning) — weaker")
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Moon", 10.0, True)["moon_strength"], "Shukla (waxing) — stronger")
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Jupiter", None, True)["moon_strength"], "")
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Jupiter", None, True)["nature"], "benefic")
        self.assertEqual(br.moon_strength(None), "")

    def test_moon_waxing_at_the_purnima_boundary(self):
        self.assertTrue(br.moon_waxing(10.0, 10.0))          # separation 0 -> tithi 1
        self.assertTrue(br.moon_waxing(0.0, 179.99))         # tithi 15, Purnima
        self.assertFalse(br.moon_waxing(0.0, 180.0))         # tithi 16, Krishna paksha
        self.assertFalse(br.moon_waxing(100.0, 99.0))        # separation 359 -> tithi 30

    def test_class_readings_rules(self):
        reads = {r["planet"]: r for r in br.class_readings(RULES, LAGNA, SIGNS)}
        jup = " | ".join(reads["Jupiter"]["texts"])               # Jupiter in the 7th: Kendra + Apachaya + Maraka
        self.assertIn("smaller efforts", jup)
        self.assertIn("highly active", jup)
        self.assertIn("lose their strength through time", jup)
        self.assertNotIn("do not do well", jup)                      # that line is for natural malefics
        sat = " | ".join(reads["Saturn"]["texts"])                   # Saturn in the 6th: Upachaya malefic
        self.assertIn("good results", sat)
        self.assertEqual(reads["Saturn"]["house"], 6)
        self.assertEqual(reads["Saturn"]["classes"], ["Apoklima", "Upachaya", "Dusthana", "Trishadaya"])
        in7 = dict(SIGNS, Saturn=10)                                 # Saturn in the 7th: Apachaya malefic
        self.assertIn("do not do well", " | ".join(
            next(r for r in br.class_readings(RULES, LAGNA, in7) if r["planet"] == "Saturn")["texts"]))

    def test_ninth_house_is_the_apoklima_exception(self):
        nine = dict(SIGNS, Venus=0)                                  # Venus in the 9th (Mesha for Simha Lagna)
        txt = " | ".join(next(r for r in br.class_readings(RULES, LAGNA, nine) if r["planet"] == "Venus")["texts"])
        self.assertIn("exception", txt)
        self.assertNotIn("considered weak", txt)
        weak = " | ".join(next(r for r in br.class_readings(RULES, LAGNA, SIGNS) if r["planet"] == "Moon")["texts"])
        self.assertIn("considered weak", weak)                       # Moon in the 3rd


class Roles(unittest.TestCase):
    def test_roles_oracle(self):
        self.assertEqual(br.planet_roles(RULES, LAGNA, SIGNS), {
            "Sun": [], "Moon": ["Dusthana lord"], "Mars": ["Badhakadhipati"],
            "Mercury": ["Maraka lord", "Trishadaya lord"], "Jupiter": ["Maraka occupant", "Dusthana lord"],
            "Venus": ["Trishadaya lord"], "Saturn": ["Maraka lord", "Dusthana lord", "Trishadaya lord"],
            "Rahu": [], "Ketu": []})

    def test_roles_for_a_planet_with_two_houses(self):
        saturn = br.planet_roles(RULES, LAGNA, SIGNS)["Saturn"]      # owns the 6th and the 7th for Simha Lagna
        self.assertEqual(saturn.count("Maraka lord"), 1)
        self.assertEqual(saturn.count("Dusthana lord"), 1)
        self.assertEqual(saturn, sorted(saturn, key=br.ROLE_ORDER.index))

    def test_rahu_ketu_occupant_roles_only(self):
        sg = dict(SIGNS, Rahu=5, Ketu=0)                              # Rahu in the 2nd, Ketu in the Badhaka house (9th)
        roles = br.planet_roles(RULES, LAGNA, sg)
        self.assertEqual(roles["Rahu"], ["Maraka occupant"])
        self.assertEqual(roles["Ketu"], ["Badhaka occupant"])


class Digbala(unittest.TestCase):
    def test_digbala_taught_cases(self):
        self.assertEqual(br.digbala(RULES, "Sun", 10), "strong")
        self.assertEqual(br.digbala(RULES, "Sun", 4), "lost")
        self.assertEqual(br.digbala(RULES, "Saturn", 7), "strong")
        self.assertEqual(br.digbala(RULES, "Moon", 4), "strong")
        self.assertEqual(br.digbala(RULES, "Jupiter", 7), "lost")
        self.assertIsNone(br.digbala(RULES, "Venus", 2))
        self.assertIsNone(br.digbala(RULES, "Rahu", 5))


import json as _json
import os as _os
import shutil as _shutil
import subprocess as _subprocess


def _playwright():
    npm = _shutil.which("npm")
    if not (npm and _shutil.which("node")):
        return None
    root = _subprocess.run([npm, "root", "-g"], capture_output=True, text=True).stdout.strip()
    pw = _os.path.join(root, "playwright")
    return pw if _os.path.isdir(pw) and _os.path.isdir(_os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")) else None


GRID_JS = r"""
const { chromium } = require(process.env.PW_MODULE);
(async () => {
  const b = await chromium.launch({headless: true});
  const ctx = await b.newContext();
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const p = await ctx.newPage();
  await p.goto('file://' + process.argv[1]);
  const out = await p.evaluate(() => {
    const planets = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"], rows = [];
    for (const pl of planets) for (let n = 1; n <= 12; n++) for (const deg of [null, ...Array(30).keys()]) {
      const d = planetDignity(pl, n, deg === null ? undefined : deg);
      rows.push([pl, n - 1, deg, d.label, d.flag, d.bala, d.note]);
    }
    return rows;
  });
  console.log(JSON.stringify(out));
  await b.close();
})();
"""


@unittest.skipUnless(_playwright(), "playwright + chromium needed to run the page's planetDignity")
class DignityPort(unittest.TestCase):
    def test_dignity_equals_the_page_on_the_full_grid(self):
        env = dict(_os.environ, PW_MODULE=_playwright(), PLAYWRIGHT_BROWSERS_PATH="/opt/pw-browsers")
        index = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "index.html")
        p = _subprocess.run(["node", "-e", GRID_JS, index], capture_output=True, text=True, timeout=180, env=env)
        self.assertEqual(p.returncode, 0, p.stderr[-600:])
        rows = _json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(len(rows), 9 * 12 * 31)
        for planet, sign, deg, label, flag, bala, note in rows:
            got = br.dignity(RULES, planet, sign, deg)
            self.assertEqual((got["label"], got["flag"], got["bala"], got["note"]), (label, flag, bala, note),
                             (planet, sign, deg))

    def test_known_dignities(self):
        self.assertEqual(br.dignity(RULES, "Sun", 0, 10)["label"], "Deep Exalted")      # Sun, Mesha 10
        self.assertEqual(br.dignity(RULES, "Sun", 0, 3)["label"], "Exalted")
        self.assertEqual(br.dignity(RULES, "Sun", 6, 23)["label"], "Debilitated")       # slide Q&A: Sun in Tula 23 deg
        self.assertEqual(br.dignity(RULES, "Sun", 4, 5)["label"], "Own (Moolatrikona)")
        self.assertEqual(br.dignity(RULES, "Sun", 4, 25)["label"], "Own House")


import datetime as _dt
import random as _random

ORACLE_ROLES = {
    "Sun": [], "Moon": ["Dusthana lord"], "Mars": ["Badhakadhipati"],
    "Mercury": ["Maraka lord", "Trishadaya lord"], "Jupiter": ["Maraka occupant", "Dusthana lord"],
    "Venus": ["Trishadaya lord"], "Saturn": ["Maraka lord", "Dusthana lord", "Trishadaya lord"],
    "Rahu": [], "Ketu": []}
BIRTH = _dt.datetime(1990, 5, 17, 6, 30)
MOON_LON = 190.0                       # Moon in Tula, as in the slide chart
NOW = _dt.datetime(2026, 10, 8, 12, 0)

DASHA_JS = r"""
const { chromium } = require(process.env.PW_MODULE);
(async () => {
  const cases = JSON.parse(process.argv[2]);
  const b = await chromium.launch({headless: true});
  const ctx = await b.newContext({timezoneId: 'UTC'});
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const p = await ctx.newPage();
  await p.goto('file://' + process.argv[1]);
  const out = await p.evaluate(cases => cases.map(([lon, dob, tob]) => {
    const D = buildDasha(lon, dob, tob);
    return D.timeline.map(t => [t.lord, t.start.getTime(), t.end.getTime(),
                                t.bhuktis.map(x => [x.lord, x.start.getTime(), x.end.getTime()])]);
  }), cases);
  console.log(JSON.stringify(out));
  await b.close();
})();
"""


def _ms(d):
    return d.replace(tzinfo=_dt.timezone.utc).timestamp() * 1000


class Vimshottari(unittest.TestCase):
    def test_structure_and_lengths(self):
        d = br.vimshottari(RULES, MOON_LON, BIRTH, NOW)
        self.assertEqual([t["lord"] for t in d["timeline"]].count("Mercury"), 1)
        self.assertEqual(len(d["timeline"]), 9)
        self.assertTrue(all(len(t["bhuktis"]) == 9 for t in d["timeline"]))
        years = [(t["end"] - t["start"]).total_seconds() / (365.25 * 86400) for t in d["timeline"]]
        self.assertEqual([round(y, 6) for y in years],
                         [RULES["reference"]["VYEARS"][t["lord"]] for t in d["timeline"]])
        first = d["timeline"][0]
        self.assertEqual(first["bhuktis"][0]["lord"], first["lord"])      # a Mahādaśā opens with its own Bhukti
        self.assertEqual(first["bhuktis"][0]["start"], first["start"])
        self.assertAlmostEqual((first["bhuktis"][-1]["end"] - first["end"]).total_seconds(), 0, delta=1)

    @unittest.skipUnless(_playwright(), "playwright + chromium needed to run the page's buildDasha")
    def test_vimshottari_equals_the_page(self):
        rnd = _random.Random(23)
        cases = []
        for _ in range(25):
            b = _dt.datetime(rnd.randint(1930, 2015), rnd.randint(1, 12), rnd.randint(1, 28),
                             rnd.randint(0, 23), rnd.randint(0, 59), 0)
            cases.append((round(rnd.uniform(0, 360), 4), b))
        arg = _json.dumps([[lon, b.strftime("%Y-%m-%d"), b.strftime("%H:%M:%S")] for lon, b in cases])
        env = dict(_os.environ, PW_MODULE=_playwright(), PLAYWRIGHT_BROWSERS_PATH="/opt/pw-browsers")
        index = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "index.html")
        p = _subprocess.run(["node", "-e", DASHA_JS, index, arg], capture_output=True, text=True,
                            timeout=180, env=env)
        self.assertEqual(p.returncode, 0, p.stderr[-600:])
        page = _json.loads(p.stdout.strip().splitlines()[-1])
        for (lon, birth), timeline in zip(cases, page):
            mine = br.vimshottari(RULES, lon, birth, NOW)["timeline"]
            self.assertEqual([t["lord"] for t in mine], [t[0] for t in timeline], (lon, birth))
            for t, (lord, s, e, bh) in zip(mine, timeline):
                self.assertAlmostEqual(_ms(t["start"]), s, delta=1000, msg=(lon, birth, lord))
                self.assertAlmostEqual(_ms(t["end"]), e, delta=1000, msg=(lon, birth, lord))
                self.assertEqual([x["lord"] for x in t["bhuktis"]], [x[0] for x in bh])
                for x, (_, bs, be) in zip(t["bhuktis"], bh):
                    self.assertAlmostEqual(_ms(x["start"]), bs, delta=1000)
                    self.assertAlmostEqual(_ms(x["end"]), be, delta=1000)

    def test_moon_exactly_on_a_nakshatra_boundary(self):
        # 40° is the first point of Rohini (Moon's star); float floor-division put it in Krittika
        names = [n for n, _ in RULES["reference"]["NAKSHATRAS"]]
        for k in range(0, 27, 3):
            lon = k * 40 / 3
            d = br.vimshottari(RULES, lon, BIRTH, NOW)
            self.assertEqual(d["nak_index"], k + 1, (lon, names[k]))
            self.assertEqual(d["nak_lord"], RULES["reference"]["NAKSHATRAS"][k][1])
        self.assertTrue(br.moon_waxing(0.0, 168.0))           # tithi 15 (Purnima) is Shukla
        self.assertFalse(br.moon_waxing(0.0, 180.0))          # tithi 16 starts Krishna

    def test_running_pair_at_boundaries(self):
        base = br.vimshottari(RULES, MOON_LON, BIRTH, NOW)["timeline"]
        edge = base[2]["start"]                                          # exactly on a Mahādaśā start
        d = br.vimshottari(RULES, MOON_LON, BIRTH, edge)
        self.assertEqual(d["cur_maha"]["lord"], base[2]["lord"])
        self.assertEqual(d["cur_bhukti"]["lord"], base[2]["lord"])       # ... and its first Bhukti
        d = br.vimshottari(RULES, MOON_LON, BIRTH, base[2]["end"])        # the end instant belongs to the next
        self.assertEqual(d["cur_maha"]["lord"], base[3]["lord"])
        for now in (BIRTH - _dt.timedelta(days=36525 * 2), BIRTH + _dt.timedelta(days=365.25 * 130)):
            d = br.vimshottari(RULES, MOON_LON, BIRTH, now)              # outside the 120-year span
            self.assertIn(d["cur_maha"]["lord"], br.PLANET_ORDER)
            self.assertIn(d["cur_bhukti"], d["cur_maha"]["bhuktis"])
            self.assertFalse(d["running"])                               # ... and says no period is running
        self.assertTrue(br.vimshottari(RULES, MOON_LON, BIRTH, NOW)["running"])

    def test_current_pair_is_the_period_containing_now(self):
        d = br.vimshottari(RULES, MOON_LON, BIRTH, NOW)
        self.assertTrue(d["cur_maha"]["start"] <= NOW < d["cur_maha"]["end"])
        self.assertTrue(d["cur_bhukti"]["start"] <= NOW < d["cur_bhukti"]["end"])


class PartialCharts(unittest.TestCase):
    def test_bhava_bhava_skips_lords_whose_sign_is_not_given(self):
        rows = br.bhava_bhava(RULES, br.context(LAGNA, {"Sun": 4}))                   # only the Sun is known
        self.assertEqual({r["lord"] for r in rows}, {"Sun"})
        self.assertEqual(len(rows), 1)


class DashaLinking(unittest.TestCase):
    def test_dasha_role_text_uses_the_slide_wording(self):
        pair = {"cur_maha": {"lord": "Saturn"}, "cur_bhukti": {"lord": "Venus"}}
        run = br.running_roles(RULES, pair, ORACLE_ROLES)
        self.assertEqual(run["maha"]["lord"], "Saturn")
        self.assertEqual(run["maha"]["roles"], ["Maraka lord", "Dusthana lord", "Trishadaya lord"])
        self.assertTrue(any("before the time of death is promised" in t for t in run["maha"]["text"]))
        self.assertEqual(run["bhukti"]["roles"], [])                      # Trishadaya is taught as a Mahādaśā effect
        self.assertEqual(run["bhukti"]["text"], [])

    def test_watch_periods_flag_maraka_and_badhaka(self):
        d = br.vimshottari(RULES, MOON_LON, BIRTH, NOW)
        watch = br.watch_periods(RULES, d, ORACLE_ROLES, NOW, years=10)
        window_end = NOW + _dt.timedelta(days=365.25 * 10)
        want = {}
        for t in d["timeline"]:
            for b in t["bhuktis"]:
                if b["end"] > NOW and b["start"] < window_end:
                    mine = set(ORACLE_ROLES[t["lord"]]) | (set(ORACLE_ROLES[b["lord"]]) - {"Trishadaya lord"})
                    if mine:
                        want[(t["lord"], b["lord"])] = [r for r in br.ROLE_ORDER if r in mine]
        self.assertEqual({(w["maha"], w["bhukti"]): w["roles"] for w in watch}, want)
        self.assertTrue(want)
        for w in watch:
            self.assertEqual(w["kind"], "favourable" if w["roles"] == ["Trishadaya lord"] else "caution", w)
            self.assertLess(w["start"], w["end"])
        self.assertEqual([w["start"] for w in watch], sorted(w["start"] for w in watch))
        mars = [w for w in watch if "Mars" in (w["maha"], w["bhukti"])]
        self.assertTrue(all("Badhakadhipati" in w["roles"] for w in mars))

    def test_trishadaya_mahadasha_periods_are_favourable(self):
        d = br.vimshottari(RULES, MOON_LON, BIRTH, NOW)
        venus = br.watch_periods(RULES, d, ORACLE_ROLES, d["timeline"][0]["start"], years=125)
        vv = [w for w in venus if w["maha"] == "Venus" and w["bhukti"] in ("Venus", "Sun", "Rahu", "Ketu")]
        self.assertTrue(vv)
        self.assertTrue(all(w["kind"] == "favourable" and w["roles"] == ["Trishadaya lord"] for w in vv))
        moon_under_venus = [w for w in venus if (w["maha"], w["bhukti"]) == ("Venus", "Moon")]
        self.assertEqual([w["kind"] for w in moon_under_venus], ["caution"])
        self.assertEqual(moon_under_venus[0]["roles"], ["Dusthana lord", "Trishadaya lord"])


MEENA = 11


class PredictionLayers(unittest.TestCase):
    def test_taught_examples_are_verbatim(self):
        # layer 2: second lord (Mercury for Simha Lagna) in the 7th (Kumbha)
        in7 = dict(SIGNS, Mercury=10)
        row = next(r for r in br.bhava_bhava(RULES, br.context(LAGNA, in7)) if (r["lord_of"], r["sits_in"]) == (2, 7))
        want = next(x for x in RULES["bhava_lord_in"] if (x["lord_of"], x["sits_in"]) == (2, 7))
        self.assertEqual((row["status"], row["text"]), ("taught", want["text"]))
        # layer 4: Jupiter and Mercury in one sign
        both = dict(SIGNS, Jupiter=1)
        pair = next(c for c in br.graha_graha(RULES, LAGNA, both)["conjunctions"] if (c["a"], c["b"]) == ("Mercury", "Jupiter"))
        taught = next(x for x in RULES["graha_pair"] if (x["a"], x["b"]) == ("Mercury", "Jupiter"))
        self.assertEqual((pair["status"], pair["text"]), ("taught", taught["conjunction"]))
        # layer 3: Sun in Mesha
        sun = next(r for r in br.graha_rashi(RULES, LAGNA, dict(SIGNS, Sun=0), {}) if r["planet"] == "Sun")
        self.assertEqual(sun["status"], "taught")
        self.assertIn("exalted", sun["text"])
        self.assertIn("full potential", sun["text"])

    def test_dignity_line_for_sun_in_meena_lagna(self):
        exalted = br.graha_bhava(RULES, MEENA, dict(SIGNS, Sun=0), "Sun", None, True)       # Mesha is the 2nd
        self.assertEqual(exalted["house"], 2)
        self.assertTrue(exalted["dignity_line"].startswith("Exalted"))
        self.assertIn("full force", exalted["dignity_line"])
        weak = br.graha_bhava(RULES, MEENA, dict(SIGNS, Sun=6), "Sun", None, True)          # Tula is the 8th
        self.assertEqual(weak["house"], 8)
        self.assertTrue(weak["dignity_line"].startswith("Debilitated"))
        self.assertIn("diminished", weak["dignity_line"])
        deep = br.graha_bhava(RULES, MEENA, dict(SIGNS, Sun=0), "Sun", 10.4, True)
        self.assertTrue(deep["dignity_line"].startswith("Deep Exalted"))

    def test_graha_bhava_uses_the_cell_digbala_and_class_texts(self):
        tenth = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Sun=1), "Sun", None, True)         # Vrishabha = 10th
        self.assertEqual((tenth["house"], tenth["status"]), (10, "taught"))
        self.assertIn("gains directional strength", tenth["digbala_line"])
        self.assertEqual(tenth["digbala_status"], "taught")
        self.assertTrue(tenth["points"] and tenth["extra"])
        fourth = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Sun=7), "Sun", None, True)
        self.assertIn("loses directional strength", fourth["digbala_line"])
        jup = br.graha_bhava(RULES, LAGNA, SIGNS, "Jupiter", None, True)                    # 7th, Kendra (S24 p.8)
        self.assertEqual((jup["house"], jup["status"]), (7, "taught"))
        self.assertTrue(jup["points"][0].strip())
        self.assertEqual(jup["classes"], ["Kendra", "Apachaya", "Maraka"])
        self.assertEqual(jup["class_texts"], next(r for r in br.class_readings(RULES, LAGNA, SIGNS)
                                                    if r["planet"] == "Jupiter")["texts"])
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Venus", None, True)["digbala_line"], "")

    def test_aspect_pairs_for_the_oracle_chart(self):
        got = [(a["by"], a["to"], a["house_aspect"]) for a in br.graha_graha(RULES, LAGNA, SIGNS)["aspects"]]
        self.assertEqual(got, [
            ("Mars", "Moon", 4), ("Mars", "Saturn", 7), ("Mars", "Jupiter", 8), ("Mercury", "Ketu", 7),
            ("Jupiter", "Sun", 5), ("Jupiter", "Venus", 5), ("Jupiter", "Moon", 9), ("Saturn", "Mars", 7),
            ("Saturn", "Moon", 10), ("Rahu", "Saturn", 9), ("Ketu", "Mars", 9), ("Ketu", "Moon", 12)])
        texts = {(a["by"], a["to"]): a["text"] for a in br.graha_graha(RULES, LAGNA, SIGNS)["aspects"]}
        # the nodes count anti-clockwise (teacher: 2nd, 5th, 9th): forward 9th is their 5th, forward 12th their 2nd
        self.assertTrue(texts[("Ketu", "Mars")].startswith("Ketu's 5th (anti-clockwise) aspect falls on Mars"))
        self.assertTrue(texts[("Ketu", "Moon")].startswith("Ketu's 2nd (anti-clockwise) aspect falls on Moon"))
        self.assertTrue(texts[("Jupiter", "Moon")].startswith("Jupiter's 9th aspect falls on Moon"))
        flags = {a["by"]: a["jupiter_flag"] for a in br.graha_graha(RULES, LAGNA, SIGNS)["aspects"]}
        self.assertEqual([k for k, v in flags.items() if v], ["Jupiter"])

    def test_oracle_conjunctions(self):
        conj = br.graha_graha(RULES, LAGNA, SIGNS)["conjunctions"]
        self.assertEqual([(c["a"], c["b"], c["house"]) for c in conj], [("Sun", "Venus", 11), ("Mercury", "Rahu", 10)])
        self.assertTrue(all(c["text"] and c["status"] == "curated" for c in conj))

    def test_combustion_note_only_for_a_close_sun_conjunction(self):
        unknown = br.graha_graha(RULES, LAGNA, SIGNS)["conjunctions"][0]
        self.assertIsNone(unknown["combust"])
        near = br.graha_graha(RULES, LAGNA, SIGNS, {"Sun": 10.0, "Venus": 14.9})["conjunctions"][0]
        self.assertTrue(near["combust"])
        self.assertIn(RULES["reference"]["PLANET_PROFILE"]["Venus"]["Combustion Effect"], near["combust_note"])
        far = br.graha_graha(RULES, LAGNA, SIGNS, {"Sun": 10.0, "Venus": 15.1})["conjunctions"][0]
        self.assertFalse(far["combust"])
        self.assertEqual(far["combust_note"], "")
        nodes = br.graha_graha(RULES, LAGNA, dict(SIGNS, Rahu=2), {"Sun": 10.0, "Rahu": 11.0})["conjunctions"]
        self.assertFalse(next(c for c in nodes if (c["a"], c["b"]) == ("Sun", "Rahu"))["combust"])

    def test_five_step_for_the_seventh_house(self):
        f = br.five_step(RULES, LAGNA, SIGNS, 7)
        self.assertEqual((f["house"], f["sign"], f["lord"], f["lord_house"]), (7, 10, "Saturn", 6))
        self.assertEqual(f["occupants"], ["Jupiter"])
        self.assertEqual([(a["by"], a["house_aspect"], a["aspect"]) for a in f["aspecting"]], [("Mars", 8, "8th")])
        self.assertIn("transformation", f["aspecting"][0]["meanings"][0])
        self.assertEqual(f["karakas"], [{"planet": "Venus", "house": 11}])
        self.assertIn("Spouse", f["significations"])

    def test_bhava_bhava_blends_and_marks_own_house(self):
        rows = br.bhava_bhava(RULES, br.context(LAGNA, SIGNS))
        # Venus (10th lord) in Mithuna and Mercury (11th lord) in Vrishabha: one Parivartana entry under the 10th
        self.assertEqual([r["lord_of"] for r in rows], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        self.assertEqual(next(r for r in rows if r["lord_of"] == 10)["exchange"], 11)
        mars = next(r for r in rows if r["lord_of"] == 4)                    # Mars owns the 4th, sits in the 12th
        self.assertEqual((mars["lord"], mars["sits_in"], mars["status"]), ("Mars", 12, "blend"))
        self.assertIn("Dusthana", mars["placement_line"])
        self.assertIn("A difficult placement.", mars["placement_line"])
        self.assertIn(RULES["reference"]["BHAVA_INFO"]["4"]["sig"].rstrip("."), mars["text"])
        self.assertIn(RULES["reference"]["BHAVA_INFO"]["12"]["sig"].rstrip("."), mars["text"])
        own = next(r for r in br.bhava_bhava(RULES, br.context(LAGNA, dict(SIGNS, Jupiter=8))) if r["lord_of"] == 5)
        self.assertEqual((own["sits_in"], own["status"]), (5, "blend"))      # the 5th lord in the 5th is not taught
        self.assertIn("own bhava", own["placement_line"])

    def test_graha_rashi_blends_rashi_fields_and_dignity(self):
        moon = next(r for r in br.graha_rashi(RULES, LAGNA, dict(SIGNS, Moon=8), {"Moon": 5.0}) if r["planet"] == "Moon")
        tula = RULES["reference"]["RASHI"][8]                                 # Dhanu: Moon there is not taught
        self.assertEqual((moon["tatwa"], moon["direction"], moon["varna"], moon["mode"]),
                         (tula["tatwa"], tula["direction"], tula["varna"], tula["mode"]))
        self.assertEqual(moon["status"], "blend")
        self.assertEqual(moon["dignity"], "Neutral House")                   # Dhanu is Jupiter's; Moon-Jupiter are neutral
        self.assertTrue(moon["strength_line"].startswith("Neutral House"))
        self.assertIn(tula["sanskrit"], moon["text"])

    def test_moon_in_tula_is_taught(self):
        moon = next(r for r in br.graha_rashi(RULES, LAGNA, SIGNS, {"Moon": 5.0}) if r["planet"] == "Moon")
        self.assertEqual(moon["status"], "taught")                          # S23-2024 p.11: Tula, balance
        self.assertIn("balance", moon["text"])

    def test_node_outside_exaltation_has_no_rulership(self):
        # Rāhu and Ketu own no rāśi: no "Own House", no sthāna-bala percentage, no dignity line
        third = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Rahu=6), "Rahu", None, True)           # Tula, the 3rd
        self.assertEqual(third["dignity"], {"label": "Node (no rulership)", "flag": "node", "bala": None,
                                            "note": "a node owns no rāśi — it gives the results of the sign's lord"})
        self.assertEqual((third["dignity_line"], third["dignity_status"]), ("", None))
        for s in range(12):
            for node in ("Rahu", "Ketu"):
                self.assertNotEqual(br.dignity(RULES, node, s, 15.0)["label"], "Own House")
        exalted = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Rahu=1), "Rahu", None, True)          # Vrishabha: exalted
        self.assertEqual((exalted["dignity"]["label"], exalted["dignity_status"]), ("Exalted", "taught"))
        sun = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Sun=4), "Sun", 25.0, True)                 # own sign, outside MT
        self.assertEqual((sun["dignity"]["label"], sun["dignity_status"]), ("Own House", "taught"))

    def test_every_status_tag_present(self):
        chart = dict(SIGNS, Mercury=10, Sun=0, Jupiter=1, Moon=7)
        seen = set()
        for p in br.PLANET_ORDER:
            g = br.graha_bhava(RULES, LAGNA, chart, p, None, True)
            seen |= {g["status"], g["digbala_status"], g["dignity_status"]}
        seen |= {r["status"] for r in br.bhava_bhava(RULES, br.context(LAGNA, chart))}
        seen |= {r["status"] for r in br.graha_rashi(RULES, LAGNA, chart, {})}
        gg = br.graha_graha(RULES, LAGNA, chart)
        seen |= {c["status"] for c in gg["conjunctions"]} | {a["status"] for a in gg["aspects"]}
        seen.discard(None)
        self.assertTrue({"taught", "curated", "blend", "standard"} <= seen, seen)
        self.assertLessEqual(seen, {"taught", "curated", "blend", "standard"})


if __name__ == "__main__":
    unittest.main()


class Helpers(unittest.TestCase):
    """Sessions 24-27 helpers: chart context, combustion, affliction (R5), strength (R3), aspects, sign lines."""

    def ctx(self, signs, degs=None, **kw):
        return br.context(LAGNA, signs, degs or {}, **kw)

    def test_context_keys_and_defaults(self):
        c = self.ctx(SIGNS)
        self.assertEqual(sorted(c), sorted(["lagna", "signs", "degs", "waxing", "retro", "gender", "age", "maha", "bhukti"]))
        self.assertEqual((c["degs"], c["retro"], c["gender"], c["age"], c["maha"]), ({}, {}, None, None, None))

    def test_gender_other_counts_as_not_filled(self):
        self.assertIsNone(self.ctx(SIGNS, gender="Other")["gender"])
        self.assertIsNone(self.ctx(SIGNS, gender="")["gender"])
        self.assertEqual(self.ctx(SIGNS, gender="Female")["gender"], "Female")

    def test_dasha_now(self):
        birth, now = _dt.datetime(1990, 5, 15, 1, 0), _dt.datetime(2026, 10, 8, 12, 0)
        d = br.dasha_now(RULES, 123.4, birth, now)
        v = br.vimshottari(RULES, 123.4, birth, now)
        self.assertEqual((d["maha"], d["bhukti"]), (v["cur_maha"]["lord"], v["cur_bhukti"]["lord"]))
        self.assertAlmostEqual(d["age"], (now - birth).total_seconds() / (365.25 * 86400), places=6)
        late = br.dasha_now(RULES, 123.4, birth, _dt.datetime(2200, 1, 1))
        self.assertEqual((late["maha"], late["bhukti"]), (None, None))       # outside the 120-year span

    def test_combust_needs_the_same_sign_and_degrees(self):
        c = self.ctx(dict(SIGNS, Mercury=5, Sun=5), {"Mercury": 10, "Sun": 12})
        self.assertTrue(br.combust(RULES, c, "Mercury"))
        self.assertFalse(br.combust(RULES, c, "Sun"))
        self.assertFalse(br.combust(RULES, self.ctx(dict(SIGNS, Mercury=5, Sun=5), {"Mercury": 10, "Sun": 16}), "Mercury"))
        self.assertFalse(br.combust(RULES, self.ctx(dict(SIGNS, Mercury=5, Sun=5)), "Mercury"))   # no degrees
        self.assertFalse(br.combust(RULES, self.ctx(dict(SIGNS, Rahu=5, Sun=5), {"Rahu": 10, "Sun": 10}), "Rahu"))

    def test_afflicted_r5(self):
        self.assertTrue(br.afflicted(RULES, self.ctx(dict(SIGNS, Venus=5)), "Venus"))          # debilitated in Kanya
        self.assertFalse(br.afflicted(RULES, self.ctx(dict(SIGNS, Venus=6)), "Venus"))         # own sign Tula
        self.assertTrue(br.afflicted(RULES, self.ctx(dict(SIGNS, Venus=4)), "Venus"))          # Simha: the Sun is Venus's enemy
        c = self.ctx(dict(SIGNS, Venus=6, Sun=6), {"Venus": 3, "Sun": 6})
        self.assertTrue(br.afflicted(RULES, c, "Venus"))                                       # combust

    def test_exalted_and_combust_is_weak(self):
        # spec S1 (Session 29 p.29): a sign of weakness wins over a good sign
        c = self.ctx(dict(SIGNS, Mercury=5, Sun=5), {"Mercury": 10, "Sun": 12})
        self.assertEqual(br.dignity(RULES, "Mercury", 5, 10)["label"], "Exalted")
        self.assertEqual(br.strength_detail(RULES, c, "Mercury"), {"word": "weak", "reasons": ["combust"]})

    def test_own_sign_is_strong_and_debilitated_is_weak(self):
        self.assertEqual(br.strength(RULES, br.context(LAGNA, {"Mars": 0}, {"Mars": 25}), "Mars"), "strong")
        self.assertEqual(br.strength(RULES, br.context(LAGNA, {"Jupiter": 9}), "Jupiter"), "weak")

    def test_aspecting_own_house_no_longer_makes_strong(self):
        # Saturn in Dhanu (Jupiter's sign, neutral) aspects Kumbha, its own sign: no longer counts as strength (D1)
        self.assertEqual(br.strength(RULES, br.context(LAGNA, {"Saturn": 8}), "Saturn"), "depends")

    def test_lords_houses(self):
        self.assertEqual(br.lords_houses(RULES, LAGNA, "Mars"), [4, 9])          # Simha Lagna: Vrischika, Mesha
        self.assertEqual(br.lords_houses(RULES, LAGNA, "Sun"), [1])
        self.assertEqual(br.lords_houses(RULES, LAGNA, "Rahu"), [])

    def test_aspects_on_a_sign(self):
        got = br.aspects_on(RULES, self.ctx(SIGNS), 6)                        # Tula for the oracle chart
        want = [{"by": p, "house_aspect": h} for p in br.PLANET_ORDER if p in SIGNS
                for h in RULES["reference"]["SPECIAL_ASPECTS"][p] if (SIGNS[p] + h - 1) % 12 == 6]
        self.assertEqual(got, want)

    def test_teacher_count_nodes(self):
        self.assertEqual([br.teacher_count("Rahu", h) for h in (12, 9, 5)], [2, 5, 9])
        self.assertEqual(br.teacher_count("Jupiter", 9), 9)

    def test_sign_line_kanya(self):
        t = br.sign_line(RULES, 5)
        for frag in ("Kanya", "dual (Dwisabhava)", "Prithvi tatwa", "continuous or repeated", "it concerns property"):
            self.assertIn(frag, t)

    def test_sign_line_tula(self):
        t = br.sign_line(RULES, 6)
        for frag in ("Tula", "movable (Chara)", "Vayu tatwa", "West"):
            self.assertIn(frag, t)
        self.assertNotIn("property", t)
        self.assertNotIn("repeated", t)

    def test_male_signs(self):
        self.assertEqual([s for s in range(12) if br.is_male_sign(RULES, s)], [0, 2, 4, 6, 8, 10])


class LayerOne(unittest.TestCase):
    """Session 26 benefic/malefic lines and the 12th-house line on each Graha + Bhava card."""

    def gb(self, planet, sign, signs=None, deg=None):
        return br.graha_bhava(RULES, LAGNA, dict(signs or SIGNS, **{planet: sign}), planet, deg, True)

    def test_benefic_in_2nd_gets_general_and_house_lines(self):
        lines = [x["text"] for x in self.gb("Venus", 5)["nature_lines"]]      # Kanya = 2nd for Simha Lagna
        self.assertTrue(lines[0].startswith("Benefic planets bring ease and comfort"), lines[0])
        self.assertTrue(lines[1].startswith("A benefic in the 2nd house indicates that"), lines[1])
        self.assertFalse(any("malefic" in t.lower() and "benefic" not in t.lower() for t in lines))

    def test_saturn_in_3rd_gets_its_own_line(self):
        sat = [x["text"] for x in self.gb("Saturn", 6)["nature_lines"]]       # Tula = 3rd
        mars = [x["text"] for x in self.gb("Mars", 6)["nature_lines"]]
        own = [t for t in sat if t not in mars]
        self.assertEqual(len(own), 1)
        self.assertIn("younger co borns", own[0])
        self.assertTrue(sat[0].startswith("Malefic planets bring struggle and pressure"))

    def test_any_planet_rows_apply_to_both_natures(self):
        jup = [x["text"] for x in self.gb("Jupiter", 9)["nature_lines"]]     # Makara = 6th
        self.assertTrue(any("dusthana and a malefic house" in t for t in jup), jup)

    def test_sun_lines_are_mild(self):
        lines = [x["text"] for x in self.gb("Sun", 0)["nature_lines"]]         # Mesha = 9th
        self.assertTrue(lines)
        self.assertTrue(all(t.startswith("(mild) ") for t in lines), lines)
        self.assertTrue(all(x["status"] == "taught" and x["source"].startswith("S26 p.") for x in self.gb("Sun", 0)["nature_lines"]))

    def test_exalted_in_12th_keeps_the_bucket_line(self):
        jup = self.gb("Jupiter", 3, deg=5)                                    # Karkataka = 12th, exalted
        self.assertEqual((jup["house"], jup["dignity"]["label"]), (12, "Deep Exalted"))
        self.assertIn("even exalted, is in the bucket of losses", jup["twelfth_line"])
        self.assertEqual(self.gb("Jupiter", 2)["twelfth_line"], "")

    def test_card_carries_its_source(self):
        self.assertTrue(self.gb("Jupiter", 10)["source"].startswith("S24 p."))


class MarsRemedies(unittest.TestCase):
    """The class of 22 Oct 2026: her Mars remedy for Mars in the 2nd, 7th, 8th or 12th (the Kuja rows: Kuja section only)."""

    @classmethod
    def setUpClass(cls):
        cls.mars = [{"text": r["text"], "source": r["source"]} for r in RULES["remedies"] if r["topic"] == "Mars"]
        cls.kuja = [{"text": r["text"], "source": r["source"]} for r in RULES["remedies"] if r["topic"] == "Kuja"]

    def gb(self, planet, house, rules=RULES):
        sign = (LAGNA + house - 1) % 12
        g = br.graha_bhava(rules, LAGNA, dict(SIGNS, **{planet: sign}), planet, None, True)
        self.assertEqual(g["house"], house)
        return g

    def test_the_rows_are_in_the_rules(self):
        self.assertEqual((len(self.mars), len(self.kuja)), (7, 3))                   # + the 29 Oct row for a child
        self.assertEqual(br.MARS_REMEDY_HOUSES, (2, 7, 8, 12))

    def test_mars_in_the_8th_2nd_and_12th(self):
        for h in (2, 8, 12):
            self.assertEqual(self.gb("Mars", h)["remedies"], self.mars, h)

    def test_mars_in_the_7th_has_the_mars_rows_only(self):
        # the "For Kuja doṣa" rows belong to the Kuja Doṣa section, which knows whether the doṣa is cancelled
        # (user's ruling, 23 Oct 2026); the card goes by Mars's position alone
        self.assertEqual(self.gb("Mars", 7)["remedies"], self.mars)

    def test_other_houses_and_other_planets_have_none(self):
        for h in (1, 3, 4, 5, 6, 9, 10, 11):                 # the 4th is a Kuja position, but she gave no remedy for it
            self.assertEqual(self.gb("Mars", h)["remedies"], [], h)
        self.assertEqual(self.gb("Moon", 8)["remedies"], [])  # "if Moon is there, it is okay"
        self.assertEqual(self.gb("Saturn", 7)["remedies"], [])

    def test_a_row_added_on_the_sheet_shows_too(self):
        rules = dict(RULES, remedies=RULES["remedies"] + [dict(topic="Mars", text="My own Mars remedy.", source="me")])
        mine = {"text": "My own Mars remedy.", "source": "me"}             # each row keeps its own source
        self.assertEqual(self.gb("Mars", 8, rules)["remedies"][-1], mine)
        self.assertEqual(br.planet_remedies(rules, "Mars", 8)[-1], mine)

    def test_the_bhava_reading_carries_them(self):
        signs = dict(SIGNS, Mars=(LAGNA + 7) % 12)            # Mars in the 8th
        ctx = br.context(LAGNA, signs, {}, True)
        occ = next(o for o in br.bhava_reading(RULES, ctx, 8)["occupants"] if o["planet"] == "Mars")
        self.assertEqual(occ["remedies"], self.mars)


class Conditions(unittest.TestCase):
    """Conditional sentences (spec §6.6): which hold for a chart, with the right row and the 'active now' flag."""

    def conds(self, signs, degs=None, **kw):
        return br.chart_conditions(RULES, br.context(LAGNA, signs, degs or {}, **kw))

    def keys(self, signs, **kw):
        return [(c["key"], c["planet"], c["house"]) for c in self.conds(signs, **kw)]

    # Simha Lagna (4): house h is sign (3 + h) % 12
    @staticmethod
    def at(h):
        return (LAGNA + h - 1) % 12

    def base(self, **placed):
        far = {p: self.at(4) for p in br.PLANET_ORDER}                 # everyone in the 4th unless placed
        far.update({p: self.at(h) for p, h in placed.items()})
        return far

    def test_saturn_matures_until_36(self):
        signs = self.base(Saturn=7)
        self.assertIn(("saturn_matures", "Saturn", 7), self.keys(signs, age=30))
        self.assertNotIn(("saturn_matures", "Saturn", 7), self.keys(signs, age=40))
        row = next(c for c in self.conds(signs, age=30) if c["key"] == "saturn_matures")
        self.assertEqual(row["source"], "S25 p.11")

    def test_saturn_retro_1(self):
        self.assertIn(("saturn_retro_1", "Saturn", 1), self.keys(self.base(Saturn=1), retro={"Saturn": True}))
        self.assertNotIn(("saturn_retro_1", "Saturn", 1), self.keys(self.base(Saturn=1)))

    def test_saturn_afflicted_10_young(self):
        signs = dict(self.base(), Saturn=1)                              # Vrishabha is the 10th: Venus's, Saturn's friend
        self.assertNotIn("saturn_afflicted_10_young", [k for k, *_ in self.keys(signs, age=25)])
        signs = dict(self.base(Sun=10), Saturn=1)                         # combust with the Sun
        got = self.keys(signs, degs={"Saturn": 10, "Sun": 12}, age=25)
        self.assertIn(("saturn_afflicted_10_young", "Saturn", 10), got)
        self.assertNotIn(("saturn_afflicted_10_young", "Saturn", 10), self.keys(signs, degs={"Saturn": 10, "Sun": 12}, age=40))

    def test_saturn_mars_12_and_afflicted_12(self):
        got = self.keys(self.base(Saturn=12, Mars=12))                   # Karkataka: the Moon's sign, Saturn's enemy
        self.assertIn(("saturn_mars_12", "Saturn", 12), got)
        self.assertIn(("saturn_afflicted_12", "Saturn", 12), got)

    def test_jupiter_md_8_active_only_in_jupiter_md(self):
        c = next(x for x in self.conds(self.base(Jupiter=8), maha="Jupiter") if x["key"] == "jupiter_md_8")
        self.assertIs(c["active"], True)
        c = next(x for x in self.conds(self.base(Jupiter=8), maha="Venus", bhukti="Jupiter") if x["key"] == "jupiter_md_8")
        self.assertIs(c["active"], False)

    def test_venus_dasha_9_active_in_bhukti(self):
        c = next(x for x in self.conds(self.base(Venus=9), maha="Sun", bhukti="Venus") if x["key"] == "venus_dasha_9")
        self.assertIs(c["active"], True)

    def test_rahu_md_9(self):
        c = next(x for x in self.conds(self.base(Rahu=9), maha="Rahu") if x["key"] == "rahu_md_9")
        self.assertIs(c["active"], True)

    def test_twelfth_hidden_talent_active_for_its_planet(self):
        got = [c for c in self.conds(self.base(Mercury=12, Venus=12), maha="Mercury") if c["key"] == "twelfth_hidden_talent"]
        self.assertEqual([(c["planet"], c["active"]) for c in got], [("Mercury", True), ("Venus", False)])

    def test_upachaya_30s_each_planet(self):
        got = [(p, h) for k, p, h in self.keys(self.base(Sun=3, Moon=6, Mars=11, Jupiter=10)) if k == "upachaya_30s"]
        self.assertEqual(got, [("Sun", 3), ("Moon", 6), ("Mars", 11)])     # no 10th-house sentence in the slides

    def test_ketu_12_purpose_age_gate(self):
        self.assertIn(("ketu_12_purpose", "Ketu", 12), self.keys(self.base(Ketu=12), age=30))
        self.assertNotIn(("ketu_12_purpose", "Ketu", 12), self.keys(self.base(Ketu=12), age=50))

    def test_venus_good_when_not_afflicted(self):
        # Simha Lagna: the 2nd is Kanya, where Venus is debilitated; the 11th is Mithuna (Mercury, Venus's friend)
        self.assertNotIn(("venus_good", "Venus", 2), self.keys(dict(self.base(), Venus=self.at(2))))
        self.assertIn(("venus_good", "Venus", 11), self.keys(dict(self.base(), Venus=self.at(11))))

    def test_venus_mercury_5(self):
        self.assertIn(("venus_mercury_5", "Venus", 5), self.keys(self.base(Venus=5, Mercury=5)))
        self.assertNotIn(("venus_mercury_5", "Venus", 5), self.keys(self.base(Venus=5)))

    def test_seventh_lord_12(self):
        # Simha Lagna: the 7th is Kumbha, lord Saturn
        self.assertIn(("seventh_lord_12", "Saturn", 12), self.keys(self.base(Saturn=12)))

    def test_mercury_foreign_language_with_rahu_or_12th_lord(self):
        self.assertIn(("mercury_foreign_language", "Mercury", 2), self.keys(self.base(Mercury=2, Rahu=2)))
        self.assertIn(("mercury_foreign_language", "Mercury", 2), self.keys(self.base(Mercury=2, Moon=2)))   # Moon owns the 12th
        self.assertNotIn(("mercury_foreign_language", "Mercury", 2), self.keys(self.base(Mercury=2)))

    def test_moon_dual_10(self):
        dhanu = br.context(8, {"Moon": 5}, {})                           # Dhanu Lagna, Moon in Kanya (10th, dual)
        self.assertIn("moon_dual_10", [c["key"] for c in br.chart_conditions(RULES, dhanu)])
        simha = br.context(LAGNA, {"Moon": 1}, {})                       # Vrishabha 10th: fixed
        self.assertNotIn("moon_dual_10", [c["key"] for c in br.chart_conditions(RULES, simha)])

    def test_gender_rules_only_when_filled(self):
        signs = self.base(Venus=5, Jupiter=1)
        male = self.conds(signs, gender="Male")
        wife = [c for c in male if c["key"] == "venus_meets_wife"]
        self.assertEqual(len(wife), 1)
        self.assertEqual((wife[0]["house"], wife[0]["source"]), (5, "S24 p.22"))
        self.assertNotIn("jupiter_husband", [c["key"] for c in male])
        female = [c["key"] for c in self.conds(signs, gender="Female")]
        self.assertIn("jupiter_husband", female)
        self.assertNotIn("venus_meets_wife", female)
        none = [c["key"] for c in self.conds(signs, gender="Other")]
        self.assertFalse({"jupiter_husband", "venus_meets_wife"} & set(none))

    def test_venus_meets_wife_needs_a_row_for_its_house(self):
        self.assertNotIn("venus_meets_wife", [c["key"] for c in self.conds(self.base(Venus=7), gender="Male")])

    def test_unknown_age_and_dasha(self):
        got = self.conds(self.base(Saturn=7, Jupiter=8))
        self.assertIn("saturn_matures", [c["key"] for c in got])
        self.assertTrue(all(c["active"] is None for c in got))

    def test_order_follows_the_key_list(self):
        got = [c["key"] for c in self.conds(self.base(Saturn=7, Jupiter=8, Mercury=12), age=20, maha="Jupiter")]
        self.assertEqual(got, sorted(got, key=br.CONDITION_KEYS.index))



class LayerTwo(unittest.TestCase):
    """Session 27: the lord of house X in house Y, in sign S."""

    def entry(self, lagna, signs, x, degs=None):
        return next(r for r in br.bhava_bhava(RULES, br.context(lagna, signs, degs or {})) if r["lord_of"] == x)

    def rows(self, x, y, cond=""):
        return next(r["text"] for r in RULES["bhava_lord_in"]
                    if (r["lord_of"], r["sits_in"], r["condition"], r["exchange"]) == (x, y, cond, False))

    def test_depends_shows_both_lines(self):
        e = self.entry(3, {"Moon": 8}, 1)                                   # Karkataka Lagna, Moon in Dhanu (6th)
        self.assertEqual((e["sits_in"], e["strength"], e["status"]), (6, "depends", "taught"))
        self.assertEqual(e["text"], "\n\n".join([self.rows(1, 6), self.rows(1, 6, "strong"), self.rows(1, 6, "weak")]))

    def test_weak_lord_shows_weak_line(self):
        e = self.entry(4, {"Sun": 9}, 1)                                    # Simha Lagna, Sun in Makara: Saturn's, an enemy
        self.assertEqual((e["sits_in"], e["strength"]), (6, "weak"))
        self.assertEqual(e["text"], "\n\n".join([self.rows(1, 6), self.rows(1, 6, "weak")]))

    def test_strong_lord_shows_strong_line(self):
        e = self.entry(4, {"Sun": 11}, 1)                                   # Sun in Meena (8th): Jupiter's, a friend
        self.assertEqual((e["sits_in"], e["strength"]), (8, "strong"))
        self.assertEqual(e["text"], "\n\n".join([self.rows(1, 8), self.rows(1, 8, "strong")]))

    def test_difficult_placement_wording(self):
        e = self.entry(LAGNA, SIGNS, 4)                                     # Mars, 4th lord, in the 12th
        self.assertEqual(e["placement"], ["Dusthana"])
        self.assertEqual(e["placement_line"], "Placed in the 12th house, a Dusthana bhava. A difficult placement.")
        k = self.entry(LAGNA, dict(SIGNS, Mars=0), 4)                       # Mesha = 9th: Trikona, and Badhaka for Simha
        self.assertTrue(k["placement_line"].startswith("Placed in the 9th house, a Trikona and Badhaka bhava. Planets posited in a Trikona"),
                        k["placement_line"])
        self.assertNotIn("difficult", k["placement_line"])

    def test_blend_names_the_sign_and_both_houses(self):
        e = self.entry(LAGNA, SIGNS, 4)
        self.assertEqual(e["status"], "blend")
        self.assertTrue(e["text"].startswith("The lord of the 4th house ("), e["text"])
        self.assertIn("in Karkataka", e["text"])
        self.assertEqual(e["sign_line"], br.sign_line(RULES, 3))

    def test_dictum_when_the_lord_aspects_its_house(self):
        e = self.entry(0, {"Mars": 5}, 1)                                   # Mesha Lagna, Mars in Kanya: 8th aspect on Mesha
        self.assertEqual(e["dictum"], "The lord aspects its own house, so the 1st house is strong.")
        self.assertEqual(self.entry(0, {"Mars": 4}, 1)["dictum"], "")        # Simha: Mars aspects Vrischika, Kumbha, Meena

    def test_with_and_aspecting_the_lord(self):
        e = self.entry(0, {"Venus": 9, "Jupiter": 9, "Ketu": 5, "Saturn": 4, "Mars": 2}, 7)
        self.assertEqual(e["with_lord"][0], {"planet": "Jupiter", "how": "with", "aspect": "", "rules": [9, 12], "meanings": [],
                                            "readings": []})
        ketu = [w for w in e["with_lord"] if w["planet"] == "Ketu"]
        self.assertEqual([(w["how"], w["aspect"]) for w in ketu], [("aspect", br.aspect_name("Ketu", 5))])
        self.assertNotIn("Venus", [w["planet"] for w in e["with_lord"]])

    def test_parivartana_is_one_entry(self):
        rows = br.bhava_bhava(RULES, br.context(6, {"Saturn": 4, "Sun": 9}))     # Tula: 4L Saturn in Simha, 11L Sun in Makara
        four = next(r for r in rows if r["lord_of"] == 4)
        self.assertEqual((four["exchange"], four["status"]), (11, "taught"))
        self.assertTrue(four["text"].startswith("In her example chart (S27): There is a Parivartana between 4 th Lord Saturn and 11 th lord Sun"))
        self.assertNotIn(11, [r["lord_of"] for r in rows])
        self.assertIsNone(next(r for r in rows if r["lord_of"] == 5)["exchange"])   # 5L Saturn in the 11th: no exchange

    def test_parivartana_without_her_text_is_a_blend_of_both_houses(self):
        rows = br.bhava_bhava(RULES, br.context(0, {"Venus": 4, "Sun": 1}))       # Mesha: 2L Venus in Simha, 5L Sun in Vrishabha
        two = next(r for r in rows if r["lord_of"] == 2)
        self.assertEqual((two["exchange"], two["status"]), (5, "blend"))
        self.assertTrue(two["text"].startswith("Parivartana: the lords of the 2nd and 5th houses have exchanged signs."))
        self.assertNotIn(5, [r["lord_of"] for r in rows])
        self.assertIn(7, [r["lord_of"] for r in rows])                       # Venus also rules the 7th: no exchange there


class Aspects(unittest.TestCase):
    """Aspect meanings: Jupiter from each house (S24), Jupiter/Saturn/Mars counts (S27), the default (S27 p.18)."""

    def row(self, planet, aspect, frm):
        return next(r["text"] for r in RULES["aspect_meaning"] if (r["planet"], r["aspect"], r["from_house"]) == (planet, aspect, frm))

    def test_jupiter_5th_from_2nd_uses_s24_then_s27(self):
        got = [m["text"] for m in br.aspect_meaning(RULES, "Jupiter", 5, 2)]
        self.assertEqual(got, [self.row("Jupiter", 5, 2), self.row("Jupiter", 5, None), self.row("Jupiter", None, None)])
        self.assertEqual(br.aspect_meaning(RULES, "Jupiter", 5, 2)[0]["source"], "S24 p.3")

    def test_jupiter_7th_has_no_count_row(self):
        got = [m["text"] for m in br.aspect_meaning(RULES, "Jupiter", 7, 4)]
        self.assertEqual(got, [self.row("Jupiter", 7, 4), self.row("Jupiter", None, None)])

    def test_saturn_10th_is_karmic_responsibility(self):
        got = [m["text"] for m in br.aspect_meaning(RULES, "Saturn", 10, 4)]
        self.assertIn("karmic responsibility", got[0])
        self.assertEqual(got[1], self.row("Saturn", None, None))

    def test_venus_7th_uses_the_default(self):
        self.assertEqual([m["text"] for m in br.aspect_meaning(RULES, "Venus", 7, 1)], [self.row("any", None, None)])

    def test_rahu_counts_anticlockwise(self):
        self.assertEqual([m["text"] for m in br.aspect_meaning(RULES, "Rahu", 9)], [self.row("any", None, None)])

    def test_layers_carry_meanings(self):
        gg = br.graha_graha(RULES, LAGNA, SIGNS)
        for a in gg["aspects"]:
            frm = br.house_of(LAGNA, SIGNS[a["by"]])
            self.assertEqual(a["meanings"], [m["text"] for m in br.aspect_meaning(RULES, a["by"], a["house_aspect"], frm)])
        f = br.five_step(RULES, LAGNA, SIGNS, 7)
        for a in f["aspecting"]:
            self.assertEqual(a["aspect"], br.aspect_name(a["by"], a["house_aspect"]))
            self.assertTrue(a["meanings"])
        e = next(r for r in br.bhava_bhava(RULES, br.context(0, {"Venus": 9, "Ketu": 5})) if r["lord_of"] == 7)
        ketu = next(w for w in e["with_lord"] if w["planet"] == "Ketu")
        self.assertEqual(ketu["meanings"], [m["text"] for m in br.aspect_meaning(RULES, "Ketu", 5, 6)])


class LifeAreas(unittest.TestCase):
    """The 7-step method for the 16 Ready Reckoner areas (S27 pp.5-16)."""

    def ctx(self, signs=None, **kw):
        return br.context(LAGNA, signs or SIGNS, {}, **kw)

    def test_all_16_areas_run(self):
        got = br.life_areas(RULES, self.ctx())
        self.assertEqual([a["no"] for a in got], list(range(1, 17)))
        for a in got:
            self.assertEqual([b["house"] for b in a["bhavas"]], a["houses"])
            self.assertEqual(sorted(a), sorted(["no", "area", "houses", "link", "source", "bhavas", "karakas", "pac",
                                                "planet_link", "supports", "pressure"]))

    def test_foreign_travel_has_two_bhavas_and_rahu(self):
        a = br.life_area(RULES, self.ctx(), 15)
        self.assertEqual([b["house"] for b in a["bhavas"]], [9, 12])
        self.assertEqual([k["planet"] for k in a["karakas"]], ["Rahu"])
        self.assertIsNone(a["pac"])

    def test_love_marriage_pac(self):
        # Simha Lagna: 5th Dhanu (Jupiter), 7th Kumbha (Saturn). Jupiter in Kumbha = the 5th lord in the 7th.
        a = br.life_area(RULES, self.ctx(dict(SIGNS, Jupiter=10, Mercury=7, Ketu=7)), 16)
        self.assertEqual(a["pac"][0], "5th lord in the 7th")
        self.assertIn("Mercury and Ketu are together in the 4th", a["planet_link"])
        self.assertIn("PAC link: 5th lord in the 7th", a["supports"])
        # Jupiter in Mesha and Saturn in Vrishabha: neither in, nor aspecting, the other's house or lord
        none = br.life_area(RULES, self.ctx(dict(SIGNS, Jupiter=0, Saturn=1, Mercury=2, Ketu=1, Rahu=7)), 16)
        self.assertEqual((none["pac"], none["planet_link"]), ([], []))

    def test_marriage_karaka_without_gender(self):
        k = br.life_area(RULES, self.ctx(), 11)["karakas"]
        self.assertEqual([x["planet"] for x in k], ["Venus"])
        self.assertEqual(k[0]["note"], "For a woman's chart the husband's karaka is Mars.")

    def test_marriage_karaka_female_is_mars_with_jupiter_note(self):
        k = br.life_area(RULES, self.ctx(gender="Female"), 11)["karakas"]
        self.assertEqual([x["planet"] for x in k], ["Mars"])
        self.assertIn("Jupiter also represents Husband", k[0]["note"])

    def test_marriage_karaka_male_notes_where_he_meets_his_wife(self):
        k = br.life_area(RULES, self.ctx(dict(SIGNS, Venus=8), gender="Male"), 11)["karakas"]   # Venus in the 5th
        self.assertEqual(k[0]["planet"], "Venus")
        want = next(r["text"] for r in RULES["conditions"] if (r["key"], r["house"]) == ("venus_meets_wife", 5))
        self.assertEqual(k[0]["note"], want)

    def test_supports_and_pressure_wording(self):
        # Simha Lagna, Mother (4th = Vrischika, lord Mars). Jupiter in the 4th; Saturn aspects it from Kumbha (10th aspect);
        # Mars in Makara (6th): exalted but in a dusthana.
        signs = {"Jupiter": 7, "Saturn": 10, "Mars": 9, "Moon": 3}
        a = br.life_area(RULES, br.context(LAGNA, signs, {"Mars": 10, "Moon": 10}), 8)
        self.assertEqual(a["supports"][:2], ["Jupiter (benefic) in the 4th", "The 4th lord Mars is strong"])
        self.assertIn("Saturn (malefic) aspects the 4th", a["pressure"])
        self.assertIn("The 4th lord Mars is in the 6th, a difficult placement", a["pressure"])
        self.assertNotIn("Karaka Moon is strong", a["supports"])            # own sign, but Mars aspects it: mixed (D1)

    def test_partial_chart_has_no_lord_or_karaka(self):
        a = br.life_area(RULES, br.context(LAGNA, {"Sun": 4}), 8)          # only the Sun is known
        self.assertIsNone(a["bhavas"][0]["lord"])
        self.assertEqual(a["karakas"], [])


class ParivartanaKeepsHerText(unittest.TestCase):
    """Review fix: an exchange of signs must not hide the teacher's reading for either direction."""

    def row(self, x, y, cond=""):
        return next(r for r in RULES["bhava_lord_in"] if (r["lord_of"], r["sits_in"], r["condition"], r["exchange"]) == (x, y, cond, False))

    def test_exchange_shows_the_taught_row(self):
        # Mesha Lagna: 1st lord Mars in Karkataka (4th), 4th lord Moon in Mesha (1st)
        rows = br.bhava_bhava(RULES, br.context(0, {"Mars": 3, "Moon": 0}))
        one = next(r for r in rows if r["lord_of"] == 1)
        self.assertEqual((one["exchange"], one["status"], one["source"]), (4, "taught", self.row(1, 4)["source"]))
        self.assertEqual(one["text"], self.row(1, 4)["text"])
        self.assertNotIn(4, [r["lord_of"] for r in rows])

    def test_exchange_keeps_the_strong_and_weak_lines(self):
        # Karkataka Lagna: the Moon in Dhanu (6th, neutral -> depends), Jupiter (6th lord) in Karkataka
        one = next(r for r in br.bhava_bhava(RULES, br.context(3, {"Moon": 8, "Jupiter": 3})) if r["lord_of"] == 1)
        self.assertEqual((one["exchange"], one["strength"], one["status"]), (6, "depends", "taught"))
        self.assertEqual(one["text"], "\n\n".join([self.row(1, 6)["text"], self.row(1, 6, "strong")["text"], self.row(1, 6, "weak")["text"]]))

    def test_exchange_without_any_taught_row_is_still_a_blend(self):
        rows = br.bhava_bhava(RULES, br.context(0, {"Venus": 4, "Sun": 1}))        # 2nd <-> 5th: no taught row either way
        two = next(r for r in rows if r["lord_of"] == 2)
        self.assertEqual((two["exchange"], two["status"]), (5, "blend"))
        self.assertTrue(two["text"].startswith("Parivartana: the lords of the 2nd and 5th houses"))


class MildOnlyOnMaleficLines(unittest.TestCase):
    def test_sun_any_rows_are_not_marked_mild(self):
        g = br.graha_bhava(RULES, LAGNA, dict(SIGNS, Sun=9), "Sun", None, True)          # Makara = 6th for Simha
        rows = {r["text"]: r["nature"] for r in RULES["bhava_nature"] if r["house"] in (None, 6)}
        any_lines = [t for t, n in rows.items() if n == "any"]
        self.assertTrue(any_lines)
        texts = [x["text"] for x in g["nature_lines"]]
        for t in any_lines:
            self.assertIn(t, texts)                                   # shown as written
        for t in texts:
            if t.startswith("(mild) "):
                self.assertEqual(rows[t[len("(mild) "):]], "malefic")


from test_teacher_charts import CHARTS as _CHARTS, ctx as _chart_ctx


class StrengthS29(unittest.TestCase):
    """D1 (S29 pp.17, 29): weak, strong, mixed, depends — with the reasons."""

    def detail(self, planet, chart="S28_CHART_3"):
        return br.strength_detail(RULES, _chart_ctx(chart), planet)

    def only(self, signs, degs=None):
        return br.context(0, signs, degs or {})

    def test_debilitated_aspecting_own_house_is_weak(self):
        self.assertEqual(self.detail("Mercury"), {"word": "weak", "reasons": ["Debilitated"]})

    def test_exalted_with_rahu_is_weak(self):
        got = br.strength_detail(RULES, self.only({"Jupiter": 3, "Rahu": 3}), "Jupiter")
        self.assertEqual(got, {"word": "weak", "reasons": ["with Rahu"]})

    def test_own_sign_aspected_by_malefic_is_mixed(self):
        self.assertEqual(self.detail("Venus"), {"word": "mixed", "reasons": ["aspected by Saturn", "aspected by Rahu"]})

    def test_sun_aspect_makes_mixed(self):
        got = br.strength_detail(RULES, self.only({"Venus": 6, "Sun": 0}), "Venus")
        self.assertEqual(got, {"word": "mixed", "reasons": ["aspected by Sun"]})

    def test_strong_without_malefic_aspect(self):
        self.assertEqual(self.detail("Sun"), {"word": "strong", "reasons": ["Deep Exalted"]})

    def test_neutral_is_depends(self):
        self.assertEqual(br.strength_detail(RULES, self.only({"Saturn": 8}), "Saturn"),
                         {"word": "depends", "reasons": ["Neutral House"]})

    def test_nodes_follow_their_dignity(self):
        # D1 has no exemption for the nodes: the site marks them exalted in Vrishabha / Vrischika and debilitated opposite
        self.assertEqual(self.detail("Rahu"), {"word": "depends", "reasons": [br.NODE_LABEL]})            # Rahu in Kanya
        exalted = self.only({"Rahu": 1, "Ketu": 7})
        self.assertEqual(br.strength_detail(RULES, exalted, "Rahu"), {"word": "strong", "reasons": ["Exalted"]})
        self.assertEqual(br.strength_detail(RULES, exalted, "Ketu"), {"word": "strong", "reasons": ["Exalted"]})
        debilitated = self.only({"Rahu": 7, "Ketu": 1})
        self.assertEqual(br.strength_detail(RULES, debilitated, "Rahu"), {"word": "weak", "reasons": ["Debilitated"]})
        self.assertEqual(br.strength_detail(RULES, debilitated, "Ketu"), {"word": "weak", "reasons": ["Debilitated"]})
        aspected = self.only({"Rahu": 1, "Ketu": 7, "Saturn": 11})                                      # Saturn's 3rd
        self.assertEqual(br.strength_detail(RULES, aspected, "Rahu"), {"word": "mixed", "reasons": ["aspected by Saturn"]})

    def test_rahu_is_never_with_itself(self):
        got = br.strength_detail(RULES, self.only({"Rahu": 3, "Ketu": 9}), "Rahu")
        self.assertEqual(got, {"word": "depends", "reasons": [br.NODE_LABEL]})

    def test_strong_karaka_in_a_dusthana_is_only_pressure(self):
        # §6.2.3: a kāraka in the 6th, 8th or 12th is pressure; *otherwise* a strong kāraka is a support
        a = br.life_area(RULES, br.context(1, {"Venus": 6}), 11)           # Vrishabha Lagna, Venus in Tula (own, the 6th)
        self.assertEqual(a["karakas"][0]["strength"], "strong")
        self.assertIn("Karaka Venus is in the 6th", a["pressure"])
        self.assertNotIn("Karaka Venus is strong", a["supports"])

    def test_strength_is_the_word(self):
        for p in br.PLANET_ORDER:
            self.assertEqual(br.strength(RULES, _chart_ctx("S28_CHART_3"), p), self.detail(p)["word"])

    def test_mixed_shows_both_rows(self):
        # Vrishabha Lagna: lord Venus in Tula (its own sign, the 6th), Saturn in Mesha aspects Tula
        e = next(r for r in br.bhava_bhava(RULES, br.context(1, {"Venus": 6, "Saturn": 0})) if r["lord_of"] == 1)
        rows = {r["condition"]: r["text"] for r in RULES["bhava_lord_in"]
                if (r["lord_of"], r["sits_in"], r["exchange"]) == (1, 6, False)}
        self.assertEqual((e["sits_in"], e["strength"]), (6, "mixed"))
        self.assertEqual(e["text"], "\n\n".join([rows[""], rows["strong"], rows["weak"]]))

    def test_dusthana_line_kept_when_not_weak(self):
        signs = {"Saturn": 9}                                         # Mithuna Lagna: Saturn in Makara, its own sign, the 8th
        g = br.graha_bhava(RULES, 2, signs, "Saturn", 15, None, ctx=br.context(2, signs, {"Saturn": 15}))
        self.assertTrue([t for t in g["class_texts"] if "give good results" in t])


class RulingHouses(unittest.TestCase):
    def test_phrase(self):
        self.assertEqual(br.ruled_phrase([]), "")
        self.assertEqual(br.ruled_phrase([9]), "(rules the 9th)")
        self.assertEqual(br.ruled_phrase([5, 12]), "(rules the 5th and 12th)")
        self.assertEqual(br.ruled_phrase([1, 4, 7]), "(rules the 1st, 4th and 7th)")

    def test_karaka_items_name_malefic_aspects(self):
        signs = {"Moon": 3, "Mars": 9}                                     # Moon in Karkataka; Mars in Makara aspects it
        k = br.life_area(RULES, br.context(LAGNA, signs), 8)["karakas"][0]
        self.assertEqual((k["planet"], k["malefic_aspects"]), ("Moon", ["Mars"]))


class ChartReadings(unittest.TestCase):
    """Her Chart 3 sentences, matched on any chart (spec §6.4)."""

    def items(self, lagna, signs, degs=None):
        return br.chart_readings(RULES, br.context(lagna, signs, degs or {}))

    def find(self, got, kind, house, start):
        return [x for x in got if x["kind"] == kind and x["house"] == house and start in x["text"]]

    def test_resolve_planets(self):
        c = br.context(8, {"Sun": 0, "Mars": 3, "Jupiter": 2, "Moon": 7})
        self.assertEqual(br.resolve_planets(RULES, c, "Mars"), ["Mars"])
        self.assertEqual(br.resolve_planets(RULES, c, "Venus"), [])
        self.assertEqual(br.resolve_planets(RULES, c, "malefic"), ["Sun", "Mars"])
        self.assertEqual(br.resolve_planets(RULES, c, "benefic"), ["Moon", "Jupiter"])
        self.assertEqual(br.resolve_planets(RULES, c, "8th lord"), ["Moon"])          # Dhanu Lagna: 8th is Kataka
        self.assertEqual(br.resolve_planets(RULES, c, "2nd lord"), [])                # Saturn not placed

    def test_in_with_condition(self):
        # Dhanu Lagna, Mercury and Ketu in Meena (4th): Mercury is debilitated there
        got = self.items(8, {"Mercury": 11, "Ketu": 11, "Rahu": 5})
        hit = self.find(got, "in", 4, "In her example chart (S28): Mercury is also posited")
        self.assertEqual([(x["on"], x["with"]) for x in hit], [(["Mercury"], ["Ketu"])])
        # Mercury and Ketu together in Kanya (10th for Dhanu): Mercury is exalted, not debilitated — and not the 4th
        self.assertFalse(self.find(self.items(8, {"Mercury": 5, "Ketu": 5, "Rahu": 11}), "in", 4, "Mercury is also"))
        # Mercury debilitated in the 4th but without Ketu
        self.assertFalse(self.find(self.items(8, {"Mercury": 11, "Ketu": 0, "Rahu": 6}), "in", 4, "Mercury is also"))

    def test_two_malefics_need_two_planets(self):
        one = self.items(8, {"Mars": 3})                                  # only Mars aspects Makara (2nd)
        self.assertFalse(self.find(one, "aspects", 2, "In her example chart (S28): Two malefics"))
        c3 = br.chart_readings(RULES, _chart_ctx("S28_CHART_3"))
        hit = self.find(c3, "aspects", 2, "In her example chart (S28): Two malefics")
        self.assertEqual([x["on"] for x in hit], [["Mars", "Rahu"]])

    def test_nth_lord_spec(self):
        c3 = br.chart_readings(RULES, _chart_ctx("S28_CHART_3"))
        lord8 = [x for x in c3 if x["kind"] == "aspects lord" and x["house"] == 11 and "inheritance" in x["text"]]
        self.assertEqual([x["on"] for x in lord8], [["Moon"]])               # the 8th lord Moon aspects Venus
        hosp = [x for x in c3 if x["kind"] == "in" and x["house"] == 12 and "hospitalised" in x["text"]]
        self.assertEqual([x["on"] for x in hosp], [["Moon"]])

    def test_aspects_planet(self):
        c3 = br.chart_readings(RULES, _chart_ctx("S28_CHART_3"))
        hit = [x for x in c3 if x["kind"] == "aspects planet"]
        self.assertEqual([(x["on"], x["with"]) for x in hit], [(["Rahu"], ["Venus"])])

    def test_partial_chart_no_raise(self):
        for signs in ({}, {"Moon": 3}, {"Rahu": 0, "Ketu": 6}):
            self.assertIsInstance(self.items(4, signs), list)


class DegreeStages(unittest.TestCase):
    def st(self, planet, deg, age=None):
        return br.degree_stage(RULES, planet, deg, age)

    def test_band_edges(self):
        self.assertEqual((self.st("Jupiter", 0.0)["stage"], len(self.st("Jupiter", 0.0)["lines"])), ("At 0 degree", 2))
        for deg, stage in ((0.99, "Infant"), (1.0, "Young"), (5.999, "Young"), (6.0, "Adult"), (17.99, "Adult"),
                           (18.0, "Mature"), (26.0, "Old"), (29.999, "Old")):
            self.assertEqual(self.st("Jupiter", deg)["stage"], stage, deg)
            self.assertEqual(len(self.st("Jupiter", deg)["lines"]), 1, deg)
        rahu = self.st("Rahu", 26.5)
        self.assertEqual((rahu["stage"], len(rahu["lines"])), ("Old", 2))
        self.assertIn("lose their strength of giving malefic results", rahu["lines"][1])
        self.assertEqual(len(self.st("Jupiter", 0.5)["lines"]), 1)                  # not a malefic
        self.assertEqual(len(self.st("Sun", 27)["lines"]), 1)                       # her list leaves out the Sun

    def test_age_note(self):
        self.assertEqual(self.st("Saturn", 0.0, 34.6)["age_note"], "Age 34: past 32, so it now gives its results.")
        self.assertEqual(self.st("Saturn", 0.0, 25)["age_note"], "Age 25: results from about 32.")
        self.assertEqual(self.st("Saturn", 0.0)["age_note"], "")
        self.assertEqual(self.st("Jupiter", 10, 34)["age_note"], "")

    def test_no_degree(self):
        self.assertIsNone(self.st("Mars", None))

    def test_her_malefics(self):
        import session28_29_teacher_texts as t
        self.assertEqual(br.DEGREE_MALEFICS, t.MALEFICS_FOR_DEGREES)


class DeeperDasha(unittest.TestCase):
    def test_children_sum_to_parent(self):
        rnd = _random.Random(3)
        for _ in range(200):
            lord = rnd.choice(RULES["reference"]["VORDER"])
            start = _dt.datetime(1950, 1, 1) + _dt.timedelta(days=rnd.uniform(0, 30000))
            years = rnd.uniform(0.001, 20)
            kids = br.sub_periods(RULES, lord, start, years)
            self.assertEqual(len(kids), 9)
            self.assertEqual(kids[0]["lord"], lord)
            self.assertEqual(kids[0]["start"], start)
            self.assertEqual(kids[-1]["end"], start + _dt.timedelta(days=years * 365.25))
            for a, b in zip(kids, kids[1:]):
                self.assertEqual(a["end"], b["start"])
            self.assertAlmostEqual(sum(k["years"] for k in kids), years, places=9)

    def test_chain_boundary_instant(self):
        birth, moon = _dt.datetime(1990, 5, 15, 1, 0), 123.4
        v = br.vimshottari(RULES, moon, birth, _dt.datetime(2026, 1, 1))
        b = v["cur_bhukti"]
        years = RULES["reference"]["VYEARS"]
        kids = br.sub_periods(RULES, b["lord"], b["start"], years[v["cur_maha"]["lord"]] * years[b["lord"]] / 120)
        now = kids[4]["start"]
        chain = br.dasha_chain(RULES, br.vimshottari(RULES, moon, birth, now), now)
        self.assertEqual((chain[2]["lord"], chain[2]["start"]), (kids[4]["lord"], kids[4]["start"]))

    def test_chain_outside_span_is_empty(self):
        birth, moon = _dt.datetime(1990, 5, 15, 1, 0), 123.4
        v = br.vimshottari(RULES, moon, birth, birth)
        for now in (v["span_start"] - _dt.timedelta(days=1), v["span_end"] + _dt.timedelta(days=1)):
            self.assertEqual(br.dasha_chain(RULES, br.vimshottari(RULES, moon, birth, now), now), [])


# ---------------------------------------------------------------- her dignity sentences (spec 2026-10-13)
PROBE_M1 = {"Sun": 9, "Moon": 8, "Mars": 11, "Mercury": 9, "Jupiter": 4, "Venus": 3, "Saturn": 3, "Rahu": 11, "Ketu": 5}
PROBE_M2 = {"Sun": 9, "Moon": 6, "Mars": 11, "Mercury": 9, "Jupiter": 7, "Venus": 1, "Saturn": 2, "Rahu": 2, "Ketu": 8}
PROBE_T1 = {"Sun": 9, "Moon": 3, "Mars": 0, "Mercury": 1, "Jupiter": 2, "Venus": 5, "Saturn": 10, "Rahu": 2, "Ketu": 8}


class DignityClaims(unittest.TestCase):
    """Her sentences that state a dignity show only when it holds (spec 2026-10-13 §2-3)."""

    @staticmethod
    def bb(lagna, signs):
        ctx = br.context(lagna, signs, {p: 15.0 for p in signs})
        return {e["lord_of"]: e for e in br.bhava_bhava(RULES, ctx)}

    @staticmethod
    def chart3(**moved):
        c = _CHARTS["S28_CHART_3"]
        signs = {p: s for p, s in dict(c["signs"], **moved).items() if s is not None}
        return br.context(c["lagna"], signs, {p: d for p, d in c["degs"].items() if p in signs}, retro=c["retro"])

    def test_lord_lines_need_their_dignity(self):
        e = self.bb(0, PROBE_M1)                                   # Mesha Lagna
        for lord_of, text in ((7, "7 th lord Mercury is debilitated"), (8, "8th Lord Moon is debilitated"),
                              (9, "9 th lord Sun is exalted"), (10, "10 th lord Mercury is debilitated")):
            self.assertNotIn(text, e[lord_of]["text"], lord_of)
        self.assertEqual((e[9]["sits_in"], e[9]["status"]), (5, "blend"))     # the 9th lord sits in the 5th, not exalted

    def test_parivartana_text_needs_the_12th_lord_debilitated(self):
        e = self.bb(0, PROBE_M2)[8]                                # 12th lord Jupiter in Vrischika: a friend's sign
        self.assertEqual((e["exchange"], e["status"]), (12, "blend"))
        self.assertTrue(e["text"].startswith("Parivartana: the lords of the 8th and 12th"), e["text"][:80])
        e = self.bb(6, PROBE_T1)[8]                                # Tula: 8th lord Venus debilitated, 12th lord Mercury not
        self.assertEqual(e["exchange"], 12)
        self.assertNotIn("12 th lord Mars is debilitated", e["text"])
        self.assertIn("8th Lord Moon is debilitated", e["text"])

    def test_sun_claim_on_the_lagna_lord_reading(self):
        sun = lambda ctx: [x for x in br.chart_readings(RULES, ctx) if "bhava karaka Sun" in x["text"]]
        self.assertEqual(len(sun(self.chart3())), 1)
        self.assertEqual(sun(self.chart3(Sun=1)), [])             # the Sun in Vrishabha: not exalted
        self.assertTrue(any("Jupiter a benefic is aspecting" in x["text"] for x in br.chart_readings(RULES, self.chart3(Sun=1))))

    def test_missing_planet_fails_the_rule(self):
        ctx = self.chart3(Sun=None)
        self.assertFalse(br.claim_holds(RULES, ctx, ("Sun", "exalted")))
        self.assertFalse([x for x in br.chart_readings(RULES, ctx) if "bhava karaka Sun" in x["text"]])

    def test_deep_exalted_counts(self):
        ctx = self.chart3()
        self.assertEqual(br.dignity(RULES, "Sun", ctx["signs"]["Sun"], ctx["degs"]["Sun"])["label"], "Deep Exalted")
        self.assertTrue(br.claim_holds(RULES, ctx, ("Sun", "exalted")))
        self.assertTrue(br.claim_holds(RULES, ctx, ("12th lord", "debilitated")))
        self.assertTrue(br.claim_holds(RULES, ctx, ("lord", "debilitated"), 8))      # the 8th lord Moon
        self.assertTrue(br.claim_holds(RULES, ctx, None))


class DignityClaimsEditedRows(unittest.TestCase):
    """The Parivartana rule follows the two houses and Exchange = yes, whatever the row's Condition or order (review fix)."""

    def test_parivartana_rule_survives_an_edited_row(self):
        import copy
        for edit in ({"condition": "weak"}, {"lord_of": 12, "sits_in": 8}):
            rules = copy.deepcopy(RULES)
            row = next(r for r in rules["bhava_lord_in"] if r["exchange"] and {r["lord_of"], r["sits_in"]} == {8, 12})
            row.update(edit)
            e = next(x for x in br.bhava_bhava(rules, br.context(0, PROBE_M2, {p: 15.0 for p in PROBE_M2})) if x["lord_of"] == 8)
            self.assertNotIn("12 th lord Mars is debilitated", e["text"], edit)
            ctx3 = _chart_ctx("S28_CHART_3")
            e3 = next(x for x in br.bhava_bhava(rules, ctx3) if x["lord_of"] == 8)
            self.assertIn("12 th lord Mars is debilitated", e3["text"], edit)      # her chart: the 12th lord is debilitated


# The chart of the 2026-10-13 bhāva-by-bhāva draft: Simha Lagna; Sun, Mars, Mercury in Mesha (9th); Moon, Venus,
# Saturn, Rahu in Meena (8th); Jupiter in Simha (1st); Ketu in Kanya (2nd).
SIMHA_SIGNS = {"Sun": 0, "Moon": 11, "Mars": 0, "Mercury": 0, "Jupiter": 4, "Venus": 11, "Saturn": 11, "Rahu": 11, "Ketu": 5}
SIMHA_DEGS = {"Sun": 11.80, "Moon": 16.91, "Mars": 27.21, "Mercury": 12.31, "Jupiter": 2.45, "Venus": 26.86,
              "Saturn": 24.61, "Rahu": 24.47, "Ketu": 24.47}


def _strings(o):
    """Every string inside a nested reading."""
    if isinstance(o, str):
        return [o]
    if isinstance(o, dict):
        return [s for v in o.values() for s in _strings(v)]
    if isinstance(o, (list, tuple)):
        return [s for v in o for s in _strings(v)]
    return []


class BhavaReading(unittest.TestCase):
    """The Prediction read bhāva by bhāva (spec 2026-10-13-bhava-by-bhava): one house with everything that bears on it."""

    def simha(self, signs=None, degs=None):
        return br.context(4, signs or SIMHA_SIGNS, SIMHA_DEGS if degs is None else degs, True)

    def test_classes_and_badhaka_note(self):
        r9 = br.bhava_reading(RULES, self.simha(), 9)
        self.assertEqual([c["name"] for c in r9["classes"]], ["Trikona", "Apoklima", "Badhaka"])
        cls = {c["name"]: c for c in r9["classes"]}
        self.assertEqual(cls["Badhaka"]["note"],
                         "For a fixed (Sthira) Lagna the 9th is the Badhaka sthāna; its lord Mars is the Badhakādhipati.")
        self.assertEqual(cls["Trikona"]["meaning"], "The most auspicious houses (and their lords) in the chart.")
        self.assertEqual(cls["Trikona"]["note"], "")
        self.assertEqual(cls["Trikona"]["other_names"], "Lakshmi Sthanas; Dharmasthanas")
        self.assertEqual(br.first_sentence("No full stop"), "No full stop")
        self.assertEqual(br.first_sentence("One. Two. Three."), "One.")

    def test_occupants_lord_and_karaka(self):
        r9 = br.bhava_reading(RULES, self.simha(), 9)
        self.assertEqual([o["planet"] for o in r9["occupants"]], ["Sun", "Mars", "Mercury"])
        self.assertEqual((r9["lord"]["planet"], r9["lord"]["house"], r9["lord"]["exchange"]), ("Mars", 9, None))
        self.assertTrue(r9["lord"]["placement_line"].startswith("The lord sits in its own bhava"))
        self.assertNotIn("Mars", [w["planet"] for w in r9["lord_company"]])
        self.assertEqual([k["planet"] for k in r9["karakas"]], ["Sun", "Jupiter"])
        self.assertEqual(r9["life_areas"], [{"no": 12, "area": "Father"}, {"no": 15, "area": "Foreign travel"}])
        self.assertEqual([(c["a"], c["b"]) for c in r9["conjunctions"]], [("Sun", "Mars"), ("Sun", "Mercury"), ("Mars", "Mercury")])
        self.assertEqual([bool(c["combust_note"]) for c in r9["conjunctions"]], [False, True, False])
        self.assertEqual([(a["by"], a["to"]) for a in r9["planet_aspects"]],
                         [("Jupiter", "Sun"), ("Jupiter", "Mars"), ("Jupiter", "Mercury")])
        self.assertEqual(r9["supports"], ["Mercury (benefic) in the 9th", "Jupiter (benefic) aspects the 9th",
                                          "The 9th lord Mars is strong", "Mercury (benefic) is with the 9th lord",
                                          "Jupiter (benefic) aspects the 9th lord", "Karaka Sun is strong"])
        self.assertEqual(r9["pressure"], ["Sun (mild malefic) in the 9th", "Mars (malefic) in the 9th",
                                          "Sun (mild malefic) is with the 9th lord", "Karaka Jupiter is aspected by Ketu"])
        self.assertEqual((r9["rashi"], r9["name"], r9["full_name"]), ("Mesha", "Dharma", "Dharma · Bhagya · Pitru Sthana"))
        self.assertEqual(r9["occupants"][1]["graha_rashi"]["tatwa"], "Agni")

    def test_parivartana_on_both_houses(self):
        ctx = _chart_ctx("S28_CHART_3")
        entry = next(e for e in br.bhava_bhava(RULES, ctx) if e["lord_of"] == 8)
        r = {h: br.bhava_reading(RULES, ctx, h) for h in (4, 7, 8, 12)}
        self.assertEqual((r[8]["lord"]["exchange"], r[12]["lord"]["exchange"]), (12, 8))
        self.assertEqual((r[4]["lord"]["exchange"], r[7]["lord"]["exchange"]), (7, 4))
        self.assertEqual(r[8]["lord"]["text"], entry["text"])
        self.assertEqual(r[12]["lord"]["text"], entry["text"])
        self.assertIn("12 th lord Mars is debilitated", r[12]["lord"]["text"])
        self.assertEqual((r[8]["lord"]["planet"], r[12]["lord"]["planet"]), ("Moon", "Mars"))
        for h in r:
            self.assertEqual(r[h]["lord"]["dictum"], br._dictum(RULES, ctx, h), h)

    def test_planet_facts(self):
        ctx = self.simha()
        f = {p: br.planet_facts(RULES, ctx, p) for p in br.PLANET_ORDER}
        self.assertEqual((f["Jupiter"]["digbala"], f["Jupiter"]["digbala_text"], f["Jupiter"]["digbala_status"]),
                         ("strong", "Jupiter gains directional strength (digbala) in the 1st house.", "standard"))
        self.assertEqual((f["Sun"]["digbala"], f["Sun"]["digbala_text"], f["Sun"]["digbala_status"]),
                         ("", "neither — strongest in the 10th, weakest in the 4th", None))
        self.assertEqual((f["Rahu"]["digbala"], f["Rahu"]["digbala_text"]), (None, "none — a node has no directional strength"))
        self.assertEqual(f["Mars"]["roles"], ["Badhakadhipati", "Badhaka occupant"])
        self.assertEqual(f["Mars"]["classes"], ["Trikona", "Apoklima", "Badhaka"])
        self.assertEqual(f["Sun"]["strength"], {"word": "strong", "reasons": ["Exalted"]})
        self.assertEqual(f["Sun"]["dignity"]["label"], "Exalted")
        self.assertEqual(f["Sun"]["dignity_effect"], RULES["dignity_effect"]["Exalted"]["text"])
        self.assertEqual((f["Sun"]["house"], f["Sun"]["rashi"], f["Sun"]["deg"], f["Sun"]["retro"]), (9, "Mesha", 11.80, False))
        self.assertIsNone(br.planet_facts(RULES, self.simha({p: s for p, s in SIMHA_SIGNS.items() if p != "Moon"}), "Moon"))
        jup = br.planet_facts(RULES, _chart_ctx("S28_CHART_3"), "Jupiter")
        self.assertEqual((jup["house"], jup["digbala"]), (7, "lost"))
        self.assertEqual(jup["digbala_text"],
                         "Jupiter loses directional strength (digbala) in the 7th house, opposite its strongest house, the 1st.")

    def test_partial_chart(self):
        signs = {p: s for p, s in SIMHA_SIGNS.items() if p not in ("Moon", "Rahu", "Ketu")}
        ctx = self.simha(signs, {})
        r = [br.bhava_reading(RULES, ctx, h) for h in range(1, 13)]
        self.assertIsNone(r[11]["lord"])                           # the 12th lord is the Moon
        self.assertEqual(r[11]["lord_company"], [])
        self.assertEqual([k["planet"] for k in r[3]["karakas"]], ["Venus"])
        self.assertIsNone(r[8]["occupants"][0]["facts"]["deg"])

    def test_nothing_lost(self):
        """Every text the By-layer view shows appears in the reading of the house it belongs to (spec §1.3)."""
        rnd = _random.Random(1313)
        for n in range(200):
            pool = rnd.sample(range(12), rnd.choice([3, 5, 12]))
            signs = {p: rnd.choice(pool) for p in br.PLANET_ORDER}
            degs = {p: round(rnd.uniform(0, 29.99), 2) for p in br.PLANET_ORDER}
            lagna = rnd.randrange(12)
            ctx = br.context(lagna, signs, degs, rnd.random() < 0.5, {p: rnd.random() < 0.3 for p in br.PLANET_ORDER},
                             rnd.choice(["Male", "Female"]), round(rnd.uniform(5, 80), 2),
                             rnd.choice(br.PLANET_ORDER), rnd.choice(br.PLANET_ORDER))
            layer2 = br.bhava_bhava(RULES, ctx)
            text = {h: "\n".join(_strings(br.bhava_reading(RULES, ctx, h, layer2))) for h in range(1, 13)}
            want = []                                              # (house, text)
            conds = br.chart_conditions(RULES, ctx)
            gr = {x["planet"]: x for x in br.graha_rashi(RULES, lagna, signs, degs)}
            for p in br.PLANET_ORDER:
                h = br.house_of(lagna, signs[p])
                g = br.graha_bhava(RULES, lagna, signs, p, degs[p], ctx["waxing"], ctx=ctx)
                ds = g["degree_stage"]
                for t in (g["points"] + g["extra"] + [x["text"] for x in g["nature_lines"]] + g["class_texts"] + g["readings"]
                          + [g["dignity_line"], g["digbala_line"], g["twelfth_line"], gr[p]["text"]]
                          + (ds["lines"] if ds else []) + [c["text"] for c in conds if c["planet"] == p]):
                    want.append((h, t))
            for e in layer2:
                for h in (e["lord_of"],) + ((e["exchange"],) if e["exchange"] else ()):
                    want.append((h, e["text"]))
                want.append((e["lord_of"], e["placement_line"]))
                for w in e["with_lord"]:
                    want += [(e["lord_of"], t) for t in w["readings"] + w["meanings"]]
            gg = br.graha_graha(RULES, lagna, signs, degs)
            want += [(c["house"], t) for c in gg["conjunctions"] for t in (c["text"], c["combust_note"])]
            want += [(a["house"], a["text"]) for a in gg["aspects"]]
            for h, t in want:
                if t:
                    self.assertIn(t, text[h], (n, h, t[:60]))
