"""The picture controls as fragments.

Item 9 of `UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md`. Every control
on a wheel used to rerun the whole script: the Chart page's layout radio,
Bounds ring, Dark wheel and download, and the Timing page's view selectbox,
layout radio and the five controls in its Options popover -- the last of
which redrew all 67 tables on that page for a toggle that moves a picture.
Each wheel and its controls are one `@st.fragment` now, and a fragment
reruns only its own body on its own widgets' changes.

What `AppTest` can and cannot show. It runs a fragment as part of a full
run, so the saving itself -- the partial rerun -- is not visible here and
was measured in the browser instead (see
`docs/UI_CHANGES_2026-09-15_fragments.md`). What is visible here, and is
what would break silently, is the shape the fragment has to keep:

1. the two functions exist and carry the decorator;
2. the wheel still renders, on both pages and both layouts;
3. the store keys the fragment's widgets write are left in the state a full
   rerun would have produced -- because the top level reads them on the NEXT
   full run (`CHART_BOUNDS`, `WHEEL_DARK`), and a fragment that wrote only
   its widget key would strand them;
4. every element the fragment draws is inside its body. A fragment may not
   write to a container outside itself, and Streamlit renders one as a block
   of its own, so this reads as: the fragment's elements are that block's
   children, contiguous by construction, and nothing the fragment is
   responsible for stands outside it.
"""
import ast
import base64

import pytest

from conftest import (READING_DEPTHS, assert_no_exception, component_mounts, make_app,
                      natal_wheel_envelope, ui_source)

LAYOUTS = ["Square", "Wide"]

# The Chart page's fragment is main's third child (header, strip, readings
# note, then the wheel block); the Timing page's is the third child of the
# first tab, after that tab's own subheader and table. The Timing page's
# tabs moved from main's sixth child to its seventh when the Sources shown
# scope line joined the header block (2026-09-16); the path into the tab is
# unchanged.
CHART_FRAGMENT = (2,)
TIMING_FRAGMENT = (6, 0, 2)


def _at(page, layout=None, view=None, **state):
    at = make_app(page=page, view=view)
    if layout is not None:
        at.session_state["_wheel_layout"] = layout
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert_no_exception(at, f"{page}, {layout or 'default'} layout")
    return at


def _node(at, path):
    node = at.main
    for i in path:
        node = list(node.children.values())[i]
    return node


def _kinds(block):
    return [type(child).__name__ for child in block.children.values()]


def _state(at):
    """The session state as a plain mapping, which is what the app's own
    reading rule reads."""
    return dict(at.session_state.filtered_state)


def _svg(image):
    """The SVG an st.image element carries, back out of its data URL."""
    url = image.proto.imgs[0].url
    assert url.startswith("data:image/svg+xml;base64,"), url[:40]
    return base64.b64decode(url.split(",", 1)[1]).decode("utf-8")


def _images(node, found=None):
    found = [] if found is None else found
    for child in getattr(node, "children", {}).values():
        if type(child).__name__ == "Image":
            found.append(child)
        else:
            _images(child, found)
    return found


# --- 1. The two functions are fragments -----------------------------------

def _fragment_defs():
    """Every function in the UI half decorated @st.fragment, by name."""
    tree = ast.parse(ui_source())
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute) and dec.attr == "fragment" \
                        and isinstance(dec.value, ast.Name) and dec.value.id == "st":
                    out[node.name] = node
    return out


@pytest.mark.parametrize("name", ["_wheel_block", "_timing_wheel_block"])
def test_the_picture_block_is_a_fragment(name):
    assert name in _fragment_defs(), sorted(_fragment_defs())


def test_these_four_are_the_only_fragments_in_the_app():
    """So that another cannot appear without this file being read: a
    fragment that draws outside its own body is a runtime error, not a test
    failure, and the harness cannot see a partial rerun at all. The two grid
    blocks are item 12's (test_row_detail_2026_09_15.py)."""
    assert sorted(_fragment_defs()) == ["_strength_grid_block", "_timing_wheel_block",
                                        "_weakness_grid_block", "_wheel_block"]


