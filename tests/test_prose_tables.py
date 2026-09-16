"""The two prose delineation tables, pinned by content -- 2026-09-08, the
lords half re-made 2026-09-16.

PLANETS_IN_HOUSES is still a paraphrase of the TNAC Reference Guide for the
Planets and Places (Dykes 2023): "Planets in the Nth" (pp. 17-40, Rhetorius
Ch. 57 / PN4 II columns). A shape test let fabricated cells pass, because
prose of the right shape contradicts no arithmetic. Two pins hold each of
its cells:

  1. A literal copy of every cell as it stood after the 2026-09-08 re-read of
     all 84 cells against the Guide pages -- any edit fails on the cell, and
     must be reconciled against the Guide page cited here.
  2. Anchor words per cell, taken mechanically from the Guide's own row for
     that cell (words the paraphrase and the Guide row share). A cell moved
     to another planet or house keeps its literal but loses its anchors.

Where the Guide prints "?" (the Moon in the 6th and 8th) the cell MUST carry
the [UNCERTAIN ...] marker; a future fill-in fails here. The one place the code
does not follow the Guide row is the 9th-house Mercury PN4 halves, which the
Guide prints against its own column headings (Good: "Bad reports and
journeys..."; Bad: "Good journeys, true visions..."); the code keeps the
sensible reading and this file pins it as it is -- an owner's decision.

MASHAALLAH_LORDS is no longer the Guide's wording: every cell is this app's
paraphrase of Sahl's own sentence for that [placed-in][ruled] pairing (On
Nativities, the twelve lords-of-places passages), shaped {'text', 'cite'}.
Its pin is MASHAALLAH_LORDS_SENTENCES below: for every cell the locator and
three anchor words that the cell text and Sahl's sentence share (words
specific to the sentence, not "the" or "will"). The corpus is private, so
the fixture carries the anchors, not the sentence; the tests hold the cell
side (locator well-formed, anchors present in the text, the illegible cell
marked by its footnote, no [UNCERTAIN] marker, the count of empty cells the
page states), and the checker verifies the anchors against the sentences.
The Guide transcription of the lords table and its page numbers are gone
from this file with the wording they pinned.
"""
from __future__ import annotations

import re

import pytest

PLANETS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
GUIDE_PAGE = {1: 17, 2: 19, 3: 21, 4: 24, 5: 26, 6: 28, 7: 30, 8: 32, 9: 34, 10: 36, 11: 38, 12: 40}

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
        'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN IV cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]',
                'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN IV cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]'},
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
        'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN IV cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]',
                'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN IV cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]'},
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


