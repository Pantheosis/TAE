"""The "Here & Now" button on the nativity sidebar, and the home place it
casts at.

"Here" is a stored home place: the reader keeps the birthplace the sidebar
has resolved, with "Set as home" in the "Home" popover of the sidebar's
first row (the owner's ruling on the preview: the home's controls out of
sight until wanted, the Birthplace section exactly main's), and it is
the preference 'home_place' -- {"label", "lat", "lon"}, validated by
engine.home_place_is_valid so that a hand-edited file cannot take the app
down. "Now" is this computer's clock, read through engine.now_utc() (and,
for a home with no zone, engine.local_clock()), which every test here
patches on the engine module AFTER make_app has run -- make_app reloads the
engine when the preferences environment moves -- so that no test depends
on the wall clock.

Preferences are switched on against a tmp_path as tests/test_preferences.py
does; the harness guard (ALMUTEN_NO_PREFERENCES=1) is lifted by the fixture.
"""
import json
import os
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

import pytest

import engine
from conftest import APP_PATH, assert_no_exception, make_app

NOON_ISH = datetime(2026, 9, 17, 12, 34, 56, tzinfo=timezone.utc)      # CEST at Florence: 14:34:56
JANUARY = datetime(2026, 1, 17, 12, 34, 56, tzinfo=timezone.utc)       # CET at Florence: 13:34:56
# 2026-10-25 00:30Z is 02:30 CEST in Europe/Rome, and 02:30 happens twice
# that morning (the clocks go back at 03:00 CEST): the repeated hour.
FALL_BACK = datetime(2026, 10, 25, 0, 30, 0, tzinfo=timezone.utc)
AT_SEA = {"label": "At sea", "lat": 0.0, "lon": -30.0}
STANDARD, MANUAL = engine.TIME_STANDARD_OPTIONS[1], engine.TIME_STANDARD_OPTIONS[2]


def _prefs_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "preferences.json"


def _store_path():
    return Path(os.environ["XDG_DATA_HOME"]) / "TraditionalAstrologyEngine" / "saved_charts.json"


