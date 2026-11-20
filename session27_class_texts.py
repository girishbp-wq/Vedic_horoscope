"""The class of 12 Nov 2026 (Session 27): Ketu in the 6th to 12th bhāvas, her remedies, her Q&A.

The recording starts in the middle of Ketu in the 6th, so Rāhu and Ketu in the 1st to 5th are not here; Ketu's
general rule (detachment, obstruction) opens the 1st-house row, as each planet's rule does. Her slide text for these
placements is already in session23_teacher_slides.py (deck S25 pp. 17-41).

  GRAHA_IN_BHAVA_EXTRA  the points from the recording (the Extra column);
  REMEDIES              (topic, text, houses, source) for S23_Remedies; houses [] = a general remedy for the planet;
                        topic "Tip" = a general answer of hers.

apply_teacher_slides.apply_s27_class() turns these into the S23_ rows of session23_rules.json.
"""

SOURCE = "Class 12 Nov 2026"

KETU_RULE = ("Ketu is detachment, as Rāhu is attachment: a headless, blind planet. Wherever Ketu sits there is "
             "detachment from that bhāva, confusion and obstruction — the results come late — but also spirituality "
             "and a search for something deeper.")

GRAHA_IN_BHAVA_EXTRA = {
    ("Ketu", 1): [KETU_RULE],
    ("Ketu", 5): [
        "Ketu in the 5th usually brings problems with conception (her answer in class).",
    ],
    ("Ketu", 6): [
        "Does not take revenge but stays silent, and God takes revenge for them: the plotting against them backfires, "
        "and they win over enemies by silence.",
        "Confusion at work: choosing a career is hard, and people can cheat them easily.",
        "Illnesses that are hard to diagnose: headaches, stomach problems, skin allergies.",
        "A loan trap: clears one debt and takes another.",
        "Detached at work: dislikes the job, the boss and the daily routine; changes jobs often, even quitting "
        "without thinking.",
    ],
    ("Ketu", 7): [
        "Mentally detached from the spouse though not separated: talks but does not connect, even with a good, "
        "beautiful, educated partner.",
        "Marries very late, or very early and it breaks; or marries someone from another region or caste.",
        "A karmic settlement, a debt from a past life, rather than a marriage for love; the spouse may be very "
        "spiritual, and a mystery to them.",
        "The partner is very different: talkative and silent, spiritual and materialistic, simple and modern.",
        "Better not to have a business partner (Ketu is obstruction): a solo business is better.",
    ],
    ("Ketu", 8): [
        "One of the most powerful placements for Ketu: strong intuition, sees what others cannot, can sense death "
        "before it comes; highly spiritual and unafraid of death, curious about the afterlife.",
        "A near-death experience, in a surgery or an accident, after which they are a different person.",
        "A very good researcher, going deep into the occult, the mystical and the hidden: astrologers, researchers, "
        "scientists.",
        "A difficult relationship with the in-laws, or spiritual in-laws, or living far from them.",
    ],
    ("Ketu", 9): [
        "A detached relationship with the father, who may be spiritual.",
        "Detached from religion's rules and rituals but very spiritual: makes their own path, and may go against "
        "their gurus or teachers.",
        "Luck is obstructed and comes late — hard work without matching results — then opens suddenly around 30 to "
        "32.",
        "Long pilgrimages, not for enjoyment but in search of truth or God; obstruction in higher education.",
    ],
    ("Ketu", 10): [
        "Changes jobs and businesses often — not unstable but bored and detached, wanting something new.",
        "Does not run after name and fame (\"just leave me alone\"), yet may become famous in spirituality, "
        "astrology, healing, research or foreign work.",
        "The boss is never happy, others take the credit, promotions are obstructed; cannot work under anyone and "
        "finds a suitable job with difficulty, but succeeds in spiritual fields.",
    ],
    ("Ketu", 11): [
        "Many friends but no true friend; detached from friends, the social circle and the elder siblings; dislikes "
        "parties and gatherings and likes to stay alone.",
        "Not interested in gains or money; spiritual goals; the income is not stable.",
        "The elder sibling lives far away or abroad, does not talk to them, or is very spiritual.",
    ],
    ("Ketu", 12): [
        "The planet of isolation in the house of isolation: withdrawn from society, as many sannyāsīs are; highly "
        "spiritual deep researchers with their own belief system.",
        "Poor sleep, waking around 2 or 3 at night; dreams of ancestors, past lives or the guru, or answers to "
        "problems in dreams.",
        "Loves solitude, temples, ashrams and mountains; meditation and yoga; people think it is depression, but it "
        "is their nature.",
        "Visits hospitals often.",
    ],
}

# (topic, text, houses, source) — S23_Remedies
REMEDIES = [
    ("Ketu", "Pray to Lord Gaṇeśa, and feed street dogs.", [], SOURCE),
    ("Ketu", "Take medical treatment, pray to Lord Gaṇeśa and feed street dogs.", [5], SOURCE),
    ("Ketu", "Feed a black dog — street dogs especially; help poor people who are sick.", [6], SOURCE),
    ("Ketu", "Never take a loan for the sake of others; don't fight your enemies, stay silent; exercise daily.", [6],
     SOURCE),
    ("Ketu", "Don't expect too much from your partner; give them space, and respect their silence; avoid business "
             "partnerships; marrying after 28 is better.", [7], SOURCE),
    ("Ketu", "Help widows and old people.", [8], SOURCE),
    ("Ketu", "Respect your father even when you disagree; never insult your religion, even if you don't follow its "
             "customs; visit a holy place at least once a year.", [9], SOURCE),
    ("Ketu", "Respect your boss, and try to be more stable and attached at work, not working like a machine.", [10],
     SOURCE),
    ("Ketu", "Don't expect help from friends, but help them without expecting anything; keep your elder siblings "
             "happy.", [11], SOURCE),
    ("Ketu", "Meditate, and do seva for people in hospital.", [12], SOURCE),
    ("Rahu", "Pray to Goddess Durgā, and do the Rāhu remedies.", [], SOURCE),
    ("Rahu", "Pray to Goddess Durgā every day (for obstruction with the in-laws).", [8], SOURCE),
    ("Tip", "You need not do every remedy: choose the general remedies of the planet that resonate with you.", [],
     SOURCE),
    ("Tip", "A planet's effect is stronger in its daśā; doing its remedies during that daśā–bhukti reduces the "
            "negative effects.", [], SOURCE),
    ("Tip", "Both the placement and the aspect act: the placement is much stronger, but a planet's qualities also "
            "colour the houses it aspects.", [], SOURCE),
    ("Tip", "Transit (gochara) gives about 25% of the effect; the birth chart is stronger.", [], SOURCE),
    ("Tip", "Astrology shows an indication, not the whole destiny: with free will and effort you can improve things — "
            "with Ketu in the 2nd, for example, make the effort to keep good relations with the family.", [], SOURCE),
    ("Tip", "Life's purpose is seen from the Lagna — its rāśi and the planets in it — and pūrva puṇya from the 5th "
            "house.", [], SOURCE),
    ("Tip", "The 6th is the house of disease; the 8th of chronic, long-lasting disease.", [], SOURCE),
]
