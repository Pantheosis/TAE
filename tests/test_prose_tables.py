"""The two prose delineation tables, pinned by content -- 2026-09-08, the
lords half re-made 2026-09-16, the planets half's PN IV column the same
day, its Rhetorius column the same day; the Rhetorius column re-shaped as a
testimony list and the PN IV halves re-headed 2026-09-17.

PLANETS_IN_HOUSES[house][planet] is {'Rhetorius': [entries], 'PN IV':
{'Good': {'text', 'cite'}, 'Bad': {'text', 'cite'}}}. Both are pinned by
sentence:

  1. The Rhetorius list is this app's paraphrases of Rhetorius, Astrological
     Compendium Ch. 57 (Holden), the significations of the twelve houses,
     and of Firmicus, Mathesis III.2-III.7 and III.13 (Dykes), the planets in
     the twelve places -- one tradition, two witnesses kept apart. Neither
     text divides a planet's reading into well and badly placed; they divide
     by sect and by conditions, so the column is a LIST of entries {'author',
     'cite', 'axis', 'text', 'portional', 'conditional'}: the author one of
     RHETORIUS_AUTHORS ('Rhetorius, as summarized by Dykes' for Dykes's fnn
     284-285 to III.13, which supply Rhetorius's Moon in the fifth and
     seventh where Firmicus's sentences are lost); the axis the author's own
     division, never converted -- 'by day', 'by night', 'in sect', 'out of
     sect', 'unsplit' where the sentence makes no such division, 'general
     malefic' / 'general benefic' for Ch. 57's class sentences entered for
     Saturn and Mars, and for Jupiter and Venus; the text with every
     condition its sentence states; 'portional' where Firmicus states the
     placement so, or where the cited run refers back to the place's opening
     sentence that states it (III.2, 4-5; 30; 41-43; 44-48; III.4, 22-25;
     80-81), never where he says "in this sign" (III.2, 18); 'conditional' where the whole reading rests on a stated
     configuration (the reader sends those to the row's detail when a cell
     runs past RHETORIUS_CELL_WORDS, never trimming them). Their pin is
     RHETORIUS_ENTRIES: one row per entry, in list order -- house, planet,
     author, axis, the locator (Rhetorius by chapter, house and Holden's page
     or pages, "Ch. 57, the sixth, p. 76", "pp. 57-61", "pp. 65, 88-89";
     Firmicus by chapter and sentence or run, "III.2, 8", "III.2, 4-5"; the
     summaries "III.13 fn 284" / "fn 285") -- and three anchor words the
     entry's text and the cited passage share (for a Rhetorius cite, on the
     cited pages; for a Firmicus cite, in the cited sentences; for a summary,
     in the footnote). No cell's list is empty; an empty list would print as a
     dash, which the help defines as the absence of testimony.
  2. The PN IV halves are this app's paraphrases of Abu Ma'shar's Book II
     chapters on the lord of the year in the houses (II.6 Saturn, II.9
     Jupiter, II.12 Mars, II.15 the Sun, II.18 Venus, II.21 Mercury) applied
     to natal planets, headed 'If in a suitable condition' / 'If in a bad
     condition' -- Book II's division is the planet's condition, the house
     among its factors. A grouped house's locator names the sharing ("II.6, 4
     (shared with the 5th)"); Saturn's four falling places (II.6, 22-24) are
     carried whole beside his second, sixth, eighth and twelfth; Mercury's
     II.21, 8 says that its sentence states no condition. Their pin is
     PN4_HALVES_SENTENCES, the same shape as before. The Moon has no Book II
     houses chapter (II.22, 13 fn 312), and VII.8, her transit through the
     twelve houses, supplies no condition split: her two halves are the
     pointer text MOON_POINTER with cite '', and her twelve readings are
     MOON_IN_HOUSES_VII8, one unsplit reading per house, pinned by
     MOON_VII8_SENTENCES (house, cite, anchors).

The corpus is private, so the fixtures carry the anchors, not the
sentences; the tests hold the cell side (locator well-formed, the house
named in a Ch. 57 locator the cell's house, pages and sentences ascending,
anchors in the text, the counts the help states, no [UNCERTAIN] marker, no
Guide wording, the readers' formats) and the checker verifies the anchors
against the sentences.

The 9th-house Mercury PN IV halves the Guide prints against its own column
headings are settled by II.21, 8-9 (the good journey and true visions are
sentence 8, the suitable reading, whose sentence states no condition; the
damage on the journey, the doubts in religion and the bad visions are
sentence 9, the bad-condition reading), the way the code always kept them.

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

from conftest import make_app, assert_no_exception

PLANETS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']

# (house, planet, author, axis, cite, anchors): one row per entry of the
# Rhetorius list, in list order within the cell, cells in grid order (house,
# then planet). The anchors are three words the entry's text shares with
# the cited passage.
RHETORIUS_ENTRIES = [
    (1, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the first, pp. 51-52', ['brothers', 'destroys', 'angular']),
    (1, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the first, p. 52', ['opposition', 'hardships', 'actions']),
    (1, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the first, p. 48', ['raised', 'born', 'first']),
    (1, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the first, p. 48', ['ascendant', 'injured', 'reared']),
    (1, 'Saturn', 'Firmicus', 'by day', 'III.2, 1-3', ['encouraged', 'announced', 'destroyed']),
    (1, 'Saturn', 'Firmicus', 'by day', 'III.2, 4-5', ['ascension', 'patrimony', 'slipping']),
    (1, 'Saturn', 'Firmicus', 'by night', 'III.2, 6-7', ['sluggishness', 'laborious', 'hindered']),
    (1, 'Jupiter', 'Rhetorius', 'in sect', 'Ch. 57, the first, p. 52', ['destruction', 'pleasantly', 'ingenious']),
    (1, 'Jupiter', 'Rhetorius', 'out of sect', 'Ch. 57, the first, p. 52', ['happiness', 'brothers', 'destroys']),
    (1, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the first, p. 49', ['commanders', 'fatherland', 'malefics']),
    (1, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the first, p. 48', ['triplicity', 'ascendant', 'nourished']),
    (1, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 1-2', ['benevolent', 'domiciles', 'charming']),
    (1, 'Jupiter', 'Firmicus', 'by night', 'III.3, 3-5', ['luckiness', 'nourished', 'principal']),
    (1, 'Mars', 'Rhetorius', 'in sect', 'Ch. 57, the first, p. 52', ['commanders', 'countries', 'military']),
    (1, 'Mars', 'Rhetorius', 'out of sect', 'Ch. 57, the first, p. 52', ['undertakings', 'craftsmen', 'military']),
    (1, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the first, p. 48', ['foolhardy', 'reckless', 'injured']),
    (1, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the first, p. 48', ['ascendant', 'injured', 'reared']),
    (1, 'Mars', 'Firmicus', 'by night', 'III.4, 1-3', ['extravagant', 'indignation', 'portionally']),
    (1, 'Mars', 'Firmicus', 'by day', 'III.4, 4-6', ['portionally', 'squandered', 'patrimony']),
    (1, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the first, pp. 48, 52-53', ['advancement', 'commanders', 'jealousies']),
    (1, 'Sun', 'Rhetorius', 'by night', 'Ch. 57, the first, p. 53', ['possessions', 'opposition', 'destroyer']),
    (1, 'Sun', 'Firmicus', 'unsplit', 'III.5, 1-2', ['difficulty', 'masculine', 'protected']),
    (1, 'Sun', 'Firmicus', 'by day', 'III.5, 4-5', ['difficulties', 'generalships', 'hindrances']),
    (1, 'Sun', 'Firmicus', 'unsplit', 'III.5, 16', ['broadly', 'clever', 'marker']),
    (1, 'Sun', 'Firmicus', 'by night', 'III.5, 21-23', ['dissipates', 'patrimony', 'substance']),
    (1, 'Venus', 'Rhetorius', 'in sect', 'Ch. 57, the first, pp. 53-54', ['quadrupedal', 'allowances', 'predicting']),
    (1, 'Venus', 'Rhetorius', 'out of sect', 'Ch. 57, the first, p. 54', ['reprehensible', 'promiscuous', 'inventors']),
    (1, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the first, p. 48', ['promiscuous', 'agreeable', 'cheerful']),
    (1, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the first, p. 48', ['triplicity', 'ascendant', 'nourished']),
    (1, 'Venus', 'Firmicus', 'by night', 'III.6, 1-8', ['magnificent', 'portionally', 'provisions']),
    (1, 'Venus', 'Firmicus', 'by day', 'III.6, 9-10', ['decorators', 'themselves', 'disgraced']),
    (1, 'Mercury', 'Rhetorius', 'by day', 'Ch. 57, the first, p. 54', ['philosophers', 'transactions', 'grammarians']),
    (1, 'Mercury', 'Rhetorius', 'by night', 'Ch. 57, the first, p. 54', ['disbursements', 'accomplished', 'governmental']),
    (1, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the first, p. 48', ['intelligent', 'ingenious', 'prudent']),
    (1, 'Mercury', 'Firmicus', 'by day', 'III.7, 1-2', ['philosophers', 'experienced', 'grammatical']),
    (1, 'Mercury', 'Firmicus', 'by day', 'III.7, 3-4', ['portionally', 'designated', 'prosperous']),
    (1, 'Mercury', 'Firmicus', 'by night', 'III.7, 5-6', ['transactions', 'instruments', 'respectable']),
    (1, 'Moon', 'Rhetorius', 'in sect', 'Ch. 57, the first, pp. 54-55', ['appearances', 'opposition', 'vespertine']),
    (1, 'Moon', 'Rhetorius', 'by day', 'Ch. 57, the first, pp. 55-56', ['opposition', 'sicknesses', 'important']),
    (1, 'Moon', 'Firmicus', 'by night', 'III.13, 1', ['increases', 'brothers', 'rejoices']),
    (1, 'Moon', 'Firmicus', 'by day', 'III.13, 2-4', ['inaccessible', 'helmsmen', 'wildness']),
    (2, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the second, p. 59', ['disturbances', 'inheritance', 'livelihood']),
    (2, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the second, p. 59', ['undistinguished', 'livelihood', 'getting']),
    (2, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the second, p. 56', ['impractical', 'individuals', 'injuries']),
    (2, 'Saturn', 'Firmicus', 'by night', 'III.2, 8-11', ['destructions', 'destitute', 'illnesses']),
    (2, 'Saturn', 'Firmicus', 'by day', 'III.2, 12-13', ['activities', 'themselves', 'increases']),
    (2, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the second, pp. 59-60', ['inheritances', 'buildings', 'someone']),
    (2, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the second, p. 56', ['benefics', 'dwelling', 'denote']),
    (2, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 8', ['inheritances', 'possessions', 'foreigners']),
    (2, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 9', ['changeable', 'diversity', 'actions']),
    (2, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the second, p. 60', ['circumstances', 'enslavement', 'necessities']),
    (2, 'Mars', 'Rhetorius', 'by night', 'Ch. 57, the second, p. 60', ['activities', 'campaigns', 'military']),
    (2, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the second, pp. 56-57', ['livelihood', 'injuries', 'fortune']),
    (2, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the second, p. 56', ['impractical', 'individuals', 'injuries']),
    (2, 'Mars', 'Firmicus', 'by day', 'III.4, 8-11', ['misfortunes', 'necessities', 'territories']),
    (2, 'Mars', 'Firmicus', 'by night', 'III.4, 12-13', ['athletes', 'soldiers', 'dangers']),
    (2, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the second, p. 60', ['existence', 'pleasant', 'property']),
    (2, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the second, p. 57', ['inheritance', 'partilely', 'deprived']),
    (2, 'Sun', 'Firmicus', 'unsplit', 'III.5, 24-28', ['contrarieties', 'hindrance', 'patrimony']),
    (2, 'Venus', 'Rhetorius', 'by day', 'Ch. 57, the second, p. 60', ['marriages', 'disputes', 'living']),
    (2, 'Venus', 'Rhetorius', 'by night', 'Ch. 57, the second, p. 60', ['delightful', 'prosperous', 'fortunate']),
    (2, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the second, p. 57', ['vespertine', 'abounding', 'mysteries']),
    (2, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the second, p. 56', ['benefics', 'dwelling', 'denote']),
    (2, 'Venus', 'Firmicus', 'by night', 'III.6, 13', ['overflowing', 'conferred', 'inventors']),
    (2, 'Venus', 'Firmicus', 'by day', 'III.6, 14-16', ['contrarieties', 'ineffective', 'powerfully']),
    (2, 'Mercury', 'Rhetorius', 'by night', 'Ch. 57, the second, pp. 60-61', ['livelihood', 'vespertine', 'merchants']),
    (2, 'Mercury', 'Rhetorius', 'by day', 'Ch. 57, the second, p. 61', ['themselves', 'learning', 'peculiar']),
    (2, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the second, p. 57', ['inquisitive', 'intelligent', 'uninitiated']),
    (2, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 7', ['destitute', 'estranged', 'knowledge']),
    (2, 'Mercury', 'Firmicus', 'by night', 'III.7, 8', ['procuring', 'business', 'interest']),
    (2, 'Mercury', 'Firmicus', 'by day', 'III.7, 9', ['philologists', 'experienced', 'discipline']),
    (2, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the second, p. 57', ['cataracts', 'saturn', 'eyes']),
    (2, 'Moon', 'Firmicus', 'by night', 'III.13, 5', ['conspicuous', 'extravagant', 'brilliant']),
    (2, 'Moon', 'Firmicus', 'by day', 'III.13, 6-8', ['dislocations', 'hemorrhoids', 'continuous']),
    (3, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the third, pp. 63-64', ['revelations', 'mysterious', 'fortune']),
    (3, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the third, p. 63', ['blasphemers', 'brothers', 'account']),
    (3, 'Saturn', 'Firmicus', 'unsplit', 'III.2, 14-16', ['sacrilegious', 'malevolent', 'prosperous']),
    (3, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 64', ['fortune', 'saturn', 'mars']),
    (3, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the third, p. 63', ['aspected', 'benefits', 'brothers']),
    (3, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 10', ['moderation', 'squandered', 'conferred']),
    (3, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the third, p. 63', ['blasphemers', 'brothers', 'account']),
    (3, 'Mars', 'Firmicus', 'unsplit', 'III.4, 14-18', ['administration', 'praetorians', 'commanders']),
    (3, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 65', ['inspired', 'fearing', 'ignoble']),
    (3, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 62', ['dwelling', 'abroad', 'moon']),
    (3, 'Sun', 'Firmicus', 'unsplit', 'III.5, 29-32', ['irreligious', 'responsible', 'treacherous']),
    (3, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 63', ['favors', 'gifts', 'women']),
    (3, 'Venus', 'Rhetorius', 'in sect', 'Ch. 57, the third, p. 65', ['philosophers', 'paragraph', 'involved']),
    (3, 'Venus', 'Rhetorius', 'out of sect', 'Ch. 57, the third, p. 66', ['ingratitudes', 'misfortunes', 'households']),
    (3, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 62', ['authority', 'positions', 'kindness']),
    (3, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the third, p. 63', ['aspected', 'benefits', 'brothers']),
    (3, 'Venus', 'Firmicus', 'unsplit', 'III.6, 17-18', ['priestess', 'religions', 'daughter']),
    (3, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the third, pp. 62-63', ['experienced', 'participant', 'revelations']),
    (3, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 12-14', ['administrators', 'mathematicians', 'physicians']),
    (3, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the third, p. 62', ['interpreter', 'blasphemer', 'soothsayer']),
    (3, 'Moon', 'Firmicus', 'by day', 'III.13, 9', ['polluted', 'ignoble', 'infamy']),
    (3, 'Moon', 'Firmicus', 'unsplit', 'III.13, 10-12', ['government', 'livelihood', 'reformers']),
    (3, 'Moon', 'Firmicus', 'by night', 'III.13, 13', ['sacrilegious', 'misfortunes', 'religions']),
    (3, 'Moon', 'Firmicus', 'by day', 'III.13, 14', ['sacrilegious', 'irreligious', 'despoilers']),
    (4, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the fourth, p. 69', ['wealth', 'gold', 'up']),
    (4, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the fourth, p. 69', ['destruction', 'illnesses', 'ignoble']),
    (4, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, pp. 69-70', ['childlessness', 'complaints', 'internally']),
    (4, 'Saturn', 'Rhetorius', 'in sect', 'Ch. 57, the fourth, p. 68', ['inheritance', 'exaltation', 'stationary']),
    (4, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the fourth, p. 67', ['possessions', 'ancestral', 'miserable']),
    (4, 'Saturn', 'Firmicus', 'by day', 'III.2, 17', ['guardians', 'greedy', 'monies']),
    (4, 'Saturn', 'Firmicus', 'by night', 'III.2, 18-20', ['illnesses', 'patrimony', 'perpetual']),
    (4, 'Jupiter', 'Rhetorius', 'in sect', 'Ch. 57, the fourth, p. 70', ['commanders', 'importance', 'enjoyable']),
    (4, 'Jupiter', 'Rhetorius', 'out of sect', 'Ch. 57, the fourth, p. 70', ['individuals', 'fortunate', 'moderate']),
    (4, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, p. 68', ['inheritances', 'activities', 'forbidden']),
    (4, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the fourth, p. 67', ['jupiter', 'death', 'venus']),
    (4, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 11-15', ['interpreters', 'beforehand', 'messengers']),
    (4, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 16-17', ['affections', 'afterwards', 'patrimony']),
    (4, 'Jupiter', 'Firmicus', 'by night', 'III.3, 18', ['middling', 'luckier', 'assets']),
    (4, 'Mars', 'Rhetorius', 'by night', 'Ch. 57, the fourth, p. 70', ['messengers', 'generals', 'soldiers']),
    (4, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the fourth, p. 70', ['particularly', 'ingratitude', 'epileptics']),
    (4, 'Mars', 'Rhetorius', 'out of sect', 'Ch. 57, the fourth, pp. 68-69', ['poisonous', 'another', 'animal']),
    (4, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the fourth, p. 67', ['possessions', 'ancestral', 'miserable']),
    (4, 'Mars', 'Firmicus', 'by night', 'III.4, 19-21', ['overthrowers', 'patrimony', 'widowhood']),
    (4, 'Mars', 'Firmicus', 'by day', 'III.4, 22-25', ['invalids', 'lunatics', 'sluggish']),
    (4, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, pp. 70-71', ['livelihood', 'diversity', 'destroys']),
    (4, 'Sun', 'Firmicus', 'unsplit', 'III.5, 33-35', ['contrarieties', 'interruptions', 'affections']),
    (4, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, p. 71', ['bicorporeal', 'homosexuals', 'widowhoods']),
    (4, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, pp. 67-69', ['effeminates', 'adulterers', 'stationary']),
    (4, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the fourth, p. 67', ['jupiter', 'death', 'venus']),
    (4, 'Venus', 'Firmicus', 'by day', 'III.6, 19-20', ['administrations', 'confiscation', 'portionally']),
    (4, 'Venus', 'Firmicus', 'by night', 'III.6, 21-23', ['intercourse', 'patrimonies', 'respectable']),
    (4, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, pp. 68-71', ['condemnation', 'participants', 'exaltation']),
    (4, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, p. 68', ['accusations', 'sorcerers', 'aspected']),
    (4, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 15-18', ['condemnations', 'accusations', 'calculation']),
    (4, 'Moon', 'Rhetorius', 'in sect', 'Ch. 57, the fourth, p. 71', ['standard', 'honored', 'living']),
    (4, 'Moon', 'Rhetorius', 'out of sect', 'Ch. 57, the fourth, p. 71', ['sovereignty', 'presidency', 'exchange']),
    (4, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the fourth, pp. 67-68', ['imprisonment', 'restrictions', 'inheritance']),
    (4, 'Moon', 'Firmicus', 'by day', 'III.13, 15-16', ['transferred', 'surviving', 'another']),
    (4, 'Moon', 'Firmicus', 'by night', 'III.13, 17', ['increases', 'supported', 'constant']),
    (5, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the fifth, pp. 73, 97-98', ['considerable', 'possessions', 'authority']),
    (5, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the fifth, pp. 73, 98', ['possessions', 'acquired', 'deprived']),
    (5, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 72', ['buildings', 'countries', 'founders']),
    (5, 'Saturn', 'Firmicus', 'by day', 'III.2, 21-24', ['inheritances', 'magistrates', 'individual']),
    (5, 'Saturn', 'Firmicus', 'by night', 'III.2, 25', ['inconsistent', 'advancement', 'luckiness']),
    (5, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, pp. 74, 98', ['authority', 'doctrines', 'paragraph']),
    (5, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the fifth, p. 72', ['indication', 'charming', 'handsome']),
    (5, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 19-23', ['administrators', 'accountants', 'conspicuous']),
    (5, 'Jupiter', 'Firmicus', 'by night', 'III.3, 32-41', ['unluckiness', 'calamities', 'herbalists']),
    (5, 'Mars', 'Rhetorius', 'by night', 'Ch. 57, the fifth, pp. 74, 98', ['acquaintances', 'possessions', 'activities']),
    (5, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the fifth, pp. 74, 98-99', ['unfavorable', 'beholding', 'dangerous']),
    (5, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 72', ['general', 'tyrant', 'makes']),
    (5, 'Mars', 'Firmicus', 'by night', 'III.4, 26-28', ['administrators', 'friendship', 'themselves']),
    (5, 'Mars', 'Firmicus', 'by day', 'III.4, 29-35', ['confinements', 'accusations', 'misfortunes']),
    (5, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 72', ['friends', 'divine', 'ruling']),
    (5, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 74', ['unfortunate', 'childless', 'children']),
    (5, 'Sun', 'Firmicus', 'unsplit', 'III.5, 36-39', ['orphanhoods', 'everything', 'misfortune']),
    (5, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 74', ['acquaintances', 'prophesying', 'everything']),
    (5, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the fifth, p. 72', ['indication', 'charming', 'handsome']),
    (5, 'Venus', 'Firmicus', 'unsplit', 'III.6, 24-27', ['advancement', 'patrimonies', 'beforehand']),
    (5, 'Venus', 'Firmicus', 'unsplit', 'III.6, 28', ['administrations', 'contentious', 'suspicions']),
    (5, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, pp. 72-75, 99', ['astronomical', 'professional', 'astronomers']),
    (5, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 19-25', ['astrologers', 'concealers', 'gymnastics']),
    (5, 'Moon', 'Rhetorius', 'by night', 'Ch. 57, the fifth, p. 75', ['illustrious', 'presidents', 'fortunate']),
    (5, 'Moon', 'Rhetorius', 'by day', 'Ch. 57, the fifth, p. 75', ['estrangement', 'orphanhood', 'fortunate']),
    (5, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the fifth, p. 72', ['increasing', 'benefics', 'malefics']),
    (5, 'Moon', 'Rhetorius, as summarized by Dykes', 'by night', 'III.13 fn 284', ['illustrious', 'infortunes', 'fortunate']),
    (5, 'Moon', 'Rhetorius, as summarized by Dykes', 'by day', 'III.13 fn 284', ['estrangement', 'improvement', 'orphanhood']),
    (6, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the sixth, p. 78', ['unsteadiness', 'consumption', 'inheritance']),
    (6, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the sixth, p. 78', ['moderate', 'be', 'evils']),
    (6, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, p. 76', ['paralysis', 'sickness', 'arising']),
    (6, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the sixth, p. 75', ['sicknesses', 'involving', 'injuries']),
    (6, 'Saturn', 'Firmicus', 'unsplit', 'III.2, 26-28', ['tuberculosis', 'disgraced', 'dysentery']),
    (6, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, pp. 76-78', ['authority', 'disputes', 'affairs']),
    (6, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 42-45', ['particularly', 'silversmiths', 'goldsmiths']),
    (6, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, pp. 76-78', ['concerning', 'hemorrhage', 'sicknesses']),
    (6, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the sixth, p. 75', ['sicknesses', 'involving', 'injuries']),
    (6, 'Mars', 'Firmicus', 'unsplit', 'III.4, 36-37', ['portionally', 'determined', 'discovered']),
    (6, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, pp. 75-78', ['subordination', 'configured', 'descending']),
    (6, 'Sun', 'Firmicus', 'unsplit', 'III.5, 40-43', ['unluckiness', 'succession', 'wickedness']),
    (6, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, pp. 76-79', ['embryotomies', 'fascinating', 'intercourse']),
    (6, 'Venus', 'Firmicus', 'unsplit', 'III.6, 29-30', ['difficulties', 'childbirth', 'compliant']),
    (6, 'Venus', 'Firmicus', 'by night', 'III.6, 31', ['compliant', 'conferred', 'luckiness']),
    (6, 'Venus', 'Firmicus', 'unsplit', 'III.6, 32', ['estranged', 'exposed', 'parents']),
    (6, 'Mercury', 'Rhetorius', 'by day', 'Ch. 57, the sixth, p. 79', ['advancements', 'business', 'actions']),
    (6, 'Mercury', 'Rhetorius', 'by night', 'Ch. 57, the sixth, p. 79', ['administrators', 'interpreters', 'unsuccessful']),
    (6, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, p. 76', ['incompetents', 'possessions', 'reputation']),
    (6, 'Mercury', 'Firmicus', 'by day', 'III.7, 26', ['advocate', 'business', 'facility']),
    (6, 'Mercury', 'Firmicus', 'by night', 'III.7, 27-30', ['interpreters', 'approaching', 'authorities']),
    (6, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, p. 75', ['subordination', 'triplicity', 'understand']),
    (6, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the sixth, pp. 76-77', ['configured', 'epileptics', 'deranged']),
    (7, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the seventh, p. 82', ['treasurers', 'fundament', 'injuries']),
    (7, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the seventh, p. 82', ['suffering', 'sickness', 'arising']),
    (7, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, p. 80', ['hemorrhages', 'exaltation', 'sicknesses']),
    (7, 'Saturn', 'Firmicus', 'by day', 'III.2, 29', ['hemorrhoids', 'contracted', 'threshold']),
    (7, 'Saturn', 'Firmicus', 'by night', 'III.2, 30', ['inflammations', 'hemorrhoids', 'misfortunes']),
    (7, 'Jupiter', 'Rhetorius', 'by day', 'Ch. 57, the seventh, p. 82', ['children', 'towards', 'lived']),
    (7, 'Jupiter', 'Rhetorius', 'by night', 'Ch. 57, the seventh, p. 82', ['circumstances', 'moderate', 'meeting']),
    (7, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, p. 80', ['inheritances', 'professional', 'troublesome']),
    (7, 'Jupiter', 'Firmicus', 'by day', 'III.3, 46', ['necessarily', 'miserable', 'children']),
    (7, 'Jupiter', 'Firmicus', 'by night', 'III.3, 47', ['increasing', 'increases', 'patrimony']),
    (7, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the seventh, p. 82', ['murderous', 'torturers', 'traitors']),
    (7, 'Mars', 'Rhetorius', 'by night', 'Ch. 57, the seventh, p. 82', ['agitations', 'everything', 'sorrows']),
    (7, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, pp. 80-82', ['professional', 'obligations', 'activities']),
    (7, 'Mars', 'Firmicus', 'by day', 'III.4, 38-41', ['executioners', 'criminals', 'inventors']),
    (7, 'Mars', 'Firmicus', 'unsplit', 'III.4, 42-43', ['lacerations', 'calamities', 'manifestly']),
    (7, 'Mars', 'Firmicus', 'by night', 'III.4, 44-45', ['cauterization', 'agitation', 'actions']),
    (7, 'Mars', 'Firmicus', 'unsplit', 'III.4, 46-49', ['accusations', 'convictions', 'portionally']),
    (7, 'Mars', 'Firmicus', 'unsplit', 'III.4, 50-51', ['vehemently', 'children', 'involved']),
    (7, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, pp. 81-83', ['prosperity', 'children', 'injuries']),
    (7, 'Sun', 'Firmicus', 'unsplit', 'III.5, 44', ['illnesses', 'defects', 'saturn']),
    (7, 'Sun', 'Firmicus', 'unsplit', 'III.5, 45-49', ['administrations', 'administrators', 'adversaries']),
    (7, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, pp. 80-83', ['dispositioned', 'intercourse', 'promiscuous']),
    (7, 'Venus', 'Firmicus', 'by night', 'III.6, 33', ['difficulty', 'children', 'slowly']),
    (7, 'Venus', 'Firmicus', 'unsplit', 'III.6, 34-37', ['capricorn', 'shameless', 'infamies']),
    (7, 'Mercury', 'Rhetorius', 'by day', 'Ch. 57, the seventh, p. 83', ['consumptives', 'dominating', 'opposition']),
    (7, 'Mercury', 'Rhetorius', 'by night', 'Ch. 57, the seventh, p. 83', ['managing', 'writings', 'affairs']),
    (7, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, p. 80', ['meddlesome', 'poisoning', 'educated']),
    (7, 'Mercury', 'Firmicus', 'by day', 'III.7, 31-33', ['tuberculosis', 'prostitutes', 'condemned']),
    (7, 'Mercury', 'Firmicus', 'by night', 'III.7, 34-35', ['calculations', 'difficult', 'documents']),
    (7, 'Moon', 'Rhetorius', 'by day', 'Ch. 57, the seventh, p. 83', ['unavoidable', 'dangers', 'foreign']),
    (7, 'Moon', 'Rhetorius', 'by night', 'Ch. 57, the seventh, p. 83', ['increases', 'changes', 'foreign']),
    (7, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the seventh, p. 81', ['homosexuals', 'effeminate', 'hospitable']),
    (7, 'Moon', 'Rhetorius, as summarized by Dykes', 'by night', 'III.13 fn 285', ['subsistence', 'changing', 'foreign']),
    (7, 'Moon', 'Rhetorius, as summarized by Dykes', 'by day', 'III.13 fn 285', ['infortunes', 'mistreated', 'foreign']),
    (8, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the eighth, p. 86', ['acquiring', 'passage', 'assets']),
    (8, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the eighth, p. 86', ['consumptives', 'banished', 'death']),
    (8, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the eighth, p. 85', ['banished', 'jupiter', 'without']),
    (8, 'Saturn', 'Firmicus', 'by day', 'III.2, 31', ['advancing', 'increases', 'patrimony']),
    (8, 'Saturn', 'Firmicus', 'by night', 'III.2, 32-35', ['destruction', 'patrimony', 'preceding']),
    (8, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the eighth, pp. 85-86', ['acquisition', 'inheritance', 'exaltation']),
    (8, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the eighth, p. 86', ['fortune', 'jupiter', 'alone']),
    (8, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 48', ['backwards', 'malicious', 'patrimony']),
    (8, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 49', ['administrators', 'announcements', 'accountants']),
    (8, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the eighth, p. 86', ['disorders', 'dangers', 'wants']),
    (8, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the eighth, p. 85', ['forgers', 'injures', 'mercury']),
    (8, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the eighth, p. 85', ['banished', 'jupiter', 'without']),
    (8, 'Mars', 'Firmicus', 'by day', 'III.4, 52-62', ['confiscation', 'difficulties', 'patrimonies']),
    (8, 'Mars', 'Firmicus', 'by night', 'III.4, 63-64', ['illustrious', 'apoplectic', 'dangerous']),
    (8, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the eighth, p. 86', ['opposing', 'injures', 'aspect']),
    (8, 'Sun', 'Firmicus', 'unsplit', 'III.5, 67-74', ['elephantiasis', 'incantations', 'approaching']),
    (8, 'Venus', 'Rhetorius', 'by day', 'Ch. 57, the eighth, p. 86', ['intercourse', 'gonorrhea', 'apoplexy']),
    (8, 'Venus', 'Rhetorius', 'by night', 'Ch. 57, the eighth, pp. 86-87', ['painless', 'benefit', 'wealthy']),
    (8, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the eighth, p. 84', ['miserable', 'shameful', 'persons']),
    (8, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the eighth, p. 86', ['fortune', 'jupiter', 'alone']),
    (8, 'Venus', 'Firmicus', 'by day', 'III.6, 38-40', ['confiscation', 'contraction', 'squandered']),
    (8, 'Venus', 'Firmicus', 'by night', 'III.6, 41', ['conferred', 'luckiness', 'torment']),
    (8, 'Mercury', 'Rhetorius', 'by day', 'Ch. 57, the eighth, p. 87', ['unsuccessful', 'ineffective', 'vespertine']),
    (8, 'Mercury', 'Rhetorius', 'by night', 'Ch. 57, the eighth, p. 87', ['inheriting', 'vespertine', 'deserving']),
    (8, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the eighth, pp. 84-87', ['responsibilities', 'relationships', 'unintelligent']),
    (8, 'Mercury', 'Firmicus', 'by day', 'III.7, 36-37', ['indispensable', 'foolishly', 'laborious']),
    (8, 'Mercury', 'Firmicus', 'by night', 'III.7, 38', ['sluggishness', 'concealed', 'exhausted']),
    (8, 'Mercury', 'Firmicus', 'by day', 'III.7, 39', ['commendations', 'instruments', 'endlessly']),
    (8, 'Moon', 'Rhetorius', 'by night', 'Ch. 57, the eighth, p. 84', ['inheritances', 'jupiter', 'matters']),
    (9, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the ninth, pp. 65, 89', ['philosophers', 'prophesying', 'hindrances']),
    (9, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the ninth, pp. 65, 89', ['interpreters', 'philosophers', 'apothegms']),
    (9, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, p. 88', ['interpretation', 'knowledgeable', 'mysteries']),
    (9, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the ninth, p. 88', ['stationary', 'despoiler', 'matutine']),
    (9, 'Saturn', 'Firmicus', 'by day', 'III.2, 36-37', ['interpretations', 'mathematicians', 'interpreters']),
    (9, 'Saturn', 'Firmicus', 'by night', 'III.2, 38-39', ['diminished', 'mitigated', 'emperors']),
    (9, 'Jupiter', 'Rhetorius', 'by day', 'Ch. 57, the ninth, pp. 65, 89', ['consecrated', 'inalienable', 'predicting']),
    (9, 'Jupiter', 'Rhetorius', 'by night', 'Ch. 57, the ninth, pp. 65, 89', ['engendered', 'themselves', 'responses']),
    (9, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the ninth, p. 87', ['exaltation', 'observance', 'religious']),
    (9, 'Jupiter', 'Firmicus', 'by day', 'III.3, 50-51', ['interpreters', 'priesthoods', 'agitation']),
    (9, 'Jupiter', 'Firmicus', 'by night', 'III.3, 52', ['flourishing', 'allotments', 'themselves']),
    (9, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, pp. 65, 88-89', ['blasphemers', 'deliverance', 'opportunity']),
    (9, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the ninth, p. 88', ['stationary', 'despoiler', 'matutine']),
    (9, 'Mars', 'Firmicus', 'unsplit', 'III.4, 67-73', ['administrations', 'everything', 'punishment']),
    (9, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, pp. 88, 90', ['inscriptions', 'foreigners', 'privileges']),
    (9, 'Sun', 'Firmicus', 'unsplit', 'III.5, 77-80', ['constructors', 'ostentation', 'worshippers']),
    (9, 'Venus', 'Rhetorius', 'out of sect', 'Ch. 57, the ninth, pp. 66, 90', ['philosophers', 'afflicted', 'something']),
    (9, 'Venus', 'Rhetorius', 'in sect', 'Ch. 57, the ninth, pp. 66, 90', ['mistreated', 'opposition', 'successful']),
    (9, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, p. 88', ['marriage', 'unstable', 'man']),
    (9, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the ninth, p. 87', ['exaltation', 'observance', 'religious']),
    (9, 'Venus', 'Firmicus', 'by day', 'III.6, 42-43', ['interpreters', 'soothsaying', 'accustomed']),
    (9, 'Venus', 'Firmicus', 'by night', 'III.6, 44-46', ['unhappiness', 'worshippers', 'instructed']),
    (9, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, pp. 66, 87-90', ['sacrilegious', 'astrologers', 'astronomers']),
    (9, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 40-44', ['mathematicians', 'argumentative', 'condemnations']),
    (9, 'Moon', 'Rhetorius', 'by night', 'Ch. 57, the ninth, pp. 67, 90-91', ['acquisitive', 'businessmen', 'entrusted']),
    (9, 'Moon', 'Rhetorius', 'by day', 'Ch. 57, the ninth, pp. 67, 91', ['inglorious', 'disturbed', 'sanctuary']),
    (9, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the ninth, p. 88', ['foreigners', 'parents', 'pious']),
    (9, 'Moon', 'Firmicus', 'by night', 'III.13, 23', ['cultivate', 'increases', 'luckiness']),
    (9, 'Moon', 'Firmicus', 'by day', 'III.13, 24', ['foreigners', 'dangers', 'ignoble']),
    (10, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the tenth, pp. 91, 93', ['agriculture', 'exaltation', 'becoming']),
    (10, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the tenth, pp. 91, 93', ['ancestral', 'fishermen', 'gardeners']),
    (10, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the tenth, p. 92', ['confiscated', 'miserable', 'whatever']),
    (10, 'Saturn', 'Firmicus', 'unsplit', 'III.2, 40', ['superintendents', 'praetorian', 'emperors']),
    (10, 'Saturn', 'Firmicus', 'by day', 'III.2, 41-43', ['inheritances', 'possessions', 'respectable']),
    (10, 'Saturn', 'Firmicus', 'by night', 'III.2, 44-48', ['unluckiness', 'changeable', 'orphanhood']),
    (10, 'Jupiter', 'Rhetorius', 'by day', 'Ch. 57, the tenth, pp. 91, 93', ['distinguished', 'contestants', 'management']),
    (10, 'Jupiter', 'Rhetorius', 'by night', 'Ch. 57, the tenth, p. 94', ['livelihood', 'overthrown', 'dignified']),
    (10, 'Jupiter', 'Firmicus', 'by day', 'III.3, 53-56', ['diminished', 'disconnect', 'squandered']),
    (10, 'Jupiter', 'Firmicus', 'by night', 'III.3, 57', ['respectable', 'squandering', 'patrimony']),
    (10, 'Mars', 'Rhetorius', 'by day', 'Ch. 57, the tenth, pp. 91, 94', ['individuals', 'possessions', 'accomplish']),
    (10, 'Mars', 'Rhetorius', 'by night', 'Ch. 57, the tenth, pp. 91, 94', ['commanders', 'districts', 'frightful']),
    (10, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the tenth, p. 94', ['rulerships', 'children', 'firmicus']),
    (10, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the tenth, p. 92', ['confiscated', 'miserable', 'whatever']),
    (10, 'Mars', 'Firmicus', 'by night', 'III.4, 74-79', ['respectability', 'overthrowers', 'approaching']),
    (10, 'Mars', 'Firmicus', 'by day', 'III.4, 80-81', ['condemnations', 'confiscations', 'ineffective']),
    (10, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the tenth, p. 92', ['distinguished', 'malefics', 'fathers']),
    (10, 'Sun', 'Firmicus', 'by day', 'III.5, 81-82', ['administrations', 'administrators', 'proconsulates']),
    (10, 'Sun', 'Firmicus', 'by day', 'III.5, 83-85', ['administrator', 'ascensions', 'estranged']),
    (10, 'Sun', 'Firmicus', 'unsplit', 'III.5, 86-88', ['respectable', 'diminished', 'education']),
    (10, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the tenth, pp. 91-95', ['hermaphrodites', 'reprehensible', 'negotiators']),
    (10, 'Venus', 'Firmicus', 'unsplit', 'III.6, 50-52', ['illustrious', 'instruments', 'musicians']),
    (10, 'Venus', 'Firmicus', 'unsplit', 'III.6, 53-58', ['hermaphrodites', 'preposterous', 'prostitutes']),
    (10, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the tenth, pp. 92, 95', ['discriminating', 'unsuccessful', 'advancement']),
    (10, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 45-47', ['benevolent', 'admirable', 'business']),
    (10, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 48-49', ['condemnation', 'promotion', 'offenses']),
    (10, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 50-51', ['confiscations', 'abundance', 'illnesses']),
    (10, 'Moon', 'Rhetorius', 'in sect', 'Ch. 57, the tenth, p. 95', ['entrusted', 'hardships', 'partilely']),
    (10, 'Moon', 'Rhetorius', 'out of sect', 'Ch. 57, the tenth, pp. 95-96', ['commanding', 'livelihood', 'frightful']),
    (10, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the tenth, p. 92', ['distinguished', 'malefics', 'fathers']),
    (10, 'Moon', 'Firmicus', 'by night', 'III.13, 25-27', ['administrators', 'neighboring', 'portionally']),
    (10, 'Moon', 'Firmicus', 'by day', 'III.13, 28-30', ['administration', 'administrators', 'portionally']),
    (11, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the eleventh, p. 96', ['significance', 'triplicities', 'opposition']),
    (11, 'Saturn', 'Firmicus', 'unsplit', 'III.2, 54', ['patrimony', 'thirtieth', 'bestowed']),
    (11, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the eleventh, p. 96', ['exaltations', 'illustrious', 'domiciles']),
    (11, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 58', ['authorities', 'proconsular', 'withdrawing']),
    (11, 'Jupiter', 'Firmicus', 'by night', 'III.3, 59', ['effectiveness', 'diminished', 'lose']),
    (11, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 60', ['unluckiness', 'conferred', 'luckiness']),
    (11, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the eleventh, p. 96', ['significance', 'triplicities', 'opposition']),
    (11, 'Mars', 'Firmicus', 'unsplit', 'III.4, 82', ['association', 'punishment', 'triangular']),
    (11, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the eleventh, p. 99', ['distinguished', 'individuals', 'happiness']),
    (11, 'Sun', 'Firmicus', 'unsplit', 'III.5, 89-91', ['perseverance', 'conferred', 'dignities']),
    (11, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the eleventh, p. 99', ['increasing', 'actresses', 'offspring']),
    (11, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the eleventh, p. 96', ['exaltations', 'illustrious', 'domiciles']),
    (11, 'Venus', 'Firmicus', 'unsplit', 'III.6, 59-62', ['patrimonies', 'difficulty', 'friendship']),
    (11, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 52', ['indispensable', 'ingenious', 'accounts']),
    (11, 'Moon', 'Rhetorius', 'by night', 'Ch. 57, the eleventh, p. 100', ['presumptive', 'unaspected', 'receiving']),
    (11, 'Moon', 'Rhetorius', 'by day', 'Ch. 57, the eleventh, p. 100', ['estrangements', 'individuals', 'separations']),
    (11, 'Moon', 'Firmicus', 'unsplit', 'III.13, 31', ['decrees', 'fifth', 'place']),
    (12, 'Saturn', 'Rhetorius', 'by night', 'Ch. 57, the twelfth, p. 46', ['inheritance', 'disturbed', 'mentally']),
    (12, 'Saturn', 'Rhetorius', 'by day', 'Ch. 57, the twelfth, p. 46', ['moderate', 'matters', 'these']),
    (12, 'Saturn', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, p. 46', ['inconstancy', 'experience', 'aspecting']),
    (12, 'Saturn', 'Rhetorius', 'general malefic', 'Ch. 57, the twelfth, p. 43', ['destruction', 'unfavorable', 'sicknesses']),
    (12, 'Saturn', 'Firmicus', 'unsplit', 'III.2, 55-56', ['insurrection', 'illnesses', 'middling']),
    (12, 'Jupiter', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, pp. 43, 46', ['litigation', 'superiors', 'uprisings']),
    (12, 'Jupiter', 'Rhetorius', 'general benefic', 'Ch. 57, the twelfth, p. 43', ['benefics', 'bestow', 'injury']),
    (12, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 61-64', ['portionally', 'unluckiness', 'calamity']),
    (12, 'Jupiter', 'Firmicus', 'unsplit', 'III.3, 65-66', ['association', 'goldsmiths', 'vestments']),
    (12, 'Mars', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, pp. 44, 46', ['treacheries', 'associated', 'sicknesses']),
    (12, 'Mars', 'Rhetorius', 'general malefic', 'Ch. 57, the twelfth, p. 43', ['destruction', 'unfavorable', 'sicknesses']),
    (12, 'Mars', 'Firmicus', 'by day', 'III.4, 83-85', ['agitations', 'condemned', 'illnesses']),
    (12, 'Sun', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, pp. 43, 46', ['experience', 'sicknesses', 'captives']),
    (12, 'Sun', 'Firmicus', 'unsplit', 'III.5, 92-94', ['obscurities', 'illnesses', 'patrimony']),
    (12, 'Venus', 'Rhetorius', 'by night', 'Ch. 57, the twelfth, p. 46', ['courtesans', 'distressed', 'childless']),
    (12, 'Venus', 'Rhetorius', 'by day', 'Ch. 57, the twelfth, pp. 46-47', ['violently', 'business', 'physical']),
    (12, 'Venus', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, pp. 43-44', ['marriages', 'slayers', 'slaves']),
    (12, 'Venus', 'Rhetorius', 'general benefic', 'Ch. 57, the twelfth, p. 43', ['benefics', 'bestow', 'injury']),
    (12, 'Venus', 'Firmicus', 'by night', 'III.6, 63-64', ['prostitutes', 'associate', 'offspring']),
    (12, 'Venus', 'Firmicus', 'by day', 'III.6, 65', ['cruelty', 'death', 'women']),
    (12, 'Venus', 'Firmicus', 'unsplit', 'III.6, 69', ['necessary', 'nocturnal', 'nativity']),
    (12, 'Venus', 'Firmicus', 'unsplit', 'III.6, 70-71', ['increases', 'patrimony', 'preceding']),
    (12, 'Mercury', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, pp. 44, 47', ['considerably', 'benefactors', 'grammarians']),
    (12, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 53-57', ['discoverers', 'grammarians', 'prosperous']),
    (12, 'Mercury', 'Firmicus', 'unsplit', 'III.7, 58-59', ['condemnations', 'transactions', 'informants']),
    (12, 'Moon', 'Rhetorius', 'unsplit', 'Ch. 57, the twelfth, p. 43', ['injured', 'outcast', 'father']),
    (12, 'Moon', 'Firmicus', 'by night', 'III.13, 32', ['portionally', 'authority', 'luckiness']),
    (12, 'Moon', 'Firmicus', 'unsplit', 'III.13, 33', ['misfortunes', 'portionally', 'accidents']),
    (12, 'Moon', 'Firmicus', 'by day', 'III.13, 34', ['sacrificing', 'miserable', 'patrimony']),
    (12, 'Moon', 'Firmicus', 'by night', 'III.13, 35', ['endangered', 'inglorious', 'miserable']),
]

PN4_HALVES_SENTENCES = [
    (1, 'Saturn', 'Good', 'II.6, 1-2 (shared with the 4th, 7th and 10th)', ['villages', 'building', 'rivers']),
    (1, 'Saturn', 'Bad', 'II.6, 3 (shared with the 4th, 7th and 10th)', ['blamed', 'accused', 'detestable']),
    (1, 'Jupiter', 'Good', 'II.9, 1-2 (shared with the 4th, 7th and 10th)', ['celebrated', 'respected', 'motives']),
    (1, 'Jupiter', 'Bad', 'II.9, 3 (shared with the 4th, 7th and 10th)', ['scarcity', 'eagerness', 'worries']),
    (1, 'Mars', 'Good', 'II.12, 1-2 (shared with the 4th, 7th and 10th)', ['awe', 'wars', 'contends']),
    (1, 'Mars', 'Bad', 'II.12, 3-5 (shared with the 4th, 7th and 10th)', ['conflagration', 'robbers', 'iron']),
    (1, 'Sun', 'Good', 'II.15, 1-2 (shared with the 4th, 7th and 10th)', ['renowned', 'voice', 'sultan']),
    (1, 'Sun', 'Bad', 'II.15, 3 (shared with the 4th, 7th and 10th)', ['detestable', 'benefit', 'fear']),
    (1, 'Venus', 'Good', 'II.18, 1-2 (shared with the 4th, 7th and 10th)', ['gates', 'kings', 'spoiled']),
    (1, 'Venus', 'Bad', 'II.18, 3-4 (shared with the 4th, 7th and 10th)', ['paralysis', 'pleurisy', 'stolen']),
    (1, 'Mercury', 'Good', 'II.21, 1 (shared with the 4th, 7th and 10th)', ['writing', 'sciences', 'preservation']),
    (1, 'Mercury', 'Bad', 'II.21, 2 (shared with the 4th, 7th and 10th)', ['writers', 'calculation', 'accused']),
    (1, 'Moon', 'Good', '', []),
    (1, 'Moon', 'Bad', '', []),
    (2, 'Saturn', 'Good', 'II.6, 12-13', ['assets', 'hoped', 'sowing']),
    (2, 'Saturn', 'Bad', 'II.6, 14', ['vegetation', 'fields', 'sinking']),
    (2, 'Jupiter', 'Good', 'II.9, 10 (shared with the 8th)', ['leisure', 'scarcity', 'dead']),
    (2, 'Jupiter', 'Bad', 'II.9, 11 (shared with the 8th)', ['spending', 'cheerfulness', 'contention']),
    (2, 'Mars', 'Good', 'II.12, 11', ['benefit', 'direction', 'aware']),
    (2, 'Mars', 'Bad', 'II.12, 12', ['spend', 'money', 'squander']),
    (2, 'Sun', 'Good', 'II.15, 8 (shared with the 8th)', ['temperedness', 'leisure', 'revenue']),
    (2, 'Sun', 'Bad', 'II.15, 9 (shared with the 8th)', ['scarcity', 'negligence', 'laziness']),
    (2, 'Venus', 'Good', 'II.18, 10 (shared with the 8th)', ['underclass', 'base', 'work']),
    (2, 'Venus', 'Bad', 'II.18, 11', ['negligence', 'idleness', 'stagnation']),
    (2, 'Mercury', 'Good', 'II.21, 10 (shared with the 8th)', ['selling', 'buying', 'praised']),
    (2, 'Mercury', 'Bad', 'II.21, 11 (shared with the 8th)', ['downturn', 'incriminated', 'quarrel']),
    (2, 'Moon', 'Good', '', []),
    (2, 'Moon', 'Bad', '', []),
    (3, 'Saturn', 'Good', 'II.6, 7-8 (shared with the 9th)', ['reward', 'toil', 'foreigners']),
    (3, 'Saturn', 'Bad', 'II.6, 9-11 (shared with the 9th)', ['gossip', 'worship', 'theft']),
    (3, 'Jupiter', 'Good', 'II.9, 8 (shared with the 9th)', ['piety', 'brothers', 'reports']),
    (3, 'Jupiter', 'Bad', 'II.9, 9 (shared with the 9th)', ['negligent', 'doubts', 'brothers']),
    (3, 'Mars', 'Good', 'II.12, 9 (shared with the 9th)', ['travel', 'strong', 'praised']),
    (3, 'Mars', 'Bad', 'II.12, 10 (shared with the 9th)', ['false', 'hardship', 'wild']),
    (3, 'Sun', 'Good', 'II.15, 6 (shared with the 9th)', ['beautiful', 'religion', 'relatives']),
    (3, 'Sun', 'Bad', 'II.15, 7 (shared with the 9th)', ['ugly', 'journey', 'relatives']),
    (3, 'Venus', 'Good', 'II.18, 8 (shared with the 9th)', ['journey', 'dressed', 'kind']),
    (3, 'Venus', 'Bad', 'II.18, 9 (shared with the 9th)', ['defamed', 'distant', 'selling']),
    (3, 'Mercury', 'Good', 'II.21, 8 (shared with the 9th)', ['visions', 'interpretation', 'insight']),
    (3, 'Mercury', 'Bad', 'II.21, 9 (shared with the 9th)', ['damage', 'doubts', 'visions']),
    (3, 'Moon', 'Good', '', []),
    (3, 'Moon', 'Bad', '', []),
    (4, 'Saturn', 'Good', 'II.6, 1-2 (shared with the 1st, 7th and 10th)', ['villages', 'building', 'rivers']),
    (4, 'Saturn', 'Bad', 'II.6, 3 (shared with the 1st, 7th and 10th)', ['blamed', 'accused', 'detestable']),
    (4, 'Jupiter', 'Good', 'II.9, 1-2 (shared with the 1st, 7th and 10th)', ['celebrated', 'fathers', 'estate']),
    (4, 'Jupiter', 'Bad', 'II.9, 3 (shared with the 1st, 7th and 10th)', ['scarcity', 'eagerness', 'worries']),
    (4, 'Mars', 'Good', 'II.12, 1-2 (shared with the 1st, 7th and 10th)', ['awe', 'wars', 'contends']),
    (4, 'Mars', 'Bad', 'II.12, 3-5 (shared with the 1st, 7th and 10th)', ['conflagration', 'dwelling', 'rescued']),
    (4, 'Sun', 'Good', 'II.15, 1-2 (shared with the 1st, 7th and 10th)', ['estate', 'fathers', 'old']),
    (4, 'Sun', 'Bad', 'II.15, 3 (shared with the 1st, 7th and 10th)', ['detestable', 'benefit', 'fear']),
    (4, 'Venus', 'Good', 'II.18, 1-2 (shared with the 1st, 7th and 10th)', ['gates', 'kings', 'spoiled']),
    (4, 'Venus', 'Bad', 'II.18, 3-5 (shared with the 1st, 7th and 10th)', ['paralysis', 'stolen', 'die']),
    (4, 'Mercury', 'Good', 'II.21, 1 (shared with the 1st, 7th and 10th)', ['writing', 'sciences', 'preservation']),
    (4, 'Mercury', 'Bad', 'II.21, 2-4 (shared with the 1st, 7th and 10th)', ['calculation', 'accused', 'contention']),
    (4, 'Moon', 'Good', '', []),
    (4, 'Moon', 'Bad', '', []),
    (5, 'Saturn', 'Good', 'II.6, 4 (shared with the 11th)', ['friends', 'guarantees', 'building']),
    (5, 'Saturn', 'Bad', 'II.6, 5-6 (shared with the 11th)', ['brothers', 'shortage', 'retrograde']),
    (5, 'Jupiter', 'Good', 'II.9, 6', ['blessed', 'children', 'root']),
    (5, 'Jupiter', 'Bad', 'II.9, 7', ['children', 'messengers', 'gifts']),
    (5, 'Mars', 'Good', 'II.12, 6-7 (shared with the 11th)', ['allies', 'fire', 'blood']),
    (5, 'Mars', 'Bad', 'II.12, 8 (shared with the 11th)', ['accidents', 'feuding', 'brothers']),
    (5, 'Sun', 'Good', 'II.15, 4 (shared with the 11th)', ['food', 'clothing', 'crops']),
    (5, 'Sun', 'Bad', 'II.15, 5 (shared with the 11th)', ['undermine', 'contend', 'children']),
    (5, 'Venus', 'Good', 'II.18, 6 (shared with the 11th)', ['friends', 'possessions', 'root']),
    (5, 'Venus', 'Bad', 'II.18, 7 (shared with the 11th)', ['purpose', 'hostile', 'friends']),
    (5, 'Mercury', 'Good', 'II.21, 5 (shared with the 11th)', ['nobles', 'business', 'children']),
    (5, 'Mercury', 'Bad', 'II.21, 6-7 (shared with the 11th)', ['hostile', 'slowness', 'confused']),
    (5, 'Moon', 'Good', '', []),
    (5, 'Moon', 'Bad', '', []),
    (6, 'Saturn', 'Good', 'II.6, 16-18', ['moisture', 'remedies', 'escape']),
    (6, 'Saturn', 'Bad', 'II.6, 16-18', ['pleurisy', 'chronic', 'ruin']),
    (6, 'Jupiter', 'Good', 'II.9, 12 (shared with the 12th)', ['lowest', 'confined', 'peace']),
    (6, 'Jupiter', 'Bad', 'II.9, 13 (shared with the 12th)', ['windiness', 'enemies', 'confinement']),
    (6, 'Mars', 'Good', 'II.12, 17', ['body', 'healthy', 'victorious']),
    (6, 'Mars', 'Bad', 'II.12, 18-19', ['moisture', 'disturbance', 'bile']),
    (6, 'Sun', 'Good', 'II.15, 10', ['mild', 'temperedness', 'safety']),
    (6, 'Sun', 'Bad', 'II.15, 11', ['dryness', 'eyes', 'head']),
    (6, 'Venus', 'Good', 'II.18, 13 (shared with the 12th)', ['underclass', 'remedies', 'provisions']),
    (6, 'Venus', 'Bad', 'II.18, 14', ['essence', 'bile', 'heat']),
    (6, 'Mercury', 'Good', 'II.21, 12 (shared with the 12th)', ['eager', 'business', 'underclass']),
    (6, 'Mercury', 'Bad', 'II.21, 13 (shared with the 12th)', ['windiness', 'seized', 'confinement']),
    (6, 'Moon', 'Good', '', []),
    (6, 'Moon', 'Bad', '', []),
    (7, 'Saturn', 'Good', 'II.6, 1-2 (shared with the 1st, 4th and 10th)', ['villages', 'building', 'rivers']),
    (7, 'Saturn', 'Bad', 'II.6, 3 (shared with the 1st, 4th and 10th)', ['blamed', 'accused', 'detestable']),
    (7, 'Jupiter', 'Good', 'II.9, 1-2 (shared with the 1st, 4th and 10th)', ['celebrated', 'women', 'antagonists']),
    (7, 'Jupiter', 'Bad', 'II.9, 3 (shared with the 1st, 4th and 10th)', ['scarcity', 'eagerness', 'worries']),
    (7, 'Mars', 'Good', 'II.12, 1-2 (shared with the 1st, 4th and 10th)', ['awe', 'wars', 'contends']),
    (7, 'Mars', 'Bad', 'II.12, 3-5 (shared with the 1st, 4th and 10th)', ['conflagration', 'cutting', 'victorious']),
    (7, 'Sun', 'Good', 'II.15, 1-2 (shared with the 1st, 4th and 10th)', ['managements', 'victorious', 'healthy']),
    (7, 'Sun', 'Bad', 'II.15, 3 (shared with the 1st, 4th and 10th)', ['detestable', 'benefit', 'fear']),
    (7, 'Venus', 'Good', 'II.18, 1-2 (shared with the 1st, 4th and 10th)', ['gates', 'kings', 'spoiled']),
    (7, 'Venus', 'Bad', 'II.18, 3-4 (shared with the 1st, 4th and 10th)', ['paralysis', 'pleurisy', 'stolen']),
    (7, 'Mercury', 'Good', 'II.21, 1 (shared with the 1st, 4th and 10th)', ['writing', 'sciences', 'preservation']),
    (7, 'Mercury', 'Bad', 'II.21, 2-4 (shared with the 1st, 4th and 10th)', ['calculation', 'accused', 'contention']),
    (7, 'Moon', 'Good', '', []),
    (7, 'Moon', 'Bad', '', []),
    (8, 'Saturn', 'Good', 'II.6, 15', ['dead', 'received', 'house']),
    (8, 'Saturn', 'Bad', 'II.6, 15', ['squandering', 'ancestors', 'destruction']),
    (8, 'Jupiter', 'Good', 'II.9, 10 (shared with the 2nd)', ['leisure', 'scarcity', 'dead']),
    (8, 'Jupiter', 'Bad', 'II.9, 11 (shared with the 2nd)', ['spending', 'cheerfulness', 'contention']),
    (8, 'Mars', 'Good', 'II.12, 13', ['dead', 'ancestors', 'inheritances']),
    (8, 'Mars', 'Bad', 'II.12, 14', ['detestable', 'quarrels', 'squandered']),
    (8, 'Sun', 'Good', 'II.15, 8 (shared with the 2nd)', ['temperedness', 'leisure', 'revenue']),
    (8, 'Sun', 'Bad', 'II.15, 9 (shared with the 2nd)', ['scarcity', 'negligence', 'laziness']),
    (8, 'Venus', 'Good', 'II.18, 10 (shared with the 2nd)', ['underclass', 'eighth', 'spending']),
    (8, 'Venus', 'Bad', 'II.18, 12', ['leisure', 'scarcity', 'contention']),
    (8, 'Mercury', 'Good', 'II.21, 10 (shared with the 2nd)', ['selling', 'buying', 'praised']),
    (8, 'Mercury', 'Bad', 'II.21, 11 (shared with the 2nd)', ['downturn', 'incriminated', 'quarrel']),
    (8, 'Moon', 'Good', '', []),
    (8, 'Moon', 'Bad', '', []),
    (9, 'Saturn', 'Good', 'II.6, 7-8 (shared with the 3rd)', ['reward', 'toil', 'foreigners']),
    (9, 'Saturn', 'Bad', 'II.6, 9-11 (shared with the 3rd)', ['gossip', 'worship', 'theft']),
    (9, 'Jupiter', 'Good', 'II.9, 8 (shared with the 3rd)', ['piety', 'brothers', 'reports']),
    (9, 'Jupiter', 'Bad', 'II.9, 9 (shared with the 3rd)', ['negligent', 'doubts', 'brothers']),
    (9, 'Mars', 'Good', 'II.12, 9 (shared with the 3rd)', ['travel', 'strong', 'praised']),
    (9, 'Mars', 'Bad', 'II.12, 10 (shared with the 3rd)', ['false', 'hardship', 'wild']),
    (9, 'Sun', 'Good', 'II.15, 6 (shared with the 3rd)', ['beautiful', 'religion', 'relatives']),
    (9, 'Sun', 'Bad', 'II.15, 7 (shared with the 3rd)', ['ugly', 'journey', 'relatives']),
    (9, 'Venus', 'Good', 'II.18, 8 (shared with the 3rd)', ['journey', 'dressed', 'kind']),
    (9, 'Venus', 'Bad', 'II.18, 9 (shared with the 3rd)', ['defamed', 'distant', 'selling']),
    (9, 'Mercury', 'Good', 'II.21, 8 (shared with the 3rd)', ['visions', 'interpretation', 'insight']),
    (9, 'Mercury', 'Bad', 'II.21, 9 (shared with the 3rd)', ['damage', 'doubts', 'visions']),
    (9, 'Moon', 'Good', '', []),
    (9, 'Moon', 'Bad', '', []),
    (10, 'Saturn', 'Good', 'II.6, 1-2 (shared with the 1st, 4th and 7th)', ['villages', 'building', 'rivers']),
    (10, 'Saturn', 'Bad', 'II.6, 3 (shared with the 1st, 4th and 7th)', ['blamed', 'accused', 'detestable']),
    (10, 'Jupiter', 'Good', 'II.9, 1-2 (shared with the 1st, 4th and 7th)', ['celebrated', 'respected', 'importance']),
    (10, 'Jupiter', 'Bad', 'II.9, 3 (shared with the 1st, 4th and 7th)', ['scarcity', 'eagerness', 'worries']),
    (10, 'Mars', 'Good', 'II.12, 1-2 (shared with the 1st, 4th and 7th)', ['awe', 'wars', 'midheaven']),
    (10, 'Mars', 'Bad', 'II.12, 3-5 (shared with the 1st, 4th and 7th)', ['conflagration', 'robbers', 'iron']),
    (10, 'Sun', 'Good', 'II.15, 1-2 (shared with the 1st, 4th and 7th)', ['renowned', 'voice', 'sultan']),
    (10, 'Sun', 'Bad', 'II.15, 3 (shared with the 1st, 4th and 7th)', ['detestable', 'benefit', 'fear']),
    (10, 'Venus', 'Good', 'II.18, 1-2 (shared with the 1st, 4th and 7th)', ['gates', 'kings', 'spoiled']),
    (10, 'Venus', 'Bad', 'II.18, 3-4 (shared with the 1st, 4th and 7th)', ['paralysis', 'pleurisy', 'stolen']),
    (10, 'Mercury', 'Good', 'II.21, 1 (shared with the 1st, 4th and 7th)', ['writing', 'sciences', 'preservation']),
    (10, 'Mercury', 'Bad', 'II.21, 2 (shared with the 1st, 4th and 7th)', ['writers', 'calculation', 'accused']),
    (10, 'Moon', 'Good', '', []),
    (10, 'Moon', 'Bad', '', []),
    (11, 'Saturn', 'Good', 'II.6, 4 (shared with the 5th)', ['friends', 'guarantees', 'building']),
    (11, 'Saturn', 'Bad', 'II.6, 5-6 (shared with the 5th)', ['brothers', 'shortage', 'retrograde']),
    (11, 'Jupiter', 'Good', 'II.9, 4', ['commended', 'friends', 'delighted']),
    (11, 'Jupiter', 'Bad', 'II.9, 5', ['worries', 'hopes', 'wishes']),
    (11, 'Mars', 'Good', 'II.12, 6-7 (shared with the 5th)', ['allies', 'fire', 'blood']),
    (11, 'Mars', 'Bad', 'II.12, 8 (shared with the 5th)', ['accidents', 'feuding', 'brothers']),
    (11, 'Sun', 'Good', 'II.15, 4 (shared with the 5th)', ['food', 'clothing', 'crops']),
    (11, 'Sun', 'Bad', 'II.15, 5 (shared with the 5th)', ['undermine', 'contend', 'children']),
    (11, 'Venus', 'Good', 'II.18, 6 (shared with the 5th)', ['friends', 'possessions', 'root']),
    (11, 'Venus', 'Bad', 'II.18, 7 (shared with the 5th)', ['purpose', 'hostile', 'friends']),
    (11, 'Mercury', 'Good', 'II.21, 5 (shared with the 5th)', ['nobles', 'business', 'children']),
    (11, 'Mercury', 'Bad', 'II.21, 6-7 (shared with the 5th)', ['hostile', 'slowness', 'confused']),
    (11, 'Moon', 'Good', '', []),
    (11, 'Moon', 'Bad', '', []),
    (12, 'Saturn', 'Good', 'II.6, 19', ['victorious', 'enemies', 'befriend']),
    (12, 'Saturn', 'Bad', 'II.6, 20-21', ['prison', 'confinement', 'torment']),
    (12, 'Jupiter', 'Good', 'II.9, 12 (shared with the 6th)', ['lowest', 'confined', 'peace']),
    (12, 'Jupiter', 'Bad', 'II.9, 13 (shared with the 6th)', ['windiness', 'enemies', 'confinement']),
    (12, 'Mars', 'Good', 'II.12, 15', ['runaways', 'confined', 'safe']),
    (12, 'Mars', 'Bad', 'II.12, 16', ['detestable', 'directions', 'affect']),
    (12, 'Sun', 'Good', 'II.15, 12', ['beautiful', 'spoken', 'safe']),
    (12, 'Sun', 'Bad', 'II.15, 13', ['confinement', 'banished', 'country']),
    (12, 'Venus', 'Good', 'II.18, 13 (shared with the 6th)', ['underclass', 'remedies', 'provisions']),
    (12, 'Venus', 'Bad', 'II.18, 15', ['enemies', 'confined', 'punishment']),
    (12, 'Mercury', 'Good', 'II.21, 12 (shared with the 6th)', ['eager', 'business', 'underclass']),
    (12, 'Mercury', 'Bad', 'II.21, 13 (shared with the 6th)', ['windiness', 'seized', 'confinement']),
    (12, 'Moon', 'Good', '', []),
    (12, 'Moon', 'Bad', '', []),
]

MOON_VII8_SENTENCES = [
    (1, 'VII.8, 1', ['preserved', 'endearing', 'lawsuits']),
    (2, 'VII.8, 2', ['revenue', 'mountains', 'deserts']),
    (3, 'VII.8, 3', ['messengers', 'mock', 'leaders']),
    (4, 'VII.8, 4', ['nobles', 'interpretation', 'disagreement']),
    (5, 'VII.8, 5', ['female', 'slaves', 'conflicting']),
    (6, 'VII.8, 6', ['hands', 'hunting', 'slaves']),
    (7, 'VII.8, 7', ['friendliness', 'maxims', 'disagreement']),
    (8, 'VII.8, 8', ['humiliation', 'degradation', 'farms']),
    (9, 'VII.8, 9', ['banquets', 'maxims', 'joyful']),
    (10, 'VII.8, 10', ['moist', 'gardens', 'associating']),
    (11, 'VII.8, 11', ['towns', 'villages', 'debts']),
    (12, 'VII.8, 12', ['guarantor', 'collateral', 'victorious']),
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


PN4_CITE = re.compile(r"^(II\.\d+|VII\.8), \d+(-\d+)?( \(shared with the \d+(st|nd|rd|th)(, \d+(st|nd|rd|th))*( and \d+(st|nd|rd|th))?\))?$")
PN4_DASH = {'text': '—', 'cite': ''}
MOON_POINTER = "see the Moon's table below (VII.8, by her transit)"
# What the page help states: every PN IV half has text (the Moon's two are
# the pointer to her own table, not dashes), and no cell of the Rhetorius
# list is empty -- a dash there would be the absence of testimony.
PN4_DASHES_THE_HELP_STATES = 0
RHETORIUS_EMPTY_CELLS_THE_HELP_STATES = 0
# The entry counts the help states, by author.
ENTRY_COUNTS_THE_HELP_STATES = {'Rhetorius': 198, 'Firmicus': 153, 'Rhetorius, as summarized by Dykes': 4}
# An entry's locator: Rhetorius by chapter, house and Holden's page -- one
# page (p. 76), a range where the sentences run over more than one page or
# fold in the house's earlier general sentences (pp. 57-61), or a list where
# the entry also rests on the paragraph the translators reassign to this
# house from another's pages (pp. 65, 88-89); Firmicus by chapter and one
# sentence or one run (III.2, 8; III.2, 4-5); the summaries by footnote.
RHETORIUS_CITE = re.compile(r"^Ch\. 57, the [a-z]+, pp?\. [\d, -]+$|^III\.\d+, \d+(-\d+)?$|^III\.13 fn 28[45]$")
RHETORIUS_AUTHORS = ('Rhetorius', 'Firmicus', 'Rhetorius, as summarized by Dykes')
RHETORIUS_AXES = ('by day', 'by night', 'in sect', 'out of sect', 'unsplit', 'general malefic', 'general benefic')
# build C's prefix form, "By day: ...", retired: an entry's axis is its own field
SECT_PREFIX = re.compile(r"^(By day|By night|In sect|Out of sect):")


def _numbers(spec):
    """The pages or sentences a locator's number list names, in order."""
    out = []
    for part in spec.split(", "):
        a, _, b = part.partition("-")
        out.extend(range(int(a), int(b or a) + 1))
    return out