@pytest.fixture
def prefs_on(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.delenv("ALMUTEN_NO_PREFERENCES", raising=False)
    return tmp_path


def _florence_app(page="chart"):
    """The example chart with Florence resolved through the atlas, so that
    the label is the atlas's own and not the harness's coordinate pair."""
    at = make_app(page=page)
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = "Florence"
    return at


def _freeze(monkeypatch, instant, local=None):
    """Patch the clock on the engine module, after make_app."""
    monkeypatch.setattr(engine, "now_utc", lambda: instant)
    if local is not None:
        monkeypatch.setattr(engine, "local_clock", lambda moment: moment.astimezone(local))


def _here_now(at):
    return at.sidebar.button(key="_here_and_now")


def _set_home(at):
    return at.sidebar.button(key="_set_home")


def _top_row(at):
    """The sidebar's first child: the row above the Nativity header."""
    return list(at.sidebar.children.values())[0]


def _popover(at):
    """The home popover, the one child of the top row's second column."""
    columns = list(_top_row(at).children.values())
    assert len(columns) == 2
    blocks = list(columns[1].children.values())
    assert len(blocks) == 1 and blocks[0].type == "popover", [b.type for b in blocks]
    return blocks[0]


def _popover_label(at):
    return _popover(at).proto.popover.label


def _sidebar_kinds(at):
    return [(getattr(c, "type", None), str(getattr(c, "label", None) or getattr(c, "value", None) or ""))
            for c in at.sidebar.children.values()]


def _buttons(at):
    return [b.label for b in at.sidebar.button]


def _home_caption(at):
    hits = [c.value for c in at.sidebar.caption if c.value.startswith("Home: ")]
    return hits[0] if hits else None


def _strip(at):
    for caption in at.main.caption:
        if " · " in caption.value:
            return caption.value
    return ""


def _no_streamlit_warning(at):
    """No widget was drawn with a default beside a seeded key."""
    noise = [w.value for w in at.warning if "Session State API" in w.value]
    assert not noise, noise


# --- The buttons and the preference --------------------------------------

def test_no_home_stored_the_button_is_disabled_and_says_why(prefs_on):
    at = _florence_app().run()
    assert_no_exception(at, "open")
    button = _here_now(at)
    assert button.disabled
    assert button.help == "Set a home place under Birthplace first."
    assert _popover_label(at) == "Set home"
    assert not _set_home(at).disabled
    assert "Forget home" not in _buttons(at)
    assert _home_caption(at) is None
    assert [c.value for c in _popover(at).caption] == ["Resolve a place under Birthplace, then set it as home."]


def test_the_top_row_holds_exactly_the_two_controls(prefs_on):
    """The sidebar's first child is the row above the Nativity header: two
    columns, the left holding the Here & Now button alone, the right the
    home popover alone; the header comes next."""
    for at in (_florence_app().run(), make_app(page="chart").run()):
        row = _top_row(at)
        assert row.type == "flex_container"
        columns = list(row.children.values())
        assert [c.type for c in columns] == ["column", "column"]
        left = list(columns[0].children.values())
        assert [(c.type, c.label) for c in left] == [("button", "\U0001F4CD Here & Now")]
        right = list(columns[1].children.values())
        assert [c.type for c in right] == ["popover"]
        kinds = _sidebar_kinds(at)
        assert kinds[1] == ("header", "Nativity"), kinds[:3]


# The Birthplace section's direct children on main, from its header to the
# chart-name box, for the harness's manual pair and for a city resolved
# through the atlas -- measured on an archive of main; the branch adds
# nothing under Birthplace (the owner's ruling).
BIRTHPLACE_ON_MAIN = {
    "manual": [("header", "Birthplace"), ("toggle", "Enter coordinates directly"),
               ("number_input", "Latitude"), ("number_input", "Longitude"),
               ("success", "**Manual [43.7792, 11.2463]**  \n43.7792, 11.2463"),
               ("text_input", "Chart name (for saving)")],
    "city": [("header", "Birthplace"), ("toggle", "Enter coordinates directly"),
             ("text_input", "City, or latitude, longitude"), ("selectbox", "Select specific location:"),
             ("success", "**Florence, 16 (IT)**  \n43.7792, 11.2463 · Europe/Rome"),
             ("text_input", "Chart name (for saving)")],
}


@pytest.mark.parametrize("which", sorted(BIRTHPLACE_ON_MAIN))
def test_the_birthplace_section_is_exactly_mains(prefs_on, which):
    """With and without a home set, and after Set as home: no extra element
    between the Birthplace header and the chart-name box."""
    at = make_app(page="chart")
    if which == "city":
        at.session_state["manual_coords_key"] = False
        at.session_state["location_input_key"] = "Florence"
        at.session_state["time_standard_key"] = STANDARD
    at.run()
    assert_no_exception(at, which)

    def section(at):
        kinds = _sidebar_kinds(at)
        start = next(i for i, (t, l) in enumerate(kinds) if (t, l) == ("header", "Birthplace"))
        end = next(i for i, (t, l) in enumerate(kinds) if t == "text_input" and l.startswith("Chart name"))
        return kinds[start:end + 1]

    assert section(at) == BIRTHPLACE_ON_MAIN[which]
    _set_home(at).click().run()
    assert _popover_label(at) == "Home"
    assert section(at) == BIRTHPLACE_ON_MAIN[which]
    assert "Set as home" not in [l for t, l in _sidebar_kinds(at)]


def test_set_as_home_is_disabled_until_a_place_is_resolved(prefs_on):
    at = make_app(page="chart")
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = "Zzqxv nowhere"
    at.run()
    assert_no_exception(at, "no match")
    assert any("No matches" in w.value for w in at.sidebar.warning)
    assert _set_home(at).disabled
    assert _here_now(at).disabled
    # An out-of-range pair is not a resolved place either.
    at = make_app(page="chart")
    at.session_state["manual_lat_key"] = 91.0
    at.run()
    assert _set_home(at).disabled
    assert _popover_label(at) == "Set home"


def test_set_as_home_writes_the_resolved_place_and_the_caption_names_it(prefs_on):
    at = _florence_app().run()
    label = [s.value for s in at.sidebar.success][0].split("**")[1]
    assert label.startswith("Florence, ")
    at.sidebar.button(key="_set_home").click().run()
    assert_no_exception(at, "set as home")
    on_disk = json.loads(_prefs_path().read_text())["home_place"]
    assert on_disk == {"label": label, "lat": pytest.approx(43.7792, abs=1e-4), "lon": pytest.approx(11.2463, abs=1e-4)}
    assert set(on_disk) == {"label", "lat", "lon"}
    assert isinstance(on_disk["lat"], float) and isinstance(on_disk["lon"], float)
    assert _home_caption(at) == f"Home: {label} · {on_disk['lat']:.4f}, {on_disk['lon']:.4f}"
    assert [c.value for c in _popover(at).caption] == [_home_caption(at)]
    assert _popover_label(at) == "Home"
    assert "Forget home" in _buttons(at)
    assert not _here_now(at).disabled
    assert _here_now(at).help == "Cast a chart for the home place at this moment, by this computer's clock."

    # The same place again writes nothing: content and mtime unchanged.
    before = (_prefs_path().read_bytes(), _prefs_path().stat().st_mtime_ns)
    at.sidebar.button(key="_set_home").click().run()
    assert_no_exception(at, "set again")
    assert (_prefs_path().read_bytes(), _prefs_path().stat().st_mtime_ns) == before

    # Forget removes it and disables the button on the same run.
    at.sidebar.button(key="_forget_home").click().run()
    assert_no_exception(at, "forget")
    assert "home_place" not in json.loads(_prefs_path().read_text())
    assert "home_place" not in at.session_state
    assert _here_now(at).disabled
    assert _popover_label(at) == "Set home"
    assert "Forget home" not in _buttons(at)
    assert _home_caption(at) is None


def test_set_as_home_writes_the_place_the_box_shows_on_that_run(prefs_on):
    """The natural gesture -- a city typed over and the button clicked
    without Enter -- delivers the edit and the click in one run. The press
    is handled at the button's site from that run's resolved place, so the
    home is the place the box beside the button shows, not the last
    run's (the adversarial pass: Madrid in the box, Berlin written)."""
    at = _florence_app().run()
    at.sidebar.text_input(key="location_input_key").set_value("Paris")
    at.sidebar.button(key="_set_home").click()
    at.run()
    assert_no_exception(at, "edit and click in one run")
    box = [s.value for s in at.sidebar.success][0]
    assert box.startswith("**Paris, ")
    on_disk = json.loads(_prefs_path().read_text())["home_place"]
    assert on_disk["label"].startswith("Paris, ")
    assert on_disk["lat"] == pytest.approx(48.85, abs=0.05)
    assert _home_caption(at).startswith(f"Home: {on_disk['label']} · ")
    # The top button sees the new home on that very run (the run is
    # repeated from the sidebar's foot once the home has changed).
    assert not _here_now(at).disabled
    # The same with a coordinate: the field edited and the button clicked
    # in one run writes the edited pair.
    at.sidebar.toggle(key="manual_coords_key").set_value(True).run()
    at.sidebar.number_input(key="manual_lat_key").set_value(10.0)
    at.sidebar.button(key="_set_home").click()
    at.run()
    assert_no_exception(at, "coordinate and click in one run")
    on_disk = json.loads(_prefs_path().read_text())["home_place"]
    assert on_disk["lat"] == 10.0
    assert on_disk["label"].startswith("Manual [10.0000, ")


def test_a_home_in_the_file_is_carried_into_a_fresh_session(prefs_on):
    _prefs_path().parent.mkdir(parents=True)
    _prefs_path().write_text(json.dumps({"home_place": {"label": "Petoskey, MI (US)", "lat": 45.3733, "lon": -84.9553}}))
    at = make_app(page="chart").run()
    assert_no_exception(at, "fresh")
    assert at.session_state["home_place"] == {"label": "Petoskey, MI (US)", "lat": 45.3733, "lon": -84.9553}
    assert not _here_now(at).disabled
    assert _home_caption(at) == "Home: Petoskey, MI (US) · 45.3733, -84.9553"


def test_the_manual_pair_is_a_home_too(prefs_on):
    at = make_app(page="chart").run()
    at.sidebar.button(key="_set_home").click().run()
    on_disk = json.loads(_prefs_path().read_text())["home_place"]
    assert on_disk["label"] == "Manual [43.7792, 11.2463]"
    assert _home_caption(at) == "Home: Manual [43.7792, 11.2463] · 43.7792, 11.2463"


def test_nothing_is_written_under_the_harness_guard(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    at = _florence_app().run()
    at.sidebar.button(key="_set_home").click().run()
    assert not _prefs_path().exists()
    # The session's copy still stands, and the button works from it.
    assert not _here_now(at).disabled


# --- The validator ---------------------------------------------------------

GOOD = {"label": "Florence, 16 (IT)", "lat": 43.7792, "lon": 11.2463}
BAD_SHAPES = {
    "not a mapping": ["Florence", 43.7792, 11.2463],
    "a string": "Florence",
    "None": None,
    "empty label": {**GOOD, "label": ""},
    "blank label": {**GOOD, "label": "   "},
    "label not a string": {**GOOD, "label": 12},
    "lat an int": {**GOOD, "lat": 43},
    "lon an int": {**GOOD, "lon": 11},
    "lat a bool": {**GOOD, "lat": True},
    "lat a string": {**GOOD, "lat": "43.7792"},
    "lat NaN": {**GOOD, "lat": float("nan")},
    "lon inf": {**GOOD, "lon": float("inf")},
    "lat 91": {**GOOD, "lat": 91.0},
    "lat -91": {**GOOD, "lat": -91.0},
    "lon 181": {**GOOD, "lon": 181.0},
    "missing lon": {"label": GOOD["label"], "lat": GOOD["lat"]},
    "missing label": {"lat": GOOD["lat"], "lon": GOOD["lon"]},
    "extra key": {**GOOD, "zone": "Europe/Rome"},
    "empty mapping": {},
}


def test_the_validator_admits_exactly_the_shape():
    assert engine.home_place_is_valid(GOOD)
    assert engine.preference_is_valid("home_place", GOOD)
    assert engine.home_place_is_valid({"label": "Pole", "lat": 90.0, "lon": -180.0})
    assert "home_place" in engine.PREFERENCE_KEYS


@pytest.mark.parametrize("shape", sorted(BAD_SHAPES))
def test_the_validator_refuses_each_malformed_shape(shape):
    assert not engine.home_place_is_valid(BAD_SHAPES[shape]), shape
    assert not engine.preference_is_valid("home_place", BAD_SHAPES[shape]), shape


@pytest.mark.parametrize("shape", ["lat an int", "lat 91", "extra key", "missing label", "a string", "lat a string"])
def test_a_malformed_home_in_the_file_is_dropped_and_the_app_opens(prefs_on, shape):
    """The loader drops the entry: the app opens on the defaults, the button
    stands disabled, and the entries beside it are kept. The launch writes
    the file back (its own count), so the dropped entry is gone from it."""
    _prefs_path().parent.mkdir(parents=True)
    _prefs_path().write_text(json.dumps({"home_place": BAD_SHAPES[shape], "_connection_rule": "Abu Ma'shar"}))
    at = make_app(page="chart").run()
    assert_no_exception(at, shape)
    assert "home_place" not in at.session_state
    assert at.session_state["_connection_rule"] == "Abu Ma'shar"
    assert _here_now(at).disabled
    assert _home_caption(at) is None
    on_disk = json.loads(_prefs_path().read_text())
    assert "home_place" not in on_disk
    assert on_disk["_connection_rule"] == "Abu Ma'shar"


def test_a_seeded_malformed_home_is_refused_by_the_button_too(prefs_on):
    """A seeded session_state wins over the file, so the button reads the
    session's copy through the same validator."""
    at = _florence_app()
    at.session_state["home_place"] = BAD_SHAPES["lat 91"]
    at.run()
    assert_no_exception(at, "seeded")
    assert _here_now(at).disabled
    assert _home_caption(at) is None


# --- Here & Now ------------------------------------------------------------

def test_here_and_now_casts_the_home_at_the_frozen_instant(prefs_on, monkeypatch):
    at = _florence_app().run()
    at.sidebar.button(key="_set_home").click().run()
    home = json.loads(_prefs_path().read_text())["home_place"]
    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "here and now")
    _no_streamlit_warning(at)
    assert at.session_state["date_input_key"] == "2026-09-17"
    assert at.session_state["time_input_key"] == time(14, 34, 56)
    assert at.session_state["time_standard_key"] == STANDARD
    assert at.session_state["manual_coords_key"] is True
    assert at.session_state["manual_lat_key"] == home["lat"]
    assert at.session_state["manual_lon_key"] == home["lon"]
    assert at.session_state["loaded_location"] == home
    # The widgets drawn from the keys.
    assert at.sidebar.text_input(key="date_input_key").value == "2026-09-17"
    assert at.sidebar.time_input(key="time_input_key").value == time(14, 34, 56)
    assert at.sidebar.selectbox(key="time_standard_key").value == STANDARD
    assert at.sidebar.toggle(key="manual_coords_key").value is True
    # The resolved box shows the home's label and its zone, not a bare pair.
    box = [s.value for s in at.sidebar.success][0]
    assert box.startswith(f"**{home['label']}**")
    assert box.endswith(" · Europe/Rome")
    assert any("UT 2026-09-17 12:34:56" in i.value for i in at.sidebar.info)
    # The strip reads the new chart.
    strip = _strip(at)
    assert strip.startswith("Unsaved chart · 2026-09-17 14:34:56")
    assert "Europe/Rome +02:00" in strip
    assert home["label"] in strip
    # Nothing was saved and nothing was written to the file by the cast.
    assert not _store_path().exists()
    assert json.loads(_prefs_path().read_text())["home_place"] == home


def test_here_and_now_across_the_dst_boundary(prefs_on, monkeypatch):
    at = _florence_app().run()
    at.sidebar.button(key="_set_home").click().run()
    _freeze(monkeypatch, JANUARY)
    _here_now(at).click().run()
    assert_no_exception(at, "january")
    assert at.session_state["date_input_key"] == "2026-01-17"
    assert at.session_state["time_input_key"] == time(13, 34, 56)
    assert at.session_state["time_standard_key"] == STANDARD
    assert any("UTC offset +01:00 (CET)" in i.value for i in at.sidebar.info)
    assert any("UT 2026-01-17 12:34:56" in i.value for i in at.sidebar.info)


def test_a_home_at_sea_is_cast_under_the_ocean_zone(prefs_on, monkeypatch):
    """A point at sea: the timezonefinder this app ships (8.3.0) answers an
    ocean zone (Etc/GMT+2 at 0.0, -30.0), and the sidebar's Standard branch
    asks it the same question, so the cast is Standard time under that
    zone and the instant is right."""
    at = make_app(page="chart")
    at.session_state["home_place"] = dict(AT_SEA)
    at.run()
    assert not _here_now(at).disabled
    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "at sea")
    _no_streamlit_warning(at)
    assert at.session_state["date_input_key"] == "2026-09-17"
    assert at.session_state["time_input_key"] == time(10, 34, 56)
    assert at.session_state["time_standard_key"] == STANDARD
    assert any("**Etc/GMT+2** · UTC offset -02:00" in i.value for i in at.sidebar.info)
    assert any("UT 2026-09-17 12:34:56" in i.value for i in at.sidebar.info)
    assert _strip(at).startswith("Unsaved chart · 2026-09-17 10:34:56 · Etc/GMT+2 -02:00 · At sea 0.00, -30.00")


