"""Browser tests for the October 2026 audit fixes in index.html.

Each test drives the real page in headless Chromium (Playwright via node) and
reads what the page computes or renders. Network access is blocked: the page
only loads from file://.

Run:  python3 -m unittest test_page_fixes
"""
import json
import os
import pathlib
import shutil
import subprocess
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
INDEX = pathlib.Path(os.environ.get("VH_INDEX", HERE / "index.html"))
NODE = shutil.which("node")


def _playwright_module():
    npm = shutil.which("npm")
    if not npm:
        return None
    root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True).stdout.strip()
    cand = pathlib.Path(root) / "playwright"
    return str(cand) if cand.exists() else None


PW_MODULE = _playwright_module() if NODE else None
BROWSERS = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")

RUNNER = r"""
const { chromium } = require(process.env.PW_MODULE);
const indexUrl = 'file://' + process.argv[1];
const opts = JSON.parse(process.argv[2]);
const scenario = new Function('page', 'opts', 'return (async () => {' + process.argv[3] + '})();');
(async () => {
  const browser = await chromium.launch({headless: true});
  const ctx = await browser.newContext({viewport: {width: 1280, height: 900},
                                        timezoneId: opts.timezoneId || 'Asia/Kolkata'});
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const page = await ctx.newPage();
  const jsErrors = [];
  page.on('pageerror', e => jsErrors.push(String(e)));
  if (opts.clock) await page.clock.install({time: new Date(opts.clock)});
  if (opts.storage) await page.addInitScript(s => { localStorage.setItem('vh_form_v1', s); }, JSON.stringify(opts.storage));
  await page.goto(indexUrl);
  const result = await scenario(page, opts);
  console.log(JSON.stringify({result, jsErrors}));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""

# Helpers available to every scenario (prepended to its body).
PRELUDE = r"""
const pickCity = async (name) => {
  await page.fill('#f-place', '');
  await page.type('#f-place', name);
  await page.waitForSelector('#suggestions.show');
  await page.evaluate(n => {
    const d = [...document.querySelectorAll('#suggestions div[data-idx]')].find(x => x.firstChild.textContent.trim() === n);
    d.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
  }, name);
};
const setBirth = async (dob, tob) => {
  await page.fill('#f-dob', dob);
  await page.fill('#f-tob', tob);
};
const generate = async () => {
  await page.click('#btn-generate');
  await page.waitForSelector('#report.show');
};
"""


def run_page(body, **opts):
    env = dict(os.environ, PW_MODULE=PW_MODULE)
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", BROWSERS)
    p = subprocess.run([NODE, "-e", RUNNER, str(INDEX), json.dumps(opts), PRELUDE + textwrap.dedent(body)],
                       capture_output=True, text=True, timeout=180, env=env)
    if p.returncode != 0:
        raise AssertionError(f"browser run failed:\n{p.stderr[-3000:]}")
    out = json.loads(p.stdout.strip().splitlines()[-1])
    if out["jsErrors"]:
        raise AssertionError(f"page errors: {out['jsErrors']}")
    return out["result"]


needs_browser = unittest.skipUnless(PW_MODULE and os.path.isdir(BROWSERS),
                                    "playwright + chromium not available — browser test skipped")


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


@needs_browser
class CityTimeZones(unittest.TestCase):
    """The UTC offset comes from the city's IANA zone on the birth date."""

    def test_offset_follows_the_birth_date(self):
        r = run_page("""
            const out = {};
            await pickCity('London');
            await setBirth('1990-07-15', '10:00');
            out.londonSummer = await page.inputValue('#f-tz');
            await setBirth('1990-01-15', '10:00');
            out.londonWinter = await page.inputValue('#f-tz');
            await pickCity('Kolkata');
            await setBirth('1943-06-01', '10:00');
            out.kolkataWar = await page.inputValue('#f-tz');
            await setBirth('1950-06-01', '10:00');
            out.kolkata1950 = await page.inputValue('#f-tz');
            await pickCity('New York');
            await setBirth('1990-07-04', '09:00');
            out.nySummer = await page.inputValue('#f-tz');
            out.hint = await page.textContent('#place-hint');
            return out;
        """)
        self.assertEqual(r["londonSummer"], "1")
        self.assertEqual(r["londonWinter"], "0")
        self.assertEqual(r["kolkataWar"], "6.5")
        self.assertEqual(r["kolkata1950"], "5.5")
        self.assertEqual(r["nySummer"], "-4")
        self.assertIn("America/New_York", r["hint"])
        self.assertIn("UTC−4", r["hint"])
        self.assertIn("daylight saving", r["hint"])

    def test_typed_place_does_not_reuse_previous_city_offset(self):
        r = run_page("""
            await setBirth('1990-07-15', '10:00');
            await pickCity('London');
            const londonTz = await page.inputValue('#f-tz');
            await page.fill('#f-place', 'Bengaluru');      // typed, no suggestion picked
            await generate();
            return {londonTz, summary: await page.textContent('#r-meta'),
                    tz: await page.inputValue('#f-tz')};
        """)
        self.assertEqual(r["londonTz"], "1")
        self.assertEqual(r["tz"], "5.5")
        self.assertIn("Bengaluru, Karnataka, India (UTC+5:30)", r["summary"])

    def test_typed_offset_overrides_until_another_city_is_picked(self):
        r = run_page("""
            await setBirth('1990-01-15', '10:00');
            await pickCity('London');
            await page.fill('#f-tz', '2');
            await generate();
            const first = await page.textContent('#r-meta');
            await setBirth('1990-01-16', '10:00');        // date change keeps the typed value
            const kept = await page.inputValue('#f-tz');
            await pickCity('Paris');
            return {first, kept, paris: await page.inputValue('#f-tz')};
        """)
        self.assertIn("London, UK (UTC+2)", r["first"])
        self.assertEqual(r["kept"], "2")
        self.assertEqual(r["paris"], "1")

    def test_chart_uses_daylight_saving_offset(self):
        # 10:00 BST in July is 09:00 UT: the same chart as manual entry with offset 1.
        r = run_page("""
            await setBirth('1990-07-15', '10:00');
            await pickCity('London');
            await generate();
            const auto = await page.evaluate(() => currentChart.chart.sidereal.Moon);
            await page.click('#btn-manual');
            await page.fill('#f-lat', '51.5074'); await page.press('#f-lat', 'Tab');
            await page.fill('#f-lon', '-0.1278'); await page.press('#f-lon', 'Tab');
            await page.fill('#f-tz', '1');
            await generate();
            return {auto, manual: await page.evaluate(() => currentChart.chart.sidereal.Moon)};
        """)
        self.assertAlmostEqual(r["auto"], r["manual"], places=6)

    def test_saved_form_from_older_build_gets_the_zone(self):
        old = {"dob": "1990-07-15", "tob": "10:00", "place": "London", "tz": "0",
               "selectedCity": ["London", "UK", 51.5074, -0.1278, 0]}
        r = run_page("""
            return {tz: await page.inputValue('#f-tz'), city: await page.evaluate(() => selectedCity)};
        """, storage=old)
        self.assertEqual(r["tz"], "1")
        self.assertEqual(r["city"][5], "Europe/London")


