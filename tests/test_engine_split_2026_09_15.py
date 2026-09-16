"""The engine's move into engine.py, and the readings that moved with it.

Two things are proved here. The third, the migration's own differential --
every evaluator run on main's engine half and on engine.py over all six
fixture charts and both values of every switch -- is retired: main's app.py
has had no engine half above the UI marker since the split merged, so the
test could only skip. Its run is recorded in docs/ENGINE_SPLIT_2026-09-15.md.

**The readings, by value.** One test per reading, asserting that the two
values produce *different* evaluator output -- the gap that let the first
attempt at this split pass its whole suite while every switch was silently
dead, the readings having been assigned into app.py's namespace where no
engine function could see them. Each also runs the two values in two
threads at once and asserts each thread sees its own, which is the reason
the readings are thread-local rather than module globals: Streamlit runs
every session's script in a thread of its own against one imported engine.

**The fixed stars.** The catalogue is attached per thread, because Swiss
Ephemeris keeps its ephemeris path in thread-local state. A second thread
must place as many stars as the first.
"""
from __future__ import annotations

import threading
from datetime import date, datetime

import pytest

from conftest import FLORENCE, LOCAL_TIME

BIRTH = date(1240, 5, 23)
TARGET = date(1283, 5, 23)


def _jd(ns, day):
    """The fixture charts' own instant: Florence, 14:30 LMT, the way the
    sidebar computes it (15 degrees of longitude to the hour)."""
    hour = LOCAL_TIME.hour + LOCAL_TIME.minute / 60.0
    return ns["civil_local_to_jd_ut"](day.year, day.month, day.day, hour, FLORENCE[1] / 15.0)


def _pool(ns, day):
    """Everything the evaluators ask for, by the names they ask for it by."""
    jd = _jd(ns, day)
    chart = ns["calculate_traditional_chart_jd"](jd, *FLORENCE)
    p, cusps, sect = chart["planetary_data"], chart["houses"], chart["sect"]
    asc = chart["ascendant"]
    essential = ns["evaluate_essential_dignities"](p, sect)
    accidental = ns["evaluate_accidental_dignities"](p, cusps, sect, jd, chart["armc"],
                                                     chart["obliquity"], chart["geo_lat"])
    sim = ns["_simulate_forward"](p, chart["julian_day"])
    syzygy = ns["calculate_prenatal_syzygy"](chart["julian_day"], *FLORENCE, cusps)
    chronocrats = ns["calculate_chronocrats"](chart["julian_day"], *FLORENCE, LOCAL_TIME.hour, 0.0)
    condition = ns["evaluate_abu_mashar_condition"](p, cusps, sect, essential, accidental, jd, asc, sim)
    return {
        "jd": jd, "jd_natal": chart["julian_day"], "jd_utc": chart["julian_day"],
        "lat": FLORENCE[0], "lon": FLORENCE[1], "geo_lat": chart["geo_lat"],
        "chart_data": chart, "planetary_data": p, "natal_houses": cusps,
        "houses": cusps, "cusps": cusps, "sect": sect,
        "ascendant_lon": asc, "asc_lon": asc, "asc": asc,
        "mc_lon": chart["mc"], "armc": chart["armc"], "obliquity": chart["obliquity"],
        "sun": p["Sun"]["longitude"], "moon": p["Moon"]["longitude"],
        "essential": essential, "accidental": accidental, "sim": sim,
        "chronocrats": chronocrats, "abu_mashar_condition": condition,
        "lot_of_fortune": chart["lot_of_fortune"], "fortune_lon": chart["lot_of_fortune"],
        "syzygy_lon": syzygy["syzygy_longitude"],
        "birth_date": BIRTH, "target_date": TARGET,
        "rule": ns["PN4_MONTHLY_TURN_OPTIONS"][0], "local_hour": LOCAL_TIME.hour,
        "utc_offset_hours": 0.0,
    }


# --- A. The doctrine differential (retired) ------------------------------
# The differential against main's engine half is recorded in
# docs/ENGINE_SPLIT_2026-09-15.md; main has had no engine half to compare
# with since the split merged, so the test that ran it could only skip.


# --- B. The readings, by value, and by thread ----------------------------
# Each entry: the reading, its two values, and a call on the default chart
# whose output the two values must differ on.

def _aspects(ns, pool):
    return ns["evaluate_ptolemaic_aspects"](pool["planetary_data"])


def _reception(ns, pool):
    return ns["evaluate_reception"](pool["planetary_data"], pool["sect"], pool["sim"])


def _rays(ns, pool):
    return [ns["solar_rays_orb"](p) for p in ("Moon", "Mars", "Venus", "Mercury")]


def _domain(ns, pool):
    return ns["evaluate_accidental_dignities"](pool["planetary_data"], pool["cusps"], pool["sect"],
                                               pool["jd"], pool["armc"], pool["obliquity"], pool["geo_lat"])


