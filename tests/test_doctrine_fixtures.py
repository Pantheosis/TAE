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


def test_abu_connection_ends_one_minute_past_exact(engine):
    m = 1.0 / 60.0
    for d, expect in ((m - 1e-6, True), (m + 1e-6, False)):
        row = engine["_pairwise_configurations"](pdata(Moon=(10 + d, MOON), Saturn=(130, SAT)))[0]
        assert row["motion"] == "Separating"
        assert engine["_is_connected_abu_mashar"](row) is expect, d


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
    assert "IX.7, 30" in segs[0]["partner_from"]
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
    assert applied["Ascendant, and things in it"] == "applied to the degree of the Ascendant"
    assert applied["Midheaven, or the fourth"] == "applied to the degrees of the Midheaven and the fourth"
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