@needs_browser
class MuhurtaUsesCityClock(unittest.TestCase):
    """Muhūrta panes show the selected city's clock, not the device's."""

    def test_sunrise_in_city_time_on_a_device_elsewhere(self):
        r = run_page("""
            await page.selectOption('#f-curcity', {label: 'Bengaluru — Karnataka, India'});
            await page.fill('#f-curdate', '2026-03-21');
            await page.dispatchEvent('#f-curdate', 'change');
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return {pan: await page.evaluate(() => { computeMhPanchanga(); return document.getElementById('mh-panchanga').textContent; }),
                    chog: await page.evaluate(() => document.getElementById('choghadiya-body').textContent),
                    rk: await page.evaluate(() => document.getElementById('pane-rahukaal').textContent)};
        """, timezoneId="America/New_York")
        import re
        rise = re.search(r"Sunrise\s*(\d\d:\d\d)", r["pan"]).group(1)
        self.assertTrue(6 * 60 + 15 <= _minutes(rise) <= 6 * 60 + 35, rise)   # ~06:24 IST
        self.assertIn("UTC+5:30", r["pan"])
        rise_c = re.search(r"Sunrise\s*(\d\d:\d\d)", r["chog"]).group(1)
        self.assertEqual(rise, rise_c)
        # 21 Mar 2026 is a Saturday: Rāhu Kāla is the 3rd eighth of the day, not 09:00–10:30.
        self.assertIn("Bengaluru, 21-03-2026 (Saturday)", r["rk"])
        m = re.search(r"between\s+(\d\d:\d\d)\s+and\s+(\d\d:\d\d)", r["rk"])
        start, end = _minutes(m.group(1)), _minutes(m.group(2))
        self.assertTrue(abs(start - (_minutes(rise) + 2 * 90)) <= 3, m.group(0))
        self.assertTrue(85 <= end - start <= 95)

    def test_rahu_kaal_follows_long_summer_days(self):
        r = run_page("""
            await page.selectOption('#f-curcity', {label: 'London — UK'});
            await page.fill('#f-curdate', '2026-06-22');
            await page.dispatchEvent('#f-curdate', 'change');
            return await page.evaluate(() => { renderRahukaalPane(); const p = document.getElementById('pane-rahukaal');
                return {text: p.textContent, rows: [...p.querySelectorAll('tbody tr')].map(tr => tr.firstChild.textContent)}; });
        """)
        import re
        m = re.search(r"between\s+(\d\d:\d\d)\s+and\s+(\d\d:\d\d)", r["text"])
        # Monday 22 Jun 2026, London: sunrise ~04:43 BST, sunset ~21:21 → 2nd eighth ≈ 06:48–08:53.
        self.assertTrue(abs(_minutes(m.group(1)) - (6 * 60 + 48)) <= 5, m.group(0))
        self.assertTrue(abs(_minutes(m.group(2)) - (8 * 60 + 53)) <= 5, m.group(0))
        self.assertEqual(r["rows"][0], "22-06-2026")
        self.assertEqual(len(r["rows"]), 7)

    def test_before_sunrise_highlights_previous_night(self):
        body = """
            await page.selectOption('#f-curcity', {label: 'Bengaluru — Karnataka, India'});
            await page.fill('#f-curdate', opts.date);
            await page.dispatchEvent('#f-curdate', 'change');
            return await page.evaluate(() => {
              computeChoghadiya();
              const b = document.getElementById('choghadiya-body');
              return {now: [...b.querySelectorAll('tr.now')].map(tr => tr.textContent), text: b.textContent};
            });
        """
        today = run_page(body, clock="2026-03-21T03:00:00+05:30", date="2026-03-21")
        self.assertEqual(today["now"], [])
        self.assertIn("before sunrise", today["text"])
        yesterday = run_page(body, clock="2026-03-21T03:00:00+05:30", date="2026-03-20")
        self.assertEqual(len(yesterday["now"]), 1)
        self.assertNotIn("before sunrise", yesterday["text"])

    def test_char_is_neutral_everywhere(self):
        r = run_page("""
            return await page.evaluate(() => { computeChoghadiya(); return document.getElementById('choghadiya-body').textContent; });
        """)
        self.assertIn("Neutral: Char", r)
        self.assertNotIn("Labh, Char", r)


