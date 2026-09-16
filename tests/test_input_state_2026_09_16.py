"""The input state of 2026-09-16: a draft, a committed nativity, and a shell
that outlives an invalid draft.

Four findings of the independent UI review of 2026-09-16 (F01, F02, F05,
F17), pinned by the review's own reproductions E01, E02, E03, E07 and E15.

What it pins:

* F01 -- the chart strip, the calculation and a saved record all read the
  COMMITTED date, never the characters in the box; an invalid draft cannot
  be saved and says so; a chart that has not moved says that too.
* F02 -- switching the coordinate fields on keeps the place that is
  resolved; an impossible latitude is refused once, before any time
  standard, instead of giving tables under one and an exception under
  another.
* F05 -- the header bar, the reference tables and the sources survive every
  invalid input; the pages that read a chart show a recovery panel; and the
  page functions are main's own, dedented out of `if tz_name:` (proved
  against main's AST, one guard line apart).
* F17 -- an unparseable target keeps the last valid target and never
  substitutes today.
"""
import ast
import copy
import json
import os
import subprocess
from datetime import date, time
from pathlib import Path

import pytest

from conftest import EXECUTABLE_DIR, assert_no_exception, make_app

NEW_YORK = (40.71427, -74.00597)
FLORENCE = (43.7792, 11.2463)
RANGE_MESSAGE = "Latitude must be between -90 and 90 and longitude between -180 and 180."
TIME_STANDARDS = ["LMT (Local Mean Time)", "Standard time (pytz)", "Manual UTC offset"]


def _saved_charts_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "saved_charts.json"


def _strip(at):
    """The chart strip: the first caption of the page, two lines joined by a
    hard break, the nativity on the first."""
    for caption in at.main.caption:
        if " · " in caption.value:
            return caption.value
    return ""


def _save_as(at, name):
    box = [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0]
    box.set_value(name).run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    return at


# --- E01 / F01: the committed date is the only date -------------------------

def test_an_invalid_draft_shows_the_last_valid_chart_and_saves_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="configurations").run()
    assert_no_exception(at, "the valid run")
    assert "1983-11-19 14:30:00" in _strip(at)

    at.sidebar.text_input(key="date_input_key").set_value("not-a-date").run()
    assert_no_exception(at, "the invalid draft")
    # (a) the strip carries the committed date, not the draft.
    assert "1983-11-19 14:30:00" in _strip(at), _strip(at)
    assert "not-a-date" not in _strip(at)
    # (d) and one line under it says the results have not moved.
    assert any(w.value == "Results have not updated. Showing the last valid chart: "
                          "1983-11-19 14:30:00." for w in at.main.warning), \
        [w.value for w in at.main.warning]
    assert any("Showing 1983-11-19" in e.value for e in at.sidebar.error)

    # (c) Save refuses, and writes nothing at all.
    before = at.session_state["saved_charts"].copy()
    _save_as(at, "Refused by the date")
    assert_no_exception(at, "save with an invalid date")
    assert at.session_state["saved_charts"] == before
    assert not _saved_charts_path().exists()
    assert any(e.value == "The date is not valid; nothing was saved." for e in at.sidebar.error)


