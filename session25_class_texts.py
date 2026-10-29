"""The class of 29 Oct 2026 (Session 25): Mercury and Jupiter in the 12 bhāvas, her remedies by placement, her Q&A.

(Not the slide deck named "S25" in some source fields: that is an earlier term's deck.)

Her slide text for these 24 placements is already in session23_teacher_slides.py (decks S23-2024 pp. 32-44 and S24
pp. 2-13). These are the points she added in class that the slides do not make, written from the recording as the
Sun's, the Moon's and Mars's were; they show on the page as "From the recording".

  GRAHA_IN_BHAVA_EXTRA  the points that hold whatever the planet's strength (the Extra column);
  IF_WEAK / IF_STRONG   the points she gave for a weak or a strong planet (the IfWeak / IfStrong columns), shown by
                        the planet's overall strength (bhava_rules.strength_points);
  REMEDIES              (topic, text, houses, source) for S23_Remedies; houses [] = a general remedy for the planet,
                        else the card of the planet in one of those houses lists it (bhava_rules.planet_remedies).

apply_teacher_slides.apply_s25_class() turns these into the S23_ rows of session23_rules.json.
"""

SOURCE = "Class 29 Oct 2026"

MERCURY_RULE = ("Mercury is the prince among the planets (the Sun the king, the Moon the queen, Mars the commander-in-"
                "chief): young, witty and fun-loving, never a serious planet. Wherever Mercury sits, that is the area "
                "of life where you show your intelligence and like to learn — the business mind and the calculation "
                "are always on there. Mercury's quarrels are fought with words, never physically.")
JUPITER_RULE = ("Jupiter is the biggest planet and the planet of wisdom: a mature person, where Mercury is the young "
                "prince. Wherever Jupiter sits, that bhāva expands (abhivṛddhi). Its keyword is respect: respect the "
                "person of the bhāva Jupiter is in, whether you like it or not, or Jupiter becomes weak.")


def _respect(who):
    return (f"Jupiter's keyword is respect: respect {who}, whether you like it or not — that keeps Jupiter strong.")