def test_a_home_with_no_zone_is_cast_by_this_computers_clock(prefs_on, monkeypatch):
    """No zone at all (timezone_at answering None, which this app's
    timezonefinder does not do at sea but the callback and the sidebar
    both provide for): the instant is written as this computer's clock
    shows it, under Manual with that clock's offset -- the clock patched to
    a +05:30 zone so the test is deterministic. Under Manual the sidebar
    does not ask for the zone, so the chart is cast."""
    from timezonefinder import TimezoneFinder
    at = make_app(page="chart")
    at.session_state["home_place"] = dict(AT_SEA)
    at.run()
    monkeypatch.setattr(TimezoneFinder, "timezone_at", lambda self, **kw: None)
    _freeze(monkeypatch, NOON_ISH, local=timezone(timedelta(hours=5, minutes=30)))
    _here_now(at).click().run()
    assert_no_exception(at, "no zone")
    _no_streamlit_warning(at)
    assert at.session_state["date_input_key"] == "2026-09-17"
    assert at.session_state["time_input_key"] == time(18, 4, 56)
    assert at.session_state["time_standard_key"] == MANUAL
    assert at.session_state["utc_offset_key"] == 5.5
    assert at.sidebar.number_input(key="utc_offset_key").value == 5.5
    assert at.session_state["manual_lat_key"] == 0.0
    assert at.session_state["manual_lon_key"] == -30.0
    assert not [e.value for e in at.sidebar.error]
    assert any("UT 2026-09-17 12:34:56" in i.value for i in at.sidebar.info)
    assert _strip(at).startswith("Unsaved chart · 2026-09-17 18:04:56 · UTC+05:30 · At sea 0.00, -30.00")
    # A quarter-hour offset stands as it is.
    _freeze(monkeypatch, NOON_ISH, local=timezone(timedelta(hours=5, minutes=45)))
    _here_now(at).click().run()
    assert at.session_state["utc_offset_key"] == 5.75
    assert at.session_state["time_input_key"] == time(18, 19, 56)
    # A clock west of Greenwich crosses midnight the other way.
    _freeze(monkeypatch, datetime(2026, 9, 17, 2, 0, 0, tzinfo=timezone.utc),
            local=timezone(timedelta(hours=-10)))
    _here_now(at).click().run()
    assert at.session_state["date_input_key"] == "2026-09-16"
    assert at.session_state["time_input_key"] == time(16, 0, 0)
    assert at.session_state["utc_offset_key"] == -10.0


