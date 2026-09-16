"""The two prose delineation tables, pinned by content -- 2026-09-08, the
lords half re-made 2026-09-16, the planets half's PN IV column the same day.

PLANETS_IN_HOUSES[house][planet] is {'Rhetorius': {'Good', 'Bad'}, 'PN IV':
{'Good', 'Bad'}}, every half {'text', 'cite'}. Its two sources are pinned
differently, because they stand differently:

  1. The PN IV halves are this app's paraphrases of Abu Ma'shar's Book II
     chapters on the lord of the year in the houses (II.6 Saturn, II.9
     Jupiter, II.12 Mars, II.15 the Sun, II.18 Venus, II.21 Mercury) applied
     to natal planets, and of VII.8 (the Moon by transit) for the Moon, who
     has no Book II houses chapter (II.22, 13 fn 312). Their pin is
     PN4_HALVES_SENTENCES: for every half the locator and three anchor words
     the half's text and the cited sentence share, or ('', []) for a dash.
     The corpus is private, so the fixture carries the anchors, not the
     sentence; the tests hold the cell side (locator well-formed, anchors in
     the text, the Moon's twelve on VII.8, the dash count the page states,
     no [UNCERTAIN] marker, the reader's cell format) and the checker
     verifies the anchors against the sentences.
  2. The Rhetorius halves still print the Guide's summary (TNAC Reference
     Guide for the Planets and Places, Dykes 2023, "Planets in the Nth",
     pp. 17-40, its Rhetorius column) as this app compressed it, with no
     locator. Their pin is RHETORIUS_HALVES, a literal copy, so that the
     build which re-derives them from Rhetorius Ch. 57 and Mathesis III can
     retire it the way the lords table's transcription was retired. The
     Guide prints "?" for the Moon in the 6th and 8th there: those four
     halves are dashes and the transcription holds None.

The 9th-house Mercury PN IV halves the Guide prints against its own column
headings are settled by II.21, 8-9 (the good journey and true visions are
sentence 8, the suitable reading; the damage on the journey, the doubts in
religion and the bad visions are sentence 9, the bad-condition reading), the
way the code always kept them.

MASHAALLAH_LORDS is this app's paraphrase of Sahl's own sentence for each
[placed-in][ruled] pairing (On Nativities, the twelve lords-of-places
passages), shaped {'text', 'cite'}. Its pin is MASHAALLAH_LORDS_SENTENCES
below, the same kind of sentence-pin fixture: locator and three anchor words
per cell; the tests hold the cell side (locator well-formed, anchors present
in the text, the illegible cell marked by its footnote, no [UNCERTAIN]
marker, the count of empty cells the page states), and the checker verifies
the anchors against the sentences.
"""
from __future__ import annotations

import re

import pytest

PLANETS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']

