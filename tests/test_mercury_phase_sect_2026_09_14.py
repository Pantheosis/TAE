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


def _planets(**longitudes):
    defaults = {'Sun': 180.0, 'Moon': 40.0, 'Mercury': 179.0, 'Venus': 45.0,
                'Mars': 10.0, 'Jupiter': 100.0, 'Saturn': 310.0}
    defaults.update(longitudes)
    speeds = {'Sun': 1.0, 'Moon': 13.0, 'Mercury': 1.2, 'Venus': 1.1,
              'Mars': .5, 'Jupiter': .08, 'Saturn': .03}
    return {name: {'longitude': lon, 'latitude': 0.0, 'distance': 1.0,
                   'speed_in_lon': speeds[name], 'speed_in_dist': -0.01}
            for name, lon in defaults.items()}


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


@pytest.mark.parametrize('sun_lon, mercury_lon, expected', [
    (180.0, 179.0, True),
    (180.0, 181.0, False),
    (0.0, 359.0, True),
    (359.0, 0.0, False),
])
def test_astra_phase_cases_use_normalized_unrounded_positions(engine, sun_lon, mercury_lon, expected):
    assert engine['mercury_phase_sect'](mercury_lon, sun_lon) is expected


def test_exact_conjunction_is_unassigned_everywhere_phase_is_used(engine):
    p = _planets(Sun=0.0, Mercury=0.0)
    phase = engine['mercury_phase_sect'](0.0, 0.0)
    assert isinstance(phase, engine['UnresolvedResult'])
    assert phase.status == 'unassigned' and phase.reason == 'exact conjunction'
    assert phase.display_label == 'Unassigned by phase' and phase.display_alternatives is False
    with pytest.raises(TypeError):
        bool(phase)

    finding = engine['evaluate_mercury_phase_sect'](p, 'Diurnal')[0]
    assert finding['Phase'] == phase and finding['Match'] == phase

    cusps = [(170.0 + 30.0 * n) % 360.0 for n in range(12)]
    accidental = engine['evaluate_accidental_dignities'](p, cusps, 'Diurnal')
    assert accidental['Mercury']['PlanetSect'] == phase
    assert isinstance(accidental['Mercury']['Hayz'], engine['UnresolvedResult'])
    score = accidental['Mercury']['Accidental Score']
    assert isinstance(score, engine['UnresolvedResult'])
    assert score.alternatives[0][1] - score.alternatives[1][1] == 3
    assert f"known subtotal {accidental['Mercury']['Known Accidental Score']}" in score.reason
    long_domain = engine['domain_description'](accidental['Mercury'])
    short_domain = engine['domain_description'](accidental['Mercury'], short=True)
    assert isinstance(long_domain, engine['UnresolvedResult'])
    assert long_domain.alternatives == (
        ('if Mercury is diurnal', 'in its own domain (hayz)'),
        ('if Mercury is nocturnal', 'contrary to its domain'))
    assert short_domain.alternatives == (
        ('if Mercury is diurnal', 'in its own domain'),
        ('if Mercury is nocturnal', 'contrary to its domain'))

    essential = engine['evaluate_essential_dignities'](p, 'Diurnal')
    strength = engine['evaluate_strength_of_planets'](p, essential, accidental, 170.0, 'Diurnal', cusps)
    mercury = next(row for row in strength if row['Planet'] == 'Mercury')
    testimony = next(item for item in mercury['Testimonies'] if item['n'] == '85')
    assert testimony['result'] == phase
    assert mercury['Unresolved Count'] == 1
    assert mercury['Count'] == len(mercury['Labels'])
    assert '(85)' not in mercury['Strength Testimonies']

    p['North Node'] = {'longitude': 220.0, 'latitude': 0.0, 'distance': 1.0,
                       'speed_in_lon': -0.05, 'speed_in_dist': 0.0}
    essential = engine['evaluate_essential_dignities'](p, 'Diurnal')
    accidental = engine['evaluate_accidental_dignities'](p, cusps, 'Diurnal')
    condition = engine['evaluate_abu_mashar_condition'](
        p, cusps, 'Diurnal', essential, accidental, 2451545.0, 170.0)['Mercury']
    assert condition['Good Fortune'].alternatives == (
        ('if Mercury is diurnal', 11), ('if Mercury is nocturnal', 10))
    assert condition['Weakness'].alternatives == (
        ('if Mercury is diurnal', 2), ('if Mercury is nocturnal', 3))
    assert condition['Net'].alternatives == (
        ('if Mercury is diurnal', 4), ('if Mercury is nocturnal', 2))
    # Both totals are outside the one-vote indeterminate band, so the class
    # converges even though the total remains unassigned.
    assert condition['Condition'] == 'Good'
    assert len(condition['Unresolved Positive Labels']) == 1
    assert len(condition['Unresolved Negative Labels']) == 1


def test_exact_conjunction_domain_can_resolve_false_from_independent_conditions(engine):
    # Mercury in Aries below the horizon in a diurnal chart: diurnal Mercury
    # fails the hemisphere condition and nocturnal Mercury fails sign gender,
    # so both alternatives settle domain as false.
    p = _planets(Sun=0.0, Mercury=0.0)
    cusps = [(350.0 + 30.0 * n) % 360.0 for n in range(12)]
    accidental = engine['evaluate_accidental_dignities'](p, cusps, 'Diurnal')
    assert accidental['Mercury']['Hayz'] is False
    assert isinstance(accidental['Mercury']['Accidental Score'], int)


def test_company_is_separate_names_conflicts_and_excludes_the_sun(engine):
    assert engine['evaluate_mercury_company'](_planets(Sun=180.0, Mercury=179.0)) == []

    venus = engine['evaluate_mercury_company'](
        _planets(Sun=180.0, Mercury=179.0, Venus=175.0))
    assert [row['Companion'] for row in venus] == ['Venus']
    assert venus[0]['Companion sect'] == 'Nocturnal'
    assert 'disagrees with phase' in venus[0]['Company indication']
    assert 'no company override' in venus[0]['Company indication']

    jupiter = engine['evaluate_mercury_company'](
        _planets(Sun=180.0, Mercury=181.0, Jupiter=185.0))
    assert [row['Companion'] for row in jupiter] == ['Jupiter']
    assert jupiter[0]['Companion sect'] == 'Diurnal'
    assert 'disagrees with phase' in jupiter[0]['Company indication']

    mixed = engine['evaluate_mercury_company'](
        _planets(Sun=180.0, Mercury=179.0, Venus=175.0, Jupiter=178.0))
    assert {row['Companion'] for row in mixed} == {'Venus', 'Jupiter'}
    assert all(row['Company indication'].startswith('Conflicting company indications') for row in mixed)
    assert all('no supplied tie-break' in row['Company indication'] for row in mixed)

    exact = engine['evaluate_mercury_company'](_planets(Sun=180.0, Mercury=180.0))
    assert exact == []
