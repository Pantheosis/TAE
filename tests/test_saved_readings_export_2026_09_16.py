"""The readings a chart is saved with, and the analysis export.

F03 and F08 of the independent UI review of 2026-09-16, with E04 as the
acceptance case: save a chart under Abu Ma'shar's connection rule, change
the rule to Sahl, load the chart again. The review found Sahl still in
force with nothing said. From this branch the record carries the readings
it was saved under, the load says which it is doing, and an Export analysis
action writes what was entered, what was in force, what was computed and
what computed it.

Everything here runs against a tmp_path XDG directory, never the real one.
"""
import json
import os
import re
from pathlib import Path

import pytest

from conftest import (FLORENCE, assert_no_exception, make_app,
                      sync_engine_to_environment, table_inventory)

ABU, SAHL = "Abu Ma'shar", "Sahl"


def _store_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "saved_charts.json"


def _name_box(at):
    return [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0]


def _save_button(at):
    return [b for b in at.sidebar.button if "Save" in b.label][0]


def _picker(at):
    return at.sidebar.selectbox(key="chart_picker")


def _save_as(at, name):
    _name_box(at).set_value(name).run()
    _save_button(at).click().run()
    return at


def _load(at, name):
    """Pick a saved chart. The picker is left ON the record a save just
    wrote (F04, item 1), so a selection has to leave it before it can be a
    selection at all -- which is what a reader does too."""
    _picker(at).select("-- New Chart --").run()
    _picker(at).select(name).run()
    return at


def _labelled(at, label):
    hits = [b for b in at.sidebar.button if b.label == label]
    assert len(hits) == 1, (
        f"expected one sidebar button '{label}', found {[b.label for b in at.sidebar.button]}")
    return hits[0]


def _has_button(at, label):
    return any(b.label == label for b in at.sidebar.button)


def _captions(at):
    return [c.value for c in at.sidebar.caption]


def _infos(at):
    return [i.value for i in at.sidebar.info]


def _strip(at):
    for caption in at.main.caption:
        if " · " in caption.value:
            return caption.value.split(" · ")[0]
    return ""


