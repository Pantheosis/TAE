"""The saved-chart lifecycle (F04 of the UI review of 2026-09-16).

The review's own reproductions are the acceptance cases: E05 -- save a new
chart, inspect the strip and the picker, edit the loaded record, choose New,
save a duplicate name, delete the record -- and E06, a malformed store in a
disposable profile.

Everything here runs against a tmp_path XDG directory, never the real one.
"""
import json
import os
from datetime import time
from pathlib import Path

import pytest

from conftest import FLORENCE, assert_no_exception, make_app

PETOSKEY = (45.37334, -84.95533)


def _store_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "saved_charts.json"


def _name_box(at):
    return [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0]


def _save_button(at):
    return [b for b in at.sidebar.button if "Save" in b.label][0]


def _bin_button(at):
    return [b for b in at.sidebar.button if b.help and "Delete" in b.help][0]


def _labelled(at, label):
    hits = [b for b in at.sidebar.button if b.label == label]
    assert len(hits) == 1, f"expected one sidebar button '{label}', found {[b.label for b in at.sidebar.button]}"
    return hits[0]


def _has(at, label):
    return any(b.label == label for b in at.sidebar.button)


def _strip(at):
    """The chart strip's first part: the name the page says it is reading."""
    for caption in at.main.caption:
        if " · " in caption.value:
            return caption.value.split(" · ")[0]
    return ""


def _full_strip(at):
    """The whole first line of the strip: the name, the moment, the place."""
    for caption in at.main.caption:
        if " · " in caption.value:
            return caption.value
    return ""


def _picker(at):
    return at.sidebar.selectbox(key="chart_picker")


def _save_as(at, name):
    _name_box(at).set_value(name).run()
    _save_button(at).click().run()
    return at


# --- E05 / F04 ------------------------------------------------------------

def test_a_save_selects_and_names_the_record(tmp_path, monkeypatch):
    """Item 1: the picker's options used to be built before the Save button
    ran, so a save reported success while the picker held only
    '-- New Chart --' and the strip still said 'Unsaved chart'."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    assert _strip(at) == "Unsaved chart"
    _save_as(at, "Lifecycle A")
    assert_no_exception(at, "the save")
    assert "Lifecycle A" in _picker(at).options
    assert _picker(at).value == "Lifecycle A"
    assert at.session_state["chart_picker"] == "Lifecycle A"
    assert _strip(at) == "Lifecycle A"
    assert json.loads(_store_path().read_text())["Lifecycle A"]["date_string"] == "1983-11-19"


def test_an_edited_record_says_it_has_been_edited(tmp_path, monkeypatch):
    """Item 2: Modified, in the strip and under the picker."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    assert _strip(at) == "Lifecycle A"
    assert not any(c.value == "Edited since it was saved." for c in at.sidebar.caption)

    at.sidebar.text_input(key="date_input_key").set_value("1983-11-20").run()
    assert_no_exception(at, "the edit")
    assert _strip(at) == "Lifecycle A (modified)"
    assert any(c.value == "Edited since it was saved." for c in at.sidebar.caption)

    # Edited back: the record and the fields are the same nativity again.
    at.sidebar.text_input(key="date_input_key").set_value("1983-11-19").run()
    assert _strip(at) == "Lifecycle A"
    assert not any(c.value == "Edited since it was saved." for c in at.sidebar.caption)


