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


def class_readings(rules, lagna, signs):
    """One entry per placed planet: {planet, house, classes, texts} from the ClassRules sheet.
    The Sun takes the malefic rules, each marked "(mild) "."""
    out = []
    for p in PLANET_ORDER:
        if p not in signs:
            continue
        house = house_of(lagna, signs[p])
        kind = nature_class(p)
        classes = [c for c in CLASS_ORDER if house in class_houses(rules, c, lagna)]
        texts = [_mild(p, r["applies"], r["text"]) for c in classes for r in rules["class_rules"]
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


def strength(rules, ctx, planet):
    """R3: 'strong' (exalted, Moolatrikona, own or friend's sign, or aspecting its own sign), 'weak' (debilitated,
    enemy's sign or combust), 'depends' when neither — or both — hold."""
    sign = ctx["signs"][planet]
    label = dignity(rules, planet, sign, ctx["degs"].get(planet))["label"]
    own = rules["reference"]["PLANET_OWN_HOUSES"].get(planet, [])
    strong = label in STRONG_LABELS or any(t + 1 in own for _, t in aspect_signs(rules, planet, sign))
    weak = label in WEAK_LABELS or combust(rules, ctx, planet)
    return "strong" if strong and not weak else "weak" if weak and not strong else "depends"


def lords_houses(rules, lagna, planet):
    return [h for h in range(1, 13) if house_lord(rules, lagna, h) == planet]


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
    for this planet itself (R11). The Sun, a mild malefic, takes the malefic lines marked "(mild) " (R10)."""
    kind = nature_class(planet)
    rows = [r for r in rules["bhava_nature"] if r["nature"] in (kind, "any") and r["house"] in (None, house)
            and r["planet"] in (None, planet)]
    group = lambda r: 0 if r["house"] is None else 1 if r["planet"] is None else 2
    return [{"text": ("(mild) " if planet == MILD_MALEFIC else "") + r["text"], "status": r["status"], "source": r["source"]}
            for r in sorted(rows, key=group)]


def twelfth_line(rules, house):
    """The 12th-house line (S23-2024 p.19, S24 p.13, S25 p.29), shown right after the dignity line."""
    if house != 12:
        return ""
    return next((r["text"] for r in rules["conditions"] if r["key"] == "twelfth_house"), "")


def graha_bhava(rules, lagna, signs, planet, deg, waxing):
    """Layer 1: the planet's cell text for its house, dignity line, digbala line and class readings."""
    house = house_of(lagna, signs[planet])
    cell = next(x for x in rules["graha_in_bhava"] if x["planet"] == planet and x["house"] == house)
    dig = dignity(rules, planet, signs[planet], deg)
    dignity_line, dignity_status = _dignity_texts(rules, dig)
    reading = next(r for r in class_readings(rules, lagna, signs) if r["planet"] == planet)
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
            "digbala_line": digbala_line, "digbala_status": row["status"] if dg else None,
            "classes": reading["classes"], "class_texts": reading["texts"]}


def _short_name(nm):
    return nm.split(" · ")[0].split(" (")[0]


def _position_wording(rules, lagna, lord_of, sits_in):
    if lord_of == sits_in:
        return "The lord sits in its own bhava, so the matters of this house are protected and strengthened."
    classes = [c for c in ("Kendra", "Trikona", "Dusthana") if sits_in in class_houses(rules, c, lagna)]
    if not classes:
        return f"The lord is placed in the {ordinal(sits_in)} house."
    texts = [r["text"] for c in classes for r in rules["class_rules"]
             if r["class"] == c and r["applies"] == "any" and sits_in not in r["exclude_houses"]]
    return f"Placed in the {ordinal(sits_in)} house, a {' and '.join(classes)} bhava: " + " ".join(texts)


def bhava_bhava(rules, lagna, signs):
    """Layer 2: one entry per bhava lord — the lord's own bhava blended with the bhava it sits in."""
    info = rules["reference"]["BHAVA_INFO"]
    out = []
    for h in range(1, 13):
        lord = house_lord(rules, lagna, h)
        if lord not in signs:                                 # a partial chart: this lord's sign is not known
            continue
        sits = house_of(lagna, signs[lord])
        taught = next((x for x in rules["bhava_lord_in"] if (x["lord_of"], x["sits_in"]) == (h, sits)), None)
        if taught:
            text, status = taught["text"], taught["status"]
        else:
            a, b = info[str(h)], info[str(sits)]
            text = (f"The lord of the {ordinal(h)} house ({_short_name(a['nm'])}) is placed in the {ordinal(sits)} house "
                    f"({_short_name(b['nm'])}). Blend their karakatwas — {ordinal(h)} house: {_clean(a['sig'])}. "
                    f"{ordinal(sits)} house: {_clean(b['sig'])}. People: {a['rel']} with {b['rel']}. "
                    f"Body: {a['body']} with {b['body']}. {_position_wording(rules, lagna, h, sits)}")
            status = "blend"
        out.append({"lord_of": h, "lord": lord, "sits_in": sits, "text": text, "status": status})
    return out


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
                                "jupiter_flag": p == "Jupiter"})
    return {"conjunctions": conjunctions, "aspects": aspects}


def five_step(rules, lagna, signs, house):
    """The slide-25 checklist for one bhava: the bhava, its lord's position, occupants, aspects onto it, karakas."""
    info = rules["reference"]["BHAVA_INFO"][str(house)]
    sign = house_sign(lagna, house)
    lord = house_lord(rules, lagna, house)
    aspecting = [{"by": p, "house_aspect": h} for p in PLANET_ORDER if p in signs
                 for h in rules["reference"]["SPECIAL_ASPECTS"][p] if (signs[p] + h - 1) % 12 == sign]
    return {"house": house, "name": info["nm"], "significations": info["sig"], "sign": sign, "lord": lord,
            "lord_house": house_of(lagna, signs[lord]) if lord in signs else None,
            "occupants": occupants(lagna, signs)[house], "aspecting": aspecting,
            "karakas": [{"planet": k, "house": house_of(lagna, signs[k])} for k in info["karaka"] if k in signs]}
