"""The teacher's worked charts (Sessions 23 (2024 deck) to 27) as fixed cases: the engine must never contradict
what she concluded (python3 -m unittest -v test_teacher_charts).

Signs are 0-based (Mesha = 0 … Meena = 11). "( )" around a planet on her charts marks it retrograde.
"""
import unittest

import bhava_rules as br

RULES = br.load_rules()
MESHA, VRISHABHA, MITHUNA, KARKATAKA, SIMHA, KANYA, TULA, VRISCHIKA, DHANU, MAKARA, KUMBHA, MEENA = range(12)


def _chart(lagna, placed, retro=()):
    return {"lagna": lagna, "signs": {p: s for p, (s, _) in placed.items()},
            "degs": {p: d for p, (_, d) in placed.items() if d is not None}, "retro": {p: True for p in retro}}


CHARTS = {
    # S23-2024 p.6: Moon in the 2nd, Makara Lagna
    "S23_2024_A": _chart(MAKARA, {"Jupiter": (MAKARA, 15), "Moon": (KUMBHA, 20), "Mars": (MEENA, 24), "Saturn": (MITHUNA, 4),
                                  "Ketu": (MITHUNA, 13), "Sun": (KARKATAKA, 3), "Mercury": (KARKATAKA, 4),
                                  "Venus": (KARKATAKA, 29), "Rahu": (DHANU, 13)}, retro=("Jupiter", "Mercury", "Rahu", "Ketu")),
    # S23-2024 p.11: Moon in the 6th, Vrishabha Lagna
    "S23_2024_B": _chart(VRISHABHA, {"Sun": (VRISHABHA, 2), "Mars": (VRISHABHA, 15), "Mercury": (VRISHABHA, 12),
                                     "Rahu": (KARKATAKA, 3), "Moon": (TULA, 18), "Ketu": (MAKARA, 3), "Jupiter": (MESHA, 26),
                                     "Venus": (MESHA, 25), "Saturn": (MESHA, 27)}, retro=("Rahu", "Ketu")),
    # S23-2024 p.13 = S27 Chart 1 (pp.8-16): Moon in the 7th, Mesha Lagna
    "S23_2024_C": _chart(MESHA, {"Saturn": (SIMHA, 22), "Mars": (KANYA, 13), "Ketu": (KANYA, 15), "Moon": (TULA, 29),
                                 "Jupiter": (MAKARA, 29), "Venus": (MAKARA, 14), "Sun": (KUMBHA, 24), "Mercury": (KUMBHA, 8),
                                 "Rahu": (MEENA, 15)}, retro=("Saturn", "Mars", "Rahu", "Ketu")),
    # S23-2024 p.17: Moon in the 10th in a dual sign, Dhanu Lagna
    "S23_2024_D": _chart(DHANU, {"Rahu": (DHANU, 2), "Sun": (MAKARA, 28), "Venus": (MAKARA, 2), "Mercury": (KUMBHA, 16),
                                 "Jupiter": (KUMBHA, 0), "Mars": (MESHA, 27), "Saturn": (MITHUNA, 4), "Ketu": (MITHUNA, 2),
                                 "Moon": (KANYA, 21)}, retro=("Venus", "Saturn", "Rahu", "Ketu")),
    # S27 pp.21-24: the second chart, Tula Lagna
    "S27_CHART_2": _chart(TULA, {"Ketu": (TULA, 6), "Jupiter": (DHANU, 25), "Venus": (MAKARA, 6), "Mercury": (MAKARA, 16),
                                 "Sun": (MAKARA, 23), "Mars": (KUMBHA, 2), "Rahu": (MESHA, 6), "Moon": (MESHA, 16),
                                 "Saturn": (SIMHA, 10)}, retro=("Mercury", "Saturn", "Rahu", "Ketu")),
    # S27 pp.19-20: the book chart "Chart XIB/XIA Sri Chaitanya" (no degrees given)
    "BOOK_SRI_CHAITANYA": _chart(TULA, {"Saturn": (VRISCHIKA, None), "Jupiter": (DHANU, None), "Mars": (MAKARA, None),
                                        "Rahu": (KUMBHA, None), "Sun": (KUMBHA, None), "Mercury": (MEENA, None),
                                        "Venus": (MESHA, None), "Moon": (SIMHA, None), "Ketu": (SIMHA, None)}),
}


def s26_karkataka(moon_house):
    """S26 pp.16-27: Karkataka Lagna with only its lord, the Moon, drawn — in house `moon_house`."""
    return _chart(KARKATAKA, {"Moon": ((KARKATAKA + moon_house - 1) % 12, 15)})


def ctx(name, **kw):
    c = CHARTS[name] if isinstance(name, str) else name
    return br.context(c["lagna"], c["signs"], c["degs"], retro=c["retro"], **kw)


