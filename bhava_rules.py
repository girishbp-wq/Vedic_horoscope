#!/usr/bin/env python3
"""Session 23 engine: bhava classifications, readings, daśā linking and prediction layers.

Signs are 0-based everywhere here (Mesha = 0 … Meena = 11), houses 1-12 counted from the Lagna sign.
The rules come from session23_rules.json (built from Session23_Rules.xlsx by build_session23.py);
its `reference` block is a copy of the tables in index.html, so nothing is kept twice by hand.

The same logic exists as JavaScript in index.html (s23* functions) and as formulas in the Excel
calculator; test_session23_cross_impl.py keeps all three identical.
"""
import datetime
import json
import math
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
BENEFICS = ("Jupiter", "Venus", "Mercury", "Moon")     # Session 26: natural benefics
MILD_MALEFIC = "Sun"                                   # Session 26: a mild malefic


def moon_waxing(sun_lon, moon_lon):
    """True in Shukla paksha: tithi 1-15 (the page's computeTithi)."""
    sep = (moon_lon - sun_lon) % 360
    return math.floor(sep / 12) + 1 <= 15            # Math.floor(sep / 12), as the page


def nature(planet):
    """Session 26: Jupiter, Venus, Mercury and the Moon are natural benefics; Saturn, Mars, Rahu and Ketu natural
    malefics; the Sun a mild malefic. The Moon's paksha changes its strength (moon_strength), not its nature."""
    if planet in BENEFICS:
        return "benefic"
    return "mild malefic" if planet == MILD_MALEFIC else "malefic"


def nature_class(planet):
    """The rule class a planet's nature selects: a mild malefic takes the malefic rules."""
    return "benefic" if planet in BENEFICS else "malefic"


def moon_strength(waxing):
    if waxing is None:
        return ""
    return "Shukla (waxing) — stronger" if waxing else "Krishna (waning) — weaker"


def _mild(planet, applies, text):
    return "(mild) " + text if planet == MILD_MALEFIC and applies == "malefic" else text


def class_readings(rules, lagna, signs, ctx=None):
    """One entry per placed planet: {planet, house, classes, texts} from the ClassRules sheet.
    The Sun takes the malefic rules, each marked "(mild) ". A rule with When 'not weak' (the S25 Dusthana line) is
    kept only for a planet that is not weak (spec §6.2.5)."""
    ctx = ctx or context(lagna, signs)
    out = []
    for p in PLANET_ORDER:
        if p not in signs:
            continue
        house = house_of(lagna, signs[p])
        kind = nature_class(p)
        classes = [c for c in CLASS_ORDER if house in class_houses(rules, c, lagna)]
        texts = [_mild(p, r["applies"], r["text"]) for c in classes for r in rules["class_rules"]
                 if r["class"] == c and r["applies"] in ("any", kind) and house not in r["exclude_houses"]
                 and not (r.get("when") == "not weak" and strength(rules, ctx, p) == "weak")]
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


# Rāhu and Ketu own no rāśi; outside their exaltation/debilitation they carry no sthāna-bala tier.
NODE_LABEL = "Node (no rulership)"
NODE_NOTE = "a node owns no rāśi — it gives the results of the sign's lord"


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
        return out(NODE_LABEL, "node", None, NODE_NOTE)
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


# ---------------------------------------------------------------- chart context and strength (Sessions 24-27)
GENDERS = ("Male", "Female")
MALE_PLANETS = ("Sun", "Mars", "Jupiter")
STRONG_LABELS = ("Deep Exalted", "Exalted", "Own (Moolatrikona)", "Own House", "Friend's House")
WEAK_LABELS = ("Deep Debilitated", "Debilitated", "Enemy's House")
MODE_WORD = {"Chara": "movable", "Sthira": "fixed", "Dwisabhava": "dual"}


def context(lagna, signs, degs=None, waxing=None, retro=None, gender=None, age=None, maha=None, bhukti=None):
    """Everything the Sessions 24-27 rules read from a chart. `gender` other than Male/Female counts as not given;
    `age` (years), `maha` and `bhukti` (running daśā lords) may be None when the birth time is not known."""
    return {"lagna": lagna, "signs": dict(signs), "degs": dict(degs or {}), "waxing": waxing, "retro": dict(retro or {}),
            "gender": gender if gender in GENDERS else None, "age": age, "maha": maha, "bhukti": bhukti}


def dasha_now(rules, moon_lon, birth, now):
    """Age in years and the running Mahādaśā and Bhukti lords (None outside the 120-year span)."""
    d = vimshottari(rules, moon_lon, birth, now)
    run = d["running"]
    return {"age": (now - birth).total_seconds() / (_YEAR_DAYS * 86400),
            "maha": d["cur_maha"]["lord"] if run else None, "bhukti": d["cur_bhukti"]["lord"] if run else None}


def combust(rules, ctx, planet):
    """Within COMBUST_ORB degrees of the Sun in the same sign (the rule graha_graha uses); False without degrees."""
    ref, sg, dg = rules["reference"], ctx["signs"], ctx["degs"]
    if planet not in ref["COMBUST_PLANETS"] or planet not in sg or "Sun" not in sg or sg[planet] != sg["Sun"]:
        return False
    if dg.get(planet) is None or dg.get("Sun") is None:
        return False
    return abs(dg[planet] - dg["Sun"]) <= ref["COMBUST_ORB"]


def afflicted(rules, ctx, planet):
    """R5: debilitated, in an enemy's sign, or combust."""
    d = dignity(rules, planet, ctx["signs"][planet], ctx["degs"].get(planet))
    return d["flag"] in ("debilitated", "enemy") or combust(rules, ctx, planet)


def aspect_signs(rules, planet, sign):
    """[(aspect counted forward, sign it falls on)] for a planet in `sign`."""
    return [(h, (sign + h - 1) % 12) for h in rules["reference"]["SPECIAL_ASPECTS"][planet]]


def aspects_on(rules, ctx, sign):
    """Placed planets whose aspect falls on `sign`: [{by, house_aspect}] in planet order."""
    sg = ctx["signs"]
    return [{"by": p, "house_aspect": h} for p in PLANET_ORDER if p in sg
            for h, t in aspect_signs(rules, p, sg[p]) if t == sign]


def teacher_count(planet, h):
    """The teacher's count of an aspect: Rahu and Ketu count anti-clockwise (forward 12, 9, 5 = her 2nd, 5th, 9th)."""
    return (13 - h) % 12 + 1 if planet in ("Rahu", "Ketu") else h


def aspect_meaning(rules, planet, h, from_house=None):
    """What an aspect means (S24, S27): the planet's reading for this aspect from its house, then for this aspect,
    then for its aspects in general; when the teacher gives none, 'to see, to influence' (S27 p.18).
    `h` is counted forward; Rahu and Ketu rows use her anti-clockwise count."""
    c = teacher_count(planet, h)
    rows = rules["aspect_meaning"]
    find = lambda pl, a, f: next((r for r in rows if (r["planet"], r["aspect"], r["from_house"]) == (pl, a, f)), None)
    found = [r for r in ((find(planet, c, from_house) if from_house else None), find(planet, c, None), find(planet, None, None)) if r]
    if not found:
        found = [r for r in (find("any", None, None),) if r]
    return [{"text": r["text"], "status": r["status"], "source": r["source"]} for r in found]


def _meanings(rules, planet, h, from_house):
    return [m["text"] for m in aspect_meaning(rules, planet, h, from_house)]


STRENGTH_MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")     # the Sun counts as a mild malefic (R10)


