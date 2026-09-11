"""Astra's adversarial engine audit of 2026-09-11, as regression tests.

The 23 expectations of `process/astra_2026-09-11/ENGINE_AUDIT.md` (appendix
harness), one test each, adopted BEFORE the fixes as the audit instructs
("add the numerical/source examples as regression cases before changing the
affected calculations"). Each is a source-derived expectation, not a pin of
the old behaviour; the source is named in the docstring. F14 and C01-C05
are provenance/policy items and have no numerical test here beyond the
audit's own controls.

Interfaces changed by the repair are adapted as the audit allows ("adapt
the harness to the new input interfaces while preserving the source-derived
expected outcomes"): F01's offset case goes through the repaired calendar
adapter, and F04 passes the chart's horizon (ARMC, obliquity, latitude).
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
import swisseph as swe


def P(lon, speed=1.0, lat=0.0):
    return dict(longitude=float(lon), latitude=float(lat), distance=1.0,
                speed_in_lon=float(speed), speed_in_lat=0.0, speed_in_dist=0.0)


def fixture(**overrides):
    p = {n: P(l, v) for n, l, v in [
        ('Sun', 280, 1), ('Moon', 160, 13), ('Mercury', 270, 1.2),
        ('Venus', 300, 1.1), ('Mars', 210, .5), ('Jupiter', 90, .08),
        ('Saturn', 330, .03), ('North Node', 200, -.05)]}
    p.update(overrides)
    return p


def linear_ephemeris(engine, p):
    ids = {engine['PLANET_SWE_IDS'][n]: v for n, v in p.items()}

    def calc(t, who, *args):
        v = ids[who]
        return ((v['longitude'] + t * v['speed_in_lon']) % 360, 0, 1, v['speed_in_lon'], 0, 0), 260
    return calc


# --- F01: the Julian calendar (Swiss Ephemeris manual s.9.1; JUL_CAL) --------

def test_f01_julian_only_leap_day_is_a_valid_date(engine):
    """1300-02-29 exists in the Julian calendar, which is the calendar the
    engine reads pre-1582 digits in; proleptic-Gregorian datetime rejects it."""
    got = engine['parse_iso_date']('1300-02-29')
    assert got is not None and (got.year, got.month, got.day) == (1300, 2, 29)


def test_f01_jd_of_a_julian_leap_day_round_trips(engine):
    j = swe.julday(1300, 2, 29, 12, swe.JUL_CAL)
    got = engine['pn4_datetime_from_jd'](j)
    assert (got.year, got.month, got.day) == (1300, 2, 29)


def test_f01_offset_arithmetic_stays_in_the_julian_calendar(engine):
    """Local Julian 1300-03-01 00:30 at +02:00 is UT 1300-02-29 22:30 -- a
    date datetime cannot hold. The repaired adapter carries the JD."""
    expected = swe.julday(1300, 3, 1, 0.5, swe.JUL_CAL) - 2 / 24
    jd = engine['civil_local_to_jd_ut'](1300, 3, 1, 0.5, 2.0)
    assert abs(jd - expected) < 1e-8
    chart = engine['calculate_traditional_chart_jd'](jd, 0, 30)
    assert abs(chart['julian_day'] - expected) < 1e-8


# --- F02, F03, F11: the timing clocks (PN IV IV.1, 5-6, 11; III.1, 13; I.2, 1-4; I.6, 6) ---

@pytest.fixture(scope='module')
def equator_chart(engine):
    return engine['calculate_traditional_chart'](datetime(2000, 1, 1, 12), 0, 0)


def test_f02_fardar_subperiod_changes_at_its_fractional_end(engine, equator_chart):
    """IV.1, 11: the Sun's first seventh is '1 year, 5 months, 4 days, and
    approximately 6 hours'; at 1.4976 elapsed years Venus is sub-lord."""
    b = engine['pn4_timing_bundle'](equator_chart, 0, 0, date(2000, 1, 1), date(2001, 7, 1), 'forward')
    assert b['fardar']['sub_lord'] == 'Venus', b['fardar']


def test_f02_distribution_changes_at_its_fractional_end(engine, equator_chart):
    """III.1, 13: a degree a year, 5' a month -- the distributor changes
    within the year (Figure 22 dates a change mid-year)."""
    b = engine['pn4_timing_bundle'](equator_chart, 0, 0, date(2000, 1, 1), date(2012, 10, 21), 'forward')
    assert b['current']['distributor'] == 'Saturn', b['current']


