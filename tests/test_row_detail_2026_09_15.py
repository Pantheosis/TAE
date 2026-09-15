"""Why a tick fired: row detail on the Strength and Weakness grids
(item 12 of UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md, scoped to
those two grids; docs/UI_CHANGES_2026-09-15_row_detail.md).

The engine's two Sahl evaluators (The Introduction Ch. 3, 78-88 and 91-100)
each gain one key per row, ``Testimonies``: a list of ``{"n", "sentence",
"facts"}`` restating each label -- its paragraph number, its own words, and
the chart values the branch tested, as ``"Fact: Value"`` strings. Every
existing key and value stays byte-identical to main's, proved here by
running both evaluators on main's engine and on this one over the six
fixture charts. The structure cannot drift from the labels: for every row
the ``n`` list equals the paragraph numbers ``_tick_grid`` parses from the
labels with its own regex, in order.

The page: each tick grid is selectable (single row, rerun), keyed by its
title, and stands with its answer key, its notes and the panel in one
``@st.fragment`` per grid. A selection draws, under the grid, the planet's
name and count, then one block per ticked testimony: the sentence's locator,
the sentence as the answer key words it, and the facts. With no selection
nothing is drawn, so ``tests/fixtures/tables.json`` is unchanged.

AppTest cannot click a dataframe, but a selection can be seeded through the
widget's own key (``st.session_state[key] = {"selection": {"rows": [i]}}``,
the schema Streamlit documents on DataframeState), which is how the panel
is rendered and read here.
"""
from __future__ import annotations

import ast
import re
import subprocess
from datetime import date

import pytest

from conftest import (CHARTS, EXECUTABLE_DIR, FLORENCE, LOCAL_TIME, READING_DEPTHS, TABLES_FIXTURE,
                      assert_no_exception, make_app, ui_source)

# _tick_grid's own regex: the first "(nn" followed by ; , or ) in a label.
PARAGRAPH = re.compile(r'\((\d{2,3})(?=[;,)])')
PANEL_HEADING = re.compile(r"^(\w+): (\d+) of (\d+) testimonies$")
LOCATOR = "Sahl, The Introduction Ch. 3"
STRENGTH_KEY = "strength_of_the_planets_grid"
WEAKNESS_KEY = "weakness_of_the_planets_grid"
STRENGTH_NUMBERS = {str(n) for n in range(78, 89)}
WEAKNESS_NUMBERS = {str(n) for n in range(91, 101)}
EVALUATORS = ("evaluate_strength_of_planets", "evaluate_weakness_of_planets")
DEFAULT = "1240-05-23"


# --- The charts, the way the sidebar computes them --------------------------

def _jd(ns, day):
    hour = LOCAL_TIME.hour + LOCAL_TIME.minute / 60.0
    return ns["civil_local_to_jd_ut"](day.year, day.month, day.day, hour, FLORENCE[1] / 15.0)


def _pool(ns, day):
    jd = _jd(ns, day)
    chart = ns["calculate_traditional_chart_jd"](jd, *FLORENCE)
    p, cusps, sect = chart["planetary_data"], chart["houses"], chart["sect"]
    essential = ns["evaluate_essential_dignities"](p, sect)
    accidental = ns["evaluate_accidental_dignities"](p, cusps, sect, jd, chart["armc"],
                                                     chart["obliquity"], chart["geo_lat"])
    return {"chart": chart, "p": p, "cusps": cusps, "sect": sect, "asc": chart["ascendant"],
            "essential": essential, "accidental": accidental}


def _rows(ns, day_text):
    pool = _pool(ns, date.fromisoformat(day_text))
    strength = ns["evaluate_strength_of_planets"](pool["p"], pool["essential"], pool["accidental"],
                                                  pool["asc"], pool["sect"], pool["cusps"])
    weakness = ns["evaluate_weakness_of_planets"](pool["p"], pool["essential"], pool["accidental"],
                                                  pool["asc"], pool["sect"])
    return {"evaluate_strength_of_planets": strength, "evaluate_weakness_of_planets": weakness}, pool


def _without(rows):
    return [{k: v for k, v in r.items() if k != "Testimonies"} for r in rows]


