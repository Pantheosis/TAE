"""Facts that are stated twice -- once in a code structure, once in prose
the user reads -- pinned together so one cannot change without the other.

Each test reads the prose from the UI half of app.py and the structure from
the engine half. When a phrase is reworded the test fails on the phrase, by
design: the count and the sentence are one fact and get edited together.
"""
import re

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
    # The help text ends "HIS OWN eleven" and the notes continue
    # "corruptions of her (63-74)"; the number lives in the help.
    assert prose_number(r"for the Moon only, HIS OWN (\w+)\"") == len(labels)
    # The docstring announces the same count.
    assert re.search(r"The ELEVEN corruptions", function_source("_abu_mashar_moon_corruption"))


def test_sahl_moon_defects_ten():
    labels = cited_paragraphs(function_source("_corruption_of_the_moon_labels"), 103, 112)
    assert labels == set(range(103, 113)), f"Sahl Moon labels cite {sorted(labels)}"
    assert prose_number(r"Sahl's (\w+) \(The Introduction Ch\.3, 103-112\)") == len(labels)


def test_non_reception_five_kinds():
    kinds = set(re.findall(r"'Kind': '([IV]+) \(", function_source("evaluate_non_reception")))
    assert kinds == {"I", "II", "III", "IV", "V"}
    assert prose_number(r"glance=\"(\w+) named ways a connection is refused") == len(kinds)


# --- Counts of code structures -------------------------------------------

def test_wildness_six_other_planets(engine):
    assert prose_number(r"in Aversion to all (\w+) other classical planets") == len(engine["WEIGHT_ORDER"]) - 1


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
    assert len(defs) == 35, f"LOT_DEFINITIONS has {len(defs)} rows; update this number deliberately"
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


def test_coverage_list_has_seventeen_unique_entries(engine):
    cov = engine["NOT_IMPLEMENTED_COVERAGE"]
    passages = [a for a, _b in cov]
    assert len(passages) == len(set(passages)), "duplicate coverage passage"
    assert all(a.strip() and b.strip() for a, b in cov)
    # The commit that grew this list to 17 believed it had written 18.
    assert len(cov) == 17, f"NOT_IMPLEMENTED_COVERAGE has {len(cov)} entries; update this number deliberately"


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
                f"{deg(r['Venus'][0])} east / {deg(r['Venus'][1])} west, and {deg(r['Moon'][0])} respectively")
    ui = ui_source().replace('"\n                    "', "")   # the caption is a wrapped literal
    assert expected in ui, f"caption should read: {expected}"
    assert b["Saturn"] == b["Jupiter"] and b["Venus"] == b["Mercury"] and r["Venus"] == r["Mercury"]
    assert round(engine["CAZIMI_ORB"] * 60) == 16 and "in the heart within 16'" in ui


def test_forward_horizon_is_quoted_correctly(engine):
    import inspect
    horizon = inspect.signature(engine["_simulate_forward"]).parameters["horizon_days"].default
    ui = ui_source()
    assert f"next {horizon} days" in ui and f"up to ~{horizon} days" in ui and f"inside {horizon} days" in ui


def test_via_combusta_span_matches_prose():
    assert "195.0 <= lon <= 225.0" in function_source("evaluate_special_degrees")
    assert "Via Combusta (15 Libra-15 Scorpio" in ui_source()


# --- Switch option literals ----------------------------------------------

def test_switch_options_match_the_values_the_code_compares_against():
    """The sidebar radios offer string literals and the engine compares
    globals against string literals. If either side is reworded the switch
    silently falls through to its default. Pin both copies together."""
    src = app_source()
    def radio_options(prefix):
        m = re.search(r"st\.radio\(\s*\"" + re.escape(prefix) + r"[^\"]*\",\s*(\[[^\]]*\])", src)
        assert m, f"radio starting {prefix!r} not found"
        return eval(m.group(1))
    assert radio_options("VII.6, 27/45") == SWITCHES["eastern"][2]
    assert "EASTERN_RULE == 'VII.2 band'" in src
    assert radio_options("Domain (hayz)") == SWITCHES["domain"][2]
    assert "DOMAIN_RULE == \"Masha'allah\"" in src
    assert radio_options("House-based Lots") == SWITCHES["lot_cusp"][2]
    assert "LOT_HOUSE_CUSP == 'quadrant cusp'" in src
    # The Connection rule radio derives its options from CONNECTION_PROFILES,
    # so it cannot drift; check it still does.
    assert re.search(r"st\.sidebar\.radio\(\s*\"Connection rule\",\s*list\(CONNECTION_PROFILES\.keys\(\)\)", src)


def test_configurations_views_match_the_code():
    src = ui_source()
    m = re.search(r"st\.segmented_control\(\s*\"Show\",\s*(\[[^\]]*\])", src)
    assert m and eval(m.group(1)) == ["Sahl (course text)", "Abu Ma'shar (supplement)", "Both"]
    assert 'show_sahl = view in (None, "Sahl (course text)", "Both")' in src
    assert 'show_abu = view in ("Abu Ma\'shar (supplement)", "Both")' in src
