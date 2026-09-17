"""Sources shown -- F12 of the independent UI review of 2026-09-16, under
the owner's ruling (option 2, not the full split).

The two-state control on the Sources page stays two-state and keeps its
stored values, "Course text" and "Course text and supplement": the harness
seeds them, the fixture's slots depend on them, and the engine compares
against them. What changes is the name the reader reads -- the radio, the
readings registry and the readings table all say "Sources shown", the radio
prints its two options as the sources they are through a format_func -- and
that every page whose CONTENT the setting changes now says so in one line
under its header, which was the review's real complaint: the setting was
remote from its effect.

See docs/SOURCES_SHOWN_2026-09-16.md.
"""
import ast

import pytest

from conftest import (APP_PATH, READING_DEPTHS, assert_no_exception,
                      find_page_widget, make_app, ui_source)

# The pages whose content the setting changes -- every page that tests
# READING_DEPTH, by the header each one carries.
SCOPED_PAGES = {
    "findings": "Findings",
    "dignities": "Dignities and places",
    "configurations": "Configurations",
    "lots": "Lots",
    "timing": "Timing",
    "releaser": "The releaser",
    "days": "Days and months",
    "fardar": "Fardar and ages",
    "reference": "Reference tables",
}
# The pages it does not change. Sources is where it is SET, and the Sources
# page's own tables do not move when it moves.
UNSCOPED_PAGES = ("chart", "victors", "sources")

COURSE_TEXT, WITH_SUPPLEMENT = READING_DEPTHS

SCOPE_LINES = {
    COURSE_TEXT: ("Sources shown: Sahl's course texts. Abu Ma'shar's supplement is off; "
                  "switch it on under Sources and readings."),
    WITH_SUPPLEMENT: "Sources shown: Sahl's course texts with Abu Ma'shar's supplement.",
}
DISPLAY = {COURSE_TEXT: "Sahl's course texts",
           WITH_SUPPLEMENT: "With Abu Ma'shar's supplement"}


def _app_tree():
    return ast.parse(APP_PATH.read_text())


def _sources_shown_radio_call():
    """The one _reading_radio call whose label is "Sources shown"."""
    calls = [node for node in ast.walk(_app_tree())
             if isinstance(node, ast.Call)
             and getattr(node.func, "id", None) == "_reading_radio"
             and node.args and isinstance(node.args[0], ast.Constant)
             and node.args[0].value == "Sources shown"]
    assert len(calls) == 1, f"expected one Sources shown radio, found {len(calls)}"
    return calls[0]


# --- The label and the values -------------------------------------------

def test_the_radio_is_labelled_sources_shown_and_keeps_the_stored_values():
    at = make_app(page="sources").run()
    assert_no_exception(at, "sources")
    radio = find_page_widget(at, "radio", "Sources shown")
    assert radio.label == "Sources shown"
    # The proto carries the FORMATTED options; the value is the stored one.
    assert list(radio.options) == [DISPLAY[COURSE_TEXT], DISPLAY[WITH_SUPPLEMENT]]
    assert radio.value == COURSE_TEXT
    assert [radio.format_func(v) for v in READING_DEPTHS] == list(radio.options)


def test_the_option_values_are_the_engine_s_own_and_are_unchanged(engine):
    assert engine["READING_DEPTH_OPTIONS"] == ("Course text", "Course text and supplement")
    assert list(engine["READING_DEPTH_OPTIONS"]) == READING_DEPTHS


def test_setting_the_radio_still_writes_the_stored_value():
    at = make_app(page="sources").run()
    find_page_widget(at, "radio", "Sources shown").set_value(WITH_SUPPLEMENT).run()
    assert at.session_state["_reading_depth"] == WITH_SUPPLEMENT


# --- The display labels ---------------------------------------------------

