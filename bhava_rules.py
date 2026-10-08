#!/usr/bin/env python3
"""Session 23 engine: bhava classifications, readings, daśā linking and prediction layers.

Signs are 0-based everywhere here (Mesha = 0 … Meena = 11), houses 1-12 counted from the Lagna sign.
The rules come from session23_rules.json (built from Session23_Rules.xlsx by build_session23.py);
its `reference` block is a copy of the tables in index.html, so nothing is kept twice by hand.

The same logic exists as JavaScript in index.html (s23* functions) and as formulas in the Excel
calculator; test_session23_cross_impl.py keeps all three identical.
"""
import json
import pathlib

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
CLASS_ORDER = ["Kendra", "Trikona", "Panapara", "Apoklima", "Upachaya", "Apachaya", "Maraka",
               "Dusthana", "Badhaka", "Trishadaya"]

_DEFAULT_JSON = pathlib.Path(__file__).resolve().parent / "session23_rules.json"


def load_rules(path=None):
    return json.loads(pathlib.Path(path or _DEFAULT_JSON).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- houses, lords, occupants
def house_sign(lagna, house):
    """0-based sign of `house` (1-12) for a chart whose Lagna is in sign `lagna`."""
    return (lagna + house - 1) % 12


def house_lord(rules, lagna, house):
    return rules["reference"]["RASHI"][house_sign(lagna, house)]["lord"]


def house_of(lagna, sign):
    """House (1-12) that `sign` occupies."""
    return (sign - lagna) % 12 + 1


def occupants(lagna, signs):
    """{house: [planets]} for houses 1-12, planets in Sun…Ketu order."""
    out = {h: [] for h in range(1, 13)}
    for p in PLANET_ORDER:
        if p in signs:
            out[house_of(lagna, signs[p])].append(p)
    return out


# ---------------------------------------------------------------- classes
def badhaka_house(rules, lagna):
    return rules["badhaka"][rules["reference"]["RASHI"][lagna]["mode"]]


def class_houses(rules, name, lagna):
    """Houses of a class; Badhaka depends on the Lagna's mode (Chara / Sthira / Dwisabhava)."""
    if name == "Badhaka":
        return [badhaka_house(rules, lagna)]
    return next(c["houses"] for c in rules["classes"] if c["name"] == name)


def _row(rules, lagna, signs, occ, house):
    lord = house_lord(rules, lagna, house)
    return {"house": house, "sign": house_sign(lagna, house), "planets": occ[house], "lord": lord,
            "lord_house": house_of(lagna, signs[lord]) if lord in signs else None}


def classification_tables(rules, lagna, signs):
    """{class: [rows]} in the slides' format — house, sign, planets in it, lord, house the lord sits in."""
    occ = occupants(lagna, signs)
    return {name: [_row(rules, lagna, signs, occ, h) for h in class_houses(rules, name, lagna)]
            for name in CLASS_ORDER}


def house_class_matrix(rules, lagna):
    """12 rows {house, sign, classes} — which of the 10 classes each house belongs to."""
    memberships = {name: class_houses(rules, name, lagna) for name in CLASS_ORDER}
    return [{"house": h, "sign": house_sign(lagna, h),
             "classes": [n for n in CLASS_ORDER if h in memberships[n]]} for h in range(1, 13)]


def badhaka(rules, lagna, signs):
    """Badhakasthana for the Lagna: {mode, house, sign, lord, occupants}."""
    house = badhaka_house(rules, lagna)
    return {"mode": rules["reference"]["RASHI"][lagna]["mode"], "house": house, "sign": house_sign(lagna, house), "lord": house_lord(rules, lagna, house),
            "occupants": occupants(lagna, signs)[house]}
