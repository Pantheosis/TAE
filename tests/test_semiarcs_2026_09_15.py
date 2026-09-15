"""Proportional semi-arc directions, III.1, 12's third case (reconciliation
decision 5, 2026-09-15): the method al-Qabisi states (Introduction IV.11-12,
ITA VIII.2.2, pp. 362-364) and Dykes works (ITA Appendix E, pp. 402-407).

The fixture is Dykes's own worked example, p. 406 (A, with the planets'
latitudes) and p. 407 (B, zodiacal degrees only): the chart of 4 September
2010, 2:15:09 PM CDT (+5), Minneapolis, 93w15'49", 44n58'48" (the figure on
p. 402), Venus (promittor) directed to Saturn (significator). His printed
values, which the engine must reproduce from the chart cast here:

    A (p. 406)                          B (p. 407)
    RAMC     179 19' 33"                179 19' 33"
    RA Venus 203 43' 00"                205 00' 51"
    RA Sat   185 02' 49"                184 11' 10"
    MD Venus  24 23' 27"                 25 41' 18"
    MD Sat     5 43' 16"                  4 51' 37"
    DSA Venus 75 57' 21"                 79 26' 40"
    DSA Sat   90 10' 46"                 88 11' 16"
    Arc       19 34' 20"                 21 18' 36"

    "PromMD - [(SigMD/SigSA) * PromSA] = Arc" (p. 404)
"""
from datetime import datetime

import pytest


def dms(d, m, s):
    return d + m / 60.0 + s / 3600.0


# Dykes's chart (ITA p. 402): 2010-09-04 14:15:09 CDT = 19:15:09 UT.
DYKES_UT = datetime(2010, 9, 4, 19, 15, 9)
DYKES_LAT = dms(44, 58, 48)
DYKES_LON = -dms(93, 15, 49)
SECOND = 1.0 / 3600.0

DYKES_A = dict(ramc=dms(179, 19, 33), ra_prom=dms(203, 43, 0), ra_sig=dms(185, 2, 49),
               md_prom=dms(24, 23, 27), md_sig=dms(5, 43, 16), sa_prom=dms(75, 57, 21), sa_sig=dms(90, 10, 46),
               arc=dms(19, 34, 20))
DYKES_B = dict(ramc=dms(179, 19, 33), ra_prom=dms(205, 0, 51), ra_sig=dms(184, 11, 10),
               md_prom=dms(25, 41, 18), md_sig=dms(4, 51, 37), sa_prom=dms(79, 26, 40), sa_sig=dms(88, 11, 16),
               arc=dms(21, 18, 36))


@pytest.fixture(scope="module")
def dykes_chart(engine):
    return engine["calculate_traditional_chart"](DYKES_UT, DYKES_LAT, DYKES_LON)


def _direct(engine, chart, with_latitude):
    venus, saturn = chart["planetary_data"]["Venus"], chart["planetary_data"]["Saturn"]
    lat = (lambda p: p["latitude"]) if with_latitude else (lambda p: 0.0)
    return engine["semi_arc_direction"](saturn["longitude"], lat(saturn), venus["longitude"], lat(venus),
                                        chart["armc"], DYKES_LAT, chart["obliquity"])


def test_the_chart_is_dykes_figure(dykes_chart):
    """The figure on p. 402: Saturn 4 Libra 33, Venus 26 Libra 57, MC 29 Virgo 15, Ascendant 7 Sagittarius 47."""
    pdata = dykes_chart["planetary_data"]
    assert pdata["Saturn"]["longitude"] == pytest.approx(180 + dms(4, 33, 0), abs=1 / 60)
    assert pdata["Venus"]["longitude"] == pytest.approx(180 + dms(26, 57, 0), abs=1 / 60)
    assert dykes_chart["mc"] == pytest.approx(150 + dms(29, 15, 0), abs=1 / 60)
    assert dykes_chart["ascendant"] == pytest.approx(240 + dms(7, 47, 0), abs=1 / 60)


