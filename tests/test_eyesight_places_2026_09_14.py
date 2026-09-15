"""Places harming the eyesight (Sahl, On Nativities 6.2, 48-75; Gr. Intr.
VI.20): the transcribed spans pinned row by row so a later reader can diff
them against the text; the evaluator on hand-built charts; the calculated
chart runs."""
from __future__ import annotations

from datetime import datetime

import pytest

from test_doctrine_fixtures import pdata

SAHL = 'Sahl, On Nativities 6.2'
ABU = 'Gr. Intr. VI.20'

# (source, sign, lo, hi, closed, sentence) -- lo/hi are degrees within the
# sign; half-open unless closed. Ordinal degrees are read as the app reads
# Figure 57: "the ninth" is 8.0-9.0.
EXPECTED = [
    (SAHL, 'Leo', 15.0, 18.0, False, 49),            # "passed half ... until she completes 18°"
    (SAHL, 'Scorpio', 7.0, 10.0, False, 50),          # eighth, ninth, tenth
    (SAHL, 'Scorpio', 22.0, 23.0, False, 50),         # "(and in 23)"
    (SAHL, 'Sagittarius', 5.0, 9.0, False, 51),       # from 6° to 9°
    (SAHL, 'Aquarius', 9.0, 10.0, False, 52),         # the tenth
    (SAHL, 'Aquarius', 17.0, 19.0, False, 52),        # eighteenth, nineteenth
    (SAHL, 'Capricorn', 25.0, 29.0, False, 53),       # from 26° to 29°
    (SAHL, 'Taurus', 5.0, 10.0, False, 54),           # from 6° to 10°
    (SAHL, 'Cancer', 8.0, 15.0, False, 55),           # ninth to fifteenth
    (SAHL, 'Leo', 17.0, 19.0, False, 61),             # Rhetorius: 18°, 19°
    (SAHL, 'Leo', 27.0, 28.0, False, 61),             # 28°
    (SAHL, 'Scorpio', 18.0, 19.0, False, 62),
    (SAHL, 'Scorpio', 28.0, 29.0, False, 62),
    (SAHL, 'Sagittarius', 0.0, 1.0, False, 63),
    (SAHL, 'Sagittarius', 6.0, 8.0, False, 63),
    (SAHL, 'Sagittarius', 17.0, 19.0, False, 63),
    (SAHL, 'Taurus', 5.0, 8.0, False, 64),
    (SAHL, 'Taurus', 9.0, 10.0, False, 64),
    (SAHL, 'Cancer', 8.0, 15.0, False, 65),
    (SAHL, 'Capricorn', 25.0, 29.0, False, 66),
    (SAHL, 'Aquarius', 9.0, 10.0, False, 67),
    (SAHL, 'Aquarius', 11.0, 12.0, False, 67),
    (SAHL, 'Aquarius', 18.0, 19.0, False, 67),
    (SAHL, 'Libra', 5.0, 8.0, False, 68),
    (SAHL, 'Libra', 9.0, 10.0, False, 68),
    (SAHL, 'Libra', 27.6, 28.0, True, 70),            # the Bizidaj: 27° 36' to 28°
    (SAHL, 'Sagittarius', 0.0, 1.0, False, 71),
    (SAHL, 'Scorpio', 8.0, 10.0, False, 71),
    (SAHL, 'Cancer', 14.0, 19.0, False, 72),          # from 15° to 19°
    (SAHL, 'Taurus', 14.0, 16.0, False, 74),          # Nawbakht: "the middle of Taurus"
    (SAHL, 'Cancer', 8.0, 9.0, False, 74),
    (SAHL, 'Sagittarius', 0.0, 1.0, False, 74),
    (ABU, 'Taurus', 13.6, 14.5, True, 4),             # 13° 36' to 14° 30'
    (ABU, 'Cancer', 21.0, 22.0, False, 5),            # 21° 08'
    (ABU, 'Scorpio', 20.0, 21.0, False, 6),           # 20°
    (ABU, 'Scorpio', 21.0, 22.0, False, 6),           # 21° 10'
    (ABU, 'Sagittarius', 15.0, 16.0, False, 7),       # 15° 20'
    (ABU, 'Capricorn', 22.0, 23.0, False, 8),         # 22°
    (ABU, 'Aquarius', 20.0 + 10.0 / 60.0, 24.0 + 20.0 / 60.0, True, 9),  # 20° 10' to 24° 20'
]


