"""The teacher's texts from Sessions 23 (2024 deck) to 27, as printed on her slides.

Transcribed from the PDFs (S23-2024, S24, S25, S26, S27) and checked against the page images. Sources cite the deck
and page. Edits made to the printed text, and nothing else:
- spaces before ',' and '.' closed up, and a space added after them where two words ran together;
  the slide's line breaks inside a sentence joined;
- misspellings whose meaning is unambiguous corrected (old -> new):
    absession -> obsession
    atleast -> at least
    beggers -> beggars
    Capricom -> Capricorn
    certificute -> certificate
    competetive -> competitive
    Concious -> Conscious
    continously -> continuously
    diseasen -> diseases
    eamings -> earnings
    enemity -> enmity
    enterpreneur -> entrepreneur
    expenditeres -> expenditures
    Gunu -> Guru
    imakes -> makes
    Kerata -> Kerala
    leamed -> learned
    leam -> learn
    Mindedpeople -> Minded people
    overalll -> overall
    prelateships -> relationships
    relatioship -> relationship
    spendtheft -> spendthrift
    sujects -> subjects
    ther -> their
    whichJupiter -> which Jupiter
    ger -> get
    lIteral -> literal
    Le 12th -> i.e. 12th
    teachers,s -> teachers
    Antanasha -> Antardasha
    funs -> fun
    Rule-(a) fixes (old -> new); the notes write these marks as "[sic, = X]":
    alignment -> ailment (S25 p.2, Saturn 1)
    or -> of (S25 p.14, Saturn 10)
    Irtigations -> litigations (S25 p.23, Rahu 6)
    er -> never (S25 p.24, Rahu 7)
    Rule (a) edits (old → new):
    S26 p.4: chidhood → childhood
    S26 p.8: duathana → dusthana
    Rule (d) edits, R11 generalisation (old → new):
    S26 p.3: Mars a malefic in lagna, whenever a malefic is in lagna lot of struggle → Whenever a malefic is in lagna lot of struggle
    S26 p.4: Jupiter a benefic is posited in the 2 nd house,this indicates that this persons early childhood → A benefic in the 2nd house indicates that this persons early childhood
    Other edits made on instruction (old → new):
    S26 p.23: , but if lagnalord is strong he will be able to overcome the diseases and other obstacles. → If lagnalord is strong he will be able to overcome the diseases and other obstacles. (strong row; the main row keeps "He may have chronic health problems.")
    S27 p.2: Jupiters 5 th aspect indicates your punya or good deeds of previous life times and the 9 th aspect indicates luck. → Jupiters 5 th aspect indicates your punya or good deeds of previous life times / The 9 th aspect indicates luck.
    S27 p.24: ( partnership business ) → Partnership business.
- Session 26 rule (R11): a house rule told through an example planet starts as a general rule
  (see the S26 lines above);
- conditional sentences (they hold only for some charts) moved from the planet-in-house text to CONDITIONS.

apply_teacher_slides.py turns these into the S23_ rows of session23_rules.json.
"""

# ---- Planet in each house (S23-2024 pp.3-44, S24 pp.2-37, S25 pp.2-41): (planet, house) -> (source, text)