# (planet, house) -> the points from the recording that hold whatever the planet's strength
GRAHA_IN_BHAVA_EXTRA = {
    ("Mercury", 1): [
        MERCURY_RULE,
        "Looks younger than their age (forty or fifty, and looks twenty-five); sharp eyes, a thin body, walks fast; "
        "talks with the hands; the face shows every feeling.",
        "A \"computer brain\": learns in two days what takes others a month; loves solving puzzles; good at mimicry, "
        "languages and comedy.",
        "Dual-minded: making a decision is hard for them.",
        "An extrovert who talks to a stranger like an old friend; so good with words they could sell a comb to a "
        "bald man — marketing suits them.",
        "A childish nature: anger and quarrels are forgotten quickly; yet nervous, and overthinks small things.",
        "Rarely stays long in one kind of job: needs change and something to learn. Business suits them best; often "
        "two sources of income.",
    ],
    ("Mercury", 2): [
        "A sweet, soft voice but calculated words; can convince anyone — anchoring and teaching suit them.",
        "Two ways of speaking: soft with the family, business-like with the world; speaks in points (\"point 1, "
        "point 2\").",
        "May talk too much, and about money; keeps an account of every rupee, and sometimes worries about money.",
        "Earns through speech (counsellor, orator, tuitions); usually a permanent job and a side income, such as "
        "evening tuitions. Saves money for books and courses: learning comes first.",
        "A talkative family, or a business or teachers' family; often the smartest in it, the one everyone asks for "
        "advice; family quarrels are arguments of words.",
        "Talks while eating or eats fast; likes green leafy vegetables and new, mixed (chatpaṭā) tastes; could earn "
        "by a food or finance blog.",
        "Sharp eyes that notice every detail; neat, clean but small handwriting.",
    ],
    ("Mercury", 3): [
        "Courage of the mind and of words, not of the fist: expresses anything without fear — on social media, in "
        "writing, on a stage; debates with anyone.",
        "Skilled hands: fast typing, mobile games, magic tricks; multitasks with the hands.",
        "Good for writers, journalists, YouTubers, social-media managers, coders, copywriters and comedians; the mind "
        "is always making content; can become famous through writing. Small handwriting.",
        "The younger sibling is intelligent too; they fight like Tom and Jerry — with words — yet love each other.",
        "Short trips for business, learning and earning on the way.",
        "Very curious (how, why, what); cannot sit idle for five minutes; two or three hobbies (Mercury's duality); "
        "always holds a pen, a pencil or a book.",
    ],
    ("Mercury", 4): [
        "The home becomes a library, a school or a business centre — study, work and thinking all happen at home. A "
        "noisy home (phones, talk, children): they dislike a silent house.",
        "The mother is intelligent or talkative, a teacher or a businesswoman, who taught them how to talk and learn.",
        "The heart works like a calculator: decisions by analysis (profit or loss?), not by emotion — business-like, "
        "not cold.",
        "One of the best placements for education: toppers in maths, commerce and languages; may change stream "
        "(science to commerce, engineering to an MBA); likes a double degree.",
        "Buys property after heavy calculation, never on emotion; real estate suits them; often works from home or "
        "sells from home (sarees, jewellery).",
        "A small vehicle, chosen on mileage and features; talks, or listens to podcasts, while driving.",
    ],
    ("Mercury", 5): [
        "Falls in love with the way someone talks or jokes, not with looks; a love life of texting and shared jokes — "
        "calculated even in romance.",
        "Children talkative, toppers and funny; a mother with this placement talked a lot during her pregnancy, and "
        "her children learn fast.",
        "See Mercury in the 5th and you can say at once: super intelligent — logic, memory, puzzles, the share market, "
        "maths, astrology, writing jokes.",
        "The 5th is the mantra-sthāna: learns mantras quickly, and chants them after understanding their meaning, "
        "never blindly.",
        "Hobbies of the brain: chess, puzzles, games, creative writing.",
    ],
    ("Mercury", 6): [
        "A benefic is not comfortable in the 6th. Enemies are talkative, cunning people, not thugs; you beat them with "
        "arguments, proof and documents — court cases and debates are won.",
        "The best placement for a lawyer, an auditor or a debater; does well in competitive exams with logical "
        "questions (bank exams, CAT, UPSC).",
        "At work, the one who finds others' mistakes: the boss gives them others' work to check.",
        "Compares ten banks before taking a loan; keeps written proof when lending.",
        "Suits working under someone: accountant, customer support, data analyst, lawyer; for a doctor, a nurse "
        "specialist.",
    ],
    ("Mercury", 7): [
        "The spouse is young-looking, talkative, funny and slim; from a business family, or a teacher, a trader or in "
        "the media.",
        "Married after long talking and chatting (a long courtship), not for looks; a small age gap.",
        "A marriage of friendship: long talks, planning the household budget together — but too much logic and little "
        "romance.",
        "Quarrels are a cold war: silence or sarcastic messages, never shouting (Mars in the 7th fights openly).",
        "Needs a business partner, bored working alone; good with clients, marketing and sales; popular in business "
        "circles and on social media; may attract young partners.",
    ],
    ("Mercury", 8): [
        "Like a torch switched on in the darkest house: talks of hidden things — astrology, share-market secrets, "
        "psychology, crime stories — and reads between the lines.",
        "Suits a detective, data scientist, surgeon, hacker or spy, as well as an astrologer.",
        "Sudden money from insurance, shares or hidden sources — and it goes as suddenly.",
        "The in-laws are intelligent, talkative or in business.",
        "Cannot keep a secret: people confide in them, and they let it out by talking too much — learn to zip the "
        "mouth.",
        "Weak nerves: overthinking brings anxiety, sleeplessness, skin trouble, piles or nerve pains — meditation "
        "helps.",
        "Talks about death logically and without fear; a benefic in the 8th gives a long life.",
    ],
    ("Mercury", 9): [
        "Luck comes by speaking, writing and trading — not by sitting or praying; the more you teach, the luckier you "
        "become, so teach what you know.",
        "The father is young-looking and intelligent, a businessman, teacher or orator who taught them business; they "
        "argue (not fight) with him and question his wisdom; he may help in business or study.",
        "Good for a Master's, a PhD or a degree abroad; often two degrees.",
        "Reads even the Bhagavad Gītā for its logic; the guru is young, witty and intelligent, not a boring old bābā.",
        "Goes abroad for study or business, not tourism; talks easily with foreigners.",
    ],
    ("Mercury", 10): [
        "Not suited to physical work: a career of talking, writing, calculation and analysis — trader, YouTuber, "
        "marketing head, news anchor, lawyer, sales, content creator.",
        "A dual career; changes two or three jobs (an engineer turns businessman, a teacher a YouTuber).",
        "The 10th is the kīrti-sthāna: famous for their speech; the boss sends them to present to clients.",
        "The boss is intelligent, talkative and business-minded; they argue with the boss logically, and win.",
        "Their intelligence shows at work: in promotions, name and fame (her answer in class).",
    ],
    ("Mercury", 11): [
        "Friends are smart, young-looking, talkative business people who help them reach their goals.",
        "Income from two or three sources (a job, a business, teaching).",
        "Wishes come true through intelligence and a wide network.",
        "The elder sibling is intelligent or in business.",
        "Popular on social media and in online groups, with a big following.",
    ],
    ("Mercury", 12): [
        "Mercury, always calculating profit, is confused in the house of loss: not a comfortable house for it.",
        "The mind is on foreign lands — to study, earn, do business or lecture there, after much calculation; one of "
        "the best placements for business with foreign countries.",
        "Spends on phones, laptops, the latest gadgets, books and courses.",
        "Sleeps late, the mind racing with ideas or scrolling the phone; dreams a lot, and sometimes finds solutions "
        "in dreams.",
        "Treats even spirituality with logic and research; keeps a secret diary; needs time alone to read, write and "
        "think.",
    ],
    ("Jupiter", 1): [
        JUPITER_RULE,
        "A broad forehead, big eyes and a teacher's mature face — even the young are called \"uncle\"; fair, chubby, a "
        "bright face, a little overweight (Mercury in the 1st is lean, Jupiter chubby).",
        "A born adviser, who advises even unasked; everyone, even the father, comes to them for advice though they "
        "may be the youngest.",
        "Honest and optimistic (\"everything will be all right\").",
        "Luck chases them; money comes without much hard work; teacher, consultant, counsellor.",
        "One of the best placements: Jupiter in the 1st protects the whole chart — it is said to cancel a hundred "
        "doṣas.",
    ],
    ("Jupiter", 2): [
        "Born into a respected or rich family, or the family prospers after the birth (abhivṛddhi).",
        "Income from a family business, banking, teaching, or a gold or food business.",
        "Saves in gold and wears gold; gold is the lucky metal.",
        "Wise, weighty speech: when they speak, people listen; they speak like the head of the family though the "
        "youngest; a good voice, can sing; blesses people (\"God bless you\").",
        "A big, joint or religious family, of which they are the chief adviser.",
        "Loves sweets, ghee, home food and a full thālī; gains weight; loves feeding others.",
        _respect("your family"),
    ],
    ("Jupiter", 3): [
        "Not comfortable in the 3rd: no blind courage (that is Mars in the 3rd); thinks many times and uses wisdom "
        "before any venture.",
        "The younger siblings are lucky, rich and wise; you act as their guru — the bond may be distant, but they come "
        "to you for advice.",
        "A motivational writer; a YouTuber who gives wisdom (gyān); books and courses full of wisdom, not time-pass.",
        "Luck needs effort here: \"you have the knowledge, but must fight like a soldier to sell it\".",
        "Short trips to teach, for seminars, or on pilgrimage.",
        _respect("your siblings"),
    ],
    ("Jupiter", 4): [
        "A big vehicle, not a small one.",
        "The mother is wise and religious, fair and plump, from a respected family; she teaches dharma and guides.",
        "A big pūjā room with many pictures of God and scriptures; a peaceful home; own house, land from the family, "
        "vehicles.",
        "A clean heart: cannot cheat anyone; trusted by everyone; leaves revenge to God.",
        "The home is near a temple, a school or a religious place.",
        "Very good for education; likes to study at home; a peaceful mind and sound sleep; known in the area as the "
        "one who advises.",
    ],
    ("Jupiter", 5): [
        "One of the best placements: a trikoṇa and the house of learning, which Jupiter expands.",
        "Understands rather than mugs up: one reading makes the concept clear; scholarships and awards.",
        "The mantra-sthāna: mantras work fast for them (mantra siddhi).",
        "The first child is lucky and wise, perhaps a son (Jupiter is a male planet); prosperity comes after the "
        "child's birth; good, obedient children.",
        "The house of pūrva-puṇya: good deeds in a past life (donating to temples, helping Brahmins, teaching for "
        "free) — blessed in this one without much hard work.",
        "Falls in love with a wise, educated, committed person, and becomes their guide.",
        "A teacher with many students; lucky in the share market.",
        _respect("your children"),
    ],
    ("Jupiter", 6): [
        "Not comfortable in a duṣthāna, a house of fights: the guru dislikes fighting.",
        "The enemies are educated and powerful, not cheap people; you fight them with wisdom.",
        "Health: liver trouble, diabetes or thyroid, and weight gain from sweets and laziness — but recovery is fast, "
        "with a good doctor.",
        "Takes a loan for education; banks lend easily, as you look trustworthy.",
        "Respected at work, where colleagues come for advice; works in a bank, a school, a court or the government, "
        "or teaches.",
        "The maternal uncle is wise, rich, or like a guru.",
    ],
    ("Jupiter", 7): [
        "The spouse is wise and educated, fair, chubby and religious, mature or older-looking, from a good family — and "
        "teaches you in life.",
        "Luck grows after marriage.",
        "Not a very good placement for marriage: ego clashes (Jupiter's ego of knowledge) — but the marriage lasts; "
        "no divorce, out of regard for dharma and society; loyal.",
        "Wise, trustworthy business partners; the public loves them.",
        _respect("your spouse"),
    ],
    ("Jupiter", 8): [
        "Gurus of the occult, tantric gurus; ups and downs — rich one day, poor the next.",
        "Drawn to death, the afterlife and the secret of life (the 4th, 8th and 12th are the moksha trikoṇa).",
        "A benefic in the 8th gives a long life.",
        "Reads what others hide, as if reading their mind: a healer.",
        "The in-laws are rich or wise; wealth comes from the spouse's family.",
        "Liver, fat and diabetes; weight comes on easily. A fear of humiliation.",
    ],
    ("Jupiter", 9): [
        "Born lucky: luck follows them wherever they go.",
        "The father is a guru who teaches dharma, morals and ethics; wise and respected; good guidance from him.",
        "Dharmic from childhood: follows the rituals and traditions, goes to the temple unasked, reads the purāṇas.",
        "Goes abroad for a PhD or a Master's, or to spread dharma; earns by teaching, preaching, or in a temple or "
        "university — clean money; donates a lot.",
        "Famous as a guru, professor, judge, IAS officer or temple priest, or a politician with a clean image.",
        "If they question everything and are not religious, see Jupiter's sign and aspects and read the whole chart "
        "(her answer in class).",
        _respect("your father and your guru"),
    ],
    ("Jupiter", 10): [
        "Thinks big: wants the big post — head of department, principal, judge, manager, business owner — and gets it "
        "through wisdom.",
        "The boss is a wise father figure; they will not work under a cheap boss.",
        "A clean, honest public image, even in politics; works for respect, not money; the office's guru, with a big "
        "cabin.",
        "Burdened with responsibility: they solve everybody's problems.",
        _respect("your boss and your father"),
    ],
    ("Jupiter", 11): [
        "Money from many sources (a salary, a side business, teaching, rent); earns more than the father; gains "
        "through the network.",
        "The friends are wise and educated; the elder sibling is wise or rich, a helper and guide.",
        "Wishes come true: a house, a car, a foreign trip.",
        "Good for big business; a teacher with many students; a social-media influencer.",
    ],
    ("Jupiter", 12): [
        "A moksha guru: money goes to good causes — temples, charity, the guru; saving is hard, but what is given "
        "comes back.",
        "May live abroad, and become a guru there; luckier or richer in a foreign land; spends time in āśrams; helps "
        "build āśrams or hospitals.",
        "A big, comfortable bed, and sleeps like a king; spiritual dreams.",
        "Knows life is temporary and seeks the truth or God; spirituality after 40; gives most things away late in "
        "life.",
        "Hidden enemies are wise too: forgive them.",
        "The feet: pain or swelling (from weight).",
    ],
}

