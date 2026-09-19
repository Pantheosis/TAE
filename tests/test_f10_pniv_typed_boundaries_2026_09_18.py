"""F10 result objects at the PN IV table and export boundaries."""

import json

from conftest import assert_no_exception, make_app


def _conditional_pniv_rows(engine):
    positions = {
        'Sun': 180.0, 'Moon': 240.0, 'Mercury': 180.0, 'Venus': 90.0,
        'Mars': 90.0, 'Jupiter': 300.0, 'Saturn': 0.0,
    }
    speeds = {
        'Sun': 1.0, 'Moon': 13.0, 'Mercury': 1.2, 'Venus': 1.1,
        'Mars': 0.7, 'Jupiter': 0.08, 'Saturn': 0.03,
    }
    data = {
        planet: {
            'longitude': longitude, 'latitude': 0.0, 'distance': 1.0,
            'speed_in_lon': speeds[planet], 'speed_in_lat': 0.0,
            'speed_in_dist': 0.0,
        }
        for planet, longitude in positions.items()
    }
    chart = {
        'planetary_data': data, 'ascendant': 0.0,
        'houses': [float(value) for value in range(0, 360, 30)],
        'sect': 'Diurnal', 'julian_day': 2451545.0,
    }
    year = {'sign': 'Gemini', 'longitude': 60.0, 'lord': 'Mercury'}
    run = engine['_RUN']
    had_override = hasattr(run, 'DOMAIN_RULE')
    previous = getattr(run, 'DOMAIN_RULE', None)
    try:
        engine['set_readings'](DOMAIN_RULE="Masha'allah")
        i7 = engine['pn4_i7_planets'](chart, chart)
        ii3 = engine['pn4_ii3_examination'](chart, chart, year, 2451545.0)
    finally:
        if had_override:
            engine['set_readings'](DOMAIN_RULE=previous)
        else:
            delattr(run, 'DOMAIN_RULE')

    mercury = [row for row in i7 if row['Planet'] == 'Mercury']
    assert len(mercury) == 2
    assert all(isinstance(row['Domain (17)'], engine['UnresolvedResult']) for row in mercury)
    domain = next(row for row in ii3['lord_rows']
                  if row['Factor'] == 'In its own domain (sect), or the contrary')
    assert isinstance(domain['Root'], engine['UnresolvedResult'])
    assert isinstance(domain['Revolution'], engine['UnresolvedResult'])
    return i7, ii3


def _export_table(export, heading, column):
    return next(table for table in export['results']['Prediction'][heading]
                if column in table['columns'])


def _assert_explicit_unresolved(value):
    assert value['result_type'] == 'UnresolvedResult'
    assert value['status'] == 'unassigned'
    assert "Mercury's domain description depends" in value['reason']
    assert value['source'] == 'Great Introduction IV.9, 8; VII.1, 37-39; VII.6, 13, 36'
    assert [alternative['name'] for alternative in value['alternatives']] == [
        'if Mercury is diurnal', 'if Mercury is nocturnal']
    assert value['display'].startswith('Unassigned — ')


def test_actual_conditional_pniv_results_render_and_export_without_internal_repr(
        engine, monkeypatch):
    # Build the AppTest before patching so the harness has already completed
    # any environment-driven engine reload.
    at = make_app(page='timing')
    i7, ii3 = _conditional_pniv_rows(engine)

    import engine as engine_module
    monkeypatch.setattr(engine_module, 'pn4_i7_planets', lambda *_args, **_kwargs: i7)
    monkeypatch.setattr(engine_module, 'pn4_ii3_examination', lambda *_args, **_kwargs: ii3)
    at.session_state['_domain_rule'] = "Masha'allah"
    at.run()
    assert_no_exception(at, 'conditional PN IV boundaries')

    frames = [node.value for node in at.main
              if getattr(node, 'type', None) == 'dataframe']
    i7_frame = next(frame for frame in frames
                    if {'Planet', 'Chart', 'Domain (17)'} <= set(frame.columns))
    mercury_cells = i7_frame.loc[i7_frame['Planet'] == 'Mercury', 'Domain (17)'].tolist()
    assert len(mercury_cells) == 2
    assert all(isinstance(value, str) and value.startswith('Unassigned — ')
               for value in mercury_cells)

    ii3_frame = next(frame for frame in frames
                     if {'Factor', 'Root', 'Revolution'} <= set(frame.columns))
    domain_row = ii3_frame.loc[
        ii3_frame['Factor'] == 'In its own domain (sect), or the contrary'].iloc[0]
    assert str(domain_row['Root']).startswith('Unassigned — ')
    assert str(domain_row['Revolution']).startswith('Unassigned — ')

    export = at.session_state['_analysis_export']
    i7_table = _export_table(export, 'The reading checklist (I.7, 1-26)', 'Domain (17)')
    exported_mercury = [row['Domain (17)'] for row in i7_table['rows']
                        if row['Planet'] == 'Mercury']
    assert len(exported_mercury) == 2
    for value in exported_mercury:
        _assert_explicit_unresolved(value)
        assert [alternative['value'] for alternative in value['alternatives']] == [
            'neither', 'in its own domain']

    ii3_table = _export_table(
        export, 'The sign of the terminal point and its lord, examined (II.3, 2-19)',
        'Factor')
    exported_domain = next(row for row in ii3_table['rows']
                           if row['Factor'] == 'In its own domain (sect), or the contrary')
    _assert_explicit_unresolved(exported_domain['Root'])
    _assert_explicit_unresolved(exported_domain['Revolution'])

    encoded = json.dumps(export, ensure_ascii=False)
    markdown = at.session_state['_analysis_markdown']
    assert 'UnresolvedResult(' not in encoded
    assert 'YearsOutcome(' not in encoded
    assert 'UnresolvedResult(' not in markdown
    assert 'YearsOutcome(' not in markdown
    assert "Unassigned — Mercury's domain description depends" in markdown
