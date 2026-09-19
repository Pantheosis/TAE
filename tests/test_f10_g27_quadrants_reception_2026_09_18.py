"""F10 G27: separate divided-house strength, quarter gender, and topical place."""

import pytest

from conftest import assert_no_exception, make_app


JD = 2451545.0
CUSPS_FEMININE_NINTH = [320.0, 350.0, 20.0, 50.0, 80.0, 110.0,
                         140.0, 170.0, 200.0, 230.0, 260.0, 290.0]
CUSPS_MASCULINE_SIGN = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0,
                         170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
CUSPS_WHOLE_SIGN_NINTH = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0,
                           170.0, 200.0, 220.0, 230.0, 270.0, 310.0]


def _planetary_data(**positions):
    defaults = {
        'Sun': (20.0, 1.0), 'Moon': (80.0, 13.0),
        'Mercury': (140.0, 1.2), 'Venus': (227.0, 1.1),
        'Mars': (170.0, 0.7), 'Jupiter': (280.0, 0.08),
        'Saturn': (310.0, 0.03), 'North Node': (30.0, -0.05),
    }
    defaults.update(positions)
    return {
        name: {
            'longitude': float(lon), 'latitude': 0.0, 'distance': 1.0,
            'speed_in_lon': float(speed), 'speed_in_lat': 0.0,
            'speed_in_dist': 0.0,
        }
        for name, (lon, speed) in defaults.items()
    }


def _condition(engine, cusps, sect='Diurnal', **positions):
    data = _planetary_data(**positions)
    essential = engine['evaluate_essential_dignities'](data, sect)
    accidental = engine['evaluate_accidental_dignities'](data, cusps, sect, JD)
    return engine['evaluate_abu_mashar_condition'](
        data, cusps, sect, essential, accidental, JD, cusps[0])


def _has(labels, paragraph):
    return any(f'({paragraph})' in label for label in labels)


@pytest.mark.parametrize('cusp_index', [0, 3, 6, 9])
@pytest.mark.parametrize('distance,carried', [(4.999, True), (5.0, True), (5.001, False)])
def test_five_degree_allowance_is_inclusive_at_each_stake_only(
        engine, cusp_index, distance, carried):
    cusps = [float(value) for value in range(10, 370, 30)]
    angle = cusps[cusp_index]
    longitude = (angle - distance) % 360.0
    strict = engine['get_house_number'](longitude, cusps)
    effective = engine['get_effective_house'](longitude, cusps)
    expected_angle_house = cusp_index + 1
    expected_strict = cusp_index if cusp_index else 12
    assert strict == expected_strict
    assert (effective == expected_angle_house) is carried
    if not carried:
        assert effective == strict


def test_five_degree_allowance_wraps_at_zero_and_skips_intermediate_cusps(engine):
    cusps = [float(value) for value in range(0, 360, 30)]
    assert engine['get_house_number'](355.0, cusps) == 12
    assert engine['get_effective_house'](355.0, cusps) == 1
    assert engine['get_effective_house'](354.999, cusps) == 12
    assert engine['get_house_number'](29.0, cusps) == 1
    assert engine['get_effective_house'](29.0, cusps) == 1


@pytest.mark.parametrize('cusp_index', [0, 3, 6, 9])
@pytest.mark.parametrize('distance,carried', [(4.999, True), (5.0, True), (5.001, False)])
def test_stake_allowance_crosses_a_narrow_intermediate_division(
        engine, cusp_index, distance, carried):
    cusps = [float(value) for value in range(0, 360, 30)]
    previous_idx = (cusp_index - 1) % 12
    cusps[previous_idx] = (cusps[cusp_index] - 2.0) % 360.0
    longitude = (cusps[cusp_index] - distance) % 360.0
    raw = engine['get_house_number'](longitude, cusps)
    effective = engine['get_effective_house'](longitude, cusps)
    stake_house = cusp_index + 1
    assert raw not in (stake_house, previous_idx + 1)
    assert (effective == stake_house) is carried
    if not carried:
        assert effective == raw
    # The retained all-cusp mode still carries only to the narrow cusp that
    # ends the raw division; it does not jump across it to the stake.
    assert engine['get_effective_house'](
        longitude, cusps, angles_only=False) == previous_idx + 1


