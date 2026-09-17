"""The six P1 blocks of readability branch A (2026-09-17), migrated onto the
renderer contract: what each block now renders, from the same rows it
rendered before.

Nothing here tests doctrine; the engine is byte-identical to main. Each
test reads the page as AppTest renders it and checks the presentation
the branch promises: the visible summary and qualification above a table,
the detail selectbox printing a chosen row whole, the sibling disclosures
carrying the book icon, and the copy correction 9a on both pages.
"""
from __future__ import annotations

import re

import pytest

from conftest import (NOTES_EXPANDER_ICON, READING_DEPTHS, assert_no_exception, make_app,
                      table_inventory, ui_source)

PROSPERITY = "Sahl: indications of fortune and livelihood"
PROSPERITY_COLUMNS = ["Class", "Ground", "Sahl", "Also"]


def _statuses(at):
    return [(n.label, n.icon) for n in at.main if getattr(n, "type", None) == "status"]


def _between(at, first, last=None):
    """The (type, text) of every element from the subheader `first` up to
    (not including) the next subheader, or `last` when given."""
    out, inside = [], False
    for node in at.main:
        kind = getattr(node, "type", None)
        if kind == "subheader":
            if node.value == first:
                inside = True
                continue
            if inside and (last is None or node.value == last):
                break
        if inside and kind in ("markdown", "caption", "selectbox", "status", "dataframe", "table"):
            out.append((kind, getattr(node, "label", None) if kind in ("selectbox", "status") else
                        (node.value if kind in ("markdown", "caption") else "")))
    return out


# --- 2.1 Findings: fortune and livelihood --------------------------------

@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_prosperity_shows_its_summary_and_qualification_above_the_table_and_three_sibling_disclosures(depth):
    at = make_app(page="findings")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, "findings")
    assert (PROSPERITY, PROSPERITY_COLUMNS) in table_inventory(at)
    block = _between(at, PROSPERITY)
    kinds = [k for k, _ in block]
    # caption, summary, qualification, table, selectbox, three siblings
    assert kinds[:5] == ["caption", "markdown", "markdown", "dataframe", "selectbox"], kinds
    assert block[1][1].startswith("The first row is this app's synthesis: the class it reads from the first and second lords")
    assert block[2][1].startswith("**This app's synthesis.** A single seven-class outcome is not specified")
    assert block[4][1] == "Read details for"
    siblings = [(label, icon) for label, icon in _statuses(at)
                if label in ("How the prosperity reading is assembled",
                             "How the Lot and the triplicity lords are combined",
                             "Source passages, alternatives and coverage")]
    assert [label for label, _ in siblings] == ["How the prosperity reading is assembled",
                                                "How the Lot and the triplicity lords are combined",
                                                "Source passages, alternatives and coverage"]
    assert all(icon == NOTES_EXPANDER_ICON for _, icon in siblings)
    # No notes expander of the finding's own: the three siblings are the notes.
    assert not [k for k, label in block if k == "status" and label == "Sources and editorial notes"]
    heading = [h for h in at.main.subheader if h.value == PROSPERITY][0]
    assert heading.help == "Sahl's indications of fortune and livelihood. Display only; nothing scores it."


def test_prosperity_detail_prints_the_chosen_rows_four_cells_verbatim():
    at = make_app(page="findings").run()
    assert_no_exception(at, "findings")
    table = [df.value for df in at.main.dataframe if list(df.value.columns) == PROSPERITY_COLUMNS][0]
    box = [s for s in at.main.selectbox if s.key == "sahl_indications_of_fortune_and_livelihood_detail"][0]
    assert box.value is None and box.placeholder == "Select a row to read its grounds and source passages"
    classes = list(table["Class"])
    expected = classes if len(set(classes)) == len(classes) else [f"{n}. {c}" for n, c in enumerate(classes, 1)]
    assert box.options == expected
    assert not [m for m in at.main.markdown if m.value.startswith("**Ground.**")]
    box.select(box.options[0])
    at.run()
    assert_no_exception(at, "findings, a row chosen")
    row = table.iloc[0]
    printed = [m.value for m in at.main.markdown if m.value.startswith(("**Class.**", "**Ground.**", "**Sahl.**", "**Also.**"))]
    assert printed == [f"**{field}.** {row[field]}" for field in PROSPERITY_COLUMNS if row[field]]