def _main_engine_namespace():
    """main's engine.py, executed into a namespace of its own."""
    for ref in ("origin/main", "main"):
        try:
            source = subprocess.run(["git", "show", f"{ref}:engine.py"], cwd=EXECUTABLE_DIR,
                                    capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        if source.returncode == 0 and "def evaluate_strength_of_planets(" in source.stdout:
            namespace = {"__file__": str(EXECUTABLE_DIR / "engine.py"),
                         "__name__": "main_engine_under_test"}
            exec(compile(source.stdout, str(EXECUTABLE_DIR / "engine.py"), "exec"), namespace)
            return namespace
    return None


@pytest.fixture(scope="module")
def main_engine():
    ns = _main_engine_namespace()
    if ns is None:
        pytest.skip("main's engine.py is not in this checkout (a shallow clone)")
    return ns


# --- A. The differential: every existing key and value is main's -----------

@pytest.mark.parametrize("day_text", list(CHARTS))
@pytest.mark.parametrize("name", EVALUATORS)
def test_the_rows_equal_mains_once_testimonies_is_dropped(engine, main_engine, day_text, name):
    """Both evaluators, six charts: drop the new key and the rows are main's,
    equal as values and as text (repr), so nothing was reformatted either."""
    new = _rows(engine, day_text)[0][name]
    old = _rows(main_engine, day_text)[0][name]
    assert new, (name, day_text)
    assert _without(new) == _without(old), (name, day_text)
    assert repr(_without(new)) == repr(_without(old)), (name, day_text)


def test_the_differential_covers_six_charts_and_both_evaluators():
    assert len(CHARTS) == 6 and len(EVALUATORS) == 2


# --- B. The structure agrees with the labels, every row ---------------------

@pytest.mark.parametrize("day_text", list(CHARTS))
@pytest.mark.parametrize("name", EVALUATORS)
def test_the_testimony_numbers_are_the_labels_own_in_order(engine, day_text, name):
    """For every row: the list of n equals the paragraph numbers parsed from
    the labels with _tick_grid's regex, in the same order; each sentence is
    the label at the same index; Count is the length of both."""
    numbers = STRENGTH_NUMBERS if name == EVALUATORS[0] else WEAKNESS_NUMBERS
    for row in _rows(engine, day_text)[0][name]:
        cited = [PARAGRAPH.search(label).group(1) for label in row["Labels"]]
        assert [t["n"] for t in row["Testimonies"]] == cited, (row["Planet"], day_text)
        assert {t["n"] for t in row["Testimonies"]} == set(cited)
        assert set(cited) <= numbers, (row["Planet"], cited)
        assert [t["sentence"] for t in row["Testimonies"]] == row["Labels"]
        assert row["Count"] == len(row["Testimonies"]) == len(row["Labels"])


@pytest.mark.parametrize("day_text", list(CHARTS))
@pytest.mark.parametrize("name", EVALUATORS)
def test_every_testimony_carries_facts_in_the_fact_value_form(engine, day_text, name):
    """Each fact is one "Fact: Value" string, the name free of ": " (the
    page splits on the first) and free of digits: a number in a fact is a
    chart value, never prose of the page's own."""
    for row in _rows(engine, day_text)[0][name]:
        for t in row["Testimonies"]:
            assert t["facts"], (row["Planet"], t["n"], day_text)
            for fact in t["facts"]:
                assert isinstance(fact, str) and ": " in fact, fact
                fact_name, _, value = fact.partition(": ")
                assert fact_name and value, fact
                assert ": " not in fact_name, fact
                assert not re.search(r"\d", fact_name), fact


@pytest.mark.parametrize("day_text", list(CHARTS))
@pytest.mark.parametrize("name", EVALUATORS)
def test_the_rows_keys_are_the_old_ones_then_testimonies(engine, day_text, name):
    text_key = "Strength Testimonies" if name == EVALUATORS[0] else "Weakness Testimonies"
    for row in _rows(engine, day_text)[0][name]:
        assert list(row) == ["Planet", text_key, "Count", "Labels", "Testimonies"]


# --- C. Pinned on the default chart, cross-checked against the chart ---------

def _testimonies(engine, name, planet):
    rows, pool = _rows(engine, DEFAULT)
    row = next(r for r in rows[name] if r["Planet"] == planet)
    return {t["n"]: t["facts"] for t in row["Testimonies"]}, pool


def test_the_suns_strength_testimonies_on_the_default_chart(engine):
    """Fig. 24's row for the Sun: 79, 80, 81, 82, 83, 85, 88 -- seven of the
    eleven -- and at least one fact of each, read back against the chart."""
    facts, pool = _testimonies(engine, EVALUATORS[0], "Sun")
    assert list(facts) == ["79", "80", "81", "82", "83", "85", "88"]
    assert facts["79"] == ["Share of dignity: Joy"]
    assert pool["accidental"]["Sun"]["Joy"]
    assert "Retrograde (accidental): no" in facts["80"]
    assert f"Speed in longitude: {pool['p']['Sun']['speed_in_lon']:.2f}" in facts["80"]
    assert "Infortunes: Mars, Saturn" in facts["81"]
    assert "Configuration with Mars: Aversion" in facts["81"]
    assert "Configuration with Saturn: Aversion" in facts["81"]
    assert "Connected with: Moon, Venus, Jupiter" in facts["82"]
    assert "Fall (essential): no" in facts["82"]
    quadrant = engine["get_effective_house"](pool["p"]["Sun"]["longitude"], pool["cusps"])
    assert f"Quadrant division: {quadrant}" in facts["83"]
    assert "Angular and succedent divisions: 1, 2, 4, 5, 7, 8, 10, 11" in facts["83"]
    assert facts["85"] == ["Planet is diurnal: yes", f"Sect: {pool['sect']}"]
    sign = engine["get_zodiac_sign"](pool["p"]["Sun"]["longitude"])
    assert f"Sign: {sign}" in facts["88"] and "Gender: Masculine" in facts["88"]
    assert "Sign gender: Masculine" in facts["88"]


def test_saturns_strength_testimonies_on_the_default_chart(engine):
    """Saturn: 78, 79, 80, 81, 82, 83, 85, 88 -- eight of the eleven."""
    facts, pool = _testimonies(engine, EVALUATORS[0], "Saturn")
    assert list(facts) == ["78", "79", "80", "81", "82", "83", "85", "88"]
    place = engine["get_wsh_house"](pool["p"]["Saturn"]["longitude"], pool["asc"])
    assert facts["78"] == [f"Whole-sign place: {place}", "Excellent places: 1, 4, 5, 7, 10, 11"]
    assert place in engine["EXCELLENT_PLACES"]
    assert facts["79"] == ["Share of dignity: Term"]
    assert pool["essential"]["Saturn"]["Term"]
    assert "Retrograde (accidental): no" in facts["80"]
    assert facts["81"] == ["Infortunes: Mars", "Configuration with Mars: Sextile"]
    assert "Connected with: Venus, Jupiter" in facts["82"]
    quadrant = engine["get_effective_house"](pool["p"]["Saturn"]["longitude"], pool["cusps"])
    assert f"Quadrant division: {quadrant}" in facts["83"]
    assert "Planet is diurnal: yes" in facts["85"]
    assert "Quadrant gender: Masculine" in facts["88"]
    assert f"Sign: {engine['get_zodiac_sign'](pool['p']['Saturn']['longitude'])}" in facts["88"]


def test_the_moons_weakness_testimonies_on_the_default_chart(engine):
    """The Moon: 93 and 98 -- two of the ten."""
    facts, pool = _testimonies(engine, EVALUATORS[1], "Moon")
    assert list(facts) == ["93", "98"]
    assert "Combust (accidental): yes" in facts["93"]
    assert pool["accidental"]["Moon"]["Combust"]
    assert "Under the beams (accidental): no" in facts["93"]
    assert any(f.startswith("Signed distance from the Sun (positive is western): ") for f in facts["93"])
    rulers = engine["get_essential_rulers"](pool["p"]["Moon"]["longitude"])
    assert facts["98"] == [f"Domicile lord where it sits: {rulers['domicile']}",
                           f"Exaltation lord where it sits: {rulers['exaltation']}",
                           f"Triplicity lord where it sits (triplicity_day): {rulers['triplicity_day']}"]
    assert "Moon" not in (rulers["domicile"], rulers["exaltation"], rulers["triplicity_day"])


# --- D. The page ------------------------------------------------------------

def _fragment_defs():
    tree = ast.parse(ui_source())
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute) and dec.attr == "fragment" \
                        and isinstance(dec.value, ast.Name) and dec.value.id == "st":
                    out[node.name] = node
    return out


