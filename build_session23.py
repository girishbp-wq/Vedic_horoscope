#!/usr/bin/env python3
"""Build the Session 23 rules: Session23_Rules.xlsx  ->  session23_rules.json  (+ index.html data block).

    python3 build_session23.py            # read the workbook, rewrite the JSON (and the page block)
    python3 build_session23.py --seed     # first-time / developer: rewrite the workbook from
                                          # session23_rule_data.py, then build as above

The workbook is the editable source of truth.  Edit a cell (a curated text, a class rule…), run this
script, and the JSON, Python engine, page and Excel calculator all pick the change up.
`reference` in the JSON is a copy of the page's own tables (bhava significations, rāśi
classifications, dignity, aspects, dasha constants) read straight out of index.html so Python and Excel
never keep a second copy by hand.
"""
import json
import pathlib
import shutil
import subprocess
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

import session23_rule_data as data

ROOT = pathlib.Path(__file__).resolve().parent
XLSX = ROOT / "Session23_Rules.xlsx"
JSON_PATH = ROOT / "session23_rules.json"
INDEX = ROOT / "index.html"

HEAD_FILL = PatternFill("solid", fgColor="6B1D2B")
HEAD_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")

PROFILE_KEYS = ["Relationships", "Profession / Status", "Reputation", "Personality Traits",
                "Body Parts Ruled", "General Health Indicator", "Nature", "Combustion Effect",
                "Soul / Mind / Body"]
REFERENCE_NAMES = ["BHAVA_INFO", "RASHI", "RASHI_DIGNITY", "DIGNITY_DEG", "PLANET_OWN_HOUSES",
                   "NATURAL_FRIENDS", "KARAKATWAS", "SPECIAL_ASPECTS", "VORDER", "VYEARS",
                   "COMBUST_ORB", "COMBUST_PLANETS", "NAKSHATRAS", "PLANET_PROFILE"]

README = [
    "Session 23 rules — editable source of truth",
    "Edit any cell, then run:  python3 build_session23.py   (rebuilds session23_rules.json and the index.html data block).",
    "Status column: taught = the teacher's own content (slides / recording);  curated = drafted by blending her karakatwas, not yet taught;  blend = generated from templates;  standard = a standard rule the teacher has not stated yet.",
    "Houses are written as comma lists (1, 4, 7, 10). Text lists: one paragraph per blank-line-separated block (Points) or one line each (Extra).",
    "When a later session teaches a graha, replace its 'curated' rows and set Status to taught.",
]

SHEETS = {
    "Classes": ["No", "Class", "SlideName", "Houses", "OtherNames", "Nature", "Rule", "Slides"],
    "ClassRules": ["Class", "AppliesTo", "ExcludeHouses", "Text", "Slide"],
    "Badhaka": ["Mode", "House"],
    "DignityEffect": ["Label", "Band", "Text", "Status", "Slide"],
    "Digbala": ["Planet", "StrongHouse", "LostHouse", "Status", "Source"],
    "DashaRoleText": ["Role", "Kind", "Text", "Slide"],
    "GrahaInBhava": ["Planet", "House", "Points", "Extra", "Status", "Source"],
    "GrahaPair": ["A", "B", "Conjunction", "Aspect", "Status", "Source"],
    "BhavaLordIn": ["LordOf", "SitsIn", "Text", "Status", "Source"],
    "GrahaRashi": ["Planet", "Rashi", "Text", "Status", "Source"],
}


def _ints(text):
    return [int(x) for x in str(text).replace(";", ",").split(",") if str(x).strip()]


def _join_ints(values):
    return ", ".join(str(v) for v in values)


def seed_rows():
    """The seed content as sheet rows, in the order of SHEETS."""
    d = data
    rows = {
        "Classes": [[c["no"], c["name"], c["slide_name"], _join_ints(c["houses"]) if c["houses"] else "by Lagna",
                     c["other_names"], c["nature"], c["rule"], c["slides"]] for c in d.CLASSES],
        "ClassRules": [[r["class"], r["applies"], _join_ints(r["exclude_houses"]), r["text"], r["slide"]]
                       for r in d.CLASS_RULES],
        "Badhaka": [[m, h] for m, h in d.BADHAKA_BY_MODE.items()],
        "DignityEffect": [[k, v["band"], v["text"], v["status"], v["slide"]] for k, v in d.DIGNITY_EFFECT.items()],
        "Digbala": [[p, v["strong"], v["lost"], v["status"], v["source"]] for p, v in d.DIGBALA.items()],
        "DashaRoleText": [[k, v["kind"], v["text"], v["slide"]] for k, v in d.DASHA_ROLE_TEXT.items()],
        "GrahaInBhava": [[r["planet"], r["house"], "\n\n".join(r["points"]), "\n".join(r["extra"]),
                          r["status"], r["source"]] for r in d.SUN_ROWS],
        "GrahaPair": [[r["a"], r["b"], r["conjunction"], r["aspect"], r["status"], r["source"]]
                      for r in d.TAUGHT_PAIRS],
        "BhavaLordIn": [[r["lord_of"], r["sits_in"], r["text"], r["status"], r["source"]]
                        for r in d.TAUGHT_BHAVA_LORD_IN],
        "GrahaRashi": [[r["planet"], r["rashi"], r["text"], r["status"], r["source"]] for r in d.TAUGHT_GRAHA_RASHI],
    }
    try:  # rows authored in later tasks
        import session23_curated as cur
        rows["GrahaInBhava"] += [[r["planet"], r["house"], "\n\n".join(r["points"]), "\n".join(r.get("extra", [])),
                                  r["status"], r["source"]] for r in cur.GRAHA_BHAVA]
        rows["GrahaPair"] += [[r["a"], r["b"], r["conjunction"], r["aspect"], r["status"], r["source"]]
                              for r in cur.PAIRS]
    except ImportError:
        pass
    return rows