def strength_detail(rules, ctx, planet):
    """Session 29 (pp.17, 29; spec D1, S1, S2): {word, reasons}.
    weak — debilitated, in an enemy's sign, combust, or with Rahu (a sign of weakness wins over a good sign);
    strong — exalted, Moolatrikona, own or friend's sign, and no malefic aspects it;
    mixed — such a sign, but a malefic aspects it (each named);
    depends — otherwise. Rahu and Ketu follow their exaltation and debilitation signs; elsewhere they depend on
    the sign's lord ("Node (no rulership)"). Rahu is never "with Rahu" itself."""
    sg = ctx["signs"]
    sign = sg[planet]
    label = dignity(rules, planet, sign, ctx["degs"].get(planet))["label"]
    weak = ([label] if label in WEAK_LABELS else []) + (["combust"] if combust(rules, ctx, planet) else []) \
        + (["with Rahu"] if planet != "Rahu" and sg.get("Rahu") == sign else [])
    if weak:
        return {"word": "weak", "reasons": weak}
    if label in STRONG_LABELS:
        mal = [f"aspected by {a['by']}" for a in aspects_on(rules, ctx, sign) if a["by"] in STRENGTH_MALEFICS and a["by"] != planet]
        return {"word": "mixed", "reasons": mal} if mal else {"word": "strong", "reasons": [label]}
    return {"word": "depends", "reasons": [label]}


def strength(rules, ctx, planet):
    """The strength word of strength_detail(): strong, weak, mixed or depends."""
    return strength_detail(rules, ctx, planet)["word"]


def lords_houses(rules, lagna, planet):
    return [h for h in range(1, 13) if house_lord(rules, lagna, h) == planet]


def ruled_phrase(houses):
    """'(rules the 9th)', '(rules the 5th and 12th)', '(rules the 1st, 4th and 7th)'; '' for a planet ruling none."""
    if not houses:
        return ""
    names = [ordinal(h) for h in houses]
    return "(rules the " + (names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]) + ")"


def resolve_planets(rules, ctx, spec):
    """The placed planets a ChartReadings Planet/With cell names: a planet, every benefic/malefic, or 'Nth lord'."""
    sg = ctx["signs"]
    if spec in ("benefic", "malefic"):
        return [p for p in PLANET_ORDER if p in sg and nature_class(p) == spec]
    if spec.endswith(" lord"):
        lord = house_lord(rules, ctx["lagna"], int(spec[:-7]))
        return [lord] if lord in sg else []
    return [spec] if spec in sg else []


def _aspects_sign(rules, sg, p, sign):
    return any(t == sign for _, t in aspect_signs(rules, p, sg[p]))


# Her sentences that state a planet's dignity show only when it holds (spec 2026-10-13, built into the code by the
# user's choice). Keyed by her row's key cells; who = a planet, "Nth lord", or "lord" (the lord of the row's LordOf).
READING_CLAIMS = {("aspects", "1st lord", "", 1, ""): ("Sun", "exalted")}               # S28 p.2: "Sun … is exalted"
LORD_IN_CLAIMS = {(9, 5, "", False): ("lord", "exalted"),                               # S28 p.12
                  (8, 12, "", True): ("12th lord", "debilitated"),                      # S28 p.16, the Parivartana:
                  # keyed (smaller house, larger house, "", True) — it follows the house pair, whatever its Condition
                  (7, 4, "weak", False): ("lord", "debilitated"),                       # S28 pp.9-10
                  (8, 12, "weak", False): ("lord", "debilitated"),                      # S28 p.11
                  (10, 4, "weak", False): ("lord", "debilitated")}                      # S28 p.13


def claim_holds(rules, ctx, claim, lord_of=None):
    """True when `claim` = (who, flag) holds for the chart (or there is none). A planet not placed fails."""
    if claim is None:
        return True
    who, flag = claim
    if who == "lord":
        who = house_lord(rules, ctx["lagna"], lord_of)
    elif who.endswith(" lord"):
        who = house_lord(rules, ctx["lagna"], int(who[:-7]))
    sg = ctx["signs"]
    return who in sg and dignity(rules, who, sg[who], ctx["degs"].get(who))["flag"] == flag


def chart_readings(rules, ctx):
    """Her Chart 3 sentences (S23_ChartReadings) that hold for this chart, in sheet order (spec §6.4):
    [{kind, house, on, with, text, status, source}]. `on` = the planets the Planet cell matched, `with` = the planets
    the With cell matched (a different planet each time); for a malefic+malefic row, `on` holds both."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    flag = lambda p: dignity(rules, p, sg[p], ctx["degs"].get(p))["flag"]
    out = []
    for r in rules.get("chart_readings", []):
        if not claim_holds(rules, ctx, READING_CLAIMS.get((r["kind"], r["planet"], r["with"], r["house"], r["condition"]))):
            continue
        kind = r["kind"]
        cands = [p for p in resolve_planets(rules, ctx, r["planet"]) if not r["condition"] or flag(p) == r["condition"]]
        partners = resolve_planets(rules, ctx, r["with"]) if r["with"] else None
        on, with_ = [], []
        if kind == "aspects planet":
            target = r["with"]
            if target in sg:
                on, with_ = [p for p in cands if p != target and _aspects_sign(rules, sg, p, sg[target])], [target]
        elif kind == "aspects lord":
            lord = house_lord(rules, lagna, r["house"])
            if lord in sg:
                on = [p for p in cands if p != lord and _aspects_sign(rules, sg, p, sg[lord])]
        else:
            sign = house_sign(lagna, r["house"])
            hits = (lambda p: sg[p] == sign) if kind == "in" else (lambda p: _aspects_sign(rules, sg, p, sign))
            on = [p for p in cands if hits(p)]
            if partners is not None:
                together = (lambda p, q: sg[p] == sg[q]) if kind == "in" else (lambda p, q: hits(q))
                pairs = [(p, q) for p in on for q in partners if q != p and together(p, q)]
                if r["planet"] == r["with"]:                      # e.g. two malefics aspecting the 2nd
                    on = sorted({x for pq in pairs for x in pq}, key=PLANET_ORDER.index)
                else:
                    on = [p for p in on if any(pp == p for pp, _ in pairs)]
                    with_ = [q for q in partners if any(qq == q for _, qq in pairs)]
                if not pairs:
                    on = []
        if on:
            out.append({"kind": kind, "house": r["house"], "on": on, "with": with_, "text": r["text"],
                        "status": r["status"], "source": r["source"]})
    return out


def _aspect_items(rules, ctx, house):
    """The planets aspecting `house`, each with its aspect, the houses it rules (S28 p.14) and her meanings."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    mine = [x for x in chart_readings(rules, ctx) if x["kind"] == "aspects" and x["house"] == house]
    # a reading is listed once, with the first planet it names
    return [{"by": a["by"], "aspect": aspect_name(a["by"], a["house_aspect"]), "rules": lords_houses(rules, lagna, a["by"]),
             "meanings": _meanings(rules, a["by"], a["house_aspect"], house_of(lagna, sg[a["by"]])),
             "readings": [x["text"] for x in mine if x["on"][0] == a["by"]]}
            for a in aspects_on(rules, ctx, house_sign(lagna, house))]


def sign_line(rules, sign):
    """S27 pp.9-10: the sign's mode, element and direction; a dual sign repeats the matter, an earth sign means property."""
    r = rules["reference"]["RASHI"][sign]
    text = f"{r['sanskrit']} is a {MODE_WORD[r['mode']]} ({r['mode']}) sign, {r['tatwa']} tatwa, {r['direction']}."
    if r["mode"] == "Dwisabhava":
        text += " A dual sign: the matter is continuous or repeated."
    if r["tatwa"] == "Prithvi":
        text += " An earth (Prithvi) sign: it concerns property."
    return text


