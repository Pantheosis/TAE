"""The Chart page with the wheel at centre stage.

The owner's ruling: the wheel centred and larger, the four controls in one
row beneath it, the three introductory sentences beneath those, and the
header metrics row gone -- its lunation moved into the chart strip, which
every page carries.

These tests read the rendered page's element order, not only its source, so
the arrangement itself is pinned: the wheel block, then the controls block,
then the four captions.
"""
import pytest

from conftest import (PAGES, READING_DEPTHS, assert_no_exception, make_app,
                      natal_wheel_envelope, ui_source)

# The four sentences, verbatim, as the page prints them.
INTRO = (
    "A TNAC study companion: cast the chart by hand, then check it here, table by table, "
    "against what the texts say.",
    "The texts are *The Astrology of Sahl b. Bishr*, vol. I, and Abu Ma'shar's *On the "
    "Revolutions of the Years of Nativities* (*Persian Nativities* IV), in Benjamin Dykes's "
    "translations, with his *Great Introduction* as the supplement. Every rule applied on "
    "a page names its sentence.",
    "Enter or load a nativity in the sidebar. The Nativity sets out what the chart contains, "
    "Prediction what the year holds; the reference tables and the sources close the page "
    "list. The judgment is the astrologer's.",
    "Click a planet or a sign on the wheel for what the tables say of it; hover a sign for its bounds and triplicity lords.",
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


# The wheel and its controls are one @st.fragment now (item 9, 2026-09-15),
# and a fragment renders as a block of its own: main's third child is that
# block, and the picture and the controls row are ITS two children. Every
# element the fragment draws is inside it, which is what a fragment requires
# -- it may not write to a container outside itself -- and it is why the
# four captions and the circumpolar warning, which stay outside, moved up
# one index in main's own children.
def _fragment(at):
    # After the header, the strip and the readings note's fixed slot
    # (2026-09-17; the slot is an unfilled st.empty() on the default chart).
    return _kids(at)[3]


def _frag_kids(at):
    return list(_fragment(at).children.values())


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
    # Line one is the nativity as entered, line two what the app reads from
    # it, and the lunation is on the second, after the sect.
    entered, read = at.main.caption[0].value.split("  \n")
    assert len(entered.split(" · ")) == 4, entered
    parts = read[2:-2].split(" · ")          # line two is bold; strip the markers
    assert len(parts) == 4, parts
    # The harness's chart: 1240-05-23, Florence. Its prenatal syzygy is a
    # conjunction, and the strip says so in one word.
    assert parts[0] == "Diurnal"
    assert parts[1] == "Conjunctional lunation", parts[1]
    assert parts[2].startswith("Day lord ")
    assert parts[3].startswith("Hour lord ")


def test_the_strip_takes_the_first_word_of_the_event_label():
    """"Conjunctional (New Moon)" and "Preventional (Full Moon)" are the two
    labels; the strip prints the first word and " lunation", and the degree
    and house stay on the lunation and victors page."""
    src = ui_source()
    assert "syzygy['event_label'].partition(' ')[0]" in src
    assert 'f"{lunation} lunation"' in src


def test_the_strip_breaks_between_the_nativity_and_the_reading():
    """Eight parts on one line wrapped wherever the window width fell, which
    put the break in a different place on every page. The two groups are
    joined with a caption hard break instead -- two spaces and a newline, as
    the sidebar's own boxes break a caption."""
    at = _chart()
    entered, read = at.main.caption[0].value.split("  \n")
    assert entered == "Unsaved chart · 1240-05-23 14:30:00 · LMT +00:44:59 · 43.78, 11.25"
    # Line two is bold: the four are measurements the app made, and nothing
    # else above the fold states them. One pair of markers round the joined
    # line, not one pair per part.
    assert read == "**Diurnal · Conjunctional lunation · Day lord Mercury · Hour lord Moon**"
    assert read.count("*") == 4
    assert '"  \\n".join((entered, f"**{read}**"))' in ui_source()


# --- The wheel, centred --------------------------------------------------

def test_the_square_wheel_is_centred_by_a_horizontal_container():
    """A three-column split centres the wheel but also caps it: a column is a
    fraction of the page, and a picture shrinks to the width it is given, so
    the middle of [1, 2, 1] drew the wheel at 454 px at a 1400 px window and
    394 px at 1280 -- narrower than the 400 px it replaced. A horizontal
    container is a flex row: it stretches the full width, its one child keeps
    its own 560 px, and the row centres it. The picture is the natal_wheel
    component now (item 11), and 560 px is carried in its envelope."""
    at = _chart(layout="Square")
    wheel_block = _frag_kids(at)[0]
    assert _kinds(wheel_block) == ["UnknownElement"]
    assert natal_wheel_envelope(wheel_block)["width"] == 560
    flex = wheel_block.proto.flex_container
    assert flex.direction == flex.Direction.HORIZONTAL, flex.direction
    assert flex.justify == flex.Justify.JUSTIFY_CENTER, flex.justify
    # The row itself is the page's full width; only the picture inside it is
    # 560 px. A container narrower than the page would cap the wheel again.
    assert wheel_block.proto.width_config.use_stretch is True
    src = ui_source()
    assert 'st.container(horizontal=True, horizontal_alignment="center")' in src
    assert '"width": "stretch" if _picked_wide else 560,' in src
    # The split that capped it must not come back.
    assert "st.columns([1, 2, 1])" not in src


def test_the_wide_wheel_still_runs_the_full_width():
    at = _chart(layout="Wide")
    assert type(_frag_kids(at)[0]).__name__ == "UnknownElement"
    assert natal_wheel_envelope(_fragment(at))["width"] == "stretch"


# --- The controls, in one row --------------------------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_four_controls_stand_in_one_row_under_the_wheel(layout):
    """The four are children of one flex row, in the ruled order. Not
    st.columns: Streamlit stacks columns vertically below about 640 px of
    page width, and the owner's browser showed the four running down the
    left-hand edge. A horizontal container holds the row at any width."""
    at = _chart(layout=layout)
    controls = _frag_kids(at)[1]
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
    assert 'label_visibility="collapsed")' in src
    assert 'st.container(horizontal=True, vertical_alignment="bottom", gap="medium")' in src
    # The split that collapsed into a column must not come back.
    assert "st.columns(\n                    [2, 1, 1, 1.4]" not in src


def test_the_chart_pages_layout_radio_hides_its_label_and_carries_no_tooltip():
    """A radio puts its label above its options and a checkbox puts its
    beside the box, so a labelled radio stood a tier above the three controls
    next to it and the row read as two. The label string stays -- Streamlit
    requires a non-empty one -- as the widget's accessible name, which is
    what a lookup by label finds it by."""
    at = _chart(layout="Square")
    radio = at.main.radio[0]
    assert radio.label == "Wheel layout"          # still findable by its name
    assert radio.proto.label_visibility.value == radio.proto.label_visibility.COLLAPSED
    assert not radio.help, repr(radio.help)
    assert radio.options == ["Square", "Wide"]


def test_the_timing_pages_copy_of_the_radio_keeps_its_label():
    """The ruling is the Chart page's row only: on Timing the same radio sits
    with a selectbox beside it, where a label is what tells the two apart."""
    at = make_app(page="timing").run()
    assert_no_exception(at, "timing")
    wheel = [r for r in at.main.radio if r.label == "Wheel layout"]
    assert len(wheel) == 1
    assert wheel[0].proto.label_visibility.value != wheel[0].proto.label_visibility.COLLAPSED


def test_reading_radio_passes_label_visibility_through_and_defaults_to_visible():
    src = ui_source()
    assert 'def _reading_radio(label, options, widget_key, store_key, help=None,\n' in src
    assert 'label_visibility="visible", format_func=None)' in src
    assert "label_visibility=label_visibility" in src


def test_the_layout_is_read_before_the_control_is_drawn():
    """The wheel is drawn above its own controls now, so the page must know
    which wheel to draw before the radio renders."""
    src = ui_source()
    wheel = src.index('"svg": svg_wide if _picked_wide else svg_code,')
    # Eight spaces fewer since the page functions left `if tz_name:`
    # (2026-09-16, F05); the call and its order are what this pins.
    control = src.index("        _layout_control()\n")
    read = src.index('wheel_layout = st.session_state.get(')
    assert read < wheel < control


# --- The three sentences, under the controls -----------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_four_captions_follow_the_controls_in_order(layout):
    at = _chart(layout=layout)
    kids = _kids(at)
    # kids[2] is the readings note's fixed slot (empty on the default chart)
    # since 2026-09-17, so the captions stand one child later.
    assert [type(k).__name__ for k in kids[4:8]] == ["Caption"] * 4
    assert [k.value for k in kids[4:8]] == list(INTRO)
    # And the Calculation section is what follows them, as before.
    assert kids[8].value == "Calculation"


def test_both_layouts_print_the_same_four_captions_and_not_one_joined():
    """Wide used to join the three with hard breaks in a single caption."""
    square = [k.value for k in _kids(_chart(layout="Square"))[4:8]]
    wide = [k.value for k in _kids(_chart(layout="Wide"))[4:8]]
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
    assert [k.value for k in kids[5:9]] == list(INTRO)