def _function_def(name):
    for node in ast.walk(ast.parse(ui_source())):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise LookupError(name)


@pytest.mark.parametrize("name", ["_strength_grid_block", "_weakness_grid_block"])
def test_each_grid_block_is_a_fragment(name):
    assert name in _fragment_defs(), sorted(_fragment_defs())


def test_the_tick_grid_is_drawn_only_inside_the_two_fragments():
    """Every call of _tick_grid stands in the body of one of the two grid
    fragments, so the grid, its expanders and the panel are all inside."""
    src = ui_source()
    defs = _fragment_defs()
    inside = {name: ast.get_source_segment(src, defs[name]) for name in ("_strength_grid_block", "_weakness_grid_block")}
    assert inside["_strength_grid_block"].count("_tick_grid(") == 1
    assert inside["_weakness_grid_block"].count("_tick_grid(") == 1
    body = ast.get_source_segment(src, _function_def("page_configurations"))
    assert body.count("_tick_grid(") == 2, "no call of _tick_grid outside the two fragments"
    assert "'Strength of the Planets'" in inside["_strength_grid_block"]
    assert "'Weakness of the Planets'" in inside["_weakness_grid_block"]


def test_the_grid_carries_on_select_and_a_key_from_its_title():
    body = ast.get_source_segment(ui_source(), _function_def("_tick_grid"))
    assert 'on_select="rerun"' in body
    assert 'selection_mode="single-row"' in body
    assert "key=_grid_key" in body
    assert "_grid_key = re.sub(r'\\W+', '_', title.lower()).strip('_') + '_grid'" in body
    assert re.sub(r'\W+', '_', 'Strength of the Planets'.lower()).strip('_') + '_grid' == STRENGTH_KEY
    assert re.sub(r'\W+', '_', 'Weakness of the Planets'.lower()).strip('_') + '_grid' == WEAKNESS_KEY
    # The grid's own DataFrame and column_config are what they were.
    assert "st.dataframe(pd.DataFrame(grid), hide_index=True, width='stretch', height=_rows_height(len(grid))," in body
    assert "column_config=_grid_columns, on_select=" in body