def test_f03_the_current_revolution_is_not_in_the_future(engine):
    """I.2, 1-3: the year concludes when the Sun returns; a target before
    this year's return belongs to the preceding cycle, in its month 12."""
    c3 = engine['calculate_traditional_chart'](datetime(2000, 1, 1, 23), 43.7792, 11.2463)
    b3 = engine['pn4_timing_bundle'](c3, 43.7792, 11.2463, date(2000, 1, 1), date(2003, 1, 1), 'forward')
    assert b3['jd_sr'] <= 2452641.0 and b3['month'] == 12, (b3['jd_sr'], b3['month'], b3['day_of_year'])


def test_f11_active_point_is_the_degree_reached_not_the_segment_start(engine, equator_chart):
    """I.6, 6 with fn 34: 'the very degree which the distribution had
    reached'. At age 1 the direction stands a degree of ascension past the
    Ascendant, not on the bound's opening degree."""
    b1 = engine['pn4_timing_bundle'](equator_chart, 0, 0, date(2000, 1, 1), date(2001, 1, 1), 'forward')
    elapsed = (b1['jd_target'] - equator_chart['julian_day']) / engine['PN4_DIRECTION_YEAR_DAYS']
    oa = engine['_oblique_ascension'](equator_chart['ascendant'], equator_chart['obliquity'], 0)
    endpoint = engine['_lon_with_oblique_ascension'](oa + elapsed, equator_chart['obliquity'], 0)
    assert b1['year_rows'][1]['Active point'] == engine['get_degree_string'](endpoint), \
        (b1['year_rows'][1]['Active point'], endpoint)


# --- F04: hayz by the actual horizon (Gr. Intr. VII.1, 37-39; VII.6, 13) ----

def test_f04_hayz_uses_the_planets_altitude_not_its_longitude(engine):
    c4 = engine['calculate_traditional_chart'](datetime(2000, 1, 1, 1, 40), 51.5, 0)
    p = c4['planetary_data']
    jup = p['Jupiter']
    lam, beta, eps, theta, phi = map(math.radians,
                                     [jup['longitude'], jup['latitude'], c4['obliquity'], c4['armc'], 51.5])
    x = math.cos(beta) * math.cos(lam)
    y = math.cos(beta) * math.sin(lam) * math.cos(eps) - math.sin(beta) * math.sin(eps)
    z = math.cos(beta) * math.sin(lam) * math.sin(eps) + math.sin(beta) * math.cos(eps)
    sinalt = math.sin(phi) * z + math.cos(phi) * (math.cos(theta) * x + math.sin(theta) * y)
    assert sinalt < 0 and c4['sect'] == 'Nocturnal' and 0 < jup['longitude'] < 30
    acc = engine['evaluate_accidental_dignities'](p, c4['houses'], c4['sect'], c4['julian_day'],
                                                  armc=c4['armc'], obliquity=c4['obliquity'], geo_lat=51.5)
    assert acc['Jupiter']['Hayz'] is True, {'Hayz': acc['Jupiter']['Hayz'],
                                            'altitude': math.degrees(math.asin(sinalt))}


# --- F05, F06, F07: ordered events (Gr. Intr. VII.5, 117-119; PN IV II.22, 1-4) ---

def test_f05_no_escape_when_the_original_contact_comes_first_synthetic(engine):
    p = {'Moon': P(1, 13), 'Mars': P(29, .5), 'Saturn': P(40, .03)}
    with patch.object(swe, 'calc_ut', linear_ephemeris(engine, p)):
        sim = engine['_simulate_forward_uncached'](p, 0, horizon_days=6, step_days=.1)
        rows = engine['evaluate_escape'](p, sim)
    bad = [r for r in rows if r['Planet'] == 'Moon' and r['Escaped'] == 'Mars'
           and r['Connected Instead With'] == 'Saturn']
    assert not bad, bad


def test_f05_no_escape_when_the_original_contact_comes_first_real(engine):
    p = {}
    for name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
        xx, _ = swe.calc_ut(2451587.0, engine['PLANET_SWE_IDS'][name])
        p[name] = dict(zip(['longitude', 'latitude', 'distance', 'speed_in_lon',
                            'speed_in_lat', 'speed_in_dist'], xx))
    sim = engine['_simulate_forward_uncached'](p, 2451587.0, horizon_days=100, step_days=1)
    bad = [r for r in engine['evaluate_escape'](p, sim) if r['Planet'] == 'Mars'
           and r['Escaped'] == 'Jupiter' and r['Connected Instead With'] == 'Moon']
    assert not bad, (bad, engine['_body_union_day'](sim, 'Mars', 'Jupiter'),
                     engine['_body_union_day'](sim, 'Mars', 'Moon', after_day=39.6))


def test_f06_a_contact_minutes_before_the_ingress_is_found(engine):
    p = {'Moon': P(29.636, 13), 'Sun': P(89.948, 1)}
    with patch.object(swe, 'calc_ut', linear_ephemeris(engine, p)):
        sim = engine['_simulate_forward_uncached'](p, 0, horizon_days=1, step_days=.25)
        exit_day = sim['events']['Moon']['sign_exits'][0]
        contact = engine['_perfection_day'](sim, 'Moon', 'Sun', 60, before_day=exit_day)
    assert contact is not None, (exit_day, contact)
    assert abs(exit_day - 0.028) < 1e-3, exit_day