HOUSE_NAMES = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth']
ENTRY_KEYS = {'author', 'cite', 'axis', 'text', 'portional', 'conditional'}


def test_planets_in_houses_has_the_list_and_halves_shape(engine):
    ph = engine["PLANETS_IN_HOUSES"]
    assert set(ph) == set(range(1, 13))
    for house in ph:
        assert set(ph[house]) == set(PLANETS)
        for cell in ph[house].values():
            assert set(cell) == {'Rhetorius', 'PN IV'}
            assert isinstance(cell['Rhetorius'], list)
            for entry in cell['Rhetorius']:
                assert set(entry) == ENTRY_KEYS and entry['text'].strip()
                assert entry['author'] in RHETORIUS_AUTHORS and entry['axis'] in RHETORIUS_AXES
                assert isinstance(entry['portional'], bool) and isinstance(entry['conditional'], bool)
            assert set(cell['PN IV']) == {'Good', 'Bad'}
            for half in cell['PN IV'].values():
                assert set(half) == {'text', 'cite'} and half['text'].strip()
    assert engine["RHETORIUS_AUTHORS"] == RHETORIUS_AUTHORS and engine["RHETORIUS_AXES"] == RHETORIUS_AXES


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
        # The Moon's two halves point to her own table; nothing else has an empty locator.
        assert planet == "Moon" and cell == {'text': MOON_POINTER, 'cite': ''} and anchors == [], (house, planet, half, cell)
        return
    assert cell["cite"] == cite and PN4_CITE.match(cite), (house, planet, half, cell["cite"])
    assert cell["text"] != PN4_DASH["text"]
    assert len(anchors) == 3 and set(anchors) <= _words(cell["text"]), (house, planet, half, anchors, cell["text"])


