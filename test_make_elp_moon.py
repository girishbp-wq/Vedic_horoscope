"""make_elp_moon.py: the fit it applies, which terms it keeps, and that it rewrites only its own block in index.html."""
import pathlib
import re
import tempfile
import unittest

import make_elp_moon

HERE = pathlib.Path(__file__).resolve().parent


def _write(folder, name, rows):
    (folder / name).write_text(f"{len(rows)}\n" + "\n".join("  ".join(map(str, r)) for r in rows) + "\n")


class ReadSeries(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        _write(self.dir, "elp_main.long", [[0, 0, 1, 0, 0.1, 0, 0, 0, 0, 0, 0],      # kept, no B: A as it is
                                           [0, 2, 0, 0, 1e-8, 0, 0, 0, 0, 0, 0],      # under 2e-8: dropped
                                           [2, 0, -1, 0, 0.01, 1, 0, 0, 0, 0, 0]])    # B1 carries the fit
        _write(self.dir, "elp_main.dist", [[0, 0, 0, 0, 385000.5, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 29.0, 0, 0, 0, 0, 0, 0]])
        zeros = [0] * 13
        _write(self.dir, "elp_pert.longT0", [zeros + [3e-8, 0.5], zeros + [1e-8, 0.5]])
        _write(self.dir, "elp_pert.longT1", [zeros + [1.5e-8, 1.0]])     # 1.5e-8 x 2 >= 2e-8: kept
        _write(self.dir, "elp_pert.longT2", [zeros + [4e-9, 1.0]])       # 4e-9 x 4 < 2e-8: dropped
        _write(self.dir, "elp_pert.longT3", [zeros + [1e-9, 1.0]])

    def test_keeps_terms_by_amplitude_and_applies_the_fit(self):
        lon, pert, dist = make_elp_moon.series(self.dir)
        fb, fa = make_elp_moon.amplitude_factors()
        self.assertEqual([t[:4] for t in lon], [[0, 0, 1, 0], [2, 0, -1, 0]])
        self.assertEqual(lon[0][4], 0.1)
        self.assertAlmostEqual(lon[1][4], 0.01 + fb[0], places=15)
        self.assertEqual([len(g) for g in pert], [1, 1])                  # the empty T^2 and T^3 groups go
        self.assertEqual(len(dist), 1)
        self.assertAlmostEqual(dist[0][4], 385000.5 * fa, places=6)


class WriteBlock(unittest.TestCase):
    def test_rewrites_only_its_own_block_after_the_planets(self):
        page = "a\n/* VSOP87-START */ x /* VSOP87-END */\nb\n"
        once = make_elp_moon.write(page, f"{make_elp_moon.START}\nONE\n{make_elp_moon.END}")
        twice = make_elp_moon.write(once, f"{make_elp_moon.START}\nTWO\n{make_elp_moon.END}")
        self.assertEqual(twice, "a\n/* VSOP87-START */ x /* VSOP87-END */\n"
                                f"{make_elp_moon.START}\nTWO\n{make_elp_moon.END}\nb\n")

    def test_the_page_carries_the_moon_block(self):
        page = (HERE / "index.html").read_text(encoding="utf-8")
        i, j = page.index(make_elp_moon.START), page.index(make_elp_moon.END)
        self.assertGreater(i, page.index("/* VSOP87-END */"))
        block = page[i:j]
        self.assertEqual(re.findall(r"^  (\w+):", block, re.M), ["args", "planets", "lon", "pert", "dist"])
        self.assertIn("/* 780 longitude terms */", block)


if __name__ == "__main__":
    unittest.main()