@pytest.mark.parametrize("with_latitude,printed", [(True, DYKES_A), (False, DYKES_B)],
                         ids=["A: with latitude (p. 406)", "B: degrees only (p. 407)"])
def test_appendix_e_example_reproduces_every_printed_term_and_the_arc(engine, dykes_chart, with_latitude, printed):
    """(a) Every term Dykes prints and both arcs, to the arc-second (he
    prints to the second; the tolerance is one second, well inside the
    0.1 degree asked for)."""
    d = _direct(engine, dykes_chart, with_latitude)
    assert dykes_chart["armc"] == pytest.approx(printed["ramc"], abs=SECOND)
    assert d["meridian"] == "upper" and d["significator"]["above"] and d["promittor"]["above"]
    assert d["promittor"]["ra"] == pytest.approx(printed["ra_prom"], abs=SECOND)
    assert d["significator"]["ra"] == pytest.approx(printed["ra_sig"], abs=SECOND)
    assert d["prom_md"] == pytest.approx(printed["md_prom"], abs=SECOND)
    assert d["sig_md"] == pytest.approx(printed["md_sig"], abs=SECOND)
    assert d["prom_sa"] == pytest.approx(printed["sa_prom"], abs=2 * SECOND)
    assert d["sig_sa"] == pytest.approx(printed["sa_sig"], abs=SECOND)
    assert d["arc"] == pytest.approx(printed["arc"], abs=SECOND)
    assert d["arc"] == pytest.approx(printed["arc"], abs=0.1)
    assert d["refused"] is None


def test_the_formula_on_dykes_printed_inputs_gives_his_arc():
    """The formula itself, p. 404, on the printed terms alone: A and B."""
    for p in (DYKES_A, DYKES_B):
        assert p["md_prom"] - (p["md_sig"] / p["sa_sig"]) * p["sa_prom"] == pytest.approx(p["arc"], abs=SECOND)


def test_a_significator_on_the_meridian_gives_the_promittors_meridian_distance(engine, dykes_chart):
    """(b) A point ON the Midheaven has MD 0, so the arc reduces to the
    promittor's own meridian distance -- the direction to the Midheaven by
    right ascension, III.1, 12's second case."""
    eps, armc, lat = dykes_chart["obliquity"], dykes_chart["armc"], DYKES_LAT
    venus = dykes_chart["planetary_data"]["Venus"]
    d = engine["semi_arc_direction"](dykes_chart["mc"], 0.0, venus["longitude"], 0.0, armc, lat, eps)
    assert d["sig_md"] == pytest.approx(0.0, abs=1e-9) and d["fraction"] == pytest.approx(0.0, abs=1e-12)
    assert d["arc"] == pytest.approx(d["prom_md"]) == pytest.approx(DYKES_B["md_prom"], abs=SECOND)
    assert d["arc"] == pytest.approx((engine["_ra_decl"](venus["longitude"], eps)[0] - armc) % 360.0)
    # and the fourth: the lower meridian, the nocturnal semi-arcs
    below = engine["semi_arc_direction"](dykes_chart["ic"], 0.0, (dykes_chart["ic"] + 20.0) % 360.0, 0.0, armc, lat, eps)
    assert below["meridian"] == "lower" and below["sig_md"] == pytest.approx(0.0, abs=1e-9)
    assert below["arc"] == pytest.approx(below["prom_md"])


def test_a_significator_on_the_horizon_gives_the_promittors_horizon(engine, dykes_chart):
    """(c) A point on the eastern horizon has MD = SA (the share is 1), so
    the arc is the promittor's distance from its own rising -- the direction
    to the Ascendant by oblique ascension, III.1, 12's first case."""
    eps, armc, lat = dykes_chart["obliquity"], dykes_chart["armc"], DYKES_LAT
    asc = dykes_chart["ascendant"]
    oa = lambda lon: engine["_oblique_ascension"](lon, eps, lat)
    for prom_lon in (asc + 20.0, asc + 75.0, asc - 30.0):
        d = engine["semi_arc_direction"](asc, 0.0, prom_lon % 360.0, 0.0, armc, lat, eps)
        assert abs(d["fraction"]) == pytest.approx(1.0, abs=1e-9)
        assert d["arc"] == pytest.approx((oa(prom_lon) - oa(asc)) % 360.0, abs=1e-6)
    # the western horizon: the share is -1, the arc is the promittor's setting
    dsc = dykes_chart["descendant"]
    d = engine["semi_arc_direction"](dsc, 0.0, (dsc + 20.0) % 360.0, 0.0, armc, lat, eps)
    assert d["fraction"] == pytest.approx(-1.0, abs=1e-9)
    assert d["arc"] == pytest.approx((oa(dsc + 200.0) - oa(dsc + 180.0)) % 360.0, abs=1e-6)


