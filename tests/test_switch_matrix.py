"""The switch matrix. The sidebar carries six controls that rewrite module
globals -- the Connection rule radio and the five "Configurable readings"
-- and the Configurations page has a three-way view. Every combination must
render without exception on every chart. This is the check that would have
caught the KeyError: 'Net (heuristic)' (a renamed column, seen only under
the Abu Ma'shar view).

The Configurations page under the "Both" view executes the union of the
Sahl and Abu Ma'shar code paths, so the full 2**6 = 64-state cross-product
runs there. The other pages read at most one or two of the switches, so
each is rendered once per single-switch alternative instead of 64 times.
"""
from itertools import product

import pytest

from conftest import CHARTS, PAGES, SWITCHES, assert_no_exception, make_app, slot_name

SWITCH_NAMES = list(SWITCHES)
MATRIX = list(product(*(SWITCHES[n][2] for n in SWITCH_NAMES)))   # 64 states


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
    alternative = SWITCHES[name][2][1]
    at = make_app(date=date, page="configurations", view=view, switches={name: alternative}).run()
    assert_no_exception(at, f"{date} configurations/{view} {name}={alternative}")


@pytest.mark.matrix
@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("page", [p for p in PAGES if p != "configurations"])
@pytest.mark.parametrize("name", SWITCH_NAMES)
def test_other_pages_under_each_alternative(date, page, name):
    alternative = SWITCHES[name][2][1]
    at = make_app(date=date, page=page, switches={name: alternative}).run()
    assert_no_exception(at, f"{date} {slot_name(page, None)} {name}={alternative}")


def test_every_switch_is_present_in_the_sidebar():
    """The matrix locates controls by label prefix; if a restructure moves
    or renames one, fail here with the name rather than 320 times below."""
    at = make_app().run()
    labels = [w.label for w in at.sidebar.radio] + [w.label for w in at.sidebar.checkbox]
    for name, (kind, prefix, _alts) in SWITCHES.items():
        hits = [l for l in labels if l.startswith(prefix)]
        assert len(hits) == 1, f"switch {name!r}: expected one sidebar {kind} starting '{prefix}', got {hits}"