def _saved_under(tmp_path, monkeypatch, name, rule, date="1240-05-23"):
    """Save a chart with the connection rule set to `rule`, and return the
    record as it reached the file."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = make_app(date=date, page="chart")
    at.session_state["_connection_rule"] = rule
    at.run()
    _save_as(at, name)
    assert_no_exception(at, f"the save under {rule}")
    return at, json.loads(_store_path().read_text())[name]


# --- Part 1: the readings travel with the record (F03, E04) ---------------

def test_a_saved_record_carries_the_readings_it_was_saved_under(tmp_path, monkeypatch):
    at, record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    assert record["readings"]["_connection_rule"] == ABU
    assert record["saved_with"]["schema"] == 2
    assert record["saved_with"]["app"]
    # Every reading the app offers is written down, not only the one moved.
    from engine import CHART_RECORD_READINGS
    assert set(record["readings"]) == {key for key, _spec in CHART_RECORD_READINGS}


def test_the_registry_and_the_engines_reading_schema_agree(engine):
    """The record's readings are validated in engine.py and named in
    app.py. One list in two files: held together here so a reading added
    to the registry cannot go unvalidated."""
    from conftest import app_source
    registry = re.search(r"READINGS_REGISTRY = \((.*?)\n\)\n", app_source(), re.S).group(1)
    in_app = set(re.findall(r'"(_[a-z0-9_]+)"', registry))
    in_engine = {key for key, _spec in engine["CHART_RECORD_READINGS"]}
    assert in_app == in_engine


def test_loading_a_record_saved_under_another_rule_asks_and_changes_nothing(tmp_path, monkeypatch):
    """E04. The store is NOT touched by the load: the prompt stands under
    the picker and neither branch has been taken."""
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    at.session_state["_connection_rule"] = SAHL
    at.run()
    _load(at, "Readings A")
    assert_no_exception(at, "the load")

    assert at.session_state["_connection_rule"] == SAHL, "the load changed a reading"
    assert "'Readings A' was saved under other readings." in _infos(at)
    assert _has_button(at, "Open saved readings")
    assert _has_button(at, "Keep current readings")


def test_open_saved_readings_puts_them_in_force_and_the_tables_follow(tmp_path, monkeypatch):
    """The first branch. The store reads Abu Ma'shar again, and the aspects
    table is computed under his rule -- compared on one row, so that a
    reading restored without reaching the evaluators would fail here."""
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU, date="1240-09-18")
    at.session_state["_connection_rule"] = SAHL
    at.run()

    under_sahl = _aspect_rows(make_app(date="1240-09-18", page="configurations",
                                       switches={"connection": SAHL}).run())
    under_abu = _aspect_rows(make_app(date="1240-09-18", page="configurations",
                                      switches={"connection": ABU}).run())
    assert under_sahl != under_abu, "this chart does not tell the two rules apart"

    _load(at, "Readings A")
    _labelled(at, "Open saved readings").click().run()
    assert_no_exception(at, "opening the saved readings")
    assert at.session_state["_connection_rule"] == ABU
    assert at.session_state["connection_rule"] == ABU
    assert not _has_button(at, "Open saved readings"), "the question is answered and gone"

    after = make_app(date="1240-09-18", page="configurations")
    after.session_state["_connection_rule"] = at.session_state["_connection_rule"]
    assert _aspect_rows(after.run()) == under_abu


def _aspect_rows(at):
    """The aspects table as the Configurations page renders it."""
    for node in at.main:
        if getattr(node, "type", None) == "dataframe" and "Aspect" in list(node.value.columns):
            return node.value.to_dict("records")
    raise AssertionError("no aspects table on the Configurations page")


def test_keep_current_readings_leaves_them_and_the_chart_reads_modified(tmp_path, monkeypatch):
    """The second branch. Nothing is set, the question goes, and the chart
    is (modified) BY ITS READINGS -- which is the truth of it, and the
    caption says which side moved."""
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    at.session_state["_connection_rule"] = SAHL
    at.run()
    _load(at, "Readings A")
    _labelled(at, "Keep current readings").click().run()
    assert_no_exception(at, "keeping the current readings")

    assert at.session_state["_connection_rule"] == SAHL
    assert not _has_button(at, "Keep current readings")
    assert _strip(at) == "Readings A (modified)"
    assert "Saved with other readings." in _captions(at)
    # The nativity itself has not been edited, so the other line is absent.
    assert "Edited since it was saved." not in _captions(at)


def test_an_edited_nativity_under_other_readings_says_both(tmp_path, monkeypatch):
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    at.session_state["_connection_rule"] = SAHL
    at.run()
    _load(at, "Readings A")
    _labelled(at, "Keep current readings").click().run()
    at.sidebar.text_input(key="date_input_key").set_value("1240-05-24").run()
    assert "Edited since it was saved." in _captions(at)
    assert "Saved with other readings." in _captions(at)


def test_a_record_saved_under_the_readings_in_force_asks_nothing(tmp_path, monkeypatch):
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    at.run()
    _picker(at).select("-- New Chart --").run()
    _load(at, "Readings A")
    assert_no_exception(at, "the load")
    assert not _has_button(at, "Open saved readings")
    assert not any("saved under other readings" in i for i in _infos(at))
    assert _strip(at) == "Readings A"


def test_a_schema_one_record_loads_with_one_caption_and_no_prompt(tmp_path, monkeypatch):
    """A record written before this app stored the readings: it has nothing
    to restore, so there is no question to ask -- one sentence instead."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    sync_engine_to_environment()
    store = _store_path()
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps({"Old Record": {
        "date_string": "1240-05-23", "time_string": "14:30:00",
        "time_standard": "LMT (Local Mean Time)", "utc_offset": 0.0,
        "location_query": "Florence, 16 (IT)", "lat": FLORENCE[0], "lon": FLORENCE[1],
        "target_mode": "Date", "target_date": "1280-05-23", "target_age": 40}}))
    at = make_app(page="chart").run()
    _picker(at).select("Old Record").run()
    assert_no_exception(at, "loading a schema-1 record")

    assert ("Saved before readings were stored with a chart; "
            "results use the current readings.") in _captions(at)
    assert not _has_button(at, "Open saved readings")
    # It is not accused of having been saved under other readings either.
    assert "Saved with other readings." not in _captions(at)


def test_the_harness_never_has_the_prompt(tmp_path, monkeypatch):
    """The harness seeds the widget keys and never fires the picker's
    callback, so no test but this file's sees the question."""
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    fresh = make_app(date="1240-05-23", page="chart")
    fresh.session_state["_connection_rule"] = SAHL
    fresh.run()
    assert "_readings_pending" not in fresh.session_state
    assert not _has_button(fresh, "Open saved readings")
    assert not _has_button(fresh, "Keep current readings")


