"""The four Prediction pages (branch N of UI_READABILITY_PLAN_2026-09-17_rev2.md
§4): Timing, The releaser, Days and months, Fardar and ages.

Until 2026-09-17 the Timing page rendered six client-side tabs; three of
them are pages of their own now, and the block that sets the year under
examination -- the mode radio, the age or date box, the read-back line --
renders at the head of all four through one helper, with the widget keys
it always had. Streamlit drops the state of a widget that is not rendered
on a run, so what carries the target across the Nativity pages is the
_target_* store keys the bundle reads at the top level: that is the carry
test below, Timing -> Chart -> The releaser.
"""
import json
import os
from pathlib import Path

import pytest
from streamlit.util import calc_hash

from conftest import READING_DEPTHS, assert_no_exception, make_app


def _read_back(at):
    """The year block's read-back line, and nothing else that says
    "completed" (the Timing page's turning caption does too)."""
    return [m.value for m in at.main.markdown
            if "completed" in m.value and "The revolution of the year fell on" in m.value]

PREDICTION_PAGES = {
    "timing": "Timing",
    "releaser": "The releaser",
    "days": "Days and months",
    "fardar": "Fardar and ages",
}
YEAR_HEADING = "The year under examination"


# --- (a) every Prediction page renders at every reading depth --------------

@pytest.mark.parametrize("view", READING_DEPTHS)
@pytest.mark.parametrize("page", list(PREDICTION_PAGES))
def test_every_prediction_page_renders_at_every_depth(page, view):
    at = make_app(page=page, view=view).run()
    assert_no_exception(at, f"{page} under {view}")
    assert [h.value for h in at.main.header] == [PREDICTION_PAGES[page]]
    assert len(at.main.dataframe) > 0, f"{page}: no table rendered"


# --- (b) the age set on Timing survives Chart and reaches The releaser -----

def test_the_age_set_on_timing_carries_through_chart_to_the_releaser():
    at = make_app(page="timing")
    at.session_state["_target_mode"] = "Age"
    at.run()
    assert_no_exception(at, "timing")
    at.number_input(key="target_age").set_value(30).run()
    assert_no_exception(at, "timing, age 30")
    assert at.session_state["_target_age"] == 30
    assert at.number_input(key="target_age").value == 30

    # A Nativity page: the widget is not rendered, so Streamlit drops its
    # key; the store key is what must hold the age.
    at._page_hash = calc_hash("chart")
    at.run()
    assert_no_exception(at, "chart, after setting the age on timing")
    assert not at.main.number_input, "the Chart page draws no age box"
    assert at.session_state["_target_age"] == 30

    at._page_hash = calc_hash("releaser")
    at.run()
    assert_no_exception(at, "releaser, after chart")
    assert at.number_input(key="target_age").value == 30
    read_back = _read_back(at)
    assert len(read_back) == 1, read_back
    assert "age **30** completed" in read_back[0], read_back[0]
    assert "the 30th birthday opens this year" in read_back[0], read_back[0]


def test_the_age_survives_a_direct_hop_between_two_prediction_pages():
    """The harder case, which the Chart hop above does not exercise. On a
    page switch Streamlit gives the same key a new element id (the id
    carries the page's hash), so the value left by the other page's widget
    is found under the user key only and does not reach the new widget by
    itself: it would take its default, 0, and _persist would carry 0 into
    the store. _carry() writes the key back to itself before the widget is
    created, so the new element adopts it on every page."""
    at = make_app(page="timing")
    at.session_state["_target_mode"] = "Age"
    at.run()
    at.number_input(key="target_age").set_value(30).run()
    assert_no_exception(at, "timing, age 30")
    for page in ("releaser", "days", "fardar", "timing"):
        at._page_hash = calc_hash(page)
        at.run()
        assert_no_exception(at, f"{page}, a direct hop")
        assert not at.exception and not at.main.warning, page
        assert at.radio(key="target_mode").value == "Age", page
        assert at.number_input(key="target_age").value == 30, page
        assert at.session_state["_target_age"] == 30, page
        assert at.session_state["_target_mode"] == "Age", page
        read_back = _read_back(at)
        assert len(read_back) == 1 and "age **30** completed" in read_back[0], (page, read_back)
    # A change on the page it was carried to is still a change.
    at.number_input(key="target_age").set_value(31).run()
    assert_no_exception(at, "timing, age 31")
    assert at.number_input(key="target_age").value == 31
    assert at.session_state["_target_age"] == 31


