"""Fortune and livelihood: Sahl's seven classes (On Nativities Ch. 2), the
classifier's spine from Theophilus's paragraph (2.11, 1-5), the Lot of
Fortune when both lords fall (2.3, 6-9; 2.16; 2.20). Fixtures: Abu 'Ali's
twelve worked charts (PN I, JN Ch. 7, Figures 10-21), each hand-built by
sign -- 0 degrees of the sign unless the text gives a degree, the
Ascendant's sign as given, the sect as the delineation reads it -- and
held to the class Abu 'Ali states. Where his verdict rests on a reading
the printed positions do not support by whole sign, Dykes's own footnote
says so and the case is xfail(strict) with his words.

Note on the sign-only charts: every planet at 0 degrees puts a planet in
the Sun's sign in his heart (16'), which is strength, not burning, so no
sign-only chart reads a lord "under the rays" (2.11, 5); the degree
charts do (Figure 19's Mars, 4 degrees from the Sun).
"""
import re
from pathlib import Path

import pytest

CORPUS = Path("/home/apothic/Desktop/Fifty Aphorism OCR Project/consolidated_texts_final/on_nativities.md")
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
    assert len(sentences) == 44
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

def _chart(engine, sect, asc, **positions):
    S = {s: i * 30.0 for i, s in enumerate(engine['SIGN_ORDER'])}
    natal = {}
    for planet, where in positions.items():
        sign, deg = (where, 0.0) if isinstance(where, str) else where
        natal[planet] = {'longitude': S[sign] + deg, 'latitude': 0.0, 'distance': 1.0}
    asc_lon = S[asc[0]] + asc[1] if isinstance(asc, tuple) else S[asc]
    lot = engine['lot_by_id']('fortune', natal, asc_lon, None, sect)
    return {'planetary_data': natal, 'ascendant': asc_lon, 'sect': sect, 'lot_of_fortune': lot}


def _verdict(engine, chart):
    rows = engine['evaluate_prosperity'](chart)
    assert rows and all(list(r)[:4] == COLUMNS for r in rows)
    assert rows[0]['Class'] == engine['PROSPERITY_CLASSES'][rows[0]['key']]
    return rows[0]['key'], rows