GRAHA_IN_BHAVA = {
    ('Moon', 1): ('S23-2024 pp.3-4',
        ('Moon represents Mind, Emotions, Mother, Peace of Mind, Home Environment, Water, Milk etc.\n'
         '\n'
         '1st house/Ascendant is your self, personality, overall health, life path etc.\n'
         '\n'
         'So when Moon comes into 1st house, it means your mind is upon yourself. These people can be all about themselves. They constantly think about their own gains, benefits and benefits of their near and dear ones. In one sentence, they can be insensitive towards other people. At times, these people can become self-centered This positions generally gives a person very selfish approach to life.\n'
         '\n'
         'Now, as Moon also represents Mother, their Mother plays a very important role in their life. Now, this role can be positive as well as negative, but Mother remains the driving force\n'
         '\n'
         'As Moon represents emotions and from 1st house Moon aspects the 7th house of spouse, they seek emotional nourishment from others.\n'
         '\n'
         'A position where someone should take care that he/she should not become self-centred\n'
         '\n'
         'Will be on the heavier side / overweight\n'
         'Will be fair and attractive\n'
         'Will be very feminine looking\n'
         'Very soft body\n'
         'Very emotional and sensitive\n'
         'Caring nature\n'
         'Fickle minded')),
    ('Moon', 2): ('S23-2024 p.5',
        ('2nd house represents Family, Wealth, Speech, Family Lineage, Values, Mouth, Throat, food you like to eat. Assets etc.\n'
         '\n'
         'So, 1st of all Moon is emotions and 2nd house is house of family and family lineage. So, these people are emotionally attached with their family and family traditions. They are also attached with wealth and assets.\n'
         '\n'
         'As Moon also represents Mother, Mother becomes an important person in family. She is the one who who is running the family\n'
         '\n'
         'As it is also a house of family assets and wealth and Moon goes through tides of waxing and waning these people go through lots of ups and downs in life with respect to wealth. But if Moon is in earth signs (Taurus, Virgo or Capricorn) then Moon finds stability of earth and this person may feel stability as per wealth and assets they may have\n'
         '\n'
         '2nd house is also a house of mouth and throat in human body, and Moon is a sensual benefic planet\n'
         '\n'
         'These people become very good singers Best example Lata Mangeshkar')),
    ('Moon', 3): ('S23-2024 p.7',
        ('3rd house-It is house of your communication skills, neighbours, short distance travels, younger siblings, marketing, announcements, collecting information, hobbies and skills, self-efforts, business, courage etc.\n'
         '\n'
         'So, when Moon comes into 3rd house, this person wants to know almost everything, as it is a house of collecting information. These people know about almost everything and their mind becomes a business oriented mind. In a way, we can say that their mind is not stable at one place and they want to gain Information about almost everything in the world.\n'
         '\n'
         'As Moon represents emotions and 3rd house is house of younger siblings, this person is very much emotionally attached with younger siblings.\n'
         '\n'
         'These people can be very good salesman. As Moon represents Mother and 3rd house is house of communications, their mother is a very communicative and business lady\n'
         '\n'
         'From 3rd house, Moon aspects the 9th house of Religion, Philosophy, Long Distance Travels, Teachers and Publishing Information. So, they are the people who will be collecting information on different subjects and aspects of life.')),
    ('Moon', 4): ('S23-2024 p.8',
        ('4th house represents your home, home environment, homeland, mother, nourishment, childhood friends, peace of mind, conveniences etc.\n'
         '\n'
         'So, when Moon comes into 4th house, these people really get emotionally attached with their Mother, because 4th house and Moon both represent Mother, so it becomes double energy representing Mother.\n'
         '\n'
         "Mother's teaching and nourishment means everything for them. These people are highly emotional and emotions can be imbalanced. They are very motherly in nature and love taking care of others, so best profession for them is Nurse, Teachers where they are required to take care of people directly\n"
         '\n'
         'Their Mother is most probably someone, who herself loved helping others')),
    ('Moon', 5): ('S23-2024 p.9',
        ('5th house represents Creativity, Happiness, Children, Innovation, Sports, Movies, Stock Trading, Gambling and betting, Education, Ancient Texts etc.\n'
         '\n'
         'So, when Moon comes in 5th house, as Moon represents emotions and 5th house is Children, these people are emotionally attached to their Children. They are very much into learnings and education. They like to learn something almost every time. They can be very creative too. As Moon represents mind and 5th house is creativity and media/arts, these people have very creative mind and do well in any creative field like Acting, Arts, Sports etc.\n'
         '\n'
         'As Moon represents Mother, their Mother is also very creative or educated lady who used to bring these creative values in children and push them towards creativity or education.\n'
         '\n'
         'They are also very much interested in learning Ancient Texts and other scriptures. They can also become good teachers')),
    ('Moon', 6): ('S23-2024 p.10',
        ('6th house is 1st of Dushthana Houses (houses # 6, 8 and 12) and 2nd of Upachaya Houses (houses #3, 6 10 &11). 6th house represents things like diseases, debts, obstacles, enemies, disputes litigations, daily routine life, colleagues at work place etc.\n'
         '\n'
         'So, now the mild and sensitive planet Moon has come into 1st of the tough houses, i. e. 6th house. Why tough house? Just see the portfolio of this house- "diseases, debts, obstacles, enemies, disputes. litigations". So, now our sensitive mind is dealing with all these issues. To start with, it looks like a very tough position but with time these people get used to dealing with obstacles and enemies. Hence, they become very good doctors, lawyers and military people, where they get chance of dealing with obstacles in daily life.\n'
         '\n'
         'As Moon also represents Mother, it shows that even mother of this person had to go through same obstacles in life. Most probably, Mother is a service oriented lady. Not only occupation wise, but also for the service to mankind, animals and under privileged people. These people become very good healers and doctors.')),
    ('Moon', 7): ('S23-2024 p.12',
        ('7th house is house of market place, other people (masses), business partnerships, marriage, spouse, marital happiness etc.\n'
         '\n'
         "This is best position of Moon because 7th house is house of other people and masses and Moon is mind. So, this person's mind is very much concerned for other people. They like to see if everyone around them is in convenient position or not. Basically, a politician loved by people can easily be seen from this position. Their own happiness is not important to them as much as other's comfort. As 7th house is also house of Business and Moon is mind, so these people are very Business Minded people. They are good traders, merchants and best deal makers. As Moon also represents Mother, their mother can also be a very good business person. Even if she may not be a full time business woman but in routine life she would have the best bargaining ability.\n"
         '\n'
         "As Moon is emotions and 7th house is house of spouse, these people are always emotionally involved with their spouse. Their peace of mind comes when they are able to emotionally connect with other people and their spouse. For spouse, they look for a person who can be like their mother. They also get impacted by others' opinions very quickly.")),
    ('Moon', 8): ('S23-2024 p.14',
        ('8th house is house of secrecy, occult knowledge, death, transformation, death and re-birth, in laws family. joint wealth with spouse etc.\n'
         '\n'
         '8th house is not a good place for Moon to be in. Why? Because Moon is a very soft & gentle planet and 8th house has portfolio like death, transformation, death and re-birth, changes and sudden ups and downs.\n'
         '\n'
         'Actually, this position of Moon is good to make anyone a perfect occultist.\n'
         '\n'
         'Moon, that is the Mind, which wants to be relaxed, is not getting good environment in 8th house.\n'
         '\n'
         'As Moon represents emotions and 8th house is sudden ups and downs, here these people suffer a lot emotionally due to sudden events of life.\n'
         '\n'
         'As Moon also represents Mother, their Mother must have gone through similar ups and downs in life. But as everything has flip side, good side of this position is that after about mid-life they just get used to this sudden ups and downs and actually become great counsellors and healers to others and teach others how to deal with these sudden events. They become very good astrologers; mystics, spiritual healers, doctors and counselors\n'
         '\n'
         'A very good placement to become an occultist, mystic healer and doctor')),
    ('Moon', 9): ('S23-2024 p.15',
        ('9th house represents Religion Law, Faith, Fortune, Gurus, Teachings of Father (as father is 1st Guru we get)\n'
         '\n'
         'So, now Mind (Moon) is coming to learn about religion and philosophy of life. Basically, this Moon provides a very religious mind. Someone who wants to get higher learnings and teachings from their Gurus. Their life is much about receiving knowledge and circulating it to others. So, these people are not only inclined towards gaining higher knowledge but also in sharing the same knowledge so that others could be benefited too. No matter what is their religion, they will be inclined towards knowing the details of it. As Moon also represents emotions, we can say that they are emotionally involved with their religious practices.\n'
         '\n'
         'But as always Moon goes through waxing and waning phases, so these people tend to be super-religious at sometimes and not so religious at other times. Moon also represents Mother and 9th house is house of Teachings, it shows that person got teachings from Mother it means that Mother may be highly educated too.\n'
         '\n'
         'A good placement for becoming a Religious Guru and Professor of Higher Learning')),
    ('Moon', 10): ('S23-2024 p.16',
        ('10 house almost represents the things like Government, Authority, Fame etc. Here, Authority should not be understood in literal sense, like someone got a Government job or became a Manager or CEO, Here Authority means doing any work with complete perfection and your opinion matters when it comes to making any decision related to that work, so even a good Hacker can be a person of authority as he is master of that particular work.\n'
         '\n'
         'Now the emotional and gentle Moon, which represents Mind has come into the 10th house of Authority and Status So, these people do want to achieve authority, status and fame in life as their mind gets peace when they get into such positions. Unless and until they get that authority, mind may be restless Also, 10th house is Society so mind is always looking at what society is thinking or saying about person. Their image in public is very important for them.\n'
         '\n'
         'As Moon also represents Mother and 10th house is house of authority it shows that person has got a Mother who is very authoritative As 10th house is also house of Career, it shows that this person and his/her Mother is very career-oriented people. It is hard for these people to live away from the Public Life, as one way or the other they end up in dealing with people. Its a very good placement to become Nurse, Doctor, Caretaker, Counsellor Public Leader etc but wherever they are, they want to be in authoritative position')),
    ('Moon', 11): ('S23-2024 p.18',
        ('11th house represents Elder Siblings, Large Organizations, Huge Structures, Network Circle, Entrepreneurs, Friends, Gains, Income and Earnings etc.\n'
         '\n'
         'Now, the gentle Moon is in 11th house of Gains, Earnings, Friend Circles and Entrepreneurship. Now, this person gains through their friends, network circles and social networks.\n'
         '\n'
         'Here mother also becomes the source of gains, apart from friend circle. It is a good idea for these people to start a business. They will gain more as an entrepreneur. These people gain a lot through their social networks and through their own skills of entrepreneurship. It is necessary for them to attach their mind with some higher purpose or goal through which they can serve humanity.')),
    ('Moon', 12): ('S23-2024 p.19',
        ('12th house is house of Losses. Expenses, Isolated Places, Foreign Lands Asylums, Jails, Hospitals, Imagination etc\n'
         '\n'
         'One thing to always keep in mind with 12th house is that it basically remains the house of losses. So, whichever planet goes in 12th house, even exalted, is in the bucket of losses. Now, to gain out of any such planet, you need to put double effort in things related with that planet.\n'
         '\n'
         'Now the Moon has reached the final destination, i. e. 12th house. Moon is mind and 12th house is house of Foreign Lands and Isolated Places, so mind of these people find balance when they reach foreign lands or places far away from where they were born\n'
         '\n'
         'As 12th house is also a house of imagination and Moon represents mind, they are highly imaginative people and become good Authors. They always have great imaginative ideas which they can use in their writing. They like to live a very private life and at secluded places\n'
         '\n'
         'As Moon also represents Mother, Mother of these people can have exactly same qualities\n'
         '\n'
         "As 12th house is also house of losses and Moon represents Mother, Moon in 12th house shows that relation between Mother and Child suffers, especially in early part of life. They may be unable to understand each other's point of view or she was always away from the person in childhood.\n"
         '\n'
         'As 12th house is house of isolation and Moon is mind, they like to remain at isolated places and stay away from hurdles and obstacles of daily routine life')),
    ('Mars', 1): ('S23-2024 p.20',
        ('Mars represents our will power, courage, ability to take actions, aggressive nature, anger, our fighting ability, brother, a soldier, an athlete and real estate etc.\n'
         '\n'
         '1st house/Ascendant is your self, personality, overall health, life path and head in human body etc.\n'
         '\n'
         'So, when this action oriented planet comes into the 1st house of personality, this person is very active by nature. They are natural athletes and sports-persons. They want to remain fit and active. It is impossible for this person to sit idle. As Mars also represents anger and aggressive nature, these people can be anger prone. As Mars also represents Brothers and Male Friends and 1st house is house of Personality, it shows that your Brothers and Male Friends had a big impact in making your personality or life path\n'
         '\n'
         "Now, Mars is represented by a Soldier in Astrology. What is Soldier's job? It is to protect his land and people So, from 1st house, Mars aspects the 4th house of home, home environment and mother etc, hence these people become very protective of their home and family. Mars then aspects 7th house of Marriage and they become protective of their spouse and marital happiness. It can be dominating nature too. Last aspect of Mars is on 8th house of occult and mysticism, and Soldier (Mars) here wants to dig deep into the secrets of mysticism")),
    ('Mars', 2): ('S23-2024 p.21',
        ('2nd house represents Family, Wealth, Speech, Family Lineage, Values, Mouth, Throat food you like to eat, assets etc\n'
         '\n'
         'So, 1st of all, 2nd house is house of speech and Mars represents Aggression/Anger, so it can give ill-speech to someone in times of anger. Someone may speak lots of foul-words in anger\n'
         '\n'
         'As 2nd house also represents the food you like to eat, Mars here shows that you like to eat non-vegetarian food more, as Mars represents violent activities.\n'
         '\n'
         "This is also house of Family and Mars is aggression, so this person's family environment may be full of aggression. It also shows that someone is able to gain wealth out of real-estate or lands. From 2nd house, Mars aspects the 5th house of education and Mars brings its energy in education. So, these people are very energetic or goal oriented towards their education. Obviously, they can be very much involved in sports too.\n"
         '\n'
         'Mars next aspect goes into 8th house of occult, mysticism, in-laws and sudden events etc. So, Mars may give this person strength to face sudden changes in life. It can also give great ability to research into occult and mysticism to learn it. It may give aggressive relation with in-laws.\n'
         '\n'
         'Mars next aspect goes into 9th house of religion and philosophy etc. It can make them fundamentalist about their own religion or they can have fluctuating interests in higher learning or religion')),
    ('Mars', 3): ('S23-2024 p.22',
        ('3rd house is house of your communication skills, neighbours, short distance travels, younger siblings, marketing, announcements, collecting information, hobbies and skills, self-efforts, business, courage etc.\n'
         '\n'
         "So Mars, the planet of courage is now coming into the house of courage. What will it make? Obviously, a very courageous person. These are highly courageous people who can take any risk in given situation. They can be very dominating with their communication. Even their writing may be thought provoking. As 3rd house also represents communications and Mars represents hands, they are very good with their written communications. They can be very aggressive in their writing. They can motivate people with their blogs or articles. They write very aggressively, that's why they can become very good lawyers too. As 3rd house is Upachaya House, most of these results can be seen in 30s.\n"
         '\n'
         'From 3rd house, Mars aspects the 6th house of disputes and litigation, another reason for them to become a lawyer, communications are important in disputes and litigation. This is also a great position for having a peaceful married life because this person will take pro-active measures to prevent conflicts.\n'
         '\n'
         'Mars next aspect goes to 9th house of teachings of Guru and it can lead to dominating struggle between them and their Gurus\n'
         '\n'
         'Mars next aspect goes to 10th house, and same aggression goes against the authority of father and they try to get the authority from father or career. But overall, a very good position for a strong willed person who can do anything to achieve on his own')),
    ('Mars', 4): ('S23-2024 p.23',
        ('4th house represents your home, home environment, homeland, mother, nourishment, childhood friends, peace of mind, conveniences etc.\n'
         '\n'
         'So, this is not the ideal position for Mars to be in, as Mars is aggression and 4th house is house of home and home environment. So, this position of Mars is going to bring aggression inside home. So, this position of Mars makes home environment filled with aggression and anger. It gives an aggressive relation with Mother. At the same time, this is a very good position for someone to enter into business of Real Estate, as 4th house relates with Home, Land and Property and Mars is the main significator of these things.\n'
         '\n'
         'Mars aspect goes to 7th house of Marriage. As it is one of the Mangalik Position of Mars, it gives the same anger and aggressive/dominating nature or experience in marital relationship.\n'
         '\n'
         'Mars next aspect goes to 10th house of Career. This is a very good position for someone to enter into business of Real Estate, as 4th house relates with Home, Land, Property, Vehicle and Mars is the main significator of these things. This can make a person approach his career in a very dominating manner.')),
    ('Mars', 5): ('S23-2024 p.24',
        ('5th house represents Creativity, Happiness, Hobbies, Children, Innovation, Sports, Movies, Stock Trading. Gambling and Betting. Education, Ancient Texts etc.\n'
         '\n'
         'Mars in 5th house is natural position for someone in Sports. They can be great athlete and sports-person as 5th house is house of sports and creativity and Mars represents courage, will power and fighting ability.\n'
         '\n'
         'They may become dominating towards children and their romantic relationship may suffer due to anger and dominating nature. Even in matters of education, person would love to compete and dominate others by getting higher marks. So, natural Mars approach of dominance will show up in 5th house matters.\n'
         '\n'
         'From 5th house, Mars aspects the 8th house of Occult Science and Secrecy and Mars provides lots of courage to person to research into occult and secrets to know about it.\n'
         '\n'
         'Mars next aspect goes to 11th house of gains, earning and income, and these people are very dominating towards their gains. They want it to be more than their peers.\n'
         '\n'
         'Mars next aspect goes to 12th house of Spirituality and Foreign Lands, and here person feels fluctuations in his spiritual interests,')),
    ('Mars', 6): ('S23-2024 p.25',
        ('6th house is 1st of Dushthana Houses (houses #6.8 and 12) and 2nd of Upachaya Houses (houses #3, 6, 10 & 11),6th house represents things like diseases, debts obstacles, enemies, disputes, competitions, litigations, under privileged people, pets, daily routine life, colleagues at work place etc.\n'
         '\n'
         'Mars is fighter & aggressive nature and 6th house in house of obstacles and conflicts. This is where Mars gets a best environment. Mars finds best environment to deal with obstacles, conflicts and competitors and defeat them. But as 6th houses Upachaya House by nature, these results will be seen in 30s. in early life, person will have lots of issues and obstacles in life. They can be great Lawyer, Fighter, Sports Person or Doctors. They become pro-active in defeating their enemies Aspect wise, Mars 4th aspect goes to 9th house and the person becomes fundamentalist in his religious views. He can have struggle with his Gurus and try to over-power them\n'
         '\n'
         'Mars next aspect good to 12th house and they can be spendthrift by nature. Mars next aspect goes to 1st house/Ascendant and they can find it difficult to find their right life path in early life.')),
    ('Mars', 7): ('S23-2024 p.26',
        ('7th house is house of market place, other people (masses), business partnerships, agreements, marriage, spouse, marital happiness etc.\n'
         '\n'
         'As it is one of the Mangalik Yoga position of Mars, conditions related to Mangalik Yoga may be taken into consideration. As it is mainly a house of marriage and marital happiness, and Mars is aggression, so if a person gets married to a non-mangalik person before the maturity age of Mars (28 to 31), then there may be aggression. or anger impacting marriage and marital happiness. But if Mars is matured and partner is also a Mangalik, then this position can actually give a very protective and caring spouse. But aggression and dominance towards other people or spouse is common theme of this placement. It can be beneficial in business as person will have dominating approach towards business.\n'
         '\n'
         'From 7th house, Mars aspects the 10th house of Career and Work Environment. Here, person remains dominating in matters of career. It can create trouble with bosses. Mars next aspect goes to 1st house and makes person highly active.\n'
         '\n'
         "Mars last aspect goes to 2nd house. it can make person's wealth aspect fluctuating till 30s.")),
    ('Mars', 8): ('S23-2024 p.27',
        ('These are the real courageous people of the world. Born Fighters, as 8th house is considered as the most chaotic house which represents things like death, sudden events like accidents, secrecy and like things and Mars represent courage, will power to fight against all these things. So, these people become fighters, soldiers, "Great Astrologers, Occult Practitioners, Mystics etc. Even if they don\'t take any of these professions, their daily routine life is filled with much of struggles and fights. Mars here gives loads and tonnes of courage to fight through all the struggles of life.\n'
         '\n'
         'From 8th house, Mars aspects the 11th house of earnings and they can have dominating approach towards making more and more gains. Mars next aspect goes to 2nd house of Family and gives an environment filled with aggression, dominance and anger in early childhood. Mars next aspect goes to 3rd house of efforts and it can give them fluctuating interests as to which area of life they should put efforts in')),
    ('Mars', 9): ('S23-2024 p.28',
        ('9th house represents Religion, Law, Faith, Fortune, Gurus, Teachings of Father (as father is 1st Guru we get)etc.\n'
         '\n'
         'So, now the Mars energy comes in 9th house of religion. These people are adamant about their religious beliefs. They can become those fundamentalists who can do anything for their religious faith. They also have a different point of view for their religious beliefs and they discard the teachings of their Guru and like to make their own rules. At the same time, they can be very dominating in matters of higher education and will treat education with war like mentality.\n'
         '\n'
         'Mars 4th aspect goes to 12th house and they become dominating with their Spiritual Values. They also become spendthrift at times. Mars next aspect goes to 3rd house of Self-Effort and Business and they are dominating about their business efforts.\n'
         '\n'
         'Mars ned aspect goes to 4th house of Mother and Home. This creates a fluctuating relation with mother or home of ups and downs')),
    ('Mars', 10): ('S23-2024 p.29',
        ('10th house represents things like Government, Authority, Fame etc. Here, Authority should not be understood in literal sense, like someone got a Government job or became a Manager or CEO of a Firm Here Authority means doing any work with complete perfection and your opinion matters when it comes to making any decision related to that work\n'
         '\n'
         'House wise this is strongest position of Mars because here Mars gets the directional strength. Person will have exact idea as to what he wants to do in life. As 10th house is house of fame in society and authority Mars here will do anything it takes to get that fame and authority. These people will be very much career oriented and want to reach up to the top of hierarchy in their workplace.\n'
         '\n'
         'From 10th house, Mars aspects the 1st house/Ascendant, and makes a person very active. It is hard to make this person sit idle\n'
         '\n'
         'Mars next aspect goes to 4th house and these people try to dominate the proceedings at home. It can also provide the aggression in home environment and relations with mother\n'
         '\n'
         'Mars next aspect goes to 5th house and for these people, relation with children, love interests and their own education becomes fluctuating by nature')),
    ('Mars', 11): ('S23-2024 p.30',
        ('11th house represents Elder Siblings, Large Organizations, Huge Structures, Network Circle, Entrepreneurship, Friends, Gains, Income and Earnings etc. So 1st of all, as it is house of earnings and gains, and Mars is a planet of taking action, here Mars makes a person very active and energetic towards his gains, income and money. It means they will be ready to take any action, whatever it takes, to make their earnings better\n'
         '\n'
         'As it is also house of elder siblings, Mars here gives the person an elder sibling but there might be a power struggle between siblings.\n'
         '\n'
         'As it is also a house of large organisations, Mars here provides will power to person to reach up to the top hierarchy of any big Company. At the same time, they can also become a spendthrift.\n'
         '\n'
         'From here, Mars aspects the 2nd house of family wealth and speech. It makes the person dominating towards his family and accumulated wealth but gives a harsh speech. Mars next aspect goes to 5th house of sports, education and children. This makes the person very active about sports and education. They can become good sports-persons but they can be dominating towards their children and love interests. Finally, Mars 8th aspect will go to 6th house and create instability in their job setup with colleagues. It can also bring illnesses of sudden nature and health may be fluctuating')),
    ('Mars', 12): ('S23-2024 p.31',
        ('12th house is house of Losses, Expenses, Isolated Places, Foreign Lands, Asylums, Jails, Hospitals, Imagination etc.\n'
         '\n'
         'One thing to always keep in mind with 12th house is that it basically remains the house of losses. So, whichever planet goes in 12th house, even exalted, is in the bucket of losses. Now, to gain out of any such planet, you need to put double effort in things related with that planet.\n'
         '\n'
         'It represents that a persons energy and action are going in matters of 12th house. It can represent someone who is working as Jailer in Prison or Doctor at a Hospital or an Asylum. It can also show a sports person, who goes to other countries to represent his country in sports. This position of Mars can also make a person Spendthrift, as Mars is in the house of losses and expenses\n'
         '\n'
         'From 12th house, Mars aspects the 3rd house of Siblings, so this aspect provides younger siblings but there may be struggles and arguments between siblings. As 3rd house is also a house of Communication Skills, this aspect provides a dominating and aggressive way of speaking.\n'
         '\n'
         'Mars next aspect goes to 6th house of obstacles and disputes, and this aspects provides the person, lots of will power and courage to fight against the obstacles of life.\n'
         '\n'
         'Mars last aspect to 7th house of Marriage and Spouse makes it a mangalik position, so care should be taken regarding Mangalik Yoga measures, It brings fluctuations and ups/downs in relations')),
    ('Mercury', 1): ('S23-2024 p.32',
        ('1st house shows personality, body, head, etc. Mercury is about communication. Mercury in the 1st house makes the person want to communicate. 1st house is about self, so they want to portray their positive side to the masses. They will be very clever, talented, diplomatic people. They are very jovial and have a sense of humor. They will be good looking and very youthful in appearance. They like to do many things simultaneously. They have the capacity to think and do more than one work at a time. But the problem with them is that they cannot get expertise in anything. They are like ‘jack of all trades and master of none’. But in a group, they will be a popular face, because they know many things and they can talk on various topics. They will have business skills and problem-solving abilities. They can become entrepreneurs, diplomats, writers, etc.')),
    ('Mercury', 2): ('S23-2024 p.33',
        ('2nd house signifies speech, wealth, family, food habits, etc. If Mercury is well placed then they become amazing communicators, good in debates, will have very good argumentative skills, but can also be critical. They can be well versed in many languages. They will be very intelligent in money matters. They will have certain calculations on how much to save and spend, They will do good planning on financial goals. Therefore they can do well as bankers, wealth managers, advisors, etc. The position will be good for businessmen, entrepreneurs, teachers etc. They can be singers, artists, too. They can also be very charitable in nature. Mercury from 2nd house aspects 8th house. They will use their intelligence and logic in occult sciences as well. They can go deep into subjects like astrology, philosophy, etc.')),
    ('Mercury', 3): ('S23-2024 p.34',
        ('3rd house represents courage, self efforts, communication, brothers etc. In the natural zodiac, Mercury owns the 3rd house of Gemini. So the energy of Mercury suits well in this house. As Mercury is the fast-moving planet and applying the energy with self-effort, they tend to be very quick in everything. They are quick to react, very fast in decision making, quick learner, etc. This trait will help them in a situation that requires being very active like sports, business, etc. For example. in Cricket sports, a batsman should be very quick in deciding which shot to play. Once the ball leaves the bowlers’ hands, there is only a fraction of the second to decide his shot. He has to be very very quick in decision making. So Mercury in the 3rd house gives that strength. But if Mercury is afflicted, then they may take the wrong decisions. In this house, communication is not only about talking, they can communicate in writing, media, mediating, etc. They will have nice handwriting, excellent written communication. Their brothers will be youthful, jovial, business-minded, etc.')),
    ('Mercury', 4): ('S23-2024 p.35',
        ('The Fourth house deals with happiness, home, vehicle, land, education, mother, etc. When Mercury is in the 4th house, it makes the native well educated. They will learn very quickly. They will be attached to family and motherland. They may be interested in education concerned with all types of communication such as telecommunications, electronics, engineering, commerce, foreign services, etc. Also, the impact of other planets on Mercury also should be studied. They can do business sitting at home. They can even do business related to education like setting up educational institutions, business management, trading, information technology,')),
    ('Mercury', 5): ('S23-2024 p.36',
        ('5th house relates to intelligence, creativity, learning, children, speculation etc. They will be very intelligent, creative, talented, well versed in many subjects. They will have a curious mind of learning new things. But the problem is that they may try to learn everything and do not get expertise in any particular field, So there should be some good aspect of other planets on Mercury. As Mercury joins the creative house, they will be very creative in writing. People love their style of writing. They may have an interest in speculative business like stock market or horse-trading. In the stock market, they will be particularly interested in technical analysis, where they will study the stock charts. The children will be very intelligent, creative, and multi-talented. They can worship Lord Vishnu to improve Mercurian energy.')),
    ('Mercury', 6): ('S23-2024 p.37',
        ('6th house signifies diseases, conflicts, enemies, debt, competition etc. Remember Mercury is exalted in Virgo which is the 6th house of the natural zodiac. 6th house signifies service, and they may work in the areas of financial management, teaching, accounting, etc. They will communicate well with peers. They will be very organized, orderly in their work. Because of their organizational capabilities, they always are loved by their bosses. These people do not like conflicts at work. They will try to balance the work environment. They will be selfless in their work. They may also work for some charity organizations apart from their regular work. They will help others when in need. Generally, they will have lesser enemies, because of the quality of Mercury. They are good at diplomacy, persuasive skills, and communication, so they will keep their enemies at bay. They have to face some problems related to health with respect to the house lordship of Mercury.')),
    ('Mercury', 7): ('S23-2024 p.38',
        ('7th house represents marriage life, spouse, partnerships, etc. They will be youthful, talented individuals. They may be very conscious of their public image. Their spouse will be beautiful, intelligent, well behaved, diplomatic, adjustable, cunning. They would like to have a very communicative relationship with spouse. They will flourish in business, trade, and will be an expert in accounting and auditing. They will have a knack of business acumen especially they will excel with a business partnership.')),
    ('Mercury', 8): ('S23-2024 pp.39-40',
        ('8th house deals with longevity, transformation, sudden events etc. They will be intelligent, well versed with many subjects. They will have a research-oriented mind. They may be interested in the occult like astrology, tantra, etc. Here Mercury gives the intelligence to study deep into the subject. If they meditate, they will easily gain intuitive powers. They may also have a philosophical bent of mind. They will not take anything on the face value, they will research on the subject for deep insights. It will be difficult for anybody to win debates with these people because they will have knowledge of the subject thoroughly.\n'
         '\n'
         'Mercury represents communication skills, marketing, calculative ability, younger siblings, hobbies, skills with hands, intelligence, quick decision making, logical thinking, youthfulness etc.\n'
         '\n'
         '8th house is house of secrecy, occult knowledge, death, transformation, death and re-birth, In laws joint wealth with spouse etc.\n'
         '\n'
         'So this can be termed as the most powerful placement for becoming an Astrologer. As it is house of occult and hidden science and Mercury is significator of Astrology, this placement may make an excellent Astrologer. These people would also love to communicate about occult and hidden science to people. So, a blogger/teacher on occult can be seen with this.\n'
         '\n'
         'As 8th house is house of in-laws family and Mercury represents communication, this person is highly communicative with in-laws 8th house is also a house of taxes and Mercury represents calculating skills, so is a good placement for becoming an auditor too. 8th house is also other people needs and Mercury is a counselor, so it shows a career in counselling people in their needs. It is also a house of death and rebirth, Mercury is a businessman, it shows someone in business of life insurance or someone who deals with inheritance or bankruptcy matter. From 8th house, Mercury aspects the 2nd house of Family, Speech etc. whereas Mercury itself is Communication, it shows that this person has good communicative relation with his family')),
    ('Mercury', 9): ('S23-2024 p.41',
        ('9th house is for luck, wisdom, teaching, father, etc. Normally people with this position will be well educated. They will always try to learn higher wisdom. They are people not just follow religion blindly rather they find a reason for any rituals, beliefs. They apply their logical mind to decode religion. They are honest, follow morality, not desirous of others’ wealth. They may teach and preach. Their teaching will always be interesting to others. They may use their intelligence and higher learning for business purposes. The father of the native may have business skills.')),
    ('Mercury', 10): ('S23-2024 p.42',
        ('10th house indicates karma, actions, activity, career etc. Mercury is about youthfulness, intelligence and 10th house is about action. So naturally, they will act with intelligence. Whatever they do, they do it with vigor and enthusiasm. Their communication and intelligence power will blossom here, because the 10th house signifies public life. They will do excellent in the profession. Their profession can be related to the karaka of Mercury. They will be multi-talented in the true sense. They will have the craving for learning various subjects. Their only problem is that they try to do many things simultaneously. Because of this, they may lack the focus after some time. They may not like monotonous work and they try to innovate themselves more. There may be a lot of changes in their career.')),
    ('Mercury', 11): ('S23-2024 p.43',
        ('11th house is about gains, desires, achievements etc. When Mercury is in this house, the native will be a very socializing person, will have many friends, etc. They will be highly ambitious and have a positive attitude. Their social network will be very vast. They are the kind of people whom everyone calls up for any help. In today’s scenario, we can say that they will be always busy on the phone. Apart from that, other Mercurian qualities are abundant in them. They will be creative and can have many sources of income. They will be good in speculative business-like in stock markets. They will do good as a teacher, public speaker, etc. They may be involved in activities involving diplomatic communicator, interpreter, press reporter, editor, newsreader, etc.')),
    ('Mercury', 12): ('S23-2024 p.44',
        ('First of all these people have real problem in communicating to people, hence they become very quiet, especially early in life, for the simple reason that Mercury is communication and 12th house is house of losses but as they speak less, they like to communicate through their writing. Hence, this is the best placement for someone to become an author or poet. Another reason for being into this field is that 12th house is also house of imagination, hence Mercury wants to communicate about imaginations through books\n'
         '\n'
         "12th house is also house of other dimensions and spirituality and Mercury is person's intellect. So, these people love to collect info about Spirituality and that improves their intellect. They like to work in isolation Mercury will give best results here when they are writing about their imagination, spirituality and other worldly things\n"
         '\n'
         'This is another placement which can make an excellent Astrologer, as Mercury remains Karaka of Astrology and 12th house is house of imagination, spirituality and intuition.\n'
         '\n'
         'in normal sense this position also shows someone running a business in foreign lands, as 12th house is house of foreign lands and Mercury is planet of Business. From 12th house. Mercury aspects the 6th house of diseases, disputes and conflicts. Now Mercury would try to resolve these conflicts through their intuition, spirituality and imaginations.')),
    ('Jupiter', 1): ('S24 p.2',
        ('1st house/Ascendant is your self, personality, overall health, life path and head in human body etc.\n'
         '\n'
         'So when Jupiter comes in to Ascendant/1st house, person becomes very knowledgeable. He is one of those people in society, who are looked upon by others with lots of respect and honor due to the knowledge and wisdom he has. Even if, this person is not educated, he will still be knowledgeable and intellectual. Their whole approach to life will be philosophical. They are looked upon in society as a natural Guru\n'
         '\n'
         'From 1st house, Jupiter aspects the 5th house of Education, Children Creativity and Speculative Business Not only this person himself becomes very well educated but he is able to give the same education, knowledge and wisdom to his children. They also get lucky in speculative businesses.\n'
         '\n'
         "Jupiter's next aspect goes to 7th house of Marriage and Spouse, He shares knowledge and wisdom with spouse\n"
         '\n'
         "Jupiter's last aspect goes to 9th house of religion, higher knowledge, philosophy, pilgrimages etc. Now the person not only gets the basic education of 5th house but also gets the higher education of 9th house. So these people receive Ph.D. and D Lit, and other higher degrees\n"
         '\n'
         "Even if this person doesn't have great certificates to show, his level of higher knowledge and higher learning would be such that he doesn't need any degree or certificate")),
    ('Jupiter', 2): ('S24 p.3',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru Spirituality, Religion, Philosophy, Literature, Elderly People.2nd house represents Family, Wealth Speech, Family Lineage Values Mouth, Throat, food you like to eat, Assets etc.\n'
         '\n'
         "As 2nd house is house of family and family lineage & Jupiter represents Religion & Spirituality, this position suggests that one has good spiritual environment in family. Person belongs to a religious family. As 2nd house is house of speech and Jupiter is Spirituality, this makes person's speech very spiritual and preachy. It is also house of wealth and Jupiter is significator of wealth, so it may expand their wealth and will always be seen as wealthy people\n"
         '\n'
         "From 2nd house, Jupiter aspects the 6th house of disputes, obstacles and enemies & it provides the wisdom and knowledge to win over enemies. This position can make a person lawyer as Jupiter is written Law and Jupiter's another aspect goes to 10th house, which is house of Career. So, it shows that someone is making a career in law and litigation\n"
         '\n'
         'Another aspect of Jupiter goes to 8th house of occult, mysticism and hidden knowledge and as Jupiter is knowledge itself, this position gives an extra-ordinary interest in gaining knowledge of occult and mysticism')),
    ('Jupiter', 3): ('S24 p.4',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge Wisdom, Law Guru Spirituality, Religion, Philosophy Literature Elderly People\n'
         '\n'
         '3nd house is house of your communication skills, neighbours, short distance travels, younger siblings. marketing, announcements, collecting information, hobbies and skills, self efforts, courage etc.\n'
         '\n'
         'Jupiter is planet of Wisdom, so first of all this persons communications would be filled with wisdom. It is not necessary that they will be preachers or saints but whatever they say will have some good message involved within it. They can be seen as Preachy in Society. Jupiter here makes a person a very good businessman but in his 30s as it is one of Upachaya Houses, which grows with time. They become very good writers and journalists. They can be like a Guide to their sibling.\n'
         '\n'
         'From 3rd house, Jupiter aspects the 7th house of marriage. It shows the need to educate yourself in matters of relations and business\n'
         '\n'
         "Jupiters next aspect goes to 9th house of religion philosophy, pilgrimage and almost all the things which Jupiter represents. So Jupiter's aspect further expands the quality of 9th house gradually and makes a person highly religious and philosophical\n"
         '\n'
         "Jupiter's last aspects goes to 11th house of gains, network circles, elder siblings So, these people gain from their elder siblings. They have large network circles and friends. They can be very good with money matters. But all these results in 30s as 11th house is again Upachaya Houses. So, before 30, person needs to learn about how to deal with all these matters")),
    ('Jupiter', 4): ('S24 p.5',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru. Spirituality, Religion, Philosophy, Literature, Elderly People.\n'
         '\n'
         '4th house represents your home, home environment, homeland, mother, nourishment, childhood friends, peace of mind, conveniences etc.\n'
         '\n'
         'Jupiter in 4th house of home gives the person very big home, as Jupiter represents expansion of things, it also gives lots of conveniences and vehicles in home. It also gives a strong bond with mother, like mother becomes Guru of a person. The person himself is considered as Guru/Learned Person in home or home town and people ask for his advice.\n'
         '\n'
         'From 4m house, Jupiters aspect goes to 8th house of secrecy, occult, in-laws and joint assets with spouse So here, not only person gets the knowledge of occult, secrecy (as Jupiter is knowledge and wisdom) but so gives a person benefits from in-laws. Spouse brings wealth in life.\n'
         '\n'
         "Jupiter's next aspect goes to 10th house of career. As Jupiter is divine teacher, it can make a person a very good teacher. A career in counselling and teaching is certainly on. As 4th house also represents land and real estate, Career in Real Estate can be a good option too\n"
         '\n'
         "Jupiter's last aspect goes to 12th house of Spirituality and Isolation. It shows a spiritual inclination.")),
    ('Jupiter', 5): ('S24 p.6',
        ('Jupiter in the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru Spirituality Religion, Philosophy, Literature, Elderly People.\n'
         '\n'
         '5th house represents Creativity, Happiness, Hobbies, Children, Innovation, Sports, Movies, Stock Trading, Gambling and Betting, Education, Ancient Texts etc.\n'
         '\n'
         'This person is all about knowledge and education. As 5th house is knowledge and education, Jupiter also represents knowledge and wisdom and Jupiter is the natural significator of 5th house. So, this person is ways looking to achieve his Degree, Post Grad Degree and higher learnings. They would even travel to the faraway places in the world to gain knowledge. They will gain association of Gurus and later in life, they may want to share the same knowledge and wisdom to others.\n'
         '\n'
         'From 5th house, Jupiter aspects the 9th house of higher learning. Another indication towards need for higher education\n'
         '\n'
         "Jupiter's next aspect goes to 11th house of network circles and friends, It shows that they like to share the knowledge with friends and networking circle. It also expands their gains\n"
         '\n'
         "Jupiter's last aspect goes to 1st house/Ascendant of life force and personality Here, the person is society as highly learned, wise and intellectual person it also shows the need to learn about the right life path")),
    ('Jupiter', 6): ('S24 p.7',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People.\n'
         '\n'
         '6th house is 1st of Dushthana Houses (houses 6, 8 and 12) and 2nd of Upachaya Houses (houses #3, 6, 10 & 11), 6th house represents things like diseases, debts, obstacles, enemies, disputes. competitions, litigations, under privileged people, pets, daily routine life, colleagues at work place etc.\n'
         '\n'
         'An excellent placement for being a lawyer, as Jupiter represents Knowledge and 6th house represents Disputes and Litigation. So, it shows a person who uses his knowledge to resolve the disputes of others. It also shows someone in service of under-privileged people and pets through his knowledge and wisdom It can also make someone a teacher of Legal Matters as 6th house is disputes and Jupiter is The Great Guru In daily routine work life, he will be treated as a learned Guru, but as it is one of the Upachaya Houses which grows with time, this situation comes after mid-30s.\n'
         '\n'
         'From 6ith house, Jupiter aspects the 10th house of Career. It shows a need to know about the right career\n'
         '\n'
         "Jupiter's next aspect goes to 12th house of isolated places and let's connect the dots again. This shows that person likes to share knowledge with foreign people\n"
         '\n'
         'Jupiters last aspect is on family. It shows that person needs to learn how to manage family and wealth matters')),
    ('Jupiter', 7): ('S24 p.8',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People.\n'
         '\n'
         '7th house is house of market place, other people (masses), business partnerships, agreements, marriage, spouse, marital happiness etc.\n'
         '\n'
         'for`a girl has this position of Jupiter in 7th house, she should feel blessed. Spouse will be of balanced nature: Spouse will work as guidance. He/She will be knowledgeable and full of wisdom. This placement also suggest someone who gains wealth from Business, as Jupiter is wealth and 7th house is Business. This is also a good placement for becoming a lawyer.\n'
         '\n'
         "From 7th house, Jupiter's aspect goes to 11th house of gains and network circles. It shows a need to learn about increasing gains.\n"
         '\n'
         "Jupiter's next aspect goes to 1st house/Ascendant. 1st house is personality and Jupiter is knowledge and wisdom. So with this aspect, person gets recognition as very wise and knowledgeable in society.\n"
         '\n'
         "Jupiter's last aspect goes to 3rd house of Siblings and Self-effort. It shows the need to learn about the right area of self-efforts")),
    ('Jupiter', 8): ('S24 p.9',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People. For a girl, Jupiter also represents Husband.\n'
         '\n'
         '8th house is house of secrecy, occult knowledge, death, transformation, death and re-birth, In laws family, joint wealth with spouse etc.\n'
         '\n'
         'Besides that it is also house of in-laws and assets of in-laws and as Jupiter represents expansion of things, this person can have huge property and wealth from in-laws. Now, a real unique thing. 8th house is serving the needs of other people and Jupiter is Religion and Spirituality. So, this placement can make a person a kind of Spiritual Healer to others.\n'
         '\n'
         'From 8th house, Jupiter aspects the 12th house of Spirituality, Charity and Donations etc. It shows the need to learn about spiritual matters.\n'
         '\n'
         "Jupiter's next aspect goes to 2nd house of family and wealth. Here Jupiter blesses the person with a spiritual and religious family and provides lots of wealth. There speech becomes very spiritual and wise.\n"
         '\n'
         "Jupiter's last aspect goes to 4th house of mother and home. It shows the need to learn about how to get peace of mind.")),
    ('Jupiter', 9): ('S24 p.10',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People. For a girl, Jupiter also represents Husband.\n'
         '\n'
         '9th house represents Religion, Law, Faith, Fortune, Gurus, Teachings of Father (as father is 1st Guru we get) etc.\n'
         '\n'
         'So, quite obviously, planet of knowledge and wisdom is now coming in the house of knowledge and wisdom, so this person will obviously be very knowledgeable and wise. They will follow their belief system like anything. Not only their own religion, but they will be equally anxious to know about different religions and religious beliefs. They love discussions of religion and philosophy. They love comparative studies of different religions. Otherwise also, they are very highly educated people and they should be.\n'
         '\n'
         'From 9th house, Jupiter aspects the 1st house of personality and life path. It shows the need to find the right life path.\n'
         '\n'
         "Jupiter's next aspect goes to 3rd house of Communication Skills, Business, Marketing etc. They become quite philosophical and spiritual in their way of communications and they share their knowledge through their business.\n"
         '\n'
         "Jupiter's last aspect is on 5th house of Education. It shows the need to educate yourself.")),
    ('Jupiter', 10): ('S24 p.11',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People. For a girl, Jupiter also represents Husband.\n'
         '\n'
         '10th house represents things like Government, Father, Authority, Fame etc. Here, Authority should not be understood in literal sense, like someone got a Government job or became a Manager or CEO of a Firm. Here Authority means doing any work with complete perfection and your opinion matters when comes to making any decision related to that work, so even a good Hacker can be a person of authority as he is master of that particular work.\n'
         '\n'
         'These are the people who are considered as highly learned and wise in their work place and people naturally come to them for advice. In society and public life too, they are looked upon as wise and intellectual people. They should be careful of not being fundamentalist and impose their beliefs on others. It shows good gains from father and other authoritative people.\n'
         '\n'
         'From 10th house, Jupiter aspects the 2nd house of wealth, family and speech. It shows the need to learn about how to manage family and wealth matters.\n'
         '\n'
         "Jupiter's next aspect goes to 4th house of home and mother. It provides a big home to the person. This shows that they like to share their knowledge from home or private offices.\n"
         '\n'
         "Jupiter's last aspect goes to 6th house of disputes and enemies. It shows the need to find the right daily work routine. So, the biggest challenge with this position is to find the right career for yourself.")),
    ('Jupiter', 11): ('S24 p.12',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People. For a girl, Jupiter also represents Husband.\n'
         '\n'
         '11th house represents Elder Siblings, Large Organizations, Huge Structures, Higher Goals and Purposes for the Universe, Network Circle, Entrepreneurship, Friends, Gains, Income and Earnings etc.\n'
         '\n'
         'This placement is great for someone who wants to be entrepreneur because Jupiter represents wealth and 11th house is house of gains and network circles. So, person gains a lot through his network circles. This position can make a person filthy rich, as planet of wealth is sitting in the house of income and gains. It is necessary that their work is directed towards serving humanity or serving a higher cause. Then best results can be expected.\n'
         '\n'
         "Another reason for becoming a successful entrepreneur from this position of Jupiter is Jupiter's aspects. From 11th house, Jupiter aspects all the houses that relates to running a business. Jupiter's 5th aspect and 9th aspect go to 3rd house of courage, marketing business and self-efforts etc & 7th house of business. It shows the need to get the knowledge about the best possible business\n"
         '\n'
         "Jupiter's next aspect goes to 5th house of education, children, creativity, risk taking abilities and speculative businesses. As Jupiter represents knowledge and 11th house is house of gains, this aspect will provide all the gain of knowledge and education. These people also impart same knowledge and education to their children. Person also gains from Speculative Businesses and his creativity.")),
    ('Jupiter', 12): ('S24 p.13',
        ('Jupiter is the most benefic planet and it represents all the auspicious things like Knowledge, Wisdom, Law, Guru, Spirituality, Religion, Philosophy, Literature, Elderly People. For a girl, Jupiter also represents Husband.\n'
         '\n'
         '12th house is house of Losses, Expenses, Isolated Places, Spirituality, Foreign Lands, Foreign Companies, Imagination, Sub-Conscious Mind, Charity, Donation, Asylums, Jails, Hospitals, Hidden Talent and Secrets of Other World etc.\n'
         '\n'
         'One thing to always keep in mind with 12th house is that it basically remains the house of losses. So, whichever planet goes in 12th house, even exalted, is in the bucket of losses. Now, to gain out of any such planet, you need to put double effort in things related with that planet.\n'
         '\n'
         "As Jupiter is knowledge, wisdom and God's blessings and 12th house is house of Spirituality, Hidden Talents and Secrets, this position of Jupiter becomes number one in following the path of Spirituality and Occult. These are highly spiritual beings who find their path in life in Occultism, Psychic, Spiritual Healing etc. They start teaching the world out of their experience that look towards spiritual path in life. They find their mental peace in spiritual realm and meditation.\n"
         '\n'
         "From 12th house, Jupiter aspects the 4th house of home and due to the effect of Jupiter's spirituality, they convert their home in to a spiritual place. It also shows the need to learn Meditation.\n"
         '\n'
         "Jupiter's next aspect goes to 6th house of obstacles, enemies, debts etc. It shows that they like to share their knowledge in resolving conflicts of others.\n"
         '\n'
         "Jupiter's last aspect goes to 8th house of occult knowledge and hidden secrets etc. This shows the need to learn about occult and mystical side of life.")),
    ('Venus', 1): ('S24 pp.14-15',
        ('Venus: With Venus in the 1st house in Vedic astrology you have a passion for 1st house significations. Your passion is your body, physical appearance, love, relationships, creativity, and social involvement.\n'
         '\n'
         'Meaning of Venus: The planet Venus represents Love, Romance, Marriage, Passion, Desire, Beauty, Transformations, Pleasures, Luxuries, Comforts, Socializing, Women. When Venus comes into your 1st house all the qualities of Venus express themselves strongly. The Venus energy will influence your personality, physical body, path in life, and thoughts.\n'
         '\n'
         'Personality: You are very charming and have a magnetism about you that draws other people to you. You are socially adept and love the company of others. You feel a sense of connection when you are around other people. You need people in your life to feel balanced. Building relationships with others is a huge part of your life.\n'
         '\n'
         "Body: When you have Venus in the 1st house, you like to dress beautifully. If you are a woman, you will love dressing in colorful clothing, accessories, perfumes, and jewelry. If you are a male, you will love appealing clothing, cologne, men's jewelry (chains, watches, etc). Both women and men care deeply about their appearance and how they look physically. You love showing off your fashion and sense of style.\n"
         '\n'
         'In the natal chart, Venus shows what you find enjoyable in life. It also describes how you want to be loved and how you love in relationships. Giving and receiving affection are all related to Venus in astrology.\n'
         '\n'
         'If your Venus is located in the first house it influences to a great extent what you look like. A Venus in first house suggests a beautiful physical body. You look like a goddess. Venus here gifts you with charm and grace.\n'
         '\n'
         "This aspect is often found in the charts of actors, models and people who are just simply beautiful. It's a very feminine placement.\n"
         '\n'
         'Venus here shows a person who has excellent social skills. You are affectionate, kind and charismatic. You want peace, harmony and beauty around you. People are drawn to you, and you are popular.')),
    ('Venus', 2): ('S24 pp.16-17',
        ("Venus – When you have Venus in the 2nd house in Vedic astrology your passion and desires are related to the 2nd house. You are passionate about your facial appearance, resources, family, money, finances, accumulating luxury items, and food. The 2nd house is the House of Taurus which is Venus's home sign. Venus feels comfortable and at ease in the 2nd house and gives good results.\n"
         '\n'
         'Face – You have a beautiful (Venus) face (2nd house) that attracts attention. If you are a woman, you love wearing makeup (lipstick, eyeshadow, blush, mascara) to enhance your facial beauty. Your face is one of the most attractive parts of your body.\n'
         '\n'
         'Silver Spoon – There is a saying that if you have Venus in the 2nd house you are born with a silver spoon (wealth, luxury). This means, as a small child there were enough resources available to support your development. Even if your parents or guardians were struggling, it was a priority that you received everything you need and more.\n'
         '\n'
         'Luxury Food – The 2nd house relates your taste buds and the type of food you like. You appreciate and love fine dining that appears to your luxury taste buds. You have expensive taste; you love specialized food. You can enjoy sour and acidulous foods.\n'
         '\n'
         'Money – You have a passion for making money. Wealth can be promised in Venus is involved Lakshmi Yoga or Dhan yoga.\n'
         '\n'
         "Sweet Voice – You have a pleasant tone to your voice. When you speak it's very pleasant and sweet. Even if you are male with a deep voice, the tone of your voice will be strong but alluring. Conjunctions with other plants with Venus can change the tone of your voice. A sweet singing voice is indicated with this position.\n"
         '\n'
         'Resources – The 2nd house represents your resources, and Venus is the karaka of luxuries. With Venus in the 2nd house, you love collecting luxuries items like gemstones, and jewelry. You may have a safety deposit box where you keep all your precious jewelry. You all are accumulating and collecting all types of luxury items. You value these items as your assets.\n'
         '\n'
         'Learn about Love – You learned about relationships, love, and creativity through family (2nd house early in your childhood. Even if you are aware of it or not, your family influenced you on how to view love and relationships (for good or bad).')),
    ('Venus', 3): ('S24 pp.18-19',
        ('Venus – When Venus is in your 3rd house in Vedic astrology your passion goes towards the 3rd house. You are passionate about your efforts, communication, younger siblings, technical skills, and movement.\n'
         '\n'
         'Creative with Hands – Venus gives creativity to the native based on its position. In the 3rd house, you are creative with your hands. You may be a painter, artist, crafter, sewer, or knitting. You are very creative when you work with your hands. You like to embellish your craftwork with color and beauty.\n'
         '\n'
         'Beautiful Hands – You are blessed with beautiful hands. If you are a woman, you love getting manicures. If the 10th lord influences the 3rd house (positioned, aspect, or conjunct). You use the beauty of your hands in your career. You could be a hand model or even a manicurist.\n'
         '\n'
         'Learn about Love – You learn about love, romance, and relationships through your younger siblings, movies, Television Shows, neighbors, and social media (Youtube, Facebook, Twitter, Instagram act.)\n'
         '\n'
         'Communications/Writing – Your handwriting is very pretty. You may be a writer of poetry, love letter, romantic novels, or have a blog that focuses on love and relationships. You love communication with loved ones, especially your spouse. You are constantly calling and communicating with your significant other.\n'
         '\n'
         'Transformations – Venus is the planet of transformation. The planet Venus relates to the dead (Venus). This goes back to the ancient mythology of Venus. In mythology, Venus died and was brought back to life. Being brought back from the dead relates to being regenerated and renewed after feeling dead (depressed, sad, defeated).\n'
         '\n'
         'You can be transformed (brought back from the dead) through your younger siblings (3rd House). When you are feeling dead, and your batteries need to be recharged your younger siblings can help you feel restored and renewed.\n'
         '\n'
         "Wife – Venus is the wife in a man's chart. Its position can indicate where a male will meet his wife or significant others. With this position, you may meet your wife through younger siblings, social media, or short journeys (trips to the store or anywhere close to the home), at the movies, or a sports game.")),
    ('Venus', 4): ('S24 pp.20-21',
        ('Venus – When you have Venus in the 4th house in Vedic astrology your passion goes toward the 4th house. You are passionate about beautifying the home, your homeland, mother, comforts, and having a peaceful mind and disposition.\n'
         '\n'
         'Beautify the Home – Venus in the 4th house give you artistic talent with decorating your home and personal space. You love to beautify your home with color and flare. Decorating your home with colorful painting, home décor, craftwork, art, pictures, paintings is an enjoyment. When people come into your home it is beautiful and welcoming. You grew up in a loving and peaceful home. You love taking the time to make your home appealing and pleasant. At work, you love decorating your cubicle, office, locker, or any personal space you have at work.\n'
         '\n'
         "Mother – Your mother is very creative and beautiful. Your mother inspired you with creativity. Growing up in the mother household, the Venusian energy colored every room in the house. The home was beautifully decorated and appealing to the eyes. Your mother could have been an artist, painter, interior decorator, musician, artist, or worked with women or women products (perfumes, scented oils, women's clothing, or any women affairs).\n"
         '\n'
         'Loving Heart – You have a loving heart. Your love radiates and shines drawing other people to you.\n'
         '\n'
         "Wife – Venus indicates the wife in the male's birth chart. Venus in the 4th house signifies that a male will meet their wife at home, through his mother, in their town or city.\n"
         '\n'
         'Marriage/Relationships – Venus is the karaka of marriage, for both men and women. If you have Venus in the 4th house your mother can get involved in your marriage or relationship. This can be for good or bad. On a positive note, the mother can be highly supportive of your marriage and may have been the one who introduced, you to your spouse. On a negative note, if Venus is damaged in the 4th house, your mother can interfere in your relationship.')),
    ('Venus', 5): ('S24 pp.22-23',
        ('Venus – When Venus is in the 5th house in Vedic astrology; you are passionate about romance, fun, creativity, children, speculation, education.\n'
         '\n'
         'Creativity – Venus is the planet of creativity in the house of visual creativity. You have great creative talents. You have a passion for the visual arts (pictures, painting, drawing, artwork). You may also be an artist who loves to devote time to your visual creativity. Venus in this house can also influence the native to pursue the art of stage performance (5th house). You may be an actor, musician, singer, or stage performer.\n'
         '\n'
         'Where You Meet Her – Venus is the wife in a males chart. If you are a male, you will meet your girlfriend, wife, or significant other anywhere there is entertainment and fun. This could be at a club, party, festival, carnival, sports game. You also have good luck meeting a romantic partner in these places.\n'
         '\n'
         'Children – You are passionate about your children (especially your first-born child). Children bring a lot of love, inspiration, and joy into your life. Your children are very beautiful and can be profoundly creative.\n'
         '\n'
         'Transformation – When you are feeling defeated, sad, or depressed your children can help uplift your spirits. Also, having fun, engaging in a creative project, or watching a movie can bring you out of the slums.\n'
         '\n'
         'Education – A good education is of utmost importance. Venus in this position gives you a desire to pursue higher education. You love learning and are passionate about feeding your intellectual mind.')),
    ('Venus', 6): ('S24 pp.24-25',
        ('Venus – If the planet Venus is in the 6th house in Vedic astrology. You are passionate about work, service, health, and everyday mundane life. The 6th house is the very first dusthana house. The dusthana are the 6th, 8th, and 12th houses. These are considered the houses of suffering and can bring obstacles to the Venusian energy.\n'
         '\n'
         'Career – Since the 6th house related to the everyday work routine (your job or career) and Venus represent beauty. You may have a job working with feminine or beauty products. You could work with cosmetics, perfumes, hair products, lotions, soaps, essential oil. Makeup, colorful clothing, or fabrics. You will also be dealing with a lot of women or feminine energies in the work environment. You may work in an office with mostly women. These positions can also give a job working in social service because of Venus about compassion.\n'
         '\n'
         'The Less Privileged – You have a soft spot in your heart for the underdog. You have a passion for helping less privileged people, suffering, or in need of help. The 6th house in the house of suffering and you love spreading your Venusian energies as a beacon of healing light.\n'
         '\n'
         'Wife – A male can meet his wife on the job. A work environment is a good place for a man to meet and engage with women.\n'
         '\n'
         'Marriage – Venus is the indicator of marriage for both men and women. Your marriage life can be hard. There can be struggles and obstacles in the marriage. If other planet alignments support it, the marriage can break. However, this is not the case in all charts. Marriage life can be hard; however, it can make the marriage stronger when difficulties are overcome.\n'
         '\n'
         'Transformation – When you are feeling depressed, sad, or unhappy, helping other people can lift your spirits and renew your soul.')),
    ('Venus', 7): ('S24 pp.26-27',
        ('Venus in the 7th house in Vedic astrology gives you a deep passion for a romantic relationship. This is a very good position for Venus. The planet Venus feels at home in its house of Libra. If the planet is in good dignity, it brings good results to the marriage life.\n'
         '\n'
         'Love Passion – You are passionate about love and enjoy being in a relationship. You feel as if you were born to be in a loving relationship with the right person. When you are involved in a marriage or relationship you love the person who you are will deeply. You love spending romantic moments with your spouse or lover. You are the happiest in a relationship and need that connection to feel alive.\n'
         '\n'
         'Learn about Love – You learn about love and by being in romantic relationships or marriage. Also, dealing with other people helps you learn about love and relationships.\n'
         '\n'
         'Spouse – Venus blesses you with a good-looking spouse. Your spouse or partner is very attractive. Your spouse will energize and start your creative and artistic abilities. Your spouse is romantic and magnetic. Spouse gets a lot of attention from other people. Other people are drawn to your spouse like a moth to a flame. A spouse can be creative and can express their love for you poetically and artistically.\n'
         '\n'
         'Transformation – When you are feeling lonely, sad, defeated, at rock bottom, or dead inside. Your spouse can raise you from the dead (Venus).\n'
         '\n'
         'Career Activation– The 7th house is the highest of your career (10th from the 10th). Once you get married, your career becomes activated. If you feel that things are not taking off for you career-wise, marriage will activate progress in your career. Once married you may get a promotion, a new job, or start your own business.')),
    ('Venus', 8): ('S24 pp.28-29',
        ('Venus in the 8th house gives you a passion and desire for sexual relationships, hidden information, esoteric knowledge, research. Your passions are related to 8th house significations.\n'
         '\n'
         'Secret Love – The 8th house is related to secrets and Venus indicates love relationships. When the planet of love comes into the house of secrete, you may have secrete love affairs. If married, you may have a lover that you keep hidden from your partner. If you are single, you like to keep your love life hidden away (private)\n'
         '\n'
         'Sexual Passion – You have a profound passion for sex. You are a passionate lover. You love sexual explorations. If the 12th lord (bedroom pleasure) aspects, conjunct, or is positioned with Venus. Your sexual passion is intensified. Also, the planet Mars in this house can heighten your sexual desires. You can be wild in bed and take your lover by surprise.\n'
         '\n'
         'Esoteric Knowledge – You love exploring the hidden side of life. Subjects like metaphysics, new age, occult, mysticism, sorcery, magic, astrology, numerology are of interest to you. Any hidden or secret information sparks your interest.\n'
         '\n'
         'Wife – A man will meet his wife in a secret location. You can also keep your wife secret and may not reveal too much information about her to others. Your wife can be very secretive and may not want you to reveal too much information about her.\n'
         '\n'
         'Marriage – Marriage can go through many sudden ups and downs. The 8th house is the house of sudden things. There can be a lot of surprises and unseen events that take the marriage by storm. Marriage life can be difficult with this position because so many hidden and unseen thing disrupts the marriage.')),
    ('Venus', 9): ('S24 pp.30-31',
        ('Venus – When Venus is in the 9th house in Vedic astrology you are passionate about the 9th house significators. Your passion goes towards higher education, long-distance travel, religion, spirituality, and your belief system.\n'
         '\n'
         'Father – Your father is very creative. Father may have been an artist, painter, musician. Father is very attractive and draws others to him.\n'
         '\n'
         "Higher Education – You find pleasure, happiness, fulfillment in higher learning. Perusing your master's degree, Ph.D., or taking a Doctoral program can bring happiness to your life.\n"
         '\n'
         'Long-Distance Travel – You are passionate about long distant travel. You may rent an RV and go on a road trip traveling around the country. Or you take time off and travel around the world visiting a foreign country. Long-distance and foreign travel spark your creativity and inspires you with hope and possibilities. You are well-traveled because you get so much pleasure from seeing the world.\n'
         '\n'
         'Marriage – Venus is the karaka of marriage for both men and women. If Venus is in your 9th house, the marriage life is fortunate.\n'
         '\n'
         'Wife – In male charts, you will meet your wife on a long distant or foreign trip. The wife is spiritual, compassionate, and educated. If you are a male, you may have a long-distance relationship with your wife before being married.\n'
         '\n'
         'Buttocks, Thighs – The 9th house represent your buttocks, thighs, and Venus is beauty. Natives with this position have beautiful buttocks and attractive thighs.\n'
         '\n'
         "Sister-in-Law – The 9th house is our spouse's youngest siblings and Venus relates to women. So, when Venus is in your 9th house it represents your spouse's younger sisters (your sister-in-law). Your sister-in-law is very attractive, social, and fun. She also has creative talents.\n"
         '\n'
         'Grandchildren – The 9th house relates to your grandchildren. Venus blesses you with beautiful grandchildren who bring joy and love to your life.')),
    ('Venus', 10): ('S24 pp.32-33',
        ('Venus – When Venus is in the 10th house in Vedic astrology your joy and pleasure is in the 10th house. You are passionate about your career, government, authority, the outside world, and your Dharma (performing actions).\n'
         '\n'
         'Creative Career – The focus of your career is creativity. A career in the arts as an artist, actor, designer singer, interior decorator, musical bring happiness and joy. You have to express creativity in your career to have fulfillment. If you are working in a career that is not utilizing your marvelous creative talents. You will feel like you are not living up to your potential.\n'
         '\n'
         'Authority – You are passionate about gaining authority and being in a leadership role. You may be a manager or supervisor in a Venusian career. A manager of a clothing store, cosmetics, beauty supply, women products, or perfumes. Any career that relates to femininity, art, and beauty is where you can have authority (10th house).\n'
         '\n'
         'Society – You find joy, pleasure, and fulfillment being out and about in society. You love the outside world. You are happier when you are in society, instead of being confined at home. You desire a public status and find fulfillment when society recognizes yours for accomplishments.\n'
         '\n'
         'Government – The 10th house represents the government. You are passionate about government and politics. This passion can lead you to have a career working for the government.\n'
         '\n'
         'Women – Venus is the karaka of women, and the 10th house is your career. You work around or with a lot of women in your career. If you have an office job, your coworkers are mostly women. If your coworkers are men, they will have feminine personalities or be very artistic.\n'
         '\n'
         'Wife – In a males chart, you could meet your wife or significant others at work. Since Venus brings women to your work environment, one of your coworkers or employees if you are a business owner could be that special someone. Your wife is career-oriented and authoritative.\n'
         '\n'
         'Beautiful Knees – Venus is beauty, and the 10th relates to your knees. The planet Venus blesses you with attractive knees. Your knees can be very well-formed and prominent.')),
    ('Venus', 11): ('S24 pp.34-35',
        ("Venus – When Venus is in the 11th house in Vedic astrology you are passionate about your hope, wishes, desires, friendships, and extra income. This is one of the most favorable positions for the planet Venus. The planet of desire in the house of financial gains can give favorable results. The 11th house is the original house of Saturn. The planet Saturn is friends with Venus. So, Saturn will try to fulfill all of Venus's hopes and wishes.\n"
         '\n'
         'Hopes/Wishes – You are passionate about your hopes, wishes, dreams, and desires. Fulfilling your goals in life brings you joy and happiness.\n'
         '\n'
         "Service – You have a humanitarian heart. It brings you great joy when you help less fortunate people. You may fight for women's rights or work for a women's organization.\n"
         '\n'
         'Friends – Regardless if you are a male or female you have more female friends. Also, your social network circle consists of more females. Friends are very charming, creative, and compassionate.\n'
         '\n'
         'Extra Income – Extra income can come from a business related to female products or products with feminine energy. Selling perfumes, hair products, make-up, lotions, cosmetics, can bring in extra income. Anything related to women (Venus) can bring financial gains in your life. Also, a creative endeavor can bring in wealth.\n'
         '\n'
         'Eldest Child – The 11th house is your eldest child spouse (it is the 7th house from the 5th) Your eldest child will have a very attractive partner.\n'
         '\n'
         'Where you meet her – If you are a male, you will meet your wife at social events. You could meet her at an organization, community event, business meeting, concert, fundraising or, charity event. You meet your wife anywhere there are crowds and a lot of people around. With this position men have good luck meeting a significant other in a social setting.\n'
         '\n'
         'Wife – The wife brings to the marriage financial gains and fulfillment of wishes.')),
    ('Venus', 12): ('S24 pp.36-37',
        ('With Venus in the 12th house in Vedic astrology your passion and desires is towards the 12th house. You are passionate about foreign travel, bedroom pleasures, isolated places, sleep, your creative imagination, and a fantasy lover.\n'
         '\n'
         'Love: The 12th house relates to losses and escapism. With Venus in the 12th house, you could lose your lover, or you may escape the relationship. You could decide that you no longer want to be in a relationship and break up with your significant other.\n'
         '\n'
         'Meet Wife: If you are a man, your will meet your wife in a place of isolation or on a foreign vacation. Men have good luck meeting women while foreign traveling or in private locations.\n'
         '\n'
         'Spirituality: You love spirituality and can be a devoted spiritualist.\n'
         '\n'
         'Beautiful Feet: Venus is a planet of beauty. Natives with this position have beautiful feet. A regular pedicure can enhance the beauty of your feet.\n'
         '\n'
         'Spend on Luxury and Pleasures: You love to spend money on pleasures and luxuries. Anything that brings you pleasure, joy, and comfort is a necessary expense.\n'
         '\n'
         'Foreign Love: You may marry or be in a relationship with someone from a foreign country or foreign birth. You can marry someone who is of a different race or culture.\n'
         '\n'
         'Marriage: Bedroom pleasures are an important part of the marriage.\n'
         '\n'
         'Love Bedroom Pleasures: You are passionate about bedroom pleasures. Having an active sex life brings you much joy and happiness.\n'
         '\n'
         'Private Social life: Venus is a very social planet, and the 12th house is isolated. You love social gatherings in private places (in the home or remote location). You also prefer very few people at social gatherings.\n'
         '\n'
         'Passion for Isolation: You love being in places of isolation. You can get In-tune with your creative imagination when you are alone.\n'
         '\n'
         'Fantasy Lover: If your Venus is in the 12th house, you have a fantasy lover. In the imaginary world of your conscious mind, you love spending time with your lover. You may have a crush on a celebrity, who you fantasize about frequently.\n'
         '\n'
         'Love Foreign Travel: You have passionate about foreign travel. Taking a trip around the world inspires you with creativity.\n'
         '\n'
         'Unsatisfied with Lover: You seem to always be unsatisfied with your lover. Your lover could be the ideal partner, but you always seem to want more or someone different.')),
    ('Saturn', 1): ('S25 pp.2-3',
        ('Cold Personality – The individual comes across as cold (Saturn) to other people.\n'
         '\n'
         'Poverty Brain/Mind – The 1st house represents the mind. Saturn brings a poverty thinking pattern. It does not matter how much money the person has the native will feel like they are in poverty. The native may choose to live in poverty and wear old and worn-out clothing when they have money in the bank.\n'
         '\n'
         'Sorrow Mind – A person brings sorrow (Saturn) on themselves (to the mind). They become pessimistic about everything and have a glass and half-full outlook on life.\n'
         '\n'
         'Karma of Physical Body – A person will have to deal with karma (Saturn) of the physical body. The person can have physical ailment like arthritis, joint issues, injuries.\n'
         '\n'
         'Older Appearance – Your appearance will look older you may grey faster, get wrinkles faster. Even as a child or younger adult you will seem like your older. There is a maturity to you that is far beyond your years. You can naturally feel old (Saturn).\n'
         '\n'
         'Delay in Marriage – Saturn in the 1st house can delay Marriage.\n'
         '\n'
         'Manual Jobs – A person will do more manual jobs that require the physical body.\n'
         '\n'
         'Walk Slow – Natives with Saturn in the 1st house tend to walk slow and move slow (Saturn). Saturn is a slow-moving planet, and it slows down the movement of the physical body.')),
    ('Saturn', 2): ('S25 pp.4-5',
        ('Family Karma – You feel some karma and sorrow from family (2nd House). There can be a detachment from the family because the planet Saturn creates a separation. The 2nd house is an indicator of early childhood. Growing up in the home may have been difficult and there were a lot of struggles especially financially for your parents. When you were a small child you may have had many hand-me-downs. The family can come across as cold and distant. You can also leave the family early in life with this position. Yogananda has Saturn in 2nd house and he Left his Family Early to practice spirituality.\n'
         '\n'
         'Early Childhood – Growing up there may not have been much money or funds available, even if you had rich parents, they could have been cheap frugal.\n'
         '\n'
         'Family and Wealth – Family and wealth relationships form with time.\n'
         '\n'
         'Voice – You have trouble being heard; Saturn suppresses your vocals you can have trouble with your vocal cords.\n'
         '\n'
         'Throats – You have health issues with your throat. You can have thyroid issues, sore throat, Strep throat, or tonsillitis problems. Any issues with the throat are Karmic because Saturn is a heavy karmic planet. Having these problems help you burn away your karma and pay back your karmic debt from a past life.\n'
         '\n'
         'Face – Saturn represents old age; with Saturn in the 2nd house, it gives the native an older appearance. You can wrinkle prematurely. There may be a part of your face that always had an older or mature appearance. You may and old eyes as a young child. Since Saturn is a dry planet you can also have dry skin on your face.\n'
         '\n'
         'Stingy and Cheat – You can often come across as being a little stingy and cheap with your resources because you feel money can easily slip from you so you trying to hold on as much as your can. You feel the need to always want to save money because you feel the money can go from you at any time, this is the Karma of Saturn, It is hard for you to save money early in life, it may seem there is a hole in your pocket and you just can hold on to money. As you mature that hole in your pocket will seal up and you will be able to save money and hold on to it longer.')),
    ('Saturn', 3): ('S25 pp.6-7',
        ('Hand, Shoulder, Ears, Neck – The 3rd house in Vedic astrology represents the hands, shoulders, ears, and neck. Saturn represents chronic diseases. Saturn in 3rd house brings karma to the health of this house. You have health issues with these regions of your body. You may have problems with hearing and suffer from ear infections, especially in early life. You can also have pain in the shoulder and hands. Your neck can bother you; regular massage and physical therapy can be needed to loosen up the tensions in your neck and shoulders.\n'
         '\n'
         'Communication – You have a hard time communicating freely with Saturn in the 3rd house. You may prefer to write down your thought and ideas instead of expressing yourself verbally. You find it difficult to communicate and put your ideas in words. You can often hesitate to speak since Saturn suppresses verbal communication. However, once you find the right words your message can come across as cold (Saturn) and blunt and may offend others even though you do not mean to do so.\n'
         '\n'
         'Skills – The 3rd house is an indicator of your skills which are also developed in time.\n'
         '\n'
         'Sibling – You have karma with a sibling. There can be separation from siblings, especially the youngest sibling. You have an estranged or distant relationship with siblings. There is a disconnect with siblings. However, with time a connection can be established.')),
    ('Saturn', 4): ('S25 p.8',
        ('Mother – If you have Saturn in the 4th house in Vedic astrology, the planet Saturn brings a karmic relationship with your mother. There can be an estranged or distant relationship with the mother, or you may feel a detachment from her. Saturn is a cold planet, the mother comes across as cold, stern, and strict. Growing up there may have been a lot of rules you have to follow that limited your freedom. You may have had a strict curfew or had to do an excessive number of chores around the house.\n'
         '\n'
         'Leave Home – Due to strict rules or limitations in the home environment, the native can leave the home and family early in life (early teens). The planet Saturn makes the native feel uncomfortable and restless in the home. The strong feeling of uneasiness can influence the native to venture out on his or her own.\n'
         '\n'
         'Acquire Property – You feel uncomfortable if you do not have your property. When you have Saturn in the 4th house, you must acquire land, property, or real estate, or some type of fixed asset; if not you will feel uneasy. You feel awkward renting property and you feel it necessary to own because you may feel that you could be homeless this is the karma of Saturn in this position.')),
    ('Saturn', 5): ('S25 p.9',
        ('Speculative Gains – The native is hesitant to invest in speculative gains like stocks, gambling, or business investments. If you have Saturn in the 5th house in Vedic astrology you should not be gambling or investing in stocks because karma is related to gambling. The native can lose money in speculative investments.\n'
         '\n'
         "Children Karma – There is karma related to children, there may be a delay in having children. The planet Saturn suppresses the house it is positioned in. Children can come later in the native's life. Saturn in this position can also limit the number of children. Natives with Saturn in the 5th house become better parents in time, even if children come late in life.\n"
         '\n'
         'First Child – The 5th house represents your first child. When the planet Saturn is in the 5th house it influences the personality and physique of your 1st child.\n'
         '\n'
         'First Child Mature – The 1st child will be mature and act older for his or her age. Even at a young age, your first child will seem like an old soul, very mature and responsible.\n'
         '\n'
         "Parenting – When Saturn is your 5th house, the native will not be the best parent to their children until later in life, even if the native has children in their mid-30's, they will be a better parent to their children later in life.\n"
         '\n'
         'Stomach – The 5th house signified the stomach. Saturn brings health issues to your tummy area. You have stomach troubles or issues with that part of your body.')),
    ('Saturn', 6): ('S25 p.10',
        ('Suppress – Saturn in the 6th house in Vedic astrology is one of the best positioned for Saturn. Saturn is a malefic planet. Malefic planets in dusthana houses (6th, 8th, and 12th) give good results. The planet Saturn suppresses the significance of the 6th house. Saturn suppresses your enemies, debts, short-term illness, litigation, rivals, and prarabdha karma.\n'
         '\n'
         'Mundane Life – The 6th house represents everyday work life.\n'
         '\n'
         'Service – With Saturn in the 6th house, you will serve other people by dealing with the sorrow and struggles of others. You feel you need to work and provide some type of service to everyday people or the underdog.\n'
         '\n'
         'Everyday Work Life – The individual works hard on their job. The native can work long and exhausting hours with little or no breaks. The native can be a workaholic because one feels overly responsible when it comes to their job. The native must remember there is more to life than the everyday work routine. However, the influence of Saturn is so strong on the 6th house when it comes to working; the natives can easily and unintentionally bury themselves in work. This is magnified if the native is going through their Saturn Dasha.\n'
         '\n'
         'Karma Chronic illness – You will have some prarabdha karma (unchanged karma) related to a chronic illness. Because the 6th house a friendly house of Saturn (original house of Virgo) you will have the power to overcome chronic illness and disease because Saturn destroys the significations of the 6th house (health issues) of the 6th house.\n'
         '\n'
         'Health – The 6th house represents the digestive tract and small intestine. The planet Saturn can bring chronic illness and health problems to your digestive tract and small intestine.')),
    ('Saturn', 7): ('S25 p.11',
        ('Directional Strength – Saturn has directions strength (Dig Bala) in the 7th because Saturn is exalted in the sign of Libra. The 7th house signifies marriage and long-term partnership. Saturn represents duty, commitment, and service. Saturn in the 7th house signifies one must have these qualities in marriage.\n'
         '\n'
         "Saturn loves to deal with and work with other people, and the zodiac sign Libra is all about others. This is why Saturn is strong in the 7th house. Saturn wants to make sure everything is done equally, and it's all about equal balance; similar to the scale associated with the zodiac sign of Libra.\n"
         '\n'
         'Karma – Saturn is strong in the 7th house but there is karma one must pay back with spouse (partner). Since Saturn also represents longevity one may have a difficult relationship with the partner, but the relationship is prolonged (Saturn) to pay back past life Karma (Saturn).\n'
         '\n'
         'Older Spouse – The partner can be older and often seem cold and detached. The spouse has a serious personality and can be very responsible if Saturn is not afflicted.\n'
         '\n'
         'Responsibility – In marriage, Saturn brings responsibility and a serious attitude in the marriage Saturn looks at the glass half empty and may feel the responsibilities of marriage is too much of a burden. Saturn also represents work; this means one must put the work in the balance out the scale (to balance karma). Saturn in the 7th house can be a wonderful placement as long as you put the work, commitment into the marriage and do not let the struggles defeat you\n'
         '\n'
         'Maternal Grandmother – There is karma with the maternal grandmother. The maternal grandmother may have passed away or you may have never known her. There can also be distant or detached relationships with the maternal grandmother.')),
    ('Saturn', 8): ('S25 p.12',
        ('Karaka – Saturn is the karaka (significator) of the 8th house. Many of the significators of the 8th house relate to the planet Saturn.\n'
         '\n'
         'Suppress – If you have Saturn in the 8th house it will suppress the qualities of this house. Sudden events, death, long term illnesses are suppressed when Saturn is positioned in the 8th house:\n'
         '\n'
         'Joint Assets – Saturn blocked joined assets from spouse. When married the native may have to bear the financial responsibility with no support from the spouse. The native may be the breadwinner. However, if money is contributed from the spouse it may not be enough to cover the bills. If the spouse is wealthy, he or she may be frugal with their money.\n'
         '\n'
         'Long Life – Saturn slows down death in the 8th house. Native with this position will live a long time. Anytime Saturn is pointed or aspect the 8th house it prolongs life for the native. Because the planet Saturn is a slow-moving planet, it delays (slow down) death in the 8th house.\n'
         '\n'
         'Private Parts – The native can have a problem or chronic issues with the external private parts; the vagina for women and the genitals for men. A chronic illness could be a urinary or yeast infection.\n'
         '\n'
         "Cold In-laws – If married the in-laws (spouse family) may seem cold towards you. The energy of Saturn is cold, and it influences the spouse's family to act cold towards you.")),
    ('Saturn', 9): ('S25 p.13',
        ("Luck – Saturn is a malefic planet and the natural karaka of the 8th and 12th house. The 9th house is the highest of luck and fortune. The 9th house is the most potent trikona house in one's birth chart. Saturn in the 9th house suppressed ones good luck and fortune. Things will not come easy to individuals with this position. The native will feel as if lady luck is not on their side, or they have to work harder than others to have good fortune.\n"
         '\n'
         'Karma – The native can have an estranged relationship with the father. If the father is in the native life, he may seem cold toward you.\n'
         '\n'
         "Father – Father is strict and disciplined. Father may have had you when he was older (Saturn). Father could have been in his 40's or 50's when you were born.\n"
         '\n'
         'Chronic Illness – The native can have issues with the thighs and buttocks.\n'
         '\n'
         'Religions – The native will understand religion and spirituality better later in life. Wisdom comes slowly as one ages and mature.')),
    ('Saturn', 10): ('S25 p.14',
        ('Serve Government – If Saturn is in your 10th house in Vedic astrology, you will give service (Saturn) to the government (King 10th house). You are attracted to any positions related to government or politics. You can work in this type of field long term especially if you are going through the 19-year Dasha of Saturn.\n'
         '\n'
         'Career Karma – You have karma to pay back in your career (10th house). You have to work harder than others to succeed in your career. Saturn in the signification of hard work and discipline; Therese are the qualities that will be required to climb the corporate ladder or be self-made. Success will not come easily but career status can be accomplished with diligence and patients.\n'
         '\n'
         'Image – The 10th house represents your image (how other people see you). With Saturn in 10th house, your image and reputation can be damaged or tarnished.\n'
         '\n'
         'Strict Job Rules – There can be strict rules and policies at work, especially if one has a government position like security checks a lot of structures in their work environment.\n'
         '\n'
         'Routine Work – You can have a strict routine at work or may have to constantly replicate a task on your job. You could have a job that requires you to perform the same task over and over again since Saturn is the karaka of systematic routines.\n'
         '\n'
         'Knees – The 10th house signifies the knees and Saturn represents health issues. With Saturn in the 10th house, you will have problems with your knees.')),
    ('Saturn', 11): ('S25 p.15',
        ('Moolatrikona – The 11th house is a natural Moolatrikona placement for Saturn. The 11th house is the original sign of Aquarius. The planet Saturn feels comfortable in this house. Saturn can give good results in this house if it is in good dignity.\n'
         '\n'
         'Elder Sibling – If you have Saturn in the 11th house eldest sibling is an older mature figure. The eldest sibling can be a mother or even a father figure. When you have the planet Saturn in the 11th house in Vedic astrology there is karma with an elder sibling. There can be an estranged or distant relationship with your eldest sibling. Saturn is a cold planet, and it can influence your eldest sibling to act cold and detached toward you. The eldest sibling is also serious-minded and responsible.\n'
         '\n'
         'Friends – Your friends have the qualities of Saturn; they are disciplined, practical, and hardworking. However, it may be difficult to connect emotionally with friends. Because of this, friendship will often seem distant and disenchanted. Due to the distance, Saturn creates and the feeling of not being able to connect. You may have very few friends but you cherish the ones you have.\n'
         '\n'
         'Service – Saturn in the 11th house can indicate that you give your service to humanitarian causes. The native may work for an organization, company, or enterprise that fights for the underdogs or help small communities or a particular group of people. Regardless, the focus of your service is to give your time to organizations and large groups of people.\n'
         '\n'
         'Health – Saturn is the karaka of diseases and health issues and the 11th house is the significator of the calves and shins (front of the bottom leg). The native can have problems with the bottom of the leg, and a section of the leg that is below the knees.')),
    ('Saturn', 12): ('S25 p.16',
        ("Sleep – If you have Saturn in the 12th house in Vedic astrology your sleep can be disturbed. It can be difficult for you to get a good night's rest. You may toss and turn for hours trying to fall asleep or it may take a long time for you to fall asleep. You may also wakeup throughout the night sporadically. You never feel fully rested and you can still be tired in the morning. In extreme cases, you may take sleeping pills or any type of sedative to get to sleep.\n"
         '\n'
         "Feet – Saturn is the indicator of chronic illnesses. The 12th house represents the feet. Saturn in the 12th house can cause problems with the feet. You can have problems with any part of the feet below the ankles. You can have problems with a particular foot or both feet. You can have an athlete's foot, bunions, or blisters.\n"
         '\n'
         'Isolation – Because of the karma accumulated from a past life. You can be placed in an isolated environment (hospitals, jails, asylums). Isolation can help you pay back and burn away your karmic debt. You may choose to be in seclusion to get in touch with your spirituality. Taking a pilgrimage to secluded places can help you developed spirituality.\n'
         '\n'
         'Service/Job – Saturn in the 12th house can influence a native to give their service to places of isolation and confinement. You can do charity work or have a job working in a hospital, prison, or asylum. The 12th house is also an indicator of foreign lands. You may work for a foreign company.\n'
         '\n'
         'Foreign Lands – You have karma in foreign lands that can frustrate you. You have karma debt to pay back in a foreign country or foreign travels may b delayed.\n'
         '\n'
         'Paternal Grandmother – There can karma with the paternal grandmother. Your paternal grandmother may have died before you were born.')),
    ('Rahu', 1): ('S25 p.17',
        ('Rahu is a poser, a deceit and a fraud. Rahu is a master of illusion and mirage. Modern day view of Rahu is that of a visionary, entrepreneur and out-of-box thinker. With Rahu in First House the native is great at putting on a show, an illusion about himself that enthralls most if not all. The native is mostly an extrovert who loves the good life. He/She is able to charm his way out of troubles and win trust of others with utmost ease.\n'
         '\n'
         "Rahu is an expert magician and illusion artist. Rahu in First House gifts person with ability to think out-of-box. Rahu's methods maybe illegal and unethical but results are quite profitable. With Rahu in First House a native is able to think like a visionary. Native is able to earn a fortune from a revolutionary idea. Natives with Rahu in First House can put on a show which very few others can do. They are easily able to win trusts of people with their charm and illusion powers. This in turn can earn them a fortune.")),
    ('Rahu', 2): ('S25 pp.18-19',
        ('The 2nd house in Astrology deals with Family Lineage, face, expression, speech, taste, food, accumulated wealth, and mathematical ability. Rahu wants to go against social norms to attain things, it will break the traditional rules and will rebel.\n'
         '\n'
         'Therefore if a person is born with Rahu in the 2nd house, it can give an unusual and unorthodox environment in the early stage of his life. It can give parents and siblings who will be very different from others. If Rahu is afflicted then it will separate you from your lineage.\n'
         '\n'
         'Rahu in 2nd house in terms of finance and career can be considered a good position. This makes the person focus on accumulating money. Rahu does not follow rules, so there are chances of making black money, or the person will not pay taxes, or he can lie or deceive people to make his profits.\n'
         '\n'
         'The 2nd house depicts a face, therefore Rahu here can give attractive but new looks, an impressive speech, and a good bank balance if there are strong Dhan yogas as well. Such people prefer to take livelihood related to Mathematicians, astrologer, researchers, singers, and musicians.\n'
         '\n'
         'Since the 2nd house planet tells about the way the person will accumulate money, so Rahu position gives us options like the I.T. industry, the food industry, and the pharmaceutical industry. If there are afflictions then such a person will earn through the cigarette, drug, or alcohol industry.')),
    ('Rahu', 3): ('S25 p.20',
        ('Rahu represents illusion, foreign lands, foreign things (foreign as in unknown things. So, for someone living in Punjab, culture and rituals of Kerala is also unknown and hence Foreign), Drugs, Medicines, any type intoxication, fame, wealth, success, obsession, past-life left-over karma, movies, television, online world, cheating, imagined fears, unusual things, unique things, creativity, rule breaker. Rahu also blows things out of proportions.\n'
         '\n'
         '3rd house - It is house of your communication skills, neighbors, short distance travels, younger siblings, marketing, announcements, collecting information, hobbies and skills, self-efforts, business, courage etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non- Rahu.\n'
         '\n'
         "Rahu in 3rd house makes someone an excellent communicator. They can be fraudulent too in their communications. That's why they become smart salesman, marketing executives and businessman who can sell you anything. They are excellent with their writing skills too. They are very good with creating illusion with their hands, means magicians. They are workaholics. Relationship with younger siblings may suffer due to the malefic nature of Rahu. 3rd house is also a house of ego. So, they can have the heftiest of Ego.")),
    ('Rahu', 4): ('S25 p.21',
        ('4th house represents your home, home environment, homeland, mother, nourishment, childhood friends, peace of mind, conveniences etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect He is unable to impact 7th house from its place as Ketu is sitting there which is the other axis of Rahu and represents all those things which are non-Rahu\n'
         '\n'
         'So, when Rahu comes in 4th house of home, land etc., these people become highly obsessive about land, home and real estate. They easily go into real estate business. To get property these people can even do fraudulent activities. It may be that these people have a home at foreign lands or they are raised by foster parents. It may also be that they are sent at a foreign place early in their childhood. Their early education is impacted by malefic Rahu. They can find peace of mind in foreign lands.')),
    ('Rahu', 5): ('S25 p.22',
        ('5th house represents Creativity, Romance, Happiness, Hobbies, Children, Innovation, Sports, Movies, Stock Trading, Gambling and Betting, Risk Taking Ability, Education, Ancient Texts etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non-Rahu\n'
         '\n'
         "So, when Rahu comes in 5th house, this is 1st of the position where Rahu can make someone celebrity. As 5th house is house of Media, Cinema, Sports and Creativity and Rahu only knows exploding things out of proportion, this position gives unimaginable fame to someone in these fields. This position makes someone highly creative in whatever field they are. It won't be wrong to say that they love lime-light around them. They love to have many kids and if they don't have, then they adopt anyone else's kid. This position also gives huge interest in reading ancient texts and studies. It can also make someone a stock-broker. As 5th house also relates to Romance and Love-life and Rahu explodes everything, here Rahu gives the person lots of love affairs")),
    ('Rahu', 6): ('S25 p.23',
        ('6th house is 1st of Dushthana Houses (houses # 6, 8 and 12) and 2nd of Upachaya Houses (houses #3, 6, 10 & 11), 6th house represents things like diseases, debts, obstacles, enemies, disputes, competitions, litigations, under privileged people, pets, daily routine life, colleagues at work place etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non- Rahu\n'
         '\n'
         'Now, Rahu is at the place where it wants to be. Rahu loves to deceive people and in the house of disputes and enemies, it gets ample opportunity to deceives enemies. Here, Rahu can make a person smart advocate very good doctor, and banker etc. As in all these fields Rahu gets every opportunity to deal with obstacles and deceive it. But at the same time, the person himself can not be reliable. As 6th house is house of divorces mainly they become divorce lawyers. It also shows that they can have some very rare type of diseases and they should always take a 2nd opinion on their illnesses.')),
    ('Rahu', 7): ('S25 p.24',
        ('7th house is house of market place, other people (masses), business partnerships, agreements, marriage, spouse, marital happiness etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non- Rahu.\n'
         '\n'
         'So, when Rahu comes into 7th house of business and partnerships, it makes a person very good businessman. These people can do anything to get success in business. As 7th house is also house of masses and public, so here Rahu gives extreme fame to person. In relations, the person never gets satisfied with their partner, they will have one or the other desire left to be fulfilled. This can also show that someone has foreign spouse or getting married in foreign lands. Also, this placement can lead to infidelity in relations')),
    ('Rahu', 8): ('S25 p.25',
        ('8th house is house of secrecy, occult knowledge, longevity, transformation, death and re-birth, in laws family, joint wealth with spouse etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non- Rahu.\n'
         '\n'
         'When Rahu is in 8th house, it makes a person highly obsessive about hidden knowledge and occult matters. This position can make a person very good occultist practitioner. Besides this, this position can also make someone a secret service agent or spy for government or in private detective services. As Rahu represents Foreign Lands and 8th house is in-laws family, this position gives in-laws in foreign lands. But over all great obsession for occult and research. They are the perfect mystics')),
    ('Rahu', 9): ('S25 p.26',
        ('9th house represents Higher Education, Philosophy, Religion, Law, Faith, Fortune, Gurus, Teachings of Father (as father is 1st Guru we get) etc.\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non-Rahu.\n'
         '\n'
         'So, now the Rahu is in the 9th house of religion, law etc. As always Rahu wants to achieve everything related with the house it is in, so here it wants to achieve all in fields of knowledge and education. They are obsessed for education. They can even become a religious Guru or even create their own religion. So, these people are rebellious against their own religion or any religion. They have extremely unorthodox religious views and they are not afraid to let the world know about their views. If not creating their own religion and becoming religious leader, then at least they give a thought about converting into different religion.')),
    ('Rahu', 10): ('S25 p.27',
        ('This placement brings good results in your career; gives you an inclination to earn fame, scale heights in career, improve your performance to reach the top position in your professional life and to get rewards and promotions. It will make you ambitious and Rahu will bless you to fulfil your desires. It also motivates you to develop your knowledge base, which advances your career. It makes pursue professional courses that will add to your job prospects and professional progress.\n'
         '\n'
         'The 10th house is related to your career and professional success; it indicates the type of profession you may be in, the amount of respect and honour you will earn, the popularity and fame you may get in life. It also gives an indication about your image in social circles; the responsibilities that would be entrusted on you and how you would handle them.\n'
         '\n'
         'You will find immense success in work or projects related to some distant places or foreign land. You may travel abroad for fulfilling your desires vis-à-vis professional excellence and success. There will be good prospects for you in MNCs. You may even achieve a lot of success in business, especially if you are in one related to export and import from a foreign land. You may expand your business in foreign countries with business tie-ups there.\n'
         '\n'
         'In terms of finances, there will never be any crunch of money at any stage of your life. Your finances will only grow and be stable. You may start earning early in life. After the initial years, around your mid-thirties, there will be good growth and earnings.')),
    ('Rahu', 11): ('S25 p.28',
        ('11th house represents Elder Siblings, Large Organizations, Huge Structures, Higher Goals and Purposes for the Universe, Network Circle, Entrepreneurship, Friends, Gains, Income and Earnings etc\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non Rahu\n'
         '\n'
         'So, now the obsessive Rahu is in 11th house of gains, earnings etc. As Rahu wants to gain everything, here it makes a person obsessive about money and gains. They have huge amount of income. Their network circle is too big which provides them continuous income and earning. Due to malefic nature of Rahu, relations with elder siblings may be spoiled. They may also find it hard to save money. It depends on malefic or benefic planet sitting with Rahu or the sign Rahu is in, which decides earning will stay or not. As Rahu represents illusion, in some signs and conjunctions, Rahu gives money because of cheating or fraud.')),
    ('Rahu', 12): ('S25 p.29',
        ('12th house is house of Losses, Expenses, Isolated Places, Spirituality, Foreign Lands, Foreign Companies, Imagination, Sub-Conscious Mind, Charity, Donation, Asylums, Jails, Hospitals, Hidden Talent and Secrets of Other World etc.\n'
         '\n'
         'One thing to always keep in mind with 12th house is that it basically remains the house of losses. So, whichever planet goes in 12th house, even exalted, is in the bucket of losses. Now, to gain out of any such planet, you need to put double effort in things related with that planet\n'
         '\n'
         'Aspect-wise, in Vedic Astrology, Rahu has 5th and 9th house aspect. He is unable to impact 7th house from its place as Ketu is sitting there, which is the other axis of Rahu and represents all those things which are non-Rahu\n'
         '\n'
         'So Rahu in 12th house, 1st of all gives obsession towards reaching foreign lands as Rahu represents Foreign Things and 12th house itself is foreign lands. Due to its malefic nature, Rahu takes the person away from his home into foreign lands. This position can also show someone who is spendthrift. This position can show different type of careers. But best indication is As 12th house is also a house of Spirituality, it also shows someone who is immensely obsessed about spiritual pursuits. The end result depends on the sign Rahu is sitting in and also conjunction of Rahu with other planets.')),
    ('Ketu', 1): ('S25 p.30',
        ("First House is the house of self. First House defines physical features and mental characteristics of a person. Ketu in First House gives rise to anti-social behaviour. Such natives prefer to be alone or remain detached from those around. Ketu is known to make a person age faster than usual. Those with Ketu in First House show early signs of ageing like grey or bald hair as well as wrinkles on the skin. Ketu hates things like hair color or face uplift. Those who proudly display their grey's are likely to have influence of Ketu on the ascendant or moon. Women with Ketu in First House don't like excessive show-off and prefer a simple lifestyle. They normally dislike make-up and other beauty products. Mind of the native hates socialisation. They don't like cultural and social norms and generally protest when such norms are forced on them by others around. Ketu just cannot understand the need to follow age-old traditions. To others around they might sound weird and problematic which is why natives with Ketu in First House prefer solitary confinement and being an introvert.")),
    ('Ketu', 2): ('S25 p.31',
        ('The second house is related to finance, money, social values, family, speech, and throat.\n'
         '\n'
         "The second house is all about family and wealth and Ketu is isolation and separation. So, when Ketu comes into the 2nd house it indicates isolation and separation from family. It could be mentally or physically. This position indicates that if a person lives with family, he/she may suffer because of fights which can make you isolate mentally. Like a person live at home physically but he/she doesn't talk to anyone.")),
    ('Ketu', 3): ('S25 p.32',
        ("Ketu in the third house indicates isolation or separation from younger siblings. Isolation could be physical or mental. It is seen in many cases that the siblings have a different mindset so they don't communicate a lot with each other. Because Ketu is a spiritual planet and these peoples love to talk about spirituality and mystical things. But their siblings will not much be interested in these topics which can cause isolation.\n"
         '\n'
         'The third house is also related to short journeys, self-efforts, and business so Ketu can isolate a person from all these things. These peoples will not like to travel, especially short travels. And it is also difficult for them to set business for them.')),
    ('Ketu', 4): ('S25 p.33',
        ('This position of Ketu isolates a person from mother and property. These peoples will mostly stay far from home and mother. In childhood, they live in hostels or with grandparents, and at a young age, they went to foreign lands to work.\n'
         '\n'
         "People with Ketu in the fourth house may have property on their name but an unfortunate sign is that they can't live there. Like a person is working abroad and send a salary to his/her spouse or parents in the homeland. But he can just visit for some days can't live there permanently.")),
    ('Ketu', 5): ('S25 p.34',
        ("This position indicates that the person has no interest in sports or other creative activities. It doesn't mean that they are not intelligent not active but the effects of Ketu isolate them from all these things related to the fifth house. It just like a kid in a school who always stays alone in the school, he has no friends, he doesn't like to play games or participate in other activities. But he passes the exams with good marks.\n"
         '\n'
         'Ketu in the 5th house also indicates separation from kids, just like a person works in another country and spends little time with his kids.')),
    ('Ketu', 6): ('S25 p.35',
        ('The sixth house is also called Dushtana house and also the Upachaya house. This house is related to enemies, legal issues, obstacles, debts, routine life, disputes, colleagues, and diseases.\n'
         '\n'
         "It is not a positive position for Ketu, because it makes a person highly confused. He has no idea what to do, even he can't choose a career for him. They can easily trust anyone who can create a problem for them. Peoples can use and cheat them very easily. They are unsure and confused about career selection.")),
    ('Ketu', 7): ('S25 p.36',
        ('The seventh house is related to Spouse, marriage, partnerships, marital happiness, and market place.\n'
         '\n'
         'Ketu in 7th house makes a person isolate from spouse and other partnerships. It shows that spouse nature will be different from a person which can cause isolation or separation. It is not the mean that they get a divorce but separation is there, it could be mentally or physically.\n'
         '\n'
         'Ketu also shows past life, so it means that they have to pay past life karma debts. Past life their relationship was good so now they have to compromise.\n'
         '\n'
         'It also shows that the person becomes highly spiritual and cut off from spouse, or go far away for business or job.')),
    ('Ketu', 8): ('S25 p.37',
        ('8th house related to death, re-birth, in-laws, secrecy, occult or hidden things or knowledge, shared properties, or wealth with spouse and transformation.\n'
         '\n'
         'This position enhances the energy of Ketu. Because Ketu is a planet of spirituality and the 8th house is also the house of spirituality and research. This placement of Ketu makes a person a true researcher. They are highly curious about everything, especially in the occult, mystical and hidden things. They have the ability to go as deep as possible in researches work.\n'
         '\n'
         'These peoples can become very good astrologers or scientists.')),
    ('Ketu', 9): ('S25 p.38',
        ('The ninth house is related to philosophy, religion, and beliefs, teachers and gurus, knowledge and wisdom, spirituality, house of fortune, law, and faith\n'
         '\n'
         'Ketu in the 9th house makes a person isolate from father and religion. This house is related to religion and spirituality and Ketu is the planet of isolation. So here a person isolates himself from everything to follow the religion but when reaching on a higher level he realized that he needs something more than religion. Because the rules of religion are defined and everyone has to follow, no one can go against the rule.\n'
         '\n'
         'Here they need something beyond the religion, where they can follow their own path. So, they start to follow spirituality. We can say the spirituality can separate or isolate these peoples from the religion, but it depends on other aspects.\n'
         '\n'
         "It is because these peoples have totally different views about religion and spirituality and they can go against their teachers and gurus. They learn a lot and research a lot. They have such great knowledge about religion and spirituality so it is not easy to challenge these people's views and beliefs.")),
    ('Ketu', 10): ('S25 p.39',
        ("Ketu in the 10th house indicates lots of ups and downs in career. These people may have trust issues because the nature of Ketu shows that they can trust on anyone very easily. So, it may lead to cheatings and fraud. Peoples can gain their trust and use them. Ketu is a blind planet. When we come to a career, these peoples can't work under anyone. But they will be good in spirituality and other mystical things, so they can do their own work and they will be successful. It is not easy for them to find a job which suits them.")),
    ('Ketu', 11): ('S25 p.40',
        ("Ketu in the 11th house makes a person isolate from friends, social circle, and elder siblings. These peoples have less friends. They don't like to stay in social gatherings or hangout with friends.\n"
         '\n'
         "They mostly stay alone and isolate. As it is the house of gains and income so these peoples can earn money but they don't care about it. Money or wealth doesn't matter for them. They may have always enough spare money to buy anything.")),
    ('Ketu', 12): ('S25 p.41',
        ('12th house represents foreign lands, losses, expenses, hospitals, jails, isolation, and Asylums.\n'
         '\n'
         'The planet of isolation in the house of isolation increases the energy of Ketu, which can isolate a person from society. They start practice in early life but they have to face a lot of difficulties at the start. They have to work hard to find the true dimensions of spirituality.\n'
         '\n'
         'These peoples are highly spiritual and intelligent. It is not easy to understand their views about spirituality. They are a deep researcher. They may have a lot of differences from their guru and teachers. These peoples have their own belief system.')),
}

