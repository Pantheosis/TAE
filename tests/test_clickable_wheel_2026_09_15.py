"""The clickable natal wheel.

Item 11 of `UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md`. The Chart
page's wheel is mounted as an `st.components.v2` component instead of being
shown with `st.image`, so that a click on a planet, an angle or a sign can
reach Python and open a panel under the controls row.

Three things have to hold and could each break quietly:

1. **The picture is the picture it always was.** The renderer gained
   `<g class="pt">` and `<g class="sign">` wrappers with `data-` attributes
   and nothing else, which is asserted by normalising the branch's SVG --
   stripping those wrappers -- and comparing it with `main`'s, byte for
   byte, for the default chart at every combination of the two flags.
2. **Every point and every sign is reachable.** A wheel whose Saturn
   carries no handle is a wheel with a dead spot no test of shape would
   see.
3. **The panel says only what the app already says.** `point_summary` and
   `sign_summary` are held here to the values the tables themselves carry:
   the whole-sign place to `get_wsh_house`, the dignities to `essential`,
   the connections to the aspect rows naming the planet, the bounds to
   `EGYPTIAN_TERMS`.

AppTest cannot click a component, so the panel is not rendered under the
harness at all -- which is also why `tests/fixtures/tables.json` does not
move. The click itself was measured in the browser; see
`docs/UI_CHANGES_2026-09-15_clickable_wheel.md`.
"""
import ast
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import pytest

from conftest import (APP_PATH, EXECUTABLE_DIR, FLORENCE, LOCAL_TIME, assert_no_exception,
                      component_mounts, make_app, natal_wheel_envelope)

SVG_NS = "{http://www.w3.org/2000/svg}"
DEFAULT_CHART = "1240-05-23"
# Every point the natal wheel draws, and the four angles it boxes.
POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
          "North Node", "South Node", "Lot of Fortune"]
ANGLES = ["Ascendant", "Midheaven", "Descendant", "Imum Coeli"]
# The added markup, and nothing else: strip it and main's SVG is left.
GROUP = re.compile(r"</?g\b[^>]*>")


def _chart(engine, date_text=DEFAULT_CHART):
    local = datetime.combine(datetime.strptime(date_text, "%Y-%m-%d").date(), LOCAL_TIME)
    dt_utc = local - timedelta(hours=FLORENCE[1] / 15.0)
    return engine["calculate_traditional_chart"](dt_utc, *FLORENCE), local


def _wheel_arguments(engine, date_text=DEFAULT_CHART):
    chart, local = _chart(engine, date_text)
    return chart, dict(chart_data=chart, chart_name="Transits", location_query="Florence",
                       lat=FLORENCE[0], lon=FLORENCE[1], dt_local=local, tz_name="LMT")


@pytest.fixture(scope="module")
def tables(engine):
    """The Chart page's own evaluators for the default chart, assembled as
    the top level assembles them."""
    chart, _local = _chart(engine)
    p_data, sect = chart["planetary_data"], chart["sect"]
    sim = engine["_simulate_forward"](p_data, chart["julian_day"])
    essential = engine["evaluate_essential_dignities"](p_data, sect)
    return {
        "chart": chart,
        "essential": essential,
        "accidental": engine["evaluate_accidental_dignities"](
            p_data, chart["houses"], sect, chart["julian_day"],
            armc=chart["armc"], obliquity=chart["obliquity"], geo_lat=FLORENCE[0]),
        "aspects": engine["evaluate_ptolemaic_aspects"](p_data),
        "reception": engine["evaluate_reception"](p_data, sect, sim),
        "classical": engine["calculate_classical_lots"](
            chart["ascendant"], p_data["Sun"]["longitude"], p_data["Moon"]["longitude"], sect),
        "topical": engine["calculate_topical_lots"](p_data, chart["ascendant"], chart["houses"], sect),
    }


def _summary(engine, tables, name):
    return engine["point_summary"](name, tables["chart"], tables["essential"], tables["accidental"],
                                   tables["aspects"], tables["reception"], tables["classical"],
                                   tables["topical"])