def test_example_1_figure_10_a_pauper(engine):
    """Nocturnal, Gemini ascending: the Moon in Scorpio, her lords Mars
    (Aquarius, the ninth) and Venus (Leo, the third), "both cadent from the
    angles -- which were signifying poverty and the bad condition of the
    native. Wherefore this native was even a pauper"."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Gemini', Sun='Leo', Venus='Leo', Saturn='Scorpio',
                                        Moon='Scorpio', Mars='Aquarius', Jupiter='Taurus', Mercury='Virgo'))
    assert key == 'low'
    assert '2.11, 3' in rows[0]['Sahl'] and 'both lords falling' in rows[0]['Ground']
    assert not any(r['key'].startswith('lot ') for r in rows)          # the Lot neither raises nor gives the middle


def test_example_2_figure_11_a_most_elegant_affair(engine):
    """Diurnal by the delineation (the figure's caption says nocturnal; the
    text reads the Sun's lords and the Sun stands in the eleventh): Saturn
    in Scorpio, the eighth, Mercury in Aquarius, the eleventh, "both in
    succeedents of the angles ... signifying prosperity and riches"."""
    key, rows = _verdict(engine, _chart(engine, 'Diurnal', 'Aries', Sun='Aquarius', Mercury='Aquarius', Moon='Sagittarius',
                                        Saturn='Scorpio', Mars='Scorpio', Jupiter='Cancer', Venus='Capricorn'))
    assert key == 'high'
    # after the check: 2.3, 18 is a sign-against-degree rule; the JN charts carry no
    # degrees, so the succedent grade rests on 2.11, 1-2 alone and says so
    assert '2.11, 2' in rows[0]['Sahl'] and "2.3, 18's degree condition not met" in rows[0]['Ground']
    assert 'infortunes on it, not judged: Saturn by square, Mars by square' in rows[0]['Ground']


def test_example_3_figure_12_great_and_eminent(engine):
    """Nocturnal, Scorpio ascending: Mars (Aquarius, the fourth), Venus
    (Taurus, the seventh), the Moon (Scorpio, the first), "all in angles --
    which signified prosperity, loftiness and a kingdom". Saturn in the
    eleventh is listed under it (2.3, 12; 2.17, 7) and does not move it."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Scorpio', Moon='Scorpio', Sun='Aries', Mars='Aquarius',
                                        Venus='Taurus', Mercury='Pisces', Jupiter='Virgo', Saturn='Virgo'))
    assert key == 'high'
    assert '2.3, 2' in rows[0]['Sahl'] and 'both in the stakes' in rows[0]['Ground']
    falls = [r for r in rows if r['key'] == 'falling']
    assert any('Saturn in the eleventh from the Ascendant' == r['Ground'] for r in falls)
    assert any(r['Ground'].startswith('Saturn in the eleventh: takes away') for r in rows if r['key'] == 'eleventh')


def test_example_4_figure_13_honored_among_kings(engine):
    """Diurnal, Cancer ascending: the Sun (Aries, the tenth) and Jupiter
    (Cancer, the first), "both in angles and their own exaltations"; Saturn
    the third lord "cadent from an angle in a domicile of Jupiter"."""
    key, rows = _verdict(engine, _chart(engine, 'Diurnal', 'Cancer', Sun='Aries', Mercury='Aries', Jupiter='Cancer',
                                        Moon='Cancer', Saturn='Pisces', Venus='Taurus', Mars='Scorpio'))
    assert key == 'high'
    third = next(r for r in rows if r['key'] == 'third')
    assert third['Ground'].startswith('Third: Saturn in Pisces, the 9th, falling from the stakes') and 'brings them down' in third['Ground']


@pytest.mark.xfail(strict=True, reason='Dykes, PN I fn 51 to Figure 14: "Note that while the text puts Jupiter in Gemini, that is not a '
                                        'succeedent place (nor is Scorpio cadent here). Dorotheus puts Jupiter and the Moon in Libra, which is '
                                        'angular, while Masha\'allah puts them both in Virgo, which is cadent." By whole sign Mercury and Saturn '
                                        'stand in the fifth, what follows a stake, and the class is the first, not the middling life he states.')
def test_example_5_figure_14_a_middling_life(engine):
    key, _rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Cancer', Jupiter='Gemini', Moon='Gemini', Saturn='Scorpio',
                                         Sun='Scorpio', Mercury='Scorpio', Mars='Virgo', Venus='Virgo'))
    assert key == 'middling'


@pytest.mark.xfail(strict=True, reason='Dykes, PN I fn 52 to Figure 15: "the positions do not match the delineation, as the Sun is in a '
                                        'watery sign, not a fiery one. Dorotheus has the Sun and Jupiter switching places ... Dorotheus\'s '
                                        'delineation is the only one that makes sense". By whole sign the Sun in Pisces has Venus (the twelfth) '
                                        'and Mars (the fourth) for lords: the fifth class, not the first he states.')
def test_example_6_figure_15_lofty_and_wealthy(engine):
    key, _rows = _verdict(engine, _chart(engine, 'Diurnal', 'Gemini', Sun='Pisces', Saturn='Pisces', Moon='Pisces',
                                         Mercury='Aries', Jupiter='Aries', Mars='Virgo', Venus='Taurus'))
    assert key == 'high'


@pytest.mark.xfail(strict=True, reason='Dykes, PN I fn 53 to Figure 16: "Also, Saturn is not cadent." Abu \'Ali reads Saturn (Taurus, the '
                                        'seventh) as cadent and "each was the detriment of the other"; by whole sign Saturn and Mercury both stand '
                                        'in the stakes and the class is the first, with Mars in the eleventh from the Ascendant listed as a fall.')
def test_example_7_figure_16_labor_and_scarcity(engine):
    key, _rows = _verdict(engine, _chart(engine, 'Diurnal', ('Scorpio', 0.0), Jupiter=('Libra', 21.2), Sun=('Libra', 8.0),
                                         Mercury=('Scorpio', 11.25), Saturn=('Taurus', 15.0), Moon=('Leo', 26.0), Mars=('Virgo', 18.0)))
    assert key == 'low'


def test_example_8_figure_17_poor_fortune(engine):
    """Nocturnal, Virgo ascending: the Moon in Gemini, Mercury and Saturn
    both in Aquarius, the sixth, "both cadent, who were signifying poverty
    and the bad condition of this native"."""
    key, rows = _verdict(engine, _chart(engine, 'Nocturnal', 'Virgo', Moon='Gemini', Saturn='Aquarius', Sun='Aquarius',
                                        Mercury='Aquarius', Mars='Capricorn', Venus='Sagittarius', Jupiter='Virgo'))
    assert key == 'low'
    assert not any(r['key'].startswith('lot ') for r in rows)


@pytest.mark.xfail(strict=True, reason='Dykes, PN I fn 56 to Figure 18: "The delineation text states that both Jupiter and the Sun are '
                                        'cadent \\"in the sign of the 6th,\\" but both Masha\'allah\'s and Abu \'Ali\'s charts have the Sun in '
                                        'the seventh sign. Because Masha\'allah\'s chart has a much later Ascendant degree, his Sun is cadent by '
                                        'standard quadrant houses." By whole sign the Sun, the second lord, stands in the seventh and the class '
                                        'is the fifth (2.11, 2), not the labor and want he states.')
def test_example_9_figure_18_labor_and_want(engine):
    key, _rows = _verdict(engine, _chart(engine, 'Nocturnal', ('Gemini', 16.0), Moon=('Aries', 16.0), Jupiter=('Scorpio', 22.0),
                                         Venus=('Scorpio', 13.0), Saturn=('Pisces', 15.0), Mercury=('Scorpio', 21.0),
                                         Sun=('Sagittarius', 9.0), Mars=('Sagittarius', 19.0)))
    assert key == 'low'


def test_example_10_figure_19_prosperity_after_labor(engine):
    """Nocturnal, 21 Taurus ascending: the Moon in Pisces; Mars "under the
    rays of the Sun, in the square aspect of Saturn -- which signified the
    native's labor and anxiety in the first third of his life"; Venus "in
    an angle, oriental ... signifying prosperity and the native's good
    condition after labor". The Lot at 7 Sagittarius as the text has it."""
    chart = _chart(engine, 'Nocturnal', ('Taurus', 21.0), Moon=('Pisces', 1.0), Sun=('Virgo', 17.0), Saturn=('Sagittarius', 14.0),
                   Jupiter=('Libra', 17.0), Mars=('Virgo', 21.0), Venus=('Leo', 17.0), Mercury=('Libra', 5.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Sagittarius' and abs(chart['lot_of_fortune'] % 30 - 7.0) < 1e-9
    key, rows = _verdict(engine, chart)
    assert key == 'low to high'
    assert 'Mars in Virgo, the 5th, what follows a stake, under the rays (no strength, 2.11, 5)' in rows[0]['Ground']
    assert 'Saturn by square' in rows[0]['Ground'] and '2.11, 2' in rows[0]['Sahl'] and '2.13, 39' in rows[0]['Sahl']


@pytest.mark.xfail(strict=True, reason='Abu \'Ali\'s rise at Figure 20 rests on the Moon, "the luminary of the time ... in the Midheaven, '
                                        '[and] she [was] also the last Lady of the triplicity; and the Lot of Fortune of the nature of Venus", '
                                        'neither a rule Sahl states (2.11, 4 makes the partnering lord a support, not a class); his own rule '
                                        'wants the Lot "conjoined to Jupiter or Venus", and the Lot in Taurus has neither. Dykes, fn 60: '
                                        '"Errors in calculation must be Abu \'Ali\'s, as the positions in Nativities yield a correct Lot of '
                                        'Fortune." Both lords fall and the class is the sixth.')
def test_example_11_figure_20_good_condition_at_the_end(engine):
    key, _rows = _verdict(engine, _chart(engine, 'Nocturnal', ('Libra', 2.5), Moon=('Cancer', 5.07), Saturn=('Gemini', 2.0),
                                         Jupiter=('Sagittarius', 15.0), Sun=('Aquarius', 10.0), Mars=('Sagittarius', 15.0),
                                         Venus=('Pisces', 25.0), Mercury=('Aquarius', 15.0)))
    assert key == 'low to high'


@pytest.mark.xfail(strict=True, reason='Dykes, PN I fn 62 to Figure 21: "According to the positions given, this is not true (she is in the '
                                        'eleventh from the Lot). But the Lot cannot be in the given position anyway; it should rather be at 16° '
                                        'Capricorn, in which case the Moon would be in its Midheaven, but the Lot would no longer be joined to '
                                        'Jupiter." The Lot computed from his positions falls in Capricorn; the Sun (the tenth) is strong and '
                                        'Jupiter (the sixth) falls, so the class is the second (2.11, 2), not the fortune from the middle of life '
                                        'he states; his weakening of the Sun, "applying to Saturn, nor received by him", is listed and not judged.')
def test_example_12_figure_21_fortune_from_the_middle_of_life(engine):
    chart = _chart(engine, 'Diurnal', ('Cancer', 10.12), Sun=('Aries', 24.0), Moon=('Libra', 17.0), Saturn=('Libra', 27.0),
                   Jupiter=('Sagittarius', 17.0), Mars=('Sagittarius', 0.0))
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Capricorn'
    key, _rows = _verdict(engine, chart)
    assert key == 'low to high'


# --- the rules beyond the twelve ------------------------------------------

def test_the_lot_raises_two_falling_lords(engine):
    """Diurnal, Aries ascending, the Sun at 10 Gemini (the third): Saturn
    (Virgo, the sixth) and Mercury (25 Gemini, the third) both fall. The
    Lot (the Moon at 10 Sagittarius) falls at 0 Libra, the seventh; its
    lady Venus in Aries, the first, eastern of the Sun, looking at the Lot
    by opposition, no infortune on her; Jupiter in Aquarius looking at the
    Lot by sextile; Saturn and Mars (Scorpio) not looking at Libra -- 2.3, 7
    raises the class to the first. Mars moved to Cancer squares both the
    Lot and its lady: 2.3, 7 fails and 2.16, 2 gives the middle."""
    chart = _chart(engine, 'Diurnal', 'Aries', Sun=('Gemini', 10.0), Moon=('Sagittarius', 10.0), Saturn='Virgo',
                   Mercury=('Gemini', 25.0), Venus='Aries', Mars='Scorpio', Jupiter='Aquarius')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Libra'
    key, rows = _verdict(engine, chart)
    assert key == 'high'
    assert rows[0]['Ground'].startswith('both lords falling, the reading goes to the Lot of Fortune (2.3, 6)')
    assert '2.3, 7' in rows[0]['Sahl'] and rows[0]['Also'] == engine['PROSPERITY_ALSO']['lot']
    chart['planetary_data']['Mars']['longitude'] = 95.0
    key2, rows2 = _verdict(engine, chart)
    assert key2 == 'middling' and '2.16, 2' in rows2[0]['Sahl'] and not any(r['key'] == 'lot high' for r in rows2)
    assert 'Jupiter eastern looking at it from an excellent place' in rows2[0]['Ground']


def test_the_lot_gives_the_middle_when_all_four_look_at_it(engine):
    """Nocturnal, Aries ascending, the Moon in Gemini: Mercury (Virgo, the
    sixth) and Saturn (Sagittarius, the ninth) fall. The Lot in Leo (the
    Sun in Libra) has Jupiter with it, Venus by sextile from Libra, Saturn
    by trine, Mars by square from Scorpio -- 2.16, 4; its lord the Sun in
    the seventh is no one's east, so 2.3, 7 does not raise it."""
    chart = _chart(engine, 'Nocturnal', 'Aries', Moon='Gemini', Sun='Libra', Mercury='Virgo', Saturn='Sagittarius',
                   Jupiter='Leo', Venus='Libra', Mars='Scorpio')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Leo'
    key, rows = _verdict(engine, chart)
    assert key == 'middling' and '2.16, 4' in rows[0]['Sahl'] and '2.3, 6' in rows[0]['Sahl']
    assert rows[0]['Also'] == engine['PROSPERITY_ALSO']['middling']


def test_misery_confirmed_by_the_lot_in_the_sixth(engine):
    """Diurnal, Cancer ascending, the Sun at 10 Libra: Saturn (Gemini, the
    twelfth) falls and Mercury at 14 Libra is burned; both weak. The Lot
    (the Moon at 10 Pisces) falls at 0 Sagittarius, the sixth, with Mars;
    its lord Jupiter in Capricorn, his fall; Mars by day with the Lot --
    2.20, 1 confirms the sixth class."""
    chart = _chart(engine, 'Diurnal', 'Cancer', Sun=('Libra', 10.0), Moon=('Pisces', 10.0), Saturn='Gemini',
                   Mercury=('Libra', 14.0), Mars='Sagittarius', Jupiter='Capricorn', Venus='Virgo')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Sagittarius'
    key, rows = _verdict(engine, chart)
    assert key == 'low'
    assert 'Confirmed by the Lot' in rows[0]['Ground'] and 'its lord in its fall' in rows[0]['Ground'] and '2.20, 1' in rows[0]['Sahl']
    assert 'Mercury in Libra, the 4th, a stake, under the rays (no strength, 2.11, 5)' in rows[0]['Ground']


def test_the_fifteen_degrees_by_ascension_at_the_equator(engine):
    """Obliquity 0 at latitude 0: ascension is longitude, so the arc after
    the stake is the zodiacal distance. Diurnal, 0 Aries rising, MC at 0
    Capricorn (armc 270): the Sun at 10 Aries is 10 degrees after the
    Ascendant (the first 15); Jupiter at 20 Taurus is 50 after it (beyond
    45, of the nativities of the poor)."""
    chart = _chart(engine, 'Diurnal', 'Aries', Sun=('Aries', 10.0), Moon='Leo', Jupiter=('Taurus', 20.0), Saturn='Libra',
                   Mars='Leo', Venus='Leo', Mercury='Aries')
    chart.update({'armc': 270.0, 'obliquity': 0.0, 'geo_lat': 0.0, 'mc': 270.0})
    rows = engine['evaluate_prosperity'](chart)
    grades = [r for r in rows if r['key'] == 'ascensions']
    assert [g['Ground'].split(' -- ')[1].split('.')[0] for g in grades] == [
        'the first 15°: praise and good fortune', 'beyond 45°, up to the next stake: of the nativities of the poor']
    assert '10.0° of ascension after the Ascendant' in grades[0]['Ground'] and '2.13, 48' in grades[0]['Sahl']
    assert '2.13, 51' in grades[1]['Sahl']
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
    chart = with_speeds(_chart(engine, 'Diurnal', 'Aries', Sun=('Gemini', 5.0), Moon=('Aries', 12.0), Venus=('Leo', 10.0),
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
    chart = _chart(engine, 'Diurnal', 'Leo', Sun='Libra', Moon='Leo', Saturn='Aries', Mars='Aries',
                   Jupiter='Cancer', Venus='Virgo', Mercury='Libra')
    assert engine['get_zodiac_sign'](chart['lot_of_fortune']) == 'Gemini'
    rows = engine['evaluate_prosperity'](chart)
    assert [r['Class'] for r in rows if r['key'] == 'injustice'] == [engine['PROSPERITY_CLASSES']['injustice']]
    assert all((r['key'] == 'middling supplement') == r['Supplement'] for r in rows)
    # 2.17, 7: each of them is also listed as a fall, in the eleventh from the Lot.
    assert sorted(r['Ground'] for r in rows if r['key'] == 'falling') == ['Mars in the eleventh from the Lot of Fortune',
                                                                          'Saturn in the eleventh from the Lot of Fortune']


def test_the_chart_page_renders_the_finding_with_its_four_columns():
    from conftest import make_app, assert_no_exception, table_inventory
    at = make_app(page="findings").run()
    assert_no_exception(at, "findings")
    assert ("Fortune and livelihood: the seven classes (Sahl)", COLUMNS) in table_inventory(at)