# ---- Benefic / malefic in each house (S26 pp.2-14): (house or None, nature, planet or None, text, source)

BHAVA_NATURE = [
    (None, 'benefic', None, 'Benefic planets bring ease and comfort to the bhava in which they are placed', 'S26 p.2'),
    (None, 'malefic', None, 'Malefic planets bring struggle and pressure to the bhavas in which they are placed', 'S26 p.2'),
    (1, 'malefic', None, ('Whenever a malefic is in lagna lot of struggle will be there in the persons life, nothing comes easily.'), 'S26 p.3'),
    (1, 'benefic', None, 'In case a benefic is posited in lagna ease and comfort is there in the natives life', 'S26 p.3'),
    (2, 'benefic', None, ('A benefic in the 2nd house indicates that this persons early childhood will be very good, Family life is good, likes satwik and good food. Born in a rich family, his speech is very cultured and respectful'), 'S26 p.4'),
    (3, 'malefic', None, 'A malefic in third house indicates that you will achieve things by struggle and hard work', 'S26 p.5'),
    (3, 'benefic', None, 'whereas a benefic indicates that things will come easily in life without much efforts.', 'S26 p.5'),
    (3, 'malefic', None, 'Malefic in third house indicates lot of fighting spirit.', 'S26 p.5'),
    (3, 'malefic', 'Saturn', ('Here Saturn a malefic in third house spoils the relationship with younger co borns, the native will struggle to communicate'), 'S26 p.5'),
    (4, 'malefic', None, ('A malefic planet in 4 rth house will disturb your domestic atmosphere, your peace of mind, your relation with your mother, education will not be smooth.'), 'S26 p.6'),
    (4, 'malefic', 'Ketu', ('Here ketu in 4 rth will give a detached mentality from home, vehicles, property and also no peace of mind.'), 'S26 p.6'),
    (5, 'benefic', None, ('A benefic in 5 th house will indicate that you will use your intelligence properly for a right cause. You have good purva punya you will do good in higher education, the person will have good relation with his children. The person will be successful in speculations. He will be very creative and also very artistic.'), 'S26 p.7'),
    (6, 'any', None, 'It is a dusthana and a malefic house', 'S26 p.8'),
    (6, 'benefic', None, ('here if a benefic is posited you will be able to overcome your shadripus which are kama, krodha, moha, madha, lobha, matsarya.'), 'S26 p.8'),
    (6, 'any', None, 'Planet here also indicates your diseases', 'S26 p.8'),
    (6, 'malefic', None, 'A malefic posited here will give you the strength to fight your enemy.', 'S26 p.8'),
    (6, 'any', None, 'the planets will also give an indication about the reason for your enmity.', 'S26 p.8'),
    (7, 'malefic', None, 'A malefic in the 7 th house creates stress in married life, and also tension in partnership.', 'S26 p.9'),
    (7, 'malefic', 'Mars', ('Here Mars is a malefic posited in the 7 th house leading to a disturbance in married life. There will be issues due to domination'), 'S26 p.9'),
    (8, 'benefic', None, ('A benefic in the 8 th house will give you good longevity, good and smooth relationship with the spouse family, inheritance. The native will have ease in the karakatwas of the 8 th bhava'), 'S26 p.10'),
    (9, 'benefic', None, 'A benefic in the 9 th house will bring ease and comfort in the karakatwas of the 9 th house', 'S26 p.11'),
    (9, 'malefic', None, 'whereas a malefic will create tension and struggle in the bhava karakatwas.', 'S26 p.11'),
    (9, 'benefic', None, ('Here the native is blessed by fortune a good relationship with father, can be successful in higher education, is religious.'), 'S26 p.11'),
    (10, 'malefic', None, ('A malefic in the 10 th house signifies tension, struggle and effort in profession. It also signifies the work atmosphere'), 'S26 p.12'),
    (10, 'malefic', 'Saturn', ('saturn in 10th signifies a strict work atmosphere, The native has to be very hardworking and disciplined in his profession'), 'S26 p.12'),
    (11, 'benefic', None, ('A benefic in the 11 th house will give ease and comfort in the 11 th house karakatwas, the person will have a good circle of friends, gains and profits with less efforts. He will have good relationship with the elder sibling. He will do good in speculations.'), 'S26 p.13'),
    (12, 'malefic', None, ('A malefic in the 12 th house will give struggle and tension in the 12 th house karakatwas. The person will be worried due to his expenditures, he may find it difficult to go abroad. Lots of unnecessary expenditures he may also incur losses. He may suffer from sleeplessness'), 'S26 p.14'),
]

