"""Valens, Anthologies II.36: the Moon's eleven phases by its waxing angle
from the Sun. The engine assigns by angle -- the text's degrees where it
gives them, the app's where it does not (the constant says which) -- and
returns exactly one row for the chart's Moon."""
from datetime import datetime

import pytest


def _pdata(moon_lon, sun_lon=0.0):
    return {'Sun': {'longitude': sun_lon}, 'Moon': {'longitude': moon_lon}}


@pytest.mark.parametrize("moon_lon,phase,ruler", [
    (3.0, 'New moon', '--'),
    (11.99, 'New moon', '--'),
    (12.0, 'First visibility', 'Mercury (to day 4)'),
    (30.0, 'First visibility', 'Mercury (to day 4)'),
    (45.0, 'Crescent', 'Mercury (to day 8)'),
    (70.0, 'Crescent', 'Mercury (to day 8)'),
    (90.0, 'Quarter', 'Venus (to day 12)'),
    (134.9, 'Quarter', 'Venus (to day 12)'),
    (135.0, 'Gibbous', 'Sun (to day 14)'),
    (180.0, 'Full moon', '--'),
    (191.9, 'Full moon', '--'),
    (192.0, 'First waning of the light', 'Mars (to day 21)'),
    (224.9, 'First waning of the light', 'Mars (to day 21)'),
    (225.0, 'Second gibbous', 'Jupiter (to day 25)'),
    (270.0, 'Second quarter', 'Saturn (to day 30)'),
    (315.0, 'Second crescent', '--'),
    (347.9, 'Second crescent', '--'),
    (348.0, 'Final visibility', '--'),
    (359.9, 'Final visibility', '--'),
])
def test_phase_by_waxing_angle(engine, moon_lon, phase, ruler):
    rows = engine["evaluate_moon_phase_valens"](_pdata(moon_lon))
    assert len(rows) == 1
    assert rows[0]['Phase'] == phase
    assert rows[0]['Ruler (to day)'] == ruler
    assert rows[0]['Angle from Sun'] == f"{moon_lon:.2f}°"


def test_angle_is_counted_forward_from_the_sun_across_aries(engine):
    # Sun at 350, Moon at 20: 30 degrees ahead, not 330 behind.
    rows = engine["evaluate_moon_phase_valens"](_pdata(20.0, 350.0))
    assert rows[0]['Phase'] == 'First visibility'
    assert rows[0]['Angle from Sun'] == "30.00°"
    # Sun at 20, Moon at 350: 330 ahead, the second crescent.
    rows = engine["evaluate_moon_phase_valens"](_pdata(350.0, 20.0))
    assert rows[0]['Phase'] == 'Second crescent'


def test_phases_are_eleven_contiguous_and_cover_the_circle(engine):
    phases = engine["VALENS_MOON_PHASES"]
    assert len(phases) == 11
    assert phases[0][1] == 0.0 and phases[-1][2] == 360.0
    for a, b in zip(phases, phases[1:]):
        assert a[2] == b[1], (a[0], b[0])
    # The text's own degrees stand at both ends of these five.
    given = {p[0]: (p[1], p[2]) for p in phases if p[3] == 'Valens'}
    assert given == {'Crescent': (45.0, 90.0), 'Quarter': (90.0, 135.0), 'Gibbous': (135.0, 180.0),
                     'Second gibbous': (225.0, 270.0), 'Second quarter': (270.0, 315.0)}


def test_chart_moon_gets_one_row(engine):
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    rows = engine["evaluate_moon_phase_valens"](chart['planetary_data'])
    assert len(rows) == 1
    assert set(rows[0]) == {'Moon', 'Angle from Sun', 'Phase', 'Indicates', 'Ruler (to day)'}
    assert rows[0]['Phase'] in {p[0] for p in engine["VALENS_MOON_PHASES"]}
