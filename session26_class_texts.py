"""The class of 4 Nov 2026 (Session 26): Venus and Saturn in the 12 bhāvas, her remedies by placement, her Q&A.

(Not the slide deck named "S26" in some source fields: that is an earlier term's deck.)

Her slide text for these 24 placements is already in session23_teacher_slides.py (decks S24 pp. 14-37 for Venus and
S25 pp. 2-16 for Saturn). These are the points she made in class, written from the recording as the other planets'
were; they show on the page as "From the recording".

  GRAHA_IN_BHAVA_EXTRA  the points that hold whatever the planet's strength (the Extra column);
  IF_WEAK / IF_STRONG   the points she gave for a weak or a strong planet (the IfWeak / IfStrong columns), shown by
                        the planet's overall strength (bhava_rules.strength_points);
  REMEDIES              (topic, text, houses, source) for S23_Remedies; houses [] = a general remedy for the planet,
                        else the card of the planet in one of those houses lists it; topic "Tip" = a general answer;
  RELATION_FRIENDS / RELATION_ENEMIES
                        her answer on two planets in one bhāva: friends work together smoothly, planets that are not
                        friends are "two contrasting energies" (the S23_GrahaPair Relation column).

Two of her answers are rules in the engines, not text: "for all the malefic planets, the Upachaya houses are good"
(bhava_rules.strength_overall) and the friendship of conjunct planets (the Relation column).

apply_teacher_slides.apply_s26_class() turns these into the S23_ rows of session23_rules.json.
"""

SOURCE = "Class 4 Nov 2026"

VENUS_RULE = ("Venus is pleasantness: whatever pleases the senses — a beautiful painting, melodious music, a fragrance "
              "— is Venus, with luxury, comfort, romance and desire. Wherever Venus sits you beautify that area of "
              "life, and the part of the body that bhāva rules is beautiful. In a man's chart Venus is the wife: its "
              "bhāva tells where he may meet her.")
SATURN_RULE = ("Saturn is the karma kāraka; its keywords are responsibility, duty, hard work and patience. Wherever "
               "Saturn sits is a responsibility you cannot run away from: in the 2nd you carry the family even as the "
               "youngest, in the 3rd your younger siblings, in the 7th your marriage even when it is troubled. Saturn "
               "does not deny, it delays: nothing comes easily there, it comes through hard work, patience and "
               "experience, and the part of the body that bhāva rules looks older. Saturn is not a bad planet; like "
               "every malefic it does well in the Upachaya houses (3, 6, 10, 11).")