def is_male_sign(rules, sign):
    return rules["reference"]["RASHI"][sign]["oddEven"].startswith("Odd")


# ---------------------------------------------------------------- conditional readings (spec §6.6)
# The fixed keys of the S23_Conditions sheet, in the order the readings are listed.
CONDITION_KEYS = ("saturn_matures", "saturn_retro_1", "saturn_afflicted_10_young", "saturn_mars_12", "saturn_afflicted_6",
                  "saturn_afflicted_12", "jupiter_md_8", "jupiter_md_11", "venus_dasha_9", "rahu_md_9",
                  "twelfth_hidden_talent", "upachaya_30s", "ketu_12_purpose", "venus_afflicted", "venus_good",
                  "venus_mercury_5", "seventh_lord_12", "mercury_foreign_language", "moon_dual_10", "venus_meets_wife",
                  "jupiter_husband", "first_child_male")
SATURN_MATURES_AGE, KETU_PURPOSE_AGE = 36, 35          # R6; S25 p.41


def _condition_row(rules, key, planet, house):
    """The S23_Conditions row for this key: planet and house both matching first, then house, then planet, then any."""
    best, score = None, -1
    for r in rules["conditions"]:
        if r["key"] != key or r["planet"] not in (None, planet) or r["house"] not in (None, house):
            continue
        s = (r["house"] is not None) * 2 + (r["planet"] is not None)
        if s > score:
            best, score = r, s
    return best


def _young(age, limit):
    return age is None or age < limit


def chart_conditions(rules, ctx):
    """The conditional sentences that hold for this chart: [{key, planet, house, text, status, source, active}].

    `active` is True/False for a daśā-linked sentence when the running daśā is known, else None."""
    sg, lagna, maha, bhukti = ctx["signs"], ctx["lagna"], ctx["maha"], ctx["bhukti"]
    house = lambda p: house_of(lagna, sg[p]) if p in sg else None
    placed = [p for p in PLANET_ORDER if p in sg]
    lord = lambda h: house_lord(rules, lagna, h)
    found = []                                                   # (key, planet, house, active)

    def add(key, planet, h, active=None):
        found.append((key, planet, h, active))

    def dasha(test):
        return None if maha is None else bool(test)

    sat = house("Saturn")
    if sat in (1, 2, 3, 5, 7, 10) and _young(ctx["age"], SATURN_MATURES_AGE):
        add("saturn_matures", "Saturn", sat)
    if sat == 1 and ctx["retro"].get("Saturn"):
        add("saturn_retro_1", "Saturn", 1)
    if sat == 10 and afflicted(rules, ctx, "Saturn") and _young(ctx["age"], SATURN_MATURES_AGE):
        add("saturn_afflicted_10_young", "Saturn", 10)
    if sat == 12 and house("Mars") == 12:
        add("saturn_mars_12", "Saturn", 12)
    for h, key in ((6, "saturn_afflicted_6"), (12, "saturn_afflicted_12")):
        if sat == h and afflicted(rules, ctx, "Saturn"):
            add(key, "Saturn", h)
    for h, key in ((8, "jupiter_md_8"), (11, "jupiter_md_11")):
        if house("Jupiter") == h:
            add(key, "Jupiter", h, dasha(maha == "Jupiter"))
    if house("Venus") == 9:
        add("venus_dasha_9", "Venus", 9, dasha("Venus" in (maha, bhukti)))
    if house("Rahu") == 9:
        add("rahu_md_9", "Rahu", 9, dasha(maha == "Rahu"))
    for p in placed:
        if house(p) == 12:
            add("twelfth_hidden_talent", p, 12, dasha(p in (maha, bhukti)))
    for p in placed:
        if house(p) in (3, 6, 10, 11):
            add("upachaya_30s", p, house(p))
    if house("Ketu") == 12 and _young(ctx["age"], KETU_PURPOSE_AGE):
        add("ketu_12_purpose", "Ketu", 12)
    ven = house("Venus")
    if ven in (2, 8, 11):
        add("venus_afflicted" if afflicted(rules, ctx, "Venus") else "venus_good", "Venus", ven)
    if ven == 5 and house("Mercury") == 5:
        add("venus_mercury_5", "Venus", 5)
    l7 = lord(7)
    if house(l7) == 12:
        add("seventh_lord_12", l7, 12)
    l12 = lord(12)
    if house("Mercury") == 2 and (sg.get("Rahu") == sg["Mercury"] or (l12 != "Mercury" and sg.get(l12) == sg["Mercury"])):
        add("mercury_foreign_language", "Mercury", 2)
    if house("Moon") == 10 and rules["reference"]["RASHI"][sg["Moon"]]["mode"] == "Dwisabhava":
        add("moon_dual_10", "Moon", 10)
    if ctx["gender"] == "Male" and ven is not None:
        add("venus_meets_wife", "Venus", ven)
    if ctx["gender"] == "Female" and house("Jupiter") is not None:
        add("jupiter_husband", "Jupiter", house("Jupiter"))
    l5, fifth = lord(5), house_sign(lagna, 5)
    if (is_male_sign(rules, fifth) and any(house(p) == 5 for p in MALE_PLANETS) and l5 in sg
            and is_male_sign(rules, sg[l5])):
        add("first_child_male", l5, 5)
    out = []
    for key, planet, h, active in sorted(found, key=lambda f: CONDITION_KEYS.index(f[0])):
        row = _condition_row(rules, key, planet, h)
        if row:
            out.append({"key": key, "planet": planet, "house": h, "text": row["text"], "status": row["status"],
                        "source": row["source"], "active": active})
    return out


# ---------------------------------------------------------------- Vimshottari daśā and role linking
_YEAR_DAYS = 365.25            # same civil-year length as buildDasha() in index.html
_NAK_SIZE = 360 / 27


def vimshottari(rules, moon_lon, birth, now):
    """Port of buildDasha(): nine Mahādaśās with nine Bhuktis each, from the Moon's nakṣatra at birth.

    Like the page, a `now` outside the 120-year span falls back to the first Mahādaśā / Bhukti, with
    running = False so callers can say that no period is running."""
    ref = rules["reference"]
    order, years = ref["VORDER"], ref["VYEARS"]
    lon = moon_lon % 360
    idx = math.floor(lon / _NAK_SIZE)        # as the page: 40° // (40/3) would floor to 2, not 3
    nak_lord = ref["NAKSHATRAS"][idx][1]
    frac = (lon - idx * _NAK_SIZE) / _NAK_SIZE
    add = lambda dt, y: dt + datetime.timedelta(days=y * _YEAR_DAYS)
    start = add(birth, -frac * years[nak_lord])            # virtual start of the Mahādaśā running at birth
    first = order.index(nak_lord)
    timeline = []
    for i in range(9):
        lord = order[(first + i) % 9]
        end = add(start, years[lord])
        x, bhuktis, li = start, [], order.index(lord)
        for j in range(9):
            sub = order[(li + j) % 9]
            be = add(x, years[lord] * years[sub] / 120)
            bhuktis.append({"lord": sub, "start": x, "end": be, "cur": x <= now < be})
            x = be
        timeline.append({"lord": lord, "years": years[lord], "start": start, "end": end,
                         "cur": start <= now < end, "bhuktis": bhuktis})
        start = end
    cur_maha = next((t for t in timeline if t["cur"]), timeline[0])
    cur_bhukti = next((b for b in cur_maha["bhuktis"] if b["cur"]), cur_maha["bhuktis"][0])
    return {"nak_index": idx + 1, "nak_lord": nak_lord, "birth": birth, "timeline": timeline,
            "cur_maha": cur_maha, "cur_bhukti": cur_bhukti, "running": any(t["cur"] for t in timeline),
            "span_start": timeline[0]["start"], "span_end": timeline[8]["end"]}