# (planet, house) -> her points for a weak planet in that house
IF_WEAK = {
    ("Mercury", 1): ["Much talk and little action."],
    ("Mercury", 2): ["May stammer, the speech not fluent; bad food habits, such as talking on the phone while eating."],
    ("Mercury", 3): ["Gossip, sibling rivalry, shaky (nervous) hands, overthinking."],
    ("Mercury", 4): ["The mother's health (nerves, skin); arguments with the mother; no peace at home."],
    ("Mercury", 5): ["Too much talking, dating two people at once, nervous and skin trouble."],
    ("Mercury", 6): ["Lies to win; office gossip; trouble from the maternal uncle; cheated through documents — read "
                     "before you sign."],
    ("Mercury", 8): ["The in-laws feel you are cunning; cheated by clever friends."],
    ("Mercury", 11): ["Friends may cheat with money or documents; friendship made for profit."],
    ("Mercury", 12): ["Cheated in a foreign country; hospital spending for nervous problems."],
    ("Jupiter", 6): ["Diabetes and health trouble, huge loans, lost court cases; the maternal uncle may cheat."],
    ("Jupiter", 10): ["No promotion, insulted by the boss; famous but poor; a \"fake guru\" who lectures but does not "
                      "work."],
    ("Jupiter", 11): ["Greedy, never satisfied; fake friends who come for money; earnings without happiness."],
    ("Jupiter", 12): ["Big hospital bills, trouble walking, isolation or illness."],
}