# ---- Lord of a house in another house (S26 pp.16-27, S27): (lord_of, sits_in, condition, exchange, text, source)

LORD_IN = [
    (1, 1, '', False, ('Lagna lord in lagna makes the native very powerful, strong, good immunity, good vitality, highly energetic, and independent always in the pursuit of their goals and they lead a principled life. Lagna is body, so the person is focussed on maintaining their body well. The native will have lot of self motivation. He will be very confident.'), 'S26 p.16'),
    (1, 2, '', False, ('Born to earn money. they always think about money or their family. They are foodies. They get good support from their family. they also make very good cooks. They are very much committed to their family. They try to fulfil all the needs of the family. The person is learned and wise.'), 'S26 p.17'),
    (1, 3, '', False, ('The native is courageous, they are high risk takers. They take lot of initiatives and new ventures. they focus in their self efforts and making themselves better. All that they gain is due to their own efforts and hardwork. They are very much attached to their younger siblings. They will be doing lot of short distance travel. The person would be very much interested in written communications.'), 'S26 p.18'),
    (1, 4, '', False, ('Lagna lord in 4 rth house will give lots of comforts in life. The person will be very much attached to mother. The native will enjoy all the material comforts. He will be very much attached to his home and family. Loves to spend more time at home. Very good in education'), 'S26 p.19'),
    (1, 5, '', False, ('It is considered a very auspicious placement. 5 th house is your past life or your purva punya, so when lagna lord is in 5 th you are experiencing the result of your punya in this life. The person gets success in life, he will be a good reciter of mantras, he will be interested in higher education. Native will be very attached to his children, he will be fortunate in speculation. he will be very creative and artistic.'), 'S26 p.20'),
    (1, 6, '', False, ('It is a difficult placement, the person may have enemies. have health issues or debts, he can become a good lawyer. he will be very service oriented. He will be attached to his maternal uncle. He will also be very competitive.\n'
        '\n'
        'In her example chart (S27): This native ( Lagna Lord ) had to fight ( 6 th House ) legal battles in property matters ( Kanya rashi is Prithvi tatwa ) continuously ( LL in a Dual sign ) all his life.\n'
        'This native ( LL ) was fond of his Maternal uncle ( 6 th House ).\n'
        'This native ( LL ) had taken Loan ( 6 H ) for construction and also for his business.\n'
        'Mars = Surgery\n'
        '6th House = Waist region\n'
        'This native had undergone Hernia surgery ( Mars )'), 'S26 p.21; S27 pp.9-10'),
    (1, 6, 'strong', False, 'If the lagna lord is strong the person can overcome his diseases, enemies and also repay his loans.', 'S26 p.21'),
    (1, 6, 'weak', False, 'If lagnalord is weak he will suffer.', 'S26 p.21'),
    (1, 7, '', False, ('When lagna lord is in the 7 th bhava, the person will be very much attached to the spouse, He will be an extrovert. He likes to do business, he will also like to do business in partnership. He is very much business minded. Focus in life will be on dealing with matters related to spouse, marriage or agreements.'), 'S26 p.22'),
    (1, 8, '', False, ('Life is full of ups and downs. The native will have a long life. He will be good in research. He will get sudden gains. He may have chronic health problems. He will be interested in learning the occult subjects. He will get inheritance. He will also get unearned wealth.'), 'S26 p.23'),
    (1, 8, 'strong', False, 'If lagnalord is strong he will be able to overcome the diseases and other obstacles.', 'S26 p.23'),
    (1, 9, '', False, ('The native will have a very good relation with father, the person will be very attached to the father. The person will be very religious. He is very fortunate or lucky. he will have a keen interest to do higher studies. He loves to travel. The person will be a good orator.'), 'S26 p.24'),
    (1, 10, '', False, ('When lagna lord is in 10 th the person is a workaholic. He is very attached to his profession. Wants to make a good name in his career and wants to reach the top post. He has good administrative skills, good leadership qualities and he is honest in his work.'), 'S26 p.25'),
    (1, 11, '', False, ('The person is very much goal oriented, his focus in life is on profits and fulfilment of desires. Very attached to elder siblings and also to friends, he has a good social circle. friends will help and support the native. The person will be generous and do lot of charities. Will have good name in the society.'), 'S26 p.26'),
    (1, 12, '', False, ('The native will incur lot of wasteful expenditures. He has a childhood away from home. Loves travelling to foreign countries. Interest in spirituality. He may undergo mental stress or sleep disorders. Loves to spend time in solitude.'), 'S26 p.27'),
    (3, 3, '', False, ("Third lord Jup is posited in 3 rd house. His younger co born has an important say in native's matters. He has a good relationship with his younger co borns. He is good in written communication"), 'S27 p.22'),
    (7, 10, '', False, ('7th House lord Venus is posited in 10 th House. Now blending the karakatwas of 7 th House and 10 th House, we can predict that the Spouse ( 7 th House ) is a partner in the profession ( 10 th House ) of the native'), 'S27 p.15'),
    (10, 7, '', False, ('Partnership business. In her example chart (S27): He was a Kirana merchant and later dealt with edible oil.'), 'S27 p.24'),
    (4, 11, '', True, ('There is a Parivartana between 4 th Lord Saturn and 11 th lord Sun. So he has gains from property and has multiple properties. Also this native gets happiness ( 4 H ) when he is in the company of friends ( 11 H )'), 'S27 p.22'),
]

