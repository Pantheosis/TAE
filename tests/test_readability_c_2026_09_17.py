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


def test_the_six_note_constants_carry_no_newline_escape():
    """The six constants are runs of adjacent literals, where a blank
    source line puts no break into the value; the paragraph breaks are a
    display representation in app.py (_paragraphs), and engine.py was
    byte-identical to main when the branch was built (the docs note holds
    that proof; a tree cannot after the merge). The check here is what a
    tree can see: every constant is one parenthesised run of plain
    literals with no newline escape in it."""
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
            # _sahl_1_20_readings_sections takes the constant as its
            # argument `text` (it reaches the page through hm_years).
            name = "SAHL_1_20_READINGS" if node.args[0].id == "text" else node.args[0].id
            sites.append((name, tuple(leads)))
    return sites


def test_every_paragraphs_site_rejoins_to_its_constant(engine):
    paragraphs = _app_function("_paragraphs")
    sites = _paragraph_sites()
    assert {name for name, _leads in sites} == {"JN_YEARS_NOTE", "JN_CH4_ADDITIONS_NOTE", "SEVEN_PLACE_RANKING_NOTE",
                                                "PN4_YEAR_INDICATOR_SCOPE_NOTE", "SAHL_1_20_READINGS"}
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


# --- Revolutions -----------------------------------------------------------

def _timing(date="1240-05-23", **state):
    at = make_app(date=date, page="timing")
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert_no_exception(at, "timing")
    return at


