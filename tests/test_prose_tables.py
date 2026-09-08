"""The two prose delineation tables, pinned by content -- 2026-09-08.

PLANETS_IN_HOUSES and MASHAALLAH_LORDS are paraphrases of the TNAC Reference
Guide for the Planets and Places (Dykes 2023): "Planets in the Nth" (pp. 17-40,
Rhetorius Ch. 57 / PN4 II columns) and "The lords of other places in the Nth
(Masha'allah)" (pp. 16-39, citing Sahl On Nativities). A shape test let
fabricated cells pass, because prose of the right shape contradicts no
arithmetic. Two pins now hold each cell:

  1. A literal copy of every cell as it stood after the 2026-09-08 re-read of
     all 84 + 144 cells against the Guide pages -- any edit fails on the cell,
     and must be reconciled against the Guide page cited here.
  2. Anchor words per cell, taken mechanically from the Guide's own row for
     that cell (words the paraphrase and the Guide row share). A cell moved
     to another planet or house keeps its literal but loses its anchors.

Where the Guide prints "?" (the Moon in the 6th and 8th) the cell MUST carry
the [UNCERTAIN ...] marker; a future fill-in fails here. The one place the code
does not follow the Guide row is the 9th-house Mercury PN4 halves, which the
Guide prints against its own column headings (Good: "Bad reports and
journeys..."; Bad: "Good journeys, true visions..."); the code keeps the
sensible reading and this file pins it as it is -- an owner's decision.
"""
from __future__ import annotations

import pytest

PLANETS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
GUIDE_PAGE = {1: 17, 2: 19, 3: 21, 4: 24, 5: 26, 6: 28, 7: 30, 8: 32, 9: 34, 10: 36, 11: 38, 12: 40}
LORDS_PAGE = {1: 16, 2: 18, 3: 20, 4: 23, 5: 25, 6: 27, 7: 29, 8: 31, 9: 33, 10: 35, 11: 37, 12: 39}

