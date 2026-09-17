"""The P2 blocks outside Prediction, readability branch B (2026-09-17),
migrated onto the renderer contract of branch A: what each block now
renders, from the same rows it rendered before.

Nothing here tests doctrine; the engine is byte-identical to main. Each
test reads the page as AppTest renders it and checks the presentation the
branch promises: the visible summary and qualifications above a table, the
headed notes with the book icon, a detail selectbox whose options are the
displayed table's column in order and which prints the chosen row whole,
the threshold table built from the engine's constants, the readings note
with its count and list, and the two Dignities cross-references.
"""
from __future__ import annotations

import re

import pytest

from conftest import (NOTES_EXPANDER_ICON, READING_DEPTHS, assert_no_exception, make_app,
                      table_inventory, ui_source)

WITH_SUPPLEMENT = READING_DEPTHS[1]


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
        if inside and kind in ("markdown", "caption", "selectbox", "status", "dataframe", "table", "expander"):
            out.append((kind, getattr(node, "label", None) if kind in ("selectbox", "status", "expander") else
                        (node.value if kind in ("markdown", "caption") else "")))
    return out


def _markdown(at):
    return [m.value for m in at.main.markdown]


def _heading(at, title):
    hits = [h for h in at.main.subheader if h.value == title]
    assert len(hits) == 1, [h.value for h in at.main.subheader]
    return hits[0]


# --- Findings --------------------------------------------------------------

FINDINGS = {
    # title: (chart, glance, summary opening, qualification openings, section headings)
    "The fetus's stay (Sahl)": (
        "1240-05-23",
        "What 1.8 and 1.9 let this app state of the fetus's stay in the belly. Display only; nothing scores it.",
        "What 1.8 and 1.9 let this app state of the fetus's stay in the belly: the meeting before the birth",
        ["**Not computed.** 1.8's three divisions are framed from a chart the text does not name",
         "**This app's reading of the year.** This app takes the year as the calendar anniversary"],
        ["The meeting before the birth and its Ascendant (1.8, 5-6).",
         "The three divisions of 1.8, not computed.",
         "The three Moons of 1.9, 1, and the year.",
         "The aspects of 1.9, 2-10.",
         "The conception and the stay by the day and hour, not computed (1.9, 11-14)."]),
    "The Moon on the third day (Sahl)": (
        "1240-05-23",
        "The Moon on the third day -- two days after the birth, the birth day counted as the first. Display only; nothing scores it.",
        "The Moon on the third day -- two days after the birth, the birth day counted as the first: her sign and place",
        ["**The third day, this app's reading of Firmicus.** This app takes it two days after the birth"],
        ["The sentences: 1.29, 11-13 and 1.26, 7.", "The day count.", "The corruption tests.",
         "The four-footed signs.", "Clauses not evaluated: 1.29, 11 and 12."]),
    "Places harming the eyesight": (
        "1240-05-25",
        'The "degrees of chronic illness in the signs". Display only; nothing scores it; shown under Course text and supplement.',
        'The "degrees of chronic illness in the signs" -- the nebulous places named for the Pleiades',
        ["**This app's addition, and what is not tested.** Sahl's rule names the Moon and the lord of the Ascendant (48)",
         "**Method.** Neither table is precessed here: each is applied as printed. Readings, this app's: a degree named"],
        ["Sahl, On Nativities 6.2, 48-75: four lists.", "Abu Ma'shar, Gr. Intr. VI.20: the measured places.",
         "Two spans read from a phrase, and one bare number.", "Abu Bakr, On Nativities II.7.3: his list, beside the others."]),
    "The Moon's phase, Valens's eleven": (
        "1240-05-23",
        "Valens's eleven phases of the Moon, the chart's Moon placed in one by its angle ahead of the Sun. Display only; nothing scores it.",
        "Valens's eleven phases of the Moon, the chart's Moon placed in one by its angle ahead of the Sun, with what he says",
        ["**Phase boundaries used by this app.** Eight of his boundaries are degrees he gives"],
        ["Phase boundaries used by this app.", "Source phase list.", "Phase indications.", "Rulers actually named."]),
    "Affliction and fortification after Rhetorius": (
        "1240-05-23",
        "Rhetorius's definitions of a planet's being harmed (Ch. 27's list, with Ch. 41's besieging) or fortified (Ch. 42's list). Display only; nothing scores it.",
        "Rhetorius's definitions of a planet's being harmed (Ch. 27's list, with Ch. 41's besieging) or fortified (Ch. 42's list), a row per planet",
        ["**How this app reads each condition.** Where a chapter gives a degree (Ch. 41's seven, Ch. 34's three) it is applied"],
        ["The conditions tested, each with its reading.", "Rhetorius's chapters, as Holden has them.",
         "The besiegers of an afflicted planet."]),
    "Morin's rules for aspects into good and bad houses": (
        "1240-05-23",
        "Each trine, sextile, square or opposition that a Fortune (Jupiter, Venus) or an Infortune (Saturn, Mars) casts to another planet. Display only; nothing scores it.",
        "Each trine, sextile, square or opposition that a Fortune (Jupiter, Venus) or an Infortune (Saturn, Mars) casts to another planet, read by the kind of ray",
        ["**The unfortunate houses, this app's reading.** Morin says \"the unfortunate houses\" without listing them"],
        ["The four governing sentences, whole.", "The unfortunate houses, this app's reading.",
         "Quoted but not tested, and what is not read."]),
}


