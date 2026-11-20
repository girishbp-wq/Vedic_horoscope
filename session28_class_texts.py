"""The class of 19 Nov 2026 (Session 28): the snapshot reading by benefic and malefic, the lords in the bhāvas (Layer 2),
the meaning of the Jupiter, Saturn and Mars aspects, the seven steps and the Ready Reckoner, her Q&A.

(Not the slide deck named "S28" in some source fields: that is an earlier term's deck. The slides she used in this class,
"MASTER COPY - Session 28", are the decks S26 and S27 that the app already holds.)

  LORD_IN        (lord_of, sits_in, text): her worked examples of a lord in a bhāva, new S23_BhavaLordIn rows;
  ASPECT_ADD     (planet, aspect) -> her explanation in class, added to the slide's S23_AspectMeaning row;
  KARAKA_FEMALE  life area no -> the karaka for a woman's chart (her answer: Parāśara's Jupiter for the husband);
  BHAVA_NATURE   (house, nature, planet, text): S23_BhavaNature rows;
  RELATION_ADD   (a, b) -> her line on that pair, added to the S23_GrahaPair Relation;
  REMEDIES       (topic, text, houses, source): her general answers as tips.

Three of her rules are code, in the placement line of a bhāva lord (bhava_rules.placement and its twins): wherever the
Lagna lord sits the person's focus goes; wherever the 3rd lord sits the person puts in effort; a lord in the 8th makes
its own bhāva the source of tension.

apply_teacher_slides.apply_s28_class() turns these into the S23_ rows of session23_rules.json.
"""

SOURCE = "Class 19 Nov 2026"

# (lord_of, sits_in, text) — her worked examples in class
LORD_IN = [
    (2, 11, "The 2nd lord (money) in the 11th (gains, friends): earnings grow, with gains through a good circle of "
            "friends."),
    (3, 2, "The 3rd lord in the 2nd: the person puts a lot of effort into earning money."),
    (3, 5, "The 3rd lord in the 5th: the person puts effort into higher learning."),
    (3, 10, "The 3rd lord in the 10th: the person puts a lot of effort into the profession, which may be connected with "
            "communication; the younger sibling may work with them."),
    (4, 8, "The 4th lord in the 8th: the family atmosphere, or property, becomes the source of tension."),
    (5, 11, "The 5th lord (pūrva puṇya) in the 11th (fulfilment of desires): the desires are fulfilled thanks to the "
            "pūrva puṇya."),
    (7, 8, "The 7th lord in the 8th: the marriage is the source of tension, problems and suffering — difficulties and "
           "struggles in married life."),
    (10, 8, "The 10th lord in the 8th: the profession is the source of tension; difficulties in the job."),
    (12, 7, "The 12th lord in the 7th: the spouse may be spiritual; expenditure in marriage; sleeplessness."),
]

# (planet, aspect in her count) -> her explanation in class, after the slide's line
ASPECT_ADD = {
    ("Jupiter", 5): "In class: thanks to that pūrva puṇya, the bhāva Jupiter's 5th aspect falls on grows and prospers "
                    "(abhivṛddhi).",
    ("Jupiter", 9): "In class: luck operates in the bhāva Jupiter's 9th aspect falls on — things come there by grace, "
                    "without effort, even when not worked for.",
    ("Saturn", 3): "In class: on the bhāva Saturn's 3rd aspect falls on you have to put in a lot of effort (where "
                   "Jupiter's 9th brings things by luck).",
    ("Saturn", 10): "In class: on the bhāva Saturn's 10th aspect falls on you are karmically bound to take "
                    "responsibility, and cannot run away from it (on the 10th: responsibility at work).",
    ("Mars", 4): "In class: protective of that bhāva and its people, and ready to fight for them (her example: friends "
                 "and elder siblings).",
    ("Mars", 8): "In class: a change is needed in that bhāva, or there will be disputes (on the Lagna: the person must "
                 "change).",
}

# life area no -> the karaka for a woman's chart
KARAKA_FEMALE = {11: "Jupiter"}            # Parāśara, which this course follows; the Nāḍī system takes Mars

# (house, nature, planet, text) — S23_BhavaNature
BHAVA_NATURE = [
    (4, "malefic", None, "With a malefic in the 4th, spending time near water — sitting by a river or a lake — gives "
                         "peace of mind."),
]

# (a, b) in planet order -> her line on that pair, after the Relation line
RELATION_ADD = {
    ("Moon", "Saturn"): "Together they give a kind of melancholy: the Moon is affected by Saturn's coldness.",
    ("Mars", "Saturn"): "One pulls slow and the other fast, so there is confusion about which direction to take.",
}

# (topic, text, houses, source) — S23_Remedies
REMEDIES = [
    ("Tip", "Benefic or malefic is a quick snapshot: a benefic in a bhāva brings its matters with ease, a malefic with "
            "struggle and effort — it does not deny them.", [], SOURCE),
    ("Tip", "When a benefic and a malefic share a bhāva both act: there is more struggle in the malefic's daśā–bhukti "
            "and more ease in the benefic's; the stronger planet (exalted, own or a friend's sign) speaks louder, like "
            "the loudest voice in a classroom.", [], SOURCE),
    ("Tip", "Her measure of a planet's results by dignity: exalted 100%, Mūlatrikoṇa 90%, own house 75%; a "
            "debilitated planet still gives results, only weaker.", [], SOURCE),
    ("Tip", "Even a combust Jupiter's aspect works, at about 80% of its effect.", [], SOURCE),
    ("Tip", "For a woman's chart the husband's karaka is Jupiter in Parāśara, which this course follows (the Nāḍī "
            "system takes Mars); Venus is the wife's. Kuja doṣa is a separate concept, read from Mars for both.", [],
     SOURCE),
    ("Tip", "Zero in on the bhāva the question is about and follow the seven steps; one placement alone never gives "
            "the answer — see the chart in totality.", [], SOURCE),
]