PLANETS_IN_HOUSES_GUIDE = {
    1: {
        'Saturn': {'Good': 'Eldest sibling; land ownership, building.',
                  'Bad': 'Sluggish, laborious; blamed.'},
        'Jupiter': {'Good': 'Glorious, in charge; celebrated, respected.',
                   'Bad': 'Decrease in assets, worries.'},
        'Mars': {'Good': 'Military, leader; successful, victorious.',
                'Bad': 'Unstable, squandering; fugitive, misfortune.'},
        'Sun': {'Good': 'Noble, lucky; high rank, management.',
               'Bad': 'Less noble, less benefit.'},
        'Venus': {'Good': 'Talented, friends of powerful; delight, clothing, sex.',
                 'Bad': 'Lustful, lower professions; disturbed life, quarrels.'},
        'Mercury': {'Good': 'Intellectual activities; status, praise.',
                   'Bad': 'Practical activities; loss in business.'},
        'Moon': {'Good': 'Increases of fortune, in charge.',
                'Bad': 'Sailing, poor livelihood.'},
    },
    2: {
        'Saturn': {'Good': 'Slow increase, strong; unexpected source.',
                  'Bad': 'Loss, lazy, ill; abject sources.'},
        'Jupiter': {'Good': 'Good all around, inheritances; leisure.',
                   'Bad': 'Spending without enjoyment; distress.'},
        'Mars': {'Good': 'Military; enough; benefits from unexpected place.',
                'Bad': 'Exile, dangers; squandering.'},
        'Sun': {'Good': 'Dignity, wealth; leisure.',
               'Bad': 'Private property; negligence.'},
        'Venus': {'Good': 'Prosperous, pleasing, arts.',
                 'Bad': 'Disruption, corruption, stagnation.'},
        'Mercury': {'Good': 'Evening star by night: good at business; benefit from commerce, partnerships.',
                   'Bad': 'Morning star by night: obscure, bad, poor; evening star by day: good at learning, poor; loss, downturn in business, blame, quarrels.'},
        'Moon': {'Good': 'Brilliant, conspicuous, extravagant.',
                'Bad': 'Family/actions dispersed and divided.'},
    },
    3: {
        'Saturn': {'Good': 'Initiates, religious chiefs; travel for benefit.',
                  'Bad': 'Recluses, bad religious reputation, confused thinking.'},
        'Jupiter': {'Good': 'Balanced moderation; good religious reputation, delight in siblings.',
                   'Bad': 'Distress from siblings, negligence in religion.'},
        'Mars': {'Good': 'Glory with labor; strong in travel.',
                'Bad': 'Worse than by night?; evil reports, difficult travels, illness from heat, misfortune from wild animals.'},
        'Sun': {'Good': 'Bad death for father; serious in counsel, manages public things, religious honors; travel due to Sultan, good reputation from religion, good from relatives and brothers.',
               'Bad': 'Bad reputation, distress due to travel/relatives.'},
        'Venus': {'Good': 'Travel with good/status, benefit from brothers.',
                 'Bad': 'Bad reports/journeys, contention with brothers.'},
        'Mercury': {'Good': 'Divination, astrologers, good journeys/visions.',
                   'Bad': 'Priests, magicians; bad travels, religious doubts.'},
        'Moon': {'Good': 'With Saturn: slow, unsuccessful, sacrilegious (Firmicus).',
                'Bad': 'Ignoble or infamous mother; sacrilege with Mercury or Mars; but good religious activities if with Jupiter.'},
    },
    4: {
        'Saturn': {'Good': 'Lots of wealth; owning property, building.',
                  'Bad': 'Destroys/threatens parents, illness; blamed.'},
        'Jupiter': {'Good': 'Commanders, jurists; respected, land/family assets.',
                   'Bad': 'Middling assets; worries from these topics.'},
        'Mars': {'Good': 'Generals, soldiers; successful, inspiring awe.',
                'Bad': 'Sickly, surgery; misfortune for home/land.'},
        'Sun': {'Good': 'Annoyances and interruptions in life, better in old age; increase in rank, gain good, commended, victory over enemies.',
               'Bad': 'Destroys native, parents, and livelihood; little benefit, or harm, in enemies.'},
        'Venus': {'Good': 'Fortunate over time, charming; delight in important people.',
                 'Bad': 'Loss of patrimony, widowhood; conflict in land/family.'},
        'Mercury': {'Good': 'Lots of money, initiates; status from Mercurial things/govt.',
                   'Bad': 'Forbidden mysteries; accusation, family quarrels.'},
        'Moon': {'Good': 'Honored mother, good living standard.',
                'Bad': 'Lowborn mother, commerce.'},
    },
    5: {
        'Saturn': {'Good': 'Kingships/command over time; delight in friends.',
                  'Bad': 'Delayed, sluggish; distress from children/siblings.'},
        'Jupiter': {'Good': 'Fortunate, honored, healthy; blessed by children.',
                   'Bad': 'Lower-status activities; distressed by children.'},
        'Mars': {'Good': 'Good possessions, honor; increase in children/rank.',
                'Bad': 'Harmful travel; distress/accidents in family/children.'},
        'Sun': {'Good': 'Honored, easy goals; delight/increase in children.',
               'Bad': 'Moderate fortune, childless; distress due to children.'},
        'Venus': {'Good': 'Prize-fighters, victors; increase/delight in women/children.',
                 'Bad': 'Distress from women and children.'},
        'Mercury': {'Good': 'Wealth, managing money; befriend nobles, profit.',
                   'Bad': 'Squanders money; hostility, illness/death of children.'},
        'Moon': {'Good': 'Gracious, leaders, fortunate.',
                'Bad': 'Foreign travel, parents estranged, orphans.'},
    },
    6: {
        'Saturn': {'Good': 'Moderate; slaves/animals recover.',
                  'Bad': 'No inheritance, dangers from slaves, chronic illness.'},
        'Jupiter': {'Good': 'Exposure, valuable materials; praise from subordinates.',
                   'Bad': 'Illnesses, distress from enemies/confinement.'},
        'Mars': {'Good': 'Harms children, uneven life, illness (Firmicus); healthy, victory over enemies.',
                'Bad': 'Worse than by night?; ailment from heat and moisture, disturbance of blood.'},
        'Sun': {'Good': 'With Jupiter and Venus, better than by night; mild-temperedness and safety.',
               'Bad': 'Bad death or condemnation for father if no star in the 10th (with one, good fortune from parents and resources); illness from heat and dryness, pain in eyes and head.'},
        'Venus': {'Good': 'Sex with low-quality women, treated badly by wives unless a planet is in the 10th, or difficulties in pregnancy; with a planet in the 10th, charm and good fortune through women; benefit from the underclass and medicine.',
                 'Bad': 'See above; leisure time and illness.'},
        'Mercury': {'Good': 'Advancement through speech/business.',
                   'Bad': 'Idle, evil; illness, arrested, confinement.'},
        'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN4 cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]',
                'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN4 cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]'},
    },
    7: {
        'Saturn': {'Good': 'Success after delay, long-lived; owning property.',
                  'Bad': 'Sickly, blamed/harmed.'},
        'Jupiter': {'Good': 'Long-lived, wealth later; praised, respected.',
                   'Bad': 'Moderate living; worries.'},
        'Mars': {'Good': 'Professions from fire/violence; successful, inspiring awe.',
                'Bad': 'Violent, short-lived; illnesses, spending.'},
        'Sun': {'Good': 'Increase in rank/land; administrators.',
               'Bad': 'Lower-status activities; little benefit, or harm, in land, fathers, ancestors.'},
        'Venus': {'Good': 'Age difference/delay in marriage; delight, increase in rank.',
                 'Bad': 'Lewdness; distress in sex/marriage.'},
        'Mercury': {'Good': '(Diurnal) Bad with Venus or Mars: lewd, brothel-keepers, fugitives; status and rank from Mercurial things, serving the Sultan/govt, good reputation.',
                   'Bad': '(Nocturnal) Managing affairs of women, good fortune from sex, numbers, arts or writings; bad experiences from Mercurial things, accusation, loss in business, quarreling within the family.'},
        'Moon': {'Good': 'Changes, travel, better resources.',
                'Bad': 'Foreign travel with dangers.'},
    },
    8: {
        'Saturn': {'Good': 'Assets over time/inheritance; good from dead.',
                  'Bad': 'Loss, bad death; squandering, distress.'},
        'Jupiter': {'Good': 'Acquisition, inheritance; leisure.',
                   'Bad': 'Spending without happiness; distress/fighting due to assets.'},
        'Mars': {'Good': 'Hot-heads, bright; benefit from dead/inheritance.',
                'Bad': 'Patrimony spent, dangers; squandered assets.'},
        'Sun': {'Good': "Father's early death, healing; mild-temperedness.",
               'Bad': 'See above; leisure but without benefit, poor way of life, negligence or laziness.'},
        'Venus': {'Good': 'Wealthy, benefit from death of women, easy death; benefit from underclass or base work, much spending.',
                 'Bad': 'Marry late, lower-quality women, STDs, seizures; negligence in assets, idleness, little benefit, fighting over assets.'},
        'Mercury': {'Good': 'Money, management, inheritance; praised.',
                   'Bad': 'Ineffective, lazy; blamed, quarreling due to assets.'},
        'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN4 cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]',
                'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN4 cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]'},
    },
    9: {
        'Saturn': {'Good': 'Initiates, chief priests; travel for benefit.',
                  'Bad': 'Recluses, anger at gods; confused religious opinions.'},
        'Jupiter': {'Good': 'Predicting future, priesthood; good religious reputation.',
                   'Bad': 'Unsteady, false speech; negligence in religion.'},
        'Mars': {'Good': 'Glory, unpunished; strong in travel.',
                'Bad': 'Evil reports, difficult travels, illness.'},
        'Sun': {'Good': 'Building sacred things, religious authority.',
               'Bad': 'Harm in travels; bad reputation, distress.'},
        'Venus': {'Good': 'Divine men, gifts from temples; travel with status.',
                 'Bad': 'Demon-afflicted, illicit sex; bad reports/journeys.'},
        'Mercury': {'Good': 'Priests, wizards; good journeys, true visions.',
                   'Bad': 'Seers, sacrificers; defamed in religion, bad assets.'},
        'Moon': {'Good': 'Living abroad, notable; benefiting from temples.',
                'Bad': 'Wandering and dangers; temple servants.'},
    },
    10: {
        'Saturn': {'Good': 'Leaders, farmers; agriculture, building.',
                  'Bad': 'Bunglers, sorrow; blamed, low work.'},
        'Jupiter': {'Good': 'Athletes, famous, trusted; celebrated, respected.',
                   'Bad': 'Handsome but unstable; decreased assets, worry.'},
        'Mars': {'Good': 'Unstable, fearsome leaders; successful, favored by Sultan.',
                'Bad': 'No accomplishments, fugitives; misfortune, violence.'},
        'Sun': {'Good': 'Rulers, leaders, dignity; increased rank, victorious.',
               'Bad': 'Success through violence; fear from Sultan.'},
        'Venus': {'Good': 'Honored, musicians; honored by Sultan, delight.',
                 'Bad': 'Blamed, burdened, indecent; bad reputation.'},
        'Mercury': {'Good': 'Admirable, trusted; status from writing.',
                   'Bad': 'Changes, living abroad; accusation, loss.'},
        'Moon': {'Good': 'Rulers, successful, trusted.',
                'Bad': 'Hardship, unsteady, error.'},
    },
    11: {
        'Saturn': {'Good': 'Middling goods over time; delight in friends.',
                  'Bad': 'Distress from children/siblings.'},
        'Jupiter': {'Good': 'Fortunate, renowned, authority; good way of life.',
                   'Bad': 'Diminished effectiveness; worries, distressed by friends.'},
        'Mars': {'Good': 'Many goods, dignity; increase in children/rank.',
                'Bad': 'Feuding with friends and brothers.'},
        'Sun': {'Good': 'Lucky, noble; good condition, delight in friends.',
               'Bad': 'Harms children; distress due to friends.'},
        'Venus': {'Good': 'Powerful, trusted; increase/delight in friends.',
                 'Bad': 'Sterility, unusual sexuality; hostility to friends.'},
        'Mercury': {'Good': 'Ingenious, accounts; befriend nobles, profit.',
                   'Bad': 'Spending, agents; hostility from friends, illness of children.'},
        'Moon': {'Good': 'Rulers, favored, good from parents.',
                'Bad': 'Living abroad, estrangements, orphanhood.'},
    },
    12: {
        'Saturn': {'Good': 'Victory over enemies.',
                  'Bad': 'Loss of inheritance, mental disturbance; hardship from prison.'},
        'Jupiter': {'Good': 'Praise from subordinates; fights against superiors.',
                   'Bad': 'Illnesses, distress from enemies/confinement.'},
        'Mars': {'Good': 'Safety from enemies.',
                'Bad': 'Illness, injury, dangers from slaves, criminals; something detestable from runaways, the confined, enemies.'},
        'Sun': {'Good': 'Good reputation, safety.',
               'Bad': 'With infortunes, long illnesses, defects, slavery; confinement, distress due to enemies and the confined; exile.'},
        'Venus': {'Good': 'Benefit from underclass.',
                 'Bad': 'Ruined by women; leisure time and illness, punishment.'},
        'Mercury': {'Good': 'Managing big affairs; benefit from low work.',
                   'Bad': 'Danger from slaves; arrested unfairly, confinement.'},
        'Moon': {'Good': 'Luckiness/authority (with fortunes).',
                'Bad': 'Short life, humble; bad for patrimony/travel.'},
    },
}