def test_the_chart_fragment_generates_its_own_svg_and_the_top_level_does_not():
    """The SVG used to be built at the top level from CHART_BOUNDS and
    WHEEL_THEME. A fragment rerun does not re-run the top level, so a wheel
    built there would be the previous full run's wheel. Nothing else read
    svg_code or svg_wide -- the picture and the download button were the two
    consumers -- so the top-level build is gone rather than kept beside it."""
    src = ui_source()
    body = ast.get_source_segment(src, _fragment_defs()["_wheel_block"])
    assert body.count("generate_hybrid_svg(") == 2, "both layouts, inside the fragment"
    assert src.count("generate_hybrid_svg(") == 2, "and nowhere else in the UI half"
    # The values it builds from are the fragment's own widgets', with this
    # run's top-level reading behind them as the fallback.
    assert 'st.session_state.get("chart_bounds", CHART_BOUNDS)' in body
    assert 'st.session_state.get("wheel_dark", WHEEL_DARK)' in body


def test_the_timing_fragment_regenerates_its_svg_from_the_top_levels_data():
    """The revolution data is computed once per run, before the tabs; the
    fragment reads pn4 and the natal chart from the enclosing scope and
    regenerates only the picture."""
    body = ast.get_source_segment(ui_source(), _fragment_defs()["_timing_wheel_block"])
    assert body.count("generate_multiwheel_svg(") == 1
    assert "pn4[" in body, "the bundle is read from the enclosing scope, not recomputed"
    assert "pn4_timing_bundle(" not in body


# --- 2. The wheel still renders -------------------------------------------

@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("view", READING_DEPTHS)
def test_the_chart_page_still_draws_its_wheel(layout, view):
    """The Chart page's picture is the natal_wheel component now (item 11),
    so the SVG is read out of the envelope it was mounted with rather than
    out of an st.image data URL. The Timing page's is still an image."""
    at = _at("chart", layout=layout, view=view)
    envelope = natal_wheel_envelope(_node(at, CHART_FRAGMENT))
    assert envelope["svg"].startswith("<svg "), "an SVG, not a placeholder"
    assert envelope["width"] == (560 if layout == "Square" else "stretch")


@pytest.mark.parametrize("view", READING_DEPTHS)
def test_the_timing_page_still_draws_its_wheel(view):
    at = _at("timing", view=view)
    images = _images(_node(at, TIMING_FRAGMENT))
    assert len(images) == 1
    assert _svg(images[0]).startswith("<svg ")


def test_both_wheels_answer_their_own_controls():
    """The picture is regenerated from the widgets' values, so a change to a
    control changes the picture -- which is the whole point of generating the
    SVG inside the fragment rather than reading a top-level string."""
    at = _at("chart")
    before = natal_wheel_envelope(_node(at, CHART_FRAGMENT))["svg"]
    at.checkbox(key="chart_bounds").uncheck().run()
    assert_no_exception(at, "chart, bounds off")
    assert natal_wheel_envelope(_node(at, CHART_FRAGMENT))["svg"] != before

    at = _at("timing")
    before = _svg(_images(_node(at, TIMING_FRAGMENT))[0])
    at.selectbox(key="timing_wheel_view").select("Year over root").run()
    assert_no_exception(at, "timing, year over root")
    assert _svg(_images(_node(at, TIMING_FRAGMENT))[0]) != before


# --- 3. The store keys survive a fragment's write -------------------------

def _top_level_value(name, at):
    """What the top level's own reading of a preference comes to, for this
    rendered app -- the app's expression lifted out of the UI half and
    evaluated, not a copy of it. `_reading(widget, store, default)` is the
    app's helper, and takes the widget key over the store key over the
    default, which is exactly what it does on a run."""
    src = ui_source()
    state = _state(at)
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            expression = ast.get_source_segment(src, node.value)
            return eval(expression, {"bool": bool}, {
                "_reading": lambda widget, store, default: state.get(widget, state.get(store, default)),
            })
    raise AssertionError(f"the UI half assigns no {name}")


# (widget key, store key, the value to set, the top-level name that reads it)
FRAGMENT_KEYS = [
    ("chart_bounds", "_chart_bounds", False, "CHART_BOUNDS"),
    ("wheel_dark", "_wheel_dark", True, "WHEEL_DARK"),
]