def test_saving_again_makes_the_readings_in_force_the_records_own(tmp_path, monkeypatch):
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    at.session_state["_connection_rule"] = SAHL
    at.run()
    _load(at, "Readings A")
    _labelled(at, "Keep current readings").click().run()
    assert _strip(at) == "Readings A (modified)"
    _save_as(at, "Readings A")
    _labelled(at, "Replace").click().run()
    assert json.loads(_store_path().read_text())["Readings A"]["readings"]["_connection_rule"] == SAHL
    assert _strip(at) == "Readings A"


# --- chart_record_fault on the readings -----------------------------------

def test_chart_record_fault_refuses_a_reading_value_the_app_cannot_set(engine):
    entry = {"date_string": "1240-05-23", "readings": {"_connection_rule": "Ptolemy"}}
    fault = engine["chart_record_fault"](entry)
    assert fault is not None
    assert fault[1] == "reading this app offers"
    assert "connection rule" in fault[0]
    # A checkbox's reading must be a bool, not the string of one.
    assert engine["chart_record_fault"]({"readings": {"_moon_rays_15": "yes"}}) is not None
    assert engine["chart_record_fault"]({"readings": {"_moon_rays_15": True}}) is None


def test_chart_record_fault_ignores_a_reading_key_it_does_not_know(engine):
    """A record from a later build, or one with a reading since withdrawn,
    is still this reader's nativity: the key is kept in the file and not
    acted on."""
    entry = {"date_string": "1240-05-23",
             "readings": {"_connection_rule": "Sahl", "_a_reading_from_the_future": "whatever"}}
    assert engine["chart_record_fault"](entry) is None
    assert engine["chart_record_readings"](entry) == {"_connection_rule": "Sahl"}


def test_a_record_with_no_readings_is_schema_one(engine):
    assert engine["chart_record_schema"]({"date_string": "1240-05-23"}) == 1
    assert engine["chart_record_schema"]({"readings": {"_connection_rule": "Sahl"}}) == 2
    assert engine["chart_record_fault"]({"readings": "not a mapping"})[0] == "saved readings"


# --- The Sources page's column -------------------------------------------

def test_the_readings_table_shows_what_the_selected_chart_was_saved_with(tmp_path, monkeypatch):
    at, _record = _saved_under(tmp_path, monkeypatch, "Readings A", ABU)
    fresh = make_app(page="sources").run()
    rows = _readings_table(fresh)
    assert [r["Saved with this chart"] for r in rows] == ["\u2013"] * len(rows), (
        "nothing is selected under the harness, so there is nothing to show")

    at2, _ = _saved_under(tmp_path, monkeypatch, "Readings B", ABU)
    at2.session_state["_connection_rule"] = SAHL
    at2.run()
    _load(at2, "Readings B")
    _labelled(at2, "Keep current readings").click()
    at2._page_hash = _page_hash("sources")
    at2.run()
    rows = _readings_table(at2)
    by_reading = {r["Reading"]: r for r in rows}
    row = by_reading["Connection test used in the shared tables"]
    assert row["In force"] == SAHL and row["Saved with this chart"] == ABU


def _page_hash(url_path):
    from streamlit.util import calc_hash
    return calc_hash(url_path)


def _readings_table(at):
    for node in at.main:
        if getattr(node, "type", None) == "dataframe" and "Reading" in list(node.value.columns):
            return node.value.to_dict("records")
    raise AssertionError("no readings table on the Sources page")


# --- Part 2: the analysis export (F08) ------------------------------------

@pytest.fixture(scope="module")
def analysis():
    """The export the default chart's sidebar built, as the download
    buttons carry it. The harness cannot read a download button's bytes,
    so the app leaves the object itself in session state."""
    at = make_app(page="chart").run()
    assert_no_exception(at, "the default chart")
    return at.session_state["_analysis_export"]


def test_the_export_has_its_schema_and_its_header(analysis):
    assert analysis["schema"] == 1
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", analysis["exported"])
    assert set(analysis) == {"schema", "exported", "app", "chart", "input", "entered",
                             "readings", "display", "target", "results", "status", "precision"}


def test_the_app_block_names_what_computed_this(analysis, engine):
    app = analysis["app"]
    assert app["version"] == engine["APP_VERSION"]
    assert app["ephemeris"] == "Moshier (built in)"
    assert re.fullmatch(r"[0-9a-f]{64}", app["engine_file_sha256"])
    assert app["streamlit"] and app["python"] and app["pyswisseph"]


def test_the_sha_is_the_engine_file_this_run_imported(analysis, engine):
    import hashlib
    from pathlib import Path as _Path
    import engine as engine_module
    expected = hashlib.sha256(_Path(engine_module.__file__).read_bytes()).hexdigest()
    assert analysis["app"]["engine_file_sha256"] == expected


