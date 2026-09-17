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


# --- Configurations --------------------------------------------------------

def _configurations(date="1240-09-18", **switches):
    at = make_app(date=date, page="configurations", switches=switches or None)
    at.session_state["_reading_depth"] = WITH_SUPPLEMENT
    at.run()
    assert_no_exception(at, f"configurations, {date}")
    return at


def test_the_aspects_notes_open_with_a_column_meaning_key_and_keep_every_sentence_under_a_heading():
    at = _configurations()
    title = "Aspects, aversions and connections"
    assert _heading(at, title).help == "Four separate facts about each pair, kept apart rather than collapsed into one verdict."
    block = _between(at, title)
    assert [k for k, _ in block][:3] == ["caption", "markdown", "dataframe"], block
    assert block[1][1] == ("**Looking** is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none "
                           "applies) -- sign to sign.")
    md = _markdown(at)
    key = [m for m in md if m.startswith("| Column | Meaning |")][0]
    rows = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \|$", key, re.M)[1:]
    assert [c for c, _ in rows] == ["Motion, Exact Orb Dist", "Bodies", "Connection", "Rules differ", "Strength",
                                    "Light, Heavy", "Connecting planet"]
    meaning = dict(rows)
    assert meaning["Light, Heavy"].startswith("The standing classes both authors name as nouns")
    assert meaning["Connecting planet"] == "The separate, directed fact: which one is actually closing the aspect"
    for section in ("**The columns, and what each one measures.**", "**Motion, orb and bodies.**",
                    "**Connection, and where the rules differ.**", "**Strength: two measures.**",
                    "**Light and heavy: the standing classes.**", "**The connecting planet, and retrogradation.**"):
        assert section in md, section
    text = "\n".join(md)
    for sentence in ("**Motion** and **Exact Orb Dist** are the degree-to-degree approach.",
                     "**Light** and **heavy** are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), "
                     "not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.",
                     "Abu Ma'shar, Gr. Intr. VII.5, 24 (\"the connection of one of them with the other ... will be BY RETROGRADATION\")",
                     "which happens for about 4% of configured pairs"):
        assert sentence in text, sentence


def test_the_fitting_infortune_tooltip_is_short_and_the_in_force_line_says_what_the_reading_changes():
    at = _configurations(fitting=True)
    box = [c for c in at.main.checkbox if c.label.startswith("Fitting infortune")][0]
    assert box.help.endswith("-- against his own 1, 16-17, so off by default. Full text on the Sources page.")
    line = [c.value for c in at.main.caption if c.value.startswith("Fitting infortune in force:")]
    assert len(line) == 1
    assert line[0].startswith("Fitting infortune in force: Saturn rules the Ascendant and is not counted as an infortune. When on, that malefic drops out of every 'afflicted by an infortune' test in these tables (Sahl's enclosure")
    assert line[0].endswith("the Moon's 67-68 and 106).")
    off = _configurations()
    assert not [c for c in off.main.caption if c.value.startswith("Fitting infortune")]


