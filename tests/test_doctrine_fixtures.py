"""Doctrinal golden fixtures with negative controls.

The other modules pin STRUCTURE -- which tables render, which columns,
which prose counts. None of them could catch an evaluator emitting a
finding the source does not support. This module runs the real
evaluators on static longitudes taken from the authors' own worked
figures, and for each figure also runs a mutation that must NOT fire.

Conventions: ``pdata(Moon=(lon, speed), ...)`` builds the minimal planet
mapping the static evaluators read; speeds default to 1.0 deg/day.
Source citations are to Sahl, The Introduction Ch.3 (Dykes) and Abu
Ma'shar, Great Introduction VII (Dykes) unless stated.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest


def pdata(**positions):
    out = {}
    for name, value in positions.items():
        lon, speed = value if isinstance(value, tuple) else (value, 1.0)
        out[name.replace("_", " ")] = {
            "longitude": float(lon), "latitude": 0.0, "distance": 1.0,
            "speed_in_lon": float(speed), "speed_in_lat": 0.0, "speed_in_dist": 0.0,
        }
    return out


# Typical daily motions, so the fixtures apply/separate the way the
# figures intend.
MOON, MERC, VENUS, MARS, JUP, SAT = 13.0, 1.2, 1.1, 0.7, 0.08, 0.03


# --- CODE-17: circular longitudes ---------------------------------------

@pytest.mark.parametrize("lon, sign", [(0.0, "Aries"), (359.999, "Pisces"), (360.0, "Aries"),
                                       (720.0, "Aries"), (-1.0, "Pisces")])
def test_get_zodiac_sign_normalises_the_circle(engine, lon, sign):
    assert engine["get_zodiac_sign"](lon) == sign


def test_public_geometry_helpers_accept_360(engine):
    assert engine["get_degree_string"](360.0) == engine["get_degree_string"](0.0)
    assert engine["get_wsh_house"](360.0, 0.0) == 1
    assert engine["get_wsh_house"](30.0, 360.0) == 2
    assert engine["get_essential_rulers"](360.0)["sign"] == "Aries"


# --- CODE-16: a tied victor's runner-up ----------------------------------

def _no_rulers(_lon):
    return {"domicile": "-", "exaltation": "-", "triplicity_day": "-", "triplicity_night": "-",
            "triplicity_participating": "-", "term": "-", "face": "-"}


def test_victor_tie_reports_a_strictly_lower_runner_up(engine):
    """Saturn and Jupiter both in house 1 (12 points), everyone else in
    house 6 (1 point): the victor is the tie, and the runner-up must be a
    planet BELOW it, not the other co-winner."""
    saved = engine["get_essential_rulers"], engine["get_wsh_house"]
    try:
        engine["get_essential_rulers"] = _no_rulers
        engine["get_wsh_house"] = lambda lon, asc: 1 if lon < 60 else 6
        seven = pdata(Saturn=0, Jupiter=30, Mars=60, Sun=90, Venus=120, Mercury=150, Moon=180)
        results = engine["evaluate_victors"](seven, 0, 0, 0, "Diurnal", {"Day Lord": None, "Hour Lord": None})
    finally:
        engine["get_essential_rulers"], engine["get_wsh_house"] = saved
    for scheme, v in results.items():
        assert v["tied"], scheme
        assert set(v["victor"].split(" / ")) == {"Saturn", "Jupiter"}, scheme
        runner = v["runner_up"].split(" (")[0]
        assert runner not in ("Saturn", "Jupiter"), f"{scheme}: runner-up is a co-winner: {v['runner_up']}"
        assert v["runner_up"].endswith("(1)"), scheme


def test_victor_runner_up_is_dash_when_everyone_ties(engine):
    saved = engine["get_essential_rulers"], engine["get_wsh_house"]
    try:
        engine["get_essential_rulers"] = _no_rulers
        engine["get_wsh_house"] = lambda lon, asc: 1
        seven = pdata(Saturn=0, Jupiter=1, Mars=2, Sun=3, Venus=4, Mercury=5, Moon=6)
        results = engine["evaluate_victors"](seven, 0, 0, 0, "Diurnal", {"Day Lord": None, "Hour Lord": None})
    finally:
        engine["get_essential_rulers"], engine["get_wsh_house"] = saved
    assert all(v["runner_up"] == "-" for v in results.values())


# --- CODE-11: saved-chart persistence -------------------------------------

@pytest.fixture
def chart_paths(engine, tmp_path):
    saved = engine["SAVED_CHARTS_PATH"], engine["_LEGACY_SAVED_CHARTS_PATH"]
    engine["SAVED_CHARTS_PATH"] = tmp_path / "saved_charts.json"
    engine["_LEGACY_SAVED_CHARTS_PATH"] = tmp_path / "legacy" / "saved_charts.json"
    try:
        yield engine["SAVED_CHARTS_PATH"], engine["_LEGACY_SAVED_CHARTS_PATH"]
    finally:
        engine["SAVED_CHARTS_PATH"], engine["_LEGACY_SAVED_CHARTS_PATH"] = saved


ENTRY = {"date_string": "1240-05-23", "time_string": "14:30:00", "location_query": "Florence",
         "lat": 43.7792, "lon": 11.2463}


@pytest.mark.parametrize("text", ["[]", "null", "3", '"x"', '{"a": 1}', '{"a": []}', "{not json"])
def test_loader_rejects_non_mapping_roots_and_entries(engine, chart_paths, text):
    path, _legacy = chart_paths
    path.write_text(text)
    assert engine["load_saved_charts"]() == {}


def test_loader_round_trips_a_valid_mapping(engine, chart_paths):
    assert engine["write_saved_charts"]({"Florence": ENTRY}) is True
    assert engine["load_saved_charts"]() == {"Florence": ENTRY}
    assert not list(chart_paths[0].parent.glob("*.tmp")), "temp file left behind"


def test_writer_refuses_a_non_mapping_and_keeps_the_old_file(engine, chart_paths):
    engine["write_saved_charts"]({"Florence": ENTRY})
    assert engine["write_saved_charts"]([]) is False
    assert engine["load_saved_charts"]() == {"Florence": ENTRY}


def test_write_replaces_atomically(engine, chart_paths, monkeypatch):
    """If the replace step fails the previous file must be untouched."""
    import os
    engine["write_saved_charts"]({"Florence": ENTRY})
    before = chart_paths[0].read_text()

    def boom(_src, _dst):
        raise OSError("disk full")
    monkeypatch.setattr(os, "replace", boom)
    assert engine["write_saved_charts"]({"Other": ENTRY}) is False
    assert chart_paths[0].read_text() == before


def test_legacy_migration_validates_and_copies(engine, chart_paths):
    path, legacy = chart_paths
    legacy.parent.mkdir()
    legacy.write_text("[]")
    assert engine["load_saved_charts"]() == {}
    assert not path.exists(), "a malformed legacy file must not be migrated"
    legacy.write_text('{"Old": %s}' % __import__("json").dumps(ENTRY))
    assert engine["load_saved_charts"]() == {"Old": ENTRY}
    assert path.exists()


# =========================================================================
# Worked figures: one positive fixture and one mutation per figure.
# Positions are the figures' own; the mutation moves one body so the
# configuration the paragraph describes no longer holds, and the row must
# not appear. Under Sahl's rule unless the figure is Abu Ma'shar's own.
# =========================================================================

def _has(rows, **want):
    return any(all(r.get(k) == v for k, v in want.items()) for r in rows)


@pytest.fixture
def sahl(engine):
    with engine["doctrine"](engine["SAHL"]):
        yield engine


# Sahl Fig. 10 (Ch.3, 25-27): Moon 10 Gemini separates from Mercury 8 Leo
# and connects with Jupiter 13 Pisces, carrying Mercury's light.
def test_fig10_transfer_of_light(sahl):
    fig = pdata(Moon=(70, MOON), Mercury=(128, MERC), Jupiter=(343, JUP))
    rows = sahl["evaluate_transfers_of_light"](fig)
    assert _has(rows, Type="I", Carrier="Moon", **{"Separates From": "Mercury", "Connects To": "Jupiter"}), rows


def test_fig10_control_moon_not_yet_past_mercury(sahl):
    # Moon 6 Gemini is still APPLYING to Mercury's sextile degree (8 Gemini):
    # nothing has been separated from, so nothing is carried.
    fig = pdata(Moon=(66, MOON), Mercury=(128, MERC), Jupiter=(343, JUP))
    rows = sahl["evaluate_transfers_of_light"](fig)
    assert not _has(rows, Carrier="Moon", **{"Separates From": "Mercury"}), rows


# Sahl Fig. 11 (Ch.3, 29-30): Venus 10 Aries and Moon 12 Taurus, not
# looking at each other, both connect with Jupiter 15 Cancer.
def test_fig11_collection_of_light(sahl):
    fig = pdata(Venus=(10, VENUS), Moon=(42, MOON), Jupiter=(105, JUP))
    rows = sahl["evaluate_collections_of_light"](fig)
    assert _has(rows, Collector="Jupiter", Collects="Moon & Venus"), rows


def test_fig11_control_both_separating_from_jupiter(sahl):
    # Jupiter at 8 Cancer: Venus's square (10 Cancer) and the Moon's
    # sextile (12 Cancer) are both already past him -- separating, not
    # connecting, so he collects nothing.
    fig = pdata(Venus=(10, VENUS), Moon=(42, MOON), Jupiter=(98, JUP))
    rows = sahl["evaluate_collections_of_light"](fig)
    assert not _has(rows, Collector="Jupiter"), rows


# Sahl Fig. 12 (Ch.3, 32-34): Mercury 10 Cancer, Mars 13 Aries, Jupiter
# 15 Pisces -- Mars's square is nearer than Jupiter's trine by 2 degrees.
def test_fig12_cutting_the_light(sahl):
    fig = pdata(Mercury=(100, MERC), Mars=(13, MARS), Jupiter=(345, JUP))
    rows = sahl["evaluate_cutting_the_light"](fig, None)
    assert _has(rows, Type="III", Planet="Mercury", **{"Yields To": "Mars", "Other Contact": "Jupiter",
                                                        "Because": "nearer by 2.0 deg"}), rows


def test_fig12_control_jupiter_nearer(sahl):
    # Mars 20 Aries: his square now lands at 20 Cancer, 10 degrees off,
    # against Jupiter's trine at 15 Cancer, 5 off. Mercury does not yield
    # to Mars.
    fig = pdata(Mercury=(100, MERC), Mars=(20, MARS), Jupiter=(345, JUP))
    rows = sahl["evaluate_cutting_the_light"](fig, None)
    assert not _has(rows, Planet="Mercury", **{"Yields To": "Mars"}), rows


# Sahl Fig. 13 / Abu Fig. 130: Moon 8, Mars 10, Saturn 12 Gemini.
def test_fig13_intervention(sahl):
    fig = pdata(Moon=(68, MOON), Mars=(70, MARS), Saturn=(72, SAT))
    rows = sahl["evaluate_blocking"](fig)
    assert _has(rows, Type="I (Intervention)", Blocked="Moon", **{"Blocked By": "Mars", "From Reaching": "Saturn"}), rows


def test_fig13_control_mars_past_saturn(sahl):
    # Mars 13 Gemini: the heavy planet no longer holds the most degrees and
    # Mars is separating from him -- nothing stands between Moon and Saturn.
    fig = pdata(Moon=(68, MOON), Mars=(73, MARS), Saturn=(72, SAT))
    rows = sahl["evaluate_blocking"](fig)
    assert not _has(rows, Type="I (Intervention)"), rows


# Sahl Fig. 14 / Abu Fig. 131: Moon 10 Scorpio opposes Saturn 23 Taurus;
# Mars 15 Taurus joins Saturn by body first (8 degrees against her 13).
def test_fig14_nullification(sahl):
    fig = pdata(Moon=(220, MOON), Mars=(45, MARS), Saturn=(53, SAT))
    rows = sahl["evaluate_blocking"](fig)
    assert _has(rows, Type="II (Nullification)", Blocked="Moon", **{"Blocked By": "Mars", "From Reaching": "Saturn"}), rows


def test_fig14_control_mars_past_saturn(sahl):
    # Mars 25 Taurus has passed Saturn: "if it goes beyond that, its
    # connection is valid" (40).
    fig = pdata(Moon=(220, MOON), Mars=(55, MARS), Saturn=(53, SAT))
    rows = sahl["evaluate_blocking"](fig)
    assert not _has(rows, Type="II (Nullification)"), rows


# Sahl Fig. 15 (Ch.3, 45-48): Moon 10 Taurus uniting with Mars 20 Taurus
# while connecting with Venus 15 Cancer; the union is not cut by the ray.
def test_fig15_union_precedence(sahl):
    fig = pdata(Moon=(40, MOON), Mars=(50, MARS), Venus=(105, VENUS))
    rows = sahl["evaluate_cutting_the_light"](fig, None)
    assert _has(rows, Type="Nullification (44-48)", Planet="Moon", **{"Yields To": "Mars", "Other Contact": "Venus"}), rows


def test_fig15_control_moon_past_mars(sahl):
    # Mars 5 Taurus: the Moon has left him, so there is no union to outrank
    # her connection with Venus.
    fig = pdata(Moon=(40, MOON), Mars=(35, MARS), Venus=(105, VENUS))
    rows = sahl["evaluate_cutting_the_light"](fig, None)
    assert not _has(rows, Type="Nullification (44-48)", Planet="Moon"), rows


# Sahl Fig. 25 (Ch.3, 119-123): Moon 10 Taurus between Mars 8 and Saturn
# 17 Taurus, both legs within seven degrees.
def test_fig25_enclosure(sahl):
    fig = pdata(Mars=(38, MARS), Moon=(40, MOON), Saturn=(47, SAT))
    rows = sahl["evaluate_enclosure"](fig)
    assert _has(rows, Planet="Moon", **{"Enclosed By": "Infortunes", "Separating From": "Mars", "Connecting To": "Saturn",
                                        "Severity": "More powerful/unfortunate (within 7°)"}), rows


def test_fig25_control_moon_before_both(sahl):
    # Moon 6 Taurus is applying to Mars AND Saturn: she separates from
    # neither, so she is not between them.
    fig = pdata(Mars=(38, MARS), Moon=(36, MOON), Saturn=(47, SAT))
    rows = sahl["evaluate_enclosure"](fig)
    assert not _has(rows, Planet="Moon", **{"Enclosed By": "Infortunes"}), rows


# Directed agency: a retrograde Mars closing on Venus is the applicant and
# hands over to her, though he is the heavier planet (VII.5, 24 and 120).
def test_retrograde_heavier_applicant_hands_over(sahl):
    fig = pdata(Venus=(10, -0.2), Mars=(17, -0.8))
    row = sahl["_pairwise_configurations"](fig)[0]
    assert row["motion"] == "Applying" and row["applicant"] == "Mars"
    handed = sahl["evaluate_handing_over"](fig, "Diurnal")
    assert _has(handed, Type="Management", Planet="Mars", **{"Hands Over To": "Venus"}), handed


def test_control_venus_sundered_from_mars_hands_nothing_over(sahl):
    # Venus 26 Aries is 9 degrees past Mars, beyond her 7-degree light:
    # "sundered from it" (Ch.3, 11), so no longer connected and nothing is
    # handed over. (At 7 degrees she would still be connected under 10.)
    fig = pdata(Venus=(26, VENUS), Mars=(17, MARS))
    row = sahl["_pairwise_configurations"](fig)[0]
    assert row["motion"] == "Separating" and not sahl["_is_connected_sahl"](row)
    assert not _has(sahl["evaluate_handing_over"](fig, "Diurnal"), Type="Management")


def test_applying_separating_agrees_with_a_finite_step(engine):
    import random
    rng = random.Random(20260906)
    pairs = engine["_pairwise_configurations"]
    for _ in range(2000):
        a, b = rng.uniform(0, 360), rng.uniform(0, 360)
        va, vb = rng.uniform(-1.5, 14.5), rng.uniform(-1.5, 14.5)
        row = pairs(pdata(Venus=(a, va), Mars=(b, vb)))[0]
        if row["aspect_name"] == "Aversion":
            continue
        dt = 1e-5
        a2, b2 = (a + va * dt) % 360, (b + vb * dt) % 360
        raw = abs(a2 - b2)
        after = abs(min(raw, 360 - raw) - row["target"])
        expected = "Applying" if after <= abs(row["deviation"]) else "Separating"
        assert row["motion"] == expected, (a, b, va, vb, row)


# =========================================================================
# Connection thresholds at limit - e, limit, limit + e.
# =========================================================================

EPS = 0.01
SPEEDS = {"Sun": 1.0, "Moon": MOON, "Mercury": MERC, "Venus": VENUS, "Mars": MARS, "Jupiter": JUP}


def _sahl_row(engine, actor, d):
    """`actor` in Aries applying by trine to Saturn 20 Leo, d degrees short."""
    fig = pdata(**{actor: (20 - d, SPEEDS[actor]), "Saturn": (140, SAT)})
    row = engine["_pairwise_configurations"](fig)[0]
    assert row["motion"] == "Applying" and row["applicant"] == actor
    return row


@pytest.mark.parametrize("actor", list(SPEEDS))
def test_sahl_applying_orb_is_the_actors_own_light(engine, actor):
    orb = engine["PLANETARY_ORBS"][actor]
    connected = engine["_is_connected_sahl"]
    assert connected(_sahl_row(engine, actor, orb - EPS))
    assert connected(_sahl_row(engine, actor, orb))
    assert not connected(_sahl_row(engine, actor, orb + EPS))


def test_sahl_orb_belongs_to_a_heavier_applicant_too(engine):
    """Saturn overtaking a slower Jupiter is the applicant; his 9 degrees
    govern, not Jupiter's."""
    for d, expect in ((9 - EPS, True), (9.0, True), (9 + EPS, False)):
        fig = pdata(Saturn=(20 - d, 0.05), Jupiter=(140, 0.02))
        row = engine["_pairwise_configurations"](fig)[0]
        assert row["applicant"] == "Saturn" and row["motion"] == "Applying"
        assert engine["_is_connected_sahl"](row) is expect, d


def test_sahl_same_sign_separation_ends_at_half_the_light_body(engine):
    """Ch.3, 10: separated when the light one departs by 'one-half of its
    body -- and that is its light'. Moon past Saturn in one sign: 12."""
    for d, expect in ((12 - EPS, True), (12.0, True), (12 + EPS, False)):
        row = engine["_pairwise_configurations"](pdata(Saturn=(10, SAT), Moon=(10 + d, MOON)))[0]
        assert row["motion"] == "Separating" and row["signs_apart"] == 0
        assert engine["_is_connected_sahl"](row) is expect, d


def test_sahl_cross_sign_separation_ends_at_one_degree(engine):
    """Ch.3, 9: 'until it separates from the planet by a full degree'."""
    for d, expect in ((1 - EPS, True), (1.0, True), (1 + EPS, False)):
        row = engine["_pairwise_configurations"](pdata(Moon=(10 + d, MOON), Saturn=(130, SAT)))[0]
        assert row["motion"] == "Separating" and row["signs_apart"] == 4
        assert engine["_is_connected_sahl"](row) is expect, d


def test_abu_assembly_window_is_fifteen(engine):
    for d, expect in ((15 - EPS, True), (15.0, True), (15 + EPS, False)):
        row = engine["_pairwise_configurations"](pdata(Moon=(0, MOON), Saturn=(d, SAT)))[0]
        assert row["assembly"] and row["motion"] == "Applying"
        assert engine["_is_connected_abu_mashar"](row) is expect, d


def test_abu_aspect_window_is_twelve_for_every_pair(engine):
    for actor in SPEEDS:
        for d, expect in ((12 - EPS, True), (12.0, True), (12 + EPS, False)):
            assert engine["_is_connected_abu_mashar"](_sahl_row(engine, actor, d)) is expect, (actor, d)


def test_abu_connection_ends_at_exactness_not_a_minute_past_it(engine):
    """Gr. Intr. VII.5, 16: 'if the light one passed by the slow one by one
    minute or by less than that, then it has already SEPARATED'; 34 the
    same for every connection. A pair 18 arcseconds past exact is
    separated; the minute is not a grace interval (Astra F09). The old
    pin here (connected up to 1' past) encoded the inversion."""
    m = 1.0 / 60.0
    for d in (1e-6, 0.005, m - 1e-6, m + 1e-6):
        row = engine["_pairwise_configurations"](pdata(Moon=(10 + d, MOON), Saturn=(130, SAT)))[0]
        assert row["motion"] == "Separating"
        assert engine["_is_connected_abu_mashar"](row) is False, d
    exact = engine["_pairwise_configurations"](pdata(Moon=(10, MOON), Saturn=(130, SAT)))[0]
    assert engine["_is_connected_abu_mashar"](exact) is True


# --- CODE-04: the Fig. 14 tolerance is bounded ----------------------------

def test_fig14_fires_under_the_named_worked_figure_tolerance(sahl):
    fig = pdata(Moon=(220, MOON), Mars=(45, MARS), Saturn=(53, SAT))
    row = next(r for r in sahl["evaluate_blocking"](fig) if r["Type"] == "II (Nullification)")
    assert row["Standing"].startswith("worked-figure tolerance"), row


def test_fig14_control_ray_29_degrees_from_exact_does_not_nullify(sahl):
    # Moon 0 Scorpio, Mars 22 Taurus, Saturn 29 Taurus: Mars is joining
    # Saturn, but the Moon's ray is 29 degrees from exact -- no connection
    # by either author's measure, so nothing is there to be cut.
    fig = pdata(Moon=(210, MOON), Mars=(52, MARS), Saturn=(59, SAT))
    rows = sahl["evaluate_blocking"](fig)
    assert not _has(rows, Type="II (Nullification)"), rows


def test_fig14_tolerance_thresholds(sahl):
    """Moon opposing Saturn 29 Taurus from Scorpio, Mars 22 Taurus joining
    him: the ray leg fires up to the Moon's 12 + 1 and not beyond."""
    for d, expect in ((13 - EPS, True), (13.0, True), (13 + EPS, False)):
        fig = pdata(Moon=(239 - d, MOON), Mars=(52, MARS), Saturn=(59, SAT))
        rows = sahl["evaluate_blocking"](fig)
        assert _has(rows, Type="II (Nullification)") is expect, (d, rows)


def test_fig14_live_connection_is_named_as_such(sahl):
    fig = pdata(Moon=(230, MOON), Mars=(52, MARS), Saturn=(59, SAT))   # 9 degrees from exact
    row = next(r for r in sahl["evaluate_blocking"](fig) if r["Type"] == "II (Nullification)")
    assert row["Standing"] == "live connection"


# --- CODE-08: the Moon's ten defects vote once per paragraph ---------------

def test_moon_defects_count_unique_testimonies_not_matches(engine):
    """Moon 0 Scorpio (her fall, the burned path) connecting with Venus in
    Virgo and Mercury in Pisces (both in their own falls) which are also
    both cadent: 104 and 109 are each met by two planets. Every clause is
    reported; the count is the number of paragraphs, not of clauses."""
    fig = pdata(Moon=(210, MOON), Venus=(155, VENUS), Mercury=(335, MERC), Sun=(0, 1.0), North_Node=(80, 0.0))
    rec = engine["evaluate_corruption_of_the_moon"](fig, 0.0, "Diurnal")
    t = rec["testimonies"]
    assert list(t) == list(range(103, 113))
    assert len(t[104]["clauses"]) == 3 and len(t[109]["clauses"]) == 2, t
    assert t[104]["matched"] and t[109]["matched"] and t[110]["matched"]
    assert rec["unique_testimony_count"] == sum(x["matched"] for x in t.values())
    assert rec["matching_instances"] == sum(len(x["clauses"]) for x in t.values())
    assert rec["matching_instances"] > rec["unique_testimony_count"]
    assert rec["unique_testimony_count"] <= 10
    assert rec["labels"] == engine["_corruption_of_the_moon_labels"](fig, 0.0, "Diurnal")
    assert sum("(104)" in l for l in rec["labels"]) == 3


def test_moon_defects_control_clean_moon(engine):
    # Moon 5 Taurus, waxing, fast, angular, no infortune in sight.
    fig = pdata(Moon=(35, 14.0), Sun=(0, 1.0), Jupiter=(155, JUP), North_Node=(200, 0.0))
    rec = engine["evaluate_corruption_of_the_moon"](fig, 30.0, "Diurnal")
    assert rec["unique_testimony_count"] == 0 and rec["labels"] == [], rec


# --- CODE-03: Sahl banishment is not Abu Ma'shar wildness -----------------

def test_banished_but_not_wild_when_signs_trine_without_a_connection(engine):
    """Moon 0 Aries, Mars 29 Leo: the signs trine, so neither is in
    aversion (not wild for Abu Ma'shar), but the ray is 29 degrees from
    exact -- outside the Moon's 12 -- so no planet connects to either
    (both banished for Sahl, 64)."""
    fig = pdata(Moon=(0, MOON), Mars=(149, MARS))
    banished = engine["evaluate_sahl_banishment"](fig)
    assert {r["Planet"] for r in banished} == {"Moon", "Mars"}, banished
    moon = next(r for r in banished if r["Planet"] == "Moon")["Closest configured planet"]
    assert "29.0" in moon and "Moon's light of 12" in moon and "(19)" in moon
    assert engine["evaluate_abu_wildness"](fig) == []


def test_banished_row_names_the_separation_rule_it_fails(engine):
    # Mars 1.1 degrees past his sextile to Saturn across signs: 9's full
    # degree is the test, not his 8-degree light.
    fig = pdata(Mars=(31.1, MARS), Saturn=(90, SAT))
    row = next(r for r in engine["evaluate_sahl_banishment"](fig) if r["Planet"] == "Mars")
    assert "separating" in row["Closest configured planet"] and "(9)" in row["Closest configured planet"], row
    # Same sign: 10's half-body.
    fig = pdata(Moon=(25, MOON), Saturn=(10, SAT))
    row = next(r for r in engine["evaluate_sahl_banishment"](fig) if r["Planet"] == "Moon")
    assert "(10)" in row["Closest configured planet"] and "Moon's body, 12" in row["Closest configured planet"], row


