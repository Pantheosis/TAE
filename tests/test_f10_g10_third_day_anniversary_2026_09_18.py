"""F10 G10: distinct third-day relations and strict local anniversaries."""

import swisseph as swe
import pytest

from conftest import assert_no_exception, find_table, make_app


MOON_SPEED = 13.0


def _planetary_data(**positions):
    defaults = {
        'Sun': (310.0, 1.0), 'Moon': (10.0, MOON_SPEED),
        'Mercury': (220.0, 1.2), 'Venus': (250.0, 1.1),
        'Mars': (40.0, 0.7), 'Jupiter': (280.0, 0.08),
        'Saturn': (160.0, 0.03),
    }
    defaults.update(positions)
    return {
        name: {'longitude': float(lon), 'latitude': 0.0, 'distance': 1.0,
               'speed_in_lon': float(speed), 'speed_in_lat': 0.0, 'speed_in_dist': 0.0}
        for name, (lon, speed) in defaults.items()
    }


def _third(**positions):
    data = _planetary_data(**positions)
    return {'planetary_data': data, **{name: row['longitude'] for name, row in data.items()}}


def _row(rows, prefix):
    hits = [row for row in rows if row['Item'].startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


@pytest.mark.parametrize(
    'saturn,look,corrupt',
    [
        (70.0, True, False),     # Gemini, sextile
        (130.0, True, False),    # Leo, trine
        (100.0, True, True),     # Cancer, square
        (190.0, True, True),     # Libra, opposition
        (25.0, False, True),     # Aries, co-present
        (160.0, False, False),   # Virgo, aversion
    ],
)
def test_astras_six_saturn_cases_keep_looking_and_corruption_distinct(engine, saturn, look, corrupt):
    # Moon 10 Aries, Sun 10 Aquarius, Mars 10 Taurus; Pisces rising makes
    # Aries the non-falling second place. Mars is in aversion, so enclosure
    # is definitively false in this complete seven-planet snapshot.
    rows = engine['moon_third_day_rows'](
        _third(Saturn=(saturn, 0.03)), {'Saturn': 160.0, 'Mars': 40.0}, 340.0)
    looking = _row(rows, 'The infortunes looking')['Value']
    corruption = _row(rows, 'Third-day Moon: corruption checks')['Value']
    indicator = _row(rows, '1.26, 7')['Value']
    assert looking.startswith('Yes:') is look
    assert corruption.startswith('Corruption found') is corrupt
    assert (indicator.startswith('Met:')) is look  # Aries has four feet.
    if saturn == 25.0:
        assert _row(rows, 'Co-presence')['Value'].startswith('Yes: Saturn with her in Aries')
        assert looking.startswith('No intersign look:')
    if saturn in (70.0, 130.0):
        assert corruption == 'No corruption found in these checks'


def test_partial_snapshot_discloses_enclosure_and_propagates_only_surviving_uncertainty(engine):
    third = {'Moon': 10.0, 'Sun': 310.0, 'Saturn': 160.0, 'Mars': 40.0}
    rows = engine['moon_third_day_rows'](third, {'Saturn': 160.0, 'Mars': 40.0}, 340.0)
    enclosure = _row(rows, 'Enclosure')['Value']
    corruption = _row(rows, 'Third-day Moon: corruption checks')['Value']
    day_11 = _row(rows, '1.29, 11')['Value']
    day_12 = _row(rows, '1.29, 12')['Value']
    assert isinstance(enclosure, engine['UnresolvedResult']) and enclosure.status == 'unavailable'
    assert isinstance(corruption, engine['UnresolvedResult']) and corruption.status == 'unavailable'
    assert isinstance(day_11, engine['UnresolvedResult'])
    # Both natal infortunes are outside the first/seventh, so that known
    # false prerequisite settles this conjunction despite unknown enclosure.
    assert isinstance(day_12, str) and day_12.startswith('Not met:')


def test_known_burning_settles_corruption_even_when_enclosure_is_unavailable(engine):
    partial = {'Moon': 10.0, 'Sun': 15.0, 'Saturn': 160.0, 'Mars': 40.0}
    rows = engine['moon_third_day_rows'](partial, {'Saturn': 160.0, 'Mars': 40.0}, 340.0)
    assert isinstance(_row(rows, 'Enclosure')['Value'], engine['UnresolvedResult'])
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == (
        'Corruption found in these checks: burned')
    assert _row(rows, '1.29, 11')['Value'].startswith('Third-day component does not hold')


def _figure_25_third(mercury=330.0):
    # Sahl Fig. 25: Moon 13 Libra separates from Mars 10 Cancer and applies
    # to Saturn 18 Aries. Mercury 14 Aries supplies the blocking control.
    return _third(
        Sun=(300.0, 1.0), Moon=(193.0, MOON_SPEED), Mercury=(mercury, 1.2),
        Venus=(50.0, 1.1), Mars=(100.0, 0.7), Jupiter=(250.0, 0.08),
        Saturn=(18.0, 0.03),
    )


def test_third_day_enclosure_uses_separation_application_and_no_intervening_ray(engine):
    open_rays = engine['third_day_enclosure'](_figure_25_third())
    assert open_rays == {'enclosed': True, 'severe': True,
                         'separating_from': 'Mars', 'connecting_to': 'Saturn'}
    for mercury in (14.0, 72.0, 74.0):
        # 14 is the existing live-connection block. At 72 and 74 Mercury's
        # trine rays fall at 192 and 194, on the two sides of the Moon and
        # strictly between Mars's ray at 190 and Saturn's at 198.
        blocked = engine['third_day_enclosure'](_figure_25_third(mercury=mercury))
        assert blocked == {'enclosed': False, 'severe': False,
                           'separating_from': None, 'connecting_to': None}


@pytest.mark.parametrize(
    'mercury,enclosed',
    [
        (69.999999, True), (70.0, True),
        (70.000001, False), (73.0, False), (77.999999, False),
        (78.0, True), (78.000001, True),
    ],
)
def test_original_orientation_uses_strict_ray_endpoints(engine, mercury, enclosed):
    result = engine['third_day_enclosure'](_figure_25_third(mercury=mercury))
    assert result['enclosed'] is enclosed


def _opposite_orientation_third(mercury, mars=310.0, saturn=258.0):
    # The Moon is west of both malefic bodies. Their selected rays remain
    # Mars 190 and Saturn 198, although unsigned deviations would reflect
    # them to 196 and 188 respectively.
    return _third(
        Sun=(300.0, 1.0), Moon=(193.0, MOON_SPEED), Mercury=(mercury, 1.2),
        Venus=(50.0, 1.1), Mars=(mars, 0.7), Jupiter=(240.0, 0.08),
        Saturn=(saturn, 0.03),
    )


@pytest.mark.parametrize('mars,saturn', [(310.0, 258.0), (280.0, 318.0)])
@pytest.mark.parametrize(
    'mercury,enclosed',
    [(330.0, True), (77.0, False), (69.0, True),
     (70.0, True), (78.0, True), (73.0, False)],
)
def test_opposite_orientation_uses_the_directed_selected_aspect_ray(
        engine, mars, saturn, mercury, enclosed):
    result = engine['third_day_enclosure'](
        _opposite_orientation_third(mercury, mars=mars, saturn=saturn))
    assert result['enclosed'] is enclosed


@pytest.mark.parametrize('mercury,enclosed', [(330.0, True), (72.0, False),
                                               (74.0, False), (70.0, True),
                                               (78.0, True)])
def test_directed_ray_interval_wraps_through_zero(engine, mercury, enclosed):
    third = _figure_25_third(mercury=mercury)
    for planet, row in third['planetary_data'].items():
        row['longitude'] = (row['longitude'] + 180.0) % 360.0
        third[planet] = row['longitude']
    assert engine['third_day_enclosure'](third)['enclosed'] is enclosed


@pytest.mark.parametrize('mercury,expected', [(35.0, None), (47.0, 'Mercury'),
                                               (59.0, None)])
def test_endpoint_uses_the_rows_selected_aspect_near_a_sign_boundary(
        engine, mercury, expected):
    # Moon 0 Virgo and Mars 29 Gemini select a square by whole-sign
    # relationship. Mars's selected square ray is 29 degrees ahead at 29
    # Virgo; its sextile ray is only one degree behind the Moon, but must not
    # replace the selected square. Saturn's selected sextile ray is 5 Virgo.
    data = _planetary_data(
        Sun=(0.0, 1.0), Moon=(150.0, MOON_SPEED), Mercury=(mercury, 1.2),
        Venus=(0.0, 1.1), Mars=(89.0, 0.7), Jupiter=(0.0, 0.08),
        Saturn=(95.0, 0.03),
    )
    rows = [
        {'aspect_name': 'Square', 'signs_apart': 3, 'motion': 'Separating',
         'applicant': 'Moon', 'light_name': 'Moon',
         'receiver': 'Mars', 'heavy_name': 'Mars'},
        {'aspect_name': 'Sextile', 'signs_apart': 2, 'motion': 'Applying',
         'applicant': 'Moon', 'light_name': 'Moon',
         'receiver': 'Saturn', 'heavy_name': 'Saturn'},
    ]
    assert engine['_third_day_intervening_ray'](
        data, rows, 'Mars', 'Saturn') == expected


@pytest.mark.parametrize(
    'mercury,corruption,day_11',
    [(77.0, 'No corruption found in these checks',
      'Third-day component holds: no corruption found'),
     (69.0, 'Corruption found in these checks: enclosed between Mars and Saturn',
      'Third-day component does not hold: corruption found')],
)
def test_opposite_orientation_propagates_through_the_soft_aggregate(
        engine, mercury, corruption, day_11):
    rows = engine['moon_third_day_rows'](
        _opposite_orientation_third(mercury),
        {'Saturn': 160.0, 'Mars': 40.0}, 270.0)
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == corruption
    assert _row(rows, '1.29, 11')['Value'].startswith(day_11)


def test_third_day_enclosure_requires_longitude_and_motion_for_every_planet(engine):
    incomplete = _figure_25_third()
    del incomplete['planetary_data']['Venus']['longitude']
    result = engine['third_day_enclosure'](incomplete)
    assert isinstance(result, engine['UnresolvedResult'])
    assert result.status == 'unavailable'
    assert 'longitude and motion' in result.reason


def test_node_and_extra_entries_do_not_cast_intervening_rays(engine):
    third = _figure_25_third()
    third['planetary_data']['North Node'] = {
        'longitude': 74.0, 'latitude': 0.0, 'distance': 1.0,
        'speed_in_lon': -0.05, 'speed_in_lat': 0.0, 'speed_in_dist': 0.0,
    }
    third['North Node'] = 74.0
    assert engine['third_day_enclosure'](third) == {
        'enclosed': True, 'severe': True,
        'separating_from': 'Mars', 'connecting_to': 'Saturn',
    }


def test_intervening_ray_propagates_to_corruption_and_rendered_third_day_rows(
        engine, monkeypatch):
    third = _third(
        Sun=(300.0, 1.0), Moon=(193.0, MOON_SPEED), Mercury=(74.0, 1.2),
        Venus=(50.0, 1.1), Mars=(70.0, 0.7), Jupiter=(250.0, 0.08),
        Saturn=(138.0, 0.03),
    )
    rows = engine['moon_third_day_rows'](
        third, {'Saturn': 160.0, 'Mars': 40.0}, 270.0)
    assert _row(rows, 'Enclosure')['Value'].startswith('No:')
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == (
        'No corruption found in these checks')
    assert _row(rows, '1.29, 11')['Value'].startswith(
        'Third-day component holds: no corruption found')

    # The page boundary must carry that settled result as readable text.
    import engine as engine_module
    monkeypatch.setattr(engine_module, 'evaluate_moon_third_day', lambda _chart: rows)
    at = make_app(page='findings').run()
    assert_no_exception(at, 'intervening-ray third-day rendering')
    table = find_table(at, 'The Moon on the third day (Sahl)').value
    value = table.loc[
        table['Item'] == 'Third-day Moon: corruption checks (limited reading of 1.29, 3)',
        'Value',
    ].iloc[0]
    assert value == 'No corruption found in these checks'


def test_known_burning_still_settles_corruption_when_a_ray_breaks_enclosure(engine):
    third = _third(
        Sun=(195.0, 1.0), Moon=(193.0, MOON_SPEED), Mercury=(74.0, 1.2),
        Venus=(50.0, 1.1), Mars=(70.0, 0.7), Jupiter=(250.0, 0.08),
        Saturn=(138.0, 0.03),
    )
    rows = engine['moon_third_day_rows'](
        third, {'Saturn': 160.0, 'Mars': 40.0}, 270.0)
    assert _row(rows, 'Enclosure')['Value'].startswith('No:')
    assert _row(rows, 'Third-day Moon: corruption checks')['Value'] == (
        'Corruption found in these checks: burned')
    assert _row(rows, '1.29, 11')['Value'].startswith(
        'Third-day component does not hold: corruption found')


def test_third_day_enclosure_always_uses_the_fixed_saturn_mars_profile(engine):
    run = engine['_RUN']
    had_override = hasattr(run, 'SOFTENED_INFORTUNE')
    previous = getattr(run, 'SOFTENED_INFORTUNE', None)
    try:
        engine['set_readings'](SOFTENED_INFORTUNE=None)
        ordinary = engine['third_day_enclosure'](_figure_25_third())
        engine['set_readings'](SOFTENED_INFORTUNE='Saturn')
        alternate = engine['third_day_enclosure'](_figure_25_third())
    finally:
        if had_override:
            engine['set_readings'](SOFTENED_INFORTUNE=previous)
        else:
            delattr(run, 'SOFTENED_INFORTUNE')
    assert ordinary == alternate
    assert ordinary['enclosed'] is True


def _anniversary(engine, birth, years, **kwargs):
    result = engine['anniversary_moment'](birth, years, **kwargs)
    assert not isinstance(result, engine['UnresolvedResult'])
    return result


def test_anniversary_selects_local_date_before_converting_to_ut(engine):
    birth = engine['CivilMoment'](2025, 3, 1, 0, 30)
    past = _anniversary(engine, birth, -1, time_standard='fixed', utc_offset_hours=1.0,
                        birth_calendar=swe.GREG_CAL)
    future = _anniversary(engine, birth, 1, time_standard='fixed', utc_offset_hours=1.0,
                          birth_calendar=swe.GREG_CAL)
    assert past['local'].isoformat() == '2024-03-01 00:30:00'
    assert past['ut'].isoformat() == '2024-02-29 23:30:00'
    assert future['local'].isoformat() == '2026-03-01 00:30:00'
    assert future['ut'].isoformat() == '2026-02-28 23:30:00'
    natal_jd = swe.julday(2025, 3, 1, 0.5, swe.GREG_CAL) - 1.0 / 24.0
    assert 364.0 <= natal_jd - past['jd'] <= 366.5
    assert 364.0 <= future['jd'] - natal_jd <= 366.5


def test_leap_day_anniversaries_are_unavailable_without_an_elapsed_year_fallback(engine):
    birth = engine['CivilMoment'](2024, 2, 29, 5, 0)
    for years in (-1, 1):
        result = engine['anniversary_moment'](
            birth, years, time_standard='fixed', birth_calendar=swe.GREG_CAL)
        assert isinstance(result, engine['UnresolvedResult'])
        assert result.status == 'unavailable'
        assert 'unavailable under the same-date convention' in result.reason


def test_julian_leap_date_is_retained_and_not_normalized_as_gregorian(engine):
    birth = engine['CivilMoment'](1299, 3, 1, 0, 30)
    result = _anniversary(engine, birth, 1, time_standard='LMT (Local Mean Time)',
                          utc_offset_hours=2.0, birth_calendar=swe.JUL_CAL)
    assert result['local'].isoformat() == '1300-03-01 00:30:00'
    assert result['ut'].isoformat() == '1300-02-29 22:30:00'
    assert result['calendar'] == 'Julian' and result['standard'] == 'LMT'
    natal_jd = swe.julday(1299, 3, 1, 0.5, swe.JUL_CAL) - 2.0 / 24.0
    assert result['jd'] - natal_jd == pytest.approx(366.0)


@pytest.mark.parametrize(
    'birth,years,calendar',
    [((1581, 10, 20, 12), 1, swe.JUL_CAL),
     ((1583, 10, 20, 12), -1, swe.GREG_CAL)],
)
def test_reform_crossings_keep_the_birth_calendar_and_a_full_year(engine, birth, years, calendar):
    moment = engine['CivilMoment'](*birth)
    result = _anniversary(engine, moment, years, time_standard='fixed',
                          utc_offset_hours=0.0, birth_calendar=calendar)
    birth_jd = swe.julday(*birth[:3], float(birth[3]), calendar)
    assert result['local'].tuple() == (birth[0] + years, birth[1], birth[2])
    assert 364.0 <= abs(result['jd'] - birth_jd) <= 366.5
    assert abs(result['jd'] - birth_jd) == pytest.approx(365.0)


def test_named_zone_uses_each_target_dates_rule(engine):
    birth = engine['CivilMoment'](2006, 3, 20, 12, 0)
    original = _anniversary(engine, birth, 0, time_standard='named',
                            zone_name='America/New_York', birth_calendar=swe.GREG_CAL)
    following = _anniversary(engine, birth, 1, time_standard='named',
                             zone_name='America/New_York', birth_calendar=swe.GREG_CAL)
    assert original['offset_hours'] == -5.0 and original['ut'].isoformat() == '2006-03-20 17:00:00'
    assert following['offset_hours'] == -4.0 and following['ut'].isoformat() == '2007-03-20 16:00:00'
    assert following['local'].isoformat() == '2007-03-20 12:00:00'


def test_named_zone_preserves_ordinary_historical_julian_dates(engine):
    birth = engine['CivilMoment'](1240, 5, 23, 13, 45)
    result = _anniversary(engine, birth, 1, time_standard='Standard time (pytz)',
                          zone_name='Europe/Rome', birth_calendar=swe.JUL_CAL)
    assert result['local'].isoformat() == '1241-05-23 13:45:00'
    assert result['calendar'] == 'Julian'
    local_jd = swe.julday(1241, 5, 23, 13.75, swe.JUL_CAL)
    assert result['jd'] == pytest.approx(local_jd - result['offset_hours'] / 24.0)


def test_named_zone_reports_only_a_julian_date_datetime_cannot_carry(engine):
    result = engine['anniversary_moment'](
        engine['CivilMoment'](1296, 2, 29, 12, 0), 4,
        time_standard='Standard time (pytz)', zone_name='Europe/Rome',
        birth_calendar=swe.JUL_CAL)
    assert isinstance(result, engine['UnresolvedResult'])
    assert 'Julian-calendar date' in result.reason and 'cannot represent' in result.reason


@pytest.mark.parametrize(
    'birth,word',
    [((2020, 3, 14, 2, 30), 'does not exist'),
     ((2020, 11, 7, 1, 30), 'happens twice')],
)
def test_named_zone_nonexistent_and_ambiguous_target_clocks_are_unavailable(engine, birth, word):
    result = engine['anniversary_moment'](
        engine['CivilMoment'](*birth), 1, time_standard='named',
        zone_name='America/New_York', birth_calendar=swe.GREG_CAL)
    assert isinstance(result, engine['UnresolvedResult'])
    assert result.status == 'unavailable' and word in result.reason


def test_gestation_rows_preserve_unavailable_anniversary_values(engine):
    birth = engine['CivilMoment'](2024, 2, 29, 5, 0)
    jd = swe.julday(2024, 2, 29, 5.0, swe.GREG_CAL)
    moons = engine['gestation_moons'](
        jd, {'local_moment': birth, 'time_standard': 'fixed',
             'utc_offset_hours': 0.0, 'birth_calendar': swe.GREG_CAL})
    assert isinstance(moons['past']['longitude'], engine['UnresolvedResult'])
    assert isinstance(moons['renewed']['longitude'], engine['UnresolvedResult'])
    rows = engine['gestation_1_9_rows'](
        moons['natal']['longitude'], moons['past']['longitude'],
        moons['renewed']['longitude'], 0.0)
    assert isinstance(_row(rows, 'The past Moon')['Value'], engine['UnresolvedResult'])
    assert isinstance(_row(rows, 'The renewed Moon')['Value'], engine['UnresolvedResult'])
    assert isinstance(_row(rows, '1.9, 2-10')['Value'], engine['UnresolvedResult'])


def test_full_gestation_evaluator_keeps_natal_moon_when_anniversaries_are_unavailable(engine):
    birth = engine['CivilMoment'](2024, 2, 29, 5, 0)
    jd = swe.julday(2024, 2, 29, 5.0, swe.GREG_CAL)
    chart = engine['calculate_traditional_chart_jd'](jd, 43.7792, 11.2463)
    rows = engine['evaluate_gestation'](
        chart, birth_context={'local_moment': birth, 'time_standard': 'fixed',
                              'utc_offset_hours': 0.0, 'birth_calendar': swe.GREG_CAL})
    natal = _row(rows, 'The Moon of the nativity')['Value']
    assert isinstance(natal, str) and natal == engine['get_degree_string'](
        swe.calc_ut(jd, swe.MOON)[0][0] % 360.0)
    assert isinstance(_row(rows, 'The past Moon')['Value'], engine['UnresolvedResult'])
    assert isinstance(_row(rows, 'The renewed Moon')['Value'], engine['UnresolvedResult'])


def test_calendar_moment_rounding_carries_across_midnight(engine):
    almost_midnight = swe.julday(2024, 5, 1, 23 + 59 / 60 + 59.6 / 3600, swe.GREG_CAL)
    rounded = engine['_moment_from_jd_in_calendar'](almost_midnight, swe.GREG_CAL)
    assert rounded.isoformat() == '2024-05-02 00:00:00'


def test_findings_page_renders_g10_values_and_reader_sentence(engine):
    at = make_app(page='findings').run()
    assert_no_exception(at, 'G10 findings')
    third = find_table(at, 'The Moon on the third day (Sahl)').value
    corruption = third.loc[
        third['Item'] == 'Third-day Moon: corruption checks (limited reading of 1.29, 3)', 'Value']
    assert len(corruption) == 1
    assert isinstance(corruption.iloc[0], str) and corruption.iloc[0]
    fetus = find_table(at, "The fetus's stay (Sahl)").value
    past = fetus.loc[fetus['Item'] == 'The past Moon, a year before (1.9, 1)', 'Value'].iloc[0]
    renewed = fetus.loc[fetus['Item'] == 'The renewed Moon, a year after (1.9, 1)', 'Value'].iloc[0]
    assert 'local ' in past and '; UT ' in past
    assert 'local ' in renewed and '; UT ' in renewed
    rendered = '\n'.join(
        str(node.value) for kind in ('markdown', 'caption', 'info')
        for node in getattr(at.main, kind)
    )
    assert 'This limited reading checks whole-sign co-presence, square or opposition' in rendered
    assert engine['SAHL_1_29_13'] in rendered
    assert engine['SAHL_1_29_FN304'] in rendered


def test_findings_page_renders_unavailable_leap_anniversaries_without_losing_natal_moon(
        ):
    at = make_app(date='2024-02-29', page='findings').run()
    assert_no_exception(at, 'leap-day gestation')
    fetus = find_table(at, "The fetus's stay (Sahl)").value
    natal = fetus.loc[fetus['Item'] == 'The Moon of the nativity (1.9, 1)', 'Value'].iloc[0]
    past = fetus.loc[fetus['Item'] == 'The past Moon, a year before (1.9, 1)', 'Value'].iloc[0]
    renewed = fetus.loc[fetus['Item'] == 'The renewed Moon, a year after (1.9, 1)', 'Value'].iloc[0]
    assert isinstance(natal, str) and '°' in natal
    assert 'Unavailable' in past and 'same-date convention' in past
    assert 'Unavailable' in renewed and 'same-date convention' in renewed
