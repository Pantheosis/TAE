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
    assert box.value is None and box.options == ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
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
    for section in ("**Abu 'Ali's chapter, whole.**", "**What the rows state, and the conventions of this display.**",
                    "**Abu Bakr, a witness beside Abu 'Ali.**", "**'Umar al-Tabari, a witness.**"):
        assert section in notes, section
    assert "Display only: no total is formed and these rows do not change the Sahl-based grant of the years above" in notes
    assert "> \"" in notes
