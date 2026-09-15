"""Every user string written into a picture, escaped where it is written.

A Lot name carrying a double quote closed the attribute it was written
into and broke the whole revolution wheel; the name was changed instead of
the generator. The four renderers now escape at the point of writing --
quotes included for an attribute -- so each picture is rendered here with
a chart name, a place, a Lot name, a ring label, a strip title, a
distributor and a direction's target that each carry " ' & < >, and is
held to three things: it parses, no attribute value carries a raw
delimiter, and every name comes back out of the parser as it went in.
"""
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime

import pytest

SVG = "{http://www.w3.org/2000/svg}"
PETOSKEY = (45.37334, -84.95533)
REFERENCE_UTC = datetime(1982, 11, 19, 16, 44)

# Every character that has ever broken an SVG: the two delimiters, the
# entity opener, and the two angle brackets.
HOSTILE = """Smith & "Jones" <the 'elder'>"""
ATTRIBUTE = re.compile(r'\s[-\w:]+="([^"]*)"')
# A bare & that does not open an entity, or an angle bracket, inside a value.
BAD_IN_VALUE = re.compile(r'&(?!#?\w+;)|[<>]')


@pytest.fixture(scope="module")
def chart(engine):
    return engine["calculate_traditional_chart"](REFERENCE_UTC, *PETOSKEY)


@pytest.fixture(scope="module")
def bundle(engine, chart):
    return engine["pn4_timing_bundle"](chart, PETOSKEY[0], PETOSKEY[1], REFERENCE_UTC.date(),
                                       date(2026, 9, 10), engine["PN4_MONTHLY_TURN_OPTIONS"][0],
                                       {"Hour Lord": "Venus", "Approximate": False})


def check(svg):
    """Parses, and no attribute value carries a raw delimiter. Returns the
    parsed root. (A raw " would close its attribute, so ET.fromstring is
    itself half the test; the scan catches the half that stays well-formed
    but is read back wrong.)"""
    root = ET.fromstring(svg)
    for value in ATTRIBUTE.findall(svg):
        assert not BAD_IN_VALUE.search(value), f"raw markup in an attribute value: {value!r}"
    return root


def texts(root):
    return [t.text or "" for t in root.iter(SVG + "text")]


def attributes(root, name):
    return [el.get(name) for el in root.iter() if el.get(name) is not None]


# --- 1. The natal wheel ----------------------------------------------------

@pytest.mark.parametrize("wide", [False, True], ids=["square", "wide"])
def test_the_natal_wheel_escapes_its_name_place_and_standard(engine, chart, wide):
    svg = engine["generate_hybrid_svg"](chart, HOSTILE, f"{HOSTILE} on Sea", PETOSKEY[0], PETOSKEY[1],
                                        datetime(1982, 11, 19, 11, 44), f"EST {HOSTILE}", wide=wide,
                                        chronocrats={"Day Lord": HOSTILE, "Hour Lord": "Moon"},
                                        bounds=True)
    root = check(svg)
    out = texts(root)
    # Short of the hub's 30-character truncation, so the whole name is there.
    assert len(HOSTILE) <= 30 and HOSTILE in out
    assert f"{HOSTILE} on Sea" in out
    assert f"EST {HOSTILE}" in out
    if wide:
        assert any(f"Lord of the day: {HOSTILE}" in t for t in out)


# --- 2. The revolution wheel ----------------------------------------------

def _rings(engine, chart, b):
    return [{"label": f"Nativity {HOSTILE}", "chart": chart, "when": f"birth {HOSTILE}"},
            {"label": f"Year, age {b['age']} {HOSTILE}", "chart": b["sr"], "when": "year"}]


def _lot_extras(engine, chart, definitions):
    """The Timing page's own path from LOT_DEFINITIONS to the wheel's
    extras (_ring_extras, with Lots wanted)."""
    out = []
    for d in definitions:
        if d["id"] == "fortune":
            continue
        lon = engine["lot_by_id"](d["id"], chart["planetary_data"], chart["ascendant"],
                                  chart["houses"], chart["sect"])
        if lon is not None:
            out.append((d["name"], lon, d["name"].replace("Lot of ", "").replace("the ", "")[:9]))
    return out