def test_wild_but_not_banished_with_an_out_of_sign_body_connection(engine):
    """Moon 29 Aries, Mars 2 Taurus: adjacent signs are in aversion (wild
    for Abu Ma'shar), yet the Moon's light strikes into Taurus and
    connects with Mars by body (Ch.3, 20-21) -- neither is banished."""
    fig = pdata(Moon=(29, MOON), Mars=(32, MARS))
    assert engine["evaluate_sahl_banishment"](fig) == []
    wild = engine["evaluate_abu_wildness"](fig)
    assert {r["Planet"] for r in wild} == {"Moon", "Mars"}
    assert all("not banished" in r["Note"] for r in wild)


def test_neither_banished_nor_wild_inside_a_live_connection(engine):
    fig = pdata(Moon=(0, MOON), Mars=(125, MARS))   # 5 degrees from the trine
    assert engine["evaluate_sahl_banishment"](fig) == []
    assert engine["evaluate_abu_wildness"](fig) == []


def test_both_banished_and_wild_in_full_aversion(engine):
    fig = pdata(Moon=(0, MOON), Mars=(45, MARS))    # Aries / Taurus, no body reach
    assert {r["Planet"] for r in engine["evaluate_sahl_banishment"](fig)} == {"Moon", "Mars"}
    assert {r["Planet"] for r in engine["evaluate_abu_wildness"](fig)} == {"Moon", "Mars"}
    assert engine["evaluate_sahl_banishment"](fig)[0]["Closest configured planet"] == "in aversion to every planet"


def test_the_shared_wildness_evaluator_is_gone(engine):
    assert "evaluate_wildness" not in engine


# --- CODE-02: Abu Ma'shar's two reception axes -----------------------------

@pytest.fixture
def abu(engine):
    with engine["doctrine"](engine["ABU_MASHAR"]):
        yield engine


def _rec(rows, receiver, received):
    return [r for r in rows if r.get("Receiver") == receiver and r.get("Received") == received]


def test_lone_domicile_reception_is_strongest_basis_and_globally_middling(abu):
    # Moon 15 Aries (Mars's house; face Sun, bound Mercury) sextile to
    # Mars 15 Gemini: Mars receives her by house alone.
    fig = pdata(Moon=(15, MOON), Mars=(75, MARS))
    rows = _rec(abu["evaluate_reception"](fig, "Diurnal"), "Mars", "Moon")
    assert len(rows) == 1 and rows[0]["Via"] == "house", rows
    assert rows[0]["Dignity quality"] == "Strongest basis, house (131)"
    assert rows[0]["Overall class"].startswith("Middling (140)")
    assert "Grade" not in rows[0]


def test_house_with_bound_is_strong_at_141(abu):
    # Moon 22 Aries: Mars's house AND his bound (20-25).
    fig = pdata(Moon=(22, MOON), Mars=(82, MARS))
    rows = _rec(abu["evaluate_reception"](fig, "Diurnal"), "Mars", "Moon")
    assert rows[0]["Via"] == "house, bound", rows
    assert rows[0]["Dignity quality"] == "Strongest basis, house (131)"
    assert rows[0]["Overall class"].startswith("Strong (141)")


def test_one_minor_dignity_is_weak_locally_and_middling_globally(abu):
    # Moon 2 Aries trine Jupiter 2 Leo, day chart: Jupiter holds only the
    # bound (0-6 Aries) where she stands.
    fig = pdata(Moon=(2, MOON), Jupiter=(122, JUP))
    rows = _rec(abu["evaluate_reception"](fig, "Diurnal"), "Jupiter", "Moon")
    assert rows[0]["Via"] == "bound", rows
    assert rows[0]["Dignity quality"] == "Weak, bound alone (132)"
    assert rows[0]["Overall class"].startswith("Middling (140)")


def test_two_minor_dignities_are_complete_locally_and_strong_globally(abu):
    # Moon 8 Taurus sextile Mercury 8 Cancer, day chart: Mercury holds the
    # bound (8-14) and the face (0-10) of Taurus; she holds Cancer, so the
    # reception is also mutual.
    fig = pdata(Moon=(38, MOON), Mercury=(98, MERC))
    rows = abu["evaluate_reception"](fig, "Diurnal")
    m = _rec(rows, "Mercury", "Moon")[0]
    assert m["Via"] == "bound, face" and m["Dignity quality"] == "Complete, bound with face (132)", m
    assert m["Overall class"].startswith("Strong (141)")
    mutual = [r for r in rows if r["Direction"] == "Mutual"]
    assert mutual and mutual[0]["Overall class"] == "Strong (141): mutual"


def test_sun_moon_opposition_keeps_detestable_off_the_ladder(abu):
    fig = pdata(Sun=(0, 1.0), Moon=(185, MOON))       # 5 Libra, applying to the opposition
    rows = _rec(abu["evaluate_reception"](fig, "Diurnal"), "Sun", "Moon")
    assert rows[0]["Overall class"].startswith("Detestable (137)"), rows


def test_harmonious_acceptance_is_below_middling(abu):
    fig = pdata(Venus=(5, VENUS), Jupiter=(125, JUP))     # trine, and the two fortunes
    rows = abu["evaluate_reception"](fig, "Diurnal")
    natural = [r for r in rows if r["Mode"] == "Not a dignity reception"]
    assert natural and all(r["Overall class"] == "Below middling (142)" for r in natural), rows


def test_sahl_rows_keep_his_own_single_grade(sahl):
    fig = pdata(Moon=(15, MOON), Mars=(75, MARS))
    rows = _rec(sahl["evaluate_reception"](fig, "Diurnal"), "Mars", "Moon")
    assert rows[0]["Grade"] == "Perfect" and "Overall class" not in rows[0], rows


# --- CODE-01: Abu Ma'shar's natural connections (VII.5, 53-77) -------------

def _nat(engine, fig):
    return engine["evaluate_abu_natural_connections"](fig)


def test_5_aries_25_pisces_is_an_exact_equal_ascension_connection(engine):
    """57: 'when a planet is in the first degree of Aries, then it is in the
    nature of a planet which is at the last degree of Pisces' -- complements
    within the sign, so 5 Aries meets 25 Pisces."""
    fig = pdata(Venus=(5, VENUS), Mars=(355, 0.6))
    rows = _nat(engine, fig)
    assert len(rows) == 1, rows
    r = rows[0]
    assert r["Family"].startswith("Equal ascensions") and r["Motion"] == "Exact" and r["From exact"] == "0.0°"
    assert r["Affinity (76-77)"] == "natural sextile (77)"       # Pisces-Aries
    assert r["Ordinary aspect"] == "Aversion", "the signs still do not look at each other"


def test_equal_ascension_motion_follows_both_speeds(engine):
    """62: the counterpart degree runs backwards as its planet runs
    forwards. Mars 24 Pisces is short of Venus's counterpart (25) and both
    are direct: applying. At 26 he is past it: separating."""
    applying = _nat(engine, pdata(Venus=(5, VENUS), Mars=(354, 0.6)))[0]
    separating = _nat(engine, pdata(Venus=(5, VENUS), Mars=(356, 0.6)))[0]
    assert applying["Motion"] == "Applying" and applying["From exact"] == "1.0°"
    assert separating["Motion"] == "Separating"
    # Venus retrograde, faster than Mars is direct: the sum of speeds
    # reverses, and so does the verdict.
    reversed_ = _nat(engine, pdata(Venus=(5, -1.0), Mars=(354, 0.6)))[0]
    assert reversed_["Motion"] == "Separating"


def test_12_gemini_18_cancer_is_an_exact_equal_daylight_connection(engine):
    """68: 'the planet which is in 12° of Gemini is in the power of the
    degree of the planet which is in 18° of Cancer'."""
    rows = _nat(engine, pdata(Moon=(72, MOON), Saturn=(108, SAT)))
    assert len(rows) == 1 and rows[0]["Family"].startswith("Equal daylight") and rows[0]["Motion"] == "Exact", rows
    assert rows[0]["Affinity (76-77)"] == "natural sextile (77)"
    assert rows[0]["Ordinary aspect"] == "Aversion"


def test_natural_opposition_pair_keeps_its_ordinary_aversion(engine):
    """76: Gemini with Capricorn is a 'natural connection by opposition';
    it is not an Opposition, and the aspect grid must not grow one."""
    fig = pdata(Venus=(70, VENUS), Mars=(290, MARS))       # 10 Gemini / 20 Capricorn
    rows = _nat(engine, fig)
    assert rows[0]["Affinity (76-77)"] == "natural opposition (76)" and rows[0]["Motion"] == "Exact"
    pair = engine["_pairwise_configurations"](fig)[0]
    assert pair["aspect_name"] == "Aversion"
    assert all(r["Ordinary aspect"] == "Aversion" for r in rows)


def test_control_unlisted_sign_pairs_have_no_natural_connection(engine):
    assert _nat(engine, pdata(Venus=(5, VENUS), Mars=(35, MARS))) == []    # Aries / Taurus
    assert _nat(engine, pdata(Venus=(5, VENUS), Mars=(15, MARS))) == []    # same sign
    # Aquarius / Scorpio: the antiscia family has it, 67-75 does not.
    assert _nat(engine, pdata(Venus=(305, VENUS), Mars=(235, MARS))) == []


def test_134_acceptance_by_equal_ascensions_reaches_an_averse_pair(abu):
    fig = pdata(Venus=(5, VENUS), Mars=(355, 0.6))
    rows = [r for r in abu["evaluate_reception"](fig, "Diurnal") if "(134)" in r["Direction"]]
    assert rows and "equal ascensions" in rows[0]["Via"], rows
    assert rows[0]["Overall class"] == "Below middling (142)"


def test_134_acceptance_by_equal_daylight(abu):
    fig = pdata(Moon=(72, MOON), Saturn=(108, SAT))
    rows = [r for r in abu["evaluate_reception"](fig, "Diurnal") if "(134)" in r["Direction"]]
    assert rows and "equal daylight" in rows[0]["Via"], rows


def test_134_same_lord_signs_accept_across_an_aversion(abu):
    """Aries and Scorpio are both Mars's and in aversion: 134's 'two signs
    belonging to one planet', which the aversion skip used to swallow."""
    fig = pdata(Sun=(5, 1.0), Moon=(215, MOON))
    rows = [r for r in abu["evaluate_reception"](fig, "Diurnal") if "(134)" in r["Direction"]]
    assert rows and "both signs of Mars" in rows[0]["Via"], rows


def test_natural_connections_are_not_in_sahl(sahl):
    # Sahl's 56-57 read the Moon, so his evaluator needs her in the chart.
    fig = pdata(Venus=(5, VENUS), Mars=(355, 0.6), Moon=(200, MOON))
    assert not any("(134)" in r.get("Direction", "") for r in sahl["evaluate_reception"](fig, "Diurnal"))


# --- The Egyptian bounds table, pinned sign by sign ----------------------
# TNAC Handy Tables from Part 1, p. 1, "Table of Egyptian bounds" (Dykes
# 2023), transcribed cell by cell from a 300-dpi render on 2026-09-07. The
# upper limit is exclusive: "0-5 59'" is (6, lord). Until that date the
# table in app.py had two adjacent lords transposed in Gemini (6-17) and in
# Aquarius (0-13), and nothing here noticed because the bound assertions
# above are all in Aries and Taurus. This literal is the whole table, so a
# transposition anywhere fails on the sign it is in.
CANONICAL_EGYPTIAN_BOUNDS = {
    'Aries':       [(6, 'Jupiter'), (12, 'Venus'),   (20, 'Mercury'), (25, 'Mars'),    (30, 'Saturn')],
    'Taurus':      [(8, 'Venus'),   (14, 'Mercury'), (22, 'Jupiter'), (27, 'Saturn'),  (30, 'Mars')],
    'Gemini':      [(6, 'Mercury'), (12, 'Jupiter'), (17, 'Venus'),   (24, 'Mars'),    (30, 'Saturn')],
    'Cancer':      [(7, 'Mars'),    (13, 'Venus'),   (19, 'Mercury'), (26, 'Jupiter'), (30, 'Saturn')],
    'Leo':         [(6, 'Jupiter'), (11, 'Venus'),   (18, 'Saturn'),  (24, 'Mercury'), (30, 'Mars')],
    'Virgo':       [(7, 'Mercury'), (17, 'Venus'),   (21, 'Jupiter'), (28, 'Mars'),    (30, 'Saturn')],
    'Libra':       [(6, 'Saturn'),  (14, 'Mercury'), (21, 'Jupiter'), (28, 'Venus'),   (30, 'Mars')],
    'Scorpio':     [(7, 'Mars'),    (11, 'Venus'),   (19, 'Mercury'), (24, 'Jupiter'), (30, 'Saturn')],
    'Sagittarius': [(12, 'Jupiter'), (17, 'Venus'),  (21, 'Mercury'), (26, 'Saturn'),  (30, 'Mars')],
    'Capricorn':   [(7, 'Mercury'), (14, 'Jupiter'), (22, 'Venus'),   (26, 'Saturn'),  (30, 'Mars')],
    'Aquarius':    [(7, 'Mercury'), (13, 'Venus'),   (20, 'Jupiter'), (25, 'Mars'),    (30, 'Saturn')],
    'Pisces':      [(12, 'Venus'),  (16, 'Jupiter'), (19, 'Mercury'), (28, 'Mars'),    (30, 'Saturn')],
}


@pytest.mark.parametrize("sign", list(CANONICAL_EGYPTIAN_BOUNDS))
def test_egyptian_bounds_match_the_course_table_sign_by_sign(engine, sign):
    assert [tuple(t) for t in engine["EGYPTIAN_TERMS"][sign]] == CANONICAL_EGYPTIAN_BOUNDS[sign], sign


def test_egyptian_bounds_table_has_exactly_the_twelve_signs_and_no_gaps(engine):
    table = engine["EGYPTIAN_TERMS"]
    assert set(table) == set(CANONICAL_EGYPTIAN_BOUNDS)
    for sign, bounds in table.items():
        limits = [limit for limit, _lord in bounds]
        assert limits == sorted(limits) and limits[-1] == 30, sign
        # Five bounds, one per non-luminary, each lord once.
        assert sorted(lord for _l, lord in bounds) == ["Jupiter", "Mars", "Mercury", "Saturn", "Venus"], sign


def test_sahl_example_6_mercury_at_aquarius_5_is_in_his_own_bound(engine):
    # On Nativities Ch. 10.2.7, 21-22: 21 gives the position ("Mercury with
    # him, 5deg", the Sun at Aquarius 16deg); 22 is the bound claim quoted here.
    # 22: "look at Mercury, how he is in the honor
    # guard of the Sun and his right side, IN HIS OWN BOUND, eastern" --
    # Mercury at Aquarius 5 degrees. The engine returned Venus here from the
    # initial commit until 2026-09-07.
    assert engine["get_essential_rulers"](305.0)["term"] == "Mercury"


def test_sahl_example_6_control_aquarius_8_is_venus_not_mercury(engine):
    # Negative control: the next bound up is Venus's (7-13). A table that
    # simply made all of early Aquarius Mercury's would pass the test above
    # and fail this one.
    assert engine["get_essential_rulers"](308.0)["term"] == "Venus"


def test_gemini_transposition_is_gone_with_control(engine):
    # Gemini 8 is Jupiter's bound (6-12); Gemini 13 is Venus's (12-17). The
    # transposed table gave the reverse.
    assert engine["get_essential_rulers"](68.0)["term"] == "Jupiter"
    assert engine["get_essential_rulers"](73.0)["term"] == "Venus"


# =========================================================================
# Persian Nativities IV: the timing apparatus (D-3 closed 2026-09-10)
# =========================================================================
# Citations are Book.chapter, sentence, as in app.py section 3b. Each rule
# gets a case from Abu Ma'shar's own text that must fire and a near-miss
# that must not -- and several of the negatives below are the specific
# wrong readings this corpus or the later tradition actually produced.


# --- III.1, 13: the rate ladder ------------------------------------------

@pytest.mark.parametrize("arc, unit, amount", [
    (1.0, "years", 1),            # "every degree a year"
    (5 / 60, "months", 1),        # "every 5' a month"
    (1 / 60, "days", 6),          # "every 1' six days"
    (10 / 3600, "days", 1),       # 'every 10" one day'
])
def test_pn4_rate_ladder_rungs(engine, arc, unit, amount):
    assert engine["pn4_arc_to_time"](arc)[unit] == amount


def test_pn4_bottom_rung_is_twenty_five_THIRDS(engine):
    """III.1, 13's last rung. 25''' is a sixtieth of a second of arc, and
    it is what closes the ladder: 10" is a day, so an hour is 10"/24."""
    assert engine["pn4_arc_to_time"](25 / 216000.0)["hours"] == pytest.approx(1.0, abs=1e-9)


def test_pn4_bottom_rung_is_NOT_twenty_five_seconds(engine):
    """The negative control for corpus defect D-07. The OCR'd text reads
    `every 25" one hour`; that would make an hour two and a half days, so
    a reading of 25 SECONDS must not produce an hour."""
    got = engine["pn4_arc_to_time"](25 / 3600.0)
    assert got["days"] == 2 and got["hours"] == pytest.approx(12.0, abs=1e-9)
    assert (got["days"] * 24 + got["hours"]) == pytest.approx(60.0, abs=1e-9)


def test_pn4_ladder_is_internally_consistent(engine):
    """Each rung is exactly the next one's multiple, on the idealised year
    of twelve 30-day months (fn 17): 12 months to a degree, 5 days to a
    minute-fifth, 24 hours to a day."""
    f = engine["pn4_arc_to_time"]
    assert f(1.0)["years"] == 1 and f(11 * 5 / 60)["months"] == 11
    assert f(59 / 60)["months"] == 11 and f(59 / 60)["days"] == 24


# --- III.1, 6: the unit is keyed to the level of the chart ----------------

@pytest.mark.parametrize("level, unit", [
    ("root", "years"),
    ("revolution of the year", "months and days"),
    ("revolution of the month", "days and hours"),
])
def test_pn4_direction_unit_by_chart_level(engine, level, unit):
    assert engine["pn4_direction_unit"](level) == unit


def test_pn4_direction_unit_has_no_key_but_the_chart_level(engine):
    """The negative control for corpus disagreement #5. PN IV keys the unit
    to the level of the chart and to nothing else -- not sign type, not
    planetary strength, not quadruplicity, not speed -- so it must not
    answer for any of those, and must not be cited on either side."""
    for absent in ("convertible", "fixed", "Saturn", "strong", "fast"):
        assert engine["pn4_direction_unit"](absent) is None


# --- IV.1, 2-4 and IV.7, 24-25: the fardar --------------------------------

@pytest.mark.parametrize("sect, first", [("Diurnal", "Sun"), ("Nocturnal", "Moon")])
def test_pn4_fardar_begins_at_the_light_of_the_sect(engine, sect, first):
    """IV.1, 3-4: by day from the Sun, by night from the Moon, then down
    the spheres."""
    assert engine["pn4_fardar_sequence"](sect)[0][0] == first


@pytest.mark.parametrize("sect, order", [
    ("Diurnal", ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]),
    ("Nocturnal", ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"]),
])
def test_pn4_fardar_planetary_order(engine, sect, order):
    """IV.1, 3 names the diurnal run "the Sun ... Venus ... Mercury, the
    Moon, and ... Saturn", IV.1, 4 the nocturnal "the Moon, then Saturn,
    Jupiter, [and] Mars" -- both descending the spheres and wrapping."""
    assert [p for p, _ in engine["pn4_fardar_sequence"](sect)][:7] == order


@pytest.mark.parametrize("sect", ["Diurnal", "Nocturnal"])
def test_pn4_fardar_sums_to_seventy_five(engine, sect):
    """IV.1, 2: "the amount of all of that is 75 years". The seven planets
    make 70 (IV.1, 8) and the Nodes carry it to 75."""
    seq = engine["pn4_fardar_sequence"](sect)
    assert sum(y for _, y in seq) == 75
    assert sum(y for p, y in seq if p not in ("Head", "Tail")) == 70


@pytest.mark.parametrize("sect", ["Diurnal", "Nocturnal"])
def test_pn4_nodes_come_last_in_BOTH_sects(engine, sect):
    """IV.7, 24: the native "will begin in the distribution of the fardars
    with the Head, then the Tail, WHETHER THE NATIVE WAS DIURNAL OR
    NOCTURNAL" -- they enter at year 71 in both."""
    seq = engine["pn4_fardar_sequence"](sect)
    assert [p for p, _ in seq][-2:] == ["Head", "Tail"]


def test_pn4_nocturnal_nodes_do_NOT_follow_mars(engine):
    """The negative control, and it is the error the later tradition
    actually made: al-Qabisi IV.21 was read as putting the Head and Tail
    after Mars in every sect, which in a nocturnal chart would place them
    at ages 39-43. IV.7, 24 puts them after MERCURY at night."""
    seq = [p for p, _ in engine["pn4_fardar_sequence"]("Nocturnal")]
    assert seq[seq.index("Mars") + 1] == "Sun"
    assert seq[seq.index("Mercury") + 1] == "Head"
    at = engine["pn4_fardar_at_age"](40.0, "Nocturnal")
    assert at["lord"] not in ("Head", "Tail")


def test_pn4_fardar_subperiods_are_sevenths_from_the_lord(engine):
    """IV.1, 5-6: "one-seventh of its years", beginning from the lord
    itself, then "the planet which is below it in the celestial circle".
    IV.1, 11 works the Sun's: 10/7 = "1 year, 5 months, 4 days, and
    approximately 6 hours"."""
    subs = engine["pn4_fardar_subperiods"]("Sun", 10)
    assert [p for p, _ in subs] == ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    t = engine["pn4_arc_to_time"](subs[0][1])
    assert (t["years"], t["months"], t["days"]) == (1, 5, 4)
    # "and approximately 6 hours": the exact value is 6h51m, which is what
    # "approximately" is doing in the sentence.
    assert 6.0 <= t["hours"] <= 7.0


@pytest.mark.parametrize("node", ["Head", "Tail"])
def test_pn4_nodes_have_no_subperiods(engine, node):
    """IV.1, 8: they "do not partner with the planets (nor do [the planets]
    partner with them), because they do not have houses"."""
    assert engine["pn4_fardar_subperiods"](node, 3) == []
    assert engine["pn4_fardar_at_age"](71.5, "Diurnal")["sub_lord"] is None


def test_pn4_fardar_restarts_at_the_SECT_LIGHT_not_always_the_sun(engine):
    """IV.7, 25: after 75 the distribution "returns to THE LUMINARY WHICH
    HE BEGAN FROM at his birth". IV.1, 2's "then it returns to the Sun" is
    the diurnal case of that, not the general rule."""
    assert engine["pn4_fardar_at_age"](75.5, "Diurnal")["lord"] == "Sun"
    assert engine["pn4_fardar_at_age"](75.5, "Nocturnal")["lord"] == "Moon"
    assert engine["pn4_fardar_at_age"](75.5, "Nocturnal")["cycle"] == 2


# --- I.8, 10-26: the Ages of Man -----------------------------------------

@pytest.mark.parametrize("age, planet", [
    (0, "Moon"), (3, "Moon"), (4, "Mercury"), (13, "Mercury"), (14, "Venus"),
    (21, "Venus"), (22, "Sun"), (40, "Sun"), (41, "Mars"), (55, "Mars"),
    (56, "Jupiter"), (67, "Jupiter"), (68, "Saturn"),
])
def test_pn4_ages_of_man_boundaries(engine, age, planet):
    """I.8, 10-26 and Figure 53. The six stated spans (4, 10, 8, 19, 15,
    12) sum to 68, where Saturn's age begins."""
    assert engine["pn4_age_of_man"](age)["planet"] == planet


def test_pn4_last_age_is_open_ended(engine):
    """The negative control for a figure that disagrees with its prose.
    Figure 53 tabulates Saturn as "30 / ages 68-97", but I.8, 25 says the
    seventh age runs "until the end of his lifespan". A native of 120 is
    still in Saturn's age, and the ages must NOT restart at the Moon --
    I.8, 31-33 reports that view without endorsing it."""
    assert engine["pn4_age_of_man"](97)["planet"] == "Saturn"
    assert engine["pn4_age_of_man"](120)["planet"] == "Saturn"
    assert engine["pn4_age_of_man"](98)["to"] is None


def test_pn4_ages_are_not_subdivided_like_fardars(engine):
    """I.8, 34-35: Abu Ma'shar refuses to divide an age among the seven
    planets -- "he will be in the nature of the planet itself". So an age
    carries no sub-lord, unlike a fardar."""
    assert "sub_lord" not in engine["pn4_age_of_man"](30)


# --- III.10, 5: the first ninth-part --------------------------------------

@pytest.mark.parametrize("sign, lord", [
    ("Taurus", "Saturn"),      # "if the year terminated at 20 deg of Taurus ... Saturn"
    ("Gemini", "Venus"),       # "if the year terminated at Gemini ... Venus"
    ("Cancer", "Moon"),        # "if the year terminated at Cancer ... the Moon"
])
def test_pn4_first_ninth_part_against_abu_mashars_worked_examples(engine, sign, lord):
    """III.10, 5 gives three worked examples; all three must reproduce."""
    assert engine["pn4_first_ninth_part_lord"](sign)["lord"] == lord


def test_pn4_ninth_part_lord_is_one_of_only_four_planets(engine):
    """III.10, 1: the Indian rule "restricts the lord of the year to four
    planets only" -- the lords of the convertible signs, because the first
    ninth-part of every sign falls in a convertible one."""
    lords = {engine["pn4_first_ninth_part_lord"](s)["lord"] for s in engine["SIGN_ORDER"]}
    assert lords == {"Mars", "Venus", "Saturn", "Moon"}


def test_pn4_ninth_part_does_NOT_depend_on_the_degree(engine):
    """The negative control. It is the FIRST ninth-part of the sign, not
    the ninth-part the degree falls in: "if the year terminated at 20 deg
    of Taurus (OR LESS THAN THAT OR MORE), then its lord would be
    Saturn" (III.10, 5)."""
    assert engine["pn4_first_ninth_part_lord"]("Taurus")["lord"] == "Saturn"
    # a degree-sensitive reading would give Taurus's 7th ninth-part here
    assert engine["pn4_first_ninth_part_lord"]("Taurus")["ninth_part_sign"] == "Capricorn"


# --- IX.1, 26-32: which way the monthly indicators turn --------------------