# Words each cell shares with its own Guide row (None where the Guide prints "?").
PLANETS_IN_HOUSES_ANCHORS = {
    1: {'Saturn': ['laborious', 'sluggish', 'blamed'], 'Jupiter': ['celebrated', 'respected', 'decrease'], 'Mars': ['squandering', 'misfortune', 'successful'], 'Sun': ['management', 'benefit', 'noble'], 'Venus': ['professions', 'disturbed', 'quarrels'], 'Mercury': ['activities', 'practical', 'business'], 'Moon': ['livelihood', 'increases', 'fortune']},
    2: {'Saturn': ['sources', 'abject', 'lazy'], 'Jupiter': ['inheritances', 'enjoyment', 'distress'], 'Mars': ['squandering', 'unexpected', 'benefits'], 'Sun': ['negligence', 'property', 'dignity'], 'Venus': ['corruption', 'disruption', 'prosperous'], 'Mercury': ['business', 'downturn', 'learning'], 'Moon': ['conspicuous', 'extravagant', 'brilliant']},
    3: {'Saturn': ['reputation', 'religious', 'confused'], 'Jupiter': ['moderation', 'negligence', 'balanced'], 'Mars': ['misfortune', 'difficult', 'animals'], 'Sun': ['reputation', 'relatives', 'religious'], 'Venus': ['contention', 'brothers', 'journeys'], 'Mercury': ['magicians', 'religious', 'priests'], 'Moon': ['activities', 'religious', 'sacrilege']},
    4: {'Saturn': ['threatens', 'destroys', 'parents'], 'Jupiter': ['middling', 'worries', 'assets'], 'Mars': ['misfortune', 'surgery', 'sickly'], 'Sun': ['livelihood', 'destroys', 'increase'], 'Venus': ['patrimony', 'widowhood', 'conflict'], 'Mercury': ['accusation', 'forbidden', 'mercurial'], 'Moon': ['commerce', 'standard', 'honored']},
    5: {'Saturn': ['children', 'distress', 'siblings'], 'Jupiter': ['activities', 'distressed', 'children'], 'Mars': ['accidents', 'children', 'distress'], 'Sun': ['childless', 'children', 'distress'], 'Venus': ['children', 'distress', 'delight'], 'Mercury': ['hostility', 'squanders', 'children'], 'Moon': ['estranged', 'foreign', 'orphans']},
    6: {'Saturn': ['inheritance', 'animals', 'chronic'], 'Jupiter': ['confinement', 'illnesses', 'distress'], 'Mars': ['disturbance', 'moisture', 'ailment'], 'Sun': ['resources', 'dryness', 'fortune'], 'Venus': ['difficulties', 'underclass', 'medicine'], 'Mercury': ['confinement', 'arrested', 'illness'], 'Moon': None},
    7: {'Saturn': ['blamed', 'harmed', 'sickly'], 'Jupiter': ['moderate', 'worries', 'living'], 'Mars': ['illnesses', 'spending', 'violent'], 'Sun': ['administrators', 'activities', 'ancestors'], 'Venus': ['difference', 'distress', 'lewdness'], 'Mercury': ['experiences', 'accusation', 'quarreling'], 'Moon': ['resources', 'changes', 'dangers']},
    8: {'Saturn': ['inheritance', 'squandering', 'distress'], 'Jupiter': ['acquisition', 'inheritance', 'happiness'], 'Mars': ['squandered', 'patrimony', 'dangers'], 'Sun': ['negligence', 'laziness', 'benefit'], 'Venus': ['negligence', 'fighting', 'idleness'], 'Mercury': ['ineffective', 'inheritance', 'quarreling'], 'Moon': None},
    9: {'Saturn': ['religious', 'confused', 'opinions'], 'Jupiter': ['negligence', 'religion', 'unsteady'], 'Mars': ['difficult', 'illness', 'reports'], 'Sun': ['reputation', 'authority', 'distress'], 'Venus': ['afflicted', 'journeys', 'illicit'], 'Mercury': ['sacrificers', 'journeys', 'visions'], 'Moon': ['wandering', 'servants', 'dangers']},
    10: {'Saturn': ['bunglers', 'blamed', 'sorrow'], 'Jupiter': ['celebrated', 'decreased', 'respected'], 'Mars': ['accomplishments', 'misfortune', 'successful'], 'Sun': ['victorious', 'increased', 'violence'], 'Venus': ['reputation', 'musicians', 'burdened'], 'Mercury': ['accusation', 'changes', 'writing'], 'Moon': ['successful', 'hardship', 'unsteady']},
    11: {'Saturn': ['children', 'distress', 'siblings'], 'Jupiter': ['diminished', 'distressed', 'friends'], 'Mars': ['brothers', 'dignity', 'feuding'], 'Sun': ['children', 'distress', 'delight'], 'Venus': ['hostility', 'sexuality', 'sterility'], 'Mercury': ['hostility', 'children', 'spending'], 'Moon': ['estrangements', 'orphanhood', 'abroad']},
    12: {'Saturn': ['disturbance', 'inheritance', 'hardship'], 'Jupiter': ['confinement', 'illnesses', 'distress'], 'Mars': ['detestable', 'criminals', 'something'], 'Sun': ['confinement', 'infortunes', 'illnesses'], 'Venus': ['punishment', 'underclass', 'benefit'], 'Mercury': ['confinement', 'arrested', 'unfairly'], 'Moon': ['patrimony', 'travel', 'bad']},
}