# (planet, house) -> the points from the recording that hold whatever the planet's strength
GRAHA_IN_BHAVA_EXTRA = {
    ("Venus", 1): [
        VENUS_RULE,
        "Good-looking whatever the complexion: big eyes, an attractive smile, often a dimple; people turn to look as "
        "they walk by.",
        "Speaks sweetly and softly, always smiling, polite, never rude; loves perfume and good, branded, colourful "
        "clothes — always presentable, even when you knock at midnight.",
        "Falls in love easily, with a filmy idea of love; drawn to a beautiful partner.",
        "Found in the charts of actors, models and people who are simply beautiful; a very good placement for the "
        "film or fashion industry.",
    ],
    ("Venus", 2): [
        "Rich: income and savings kept as gold, jewellery and a good bank balance; money may come from fashion, "
        "films, singing, beauty, make-up or jewellery, or through the wife.",
        "Born into a rich family (a silver spoon), or the family's finances improve after the birth; a comfortable, "
        "well-nourished childhood.",
        "A beautiful face, sparkling eyes and a sweet, melodious, soothing voice: a singer, speaker, anchor or "
        "YouTuber.",
        "Eats in fine restaurants and five-star hotels, never at roadside stalls; loves sweets, chocolates and ice "
        "cream. Venus eats for taste, Jupiter when hungry — Jupiter takes the prasād for the blessing and likes "
        "traditional ghee sweets such as laddus.",
    ],
    ("Venus", 3): [
        "Creative with the hands — painting, knitting, sewing, embroidery, all full of colour; beautiful, well-kept "
        "hands; with the 10th lord's influence, a make-up artist.",
        "Pretty handwriting; writes poetry or romantic novels, a love-letter expert; always communicating with the "
        "spouse.",
        "Short trips for fashion shows or film shoots, and even a short trip must be luxurious.",
        "A benefic in the 3rd gives no push for effort (only a malefic does): dislikes hard work and struggle.",
        "The younger sibling is beautiful or loves luxuries.",
    ],
    ("Venus", 4): [
        "One of the best placements for Venus: a beautiful, clean, fragrant, artistically decorated home kept like a "
        "five-star hotel, a peaceful and welcoming atmosphere; grew up in a loving home.",
        "A creative, stylish, loving mother who loves luxury; loves the mother more than the father.",
        "A luxurious vehicle, or a small one with luxurious interiors, kept clean.",
        "A soft heart: forgives easily and loves everyone; a wonderful host.",
        "Too much comfort can make them lazy, happy to stay at home.",
        "In a man's chart, met the wife through the mother or in the home town; the mother is involved in, and "
        "supports, the marriage.",
    ],
    ("Venus", 5): [
        "A wonderful placement for love: a romantic, filmy love story; falls in love easily and proposes in a "
        "spectacular way; many proposals.",
        "Beautiful, talented children, and surely a daughter (Venus is a female planet).",
        "A born artist — acting, dancing, singing, painting, fashion, writing; can earn from creativity (a YouTube "
        "influencer); studies creative fields such as fashion, make-up or jewellery design.",
        "Venus is liquid cash: gains from the share market or a lucky draw.",
        "Too many love affairs can disturb the studies; heartbreaks; too filmy, not realistic.",
    ],
    ("Venus", 6): [
        "Works with beauty or feminine products (cosmetics, perfumes, hair products, clothes and fabrics), among many "
        "women colleagues and visitors, perhaps under a woman boss; beauty, fashion, luxury hotels or films suit them.",
        "Compassion: serves women in need and the poor.",
        "A difficult, uncomfortable house for soft Venus, which wants love and peace, not disputes: kidney, hormone or "
        "urinary trouble, diabetes, PCOD or PCOS.",
        "Takes loans for luxuries such as a car or a house, and must work hard to repay them.",
        "An enemy may be a woman, perhaps a beautiful one.",
    ],
    ("Venus", 7): [
        "A very good placement for marriage: a beautiful, fair, stylish, romantic spouse, perhaps from a rich family; "
        "luck multiplies after marriage.",
        "An early or a love marriage, a beautiful, luxurious wedding, and a romantic married life — made for each "
        "other.",
        "The spouse, or a beautiful woman, as business partner; business in fashion, clothes, jewellery or luxury "
        "goods suits them.",
    ],
    ("Venus", 8): [
        "A tricky placement: sudden money from the in-laws, insurance or a lottery; the wife may get property from "
        "her father.",
        "Not a good placement for marriage: a secret love affair is possible.",
        "The 8th is the private parts: urinary or kidney trouble, so keep them very clean.",
        "A benefic in the 8th gives a long life, with many ups and downs.",
        "Loves exploring the hidden side of life: mysticism, magic, astrology, numerology.",
    ],
    ("Venus", 9): [
        "Luck opens after marriage or after the birth of a daughter: the wife or daughter is the lucky charm; "
        "struggle before marriage, abundance after.",
        "A handsome, rich father who loves luxury and treats the native like a daughter; he may deal in fashion, "
        "beauty or luxury goods.",
        "Luxurious long journeys, business class and five-star hotels; may meet the wife on a long journey or abroad, "
        "or have a long-distance relationship before marriage.",
        "Lucky in dharma: pūjā in beautiful temples activates the luck; a dharmic, spiritual or well-educated wife.",
        "Success in higher education; beautiful thighs; a beautiful sister-in-law (the wife's sister) and beautiful "
        "grandchildren.",
    ],
    ("Venus", 10): [
        "Passionate about a creative career — artist, actor, designer, singer, interior decorator; name and fame in "
        "beauty, films or fashion without much effort; a career that pays well.",
        "A big, beautifully decorated office; may follow the father's career.",
        "The wife helps the career as manager, stylist or lucky charm, and the career improves after marriage; often "
        "met the wife at the workplace.",
        "Work with women's products, perfumes, clothing or cosmetics, among many women colleagues, perhaps as a "
        "manager.",
        "A beautiful niece.",
    ],
    ("Venus", 11): [
        "A very good placement for income: money from several sources at once (job, business, friends, the wife, "
        "social media); when one stops, another starts.",
        "Wishes are fulfilled easily — a car, a house.",
        "Rich, beautiful, stylish friends, many of them women; popular and invited to every party; may meet the wife "
        "among friends; sometimes too many affairs.",
        "A rich or beautiful elder sibling.",
    ],
    ("Venus", 12): [
        "A beautiful, luxurious bed and bedroom, a romantic spouse and good sleep.",
        "Foreign travel or settlement abroad, or a spouse from abroad; meets the wife in a secluded place or on a "
        "foreign holiday.",
        "Spends on luxuries, the wife and foreign trips — often unnecessary luxuries.",
        "Secret love affairs are possible.",
        "Beautiful feet and regular pedicures.",
    ],
    ("Saturn", 1): [
        SATURN_RULE,
        "Cold rather than warm or welcoming: serious, reserved and mature; looks older than their age (Mercury in "
        "the 1st looks younger).",
        "Lean and bony, with slow, measured movements and thoughtful expressions (Mars in the 1st moves quickly).",
        "Practical rather than emotional, responsible and disciplined; thinks before speaking; slow to open up or to "
        "trust; prefers a few meaningful relationships; does not show affection openly.",
        "Believes in hard work, not luck or short cuts — slow and steady wins the race; great patience; learns "
        "through experience and grows more confident with age.",
        "Each planet's wish in the 1st: the Sun says I want to lead, Venus I want comfort, Saturn I want to fulfil my "
        "responsibilities and keep everything organised.",
    ],
    ("Saturn", 2): [
        "Born into a family that values discipline and responsibility; takes up the family's responsibilities young, "
        "even as the youngest.",
        "Slow, measured, serious speech with carefully chosen words; a deep, dry, sometimes harsh voice; prefers "
        "meaningful conversation (Mercury in the 2nd speaks cleverly and fast, Venus sweetly, Saturn slowly and "
        "thoughtfully).",
        "Wealth comes slowly through steady hard work; spends cautiously and can seem stingy; good at long-term "
        "financial planning.",
        "Simple, home-cooked, traditional food; no fixed meal times when busy.",
        "The face looks older or wrinkles early; mature eyes even as a child; dry skin.",
    ],
    ("Saturn", 3): [
        "Communication does not flow: prefers writing to speaking, in very small letters; messages are cold, blunt "
        "and to the point, but well organised (Jupiter in the 3rd writes big letters, Venus neatly).",
        "Not adventurous: takes calculated risks, not impulsive ones; courage and skills grow with age; handles "
        "situations with great patience.",
        "Responsible and protective towards the younger siblings, a guiding role; a bond of duty rather than "
        "emotion, so the siblings may find them cold.",
        "Works step by step with patience (Mars in the 3rd says let's start now, Mercury let's analyse and plan).",
    ],
    ("Saturn", 4): [
        "A disciplined, mature, practical mother; feels responsible for her, though the bond may feel distant; may "
        "live apart from her.",
        "Takes on household responsibilities young; a simple, organised, disciplined home, sometimes uncomfortably "
        "strict; little peace at home, and worries about the family.",
        "Keeps emotions inside; happiness comes only after the duties are done.",
        "Takes education seriously, with delays; may study while carrying family responsibilities.",
        "Property comes through hard work and with delays; prefers land and long-term assets to luxuries; a "
        "practical, durable vehicle (Venus wants a luxurious one, Mercury compares mileage and features).",
        "Suits real estate, construction, civil engineering, architecture, agriculture, mining, property management "
        "and public infrastructure.",
    ],
    ("Saturn", 5): [
        "Practical, logical, structured thinking; thinks deeply before deciding; never impulsive.",
        "Slow to learn but retains it for long; learns by experience; good concentration and patience; delays or "
        "breaks in higher education, but completes it.",
        "Strict, traditional, disciplined parents who take the children's responsibility seriously; delays in "
        "conceiving; the first child is mature beyond their age.",
        "Does not fall in love easily; seeks commitment, loyalty and stability, not casual relationships (Venus in "
        "the 5th falls in love at the drop of a hat).",
        "Creativity in traditional, structured forms, developed with patience; cautious, long-term investments and "
        "no gambling.",
        "Disciplined mantra chanting and meditation; respects teachers and ancient knowledge.",
        "Stomach-related health issues (the 5th is the stomach).",
    ],
    ("Saturn", 6): [
        "Does not react to provocation at once: deals with enemies patiently and by strategy, and wins by "
        "persistence (Mars in the 6th fights at once, Mercury uses intelligence; Saturn keeps going until the enemy "
        "tires).",
        "Cautious with loans: plans the repayment before borrowing — excellent financial discipline.",
        "Works hard and responsibly, trusted by the boss; suits structured organisations and routine work; as a boss, "
        "strict and expects discipline and punctuality.",
        "Neglects health for work: take care of the health.",
        "Long court cases or disputes, settled through rules and procedures, with patience.",
    ],
    ("Saturn", 7): [
        "Takes marriage very seriously and feels responsible for the spouse; values a stable, committed, loyal "
        "relationship over romance; does not show love openly.",
        "Marriage is delayed; drawn to a mature, responsible, serious spouse.",
        "Enters business partnerships only after much thought and expects discipline and accountability; business "
        "grows slowly.",
        "Seen in public as serious and reserved, but reliable and responsible.",
        "What each planet wants from marriage: Venus love and romance, Jupiter understanding and respect, Saturn "
        "commitment, loyalty and stability.",
    ],
    ("Saturn", 8): [
        "Overcomes difficult situations with patience and persistent hard work; the ups and downs make them very "
        "mature; transformation comes after a long time.",
        "Prefers stability to sudden change; keeps the personal life private; drawn to mysteries and research.",
        "Responsible for ancestral property; the inheritance comes after delays and paperwork; holds on to inherited "
        "assets.",
        "Saturn is the roga kāraka: chronic health issues needing regular check-ups, but a long life; take care of "
        "the private parts.",
        "Fear of uncertainty, excessive worry, difficulty trusting others, holding on to the past.",
        "Cold, not very affectionate in-laws.",
        "Excellent research ability and a deep understanding of karma and transformation.",
    ],
    ("Saturn", 9): [
        "Believes success comes through hard work, not luck; delays rather than obstacles on the way.",
        "Believes in personal responsibility and karma; follows the religious traditions diligently, wanting to "
        "practise what dharma prescribes (Jupiter in the 9th wants the knowledge of the deeper truth, Mercury to "
        "analyse it logically).",
        "A disciplined, strict, traditional, serious and hard-working father; a dutiful rather than a warm bond.",
        "Delays in higher education; prefers structured, traditional study such as religion; finds a suitable guru "
        "with difficulty.",
        "Long journeys for work rather than for education; planned pilgrimages.",
        "Feels unlucky and unsupported, burdened by the family's traditions — yet strong moral principles, "
        "discipline, a deep understanding of the scriptures and practical wisdom.",
    ],
    ("Saturn", 10): [
        "Hard-working and responsible at work; takes professional duties very seriously; prefers stability and "
        "security.",
        "Slow, steady growth to a good, stable position in later years; recognition comes gradually; wants respect "
        "rather than popularity; known as reliable, sincere and disciplined.",
        "Humble, respects authority, works under demanding superiors; promotions are delayed.",
        "Suits government and administration, engineering and construction, law and the judiciary, management, "
        "mining, manufacturing and public service.",
    ],
    ("Saturn", 11): [
        "Earns through consistent hard work; prefers one stable income to many sources; wealth grows gradually with "
        "long-term planning; gains from large organisations and structured businesses.",
        "Realistic, practical ambitions, achieved with patience and hard work.",
        "A small circle of loyal, trustworthy, often older friends; long friendships.",
        "A formal, responsible bond with the elder sibling, whose support comes late.",
    ],
    ("Saturn", 12): [
        "Careful with money and avoids unnecessary expense (luxury is unnecessary); spends on practical needs, "
        "family duties, hospitals or institutions; long-term financial responsibilities.",
        "Work abroad or in multinational companies; lives away from the birthplace.",
        "Poor sleep from responsibilities and overthinking; a simple bed is enough.",
        "Drawn to meditation and disciplined spiritual practice, ancient scriptures and spiritual organisations; "
        "prefers privacy; a detached mind.",
        "Takes responsibility for the underprivileged or the elderly; may work in a hospital or a large "
        "organisation; social service.",
    ],
}