@pytest.mark.parametrize("lon, forward", [
    (45.0, True),     # 15 Taurus -- fixed, forwards (IX.1, 26)
    (5.0, False),     # 5 Aries -- convertible, backwards (IX.1, 27)
    (65.0, True),     # 5 Gemini -- double-bodied, below 15 deg (IX.1, 28)
    (80.0, False),    # 20 Gemini -- double-bodied, from 15 deg (IX.1, 29)
    (75.0, False),    # exactly 15 Gemini: "the beginning of the sixteenth degree"
    (74.99, True),    # just under it
])
def test_pn4_monthly_turn_under_abu_mashars_rule(engine, lon, forward):
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][1]
    assert engine["pn4_monthly_turn_forward"](lon, rule) is forward


@pytest.mark.parametrize("lon", [45.0, 5.0, 65.0, 80.0])
def test_pn4_monthly_turn_under_dykes_is_always_forward(engine, lon):
    """The negative control for the shipped default. Dykes rejects the
    quadruplicity rule and counts forward always, which is the engine's
    default by the owner's decision of 2026-09-10."""
    assert engine["pn4_monthly_turn_forward"](lon, engine["PN4_MONTHLY_TURN_OPTIONS"][0]) is True


def test_pn4_each_indicator_turns_by_its_OWN_sign(engine):
    """IX.1, 31: when the four rooted indicators fall in different
    quadruplicities, "one turns EACH ONE OF THEM INDIVIDUALLY". The
    direction is not decided once, globally, by the sign of the year.

    Here indicator #1 sits in a convertible sign and #4 in a fixed one, so
    under Abu Ma'shar's rule they must turn in OPPOSITE directions."""
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][1]
    rows = engine["pn4_monthly_indicators"](
        3, 0, 5.0, 5.0, 45.0, 45.0, 100.0, 100.0, rule)
    by_number = {r["number"]: r for r in rows}
    assert by_number[1]["direction"] == "backwards"     # 5 Aries, convertible
    assert by_number[4]["direction"] == "forward"       # 15 Taurus, fixed


def test_pn4_ninth_part_indicator_never_reverses(engine):
    """IX.1, 32: indicator #2 "is turned in succession without
    distinction, whether the sign of the terminal point is convertible,
    fixed, or having two bodies"."""
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][1]
    for sign_of_year in (5.0, 45.0, 80.0):       # convertible, fixed, late double-bodied
        rows = engine["pn4_monthly_indicators"](
            4, 0, sign_of_year, 5.0, 5.0, 5.0, 5.0, 5.0, rule)
        assert next(r for r in rows if r["number"] == 2)["direction"].startswith("forward")


# --- II.3, 1: the lord of the year ---------------------------------------

def test_pn4_lord_of_the_year_is_the_lord_of_the_SIGN(engine):
    """II.3, 1: "the sign which the intended year reaches is the 'sign of
    the terminal point,' and its lord is the 'lord of the year'". One sign
    per completed year from the natal Ascendant (I.2, 5)."""
    year = engine["pn4_sign_of_the_year"](5.0, 0)          # 5 Aries, age 0
    assert year["sign"] == "Aries" and year["lord"] == "Mars"
    assert engine["pn4_sign_of_the_year"](5.0, 4)["sign"] == "Leo"
    assert engine["pn4_sign_of_the_year"](5.0, 12)["sign"] == "Aries"   # a full turn


def test_pn4_lord_of_the_year_is_NOT_the_lord_of_the_revolution_ascendant(engine):
    """The negative control for Q21 and corpus disagreement #11. PN IV
    keeps "sign of the year" and "Ascendant of the year" apart (Intro
    Sect. 8, p. 77): the lord of the year is the profection lord, and it
    must not track the revolution's Ascendant."""
    # age 3 from 5 Aries profects to Cancer, lord the Moon, whatever the
    # revolution's Ascendant happens to be.
    assert engine["pn4_sign_of_the_year"](5.0, 3)["lord"] == "Moon"
    assert engine["pn4_sign_of_the_year"](5.0, 3)["sign"] == "Cancer"


# --- III.1, 11-16 and 23-25: the distribution and its partner -------------

def test_pn4_distributor_is_the_bound_lord_aspect_or_no_aspect(engine):
    """III.1, 11: "the lord of that bound is the 'distributor,' WHETHER IT
    LOOKED AT [THE BOUND] OR NOT" -- so it is a pure lookup and must not
    consult any aspect."""
    assert engine["pn4_bound_lord"](0.5) == "Jupiter"      # 0 Aries, Egyptian
    assert engine["pn4_bound_lord"](27.0) == "Saturn"      # 27 Aries
    assert engine["pn4_bound_lord"](185.0) == "Saturn"     # 5 Libra


def test_pn4_partner_ranking_puts_hard_aspects_above_soft(engine):
    """III.2, 103-104: the body first, then "the strongest of the rays is
    the opposition, and after that the square, the[n] the trine, and the
    weakest of them is the sextile". This is the reverse of the usual
    benefic intuition and is the easy thing to get backwards."""
    rank = engine["pn4_partner_strength"]
    assert rank("body") < rank("opposition") < rank("square") < rank("trine") < rank("sextile")


def test_pn4_birth_partner_is_found_behind_the_ascendant(engine):
    """III.1, 23-25: at birth look back "from the beginning of the sign up
    to the degree of the Ascendant". A body there is already the partner."""
    points = pdata(Sun=100.0)                 # 10 Cancer, behind 20 Cancer
    segs = engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78)
    assert segs[0]["partner"] == "Sun" and segs[0]["partner_aspect"] == "body"


def test_pn4_birth_partner_search_stops_at_the_sign_boundary(engine):
    """The negative control. The search runs to the beginning of the
    Ascendant's SIGN, not backwards without limit: a body one degree
    earlier but in the PREVIOUS sign is not the birth partner, and the
    distributor then "[acts] without a planet partnering with her"
    (III.1, 25)."""
    points = pdata(Sun=89.0)                  # 29 Gemini, just before 0 Cancer
    segs = engine["pn4_distribution_from_ascendant"](points, 95.0, 23.44, 43.78)
    assert segs[0]["partner"] is None
    assert "alone" in segs[0]["opened_by"]


def test_pn4_distribution_refuses_above_the_polar_circle(engine):
    """The domain of D-23. Where |latitude| + obliquity >= 90 some degrees
    never rise, the oblique ascension has no unique inverse, and an arc of
    direction from the Ascendant is not defined."""
    points = pdata(Sun=100.0)
    assert engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 78.0) is None
    assert engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78) is not None


def test_pn4_distribution_segments_are_contiguous_and_ordered(engine):
    """Every moment of the span has exactly one distributor and one
    partner: III.1, 16 says the management holds "until it encounters
    another planet", so the segments must tile the span without gaps."""
    points = pdata(Sun=100.0, Moon=200.0, Mars=300.0)
    segs = engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78)
    assert segs[0]["from"] == 0.0
    for a, b in zip(segs, segs[1:]):
        assert a["to"] == pytest.approx(b["from"], abs=1e-12)
        assert a["to"] > a["from"]


# --- III.1, 12: the meridian, by right ascension (built 2026-09-10) -------
# PN IV works no example of a meridian direction -- III.1, 19-45 directs
# the Ascendant only -- so nothing below is the author's arithmetic. These
# pin the measure (right ascension, not oblique), the domain (every
# latitude), the IC's relation to the MC, and the editor's animation check.

def _angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def test_pn4_meridian_distribution_is_measured_in_right_ascension(engine):
    """III.1, 12: "what is in the Midheaven or the fourth is directed by
    the ascensions of the right sphere". From 0 Aries (right ascension 0)
    the Sun's body at 0 Cancer -- the solstice, right ascension exactly 90
    at any obliquity -- is met at 90.0 years; and every segment opens on
    the degree whose right ascension is the arc, by the inverse.

    The negative control is the Ascendant's own distribution from the same
    degree: in oblique ascension at 43.78 N the same body is met about 65
    years in, so a meridian run that agreed with it would be using the
    wrong sphere."""
    points = pdata(Sun=90.0)
    segs = engine["pn4_distribution_from_meridian"](points, 0.0, 23.44, "Midheaven")
    assert segs[0]["from"] == 0.0 and segs[0]["distributor"] == "Jupiter"     # 0 Aries, Egyptian
    met = [s for s in segs if s["partner"] == "Sun" and s["partner_aspect"] == "body"]
    assert met and met[0]["from"] == pytest.approx(90.0, abs=1e-9)
    inverse = engine["_lon_with_right_ascension"]
    for seg in segs:
        assert _angdiff(inverse(seg["from"], 23.44), seg["from_lon"]) == pytest.approx(0.0, abs=1e-8)

    asc = engine["pn4_distribution_from_ascendant"](points, 0.0, 23.44, 43.78)
    met_asc = [s for s in asc if s["partner"] == "Sun" and s["partner_aspect"] == "body"]
    assert abs(met_asc[0]["from"] - 90.0) > 20.0


def test_pn4_meridian_distribution_does_not_refuse_at_the_poles(engine):
    """Right ascension has no latitude in it and the meridian crosses the
    ecliptic at every latitude, so III.1, 12's meridian direction has no
    undefined domain: D-23's refusal is about inverting the OBLIQUE
    ascension, which it never does. The Ascendant's run refuses at 78 N;
    the meridian's takes no latitude and tiles its whole span."""
    points = pdata(Sun=100.0, Moon=200.0, Mars=300.0)
    assert engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 78.0) is None
    for point in engine["PN4_MERIDIAN_POINTS"]:
        segs = engine["pn4_distribution_from_meridian"](points, 110.0, 23.44, point)
        assert segs[0]["from"] == 0.0 and segs[-1]["to"] == 120.0
        for a, b in zip(segs, segs[1:]):
            assert a["to"] == pytest.approx(b["from"], abs=1e-12)
            assert a["to"] > a["from"]


def test_pn4_the_fourth_is_the_midheaven_run_half_a_turn_on(engine):
    """Fn 14: "the fourth" is the IC itself, the point opposite the
    Midheaven. Opposite points are 180 apart in right ascension, so every
    boundary the fourth's direction crosses in its first 180 years is one
    the Midheaven's direction crosses exactly 180 years later, on the same
    degree, with the same distributor taking over."""
    points = pdata(Sun=100.0, Moon=200.0, Mars=300.0, Saturn=15.0)
    mc = engine["pn4_distribution_from_meridian"](points, 47.0, 23.44, "Midheaven", span_years=360.0)
    ic = engine["pn4_distribution_from_meridian"](points, 47.0, 23.44, "Fourth (IC)", span_years=180.0)
    assert ic[0]["from_lon"] == pytest.approx(227.0)
    for seg in ic[1:]:
        twins = [s for s in mc if abs(s["from"] - (seg["from"] + 180.0)) < 1e-6]
        assert len(twins) == 1, seg
        assert twins[0]["distributor"] == seg["distributor"]
        assert _angdiff(twins[0]["from_lon"], seg["from_lon"]) == pytest.approx(0.0, abs=1e-9)


def test_pn4_meridian_refuses_the_descendant(engine):
    """Fn 15: "Abu Ma'shar has omitted the Descendant" from III.1, 12's
    three positions. The engine directs the two points the sentence names
    and nothing else by right ascension."""
    with pytest.raises(ValueError):
        engine["pn4_distribution_from_meridian"](pdata(Sun=90.0), 0.0, 23.44, "Descendant")


def test_pn4_meridian_direction_against_dykes_four_minutes_a_degree(engine):
    """The editor's check, since the author gives none. Appendix A (p. 673):
    "the celestial sphere rotates 1 degree for every 4 minutes of clock
    time" (fn 1: "actually 3m 59.34s"), so "animate the MC ... multiply
    the age by 4 and add those minutes to the birth time, to see where the
    MC lands at that age". Cast the chart, advance the clock by that much
    per year, and the Midheaven swe.houses reports for the later moment
    must be the degree the engine directs the Midheaven to -- and lie in
    the bound of the engine's distributor for that age. swe.houses'
    meridian is an independent path from the cotrans the engine uses."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    root = cast(birth, lat, lon)
    segs = engine["pn4_distribution_from_meridian"](root["planetary_data"], root["mc"], root["obliquity"])
    ra_mc = engine["_ra_decl"](root["mc"], root["obliquity"])[0]
    for age in (17.97, 42.0, 100.0):
        later = cast(birth + timedelta(seconds=age * (3 * 60 + 59.34)), lat, lon)
        directed = engine["_lon_with_right_ascension"](ra_mc + age, root["obliquity"])
        assert _angdiff(later["mc"], directed) == pytest.approx(0.0, abs=0.01)
        seg = engine["pn4_distribution_at_age"](segs, age)
        assert seg["distributor"] == engine["pn4_bound_lord"](later["mc"])


def test_pn4_segment_from_lon_agrees_with_the_ascension_inverse(engine):
    """Every segment records the degree it opened on (from_lon), and the
    page's Ascendant row still recovers that degree by inverting the
    oblique ascension (_pn4_seg_degree). Two routes to one number; they
    must agree on every segment or one of them is wrong."""
    points = pdata(Sun=100.0, Moon=200.0, Mars=300.0, Venus=15.0)
    segs = engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78)
    for seg in segs:
        got = engine["_pn4_seg_degree"](seg, 110.0, {"obliquity": 23.44}, 43.78)
        assert _angdiff(got, seg["from_lon"]) == pytest.approx(0.0, abs=1e-8)


# --- IX.7, 29-31: the small days (built 2026-09-10) -----------------------
# No worked example exists in PN IV (IX.7's only one, 57-69, is the
# ninth-part method), so these pin the sentence: the rate, the circuit,
# the zodiacal measure, and IX.7, 30's opening window -- the bound, not
# the sign -- read as III.1, 23-25 is worked, which the owner chose.

def test_pn4_small_days_rate_closes_the_year(engine):
    """IX.7, 29: "a day for every 59' 08", until it returns to the degree
    of the Ascendant at the end of the year". 59' 08" is one day exactly,
    and the full circuit is 360 / (59' 08") = 365.28 days -- the year to
    within an hour, which is what "returns ... at the end of the year"
    requires of a zodiacal rate."""
    assert engine["pn4_small_days_arc_to_days"](59 / 60 + 8 / 3600) == pytest.approx(1.0)
    segs = engine["pn4_small_days"](pdata(Sun=100.0, Moon=200.0), 10.0)
    assert segs[0]["from"] == 0.0
    circuit = segs[-1]["to"]
    assert circuit == pytest.approx(360.0 / (59 / 60 + 8 / 3600))
    assert abs(circuit - 365.2422) < 1 / 24 + 0.01
    for a, b in zip(segs, segs[1:]):
        assert a["to"] == pytest.approx(b["from"], abs=1e-9) and a["to"] > a["from"]


def test_pn4_small_days_are_zodiacal_and_take_no_latitude(engine):
    """The sentence gives its rate in degrees of the zodiac (IX.7, 29) and
    Abu Ma'shar calls that an approximation he is content with (IX.7,
    32). A body 30 degrees ahead is met at 30 / (59' 08") = 30.44 days,
    wherever the native was born; the Ascendant's own distribution from
    the same degree at 43.78 N reaches the same body at a different arc,
    because that one runs in oblique ascension (III.1, 12)."""
    points = pdata(Sun=130.0)
    segs = engine["pn4_small_days"](points, 100.0)
    met = [s for s in segs if s["partner"] == "Sun" and s["partner_aspect"] == "body"]
    assert met[0]["from"] == pytest.approx(30.0 / (59 / 60 + 8 / 3600))
    assert met[0]["from_lon"] == pytest.approx(130.0)
    natal = engine["pn4_distribution_from_ascendant"](points, 100.0, 23.44, 43.78)
    met_natal = [s for s in natal if s["partner"] == "Sun" and s["partner_aspect"] == "body"]
    assert abs(met_natal[0]["from"] - 30.0) > 1.0


def test_pn4_small_days_opening_partner_is_looked_for_within_the_bound(engine):
    """IX.7, 30: "if in the bounds of the degree of the Ascendant of the
    revolution there was the body of a planet or its rays, the management
    ... will belong to it". The window is the BOUND: a body one degree
    behind the degree in the same bound is the partner from day 0."""
    # 22 Aries is Mars's Egyptian bound (20-25); the Sun at 21 Aries is in it.
    segs = engine["pn4_small_days"](pdata(Sun=21.0), 22.0)
    assert segs[0]["distributor"] == "Mars"
    assert segs[0]["partner"] == "Sun" and segs[0]["partner_aspect"] == "body"
    assert segs[0]["opened_by"] == "at the revolution: Sun by body"


def test_pn4_small_days_window_is_the_bound_not_the_sign(engine):
    """The negative control, and the point where IX.7, 30 differs from
    III.1, 23-25. The Sun at 19 Aries is behind 22 Aries in the SAME SIGN
    but in Mercury's bound (12-20), not Mars's (20-25): the Ascendant's
    natal distribution takes it as the birth partner, the small days do
    not, and cite IX.7, 30 for the distributor acting alone."""
    points = pdata(Sun=19.0)
    natal = engine["pn4_distribution_from_ascendant"](points, 22.0, 23.44, 43.78)
    assert natal[0]["partner"] == "Sun"
    segs = engine["pn4_small_days"](points, 22.0)
    assert segs[0]["partner"] is None
    assert "IX.7, 24 and 30" in segs[0]["partner_from"]
    assert segs[0]["opened_by"] == "at the revolution: the distributor alone"


def test_pn4_small_days_body_ahead_in_the_bound_manages_on_arrival(engine):
    """The owner's reading of IX.7, 30's silence: a body AHEAD of the
    degree within its bound is not the opening partner; the direction
    reaches it and III.1, 16 gives it the management then. The Sun at 24
    Aries, two degrees ahead of 22 Aries in Mars's bound, is met at
    2 / (59' 08") = 2.03 days, not on day 0."""
    segs = engine["pn4_small_days"](pdata(Sun=24.0), 22.0)
    assert segs[0]["partner"] is None
    assert segs[1]["partner"] == "Sun" and segs[1]["from"] == pytest.approx(2.0 / (59 / 60 + 8 / 3600))


def test_pn4_small_days_start_from_the_revolutions_ascendant(engine):
    """The bundle directs the REVOLUTION'S Ascendant through the
    revolution's own bodies and rays (IX.7, 29-30 sit inside the
    revolution), not the natal Ascendant, and counts days from the
    moment of the revolution."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    bundle = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule)
    segs = bundle["small_days"]
    assert segs[0]["from_lon"] == pytest.approx(bundle["sr"]["ascendant"])
    assert abs(segs[0]["from_lon"] - chart["ascendant"]) > 1.0
    assert 0.0 <= bundle["day_of_year"] < 366.0
    assert bundle["small_days_current"] is not None
    assert bundle["small_days_rows"][0]["From day"] == "0.00"


# --- IX.7, 23-28: the mighty days (built 2026-09-10) ----------------------
# No worked example exists in PN IV. These pin the printed rate and its
# consequence, the zodiacal measure, the crossing of the sign boundary
# under IX.7, 24, the bound-window opening, and the point directed.

MIGHTY_DAY = 12 + 1 / 6 + 1 / 120                          # IX.7, 25's parenthetical: 12.175 d
MIGHTY_DAY_HYBRID = 12 + 4 / 24 + 10 / 1440 + 30 / 86400    # Dykes's "<4 hours>" + the minutes read as clock time


def test_pn4_mighty_days_rate_is_the_authors_fraction_and_its_year_is_365_and_a_quarter(engine):
    """IX.7, 25: "12 days, <4 hours>, 10 minutes, and 30 seconds (and that
    is 1/6 of a day and half a sixth of a tenth of a day)" a degree. The
    parenthetical is the author's own number, 12 + 1/6 + 1/120 = 12.175 d,
    and thirty of them are 365 1/4 days exactly (IX.7, 28). The "<4 hours>"
    is Dykes's pointed-bracket supply and the hybrid 12 d 4 h 10 m 30 s
    (365 d 5 h 15 m for thirty) is neither the manuscript's number nor the
    author's; it was applied 2026-09-10 as "the printed rate" and replaced
    by the owner on 2026-09-11 (sheet row 13). The fixture rejects it."""
    assert engine["pn4_mighty_days_arc_to_days"](1.0) == pytest.approx(MIGHTY_DAY)
    segs = engine["pn4_mighty_days"](pdata(Sun=100.0, Moon=200.0), 10.0)
    assert segs[0]["from"] == 0.0
    year = segs[-1]["to"]
    assert year == pytest.approx(365.25, abs=1e-9)
    assert year != pytest.approx(30 * MIGHTY_DAY_HYBRID, abs=1e-3)
    for a, b in zip(segs, segs[1:]):
        assert a["to"] == pytest.approx(b["from"], abs=1e-9) and a["to"] > a["from"]


def test_pn4_mighty_days_are_zodiacal_and_cross_the_sign_boundary(engine):
    """Thirty degrees are the year (IX.7, 28) and there is no ascension in
    the sentence: a body ten degrees ahead is met at ten printed days,
    wherever the native was born. And the direction does not stop at the
    end of the sign: from 25 Aries it leaves Saturn's bound for Venus's
    at 0 Taurus, five degrees on, "then to the lord of the bound which
    follows it" (IX.7, 24), and runs on to 25 Taurus."""
    segs = engine["pn4_mighty_days"](pdata(Sun=35.0), 25.0)
    assert segs[0]["distributor"] == "Saturn"                       # 25 Aries, Egyptian
    venus = [s for s in segs if s["opened_by"].startswith("bound of Venus at 00")]
    assert venus and venus[0]["from"] == pytest.approx(5 * MIGHTY_DAY)
    met = [s for s in segs if s["partner"] == "Sun" and s["partner_aspect"] == "body"]
    assert met[0]["from"] == pytest.approx(10 * MIGHTY_DAY)
    assert met[0]["from_lon"] == pytest.approx(35.0)
    assert segs[-1]["to"] == pytest.approx(30 * MIGHTY_DAY)


def test_pn4_mighty_days_opening_window_is_the_bound(engine):
    """IX.7, 23: "if the body of a planet or its rays was in the bounds of
    that degree, then the management of the days will belong to it". A
    body behind the degree in its bound is the partner from day 0; one
    behind it in the previous bound of the same sign is not, and the
    distributor acts alone."""
    within = engine["pn4_mighty_days"](pdata(Sun=21.0), 22.0)          # both in Mars's 20-25 Aries
    assert within[0]["partner"] == "Sun"
    assert within[0]["opened_by"] == "at the revolution: Sun by body"
    outside = engine["pn4_mighty_days"](pdata(Sun=19.0), 22.0)         # Sun in Mercury's 12-20
    assert outside[0]["partner"] is None
    assert "IX.7, 24 and 30" in outside[0]["partner_from"]


def test_pn4_mighty_days_direct_the_terminal_point_through_the_revolution(engine):
    """IX.7, 23: the degree directed is the terminal point -- the natal
    Ascendant's degree in the sign of the year -- and it is read "in the
    revolution of the year". The bundle starts the direction from the
    terminal point, not from the revolution's Ascendant and not from the
    natal Ascendant itself."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    bundle = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule)
    start = bundle["mighty_days"][0]["from_lon"]
    assert start == pytest.approx(bundle["year"]["longitude"])
    assert start % 30.0 == pytest.approx(chart["ascendant"] % 30.0)      # the same degree, in the sign of the year
    assert abs(start - chart["ascendant"]) > 1.0                          # age 42: six signs on
    assert abs(start - bundle["sr"]["ascendant"]) > 1.0
    assert bundle["mighty_days_rows"][0]["From day"] == "0.00"


# --- VI.1: the lord of the orb (built 2026-09-10) -------------------------

def test_pn4_lord_of_the_orb_against_dykes_worked_example(engine):
    """The author gives no example; the editor does (Intro Sect. 13,
    Figures 46-47): a nocturnal birth in the second night hour of a
    Wednesday, natal hour lord Venus. "At Age 1 the lord of the year is
    the Moon, with its lord of the orb Mercury"; "ages 9 and 10: the Moon
    and Saturn"; "the new lord of the orb for Age 12 is Mars, not Venus.
    At Age 13 ... the Sun"; "at Age 82 ... Mars will likewise be the lord
    of the orb, as Mars is always the sixth lord from Venus". Every value
    follows from VI.1, 8's continuous loop down the spheres."""
    orb = engine["pn4_lord_of_the_orb"]
    assert [orb("Venus", a) for a in (0, 1, 9, 10, 12, 13, 82)] == [
        "Venus", "Mercury", "Moon", "Saturn", "Mars", "Sun", "Mars"]


def test_pn4_lord_of_the_orb_loops_and_does_not_reset(engine):
    """VI.1, 8: "the lord of the thirteenth hour from it belongs to the
    Ascendant of the root and the thirteenth year". The negative control
    is Dykes' single-cycle alternative (Intro Figure 48), under which the
    Ascendant's lord at age 12 would be the natal lord again. It is not:
    the loop of seven against the cycle of twelve gives a different lord
    at 12, 24, 36, 48, 60 and 72, and the natal lord returns only at 84."""
    orb = engine["pn4_lord_of_the_orb"]
    for natal in engine["PN4_DESCENDING_SPHERES"]:
        assert orb(natal, 0) == natal
        for cycle in range(1, 7):
            assert orb(natal, 12 * cycle) != natal
        assert orb(natal, 84) == natal
    assert orb("Pluto", 3) is None


def test_pn4_named_lords_of_the_orb_by_vi_1_10s_naming(engine):
    """VI.1, 10: "the lord of the hour of the house of assets" is the
    second hour lord from the natal one -- the name is fixed to the hour
    number. VI.1, 18-19 use those names for the Ascendant, Midheaven and
    house of hope of the root, and for the sign of the year with the
    tenth and eleventh from it. With Venus natal the hours run Venus,
    Mercury, Moon, Saturn, Jupiter, Mars, Sun and round again, so hours
    10 and 11 are the Moon and Saturn -- which is what Dykes' example
    gives for the natal tenth and eleventh ("ages 9 and 10: the Moon and
    Saturn")."""
    rows = engine["pn4_named_lords_of_the_orb"]("Venus", 14)     # age 14: sign of the year in house 3
    by = {r["Position"]: r for r in rows}
    assert by["Ascendant of the root"]["Lord of the hour (VI.1, 10)"] == "Venus"
    assert by["Midheaven of the root"]["Lord of the hour (VI.1, 10)"] == "Moon"          # hour 10
    assert by["House of hope of the root"]["Lord of the hour (VI.1, 10)"] == "Saturn"    # hour 11
    assert by["Sign of the terminal point"]["House"] == 3
    assert by["Sign of the terminal point"]["Lord of the hour (VI.1, 10)"] == "Moon"     # hour 3
    assert by["Tenth from the sign of the year"]["House"] == 12
    assert by["Eleventh from the sign of the year"]["House"] == 1
    assert by["Eleventh from the sign of the year"]["Lord of the hour (VI.1, 10)"] == "Venus"
    # Dykes' "reset" would make the third house's lord at age 14 the natal
    # lord (Venus); VI.1, 10's naming keeps it the third hour lord (Moon).
    assert by["Sign of the terminal point"]["Lord of the hour (VI.1, 10)"] != "Venus"


def test_pn4_bundle_carries_the_lord_of_the_orb_as_indicator_five(engine):
    """II.1, 10: "The fifth is the lord of the orb." The bundle's
    indicators table gains row 5 from the natal hour lord it is handed,
    and says so when it is handed none."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    target = datetime(2027, 6, 1).date()                                # age 42
    with_hour = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), target, rule,
                                            {"Hour Lord": "Venus", "Approximate": False})
    row = with_hour["year_rows"][4]
    assert row["#"] == 5 and row["Ruler"] == "Venus"                    # 42 = 6 x 7: the natal lord again
    assert "cycle 4" in row["Active point"]
    assert len(with_hour["orb_rows"]) == 6
    without = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), target, rule)
    assert without["year_rows"][4]["Ruler"] == "-"
    assert without["year_rows"][4]["Active point"] == "natal hour lord unavailable"


# --- VI.2, 1-26: the turning of the houses of the root (built 2026-09-10) --

def _turning_chart(engine, asc=5.0, cusps=None, sect="Diurnal", **planets):
    """A minimal chart_data for pn4_turning_rows. Default cusps are the
    whole-sign starts, so no house is displaced unless the test says so."""
    if cusps is None:
        base = (asc // 30.0) * 30.0
        cusps = [(base + 30.0 * i) % 360.0 for i in range(12)]
    seven = dict(Sun=100.0, Moon=200.0, Mercury=110.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=20.0)
    seven.update(planets)
    return {"planetary_data": pdata(**seven), "ascendant": asc, "houses": cusps, "sect": sect}


def test_pn4_turning_is_from_each_points_own_position(engine):
    """VI.2, 1: "turned ... from its own position (a year for every
    sign)". Three years on, the Sun at 10 Cancer is in Libra, house 3 of
    an Aries Ascendant (Gemini) is in Virgo, and the Lot of the father is
    three signs from where it stands natally -- each from its own sign,
    none from the sign of the year."""
    rows = {r["Point"]: r for r in engine["pn4_turning_rows"](_turning_chart(engine), 3)}
    assert rows["Sun"]["Turned to"] == "Libra"
    assert rows["House 3 (by counting)"]["Natal"].startswith("Gemini")
    assert rows["House 3 (by counting)"]["Turned to"] == "Virgo"
    father = next(r for k, r in rows.items() if k.startswith("Lot of the father"))
    natal_sign = father["Natal"].split(" ")[0]
    order = engine["SIGN_ORDER"]
    assert father["Turned to"] == order[(order.index(natal_sign) + 3) % 12]
    assert engine["pn4_turned_sign"](100.0, 0) == "Cancer"


def test_pn4_turning_reports_the_fortune_or_infortune_reached(engine):
    """VI.2, 1: "when any of them ... reaches a sign or planetary fortune
    or infortune, it produces the indication of that sign or planet". The
    row names the natal planets in the sign reached, tagged; Jupiter at
    10 Sagittarius is reached by the Sun (10 Cancer) at age 5."""
    rows = {r["Point"]: r for r in engine["pn4_turning_rows"](_turning_chart(engine), 5)}
    assert rows["Sun"]["Turned to"] == "Sagittarius"
    assert rows["Sun"]["Natal planets there"] == "Jupiter (fortune)"
    assert rows["Moon"]["Natal planets there"] == "none"          # 20 Libra + 5 = Pisces, empty


def test_pn4_turning_displaced_cusp_is_turned_both_ways(engine):
    """VI.2, 22-24: when "the [natal] degree of the house of children fell
    in the sixth sign ... the turning in the indication of the condition
    of children will be from two signs: one of them is from the fifth
    house by counting, and the second is from the sixth sign". With the
    fifth cusp at 2 Virgo under an Aries Ascendant, house 5 gets two
    rows; house 6, whose cusp sits in its own sign, gets one."""
    base = 0.0
    cusps = [(base + 30.0 * i) % 360.0 for i in range(12)]
    cusps[4] = 152.0                                            # 2 Virgo, the sixth sign
    rows = engine["pn4_turning_rows"](_turning_chart(engine, asc=5.0, cusps=cusps), 1)
    five = [r for r in rows if r["Point"].startswith("House 5")]
    assert len(five) == 2
    assert five[0]["Turned to"] == "Virgo"               # Leo by counting, a year on
    assert five[1]["Turned to"] == "Libra"               # from Virgo, where the degree falls
    assert "VI.2, 21-24" in five[1]["Source"]
    assert len([r for r in rows if r["Point"].startswith("House 6")]) == 1


def test_pn4_turning_direction_column_refuses_and_points_to_the_distributions(engine):
    """Only the turning is built. Planets and Lots say the direction is
    III.1, 12's third case; ordinary houses cite VI.2, 21's semi-arcs
    with no procedure; houses 1, 10 and 4 point to the distributions the
    page already applies."""
    rows = {r["Point"]: r for r in engine["pn4_turning_rows"](_turning_chart(engine), 2)}
    assert rows["Mars"]["Directed a year per degree"].startswith("refused")
    assert "III.1, 12" in rows["Mars"]["Directed a year per degree"]
    assert "VI.2, 21" in rows["House 7 (by counting)"]["Directed a year per degree"]
    assert "Ascendant" in rows["House 1 (by counting)"]["Directed a year per degree"]
    assert "Midheaven" in rows["House 10 (by counting)"]["Directed a year per degree"]
    assert "fourth" in rows["House 4 (by counting)"]["Directed a year per degree"]
    lot = next(r for k, r in rows.items() if k.startswith("Lot of travel"))
    assert lot["Directed a year per degree"].startswith("refused")


def test_pn4_turning_parents_indicators_follow_the_sect(engine):
    """VI.2, 6 and 8: "the Sun or Saturn ... (whichever one of the two had
    the shift in the root)", "Venus or the Moon": fn 16 and 19 read the
    shift as sect. By day the Sun and Venus carry the parents; by night
    Saturn and the Moon."""
    day = engine["pn4_turning_planet_topics"]("Diurnal")
    night = engine["pn4_turning_planet_topics"]("Nocturnal")
    assert "fathers" in day["Sun"] and "fathers" not in day["Saturn"]
    assert "mother" in day["Venus"] and "mother" not in day["Moon"]
    assert "fathers" in night["Saturn"] and "fathers" not in night["Sun"]
    assert "mother" in night["Moon"] and "mother" not in night["Venus"]


def test_pn4_turning_lots_are_paired_to_dykes_footnotes_and_say_where_they_differ(engine):
    """Which "twelve Lots" VI.2, 1 means is not stated; fn 12-31 are the
    editor's identifications. Every Lot VI.2 names is present with its
    footnote cited, fn 31's three enemy Lots all appear, and the two
    rows whose engine formula does not reverse at night where the
    footnote does say so in the row."""
    rows = engine["pn4_turning_rows"](_turning_chart(engine), 0)
    lots = [r for r in rows if r["Point"].startswith("Lot")]
    cites = {r["Source"] for r in lots}
    for fn in ("fn 12", "fn 15", "fn 17", "fn 20", "fn 22", "fn 24", "fn 25", "fn 26", "fn 27", "fn 28", "fn 29", "fn 30", "fn 31"):
        assert any(fn in c for c in cites), fn
    assert sum(1 for r in lots if "fn 31" in r["Source"]) == 3
    siblings = next(r for r in lots if r["Point"].startswith("Lot of siblings"))
    assert "fn 15 reverses it at night" in siblings["Point"]
    assert len([r for r in lots if "fn 26 reverses" in r["Point"]]) == 2


# --- II.1, 11-24: indicators 6-19, the fact each reads (built 2026-09-10) --

def _two_charts(engine, natal=None, rev=None, n_asc=5.0, r_asc=95.0, year_lon=None):
    """A root and a revolution for pn4_further_indicators, planets given
    as longitudes. The Node is carried like the engine's chart."""
    base = dict(Sun=100.0, Moon=200.0, Mercury=110.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=20.0)
    n = dict(base); n.update(natal or {})
    r = dict(base); r.update(rev or {})
    root = {"planetary_data": pdata(**n), "ascendant": n_asc, "houses": [], "sect": "Diurnal"}
    root["planetary_data"]["North Node"] = {"longitude": r.pop("North_Node", 40.0), "latitude": 0.0, "distance": 1.0,
                                           "speed_in_lon": -0.05, "speed_in_lat": 0.0, "speed_in_dist": 0.0}
    sr = {"planetary_data": pdata(**r), "ascendant": r_asc, "houses": [], "sect": "Diurnal"}
    sr["planetary_data"]["North Node"] = dict(root["planetary_data"]["North Node"])
    return root, sr, (year_lon if year_lon is not None else n_asc)


