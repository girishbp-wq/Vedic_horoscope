"""The teacher's texts from Session 28 (Chart 3, degree stages) and Session 29 (tip), as printed on her slides.

Transcribed from the PDFs (S28, 12/09/2024; S29, 18/09/2024) and checked against the page images. Sources cite the
deck and page. Edits made to the printed text, and nothing else:
- spaces before ',' and '.' closed up; a bold heading line and the line under it joined with '. ';
  '*' written for the degree sign printed as '°';
- misspellings whose meaning is unambiguous corrected (old -> new):
    aspectin -> aspecting
    there in no easy flow -> there is no easy flow
    wouid -> would
    couid -> could
    ia -> is
    competetive -> competitive
    harmonal -> hormonal
    cusines -> cuisines
    undiagnoisable -> undiagnosable
    inheritence -> inheritance
    seperative -> separative
    therby -> thereby
    Rahus's -> Rahu's
    wife . daughter -> wife, daughter
- a sentence that starts in the middle of one of hers, or after a full stop, starts with a capital ("As sun is
  aspecting…", "The house of the native…"); a reading that ends without a full stop gets one;
- every Chart 3 sentence starts 'In her example chart (S28): ' (it applies to any chart with the same placement);
- the degree bands are closed by whole degrees (spec ruling S8): young 1°-5°59', adult 6°-17°59', mature 18°-25°59'.

apply_teacher_slides.apply_s28_29() turns these into the S23_ rows of session23_rules.json.
"""

_EX = "In her example chart (S28): "

# (lord_of, sits_in, condition, exchange, text, source) — S23_BhavaLordIn
LORD_IN = [
    (2, 9, "", False, _EX + "2 nd Lord Saturn is posited in 9 th House. This native gets finances from his father. "
                            "He has Vaak Siddhi. The family members are Dharmic in nature.", "S28 p.4"),
    (3, 9, "", False, _EX + "Saturn being the 3 rd lord posited in 9 th house, indicates that the native puts lot of "
                            "efforts to please his father, it also indicates that he is very traditional.", "S28 p.12"),
    (4, 7, "", False, _EX + "4 rth lord is posited in 7 th, so he will be providing happiness to spouse or he will find "
                            "peace of mind when he does business or interacting with others.", "S28 p.6"),
    (5, 8, "", False, _EX + "5 th lord Mars is in the 8 th house, The native will be worried about his son all the time. "
                            "5 th lord in the 8 th house makes the native interested in learning occult subjects.",
     "S28 p.7"),
    (6, 6, "", False, _EX + "6 th lord in the 6 th house makes the native health conscious. He could be competitive. "
                            "He will get loans easily.", "S28 p.8"),
    (7, 4, "weak", False, _EX + "7 th lord Mercury is debilitated and posited in the 4 th house, conjoined with Ketu in a "
                                "Dwiswabhava rashi ( jala tatwa - emotional ) So the quality of the married life is not "
                                "that great as Ketu ( fault finder and litigation ) creates hurdles in marital life. The "
                                "wife is a great Critic, fault finder and creates litigation in her talks and actions.\n\n"
                                "7th Lord Mercury is in 4 th house ( Mother ) with Ketu. The wife of this native always "
                                "have a separative influence towards his mother ie her mother in law.", "S28 pp.9-10"),
    (8, 12, "weak", False, _EX + "8th Lord Moon is debilitated and posited in 12 th house. His worries and tensions is due "
                                 "to expenses and losses.", "S28 p.11"),
    (8, 12, "", True, _EX + "12 th lord Mars is debilitated and posited in 8 th house and 8 th lord Moon is in Parivartana "
                            "with 12 th lord Mars. The native might lose his inheritance or unearned money.", "S28 p.16"),
    (9, 5, "", False, _EX + "9 th lord Sun is exalted and posited in 5th house. This native got benefits from the "
                            "government in the education of his son.", "S28 p.12"),
    (10, 4, "weak", False, _EX + "10 th lord Mercury is debilitated and conjoined with Ketu. Thus the profession of the "
                                 "native would suffer if he does any profession other than Rahu karakatwas.", "S28 p.13"),
    (11, 6, "", False, _EX + "11 th lord Venus is in 6 th house. So sometimes the gains can result in quarrels and "
                             "litigation. Friends could become enemies at times.", "S28 p.15"),
]