# Her points for a weak (or afflicted) and for a strong planet in the bhāva
IF_WEAK = {
    ("Venus", 1): ["Over-attached to beauty: hours in front of the mirror; lazy, wanting only comfort and luxury."],
    ("Venus", 2): ["Too many sweets: diabetes and weight gain."],
    ("Venus", 4): ["The mother may interfere in the relationship."],
    ("Venus", 8): ["In a man's chart the wife may suffer a chronic illness, or a secret affair may lead to divorce."],
    ("Saturn", 1): ["Lack of confidence, pessimism, fear of failure, excessive seriousness."],
    ("Saturn", 2): ["Hard to put feelings into words; harsh or pessimistic speech; money flows slowly; family "
                    "misunderstandings; burdened by the family's responsibilities."],
    ("Saturn", 3): ["Hesitates to take the initiative for fear of risk; finds it hard to express opinions; delays in "
                    "finishing projects; misunderstandings with the siblings; overthinking."],
    ("Saturn", 4): ["No peace at home; excessive worry about the house (her answer for a debilitated Saturn in the "
                    "4th)."],
    ("Saturn", 6): ["Overloaded with work, chronic worries, trouble with colleagues or employees, long disputes, "
                    "neglected health; rigid or critical at work."],
    ("Saturn", 10): ["Delayed career growth, little recognition, a heavy workload, career dissatisfaction, a poor "
                     "work-life balance; feels burdened."],
    ("Saturn", 11): ["Delayed gains and wishes, few social connections, friends who do not support, slow "
                     "professional growth."],
    ("Saturn", 12): ["Loneliness and isolation, excessive worry, cannot enjoy personal comforts, financial burdens, "
                     "sleep problems, cannot let go of the past."],
}
IF_STRONG = {
    ("Venus", 1): ["A good house and a luxurious car."],
    ("Venus", 2): ["Eats costly food and stays healthy."],
    ("Saturn", 2): ["Excellent financial planning and discipline, wealth built over time; handles family matters "
                    "responsibly; mature, thoughtful speech; keeps the family's duties, traditions and assets."],
    ("Saturn", 3): ["Perseverance and mental determination; the courage to face difficulties; masters skills through "
                    "patience and practice."],
    ("Saturn", 6): ["An excellent work ethic, a strong ability to overcome enemies, good discipline and organisation, "
                    "a strong service mentality."],
    ("Saturn", 7): ["A loyal, committed partner and a stable, lasting marriage; a strong sense of duty to the spouse; "
                    "a good name in professional dealings."],
    ("Saturn", 8): ["A long life, and the patience and hard work to overcome the 8th house's ups and downs, sudden "
                    "changes and obstacles (her answer for an exalted Saturn in the 8th)."],
    ("Saturn", 10): ["Excellent professional discipline, good leadership and administrative ability, authority and "
                     "respect in society."],
    ("Saturn", 11): ["Strong, lasting friendships, gains through large structured organisations, resources managed "
                     "systematically."],
    ("Saturn", 12): ["Controls unnecessary expenses; patience and endurance; meditation, self-reflection and "
                     "spiritual practice; a simple life."],
}

