"""Sahl: indications of fortune and livelihood (On Nativities Ch. 2) -- the
synthesis from the first and second lords of the sect light's triplicity
(2.11, 1-5), the partnering lord (2.11, 4; 2.3, 22), the Lot step (2.3, 6-9;
2.16; 2.20) -- against Abu 'Ali's twelve worked charts (PN I, JN Ch. 7,
Figures 10-21).

The fixtures' evidential status. Each chart is built from what Abu 'Ali
PRINTS: the signs of the planets and of the Ascendant, and the degrees only
where his text gives them (Figures 16 and 18-21; his ordinal words are taken
as the numbers, "the eighth degree, fourth minute" as 8.07, and Dykes's wheel
prints each one degree lower). An unprinted degree is unknown: the sign-only
charts (Figures 10-15, 17) put every planet at 0 of its sign for the whole-
sign place alone, and nothing that depends on that 0 is asserted of them --
no burning or rays, no application or separation, no degree-angularity, no
ascensional grade, and no Lot of Fortune, since a Lot computed from unprinted
degrees could stand in any one of three signs (the Ascendant, the Moon and
the Sun each anywhere in its sign, the sum ranges over ninety degrees); those
charts carry no Lot. A sign-only lord printed in the Sun's sign is not judged
for the rays at all: at 0 with him the app reads it in his heart, at any real
separation under the orb under the rays, and the printed sign cannot tell --
so Figure 10's Venus, Figure 11's Mercury, Figure 17's Mercury and Saturn,
Figure 14's Mercury and Saturn and Figure 15's Moon are asserted by place
alone, and Figure 11 pins no synthesis, the 0 deciding it. A planet printed
with its sign only in a degree chart (Figure 21's Mars) is at 0 for the same
reason. Six of the twelve are internally inconsistent by
Dykes's own notes or by the printed signs against Abu 'Ali's words (Figures
14, 15, 16, 18, 21; Figure 20's rise rests on grounds Sahl does not state,
and fn 60 warns of calculation errors in its Lot): those six are textual
observations -- they assert the places the app reads from the printed signs
and that the synthesis is NOT the verdict Abu 'Ali states, with Dykes's note
in the message, and pin no expected class. The other six assert the lords'
places, strong or falling, the partnering lord's effect, the Lot's place
where it is printed, and the synthesis.
"""
import re
from pathlib import Path

import pytest

from corpus_paths import corpus_file

CORPUS = corpus_file("on_nativities.md")
PN1 = CORPUS.parent / "pn1" / "pn1_photographed.md"
COLUMNS = ['Class', 'Ground', 'Sahl', 'Also']


