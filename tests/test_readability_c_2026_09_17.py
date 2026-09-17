"""The four Prediction pages, readability branch C (2026-09-17), migrated
onto the renderer contract of branch A: what each block now renders, from
the same rows it rendered before, and how the engine's six note constants
are shown in paragraphs without a character of engine.py changing.

Nothing here tests doctrine; the engine is byte-identical to main. Each
test reads a page as AppTest renders it and checks the presentation the
branch promises: the visible summary and qualifications at reading width,
the headed notes with the book icon, the comparison tables' rows against
the sentences they were built from, a detail selectbox whose options are
the displayed table's column in order, the wheel legend's letters against
the badges the wheel is drawn with, correction 9b's wording, and every
_paragraphs() site rejoining to its constant.
"""
from __future__ import annotations

import ast
import re

import pytest

from conftest import (NOTES_EXPANDER_ICON, READING_DEPTHS, assert_no_exception, engine_source, make_app,
                      ui_source)

WITH_SUPPLEMENT = READING_DEPTHS[1]


# --- helpers ---------------------------------------------------------------

def _walk(node, depth=0, out=None):
    """Every element under `node` as (depth, type, text), text being the
    label of a status/expander/selectbox and the value of a markdown,
    caption or subheader."""
    out = [] if out is None else out
    for child in getattr(node, "children", {}).values():
        kind = getattr(child, "type", None)
        if kind in ("status", "expander", "selectbox"):
            text = child.label
        elif kind in ("markdown", "caption", "subheader", "warning"):
            text = child.value
        else:
            text = ""
        out.append((depth, kind, text, child))
        _walk(child, depth + 1, out)
    return out


def _statuses(at):
    return [(n.label, n.icon) for n in at.main if getattr(n, "type", None) == "status"]


def _expander(at, label):
    hits = [n for _d, k, t, n in _walk(at.main) if k == "status" and t == label]
    assert len(hits) == 1, [t for _d, k, t, _n in _walk(at.main) if k == "status"]
    return hits[0]


def _markdowns(node):
    return [m.value for m in node.markdown]


def _headings_in(expander):
    return [m.value for m in expander.markdown if re.fullmatch(r"\*\*.+\*\*", m.value)]


def _visible_markdowns(at):
    """Markdown values that stand outside every expander."""
    out, inside = [], None
    for depth, kind, text, _node in _walk(at.main):
        if inside is not None and depth <= inside:
            inside = None
        if kind == "status" and inside is None:
            inside = depth
            continue
        if inside is None and kind == "markdown":
            out.append(text)
    return out


def _heading(at, title):
    hits = [h for h in at.main.subheader if h.value == title]
    assert len(hits) == 1, [h.value for h in at.main.subheader]
    return hits[0]


def _page(page, date="1240-05-23", depth=None):
    at = make_app(date=date, page=page)
    if depth:
        at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, page)
    return at


def _app_function(name):
    """One module-level function of app.py, lifted by AST and executed
    alone (it must not touch Streamlit)."""
    tree = ast.parse(ui_source())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {}
    exec(ast.get_source_segment(ui_source(), node), namespace)
    return namespace[name]


# --- the engine constants, shown in paragraphs -----------------------------

ENGINE_NOTES = ("JN_YEARS_NOTE", "JN_CH4_ADDITIONS_NOTE", "SAHL_1_7_UNMODELLED", "SAHL_1_7_MODEL_DISCLOSURE",
                "SEVEN_PLACE_RANKING_NOTE", "PN4_YEAR_INDICATOR_SCOPE_NOTE")


def test_engine_py_is_byte_identical_to_main_on_this_branch():
    """The six constants are runs of adjacent literals, where a blank
    source line puts no break into the value; the paragraph breaks are a
    display representation in app.py (_paragraphs), and engine.py stays
    as main has it. The check here is what a tree can see of that: every
    constant is one parenthesised run of plain literals with no newline
    escape in it."""
    src = engine_source()
    for name in ENGINE_NOTES:
        start = src.index(f"\n{name} = (") + 1
        end = src.index("\n\n", start)
        literal = src[start:end]
        assert "\\n" not in literal, name


