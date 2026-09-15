"""The Chart page with the wheel at centre stage.

The owner's ruling: the wheel centred and larger, the four controls in one
row beneath it, the three introductory sentences beneath those, and the
header metrics row gone -- its lunation moved into the chart strip, which
every page carries.

These tests read the rendered page's element order, not only its source, so
the arrangement itself is pinned: the wheel block, then the controls block,
then the three captions.
"""
import pytest

from conftest import PAGES, READING_DEPTHS, assert_no_exception, make_app, ui_source

# The three sentences, verbatim, as the page prints them.
INTRO = (
    "A TNAC study companion: cast the chart by hand, then check it here, table by table, "
    "against what the texts say.",
    "The texts are *The Astrology of Sahl b. Bishr*, vol. I, and Abu Ma'shar's *On the "
    "Revolutions of the Years of Nativities* (*Persian Nativities* IV), in Benjamin Dykes's "
    "translations, with his *Great Introduction* as the supplement. Every rule applied on "
    "a page names its sentence.",
    "Enter or load a nativity in the sidebar. Part 1 sets out what the chart contains, "
    "Part 2 what the year holds; the reference tables and the sources close the page "
    "list. The judgment is the astrologer's.",
)
LAYOUTS = ["Square", "Wide"]


def _chart(layout=None, view=None, **state):
    at = make_app(page="chart", view=view)
    if layout is not None:
        at.session_state["_wheel_layout"] = layout
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert_no_exception(at, f"chart, {layout or 'default'} layout")
    return at


def _kids(at):
    return list(at.main.children.values())


def _kinds(block):
    return [type(child).__name__ for child in block.children.values()]


# --- The metrics row is gone ---------------------------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("view", READING_DEPTHS)
def test_the_chart_page_renders_no_metric(layout, view):
    """The four st.metric calls under the wheel -- lunation, sect, day lord,
    hour lord -- were the header row. Three of the four were already in the
    chart strip; the fourth joined it."""
    at = _chart(layout=layout, view=view)
    assert len(at.main.metric) == 0, [m.label for m in at.main.metric]


def test_no_page_carries_the_old_header_metrics():
    src = ui_source()
    for gone in ('.metric("Prenatal lunation"', '.metric("Sect"',
                 '.metric("Lord of the Day"', '.metric("Lord of the Hour"',
                 'hdr1, hdr2, hdr3, hdr4'):
        assert gone not in src, gone


# --- The lunation in the strip -------------------------------------------

@pytest.mark.parametrize("page", PAGES)
def test_the_strip_names_the_lunation_after_the_sect(page):
    at = make_app(page=page).run()
    assert_no_exception(at, page)
    parts = at.main.caption[0].value.split(" · ")
    assert len(parts) == 8, parts
    # The harness's chart: 1240-05-23, Florence. Its prenatal syzygy is a
    # conjunction, and the strip says so in one word.
    assert parts[4] == "Diurnal"
    assert parts[5] == "Conjunctional lunation", parts[5]
    assert parts[6].startswith("Day lord ")


def test_the_strip_takes_the_first_word_of_the_event_label():
    """"Conjunctional (New Moon)" and "Preventional (Full Moon)" are the two
    labels; the strip prints the first word and " lunation", and the degree
    and house stay on the lunation and victors page."""
    src = ui_source()
    assert "syzygy['event_label'].partition(' ')[0]" in src
    assert 'f"{lunation} lunation"' in src


# --- The wheel, centred --------------------------------------------------

def test_the_square_wheel_is_centred_by_a_horizontal_container():
    """A three-column split centres the wheel but also caps it: a column is a
    fraction of the page, and st.image shrinks a picture to the width it is
    given, so the middle of [1, 2, 1] drew the wheel at 454 px at a 1400 px
    window and 394 px at 1280 -- narrower than the 400 px it replaced. A
    horizontal container is a flex row: it stretches the full width, its one
    child keeps its own 560 px, and the row centres it."""
    at = _chart(layout="Square")
    wheel_block = _kids(at)[2]
    assert _kinds(wheel_block) == ["Image"]
    flex = wheel_block.proto.flex_container
    assert flex.direction == flex.Direction.HORIZONTAL, flex.direction
    assert flex.justify == flex.Justify.JUSTIFY_CENTER, flex.justify
    # The row itself is the page's full width; only the picture inside it is
    # 560 px. A container narrower than the page would cap the wheel again.
    assert wheel_block.proto.width_config.use_stretch is True
    src = ui_source()
    assert 'st.container(horizontal=True, horizontal_alignment="center")' in src
    assert "st.image(svg_code, width=560)" in src
    # The split that capped it must not come back.
    assert "st.columns([1, 2, 1])" not in src


