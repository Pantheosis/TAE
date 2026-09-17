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


# --- Dignities and places ------------------------------------------------

MOON_TITLE = "The Moon in the houses — PN IV VII.8, by her transit"
LORDS_TITLE = "Topical House Lords (Masha'allah)"


def _table_under(at, title, columns):
    frames = [df.value for df in at.main.dataframe if list(df.value.columns) == columns]
    assert len(frames) == 1, [list(df.value.columns) for df in at.main.dataframe]
    return frames[0]


def test_the_moon_in_the_houses_shows_its_summary_and_two_qualifications_then_the_table_and_a_selector(engine):
    at = make_app(page="dignities").run()
    assert_no_exception(at, "dignities")
    assert _heading(at, MOON_TITLE).help == ("A natal analogy: VII.8 reads the Moon's transit through the houses, and the natal "
                                             "Moon's own whole-sign house is marked.")
    block = _between(at, MOON_TITLE, LORDS_TITLE)
    assert [k for k, _ in block] == ["markdown", "markdown", "markdown", "dataframe", "selectbox"], block
    assert block[0][1].startswith("A natal analogy: VII.8 reads the Moon's transit through the houses from the three positions")
    assert "it supplies no condition split" in block[0][1]
    assert block[1][1].startswith("**The text's own reservation.** (From this indication) is the text's own reservation")
    assert block[2][1].startswith("**The translator's readings.** Where the translator reads conflicting dreams")
    table = _table_under(at, MOON_TITLE, ['House', 'Reading', 'Locator', 'Natal Moon here'])
    box = [s for s in at.main.selectbox if s.key == "the_moon_in_the_houses_pn_iv_vii_8_by_her_transit_detail"][0]
    assert box.value is None and box.placeholder == "Select a house to read the Moon's transit through it in full"
    ordinal = engine["HOUSE_ORDINAL"]
    assert box.options == [f"{ordinal[h]} house" + (" (the natal Moon's)" if natal == 'Yes' else "")
                           for h, natal in zip(table['House'], table['Natal Moon here'])]
    assert sum(1 for o in box.options if o.endswith("(the natal Moon's)")) == 1
    natal = [o for o in box.options if o.endswith("(the natal Moon's)")][0]
    box.select(natal)
    at.run()
    assert_no_exception(at, "dignities, a house chosen")
    row = table[table['Natal Moon here'] == 'Yes'].iloc[0]
    md = _markdown(at)
    assert f"**The Moon in the {ordinal[row['House']]} house.** {row['Reading']}" in md
    assert f"{row['Locator']}. Natal Moon here: Yes." in md