# The Rhetorius halves, literal: the Guide's summary of Rhetorius Ch. 57 and
# Firmicus as this app compressed it (its Rhetorius column, pp. 17-40),
# {house: {planet: (Good, Bad)}}; None where the Guide prints "?". These
# halves carry no locator and are to be re-derived from the two texts; when
# they are, this transcription retires the way the lords table's did.
RHETORIUS_HALVES = {
    1: {
        'Saturn': ('Eldest sibling.', 'Sluggish, laborious.'),
        'Jupiter': ('Glorious, in charge.', 'Eldest, well nourished, parents lucky.'),
        'Mars': ('Military, leader.', 'Unstable, squandering.'),
        'Sun': ('Noble, lucky.', 'Less noble.'),
        'Venus': ('Talented, friends of powerful.', 'Lustful, lower professions.'),
        'Mercury': ('Intellectual activities.', 'Practical activities.'),
        'Moon': ('Increases of fortune, in charge.', 'Sailing, poor livelihood.'),
    },
    2: {
        'Saturn': ('Slow increase.', 'Loss, lazy, ill.'),
        'Jupiter': ('Good all around, inheritances.', 'Pretty good, more ups and downs.'),
        'Mars': ('Military; enough.', 'Exile, dangers.'),
        'Sun': ('Dignity, wealth.', 'Private property.'),
        'Venus': ('Prosperous, pleasing, arts.', 'Disruption.'),
        'Mercury': ('Evening star by night: good at business.', 'Morning star by night: obscure, bad, poor; evening star by day: good at learning, poor.'),
        'Moon': ('Brilliant, conspicuous, extravagant.', 'Family/actions dispersed and divided.'),
    },
    3: {
        'Saturn': ('Initiates, religious chiefs.', 'Recluses.'),
        'Jupiter': ('Balanced moderation.', 'Balanced moderation in gaining and spending.'),
        'Mars': ('Glory with labor.', 'Worse than by night?'),
        'Sun': ('Bad death for father; serious in counsel, manages public things, religious honors.', 'Lower services in temples, spend time in dirty places, irreligious, full of worry.'),
        'Venus': ('Good for marriage and being religious, especially with Jupiter.', 'See above.'),
        'Mercury': ('Divination, astrologers.', 'Priests, magicians.'),
        'Moon': ('With Saturn: slow, unsuccessful, sacrilegious (Firmicus).', 'Ignoble or infamous mother; sacrilege with Mercury or Mars; but good religious activities if with Jupiter.'),
    },
    4: {
        'Saturn': ('Lots of wealth.', 'Destroys/threatens parents, illness.'),
        'Jupiter': ('Commanders, jurists.', 'Middling assets.'),
        'Mars': ('Generals, soldiers.', 'Sickly, surgery.'),
        'Sun': ('Annoyances and interruptions in life, better in old age.', 'Destroys native, parents, and livelihood.'),
        'Venus': ('Fortunate over time, charming.', 'Loss of patrimony, widowhood.'),
        'Mercury': ('Lots of money, initiates.', 'Forbidden mysteries.'),
        'Moon': ('Honored mother, good living standard.', 'Lowborn mother, commerce.'),
    },
    5: {
        'Saturn': ('Kingships/command over time.', 'Delayed, sluggish.'),
        'Jupiter': ('Fortunate, honored, healthy.', 'Lower-status activities.'),
        'Mars': ('Good possessions, honor.', 'Harmful travel.'),
        'Sun': ('Honored, easy goals.', 'Moderate fortune, childless.'),
        'Venus': ('Prize-fighters, victors.', 'Worse than by day?'),
        'Mercury': ('Wealth, managing money.', 'Squanders money.'),
        'Moon': ('Gracious, leaders, fortunate.', 'Foreign travel, parents estranged, orphans.'),
    },
    6: {
        'Saturn': ('Moderate.', 'No inheritance, dangers from slaves.'),
        'Jupiter': ('Exposure, valuable materials.', 'Worse than by day.'),
        'Mars': ('Harms children, uneven life, illness (Firmicus).', 'Worse than by night?'),
        'Sun': ('With Jupiter and Venus, better than by night.', 'Bad death or condemnation for father if no star in the 10th (with one, good fortune from parents and resources).'),
        'Venus': ('Sex with low-quality women, treated badly by wives unless a planet is in the 10th, or difficulties in pregnancy; with a planet in the 10th, charm and good fortune through women.', 'See above.'),
        'Mercury': ('Advancement through speech/business.', 'Idle, evil.'),
        'Moon': (None, None),
    },
    7: {
        'Saturn': ('Success after delay, long-lived.', 'Sickly.'),
        'Jupiter': ('Long-lived, wealth later.', 'Moderate living.'),
        'Mars': ('Professions from fire/violence.', 'Violent, short-lived.'),
        'Sun': ('Administrators.', 'Lower-status activities.'),
        'Venus': ('Age difference/delay in marriage.', 'Lewdness.'),
        'Mercury': ('(Diurnal) Bad with Venus or Mars: lewd, brothel-keepers, fugitives.', '(Nocturnal) Managing affairs of women, good fortune from sex, numbers, arts or writings.'),
        'Moon': ('Changes, travel, better resources.', 'Foreign travel with dangers.'),
    },
    8: {
        'Saturn': ('Assets over time/inheritance.', 'Loss, bad death.'),
        'Jupiter': ('Acquisition, inheritance.', 'Acquisition, inheritance, over time.'),
        'Mars': ('Hot-heads, bright.', 'Patrimony spent, dangers.'),
        'Sun': ("Father's early death, healing.", 'See above.'),
        'Venus': ('Wealthy, benefit from death of women, easy death.', 'Marry late, lower-quality women, STDs, seizures.'),
        'Mercury': ('Money, management, inheritance.', 'Ineffective, lazy.'),
        'Moon': (None, None),
    },
    9: {
        'Saturn': ('Initiates, chief priests.', 'Recluses, anger at gods.'),
        'Jupiter': ('Predicting future, priesthood.', 'Unsteady, false speech.'),
        'Mars': ('Glory, unpunished.', 'Worse than by night?'),
        'Sun': ('Building sacred things, religious authority.', 'Harm in travels.'),
        'Venus': ('Divine men, gifts from temples.', 'Demon-afflicted, illicit sex.'),
        'Mercury': ('Priests, wizards.', 'Seers, sacrificers.'),
        'Moon': ('Living abroad, notable; benefiting from temples.', 'Wandering and dangers; temple servants.'),
    },
    10: {
        'Saturn': ('Leaders, farmers.', 'Bunglers, sorrow.'),
        'Jupiter': ('Athletes, famous, trusted.', 'Handsome but unstable.'),
        'Mars': ('Unstable, fearsome leaders.', 'No accomplishments, fugitives.'),
        'Sun': ('Rulers, leaders, dignity.', 'Success through violence.'),
        'Venus': ('Honored, musicians.', 'Blamed, burdened, indecent.'),
        'Mercury': ('Admirable, trusted.', 'Changes, living abroad.'),
        'Moon': ('Rulers, successful, trusted.', 'Hardship, unsteady, error.'),
    },
    11: {
        'Saturn': ('Middling goods over time.', 'Probably worse than by day.'),
        'Jupiter': ('Fortunate, renowned, authority.', 'Diminished effectiveness.'),
        'Mars': ('Many goods, dignity.', 'Same as when well placed.'),
        'Sun': ('Lucky, noble.', 'Harms children.'),
        'Venus': ('Powerful, trusted.', 'Sterility, unusual sexuality.'),
        'Mercury': ('Ingenious, accounts.', 'Spending, agents.'),
        'Moon': ('Rulers, favored, good from parents.', 'Living abroad, estrangements, orphanhood.'),
    },
    12: {
        'Saturn': ('More moderate than by night.', 'Loss of inheritance, mental disturbance.'),
        'Jupiter': ('Fights against superiors.', 'Worse than by day.'),
        'Mars': ('Better than by day.', 'Illness, injury, dangers from slaves, criminals.'),
        'Sun': ('Parents lowborn or slaves or captives; injuries and illness.', 'With infortunes, long illnesses, defects, slavery.'),
        'Venus': ('Distressed by women; if harmed, erotic derangement; low-status wives.', 'Ruined by women.'),
        'Mercury': ('Managing big affairs.', 'Danger from slaves.'),
        'Moon': ('Luckiness/authority (with fortunes).', 'Short life, humble; bad for patrimony/travel.'),
    },
}