MASHAALLAH_LORDS_GUIDE = {
    1: {
        1: 'Respected in family (subject to other conditions)',
        2: 'Work with own hands, blessed without searching and need',
        3: 'Good for siblings from native',
        4: 'Master of his family and their livelihood; charitable to parents',
        5: 'Blessed with children in youth, happy with children',
        6: 'Illness of nature of that planet; death of animals and servants',
        7: 'Good from women, success from them',
        8: 'Long lifespan (if good condition); frustration in seeking necessities',
        9: 'Of fine religion, good soul, knowing the Sunnah',
        10: 'Associate of authorities, proficient in work, Sultan comes to him',
        11: 'Successful, good livelihood and condition, glad',
        12: 'Unhappy, enemies multiply and are victorious, tribulation, belligerent',
    },
    2: {
        1: 'Will corrupt assets; but if received, gains from sign essence',
        2: 'Livelihood from known source; if looked at by infortune, ruin',
        3: 'Siblings compete for assets; they will seek the native',
        4: 'Prosperous parents; native inherits and is distinguished among siblings',
        5: 'Children will have good livelihood',
        6: 'Livelihood from what slaves produce, and animals; lowly benefits',
        7: 'Corrupts assets due to conflict',
        8: 'Inheritance; sometimes do work for government/authority',
        9: 'Assets from foreign country, benefit from travel',
        10: 'Livelihood from government/authority figure; accumulates assets',
        11: 'Benefit and assets from friends',
        12: 'Shameful work, bad character and livelihood, with deception',
    },
    3: {
        1: 'Siblings suitable, dependent on native; good/wicked mind based on aspects',
        2: 'Gain from travels and siblings; religion/gain if a fortune',
        3: 'Siblings are well known, will protect him, love him',
        4: 'Parents have hardship from siblings; parents like native better',
        5: "Native's children named after his siblings; successful in travels",
        6: 'Siblings have defects/illness, or do the work of slaves',
        7: "Brother marries native's women; hostility; native marries relative",
        8: 'Siblings have defects, chronic illness, diminished condition',
        9: 'Siblings marry foreign women; moves to another country',
        10: 'Few siblings, siblings ruined; many travels',
        11: 'Well-known siblings, condition good, esp. in youth',
        12: 'Siblings hostile to native, hardship from them',
    },
    4: {
        1: 'Reverent to parents; hardship from ruler; gains from fathers if received',
        2: 'Livelihood relates to ancestors; thriving childhood home; devotion',
        3: "Siblings steal parents' assets; recognized as thieves",
        4: 'Parents well known, good reputation; short life if harmed',
        5: "Native's children are wretches; encounters hardship due to them",
        6: 'Native is child of slaves or those doing slave work',
        7: 'Marries someone from own house, spouse is well known and good',
        8: 'Fathers are foreigners or have defects/illness, short lifespans',
        9: 'Parents have hidden illnesses, die outside homeland',
        10: 'Parents known to rulers; hardship from rulers',
        11: 'Father has chronic illness, short life, diminished condition',
        12: 'Parents/family hostile to native; native destroys/leaves childhood home',
    },
    5: {
        1: 'Happy with children (if unharmed)',
        2: 'Children have status, will gain good',
        3: 'Native has siblings abroad who travel and have children',
        4: 'Prosperous parents see successive generations; good increases',
        5: 'Native has well-known children who are happy',
        6: "Children's upbringing hard, children have defect",
        7: 'Native marries younger spouse, well-known and virtuous',
        8: 'Children die early, or have power over others due to Sultan',
        9: 'Has children in foreign country, delighted; children religious/educated',
        10: 'Abundance of children; illness/death if harmed; hardship from Sultan',
        11: 'Delightful children, blessed with good and comfort',
        12: 'Children debased, sick, from low-status; disobedient/hostile',
    },
    6: {
        1: 'Miserable, slave work; illness if received; literal slave if Moon corrupted',
        2: 'Livelihood from 6th-place things; disaster/hardship if not received',
        3: 'Siblings are hostile and crave his ruin',
        4: 'Parents unknown in country; aspecting planet shows good/bad',
        5: 'Fortunate children, but defects will appear in them',
        6: 'Native healthy, if lord of Ascendant does not look',
        7: 'Native associates with slave girls or women with defects',
        8: 'Calamities in slaves and riding animals; not blessed by them',
        9: 'Blessed with slaves/animals; travel brings illness or corrupts slaves',
        10: 'Short lifespan, itinerant, enslaves free people',
        11: 'Bad condition in livelihood, little good, creating discord',
        12: 'Saddened by slaves and riding animals, no good in them',
    },
    7: {
        1: 'Native very eager; subordinate to spouse',
        2: 'Lower-status women; gain/lose money in marriage',
        3: 'Marries a relative; brothers hostile or marry his women',
        4: 'Marries relative, good rank; father hostile to native',
        5: 'Younger spouse; children hostile; deluded about women; servant children',
        6: 'Sick/slave spouse; low-status spouse; bad reputation due to spouse',
        7: 'Suitable marriage; spouse has rank of maternal relatives; well-known',
        8: 'Will inherit from spouse; native dies in exile',
        9: 'Foreign spouse; good character/pious if a fortune',
        10: 'Esteemed, well-known spouse; higher-status and connected',
        11: 'Loving, happy spouse; children and benefit from spouse',
        12: 'Low-status or sick spouse; spouse is hostile',
    },
    8: {
        1: 'A wicked soul, much distress, faint-hearted',
        2: 'Livelihood from inheritance/dead; generous; assets taken if connecting to 8th',
        3: "Brother's women will not survive or get inheritance",
        4: "Diminishes father's lifespan; fear for native, mother dies in childbirth",
        5: 'Children premature or miscarried.',
        6: 'Native healthy if lord of Ascendant does not look',
        7: 'Consumes inheritance of women; marries foreign woman',
        8: 'Native is healthy, illness insignificant, death will be light',
        9: 'Suffers robbery on journeys, eager in accumulating assets',
        10: 'Authority in youth, a follower who seeks leadership/boasts',
        11: 'Not well known/descended; does low work like commerce',
        12: "Few enemies; many of native's slaves will die",
    },
    9: {
        1: 'Remains in foreign land; travel; speaks knowledge; sensible if unharmed',
        2: 'Livelihood from travel, piety, religion',
        3: 'Siblings marry foreign women, live abroad',
        4: 'Unknown fathers who leave, with defects/bad death; bad faith',
        5: 'Has children abroad; they make native happy',
        6: 'Excellent intentions; illness while traveling, encounters hardship',
        7: 'Marries foreign woman given by her brother; native loves her',
        8: 'Bad thoughts and work; die in exile',
        9: 'Few journeys; upright in religion of fathers, good intention',
        10: 'Authority/leadership traveling abroad; offered the good',
        11: 'Good fortune abroad; happy until end of life',
        12: 'Siblings/native have hardship from enemies traveling; bad religion',
    },
    10: {
        1: 'Interacting with Sultan, known by him, living due to Sultan',
        2: 'Livelihood from the Sultan',
        3: 'Death of siblings, jealousy and grudges',
        4: 'Fathers well known to Sultan',
        5: 'Defects and illnesses in children',
        6: 'Encounters hardship from the Sultan',
        7: 'Marriage to someone related to Sultan, fortunate woman, good from her',
        8: "Native's ruin will be due to Sultan",
        9: "Siblings marry better women or from Sultan's family; native is pious",
        10: 'Proficient in work, having influence, livelihood from work',
        11: 'Authority in friendship, Sultan will not be hostile',
        12: "Hostility from Sultan and native's superiors; unhappy",
    },
    11: {
        1: 'Good character, many friends, but harsh toward children/few children',
        2: 'Livelihood relates to friends/commerce; friends need native if Asc lord looks',
        3: 'Pious siblings known for that; reflects well on native',
        4: 'Short lifespan for father; bad condition unless received by fortune',
        5: 'Pleased by children and family; praise for him',
        6: 'Friends are not well known',
        7: 'Marries fertile woman, will love her, live in luxury because of her',
        8: 'Friends diminished; corrupts friendship; dies when condition is good',
        9: 'Pious friends, shared religious love; siblings marry foreign women',
        10: 'Friends benefit from native; child inherits assets from Sultan',
        11: 'Lives comfortable life, imputed with goodness, many friends, culture',
        12: 'Leaves goodness of friends; friends become enemies, unhappy',
    },
    12: {
        1: 'Miserable, bad livelihood, enemies victorious; worse if bad connection',
        2: 'Life/livelihood from prisons, enemies; distressed and poor in soul',
        3: 'Hostile siblings; they get his authority and are superior',
        4: 'Parents are foreigners in exile; aspects show if good/bad for them',
        5: 'Children have defect/illness, will die; no children if unfortunate',
        6: 'Hostile to lower-status people; native sickly or ongoing health problems',
        7: 'Spouse has little esteem; hardship/hostility; secret relationships/cheating',
        8: 'Killing by enemies feared, or foolish people oppose him',
        9: 'Wicked intentions; corrupts religion, thinks he is right',
        10: 'Dispossessed by authorities; griefs; works with large animals/secrets',
        11: 'Little good, miserable life; few friends, many enemies',
        12: 'Few enemies, may not manifest; safe from them',
    },
}

