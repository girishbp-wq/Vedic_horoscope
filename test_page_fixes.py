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
  await page.waitForFunction(n => [...document.querySelectorAll('#suggestions div[data-idx]')]
    .some(x => x.firstChild.textContent.trim() === n), name);       // built-in at once; online after a moment
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
// The current-location box: type a place and pick it from the suggestions, as for the birth place.
const pickCurCity = async (name) => {
  await page.fill('#f-curcity', '');
  await page.type('#f-curcity', name);
  await page.waitForFunction(n => [...document.querySelectorAll('#cur-suggestions div[data-idx]')]
    .some(x => x.firstChild.textContent.trim() === n), name);       // built-in at once; online after a moment
  await page.evaluate(n => {
    const d = [...document.querySelectorAll('#cur-suggestions div[data-idx]')].find(x => x.firstChild.textContent.trim() === n);
    d.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
  }, name);
};
// A stand-in for the online place search (Open-Meteo's GeoNames search): answers each query with the given places
// whose name starts with it, after an optional delay per query.
const mockGeo = async (places, delays = {}) => {
  const asked = [];
  await page.route('https://geocoding-api.open-meteo.com/**', async route => {
    const u = new URL(route.request().url()), q = (u.searchParams.get('name') || '').toLowerCase();
    asked.push(Object.fromEntries(u.searchParams));
    if (delays[q]) await new Promise(r => setTimeout(r, delays[q]));
    const results = places.filter(p => p.name.toLowerCase().startsWith(q));
    await route.fulfill({status: 200, contentType: 'application/json', headers: {'access-control-allow-origin': '*'},
                         body: JSON.stringify(results.length ? {results, generationtime_ms: 0.4} : {generationtime_ms: 0.4})});
  });
  return asked;
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
            await pickCurCity('Bengaluru');
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
            await pickCurCity('London');
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
            await pickCurCity('Bengaluru');
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


@needs_browser
class LabelsAndText(unittest.TestCase):
    """Node aspect names, ordinals, live Saturn dates, notes and reference text."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              const txt = id => document.getElementById(id).textContent;
              // Rahu in Karkataka: forward 5/9/12 = Vrischika, Meena, Mithuna; Sun in Meena, Moon in Mithuna
              renderAspectsSection({Sun:12, Moon:3, Mars:1, Mercury:1, Jupiter:1, Venus:1, Saturn:1, Rahu:4, Ketu:10});
              const aspects = txt('aspect-table') + ' ' + txt('aspect-influence');
              const now = new Date();
              const jd = julianDay(now.getUTCFullYear(), now.getUTCMonth()+1, now.getUTCDate(), 12);
              const jup = rashiOf(computeChart(jd, 'lahiri').sidereal.Jupiter).n;
              renderGurubalaSection(jup, 'lahiri');                       // Jupiter in the 1st from the Moon
              const guru1 = document.getElementById('gurubala-body') ? txt('gurubala-body') : document.body.textContent;
              renderGurubalaSection(jup % 12 + 1, 'lahiri');             // Jupiter in the 12th
              const guru12 = document.getElementById('gurubala-body') ? txt('gurubala-body') : document.body.textContent;
              renderPredictive();
              return {
                aspects, guru1, guru12,
                ord: [1,2,3,4,11,12,13,21,22,23].map(ord),
                nodeOrd: [5,9,12].map(h => aspectOrd('Rahu', h)), jupOrd: aspectOrd('Jupiter', 9),
                fmt: [fmtDeg(29.99999999), fmtDeg(10.5), fmtDeg(0)],
                sade: document.body.textContent.match(/Saturn has been in [^.]*\\./) ? document.body.textContent.match(/Saturn has been in [^.]*\\./)[0] : '',
                old29: document.body.textContent.includes('Saturn entered Meena (Pisces) on 29 Mar 2025'),
                ks: txt('pane-ksarpa'), combos: txt('pane-combos'),
                dasha: txt('s23-dasha-tables'),
                letters: GRAHA_REF.Mercury.deva, jupLetters: GRAHA_REF.Jupiter.deva,
                merc: GRAHA_ATTRS.Mercury, marsTransit: GRAHA_ATTRS.Mars.transit,
                aksharaNote: document.body.textContent.includes('beejakshari mantras are listed'),
                meanNode: txt('planet-narrative').includes('mean lunar nodes'),
                bm: Object.fromEntries(['Sun', 'Moon', 'Mercury', 'Mars', 'Jupiter'].map(p => [p, beneficMalefic(p)])),
              };
            });
        """)

    def test_session12_table_follows_s26(self):
        bm = self.r["bm"]
        self.assertEqual(bm["Sun"], "Mild malefic")
        self.assertEqual(bm["Mercury"], "Benefic (Shubha)")
        self.assertEqual(bm["Jupiter"], "Benefic (Shubha)")
        self.assertEqual(bm["Mars"], "Malefic (Papa)")
        self.assertTrue(bm["Moon"].startswith("Benefic (Shubha)"), bm["Moon"])
        self.assertIn("waxing", bm["Moon"])

    def test_node_aspects_are_named_anti_clockwise(self):
        self.assertEqual(self.r["nodeOrd"], ["9th (anti-clockwise)", "5th (anti-clockwise)", "2nd (anti-clockwise)"])
        self.assertEqual(self.r["jupOrd"], "9th")
        self.assertIn("2, 5, 9 (anti-clockwise)", self.r["aspects"])
        self.assertIn("Moon (2nd (anti-clockwise))", self.r["aspects"])
        self.assertNotIn("12th (anti-clockwise)", self.r["aspects"])
        self.assertIn("2nd/5th/9th aspect (counted anti-clockwise)", self.r["combos"])

    def test_ordinals(self):
        self.assertEqual(self.r["ord"], ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "23rd"])
        self.assertIn("1st house from your natal Moon", self.r["guru1"])
        self.assertIn("12th house from your natal Moon", self.r["guru12"])
        self.assertNotRegex(self.r["guru1"] + self.r["guru12"], r"\b(1|2|3|21|22)th\b")

    def test_saturn_dates_are_computed(self):
        self.assertFalse(self.r["old29"])
        self.assertRegex(self.r["sade"], r"Saturn has been in \w+ \(\w+\) since \d{1,2} \w{3} \d{4} and moves on around \d{1,2} \w{3} \d{4}\.")

    def test_kaala_sarpa_note_follows_session_18(self):
        self.assertIn("The Lagna is not considered (Session 18)", self.r["ks"])
        self.assertNotIn("(and the Lagna)", self.r["ks"])
        self.assertIn("in Rahu's rashi it is on the Rahu→Ketu side when its degree is higher than Rahu's", self.r["ks"])

    def test_degree_format_never_shows_60(self):
        self.assertEqual(self.r["fmt"], ["30° 00' 00\"", "10° 30' 00\"", "0° 00' 00\""])

    def test_dasha_balance_is_shown(self):
        self.assertRegex(self.r["dasha"], r"Balance at birth: \d+ y \d+ m \d+ d of \w+ mahādaśā")

    def test_reference_text(self):
        self.assertEqual(self.r["letters"], "ट ठ ड ढ ण")
        self.assertEqual(self.r["jupLetters"], "त थ द ध न")
        self.assertEqual((self.r["merc"]["metal"], self.r["merc"]["dhanya"], self.r["merc"]["stotram"]),
                         ("Brass", "Green gram", "Vishnu Sahasranama"))
        self.assertEqual(self.r["merc"]["masa"], "Jyeshta Masa, Krishna Ekadashi")
        self.assertEqual(self.r["marsTransit"], "~45–49 days in each rashi")
        self.assertTrue(self.r["aksharaNote"])
        self.assertTrue(self.r["meanNode"])


@needs_browser
class LayerOneCards(unittest.TestCase):
    """Graha + Bhava cards: Session 26 lines, the 12th-house line after the dignity line, source chips."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              // Simha Lagna; Jupiter 5 deg Karkataka (deep exalted) in the 12th; Venus in Kanya (2nd)
              const sid = {Sun: 20, Moon: 200, Mars: 300, Mercury: 40, Jupiter: 95, Venus: 160, Saturn: 250, Rahu: 10, Ketu: 190};
              renderS23Sections(sid, 5);
              const card = p => document.querySelector(`#s23-predict-body .s23-gb[data-planet="${p}"]`);
              const jup = card('Jupiter');
              const digP = jup.querySelector('.s23-dig-line').closest('p'), tw = jup.querySelector('.s23-twelfth');
              return {jup: jup.textContent, digText: digP.textContent, nextIsTwelfth: digP.nextElementSibling === tw,
                      twelfth: tw ? tw.textContent : '', venus: card('Venus').textContent, sun: card('Sun').textContent,
                      chips: [...jup.querySelectorAll('.s23-src')].map(e => e.textContent)};
            });
        """)

    def test_card_shows_nature_twelfth_and_source(self):
        r = self.r
        self.assertIn("benefic", r["jup"])
        self.assertIn("Benefic planets bring ease and comfort", r["jup"])
        self.assertTrue(any(c.startswith("S24 p.") for c in r["chips"]), r["chips"])
        self.assertIn("Deep Exalted:", r["digText"])
        self.assertTrue(r["nextIsTwelfth"])                    # right after the dignity line
        self.assertIn("even exalted, is in the bucket of losses", r["twelfth"])

    def test_benefic_house_line_and_mild_sun(self):
        self.assertIn("A benefic in the 2nd house indicates that", self.r["venus"])
        self.assertIn("mild malefic", self.r["sun"])
        self.assertIn("(mild) Malefic planets bring struggle", self.r["sun"])


@needs_browser
class ConditionLines(unittest.TestCase):
    """Sentences that hold only for some charts appear on the planet's card; the form's gender switches them."""

    def test_gender_from_the_form(self):
        r = run_page("""
            const out = {};
            for (const g of ['', 'Female']) {
              await setBirth('1990-05-15', '06:30');
              await pickCity('Bengaluru');
              await page.selectOption('#f-gender', g);
              await generate();
              out[g || 'none'] = await page.evaluate(() =>
                document.querySelector('#s23-predict-body .s23-gb[data-planet="Jupiter"]').textContent);
            }
            return out;
        """)
        self.assertIn("Jupiter also represents Husband", r["Female"])
        self.assertNotIn("Jupiter also represents Husband", r["none"])

    def test_active_now_chip(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              // Simha Lagna, Jupiter in Meena (the 8th); a running Jupiter Mahadasha
              const sid = {Sun: 20, Moon: 200, Mars: 300, Mercury: 40, Jupiter: 335, Venus: 160, Saturn: 250, Rahu: 10, Ketu: 190};
              const card = () => document.querySelector('#s23-predict-body .s23-gb[data-planet="Jupiter"]');
              const D = (maha) => ({running: true, birth: new Date('1990-01-01T00:00:00Z'), curMaha: {lord: maha}, curBhukti: {lord: 'Sun'}});
              renderS23Sections(sid, 5, {dasha: D('Jupiter')});
              const on = card().innerHTML;
              renderS23Sections(sid, 5, {dasha: D('Venus')});
              const off = card().innerHTML;
              return {on, off};
            });
        """)
        self.assertIn("active now", r["on"])
        self.assertIn("S24 p.9", r["on"])
        self.assertNotIn("active now", r["off"])


@needs_browser
class Remedies(unittest.TestCase):
    def test_teacher_remedies_and_tips(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => ({
              text: document.getElementById('akshara-body').textContent,
              remedies: S23.remedies,
              tips: [...document.querySelectorAll('#akshara-body .s23-tips li')].map(li => li.textContent),
            }));
        """)
        for x in r["remedies"]:
            if x["topic"] != "Tip":
                self.assertIn(x["text"].split("\n")[0], r["text"])
        self.assertIn("Lord Vishnu", r["text"])
        self.assertIn("debilitated or an afflicted Moon", r["text"])
        self.assertIn("Tips of the day", r["text"])
        tips = [x for x in r["remedies"] if x["topic"] == "Tip"]
        self.assertEqual(len(r["tips"]), len(tips))
        self.assertTrue(any("Never wear black coloured clothes" in t and "S29 p.50" in t for t in r["tips"]), r["tips"])
        self.assertTrue(r["tips"][0].startswith(tips[0]["text"].split("\n")[0]), r["tips"][0])
        self.assertIn("S24 p.38", r["tips"][0])