def test_the_house_lords_show_the_condition_and_its_implementation_apart_and_read_one_lord_with_its_result(engine):
    at = make_app(page="dignities").run()
    assert_no_exception(at, "dignities")
    assert _heading(at, LORDS_TITLE).help == ("For each of the twelve topical houses, its domicile lord's own whole-sign placement, and "
                                              "Masha'allah's delineation for that [placed-in, rules] pairing -- the classical way of "
                                              "reading what a house's ruler is \"doing\" elsewhere in the chart.")
    block = _between(at, LORDS_TITLE)
    kinds = [k for k, _ in block]
    assert kinds[:8] == ["markdown", "markdown", "markdown", "dataframe", "selectbox", "expander", "table", "status"], kinds
    assert block[0][1] == ("Every cell's wording is this app's paraphrase of Sahl's own sentence for that pairing, from his "
                           "twelve lords-of-places passages in On Nativities.")
    assert block[1][1] == ("**Masha'allah's condition.** Masha'allah's condition is his own, stated at the end of eight of the "
                           "twelve lord-of-the-Nth sections.")
    assert block[2][1].startswith("**This app's implementation.** Whole-sign: an infortune with, square or opposite the house or its lord")
    assert block[2][1].endswith("with the column saying whether he would apply them.")
    assert block[5][1] == "Masha'allah readings for lord placements" and block[7][1] == "Sources and editorial notes"
    grid = [df.value for df in at.main.dataframe if 'Averse to its place' in df.value.columns][0]
    readings = [t.value for t in at.main.table if "Masha'allah Signification" in t.value.columns][0]
    box = [s for s in at.main.selectbox if s.key == "topical_house_lords_masha_allah_detail"][0]
    assert box.value is None
    assert box.placeholder == "Select a topical house to read its lord's placement and Masha'allah's sentence"
    ordinal = engine["HOUSE_ORDINAL"]
    assert box.options == [f"Lord of the {ordinal[h]}: {lord}, in the {ordinal[placed]} place"
                           for h, lord, placed in zip(grid['Topical House'], grid['Domicile Lord'], grid['Placed in (WS place)'])]
    box.select(box.options[7])
    at.run()
    assert_no_exception(at, "dignities, a lord chosen")
    row, reading = grid.iloc[7], readings.iloc[7]
    md = _markdown(at)
    assert (f"**{box.options[7]}.** Masha'allah's condition: {row[chr(77) + chr(97) + 'sha' + chr(39) + 'allah' + chr(39) + 's condition']}. "
            f"Averse to its place: {row['Averse to its place']}.") in md
    assert f"**Masha'allah's signification.** {reading['Masha' + chr(39) + 'allah Signification']}" in md
    notes = "\n".join(md)
    for section in ("**The twelve passages, and the arrangement.**", "**Masha'allah's condition, where he states it.**"):
        assert section in md, section
    assert "the lord of the first 1.36, 79-97; the second 2.14, 9-28" in notes
    assert ("sections:\n\n> \"Work in this chapter if the lord of the third and the third [itself] were free of the infortunes, "
            "and the fortunes do not witness\"\n\n(On Nativities 3.10, 14; likewise 4.11, 24; 6.3.4, 24; 7.1, 217; 9.4, 35; "
            "10.2.4, 13; 11.1, 28; 12.1, 47).") in notes
    assert not [c for c in at.main.caption if c.value.startswith("Masha'allah's condition is his own")]


@pytest.mark.parametrize("switches, moon, mars_west", [({}, 12.0, 15.0), ({"moon_rays": True}, 15.0, 15.0),
                                                        ({"mars_west": True}, 12.0, 18.0)])
def test_the_dignity_thresholds_table_follows_the_constants_and_the_readings(engine, switches, moon, mars_west):
    at = make_app(page="dignities", switches=switches).run()
    assert_no_exception(at, "dignities")
    md = _markdown(at)
    statement = [m for m in md if m.startswith("**This app's ranking convenience.** The point weights are this app's own ranking convenience")]
    table = [m for m in md if m.startswith("| Planet | Burned within | Under the rays within |")]
    assert len(statement) == 1 and len(table) == 1
    # The statement stands before the score table, the method table after it.
    order = []
    for node in at.main:
        kind = getattr(node, "type", None)
        if kind == "markdown" and node.value in (statement[0], table[0]):
            order.append("statement" if node.value == statement[0] else "method table")
        elif kind == "dataframe" and 'Ess' in node.value.columns:
            order.append("score table")
    assert order == ["statement", "score table", "method table"]
    rows = dict((p, (b, r)) for p, b, r in re.findall(r"^\| (\w+) \| ([^|]+?) \| ([^|]+?) \|$", table[0], re.M)[1:])
    b = engine["SOLAR_BURNED_ORB"]
    assert list(rows) == list(b)
    assert rows["Saturn"] == (f"{b['Saturn'][0]:.0f}°", "15°") and rows["Venus"] == ("7°", "12° east / 15° west")
    assert rows["Moon"] == (f"{b['Moon'][0]:.0f}°", f"{moon:.0f}°")
    assert rows["Mars"] == (f"{b['Mars'][0]:.0f}°", f"18° east / {mars_west:.0f}° west" if mars_west != 18.0 else "18°")
    heart = [m for m in md if m.startswith("In the heart: within 16' (VII.2, 7-9, from the Sun's own apparent diameter).")]
    assert len(heart) == 1 and "Sahl elsewhere says one whole degree for the heart" in heart[0]
    assert any(m.startswith("**Domain/hayz** follows the Domain switch beside the Sect table above, currently ") for m in md)


# --- Lots ------------------------------------------------------------------

