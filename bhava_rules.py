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


# ---------------------------------------------------------------- nature, class readings, roles
ROLE_ORDER = ["Maraka lord", "Maraka occupant", "Badhakadhipati", "Badhaka occupant",
              "Dusthana lord", "Trishadaya lord"]
_MERCURY_SPOILERS = ("Mars", "Saturn", "Rahu", "Ketu")


def moon_waxing(sun_lon, moon_lon):
    """True in Shukla paksha: tithi 1-15 (the page's computeTithi)."""
    sep = (moon_lon - sun_lon) % 360
    return int(sep // 12) + 1 <= 15


def nature(planet, signs, waxing):
    """'benefic' or 'malefic' — Mercury is benefic unless it shares a sign with Mars, Saturn, Rahu or Ketu."""
    if planet in ("Jupiter", "Venus"):
        return "benefic"
    if planet == "Moon":
        return "benefic" if waxing else "malefic"
    if planet == "Mercury":
        spoiled = any(signs.get(o) == signs.get("Mercury") for o in _MERCURY_SPOILERS)
        return "malefic" if spoiled else "benefic"
    return "malefic"


def class_readings(rules, lagna, signs, waxing):
    """One entry per placed planet: {planet, house, classes, texts} from the ClassRules sheet."""
    out = []
    for p in PLANET_ORDER:
        if p not in signs:
            continue
        house = house_of(lagna, signs[p])
        kind = nature(p, signs, waxing)
        classes = [c for c in CLASS_ORDER if house in class_houses(rules, c, lagna)]
        texts = [r["text"] for c in classes for r in rules["class_rules"]
                 if r["class"] == c and r["applies"] in ("any", kind) and house not in r["exclude_houses"]]
        out.append({"planet": p, "house": house, "classes": classes, "texts": texts})
    return out


def planet_roles(rules, lagna, signs):
    """{planet: [roles]} — the six daśā-relevant roles, in ROLE_ORDER. Rahu and Ketu get occupant roles only."""
    bad = badhaka_house(rules, lagna)
    lords = lambda houses: {house_lord(rules, lagna, h) for h in houses}
    occ = occupants(lagna, signs)
    roles = {}
    for p in PLANET_ORDER:
        mine = []
        if p in lords((2, 7)):
            mine.append("Maraka lord")
        if p in occ[2] + occ[7]:
            mine.append("Maraka occupant")
        if p in lords((bad,)):
            mine.append("Badhakadhipati")
        if p in occ[bad]:
            mine.append("Badhaka occupant")
        if p in lords((6, 8, 12)):
            mine.append("Dusthana lord")
        if p in lords((3, 6, 11)):
            mine.append("Trishadaya lord")
        roles[p] = mine
    return roles


# ---------------------------------------------------------------- dignity (port of the page's planetDignity)
def _relation(ref, planet, lord):
    nf = ref["NATURAL_FRIENDS"].get(planet)
    if not nf or planet == lord:
        return None
    if lord in nf["friend"]:
        return "friend"
    if lord in nf["enemy"]:
        return "enemy"
    return "neutral"


def dignity(rules, planet, sign, deg=None):
    """{label, flag, bala, note} — identical to planetDignity(planet, sign + 1, deg) in index.html."""
    ref = rules["reference"]
    n = sign + 1
    d = ref["RASHI_DIGNITY"][str(n)]
    dd = ref["DIGNITY_DEG"].get(planet)
    own = ref["PLANET_OWN_HOUSES"].get(planet, [])
    is_mt_sign = bool(dd) and n == dd["mtR"]
    in_mt_range = is_mt_sign and (deg is None or dd["mt"][0] <= deg <= dd["mt"][1])
    near = lambda target: deg is not None and abs(deg - target) <= 1.0

    def out(label, flag, bala, note):
        return {"label": label, "flag": flag, "bala": bala, "note": note}

    if planet in d["exalted"]:
        # Moon and Mercury are exalted in their own MT sign: exaltation holds only to the deep degree
        overlaps_mt = is_mt_sign and deg is not None and deg > dd["exD"]
        if not overlaps_mt:
            if dd and n == dd["exR"] and near(dd["exD"]):
                return out("Deep Exalted", "exalted", 100, f"deep exaltation {dd['exD']}°")
            return out("Exalted", "exalted", 100, f"exaltation sign · deep {dd['exD']}°" if dd else "")
    if planet in d["debilitated"]:
        if dd and n == dd["deR"] and near(dd["deD"]):
            return out("Deep Debilitated", "debilitated", 0, f"deep debilitation {dd['deD']}°")
        return out("Debilitated", "debilitated", 0, f"debilitation sign · deep {dd['deD']}°" if dd else "")
    if planet in ("Rahu", "Ketu"):
        return out("Own House", "own", 50, "node treats its occupied rashi as own")
    if in_mt_range:
        return out("Own (Moolatrikona)", "mtr", 75, f"MT {dd['mt'][0]}–{dd['mt'][1]}°" if dd else "")
    if n in own:
        note = f"Own {dd['mt'][1]}–30° · MT {dd['mt'][0]}–{dd['mt'][1]}°" if is_mt_sign and dd else "own sign"
        return out("Own House", "own", 50, note)
    rel = _relation(ref, planet, d["lord"])
    if rel == "friend":
        return out("Friend's House", "friend", 25, f"lord {d['lord']} — friend")
    if rel == "neutral":
        return out("Neutral House", "neutral", 12.5, f"lord {d['lord']} — neutral")
    if rel == "enemy":
        return out("Enemy's House", "enemy", 0, f"lord {d['lord']} — enemy")
    return out("—", "neutral", None, "")


def digbala(rules, planet, house):
    """'strong' in the planet's directional-strength house, 'lost' in the opposite one, else None."""
    row = rules["digbala"].get(planet)
    if not row:
        return None
    return "strong" if house == row["strong"] else "lost" if house == row["lost"] else None