def _eastern(ns, pool):
    return ns["evaluate_abu_mashar_condition"](pool["planetary_data"], pool["cusps"], pool["sect"],
                                               pool["essential"], pool["accidental"], pool["jd"],
                                               pool["ascendant_lon"], pool["sim"])


def _topical_lots(ns, pool):
    return ns["calculate_topical_lots"](pool["planetary_data"], pool["asc"], pool["cusps"], pool["sect"])


def _infortunes(ns, pool):
    return sorted(ns["effective_infortunes"]())


READING_CASES = (
    # (reading, value A, value B, call, the chart the two values differ on)
    ("CONNECTION_PROFILE", "Sahl", "Abu Ma'shar", _aspects, "1240-05-23"),
    ("MOON_RAYS_ORB", 12.0, 15.0, _rays, "1240-05-23"),
    ("MARS_WEST_RAYS_18", False, True, _rays, "1240-05-23"),
    ("DOMAIN_RULE", "Abu Ma'shar", "Masha'allah", _domain, "1240-05-23"),
    # The eastern rule moves VII.6, 27 and 45, which the default chart does
    # not reach: of the six fixture charts it changes 1240-09-18, 1240-10-05
    # and 1240-01-04, and the first of those is taken here.
    ("EASTERN_RULE", "hemisphere", "VII.2 band", _eastern, "1240-09-18"),
    ("LOT_HOUSE_CUSP", "whole-sign place", "quadrant cusp", _topical_lots, "1240-05-23"),
    ("SOFTENED_INFORTUNE", None, "Mars", _infortunes, "1240-05-23"),
)

_POOLS = {}


@pytest.fixture
def pool(engine, day):
    """The chart a case names, built once per chart for the module."""
    if day not in _POOLS:
        _POOLS[day] = _pool(engine, date.fromisoformat(day))
    return _POOLS[day]


@pytest.mark.parametrize("name,a,b,call,day", READING_CASES,
                         ids=[c[0] for c in READING_CASES])
def test_a_reading_changes_what_the_engine_answers(engine, pool, name, a, b, call, day):
    """The value-level guard the first attempt at this split did not have:
    the suite passed with every switch dead because the switch tests read
    table shape and widget labels, never a cell."""
    engine["set_readings"](**{name: a})
    first = repr(call(engine, pool))
    engine["set_readings"](**{name: b})
    second = repr(call(engine, pool))
    engine["set_readings"](**{name: a})
    assert first != second, f"{name}: {a!r} and {b!r} produce the same output, so the test proves nothing"


@pytest.mark.parametrize("name,a,b,call,day", READING_CASES,
                         ids=[c[0] for c in READING_CASES])
def test_two_threads_each_see_their_own_reading(engine, pool, name, a, b, call, day):
    """Two runs at once, as two browser sessions are. Each thread pins its
    own value and must get its own answer: a module global would give both
    whichever was written last."""
    results, barrier = {}, threading.Barrier(2)

    def run(value):
        engine["set_readings"](**{name: value})
        barrier.wait(timeout=30)              # both pinned before either reads
        results[value] = repr(call(engine, pool))

    threads = [threading.Thread(target=run, args=(value,)) for value in (a, b)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert set(results) == {a, b}, results.keys()
    assert results[a] != results[b], f"{name}: both threads got the same answer"


def test_a_thread_that_pins_nothing_reads_the_course_text(engine):
    """An engine imported with no run behind it -- the harness's own use --
    answers with the module constants, as it did before the split."""
    done = {}

    def run():
        done["profile"] = engine["reading"]("CONNECTION_PROFILE")
        done["orb"] = engine["reading"]("MOON_RAYS_ORB")
        done["softened"] = engine["reading"]("SOFTENED_INFORTUNE")

    t = threading.Thread(target=run)
    t.start()
    t.join(timeout=30)
    assert done["profile"] == engine["CONNECTION_PROFILE"] == "Sahl"
    assert done["orb"] == engine["MOON_RAYS_ORB"] == 12.0
    assert done["softened"] is engine["SOFTENED_INFORTUNE"] is None


def test_set_readings_refuses_a_name_the_engine_does_not_read(engine):
    with pytest.raises(KeyError):
        engine["set_readings"](FITTING_INFORTUNE=True)


# --- C. The fixed stars, in a second thread ------------------------------

def test_the_star_catalogue_attaches_in_every_thread(engine):
    """Swiss Ephemeris keeps its ephemeris path per thread, so each thread's
    first use must attach the catalogue for itself. Before that was so, the
    Timing page's stars were placed for the first session of a process and
    for no other."""
    jd = 2176000.0
    here = engine["fixed_star_longitudes"](jd)
    assert here, "no catalogue attached in the main thread; the rest proves nothing"
    there = {}

    def run():
        there["stars"] = engine["fixed_star_longitudes"](jd)

    t = threading.Thread(target=run)
    t.start()
    t.join(timeout=60)
    assert len(there["stars"]) == len(here), (
        f"the main thread placed {len(here)} stars and a second thread {len(there['stars'])}: "
        "the catalogue is not being attached per thread")