def test_the_harness_leaves_the_picker_on_new_chart(tmp_path, monkeypatch):
    """A saved store does not select itself: the harness seeds the fields,
    and every other test's strip goes on reading 'Unsaved chart'."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    fresh = make_app(date="1240-05-23", page="chart").run()
    assert fresh.session_state["chart_picker"] == "-- New Chart --"
    assert _strip(fresh) == "Unsaved chart"


def test_new_chart_clears_the_form_to_the_example_nativity(tmp_path, monkeypatch):
    """Item 3: '-- New Chart --' is a new chart, not a deselection. The
    review found it keeping the edited date and place of the record just
    left. The preferences are not touched: 'last_chart' still names the
    chart that was saved, so the next launch opens on it."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart")
    at.session_state["manual_lat_key"], at.session_state["manual_lon_key"] = PETOSKEY
    at.session_state["time_input_key"] = time(11, 44)
    at.session_state["time_standard_key"] = "Standard time (pytz)"
    at.run()
    _save_as(at, "Lifecycle A")
    assert _picker(at).value == "Lifecycle A"

    _picker(at).select("-- New Chart --").run()
    assert_no_exception(at, "a new chart")
    assert at.session_state["date_input_key"] == "1240-05-23"
    assert at.session_state["time_input_key"] == time(14, 30)
    assert at.session_state["time_standard_key"] == "LMT (Local Mean Time)"
    assert at.session_state["utc_offset_key"] == 0.0
    assert at.session_state["manual_coords_key"] is False
    assert at.session_state["location_input_key"] == "Florence"
    assert at.session_state["manual_lat_key"] == pytest.approx(43.7698)
    assert at.session_state["manual_lon_key"] == pytest.approx(11.2556)
    # The store key, which the top level reads; since 2026-09-17 the form
    # drops the widget key rather than writing it (a plain value under a
    # widget's key, written on a page that does not render the widget,
    # shadowed the store once the widget went stale -- see the loader).
    assert at.session_state["_target_mode"] == "Date"
    assert "target_mode" not in at.session_state
    assert "loaded_location" not in at.session_state
    assert _strip(at) == "Unsaved chart"
    # The record itself is untouched, and it is still the chart a fresh
    # session would open on.
    assert "Lifecycle A" in json.loads(_store_path().read_text())


def test_saving_the_same_name_unchanged_writes_nothing(tmp_path, monkeypatch):
    """Item 4, first arm: nothing to write, and nothing to ask about."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    before = _store_path().read_bytes()

    _save_button(at).click().run()
    assert_no_exception(at, "the second save")
    assert any(i.value == "'Lifecycle A' is already saved as it is." for i in at.sidebar.info)
    assert not _has(at, "Replace")
    assert _store_path().read_bytes() == before


def test_a_same_name_save_asks_before_replacing_and_replace_overwrites(tmp_path, monkeypatch):
    """Item 4, second arm: the first press writes nothing at all."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    before = _store_path().read_bytes()

    at.sidebar.text_input(key="date_input_key").set_value("1983-11-20").run()
    _save_button(at).click().run()
    assert_no_exception(at, "the colliding save")
    assert any(w.value == "'Lifecycle A' exists. Replace it?" for w in at.sidebar.warning)
    assert _has(at, "Replace") and _has(at, "Keep both")
    assert _store_path().read_bytes() == before, "the first press must write nothing"
    assert at.session_state["_replace_pending"] == "Lifecycle A"

    _labelled(at, "Replace").click().run()
    assert_no_exception(at, "replace")
    stored = json.loads(_store_path().read_text())
    assert list(stored) == ["Lifecycle A"]
    assert stored["Lifecycle A"]["date_string"] == "1983-11-20"
    assert _picker(at).value == "Lifecycle A"
    assert _strip(at) == "Lifecycle A"
    assert not _has(at, "Replace")