# (kind, planet, with, house, condition, text, source) — S23_ChartReadings
#   kind: "in" (Planet in House), "aspects" (Planet aspects House), "aspects lord" (Planet aspects the lord of House),
#         "aspects planet" (Planet aspects the planet named in With; House blank)
#   planet / with: a planet, "benefic", "malefic" or "Nth lord"; with "" = alone
#   condition: "", "exalted" or "debilitated" (of Planet)
CHART_READINGS = [
    ("aspects", "Jupiter", "", 1, "", _EX + "Jupiter is aspecting lagna, indicate the nature of the native. Here as Jup "
                                            "is aspecting, the person will be satwik in nature, dharmic and religious.",
     "S28 p.2"),
    ("aspects", "benefic", "", 1, "", _EX + "Jupiter a benefic is aspecting the lagna, so life will be smooth going and "
                                            "easy.", "S28 p.2"),
    ("aspects", "1st lord", "", 1, "", _EX + "As LL Jup is aspecting the Lagna and the bhava karaka Sun ( Arogya karaka ) "
                                             "is exalted, he will have a good health in general.", "S28 p.2"),
    ("aspects", "malefic", "malefic", 2, "", _EX + "Two malefics are aspecting the 2 nd bhava. So there is no easy flow "
                                                   "of money.", "S28 p.3"),
    ("aspects", "Mars", "Rahu", 2, "", _EX + "Mars and Rahu are aspecting the 2 nd bhava. This native could have "
                                             "aggressive, anger, fast and loud speech. Family members could be short "
                                             "tempered. The native would like to have spicy, hot food and might also like "
                                             "to try different cuisines as well. The native's eyes would become Red ( mars ) "
                                             "and wide ( rahu influence ) while he talks in anger. The native has a cut mark "
                                             "near the eyebrows.", "S28 p.3"),
    ("aspects", "Mars", "Saturn", 3, "", _EX + "Mars and Saturn are aspecting the 3 rd house. The native had undergone a "
                                               "surgery ( Mars aspect ) in the wrist area ( 3 rd house ). His written "
                                               "communication would be very commanding and because of Saturn's aspect, "
                                               "there could be delay in communication. He would like to undertake new "
                                               "ventures. As Mars is aspecting he will be brave.", "S28 p.5"),
    ("aspects", "Jupiter", "", 3, "", _EX + "As Jupiter is aspecting the words that he writes are big in size.",
     "S28 p.5"),
    ("aspects", "3rd lord", "", 3, "", _EX + "3 rd house is also support as 3 rd lord is aspecting 3 rd house he will get "
                                             "good support.", "S28 p.5"),
    ("aspects", "Ketu", "", 3, "", _EX + "Ketu's aspect on the third house makes him give pauses when he is "
                                         "communicating.", "S28 p.5"),
    ("in", "Ketu", "", 4, "", _EX + "Ketu a malefic in 4 rth house will not give peace of mind, the native will be "
                                    "detached to his family. The native will own a small vehicle as ketu denotes small. "
                                    "The house of the native may also be small.", "S28 p.6"),
    ("in", "Mercury", "Ketu", 4, "debilitated", _EX + "Mercury is also posited, though it is a benefic it is weak and "
                                                      "debilitated. Mother will be intelligent and also a fault finder. "
                                                      "There will be a break in education.", "S28 p.6"),
    ("in", "Sun", "", 5, "exalted", _EX + "Exalted Sun is posited in the 5 th bhava. The native's son would be egoistic, "
                                          "dominating and also a good administrator.", "S28 p.7"),
    ("in", "Venus", "", 6, "", _EX + "Venus is posited in the 6 th house, so the enemies of the native can be wife, "
                                     "daughter or ladies. Enemies would talk very pleasantly. He may be working with female "
                                     "colleagues. Venus in 6 th will give hormonal imbalance like thyroid, indigestion, loss "
                                     "of appetite.\n\nKaraka for wife ie Venus is posited in 6 th house ( house of litigation "
                                     "and quarrels ). His wife always quarrels with the native for small things.",
     "S28 pp.8-10"),
    ("aspects", "Saturn", "", 6, "", _EX + "Saturn gives chronic disease and thyroid is chronic.", "S28 p.8"),
    ("aspects", "Moon", "", 6, "", _EX + "Emotional disturbances leading to diseases as moon is aspecting.", "S28 p.8"),
    ("aspects", "Rahu", "", 6, "", _EX + "Rahu gives undiagnosable disease.", "S28 p.8"),
    ("in", "Jupiter", "", 7, "", _EX + "7th House is Mithuna rashi ( Vayu tatwa ) occupied by Jup, a planet of wisdom. "
                                       "This native's spouse is intelligent and always gives advice to the native.",
     "S28 p.9"),
    ("aspects planet", "Rahu", "Venus", None, "", _EX + "Venus aspected by Rahu makes the wife very unconventional and "
                                                        "dominating. Venus ( karaka for relationships ) is aspected by "
                                                        "Rahu, thereby spoiling the same.", "S28 p.10"),
    ("in", "Mars", "", 8, "", _EX + "Mars is posited in the 8 th house. The native has Kuja dosha. The family members of "
                                    "the spouse are very dominating. Chances of surgeries or accidents are there. It makes "
                                    "the person impatient.", "S28 p.11"),
    ("aspects", "Ketu", "", 8, "", _EX + "Ketu is aspecting the 8 th house. The family members of the spouse are critics "
                                         "or fault finders.", "S28 p.11"),
    ("in", "Saturn", "", 9, "", _EX + "Saturn is posited in 9 th house. The father of the native is hard working and "
                                      "highly disciplined.", "S28 p.12"),
    ("in", "Rahu", "", 10, "", _EX + "Rahu is posited in 10 th house. The native can do a profession related to export, "
                                     "forex, chemicals, fertilizers, photography, or could work abroad preferably in "
                                     "Muslim countries.", "S28 p.13"),
    ("aspects", "Sun", "", 11, "", _EX + "As sun is aspecting his elder sibling might be popular or good in "
                                         "administration.", "S28 p.14"),
    ("aspects", "Jupiter", "", 11, "", _EX + "This native will have a good friend circle as jupiter is aspecting.",
     "S28 p.14"),
    ("aspects lord", "8th lord", "", 11, "", _EX + "Planets aspecting 11 th lord Venus are 8th lord Moon, This native "
                                                   "could get inheritance.", "S28 p.15"),
    ("aspects lord", "Rahu", "", 11, "", _EX + "Rahu's aspect on 11 th lord Venus can create gains from foreign source or "
                                               "outsiders.", "S28 p.15"),
    ("in", "Moon", "", 12, "", _EX + "Moon is posited in 12 th house. Expenses towards mother is possible.", "S28 p.16"),
    ("in", "8th lord", "", 12, "", _EX + "Moon is 8th Lord. So the native could get hospitalised due to chronic ailments.",
     "S28 p.16"),
    ("aspects", "Venus", "", 12, "", _EX + "Venus aspect on 12 th house can cause expenses due to wife as well.",
     "S28 p.16"),
]