def lord_sits(c, house):
    lord = br.house_lord(RULES, c["lagna"], house)
    return br.house_of(c["lagna"], c["signs"][lord])


class S27Chart1(unittest.TestCase):
    def test_lord_list_p8(self):
        c = CHARTS["S23_2024_C"]
        self.assertEqual({h: lord_sits(c, h) for h in range(1, 13)},
                         {1: 6, 2: 10, 3: 11, 4: 7, 5: 11, 6: 11, 7: 10, 8: 6, 9: 10, 10: 5, 11: 5, 12: 10})

    def test_mars_aspects_lagna(self):
        self.assertIn({"by": "Mars", "house_aspect": 8}, br.aspects_on(RULES, ctx("S23_2024_C"), MESHA))


if __name__ == "__main__":
    unittest.main()


class S23_2024(unittest.TestCase):
    def test_moon_readings_have_no_malefic_lines(self):
        malefic = {r["text"] for r in RULES["bhava_nature"] if r["nature"] == "malefic"}
        malefic |= {r["text"] for r in RULES["class_rules"] if r["applies"] == "malefic"}
        for name in ("S23_2024_A", "S23_2024_B", "S23_2024_C", "S23_2024_D"):
            c = CHARTS[name]
            g = br.graha_bhava(RULES, c["lagna"], c["signs"], "Moon", c["degs"]["Moon"], False)   # A, C, D are waning
            self.assertEqual(g["status"], "taught", name)
            self.assertEqual(g["nature"], "benefic", name)
            self.assertFalse({x["text"] for x in g["nature_lines"]} & malefic, name)
            self.assertFalse(set(g["class_texts"]) & malefic, name)


class Conditions(unittest.TestCase):
    def test_chart_d_has_moon_dual_10(self):
        got = br.chart_conditions(RULES, ctx("S23_2024_D"))
        self.assertIn(("moon_dual_10", "Moon", 10), [(c["key"], c["planet"], c["house"]) for c in got])

    def test_chart_2_first_child_male(self):
        got = br.chart_conditions(RULES, ctx("S27_CHART_2"))
        c = next(c for c in got if c["key"] == "first_child_male")
        self.assertEqual((c["planet"], c["house"], c["source"]), ("Saturn", 5, "S27 p.24"))
        self.assertIn("first child is Male", c["text"])



def layer2(name, house):
    return next(r for r in br.bhava_bhava(RULES, ctx(name)) if r["lord_of"] == house or r["exchange"] == house)


class S27LayerTwo(unittest.TestCase):
    def test_lagna_lord_in_6th(self):
        e = layer2("S23_2024_C", 1)
        self.assertEqual((e["lord"], e["sits_in"], RULES["reference"]["RASHI"][e["sign"]]["sanskrit"]), ("Mars", 6, "Kanya"))
        self.assertIn("continuous or repeated", e["sign_line"])
        self.assertIn("property", e["sign_line"])
        self.assertEqual(e["dictum"], "The lord aspects its own house, so the 1st house is strong.")
        self.assertEqual(e["status"], "taught")
        self.assertTrue(e["text"].startswith("It is a difficult placement"))
        self.assertIn("In her example chart (S27)", e["text"])

    def test_7th_lord_with_jupiter_and_ketu_aspect(self):
        e = layer2("S23_2024_C", 7)
        self.assertEqual((e["lord"], e["sits_in"], e["status"]), ("Venus", 10, "taught"))
        jup = next(w for w in e["with_lord"] if w["planet"] == "Jupiter")
        self.assertEqual((jup["how"], jup["rules"]), ("with", [9, 12]))
        ketu = next(w for w in e["with_lord"] if w["planet"] == "Ketu")
        self.assertEqual((ketu["how"], ketu["aspect"]), ("aspect", br.aspect_name("Ketu", 5)))

    def test_chart_2_third_lord_in_third(self):
        e = layer2("S27_CHART_2", 3)
        self.assertEqual((e["lord"], e["sits_in"], e["status"], e["source"]), ("Jupiter", 3, "taught", "S27 p.22"))

    def test_chart_2_parivartana_4_11(self):
        rows = br.bhava_bhava(RULES, ctx("S27_CHART_2"))
        four = next(r for r in rows if r["lord_of"] == 4)
        self.assertEqual((four["exchange"], four["status"]), (11, "taught"))
        self.assertNotIn(11, [r["lord_of"] for r in rows])

    def test_book_chart_saturn_mars_exchange(self):
        rows = br.bhava_bhava(RULES, ctx("BOOK_SRI_CHAITANYA"))
        # Tula Lagna: Mars (2L, 7L) in Makara (4th); Saturn (4L, 5L) in Vrischika (2nd)
        e = next(r for r in rows if r["exchange"])
        self.assertEqual((e["lord_of"], e["lord"], e["exchange"]), (2, "Mars", 4))