def test_the_input_block_is_the_committed_chart(analysis):
    block = analysis["input"]
    assert block["date"] == "1240-05-23"
    assert block["time"] == "14:30:00"
    assert block["latitude"] == pytest.approx(FLORENCE[0])
    assert block["longitude"] == pytest.approx(FLORENCE[1])
    assert isinstance(block["julian_day_ut"], float)
    assert "Julian calendar" in block["calendar"]
    assert block["timezone"]


def test_every_reading_is_in_the_export_with_its_value_and_default(analysis, engine):
    by_key = {r["store_key"]: r for r in analysis["readings"]}
    assert set(by_key) == {key for key, _spec in engine["CHART_RECORD_READINGS"]}
    for row in analysis["readings"]:
        assert row["label"] and row["set_on"]
        assert "value" in row and "default" in row
    assert by_key["_connection_rule"]["value"] == "Sahl"
    assert by_key["_connection_rule"]["default"] == "Sahl"


def test_the_display_preferences_are_kept_apart_from_the_readings(analysis):
    assert set(analysis["display"]) == {"chart_bounds", "wheel_dark", "wheel_layout"}
    reading_keys = {r["store_key"] for r in analysis["readings"]}
    assert not reading_keys & {"_chart_bounds", "_wheel_dark", "_wheel_layout"}


def test_the_target_and_the_status_are_written_down(analysis):
    assert set(analysis["target"]) == {"mode", "date", "age"}
    status = analysis["status"]
    assert status["chart_ok"] is True
    assert status["chart_error"] is None
    assert status["stale"] is False
    assert status["equal_hour_approximation"] in (True, False)
    assert status["forward_search_days"] == 200


def test_the_entered_block_is_the_record_a_save_would_write(analysis):
    entered = analysis["entered"]
    assert entered["date_string"] == "1240-05-23"
    assert entered["saved_with"]["schema"] == 2
    assert entered["readings"]["_connection_rule"] == "Sahl"


def test_the_results_are_keyed_by_page_and_heading(analysis):
    assert set(analysis["results"]) == {"Chart", "Dignities and places", "Configurations",
                                        "Lots", "Lunation and victors", "Timing"}
    for _page, headings in analysis["results"].items():
        for _heading, tables in headings.items():
            assert isinstance(tables, list) and tables
            for table in tables:
                assert set(table) <= {"rows", "columns", "citation"}
                assert isinstance(table["rows"], list)


# The tables the ruling names, and the page each is rendered on. The export
# must carry exactly the rows the reader saw.
# (url_path, page, heading, whether the page's own columns are the exported
# row's keys). The two tick grids are the exception: the page draws one
# ticked column per numbered testimony, while the export carries the
# evaluator's rows -- Labels, Count and the Testimonies themselves, which is
# what makes an exported strength reading inspectable at all.
NAMED_TABLES = [
    ("chart", "Chart", "Planetary Positions", True),
    ("chart", "Chart", "Calculated Points", True),
    ("chart", "Chart", "Quadrant divisions (Alchabitius)", True),
    ("dignities", "Dignities and places", "Lordship Mapping", True),
    ("dignities", "Dignities and places", "Sect", True),
    ("dignities", "Dignities and places", "Topical Planets in Houses", False),
    ("dignities", "Dignities and places", "Topical House Lords (Masha'allah)", True),
    ("configurations", "Configurations", "Aspects, aversions and connections", False),
    ("configurations", "Configurations", "Strength of the Planets", False),
    ("configurations", "Configurations", "Weakness of the Planets", False),
    ("lots", "Lots", "Classical Lots", True),
    ("lots", "Lots", "Topical Lots (Sahl, On Nativities)", False),
    ("victors", "Lunation and victors", "Prenatal Lunation (Syzygy)", True),
    ("victors", "Lunation and victors", "Victor of the Chart", True),
]


@pytest.mark.parametrize("url_path,page,heading,same_columns", NAMED_TABLES,
                         ids=[f"{p}-{h}" for _u, p, h, _c in NAMED_TABLES])
def test_each_named_table_is_exported_with_the_rows_the_page_renders(
        analysis, url_path, page, heading, same_columns):
    at = make_app(page=url_path).run()
    assert_no_exception(at, url_path)
    rendered = [node.value for node in at.main
                if getattr(node, "type", None) == "dataframe"]
    drawn = [df for df, (h, _cols) in zip(rendered, table_inventory(at)) if h == heading]
    assert drawn, f"{heading!r} did not render on {url_path}"
    exported = analysis["results"][page][heading]
    # The first table under the heading, on both sides: table_inventory()
    # hands a heading down to every grid that follows it until the next
    # one, so a heading can gather tables the export files elsewhere.
    assert len(exported[0]["rows"]) == len(drawn[0])
    if same_columns:
        assert set(exported[0]["columns"]) >= {str(c) for c in drawn[0].columns}