def _normalised(text):
    """Footnote marks, footnote blocks and page markers out, entities in,
    whitespace collapsed -- so a sentence split by a page break compares."""
    text = re.sub(r"\n\n<sup>\d+</sup>[^\n]*", "", text)
    text = re.sub(r"\n\n---\n\n\*\[Sahl I p\. \d+\]\*", "", text)
    text = re.sub(r"<sup>\d+</sup>", "", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("*", "")
    return re.sub(r"\s+", " ", text)


@pytest.fixture(scope="module")
def chapter_two():
    if not CORPUS.exists():
        pytest.skip("the corpus is not on this machine")
    text = CORPUS.read_text(encoding="utf-8")
    start = text.index("### Chapter 2: On assets, fortune, & livelihood")
    end = text.index("### [Chapter 2.22:")
    return _normalised(text[start:end])


def test_every_sahl_sentence_is_verbatim(engine, chapter_two):
    sentences = engine["PROSPERITY_SAHL"]
    assert len(sentences) == 48
    for ref, sentence in sentences.items():
        assert re.sub(r"\s+", " ", sentence) in chapter_two, ref


def test_abu_ali_and_ba_quotations_are_verbatim(engine):
    if not PN1.exists():
        pytest.skip("the corpus is not on this machine")
    pn1 = re.sub(r"\s+", " ", re.sub(r"<sup>\d+</sup>", "", PN1.read_text(encoding="utf-8")).replace("*", ""))
    also = engine["PROSPERITY_ALSO"]
    for quoted in re.findall(r'"([^"]+)"', also['angles']) + re.findall(r'"([^"]+)"', also['cadent']) + \
            re.findall(r'"([^"]+)"', also['mixed']) + re.findall(r'"([^"]+)"', also['lot']) + \
            re.findall(r'"([^"]+)"', also['succedent']) + re.findall(r'"([^"]+)"', also['third']) + \
            re.findall(r'"([^"]+)"', also['middling']) + re.findall(r'"([^"]+)"', also['eleventh from the lot']):
        assert quoted in pn1, quoted


def test_classes_are_sahl_s_six_keys_and_the_seventh_split(engine):
    assert list(engine["PROSPERITY_CLASSES"]) == ['high', 'high to low', 'middling', 'low to high', 'low', 'own hands', 'injustice']


# --- the twelve charts ----------------------------------------------------

def _chart(engine, sect, asc, lot=False, **positions):
    """A chart by sign, a degree where one is given. lot=True computes the
    Lot of Fortune from the positions (only for a chart whose degrees are
    printed); a sign-only chart carries none."""
    S = {s: i * 30.0 for i, s in enumerate(engine['SIGN_ORDER'])}
    natal = {}
    for planet, where in positions.items():
        sign, deg = (where, 0.0) if isinstance(where, str) else where
        natal[planet] = {'longitude': S[sign] + deg, 'latitude': 0.0, 'distance': 1.0}
    asc_lon = S[asc[0]] + asc[1] if isinstance(asc, tuple) else S[asc]
    lot_lon = engine['lot_by_id']('fortune', natal, asc_lon, None, sect) if lot else None
    return {'planetary_data': natal, 'ascendant': asc_lon, 'sect': sect, 'lot_of_fortune': lot_lon}


CLASS_NUMBER = {'high': 1, 'high to low': 2, 'low to high': 5, 'low': 6}


def _verdict(engine, chart):
    """The synthesis row's key and the rows. key is a class word when the
    app reads one class (the two lords alone, or the Lot concordant with
    them), 'mixed' when the Lot's level stands beside the mixed pair's
    timing pattern, 'unresolved' when the judgments are opposed; the Class
    cell carries the class field after 'Synthesis (this app): '."""
    rows = engine['evaluate_prosperity'](chart)
    assert rows and all(list(r)[:4] == COLUMNS for r in rows)
    top = rows[0]
    if top['key'] in CLASS_NUMBER:
        assert top['Class'].startswith('Synthesis (this app): ')
        field = top['Class'][len('Synthesis (this app): '):]
        label = engine['PROSPERITY_CLASSES'][top['key']]
        assert field == f"class {CLASS_NUMBER[top['key']]}"
        assert 'read by this app as class' in top['Ground'] and label[0].lower() + label[1:] in top['Ground']
    elif top['key'] == 'mixed':
        field = top['Class'][len('Synthesis (this app): '):]
        assert 'by the Lot; class' in field and "'s pattern by the lords" in field
    else:
        assert top['key'] == 'unresolved'
        assert isinstance(top['Class'], engine['UnresolvedResult'])
        assert top['Class'].alternatives
    assert 'Synthesis: ' in top['Ground']
    return top['key'], rows


def _row(rows, key):
    found = [r for r in rows if r['key'] == key]
    assert len(found) == 1, key
    return found[0]


# The six whose printed signs carry Abu 'Ali's verdict.

def test_example_1_figure_10_a_pauper(engine):
    """Nocturnal, Gemini ascending: the Moon in Scorpio, her lords Mars
    (Aquarius, the ninth) and Venus (Leo, the third), "both cadent from the
    angles -- which were signifying poverty and the bad condition of the
    native. Wherefore this native was even a pauper"."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Gemini', Sun='Leo', Venus='Leo', Saturn='Scorpio',
                                        Moon='Scorpio', Mars='Aquarius', Jupiter='Taurus', Mercury='Virgo'))
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Mars in Aquarius, the 9th, falling from the stakes' in lords
    # Venus is printed in the Sun's sign: her place and falling by place only, nothing on the rays
    assert 'Second: Venus in Leo, the 3rd, falling from the stakes' in lords
    assert key == 'low'                                   # both falling by place, whatever the rays
    assert 'both lords weak -- Mars falling (2.11, 3)' in rows[0]['Ground'] and '2.11, 3' in rows[0]['Sahl']
    assert 'the Lot step (2.3, 6), Mars and Venus made unfortunate -- the either-lord entry being this app\'s reading of the sentence\'s singular: no Lot of Fortune in hand' in rows[0]['Ground']
    third = _row(rows, 'third')['Ground']
    assert third.startswith('Third: Moon in Scorpio, the 6th, falling from the stakes') and 'brings [them] down' in third
    assert 'Modified by the partnering lord (2.11, 4): Moon in Scorpio, the 6th, falling from the stakes -- brings [them] down' in rows[0]['Ground']


def test_example_2_figure_11_a_most_elegant_affair(engine):
    """Diurnal by the delineation (the figure's caption says nocturnal; the
    text reads the Sun's lords and the Sun stands in the eleventh): Saturn
    in Scorpio, the eighth, Mercury in Aquarius, the eleventh, "both in
    succeedents of the angles ... signifying prosperity and riches"."""
    _key, rows = _verdict(engine, _chart(engine, 'Diurnal', 'Aries', Sun='Aquarius', Mercury='Aquarius', Moon='Sagittarius',
                                         Saturn='Scorpio', Mars='Scorpio', Jupiter='Cancer', Venus='Capricorn'))
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Saturn in Scorpio, the 8th, what follows a stake' in lords
    # Mercury is printed in the Sun's sign: his place only, and no synthesis -- the 0 would decide it
    assert 'Second: Mercury in Aquarius, the 11th, what follows a stake' in lords and 'Saturn by square, Mars by square' in lords
    # 2.3, 18 wants the stake by degrees and is its own row; no cusps, so none
    assert '2.3, 18' not in rows[0]['Sahl'] and not [r for r in rows if r['key'] == 'by degree']
    assert _row(rows, 'third')['Ground'].startswith('Third: Jupiter in Cancer, the 4th, a stake') and 'supports them both' in _row(rows, 'third')['Ground']
    # a lord with an infortune on it is made unfortunate for 2.3, 6; the chart carries no Lot to turn to
    assert 'the Lot step (2.3, 6), Saturn and Mercury made unfortunate -- the either-lord entry being this app\'s reading of the sentence\'s singular: no Lot of Fortune in hand' in rows[0]['Ground']
    assert any(r['Class'] == 'Decline' and r['Ground'].startswith('Saturn, a lord of the sect light\'s triplicity, in the 8th') for r in rows)


def test_example_3_figure_12_great_and_eminent(engine):
    """Nocturnal, Scorpio ascending: Mars (Aquarius, the fourth), Venus
    (Taurus, the seventh), the Moon (Scorpio, the first), "all in angles --
    which signified prosperity, loftiness and a kingdom". Saturn in the
    eleventh is listed under it (2.3, 12; 2.17, 7) and does not move it."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Scorpio', Moon='Scorpio', Sun='Aries', Mars='Aquarius',
                                        Venus='Taurus', Mercury='Pisces', Jupiter='Virgo', Saturn='Virgo'))
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Mars in Aquarius, the 4th, a stake' in lords and 'Second: Venus in Taurus, the 7th, a stake' in lords
    assert key == 'high'
    assert 'both lords strong, both in the stakes' in rows[0]['Ground'] and '2.3, 2' in rows[0]['Sahl']
    assert _row(rows, 'third')['Ground'].startswith('Third: Moon in Scorpio, the 1st, a stake') and 'supports them both' in _row(rows, 'third')['Ground']
    falls = [r for r in rows if r['key'] == 'falling']
    assert any('Saturn in the eleventh from the Ascendant' == r['Ground'] for r in falls)
    assert any(r['Ground'].startswith('Saturn in the eleventh: takes away') for r in rows if r['key'] == 'eleventh')


def test_example_4_figure_13_honored_among_kings(engine):
    """Diurnal, Cancer ascending: the Sun (Aries, the tenth) and Jupiter
    (Cancer, the first), "both in angles and their own exaltations"; Saturn
    the third lord "cadent from an angle in a domicile of Jupiter"."""
    key, rows = _verdict(engine, _chart(engine, 'Diurnal', 'Cancer', Sun='Aries', Mercury='Aries', Jupiter='Cancer',
                                        Moon='Cancer', Saturn='Pisces', Venus='Taurus', Mars='Scorpio'))
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Sun in Aries, the 10th, a stake' in lords and 'Second: Jupiter in Cancer, the 1st, a stake' in lords
    assert key == 'high'
    third = _row(rows, 'third')['Ground']
    assert third.startswith('Third: Saturn in Pisces, the 9th, falling from the stakes') and 'brings [them] down' in third and 'ranked third (2.3, 22)' in third
    assert 'Modified by the partnering lord (2.11, 4): Saturn in Pisces, the 9th, falling from the stakes -- brings [them] down, a falling place; no class step' in rows[0]['Ground']
    assert 'the Lot step' not in rows[0]['Ground']          # neither lord weak nor with an infortune on it


def test_example_8_figure_17_poor_fortune(engine):
    """Nocturnal, Virgo ascending: the Moon in Gemini, Mercury and Saturn
    both in Aquarius, the sixth, "both cadent, who were signifying poverty
    and the bad condition of this native"."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Virgo', Moon='Gemini', Saturn='Aquarius', Sun='Aquarius',
                                        Mercury='Aquarius', Mars='Capricorn', Venus='Sagittarius', Jupiter='Virgo'))
    lords = _row(rows, 'lords')['Ground']
    # both lords are printed in the Sun's sign: their places and falling by place only, nothing on the rays
    assert 'First: Mercury in Aquarius, the 6th, falling from the stakes' in lords
    assert 'Second: Saturn in Aquarius, the 6th, falling from the stakes' in lords
    assert key == 'low'                                   # both falling by place, whatever the rays
    assert 'both lords weak' in rows[0]['Ground'] and '2.11, 3' in rows[0]['Sahl']
    assert _row(rows, 'third')['Ground'].startswith('Third: Jupiter in Virgo, the 1st, a stake') and 'supports them both' in _row(rows, 'third')['Ground']