# ---- Graha in a rashi (S23-2024 pp.5, 11): (planet, rashi 1-12, text, source)

GRAHA_RASHI = [
    ('Moon', 2, ('But if Moon is in earth signs (Taurus, Virgo or Capricorn) then Moon finds stability of earth and this person may feel stability as per wealth and assets they may have'), 'S23-2024 p.5'),
    ('Moon', 6, ('But if Moon is in earth signs (Taurus, Virgo or Capricorn) then Moon finds stability of earth and this person may feel stability as per wealth and assets they may have'), 'S23-2024 p.5'),
    ('Moon', 10, ('But if Moon is in earth signs (Taurus, Virgo or Capricorn) then Moon finds stability of earth and this person may feel stability as per wealth and assets they may have'), 'S23-2024 p.5'),
    ('Moon', 7, ('as the moon is posited in tula which indicates balance this natives approach towards life is very balanced'), 'S23-2024 p.11'),
]

# ---- Aspect meanings (S27 pp.2-4, 18; Jupiter from each house S24 pp.2-13): (planet or 'any', aspect in her count or None, from_house or None, text, source)

ASPECT_MEANING = [
    ('Jupiter', None, None, "Jupiter's aspect is equal to the blessings of God himself.", 'S27 p.2'),
    ('Jupiter', 5, None, 'Jupiters 5 th aspect indicates your punya or good deeds of previous life times', 'S27 p.2'),
    ('Jupiter', 9, None, 'The 9 th aspect indicates luck.', 'S27 p.2'),
    ('Saturn', None, None, 'Saturn aspects indicate the areas of life on which you have to focus.', 'S27 p.3'),
    ('Saturn', 3, None, '3 rd aspect tells about effort required', 'S27 p.3'),
    ('Saturn', 10, None, '10 th aspect tells about your karmic responsibility.', 'S27 p.3'),
    ('Mars', 4, None, 'Mars 4 th aspect means you will be protective towards that bhava and conflicts due to that house.', 'S27 p.4'),
    ('Mars', 8, None, 'Mars 8 th aspects signifies transformation required in that bhava.', 'S27 p.4'),
    ('Jupiter', 5, 1, ('From 1st house, Jupiter aspects the 5th house of Education, Children Creativity and Speculative Business Not only this person himself becomes very well educated but he is able to give the same education, knowledge and wisdom to his children. They also get lucky in speculative businesses.'), 'S24 p.2'),
    ('Jupiter', 7, 1, ("Jupiter's next aspect goes to 7th house of Marriage and Spouse, He shares knowledge and wisdom with spouse"), 'S24 p.2'),
    ('Jupiter', 9, 1, ("Jupiter's last aspect goes to 9th house of religion, higher knowledge, philosophy, pilgrimages etc. Now the person not only gets the basic education of 5th house but also gets the higher education of 9th house. So these people receive Ph.D. and D Lit, and other higher degrees\n"
        '\n'
        "Even if this person doesn't have great certificates to show, his level of higher knowledge and higher learning would be such that he doesn't need any degree or certificate"), 'S24 p.2'),
    ('Jupiter', 5, 2, ("From 2nd house, Jupiter aspects the 6th house of disputes, obstacles and enemies & it provides the wisdom and knowledge to win over enemies. This position can make a person lawyer as Jupiter is written Law and Jupiter's another aspect goes to 10th house, which is house of Career."), 'S24 p.3'),
    ('Jupiter', 7, 2, ('Another aspect of Jupiter goes to 8th house of occult, mysticism and hidden knowledge and as Jupiter is knowledge itself, this position gives an extra-ordinary interest in gaining knowledge of occult and mysticism'), 'S24 p.3'),
    ('Jupiter', 9, 2, ("This position can make a person lawyer as Jupiter is written Law and Jupiter's another aspect goes to 10th house, which is house of Career. So, it shows that someone is making a career in law and litigation"), 'S24 p.3'),
    ('Jupiter', 5, 3, ('From 3rd house, Jupiter aspects the 7th house of marriage. It shows the need to educate yourself in matters of relations and business'), 'S24 p.4'),
    ('Jupiter', 7, 3, ("Jupiters next aspect goes to 9th house of religion philosophy, pilgrimage and almost all the things which Jupiter represents. So Jupiter's aspect further expands the quality of 9th house gradually and makes a person highly religious and philosophical"), 'S24 p.4'),
    ('Jupiter', 9, 3, ("Jupiter's last aspects goes to 11th house of gains, network circles, elder siblings So, these people gain from their elder siblings. They have large network circles and friends. They can be very good with money matters. But all these results in 30s as 11th house is again Upachaya Houses. So, before 30, person needs to learn about how to deal with all these matters"), 'S24 p.4'),
    ('Jupiter', 5, 4, ('From 4m house, Jupiters aspect goes to 8th house of secrecy, occult, in-laws and joint assets with spouse So here, not only person gets the knowledge of occult, secrecy (as Jupiter is knowledge and wisdom) but so gives a person benefits from in-laws. Spouse brings wealth in life.'), 'S24 p.5'),
    ('Jupiter', 7, 4, ("Jupiter's next aspect goes to 10th house of career. As Jupiter is divine teacher, it can make a person a very good teacher. A career in counselling and teaching is certainly on. As 4th house also represents land and real estate, Career in Real Estate can be a good option too"), 'S24 p.5'),
    ('Jupiter', 9, 4, ("Jupiter's last aspect goes to 12th house of Spirituality and Isolation. It shows a spiritual inclination."), 'S24 p.5'),
    ('Jupiter', 5, 5, ('From 5th house, Jupiter aspects the 9th house of higher learning. Another indication towards need for higher education'), 'S24 p.6'),
    ('Jupiter', 7, 5, ("Jupiter's next aspect goes to 11th house of network circles and friends, It shows that they like to share the knowledge with friends and networking circle. It also expands their gains"), 'S24 p.6'),
    ('Jupiter', 9, 5, ("Jupiter's last aspect goes to 1st house/Ascendant of life force and personality Here, the person is society as highly learned, wise and intellectual person it also shows the need to learn about the right life path"), 'S24 p.6'),
    ('Jupiter', 5, 6, ('From 6ith house, Jupiter aspects the 10th house of Career. It shows a need to know about the right career'), 'S24 p.7'),
    ('Jupiter', 7, 6, ("Jupiter's next aspect goes to 12th house of isolated places and let's connect the dots again. This shows that person likes to share knowledge with foreign people"), 'S24 p.7'),
    ('Jupiter', 9, 6, ('Jupiters last aspect is on family. It shows that person needs to learn how to manage family and wealth matters'), 'S24 p.7'),
    ('Jupiter', 5, 7, ("From 7th house, Jupiter's aspect goes to 11th house of gains and network circles. It shows a need to learn about increasing gains."), 'S24 p.8'),
    ('Jupiter', 7, 7, ("Jupiter's next aspect goes to 1st house/Ascendant. 1st house is personality and Jupiter is knowledge and wisdom. So with this aspect, person gets recognition as very wise and knowledgeable in society."), 'S24 p.8'),
    ('Jupiter', 9, 7, ("Jupiter's last aspect goes to 3rd house of Siblings and Self-effort. It shows the need to learn about the right area of self-efforts"), 'S24 p.8'),
    ('Jupiter', 5, 8, ('From 8th house, Jupiter aspects the 12th house of Spirituality, Charity and Donations etc. It shows the need to learn about spiritual matters.'), 'S24 p.9'),
    ('Jupiter', 7, 8, ("Jupiter's next aspect goes to 2nd house of family and wealth. Here Jupiter blesses the person with a spiritual and religious family and provides lots of wealth. There speech becomes very spiritual and wise."), 'S24 p.9'),
    ('Jupiter', 9, 8, ("Jupiter's last aspect goes to 4th house of mother and home. It shows the need to learn about how to get peace of mind."), 'S24 p.9'),
    ('Jupiter', 5, 9, ('From 9th house, Jupiter aspects the 1st house of personality and life path. It shows the need to find the right life path.'), 'S24 p.10'),
    ('Jupiter', 7, 9, ("Jupiter's next aspect goes to 3rd house of Communication Skills, Business, Marketing etc. They become quite philosophical and spiritual in their way of communications and they share their knowledge through their business."), 'S24 p.10'),
    ('Jupiter', 9, 9, "Jupiter's last aspect is on 5th house of Education. It shows the need to educate yourself.", 'S24 p.10'),
    ('Jupiter', 5, 10, ('From 10th house, Jupiter aspects the 2nd house of wealth, family and speech. It shows the need to learn about how to manage family and wealth matters.'), 'S24 p.11'),
    ('Jupiter', 7, 10, ("Jupiter's next aspect goes to 4th house of home and mother. It provides a big home to the person. This shows that they like to share their knowledge from home or private offices."), 'S24 p.11'),
    ('Jupiter', 9, 10, ("Jupiter's last aspect goes to 6th house of disputes and enemies. It shows the need to find the right daily work routine. So, the biggest challenge with this position is to find the right career for yourself."), 'S24 p.11'),
    ('Jupiter', 5, 11, ("Another reason for becoming a successful entrepreneur from this position of Jupiter is Jupiter's aspects. From 11th house, Jupiter aspects all the houses that relates to running a business. Jupiter's 5th aspect and 9th aspect go to 3rd house of courage, marketing business and self-efforts etc & 7th house of business. It shows the need to get the knowledge about the best possible business"), 'S24 p.12'),
    ('Jupiter', 7, 11, ("Jupiter's next aspect goes to 5th house of education, children, creativity, risk taking abilities and speculative businesses. As Jupiter represents knowledge and 11th house is house of gains, this aspect will provide all the gain of knowledge and education. These people also impart same knowledge and education to their children. Person also gains from Speculative Businesses and his creativity."), 'S24 p.12'),
    ('Jupiter', 9, 11, ("Another reason for becoming a successful entrepreneur from this position of Jupiter is Jupiter's aspects. From 11th house, Jupiter aspects all the houses that relates to running a business. Jupiter's 5th aspect and 9th aspect go to 3rd house of courage, marketing business and self-efforts etc & 7th house of business. It shows the need to get the knowledge about the best possible business"), 'S24 p.12'),
    ('Jupiter', 5, 12, ("From 12th house, Jupiter aspects the 4th house of home and due to the effect of Jupiter's spirituality, they convert their home in to a spiritual place. It also shows the need to learn Meditation."), 'S24 p.13'),
    ('Jupiter', 7, 12, ("Jupiter's next aspect goes to 6th house of obstacles, enemies, debts etc. It shows that they like to share their knowledge in resolving conflicts of others."), 'S24 p.13'),
    ('Jupiter', 9, 12, ("Jupiter's last aspect goes to 8th house of occult knowledge and hidden secrets etc. This shows the need to learn about occult and mystical side of life."), 'S24 p.13'),
    ('any', None, None, "To see, to influence; it brings the aspecting planet's karakatwas.", 'S27 p.18'),
]