def _paragraph_sites():
    """Every _paragraphs(CONSTANT, "lead", ...) call in app.py as
    (constant name, leads)."""
    sites = []
    for node in ast.walk(ast.parse(ui_source())):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_paragraphs"
                and node.args and isinstance(node.args[0], ast.Name)):
            leads = [a.value for a in node.args[1:]]
            assert all(isinstance(lead, str) for lead in leads)
            sites.append((node.args[0].id, tuple(leads)))
    return sites


def test_every_paragraphs_site_rejoins_to_its_constant(engine):
    paragraphs = _app_function("_paragraphs")
    sites = _paragraph_sites()
    assert {name for name, _leads in sites} == {"JN_YEARS_NOTE", "JN_CH4_ADDITIONS_NOTE",
                                                "SEVEN_PLACE_RANKING_NOTE", "PN4_YEAR_INDICATOR_SCOPE_NOTE"}
    for name, leads in sites:
        constant = engine[name]
        parts = paragraphs(constant, *leads)
        assert len(parts) == len(leads) + 1, (name, len(parts))
        assert " ".join(parts) == constant, name
        for lead, part in zip(leads, parts[1:]):
            assert part.startswith(lead), (name, lead)
        # A paragraph break never falls inside a quotation.
        for part in parts:
            assert part.count('"') % 2 == 0, (name, part[:60])


def test_the_two_governor_constants_are_shown_whole_by_the_victors_page(engine):
    """SAHL_1_7_UNMODELLED and SAHL_1_7_MODEL_DISCLOSURE are composed into
    the governor rows' own text by the engine, so no break is made in
    them; the victors page prints them whole as branch A left it."""
    at = _page("victors")
    text = "\n".join(_markdowns(at.main))
    assert engine["SAHL_1_7_UNMODELLED"] in text and engine["SAHL_1_7_MODEL_DISCLOSURE"] in text


def test_the_scope_note_is_headed_sections_under_a_comparison_table(engine):
    at = _page("timing")
    exp = _expander(at, "The lord of the year and the distributor, ranked by scope")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**Within one year, and across several.**", "**Sahl's two sentences, as printed.**",
                                 "**The editor's emendation, not adopted.**",
                                 "**The disagreement, recorded and not resolved.**"]
    md = _markdowns(exp)
    table = next(m for m in md if m.startswith("| Scope |"))
    assert "| Within one year | the lord of the year (II.1, 25; II.23, 1); Sahl's 1.24, 2 agrees |" in table
    assert "| Across several years | the distribution (III.2, 2-3); Sahl's 1.23, 33 agrees |" in table
    note = re.sub(r"\s+", " ", engine["PN4_YEAR_INDICATOR_SCOPE_NOTE"])
    assert note in re.sub(r"\s+", " ", " ".join(m for m in md if not m.startswith("**")))
    assert "tender [of sheep]" in md[3] and "fn 245" in md[5] and "not resolved" in md[7]


def test_the_seven_place_note_is_a_manuscript_table_over_its_two_sentences(engine):
    at = _page("reference")
    md = "\n".join(_markdowns(at.main))
    for row in ("| Manuscripts H and L (the printed order) | ... 11, 9, 5 |",
                "| Manuscript B | ... 11, 5, 9, with the note that the ninth is the Sun's joy (Introduction Ch. 2, 42, fn 42) |",
                "| The printed text | H/L's order plus B's note -- Dykes's conflation, kept as printed |"):
        assert row in md, row
    assert re.sub(r"\s+", " ", engine["SEVEN_PLACE_RANKING_NOTE"]) in re.sub(r"\s+", " ", md)


LADDER_CHART = "1240-02-02"     # the Moon, house-master, no sentence of 1.20 reaches her