@pytest.mark.parametrize("widget_key, store_key, value, constant", FRAGMENT_KEYS)
def test_a_checkbox_inside_the_fragment_leaves_the_store_a_full_rerun_reads(
        widget_key, store_key, value, constant):
    """_persist() writes the store key from inside a fragment exactly as it
    does at the top level. That matters because the top level reads the
    STORE on the next full run: a fragment that moved only its widget key
    would show the reader one wheel and hand the rest of the app another."""
    at = _at("chart")
    box = at.checkbox(key=widget_key)
    (box.check() if value else box.uncheck()).run()
    assert_no_exception(at, f"chart, {widget_key}={value}")
    assert at.session_state[store_key] is value

    # And now a full rerun, the way navigating or any other control causes
    # one: the top level reads the store and gets what the fragment left.
    at.run()
    assert_no_exception(at, f"chart, {widget_key}={value}, full rerun")
    assert at.session_state[store_key] is value
    assert _top_level_value(constant, at) is value


def test_the_chart_fragments_own_reading_matches_the_top_levels():
    """The fragment reads its widget key with the top-level constant behind
    it, so on a full run -- when the two cannot disagree -- the wheel drawn
    and the value every other reader sees are the same one."""
    at = _at("chart")
    at.checkbox(key="chart_bounds").uncheck().run()
    at.run()
    state = _state(at)
    assert state.get("chart_bounds", _top_level_value("CHART_BOUNDS", at)) is False


TIMING_STORE_KEYS = ["_timing_wheel_view", "_wheel_order", "_timing_bounds",
                     "_timing_lots", "_timing_rays", "_timing_twelfths"]


def test_the_timing_fragments_widgets_all_write_their_store_keys():
    at = _at("timing")
    at.selectbox(key="timing_wheel_view").select("Month over year and root").run()
    for box in ("timing_lots", "timing_rays", "timing_twelfths"):
        at.checkbox(key=box).check().run()
    at.checkbox(key="timing_bounds").uncheck().run()
    assert_no_exception(at, "timing, options set")
    at.run()
    assert_no_exception(at, "timing, full rerun")
    assert at.session_state["_timing_wheel_view"] == "Month over year and root"
    assert at.session_state["_timing_bounds"] is False
    for store in ("_timing_lots", "_timing_rays", "_timing_twelfths"):
        assert at.session_state[store] is True
    # Every store key the fragment owns is present after the full rerun.
    for store in TIMING_STORE_KEYS:
        assert store in at.session_state, store


def test_the_wheel_layout_set_on_one_page_still_reaches_the_other():
    """Both fragments write the same pair of keys for the layout, which is
    how the setting followed the reader between the pages before."""
    at = _at("chart")
    at.radio(key="wheel_layout").set_value("Wide").run()
    assert at.session_state["_wheel_layout"] == "Wide"
    timing = make_app(page="timing")
    timing.session_state["_wheel_layout"] = at.session_state["_wheel_layout"]
    timing.run()
    assert_no_exception(timing, "timing, wide")
    assert timing.radio(key="wheel_layout").value == "Wide"


# --- 4. Nothing the fragment draws stands outside it ----------------------

@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_chart_fragment_holds_its_picture_and_its_controls_and_no_more(layout):
    """A fragment may not write to a container outside itself. Streamlit
    renders one as a block of its own, so its elements are that block's
    children -- contiguous, in order, with nothing of the page's between
    them -- and the page's own elements are its siblings."""
    at = _at("chart", layout=layout)
    fragment = _node(at, CHART_FRAGMENT)
    # Square centres its picture in a flex row of its own; Wide is the bare
    # image at the page's full width. Either way the picture comes first and
    # the controls' row second, and the fragment holds those two and no more.
    assert _kinds(fragment) == [("Block" if layout == "Square" else "UnknownElement"), "Block"]
    controls = list(fragment.children.values())[1]
    assert _kinds(controls) == ["Radio", "Checkbox", "Checkbox", "DownloadButton"]
    assert len(component_mounts(fragment, "natal_wheel")) == 1
    assert _images(fragment) == [], "the picture is a component, not an image"