def test_reception_shows_its_qualifications_above_the_table_and_its_comparison_in_a_sibling_disclosure():
    at = _configurations()
    title = "Reception — Sahl rule"
    assert _heading(at, title).help == "Who receives whom, on what dignity, which way round, and how strongly."
    block = _between(at, title, "Non-reception")
    kinds = [k for k, _ in block]
    assert kinds[:5] == ["markdown", "markdown", "markdown", "dataframe", "status"], kinds
    assert block[0][1] == "The two authors differ on every one of those, so the Connection rule at the top of this page governs here too."
    assert block[1][1].startswith("**Under Sahl's rule.** Under Sahl's rule a pair refused by non-reception Kind II")
    assert block[2][1] == ("**An empty table.** An empty table is **not** non-reception -- that is a separate set of hostile "
                           "configurations, in the table below.")
    assert block[4][1] == "Sahl and Abu Ma'shar on reception"
    assert [i for l, i in _statuses(at) if l == "Sahl and Abu Ma'shar on reception"] == [NOTES_EXPANDER_ICON]
    md = _markdown(at)
    table = [m for m in md if m.startswith("| Question | Sahl (Ch. 3, 49-55) | Abu Ma'shar (VII.5, 129-133) |")][0]
    rows = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", table, re.M)[1:]
    assert [q for q, _, _ in rows] == ["Direction", "Dignities that count", "Connection required"]
    assert rows[2][1] == "Always" and rows[2][2] == "Reception can hold by looking with no connection at all (133)"
    for section in ("**Sahl's reception (Ch. 3, 49-55).**", "**Abu Ma'shar's reception (VII.5, 129-133).**",
                    "**Dignity quality: the local basis.**", "**Overall class: 136-142.**",
                    "**Sahl's reception at one remove (56).**", "**Sahl's reception after the sign change (57).**"):
        assert section in md, section
    text = "\n".join(md)
    assert "56, **reception at one remove**:\n\n> \"if the Moon was connecting with a planet" in text
    assert "it is JUST LIKE RECEPTION; and if she connected with a planet OTHER than [that], IT UNDERMINES HER.\"" in text
    assert "both are true, and they are different questions." in text


def test_an_absent_reception_finding_draws_no_sibling_disclosure():
    at = _configurations(date="1240-05-23")
    assert not [h for h in at.main.subheader if h.value.startswith("Reception")]
    assert "Sahl and Abu Ma'shar on reception" not in [l for l, _ in _statuses(at)]
    assert any("Reception — Sahl rule" in c.value for c in at.main.caption if c.value.startswith("Not present in this chart"))


def test_non_reception_lists_its_five_kinds_and_the_strength_grids_carry_headed_notes():
    at = _configurations()
    assert _heading(at, "Non-reception").help.endswith("a distinct finding from simply lacking reception.")
    block = _between(at, "Non-reception", "Returning")
    assert [k for k, _ in block][:4] == ["caption", "markdown", "markdown", "dataframe"], block
    assert block[2][1].startswith("**Under Sahl's rule.** Under Sahl's rule Kind II overrides any reception for the same pair")
    md = _markdown(at)
    kinds = [m for m in md if m.startswith("- **Kind I (58):**")][0].split("\n")
    assert [k.split(":**")[0] for k in kinds] == ["- **Kind I (58)", "- **Kind II (59-60)", "- **Kind III (61)", "- **Kind IV (62)", "- **Kind V (62)"]
    assert "A is in its **own** fall" in kinds[2]
    for section in ("**Sahl's A -> B model.**", "**The five kinds.**", "**Testimonies 78 and 83: two measurements.**",
                    "**Sahl's five-degree rule.**", "**Distinct from Planetary Condition.**", "**The ten, in words.**"):
        assert section in md, section
    text = "\n".join(md)
    assert "83 also carries Sahl's **five-degree rule**:\n\n> \"the planet will not be falling from the stake" in text
    assert "the course's reading, Lesson 3 §4-5, adopted here." in text