# (placed_in, ruled, cite, anchors): Sahl's locator for the cell and three
# words the cell text shares with his sentence, in grid order. The six cells
# the fourth check spot-checked against the Guide (BUILD_PR3 check,
# 2026-09-12, s.6) are the first regression set, named in REGRESSION_SET.
REGRESSION_SET = [(1, 2), (6, 3), (6, 10), (10, 1), (7, 3), (8, 4)]
MASHAALLAH_LORDS_SENTENCES = [
    (1, 1, '1.36, 79-81', ['respected', 'family', 'midheaven']),
    (1, 2, '2.14, 9', ['hands', 'blessed', 'searching']),
    (1, 3, '3.10, 1', ['siblings', 'good', 'sincere']),
    (1, 4, '4.11, 2-3', ['master', 'charitable', 'authority']),
    (1, 5, '5.1, 78', ['blessed', 'youth', 'pleased']),
    (1, 6, '6.3.4, 12', ['illness', 'essence', 'servants']),
    (1, 7, '7.1, 205', ['good', 'women', 'successful']),
    (1, 8, '8.5, 2', ['lifespan', 'frustrated', 'necessities']),
    (1, 9, '9.4, 23', ['religion', 'endearing', 'sunnah']),
    (1, 10, '10.2.4, 1', ['associate', 'proficient', 'seeking']),
    (1, 11, '11.1, 16', ['successful', 'livelihood', 'glad']),
    (1, 12, '12.1, 35', ['unhappy', 'victorious', 'belligerent']),
    (2, 1, '1.36, 83', ['corruptor', 'assets', 'essence']),
    (2, 2, '2.14, 10-11', ['livelihood', 'suffering', 'siblings']),
    (2, 3, '3.10, 2', ['siblings', 'contend', 'sorrows']),
    (2, 4, '4.11, 4', ['prosperous', 'assets', 'distinguished']),
    (2, 5, '5.1, 79', ['blessed', 'livelihood', 'authority']),
    (2, 6, '6.3.4, 13', ['produce', 'renting', 'lowly']),
    (2, 7, '7.1, 206', ['corrupts', 'contention', 'defects']),
    (2, 8, '8.5, 3', ['inheritance', 'steady', 'employ']),
    (2, 9, '9.4, 24', ['assets', 'country', 'journeys']),
    (2, 10, '10.2.4, 2', ['livelihood', 'sultan', 'assets']),
    (2, 11, '11.1, 17', ['blessed', 'friends', 'assets']),
    (2, 12, '12.1, 36', ['embarrassed', 'livelihood', 'deception']),
    (3, 1, '1.36, 84-85', ['siblings', 'religion', 'wicked']),
    (3, 2, '2.14, 12', ['travels', 'siblings', 'religion']),
    (3, 3, '3.10, 3', ['siblings', 'protect', 'loved']),
    (3, 4, '4.11, 5-6', ['hardship', 'prisons', 'wretched']),
    (3, 5, '5.1, 80', ['named', 'siblings', 'successful']),
    (3, 6, '6.3.4, 14', ['siblings', 'defects', 'livelihood']),
    (3, 7, '7.1, 207', ['brother', 'relatives', 'abroad']),
    (3, 8, '8.5, 4', ['defects', 'chronic', 'slaves']),
    (3, 9, '9.4, 25', ['siblings', 'foreign', 'country']),
    (3, 10, '10.2.4, 3', ['siblings', 'ruined', 'multiplies']),
    (3, 11, '11.1, 18', ['siblings', 'blessed', 'youth']),
    (3, 12, '12.1, 37', ['siblings', 'hostile', 'badness']),
    (4, 1, '1.36, 86', ['reverent', 'hardship', 'livelihood']),
    (4, 2, '2.14, 13', ['ancestors', 'thriving', 'devoted']),
    (4, 3, '3.10, 4', ['steal', 'assets', 'family']),
    (4, 4, '4.11, 7-8', ['importance', 'reputation', 'lifespan']),
    (4, 5, '5.1, 81', ['wretches', 'hardship', 'enmity']),
    (4, 6, '6.3.4, 15', ['children', 'slaves', 'work']),
    (4, 7, '7.1, 208', ['house', 'known', 'virtuous']),
    (4, 8, '8.5, 5', ['foreigners', 'chronic', 'lifespans']),
    (4, 9, '9.4, 26', ['hidden', 'illnesses', 'homeland']),
    (4, 10, '10.2.4, 4', ['parents', 'doors', 'hardship']),
    (4, 11, '11.1, 19', ['chronic', 'shortened', 'condition']),
    (4, 12, '12.1, 38', ['parents', 'family', 'home']),
    (5, 1, '1.36, 87', ['happy', 'children', 'friends']),
    (5, 2, '2.14, 14', ['women', 'children', 'importance']),
    (5, 3, '3.10, 5', ['homeland', 'travel', 'suitable']),
    (5, 4, '4.11, 9', ['prosperous', 'lifespan', 'increase']),
    (5, 5, '5.1, 82', ['well', 'known', 'happy']),
    (5, 6, '6.3.4, 16', ['upbringing', 'hard', 'defect']),
    (5, 7, '7.1, 209', ['younger', 'compassion', 'character']),
    (5, 8, '8.5, 6', ['youth', 'power', 'sultan']),
    (5, 9, '9.4, 27', ['children', 'country', 'marry']),
    (5, 10, '10.2.4, 5', ['chronic', 'disease', 'hardship']),
    (5, 11, '11.1, 20', ['delightful', 'comfort', 'last']),
    (5, 12, '12.1, 39', ['disobey', 'hostile', 'defects']),
    (6, 1, '1.36, 88-89', ['miserable', 'slaves', 'corrupted']),
    (6, 2, '2.14, 15-16', ['medications', 'disaster', 'toil']),
    (6, 3, '3.10, 6', ['hostile', 'calamity', 'crave']),
    (6, 4, '4.11, 10-12', ['unknown', 'country', 'illnesses']),
    (6, 5, '5.1, 83', ['fortunate', 'defects', 'appear']),
    (6, 6, '6.3.4, 17', ['healthy', 'ascendant', 'look']),
    (6, 7, '7.1, 210', ['slave', 'girls', 'defects']),
    (6, 8, '8.5, 7', ['calamities', 'riding', 'animals']),
    (6, 9, '9.4, 28', ['riding', 'journeys', 'escape']),
    (6, 10, '10.2.4, 6', ['lifespan', 'walking', 'free']),
    (6, 11, '11.1, 21', ['livelihood', 'creating', 'discord']),
    (6, 12, '12.1, 40', ['saddened', 'riding', 'animals']),
    (7, 1, '1.36, 90', ['lawsuits', 'deceptive', 'subordinate']),
    (7, 2, '2.14, 17-19', ['lawsuits', 'contention', 'servant']),
    (7, 3, '3.10, 7', ['brothers', 'marry', 'hostile']),
    (7, 4, '4.11, 13', ['family', 'base', 'hostile']),
    (7, 5, '5.1, 84', ['maids', 'service', 'hostile']),
    (7, 6, '6.3.4, 18', ['esteem', 'words', 'said']),
    (7, 7, '7.1, 211', ['known', 'equal', 'match']),
    (7, 8, '8.5, 8', ['inheritances', 'assets', 'exile']),
    (7, 9, '9.4, 29', ['foreign', 'pleasing', 'pious']),
    (7, 10, '10.2.4, 7', ['powerful', 'significant', 'upright']),
    (7, 11, '11.1, 22', ['loves', 'lucky', 'benefit']),
    (7, 12, '12.1, 41', ['women', 'low', 'defects']),
    (8, 1, '1.36, 91', ['wicked', 'soul', 'distress']),
    (8, 2, '2.14, 20-21', ['inheritance', 'generous', 'taxes']),
    (8, 3, '3.10, 8', ['brothers', 'survive', 'inheritances']),
    (8, 4, '4.11, 14-15', ['diminishes', 'childbirth', 'retrograde']),
    (8, 5, '5.1, 85 fn 47', ['survive', 'miscarried', 'premature']),
    (8, 6, '6.3.4, 19', ['healthy', 'ascendant', 'look']),
    (8, 7, '7.1, 212', ['consumes', 'inheritance', 'foreign']),
    (8, 8, '8.5, 9', ['healthy', 'insignificant', 'light']),
    (8, 9, '9.4, 30', ['highway', 'robbery', 'accumulation']),
    (8, 10, '10.2.4, 8', ['younger', 'follower', 'boastful']),
    (8, 11, '11.1, 23', ['distinguished', 'descent', 'commerce']),
    (8, 12, '12.1, 42', ['few', 'enemies', 'slaves']),
    (9, 1, '1.36, 92', ['land', 'knowledge', 'sensible']),
    (9, 2, '2.14, 22-24', ['piety', 'devoutness', 'magic']),
    (9, 3, '3.10, 9', ['foreign', 'homeland', 'shelter']),
    (9, 4, '4.11, 16-17', ['unknown', 'defect', 'deceiver']),
    (9, 5, '5.1, 86', ['absent', 'homeland', 'happy']),
    (9, 6, '6.3.4, 20', ['excellent', 'intentions', 'hardship']),
    (9, 7, '7.1, 213', ['foreign', 'brother', 'marriage']),
    (9, 8, '8.5, 10', ['thoughts', 'work', 'exile']),
    (9, 9, '9.4, 31', ['journeys', 'upright', 'intention']),
    (9, 10, '10.2.4, 9', ['traveling', 'leadership', 'offered']),
    (9, 11, '11.1, 24', ['fortune', 'country', 'happy']),
    (9, 12, '12.1, 43', ['siblings', 'travels', 'religion']),
    (10, 1, '1.36, 93', ['doors', 'sultan', 'known']),
    (10, 2, '2.14, 25', ['doors', 'sultan', 'because']),
    (10, 3, '3.10, 10', ['death', 'ruin', 'jealous']),
    (10, 4, '4.11, 18-19', ['knowledge', 'tribulation', 'conflict']),
    (10, 5, '5.1, 87', ['illness', 'appearing', 'defect']),
    (10, 6, '6.3.4, 21', ['encounter', 'hardship', 'sultan']),
    (10, 7, '7.1, 214', ['family', 'sultan', 'fortunate']),
    (10, 8, '8.5, 11', ['ruin', 'sultan', 'hands']),
    (10, 9, '9.4, 32', ['siblings', 'better', 'pious']),
    (10, 10, '10.2.4, 10', ['proficient', 'influence', 'informed']),
    (10, 11, '11.1, 25', ['authority', 'friendship', 'hostile']),
    (10, 12, '12.1, 44', ['wield', 'sorrow', 'griefs']),
    (11, 1, '1.36, 94', ['character', 'friends', 'harsh']),
    (11, 2, '2.14, 26-27', ['friends', 'commerce', 'need']),
    (11, 3, '3.10, 12', ['pious', 'renowned', 'attribute']),
    (11, 4, '4.11, 20', ['lifespan', 'badness', 'dissolves']),
    (11, 5, '5.1, 88', ['pleased', 'family', 'praised']),
    (11, 6, '6.3.4, 22', ['people', 'well', 'known']),
    (11, 7, '7.1, 215', ['fertile', 'luxury', 'woman']),
    (11, 8, '8.5, 12', ['friends', 'diminished', 'condition']),
    (11, 9, '9.4, 33', ['friends', 'religion', 'foreign']),
    (11, 10, '10.2.4, 11', ['friends', 'child', 'assets']),
    (11, 11, '11.1, 26', ['comfortable', 'imputed', 'culture']),
    (11, 12, '12.1, 45', ['goodness', 'enmity', 'unhappy']),
    (12, 1, '1.36, 95-97', ['miserable', 'livelihood', 'enemies']),
    (12, 2, '2.14, 28', ['prisons', 'enemies', 'distressed']),
    (12, 3, '3.10, 13', ['hostile', 'authority', 'superior']),
    (12, 4, '4.11, 21-23', ['foreigners', 'badness', 'exile']),
    (12, 5, '5.1, 89-90', ['chronic', 'disease', 'unfortunate']),
    (12, 6, '6.3.4, 23', ['hostile', 'esteem', 'harm']),
    (12, 7, '7.1, 216', ['esteem', 'hardship', 'hostile']),
    (12, 8, '8.5, 13', ['enemies', 'kill', 'foolish']),
    (12, 9, '9.4, 34', ['wicked', 'corruptor', 'religion']),
    (12, 10, '10.2.4, 12', ['dispossessed', 'authorities', 'griefs']),
    (12, 11, '11.1, 27', ['miserable', 'living', 'enemies']),
    (12, 12, '12.1, 46', ['enemies', 'appear', 'safe']),
]



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