# Reference values from the Swiss Ephemeris 2.10 (pyswisseph, Moshier ephemeris):
# get_ayanamsa_ut for SIDM_LAHIRI / SIDM_RAMAN / SIDM_KRISHNAMURTI_VP291, deltat, and
# sidereal (Lahiri) Sun and Moon from calc_ut. STATIONS: Mercury, Venus and Mars 0.35
# day either side of each station from 2000 on, with the sign of the true speed.
SWE = json.loads('{"ayan_jd": [2415020.5, 2433282.5, 2444239.5, 2451545.0, 2460676.5, 2469807.5], "ayan_lahiri": [22.4605306, 23.1587251, 23.5777079, 23.8570924, 24.2063431, 24.5556131], "ayan_raman": [21.0142291, 21.7124238, 22.1314066, 22.410791, 22.7600418, 23.1093118], "ayan_kp": [22.3838085, 23.0820007, 23.5009818, 23.780365, 24.1296141, 24.4788823], "dt": [[2415020.5, -1.99], [2433282.5, 28.93], [2444239.5, 50.54], [2451545.0, 63.83], [2460676.5, 69.0], [2469807.5, 74.58]], "pos": [[2441974.158, 181.62544, 87.94615], [2453160.4725, 49.77283, 241.09253], [2446795.1125, 254.93125, 247.47757], [2455340.6794, 38.90751, 170.92122], [2456136.9341, 101.71102, 219.01324], [2435675.9416, 95.36377, 259.54222], [2433763.4609, 12.71796, 262.36153], [2463871.0582, 163.37517, 240.1017], [2442755.4054, 232.65889, 303.87252], [2441841.4384, 53.51902, 144.20173], [2469648.4276, 98.85495, 56.23725], [2450458.8746, 266.34928, 283.11322]], "stations": [["Mercury", 2451595.68227, false], ["Mercury", 2451596.38227, true], ["Mercury", 2451618.01069, true], ["Mercury", 2451618.71069, false], ["Mercury", 2451718.50555, false], ["Mercury", 2451719.20555, true], ["Mercury", 2451742.70583, true], ["Mercury", 2451743.40583, false], ["Mercury", 2451835.7202, false], ["Mercury", 2451836.4202, true], ["Mercury", 2451856.25286, true], ["Mercury", 2451856.95286, false], ["Venus", 2451977.19623, false], ["Venus", 2451977.89623, true], ["Venus", 2452019.34037, true], ["Venus", 2452020.04037, false], ["Venus", 2452557.92443, false], ["Venus", 2452558.62443, true], ["Venus", 2452599.45046, true], ["Venus", 2452600.15046, false], ["Venus", 2453143.08633, false], ["Venus", 2453143.78633, true], ["Venus", 2453186.11892, true], ["Venus", 2453186.81892, false], ["Mars", 2452040.82241, false], ["Mars", 2452041.52241, true], ["Mars", 2452110.09822, true], ["Mars", 2452110.79822, false], ["Mars", 2452849.46732, false], ["Mars", 2452850.16732, true], ["Mars", 2452909.47796, true], ["Mars", 2452910.17796, false], ["Mars", 2453645.06906, false], ["Mars", 2453645.76906, true], ["Mars", 2453714.31895, true], ["Mars", 2453715.01895, false]]}')


