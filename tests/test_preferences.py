"""Preferences across runs (2026-09-10, UI_REVIEW_2026-09-10.md §2).

The readings and display choices live in preferences.json beside the
saved charts, written through _persist() and read once per session into
the store keys. Under the harness the file is switched off
(ALMUTEN_NO_PREFERENCES=1 in conftest), so these tests switch it back on
against a tmp_path and prove: a reading set on its page is on disk and in
force in a fresh session; the last chart loaded is the chart a fresh
session opens on; the Sources page lists the readings in force and its
reset returns them to the course defaults; and, with the guard set,
nothing is ever written.
"""
import json
import os
from datetime import time
from pathlib import Path

import pytest

from conftest import APP_PATH, assert_no_exception, find_page_widget, make_app

PETOSKEY = (45.37334, -84.95533)


def _prefs_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "preferences.json"


@pytest.fixture
def prefs_on(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    return tmp_path


def test_nothing_is_written_under_the_harness_guard(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(page="configurations").run()
    find_page_widget(at, "radio", "Connection test").set_value("Abu Ma'shar").run()
    assert at.session_state["_connection_rule"] == "Abu Ma'shar"
    assert not _prefs_path().exists()


def test_a_reading_set_on_its_page_is_on_disk_and_in_force_next_session(prefs_on):
    at = make_app(page="configurations").run()
    find_page_widget(at, "radio", "Connection test").set_value("Abu Ma'shar").run()
    assert_no_exception(at, "set the rule")
    on_disk = json.loads(_prefs_path().read_text())
    assert on_disk["_connection_rule"] == "Abu Ma'shar"

    fresh = make_app(page="configurations").run()
    assert_no_exception(fresh, "fresh session")
    assert find_page_widget(fresh, "radio", "Connection test").value == "Abu Ma'shar"
    assert any("Abu Ma'shar rule in force" in c.value for c in fresh.main.caption)
    # And the page says so under its header.
    assert any("differ from the course defaults" in c.value for c in fresh.main.caption)


def test_a_seeded_store_wins_over_the_file(prefs_on):
    _prefs_path().parent.mkdir(parents=True)
    _prefs_path().write_text(json.dumps({"_connection_rule": "Abu Ma'shar", "unknown_key": 1, "_wheel_layout": "Wide"}))
    at = make_app(page="configurations", switches={"connection": "Sahl"}).run()
    assert find_page_widget(at, "radio", "Connection test").value == "Sahl"
    assert at.session_state["_wheel_layout"] == "Wide"
    assert "unknown_key" not in at.session_state


def test_the_last_chart_loaded_is_the_chart_a_fresh_session_opens_on(prefs_on):
    from streamlit.testing.v1 import AppTest
    from streamlit.util import calc_hash
    at = make_app(date="1982-11-19", page="chart")
    at.session_state["manual_lat_key"], at.session_state["manual_lon_key"] = PETOSKEY
    at.session_state["time_input_key"] = time(11, 44)
    at.session_state["time_standard_key"] = "Standard time (pytz)"
    at.run()
    [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0].set_value("Ref").run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    assert json.loads(_prefs_path().read_text())["last_chart"] == "Ref"

    # A session that seeds nothing, as a person opening the app seeds nothing.
    fresh = AppTest.from_file(str(APP_PATH), default_timeout=60)
    fresh._page_hash = calc_hash("chart")
    fresh.run()
    assert_no_exception(fresh, "fresh session")
    assert fresh.session_state["chart_picker"] == "Ref"
    assert fresh.session_state["date_input_key"] == "1982-11-19"
    assert fresh.session_state["time_standard_key"] == "Standard time (pytz)"
    calc = [df.value for df in fresh.main.dataframe if "Quantity" in df.value.columns][0]
    assert "1982-11-19 16:44:00" in str(calc[calc["Quantity"].str.startswith("Universal time")].iloc[0]["Value"])

    # Deleting the chart forgets it.
    [b for b in fresh.sidebar.button if b.help and "Delete" in b.help][0].click().run()
    assert "last_chart" not in json.loads(_prefs_path().read_text())


def test_sources_lists_the_readings_in_force_and_reset_restores_the_defaults(prefs_on):
    at = make_app(page="sources", switches={"connection": "Abu Ma'shar", "domain": "Masha'allah"}).run()
    assert_no_exception(at, "sources")
    table = [df.value for df in at.main.dataframe if "In force" in df.value.columns][0]
    rows = {r["Reading"]: r for _, r in table.iterrows()}
    assert rows["Connection test used in the shared tables"]["In force"] == "Abu Ma'shar"
    assert rows["Connection test used in the shared tables"]["Differs"] == "yes"
    assert rows["Domain (hayz)"]["Differs"] == "yes"
    assert rows["Reading depth"]["In force"] == "Course text"
    assert len(rows) == 10
    # _persist has been through the radios? Not on this page -- seed the file the way a session would.
    at.session_state["_prefs"]["_connection_rule"] = "Abu Ma'shar"
    [b for b in at.main.button if "Reset" in b.label][0].click().run()
    assert_no_exception(at, "reset")
    table = [df.value for df in at.main.dataframe if "In force" in df.value.columns][0]
    assert all(r["Differs"] == "" for _, r in table.iterrows())
    with pytest.raises(KeyError):
        at.session_state["_connection_rule"]
    on_disk = json.loads(_prefs_path().read_text()) if _prefs_path().exists() else {}
    assert "_connection_rule" not in on_disk


def test_the_reading_depth_is_a_reading_on_the_sources_page(prefs_on):
    at = make_app(page="sources").run()
    find_page_widget(at, "radio", "Reading depth").set_value("Course text and supplement").run()
    assert at.session_state["_reading_depth"] == "Course text and supplement"
    assert json.loads(_prefs_path().read_text())["_reading_depth"] == "Course text and supplement"


def test_option_values_renamed_by_the_citation_convention_still_load(prefs_on):
    """A preferences file written before 2026-09-10 holds the old option
    strings; load_preferences maps them to the new ones."""
    _prefs_path().parent.mkdir(parents=True)
    _prefs_path().write_text(json.dumps({"_pn4_monthly_turn": "Abu Ma'shar IX.1, 26-34",
                                         "_wheel_order": "Revolution inside (Abu Ma'shar, I.6)"}))
    at = make_app(page="timing").run()
    assert_no_exception(at, "renamed options")
    assert at.session_state["_pn4_monthly_turn"] == "PN IV IX.1, 26-34"
    assert at.session_state["_wheel_order"] == "Revolution inside (Abu Ma'shar's order, PN IV I.6)"
    assert at.main.radio(key="pn4_monthly_turn").value == "PN IV IX.1, 26-34"
