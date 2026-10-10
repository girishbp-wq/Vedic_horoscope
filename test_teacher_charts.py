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