REVOLUTIONS_BLOCKS = {
    # subheader: (tooltip, visible markdown openings, expander label, section headings)
    "The revolution of the year": (
        "I.2, 1: a revolution is the moment the Sun comes back to \"his position in which he was at the root\". "
        "I.2, 4: derive its Ascendant and the twelve houses.",
        ["**A true-Sun return.** The engine uses a **true**-Sun return; Abu Ma'shar computes a mean Sun"],
        None, []),
    "The image of the revolution of the year: its points (I.6, 3-8)": (
        "I.6, 8 and Figure 52: 14 planets, 98 rays, the Head and Tail twice each, 38 twelfth-parts -- 154 -- "
        "\"and the Lots according to how you do it\"; I.6, 9-10: within a house, by degree.",
        [],
        "How the image table is built",
        ["What I.6, 3-8 asks for.", "A table, by the revolution's cusps.", "The twelfth-parts."]),
    "The reading checklist (I.7, 1-26)": (
        "\"If you made the image of the revolution of the year, then understand:\" (I.7, 1) -- twenty-six things.",
        ["**Facts from this app's own evaluators**, run on the revolution's data as on the root's"],
        "The twenty-six things, and what is not read",
        ["The checklist, I.7, 2-26.", "Not read, and said so.", "The Lots, the principle, and the worked example."]),
    "Indicators of the year, in Abu Ma'shar's order": (
        "II.1, 5-24 ranks nineteen indicators of the year and II.1, 25 says \"each one in turn is stronger in "
        "indication than the one which is after it\".",
        ["The first five are computed here; the rest are delineation material.",
         "**Note the order: within a year** the lord of the year outranks the distributor (II.1, 25; II.23, 1)."],
        "The lord of the year and the distributor, ranked by scope",
        ["Within one year, and across several.", "Sahl's two sentences, as printed.",
         "The editor's emendation, not adopted.", "The disagreement, recorded and not resolved."]),
    "The sign of the terminal point and its lord, examined (II.3, 2-19)": (
        "II.3, 2: examine the sign of the terminal point in the root -- which house of the circle, whose house, "
        "exaltation and triplicity, which planets, Lots and twelfth-parts are in it, who looks at it or casts rays "
        "at it and from where, and whether it is devoid of them.",
        ["**Facts, not a verdict.** II.3, 5-6 name the factors of a suitable and a contrary condition"],
        "How the factors are read",
        ["What II.3, 3-18 asks.", "Row conventions.", "Not built."]),
    "Indicators 6-19: the fact each one reads": (
        "II.1, 11-24 list the remaining fourteen indicators, in II.1, 25's order of strength.",
        ["Each reads a fact from the root and the revolution and judges it in a chapter of its own",
         "**Facts, not judgments:** the delineation chapters behind these rows"],
        "Row conventions of the fourteen indicators",
        ["What each row reads."]),
    "The lord of the orb (VI.1)": (
        "VI.1, 4: \"the lord of the hour in which the native was born\" is assigned to the Ascendant and the first "
        "year; VI.1, 5-8: the next hour lord down the spheres to the next house and the next year, and on past twelve.",
        ["Row 5 above is this year's. The table here is VI.1, 18-19"],
        "The cycle of the hour lords, and the three answers to their names",
        ["The continuing cycle.", "The names of the lords: three answers, and what is built.",
         "What PN IV presupposes: the planetary hours.", "Not built, and built elsewhere."]),
    "The governor (IX.9, 1-10; IX.2, 4-7)": (
        "IX.9, 1-9 name eight testimonies and IX.9, 10 the rule; IX.2, 4 gives a second, sign-level governor for "
        "the first month.",
        ["**Partial by nature, and said so per row.** Testimony #3 and the releaser's half of #4 need the longevity "
         "releaser, which PN IV does not supply (IX.8, 123); they are filled from the releaser's distribution "
         "(Sahl, On Nativities 1.15, on The releaser page)"],
        "How the governor is tallied",
        ["The eight testimonies, and the rule.", "The meaning of \"alone\".", "A reading of \"the first lord\".",
         "The first month's governor (IX.2, 4).", "The condition of the primary planet, and what is not built."]),
    "The Moon's connections in her sign, and the portions of the year (II.22)": (
        "The revolution's Moon is followed by the ephemeris until she leaves her sign, and every perfection of "
        "body or Ptolemaic ray before that is a connection.",
        [],
        "How the Moon's connections are read",
        ["The sentences of II.22.", "Read into the sentences.", "Not counted, and not built.",
         "Where else this computation is used."]),
    "When a luminary is lord of the year: the proxies (II.13, 1; II.14, 1; II.22, 1-5)": (
        "II.14, 1 adds the distributor; II.22, 1-5 give the Moon's list. Dykes's fn 237 reads these as proxies "
        "standing in for the luminary.",
        ["**The first proxy needs the releaser.** The first proxy in every version is the sign the longevity "
         "releaser's distribution stands in, which PN IV does not supply (IX.8, 123)"],
        "The proxies, and what each depends on",
        ["II.13, 1, whole.", "The Sun's proxies, as read.", "The Moon's rows."]),
    "The turning of the houses of the root (VI.2)": (
        "Only the **turning** is built: whole-sign profection from each point's own natal position, as for the "
        "Ascendant.",
        ["**Two rows for a cusp in another sign.** VI.2, 21-24: a quadrant cusp that falls in another sign"],
        "The turning, the direction, and the twelve Lots",
        ["VI.2, 1, whole.", "The direction \"a year for every degree\".", "Which twelve Lots: not stated.",
         "A substitution read from the editor.", "The triplicity lords, and what is not built."]),
    "The distribution from the Ascendant (the *jar bakhtar*)": (
        "III.1, 12: the Ascendant is directed by the ascensions \"of the country in which the native was born\" -- "
        "oblique ascensions of the birth latitude, one degree of ascension to a year (III.1, 13). III.1, 14: the "
        "Persians gave this particular distribution, and no other, the name *jar bakhtar*.",
        ["III.1, 11: the lord of the bound reached is the distributor, \"whether it looked at [the bound] or not\". "
         "III.1, 15-16: the most recent body or ray met is the partner"],
        None, []),
    "The distribution analysed (III.2)": (
        "III.2, 4-9: a checklist of questions about the bound the distribution stands in, answered here as facts.",
        ["**Facts and classification, not judgment:** the conditions III.2's delineation turns on"],
        "How the distribution is classified",
        ["Method: the checklist, the types, the transitions, the ranking.",
         "Classifications, and the three planets of neither nature.",
         "The transitions, and the transits into the bound.", "Qualifications on the quoted conclusions.",
         "No worked example."]),
    "The distribution from the Midheaven and the fourth": (
        "III.1, 12: \"what is in the Midheaven or the fourth is directed by the ascensions of the right sphere\" -- "
        "right ascension, one degree to a year (III.1, 13), the lord of the bound reached as distributor (III.1, 11) "
        "and the last body or ray met as partner (III.1, 15-16), exactly as for the Ascendant.",
        ["Right ascension has no latitude in it, so these two distributions are defined at every latitude",
         "**What PN IV does not supply here, stated rather than filled in.**"],
        "Five things the book leaves unsaid of this distribution",
        ["No topic from the author.", "Not among the year's indicators.", "No worked example.",
         "The partner at birth, by analogy.", "\"In\", read as on the axial degree itself."]),
    "The planets, each with its measure under III.1, 12": (
        "A planet **on** an axial degree is directed as that degree is. Every other planet is the third case, "
        "whose method PN IV defers to a book it does not reproduce.",
        [],
        "The third case: proportional semi-arcs",
        ["III.1, 12, whole.", "The three positional cases.", "The formula.", "Definitions.", "Sign conventions.",
         "Not used, and not built."]),
}


@pytest.fixture(scope="module")
def timing_page():
    return _timing()


@pytest.mark.parametrize("title", list(REVOLUTIONS_BLOCKS))
def test_each_revolutions_block_has_its_tooltip_visible_text_and_headed_notes(timing_page, title):
    tooltip, visible, label, sections = REVOLUTIONS_BLOCKS[title]
    at = timing_page
    assert _heading(at, title).help == tooltip
    assert len(tooltip) <= 300
    shown = _visible_markdowns(at)
    for opening in visible:
        assert any(m.startswith(opening) for m in shown), opening
    if label:
        exp = _expander(at, label)
        assert exp.icon == NOTES_EXPANDER_ICON
        assert _headings_in(exp) == [f"**{s}**" for s in sections]
        assert not exp.dataframe


