"""Unit tests for ashtakavarga.py (run: python3 -m unittest -v)."""
import contextlib
import copy
import io
import random
import unittest

import ashtakavarga as av

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
CONTRIBUTORS = PLANETS + ["Lagna"]

# Classical per-planet totals (Parashara) and the grand total.
EXPECTED = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
            "Jupiter": 56, "Venus": 52, "Saturn": 39}

GOLDEN = {  # BPHS ch.66, R. Santhanam translation; cross-checked row by row on 2026-10-07
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 9, 10, 11],
        "Mars": [2, 3, 5, 6, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 2, 4, 7, 8, 10, 11],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 4, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

ALL_ARIES = {p: 0 for p in CONTRIBUTORS}


def chart(**kw):
    c = dict(ALL_ARIES)
    c.update({k.capitalize(): v for k, v in kw.items()})
    return c


class RuleTables(unittest.TestCase):
    def test_every_target_has_all_eight_contributors(self):
        self.assertEqual(sorted(av.RULES), sorted(PLANETS))
        for p in PLANETS:
            self.assertEqual(sorted(av.RULES[p]), sorted(CONTRIBUTORS), p)

    def test_each_planet_total_matches_classical_value(self):
        for p, want in EXPECTED.items():
            got = sum(len(av.RULES[p][c]) for c in CONTRIBUTORS)
            self.assertEqual(got, want, p)

    def test_grand_total_is_337(self):
        self.assertEqual(sum(EXPECTED.values()), 337)
        self.assertEqual(av.SAV_TOTAL, 337)

    def test_every_row_matches_the_golden_bphs_table(self):
        for target, row in GOLDEN.items():
            for contributor, houses in row.items():
                self.assertEqual(sorted(av.RULES[target][contributor]), houses,
                                 f"{target} <- {contributor}")

    def test_moon_rows_follow_the_bphs_text_and_the_uploaded_reference_file(self):
        self.assertEqual(sorted(av.RULES["Moon"]["Moon"]), [1, 3, 6, 7, 9, 10, 11])
        self.assertEqual(sorted(av.RULES["Moon"]["Mars"]), [2, 3, 5, 6, 10, 11])
        self.assertEqual(sorted(av.RULES["Moon"]["Jupiter"]), [1, 2, 4, 7, 8, 10, 11])

    def test_alternate_moon_recension_is_a_valid_table_differing_in_exactly_three_rows(self):
        alt = {**av.RULES, "Moon": av.RULES_MOON_COMMON}
        av.validate_rules(alt)
        differing = [c for c in CONTRIBUTORS
                     if sorted(av.RULES["Moon"][c]) != sorted(av.RULES_MOON_COMMON[c])]
        self.assertEqual(differing, ["Moon", "Mars", "Jupiter"])
        self.assertEqual(sorted(av.RULES_MOON_COMMON["Moon"]), [1, 3, 6, 7, 10, 11])
        self.assertEqual(sorted(av.RULES_MOON_COMMON["Mars"]), [2, 3, 5, 6, 9, 10, 11])
        self.assertEqual(sorted(av.RULES_MOON_COMMON["Jupiter"]), [1, 4, 7, 8, 10, 11, 12])
        r = av.compute(ALL_ARIES, rules=alt)
        self.assertEqual(sum(r["bav"]["Moon"]), 49)
        self.assertEqual(sum(r["sav"]), 337)

    def test_houses_are_unique_and_in_range(self):
        for p in PLANETS:
            for c in CONTRIBUTORS:
                h = list(av.RULES[p][c])
                self.assertEqual(len(h), len(set(h)), (p, c))
                self.assertTrue(all(1 <= x <= 12 for x in h), (p, c))

    def test_validate_rules_accepts_the_shipped_tables(self):
        av.validate_rules(av.RULES)  # must not raise

    def test_validate_rules_rejects_a_table_that_fails_its_checksum(self):
        bad = copy.deepcopy(av.RULES)
        bad["Mars"]["Sun"] = tuple(bad["Mars"]["Sun"][:-1])
        with self.assertRaisesRegex(av.AshtakavargaError, "Mars"):
            av.validate_rules(bad)

    def test_validate_rules_rejects_out_of_range_house(self):
        bad = copy.deepcopy(av.RULES)
        bad["Sun"]["Moon"] = (3, 6, 10, 13)
        with self.assertRaises(av.AshtakavargaError):
            av.validate_rules(bad)