def test_the_classical_lots_key_pairs_each_lots_own_formula_with_where_it_is_stated():
    at = make_app(page="lots").run()
    assert_no_exception(at, "lots")
    key = [n for n in at.main if getattr(n, "type", None) == "status" and n.label == "Where the four classical Lots are stated"]
    assert len(key) == 1 and key[0].icon == NOTES_EXPANDER_ICON
    md = [m.value for m in key[0].markdown]
    table = [df.value for df in at.main.dataframe if 'Lot Name' in df.value.columns][0]
    rows = re.findall(r"^\| (Lot of \w+) \| ([^|]+?) \| ([^|]+?) \|$", md[0], re.M)
    assert [lot for lot, _, _ in rows] == list(table['Lot Name'])
    assert [formula for _, formula, _ in rows] == list(table['Formula'])
    where = dict((lot, stated) for lot, _, stated in rows)
    assert where['Lot of Fortune'] == where['Lot of Exaltation'] == "Stated in Sahl"
    assert where['Lot of Spirit'].startswith("Gr. Intr. VIII.3, 28-29") and "which Sahl names" in where['Lot of Spirit']
    assert where['Lot of Basis'].startswith("Gr. Intr. VIII.4, 22-24") and "fn 67: the Greek Basis" in where['Lot of Basis']
    assert md[1] == "**The four, in the sources' words.**"
    assert md[2].startswith("Fortune and Exaltation are stated in Sahl. Spirit -- the Lot of the Invisible, which Sahl names -- is stated at")
    assert md[2].endswith("All four carry their provenance under Provenance and standing per Lot, below the Topical Lots table.")


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_a_lots_provenance_is_read_by_selecting_it_and_the_comparison_table_stays(depth):
    at = make_app(page="lots")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, "lots")
    table = [t.value for t in at.main.table if 'Editor’s note' in t.value.columns][0]
    box = [s for s in at.main.selectbox if s.key == "provenance_and_standing_per_lot_detail"][0]
    assert box.value is None and box.placeholder == "Select a Lot to read its standing, source and editor's note"
    assert box.options == list(table['Lot'])
    expanders = [e.label for e in at.main.get("expander")]
    assert "Provenance and standing per Lot" in expanders
    death = [o for o in box.options if o == "Lot of death"][0]
    box.select(death)
    at.run()
    assert_no_exception(at, "lots, a Lot chosen")
    row = table[table['Lot'] == "Lot of death"].iloc[0]
    md = _markdown(at)
    assert f"**{row['Topic']}: Lot of death.**" in md
    for field in ('Standing', 'Source', 'Editor’s note'):
        if row[field]:
            assert f"**{field}.** {row[field]}" in md, field


def test_the_standings_note_labels_its_four_cases_and_keeps_the_lot_of_death_apart():
    at = make_app(page="lots").run()
    assert_no_exception(at, "lots")
    note = [n for n in at.main if getattr(n, "type", None) == "status" and n.label == "How the standings are recorded"]
    assert len(note) == 1 and note[0].icon == NOTES_EXPANDER_ICON
    md = [m.value for m in note[0].markdown]
    assert md[0::2] == ["**The Standing column.**", "**Four kinds of case.**",
                        "**The Lot of death: a stated rule with a manuscript variant.**"]
    assert md[1].startswith("The **Standing** column records his editorial position in his own words where he states one.")
    cases = md[3].split("\n")
    assert [c.split(":**")[0] for c in cases] == ["- **Sahl himself rules", "- **Dykes names his choice",
                                                  "- **Dykes marks one standard", "- **Dykes only tabulates"]
    assert '"both of the Lots are correct, so work with them both together" (3.11, 4)' in cases[0]
    assert '"I have used M here"' in cases[1] and "We should follow Paul." in cases[1]
    assert '"the usual calculation ... is that of Hermes."' in cases[2]
    assert "Sahl quietly switches to Masha'allah's treatise on Lots" in cases[3]
    assert md[5].startswith("The Lot of death is projected from Saturn: **stated** by Abu Ma'shar (Gr. Intr. VIII.4, 226; VIII.6, 69)")
    assert md[5].endswith("A stated rule with a manuscript variant, not an emendation.")
    src = ui_source()
    lots = src[src.index("def page_lots():"):src.index("def page_victors():")]
    for caps in ("MORE THAN ONCE", "STANDING column", "SAHL HIMSELF RULES", "DYKES NAMES HIS CHOICE",
                 "DYKES MARKS ONE STANDARD", "DYKES ONLY TABULATES", "STATED by"):
        assert caps not in lots, caps