def test_a_clock_offset_outside_the_bounds_refuses_the_cast(prefs_on, monkeypatch):
    """No zone and an OS clock outside +-14 (only a broken TZ string gives
    one): nothing is written -- a Manual standard with the old offset left
    underneath would cast a wrong chart silently -- and one sentence
    stands in the notice slot beside the picker."""
    from timezonefinder import TimezoneFinder
    at = make_app(page="chart")
    at.session_state["home_place"] = dict(AT_SEA)
    at.run()
    before = {k: at.session_state[k] for k in ("date_input_key", "time_input_key", "time_standard_key",
                                                "manual_lat_key", "manual_lon_key")}
    monkeypatch.setattr(TimezoneFinder, "timezone_at", lambda self, **kw: None)
    _freeze(monkeypatch, NOON_ISH, local=timezone(timedelta(hours=15)))
    _here_now(at).click().run()
    assert_no_exception(at, "offset out of bounds")
    for key, value in before.items():
        assert at.session_state[key] == value, key
    assert "utc_offset_key" not in at.session_state
    assert "loaded_location" not in at.session_state
    assert [w.value for w in at.sidebar.warning] == [
        "This computer's clock has an offset outside ±14 hours, so Here & Now cast nothing."]
    assert _strip(at).startswith("Unsaved chart · 1240-05-23 14:30:00")
    # A clock inside the bounds casts, and the sentence goes with the cast.
    _freeze(monkeypatch, NOON_ISH, local=timezone(timedelta(hours=14)))
    _here_now(at).click().run()
    assert at.session_state["utc_offset_key"] == 14.0
    assert at.session_state["date_input_key"] == "2026-09-18"
    assert not [w.value for w in at.sidebar.warning]


