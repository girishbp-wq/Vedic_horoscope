"""Cross-implementation tests for Session 23: the page's JavaScript vs bhava_rules.py.

python3 -m unittest -v test_session23_cross_impl
The JS runs in headless Chromium against the real index.html (all network blocked); results are compared to
the Python engine on random charts by canonical-JSON fingerprint, and a mismatch is reported with the first
differing path."""
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import unittest

import bhava_rules as br

ROOT = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
JSON_PATH = ROOT / "session23_rules.json"
RULES = br.load_rules()
NODE, NPM = shutil.which("node"), shutil.which("npm")


def _pw():
    if not (NODE and NPM):
        return None
    root = subprocess.run([NPM, "root", "-g"], capture_output=True, text=True).stdout.strip()
    p = pathlib.Path(root) / "playwright"
    return str(p) if p.exists() and os.path.isdir(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")) else None


PW = _pw()

# --------------------------------------------------------------------------------------- canonical form
def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def fingerprint(o):
    s = canon(o)
    h = 0x811C9DC5
    b = s.encode("utf-16-le")
    for i in range(0, len(b), 2):
        h = ((h ^ (b[i] | (b[i + 1] << 8))) * 0x01000193) & 0xFFFFFFFF
    return [len(s), h]


NODE_RUNNER = r"""
const { chromium } = require(process.env.PW_MODULE);
(async () => {
  const job = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch({headless: true});
  const ctx = await b.newContext({timezoneId: 'UTC'});
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  await p.goto('file://' + job.index);
  const out = await p.evaluate(new Function('job', job.body), job.arg);
  console.log(JSON.stringify({out, errors}));
  await b.close();
})();
"""


def run_page(body, arg, tmp):
    """Run JS `body` (a function body receiving `job`) on the loaded page; returns the JSON-able result."""
    job = tmp / "job.json"
    runner = tmp / "runner.js"
    job.write_text(json.dumps({"index": str(INDEX), "body": body, "arg": arg}), encoding="utf-8")
    runner.write_text(NODE_RUNNER, encoding="utf-8")
    env = dict(os.environ, PW_MODULE=PW, PLAYWRIGHT_BROWSERS_PATH="/opt/pw-browsers")
    p = subprocess.run([NODE, str(runner), str(job)], capture_output=True, text=True, timeout=600, env=env)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-1500:])
    res = json.loads(p.stdout.strip().splitlines()[-1])
    if res["errors"]:
        raise AssertionError("page errors: " + "; ".join(res["errors"]))
    return res["out"]


JS_CANON = r"""
function canon(v){
  if (Array.isArray(v)) return '[' + v.map(canon).join(',') + ']';
  if (v === undefined) return '"__undefined__"';
  if (v && typeof v === 'object') return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}';
  return JSON.stringify(v);
}
function fp(v){ const s = canon(v); let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return [s.length, h]; }
const PL = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"];
function layers(c){
  const lg = c.lagna + 1, pbr = {}; for (const p of PL) pbr[p] = c.signs[p] + 1;
  return {
    tables: s23ClassificationTables(lg, pbr), matrix: s23HouseClassMatrix(lg), badhaka: s23Badhaka(lg, pbr),
    roles: s23Roles(lg, pbr), readings: s23ClassReadings(lg, pbr, c.waxing),
    graha_bhava: PL.map(p => s23GrahaBhava(lg, pbr, p, c.degs[p], c.waxing)),
    bhava_bhava: s23BhavaBhava(lg, pbr), graha_rashi: s23GrahaRashi(lg, pbr, c.degs),
    graha_graha: s23GrahaGraha(lg, pbr, c.degs),
    five_step: [1,2,3,4,5,6,7,8,9,10,11,12].map(h => s23FiveStep(lg, pbr, h)),
  };
}
"""


def python_layers(c):
    lg, sg, degs, w = c["lagna"], c["signs"], c["degs"], c["waxing"]
    return {
        "tables": br.classification_tables(RULES, lg, sg), "matrix": br.house_class_matrix(RULES, lg),
        "badhaka": br.badhaka(RULES, lg, sg), "roles": br.planet_roles(RULES, lg, sg),
        "readings": br.class_readings(RULES, lg, sg, w),
        "graha_bhava": [br.graha_bhava(RULES, lg, sg, p, degs[p], w) for p in br.PLANET_ORDER],
        "bhava_bhava": br.bhava_bhava(RULES, lg, sg), "graha_rashi": br.graha_rashi(RULES, lg, sg, degs),
        "graha_graha": br.graha_graha(RULES, lg, sg, degs),
        "five_step": [br.five_step(RULES, lg, sg, h) for h in range(1, 13)],
    }