def test_prosperity_disclosures_keep_every_locator_of_the_old_notes_and_list_the_unevaluated_passages():
    at = make_app(page="findings").run()
    assert_no_exception(at, "findings")
    text = "\n".join(m.value for m in at.main.markdown)
    for locator in ("2.1, 2-9", "2.11, 1-3", "2.11, 5", "2.13, 40", "2.11, 4", "2.3, 22", "2.3, 17-18", "2.13, 48",
                    "2.3, 6", "2.3, 10", "2.16, 5", "2.20, 1", "2.20, 2", "2.11, 14", "2.3, 19", "2.17, 8", "2.19, 6",
                    "III.2.5 [5.1]", "III.2.4 [4.5]", "III.2.1 [1.7]", "fn 255", "fn 256", "fn 258", "fnn 225-226",
                    "Figures 10-21"):
        assert locator in text, locator
    for phrase in ("Sahl gives an order of investigation (2.3, 6, then 2.3, 10,",
                   "says the combination is this app's",
                   "this app installs no priority",
                   "falling (2.11, 3) or under the rays (2.11, 5)",
                   "\"Made unfortunate\" is read by this app as a lord weak (falling, or under the rays)"):
        assert phrase in text, phrase
    rows = re.findall(r"^\| (2\.[^|]+?) \| ([^|]+?) \|$", text, re.M)
    assert [p for p, _ in rows] == ["2.3, 3, 4-5", "2.3, 8", "2.3, 10-11", "2.3, 13-16, 23-24", "2.11, 6-13 and 15-19",
                                    "2.13 apart from 39-40 and 48-51", "2.16, 3", "2.17, 6, 9, 12-14 and 2.18",
                                    "2.19, 3-4 and 7-9", "2.20, 3-6", "2.2's fixed stars", "2.4-2.10 and 2.12-2.15"]
    assert dict(rows)["2.3, 3, 4-5"] == "Not read, except as the grade's footing (fnn 82-83)"
    assert dict(rows)["2.16, 3"] == "Not read, except as the grade"
    assert "> \"" in text          # the quotations are blockquotes


def test_a_garbage_prosperity_selection_renders_nothing_and_raises_nothing():
    at = make_app(page="findings")
    at.session_state["sahl_indications_of_fortune_and_livelihood_detail"] = "no such row"
    at.run()
    assert_no_exception(at, "findings, garbage selection")
    assert not [m for m in at.main.markdown if m.value.startswith("**Ground.**")]


# --- 2.2 Dignities: Topical Planets in Houses ------------------------------

PLANETS_KEY = "topical_planets_in_houses_detail"
PLANETS_GRID = "topical_planets_in_houses_grid"


def _planet_lines(at):
    return [m.value for m in at.main.markdown if re.match(r"^\*\*\w+ in the \d+\w\w place\.\*\* Lean: ", m.value)]


def test_the_planets_panel_is_reached_by_the_selectbox_and_by_a_row_click_through_one_key():
    # Keyboard path: the selectbox alone.
    at = make_app(page="dignities").run()
    assert_no_exception(at, "dignities")
    box = [s for s in at.main.selectbox if s.key == PLANETS_KEY][0]
    grid = [df.value for df in at.main.dataframe if list(df.value.columns) == ['Planet', 'Placed in (WS place)', 'Lean']][0]
    assert box.value is None and box.options == list(grid["Planet"]) == ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    assert box.placeholder == "Select a planet to read its complete entries and sources"
    assert not _planet_lines(at)
    box.select("Venus")
    at.run()
    assert_no_exception(at, "dignities, Venus chosen")
    assert [l.startswith("**Venus in the ") for l in _planet_lines(at)] == [True]
    assert at.session_state[PLANETS_KEY] == "Venus"
    # Pointer path: a grid row selected writes the same key before the
    # selectbox is drawn, so the selectbox shows the planet and the panel
    # is the same panel.
    at = make_app(page="dignities")
    at.session_state[PLANETS_GRID] = {"selection": {"rows": [4], "columns": []}}
    at.run()
    assert_no_exception(at, "dignities, row 4 clicked")
    assert at.session_state[PLANETS_KEY] == "Mars"
    assert [s for s in at.main.selectbox if s.key == PLANETS_KEY][0].value == "Mars"
    assert [l.startswith("**Mars in the ") for l in _planet_lines(at)] == [True]
    # The grid's selection standing, the selectbox then moved: the
    # selectbox is the state and the panel follows it.
    [s for s in at.main.selectbox if s.key == PLANETS_KEY][0].select("Jupiter")
    at.run()
    assert_no_exception(at, "dignities, Jupiter after Mars")
    assert [l.startswith("**Jupiter in the ") for l in _planet_lines(at)] == [True]
    # A second click on a different row moves it again.
    at.session_state[PLANETS_GRID] = {"selection": {"rows": [0], "columns": []}}
    at.run()
    assert_no_exception(at, "dignities, row 0 clicked")
    assert [l.startswith("**Sun in the ") for l in _planet_lines(at)] == [True]


