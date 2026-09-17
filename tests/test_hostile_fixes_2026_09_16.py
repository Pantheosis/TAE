"""The fixes for the hostile pass of 2026-09-16 -- what its own
reproductions do not reach.

tests/test_hostile_pass_2026_09_16.py asserts that the shell survives each
of the five High findings; those tests were written as strict xfails and
are plain tests now that it does. This file pins the rest of the behaviour
the fixes were asked for, which "no exception" does not describe: the upper
bound the Age box grew, the boundary the timing bundle is kept inside, the
presentation chosen for a record that cannot be loaded (and the launch that
now survives one), each preference key falling to its default rather than
crashing the open, the name the picker reserves for itself, and the one
Timing control that did not survive navigation.

The prose account is docs/HOSTILE_FIXES_2026-09-16.md.
"""
import json
import os
from pathlib import Path

import pytest
from streamlit.util import calc_hash

import engine
from conftest import (APP_PATH, assert_no_exception, find_page_widget, make_app,
                      sync_engine_to_environment)

PETOSKEY = {"date_string": "1982-11-19", "time_string": "11:44:00",
            "time_standard": "Standard time (pytz)", "utc_offset": None,
            "location_query": "Petoskey, MI (US)", "lat": 45.37334, "lon": -84.95533,
            "target_mode": "Date", "target_date": "2026-09-15", "target_age": 43}


def _data_dir():
    d = Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _saved_path():
    return _data_dir() / "saved_charts.json"


def _prefs_path():
    return _data_dir() / "preferences.json"


def _fresh_launch(page="chart"):
    """An AppTest that seeds nothing, so the launch autoload and the
    preferences read run as they do for someone opening the app."""
    from streamlit.testing.v1 import AppTest
    sync_engine_to_environment()
    at = AppTest.from_file(str(APP_PATH), default_timeout=90)
    at._page_hash = calc_hash(page)
    return at


def _state(at, key, default=None):
    """session_state.get, which AppTest's session_state does not carry."""
    try:
        return at.session_state[key]
    except KeyError:
        return default


def _picked(at):
    return at.sidebar.selectbox(key="chart_picker").value


def _save_as(at, name):
    [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0].set_value(name).run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    return at


# --- H1/H2: the span, and the two boxes that can leave it -------------------

def test_the_span_is_the_one_the_ephemeris_answers_to():
    """The constants are measured, not assumed: swe.calc_ut answers from
    625000.5 and raises at 2818000.5, and the app's own last moment leaves
    the forward searches their room below that -- 950 days, the Timing
    page's 900-day Saturn horizon and a little."""
    import swisseph as swe
    swe.calc_ut(625000.5, swe.SUN)                       # the first moment answered
    with pytest.raises(swe.Error):
        swe.calc_ut(2818000.5, swe.SUN)
    with pytest.raises(swe.Error):
        swe.calc_ut(625000.5 - 1.0, swe.SUN)
    from conftest import ui_source
    src = ui_source()
    assert "EPHEMERIS_JD_MIN = 625000.5" in src and "EPHEMERIS_JD_MAX = 2818000.5" in src
    assert "EPHEMERIS_SEARCH_DAYS = 950.0" in src


