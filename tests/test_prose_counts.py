"""Facts that are stated twice -- once in a code structure, once in prose
the user reads -- pinned together so one cannot change without the other.

Each test reads the prose from the UI half of app.py and the structure from
the engine half. When a phrase is reworded the test fails on the phrase, by
design: the count and the sentence are one fact and get edited together.
"""
import os
import re
from pathlib import Path

import pytest

from conftest import (SWITCHES, app_source, cited_paragraphs, engine_source,
                      function_source, prose_number, ui_source)


# --- Sahl's numbered testimonies -----------------------------------------

def test_strength_testimonies_eleven():
    labels = cited_paragraphs(function_source("evaluate_strength_of_planets"), 78, 88)
    assert labels == set(range(78, 89)), f"Strength labels cite {sorted(labels)}"
    assert prose_number(r"glance=\"The (\w+) testimonies of a planet's strength") == len(labels)


def test_weakness_testimonies_ten():
    labels = cited_paragraphs(function_source("evaluate_weakness_of_planets"), 91, 100)
    assert labels == set(range(91, 101)), f"Weakness labels cite {sorted(labels)}"
    assert prose_number(r"glance=\"The (\w+) testimonies of a planet's weakness") == len(labels)


def test_abu_mashar_moon_corruptions_eleven():
    labels = cited_paragraphs(function_source("_abu_mashar_moon_corruption"), 64, 74)
    assert labels == set(range(64, 75)), f"VII.6 Moon labels cite {sorted(labels)}"
    assert prose_number(r"for the Moon only, HIS OWN (\w+) corruptions") == len(labels)
    # The docstring announces the same count.
    assert re.search(r"The ELEVEN corruptions", function_source("_abu_mashar_moon_corruption"))


def test_sahl_moon_defects_ten():
    # Each clause is recorded as hit(<paragraph>, text); the paragraph is
    # the testimony ID, not a suffix parsed back out of the label.
    src = function_source("evaluate_corruption_of_the_moon")
    labels = {int(n) for n in re.findall(r"\bhit\((\d{3}),", src)} | cited_paragraphs(src, 103, 112)
    assert labels == set(range(103, 113)), f"Sahl Moon labels cite {sorted(labels)}"
    assert prose_number(r"Sahl's (\w+) \(The Introduction Ch\.3, 103-112\)") == len(labels)


def test_non_reception_five_kinds():
    kinds = set(re.findall(r"'Kind': '([IV]+) \(", function_source("evaluate_non_reception")))
    assert kinds == {"I", "II", "III", "IV", "V"}
    assert prose_number(r"glance=\"(\w+) named ways a connection is refused") == len(kinds)


# --- Counts of code structures -------------------------------------------

def test_wildness_six_other_planets(engine):
    assert prose_number(r"in (?:whole-sign )?Aversion to all (\w+) other classical planets") == len(engine["WEIGHT_ORDER"]) - 1


def test_classical_lots_are_four(engine):
    rows = engine["calculate_classical_lots"](100.0, 50.0, 200.0, "Diurnal")
    assert len(rows) == 4
    assert re.search(r"The four Lots this app has always shown", function_source("calculate_classical_lots"))
    # Every Standing string comes from LOT_DEFINITIONS except Basis, which
    # the definitions table does not carry.
    standing = {d["id"]: d["confidence"] for d in engine["LOT_DEFINITIONS"]}
    by_name = {r["Lot Name"]: r["Standing"] for r in rows}
    assert by_name["Lot of Fortune"] == standing["fortune"]
    assert by_name["Lot of Spirit"] == standing["spirit"]
    assert by_name["Lot of Exaltation"] == standing["exaltation"]