DASHA_LEVELS = ("Mahādaśā", "Bhukti", "Pratyantara", "Sookshma", "Prāṇa")


def sub_periods(rules, lord, start, years):
    """S29 pp.5, 11: the nine periods inside a period of `years` ruled by `lord`, in the daśā order from `lord`,
    each `years × its years / 120` long. The last one ends exactly where the parent ends."""
    ref = rules["reference"]
    order, ys = ref["VORDER"], ref["VYEARS"]
    add = lambda dt, y: dt + datetime.timedelta(days=y * _YEAR_DAYS)
    out, x, li = [], start, order.index(lord)
    for j in range(9):
        sub = order[(li + j) % 9]
        y = years * ys[sub] / 120
        end = add(start, years) if j == 8 else add(x, y)
        out.append({"lord": sub, "start": x, "end": end, "years": y})
        x = end
    return out


def dasha_chain(rules, dasha, now):
    """The running Mahādaśā, Bhukti, Pratyantara, Sookshma and Prāṇa: [{level, lord, start, end}]; [] outside the span."""
    m = next((t for t in dasha["timeline"] if t["start"] <= now < t["end"]), None)
    if m is None:
        return []
    ys = rules["reference"]["VYEARS"]
    b = next((x for x in m["bhuktis"] if x["start"] <= now < x["end"]), m["bhuktis"][-1])
    chain = [{"level": DASHA_LEVELS[0], "lord": m["lord"], "start": m["start"], "end": m["end"]},
             {"level": DASHA_LEVELS[1], "lord": b["lord"], "start": b["start"], "end": b["end"]}]
    lord, start, years = b["lord"], b["start"], ys[m["lord"]] * ys[b["lord"]] / 120
    for level in DASHA_LEVELS[2:]:
        kids = sub_periods(rules, lord, start, years)
        k = next((k for k in kids if k["start"] <= now < k["end"]), kids[-1])
        chain.append({"level": level, "lord": k["lord"], "start": k["start"], "end": k["end"]})
        lord, start, years = k["lord"], k["start"], k["years"]
    return chain


def _applicable_roles(roles, as_maha):
    """Trishadaya is taught as an effect of the Mahādaśā, so a Bhukti lord does not carry it."""
    return [r for r in roles if as_maha or r != "Trishadaya lord"]


def _role_texts(rules, roles):
    return [rules["dasha_role_text"][r]["text"] for r in roles]


def running_roles(rules, dasha, roles):
    """The running Mahādaśā and Bhukti lords with their roles and the slides' wording for each role."""
    out = {}
    for key, period, as_maha in (("maha", dasha["cur_maha"], True), ("bhukti", dasha["cur_bhukti"], False)):
        mine = _applicable_roles(roles[period["lord"]], as_maha)
        out[key] = {"lord": period["lord"], "roles": mine, "text": _role_texts(rules, mine)}
    return out


def watch_periods(rules, dasha, roles, now, years=10):
    """Bhuktis within `years` of `now` whose Mahādaśā or Bhukti lord holds one of the six roles.

    kind is 'caution' when any caution role is present, 'favourable' when Trishadaya is the only one."""
    window_end = now + datetime.timedelta(days=years * _YEAR_DAYS)
    out = []
    for t in dasha["timeline"]:
        for b in t["bhuktis"]:
            if not (b["end"] > now and b["start"] < window_end):
                continue
            mine = set(_applicable_roles(roles[t["lord"]], True)) | set(_applicable_roles(roles[b["lord"]], False))
            ordered = [r for r in ROLE_ORDER if r in mine]
            if not ordered:
                continue
            kinds = {rules["dasha_role_text"][r]["kind"] for r in ordered}
            out.append({"start": b["start"], "end": b["end"], "maha": t["lord"], "bhukti": b["lord"],
                        "roles": ordered, "kind": "caution" if "caution" in kinds else "favourable"})
    return sorted(out, key=lambda w: w["start"])


# ---------------------------------------------------------------- prediction layers
def aspect_name(planet, h):
    """The name of a planet's aspect on the house h counted forward. Rahu and Ketu count anti-clockwise
    (teacher: 2nd, 5th, 9th), which lands on forward houses 12, 9, 5 — as aspectOrd() on the page."""
    if planet in ("Rahu", "Ketu"):
        return f"{ordinal((13 - h) % 12 + 1)} (anti-clockwise)"
    return ordinal(h)


def ordinal(n):
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def _clean(text):
    return text.strip().rstrip(".")


def _pair_row(rules, a, b):
    a, b = sorted((a, b), key=PLANET_ORDER.index)
    return next(x for x in rules["graha_pair"] if (x["a"], x["b"]) == (a, b))


def _dignity_texts(rules, d):
    eff = rules["dignity_effect"].get(d["label"])
    if not eff:
        return "", None
    return f"{d['label']}: {eff['text']}", eff["status"]


def bhava_nature_lines(rules, planet, house):
    """Session 26 lines for a planet of this nature in this house: the general line, the house's lines, then lines
    for this planet itself (R11). The Sun, a mild malefic, takes the malefic lines marked "(mild) " (R10); lines for any
    planet stay as written."""
    kind = nature_class(planet)
    rows = [r for r in rules["bhava_nature"] if r["nature"] in (kind, "any") and r["house"] in (None, house)
            and r["planet"] in (None, planet)]
    group = lambda r: 0 if r["house"] is None else 1 if r["planet"] is None else 2
    return [{"text": _mild(planet, r["nature"], r["text"]), "status": r["status"], "source": r["source"]}
            for r in sorted(rows, key=group)]


DEGREE_MALEFICS = ("Mars", "Saturn", "Rahu", "Ketu")     # S28 p.17 names these (not the Sun)


def degree_stage(rules, planet, deg, age=None):
    """S28 p.17: the planet's stage by its degree in the sign — {stage, lines, age_note}; None without a degree.
    Her malefic sentence is added for Mars, Saturn, Rahu and Ketu at 0-1° or 26-30°. Nothing else depends on it."""
    if deg is None:
        return None
    rows = [r for r in rules.get("degree_stages", []) if r["from"] <= deg < r["to"]
            and (r["applies"] == "any" or planet in DEGREE_MALEFICS)]
    rows.sort(key=lambda r: r["applies"] != "any")               # her stage lines first, then the malefic line
    if not rows:
        return None
    after = max((r["after_age"] for r in rows if r["after_age"] is not None), default=None)
    note = ""
    if after is not None and age is not None:
        a = int(age)
        note = f"Age {a}: past {after}, so it now gives its results." if age >= after else f"Age {a}: results from about {after}."
    stage = next((r["stage"] for r in rows if r["applies"] == "any"), rows[0]["stage"])
    return {"stage": stage, "lines": [r["text"] for r in rows], "age_note": note}


def twelfth_line(rules, house):
    """The 12th-house line (S23-2024 p.19, S24 p.13, S25 p.29), shown right after the dignity line."""
    if house != 12:
        return ""
    return next((r["text"] for r in rules["conditions"] if r["key"] == "twelfth_house"), "")


MARS_REMEDY_HOUSES = (2, 7, 8, 12)     # class of 22 Oct 2026: the 8th "irrespective of the planet with Mars"; the 2nd and
#                                        12th "the same remedies"; the 7th is Kuja doṣa (and takes the "Kuja" rows too)