@needs_browser
class Astronomy(unittest.TestCase):
    """Ayanamsa, ΔT, Sun/Moon and retrograde flags against the Swiss Ephemeris."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            return await page.evaluate((g) => ({
              ayan: Object.fromEntries(['lahiri','raman','kp'].map(a => [a, g.ayan_jd.map(j => ayanamsa(j, a))])),
              dt: g.dt.map(([j]) => deltaTSeconds(j)),
              pos: g.pos.map(([j]) => { const c = computeChart(j, 'lahiri').sidereal; return [c.Sun, c.Moon]; }),
              retro: g.stations.map(([p, j]) => retrogradeSet(j, 'lahiri').has(p)),
            }), opts.g);
        """, g=SWE)

    def test_ayanamsa_matches_swiss_ephemeris(self):
        for mode in ("lahiri", "raman", "kp"):
            for got, want in zip(self.r["ayan"][mode], SWE["ayan_" + mode]):
                self.assertAlmostEqual(got, want, delta=1 / 3600, msg=mode)   # within 1"

    def test_delta_t(self):
        for got, (_, want) in zip(self.r["dt"], SWE["dt"]):
            self.assertAlmostEqual(got, want, delta=1.0)

    def test_sun_and_moon_positions(self):
        for (sun, moon), (_, want_sun, want_moon) in zip(self.r["pos"], SWE["pos"]):
            self.assertAlmostEqual(((sun - want_sun + 180) % 360) - 180, 0, delta=0.01)
            self.assertAlmostEqual(((moon - want_moon + 180) % 360) - 180, 0, delta=0.015)

    def test_retrograde_flag_near_stations(self):
        wrong = [(p, j, want) for (p, j, want), got in zip(SWE["stations"], self.r["retro"]) if got != want]
        self.assertEqual(wrong, [])