# --- A. The renderer gained handles and nothing else ----------------------

def _main_engine_namespace():
    """main's engine.py, executed into a namespace of its own."""
    for ref in ("origin/main", "main"):
        try:
            source = subprocess.run(["git", "show", f"{ref}:engine.py"], cwd=EXECUTABLE_DIR,
                                    capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        if source.returncode == 0 and "def generate_hybrid_svg(" in source.stdout:
            namespace = {"__file__": str(EXECUTABLE_DIR / "engine.py"),
                         "__name__": "main_engine_under_test"}
            exec(compile(source.stdout, str(EXECUTABLE_DIR / "engine.py"), "exec"), namespace)
            return namespace
    return None


@pytest.mark.parametrize("flags", [{}, {"wide": True}, {"bounds": True},
                                   {"wide": True, "bounds": True}, {"theme": "dark"}])
def test_the_normalised_svg_is_mains_svg(engine, flags):
    """The proof that the renderer only gained handles: strip the added
    <g ...> wrappers from this branch's SVG and what is left is main's,
    string for string, for the default chart at every flag."""
    old = _main_engine_namespace()
    if old is None:
        pytest.skip("main's engine.py is not in this checkout (a shallow clone); "
                    "see docs/UI_CHANGES_2026-09-15_clickable_wheel.md for the branch's own run")
    _chart_data, arguments = _wheel_arguments(engine)
    here = engine["generate_hybrid_svg"](**arguments, **flags)
    there = old["generate_hybrid_svg"](**arguments, **flags)
    assert GROUP.sub("", here) == there
    assert here != there, "the handles are in the branch's SVG"


def test_the_only_added_markup_is_the_groups_and_their_data_attributes(engine):
    """Nothing but <g> elements was added, and each carries only class and
    the data- attribute that makes it a target."""
    _chart_data, arguments = _wheel_arguments(engine)
    root = ET.fromstring(engine["generate_hybrid_svg"](**arguments))
    groups = list(root.iter(SVG_NS + "g"))
    assert groups, "the wheel carries groups now"
    for group in groups:
        assert set(group.attrib) in ({"class", "data-point", "data-lon"}, {"class", "data-sign"}), group.attrib
        assert group.get("class") in ("pt", "sign"), group.get("class")


def test_every_point_and_every_sign_carries_its_handle(engine):
    """A wheel whose Saturn has no handle has a dead spot. The convention is
    the revolution wheels' own: class="pt", data-point, data-lon."""
    chart, arguments = _wheel_arguments(engine)
    root = ET.fromstring(engine["generate_hybrid_svg"](**arguments))
    points = {group.get("data-point"): group for group in root.iter(SVG_NS + "g")
              if group.get("data-point")}
    assert sorted(points) == sorted(POINTS + ANGLES)
    assert sorted(group.get("data-sign") for group in root.iter(SVG_NS + "g")
                  if group.get("data-sign") is not None) == sorted(str(i) for i in range(12))
    # The longitude on the handle is the point's own, to six places.
    p_data = chart["planetary_data"]
    for name in POINTS:
        if name in p_data:
            expected = p_data[name]["longitude"] % 360.0
        elif name == "South Node":
            expected = (p_data["North Node"]["longitude"] + 180.0) % 360.0
        else:
            expected = chart["lot_of_fortune"] % 360.0
        assert points[name].get("data-lon") == f"{expected:.6f}", name
    assert points["Ascendant"].get("data-lon") == f"{chart['ascendant'] % 360.0:.6f}"
    assert points["Midheaven"].get("data-lon") == f"{chart['mc'] % 360.0:.6f}"


def test_the_handles_are_escaped_like_every_other_attribute():
    """_esc_attr at every attribute value, as the four renderers have done
    since a Lot name with a double quote broke a wheel."""
    body = (EXECUTABLE_DIR / "engine.py").read_text()
    body = body[body.index("def generate_hybrid_svg("):]
    body = body[:body.index("\ndef ", 1)]
    written = [line for line in body.splitlines()
               if "svg.append(" in line and ("data-point=" in line or "data-sign=" in line)]
    assert len(written) == 3, written          # the planets, the angles, the signs
    for line in written:
        assert "_esc_attr(" in line, line


# --- B. The component -----------------------------------------------------

def _registrations(tree):
    """Every call to st.components.v2.component in the app's AST."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        names = []
        while isinstance(target, ast.Attribute):
            names.append(target.attr)
            target = target.value
        if isinstance(target, ast.Name):
            names.append(target.id)
        if list(reversed(names)) == ["st", "components", "v2", "component"]:
            found.append(node)
    return found


def test_the_component_is_registered_once_and_at_the_module_level():
    """The API's own warning: a registration wrapped up with its mounting
    re-registers the name on every instance. One call, in the module body,
    assigned to a name the page mounts."""
    tree = ast.parse(APP_PATH.read_text())
    calls = _registrations(tree)
    assert len(calls) == 1, f"{len(calls)} registrations of a component in app.py"
    top_level = [node for node in tree.body
                 if isinstance(node, ast.Assign) and _registrations(node.value) == calls]
    assert len(top_level) == 1, "the registration is not a statement of the module body"
    assert [t.id for t in top_level[0].targets] == ["NATAL_WHEEL"]
    assert calls[0].args and calls[0].args[0].value == "natal_wheel"


def test_nothing_but_a_constant_reaches_the_components_own_code():
    """The html, css and js of a component are trusted code Streamlit does
    not sanitise. Each is a plain name bound to a string literal here, so no
    chart name, place label or sidebar entry can reach them; user strings
    reach the component inside `data` only, and the renderer escaped them
    before they got there."""
    tree = ast.parse(APP_PATH.read_text())
    call = _registrations(tree)[0]
    passed = {keyword.arg: keyword.value for keyword in call.keywords}
    assert set(passed) <= {"css", "js", "html"}, sorted(passed)
    literals = {node.targets[0].id: node.value for node in tree.body
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)}
    for argument, value in passed.items():
        assert isinstance(value, ast.Name), f"{argument}= is not a plain name"
        assert isinstance(literals.get(value.id), ast.Constant), f"{value.id} is not a string literal"
        assert isinstance(literals[value.id].value, str)


def test_the_components_css_does_not_colour_the_wheel():
    """The palette is inside the SVG, light or dark by the reader's own
    preference. The component styles its wrapper, its expand control and its
    tooltip, and reaches nothing inside the picture but the pointer."""
    tree = ast.parse(APP_PATH.read_text())
    css = {node.targets[0].id: node.value.value for node in tree.body
           if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
           and isinstance(node.value, ast.Constant)}["NATAL_WHEEL_CSS"]
    for rule in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selector, body = rule[0].strip(), rule[1]
        if "data-point" in selector or "data-sign" in selector:
            assert body.strip() == "cursor: pointer;", body
    assert "fill" not in css and "stroke" not in css


@pytest.mark.parametrize("layout", ["Square", "Wide"])
def test_the_chart_page_mounts_the_wheel_and_draws_no_panel(layout):
    """Under AppTest nothing is clicked, so the fragment is the picture and
    the controls row and nothing else -- which is why the page's inventory
    of tables did not move."""
    at = make_app(page="chart")
    at.session_state["_wheel_layout"] = layout
    at.run()
    assert_no_exception(at, f"chart, {layout}")
    fragment = list(at.main.children.values())[2]
    mounts = component_mounts(fragment, "natal_wheel")
    assert len(mounts) == 1
    assert len(list(fragment.children.values())) == 2, "picture, controls row, and no panel"
    assert not fragment.get("dataframe"), "no panel table until something is clicked"
    assert not fragment.get("subheader"), "no panel heading until something is clicked"


def test_the_envelope_carries_the_svg_the_width_and_the_twelve_signs():
    """Three keys and no more: the picture, the width the layout asks for,
    and the hover text of the twelve signs, so that a hover is answered in
    the browser and never reaches Python."""
    at = make_app(page="chart").run()
    assert_no_exception(at, "chart")
    envelope = natal_wheel_envelope(at.main)
    assert sorted(envelope) == ["signs", "svg", "width"]
    assert envelope["svg"].startswith("<svg ")
    assert 'data-point="Sun"' in envelope["svg"] and 'data-sign="0"' in envelope["svg"]
    assert len(envelope["signs"]) == 12
    gemini = envelope["signs"][2]
    assert gemini.startswith("Gemini")
    # The bounds and the triplicity lords, which is what the hover promises.
    for lord, limit in (("Mercury", "6"), ("Jupiter", "12"), ("Venus", "17"),
                        ("Mars", "24"), ("Saturn", "30")):
        assert f"{lord} to {limit}°" in gemini, gemini
    assert "Triplicity (Diurnal): Saturn, with Jupiter partnering" in gemini


# --- C. The panel says what the tables say --------------------------------

def test_the_suns_places_are_the_places_the_tables_print(engine, tables):
    summary = _summary(engine, tables, "Sun")
    chart = tables["chart"]
    lon = chart["planetary_data"]["Sun"]["longitude"]
    values = {row["Reading"]: row["Value"] for row in summary["position"]}
    assert values["Position"] == engine["get_degree_string"](lon)
    assert values["Sign"] == engine["get_zodiac_sign"](lon)
    assert values["Whole-sign place"] == str(engine["get_wsh_house"](lon, chart["ascendant"]))
    assert values["Quadrant division (Alchabitius)"] == str(engine["get_effective_house"](lon, chart["houses"]))
    assert values["Motion"] == "direct"


@pytest.mark.parametrize("name", ["Sun", "Moon"])
def test_the_dignities_and_conditions_are_the_evaluators_own(engine, tables, name):
    summary = _summary(engine, tables, name)
    expected = [key for key, value in tables["essential"][name].items() if value is True]
    assert [row["Dignity"] for row in summary["essential"]] == expected
    assert expected, "the default chart's luminaries hold something to show"
    conditions = [key for key, value in tables["accidental"][name].items() if value is True]
    assert [row["Condition"] for row in summary["accidental"]] == conditions


@pytest.mark.parametrize("name", ["Sun", "Moon"])
def test_the_connections_are_the_aspect_rows_naming_it(engine, tables, name):
    summary = _summary(engine, tables, name)
    expected = [row for row in tables["aspects"]
                if name in (row["Light Planet"], row["Heavy Planet"])]
    assert len(summary["connections"]) == len(expected) > 0
    for shown, row in zip(summary["connections"], expected):
        for column in ("Light Planet", "Aspect", "Heavy Planet", "Applying Planet",
                       "Motion", "Exact Orb Dist", "Connected"):
            assert shown[column] == row[column]


@pytest.mark.parametrize("name", ["Sun", "Moon"])
def test_the_receptions_are_the_reception_rows_naming_it(engine, tables, name):
    summary = _summary(engine, tables, name)
    expected = [row for row in tables["reception"]
                if name in (row["Receiver"], row["Received"])]
    assert summary["receptions"] == expected
    # The default chart has no reception at all, so an empty panel section is
    # the correct reading of it and not a missing lookup.
    assert tables["reception"] == []


@pytest.mark.parametrize("name", ["Sun", "Moon"])
def test_the_lots_are_the_lots_it_is_lord_of(engine, tables, name):
    summary = _summary(engine, tables, name)
    classical = [row["Lot Name"] for row in tables["classical"] if row["Sign Dispositor"] == name]
    topical = [row["Lot"] for row in tables["topical"] if row["Lord"] == name]
    assert [row["Lot"] for row in summary["lots"]] == classical + topical
    # Each row carries its own table's citation, and none is invented: the
    # topical table has a Source column and the classical table has none.
    for row in summary["lots"]:
        if row["Table"] == "Classical Lots":
            assert row["Source"] == ""
        else:
            source = next(r for r in tables["topical"] if r["Lot"] == row["Lot"])
            assert row["Source"] == (source["Source"] or "")


def test_a_point_the_wheel_does_not_draw_has_no_panel(engine, tables):
    assert _summary(engine, tables, "Pluto") is None


def test_the_angles_carry_their_places_and_claim_no_dignity(engine, tables):
    """An angle is a degree, not a planet: it stands somewhere and holds
    nothing. The panel says the first and does not invent the second."""
    summary = _summary(engine, tables, "Ascendant")
    values = {row["Reading"]: row["Value"] for row in summary["position"]}
    assert values["Whole-sign place"] == "1"
    assert values["Motion"] == "-"
    assert summary["essential"] == summary["accidental"] == []
    assert summary["connections"] == summary["receptions"] == summary["lots"] == []


def test_gemini_reads_as_the_reference_page_prints_it(engine):
    """Mercury's own sign: his domicile, no exaltation, the air triplicity by
    sect, the five Egyptian bounds in order and the three faces."""
    summary = engine["sign_summary"](2, "Diurnal")
    assert summary["sign"] == "Gemini" and summary["element"] == "Air"
    assert summary["lords"][0] == {"Dignity": "Domicile", "Lord": "Mercury"}
    assert summary["lords"][1] == {"Dignity": "Exaltation", "Lord": "-"}
    assert summary["lords"][2] == {"Dignity": "Triplicity (Diurnal)", "Lord": "Saturn"}
    assert summary["lords"][3] == {"Dignity": "Triplicity, participating", "Lord": "Jupiter"}
    assert summary["bounds"] == [
        {"Bound": "0°-6°", "Lord": "Mercury"},
        {"Bound": "6°-12°", "Lord": "Jupiter"},
        {"Bound": "12°-17°", "Lord": "Venus"},
        {"Bound": "17°-24°", "Lord": "Mars"},
        {"Bound": "24°-30°", "Lord": "Saturn"},
    ]
    assert [row["Lord"] for row in summary["faces"]] == ["Jupiter", "Mars", "Sun"]


def test_every_signs_lords_come_from_the_engines_own_tables(engine):
    """All twelve, against EGYPTIAN_TERMS and the triplicity table
    themselves, and against get_essential_rulers for the faces -- which is
    what the Reference page's own rows are built from."""
    terms, order = engine["EGYPTIAN_TERMS"], engine["SIGN_ORDER"]
    for index, sign in enumerate(order):
        for sect in ("Diurnal", "Nocturnal"):
            summary = engine["sign_summary"](index, sect)
            assert summary["sign"] == sign
            assert [(row["Bound"], row["Lord"]) for row in summary["bounds"]] == [
                (f"{start}°-{limit}°", lord) for (start, (limit, lord))
                in zip([0] + [limit for limit, _lord in terms[sign][:-1]], terms[sign])]
            rulers = engine["get_essential_rulers"](index * 30 + 15)
            assert summary["lords"][0]["Lord"] == rulers["domicile"]
            assert summary["lords"][2]["Lord"] == rulers[
                "triplicity_day" if sect == "Diurnal" else "triplicity_night"]
            assert summary["lords"][3]["Lord"] == rulers["triplicity_participating"]
            assert [row["Lord"] for row in summary["faces"]] == [
                engine["get_essential_rulers"](index * 30 + degree)["face"] for degree in (5, 15, 25)]


def test_the_sign_index_is_read_the_way_a_click_sends_it(engine):
    """The component sends "sign:<0-11>" and the panel reads the number, so
    the wrap-around is the engine's to hold."""
    assert engine["sign_summary"](0)["sign"] == "Aries"
    assert engine["sign_summary"](11)["sign"] == "Pisces"
    assert engine["sign_summary"](12)["sign"] == "Aries"