def random_charts(n, seed):
    rnd = random.Random(seed)
    charts = []
    for _ in range(n):
        pool = rnd.sample(range(12), rnd.choice([3, 5, 12]))
        signs = {p: rnd.choice(pool) for p in br.PLANET_ORDER}
        charts.append({"lagna": rnd.randrange(12), "signs": signs, "waxing": rnd.random() < 0.5,
                       "degs": {p: round(rnd.uniform(0, 29.99), 2) for p in br.PLANET_ORDER}})
    return charts


def first_difference(a, b, path="$"):
    if type(a) != type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        return f"{path}: type {type(a).__name__} vs {type(b).__name__}"
    if isinstance(a, dict):
        if set(a) != set(b):
            return f"{path}: keys {sorted(set(a) ^ set(b))}"
        for k in a:
            d = first_difference(a[k], b[k], f"{path}.{k}")
            if d:
                return d
    elif isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_difference(x, y, f"{path}[{i}]")
            if d:
                return d
    elif a != b:
        return f"{path}: {a!r} vs {b!r}"
    return None


SRC = INDEX.read_text(encoding="utf-8")


class PageBlocks(unittest.TestCase):
    def test_block_markers_once(self):
        marks = ["/* SESSION23-DATA-START", "/* SESSION23-DATA-END", "/* SESSION23-ENGINE-START", "/* SESSION23-ENGINE-END"]
        pos = []
        for m in marks:
            self.assertEqual(SRC.count(m), 1, m)
            pos.append(SRC.index(m))
        self.assertEqual(pos, sorted(pos))
        self.assertLess(pos[-1], SRC.index("function renderPredictive(){"))
        self.assertGreater(pos[0], SRC.index("/* ASHTAKAVARGA-END */"))

    def test_page_data_block_is_current(self):
        import build_session23 as b23
        a = SRC.index(b23.DATA_START)
        z = SRC.index(b23.DATA_END) + len(b23.DATA_END) + 1
        self.assertEqual(SRC[a:z], b23.page_data_block(json.loads(JSON_PATH.read_text(encoding="utf-8"))),
                         "run python3 build_session23.py to refresh the page's data block")

    def test_no_duplicate_function_declarations_added(self):
        names = re.findall(r"^\s*function\s+([A-Za-z0-9_$]+)\s*\(", SRC, re.M)
        dup = sorted({n for n in names if names.count(n) > 1})
        # two renderClassificationSection declarations pre-date this work
        self.assertEqual([n for n in dup if n != "renderClassificationSection"], [])
        engine = SRC[SRC.index("/* SESSION23-ENGINE-START"):SRC.index("/* SESSION23-ENGINE-END")]
        mine = re.findall(r"function\s+([A-Za-z0-9_$]+)\s*\(", engine)
        self.assertTrue(mine and all(n.startswith("s23") for n in mine), mine)
        before = SRC[:SRC.index("/* SESSION23-ENGINE-START")] + SRC[SRC.index("/* SESSION23-ENGINE-END"):]
        self.assertEqual([n for n in mine if re.search(r"function\s+" + n + r"\s*\(", before)], [])