def test_the_planets_panel_prints_whole_conditional_entries_and_the_deferred_count_leads_to_them(engine):
    at = make_app(page="dignities").run()
    grid = [df.value for df in at.main.dataframe if list(df.value.columns) == ['Planet', 'Placed in (WS place)', 'Lean']][0]
    readings = [t.value for t in at.main if getattr(t, "type", None) == "table"
                and 'Rhetorius and Firmicus, as the texts state it' in t.value.columns][0]
    for _, g in grid.iterrows():
        planet, house = g['Planet'], int(g['Placed in (WS place)'])
        entries = engine["PLANETS_IN_HOUSES"][house][planet]['Rhetorius']
        cell = readings[readings['Planet'] == planet].iloc[0]['Rhetorius and Firmicus, as the texts state it']
        deferred = re.search(r"(\d+) conditional entr(?:y|ies) in the row's detail", cell)
        at2 = make_app(page="dignities")
        at2.session_state[PLANETS_KEY] = planet
        at2.run()
        assert_no_exception(at2, planet)
        printed = [m.value for m in at2.main.markdown if m.value.startswith(("Rhetorius", "Firmicus"))]
        assert printed == [engine["rhetorius_entry_text"](e) for e in entries], planet
        if deferred:
            assert len(entries) - len(printed) == 0 and int(deferred.group(1)) == sum(e['conditional'] for e in entries), planet
        # every conditional entry is printed whole, never cut before its condition
        for e, text in zip(entries, printed):
            assert e['text'] in text, (planet, e['cite'])


def test_a_garbage_planet_selection_renders_no_panel():
    at = make_app(page="dignities")
    at.session_state[PLANETS_KEY] = "Pluto"
    at.run()
    assert_no_exception(at, "dignities, garbage")
    assert not _planet_lines(at)
    assert [s for s in at.main.selectbox if s.key == PLANETS_KEY][0].value is None


# --- 2.3 The releaser ------------------------------------------------------

RELEASER = "The releaser and the house-master (Sahl, *On Nativities* 1.15-1.16, 1.20)"
RELEASER_NOTES = ("Place tests and candidate selection", "Lunations, looking, and the house-master",
                  "Years granted and alternative procedures")


def _expander_text(at, label, containing=""):
    """The markdown of the first book-icon expander with this label (and,
    when given, holding this text)."""
    for node in at.main:
        if getattr(node, "type", None) == "status" and node.label == label:
            text = "\n".join(m.value for m in node.markdown)
            if containing in text:
                return text
    raise LookupError(label)


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_the_releaser_shows_its_method_and_qualification_then_three_sibling_disclosures(depth):
    at = make_app(page="releaser")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, "releaser")
    heading = [h for h in at.main.subheader if h.value == RELEASER][0]
    assert heading.help == ("Not PN IV: Abu Ma'shar lists the five candidates (III.3, 1) and sends the reader to "
                            "another book for the choice (IX.8, 123).")
    block = _between(at, RELEASER)
    assert block[0][0] == "markdown" and block[0][1].startswith("Nawbakht's procedure in Sahl, On Nativities 1.15: by day the Sun")
    assert "is read as a test of the planet's power and counted by the Alchabitius divisions with the five-degree allowance at the four axial degrees only" in block[0][1]
    assert "the Lot of Fortune (a candidate by night, 1.15, 14) has no dynamic angularity and is tested by its whole-sign place" in block[0][1]
    assert "the years the house-master grants are granted from On Nativities 1.20, 7-34 read in full" in block[0][1]
    assert block[1] == ("markdown", "**Readings made here, each one Sahl leaves open.**")
    labels = [label for label, icon in _statuses(at) if icon == NOTES_EXPANDER_ICON]
    assert [l for l in labels if l in RELEASER_NOTES] == list(RELEASER_NOTES)
    # No caption of the old readings survives on the page.
    assert not [c for c in at.main.caption if c.value.startswith("Readings made here")]


