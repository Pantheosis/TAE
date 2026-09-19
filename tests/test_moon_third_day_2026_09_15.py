"""The Moon on the third day (Sahl, On Nativities 1.29, 11-12; 1.26, 7) and
the fetus's stay (1.8-1.9): two course-text, display-only findings. The
third-day Moon is the ephemeris Moon two days after the birth moment, the
birth day counted as the first (Firmicus, Mathesis II.29, 34);
hand-built cases hit 1.26, 7 met and not met; every quoted sentence is
verbatim in the corpus; the gestation rows carry their sentences."""
import re
from datetime import datetime
from pathlib import Path

import pytest
import swisseph as swe

from corpus_paths import corpus_file

CORPUS = corpus_file("on_nativities.md")
FLORENCE = (43.7792, 11.2463)


def _clean(text):
    text = re.sub(r"<sup>\d+</sup>", "", text)
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("*", "")


@pytest.fixture(scope="module")
def corpus():
    if not CORPUS.exists():
        pytest.skip("the corpus is not on this machine")
    return _clean(CORPUS.read_text(encoding="utf-8"))


def _chart(engine):
    return engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), *FLORENCE)


def test_third_day_moon_is_the_ephemeris_moon_two_days_on(engine):
    chart = _chart(engine)
    third = engine["third_day_positions"](chart['julian_day'])
    assert engine["MOON_THIRD_DAY_DAYS"] == 2.0
    jd3 = chart['julian_day'] + 2.0
    assert third['jd'] == jd3
    expected = swe.calc_ut(jd3, swe.MOON)[0][0] % 360.0
    assert abs(third['Moon'] - expected) < 1e-9
    assert abs(third['Sun'] - swe.calc_ut(jd3, swe.SUN)[0][0] % 360.0) < 1e-9
    rows = engine["evaluate_moon_third_day"](chart)
    assert [list(r) for r in rows] == [engine["MOON_THIRD_DAY_COLUMNS"]] * len(rows)
    first = rows[0]
    assert first['Item'] == 'The Moon on the third day'
    assert first['Value'].startswith(engine["get_degree_string"](expected))
    assert 'two days after the birth, the birth day counted as the first' in first['Value']
    # The finding names its two sentences and 1.26, 7.
    items = [r['Item'] for r in rows]
    assert any(i.startswith('1.29, 11') for i in items)
    assert any(i.startswith('1.29, 12') for i in items)
    assert any(i.startswith('1.26, 7') for i in items)


def _rows_for(engine, moon, sun=300.0, saturn=290.0, mars=250.0, natal_saturn=290.0, natal_mars=250.0, asc=95.0):
    positions = {
        'Sun': (sun, 1.0), 'Moon': (moon, 13.0), 'Mercury': (25.0, 1.2),
        'Venus': (55.0, 1.1), 'Mars': (mars, 0.7), 'Jupiter': (265.0, 0.08),
        'Saturn': (saturn, 0.03),
    }
    planetary_data = {
        name: {'longitude': lon, 'latitude': 0.0, 'distance': 1.0,
               'speed_in_lon': speed, 'speed_in_lat': 0.0, 'speed_in_dist': 0.0}
        for name, (lon, speed) in positions.items()
    }
    third = {'planetary_data': planetary_data,
             **{name: row['longitude'] for name, row in planetary_data.items()}}
    return engine["moon_third_day_rows"](third, {'Saturn': natal_saturn, 'Mars': natal_mars}, asc)


