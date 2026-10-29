"""The class of 22 Oct 2026 (Session 24): the Moon and Mars in the 12 bhāvas, her Mars remedy, her Q&A.

Her slide text for these 24 placements is already in session23_teacher_slides.py (deck S23-2024, pp. 3-31). These are
the points she added in class that the slides do not make, written from the recording as the Sun's Session 23 points
were; they show on the page as "From the recording". Her examples from real charts are labelled "Her example".

The remedies: she gave the Mars remedy for Mars in the 8th ("irrespective of the planet with Mars"), said the 2nd and
the 12th take the same, and gave the Kuja rows for Kuja doṣa (Mars in the 7th); "otherwise it is not required".
The "Mars" rows carry that rule in their Houses (2, 7, 8, 12; S23_Remedies, class of 29 Oct); the "Kuja" rows show only in the page's Kuja Doṣa
section, when the doṣa is present and not cancelled (the user's ruling of 23 Oct 2026). The three Moon rows are her
answer for an emotional mind.

apply_teacher_slides.apply_s24_class() turns these into the S23_ rows of session23_rules.json.
"""

SOURCE = "Class 22 Oct 2026"

# (planet, house) -> the points from the recording (the `extra` list of that S23_GrahaInBhava row)
GRAHA_IN_BHAVA_EXTRA = {
    ("Moon", 1): [
        "Wherever the Moon sits, the mind dwells on that area of life: doing that house's activities brings emotional "
        "satisfaction, and one seeks emotional support from the person the house stands for.",
        "A round, bright face and a fair complexion; a motherly, baby-like face; watery eyes; stout rather than tall.",
        "Finds it hard to make a choice and keeps changing their mind, as the Moon waxes and wanes; moods and "
        "confidence go up and down.",
        "The Moon's portfolio is the queen: good at administration, at getting work done through others and at "
        "managing people; nurturing and caring towards those around them.",
        "Likes to stay in the shade rather than go out in the sun; loves travelling; prefers an easy-going life.",
        "An expressive face: what they feel shows on it without a word.",
        "A strong Moon gives a calm mind and a good memory; a weak, debilitated or afflicted Moon gives a restless, "
        "agitated, confused mind that panics quickly and can tend to depression.",
    ],
    ("Moon", 2): [
        "A soft, sweet voice whose tone and volume vary; if the Moon is afflicted they may stammer or speak very fast.",
        "A foodie: rice, milk, curd, ghee and other dairy, juices and liquids; tends to add extra salt; finds fasting "
        "hard.",
        "Talkative, with a charming personality; dislikes arguments.",
        "Looks to the family for emotional security: after a stressful day they want time and a meal with the family; "
        "the mother is given great importance.",
        "The 2nd is also the eyes: some trouble with the eyes is possible.",
    ],
    ("Moon", 3): [
        "Their feelings come out through writing, speaking or creative hobbies; always keen to learn new skills and "
        "exchange ideas.",
        "Look to the younger siblings for emotional support.",
        "When anything happens they immediately want to tell someone close: communicating is how they find balance.",
    ],
    ("Moon", 4): [
        "Home is their comfort: even after a wonderful holiday they feel at peace only on returning home.",
        "Being near water, rivers or the sea, gives them emotional stability.",
    ],
    ("Moon", 5): [
        "Drawn to the arts, singing, dancing and acting, and to music and storytelling; very imaginative.",
        "Depend on their children for emotional security; feel immense joy watching them learn or create something.",
    ],
    ("Moon", 6): [
        "Care for the underprivileged and for animals; motivated to help others solve their problems.",
        "The daily routine and its responsibilities affect their emotional well-being.",
        "The 6th is also the maternal uncle, and the Moon here describes him. Her example: an uncle who travels a lot, "
        "a foodie fond of dairy and, the Moon being in Tulā, a business sign, a successful businessman.",
    ],
    ("Moon", 7): [
        "The spouse is caring and nurturing (her example: a very good cook, very adjusting); they seek emotional "
        "support from the spouse.",
        "Her example: the Moon in Tulā in the 7th gave a rice and dairy business and farming, and a love of giving "
        "food to others (anna dāna).",
    ],
    ("Moon", 8): [
        "Interested in psychology and mysteries: mystery films and novels.",
        "Keep their life private; research everything and never accept things at face value.",
    ],
    ("Moon", 9): [
        "Emotionally connected to the father or the guru, and seek support from them.",
        "Teachers and mentors shape their life; travel and higher studies broaden their outlook.",
    ],
    ("Moon", 10): [
        "Professions connected to food, water or dairy, or psychology, suit them.",
        "Work moves their mood: appreciation at work lifts it at once.",
        "Her example: the Moon in a dual sign in the 10th gave much travel for work, a rice business, ups and downs "
        "and several changes of profession.",
    ],
    ("Moon", 11): [
        "Seek emotional support from friends or the elder sibling; happiest with friends; group activities fulfil "
        "them; they celebrate every success with friends.",
        "If the Moon is afflicted (her example: with Rāhu in the 11th) there may be misunderstandings with the elder "
        "sibling instead.",
    ],
    ("Moon", 12): [
        "Spiritual and happiest alone; solitude, retreats, an āśram or meditation rejuvenate them: after a busy day "
        "they switch off and relax by themselves.",
        "Often like to settle abroad; mentally happier away from their birthplace.",
        "May spend on the mother, on spirituality, or on things that engage the mind.",
    ],
    ("Mars", 1): [
        "Wherever Mars sits is where one spends one's energy; Mars is the soldier who protects the person or thing of "
        "that house.",
        "May be soft inside but looks aggressive; fit and athletic like a soldier; often a scar on the face.",
        "Bold, competitive, never gives up; takes the first initiative (in a group project the first to say \"I'll do "
        "this\").",
        "Stubborn, with some anger issues; dominating yet protective of the family and the spouse.",
    ],
    ("Mars", 2): [
        "A commanding speech, like an army commander giving orders; direct, forceful and sharp, harsh when angry.",
        "Non-vegetarian food (Mars is a Kṣatriya); if vegetarian, spicy food; wants food served hot.",
        "A strict, disciplined family environment; may quarrel within the family but defends it, its traditions and "
        "values fiercely before outsiders.",
    ],
    ("Mars", 3): [
        "A good position: the 3rd is an Upachaya, where malefics do well. Strong will, self-effort and the courage to "
        "start new ventures make good entrepreneurs; the first to take up a difficult task when others hold back.",
        "Writing is direct and to the point: revolutionary (krāntikārī) writing that fires others up.",
        "Rivalry or disputes with siblings, yet protects the younger sibling before others.",
        "Great at starting things, but interest can fade before the finish; being aware of it helps.",
    ],
    ("Mars", 4): [
        "Treats the home as their territory and protects the home, mother, family, property and vehicles.",
        "Likes rugged, powerful, fast vehicles (a Thar, a Jeep, a Bullet) and off-roading.",
        "Needs adventure and physical activity, such as trekking, for peace of mind; impatient and dominating at home.",
        "A natural interest in acquiring land and buildings.",
    ],
    ("Mars", 5): [
        "Not very romantic: no interest in candle-light dinners and outings.",
        "Prefers technical education such as engineering; treats studies as a race for marks.",
        "Lays down rules for the children; should cultivate patience with them.",
    ],
    ("Mars", 6): [
        "If Mars is not well placed: disputes and poor relations with colleagues, a tense workplace.",
        "In a crisis at work, when everyone panics, they take it up and find a solution.",
    ],
    ("Mars", 7): [
        "The spouse is energetic, bold and courageous; an intense, open and direct relationship.",
        "Ego clashes, dominance and disputes in married life: one wants to settle calmly, the other wants to fight. "
        "Protects the spouse and the partners. Mars in the 7th is Kuja doṣa (Mangalik).",
    ],
    ("Mars", 8): [
        "The courage to investigate hidden subjects and mysteries; good in crisis management and technical "
        "investigation.",
        "Health issues, accidents and surgeries are common; quarrels with in-laws are possible. A difficult position "
        "that takes her Mars remedies.",
    ],
    ("Mars", 9): [
        "Defends their principles and values strongly; may argue or differ with the father as well as the guru.",
        "Interested in higher learning.",
    ],
    ("Mars", 10): [
        "The profession is where their energy goes: ambitious, a leader with a strong work ethic; knows exactly what "
        "they want and gets it; dominating and seeks authority.",
        "Fast to act: while others are still planning, they have formed the team and started.",
    ],
    ("Mars", 11): [
        "Takes the initiative in the friend circle and organises big gatherings, though there can be arguments or "
        "competition with friends.",
        "All their energy goes into their gains and goals.",
    ],
    ("Mars", 12): [
        "Spends on gyms and equipment to build the body (Mars is also the bodybuilder).",
        "Practises a skill for hours alone, mastering it without an audience; channels energy into foreign "
        "environments or solitary practice.",
        "Kuja doṣa comes from Mars's position, not its aspect: Mars in the 12th is Mangalik because of where it sits "
        "(the slide's reason, its aspect on the 7th, does not make the doṣa).",
    ],
}