def test_the_releaser_disclosures_carry_the_two_tables_and_every_reading():
    at = make_app(page="releaser").run()
    assert_no_exception(at, "releaser")
    places = _expander_text(at, RELEASER_NOTES[0])
    rows = re.findall(r"^\| (.+?) \| (.+?) \|$", places, re.M)
    assert ("The places: \"a stake or what follows a stake\" (1.15, 6-16)",
            "A test of the planet's power, counted by the Alchabitius divisions with the five-degree allowance at the four axial degrees only") in rows
    assert ("The Lot of Fortune (a candidate by night, 1.15, 14)", "Its whole-sign place; it has no dynamic angularity") in rows
    assert ("The meeting's and the fullness's degrees (1.15, 6-8, 12)", "The division, an open reading; they are neither planet nor Lot") in rows
    assert ("\"In good places\" for the Ascendant's lord (1.15, 16)",
            "Sahl's seven praised places, counted by whole-sign place; the identification is an interpretation") in rows
    assert ("Day", "the Sun, the meeting, then the Ascendant") in rows
    assert ("Night", "the Moon, the fullness, the Lot of Fortune, then the Ascendant") in rows
    # The five-degree allowance keeps its direction, unit and extent.
    assert ("a planet 0-5 degrees past the Ascendant, Midheaven, setting degree or fourth into the cadent division keeps "
            "the stake's power, measured from the axial degree, in longitude") in places
    assert "here the five degrees stay at the four stakes and the places are Sahl's" in places
    # The order table is followed by the sentence that every candidate needs its place and a looking lord.
    assert places.index("| Night |") < places.index("Each needs its place -- by day")
    assert "1.15, 15 lists all five before the Ascendant and is read as the summary of the two lists" in places
    assert re.search(r"^- 1\.16, 4 \(", places, re.M) and re.search(r"^- 1\.18, 8-10 \(", places, re.M) and re.search(r"^- 1\.15, 5 \(", places, re.M)
    lunations = _expander_text(at, RELEASER_NOTES[1])
    for phrase in ("The meeting is the last New Moon and the fullness the last Full Moon before birth",
                   "when both or neither is above the earth this app takes the Moon's degree",
                   "The Moon default is Valens's; the sages' tie rule is named here and not adopted",
                   "\"Looking\" is the whole-sign aspect, and a lord in the candidate's own sign counts as looking (1.20, 4).",
                   "A candidate is not its own house-master except in 1.16's four signs.",
                   "1.16: the Sun in Aries or Leo, the Moon in Taurus or Cancer, is both.",
                   "The triplicity lord is the lord of the sect.",
                   "1.20, 2-4 rank the lords: bound, house, exaltation, triplicity, image; two shares beat one",
                   "\"In good places\" for the Ascendant's lord (1.15, 16): Sahl's seven praised places"):
        assert phrase in lunations, phrase
    years = _expander_text(at, RELEASER_NOTES[2])
    assert "The **years** the house-master grants are granted from On Nativities 1.20, 7-34 read in full, above" in years
    assert "the Fardar and ages page's Planetary years table shows 1.20's grade for every planet" in years
    assert "On Times 4, 2-5's shorter list (victor by testimony, seven candidates)" in years
    assert "No worked example exists in Sahl." in years
    assert "the app " not in places + lunations + years


def test_the_house_masters_years_and_abu_alis_additions_keep_their_flags_and_display_only_status():
    at = make_app(page="releaser")
    at.session_state["_reading_depth"] = READING_DEPTHS[1]
    at.run()
    assert_no_exception(at, "releaser, supplement")
    years = [m.value for m in at.main.markdown if m.value.startswith("**The house-master's years**")]
    assert len(years) == 1
    assert "\n\nPlaced by division " in years[0] and "(the **power** unit).\n\nThese are the years the infortunes may cut off (1.23, 53 and 61)" in years[0]
    additions = [h for h in at.main.subheader if h.value.startswith("Additions and subtractions to the house-master's years")]
    assert len(additions) == 1
    assert additions[0].help == ("What each planet joined to the house-master or looking at it would add to or subtract "
                                 "from its years by Abu 'Ali's chapter.")
    block = _between(at, additions[0].value)
    assert block[0][0] == "caption" and block[0][1].startswith("Supplement · display only · ")
    assert block[1][0] == "markdown" and block[1][1].startswith("What each planet joined to the house-master or looking at it would add to or subtract from its years by Abu 'Ali's chapter: a fortune joined, trine or sextile adds its lesser years")
    assert block[2] == ("markdown", "**Display only:** no sum is formed, and Sahl's grant above is not changed.")
    assert block[3][0] == "dataframe"
    notes = _expander_text(at, "Sources and editorial notes", "Abu 'Ali's chapter, whole")
    # Re-pinned on branch C: the engine note's one section is five headed
    # sections (its paragraphs), the first "What the rows state.".
    for section in ("**Abu 'Ali's chapter, whole.**", "**What the rows state.**", "**Conventions of this display.**",
                    "**Abu Bakr, a witness beside Abu 'Ali.**", "**'Umar al-Tabari, a witness.**"):
        assert section in notes, section
    assert "Display only: no total is formed and these rows do not change the Sahl-based grant of the years above" in notes
    assert "> \"" in notes