def test_the_revolutions_page_has_no_text_over_its_ceiling():
    from test_text_lengths_2026_09_17 import offenders
    src = ui_source()
    start = src.index("def page_timing():")
    end = src.index("def page_releaser():")
    first_line = src[:start].count("\n") + 1
    last_line = src[:end].count("\n") + 1
    assert not [o for o in offenders() if first_line <= o[1] <= last_line]


def test_the_wheel_legend_letters_are_the_badges_the_wheel_is_drawn_with(timing_page):
    exp = _expander(timing_page, "How the wheel is drawn")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**The five views.**", "**Chart layers.**", "**Points shown.**",
                                 "**Display conventions: whole signs drawn, cusps computed.**"]
    points = next(m for m in _markdowns(exp) if m.startswith("| Mark | Meaning |"))
    table, _, sentence = points.partition("\n\n")
    rows = [tuple(c.strip() for c in ln.strip("|").split("|")) for ln in table.split("\n")[2:]]
    letters = [(mark, meaning) for mark, meaning in rows if len(mark) <= 2]
    assert letters == [("TP", "the terminal point of the year (I.6, 5)"),
                       ("D", "distributor (I.6, 6's time lords, lettered under a natal planet)"),
                       ("P", "partner"), ("F", "lord of the fardar"), ("f", "its divider"), ("O", "lord of the orb")]
    # Each letter's meaning is the definition the sentence beneath gives it, verbatim.
    assert ("TP marks the terminal point of the year (I.6, 5); the letters under a natal planet mark I.6, 6's time "
            "lords -- D distributor, P partner, F lord of the fardar, f its divider, O lord of the orb; the solid "
            "arc from the natal Ascendant is the distribution") in sentence
    for mark, meaning in letters[1:]:
        assert f"{mark} {meaning.split(' (')[0]}" in sentence, mark
    # And the letters are the ones the wheel is badged with, F and f distinct.
    src = ui_source()
    badges = re.findall(r"\('(?:distributor|partner|lord|sub_lord)'\), '([A-Za-z])'\)|\(pn4\['orb'\], '([A-Za-z])'\)", src)
    drawn = [a or b for a, b in badges]
    assert drawn == ["D", "P", "F", "f", "O"] == [mark for mark, _m in letters[1:]]
    arcs = [mark for mark, _m in rows if "arc" in mark]
    assert arcs == ["dashed arc", "solid arc"]
    caption = next(c.value for c in timing_page.main.caption if c.value.startswith("Default points are Dykes's"))
    assert caption.endswith("the inventory table below is the authority the picture is held to.")


def test_the_three_positional_cases_are_the_engines_own_rows(timing_page, engine):
    exp = _expander(timing_page, "The third case: proportional semi-arcs")
    cases = next(m for m in _markdowns(exp) if m.startswith("| Point directed | Measured in |"))
    rows = [ln for ln in cases.split("\n") if ln.startswith("| ") and not ln.startswith("| Point")]
    assert rows == [f"| {r['Point directed']} | {r['Measured in']} |" for r in engine["PN4_ASCENSION_ROWS"]]
    assert cases.endswith("A planet **on** an axial degree is directed as that degree is.")
    formula = next(m for m in _markdowns(exp) if "`PromMD - (SigMD / SigSA) * PromSA`" in m)
    assert formula.endswith("`PromMD - (SigMD / SigSA) * PromSA`")
    assert "-- PromMD - (SigMD / SigSA) * PromSA -- a degree of it a year (III.1, 13)." in formula


def test_the_orb_blocks_hour_lord_line_shows_only_where_the_chart_page_flags_the_approximation():
    florence = _timing()
    assert not any(m.startswith("**The natal hour lord is approximate here.**") for m in _visible_markdowns(florence))
    polar = _timing(manual_lat_key=78.2, manual_lon_key=15.6)
    lines = [m for m in _visible_markdowns(polar) if m.startswith("**The natal hour lord is approximate here.**")]
    assert len(lines) == 1 and "flagged equal-hour approximation where the Sun is circumpolar" in lines[0]
    notes = _expander(polar, "The cycle of the hour lords, and the three answers to their names")
    assert any("flagged equal-hour approximation where the Sun is circumpolar" in m for m in _markdowns(notes))