class BinduSigns(unittest.TestCase):
    def test_wraps_past_pisces(self):
        # Lagna in Pisces (11) gives the Sun houses 3,4,6,10,11,12 ->
        # signs 1,2,4,8,9,10 (Taurus, Gemini, Leo, Sagittarius, Capricorn, Aquarius)
        self.assertEqual(av.bindu_signs("Sun", "Lagna", 11), [1, 2, 4, 8, 9, 10])

    def test_house_one_is_the_contributors_own_sign(self):
        self.assertIn(4, av.bindu_signs("Sun", "Sun", 4))
        self.assertNotIn(4, av.bindu_signs("Sun", "Moon", 4))


class Compute(unittest.TestCase):
    def test_hand_computed_sun_bav_with_everything_in_aries(self):
        # Counted by hand from the Sun table: for each house 1..12, how many of the
        # eight contributors list that house.
        hand = [3, 3, 3, 4, 2, 5, 4, 3, 5, 6, 7, 3]
        self.assertEqual(sum(hand), 48)
        self.assertEqual(av.compute(ALL_ARIES)["bav"]["Sun"], hand)

    def test_sav_is_the_column_sum_of_the_seven_bavs(self):
        r = av.compute(chart(sun=3, moon=7, mars=10, lagna=5))
        for s in range(12):
            self.assertEqual(r["sav"][s], sum(r["bav"][p][s] for p in PLANETS))

    def test_totals_never_depend_on_the_chart(self):
        rng = random.Random(337)
        for _ in range(1000):
            c = {k: rng.randrange(12) for k in CONTRIBUTORS}
            r = av.compute(c)
            for p in PLANETS:
                self.assertEqual(sum(r["bav"][p]), EXPECTED[p], (p, c))
                self.assertTrue(all(0 <= v <= 8 for v in r["bav"][p]), (p, c))
            self.assertEqual(sum(r["sav"]), 337, c)

    def test_rotating_the_whole_chart_rotates_every_result(self):
        base = chart(sun=1, moon=9, mars=4, mercury=2, jupiter=11, venus=6,
                     saturn=8, lagna=3)
        r0 = av.compute(base)
        for k in (1, 5, 11):
            rk = av.compute({n: (s + k) % 12 for n, s in base.items()})
            for p in PLANETS:
                self.assertEqual(rk["bav"][p], r0["bav"][p][-k:] + r0["bav"][p][:-k])
            self.assertEqual(rk["sav"], r0["sav"][-k:] + r0["sav"][:-k])

    def test_rejects_missing_contributor(self):
        c = dict(ALL_ARIES)
        del c["Lagna"]
        with self.assertRaisesRegex(av.AshtakavargaError, "Lagna"):
            av.compute(c)

    def test_rejects_sign_outside_0_to_11(self):
        for bad in (12, -1, 3.5, "Aries", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(av.AshtakavargaError):
                    av.compute(chart(sun=bad))

    def test_rejects_unknown_contributor(self):
        c = dict(ALL_ARIES)
        c["Rahu"] = 3
        with self.assertRaisesRegex(av.AshtakavargaError, "Rahu"):
            av.compute(c)


class Cli(unittest.TestCase):
    def run_cli(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = av.main(argv)
        return code, out.getvalue()

    def test_prints_sav_total_for_a_chart_given_by_sign_names(self):
        code, out = self.run_cli(
            ["--lagna", "Leo", "--sun", "Aries", "--moon", "Cancer", "--mars", "0",
             "--mercury", "0", "--jupiter", "Sagittarius", "--venus", "1",
             "--saturn", "Capricorn"])
        self.assertEqual(code, 0)
        self.assertIn("SAV", out)
        self.assertIn("337", out)

    def test_json_output_round_trips_compute(self):
        import json
        code, out = self.run_cli(["--json"] + [a for p in CONTRIBUTORS
                                              for a in (f"--{p.lower()}", "0")])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), av.compute(ALL_ARIES))

    def test_bad_sign_exits_nonzero(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = av.main(["--lagna", "Zebra"] + [a for p in PLANETS
                                                  for a in (f"--{p.lower()}", "0")])
        self.assertNotEqual(code, 0)
        self.assertIn("Zebra", err.getvalue())


if __name__ == "__main__":
    unittest.main()