# (topic, text, source) — S23_Remedies. Moon: her answer for an emotional mind; Mars: for Mars in the 2nd, 7th, 8th or
# 12th; Kuja: added for Kuja doṣa (shown in the Kuja Doṣa section when the doṣa is present and not cancelled).
REMEDIES = [
    ("Moon", "For an emotional mind: write down whatever you feel in a book.", SOURCE),
    ("Moon", "For an emotional mind: meditate, even for five minutes.", SOURCE),
    ("Moon", "For an emotional mind: chant \"Hare Rāma Hare Rāma, Rāma Rāma Hare Hare, Hare Kṛṣṇa Hare Kṛṣṇa, Kṛṣṇa "
             "Kṛṣṇa Hare Hare\" 108 times.", SOURCE),
    ("Mars", "Read the Hanuman Chālīsā every day, or at least on Tuesdays.", SOURCE),
    ("Mars", "Visit a Hanumān temple on Tuesdays and offer sindoor.", SOURCE),
    ("Mars", "Donate blood once every six months or a year, if your health permits: better to give blood willingly "
             "than to lose it in an accident or a surgery.", SOURCE),
    ("Mars", "Avoid non-vegetarian food, alcohol and very spicy food; drink more water to cool Mars's energy.", SOURCE),
    ("Mars", "Do not quarrel with your younger brother.", SOURCE),
    ("Mars", "Chant \"Om Aṅgārakāya Namaḥ\" or \"Om Hanumate Namaḥ\" 108 times on Tuesdays, or the Mars verse of the "
             "Navagraha Stotram (\"Dharaṇī garbha sambhūtaṁ…\").", SOURCE),
    ("Mars", "Keep your anger under control.", SOURCE),
    ("Kuja", "For Kuja doṣa: donate toor dāl tied in a red cloth to the priest at the temple.", SOURCE),
    ("Kuja", "For Kuja doṣa: visit a Lord Subrahmaṇya temple.", SOURCE),
]