def test_the_orb_names_table_lists_the_four_readings_with_their_status(timing_page):
    exp = _expander(timing_page, "The cycle of the hour lords, and the three answers to their names")
    table = next(m for m in _markdowns(exp) if m.startswith("| Reading | Here |"))
    for row in ("| The continuing cycle (VI.1, 5-8): the loop of seven runs on against the cycle of twelve | Built |",
                "| The names fixed to the first cycle (VI.1, 10) | Shown beside the loop's planet for the same name; neither is stated for 18-19 |",
                "| A single-cycle version, each house keeping its first hour lord for life (Intro Figure 48, Dykes's thought) | Not built; VI.1, 8 states the loop and the loop is built |",
                "| The twelve-year reset of the named lords (Intro Sect. 13, \"my idea\") | Not built |"):
        assert row in table, row
    assert "and the reset Dykes proposes (Intro Sect. 13, \"my idea\") is a third answer, his own." in table


def test_the_refused_distribution_keeps_its_notes_and_qualifications():
    """Far north the Ascendant's distribution is refused; the visible
    statements and the notes stand regardless."""
    at = _timing(manual_lat_key=78.2, manual_lon_key=15.6)
    warnings = [w.value for w in at.main.warning]
    assert any(w.startswith("Refused at this latitude.") for w in warnings)
    for label in ("How the distribution is classified", "Five things the book leaves unsaid of this distribution",
                  "The third case: proportional semi-arcs"):
        _expander(at, label)
    shown = _visible_markdowns(at)
    assert any(m.startswith("No current distribution to analyse") for m in shown)
    assert any(m.startswith("**Facts and classification, not judgment:**") for m in shown)


# --- The releaser ----------------------------------------------------------

@pytest.fixture(scope="module")
def releaser_page():
    return _page("releaser")


def test_the_releaser_caption_is_two_sentences_and_the_exception_clause_leads_the_method(releaser_page):
    at = releaser_page
    caption = next(c.value for c in at.main.caption if c.value.startswith("They are taken from Sahl"))
    assert caption == ("They are taken from Sahl, *On Nativities* (cited on this page by that book's chapter and "
                       "sentence). What neither book settles is listed at the foot of the Fardar and ages page rather "
                       "than filled in.")
    shown = _visible_markdowns(at)
    lead = next(m for m in shown if m.startswith("The releaser and the house-master PN IV leaves to another book"))
    assert lead.endswith("not the *Great Introduction*, which has only the Lot of the releaser.")
    assert shown.index(lead) + 1 == shown.index(next(m for m in shown if m.startswith("Nawbakht's procedure")))
    exp = _expander(at, "Years granted and alternative procedures")
    text = " ".join(_markdowns(exp))
    assert ("Al-Qabisi's own account of the releaser and the house-master (ITA VIII.1.3, al-Qabisi IV.4-6) is in "
            "hand and stands beside Sahl's in the Sources page's coverage table, not built.") in text


def test_the_house_master_direction_shows_the_join_and_denial_and_heads_its_notes(releaser_page):
    at = releaser_page
    assert _heading(at, "The house-master directed (Sahl, *On Nativities* 1.23, 1-11)").help == (
        "This is the technique that needs no grant of years -- Masha'allah's alternative, absent from PN IV and "
        "present in Sahl.")
    shown = _visible_markdowns(at)
    assert any(m == "**Facts, not judgment:** 1.23, 4's verdict is quoted in the notes and not pronounced."
               for m in shown)
    # Folded on the owner's ruling: one visible sentence (the paragraph's
    # opening clause and its "The join is this app's" sentence), the
    # paragraph whole under "The join." and "The denial." in the notes.
    join = next(m for m in shown if m.startswith("The house-master directed here is selected by **Nawbakht's** rule"))
    assert join.endswith("(1.23, 2, \"direct it\" -- the governor). The join is this app's; no sentence states it.")
    assert "1.23, 40 and 43" not in join and "denies" not in join
    assert not any("The join, and the denial beside it" in m for m in shown)
    assert any(m.startswith("IX.8, 30's turning, the one operation") for m in shown)
    turned = next(m for m in shown if "turned a year a sign from its natal sign (whole signs, as VI.2, 1)" in m)
    assert turned.endswith("(31) and is not shown.")
    assert any(c.value == "Read: \"their\" as Saturn's and Mars's, the cutters the direction table targets."
               for c in at.main.caption)
    exp = _expander(at, "How the house-master is directed")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**Masha'allah's operation, 1.23, 2-4.**", "**The join.**", "**The denial.**",
                                 "**Limitations: two limits of the denial.**", "**Current direction: the readings.**",
                                 "**Not applied, and the redirection applied.**"]
    md = _markdowns(exp)
    assert md[1].startswith("Masha'allah:\n\n> \"look at the position of the governor") and md[1].endswith("(1.23, 2-4).")
    assert md[3].startswith("The house-master directed here is selected by **Nawbakht's** rule")
    assert "1.23, 40 and 43 call Masha'allah's governor" in md[3] and md[3].endswith("no sentence states it.")
    assert md[5].startswith("Abu Ma'shar denies the direction:\n\n> \"the indicator of the lifespan alone")
    assert "(PN IV IX.8, 32; fn 129: \"Some texts say" in md[5] and md[5].endswith("Shown as Sahl's, with the denial beside it.")
    assert "IX.8, 32 restricts the **role**" in md[7]
    assert "is **applied** below when a 1.23, 12 flag fires" in md[11]