# ---- Ready Reckoner (S27 pp.12-13): (no, area, houses, karakas, karaka_female, link, source)

LIFE_AREAS = [
    (1, 'Health', (1,), ('Sun',), '', '', 'S27 p.12'),
    (2, 'Money and Finances', (2,), ('Jupiter',), '', '', 'S27 p.12'),
    (3, 'Food habits', (2,), ('Moon',), '', '', 'S27 p.12'),
    (4, 'Younger Coborn', (3,), ('Mars',), '', '', 'S27 p.12'),
    (5, 'Landed Property', (4,), ('Mars',), '', '', 'S27 p.12'),
    (6, 'Degree Education', (4,), ('Mercury',), '', '', 'S27 p.12'),
    (7, 'House and vehicle', (4,), ('Venus',), '', '', 'S27 p.12'),
    (8, 'Mother', (4,), ('Moon',), '', '', 'S27 p.12'),
    (9, 'Children', (5,), ('Jupiter',), '', '', 'S27 p.12'),
    (10, 'Disease', (6,), ('Saturn',), '', '', 'S27 p.13'),
    (11, 'Marriage and Spouse', (7,), ('Venus',), 'Mars', '', 'S27 p.13'),
    (12, 'Father', (9,), ('Sun',), '', '', 'S27 p.13'),
    (13, 'Profession', (10,), ('Saturn',), '', '', 'S27 p.13'),
    (14, 'Elder sibling', (11,), ('Saturn',), '', '', 'S27 p.13'),
    (15, 'Foreign travel', (9, 12), ('Rahu',), '', '', 'S27 p.13'),
    (16, 'Love marriage', (5, 7), ('Mercury', 'Ketu'), '', 'PAC', 'S27 p.13'),
]