def _rows(engine, **kw):
    root, sr, year_lon = _two_charts(engine, **kw)
    return {r["#"]: r for r in engine["pn4_further_indicators"](root, sr, year_lon)}


def test_pn4_further_indicators_are_fourteen_in_ii_1_25s_order(engine):
    """II.1, 11-24: indicators 6 to 19, one row each, in the ranking's
    order. The four that are not lookups say what they do not compute."""
    rows = _rows(engine)
    assert sorted(rows) == list(range(6, 20))
    assert "NOT computed" in rows[7]["Reads"] and "II.22" in rows[7]["Reads"]
    assert "NOT computed" in rows[15]["Reads"]
    assert rows[16]["Reads"].startswith("NOT tracked") and rows[17]["Reads"].startswith("NOT tracked")


def test_pn4_transit_over_rooted_position_is_graded_as_v_1_2_3(engine):
    """V.1, 2-3: a planet in the revolution "reaches its own rooted
    degree", or "the bound which it was in at the root", or "[only] that
    sign". Saturn natal 20 Aries (Mars's bound 20-25): the revolution's
    Saturn at 20.5 is by degree, at 23 by bound, at 27 (Saturn's bound)
    by sign, and at 35 not at all."""
    grade = engine["_pn4_transit_grade"]
    assert grade(20.5, 20.0) == "degree"
    assert grade(23.0, 20.0) == "bound"
    assert grade(27.0, 20.0) == "sign"
    assert grade(35.0, 20.0) is None
    rows = _rows(engine, rev=dict(Saturn=23.0, Mars=100.4))       # Mars on natal Sun's degree
    assert "Saturn on its own place, by bound" in rows[8]["Reads"]
    assert "Mars on natal Sun place, by degree" in rows[8]["Reads"]
    quiet = _rows(engine, rev=dict(Sun=40.0, Moon=70.0, Mercury=75.0, Venus=160.0, Mars=220.0, Jupiter=280.0, Saturn=340.0))
    assert quiet[8]["Reads"] == "none, even by sign"


def test_pn4_three_lords_are_counted_from_their_own_ascendants(engine):
    """VI.6, 1 with fn 128: "relative to its own Ascendant. So if the
    Ascendant of the revolution was Scorpio, see where Mars falls in the
    revolutionary houses, relative to Scorpio." Revolution Ascendant 5
    Scorpio, Mars at 10 Capricorn: house 3 from Scorpio."""
    rows = _rows(engine, r_asc=215.0, rev=dict(Mars=280.0))
    assert "lord of the Ascendant of the revolution (Mars): house 3 from Scorpio" in rows[10]["Reads"]
    # natal Ascendant 5 Aries, its lord Mars at 10 Capricorn: house 10 from Aries
    assert "lord of the natal Ascendant (Mars): house 10 from Aries" in rows[10]["Reads"]


def test_pn4_coincidence_of_terminal_sign_and_revolution_ascendant(engine):
    """VI.3, 3: "if the sign of the terminal point and the Ascendant of
    the revolution were a single house of the rooted circle". Terminal
    sign Cancer (natal house 4 from Aries) and revolution Ascendant 5
    Cancer: one house; with the revolution Ascendant in Leo, two."""
    one = _rows(engine, year_lon=95.0, r_asc=97.0)
    assert "natal house 4" in one[12]["Reads"] and "ONE house" in one[12]["Reads"]
    assert "revolution planets there: Sun, Mercury" in one[12]["Reads"]          # 10 and 20 Cancer
    two = _rows(engine, year_lon=95.0, r_asc=125.0)
    assert "two different houses" in two[12]["Reads"]
    # VI.4, 1: natal planets in the terminal sign
    assert one[13]["Reads"].startswith("natal planets in the terminal sign Cancer: Sun, Mercury")


def test_pn4_house_shift_and_nodes_count_from_the_three_places(engine):
    """VI.5, 1: the three places are the natal Ascendant, the sign of the
    terminal point, and the revolution's Ascendant; VII.9, 1 reads the
    Head and Tail against the same three. Natal Ascendant Aries,
    terminal sign Cancer, revolution Ascendant Libra: the Sun at 10
    Cancer is natal house 4, then 4 / 1 / 10; the Head at 10 Taurus is
    houses 2 / 11 / 8 and the Tail 8 / 5 / 2."""
    rows = _rows(engine, year_lon=95.0, r_asc=185.0)
    assert "Sun: natal 4 -> 4 / 1 / 10" in rows[14]["Reads"]
    assert "Head in Taurus, houses 2 / 11 / 8; Tail in Scorpio, houses 8 / 5 / 2" in rows[19]["Reads"]
    # VIII: own house or another's, own bound or another's -- Mars 0 Aquarius is
    # in Saturn's house and Mercury's bound (Egyptian Aquarius 0-7)
    assert "Mars in Aquarius (house of Saturn; bound of Mercury)" in rows[18]["Reads"]
    assert "Jupiter in Sagittarius (own house;" in rows[18]["Reads"]


# --- IX.9, 1-10 and IX.2, 4-7: the governor (built 2026-09-10) -------------

def test_pn4_governor_tally_counts_the_available_and_never_claims_alone(engine):
    """IX.9, 10: a planet is the governor ALONE only if all eight
    testimonies combine in it. Without the releaser's distribution
    (Sahl, On Nativities 1.15, passed in by the bundle since 2026-09-10)
    #3 is unavailable and #4, "the partner to them both", is not counted
    -- it is counted only when the two distributions share one partner
    (a reading) -- and with the connection uncomputed at most five are
    counted; even when all five agree the summary says primary with 5 of
    5 of eight, not the governor alone. With the releaser's distribution
    supplied and the same partner, seven; with a different partner, six.
    215 Scorpio: the revolution's Ascendant's domicile lord is Mars."""
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0)
    assert [r["#"] for r in rows] == list(range(1, 9))
    assert s["counted"] == 5 and s["primary"] == ["Mars"] and s["top"] == 5
    assert "ALONE" in s["text"] and "5 of the 5 testimonies available (of eight)" in s["text"]
    by = {r["#"]: r for r in rows}
    assert by[3]["Counted"] == "no" and "releaser" in by[3]["Planet"] and "IX.8, 123" in by[3]["Planet"]
    assert by[7]["Counted"] == "no" and "connection" in by[7]["Planet"]
    assert by[4]["Counted"] == "no" and "not counted" in by[4]["Planet"]
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0,
                                     releaser_distributor="Mars", releaser_partner="Mars")
    by = {r["#"]: r for r in rows}
    assert s["counted"] == 7 and by[3]["Planet"] == "Mars" and by[4]["Counted"] == "yes" and "both" in by[4]["Planet"]
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0,
                                     releaser_distributor="Venus", releaser_partner="Saturn")
    by = {r["#"]: r for r in rows}
    assert s["counted"] == 6 and by[3]["Planet"] == "Venus" and by[4]["Counted"] == "no" and "Saturn" in by[4]["Planet"]
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0, releaser_note="no releaser by 1.15")
    assert {r["#"]: r for r in rows}[3]["Planet"] == "unavailable: no releaser by 1.15"
    assert by[8]["Planet"] == "Mars" and by[8]["Source"] == "IX.9, 9"


def test_pn4_governor_primary_and_partners_and_missing_distribution(engine):
    """IX.9, 10: "if one of them had [only] some of the testimonies, it
    will be more primary than the others, and the rest of them will have
    a partnership with it". With the releaser's distribution supplied
    (distributor Venus, partner Saturn -- the same partner as the
    Ascendant's, so #4 counts): Saturn twice, Venus three times, Mars
    once, the Moon once; Venus primary. Without it, #4 is not counted and
    Saturn and Venus tie. With no distributor (the age past the table) #2
    and #4 are unavailable with the reason, and the tally counts four."""
    _rows, s = engine["pn4_governor"]("Saturn", "Venus", "Saturn", "", "Venus", "Mars", 95.0,   # Cancer: Moon
                                      releaser_distributor="Venus", releaser_partner="Saturn")
    assert s["tally"] == {"Saturn": 2, "Venus": 3, "Mars": 1, "Moon": 1} and s["primary"] == ["Venus"]
    _rows, s = engine["pn4_governor"]("Saturn", "Venus", "Saturn", "", "Venus", "Mars", 95.0)
    assert s["tally"] == {"Saturn": 1, "Venus": 2, "Mars": 1, "Moon": 1}
    _rows, s = engine["pn4_governor"]("Saturn", "Venus", "Saturn", "", "Venus", "Saturn", 95.0)
    assert s["primary"] == ["Saturn", "Venus"] and "are primary with 2" in s["text"]
    rows, s2 = engine["pn4_governor"]("Saturn", None, None, "age 786 is past the 120-year table", "Venus", "Mars", 95.0)
    by = {r["#"]: r for r in rows}
    assert by[2]["Counted"] == "no" and "past the 120-year table" in by[2]["Planet"]
    assert by[4]["Counted"] == "no"
    assert s2["counted"] == 4


def test_pn4_first_month_governor_against_dykes_fn_39(engine):
    """IX.2, 4 worked by Dykes at fn 39: at age 39 the natal Lot on the
    natal Ascendant profects with it to Cancer, "the Ascendant of the
    revolution and the Lot of the revolution are also on Cancer", and
    Cancer is convertible, so "the Moon is the lord of all of them" and
    Cancer governs the first month and the year. Natal Ascendant 5
    Aries, Lot 10 Aries, age 39 -> Cancer; revolution Ascendant 5 Cancer,
    Lot 20 Cancer."""
    year_lon = engine["pn4_profect"](5.0, 39)
    assert engine["get_zodiac_sign"](year_lon) == "Cancer"
    rows, verdict = engine["pn4_first_month_governor"](5.0, 10.0, year_lon, 95.0, 110.0)
    assert [r["Holds"] for r in rows] == ["yes"] * 5
    assert verdict.startswith("Cancer and its lord Moon govern the first month")
    assert "ninth-part lord Moon, sign lord Moon" in rows[4]["Reads"]


def test_pn4_first_month_governor_fails_one_condition_at_a_time(engine):
    """The negative controls, one condition each. The revolution's Lot in
    Leo fails #5; a fixed sign of the year fails the convertible test
    (fn 36); the natal Lot outside the Ascendant fails the first two."""
    year_lon = engine["pn4_profect"](5.0, 39)
    rows, verdict = engine["pn4_first_month_governor"](5.0, 10.0, year_lon, 95.0, 125.0)
    assert [r["Holds"] for r in rows][:5] == ["yes", "yes", "yes", "no", "yes"]      # the sixth row is IX.2, 5's tally (PN4R-4h-4)
    assert verdict.startswith("no governor: 1 of the five conditions fail")
    fixed = engine["pn4_profect"](35.0, 39)                          # Taurus -> Leo
    rows, _v = engine["pn4_first_month_governor"](35.0, 40.0, fixed, 125.0, 130.0)
    assert [r["Holds"] for r in rows][:5] == ["yes", "yes", "yes", "yes", "no"]
    rows, _v = engine["pn4_first_month_governor"](5.0, 40.0, year_lon, 95.0, 110.0)
    assert [r["Holds"] for r in rows][:2] == ["no", "no"]


# --- II.22, 1-4: the Moon's connections and the portions (built 2026-09-10)

def test_pn4_moon_portions_divide_the_year_by_the_count(engine):
    """II.22, 2: two planets, halves; three, thirds; more, "according to
    their number"; none, no division. Each portion is owned by one planet
    in the order of connection."""
    portions = engine["pn4_moon_portions"]
    two = portions([{"planet": "Venus"}, {"planet": "Mars"}], 365.25)
    assert [(p["planet"], p["from_day"], p["to_day"]) for p in two] == [
        ("Venus", 0.0, 365.25 / 2), ("Mars", 365.25 / 2, 365.25)]
    three = portions([{"planet": "Saturn"}, {"planet": "Sun"}, {"planet": "Jupiter"}], 366.0)
    assert [p["of"] for p in three] == [3, 3, 3] and three[1]["from_day"] == pytest.approx(122.0)
    assert portions([], 365.25) == []


def test_pn4_moon_connections_perfect_inside_her_sign(engine):
    """II.22, 1: the connection counts only "so long as she is in her
    [current] sign". Every connection the simulator reports must perfect
    before her sign exit, with the Moon still in her starting sign and
    the aspect exact to the ephemeris at that moment, in day order."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    natal_sun = chart["planetary_data"]["Sun"]["longitude"]
    for age in (30, 41, 42, 55):
        jd_sr = engine["pn4_solar_revolution_jd"](chart["julian_day"], natal_sun, age)
        sr = cast(engine["pn4_datetime_from_jd"](jd_sr), lat, lon)
        moon = engine["pn4_moon_connections"](sr["planetary_data"], jd_sr)
        assert moon["sign"] == engine["get_zodiac_sign"](sr["planetary_data"]["Moon"]["longitude"])
        assert 0.0 < moon["exit_day"] < 3.0
        days = [c["day"] for c in moon["connections"]]
        assert days == sorted(days)
        for c in moon["connections"]:
            assert 0.0 < c["day"] < moon["exit_day"]
            assert engine["get_zodiac_sign"](c["moon_at"]) == moon["sign"]
            swe = engine["swe"]
            m = swe.calc_ut(jd_sr + c["day"], swe.MOON)[0][0]
            p = swe.calc_ut(jd_sr + c["day"], engine["PLANET_SWE_IDS"][c["planet"]])[0][0]
            target = {"body": 0.0, "sextile": 60.0, "square": 90.0, "trine": 120.0, "opposition": 180.0}[c["aspect"]]
            sep = abs(engine["_wrap180"](m - p))
            assert abs(sep - target) < 0.05
        assert moon["void"] == (not moon["connections"])


def test_pn4_moon_empty_in_course_falls_to_her_house_lord(engine):
    """II.22, 4: "if the Moon was empty in course, his situation will be
    in accordance with the condition of the lord of her house". Built by
    construction: a moment when the Moon is within a third of a degree of
    the end of her sign and no planet's body or ray lies in the little
    arc she has left, found by searching the ephemeris."""
    swe = engine["swe"]
    ids = engine["PLANET_SWE_IDS"]
    jd = swe.julday(2000, 1, 1, 0.0)
    found = None
    for k in range(4000):
        t = jd + k * 0.02
        m = swe.calc_ut(t, swe.MOON)[0][0] % 360.0
        left = 30.0 - (m % 30.0)
        if left > 0.3:
            continue
        clear = True
        for name, pid in ids.items():
            if name == "Moon":
                continue
            p = swe.calc_ut(t, pid)[0][0]
            for target in (0.0, 60.0, 90.0, 120.0, 180.0):
                for off in (target, -target):
                    ahead = (p + off - m) % 360.0
                    if ahead < left + 0.5:
                        clear = False
        if clear:
            found = t
            break
    assert found is not None
    data = {name: {"longitude": swe.calc_ut(found, pid)[0][0] % 360.0, "latitude": 0.0, "distance": 1.0,
                   "speed_in_lon": 1.0, "speed_in_lat": 0.0, "speed_in_dist": 0.0} for name, pid in ids.items()}
    moon = engine["pn4_moon_connections"](data, found)
    assert moon["void"] and moon["connections"] == []
    assert moon["house_lord"] == engine["SIGN_TO_DOMICILE"][moon["sign"]]
    assert engine["pn4_moon_testimony"](moon) == moon["house_lord"]


def test_pn4_governor_counts_the_moons_testimony_when_it_is_read(engine):
    """IX.9, 8: "the one accepting the connection of the Moon, or the lord
    of her house". Handed the Moon's testimony the governor counts seven
    of eight (with the releaser's distribution and a shared partner, all
    eight); handed none it still says why #7 is unavailable."""
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0, "Venus", False)
    by = {r["#"]: r for r in rows}
    assert by[7]["Counted"] == "yes" and by[7]["Planet"].startswith("Venus; accepting her connection")
    assert s["counted"] == 6 and s["tally"] == {"Mars": 5, "Venus": 1}
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0, "Venus", False,
                                     releaser_distributor="Mars", releaser_partner="Mars")
    assert s["counted"] == 8 and s["tally"] == {"Mars": 7, "Venus": 1} and "1 are unavailable" not in s["text"]
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0, "Saturn", True)
    assert "empty in course" in {r["#"]: r for r in rows}[7]["Planet"]
    rows, s = engine["pn4_governor"]("Mars", "Mars", "Mars", "", "Mars", "Mars", 215.0)
    assert {r["#"]: r for r in rows}[7]["Counted"] == "no" and s["counted"] == 5