def test_the_last_date_the_app_covers_casts_and_the_next_one_does_not(tmp_path, monkeypatch):
    """Where the refusal falls, measured: 3000-09-20 is the last date with
    a search's room above it, and it casts on every page that reads the
    chart. The day after it is refused."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    for page in ("chart", "timing", "configurations"):
        at = make_app(date="3000-09-20", page=page).run()
        assert_no_exception(at, f"the last date covered, on {page}")
        assert not [e for e in at.sidebar.error if "ephemeris" in e.value]
    refused = make_app(date="3000-09-21", page="chart").run()
    assert_no_exception(refused, "the day after the last date covered")
    assert [e for e in refused.sidebar.error if "ephemeris" in e.value]


@pytest.mark.parametrize("date,expected_max", [("1240-05-23", 1760), ("1982-11-19", 1017)])
def test_the_age_box_stops_at_the_ephemeris(tmp_path, monkeypatch, date, expected_max):
    """H2: the Age box had no upper bound at all, so the limit could be
    crossed by counting years instead of typing a date. The bound is this
    chart's own -- the birth year's distance from the last year the app
    covers -- and the age AT that bound still casts."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date=date, page="timing")
    at.session_state["_target_mode"] = "Age"
    at.run()
    box = find_page_widget(at, "number_input", "Age (completed years)")
    assert box.min == 0 and box.max == expected_max

    # The age at the bound is one the app can still analyse whole.
    box.set_value(expected_max).run()
    assert_no_exception(at, f"the greatest age the {date} chart offers")
    assert not [e for e in at.main.error if "beyond this app's ephemeris" in e.value]
    assert at.session_state["_target_date"].startswith(str(int(date[:4]) + expected_max))

    # One year further is out of reach -- reachable only from a store the
    # box no longer offers, which is where a saved record's age arrives.
    beyond = make_app(date=date, page="timing")
    beyond.session_state["_target_mode"] = "Age"
    beyond.session_state["_target_age"] = expected_max + 1
    beyond.run()
    assert_no_exception(beyond, f"one age past the bound on the {date} chart")
    assert [e for e in beyond.main.error if "beyond this app's ephemeris (3000 AD)" in e.value]


def test_a_target_past_the_span_keeps_the_last_valid_one(tmp_path, monkeypatch):
    """The bundle boundary: a birth in 2990 with age 20 lands in 3010,
    which the ephemeris cannot reach -- and the bundle reaches a year
    further still, for the revolution that closes the year. The last valid
    target stands, as it does for a target that will not parse (F17), and
    the target's own row says so."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    near = make_app(date="2990-06-01", page="timing")
    near.session_state["_target_mode"] = "Age"
    near.session_state["_target_age"] = 5
    near.run()
    assert_no_exception(near, "a 2990 birth at age 5")
    assert near.session_state["_target_date"].startswith("2995-")
    assert not [e for e in near.main.error if "ephemeris" in e.value]

    # 20 comes from a store the Age box no longer offers -- a record saved
    # with it, or a session that carried it over -- since the box itself
    # stops at 10 for this chart.
    assert find_page_widget(near, "number_input", "Age (completed years)").max == 10
    at = make_app(date="2990-06-01", page="timing")
    at.session_state["_target_mode"] = "Age"
    at.session_state["_target_age"] = 20
    at.run()
    assert_no_exception(at, "a 2990 birth at age 20")
    kept = at.session_state["_target_date"]
    assert not kept.startswith("3010-"), kept
    assert [e for e in at.main.error
            if e.value == f"The target is beyond this app's ephemeris (3000 AD); keeping {kept}."]


def test_a_date_past_the_span_says_so_once_and_keeps_the_shell(tmp_path, monkeypatch):
    """H1's own sentence, in the sidebar, and no second complaint on the
    page: the pages show the recovery panel, which prints it."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="3100-06-01", page="chart").run()
    assert_no_exception(at, "birth year 3100")
    sentence = "This app's ephemeris covers 3000 BC to 3000 AD; the date is outside it."
    assert [e for e in at.sidebar.error if e.value == sentence]
    assert [e for e in at.main.error if e.value == sentence]
    assert len(at.main.dataframe) == 0
    # The last year the app covers still casts, so the limit is where it says.
    ok = make_app(date="3000-09-20", page="chart").run()
    assert_no_exception(ok, "the last date covered")
    assert not [e for e in ok.sidebar.error if "ephemeris" in e.value]


# --- H3: a record the sidebar cannot load ----------------------------------
# The presentation chosen: the record keeps its own name in the picker, the
# load is refused, the form is left exactly as it was, and the sidebar says
# in one sentence which field it could not read.

