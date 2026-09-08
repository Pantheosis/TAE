"""The switch matrix. The page controls in conftest.SWITCHES rewrite module
globals -- the Connection rule radio and the configurable readings, each
on the page it affects and read at the top level from a persisted store
key -- and the Configurations page has a three-way view. Every combination must render
without exception on every chart. This is the check that would have
caught the KeyError: 'Net (heuristic)' (a renamed column, seen only under
the Abu Ma'shar view).

The Configurations page under the "Both" view executes the union of the
Sahl and Abu Ma'shar code paths, so the full 2**len(SWITCHES) cross-product
runs there (64 states with six switches; each added switch doubles it). The other pages read at most one or two of the switches, so
each is rendered once per single-switch alternative instead of 64 times.
"""
from itertools import product

import pytest

from conftest import CHARTS, PAGES, SWITCHES, assert_no_exception, find_page_widget, make_app, slot_name

SWITCH_NAMES = list(SWITCHES)
MATRIX = list(product(*(SWITCHES[n][1] for n in SWITCH_NAMES)))   # 2**len(SWITCHES) states


def _state_id(values):
    return ",".join(f"{n}={v}" for n, v in zip(SWITCH_NAMES, values))


@pytest.mark.matrix
@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("values", MATRIX, ids=_state_id)
def test_configurations_both_views_under_every_switch_state(date, values):
    switches = dict(zip(SWITCH_NAMES, values))
    at = make_app(date=date, page="configurations", view="Both", switches=switches).run()
    assert_no_exception(at, f"{date} configurations/Both {_state_id(values)}")
    assert len(at.main.dataframe) > 0


@pytest.mark.matrix
@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("view", ["Sahl (course text)", "Abu Ma'shar (supplement)"])
@pytest.mark.parametrize("name", SWITCH_NAMES)
def test_configurations_single_views_under_each_alternative(date, view, name):
    alternative = SWITCHES[name][1][1]
    at = make_app(date=date, page="configurations", view=view, switches={name: alternative}).run()
    assert_no_exception(at, f"{date} configurations/{view} {name}={alternative}")


@pytest.mark.matrix
@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("page", [p for p in PAGES if p != "configurations"])
@pytest.mark.parametrize("name", SWITCH_NAMES)
def test_other_pages_under_each_alternative(date, page, name):
    alternative = SWITCHES[name][1][1]
    at = make_app(date=date, page=page, switches={name: alternative}).run()
    assert_no_exception(at, f"{date} {slot_name(page, None)} {name}={alternative}")


@pytest.mark.parametrize("name", SWITCH_NAMES)
def test_every_switch_renders_on_its_page(name):
    """Each control lives on the page it affects, and the store key the
    engine reads is what the widget shows: set the alternative through the
    store, render the page, and the widget must display it."""
    store, alternatives, page, view, kind, prefix = SWITCHES[name]
    at = make_app(page=page, view=view, switches={name: alternatives[1]}).run()
    assert_no_exception(at, f"{page} {name}")
    widget = find_page_widget(at, kind, prefix)
    assert widget.value == alternatives[1], f"{name}: widget shows {widget.value!r}, store holds {alternatives[1]!r}"
    # No reading is left in the sidebar.
    assert not [w for w in list(at.sidebar.radio) + list(at.sidebar.checkbox) if w.label.startswith(prefix)]


def test_page_control_survives_navigation():
    """The persist pattern: a value chosen on the Configurations page is
    still in force after rendering another page and coming back."""
    at = make_app(page="configurations", view="Both").run()
    find_page_widget(at, "radio", "Connection test").set_value("Abu Ma'shar").run()
    assert at.session_state["_connection_rule"] == "Abu Ma'shar"
    from streamlit.util import calc_hash
    at._page_hash = calc_hash("chart"); at.run()
    at._page_hash = calc_hash("configurations"); at.run()
    assert_no_exception(at)
    assert find_page_widget(at, "radio", "Connection test").value == "Abu Ma'shar"
    assert any("Abu Ma'shar rule in force" in c.value for c in at.main.caption)
