"""A fragment rerun evaluates under the run's own readings.

The readings are per run and per thread (PR #45): app.py pins them at the
top of each run with engine.set_readings and every evaluator asks through
engine.reading(), which falls back to the module default in a thread that
has pinned nothing. Five blocks of the pages are @st.fragment bodies (the
fragments of 2026-09-15), and a click on one of their own widgets reruns
the body alone -- in a fresh ScriptRunner thread whenever the previous
run's runner has stopped, which is the ordinary case, the reader clicking
after the page has rendered. The top level does not execute on such a
rerun, so nothing pinned, and the Timing wheel's Lots ring -- the one
fragment path that reaches an evaluator reading a reading, lot_by_id and
LOT_HOUSE_CUSP -- drew the house-based Lots at the whole-sign cusps under a
'quadrant cusp' run: assets, travel and enemies moved by 9-15 degrees on
1240-05-23 Florence while the two death Lots, which carry their own cusp
rule, stood (G18 of the doctrine audit, both readers, 2026-09-17/18).

The fix: every fragment is declared with app.py's _pinned_fragment, which
is st.fragment with the run's recorded pins (_RUN_READINGS, filled by
_pin_readings at both pin sites) re-pinned in the rerun's thread before
the body runs. The body Streamlit stores is a closure over the full run
that declared it, so the record it reads is that run's.

What is pinned here:

A. Behaviour, on Streamlit's own server path -- a full run under AppTest,
   then a fragment-only rerun of the stored fragment through a second
   LocalScriptRunner sharing the first run's fragment storage and session
   state, with RerunData(fragment_id_queue=[...]) as AppSession.request_rerun
   sends it, in a new thread (the readers' C-FR recipe):
   1. the Timing wheel's cusp-based Lots have the same longitudes on the
      fragment rerun as on the full run, and lot_by_id sees the run's
      LOT_HOUSE_CUSP there;
   2. the Chart wheel's renderer, the engine function that fragment reaches,
      runs under every one of the run's readings on the rerun;
   3. every fragment of every page that has one, rerun alone, pins exactly
      the run's readings in its own thread before its body -- the planets
      block on Dignities and the two tick grids on Configurations reach no
      engine function, so this is their probe.
   Each fails at main (9476d8b): the rerun's thread reads the defaults.
B. Structure, by AST over app.py, so a future fragment cannot regress
   silently: every fragment is declared with _pinned_fragment and no other
   way; st.fragment is called once, inside it; the wrapper pins the record
   before it calls the body; every engine.set_readings in the file goes
   through _pin_readings or the wrapper, so the record is complete; and no
   doctrinal reading's control stands inside a fragment, which is the
   premise that a reading cannot move without a full run.

Every AppTest here runs under the harness's scratch XDG_DATA_HOME and with
preferences off (conftest); the engine's functions are wrapped AFTER
make_app, which is where the harness reloads the engine.
"""
import ast
import threading
from unittest.mock import MagicMock

import pytest
from streamlit.runtime import Runtime
from streamlit.runtime.caching.storage.dummy_cache_storage import MemoryCacheStorageManager
from streamlit.runtime.dataframe_source_manager import DataframeSourceManager
from streamlit.runtime.fragment import MemoryFragmentStorage
from streamlit.runtime.media_file_manager import MediaFileManager
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
from streamlit.runtime.pages_manager import PagesManager
from streamlit.runtime.scriptrunner import RerunData
from streamlit.runtime.scriptrunner.script_cache import ScriptCache
from streamlit.testing.v1.element_tree import parse_tree_from_messages
from streamlit.testing.v1.local_script_runner import LocalScriptRunner, require_widgets_deltas
from streamlit.testing.v1.util import patch_config_options

from conftest import APP_PATH, assert_no_exception, make_app, ui_source

FRAGMENTS = ["_planets_in_houses_block", "_strength_grid_block", "_timing_wheel_block",
             "_weakness_grid_block", "_wheel_block"]
# The pages that declare fragments, with how many each declares.
FRAGMENT_PAGES = {"chart": 1, "dignities": 1, "configurations": 2, "timing": 1}
# The three Lots whose start, end or projection is a house cusp and which
# carry no cusp rule of their own, so LOT_HOUSE_CUSP decides where they
# stand; the two death Lots carry their own rule and are the control.
CUSP_LOTS = ("assets_lord2", "travel", "enemies_hermes")
DEATH_LOTS = ("death", "death_ws")


# --- The fragment-only rerun ----------------------------------------------