# The teacher's S27 Chart 1 (= S23-2024 p.13): Mesha Lagna; sidereal longitudes (sign * 30 + degree)
S27_CHART_1_SID = {"Sun": 324, "Moon": 209, "Mars": 163, "Mercury": 308, "Jupiter": 299, "Venus": 284,
                   "Saturn": 142, "Rahu": 345, "Ketu": 165}


@needs_browser
class LayerTwoTable(unittest.TestCase):
    def test_columns_and_chips(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate((sid) => {
              renderS23Sections(sid, 1);
              const row = h => document.querySelector(`#s23-bb tr[data-lord-of="${h}"]`);
              return {one: row(1).textContent, oneDictum: row(1).dataset.dictum, seven: row(7).textContent,
                      head: [...document.querySelectorAll('#s23-bb thead th')].map(th => th.textContent)};
            }, %s);
        """ % json.dumps(S27_CHART_1_SID))
        self.assertEqual(r["head"], ["Lord of → sits in", "Reading", "Sign · placement · company"])
        self.assertEqual(r["oneDictum"], "1")
        for frag in ("Kanya", "continuous or repeated", "A difficult placement.", "the 1st house is strong", "S26 p.21"):
            self.assertIn(frag, r["one"])
        self.assertIn("Jupiter with the lord — lord of the 9th and 12th", r["seven"])
        self.assertIn("Ketu aspects it", r["seven"])


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
  await page.waitForFunction(n => [...document.querySelectorAll('#suggestions div[data-idx]')]
    .some(x => x.firstChild.textContent.trim() === n), name);       // built-in at once; online after a moment
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
// The current-location box: type a place and pick it from the suggestions, as for the birth place.
const pickCurCity = async (name) => {
  await page.fill('#f-curcity', '');
  await page.type('#f-curcity', name);
  await page.waitForFunction(n => [...document.querySelectorAll('#cur-suggestions div[data-idx]')]
    .some(x => x.firstChild.textContent.trim() === n), name);       // built-in at once; online after a moment
  await page.evaluate(n => {
    const d = [...document.querySelectorAll('#cur-suggestions div[data-idx]')].find(x => x.firstChild.textContent.trim() === n);
    d.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
  }, name);
};
// A stand-in for the online place search (Open-Meteo's GeoNames search): answers each query with the given places
// whose name starts with it, after an optional delay per query.
const mockGeo = async (places, delays = {}) => {
  const asked = [];
  await page.route('https://geocoding-api.open-meteo.com/**', async route => {
    const u = new URL(route.request().url()), q = (u.searchParams.get('name') || '').toLowerCase();
    asked.push(Object.fromEntries(u.searchParams));
    if (delays[q]) await new Promise(r => setTimeout(r, delays[q]));
    const results = places.filter(p => p.name.toLowerCase().startsWith(q));
    await route.fulfill({status: 200, contentType: 'application/json', headers: {'access-control-allow-origin': '*'},
                         body: JSON.stringify(results.length ? {results, generationtime_ms: 0.4} : {generationtime_ms: 0.4})});
  });
  return asked;
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
            await pickCurCity('Bengaluru');
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
            await pickCurCity('London');
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
            await pickCurCity('Bengaluru');
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


@needs_browser
class LabelsAndText(unittest.TestCase):
    """Node aspect names, ordinals, live Saturn dates, notes and reference text."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              const txt = id => document.getElementById(id).textContent;
              // Rahu in Karkataka: forward 5/9/12 = Vrischika, Meena, Mithuna; Sun in Meena, Moon in Mithuna
              renderAspectsSection({Sun:12, Moon:3, Mars:1, Mercury:1, Jupiter:1, Venus:1, Saturn:1, Rahu:4, Ketu:10});
              const aspects = txt('aspect-table') + ' ' + txt('aspect-influence');
              const now = new Date();
              const jd = julianDay(now.getUTCFullYear(), now.getUTCMonth()+1, now.getUTCDate(), 12);
              const jup = rashiOf(computeChart(jd, 'lahiri').sidereal.Jupiter).n;
              renderGurubalaSection(jup, 'lahiri');                       // Jupiter in the 1st from the Moon
              const guru1 = document.getElementById('gurubala-body') ? txt('gurubala-body') : document.body.textContent;
              renderGurubalaSection(jup % 12 + 1, 'lahiri');             // Jupiter in the 12th
              const guru12 = document.getElementById('gurubala-body') ? txt('gurubala-body') : document.body.textContent;
              renderPredictive();
              return {
                aspects, guru1, guru12,
                ord: [1,2,3,4,11,12,13,21,22,23].map(ord),
                nodeOrd: [5,9,12].map(h => aspectOrd('Rahu', h)), jupOrd: aspectOrd('Jupiter', 9),
                fmt: [fmtDeg(29.99999999), fmtDeg(10.5), fmtDeg(0)],
                sade: document.body.textContent.match(/Saturn has been in [^.]*\\./) ? document.body.textContent.match(/Saturn has been in [^.]*\\./)[0] : '',
                old29: document.body.textContent.includes('Saturn entered Meena (Pisces) on 29 Mar 2025'),
                ks: txt('pane-ksarpa'), combos: txt('pane-combos'),
                dasha: txt('s23-dasha-tables'),
                letters: GRAHA_REF.Mercury.deva, jupLetters: GRAHA_REF.Jupiter.deva,
                merc: GRAHA_ATTRS.Mercury, marsTransit: GRAHA_ATTRS.Mars.transit,
                aksharaNote: document.body.textContent.includes('beejakshari mantras are listed'),
                meanNode: txt('planet-narrative').includes('mean lunar nodes'),
                bm: Object.fromEntries(['Sun', 'Moon', 'Mercury', 'Mars', 'Jupiter'].map(p => [p, beneficMalefic(p)])),
              };
            });
        """)

    def test_session12_table_follows_s26(self):
        bm = self.r["bm"]
        self.assertEqual(bm["Sun"], "Mild malefic")
        self.assertEqual(bm["Mercury"], "Benefic (Shubha)")
        self.assertEqual(bm["Jupiter"], "Benefic (Shubha)")
        self.assertEqual(bm["Mars"], "Malefic (Papa)")
        self.assertTrue(bm["Moon"].startswith("Benefic (Shubha)"), bm["Moon"])
        self.assertIn("waxing", bm["Moon"])

    def test_node_aspects_are_named_anti_clockwise(self):
        self.assertEqual(self.r["nodeOrd"], ["9th (anti-clockwise)", "5th (anti-clockwise)", "2nd (anti-clockwise)"])
        self.assertEqual(self.r["jupOrd"], "9th")
        self.assertIn("2, 5, 9 (anti-clockwise)", self.r["aspects"])
        self.assertIn("Moon (2nd (anti-clockwise))", self.r["aspects"])
        self.assertNotIn("12th (anti-clockwise)", self.r["aspects"])
        self.assertIn("2nd/5th/9th aspect (counted anti-clockwise)", self.r["combos"])

    def test_ordinals(self):
        self.assertEqual(self.r["ord"], ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "23rd"])
        self.assertIn("1st house from your natal Moon", self.r["guru1"])
        self.assertIn("12th house from your natal Moon", self.r["guru12"])
        self.assertNotRegex(self.r["guru1"] + self.r["guru12"], r"\b(1|2|3|21|22)th\b")

    def test_saturn_dates_are_computed(self):
        self.assertFalse(self.r["old29"])
        self.assertRegex(self.r["sade"], r"Saturn has been in \w+ \(\w+\) since \d{1,2} \w{3} \d{4} and moves on around \d{1,2} \w{3} \d{4}\.")

    def test_kaala_sarpa_note_follows_session_18(self):
        self.assertIn("The Lagna is not considered (Session 18)", self.r["ks"])
        self.assertNotIn("(and the Lagna)", self.r["ks"])
        self.assertIn("in Rahu's rashi it is on the Rahu→Ketu side when its degree is higher than Rahu's", self.r["ks"])

    def test_degree_format_never_shows_60(self):
        self.assertEqual(self.r["fmt"], ["30° 00' 00\"", "10° 30' 00\"", "0° 00' 00\""])

    def test_dasha_balance_is_shown(self):
        self.assertRegex(self.r["dasha"], r"Balance at birth: \d+ y \d+ m \d+ d of \w+ mahādaśā")

    def test_reference_text(self):
        self.assertEqual(self.r["letters"], "ट ठ ड ढ ण")
        self.assertEqual(self.r["jupLetters"], "त थ द ध न")
        self.assertEqual((self.r["merc"]["metal"], self.r["merc"]["dhanya"], self.r["merc"]["stotram"]),
                         ("Brass", "Green gram", "Vishnu Sahasranama"))
        self.assertEqual(self.r["merc"]["masa"], "Jyeshta Masa, Krishna Ekadashi")
        self.assertEqual(self.r["marsTransit"], "~45–49 days in each rashi")
        self.assertTrue(self.r["aksharaNote"])
        self.assertTrue(self.r["meanNode"])


@needs_browser
class LayerOneCards(unittest.TestCase):
    """Graha + Bhava cards: Session 26 lines, the 12th-house line after the dignity line, source chips."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              // Simha Lagna; Jupiter 5 deg Karkataka (deep exalted) in the 12th; Venus in Kanya (2nd)
              const sid = {Sun: 20, Moon: 200, Mars: 300, Mercury: 40, Jupiter: 95, Venus: 160, Saturn: 250, Rahu: 10, Ketu: 190};
              renderS23Sections(sid, 5);
              const card = p => document.querySelector(`#s23-predict-body .s23-gb[data-planet="${p}"]`);
              const jup = card('Jupiter');
              const digP = jup.querySelector('.s23-dig-line').closest('p'), tw = jup.querySelector('.s23-twelfth');
              return {jup: jup.textContent, digText: digP.textContent, nextIsTwelfth: digP.nextElementSibling === tw,
                      twelfth: tw ? tw.textContent : '', venus: card('Venus').textContent, sun: card('Sun').textContent,
                      chips: [...jup.querySelectorAll('.s23-src')].map(e => e.textContent)};
            });
        """)

    def test_card_shows_nature_twelfth_and_source(self):
        r = self.r
        self.assertIn("benefic", r["jup"])
        self.assertIn("Benefic planets bring ease and comfort", r["jup"])
        self.assertTrue(any(c.startswith("S24 p.") for c in r["chips"]), r["chips"])
        self.assertIn("Deep Exalted:", r["digText"])
        self.assertTrue(r["nextIsTwelfth"])                    # right after the dignity line
        self.assertIn("even exalted, is in the bucket of losses", r["twelfth"])

    def test_benefic_house_line_and_mild_sun(self):
        self.assertIn("A benefic in the 2nd house indicates that", self.r["venus"])
        self.assertIn("mild malefic", self.r["sun"])
        self.assertIn("(mild) Malefic planets bring struggle", self.r["sun"])


@needs_browser
class ConditionLines(unittest.TestCase):
    """Sentences that hold only for some charts appear on the planet's card; the form's gender switches them."""

    def test_gender_from_the_form(self):
        r = run_page("""
            const out = {};
            for (const g of ['', 'Female']) {
              await setBirth('1990-05-15', '06:30');
              await pickCity('Bengaluru');
              await page.selectOption('#f-gender', g);
              await generate();
              out[g || 'none'] = await page.evaluate(() =>
                document.querySelector('#s23-predict-body .s23-gb[data-planet="Jupiter"]').textContent);
            }
            return out;
        """)
        self.assertIn("Jupiter also represents Husband", r["Female"])
        self.assertNotIn("Jupiter also represents Husband", r["none"])

    def test_active_now_chip(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              // Simha Lagna, Jupiter in Meena (the 8th); a running Jupiter Mahadasha
              const sid = {Sun: 20, Moon: 200, Mars: 300, Mercury: 40, Jupiter: 335, Venus: 160, Saturn: 250, Rahu: 10, Ketu: 190};
              const card = () => document.querySelector('#s23-predict-body .s23-gb[data-planet="Jupiter"]');
              const D = (maha) => ({running: true, birth: new Date('1990-01-01T00:00:00Z'), curMaha: {lord: maha}, curBhukti: {lord: 'Sun'}});
              renderS23Sections(sid, 5, {dasha: D('Jupiter')});
              const on = card().innerHTML;
              renderS23Sections(sid, 5, {dasha: D('Venus')});
              const off = card().innerHTML;
              return {on, off};
            });
        """)
        self.assertIn("active now", r["on"])
        self.assertIn("S24 p.9", r["on"])
        self.assertNotIn("active now", r["off"])


