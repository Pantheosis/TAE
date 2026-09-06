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


def test_abu_connection_ends_one_minute_past_exact(engine):
    m = 1.0 / 60.0
    for d, expect in ((m - 1e-6, True), (m + 1e-6, False)):
        row = engine["_pairwise_configurations"](pdata(Moon=(10 + d, MOON), Saturn=(130, SAT)))[0]
        assert row["motion"] == "Separating"
        assert engine["_is_connected_abu_mashar"](row) is expect, d