_MALEFIC_DEGREES = ("Actually, it is great to have all the malefic planets (Saturn, Rahu, Ketu, Mars) either at 0° to 1 "
                    "or at 26 to 29.99°, because they lose their strength of giving malefic results.")

# (from, to, stage, applies, after_age, text, source) — S23_DegreeStages; degrees within the sign, `to` exclusive
DEGREE_STAGES = [
    (0, 1 / 60, "At 0 degree", "any", 30,
     "At 0 degree - If a planet is at 0 degree at the time person was born, then actually it means it just entered that "
     "particular sign at the exact moment of birth. Planets at 0° have 0 power. Lifelong? Certainly not. These planets "
     "gain strength through time and start making their impact on native's life after 30 years of age.", "S28 p.17"),
    (0, 1, "Infant", "any", 32,
     "Between 0 to 1° - If a planet is placed between these degrees, it is called infant. This again is a powerless state "
     "of planet and gives results after 30-32 years.", "S28 p.17"),
    (1, 6, "Young", "any", None,
     "Between 1° to 5° - It is called as young or teenager stage of a planet. Planets at these degrees are alive and "
     "kicking.", "S28 p.17"),
    (6, 18, "Adult", "any", None,
     "Between 6 to 17 - It is known as Adult stage of a planet. Ready to take up the challenges and perform at best of "
     "abilities.", "S28 p.17"),
    (18, 26, "Mature", "any", None,
     "Between 18 to 25 - It is Mature stage of a planet. They are much wiser now. These planets make us think like a "
     "matured person.", "S28 p.17"),
    (26, 30, "Old", "any", None,
     "Between 26 to 29.99° These are old planets. Are they useless? Certainly not.", "S28 p.17"),
    (0, 1, "Malefic", "malefic", None, _MALEFIC_DEGREES, "S28 p.17"),
    (26, 30, "Malefic", "malefic", None, _MALEFIC_DEGREES, "S28 p.17"),
]

# The malefics her degree slide names (Applies = "malefic" in S23_DegreeStages); the Sun is not among them.
MALEFICS_FOR_DEGREES = ("Mars", "Saturn", "Rahu", "Ketu")

# (topic, text, source) — S23_Remedies
REMEDIES = [
    ("Tip", "Never wear black coloured clothes when you are visiting a temple, a guru or when performing a vrata or a "
            "puja", "S29 p.50"),
]

# S23_ClassRules `When` (spec §6.2.5): the S25 p.10 Dusthana-malefic line shows only for a planet that is not weak.
CLASS_RULE_WHEN = {("Dusthana", "malefic"): "not weak"}