@needs_browser
class Remedies(unittest.TestCase):
    def test_teacher_remedies_and_tips(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => ({
              text: document.getElementById('akshara-body').textContent,
              remedies: S23.remedies,
              tips: [...document.querySelectorAll('#akshara-body .s23-tips li')].map(li => li.textContent),
            }));
        """)
        for x in r["remedies"]:
            if x["topic"] != "Tip":
                self.assertIn(x["text"].split("\n")[0], r["text"])
        self.assertIn("Lord Vishnu", r["text"])
        self.assertIn("debilitated or an afflicted Moon", r["text"])
        self.assertIn("Tips of the day", r["text"])
        tips = [x for x in r["remedies"] if x["topic"] == "Tip"]
        self.assertEqual(len(r["tips"]), len(tips))
        self.assertTrue(any("Never wear black coloured clothes" in t and "S29 p.50" in t for t in r["tips"]), r["tips"])
        self.assertTrue(r["tips"][0].startswith(tips[0]["text"].split("\n")[0]), r["tips"][0])
        self.assertIn("S24 p.38", r["tips"][0])


# The teacher's S27 Chart 1 (= S23-2024 p.13): Mesha Lagna; sidereal longitudes (sign * 30 + degree)
S27_CHART_1_SID = {"Sun": 324, "Moon": 209, "Mars": 163, "Mercury": 308, "Jupiter": 299, "Venus": 284,
                   "Saturn": 142, "Rahu": 345, "Ketu": 165}


@needs_browser
class LayerTwoTable(unittest.TestCase):
    def test_columns_and_chips(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate((sid) => {
              renderS23Sections(sid, 1);
              const row = h => document.querySelector(`#s23-bb tr[data-lord-of="${h}"]`);
              return {one: row(1).textContent, oneDictum: row(1).dataset.dictum, seven: row(7).textContent,
                      head: [...document.querySelectorAll('#s23-bb thead th')].map(th => th.textContent)};
            }, %s);
        """ % json.dumps(S27_CHART_1_SID))
        self.assertEqual(r["head"], ["Lord of → sits in", "Reading", "Sign · placement · company"])
        self.assertEqual(r["oneDictum"], "1")
        for frag in ("Kanya", "continuous or repeated", "A difficult placement.", "the 1st house is strong", "S26 p.21"):
            self.assertIn(frag, r["one"])
        self.assertIn("Jupiter with the lord — lord of the 9th and 12th", r["seven"])
        self.assertIn("Ketu aspects it", r["seven"])


@needs_browser
class LifeAreasTab(unittest.TestCase):
    """Session 27's Ready Reckoner as a report tab: 16 areas, the 7 steps for the chosen one, all 16 on paper."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            const out = {};
            out.nav = await page.evaluate(() => [...document.querySelectorAll('#reportNav button')].map(b => b.textContent));
            await page.evaluate((sid) => renderS23Sections(sid, 1), SID);
            out.buttons = await page.evaluate(() => [...document.querySelectorAll('#s23-life-body .s23-area-btn')].map(b => b.textContent));
            await page.evaluate(() => [...document.querySelectorAll('#reportNav button')].find(b => b.textContent === 'Life areas').click());
            await page.click('#s23-life-body .s23-area-btn[data-area="8"]');
            out.visible = await page.evaluate(() => [...document.querySelectorAll('.s23-area-pane')].filter(p => getComputedStyle(p).display !== 'none').map(p => p.id));
            out.mother = await page.evaluate(() => document.getElementById('s23-area-8').textContent);
            out.love = await page.evaluate(() => document.getElementById('s23-area-16').textContent);
            await page.emulateMedia({media: 'print'});
            out.printed = await page.evaluate(() => [...document.querySelectorAll('.s23-area-pane')].filter(p => getComputedStyle(p).display !== 'none').length);
            await page.emulateMedia({media: 'screen'});
            await page.setViewportSize({width: 390, height: 800});
            out.width = await page.evaluate(() => document.documentElement.scrollWidth);
            await page.evaluate(() => renderS23Sections(null, null));
            out.noLagna = await page.evaluate(() => document.getElementById('s23-life-body').textContent);
            return out;
        """.replace("SID", json.dumps(S27_CHART_1_SID)))

    def test_tab_sits_between_dasha_and_predictive(self):
        nav = self.r["nav"]
        self.assertEqual(nav[nav.index("Daśā–Bhukti") + 1], "Life areas")
        self.assertEqual(nav[nav.index("Life areas") + 1], "Predictive & Remedies")

    def test_sixteen_buttons_and_mother_pane(self):
        self.assertEqual(len(self.r["buttons"]), 16)
        self.assertEqual(self.r["buttons"][7], "Mother")
        self.assertEqual(self.r["visible"], ["s23-area-8"])
        for frag in ("Karkataka", "Jupiter", "Venus", "Rahu", "Saturn", "Supports", "Pressure"):
            self.assertIn(frag, self.r["mother"])

    def test_love_marriage_shows_the_pac_step(self):
        self.assertIn("PAC link", self.r["love"])

    def test_print_shows_all_areas(self):
        self.assertEqual(self.r["printed"], 16)

    def test_phone_width_no_horizontal_scroll(self):
        self.assertLessEqual(self.r["width"], 390)

    def test_no_lagna_message(self):
        self.assertIn("needs the birth time and place", self.r["noLagna"])


@needs_browser
class ReviewFixesOnThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate((sid) => {
              S23.life_areas[7].area = 'Mother "Amma"';                     // a user-edited cell with quotes
              renderS23Sections(sid, 1);
              const pane = document.getElementById('s23-area-8');
              const four = document.querySelector('#s23-fivestep tr[data-house="4"]');
              const want = S23.aspect_meaning.find(r => r.planet === 'Jupiter' && r.aspect === 7 && r.from_house === 10).text;
              const card = document.querySelector('#s23-predict-body .s23-gb[data-planet="Saturn"]');
              const size = sel => { const e = card.querySelector(sel); return e ? getComputedStyle(e).fontSize : null; };
              return {printTitle: pane ? pane.dataset.printTitle : null, panes: document.querySelectorAll('.s23-area-pane').length,
                      button: document.querySelector('.s23-area-btn[data-area="8"]').textContent,
                      fourText: four.textContent, want,
                      pointSize: size('.s23-points li'), natureSize: size('.s23-nature-lines li')};
            }, SID);
        """.replace("SID", json.dumps(S27_CHART_1_SID)))

    def test_quotes_in_a_cell_do_not_break_the_markup(self):
        self.assertEqual(self.r["printTitle"], 'Life area 8 · Mother "Amma"')
        self.assertEqual(self.r["panes"], 16)
        self.assertEqual(self.r["button"], 'Mother "Amma"')

    def test_five_step_shows_aspect_meanings(self):
        self.assertIn(self.r["want"], self.r["fourText"])          # Jupiter's 7th from the 10th onto the 4th (S24)

    def test_session26_lines_match_the_other_lists(self):
        self.assertEqual(self.r["natureSize"], self.r["pointSize"])


@needs_browser
class DashaOutsideItsSpan(unittest.TestCase):
    def test_no_running_period_is_claimed_outside_the_120_years(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              const sid = currentChart.chart.sidereal;
              const roles = s23Roles(currentChart.lagnaRashi.n, s23Inputs(sid).pbr);
              const old = buildDasha(sid.Moon, '1850-01-01', '10:00');          // span ends in 1970
              renderS23Dasha(old, roles, new Date());
              const before = {running: old.running, body: document.getElementById('s23-dasha-body').textContent,
                              tables: document.getElementById('s23-dasha-tables').textContent};
              const now = buildDasha(sid.Moon, currentChart.dob, currentChart.tob, currentChart.JD);
              return {before, nowRunning: now.running};
            });
        """)
        self.assertFalse(r["before"]["running"])
        self.assertIn("No daśā is running today", r["before"]["body"])
        self.assertIn("No daśā is running today", r["before"]["tables"])
        self.assertNotIn("Running now:", r["before"]["tables"])
        self.assertTrue(r["nowRunning"])


@needs_browser
class CurrentLocationDay(unittest.TestCase):
    """Review follow-ups: the muhūrta date follows the city's own day; toggles; clock-change nights."""

    def test_default_date_is_the_citys_day_from_sunrise(self):
        r = run_page("""
            const read = () => page.evaluate(() => ({date: document.getElementById('f-curdate').value,
              now: [...document.querySelectorAll('#choghadiya-body tr.now')].map(tr => tr.textContent)}));
            const out = {};
            out.bengaluru = await read();                                    // 03:00 IST: before sunrise
            await pickCurCity('London');  // 22:30 BST on the 9th
            out.london = await read();
            await page.fill('#f-curdate', '2026-10-08');
            await page.dispatchEvent('#f-curdate', 'change');
            await pickCurCity('Bengaluru');
            out.kept = await read();
            return out;
        """, clock="2026-10-10T03:00:00+05:30", timezoneId="Asia/Kolkata")
        self.assertEqual(r["bengaluru"]["date"], "2026-10-09")
        self.assertEqual(len(r["bengaluru"]["now"]), 1)                     # the night in progress is highlighted
        self.assertEqual(r["london"]["date"], "2026-10-09")
        self.assertEqual(len(r["london"]["now"]), 1)
        self.assertEqual(r["kept"]["date"], "2026-10-08")                    # a date picked by hand stays

    def test_switching_back_from_manual_refreshes_the_offset(self):
        r = run_page("""
            await setBirth('1990-07-15', '10:00');
            await pickCity('London');
            const summer = await page.inputValue('#f-tz');
            await page.click('#btn-manual');
            await page.fill('#f-dob', '1990-01-15');
            await page.click('#btn-manual');                               // back to the city lookup
            return {summer, winter: await page.inputValue('#f-tz')};
        """)
        self.assertEqual((r["summer"], r["winter"]), ("1", "0"))

    def test_night_with_a_clock_change_is_split_evenly(self):
        r = run_page("""
            await pickCurCity('London');
            const rows = async (date) => { await page.fill('#f-curdate', date); await page.dispatchEvent('#f-curdate', 'change');
              return page.evaluate(() => { const b = document.getElementById('choghadiya-body');
                const t = b.querySelectorAll('table'); return {
                  night: [...t[1].querySelectorAll('tbody tr')].map(tr => tr.children[0].textContent),
                  rise: b.textContent.match(/Sunrise (\\d\\d:\\d\\d)/)[1]}; }); };
            return {oct24: await rows('2026-10-24'), oct25: await rows('2026-10-25')};
        """)
        mins = lambda t: int(t[:2]) * 60 + int(t[3:5])
        spans = [x.split(" – ") for x in r["oct24"]["night"]]
        self.assertEqual(spans[-1][1], r["oct25"]["rise"])                    # the night ends at the next sunrise
        lengths = [(mins(b) - mins(a)) % 1440 for a, b in spans]
        # clocks go back at 02:00 BST: the window holding the change shows 60 minutes less than the others
        rest = sorted(lengths)[1:]
        self.assertLessEqual(max(rest) - min(rest), 1)                         # whole minutes: ±1 from rounding
        self.assertAlmostEqual(min(rest) - min(lengths), 60, delta=1)