def test_the_panel_strings_carry_no_number_of_their_own():
    """Every string literal in _row_detail is free of digits: the numbers
    the panel prints are the paragraph number, the count and the total, and
    the facts' values -- all of them runtime values."""
    node = _function_def("_row_detail")
    literals = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert literals, "the panel prints something"
    assert not [s for s in literals if re.search(r"\d", s)], literals


def _render(depth, seed=None, date_text=DEFAULT):
    at = make_app(date=date_text, page="configurations")
    at.session_state["_reading_depth"] = depth
    for key, rows in (seed or {}).items():
        at.session_state[key] = {"selection": {"rows": rows}}
    at.run()
    assert_no_exception(at, f"configurations under {depth}")
    return at


def _panel_headings(at):
    return [s.value for s in at.main.subheader if PANEL_HEADING.match(s.value)]


def _fact_tables(at):
    return [df for df in at.main.dataframe if list(df.value.columns) == ["Fact", "Value"]]


def _grid_block(at, title):
    """The fragment's block: the one whose direct children include the
    grid's subheader."""
    def walk(node):
        kids = list(getattr(node, "children", {}).values())
        if any(getattr(k, "type", None) == "subheader" and k.value == title for k in kids):
            return node
        for k in kids:
            hit = walk(k)
            if hit is not None:
                return hit
        return None
    block = walk(at.main)
    assert block is not None, title
    return block


def _kinds(block):
    return [type(k).__name__ for k in block.children.values()]