MASHAALLAH_LORDS_ANCHORS = {
    1: {1: ['conditions', 'respected', 'subject'], 2: ['searching', 'blessed', 'without'], 3: ['siblings', 'native', 'good'], 4: ['charitable', 'livelihood', 'parents'], 5: ['children', 'blessed', 'happy'], 6: ['servants', 'animals', 'illness'], 7: ['success', 'women', 'good'], 8: ['frustration', 'necessities', 'condition'], 9: ['religion', 'knowing', 'sunnah'], 10: ['authorities', 'proficient', 'associate'], 11: ['livelihood', 'successful', 'condition'], 12: ['belligerent', 'tribulation', 'victorious']},
    2: {1: ['received', 'corrupt', 'essence'], 2: ['livelihood', 'infortune', 'looked'], 3: ['siblings', 'compete', 'assets'], 4: ['distinguished', 'prosperous', 'siblings'], 5: ['livelihood', 'children', 'good'], 6: ['livelihood', 'animals', 'produce'], 7: ['conflict', 'corrupts', 'assets'], 8: ['inheritance', 'government', 'authority'], 9: ['benefit', 'country', 'foreign'], 10: ['accumulates', 'government', 'livelihood'], 11: ['benefit', 'friends', 'assets'], 12: ['livelihood', 'character', 'deception']},
    3: {1: ['dependent', 'siblings', 'suitable'], 2: ['religion', 'siblings', 'fortune'], 3: ['siblings', 'protect', 'known'], 4: ['hardship', 'siblings', 'parents'], 5: ['successful', 'children', 'siblings'], 6: ['siblings', 'defects', 'illness'], 7: ['hostility', 'brother', 'marries'], 8: ['diminished', 'condition', 'siblings'], 9: ['siblings', 'another', 'country'], 10: ['siblings', 'travels', 'ruined'], 11: ['condition', 'siblings', 'known'], 12: ['hardship', 'siblings', 'hostile']},
    4: {1: ['hardship', 'received', 'reverent'], 2: ['livelihood', 'ancestors', 'childhood'], 3: ['siblings', 'parents', 'thieves'], 4: ['reputation', 'parents', 'known'], 5: ['encounters', 'children', 'hardship'], 6: ['native', 'slaves', 'child'], 7: ['marries', 'someone', 'spouse'], 8: ['foreigners', 'lifespans', 'defects'], 9: ['illnesses', 'homeland', 'outside'], 10: ['hardship', 'parents', 'rulers'], 11: ['diminished', 'condition', 'chronic'], 12: ['childhood', 'hostile', 'parents']},
    5: {1: ['children', 'unharmed', 'happy'], 2: ['children', 'status', 'gain'], 3: ['children', 'siblings', 'native'], 4: ['generations', 'prosperous', 'successive'], 5: ['children', 'native', 'happy'], 6: ['upbringing', 'children', 'defect'], 7: ['virtuous', 'marries', 'younger'], 8: ['children', 'others', 'sultan'], 9: ['delighted', 'religious', 'children'], 10: ['abundance', 'children', 'hardship'], 11: ['delightful', 'children', 'blessed'], 12: ['disobedient', 'children', 'debased']},
    6: {1: ['corrupted', 'miserable', 'received'], 2: ['disaster', 'hardship', 'things'], 3: ['siblings', 'hostile', 'crave'], 4: ['aspecting', 'country', 'parents'], 5: ['fortunate', 'children', 'defects'], 6: ['ascendant', 'healthy', 'native'], 7: ['associates', 'defects', 'native'], 8: ['calamities', 'animals', 'blessed'], 9: ['corrupts', 'animals', 'blessed'], 10: ['itinerant', 'lifespan', 'people'], 11: ['livelihood', 'condition', 'creating'], 12: ['saddened', 'animals', 'riding']},
    7: {1: ['subordinate', 'native', 'spouse'], 2: ['marriage', 'status', 'lower'], 3: ['brothers', 'relative', 'hostile'], 4: ['relative', 'hostile', 'marries'], 5: ['children', 'deluded', 'hostile'], 6: ['reputation', 'spouse', 'status'], 7: ['relatives', 'marriage', 'maternal'], 8: ['inherit', 'native', 'spouse'], 9: ['character', 'foreign', 'fortune'], 10: ['connected', 'esteemed', 'higher'], 11: ['children', 'benefit', 'loving'], 12: ['hostile', 'spouse', 'status']},
    8: {1: ['distress', 'hearted', 'wicked'], 2: ['inheritance', 'connecting', 'assets'], 3: ['inheritance', 'brother', 'survive'], 4: ['childbirth', 'diminishes', 'lifespan'], 5: ['miscarried', 'premature', 'children'], 6: ['ascendant', 'healthy', 'native'], 7: ['inheritance', 'consumes', 'foreign'], 8: ['insignificant', 'healthy', 'illness'], 9: ['accumulating', 'journeys', 'robbery'], 10: ['leadership', 'authority', 'follower'], 11: ['commerce', 'known', 'well'], 12: ['enemies', 'native', 'slaves']},
    9: {1: ['knowledge', 'sensible', 'foreign'], 2: ['livelihood', 'religion', 'travel'], 3: ['siblings', 'foreign', 'abroad'], 4: ['defects', 'fathers', 'unknown'], 5: ['children', 'native', 'happy'], 6: ['intentions', 'excellent', 'traveling'], 7: ['brother', 'foreign', 'marries'], 8: ['thoughts', 'exile', 'work'], 9: ['intention', 'journeys', 'religion'], 10: ['leadership', 'authority', 'traveling'], 11: ['fortune', 'abroad', 'happy'], 12: ['traveling', 'hardship', 'religion']},
    10: {1: ['interacting', 'living', 'sultan'], 2: ['livelihood', 'sultan'], 3: ['jealousy', 'siblings', 'grudges'], 4: ['fathers', 'sultan', 'known'], 5: ['illnesses', 'children', 'defects'], 6: ['encounters', 'hardship', 'sultan'], 7: ['fortunate', 'marriage', 'related'], 8: ['native', 'sultan', 'ruin'], 9: ['siblings', 'better', 'family'], 10: ['livelihood', 'proficient', 'influence'], 11: ['friendship', 'authority', 'hostile'], 12: ['hostility', 'superiors', 'unhappy']},
    11: {1: ['character', 'children', 'friends'], 2: ['livelihood', 'commerce', 'friends'], 3: ['siblings', 'native', 'known'], 4: ['condition', 'lifespan', 'received'], 5: ['children', 'pleased', 'family'], 6: ['friends', 'known', 'well'], 7: ['because', 'fertile', 'marries'], 8: ['diminished', 'friendship', 'condition'], 9: ['religious', 'siblings', 'foreign'], 10: ['inherits', 'benefit', 'friends'], 11: ['comfortable', 'goodness', 'culture'], 12: ['goodness', 'enemies', 'friends']},
    12: {1: ['connection', 'livelihood', 'victorious'], 2: ['distressed', 'livelihood', 'enemies'], 3: ['authority', 'siblings', 'superior'], 4: ['foreigners', 'parents', 'exile'], 5: ['unfortunate', 'children', 'illness'], 6: ['problems', 'ongoing', 'health'], 7: ['relationships', 'cheating', 'hardship'], 8: ['enemies', 'foolish', 'killing'], 9: ['intentions', 'corrupts', 'religion'], 10: ['animals', 'large', 'works'], 11: ['miserable', 'enemies', 'friends'], 12: ['manifest', 'enemies', 'safe']},
}