def test_the_fathers_lot_has_its_summary_visible_and_four_headed_notes(releaser_page):
    at = releaser_page
    title = "The father's Lot: its harmers and their direction (Sahl, *On Nativities* 4.20, 31-36)"
    assert _heading(at, title).help == ("32: \"direct the degree of the Lot of the father and the Sun by day, and by "
                                        "night the Lot and Saturn\".")
    shown = _visible_markdowns(at)
    assert any(m.startswith("The Lot of the father stands at") and m.endswith("31 is applied as printed.") for m in shown)
    exp = _expander(at, "The harmers, the points directed, and the readings")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**Harmers, 4.20, 31.**", "**Points directed, 4.20, 32.**",
                                 "**The direction's verdict, and the ranking of two infortunes, 4.20, 33-36.**",
                                 "**Interpretive choices.**"]
    md = _markdowns(exp)
    assert md[1].startswith("31: \"if the nativity was by day") and md[7].startswith("Readings: \"casting its rays\"")
    assert md[7].endswith("33-35's choice between two infortunes is not made.")


def test_the_releaser_page_has_no_text_over_its_ceiling():
    from test_text_lengths_2026_09_17 import offenders
    src = ui_source()
    start = src.index("def page_releaser():")
    end = src.index("def page_days():")
    first_line = src[:start].count("\n") + 1
    last_line = src[:end].count("\n") + 1
    assert not [o for o in offenders() if first_line <= o[1] <= last_line]


# --- Days and months -------------------------------------------------------

@pytest.fixture(scope="module")
def days_page():
    return _page("days")


DAYS_BLOCKS = {
    "The small days: the revolution's Ascendant distributed round the year": (
        "A second distribution, running inside the year at its own rate; the Ascendant's distribution on the "
        "Revolutions page runs across the years.",
        ["| Method | As applied |"],
        "How the small days are read",
        ["The sentences, IX.7, 29-31.", "Zodiacal, by the sentence.", "Source and approximation.",
         "Read into the sentence.", "The selector, and the worked example."]),
    "The mighty days: the terminal degree of the year directed through the revolution": (
        "The profected thirty degrees treated as a year, walked degree by degree.",
        ["**Applied rate: 12.175 days per degree** -- the author's parenthetical (IX.7, 25)",
         "The direction does not stop at the end of the sign of the year: it starts at the terminal degree and "
         "runs thirty degrees, so its last part lies in the bounds of the next sign"],
        "How the mighty days are read, and why this rate",
        ["The sentences, IX.7, 23-28.", "Why this rate.", "Zodiacal by construction.", "Read into the sentence.",
         "The selector, and the worked example."]),
    "The nine methods for the days and hours (IX.7, 1-72)": (
        "\"The days and hours have nine indicators\" (IX.7, 1). IX.7, 56: all in equal hours. IX.7, 79 declines "
        "day and hour charts and keeps these.",
        ["**The day.** A \"day\" is a whole 24-hour period from the birth moment"],
        "The nine methods, one by one, and how they are counted",
        ["The nine methods.", "The hours.", "Methods 8 and 9.", "The example's printed errors, and what is not built."]),
    "The seven indicators of the month": (
        "IX.1, 35-39. Five are \"rooted\" -- turned from the positions they hold at the revolution of the year -- "
        "and two are not, being cast fresh from each monthly revolution.",
        ["They decrease in universality in the order given (IX.1, 39). The sign of the year is itself month 1"],
        "The turning rule the radio chooses between",
        ["Abu Ma'shar's rule, IX.1, 26-34.", "Dykes's reading, the default."]),
}


@pytest.mark.parametrize("title", list(DAYS_BLOCKS))
def test_each_days_block_has_its_tooltip_visible_text_and_headed_notes(days_page, title):
    tooltip, visible, label, sections = DAYS_BLOCKS[title]
    at = days_page
    assert _heading(at, title).help == tooltip
    shown = _visible_markdowns(at)
    for opening in visible:
        assert any(m.startswith(opening) for m in shown), opening
    exp = _expander(at, label)
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == [f"**{s}**" for s in sections]
    assert not exp.dataframe


def test_the_small_days_method_line_names_start_rate_and_time_origin(days_page):
    method = next(m for m in _visible_markdowns(days_page) if m.startswith("| Method | As applied |"))
    assert method.startswith("| Method | As applied |")
    assert "| Start | the degree of the Ascendant of the revolution of the year (IX.7, 29) |" in method
    assert "| Rate | 59' 08\" a day round the zodiac, returning to the degree in 365.28 days |" in method
    assert ("| Time origin | the days count from the moment of the revolution (fn 161 leaves a \"day\" undefined) "
            "-- read into the sentence rather than stated by it |") in method
    box = next(b for b in days_page.main.selectbox if b.key == "pn4_day_point")
    assert "**A reading:** the \"houses\" are offered" in box.help


