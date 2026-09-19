"""The renderer contract of the readability branch A (2026-09-17):
``_prose()``, ``_finding``'s new layers (summary, qualifications, detail,
note_sections, notes_title), ``_notes_expander``, and ``_tick_grid``'s
``key=`` and ``note_sections``.

The helpers are exercised in a minimal Streamlit script built from their
own source, lifted out of app.py by AST, so that the contract is tested in
isolation from any page: every layer renders in the stated order; both
early returns are what they were; a notes expander carries the book icon
and never an st.dataframe; the detail selectbox starts unselected and
renders the panel for a chosen row; a tick grid keeps its old key when
key= is omitted.
"""
from __future__ import annotations

import ast
import re

import pytest

from conftest import (APP_PATH, NOTES_EXPANDER_ICON, NOTES_EXPANDER_LABEL, assert_no_exception,
                      table_inventory, ui_source)

HELPERS = ("PROSE_WIDTH", "_prose", "NOTES_ICON", "NOTES_TITLE", "_display_result", "_display_rows",
           "_note_sections", "_notes_expander",
           "_slug", "_detail_selector", "_finding", "_absent", "_WIDE_TEXT_COLUMNS", "_wide_text_columns",
           "_YES_NO_COLUMNS", "_yes_no_columns", "_MEDIUM_TEXT_COLUMNS", "_medium_text_columns",
           "_PARAGRAPH", "_CITATION_LOCATOR", "_tick_grid", "_row_detail", "_rows_height")


def _segments(names):
    """The source of each top-level def or assignment in app.py, by AST."""
    src = APP_PATH.read_text()
    tree = ast.parse(src)
    found = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            found[node.name] = ast.get_source_segment(src, node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    found[target.id] = ast.get_source_segment(src, node)
    missing = [n for n in names if n not in found]
    assert not missing, f"not found at the top level of app.py: {missing}"
    return "\n\n".join(found[n] for n in names)


SCRIPT_HEAD = """import re
import streamlit as st
import pandas as pd

class YearsOutcome:
    pass

class UnresolvedResult:
    pass

"""

ROWS = [{"Name": "Alpha", "Value": "one", "Ground": "the first ground"},
        {"Name": "Beta", "Value": "two", "Ground": "the second ground"},
        {"Name": "Alpha", "Value": "three", "Ground": "the third ground"}]

DRIVER = '''
def _detail(row):
    st.markdown("Detail for " + row["Name"] + ": " + row["Ground"])

gap = []
_finding(gap, "A full finding", "Source A, passage 1", ROWS,
         glance="The glance.",
         summary="The summary sentence.",
         qualifications=["**First qualification.** Its statement.", "**Second qualification.** Its statement."],
         caption="The caption under the table.",
         detail=_detail, detail_key="Name",
         notes="The one-string notes.",
         note_sections=[("First heading", "First body."), ("Second heading", "| a | b |\\n|---|---|\\n| 1 | 2 |")])
_finding(gap, "An empty finding", "Source A, passage 2", [], glance="Empty.")
_finding(gap, "A bounded search", "Source A, passage 3", [], absent="Nothing within the bound.")
_absent(gap)
_notes_expander("A sibling topic", [("Sibling heading", "Sibling body.")])
_finding(gap, "A titled notes finding", "Source A, passage 4", ROWS[:1],
         notes_title="Grounds and passages", note_sections=[("Only heading", "Only body.")])
'''

TICK_ROWS = [{"Planet": "Sun", "Strength Testimonies": "x", "Count": 1,
              "Labels": ["78 excellent place (78)"], "Testimonies": [{"n": "78", "sentence": "s", "facts": ["Fact: v"]}]}]

TICK_DRIVER = '''
COLS = [('78', '78 excellent place')]
_tick_grid([], "Strength of the Planets", "Sahl, The Introduction Ch. 3, 78-88", TICK_ROWS,
           "Strength Testimonies", COLS, glance="g", note_sections=[("Tick heading", "Tick body.")])
_tick_grid([], "Strength of the Planets", "Sahl, The Introduction Ch. 3, 78-88", TICK_ROWS,
           "Strength Testimonies", COLS, key="explicit_key_grid", notes="Old-style notes.")
'''


@pytest.fixture(scope="module")
def script(tmp_path_factory):
    path = tmp_path_factory.mktemp("contract") / "finding_contract_app.py"
    path.write_text(SCRIPT_HEAD + _segments(HELPERS) + f"\n\nROWS = {ROWS!r}\n" + DRIVER)
    return path


@pytest.fixture(scope="module")
def tick_script(tmp_path_factory):
    path = tmp_path_factory.mktemp("contract") / "tick_contract_app.py"
    path.write_text(SCRIPT_HEAD + _segments(HELPERS) + f"\n\nTICK_ROWS = {TICK_ROWS!r}\n" + TICK_DRIVER)
    return path


def _run(path, **state):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(path), default_timeout=30)
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert_no_exception(at, path.name)
    return at