@pytest.mark.parametrize("layout", LAYOUTS)
def test_the_chart_pages_wheel_controls_are_all_inside_the_fragment(layout):
    """No picture, checkbox, radio or download button of the wheel's is left
    on the page beside the fragment."""
    at = _at("chart", layout=layout)
    fragment = _node(at, CHART_FRAGMENT)
    assert len(component_mounts(at.main, "natal_wheel")) == 1
    assert len(component_mounts(fragment, "natal_wheel")) == 1
    assert _images(at.main) == [], "the Chart page draws no st.image at all now"
    controls = list(fragment.children.values())[1]
    assert [c.key for c in controls.checkbox] == ["chart_bounds", "wheel_dark"]
    assert [r.key for r in controls.radio] == ["wheel_layout"]
    # The page's other two checkboxes -- the rays readings, further down --
    # are outside the fragment and are not redrawn by it.
    assert [c.key for c in at.main.checkbox][2:] == ["moon_rays_15", "mars_west_18"]
    assert [r.key for r in at.main.radio] == ["wheel_layout"]
    assert len(at.main.get("download_button")) == 1


def test_the_page_around_the_chart_fragment_is_untouched():
    """The four captions, the circumpolar warning and everything below stay
    outside, where a click on a control does not redraw them."""
    at = _at("chart")
    kids = list(at.main.children.values())
    # The header, the chart strip, the fragment, the three sentences, then
    # the page as it was.
    assert [type(k).__name__ for k in kids[:3]] == ["Header", "Caption", "Block"]
    assert [type(k).__name__ for k in kids[3:7]] == ["Caption"] * 4
    assert kids[7].value == "Calculation"


def test_the_timing_fragment_holds_the_subheader_picture_and_controls_only():
    at = _at("timing")
    fragment = _node(at, TIMING_FRAGMENT)
    assert _kinds(fragment) == ["Subheader", "Block", "Image", "DownloadButton", "Caption"]
    assert list(fragment.children.values())[0].value == "The charts, drawn"
    # The controls: the View selectbox, the layout radio, the Options popover.
    controls = list(fragment.children.values())[1]
    assert _kinds(controls) == ["Column"] * 3


def test_no_table_on_the_timing_page_is_inside_the_fragment():
    """The 67 tables are what the fragment exists to stop redrawing, so not
    one of them may be inside it."""
    at = _at("timing")
    fragment = _node(at, TIMING_FRAGMENT)

    def dataframes(node, n=0):
        for child in getattr(node, "children", {}).values():
            n = n + 1 if type(child).__name__ == "Dataframe" else dataframes(child, n)
        return n

    assert dataframes(fragment) == 0
    assert dataframes(at.main) > 50, "the page still draws its tables, outside the fragment"


def test_the_direction_strips_stay_outside_the_timing_fragment():
    """Six strips are drawn at the top level from WHEEL_THEME, on tabs of
    their own; only the revolution wheel moved."""
    at = _at("timing")
    assert len(_images(_node(at, TIMING_FRAGMENT))) == 1
    assert len(_images(at.main)) > 1


# --- The leftover: the Planetary years heading ----------------------------

def test_the_planetary_years_heading_carries_no_metadata():
    """The one heading the short-headings branch left with its citation and
    its standing inside it. The caption under it reads the way _finding()'s
    own does: the standing, a middle dot, the citation."""
    at = _at("timing")
    headings = [s.value for s in at.main.get("subheader")]
    assert "Planetary years" in headings
    assert not any("Figure 146" in h for h in headings), headings
    assert not any("display only" in h.lower() for h in headings), headings
    captions = [c.value for c in at.main.caption]
    assert "Display only · Gr. Intr. VII.8, Figure 146" in captions


def test_the_planetary_years_caption_follows_its_heading():
    at = _at("timing")
    tab = _node(at, (6, 5))
    kids = list(tab.children.values())
    at_heading = next(i for i, k in enumerate(kids)
                      if type(k).__name__ == "Subheader" and k.value == "Planetary years")
    assert type(kids[at_heading + 1]).__name__ == "Caption"
    assert kids[at_heading + 1].value == "Display only · Gr. Intr. VII.8, Figure 146"
    assert type(kids[at_heading + 2]).__name__ == "Dataframe"