# (topic, text, houses, source) — S23_Remedies
REMEDIES = [
    ("Venus", "Always be clean and wear clean clothes.", [1], SOURCE),
    ("Venus", "Respect your wife or girlfriend and take good care of your wife: that makes Venus strong.", [1], SOURCE),
    ("Venus", "Don't get into extramarital affairs.", [1], SOURCE),
    ("Venus", "Speak sweetly, but always speak the truth.", [2], SOURCE),
    ("Venus", "Don't indulge in heavy food; save money; respect your family and your wife.", [2], SOURCE),
    ("Venus", "Don't fight with your wife or with women; learn to respect all women.", [6], SOURCE),
    ("Venus", "Never take a loan to buy luxuries; control sugar cravings and keep a healthy lifestyle.", [6], SOURCE),
    ("Venus", "Don't get involved in affairs at the workplace.", [6], SOURCE),
    ("Venus", "No secret affairs, and don't hide money from your wife.", [8], SOURCE),
    ("Venus", "Keep good hygiene.", [8], SOURCE),
    ("Venus", "Choose your friends wisely; don't spend your income on unnecessary things — save.", [11], SOURCE),
    ("Venus", "Take good care of your elder brother or sister, for your wishes to be fulfilled.", [11], SOURCE),
    ("Saturn", "Worship Lord Śiva or Hanumān: chant Om Namaḥ Śivāya or the Hanumān Chālīsā.", [8], SOURCE),
    ("Saturn", "Develop patience and humility, and accept your responsibilities (\"this is what my life is\"): you "
               "cannot run away from them. That makes Saturn strong.", [8], SOURCE),
    ("Saturn", "Take care of underprivileged people.", [8], SOURCE),
    ("Tip", "A remedy is needed only when there is a problem in that area of life; otherwise nothing need be done.",
     [], SOURCE),
]

# Her answer on two planets in one bhāva ({a}, {b} in planet order)
RELATION_FRIENDS = ("{a} and {b} are friends: each takes on the other's influence and both work together in that "
                    "bhāva, so things go easier and smoother.")
RELATION_ENEMIES = ("{a} and {b} are not friends: two contrasting energies work in that bhāva, so that area of life "
                    "sees some stress.")