def test_every_span_is_pinned(engine):
    rows = engine["EYESIGHT_PLACES"]
    got = [(r['source'], r['sign'], r['lo'], r['hi'], r['closed'], r['sentence']) for r in rows]
    assert got == EXPECTED
    for r in rows:
        assert r['printed'] and r['place'] and r['quote'].startswith('"') and r['reading']
        assert r['source'] in (SAHL, ABU)


def test_moon_in_the_pleiades_span_returns_the_rows(engine):
    # 7 Taurus: inside Sahl 54 (6°-10°) and Rhetorius 64 (sixth-eighth); not Abu Ma'shar's 13°36'-14°30'.
    rows = engine["evaluate_eyesight_places"](pdata(Sun=200.0, Moon=37.0), 130.0)
    assert [r['Point'] for r in rows] == ['Moon', 'Moon']
    assert [r['Source'] for r in rows] == [f'{SAHL}, 54', f'{SAHL}, 64']
    assert list(rows[0]) == ['Point', 'Position', 'Place', 'Source', 'Text']
    assert 'the Pleiades' in rows[0]['Place'] and rows[0]['Text'].startswith('54: "And in Taurus from 6° to 10°')
    assert 'Rule -- 48:' in rows[0]['Text']


def test_moon_outside_every_span_returns_nothing(engine):
    assert engine["evaluate_eyesight_places"](pdata(Sun=200.0, Moon=55.0), 130.0) == []


def test_ordinal_spans_are_half_open_and_measured_spans_closed(engine):
    f = engine["evaluate_eyesight_places"]
    assert [r['Source'] for r in f(pdata(Sun=0.0, Moon=90.0 + 8.0), 130.0)] == [f'{SAHL}, 55', f'{SAHL}, 65', f'{SAHL}, 74']
    assert f(pdata(Sun=0.0, Moon=90.0 + 15.0), 130.0)[0]['Source'] == f'{SAHL}, 72'   # 15.0 is out of "ninth to fifteenth", in "15° to 19°"
    assert [r['Source'] for r in f(pdata(Sun=0.0, Moon=180.0 + 28.0), 130.0)] == [f'{SAHL}, 70']   # closed at 28°00'
    assert f(pdata(Sun=0.0, Moon=180.0 + 28.01), 130.0) == []
    assert [r['Source'] for r in f(pdata(Sun=30.0 + 14.5, Moon=0.0), 130.0)] == [f'{SAHL}, 74', f'{ABU}, 4']


def test_ascendant_and_sun_are_read_too(engine):
    rows = engine["evaluate_eyesight_places"](pdata(Sun=240.5, Moon=0.0), 240.5)
    assert [(r['Point'], r['Source']) for r in rows] == [
        ('Sun', f'{SAHL}, 63'), ('Sun', f'{SAHL}, 71'), ('Sun', f'{SAHL}, 74'),
        ('Ascendant', f'{SAHL}, 63'), ('Ascendant', f'{SAHL}, 71'), ('Ascendant', f'{SAHL}, 74')]


def test_calculated_chart_runs(engine):
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    rows = engine["evaluate_eyesight_places"](chart['planetary_data'], chart['ascendant'])
    assert isinstance(rows, list)


def test_the_lord_of_the_ascendant_is_read_as_sahl_48_names_it(engine):
    # Ascendant in Taurus: the lord is Venus. Venus in the Pleiades' span
    # (Sahl 49-55 name the Moon; 48 names "the lord of the Ascendant").
    p = pdata(Sun=200.0, Moon=250.0)
    p['Venus'] = {'longitude': 30.0 + 8.5}
    rows = engine["evaluate_eyesight_places"](p, 40.0)
    assert rows and all(r['Point'] == 'Lord of the Ascendant (Venus)' for r in rows)
    # Ascendant in Leo: the Sun is the lord, and its one row carries both roles.
    p2 = pdata(Sun=30.0 + 8.5, Moon=250.0)
    rows2 = engine["evaluate_eyesight_places"](p2, 130.0)
    assert rows2 and {r['Point'] for r in rows2} == {'Sun (the lord of the Ascendant)'}