# --- 2.4 Victors: the governor and the worksheet ---------------------------

GOVERNOR = "Governor of the syzygy degree: the five lords under 1.7, 3-7"


def test_the_governor_disclosure_keeps_its_table_and_holds_the_four_headed_sections(engine):
    at = make_app(page="victors").run()
    assert_no_exception(at, "victors")
    # The core sentence is visible under the syzygy table, before the expander.
    block = _between(at, "Prenatal Lunation (Syzygy)", "Victor of the Chart")
    assert block[0][0] == "dataframe"
    assert block[1] == ("markdown", "**The verdict** names a planet only where the text's clear subcases decide, and "
                                    "otherwise says \"unresolved\" with each candidate's profile.")
    # The expander is not a notes expander (no icon): the walker keys its table under its label.
    expanders = [(n.label, n.icon) for n in at.main if getattr(n, "type", None) in ("expander", "status")]
    assert (GOVERNOR, "") in expanders
    assert (GOVERNOR, [c for c in table_inventory(at) if c[0] == GOVERNOR][0][1]) in table_inventory(at)
    governor = [n for n in at.main if getattr(n, "type", None) == "expander" and n.label == GOVERNOR][0]
    text = "\n".join(m.value for m in governor.markdown)
    for section in ("**How the governor is decided.**", "**Interpretive choices.**", "**The three results compared.**",
                    "**Source passages, and what is not modelled.**"):
        assert section in text, section
    assert text.index("**How the governor is decided.**") < text.index("**Interpretive choices.**") < \
        text.index("**The three results compared.**") < text.index("**Source passages, and what is not modelled.**")
    rows = dict(re.findall(r"^\| (.+?) \| (.+?) \|$", text, re.M))
    assert rows["\"In a stake\""].startswith("Read by the division (Alchabitius, the five degrees at the four axial degrees)")
    assert rows["The Moon's side"] == "The same rising-before-the-Sun rule as the planets', the texts not defining her easternness for this procedure"
    assert rows["The Sun's side"] == "A claim-holder whose side relative to himself is not applicable, so 3 neither prefers nor sets him aside"
    assert rows["The chart the conditions are read in"].startswith("The natal chart, the target degree being the lunation's")
    assert engine["SAHL_1_7_UNMODELLED"] in text and engine["SAHL_1_7_MODEL_DISCLOSURE"] in text
    assert "> \"you will know the one in charge of that portion from five things" in text
    assert "[Sahl I p. 265]" in text
    assert "Where the three differ, the difference is the finding." in text
    assert not [c for c in governor.caption]


def test_the_victor_worksheet_shows_three_steps_and_the_two_by_two_of_the_four_computed_combinations(engine):
    at = make_app(page="victors").run()
    assert_no_exception(at, "victors")
    heading = [h for h in at.main.subheader if h.value == "Victor of the Chart"][0]
    assert heading.help == ("Ibn Ezra's victor worksheet (his book is not in hand), reproduced cell for cell so it can be "
                            "checked against a hand-filled sheet.")
    block = _between(at, "Victor of the Chart")
    assert block[0] == ("caption", "ibn Ezra's victor #1, 1485/1537")
    steps = block[1][1]
    assert steps.startswith("1. The first five rows score each planet's essential-dignity claim **at that point's** degree")
    assert "\n2. Then Lord of the Day (+7), Lord of the Hour (+6) and Places are added **once** each, not per point" in steps
    assert "\n3. Every column is summed into Totals, and the single highest total is the chart's victor." in steps
    grid = block[2][1]
    # Each cell is the scheme's own result, read off the page's own grids.
    results = {}
    for m in at.main.markdown:
        hit = re.match(r"^\*\*(.+?)\*\* — victor: \*\*(.+?)\*\* \((\d+)\)", m.value)
        if hit:
            results[hit.group(1)] = (hit.group(2), hit.group(3), "Tied at the top" in m.value)
    assert len(results) == 4
    lines = grid.split("\n")
    assert lines[0] == "| Dignity weights | Older places | Newer places |"
    for line, w in ((lines[2], "Older"), (lines[3], "Newer")):
        cells = [c.strip() for c in line.strip("|").split("|")]
        assert cells[0] == w
        for cell, p in ((cells[1], "Older"), (cells[2], "Newer")):
            scheme = f"{w} weights + {p} places" + (" (matched preset)" if w == p else "")
            victor, total, tied = results[scheme]
            assert cell.startswith(f"**{victor}** ({total})"), (scheme, cell)
            assert (", matched preset" in cell) == (w == p), (scheme, cell)
            assert (", tied at the top" in cell) == tied, (scheme, cell)
    # The full worksheets stay as detail: two matched grids, two in the cross-check expander.
    assert len([n for n in at.main if getattr(n, "type", None) == "expander"
                and n.label == "Cross-check: the two unmatched weight/place pairings"]) == 1
    notes = _expander_text(at, "Sources and editorial notes", "Two independent axes")
    for section in ("**The weights and the places.**", "**Two independent axes.**", "**The \"Older\" attribution.**",
                    "**Dykes's critique of the weighting.**", "**Ibn Ezra's later victor, not implemented.**"):
        assert section in notes, section
    assert "The seven planets are the columns." in notes and "ITA I.18 fn 211" in notes
    assert "so it is not implemented rather than guessed" in notes