def test_the_mighty_days_rate_is_the_engines_constant_and_the_three_readings_are_compared(days_page, engine):
    rate = engine["PN4_MIGHTY_DAYS_PER_DEGREE"]
    assert f"{rate:g}" == "12.175"
    exp = _expander(days_page, "How the mighty days are read, and why this rate")
    why = next(m for m in _markdowns(exp) if m.startswith("| Reading of IX.7, 25 | A degree is |"))
    for row in ("| The manuscript's 12;10,30 days (10 minutes and 30 seconds as sexagesimal fractions of a day) | 12.175 d |",
                "| The author's parenthetical, 12 + 1/6 + 1/120 | 12.175 d; thirty of which are 365 1/4 days exactly (IX.7, 28) |",
                "| Dykes's hybrid, his \"<4 hours>\" supplied and the minutes read as clock time | 12 d 4 h 10 m 30 s (12.17396 d); thirty of them 365 d 5 h 15 m |"):
        assert row in why, row
    assert "Three figures stand in that sentence: the manuscript's 12;10,30 days" in why
    assert why.endswith("**Applied**: the author's parenthetical, 12.175 d a degree.")


def test_the_nine_methods_are_listed_one_per_line_with_the_errata(days_page, engine):
    exp = _expander(days_page, "The nine methods, one by one, and how they are counted")
    md = _markdowns(exp)
    methods = [ln for ln in md[1].split("\n") if ln.startswith("- ")]
    assert [ln[:5] for ln in methods] == ["- 1: ", "- 2: ", "- 3: ", "- 4: ", "- 5: ", "- 6 a", "- 8: ", "- 9: "]
    errata = md[7]
    for c, p, e, fn in engine["PN4_IX7_EXAMPLE_ERRATA"]:
        assert f"- {c} prints {p} for {e} ({fn})" in errata
    assert errata.endswith("The judgments of IX.7, 21-22 and 40-42 are not built.")


def test_the_monthly_turn_radio_keeps_dykes_reading_in_its_help_and_abu_mashars_rule_in_the_notes(days_page):
    radio = next(r for r in days_page.main.radio if r.key == "pn4_monthly_turn")
    assert radio.help.startswith("Dykes rejects the whole rule as \"complicated, probably wrong\"")
    exp = _expander(days_page, "The turning rule the radio chooses between")
    md = _markdowns(exp)
    assert "turns the monthly indicators **backwards** when the sign is convertible" in md[1]
    assert "each indicator's **own** sign, individually" in md[1]


def test_the_days_page_has_no_text_over_its_ceiling():
    from test_text_lengths_2026_09_17 import offenders
    src = ui_source()
    start = src.index("def page_days():")
    end = src.index("def page_fardar():")
    first_line = src[:start].count("\n") + 1
    last_line = src[:end].count("\n") + 1
    assert not [o for o in offenders() if first_line <= o[1] <= last_line]


# --- Fardar and ages -------------------------------------------------------

@pytest.fixture(scope="module")
def fardar_page():
    return _page("fardar")


FARDAR_BLOCKS = {
    "The lords of the triplicity of the sect light, over the life": (
        "The three lords of the sect light's triplicity (the Sun's by day, the Moon's by night) in the "
        "day-night-partner order for a day birth and night-day-partner for a night birth, each with its natal "
        "condition.",
        ["**No period is assigned.** No text in hand assigns a number of years to any lord's stretch of the life"],
        "The source testimony on the lords over the life",
        ["Sahl, On Nativities 2.11, 1-2 and 4.", "2.13, 39 and 2.19, 5.", "PN IV VI.2, 4.",
         "The Ascendant's triplicity lords, for comparison."]),
    "The *fardar*": (
        "IV.1, 2-4: the years are Sun 10, Venus 8, Mercury 13, Moon 9, Saturn 11, Jupiter 12, Mars 7, Head 3, "
        "Tail 2 -- 75 in all. The order runs down the spheres from the light of the sect: by day from the Sun, "
        "by night from the Moon.",
        ["**The nodes last, in both sects.** IV.7, 24: the Head and Tail come **last in both sects**"],
        None, []),
    "When a natal indication comes out (III.7, 32-42)": (
        "A planet may distribute or manage more than once in a lifetime (III.7, 32), and this chapter asks how "
        "often what it promised in the root actually manifests, and at what ages.",
        ["**All three grades are shown and none is chosen.**"],
        "How the manifestation is read: the grade, the looking, the confirmation",
        ["How often, and at what age, III.7, 35-42.", "The grade choice.", "Looking.", "Confirmation."]),
    "The Ages of Man": (
        "I.8, 10-26 and Figure 53 (PN IV): Ptolemy's seven ages, ordered by sphere from the lowest upward -- not "
        "the quadrant scheme of Sahl, On Nativities 3.9.",
        [],
        "How the spans are counted",
        ["The spans, I.8, 9.", "The Moon's 4, a witness."]),
    "Chronocrator Matrix": (
        "Two rows: the lord of the year by annual profection, and the Egyptian bound lord of the Ascendant "
        "directed symbolically at one degree per year -- which is not a distribution, as its label says.",
        ["**An approximation, by the author's own grading.** Abu Ma'shar names the shortcut himself and grades it"],
        None, []),
    "Planetary years": (
        "The lesser, middle, greater and mighty years and the fardar of each planet, beside its placement, the "
        "grade On Nativities 1.20, 7-34 would give it as house-master (placed by the division, the **power** "
        "unit) and what On Times 4, 7 -- a question-chart rule, 4, 2 -- would give it, for comparison.",
        ["**Applied to one planet only:** the house-master The releaser page names from On Nativities 1.15"],
        None, []),
}