def test_the_display_only_findings_and_the_supplement_findings_show_their_summaries_and_headed_notes():
    at = _configurations()
    md = _markdown(at)
    text = "\n".join(md)
    triplicity = "The sect light's first triplicity lord by ascensional band -- and the app's generalisation"
    assert _heading(at, triplicity).help == ("Stated for **one** planet, the sect light's first triplicity lord (fn 190), and applied "
                                             "to it in the last column.")
    summary = [m for m in md if m.startswith("2.13, 48: \"if the first lord of the triplicity of the glowing one")][0]
    assert "Stated for **one** planet, the sect light's first triplicity lord (fn 190), and applied to it in the last column" in summary
    assert "**Aphorism 45 as printed:**\n\n> \"every planet which is [distant] from the stake" in text
    assert "**Conventions, this app's:** the stake a planet **follows**" in text
    assert _heading(at, 'Right-sidedness, "the spear-bearing of the planets"').help.endswith("-- \"a strong right-sidedness\".")
    assert _heading(at, 'The honor-guard, "and it is spear-bearing"').help.endswith("and western from the Moon)\".")
    assert sum(1 for m in md if m.startswith("Readings, this app's:")) == 2
    assert _heading(at, "Natural connections").help.startswith("A relation of its own, not an aspect and not a dignity")
    assert _heading(at, "Book V degrees").help == ("Two degree tables from Book V that no condition in VII.6 reads. Shown when a "
                                                    "named point falls in one; never scored.")
    assert _heading(at, "Enclosure").help.endswith("with neither leg intercepted by a third planet's rays.") if \
        [h for h in at.main.subheader if h.value == "Enclosure"] else True
    for section in ("**This app's generalisation, an ordinal preference and no score.**",
                    "**Aphorism 45 as printed, and the editor's correction.**", "**Conventions, this app's.**",
                    "**Readings, this app's.**", "**A second definition, and the witnesses.**",
                    "**Equal ascensions (56), and equal daylight (67-75).**", "**Degrees, and the motion read from both speeds.**",
                    "**Affinity (76-77).**", "**The same pairs in the Reception table.**",
                    "**V.22, 1-2 and 4, the sentences.**", "**Ordinal degrees, and the degrees in both tables.**"):
        assert section in md, section
    assert "**Sahl's own table of the second rule.** Sahl states the second rule with a table of his own" in text
    assert "V.22, 1-2:\n\n> \"when planets indicate the native's good fortune" in text
    # The forward-looking search finds nothing within its horizon on 1240-09-18
    # (its bounded caption stands alone); the default chart has rows and notes.
    found = _configurations(date="1240-05-23")
    found_md = _markdown(found)
    for section in ("**An ordered sequence, against the ephemeris.**", "**Revoking (117).**", "**Resistance (118).**", "**Escape (119).**"):
        assert section in found_md, section
    assert any(m.startswith("**Revoking** (117): \"a planet is connecting with a planet, but BEFORE IT REACHES IT") for m in found_md)


def test_the_condition_block_names_the_dignities_and_places_page_and_the_page_says_the_app_only_in_its_one_title():
    import ast
    src = ui_source()
    page = src[src.index("def page_configurations():"):src.index("def page_lots():")]
    tree = ast.parse(page)
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    text = "\n".join(strings)
    assert text.count("Dignities and places page") == 2
    assert "the Dignities page" not in text
    # The one "the app" left in a page string is the triplicity finding's
    # title, a fixture key (comments may say what they like).
    assert [s for s in strings if re.search(r"\bthe app\b", s)] == [
        "The sect light's first triplicity lord by ascensional band -- and the app's generalisation"]
    for caps in ("LOOKING is", "MOTION and EXACT", "RULES DIFFER marks", "STRENGTH is", "LIGHT and HEAVY", "CONNECTING PLANET is",
                 "SAHL (Ch", "ABU MA'SHAR (VII", "DIGNITY QUALITY", "OVERALL CLASS", "RECEPTION AT ONE REMOVE", "AFTER THE SIGN CHANGE",
                 "is NOT non-reception", "its OWN fall", "about CONNECTIONS", "FIVE-DEGREE RULE", "is DYNAMIC", "that LOOK at",
                 "THE APP'S ANGULAR", "APHORISM 45 AS PRINTED", "CONVENTIONS, this", "Readings, the app's", "EQUAL ASCENSIONS",
                 "EQUAL DAYLIGHT", "DEGREES:", "AFFINITY:", "ORDERED SEQUENCE", "REVOKING (117)", "RESISTANCE (118)", "ESCAPE (119)",
                 "candidate NEAREST", "more DISTANT"):
        assert caps not in page, caps


# --- Reference tables -------------------------------------------------------

def _reference(depth=READING_DEPTHS[0]):
    at = make_app(page="reference")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, "reference")
    return at