def test_a_table_the_page_does_not_draw_is_not_in_the_export(analysis):
    """Reception has no rows on the default chart, so the Configurations
    page prints its "nothing found" sentence and draws no grid. The export
    carries what the reader saw: no grid, no table."""
    assert not any(h.startswith("Reception") for h in analysis["results"]["Configurations"])

    at = make_app(date="1240-05-25", page="chart").run()
    other = at.session_state["_analysis_export"]
    reception = [h for h in other["results"]["Configurations"] if h.startswith("Reception")]
    assert reception == ["Reception \u2014 Sahl rule"], (
        "the chart the harness keeps for reception has none")
    page_at = make_app(date="1240-05-25", page="configurations").run()
    drawn = [df for df, (h, _c) in zip([n.value for n in page_at.main
                                        if getattr(n, "type", None) == "dataframe"],
                                       table_inventory(page_at))
             if h == "Reception \u2014 Sahl rule"]
    assert len(other["results"]["Configurations"][reception[0]][0]["rows"]) == len(drawn[0])


def test_the_strength_and_weakness_rows_carry_their_testimonies(analysis):
    for heading in ("Strength of the Planets", "Weakness of the Planets"):
        rows = analysis["results"]["Configurations"][heading][0]["rows"]
        assert rows
        for row in rows:
            assert row["Testimonies"], f"{heading}: a row with no testimonies"
            assert all("sentence" in t for t in row["Testimonies"])


def test_the_timing_bundles_tables_are_under_the_pages_own_headings(analysis):
    """The export's Timing section keeps its name and its headings; since
    2026-09-17 the pages that render them are four (Timing, The releaser,
    Days and months, Fardar and ages), so the headings are gathered from
    all four."""
    on_page = set()
    for page in ("timing", "releaser", "days", "fardar"):
        at = make_app(page=page).run()
        assert_no_exception(at, page)
        on_page |= {heading for heading, _cols in table_inventory(at)}
    exported = set(analysis["results"]["Timing"])
    missing = exported - on_page
    assert not missing, f"the export names headings the Prediction pages do not render: {sorted(missing)}"
    assert len(exported) > 20


def test_the_export_round_trips_through_json(analysis):
    text = json.dumps(analysis, indent=1, ensure_ascii=False)
    assert json.loads(text) == analysis


def test_the_markdown_carries_the_same_sections_and_headings(analysis):
    at = make_app(page="chart").run()
    report = _markdown(at)
    for section in ("What computed this", "What was entered", "The readings in force",
                    "Display preferences", "The target", "Status", "Results", "Precision"):
        assert f"## {section}" in report, section
    for page in analysis["results"]:
        assert f"### {page}" in report
    for heading in analysis["results"]["Chart"]:
        assert f"#### {heading}" in report
    assert analysis["app"]["engine_file_sha256"] in report
    assert "| Planet |" in report


# The Markdown cannot be read off a download button any more than the JSON
# can, so the app leaves the report it handed the button in session state
# and the test reads the very bytes the reader would have downloaded.
def _markdown(at):
    return at.session_state["_analysis_markdown"]


# --- The buttons themselves ----------------------------------------------

def test_the_two_download_buttons_stand_under_save_when_there_is_a_chart():
    at = make_app(page="chart").run()
    labels = [b.label for b in at.sidebar.download_button]
    assert "Export analysis (JSON)" in labels
    assert "Export analysis (Markdown)" in labels
    assert not any(b.proto.disabled for b in at.sidebar.download_button)


def test_the_buttons_are_disabled_with_a_caption_when_there_is_no_chart():
    at = make_app(page="chart")
    at.session_state["date_input_key"] = "1240-05-23"
    at.session_state["manual_lat_key"] = 43.7792
    at.session_state["manual_lon_key"] = 11.2463
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = ""
    at.run()
    buttons = at.sidebar.download_button
    labels = [b.label for b in buttons]
    assert "Export analysis (JSON)" in labels and "Export analysis (Markdown)" in labels
    assert all(b.proto.disabled for b in buttons if b.label.startswith("Export analysis"))
    assert "There is no chart to export; the input above says why." in _captions(at)