def planet_remedies(rules, planet, house):
    """Her remedies for this planet in this house (S23_Remedies): the "Mars" rows for Mars in the 2nd, 7th, 8th or
    12th, then the "Kuja" rows for Mars in the 7th; [] otherwise ("otherwise it is not required")."""
    if planet != "Mars" or house not in MARS_REMEDY_HOUSES:
        return []
    topics = ("Mars", "Kuja") if house == 7 else ("Mars",)
    return [r["text"] for t in topics for r in rules["remedies"] if r["topic"] == t]


def graha_bhava(rules, lagna, signs, planet, deg, waxing, ctx=None):
    """Layer 1: the planet's cell text for its house, dignity line, digbala line and class readings.
    `ctx` (context()) gives the whole chart; without it only this planet's degree is known."""
    ctx = ctx or context(lagna, signs, {planet: deg} if deg is not None else {}, waxing)
    house = house_of(lagna, signs[planet])
    cell = next(x for x in rules["graha_in_bhava"] if x["planet"] == planet and x["house"] == house)
    dig = dignity(rules, planet, signs[planet], deg)
    dignity_line, dignity_status = _dignity_texts(rules, dig)
    reading = next(r for r in class_readings(rules, lagna, signs, ctx) if r["planet"] == planet)
    dg = digbala(rules, planet, house)
    row = rules["digbala"].get(planet)
    if dg == "strong":
        digbala_line = f"{planet} gains directional strength (digbala) in the {ordinal(house)} house."
    elif dg == "lost":
        digbala_line = (f"{planet} loses directional strength (digbala) in the {ordinal(house)} house, "
                        f"opposite its strongest house, the {ordinal(row['strong'])}.")
    else:
        digbala_line = ""
    return {"planet": planet, "house": house, "nature": nature(planet),
            "moon_strength": moon_strength(waxing) if planet == "Moon" else "",
            "status": cell["status"], "source": cell["source"], "points": cell["points"],
            "extra": cell["extra"], "dignity": dig, "dignity_line": dignity_line, "dignity_status": dignity_status,
            "twelfth_line": twelfth_line(rules, house), "nature_lines": bhava_nature_lines(rules, planet, house),
            "remedies": planet_remedies(rules, planet, house),
            "digbala_line": digbala_line, "digbala_status": row["status"] if dg else None,
            "classes": reading["classes"], "class_texts": reading["texts"],
            "degree_stage": degree_stage(rules, planet, deg, ctx["age"]),
            "readings": [x["text"] for x in chart_readings(rules, ctx)
                         if (x["kind"] == "in" and planet in x["on"]) or (x["kind"] == "aspects planet" and planet in x["with"])]}


def _short_name(nm):
    return nm.split(" · ")[0].split(" (")[0]


PLACEMENT_CLASSES = ("Kendra", "Trikona", "Dusthana", "Badhaka")


def placement(rules, lagna, lord_of, sits_in):
    """S27 p.6: the classes of the house the lord sits in, and the sentence for them. A lord in the 6th, 8th or 12th
    is 'a difficult placement'."""
    if lord_of == sits_in:
        return [], "The lord sits in its own bhava, so the matters of this house are protected and strengthened."
    classes = [c for c in PLACEMENT_CLASSES if sits_in in class_houses(rules, c, lagna)]
    line = f"Placed in the {ordinal(sits_in)} house" + (f", a {' and '.join(classes)} bhava" if classes else "") + "."
    texts = [r["text"] for c in ("Kendra", "Trikona") if c in classes for r in rules["class_rules"]
             if r["class"] == c and r["applies"] == "any" and sits_in not in r["exclude_houses"]]
    if texts:
        line += " " + " ".join(texts)
    if sits_in in (6, 8, 12):
        line += " A difficult placement."
    return classes, line


def _dictum(rules, ctx, house):
    """S27 p.11: a lord aspecting its own house fortifies that house — unless the lord is debilitated (S28 p.13:
    the debilitated 10th lord aspects the 10th, yet the profession suffers; spec §6.2.1, S3)."""
    lord = house_lord(rules, ctx["lagna"], house)
    target = house_sign(ctx["lagna"], house)
    if lord in ctx["signs"] and dignity(rules, lord, ctx["signs"][lord], ctx["degs"].get(lord))["flag"] == "debilitated":
        return ""
    if lord in ctx["signs"] and any(t == target for _, t in aspect_signs(rules, lord, ctx["signs"][lord])):
        return f"The lord aspects its own house, so the {ordinal(house)} house is strong."
    return ""


def with_lord(rules, ctx, lord):
    """S27 p.16: planets conjoined with the lord, then planets aspecting it, each with the houses it rules and her
    Chart 3 sentences for a planet aspecting a lord of this planet's houses (S28 p.15)."""
    sg = ctx["signs"]
    mine = [x for x in chart_readings(rules, ctx)
            if x["kind"] == "aspects lord" and house_lord(rules, ctx["lagna"], x["house"]) == lord]
    out = [{"planet": p, "how": "with", "aspect": "", "rules": lords_houses(rules, ctx["lagna"], p), "meanings": [],
            "readings": []} for p in PLANET_ORDER if p != lord and p in sg and sg[p] == sg[lord]]
    out += [{"planet": a["by"], "how": "aspect", "aspect": aspect_name(a["by"], a["house_aspect"]),
             "rules": lords_houses(rules, ctx["lagna"], a["by"]),
             "meanings": _meanings(rules, a["by"], a["house_aspect"], house_of(ctx["lagna"], sg[a["by"]])),
             "readings": [x["text"] for x in mine if a["by"] in x["on"]]}
            for a in aspects_on(rules, ctx, sg[lord]) if a["by"] != lord]
    return out


def _blend(rules, lagna, x, y, sign):
    info = rules["reference"]["BHAVA_INFO"]
    a, b = info[str(x)], info[str(y)]
    return (f"The lord of the {ordinal(x)} house ({_short_name(a['nm'])}) is placed in the {ordinal(y)} house "
            f"({_short_name(b['nm'])}), in {rules['reference']['RASHI'][sign]['sanskrit']}. Blend their karakatwas — "
            f"{ordinal(x)} house: {_clean(a['sig'])}. {ordinal(y)} house: {_clean(b['sig'])}. "
            f"People: {a['rel']} with {b['rel']}. Body: {a['body']} with {b['body']}.")


def _exchange_blend(rules, x, y):
    info = rules["reference"]["BHAVA_INFO"]
    return (f"Parivartana: the lords of the {ordinal(x)} and {ordinal(y)} houses have exchanged signs. Blend the two "
            f"houses — {ordinal(x)} house: {_clean(info[str(x)]['sig'])}. {ordinal(y)} house: {_clean(info[str(y)]['sig'])}.")


def _taught_rows(rules, ctx, x, y, strength_word):
    """Her rows for the lord of x in y: the general row, then the strong and/or weak row chosen by its strength —
    each only if the dignity it states holds (LORD_IN_CLAIMS)."""
    rows = [r for r in rules["bhava_lord_in"] if (r["lord_of"], r["sits_in"]) == (x, y) and not r["exchange"]
            and claim_holds(rules, ctx, LORD_IN_CLAIMS.get((x, y, r["condition"], False)), x)]
    pick = {"strong": ("strong",), "weak": ("weak",), "mixed": ("strong", "weak"), "depends": ("strong", "weak")}[strength_word]
    return [r for r in rows if r["condition"] == ""] + [r for c in pick for r in rows if r["condition"] == c]