def test_narrow_pre_mc_allowance_reaches_the_strength_evaluator(engine):
    cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0,
             180.0, 210.0, 268.0, 270.0, 300.0, 330.0]
    data = _planetary_data(Venus=(267.0, 1.1))
    essential = engine['evaluate_essential_dignities'](data, 'Diurnal')
    accidental = engine['evaluate_accidental_dignities'](data, cusps, 'Diurnal', JD)
    rows = engine['evaluate_strength_of_planets'](
        data, essential, accidental, cusps[0], 'Diurnal', cusps)
    venus = next(row for row in rows if row['Planet'] == 'Venus')
    testimony = next(row for row in venus['Testimonies'] if row['n'] == '83')
    assert 'into the 10th' in testimony['sentence']
    assert 'Quadrant division, strict: 8' in testimony['facts']
    position = engine['quadrant_strength_position'](267.0, cusps)
    assert position == {
        'division': 8, 'strength_house': 10, 'strength': 'stake or following',
        'quarter_gender': 'Feminine', 'carried': True,
    }
    assert engine['get_wsh_house'](267.0, cusps[0]) == 9


def test_quarter_gender_uses_actual_angle_boundaries_without_allowance(engine):
    cusps = [float(value) for value in range(10, 370, 30)]
    before_mc = engine['quadrant_strength_position'](99.0, cusps)
    on_mc = engine['quadrant_strength_position'](100.0, cusps)
    assert before_mc == {
        'division': 3, 'strength_house': 4, 'strength': 'stake or following',
        'quarter_gender': 'Feminine', 'carried': True,
    }
    assert on_mc['division'] == 4 and on_mc['quarter_gender'] == 'Masculine'
    before_asc = engine['quadrant_strength_position'](9.0, cusps)
    on_asc = engine['quadrant_strength_position'](10.0, cusps)
    assert before_asc['division'] == 12 and before_asc['quarter_gender'] == 'Masculine'
    assert on_asc['division'] == 1 and on_asc['quarter_gender'] == 'Feminine'


def test_venus_before_mc_uses_one_adjusted_class_but_its_actual_feminine_quarter(engine):
    condition = _condition(engine, CUSPS_FEMININE_NINTH)['Venus']
    assert _has(condition['Positive Labels'], '26')
    assert not _has(condition['Negative Labels'], '39')
    assert not _has(condition['Negative Labels'], '46')
    position = engine['quadrant_strength_position'](227.0, CUSPS_FEMININE_NINTH)
    assert position['division'] == 9 and position['strength_house'] == 10
    assert position['quarter_gender'] == 'Feminine'

    data = _planetary_data()
    essential = engine['evaluate_essential_dignities'](data, 'Diurnal')
    accidental = engine['evaluate_accidental_dignities'](
        data, CUSPS_FEMININE_NINTH, 'Diurnal', JD)
    strength = engine['evaluate_strength_of_planets'](
        data, essential, accidental, CUSPS_FEMININE_NINTH[0],
        'Diurnal', CUSPS_FEMININE_NINTH)
    venus = next(row for row in strength if row['Planet'] == 'Venus')
    assert _has(venus['Labels'], '88')
    testimony = next(row for row in venus['Testimonies'] if row['n'] == '88')
    assert 'Quadrant division, strict: 9' in testimony['facts']


def test_masculine_sign_stake_fixture_keeps_strength_separate_from_sahl_88(engine):
    data = _planetary_data(Venus=(257.0, 1.1))
    essential = engine['evaluate_essential_dignities'](data, 'Diurnal')
    accidental = engine['evaluate_accidental_dignities'](
        data, CUSPS_MASCULINE_SIGN, 'Diurnal', JD)
    strength = engine['evaluate_strength_of_planets'](
        data, essential, accidental, CUSPS_MASCULINE_SIGN[0],
        'Diurnal', CUSPS_MASCULINE_SIGN)
    venus = next(row for row in strength if row['Planet'] == 'Venus')
    assert not _has(venus['Labels'], '88')
    condition = _condition(
        engine, CUSPS_MASCULINE_SIGN, Venus=(257.0, 1.1))['Venus']
    assert _has(condition['Positive Labels'], '26')
    assert not _has(condition['Negative Labels'], '39')