if __name__ == "__main__":
    unittest.main()

    def test_no_running_period_is_claimed_outside_the_120_years(self):
        r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            return await page.evaluate(() => {
              const sid = currentChart.chart.sidereal;
              const roles = s23Roles(currentChart.lagnaRashi.n, s23Inputs(sid).pbr);
              const old = buildDasha(sid.Moon, '1850-01-01', '10:00');          // span ends in 1970
              renderS23Dasha(old, roles, new Date());
              const before = {running: old.running, body: document.getElementById('s23-dasha-body').textContent,
                              tables: document.getElementById('s23-dasha-tables').textContent};
              const now = buildDasha(sid.Moon, currentChart.dob, currentChart.tob, currentChart.JD);
              return {before, nowRunning: now.running};
            });
        """)
        self.assertFalse(r["before"]["running"])
        self.assertIn("No daśā is running today", r["before"]["body"])
        self.assertIn("No daśā is running today", r["before"]["tables"])
        self.assertNotIn("Running now:", r["before"]["tables"])
        self.assertTrue(r["nowRunning"])


@needs_browser
class CurrentLocationDay(unittest.TestCase):
    """Review follow-ups: the muhūrta date follows the city's own day; toggles; clock-change nights."""

    def test_default_date_is_the_citys_day_from_sunrise(self):
        r = run_page("""
            const read = () => page.evaluate(() => ({date: document.getElementById('f-curdate').value,
              now: [...document.querySelectorAll('#choghadiya-body tr.now')].map(tr => tr.textContent)}));
            const out = {};
            out.bengaluru = await read();                                    // 03:00 IST: before sunrise
            await pickCurCity('London');  // 22:30 BST on the 9th
            out.london = await read();
            await page.fill('#f-curdate', '2026-10-08');
            await page.dispatchEvent('#f-curdate', 'change');
            await pickCurCity('Bengaluru');
            out.kept = await read();
            return out;
        """, clock="2026-10-10T03:00:00+05:30", timezoneId="Asia/Kolkata")
        self.assertEqual(r["bengaluru"]["date"], "2026-10-09")
        self.assertEqual(len(r["bengaluru"]["now"]), 1)                     # the night in progress is highlighted
        self.assertEqual(r["london"]["date"], "2026-10-09")
        self.assertEqual(len(r["london"]["now"]), 1)
        self.assertEqual(r["kept"]["date"], "2026-10-08")                    # a date picked by hand stays

    def test_switching_back_from_manual_refreshes_the_offset(self):
        r = run_page("""
            await setBirth('1990-07-15', '10:00');
            await pickCity('London');
            const summer = await page.inputValue('#f-tz');
            await page.click('#btn-manual');
            await page.fill('#f-dob', '1990-01-15');
            await page.click('#btn-manual');                               // back to the city lookup
            return {summer, winter: await page.inputValue('#f-tz')};
        """)
        self.assertEqual((r["summer"], r["winter"]), ("1", "0"))

    def test_night_with_a_clock_change_is_split_evenly(self):
        r = run_page("""
            await pickCurCity('London');
            const rows = async (date) => { await page.fill('#f-curdate', date); await page.dispatchEvent('#f-curdate', 'change');
              return page.evaluate(() => { const b = document.getElementById('choghadiya-body');
                const t = b.querySelectorAll('table'); return {
                  night: [...t[1].querySelectorAll('tbody tr')].map(tr => tr.children[0].textContent),
                  rise: b.textContent.match(/Sunrise (\\d\\d:\\d\\d)/)[1]}; }); };
            return {oct24: await rows('2026-10-24'), oct25: await rows('2026-10-25')};
        """)
        mins = lambda t: int(t[:2]) * 60 + int(t[3:5])
        spans = [x.split(" – ") for x in r["oct24"]["night"]]
        self.assertEqual(spans[-1][1], r["oct25"]["rise"])                    # the night ends at the next sunrise
        lengths = [(mins(b) - mins(a)) % 1440 for a, b in spans]
        # clocks go back at 02:00 BST: the window holding the change shows 60 minutes less than the others
        rest = sorted(lengths)[1:]
        self.assertLessEqual(max(rest) - min(rest), 1)                         # whole minutes: ±1 from rounding
        self.assertAlmostEqual(min(rest) - min(lengths), 60, delta=1)


if __name__ == "__main__":
    unittest.main()


# Her Chart 3 (S28): Dhanur Lagna; sidereal longitudes (sign * 30 + degree)
S28_CHART_3_SID = {"Sun": 10, "Moon": 211, "Mars": 101, "Mercury": 351, "Jupiter": 68, "Venus": 33,
                   "Saturn": 120, "Rahu": 160, "Ketu": 340}


@needs_browser
class Round1Page(unittest.TestCase):
    """Sessions 28-29 on the page: strength reasons, degree stages, her Chart 3 sentences, daśā to Prāṇa."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            const out = await page.evaluate((sid) => {
              renderS23Sections(sid, 9);
              const card = p => document.querySelector(`#s23-predict-body .s23-gb[data-planet="${p}"]`);
              const q = (el, s) => el.querySelector(s) ? el.querySelector(s).textContent : null;
              return {venusStrength: q(card('Venus'), '.s23-strength'), saturnDegree: q(card('Saturn'), '.s23-degree'),
                      rahu: q(card('Rahu'), '.s23-readings'),
                      eleven: q(document.querySelector('#s23-bb tr[data-lord-of="11"]'), '.s23-house-aspects'),
                      area14: document.getElementById('s23-area-14').textContent};
            }, SID);
            await page.evaluate(() => renderDashaPane(buildDasha(253.6103, '1982-06-08', '12:00:00'), null));
            out.chain = await page.evaluate(() => [...document.querySelectorAll('#s23-dasha-chain li')].map(li => li.textContent));
            const count = l => page.evaluate(l => document.querySelectorAll(`#s23-dasha-tables tr[data-level="${l}"]`).length, l);
            const click = sel => page.evaluate(sel => document.querySelector(sel).click(), sel);   // the section may be folded
            await click('tr.s23-bhukti .s23-open');
            out.level2 = await count(2);
            await click('#s23-dasha-tables tr[data-level="2"] .s23-open');
            out.level3 = await count(3);
            out.rows = await page.evaluate(() => {
              const td = document.querySelector('#s23-dasha-tables tr[data-level="2"] td'), cs = getComputedStyle(td);
              const l3 = document.querySelector('#s23-dasha-tables tr[data-level="3"]');
              return {transform: cs.textTransform, font: cs.fontFamily, l2date: td.nextElementSibling.textContent,
                      l3date: l3.cells[1].textContent};
            });
            await click('tr.s23-bhukti .s23-open');
            out.closed = await count(2) + await count(3);
            // Classes tab with degrees: Mars combust in Vrischika (the 8th from Mesha) is weak, so no Dusthana line
            out.classes = await page.evaluate(() => {
              renderS23Sections({Sun: 215, Moon: 100, Mars: 218, Mercury: 250, Jupiter: 10, Venus: 300, Saturn: 40,
                                 Rahu: 160, Ketu: 340}, 1);
              const row = document.querySelector('#s23-readings tr[data-planet="Mars"]');
              const card = document.querySelector('#s23-predict-body .s23-gb[data-planet="Mars"] .s23-class-texts');
              return {table: row ? row.textContent : null, card: card ? card.textContent : ""};
            });
            await page.setViewportSize({width: 390, height: 800});
            out.width = await page.evaluate(() => document.documentElement.scrollWidth);
            return out;
        """.replace("SID", json.dumps(S28_CHART_3_SID)))

    def test_strength_chip_reasons(self):
        self.assertEqual(self.r["venusStrength"], "mixed — aspected by Saturn, aspected by Rahu (S29)")

    def test_degree_line(self):
        self.assertIn("At 0 degree", self.r["saturnDegree"])
        self.assertIn("lose their strength of giving malefic results", self.r["saturnDegree"])

    def test_reading_on_card(self):
        self.assertIn("In her example chart (S28):", self.r["rahu"])
        self.assertIn("export, forex", self.r["rahu"])

    def test_layer2_house_aspects(self):
        self.assertIn("Sun aspects the 11th (rules the 9th)", self.r["eleven"])

    def test_life_area_shows_ruled_houses_and_gains(self):
        self.assertIn("Saturn aspects the 11th (rules the 2nd and 3rd)", self.r["area14"])

    def test_dasha_chain_and_open_rows(self):
        self.assertEqual(len(self.r["chain"]), 5)
        self.assertTrue(self.r["chain"][0].startswith("Mahādaśā:"), self.r["chain"])
        self.assertTrue(self.r["chain"][4].startswith("Prāṇa:"), self.r["chain"])
        self.assertEqual((self.r["level2"], self.r["level3"], self.r["closed"]), (9, 9, 0))

    def test_no_horizontal_scroll_390(self):
        self.assertLessEqual(self.r["width"], 390)

    def test_opened_rows_are_table_rows_not_headings(self):
        self.assertEqual(self.r["rows"]["transform"], "none")
        self.assertNotIn("Cinzel", self.r["rows"]["font"])

    def test_sookshma_and_prana_show_the_time(self):
        clock = r"\d{1,2}:\d{2}"
        for line in self.r["chain"][3:]:
            self.assertRegex(line, clock)
        for line in self.r["chain"][:3]:
            self.assertNotRegex(line, clock)
        self.assertRegex(self.r["rows"]["l3date"], clock)                 # a Sookshma row
        self.assertNotRegex(self.r["rows"]["l2date"], clock)              # a Pratyantara row keeps the date

    def test_classes_tab_uses_the_degrees(self):
        line = "Malefic planets in dusthana houses"
        self.assertIsNotNone(self.r["classes"]["table"])
        self.assertNotIn(line, self.r["classes"]["card"])
        self.assertNotIn(line, self.r["classes"]["table"])


# The chart of the 2026-10-13 bhāva-by-bhāva draft (Simha Lagna), as sidereal longitudes.
SIMHA_SID = {"Sun": 11.80, "Moon": 346.91, "Mars": 27.21, "Mercury": 12.31, "Jupiter": 122.45, "Venus": 356.86,
             "Saturn": 354.61, "Rahu": 354.47, "Ketu": 174.47}