# --- 2.5 Sources and readings ---------------------------------------------

def _registry():
    """READINGS_REGISTRY as the UI half states it: (label, widget key, store
    key, default expression, page)."""
    src = ui_source()
    body = src[src.index("READINGS_REGISTRY = ("):src.index(")\n", src.index("READINGS_REGISTRY = ("))]
    return re.findall(r'\("([^"]+)", "(\w+)", "(\w+)", ([^,]+), "([^"]+)"\)', body)


def test_the_sources_page_runs_in_the_new_order_with_the_citation_key_and_the_connection_table():
    at = make_app(page="sources").run()
    assert_no_exception(at, "sources")
    heads = [h.value for h in at.main.subheader]
    assert heads == ["Readings in force", "How citations are written", "Connection rule: Sahl and Abu Ma'shar", "Configurable readings"]
    caption = [c.value for c in at.main.caption if c.value.startswith("This app ")][0]
    assert caption.endswith("What this app reads from, how it can be read, and what it does not cover.")
    key_block = _between(at, "How citations are written", "Connection rule: Sahl and Abu Ma'shar")
    assert [k for k, _ in key_block] == ["markdown", "markdown", "markdown"]   # sentence, the table at page width, sentences
    key = "\n".join(text for _, text in key_block)
    assert key.startswith("A locator names its volume, never the author alone.")
    rows = re.findall(r"^\| (.+?) \| (.+?) \| (.+?) \|$", key, re.M)
    abbreviations = [a for a, _w, _e in rows]
    for wanted in ("Gr. Intr.", "PN IV", "ITA", "Abbr.", "Abu Bakr, On Nativities", "'Umar al-Tabari, Book of Nativities",
                   "Masha'allah, Book of Aristotle", "Abu 'Ali al-Khayyat, Judgments of Nativities",
                   "Sahl, The Introduction", "Sahl, On Nativities"):
        assert wanted in abbreviations, wanted
    examples = {a: e for a, _w, e in rows}
    assert examples["Gr. Intr."] == "Gr. Intr. VII.6, 27" and examples["PN IV"] == "PN IV IX.1, 26"
    assert examples["ITA"] == "ITA I.22 (al-Qabisi)" and examples["Abbr."] == "Abbr. II.27"
    assert "Both of Abu Ma'shar's volumes have a Book VII, which is why his name alone no longer locates anything." in key
    assert "On the Prediction pages other than The releaser, whose rules all come from PN IV, its locators are bare Book.chapter, sentence." in key
    connection = _between(at, "Connection rule: Sahl and Abu Ma'shar", "Configurable readings")
    assert [k for k, _ in connection][:3] == ["markdown", "markdown", "markdown"]   # intro, the table at page width, scope
    text = "\n".join(text for kind, text in connection[:3])
    assert text.startswith("Which author's rule decides whether a pair counts as Connected.")
    rows = re.findall(r"^\| (.+?) \| (.+?) \| (.+?) \|$", text, re.M)
    assert rows[0] == ("Question", "Sahl, as implemented", "Abu Ma'shar, as implemented")
    assert rows[1][0] == "Which distance governs?" and "15/12/9/8/7 by planet" in rows[1][1] and "VII.4, 3" in rows[1][2] and "VII.5, 27" in rows[1][2]
    assert rows[2][0] == "What happens at a sign boundary?" and "(20-21)" in rows[2][1] and "(VII.5, 14)" in rows[2][2]
    assert rows[3] == ("Source", "The Introduction Ch. 3, 6-21", "Gr. Intr. VII.4-5")
    assert text.endswith("the Configurations page has its own control for which author you want to **see**.")
    alternative = _expander_text(at, "The two rules in full, and the alternative reading")
    assert "**Alternative reading: reciprocal light, not implemented.**" in alternative
    assert "A **dissenting reading** is recorded in the code but not implemented." in alternative
    assert "the reciprocal one would move about 5% of applying pairs, and only half of those involve the Sun." in alternative
    assert "**Sahl's rule.**" in alternative and "**Abu Ma'shar's rule.**" in alternative