@pytest.mark.parametrize("title", list(FINDINGS))
def test_each_migrated_finding_shows_summary_qualifications_table_and_headed_notes(title):
    chart, glance, summary, qualifications, sections = FINDINGS[title]
    at = make_app(date=chart, page="findings")
    at.session_state["_reading_depth"] = WITH_SUPPLEMENT
    at.run()
    assert_no_exception(at, "findings")
    assert _heading(at, title).help == glance
    block = _between(at, title)
    kinds = [k for k, _ in block]
    n = len(qualifications)
    assert kinds[:3 + n] == ["caption"] + ["markdown"] * (1 + n) + ["dataframe"], kinds
    assert block[1][1].startswith(summary), block[1][1]
    for opening, (_, text) in zip(qualifications, block[2:2 + n]):
        assert text.startswith(opening), text
    notes = [(k, label) for k, label in block if k == "status"]
    assert notes == [("status", "Sources and editorial notes")], block
    icon = [icon for label, icon in _statuses(at) if label == "Sources and editorial notes"]
    assert icon and all(i == NOTES_EXPANDER_ICON for i in icon)
    headings = [m for m in _markdown(at) if m in {f"**{s}**" for s in sections}]
    assert headings == [f"**{s}**" for s in sections], headings


def test_the_findings_quotations_are_blockquotes_under_their_locators():
    at = make_app(date="1240-05-25", page="findings")
    at.session_state["_reading_depth"] = WITH_SUPPLEMENT
    at.run()
    assert_no_exception(at, "findings")
    text = "\n".join(_markdown(at))
    for locator_line in ("On Nativities 1.8, 5-6:\n\n> \"", "1.8, 3-4:\n\n> \"", "1.9, 1:\n\n> \"", "1.9, 2-10:\n\n> \"",
                         "1.9, 11:\n\n> \"", "1.9, 12-14:\n\n> \"",
                         "On Nativities 1.29, 11:\n\n> \"", "1.29, 12:\n\n> \"", "1.29, 13:\n\n> \"",
                         "1.29, 3 names the corruptions the chapter has in view:\n\n> \"", "1.26, 7's sign is taken from 1.38, 1:\n\n> \"",
                         "Sahl, On Nativities 6.2, 48:\n\n> \"", "Abu Ma'shar, Gr. Intr. VI.20, 1-3:\n\n> \"",
                         "Abu Bakr, On Nativities II.7.3 (p. 238):\n\n> \"",
                         "Abu Bakr, On Nativities II.1.0, the paragraph whole:\n\n> \"", "Dykes's fn 652, on \"unsound\":\n\n> \"",
                         "Valens lists the phases so:\n\n> \"1. New moon;", "as Riley has it:\n\n> \"We will append",
                         "Rhetorius Ch. 27 (Holden):\n\n> \"", "**Rhetorius Ch. 41 (Holden):**\n\n> \"",
                         "**Rhetorius Ch. 34 (Holden), where Ch. 27's note sends the word:**\n\n> \"",
                         "The four governing sentences, whole:\n\n> \"The distinction", "(ITA IV.4.1 fn 43):\n\n> \"That is,"):
        assert locator_line in text, locator_line
    # The fragments that followed a quotation on main still follow it.
    for tail in ("\"\n\n-- the meeting is the last New Moon before the birth;", "\") -- not computed: the meeting of the conception is not in hand.",
                 "\"\n\nSo the third-day Moon is read as corrupted", "\"\n\n-- Aries, Taurus, Leo and the second half of Sagittarius.",
                 "\"\n\n-- then 49-55, the places. 56-57:\n\n> \"", "\"\n\nHolden's notes name them: the fifth house and the ninth; the eleventh house."):
        assert tail in text, tail
    # The tested conditions are a list, before the chapters.
    conditions = text.index("**The conditions tested, each with its reading.**")
    assert text.index("**Rhetorius's chapters, as Holden has them.**") > conditions
    assert re.search(r"^- \*\*[^*]+\*\* \(Rhetorius Ch\. \d+ \(Holden\)", text[conditions:], re.M)


def test_the_mars_block_shows_its_sentences_at_reading_width_and_three_sections():
    at = make_app(page="findings")
    at.session_state["_reading_depth"] = WITH_SUPPLEMENT
    at.run()
    assert_no_exception(at, "findings")
    title = "Mars in his own domicile, by sect (Abu Bakr)"
    assert _heading(at, title).help == ("Abu Bakr, On Nativities II.1.0: Mars in his own domicile (Aries, Scorpio) by night, "
                                        "or by day. Display only; nothing scores it.")
    block = _between(at, title)
    assert [k for k, _ in block][:4] == ["markdown", "dataframe", "caption", "status"], block
    assert block[0][1].startswith("Abu Bakr, On Nativities II.1.0: Mars in his own domicile (Aries, Scorpio) by night, or by day; Mars in a domicile of Saturn")
    assert block[0][1].endswith("where none reaches him the row says so.")
    assert block[2][1].startswith("Supplement · display only · Abu Bakr, On Nativities II.1.0.")
    md = _markdown(at)
    for section in ("**The paragraph whole.**", "**Dykes's note on \"unsound\".**", "**This app's reading.**"):
        assert section in md, section
    assert any(m.startswith("How this app reads it: his own domicile is Aries or Scorpio") for m in md)


def test_the_findings_page_no_longer_says_the_app_in_the_migrated_blocks():
    src = ui_source()
    start, end = src.index("def page_findings():"), src.index("def page_dignities():")
    assert "the app's" not in src[start:end] and "the app " not in src[start:end]