@pytest.mark.parametrize("title", list(FARDAR_BLOCKS))
def test_each_fardar_block_has_its_tooltip_visible_text_and_headed_notes(fardar_page, title):
    tooltip, visible, label, sections = FARDAR_BLOCKS[title]
    at = fardar_page
    assert _heading(at, title).help == tooltip
    assert len(tooltip) <= 300
    shown = _visible_markdowns(at)
    for opening in visible:
        assert any(m.startswith(opening) for m in shown), opening
    if label:
        exp = _expander(at, label)
        assert exp.icon == NOTES_EXPANDER_ICON
        assert _headings_in(exp) == [f"**{s}**" for s in sections]
        assert not exp.dataframe


def test_the_direction_units_keep_their_three_tables_with_separate_notes(fardar_page, engine):
    at = fardar_page
    captions = [c.value for c in at.main.caption]
    assert "The three cases do not stand alike." in captions
    assert "An idealised year of twelve 30-day months (fn 17)." in captions
    exp = _expander(at, "How a degree is directed, and what it is worth")
    assert _headings_in(exp) == ["**By position, III.1, 12.**", "**By level of chart, III.1, 6.**",
                                 "**The rate ladder, III.1, 13.**"]
    md = _markdowns(exp)
    assert md[1].startswith("The **Ascendant** and the **meridian** are the distributions on the Revolutions page")
    assert md[1].endswith("; no other ascension is substituted.")
    for r in engine["PN4_UNIT_ROWS"]:
        assert f"- {r['Directed in the']}: a degree is {r['A degree is']}" in md[3]
    assert md[5].startswith("The bottom rung is **25 thirds**")
    checkbox = next(c for c in at.main.checkbox if c.key == "life_lords_ascendant")
    assert checkbox.help == ("Some software divides the life by the lords of the **Ascendant's** triplicity. The rows "
                             "are shown only so the difference can be seen.")


def test_the_scope_index_names_each_items_state_with_correction_9b(fardar_page):
    at = fardar_page
    kids = list(at.main.children.values())
    statuses = [n for n in kids if getattr(n, "type", None) == "status"]
    assert [n.label for n in statuses[-2:]] == ["What Persian Nativities IV does not settle", "Sources and editorial notes"]
    assert statuses[-2].icon == ":material/help:" and statuses[-1].icon == NOTES_EXPANDER_ICON
    # The two foot expanders are the page's last elements, and no
    # dataframe stands after the help-icon one.
    assert kids[-2:] == statuses[-2:]
    assert not statuses[-2].dataframe and not statuses[-1].dataframe
    md = _markdowns(statuses[-2])
    assert md[0].startswith("The Prediction pages leave these items open.")
    index = md[1]
    assert index.startswith("| Topic | State |")
    rows = [ln for ln in index.split("\n") if ln.startswith("| ") and not ln.startswith("| Topic")]
    assert [r.split(" | ")[0][2:] for r in rows] == [
        "The releaser and the house-master", "Where the greater years are granted",
        "Directing anything that is not the Ascendant or the meridian", "Revolutions of the day and the hour",
        "The unit of a directed degree by sign type, strength or planet", "The Indian rule for the lord of the year"]
    assert "displayed, row by row, and not applied to Sahl's grant" in rows[0]
    assert "not implemented" in rows[3] and "Source silence" in rows[4]
    headings = _headings_in(statuses[-2])
    assert headings == ["**The releaser and the house-master.**", "**Where the greater years are granted.**",
                        "**Directing anything that is not the Ascendant or the meridian.**",
                        "**Revolutions of the day and the hour.**",
                        "**The unit of a directed degree by sign type, strength or planet.**",
                        "**The Indian rule, reported and not adopted.**"]
    text = "\n".join(md)
    # Correction 9b: Abu 'Ali's modifiers are displayed and not applied, never "not built here".
    assert ("Al-Qabisi's choice is stated in that text, not built here; Abu 'Ali's additions and subtractions are "
            "displayed, row by row, and not applied to Sahl's grant; the choice stays Sahl's.") in text
    assert "Both are stated in those texts, not built here" not in text
    assert "Both are stated in those texts, not built here" not in ui_source()
    editorial = _headings_in(statuses[-1])
    assert editorial == ["**The rate ladder's bottom rung, and the fardar order.**", "**One printed error is not reproduced.**",
                         "**The lord of the year is the lord of the sign of the year.**",
                         "**Figure 146, On Times 4, 7 and On Nativities 1.20, 10-17.**"]