def test_a_grouped_locator_names_the_houses_it_is_shared_with(engine):
    # Book II pairs the eleventh with the fifth, the ninth with the third,
    # the second with the eighth (Jupiter, the Sun, Venus, Mercury), the
    # sixth with the twelfth (Jupiter, Venus's suitable half, Mercury), and
    # gives the four stakes one sentence: each such half says so in its
    # locator, and the partner's locator names this house back.
    ph = engine["PLANETS_IN_HOUSES"]
    shared = re.compile(r"\(shared with (.*)\)$")
    ordinal = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th', 11: '11th', 12: '12th'}
    inverse = {v: k for k, v in ordinal.items()}
    seen = 0
    for h in ph:
        for p in PLANETS:
            for x in ('Good', 'Bad'):
                cite = ph[h][p]['PN IV'][x]['cite']
                m = shared.search(cite)
                if not m:
                    continue
                seen += 1
                partners = [inverse[t] for t in re.findall(r"\d+(?:st|nd|rd|th)", m.group(1))]
                assert h not in partners and partners == sorted(partners), (h, p, x, cite)
                # a stake's half may add its own clause to the group's sentence
                # (Venus's fourth, II.18, 3-5; Mercury's seventh and fourth,
                # II.21, 2-4), so the partners share the chapter and the first
                # sentence, not always the whole run
                base = re.match(r"^(II\.\d+, \d+)", cite).group(1)
                for other in partners:
                    back = ph[other][p]['PN IV'][x]['cite']
                    assert back.startswith(base) and ordinal[h] in re.findall(r"\d+(?:st|nd|rd|th)", shared.search(back).group(1)), (h, p, x, other, back)
    # the four stakes (48), the eleventh-or-fifth (Saturn, Mars, the Sun,
    # Venus, Mercury: 20), the ninth-or-third (24), the second-or-eighth
    # (Jupiter, the Sun, Mercury both halves, Venus's suitable half: 14), the
    # sixth-or-twelfth (Jupiter, Mercury both halves, Venus's suitable half: 10)
    assert seen == 116, seen