def bhava_bhava(rules, ctx):
    """Layer 2 (Sessions 23, 26, 27): for each house X, its lord in house Y and sign S — the teacher's text (with her
    strong/weak lines chosen by R3) or a blend of both houses, the sign line, the placement, the dictum and the planets
    with or aspecting the lord. A Parivartana pair gives one entry, under the smaller house."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    lord_of = {h: house_lord(rules, lagna, h) for h in range(1, 13)}
    sits = {h: house_of(lagna, sg[lord_of[h]]) for h in range(1, 13) if lord_of[h] in sg}
    out = []
    for x in range(1, 13):
        if x not in sits:                                     # a partial chart: this lord's sign is not known
            continue
        lord, y = lord_of[x], sits[x]
        swap = (y if y != x and sits.get(y) == x and lord_of[y] != lord else None)
        if swap is not None and swap < x:
            continue                                          # shown with the smaller house of the pair
        strength_word = strength(rules, ctx, lord)
        if swap is not None:
            # a Parivartana row is found by its two houses (either order, any Condition), and so is its rule
            row = next((r for r in rules["bhava_lord_in"] if r["exchange"] and {r["lord_of"], r["sits_in"]} == {x, y}
                        and claim_holds(rules, ctx, LORD_IN_CLAIMS.get((min(x, y), max(x, y), "", True)), min(x, y))), None)
            # her Parivartana text first (if any), then her readings for either direction (each lord judged by its
            # strength) — on her Chart 3 both the 8↔12 line and her 8→12 line show (spec §9.1)
            chosen = ([row] if row else []) + _taught_rows(rules, ctx, x, y, strength_word) \
                + _taught_rows(rules, ctx, y, x, strength(rules, ctx, lord_of[y]))
            if chosen:
                text, status, source = "\n\n".join(r["text"] for r in chosen), chosen[0]["status"], chosen[0]["source"]
            else:
                text, status, source = _exchange_blend(rules, x, y), "blend", ""
            dictum = " ".join(d for d in (_dictum(rules, ctx, x), _dictum(rules, ctx, y)) if d)
        else:
            chosen = _taught_rows(rules, ctx, x, y, strength_word)
            if chosen:
                text, status, source = "\n\n".join(r["text"] for r in chosen), chosen[0]["status"], chosen[0]["source"]
            else:
                text, status, source = _blend(rules, lagna, x, y, sg[lord]), "blend", ""
            dictum = _dictum(rules, ctx, x)
        classes, line = placement(rules, lagna, x, y)
        house_aspects = [dict(house=h, **a) for h in ((x, swap) if swap else (x,)) for a in _aspect_items(rules, ctx, h)]
        out.append({"lord_of": x, "lord": lord, "sits_in": y, "sign": sg[lord], "text": text, "status": status,
                    "source": source, "sign_line": sign_line(rules, sg[lord]), "placement": classes, "placement_line": line,
                    "strength": strength_word, "dictum": dictum, "with_lord": with_lord(rules, ctx, lord), "exchange": swap,
                    "house_aspects": house_aspects})
    return out


# ---------------------------------------------------------------- Life areas (S27 pp.5-16)
def _karakas(rules, ctx, row):
    """The area's karakas; for a row with a female karaka (Marriage) the form's gender chooses (R4)."""
    sg, female = ctx["signs"], row["karaka_female"]
    planets, note = list(row["karakas"]), ""
    if female:
        if ctx["gender"] == "Female":
            planets = [female]
            r = _condition_row(rules, "jupiter_husband", "Jupiter", None)
            note = r["text"] if r else ""
        elif ctx["gender"] == "Male":
            v = planets[0]
            r = _condition_row(rules, "venus_meets_wife", v, house_of(ctx["lagna"], sg[v])) if v in sg else None
            note = r["text"] if r else ""
        else:
            note = f"For a woman's chart the husband's karaka is {female}."
    out = []
    for k in planets:
        if k not in sg:
            continue
        out.append({"planet": k, "house": house_of(ctx["lagna"], sg[k]), "sign": sg[k],
                    "rashi": rules["reference"]["RASHI"][sg[k]]["sanskrit"],
                    "dignity": dignity(rules, k, sg[k], ctx["degs"].get(k))["label"], "combust": combust(rules, ctx, k),
                    "retro": bool(ctx["retro"].get(k)), "strength": strength(rules, ctx, k), "note": note,
                    "malefic_aspects": [a["by"] for a in aspects_on(rules, ctx, sg[k])
                                        if a["by"] in STRENGTH_MALEFICS and a["by"] != k]})
    return out


def _aspects(rules, ctx, planet_a, planet_b):
    """Aspect names of planet_a's aspects that fall on planet_b's sign."""
    sg = ctx["signs"]
    return [aspect_name(planet_a, h) for h, t in aspect_signs(rules, planet_a, sg[planet_a]) if t == sg[planet_b]]


def pac_links(rules, ctx, a, b):
    """S27 pp.17-20: Position, Aspect, Conjunction links between houses a and b through their lords."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    la, lb = house_lord(rules, lagna, a), house_lord(rules, lagna, b)
    A, B = ordinal(a), ordinal(b)
    at = lambda p: house_of(lagna, sg[p]) if p in sg else None
    hits = lambda p, h: p in sg and any(t == house_sign(lagna, h) for _, t in aspect_signs(rules, p, sg[p]))
    out = []
    if at(la) == b:
        out.append(f"{A} lord in the {B}")
    if at(lb) == a:
        out.append(f"{B} lord in the {A}")
    if at(la) == b and at(lb) == a and la != lb:
        out.append(f"Exchange between the {A} and {B} lords")
    if la != lb and la in sg and lb in sg and sg[la] == sg[lb]:
        out.append(f"The {A} and {B} lords are together")
    if hits(la, b):
        out.append(f"The {A} lord aspects the {B} house")
    if hits(lb, a):
        out.append(f"The {B} lord aspects the {A} house")
    if la != lb and la in sg and lb in sg:
        if _aspects(rules, ctx, la, lb):
            out.append(f"The {A} lord aspects the {B} lord")
        if _aspects(rules, ctx, lb, la):
            out.append(f"The {B} lord aspects the {A} lord")
    return out


def planet_link(rules, ctx, p, q):
    """A conjunction or mutual aspect between two planets (S27 p.13: 'Mer and Ketu Combo')."""
    sg = ctx["signs"]
    if p not in sg or q not in sg:
        return []
    out = []
    if sg[p] == sg[q]:
        out.append(f"{p} and {q} are together in the {ordinal(house_of(ctx['lagna'], sg[p]))}")
    for x, y in ((p, q), (q, p)):
        out += [f"{x} aspects {y} ({name} aspect)" for name in _aspects(rules, ctx, x, y)]
    return out