@needs_browser
class BhavaView(unittest.TestCase):
    """The Prediction read bhāva by bhāva (spec 2026-10-13): the default view, its panels, links, phone and print."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            await page.click('#reportNav button:has-text("Bhāvas")');
            const render = () => page.evaluate(sid => renderS23Sections(sid, 5, {retro: {Rahu: true, Ketu: true}}), SID);
            await render();
            const out = {};
            out.view = await page.evaluate(() => ({bhava: getComputedStyle(document.getElementById('s23-view-bhava')).display,
              layer: getComputedStyle(document.getElementById('s23-view-layer')).display,
              active: [...document.querySelectorAll('.s23-view-btn.active')].map(b => b.dataset.view)}));
            out.panels = await page.evaluate(() => [...document.querySelectorAll('#s23-view-bhava section.s23-bv-house')].map(s => ({
              house: +s.dataset.house, layers: [...s.querySelectorAll('.s23-bv-layer > h5')].map(h => h.textContent),
              karaka: !!s.querySelector('.s23-bv-karaka')})));
            out.ninth = await page.evaluate(() => {
              const s = document.getElementById('s23-bv-h9'), t = el => el.textContent;
              const dts = x => [...x.querySelectorAll('dl.s23-bv-facts dt')].map(t);
              const role = r => [...s.querySelectorAll(`.s23-bv-planet[data-role="${r}"]`)];
              return {classes: [...s.querySelectorAll('.s23-bv-classes li')].map(li => li.dataset.class),
                      badhaka: t(s.querySelector('.s23-bv-classes li[data-class="Badhaka"]')),
                      occupants: role('occupant').map(x => x.dataset.planet), occupantDts: role('occupant').map(dts),
                      lord: role('lord').map(x => ({planet: x.dataset.planet, dts: dts(x)})),
                      areas: [...s.querySelectorAll('a.s23-bv-area')].map(a => +a.dataset.area)};
            });
            out.jupiter = await page.evaluate(() => {
              const x = document.querySelector('#s23-bv-h1 .s23-bv-planet[data-role="occupant"][data-planet="Jupiter"]');
              return [...x.querySelectorAll('dt')].find(d => d.textContent === 'Digbala').nextElementSibling.textContent;
            });
            out.jup = await page.evaluate(() => [document.querySelectorAll('#s23-view-layer #s23-asp .s23-jup').length,
                                                 document.querySelectorAll('#s23-view-bhava .s23-bv-pairs .s23-jup').length]);
            await page.click('#s23-bv-jump a[href="#s23-bv-h7"]');
            out.jump = await page.evaluate(() => {
              const bar = document.getElementById('s23-bv-jump').getBoundingClientRect();
              const hit = document.elementFromPoint(bar.left + bar.width / 2, bar.top + bar.height / 2);
              return {top: bar.top, bottom: bar.bottom, onTop: !!(hit && hit.closest('#s23-bv-jump')), scrolled: window.scrollY,
                      panel: document.getElementById('s23-bv-h7').getBoundingClientRect().top};
            });
            await page.click('#s23-bv-h7 a.s23-bv-top');
            out.up = await page.evaluate(() => ({pane: document.getElementById('s23-view-bhava').getBoundingClientRect().top,
                                                 scrolled: window.scrollY}));
            await page.click('#s23-bv-h9 a.s23-bv-area[data-area="12"]');
            out.area = await page.evaluate(() => {
              const life = document.getElementById('s23-life-body').closest('details.section');
              return {pane: getComputedStyle(document.getElementById('s23-area-12')).display, shown: s23AreaShown,
                      open: life.open, section: getComputedStyle(life).display};
            });
            await page.click('#reportNav button:has-text("Bhāvas")');
            await page.click('.s23-view-btn[data-view="layer"]');
            out.layer = await page.evaluate(() => ({pane: getComputedStyle(document.getElementById('s23-view-layer')).display,
              bhava: getComputedStyle(document.getElementById('s23-view-bhava')).display,
              cards: [...document.querySelectorAll('#s23-view-layer .s23-gb')].filter(c => c.offsetParent !== null).length}));
            await render();
            out.persist = await page.evaluate(() => [getComputedStyle(document.getElementById('s23-view-layer')).display,
              getComputedStyle(document.getElementById('s23-view-bhava')).display]);
            await page.click('.s23-view-btn[data-view="bhava"]');
            out.back = await page.evaluate(() => [getComputedStyle(document.getElementById('s23-view-bhava')).display, s23ViewShown]);
            await page.emulateMedia({media: 'print'});
            out.print = await page.evaluate(() => [getComputedStyle(document.querySelector('.s23-view-btns')).display,
              getComputedStyle(document.getElementById('s23-bv-jump')).display]);
            await page.emulateMedia({media: 'screen'});
            out.rest = await page.evaluate(() => {
              const open = () => [...document.querySelectorAll('details.s23-bv-rest')].filter(d => d.open).length;
              const n = document.querySelectorAll('details.s23-bv-rest').length, before = open();
              window.dispatchEvent(new Event('beforeprint'));
              const during = open();
              window.dispatchEvent(new Event('afterprint'));
              return {n, before, during, after: open()};
            });
            await page.setViewportSize({width: 375, height: 800});
            out.phone = await page.evaluate(() => ({sw: document.documentElement.scrollWidth, vw: window.innerWidth}));
            out.crowded = await page.evaluate(() => {
              const sid = {}; for (const p of S23_PLANETS) sid[p] = 100 + S23_PLANETS.indexOf(p) * 0.1;
              renderS23Sections(sid, 4);                    // Lagna Karka: every planet in the 1st house
              return {conj: document.querySelectorAll('#s23-bv-h1 .s23-bv-pairs li[data-a]').length,
                      sw: document.documentElement.scrollWidth, vw: window.innerWidth};
            });
            return out;
        """.replace("SID", json.dumps(SIMHA_SID)))

    def test_by_bhava_is_the_default(self):
        self.assertEqual(self.r["view"], {"bhava": "block", "layer": "none", "active": ["bhava"]})

    def test_twelve_panels_with_four_layers(self):
        layers = ["Layer 1 · Graha + Bhāva", "Layer 2 · Bhāva + Bhāva", "Layer 3 · Graha + Rāśi", "Layer 4 · Graha + Graha"]
        self.assertEqual([p["house"] for p in self.r["panels"]], list(range(1, 13)))
        for p in self.r["panels"]:
            self.assertEqual(p["layers"], layers, p["house"])
            self.assertTrue(p["karaka"], p["house"])

    def test_ninth_house_panel(self):
        n = self.r["ninth"]
        self.assertEqual(n["classes"], ["Trikona", "Apoklima", "Badhaka"])
        self.assertIn("its lord Mars is the Badhakādhipati", n["badhaka"])
        self.assertEqual(n["occupants"], ["Sun", "Mars", "Mercury"])
        for dts in n["occupantDts"]:
            self.assertEqual(dts[:5], ["House", "Roles", "Dignity", "Digbala", "Strength"])
        self.assertEqual([x["planet"] for x in n["lord"]], ["Mars"])
        self.assertNotIn("Class rules", n["lord"][0]["dts"])
        self.assertEqual(n["areas"], [12, 15])

    def test_first_house_digbala(self):
        self.assertIn("gains directional strength (digbala) in the 1st house", self.r["jupiter"])

    def test_jump_bar_stays_in_view(self):
        """Final review: the bar must really stick (its clipping ancestors once kept it from sticking)."""
        j = self.r["jump"]
        self.assertGreater(j["scrolled"], 1000, j)                  # the page scrolled down to the 7th house
        self.assertTrue(-1 <= j["top"] <= 1, j)                     # the bar is held at the top of the window
        self.assertTrue(j["onTop"], j)                              # and nothing covers it
        self.assertGreaterEqual(j["panel"], j["bottom"] - 1, j)     # the 7th house is not hidden under it
        self.assertLess(j["panel"], j["bottom"] + 120, j)
        u = self.r["up"]
        self.assertLess(u["scrolled"], j["scrolled"] - 1000, u)     # "↑ Houses" goes back up to the planet table
        self.assertTrue(-1 <= u["pane"] <= 60, u)

    def test_jupiter_aspect_flag(self):
        """Final review: By bhāva shows "Aspect > placement" on each of Jupiter's aspects, as By layer does."""
        self.assertEqual(self.r["jup"], [3, 3])                     # Jupiter aspects the Sun, Mars and Mercury

    def test_area_link_opens_life_area(self):
        self.assertEqual(self.r["area"], {"pane": "block", "shown": 12, "open": True, "section": "block"})

    def test_view_persists_across_charts(self):
        self.assertEqual(self.r["layer"], {"pane": "block", "bhava": "none", "cards": 9})
        self.assertEqual(self.r["persist"], ["block", "none"])
        self.assertEqual(self.r["back"], ["block", "bhava"])

    def test_print(self):
        self.assertEqual(self.r["print"], ["none", "none"])
        rest = self.r["rest"]
        self.assertGreater(rest["n"], 0)
        self.assertEqual((rest["before"], rest["during"], rest["after"]), (0, rest["n"], 0))

    def test_phone_width(self):
        self.assertLessEqual(self.r["phone"]["sw"], self.r["phone"]["vw"] + 1)

    def test_crowded_house(self):
        c = self.r["crowded"]
        self.assertEqual(c["conj"], 36)
        self.assertLessEqual(c["sw"], c["vw"] + 1)


@needs_browser
class PhoneForm(unittest.TestCase):
    """On a phone every field of the birth form fits the screen, with the city search and with manual lat/lon. The
    time field ran off the right edge (the Name and Place fields' span 2 kept a second column), so its picker button
    could not be tapped; with manual lat/lon the form grew to 771 px."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            const check = () => page.evaluate(() => {
              const vw = document.documentElement.clientWidth;
              const off = [...document.querySelectorAll('#inputPanel input, #inputPanel select')].filter(e => e.offsetParent)
                .map(e => [e.id, e.getBoundingClientRect()]).filter(([, r]) => r.left < 0 || r.right > vw)
                .map(([id, r]) => `${id} ${Math.round(r.left)}..${Math.round(r.right)}`);
              const tob = document.getElementById('f-tob');
              tob.scrollIntoView({block: 'center'});
              const t = tob.getBoundingClientRect(), hit = document.elementFromPoint(t.right - 6, t.top + t.height / 2);
              return {off, timeButtonOnScreen: !!hit && hit.id === 'f-tob'};
            });
            const out = {};
            for (const w of [320, 390, 412]) {
              await page.setViewportSize({width: w, height: 800});
              out[w] = {city: await check()};
              await page.click('#btn-manual');                       // manual lat/lon on …
              out[w].manual = await check();
              await page.click('#btn-manual');                       // … and off again
            }
            return out;
        """)

    def test_every_form_field_fits_a_phone_screen(self):
        for w, modes in self.r.items():
            for mode, got in modes.items():
                self.assertEqual(got["off"], [], (w, mode))

    def test_the_time_field_can_be_tapped_at_its_picker_end(self):
        for w, modes in self.r.items():
            for mode, got in modes.items():
                self.assertTrue(got["timeButtonOnScreen"], (w, mode))


@needs_browser
class PhoneReport(unittest.TestCase):
    """On a phone nothing in the report is cut off at the right edge (outside a box that scrolls sideways), and the
    South-Indian chart fits: four equal columns, square cells (the right-hand column — Gemini to Virgo — was cut off)."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            await page.click('#btn-manual');
            await setBirth('1968-04-25', '14:27:00');
            await page.fill('#f-lat', '13.55'); await page.press('#f-lat', 'Tab');
            await page.fill('#f-lon', '76.01'); await page.press('#f-lon', 'Tab');
            await page.fill('#f-tz', '5.5');
            await generate();
            const out = {};
            for (const w of [320, 390]) {
              await page.setViewportSize({width: w, height: 800});
              out[w] = {cut: {}, chart: null};
              const groups = await page.evaluate(() => [...document.querySelectorAll('#reportNav button')].map(b => b.textContent));
              for (const g of groups) {
                await page.evaluate(g => [...document.querySelectorAll('#reportNav button')].find(b => b.textContent === g).click(), g);
                out[w].cut[g] = await page.evaluate(() => {
                  const vw = document.documentElement.clientWidth, found = [];
                  for (const el of document.querySelectorAll('#report *')) {
                    if (!el.offsetParent) continue;
                    const r = el.getBoundingClientRect();
                    if (!r.width) continue;
                    let right = vw, scroller = false;
                    for (let a = el.parentElement; a && a.id !== 'report'; a = a.parentElement) {
                      const o = getComputedStyle(a).overflowX;
                      if (o === 'auto' || o === 'scroll') { scroller = true; break; }
                      if (o === 'hidden' || o === 'clip') right = Math.min(right, a.getBoundingClientRect().right);
                    }
                    if (!scroller && r.right > right + 1)
                      found.push(`${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]} ${Math.round(r.right)} > ${Math.round(right)}`);
                  }
                  return found.slice(0, 5);
                });
              }
              await page.evaluate(() => [...document.querySelectorAll('#reportNav button')].find(b => b.textContent === 'Charts').click());
              await page.evaluate(() => { const t = [...document.querySelectorAll('.chart-tab')].find(b => /south/i.test(b.textContent)); if (t) t.click(); });
              out[w].chart = await page.evaluate(() => {
                const c = document.querySelector('#chartSouth .south-chart'), cr = c.getBoundingClientRect();
                const cells = [...c.querySelectorAll('.south-cell:not(.center)')].map(x => x.getBoundingClientRect());
                const panel = c.closest('.chart-panel').getBoundingClientRect();
                const all = [...c.querySelectorAll('.south-cell:not(.center)')];
                const crowdedTops = new Set(all.filter(x => x.querySelectorAll('.sc-planet').length > 2).map(x => Math.round(x.getBoundingClientRect().top)));
                return {left: cr.left, right: cr.right, panelLeft: panel.left, panelRight: panel.right, vw: document.documentElement.clientWidth,
                        widths: cells.map(r => Math.round(r.width)), heights: cells.map(r => Math.round(r.height)),
                        uncrowded: cells.map(r => !crowdedTops.has(Math.round(r.top))),
                        brokenNames: [...c.querySelectorAll('.sc-name')].filter(n => n.getClientRects().length > 1).map(n => n.textContent)};
              });
            }
            return out;
        """)

    def test_nothing_is_cut_off_on_a_phone(self):
        for w, got in self.r.items():
            for group, cut in got["cut"].items():
                self.assertEqual(cut, [], (w, group))

    def test_south_indian_chart_fits_with_square_cells(self):
        for w, got in self.r.items():
            c = got["chart"]
            self.assertGreaterEqual(c["left"], c["panelLeft"] - 1, (w, c))
            self.assertLessEqual(c["right"], min(c["panelRight"], c["vw"]) + 1, (w, c))
            self.assertLessEqual(max(c["widths"]) - min(c["widths"]), 2, (w, c["widths"]))      # four equal columns
            for wd, ht, free in zip(c["widths"], c["heights"], c["uncrowded"]):
                if free:                                     # a row holding a sign with 3+ planets grows so all show
                    self.assertLessEqual(abs(ht - wd), max(4, wd * 0.15), (w, wd, ht))             # square when uncrowded
            self.assertEqual(c["brokenNames"], [], w)        # a sign's name is never split across two lines