@pytest.mark.parametrize("wide", [False, True], ids=["square", "wide"])
def test_the_revolution_wheel_escapes_every_label_it_is_given(engine, chart, bundle, wide):
    rings = _rings(engine, chart, bundle)
    svg = engine["generate_multiwheel_svg"](
        rings, HOSTILE, wide=wide, shade_sign=3, shade_label=f"Sign of year {HOSTILE}",
        outline_sign=5, outline_label=f"Sign of month {HOSTILE}",
        marks=[(f"TP {HOSTILE}", 123.4, 0)], badges={0: {"Sun": f"D {HOSTILE}"}},
        hub_lines=(f"a hub line {HOSTILE}",))
    root = check(svg)
    out = texts(root)
    assert HOSTILE in out
    assert f"Inner: Nativity {HOSTILE}" in out or f"Nativity {HOSTILE}" in out
    assert f"a hub line {HOSTILE}" in out
    assert f"Sign of year {HOSTILE}" in out and f"Sign of month {HOSTILE}" in out
    assert f"TP {HOSTILE}" in out
    # The ring's own label goes into data-chart on every point of that ring.
    assert f"Nativity {HOSTILE}" in attributes(root, "data-chart")
    assert f"TP {HOSTILE}" in attributes(root, "data-point")


def test_a_lot_name_with_a_double_quote_no_longer_breaks_the_wheel(engine, chart, bundle):
    """The failure this branch is for (CI on the Lots of Jupiter and
    Saturn): the name is built into the wheel down the app's own path --
    a LOT_DEFINITIONS row, lot_by_id, the ring's extras."""
    definitions = list(engine["LOT_DEFINITIONS"])
    hostile_row = dict(definitions[1], name=f'Lot of {HOSTILE}')
    extras = _lot_extras(engine, chart, [hostile_row] + definitions)
    assert extras and extras[0][0] == f'Lot of {HOSTILE}'
    svg = engine["generate_multiwheel_svg"](_rings(engine, chart, bundle), "Test Chart 1240",
                                            extras={0: extras})
    root = check(svg)
    assert f'Lot of {HOSTILE}' in attributes(root, "data-point")


# --- 3. The two strips -----------------------------------------------------

def test_the_distribution_strip_escapes_its_title_and_its_segments(engine, bundle):
    segments = [dict(s) for s in bundle["segments"][:3]]
    segments[0]["distributor"] = f'Saturn {HOSTILE}'
    segments[0]["partner"] = f'Mars {HOSTILE}'
    segments[0]["partner_aspect"] = f'square {HOSTILE}'
    svg = engine["generate_distribution_strip_svg"](segments, 40.0, "years", 120.0,
                                                    f"The distributions {HOSTILE}")
    root = check(svg)
    assert f"The distributions {HOSTILE}" in texts(root)
    assert f'Saturn {HOSTILE}' in attributes(root, "data-distributor")
    assert f'Mars {HOSTILE}' in attributes(root, "data-partner")
    assert f'square {HOSTILE}' in attributes(root, "data-aspect")


def test_the_hit_strip_escapes_its_title_and_its_targets(engine, bundle):
    rows = [{"Target": f"the {HOSTILE}'s body", "Arc (years)": 12.5},
            {"Target": f"Saturn & {HOSTILE}", "Arc (years)": 41.0}]
    svg = engine["generate_hit_strip_svg"](rows, 40.0, 120.0, f"The house-master directed {HOSTILE}")
    root = check(svg)
    assert f"The house-master directed {HOSTILE}" in texts(root)
    targets = attributes(root, "data-target")
    assert f"the {HOSTILE}'s body" in targets and f"Saturn & {HOSTILE}" in targets
    # A target the label pattern does not match is printed whole, escaped.
    assert f"Saturn & {HOSTILE}" in texts(root)


# --- 4. Nothing is escaped twice ------------------------------------------

def test_no_value_is_escaped_twice(engine, chart, bundle):
    """An ampersand that came out as &amp;amp; would mean two escapes on
    one path. Every picture, every place a name is written."""
    pictures = [
        engine["generate_hybrid_svg"](chart, HOSTILE, HOSTILE, PETOSKEY[0], PETOSKEY[1],
                                      datetime(1982, 11, 19, 11, 44), HOSTILE, wide=True,
                                      chronocrats={"Day Lord": HOSTILE, "Hour Lord": HOSTILE}),
        engine["generate_multiwheel_svg"](_rings(engine, chart, bundle), HOSTILE, wide=True,
                                          marks=[(HOSTILE, 10.0, 0)], hub_lines=(HOSTILE,),
                                          extras={0: [(HOSTILE, 44.0, HOSTILE[:6])]}),
        engine["generate_distribution_strip_svg"](bundle["segments"], 40.0, "years", 120.0, HOSTILE),
        engine["generate_hit_strip_svg"]([{"Target": HOSTILE, "Arc (years)": 12.5}], 40.0, 120.0, HOSTILE),
    ]
    for svg in pictures:
        check(svg)
        assert "&amp;amp;" not in svg and "&amp;#x27;" not in svg and "&amp;quot;" not in svg