def test_pn4_bundle_reads_the_moon_into_indicator_seven_and_the_portions(engine):
    """The bundle fills indicator #7 from II.22 and carries the portions;
    "NOT computed" no longer appears on that row."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule,
                                    {"Hour Lord": "Venus", "Approximate": False})
    row7 = next(r for r in b["further_rows"] if r["#"] == 7)
    assert "NOT computed" not in row7["Reads"]
    assert 360.0 < b["year_days"] < 370.0
    assert len(b["moon_portions"]) == len(b["moon"]["connections"])
    if b["moon_portions"]:
        assert b["moon_portions"][-1]["to_day"] == pytest.approx(b["year_days"])
    gov_rows, gov = b["governor"]
    assert {r["#"]: r for r in gov_rows}[7]["Counted"] == "yes"


# --- III.2: the distribution analysed (built 2026-09-10) -------------------

def _seg(distributor, partner, frm, to=None, aspect="body"):
    return {"from": frm, "to": to if to is not None else frm + 1.0, "from_lon": 0.0,
            "distributor": distributor, "partner": partner, "partner_aspect": aspect if partner else None,
            "partner_from": "", "opened_by": ""}


def test_pn4_iii2_static_types_by_nature_and_dykes_figure_67(engine):
    """III.2, 10-17: the seven types. Figure 67 / fn 56: "the directed
    Ascendant has reached the bound of Mars in Leo, with its partner
    Venus sending a sextile ray to it. So, the distribution is
    Mars-Venus" -- an infortune distributing with a fortune partnering,
    the third type (III.2, 13). The Sun, Moon and Mercury have no type
    by nature, and type 5 is never assigned."""
    t = engine["pn4_static_type"]
    assert t("Mars", "Venus")[0] == 3
    assert t("Venus", "Mars")[0] == 4
    assert t("Jupiter", None)[0] == 1 and t("Saturn", None)[0] == 2
    assert t("Saturn", "Mars")[0] == 6 and t("Venus", "Jupiter")[0] == 7
    assert t("Sun", "Venus")[0] is None and "neither fortune nor infortune" in t("Sun", "Venus")[1]
    assert t("Venus", "Mercury")[0] is None
    assert all(n != 5 for n in (t(d, p)[0] for d in ("Jupiter", "Venus", "Saturn", "Mars")
                                for p in (None, "Jupiter", "Venus", "Saturn", "Mars")))


def test_pn4_iii2_twenty_four_map_to_twelve_indications(engine):
    """III.2, 57: "these six indicators ... are in twenty-four ways";
    III.2, 87: twelve indications, "four of them are called a paired
    indication, and eight of them are called a double indication". Every
    numbered transition answers to exactly one indication; the isolated
    eight to the paired four, the qualified sixteen to the doubled eight;
    and each qualified number is the isolated one plus its context."""
    trans = engine["PN4_III2_TRANSITIONS"]
    assert sorted(trans) == list(range(1, 25))
    paired, doubled = engine["PN4_III2_PAIRED"], engine["PN4_III2_DOUBLED"]
    assert len(paired) == 4 and len(doubled) == 8
    for n, (kind, f, t, c) in trans.items():
        if c is None:
            assert 1 <= n <= 8 and (f, t) in paired
        else:
            assert 9 <= n <= 24 and (f, t, c) in doubled
    numbers = engine["pn4_transition_numbers"]
    assert numbers("bound", "fortune", "fortune", "fortune") == [1, 9]
    assert numbers("management", "infortune", "fortune", "infortune") == [7, 22]
    assert numbers("bound", "infortune", "infortune", None) == [4]
    # the sentences that mention death are gated on III.2, 110-111
    gated = {c for c, _t, d in list(paired.values()) + list(doubled.values()) if d}
    assert gated == {"III.2, 90", "III.2, 91", "III.2, 98", "III.2, 99", "III.2, 100"}


def test_pn4_iii2_shift_classification_quotes_the_sentence(engine):
    """III.2, 60 / 71 and 97: the distribution shifting "from the bound of
    a fortune to the bound of an infortune, in the management of a
    fortune" is #2 and #11, and "in that year it indicates a middling
    condition in suitability and corruption, and good and evil, even
    though the indication of evil is stronger" (97). III.2, 66 / 83 and
    96: the management shifting from an infortune to a fortune in the
    bound of an infortune is #7 and #22 (96). A death sentence carries the
    gate; a neutral planet is not among the twenty-four."""
    classify = engine["pn4_classify_shift"]
    rows = classify(_seg("Venus", "Jupiter", 3.0), _seg("Saturn", "Jupiter", 4.0))
    assert len(rows) == 1 and rows[0]["numbers"] == [2, 11]
    assert "middling condition in suitability and corruption" in rows[0]["indication"]
    assert "III.2, 97" in rows[0]["indication"] and "III.2, 90" in rows[0]["indication"]
    rows = classify(_seg("Mars", "Saturn", 3.0), _seg("Mars", "Venus", 4.0, aspect="trine"))
    assert rows[0]["numbers"] == [7, 22] and "III.2, 96" in rows[0]["indication"]
    rows = classify(_seg("Venus", "Venus", 3.0), _seg("Mars", "Mars", 4.0))
    assert len(rows) == 2 and rows[0]["numbers"] == [2, 12] and "110-111" in rows[0]["indication"]
    assert rows[1]["numbers"] == [6, 20]
    assert "harshest adversity" not in rows[0]["indication"]        # not all four infortunes
    rows = classify(_seg("Saturn", "Mars", 3.0), _seg("Mars", "Saturn", 4.0))
    assert "greatest and harshest adversity" in rows[0]["indication"] and "III.2, 101" in rows[0]["indication"]
    rows = classify(_seg("Jupiter", "Venus", 3.0), _seg("Venus", "Jupiter", 4.0))
    assert "good fortune upon good fortune" in rows[0]["indication"] and "III.2, 93" in rows[0]["indication"]
    rows = classify(_seg("Venus", "Sun", 3.0), _seg("Mars", "Sun", 4.0))
    assert rows[0]["numbers"] == [2] and "is neither" in rows[0]["indication"]
    rows = classify(_seg("Mercury", "Venus", 3.0), _seg("Mars", "Venus", 4.0))
    assert rows[0]["numbers"] == [] and "not among the twenty-four" in rows[0]["indication"]
    assert classify(_seg("Mars", "Venus", 3.0), _seg("Mars", "Venus", 4.0)) == []


def test_pn4_iii2_transitions_fall_inside_the_year(engine):
    """III.2, 55: "within one of the years it will shift". Only the
    boundaries with age <= from < age + 1 are this year's; a boundary at
    exactly the next birthday belongs to the next year."""
    segs = [_seg("Venus", None, 0.0, 3.5), _seg("Saturn", None, 3.5, 4.0), _seg("Saturn", "Jupiter", 4.0, 4.7),
            _seg("Mars", "Jupiter", 4.7, 9.0)]
    rows = engine["pn4_year_transitions"](segs, 3)
    assert [r["At age"] for r in rows] == ["3.50"] and rows[0]["Transition"] == "#2"
    rows = engine["pn4_year_transitions"](segs, 4)
    assert [r["At age"] for r in rows] == ["4.00", "4.70"]
    assert rows[1]["Transition"] == "#4, #15"
    assert engine["pn4_year_transitions"](segs, 6) == []
    assert engine["pn4_year_transitions"](None, 6) == []


def test_pn4_iii2_checklist_reads_the_bound_as_facts(engine):
    """III.2, 4-9 answered as facts for the bound the distribution stands
    in. Current segment opened at 22 Aries, Mars's Egyptian bound
    (20-25): the bound and its span; the places from the three signs;
    the sign's rulers; who is in Aries in root and revolution; who casts
    rays into 20-25 Aries -- the Sun at 20 Cancer squares 20 Aries."""
    root = {"planetary_data": pdata(Sun=110.0, Moon=200.0, Mercury=100.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=23.0),
            "ascendant": 5.0, "houses": [], "sect": "Diurnal"}
    rev = {"planetary_data": pdata(Sun=110.0, Moon=21.0, Mercury=100.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=(24.0, -0.05)),
           "ascendant": 95.0, "houses": [], "sect": "Diurnal"}
    current = _seg("Mars", "Saturn", 20.0); current["from_lon"] = 22.0
    rows = engine["pn4_distribution_checklist"](root, rev, 125.0, current)
    assert [r["Question"][:3] for r in rows] == ["[1a", "[1b", "[2]", "[3]", "[4]", "[5]", "[5]"]
    assert rows[0]["Reads"].startswith("Mars's, 20") and "25" in rows[0]["Reads"]
    assert rows[2]["Reads"] == "house 1 / 9 / 10"                             # from Aries / Leo / Cancer
    assert "Aries: house of Mars, exaltation of Sun" in rows[3]["Reads"]
    assert rows[4]["Reads"].startswith("root: Saturn (infortune); revolution: Saturn (infortune), Moon (neither)")
    assert "Sun by square at 20" in rows[5]["Reads"] and "Saturn by body at 23" in rows[5]["Reads"]
    assert "Saturn by body at 24" in rows[6]["Reads"]
    assert engine["pn4_distribution_checklist"](root, rev, 125.0, None) == []


# --- II.13, 1; II.14, 1; II.22, 1-5: the luminary proxies (built 2026-09-10)

def test_pn4_sun_handover_is_applying_and_inside_his_sign(engine):
    """II.13, 1 [3] with fn 239: "the planet to which the Sun hands over the
    management (so long as it is in its sign)" -- the Sun's own
    connections before he leaves his sign, and "hands over" as the Sun
    applying. Every reported hand-over perfects before his exit, inside
    his starting sign, exact to a fresh ephemeris call, with the Sun the
    faster body at that moment; the Moon, always faster, is never one."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    natal_sun = chart["planetary_data"]["Sun"]["longitude"]
    swe = engine["swe"]
    for age in (30, 42):
        jd_sr = engine["pn4_solar_revolution_jd"](chart["julian_day"], natal_sun, age)
        sr = cast(engine["pn4_datetime_from_jd"](jd_sr), lat, lon)
        sun = engine["pn4_sun_handover"](sr["planetary_data"], jd_sr)
        assert sun["sign"] == engine["get_zodiac_sign"](sr["planetary_data"]["Sun"]["longitude"])
        assert 0.0 < sun["exit_day"] < 32.0
        for c in sun["connections"]:
            assert c["planet"] != "Moon"
            assert 0.0 < c["day"] < sun["exit_day"]
            assert engine["get_zodiac_sign"](c["moon_at"]) == sun["sign"]
            s = swe.calc_ut(jd_sr + c["day"], swe.SUN)[0]
            p = swe.calc_ut(jd_sr + c["day"], engine["PLANET_SWE_IDS"][c["planet"]])[0]
            target = {"body": 0.0, "sextile": 60.0, "square": 90.0, "trine": 120.0, "opposition": 180.0}[c["aspect"]]
            assert abs(abs(engine["_wrap180"](s[0] - p[0])) - target) < 0.05
            assert s[3] > p[3]


def test_pn4_proxies_only_for_a_luminary_year_and_admit_the_releaser(engine):
    """The luminary proxies exist when the Sun or the Moon is lord of the
    year (II.13, 1; II.22, 1) -- any other lord gets II.22, 23-25's one row
    -- and their first member needs the longevity
    releaser: that row says so. Leo's and Cancer's occupants are read
    from both charts; the Moon's rows carry the II.22 computation."""
    root, sr, _y = _two_charts(engine, natal=dict(Venus=140.0), rev=dict(Mars=100.0, Saturn=145.0))
    mars = engine["pn4_luminary_proxies"]("Mars", root, sr)          # II.22, 23-25 (PN4R-4i-5): one row for any other lord
    assert len(mars) == 1 and mars[0]["Source"] == "II.22, 23-25" and "Mars in Cancer, the house of Moon" in mars[0]["Reads"]
    moon = {"sign": "Libra", "moon_lon": 200.0, "exit_day": 1.5, "void": False, "house_lord": "Venus",
            "connections": [{"day": 0.4, "planet": "Jupiter", "aspect": "sextile", "moon_at": 205.0}]}
    sun = {"sign": "Cancer", "moon_lon": 100.0, "exit_day": 20.0, "void": True, "house_lord": "Moon", "connections": []}
    rows = engine["pn4_luminary_proxies"]("Sun", root, sr, moon, sun)
    assert [r["Proxy"][:4] for r in rows] == ["[II.", "[1] ", "[2] ", "[3] ", "[4] "]
    assert "releaser" in rows[0]["Reads"] and "IX.8, 123" in rows[1]["Reads"]
    assert rows[2]["Reads"] == "root: Venus; revolution: Saturn, Venus"             # 20 Leo natal; 25 and 10 Leo in the revolution
    assert rows[3]["Reads"].startswith("none: leaves Cancer on day 20.00 without a connection")
    assert rows[4]["Reads"].startswith("Cancer (10")
    rows = engine["pn4_luminary_proxies"]("Moon", root, sr, moon, None)
    assert [r["Proxy"][:3] for r in rows] == ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]
    assert rows[2]["Reads"] == "root: Sun, Mercury; revolution: Mars, Sun, Mercury"
    assert rows[3]["Reads"] == "Jupiter by sextile on day 0.40"
    assert rows[4]["Reads"] == "not empty in course"
    assert "in glow" in rows[5]["Reads"]


def test_pn4_bundle_shows_proxies_in_a_luminary_year_only(engine):
    """Through the bundle: a year whose lord is the Sun gets the Sun's
    hand-over computed and five rows; a Mars year gets none."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    lords = {age: engine["pn4_sign_of_the_year"](chart["ascendant"], age)["lord"] for age in range(12)}
    sun_age = next(a for a, l in lords.items() if l == "Sun")
    mars_age = next(a for a, l in lords.items() if l == "Mars")
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(1985 + sun_age, 6, 1).date(), rule)
    assert b["year"]["lord"] == "Sun" and b["sun_handover"] is not None and len(b["proxies"]) == 5
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(1985 + mars_age, 6, 1).date(), rule)
    # II.22, 23-25 (order PN4R-4i-5): a Mars year gets the one row for any lord -- the house he stands in
    assert b["sun_handover"] is None and len(b["proxies"]) == 1 and b["proxies"][0]["Source"] == "II.22, 23-25"
    assert "Mars in " in b["proxies"][0]["Reads"] and "the house of " in b["proxies"][0]["Reads"]


# --- II.3, 2-19: the sign of the terminal point and its lord (built 2026-09-10)

def _ii3_pair(engine, **kw):
    """A root and a revolution with twelve whole-sign cusps, for the
    accidental-dignity evaluator."""
    root, sr, year_lon = _two_charts(engine, **kw)
    for chart in (root, sr):
        base = (chart["ascendant"] // 30.0) * 30.0
        chart["houses"] = [(base + 30.0 * i) % 360.0 for i in range(12)]
        chart["julian_day"] = 2451545.0
    return root, sr, year_lon


def test_pn4_ii3_examines_the_sign_of_the_terminal_point_in_the_root(engine):
    """II.3, 2 as facts. Terminal sign Cancer under an Aries Ascendant:
    house 4, "a stake"; house of the Moon, exaltation of Jupiter,
    triplicity of Venus by day; the Sun and Mercury in it; the Moon at 20
    Libra squares it from 20 Libra with the ray at 20 Cancer, in
    Jupiter's bound (19-26) and the face of the Moon (20-30 Cancer)."""
    root, sr, _ = _ii3_pair(engine, year_lon=95.0)
    year = {"sign": "Cancer", "longitude": 95.0, "lord": "Moon"}
    out = engine["pn4_ii3_examination"](root, sr, year, 2451545.0)
    rows = out["root_rows"]
    assert rows[0]["Reads"] == "house 4 from the natal Ascendant, a stake"
    assert rows[1]["Reads"].startswith("house of Moon (neither); exaltation of Jupiter (fortune); triplicity of Venus (fortune) (day)")
    assert rows[2]["Reads"].startswith("planets: Sun (neither), Mercury (neither); Lots:")
    assert "twelfth-parts of: " in rows[2]["Reads"]                                   # computed since 2026-09-11 (PN4R-4l-7)
    assert "Moon (neither) by square from 20\u00b0 Lib 00', the ray at 20\u00b0 Can 00' (bound of Jupiter, face of Moon)" in rows[3]["Reads"]
    assert rows[4]["Reads"] == "no"


def test_pn4_ii3_examines_the_revolution_and_reads_conditions_as_labels(engine):
    """II.3, 3: the revolution's planets in the sign, who looks at it and
    from where, whether it is devoid, where those planets were and are,
    and their condition in each -- the engine's labels, not a verdict.
    A revolution with Saturn at 5 Cancer and nothing else configured to
    Cancer: Saturn in it; and a revolution where nothing touches the
    sign reads devoid."""
    root, sr, _ = _ii3_pair(engine, year_lon=95.0,
                            rev=dict(Sun=40.0, Moon=70.0, Mercury=75.0, Venus=160.0, Mars=220.0, Jupiter=280.0, Saturn=95.0))
    year = {"sign": "Cancer", "longitude": 95.0, "lord": "Moon"}
    out = engine["pn4_ii3_examination"](root, sr, year, 2451545.0)
    rows = out["revolution_rows"]
    assert rows[0]["Reads"].startswith("Saturn (infortune); twelfth-parts of: ")     # PN4R-4l-7
    assert "Mars (infortune) by trine from 10\u00b0 Sco 00'" in rows[1]["Reads"]           # 10 Scorpio trines Cancer
    assert "Jupiter (fortune) by opposition from 10\u00b0 Cap 00'" in rows[1]["Reads"]
    assert rows[2]["Reads"] == "no"
    assert "Saturn: house 1 -> 4 from the natal Ascendant" in rows[3]["Reads"]
    assert rows[4]["Reads"].startswith("Saturn: root ")
    quiet = _ii3_pair(engine, year_lon=95.0,
                      rev=dict(Sun=70.0, Moon=75.0, Mercury=80.0, Venus=130.0, Mars=250.0, Jupiter=300.0, Saturn=310.0))
    out = engine["pn4_ii3_examination"](quiet[0], quiet[1], year, 2451545.0)
    assert out["revolution_rows"][2]["Reads"] == "yes: devoid"


def test_pn4_ii3_lords_factors_per_chart_and_no_verdict(engine):
    """II.3, 5-6: the factors of a suitable and a contrary condition,
    shown for the root and the revolution. A retrograde lord under the
    rays in the revolution reads so; Figure 55's four sentences are
    quoted and no cell is chosen."""
    root, sr, _ = _ii3_pair(engine, year_lon=5.0, rev=dict(Mars=(102.0, -0.3), Sun=100.0))   # Mars retrograde, burned
    year = {"sign": "Aries", "longitude": 5.0, "lord": "Mars"}
    out = engine["pn4_ii3_examination"](root, sr, year, 2451545.0)
    row = lambda prefix: next(r for r in out["lord_rows"] if r["Factor"].startswith(prefix))
    assert row("Direct")["Root"] == "direct" and row("Direct")["Revolution"] == "retrograde"
    assert row("In its own glow")["Revolution"].startswith(("burned", "cazimi"))
    assert row("In a sign")["Root"] == "peregrine"                                # Mars at 0 Aquarius
    assert row("Its place")["Root"].startswith("house ")
    assert row("In its own domain")["Revolution"] in ("in its own domain (hayz)", "contrary to its domain", "neither in nor contrary to its domain")
    assert [r["Source"] for r in out["figure_55"]] == ["II.3, 5", "II.3, 6", "II.3, 7", "II.3, 8"]
    assert all(r["Indicates"].startswith('"') for r in out["figure_55"])
    assert not any("verdict" in k.lower() for k in out)


def test_pn4_ii3_refinements_reception_stake_and_aversion(engine):
    """II.3, 9-18 as facts: received or not; in a stake of the revolution's
    Ascendant with an infortune squaring or opposing; looking at the
    Ascendant or in 2, 6, 8, 12. Mars at 10 Capricorn under a Cancer
    revolution Ascendant is in house 7, a stake, opposed by Saturn at 20
    Cancer; from the natal Aries Ascendant it is in house 10 and looks at
    the Ascendant from a stake."""
    root, sr, _ = _ii3_pair(engine, year_lon=5.0, r_asc=95.0, rev=dict(Mars=280.0, Saturn=110.0))
    year = {"sign": "Aries", "longitude": 5.0, "lord": "Mars"}
    out = engine["pn4_ii3_examination"](root, sr, year, 2451545.0)
    ref = out["refinement_rows"]
    assert ref[0]["Reads"].startswith("root: ") and "revolution: " in ref[0]["Reads"]
    assert ref[1]["Reads"].startswith("house 7 from the revolution Ascendant (a stake); infortunes by square or opposition: Saturn by opposition")
    assert ref[2]["Reads"] == "house 10 from the natal Ascendant: looks at the Ascendant from a stake"
    hidden = _ii3_pair(engine, year_lon=5.0, r_asc=95.0, rev=dict(Mars=160.0))              # 10 Virgo: house 6 from Aries
    out = engine["pn4_ii3_examination"](hidden[0], hidden[1], year, 2451545.0)
    assert out["refinement_rows"][2]["Reads"].startswith("house 6 from the natal Ascendant: does NOT look at the Ascendant")


# --- III.2, 38, 43, 46-47, 54; III.8, 7: transits into the bound (built 2026-09-10)

def test_pn4_bound_transit_sentence_is_keyed_to_the_type(engine):
    """Each of the five sentences fits one type and one nature of
    entrant: 38 a fortune alone with an infortune entering; 54 both
    fortunes with an infortune entering; 46 both infortunes with a
    fortune's ray, 47 with an infortune's ray, and a body says the
    sentences speak of rays; 43 a fortune entering where a rooted infortune
    is in the bound -- 40's premise, which types 4, 5 and 6 have and types
    2 and 3 do not (order PN4R-4m-1) -- under 40-42's unjudged conditions;
    a fortune's BODY under type 6 takes 43 too; the neutrals, none."""
    key = engine["pn4_bound_transit_sentence"]
    assert key(1, "infortune", False) == (38, "")
    assert key(7, "infortune", True) == (54, "")
    assert key(6, "fortune", True) == (46, "")
    assert key(6, "infortune", True) == (47, "")
    assert key(6, "infortune", False)[0] is None and "speak of a ray" in key(6, "infortune", False)[1]
    assert key(6, "fortune", False)[0] == 43
    assert key(4, "fortune", True)[0] == 43 and key(5, "fortune", False)[0] == 43
    assert key(2, "fortune", True)[0] is None and key(3, "fortune", False)[0] is None and key(None, "fortune", True)[0] is None
    assert key(1, None, True)[0] is None and "Sun, the Moon or Mercury" in key(1, None, True)[1]
    assert key(1, "fortune", True)[0] is None
    gated = {k for k, (_c, _t, d) in engine["PN4_BOUND_TRANSIT_SENTENCES"].items() if d}
    assert gated == {43, 46, 47}


def test_pn4_bound_transits_quote_the_sentence_and_read_iii_8_7(engine):
    """Jupiter distributing alone at 22 Aries (Mars's bound, 20-25) with
    the revolution's Saturn at 23 Aries: III.2, 38 quoted; the
    revolution's Sun at 21 Aries: no sentence. III.8, 7: the lord of the
    year and the distributor both infortunes read as facts; a fortune
    lord of the year reads why the sentence does not apply."""
    root, sr, _ = _two_charts(engine, rev=dict(Saturn=23.0, Sun=21.0, Venus=130.0))
    current = _seg("Jupiter", None, 20.0); current["from_lon"] = 22.0
    rows = engine["pn4_bound_transits"](root, sr, current, "Venus")
    pick = lambda prefix: next(r for r in rows if r["In the bound, in the revolution"].startswith(prefix))
    assert pick("Sun by body at 21")["Sentence"].startswith("no sentence of III.2 speaks of the Sun")
    assert pick("Moon by opposition at 20")["Nature"] == "neither"                    # the revolution's Moon at 20 Libra
    saturn = pick("Saturn by body at 23")
    assert "incidental adversity and harm" in saturn["Sentence"] and "III.2, 38-39" in saturn["Sentence"]
    assert "110-111" not in saturn["Sentence"]
    assert rows[-1]["Source"] == "III.8, 7" and "needs the lord of the year and the distributor both infortunes" in rows[-1]["Sentence"]
    # both infortunes: the facts, then the sentence
    current = _seg("Mars", "Saturn", 20.0); current["from_lon"] = 22.0
    rows = engine["pn4_bound_transits"](root, sr, current, "Saturn")
    last = rows[-1]
    assert "a little good" in last["Sentence"] and "the facts:" in last["Sentence"]
    assert "Saturn in Aries: not in its own share" in last["Sentence"]
    # type 6 with a fortune's ray: 46, gated; with Venus's body: rays only
    root, sr, _ = _two_charts(engine, rev=dict(Venus=142.0, Saturn=340.0, Sun=190.0))   # Venus 22 Leo trines 22 Aries
    rows = engine["pn4_bound_transits"](root, sr, current, "Saturn")
    venus = next(r for r in rows if r["In the bound, in the revolution"].startswith("Venus by trine"))
    assert "revered in his illness" in venus["Sentence"] and "110-111" in venus["Sentence"]
    root, sr, _ = _two_charts(engine, rev=dict(Venus=22.5, Saturn=340.0, Sun=190.0))
    rows = engine["pn4_bound_transits"](root, sr, current, "Saturn")
    body = next(r for r in rows if r["In the bound, in the revolution"].startswith("Venus by body"))
    # a fortune's BODY under type 6 is 43 (40's premise holds; order PN4R-4m-1), still under 40-42's unjudged conditions
    assert "III.2, 43" in body["Sentence"] and "40-42" in body["Sentence"]
    assert engine["pn4_bound_transits"](root, sr, None, "Saturn") == []


# --- I.6, 3-8: the image of the revolution of the year (built 2026-09-10)

def test_pn4_twelfth_part_agrees_with_the_engines_construction(engine):
    """The twelfth-part as a degree: 2.5 degrees to a sign, beginning with
    the sign itself, the position inside the 2.5 spread over the sign's
    30. Its sign must be _twelfth_part_sign's (the engine's existing
    construction, supplied from convention and said so). 1 Aries is 12
    Aries; 5 Aries is 0 Gemini; 29 Pisces is 18 Aquarius."""
    tp = engine["pn4_twelfth_part"]
    assert tp(1.0) == pytest.approx(12.0)
    assert tp(5.0) == pytest.approx(60.0)
    assert tp(359.0) == pytest.approx(300.0 + 18.0)
    for lon in range(0, 360, 7):
        assert engine["get_zodiac_sign"](tp(lon + 0.3)) == engine["_twelfth_part_sign"](lon + 0.3)