class Session24Remedies(unittest.TestCase):
    """The class of 22 Oct 2026: her Mars remedies on the Mars card (2nd, 7th, 8th, 12th), in the graha remedies list,
    and with the Kuja rows in the Kuja Doṣa section when the doṣa is present and not cancelled. Every row shows its
    source, under a plain "Remedies" heading (a row the user adds shows the user's source)."""

    @classmethod
    def setUpClass(cls):
        base = {"Sun": 10, "Moon": 100, "Mercury": 20, "Jupiter": 130, "Venus": 50, "Saturn": 200, "Rahu": 250, "Ketu": 70}
        cls.r = run_page("""
            await setBirth('1990-05-15', '06:30');
            await pickCity('Bengaluru');
            await generate();
            const base = %s, out = {};
            const marsIn = async lon => {
              await page.evaluate(sid => renderS23Sections(sid, 5, {retro: {Rahu: true, Ketu: true}}), Object.assign({}, base, {Mars: lon}));
              return page.evaluate(() => {
                const card = document.querySelector('#s23-view-layer .s23-gb[data-planet="Mars"]');
                const occ = document.querySelector('#s23-view-bhava .s23-bv-planet[data-role="occupant"][data-planet="Mars"]');
                const pad = el => el ? getComputedStyle(el).paddingLeft : null;
                return {card: [...card.querySelectorAll('ul.s23-remedies li')].map(li => li.textContent),
                        head: (card.querySelector('.s23-remedies-head') || {}).textContent || "",
                        bv: occ ? [...occ.querySelectorAll('ul.s23-remedies li')].length : 0,
                        pad: [pad(card.querySelector('ul.s23-remedies')), pad(card.querySelector('ul.s23-points'))],
                        bvPad: occ ? [pad(occ.querySelector('ul.s23-remedies')), pad(occ.querySelector('ul.s23-bv-side'))] : []};
              });
            };
            out.eighth = await marsIn(340);      // Meena = the 8th from Simha
            out.seventh = await marsIn(310);     // Kumbha = the 7th
            out.ninth = await marsIn(10);        // Mesha = the 9th
            await page.evaluate(() => renderGrahaReference());
            out.ref = await page.evaluate(() => {
              const box = document.getElementById('akshara-body');
              const entry = name => {
                const head = [...box.querySelectorAll('p strong')].find(s => s.textContent === name);
                const ul = head && head.closest('p').nextElementSibling;
                return {found: !!head, items: ul ? [...ul.querySelectorAll('li')].map(li => li.textContent) : [],
                        when: head ? head.closest('p').textContent : ""};
              };
              return {mars: entry('Mars'), kuja: entry('Kuja doṣa')};
            });
            const kuja = (byRashi, lagna) => page.evaluate(([b, l]) => {
              renderKujaSection(b, l, '1990-01-01', {Mars: (b.Mars - 1) * 30 + 10, Moon: 15});
              return [...document.querySelectorAll('#kuja-remedies li')].map(li => li.textContent);
            }, [byRashi, lagna]);
            out.kujaPresent = await kuja({Mars: 7, Venus: 3, Moon: 1, Saturn: 2}, 1);    // 7th from Mesha, nothing cancels
            out.kujaNone = await kuja({Mars: 10, Venus: 1, Moon: 1, Saturn: 2}, 1);      // the 10th from every reference
            out.kujaCancelled = await kuja({Mars: 11, Venus: 3, Moon: 1, Saturn: 2}, 5);  // Simha Lagna cancels (rule 3)
            await page.setViewportSize({width: 375, height: 800});
            await marsIn(340);
            const cut = sel => page.evaluate(sel => {          // as PhoneReport: nothing cut off at a clipping box's edge
              const vw = document.documentElement.clientWidth, found = [];
              for (const el of document.querySelectorAll(sel + ' *')) {
                if (!el.offsetParent) continue;
                const r = el.getBoundingClientRect();
                if (!r.width) continue;
                let right = vw, scroller = false;
                for (let a = el.parentElement; a && a.id !== 'report'; a = a.parentElement) {
                  const o = getComputedStyle(a).overflowX;
                  if (o === 'auto' || o === 'scroll') { scroller = true; break; }
                  if (o === 'hidden' || o === 'clip') right = Math.min(right, a.getBoundingClientRect().right);
                }
                if (!scroller && r.right > right + 1)
                  found.push(`${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]} ${Math.round(r.right)} > ${Math.round(right)}`);
              }
              return found.slice(0, 5);
            }, sel);
            await page.click('#reportNav button:has-text("Bhāvas")');
            await page.click('.s23-view-btn[data-view="layer"]');
            out.phoneLayer = {cut: await cut('#s23-view-layer'),
                              shown: await page.evaluate(() => document.querySelectorAll('#s23-view-layer .s23-gb[data-planet="Mars"] ul.s23-remedies li').length > 0
                                && document.querySelector('#s23-view-layer .s23-gb[data-planet="Mars"]').offsetParent !== null)};
            await page.click('.s23-view-btn[data-view="bhava"]');
            out.phoneBhava = await cut('#s23-view-bhava');
            out.phone = await page.evaluate(() => document.documentElement.scrollWidth);
            await page.evaluate(() => S23.remedies.push({topic: "Mars", text: "My own Mars remedy.", source: "me"}));
            out.userRow = await marsIn(340);
            return out;
        """ % json.dumps(base))
        import bhava_rules as br
        rules = br.load_rules()
        cls.mars = [x for x in rules["remedies"] if x["topic"] == "Mars"]
        cls.kuja = [x for x in rules["remedies"] if x["topic"] == "Kuja"]

    def assertRows(self, items, rows):
        """Each item is the row's text followed by its source."""
        self.assertEqual(len(items), len(rows), items)
        for got, want in zip(items, rows):
            got = " ".join(got.split())
            self.assertTrue(got.startswith(" ".join(want["text"].split())) and got.endswith(want["source"]), (got, want))

    def test_mars_card_in_the_8th_lists_her_remedies_with_their_sources(self):
        self.assertRows(self.r["eighth"]["card"], self.mars)
        self.assertEqual(self.r["eighth"]["head"], "Remedies")
        self.assertEqual(self.r["eighth"]["bv"], len(self.mars))

    def test_lists_are_indented_like_their_neighbours(self):
        self.assertEqual(self.r["eighth"]["pad"], ["18px", "18px"])
        self.assertEqual(self.r["eighth"]["bvPad"], ["18px", "18px"])

    def test_a_row_the_user_adds_shows_with_the_users_source(self):
        self.assertRows(self.r["userRow"]["card"], self.mars + [{"text": "My own Mars remedy.", "source": "me"}])
        self.assertEqual(self.r["userRow"]["head"], "Remedies")

    def test_mars_in_the_7th_shows_the_mars_rows_only(self):
        self.assertRows(self.r["seventh"]["card"], self.mars)                   # Kuja rows: Kuja section only
        self.assertEqual(self.r["seventh"]["bv"], len(self.mars))

    def test_mars_in_the_9th_has_none(self):
        self.assertEqual((self.r["ninth"]["card"], self.r["ninth"]["bv"]), ([], 0))

    def test_graha_remedies_list_has_mars_and_kuja_dosha(self):
        mars, kuja = self.r["ref"]["mars"], self.r["ref"]["kuja"]
        self.assertTrue(mars["found"] and kuja["found"])
        self.assertRows(mars["items"], self.mars)
        self.assertRows(kuja["items"], self.kuja)
        self.assertIn("2nd, 7th, 8th or 12th", mars["when"])
        self.assertIn("Kuja Doṣa section", kuja["when"])

    def test_kuja_section_lists_them_only_when_present_and_not_cancelled(self):
        self.assertRows(self.r["kujaPresent"], self.mars + self.kuja)
        self.assertEqual((self.r["kujaNone"], self.r["kujaCancelled"]), ([], []))

    def test_phone_has_no_sideways_scroll_and_nothing_is_cut_off(self):
        self.assertLessEqual(self.r["phone"], 375)
        self.assertTrue(self.r["phoneLayer"]["shown"])                  # the Mars card with its remedies is on screen
        self.assertEqual((self.r["phoneLayer"]["cut"], self.r["phoneBhava"]), ([], []))


# Sidereal positions from the Swiss Ephemeris 2.10 (pyswisseph, Moshier ephemeris, calc_ut with SEFLG_SIDEREAL):
# 60 random moments 1900-2100 in Lahiri, and Kusuma's chart (22 Feb 1975 16:30 IST) in Lahiri and KP-New, whose Mars
# sits 57" short of Capricorn in KP-New.
SWE_PLANETS = json.loads('{"bodies":["Sun","Mercury","Venus","Mars","Jupiter","Saturn"],"lahiri":[[2438540.70208,40.649516,15.717473,73.176407,19.742035,16.818145,311.323541],[2448000.867,5.313343,23.044398,319.977162,305.111457,71.376454,271.41511],[2453063.89845,315.222464,311.224338,358.950407,22.038396,140.679176,72.437873],[2434144.79607,28.297191,3.548603,16.53781,193.361704,9.987227,165.699135],[2469946.45094,34.591956,9.202126,68.287802,286.056892,94.96569,284.3581],[2447910.90325,275.330603,256.018885,274.582735,238.971149,69.201614,264.051421],[2428409.38799,132.376976,158.445528,148.972679,108.891881,232.069873,327.216944],[2450153.23766,326.632628,311.53588,11.351972,325.318634,259.47444,332.792436],[2419896.07458,24.700655,1.540431,4.650789,337.6977,265.180658,42.185447],[2439299.82884,68.020038,92.307929,32.899327,54.443546,76.941233,336.025114],[2468004.34839,279.751448,272.041165,266.574326,302.06792,291.226664,224.796091],[2440370.38736,43.91232,44.707314,359.944867,227.49595,152.719874,10.071722],[2486187.22194,198.633219,192.430267,207.720024,152.103776,8.696483,115.781988],[2473811.10864,241.711546,246.678552,220.977441,157.925194,66.753374,48.247921],[2469388.82163,202.036209,198.298815,242.888488,279.992125,65.77279,257.314435],[2484547.26401,25.488999,359.492213,59.724447,6.104767,232.822445,46.437354],[2447901.27292,265.524265,263.903189,280.025022,232.120439,70.343874,262.916434],[2429045.727,42.268476,18.315713,70.093829,59.767987,308.237878,351.731611],[2423812.41281,283.916886,260.747927,317.439962,222.414547,230.457766,189.365158],[2471563.65516,185.337785,167.11604,187.894206,69.451082,222.548574,326.400478],[2470927.05022,280.414295,291.675767,268.014914,20.149041,190.458784,306.863287],[2415861.17649,8.120993,359.965624,322.000689,3.166078,291.648945,275.082561],[2476085.77448,325.964338,298.958722,289.878053,258.371696,254.384349,131.7123],[2488411.54209,231.732025,237.672653,211.743992,212.584936,197.489122,189.660055],[2452865.01152,116.444268,143.792119,114.99982,314.762749,123.070008,74.876183],[2422626.44858,192.465096,216.0896,223.051619,254.87085,139.848283,148.258149],[2475076.68771,50.572016,49.213195,53.797127,63.997137,155.775666,92.501095],[2438959.0461,91.351468,118.098722,116.849083,166.403908,56.164013,323.543042],[2457781.19098,283.840552,260.988274,330.065867,335.49929,178.901464,240.106822],[2426236.08636,150.084385,160.52617,196.329685,78.76924,83.469978,252.405686],[2437055.74534,17.558781,0.34644,3.521059,329.006528,250.121914,265.116151],[2468426.29319,336.820812,310.869382,290.418628,191.009288,332.162159,238.625977],[2457459.96203,328.224897,317.987467,305.952975,218.14808,143.699768,232.18244],[2466831.86512,201.879967,192.778684,188.688593,110.759556,198.675404,185.197872],[2449588.53619,126.861803,137.448605,172.872187,70.912454,194.864313,315.880329],[2472669.92047,195.819428,215.676747,182.370734,217.203731,312.889818,7.215755],[2417993.00302,308.906703,322.324823,346.317644,6.296341,103.202653,334.13256],[2439318.27133,85.602491,107.661629,54.724344,67.044226,81.102877,336.301918],[2418080.73982,35.255334,48.522974,78.408585,65.242431,104.566767,344.361388],[2467660.75444,301.719277,295.278258,345.49733,155.101284,269.791315,215.316184],[2425012.62225,27.562405,18.205528,66.892679,81.931456,333.02632,222.598363],[2444579.68069,230.622272,216.955974,201.390192,257.176548,163.178144,164.549703],[2467775.31469,54.167649,52.090335,36.164021,148.268131,282.108688,210.835403],[2471240.29257,227.466011,219.642088,261.281576,211.982593,207.449696,313.690001],[2421343.31149,11.322529,31.513559,10.908159,359.658015,22.062762,91.744416],[2425308.88991,319.719692,304.764528,289.04686,280.270483,345.553403,235.743138],[2449012.55266,281.317937,282.270347,328.279958,77.85963,170.906103,295.29489],[2469752.03065,199.987089,207.201377,186.952976,167.862559,99.489233,267.698402],[2433641.18122,250.14215,264.598269,260.252877,284.895738,310.378332,158.916065],[2463136.32507,159.227146,161.479652,115.750426,236.20486,237.410832,58.65534],[2447412.52214,141.87969,167.312176,96.868066,346.686427,41.977439,242.288965],[2482058.37024,90.488823,115.877761,87.864848,111.031598,38.382104,326.393194],[2443050.11743,162.06445,150.169523,189.45378,179.586089,37.541015,110.218842],[2479610.15407,196.183078,209.248648,166.134852,241.814591,183.552932,241.80175],[2442730.73022,207.696092,199.146341,161.297132,68.710175,352.396993,99.452251],[2456489.96283,90.033484,80.112851,118.646463,67.915034,70.562012,190.824362],[2471657.69443,280.543026,273.017798,305.590412,53.282092,243.00723,328.848991],[2473251.80205,51.914166,74.925422,36.465272,139.681162,22.090215,31.3233],[2445405.02189,326.747154,313.675844,356.784685,347.509475,226.885265,190.200758],[2468976.08461,154.978182,181.198337,111.439543,126.928211,31.053355,243.813087]],"kusuma":{"lahiri":[309.683589,286.596729,335.308063,269.907454,330.681336,78.793875],"kp":[309.760315,286.673455,335.384789,269.98418,330.758062,78.870601],"jd":2442465.9583333335}}')