# Grid, answer key, notes: the notes expander carries an icon, which AppTest
# renders as a Status element rather than an Expander.
BARE_GRID = ["Subheader", "Caption", "Dataframe", "Expander", "Status"]


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_no_selection_draws_no_panel_on_either_depth(depth):
    at = _render(depth)
    assert _panel_headings(at) == []
    assert _fact_tables(at) == []
    for title in ("Strength of the Planets", "Weakness of the Planets"):
        block = _grid_block(at, title)
        assert _kinds(block) == BARE_GRID, title
        assert list(block.children.values())[3].label == "Answer key: testimonies in words"


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_selecting_the_suns_row_draws_its_strength_testimonies_inside_the_fragment(engine, depth):
    at = _render(depth, seed={STRENGTH_KEY: [0]})
    assert _panel_headings(at) == ["Sun: 7 of 11 testimonies"]
    row = next(r for r in _rows(engine, DEFAULT)[0][EVALUATORS[0]] if r["Planet"] == "Sun")
    block = _grid_block(at, "Strength of the Planets")
    kids = list(block.children.values())
    assert [type(k).__name__ for k in kids[:3]] == ["Subheader", "Caption", "Dataframe"]
    assert kids[3].value == "Sun: 7 of 11 testimonies"
    assert [type(k).__name__ for k in kids[-2:]] == ["Expander", "Status"]
    # Between the heading and the expanders: one block per ticked testimony,
    # in numerical order -- caption, the sentence, then the facts.
    detail = kids[4:-2]
    i = 0
    for t in row["Testimonies"]:
        assert detail[i].value == f"{LOCATOR}, {t['n']}"
        assert detail[i + 1].value == t["sentence"]
        if len(t["facts"]) == 1:
            assert detail[i + 2].value == t["facts"][0]
        else:
            table = detail[i + 2].value
            assert list(table.columns) == ["Fact", "Value"]
            assert table.to_dict("records") == [{"Fact": f.partition(": ")[0], "Value": f.partition(": ")[2]}
                                                for f in t["facts"]]
        i += 3
    assert i == len(detail), "nothing else in the panel"
    assert [t["n"] for t in row["Testimonies"]] == sorted((t["n"] for t in row["Testimonies"]), key=int)
    # The weakness grid's block is untouched by the strength selection.
    assert _kinds(_grid_block(at, "Weakness of the Planets")) == BARE_GRID


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_selecting_the_moons_row_draws_her_weakness_testimonies(engine, depth):
    rows = _rows(engine, DEFAULT)[0][EVALUATORS[1]]
    index = next(i for i, r in enumerate(rows) if r["Planet"] == "Moon")
    at = _render(depth, seed={WEAKNESS_KEY: [index]})
    assert _panel_headings(at) == ["Moon: 2 of 10 testimonies"]
    captions = [c.value for c in at.main.caption if c.value in (f"{LOCATOR}, 93", f"{LOCATOR}, 98")]
    assert captions == [f"{LOCATOR}, 93", f"{LOCATOR}, 98"]
    sentences = [m.value for m in at.main.markdown if m.value in rows[index]["Labels"]]
    assert sentences == rows[index]["Labels"]
    assert len(_fact_tables(at)) == 2
    assert _kinds(_grid_block(at, "Strength of the Planets")) == BARE_GRID


def test_both_grids_can_be_selected_at_once():
    at = _render(READING_DEPTHS[0], seed={STRENGTH_KEY: [6], WEAKNESS_KEY: [0]})
    assert _panel_headings(at) == ["Saturn: 8 of 11 testimonies", "Sun: 1 of 10 testimonies"]


def test_the_panels_captions_name_only_paragraph_numbers_of_the_grid():
    """Every locator caption the panel prints ends in a number of the grid's
    own range, and the heading's numbers are the row's count and the grid's
    total: no number of the page's own."""
    at = _render(READING_DEPTHS[0], seed={STRENGTH_KEY: [0], WEAKNESS_KEY: [1]})
    captions = [k for title in ("Strength of the Planets", "Weakness of the Planets")
                for k in _grid_block(at, title).children.values() if type(k).__name__ == "Caption"]
    numbers = [m.group(1) for c in captions for m in [re.match(rf"^{re.escape(LOCATOR)}, (\d+)$", c.value)] if m]
    assert numbers and set(numbers) <= STRENGTH_NUMBERS | WEAKNESS_NUMBERS, numbers
    for heading in _panel_headings(at):
        _, count, total = PANEL_HEADING.match(heading).groups()
        assert total in ("11", "10") and 1 <= int(count) <= int(total)


def test_the_tables_fixture_is_mains():
    """No panel renders without a selection, so the page's inventory of
    tables -- and the fixture that pins it -- is what main has."""
    for ref in ("origin/main", "main"):
        try:
            shown = subprocess.run(["git", "show", f"{ref}:tests/fixtures/tables.json"], cwd=EXECUTABLE_DIR,
                                   capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        if shown.returncode == 0:
            assert TABLES_FIXTURE.read_text() == shown.stdout
            return
    pytest.skip("main's fixture is not in this checkout")
