"""Mercury's phase against the sect of the chart (Firmicus, Mathesis III.7,
Dykes's fnn 186, 194): a morning star (eastern of the Sun) matches a
diurnal nativity, an evening star (western) a nocturnal one; the other two
pairings mismatch. One display-only row, returned for every chart."""
from datetime import datetime

import pytest

MATCH = "the success that comes from Mercury's phase matching that of the chart"
MISMATCH = "less respected and independent uses of the intellect and skill"


def _chart(sun_lon, mercury_lon):
    return {'Sun': {'longitude': sun_lon},
            'Mercury': {'longitude': mercury_lon, 'speed_in_lon': 1.0}}


@pytest.mark.parametrize("sun_lon, mercury_lon, sect, phase, match, reading", [
    # Mercury 12 degrees behind the Sun in the zodiac: rises before him, eastern.
    (100.0, 88.0, 'Diurnal', 'morning star (eastern)', 'Yes', MATCH),
    (100.0, 88.0, 'Nocturnal', 'morning star (eastern)', 'No', MISMATCH),
    # Mercury 12 degrees ahead of the Sun: sets after him, western.
    (100.0, 112.0, 'Nocturnal', 'evening star (western)', 'Yes', MATCH),
    (100.0, 112.0, 'Diurnal', 'evening star (western)', 'No', MISMATCH),
])
def test_four_pairings(engine, sun_lon, mercury_lon, sect, phase, match, reading):
    rows = engine["evaluate_mercury_phase_sect"](_chart(sun_lon, mercury_lon), sect)
    assert len(rows) == 1
    row = rows[0]
    assert list(row) == ['Mercury', 'Phase', 'Sect', 'Match', 'Reading']
    assert (row['Phase'], row['Sect'], row['Match'], row['Reading']) == (phase, sect, match, reading)


def test_side_agrees_with_solar_phase_across_the_circle(engine):
    """The row's phase is solar_phase's side, wrap-around included."""
    for sun_lon, mercury_lon in [(5.0, 355.0), (355.0, 5.0), (0.0, 20.0), (20.0, 0.0)]:
        _p, side, _e = engine["solar_phase"]('Mercury', mercury_lon, sun_lon, 1.0)
        row = engine["evaluate_mercury_phase_sect"](_chart(sun_lon, mercury_lon), 'Diurnal')[0]
        assert row['Phase'] == ('morning star (eastern)' if side == 'eastern' else 'evening star (western)')


def test_a_computed_chart_passes_through(engine):
    """A diurnal chart with Mercury eastern of the Sun: the match case."""
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    assert chart['sect'] == 'Diurnal'
    rows = engine["evaluate_mercury_phase_sect"](chart['planetary_data'], chart['sect'])
    assert len(rows) == 1
    row = rows[0]
    assert row['Sect'] == 'Diurnal'
    assert row['Phase'] == 'morning star (eastern)'
    assert row['Match'] == 'Yes'
    assert row['Reading'] == MATCH