# ---- Sentences that hold only for some charts: (key, planet or None, house or None, text, source)

CONDITIONS = [
    ('twelfth_hidden_talent', None, 12, ("Moreover, 12th house is house of your hidden talents in a way God's gift about which you become aware only when you go through that particular planets Mahadasha or Antardasha"), 'S23-2024 p.44'),
    ('upachaya_30s', None, 3, 'As 3rd house is Upachaya House, most of these results can be seen in 30s.', 'S23-2024 p.22'),
    ('upachaya_30s', None, 6, 'But as 6th houses Upachaya House by nature, these results will be seen in 30s.', 'S23-2024 p.25'),
    ('upachaya_30s', None, 11, 'But all these results in 30s as 11th house is again Upachaya Houses.', 'S24 p.4'),
    ('mercury_foreign_language', 'Mercury', 2, 'If there is a connection of Rahu or 12th lord, then they may learn a foreign language also.', 'S23-2024 p.33'),
    ('moon_dual_10', 'Moon', 10, ('As Moon is a fluctuating planet and 10 th house is a Dual sign, the native has done multiple professions.'), 'S23-2024 p.17'),
    ('jupiter_md_8', 'Jupiter', 8, ('So, obviously it makes a great position for someone who wants to become an occult practitioner, as Jupiter is knowledge and 8th house is house of Secrecy and Occult but for that to be manifested, person should go through Jupiter Mahadasha.'), 'S24 p.9'),
    ('jupiter_md_11', 'Jupiter', 11, "Specially, if person goes through Jupiter's Mahadasha.", 'S24 p.12'),
    ('venus_dasha_9', 'Venus', 9, ('If you have not traveled but have a strong desire. Traveling opportunities come during your Venus Dasha.'), 'S24 p.30'),
    ('venus_good', 'Venus', 2, ('Love Family – If Venus is not afflicted (debilitated enemy sign, combusted) You love being around your family. You appreciate a loving and harmonious family environment. Happy family life brings contentment and happiness.'), 'S24 p.17'),
    ('venus_good', 'Venus', 8, ('In-Laws – If Venus is not afflicted you have a loving relationship with your in-laws. Your in-laws are loving and social. Your in-laws invite you to cookouts, parties, weddings, and all social events and gatherings.'), 'S24 p.29'),
    ('venus_good', 'Venus', 11, ('Eldest Siblings – If Venus is not afflicted, you have a beautiful relationship with your eldest sibling. Your eldest sibling is good looking and can be a creative inspiration to you.'), 'S24 p.35'),
    ('venus_mercury_5', 'Venus', 5, 'If Venus is conjunct Mercury, the native may be a comedian.', 'S24 p.22'),
    ('seventh_lord_12', None, 12, 'If the 7th House Lord is in the 12th house your husband or wife can be of foreign birth.', 'S24 p.37'),
    ('venus_meets_wife', 'Venus', 3, ('With this position, you may meet your wife through younger siblings, social media, or short journeys (trips to the store or anywhere close to the home), at the movies, or a sports game.'), 'S24 p.19'),
    ('venus_meets_wife', 'Venus', 4, ('Venus in the 4th house signifies that a male will meet their wife at home, through his mother, in their town or city.'), 'S24 p.21'),
    ('venus_meets_wife', 'Venus', 5, ('If you are a male, you will meet your girlfriend, wife, or significant other anywhere there is entertainment and fun. This could be at a club, party, festival, carnival, sports game.'), 'S24 p.22'),
    ('venus_meets_wife', 'Venus', 6, ('A male can meet his wife on the job. A work environment is a good place for a man to meet and engage with women.'), 'S24 p.25'),
    ('venus_meets_wife', 'Venus', 8, 'A man will meet his wife in a secret location.', 'S24 p.29'),
    ('venus_meets_wife', 'Venus', 9, 'In male charts, you will meet your wife on a long distant or foreign trip.', 'S24 p.31'),
    ('venus_meets_wife', 'Venus', 10, ('In a males chart, you could meet your wife or significant others at work. Since Venus brings women to your work environment, one of your coworkers or employees if you are a business owner could be that special someone.'), 'S24 p.33'),
    ('venus_meets_wife', 'Venus', 11, ('If you are a male, you will meet your wife at social events. You could meet her at an organization, community event, business meeting, concert, fundraising or, charity event. You meet your wife anywhere there are crowds and a lot of people around.'), 'S24 p.35'),
    ('venus_meets_wife', 'Venus', 12, ('If you are a man, your will meet your wife in a place of isolation or on a foreign vacation. Men have good luck meeting women while foreign traveling or in private locations.'), 'S24 p.36'),
    ('jupiter_husband', 'Jupiter', None, 'For a girl, Jupiter also represents Husband.', 'S24 pp.9-13'),
    ('saturn_matures', 'Saturn', 1, 'Marriage can come later in life after the age of 36 when the planet Saturn is matured.', 'S25 p.3'),
    ('saturn_retro_1', 'Saturn', 1, ('If Saturn is in retrograde in your birth chart, it can remove restrictions and you can marriage at a reasonable age.'), 'S25 p.3'),
    ('saturn_matures', 'Saturn', 3, ('Although it can be hard for you to put words in a verbal form your communication skills are developed in time, later on in life when Saturn matures.'), 'S25 p.6'),
    ('saturn_matures', 'Saturn', 5, ('Saturn does not deny children it just delays children usually after Saturn matures at the age of 35, or when Saturn returns to its natal position in your birth chart.'), 'S25 p.9'),
    ('saturn_afflicted_6', 'Saturn', 6, ('If Saturn is in Aries or afflicted the native will be frustrated with dealing with the everyday mundane routines.'), 'S25 p.10'),
    ('saturn_matures', 'Saturn', 7, ('Marriage can be delayed until after the age of 35 or when Saturn returns to its natal position in your birth chart.'), 'S25 p.11'),
    ('saturn_matures', 'Saturn', 10, ('You may have career success later in life when Saturn matures (after age 36) or when Saturn returns to your natal Saturn.'), 'S25 p.14'),
    ('saturn_afflicted_10_young', 'Saturn', 10, ('If Saturn is afflicted (debilitated, enemy sign, combusted) and you are under the age of 36. You may be only able to acquire menial jobs. A job that requires a lot of hard work and is low-skilled. If you work or worked for a corporate rate in early in life you may start as an intern or doing the office work no one else wants to do like filing paperwork or data entry. When Saturn matures you will be able to acquire a better job or work your way up the corporate ladder.'), 'S25 p.14'),
    ('saturn_mars_12', 'Saturn', 12, 'If the planet Mars is in the 12th you can sustain an injury to your feet that can prolong (Saturn)', 'S25 p.16'),
    ('saturn_afflicted_12', 'Saturn', 12, 'If Saturn is afflicted, you will not like isolation and being in a confined space.', 'S25 p.16'),
    ('rahu_md_9', 'Rahu', 9, 'Under Rahu Mahadasha, these people travel a lot in foreign lands or for pilgrimage purposes.', 'S25 p.26'),
    ('ketu_12_purpose', 'Ketu', 12, ('In early life, they can suffer a lot but after the age of 30-35 they can find the purpose of life and they put all their efforts to achieve it.'), 'S25 p.41'),
    ('first_child_male', None, 5, ('5 th House is Kumbha rashi, a male rashi in which a male planet Mars is posited there. 5th lord Saturn is again posited in male rashi Simha. So his first child is Male.'), 'S27 p.24'),
    ('twelfth_house', None, 12, ('One thing to always keep in mind with 12th house is that it basically remains the house of losses. So, whichever planet goes in 12th house, even exalted, is in the bucket of losses. Now, to gain out of any such planet, you need to put double effort in things related with that planet.'), 'S23-2024 p.19; S24 p.13; S25 p.29'),
]