def _kinds(at):
    """(type, text) for every element in the main block, in order, the
    expanders by label."""
    out = []
    for node in at.main:
        kind = getattr(node, "type", None)
        if kind in ("expander", "status"):
            out.append((kind, node.label))
        elif kind in ("subheader", "caption", "markdown"):
            out.append((kind, node.value))
        elif kind in ("dataframe", "selectbox"):
            out.append((kind, getattr(node, "label", "")))
    return out


def prose_width():
    return int(re.search(r"^PROSE_WIDTH = (\d+)$", ui_source(), re.M).group(1))


def PROSE_WIDTH_IN_TREE(at):
    """The one pixel width every flex container in the tree declares."""
    widths = set()

    def walk(block):
        for child in block.children.values():
            if getattr(child, "type", None) == "flex_container" and child.proto.HasField("width_config"):
                widths.add(child.proto.width_config.pixel_width)
            if hasattr(child, "children"):
                walk(child)
    walk(at.main)
    assert len(widths) == 1, widths
    return widths.pop()


# --- _prose and the constants -------------------------------------------

def test_prose_is_a_native_container_at_prose_width():
    src = ui_source()
    assert re.search(r"^PROSE_WIDTH = \d+$", src, re.M)
    assert "return st.container(width=PROSE_WIDTH)" in src
    for forbidden in ("unsafe_allow_html=True", "st.html(", "<style"):
        assert forbidden not in src, forbidden
    assert NOTES_EXPANDER_ICON == ":material/menu_book:" and 'NOTES_ICON = ":material/menu_book:"' in src
    assert 'NOTES_TITLE = "Sources and editorial notes"' in src and NOTES_EXPANDER_LABEL == "Sources and editorial notes"


# --- _finding: the layers in order ----------------------------------------

def test_every_layer_renders_in_the_contracts_order(script):
    at = _run(script)
    kinds = _kinds(at)
    start = kinds.index(("subheader", "A full finding"))
    end = kinds.index(("subheader", "A titled notes finding"))
    layers = kinds[start:end]
    expected_head = [("subheader", "A full finding"),
                     ("caption", "Source A, passage 1"),
                     ("markdown", "The summary sentence."),
                     ("markdown", "**First qualification.** Its statement."),
                     ("markdown", "**Second qualification.** Its statement."),
                     ("dataframe", ""),
                     ("caption", "The caption under the table."),
                     ("selectbox", "Read details for"),
                     ("status", NOTES_EXPANDER_LABEL),
                     ("markdown", "The one-string notes."),
                     ("markdown", "**First heading**"),
                     ("markdown", "First body."),
                     ("markdown", "**Second heading**"),
                     ("markdown", "| a | b |\n|---|---|\n| 1 | 2 |")]
    assert layers[:len(expected_head)] == expected_head, layers
    # The one bounded search keeps its heading and its scope caption; the
    # ordinary empty finding is named in the bucket line; the sibling
    # expander and the retitled notes expander both carry the book icon.
    rest = layers[len(expected_head):]
    assert rest == [("subheader", "A bounded search"),
                    ("caption", "Nothing within the bound."),
                    ("caption", "Not present in this chart: An empty finding."),
                    ("status", "A sibling topic"),
                    ("markdown", "**Sibling heading**"),
                    ("markdown", "Sibling body.")], rest
    assert kinds[end:] == [("subheader", "A titled notes finding"),
                           ("caption", "Source A, passage 4"),
                           ("dataframe", ""),
                           ("status", "Grounds and passages"),
                           ("markdown", "**Only heading**"),
                           ("markdown", "Only body.")], kinds[end:]
    for node in at.main:
        if getattr(node, "type", None) == "status":
            assert node.icon == NOTES_EXPANDER_ICON, node.label
    assert [h.value for h in at.main.subheader] == ["A full finding", "A bounded search", "A titled notes finding"]


def test_the_notes_expander_holds_no_dataframe_and_the_walker_keys_tables_under_the_finding(script):
    at = _run(script)
    inventory = table_inventory(at)
    assert inventory == [("A full finding", ["Name", "Value", "Ground"]),
                         ("A titled notes finding", ["Name", "Value", "Ground"])]
    for node in at.main:
        if getattr(node, "type", None) == "status":
            inside = [getattr(child, "type", None) for child in node]
            assert "dataframe" not in inside, node.label