@unittest.skipUnless(PW, "playwright + chromium needed")
class JsEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp_dir = tempfile.TemporaryDirectory()
        cls.tmp = pathlib.Path(cls.tmp_dir.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_dir.cleanup()

    def test_generated_data_equals_json(self):
        rules = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        want = {k: v for k, v in rules.items() if k not in ("reference", "meta")}
        got = run_page("return S23;", None, self.tmp)
        self.assertIsNone(first_difference(want, got))

    def test_js_equals_python_on_2000_random_charts(self):
        charts = random_charts(2000, 2310)
        body = JS_CANON + "return job.map(c => { const r = layers(c); const o = {}; for (const k in r) o[k] = fp(r[k]); return o; });"
        got = run_page(body, charts, self.tmp)
        bad = []
        for i, (c, g) in enumerate(zip(charts, got)):
            mine = python_layers(c)
            for k, v in mine.items():
                if fingerprint(v) != g[k]:
                    bad.append((i, k))
        if bad:
            i, k = bad[0]
            full = run_page(JS_CANON + "return layers(job);", charts[i], self.tmp)[k]
            self.fail(f"{len(bad)} mismatches; first: chart {i} layer {k}: "
                      f"{first_difference(python_layers(charts[i])[k], full)}")

    def test_moon_waxing_matches_python_and_the_page_tithi(self):
        rnd = random.Random(7)
        pairs = [[rnd.uniform(0, 360), rnd.uniform(0, 360)] for _ in range(3000)]
        pairs += [[10.0, 10.0], [0.0, 180.0], [0.0, 179.999], [100.0, 99.0], [350.0, 170.0], [350.0, 169.9]]
        body = "return job.map(([s, m]) => [s23MoonWaxing(s, m), computeTithi(s, m).tithiNum <= 15]);"
        got = run_page(body, pairs, self.tmp)
        for (s, m), (js, tithi) in zip(pairs, got):
            self.assertEqual((js, tithi), (br.moon_waxing(s, m),) * 2, (s, m))

    def test_oracle_chart_in_the_page(self):
        c = {"lagna": 4, "signs": {"Moon": 6, "Ketu": 7, "Saturn": 9, "Jupiter": 10, "Mars": 3, "Sun": 2,
                                   "Venus": 2, "Mercury": 1, "Rahu": 1},
             "waxing": True, "degs": {p: 12.5 for p in br.PLANET_ORDER}}
        got = run_page(JS_CANON + "const r = layers(job); return {roles: r.roles, asp: r.graha_graha.aspects.map(a => [a.by, a.to, a.house_aspect])};",
                       c, self.tmp)
        self.assertEqual(got["roles"]["Saturn"], ["Maraka lord", "Dusthana lord", "Trishadaya lord"])
        self.assertEqual(len(got["asp"]), 12)


BROWSER_SCRIPT = r"""
const { chromium } = require(process.env.PW_MODULE);
const indexUrl = 'file://' + process.argv[2];
const shots = process.env.S23_ARTIFACT_DIR || '';
const BIRTHS = [
  {dob:'1990-05-15', tob:'06:30:00', lat:'19.08',  lon:'72.88',  tz:'5.5'},
  {dob:'1975-11-02', tob:'22:10:00', lat:'13.0',   lon:'77.6',   tz:'5.5'},
  {dob:'2001-02-28', tob:'13:45:00', lat:'51.5',   lon:'-0.12',  tz:'0'},
];
const EXTRACT = () => {
  const $ = (s, r = document) => [...r.querySelectorAll(s)];
  const norm = s => s.replace(/\s+/g, ' ').trim();
  const classes = {};
  $('#s23-classes-body table.s23-table[data-class]').forEach(t => {
    classes[t.dataset.class] = $('tbody tr[data-house]', t).map(tr => ({
      house: +tr.dataset.house, sign: +tr.dataset.sign, lord: tr.dataset.lord,
      lord_house: tr.dataset.lordHouse === '' ? null : +tr.dataset.lordHouse,
      skt: tr.querySelector('.s23-skt').textContent, abbr: tr.querySelector('.s23-abbr').textContent,
      planets: $('.s23-pl', tr).map(x => x.dataset.p), text: norm(tr.innerText)}));
  });
  const m = document.getElementById('s23-matrix');
  const bad = document.getElementById('s23-badhaka');
  const predict = document.getElementById('s23-predict-body');
  return {
    sid: currentChart.chart.sidereal, lagna: currentChart.lagnaRashi.n,
    classes, titles: $('#report details.section .section-title').map(x => x.textContent),
    classHeadings: $('#s23-classes-body .s23-class-block .s23-class-head').map(x => norm(x.innerText)),
    matrixHead: m ? $('thead th[data-class]', m).map(th => th.dataset.class) : null,
    matrix: m ? $('tbody tr[data-house]', m).map(tr => ({house: +tr.dataset.house,
              classes: $('td[data-class]', tr).filter(td => td.dataset.in === '1').map(td => td.dataset.class),
              cells: $('td[data-class]', tr).length})) : null,
    badhaka: bad ? {mode: bad.dataset.mode, house: +bad.dataset.house, sign: +bad.dataset.sign, lord: bad.dataset.lord,
                    occupants: bad.dataset.occupants ? bad.dataset.occupants.split(',') : [], text: norm(bad.innerText)} : null,
    readings: $('#s23-readings tbody tr[data-planet]').map(tr => ({planet: tr.dataset.planet, house: +tr.dataset.house,
              nature: tr.dataset.nature, classes: tr.dataset.classes ? tr.dataset.classes.split(',') : [],
              texts: $('li', tr).map(li => norm(li.innerText))})),
    fivestep: $('#s23-fivestep tbody tr[data-house]').map(tr => ({house: +tr.dataset.house, lord: tr.dataset.lord,
              lord_house: +tr.dataset.lordHouse, occupants: tr.dataset.occupants ? tr.dataset.occupants.split(',') : [],
              aspecting: tr.dataset.aspecting ? tr.dataset.aspecting.split(',') : [], karakas: tr.dataset.karakas ? tr.dataset.karakas.split(',') : []})),
    gb: $('#s23-predict-body .s23-gb').map(c => ({planet: c.dataset.planet, house: +c.dataset.house, status: c.dataset.status,
              dig: norm(c.querySelector('.s23-dig').textContent), digLine: norm((c.querySelector('.s23-dig-line') || {textContent: ''}).textContent),
              digbala: norm((c.querySelector('.s23-digbala-line') || {textContent: ''}).textContent),
              points: $('.s23-points > li', c).map(li => norm(li.innerText)),
              extra: $('.s23-extra > li', c).map(li => norm(li.innerText)),
              classTexts: $('.s23-class-texts > li', c).map(li => norm(li.innerText)),
              tags: $('.s23-tag', c).map(x => x.textContent)})),
    bb: $('#s23-bb tbody tr[data-lord-of]').map(tr => ({lord_of: +tr.dataset.lordOf, sits_in: +tr.dataset.sits, lord: tr.dataset.lord,
              status: tr.dataset.status, text: norm(tr.querySelector('.s23-text').textContent), tags: $('.s23-tag', tr).map(x => x.textContent)})),
    gr: $('#s23-gr tbody tr[data-planet]').map(tr => ({planet: tr.dataset.planet, sign: +tr.dataset.sign, status: tr.dataset.status,
              tatwa: tr.dataset.tatwa, direction: tr.dataset.direction, varna: tr.dataset.varna, mode: tr.dataset.mode,
              dignity: tr.dataset.dignity, text: norm(tr.nextElementSibling.textContent), tags: $('.s23-tag', tr).map(x => x.textContent)})),
    conj: $('#s23-conj > li').map(li => ({a: li.dataset.a, b: li.dataset.b, house: +li.dataset.house, status: li.dataset.status,
              combust: li.dataset.combust, text: norm(li.querySelector('.s23-text').textContent),
              note: norm((li.querySelector('.s23-combust') || {textContent: ''}).textContent)})),
    asp: $('#s23-asp > li').map(li => ({by: li.dataset.by, to: li.dataset.to, h: +li.dataset.h, status: li.dataset.status,
              text: norm(li.querySelector('.s23-text').textContent), jup: !!li.querySelector('.s23-jup')})),
    predictText: predict ? predict.innerText : '',
    classesText: document.getElementById('s23-classes-body').innerText,
  };
};
(async () => {
  const browser = await chromium.launch({headless: true});
  const ctx = await browser.newContext({viewport: {width: 1280, height: 900}});
  const blocked = [];
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue()
                                : (blocked.push(r.request().url()), r.abort()));
  const page = await ctx.newPage();
  const jsErrors = [];
  page.on('pageerror', e => jsErrors.push(String(e)));
  await page.goto(indexUrl);
  await page.click('#btn-manual');
  const out = {charts: [], jsErrors, blocked: null};
  for (const [i, b] of BIRTHS.entries()) {
    await page.fill('#f-dob', b.dob);
    await page.fill('#f-tob', b.tob);
    await page.fill('#f-lat', b.lat); await page.press('#f-lat', 'Tab');
    await page.fill('#f-lon', b.lon); await page.press('#f-lon', 'Tab');
    await page.fill('#f-tz', b.tz);
    await page.click('#btn-generate');
    await page.waitForSelector('#report.show');
    await page.click('#reportNav button:has-text("Bhāvas")');
    const d = await page.evaluate(EXTRACT);
    d.nav = await page.evaluate(() => {
      const grp = [...document.querySelectorAll('#reportNav button')].map(b => b.textContent);
      const mine = [...document.querySelectorAll('#report details.section')].filter(s => /Bhāva Analysis/.test(s.querySelector('.section-title').textContent))
        .map(s => ({title: s.querySelector('.section-title').textContent, grp: s.dataset.grp, shown: getComputedStyle(s).display !== 'none'}));
      return {grp, mine};
    });
    out.charts.push(d);
    if (i === 0) {
      await page.click('#reportNav button:has-text("Planetary")');
      out.hiddenElsewhere = await page.evaluate(() => [...document.querySelectorAll('#report details.section')]
        .filter(s => /Bhāva Analysis/.test(s.querySelector('.section-title').textContent)).map(s => getComputedStyle(s).display));
      await page.click('#reportNav button:has-text("Bhāvas")');
      out.noLagna = await page.evaluate(() => { renderS23Sections(currentChart.chart.sidereal, 0);
        return {classes: document.getElementById('s23-classes-body').innerText, predict: document.getElementById('s23-predict-body').innerText,
                tables: document.querySelectorAll('#s23-classes-body table, #s23-predict-body table').length}; });
      await page.evaluate(() => renderS23Sections(currentChart.chart.sidereal, currentChart.lagnaRashi.n));
      out.layout = {};
      if (shots) await page.locator('#s23-classes-body').screenshot({path: shots + '/s23_classes_desktop.png'});
      if (shots) await page.locator('#s23-predict-body').screenshot({path: shots + '/s23_predict_desktop.png'});
      await page.setViewportSize({width: 375, height: 800});
      out.layout.phone = await page.evaluate(() => ({vw: window.innerWidth, pageScrollW: document.documentElement.scrollWidth,
        wrappers: [...document.querySelectorAll('#s23-classes-body .table-scroll, #s23-predict-body .table-scroll')].map(w => {
          const tb = w.querySelector('table');
          return {w: Math.round(w.getBoundingClientRect().width), id: tb.id || tb.dataset.class || '',
                  scrolls: w.scrollWidth > w.clientWidth || tb.scrollWidth > tb.clientWidth}; })}));
      if (shots) await page.locator('#s23-classes-body').screenshot({path: shots + '/s23_classes_phone.png'});
      await page.setViewportSize({width: 1280, height: 900});
      await page.emulateMedia({media: 'print'});
      out.layout.print = await page.evaluate(() => {
        const sections = [...document.querySelectorAll('#report details.section')].filter(s => /Bhāva Analysis/.test(s.querySelector('.section-title').textContent));
        const skt = document.querySelector('#s23-classes-body .s23-skt'), abbr = document.querySelector('#s23-classes-body .s23-abbr');
        return {display: sections.map(s => getComputedStyle(s).display), skt: getComputedStyle(skt).display, abbr: getComputedStyle(abbr).display};
      });
      await page.setViewportSize({width: 695, height: 1000});
      out.layout.printA4 = await page.evaluate(() =>
        [...document.querySelectorAll('#s23-classes-body .table-scroll, #s23-predict-body .table-scroll')].map(w => {
          const t = w.querySelector('table');
          return {id: t.id || t.dataset.class || '', wrapClient: w.clientWidth, wrapScroll: w.scrollWidth, tableScroll: t.scrollWidth,
                  headers: [...t.querySelectorAll('thead th')].map(th => ({txt: th.innerText.replace(/\s+/g, ' ').trim(), cw: th.clientWidth,
                    sw: (() => { const r = document.createRange(); r.selectNodeContents(th); return Math.ceil(r.getBoundingClientRect().width); })()}))};
        }));
      await page.setViewportSize({width: 1280, height: 900});
      if (shots) await page.pdf({path: shots + '/s23_print.pdf', format: 'A4', printBackground: true});
      await page.emulateMedia({media: 'screen'});
    }
  }
  out.blocked = blocked;
  console.log(JSON.stringify(out));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def _norm(s):
    return " ".join(str(s).split())


def page_chart(d):
    sid = d["sid"]
    signs = {p: int((sid[p] % 360) // 30) for p in br.PLANET_ORDER}
    degs = {p: (sid[p] % 360) - 30 * signs[p] for p in br.PLANET_ORDER}
    return d["lagna"] - 1, signs, degs, br.moon_waxing(sid["Sun"], sid["Moon"])


@unittest.skipUnless(PW, "playwright + chromium needed")
class BrowserSession23(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dict(os.environ, PW_MODULE=PW, PLAYWRIGHT_BROWSERS_PATH="/opt/pw-browsers")
        import tempfile
        cls.tmp_dir = tempfile.TemporaryDirectory()
        script = pathlib.Path(cls.tmp_dir.name) / "browser.js"
        script.write_text(BROWSER_SCRIPT, encoding="utf-8")
        p = subprocess.run([NODE, str(script), str(INDEX)], capture_output=True, text=True, timeout=600, env=env)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.out = json.loads(p.stdout.strip().splitlines()[-1])

    @classmethod
    def tearDownClass(cls):
        cls.tmp_dir.cleanup()

    def test_no_js_errors_and_no_network(self):
        self.assertEqual(self.out["jsErrors"], [])
        # the page's own font and sheet-logger requests are blocked; the new sections must not add any host
        import urllib.parse
        hosts = {urllib.parse.urlparse(u).netloc for u in self.out["blocked"]}
        self.assertLessEqual(hosts, {"fonts.googleapis.com", "script.google.com"})

    def test_sections_sit_in_the_bhavas_group(self):
        for d in self.out["charts"]:
            self.assertEqual([m["title"] for m in d["nav"]["mine"]],
                             ["Bhāva Analysis — the 12 Houses", "Bhāva Analysis — The 10 Bhāva Classes",
                              "Bhāva Analysis — Prediction Layers"])
            self.assertTrue(all(m["shown"] and m["grp"] == "3" for m in d["nav"]["mine"]), d["nav"])
        self.assertEqual(self.out["hiddenElsewhere"], ["none", "none", "none"])

    def test_ten_class_tables_equal_python(self):
        for d in self.out["charts"]:
            lg, signs, degs, w = page_chart(d)
            want = br.classification_tables(RULES, lg, signs)
            self.assertEqual(list(d["classes"]), br.CLASS_ORDER)
            for name, rows in want.items():
                got = d["classes"][name]
                self.assertEqual([(r["house"], r["sign"], r["planets"], r["lord"], r["lord_house"]) for r in got],
                                 [(r["house"], r["sign"], r["planets"], r["lord"], r["lord_house"]) for r in rows], name)
                for r in got:
                    self.assertEqual(r["skt"], RULES["reference"]["RASHI"][r["sign"]]["sanskrit"])
                    self.assertEqual(r["abbr"], RULES["reference"]["RASHI"][r["sign"]]["english"][:3])
            self.assertEqual(len(d["classHeadings"]), 10)
            self.assertIn("Apachaya", d["classHeadings"][5])
            self.assertIn("1, 2, 4, 7, 8", d["classHeadings"][5])

    def test_matrix_has_12_rows_10_classes(self):
        for d in self.out["charts"]:
            lg, *_ = page_chart(d)
            self.assertEqual(d["matrixHead"], br.CLASS_ORDER)
            self.assertEqual(len(d["matrix"]), 12)
            self.assertTrue(all(r["cells"] == 10 for r in d["matrix"]))
            self.assertEqual([(r["house"], r["classes"]) for r in d["matrix"]],
                             [(r["house"], r["classes"]) for r in br.house_class_matrix(RULES, lg)])

    def test_badhaka_block(self):
        for d in self.out["charts"]:
            lg, signs, degs, w = page_chart(d)
            want = br.badhaka(RULES, lg, signs)
            b = d["badhaka"]
            self.assertEqual((b["mode"], b["house"], b["sign"], b["lord"], b["occupants"]),
                             (want["mode"], want["house"], want["sign"], want["lord"], want["occupants"]))
            self.assertIn("a sign, not the horoscope", b["text"])

    def test_readings_and_five_step_equal_python(self):
        for d in self.out["charts"]:
            lg, signs, degs, w = page_chart(d)
            want = br.class_readings(RULES, lg, signs, w)
            self.assertEqual([(r["planet"], r["house"], r["classes"], [_norm(x) for x in r["texts"]]) for r in want],
                             [(r["planet"], r["house"], r["classes"], r["texts"]) for r in d["readings"]])
            for r in d["readings"]:
                self.assertEqual(r["nature"], br.nature(r["planet"], signs, w))
            for h, got in zip(range(1, 13), d["fivestep"]):
                f = br.five_step(RULES, lg, signs, h)
                self.assertEqual((got["house"], got["lord"], got["lord_house"], got["occupants"]),
                                 (h, f["lord"], f["lord_house"], f["occupants"]))
                self.assertEqual(got["aspecting"], [f"{a['by']}:{a['house_aspect']}" for a in f["aspecting"]])
                self.assertEqual(got["karakas"], [f"{k['planet']}:{k['house']}" for k in f["karakas"]])

    def test_prediction_layers_equal_python_and_show_status_tags(self):
        for d in self.out["charts"]:
            lg, signs, degs, w = page_chart(d)
            for g, p in zip(d["gb"], br.PLANET_ORDER):
                want = br.graha_bhava(RULES, lg, signs, p, degs[p], w)
                self.assertEqual((g["planet"], g["house"], g["status"]), (p, want["house"], want["status"]))
                self.assertEqual(g["dig"], want["dignity"]["label"])
                self.assertEqual(g["digLine"], _norm(want["dignity_line"]))
                self.assertEqual(g["digbala"], _norm(want["digbala_line"]))
                self.assertEqual(g["points"], [_norm(x) for x in want["points"]])
                self.assertEqual(g["extra"], [_norm(x) for x in want["extra"]])
                self.assertEqual(g["classTexts"], [_norm(x) for x in want["class_texts"]])
                self.assertIn(want["status"], g["tags"])
            for r, want in zip(d["bb"], br.bhava_bhava(RULES, lg, signs)):
                self.assertEqual((r["lord_of"], r["sits_in"], r["lord"], r["status"], r["text"]),
                                 (want["lord_of"], want["sits_in"], want["lord"], want["status"], _norm(want["text"])))
                self.assertIn(want["status"], r["tags"])
            for r, want in zip(d["gr"], br.graha_rashi(RULES, lg, signs, degs)):
                self.assertEqual((r["planet"], r["sign"], r["status"], r["tatwa"], r["direction"], r["varna"], r["mode"], r["dignity"], r["text"]),
                                 (want["planet"], want["sign"], want["status"], want["tatwa"], want["direction"], want["varna"],
                                  want["mode"], want["dignity"], _norm(want["text"])))
            gg = br.graha_graha(RULES, lg, signs, degs)
            self.assertEqual([(c["a"], c["b"], c["house"], c["status"], _norm(c["text"])) for c in gg["conjunctions"]],
                             [(c["a"], c["b"], c["house"], c["status"], c["text"]) for c in d["conj"]])
            self.assertEqual([c["note"] for c in d["conj"]], [_norm(c["combust_note"]) for c in gg["conjunctions"]])
            self.assertEqual([(a["by"], a["to"], a["house_aspect"], a["status"], _norm(a["text"]), a["jupiter_flag"]) for a in gg["aspects"]],
                             [(a["by"], a["to"], a["h"], a["status"], a["text"], a["jup"]) for a in d["asp"]])
            self.assertIn("taught", d["predictText"].lower())      # the legend explains the tags
            self.assertIn("curated", d["predictText"].lower())

    def test_sections_explain_missing_lagna(self):
        n = self.out["noLagna"]
        self.assertEqual(n["tables"], 0)
        self.assertIn("Lagna", n["classes"])
        self.assertIn("Lagna", n["predict"])

    def test_phone_tables_scroll_in_their_box(self):
        ph = self.out["layout"]["phone"]
        self.assertLessEqual(ph["pageScrollW"], ph["vw"] + 1, "the page itself must not scroll sideways")
        self.assertTrue(ph["wrappers"])
        for w in ph["wrappers"]:
            self.assertLessEqual(w["w"], ph["vw"], w)
        self.assertTrue(next(w for w in ph["wrappers"] if w["id"] == "s23-matrix")["scrolls"])

    def test_print_fits_a4_without_clipped_headers(self):
        pr = self.out["layout"]["print"]
        self.assertNotIn("none", pr["display"])
        self.assertEqual((pr["skt"], pr["abbr"]), ("none", "inline"))
        wraps = self.out["layout"]["printA4"]
        self.assertTrue(wraps)
        for w in wraps:
            self.assertLessEqual(w["wrapScroll"], w["wrapClient"] + 1, w)
            self.assertLessEqual(w["tableScroll"], w["wrapClient"] + 1, w)
            for h in w["headers"]:
                self.assertLessEqual(h["sw"], h["cw"] + 1, (w["id"], h))


if __name__ == "__main__":
    unittest.main()