def test_lot_definitions_are_well_formed(engine):
    defs = engine["LOT_DEFINITIONS"]
    ids = [d["id"] for d in defs]
    assert len(ids) == len(set(ids)), "duplicate Lot ids"
    assert len(defs) == 36, f"LOT_DEFINITIONS has {len(defs)} rows; update this number deliberately"   # 36 since 2026-09-11: the Lot of death's whole-sign variant row (sheet row 4)
    planets = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
    seen = set()
    for d in defs:
        for point in (d["start"], d["end"], d["project"]):
            ok = (point in planets or point == "Ascendant"
                  or point in ("sect_light", "exaltation_degree")
                  or re.fullmatch(r"(cusp|lord)\d{1,2}", point)
                  or point in seen)                   # a Lot feeding a Lot: must precede it
            assert ok, f"{d['id']}: point {point!r} is not resolvable at its position in the table"
        seen.add(d["id"])
        for field in ("topic", "name", "source", "confidence", "note"):
            assert d[field].strip(), f"{d['id']}: empty {field}"


# Places the corpus actually contains. An entry may say material is absent
# only if it points outside these; the 2026-09-06 audit found two entries
# saying VII.5's natural-connection sign pairs were "not in this corpus"
# when VII.5, 56 and 67-68 list them. A pinned entry count let that ship.
CORPUS_BOOKS = ("VII",)                      # Abu Ma'shar, Great Introduction VII
ABSENCE_CLAIM = re.compile(r"not in (?:this|the) corpus|no table for them in this corpus", re.I)
BOOK_CITE = re.compile(r"\b(I{1,3}|IV|VI{0,3}|IX|X)\.\d+")

# A second, distinct kind of absence claim: that the TEXT of the cited
# passage itself is missing (a page not photographed, a figure not in the
# photo set) rather than a table the text refers to. The VII.7 entry said
# "begins on a page not photographed" for four days after VII.7 landed in
# the corpus, and the test above never looked at it: its gate matched
# neither phrase, and the book token lives in the passage, not the
# description. Every book in CORPUS_BOOKS is photographed end to end
# (CORPUS_MANIFEST.md), so such a claim about one of them is false on its
# face -- no corpus file is needed to decide it, which is why this can run
# in CI. test_page_absence_claims_agree_with_the_corpus_when_present goes
# further when the corpus is on disk.
PAGE_ABSENCE = re.compile(
    r"not photographed|photo set|page not|begins on (?:a|the following) page"
    r"|not (?:legible|included)|illegible|missing page|not yet (?:photographed|scanned)", re.I)
CORPUS_DIR = Path(os.environ.get(
    "CORPUS_DIR", Path.home() / "Desktop" / "Fifty Aphorism OCR Project" / "consolidated_texts"))
CORPUS_FILES = {"VII": "abu_mashar_book_vii.md"}


def test_coverage_list_entries_are_unique_and_filled(engine):
    cov = engine["NOT_IMPLEMENTED_COVERAGE"]
    passages = [a for a, _b in cov]
    assert len(passages) == len(set(passages)), "duplicate coverage passage"
    assert all(a.strip() and b.strip() for a, b in cov)


def test_coverage_entries_do_not_call_corpus_material_absent(engine):
    """Every 'not in this corpus' claim must name where the missing material
    lives, and that place must be outside the books the corpus holds."""
    for passage, desc in engine["NOT_IMPLEMENTED_COVERAGE"]:
        if not ABSENCE_CLAIM.search(desc):
            continue
        cited = {m.group(1) for m in BOOK_CITE.finditer(desc)}
        inside = cited & set(CORPUS_BOOKS)
        assert not inside, (
            f"{passage}: says Book {sorted(inside)} material is not in the corpus, but it is")


def test_coverage_entries_do_not_call_a_photographed_passage_missing(engine):
    """A coverage entry may not say the cited passage's own text is absent
    (unphotographed, not in the photo set) when the passage is in a book
    the corpus holds complete. The book is read from the passage, where
    the citation actually lives."""
    for passage, desc in engine["NOT_IMPLEMENTED_COVERAGE"]:
        if not PAGE_ABSENCE.search(desc):
            continue
        cited = {m.group(1) for m in BOOK_CITE.finditer(passage + " " + desc)}
        inside = cited & set(CORPUS_BOOKS)
        assert not inside, (
            f"{passage}: says its text is unphotographed/missing, but Book {sorted(inside)} "
            f"is complete in the corpus -- {desc!r}")