def test_the_repeated_hour_is_cast_under_a_manual_offset(prefs_on, monkeypatch):
    """The sidebar's Standard branch refuses a clock time that happens twice
    (fall-back), so at that one hour the instant is written under Manual
    with the offset it actually has, and the chart is cast."""
    at = _florence_app().run()
    at.sidebar.button(key="_set_home").click().run()
    _freeze(monkeypatch, FALL_BACK)
    _here_now(at).click().run()
    assert_no_exception(at, "fall-back")
    assert at.session_state["date_input_key"] == "2026-10-25"
    assert at.session_state["time_input_key"] == time(2, 30, 0)
    assert at.session_state["time_standard_key"] == MANUAL
    assert at.session_state["utc_offset_key"] == 2.0
    assert not [e.value for e in at.sidebar.error]
    assert any("UT 2026-10-25 00:30:00" in i.value for i in at.sidebar.info)


def test_here_and_now_does_not_touch_the_target_or_save_anything(prefs_on, monkeypatch):
    at = _florence_app(page="timing")
    at.session_state["_target_mode"] = "Age"
    at.session_state["_target_age"] = 30
    at.run()
    at.sidebar.button(key="_set_home").click().run()
    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "timing")
    assert at.session_state["_target_mode"] == "Age"
    assert at.session_state["_target_age"] == 30
    assert not _store_path().exists()
    assert at.session_state["chart_picker"] == "-- New Chart --"