@pytest.mark.parametrize(
    'longitude,quarter_matches,sign_matches,earns_88',
    [
        (45.0, True, True, True),    # feminine quarter, Taurus
        (15.0, True, False, False),  # feminine quarter, Aries
        (105.0, False, True, False), # masculine quarter, Cancer
        (135.0, False, False, False),# masculine quarter, Leo
    ],
)
def test_sahl_88_requires_the_complete_quarter_and_sign_conjunction(
        engine, longitude, quarter_matches, sign_matches, earns_88):
    cusps = [float(value) for value in range(0, 360, 30)]
    data = _planetary_data(Venus=(longitude, 1.1))
    essential = engine['evaluate_essential_dignities'](data, 'Diurnal')
    accidental = engine['evaluate_accidental_dignities'](data, cusps, 'Diurnal', JD)
    rows = engine['evaluate_strength_of_planets'](
        data, essential, accidental, cusps[0], 'Diurnal', cusps)
    venus = next(row for row in rows if row['Planet'] == 'Venus')
    position = engine['quadrant_strength_position'](longitude, cusps)
    sign = engine['get_zodiac_sign'](longitude)
    assert (position['quarter_gender'] == 'Feminine') is quarter_matches
    assert (sign in engine['FEMININE_SIGNS']) is sign_matches
    assert _has(venus['Labels'], '88') is earns_88


def test_saturn_before_mc_keeps_strength_and_actual_quarter_weakness_distinct(engine):
    condition = _condition(
        engine, CUSPS_FEMININE_NINTH, Saturn=(227.0, 0.03))['Saturn']
    assert _has(condition['Positive Labels'], '26')
    assert not _has(condition['Negative Labels'], '39')
    assert not _has(condition['Negative Labels'], '28')
    assert any('feminine quadrant (45)' in label for label in condition['Negative Labels'])


def test_outside_allowance_is_falling_even_when_whole_sign_place_is_angular(engine):
    condition = _condition(
        engine, CUSPS_FEMININE_NINTH, Venus=(215.0, 1.1))['Venus']
    assert not _has(condition['Positive Labels'], '26')
    assert _has(condition['Negative Labels'], '39')
    assert engine['get_wsh_house'](215.0, CUSPS_FEMININE_NINTH[0]) == 10


def test_past_mc_is_strong_and_masculine_even_in_whole_sign_ninth(engine):
    condition = _condition(
        engine, CUSPS_WHOLE_SIGN_NINTH, Venus=(232.0, 1.1))['Venus']
    assert _has(condition['Positive Labels'], '26')
    assert not _has(condition['Negative Labels'], '39')
    position = engine['quadrant_strength_position'](232.0, CUSPS_WHOLE_SIGN_NINTH)
    assert position['division'] == 10 and position['quarter_gender'] == 'Masculine'
    assert engine['get_wsh_house'](232.0, CUSPS_WHOLE_SIGN_NINTH[0]) == 9


def test_sun_ninth_exception_uses_raw_division_before_allowance(engine):
    raw_ninth = _condition(
        engine, CUSPS_FEMININE_NINTH, Sun=(227.0, 1.0))['Sun']
    assert _has(raw_ninth['Positive Labels'], '26')
    assert not _has(raw_ninth['Negative Labels'], '45')

    raw_tenth_whole_sign_ninth = _condition(
        engine, CUSPS_WHOLE_SIGN_NINTH, Sun=(232.0, 1.0))['Sun']
    assert engine['get_wsh_house'](232.0, CUSPS_WHOLE_SIGN_NINTH[0]) == 9
    assert any(label.startswith('Sun, feminine sign (45)')
               for label in raw_tenth_whole_sign_ninth['Negative Labels'])