@pytest.mark.skipif(not CORPUS_DIR.is_dir(), reason="corpus not on this machine (CI): the "
                    "book-list test above still guards the claim")
def test_page_absence_claims_agree_with_the_corpus_when_present(engine):
    """With the corpus on disk, check the chapter heading itself: every
    passage cited as 'Gr. Intr. VII.N' must have a '### Chapter VII.N'
    heading in the OCR, whatever the description says. Catches the next
    stale marker even if it uses a phrase PAGE_ABSENCE does not know."""
    text = (CORPUS_DIR / CORPUS_FILES["VII"]).read_text(encoding="utf-8")
    headings = set(re.findall(r"^### Chapter (VII\.\d+)", text, re.M))
    assert headings, "no VII chapter headings found -- wrong file?"
    for passage, desc in engine["NOT_IMPLEMENTED_COVERAGE"]:
        m = re.match(r"Gr\. Intr\. (VII\.\d+)", passage)
        if not m:
            continue
        assert m.group(1) in headings, f"{passage}: no '### Chapter {m.group(1)}' heading in the corpus"
        assert not PAGE_ABSENCE.search(desc), (
            f"{passage}: chapter {m.group(1)} is in the corpus, yet the entry says {desc!r}")


def test_natural_connections_are_built_and_only_the_omitted_pairs_remain(engine):
    """VII.5, 53-77 is implemented (evaluate_abu_natural_connections); the
    coverage list may name only what the text itself leaves out."""
    passages = [a for a, _b in engine["NOT_IMPLEMENTED_COVERAGE"]]
    assert not any(a in ("Gr. Intr. VII.5, 53-77", "Gr. Intr. VII.5, 134") for a in passages)
    omitted = [b for a, b in engine["NOT_IMPLEMENTED_COVERAGE"] if a.startswith("Gr. Intr. VII.5, 67-77")]
    assert len(omitted) == 1 and "Aquarius-Scorpio" in omitted[0] and "not added" in omitted[0]


def test_victor_grid_shape(engine):
    """ibn Ezra's worksheet: seven planet columns, five point rows, then
    Day, Hour, Places, Totals -- as the notes describe it."""
    from datetime import datetime
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    res = engine["evaluate_victors"](chart["planetary_data"], chart["ascendant"], chart["lot_of_fortune"],
                                     30.0, chart["sect"], {"Day Lord": "Sun", "Hour Lord": "Moon"})
    assert len(res) == 4, "two weightings x two wheels"
    for scheme in res.values():
        grid = scheme["grid"]
        assert [r["Row"] for r in grid] == ["Sun", "Moon", "Ascendant", "Lot of Fortune", "Prenatal Syzygy",
                                            "Lord of the Day (7)", "Lord of the Hour (6)", "Places", "Totals"]
        assert set(grid[0]) == {"Row", *engine["WEIGHT_ORDER"]}
    assert "The seven planets are the columns" in ui_source()
    assert "The first five rows" in ui_source()


# --- Constants restated in prose ----------------------------------------

def test_connection_help_lists_the_planetary_lights(engine):
    lights = sorted(set(engine["PLANETARY_ORBS"].values()), reverse=True)
    phrase = "/".join(str(int(x)) for x in lights) + " by planet"
    assert phrase in ui_source(), f"Connection-rule help should say '({phrase})'"