def test_a_point_of_declination_zero_has_two_semi_arcs_of_ninety(engine, dykes_chart):
    """(d) Symmetry: at declination 0 the ascensional difference is 0, so
    the diurnal and nocturnal semi-arcs are 90 each, at every latitude;
    elsewhere the two close to 180 exactly, day and night swapping when the
    declination changes sign."""
    eps = dykes_chart["obliquity"]
    for lat in (0.0, 30.0, DYKES_LAT, -60.0):
        for lon in (0.0, 180.0):                          # the equinoctial points
            t = engine["semi_arc_terms"](lon, 0.0, 100.0, lat, eps)
            assert t["declination"] == pytest.approx(0.0, abs=1e-9)
            assert t["diurnal_sa"] == pytest.approx(90.0) and t["nocturnal_sa"] == pytest.approx(90.0)
    north = engine["semi_arc_terms"](90.0, 0.0, 100.0, DYKES_LAT, eps)    # the summer solstice, declination +eps
    south = engine["semi_arc_terms"](270.0, 0.0, 100.0, DYKES_LAT, eps)   # the winter solstice, -eps
    assert north["diurnal_sa"] + north["nocturnal_sa"] == 180.0
    assert north["diurnal_sa"] == pytest.approx(south["nocturnal_sa"]) and north["diurnal_sa"] > 90.0
    assert north["diurnal_sa"] == pytest.approx(engine["_semiarcs"](90.0, eps, DYKES_LAT)[0])


def test_signed_meridian_distance_and_the_choice_of_meridian(engine, dykes_chart):
    """The choices the text leaves open, pinned: MD positive before the
    meridian in primary motion (Dykes's +24 23' and +5 43' east of the
    Midheaven); the significator's side of the horizon picks the meridian
    and the semi-arcs; a promittor already past the place comes round."""
    eps, armc, lat = dykes_chart["obliquity"], dykes_chart["armc"], DYKES_LAT
    terms = lambda lon: engine["semi_arc_terms"](lon, 0.0, armc, lat, eps)
    east, west = terms(dykes_chart["mc"] + 10.0), terms(dykes_chart["mc"] - 10.0)
    assert east["md_upper"] > 0 > west["md_upper"] and east["above"] and west["above"]
    below = terms(dykes_chart["ic"] - 10.0)               # past the fourth, heading to rise
    assert not below["above"] and below["md_lower"] < 0
    # Saturn above the horizon: Venus's MD from the upper meridian, diurnal arcs
    d = _direct(engine, dykes_chart, False)
    assert d["meridian"] == "upper" and d["prom_sa"] == d["promittor"]["diurnal_sa"]
    # the reverse direction, Saturn (behind Venus in the zodiac) to Venus, has passed: it comes round
    saturn, venus = dykes_chart["planetary_data"]["Saturn"], dykes_chart["planetary_data"]["Venus"]
    back = engine["semi_arc_direction"](venus["longitude"], 0.0, saturn["longitude"], 0.0, armc, lat, eps)
    assert back["raw"] < 0 and back["arc"] == pytest.approx(back["raw"] + 360.0) and back["arc"] > 300.0
    # a promittor below the horizon coming to a significator above it: its rise plus its share of its own day arc
    prom_lon = (dykes_chart["ascendant"] + 30.0) % 360.0   # in the first house, below the horizon
    d = engine["semi_arc_direction"](saturn["longitude"], 0.0, prom_lon, 0.0, armc, lat, eps)
    assert not d["promittor"]["above"] and d["meridian"] == "upper"
    oa = engine["_oblique_ascension"]
    rise = (oa(prom_lon, eps, lat) - oa(dykes_chart["ascendant"], eps, lat)) % 360.0
    assert d["arc"] == pytest.approx(rise + (1.0 - d["fraction"]) * d["prom_sa"], abs=1e-6)