def test_the_fardar_page_has_no_text_over_its_ceiling():
    from test_text_lengths_2026_09_17 import offenders
    src = ui_source()
    start = src.index("def page_fardar():")
    end = src.index("def page_sources():")
    first_line = src[:start].count("\n") + 1
    last_line = src[:end].count("\n") + 1
    assert not [o for o in offenders() if first_line <= o[1] <= last_line]


# --- The allowlist closed, the sidebar's LMT help, the pick panel -----------

def test_the_allowlist_is_empty_and_the_guard_passes_plainly():
    import test_text_lengths_2026_09_17 as guard
    assert guard.ALLOWED_LONG == ()
    assert not guard.offenders()
    src = open(guard.__file__, encoding="utf-8").read()
    assert "pytest.mark.xfail" not in src


def test_the_time_standard_help_is_a_line_and_the_three_standards_stand_in_the_sidebar():
    at = _page("chart")
    box = at.sidebar.selectbox(key="time_standard_key")
    assert box.help == ("LMT (local mean time) for charts before standard time was adopted (late 19th century); "
                        "Standard time: the named zone at the birthplace; Manual: type the offset the birth record "
                        "states, east positive.")
    exp = next(n for n in at.sidebar if getattr(n, "type", None) == "status" and n.label == "The three time standards")
    assert exp.icon == NOTES_EXPANDER_ICON
    lines = [ln for ln in _markdowns(exp)[0].split("\n") if ln.startswith("- ")]
    assert lines == [
        "- LMT (local mean time) for charts before standard time was adopted (late 19th century): the offset is "
        "the longitude at 4 minutes a degree.",
        "- Standard time: the named zone at the birthplace, with daylight saving as the zone's own history records it.",
        "- Manual: type the offset the birth record states, east positive (EST is -5, CDT is -5, IST is +5.5).",
    ]


def test_the_wheel_pick_panel_names_pages_as_the_bar_names_them():
    src = ui_source()
    panel = src[src.index("def _pick_panel(picked):"):src.index("# Looking at the chart is the primary act")]
    assert "The Reference page carries" not in panel and "The Dignities page carries" not in panel
    assert panel.count("Reference tables page carries") == 3
    assert panel.count("Dignities and places page carries") == 2


# --- Sahl 1.20's readings, the caption every net missed --------------------

def test_the_1_20_readings_are_headed_sections_not_a_caption(engine):
    at = _page("releaser")
    assert not [c for c in at.main.caption if c.value.startswith("Readings of 1.20 made here")]
    exp = _expander(at, "How 1.20 is read here")
    assert exp.icon == NOTES_EXPANDER_ICON
    assert _headings_in(exp) == ["**The placement: the division, and a power judgment.**", "**The vocabulary.**",
                                 "**The sentences, as read.**", "**On Times 4, 7, and 1.23, 53 and 61.**",
                                 "**The test-chart figures.**"]
    md = _markdowns(exp)
    assert md[1].startswith("Readings of 1.20 made here: the house-master is placed by the Alchabitius DIVISION")
    vocabulary = [ln for ln in md[3].split("\n") if ln.startswith("- ")]
    assert [ln[:11] for ln in vocabulary] == ['- "enhanced', '- "a share"', '- "eastern"', '- "under th', '- "alien" =']
    readings = [ln for ln in md[5].split("\n") if ln.startswith("- ")]
    assert [ln[:9] for ln in readings] == ["- 10 and ", '- "under ', "- 12 is s", "- 13 is i", "- 14-15 a", "- 19 and ",
                                            "- where a", "- Placeme"]
    assert md[7].startswith("On Times 4, 7 is a rule") and "\n\n1.23, 53 and 61:" in md[7]
    assert md[9].startswith("On 406 test charts")
    bodies = "\n".join(m for m in md if not re.fullmatch(r"\*\*.+\*\*", m))
    shown = re.sub(r"(^|\n)- ", r"\1", bodies)
    assert re.sub(r"\s+", " ", shown).strip() == re.sub(r"\s+", " ", engine["SAHL_1_20_READINGS"]).strip()
    # The three paragraphs and the flags stand above it as before.
    shown_md = _visible_markdowns(at)
    years = next(m for m in shown_md if m.startswith("**The house-master's years**"))
    assert "\n\nPlaced by division" in years and "(the **power** unit).\n\nThese are the years" in years