def test_the_moons_pn4_halves_point_to_her_vii8_table(engine):
    # II.22 has no houses list for the Moon; fn 312 sends the reader to VII.8,
    # her transit through the twelve houses, which supplies no condition
    # split -- so she is not sorted into the two columns at all.
    ph = engine["PLANETS_IN_HOUSES"]
    for house in range(1, 13):
        cell = ph[house]["Moon"]["PN IV"]
        assert cell["Good"] == cell["Bad"] == {'text': MOON_POINTER, 'cite': ''}, cell
    assert engine["planets_in_houses_cell"](6, "Moon", "Good") == MOON_POINTER


def test_the_moon_vii8_fixture_covers_every_house_once():
    assert [h for h, _c, _a in MOON_VII8_SENTENCES] == list(range(1, 13))


@pytest.mark.parametrize("house, cite, anchors", MOON_VII8_SENTENCES, ids=[f"Moon-in-{h}" for h, _c, _a in MOON_VII8_SENTENCES])
def test_the_moons_vii8_reading_is_pinned_to_its_sentence(engine, house, cite, anchors):
    row = engine["MOON_IN_HOUSES_VII8"][house]
    assert set(row) == {'text', 'cite'} and row["cite"] == cite == f"VII.8, {house}"
    assert "[UNCERTAIN" not in row["text"] and not row["text"].startswith("By transit")
    assert len(anchors) == 3 and set(anchors) <= _words(row["text"]), (house, anchors, row["text"])


