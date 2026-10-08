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


if __name__ == "__main__":
    unittest.main()