def _bhava_step(rules, ctx, h, layer2):
    lagna, sg = ctx["lagna"], ctx["signs"]
    sign = house_sign(lagna, h)
    occ = []
    for p in occupants(lagna, sg)[h]:
        g = graha_bhava(rules, lagna, sg, p, ctx["degs"].get(p), ctx["waxing"], ctx=ctx)
        occ.append({"planet": p, "nature": nature(p), "text": "\n\n".join(g["points"]), "status": g["status"],
                    "nature_lines": [x["text"] for x in g["nature_lines"]],
                    "debilitated": g["dignity"]["flag"] == "debilitated"})
    aspecting = _aspect_items(rules, ctx, h)
    lord_p, lord, company = house_lord(rules, lagna, h), None, []
    if lord_p in sg:
        y = house_of(lagna, sg[lord_p])
        entry = next(e for e in layer2 if e["lord_of"] == h or e["exchange"] == h)
        lord = {"planet": lord_p, "house": y, "sign": sg[lord_p], "rashi": rules["reference"]["RASHI"][sg[lord_p]]["sanskrit"],
                "placement_line": placement(rules, lagna, h, y)[1],
                "dignity": dignity(rules, lord_p, sg[lord_p], ctx["degs"].get(lord_p))["label"],
                "strength": strength(rules, ctx, lord_p), "text": entry["text"], "status": entry["status"],
                "dictum": _dictum(rules, ctx, h)}
        company = with_lord(rules, ctx, lord_p)
    return {"house": h, "sign": sign, "rashi": rules["reference"]["RASHI"][sign]["sanskrit"],
            "sign_line": sign_line(rules, sign), "occupants": occ, "aspecting": aspecting, "lord": lord,
            "with_lord": company}


def _summary(bhavas, karakas, pac, link):
    """Step 7: what supports the area and what puts it under pressure — two lists, no score."""
    good, bad = [], []
    benefic = lambda p: nature_class(p) == "benefic"
    for b in bhavas:
        H = ordinal(b["house"])
        for o in b["occupants"]:
            if benefic(o["planet"]) and o["debilitated"]:      # S28 p.6: "though it is a benefic it is weak and debilitated"
                bad.append(f"{o['planet']} (benefic, debilitated) in the {H}")
            else:
                (good if benefic(o["planet"]) else bad).append(f"{o['planet']} ({nature(o['planet'])}) in the {H}")
        for a in b["aspecting"]:
            if b["house"] == 11:                                # S28 p.14: aspects on the 11th bring gains from the houses ruled
                good.append(" ".join(x for x in (f"{a['by']} aspects the 11th", ruled_phrase(a["rules"])) if x))
            else:
                (good if benefic(a["by"]) else bad).append(f"{a['by']} ({nature(a['by'])}) aspects the {H}")
        lord = b["lord"]
        if lord:
            L = lord["planet"]
            if lord["strength"] == "strong":
                good.append(f"The {H} lord {L} is strong")
            elif lord["strength"] == "weak":
                bad.append(f"The {H} lord {L} is weak")
            if lord["dictum"]:
                good.append(f"The {H} lord {L} aspects its own house")
            if lord["house"] in (6, 8, 12):
                bad.append(f"The {H} lord {L} is in the {ordinal(lord['house'])}, a difficult placement")
            for w in b["with_lord"]:
                what = "is with" if w["how"] == "with" else "aspects"
                (good if benefic(w["planet"]) else bad).append(f"{w['planet']} ({nature(w['planet'])}) {what} the {H} lord")
    for k in karakas:
        if k["house"] in (6, 8, 12):                            # S28 p.10: the karaka in the 6th, the house of quarrels
            bad.append(f"Karaka {k['planet']} is in the {ordinal(k['house'])}")
        bad += [f"Karaka {k['planet']} is aspected by {m}" for m in k["malefic_aspects"]]
        if k["strength"] == "strong" and k["house"] not in (6, 8, 12):    # §6.2.3: otherwise a strong karaka supports
            good.append(f"Karaka {k['planet']} is strong")
        elif k["strength"] == "weak":
            bad.append(f"Karaka {k['planet']} is weak")
    good += [f"PAC link: {x}" for x in pac or []] + list(link or [])
    return good, bad


def life_area(rules, ctx, no):
    """Session 27's 7-step method for one Ready Reckoner area: the house(s), occupants, aspects, the lord, its company,
    the karaka(s), and what supports or presses on it. Love marriage adds the PAC link between the 5th and 7th and the
    Mercury-Ketu combination."""
    row = next(r for r in rules["life_areas"] if r["no"] == no)
    layer2 = bhava_bhava(rules, ctx)
    bhavas = [_bhava_step(rules, ctx, h, layer2) for h in row["houses"]]
    karakas = _karakas(rules, ctx, row)
    pac = link = None
    if row["link"] == "PAC" and len(row["houses"]) == 2:
        pac = pac_links(rules, ctx, *row["houses"])
        link = planet_link(rules, ctx, *row["karakas"][:2]) if len(row["karakas"]) >= 2 else []
    supports, pressure = _summary(bhavas, karakas, pac, link)
    return {"no": no, "area": row["area"], "houses": list(row["houses"]), "link": row["link"], "source": row["source"],
            "bhavas": bhavas, "karakas": karakas, "pac": pac, "planet_link": link, "supports": supports, "pressure": pressure}


def life_areas(rules, ctx):
    return [life_area(rules, ctx, r["no"]) for r in rules["life_areas"]]


# ---------------------------------------------------------------- the Prediction read bhāva by bhāva (spec 2026-10-13)
DIGBALA_NODE_TEXT = "none — a node has no directional strength"


def first_sentence(text):
    """A class's meaning: its Nature up to and including the first ". ", or the whole text."""
    i = text.find(". ")
    return text if i < 0 else text[:i + 1]