# (house, planet, half, cite, anchors): the PN IV half's locator and three
# words the half's text shares with the cited sentence(s); ('', []) for a
# dash. Grid order: house, then planet, Good before Bad.
PN4_HALVES_SENTENCES = [
    (1, 'Saturn', 'Good', 'II.6, 1-2', ['villages', 'building', 'rivers']),
    (1, 'Saturn', 'Bad', 'II.6, 3', ['blamed', 'accused', 'detestable']),
    (1, 'Jupiter', 'Good', 'II.9, 1-2', ['celebrated', 'respected', 'motives']),
    (1, 'Jupiter', 'Bad', 'II.9, 3', ['scarcity', 'eagerness', 'worries']),
    (1, 'Mars', 'Good', 'II.12, 1-2', ['awe', 'wars', 'contends']),
    (1, 'Mars', 'Bad', 'II.12, 3-5', ['conflagration', 'robbers', 'iron']),
    (1, 'Sun', 'Good', 'II.15, 1-2', ['renowned', 'voice', 'sultan']),
    (1, 'Sun', 'Bad', 'II.15, 3', ['detestable', 'benefit', 'fear']),
    (1, 'Venus', 'Good', 'II.18, 1-2', ['gates', 'kings', 'spoiled']),
    (1, 'Venus', 'Bad', 'II.18, 3-4', ['paralysis', 'pleurisy', 'stolen']),
    (1, 'Mercury', 'Good', 'II.21, 1', ['writing', 'sciences', 'preservation']),
    (1, 'Mercury', 'Bad', 'II.21, 2', ['writers', 'calculation', 'accused']),
    (1, 'Moon', 'Good', 'VII.8, 1', ['preserved', 'endearing', 'lawsuits']),
    (1, 'Moon', 'Bad', '', []),
    (2, 'Saturn', 'Good', 'II.6, 12-13', ['assets', 'hoped', 'sowing']),
    (2, 'Saturn', 'Bad', 'II.6, 14', ['vegetation', 'fields', 'sinking']),
    (2, 'Jupiter', 'Good', 'II.9, 10', ['leisure', 'scarcity', 'dead']),
    (2, 'Jupiter', 'Bad', 'II.9, 11', ['spending', 'cheerfulness', 'contention']),
    (2, 'Mars', 'Good', 'II.12, 11', ['benefit', 'direction', 'aware']),
    (2, 'Mars', 'Bad', 'II.12, 12', ['spend', 'money', 'squander']),
    (2, 'Sun', 'Good', 'II.15, 8', ['temperedness', 'leisure', 'revenue']),
    (2, 'Sun', 'Bad', 'II.15, 9', ['scarcity', 'negligence', 'laziness']),
    (2, 'Venus', 'Good', 'II.18, 10', ['underclass', 'base', 'work']),
    (2, 'Venus', 'Bad', 'II.18, 11', ['negligence', 'idleness', 'stagnation']),
    (2, 'Mercury', 'Good', 'II.21, 10', ['selling', 'buying', 'praised']),
    (2, 'Mercury', 'Bad', 'II.21, 11', ['downturn', 'incriminated', 'quarrel']),
    (2, 'Moon', 'Good', '', []),
    (2, 'Moon', 'Bad', 'VII.8, 2', ['revenue', 'mountains', 'deserts']),
    (3, 'Saturn', 'Good', 'II.6, 7-8', ['reward', 'toil', 'foreigners']),
    (3, 'Saturn', 'Bad', 'II.6, 9-11', ['gossip', 'worship', 'theft']),
    (3, 'Jupiter', 'Good', 'II.9, 8', ['piety', 'brothers', 'reports']),
    (3, 'Jupiter', 'Bad', 'II.9, 9', ['negligent', 'doubts', 'brothers']),
    (3, 'Mars', 'Good', 'II.12, 9', ['travel', 'strong', 'praised']),
    (3, 'Mars', 'Bad', 'II.12, 10', ['false', 'hardship', 'wild']),
    (3, 'Sun', 'Good', 'II.15, 6', ['beautiful', 'religion', 'relatives']),
    (3, 'Sun', 'Bad', 'II.15, 7', ['ugly', 'journey', 'relatives']),
    (3, 'Venus', 'Good', 'II.18, 8', ['journey', 'dressed', 'kind']),
    (3, 'Venus', 'Bad', 'II.18, 9', ['defamed', 'distant', 'selling']),
    (3, 'Mercury', 'Good', 'II.21, 8', ['visions', 'interpretation', 'insight']),
    (3, 'Mercury', 'Bad', 'II.21, 9', ['damage', 'doubts', 'visions']),
    (3, 'Moon', 'Good', 'VII.8, 3', ['messengers', 'mock', 'leaders']),
    (3, 'Moon', 'Bad', '', []),
    (4, 'Saturn', 'Good', 'II.6, 1-2', ['villages', 'building', 'rivers']),
    (4, 'Saturn', 'Bad', 'II.6, 3', ['blamed', 'accused', 'detestable']),
    (4, 'Jupiter', 'Good', 'II.9, 1-2', ['celebrated', 'fathers', 'estate']),
    (4, 'Jupiter', 'Bad', 'II.9, 3', ['scarcity', 'eagerness', 'worries']),
    (4, 'Mars', 'Good', 'II.12, 1-2', ['awe', 'wars', 'contends']),
    (4, 'Mars', 'Bad', 'II.12, 3-5', ['conflagration', 'dwelling', 'rescued']),
    (4, 'Sun', 'Good', 'II.15, 1-2', ['estate', 'fathers', 'old']),
    (4, 'Sun', 'Bad', 'II.15, 3', ['detestable', 'benefit', 'fear']),
    (4, 'Venus', 'Good', 'II.18, 1-2', ['gates', 'kings', 'spoiled']),
    (4, 'Venus', 'Bad', 'II.18, 3-5', ['paralysis', 'stolen', 'die']),
    (4, 'Mercury', 'Good', 'II.21, 1', ['writing', 'sciences', 'preservation']),
    (4, 'Mercury', 'Bad', 'II.21, 2-4', ['calculation', 'accused', 'contention']),
    (4, 'Moon', 'Good', '', []),
    (4, 'Moon', 'Bad', 'VII.8, 4', ['nobles', 'interpretation', 'disagreement']),
    (5, 'Saturn', 'Good', 'II.6, 4', ['friends', 'guarantees', 'building']),
    (5, 'Saturn', 'Bad', 'II.6, 5-6', ['brothers', 'shortage', 'retrograde']),
    (5, 'Jupiter', 'Good', 'II.9, 6', ['blessed', 'children', 'root']),
    (5, 'Jupiter', 'Bad', 'II.9, 7', ['children', 'messengers', 'gifts']),
    (5, 'Mars', 'Good', 'II.12, 6-7', ['allies', 'fire', 'blood']),
    (5, 'Mars', 'Bad', 'II.12, 8', ['accidents', 'feuding', 'brothers']),
    (5, 'Sun', 'Good', 'II.15, 4', ['food', 'clothing', 'crops']),
    (5, 'Sun', 'Bad', 'II.15, 5', ['undermine', 'contend', 'children']),
    (5, 'Venus', 'Good', 'II.18, 6', ['friends', 'possessions', 'root']),
    (5, 'Venus', 'Bad', 'II.18, 7', ['purpose', 'hostile', 'friends']),
    (5, 'Mercury', 'Good', 'II.21, 5', ['nobles', 'business', 'children']),
    (5, 'Mercury', 'Bad', 'II.21, 6-7', ['hostile', 'slowness', 'confused']),
    (5, 'Moon', 'Good', '', []),
    (5, 'Moon', 'Bad', 'VII.8, 5', ['female', 'slaves', 'conflicting']),
    (6, 'Saturn', 'Good', 'II.6, 16-18', ['moisture', 'remedies', 'escape']),
    (6, 'Saturn', 'Bad', 'II.6, 16-18', ['pleurisy', 'chronic', 'ruin']),
    (6, 'Jupiter', 'Good', 'II.9, 12', ['lowest', 'confined', 'peace']),
    (6, 'Jupiter', 'Bad', 'II.9, 13', ['windiness', 'enemies', 'confinement']),
    (6, 'Mars', 'Good', 'II.12, 17', ['body', 'healthy', 'victorious']),
    (6, 'Mars', 'Bad', 'II.12, 18-19', ['moisture', 'disturbance', 'bile']),
    (6, 'Sun', 'Good', 'II.15, 10', ['mild', 'temperedness', 'safety']),
    (6, 'Sun', 'Bad', 'II.15, 11', ['dryness', 'eyes', 'head']),
    (6, 'Venus', 'Good', 'II.18, 13', ['underclass', 'remedies', 'provisions']),
    (6, 'Venus', 'Bad', 'II.18, 14', ['essence', 'bile', 'heat']),
    (6, 'Mercury', 'Good', 'II.21, 12', ['eager', 'business', 'underclass']),
    (6, 'Mercury', 'Bad', 'II.21, 13', ['windiness', 'seized', 'confinement']),
    (6, 'Moon', 'Good', '', []),
    (6, 'Moon', 'Bad', 'VII.8, 6', ['hands', 'hunting', 'slaves']),
    (7, 'Saturn', 'Good', 'II.6, 1-2', ['villages', 'building', 'rivers']),
    (7, 'Saturn', 'Bad', 'II.6, 3', ['blamed', 'accused', 'detestable']),
    (7, 'Jupiter', 'Good', 'II.9, 1-2', ['celebrated', 'women', 'antagonists']),
    (7, 'Jupiter', 'Bad', 'II.9, 3', ['scarcity', 'eagerness', 'worries']),
    (7, 'Mars', 'Good', 'II.12, 1-2', ['awe', 'wars', 'contends']),
    (7, 'Mars', 'Bad', 'II.12, 3-5', ['conflagration', 'cutting', 'victorious']),
    (7, 'Sun', 'Good', 'II.15, 1-2', ['managements', 'victorious', 'healthy']),
    (7, 'Sun', 'Bad', 'II.15, 3', ['detestable', 'benefit', 'fear']),
    (7, 'Venus', 'Good', 'II.18, 1-2', ['gates', 'kings', 'spoiled']),
    (7, 'Venus', 'Bad', 'II.18, 3-4', ['paralysis', 'pleurisy', 'stolen']),
    (7, 'Mercury', 'Good', 'II.21, 1', ['writing', 'sciences', 'preservation']),
    (7, 'Mercury', 'Bad', 'II.21, 2-4', ['calculation', 'accused', 'contention']),
    (7, 'Moon', 'Good', 'VII.8, 7', ['friendliness', 'maxims', 'worship']),
    (7, 'Moon', 'Bad', '', []),
    (8, 'Saturn', 'Good', 'II.6, 15', ['dead', 'received', 'house']),
    (8, 'Saturn', 'Bad', 'II.6, 15', ['squandering', 'ancestors', 'destruction']),
    (8, 'Jupiter', 'Good', 'II.9, 10', ['leisure', 'scarcity', 'dead']),
    (8, 'Jupiter', 'Bad', 'II.9, 11', ['spending', 'cheerfulness', 'contention']),
    (8, 'Mars', 'Good', 'II.12, 13', ['dead', 'ancestors', 'inheritances']),
    (8, 'Mars', 'Bad', 'II.12, 14', ['detestable', 'quarrels', 'squandered']),
    (8, 'Sun', 'Good', 'II.15, 8', ['temperedness', 'leisure', 'revenue']),
    (8, 'Sun', 'Bad', 'II.15, 9', ['scarcity', 'negligence', 'laziness']),
    (8, 'Venus', 'Good', 'II.18, 10', ['underclass', 'eighth', 'spending']),
    (8, 'Venus', 'Bad', 'II.18, 12', ['leisure', 'scarcity', 'contention']),
    (8, 'Mercury', 'Good', 'II.21, 10', ['selling', 'buying', 'praised']),
    (8, 'Mercury', 'Bad', 'II.21, 11', ['downturn', 'incriminated', 'quarrel']),
    (8, 'Moon', 'Good', '', []),
    (8, 'Moon', 'Bad', 'VII.8, 8', ['humiliation', 'degradation', 'farms']),
    (9, 'Saturn', 'Good', 'II.6, 7-8', ['reward', 'toil', 'foreigners']),
    (9, 'Saturn', 'Bad', 'II.6, 9-11', ['gossip', 'worship', 'theft']),
    (9, 'Jupiter', 'Good', 'II.9, 8', ['piety', 'brothers', 'reports']),
    (9, 'Jupiter', 'Bad', 'II.9, 9', ['negligent', 'doubts', 'brothers']),
    (9, 'Mars', 'Good', 'II.12, 9', ['travel', 'strong', 'praised']),
    (9, 'Mars', 'Bad', 'II.12, 10', ['false', 'hardship', 'wild']),
    (9, 'Sun', 'Good', 'II.15, 6', ['beautiful', 'religion', 'relatives']),
    (9, 'Sun', 'Bad', 'II.15, 7', ['ugly', 'journey', 'relatives']),
    (9, 'Venus', 'Good', 'II.18, 8', ['journey', 'dressed', 'kind']),
    (9, 'Venus', 'Bad', 'II.18, 9', ['defamed', 'distant', 'selling']),
    (9, 'Mercury', 'Good', 'II.21, 8', ['visions', 'interpretation', 'insight']),
    (9, 'Mercury', 'Bad', 'II.21, 9', ['damage', 'doubts', 'visions']),
    (9, 'Moon', 'Good', 'VII.8, 9', ['banquets', 'maxims', 'joyful']),
    (9, 'Moon', 'Bad', '', []),
    (10, 'Saturn', 'Good', 'II.6, 1-2', ['villages', 'building', 'rivers']),
    (10, 'Saturn', 'Bad', 'II.6, 3', ['blamed', 'accused', 'detestable']),
    (10, 'Jupiter', 'Good', 'II.9, 1-2', ['celebrated', 'respected', 'importance']),
    (10, 'Jupiter', 'Bad', 'II.9, 3', ['scarcity', 'eagerness', 'worries']),
    (10, 'Mars', 'Good', 'II.12, 1-2', ['awe', 'wars', 'midheaven']),
    (10, 'Mars', 'Bad', 'II.12, 3-5', ['conflagration', 'robbers', 'iron']),
    (10, 'Sun', 'Good', 'II.15, 1-2', ['renowned', 'voice', 'sultan']),
    (10, 'Sun', 'Bad', 'II.15, 3', ['detestable', 'benefit', 'fear']),
    (10, 'Venus', 'Good', 'II.18, 1-2', ['gates', 'kings', 'spoiled']),
    (10, 'Venus', 'Bad', 'II.18, 3-4', ['paralysis', 'pleurisy', 'stolen']),
    (10, 'Mercury', 'Good', 'II.21, 1', ['writing', 'sciences', 'preservation']),
    (10, 'Mercury', 'Bad', 'II.21, 2', ['writers', 'calculation', 'accused']),
    (10, 'Moon', 'Good', 'VII.8, 10', ['moist', 'gardens', 'lawsuits']),
    (10, 'Moon', 'Bad', '', []),
    (11, 'Saturn', 'Good', 'II.6, 4', ['friends', 'guarantees', 'building']),
    (11, 'Saturn', 'Bad', 'II.6, 5-6', ['brothers', 'shortage', 'retrograde']),
    (11, 'Jupiter', 'Good', 'II.9, 4', ['commended', 'friends', 'delighted']),
    (11, 'Jupiter', 'Bad', 'II.9, 5', ['worries', 'hopes', 'wishes']),
    (11, 'Mars', 'Good', 'II.12, 6-7', ['allies', 'fire', 'blood']),
    (11, 'Mars', 'Bad', 'II.12, 8', ['accidents', 'feuding', 'brothers']),
    (11, 'Sun', 'Good', 'II.15, 4', ['food', 'clothing', 'crops']),
    (11, 'Sun', 'Bad', 'II.15, 5', ['undermine', 'contend', 'children']),
    (11, 'Venus', 'Good', 'II.18, 6', ['friends', 'possessions', 'root']),
    (11, 'Venus', 'Bad', 'II.18, 7', ['purpose', 'hostile', 'friends']),
    (11, 'Mercury', 'Good', 'II.21, 5', ['nobles', 'business', 'children']),
    (11, 'Mercury', 'Bad', 'II.21, 6-7', ['hostile', 'slowness', 'confused']),
    (11, 'Moon', 'Good', 'VII.8, 11', ['towns', 'villages', 'debts']),
    (11, 'Moon', 'Bad', '', []),
    (12, 'Saturn', 'Good', 'II.6, 19', ['victorious', 'enemies', 'befriend']),
    (12, 'Saturn', 'Bad', 'II.6, 20-21', ['prison', 'confinement', 'torment']),
    (12, 'Jupiter', 'Good', 'II.9, 12', ['lowest', 'confined', 'peace']),
    (12, 'Jupiter', 'Bad', 'II.9, 13', ['windiness', 'enemies', 'confinement']),
    (12, 'Mars', 'Good', 'II.12, 15', ['runaways', 'confined', 'safe']),
    (12, 'Mars', 'Bad', 'II.12, 16', ['detestable', 'directions', 'affect']),
    (12, 'Sun', 'Good', 'II.15, 12', ['beautiful', 'spoken', 'safe']),
    (12, 'Sun', 'Bad', 'II.15, 13', ['confinement', 'banished', 'country']),
    (12, 'Venus', 'Good', 'II.18, 13', ['underclass', 'remedies', 'provisions']),
    (12, 'Venus', 'Bad', 'II.18, 15', ['enemies', 'confined', 'punishment']),
    (12, 'Mercury', 'Good', 'II.21, 12', ['eager', 'business', 'underclass']),
    (12, 'Mercury', 'Bad', 'II.21, 13', ['windiness', 'seized', 'confinement']),
    (12, 'Moon', 'Good', '', []),
    (12, 'Moon', 'Bad', 'VII.8, 12', ['guarantor', 'collateral', 'victorious']),
]


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