def test_the_moons_vii8_readings_keep_the_texts_reservations(engine):
    # Mixed readings stay mixed; "(from this indication)" where the sentence
    # has it (2, 3, 5, 9, 11, 12); fn 99/101/110's alternative for the dreams
    # (5, 6, 11); fn 106's reading marked as the translator's guess (10);
    # VII.8, 3's "some of him and his parents" as printed.
    m = engine["MOON_IN_HOUSES_VII8"]
    for h in (2, 3, 5, 9, 11, 12):
        assert "(from this indication)" in m[h]["text"], h
    for h in (5, 6, 11):
        assert "conflicting (or different) dreams" in m[h]["text"], h
    assert "the translator's guess" in m[10]["text"] and "fn 106" in m[10]["text"]
    assert "some of him and his parents" in m[3]["text"]
    assert "mixed in condition, of the good and the bad" in m[12]["text"]
    assert "harm from handling purchases and sales and from acquiring homes and lands" in m[4]["text"]


def test_every_pn4_half_has_text_and_no_dash(engine):
    # Every Saturn-Mercury half has its own sentence, and the Moon's are
    # the pointer: the dash count is what the help states (none).
    ph = engine["PLANETS_IN_HOUSES"]
    dashes = [(h, p, x) for h in ph for p in PLANETS for x in ('Good', 'Bad') if ph[h][p]['PN IV'][x] == PN4_DASH]
    assert len(dashes) == PN4_DASHES_THE_HELP_STATES == 0, dashes


