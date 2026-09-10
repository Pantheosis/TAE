"""The Configurations page in chapters and the reading depth (2026-09-10,
UI_REVIEW_2026-09-10.md §1 B and §3)."""
from conftest import CHARTS, READING_DEPTHS, assert_no_exception, make_app, table_inventory

SAHL = {"Aspects, aversions and connections", "Strength of the Planets", "Weakness of the Planets",
        "Prevented connections", "Corruption of the Moon"}
ABU = {"Planetary Condition", "Rays cast by ascensions (Ptolemy's method as reported by Abu Ma'shar, VII.7)"}


def _render(depth, date="1240-05-26"):
    at = make_app(date=date, page="configurations")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"configurations under {depth}")
    return at


def test_course_text_keeps_abu_mashar_in_his_own_chapter():
    at = _render("Course text")
    labels = [t.label for t in at.main.tabs]
    assert labels == ["Aspects and connections", "Handing over and reception", "Prevented connections",
                      "Strength and weakness", "Abu Ma'shar (supplement)"]
    # His tables are in the last tab and nowhere else.
    last = at.main.tabs[-1]
    inside = {n.value for n in last if getattr(n, "type", None) == "subheader"}
    assert ABU <= inside
    for tab in at.main.tabs[:-1]:
        heads = {n.value for n in tab if getattr(n, "type", None) == "subheader"}
        assert not (heads & ABU), (tab.label, heads & ABU)


def test_the_supplement_joins_the_topics_it_belongs_to():
    at = _render("Course text and supplement")
    labels = [t.label for t in at.main.tabs]
    assert labels == ["Aspects and connections", "Handing over and reception", "Prevented connections",
                      "Strength and weakness"]
    heads = {tab.label: {n.value for n in tab if getattr(n, "type", None) == "subheader"} for tab in at.main.tabs}
    assert "Planetary Condition" in heads["Strength and weakness"]
    assert "Rays cast by ascensions (Ptolemy's method as reported by Abu Ma'shar, VII.7)" in heads["Aspects and connections"]
    assert "Aspects, aversions and connections" in heads["Aspects and connections"]
    assert "Strength of the Planets" in heads["Strength and weakness"]


def test_the_same_tables_render_under_either_depth():
    """The depth moves tables between chapters; it never adds or removes one."""
    for date in list(CHARTS)[:3]:
        a = sorted(table_inventory(_render("Course text", date)))
        b = sorted(table_inventory(_render("Course text and supplement", date)))
        assert a == b, date


def test_the_chapter_is_a_reading_and_the_controls_stay_above_it():
    at = make_app(page="configurations")
    at.session_state["_configurations_tab"] = "Prevented connections"
    at.run()
    assert_no_exception(at, "stored tab")
    assert at.session_state["configurations_tab"] == "Prevented connections"
    assert [r for r in at.main.radio if r.label.startswith("Connection test")]
    assert [c for c in at.main.checkbox if c.label.startswith("Fitting infortune")]
    # A stored tab that the fuller depth removes falls back to the first.
    at2 = make_app(page="configurations")
    at2.session_state["_configurations_tab"] = "Abu Ma'shar (supplement)"
    at2.session_state["_reading_depth"] = "Course text and supplement"
    at2.run()
    assert_no_exception(at2, "removed tab")
    assert at2.session_state["configurations_tab"] == "Aspects and connections"


def test_dignities_supplement_expanders_follow_the_depth():
    from conftest import ui_source
    src = ui_source()
    assert src.count("expanded=READING_DEPTH == READING_DEPTH_OPTIONS[1]") == 3
    for depth in READING_DEPTHS:
        at = make_app(page="dignities")
        at.session_state["_reading_depth"] = depth
        at.run()
        assert_no_exception(at, f"dignities under {depth}")
