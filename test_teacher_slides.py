"""The teacher's texts from Sessions 23 (2024 deck) to 27 (python3 -m unittest -v test_teacher_slides)."""
import re
import unittest

import session23_teacher_slides as ts

PLANETS8 = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
DECK = r"(S23-2024|S23|S24|S25|S26|S27)"
SRC = re.compile(rf"^{DECK} pp?\.\d+(-\d+)?(; {DECK} pp?\.\d+(-\d+)?)*$")


class TeacherSlides(unittest.TestCase):
    def test_96_cells_with_page_sources(self):
        self.assertEqual(sorted(ts.GRAHA_IN_BHAVA), sorted((p, h) for p in PLANETS8 for h in range(1, 13)))
        for k, (src, text) in ts.GRAHA_IN_BHAVA.items():
            self.assertRegex(src, SRC, k)
            self.assertTrue(text.strip(), k)

    def test_decks_per_planet(self):
        deck = {"Moon": "S23-2024", "Mars": "S23-2024", "Mercury": "S23-2024", "Jupiter": "S24", "Venus": "S24",
                "Saturn": "S25", "Rahu": "S25", "Ketu": "S25"}
        for (p, h), (src, _) in ts.GRAHA_IN_BHAVA.items():
            self.assertTrue(src.startswith(deck[p] + " "), (p, h, src))

    def test_no_editorial_marks_left(self):
        for text in self._all_texts():
            self.assertNotIn("[", text, text[:80])
            self.assertNotIn(" ,", text, text[:80])
            self.assertNotIn(" .", text, text[:80])

    def test_bhava_nature_rows(self):
        general = [r for r in ts.BHAVA_NATURE if r[0] is None]
        self.assertEqual(sorted(r[1] for r in general), ["benefic", "malefic"])
        self.assertEqual({r[0] for r in ts.BHAVA_NATURE if r[0]}, set(range(1, 13)))
        self.assertEqual(sorted((r[0], r[2]) for r in ts.BHAVA_NATURE if r[2]),
                         [(3, "Saturn"), (4, "Ketu"), (7, "Mars"), (10, "Saturn")])
        for r in ts.BHAVA_NATURE:
            self.assertIn(r[1], ("benefic", "malefic", "any"))
            self.assertRegex(r[4], SRC)
            self.assertNotRegex(r[3], r"^(Jupiter|Mars|Venus|Mercury|Moon) a (benefic|malefic)")   # R11 generalised

    def test_lord_in_rows(self):
        keys = [(r[0], r[1], r[2], r[3]) for r in ts.LORD_IN]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual({(a, b) for a, b, c, x in keys if a == 1 and c == "" and not x}, {(1, h) for h in range(1, 13)})
        self.assertIn((1, 6, "strong", False), keys)
        self.assertIn((1, 6, "weak", False), keys)
        self.assertIn((1, 8, "strong", False), keys)
        self.assertIn((4, 11, "", True), keys)
        for k in ((3, 3), (7, 10), (10, 7)):
            self.assertIn(k + ("", False), keys)
        for r in ts.LORD_IN:
            self.assertRegex(r[5], SRC)

    def test_life_areas(self):
        self.assertEqual([r[0] for r in ts.LIFE_AREAS], list(range(1, 17)))
        by = {r[0]: r for r in ts.LIFE_AREAS}
        self.assertEqual(by[11][3:5], (("Venus",), "Mars"))
        self.assertEqual(by[15][2:4], ((9, 12), ("Rahu",)))
        self.assertEqual(by[16][2:6], ((5, 7), ("Mercury", "Ketu"), "", "PAC"))
        self.assertEqual(by[8][1:4], ("Mother", (4,), ("Moon",)))

    def test_conditions_unique_and_known(self):
        import build_session23 as b23
        keys = [(k, p, h) for k, p, h, _, _ in ts.CONDITIONS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue({k for k, *_ in ts.CONDITIONS} <= set(b23.CONDITION_KEYS) | {"twelfth_house"})
        # S24 says where a man meets his wife for Venus in these houses only (pp.19-36)
        self.assertEqual(sorted(h for k, p, h, *_ in ts.CONDITIONS if k == "venus_meets_wife"), [3, 4, 5, 6, 8, 9, 10, 11, 12])
        for r in ts.CONDITIONS:
            self.assertRegex(r[4], SRC)

    def test_aspect_meanings(self):
        jup = [(r[2], r[1]) for r in ts.ASPECT_MEANING if r[0] == "Jupiter" and r[2]]
        self.assertEqual(sorted(jup), sorted((h, a) for h in range(1, 13) for a in (5, 7, 9)))
        self.assertIn(("any", None, None), [r[:3] for r in ts.ASPECT_MEANING])

    def test_remedies(self):
        topics = [r[0] for r in ts.REMEDIES]
        self.assertEqual(topics.count("Moon"), 8)
        self.assertEqual(topics.count("Tip"), 3)
        self.assertIn("Mercury", topics)
        self.assertIn("Saturn", topics)

    def _all_texts(self):
        yield from (t for _, t in ts.GRAHA_IN_BHAVA.values())
        for rows, i in ((ts.BHAVA_NATURE, 3), (ts.LORD_IN, 4), (ts.GRAHA_RASHI, 2), (ts.ASPECT_MEANING, 3),
                        (ts.CONDITIONS, 3), (ts.REMEDIES, 1)):
            yield from (r[i] for r in rows)


if __name__ == "__main__":
    unittest.main()


class ExampleAndConditionText(unittest.TestCase):
    """Review fixes: worked-example sentences are labelled; a conditional sentence is not also in its own card's text."""

    def test_s27_example_rows_are_labelled(self):
        for a, b, c, x, text, src in ts.LORD_IN:
            if src.startswith("S27") or "; S27" in src:
                self.assertIn("In her example chart (S27)", text, (a, b, c, x))
        for key, p, h, text, src in ts.CONDITIONS:
            if src.startswith("S27"):
                self.assertIn("In her example chart (S27)", text, key)

    def test_condition_sentence_not_repeated_in_the_same_card(self):
        for key, p, h, text, src in ts.CONDITIONS:
            for (planet, house), (_, cell) in ts.GRAHA_IN_BHAVA.items():
                if (p is None or p == planet) and (h is None or h == house):
                    self.assertNotIn(text, cell, (key, planet, house))