def _row(rows, prefix):
    hits = [r for r in rows if r['Item'].startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_four_footed_and_afflicted_meets_1_26_7(engine):
    """The Moon at 10 Leo, Mars at 5 Scorpio (a whole-sign square), the Sun
    far off, the Ascendant in Cancer so Leo is the second place -- not
    falling. 1.26, 7 met; corrupted by the infortune looking alone."""
    rows = _rows_for(engine, moon=130.0, mars=215.0, saturn=290.0, asc=95.0)
    assert _row(rows, 'A sign having four feet')['Value'] == 'Yes: Leo, whole'
    looking = _row(rows, 'The infortunes looking')['Value']
    assert looking.startswith('Yes: Mars by square from Scorpio')
    assert 'Saturn' not in looking.split('(')[0]
    assert _row(rows, 'Burning')['Value'].startswith('No')
    assert _row(rows, 'Falling')['Value'].startswith('No: the 2nd place')
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == (
        'Corruption found in these checks: infortune relation (Mars by square from Scorpio)')
    assert _row(rows, '1.26, 7')['Value'].startswith('Met: a sign having four feet, and Mars by square from Scorpio')
    assert _row(rows, '1.29, 11')['Value'].startswith('Third-day component does not hold')
    # 1.29, 12's first clause: the natal infortunes are in the 8th and 6th, not the 1st or 7th.
    twelve = _row(rows, '1.29, 12')['Value']
    assert twelve.startswith('Not met: the two infortunes are not both in the Ascendant or seventh')
    # Move the natal infortunes into the Ascendant and the seventh: met, since the third day is corrupted.
    rows2 = _rows_for(engine, moon=130.0, mars=215.0, saturn=290.0, natal_saturn=100.0, natal_mars=280.0, asc=95.0)
    assert _row(rows2, '1.29, 12')['Value'].startswith("The first clause's two components hold")


def test_not_four_footed_and_clean_is_not_corrupted(engine):
    """The Moon at 10 Virgo, both infortunes in aversion (Aquarius, Aries),
    the Sun far off, the Ascendant in Cancer so Virgo is the third place --
    falling, so 1.29, 3's third corruption holds while 1.26, 7 does not.
    Then the Ascendant in Leo: the second place, nothing corrupts her."""
    rows = _rows_for(engine, moon=160.0, saturn=310.0, mars=10.0, sun=300.0, asc=95.0)
    assert _row(rows, 'A sign having four feet')['Value'].startswith("No: Virgo")
    assert _row(rows, 'The infortunes looking')['Value'].startswith('No intersign look: Saturn in Aquarius and Mars in Aries')
    assert _row(rows, 'Falling')['Value'].startswith('Yes: the 3rd place')
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == 'Corruption found in these checks: falling'
    assert _row(rows, '1.26, 7')['Value'] == 'Not met: the sign has no four feet'
    clean = _rows_for(engine, moon=160.0, saturn=310.0, mars=10.0, sun=300.0, asc=125.0)
    assert _row(clean, 'Falling')['Value'] == 'No: the 2nd place from the Ascendant of the nativity'
    assert _row(clean, 'Third-day Moon: corruption checks')['Value'] == 'No corruption found in these checks'
    assert _row(clean, '1.29, 11')['Value'].startswith('Third-day component holds')
    # Burned: the Sun 8 degrees off.
    burned = _rows_for(engine, moon=160.0, saturn=310.0, mars=10.0, sun=168.0, asc=125.0)
    assert _row(burned, 'Burning')['Value'].startswith('Yes: 8.0° from the Sun')
    assert _row(burned, 'Third-day Moon: corruption checks')['Value'] == 'Corruption found in these checks: burned'


def test_four_footed_signs_follow_1_38_1(engine):
    f = engine["sign_has_four_feet"]
    assert f(10.0) == 'whole' and f(40.0) == 'whole' and f(130.0) == 'whole'
    assert f(250.0) is None and f(255.0) == 'the second half' and f(244.99) is None
    assert f(160.0) is None and f(280.0) is None


def test_quotations_are_verbatim_in_the_corpus(engine, corpus):
    for name in ('SAHL_1_29_3', 'SAHL_1_29_11', 'SAHL_1_29_12', 'SAHL_1_29_13', 'SAHL_1_29_FN303', 'SAHL_1_29_FN304',
                 'SAHL_1_26_7', 'SAHL_1_38_1', 'SAHL_9_3', 'SAHL_1_30_22',
                 'SAHL_1_8_1', 'SAHL_1_8_3', 'SAHL_1_8_4', 'SAHL_1_8_5', 'SAHL_1_8_6', 'SAHL_1_8_FN38', 'SAHL_1_8_FN40',
                 'SAHL_1_8_COMMENT', 'SAHL_1_9_1', 'SAHL_1_9_FN45', 'SAHL_1_9_11', 'SAHL_1_9_12', 'SAHL_1_9_13',
                 'SAHL_1_9_14', 'SAHL_1_9_FN47', 'SAHL_1_9_FN49', 'SAHL_1_9_FN51', 'SAHL_1_9_FN53', 'SAHL_1_9_FN54',
                 'SAHL_1_9_FN55'):
        assert engine[name] in corpus, name
    rules = engine["SAHL_1_9_RULES"]
    assert [n for n, _ in rules] == list(range(2, 11))
    for n, text in rules:
        assert text in corpus, f"1.9, {n}"


def test_gestation_rows_carry_the_sentences(engine):
    chart = _chart(engine)
    rows = engine["evaluate_gestation"](chart)
    assert rows and all(list(r) == engine["GESTATION_COLUMNS"] for r in rows)
    by = {r['Item']: r for r in rows}
    meeting = by['The meeting before the birth (1.8, 5)']
    assert engine["SAHL_1_8_5"] in meeting['Text']
    lun = engine["sahl_prenatal_meeting_and_fullness"](chart['julian_day'], *FLORENCE)
    assert engine["get_degree_string"](lun['meeting']['longitude']) in meeting['Value']
    asc_row = by['The Ascendant of the meeting (1.8, 6)']
    assert engine["SAHL_1_8_6"] in asc_row['Text']
    asc_at_meeting = swe.houses(lun['meeting']['jd'], *FLORENCE, b'B')[1][0]
    assert asc_row['Value'].startswith(engine["get_degree_string"](asc_at_meeting))
    divisions = by['The three divisions (1.8, 3-4) and their reading (1.8, 7-13)']
    assert divisions['Value'].startswith(engine["GESTATION_NOT_COMPUTED"])
    assert engine["SAHL_1_8_3"] in divisions['Text'] and engine["SAHL_1_8_FN38"] in divisions['Text']
    # 1.9: the three Moons, then a sentence row or the no-sentence row, then 11 and 12-13.
    moons = engine["gestation_moons"](chart['julian_day'])
    assert abs(moons['natal']['longitude'] - chart['planetary_data']['Moon']['longitude']) < 1e-9
    # The calendar anniversary at the birth hour (Julian calendar; 1240 is a leap year, so 366 days back, 365 on).
    y, m, d, h = swe.revjul(chart['julian_day'], swe.JUL_CAL)
    assert abs(moons['past']['jd'] - swe.julday(y - 1, m, d, h, swe.JUL_CAL)) < 1e-9
    assert abs(moons['renewed']['jd'] - swe.julday(y + 1, m, d, h, swe.JUL_CAL)) < 1e-9
    assert abs(moons['past']['jd'] - (chart['julian_day'] - 366.0)) < 1e-9
    assert abs(moons['renewed']['jd'] - (chart['julian_day'] + 365.0)) < 1e-9
    assert abs(moons['past']['longitude'] - swe.calc_ut(moons['past']['jd'], swe.MOON)[0][0]) < 1e-9
    assert engine["SAHL_1_9_1"] in by['The Moon of the nativity (1.9, 1)']['Text']
    assert engine["get_degree_string"](moons['past']['longitude']) in by['The past Moon, a year before (1.9, 1)']['Value']
    assert engine["get_degree_string"](moons['renewed']['longitude']) in by['The renewed Moon, a year after (1.9, 1)']['Value']
    sentence_rows = [r for r in rows if re.fullmatch(r'1\.9, (\d+|2-10)', r['Item'])]
    assert sentence_rows
    for r in sentence_rows:
        if r['Item'] != '1.9, 2-10':
            n = int(r['Item'].split(', ')[1])
            assert dict(engine["SAHL_1_9_RULES"])[n] in r['Text']
    assert by['1.9, 11, the meeting of the conception']['Value'].startswith(engine["GESTATION_NOT_COMPUTED"])
    assert engine["SAHL_1_9_11"] in by['1.9, 11, the meeting of the conception']['Text']
    assert engine["SAHL_1_9_12"] in by['1.9, 12-13, the three stays']['Text']


def test_1_9_cases_as_written(engine):
    """Whole-sign aspects to the Moon of the nativity at 10 Gemini (the
    Ascendant in Libra): every sentence of 2-10 hit once, and the sextile
    named by none."""
    f = engine["gestation_1_9_rows"]
    natal, asc = 70.0, 190.0
    def hit(past, renewed, want):
        rows = f(natal, past, renewed, asc)
        got = [r['Item'] for r in rows if re.fullmatch(r'1\.9, (\d+|2-10)', r['Item'])]
        assert got == want, (past, renewed, got)
        return rows
    hit(190.0, 310.0, ['1.9, 2'])          # both trine
    hit(160.0, 340.0, ['1.9, 3'])          # both square
    hit(190.0, 340.0, ['1.9, 4'])          # past trine, renewed square
    hit(340.0, 190.0, ['1.9, 4'])          # reversed
    hit(160.0, 100.0, ['1.9, 5'])          # past square, renewed in aversion (Cancer)
    hit(250.0, 100.0, ['1.9, 6'])          # past opposed, renewed averse
    hit(100.0, 220.0, ['1.9, 7'])          # both averse (Cancer, Scorpio)
    hit(250.0, 250.0, ['1.9, 8'])          # both in the seventh
    hit(250.0, 310.0, ['1.9, 9'])          # past seventh, renewed trine of the Moon
    rows = hit(250.0, 75.0, ['1.9, 9'])    # past seventh, renewed in her own sign but in the trine of the Ascendant
    assert 'from the trine of the Ascendant (Libra)' in [r for r in rows if r['Item'].startswith('The renewed Moon')][0]['Value']
    hit(190.0, 250.0, ['1.9, 10'])         # past trine, renewed opposite
    hit(160.0, 250.0, ['1.9, 10'])         # past square, renewed opposite
    rows = hit(10.0, 310.0, ['1.9, 2-10']) # a sextile: no sentence names it
    assert rows[-3]['Value'].startswith('No sentence names this pair: the past Moon from the sextile')