def test_keep_both_saves_under_the_first_free_number(tmp_path, monkeypatch):
    """Item 4, third arm."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    at.sidebar.text_input(key="date_input_key").set_value("1983-11-20").run()
    _save_button(at).click().run()

    _labelled(at, "Keep both").click().run()
    assert_no_exception(at, "keep both")
    stored = json.loads(_store_path().read_text())
    assert sorted(stored) == ["Lifecycle A", "Lifecycle A (2)"]
    assert stored["Lifecycle A"]["date_string"] == "1983-11-19", "the first record stands"
    assert stored["Lifecycle A (2)"]["date_string"] == "1983-11-20"
    assert _picker(at).value == "Lifecycle A (2)"
    assert _strip(at) == "Lifecycle A (2)"

    # And the next collision takes (3).
    at.sidebar.text_input(key="date_input_key").set_value("1983-11-21").run()
    _name_box(at).set_value("Lifecycle A").run()
    _save_button(at).click().run()
    _labelled(at, "Keep both").click().run()
    assert sorted(json.loads(_store_path().read_text())) == [
        "Lifecycle A", "Lifecycle A (2)", "Lifecycle A (3)"]


def test_another_sidebar_change_clears_the_replace_question(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    at.sidebar.text_input(key="date_input_key").set_value("1983-11-20").run()
    _save_button(at).click().run()
    assert _has(at, "Replace")

    at.sidebar.time_input(key="time_input_key").set_value(time(9, 15)).run()
    assert_no_exception(at, "another change")
    assert not _has(at, "Replace") and not _has(at, "Keep both")
    assert "_replace_pending" not in at.session_state
    assert not any(w.value.endswith("exists. Replace it?") for w in at.sidebar.warning)


def test_the_bin_asks_and_keep_leaves_the_record_alone(tmp_path, monkeypatch):
    """Item 5: the bin used to delete on the press, with no confirmation."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    before = _store_path().read_bytes()

    _bin_button(at).click().run()
    assert_no_exception(at, "the bin")
    assert any(w.value == "Delete 'Lifecycle A'?" for w in at.sidebar.warning)
    assert _has(at, "Delete") and _has(at, "Keep")
    assert _store_path().read_bytes() == before
    assert at.session_state["saved_charts"].get("Lifecycle A")

    _labelled(at, "Keep").click().run()
    assert_no_exception(at, "keep")
    assert not _has(at, "Delete") and not _has(at, "Keep")
    assert _store_path().read_bytes() == before
    assert _picker(at).value == "Lifecycle A"
    # Answering the question must not empty the boxes: a rerun from beside
    # the picker abandons the run before the fields are drawn, and Streamlit
    # discards a widget's state when a run does not draw it.
    assert at.session_state["date_input_key"] == "1983-11-19"
    assert "1983-11-19 14:30:00" in _full_strip(at)
    assert _strip(at) == "Lifecycle A", "nothing was edited"


