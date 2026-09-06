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