def test_refusal_where_a_point_never_rises_or_sets(engine):
    """A degree that never rises or sets has no semi-arc to proportion: the
    arc is None and the sentence says which point; the distribution refuses
    above the polar circle as the Ascendant's does."""
    d = engine["semi_arc_direction"](90.0, 0.0, 100.0, 0.0, 0.0, 70.0, 23.44)   # the summer solstice at 70N
    assert d["arc"] is None and d["significator"]["circumpolar"] and "significator never rises or sets" in d["refused"]
    assert engine["pn4_distribution_by_semi_arcs"]({}, 90.0, 23.44, 70.0, 0.0) is None
    assert engine["semi_arc_direction"](0.0, 0.0, 30.0, 0.0, 0.0, 70.0, 23.44)["arc"] is not None   # both rise and set


def test_the_distribution_by_semi_arcs_dates_the_bounds_by_the_arc(engine, dykes_chart):
    """Saturn's degree distributed through the bounds: the first period is
    its own bound, every segment opens on the arc the engine gives for the
    opener's degree, and the arc to Venus's degree is Dykes's B arc (the
    body row Venus opens as partner)."""
    chart = dykes_chart
    pdata, eps, armc, lat = chart["planetary_data"], chart["obliquity"], chart["armc"], DYKES_LAT
    saturn = pdata["Saturn"]["longitude"]
    segs = engine["pn4_distribution_by_semi_arcs"](pdata, saturn, eps, lat, armc)
    assert segs and segs[0]["from"] == 0.0 and segs[0]["from_lon"] == pytest.approx(saturn)
    assert segs[0]["distributor"] == engine["pn4_bound_lord"](saturn)
    for seg in segs[1:]:
        d = engine["semi_arc_direction"](saturn, 0.0, seg["from_lon"], 0.0, armc, lat, eps)
        assert seg["from"] == pytest.approx(d["arc"], abs=1e-9)
    venus_seg = next(s for s in segs if s["partner"] == "Venus" and s["partner_aspect"] == "body")
    assert venus_seg["from"] == pytest.approx(DYKES_B["arc"], abs=SECOND)
    # the terms table beside it: the significator first, then the period's opener and the next
    cur = engine["pn4_distribution_at_age"](segs, 10.0)
    rows = engine["pn4_semi_arc_terms_rows"](saturn, eps, lat, armc, segs, cur)
    assert [r["Point"].split(":")[0] for r in rows] == ["significator", "promittor that opened the period now running",
                                                        "promittor that reached next"]
    assert rows[0]["Arc"] == "-" and rows[1]["Arc"].startswith(f"{cur['from']:.2f}")
    assert all(set(r) == {"Point", "Longitude", "Right ascension", "Declination", "Meridian distance", "Semi-arc", "Arc"}
               for r in rows)


def test_the_timing_bundle_directs_every_planet_off_an_axis_by_semi_arcs(engine, dykes_chart):
    """Dykes's chart through the page's bundle: no planet on an axial
    degree, so all seven are the third case, each with segments and terms."""
    b = engine["pn4_timing_bundle"](dykes_chart, DYKES_LAT, DYKES_LON, DYKES_UT.date(), datetime(2030, 3, 1).date(),
                                    engine["PN4_MONTHLY_TURN_OPTIONS"][0])
    aps = {ap["planet"]: ap for ap in b["angle_planets"]}
    assert set(aps) == set(engine["PN4_SEVEN"])
    for ap in aps.values():
        assert ap["axis"] is None and ap["how"] == "proportional semi-arcs" and ap["segments"] and ap["terms"]
    assert "unavailable" not in str(b["turning_rows"])