# A sidereal chart for renderKujaSection: whole-sign positions at mid-sign unless given.
def _sid(**signs_deg):
    base = {"Sun": 15, "Moon": 45, "Mars": 75, "Mercury": 105, "Jupiter": 135, "Venus": 165,
            "Saturn": 195, "Rahu": 225, "Ketu": 45}
    base.update(signs_deg)
    return base


KUJA = r"""
  return await page.evaluate((cases) => cases.map(c => {
    const pbr = {}; for (const p in c.sid) pbr[p] = rashiOf(c.sid[p]).n;
    renderKujaSection(pbr, c.lagna, c.dob || '2010-01-01', c.sid);
    const rows = [...document.querySelectorAll('#kuja-cancel tbody tr')].map(tr => [...tr.children].map(td => td.textContent));
    return {rows, verdict: document.getElementById('kuja-verdict').textContent};
  }), opts.cases);
"""


@needs_browser
class KujaDosha(unittest.TestCase):
    """Rules 1-4 of the teacher's list are read from the chart; 5 is for matching; 6 reduces."""

    def kuja(self, *cases):
        return run_page(KUJA, cases=list(cases))

    def status(self, r, n):
        return r["rows"][n - 1][1]

    def test_friends_house_cancels(self):
        # Lagna Mesha, Mars in Meena (Jupiter's, a friend) = 12th from Lagna: doṣa, cancelled by rule 1
        r, = self.kuja({"lagna": 1, "sid": _sid(Mars=345, Saturn=15, Moon=125)})
        self.assertEqual(self.status(r, 1), "✅ Cancelled")
        self.assertIn("Friend's House", r["rows"][0][2])
        self.assertIn("CANCELLED by rule 1", r["verdict"])

    def test_saturn_conjunction_and_aspects_cancel(self):
        # Lagna Vrishabha, Mars in Mithuna (Mercury's, an enemy) = 2nd: doṣa; Saturn decides
        got = {}
        for sat_sign, label in ((3, "conj"), (1, "3rd"), (9, "7th"), (6, "10th"), (2, "none")):
            r, = self.kuja({"lagna": 2, "sid": _sid(Mars=75, Saturn=(sat_sign - 1) * 30 + 10, Moon=125)})
            got[label] = (self.status(r, 2), r["verdict"])
        for label in ("conj", "3rd", "7th", "10th"):
            self.assertEqual(got[label][0], "✅ Cancelled", label)
            self.assertIn("CANCELLED by rule 2", got[label][1])
        self.assertEqual(got["none"][0], "❌ Not met")
        self.assertIn("not cancelled", got["none"][1])

    def test_exempt_birth_nakshatra_cancels(self):
        cases = [{"lagna": 2, "sid": _sid(Mars=75, Saturn=40, Moon=moon)} for moon in (3.0, 150.0, 140.0)]
        ashwini, uttara_phalguni, purva_phalguni = self.kuja(*cases)
        self.assertEqual(self.status(ashwini, 4), "✅ Cancelled")
        self.assertEqual(self.status(uttara_phalguni, 4), "✅ Cancelled")
        self.assertEqual(self.status(purva_phalguni, 4), "❌ Not met")
        self.assertIn("CANCELLED by rule 4", ashwini["verdict"])

    def test_no_dosha_is_reported_before_cancellations(self):
        # Mars in the 5th from Lagna, Venus and Moon: no doṣa, even though rule 3 (Simha Lagna) holds
        r, = self.kuja({"lagna": 5, "sid": _sid(Mars=255, Venus=255, Moon=255)})
        self.assertEqual(self.status(r, 3), "✅ Cancelled")
        self.assertIn("No Kuja Dosha detected", r["verdict"])

    def test_deep_exalted_mars_and_age(self):
        r, = self.kuja({"lagna": 4 + 0, "sid": _sid(Mars=270 + 28.2, Saturn=40, Moon=125), "dob": "1960-01-01"})
        self.assertIn("Deep Exalted", r["rows"][0][2])
        self.assertEqual(self.status(r, 6), "✅ Reduced")
        self.assertEqual(self.status(r, 5), "ℹ Check at matching")
        self.assertEqual(len(r["rows"]), 6)


