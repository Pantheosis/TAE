"""The page list at the top, the repeated title gone, and the chart strip
under every page header (UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md,
§A items 3, 4 and B item 10).

The sidebar is the nativity form now; the page list is a header bar. Each
page opens with its st.header, then one caption naming the chart the page is
reading -- and nothing between the two.
"""
import pytest
from streamlit.util import calc_hash

from conftest import (PAGES, READING_DEPTHS, assert_no_exception, make_app,
                      ui_source)


def test_navigation_sits_at_the_top_and_keeps_its_three_sections():
    src = ui_source()
    assert 'st.navigation(pages, position="top")' in src
    # expanded= is read only when position="sidebar"; it went with the move.
    assert "expanded=True" not in src
    for section in ('"Part 1: the nativity"', '"Part 2: prediction"', '"Reference"'):
        assert section in src


def test_no_page_repeats_the_app_name_as_a_title():
    """The name is the browser title and the header bar's; it was an st.title
    above every page's st.header as well."""
    assert 'st.title(' not in ui_source()
    for page in PAGES:
        at = make_app(page=page).run()
        assert_no_exception(at, page)
        assert len(at.main.title) == 0, f"{page} rendered an st.title"


@pytest.mark.parametrize("page", PAGES)
def test_every_page_opens_with_its_header_and_then_the_chart_strip(page):
    at = make_app(page=page).run()
    assert_no_exception(at, page)
    assert len(at.main.header) == 1, f"{page}: expected exactly one st.header"
    captions = [c.value for c in at.main.caption]
    assert captions, f"{page}: no caption at all"
    # The strip is the FIRST caption: on the pages that carry one it comes
    # before _readings_note() and before the page's own opening sentence.
    strip = captions[0]
    parts = strip.split(" · ")
    assert len(parts) == 7, f"{page}: the strip has {len(parts)} parts: {strip!r}"
    name, when, standard, place, sect, day, hour = parts
    assert name == "Unsaved chart"                       # the harness saves none
    assert when == "1240-05-23 14:30:00"
    assert standard.startswith("LMT ")                   # the harness casts in LMT
    assert place.endswith("43.78, 11.25")                # two decimals, not four
    assert sect == "Diurnal"
    assert day.startswith("Day lord ") and hour.startswith("Hour lord ")


def test_the_strip_names_a_saved_chart_when_one_is_loaded():
    at = make_app(page="chart")
    # The picker's options come from saved_charts; a selection that is not an
    # option is discarded before the page runs.
    at.session_state["saved_charts"] = {"Test Chart 1240": {}}
    at.session_state["chart_picker"] = "Test Chart 1240"
    at.run()
    assert_no_exception(at, "chart with a saved chart picked")
    assert at.main.caption[0].value.startswith("Test Chart 1240 · ")


@pytest.mark.parametrize("view", READING_DEPTHS)
def test_the_findings_page_carries_the_strip_at_both_reading_depths(view):
    at = make_app(page="findings", view=view).run()
    assert_no_exception(at, f"findings, {view}")
    assert len(at.main.header) == 1 and at.main.header[0].value == "Findings"
    assert at.main.caption[0].value.startswith("Unsaved chart · 1240-05-23 14:30:00 · ")
    assert len(at.main.title) == 0


def test_the_chart_pages_intro_no_longer_sends_the_reader_down_the_sidebar():
    """The reference pages are in the header bar now, not at the sidebar's
    foot; the sentence that said so is the only page text the move touched."""
    src = ui_source()
    assert "at the foot of the sidebar" not in src
    assert "The reference tables and the sources are at the end of the page list above." in src
    # The nativity form still is the sidebar, and still opens with the picker.
    assert "Enter a chart in the sidebar, or load a saved one from the top of it." in src


def test_the_default_page_is_served_at_the_root_but_keeps_its_url_path():
    """Streamlit 1.62: Page.url_path returns "" for the default page, so
    /chart is never a route -- but Page._script_hash is calc_hash of the
    PRIVATE _url_path, which keeps the given string. That is why url_path=
    stays on the Chart page and why make_app(page="chart") resolves."""
    at = make_app(page="chart").run()
    assert_no_exception(at, "chart")
    assert at.main.header[0].value == "Chart"
    assert 'url_path="chart"' in ui_source()
    # An unknown hash falls back to the default page, which is the Chart page.
    fallback = make_app(page="chart")
    fallback._page_hash = calc_hash("")
    fallback.run()
    assert_no_exception(fallback, "root")
    assert fallback.main.header[0].value == "Chart"