def test_dignity_caption_restates_the_solar_orbs(engine):
    """The Dignity Evaluation caption quotes SOLAR_BURNED_ORB, SOLAR_RAYS_ORB
    and CAZIMI_ORB in prose. Build the sentence from the constants."""
    b, r = engine["SOLAR_BURNED_ORB"], engine["SOLAR_RAYS_ORB"]
    deg = lambda x: f"{int(x)}°"
    expected = (f"burned to {deg(b['Saturn'][0])} for Saturn and Jupiter, {deg(b['Mars'][0])} for Mars, "
                f"{deg(b['Venus'][0])} for Venus and Mercury, {deg(b['Moon'][0])} for the Moon; "
                f"under the rays to {deg(r['Saturn'][0])}, {deg(r['Mars'][0])} east / {deg(r['Mars'][1])} west, "
                f"{deg(r['Venus'][0])} east / {deg(r['Venus'][1])} west, and ")
    ui = re.sub(r'"\n\s+f?"', "", ui_source())   # the caption is a wrapped literal
    assert expected in ui, f"caption should read: {expected}"
    # The Moon's figure and the domain rule are sidebar switches, so the
    # caption interpolates them rather than quoting a number.
    assert "{MOON_RAYS_ORB:.0f}° for the Moon" in ui
    assert "currently {DOMAIN_RULE}" in ui and "DOMAIN_RULE == DOMAIN_RULE_OPTIONS[0]" in ui
    assert b["Saturn"] == b["Jupiter"] and b["Venus"] == b["Mercury"] and r["Venus"] == r["Mercury"]
    assert round(engine["CAZIMI_ORB"] * 60) == 16 and "in the heart within 16'" in ui


def test_forward_horizon_is_quoted_correctly(engine):
    import inspect
    horizon = inspect.signature(engine["_simulate_forward"]).parameters["horizon_days"].default
    ui = ui_source()
    assert f"next {horizon} days" in ui and f"up to ~{horizon} days" in ui and f"inside {horizon} days" in ui


def test_no_via_combusta_span_is_attributed_anywhere():
    # D-5 (2026-09-08): Sahl gives the burned place no degrees, and the
    # 15 Libra-15 Scorpio span is in no source in hand. Neither half of
    # the file may reintroduce it.
    assert "195.0 <= lon" not in function_source("evaluate_special_degrees")
    assert "Via Combusta" not in engine_source() and "Via Combusta" not in ui_source()


# --- Switch option literals ----------------------------------------------

def test_switch_options_match_the_values_the_code_compares_against(engine):
    """Each switch's alternatives live in one *_OPTIONS tuple that both the
    page radio and the engine's comparison read. A radio that typed its
    own list, or a comparison against a bare literal, would let a reworded
    option silently fall through to the default. The top-level read of the
    store key must default to the same first option."""
    src = app_source()
    for prefix, const, name in (("VII.6, 27/45", "EASTERN_RULE", "eastern"),
                                ("Domain (hayz)", "DOMAIN_RULE", "domain"),
                                ("House-based Lots", "LOT_HOUSE_CUSP", "lot_cusp")):
        assert list(engine[const + "_OPTIONS"]) == SWITCHES[name][1]
        assert engine[const] == engine[const + "_OPTIONS"][0], f"{const} default is not the first option"
        assert re.search(r"_reading_radio\(\s*\"" + re.escape(prefix) + r"[^\"]*\",\s*" + const + r"_OPTIONS,", src), \
            f"the {prefix!r} radio should take {const}_OPTIONS"
        assert re.search(const + r" = _reading\(\"\w+\", \"" + SWITCHES[name][0] + r"\", " + const + r"_OPTIONS\[0\]\)", src), \
            f"the top-level read of {const} should default to {const}_OPTIONS[0]"
        assert f"{const} == {const}_OPTIONS[1]" in src, f"the engine should compare {const} against its OPTIONS tuple"
        # No bare literal comparison anywhere.
        assert not re.search(const + r" == ['\"]", src), f"{const} is compared against a bare literal somewhere"
    # The Connection rule radio derives its options from CONNECTION_PROFILES,
    # so it cannot drift; check it still does.
    assert re.search(r"_reading_radio\(\"Connection test used in the shared tables\", CONNECTION_PROFILES\.keys\(\)", src)