def test_mercury_in_the_ninth_reads_as_ii21_8_and_9(engine):
    # The Guide prints these two halves against its own headings; II.21, 8
    # (the journey he loves, true visions) is the suitable reading and 9 the
    # bad-condition one, as the code always had them -- and 8 states no
    # condition, which the half says, for the third as for the ninth.
    for house in (9, 3):
        cell = engine["PLANETS_IN_HOUSES"][house]["Mercury"]["PN IV"]
        assert cell["Good"]["cite"].startswith("II.21, 8") and "true interpretation" in cell["Good"]["text"]
        assert cell["Good"]["text"].endswith("(condition not explicitly stated in II.21, 8)")
        assert cell["Bad"]["cite"].startswith("II.21, 9") and "bad visions" in cell["Bad"]["text"]


def test_saturns_falling_places_layer_is_carried_whole(engine):
    # II.6, 22-24 over Saturn's second, sixth, eighth and twelfth bad halves:
    # 22's "in the revolution", 23's intensifications (not received: harsher,
    # dispossessed, hardship, evil said, illness from cold; retrograde:
    # harsher again), 24's residual leisure -- beside each house's own
    # sentence, whose locator stays its own.
    ph = engine["PLANETS_IN_HOUSES"]
    for h in (2, 6, 8, 12):
        text = ph[h]["Saturn"]["PN IV"]["Bad"]["text"]
        assert "II.6, 22-24 add" in text and "in the revolution" in text
        for phrase in ("not received as well", "dispossessed", "evil said about him", "cold and moisture or cold and dryness",
                       "retrograde, harsher again", "except that he is at leisure"):
            assert phrase in text, (h, phrase)
        assert ph[h]["Saturn"]["PN IV"]["Bad"]["cite"].startswith("II.6, ") and "(shared" not in ph[h]["Saturn"]["PN IV"]["Bad"]["cite"]
    for h in (2, 6, 8, 12):
        assert "II.9, 15-16 add that in the revolution especially" in ph[h]["Jupiter"]["PN IV"]["Bad"]["text"]
    for h in (3, 6, 9, 12):
        assert "II.18, 18 adds that in the revolution" in ph[h]["Venus"]["PN IV"]["Bad"]["text"]


