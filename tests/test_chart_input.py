"""The chart-input rework of 2026-09-10 (UI_CHART_INPUT_EVALUATION_2026-09-10.md).

What it pins: the pure parsers and the birthday arithmetic the sidebar
and the Timing page use; that a malformed date no longer stops the script
(which used to take the page list with it); that the target of the Timing
page can be set as an age or as a date and the two agree; that a saved
chart carries its time standard and target and restores them; and the bug
that started it -- the owner's reference nativity, recorded EST, loaded at
LMT and forty minutes wrong -- cannot come back: loaded under Standard
time it casts at 16:44 UT, the value tests/test_wheel.py pins.
"""
import json
from datetime import date, time

import pytest

from conftest import EXECUTABLE_DIR, assert_no_exception, make_app

PETOSKEY = (45.37334, -84.95533)


# --- Parsers and arithmetic (engine half) ----------------------------------

@pytest.mark.parametrize("text, expected", [
    ("1240-05-23", date(1240, 5, 23)), (" 1982-11-19 ", date(1982, 11, 19)),
    ("0787-08-10", date(787, 8, 10)), ("1240-5-23", date(1240, 5, 23)),
    ("23/05/1240", None), ("1240-13-01", None), ("", None), (None, None),
])
def test_parse_iso_date(engine, text, expected):
    assert engine["parse_iso_date"](text) == expected


@pytest.mark.parametrize("text, expected", [
    ("45.3733, -84.9553", (45.3733, -84.9553)), ("45.3733 -84.9553", (45.3733, -84.9553)),
    ("-33.9, 151.2", (-33.9, 151.2)), ("Florence", None), ("91, 0", None), ("0, 181", None),
    ("45.3733", None), ("", None),
])
def test_parse_lat_lon(engine, text, expected):
    got = engine["parse_lat_lon"](text)
    assert got == pytest.approx(expected) if expected else got is None


def test_birthday_is_the_first_day_of_that_completed_year(engine):
    """pn4_birthday(b, n) is the first date whose completed years are n,
    so "age 42" and "the 42nd birthday" are the same target."""
    completed, birthday = engine["pn4_completed_years"], engine["pn4_birthday"]
    for b in (date(1982, 11, 19), date(1240, 5, 23), date(2000, 2, 29), date(1999, 12, 31)):
        for n in (0, 1, 17, 42, 43, 120):
            d = birthday(b, n)
            assert completed(b, d) == n, (b, n, d)
            from datetime import timedelta
            assert completed(b, d - timedelta(days=1)) == n - 1 if n else True
    assert birthday(date(2000, 2, 29), 1) == date(2001, 3, 1)
    assert birthday(date(2000, 2, 29), 4) == date(2004, 2, 29)