def test_every_registry_reading_has_its_section_with_the_value_in_force():
    at = make_app(page="sources", switches={"domain": "Masha'allah"}).run()
    assert_no_exception(at, "sources")
    registry = _registry()
    assert len(registry) == 9
    block = _between(at, "Configurable readings")
    captions = [text for kind, text in block if kind == "caption" and text.startswith("In force: ")]
    assert len(captions) == len(registry)
    table = [df.value for df in at.main.dataframe if "In force" in df.value.columns][0]
    for (label, _wk, _sk, _default, page), caption, (_, row) in zip(registry, captions, table.iterrows()):
        assert row["Reading"] == label
        assert caption == f"In force: {row['In force']} · default: {row['Default']} · set on the {page} page", caption
    leads = [text for kind, text in block if kind == "markdown" and text.startswith("**")]
    assert [l.split("**")[1] for l in leads] == [
        "Connection test used in the shared tables",
        "VII.6, 27/45 'eastern/western relative to the Sun'",
        "Fitting infortune (Sahl, Choices Ch. 1, 12)",
        "Moon under the rays to 15 degrees (Sahl, On Nativities 1.19, 6)",
        "Mars under the rays to 18 degrees west (Dykes's table in On Nativities 1.22, fn 175)",
        "Domain (hayz)", "House-based Lots measure to the", "Monthly profections turn", "Sources shown"]
    affects = [text for kind, text in block if kind == "markdown" and text.startswith("Affects: ")]
    assert len(affects) == 5
    assert "In force: Masha'allah · default: Gr. Intr. · set on the Dignities and places page" in captions or \
        any("Masha'allah" in c and "Dignities and places" in c for c in captions)
    # No second set of controls: the one radio on the page is Sources shown.
    assert [r.label for r in at.main.radio] == ["Sources shown"]


# --- 2.6 Configurations: Planetary Condition and correction 9a --------------

CONDITION_KEY = "planetary_condition_detail"
NET_BAND = "a Net of −1, 0 or +1 is Indeterminate"


def _configurations(**switches):
    at = make_app(page="configurations", switches=switches or None)
    at.session_state["_reading_depth"] = READING_DEPTHS[1]
    at.run()
    assert_no_exception(at, "configurations, supplement")
    return at


def test_the_condition_qualification_stands_above_the_table_and_the_panel_lists_the_labels(engine):
    at = _configurations()
    block = _between(at, "Planetary Condition")
    assert block[0] == ("caption", "Gr. Intr. VII.6")
    markdown = [text for kind, text in block if kind == "markdown"]
    assert markdown[0].startswith(":orange[**Net and Verdict are this app's heuristic, not Abu Ma'shar's.**] He enumerates these conditions")
    assert f"{NET_BAND} on both pages" in markdown[0]
    kinds = [k for k, _ in block]
    assert kinds.index("markdown") < kinds.index("dataframe") < kinds.index("selectbox")
    table = [df.value for df in at.main.dataframe if "Verdict" in df.value.columns and "Moon Defects" in df.value.columns][0]
    box = [s for s in at.main.selectbox if s.key == CONDITION_KEY][0]
    assert box.value is None and box.placeholder == "Select a planet to read its conditions in words"
    # The options are the displayed table's first column, in its order (the
    # table is sorted by Net, so this is not the evaluator's planet order).
    assert box.options == list(table["Planet"])
    assert box.options != ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    for planet in ("Moon", "Saturn"):
        at2 = _configurations()
        [s for s in at2.main.selectbox if s.key == CONDITION_KEY][0].select(planet)
        at2.run()
        assert_no_exception(at2, planet)
        lines = [m.value for m in at2.main.markdown]
        row = table[table["Planet"] == planet].iloc[0]
        head = [l for l in lines if l.startswith(f"**{planet}.** Good Fortune ")][0]
        expected = (f"**{planet}.** Good Fortune {row['Good Fortune']} · Strength {row['Strength']} · Weakness {row['Weakness']} · "
                    f"Misfortune {row['Misfortune']}" + (f" · Moon Defects {row['Moon Defects']}" if row['Moon Defects'] else "")
                    + f" · Net {row['Net']} · Verdict {row['Verdict']}")
        assert head == expected
        positive = [l for l in lines if l.startswith("**Good Fortune / Strength**")][0]
        negative = [l for l in lines if l.startswith("**Weakness / Misfortune**")][0]
        # The bullets are the engine's arrays, not the joined cell split on commas.
        bullets = lambda text: [b[2:] for b in text.split("\n") if b.startswith("- ")]
        joined = lambda labels: ", ".join(labels) if labels else "-"
        assert joined(bullets(positive)) == row["Good Fortune / Strength"]
        assert joined(bullets(negative)) == row["Weakness / Misfortune"]
        if planet == "Moon":
            assert row["Moon Defects"] != "" and " · Moon Defects " in head
    notes = _expander_text(at, "Sources and editorial notes", "The two Moon checklists")
    for section in ("**The two Moon checklists.**", "**How this app's count is formed.**", "**Enclosure under this source.**"):
        assert section in notes, section
    assert "Sahl's ten (The Introduction Ch. 3, 103-112) are a different list" in notes
    assert "it fires on roughly 43% of placements" in notes


