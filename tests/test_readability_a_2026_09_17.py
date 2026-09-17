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