# (planet, house) -> her points for a strong planet in that house
IF_STRONG = {
    ("Mercury", 5): ["Can become a famous writer, or a teacher popular with the students."],
    ("Mercury", 10): ["Their own business, name and fame; two or three businesses at once."],
    ("Jupiter", 1): ["A very good teacher, consultant or counsellor."],
    ("Jupiter", 6): ["Wins over every enemy, court case and competition; a good doctor, lawyer or bank manager; clears "
                     "every loan — Jupiter protects."],
    ("Jupiter", 10): ["A principal, judge, minister, big business owner or CEO; very famous."],
}

# (topic, text, houses, source) — S23_Remedies. houses []: a general remedy for the planet.
REMEDIES = [
    ("Mercury", "Help poor children with their education (her universal Mercury remedy).", [], SOURCE),
    ("Mercury", "Never use bad words or abuse anyone, and never tell lies: a lie lessens your wealth.", [2], SOURCE),
    ("Mercury", "Keep a picture of Sarasvatī on your desk.", [2], SOURCE),
    ("Mercury", "Donate books and stationery to poor people on Wednesdays.", [2], SOURCE),
    ("Mercury", "Don't gossip and don't abuse; if your maternal uncle is in trouble, help him.", [6], SOURCE),
    ("Mercury", "If Mercury is weak: feed green fodder to cows on Wednesdays.", [6], SOURCE),
    ("Mercury", "Never commit fraud with documents, and keep any secret told to you.", [8], SOURCE),
    ("Mercury", "Never mock or misuse occult knowledge.", [8], SOURCE),
    ("Mercury", "Donate stationery, or for a poor child's education.", [8], SOURCE),
    ("Mercury", "Never cheat anyone — it keeps the business stable; respect your boss, and don't be over-smart.",
     [10], SOURCE),
    ("Mercury", "Never cheat your friends; help poor children with their education.", [11], SOURCE),
    ("Mercury", "Sleeplessness comes from overthinking: keep off the phone for long, and meditate before sleep.",
     [12], SOURCE),
    ("Jupiter", "Never gamble, and keep no secret life: keep your life clean.", [8], SOURCE),
    ("Jupiter", "If Jupiter is weak, don't take your in-laws' money (if they give it willingly, you may take it).",
     [8], SOURCE),
    ("Jupiter", "Do Śiva pūjā, and control your weight.", [8], SOURCE),
    ("Jupiter", "Help others at their last rites, or guide others with your wisdom.", [8], SOURCE),
    ("Jupiter", "If Jupiter is weak: touch your father's or your guru's feet daily for their blessings — it opens your "
                "luck; never insult them.", [9], SOURCE),
    ("Jupiter", "Go to the temple daily and follow your dharma.", [9], SOURCE),
    ("Jupiter", "Respect your father and your boss; do the work given to you honestly; take no bribe.", [10], SOURCE),
    ("Jupiter", "Feed Brahmins on Thursdays.", [10], SOURCE),
    ("Jupiter", "Give a part of your profit to charity; help your elder brother or sister.", [11], SOURCE),
    ("Jupiter", "Never cheat your friends, and choose them wisely.", [11], SOURCE),
    ("Jupiter", "Feed the poor, donate at a temple, and help at a hospital.", [12], SOURCE),
    ("Jupiter", "Don't spend for show — spend wisely; take care of your feet.", [12], SOURCE),
    ("Kuja", "For a child with Kuja doṣa: the child does the remedy themselves — as whoever is ill takes the medicine — "
             "for example a visit to a Subrahmaṇya temple, or a small prayer.", [], SOURCE),
]