def _words(text):
    import re
    return set(re.findall(r"[a-z]+", text.lower()))


@pytest.mark.parametrize("house", range(1, 13))
def test_planets_in_houses_match_the_guide_page_cell_by_cell(engine, house):
    for planet in PLANETS:
        assert engine["PLANETS_IN_HOUSES"][house][planet] == PLANETS_IN_HOUSES_GUIDE[house][planet], \
            (house, planet, "Reference Guide p.", GUIDE_PAGE[house])


@pytest.mark.parametrize("house", range(1, 13))
def test_planets_in_houses_cells_carry_their_own_guide_row_anchors(engine, house):
    for planet in PLANETS:
        cell = engine["PLANETS_IN_HOUSES"][house][planet]
        anchors = PLANETS_IN_HOUSES_ANCHORS[house][planet]
        if anchors is None:
            continue
        words = _words(cell["Good"] + " " + cell["Bad"])
        assert set(anchors) <= words, (house, planet, anchors, "Reference Guide p.", GUIDE_PAGE[house])


@pytest.mark.parametrize("house", [6, 8])
def test_moon_cells_the_guide_leaves_blank_stay_marked_uncertain(engine, house):
    # Reference Guide p. 28 (6th) and p. 32 (8th): the Moon row reads "?" in
    # both columns. A sourced delineation would be a sourcing decision for the
    # owner; an unsourced one fails here.
    cell = engine["PLANETS_IN_HOUSES"][house]["Moon"]
    assert cell["Good"].startswith("[UNCERTAIN") and cell["Bad"].startswith("[UNCERTAIN"), cell
    assert "do not rely on this cell" in cell["Good"]


