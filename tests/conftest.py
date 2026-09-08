"""Regression harness for Executable/app.py.

The app is one 6,500-line file: engine first, Streamlit UI from the marker
``# 4. STREAMLIT UI INTEGRATION`` onward. Two ways in:

* ``engine`` -- the engine half executed as a plain module, so constants and
  evaluators can be inspected without a Streamlit run.
* ``make_app()`` -- ``streamlit.testing.v1.AppTest`` driving the whole script
  headless: no browser, no port. One call renders ONE page (Streamlit runs
  the script once per page), so tests parametrise over pages.

The app is located relative to this file, so the suite runs from any
checkout or CI runner. (It used to hard-code the developer's absolute path
to dodge a stale ``app.py`` one directory up; that file is gone.)
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from collections import Counter
from datetime import time
from pathlib import Path

import pytest

EXECUTABLE_DIR = Path(__file__).resolve().parents[1]
APP_PATH = EXECUTABLE_DIR / "app.py"
UI_MARKER = "# 4. STREAMLIT UI INTEGRATION"
FIXTURE_DIR = Path(__file__).parent / "fixtures"
TABLES_FIXTURE = FIXTURE_DIR / "tables.json"

# Saved charts live in the user's XDG data dir. Point them at a scratch
# directory so a test run can never read or write the real file.
os.environ.setdefault("XDG_DATA_HOME", str(Path(__file__).parent / ".xdg-scratch"))

# --- Charts and pages ----------------------------------------------------
# All Florence, LMT, 14:30. Between them they populate the conditional
# tables that are empty on the default chart.
CHARTS = {
    "1240-05-23": "the app default",
    "1240-05-25": "Reception by nature (Sun/Moon in aversion)",
    "1240-05-26": "Reflection of Light and Favor & Recompense",
    "1240-09-18": "dense Returning and Prevented connections",
    "1240-10-05": "retreating quadrants, a retrograde planet",
    # Added 2026-09-07 when the Egyptian-bounds fix emptied Favor & Recompense
    # on 1240-05-26 (its only row had come from the transposed Gemini bound).
    # The Sun at 21 Capricorn (degree 22, a Well degree) with Saturn, its
    # domicile lord, connected -- a Saturn-helped Favor, which no other chart
    # has; the others' Favor rows were all Jupiter-helped.
    "1240-01-04": "Favor & Recompense (Sun in a Well, favored by Saturn)",
}
FLORENCE = (43.7792, 11.2463)
LOCAL_TIME = time(14, 30)

# url_path of every st.Page, in navigation order. The Configurations page
# has a three-way view control; each view is treated as its own page.
PAGES = ["chart", "dignities", "configurations", "lots", "victors", "timing", "sources"]
CONFIG_VIEWS = ["Sahl (course text)", "Abu Ma'shar (supplement)", "Both"]

# The six configurable readings. Since the 2026-09-06 UI restructure each
# control renders on the page and table it affects, and the engine reads
# its value at the top level from a store key that _persist() keeps across
# navigation. Tests set the STORE key through session_state before the run
# (the widget-first read at the top level falls back to it); the widget
# itself is located by label prefix on its page so a reworded or moved
# control fails loudly.
SWITCHES = {
    # name: (store key, alternatives, page, view, widget kind, label prefix)
    "connection": ("_connection_rule", ["Sahl", "Abu Ma'shar"], "configurations", "Both", "radio", "Connection test"),
    "five_degree": ("_five_degree_all_cusps", [False, True], "configurations", "Both", "checkbox", "Five-degree carryover"),
    "eastern": ("_eastern_rule", ["hemisphere", "VII.2 band"], "configurations", "Both", "radio", "VII.6, 27/45"),
    "moon_rays": ("_moon_rays_15", [False, True], "chart", None, "checkbox", "Moon under the rays"),
    "domain": ("_domain_rule", ["Abu Ma'shar", "Masha'allah"], "dignities", None, "radio", "Domain (hayz)"),
    "lot_cusp": ("_lot_house_cusp", ["whole-sign place", "quadrant cusp"], "lots", None, "radio", "House-based Lots"),
}


def page_slots():
    """Every (page, view) a test should render. view is None except for
    the Configurations page."""
    slots = []
    for page in PAGES:
        if page == "configurations":
            slots.extend((page, view) for view in CONFIG_VIEWS)
        else:
            slots.append((page, None))
    return slots


def slot_name(page, view):
    return page if view is None else f"{page}/{view}"


# --- The app under AppTest ----------------------------------------------

def make_app(date="1240-05-23", page=None, view=None, switches=None, timeout=60):
    """Build an AppTest for one chart and one page, unrun.

    Sidebar inputs that carry a session_state key are set through the key
    (that is how the app's own saved-chart loader does it). The page is
    selected the way st.navigation selects it: by the hash of the
    st.Page url_path, which is what AppTest.switch_page() computes for
    file-based pages -- there is no public equivalent for function pages.
    """
    from streamlit.testing.v1 import AppTest
    from streamlit.util import calc_hash

    at = AppTest.from_file(str(APP_PATH), default_timeout=timeout)
    at.session_state["manual_coords_key"] = True
    at.session_state["manual_lat_key"] = FLORENCE[0]
    at.session_state["manual_lon_key"] = FLORENCE[1]
    at.session_state["date_input_key"] = date
    at.session_state["time_input_key"] = LOCAL_TIME
    if view is not None:
        at.session_state["configurations_view"] = view
    if page is not None:
        at._page_hash = calc_hash(page)
    if switches:
        apply_switches(at, switches)
    return at


def find_page_widget(at, kind, label_prefix):
    """The one widget of `kind` on the rendered page whose label starts
    with `label_prefix`."""
    widgets = getattr(at.main, kind)
    hits = [w for w in widgets if w.label.startswith(label_prefix)]
    assert len(hits) == 1, (
        f"expected exactly one page {kind} labelled '{label_prefix}...', "
        f"found {[w.label for w in widgets]}")
    return hits[0]


def apply_switches(at, switches):
    """switches: {name: value} using the names in SWITCHES. Sets the store
    key the engine reads; call before at.run()."""
    for name, value in switches.items():
        store, alternatives = SWITCHES[name][0], SWITCHES[name][1]
        assert value in alternatives, f"{name}: {value!r} not in {alternatives}"
        at.session_state[store] = value
    return at


def assert_no_exception(at, context=""):
    if len(at.exception):
        details = "\n\n".join(e.value for e in at.exception)
        pytest.fail(f"{context}: the app raised\n{details}")


# --- Table identity -----------------------------------------------------

def table_inventory(at):
    """Every st.dataframe on the rendered page, in order, as
    (heading, columns). The heading is the nearest preceding st.subheader
    or expander label -- a "Sources and editorial notes" expander follows
    its table and is not a heading for the next one."""
    inventory = []
    heading = None
    for node in at.main:          # Block.__iter__ walks the tree in order
        kind = getattr(node, "type", None)
        if kind == "subheader":
            heading = node.value
        elif kind == "expander" and node.label != "Sources and editorial notes":
            heading = node.label
        elif kind == "dataframe":
            inventory.append((heading or "(no heading)", list(node.value.columns)))
    return inventory


def _key(entry):
    heading, columns = entry
    return (heading, tuple(columns))


def describe_table_diff(expected, actual):
    """A readable account of which tables went missing, appeared, or
    changed multiplicity. Compares multisets, not counts."""
    exp, act = Counter(map(_key, expected)), Counter(map(_key, actual))
    lines = []
    for key in sorted(set(exp) | set(act)):
        e, a = exp[key], act[key]
        if e == a:
            continue
        heading, columns = key
        if a == 0:
            lines.append(f"  MISSING   {heading!r} (expected {e}x) columns={list(columns)}")
        elif e == 0:
            lines.append(f"  UNEXPECTED {heading!r} ({a}x) columns={list(columns)}")
        else:
            lines.append(f"  COUNT     {heading!r}: expected {e}x, rendered {a}x")
    return "\n".join(lines)


def dump_fixture(data):
    """One table per line, so a diff of the fixture reads as which table
    appeared or went missing."""
    out = ["{"]
    dates = list(data)
    for i, d in enumerate(dates):
        out.append(f' "{d}": {{')
        slots = list(data[d])
        for j, s in enumerate(slots):
            out.append(f"  {json.dumps(s, ensure_ascii=False)}: [")
            rows = data[d][s]
            for k, row in enumerate(rows):
                out.append("   " + json.dumps(row, ensure_ascii=False) + ("," if k < len(rows) - 1 else ""))
            out.append("  ]" + ("," if j < len(slots) - 1 else ""))
        out.append(" }" + ("," if i < len(dates) - 1 else ""))
    out.append("}")
    return "\n".join(out) + "\n"


def load_table_fixture():
    if not TABLES_FIXTURE.exists():
        pytest.fail(f"{TABLES_FIXTURE} is missing; run  UPDATE_TABLE_FIXTURE=1 pytest tests/test_pages_render.py")
    return json.loads(TABLES_FIXTURE.read_text())


# --- The engine half as a module ----------------------------------------

def app_source():
    return APP_PATH.read_text()


def engine_source():
    src = app_source()
    idx = src.index(UI_MARKER)
    return src[:idx]


def ui_source():
    src = app_source()
    return src[src.index(UI_MARKER):]


@pytest.fixture(scope="session")
def engine():
    """The pre-UI half of app.py executed as a module namespace."""
    src = engine_source()
    ns = {"__file__": str(APP_PATH), "__name__": "almuten_engine_under_test"}
    exec(compile(src, str(APP_PATH), "exec"), ns)
    return ns


def function_source(name):
    """Source text of one top-level function in the engine half, by AST --
    inspect.getsource cannot see exec'd code."""
    src = engine_source()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    raise LookupError(f"no top-level function {name!r} in the engine half")


def cited_paragraphs(text, lo, hi):
    """Paragraph numbers between lo and hi that appear as trailing
    citations in string literals: '... (83)', '(93, 99)', '(106, 119-123)'.
    Docstrings and comments cite ranges too, so this only reads quoted
    strings."""
    found = set()
    for literal in re.findall(r"""(?:'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")""", text):
        for group in re.findall(r"\(([^()]*)\)", literal):
            # leading run of numbers: "84; ...", "93, 99", "106, 119-123"
            m = re.match(r"\s*(\d{2,3}(?:\s*[-,;]\s*\d{2,3})*)", group)
            if not m:
                continue
            for n in map(int, re.findall(r"\d+", m.group(1))):
                if lo <= n <= hi:
                    found.add(n)
    return found


NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}


def prose_number(pattern, text=None):
    """The number word captured by `pattern` (one group) in the UI source.
    Fails loudly if the phrase has been reworded, which is the point: a
    prose count and the structure it describes must be updated together."""
    text = ui_source() if text is None else text
    m = re.search(pattern, text)
    assert m, f"prose phrase not found in the UI source: /{pattern}/ -- reworded? update the test with it"
    word = m.group(1).lower()
    return NUMBER_WORDS.get(word) if word in NUMBER_WORDS else int(word)