def test_a_loaded_record_then_here_and_now(prefs_on, monkeypatch):
    """The record in the file is untouched, the strip reads (modified), and
    Save under a new name writes the cast chart's fields."""
    at = make_app(date="1983-11-19", page="chart")
    # Seeded before the first run: a button drawn disabled takes no click.
    at.session_state["home_place"] = {"label": "Petoskey, MI (US)", "lat": 45.3733, "lon": -84.9553}
    at.run()
    [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0].set_value("Before").run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    assert_no_exception(at, "save")
    stored_before = _store_path().read_text()
    assert at.session_state["chart_picker"] == "Before"
    assert _strip(at).startswith("Before · 1983-11-19 14:30:00")

    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "here and now on a loaded record")
    assert _store_path().read_text() == stored_before
    assert at.session_state["chart_picker"] == "Before"
    assert _strip(at).startswith("Before (modified) · 2026-09-17 08:34:56")
    assert "America/Detroit -04:00" in _strip(at)
    assert any(c.value == "Edited since it was saved." for c in at.sidebar.caption)
    assert json.loads(stored_before)["Before"]["date_string"] == "1983-11-19"

    [t for t in at.sidebar.text_input if t.label.startswith("Chart name")][0].set_value("Cast now").run()
    [b for b in at.sidebar.button if "Save" in b.label][0].click().run()
    assert_no_exception(at, "save the cast chart")
    store = json.loads(_store_path().read_text())
    assert store["Before"] == json.loads(stored_before)["Before"]
    record = store["Cast now"]
    assert record["date_string"] == "2026-09-17"
    assert record["time_string"] == "08:34:56"
    assert record["time_standard"] == STANDARD
    assert record["location_query"] == "Petoskey, MI (US)"
    assert record["lat"] == pytest.approx(45.3733) and record["lon"] == pytest.approx(-84.9553)
    assert _strip(at).startswith("Cast now · 2026-09-17 08:34:56")