def test_configurations_chapters_match_the_code():
    """The three-way view went on 2026-09-10; the page is four chapters in
    the course's order plus, under the Course text depth, Abu Ma'shar's
    own; under the fuller depth his tables join the topics."""
    src = ui_source()
    assert "segmented_control" not in src.split("def page_configurations")[1].split("def page_lots")[0]
    assert ('_labels = ["Aspects & Connections", "Handing Over & Reception", "Prevented Connections",\n'
            '                       "Strength & Weakness"] + ([] if supplement else ["Abu Ma\'shar (Supplement)"])') in src
    assert "abu_block([abu_condition, abu_natural, abu_wildness, abu_reflection, abu_favor, abu_rays," in src


# --- Pins added with the 2026-09-06 consistency fixes -------------------

def test_sahl_moon_table_prose_matches_its_list():
    assert prose_number(r"glance=\"Sahl's own (\w+) defects of the Moon") == 10
    assert "'Corruption of the Moon', 'Sahl, The Introduction Ch.3, 103-112'" in ui_source()
    # Every mention of the two lists points at a table that exists.
    assert "stay in Sahl's own tables" not in app_source()
    assert "102-113" not in app_source()


def test_timing_table_has_exactly_the_rows_its_help_describes(engine):
    from datetime import date
    rows = engine["calculate_time_lords"](100.0, date(1240, 5, 23), date(2026, 9, 6))
    assert [r["Technique"] for r in rows] == ["Annual Profection",
                                             "Symbolic direction (1\u00b0/yr, NOT a distribution)"]
    assert "Two rows: the lord of the year" in ui_source()
    assert "month, day, and hour" not in ui_source()


def test_governed_tables_list_is_stated_identically_and_excludes_wildness():
    """The Connection rule governs the dual-author tables; wildness never
    reads it. The list is stated in the sidebar help and in doctrine()'s
    docstring, and the two must agree."""
    governed = "the aspect grid, reception, blocking, cutting"
    assert governed + ". Each author's own tables" in re.sub(r'"\n\s+"', "", ui_source())
    assert governed + " --" in function_source("doctrine")
    assert "cutting, wildness" not in app_source()


def test_one_station_tolerance(engine):
    src = engine_source()
    assert src.count("STATION_SPEED_TOLERANCE") >= 3          # definition + two readers
    assert not re.search(r"abs\(speed\) <= 0\.\d", src), "a bare station threshold literal is back"
    assert engine["STATION_SPEED_TOLERANCE"] == 0.003


def test_lots_tables_agree_with_each_other_and_with_the_chart(engine):
    """Fortune, Spirit and Exaltation appear in the Classical Lots table,
    the Topical Lots table and (Fortune) the chart itself. All three now
    read LOT_DEFINITIONS; check they say the same thing on both sects."""
    from datetime import datetime
    for dt in (datetime(1240, 5, 23, 13, 45), datetime(1240, 5, 23, 1, 45)):
        chart = engine["calculate_traditional_chart"](dt, 43.7792, 11.2463)
        pd_, asc, sect = chart["planetary_data"], chart["ascendant"], chart["sect"]
        classical = {r["Lot Name"]: r["Position"] for r in
                     engine["calculate_classical_lots"](asc, pd_["Sun"]["longitude"], pd_["Moon"]["longitude"], sect)}
        topical = {r["Lot"]: r["Position"] for r in engine["calculate_topical_lots"](pd_, asc, chart["houses"], sect)}
        for name in ("Lot of Fortune", "Lot of Spirit", "Lot of Exaltation"):
            assert classical[name] == topical[name], (sect, name)
        assert classical["Lot of Fortune"] == engine["get_degree_string"](chart["lot_of_fortune"])


def test_no_engine_function_is_dead():
    """Every top-level function in the engine half is referenced somewhere
    else in the file. Sahl's Moon-defect evaluator sat uncalled for weeks
    while three notes told the user where to find its table."""
    import ast
    src = app_source()
    tree = ast.parse(engine_source())
    dead = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            uses = len(re.findall(r"\b" + re.escape(node.name) + r"\b", src)) - 1   # minus the def
            if uses == 0:
                dead.append(node.name)
    assert not dead, f"engine functions defined but never referenced: {dead}"


