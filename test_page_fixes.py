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


if __name__ == "__main__":
    unittest.main()