PN4_CITE = re.compile(r"^(II\.\d+|VII\.8), \d+(-\d+)?$")
PN4_DASH = {'text': '\u2014', 'cite': ''}
# What the page help states of the PN IV halves with no sentence: twelve, all
# the Moon's (VII.8 gives her one reading per house, so the other half is a
# dash); and of the Rhetorius halves: four, the Moon in the 6th and 8th,
# where the Guide prints "?".
PN4_DASHES_THE_HELP_STATES = 12
RHETORIUS_DASHES_THE_HELP_STATES = 4


def test_planets_in_houses_has_the_two_source_shape(engine):
    ph = engine["PLANETS_IN_HOUSES"]
    assert set(ph) == set(range(1, 13))
    for house in ph:
        assert set(ph[house]) == set(PLANETS)
        for cell in ph[house].values():
            assert set(cell) == {'Rhetorius', 'PN IV'}
            for source in cell.values():
                assert set(source) == {'Good', 'Bad'}
                for half in source.values():
                    assert set(half) == {'text', 'cite'} and half['text'].strip()


def test_the_pn4_fixture_covers_every_half_once():
    keys = [(h, p, x) for h, p, x, _c, _a in PN4_HALVES_SENTENCES]
    assert keys == [(h, p, x) for h in range(1, 13) for p in PLANETS for x in ('Good', 'Bad')]
    assert len(keys) == 168