def test_pn4_revolution_image_counts_as_i_6_8(engine):
    """I.6, 8 and Figure 52: 14 planets, 98 rays, the Head and Tail twice
    each, 24 twelfth-parts of houses and 14 of planets -- 154 -- with the
    Lots outside the count. On a real chart the inventory counts exactly
    that, carries I.6, 5's two points and I.6, 6's time lords, and is
    ordered by degree within each house."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule,
                                    {"Hour Lord": "Venus", "Approximate": False})
    rows, counts = b["image"]
    assert counts["planets"] == 14 and counts["rays"] == 98 and counts["nodes"] == 4
    assert counts["twelfth-parts of houses"] == 24 and counts["twelfth-parts of planets"] == 14
    assert counts["total of I.6, 8"] == 154 and counts["Lots"] > 0
    points = [r["Point"] for r in rows]
    assert "Ascendant of the root" in points and "Terminal point of the year" in points
    assert any(p.startswith("Endpoint of the distribution") for p in points)
    assert any(", the distributor" in p for p in points) and any(", lord of the orb" in p for p in points)
    assert any(", lord of the fardar" in p for p in points)
    assert all(r["Bound"] in engine["PN4_SEVEN"] for r in rows)
    by_house = {}
    for r in rows:
        by_house.setdefault(r["House"], []).append(r["Position"])
    assert sorted(by_house) == list(range(1, 13))
    # within a house the degree FROM THE HOUSE'S CUSP never decreases (I.6, 2:
    # the revolution's cusps; a quadrant house spans two signs and may straddle 0 Aries)
    lon_of = lambda s: engine["SIGN_ORDER"].index(next(z for z in engine["SIGN_ORDER"] if z.startswith(s.split(" ")[1]))) * 30 \
        + int(s.split("\u00b0")[0]) + int(s.split(" ")[-1].rstrip("'")) / 60.0
    for house, positions in by_house.items():
        vals = [round((lon_of(p) - b["sr"]["houses"][house - 1]) % 360.0, 6) for p in positions]
        assert vals == sorted(vals), house
    assert rows == b["image"][0]


# --- I.7, 1-26: the reading checklist (built 2026-09-10) -------------------

def test_pn4_i7_ascendant_rows_read_2_to_6(engine):
    """I.7, 2-6 for the revolution's Ascendant. Revolution Ascendant 5
    Cancer under a natal Aries Ascendant: house 4 from the root, a stake;
    who is in Cancer in each chart; who looks at it; the claimants and
    their shares; the Moon's one house, Cancer, which she is in."""
    root, sr, _ = _ii3_pair(engine, r_asc=95.0, rev=dict(Moon=100.0, Jupiter=250.0, Venus=130.0))
    rows = engine["pn4_i7_ascendant"](root, sr)
    assert [r["I.7"] for r in rows] == ["2", "3", "4", "5", "6"]
    assert rows[0]["Reads"].startswith("Cancer (05\u00b0 Can 00') is house 4 from the natal Ascendant, a stake")
    assert "root -- planets: Sun (neither), Mercury (neither)" in rows[1]["Reads"]
    assert "revolution -- planets: Sun (neither), Mercury (neither), Moon (neither)" in rows[1]["Reads"]
    assert "twelfth-parts of planets falling in it" in rows[1]["Reads"]
    assert "root: " in rows[2]["Reads"] and "revolution: " in rows[2]["Reads"]
    assert rows[3]["Reads"].startswith("Moon (house): house 1 from it, in Cancer, a share: house")
    assert "Jupiter (exaltation): house 6 from it, in Sagittarius, a share: house" in rows[3]["Reads"]
    assert rows[4]["Reads"].startswith("1 house: Cancer (house 1 from the Ascendant): Moon in it; Moon is house 1 from Cancer")
    # a lord with two houses: Mercury, for an Ascendant in Gemini
    root, sr, _ = _ii3_pair(engine, r_asc=65.0, rev=dict(Mercury=200.0))
    rows = engine["pn4_i7_ascendant"](root, sr)
    assert rows[4]["Reads"].startswith("2 houses: Gemini") and "Virgo" in rows[4]["Reads"]
    assert "Mercury looks at it by trine" in rows[4]["Reads"]                     # Libra trines Gemini
    assert "Virgo" in rows[4]["Reads"] and "does not look at it (aversion)" in rows[4]["Reads"]   # Libra is averse to Virgo


def test_pn4_share_or_exile(engine):
    """I.7, 5: "either in a position in which it has a share, or in the
    contrary of that (being in exile)". Mars at 10 Aries has a share (his
    house); Mars at 10 Libra is in exile; Mars at 5 Gemini has none;
    Venus at 10 Aquarius has the bound (Mercury-first Aquarius: Venus
    7-13)."""
    s = engine["_pn4_share_or_exile"]
    assert s("Mars", 10.0).startswith("a share: house")
    assert s("Mars", 190.0) == "exile (detriment)"
    assert s("Mars", 65.0) == "no share (peregrine)"
    assert s("Venus", 310.0).startswith("a share:") and "bound" in s("Venus", 310.0)


def test_pn4_i7_planet_rows_in_both_times(engine):
    """I.7, 7-24 per planet: fourteen rows, seven a chart, with motion,
    whole-sign configurations, degree connections, reception, domain,
    twelfth-part, return, stakes and the Sun. The revolution's Saturn on
    its natal degree reads a return by degree; the revolution's Mars on
    the natal Sun's bound reads it too."""
    root, sr, _ = _ii3_pair(engine, rev=dict(Saturn=(20.3, -0.05), Mars=(102.0, 0.6)))
    rows = engine["pn4_i7_planets"](root, sr)
    assert len(rows) == 14 and [r["Chart"] for r in rows] == ["root"] * 7 + ["revolution"] * 7
    by = {(r["Planet"], r["Chart"]): r for r in rows}
    assert by[("Saturn", "revolution")]["Motion (7)"] == "retrograde"
    assert by[("Saturn", "revolution")]["Return (19)"].startswith("on its own rooted place by degree")
    assert "on the rooted place of Sun" in by[("Mars", "revolution")]["Return (19)"]
    assert by[("Saturn", "root")]["Return (19)"] == "-"
    assert by[("Sun", "root")]["Whole sign (10-11)"].startswith("assembled with Mercury")
    assert "Moon (square)" in by[("Sun", "root")]["Whole sign (10-11)"]
    assert by[("Sun", "root")]["Stakes (23)"] == "house 4, a stake"
    assert by[("Sun", "root")]["Sun (24)"] == "-, in its own glow"
    assert by[("Mercury", "root")]["Sun (24)"].split(",")[0] in ("eastern", "western")
    assert by[("Moon", "root")]["Twelfth-part (18)"] == "00\u00b0 Gem 00'"           # 20 Libra: the ninth twelfth-part, Gemini
    for r in rows:
        assert r["Domain (17)"] in ("in its own domain", "contrary to its domain", "neither")
        assert r["Received by (14)"] != ""


# --- IX.7, 1-72: the nine methods for the days and hours (built 2026-09-10)

def test_pn4_ix7_ninth_parts_against_the_worked_example(engine):
    """IX.7, 57-69, "a year terminated at 20 Taurus": Saturn, lord of
    Capricorn and of the first ninth-part, "manages 3 days, 9 hours, and
    1/6 of an hour"; the thirds of 1 06' 40" go to Saturn, Venus (lord of
    Taurus) and Mercury (lord of Virgo) "for 27 hours, and one-half of a
    ninth of an hour"; the ninths of the first third to Saturn
    (Capricorn), Saturn (Aquarius) and Jupiter (Pisces) for "three hours
    and one-third of a sixth of a ninth of an hour"; the thirds of the
    first ninth to Saturn, Venus, Mercury for "1 hour and one-third of
    one-ninth of one-third of one-sixth of an hour"."""
    np = engine["pn4_ix7_ninth_parts"]
    r = np(0.0, "Taurus")
    assert (r["month_sign"], r["ninth_part_sign"], r["ninth_part_lord"]) == ("Taurus", "Capricorn", "Saturn")
    d = r["durations_hours"]
    assert d["ninth-part"] == pytest.approx(3 * 24 + 9 + 1 / 6, abs=1e-6)                  # 3 d 9 h 10 m
    assert d["third"] == pytest.approx(27 + 1 / 18, abs=1e-6)                             # 27 h and half a ninth
    assert d["ninth of the third"] == pytest.approx(3 + 1 / 162, abs=1e-6)                 # fn 196
    assert d["third of the ninth"] == pytest.approx(1 + 1 / 486, abs=1e-6)                 # fn 198
    assert (r["third_lord"], r["ninth_lord"], r["third_of_ninth_lord"]) == ("Saturn", "Saturn", "Saturn")
    hours = lambda h: h / 24.0
    assert np(hours(27.5), "Taurus")["third_lord"] == "Venus"                              # 60: the second third
    assert np(hours(55.0), "Taurus")["third_lord"] == "Mercury"                            # 61
    assert np(hours(3.5), "Taurus")["ninth_lord"] == "Saturn" and np(hours(3.5), "Taurus")["ninth_sign"] == "Aquarius"   # 64
    assert np(hours(6.5), "Taurus")["ninth_lord"] == "Jupiter"                             # 65: Pisces
    assert np(hours(1.5), "Taurus")["third_of_ninth_lord"] == "Venus"                      # 68
    assert np(hours(2.5), "Taurus")["third_of_ninth_lord"] == "Mercury"                    # 69
    second = np(3.4, "Taurus")
    assert (second["ninth_part"], second["ninth_part_sign"], second["ninth_part_lord"]) == (2, "Aquarius", "Saturn")
    month2 = np(engine["PN4_IX7_MONTH_DAYS"] + 0.1, "Taurus")
    assert (month2["month"], month2["month_sign"]) == (2, "Gemini")                        # 46: the next sign
    assert engine["PN4_IX7_MONTH_DAYS"] * 12 == pytest.approx(365.25)                       # 55
    # the two printed errata, shown as printed beside the exact (fn 195, 197)
    errata = engine["PN4_IX7_EXAMPLE_ERRATA"]
    assert [e[0] for e in errata] == ["IX.7, 62", "IX.7, 66"]
    third_arc = (30.0 / 9.0) / 3.0                                                        # 1 06' 40"
    ninth_arc = third_arc / 9.0 * 3600.0                                                   # in arcseconds
    assert int(ninth_arc // 60) == 7 and int(ninth_arc % 60) == 24                         # 7' 24" ..., not 7' 25" 33""


def test_pn4_ix7_moon_starts_from_her_own_ninth_part_and_degree(engine):
    """IX.7, 71: "one sees at the revolution of the year which ninth-part
    she is in, of the sign she is in, so that the beginning of the
    management of the days will be from that ninth-part and from that
    degree". The Moon at 5 Taurus is in Taurus's second ninth-part (3 20'
    to 6 40'), half-way through it."""
    sign, offset = engine["pn4_ix7_moon_start"](35.0)
    assert sign == "Taurus"
    N = engine["PN4_IX7_NINTH_PART_DAYS"]
    assert offset == pytest.approx(1.5 * N)
    r = engine["pn4_ix7_ninth_parts"](0.0, sign, offset)
    assert r["ninth_part"] == 2 and r["ninth_part_sign"] == "Aquarius"
    assert r["third"] == 2                                                                  # half-way: the second third


def test_pn4_ix7_weeks_and_sevenths(engine):
    """Methods 1-5. Fn 163: "let a native be born with Scorpio rising:
    Mars rules the first week (and the first day of it), and after seven
    weeks of the seven planets (or 49 days)" Mars again. Method 3: the
    greater seventh is 52 d 4 h 16 m (fn 168), the lesser about 7 d 10 h
    52 m; the lord of the revolution's Ascendant takes the first of each.
    Method 5: the days by twelves; two hours a sign."""
    w = engine["pn4_ix7_weeks_from_birth"]
    assert w(0.0, "Mars") == {"weeks": 0, "remainder": 0, "left_of_week": 7, "week": "Mars", "day": "Mars", "hour": "Mars"}
    assert w(49.0, "Mars")["week"] == "Mars" and w(48.0, "Mars")["week"] == "Jupiter"       # the seventh planet from Mars
    assert w(1.0, "Mars")["day"] == "Sun" and w(1.5, "Mars")["hour"] == "Moon"              # 12 h = the fourth 3 3/7 from the Sun
    assert w(3.9999, "Mars")["day"] == "Mercury"                                            # whole days from the birth moment
    o = engine["pn4_ix7_weeks_from_orb"]
    assert o(7.0, "Venus")["week"] == "Mercury" and o(8.0, "Venus")["day"] == "Moon"
    assert o(0.0, None) is None
    G = engine["PN4_IX7_GREATER_SEVENTH"]
    assert G == pytest.approx(52 + 4 / 24 + 16 / 1440, abs=0.001)
    s = engine["pn4_ix7_sevenths"]
    assert s(0.0, "Venus")["greater_seventh"] == "Venus" and s(0.0, "Venus")["lesser_seventh"] == "Venus"
    assert s(G + 0.5, "Venus")["greater_seventh"] == "Mercury"
    assert s(engine["PN4_IX7_LESSER_SEVENTH"] + 0.5, "Venus")["lesser_seventh"] == "Mercury"
    ws = engine["pn4_ix7_weeks_to_signs"]
    assert ws(0.0, "Scorpio")["week"] == "Scorpio" and ws(7.0, "Scorpio")["week"] == "Sagittarius"
    assert ws(14.5 / 24.0, "Scorpio")["now"] == "Sagittarius"                               # 14 hours a sign
    ds = engine["pn4_ix7_days_to_signs"]
    assert ds(0.0, "Scorpio") == {"day": "Scorpio", "hour": "Scorpio"}
    assert ds(13.0, "Scorpio")["day"] == "Sagittarius"
    assert ds(2.5 / 24.0, "Scorpio")["hour"] == "Sagittarius"


def test_pn4_ix7_month_days_two_ways(engine):
    """Method 8, IX.7, 35-38: from a start at 10 Aries, day 4 of the month
    reaches 14 Aries by way [1]; by way [2] the day belongs to the second
    sign, Taurus (2 1/2 days a sign), and 36 hours into that slot the
    hours have moved seven signs on, to Sagittarius (five hours a sign)."""
    rows = engine["pn4_ix7_month_days"](4.0, [("x", 10.0)])
    assert rows[0]["Way 1: a day per degree, now at"].startswith("14\u00b0 Ari 00'")
    assert rows[0]["Way 2: the day's sign"] == "Taurus"                                     # 4 // 2.5 = 1
    assert rows[0]["Way 2: this hour's sign"] == "Sagittarius"                              # 36 h into the slot: the eighth five-hour portion
    # IX.7, 39: "it will return to the position which it began from" -- day
    # 30.3 is 0.3 into the next month, 10 Ari 18' by way [1], Aries by way [2].
    late = engine["pn4_ix7_month_days"](30.3, [("x", 10.0)])
    assert late[0]["Way 1: a day per degree, now at"].startswith("10\u00b0 Ari 18'")
    assert late[0]["Way 2: the day's sign"] == "Aries"
    assert late[0]["Source"] == "IX.7, 35-39"


def test_pn4_bundle_carries_the_day_methods(engine):
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule,
                                    {"Hour Lord": "Venus", "Approximate": False})
    rows, month_rows, ninth_rows = b["day_methods"]
    assert [r["Method"][:2] for r in rows] == ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."]
    assert rows[1]["This week"] in engine["PN4_SEVEN"] and rows[0]["This hour"] in engine["PN4_SEVEN"]
    assert len(month_rows) == 7 and len(ninth_rows) == 3
    assert ninth_rows[0]["Start"] == "the sign of the terminal point"


def test_pn4_indicator_two_against_abu_mashars_worked_months(engine):
    """IX.1, 15-16 works indicator #2 out month by month for a year that
    terminates at Cancer: "the lord of its first ninth-part is the Moon,
    and she is the lord of the year, as well as the lord of the first
    month"; then "the lord of the first ninth-part of Leo is Mars ... of
    Virgo is Saturn ... of Libra is Venus".

    The thing this pins is the SHAPE of the indicator. What turns is the
    sign of the terminal point; the lord is read off the first ninth-part
    of whatever sign the turning reaches. Turning the year's ninth-part
    SIGN instead would give the Sun for month 2, not Mars."""
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    cancer = 3 * 30.0
    for month, lord in ((1, "Moon"), (2, "Mars"), (3, "Saturn"), (4, "Venus")):
        rows = engine["pn4_monthly_indicators"](
            month, 0, cancer, 0.0, 0.0, 0.0, 0.0, 0.0, rule)
        got = next(r for r in rows if r["number"] == 2)
        assert got["lord"] == lord, f"month {month}: got {got['lord']}, want {lord}"


def test_pn4_indicator_three_is_profected_a_sign_a_year_first(engine):
    """IX.1, 17-18: "you see where the Lot of Fortune is in the root of the
    nativity, and TURN FROM IT A SIGN FOR EVERY YEAR, up to the year which
    you want" -- and only then a sign a month (19). Indicator #3 is the
    PROFECTED natal Lot, not the natal Lot itself."""
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    fortune = 5.0                                   # 5 Aries
    rows = engine["pn4_monthly_indicators"](1, 4, 0.0, fortune, 0.0, 0.0, 0.0, 0.0, rule)
    assert next(r for r in rows if r["number"] == 3)["sign"] == "Leo"      # 4 years on
    rows = engine["pn4_monthly_indicators"](3, 4, 0.0, fortune, 0.0, 0.0, 0.0, 0.0, rule)
    assert next(r for r in rows if r["number"] == 3)["sign"] == "Libra"    # +2 months


def test_pn4_indicators_four_and_five_are_NOT_annually_profected(engine):
    """The negative control for the pair above. IX.1, 20-21 assigns the
    revolution's Ascendant and its Lot of Fortune to the first month AS
    THEY STAND -- they must not be profected by the age the way #1 and #3
    are, or a native's age would move the revolution's own Ascendant."""
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    sr_asc, sr_fortune = 5.0, 35.0                  # 5 Aries, 5 Taurus
    for age in (0, 4, 40):
        rows = engine["pn4_monthly_indicators"](1, age, 0.0, 0.0, sr_asc, sr_fortune, 0.0, 0.0, rule)
        by = {r["number"]: r["sign"] for r in rows}
        assert by[4] == "Aries" and by[5] == "Taurus"


def test_pn4_printed_reference_tables_derive_from_the_rules(engine):
    """The Timing page's three reference tables are built from the same
    functions the engine applies, not restated beside them. Each ladder row
    is emitted only if pn4_arc_to_time agrees with it, so a rung that
    stopped agreeing would vanish -- this makes that loud instead."""
    assert len(engine["PN4_LADDER_ROWS"]) == 5, engine["PN4_LADDER_ROWS"]
    assert engine["PN4_LADDER_ROWS"][-1] == {"Arc": "25‴", "Is": "1 hour"}
    assert [r["A degree is"] for r in engine["PN4_UNIT_ROWS"]] == [
        "years", "months and days", "days and hours"]
    state = {r["Point directed"]: r["In this engine"] for r in engine["PN4_ASCENSION_ROWS"]}
    # III.1, 12's three cases do not stand alike and the table must not say
    # they do: two are built (since 2026-09-10), each for the DEGREE of its
    # point and not for the planets in it; the third has no stated method
    # at all. A row may claim "applied" only for what the engine directs,
    # so directing a planet on an angle, or building the third case, means
    # changing these strings too.
    applied = {k: v for k, v in state.items() if v.startswith("applied")}
    assert sorted(applied) == ["Ascendant, and things in it", "Midheaven, or the fourth"]
    # since 2026-09-11 (GAP-37 / PN4R-4b-4) the planets in those divisions are directed as their degrees are
    assert applied["Ascendant, and things in it"] == "applied to the degree of the Ascendant and to the planets in it (the first division, carried over)"
    assert applied["Midheaven, or the fourth"] == "applied to the degrees of the Midheaven and the fourth and to the planets in them (the tenth and fourth divisions, carried over)"
    assert state["Anything else"] == "method not stated in PN IV"


# --- III.7, 32-42: when a natal indication comes out ----------------------

@pytest.mark.parametrize("lon, sign, kind, cite", [
    (40.0, "Taurus", "fixed", "III.7, 35"),           # "in [only] a single time"
    (5.0, "Aries", "convertible", "III.7, 39"),       # "in [only] one of the times"
    (70.0, "Gemini", "double-bodied", "III.7, 38"),   # "on an occasional basis"
])
def test_pn4_manifestation_frequency_by_quadruplicity(engine, lon, sign, kind, cite):
    """III.7, 35, 38 and 39 key how often a natal indication comes out to
    the quadruplicity of the sign the planet holds in the ROOT."""
    rows = engine["pn4_activation_ages"](pdata(Saturn=lon), 23.44, 43.78)
    row = next(r for r in rows if r["Planet"] == "Saturn")
    assert (row["Natal sign"], row["Quadruplicity"]) == (sign, kind)
    assert cite in row["Manifests"]


def test_pn4_sign_ascensions_close_to_the_circle(engine):
    """III.7, 34's "ascensions of its sign": the arc of the equator that
    rises with it. The twelve must sum to 360 at any latitude in domain,
    which is the check that catches a sign measured the wrong way round."""
    for lat in (0.0, 43.78, 51.5):
        total = sum(engine["pn4_sign_ascensions"](s, 23.44, lat) for s in engine["SIGN_ORDER"])
        assert total == pytest.approx(360.0, abs=1e-9)


def test_pn4_sign_ascensions_are_latitude_dependent(engine):
    """A long-ascension sign in the north rises with more than 30 degrees
    of equator and its opposite with fewer; at the equator every sign is
    the same pair. A latitude-independent answer would mean the birth
    latitude was dropped -- III.7, 34 reads it from the birth place, as
    III.1, 12 does."""
    at = engine["pn4_sign_ascensions"]
    # At the equator every sign rises with its right-ascension span, and a
    # sign and its opposite rise alike: Taurus and Scorpio both 29.91.
    assert at("Taurus", 23.44, 0.0) == pytest.approx(29.908, abs=0.01)
    assert at("Scorpio", 23.44, 0.0) == pytest.approx(at("Taurus", 23.44, 0.0), abs=1e-9)
    # In the north that symmetry breaks: Taurus is a sign of short
    # ascension and Scorpio, its opposite, of long, and the pair still
    # closes to twice 30.
    assert at("Taurus", 23.44, 51.5) < 20.0
    assert at("Scorpio", 23.44, 51.5) > 40.0
    # A sign and its opposite sum to the SAME value at every latitude --
    # twice that sign's equatorial span, not 60 -- because the two
    # ascensional differences are equal and opposite and cancel. This is
    # the check that would catch a dropped or mis-signed AD, which is the
    # way an ascension goes wrong without looking wrong.
    for sign in engine["SIGN_ORDER"][:6]:
        opposite = engine["SIGN_ORDER"][engine["SIGN_ORDER"].index(sign) - 6]
        equatorial = at(sign, 23.44, 0.0) + at(opposite, 23.44, 0.0)
        for lat in (23.0, 43.78, 51.5, -35.0):
            assert at(sign, 23.44, lat) + at(opposite, 23.44, lat) == pytest.approx(
                equatorial, abs=1e-9), f"{sign}/{opposite} at {lat}"


def test_pn4_activation_ages_refuse_above_the_polar_circle(engine):
    """D-23's domain again: above it a sign may never rise, so it has no
    ascensional time."""
    assert engine["pn4_sign_ascensions"]("Taurus", 23.44, 78.0) is None
    row = engine["pn4_activation_ages"](pdata(Mars=40.0), 23.44, 78.0)[0]
    assert row["Ascensions of the sign"] == "-"


def test_pn4_activation_ages_choose_none_of_the_three_grades(engine):
    """The negative control that admitted this evaluator past the D-3
    guard. III.7, 35 picks among the greater, middle and lesser years "in
    accordance with what its position in the rotation of the circle
    indicated in the root" -- and PN IV never states that rule. It is
    corpus disagreement #2, which PN IV does not adjudicate (IX.8, 123).

    So all three must be present and none marked as the answer: no
    "grants", no "selected", no single Years column."""
    row = engine["pn4_activation_ages"](pdata(Mercury=40.0), 23.44, 43.78)[0]
    assert row["Lesser"] == "20" and row["Middle"] == "48" and row["Greater"] == "76"
    joined = " ".join(str(v).lower() for v in row.values())
    for verdict in ("grants", "granted", "selected", "chosen", "house-master"):
        assert verdict not in joined, f"{verdict!r} appears: a grade was chosen"


def test_pn4_activation_ages_do_NOT_carry_valens_sum_or_thirds(engine):
    """The other negative control, and the reason this is narrower than
    the answer document's summary. Dykes' fn 191 introduces the SUM of the
    ascensions and the years, and 1/3, 1/2 and 2/3 of it, with the words
    "IF WE FOLLOW VALENS". No sentence of III.7 contains them; III.7, 42
    names only the ascensions, "the amount of one of its own years", and
    an unquantified "rest of the times which one employs as models".

    For Mercury in Taurus -- Figure 75's own configuration -- the Valens
    construction would put candidates near 13.4, 20.1 and 26.8. None may
    appear."""
    row = engine["pn4_activation_ages"](pdata(Mercury=40.0), 23.44, 45.0)[0]
    ascensions, lesser = float(row["Ascensions of the sign"]), 20.0
    total = ascensions + lesser
    printed = " ".join(str(v) for v in row.values())
    for absent in (total, total / 3, total / 2, 2 * total / 3):
        assert f"{absent:.2f}" not in printed, f"{absent:.2f} is Valens's, not Abu Ma'shar's"


