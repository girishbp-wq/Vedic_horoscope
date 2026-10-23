"""make_vsop87.py: which VSOP87D terms it keeps, and that it rewrites only its own block in index.html."""
import pathlib
import re
import tempfile
import unittest

import make_vsop87

HERE = pathlib.Path(__file__).resolve().parent


def _header(var, power, n):
    return (f" VSOP87 VERSION D4    MERCURY   VARIABLE {var} (LBR)       *T**{power}   {n:4d} TERMS    "
            "HELIOCENTRIC DYNAMICAL ECLIPTIC AND EQUINOX OF THE DATE")


def _term(a, b, c):
    return f" 4110    1  0  0  0  0  0  0  0  0  0  0  0  0  0.00000000000  0.0  0.0 {a} {b} {c}"


class ReadSeries(unittest.TestCase):
    def setUp(self):
        lines = [_header(1, 0, 3), _term("4.40250710144", "0.00000000000", "0.00000000000"),
                 _term("0.00000010000", "1.50000000000", "26087.90314157420"),       # 1e-7 at t^0: kept
                 _term("0.00000009999", "2.00000000000", "52175.80628314840"),       # just under: dropped
                 _header(1, 1, 2), _term("26087.90313685529", "0.00000000000", "0.00000000000"),
                 _term("0.00000030000", "1.00000000000", "10.00000000000"),          # 3e-7 x 0.3 < 1e-7: dropped
                 _header(2, 0, 1), _term("0.00000005000", "1.00000000000", "1.00000000000"),   # all B dropped
                 _header(3, 0, 1), _term("0.39528271651", "0.00000000000", "0.00000000000")]
        self.path = pathlib.Path(tempfile.mkdtemp()) / "VSOP87D.mer"
        self.path.write_text("\n".join(lines) + "\n")

    def test_keeps_terms_by_amplitude_times_point_three_to_the_power(self):
        s = make_vsop87.read_series(self.path)
        self.assertEqual(s["L"], [["4.40250710144", "0", "0", "0.0000001", "1.5", "26087.9031415742"],
                                  ["26087.90313685529", "0", "0"]])
        self.assertEqual(s["B"], [])
        self.assertEqual(s["R"], [["0.39528271651", "0", "0"]])


class WriteBlock(unittest.TestCase):
    def test_rewrites_only_its_own_block(self):
        page = "a\n/* EPHEMERIS-START */ x /* EPHEMERIS-END */\nb\n"
        once = make_vsop87.write(page, f"{make_vsop87.START}\nONE\n{make_vsop87.END}")
        twice = make_vsop87.write(once, f"{make_vsop87.START}\nTWO\n{make_vsop87.END}")
        self.assertEqual(twice, "a\n/* EPHEMERIS-START */ x /* EPHEMERIS-END */\n"
                                f"{make_vsop87.START}\nTWO\n{make_vsop87.END}\nb\n")

    def test_the_page_carries_the_six_bodies_outside_the_workbook_block(self):
        page = (HERE / "index.html").read_text(encoding="utf-8")
        i, j = page.index(make_vsop87.START), page.index(make_vsop87.END)
        self.assertGreater(i, page.index("/* EPHEMERIS-END */"))
        block = page[i:j]
        self.assertEqual(re.findall(r"^  (\w+):\{L:", block, re.M), ["Earth", "Mercury", "Venus", "Mars", "Jupiter",
                                                                     "Saturn"])
        self.assertIn("/* 2662 terms */", block)


if __name__ == "__main__":
    unittest.main()