def seed_workbook(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    ws.column_dimensions["A"].width = 130
    for i, line in enumerate(README, 1):
        c = ws.cell(row=i, column=1, value=line)
        c.alignment = WRAP
        c.font = Font(bold=(i == 1), size=14 if i == 1 else 11, color="6B1D2B" if i == 1 else "000000")
    rows = seed_rows()
    for name, header in SHEETS.items():
        sh = wb.create_sheet(name)
        for j, h in enumerate(header, 1):
            c = sh.cell(row=1, column=j, value=h)
            c.fill, c.font = HEAD_FILL, HEAD_FONT
        for i, row in enumerate(rows[name], 2):
            for j, v in enumerate(row, 1):
                c = sh.cell(row=i, column=j, value=v)
                c.alignment = WRAP
        for j, h in enumerate(header, 1):
            long_col = h in ("Nature", "Rule", "Text", "Points", "Extra", "Conjunction", "Aspect", "Source", "OtherNames")
            sh.column_dimensions[chr(64 + j)].width = 70 if long_col else 16
        sh.freeze_panes = "A2"
    wb.save(path)


def _sheet_rows(wb, name):
    sh = wb[name]
    it = sh.iter_rows(min_row=2, values_only=True)
    return [list(r) for r in it if any(v not in (None, "") for v in r)]


def _s(v):
    return "" if v is None else str(v)


def read_workbook(path):
    """Workbook -> the rules dict (everything in the JSON except `reference` and `meta`)."""
    wb = load_workbook(path)
    out = {}
    out["classes"] = [dict(no=int(r[0]), name=r[1], slide_name=r[2],
                           houses=None if _s(r[3]).strip() in ("", "by Lagna") else _ints(r[3]),
                           other_names=_s(r[4]), nature=_s(r[5]), rule=_s(r[6]), slides=_s(r[7]))
                      for r in _sheet_rows(wb, "Classes")]
    out["class_rules"] = [{"class": r[0], "applies": r[1], "exclude_houses": _ints(r[2]) if _s(r[2]).strip() else [],
                           "text": _s(r[3]), "slide": _s(r[4])} for r in _sheet_rows(wb, "ClassRules")]
    out["badhaka"] = {r[0]: int(r[1]) for r in _sheet_rows(wb, "Badhaka")}
    out["dignity_effect"] = {r[0]: dict(band=r[1], text=_s(r[2]), status=r[3], slide=_s(r[4]))
                             for r in _sheet_rows(wb, "DignityEffect")}
    out["digbala"] = {r[0]: dict(strong=int(r[1]), lost=int(r[2]), status=r[3], source=_s(r[4]))
                      for r in _sheet_rows(wb, "Digbala")}
    out["dasha_role_text"] = {r[0]: dict(kind=r[1], text=_s(r[2]), slide=_s(r[3]))
                              for r in _sheet_rows(wb, "DashaRoleText")}
    out["graha_in_bhava"] = [dict(planet=r[0], house=int(r[1]),
                                  points=[p for p in _s(r[2]).split("\n\n") if p.strip()],
                                  extra=[p for p in _s(r[3]).split("\n") if p.strip()],
                                  status=r[4], source=_s(r[5])) for r in _sheet_rows(wb, "GrahaInBhava")]
    out["graha_pair"] = [dict(a=r[0], b=r[1], conjunction=_s(r[2]), aspect=_s(r[3]), status=r[4], source=_s(r[5]))
                         for r in _sheet_rows(wb, "GrahaPair")]
    out["bhava_lord_in"] = [dict(lord_of=int(r[0]), sits_in=int(r[1]), text=_s(r[2]), status=r[3], source=_s(r[4]))
                            for r in _sheet_rows(wb, "BhavaLordIn")]
    out["graha_rashi"] = [dict(planet=r[0], rashi=int(r[1]), text=_s(r[2]), status=r[3], source=_s(r[4]))
                          for r in _sheet_rows(wb, "GrahaRashi")]
    return out


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


def extract_reference(index_path=INDEX):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is required to read the page's reference tables")
    p = subprocess.run([node, "-e", GRAB_JS, str(index_path), json.dumps(REFERENCE_NAMES)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"reference extraction failed: {p.stderr[-600:]}")
    ref = json.loads(p.stdout)
    ref["PLANET_PROFILE"] = {planet: {k: prof[k] for k in PROFILE_KEYS if k in prof}
                             for planet, prof in ref["PLANET_PROFILE"].items()}
    return ref


DATA_START = "/* SESSION23-DATA-START — generated from Session23_Rules.xlsx by build_session23.py; do not edit by hand */"
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
    if DATA_START in page:
        a = page.index(DATA_START)
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


def build(xlsx_path=XLSX, json_path=JSON_PATH, index_path=INDEX, seed=False, write_page=False):
    """Workbook -> JSON (and, with write_page, the index.html data block).
    `seed=True` first rewrites the workbook from session23_rule_data.py."""
    xlsx_path, json_path = pathlib.Path(xlsx_path), pathlib.Path(json_path)
    if seed or not xlsx_path.exists():
        seed_workbook(xlsx_path)
    rules = read_workbook(xlsx_path)
    rules["reference"] = extract_reference(index_path)
    rules["meta"] = {"source": "Session 23 slides + recording (8 Oct 2026)", "version": 1,
                     "statuses": ["taught", "curated", "blend", "standard"]}
    json_path.write_text(json.dumps(rules, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if write_page:
        write_page_block(index_path, rules)
    return rules


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    build(seed="--seed" in argv, write_page=True)
    print(f"wrote {JSON_PATH.name} from {XLSX.name} and the SESSION23-DATA block of {INDEX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