def test_pn4_activation_confirmation_needs_the_planet_to_be_a_time_lord(engine):
    """III.7, 42 is Abu Ma'shar's own contribution: the effect is "strong,
    evident, notable" when such an age falls where that same planet is the
    distributor or the manager. Without a distribution to check against,
    nothing may be confirmed -- the column must not assert on its own."""
    unchecked = engine["pn4_activation_ages"](pdata(Mercury=40.0), 23.44, 43.78, None)[0]
    assert unchecked["Confirmed by the distribution"] == "none"

    points = pdata(Mercury=40.0, Saturn=200.0)
    segments = engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78)
    rows = engine["pn4_activation_ages"](points, 23.44, 43.78, segments)
    for row in rows:
        for claim in row["Confirmed by the distribution"].split(";"):
            if "as " not in claim:
                continue
            age = float(claim.split("(")[1].split(",")[0])
            segment = engine["pn4_distribution_at_age"](segments, age)
            assert row["Planet"] in (segment["distributor"], segment["partner"])


def test_pn4_ascensions_against_abu_mashars_own_worked_conversion(engine):
    """III.1, 26 (p. 291) converts a zodiacal arc into ascensions and then
    into time, and prints every step, so the engine can be checked against
    the author's own arithmetic rather than against an editor's note.

        Ascendant Taurus 2 54' (III.1, 19), the Lot of courage 4 20'
        later; "in the ascensions of the clime of Babylon (the fourth)
        that is 3 02', so Venus distributes alone for 3 years, 12 days."

    The chart's latitude is given as 36 deg (III.1, 19). With PTOLEMY'S
    obliquity, 23;51 = 23.85 -- the value Abu Ma'shar's own tables use,
    not the modern one -- the engine returns 3 02' to within half an
    arcminute. The modern 23.44 gives 3 04', which is the size of error to
    expect from using the wrong obliquity and is worth seeing here.

    Then the rate ladder closes the circle: 3 deg is 3 years and 2' is
    12 days at 6 days to the minute (III.1, 13), which is exactly the
    period printed.

    A NOTE ON USING THIS EXAMPLE AT ALL. Dykes judges the III.1 worked
    example "corrupted and ought to be ignored" (Intro Sect. 7, pp. 73-75)
    and 04_timing_answers_2026-09-10.md repeats "do not use it as a test
    fixture". That verdict is about its DOCTRINE -- the chart data in 19
    and 22 are mutually inconsistent, and it accumulates Lots as though
    each became a releaser when met, against III.1, 47. This test takes no
    doctrine from it. It takes one self-contained arithmetic step, whose
    inputs are all printed in the same sentence and whose output is
    checkable three ways, and uses it to pin the ascension code. Nothing
    here depends on the example being a sound piece of astrology."""
    oa = engine["_oblique_ascension"]
    ascendant = 30 + 2 + 54 / 60           # Taurus 2 54'
    lot = ascendant + 4 + 20 / 60          # 4 20' later, by degrees of equality
    printed = 3 + 2 / 60                   # "that is 3 02'"

    ptolemy = (oa(lot, 23.85, 36.0) - oa(ascendant, 23.85, 36.0)) % 360.0
    assert ptolemy == pytest.approx(printed, abs=0.5 / 60)

    modern = (oa(lot, 23.44, 36.0) - oa(ascendant, 23.44, 36.0)) % 360.0
    assert modern == pytest.approx(printed, abs=2.5 / 60)
    assert abs(modern - printed) > abs(ptolemy - printed)

    # "so Venus distributes alone for 3 years, 12 days"
    period = engine["pn4_arc_to_time"](printed)
    assert (period["years"], period["months"], period["days"]) == (3, 0, 12)


# --- III.1: the jar bakhtar against the editor's worked figure (added 2026-09-10)

FIG22_ROWS = [
    # (arc d, m, s), distributor, partner, aspect -- PN IV Figure 22 (p. 63),
    # a Janus run on the chart of Apr 27 2019, 5:13:00 AM CDT, Minneapolis
    # 93w15'49" 44n58'48". Janus leaves the partner at birth blank; III.1,
    # 23-25 gives the body or ray behind the Ascendant in its sign, Venus.
    ((0, 0, 0), "Venus", "Venus", "body"),
    ((1, 10, 54), "Mercury", "Venus", "body"),
    ((1, 19, 57), "Mercury", "Moon", "sextile"),
    ((2, 19, 36), "Mercury", "Mercury", "body"),
    ((4, 18, 54), "Mercury", "Mars", "sextile"),
    ((5, 28, 58), "Mars", "Mars", "sextile"),
    ((5, 45, 50), "Mars", "Saturn", "square"),
    ((7, 38, 54), "Mars", "Jupiter", "trine"),
]


def test_pn4_distribution_reproduces_figure_22(engine):
    """PN IV Figure 22 is the one printed distribution with arcs to the
    second: eight segments over the first 7.6 years. The engine's
    oblique-ascension direction of the Ascendant (III.1, 12-13) must land
    every bound and every partner where the figure does, within two
    seconds of arc -- the figure's own rounding."""
    lat, lon = 44 + 58 / 60 + 48 / 3600, -(93 + 15 / 60 + 49 / 3600)
    chart = engine["calculate_traditional_chart"](datetime(2019, 4, 27, 10, 13, 0), lat, lon)
    assert engine["get_degree_string"](chart["ascendant"]) == "09° Ari 45'"
    segs = engine["pn4_distribution_from_ascendant"](chart["planetary_data"], chart["ascendant"],
                                                     chart["obliquity"], lat)
    assert len(segs) >= len(FIG22_ROWS)
    for seg, ((d, m, s), distributor, partner, aspect) in zip(segs, FIG22_ROWS):
        expected = d + m / 60.0 + s / 3600.0
        assert seg["from"] == pytest.approx(expected, abs=2.0 / 3600.0), (seg, (d, m, s))
        assert seg["distributor"] == distributor
        assert seg["partner"] == partner and seg["partner_aspect"] == aspect


# --- SAHL: the releaser (On Nativities 1.15-1.16, 1.20) and the house-master
# directed (1.23, 2) -- built 2026-09-10 on the owner's decision. Cusps are
# the whole-sign starts, so the quadrant place with the carry-over is the
# sign count unless a planet sits within five degrees of a stake's cusp.

def _sahl_chart(asc, **planets):
    base = (asc // 30.0) * 30.0
    cusps = [(base + 30.0 * i) % 360.0 for i in range(12)]
    seven = dict(Sun=100.0, Moon=200.0, Mercury=110.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=20.0)
    seven.update(planets)
    return pdata(**seven), cusps


def _releaser(engine, asc, sect, lot=15.0, meeting=15.0, fullness=15.0, **planets):
    data, cusps = _sahl_chart(asc, **planets)
    return engine["sahl_releaser"](data, asc, cusps, sect, lot, meeting, fullness)


def test_sahl_releaser_the_sun_in_leo_is_both_releaser_and_house_master(engine):
    """1.16, 1: "if the Sun was in Aries or Leo ... the Sun in these two
    signs becomes both the releaser and the house-master". Scorpio rising,
    the Sun at 15 Leo in the tenth (one of 1.15, 6's five places)."""
    r = _releaser(engine, 215.0, "Diurnal", Sun=135.0)
    assert r["releaser"] == "the Sun" and r["house_master"] == "Sun"
    assert r["chosen"]["both_at_once"] and "1.16" in r["verdict"]
    assert r["candidates"][0]["Verdict"].startswith("THE RELEASER")


def test_sahl_releaser_falls_to_the_meeting_and_two_shares_beat_one(engine):
    """1.15, 7-8: the Sun in the twelfth "will not be the releaser ... look
    at the meeting"; 1.20, 3: "the one having two shares is stronger than
    the lord of only a single one". Scorpio rising, the Sun at 10 Libra
    (twelfth, falling), the meeting at 5 Leo in the tenth: its house and
    triplicity lord is the Sun, looking by sextile from Libra -- two
    shares; its face lord Saturn looks by opposition from Aquarius -- one;
    its bound lord Jupiter is in aversion from Capricorn."""
    r = _releaser(engine, 215.0, "Diurnal", Sun=190.0, meeting=125.0, Saturn=320.0, Jupiter=280.0)
    assert r["releaser"] == "the meeting (the last New Moon)"
    assert r["house_master"] == "Sun"
    assert [row["Planet"] for row in r["ranking"]] == ["Sun", "Saturn"]
    assert r["ranking"][0]["Shares"] == "house, triplicity"
    assert r["candidates"][0]["Verdict"].startswith("falling: house 12")


def test_sahl_releaser_falls_to_the_ascendant_and_the_bound_lord_with_it_wins(engine):
    """1.15, 9 and 15-16: both falling, the Ascendant, "being looked at by
    the fortunes, and the lord of the Ascendant in its own house ... in
    good places"; 1.20, 4: the releaser "in the bound of a planet, and that
    planet was in the Ascendant with the releaser, it is stronger than the
    others". 5 Scorpio rising, Mars at 10 Scorpio (own house, bound lord
    of 5 Scorpio, in the Ascendant), Venus trine from Pisces, Jupiter
    opposing from Taurus; Sun and meeting both falling."""
    r = _releaser(engine, 215.0, "Diurnal", Sun=190.0, meeting=20.0, Mars=220.0, Venus=345.0, Jupiter=50.0)
    assert r["releaser"] == "the Ascendant" and r["house_master"] == "Mars"
    assert "1.20, 4" in r["ranking"][0]["Rank"]
    # the same chart with Mars at 25 Gemini, out of every share of his: no foundation (1.15, 16)
    none = _releaser(engine, 215.0, "Diurnal", Sun=190.0, meeting=20.0, Mars=85.0, Venus=345.0, Jupiter=50.0)
    assert none["releaser"] is None and none["house_master"] is None
    assert "does not have a foundation" in none["verdict"]
    assert engine["sahl_releaser_distribution"](_sahl_chart(215.0)[0], None, 23.44, 40.0) is None


def test_sahl_releaser_by_night_ranks_bound_above_house_and_shares_above_rank(engine):
    """1.15, 11: the Moon "in a stake or what follows a stake, with the
    lord of the bound, house, exaltation, triplicity, or image looking at
    her, then the Moon is the releaser". Cancer rising, the Moon at 10
    Libra in the fourth: Saturn holds exaltation and face (two shares),
    Venus the house (one), Mercury the bound and the night triplicity
    (two). With Mercury in aversion Saturn wins by shares over Venus;
    with Mercury looking, Mercury and Saturn tie on shares and the bound
    decides (1.20, 2)."""
    r = _releaser(engine, 95.0, "Nocturnal", Moon=190.0, Mercury=230.0, Venus=3.0, Saturn=75.0)
    assert r["releaser"] == "the Moon" and r["house_master"] == "Saturn"
    assert r["ranking"][0]["Shares"] == "exaltation, face" and r["ranking"][1]["Planet"] == "Venus"
    r2 = _releaser(engine, 95.0, "Nocturnal", Moon=190.0, Mercury=75.0, Venus=3.0, Saturn=75.0)
    assert r2["house_master"] == "Mercury" and r2["ranking"][0]["Shares"] == "bound, triplicity"
    assert r2["ranking"][1]["Planet"] == "Saturn"


def test_sahl_releaser_by_night_falls_to_the_fullness_then_the_lot(engine):
    """1.15, 12 and 14: "if the Moon was falling ... turn to the fullness
    ... Now if the fullness was also falling ... then the Lot of Fortune
    is the releaser". Cancer rising, the Moon at 10 Gemini (twelfth); the
    fullness at 10 Capricorn (seventh), its bound lord Jupiter trine from
    Taurus outranking its house lord Saturn square from Aries; then the
    fullness moved to 15 Sagittarius (sixth) and the Lot at 10 Scorpio
    (fifth): its bound lord Venus looks by trine from Pisces, one share,
    but Mars, its house lord and (by night) its triplicity lord, looks by
    square from Aquarius with two -- and two shares beat the bound
    (1.20, 3)."""
    r = _releaser(engine, 95.0, "Nocturnal", Moon=70.0, fullness=280.0, Jupiter=40.0)
    assert r["releaser"] == "the fullness (the last Full Moon)" and r["house_master"] == "Jupiter"
    assert [row["Planet"] for row in r["ranking"]] == ["Jupiter", "Saturn"]
    r2 = _releaser(engine, 95.0, "Nocturnal", Moon=70.0, fullness=255.0, lot=220.0, Venus=345.0, Jupiter=40.0)
    assert r2["releaser"] == "the Lot of Fortune" and r2["house_master"] == "Mars"
    assert r2["ranking"][0]["Shares"] == "house, triplicity" and r2["ranking"][1]["Planet"] == "Venus"
    assert r2["candidates"][1]["Verdict"].startswith("falling: house 6")


def test_sahl_house_master_direction_at_the_equator_is_right_ascension(engine):
    """1.23, 2: "direct it to the conjunction of the infortunes and the
    degree of burning, and its opposition and its square, a year for every
    degree of ascensions". At the equator the ascensions are right
    ascensions: a house-master at 0 Aries reaches Saturn's body at 0 Cancer
    and Mars's square at 0 Cancer in 90 years, the Sun's degree at 15
    Aries in atan(cos e tan 15) = 13.8 years; Mars's body at 0 Libra (180)
    and Saturn's opposition (270) lie past the table."""
    import math
    data = pdata(Venus=0.0, Saturn=90.0, Mars=180.0, Sun=15.0, Moon=200.0, Mercury=20.0, Jupiter=250.0)
    obl = 23.44
    rows = engine["sahl_house_master_direction"](data, "Venus", obl, 0.0)
    got = {r["Target"]: float(r["Arc (years)"]) for r in rows}
    assert got["the Sun's degree (burning)"] == pytest.approx(math.degrees(math.atan(math.cos(math.radians(obl)) * math.tan(math.radians(15.0)))), abs=0.01)
    assert got["Saturn's body"] == pytest.approx(90.0, abs=1e-6)
    assert got["Mars's square (right)"] == pytest.approx(90.0, abs=1e-6)
    assert "Mars's body" not in got and "Saturn's opposition" not in got
    assert [r["Target"] for r in rows][0] == "the Sun's degree (burning)"          # age order
    assert rows[0]["In the year of age"] == 13
    assert engine["sahl_house_master_direction"](data, "Venus", obl, 70.0) is None   # D-23
    assert engine["sahl_house_master_direction"](data, "Pluto", obl, 0.0) is None


def test_sahl_house_master_flags_name_the_infortune_the_eighth_and_the_fall(engine):
    """1.23, 12: an infortune, or the lord of the eighth; 1.23, 53:
    retrograde or in its fall. Scorpio rising: the eighth is Gemini,
    Mercury's; Saturn at 10 Aries retrograde is in his fall."""
    data, cusps = _sahl_chart(215.0, Saturn=(10.0, -0.03))
    flags = engine["sahl_house_master_flags"]("Saturn", data, cusps)
    assert any("infortune" in f for f in flags) and any("fall" in f for f in flags) and any("retrograde" in f for f in flags)
    assert not any("eighth" in f for f in flags)
    assert any("lord of the eighth (Gemini)" in f for f in engine["sahl_house_master_flags"]("Mercury", data, cusps))
    assert engine["sahl_house_master_flags"](None, data, cusps) == []


def test_sahl_releaser_in_the_bundle_feeds_the_governor_and_the_proxies(engine):
    """The bundle carries the releaser, its distribution and the
    house-master's direction; when a releaser and a current segment exist,
    the governor's testimony #3 is that distribution's distributor and is
    counted; #4 is counted only when both distributions share a partner."""
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), rule,
                                    {"Hour Lord": "Venus", "Approximate": False})
    rel = b["releaser"]
    assert rel["releaser"] == "the Sun" and rel["house_master"] == "Saturn"
    assert b["releaser_note"] is None and b["releaser_stand"]["distributor"] in engine["PN4_SEVEN"]
    gov_rows, gov = b["governor"]
    assert gov_rows[2]["Planet"] == b["releaser_stand"]["distributor"] and gov_rows[2]["Counted"] == "yes"
    both = b["current"]["partner"] == b["releaser_current"]["partner"]
    assert gov_rows[3]["Counted"] == ("yes" if both else "no")
    assert b["hm_direction"] and all(r["In the year of age"] == int(float(r["Arc (years)"])) for r in b["hm_direction"])
    assert [r["Fact"] for r in b["hm_revolution"]][:2] == ["Saturn in the revolution", "Burned at the revolution"]
    # the same chart at the year the earliest target falls in: the page's "this year" list is that row
    first = b["hm_direction"][0]
    b2 = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(),
                                     (birth + timedelta(days=365.2425 * first["In the year of age"] + 10)).date(), rule,
                                     {"Hour Lord": "Venus", "Approximate": False})
    assert b2["hm_this_year"] and b2["hm_this_year"][0]["Target"] == first["Target"]
    # a year whose lord is a luminary reads the releaser's distributor and sign in its first proxies
    stand = {"distributor": "Venus", "partner": "Sun", "sign": "Gemini", "lord": "Mercury", "note": None}
    sun_rows = engine["pn4_luminary_proxies"]("Sun", chart, b["sr"], None, None, stand)
    assert sun_rows[0]["Reads"].startswith("Venus (the releaser's distributor") and sun_rows[1]["Reads"].startswith("Gemini, lord Mercury")
    moon_rows = engine["pn4_luminary_proxies"]("Moon", chart, b["sr"], b["moon"], None, {"note": "no releaser by 1.15"})
    assert moon_rows[0]["Reads"] == "unavailable: no releaser by 1.15" == moon_rows[1]["Reads"]
    assert engine["pn4_luminary_proxies"]("Moon", chart, b["sr"], b["moon"], None, None)[0]["Reads"].startswith("unavailable: the sign")
    syz = b["syzygies"]
    assert 0.0 <= syz["meeting"]["longitude"] < 360.0 and syz["fullness"]["jd"] < chart["julian_day"] and syz["meeting"]["jd"] < chart["julian_day"]


# --- CONV-SOLAR_BURNED_ORB: VII.2, 44 as printed for the direct eastern inferior ---

@pytest.mark.parametrize("planet", ["Venus", "Mercury"])
def test_direct_eastern_inferior_leaves_burning_at_six_degrees_as_vii_2_44_prints(engine, planet):
    """VII.2, 44: an inferior that has gone direct in the east (43) is
    "simply under the rays until there are 6 degrees between them and [the
    Sun]"; fn 43 doubts the 6 and keeps it. Applied as printed: at 6.5
    degrees east and direct, 'Under the rays'; retrograde there (37/40's
    7), 'Burned'; 6.5 west and direct (47's 7), 'Burned'; 5.5 east and
    direct (45), 'Burned'; with no speed the 7 stands."""
    sp = engine["solar_phase"]
    assert sp(planet, 93.5, 100.0, 1.0)[0] == "Under the rays"
    assert sp(planet, 93.5, 100.0, -0.5)[0] == "Burned"
    assert sp(planet, 106.5, 100.0, 1.0)[0] == "Burned"
    assert sp(planet, 94.5, 100.0, 1.0)[0] == "Burned"
    assert sp(planet, 93.5, 100.0)[0] == "Burned"
    assert "VII.2, 44" in engine["solar_phase_note"](planet, "eastern", 1.0, 6.5)
    assert engine["solar_phase_note"](planet, "eastern", 1.0, 7.5) == ""
    assert engine["solar_phase_note"]("Mars", "eastern", 1.0, 6.5) == ""


# --- PN4R-4g-2: indicator #9 from the three places of II.6, 1 -----------------

def test_pn4_indicator_nine_reads_the_lord_of_the_years_house_from_the_three_places(engine):
    """II.6, 1: "in one of the stakes of the Ascendant of the root, or of
    the terminal point, or of the Ascendant of the revolution" -- three
    counts, in row 14's format; the row had read the revolution's alone."""
    rows = _rows(engine)
    reads = rows[9]["Reads"]
    assert "from the natal Ascendant / the terminal sign / the revolution Ascendant" in reads
    assert " in house " in reads and reads.split(" in house ")[1].split(" (")[0].count("/") == 2
    assert "II.6, 1" in rows[9]["Source"]


# --- DEC-D-5 as implemented (sheet row 9): condition 110 keeps 19 Libra-3 Scorpio, labelled Abu Ma'shar's ---

@pytest.mark.parametrize("moon, fires", [(182.0, False), (205.0, True), (212.9, True), (213.0, False), (235.0, False)])
def test_moon_corruption_110_keeps_the_borrowed_19_libra_3_scorpio_span_and_says_whose_it_is(engine, moon, fires):
    """Introduction 3, 110: "at the end of Libra and the beginning of
    Scorpio" -- no degrees. The span tested is Gr. Intr. VII.6, 40's
    (fn 120), borrowed and named as such; the Moon at 2 Libra or 25
    Scorpio does not fire (owner, 2026-09-11)."""
    fig = pdata(Moon=(moon, MOON), Venus=(155, VENUS), Mercury=(335, MERC), Sun=(0, 1.0), North_Node=(80, 0.0))
    t = engine["evaluate_corruption_of_the_moon"](fig, 0.0, "Diurnal")["testimonies"][110]
    assert t["matched"] is fires
    if fires:
        assert any("VII.6, 40" in str(c) and "no degrees" in str(c) for c in t["clauses"]), t["clauses"]


# --- REL-2-6 (sheet row 12): 1.15, 16's "good places" are Sahl's seven praised places, by whole-sign place ---

@pytest.mark.parametrize("mars, place, releaser", [(93.0, 9, "the Ascendant"), (267.0, 2, None)])
def test_ascendant_candidates_lord_is_judged_by_the_seven_praised_places(engine, mars, place, releaser):
    """Scorpio rising by day; the Sun at 10 Cancer (the ninth, falling) and
    the meeting at 15 Aries (the sixth) fail, so the Ascendant is examined:
    Venus in Leo squares it (a fortune looking); its lord Mars in his own
    bound. In the NINTH (3 Cancer, Mars's bound 0-7) the ninth is one of
    the seven praised places (Introduction 2, 42; 1.30, 71) though not a
    succedent, so the Ascendant is the releaser; in the SECOND (27
    Sagittarius, Mars's bound 26-30) the second is a succedent but not a
    praised place, so it is not. The old reading (stake or succedent) gave
    the opposite on both."""
    r = _releaser(engine, 215.0, "Diurnal", Mars=mars, Venus=130.0, Jupiter=250.0)
    asc = next(c for c in r["candidates"] if c["Candidate"] == "the Ascendant")
    assert f"whole-sign place {place}" in asc["Verdict"] and "seven praised places" in asc["Verdict"]
    assert r["releaser"] == releaser


# --- REL-2-3: 1.15, 7's gate against 1.16, 4, named on the row -----------------

def test_unwitnessed_luminary_row_names_nawbakhts_gate_and_al_andarzaghars_rule(engine):
    """Scorpio rising by day, the Sun at 15 Virgo (the eleventh, one of
    1.15, 6's five places): its lords are Venus (bound, triplicity, face)
    and Mercury (house, exaltation); with both in Leo, the adjacent sign,
    neither looks. Nawbakht's 1.15, 7 sends the search on; the row
    says so and names al-Andarzaghar's 1.16, 4, which would keep the Sun
    "even if a house-master is not looking". Control: Mercury in Pisces
    opposes Virgo, the Sun is the releaser and the row cites neither."""
    r = _releaser(engine, 215.0, "Diurnal", Sun=165.0, Mercury=145.0)
    sun = next(c for c in r["candidates"] if c["Candidate"] == "the Sun")
    assert "1.15, 7" in sun["Verdict"] and "1.16, 4" in sun["Verdict"] and r["releaser"] != "the Sun"
    assert any(c == "1.16, 4" for c, _t in engine["SAHL_RELEASER_NOT_APPLIED"])
    r2 = _releaser(engine, 215.0, "Diurnal", Sun=165.0, Mercury=340.0)
    sun2 = next(c for c in r2["candidates"] if c["Candidate"] == "the Sun")
    assert r2["releaser"] == "the Sun" and "1.15, 7" not in sun2["Verdict"] and "1.16, 4" not in sun2["Verdict"]


# --- GAP-3: Sahl 1.23, 33 and 1.24, 2 shown side by side; PN IV ranks by scope ---

def test_year_indicator_note_shows_sahls_two_sentences_and_does_not_claim_to_resolve_them(engine):
    note = engine["PN4_YEAR_INDICATOR_SCOPE_NOTE"]
    assert "1.23, 33" in note and "1.24, 2" in note and "fn 245" in note
    assert "tender [of sheep]" in note and "stronger <than> the distributor of time" in note
    assert "II.1, 25" in note and "III.2, 2-3" in note
    assert "resolves the corpus disagreement" not in note and "not resolved" in note


# --- GAP-27: the seven-day grant of IX.7, 7-9 is built (method 2), and the page no longer says otherwise ---

def test_orb_lord_holds_the_first_week_of_ix_7_7(engine):
    """IX.7, 7: the lord of the orb "grants 7 days"; at day 0 of the
    revolution the week, the day and the hour are its own."""
    m2 = engine["pn4_ix7_weeks_from_orb"](0.0, "Venus")
    assert m2["week"] == "Venus" and m2["day"] == "Venus"
    from conftest import engine_source
    assert "IX.7, 7-8 are not built" not in engine_source()


# --- FINAL-A7 (sheet row 8): the stand-in of 1.32, 11-13 in the empty case ---------------

def test_no_releaser_names_the_stand_in_and_the_moon_is_directed(engine):
    """Scorpio rising by day: the Sun at 10 Cancer (ninth, falling) and the
    meeting at 15 Aries (sixth) fail; no fortune looks at Scorpio (Venus
    and Jupiter both in Sagittarius, the adjacent sign), so the Ascendant
    fails 1.15, 16. The verdict now quotes 1.32, 13 across the page break
    -- "the first of them is the Ascendant, then the Moon" -- and 1.32,
    11-13 is no longer listed as not applied."""
    r = _releaser(engine, 215.0, "Diurnal", Venus=240.0, Jupiter=250.0)
    assert r["releaser"] is None
    assert "1.32, 11" in r["verdict"] and "the first of them is the Ascendant, then the Moon" in r["verdict"]
    assert "not applied" not in r["verdict"]
    assert not any(c == "1.32, 11-13" for c, _t in engine["SAHL_RELEASER_NOT_APPLIED"])


# --- FINAL-A2 (sheet row 2): IX.8, 30's turning of the indicator, a year a sign ---------------