class PlanetPositions(unittest.TestCase):
    """The planets (VSOP87) agree with the Swiss Ephemeris to within 2", so a planet near a sign, nakshatra or pada
    boundary lands where other careful software puts it."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            return await page.evaluate((g) => {
              const ks = g.kusuma, t0 = performance.now();
              saturnSignStay(2460972.5, 'lahiri');
              const stayMs = performance.now() - t0;
              return {
                lahiri: g.lahiri.map(([j]) => g.bodies.map(b => computeChart(j, 'lahiri').sidereal[b])),
                kusuma: {lahiri: g.bodies.map(b => computeChart(ks.jd, 'lahiri').sidereal[b]),
                         kp: g.bodies.map(b => computeChart(ks.jd, 'kp').sidereal[b])},
                stayMs};
            }, opts.g);
        """, g=SWE_PLANETS)

    @staticmethod
    def arcsec(a, b):
        return abs(((a - b + 180) % 360) - 180) * 3600

    def test_every_planet_within_2_arcseconds(self):
        worst = {}
        for got, (_, *want) in zip(self.r["lahiri"], SWE_PLANETS["lahiri"]):
            for b, x, y in zip(SWE_PLANETS["bodies"], got, want):
                worst[b] = max(worst.get(b, 0), self.arcsec(x, y))
        self.assertTrue(all(v <= 2 for v in worst.values()), worst)

    def test_kusuma_matches_and_mars_stays_in_sagittarius(self):
        for mode in ("lahiri", "kp"):
            for b, x, y in zip(SWE_PLANETS["bodies"], self.r["kusuma"][mode], SWE_PLANETS["kusuma"][mode]):
                self.assertLessEqual(self.arcsec(x, y), 2, (mode, b))
            mars = self.r["kusuma"][mode][SWE_PLANETS["bodies"].index("Mars")]
            self.assertEqual(int(mars // 30), 8, (mode, mars))              # Dhanu, as the Swiss Ephemeris has it

    def test_saturn_sign_search_stays_quick(self):
        self.assertLess(self.r["stayMs"], 3000)


# The Swiss Ephemeris with its JPL-based files (DE431): 60 moments 1800-2200 UT at random places, sidereal
# Lahiri and KP-New, apparent and true (geometric) positions, the Lagna, and delta T; and 30 Lahiri Lagnas 1900-2040 at
# latitudes 64-66.4°, the 30 of 400 most sensitive to the obliquity ("high_lat"). Made by pyswisseph 2.10.
SWE_ORACLE = json.loads((HERE / "swe_oracle.json").read_text())

# Kusuma, 22 Feb 1975 16:30 IST, Nanjangud 12°7'4" N 76°41'2" E, as the Lahiri website the user compared shows her:
# it gives true (geometric) positions, which the Swiss Ephemeris matches to within 2.5".
KUSUMA_SITE = {"jd": 2442465.9583333335, "lat": 12 + 7 / 60 + 4 / 3600, "lon": 76 + 41 / 60 + 2 / 3600,
               "Sun": "10 09 41 21", "Moon": "02 19 16 22", "Mars": "08 29 54 59", "Mercury": "09 16 35 51",
               "Jupiter": "11 00 41 21", "Venus": "11 05 19 07", "Saturn": "02 18 47 31", "Rahu": "07 12 18 15",
               "Lagna": "03 11 46 14"}


def _sign_dms(s):
    sign, d, m, sec = map(int, s.split())
    return sign * 30 + d + m / 60 + sec / 3600


@needs_browser
class SwissOracle(unittest.TestCase):
    """The Moon, the Lagna, delta T and both kinds of position agree with the Swiss Ephemeris, so a chart reads the
    same, to the arc-second, as in careful software."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            return await page.evaluate((a) => {
              const g = a.g, k = a.k;
              const rows = g.rows.map(row => {
                const o = {dt: deltaTSeconds(row.jd)};
                for (const m of ['lahiri', 'kp']) {
                  const app = computeChart(row.jd, m, 'apparent').sidereal, tru = computeChart(row.jd, m, 'true').sidereal;
                  o[m] = {app: g.bodies.map(b => app[b]), true: g.bodies.map(b => tru[b]),
                          asc: computeLagna(row.jd, row.lat, row.lon, m)};
                }
                return o;
              });
              const c = computeChart(k.jd, 'lahiri', 'true').sidereal;
              const highLat = g.high_lat.map(row => computeLagna(row.jd, row.lat, row.lon, 'lahiri'));
              return {rows, highLat, kusuma: Object.assign({Lagna: computeLagna(k.jd, k.lat, k.lon, 'lahiri')}, c)};
            }, opts.a);
        """, a={"g": SWE_ORACLE, "k": KUSUMA_SITE})

    @staticmethod
    def arcsec(a, b):
        return abs(((a - b + 180) % 360) - 180) * 3600

    def worst(self, kind, bodies):
        out = {}
        for row, got in zip(SWE_ORACLE["rows"], self.r["rows"]):
            for mode in ("lahiri", "kp"):
                for b, x, y in zip(SWE_ORACLE["bodies"], got[mode][kind], row[mode][kind]):
                    if b in bodies:
                        out[b] = round(max(out.get(b, 0), self.arcsec(x, y)), 2)
        return out

    def test_moon_within_half_an_arcsecond(self):
        worst = self.worst("app", {"Moon"})
        self.assertLessEqual(worst["Moon"], 0.5, worst)

    def test_sun_and_planets_within_2_arcseconds_1800_to_2200(self):
        worst = self.worst("app", set(SWE_ORACLE["bodies"]) - {"Moon"})
        self.assertTrue(all(v <= 2 for v in worst.values()), worst)

    def test_true_positions_within_2_arcseconds(self):
        worst = self.worst("true", set(SWE_ORACLE["bodies"]))
        self.assertTrue(all(v <= 2 for v in worst.values()), worst)

    def test_lagna_within_a_fifth_of_an_arcsecond_1850_to_2050(self):
        # Outside 1850-2050 the Swiss Ephemeris turns to a long-term sidereal-time model of its own, up to 3" away.
        worst = {True: 0, False: 0}
        for row, got in zip(SWE_ORACLE["rows"], self.r["rows"]):
            inside = 1850 <= 2000 + (row["jd"] - 2451545) / 365.25 <= 2050
            for m in ("lahiri", "kp"):
                worst[inside] = max(worst[inside], self.arcsec(got[m]["asc"], row[m]["asc"]))
        self.assertLessEqual(worst[True], 0.2, worst)
        self.assertLessEqual(worst[False], 4, worst)

    def test_lagna_near_the_polar_circle(self):
        # 64-66.4° north or south, 1900-2040: the obliquity must be the one the Swiss Ephemeris uses (IAU 2006), as an
        # error in it grows towards the polar circle.
        worst = max(self.arcsec(got, row["asc"]) for row, got in zip(SWE_ORACLE["high_lat"], self.r["highLat"]))
        self.assertLessEqual(worst, 0.5, worst)

    def test_delta_t_within_a_second(self):
        worst = max(abs(got["dt"] - row["dt"]) for row, got in zip(SWE_ORACLE["rows"], self.r["rows"]))
        self.assertLessEqual(worst, 1, worst)

    def test_kusuma_true_positions_match_the_lahiri_website(self):
        for k, want in KUSUMA_SITE.items():
            if k in ("jd", "lat", "lon"):
                continue
            self.assertLessEqual(self.arcsec(self.r["kusuma"][k], _sign_dms(want)), 3, k)


@needs_browser
class PositionsSetting(unittest.TestCase):
    """The form's Positions choice: apparent by default, true (geometric) when picked; it is remembered and shown."""

    def test_default_choice_and_report_tag(self):
        r = run_page("""
            await setBirth('1975-02-22', '16:30');
            await pickCity('Bengaluru');
            const out = {initial: await page.$eval('#f-positions', s => s.value)};
            await generate();
            out.appTag = await page.$eval('#r-aytag', e => e.textContent);
            out.appMoon = await page.evaluate(() => currentChart.chart.sidereal.Moon);
            await page.selectOption('#f-positions', 'true');
            await generate();
            out.trueTag = await page.$eval('#r-aytag', e => e.textContent);
            out.trueMoon = await page.evaluate(() => currentChart.chart.sidereal.Moon);
            out.saved = await page.evaluate(() => JSON.parse(localStorage.getItem('vh_form_v1')).positions);
            return out;
        """)
        self.assertEqual(r["initial"], "apparent")
        self.assertNotIn("True", r["appTag"])
        self.assertIn("True positions", r["trueTag"])
        self.assertNotEqual(r["appMoon"], r["trueMoon"])
        self.assertEqual(r["saved"], "true")

    def test_saved_choice_is_restored(self):
        r = run_page("return await page.$eval('#f-positions', s => s.value);",
                     storage={"dob": "1975-02-22", "tob": "16:30", "positions": "true"})
        self.assertEqual(r, "true")


# True Astrology Pro 5.8.7.1 (KP), as the user's screenshots show it: Kusuma's chart, and its transit chart for
# 23 Oct 2026 18:23:49 IST at Nanjangud (slow grahas only: the transit's exact second is not certain).
TRUE_ASTROLOGY = {
    "natal": {"jd": 2442465.9583333335, "Sun": "10 09 46 25", "Moon": "02 19 21 48", "Mars": "08 29 59 51",
              "Mercury": "09 16 41 13", "Jupiter": "11 00 46 17", "Venus": "11 05 23 53", "Saturn": "02 18 53 02",
              "Rahu": "07 12 23 39", "Lagna": "03 11 50 20"},
    "transit": {"jd": 2461337.0373726850, "Mars": "03 20 06 24", "Jupiter": "03 29 04 18", "Venus": "06 06 59 09",
                "Saturn": "11 15 42 41", "Rahu": "10 02 22 42"},
}


@needs_browser
class TrueAstrologyKP(unittest.TestCase):
    """The "KP (True Astrology Pro)" ayanamsa reproduces that program to the arc-second: its ayanamsa and its Lagna
    (geocentric latitude, true equinox)."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_page("""
            return await page.evaluate((a) => {
              const out = {};
              for (const k of ['natal', 'transit']) {
                out[k] = computeChart(a[k].jd, 'kp-ta', 'apparent').sidereal;
                out[k].Lagna = computeLagna(a[k].jd, a.lat, a.lon, 'kp-ta');
              }
              out.option = [...document.querySelectorAll('#f-ayanamsa option')].find(o => o.value === 'kp-ta')?.textContent;
              return out;
            }, opts.a);
        """, a=dict(TRUE_ASTROLOGY, lat=KUSUMA_SITE["lat"], lon=KUSUMA_SITE["lon"]))

    def check(self, which):
        for k, want in TRUE_ASTROLOGY[which].items():
            if k != "jd":
                self.assertLessEqual(SwissOracle.arcsec(self.r[which][k], _sign_dms(want)), 1, (which, k))

    def test_kusuma_matches_true_astrology(self):
        self.check("natal")

    def test_transit_matches_true_astrology_51_years_later(self):
        self.check("transit")

    def test_the_form_offers_it(self):
        self.assertIn("True Astrology", self.r["option"])


# Places as Open-Meteo's GeoNames search returns them (the fields the page reads).
def _geo(name, lat, lon, tz, admin1, country, admin2="", pop=0):
    return {"id": abs(hash(name + admin1)) % 10 ** 7, "name": name, "latitude": lat, "longitude": lon, "timezone": tz,
            "admin1": admin1, "admin2": admin2, "country": country, "population": pop, "feature_code": "PPL"}


GEO_PLACES = [
    _geo("Hunsur", 12.30359, 76.29275, "Asia/Kolkata", "Karnataka", "India", "Mysuru", 50865),
    _geo("Gundlupet", 11.80999, 76.69033, "Asia/Kolkata", "Karnataka", "India", "Chamarajanagar", 29608),
    _geo("Nanjangud", 12.11764, 76.68397, "Asia/Kolkata", "Karnataka", "India", "Mysuru", 50598),
    _geo("Springfield", 39.80172, -89.64371, "America/Chicago", "Illinois", "United States", "Sangamon", 116250),
    _geo("Springfield", 42.10148, -72.58981, "America/New_York", "Massachusetts", "United States", "Hampden", 153606),
    _geo("Kovel", 51.21526, 24.70867, "Europe/Kyiv", "Volyn", "Ukraine", "", 68597),
    _geo("Kovilpatti", 9.17167, 77.86989, "Asia/Kolkata", "Tamil Nadu", "India", "Thoothukudi", 95057),
    _geo('<img src=x onerror="window.__pwned=1">Evil', 10.0, 10.0, "Africa/Lagos", "<b>Bold</b>", "Nowhere"),
]

PLACE_ITEMS = "() => [...document.querySelectorAll('#suggestions div[data-idx]')].map(d => d.textContent.replace(/\\s+/g, ' ').trim())"


@needs_browser
class PlaceSearch(unittest.TestCase):
    """The place box finds any city, town or village through the online GeoNames search, with its time zone;
    the built-in list still answers at once and when offline."""

    def test_any_town_from_the_online_search(self):
        r = run_page("""
            const asked = await mockGeo(opts.places);
            await setBirth('1975-02-22', '16:30');
            await page.type('#f-place', 'Huns');
            await page.waitForFunction(() => document.querySelector('#suggestions div[data-idx]')?.textContent.includes('Hunsur'));
            const out = {items: await page.evaluate(%s)};
            await page.evaluate(() => document.querySelector('#suggestions div[data-idx]').dispatchEvent(new MouseEvent('mousedown', {bubbles: true})));
            out.tz = await page.inputValue('#f-tz');
            out.hint = await page.textContent('#place-hint');
            await generate();
            out.meta = await page.textContent('#r-meta');
            out.asked = asked[asked.length - 1];
            out.lat = await page.evaluate(() => selectedCity[2]);
            return out;
        """ % PLACE_ITEMS, places=GEO_PLACES)
        self.assertEqual(r["items"], ["Hunsur · Mysuru, Karnataka, India"])
        self.assertEqual((r["asked"]["name"], r["asked"]["count"], r["asked"]["language"]), ("Huns", "10", "en"))
        self.assertEqual(r["tz"], "5.5")
        self.assertIn("Asia/Kolkata", r["hint"])
        self.assertIn("lat 12.3036", r["hint"])
        self.assertIn("Hunsur, Mysuru, Karnataka, India", r["meta"])
        self.assertAlmostEqual(r["lat"], 12.30359, places=4)

    def test_same_named_towns_are_told_apart(self):
        r = run_page("""
            await mockGeo(opts.places);
            await setBirth('1990-01-15', '10:00');
            await page.type('#f-place', 'Springf');
            await page.waitForFunction(() => document.querySelectorAll('#suggestions div[data-idx]').length === 2);
            const items = await page.evaluate(%s);
            await page.evaluate(() => [...document.querySelectorAll('#suggestions div[data-idx]')].find(d => d.textContent.includes('Massachusetts'))
              .dispatchEvent(new MouseEvent('mousedown', {bubbles: true})));
            return {items, tz: await page.inputValue('#f-tz'), hint: await page.textContent('#place-hint')};
        """ % PLACE_ITEMS, places=GEO_PLACES)
        self.assertEqual(sorted(r["items"]), ["Springfield · Hampden, Massachusetts, United States",
                                              "Springfield · Sangamon, Illinois, United States"])
        self.assertEqual(r["tz"], "-5")
        self.assertIn("America/New_York", r["hint"])

    def test_a_built_in_town_is_not_listed_twice(self):
        r = run_page("""
            await mockGeo(opts.places);
            await page.type('#f-place', 'Nanjan');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            return await page.evaluate(%s);
        """ % PLACE_ITEMS, places=GEO_PLACES)
        self.assertEqual(len([x for x in r if x.startswith("Nanjangud")]), 1, r)

    def test_offline_the_built_in_list_still_answers(self):
        r = run_page("""
            await page.type('#f-place', 'Mysu');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'failed');
            return {items: await page.evaluate(%s),
                    note: await page.evaluate(() => document.querySelector('#suggestions .sug-note')?.textContent || '')};
        """ % PLACE_ITEMS)
        self.assertIn("Mysuru · Karnataka, India", r["items"])
        self.assertIn("built-in", r["note"])

    def test_names_from_the_search_are_shown_as_text(self):
        r = run_page("""
            await mockGeo(opts.places);
            await setBirth('1990-01-15', '10:00');
            await page.type('#f-place', '<img');
            await page.waitForFunction(() => document.querySelector('#suggestions div[data-idx]'));
            const out = {imgs: await page.evaluate(() => document.querySelectorAll('#suggestions img, #suggestions b').length)};
            await page.evaluate(() => document.querySelector('#suggestions div[data-idx]').dispatchEvent(new MouseEvent('mousedown', {bubbles: true})));
            await generate();
            out.hintImgs = await page.evaluate(() => document.querySelectorAll('#place-hint img, #r-meta img').length);
            out.pwned = await page.evaluate(() => window.__pwned || 0);
            out.meta = await page.textContent('#r-meta');
            return out;
        """, places=GEO_PLACES)
        self.assertEqual((r["imgs"], r["hintImgs"], r["pwned"]), (0, 0, 0))
        self.assertIn("<img", r["meta"])

    def test_a_late_answer_does_not_replace_a_newer_one(self):
        r = run_page("""
            await mockGeo(opts.places, {kov: 1500});
            await page.type('#f-place', 'Kov');
            await page.waitForTimeout(600);                    // the 'Kov' search is sent, and answers late
            await page.type('#f-place', 'i');
            await page.waitForFunction(() => document.querySelector('#suggestions div[data-idx]')?.textContent.includes('Kovilpatti'));
            await page.waitForTimeout(1500);                   // the late 'Kov' answer arrives
            return await page.evaluate(%s);
        """ % PLACE_ITEMS, places=GEO_PLACES)
        self.assertEqual(r, ["Kovilpatti · Thoothukudi, Tamil Nadu, India"])

    def test_a_typed_name_counts_when_only_one_place_has_it(self):
        r = run_page("""
            await mockGeo(opts.places);
            await setBirth('1975-02-22', '16:30');
            await page.type('#f-place', 'Gundlupet');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            await generate();                                  // not picked from the list: the one exact match is used
            const out = {meta: await page.textContent('#r-meta')};
            await page.fill('#f-place', '');
            await page.type('#f-place', 'Springfield');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            await page.click('#btn-generate');
            out.msg = await page.textContent('#msg');
            await page.fill('#f-place', '');
            await page.type('#f-place', 'Springfield, Massachusetts');   // the state says which one
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            await generate();
            out.meta2 = await page.textContent('#r-meta');
            return out;
        """, places=GEO_PLACES)
        self.assertIn("Gundlupet, Chamarajanagar, Karnataka, India", r["meta"])
        self.assertIn("pick", r["msg"].lower())
        self.assertIn("Springfield, Hampden, Massachusetts, United States", r["meta2"])

    def test_a_saved_online_place_comes_back(self):
        saved = ["Hunsur", "Mysuru, Karnataka, India", 12.30359, 76.29275, 5.5, "Asia/Kolkata"]
        r = run_page("return await page.textContent('#place-hint');",
                     storage={"dob": "1975-02-22", "tob": "16:30", "place": "Hunsur", "selectedCity": saved})
        self.assertIn("Hunsur, Mysuru, Karnataka, India", r)
        self.assertIn("Asia/Kolkata", r)

    def test_the_hint_credits_the_search(self):
        r = run_page("return await page.innerHTML('#place-hint');")
        self.assertIn("open-meteo.com", r)
        self.assertIn("GeoNames", r)

    def test_current_location_can_be_any_town(self):
        r = run_page("""
            await mockGeo(opts.places);
            await pickCurCity('Gundlupet');
            return await page.evaluate(() => ({value: document.getElementById('f-curcity').value,
              rahu: document.getElementById('pane-rahukaal').textContent,
              choghadiya: document.getElementById('choghadiya-body').textContent}));
        """, places=GEO_PLACES, clock="2026-10-10T09:00:00+05:30")
        self.assertEqual(r["value"], "Gundlupet")
        self.assertIn("Rāhu Kaalam — Gundlupet", r["rahu"])
        self.assertIn("Choughadiya — Gundlupet", r["choghadiya"])


@needs_browser
class PlaceSearchReviewFixes(unittest.TestCase):
    """Review of the place search: leaving the box, a typed place kept, "Name, State", no time zone, re-typing."""

    def test_a_late_answer_does_not_reopen_the_list_after_leaving(self):
        r = run_page("""
            await mockGeo(opts.places, {huns: 800});
            await page.type('#f-place', 'Huns');
            await page.click('#f-name');
            await page.waitForTimeout(1500);
            return await page.evaluate(() => document.getElementById('suggestions').classList.contains('show'));
        """, places=GEO_PLACES)
        self.assertFalse(r)

    def test_a_typed_place_is_kept_like_a_picked_one(self):
        r = run_page("""
            await mockGeo(opts.places);
            await setBirth('1975-02-22', '16:30');
            await page.type('#f-place', 'Gundlupet');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            await generate();
            return await page.evaluate(() => JSON.parse(localStorage.getItem('vh_form_v1')).selectedCity);
        """, places=GEO_PLACES)
        self.assertEqual(r[0], "Gundlupet")
        self.assertEqual(r[5], "Asia/Kolkata")

    def test_a_state_asks_for_more_places_and_says_when_it_matches_none(self):
        r = run_page("""
            const asked = await mockGeo(opts.places);
            await page.type('#f-place', 'Springfield, Vermont');
            await page.waitForFunction(() => document.querySelector('#suggestions')?.dataset.online === 'done');
            return {count: asked[asked.length - 1].count, items: await page.evaluate(%s),
                    note: await page.evaluate(() => document.querySelector('#suggestions .sug-note')?.textContent || '')};
        """ % PLACE_ITEMS, places=GEO_PLACES)
        self.assertEqual(r["count"], "100")
        self.assertIn("Vermont", r["note"])
        self.assertEqual(len(r["items"]), 2)                     # the places of that name are still offered

    def test_a_place_without_a_time_zone_warns(self):
        place = dict(GEO_PLACES[0], name="Notz", timezone=None)
        r = run_page("""
            await mockGeo(opts.places);
            await setBirth('1975-02-22', '16:30');
            await pickCity('Notz');
            return await page.textContent('#place-hint');
        """, places=[place])
        self.assertIn("time zone", r.lower())
        self.assertIn("check", r.lower())

    def test_clicking_the_current_location_selects_it_for_retyping(self):
        r = run_page("""
            await mockGeo(opts.places);
            await page.click('#f-curcity');
            await page.keyboard.type('Gund');
            return await page.inputValue('#f-curcity');
        """, places=GEO_PLACES)
        self.assertEqual(r, "Gund")