# ---- Remedies and tips of the day: (topic = planet or 'Tip', text, source)

REMEDIES = [
    ('Moon', 'Keep traveling', 'S23-2024 p.45'),
    ('Moon', ('Collect some rain water in a vessel keep it in the puja room and perform puja to it on a monday and then sprinkle it in your house'), 'S23-2024 p.45'),
    ('Moon', 'Worship Parvathi devi on poornami tithi', 'S23-2024 p.45'),
    ('Moon', 'Frequent change of place', 'S23-2024 p.45'),
    ('Moon', 'Visit places where there is heavy rainfall like Kerala, Coorg, Chirapunji', 'S23-2024 p.45'),
    ('Moon', 'Donate water, buttermilk, rice to poor people on mondays', 'S23-2024 p.45'),
    ('Moon', 'Take bath in rivers', 'S23-2024 p.45'),
    ('Moon', 'For people who are unable to travel they can spend some time at the bus stand.', 'S23-2024 p.45'),
    ('Mercury', 'They can worship Lord Vishnu to improve Mercurian energy.', 'S23-2024 p.36'),
    ('Saturn', ('If you want success in your profession or Happiness in married life distribute prasadam made with rice in a temple\n'
        'For profession you can distribute in a shiva or Anjaneya temple on saturdays\n'
        'For a happy married life you can distribute in a vishnu temple on fridays'), 'S25 p.42'),
    ('Tip', ('To attract money and luck in your life, switch words are :-\n'
        'CHARM-SPEED-FIND-COUNT-PERFECT-YES !\n'
        '777,444,777,444\n'
        'chant as many times as possible in a day, it should be chanted for at least 48 times in a day.\n'
        'You can also write this in a blank paper in either blue or green ink and keep it at your workplace.'), 'S24 p.38'),
    ('Tip', ('PLace a peacock feather in your puja room to remove negative energies in the house.\n'
        'place a peacock feather under your pillow to stop bad dreams.\n'
        'Place 7 peacock feathers in your cash box to attract money and growth in business.\n'
        'Place 2 peacock feathers in the bedroom to increase love between the couple.\n'
        'Keep 5 on the study table to increase focus and concentration in studies'), 'S26 p.28'),
    ('Tip', ('Do not give your used or old clothes to beggars\n'
        'Do not use it for cleaning or mopping the house\n'
        'You can donate them to any needy or poor people, but before giving them away, soak them in water adding rock salt, wash them well and then donate.'), 'S27 p.25'),
]

# ---- Class rules (spec R2; S25 p.10) and digbala

CLASS_RULE_TEXT = {
    "upachaya_malefic": ("A malefic planet placed here bestows good results during its dasa period; the results come "
                         "through struggle and effort and grow with time — mostly in the 30s.", "14; S26 p.5; S23-2024 p.22"),
    "dusthana_malefic": ('Malefic planets in dusthana houses (6th, 8th, and 12th) give good results.', 'S25 p.10'),
}
DIGBALA_TAUGHT = {"Mars": "S23-2024 p.29"}