def test_a_loaded_records_target_does_not_come_back_after_a_nativity_page(tmp_path, monkeypatch):
    """Found in the browser on the clone, with the owner's saved chart, and
    on main before this branch. The saved-chart loader used to write the
    widget keys (target_age and the rest) as plain session values on a run
    where the year block is not rendered -- the app opens on Chart -- and
    Streamlit's state compaction never refreshes a plain value under a key
    that later maps to a widget (SessionState._keys converts the key to the
    element id first): the record's age stayed in _old_state under the bare
    key, and came back as the widget's value whenever the widget went stale
    on a Nativity page. The loader writes the store keys only now and drops
    the widget keys; the year block seeds its widgets from the store."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    folder = Path(tmp_path) / "TraditionalAstrologyEngine"
    folder.mkdir(parents=True)
    (folder / "saved_charts.json").write_text(json.dumps({"Loaded 1240": {
        "date_string": "1240-05-23", "time_string": "14:30:00", "time_standard": "LMT (Local Mean Time)",
        "utc_offset": None, "location_query": "Florence, Italy", "lat": 43.7792, "lon": 11.2463,
        "target_mode": "Age", "target_date": "1283-05-23", "target_age": 43}}))
    at = make_app(page="chart").run()
    at.sidebar.selectbox(key="chart_picker").select("Loaded 1240").run()
    assert_no_exception(at, "chart, record loaded")
    assert at.session_state["_target_age"] == 43
    assert at.session_state["_target_mode"] == "Age"

    at._page_hash = calc_hash("timing")
    at.run()
    assert_no_exception(at, "timing, record loaded")
    assert at.number_input(key="target_age").value == 43, "the record's target, seeded from the store"
    at.number_input(key="target_age").set_value(30).run()
    assert_no_exception(at, "timing, age 30")
    assert at.session_state["_target_age"] == 30

    at._page_hash = calc_hash("chart")
    at.run()
    assert_no_exception(at, "chart, after the change")
    at._page_hash = calc_hash("releaser")
    at.run()
    assert_no_exception(at, "releaser, after chart")
    assert at.number_input(key="target_age").value == 30, "the record's 43 must not come back"
    assert at.session_state["_target_age"] == 30
    read_back = _read_back(at)
    assert len(read_back) == 1 and "age **30** completed" in read_back[0], read_back


def test_a_date_target_set_on_days_reaches_fardar_and_timing_the_same_way():
    at = make_app(page="days")
    at.session_state["_target_mode"] = "Date"
    at.run()
    assert_no_exception(at, "days")
    at.text_input(key="target_date").set_value("1282-05-23").run()
    assert_no_exception(at, "days, a date target")
    assert at.session_state["_target_date"] == "1282-05-23"
    # Through a Nativity page (the key is dropped) and then two direct
    # hops (the key is carried under a new element id).
    for page in ("findings", "fardar", "timing"):
        at._page_hash = calc_hash(page)
        at.run()
        assert_no_exception(at, f"{page} after the date target")
        assert at.session_state["_target_date"] == "1282-05-23", page
    assert at.text_input(key="target_date").value == "1282-05-23"
    read_back = _read_back(at)
    assert len(read_back) == 1 and "**1282-05-23**" in read_back[0], read_back
    # Switching the mode on the page it was carried to reads the date's
    # completed years into the age box.
    at.radio(key="target_mode").set_value("Age").run()
    assert_no_exception(at, "timing, mode switched")
    assert at.number_input(key="target_age").value == 42
    assert at.session_state["_target_age"] == 42


# --- (c) the year block stands once on each of the four pages --------------

@pytest.mark.parametrize("page", list(PREDICTION_PAGES))
def test_the_year_block_renders_once_on_each_prediction_page(page):
    at = make_app(page=page).run()
    assert_no_exception(at, page)
    headings = [s.value for s in at.main.subheader]
    assert headings.count(YEAR_HEADING) == 1, headings
    assert headings[0] == YEAR_HEADING, "the year block opens the page's body"
    assert [r.key for r in at.main.radio if r.key == "target_mode"] == ["target_mode"]
    assert len(_read_back(at)) == 1


@pytest.mark.parametrize("page", ["chart", "findings", "reference", "sources"])
def test_no_other_page_draws_the_year_block(page):
    at = make_app(page=page).run()
    assert_no_exception(at, page)
    assert YEAR_HEADING not in [s.value for s in at.main.subheader]
    assert not [r for r in at.main.radio if r.key == "target_mode"]