def test_an_unloadable_record_is_refused_with_a_sentence_and_the_form_stands(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    entry = {**PETOSKEY, "time_string": 1144}
    _saved_path().write_text(json.dumps({"Rec": entry}))
    at = make_app(page="chart").run()
    assert "Rec" in at.sidebar.selectbox(key="chart_picker").options
    at.sidebar.selectbox(key="chart_picker").select("Rec").run()
    assert_no_exception(at, "selecting an unreadable record")
    assert [w for w in at.sidebar.warning
            if w.value == "'Rec' could not be loaded: its time is not a time of day as HH:MM:SS."]
    # The form is as it was, and the chart it was showing is still cast.
    assert at.session_state["date_input_key"] == "1240-05-23"
    assert len(at.main.dataframe) > 0
    # Nothing is written down: the record is in the file exactly as it was.
    assert json.loads(_saved_path().read_text()) == {"Rec": entry}
    # And it is not called "modified" -- the fields never held it.
    assert not [c for c in at.sidebar.caption if "Edited since" in c.value]
    # Nor does it name the chart on the screen, which is not it (seen in
    # the browser, 2026-09-16: the strip read "Type wrong" over the chart
    # the boxes were still holding).
    strip = next((c.value for c in at.main.caption if " · " in c.value), "")
    assert strip.startswith("Unsaved chart"), strip


@pytest.mark.parametrize("field,value,said", [
    ("date_string", 19821119, "its date is not a date, written down as text"),
    ("time_string", "11:44", "its time is not a time of day as HH:MM:SS"),
    ("lat", "forty-five", "its latitude is not a number between -90 and 90"),
    ("lon", 999.0, "its longitude is not a number between -180 and 180"),
    ("utc_offset", "abc", "its UTC offset is not a number of hours"),
    ("location_query", 5, "its place is not a place, written down as text"),
    ("target_age", "abc", "its target age is not a whole number of years, zero or more"),
])
def test_each_field_names_itself_when_it_cannot_be_read(tmp_path, monkeypatch, field, value, said):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    _saved_path().write_text(json.dumps({"Rec": {**PETOSKEY, field: value}}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Rec").run()
    assert_no_exception(at, f"a record whose {field} is {value!r}")
    assert [w for w in at.sidebar.warning if w.value == f"'Rec' could not be loaded: {said}."]


def test_a_record_missing_a_field_still_loads(tmp_path, monkeypatch):
    """The check is of the fields a record HAS: one written before a field
    existed, or with a null in it, is not a fault."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    legacy = {"date_string": "1982-11-19", "time_string": "11:44:00",
              "location_query": "Petoskey, MI (US)", "lat": 45.37334, "lon": -84.95533,
              "utc_offset": None}
    _saved_path().write_text(json.dumps({"Legacy": legacy}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Legacy").run()
    assert_no_exception(at, "a record written before the time standard was stored")
    assert at.session_state["date_input_key"] == "1982-11-19"
    assert not at.sidebar.warning or not [w for w in at.sidebar.warning if "could not be loaded" in w.value]


def test_the_launch_survives_an_unloadable_last_chart(tmp_path, monkeypatch):
    """Dead-on-open was the worst of it: a corrupt last_chart is autoloaded
    at launch, so the app opened on a traceback with no page reachable.
    Now it opens on no chart loaded, with the sentence beside the picker."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    _saved_path().write_text(json.dumps({"Rec": {**PETOSKEY, "time_string": 1144}}))
    _prefs_path().write_text(json.dumps({"last_chart": "Rec"}))
    at = _fresh_launch("chart").run()
    assert_no_exception(at, "a launch whose last chart cannot be read")
    assert _picked(at) == "-- New Chart --"
    assert [w for w in at.sidebar.warning if "'Rec' could not be loaded" in w.value]
    assert at.session_state["date_input_key"] == "1240-05-23"
    assert len(at.main.header) == 1


# --- H5: an offset outside the bounds a chart can be cast at ---------------

def test_an_out_of_range_offset_is_reported_not_written_to_the_widget(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    entry = {**PETOSKEY, "time_standard": "Manual UTC offset", "utc_offset": 99}
    _saved_path().write_text(json.dumps({"Rec": entry}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Rec").run()
    assert_no_exception(at, "a record with an offset of 99")
    assert [w for w in at.sidebar.warning
            if w.value == "'Rec' was saved with a UTC offset of 99, outside ±14; "
                          "check the time standard."]
    # The rest of the record loaded; the offset did not, and was not clamped.
    assert at.session_state["date_input_key"] == "1982-11-19"
    assert at.session_state["utc_offset_key"] == 0.0
    assert json.loads(_saved_path().read_text())["Rec"]["utc_offset"] == 99
    # The difference is what the strip shows.
    assert [c for c in at.sidebar.caption if "Edited since it was saved" in c.value]

    # And a re-save writes what the box holds, not the clamp.
    _save_as(at, "Rec")
    [b for b in at.sidebar.button if b.label == "Replace"][0].click().run()
    assert json.loads(_saved_path().read_text())["Rec"]["utc_offset"] == 0.0


def test_an_offset_inside_the_bounds_still_loads(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    _saved_path().write_text(json.dumps(
        {"Rec": {**PETOSKEY, "time_standard": "Manual UTC offset", "utc_offset": -5.5}}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Rec").run()
    assert_no_exception(at, "a record with an offset of -5.5")
    assert at.session_state["utc_offset_key"] == -5.5
    assert not [w for w in at.sidebar.warning if "UTC offset" in w.value]


# --- H4: a preferences file the app did not write --------------------------

def _valid_preference(key):
    if key == '_launches':
        return 3
    if key == 'last_chart':
        return "Rec"
    if key == 'home_place':
        return {"label": "Florence, 16 (IT)", "lat": 43.7792, "lon": 11.2463}
    if key in engine.PREFERENCE_BOOL_KEYS:
        return True
    return engine._preference_option_tuples()[key][-1]


def _invalid_preference(key):
    if key == '_launches':
        return "many"
    if key == 'last_chart':
        return ["a"]
    if key == 'home_place':
        return {"label": "Florence, 16 (IT)", "lat": 91.0, "lon": 11.2463}
    if key in engine.PREFERENCE_BOOL_KEYS:
        return "yes"
    return "no such option"


PREFERENCE_NAMES = engine.PREFERENCE_KEYS + ('last_chart',)


def test_every_preference_key_is_covered_by_a_rule(engine):
    """A preference added without a rule would be dropped on every read --
    silently, which is how the file is meant to behave, so nothing would
    say the reading no longer persists. It is a rule per key or nothing."""
    for key in engine["PREFERENCE_KEYS"] + ('last_chart',):
        assert engine["preference_is_valid"](key, _valid_preference(key)), key
        assert not engine["preference_is_valid"](key, _invalid_preference(key)), key


@pytest.mark.parametrize("key", PREFERENCE_NAMES)
def test_an_invalid_preference_falls_to_its_default(tmp_path, monkeypatch, key):
    """Read through load_preferences itself: the invalid entry is gone and
    every other entry in the file stands. The file is not rewritten here --
    nothing is written until the next reading is set."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    whole = {k: _valid_preference(k) for k in PREFERENCE_NAMES}
    corrupt = {**whole, key: _invalid_preference(key)}
    _prefs_path().write_text(json.dumps(corrupt))
    before = _prefs_path().read_bytes()
    sync_engine_to_environment()
    loaded = engine.load_preferences()
    assert key not in loaded, f"{key}={corrupt[key]!r} should have been dropped"
    assert loaded == {k: v for k, v in whole.items() if k != key}
    assert _prefs_path().read_bytes() == before


def test_a_whole_valid_file_survives_the_check(tmp_path, monkeypatch):
    """The other half of the rule: nothing valid is thrown away."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    whole = {k: _valid_preference(k) for k in PREFERENCE_NAMES}
    _prefs_path().write_text(json.dumps(whole))
    sync_engine_to_environment()
    assert engine.load_preferences() == whole


@pytest.mark.parametrize("corrupt", [
    {"_launches": "many"},
    {"_launches": -3},
    {"last_chart": ["a"]},
    {"_chart_bounds": "yes"},
    {"_wheel_layout": "Sideways"},
    {"_target_mode": "Whenever"},
    {"_connection_rule": 7},
    {"_reading_depth": "Everything at once"},
])
def test_a_corrupt_preferences_file_opens_on_the_defaults(tmp_path, monkeypatch, corrupt):
    """And through a whole run, which is where it used to raise: the launch
    block does int() on _launches and indexes the saved charts by
    last_chart."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    _saved_path().write_text(json.dumps({"Rec": PETOSKEY}))
    _prefs_path().write_text(json.dumps(corrupt))
    at = _fresh_launch("chart").run()
    assert_no_exception(at, f"a launch with preferences {corrupt}")
    assert len(at.main.header) == 1
    for key, value in corrupt.items():
        if key == 'last_chart':
            assert _picked(at) == "-- New Chart --"
        else:
            assert _state(at, key) != value
    # The launch counter is the one legitimate write the open makes, and it
    # is an int whatever the file held.
    assert isinstance(json.loads(_prefs_path().read_text())["_launches"], int)


# --- M3: the name the picker keeps for itself ------------------------------

@pytest.mark.parametrize("name", ["-- New Chart --", "--new chart--", "  -- NEW  CHART --  "])
def test_the_pickers_own_option_is_a_reserved_chart_name(tmp_path, monkeypatch, name):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(page="chart").run()
    _save_as(at, name)
    assert_no_exception(at, f"saving under {name!r}")
    assert [e for e in at.sidebar.error if e.value == "That name is reserved; choose another."]
    assert not _saved_path().exists() or json.loads(_saved_path().read_text()) == {}
    # The picker still has one of it, and it still means "new chart".
    options = at.sidebar.selectbox(key="chart_picker").options
    assert options.count("-- New Chart --") == 1 and len(options) == 1


def test_a_name_that_merely_resembles_it_still_saves(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(page="chart").run()
    _save_as(at, "-- New Chart 2 --")
    assert_no_exception(at, "a name that is not the sentinel")
    assert "-- New Chart 2 --" in json.loads(_saved_path().read_text())


# --- M4: the one Days and months control that did not survive navigation ---
# (the small days were a tab of the Timing page until 2026-09-17)

def test_the_day_point_choice_survives_navigation(tmp_path, monkeypatch):
    """A plain widget key is dropped by Streamlit when the page is not
    rendered; through the store it stands, as every other page control on
    the page does."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1982-11-19", page="days").run()
    box = find_page_widget(at, "selectbox", "Also direct, for the small days")
    other = [o for o in box.options if o.endswith("Sun")][0]
    box.set_value(other).run()
    assert at.session_state["_pn4_day_point"] == other
    assert any(f"Small days from {other[len('the revolution'+chr(39)+'s '):]}" in m.value
               or other.split("'s ")[-1] in m.value for m in at.main.markdown)

    at._page_hash = calc_hash("chart"); at.run()
    at._page_hash = calc_hash("days"); at.run()
    assert_no_exception(at, "back on the Days and months page")
    assert find_page_widget(at, "selectbox", "Also direct, for the small days").value == other


def test_the_day_point_is_not_written_to_the_preferences_file(tmp_path, monkeypatch):
    """It survives navigation, not the run: it is a store key, not a
    preference, and whether it should be remembered between runs is the
    owner's call, not this branch's."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    at = make_app(date="1982-11-19", page="days").run()
    box = find_page_widget(at, "selectbox", "Also direct, for the small days")
    box.set_value([o for o in box.options if o.endswith("Sun")][0]).run()
    assert_no_exception(at, "choosing a day point")
    assert '_pn4_day_point' not in engine.PREFERENCE_KEYS
    assert '_pn4_day_point' not in json.loads(_prefs_path().read_text())