CITE = re.compile(r"^\d+(\.\d+)*, \d+(-\d+)?( fn \d+)?$")
DASH = {'text': '\u2014', 'cite': ''}
# What the page help states of empty cells: Sahl has a sentence for every one
# of the 144 pairings, so none.
DASH_CELLS_THE_HELP_STATES = 0


def test_the_sentence_fixture_covers_every_cell_once():
    keys = [(p, r) for p, r, _c, _a in MASHAALLAH_LORDS_SENTENCES]
    assert sorted(keys) == [(p, r) for p in range(1, 13) for r in range(1, 13)]
    assert len(keys) == len(set(keys)) == 144


@pytest.mark.parametrize("placed_in, ruled, cite, anchors", MASHAALLAH_LORDS_SENTENCES,
                         ids=[f"lord-of-{r}-in-{p}" for p, r, _c, _a in MASHAALLAH_LORDS_SENTENCES])
def test_mashaallah_lords_cell_is_pinned_to_sahls_sentence(engine, placed_in, ruled, cite, anchors):
    cell = engine["MASHAALLAH_LORDS"][placed_in][ruled]
    assert set(cell) == {"text", "cite"}
    if cell == DASH:
        assert cite == "" and anchors == []
        return
    assert cell["text"].strip() and cell["cite"] == cite
    assert CITE.match(cell["cite"]), cell["cite"]
    assert len(anchors) == 3 and set(anchors) <= _words(cell["text"]), (placed_in, ruled, anchors, cell["text"])
    assert "[UNCERTAIN" not in cell["text"]


