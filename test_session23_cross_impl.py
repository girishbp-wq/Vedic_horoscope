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


if __name__ == "__main__":
    unittest.main()
