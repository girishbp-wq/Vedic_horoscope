#!/usr/bin/env python3
"""Apply the teacher's Session 23 (2024 deck) to 27 texts to the rules shipped before them.

    python apply_teacher_slides.py

Reads session23_rules.previous.json (the rules as shipped before these sessions), adds the rows from
session23_teacher_slides.py, and writes session23_rules.json and the SESSION23-DATA block of index.html.
On the user's PC the same rows reach the master workbook through `make_session23_xlsx.py --install`.
"""
import copy
import json
import pathlib
import sys

import build_session23 as b23
import session23_teacher_slides as ts

ROOT = pathlib.Path(__file__).resolve().parent
PREVIOUS = ROOT / "session23_rules.previous.json"


def _taught(**row):
    return dict(row, status="taught")


def apply(previous):
    """A copy of `previous` (a rules dict) with the teacher's rows from session23_teacher_slides applied."""
    rules = copy.deepcopy(previous)
    for row in rules["graha_in_bhava"]:
        cell = ts.GRAHA_IN_BHAVA.get((row["planet"], row["house"]))
        if cell:
            source, text = cell
            row.update(points=[p for p in text.split("\n\n") if p.strip()], extra=[], status="taught", source=source)
    for row in rules["bhava_lord_in"]:
        row.setdefault("condition", "")
        row.setdefault("exchange", False)
    rules["bhava_lord_in"] += [dict(lord_of=a, sits_in=b, text=t, status="taught", source=s, condition=c, exchange=x)
                               for a, b, c, x, t, s in ts.LORD_IN]
    rules["graha_rashi"] += [_taught(planet=p, rashi=n, text=t, source=s) for p, n, t, s in ts.GRAHA_RASHI]
    cr = rules["class_rules"]
    upachaya = next(r for r in cr if r["class"] == "Upachaya" and r["applies"] == "malefic")
    upachaya.update(text=ts.CLASS_RULE_TEXT["upachaya_malefic"][0], slide=ts.CLASS_RULE_TEXT["upachaya_malefic"][1])
    last_dusthana = max(i for i, r in enumerate(cr) if r["class"] == "Dusthana")
    text, slide = ts.CLASS_RULE_TEXT["dusthana_malefic"]
    cr.insert(last_dusthana + 1, {"class": "Dusthana", "applies": "malefic", "exclude_houses": [], "text": text, "slide": slide})
    for planet, source in ts.DIGBALA_TAUGHT.items():
        rules["digbala"][planet].update(status="taught", source=source)
    new = {
        "bhava_nature": [_taught(house=h, nature=n, planet=p, text=t, source=s) for h, n, p, t, s in ts.BHAVA_NATURE],
        "aspect_meaning": [_taught(planet=p, aspect=a, from_house=f, text=t, source=s) for p, a, f, t, s in ts.ASPECT_MEANING],
        "life_areas": [dict(no=n, area=a, houses=list(h), karakas=list(k), karaka_female=kf, link=l, source=s)
                       for n, a, h, k, kf, l, s in ts.LIFE_AREAS],
        "conditions": [_taught(key=k, planet=p, house=h, text=t, source=s) for k, p, h, t, s in ts.CONDITIONS],
        "remedies": [dict(topic=t, text=x, source=s) for t, x, s in ts.REMEDIES],
    }
    out = {}
    for k, v in rules.items():                 # new keys go before `reference` and `meta`, in sheet order
        if k == "reference":
            out.update(new)
        out[k] = v
    out["meta"] = dict(b23.META)
    return out


def main():
    rules = apply(json.loads(PREVIOUS.read_text(encoding="utf-8")))
    b23.JSON_PATH.write_text(json.dumps(rules, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    b23.write_page_block(b23.INDEX, rules)
    print(f"wrote {b23.JSON_PATH.name} and the SESSION23-DATA block of {b23.INDEX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
