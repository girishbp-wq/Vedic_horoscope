"""Curated graha–graha text (conjunction and aspect) for the 35 pairs the teacher has not yet covered.

Mercury + Jupiter is taught (slide 26 and the recording) and lives in session23_rule_data.TAUGHT_PAIRS.
Each text blends the two grahas' KARAKATWAS entries (qualities, signifies) and PLANET_PROFILE nature,
phrased as tendencies.  Pairs are unordered, stored with a before b in Sun … Ketu order; the same text is
shown whichever planet casts the aspect.  Every row is tagged `curated`.
"""

ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

DATA = {
    ("Sun", "Moon"): (
        "The Sun is the soul, authority and the father; the Moon is the mind, emotion and the mother. Together the will and the feelings work as one: purposeful and self-aware, though close to the new moon the mind can be dominated by ego and may struggle to see other views.",
        "When the Sun and Moon look at each other, the soul and the mind are in dialogue: confidence and sensitivity balance each other, and the relation between the father and mother plays a visible role in the person's life."),
    ("Sun", "Mars"): (
        "The Sun is authority and ego; Mars is energy, courage and aggression. Together they give a bold, driven and competitive nature, good for leadership, defence, surgery or engineering, but anger, pride and heat (blood pressure, inflammation) need watching.",
        "When the Sun and Mars look at each other, drive and willpower reinforce one another; the person acts with confidence, and conflicts with authority figures or siblings need a cool head."),
    ("Sun", "Mercury"): (
        "The Sun is authority and the soul; Mercury is intellect, speech and business. Together they give a sharp, authoritative mind — good for administration, teaching, writing and government work — though the close conjunction is called combustion and can dim Mercury's expression.",
        "When the Sun and Mercury look at each other, the intellect is lit by self-confidence; the person speaks with authority and values knowledge, though it can sound self-assured."),
    ("Sun", "Jupiter"): (
        "The Sun is authority, the father and the soul; Jupiter is wisdom, nobility and the guru. Together they give an ethical, dignified, respected person, suited to teaching, counselling, law and public office, with natural leadership and faith.",
        "When the Sun and Jupiter look at each other, wisdom supports authority: the person is guided by principles, gets help from teachers and elders, and fortune improves through merit."),
    ("Sun", "Venus"): (
        "The Sun is ego and authority; Venus is refinement, charm and comfort. Together they give a dignified, artistic and attractive personality, but Venus is easily overshadowed by the Sun's heat, so relationships and pleasures may take second place to ambition.",
        "When the Sun and Venus look at each other, authority and charm interact: the person likes a refined lifestyle, though ego can colour relationships and the spouse may be strong-minded."),
    ("Sun", "Saturn"): (
        "The Sun is authority, the father and ego; Saturn is discipline, delay and hard work. Being natural enemies, they can bring tension between ego and duty, or between father and son, and a hard-won, late-maturing success.",
        "When the Sun and Saturn look at each other, willpower meets restraint: there is struggle and delay, but it matures into responsibility, perseverance and respect over time."),
    ("Sun", "Rahu"): (
        "The Sun is the soul and authority; Rahu is obsession and amplification. Together ego can swell, and the person may seek status, power or recognition with intensity; the father's influence may be unusual. This asks for humility.",
        "When the Sun and Rahu look at each other, ambition and illusion mingle: there is a pull towards unconventional paths and recognition, with the need to guard against ego and confusion about identity."),
    ("Sun", "Ketu"): (
        "The Sun is the soul and ego; Ketu is detachment and spirituality. Together the sense of self is turned inward: the person may be introspective, spiritual or indifferent to status, and the relationship with the father may be distant.",
        "When the Sun and Ketu look at each other, ego meets detachment: the person questions identity and authority, and may find purpose in spiritual or research pursuits."),
    ("Moon", "Mars"): (
        "The Moon is the mind and emotion; Mars is energy and courage. Together feelings turn into action: a passionate, courageous, quick-tempered mind; good for property, real estate and energetic work. It favours earning, though moods and impulsiveness need steadying.",
        "When the Moon and Mars look at each other, emotion and drive influence one another: the person acts on feelings, can be enterprising and short-tempered, and the mother and younger siblings play an active role."),
    ("Moon", "Mercury"): (
        "The Moon is emotion and the mind; Mercury is intellect and communication. Together they give a quick, imaginative, communicative mind with a gift for writing, trading and learning, though it can be restless and over-thinking.",
        "When the Moon and Mercury look at each other, feeling and reasoning work together: the person is a sensitive communicator, adaptable, curious and inventive."),
    ("Moon", "Jupiter"): (
        "The Moon is the mind and nurture; Jupiter is wisdom and good fortune. Together they give a kind, optimistic, generous mind — which favours respect, wisdom, family happiness and prosperity.",
        "When the Moon and Jupiter look at each other, the mind is blessed with wisdom and optimism; the person is respected, calm and supported by teachers and family."),
    ("Moon", "Venus"): (
        "The Moon is emotion and the mother; Venus is charm, love and comfort. Together they give a loving, artistic, pleasure-seeking nature with a taste for music, beauty and comfort; relationships with women are important, and excess indulgence is the caution.",
        "When the Moon and Venus look at each other, feeling and charm blend: the person is affectionate, tasteful and sociable, with warm family bonds."),
    ("Moon", "Saturn"): (
        "The Moon is the mind and emotion; Saturn is delay, discipline and detachment. Together they bring a serious, reserved, worry-prone mind; emotional heaviness and a hard early life can mature into patience and resilience.",
        "When the Moon and Saturn look at each other, the mind is tested by restraint: caution, worry and isolation are possible, but so are discipline, endurance and depth."),
    ("Moon", "Rahu"): (
        "The Moon is the mind; Rahu is obsession and illusion. Together they can amplify emotions, anxieties and fears and bring an unconventional mind, a pull towards foreign matters and mental restlessness; steadiness and meditation help.",
        "When the Moon and Rahu look at each other, the mind is stirred by desire and imagination; vivid dreams, anxieties and unusual attractions are possible, and the mother's influence may be unconventional."),
    ("Moon", "Ketu"): (
        "The Moon is emotion and the mother; Ketu is detachment and mysticism. Together they give an intuitive, spiritual and withdrawn mind that can find the emotional world confusing; sudden emotional severances and sensitivity are possible.",
        "When the Moon and Ketu look at each other, feelings are tinged with detachment: intuition and psychic sensitivity are high, with moods that are hard to explain."),
    ("Mars", "Mercury"): (
        "Mars is energy and aggression; Mercury is intellect and speech. Together they give a sharp, quick, argumentative mind — good for debate, engineering, technical work and sales — but words can turn harsh and nerves can be strained.",
        "When Mars and Mercury look at each other, the intellect is spurred by energy: the person is quick-witted and direct, though impatient and sometimes sharp-tongued."),
    ("Mars", "Jupiter"): (
        "Mars is courage and action; Jupiter is wisdom and expansion. Together action is guided by principle: a brave, ethical, enterprising person, good for law, administration, defence and teaching.",
        "When Mars and Jupiter look at each other, energy meets wisdom: the person acts with purpose and optimism, and effort is rewarded when it follows dharma."),
    ("Mars", "Venus"): (
        "Mars is passion and aggression; Venus is love and refinement. Together they give a passionate, energetic, romantic nature, artistic drive and attraction to the opposite sex; desires are strong and the relationship needs balance.",
        "When Mars and Venus look at each other, energy and desire interact: the person is magnetic and passionate, with creative drive and a lively romantic life."),
    ("Mars", "Saturn"): (
        "Mars is energy and impulse; Saturn is delay and discipline. Together they bring friction — drive held back by restraint — which can build endurance and technical skill but also frustration, accidents and harshness.",
        "When Mars and Saturn look at each other, impulse meets caution: there are tests of patience, delays and tensions, and the result can be sustained, disciplined effort."),
    ("Mars", "Rahu"): (
        "Mars is courage and aggression; Rahu is obsession and amplification. Together they intensify anger, risk-taking and ambition; the person is daring and unconventional but prone to impulse, accidents and conflict.",
        "When Mars and Rahu look at each other, aggression and obsession feed each other: bold, risk-taking energy, with the need to guard against accidents, anger and rash decisions."),
    ("Mars", "Ketu"): (
        "Mars is courage and action; Ketu is detachment and severance. Together the courage can turn into fearless, sharp, sometimes reckless action, and interest in surgery, spiritual discipline or martial work; sudden cuts, injuries and quarrels need care.",
        "When Mars and Ketu look at each other, energy meets detachment: the person can be fearless and indifferent to consequences; channelled well, it becomes spiritual discipline."),
    ("Mercury", "Venus"): (
        "Mercury is intellect, speech and business; Venus is charm and the arts. Together they give a witty, artistic, charming communicator with talent in design, writing, music, fashion and trade; friendly and pleasing manners.",
        "When Mercury and Venus look at each other, intellect and charm blend: the person is sociable, creative and persuasive, with taste in language and the arts."),
    ("Mercury", "Saturn"): (
        "Mercury is intellect and speech; Saturn is discipline and delay. Together they give a serious, methodical, analytical mind with skill in accounts, research and technical work; speech is measured, and worry or nervous strain can build.",
        "When Mercury and Saturn look at each other, the intellect is steadied by discipline: careful, practical thinking and good concentration, with a tendency to over-think."),
    ("Mercury", "Rahu"): (
        "Mercury is intellect and communication; Rahu is amplification and unconventionality. Together they give a clever, inventive mind with talent for technology, media and foreign languages; it can also be restless, cunning or confused.",
        "When Mercury and Rahu look at each other, thinking is stirred by novelty and ambition: smart, tech-minded and persuasive, with the need to guard against exaggeration and deceit."),
    ("Mercury", "Ketu"): (
        "Mercury is intellect and speech; Ketu is detachment and mysticism. Together they give an intuitive, research-oriented mind with an interest in astrology, mathematics and spirituality; speech can be brief and the mind withdrawn.",
        "When Mercury and Ketu look at each other, logic meets intuition: sudden insights and an analytical bent for hidden subjects, with a tendency to isolation of thought."),
    ("Jupiter", "Venus"): (
        "Jupiter is wisdom and the guru; Venus is charm and refinement. Being the two great benefics, they combine knowledge and culture: a refined, prosperous, generous nature with artistic and spiritual sense; moderation guards against indulgence.",
        "When Jupiter and Venus look at each other, wisdom and charm support one another: harmonious relationships, comfort, good teachers and an appreciation of culture."),
    ("Jupiter", "Saturn"): (
        "Jupiter is wisdom and expansion; Saturn is discipline and restraint. Together they balance growth and caution, giving a practical, wise and patient person who builds slowly and steadily; delays are followed by lasting success.",
        "When Jupiter and Saturn look at each other, expansion meets structure: sound judgement, responsibility and a methodical path to wisdom and security."),
    ("Jupiter", "Rahu"): (
        "Jupiter is wisdom and the guru; Rahu is obsession and unconventionality. Together they can give an unorthodox or foreign-influenced path of belief, big ambitions and doubt about teachers; ethics need care.",
        "When Jupiter and Rahu look at each other, wisdom meets amplification: an adventurous, boundary-pushing mind, with the need to guard against exaggeration and misplaced faith."),
    ("Jupiter", "Ketu"): (
        "Jupiter is wisdom; Ketu is detachment and moksha. Together they give a spiritual, philosophical mind with an interest in mysticism, meditation and the inner life; worldly ambition may be low.",
        "When Jupiter and Ketu look at each other, wisdom is turned inward: intuition, spiritual insight and detachment from rituals or conventional teachers."),
    ("Venus", "Saturn"): (
        "Venus is charm, love and comfort; Saturn is discipline and delay. Together they give a serious, loyal and mature approach to love and the arts; relationships can be delayed or cooler, but are lasting, and discipline improves artistic work.",
        "When Venus and Saturn look at each other, pleasure meets restraint: delays or sobriety in love and comfort, with steady commitment and craftsmanship."),
    ("Venus", "Rahu"): (
        "Venus is love and luxury; Rahu is obsession and amplification. Together desires for pleasure, status and glamour are magnified: an unconventional, magnetic romantic life, interest in fashion, media and foreign culture, with a tendency to overindulge.",
        "When Venus and Rahu look at each other, charm and obsession combine: strong attractions, ambition in the arts and a pull towards luxury, with care needed in relationships."),
    ("Venus", "Ketu"): (
        "Venus is love and comfort; Ketu is detachment. Together the pleasure drive is turned towards the spiritual: refined taste with disinterest in worldly comfort, and relationships that carry a past-life or karmic tone.",
        "When Venus and Ketu look at each other, love meets detachment: a spiritual, introspective approach to relationships, with sudden changes in love life possible."),
    ("Saturn", "Rahu"): (
        "Saturn is discipline and delay; Rahu is obsession and amplification. Together they intensify worry, ambition and the drive for worldly success through hard work; the person can be driven, unconventional and burdened by fears.",
        "When Saturn and Rahu look at each other, restraint meets obsession: heavy responsibilities and anxieties, with great determination and the need for patient, ethical effort."),
    ("Saturn", "Ketu"): (
        "Saturn is discipline and detachment; Ketu is mysticism and severance. Together they give a deeply austere, spiritual and reserved temperament, interested in solitude and renunciation; coldness and isolation are the caution.",
        "When Saturn and Ketu look at each other, detachment is doubled: a serious, solitary and philosophical bent, with endurance and an interest in karma and moksha."),
    ("Rahu", "Ketu"): (
        "Rahu and Ketu are always 180° apart, so they never occupy the same sign; the nodal axis itself is the pairing — worldly desire on one end and detachment on the other.",
        "Rahu and Ketu sit opposite each other on one axis: the houses they occupy pull between obsession and release, and the life themes in those two houses are tied together in this life."),
}


def rows():
    """35 curated pair rows in Sun … Ketu order, excluding the taught Mercury + Jupiter."""
    out = []
    for i, a in enumerate(ORDER):
        for b in ORDER[i + 1:]:
            if (a, b) == ("Mercury", "Jupiter"):
                continue
            conj, asp = DATA[(a, b)]
            out.append({"a": a, "b": b, "conjunction": conj, "aspect": asp, "status": "curated",
                        "source": f"KARAKATWAS[{a}, {b}: qualities, signifies] + PLANET_PROFILE[{a}, {b}: Nature]"})
    return out
