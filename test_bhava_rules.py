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
    def test_nature_edge_cases(self):
        base = {p: 0 for p in br.PLANET_ORDER}
        with_saturn = dict(base, Saturn=0, Mercury=0)
        self.assertEqual(br.nature("Mercury", with_saturn, True), "malefic")            # beside Saturn
        apart = dict(base, Mars=5, Saturn=6, Rahu=7, Ketu=8, Mercury=0)
        self.assertEqual(br.nature("Mercury", apart, True), "benefic")
        sun_only = dict(apart, Sun=0)
        self.assertEqual(br.nature("Mercury", sun_only, True), "benefic")              # Sun does not spoil Mercury
        for node in ("Rahu", "Ketu"):
            self.assertEqual(br.nature("Mercury", dict(apart, **{node: 0}), True), "malefic")
        self.assertEqual(br.nature("Moon", apart, True), "benefic")
        self.assertEqual(br.nature("Moon", apart, False), "malefic")
        self.assertEqual([br.nature(p, apart, True) for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")], ["malefic"] * 5)
        self.assertEqual([br.nature(p, apart, True) for p in ("Jupiter", "Venus")], ["benefic"] * 2)

    def test_moon_waxing_at_the_purnima_boundary(self):
        self.assertTrue(br.moon_waxing(10.0, 10.0))          # separation 0 -> tithi 1
        self.assertTrue(br.moon_waxing(0.0, 179.99))         # tithi 15, Purnima
        self.assertFalse(br.moon_waxing(0.0, 180.0))         # tithi 16, Krishna paksha
        self.assertFalse(br.moon_waxing(100.0, 99.0))        # separation 359 -> tithi 30

    def test_class_readings_rules(self):
        reads = {r["planet"]: r for r in br.class_readings(RULES, LAGNA, SIGNS, True)}
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
            next(r for r in br.class_readings(RULES, LAGNA, in7, True) if r["planet"] == "Saturn")["texts"]))

    def test_ninth_house_is_the_apoklima_exception(self):
        nine = dict(SIGNS, Venus=0)                                  # Venus in the 9th (Mesha for Simha Lagna)
        txt = " | ".join(next(r for r in br.class_readings(RULES, LAGNA, nine, True) if r["planet"] == "Venus")["texts"])
        self.assertIn("exception", txt)
        self.assertNotIn("considered weak", txt)
        weak = " | ".join(next(r for r in br.class_readings(RULES, LAGNA, SIGNS, True) if r["planet"] == "Moon")["texts"])
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
        rows = br.bhava_bhava(RULES, LAGNA, {"Sun": 4})                   # only the Sun is known
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
        row = next(r for r in br.bhava_bhava(RULES, LAGNA, in7) if (r["lord_of"], r["sits_in"]) == (2, 7))
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
        jup = br.graha_bhava(RULES, LAGNA, SIGNS, "Jupiter", None, True)                    # curated, 7th, Kendra
        self.assertEqual((jup["house"], jup["status"]), (7, "curated"))
        self.assertEqual(jup["classes"], ["Kendra", "Apachaya", "Maraka"])
        self.assertEqual(jup["class_texts"], next(r for r in br.class_readings(RULES, LAGNA, SIGNS, True)
                                                    if r["planet"] == "Jupiter")["texts"])
        self.assertEqual(br.graha_bhava(RULES, LAGNA, SIGNS, "Venus", None, True)["digbala_line"], "")

    def test_aspect_pairs_for_the_oracle_chart(self):
        got = [(a["by"], a["to"], a["house_aspect"]) for a in br.graha_graha(RULES, LAGNA, SIGNS)["aspects"]]
        self.assertEqual(got, [
            ("Mars", "Moon", 4), ("Mars", "Saturn", 7), ("Mars", "Jupiter", 8), ("Mercury", "Ketu", 7),
            ("Jupiter", "Sun", 5), ("Jupiter", "Venus", 5), ("Jupiter", "Moon", 9), ("Saturn", "Mars", 7),
            ("Saturn", "Moon", 10), ("Rahu", "Saturn", 9), ("Ketu", "Mars", 9), ("Ketu", "Moon", 12)])
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
        self.assertEqual(f["aspecting"], [{"by": "Mars", "house_aspect": 8}])
        self.assertEqual(f["karakas"], [{"planet": "Venus", "house": 11}])
        self.assertIn("Spouse", f["significations"])

    def test_bhava_bhava_blends_and_marks_own_house(self):
        rows = br.bhava_bhava(RULES, LAGNA, SIGNS)
        self.assertEqual([r["lord_of"] for r in rows], list(range(1, 13)))
        mars = next(r for r in rows if r["lord_of"] == 4)                    # Mars owns the 4th, sits in the 12th
        self.assertEqual((mars["lord"], mars["sits_in"], mars["status"]), ("Mars", 12, "blend"))
        self.assertIn("Dusthana", mars["text"])
        self.assertIn(RULES["reference"]["BHAVA_INFO"]["4"]["sig"].rstrip("."), mars["text"])
        self.assertIn(RULES["reference"]["BHAVA_INFO"]["12"]["sig"].rstrip("."), mars["text"])
        own = next(r for r in br.bhava_bhava(RULES, LAGNA, dict(SIGNS, Sun=4)) if r["lord_of"] == 1)
        self.assertEqual(own["sits_in"], 1)
        self.assertIn("own bhava", own["text"])

    def test_graha_rashi_blends_rashi_fields_and_dignity(self):
        moon = next(r for r in br.graha_rashi(RULES, LAGNA, SIGNS, {"Moon": 5.0}) if r["planet"] == "Moon")
        tula = RULES["reference"]["RASHI"][6]
        self.assertEqual((moon["tatwa"], moon["direction"], moon["varna"], moon["mode"]),
                         (tula["tatwa"], tula["direction"], tula["varna"], tula["mode"]))
        self.assertEqual(moon["status"], "blend")
        self.assertEqual(moon["dignity"], "Neutral House")                   # Libra is Venus's; Moon-Venus are neutral
        self.assertTrue(moon["strength_line"].startswith("Neutral House"))
        self.assertIn(tula["sanskrit"], moon["text"])

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
        seen |= {r["status"] for r in br.bhava_bhava(RULES, LAGNA, chart)}
        seen |= {r["status"] for r in br.graha_rashi(RULES, LAGNA, chart, {})}
        gg = br.graha_graha(RULES, LAGNA, chart)
        seen |= {c["status"] for c in gg["conjunctions"]} | {a["status"] for a in gg["aspects"]}
        seen.discard(None)
        self.assertTrue({"taught", "curated", "blend", "standard"} <= seen, seen)
        self.assertLessEqual(seen, {"taught", "curated", "blend", "standard"})


if __name__ == "__main__":
    unittest.main()