def test_delete_removes_the_record_and_resets_the_picker(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    _bin_button(at).click().run()
    _labelled(at, "Delete").click().run()
    assert_no_exception(at, "delete")
    assert json.loads(_store_path().read_text()) == {}
    assert at.session_state["saved_charts"] == {}
    assert at.session_state["chart_picker"] == "-- New Chart --"
    assert _picker(at).options == ["-- New Chart --"]
    assert _strip(at) == "Unsaved chart"
    assert not _has(at, "Delete")
    # The picker is reset; the nativity in the boxes is not touched.
    assert at.session_state["date_input_key"] == "1983-11-19"
    assert "1983-11-19 14:30:00" in _full_strip(at)


# --- E06 / F04, item 6: an unreadable store -------------------------------

MALFORMED = b'{"Kept": {"date_string": "1983-11-19", '


def test_a_malformed_store_is_preserved_named_and_not_overwritten(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    path = _store_path()
    path.parent.mkdir(parents=True)
    path.write_bytes(MALFORMED)

    at = make_app(date="1240-05-23", page="chart").run()
    assert_no_exception(at, "a malformed store")
    copies = sorted(path.parent.glob("saved_charts.json.unreadable-*"))
    assert len(copies) == 1, [p.name for p in copies]
    assert copies[0].read_bytes() == MALFORMED
    assert any(e.value == ("Saved charts could not be read. The original file was "
                           f"kept as {copies[0].name}.") for e in at.sidebar.error), \
        [e.value for e in at.sidebar.error]
    # The picker is empty and says so by holding nothing but the new chart.
    assert _picker(at).options == ["-- New Chart --"]
    assert at.session_state["saved_charts"] == {}

    # Saving afterwards writes a fresh store; the bytes are still beside it.
    _save_as(at, "After the wreck")
    assert_no_exception(at, "saving over a wreck")
    assert json.loads(path.read_text())["After the wreck"]["date_string"] == "1240-05-23"
    assert copies[0].read_bytes() == MALFORMED
    assert _picker(at).value == "After the wreck"


def test_the_message_is_shown_once_per_session(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    path = _store_path()
    path.parent.mkdir(parents=True)
    path.write_bytes(MALFORMED)
    at = make_app(date="1240-05-23", page="chart").run()
    assert any("could not be read" in e.value for e in at.sidebar.error)
    at.sidebar.text_input(key="date_input_key").set_value("1240-05-24").run()
    assert not any("could not be read" in e.value for e in at.sidebar.error)


def test_the_same_bytes_are_copied_once_not_once_per_launch(tmp_path, monkeypatch):
    """A reader who opens the app three times against one broken file gets
    one recovery copy, not three."""
    import engine as engine_module

    path = tmp_path / "saved_charts.json"
    monkeypatch.setattr(engine_module, "SAVED_CHARTS_PATH", path)
    monkeypatch.setattr(engine_module, "_LEGACY_SAVED_CHARTS_PATH", tmp_path / "legacy" / "saved_charts.json")
    path.write_bytes(MALFORMED)
    for _ in range(3):
        assert engine_module.load_saved_charts() == {}
    copies = sorted(tmp_path.glob("saved_charts.json.unreadable-*"))
    assert len(copies) == 1, [p.name for p in copies]
    assert copies[0].read_bytes() == MALFORMED
    assert engine_module.LAST_STORE_ERROR == copies[0].name

    # Different bytes, a second copy.
    path.write_bytes(MALFORMED + b"x")
    assert engine_module.load_saved_charts() == {}
    assert len(sorted(tmp_path.glob("saved_charts.json.unreadable-*"))) == 2

    # A readable store leaves nothing to report.
    path.write_text(json.dumps({"Fine": {"date_string": "1240-05-23"}}))
    assert engine_module.load_saved_charts() == {"Fine": {"date_string": "1240-05-23"}}
    assert engine_module.LAST_STORE_ERROR is None


# --- Item 7: the session follows the disk ---------------------------------

def test_a_failed_write_leaves_the_session_as_it_was(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    before = dict(at.session_state["saved_charts"])

    import engine as engine_module
    monkeypatch.setattr(engine_module, "write_saved_charts", lambda charts: False)
    _save_as(at, "Never written")
    assert_no_exception(at, "a failed write")
    assert at.session_state["saved_charts"] == before
    assert "Never written" not in at.session_state["saved_charts"]
    assert any(e.value == "Could not write saved_charts.json to disk." for e in at.sidebar.error)
    assert not _store_path().exists()
    assert _strip(at) == "Unsaved chart"


def test_a_failed_delete_leaves_the_record_in_the_session(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    on_disk = _store_path().read_bytes()

    import engine as engine_module
    monkeypatch.setattr(engine_module, "write_saved_charts", lambda charts: False)
    _bin_button(at).click().run()
    _labelled(at, "Delete").click().run()
    assert_no_exception(at, "a failed delete")
    assert "Lifecycle A" in at.session_state["saved_charts"]
    assert _store_path().read_bytes() == on_disk
    assert any(e.value == "Could not write saved_charts.json to disk." for e in at.sidebar.error)


# --- The record comparison itself -----------------------------------------

def test_the_coordinates_are_compared_as_numbers_to_four_places(tmp_path, monkeypatch):
    """A record whose coordinates came back from JSON as ints, or as a
    string, is the same place: the strip must not cry Modified over it."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date="1983-11-19", page="chart").run()
    _save_as(at, "Lifecycle A")
    record = dict(at.session_state["saved_charts"]["Lifecycle A"])
    assert record["lat"] == pytest.approx(FLORENCE[0])
    record["lat"] = str(FLORENCE[0])
    record["lon"] = round(FLORENCE[1], 4)
    record["target_age"] = float(record["target_age"])
    at.session_state["saved_charts"] = {"Lifecycle A": record}
    at.run()
    assert _strip(at) == "Lifecycle A"
