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


if __name__ == "__main__":
    unittest.main()