def test_f07_a_retrograde_excursion_across_a_sign_boundary_is_two_crossings(engine):
    def retro_ephemeris(t, who, *args):
        return (29.99 + .12 * t - .12 * t * t, 0, 1, .12 - .24 * t, 0, 0), 260
    with patch.object(swe, 'calc_ut', retro_ephemeris):
        sim = engine['_simulate_forward_uncached']({'Mercury': P(29.99, .12)}, 0,
                                                   horizon_days=1, step_days=1)
    crossings = sim['events']['Mercury']['sign_exits']
    assert len(crossings) == 2, sim['events']['Mercury']
    assert crossings[0] == pytest.approx((1 - math.sqrt(2 / 3)) / 2, abs=1e-3)
    assert crossings[1] == pytest.approx((1 + math.sqrt(2 / 3)) / 2, abs=1e-3)


# --- F08: Sahl, Introduction 3, 97 "separating from a planet receiving it" ---

@pytest.mark.parametrize('tag, p, expected_word', [
    ('missing', fixture(Moon=P(190.5, 13), Venus=P(190, 1)), 'venus'),
    ('reversed', fixture(Moon=P(95.5, 13), Saturn=P(95, .03), Jupiter=P(120, .08)), 'saturn'),
])
def test_f08_the_receiver_is_judged_at_the_departing_planets_degree(engine, tag, p, expected_word):
    """3, 52: Mars receives the Moon in Aries 'because [Aries] is his
    house' -- the receiver owns a dignity at the RECEIVED planet's place."""
    ess = engine['evaluate_essential_dignities'](p, 'Diurnal')
    acc = engine['evaluate_accidental_dignities'](p, tuple(range(0, 360, 30)), 'Diurnal')
    rows = engine['evaluate_weakness_of_planets'](p, ess, acc, 0, 'Diurnal')
    labels = next(r['Labels'] for r in rows if r['Planet'] == 'Moon')
    hit = any(x.startswith('Separating from') and expected_word in x.lower() for x in labels)
    assert (hit if tag == 'missing' else not hit), labels


# --- F09: Gr. Intr. VII.5, 16 and 34 -- separated at 1' or less past exact ---

def test_f09_eighteen_arcseconds_past_exact_is_separated(engine):
    r = engine['_pairwise_configurations']({'Moon': P(10.005, 13), 'Saturn': P(10, .03)})[0]
    assert r['motion'] == 'Separating'
    assert not engine['_is_connected_abu_mashar'](r)


# --- F10: Gr. Intr. VII.2, 11-14 and 40-41 -- the eastern phase is left when its degrees are COMPLETED ---

@pytest.mark.parametrize('name, lon, want', [
    ('Saturn', 94, 'Under the rays'), ('Saturn', 85, None),
    ('Mars', 90, 'Under the rays'), ('Mars', 82, None),
    ('Mercury', 93, 'Under the rays'), ('Mercury', 88, None),
])
def test_f10_eastern_thresholds_are_exclusive_at_completion(engine, name, lon, want):
    got = engine['solar_phase'](name, lon, 100)[0]
    assert got == want, (got, want)


def test_f10_control_the_western_threshold_stays_inclusive(engine):
    """VII.2, 31-34: the western phases are entered AT their degrees."""
    assert engine['solar_phase']('Saturn', 106, 100)[0] == 'Burned'


# --- F12, F13: boundary ownership and sexagesimal display ------------------

def test_f12_a_fardar_subperiod_does_not_own_its_own_end(engine):
    r = engine['pn4_fardar_at_age'](4.0, 'Diurnal')
    r2 = engine['pn4_fardar_at_age'](r['sub_to'], 'Diurnal')
    assert r2['sub_lord'] == 'Moon', r2


def test_f13_a_whole_entered_minute_survives_display(engine):
    assert engine['get_degree_string'](30 + 1 / 60) == "00° Tau 01'"
    assert engine['get_degree_string'](360) == "00° Ari 00'"
    assert engine['get_degree_string'](-1 / 60) == "29° Pis 59'"


# --- The audit's passing controls, kept as pins ----------------------------

def test_control_twelfth_part_formula(engine):
    assert engine['pn4_twelfth_part'](35.25) == 93


def test_control_wells_count_is_sixty_four(engine):
    assert sum(map(len, engine['WELLED_DEGREES'].values())) == 64


def test_control_twenty_five_thirds_are_one_symbolic_hour(engine):
    assert engine['pn4_arc_to_time'](25 / 216000)['hours'] == 1