def test_the_entries_fixture_covers_every_entry_once(engine):
    ph = engine["PLANETS_IN_HOUSES"]
    expected = [(h, p, e['author'], e['axis'], e['cite']) for h in range(1, 13) for p in PLANETS for e in ph[h][p]['Rhetorius']]
    assert [(h, p, a, x, c) for h, p, a, x, c, _an in RHETORIUS_ENTRIES] == expected
    assert len(RHETORIUS_ENTRIES) == sum(ENTRY_COUNTS_THE_HELP_STATES.values()) == 355


@pytest.mark.parametrize("i, house, planet, author, axis, cite, anchors",
                         [(i, *row) for i, row in enumerate(RHETORIUS_ENTRIES)],
                         ids=[f"{p}-in-{h}-{i}" for i, (h, p, _a, _x, _c, _an) in enumerate(RHETORIUS_ENTRIES)])
def test_rhetorius_entry_is_pinned_to_its_passage(engine, i, house, planet, author, axis, cite, anchors):
    entries = engine["PLANETS_IN_HOUSES"][house][planet]['Rhetorius']
    position = [k for k, (h, p, *_rest) in enumerate(RHETORIUS_ENTRIES) if (h, p) == (house, planet)].index(i)
    entry = entries[position]
    assert (entry['author'], entry['axis'], entry['cite']) == (author, axis, cite)
    assert "[UNCERTAIN" not in entry["text"]
    assert RHETORIUS_CITE.match(cite), cite
    if cite.startswith("Ch. 57"):
        # The house named in the locator is the house of the cell; "p." names
        # one page and "pp." more than one, ascending.
        assert author == 'Rhetorius'
        assert cite.split(", ")[1] == f"the {HOUSE_NAMES[house - 1]}", (house, cite)
        pages = _numbers(cite.split(", ", 2)[2].split(" ", 1)[1])
        assert pages == sorted(set(pages)) and (len(pages) == 1) == (", p. " in cite), (house, planet, cite)
    elif " fn " in cite:
        assert author == 'Rhetorius, as summarized by Dykes' and planet == 'Moon' and house in (5, 7)
        assert axis in ('by day', 'by night')
    else:
        assert author == 'Firmicus'
        nums = _numbers(cite.split(", ", 1)[1])
        assert nums == sorted(set(nums)) and len(nums) == nums[-1] - nums[0] + 1, cite
        assert not axis.startswith('general')
    if entry['portional']:
        assert author == 'Firmicus', (house, planet, cite)
    assert not SECT_PREFIX.match(entry["text"]), (house, planet, cite, entry["text"][:30])
    assert len(anchors) == 3 and set(anchors) <= _words(entry["text"]), (house, planet, cite, anchors, entry["text"])


def test_no_cell_is_empty_and_the_counts_are_the_helps(engine):
    # An empty list would print as a dash -- the absence of testimony in
    # both texts, never a Guide summary and never an invented reading; the
    # help states the count (none), and the entry counts by author.
    ph = engine["PLANETS_IN_HOUSES"]
    empty = [(h, p) for h in ph for p in PLANETS if not ph[h][p]['Rhetorius']]
    assert len(empty) == RHETORIUS_EMPTY_CELLS_THE_HELP_STATES == 0, empty
    counts = {a: 0 for a in RHETORIUS_AUTHORS}
    for h in ph:
        for p in PLANETS:
            for e in ph[h][p]['Rhetorius']:
                counts[e['author']] += 1
    assert counts == ENTRY_COUNTS_THE_HELP_STATES
    assert not any("[UNCERTAIN" in e["text"] for h in ph for p in PLANETS for e in ph[h][p]['Rhetorius'])
    assert not any("[UNCERTAIN" in ph[h][p]['PN IV'][x]["text"] for h in ph for p in PLANETS for x in ('Good', 'Bad'))


def test_the_general_class_testimony_is_entered_for_both_members(engine):
    # Ch. 57's "the malefics there ..." is Saturn's and Mars's entry alike,
    # "the benefics ..." Jupiter's and Venus's, with the same text and
    # locator in both cells; the houses whose sections carry such a
    # sentence are pinned.
    ph = engine["PLANETS_IN_HOUSES"]
    def general(h, p, axis):
        return [(e['cite'], e['text']) for e in ph[h][p]['Rhetorius'] if e['axis'] == axis]
    malefic = {h for h in ph if general(h, 'Saturn', 'general malefic')}
    benefic = {h for h in ph if general(h, 'Jupiter', 'general benefic')}
    assert malefic == {1, 2, 3, 4, 6, 8, 9, 10, 11, 12} and benefic == {1, 2, 3, 4, 5, 8, 9, 11, 12}
    for h in malefic:
        assert general(h, 'Saturn', 'general malefic') == general(h, 'Mars', 'general malefic'), h
    for h in benefic:
        assert general(h, 'Jupiter', 'general benefic') == general(h, 'Venus', 'general benefic'), h
    for h in ph:
        for p in ('Sun', 'Mercury', 'Moon'):
            assert not any(e['axis'].startswith('general') for e in ph[h][p]['Rhetorius']), (h, p)


def test_the_axis_is_the_authors_own_word(engine):
    # Saturn "by day" is not "in sect", and Mars "in sect" is not "by night":
    # the labels are the texts', and where the two authors divide the same
    # placement differently the entries show it. The Moon in the sixth has
    # Rhetorius's two entries (the transfer to the mother; the spleen
    # sentence, scope noted) and no Firmicus; Venus in the ninth carries
    # both copies' labels; Dykes's summaries are the Moon's fifth and
    # seventh alone.
    ph = engine["PLANETS_IN_HOUSES"]
    def axes(h, p, author):
        return [e['axis'] for e in ph[h][p]['Rhetorius'] if e['author'] == author]
    assert axes(1, 'Saturn', 'Rhetorius') == ['by day', 'by night', 'unsplit', 'general malefic']
    assert axes(1, 'Jupiter', 'Rhetorius') == ['in sect', 'out of sect', 'unsplit', 'general benefic']
    assert axes(1, 'Mars', 'Rhetorius') == ['in sect', 'out of sect', 'unsplit', 'general malefic']
    assert axes(1, 'Saturn', 'Firmicus') == ['by day', 'by day', 'by night']
    assert axes(1, 'Sun', 'Firmicus') == ['unsplit', 'by day', 'unsplit', 'by night']
    assert [e['cite'] for e in ph[1]['Sun']['Rhetorius'] if e['author'] == 'Firmicus'][2] == 'III.5, 16'
    # a clause the page states without a sect word is an unsplit entry even
    # where it follows a sect clause: Saturn's Moon-aspect sentences in the
    # fourth (pp. 69-70) and the twelfth (p. 46)
    assert axes(4, 'Saturn', 'Rhetorius') == ['by day', 'by night', 'unsplit', 'in sect', 'general malefic']
    assert axes(12, 'Saturn', 'Rhetorius') == ['by night', 'by day', 'unsplit', 'general malefic']
    assert ph[4]['Saturn']['Rhetorius'][2]['text'].startswith("Aspecting the Moon") and ph[12]['Saturn']['Rhetorius'][2]['text'].startswith("Squaring or opposing the Moon")
    assert "Moon" not in ph[4]['Saturn']['Rhetorius'][1]['text'] and "Moon" not in ph[12]['Saturn']['Rhetorius'][0]['text']
    assert axes(2, 'Jupiter', 'Rhetorius') == ['unsplit', 'general benefic'] and ph[2]['Jupiter']['Rhetorius'][0]['text'].startswith("By day or by night:")
    moon6 = ph[6]['Moon']['Rhetorius']
    assert [e['author'] for e in moon6] == ['Rhetorius', 'Rhetorius'] and "mother" in moon6[0]['text'] and "spleen" in moon6[1]['text']
    assert "Sun, Mars and the Moon badly configured" in moon6[1]['text']
    venus9 = [(e['axis'], e['cite']) for e in ph[9]['Venus']['Rhetorius'] if e['author'] == 'Rhetorius']
    assert venus9[:2] == [('out of sect', 'Ch. 57, the ninth, pp. 66, 90'), ('in sect', 'Ch. 57, the ninth, pp. 66, 90')]
    assert all("copy under the third" in e['text'] for e in ph[9]['Venus']['Rhetorius'][:2])
    summaries = [(h, p, e['axis'], e['cite']) for h in ph for p in PLANETS for e in ph[h][p]['Rhetorius']
                 if e['author'] == 'Rhetorius, as summarized by Dykes']
    assert summaries == [(5, 'Moon', 'by night', 'III.13 fn 284'), (5, 'Moon', 'by day', 'III.13 fn 284'),
                         (7, 'Moon', 'by night', 'III.13 fn 285'), (7, 'Moon', 'by day', 'III.13 fn 285')]
    assert not any(e['author'] == 'Firmicus' for h in (5, 6, 7, 8) for e in ph[h]['Moon']['Rhetorius'])