def test_the_wide_wheel_still_runs_the_full_width():
    at = _chart(layout="Wide")
    assert type(_kids(at)[2]).__name__ == "Image"
    assert "st.image(svg_wide, width='stretch')" in ui_source()


# --- The controls, in one row --------------------------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_four_controls_stand_in_one_row_under_the_wheel(layout):
    """The four are children of one flex row, in the ruled order. Not
    st.columns: Streamlit stacks columns vertically below about 640 px of
    page width, and the owner's browser showed the four running down the
    left-hand edge. A horizontal container holds the row at any width."""
    at = _chart(layout=layout)
    controls = _kids(at)[3]
    assert _kinds(controls) == ["Radio", "Checkbox", "Checkbox", "DownloadButton"]
    flex = controls.proto.flex_container
    assert flex.direction == flex.Direction.HORIZONTAL, flex.direction
    assert flex.align == flex.Align.ALIGN_END, flex.align        # feet aligned
    assert flex.justify == flex.Justify.JUSTIFY_START, flex.justify   # full width, left
    assert flex.wrap is True          # a row that truly cannot fit may wrap
    assert controls.proto.width_config.use_stretch is True
    assert at.main.radio[0].label == "Wheel layout"
    assert [c.label for c in at.main.checkbox][:2] == ["Bounds ring", "Dark wheel"]
    src = ui_source()
    assert 'st.container(horizontal=True, vertical_alignment="bottom", gap="medium")' in src
    # The split that collapsed into a column must not come back.
    assert "st.columns(\n                    [2, 1, 1, 1.4]" not in src


def test_the_layout_is_read_before_the_control_is_drawn():
    """The wheel is drawn above its own controls now, so the page must know
    which wheel to draw before the radio renders."""
    src = ui_source()
    wheel = src.index("st.image(svg_code, width=560)")
    control = src.index("            _layout_control()\n")
    read = src.index('wheel_layout = st.session_state.get(')
    assert read < wheel < control


# --- The three sentences, under the controls -----------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_three_captions_follow_the_controls_in_order(layout):
    at = _chart(layout=layout)
    kids = _kids(at)
    assert [type(k).__name__ for k in kids[4:7]] == ["Caption"] * 3
    assert [k.value for k in kids[4:7]] == list(INTRO)
    # And the Calculation section is what follows them, as before.
    assert kids[7].value == "Calculation"


def test_both_layouts_print_the_same_three_captions_and_not_one_joined():
    """Wide used to join the three with hard breaks in a single caption."""
    square = [k.value for k in _kids(_chart(layout="Square"))[4:7]]
    wide = [k.value for k in _kids(_chart(layout="Wide"))[4:7]]
    assert square == wide == list(INTRO)
    assert '"  \\n".join(_intro)' not in ui_source()


def test_the_sentences_carry_their_italics_as_markdown_asterisks():
    text = INTRO[1]
    for title in ("*The Astrology of Sahl b. Bishr*", "*Persian Nativities* IV",
                  "*On the Revolutions of the Years of Nativities*",
                  "*Great Introduction*"):
        assert title in text


# --- The circumpolar warning ---------------------------------------------

def test_the_circumpolar_caption_is_absent_on_the_default_chart():
    at = _chart()
    assert not any("not a temporal hour" in c.value for c in at.main.caption)


def test_the_circumpolar_caption_stands_directly_under_the_controls_row():
    """A chart with no sunrise or sunset: the warning is the first thing
    under the controls, before the three sentences."""
    at = _chart(manual_lat_key=78.2, manual_lon_key=15.6)
    kids = _kids(at)
    assert type(kids[4]).__name__ == "Caption"
    assert "not a temporal hour" in kids[4].value, kids[4].value
    assert [k.value for k in kids[5:8]] == list(INTRO)