@pytest.mark.parametrize("house, planet, half, cite, anchors", PN4_HALVES_SENTENCES,
                         ids=[f"{p}-in-{h}-{x}" for h, p, x, _c, _a in PN4_HALVES_SENTENCES])
def test_pn4_half_is_pinned_to_its_sentence(engine, house, planet, half, cite, anchors):
    cell = engine["PLANETS_IN_HOUSES"][house][planet]['PN IV'][half]
    assert "[UNCERTAIN" not in cell["text"]
    if cite == "":
        assert cell == PN4_DASH and anchors == [], (house, planet, half, cell)
        return
    assert cell["cite"] == cite and PN4_CITE.match(cite), (house, planet, half, cell["cite"])
    assert cell["text"] != PN4_DASH["text"]
    assert len(anchors) == 3 and set(anchors) <= _words(cell["text"]), (house, planet, half, anchors, cell["text"])


@pytest.mark.parametrize("house", range(1, 13))
def test_the_moons_pn4_reading_is_vii8_by_transit_one_half_per_house(engine, house):
    # II.22 has no houses list for the Moon; fn 312 sends the reader to VII.8,
    # her transit through the twelve houses. One sentence per house, placed
    # in the half its balance belongs to, the other half a dash.
    cell = engine["PLANETS_IN_HOUSES"][house]["Moon"]["PN IV"]
    filled = [x for x in ('Good', 'Bad') if cell[x] != PN4_DASH]
    assert len(filled) == 1, cell
    assert cell[filled[0]]["cite"] == f"VII.8, {house}"
    assert cell[filled[0]]["text"].startswith("By transit:")