def test_the_bodies_of_the_notes_and_the_summary_are_at_reading_width(script):
    """Every markdown of the summary, the qualifications and the note
    sections stands inside a flex container of width PROSE_WIDTH; the
    table, the captions and the selectbox do not."""
    at = _run(script)
    inside = set()

    def walk(block, width):
        for child in block.children.values():     # direct children; Block.__iter__ walks the whole tree
            kind = getattr(child, "type", None)
            if kind == "flex_container":
                w = child.proto.width_config.pixel_width if child.proto.HasField("width_config") else 0
                walk(child, w or width)
            elif kind == "markdown" and width:
                inside.add(child.value)
            elif hasattr(child, "children"):
                walk(child, width)
    walk(at.main, 0)
    assert PROSE_WIDTH_IN_TREE(at) == prose_width()
    for text in ("The summary sentence.", "**First qualification.** Its statement.", "First body.",
                 "**First heading**", "Sibling body.", "Only body."):
        assert text in inside, text
    assert "Detail for" not in " ".join(inside)


def test_the_detail_selectbox_starts_unselected_and_renders_the_chosen_row(script):
    at = _run(script)
    boxes = [s for s in at.main.selectbox if s.label == "Read details for"]
    assert len(boxes) == 1
    box = boxes[0]
    assert box.value is None and box.index is None
    assert box.key == "a_full_finding_detail"
    assert box.placeholder == "Select a row to read its grounds and source passages"
    # Two rows share the name Alpha, so every option is prefixed with its
    # 1-based row number; the order is the table's.
    assert box.options == ["1. Alpha", "2. Beta", "3. Alpha"]
    assert not [m.value for m in at.main.markdown if m.value.startswith("Detail for")]
    box.select("3. Alpha")
    at.run()
    assert_no_exception(at, "after a selection")
    assert [m.value for m in at.main.markdown if m.value.startswith("Detail for")] == ["Detail for Alpha: the third ground"]


def test_a_stale_or_garbage_selection_renders_no_panel_and_raises_nothing(script):
    at = _run(script, a_full_finding_detail="Not a row")
    assert not [m.value for m in at.main.markdown if m.value.startswith("Detail for")]
    assert at.main.selectbox[0].value is None


# --- _tick_grid: key= and note_sections ------------------------------------

def test_tick_grid_keeps_its_old_key_without_key_and_takes_one_with_it(tick_script):
    at = _run(tick_script)
    keys = [n.key for n in at.main if getattr(n, "type", None) == "dataframe" and getattr(n, "key", None)]
    assert keys == ["strength_of_the_planets_grid", "explicit_key_grid"]
    statuses = [(n.label, n.icon) for n in at.main if getattr(n, "type", None) == "status"]
    assert statuses == [(NOTES_EXPANDER_LABEL, NOTES_EXPANDER_ICON), (NOTES_EXPANDER_LABEL, NOTES_EXPANDER_ICON)]
    markdown = [m.value for m in at.main.markdown]
    assert "**Tick heading**" in markdown and "Tick body." in markdown and "Old-style notes." in markdown
    # The answer key's own table is the only one inside an expander, and the
    # walker keys both grids under the grid's subheader as before.
    assert table_inventory(at) == [("Strength of the Planets", ["Planet", "78 excellent place", "Count"]),
                                   ("Answer key: testimonies in words", ["Planet", "Strength Testimonies", "Count"]),
                                   ("Strength of the Planets", ["Planet", "78 excellent place", "Count"]),
                                   ("Answer key: testimonies in words", ["Planet", "Strength Testimonies", "Count"])]


def test_no_finding_call_in_app_passes_a_dataframe_into_notes():
    """The bodies handed to note_sections and _notes_expander are Markdown
    strings; by source, no st.dataframe call stands inside a notes
    expander anywhere in the UI half (the walker keeps such a table out of
    the fixture, so this is the guard)."""
    src = ui_source()
    tree = ast.parse(APP_PATH.read_text())

    def is_notes_with(node):
        if not (isinstance(node, ast.With) and node.items):
            return False
        call = node.items[0].context_expr
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "expander"):
            return False
        for kw in call.keywords:
            if kw.arg == "icon":
                value = kw.value
                return (isinstance(value, ast.Constant) and value.value == NOTES_EXPANDER_ICON) or \
                       (isinstance(value, ast.Name) and value.id == "NOTES_ICON")
        return False

    offenders = []
    for node in ast.walk(tree):
        if is_notes_with(node):
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "dataframe"):
                    offenders.append(inner.lineno)
    # The Chart page's sign-category lookup table stands in a book-icon
    # expander by design (it is a lookup, not a finding's table): that one
    # expander is the only allowed site, and it is not a notes expander
    # created by _finding, _tick_grid or _notes_expander.
    allowed = [n for n, line in enumerate(APP_PATH.read_text().splitlines(), 1)
               if "Sahl's sign categories for this chart's points" in line]
    assert all(any(abs(o - a) < 12 for a in allowed) for o in offenders), offenders
    assert "st.dataframe" not in src[src.index("def _note_sections"):src.index("def _slug")]