def test_the_reference_page_keeps_its_headings_and_moves_the_long_captions_into_headed_notes():
    at = _reference()
    assert [h.value for h in at.main.subheader] == ["Dignities by sign", "Egyptian bounds",
                                                    "Orders of the dignities, and the good places",
                                                    "Planetary years", "Degrees of nobility and rank", "The Ages of Man"]
    captions = [c.value for c in at.main.caption]
    assert any(c.startswith("Sources: Sahl, The Introduction Ch. 1;") and c.endswith("against the 15th.") for c in captions)
    assert "Gr. Intr. VII.8, Figure 146; the fardar periods PN IV IV.1, 2." in captions
    assert not any("Triplicity lords are Dorothean" in c or "Sahl's figure prints bare degrees" in c
                   or c.startswith("Printed order (manuscripts") for c in captions)
    md = _markdown(at)
    for section in ("**The triplicity lords.**", "**The faces.**", "**The seven praised places' printed order.**",
                    "**Two constructions of the middle years.**", "**The witnesses, kept apart.**",
                    "**Four witnesses, and three against.**", "**A variant not adopted.**",
                    "**The ordinal span, and the editor's endpoint reading.**", "**The distinct source lists.**"):
        assert section in md, section
    text = "\n".join(md)
    assert "Triplicity lords are Dorothean (Gr. Intr. V.14, 6-9; Figure 53 (Gr. Intr.));" in text
    assert "Faces are read at 5, 15 and 25 degrees of each sign." in md
    assert "as this app holds them" in _heading(at, "Dignities by sign").help
    assert "this app directs by" in _heading(at, "Egyptian bounds").help


def test_the_seven_place_note_is_the_engine_constant_whole(engine):
    at = _reference()
    assert engine["SEVEN_PLACE_RANKING_NOTE"] in _markdown(at)


def test_the_planetary_years_state_the_convention_above_the_table_and_compare_the_witnesses_in_a_table():
    at = _reference()
    block = _between(at, "Planetary years", "Degrees of nobility and rank")
    assert [k for k, _ in block][:4] == ["markdown", "dataframe", "caption", "status"], block
    assert block[0][1] == ("**The middle years, this app's convention.** This app keeps 39 1/2, the Arabic Great Introduction's, "
                           "the table it reads for the rest of the row.")
    assert block[3][1] == "Why the middle years differ"
    assert [i for l, i in _statuses(at) if l == "Why the middle years differ"] == [NOTES_EXPANDER_ICON]
    md = _markdown(at)
    table = [m for m in md if m.startswith("| Construction | The luminaries' middle years | Witnesses |")][0]
    rows = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", table, re.M)[1:]
    assert [(c, v) for c, v, _ in rows] == [("(least + great/2)/2", "39 1/2 for both"),
                                            ("The ordinary mean", "the Sun 69 1/2 and the Moon 66 1/2")]
    assert rows[0][2].startswith("Valens VII.5; Gr. Intr. VII.8, 3-8 with Figure 146; Abu Bakr, On Nativities I.16")
    assert rows[1][2].startswith("Masha'allah, Book of Aristotle III.1.8; Abu 'Ali al-Khayyat, Judgments of Nativities Ch. 4")
    text = "\n".join(md)
    assert ("which Valens VII.5 states outright:\n\n> \"The sun has half of 120 years and hence receives 60; its minimum period is 19. "
            "The total is 79, half of which is 39 years, 6 months.\"\n\nThe Moon's is the same, half of 108 with 25, 79 halved.") in text
    assert "So the luminaries' 39 1/2 has four witnesses in hand -- Valens VII.5;" in text
    assert "Valens's Venus is a complete period of 84 (half 46), not Figure 146's 82 -- a variant not adopted." in md