def test_example_10_figure_19_prosperity_after_labor(engine):
    """Nocturnal, 21 Taurus ascending, the degrees printed: the Moon in
    Pisces; Mars "under the rays of the Sun, in the square aspect of Saturn
    -- which signified the native's labor and anxiety in the first third of
    his life"; Venus "in an angle, oriental ... signifying prosperity and
    the native's good condition after labor". The Lot at 7 Sagittarius as
    the text has it, the eighth; all four looking at it by sign (2.16, 4)
    is the Lot's judgment, middling, carried beside the two lords' timing
    pattern with no single class, the first lord being made unfortunate."""
    chart = _chart(engine, 'Nocturnal', ('Taurus', 21.0), lot=True, Moon=('Pisces', 1.0), Sun=('Virgo', 17.0),
                   Saturn=('Sagittarius', 14.0), Jupiter=('Libra', 17.0), Mars=('Virgo', 21.0), Venus=('Leo', 17.0),
                   Mercury=('Libra', 5.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Sagittarius' and abs(chart['lot_of_fortune'] % 30 - 7.0) < 1e-9
    key, rows = _verdict(engine, chart)
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Mars in Virgo, the 5th, what follows a stake, under the rays (no strength, 2.11, 5); infortunes on it: Saturn by square' in lords
    assert 'Second: Venus in Leo, the 4th, a stake' in lords
    assert key == 'mixed'
    assert rows[0]['Class'] == "Synthesis (this app): middling by the Lot; class 5's pattern by the lords"
    assert 'the first lord weak -- Mars under the rays (2.11, 5) -- the second strong: benefit in the time of the strong one (2.11, 2)' in rows[0]['Ground']
    assert 'the Lot of Fortune in Sagittarius, the 8th, what follows a stake' in rows[0]['Ground']
    # the two attributed clauses, the Lot's judgment and the two lords', each with its sentence
    assert ("Synthesis: the Lot indicates middling livelihood (2.16, 4); the two triplicity lords indicate hardship in the "
            "first lord's time and benefit in the second's (2.11, 2) -- middling by the Lot; class 5's pattern by the lords, "
            "the fifth: rises up after wretchedness (2.1, 7), the first lord's time being the beginning of life (2.13, 39); "
            "the combination is this app's, Sahl giving no express precedence between the Lot's sentences and Theophilus's") in rows[0]['Ground']
    assert "the either-lord entry being this app's reading of the sentence's singular" in rows[0]['Ground']
    # Sahl 2.11, 2 verbatim beside it, with the Lot's sentence
    assert engine['PROSPERITY_SAHL']['2.11, 2'] in rows[0]['Sahl'] and engine['PROSPERITY_SAHL']['2.16, 4'] in rows[0]['Sahl']
    assert '2.13, 39' in rows[0]['Sahl'] and '2.3, 6' in rows[0]['Sahl']
    assert _row(rows, 'third')['Ground'].startswith('Third: Moon in Pisces, the 11th, what follows a stake') and 'supports them both' in _row(rows, 'third')['Ground']


# The six whose printed signs do not carry Abu 'Ali's verdict: textual
# observations. Each asserts what the app reads from the printed signs and
# that the synthesis is not the class he states; no expected class.

def test_example_5_figure_14_a_middling_life(engine):
    """Nocturnal, Cancer ascending: the Moon in Gemini, her lords Mercury
    and Saturn both in Scorpio; Abu 'Ali reads them "cadent from the
    angles" and Jupiter "in the succeedent to the angle of the Midheaven",
    tempering them to "a middling life"."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Cancer', Jupiter='Gemini', Moon='Gemini', Saturn='Scorpio',
                                        Sun='Scorpio', Mercury='Scorpio', Mars='Virgo', Venus='Virgo'))
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Mercury in Scorpio, the 5th, what follows a stake' in lords
    assert 'Second: Saturn in Scorpio, the 5th, what follows a stake' in lords
    assert _row(rows, 'third')['Ground'].startswith('Third: Jupiter in Gemini, the 12th, falling from the stakes')
    assert key != 'middling', (
        'Dykes, PN I fn 51 to Figure 14: "Note that while the text puts Jupiter in Gemini, that is not a succeedent '
        'place (nor is Scorpio cadent here). Dorotheus puts Jupiter and the Moon in Libra, which is angular, while '
        'Masha\'allah puts them both in Virgo, which is cadent." By whole sign Mercury and Saturn stand in the fifth, '
        'what follows a stake, and Jupiter in the twelfth: the printed signs do not carry the middling life he states.')


def test_example_6_figure_15_lofty_and_wealthy(engine):
    """Diurnal, Gemini ascending: the Sun in Pisces; Abu 'Ali names the
    Sun, Jupiter and Saturn as the lords, "all appearing in the angles ...
    fortune and a multitude of riches"."""
    key, rows = _verdict(engine, _chart(engine, 'Diurnal', 'Gemini', Sun='Pisces', Saturn='Pisces', Moon='Pisces',
                                        Mercury='Aries', Jupiter='Aries', Mars='Virgo', Venus='Taurus'))
    lords = _row(rows, 'lords')['Ground']
    assert 'The Sun, the sect light, in Pisces; its lords Venus, Mars, Moon' in lords
    assert 'First: Venus in Taurus, the 12th, falling from the stakes' in lords
    assert 'Second: Mars in Virgo, the 4th, a stake' in lords
    assert key != 'high', (
        'Dykes, PN I fn 52 to Figure 15: "the positions do not match the delineation, as the Sun is in a watery sign, '
        'not a fiery one. Dorotheus has the Sun and Jupiter switching places ... Dorotheus\'s delineation is the only '
        'one that makes sense". By the printed signs the Sun in Pisces has Venus (the twelfth) and Mars (the fourth) '
        'for lords, not the Sun, Jupiter and Saturn he names: the printed signs do not carry the first class he states.')


def test_example_7_figure_16_labor_and_scarcity(engine):
    """Diurnal, the beginning of Scorpio ascending, the degrees printed:
    Saturn in Taurus and Mercury in Scorpio, which Abu 'Ali reads as
    cadent and "each was the detriment of the other"; Jupiter cadent; the
    Lot at 18 Virgo with Mars -- "labor and a scarcity of goods". The Lot
    computed from his positions is 18 Virgo, as printed."""
    chart = _chart(engine, 'Diurnal', ('Scorpio', 0.0), lot=True, Jupiter=('Libra', 21.2), Sun=('Libra', 8.0),
                   Mercury=('Scorpio', 11.25), Saturn=('Taurus', 15.0), Moon=('Leo', 26.0), Mars=('Virgo', 18.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Virgo' and abs(chart['lot_of_fortune'] % 30 - 18.0) < 1e-9
    key, rows = _verdict(engine, chart)
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Saturn in Taurus, the 7th, a stake' in lords
    assert 'Second: Mercury in Scorpio, the 1st, a stake; infortunes on it: Saturn by opposition' in lords
    assert _row(rows, 'third')['Ground'].startswith('Third: Jupiter in Libra, the 12th, falling from the stakes')
    assert 'the Lot of Fortune in Virgo, the 11th, what follows a stake' in rows[0]['Ground']
    assert key != 'low', (
        'Dykes, PN I fn 53 to Figure 16: "Also, Saturn is not cadent." Abu \'Ali reads Saturn (Taurus, the seventh) '
        'as cadent; by whole sign Saturn and Mercury both stand in the stakes, Mars in the eleventh from the Ascendant '
        'is listed as a fall, and the printed signs do not carry the labor and scarcity he states.')


def test_example_9_figure_18_labor_and_want(engine):
    """Nocturnal, 16 Gemini ascending (Dykes's Ascendant from the Lot), the
    degrees printed: the Moon in Aries, her lords Jupiter (Scorpio) and the
    Sun (Sagittarius), which Abu 'Ali reads "both cadent from the angles in
    the sign of the 6th"; the Lot in the ninth, its lord not regarding it
    -- "labor and want". The Lot computed from his positions is 9
    Aquarius, as printed with fn 57's Aquarius for Pisces."""
    chart = _chart(engine, 'Nocturnal', ('Gemini', 16.0), lot=True, Moon=('Aries', 16.0), Jupiter=('Scorpio', 22.0),
                   Venus=('Scorpio', 13.0), Saturn=('Pisces', 15.0), Mercury=('Scorpio', 21.0),
                   Sun=('Sagittarius', 9.0), Mars=('Sagittarius', 19.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Aquarius' and abs(chart['lot_of_fortune'] % 30 - 9.0) < 1e-9
    key, rows = _verdict(engine, chart)
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Jupiter in Scorpio, the 6th, falling from the stakes' in lords
    assert 'Second: Sun in Sagittarius, the 7th, a stake' in lords
    assert 'the Lot of Fortune in Aquarius, the 9th, falling from the stakes; its lord Saturn in Pisces, the 10th, western, not looking at the Lot' in rows[0]['Ground']
    assert key != 'low', (
        'Dykes, PN I fn 56 to Figure 18: "The delineation text states that both Jupiter and the Sun are in cadent "in '
        'the sign of the 6th," but both Masha\'allah\'s and Abu \'Ali\'s charts have the Sun in the seventh sign. '
        'Because Masha\'allah\'s chart has a much later Ascendant degree, his Sun is cadent by standard quadrant '
        'houses." By whole sign the Sun, the second lord, stands in the seventh, a stake: the printed signs do not '
        'carry the labor and want he states.')


def test_example_11_figure_20_good_condition_at_the_end(engine):
    """Nocturnal, 2 30 Libra ascending, the degrees printed: the Moon in
    Cancer, her lords Mars (Sagittarius) and Venus (Pisces), "both cadent in
    the 6th and 3rd" -- which the printed signs carry; then "the Moon, who
    was the luminary of the time, was in the Midheaven, [and] she [was]
    also the last Lady of the triplicity; and the Lot of Fortune of the
    nature of Venus; they were signifying the beauty and good condition of
    the native at the end of his life". The Lot computed from his positions
    is 4 Taurus where he prints the tenth degree; the same sign."""
    chart = _chart(engine, 'Nocturnal', ('Libra', 2.5), lot=True, Moon=('Cancer', 8.07), Saturn=('Gemini', 2.0),
                   Jupiter=('Sagittarius', 15.0), Sun=('Aquarius', 10.0), Mars=('Sagittarius', 15.0),
                   Venus=('Pisces', 25.0), Mercury=('Aquarius', 15.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Taurus'
    key, rows = _verdict(engine, chart)
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Mars in Sagittarius, the 3rd, falling from the stakes' in lords
    assert 'Second: Venus in Pisces, the 6th, falling from the stakes' in lords
    third = _row(rows, 'third')['Ground']
    assert third.startswith('Third: Moon in Cancer, the 10th, a stake') and 'supports them both in their elevation, through its strength' in third
    assert 'Modified by the partnering lord (2.11, 4): Moon in Cancer, the 10th, a stake -- supports them both' in rows[0]['Ground']
    assert 'the Lot of Fortune in Taurus, the 8th, what follows a stake' in rows[0]['Ground']
    assert key != 'low to high', (
        'Abu \'Ali\'s rise at Figure 20 rests on the Moon, "the luminary of the time ... in the Midheaven, [and] she '
        '[was] also the last Lady of the triplicity; and the Lot of Fortune of the nature of Venus": Sahl makes the '
        'partnering lord a support (2.11, 4) with no class step, and gives the Lot no rule by its nature; Abu \'Ali\'s '
        'own rule wants the Lot "conjoined to Jupiter or Venus", and the Lot in Taurus has neither. Dykes, fn 60: '
        '"Errors in calculation must be Abu \'Ali\'s, as the positions in Nativities yield a correct Lot of Fortune." '
        'Both lords fall and the printed signs do not carry the rise he states.')


def test_example_12_figure_21_fortune_from_the_middle_of_life(engine):
    """Diurnal, 10 07 Cancer ascending, the degrees printed (Mars by sign
    only): the Sun "in his own exaltation in the Midheaven, applying to
    Saturn, nor received by him"; Jupiter "cadent in the sign of the 6th";
    Saturn the third lord "in his own exaltation, was signifying prosperity
    for the native at the end of his life"; the Lot he prints at 18
    Sagittarius, "joined to Jupiter, and the Moon in the Midheaven from the
    Lot" -- fortune from the middle of life. The Lot computed from his
    positions falls in Capricorn."""
    chart = _chart(engine, 'Diurnal', ('Cancer', 10.12), lot=True, Sun=('Aries', 24.0), Moon=('Libra', 17.0),
                   Saturn=('Libra', 27.0), Jupiter=('Sagittarius', 17.0), Mars=('Sagittarius', 0.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Capricorn'
    key, rows = _verdict(engine, chart)
    lords = _row(rows, 'lords')['Ground']
    assert 'First: Sun in Aries, the 10th, a stake; infortunes on it: Saturn by opposition' in lords
    assert 'Second: Jupiter in Sagittarius, the 6th, falling from the stakes' in lords
    assert _row(rows, 'third')['Ground'].startswith('Third: Saturn in Libra, the 4th, a stake') and 'supports them both' in _row(rows, 'third')['Ground']
    assert 'the Lot of Fortune in Capricorn, the 7th, a stake' in rows[0]['Ground']
    assert key != 'low to high', (
        'Dykes, PN I fn 62 to Figure 21: "According to the positions given, this is not true (she is in the eleventh '
        'from the Lot). But the Lot cannot be in the given position anyway; it should rather be at 16° Capricorn, in '
        'which case the Moon would be in its Midheaven, but the Lot would no longer be joined to Jupiter." The Lot '
        'computed from his positions falls in Capricorn; the Sun (the tenth) is strong and Jupiter (the sixth) falls, '
        'the partnering Saturn in the fourth supports (2.11, 4) with no class step, and the printed positions do not '
        'carry the fortune from the middle of life he states; his weakening of the Sun, "applying to Saturn, nor '
        'received by him", is listed and not judged.')


# --- the rules beyond the twelve ------------------------------------------

def test_the_lot_raises_two_falling_lords(engine):
    """Diurnal, Aries ascending, the Sun at 10 Gemini (the third): Saturn
    (Virgo, the sixth) and Mercury (25 Gemini, the third) both fall. The
    Lot (the Moon at 10 Sagittarius) falls at 0 Libra, the seventh; its
    lady Venus in Aries, the first, eastern of the Sun, looking at the Lot
    by opposition, no infortune on her; Jupiter in Aquarius looking at the
    Lot by sextile; Saturn and Mars (Scorpio) not looking at Libra -- 2.3, 7
    met in full against 2.11, 3: opposed status judgments, unresolved, both
    kept. Mars moved to Cancer squares both the Lot and its lady: 2.3, 7
    fails and 2.16, 2 gives the middle, against baseness throughout --
    unresolved likewise."""
    chart = _chart(engine, 'Diurnal', 'Aries', lot=True, Sun=('Gemini', 10.0), Moon=('Sagittarius', 10.0), Saturn='Virgo',
                   Mercury=('Gemini', 25.0), Venus='Aries', Mars='Scorpio', Jupiter='Aquarius')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Libra'
    key, rows = _verdict(engine, chart)
    assert key == 'unresolved' and isinstance(rows[0]['Class'], engine['UnresolvedResult'])
    assert rows[0]['Ground'].startswith('both lords weak -- Saturn falling (2.11, 3); Mercury falling (2.11, 3)')
    assert ("the Lot step (2.3, 6), Saturn and Mercury made unfortunate -- the either-lord entry being this app's reading "
            "of the sentence's singular: the Lot in a stake" in rows[0]['Ground'])
    assert ("Synthesis: conflicting status indications -- the Lot promises very high rank, a king, or prominent, and a "
            "powerful noble (2.3, 7); the two weak triplicity lords indicate baseness throughout life (2.11, 3, read with "
            "2.11, 5) -- unresolved: this app installs no priority between them, Sahl giving no express precedence between "
            "the Lot's sentences and Theophilus's; both judgments stand") in rows[0]['Ground']
    assert '2.3, 6' in rows[0]['Sahl'] and engine['PROSPERITY_SAHL']['2.3, 7'] in rows[0]['Sahl'] and engine['PROSPERITY_SAHL']['2.11, 3'] in rows[0]['Sahl']
    assert 'read by this app as class' not in rows[0]['Ground']
    chart['planetary_data']['Mars']['longitude'] = 95.0
    key2, rows2 = _verdict(engine, chart)
    assert key2 == 'unresolved' and '2.16, 2' in rows2[0]['Sahl'] and not any(r['key'] == 'lot high' for r in rows2)
    assert 'Jupiter eastern looking at it from an excellent place' in rows2[0]['Ground']
    assert 'conflicting status indications -- the Lot indicates middling livelihood (2.16, 2); the two weak triplicity lords indicate baseness throughout life' in rows2[0]['Ground']


def test_the_lot_gives_the_middle_when_all_four_look_at_it(engine):
    """Nocturnal, Aries ascending, the Moon in Gemini: Mercury (Virgo, the
    sixth) and Saturn (Sagittarius, the ninth) fall. The Lot in Leo (the
    Sun in Libra) has Jupiter with it, Venus by sextile from Libra, Saturn
    by trine, Mars by square from Scorpio -- 2.16, 4, the middle, against
    2.11, 3's baseness throughout: unresolved; its lord the Sun in the
    seventh is no one's east, so 2.3, 7 is not met."""
    chart = _chart(engine, 'Nocturnal', 'Aries', lot=True, Moon='Gemini', Sun='Libra', Mercury='Virgo', Saturn='Sagittarius',
                   Jupiter='Leo', Venus='Libra', Mars='Scorpio')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Leo'
    key, rows = _verdict(engine, chart)
    assert key == 'unresolved' and '2.16, 4' in rows[0]['Sahl'] and '2.3, 6' in rows[0]['Sahl']
    assert 'conflicting status indications -- the Lot indicates middling livelihood (2.16, 4); the two falling triplicity lords indicate baseness throughout life (2.11, 3)' in rows[0]['Ground']
    assert [r['key'] for r in rows if r['key'].startswith('lot ')] == ['lot middling']


def test_misery_confirmed_by_the_lot_in_the_sixth(engine):
    """Diurnal, Cancer ascending, the Sun at 10 Libra: Saturn (Gemini, the
    twelfth) falls and Mercury at 14 Libra is burned; both weak. The Lot
    (the Moon at 10 Pisces) falls at 0 Sagittarius, the sixth, with Mars;
    its lord Jupiter in Capricorn, his fall; Mars by day with the Lot --
    2.20, 1's misery, concordant with 2.11, 3's baseness: the sixth class."""
    chart = _chart(engine, 'Diurnal', 'Cancer', lot=True, Sun=('Libra', 10.0), Moon=('Pisces', 10.0), Saturn='Gemini',
                   Mercury=('Libra', 14.0), Mars='Sagittarius', Jupiter='Capricorn', Venus='Virgo')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Sagittarius'
    key, rows = _verdict(engine, chart)
    assert key == 'low'
    # the weakness named per lord, never one word for both
    assert 'both lords weak -- Saturn falling (2.11, 3); Mercury under the rays (2.11, 5)' in rows[0]['Ground']
    assert "its word is falling, and a lord under the rays, which has no strength by 2.11, 5, is read with it by this app" in rows[0]['Ground']
    assert ('Synthesis: the Lot indicates misery from birth to death (2.20, 1); the two weak triplicity lords indicate baseness '
            'throughout life (2.11, 3, read with 2.11, 5) -- concordant, read by this app as class 6') in rows[0]['Ground']
    assert 'its lord in its fall' in rows[0]['Ground'] and '2.20, 1' in rows[0]['Sahl'] and rows[0]['Class'] == 'Synthesis (this app): class 6'
    assert 'Mercury in Libra, the 4th, a stake, under the rays (no strength, 2.11, 5)' in rows[0]['Ground']


def test_the_fifteen_degrees_by_ascension_at_the_equator(engine):
    """Obliquity 0 at latitude 0: ascension is longitude, so the arc after
    the stake is the zodiacal distance. Diurnal, 0 Aries rising, MC at 0
    Capricorn (armc 270): the Sun at 10 Aries is 10 degrees after the
    Ascendant (the first 15); Jupiter at 20 Taurus is 50 after it (beyond
    45, of the nativities of the poor)."""
    chart = _chart(engine, 'Diurnal', 'Aries', lot=True, Sun=('Aries', 10.0), Moon='Leo', Jupiter=('Taurus', 20.0), Saturn='Libra',
                   Mars='Leo', Venus='Leo', Mercury='Aries')
    chart.update({'armc': 270.0, 'obliquity': 0.0, 'geo_lat': 0.0, 'mc': 270.0})
    rows = engine['evaluate_prosperity'](chart)
    grades = [r for r in rows if r['key'] == 'ascensions']
    assert [g['Ground'].split(' -- ')[1].split('.')[0] for g in grades] == [
        'the first 15°: praise and good fortune', 'beyond 45°, up to the next stake: of the nativities of the poor']
    assert '10.0° of ascension after the Ascendant' in grades[0]['Ground'] and '2.13, 48' in grades[0]['Sahl']
    assert '2.13, 51' in grades[1]['Sahl']
    assert all('A third measure, the ascensional grade, beside the synthesis' in g['Ground'] and 'never folded into strong or weak' in g['Ground'] for g in grades)
    # Jupiter moved to 20 Cancer: 20 degrees after the fourth (0 Cancer) -- the second 15.
    chart['planetary_data']['Jupiter']['longitude'] = 110.0
    rows = engine['evaluate_prosperity'](chart)
    second = [r for r in rows if r['key'] == 'ascensions'][1]
    assert 'after the fourth -- the second 15°: below the first' in second['Ground'] and '2.13, 49' in second['Sahl']


def test_the_moon_s_separation_and_connection_by_degree(engine):
    """The Moon at 12 Aries, 13 a day, past Venus's trine from 10 Leo by two
    degrees and three short of Saturn's square from 15 Cancer: a fall
    (2.17, 10). Reverse the two planets and it is the rise (2.19, 2)."""
    def with_speeds(chart):
        for p, v in (('Moon', 13.0), ('Sun', 1.0), ('Saturn', 0.05), ('Jupiter', 0.1), ('Mars', 0.5), ('Venus', 1.0), ('Mercury', 1.0)):
            if p in chart['planetary_data']:
                chart['planetary_data'][p]['speed_in_lon'] = v
        return chart
    chart = with_speeds(_chart(engine, 'Diurnal', 'Aries', lot=True, Sun=('Gemini', 5.0), Moon=('Aries', 12.0), Venus=('Leo', 10.0),
                               Saturn=('Cancer', 15.0), Jupiter='Sagittarius', Mars='Capricorn', Mercury='Gemini'))
    rows = engine['evaluate_prosperity'](chart)
    fall = [r for r in rows if r['key'] == 'falling' and '2.17, 10' in r['Sahl']]
    assert len(fall) == 1 and fall[0]['Ground'] == 'the Moon separating from Venus and connecting with Saturn, by degree within her orb'
    chart['planetary_data']['Venus']['longitude'], chart['planetary_data']['Saturn']['longitude'] = 105.0, 130.0
    rows = engine['evaluate_prosperity'](chart)
    rise = [r for r in rows if r['key'] == 'rising' and '2.19, 2' in r['Sahl']]
    assert len(rise) == 1 and rise[0]['Ground'] == 'the Moon separating from Saturn and connecting with Venus, by degree within her orb'


def test_force_and_injustice_and_the_supplement_flag(engine):
    """Diurnal, Leo ascending, the Sun in Libra and the Moon in Leo: the Lot
    at 0 Gemini; Saturn and Mars both in Aries, the eleventh from it, Mars
    in his own house and Saturn in his triplicity -- 2.21, 3. Only 2.16,
    6's row is a supplement."""
    chart = _chart(engine, 'Diurnal', 'Leo', lot=True, Sun='Libra', Moon='Leo', Saturn='Aries', Mars='Aries',
                   Jupiter='Cancer', Venus='Virgo', Mercury='Libra')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Gemini'
    rows = engine['evaluate_prosperity'](chart)
    assert [r['Class'] for r in rows if r['key'] == 'injustice'] == [engine['PROSPERITY_CLASSES']['injustice']]
    assert all((r['key'] == 'middling supplement') == r['Supplement'] for r in rows)
    # 2.17, 7: each of them is also listed as a fall, in the eleventh from the Lot.
    assert sorted(r['Ground'] for r in rows if r['key'] == 'falling') == ['Mars in the eleventh from the Lot of Fortune',
                                                                          'Saturn in the eleventh from the Lot of Fortune']


def test_by_sign_and_by_degree_are_their_own_rows_from_the_cusps(engine):
    """Diurnal, 20 Aries rising, the quadrant cusps every thirty degrees
    from it: the Sun at 10 Aries is the first by sign (a stake) but in the
    twelfth by the cusps -- 2.3, 17; Jupiter at 15 Taurus is the second by
    sign but in the first by the cusps -- 2.3, 18; Saturn, the partnering
    lord, at 15 Cancer is the fourth by sign and the third by the cusps --
    2.3, 17. A second measure, its own rows; the synthesis stays by whole
    sign and cites neither."""
    chart = _chart(engine, 'Diurnal', ('Aries', 20.0), Sun=('Aries', 10.0), Jupiter=('Taurus', 15.0), Saturn=('Cancer', 15.0),
                   Moon='Leo', Mars='Libra', Venus='Leo', Mercury=('Aries', 25.0))
    chart['houses'] = [(20.0 + 30.0 * i) % 360.0 for i in range(12)]
    key, rows = _verdict(engine, chart)
    assert key == 'high' and '2.3, 17' not in rows[0]['Sahl'] and '2.3, 18' not in rows[0]['Sahl']
    by_degree = [r for r in rows if r['key'] == 'by degree']
    assert [r['Class'] for r in by_degree] == ['By sign and by degree'] * 3
    assert by_degree[0]['Ground'].startswith('Sun in the 1st, a stake by sign, and falling from the stakes by degrees (the 12th by the quadrant cusps): reputation, but it corrupts assets') and '2.3, 17' in by_degree[0]['Sahl']
    assert by_degree[1]['Ground'].startswith('Jupiter in the 2nd, what follows a stake by sign, and in the stake by degrees (the 1st by the quadrant cusps): assets and a fine condition, without fame') and '2.3, 18' in by_degree[1]['Sahl']
    assert by_degree[2]['Ground'].startswith('Saturn in the 4th, a stake by sign, and falling from the stakes by degrees (the 3rd by the quadrant cusps)')
    assert all('it moves nothing' in r['Ground'] for r in by_degree)
    del chart['houses']
    assert not [r for r in engine['evaluate_prosperity'](chart) if r['key'] == 'by degree']


def test_the_lord_of_the_house_of_assets_falling_but_clean_is_a_middling_row(engine):
    """Diurnal, Aries rising: the house of assets is Taurus, its lady Venus
    in Virgo, the sixth, with Saturn in Libra and Mars in Leo neither with
    her nor in her square or opposition -- 2.11, 14, listed. Mars moved to
    Gemini squares her and the row goes."""
    chart = _chart(engine, 'Diurnal', 'Aries', Sun=('Aries', 10.0), Moon='Leo', Venus='Virgo', Saturn='Libra', Mars='Leo',
                   Jupiter='Sagittarius', Mercury='Aries')
    rows = engine['evaluate_prosperity'](chart)
    assets = [r for r in rows if r['key'] == 'assets']
    assert len(assets) == 1 and assets[0]['Class'] == 'The middle: the lord of the house of assets'
    assert assets[0]['Ground'].startswith('Venus, the lord of the house of assets (Taurus), in Virgo, the 6th, falling from the stakes, no infortune with it or in its square or opposition: what is middling of assets')
    assert 'fn 154 on 2.11, 13' in assets[0]['Ground'] and '2.11, 14' in assets[0]['Sahl']
    chart['planetary_data']['Mars']['longitude'] = 75.0
    assert not [r for r in engine['evaluate_prosperity'](chart) if r['key'] == 'assets']


def test_the_partnering_lord_under_the_rays_in_a_good_place_is_neither(engine):
    """Diurnal, Aries rising, the Sun at 10 Leo: the fire lords Sun, Jupiter,
    Saturn; Saturn at 5 Leo is burned in the fifth, what follows a stake --
    not a falling place, no strength (2.11, 5): 2.11, 4's support wants
    strength and its bringing down a falling place, so the row says
    neither. Jupiter in Sagittarius, the ninth, falls; the first lord the
    Sun in the fifth is strong."""
    chart = _chart(engine, 'Diurnal', 'Aries', Sun=('Leo', 10.0), Saturn=('Leo', 5.0), Jupiter='Sagittarius', Moon='Taurus',
                   Mars='Capricorn', Venus='Cancer', Mercury='Virgo')
    key, rows = _verdict(engine, chart)
    assert key == 'high to low'
    assert 'the first lord strong, the second weak -- Jupiter falling (2.11, 3)' in rows[0]['Ground']
    assert 'the Lot step (2.3, 6), Sun and Jupiter made unfortunate -- the either-lord entry being this app\'s reading of the sentence\'s singular: no Lot of Fortune in hand' in rows[0]['Ground']
    third = _row(rows, 'third')['Ground']
    assert third.startswith('Third: Saturn in Leo, the 5th, what follows a stake, under the rays (no strength, 2.11, 5)')
    assert "under the rays, no strength (2.11, 5): neither 2.11, 4's support, which wants strength, nor its bringing down, which wants a falling place" in third
    assert 'Modified by the partnering lord (2.11, 4): Saturn in Leo, the 5th, what follows a stake -- under the rays, no strength (2.11, 5): neither' in rows[0]['Ground']


def test_the_lot_rows_say_when_the_turn_to_the_lot_is_not_met(engine):
    """Figure 13 with its Lot computed: neither lord weak nor with an
    infortune on it, so 2.3, 6's turn to the Lot is not made; the Lot in
    Libra, its lady Venus in the eleventh not looking at it (2.3, 9), is
    still listed, and the row says the turn is not met. The synthesis
    carries no Lot step."""
    chart = _chart(engine, 'Diurnal', 'Cancer', lot=True, Sun='Aries', Mercury='Aries', Jupiter='Cancer',
                   Moon='Cancer', Saturn='Pisces', Venus='Taurus', Mars='Scorpio')
    key, rows = _verdict(engine, chart)
    assert key == 'high' and 'the Lot step' not in rows[0]['Ground'] and '2.3, 6' not in rows[0]['Sahl']
    lot_rows = [r for r in rows if r['key'].startswith('lot ')]
    assert len(lot_rows) == 1 and '2.3, 9' in lot_rows[0]['Sahl']
    assert lot_rows[0]['Ground'].startswith('the lord of the Lot not looking at the Lot, in the 11th')
    assert lot_rows[0]['Ground'].endswith("; listed: 2.3, 6's turn to the Lot is not met, neither lord being made unfortunate")


def test_the_lot_s_own_sentences_at_two_levels_are_unresolved(engine):
    """Diurnal, Aries rising, the Sun at 10 Leo (the fifth, strong), Jupiter
    in Sagittarius (the ninth, falling): the Lot (the Moon at 10 Capricorn)
    at 0 Virgo, the sixth; its lord Mercury in Leo, the fifth, not looking
    at it -- 2.3, 9, happy; Jupiter (Sagittarius, square), Venus (Cancer,
    sextile), Saturn (Gemini, square) and Mars (Capricorn, trine) all
    looking at Virgo -- 2.16, 4, the middle. Two levels from the Lot's own
    sentences, beside the mixed pair: unresolved, no order installed."""
    chart = _chart(engine, 'Diurnal', 'Aries', lot=True, Sun=('Leo', 10.0), Moon=('Capricorn', 10.0), Jupiter='Sagittarius',
                   Saturn='Gemini', Mars='Capricorn', Venus='Cancer', Mercury='Leo')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Virgo'
    key, rows = _verdict(engine, chart)
    assert key == 'unresolved' and isinstance(rows[0]['Class'], engine['UnresolvedResult'])
    assert sorted(r['key'] for r in rows if r['key'].startswith('lot ')) == ['lot high', 'lot middling']
    assert ("Synthesis: the Lot's own sentences disagree -- the Lot's lord promises happiness (2.3, 9); the Lot indicates "
            "middling livelihood (2.16, 4) -- and the two triplicity lords indicate benefit in the first lord's time and "
            "hardship in the second's (2.11, 2) -- unresolved: this app installs no priority among the Lot's sentences nor "
            "between them and Theophilus's, Sahl giving none; every judgment stands") in rows[0]['Ground']
    assert all(engine['PROSPERITY_SAHL'][r] in rows[0]['Sahl'] for r in ('2.3, 9', '2.16, 4', '2.11, 2', '2.3, 6'))


def test_misery_beside_the_mixed_pair_is_a_conflict_not_a_mixture(engine):
    """Diurnal, Cancer rising, the Sun at 10 Aries (the tenth, strong),
    Jupiter in Gemini (the twelfth, falling, Saturn in Virgo square him):
    the Lot (the Moon at 10 Virgo) at 0 Sagittarius, the sixth, with Mars
    by day, its lord Jupiter made unfortunate -- 2.20, 1. Lifelong misery
    admits no time of benefit, so beside 2.11, 2's pattern it is
    unresolved, not mixed (2.16, 5 licenses variation within middling;
    nothing licenses a benefit period within 2.20's misery). Jupiter moved
    to Libra with Saturn in Capricorn (both lords strong, Jupiter squared)
    is the same conflict against 2.11, 1."""
    chart = _chart(engine, 'Diurnal', 'Cancer', lot=True, Sun=('Aries', 10.0), Moon=('Virgo', 10.0), Jupiter='Gemini',
                   Saturn='Virgo', Mars='Sagittarius', Venus='Taurus', Mercury='Aries')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Sagittarius'
    key, rows = _verdict(engine, chart)
    assert key == 'unresolved' and isinstance(rows[0]['Class'], engine['UnresolvedResult'])
    assert [r['key'] for r in rows if r['key'].startswith('lot ')] == ['lot low']
    assert ("Synthesis: conflicting status indications -- the Lot indicates misery from birth to death (2.20, 1); the two "
            "triplicity lords indicate benefit in the first lord's time and hardship in the second's (2.11, 2) -- unresolved: "
            "this app installs no priority between them") in rows[0]['Ground']
    assert all('mixed' not in str(value) and "'s pattern by the lords" not in str(value)
               for _name, value in rows[0]['Class'].alternatives)
    assert engine['PROSPERITY_SAHL']['2.20, 1'] in rows[0]['Sahl'] and engine['PROSPERITY_SAHL']['2.11, 2'] in rows[0]['Sahl']
    chart['planetary_data']['Jupiter']['longitude'], chart['planetary_data']['Saturn']['longitude'] = 180.0, 270.0
    key2, rows2 = _verdict(engine, chart)
    assert key2 == 'unresolved'
    assert ("conflicting status indications -- the Lot indicates misery from birth to death (2.20, 1); the two strong "
            "triplicity lords indicate high rank from the beginning of his life to its end (2.11, 1) -- unresolved") in rows2[0]['Ground']


def test_the_chart_page_renders_the_finding_with_its_four_columns():
    from conftest import make_app, assert_no_exception, table_inventory
    at = make_app(page="findings").run()
    assert_no_exception(at, "findings")
    assert ("Sahl: indications of fortune and livelihood", COLUMNS) in table_inventory(at)
