#!/usr/bin/env python3
"""Ashtakavarga (Parashara) — Bhinnashtakavarga (BAV) and Sarvashtakavarga (SAV).

Each of the eight contributors (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
and the Lagna) gives one bindu to a target planet's chart in the signs that fall
in certain houses counted from the contributor's own sign.  The seven BAVs add up
to the SAV.

The rule tables below are the single source of truth: index.html embeds the same
table (checked by test_cross_impl.py) and make_ashtakavarga_xlsx.py reads it to
build the Excel workbook.

Usage:
    python3 ashtakavarga.py --lagna Leo --sun Aries --moon Cancer --mars Aries \\
        --mercury Aries --jupiter Sagittarius --venus Taurus --saturn Capricorn
    (signs by name, or by number 0 = Aries ... 11 = Pisces; add --json for JSON)
"""
import argparse
import json
import sys

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
CONTRIBUTORS = PLANETS + ("Lagna",)

# Classical bindu totals per planet; they always sum to 337.
EXPECTED_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                   "Jupiter": 56, "Venus": 52, "Saturn": 39}
SAV_TOTAL = 337

# RULES[target][contributor] = houses (counted from the contributor, 1 = its own
# sign) that receive a bindu in the target planet's Ashtakavarga.
#
# Source: Brihat Parashara Hora Shastra, ch. 66 (R. Santhanam's English translation).
# All 56 rows were checked against that chapter.  Where its rekha (auspicious) list has a
# transcription slip (Mercury <- Sun, Mercury <- Saturn, Jupiter <- Jupiter) the dot
# (karana) list of the same chapter settles it.  The Moon rows below are the chapter as
# printed, and match the reference file this project started from; see RULES_MOON_COMMON
# for the variant most modern books and software use.
RULES = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 9, 10, 11),
        "Mars": (2, 3, 5, 6, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 2, 4, 7, 8, 10, 11),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 4, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
}

# The Moon's own Ashtakavarga as given by most modern books and software.  It differs from
# the BPHS text above in three rows (Moon, Mars, Jupiter) and has the same totals, so the
# checksums cannot tell the two apart.  To use it:
#     compute(signs, rules={**RULES, "Moon": RULES_MOON_COMMON})
RULES_MOON_COMMON = {
    "Sun": (3, 6, 7, 8, 10, 11),
    "Moon": (1, 3, 6, 7, 10, 11),
    "Mars": (2, 3, 5, 6, 9, 10, 11),
    "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
    "Jupiter": (1, 4, 7, 8, 10, 11, 12),
    "Venus": (3, 4, 5, 7, 9, 10, 11),
    "Saturn": (3, 5, 6, 11),
    "Lagna": (3, 6, 10, 11),
}


class AshtakavargaError(ValueError):
    """Bad chart input, or a rule table that fails its classical checksum."""


def validate_rules(rules=RULES):
    """Refuse a rule table whose per-planet totals differ from the classical ones."""
    for target in PLANETS:
        row = rules.get(target)
        if row is None or sorted(row) != sorted(CONTRIBUTORS):
            raise AshtakavargaError(f"{target}: table must list all eight contributors")
        total = 0
        for c in CONTRIBUTORS:
            houses = tuple(row[c])
            if len(set(houses)) != len(houses) or not all(
                    isinstance(h, int) and 1 <= h <= 12 for h in houses):
                raise AshtakavargaError(f"{target} <- {c}: houses must be unique, 1-12")
            total += len(houses)
        if total != EXPECTED_TOTALS[target]:
            raise AshtakavargaError(
                f"{target}: table has {total} bindus, but the classical total is "
                f"{EXPECTED_TOTALS[target]}")


def _check_sign(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 11:
        raise AshtakavargaError(f"{name}: sign must be an integer 0-11, got {value!r}")


def bindu_signs(target, contributor, from_sign, rules=RULES):
    """Signs (0-11) that receive a bindu in `target`'s chart from `contributor`."""
    return sorted((from_sign + h - 1) % 12 for h in rules[target][contributor])


def compute(signs, rules=RULES):
    """signs: {contributor: sign 0-11 (0 = Aries)} for all eight contributors.

    Returns {"bav": {planet: [12 bindu counts by sign]}, "sav": [12 counts]}.
    """
    unknown = sorted(set(signs) - set(CONTRIBUTORS))
    if unknown:
        raise AshtakavargaError(f"unknown contributor: {', '.join(unknown)}")
    for c in CONTRIBUTORS:
        if c not in signs:
            raise AshtakavargaError(f"missing sign for {c}")
        _check_sign(c, signs[c])
    validate_rules(rules)

    bav = {}
    for target in PLANETS:
        counts = [0] * 12
        for c in CONTRIBUTORS:
            for s in bindu_signs(target, c, signs[c], rules):
                counts[s] += 1
        bav[target] = counts
    sav = [sum(bav[p][s] for p in PLANETS) for s in range(12)]
    return {"bav": bav, "sav": sav}


def parse_sign(text):
    """'Leo' / 'leo' / '4' -> 4."""
    t = str(text).strip()
    if t.isdigit() and 0 <= int(t) <= 11:
        return int(t)
    for i, name in enumerate(SIGNS):
        if name.lower() == t.lower():
            return i
    raise AshtakavargaError(f"unknown sign {text!r} (use a name or 0-11)")


def _format(result):
    head = "".join(f"{s[:3]:>5}" for s in SIGNS)
    lines = [f"{'':<9}{head}  Total"]
    for p in PLANETS:
        row = result["bav"][p]
        lines.append(f"{p:<9}" + "".join(f"{v:>5}" for v in row) + f"{sum(row):>7}")
    sav = result["sav"]
    lines.append(f"{'SAV':<9}" + "".join(f"{v:>5}" for v in sav) + f"{sum(sav):>7}")
    ok = "ok" if sum(sav) == SAV_TOTAL else f"WRONG, should be {SAV_TOTAL}"
    lines.append(f"SAV total {sum(sav)} ({ok})")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ashtakavarga (BAV + SAV) from sign placements.")
    for c in CONTRIBUTORS:
        ap.add_argument(f"--{c.lower()}", required=True, metavar="SIGN",
                        help=f"{c}'s sign (name or 0-11, Aries = 0)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args(argv)
    try:
        signs = {c: parse_sign(getattr(args, c.lower())) for c in CONTRIBUTORS}
        result = compute(signs)
    except AshtakavargaError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(result) if args.json else _format(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