def test_ordinal(engine):
    o = engine["pn4_ordinal"]
    assert [o(n) for n in (0, 1, 2, 3, 4, 11, 12, 13, 21, 22, 42, 101, 111)] == \
        ["0th", "1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "42nd", "101st", "111th"]


# --- The sidebar under AppTest ----------------------------------------------

def test_a_malformed_date_keeps_the_page_and_says_so():
    at = make_app(date="not a date", page="chart").run()
    assert_no_exception(at, "malformed date")
    assert len(at.main.header) >= 1, "the page vanished (st.stop before st.navigation)"
    assert any("YYYY-MM-DD" in e.value for e in at.sidebar.error)


def test_time_is_to_the_second_and_calendar_is_named():
    at = make_app(page="chart").run()
    assert_no_exception(at, "default chart")
    assert at.sidebar.time_input[0].step == 1
    captions = " ".join(c.value for c in at.sidebar.caption) + " ".join(i.value for i in at.sidebar.info)
    assert "Julian calendar" in captions
    assert at.sidebar.selectbox(key="time_standard_key").value == "LMT (Local Mean Time)"
    assert at.sidebar.toggle(key="manual_coords_key").value is True


def test_coordinates_typed_into_the_place_box_are_used():
    at = make_app(page="chart")
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = "45.3733, -84.9553"
    at.run()
    assert_no_exception(at, "typed coordinates")
    assert any("45.3733, -84.9553" in s.value for s in at.sidebar.success)


def _timing_age_markdown(at):
    for md in at.main.markdown:
        if "completed" in md.value and "birthday opens this year" in md.value:
            return md.value
    pytest.fail("the target read-back line did not render")


def test_target_as_age_and_as_date_agree():
    by_age = make_app(page="timing")
    by_age.session_state["_target_mode"] = "Age"
    by_age.session_state["_target_age"] = 42
    by_age.run()
    assert_no_exception(by_age, "target by age")
    line = _timing_age_markdown(by_age)
    assert "**1282-05-23** -- age **42** completed" in line, line

    by_date = make_app(page="timing")
    by_date.session_state["_target_mode"] = "Date"
    by_date.session_state["_target_date"] = "1282-05-23"
    by_date.run()
    assert_no_exception(by_date, "target by date")
    assert _timing_age_markdown(by_date) == line
    # And the revolution table is the same revolution.
    rev = lambda a: a.main.dataframe[0].value.iloc[0]["Value"]
    assert rev(by_age) == rev(by_date)
    assert by_age.main.number_input(key="target_age").value == 42


def test_the_target_control_sits_on_the_timing_page_not_the_sidebar():
    at = make_app(page="timing").run()
    assert_no_exception(at, "timing")
    assert not [t for t in at.sidebar.text_input if "Target" in t.label]
    assert at.main.radio(key="target_mode").value == "Date"
    assert at.main.text_input(key="target_date").value == date.today().isoformat()


# --- Save and load carry the time standard and the target -------------------

def _saved_charts_path():
    import os
    from pathlib import Path
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "saved_charts.json"


def test_save_stores_standard_and_target_and_load_restores_them(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1982-11-19", page="timing")
    at.session_state["manual_lat_key"], at.session_state["manual_lon_key"] = PETOSKEY
    at.session_state["time_input_key"] = time(11, 44)
    at.session_state["time_standard_key"] = "Standard time (pytz)"
    at.session_state["_target_mode"] = "Age"
    at.session_state["_target_age"] = 43
    at.run()
    assert_no_exception(at, "before save")
    name_box = [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0]
    name_box.set_value("Reference 1982").run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    assert_no_exception(at, "save")
    saved = json.loads(_saved_charts_path().read_text())
    entry = saved["Reference 1982"]
    assert entry["time_standard"] == "Standard time (pytz)"
    assert entry["target_mode"] == "Age" and entry["target_age"] == 43
    assert entry["target_date"] == "2025-11-19"
    assert entry["lat"] == pytest.approx(PETOSKEY[0])

    # A fresh session: load it through the picker's own on_change, exactly
    # as a click does, and the chart is cast under Standard time, 16:44 UT.
    fresh = make_app(page="chart")
    fresh.session_state["time_standard_key"] = "LMT (Local Mean Time)"
    fresh.run()
    fresh.sidebar.selectbox(key="chart_picker").select("Reference 1982").run()
    assert_no_exception(fresh, "load")
    assert fresh.session_state["time_standard_key"] == "Standard time (pytz)"
    assert fresh.session_state["_target_mode"] == "Age" and fresh.session_state["_target_age"] == 43
    assert fresh.session_state["date_input_key"] == "1982-11-19"
    calc = [df.value for df in fresh.main.dataframe if "Quantity" in df.value.columns]
    assert calc, "no Calculation table"
    ut = calc[0][calc[0]["Quantity"].str.startswith("Universal time")].iloc[0]["Value"]
    assert "1982-11-19 16:44:00" in str(ut), ut
    assert not fresh.sidebar.warning, "a chart saved with its standard must not be flagged"


def test_a_legacy_entry_without_a_standard_is_flagged_on_load(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    path = _saved_charts_path()
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"Old": {"date_string": "1982-11-19", "time_string": "11:44:00",
                                        "location_query": "Petoskey, MI (US)",
                                        "lat": PETOSKEY[0], "lon": PETOSKEY[1]}}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Old").run()
    assert_no_exception(at, "legacy load")
    assert any("saved before the time standard" in w.value for w in at.sidebar.warning)
