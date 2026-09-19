"""F10 G28/G05: directional solar endpoints and canon-only aspect display."""

from contextlib import contextmanager

import pytest

from conftest import assert_no_exception, find_table, make_app


EPS = 1e-9


@contextmanager
def _reading(engine, name, value):
    run = engine['_RUN']
    missing = object()
    previous = getattr(run, name, missing)
    engine['set_readings'](**{name: value})
    try:
        yield
    finally:
        if previous is missing:
            delattr(run, name)
        else:
            setattr(run, name, previous)


@pytest.mark.parametrize(
    'planet,longitude,speed,at_boundary,outside',
    [
        ('Moon', 88.0, None, 'Under the rays', None),
        ('Moon', 94.0, None, 'Burned', 'Under the rays'),
        ('Venus', 88.0, 1.0, 'Under the rays', None),
        ('Mercury', 88.0, 1.0, 'Under the rays', None),
        ('Venus', 94.0, 1.0, 'Burned', 'Under the rays'),
        ('Mercury', 94.0, 1.0, 'Burned', 'Under the rays'),
    ],
)
def test_approaching_eastern_moon_and_direct_inferiors_enter_at_the_endpoint(
        engine, planet, longitude, speed, at_boundary, outside):
    phase = engine['solar_phase']
    assert phase(planet, longitude, 100.0, speed)[0] == at_boundary
    assert phase(planet, longitude - EPS, 100.0, speed)[0] == outside


@pytest.mark.parametrize('planet', ['Venus', 'Mercury'])
def test_direct_western_inferiors_leave_burning_at_seven_but_keep_fifteen(engine, planet):
    phase = engine['solar_phase']
    assert phase(planet, 107.0 - EPS, 100.0, 1.0)[0] == 'Burned'
    assert phase(planet, 107.0, 100.0, 1.0)[0] == 'Under the rays'
    assert phase(planet, 115.0, 100.0, 1.0)[0] == 'Under the rays'
    assert phase(planet, 115.0 + EPS, 100.0, 1.0)[0] is None


def test_retrograde_superior_and_missing_motion_endpoint_controls_stand(engine):
    phase = engine['solar_phase']
    # Retrograde inferiors retain 37/40's eastern completion and 53's
    # western entry. The speedless fallback retains 7 and side ownership.
    assert phase('Venus', 93.0, 100.0, -0.5)[0] == 'Under the rays'
    assert phase('Venus', 107.0, 100.0, -0.5)[0] == 'Burned'
    assert phase('Venus', 93.0, 100.0, None)[0] == 'Under the rays'
    assert phase('Venus', 88.0, 100.0, None)[0] is None
    # The F10 superior cases keep completion east and entry west.
    assert phase('Saturn', 94.0, 100.0)[0] == 'Under the rays'
    assert phase('Saturn', 85.0, 100.0)[0] is None
    assert phase('Saturn', 106.0, 100.0)[0] == 'Burned'


def test_moon_fifteen_degree_reading_remains_symmetric_and_inclusive(engine):
    with _reading(engine, 'MOON_RAYS_ORB', 15.0):
        assert engine['solar_phase']('Moon', 85.0, 100.0)[0] == 'Under the rays'
        assert engine['solar_phase']('Moon', 115.0, 100.0)[0] == 'Under the rays'
        assert engine['solar_phase']('Moon', 85.0 - EPS, 100.0)[0] is None
        assert engine['solar_phase']('Moon', 115.0 + EPS, 100.0)[0] is None


def test_mars_eighteen_west_reading_keeps_the_paired_setting_band(engine):
    with _reading(engine, 'MARS_WEST_RAYS_18', False):
        assert engine['solar_setting_degree']('Mars') == 18.0
        assert engine['solar_phase']('Mars', 118.0, 100.0, 0.7)[0] == 'Degrees of setting'
        assert engine['solar_phase']('Mars', 120.0, 100.0, 0.7)[0] is None

    with _reading(engine, 'MARS_WEST_RAYS_18', True):
        assert engine['solar_setting_degree']('Mars') == 22.0
        assert engine['solar_phase']('Mars', 118.0, 100.0, 0.7)[0] == 'Under the rays'
        assert engine['solar_phase']('Mars', 118.0 + EPS, 100.0, 0.7)[0] == 'Degrees of setting'
        assert engine['solar_phase']('Mars', 122.0, 100.0, 0.7)[0] == 'Degrees of setting'
        assert engine['solar_phase']('Mars', 122.0 + EPS, 100.0, 0.7)[0] is None
        assert engine['solar_phase']('Saturn', 120.0, 100.0, 0.03)[0] == 'Degrees of setting'