def test_house_master_turning_reaches_the_cutters_bodies_oppositions_and_squares(engine):
    """Jupiter the house-master at 15 Aries; Saturn at 10 Gemini, Mars at
    20 Libra. Turned a year a sign from Aries: year 0 (Aries) is Mars's
    opposition sign; year 2 (Gemini) Saturn's body; year 3 (Cancer) Mars's
    square (right: Libra less three signs); year 6 (Libra) Mars's body;
    year 12 Aries again. Years 1 and 4 reach nothing."""
    p = pdata(Jupiter=(15.0, 0.08), Saturn=(70.0, 0.03), Mars=(200.0, 0.5), Sun=(300.0, 1.0), Moon=(10.0, 13.0))
    rows = engine["sahl_house_master_turning"]("Jupiter", p, span_years=13)
    by_year = {r["Year of age"]: r["Reaches"] for r in rows}
    assert "Mars's opposition" in by_year[0] and by_year[0].count(",") == 0
    assert by_year[2] == "Saturn's body"
    assert by_year[3] == "Mars's square (right)"
    assert by_year[6] == "Mars's body"
    assert by_year[12] == by_year[0]
    assert all(r["Source"] == "PN IV IX.8, 30" for r in rows)
    assert 1 not in by_year and 4 not in by_year


# --- Sheet row 3 (owner's ruling): the Lot of Fortune tested by whole-sign place, the planets by the division ---

def test_lot_of_fortune_candidate_is_placed_by_whole_sign_and_the_moon_by_the_division(engine):
    """A night chart with Scorpio rising at 5 Scorpio and unequal cusps
    (the third division opening at 10 Sagittarius). The Moon at 13
    Sagittarius stands in the second whole sign but the third division,
    so by the POWER unit she is falling and fails; the fullness at 10
    Virgo (the twelfth division and sign) fails; the Lot of Fortune at 15 Sagittarius has no
    dynamic angularity and is tested by whole-sign place -- the second, a
    succedent -- with Jupiter (its house and triplicity lord) in its sign,
    so the Lot is the releaser. Under the old division test the Lot too
    would have been falling (third division)."""
    data, _ = _sahl_chart(215.0, Moon=253.0, Jupiter=250.0, Sun=100.0)
    cusps = [215.0, 228.0, 250.0, 275.0, 305.0, 335.0, 35.0, 48.0, 70.0, 95.0, 125.0, 155.0]
    r = engine["sahl_releaser"](data, 215.0, cusps, "Nocturnal", 255.0, 100.0, 160.0)
    moon = next(c for c in r["candidates"] if c["Candidate"] == "the Moon")
    lot = next(c for c in r["candidates"] if c["Candidate"] == "the Lot of Fortune")
    key = "House (division, 5 deg at the stakes; the Lot by whole-sign place)"
    assert moon[key] == 3 and "falling" in moon["Verdict"]
    assert lot[key] == 2 and r["releaser"] == "the Lot of Fortune"


# --- FINAL-A1 (sheet row 1): the house-master's years from 1.20, 7-34, by the division ---------

def _years(engine, planet, sect="Nocturnal", **planets):
    data, cusps = _sahl_chart(215.0, **planets)                 # Scorpio rising; the cusps equal the signs
    ess = engine["evaluate_essential_dignities"](data, sect)
    return engine["sahl_house_master_years"](planet, data, cusps, sect, ess)


def test_house_master_years_greater_in_an_enhanced_stake_and_middle_in_a_bare_one(engine):
    """1.20, 10: Jupiter at 15 Taurus (the seventh, "the sign of the west";
    his own bound, 14-22), eastern of a Sun at 10 Gemini, direct, not under
    the rays -- enhanced, the greater years (79). 1.20, 20 with fn 158: the
    same Jupiter at 5 Taurus (Venus's bound, no share) is a bare stake,
    direct and unburned -- the middle years (45.5)."""
    g = _years(engine, "Jupiter", Jupiter=45.0, Sun=70.0)
    assert (g["grade"], g["sentence"], g["years"], g["division"]) == ("greater", "1.20, 10", 79, 7)
    assert "the sign of the west" in g["text"]
    g = _years(engine, "Jupiter", Jupiter=35.0, Sun=70.0)
    assert (g["grade"], g["sentence"], g["years"]) == ("middle", "1.20, 20", 45.5)


def test_house_master_years_second_eighth_falling_and_the_third_retrograde(engine):
    """16: the second or eighth = middle (Jupiter at 15 Gemini, the eighth).
    28: the other falling places = lesser (Jupiter at 15 Aries, the sixth).
    33: the third, retrograde under the rays = days, no count restated
    (Mercury at 15 Capricorn retrograde with the Sun at 20 Capricorn).
    34: with that in its fall = hours (Jupiter there: Capricorn is his fall)."""
    assert (_years(engine, "Jupiter", Jupiter=75.0, Sun=70.0)["sentence"]) == "1.20, 16"
    g = _years(engine, "Jupiter", Jupiter=15.0, Sun=70.0)
    assert (g["grade"], g["sentence"], g["years"]) == ("lesser", "1.20, 28", 12)
    data, cusps = _sahl_chart(215.0, Mercury=285.0, Sun=290.0)
    data["Mercury"]["speed_in_lon"] = -0.5
    ess = engine["evaluate_essential_dignities"](data, "Diurnal")
    g = engine["sahl_house_master_years"]("Mercury", data, cusps, "Diurnal", ess)
    assert (g["grade"], g["sentence"], g["years"]) == ("days", "1.20, 33", None) and "not restated" in g["text"]
    data, cusps = _sahl_chart(215.0, Jupiter=285.0, Sun=290.0)
    data["Jupiter"]["speed_in_lon"] = -0.05
    ess = engine["evaluate_essential_dignities"](data, "Diurnal")
    g = engine["sahl_house_master_years"]("Jupiter", data, cusps, "Diurnal", ess)
    assert (g["grade"], g["sentence"]) == ("hours", "1.20, 34")
    assert any("14-15" in f for f in g["flags"])           # a superior, retrograde and burned: 14-15 printed, not applied


def test_house_master_years_are_by_the_division_not_the_sign(engine):
    """The unit is the owner's: a planet 3 degrees before the tenth cusp is
    in the tenth DIVISION by the five-degree allowance, though in the
    ninth SIGN. Cusps unequal here; Jupiter at 12 Leo, the Midheaven cusp
    at 15 Leo, in his own triplicity by night, eastern, direct: the
    greater years by 10 -- by whole sign he would have been in the ninth."""
    data, _ = _sahl_chart(215.0, Jupiter=132.0, Sun=170.0)
    cusps = [215.0, 245.0, 275.0, 305.0, 335.0, 5.0, 35.0, 65.0, 95.0, 135.0, 165.0, 190.0]
    ess = engine["evaluate_essential_dignities"](data, "Nocturnal")
    g = engine["sahl_house_master_years"]("Jupiter", data, cusps, "Nocturnal", ess)
    assert g["division"] == 10 and engine["get_wsh_house"](132.0, 215.0) == 10   # both tenth here: Leo IS the tenth sign
    data, _ = _sahl_chart(215.0, Jupiter=132.0, Sun=170.0)
    cusps = [215.0, 245.0, 275.0, 305.0, 335.0, 5.0, 35.0, 65.0, 105.0, 135.0, 165.0, 190.0]
    g = engine["sahl_house_master_years"]("Jupiter", data, cusps, "Nocturnal", ess)
    assert g["division"] == 10 and (g["grade"], g["sentence"]) == ("greater", "1.20, 10")
    cusps2 = [215.0, 245.0, 275.0, 305.0, 335.0, 5.0, 35.0, 65.0, 105.0, 140.0, 165.0, 190.0]   # the cusp 8 degrees on: the ninth division
    g2 = engine["sahl_house_master_years"]("Jupiter", data, cusps2, "Nocturnal", ess)
    assert g2["division"] == 9 and g2["sentence"] == "1.20, 26"


# --- FINAL-A4 (sheet row 5): 2.13, 48-51 under its own name; the engine's generalisation labelled; Aphorism 45 as printed ---

def _bands(engine, lat=0.0, sect="Diurnal", asc=0.0, mc=270.0, **planets):
    base = dict(Sun=20.0, Moon=200.0, Mercury=110.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=160.0)
    base.update(planets)
    return engine["evaluate_ascensional_bands"](pdata(**base), asc, mc, 23.4392911, lat, sect)


def test_2_13_grades_the_sect_lights_first_triplicity_lord_only_and_the_display_grades_all(engine):
    """Day chart, the Sun at 20 Aries: the fire triplicity's first lord by
    day is the Sun himself. At the equator with 0 Aries rising the
    ascension from the Ascendant equals right ascension: 20 Aries is 18.4
    degrees of ascension past the stake -- the SECOND band, "good fortune
    below the first" (49). Mercury at 10 Aries stands in the first band
    of the same stake with the engine's grade only, no 2.13 judgment; by
    Aphorism 45 as printed Mercury (10 zodiacal degrees) is within and
    the Sun (20) beyond, neither applied."""
    out = _bands(engine, Sun=20.0, Mercury=10.0)
    rows = {r["Planet"]: r for r in out["rows"]}
    assert out["first_lord"] == "Sun" and out["judged"]["band"] == "second 15 degrees"
    assert "below the first" in rows["Sun"]["2.13, 48-51 (the sect light's first triplicity lord only)"]
    assert rows["Mercury"]["2.13, 48-51 (the sect light's first triplicity lord only)"] == "-"
    assert rows["Mercury"]["Engine grade (generalised from 2.13, 48-51)"] == "first 15 degrees of ascension"
    assert rows["Mercury"]["Aphorism #45 as printed (15 zodiacal degrees; not applied)"] == "within"
    assert rows["Sun"]["Aphorism #45 as printed (15 zodiacal degrees; not applied)"] == "beyond"
    assert rows["Sun"]["Follows the stake"].startswith("Ascendant")


def test_2_13_bands_are_end_inclusive_and_truncated_by_the_next_stake(engine):
    """At the equator RA(x) < x in Aries, so a planet whose RA is exactly
    15 sits in band one (end-inclusive); the Midheaven at 30 Aries makes
    a planet at 40 Aries follow the MIDHEAVEN by right ascension, not the
    Ascendant, and the remainder is bounded by the next actual stake."""
    out = _bands(engine, Sun=16.0, mc=30.0)                     # RA(16 Aries) = 14.7: band one, inclusive of 15
    assert {r["Planet"]: r for r in out["rows"]}["Sun"]["Engine grade (generalised from 2.13, 48-51)"] == "first 15 degrees of ascension"
    out = _bands(engine, Sun=40.0, mc=30.0)
    sun = {r["Planet"]: r for r in out["rows"]}["Sun"]
    assert sun["Follows the stake"].startswith("Midheaven") and "right ascension" in sun["Ascensional distance"]
    out = _bands(engine, Sun=60.0, mc=270.0)                    # 60 Aries-Taurus: RA 57.8 past the Ascendant, the remainder
    assert {r["Planet"]: r for r in out["rows"]}["Sun"]["Engine grade (generalised from 2.13, 48-51)"] == "the remainder, up to the next stake"


def test_2_13_refuses_at_the_poles(engine):
    out = _bands(engine, lat=70.0)
    assert out["rows"] == [] and "D-23" in out["refused"]


# --- DEC-D-18 (sheet row 11): spear-bearing, two display-only definitions ---------------------

def test_right_sidedness_strong_and_by_sect(engine):
    """2.5, 2: Jupiter in Cancer (exaltation) sextile Venus in Taurus
    (domicile), connected -- strong. 2.5, 3: Saturn at 10 Leo and Jupiter at
    10 Libra, neither in house nor exaltation nor any share, both diurnal,
    sextile and connected -- "below the first". Jupiter at 6 Leo and Mars
    at 10 Libra (opposite sects, no dignities) in sextile: no grade."""
    p = pdata(Sun=280.0, Moon=160.0, Mercury=270.0, Venus=40.0, Mars=210.0, Jupiter=100.0, Saturn=330.0)
    rows = {r["Pair"]: r for r in engine["evaluate_right_sidedness"](p, "Diurnal")}
    assert rows["Jupiter and Venus"]["Grade"].startswith("strong")
    p = pdata(Sun=280.0, Moon=160.0, Mercury=270.0, Venus=300.0, Mars=210.0, Jupiter=190.0, Saturn=130.0)
    rows = {r["Pair"]: r for r in engine["evaluate_right_sidedness"](p, "Diurnal")}
    assert "below the first" in rows["Saturn and Jupiter"]["Grade"] and rows["Saturn and Jupiter"]["One sect"] == "yes"
    p = pdata(Sun=280.0, Moon=160.0, Mercury=270.0, Venus=300.0, Mars=190.0, Jupiter=126.0, Saturn=330.0)
    rows = {r["Pair"]: r for r in engine["evaluate_right_sidedness"](p, "Diurnal")}
    assert rows["Jupiter and Mars"]["Grade"] == "-" and rows["Jupiter and Mars"]["One sect"] == "no"


def test_honor_guard_reads_eastern_from_the_sun_and_western_from_the_moon(engine):
    """10.2.1, 10: Mars at 5 Capricorn rises before a Sun at 10 Capricorn
    (eastern from him) and after a Moon at 20 Sagittarius (western from
    her): an honor-guard; Saturn at 20 Capricorn is western from both."""
    p = pdata(Sun=280.0, Moon=260.0, Mercury=300.0, Venus=310.0, Mars=275.0, Jupiter=100.0, Saturn=290.0)
    rows = {r["Planet"]: r for r in engine["evaluate_honor_guard"](p, 270.0)}
    assert rows["Mars"]["Role"] == "honor-guard" and rows["Mars"]["In a stake"] == "yes"
    assert rows["Saturn"]["Role"] == "-" and rows["Saturn"]["Eastern from the Sun"] == "no"
    assert rows["Sun"]["Sign"].endswith("(female)") and rows["Sun"]["In a stake"] == "yes"


# --- PN4R-4e-2: the six named lords of the orb by VI.1, 10 and by VI.1, 8 -------------------

def test_named_lords_of_the_orb_show_both_vi_1_10_and_vi_1_8(engine):
    """Natal hour lord Venus, 14 completed years: the sign of the terminal
    point is the third house; by VI.1, 10 its lord is the third hour from
    Venus (the Moon); by VI.1, 8 the hour lord it received when the
    profection last reached it is the fifteenth hour, which is the year's
    lord of the orb. At 2 completed years both columns agree."""
    rows = {r["Position"]: r for r in engine["pn4_named_lords_of_the_orb"]("Venus", 14)}
    k10, k8 = "Lord of the hour (VI.1, 10)", "By VI.1, 8's assignment (the hour lord the house received when the profection last reached it)"
    r = rows["Sign of the terminal point"]
    assert r["House"] == 3 and r[k10] == engine["pn4_hour_lord_from_natal"]("Venus", 2)
    assert r[k8] == engine["pn4_lord_of_the_orb"]("Venus", 14) and r[k8] != r[k10]
    early = {r["Position"]: r for r in engine["pn4_named_lords_of_the_orb"]("Venus", 2)}["Sign of the terminal point"]
    assert early[k10] == early[k8]
    assert {r["Position"]: r for r in engine["pn4_named_lords_of_the_orb"]("Venus", 5)}["Midheaven of the root"][k8] == "-"


# --- PN4R-4l-7: II.3, 2 [3]'s twelfth-parts, computed -------------------------------------

def test_ii3_lists_the_planets_whose_twelfth_parts_fall_in_the_terminal_sign(engine):
    """Terminal sign Cancer. Saturn at 4 Gemini: its second twelfth-part
    (2.5-5 of Gemini) is Cancer, so Saturn's twelfth-part falls in the
    sign; Mars at 20 Capricorn (twelfth-part in Virgo) does not."""
    root, sr, _ = _ii3_pair(engine, year_lon=95.0)
    root["planetary_data"]["Saturn"]["longitude"] = 64.0
    root["planetary_data"]["Mars"]["longitude"] = 290.0
    year = {"sign": "Cancer", "longitude": 95.0, "lord": "Moon"}
    out = engine["pn4_ii3_examination"](root, sr, year, 2451545.0)
    reads = out["root_rows"][2]["Reads"]
    assert "twelfth-parts of: " in reads and "Saturn" in reads.split("twelfth-parts of: ")[1]
    assert "Mars" not in reads.split("twelfth-parts of: ")[1]
    assert "not computed" not in reads and "V.18, 3" in out["root_rows"][2]["Source"]
    assert "twelfth-parts of:" in out["revolution_rows"][0]["Reads"]


# --- PN4R-4a-1 and 4a-2: III.7, 35's "not looking"; III.7, 42 against every distribution -----

def test_fixed_sign_planet_that_looks_at_the_ascendant_is_not_given_35s_once(engine):
    """Saturn at 10 Taurus (fixed) under a Leo Ascendant: Taurus squares
    Leo, so 35's "not looking" does not hold and the row names 36; under
    an Aries Ascendant Taurus is in aversion and the "once" stands. With no
    Ascendant given the quadruplicity label is printed as before."""
    look = next(r for r in engine["pn4_activation_ages"](pdata(Saturn=40.0), 23.44, 43.78, ascendant_lon=125.0) if r["Planet"] == "Saturn")
    assert "III.7, 36" in look["Manifests"] and "square" in look["Manifests"]
    avert = next(r for r in engine["pn4_activation_ages"](pdata(Saturn=40.0), 23.44, 43.78, ascendant_lon=5.0) if r["Planet"] == "Saturn")
    assert avert["Manifests"].startswith("once in the lifespan") and "III.7, 35" in avert["Manifests"]
    plain = next(r for r in engine["pn4_activation_ages"](pdata(Saturn=40.0), 23.44, 43.78) if r["Planet"] == "Saturn")
    assert plain["Manifests"] == "once in the lifespan (III.7, 35)"


def test_activation_confirmation_names_the_distribution_that_confirms(engine):
    """A planet confirmed by the Midheaven's distribution and not by the
    Ascendant's is now confirmed, with the distribution named."""
    points = pdata(Mercury=40.0, Saturn=200.0, Sun=100.0, Moon=300.0)
    asc_segs = engine["pn4_distribution_from_ascendant"](points, 110.0, 23.44, 43.78)
    mc_segs = engine["pn4_distribution_from_meridian"](points, 20.0, 23.44, 'Midheaven')
    rows = engine["pn4_activation_ages"](points, 23.44, 43.78, distributions={"the Ascendant's distribution": asc_segs,
                                                                             "the Midheaven's distribution": mc_segs})
    claims = [c for r in rows for c in r["Confirmed by the distribution"].split(";") if "as " in c]
    assert claims and all(("Ascendant's" in c) or ("Midheaven's" in c) for c in claims)
    for r in rows:
        for c in r["Confirmed by the distribution"].split(";"):
            if "as " not in c:
                continue
            age = float(c.split("(")[1].split(",")[0])
            segs = mc_segs if "Midheaven's" in c else asc_segs
            seg = engine["pn4_distribution_at_age"](segs, age)
            assert r["Planet"] in (seg["distributor"], seg["partner"])
    only_asc = engine["pn4_activation_ages"](points, 23.44, 43.78, asc_segs)
    assert all("Ascendant's" in c for r in only_asc for c in r["Confirmed by the distribution"].split(";") if "as " in c)


# --- DIS-9: the caveat row names Sahl's own quadrant timing beside On Times 1's hemispheres ----

def test_quick_and_slow_places_caveat_names_sahls_own_natal_timing(engine):
    row = next(t for c, t in engine["NOT_IMPLEMENTED_COVERAGE"] if "ADVANCING_BY_QUADRANT_FIG90" in t)
    assert "7.4, 17" in row and "5.3, 11-12" in row and "6.5, 1" in row and "On Choices 6, 16-17" in row


# --- PN4R-4h-4: IX.2, 5's partial rule when the strict governor fails ------------------------

def test_first_month_governor_names_the_primary_sign_when_the_strict_test_fails(engine):
    """Natal Ascendant 5 Aries, natal Lot 5 Cancer (not in the Ascendant, so
    the strict test fails); the terminal sign Leo (offset four): the Lot's
    terminal is Scorpio; the revolution's Ascendant and Lot both in Leo;
    Leo's first ninth-part is Aries. Leo holds three of five -- primary,
    Scorpio and Aries the partners. With the revolution's Ascendant and Lot
    in Scorpio the tally is Leo 1, Scorpio 3, Aries 1 -- Scorpio primary."""
    rows, verdict = engine["pn4_first_month_governor"](5.0, 95.0, 125.0, 130.0, 135.0)
    assert verdict.startswith("no governor") and "Primary: Leo (3 of five" in verdict and "Scorpio" in verdict.split("partners:")[1]
    assert rows[-1]["Source"] == "IX.2, 5; fn 38"
    rows, verdict = engine["pn4_first_month_governor"](5.0, 95.0, 125.0, 220.0, 225.0)
    assert "Primary: Scorpio (3 of five" in verdict
    rows, verdict = engine["pn4_first_month_governor"](5.0, 5.0, 185.0, 190.0, 195.0)     # Libra, convertible: the strict case
    assert "govern the first month" in verdict and len(rows) == 5


# --- GAP-37 / PN4R-4b-4: the planets in the Midheaven, the fourth and the Ascendant, directed -----

def test_planets_in_the_angular_divisions_are_directed_as_their_degrees_are(engine):
    """III.1, 12. A meridian distribution from a planet's own degree runs by
    right ascension from that degree; the bundle lists every planet whose
    division is 1, 10 or 4 with its own table."""
    p = pdata(Sun=100.0, Moon=200.0, Mercury=110.0, Venus=130.0, Mars=300.0, Jupiter=250.0, Saturn=20.0)
    segs = engine["pn4_distribution_from_meridian"](p, 15.0, 23.44, start_lon=22.0, label="Saturn in the Midheaven")
    assert segs and segs[0]["from"] == 0.0 and segs[0]["from_lon"] == pytest.approx(22.0)
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), engine["PN4_MONTHLY_TURN_OPTIONS"][0])
    for ap in b["angle_planets"]:
        assert ap["division"] in (1, 10, 4) and ap["division"] == engine["get_effective_house"](chart["planetary_data"][ap["planet"]]["longitude"], chart["houses"])
        assert ap["how"] == ("oblique ascension of the birth latitude" if ap["division"] == 1 else "right ascension")
    expected = [pl for pl in engine["PN4_SEVEN"] if engine["get_effective_house"](chart["planetary_data"][pl]["longitude"], chart["houses"]) in (1, 10, 4)]
    assert [ap["planet"] for ap in b["angle_planets"]] == expected


# --- GAP-2: the year of the turning reaching the partner's body (1.24, 4-5; 1.23, 23) ---------

def test_turning_reaches_the_partners_natal_body_while_it_holds(engine):
    """Ascendant 5 Aries; at age 4 the year of the turning is Leo. A current
    segment whose partner is Jupiter, natal in Leo: "preferable" (1.23,
    23); the partner Saturn in Leo: "the infortunes are worse"; a partner in
    Virgo: not reached."""
    seg = [{"from": 0.0, "to": 10.0, "from_lon": 5.0, "distributor": "Mars", "partner": "Jupiter", "partner_aspect": "trine",
            "partner_from": "", "opened_by": ""}]
    p = pdata(Jupiter=130.0, Saturn=135.0, Venus=160.0, Sun=100.0, Moon=200.0, Mercury=110.0, Mars=300.0)
    r = engine["sahl_turning_reaches_partner"](seg, 4, 5.0, p)
    assert r["holds"] and r["sign_of_year"] == "Leo" and "preferable" in r["verdict"]
    seg[0]["partner"] = "Saturn"
    assert "worse" in engine["sahl_turning_reaches_partner"](seg, 4, 5.0, p)["verdict"]
    seg[0]["partner"] = "Venus"
    r = engine["sahl_turning_reaches_partner"](seg, 4, 5.0, p)
    assert not r["holds"] and r["verdict"] == "-"
    seg[0]["partner"] = None
    assert engine["sahl_turning_reaches_partner"](seg, 4, 5.0, p) is None


# --- PN4R-4f-6: VI.2, 4-5's triplicity lords beside the turning -----------------------------

def test_turning_triplicity_lords_for_assets_and_siblings(engine):
    """Day chart, Sun in Cancer (water: Venus, Mars, Moon by day) for assets
    (VI.2, 4); Mars in Aquarius (air: Saturn, Mercury, Jupiter) for siblings
    (VI.2, 5), the first lord the older siblings. Conditions come from both
    charts."""
    root, sr, _ = _two_charts(engine, natal=dict(Sun=100.0, Mars=310.0), rev=dict(Venus=200.0, Saturn=10.0))
    rows = engine["pn4_turning_triplicity_lords"](root, sr)
    assets = [r for r in rows if r["Topic"] == "assets"]
    sibs = [r for r in rows if r["Topic"] == "siblings"]
    assert [r["Lord"] for r in assets] == ["Venus", "Mars", "Moon"] and assets[0]["Source"].startswith("VI.2, 4")
    assert [r["Lord"] for r in sibs] == ["Saturn", "Mercury", "Jupiter"] and sibs[0]["Siblings (5)"] == "the older"
    assert assets[0]["Revolution condition"].startswith("Libra") and sibs[0]["Revolution condition"].startswith("Aries")


# --- PN4R-4g-5: indicator #15, the lords' connections in the revolution ---------------------

def test_indicator_fifteen_reads_the_three_lords_connections_when_given_the_moment(engine):
    """Without the revolution's moment the row says so; with it, each of
    VI.6, 1's three lords is followed until it leaves its sign and its
    perfections with the other house lords are listed."""
    rows = _rows(engine)
    assert rows[15]["Reads"].startswith("NOT computed here")
    cast = engine["calculate_traditional_chart"]
    birth, lat, lon = datetime(1985, 3, 20, 14, 30), 51.5, -0.12
    chart = cast(birth, lat, lon)
    b = engine["pn4_timing_bundle"](chart, lat, lon, birth.date(), datetime(2027, 6, 1).date(), engine["PN4_MONTHLY_TURN_OPTIONS"][0])
    r15 = next(r for r in b["further_rows"] if r["#"] == 15)
    assert "the lord of the natal Ascendant" in r15["Reads"] and "the lord of the revolution's Ascendant" in r15["Reads"]
    assert "NOT computed" not in r15["Reads"] and r15["Source"] == "II.1, 20; VI.6, 1-3"