def test_an_unresolved_place_cannot_be_saved(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(page="chart")
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = "zzzz-no-such-city"
    at.run()
    _save_as(at, "Refused by the place")
    assert_no_exception(at, "save with no place")
    assert at.session_state["saved_charts"] == {}
    assert not _saved_charts_path().exists()
    assert any(e.value == "No place is resolved; nothing was saved." for e in at.sidebar.error)


def test_a_saved_record_holds_the_committed_date_and_reloads_as_itself(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Committed 1983")
    assert_no_exception(at, "save")
    entry = json.loads(_saved_charts_path().read_text())["Committed 1983"]
    # (b) the committed date in ISO, whatever the box held.
    assert entry["date_string"] == "1983-11-19"

    fresh = make_app(page="chart").run()
    fresh.sidebar.selectbox(key="chart_picker").select("Committed 1983").run()
    assert_no_exception(fresh, "load in a fresh session")
    assert fresh.session_state["date_input_key"] == "1983-11-19"
    assert "1983-11-19" in _strip(fresh), _strip(fresh)
    calculation = [df.value for df in fresh.main.dataframe if "Quantity" in df.value.columns][0]
    universal = calculation[calculation["Quantity"].str.startswith("Universal time")].iloc[0]["Value"]
    assert "1983-11-19" in str(universal), universal


def test_a_record_saved_with_a_malformed_date_loads_without_crashing(tmp_path, monkeypatch):
    """A record written by a version that saved the raw draft (the state the
    review found). It loads as the sidebar loads malformed text: the last
    good date, and the box's own error."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    path = _saved_charts_path()
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"Old and broken": {
        "date_string": "not-a-date", "time_string": "14:30:00",
        "time_standard": "LMT (Local Mean Time)",
        "location_query": "Manual [43.7792, 11.2463]",
        "lat": FLORENCE[0], "lon": FLORENCE[1]}}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Old and broken").run()
    assert_no_exception(at, "loading a malformed record")
    assert any("Date must be YYYY-MM-DD" in e.value for e in at.sidebar.error)
    assert len(at.main.header) == 1


# --- E02, E03 / F02: the coordinates -----------------------------------------

def test_switching_the_fields_on_keeps_the_resolved_place():
    """New York by city search, then 'Enter coordinates directly': the
    fields open on New York, not on the Florence constants."""
    at = make_app(page="chart")
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = "New York"
    at.run()
    assert_no_exception(at, "the city search")
    assert at.session_state["_resolved_lat"] == pytest.approx(NEW_YORK[0])
    assert at.session_state["_resolved_lon"] == pytest.approx(NEW_YORK[1])

    at.sidebar.toggle(key="manual_coords_key").set_value(True).run()
    assert_no_exception(at, "the toggle")
    assert at.sidebar.number_input(key="manual_lat_key").value == pytest.approx(NEW_YORK[0])
    assert at.sidebar.number_input(key="manual_lon_key").value == pytest.approx(NEW_YORK[1])
    assert any("40.7143, -74.0060" in s.value for s in at.sidebar.success)


def test_the_harness_seeds_the_fields_and_the_callback_never_fires():
    """The callback runs on a change of the toggle; a seeded session state
    is not a change, so every existing test's Florence stands."""
    at = make_app(page="chart")
    at.session_state["_resolved_lat"], at.session_state["_resolved_lon"] = NEW_YORK
    at.run()
    assert_no_exception(at, "seeded keys")
    assert at.sidebar.number_input(key="manual_lat_key").value == pytest.approx(FLORENCE[0])
    assert at.session_state["_resolved_lat"] == pytest.approx(FLORENCE[0]), \
        "the run records the place it actually used"


@pytest.mark.parametrize("standard", TIME_STANDARDS)
def test_an_impossible_latitude_is_refused_in_every_time_standard(standard):
    at = make_app(page="chart")
    at.session_state["manual_lat_key"] = 91.0
    at.session_state["time_standard_key"] = standard
    at.run()
    assert_no_exception(at, f"latitude 91 under {standard}")
    assert [e.value for e in at.sidebar.error] == [RANGE_MESSAGE]
    assert len(at.main.header) == 1 and at.main.header[0].value == "Chart"
    assert [e.value for e in at.main.error] == [RANGE_MESSAGE]
    assert not at.main.dataframe, "no chart may be computed for an impossible latitude"


@pytest.mark.parametrize("lat, lon", [(90.0, 0.0), (-90.0, 179.9)])
def test_a_polar_but_possible_latitude_still_casts(lat, lon):
    at = make_app(page="chart")
    at.session_state["manual_lat_key"], at.session_state["manual_lon_key"] = lat, lon
    at.run()
    assert_no_exception(at, f"{lat}, {lon}")
    assert not [e for e in at.sidebar.error if e.value == RANGE_MESSAGE]


def test_the_number_inputs_carry_their_own_bounds():
    at = make_app(page="chart").run()
    latitude = at.sidebar.number_input(key="manual_lat_key")
    longitude = at.sidebar.number_input(key="manual_lon_key")
    assert (latitude.min, latitude.max) == (-90.0, 90.0)
    assert (longitude.min, longitude.max) == (-180.0, 180.0)


# --- E07 / F05: the shell survives -------------------------------------------

def _broken(kind, page):
    at = make_app(page=page)
    if kind == "empty location":
        at.session_state["manual_coords_key"] = False
        at.session_state["location_input_key"] = ""
    elif kind == "no such city":
        at.session_state["manual_coords_key"] = False
        at.session_state["location_input_key"] = "zzzz-no-such-city"
    else:
        at.session_state["manual_lat_key"], at.session_state["manual_lon_key"] = NEW_YORK
        at.session_state["time_standard_key"] = "Standard time (pytz)"
        if kind == "ambiguous hour":
            at.session_state["date_input_key"] = "2025-11-02"
            at.session_state["time_input_key"] = time(1, 30)
        else:
            at.session_state["date_input_key"] = "2025-03-09"
            at.session_state["time_input_key"] = time(2, 30)
    return at.run()


BROKEN = ["empty location", "no such city", "ambiguous hour", "non-existent hour"]


@pytest.mark.parametrize("kind", BROKEN)
@pytest.mark.parametrize("page", ["chart", "reference", "sources"])
def test_every_page_keeps_its_header_whatever_the_input(kind, page):
    at = _broken(kind, page)
    assert_no_exception(at, f"{kind} on {page}")
    assert len(at.main.header) == 1


@pytest.mark.parametrize("kind", BROKEN)
def test_the_reference_and_the_sources_render_in_full(kind):
    for page in ("reference", "sources"):
        valid = make_app(page=page).run()
        assert_no_exception(valid, f"the valid {page} run")
        broken = _broken(kind, page)
        assert len(broken.main.dataframe) == len(valid.main.dataframe) > 0, page
        assert not broken.main.error, f"{page} has no chart to complain about"


@pytest.mark.parametrize("kind", BROKEN)
def test_a_chart_page_shows_the_recovery_panel(kind):
    at = _broken(kind, "chart")
    assert at.main.header[0].value == "Chart"
    assert len(at.main.error) == 1 and at.main.error[0].value
    assert any(c.value == "Correct the nativity in the sidebar; the reference tables and the "
                          "sources stay available." for c in at.main.caption)
    assert not at.main.dataframe
    # The strip names a chart; a recovery page has none to name.
    assert _strip(at) == ""


def test_the_dst_refusals_still_state_themselves_in_the_sidebar():
    """The three st.stop() calls became chart_ok/chart_error; the sidebar's
    own box says what it always said."""
    ambiguous = _broken("ambiguous hour", "chart")
    assert any("happens twice in America/New_York" in e.value for e in ambiguous.sidebar.error)
    assert ambiguous.main.error[0].value == [e.value for e in ambiguous.sidebar.error
                                             if "happens twice" in e.value][0]
    missing = _broken("non-existent hour", "chart")
    assert any("does not exist in America/New_York" in e.value for e in missing.sidebar.error)


# --- E15 / F17: the target ---------------------------------------------------

def test_an_invalid_target_keeps_the_last_valid_one():
    at = make_app(page="timing")
    at.session_state["_target_mode"] = "Date"
    at.session_state["_target_date"] = "1282-05-23"
    at.run()
    assert_no_exception(at, "a valid target")
    assert at.main.text_input(key="target_date").value == "1282-05-23"

    at.main.text_input(key="target_date").set_value("invalid").run()
    assert_no_exception(at, "an invalid target")
    assert any(e.value == "Not a YYYY-MM-DD date; keeping 1282-05-23." for e in at.main.error), \
        [e.value for e in at.main.error]
    read_back = [m.value for m in at.main.markdown if "completed" in m.value]
    assert read_back and "**1282-05-23**" in read_back[0], read_back
    today = date.today().isoformat()
    assert not any(f"using {today}" in element.value
                   for element in list(at.main.markdown) + list(at.main.caption))
    assert today not in read_back[0], "today may not stand in for the target"
    assert at.session_state["_target_last_good"] == "1282-05-23"


def test_a_session_that_never_had_a_valid_target_falls_to_today():
    at = make_app(page="timing")
    at.session_state["_target_mode"] = "Date"
    at.session_state["_target_date"] = "invalid"
    at.run()
    assert_no_exception(at, "no valid target ever")
    assert at.session_state["_target_last_good"] == date.today().isoformat()


# --- The dedent, proved against main -----------------------------------------

PAGE_FUNCTIONS = {
    "page_chart": "Chart",
    "page_findings": "Findings",
    "page_dignities": "Dignities and places",
    "page_configurations": "Configurations",
    "page_lots": "Lots",
    "page_victors": "Lunation and victors",
    "page_timing": "Timing",
    "page_sources": None,          # no chart to guard
    "page_reference": None,
}
# page_timing's one deliberate change, F17: the same test, a different box
# and the word "keeping" for "using".
F17_NOW = ast.unparse(ast.parse('st.error(f"Not a YYYY-MM-DD date; keeping {target_date:%Y-%m-%d}.")'))
F17_ON_MAIN = ast.unparse(ast.parse('st.caption(f"Not a YYYY-MM-DD date; using {target_date:%Y-%m-%d}.")'))


def _from_main(path):
    for ref in ("origin/main", "main"):
        try:
            shown = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=EXECUTABLE_DIR,
                                   capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        if shown.returncode == 0 and shown.stdout:
            return shown.stdout
    return None


def _functions(source):
    """Every function called page_* in a file, wherever it is nested."""
    found = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name in PAGE_FUNCTIONS:
            found[node.name] = node
    return found


def _body_text(statements):
    """The statements as code, with docstrings' own whitespace collapsed --
    the two docstrings that carry a continuation line lost eight spaces of
    indentation with the code around them, and a docstring is not
    behaviour."""
    out = []
    for statement in statements:
        node = copy.deepcopy(statement)
        for sub in ast.walk(node):
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and sub.body:
                first = sub.body[0]
                if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    first.value.value = " ".join(first.value.value.split())
        out.append(ast.unparse(node))
    return "\n".join(out)


def test_the_page_functions_are_mains_own_one_guard_line_apart():
    """F05's dedent, proved: every page function's body is the body main
    carries, plus (for the seven that read a chart) the guard line."""
    main_source = _from_main("app.py")
    if main_source is None:
        pytest.skip("main's app.py is not in this checkout (a shallow clone)")
    theirs = _functions(main_source)
    ours = _functions((EXECUTABLE_DIR / "app.py").read_text())
    assert set(ours) == set(theirs) == set(PAGE_FUNCTIONS)
    for name, title in PAGE_FUNCTIONS.items():
        body = list(ours[name].body)
        if title is not None:
            guard = ast.unparse(body.pop(0))
            assert guard == f"if not chart_ok:\n    _recovery_panel({title!r})\n    return", \
                f"{name}: {guard}"
        mine = _body_text(body)
        if name == "page_timing":
            assert mine.count(F17_NOW) == 1
            mine = mine.replace(F17_NOW, F17_ON_MAIN)
        assert mine == _body_text(theirs[name].body), f"{name} is not main's function dedented"
    # And they are top-level functions now, not nested in a calculation.
    module = ast.parse((EXECUTABLE_DIR / "app.py").read_text())
    top_level = {node.name for node in module.body if isinstance(node, ast.FunctionDef)}
    assert set(PAGE_FUNCTIONS) <= top_level
    assert any(isinstance(node, ast.Expr) and "st.navigation" in ast.unparse(node)
               for node in module.body), "the navigation must be reached on every run"


def test_the_table_fixture_is_the_one_main_carries():
    shown = _from_main("tests/fixtures/tables.json")
    if shown is None:
        pytest.skip("main's fixture is not in this checkout (a shallow clone)")
    assert json.loads(shown) == json.loads(
        (EXECUTABLE_DIR / "tests" / "fixtures" / "tables.json").read_text())