def test_the_radio_call_prints_its_two_options_as_the_sources_they_are():
    """Pinned on the call itself as well as on the rendered widget: the
    display strings are a decision about what the reader sees, and a later
    edit that dropped the format_func would leave the radio printing the
    stored values with no test to say so."""
    call = _sources_shown_radio_call()
    keywords = {k.arg: k.value for k in call.keywords}
    assert "format_func" in keywords, "the Sources shown radio should pass a format_func"
    shown = {node.value for node in ast.walk(keywords["format_func"])
             if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    assert DISPLAY[COURSE_TEXT] in shown, shown
    assert DISPLAY[WITH_SUPPLEMENT] in shown, shown
    # The values are named through the OPTIONS tuple, never typed out.
    assert "READING_DEPTH_OPTIONS" in ast.unparse(keywords["format_func"])


def test_reading_radio_takes_a_format_func_and_passes_it_through():
    """The pass-through is the whole change to the helper: every other
    radio calls it without one and must behave exactly as before."""
    definition = [node for node in ast.walk(_app_tree())
                  if isinstance(node, ast.FunctionDef) and node.name == "_reading_radio"]
    assert len(definition) == 1
    signature = definition[0].args
    assert signature.args[-1].arg == "format_func"
    assert signature.defaults[-1].value is None
    radio = [node for node in ast.walk(definition[0])
             if isinstance(node, ast.Call) and ast.unparse(node.func) == "st.radio"]
    assert len(radio) == 1
    passed = {k.arg: ast.unparse(k.value) for k in radio[0].keywords}
    assert passed.get("format_func") == "format_func or str"


# --- The registry, the table and the note --------------------------------

def test_the_registry_entry_is_named_sources_shown():
    src = ui_source()
    assert '("Sources shown", "reading_depth", "_reading_depth", READING_DEPTH_OPTIONS[0], "Sources and readings")' in src


def test_the_readings_table_names_it_sources_shown_and_prints_the_stored_value():
    at = make_app(page="sources").run()
    assert_no_exception(at, "sources")
    table = [df.value for df in at.main.dataframe if "In force" in df.value.columns][0]
    rows = {r["Reading"]: r for _, r in table.iterrows()}
    assert "Sources shown" in rows, list(rows)
    assert "Reading depth" not in rows
    assert rows["Sources shown"]["In force"] == COURSE_TEXT
    assert rows["Sources shown"]["Set on"] == "Sources and readings"


def test_the_readings_in_force_help_says_what_each_stored_value_means():
    at = make_app(page="sources").run()
    help_text = [s.help for s in at.main.subheader if s.value == "Readings in force"][0]
    assert "Sources shown" in help_text
    assert COURSE_TEXT in help_text and WITH_SUPPLEMENT in help_text


def test_the_readings_note_still_excludes_it():
    assert 'if l != "Sources shown"' in ui_source()
    at = make_app(page="dignities", switches={"domain": "Masha'allah"})
    at.session_state["_reading_depth"] = WITH_SUPPLEMENT
    at.run()
    assert_no_exception(at, "dignities, supplement and a changed domain")
    note = [c.value for c in at.main.caption if c.value.startswith("Readings in force that differ")]
    assert len(note) == 1, [c.value for c in at.main.caption]
    assert "Domain (hayz)" in note[0]
    assert "Sources shown" not in note[0]
    assert WITH_SUPPLEMENT not in note[0]


# --- The help of the radio -----------------------------------------------

def test_the_radio_help_describes_both_states_without_the_word_depth():
    at = make_app(page="sources").run()
    help_text = find_page_widget(at, "radio", "Sources shown").help
    assert "depth" not in help_text.lower()
    assert help_text.startswith(DISPLAY[COURSE_TEXT] + ":")
    assert DISPLAY[WITH_SUPPLEMENT] + ":" in help_text
    # What each state does: whose tables are shown, and where the
    # Configurations page keeps Abu Ma'shar's.
    assert "its own tab on the Configurations" in help_text
    assert "folds his tab into the topic blocks" in help_text


# --- The scope line ------------------------------------------------------

@pytest.mark.parametrize("page", sorted(SCOPED_PAGES))
@pytest.mark.parametrize("state", READING_DEPTHS)
def test_every_page_the_setting_changes_carries_the_scope_line(page, state):
    at = make_app(page=page)
    at.session_state["_reading_depth"] = state
    at.run()
    assert_no_exception(at, f"{page}, {state}")
    captions = [c.value for c in at.main.caption]
    assert SCOPE_LINES[state] in captions, f"{page}, {state}: {captions[:4]}"
    assert SCOPE_LINES[READING_DEPTHS[1 - READING_DEPTHS.index(state)]] not in captions


@pytest.mark.parametrize("page", sorted(SCOPED_PAGES))
@pytest.mark.parametrize("state", READING_DEPTHS)
def test_the_scope_line_follows_the_strip_under_the_header(page, state):
    at = make_app(page=page)
    at.session_state["_reading_depth"] = state
    at.run()
    captions = [c.value for c in at.main.caption]
    assert captions[0].startswith("Unsaved chart · "), captions[0]   # the strip
    where = captions.index(SCOPE_LINES[state])
    # After the strip, and inside the header block: at most the page's own
    # opening sentence stands between the two.
    assert 1 <= where <= 2, f"{page}, {state}: the scope line is caption {where}"


@pytest.mark.parametrize("page", UNSCOPED_PAGES)
@pytest.mark.parametrize("state", READING_DEPTHS)
def test_the_pages_the_setting_does_not_change_carry_no_scope_line(page, state):
    at = make_app(page=page)
    at.session_state["_reading_depth"] = state
    at.run()
    assert_no_exception(at, f"{page}, {state}")
    captions = [c.value for c in at.main.caption]
    for line in SCOPE_LINES.values():
        assert line not in captions, f"{page} should carry no scope line"


def test_the_scope_line_is_one_helper_called_from_each_scoped_page():
    """One helper, so the sentence cannot drift page by page."""
    tree = _app_tree()
    calling = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("page_"):
            if any(isinstance(inner, ast.Call) and getattr(inner.func, "id", None) == "_sources_scope_line"
                   for inner in ast.walk(node)):
                calling.add(node.name)
    assert calling == {f"page_{page}" for page in SCOPED_PAGES}, sorted(calling)
    helper = [node for node in ast.walk(tree)
              if isinstance(node, ast.FunctionDef) and node.name == "_sources_scope_line"]
    assert len(helper) == 1 and not helper[0].args.args, "the line is the same on every page"


# --- The old name is gone ------------------------------------------------

def test_the_app_no_longer_says_reading_depth_anywhere():
    """Label, help, caption, comment: the name the review objected to is
    off the file entirely, so a later edit cannot reintroduce it quietly."""
    source = APP_PATH.read_text()
    hits = [(n, line.strip()) for n, line in enumerate(source.split("\n"), 1)
            if "reading depth" in line.lower()]
    assert not hits, hits