def test_the_ladder_note_is_visible_then_headed_with_each_impediment_on_its_own_line(engine):
    at = _page("releaser", LADDER_CHART, WITH_SUPPLEMENT)
    visible = _visible_markdowns(at)
    lead = next(m for m in visible if m.startswith("**When this ladder is shown.**"))
    assert "Sahl's grade, where he gives one, is never overridden by it." in lead
    exp = _expander(at, "The ladder's steps, this app's definitions, and the sources")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**Steps and impediments.**", "**This app's definitions and exceptions.**",
                                 "**Source disagreement.**"]
    md = _markdowns(exp)
    definitions = md[3]
    lines = [ln for ln in definitions.split("\n") if ln.startswith("- ")]
    assert [ln[:20] for ln in lines] == ['- "peregrine" is a p', '- "burned up" is thi', '- the Sun takes no s',
                                          '- "free from the bad']
    assert definitions.rstrip().endswith("it is printed as Ch. 4 has it.")
    # The whole note, its bullets and the escaping of its angle brackets
    # undone, is the lead and the three sections' bodies in order.
    bodies = [lead.replace("**When this ladder is shown.** ", "")] + [m for m in md if not re.fullmatch(r"\*\*.+\*\*", m)]
    shown = re.sub(r"(^|\n)- ", r"\1", "\n".join(bodies)).replace("\\<", "<")
    assert re.sub(r"\s+", " ", shown).strip() == re.sub(r"\s+", " ", engine["JN_YEARS_NOTE"]).strip()


def test_the_ladder_note_stands_on_fardar_under_the_planetary_years(engine):
    at = _page("fardar", depth=WITH_SUPPLEMENT)
    exp = _expander(at, "Abu 'Ali's ladder, where 1.20 is silent")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**When this ladder is shown.**", "**Steps and impediments.**",
                                 "**This app's definitions and exceptions.**", "**Source disagreement.**"]
    caption = next(c.value for c in at.main.caption if c.value.startswith("The last column"))
    assert caption.endswith("and the steps taken.")


def test_the_additions_note_is_headed_and_a_planet_can_be_read_whole(engine):
    at = _page("releaser", LADDER_CHART, WITH_SUPPLEMENT)
    title = "Additions and subtractions to the house-master's years (Abu 'Ali)"
    _heading(at, title)
    exp = _expander(at, "Sources and editorial notes")
    heads = _headings_in(exp)
    for h in ("**What the rows state.**", "**Abu Bakr and 'Umar, separate witnesses.**",
              "**Grades left unchosen, and Mercury's conjecture.**", "**The luminaries.**",
              "**Conventions of this display.**"):
        assert h in heads, h
    md = _markdowns(exp)
    bodies = " ".join(m for m in md if not re.fullmatch(r"\*\*.+\*\*", m))
    assert re.sub(r"\s+", " ", engine["JN_CH4_ADDITIONS_NOTE"]) in re.sub(r"\s+", " ", bodies)
    box = at.main.selectbox(key="additions_and_subtractions_to_the_house_master_s_years_abu_ali_detail")
    table = at.main.dataframe
    rows = next(d.value for d in table if "Looks at the house-master" in d.value.columns)
    assert list(box.options) == list(rows["Planet"])
    assert box.value is None and box.placeholder == "Select a planet to read its effect, grades, reading and witnesses"
    for planet in rows["Planet"]:
        box.select(planet).run()
        row = rows[rows["Planet"] == planet].iloc[0]
        text = "\n".join(_visible_markdowns(at))
        assert f"**{planet}**, {row['Looks at the house-master']}." in text
        assert f"**Effect (Ch. 4).** {row['Ch. 4']}." in text
        assert f"**This app's reading.** {row['Reading']}." in text
        assert f"**Other witnesses.** {row['Witnesses']}" in text
        if planet == "Mercury":
            assert "adds or subtracts nothing" not in row["Ch. 4"] or "fn 28" in row["Ch. 4"]