def _body(longitude, speed):
    return {'longitude': longitude, 'latitude': 0.0, 'distance': 1.0,
            'speed_in_lon': speed, 'speed_in_lat': 0.0, 'speed_in_dist': 0.0}


@pytest.mark.parametrize('moon,connection,distance', [
    (227.0, 'Separated', "07° 00'"),
    (232.0, 'Separated', "12° 00'"),
    (238.0, 'Separated', "18° 00'"),
    (212.0, 'Applying', "08° 00'"),
])
def test_aspect_rows_keep_exact_distance_and_connection_without_an_app_grade(
        engine, moon, connection, distance):
    row = engine['evaluate_ptolemaic_aspects']({
        'Saturn': _body(100.0, 0.03), 'Moon': _body(moon, 13.0)})[0]
    assert row['Aspect'] == 'Trine'
    assert row['Exact Orb Dist'] == distance
    assert row['Connection'] == connection
    assert row['Strength'] == '–'


def test_source_backed_assembly_strength_remains(engine):
    row = engine['evaluate_ptolemaic_aspects']({
        'Saturn': _body(100.0, 0.03), 'Moon': _body(105.0, 13.0)})[0]
    assert row['Aspect'] == 'Conjunction'
    assert row['Bodies'] == 'Mutual'
    assert row['Strength'].startswith('Strong')


def test_chart_app_value_shows_the_preserved_mars_setting_band():
    off = make_app(date='1240-01-10', page='chart').run()
    on = make_app(date='1240-01-10', page='chart', switches={'mars_west': True}).run()
    assert_no_exception(off, 'Mars setting reading off')
    assert_no_exception(on, 'Mars setting reading on')
    off_table = next(node.value for node in off.main.dataframe if 'Solar phase' in node.value.columns)
    on_table = next(node.value for node in on.main.dataframe if 'Solar phase' in node.value.columns)
    off_value = off_table.loc[off_table['Planet'] == 'Mars', 'Solar phase'].iloc[0]
    on_value = on_table.loc[on_table['Planet'] == 'Mars', 'Solar phase'].iloc[0]
    assert off_value == '–'
    assert on_value == 'Degrees of setting, western'


def test_configurations_app_values_drop_aspect_scale_and_keep_assembly_grades():
    at = make_app(page='configurations').run()
    assert_no_exception(at, 'G28 aspect display')
    table = find_table(at, 'Aspects, aversions and connections').value
    aspect_rows = table[~table['Aspect'].isin(['Conjunction', 'Aversion'])]
    assert len(aspect_rows) and set(aspect_rows['Strength']) == {'–'}
    assembly_rows = table[table['Aspect'] == 'Conjunction']
    assert len(assembly_rows) and all(value != '–' for value in assembly_rows['Strength'])
    rendered = '\n'.join(str(node.value) for node in at.main.markdown)
    assert '(app scale)' not in rendered
    assert '**Strength for assemblies; distance for aspects.**' in rendered


def test_moon_phase_and_rays_measures_remain_independent_and_are_explained(engine):
    with _reading(engine, 'MOON_RAYS_ORB', 15.0):
        assert engine['solar_phase']('Moon', 13.0, 0.0, 13.0)[0] == 'Under the rays'
        row = engine['evaluate_moon_phase_valens']({
            'Sun': {'longitude': 0.0}, 'Moon': {'longitude': 13.0}})[0]
        assert row['Phase'] == 'First visibility'

    at = make_app(page='findings', view="Abu Ma'shar").run()
    assert_no_exception(at, 'G05 independent measures')
    phase_table = find_table(at, "The Moon's phase, Valens's eleven").value
    assert len(phase_table) == 1 and phase_table['Phase'].iloc[0]
    rendered = '\n'.join(str(node.value) for node in at.main.markdown)
    sentence = ("The 12° bounds not given by Valens are Abu Ma'shar's phase markers "
                "(ITA II.10.5) applied to Valens's phases")
    assert sentence in rendered
    assert "at 13° the Moon can be both under the rays and in first visibility" in rendered
