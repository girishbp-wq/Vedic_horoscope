#!/usr/bin/env python3
"""Build the Session 23 rules from the master workbook:

    Classification_for_Horoscope_Analysis_v7_1.xlsx  (sheets prefixed S23_)
        ->  session23_rules.json  +  the SESSION23-DATA block of index.html

    python3 build_session23.py                  # master workbook found next to this file
    python3 build_session23.py --workbook FILE  # any workbook that has the S23_ sheets (e.g. an --export copy)

`publish.bat` runs this right after scripts/build_data.py, so one double-click rebuilds everything.
The S23_ sheets are the editable source of truth (edit a text or a class rule, save, publish).
`reference` in the JSON is a copy of the page's own tables (bhāva significations, rāśi classifications,
dignity, aspects, daśā constants).  It is read from the master workbook with the same loaders
scripts/build_data.py uses; where that script is not available it is read from index.html through node.
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = ROOT / "session23_rules.json"
INDEX = ROOT / "index.html"
MASTER_GLOB = "Classification_for_Horoscope_Analysis_*.xlsx"
PREFIX = "S23_"

HEAD_FILL = PatternFill("solid", fgColor="6B1D2B")
HEAD_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")

PROFILE_KEYS = ["Relationships", "Profession / Status", "Reputation", "Personality Traits",
                "Body Parts Ruled", "General Health Indicator", "Nature", "Combustion Effect",
                "Soul / Mind / Body"]
REFERENCE_NAMES = ["BHAVA_INFO", "RASHI", "RASHI_DIGNITY", "DIGNITY_DEG", "PLANET_OWN_HOUSES",
                   "NATURAL_FRIENDS", "KARAKATWAS", "SPECIAL_ASPECTS", "VORDER", "VYEARS",
                   "COMBUST_ORB", "COMBUST_PLANETS", "NAKSHATRAS", "PLANET_PROFILE"]
# Constants the page holds itself (not in the workbook); test_session23_data checks them against the live page.
FIXED_REFERENCE = {
    "VORDER": ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"],
    "VYEARS": {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17},
    "COMBUST_ORB": 5,
    "COMBUST_PLANETS": ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
}

# sheet name -> header row.  (The data sheets only; calculator sheets are added by make_session23_xlsx.py.)
SHEETS = {
    PREFIX + "Classes": ["No", "Class", "SlideName", "Houses", "OtherNames", "Nature", "Rule", "Slides"],
    PREFIX + "ClassRules": ["Class", "AppliesTo", "ExcludeHouses", "Text", "Slide"],
    PREFIX + "Badhaka": ["Mode", "House"],
    PREFIX + "DignityEffect": ["Label", "Band", "Text", "Status", "Slide"],
    PREFIX + "Digbala": ["Planet", "StrongHouse", "LostHouse", "Status", "Source"],
    PREFIX + "DashaRoleText": ["Role", "Kind", "Text", "Slide"],
    PREFIX + "GrahaInBhava": ["Planet", "House", "Points", "Extra", "Status", "Source"],
    PREFIX + "GrahaPair": ["A", "B", "Conjunction", "Aspect", "Status", "Source"],
    PREFIX + "BhavaLordIn": ["LordOf", "SitsIn", "Text", "Status", "Source"],
    PREFIX + "GrahaRashi": ["Planet", "Rashi", "Text", "Status", "Source"],
}
LONG_COLUMNS = ("Nature", "Rule", "Text", "Points", "Extra", "Conjunction", "Aspect", "Source", "OtherNames")

README_LINES = [
    "Session 23 rules — editable source of truth (sheets whose names start with S23_)",
    "Edit any cell in the S23_ data sheets, save, then double-click publish.bat (or run python build_session23.py).",
    "Status column: taught = the teacher's own content (slides / recording);  curated = drafted by blending her karakatwas, not yet taught;  blend = generated from templates;  standard = a standard rule the teacher has not stated yet.",
    "Houses are comma lists (1, 4, 7, 10). Points: one paragraph per blank-line-separated block; Extra: one line each.",
    "Keep the S23_ClassRules rows grouped in the order of the ten classes (Kendra … Trishadaya): the Excel calculator joins their texts in sheet order.",
    "S23_Chart, S23_Classes_Calc, S23_Roles_Calc, S23_Dasha_Calc, S23_Predict_Calc and S23_Ref_Calc are the live calculator (formulas) — set the signs on S23_Chart.",
    "When a later session teaches a graha, replace its 'curated' rows and set Status to taught.",
]


# ---------------------------------------------------------------- sheets <-> rules dict
def _ints(text):
    return [int(x) for x in str(text).replace(";", ",").split(",") if str(x).strip()]


def _join_ints(values):
    return ", ".join(str(v) for v in values)


def rules_to_rows(rules):
    """The rules dict as sheet rows, keyed by (prefixed) sheet name — the inverse of read_workbook()."""
    return {
        PREFIX + "Classes": [[c["no"], c["name"], c["slide_name"], _join_ints(c["houses"]) if c["houses"] else "by Lagna",
                              c["other_names"], c["nature"], c["rule"], c["slides"]] for c in rules["classes"]],
        PREFIX + "ClassRules": [[r["class"], r["applies"], _join_ints(r["exclude_houses"]), r["text"], r["slide"]]
                                for r in rules["class_rules"]],
        PREFIX + "Badhaka": [[m, h] for m, h in rules["badhaka"].items()],
        PREFIX + "DignityEffect": [[k, v["band"], v["text"], v["status"], v["slide"]] for k, v in rules["dignity_effect"].items()],
        PREFIX + "Digbala": [[p, v["strong"], v["lost"], v["status"], v["source"]] for p, v in rules["digbala"].items()],
        PREFIX + "DashaRoleText": [[k, v["kind"], v["text"], v["slide"]] for k, v in rules["dasha_role_text"].items()],
        PREFIX + "GrahaInBhava": [[r["planet"], r["house"], "\n\n".join(r["points"]), "\n".join(r["extra"]), r["status"], r["source"]]
                                  for r in rules["graha_in_bhava"]],
        PREFIX + "GrahaPair": [[r["a"], r["b"], r["conjunction"], r["aspect"], r["status"], r["source"]] for r in rules["graha_pair"]],
        PREFIX + "BhavaLordIn": [[r["lord_of"], r["sits_in"], r["text"], r["status"], r["source"]] for r in rules["bhava_lord_in"]],
        PREFIX + "GrahaRashi": [[r["planet"], r["rashi"], r["text"], r["status"], r["source"]] for r in rules["graha_rashi"]],
    }


def write_data_sheets(wb, rules):
    """Create (replacing any existing) the S23_ data sheets in `wb` from the rules dict."""
    rows = rules_to_rows(rules)
    for name, header in SHEETS.items():
        if name in wb.sheetnames:
            del wb[name]
        sh = wb.create_sheet(name)
        for j, h in enumerate(header, 1):
            c = sh.cell(row=1, column=j, value=h)
            c.fill, c.font = HEAD_FILL, HEAD_FONT
        for i, row in enumerate(rows[name], 2):
            for j, v in enumerate(row, 1):
                sh.cell(row=i, column=j, value=v).alignment = WRAP
        for j, h in enumerate(header, 1):
            sh.column_dimensions[chr(64 + j)].width = 70 if h in LONG_COLUMNS else 16
        sh.freeze_panes = "A2"
        sh.sheet_properties.tabColor = "6B1D2B"


def write_readme_sheet(wb):
    name = PREFIX + "README"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws.column_dimensions["A"].width = 130
    for i, line in enumerate(README_LINES, 1):
        c = ws.cell(row=i, column=1, value=line)
        c.alignment = WRAP
        c.font = Font(bold=(i == 1), size=14 if i == 1 else 11, color="6B1D2B" if i == 1 else "000000")
    ws.sheet_properties.tabColor = "6B1D2B"


def _sheet_rows(wb, name):
    it = wb[name].iter_rows(min_row=2, values_only=True)
    return [list(r) for r in it if any(v not in (None, "") for v in r)]


def _s(v):
    return "" if v is None else str(v)


def has_session23_sheets(wb):
    return all(name in wb.sheetnames for name in SHEETS)


def read_workbook(path_or_wb):
    """S23_ data sheets -> the rules dict (everything in the JSON except `reference` and `meta`)."""
    wb = path_or_wb if hasattr(path_or_wb, "sheetnames") else load_workbook(path_or_wb, data_only=True)
    missing = [n for n in SHEETS if n not in wb.sheetnames]
    if missing:
        raise SystemExit(f"Workbook has no Session 23 sheets {missing}. Run: python make_session23_xlsx.py --install")
    rows = lambda short: _sheet_rows(wb, PREFIX + short)
    out = {}
    out["classes"] = [dict(no=int(r[0]), name=r[1], slide_name=r[2],
                           houses=None if _s(r[3]).strip() in ("", "by Lagna") else _ints(r[3]),
                           other_names=_s(r[4]), nature=_s(r[5]), rule=_s(r[6]), slides=_s(r[7]))
                      for r in rows("Classes")]
    out["class_rules"] = [{"class": r[0], "applies": r[1], "exclude_houses": _ints(r[2]) if _s(r[2]).strip() else [],
                           "text": _s(r[3]), "slide": _s(r[4])} for r in rows("ClassRules")]
    out["badhaka"] = {r[0]: int(r[1]) for r in rows("Badhaka")}
    out["dignity_effect"] = {r[0]: dict(band=r[1], text=_s(r[2]), status=r[3], slide=_s(r[4])) for r in rows("DignityEffect")}
    out["digbala"] = {r[0]: dict(strong=int(r[1]), lost=int(r[2]), status=r[3], source=_s(r[4])) for r in rows("Digbala")}
    out["dasha_role_text"] = {r[0]: dict(kind=r[1], text=_s(r[2]), slide=_s(r[3])) for r in rows("DashaRoleText")}
    out["graha_in_bhava"] = [dict(planet=r[0], house=int(r[1]),
                                  points=[p for p in _s(r[2]).split("\n\n") if p.strip()],
                                  extra=[p for p in _s(r[3]).split("\n") if p.strip()],
                                  status=r[4], source=_s(r[5])) for r in rows("GrahaInBhava")]
    out["graha_pair"] = [dict(a=r[0], b=r[1], conjunction=_s(r[2]), aspect=_s(r[3]), status=r[4], source=_s(r[5]))
                         for r in rows("GrahaPair")]
    out["bhava_lord_in"] = [dict(lord_of=int(r[0]), sits_in=int(r[1]), text=_s(r[2]), status=r[3], source=_s(r[4]))
                            for r in rows("BhavaLordIn")]
    out["graha_rashi"] = [dict(planet=r[0], rashi=int(r[1]), text=_s(r[2]), status=r[3], source=_s(r[4]))
                          for r in rows("GrahaRashi")]
    return out


# ---------------------------------------------------------------- reference tables
GRAB_JS = r"""
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
function grab(name) {
  const m = new RegExp('\\b(?:const|let|var)\\s+' + name + '\\s*=\\s*').exec(src);
  if (!m) throw new Error('missing ' + name);
  let i = m.index + m[0].length; const start = i; let depth = 0, q = null;
  for (; i < src.length; i++) {
    const c = src[i], n = src[i + 1];
    if (q) { if (c === '\\') { i++; continue; } if (c === q) q = null; continue; }
    if (c === '/' && n === '/') { while (i < src.length && src[i] !== '\n') i++; continue; }
    if (c === '/' && n === '*') { i = src.indexOf('*/', i + 2) + 1; continue; }
    if (c === '"' || c === "'" || c === '`') { q = c; continue; }
    if ('{[('.includes(c)) depth++;
    else if ('}])'.includes(c)) depth--;
    else if (c === ';' && depth === 0) break;
  }
  // convert Sets inside the context: a Set made in a vm realm is not `instanceof Set` out here
  return vm.runInNewContext('(function(){ var v = ' + src.slice(start, i) + '; return v instanceof Set ? Array.from(v) : v; })()');
}
const out = {};
for (const name of JSON.parse(process.argv[2])) out[name] = grab(name);
console.log(JSON.stringify(out));
"""


def _trim_profile(profile):
    return {planet: {k: prof[k] for k in PROFILE_KEYS if k in prof} for planet, prof in profile.items()}


def extract_reference(index_path=INDEX):
    """The reference tables as the page holds them, read from index.html through node."""
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is required to read the page's reference tables")
    p = subprocess.run([node, "-e", GRAB_JS, str(index_path), json.dumps(REFERENCE_NAMES)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"reference extraction failed: {p.stderr[-600:]}")
    ref = json.loads(p.stdout)
    ref["PLANET_PROFILE"] = _trim_profile(ref["PLANET_PROFILE"])
    return ref


def load_build_data(root=ROOT):
    """Import scripts/build_data.py (the page builder) so its sheet loaders can be reused; None if absent."""
    path = pathlib.Path(root) / "scripts" / "build_data.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("build_data_for_session23", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def reference_from_workbook(wb, bd):
    """The reference tables built from the master workbook's own sheets, with build_data.py's loaders —
    the same values scripts/build_data.py writes into index.html."""
    rashi = bd.load_rashi(wb)
    dignity, lord_by_rashi = bd.load_dignity(wb)
    plts = bd.load_planets(wb)
    ref = {
        "BHAVA_INFO": {str(h): v for h, v in bd.load_bhava_info(wb).items()},
        "RASHI": [dict(r, lord=lord_by_rashi.get(r["n"], "")) for r in rashi],
        "RASHI_DIGNITY": {str(n): v for n, v in dignity.items()},
        "DIGNITY_DEG": plts["DIGNITY_DEG"],
        "PLANET_OWN_HOUSES": bd.derive_own_houses(lord_by_rashi),
        "NATURAL_FRIENDS": plts["NATURAL_FRIENDS"],
        "KARAKATWAS": plts["KARAKATWAS"],
        "SPECIAL_ASPECTS": plts["SPECIAL_ASPECTS"],
        "NAKSHATRAS": bd.load_nakshatras(wb)["NAKSHATRAS"],
        "PLANET_PROFILE": _trim_profile(bd.load_planet_profile(wb)),
    }
    ref.update(json.loads(json.dumps(FIXED_REFERENCE)))
    return {name: ref[name] for name in REFERENCE_NAMES}


# ---------------------------------------------------------------- build
DATA_START = "/* SESSION23-DATA-START — generated from the S23_ sheets of the master workbook by build_session23.py; do not edit by hand */"
DATA_END = "/* SESSION23-DATA-END */"
ENGINE_START = "/* SESSION23-ENGINE-START"


def page_data_block(rules):
    """The generated `const S23 = {...}` block: the rules without `reference` (the page has those tables itself)."""
    lines = [DATA_START, "const S23 = {"]
    keys = [k for k in rules if k not in ("reference", "meta")]
    for i, k in enumerate(keys):
        body = json.dumps(rules[k], ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        lines.append(f" {json.dumps(k)}: {body}{',' if i < len(keys) - 1 else ''}")
    lines += ["};", DATA_END]
    return "\n".join(lines) + "\n"


def write_page_block(index_path, rules):
    """Replace (or, the first time, insert before the engine block) the SESSION23-DATA block in index.html."""
    index_path = pathlib.Path(index_path)
    page = index_path.read_text(encoding="utf-8")
    block = page_data_block(rules)
    marker = DATA_START.split(" — ")[0]            # tolerate an older marker comment after the name
    if marker in page:
        a = page.index(marker)
        z = page.index(DATA_END, a) + len(DATA_END) + 1
        new = page[:a] + block + page[z:]
    else:
        if ENGINE_START not in page:
            raise RuntimeError("index.html has no SESSION23-ENGINE block to anchor the data block")
        i = page.index(ENGINE_START)
        new = page[:i] + block + page[i:]
    if new != page:
        index_path.write_text(new, encoding="utf-8")
    return new != page


def find_master(root=ROOT):
    """The master workbook, chosen the way scripts/build_data.py chooses it (v7_1 first, else the newest)."""
    root = pathlib.Path(root)
    preferred = root / "Classification_for_Horoscope_Analysis_v7_1.xlsx"
    if preferred.exists():
        return preferred
    found = sorted(root.glob(MASTER_GLOB))
    return found[-1] if found else None


def build(xlsx_path=None, json_path=JSON_PATH, index_path=INDEX, write_page=False, reference=None, root=ROOT):
    """S23_ sheets of the workbook -> JSON (and, with write_page, the index.html data block).

    `reference` may be passed in (tests); otherwise it comes from the master's own sheets through
    scripts/build_data.py, or — when that script is not there — from index.html through node."""
    xlsx_path = pathlib.Path(xlsx_path) if xlsx_path else find_master(root)
    if not xlsx_path or not xlsx_path.exists():
        raise SystemExit(f"No {MASTER_GLOB} workbook found in {root}")
    json_path = pathlib.Path(json_path)
    wb = load_workbook(xlsx_path, data_only=True)
    rules = read_workbook(wb)
    if reference is None:
        bd = load_build_data(root)
        reference = reference_from_workbook(wb, bd) if bd else extract_reference(index_path)
    rules["reference"] = reference
    rules["meta"] = {"source": "Session 23 slides + recording (8 Oct 2026)", "version": 1,
                     "statuses": ["taught", "curated", "blend", "standard"]}
    json_path.write_text(json.dumps(rules, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if write_page:
        write_page_block(index_path, rules)
    return rules


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    wb = None
    if "--workbook" in argv:
        wb = argv[argv.index("--workbook") + 1]
    rules = build(wb, write_page=True)
    print(f"Session 23: {len(rules['graha_in_bhava'])} graha-in-bhava rows, {len(rules['graha_pair'])} pairs "
          f"-> {JSON_PATH.name} and the SESSION23-DATA block of {INDEX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