def test_correction_9a_the_indeterminate_band_is_minus_one_to_plus_one_on_both_pages(engine):
    """The engine's abs(net) <= 1 for the Condition verdict and for the
    Dignities Lean; the Configurations copy says so in the qualification
    and in the notes, and the Dignities page's own words agree."""
    import inspect
    assert "abs(net) <= 1" in inspect.getsource(engine["evaluate_planets_in_houses"])
    assert "abs(net) <= 1" in engine_source_of("evaluate_abu_mashar_condition")
    at = _configurations()
    texts = [m.value for m in at.main.markdown]
    assert any(f"{NET_BAND} on both pages" in t for t in texts)
    assert any(f"{NET_BAND} in both places" in t for t in texts)
    assert not any("a Net of zero" in t for t in texts + [c.value for c in at.main.caption])
    dignities = make_app(page="dignities").run()
    assert any("reads Indeterminate within a margin of one, which is the width of a single testimony" in m.value
               for m in dignities.main.markdown)
    heading = [h for h in at.main.subheader if h.value == "Planetary Condition"][0]
    assert "for the Moon only, his own eleven corruptions (63-74)" in heading.help


def engine_source_of(name):
    from conftest import function_source
    return function_source(name)


# --- Fixed in passing: the tabs keep their place in the element tree --------
# A conditional element drawn directly in the main block before st.tabs
# (the readings-off-default note, the fitting-infortune line, the stale-date
# warning) shifted the tabs' delta path between runs, and the frontend then
# treated them as a new tabs widget and opened the first tab on every rerun
# a control inside a tab caused. Each such element now takes a fixed
# st.empty() slot (the strip and the stale warning share one, the caption
# alone or a container with both). The invariant AppTest can pin: the tabs'
# position among the main block's direct children is the same with and
# without those elements filled, which holds the tab selection by
# construction.

def _tabs_index(at):
    kinds = [getattr(child, "type", None) for child in at.main.children.values()]
    assert "tab_container" in kinds, kinds
    return kinds.index("tab_container"), kinds[:kinds.index("tab_container")]


@pytest.mark.parametrize("page", ["configurations", "timing"])
def test_the_tabs_keep_their_place_whatever_the_readings_say(page):
    plain = make_app(page=page).run()
    assert_no_exception(plain, page)
    changed = make_app(page=page, switches={"domain": "Masha'allah", "connection": "Abu Ma'shar"})
    changed.session_state["_fitting_infortune"] = True
    changed.run()
    assert_no_exception(changed, f"{page}, readings changed")
    index, before = _tabs_index(plain)
    index_changed, before_changed = _tabs_index(changed)
    assert index == index_changed, (before, before_changed)
    # The reserved slots are filled, not added: on Configurations the note
    # (three readings off default here, so a container with the count and the
    # list since readability branch B, 2026-09-17) and the fitting-infortune
    # line stand where the plain run had empties, at the same positions.
    if page == "configurations":
        assert any(c.value.startswith("3 readings differ from defaults") for c in changed.main.caption)
        assert any(c.value.startswith("Fitting infortune") for c in changed.main.caption)
        assert not any(c.value.startswith(("Readings in force that differ", "3 readings differ")) for c in plain.main.caption)
        empties = [i for i, k in enumerate(before) if k == "empty"]
        assert len(empties) >= 2 and all(before_changed[i] in ("empty", "caption", "flex_container") for i in empties)
    # Every fixed slot is drawn by the app's own helpers, never as a bare
    # conditional element: by source, the three sites use st.empty().
    src = ui_source()
    assert "slot = st.empty()" in src[src.index("def _readings_note"):src.index("def _readings_note") + 900]
    strip = src[src.index("def _chart_strip"):src.index("def _stale_notice")]
    assert "slot = st.empty()" in strip and "with slot.container():" in strip and "slot.caption(strip)" in strip
    assert "_fitting_slot = st.empty()" in src[src.index("def page_configurations"):src.index("_tabs = st.tabs(_labels)")]