def test_the_conditions_are_constitutive(engine):
    # III.2, 4-5 needs Saturn in the Hour-marker by day AND Mars in another
    # pivot: its own entry, whole, flagged conditional; "portionally" is a
    # flag the reader prints; "the full Moon moving toward Mars" (Ch. 57 p.
    # 77) is a configuration, not occupancy, and no Moon entry carries it.
    ph = engine["PLANETS_IN_HOUSES"]
    sat1 = [e for e in ph[1]['Saturn']['Rhetorius'] if e['cite'] == 'III.2, 4-5']
    assert len(sat1) == 1 and sat1[0]['conditional'] and sat1[0]['portional'] and sat1[0]['axis'] == 'by day'
    assert "Mars in another pivot" in sat1[0]['text'] and "violent death" in sat1[0]['text']
    mars6 = [e for e in ph[6]['Mars']['Rhetorius'] if e['author'] == 'Firmicus']
    assert [e['cite'] for e in mars6] == ['III.4, 36-37'] and mars6[0]['portional'] and "portionally" in mars6[0]['text']
    assert not any("full Moon" in e['text'] for e in ph[6]['Moon']['Rhetorius'])
    assert all(e['conditional'] for h in ph for p in PLANETS for e in ph[h][p]['Rhetorius'] if e['text'].startswith("With Mars in another pivot"))
    # the flag is Firmicus's word for the placement, or inherited where the run
    # refers back to the place's opening sentence that states it; III.2, 18 says
    # "in this sign" and carries none
    assert [e['portional'] for e in ph[4]['Saturn']['Rhetorius'] if e['author'] == 'Firmicus'] == [True, False]
    inherited = {(1, 'Saturn', 'III.2, 4-5'), (7, 'Saturn', 'III.2, 30'), (10, 'Saturn', 'III.2, 41-43'), (10, 'Saturn', 'III.2, 44-48'),
                 (4, 'Mars', 'III.4, 22-25'), (10, 'Mars', 'III.4, 80-81')}
    assert all(next(e for e in ph[h][p]['Rhetorius'] if e['cite'] == c)['portional'] for h, p, c in inherited)
    conditional = sum(1 for h in ph for p in PLANETS for e in ph[h][p]['Rhetorius'] if e['conditional'])
    portional = sum(1 for h in ph for p in PLANETS for e in ph[h][p]['Rhetorius'] if e['portional'])
    assert conditional == 60 and portional == 35


def test_no_guide_wording_survives_in_an_entry(engine):
    # The Guide's compressions the app used to carry, verbatim, and the
    # build-C sect prefixes and "(Firmicus)" tags.
    ph = engine["PLANETS_IN_HOUSES"]
    old = {'Eldest sibling.', 'Worse than by night?', 'With Jupiter and Venus, better than by night.', 'See above.', 'Priests, wizards.',
           'Middling goods over time', 'Many goods, dignity', 'Luckiness/authority (with fortunes)'}
    for h in ph:
        for p in PLANETS:
            for e in ph[h][p]['Rhetorius']:
                assert e['text'] not in old and '(Firmicus)' not in e['text'], (h, p, e['text'][:40])
                assert 'Worse than by night' not in e['text'] and 'healthy, victory over enemies' not in e['text']


def test_the_planets_reader_prints_the_halves_the_entries_and_the_moon_pointer(engine):
    # A PN IV half prints as "<text> (<locator>)", the Moon's pointer bare;
    # an entry as "Author (axis): <text>[ (portionally)] [<locator>]"; the
    # third column joins the entries with a middle dot, keeps the whole list
    # under RHETORIUS_CELL_WORDS, and over it prints the entries that are
    # not conditional and says how many it sent to the row's detail (all
    # entries if every one is conditional).
    fmt, cell, entry_text = engine["planets_in_houses_cell"], engine["rhetorius_entries_cell"], engine["rhetorius_entry_text"]
    ph = engine["PLANETS_IN_HOUSES"]
    assert fmt(9, "Mercury", "Good") == ph[9]["Mercury"]["PN IV"]["Good"]["text"] + " (II.21, 8 (shared with the 3rd))"
    assert fmt(11, "Saturn", "Good") == ph[11]["Saturn"]["PN IV"]["Good"]["text"] + " (II.6, 4 (shared with the 5th))"
    assert fmt(1, "Moon", "Bad") == MOON_POINTER
    e = ph[1]["Saturn"]["Rhetorius"][4]
    assert entry_text(e) == "Firmicus (by day): " + e["text"] + " (portionally) [III.2, 1-3]"
    assert entry_text(ph[1]["Saturn"]["Rhetorius"][0]) == "Rhetorius (by day): " + ph[1]["Saturn"]["Rhetorius"][0]["text"] + " [Ch. 57, the first, pp. 51-52]"
    words = engine["RHETORIUS_CELL_WORDS"]
    assert words == 60
    for h in ph:
        for p in PLANETS:
            entries = ph[h][p]['Rhetorius']
            total = sum(len(x['text'].split()) for x in entries)
            shown = entries if total <= words else ([x for x in entries if not x['conditional']] or entries)
            expected = " · ".join(entry_text(x) for x in shown)
            left = len(entries) - len(shown)
            if left:
                expected += f" · {left} conditional {'entry' if left == 1 else 'entries'} in the row's detail"
            assert cell(h, p) == expected, (h, p)
    assert "2 conditional entries in the row's detail" in cell(1, "Saturn")
    assert cell(6, "Mars").count(" · ") == 2 and "in the row's detail" not in cell(6, "Mars")
    planets = {p: {'longitude': lon} for p, lon in
               [('Saturn', 10.0), ('Jupiter', 40.0), ('Mars', 70.0), ('Sun', 100.0),
                ('Venus', 130.0), ('Mercury', 160.0), ('Moon', 190.0)]}
    cond = {p: {'Net': 0, 'Condition': 'Good'} for p in planets}
    rows = engine["evaluate_planets_in_houses"](planets, cond, 0.0)
    assert len(rows) == 7
    for row in rows:
        h = row['Placed in (WS place)']
        assert row['If in a suitable condition'] == fmt(h, row['Planet'], 'Good')
        assert row['If in a bad condition'] == fmt(h, row['Planet'], 'Bad')
        assert row['Rhetorius and Firmicus, as the texts state it'] == cell(h, row['Planet'])
        assert row['Entries'] == [entry_text(x) for x in ph[h][row['Planet']]['Rhetorius']]
        assert 'If Well Placed' not in row and 'If Badly Placed' not in row
    moon = engine["evaluate_moon_in_houses"](planets, 0.0)
    assert [r['House'] for r in moon] == list(range(1, 13))
    assert [r['Natal Moon here'] for r in moon] == [''] * 6 + ['Yes'] + [''] * 5
    assert all(r['Reading'] == engine["MOON_IN_HOUSES_VII8"][r['House']]['text'] and r['Locator'] == f"VII.8, {r['House']}" for r in moon)
    assert [r['Natal Moon here'] for r in engine["evaluate_moon_in_houses"]({}, 0.0)] == [''] * 12


def _planets_notes(at):
    """The text of the Topical Planets in Houses notes expander: the headed
    sections that took the old heading tooltip's sentences (readability
    branch A, 2026-09-17)."""
    for node in at.main:
        if getattr(node, "type", None) == "status" and node.label == "Sources and editorial notes":
            text = "\n".join(m.value for m in node.markdown)
            if "Which sources each column represents" in text:
                return text
    raise LookupError("the planets notes expander")


def test_the_help_and_caption_state_what_the_table_is(engine):
    # The counts are in the notes (the old tooltip's sentences, under
    # headings); the tooltip is one sentence; the adaptation statement is
    # visible body text above the grid; the Moon's table stands under the
    # main one with its own help.
    at = make_app(page="dignities").run()
    assert_no_exception(at, "dignities")
    heading = [h for h in at.main.subheader if h.value == "Topical Planets in Houses"][0]
    assert heading.help == ("Each planet's whole-sign house placement with the readings for that pairing from two "
                            "traditions, in three text columns, every entry with its locator.")
    notes = _planets_notes(at)
    counts = ENTRY_COUNTS_THE_HELP_STATES
    assert (f"{sum(counts.values())} entries: {counts['Rhetorius']} by Rhetorius, {counts['Firmicus']} by Firmicus and "
            f"{counts['Rhetorius, as summarized by Dykes']} by Dykes's summary; no cell is without one") in notes
    for phrase in ("Rhetorius and Firmicus, as the texts state it", "If in a suitable condition and If in a bad condition",
                   "the absence of testimony, not a neutral reading", "general malefic or general benefic testimony",
                   "Every PN IV half has text", "the TNAC Reference Guide for the Planets and Places (Dykes, 2023)",
                   "about sixty words", "condition not explicitly stated"):
        assert phrase in notes, phrase
    assert notes.count("TNAC Reference Guide") == 1
    for section in ("**Which sources each column represents.**", "**How conditional entries are included.**",
                    "**Misplaced, missing and supplemented passages.**", "**How PN IV is adapted to natal placements.**",
                    "**Why both condition readings remain visible.**"):
        assert section in notes, section
    adaptation = ("**Natal adaptation.** "
                  "The Book II entries adapt PN IV's annual rules for planets serving as lord of the year to natal house positions. "
                  "The source evaluates the root and revolution together; the natal lookup does not establish those annual prerequisites. "
                  "The columns summarize suitable and adverse conditions, with the qualifications shown in each entry.")
    assert adaptation in [m.value for m in at.main.markdown]
    captions = [c.value for c in at.main.caption]
    assert any(c.startswith("The third column is Rhetorius Ch. 57 and Firmicus, Mathesis III, as the texts state it") for c in captions)
    assert not any("If Well Placed" in c or "Fifteen Rhetorius halves" in c for c in captions)
    moon = [h for h in at.main.subheader if h.value == "The Moon in the houses — PN IV VII.8, by her transit"]
    assert len(moon) == 1 and moon[0].help.startswith("A natal analogy:")
    # The tooltip's long sentence is visible body text above the table since
    # readability branch B (2026-09-17); the tooltip keeps its opening.
    moon_summary = [m.value for m in at.main.markdown if m.value.startswith("A natal analogy: VII.8 reads the Moon's transit")]
    assert len(moon_summary) == 1 and "supplies no condition split" in moon_summary[0]
    frames = [n.value for n in at.main if getattr(n, "type", None) == "dataframe"]
    moon_frame = [f for f in frames if list(f.columns) == ['House', 'Reading', 'Locator', 'Natal Moon here']]
    assert len(moon_frame) == 1 and len(moon_frame[0]) == 12 and list(moon_frame[0]['Natal Moon here']).count('Yes') == 1
    tables = [n for n in at.main if getattr(n, "type", None) == "table"]
    assert any(list(t.value.columns) == ['Planet', 'Net', 'Standing', 'If in a suitable condition', 'If in a bad condition',
                                         'Rhetorius and Firmicus, as the texts state it'] for t in tables)


def _planet_panel(at):
    """The detail panel's lines: the placement line, the two PN IV halves,
    the entries heading, and the entries (readability branch A: the panel
    is bold-led body text under the "Read details for" selectbox, no
    longer a subheader with the entries alone)."""
    lines = [m.value for m in at.main.markdown]
    heads = [l for l in lines if re.match(r"^\*\*\w+ in the \d+\w\w place\.\*\* Lean: ", l)]
    return heads, lines


def test_selecting_a_planets_row_prints_every_entry_of_its_list(engine):
    at = make_app(page="dignities")
    at.session_state["topical_planets_in_houses_grid"] = {"selection": {"rows": [0], "columns": []}}
    at.run()
    assert_no_exception(at, "dignities")
    heads, lines = _planet_panel(at)
    assert len(heads) == 1
    planet = heads[0][2:].split(" in the ")[0]
    house = int(re.search(r" in the (\d+)", heads[0]).group(1))
    row = _planets_row(at, planet)
    assert row['Placed in (WS place)'] == house
    assert heads[0] == f"**{planet} in the {engine['HOUSE_ORDINAL'][house]} place.** Lean: {row['Lean']} (Net {row['Net']}; {row['Standing']})."
    entries = engine["PLANETS_IN_HOUSES"][house][planet]['Rhetorius']
    assert f"**Rhetorius and Firmicus, as the texts state it: {len(entries)} {'entry' if len(entries) == 1 else 'entries'}.**" in lines
    assert f"**If in a suitable condition (PN IV).** {row['If in a suitable condition']}" in lines
    assert f"**If in a bad condition (PN IV).** {row['If in a bad condition']}" in lines
    printed = [l for l in lines if l.startswith(("Rhetorius", "Firmicus"))]
    assert printed == [engine["rhetorius_entry_text"](e) for e in entries]
    # The row click wrote the selectbox's key: the selectbox is the state.
    box = [s for s in at.main.selectbox if s.key == "topical_planets_in_houses_detail"][0]
    assert box.value == planet
    bare = make_app(page="dignities").run()
    assert not _planet_panel(bare)[0]
    assert [s for s in bare.main.selectbox if s.key == "topical_planets_in_houses_detail"][0].value is None


def _planets_row(at, planet):
    """The page's own row for one planet, read back from the two tables it
    prints: the selectable grid (Planet, Placed in, Lean) and the readings
    table in the expander (Net, Standing, the two PN IV halves)."""
    grid = [df.value for df in at.main.dataframe if list(df.value.columns) == ['Planet', 'Placed in (WS place)', 'Lean']][0]
    readings = [t.value for t in at.main if getattr(t, "type", None) == "table"
                and 'If in a suitable condition' in t.value.columns][0]
    g = grid[grid['Planet'] == planet].iloc[0]
    r = readings[readings['Planet'] == planet].iloc[0]
    return {'Placed in (WS place)': int(g['Placed in (WS place)']), 'Lean': g['Lean'], 'Net': int(r['Net']),
            'Standing': r['Standing'], 'If in a suitable condition': r['If in a suitable condition'],
            'If in a bad condition': r['If in a bad condition']}


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