class S26Series(unittest.TestCase):
    def test_lagna_lord_in_each_house(self):
        import session23_teacher_slides as ts
        for h in range(1, 13):
            c = s26_karkataka(h)
            e = layer2(c, 1)
            want = next(t for a, b, cond, x, t, s in ts.LORD_IN if (a, b, cond, x) == (1, h, "", False))
            self.assertEqual(e["sits_in"], h)
            self.assertTrue(e["text"].startswith(want), h)
        eleventh = s26_karkataka(11)
        self.assertEqual(br.dignity(RULES, "Moon", eleventh["signs"]["Moon"], 3)["label"], "Deep Exalted")   # S26 p.26


class AspectsAndRashi(unittest.TestCase):
    def test_mother_4th_aspects(self):
        c = CHARTS["S23_2024_C"]
        got = br.five_step(RULES, c["lagna"], c["signs"], 4)["aspecting"]
        self.assertEqual([a["by"] for a in got], ["Jupiter", "Venus", "Rahu"])           # S27 p.14

    def test_book_chart_listed_aspects_found(self):
        c = CHARTS["BOOK_SRI_CHAITANYA"]
        got = {(a["by"], a["to"], a["house_aspect"]) for a in br.graha_graha(RULES, c["lagna"], c["signs"])["aspects"]}
        for want in (("Sun", "Moon", 7), ("Mars", "Venus", 4), ("Mars", "Moon", 8), ("Jupiter", "Moon", 9),
                     ("Jupiter", "Venus", 5), ("Saturn", "Mars", 3), ("Saturn", "Moon", 10)):
            self.assertIn(want, got)
        lagna = br.five_step(RULES, c["lagna"], c["signs"], 1)["aspecting"]
        twelfth = br.five_step(RULES, c["lagna"], c["signs"], 12)["aspecting"]
        self.assertIn(("Venus", 7), [(a["by"], a["house_aspect"]) for a in lagna])            # S27 p.20 (iv)
        self.assertIn(("Mercury", 7), [(a["by"], a["house_aspect"]) for a in twelfth])         # S27 p.20 (v)

    def test_moon_rashi_rows_are_taught(self):
        for name, source in (("S23_2024_D", "S23-2024 p.5"), ("S23_2024_C", "S23-2024 p.11")):
            c = CHARTS[name]
            moon = next(r for r in br.graha_rashi(RULES, c["lagna"], c["signs"], c["degs"]) if r["planet"] == "Moon")
            row = next(r for r in RULES["graha_rashi"] if (r["planet"], r["rashi"]) == ("Moon", c["signs"]["Moon"] + 1))
            self.assertEqual((moon["status"], moon["text"], row["source"]), ("taught", row["text"], source))


def area(name_or_chart, no, **kw):
    return br.life_area(RULES, ctx(name_or_chart, **kw), no)


class LifeAreas(unittest.TestCase):
    def test_mother(self):                                                  # S27 p.14
        a = area("S23_2024_C", 8)
        self.assertEqual((a["area"], a["houses"]), ("Mother", [4]))
        b = a["bhavas"][0]
        self.assertEqual((b["house"], b["rashi"], b["occupants"]), (4, "Karkataka", []))
        self.assertEqual([x["by"] for x in b["aspecting"]], ["Jupiter", "Venus", "Rahu"])
        self.assertEqual(b["lord"]["planet"], "Moon")
        self.assertIn(("Saturn", "aspect"), [(w["planet"], w["how"]) for w in b["with_lord"]])
        self.assertEqual([k["planet"] for k in a["karakas"]], ["Moon"])

    def test_marriage(self):                                                # S27 pp.15-16
        a = area("S23_2024_C", 11)
        b = a["bhavas"][0]
        for frag in ("movable (Chara)", "Vayu", "West"):
            self.assertIn(frag, b["sign_line"])
        self.assertEqual([o["planet"] for o in b["occupants"]], ["Moon"])
        self.assertIn("Saturn", [x["by"] for x in b["aspecting"]])
        self.assertEqual((b["lord"]["planet"], b["lord"]["house"]), ("Venus", 10))
        self.assertEqual(b["lord"]["status"], "taught")                     # 7th lord in the 10th, S27 p.15
        jup = next(w for w in b["with_lord"] if w["planet"] == "Jupiter")
        self.assertEqual((jup["how"], jup["rules"]), ("with", [9, 12]))
        self.assertIn(("Ketu", "aspect"), [(w["planet"], w["how"]) for w in b["with_lord"]])

    def test_chart_2_ketu_in_lagna_aspected_by_saturn(self):              # S27 p.21
        b = area("S27_CHART_2", 1)["bhavas"][0]
        self.assertIn("Ketu", [o["planet"] for o in b["occupants"]])
        self.assertIn("Saturn", [x["by"] for x in b["aspecting"]])
