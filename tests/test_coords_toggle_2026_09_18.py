"""The coordinate toggle starts the fields at the place the box shows on
that run.

F02 of the review of 2026-09-16 made "Enter coordinates directly" a change
of input method rather than of place: the fields open at the place that is
resolved. Its callback read _resolved_lat/_resolved_lon, the PREVIOUS run's
place, and the natural gesture -- a city typed over the box and the toggle
clicked without Enter, the click's mouse-down committing the text so that
the edit and the switch arrive in one run -- started the fields at the
place the box no longer showed (seen in passing by the Here & Now branch's
adversarial pass, 2026-09-17, which fixed the same staleness in "Set as
home" and left this one for the owner).

Now the callback only flags that the toggle moved; the toggle's own site
starts the fields from THIS run's values: the box's committed text, which
is in its key on that run whether or not the box is drawn, resolved as
the box would resolve it (a typed pair, or the atlas's first match) when
the text has moved since it was last resolved; the last resolution
(its choice among the matches included) when it has not, or when the
moved text resolves to nothing. The one atlas lookup, _atlas_matches, is
shared by the box and the site.

Every AppTest runs under the harness's scratch XDG_DATA_HOME with
preferences off (conftest).
"""
import ast

import pytest

from conftest import assert_no_exception, make_app, ui_source

BERLIN = (52.52437, 13.41053)             # the atlas's first match for "Berlin"
MADRID = (40.4165, -3.70256)              # the atlas's first match for "Madrid"
MADRID_CO = (4.73245, -74.26419)          # "Madrid, 33 (CO)", its third match


def _city_app(text):
    at = make_app(page="chart")
    at.session_state["manual_coords_key"] = False
    at.session_state["location_input_key"] = text
    return at


def _fields(at):
    return (at.sidebar.number_input(key="manual_lat_key").value,
            at.sidebar.number_input(key="manual_lon_key").value)


def _resolved_box(at):
    return [s.value for s in at.sidebar.success][0]


def test_the_fields_start_at_the_place_the_box_shows_on_that_run():
    """Berlin resolved; "Madrid" typed over it and the toggle clicked
    without Enter, one run: the fields open on Madrid. At main they opened
    on Berlin."""
    at = _city_app("Berlin").run()
    assert_no_exception(at, "Berlin")
    assert _resolved_box(at).startswith("**Berlin, ")
    at.sidebar.text_input(key="location_input_key").set_value("Madrid")
    at.sidebar.toggle(key="manual_coords_key").set_value(True)
    at.run()
    assert_no_exception(at, "edit and toggle in one run")
    assert _fields(at) == pytest.approx(MADRID, abs=1e-4), _fields(at)
    assert _resolved_box(at).startswith("**Manual [40.4165, -3.7026]**")


def test_a_pair_typed_over_the_box_starts_the_fields_at_the_pair():
    at = _city_app("Berlin").run()
    at.sidebar.text_input(key="location_input_key").set_value("10.5, -20.25")
    at.sidebar.toggle(key="manual_coords_key").set_value(True)
    at.run()
    assert_no_exception(at, "a pair and the toggle in one run")
    assert _fields(at) == (10.5, -20.25)


def test_the_choice_among_matches_is_kept_when_the_text_has_not_moved():
    """"Madrid" resolved and its third match chosen in the selectbox, a run
    of its own; then the toggle alone: the fields open on the chosen
    match, not on the first -- the last resolution stands for a text that
    has not moved since."""
    at = _city_app("Madrid").run()
    picker = [s for s in at.sidebar.selectbox if s.label.startswith("Select specific location")][0]
    assert picker.options[0].startswith("Madrid, 29 (ES)")
    colombia = [o for o in picker.options if o.startswith("Madrid, 33 (CO)")][0]
    picker.select(colombia).run()
    assert_no_exception(at, "the third match")
    assert _resolved_box(at).startswith("**Madrid, 33 (CO)**")
    at.sidebar.toggle(key="manual_coords_key").set_value(True).run()
    assert_no_exception(at, "the toggle")
    assert _fields(at) == pytest.approx(MADRID_CO, abs=1e-4), _fields(at)


def test_a_moved_text_that_resolves_to_nothing_keeps_the_last_place():
    """Berlin resolved; a text no atlas row matches typed over it and the
    toggle clicked in one run: the box holds no place, so the fields open
    on the last place that resolved, Berlin -- as they did at main."""
    at = _city_app("Berlin").run()
    at.sidebar.text_input(key="location_input_key").set_value("zzzz-no-such-city")
    at.sidebar.toggle(key="manual_coords_key").set_value(True)
    at.run()
    assert_no_exception(at, "no such city and the toggle in one run")
    assert _fields(at) == pytest.approx(BERLIN, abs=1e-4), _fields(at)


def test_nothing_ever_resolved_leaves_the_fields_as_they_were():
    """A session whose first run resolved nothing (an unmatched text), then
    the toggle: no place ever resolved, so the fields open on what they
    held -- the harness's seeds here, EXAMPLE_CHART's constants in a fresh
    session -- the F02 rule's own fallback."""
    at = _city_app("zzzz-no-such-city").run()
    assert_no_exception(at, "no such city")
    assert "_resolved_lat" not in at.session_state
    at.sidebar.toggle(key="manual_coords_key").set_value(True).run()
    assert_no_exception(at, "the toggle")
    assert _fields(at) == pytest.approx((43.7792, 11.2463)), _fields(at)


def test_the_callback_only_flags_and_the_site_reads_this_runs_text():
    """The shape the fix has to keep: _manual_coords_switched writes one
    flag and reads nothing resolved; the toggle's site pops the flag and
    resolves the box's committed text through _place_the_box_holds, the
    same lookup the box uses (_atlas_matches, called from exactly the box's
    branch and that helper)."""
    tree = ast.parse(ui_source())
    defs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    callback = defs["_manual_coords_switched"]
    statements = [n for n in callback.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    assert len(statements) == 1 and isinstance(statements[0], ast.Assign), ast.dump(callback)
    literals = {n.value for n in ast.walk(callback) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "_coords_switched" in literals and not literals & {"_resolved_lat", "_resolved_lon", "manual_lat_key"}
    # _atlas_matches is called from the box's branch and from
    # _place_the_box_holds, and nowhere else.
    callers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_atlas_matches":
            callers.append(node.lineno)
    assert len(callers) == 2, callers
    helper_lines = set(range(defs["_place_the_box_holds"].lineno, defs["_place_the_box_holds"].end_lineno + 1))
    assert len([ln for ln in callers if ln in helper_lines]) == 1
    # The sidebar's own resolution query is written once, in _atlas_matches.
    assert ui_source().count("FROM cities") == 1