def test_topical_whole_sign_house_and_joy_do_not_follow_quadrant_cusps(engine):
    data = _planetary_data(Venus=(125.0, 1.1))
    regular = [float(value) for value in range(0, 360, 30)]
    distorted = [0.0, 15.0, 55.0, 91.0, 119.0, 151.0,
                 180.0, 205.0, 244.0, 276.0, 302.0, 331.0]
    first = engine['evaluate_accidental_dignities'](data, regular, 'Diurnal', JD)['Venus']
    second = engine['evaluate_accidental_dignities'](data, distorted, 'Diurnal', JD)['Venus']
    assert first['House'] == second['House'] == 5
    assert first['Joy'] is second['Joy'] is True


def _reception_data(**positions):
    defaults = {
        'Sun': (20.0, 1.0), 'Moon': (215.0, 13.0),
        'Mercury': (140.0, 1.2), 'Venus': (250.0, 1.1),
        'Mars': (218.0, 0.7), 'Jupiter': (280.0, 0.08),
        'Saturn': (310.0, 0.03),
    }
    defaults.update(positions)
    return _planetary_data(**defaults)


def _sahl_reception(engine, data, sect='Diurnal'):
    run = engine['_RUN']
    had_override = hasattr(run, 'CONNECTION_PROFILE')
    previous = getattr(run, 'CONNECTION_PROFILE', None)
    try:
        engine['set_readings'](CONNECTION_PROFILE=engine['SAHL'])
        return (engine['evaluate_reception'](data, sect),
                engine['evaluate_non_reception'](data, sect))
    finally:
        if had_override:
            engine['set_readings'](CONNECTION_PROFILE=previous)
        else:
            delattr(run, 'CONNECTION_PROFILE')


@pytest.mark.parametrize(
    'data,received,receiver',
    [(_reception_data(), 'Moon', 'Mars'),
     (_reception_data(Moon=(280.0, 13.0), Jupiter=(283.0, 0.08),
                      Saturn=(285.0, 0.03)), 'Jupiter', 'Saturn')],
)
def test_kind_v_keeps_reception_and_names_the_applicants_fall(
        engine, data, received, receiver):
    reception, non_reception = _sahl_reception(engine, data)
    assert any(row['Kind'].startswith('V ') and row['Connecting'] == received
               and row['With'] == receiver for row in non_reception)
    row = next(row for row in reception
               if row.get('Received') == received and row.get('Receiver') == receiver)
    assert "brought down, the receiver in the applicant's fall (62)" in row['Grade']


def test_kind_iv_reason_remains_distinct_and_kinds_ii_iii_still_refuse(engine):
    reception, _non = _sahl_reception(
        engine, _reception_data(Moon=(215.0, 13.0), Mars=(100.0, 0.7)))
    moon_mars = next(row for row in reception
                     if row.get('Received') == 'Moon' and row.get('Receiver') == 'Mars')
    assert 'receiver in its own fall (62)' in moon_mars['Grade']
    assert "applicant's fall" not in moon_mars['Grade']

    kind_ii, _ = _sahl_reception(
        engine, _reception_data(Moon=(95.0, 13.0), Mars=(98.0, 0.7)), 'Nocturnal')
    assert not any(row.get('Received') == 'Moon' and row.get('Receiver') == 'Mars'
                   for row in kind_ii)
    kind_iii, _ = _sahl_reception(
        engine, _reception_data(Moon=(218.0, 13.0), Venus=(221.0, 1.1)))
    assert not any(row.get('Received') == 'Moon' and row.get('Receiver') == 'Venus'
                   for row in kind_iii)


def test_configurations_page_discloses_g27_measurements_and_reception_behavior(engine):
    at = make_app(date='1240-05-25', page='configurations').run()
    assert_no_exception(at, 'G27 configurations')
    rendered = '\n'.join(
        str(node.value) for kind in ('markdown', 'caption', 'info')
        for node in getattr(at.main, kind)
    )
    assert engine['QUADRANT_GENDER_READER'] in rendered
    assert engine['SUN_NINTH_EXCEPTION_READER'] in rendered
    assert "fn 231 also leaves a whole-sign reading of 39 open" in rendered
    assert 'Kind IV and Kind V keep the reception row but mark it brought down' in rendered