@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_the_nobility_degrees_state_the_ordinal_convention_above_the_table_and_the_rest_in_two_sections(depth):
    at = _reference(depth)
    block = _between(at, "Degrees of nobility and rank", "The Ages of Man" if depth == READING_DEPTHS[0]
                     else "The natures of the planets (Gr. Intr. IV.1)")
    assert [k for k, _ in block][:3] == ["markdown", "dataframe", "status"], block
    assert block[0][1] == ("**This app's ordinal-degree convention.** Sahl's figure prints bare degrees, read here as ordinals -- "
                           "how Abu Ma'shar's Figure 64 prints the same rule's degrees.")
    md = _markdown(at)
    span = [m for m in md if m.startswith("Dykes resolves the ordinal to a point:")][0]
    assert span.endswith("the point at which the ordinal span tested here (18° to 19° for the nineteenth) ends.")
    lists = [m for m in md if m.startswith("Al-Qabisi's own table of the same rule")][0]
    if depth == READING_DEPTHS[1]:
        assert lists.endswith("six of the eight disagreeing; the text reconciles none of it.")
    else:
        assert lists.endswith("Course text and supplement lays it beside this one.")


# --- Chart ------------------------------------------------------------------

def test_the_mars_west_tooltip_is_short_and_both_rays_readings_stand_whole_in_notes_under_the_positions():
    at = make_app(page="chart").run()
    assert_no_exception(at, "chart")
    mars = [c for c in at.main.checkbox if c.label == "Mars under the rays to 18° west"][0]
    assert mars.help == ("Dykes's table for Sahl has Mars under the rays at 18 west; Gr. Intr. VII.2, 31 puts him under the rays "
                         "at 15 on the western side. Both give 18 east. Full text on the Sources page, and in the notes under this table.")
    moon = [c for c in at.main.checkbox if c.label == "Moon under the rays to 15°"][0]
    notes = [n for n in at.main if getattr(n, "type", None) == "status" and n.label == "Sources and editorial notes"]
    # the one notes expander on the Chart page stands after the positions table
    md = [m.value for m in notes[0].markdown]
    assert md[0::2] == ["**The Moon under the rays to 15°.**", "**Mars under the rays to 18° west.**"]
    assert moon.help == md[1] + " Full text on the Sources page."     # the Moon's tooltip, less its pointer
    assert md[3] == ("Dykes's table for Sahl (the chapter head of On Nativities 1.22, with fn 175, which reads VII.2, 30's "
                     "westernizing boundary into 18 degrees) has Mars under the rays at 18 west; Sahl's own sentences are silent "
                     "on Mars west. Gr. Intr. VII.2, 31 puts him under the rays at 15 on the western side. Both give 18 east. "
                     "Affects: the Solar phase column here and every test that reads it (Weakness 93, Planetary Condition 27/34/45).")
    kinds = [getattr(n, "type", None) for n in at.main]
    positions = next(i for i, n in enumerate(at.main) if getattr(n, "type", None) == "subheader" and n.value == "Planetary Positions")
    notes_at = next(i for i, n in enumerate(at.main) if getattr(n, "type", None) == "status" and n.label == "Sources and editorial notes")
    calculated = next(i for i, n in enumerate(at.main) if getattr(n, "type", None) == "subheader" and n.value == "Calculated Points")
    assert positions < notes_at < calculated


def test_the_circumpolar_notes_stand_only_on_a_chart_without_sunrise_or_sunset():
    at = make_app(page="chart").run()
    assert "Why the hour lord is approximate here" not in [l for l, _ in _statuses(at)]
    polar = make_app(page="chart")
    polar.session_state["manual_lat_key"] = 78.2
    polar.session_state["manual_lon_key"] = 15.6
    polar.run()
    assert_no_exception(polar, "chart, circumpolar")
    assert [i for l, i in _statuses(polar) if l == "Why the hour lord is approximate here"] == [NOTES_EXPANDER_ICON]
    notice = [c.value for c in polar.main.caption if "not a temporal hour" in c.value]
    assert len(notice) == 1 and "explicitly modern approximation" in notice[0] and notice[0].endswith("The Lord of the Day is still exact.")
    assert len(notice[0]) <= 400


# --- The active-readings line ------------------------------------------------

def _slot(at, page):
    """The readings note's fixed st.empty() slot: main's fourth child on the
    pages that draw the sources scope line before it, third on Chart (no
    scope line), fifth on Findings (its own caption before the scope line)."""
    kids = list(at.main.children.values())
    index = {"chart": 2, "findings": 4}.get(page, 3)
    return kids[index], kids