def test_no_other_cell_is_marked_uncertain(engine):
    # Negative control: exactly the two Guide-blank cells carry the marker.
    marked = {(h, p) for h, row in engine["PLANETS_IN_HOUSES"].items()
              for p, cell in row.items() if cell["Good"].startswith("[UNCERTAIN")}
    assert marked == {(6, "Moon"), (8, "Moon")}


@pytest.mark.parametrize("house", range(1, 13))
def test_mashaallah_lords_match_the_guide_page_cell_by_cell(engine, house):
    for lord in range(1, 13):
        assert engine["MASHAALLAH_LORDS"][house][lord] == MASHAALLAH_LORDS_GUIDE[house][lord], \
            (house, lord, "Reference Guide p.", LORDS_PAGE[house])
        assert set(MASHAALLAH_LORDS_ANCHORS[house][lord]) <= _words(engine["MASHAALLAH_LORDS"][house][lord])


def test_lord_of_the_fifth_in_the_eighth_is_resolved_from_the_guide(engine):
    # p. 31, row 5th: "Children premature or miscarried." -- the OCR of Sahl
    # 8.5 is illegible here; the Guide settles the reading. No cell may carry
    # the old placeholder.
    assert engine["MASHAALLAH_LORDS"][8][5] == "Children premature or miscarried."
    assert not any("[UNCERTAIN" in v for row in engine["MASHAALLAH_LORDS"].values() for v in row.values())
