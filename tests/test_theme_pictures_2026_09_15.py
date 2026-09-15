"""The pictures in the viewer's own theme.

Each picture is an SVG inside an <img>, where no page CSS reaches it, so
every one of them carried its own opaque white ground and black ink and
showed as a white square on a dark page. The four renderers now take a
theme: None is the palette they have always drawn in -- held here to the
byte -- and "dark" is the same geometry on Streamlit's dark ground, with
nothing white or black left in it.
"""
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime

import pytest

from conftest import assert_no_exception, make_app, ui_source

PETOSKEY = (45.37334, -84.95533)
REFERENCE_UTC = datetime(1982, 11, 19, 16, 44)
COLOUR = re.compile(r'(?:fill|stroke)="(#[0-9a-fA-F]{3,6})"')
LIGHT_ONLY = {"#fff", "#ffffff", "#000", "#000000"}


@pytest.fixture(scope="module")
def chart(engine):
    return engine["calculate_traditional_chart"](REFERENCE_UTC, *PETOSKEY)


@pytest.fixture(scope="module")
def bundle(engine, chart):
    return engine["pn4_timing_bundle"](chart, PETOSKEY[0], PETOSKEY[1], REFERENCE_UTC.date(),
                                       date(2026, 9, 10), engine["PN4_MONTHLY_TURN_OPTIONS"][0],
                                       {"Hour Lord": "Venus", "Approximate": False})


def pictures(engine, chart, bundle, **kw):
    """The four, each rendered with whatever theme is passed."""
    rings = [{"label": "Nativity", "chart": chart, "when": "birth"},
             {"label": f"Year, age {bundle['age']}", "chart": bundle["sr"], "when": "year"}]
    return {
        "natal wheel": engine["generate_hybrid_svg"](
            chart, "Test Chart 1240", "Florence, 16 (IT)", PETOSKEY[0], PETOSKEY[1],
            datetime(1240, 5, 23, 14, 30), "LMT", bounds=True,
            chronocrats={"Day Lord": "Sun", "Hour Lord": "Moon"}, **kw),
        "revolution wheel": engine["generate_multiwheel_svg"](
            rings, "Test Chart 1240", shade_sign=3, outline_sign=5,
            profection_from=chart["ascendant"], marks=[("TP", 123.4, 0)],
            badges={0: {"Sun": "D"}},
            distribution={"start": chart["ascendant"], "end": (chart["ascendant"] + 47.0) % 360.0},
            **kw),
        "distribution strip": engine["generate_distribution_strip_svg"](
            bundle["segments"], bundle["elapsed_years"], "years",
            engine["PN4_DISTRIBUTION_SPAN_YEARS"], "The distributions", **kw),
        "hit strip": engine["generate_hit_strip_svg"](
            bundle["hm_direction"], bundle["elapsed_years"],
            engine["PN4_DISTRIBUTION_SPAN_YEARS"], "The house-master directed", **kw),
    }


# --- 1. The default is what it always was ---------------------------------

@pytest.mark.parametrize("theme", [None, "light", "", "Light"])
def test_no_theme_and_a_light_one_draw_exactly_the_old_picture(engine, chart, bundle, theme):
    plain = pictures(engine, chart, bundle)
    themed = pictures(engine, chart, bundle, theme=theme)
    for name, svg in plain.items():
        assert themed[name] == svg, f"{name} changed under theme={theme!r}"
    for svg in plain.values():
        assert '"#ffffff"' in svg, "the light ground is the white one it has always been"


# --- 2. The dark palette --------------------------------------------------

def test_the_dark_pictures_carry_no_white_ground_and_no_black_ink(engine, chart, bundle):
    for name, svg in pictures(engine, chart, bundle, theme="dark").items():
        ET.fromstring(svg)
        colours = set(COLOUR.findall(svg))
        assert not (colours & LIGHT_ONLY), f"{name} still carries {colours & LIGHT_ONLY}"
        root = ET.fromstring(svg)
        ground = next(el for el in root.iter() if el.tag.endswith("rect"))
        assert ground.get("fill") == engine["_PALETTE_DARK"]["bg"], f"{name}: ground {ground.get('fill')}"


def test_the_dark_palette_answers_for_every_colour_the_light_one_does(engine):
    light, dark = engine["_PALETTE_LIGHT"], engine["_PALETTE_DARK"]
    assert set(light) == set(dark)
    for key, value in light.items():
        assert type(value) is type(dark[key]), key
        if key in ("tints", "rings"):
            assert len(value) == len(dark[key])
        if key in ("axis", "strip_tint"):
            assert set(value) == set(dark[key])
    assert dark["bg"] == "#0e1117"                     # Streamlit's own dark ground


def test_the_geometry_is_the_same_picture_in_both_palettes(engine, chart, bundle):
    """Same elements, same coordinates: only the colours move."""
    plain = pictures(engine, chart, bundle)
    dark = pictures(engine, chart, bundle, theme="dark")
    for name, svg in plain.items():
        light_shape = COLOUR.sub('fill=""', svg)
        dark_shape = COLOUR.sub('fill=""', dark[name])
        assert light_shape == dark_shape, f"{name}: the geometry moved with the palette"


# --- 3. The UI half reads the viewer's theme once and passes it on --------

def test_the_ui_reads_the_theme_once_and_hands_it_to_every_picture():
    src = ui_source()
    assert 'getattr(st.context, "theme", None)' in src, "the read must survive a missing attribute"
    assert 'getattr(_context_theme, "type", None)' in src
    assert src.count("APP_THEME = ") == 1, "read once, at the top level"
    # Two wheels on the Chart page, the Timing page's wheel, six strips.
    assert src.count("theme=APP_THEME") == 9


@pytest.mark.parametrize("page", ["chart", "timing"])
def test_the_pages_with_pictures_render_under_a_theme_the_harness_cannot_report(page):
    """AppTest has no browser, so st.context.theme.type is None there; the
    pages must render on the light palette rather than raise."""
    at = make_app(page=page).run()
    assert_no_exception(at, page)