def test_one_reading_off_default_keeps_the_single_sentence():
    at = make_app(page="dignities", switches={"domain": "Masha'allah"}).run()
    assert_no_exception(at, "dignities")
    slot, _ = _slot(at, "dignities")
    assert slot.type == "caption"
    assert slot.value == ("Readings in force that differ from the defaults: Domain (hayz) = Masha'allah. They are remembered "
                          "between runs; see Sources and readings to reset them.")


@pytest.mark.parametrize("page", ["dignities", "chart", "configurations", "lots", "findings"])
def test_several_readings_off_default_give_a_count_and_a_list_in_one_element(page):
    switches = {"domain": "Masha'allah", "moon_rays": True, "fitting": True}
    at = make_app(page=page, switches=switches).run()
    assert_no_exception(at, page)
    slot, kids = _slot(at, page)
    assert slot.type == "flex_container", [getattr(k, "type", None) for k in kids[:5]]
    inside = list(slot.children.values())
    assert [c.type for c in inside] == ["caption", "caption"]
    assert inside[0].value == ("3 readings differ from defaults. They are remembered between runs; see Sources and readings "
                               "to reset them.")
    lines = inside[1].value.split("\n")
    assert len(lines) == 3 and all(l.startswith("- ") and " = " in l for l in lines)
    assert "- Domain (hayz) = Masha'allah" in lines
    assert "- Moon under the rays to 15 degrees = True" in lines
    assert any(l.startswith("- Fitting infortune") and l.endswith("= True") for l in lines)
    assert not any("Sources shown" in l for l in lines)
    # the note filled its slot and added no element: main has as many
    # direct children as on the default chart, where the slot stays empty
    plain = make_app(page=page).run()
    plain_slot, plain_kids = _slot(plain, page)
    assert plain_slot.type == "empty"
    assert len(kids) == len(plain_kids), "the note took more than its one slot"


def test_the_configurations_tabs_keep_their_place_with_several_readings_off_default():
    plain = make_app(page="configurations").run()
    changed = make_app(page="configurations", switches={"domain": "Masha'allah", "moon_rays": True, "connection": "Abu Ma'shar"}).run()
    for at in (plain, changed):
        assert_no_exception(at, "configurations")
    kinds = lambda at: [getattr(c, "type", None) for c in at.main.children.values()]
    assert kinds(plain).index("tab_container") == kinds(changed).index("tab_container")
    assert kinds(changed)[3] == "flex_container" and kinds(plain)[3] == "empty"


def test_special_degrees_shows_its_sentence_whole_above_the_table_and_its_two_rules_as_blockquotes():
    at = make_app(date="1240-09-18", page="chart").run()      # the default chart has no special degree
    assert_no_exception(at, "chart")
    title = "Special Degrees & Conditions"
    assert _heading(at, title).help == ("Flags planets in Sahl's dark signs (Libra, Capricorn), in the two signs of his burned place, "
                                        "in a welled degree of their sign, or in one of Sahl's two sign-boundary conditions.")
    block = _between(at, title, "Degrees of nobility and rank")
    assert [k for k, _ in block][:3] == ["markdown", "dataframe", "status"], block
    assert block[0][1].startswith("Flags planets in Sahl's dark signs (Libra, Capricorn), in the two signs of his burned place (\"the end of Libra")
    md = _markdown(at)
    assert "**Entering a sign.**" in md and "**Leaving a sign.**" in md
    text = "\n".join(md)
    assert "**Entering**:\n\n> \"every planet which is at the beginning of a sign is weak" in text
    assert "then indeed the strength of the planet IS in that sign\"\n\n(Fifty Aphorisms #15, 31-33) -- so the 29th degree still counts" in text
    for tooltip in ("Calculation", "Quadrant divisions (Alchabitius)"):
        assert "this app" in _heading(at, tooltip).help and "the app" not in _heading(at, tooltip).help