@pytest.fixture
def shared_fragments(monkeypatch):
    """Every LocalScriptRunner made while this is in force shares one
    MemoryFragmentStorage, so the fragments a full run registers are there
    for the runner that reruns one of them alone -- as the server's runners
    share a session's storage."""
    storage = MemoryFragmentStorage()
    original = LocalScriptRunner.__init__

    def _sharing(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self._fragment_storage = storage

    monkeypatch.setattr(LocalScriptRunner, "__init__", _sharing)
    return storage


def _fragment_rerun(at, fragment_ids, timeout=120):
    """Rerun the given fragments alone, as the server does after a full run's
    runner has stopped: a new LocalScriptRunner on the same session state, a
    new thread, RerunData naming the fragments and nothing else. Returns
    the rerun's element tree."""
    runtime = MagicMock(spec=Runtime)
    runtime.media_file_mgr = MediaFileManager(MemoryMediaFileStorage("/mock/media"))
    runtime.cache_storage_manager = MemoryCacheStorageManager()
    runtime.dataframe_source_mgr = DataframeSourceManager()
    runtime.bidi_component_registry = at._bidi_component_manager
    Runtime._instance = runtime
    try:
        runner = LocalScriptRunner(str(APP_PATH), at.session_state,
                                   PagesManager(str(APP_PATH), ScriptCache(), setup_watcher=False))
        with patch_config_options({"global.appTest": True}):
            runner.request_rerun(RerunData(page_script_hash=at._page_hash, fragment_id_queue=list(fragment_ids)))
            runner.start()
            require_widgets_deltas(runner, timeout)
    finally:
        Runtime._instance = None
    tree = parse_tree_from_messages(runner.forward_msgs())
    assert "FRAGMENT_STOPPED_WITH_SUCCESS" in [e.name for e in runner.events], [e.name for e in runner.events]
    assert not tree.get("exception"), [e.value for e in tree.get("exception")]
    return tree


def _off_default(engine):
    """Every reading the engine reads, moved off its course default, by
    store key -- so that a thread reading the defaults is caught on every
    one of them."""
    return {
        "_connection_rule": "Abu Ma'shar",
        "_eastern_rule": engine.EASTERN_RULE_OPTIONS[1],
        "_moon_rays_15": True,
        "_mars_west_18": True,
        "_domain_rule": engine.DOMAIN_RULE_OPTIONS[1],
        "_lot_house_cusp": engine.LOT_HOUSE_CUSP_OPTIONS[1],
        "_fitting_infortune": True,
    }


def _readback(engine):
    """This thread's answer for every reading the engine reads."""
    return {name: engine.reading(name) for name in engine.READINGS}


def _record_pins(engine, monkeypatch, log):
    """Wrap engine.set_readings to log (thread object, pins, answers).

    A completed runner's numeric thread identifier can be recycled before
    the fragment runner starts. The Thread objects remain distinct, which
    is the lifecycle this test needs to distinguish.
    """
    original = engine.set_readings

    def _recording(**values):
        original(**values)
        log.append((threading.current_thread(), dict(values), _readback(engine)))

    monkeypatch.setattr(engine, "set_readings", _recording)


def _run_pins(log, thread):
    """The union of what one thread pinned, in order -- the run's record."""
    out = {}
    for ident, values, _seen in log:
        if ident == thread:
            out.update(values)
    return out


# --- A. Behaviour ----------------------------------------------------------

def test_the_timing_wheels_lots_are_the_runs_on_a_fragment_rerun(shared_fragments, monkeypatch):
    """C-FR as the readers wrote it: 1240-05-23 Florence, the Timing page at
    2026-09-17 (the Year view, one ring), Lots on, the house-based Lots
    measured to the quadrant cusp. The full run, then the wheel's fragment
    alone in a new thread: lot_by_id sees 'quadrant cusp' in that thread
    and every Lot stands where the full run put it. At main the fragment
    thread saw 'whole-sign place' and assets, travel and enemies moved
    (15.25 -> 1.81, 177.56 -> 163.86, 263.28 -> 253.86) while the death
    Lots did not."""
    at = make_app(page="timing")
    import engine
    calls = []
    original = engine.lot_by_id

    def _recording(lot_id, planets, ascendant, houses, sect, *args, **kwargs):
        value = original(lot_id, planets, ascendant, houses, sect, *args, **kwargs)
        calls.append((threading.get_ident(), engine.reading("LOT_HOUSE_CUSP"), (lot_id, round(ascendant, 6)), value))
        return value

    monkeypatch.setattr(engine, "lot_by_id", _recording)
    at.session_state["_lot_house_cusp"] = "quadrant cusp"
    at.session_state["_timing_lots"] = True
    at.session_state["_target_mode"] = engine.TARGET_MODE_OPTIONS[0]      # "Date"
    at.session_state["_target_date"] = "2026-09-17"
    at.run(timeout=120)
    assert_no_exception(at, "the full run")
    full = list(calls)
    calls.clear()
    assert len(shared_fragments._fragments) == 1, "the Timing page declares one fragment, the wheel's"
    full_threads = {ident for ident, *_ in full}
    assert len(full_threads) == 1 and {seen for _, seen, *_ in full} == {"quadrant cusp"}, full_threads

    _fragment_rerun(at, shared_fragments._fragments)
    fragment = list(calls)
    assert fragment, "the fragment rerun drew the Lots ring through lot_by_id"
    fragment_threads = {ident for ident, *_ in fragment}
    assert len(fragment_threads) == 1 and fragment_threads.isdisjoint(full_threads), \
        "a fragment-only rerun runs in a thread of its own, as the server's does"

    full_map = {key: value for _, _, key, value in full}
    fragment_map = {key: value for _, _, key, value in fragment}
    common = set(full_map) & set(fragment_map)
    assert len(common) == len(fragment_map) >= 37, (len(common), len(fragment_map))
    ring = {key[0] for key in common}
    assert set(CUSP_LOTS) <= ring and set(DEATH_LOTS) <= ring, sorted(ring)
    moved = {key: (full_map[key], fragment_map[key]) for key in common
             if (full_map[key] is None) != (fragment_map[key] is None)
             or (full_map[key] is not None and abs(full_map[key] - fragment_map[key]) > 1e-6)}
    assert not moved, f"Lots that moved on the fragment rerun (full run, fragment rerun): {moved}"
    assert {seen for _, seen, *_ in fragment} == {at.session_state["_lot_house_cusp"]}, \
        {seen for _, seen, *_ in fragment}


def test_the_chart_wheels_renderer_runs_under_the_runs_readings(shared_fragments, monkeypatch):
    """The Chart page's fragment reaches one engine function, the wheel's
    renderer generate_hybrid_svg. With every reading off its default, the
    renderer on the fragment rerun answers, for every reading, what the
    full run answered -- and not the module default. 1240-10-05 Florence,
    on which fitting_infortune(asc) gives Saturn, so SOFTENED_INFORTUNE is
    not compared None against None (1240-05-23's Ascendant is ruled by a
    benefic, for which the reading is None both ways)."""
    at = make_app(page="chart", date="1240-10-05")
    import engine
    seen = []
    original = engine.generate_hybrid_svg

    def _recording(*args, **kwargs):
        seen.append((threading.get_ident(), _readback(engine)))
        return original(*args, **kwargs)

    monkeypatch.setattr(engine, "generate_hybrid_svg", _recording)
    for store, value in _off_default(engine).items():
        at.session_state[store] = value
    at.run(timeout=120)
    assert_no_exception(at, "the full run")
    assert len(shared_fragments._fragments) == 1, "the Chart page declares one fragment, the wheel's"
    full = list(seen)
    seen.clear()
    assert full and len({ident for ident, _ in full}) == 1
    full_thread, full_readings = full[0]
    defaults = {name: getattr(engine, name) for name in engine.READINGS}
    assert full_readings != defaults, "the run's readings are off their defaults, so the probe has teeth"
    assert full_readings["LOT_HOUSE_CUSP"] == engine.LOT_HOUSE_CUSP_OPTIONS[1]
    assert full_readings["MOON_RAYS_ORB"] == 15.0
    assert full_readings["SOFTENED_INFORTUNE"] is not None, \
        "the probe date must give fitting_infortune(asc) a planet, or this reading is compared None against None"

    _fragment_rerun(at, shared_fragments._fragments)
    assert seen, "the fragment rerun regenerated the wheel"
    for ident, readings in seen:
        assert ident != full_thread, "a fragment-only rerun runs in a thread of its own"
        assert readings == full_readings, {name: (readings[name], full_readings[name])
                                           for name in readings if readings[name] != full_readings[name]}


@pytest.mark.parametrize("page", sorted(FRAGMENT_PAGES))
def test_every_fragment_pins_the_runs_readings_in_its_own_thread(page, shared_fragments, monkeypatch):
    """Each fragment of the page, rerun alone in a new thread, pins exactly
    the readings the full run pinned -- the record the run kept -- and the
    thread then answers with them. The planets block (Dignities) and the
    two tick grids (Configurations) reach no engine function at all, so
    what can be observed for them is the pin itself, which is what makes any evaluator they may come to call answer
    as the full run's would. At main no pin happens in the fragment's
    thread. The chart run uses 1240-10-05 Florence rather than the
    default 1240-05-23, on which fitting_infortune(asc) is None."""
    at = make_app(page=page, date="1240-10-05") if page == "chart" else make_app(page=page)
    import engine
    pins = []
    _record_pins(engine, monkeypatch, pins)
    for store, value in _off_default(engine).items():
        at.session_state[store] = value
    at.run(timeout=120)
    assert_no_exception(at, f"the full run of {page}")
    assert len(shared_fragments._fragments) == FRAGMENT_PAGES[page], \
        f"{page} declares {FRAGMENT_PAGES[page]} fragments; found {len(shared_fragments._fragments)}"
    full_threads = {ident for ident, _, _ in pins}
    assert len(full_threads) == 1, "one full run, one thread"
    full_thread = full_threads.pop()
    run_record = _run_pins(pins, full_thread)
    assert set(run_record) == set(engine.READINGS), "the full run pinned every reading the engine reads"
    assert run_record["LOT_HOUSE_CUSP"] == engine.LOT_HOUSE_CUSP_OPTIONS[1]

    for fragment_id in list(shared_fragments._fragments):
        pins.clear()
        _fragment_rerun(at, [fragment_id])
        assert pins, f"the fragment rerun on {page} pinned nothing in its thread"
        threads = {ident for ident, _, _ in pins}
        assert full_thread not in threads and len(threads) == 1, "a fragment-only rerun runs in a thread of its own"
        for ident, values, answered in pins:
            assert values == run_record, {name: (values.get(name), run_record.get(name))
                                          for name in set(values) | set(run_record)
                                          if values.get(name) != run_record.get(name)}
            assert answered == run_record, "the thread answers with what it pinned"


# --- B. Structure -----------------------------------------------------------

def _app_tree():
    return ast.parse(ui_source())


def _function_defs(tree):
    return {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def _mentions_fragment(decorator):
    """Any decorator that names a fragment: st.fragment, streamlit.fragment,
    a bare fragment, a call of one of those, or the app's own."""
    node = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(node, ast.Attribute):
        return "fragment" in node.attr
    if isinstance(node, ast.Name):
        return "fragment" in node.id
    return False


def _fragment_decorated(tree):
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if _mentions_fragment(dec):
                    out[node.name] = dec
    return out


def test_every_fragment_is_declared_with_the_pinning_decorator():
    """The five blocks, and no other function, are fragments; each is
    declared with the bare _pinned_fragment and nothing else that names a
    fragment."""
    decorated = _fragment_decorated(_app_tree())
    assert sorted(decorated) == FRAGMENTS, sorted(decorated)
    for name, dec in decorated.items():
        assert isinstance(dec, ast.Name) and dec.id == "_pinned_fragment", \
            f"{name} is declared with {ast.dump(dec)}, not @_pinned_fragment"


def test_st_fragment_is_used_once_inside_the_pinning_decorator():
    """Every reference to a fragment of Streamlit's -- st.fragment, an
    imported fragment, streamlit.fragment -- stands inside _pinned_fragment,
    and there is exactly one."""
    tree = _app_tree()
    wrapper = _function_defs(tree)["_pinned_fragment"]
    inside = {id(node) for node in ast.walk(wrapper)}
    uses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "fragment":
            uses.append(node)
        elif isinstance(node, ast.Name) and node.id == "fragment":
            uses.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                assert alias.name != "fragment" and alias.asname != "fragment", ast.dump(node)
    assert len(uses) == 1, [f"line {u.lineno}" for u in uses]
    assert id(uses[0]) in inside, f"st.fragment used outside _pinned_fragment at line {uses[0].lineno}"
    use = uses[0]
    assert isinstance(use, ast.Attribute) and isinstance(use.value, ast.Name) and use.value.id == "st"


def _is_call_of(node, dotted):
    """node is a Call of `a.b` (dotted 'a.b') or of a bare name."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if "." in dotted:
        obj, attr = dotted.split(".")
        return isinstance(func, ast.Attribute) and func.attr == attr \
            and isinstance(func.value, ast.Name) and func.value.id == obj
    return isinstance(func, ast.Name) and func.id == dotted


def test_the_pinning_decorator_pins_the_record_before_the_body():
    """_pinned_fragment wraps the body in a function whose first statement
    pins engine.set_readings(**_RUN_READINGS) and whose second returns the
    body's call, and hands that wrapper to st.fragment."""
    wrapper = _function_defs(_app_tree())["_pinned_fragment"]
    inner = [n for n in wrapper.body if isinstance(n, ast.FunctionDef)]
    assert len(inner) == 1, "one inner function, the pinned body"
    body = inner[0].body
    assert len(body) == 2, ast.dump(inner[0])
    first, second = body
    assert isinstance(first, ast.Expr) and _is_call_of(first.value, "engine.set_readings"), ast.dump(first)
    assert not first.value.args and len(first.value.keywords) == 1
    spread = first.value.keywords[0]
    assert spread.arg is None and isinstance(spread.value, ast.Name) and spread.value.id == "_RUN_READINGS", \
        "the pin is **_RUN_READINGS, the run's record, and nothing else"
    assert isinstance(second, ast.Return) and isinstance(second.value, ast.Call) \
        and isinstance(second.value.func, ast.Name) and second.value.func.id == wrapper.args.args[0].arg
    returned = wrapper.body[-1]
    assert isinstance(returned, ast.Return) and _is_call_of(returned.value, "st.fragment")
    assert [a.id for a in returned.value.args if isinstance(a, ast.Name)] == [inner[0].name]


def test_every_pin_in_the_file_goes_through_the_record():
    """engine.set_readings is called in app.py from _pin_readings and from
    the wrapper only, and _pin_readings both pins and records -- so the
    record a fragment re-pins is everything the run pinned, the top-level
    six and SOFTENED_INFORTUNE under chart_ok alike."""
    tree = _app_tree()
    defs = _function_defs(tree)
    allowed = {id(n) for name in ("_pin_readings", "_pinned_fragment") for n in ast.walk(defs[name])}
    sites = [n for n in ast.walk(tree) if _is_call_of(n, "engine.set_readings")]
    assert len(sites) == 2, [f"line {n.lineno}" for n in sites]
    assert all(id(n) in allowed for n in sites), \
        [f"line {n.lineno}" for n in sites if id(n) not in allowed]
    body = defs["_pin_readings"].body
    statements = [n for n in body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    assert len(statements) == 2, ast.dump(defs["_pin_readings"])
    pin, record = statements
    assert _is_call_of(pin.value, "engine.set_readings") and pin.value.keywords[0].arg is None
    assert isinstance(record, ast.Expr) and _is_call_of(record.value, "_RUN_READINGS.update")
    # The two pin sites of the run are _pin_readings calls, and no other
    # function of the file calls it.
    callers = [n for n in ast.walk(tree) if _is_call_of(n, "_pin_readings")]
    assert len(callers) == 2, [f"line {n.lineno}" for n in callers]
    pinned_names = sorted(kw.arg for c in callers for kw in c.keywords)
    assert pinned_names == ["CONNECTION_PROFILE", "DOMAIN_RULE", "EASTERN_RULE", "LOT_HOUSE_CUSP",
                            "MARS_WEST_RAYS_18", "MOON_RAYS_ORB", "SOFTENED_INFORTUNE"]


def _registry_widget_keys(tree):
    """The widget keys and the store keys of READINGS_REGISTRY, read from
    the tuple literal -- so a control keyed straight on a store key (rather
    than drawn through the app's _reading_* helpers on the widget key) is
    caught too."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "READINGS_REGISTRY" for t in node.targets):
            rows = node.value.elts
            keys = {row.elts[1].value for row in rows} | {row.elts[2].value for row in rows}
            assert len(keys) == 2 * len(rows) >= 18
            return keys
    raise LookupError("READINGS_REGISTRY not found")


def test_no_doctrinal_readings_control_stands_inside_a_fragment():
    """The premise of re-pinning the run's record: a doctrinal reading
    cannot move without a full run, because no fragment draws a control
    keyed by a READINGS_REGISTRY widget key. (The fragments' own controls
    are display preferences -- layout, rings, the dark wheel, the Lots,
    rays and twelfth-parts toggles -- none of which an evaluator reads.)"""
    tree = _app_tree()
    keys = _registry_widget_keys(tree)
    defs = _function_defs(tree)
    for name in FRAGMENTS:
        literals = {n.value for n in ast.walk(defs[name]) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert not (literals & keys), f"{name} draws a reading's control: {sorted(literals & keys)}"