def test_prevented_connections_cite_what_they_contain():
    ui = ui_source()
    assert "Gr. Intr. VII.5, 90-94 and 120-125\", prevented" in ui
    # The per-row Source column is gone (the caption cites both passages);
    # the two readings it distinguished are kept as comments on the rows.
    assert "'Source'" not in ui[ui.index("prevented = []"):ui.index("_finding(_gap, 'Prevented connections'")]
    assert "Sahl Ch.3, 35-48; VII.5, 90-94 -- cited in the caption" in ui
    assert "Types I and II are Abu Ma'shar's own (VII.5, 121-124)" in ui
    assert "Type II is Gr. Intr. VII.5, 84-85" in ui


def test_a_locator_names_its_volume_never_the_author_alone():
    """The citation convention of 2026-09-10. Both of Abu Ma'shar's volumes
    in the corpus have a Book VII, so 'Abu Ma'shar VII.6' located nothing;
    every locator now carries 'Gr. Intr.' or 'PN IV' (Sahl's works were
    already named). The Timing page's own rule -- bare Book.chapter for
    PN IV, stated in its header -- is the one exception and is page-wide."""
    leftover = re.compile(r"Abu Ma'shar(?:'s)?,? (?:Great Introduction )?(?:I|II|III|IV|V|VI|VII|VIII|IX)\.\d")
    # (PREFERENCE_RENAMES pairs each old form with its new one on one line; those lines are the migration, not a citation)
    hits = [(n, l.strip()[:100]) for n, l in enumerate(app_source().split("\n"), 1)
            if leftover.search(l) and not ("PN IV" in l or "Gr. Intr." in l)]
    assert not hits, hits
    assert "Gr. Intr. VII.6" in app_source() and "PN IV IX.1, 26-34" in app_source()


# --- The page carries no build process (owner, 2026-09-11) ---------------

# Markers of the build process that belong in comments, docstrings and the
# build log, never in a string the user reads: dates, decision and order
# ids, process filenames, the reviewers, the owner. Citations (Sahl I p.
# 265; PN IV IX.5, 4 fn 106), "a reading", "not built" and quoted
# sentences are doctrine and stay.
BUILD_PROCESS_MARKERS = re.compile(
    r"2026-0\d-\d\d|\bD-\d+\b|DEC-D-|FINAL-A\d|GAP-\d|PN4R-|REL-\d|DIS-\d+|CONV-|Astra F\d|"
    r"\.md\b|\bOCR|the owner|owner,|owner's|\bOwner\b|review D\d|the checker|work order|(?-i:\border [A-Z]{2,})|"
    r"OWNER_RULING|decision sheet|sheet row|the corpus|the ruling|by ruling|the canon\b|canon's|since 2026|"
    r"the builder|builder's|lane \d|\bdecision D|blind reading|the harness|PN4_REPAIRS|READTHROUGH|"
    r"this corpus|corpus disagreement|rephotograph|for weeks", re.IGNORECASE)


def test_page_strings_carry_no_build_process():
    """Every string literal in app.py that is not a docstring is a string
    the page may print; none may name the build process. A new page string
    that says "decision D-9" or "owner, 2026-09-11" fails here by design:
    say the reading, cite the sentence, and put the history in a comment."""
    import ast
    src = app_source()
    tree = ast.parse(src)
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                doc_lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.lineno not in doc_lines:
            for m in BUILD_PROCESS_MARKERS.finditer(node.value):
                if m.group(0).lower() == "the owner" and "the owner of the revolution" in node.value:
                    continue                                                  # II.3, 5's own words
                offenders.append((node.lineno, m.group(0), node.value[max(0, m.start() - 40):m.end() + 40]))
    assert not offenders, "\n".join(f"app.py:{ln}: {mark!r} in ...{ctx}..." for ln, mark, ctx in offenders)