def test_a_legacy_record_notice_is_cleared_by_the_cast(prefs_on, monkeypatch):
    """A record saved before the time standard was stored leaves a warning
    that the standard must be checked; the cast writes a standard, so the
    warning goes with the rest of what the record said about itself."""
    _store_path().parent.mkdir(parents=True)
    _store_path().write_text(json.dumps({"Old": {"date_string": "1983-11-19", "time_string": "14:30:00",
                                                 "location_query": "Somewhere", "lat": 45.0, "lon": -84.0}}))
    at = _florence_app()
    at.session_state["home_place"] = dict(GOOD)
    at.run()
    at.sidebar.selectbox(key="chart_picker").select("Old").run()
    assert any("saved before the time standard" in w.value for w in at.sidebar.warning)
    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "cast over a legacy record")
    assert not any("saved before the time standard" in w.value for w in at.sidebar.warning)
    assert at.session_state["time_standard_key"] == STANDARD


def test_the_readings_question_outlives_the_cast(prefs_on, monkeypatch):
    """A record loaded under other readings poses a question -- open its
    readings, or keep the current ones -- that the cast leaves standing:
    the record was saved under other readings still, the picker still
    names it, and which readings the chart is read under is the reader's
    to say. The picker's caption then reads both lines."""
    _store_path().parent.mkdir(parents=True)
    _store_path().write_text(json.dumps({"Other": {
        "date_string": "1983-11-19", "time_string": "14:30:00", "time_standard": STANDARD,
        "location_query": "Somewhere", "lat": 45.0, "lon": -84.0,
        "readings": {"_connection_rule": "Abu Ma'shar"}}}))
    at = _florence_app()
    at.session_state["home_place"] = dict(GOOD)
    at.run()
    at.sidebar.selectbox(key="chart_picker").select("Other").run()
    assert any("saved under other readings" in i.value for i in at.sidebar.info)
    assert at.session_state["_readings_pending"] == "Other"
    _freeze(monkeypatch, NOON_ISH)
    _here_now(at).click().run()
    assert_no_exception(at, "cast over a record with a readings question")
    assert at.session_state["_readings_pending"] == "Other"
    assert any("saved under other readings" in i.value for i in at.sidebar.info)
    assert any(b.label == "Open saved readings" for b in at.sidebar.button)
    captions = [c.value for c in at.sidebar.caption]
    assert "Edited since it was saved." in captions
    assert "Saved with other readings." in captions
    assert _strip(at).startswith("Other (modified) · 2026-09-17 14:34:56")
    # Keep current readings answers it, as it did before the cast.
    [b for b in at.sidebar.button if b.label == "Keep current readings"][0].click().run()
    assert "_readings_pending" not in at.session_state
    assert at.session_state["date_input_key"] == "2026-09-17"


# --- The page text -----------------------------------------------------------

def test_the_sidebar_text_is_short_and_in_this_apps_voice():
    src = APP_PATH.read_text()
    for text in ("Cast a chart for the home place at this moment, by this computer's clock.",
                 "Set a home place under Birthplace first.",
                 "Keep the place resolved under Birthplace as the home that Here & Now casts a chart for.",
                 "Remove the home place; Here & Now is then disabled.",
                 "Resolve a place under Birthplace, then set it as home.",
                 "so Here & Now cast nothing.",
                 '"Home" if _home_now else "Set home"'):
        assert text in src
        assert len(text) <= 300
        assert "the app" not in text
    assert "Here & Now" in src