def test_the_pn4_halves_split_only_where_book_ii_splits(engine):
    # Every Saturn-Mercury half has its own sentence: no dash outside the
    # Moon's row.
    ph = engine["PLANETS_IN_HOUSES"]
    dashes = [(h, p, x) for h in ph for p in PLANETS for x in ('Good', 'Bad') if ph[h][p]['PN IV'][x] == PN4_DASH]
    assert all(p == "Moon" for _h, p, _x in dashes), dashes
    assert len(dashes) == PN4_DASHES_THE_HELP_STATES


def test_mercury_in_the_ninth_reads_as_ii21_8_and_9(engine):
    # The Guide prints these two halves against its own headings; II.21, 8
    # (the journey he loves, true visions) is the suitable reading and 9 the
    # bad-condition one, as the code always had them.
    cell = engine["PLANETS_IN_HOUSES"][9]["Mercury"]["PN IV"]
    assert cell["Good"]["cite"] == "II.21, 8" and "true interpretation" in cell["Good"]["text"]
    assert cell["Bad"]["cite"] == "II.21, 9" and "bad visions" in cell["Bad"]["text"]


@pytest.mark.parametrize("house", range(1, 13))
def test_rhetorius_halves_are_the_guide_transcription_verbatim(engine, house):
    for planet in PLANETS:
        cell = engine["PLANETS_IN_HOUSES"][house][planet]["Rhetorius"]
        good, bad = RHETORIUS_HALVES[house][planet]
        assert cell["Good"] == ({'text': good, 'cite': ''} if good else PN4_DASH), (house, planet, cell["Good"])
        assert cell["Bad"] == ({'text': bad, 'cite': ''} if bad else PN4_DASH), (house, planet, cell["Bad"])


