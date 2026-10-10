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
        self.assertEqual(len(r["tips"]), 3)
        self.assertTrue(r["tips"][0].startswith(tips[0]["text"].split("\n")[0]), r["tips"][0])
        self.assertIn("S24 p.38", r["tips"][0])


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
            await page.selectOption('#f-curcity', {label: 'London — UK'});  // 22:30 BST on the 9th
            out.london = await read();
            await page.fill('#f-curdate', '2026-10-08');
            await page.dispatchEvent('#f-curdate', 'change');
            await page.selectOption('#f-curcity', {label: 'Bengaluru — Karnataka, India'});
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
            await page.selectOption('#f-curcity', {label: 'London — UK'});
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