@needs_browser
class DignityOnThePage(unittest.TestCase):
    """Dignity uses the degree everywhere; nodes have no rulership; Section II·b is filled."""

    @classmethod
    def setUpClass(cls):
        # A birth (UT) with the Moon at Vrishabha 4°-20°: exaltation sign but Moolatrikona by degree.
        cls.r = run_page("""
            const jd = await page.evaluate(() => {
              for (let j = 2451545.0; ; j += 0.25) { const m = computeChart(j, 'lahiri').sidereal.Moon; if (m > 40 && m < 48) return j; }
            });
            const d = new Date((jd - 2440587.5) * 86400000);
            const pad = n => String(n).padStart(2, '0');
            await page.click('#btn-manual');
            await page.fill('#f-lat', '51.5'); await page.press('#f-lat', 'Tab');
            await page.fill('#f-lon', '0'); await page.press('#f-lon', 'Tab');
            await page.fill('#f-tz', '0');
            await setBirth(`${d.getUTCFullYear()}-${pad(d.getUTCMonth()+1)}-${pad(d.getUTCDate())}`, `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}`);
            await generate();
            return await page.evaluate(() => {
              const moon = currentChart.chart.sidereal.Moon;
              return {
                moon,
                moonSection: document.getElementById('moon-kv').textContent + ' ' + document.getElementById('moon-narrative').textContent,
                southExaltedText: [...document.querySelectorAll('.south-chart .exalted')].map(e => e.textContent),
                classBody: document.getElementById('classification-body').textContent,
                rahu: planetDignity('Rahu', 7, 12), ketu: planetDignity('Ketu', 1, 12),
                rahuTaurus: planetDignity('Rahu', 2, 12).label,
                dignityBody: document.getElementById('dignity-body') ? document.getElementById('dignity-body').textContent : '',
              };
            });
        """)

    def test_moon_in_vrishabha_past_3_degrees_is_moolatrikona(self):
        self.assertTrue(40 < self.r["moon"] < 48)
        self.assertIn("Own (Moolatrikona)", self.r["moonSection"])
        self.assertNotIn("An exalted Moon gives", self.r["moonSection"])
        self.assertFalse(any(t.strip().startswith("Mo") for t in self.r["southExaltedText"]), self.r["southExaltedText"])

    def test_nodes_have_no_rulership(self):
        self.assertEqual(self.r["rahu"]["label"], "Node (no rulership)")
        self.assertEqual((self.r["rahu"]["flag"], self.r["rahu"]["bala"]), ("node", None))
        self.assertEqual(self.r["ketu"]["label"], "Node (no rulership)")
        self.assertEqual(self.r["rahuTaurus"], "Exalted")          # the teacher's exaltation sign still applies

    def test_section_two_b_is_rendered(self):
        body = self.r["classBody"]
        self.assertIn("Mukkoota", body)
        self.assertIn("Retrograde (Vakri) Grahas", body)
        self.assertIn("they and the Moon become combust within 5°", body)
        self.assertIn("Every ~13 months", body)


if __name__ == "__main__":
    unittest.main()