def test_the_rhetorius_dashes_are_the_guides_question_marks(engine):
    ph = engine["PLANETS_IN_HOUSES"]
    dashes = {(h, p, x) for h in ph for p in PLANETS for x in ('Good', 'Bad') if ph[h][p]['Rhetorius'][x] == PN4_DASH}
    assert dashes == {(6, "Moon", "Good"), (6, "Moon", "Bad"), (8, "Moon", "Good"), (8, "Moon", "Bad")}
    assert len(dashes) == RHETORIUS_DASHES_THE_HELP_STATES
    assert not any("[UNCERTAIN" in ph[h][p][s][x]["text"] for h in ph for p in PLANETS
                   for s in ('Rhetorius', 'PN IV') for x in ('Good', 'Bad'))


def test_the_planets_reader_prints_both_halves_with_the_pn4_locator(engine):
    # One column = "Rhetorius: <text> · PN IV: <text> (<locator>)"; a dash
    # prints as a dash and carries no locator.
    fmt = engine["planets_in_houses_cell"]
    assert fmt(9, "Mercury", "Good") == ("Rhetorius: Priests, wizards. \u00b7 PN IV: "
                                        + engine["PLANETS_IN_HOUSES"][9]["Mercury"]["PN IV"]["Good"]["text"] + " (II.21, 8)")
    assert fmt(6, "Moon", "Good") == "Rhetorius: \u2014 \u00b7 PN IV: \u2014"
    assert fmt(1, "Moon", "Bad") == "Rhetorius: Sailing, poor livelihood. \u00b7 PN IV: \u2014"
    planets = {p: {'longitude': lon} for p, lon in
               [('Saturn', 10.0), ('Jupiter', 40.0), ('Mars', 70.0), ('Sun', 100.0),
                ('Venus', 130.0), ('Mercury', 160.0), ('Moon', 190.0)]}
    cond = {p: {'Net': 0, 'Condition': 'Good'} for p in planets}
    rows = engine["evaluate_planets_in_houses"](planets, cond, 0.0)
    assert len(rows) == 7
    for row in rows:
        h = row['Placed in (WS place)']
        assert row['If Well Placed'] == fmt(h, row['Planet'], 'Good')
        assert row['If Badly Placed'] == fmt(h, row['Planet'], 'Bad')



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