@pytest.mark.parametrize("placed_in, ruled", REGRESSION_SET)
def test_the_fourth_checks_six_cells_now_rest_on_sahls_sentence(engine, placed_in, ruled):
    # Spot-checked against the Guide on 2026-09-12; re-derived from Sahl here.
    # [7][3] is the one of the six whose Guide wording ("Marries a relative")
    # Sahl's sentence (3.10, 7) does not carry.
    cite = next(c for p, r, c, _a in MASHAALLAH_LORDS_SENTENCES if (p, r) == (placed_in, ruled))
    cell = engine["MASHAALLAH_LORDS"][placed_in][ruled]
    assert cell["cite"] == cite and cell != DASH
    if (placed_in, ruled) == (7, 3):
        assert "relative" not in cell["text"]


def test_lord_of_the_fifth_in_the_eighth_carries_the_translators_footnote(engine):
    # 5.1, 85 is printed with an [illegible] bracket by the translator himself
    # (manuscript E smudged); his fn 47 gives the sense. The cell says so.
    cell = engine["MASHAALLAH_LORDS"][8][5]
    assert cell["cite"] == "5.1, 85 fn 47"
    assert "smudged" in cell["text"] and "premature" in cell["text"] and "miscarried" in cell["text"]


def test_the_count_of_empty_cells_is_what_the_help_states(engine):
    dashes = [(p, r) for p, row in engine["MASHAALLAH_LORDS"].items() for r, c in row.items() if c == DASH]
    assert len(dashes) == DASH_CELLS_THE_HELP_STATES, dashes
    assert not any("[UNCERTAIN" in c["text"] for row in engine["MASHAALLAH_LORDS"].values() for c in row.values())


def test_the_reader_prints_the_text_with_its_locator(engine):
    # A chart with every lord in a known place: the Signification column is
    # the cell's text followed by its locator in parentheses.
    planets = {p: {'longitude': lon} for p, lon in
               [('Saturn', 10.0), ('Jupiter', 40.0), ('Mars', 70.0), ('Sun', 100.0),
                ('Venus', 130.0), ('Mercury', 160.0), ('Moon', 190.0)]}
    rows = engine["evaluate_house_lords"](planets, 0.0)
    assert len(rows) == 12
    for row in rows:
        cell = engine["MASHAALLAH_LORDS"][row['Placed in (WS place)']][row['Topical House']]
        assert row["Masha'allah Signification"] == f"{cell['text']} ({cell['cite']})"