def planet_facts(rules, ctx, planet):
    """The facts box of a planet: its house and that house's classes, roles, dignity, digbala and strength."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    if planet not in sg:
        return None
    deg = ctx["degs"].get(planet)
    house = house_of(lagna, sg[planet])
    g = graha_bhava(rules, lagna, sg, planet, deg, ctx["waxing"], ctx=ctx)
    eff = rules["dignity_effect"].get(g["dignity"]["label"])
    row = rules["digbala"].get(planet)
    dg = digbala(rules, planet, house)
    if not row:
        text = DIGBALA_NODE_TEXT
    elif dg:
        text = g["digbala_line"]
    else:
        text = f"neither — strongest in the {ordinal(row['strong'])}, weakest in the {ordinal(row['lost'])}"
    return {"planet": planet, "sign": sg[planet], "rashi": rules["reference"]["RASHI"][sg[planet]]["sanskrit"], "deg": deg,
            "house": house, "retro": bool(ctx["retro"].get(planet)), "nature": nature(planet),
            "classes": house_class_matrix(rules, lagna)[house - 1]["classes"],
            "roles": planet_roles(rules, lagna, sg).get(planet, []), "dignity": g["dignity"],
            "dignity_effect": eff["text"] if eff else "", "dignity_status": g["dignity_status"],
            "digbala": (dg or "") if row else None, "digbala_text": text, "digbala_status": g["digbala_status"],
            "strength": strength_detail(rules, ctx, planet), "class_texts": g["class_texts"]}


def bhava_reading(rules, ctx, house, layer2=None):
    """One house with everything that bears on it, as Session 28 reads a chart: its classes, the four layers, its
    karaka(s), what supports it and what presses on it, and the life areas that read it."""
    lagna, sg = ctx["lagna"], ctx["signs"]
    layer2 = bhava_bhava(rules, ctx) if layer2 is None else layer2
    ref = rules["reference"]
    info = ref["BHAVA_INFO"][str(house)]
    sign = house_sign(lagna, house)
    names = house_class_matrix(rules, lagna)[house - 1]["classes"]
    bad = badhaka(rules, lagna, sg)
    by_name = {c["name"]: c for c in rules["classes"]}
    classes = []
    for n in names:
        c = by_name[n]
        note = ""
        if n == "Badhaka":
            note = (f"For a {MODE_WORD[bad['mode']]} ({bad['mode']}) Lagna the {ordinal(house)} is the Badhaka sthāna; "
                    f"its lord {bad['lord']} is the Badhakādhipati.")
        classes.append({"name": n, "other_names": c["other_names"], "meaning": first_sentence(c["nature"]), "note": note})
    gr = {x["planet"]: x for x in graha_rashi(rules, lagna, sg, ctx["degs"])}
    conds = chart_conditions(rules, ctx)
    occ = []
    for p in occupants(lagna, sg)[house]:
        g = graha_bhava(rules, lagna, sg, p, ctx["degs"].get(p), ctx["waxing"], ctx=ctx)
        x = gr[p]
        occ.append({"planet": p, "nature": nature(p), "facts": planet_facts(rules, ctx, p),
                          "text": "\n\n".join(g["points"]), "status": g["status"], "source": g["source"], "extra": g["extra"],
                          "moon_strength": g["moon_strength"], "nature_lines": g["nature_lines"],
                          "twelfth_line": g["twelfth_line"], "degree_stage": g["degree_stage"],
                          "conditions": [c for c in conds if c["planet"] == p], "readings": g["readings"],
                          "remedies": g["remedies"],
                          "graha_rashi": {k: x[k] for k in ("text", "status", "tatwa", "direction", "varna", "mode")},
                          "dignity_line": g["dignity_line"], "dignity_status": g["dignity_status"]})
    lord_p, lord, company = house_lord(rules, lagna, house), None, []
    if lord_p in sg:
        y = house_of(lagna, sg[lord_p])
        entry = next(e for e in layer2 if e["lord_of"] == house or e["exchange"] == house)
        other = (entry["lord_of"] if entry["exchange"] == house else entry["exchange"]) if entry["exchange"] else None
        lord = {"planet": lord_p, "facts": planet_facts(rules, ctx, lord_p), "house": y, "sign": sg[lord_p],
                "rashi": ref["RASHI"][sg[lord_p]]["sanskrit"], "exchange": other,
                "placement_line": placement(rules, lagna, house, y)[1], "text": entry["text"], "status": entry["status"],
                "source": entry["source"], "dictum": _dictum(rules, ctx, house)}
        company = with_lord(rules, ctx, lord_p)
    gg = graha_graha(rules, lagna, sg, ctx["degs"])
    karakas = _karakas(rules, ctx, {"karakas": list(info["karaka"]), "karaka_female": ""})
    supports, pressure = _summary([_bhava_step(rules, ctx, house, layer2)], karakas, None, None)
    return {"house": house, "sign": sign, "rashi": ref["RASHI"][sign]["sanskrit"], "name": _short_name(info["nm"]),
            "full_name": info["nm"], "significations": _clean(info["sig"]), "people": info["rel"], "body": info["body"],
            "classes": classes, "sign_line": sign_line(rules, sign), "supports": supports, "pressure": pressure,
            "occupants": occ, "aspecting": _aspect_items(rules, ctx, house), "lord": lord,
            "conjunctions": [c for c in gg["conjunctions"] if c["house"] == house],
            "planet_aspects": [a for a in gg["aspects"] if a["house"] == house], "lord_company": company,
            "karakas": [dict(k, facts=planet_facts(rules, ctx, k["planet"])) for k in karakas],
            "life_areas": [{"no": r["no"], "area": r["area"]} for r in rules["life_areas"] if house in r["houses"]]}


def graha_rashi(rules, lagna, signs, degs):
    """Layer 3: each planet in its rāśi — tatwa, direction, varna, mode — with the dignity strength line."""
    out = []
    for p in PLANET_ORDER:
        if p not in signs:
            continue
        r = rules["reference"]["RASHI"][signs[p]]
        dig = dignity(rules, p, signs[p], degs.get(p))
        strength_line, _ = _dignity_texts(rules, dig)
        taught = next((x for x in rules["graha_rashi"] if (x["planet"], x["rashi"]) == (p, signs[p] + 1)), None)
        if taught:
            text, status = taught["text"], taught["status"]
        else:
            text = (f"{p} in {r['sanskrit']} ({r['english']}): {r['tatwa']} tatwa, {r['direction']} direction, "
                    f"{r['varna']} varna, {r['mode']} rāśi. The rāśi's traits: {', '.join(r['traits'])}. {strength_line}")
            status = "blend"
        out.append({"planet": p, "sign": signs[p], "rashi": r["sanskrit"], "english": r["english"],
                    "house": house_of(lagna, signs[p]), "tatwa": r["tatwa"], "direction": r["direction"],
                    "varna": r["varna"], "mode": r["mode"], "dignity": dig["label"], "strength_line": strength_line,
                    "text": text, "status": status})
    return out


def graha_graha(rules, lagna, signs, degs=None):
    """Layer 4: conjunctions (same rāśi) and special aspects between planets.

    `degs` (planet -> degree in its sign) is optional; without it the combustion flag of a Sun conjunction is None."""
    ref = rules["reference"]
    combustible = set(ref["COMBUST_PLANETS"])
    placed = [p for p in PLANET_ORDER if p in signs]
    conjunctions = []
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            if signs[a] != signs[b]:
                continue
            row = _pair_row(rules, a, b)
            combust, note = False, ""
            if a == "Sun" and b in combustible:
                if degs and degs.get(a) is not None and degs.get(b) is not None:
                    combust = abs(degs[a] - degs[b]) <= ref["COMBUST_ORB"]
                    if combust:
                        effect = ref["PLANET_PROFILE"][b]["Combustion Effect"]
                        note = f"{b} is within {ref['COMBUST_ORB']}° of the Sun (combust): {effect}."
                else:
                    combust = None
            conjunctions.append({"a": a, "b": b, "house": house_of(lagna, signs[a]), "text": row["conjunction"],
                                 "status": row["status"], "combust": combust, "combust_note": note})
    aspects = []
    for p in placed:
        for h in ref["SPECIAL_ASPECTS"][p]:
            target = (signs[p] + h - 1) % 12
            for q in placed:
                if q == p or signs[q] != target:
                    continue
                row = _pair_row(rules, p, q)
                k = ref["KARAKATWAS"]
                text = (f"{p}'s {aspect_name(p, h)} aspect falls on {q}: {p}'s qualities ({k[p]['qualities']}) colour what "
                        f"{q} signifies ({k[q]['signifies']}).")
                if row["aspect"].strip():
                    text += " " + row["aspect"]
                aspects.append({"by": p, "to": q, "house_aspect": h, "house": house_of(lagna, signs[q]),
                                "text": text, "status": row["status"] if row["aspect"].strip() else "blend",
                                "jupiter_flag": p == "Jupiter",
                                "meanings": _meanings(rules, p, h, house_of(lagna, signs[p]))})
    return {"conjunctions": conjunctions, "aspects": aspects}


def five_step(rules, lagna, signs, house):
    """The slide-25 checklist for one bhava: the bhava, its lord's position, occupants, aspects onto it, karakas."""
    info = rules["reference"]["BHAVA_INFO"][str(house)]
    sign = house_sign(lagna, house)
    lord = house_lord(rules, lagna, house)
    aspecting = [{"by": p, "house_aspect": h, "aspect": aspect_name(p, h),
                  "meanings": _meanings(rules, p, h, house_of(lagna, signs[p]))} for p in PLANET_ORDER if p in signs
                 for h in rules["reference"]["SPECIAL_ASPECTS"][p] if (signs[p] + h - 1) % 12 == sign]
    return {"house": house, "name": info["nm"], "significations": info["sig"], "sign": sign, "lord": lord,
            "lord_house": house_of(lagna, signs[lord]) if lord in signs else None,
            "occupants": occupants(lagna, signs)[house], "aspecting": aspecting,
            "karakas": [{"planet": k, "house": house_of(lagna, signs[k])} for k in info["karaka"] if k in signs]}
