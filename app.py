"""The Streamlit pages: the sidebar, the navigation, and every page a reader
opens, each one a function closing over the engine's top-level names.

The engine itself is engine.py, beside this file, and arrives whole through
the star import below. Run this file, not that one: ``streamlit run app.py``.
"""

import re
import sqlite3
from datetime import datetime, time, timedelta
from math import isfinite
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
import pytz
import streamlit as st
import swisseph as swe
from timezonefinder import TimezoneFinder

import engine
from engine import *

# ==========================================
# 4. STREAMLIT UI INTEGRATION
# ==========================================

_icon_path = Path(__file__).parent / "app_icon.ico"
st.set_page_config(
    page_title="Traditional Astrology Engine",
    page_icon=str(_icon_path) if _icon_path.exists() else None,
    layout="wide",
)

# --- Structure: the course's own order, in three sections -----------------
# Pages follow the syllabus and are grouped in the navigation as the course
# is: Part 1 (the nativity), Part 2 (prediction), and the reference pages.
# Nothing is hidden. The lesson gate that used to hide pages by lesson
# number went on 2026-09-10 (UI_REVIEW_2026-09-10.md §1): the course
# reviews later material early -- the Lesson 5 warm-ups are the planets
# and their places, the Dignities page -- so a filter by lesson number hid
# exactly what the lecture was using, and a page a student is not ready
# for is simply a page not opened. What restrains the pages now is the
# Sources shown reading on the Sources page, which folds the supplement.

# The viewer's theme, read once for the pictures. Streamlit 1.62 reports
# it as st.context.theme.type -- "dark", "light", or None when the browser
# has not said yet (and under AppTest, which has no browser at all). It is
# not by itself what a picture is drawn in: the owner's ruling is that the
# wheels keep their white ground in every theme unless the reader asks
# otherwise, so this is read here and consulted only when the Dark wheel
# preference is on (WHEEL_THEME, below with the other readings).
_context_theme = getattr(st.context, "theme", None)
VIEWER_THEME = getattr(_context_theme, "type", None) if _context_theme is not None else None

# --- The natal wheel, clickable -------------------------------------------
# The Chart page's wheel is mounted as an st.components.v2 component rather
# than shown with st.image, so that a click on a planet or a sign can reach
# Python. The component is registered ONCE, here at the module level: a
# registration wrapped up with its own mounting would re-register the name
# on every instance, which the API warns against. It is mounted inside the
# Chart page's fragment, so a click reruns that fragment and not the page.
#
# What the component is handed is the SVG the app's own renderer produced,
# with every value already escaped at the point it was written (_esc_attr,
# _esc_text). No string from the sidebar, from a saved chart's name or from
# a place label is ever put into the html, css or js below -- those are
# component code, which Streamlit does not sanitise, and they are constants
# written here. User strings reach the component only inside `data`, which
# is data.
#
# The CSS styles the wrapper, the expand control and the hover tooltip and
# NOTHING inside the picture: the wheel carries its own palette, light or
# dark, and a component that recoloured it would be overruling the reader's
# own Dark wheel preference. Styles are isolated in a shadow root
# (isolate_styles defaults to True), so none of this reaches the app.
NATAL_WHEEL_CSS = """
/* The component's own root spans the main area, and an inline-block inside
   it sat at the left edge -- st.image used to do the centring itself, which
   the mount does not inherit. A block with auto margins centres the 560 px
   wheel inside the host, and at Wide, where the width is 100%, the margins
   come to nothing and the picture runs the full width as before. The outer
   st.container(horizontal=True, horizontal_alignment="center") stays where
   it is. overflow is visible so the tooltip is not cut off at the edge. */
.nw-wrap {
    position: relative;
    display: block;
    margin: 0 auto;
    max-width: 100%;
    overflow: visible;
}
.nw-wrap.nw-full {
    position: fixed;
    inset: 0;
    z-index: 2147483000;
    width: 100% !important;
    height: 100%;
    padding: 0.5rem;
    background: var(--st-background-color, #ffffff);
    display: flex;
    align-items: center;
    justify-content: center;
}
.nw-svg { line-height: 0; }
.nw-full .nw-svg {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.nw-full .nw-svg svg {
    width: auto !important;
    height: 100% !important;
    max-width: 100%;
}
.nw-svg [data-point], .nw-svg [data-sign] { cursor: pointer; }
.nw-expand {
    position: absolute;
    top: 0.35rem;
    right: 0.35rem;
    z-index: 1;
    border: 1px solid var(--st-border-color, rgba(49, 51, 63, 0.2));
    border-radius: 0.35rem;
    background: var(--st-secondary-background-color, rgba(240, 242, 246, 0.9));
    color: var(--st-text-color, inherit);
    font: inherit;
    font-size: 0.9rem;
    line-height: 1;
    padding: 0.25rem 0.4rem;
    cursor: pointer;
    opacity: 0.55;
}
.nw-expand:hover { opacity: 1; }
/* The tooltip is placed against the VIEWPORT, not against the wrapper: at
   the right-hand side of the wheel a tooltip bounded by the wrapper had
   nowhere to go and wrapped itself into a column one word wide. Fixed
   position, one fixed width so the text breaks in the same place wherever
   it is raised, and the frontend flips it to the left of the pointer, or
   above it, when it would otherwise run off the screen. */
.nw-tip {
    position: fixed;
    z-index: 2147483001;
    width: 22rem;
    max-width: calc(100vw - 2rem);
    white-space: pre-line;
    pointer-events: none;
    padding: 0.3rem 0.45rem;
    border: 1px solid var(--st-border-color, rgba(49, 51, 63, 0.2));
    border-radius: 0.35rem;
    background: var(--st-secondary-background-color, rgba(240, 242, 246, 0.97));
    color: var(--st-text-color, inherit);
    font: inherit;
    font-size: 0.78rem;
    line-height: 1.35;
}
"""

# The frontend: one child div under the component's own root (the API's own
# warning -- writing innerHTML on the root itself would overwrite the CSS
# and HTML the component was registered with), the SVG dropped into it, a
# click listener on every [data-point] and every [data-sign], a tooltip fed
# from the envelope's own text, and an expand control the Escape key also
# closes. The listener set is rebuilt from scratch on every rerun because
# the SVG is replaced whole; the keydown listener is not, so the cleanup
# function returned at the end takes it off again when Streamlit unmounts.
NATAL_WHEEL_JS = """
export default function (component) {
    const { data, parentElement, setTriggerValue } = component;
    let wrap = parentElement.querySelector(".nw-wrap");
    if (!wrap) {
        wrap = document.createElement("div");
        wrap.className = "nw-wrap";
        const holder = document.createElement("div");
        holder.className = "nw-svg";
        const tip = document.createElement("div");
        tip.className = "nw-tip";
        tip.hidden = true;
        const expand = document.createElement("button");
        expand.type = "button";
        expand.className = "nw-expand";
        expand.title = "Expand the wheel (Escape closes it)";
        expand.textContent = "\\u2921";
        expand.onclick = () => { wrap.classList.toggle("nw-full"); };
        wrap.appendChild(holder);
        wrap.appendChild(tip);
        wrap.appendChild(expand);
        parentElement.appendChild(wrap);
    }
    const holder = wrap.querySelector(".nw-svg");
    const tip = wrap.querySelector(".nw-tip");
    const signs = (data && data.signs) || [];
    holder.innerHTML = (data && data.svg) || "";
    const svg = holder.querySelector("svg");
    if (svg) {
        svg.removeAttribute("width");
        svg.removeAttribute("height");
        svg.style.height = "auto";
        if (data.width === "stretch") {
            svg.style.width = "100%";
            wrap.style.width = "100%";
        } else {
            svg.style.width = data.width + "px";
            wrap.style.width = data.width + "px";
            wrap.style.maxWidth = "100%";
        }
    }
    holder.querySelectorAll("[data-point]").forEach((element) => {
        element.addEventListener("click", () => {
            setTriggerValue("picked", "planet:" + element.getAttribute("data-point"));
        });
    });
    holder.querySelectorAll("[data-sign]").forEach((element) => {
        const index = element.getAttribute("data-sign");
        element.addEventListener("click", () => {
            setTriggerValue("picked", "sign:" + index);
        });
        element.addEventListener("pointermove", (event) => {
            const text = signs[Number(index)];
            if (!text) { return; }
            tip.textContent = text;
            tip.hidden = false;
            // Placed in viewport coordinates, and flipped to the other side
            // of the pointer when it would otherwise run off the screen --
            // which is what the right-hand signs did before.
            const gap = 14;
            const box = tip.getBoundingClientRect();
            let left = event.clientX + gap;
            let top = event.clientY + gap;
            if (left + box.width + gap > window.innerWidth) {
                left = Math.max(gap, event.clientX - gap - box.width);
            }
            if (top + box.height + gap > window.innerHeight) {
                top = Math.max(gap, event.clientY - gap - box.height);
            }
            tip.style.left = left + "px";
            tip.style.top = top + "px";
        });
        element.addEventListener("mouseleave", () => { tip.hidden = true; });
    });
    const onKey = (event) => {
        if (event.key === "Escape") { wrap.classList.remove("nw-full"); }
    };
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("keydown", onKey); };
}
"""

NATAL_WHEEL = st.components.v2.component("natal_wheel", css=NATAL_WHEEL_CSS, js=NATAL_WHEEL_JS)

st.sidebar.header("Nativity")

if "saved_charts" not in st.session_state:
    st.session_state["saved_charts"] = load_saved_charts()
    # F04 of the review of 2026-09-16: a store that cannot be read is copied
    # beside itself by the loader before anything writes over it, and the
    # copy's name is left in engine.LAST_STORE_ERROR. Held here so the
    # sidebar can say so once, below, in the session that read it.
    if engine.LAST_STORE_ERROR:
        st.session_state["_store_error_notice"] = engine.LAST_STORE_ERROR

# Preferences: read once per session into the store keys that nothing has
# set yet (a test's seeded session_state wins), written back through
# _remember() whenever _persist() moves a reading, so the file is the
# stores' shadow and never a second source of truth.
if "_prefs" not in st.session_state:
    st.session_state["_prefs"] = load_preferences()
    for _key, _value in st.session_state["_prefs"].items():
        if _key in PREFERENCE_KEYS and _key not in st.session_state:
            st.session_state[_key] = _value

def _remember(key, value):
    """Keep `key` = `value` in the preferences file, if it is a preference
    and it changed."""
    prefs = st.session_state["_prefs"]
    if (key in PREFERENCE_KEYS or key == 'last_chart') and prefs.get(key) != value:
        prefs[key] = value
        write_preferences(prefs)

def _forget(key):
    prefs = st.session_state["_prefs"]
    if key in prefs:
        del prefs[key]
        write_preferences(prefs)

# The example nativity this app opens on -- Florence, 1240-05-23, 14:30 LMT
# -- as the sidebar's own widgets default to it, in one place so that the
# boxes and the reset below cannot come to disagree.
EXAMPLE_CHART = {
    "date_input_key": "1240-05-23",
    "time_input_key": time(14, 30),
    "time_standard_key": TIME_STANDARD_OPTIONS[0],
    "utc_offset_key": 0.0,
    "manual_coords_key": False,
    "location_input_key": "Florence",
    "manual_lat_key": 43.7698,
    "manual_lon_key": 11.2556,
}

# The picker's first option, which is not a chart but the act of starting
# one. M3 of the hostile pass of 2026-09-16: a chart could be SAVED under
# this very string, after which the picker listed it twice and the record
# could be neither selected nor deleted -- the option that means "new
# chart" cannot also mean "that chart". Named here so that the save can
# refuse it.
NEW_CHART_SENTINEL = "-- New Chart --"


def _is_reserved_name(name):
    """Whether a chart name would collide with the picker's own first
    option. Case and spacing do not save it: '--new chart--' and
    '-- NEW CHART --' read as the same option in the list."""
    def _flat(text):
        return re.sub(r"\s+", "", str(text)).casefold()
    return _flat(name) == _flat(NEW_CHART_SENTINEL)


# The keys a new chart drops rather than sets: the target of the Timing page
# (widget and store alike, so the page's own setdefault seeds them afresh),
# the label a loaded chart put on its coordinates, the legacy-record flag,
# and the last date that parsed.
_NEW_CHART_DROPS = ("target_date", "_target_date", "target_age", "_target_age",
                    "_target_last_good", "loaded_location",
                    "_loaded_without_standard", "_date_last_good",
                    # what the last record loaded said about itself (H3, H5):
                    # a new chart is not that record
                    "_record_notice")


def _new_chart_form():
    """Put the example nativity back in the sidebar's boxes. Selecting
    '-- New Chart --' is a NEW CHART, not a deselection: the review found it
    keeping the edited date and place of the record just left, so that the
    next save wrote one chart under another chart's name (F04).

    The form only. The preferences file is not touched and 'last_chart' is
    not forgotten, so the next launch still opens on the last chart saved or
    loaded -- the reading taken of a new chart being an unsaved draft, which
    has nothing to be opened on."""
    for key, value in EXAMPLE_CHART.items():
        st.session_state[key] = value
    for key in ("target_mode", "_target_mode"):
        st.session_state[key] = TARGET_MODE_OPTIONS[0]
    for key in _NEW_CHART_DROPS:
        st.session_state.pop(key, None)


def _apply_selected_chart():
    """on_change callback: runs before the script reruns, so writing into
    these session_state keys here makes the widgets below pick up the
    loaded values on this same rerun. The chart loaded becomes the one the
    app opens on next time (preference 'last_chart', 2026-09-10)."""
    name = st.session_state.get("chart_picker")
    if name and name != NEW_CHART_SENTINEL:
        # A record the sidebar cannot load is not the chart the app opens
        # on next time either: the fields have not moved, and nothing has
        # been loaded to remember.
        if _restore_chart(name):
            _remember('last_chart', name)
    else:
        _new_chart_form()

def _restore_chart(name):
    """Write a saved chart's fields into the sidebar widgets' keys. True
    when the record was loaded, False when it was refused.

    H3 of the hostile pass of 2026-09-16: the fields were written into the
    widget keys unread, so a record whose fields are the wrong TYPE -- an
    int time_string, a str latitude, an "abc" target_age, from a hand-edit
    or an import -- raised where the value was consumed and took the whole
    script down: on the selection, and at launch when it was the last
    chart, which made the app dead-on-open. The record is read first
    (chart_record_fault, engine): a fault leaves every widget exactly as it
    was, leaves the record in the file untouched, and leaves one sentence
    in _record_notice for the sidebar to show beside the picker."""
    entry = st.session_state["saved_charts"].get(name, {})
    fault = chart_record_fault(entry)
    if fault is not None:
        field, expected = fault
        st.session_state["_record_notice"] = (
            f"'{name}' could not be loaded: its {field} is not a {expected}.")
        return False
    st.session_state.pop("_record_notice", None)
    if True:
        if "date_string" in entry:
            st.session_state["date_input_key"] = entry["date_string"]
        if "time_string" in entry:
            try:
                h, m, s = (int(x) for x in entry["time_string"].split(":"))
                st.session_state["time_input_key"] = time(h, m, s)
            except (ValueError, KeyError):
                pass
        # The time standard (2026-09-10). An entry saved before it was
        # stored is flagged rather than silently cast at LMT: the owner's
        # reference nativity, recorded EST, loaded forty minutes wrong.
        if entry.get("time_standard") in TIME_STANDARD_OPTIONS:
            st.session_state["time_standard_key"] = entry["time_standard"]
            st.session_state.pop("_loaded_without_standard", None)
        else:
            st.session_state["_loaded_without_standard"] = name
        # H5: an offset outside +-14 is NOT written to the widget. Streamlit
        # pulls a seeded value out of a number_input's bounds to a bound --
        # and to the wrong one: a stored 99 came back as -14, and the chart
        # was cast at UTC-14:00 with nothing said, while a re-save wrote the
        # clamp into the record. The record keeps its 99, the box keeps the
        # offset a chart is cast at by default, the sidebar says what was
        # stored, and the strip reads (modified) because the two differ --
        # which is the truth of it.
        if entry.get("utc_offset") is not None:
            if utc_offset_in_range(entry["utc_offset"]):
                st.session_state["utc_offset_key"] = record_number(entry["utc_offset"])
            else:
                st.session_state["utc_offset_key"] = EXAMPLE_CHART["utc_offset_key"]
                st.session_state["_record_notice"] = (
                    f"'{name}' was saved with a UTC offset of {entry['utc_offset']}, "
                    "outside ±14; check the time standard.")
        # The target of the Timing page, both the store the engine reads
        # and the page widgets, so the page shows what was loaded.
        if entry.get("target_mode") in TARGET_MODE_OPTIONS:
            for key in ("target_mode", "_target_mode"):
                st.session_state[key] = entry["target_mode"]
            if entry.get("target_date"):
                for key in ("target_date", "_target_date"):
                    st.session_state[key] = entry["target_date"]
            if entry.get("target_age") is not None:
                for key in ("target_age", "_target_age"):
                    st.session_state[key] = int(record_number(entry["target_age"]))
        if entry.get("lat") is not None and entry.get("lon") is not None:
            # Restore via Manual Coordinate Entry, using the saved lat/lon
            # directly, rather than re-running a City Search text query --
            # which would receive the already-resolved display label (e.g.
            # "Petoskey, MI (US)") as its search term and reliably match
            # nothing, since city names in atlas.db don't include the
            # ", State (Country)" suffix. This also correctly restores
            # charts that were originally entered via Manual Coordinate
            # Entry in the first place, which a location_query of
            # "Manual [lat, lon]" could never do by re-searching either.
            # As NUMBERS: a record can hold a coordinate written as text
            # ('43.7792'), which the comparison already reads as that
            # coordinate, and a string in a number_input's key raised
            # where the widget compared it with its own bounds (H3).
            _lat, _lon = record_number(entry["lat"]), record_number(entry["lon"])
            st.session_state["manual_coords_key"] = True
            st.session_state["manual_lat_key"] = _lat
            st.session_state["manual_lon_key"] = _lon
            st.session_state["loaded_location"] = {
                "lat": _lat,
                "lon": _lon,
                "label": entry.get("location_query", ""),
            }
        elif "location_query" in entry:
            # Saved before lat/lon capture was added -- best effort only,
            # since atlas.db matching needs a raw city name, not the old
            # free-text/resolved-label value this field used to hold.
            st.session_state["manual_coords_key"] = False
            st.session_state["location_input_key"] = entry["location_query"]
    return True

chart_options = [NEW_CHART_SENTINEL] + sorted(st.session_state["saved_charts"].keys())
# The app opens on the chart it was last working on (owner's decision
# 2026-09-10), unless something has already seeded the sidebar -- the
# harness does, and a fresh session has not.
LAUNCH_COUNT = 0          # bound every run; the count is set just below, once per session
if "_autoload_done" not in st.session_state:
    st.session_state["_autoload_done"] = True
    # One launch, counted once: this block runs exactly once per session.
    # The count includes the launch in hand, and it is what decides whether
    # the Chart page's introduction stands open or folded -- three
    # paragraphs that are read once and then in the way. A count already in
    # the session that the file did not put there is a test's, and is left
    # as it stands, which is the same rule the preferences read above
    # follows: a seeded session_state wins.
    if '_launches' not in st.session_state or '_launches' in st.session_state["_prefs"]:
        st.session_state["_launches"] = int(st.session_state["_prefs"].get('_launches', 0) or 0) + 1
        _remember('_launches', st.session_state["_launches"])
    _last = st.session_state["_prefs"].get('last_chart')
    if _last in st.session_state["saved_charts"] and "date_input_key" not in st.session_state:
        # H3: the launch survives a last chart it cannot load -- the app
        # opens on no chart at all, with the sentence beside the picker,
        # where it used to open on a traceback and nothing else. The picker
        # is only pointed at the record when the record was loaded, so that
        # it never names a chart the boxes do not hold.
        if _restore_chart(_last):
            st.session_state["chart_picker"] = _last
# Read at the top level on every run, as every other reading is, so that a
# fragment rerun and a page change see the same number the launch set.
LAUNCH_COUNT = int(st.session_state.get("_launches", 0) or 0)
# A selection the script makes rather than the reader -- the record just
# saved, the picker after a delete -- is left here by the run that makes it
# and applied by the next one, because a widget's key cannot be assigned
# once the widget has been drawn (F04, item 1: the picker's options were
# built before the Save button ran, so a save reported success while the
# picker and the strip still said the chart was unsaved). The picker's
# on_change does not fire for a selection made this way, which is right:
# the fields already hold the values that were just written.
_selection = st.session_state.pop("_select_after_rerun", None)
if _selection is not None:
    st.session_state["chart_picker"] = _selection

# Said once, in the session whose load found the store unreadable (F04,
# item 6). The bytes are beside the file under the name this names; the
# store this session writes is a fresh one.
_saved_flash = st.session_state.pop("_saved_flash", None)
if _saved_flash:
    st.sidebar.success(f"Saved '{_saved_flash}'.")

_store_error = st.session_state.pop("_store_error_notice", None)
if _store_error:
    st.sidebar.error("Saved charts could not be read. The original file was "
                     f"kept as {_store_error}.")

# What a record said about itself when it was loaded, or refused to be: the
# fields the sidebar could not read (H3), or an offset outside the bounds a
# chart can be cast at (H5). It stands beside the picker for as long as
# that record is the one in hand -- until another is loaded, a new chart is
# begun, or one is saved -- because it describes the record, not the click.
_record_notice = st.session_state.get("_record_notice")
if _record_notice:
    st.sidebar.warning(_record_notice)

load_col, del_col = st.sidebar.columns([3, 1])
load_col.selectbox("\U0001F4C2 Load saved chart", chart_options, key="chart_picker", on_change=_apply_selected_chart)
# Filled once the sidebar's validation has run, when the fields have moved
# away from the record the picker names.
picker_note = st.sidebar.empty()
if del_col.button("\U0001F5D1", help="Delete the selected saved chart"):
    picked = st.session_state.get("chart_picker")
    if picked and picked != "-- New Chart --" and picked in st.session_state["saved_charts"]:
        # The bin asks first (F04, item 5): it used to delete the record on
        # the press, with no confirmation and nothing to undo it with.
        st.session_state["_delete_pending"] = picked
        st.session_state.pop("_replace_pending", None)
        st.session_state.pop("_replace_pending_record", None)

# The question stands here, beside the bin that asked it, in a placeholder
# of its own so that answering it can clear it without a rerun. A rerun from
# this height of the sidebar is not available: it abandons the run before
# the date, time and place widgets are drawn, and Streamlit discards the
# state of a widget a run did not draw -- the boxes came back holding the
# example nativity (seen in the browser, 2026-09-16). So Keep clears the
# placeholder, and Delete leaves the writing to the foot of the sidebar,
# where every field has been drawn and a rerun costs nothing.
delete_box = st.sidebar.empty()
_delete_pending = st.session_state.get("_delete_pending")
if _delete_pending and _delete_pending not in st.session_state["saved_charts"]:
    st.session_state.pop("_delete_pending", None)
    _delete_pending = None
if _delete_pending:
    with delete_box.container():
        st.warning(f"Delete '{_delete_pending}'?")
        _delete_col, _keep_col = st.columns(2)
        _delete_clicked = _delete_col.button("Delete", key="_delete_confirm")
        _keep_clicked = _keep_col.button("Keep", key="_delete_keep")
    if _keep_clicked:
        st.session_state.pop("_delete_pending", None)
        delete_box.empty()
    elif _delete_clicked:
        st.session_state["_delete_now"] = _delete_pending
        delete_box.empty()

# --- Configurable readings: read here, set on the pages ------------------
# The Connection rule and the five readings the sources leave open are set
# by controls on the page and table each one affects (Configurations, Chart,
# Dignities, Lots), and remembered across navigation in a store key that
# _persist() keeps up to date. They are READ here, at the top level, because
# the engine functions below run before any page function does and read
# these globals at call time. The widget key is preferred when present: on
# the rerun a change triggers, the widget already carries the new value
# while the store still holds the old one. The target of the Timing page
# (2026-09-10) is read the same way, further down.
def _reading(widget_key, store_key, default):
    return st.session_state.get(widget_key, st.session_state.get(store_key, default))

# The date is typed, not picked (UI evaluation 2026-09-10, A.1): a calendar
# popup is the wrong control for 1240, and the harness sets this key as a
# string. A malformed date no longer stops the script -- which took the
# page list with it -- but keeps the last good date and says so.
# Seeded through session state rather than a default argument: a loaded
# chart writes these keys before the widgets run, and Streamlit warns when a
# widget has both a default and a seeded key (the konsole warning of
# 2026-09-15). The same for every key _restore_chart writes.
st.session_state.setdefault("date_input_key", EXAMPLE_CHART["date_input_key"])
date_string = st.sidebar.text_input(
    "Date (YYYY-MM-DD)", key="date_input_key",
    help="The civil date of birth. Before 1582-10-15 the digits are read as a JULIAN-calendar date, "
         "as Solar Fire and astro.com read them; from that day on, Gregorian. Years before 1000 "
         "are typed with their leading zeros (0787-08-10).")
# date_string is the DRAFT -- the characters in the box. input_date is the
# COMMITTED date: the draft when it parses, the last one that did when it
# does not. F01 of the review of 2026-09-16: everything downstream reads the
# committed date and nothing reads the draft, so the strip, the chart and a
# saved record cannot describe three different nativities.
_parsed = parse_iso_date(date_string)
date_is_valid = _parsed is not None
if _parsed is None:
    input_date = st.session_state.get("_date_last_good", CivilDate(1240, 5, 23))
    st.sidebar.error(f"Date must be YYYY-MM-DD, e.g. 1240-05-23. Showing {input_date:%Y-%m-%d}.")
else:
    input_date = _parsed
    st.session_state["_date_last_good"] = input_date
_cal_note = ("Julian calendar (before the reform of 1582-10-15)"
             if (input_date.year, input_date.month, input_date.day) < (1582, 10, 15) else "Gregorian calendar")

# --- What the ephemeris can reach ----------------------------------------
# H1/H2 of the hostile pass of 2026-09-16. The date box takes any year from
# 1 to 9999 and a chart was cast from it without asking whether the
# ephemeris shipped with this app has a position for it: outside its span
# swe.calc_ut RAISES, and the calculation runs at module level, above
# st.navigation(...).run(), so a reachable-looking date took the whole
# shell down -- no page, no recovery panel, an inert navigation bar.
#
# The span the built-in (Moshier) ephemeris answers to, measured rather
# than assumed: swe.calc_ut is answered from Julian Day 625000.5
# (swe.revjul: -3001 February, i.e. 3002 BC) up to but not including
# 2818000.5 (3003 April).
EPHEMERIS_JD_MIN = 625000.5
EPHEMERIS_JD_MAX = 2818000.5
# A chart is never one position: every date this app is given is SEARCHED
# forward from, and the search must land inside the ephemeris too. The
# furthest of them, measured: the Timing page's fifteenth indicator
# simulates the revolution's lord forward for as long as Saturn takes to
# leave a sign -- 900 days past the revolution of the year (the horizons in
# pn4_further_indicators) -- and the natal page's gestation Moons reach
# about 380 past the birth. So a usable date is one with a search's room
# left above it, which is what a date inside the RAW span need not have: a
# birth in 3002 is answered by swe.calc_ut and then raises in the gestation
# search.
EPHEMERIS_SEARCH_DAYS = 950.0
# The app's own last moment: the end of 3000 AD, which is what the sidebar
# states, or the last moment with a search's room above it, whichever comes
# first. It is the second, by some four months -- the sentence names the
# round span, as a limit stated to a reader should be, and the refusal
# falls just inside it rather than just outside.
EPHEMERIS_JD_LAST = min(civil_to_jd(3001, 1, 1, 0.0),
                        EPHEMERIS_JD_MAX - EPHEMERIS_SEARCH_DAYS)
EPHEMERIS_DATE_MESSAGE = ("This app's ephemeris covers 3000 BC to 3000 AD; "
                          "the date is outside it.")
EPHEMERIS_LAST_YEAR = 3000


def jd_in_ephemeris(jd):
    """Whether a Julian Day is one this app can compute a chart for, with
    room left over for the searches that run forward from it."""
    try:
        jd = float(jd)
    except (TypeError, ValueError):
        return False
    return EPHEMERIS_JD_MIN <= jd < EPHEMERIS_JD_LAST


def date_in_ephemeris(date):
    """The same question of a civil DATE, asked at noon: the offset can move
    a moment by at most 14 hours and the limit is a whole year inside the
    ephemeris, so the hour cannot decide this."""
    return jd_in_ephemeris(civil_to_jd(date.year, date.month, date.day, 12.0))


def max_target_age(birth_date):
    """The greatest age whose birthday this app can still analyse -- the
    Age box's own upper bound, so that the limit cannot be crossed by
    counting years instead of typing a date. Counted down from the last
    year covered, because the limit falls inside that year and a birthday
    late in it is past the limit while an earlier one is not."""
    age = EPHEMERIS_LAST_YEAR - int(birth_date.year)
    while age > 0 and not date_in_ephemeris(pn4_birthday(birth_date, age)):
        age -= 1
    return max(0, age)

# To the second: the engine reads seconds, and a rectified time has them.
st.session_state.setdefault("time_input_key", EXAMPLE_CHART["time_input_key"])
input_time = st.sidebar.time_input("Time", key="time_input_key", step=timedelta(seconds=1))

# The time standard gets a key, so it is saved with the chart (F1 of the
# 2026-09-10 evaluation: the saved reference nativity, recorded EST, was
# loading at LMT, forty minutes wrong). The resolved offset is shown in the
# box directly under it, before the chart is cast, not at the sidebar's foot.
time_standard = st.sidebar.selectbox(
    "Time standard", TIME_STANDARD_OPTIONS, key="time_standard_key",
    help="LMT (local mean time) for charts before standard time was adopted (late 19th century): the "
         "offset is the longitude at 4 minutes a degree. Standard time: the named zone at the "
         "birthplace, with daylight saving as the zone's own history records it. Manual: type the "
         "offset the birth record states, east positive (EST is -5, CDT is -5, IST is +5.5).")
utc_offset_manual = None
if time_standard == TIME_STANDARD_OPTIONS[2]:
    st.session_state.setdefault("utc_offset_key", EXAMPLE_CHART["utc_offset_key"])
    utc_offset_manual = st.sidebar.number_input(
        "UTC offset (hours, east positive)", min_value=-14.0, max_value=14.0, step=0.25,
        format="%.2f", key="utc_offset_key")
time_standard_box = st.sidebar.empty()
time_standard_box.caption(_cal_note)
if st.session_state.get("_loaded_without_standard"):
    st.sidebar.warning(f"'{st.session_state['_loaded_without_standard']}' was saved before the time "
                       "standard was stored with a chart. Check it, then save the chart again.")

st.sidebar.header("Birthplace")

COORDINATE_RANGE_MESSAGE = ("Latitude must be between -90 and 90 and longitude "
                            "between -180 and 180.")


def coordinates_in_range(lat, lon):
    """A pair the engine can be asked about at all: both finite, latitude
    within [-90, 90] and longitude within [-180, 180]. Polar is valid."""
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return False
    if not (isfinite(lat) and isfinite(lon)):
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0

# One control in effect (evaluation A.3): the search box also accepts a
# typed "latitude, longitude" pair; the toggle exposes the coordinate
# fields themselves, which is also how a saved chart is restored (the
# loader writes these three keys, as the harness does).
def _manual_coords_switched():
    """on_change: switching the coordinate fields ON starts them at the
    place that is resolved now, not at the Florence constants (F02 of the
    review of 2026-09-16: the toggle reads as a change of input method and
    was acting as a change of location). A callback runs BEFORE the widgets
    of the rerun it triggers, so writing their keys here is what the loader
    of a saved chart already does. Nothing resolved yet: the constants
    stand as the fields' default."""
    if not st.session_state.get("manual_coords_key"):
        return
    resolved_lat = st.session_state.get("_resolved_lat")
    resolved_lon = st.session_state.get("_resolved_lon")
    if resolved_lat is not None and resolved_lon is not None:
        st.session_state["manual_lat_key"] = float(resolved_lat)
        st.session_state["manual_lon_key"] = float(resolved_lon)


manual_coords = st.sidebar.toggle("Enter coordinates directly", key="manual_coords_key",
                                  on_change=_manual_coords_switched,
                                  help="Or type them into the search box as 'latitude, longitude'.")

# The reason a place cannot be read, in the words the sidebar already used;
# it becomes chart_error below, which the recovery panel prints.
location_error = None
if manual_coords:
    st.session_state.setdefault("manual_lat_key", EXAMPLE_CHART["manual_lat_key"])
    st.session_state.setdefault("manual_lon_key", EXAMPLE_CHART["manual_lon_key"])
    # What the fields hold BEFORE the widgets clamp them to their own
    # min/max: an impossible latitude seeded into the key (the review's own
    # reproduction, E03) is refused below rather than silently pulled to
    # the pole.
    _draft_lat = st.session_state.get("manual_lat_key")
    _draft_lon = st.session_state.get("manual_lon_key")
    lat = st.sidebar.number_input("Latitude", min_value=-90.0, max_value=90.0,
                                  format="%.4f", key="manual_lat_key")
    lon = st.sidebar.number_input("Longitude", min_value=-180.0, max_value=180.0,
                                  format="%.4f", key="manual_lon_key")
    if not coordinates_in_range(_draft_lat, _draft_lon):
        lat, lon = _draft_lat, _draft_lon
    # If these coordinates came from loading a saved chart and haven't been
    # hand-edited since, show the friendly place name it was saved under
    # instead of a bare coordinate pair.
    loaded_location = st.session_state.get("loaded_location")
    if (
        loaded_location
        and loaded_location.get("label")
        and loaded_location["lat"] == lat
        and loaded_location["lon"] == lon
    ):
        location_query = loaded_location["label"]
    else:
        location_query = f"Manual [{lat:.4f}, {lon:.4f}]"
else:
    st.session_state.setdefault('location_input_key', EXAMPLE_CHART['location_input_key'])
    city_search = st.sidebar.text_input("City, or latitude, longitude", key="location_input_key",
                                        placeholder="Florence  |  45.3733, -84.9553")
    _typed = parse_lat_lon(city_search) if city_search else None
    if _typed:
        lat, lon = _typed
        location_query = f"Manual [{lat:.4f}, {lon:.4f}]"
    elif city_search:
        db_path = Path(__file__).parent / "atlas.db"
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, admin1, country, lat, lon
                    FROM cities
                    WHERE name LIKE ? COLLATE NOCASE OR ascii_name LIKE ? COLLATE NOCASE
                    ORDER BY population DESC
                    LIMIT 20
                """, (city_search + '%', city_search + '%'))
                matches = cursor.fetchall()

            if matches:
                options = {}
                for m in matches:
                    # Format: City, State/Admin (Country Code)
                    label = f"{m[0]}, {m[1]} ({m[2]})"
                    # Deduplicate identical names in the same region
                    if label in options:
                        label += f" [{m[3]:.4f}, {m[4]:.4f}]"
                    options[label] = (m[3], m[4])

                selected_label = st.sidebar.selectbox("Select specific location:", list(options.keys()))
                lat, lon = options[selected_label]
                location_query = selected_label
            else:
                location_error = "No matches found in offline atlas."
                st.sidebar.warning(location_error)
                lat, lon, location_query = None, None, None
        else:
            location_error = "`atlas.db` not found. Please ensure it is in the root directory."
            st.sidebar.error(location_error)
            lat, lon, location_query = None, None, None
    else:
        location_error = "No place is resolved."
        lat, lon, location_query = None, None, None
location_box = st.sidebar.empty()

# --- One validation of the coordinates, before any time standard ----------
# F02: the named-zone branch used to be the only thing that refused an
# impossible latitude, so the same 91 gave tables under a manual offset and
# an uncaught exception under a named zone. The pair is checked once, here,
# for the fields and for a "latitude, longitude" typed into the search box
# alike; a valid polar latitude passes (the engine refuses for itself what
# it cannot compute there).
chart_ok = True
chart_error = None
if lat is None or lon is None or not location_query:
    chart_ok = False
    chart_error = location_error or "No place is resolved."
elif not coordinates_in_range(lat, lon):
    chart_ok = False
    chart_error = COORDINATE_RANGE_MESSAGE
    st.sidebar.error(COORDINATE_RANGE_MESSAGE)
else:
    # The place now resolved, for the coordinate fields to start from when
    # they are switched on (F02a).
    st.session_state["_resolved_lat"] = float(lat)
    st.session_state["_resolved_lon"] = float(lon)

# --- The target of the Timing page: an age or a date -----------------------
# Set on the Timing page, where it is used (the owner's instinct, 2026-09-10),
# and remembered in store keys like the readings; read here because the
# bundle below is computed before the page runs. "Age 42" is the 42nd
# birthday; a date shows its completed years beside it on the page. Saved
# with the chart.
_today = CivilDate.of(datetime.now().date())
target_mode = _reading("target_mode", "_target_mode", TARGET_MODE_OPTIONS[0])
# F17 of the review of 2026-09-16: an unparseable target used to fall to
# today, which silently analysed a different period from the one asked for.
# It keeps the last target that did parse instead -- the same rule the birth
# date follows -- and only a session that has never had one falls to today.
st.session_state.setdefault("_target_last_good", _today.isoformat())
# H2 of the hostile pass of 2026-09-16: a target the ephemeris cannot reach
# -- typed as a date, or counted as an age, the Age box having had no upper
# bound at all -- raised inside the timing bundle at module level and took
# the shell with it. A target out of reach is treated exactly as a target
# that will not parse (F17): the last valid one stands, and the Timing page
# says so in the target's own row. `target_range_note` is that sentence, or
# None; it is read by the page, which is where the target is set.
_target_parsed = parse_iso_date(_reading("target_date", "_target_date", _today.isoformat()))
_target_reachable = _target_parsed is not None and date_in_ephemeris(_target_parsed)
if _target_reachable:
    st.session_state["_target_last_good"] = _target_parsed.isoformat()
_target_kept = parse_iso_date(st.session_state["_target_last_good"]) or _today
_date_target = _target_parsed if _target_reachable else _target_kept
target_out_of_reach = False
if target_mode == TARGET_MODE_OPTIONS[1]:
    _asked_age = max(0, int(_reading("target_age", "_target_age", pn4_completed_years(input_date, _date_target))))
    _asked_date = pn4_birthday(input_date, _asked_age)
    if date_in_ephemeris(_asked_date):
        target_age, target_date = _asked_age, _asked_date
        st.session_state["_target_last_good"] = target_date.isoformat()
    else:
        target_out_of_reach = True
        target_date = _target_kept
        target_age = pn4_completed_years(input_date, target_date)
        st.session_state["_target_age"] = target_age
    # The other reading follows, so switching the mode carries the target over.
    st.session_state["_target_date"] = target_date.isoformat()
else:
    target_out_of_reach = _target_parsed is not None and not _target_reachable
    target_date = _date_target
    target_age = pn4_completed_years(input_date, target_date)
    st.session_state["_target_age"] = target_age
target_range_note = (f"The target is beyond this app's ephemeris ({EPHEMERIS_LAST_YEAR} AD); "
                     f"keeping {target_date:%Y-%m-%d}." if target_out_of_reach else None)

def _chart_record():
    """The committed input as a record: the fields Save writes, and the
    fields a saved record is compared with to see whether the nativity in
    the sidebar is still the one that was saved."""
    return {
        "date_string": input_date.isoformat(),
        "time_string": input_time.strftime("%H:%M:%S"),
        "time_standard": time_standard,
        "utc_offset": utc_offset_manual,
        "location_query": location_query,
        "lat": lat,
        "lon": lon,
        "target_mode": target_mode,
        "target_date": target_date.isoformat(),
        "target_age": target_age,
    }


def _records_match(stored, record):
    """Whether a stored record describes the nativity `record` describes.

    The stored record's OWN fields are what is compared: a field it does not
    carry cannot have been edited since it was saved, so a record written
    before the time standard or the target was stored with a chart is not
    called modified for lacking them. Numbers are compared as floats to four
    decimals -- the coordinates are written to four places and JSON reads a
    whole number back as an int."""
    if not isinstance(stored, dict):
        return False
    for field, value in record.items():
        if field not in stored:
            continue
        other = stored[field]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                if round(float(other), 4) != round(float(value), 4):
                    return False
            except (TypeError, ValueError):
                return False
        elif other != value:
            return False
    return True


def _store_chart(name, record):
    """Write the record under `name` and, only if the disk took it, let the
    session's mapping, the preferences and the picker follow (F04, item 7:
    the mapping used to be mutated first, so a failed write left the session
    holding a record the file did not have). True when it was written."""
    charts = dict(st.session_state["saved_charts"])
    charts[name] = record
    if not write_saved_charts(charts):
        st.sidebar.error("Could not write saved_charts.json to disk.")
        return False
    st.session_state["saved_charts"] = charts
    st.session_state.pop("_loaded_without_standard", None)
    # The record under this name is now the one the boxes hold, whatever it
    # was before: an offset outside the bounds (H5) has just been written
    # over with the one the box holds, so the sentence that reported it is
    # no longer true of the record.
    st.session_state.pop("_record_notice", None)
    _remember('last_chart', name)
    st.session_state["_select_after_rerun"] = name
    # The success message is carried over the rerun the caller asks for,
    # so that the reader still sees it beside the picker that now names
    # the record.
    st.session_state["_saved_flash"] = name
    return True


def _free_name(name):
    """The first free '<name> (n)', counting from 2."""
    n = 2
    while f"{name} ({n})" in st.session_state["saved_charts"]:
        n += 1
    return f"{name} ({n})"


# The nativity as it stands, or None when there is nothing to save: the
# record Save writes, and the record the picker's own is compared with.
input_record = _chart_record() if (chart_ok and date_is_valid) else None

new_chart_name = st.sidebar.text_input("Chart name (for saving)", value="", placeholder="e.g. Test Chart 1240")
if st.sidebar.button("\U0001F4BE Save this chart"):
    trimmed_name = new_chart_name.strip()
    # A record is made of committed values or it is not made at all (F01):
    # an invalid draft used to be written out verbatim and to reload, in a
    # session with no last good date behind it, as the 1240 default.
    if not trimmed_name:
        st.sidebar.warning("Enter a name before saving.")
    elif _is_reserved_name(trimmed_name):
        # M3: the picker's first option is not a chart. A record saved under
        # that name was listed twice and could then be neither selected nor
        # deleted, since picking it is picking "new chart".
        st.sidebar.error("That name is reserved; choose another.")
    elif not date_is_valid:
        st.sidebar.error("The date is not valid; nothing was saved.")
    elif not (lat is not None and lon is not None and location_query
              and coordinates_in_range(lat, lon)):
        st.sidebar.error("No place is resolved; nothing was saved.")
    else:
        _existing = st.session_state["saved_charts"].get(trimmed_name)
        if _existing is None:
            if _store_chart(trimmed_name, input_record):
                # The picker lists and selects it, and the strip names it,
                # on the rerun this asks for (item 1).
                st.rerun()
        elif _records_match(_existing, input_record):
            # Nothing to write, and nothing to ask about.
            st.sidebar.info(f"'{trimmed_name}' is already saved as it is.")
        else:
            # A name in use and a different nativity: the collision is put
            # to the reader and NOTHING is written on this press (item 4).
            st.session_state["_replace_pending"] = trimmed_name
            st.session_state["_replace_pending_record"] = input_record

# The question stands only while the name and the nativity it was asked
# about stand: any other change in the sidebar rewrites one or the other
# and takes the question with it.
_replace_pending = st.session_state.get("_replace_pending")
if _replace_pending is not None and (
        _replace_pending != new_chart_name.strip()
        or _replace_pending not in st.session_state["saved_charts"]
        or input_record != st.session_state.get("_replace_pending_record")):
    st.session_state.pop("_replace_pending", None)
    st.session_state.pop("_replace_pending_record", None)
    _replace_pending = None
if _replace_pending:
    st.sidebar.warning(f"'{_replace_pending}' exists. Replace it?")
    _replace_col, _both_col = st.sidebar.columns(2)
    if _replace_col.button("Replace", key="_replace_now"):
        if _store_chart(_replace_pending, input_record):
            st.session_state.pop("_replace_pending", None)
            st.session_state.pop("_replace_pending_record", None)
            st.rerun()
    if _both_col.button("Keep both", key="_keep_both"):
        if _store_chart(_free_name(_replace_pending), input_record):
            st.session_state.pop("_replace_pending", None)
            st.session_state.pop("_replace_pending_record", None)
            st.rerun()

# The delete the confirmation asked for, done here rather than where it was
# asked: every sidebar field has been drawn by now, so the rerun below keeps
# them. The disk first, the session's mapping after (item 7).
_delete_now = st.session_state.pop("_delete_now", None)
if _delete_now and _delete_now in st.session_state["saved_charts"]:
    _remaining = dict(st.session_state["saved_charts"])
    del _remaining[_delete_now]
    if write_saved_charts(_remaining):
        st.session_state["saved_charts"] = _remaining
        if st.session_state["_prefs"].get('last_chart') == _delete_now:
            _forget('last_chart')
        st.session_state.pop("_delete_pending", None)
        st.session_state["_select_after_rerun"] = "-- New Chart --"
        st.rerun()
    else:
        st.sidebar.error("Could not write saved_charts.json to disk.")
        st.session_state.pop("_delete_pending", None)

# Modified: the picker names a record and the fields have moved away from
# it (F04, item 2). The strip says so beside the name; the sidebar says so
# under the picker. A record the sidebar could not load is not compared at
# all (H3): the fields never held it, so they cannot have been edited away
# from it, and the sentence beside the picker already says why.
_picked_name = st.session_state.get("chart_picker")
_picked_record = (st.session_state["saved_charts"].get(_picked_name)
                  if _picked_name and _picked_name != NEW_CHART_SENTINEL else None)
# Whether the record the picker names is the one the boxes are holding.
_picked_loaded = _picked_record is not None and chart_record_fault(_picked_record) is None
chart_modified = bool(
    input_record is not None
    and _picked_loaded
    and not _records_match(_picked_record, input_record))
if chart_modified:
    picker_note.caption("Edited since it was saved.")

CONNECTION_PROFILE = _reading("connection_rule", "_connection_rule", "Sahl")
EASTERN_RULE = _reading("eastern_rule", "_eastern_rule", EASTERN_RULE_OPTIONS[0])
MOON_RAYS_ORB = 15.0 if _reading("moon_rays_15", "_moon_rays_15", False) else 12.0
MARS_WEST_RAYS_18 = bool(_reading("mars_west_18", "_mars_west_18", False))
FITTING_INFORTUNE = bool(_reading("fitting_infortune", "_fitting_infortune", False))
DOMAIN_RULE = _reading("domain_rule", "_domain_rule", DOMAIN_RULE_OPTIONS[0])
LOT_HOUSE_CUSP = _reading("lot_house_cusp", "_lot_house_cusp", LOT_HOUSE_CUSP_OPTIONS[0])
# The names above are this run's, for the page's own use; the evaluators read
# them from the engine, which keeps them per thread because Streamlit runs
# every session's script in one of its own. Pinned here, at the top of the
# run, before any evaluator is called. FITTING_INFORTUNE is not among them:
# no evaluator reads it, the page reads it to compute SOFTENED_INFORTUNE,
# which is pinned where it is named (D-13, below).
engine.set_readings(CONNECTION_PROFILE=CONNECTION_PROFILE, EASTERN_RULE=EASTERN_RULE,
                    MOON_RAYS_ORB=MOON_RAYS_ORB, MARS_WEST_RAYS_18=MARS_WEST_RAYS_18,
                    DOMAIN_RULE=DOMAIN_RULE, LOT_HOUSE_CUSP=LOT_HOUSE_CUSP)
# Owner's decision 2026-09-10: ship Abu Ma'shar's quadruplicity turn (IX.1, 26-34)
# as a reading, defaulting to Dykes' plain forward count. Read only by the
# Timing page, so it is not in the Configurations cross-product.
PN4_MONTHLY_TURN = _reading("pn4_monthly_turn", "_pn4_monthly_turn", PN4_MONTHLY_TURN_OPTIONS[0])
# Owner's decision 2026-09-10: the natal wheel carries the Egyptian-bounds
# ring too, as every PN IV wheel does -- the course works the bounds by hand.
CHART_BOUNDS = bool(_reading("chart_bounds", "_chart_bounds", True))
# Owner's ruling 2026-09-15: the wheels and the strips are drawn on white in
# every theme, because that is what a chart on paper is, and the dark
# palette is offered rather than imposed. A display preference like the
# bounds ring and the wheel layout -- not a doctrinal reading, so not in
# READINGS_REGISTRY -- set on the Chart page and in the Timing page's
# Options, one setting for both wheels. Off, every picture is handed None
# and draws exactly as it always has; on, it is handed the viewer's own
# theme, which is the dark palette only when the viewer is in the dark
# theme.
WHEEL_DARK_HELP = ("The wheels and the strips are drawn on a white ground unless this is on, when they take "
                   "the dark palette in the dark theme; in the light theme it changes nothing.")
WHEEL_DARK = bool(_reading("wheel_dark", "_wheel_dark", False))
WHEEL_THEME = VIEWER_THEME if WHEEL_DARK else None
# Which sources are shown (UI_REVIEW_2026-09-10.md §1 B): the course text
# alone, or with Abu Ma'shar's supplement laid beside it. Set on the Sources
# page, where the radio is labelled Sources shown (F12 of the review of
# 2026-09-16: it selects sources, it does not deepen a reading). The stored
# VALUES are unchanged -- the radio prints them through a format_func.
READING_DEPTH = _reading("reading_depth", "_reading_depth", READING_DEPTH_OPTIONS[0])

# Every doctrinal reading, for the Sources page's table of what is in force
# and its reset. (label, widget key, store key, default, page it is set on)
READINGS_REGISTRY = (
    ("Connection test used in the shared tables", "connection_rule", "_connection_rule", "Sahl", "Configurations"),
    ("VII.6, 27/45 eastern/western relative to the Sun", "eastern_rule", "_eastern_rule", EASTERN_RULE_OPTIONS[0], "Configurations"),
    ("Fitting infortune (Choices Ch. 1, 12)", "fitting_infortune", "_fitting_infortune", False, "Configurations"),
    ("Moon under the rays to 15 degrees", "moon_rays_15", "_moon_rays_15", False, "Chart"),
    ("Mars under the rays to 18 degrees west", "mars_west_18", "_mars_west_18", False, "Chart"),
    ("Domain (hayz)", "domain_rule", "_domain_rule", DOMAIN_RULE_OPTIONS[0], "Dignities and places"),
    ("House-based Lots measure to the", "lot_house_cusp", "_lot_house_cusp", LOT_HOUSE_CUSP_OPTIONS[0], "Lots"),
    ("Monthly profections turn", "pn4_monthly_turn", "_pn4_monthly_turn", PN4_MONTHLY_TURN_OPTIONS[0], "Timing"),
    ("Sources shown", "reading_depth", "_reading_depth", READING_DEPTH_OPTIONS[0], "Sources and readings"),
)

def _readings_off_default():
    """The doctrinal readings not at their course default, as (label, value)."""
    out = []
    for label, widget_key, store_key, default, _page in READINGS_REGISTRY:
        value = _reading(widget_key, store_key, default)
        if value != default:
            out.append((label, value))
    return out

def _readings_note():
    """One line under a page header when a persisted reading is in force
    that a reader might not remember setting (UI_REVIEW §2's caution)."""
    off = [(l, v) for l, v in _readings_off_default() if l != "Sources shown"]
    if off:
        st.caption("Readings in force that differ from the defaults: "
                   + "; ".join(f"{l} = {v}" for l, v in off)
                   + ". They are remembered between runs; see Sources and readings to reset them.")


# One line under the header of every page whose CONTENT the Sources shown
# reading changes -- F12 of the review of 2026-09-16 found the setting
# remote from its effect: it is set on Sources, and the pages it adds
# tables to, moves tabs on and adds rows to said nothing about it. The two
# sentences are the same on every such page; nothing here is page-specific.
def _sources_scope_line():
    """The sources in force, said where their effect is read."""
    if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
        st.caption("Sources shown: Sahl's course texts with Abu Ma'shar's supplement.")
    else:
        st.caption("Sources shown: Sahl's course texts. Abu Ma'shar's supplement is off; "
                   "switch it on under Sources and readings.")


# --- The committed nativity, or the reason there is none -----------------
# F05 of the review of 2026-09-16. The shell must not depend on the draft
# being valid, so the sidebar's validation ends in two names -- chart_ok,
# whether a chart can be cast at all, and chart_error, the one sentence
# that says why not -- and only the calculation is conditional. The page
# functions below are defined whatever the answer is: they are closures
# over these top-level names and resolve them when they are called, so a
# page that is never called never touches a name the invalid run left
# unbound, and each page that reads the chart opens with the recovery
# panel instead of its tables.
tz_name = None
if chart_ok:
    # The local moment as digits in the policy's calendar (a CivilMoment,
    # not a datetime: 1300-02-29 is a date here). The UT moment is a Julian
    # Day, jd_ut, and the offset is subtracted on it -- see the calendar
    # note above calculate_traditional_chart (Astra F01).
    local_dt = CivilMoment(input_date.year, input_date.month, input_date.day,
                           input_time.hour, input_time.minute, input_time.second)
    tz_name = None
    zone_note = ""

    if time_standard == TIME_STANDARD_OPTIONS[0]:
        # 15 degrees of longitude = 1 hour of time. East is +, West is -.
        offset_hours = lon / 15.0
        jd_ut = civil_local_to_jd_ut(local_dt.year, local_dt.month, local_dt.day, local_dt.hour_decimal(), offset_hours)
        dt_utc = pn4_datetime_from_jd(jd_ut)
        tz_name = "LMT"
        offset_str = (
            f"{'+' if offset_hours >= 0 else '-'}"
            f"{abs(int(offset_hours)):02d}:{int((abs(offset_hours) * 60) % 60):02d}:{int((abs(offset_hours) * 3600) % 60):02d}"
        )
        utc_offset_hours = offset_hours
        time_standard_box.info(f"**Exact LMT** · UTC offset {offset_str}  \n"
                               f"UT {dt_utc:%Y-%m-%d %H:%M:%S} · {_cal_note}")
    elif time_standard == TIME_STANDARD_OPTIONS[2]:
        utc_offset_hours = float(utc_offset_manual or 0.0)
        jd_ut = civil_local_to_jd_ut(local_dt.year, local_dt.month, local_dt.day, local_dt.hour_decimal(), utc_offset_hours)
        dt_utc = pn4_datetime_from_jd(jd_ut)
        _tot = int(round(abs(utc_offset_hours) * 3600))
        tz_name = f"UTC{'+' if utc_offset_hours >= 0 else '-'}{_tot // 3600:02d}:{(_tot % 3600) // 60:02d}"
        time_standard_box.info(f"**Manual offset** {tz_name}  \n"
                               f"UT {dt_utc:%Y-%m-%d %H:%M:%S} · {_cal_note}")
    else:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        if tz_name:
            local_tz = pytz.timezone(tz_name)
            # A named zone needs a datetime, which is proleptic Gregorian: a
            # Julian-only day (1300-02-29) has no place in it, and no zone
            # kept standard time then anyway.
            # The three refusals below used to end in st.stop(), which took
            # the page list with them (F05): each states the same sentence
            # in the sidebar's own box and hands it to chart_error, and the
            # else-arms carry what st.stop() used to skip.
            try:
                _local_py = datetime(local_dt.year, local_dt.month, local_dt.day,
                                     local_dt.hour, local_dt.minute, local_dt.second)
            except ValueError:
                chart_error = (
                    f"**{local_dt:%Y-%m-%d}** is a Julian-calendar date that no standard-time zone can "
                    "place. Choose LMT or a manual offset."
                )
                time_standard_box.error(chart_error)
                chart_ok = False
            else:
                # is_dst=None makes pytz RAISE on the two clock times a named
                # zone cannot resolve on its own: the hour that occurs twice at
                # a DST fall-back, and the hour that never occurs at spring
                # forward. Without it pytz silently picks one, which moves the
                # chart by an hour with no indication that a choice was made.
                try:
                    localized_dt = local_tz.localize(_local_py, is_dst=None)
                except pytz.exceptions.AmbiguousTimeError:
                    chart_error = (
                        f"**{local_dt:%Y-%m-%d %H:%M}** happens twice in {tz_name} "
                        "(daylight-saving fall-back). Choose LMT or a manual offset, or enter a time "
                        "outside the repeated hour."
                    )
                    time_standard_box.error(chart_error)
                    chart_ok = False
                except pytz.exceptions.NonExistentTimeError:
                    chart_error = (
                        f"**{local_dt:%Y-%m-%d %H:%M}** does not exist in {tz_name} "
                        "(the clocks jump over it at daylight-saving spring-forward). "
                        "Check the recorded time."
                    )
                    time_standard_box.error(chart_error)
                    chart_ok = False
                else:
                    # This is the OFFSET, not the UTC clock time -- an earlier
                    # version printed dt_utc's own time under the label "UTC offset".
                    _off = localized_dt.utcoffset()
                    utc_offset_hours = _off.total_seconds() / 3600.0
                    jd_ut = civil_local_to_jd_ut(local_dt.year, local_dt.month, local_dt.day, local_dt.hour_decimal(), utc_offset_hours)
                    dt_utc = pn4_datetime_from_jd(jd_ut)
                    _sign = '+' if utc_offset_hours >= 0 else '-'
                    _tot = int(abs(_off.total_seconds()))
                    time_standard_box.info(
                        f"**{tz_name}** · UTC offset {_sign}{_tot // 3600:02d}:{(_tot % 3600) // 60:02d}"
                        f" ({localized_dt.tzname()})  \nUT {dt_utc:%Y-%m-%d %H:%M:%S} · {_cal_note}"
                    )
                    zone_note = f" · {tz_name}"
    if chart_ok:
        location_box.success(f"**{escape(str(location_query))}**  \n{lat:.4f}, {lon:.4f}{zone_note}")

# The named-zone branch alone can end with no zone at all (a point at sea
# has none); its message used to be the `else` of `if tz_name:`, three
# thousand lines below.
if chart_ok and not tz_name:
    chart_error = "Timezone boundary not found for coordinates."
    st.sidebar.error(chart_error)
    chart_ok = False

# H1: the moment is in UT by now, offset and all, so this is where to ask
# whether the ephemeris has anything to say about it -- and it is asked
# BEFORE the calculation, and answered like any other invalid input: one
# sentence in the sidebar and chart_ok False. The shell, the top
# navigation, Reference and Sources all stay, and every page that reads the
# chart opens with the recovery panel. The box the branch above filled is
# overwritten rather than left announcing the UT of a chart that is not
# going to be cast.
if chart_ok and not jd_in_ephemeris(jd_ut):
    chart_error = EPHEMERIS_DATE_MESSAGE
    time_standard_box.error(chart_error)
    chart_ok = False

if chart_ok:
    chart_data = calculate_traditional_chart_jd(jd_ut, lat, lon)
    p_data = chart_data['planetary_data']
    sect = chart_data['sect']
    # D-13: named here, before any evaluator runs, since they read it.
    SOFTENED_INFORTUNE = fitting_infortune(chart_data['ascendant']) if FITTING_INFORTUNE else None
    engine.set_readings(SOFTENED_INFORTUNE=SOFTENED_INFORTUNE)

    essential = evaluate_essential_dignities(p_data, sect)
    accidental = evaluate_accidental_dignities(p_data, chart_data['houses'], sect, chart_data['julian_day'],
                                               armc=chart_data['armc'], obliquity=chart_data['obliquity'], geo_lat=lat)
    aspects = evaluate_ptolemaic_aspects(p_data)
    transfers = evaluate_transfers_of_light(p_data)
    collections = evaluate_collections_of_light(p_data)
    sim = _simulate_forward(p_data, chart_data['julian_day'])
    abu_mashar_condition = evaluate_abu_mashar_condition(
        p_data, chart_data['houses'], sect, essential, accidental, chart_data['julian_day'], chart_data['ascendant'], sim
    )
    banishment_data = evaluate_sahl_banishment(p_data)
    natural_connections = evaluate_abu_natural_connections(p_data)
    wildness_data = evaluate_abu_wildness(p_data)
    reflections = evaluate_reflections_of_light(p_data, chart_data['ascendant'])
    blocking_data = evaluate_blocking(p_data)
    enclosure_data = evaluate_enclosure(p_data)
    handing_over_data = evaluate_handing_over(p_data, sect)
    reception_data = evaluate_reception(p_data, sect, sim)
    non_reception_data = evaluate_non_reception(p_data, sect)
    strength_data = evaluate_strength_of_planets(p_data, essential, accidental, chart_data['ascendant'], sect, chart_data['houses'])
    weakness_data = evaluate_weakness_of_planets(p_data, essential, accidental, chart_data['ascendant'], sect)
    ascensional_bands = evaluate_ascensional_bands(p_data, chart_data['ascendant'], chart_data['mc'], chart_data['obliquity'], lat, sect)
    right_sidedness = evaluate_right_sidedness(p_data, sect)
    honor_guard = evaluate_honor_guard(p_data, chart_data['ascendant'])
    _moon = evaluate_corruption_of_the_moon(p_data, chart_data['ascendant'], sect)
    # Count is "how many of Sahl's ten testimonies", never the number of
    # clauses that matched: 104 and 109 can each be met by several
    # planets, and a list of ten must not add up to twelve.
    moon_corruption_data = ([{'Planet': 'Moon',
                              'Defects': ', '.join(_moon['labels'])
                              + (f"  [{_moon['matching_instances']} clauses across "
                                 f"{_moon['unique_testimony_count']} of the ten testimonies]"
                                 if _moon['matching_instances'] > _moon['unique_testimony_count'] else ''),
                              'Count': _moon['unique_testimony_count']}]
                            if _moon['labels'] else [])
    returning_data = evaluate_returning(p_data, accidental, chart_data['ascendant'])
    revoking_data = evaluate_revoking(p_data, sim)
    resistance_data = evaluate_resistance(p_data, sim)
    escape_data = evaluate_escape(p_data, sim)
    cutting_data = evaluate_cutting_the_light(p_data, sim)
    favor_recompense_data = evaluate_favor_and_recompense(p_data, essential, sect, sim)
    forward_looking_data = (
        [{'Condition': 'Revoking', **row} for row in revoking_data]
        + [{'Condition': 'Resistance', **row} for row in resistance_data]
        + [{'Condition': 'Escape', **row} for row in escape_data]
    )
    syzygy = calculate_prenatal_syzygy(chart_data['julian_day'], lat, lon, chart_data['houses'])
    syzygy_governor = sahl_syzygy_governor(syzygy, p_data, chart_data['houses'], sect)
    # The cached function takes the local HOUR (an int Streamlit can
    # hash), not the CivilMoment; it reads nothing else of it.
    chronocrats = calculate_chronocrats(chart_data['julian_day'], lat, lon, local_dt.hour, utc_offset_hours)
    classical_lots = calculate_classical_lots(chart_data['ascendant'], p_data['Sun']['longitude'], p_data['Moon']['longitude'], sect)
    topical_lots = calculate_topical_lots(p_data, chart_data['ascendant'], chart_data['houses'], sect)
    special_degrees = evaluate_special_degrees(p_data)
    book_v_degrees_data = evaluate_book_v_degrees(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'], sect)
    nobility_degrees_data = evaluate_nobility_degrees(p_data, chart_data['ascendant'], sect)
    moon_third_day_data = evaluate_moon_third_day(chart_data)
    gestation_data = evaluate_gestation(chart_data, lat, lon)
    mercury_phase_sect_data = evaluate_mercury_phase_sect(p_data, sect)
    moon_phase_valens_data = evaluate_moon_phase_valens(p_data)
    morin_aspects_data = evaluate_morin_aspects(p_data, chart_data['houses'], chart_data['ascendant'])
    eyesight_places_data = evaluate_eyesight_places(p_data, chart_data['ascendant'])
    rhetorius_affliction_data = evaluate_rhetorius_affliction(p_data, chart_data['ascendant'], sect)
    mars_abu_bakr_data = evaluate_mars_abu_bakr(p_data, sect, chart_data['ascendant'])
    prosperity_data = evaluate_prosperity(chart_data)
    rays_by_ascension_data = evaluate_rays_by_ascension(p_data, chart_data['armc'], chart_data['obliquity'], lat)
    house_lords_data = evaluate_house_lords(p_data, chart_data['ascendant'])
    victors_data = evaluate_victors(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'],
                                     syzygy['syzygy_longitude'], sect, chronocrats)
    planets_in_houses_data = evaluate_planets_in_houses(p_data, abu_mashar_condition, chart_data['ascendant'])
    time_lords_data = calculate_time_lords(chart_data['ascendant'], input_date, target_date)
    planetary_years_data = evaluate_planetary_years_display(p_data, chart_data['houses'], chart_data['ascendant'], sect, essential,
                                                            supplement=READING_DEPTH == READING_DEPTH_OPTIONS[1])
    pn4 = pn4_timing_bundle(chart_data, lat, lon, input_date, target_date, PN4_MONTHLY_TURN, chronocrats)

    # The hub names the chart: the saved chart picked in the sidebar, else
    # the name typed for saving, else "Transits" (owner's decision D5,
    # 2026-09-07: an unnamed chart cast for a date is a transit chart).
    # Loading a saved chart and then editing its date keeps the saved
    # name; accepted.
    #
    # The two natal wheels used to be built here, at the top level, from
    # CHART_BOUNDS and WHEEL_THEME. They are built inside the Chart
    # page's _wheel_block() fragment now (item 9, 2026-09-15), from the
    # bounds and dark-wheel values its own widgets hold: a fragment rerun
    # does not re-run this line, so a wheel built here would be the
    # previous full run's wheel. Nothing else on this page or any other
    # read svg_code or svg_wide -- the Chart page's picture and its
    # download button were the only two consumers -- so the top-level
    # build is gone rather than kept beside the fragment's, and the eight
    # pages that never draw a natal wheel no longer generate two of them.
    # A record the sidebar could not load does not name the chart either
    # (H3): the boxes hold what they held before it was picked, so titling
    # the strip with it would name a nativity that is not on the screen.
    # The picker still shows the name the reader clicked, and the sentence
    # beside it says why nothing was loaded.
    chart_name = (_picked_name if _picked_loaded
                  else new_chart_name.strip() or "Transits")

# The app's name is the browser title (st.set_page_config) and the
# header bar's own; it used to be repeated as an st.title above every
# page's st.header, which cost a heading's height on every page and
# told the reader nothing the window did not already say.

# --- one finding, at three depths ---------------------------------
# Provenance used to live in help= because that was the nearest
# container, and 31 tooltips grew to 22,771 characters of citations,
# quotations, measured frequencies and superseded readings -- served
# as hover text, which cannot be scrolled, selected or searched.
#
# Three depths, three containers. GLANCE: what this is, in the
# tooltip, under about 200 characters. CHECK: the citation, as a
# visible caption, plus the row's own Source and Standing columns
# where the table carries them. AUDIT: the quotations and the
# measurements, in an expander under the table.
#
# column_config, name-based: the DataFrame's own values never change
# on this branch (the doctrine fixtures compare them), only how a
# column is displayed. Value/Text/Reading/Source/Note/Notes/
# Quotation/Sentence/Standing are this app's citation- and
# prose-heavy columns, cut off at the default width.
_WIDE_TEXT_COLUMNS = {'Value', 'Text', 'Reading', 'Source', 'Note', 'Notes',
                       'Quotation', 'Sentence', 'Standing'}

def _wide_text_columns(df):
    """column_config for a table's own text-heavy columns, by name."""
    return {col: st.column_config.TextColumn(width="large")
            for col in df.columns if col in _WIDE_TEXT_COLUMNS}

# The columns this app actually prints as "Yes" / "No" / "" -- found
# by checking each candidate's real values (2026-09-15): "Received"
# holds a planet's name and "Active" holds "yes" (lowercase) or a
# full sentence, so neither is here despite the family resemblance.
# Width alone; no CheckboxColumn and no boolean conversion.
_YES_NO_COLUMNS = {'Match', 'Sees ASC', 'Above horizon',
                    "Domain (hayz)", "Of the chart's sect", 'Averse to its place',
                    'Rules differ'}

def _yes_no_columns(df):
    """column_config for a table's own Yes/No/"" columns, by name."""
    return {col: st.column_config.TextColumn(width="small")
            for col in df.columns if col in _YES_NO_COLUMNS}

# Columns whose values are a short PHRASE rather than a word, a name or a
# number: wider than the default, narrower than a prose column. Connection
# holds "Under a single blanket" (Sahl, The Introduction Ch. 3, 7), which
# the default width cuts off mid-word -- and the width of a state's name is
# not a reason to shorten the name the text gives it.
_MEDIUM_TEXT_COLUMNS = {'Connection'}


def _medium_text_columns(df):
    """column_config for a table's own short-phrase columns, by name."""
    return {col: st.column_config.TextColumn(width="medium")
            for col in df.columns if col in _MEDIUM_TEXT_COLUMNS}

# A finding with nothing to report is not given a heading at all --
# it is collected and named in one line at the foot of its group,
# which is what turns seventeen "No X found" headings into four.
# standing= is the finding's own footing -- "Supplement", "display
# only" -- which used to be a parenthesis inside the h3 itself. The
# heading is the finding's NAME; the footing and the citation are one
# caption under it, separated by a middle dot.
def _finding(bucket, title, citation, data, glance=None, notes=None, columns=None, height=None,
             standing=None, absent=None, column_help=None, caption=None):
    if not data:
        # absent= is for a finding whose emptiness is the END OF A SEARCH,
        # not an absence: the search ran, it was bounded, and what it
        # covered has to be said where the zero rows are (F07). Such a
        # finding keeps its own heading and says what was looked at,
        # instead of joining the "Not present in this chart" line, which
        # claims more than a bounded search can establish.
        if absent:
            st.subheader(title, help=glance)
            st.caption(absent)
            return
        bucket.append(title)
        return
    st.subheader(title, help=glance)
    if standing or citation:
        st.caption(" · ".join(part for part in (standing, citation) if part))
    # columns= pins the order (pandas otherwise takes the first
    # row's); height= shows every row of a table meant to be read
    # whole, instead of st.dataframe's ten-row inner scroll.
    _df = pd.DataFrame(data, columns=columns)
    # column_help= is the one-line definition of a column whose HEADING is
    # a term of art, carried on the heading itself rather than in the notes
    # expander, so the word is defined where it is read (F10).
    _help = {col: st.column_config.TextColumn(
                 help=text, **({'width': 'medium'} if col in _MEDIUM_TEXT_COLUMNS else {}))
             for col, text in (column_help or {}).items() if col in _df.columns}
    st.dataframe(_df, hide_index=True, width='stretch',
                 column_config={**_wide_text_columns(_df), **_yes_no_columns(_df),
                                **_medium_text_columns(_df), **_help},
                 **({'height': height} if height is not None else {}))
    # caption= sits UNDER the table, for the sentence that explains the
    # rows themselves rather than the finding's source.
    if caption:
        st.caption(caption)
    if notes:
        with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
            st.markdown(notes)

def _absent(bucket):
    if bucket:
        st.caption("Not present in this chart: " + ", ".join(bucket) + ".")
        del bucket[:]

# The strip under every page header: which chart the page is reading.
# The app opens on the last chart used, and nothing above the fold
# named it except the sidebar's picker and the wheel's hub -- and the
# wheel is on one page of nine. One caption, the parts separated by a
# middle dot, each formatted as the sidebar's own boxes format it, so
# the strip and the sidebar cannot come to disagree.
def _chart_strip():
    # No chart, no strip: a recovery page has nothing to name (F05).
    if not chart_ok:
        return
    # A record the sidebar could not load does not name the chart either
    # (H3): the boxes hold what they held before it was picked, so naming
    # the strip after it would name a nativity that is not on the screen.
    # The picker still shows the name the reader clicked, and the sentence
    # beside it says why nothing was loaded.
    name = _picked_name if _picked_loaded else "Unsaved chart"
    # A record whose fields have been edited since it was saved is named as
    # what it is (F04, item 2): the review found an edited record still
    # carrying its saved name with nothing to say the two had parted.
    if chart_modified:
        name = f"{name} (modified)"
    _sign = "+" if utc_offset_hours >= 0 else "-"
    _tot = int(round(abs(utc_offset_hours) * 3600))
    # LMT resolves to the second, as its box prints it; a named zone
    # and a manual offset resolve to the minute, as theirs do.
    if time_standard == TIME_STANDARD_OPTIONS[0]:
        _offset = f"{_sign}{_tot // 3600:02d}:{(_tot % 3600) // 60:02d}:{_tot % 60:02d}"
    else:
        _offset = f"{_sign}{_tot // 3600:02d}:{(_tot % 3600) // 60:02d}"
    # A manual offset's name IS its offset ("UTC+05:00"), so it is not
    # printed twice.
    standard = tz_name if tz_name.startswith("UTC") else f"{tz_name} {_offset}"
    # Coordinates entered directly name themselves -- the place IS
    # "Manual [43.7792, 11.2463]" -- so the strip prints them once.
    place = (f"{lat:.2f}, {lon:.2f}" if location_query.startswith("Manual [")
             else f"{location_query} {lat:.2f}, {lon:.2f}")
    # The prenatal lunation is one of the first questions asked of a
    # nativity, and the strip is on every page, so it rides here as
    # one word: the label is "Conjunctional (New Moon)" and its first
    # word is the answer. The degree and the house it falls in stay
    # on the lunation and victors page, whose syzygy table carries
    # them in full.
    lunation = syzygy['event_label'].partition(' ')[0]
    # Two lines, not one: the first is the nativity as it was entered
    # -- the name, the moment, the standard it is counted in, the
    # place -- and the second is what the app makes of it. Eight parts
    # on one line ran past the window and wrapped where the width
    # happened to fall, which put the break in a different place on
    # every page. The hard break is two spaces and a newline, which is
    # how the sidebar's own boxes break a caption.
    # The COMMITTED date, never the draft in the box: the strip names the
    # chart the page is showing, and "not-a-date 14:30" named a chart that
    # was never cast (F01a).
    entered = " · ".join((
        str(name),
        f"{input_date:%Y-%m-%d} {input_time:%H:%M:%S}",
        standard,
        place,
    ))
    # The qualification travels with the value (F09). Where there is no
    # sunrise or sunset the hour is not a temporal hour at all, and the
    # strip is on every page while the Chart page's fuller warning is on
    # one: an unqualified hour lord elsewhere is the same value said
    # without the thing that makes it approximate.
    hour_lord = f"Hour lord {chronocrats['Hour Lord']}"
    if chronocrats.get('Approximate'):
        hour_lord += " (equal-hour approximation)"
    read = " · ".join((
        sect,
        f"{lunation} lunation",
        f"Day lord {chronocrats['Day Lord']}",
        hour_lord,
    ))
    # The second line in bold: the first line is the nativity as the
    # reader typed it and they know it already, while these four are
    # measurements the app made, and nothing else above the fold
    # states them. The markers wrap the joined line once, not each
    # part -- a caption renders markdown, as the sidebar's own boxes
    # do.
    st.caption("  \n".join((entered, f"**{read}**")))
    _stale_notice()


def _stale_notice():
    """One line under the strip while the draft date does not parse: the
    tables below it are the last valid chart's and have not moved (F01d).
    The sidebar says the same of the date field; this says it where the
    results are, on every page."""
    if chart_ok and not date_is_valid:
        st.warning(f"Results have not updated. Showing the last valid chart: "
                   f"{input_date:%Y-%m-%d} {input_time:%H:%M:%S}.")


def _recovery_panel(title):
    """What a page that reads the chart shows when there is no chart: its
    own header, the one sentence that says why, and where to fix it. The
    reference tables and the sources do not call it -- they read the
    engine's tables, not the chart, and render in full (F05)."""
    st.header(title)
    st.error(chart_error)
    st.caption("Correct the nativity in the sidebar; the reference tables and the sources "
               "stay available.")

# Streamlit drops a widget's state when the widget is not rendered
# on a run, which is why a page-level control resets after
# navigating away even with a key. _persist() copies the widget's
# value into a store key that survives navigation; the widget takes
# st.session_state.get(store_key, default) as its default, so the
# page and the engine (which read the same store at the top level)
# agree on the first render.
def _persist(widget_key, store_key, default):
    """Render-independent memory for a page widget. Call AFTER the widget.
    A store that is a preference is also written to disk (2026-09-10)."""
    if widget_key in st.session_state:
        st.session_state[store_key] = st.session_state[widget_key]
        _remember(store_key, st.session_state[store_key])
    return st.session_state.get(store_key, default)

def _reading_checkbox(label, widget_key, store_key, help=None):
    st.checkbox(label, value=st.session_state.get(store_key, False), key=widget_key, help=help)
    return _persist(widget_key, store_key, False)

def _reading_select(label, options, widget_key, store_key, help=None):
    options = list(options)
    stored = st.session_state.get(store_key, options[0])
    st.selectbox(label, options, index=options.index(stored) if stored in options else 0,
                 key=widget_key, help=help)
    return _persist(widget_key, store_key, options[0])

def _reading_radio(label, options, widget_key, store_key, help=None,
                   label_visibility="visible", format_func=None):
    # label_visibility is passed through for the one control that
    # stands in a row of checkboxes, where a label above the options
    # puts the radio on a tier of its own. The label string is still
    # given -- Streamlit requires a non-empty one, and it stays the
    # widget's accessible name and the name a test looks it up by.
    options = list(options)
    stored = st.session_state.get(store_key, options[0])
    # Seeded, not defaulted by index: the target keys are also written
    # by _restore_chart, and a default beside a seeded key warns.
    st.session_state.setdefault(widget_key, stored if stored in options else options[0])
    # format_func changes only what the reader sees: the option VALUES are
    # what is stored, compared and printed in the readings table.
    st.radio(label, options, key=widget_key, horizontal=True, help=help,
             label_visibility=label_visibility, format_func=format_func or str)
    return _persist(widget_key, store_key, options[0])

# Strength and Weakness as tick grids: one row per planet, one column
# per numbered testimony, ticked where the planet's Labels cite that
# paragraph. The labels end in "(78)" ... "(100)", or "(84; ...)",
# "(95, ...)" where a citation follows; the first such number is the
# paragraph. The sentence form stays under the grid as the answer key.
STRENGTH_COLUMNS = [('78', '78 excellent place'), ('79', '79 own dignity'), ('80', '80 direct'),
                    ('81', '81 not in infortune stakes'), ('82', '82 not with fallen'),
                    ('83', '83 advancing'), ('84', '84 eastern, masculine'), ('85', '85 of sect'),
                    ('86', '86 fixed sign'), ('87', '87 heart of Sun'), ('88', '88 gender match')]
WEAKNESS_COLUMNS = [('91', '91 falling, averse ASC'), ('92', '92 retrograde'), ('93', '93 under rays'),
                    ('94', '94 connects infortune'), ('95', '95 enclosed'), ('96', '96 own fall'),
                    ('97', '97 averse / lost receiver'), ('98', '98 alien'), ('99', '99 with nodes'),
                    ('100', '100 inverted')]
_PARAGRAPH = re.compile(r'\((\d{2,3})(?=[;,)])')
# citation reads "Sahl, The Introduction Ch. 3, 78-88": everything
# before the trailing run of sentence numbers is the chapter locator.
_CITATION_LOCATOR = re.compile(r'^(.*), [\d\s,-]+$')

def _tick_grid(bucket, title, citation, data, text_key, columns, glance=None, notes=None):
    if not data:
        bucket.append(title)
        return
    st.subheader(title, help=glance)
    if citation:
        st.caption(citation)
    grid = []
    for row in data:
        cited = {m.group(1) for m in map(_PARAGRAPH.search, row['Labels']) if m}
        cells = {'Planet': row['Planet']}
        for num, header in columns:
            cells[header] = '\u2713' if num in cited else ''
        cells['Count'] = row['Count']
        grid.append(cells)
    # Each testimony column's header becomes the words alone -- "78
    # excellent place" reads "excellent place" -- with the sentence
    # number moved into the header's tooltip: the chapter locator
    # read off `citation` itself (not invented) plus the number, or
    # "sentence 78" alone where the citation does not name a chapter.
    _locator_match = _CITATION_LOCATOR.match(citation) if citation else None
    _locator = _locator_match.group(1) if _locator_match else None
    _grid_columns = {'Planet': st.column_config.TextColumn(width="small"),
                      'Count': st.column_config.TextColumn(width="small")}
    for num, header in columns:
        _grid_columns[header] = st.column_config.TextColumn(
            label=header[len(num) + 1:],
            help=f"{_locator}, {num}" if _locator else f"sentence {num}",
            width="small")
    # A row can be selected (single-row, rerun): the grid's key is
    # its title, lower-cased and underscored. The selection reruns
    # the fragment this grid stands in and nothing else on the page.
    _grid_key = re.sub(r'\W+', '_', title.lower()).strip('_') + '_grid'
    _event = st.dataframe(pd.DataFrame(grid), hide_index=True, width='stretch', height=_rows_height(len(grid)),
                          column_config=_grid_columns, on_select="rerun", selection_mode="single-row",
                          key=_grid_key)
    _picked = list(_event.selection.rows)
    if _picked and 0 <= _picked[0] < len(data):
        _row_detail(data[_picked[0]], len(columns), _locator)
    with st.expander("Answer key: testimonies in words"):
        st.dataframe(pd.DataFrame(data, columns=['Planet', text_key, 'Count']),
                     hide_index=True, width='stretch', height=_rows_height(len(data)))
    if notes:
        with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
            st.markdown(notes)

# Why a tick fired: the selected planet's row, one block per ticked
# testimony in numerical order -- the sentence's locator as the
# column tooltips give it, the sentence as the answer key words it,
# then the chart values the evaluator tested, which it reports as
# "Fact: Value" strings alongside each label (its Testimonies key).
# Nothing here is computed on the page; the panel restates the
# evaluator's own reasoning and adds no test of its own.
def _row_detail(row, total, locator):
    st.subheader(f"{row['Planet']}: {row['Count']} of {total} testimonies")
    for testimony in sorted(row.get('Testimonies', []), key=lambda t: int(t['n'])):
        st.caption(f"{locator}, {testimony['n']}" if locator else f"sentence {testimony['n']}")
        st.markdown(testimony['sentence'])
        facts = [fact.partition(': ') for fact in testimony['facts']]
        if len(facts) == 1:
            st.caption(testimony['facts'][0])
        elif facts:
            st.dataframe(pd.DataFrame([{'Fact': name, 'Value': value} for name, _, value in facts]),
                         hide_index=True, width='stretch', height=_rows_height(len(facts)))

# Table heights: st.dataframe shows about ten rows and then scrolls
# inside itself. A table meant to be read whole gets its own height:
# 35 px per row and header, 3 px of border, and 12 px for the
# horizontal scrollbar a wide table (the aspects grid, the tick
# grids) draws -- measured at 1280 px, where without it those
# tables were 9 px short and still scrolled.
def _rows_height(n):
    return 35 * (n + 1) + 15

def _hms(hours):
    total = int(round((hours % 24.0) * 3600))
    return f"{total // 3600:02d}h {(total % 3600) // 60:02d}m {total % 60:02d}s"

def _dms(degrees):
    total = int(round((degrees % 360.0) * 3600))
    return f"{total // 3600}° {(total % 3600) // 60:02d}' {total % 60:02d}\""


def page_chart():
    if not chart_ok:
        _recovery_panel("Chart")
        return
    st.header("Chart")
    _chart_strip()
    _readings_note()
    _gap = []
    # The twelve signs' hover text, and the panel a click opens. Both
    # are display only: every row either restates a position the page
    # already prints or is lifted whole out of a table another page
    # draws, and each table's caption says which page that is. The
    # hover text is worked out once per run, in Python, and handed to
    # the component inside its envelope, so that moving the pointer
    # across the zodiac asks the server nothing.
    def _sign_hover(index):
        summary = sign_summary(index, sect)
        bounds = ", ".join(f"{row['Lord']} to {row['Bound'].split('-')[1]}" for row in summary['bounds'])
        return (f"{summary['sign']} · {summary['element']}\n"
                f"Bounds: {bounds}\n"
                f"Triplicity ({sect}): {summary['lords'][2]['Lord']}, "
                f"with {summary['lords'][3]['Lord']} partnering")

    # Two across rather than one down: a caption and a small table
    # stacked six deep ran the panel far past the wheel. Each section
    # is its caption and then its table, so the pair reads as a
    # labelled block, and the sections fill left, right, left, right
    # in their own order. A section with no rows draws nothing and
    # takes no slot, so the two columns stay level.
    def _panel_columns(sections):
        filled = [(caption, rows) for caption, rows in sections if rows]
        if not filled:
            return
        columns = st.columns(2)
        for index, (caption, rows) in enumerate(filled):
            with columns[index % 2]:
                st.caption(caption)
                st.dataframe(pd.DataFrame(rows), hide_index=True, width='content')

    def _pick_panel(picked):
        """The panel under the controls row: nothing until a planet,
        an angle or a sign is clicked in the wheel."""
        kind, _sep, value = str(picked or "").partition(":")
        if kind == "sign" and value.isdigit():
            summary = sign_summary(int(value), sect)
            st.subheader(summary['sign'])
            _panel_columns([
                ("The lords of the sign. The Reference page carries every sign.", summary['lords']),
                ("The Egyptian bounds, which the Reference page carries in full.", summary['bounds']),
                ("The three faces, which the Reference page carries beside the other dignities.", summary['faces']),
            ])
        elif kind == "planet":
            summary = point_summary(value, chart_data, essential, accidental, aspects,
                                    reception_data, classical_lots, topical_lots)
            if summary is None:
                return
            st.subheader(summary['point'])
            _panel_columns([
                ("Where it stands. The Calculated Points and Quadrant divisions tables below carry every point.",
                 summary['position']),
                ("Its dignity at its own degree. The Dignities page carries the full lordship table.",
                 summary['essential']),
                ("Its accidental conditions. The Dignities page carries them for every planet.",
                 summary['accidental']),
                ("The connections it stands in. The Configurations page carries the whole aspects table.",
                 summary['connections']),
                (f"Reception under the {CONNECTION_PROFILE} rule. The Configurations page carries the full table.",
                 summary['receptions']),
                ("The Lots it is lord of. The Lots page carries the classical and the topical Lots in full.",
                 summary['lots']),
            ])

    # Looking at the chart is the primary act, so the wheel takes the
    # centre of the page: the square wheel centred at 560 px, its
    # controls in one row beneath it, the introduction beneath those.
    # The picture is a component (item 11) rather than an st.image,
    # which cost it Streamlit's own fullscreen wrapper -- the expand
    # arrows the tables carry -- so the component carries an expand
    # control of its own instead. The wide variant runs the full page width and scrolls,
    # with its positions panel drawn into the picture, and is there for
    # the full-window view, which a square can only fill to the
    # window's height. Both layouts then read alike: the same controls
    # row, the same three sentences.
    #
    # The layout is still read from the control's state BEFORE the
    # control is drawn, because the control now sits under the wheel
    # and the wheel must know which of the two to draw. The widget key
    # holds the new value from the start of the rerun that a click
    # causes; the store key keeps it across pages.
    #
    # The wheel and its four controls are one @st.fragment (item 9,
    # 2026-09-15). A click on the radio, either checkbox or the
    # download button used to rerun the whole script and redraw every
    # table on the page; a fragment reruns only its own body on its
    # own widgets' changes. The engine is cheap -- the whole run is
    # about a fifth of a second -- so this is about the redraw and
    # the flicker, not the compute. Two consequences the code has to
    # honour: the SVG is generated INSIDE the fragment, from the
    # bounds and dark-wheel values the fragment's own widgets hold
    # (the top-level CHART_BOUNDS and WHEEL_THEME are a full run's
    # values and do not move on a fragment rerun), and a fragment may
    # not write to a container outside itself, so everything it draws
    # -- picture and controls row -- is inside its body and nothing
    # else is. The three captions, the circumpolar warning and the
    # rest of the page stay outside, where they are not redrawn.
    @st.fragment
    def _wheel_block():
        st.session_state.setdefault("_chart_bounds", True)
        # The four controls in one row across the page, aligned on
        # their feet so the radio's row of options, the two checkboxes
        # and the button sit on one line rather than at three heights.
        #
        # A flex row, not st.columns: Streamlit stacks columns
        # vertically below about 640 px of page width, and a reader
        # zoomed in or in a narrow window is below it, so the four
        # controls ran down the left-hand edge in a column. A
        # horizontal container keeps them in a row at any width and
        # wraps (wrap defaults to True) only when they genuinely
        # cannot fit. Left-aligned and the page's full width, as the
        # row of controls was asked for.
        def _layout_control():
            with st.container(horizontal=True, vertical_alignment="bottom", gap="medium"):
                # The label is collapsed and the tooltip dropped here, and
                # here only: a radio carries its label above its options
                # and a checkbox carries its beside the box, so labelled
                # this radio stood a tier above the three controls next to
                # it and the row read as two. The two words "Square" and
                # "Wide" beneath a wheel say what the control does. The
                # label string stays as the widget's accessible name.
                layout = _reading_radio(
                    "Wheel layout", WHEEL_LAYOUT_OPTIONS, "wheel_layout", "_wheel_layout",
                    label_visibility="collapsed")
                # The two checkboxes still write their store keys and the
                # preferences file through _persist, which works inside a
                # fragment exactly as it does at the top level; that is
                # what lets the next full run read CHART_BOUNDS and
                # WHEEL_DARK and find what the fragment left.
                _reading_checkbox("Bounds ring", "chart_bounds", "_chart_bounds",
                                  help="The Egyptian bounds, with their lords, as a ring inside the degree scale -- "
                                       "as every natal wheel in Persian Nativities IV carries them (Figures 1, 22, "
                                       "25, 26).")
                _reading_checkbox("Dark wheel", "wheel_dark", "_wheel_dark", help=WHEEL_DARK_HELP)
                st.download_button("Download the wheel (SVG)", svg_wide if layout == WHEEL_LAYOUT_OPTIONS[1] else svg_code,
                                   key="dl_chart_wheel", mime="image/svg+xml",
                                   file_name=f"{re.sub(r'[^A-Za-z0-9]+', '_', chart_name).strip('_') or 'chart'}_natal.svg")
            return layout
        wheel_layout = st.session_state.get(
            "wheel_layout", st.session_state.get("_wheel_layout", WHEEL_LAYOUT_OPTIONS[0]))
        # Read before draw, for the same reason the layout is: the two
        # checkboxes sit UNDER the picture, and the picture has to be
        # generated before them. A widget key holds the new value from
        # the start of the rerun a click causes, so the wheel the click
        # asks for is the wheel drawn on that same (fragment) rerun.
        # The fallback is this run's top-level reading -- CHART_BOUNDS
        # and WHEEL_DARK are _reading(widget key, store key, default)
        # and are what every other reader of these two preferences
        # sees -- which is what the first render of the page uses,
        # before the checkbox has a key, and after navigating back to
        # the page, where Streamlit has dropped the widget's state.
        # On a fragment rerun they are the last full run's values, so
        # the widget key in front of them is what moves.
        _bounds = bool(st.session_state.get("chart_bounds", CHART_BOUNDS))
        _dark = bool(st.session_state.get("wheel_dark", WHEEL_DARK))
        # The same rule the top level uses for WHEEL_THEME: the
        # viewer's own theme when the preference is on, None when it
        # is off, so off the picture is drawn exactly as it always was.
        _theme = VIEWER_THEME if _dark else None
        svg_code = generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, local_dt, tz_name,
                                       chronocrats=chronocrats, bounds=_bounds, theme=_theme)
        svg_wide = generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, local_dt, tz_name,
                                       wide=True, chronocrats=chronocrats, bounds=_bounds, theme=_theme)
        # The picture is mounted as the natal_wheel component rather
        # than shown with st.image, so that a click on a planet, an
        # angle or a sign can reach Python (item 11, 2026-09-15).
        # The mount stands INSIDE this fragment, so the rerun a
        # click causes is a fragment rerun: the tables on the rest
        # of the page are not redrawn to show a panel under a wheel.
        #
        # The envelope carries three things and no more: the SVG the
        # renderer just produced, the width this layout asks for,
        # and the twelve signs' hover text, worked out here from the
        # engine's own tables so that a hover is answered in the
        # browser and never round-trips to Python.
        _picked_wide = wheel_layout == WHEEL_LAYOUT_OPTIONS[1]
        _envelope = {
            "svg": svg_wide if _picked_wide else svg_code,
            "width": "stretch" if _picked_wide else 560,
            "signs": [_sign_hover(i) for i in range(12)],
        }
        if _picked_wide:
            picked = NATAL_WHEEL(data=_envelope, key="natal_wheel",
                                 on_picked_change=lambda: None).picked
        else:
            # st.image draws at the left edge of whatever holds it, so the
            # wheel needs a container that centres its contents. A three
            # column split does NOT do it: a column is a fraction of the
            # page, and the middle of [1, 2, 1] is 454 px at 1400 and
            # 394 px at 1280 -- narrower than the 400 px this replaced,
            # because st.image shrinks a picture to the width it is given.
            # A horizontal container is a flex row instead: its children
            # keep their own width and the row centres them, so the wheel
            # is 560 px at every window width.
            with st.container(horizontal=True, horizontal_alignment="center"):
                picked = NATAL_WHEEL(data=_envelope, key="natal_wheel",
                                     on_picked_change=lambda: None).picked
        _layout_control()
        # Nothing at all until something is clicked, which is why the
        # page's inventory of tables is what it always was.
        _pick_panel(picked)
    _wheel_block()
    if chronocrats.get('Approximate'):
        st.caption(
            "⚠️ **The Lord of the Hour here is not a temporal hour.** No sunrise "
            "or sunset exists for this date at this location (circumpolar day or night), and "
            "the temporal hour is *defined* by the interval between them — so it has no "
            "value at all, and no source in hand contemplates the case. What is shown is an "
            "explicitly modern approximation: the civil day divided into 24 equal hours, "
            "continuing the same Chaldean cycle. The Lord of the Day is still exact."
        )
    # Three sentences, the full page width, each its own caption so it
    # is its own short paragraph and wraps only where the page makes
    # it. Both layouts print the same three, so the page reads alike
    # whichever wheel is drawn.
    _intro = ("A TNAC study companion: cast the chart by hand, then check it here, table by "
              "table, against what the texts say.",
              "The texts are *The Astrology of Sahl b. Bishr*, vol. I, and Abu Ma'shar's *On the "
              "Revolutions of the Years of Nativities* (*Persian Nativities* IV), in Benjamin Dykes's "
              "translations, with his *Great Introduction* as the supplement. Every rule applied on "
              "a page names its sentence.",
              "Enter or load a nativity in the sidebar. Part 1 sets out what the chart contains, "
              "Part 2 what the year holds; the reference tables and the sources close the page "
              "list. The judgment is the astrologer's.",
              "Click a planet or a sign on the wheel for what the tables say of it; hover a sign for its bounds and triplicity lords.")
    # They are read once and then in the way, so they stand open for
    # the first two launches and fold themselves after that, one
    # click from the reader either way. The count is the launches
    # including this one; under the harness, where preferences are
    # neither read nor written, it stays 0 and the three stand open.
    if LAUNCH_COUNT <= 2:
        for _sentence in _intro:
            st.caption(_sentence)
    else:
        with st.expander("About this app", expanded=False):
            for _sentence in _intro:
                st.caption(_sentence)
    # The Lesson 5 worksheet's intermediate lines, so a hand
    # calculation can be checked line by line rather than only at
    # the Ascendant. GST is the Greenwich sidereal time at the UT of
    # birth; LST adds the longitude in hours; RAMC is the right
    # ascension of the meridian from the same swe.houses call that
    # produced the cusps.
    st.subheader('Calculation', help="The intermediate quantities of the chart calculation -- universal time, the Julian day, sidereal time, the RAMC, the obliquity -- so a hand calculation can be checked against the app line by line.")
    gst_hours = swe.sidtime(chart_data['julian_day'])
    lst_hours = (gst_hours + lon / 15.0) % 24.0
    calc_rows = [
        {"Quantity": "Local time", "Value": f"{local_dt:%Y-%m-%d %H:%M:%S}"},
        {"Quantity": "Time standard", "Value": tz_name},
        {"Quantity": "Universal time", "Value": f"{dt_utc:%Y-%m-%d %H:%M:%S} UT"},
        {"Quantity": "Julian Day", "Value": f"{chart_data['julian_day']:.4f}"},
        {"Quantity": "Greenwich sidereal time at birth", "Value": _hms(gst_hours)},
        {"Quantity": "Local sidereal time", "Value": _hms(lst_hours)},
        {"Quantity": "RAMC", "Value": _dms(chart_data['armc'])},
        {"Quantity": "Obliquity of the ecliptic", "Value": _dms(chart_data['obliquity'])},
        {"Quantity": "MC", "Value": get_degree_string(chart_data['mc'])},
        {"Quantity": "Ascendant", "Value": get_degree_string(chart_data['ascendant'])},
    ]
    st.dataframe(pd.DataFrame(calc_rows), hide_index=True, width='content',
                 column_config=_wide_text_columns(pd.DataFrame(calc_rows)))
    pos_col, moon_col = st.columns([2, 1], vertical_alignment="center")
    pos_col.subheader('Planetary Positions', help="The seven classical planets' ecliptic (tropical) longitude at the moment of birth, in sign and degree.")
    with moon_col:
        _reading_checkbox("Moon under the rays to 15°", "moon_rays_15", "_moon_rays_15",
                          help="Sahl, On Nativities 1.19, 6 gives 15 degrees for the Moon; Gr. Intr. VII.2, 61 "
                               "and 72-73 give 12. Affects: the Solar phase column here, and on the Configurations "
                               "page Weakness (93), Planetary Condition and Corruption of the Moon. Full text on the Sources page.")
        _reading_checkbox("Mars under the rays to 18° west", "mars_west_18", "_mars_west_18",
                          help="Dykes's table for Sahl (the chapter head of On Nativities 1.22, with fn 175, which "
                               "reads VII.2, 30's westernizing boundary into 18 degrees) has Mars under the rays "
                               "at 18 west; Sahl's own sentences are silent on Mars west. Gr. Intr. VII.2, 31 puts "
                               "him under the rays at 15 on the western side. Both "
                               "give 18 east. Affects: the Solar phase column here and every test that reads it "
                               "(Weakness 93, Planetary Condition 27/34/45).")
    # True planets only — angles, nodes, and Lot of Fortune
    # now live in the "Calculated Points" table alongside it.
    # The Lesson 3 homework asks for sign/degree/minute AND absolute
    # longitude, whole-sign place, quadrant division, and whether the
    # planet is direct or retrograde -- all of which this app already
    # computes and none of which it showed on the table a student
    # reaches for first. Lesson 16's solar phase is here for the same
    # reason, and Lesson 15's standing instruction -- does the planet
    # see the Ascendant, i.e. is it out of the 2nd, 6th, 8th and 12th
    # -- is the "Sees ASC" column.
    pos_list = []
    for p, d in p_data.items():
        if p == 'North Node':
            continue
        lon_p = d['longitude']
        q = get_effective_house(lon_p, chart_data['houses'])
        phase, side, elong = solar_phase(p, lon_p, p_data['Sun']['longitude'], p_data[p].get('speed_in_lon'))
        acc_p = accidental[p]
        ws_place = get_wsh_house(lon_p, chart_data['ascendant'])
        pos_list.append({
            "Planet": p,
            "Position": get_degree_string(lon_p),
            "Absolute": f"{lon_p:.4f}°",
            "WS place": ws_place,
            "Sees ASC": "No (averse)" if ws_place in (2, 6, 8, 12) else "Yes",
            # Sahl's sense (Ch.3, 4-5: stake or succedent vs. falling), not
            # Abu Ma'shar's quadrant term of VI.26, 3. Cited in the caption.
            "Quadrant": f"{q}, {'advancing' if q in ANGLE_HOUSES | SUCCEDENT_HOUSES else 'retreating'}",
            "Motion": ('Retrograde' if acc_p['Retrograde']
                       else 'Stationary' if acc_p['Stationary'] else 'Direct'),
            "Solar phase": (f"{phase}, {side}" if phase and side else (phase or '–')),
        })
    st.dataframe(pd.DataFrame(pos_list), hide_index=True, width='stretch',
                 column_config=_yes_no_columns(pd.DataFrame(pos_list)))
    st.caption("Quadrant column: Alchabitius house, advancing or retreating in Sahl's sense "
               "(The Introduction Ch. 3, 4-5): stake or succedent versus falling. "
               "Sees ASC: whole-sign aversion to the first place (the 2nd, 6th, 8th and 12th do not see it).")
    points_col, cusps_col = st.columns(2)
    with points_col:
        st.subheader('Calculated Points', help="Non-planetary chart points: the four angles (Ascendant, Midheaven, Descendant, Imum Coeli), the Moon's Nodes, and the Lot of Fortune (a sect-dependent formula combining the Sun, Moon, and Ascendant).")
        north_node_lon = p_data['North Node']['longitude']
        south_node_lon = (north_node_lon + 180.0) % 360.0
        calculated_points = {
            'Ascendant': chart_data['ascendant'],
            'Midheaven': chart_data['mc'],
            'Descendant': chart_data['descendant'],
            'Imum Coeli': chart_data['ic'],
            'North Node': north_node_lon,
            'South Node': south_node_lon,
            'Lot of Fortune': chart_data['lot_of_fortune'],
        }
        calc_list = [{"Point": name, "Position": get_degree_string(lon_val)} for name, lon_val in calculated_points.items()]
        st.dataframe(pd.DataFrame(calc_list), hide_index=True, width='content')
    with cusps_col:
        st.subheader('Quadrant divisions (Alchabitius)', help='The twelve quadrant house cusps computed by the Alchabitius (semi-arc) system -- the app\'s other unit beside the whole-sign places: whole signs where the texts speak of a topic, these divisions where they speak of a planet\'s strength (the five-degree allowance at the four axial degrees).')
        house_list = [{"House": i+1, "Cusp": get_degree_string(chart_data['houses'][i])} for i in range(12)]
        st.dataframe(pd.DataFrame(house_list), hide_index=True, width='content', height=_rows_height(12))
    _finding(_gap, 'Special Degrees & Conditions', None, special_degrees,
              glance='Flags planets in Sahl\'s dark signs (Libra, Capricorn), in the two signs of his burned place ("the end of Libra and the beginning of Scorpio" -- he gives no degrees; Abu Ma\'shar\'s 19 Libra-3 Scorpio is applied in his own Planetary Condition table and, borrowed and labelled, in Sahl\'s condition 110), in a welled degree of their sign (Abu Ma\'shar, Gr. Intr. V.21, Fig. 62), or in one of Sahl\'s two sign-boundary conditions.',
              notes='ENTERING: "every planet which is at the beginning of a sign is weak until it is firmly established in it and comes to be 5 degrees within it" (Fifty Aphorisms #44, 87), repeated in On Nativities Ch. 1.22, 9. This is the other half of the five-degree rule that also governs advancement.\n\nLEAVING: "if a planet came to be in the last degree of the sign, then its strength has already gone away from that sign, and its strength is in the next sign ... like a man putting his foot on the threshold of his door. And if a planet was in the twenty-ninth degree, then indeed the strength of the planet IS in that sign" (Fifty Aphorisms #15, 31-33) -- so the 29th degree still counts and only the 30th has left.')
    _finding(_gap, 'Degrees of nobility and rank', 'Sahl, On Nativities 1.38, 39-41 (Figure 57)', nobility_degrees_data,
              glance='Sahl\'s own table of the degrees in which "the native will reach nobility and rank": a row when the Ascendant, the Sun or the Moon stands in one. Display only; nothing scores it.',
              notes='On Nativities 1.38, 40-41: "If it happened that a native was born and his Ascendant was one of these degrees, or the Moon and Sun were in the equivalent of these degrees (and that is superior if it was the Sun by day and by night the Moon), then he will reach exaltation and power, or he will rule many lands, by the permission of God." Figure 57 of his volume prints the degrees: Aries 19; Taurus 3; Gemini 13; Cancer 1, 13, 14, 15; Leo 5, 7; Virgo 2, 13, 20; Capricorn 12, 13, 20; Aquarius 12, 20 -- none in Libra, Scorpio, Sagittarius or Pisces. The figure prints bare degrees; this app reads them as ordinals, as Figure 64 prints the same rule\'s degrees -- Dykes\'s own resolution of the tables\' cardinal-or-ordinal inconsistency is the end of the numbered degree, 19 for "the nineteenth" (ITA I.3 fn 23), the point at which the ordinal span tested here ends. The whole table is on the Reference tables page, with al-Qabisi\'s third table of the rule named (ITA VII.9, Figure 118). Abu Ma\'shar states the same rule with a table of his own (Gr. Intr. V.22, 4, Figure 64), twelve signs to its eight, six of those eight disagreeing; it is shown under Course text and supplement, on the Configurations page beside Strength and weakness and on the Reference tables page beside this table.')
    _absent(_gap)
    # The orders of the dignities and the good places -- static tables --
    # moved to the Reference tables page on 2026-09-10; what stays is
    # the one table that reads this chart.
    with st.expander("Sahl's sign categories for this chart's points", icon=":material/menu_book:"):
        st.caption("Where The Introduction and On Nativities disagree, both readings are shown and neither is merged. "
                   "Sources: " + "; ".join(f"{k}: {a} / {b}" for k, (a, b) in SIGN_CATEGORY_SOURCES.items())
                   + ". The orders of the dignities and the good places are on the Reference tables page.")
        cat_rows = []
        for p, d in list(p_data.items()) + [('Ascendant', {'longitude': chart_data['ascendant']})]:
            if p == 'North Node':
                continue
            sign_p = get_zodiac_sign(d['longitude'])
            cat_rows.append({'Point': p, 'Sign': sign_p, **sign_categories(sign_p)})
        st.dataframe(pd.DataFrame(cat_rows), hide_index=True, width='stretch', height=_rows_height(len(cat_rows)))

# The delineation findings, off the Chart page (which is the cast) and,
# for Mars by sect, off the Dignities page. Ordered by the source rather
# than by the order they were appended: the course text's findings in the
# order of the Sahl chapter each cites, then the supplement's, grouped by
# author in the order the Sources page names the texts, and the texts it
# does not name after those, the oldest first.
def page_findings():
    if not chart_ok:
        _recovery_panel("Findings")
        return
    st.header("Findings")
    _chart_strip()
    st.caption("Part 1: the nativity. The delineations the texts read off the chart already cast -- "
               "Sahl's own findings first, then the supplement's -- each under the sentence it applies. "
               "Nothing here is scored; the judgment is the astrologer's.")
    _sources_scope_line()
    _readings_note()
    _gap = []
    _finding(_gap, "The fetus's stay (Sahl)", "Sahl, On Nativities 1.8-1.9", gestation_data,
              columns=GESTATION_COLUMNS, height=_rows_height(len(gestation_data)),
              glance="What 1.8 and 1.9 let this app state of the fetus's stay in the belly: the meeting before the birth and its Ascendant (1.8, 5-6), the three Moons of 1.9, 1 and the sentence of 1.9, 2-10 that names their aspects. 1.8's three divisions are framed from a chart the text does not name and are not computed; the rows say what is not. Display only; nothing scores it.",
              notes='On Nativities 1.8, 5-6: "' + SAHL_1_8_5 + ' ' + SAHL_1_8_6 + '" -- the meeting is the last New Moon before the birth; Dykes\'s fn 40 ("' + SAHL_1_8_FN40 + '") allows the lunation generally, so the opposition is shown beside it when that was the lunation nearer the birth. The Ascendant is erected for the hour of the meeting at the birthplace.\n\n'
                    '1.8, 3-4: "' + SAHL_1_8_3 + ' ' + SAHL_1_8_4 + '" Fn 38 on "the degree of the Ascendant": "' + SAHL_1_8_FN38 + '" Dykes\'s comment: "' + SAHL_1_8_COMMENT + '". The sentence does not name the chart whose Ascendant frames the divisions; the pre-conception lunation is not found by any sentence of 1.8 (the conception is the matter of 1.10); so this app lays out no divisions and does not read 7-13. Dykes also notes that 7-9 disagree with Hephaistion (fnn 41-42) and that 10-13 give three of the six permutations.\n\n'
                    '1.8, 1: "' + SAHL_1_8_1 + '"\n\n'
                    '1.9, 1: "' + SAHL_1_9_1 + '" Fn 45: "' + SAHL_1_9_FN45 + '" This app takes the year as the calendar anniversary at the birth hour (a Julian year of 365.25 days only where the anniversary\'s digits name no day), its own reading, and the aspects of the past and renewed Moons to the Moon of the nativity by whole sign; a sentence of 2-10 whose condition holds is a row, and where none holds the row says so.\n\n'
                    '1.9, 2-10: "' + ' '.join(t for _, t in SAHL_1_9_RULES) + '" (fn 47: "' + SAHL_1_9_FN47 + '"; fn 49: "' + SAHL_1_9_FN49 + '"; fn 51: "' + SAHL_1_9_FN51 + '")\n\n'
                    '1.9, 11: "' + SAHL_1_9_11 + '" (fn 53: "' + SAHL_1_9_FN53 + '") -- not computed: the meeting of the conception is not in hand.\n\n'
                    '1.9, 12-14: "' + SAHL_1_9_12 + ' ' + SAHL_1_9_13 + ' ' + SAHL_1_9_14 + '" (fn 54: "' + SAHL_1_9_FN54 + '"; fn 55: "' + SAHL_1_9_FN55 + '") -- the stay by the day and hour is 1.10\'s matter and is not computed here.')
    _finding(_gap, "The Moon on the third day (Sahl)", "Sahl, On Nativities 1.29, 11-12; 1.26, 7", moon_third_day_data,
              columns=MOON_THIRD_DAY_COLUMNS, height=_rows_height(len(moon_third_day_data)),
              glance="The Moon on the third day -- two days after the birth, the birth day counted as the first: her sign and place, whether the sign has four feet (1.26, 7), whether an infortune looks at her, whether she is burned or falling -- \"corrupted\" in 1.29, 3's own terms -- and what 1.29, 11-12 and 1.26, 7 say of that. Display only; nothing scores it.",
              notes='On Nativities 1.29, 11: "' + SAHL_1_29_11 + '"\n\n'
                    '1.29, 12: "' + SAHL_1_29_12 + '"\n\n'
                    '1.29, 13: "' + SAHL_1_29_13 + '" (fn 304: "' + SAHL_1_29_FN304 + '")\n\n'
                    'Dykes\'s fn 303 on 11: "' + SAHL_1_29_FN303 + '"\n\n'
                    '1.26, 7: "' + SAHL_1_26_7 + '"\n\n'
                    'The third day. No sentence of 1.29 or 1.26 says when "the third day of the Moon" is taken; Sahl\'s words elsewhere are "the position of the Moon, where she is on the third day from the nativity" (9, 3) and "the position of the Moon on the third day, the seventh, and the fortieth day" (1.30, 22). This app takes it two days after the birth, the birth day counted as the first (Firmicus, Mathesis II.29, 34, in the nativity of Albinus; III.14, 17-19), the birth hour kept, and computes the Moon, the Sun and the infortunes there. The count rests on his worked chart, the nativity of Albinus: Firmicus gives its places by sign only (II.29, 22), and "on the third day the Moon, being established in Leo, full of light, flung herself into the rays of Mars"; Leo opposes Mars\'s Aquarius by sign on the second day and the third alike, so the count is read by degree from Dykes\'s Figure 34, his approximate chart (fn 129: within a day) -- the Moon at 14 Cancer and Mars at 11 Aquarius at the birth, and the Moon on Mars\'s opposition ray in Leo two days after, sixteen degrees past it after three. That is this app\'s reading of Firmicus, not his statement of the count. Of the third day he says, "and this day, that is the third, operates in a very powerful way in nativities" (II.29, 34), and at III.14, 17-19 that on it "she decrees all things in a similar way" to the first.\n\n'
                    'Corrupted. 1.29, 3 names the corruptions the chapter has in view: "' + SAHL_1_29_3 + '" So the third-day Moon is read as corrupted when an infortune looks at her by whole sign (Saturn and Mars where they stand on that day), when she is burned (within the twelve degrees this app uses for the Moon, The Introduction Ch. 3, 103), or when she is falling from the stakes by the whole-sign place from the Ascendant of the nativity (1.30, 33: "how is her position relative to the Ascendant"). Nothing else of the Moon\'s ten defects is read here.\n\n'
                    'Four feet. 1.26, 7\'s sign is taken from 1.38, 1: "' + SAHL_1_38_1 + '" -- Aries, Taurus, Leo and the second half of Sagittarius. 1.26, 7 is one indicator among the chapter\'s; the row says met or not met and no more.\n\n'
                    '1.29, 11 and 12. The row for 11 reports only its last clause, the third day not corrupted; the lords of the triplicity and the fortune in a stake are not tested in this table. The row for 12 reads "the two infortunes were in the Ascendant or seventh" as both natal infortunes in the whole-sign first or seventh place, this app\'s reading, and reports its first clause; the second clause (the lords of the triplicities withdrawing from the stakes) is not tested here.')
    # The class is the lords' (2.11, 1-3), as Abu 'Ali's twelve charts read
    # it; the Lot decides only when both lords fall (2.3, 6). Rows a text
    # other than Sahl states (2.16, 6, bracketed from BA) show under
    # Course text and supplement only.
    _finding(_gap, "Fortune and livelihood: the seven classes (Sahl)", "Sahl, On Nativities 2.1-2.21",
              [r for r in prosperity_data if READING_DEPTH == READING_DEPTH_OPTIONS[1] or not r['Supplement']],
              columns=['Class', 'Ground', 'Sahl', 'Also'],
              glance="Which of Sahl's seven classes of good fortune and misery the chart falls in, from the two lords of the sect light's triplicity by whole-sign place, the Lot of Fortune when both fall; under it, every further rule of the chapter that the chart meets, each with Sahl's sentence and the parallel in the Book of Aristotle or Abu 'Ali. Display only; nothing scores it.",
              notes="Sahl, On Nativities 2.1, 2-9: \"And good fortune is based on seven approaches: The first of them, on good fortune and how much that good fortune will come to. Second, <on one who> falls from that good fortune. Third, those whose livelihood is middling. Fourth, the rabble [and] those who come down from an ascent to a downfall. Fifth, those who rise up after wretchedness. Sixth, the wretched who do not cease to be in wretchedness. Seventh, those whose profit comes from their own hands.\" Dykes's comment at the head of the chapter: the fourth repeats the second, and the seventh joins profit from one's own hands with violence and injustice (fn 1; 2.21, 3); his table sets them against the Book of Aristotle's III.2.1-III.2.6.\n\n"
                    "The class is read as Theophilus states it in 2.11, 1-3 -- \"" + PROSPERITY_SAHL['2.11, 1'] + " " + PROSPERITY_SAHL['2.11, 2'] + " " + PROSPERITY_SAHL['2.11, 3'] + "\" -- with 2.11, 5, \"" + PROSPERITY_SAHL['2.11, 5'] + "\", and 2.13, 40, \"" + PROSPERITY_SAHL['2.13, 40'] + "\" Strong is a stake or what follows one, falling the third, sixth, ninth and twelfth (fn 149 on \"strong\"), by whole sign. The first lord's time is the beginning of life (2.13, 39), so the first strong and the second falling is the fall, and the reverse the rise. Both in the stakes is 2.3, 2's greatest good fortune; a lord in what follows a stake is 2.3, 18's \"assets and a fine condition, with difficulty in [his] reputation and no fame\". The infortunes with a lord or in its square or opposition are listed and not judged: 2.11, 4 makes their aspect an increase or a subtraction, and Abu 'Ali's charts read the lords' places alone.\n\n"
                    "When both lords fall the reading goes to the Lot of Fortune, 2.3, 6: \"" + PROSPERITY_SAHL['2.3, 6'] + "\" There 2.20, 1-2 confirm the sixth class, 2.3, 7 and 9 raise it to the first, and 2.16, 2 and 4 give the third; for the Lot, its lord and the lords of places, \"made unfortunate\" is 2.20, 1's own gloss, an infortune with it or looking at it from a square or opposition, by whole sign; 2.3, 7's \"eastern or cleansed\" is read as \"and\" (fn 87). Sahl's further indications -- the partnering lord (2.11, 4), the eleventh from the Ascendant (2.3, 12), the motley mixture (2.16, 5; its third place disputed, fnn 225-226), the falling of 2.17 (4, 5, 7, 8, 10, 11), the rising of 2.19 (1, 2, 5), the earnings of 2.21 (1-4) -- are listed under the class with their sentences and do not move it: the chapter gives no order for combining them and the twelve charts apply none. 2.17, 7's and 2.21, 3's eleventh from the Lot of Fortune is Sahl's own; the Book of Aristotle (III.2.1 [1.7]) has it as strong as the eleventh from the Ascendant. The Moon's separation and connection (2.17, 10; 2.19, 2) are read by degree within her orb when the chart carries motions.\n\n"
                    "The fifteen degrees: \"" + PROSPERITY_SAHL['2.13, 48'] + " " + PROSPERITY_SAHL['2.13, 49'] + " " + PROSPERITY_SAHL['2.13, 50'] + " " + PROSPERITY_SAHL['2.13, 51'] + "\" Measured from the axial degree by ascensions (fnn 82-83, 222): oblique ascension from the Ascendant, oblique descension from the seventh, right ascension from the Midheaven and the fourth, the nearest stake behind the lord. Shown as a grade beside the class when the chart carries its meridian and latitude; the class itself stays by whole sign.\n\n"
                    "The Lot's gate is Abu 'Ali's: the reading turns to the Lot when both lords fall, as his twelve charts do; Sahl's 2.3, 6 says \"made unfortunate\", a wider condition this app does not apply. 2.17, 8 states its own precedence (\"even if he was a king\") and is listed, not applied to the class, like every rule of 2.17 and 2.19; 2.3, 19-21 and 2.19, 6 are listed rows on the same footing (BA III.2.4 [4.5] has the stars \"from the east toward the Midheaven\" where Sahl has the bad places). Not read: 2.19, 3-4 and 7-9; 2.17, 6, 12-14 and 2.18; 2.16, 3 except as the grade above; 2.20, 3-6; 2.2's fixed stars; 2.4-2.10 and 2.12-2.15, which are the chapter's other topics.\n\n"
                    "The fixtures are Abu 'Ali's twelve worked charts (PN I, JN Ch. 7, Figures 10-21), each read by whole sign from the positions he prints and held to the verdict he states; the ones he or Dykes reads otherwise are marked in the tests with Dykes's footnote.")
    if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
        _finding(_gap, 'Places harming the eyesight', 'Sahl, On Nativities 6.2, 48-75; Gr. Intr. VI.20; Abu Bakr, On Nativities II.7.3',
                eyesight_places_data,
                columns=['Point', 'Position', 'Place', 'Source', 'Text'],
                standing="Display only",
                glance='The "degrees of chronic illness in the signs" -- the nebulous places named for the Pleiades, the cloud of Cancer, the forehead and sting of the Scorpion, the arrow, the spines and the rope: a row when the Moon, the lord of the Ascendant, the Sun or the Ascendant degree stands in one, each text\'s span under its own source (Sahl\'s four lists, Abu Ma\'shar\'s measured places, Abu Bakr\'s list), none reconciled. Sahl\'s rule names the Moon and the lord of the Ascendant (48), the Moon by night and the Sun by day (69); the Ascendant degree itself is shown beside them as this app\'s addition, and the further conditions each rule attaches -- the infortunes looking, the Moon\'s light, made unfortunate -- are printed in the Text column and are not tested. Display only; nothing scores it; shown under Course text and supplement.',
                notes='Sahl, On Nativities 6.2, 48: "And if you found the Moon in the degrees of chronic illness in the signs, and the infortunes looked at her and their bound, <it indicates> a defect of the eyesight generally, or in the rest of the body: because in the signs are positions which if the Moon is made unfortunate in them, or the lord of the Ascendant, it indicates the corruption of the eye; and that is:" -- then 49-55, the places. 56-57: "If you found the Moon in something of these signs, decreasing in glow, made unfortunate from hostility, then the eyesight will be chronically afflicted. And if she was increasing in glow, full, there will be water in his eyesight, and [uncertain] and [what] resembles that like [uncertain], and his eyesight will not be obscured." Rhetorius\'s list follows (60: "The [degrees] indicative of chronic illness are:", 61-68), which Dykes says "overlap with, but are not identical to, the degrees harming the eyes"; then the Bizidaj (69: "Now as for the degrees which indicate the corruption of vision especially, if the Moon was with them by night and the Sun by day, made unfortunate, that is in the conjunction of:", 70-72); then Nawbakht (74: "And likewise if the Moon was in the middle of Taurus, or in the ninth degree of Cancer, or in the first degree of Sagittarius, for the native will have darkness in his eyes."). Nawbakht\'s 73 (the first degrees of Aries, the last of Capricorn) says the child will be sickly, not that the eyes are harmed, and is not a row.\n\nAbu Ma\'shar, Gr. Intr. VI.20, 1-3: "The positions in the signs which indicate an ailment of the eyes, are [1] the position of the Pleiades in Taurus, [2] the position of the nebula in Cancer, Scorpio (the position of [3] its leg and the position of [4] its stinger), Sagittarius (the position of [5] the arrows), and Capricorn (the position of [6] the spines). And the position of [7] the pour of water from Aquarius also indicates an eruption in the eyes. But as for Libra and Leo, they both sometimes corrupt the vision as well." His longitudes (4-9) differ from Sahl\'s by a few degrees to fourteen, not in one direction (his spines of Capricorn stand before Sahl\'s, the rest after), and 10: "these positions which we have stated are their degrees in longitude and latitude in our time period; but their positions must be searched out and measured for every time period, because they move and withdraw from these degrees which we have stated." Neither table is precessed here: each is applied as printed. Dykes notes (fn 278) that Abu Ma\'shar names the leg where the sting is customary. Libra and Leo (3) carry no degrees and are not rows.\n\nReadings, this app\'s: a degree named as an ordinal or printed bare ("the ninth degree", "from 6° to 9°") is the ordinal degree, as Figure 57 is read, so "the ninth to the fifteenth" is 8°00\'-15°00\'; a longitude measured in minutes is taken as printed, a single one as the whole degree it falls in, and Abu Ma\'shar\'s bare "20°" and "22°" (VI.20, 6 and 8) as measured whole degrees, 20°00\'-21°00\' and 22°00\'-23°00\'. Two spans are this app\'s reading of a phrase: 49\'s "having already passed half [of it] until she completes 18°" as 15°00\'-18°00\', and Nawbakht\'s "the middle of Taurus" as the 15th and 16th degrees. 50\'s bare "(and in 23)" is read as the 23rd degree, the sting (fn 75).\n\nAbu Bakr, On Nativities II.7.3 (p. 238): "And it must be known that in some signs are some degrees which destroy vision: in Taurus, the place of Thurayyā, the sixth, ninth, and tenth degrees. In Cancer, from the ninth degree up to the fifteenth. In Leo, the place of Dafira, the eighteenth degree, the twenty-seventh, and twenty-eighth. In Scorpio, the nineteenth and twenty-eighth. And according to Dorotheus, in Scorpio the eighth degree, the ninth, tenth, and twenty-second. In Sagittarius, the first, seventh, eighth, and ninth degree. In Capricorn, from the twenty-sixth up to the twenty-ninth. In Aquarius, the sixth degree, tenth, and nineteenth." Dykes: "This is the same list as Mash\'allah\'s" (fn 1024, the Book of Aristotle III.6.2), and Dykes, in his Introduction\'s paragraph on the fixed stars, calls the accounts of Dorotheus and Sahl somewhat different from it; this app carries the three lists side by side, each under its own source, and does not reconcile them. Abu Bakr\'s ordinals are read as Sahl\'s are, neighbouring degrees as one span ("the ninth, tenth" of Taurus is 8°00\'-10°00\', "the twenty-seventh, and twenty-eighth" of Leo 26°00\'-28°00\'), and Dorotheus\'s Scorpio degrees, which he gives as a second opinion, are their own rows and say so. The points tested stay the same four -- the Moon, the Sun, the lord of the Ascendant and the Ascendant degree; Abu Bakr\'s own rule sentences in the chapter (the Sun and Moon besieged by the infortunes, the Moon decreased in light in the sixth, the Tail in the degree of the Ascendant, and the rest) are not computed.')
        # Abu Bakr's one paragraph on Mars by sect (II.1.0), whose condition
        # is his own domicile -- the sect of the chart decides which of two
        # sentences reaches him. Supplement only, display only; the other
        # planets have no such witness here and are not built.
        st.subheader("Mars in his own domicile, by sect (Abu Bakr)",
                     help="Abu Bakr, On Nativities II.1.0: Mars in his own domicile (Aries, Scorpio) by night, or by day; Mars in a domicile of Saturn (Capricorn, Aquarius); and, as a second row, Mars in the Midheaven, read as the whole-sign tenth. The sentence for the case is quoted whole; where none reaches him the row says so. Display only; nothing scores it.")
        st.dataframe(pd.DataFrame(mars_abu_bakr_data), hide_index=True, width='stretch',
                     height=_rows_height(len(mars_abu_bakr_data)),
                     column_config=_wide_text_columns(pd.DataFrame(mars_abu_bakr_data)))
        st.caption("Supplement · display only · Abu Bakr, On Nativities II.1.0. The condition is his own domicile by the sect of the chart, "
                   "not his being of or contrary to the sect at large; the fortune's aspect and \"he would rejoice in his own place\" are not tested.")
        with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
            st.markdown("Abu Bakr, On Nativities II.1.0, the paragraph whole: \"" + ABU_BAKR_MARS_II_1_0['Nocturnal'][1] + " "
                        + ABU_BAKR_MARS_II_1_0['Diurnal'][1] + " " + ABU_BAKR_MARS_II_1_0['Saturn'][1] + " "
                        + ABU_BAKR_MARS_II_1_0['Midheaven'][1] + " " + ABU_BAKR_MARS_II_1_0['Fortune'] + "\"\n\n"
                        "Dykes's fn 652, on \"unsound\": \"" + ABU_BAKR_MARS_II_1_0['fn652'] + "\"\n\n"
                        "How this app reads it: his own domicile is Aries or Scorpio, a domicile of Saturn Capricorn or Aquarius, by sign; "
                        "the nativity's being nocturnal or diurnal is the chart's sect as the Chart page states it. The Midheaven is the "
                        "whole-sign tenth, and \"he would rejoice in his own place\" is quoted, not tested -- the text does not say which "
                        "place is meant. \"It was already stated\" points back to an earlier passage of the book, not quoted here. The fortune's "
                        "aspect on \"a Mars so disposed\" is quoted above and not tested. The paragraph is about Mars alone; no other planet "
                        "is read here.")
        _finding(_gap, "The Moon's phase, Valens's eleven", 'Valens, Anthologies II.36 (Riley)', moon_phase_valens_data,
                  standing="Supplement · display only",
                  glance="Valens's eleven phases of the Moon, the chart's Moon placed in one by its angle ahead of the Sun, with what he says the phase indicates and the planet that adds its influence to the day he names. Eight of his boundaries are degrees he gives; the rest are Abu Ma'shar's 12-degree markers of the Moon's phases applied to Valens's, and the notes say which. Display only; nothing scores it.",
                  notes='Valens lists the phases so: "1. New moon; 2. First visibility; 3. Next the crescent moon, 45° from the sun; 4. Next the quarter moon at 90°; 5. Next the gibbous moon at 135°; 6. Next the full moon at 180°; 7. Next the second gibbous phase when it is 45° from full, i.e. 225° <from the sun>; 8. Next the second quarter at 270°; 9. Next the second crescent at 315°; 10. Final visibility at 360°; 11. There is another phase as well, when it first begins to wane."\n\n'
                        'His degrees are moments; this app reads each phase as running from its own degree to the next one\'s, so the crescent is 45-90, the quarter 90-135, the gibbous 135-180, the second gibbous 225-270, the second quarter 270-315 -- his degrees at both ends. The boundaries he does not give are Abu Ma\'shar\'s markers of the Moon\'s phases (Abbr. II.27-31, in ITA II.10.5), where she changes her property at 12° from the conjunction and from the opposition, applied here to Valens\'s phases: the new moon to 12° after the conjunction and the final visibility from 12° before it, the first visibility from 12° to his 45°, the full moon to 12° after the opposition, and the phase "when it first begins to wane" from there to his second gibbous at 225°, where his "What Each Phase Indicates" puts it, between the full moon and the second gibbous. Abu Ma\'shar\'s fourth marker, 12° before the opposition, is not used: Valens\'s gibbous runs to his 180°. The angle is the Moon\'s longitude less the Sun\'s, counted forward.\n\n'
                        'What Each Phase Indicates and What Effects It Has, as Riley has it: "We will append how the preceding phases are to be taken in casting horoscopes and to which god they belong. '
                        'The new moon is indicative of rank and power, of kingly and despotic dispositions, of all public business concerning cities, of parents, marriages, religion, and of all universal, cosmic matters. The rulers of the new moon, of the latitude, and of the motion are indicative of the same things. '
                        'The first visibility of the moon (which is also called its “light”) and its ruler are indicative of life, occupation, and future wealth; in addition, it strengthens the matters influences by the now moon. The ruler of the “light” indicates the overall influences in the same way that the monthly cycles and the universal cycles are observed by means of the first visibility. Mercury adds its influence until day 4 of the moon’s motion. '
                        'The crescent formation is indicative of nurture and expectations in life, of wives and mothers. Mercury adds its influence until day 8. '
                        'The quarter formation is indicative of injuries, diseases, and violent accidents; also of children, status, and good things to come. Venus is configured with the moon until day 12. '
                        'The gibbous phase is indicative of prosperity, future success, travel, and the affinity of relatives. The sun works with the moon until day 14. '
                        'The full moon is indicative of fame and infamy, of travel and violent events, of those who fall from pre-eminence as well as those who rise from a humble state, of affinities, passions, political opposition, and the affinity of parents. This phase has the color of the sign in the Descendant. '
                        'The first ruler of the waning of the light is indicative of the diminishing of resources, of the chilling of occupations, of those who grow humble and lowly, and of sudden falls. This phase has the same influence as the sign which just follows the Descendant. Mars is its ruler until day 21. '
                        'The second gibbous phase is indicative of travel abroad, of great activities, and of prosperity. It has the same influence as <the IX Place of> the God. Jupiter is its ruler to day 25 of the moon. '
                        'The second quarter phase is indicative of old affairs, of chronic diseases, and of children. It has the same influence as… Saturn is its ruler to day 30. '
                        'The ruler of the last crescent is indicative of a wife’s death, of unemployment or robbery. '
                        'Finally, the last visibility is indicative of chains, imprisonment, secrets, condemnation, and infamy. '
                        'The preceding was the arrangement of the moon’s phases, their relationships with the five gods and the sun in the … angles."\n\n'
                        'The Ruler column carries the planet and day only where the sentence names one; the new moon, the full moon, the last crescent and the last visibility have none. "The rulers of the new moon, of the latitude, and of the motion" are not computed.')
        _finding(_gap, "Mercury's phase against the sect",
                  "Firmicus, Mathesis III.7, 7-9 and 26-30 (Dykes's fnn 186, 194)", mercury_phase_sect_data,
                  standing="Supplement · display only",
                  glance="Whether Mercury's phase matches the sect of the chart: a morning star in a diurnal nativity or an evening star in a nocturnal one matches; the other two pairings do not. One row for every chart, in Dykes's words for each case. Display only; nothing scores it.",
                  notes="Firmicus, Mathesis III.7 (Dykes), fn 194, on the figures for the sixth place (26-29): \"In the Figures here I have put the scenarios slightly out of order. In the top row we see the success that comes from Mercury's phase matching that of the chart (morning star-diurnal, evening star-nocturnal). In the second row, mismatches between the phase and sect produce less respected and independent uses of the intellect and skill.\" Fn 186, on the morning star in the second place (7): \"In this case he would be a morning star in a nocturnal chart, so there would be a mismatch between his phase and the sect of the chart.\" The examples: 7-9 for the second place (obscure men; lenders and business men; philologists), 26-30 for the sixth (the greatest fortune from speech, advocacy or business; interpreters, fishermen, sculptors; malign people; those in charge of accounts, banking, granaries, medicines, legal instruments; the scribes of judges). This app reads \"morning star\" as Mercury eastern of the Sun, rising before him, and \"evening star\" as western, the same reading its Solar phase column uses; the sect each phase gives him is Abu Ma'shar's rule, rising before the Sun diurnal and setting after him nocturnal (Gr. Intr. IV.9, in ITA V.11), the rule the Sect table applies. The Reading column gives fn 194's phrase for the matching and the mismatching case.")
        _finding(_gap, "Affliction and fortification after Rhetorius",
                  "Rhetorius Chs. 26-28, 41-42 (Holden)", rhetorius_affliction_data,
                  standing="Supplement · display only",
                  glance="Rhetorius's definitions of a planet's being harmed (Ch. 27's list, with Ch. 41's besieging) or fortified (Ch. 42's list), a row per planet per condition met, and Ch. 26's dominance on its own since that chapter ties it to no harm. Each condition is quoted in the text's words and read as the notes say. Display only; nothing scores it.",
                  notes=("Rhetorius Ch. 27 (Holden): \"" + RHETORIUS_CH27 + "\"\n\n"
                         "Rhetorius Ch. 41 (Holden): \"" + RHETORIUS_CH41 + "\"\n\n"
                         "Rhetorius Ch. 42 (Holden): \"" + RHETORIUS_CH42 + "\"\n\n"
                         "Rhetorius Ch. 28 (Holden): \"" + RHETORIUS_CH28 + "\" Holden's notes name them: the fifth house and the ninth; the eleventh house.\n\n"
                         "Rhetorius Ch. 26 (Holden): \"" + RHETORIUS_CH26 + "\"\n\n"
                         "Rhetorius Ch. 34 (Holden), where Ch. 27's note sends the word: \"" + RHETORIUS_CH34 + "\"\n\n"
                         "The besiegers of an afflicted planet are the malefics, as the definitions gathered in ITA IV.4.2 have it -- Abbr. IV.21-25: \"And there is another kind of misfortune which is called \u201cenclosure.\u201d But this is twofold. First, with some star between two malevolents or between two rays of malevolents, or if it heads from a malevolent to a malevolent. And likewise concerning the rays.\"; al-Qabisi III.28b: \"This is if a planet is in some sign, and in addition a bad one or its rays is in front of it, and a bad one or its rays after it.\" Enclosure by the fortunes is its own row: \"And if a planet or sign were besieged by the fortunes, this will be of the more worthy fortunes\" (Gr. Intr. VII.6, in ITA IV.4.2); BW VIII.76: \"[But if a significator is] from the class of being-in-the-middle [between infortunes], it denotes [prison and torture; if between fortunes], a good condition is going to come.\". What loosens a malefic besieging is the Sun or a fortune aspecting the besieged planet by a friendly aspect with fewer than seven degrees between it and the ray (Gr. Intr. VII.6; al-Qabisi III.28b, both in ITA IV.4.2); what breaks an enclosure by the fortunes is a malefic body or ray in the region (Dykes's comment there). Either is said on the row; a besieging is not silently dropped for a third body of another kind.\n\n"
                         "How this app reads each condition. Where a chapter gives a degree (Ch. 41's seven, Ch. 34's three) it is applied; where it gives none, the condition is read by whole sign and no degree is invented. Malefics are Saturn and Mars.\n\n"
                         + "\n".join(f"- **{c['key']}** ({c['chapter']}), \"{c['text']}\": {c.get('reading') or c['untested']}"
                                     for c in RHETORIUS_AFFLICTION_CONDITIONS)))
        _finding(_gap, "Morin's rules for aspects into good and bad houses",
                  'Morin, Astrologia Gallica 21.II.X (Holden, pp. 105-106)', morin_aspects_data,
                  standing="Supplement · display only",
                  glance='Each trine, sextile, square or opposition that a Fortune (Jupiter, Venus) or an Infortune (Saturn, Mars) casts to another planet, read by the kind of ray and the kind of house it falls into -- the whole-sign house of the aspected planet -- with Morin\'s sentence for that case. Display only; nothing scores it.',
                  notes='Morin, Astrologia Gallica 21.II.X (Holden, pp. 105-106). The chapter\'s opening names the trine, sextile and semi-sextile as the rays "by nature benefic" and the opposition, square and quincunx as those "by nature malefic"; this app\'s aspect table has the four the ancients used (p. 110), so the two weak rays are not read. The four governing sentences, whole:\n\n"The distinction should be observed, however, that the favorable rays of benefic planets are more prone to good, and the unfavorable rays are less prone to evil, than is true for the malefic planets."\n\n"Moreover, a benefic planet\'s favorable rays produce good with ease and in abundance, and cause good in the fortunate houses as well as prevent or mitigate evil in the unfortunate ones, but its unfavorable rays bring difficulties, hindrances, or misfortunes to be surmounted."\n\n"On the other hand, a malefic planet\'s malefic rays are extremely harmful, causing evil in the unfortunate houses and preventing or spoiling the good in the fortunate ones, unless it rules over the location where the adverse aspect falls, for in that case the aspect produces good in fortunate houses, but this good will be accompanied by violence, evil, or misfortune."\n\n"And again, the favorable rays indicate something good gained by difficult means; for example, in the horoscope of the king of Sweden, Saturn ruled the second, and its trine to the Sun in the first house indicated great wealth, which he would acquire through war because Mercury, ruler of the seventh, is placed in the second; and in obtaining these things he had good fortune since Jupiter, Mercury, Venus, and the part of fortune were in the second house—and all ruled in turn by Saturn."\n\nMorin says "the unfortunate houses" without listing them; this app takes the 6th, 8th and 12th as the unfortunate ones and the other nine as fortunate. The equation with Morin\'s phrase is the app\'s; the three are the tradition\'s difficult averse places, as Dykes\'s note on al-Qabisi III.28\'s "cadent from the Ascendant" has it (ITA IV.4.1 fn 43): "That is, being in aversion to it; in a sign which does not aspect the rising sign, particularly the twelfth, eighth, and sixth; the second sign is also cadent from the Ascendant but is not considered as difficult." Where one clause covers both kinds of house (a Fortune\'s adverse rays, an Infortune\'s favorable rays) the Rule column repeats the clause and says so. The "unless it rules over the location" exception is quoted, not tested: the table does not look up the ruler of the house. The chapter goes on to make the aspecting planet\'s own house, its celestial state and its rulership part of the judgment; none of that is read here.')
    _absent(_gap)

def page_dignities():
    if not chart_ok:
        _recovery_panel("Dignities and places")
        return
    st.header("Dignities and places")
    _chart_strip()
    _sources_scope_line()
    _readings_note()
    st.subheader('Lordship Mapping', help="The domicile, exaltation, triplicity, term (bound), and face ruler of each planet's OWN degree -- the five essential dignities, read at the planet's own position rather than another point.")
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    lordship_list = []
    for p, data in p_data.items():
        if p == 'North Node': continue
        rulers = get_essential_rulers(data['longitude'])
        # The planet's own claim at its position, from the labels the
        # dignity evaluation already computed, without the app's
        # point weights ("Domicile (+5)" -> "Domicile").
        own = [re.sub(r'\s*\([+-]\d+\)', '', lbl) for lbl in essential[p]['Essential Labels']]
        lordship_list.append({
            "Planet": p,
            "Position": get_degree_string(data['longitude']),
            "Sign Dispositor": rulers['domicile'],
            "Exaltation Lord": rulers['exaltation'],
            "Triplicity lord": rulers[triplicity_key],
            "Bound lord": rulers['term'],
            "Face lord": rulers['face'],
            "Own dignity here": ", ".join(own) if own else ("Peregrine" if essential[p]['Peregrine'] else "-"),
        })
    st.dataframe(pd.DataFrame(lordship_list), hide_index=True, width='stretch')
    # ---- Sect (Lesson 10) ----------------------------------------
    # The planet's own sect (85's test), its hemisphere, whether it is
    # of the chart's sect, and domain (hayz) under the rule chosen
    # beside the table. The chart's sect itself is the Chart page's
    # header metric.
    st.subheader('Sect', help="Each planet's own sect, whether it stands above the horizon, whether it agrees with the chart's sect (Sahl's testimony 85), and whether it is in its domain (hayz) under the Domain rule chosen beside the table.")
    sect_col, domain_col = st.columns([3, 1])
    with domain_col:
        _reading_radio("Domain (hayz)", DOMAIN_RULE_OPTIONS, "domain_rule", "_domain_rule",
                       help="Gr. Intr. VII.1, 37 / VII.6, 13: sign gender fixed to the planet's own; "
                            "Masha'allah, On Nativities 1.23, 17: gender follows the hemisphere. "
                            "Affects: this Sect table, Dignity Evaluation below, and Planetary Condition "
                            "(13) on the Configurations page. Full text on the Sources page.")
    with sect_col:
        sect_rows = []
        for p, data in p_data.items():
            if p == 'North Node': continue
            own_diurnal = planet_sect_is_diurnal(p, data['longitude'], p_data['Sun']['longitude'])
            above = (data['longitude'] - chart_data['ascendant']) % 360 > 180.0
            sect_rows.append({
                "Planet": p,
                "Planet's sect": 'Diurnal' if own_diurnal else 'Nocturnal',
                "Above horizon": 'Yes' if above else 'No',
                "Of the chart's sect": 'Yes' if own_diurnal == (sect == 'Diurnal') else 'No',
                "Domain (hayz)": 'Yes' if accidental[p]['Hayz'] else 'No',
            })
        st.dataframe(pd.DataFrame(sect_rows), hide_index=True, width='stretch', height=_rows_height(len(sect_rows)),
                     column_config=_yes_no_columns(pd.DataFrame(sect_rows)))
    st.caption("Sect: Sahl, The Introduction Ch. 3, 85. Domain: Gr. Intr. VII.1, 37 and VII.6, 13 "
               "(or Masha'allah, On Nativities 1.23, 17, per the switch).")
    st.subheader('Topical Planets in Houses', help="Each planet's whole-sign house placement with BOTH readings for that pairing, good and bad, as the TNAC Reference Guide for the Planets and Places (Dykes, 2023) summarises them: its Rhetorius column from Rhetorius Ch. 57 and Firmicus, Mathesis III.2-III.13 (both texts are now in hand; the Guide's summary is still what the table prints, and it has not yet been checked against them), its PN IV column from Book II's lord of the year in the places, which the Guide applies to natal planets -- a reading of the Guide's, followed here.")
    st.caption("Rhetorius & PN IV, as the Reference Guide summarises them; the Guide prints ? for the Moon in the sixth and the eighth, and so does this table.")
    st.dataframe(pd.DataFrame(planets_in_houses_data, columns=['Planet', 'Placed in (WS place)', 'Lean']),
                 hide_index=True, width='content', height=_rows_height(len(planets_in_houses_data)))
    # The readings wrap in st.table; the structural columns stay above.
    with st.expander("Rhetorius / PN IV readings for these placements", expanded=READING_DEPTH == READING_DEPTH_OPTIONS[1]):
        st.table(pd.DataFrame(planets_in_houses_data,
                              columns=['Planet', 'Net', 'Standing', 'If Well Placed', 'If Badly Placed']),
                 hide_index=True)
    with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
        st.markdown("Neither is chosen for you. The only thing available to choose with is the Net from the Planetary Condition table, and that number is this app's own arithmetic -- Abu Ma'shar enumerates the VII.6 conditions, never totals them, gives no weighting and no tie rule. An invented score silently picking one of two classical delineations turns a convenience into a verdict.\n\nThe Net is shown as a LEAN instead, and reads Indeterminate within a margin of one, which is the width of a single testimony: those charts sit one label away from the opposite reading, and should be judged on the condition counts and the labels rather than on the number.")
    st.subheader("Topical House Lords (Masha'allah)", help='For each of the twelve topical houses, its domicile lord\'s own whole-sign placement, and Masha\'allah\'s delineation for that [placed-in, rules] pairing, as the TNAC Reference Guide for the Planets and Places (Dykes, 2023) summarises Sahl, On Nativities\' lords-of-places chapters (1.36, 78-97; 2.14; 3.10; 4.11; 5.1; 6.3.4, 12-24; 7.1; 8.5; 9.4; 10.2.4; 11.1; 12.1) -- the classical way of reading what a house\'s ruler is "doing" elsewhere in the chart.')
    # Averse: the lord sits in the 2nd, 6th, 8th or 12th sign from the
    # house it rules, so it does not see its own place.
    lords_rows = [{**{k: v for k, v in r.items() if k != "Masha'allah Signification"},
                   'Averse to its place': 'Yes' if (r['Placed in (WS place)'] - r['Topical House']) % 12 in (1, 5, 7, 11) else 'No'}
                  for r in house_lords_data]
    st.dataframe(pd.DataFrame(lords_rows), hide_index=True, width='content', height=_rows_height(len(lords_rows)),
                 column_config=_yes_no_columns(pd.DataFrame(lords_rows)))
    st.caption("Masha'allah's condition is his own, stated at the end of every lord-of-the-Nth section: \"Work in this chapter "
               "if the lord of the third and the third [itself] were free of the infortunes, and the fortunes do not witness\" "
               "(On Nativities 3.10, 14; likewise 4.11, 24; 6.3.4, 24; 7.1, 217; 9.4, 35; 10.2.4, 13; 11.1, 28; 12.1, 47). "
               "Whole-sign: an infortune with, square or opposite the house or its lord; a fortune in any aspect or assembly. "
               "It is met on about one row in ten; the readings are shown regardless, with the column saying whether he would apply them.")
    with st.expander("Masha'allah readings for lord placements", expanded=READING_DEPTH == READING_DEPTH_OPTIONS[1]):
        st.table(pd.DataFrame(house_lords_data,
                              columns=['Topical House', 'Domicile Lord', 'Placed in (WS place)', "Masha'allah Signification"]),
                 hide_index=True)
    with st.expander("Planetary Dignity Evaluation (Hellenistic/Rhetorius reconstruction)", expanded=READING_DEPTH == READING_DEPTH_OPTIONS[1]):
        dignity_list = []
        for p in essential.keys():
            ess = essential[p]
            acc = accidental[p]

            dignity_list.append({
                "Planet": p,
                "Net": ess['Essential Score'] + acc['Accidental Score'],
                "Ess": ess['Essential Score'],
                "Acc": acc['Accidental Score'],
                "Essential Dignities": ", ".join(ess['Essential Labels']) if ess['Essential Labels'] else "-",
                "Accidental Conditions": ", ".join(acc['Accidental Labels']) if acc['Accidental Labels'] else "-",
            })

        df_dignity = pd.DataFrame(dignity_list).sort_values(by="Net", ascending=False)
        st.dataframe(df_dignity, hide_index=True, width='stretch')
        st.caption(
            "The point weights are this app's own ranking convenience -- no source in hand "
            "totals these conditions. The geometry each test uses is sourced. **Solar phase** "
            "follows Abu Ma'shar's walk through the synodic cycle (VII.2); Sahl's *On Nativities* "
            "1.22 and al-Biruni give the under-the-rays figures independently (Sahl states no burn "
            "boundary, and his Mars westernizes at 18°, not 15°): burned to "
            "6° for Saturn and Jupiter, 10° for Mars, 7° for Venus and Mercury, "
            "6° for the Moon; under the rays to 15°, 18° east / 15° west, "
            f"12° east / 15° west, and {MOON_RAYS_ORB:.0f}° for the Moon; in the heart within 16' "
            "(VII.2, 7-9, from the Sun's own apparent diameter). Sahl elsewhere says one whole "
            "degree for the heart, and that reading is used where his own testimonies are "
            f"scored. **Domain/hayz** follows the Domain switch beside the Sect table above, currently {DOMAIN_RULE}: "
            + ("VII.1, 37-39 and VII.6, 13 -- the planet's own sect need not match the chart's; "
               "the hemisphere requirement is what flips with it."
               if DOMAIN_RULE == DOMAIN_RULE_OPTIONS[0] else
               "On Nativities 1.23, 17 -- a male planet by day above the earth in a male sign, by "
               "night under the earth in a female sign; the feminine planets by hemisphere only.")
        )

def page_configurations():
    if not chart_ok:
        _recovery_panel("Configurations")
        return
    st.header("Configurations")
    _chart_strip()
    _sources_scope_line()
    _readings_note()
    _gap = []
    # The connection rule and the fitting infortune govern tables on every
    # tab, so they stay above the tabs. The three-way view control went on
    # 2026-09-10: the Sources shown reading (Sources page) decides where Abu
    # Ma'shar's tables sit -- a tab of their own under Course text, or
    # beside Sahl's on the same topic under Course text and supplement.
    rule_col, fit_col = st.columns([1.1, 1.9], vertical_alignment="bottom")
    with rule_col:
        # Governs only the dual-author tables; each author's own
        # tables pin their own rule (see doctrine()). The essay
        # comparing the two rules is on the Sources page.
        _reading_radio("Connection test used in the shared tables", CONNECTION_PROFILES.keys(),
                       "connection_rule", "_connection_rule",
                       help="Which author's test decides Connected in the aspects, reception and "
                            "prevented-connections tables. Sahl: the applying planet's own light. "
                            "Abu Ma'shar: 15° in one sign, 12° for aspects. Full comparison on the Sources page.")
    with fit_col:
        _reading_checkbox("Fitting infortune: the malefic that rules the Ascendant is not counted as an infortune (Choices Ch. 1, 12)",
                          "fitting_infortune", "_fitting_infortune",
                          help="Sahl, Choices Ch. 1, 12: \"that infortune was good for him, because the infortunes are "
                               "perhaps more fitting for him, since [one] may be the lord of the original Ascendant\" -- "
                               "against his own 1, 16-17, so off by default. When on, that malefic drops out of every "
                               "'afflicted by an infortune' test in these tables (Sahl's enclosure, strength and weakness "
                               "94-95; Abu Ma'shar's 3, 47-50 and enclosure; the Moon's 67-68 and 106).")
    if FITTING_INFORTUNE:
        st.caption(f"Fitting infortune in force: {SOFTENED_INFORTUNE} rules the Ascendant and is not counted as an infortune."
                   if SOFTENED_INFORTUNE else "Fitting infortune switched on, but no malefic rules this Ascendant -- nothing changes.")
    supplement = READING_DEPTH == READING_DEPTH_OPTIONS[1]

    def sahl_aspects():
        _finding(_gap, "Aspects, aversions and connections",
                 f"Sahl, The Introduction Ch. 2, 50-60 and Ch. 3, 6-21 — {CONNECTION_PROFILE} rule in force", aspects,
                  columns=['Light Planet', 'Aspect', 'Heavy Planet', 'Connecting planet', 'Motion', 'Orientation', 'Exact Orb Dist', 'Bodies', 'Strength', 'Connection', 'Rules differ'], height=_rows_height(len(aspects)),
                  column_help={
                      'Connecting planet': "Which planet's own motion is closing the aspect, and the one it closes with: "
                                           "the light planet \"connects with\" the slower one (Sahl, The Introduction Ch. 3, 6; "
                                           "Gr. Intr. VII.5, 9). Retrogradation reverses it, and the cause is named in the cell.",
                      'Motion': "Applying is the approach, \"going straightaway to\" the connection (Sahl, The Introduction "
                                "Ch. 3, 6); Separating is the recession, the light planet's degree moving away from the heavy "
                                "one's (22). The kinetic fact alone, not the verdict.",
                      'Connection': "Applying: connected and still approaching (Sahl, The Introduction Ch. 3, 6; Gr. Intr. "
                                    "VII.5, 9-11). Under a single blanket: past exact and still connected, the light planet "
                                    "not yet departed by half of its body (Sahl 7-10). Not yet: configured but not connecting "
                                    "by the relevant degrees, \"only wanting to be connected\" (Sahl glossary, Applying). "
                                    "Separated: past the window (Sahl 10; glossary, Separation). A dash: in aversion, so not "
                                    "configured at all.",
                      'Orientation': "Dexter, Dykes's right: the ray cast to earlier degrees of the zodiac; sinister, his "
                                     "left: to later ones (Sahl glossary, Right/left).",
                  },
                  caption="A separating pair stays connected inside Sahl's window (The Introduction Ch. 3, 7–10), "
                          "which is why Connecting planet, Motion and Connection can differ in one row.",
                  glance='Four separate facts about each pair, kept apart rather than collapsed into one verdict. LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign.',
                  notes='MOTION and EXACT ORB DIST are the degree-to-degree approach. BODIES is whether each planet falls inside the other\'s sphere of power, which is asymmetric because the spheres differ in size: Abu Ma\'shar VII.4, 7 notes that Saturn sits inside the Moon\'s body from 12 degrees while she only enters his at a little under 9. CONNECTION is the active author\'s verdict, named as his own text names the state -- switch the Connection rule at the top of this page to see where they disagree; RULES DIFFER marks the pairs where the two tests disagree.\n\nSTRENGTH is two different measures. For an assembly it is the source\'s own: whose body reaches whose (VII.4, 5-8) and whether they share a bound. For an aspect it is marked "(app scale)", because VII.5, 4 grades looking as a continuum with no cutoffs anywhere -- "the strongest thing there is in its looking is the degree related most closely by number to the degree of its own sign, and if the aspect was far from these degrees, its aspect will be weaker." The thirds are this app\'s own scanning aid; the measurement itself is the Exact Orb Dist column.\n\nLIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.\n\nCONNECTING PLANET is the separate, directed fact: which one is actually closing the aspect. Normally it is the lighter, and Ch. 3, 6 assumes as much ("a light, quick star GOING STRAIGHTAWAY TO a heavy star ... FEWER IN DEGREES than the heavy one"). Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma\'shar VII.5, 24 ("the connection of one of them with the other ... will be BY RETROGRADATION"), VII.5, 118 ("the light one IN MORE DEGREES goes retrograde and connects with the heavy one"), and the note on VII.5, 130 (Saturn "could never be received because he is too slow to connect with anyone, UNLESS BY RETROGRADATION"). The cause is named in this column whenever the heavier planet is the one applying, which happens for about 4% of configured pairs. Reception, transfer, collection, returning, revoking, emptiness of course and enclosure all read this column, not the light/heavy one.')

    def sahl_connection_group():
        with st.container(border=True):
            st.markdown("**Connection group** — Ch. 3, 24-30 and 119-123")
            _finding(_gap, 'Transfer of Light', "Sahl, The Introduction Ch. 3, 24-27; Type II is Gr. Intr. VII.5, 84-85", transfers,
                      glance='A faster "carrier" planet separates from one planet and connects with another, carrying the first planet\'s nature to the second -- Type I is a direct hand-off, Type II is via an intermediate planet already connecting onward.')
            _finding(_gap, 'Collection of Light', 'Sahl, The Introduction Ch. 3, 28-30', collections,
                      glance='Two planets not connected to each other both connect with a single heavier planet, which "collects" their combined power -- often read as a third party or authority resolving/mediating between two unconnected significators.')
            _finding(_gap, 'Enclosure', 'Sahl, The Introduction Ch. 3, 119-123', enclosure_data,
                      glance='A planet separating from one of the two infortunes (or, per Abu Ma\'shar\'s extension, fortunes) and connecting with the other, with neither leg intercepted by a third planet\'s rays -- graded "more powerful/unfortunate" when both legs are within 7 degrees of exact.')
            _absent(_gap)

    def sahl_handing_over():
        with st.container(border=True):
            st.markdown("**Handing-over group** — Ch. 3, 49-76")
            _finding(_gap, 'Handing Over', 'Sahl, The Introduction Ch. 3, 70-76', handing_over_data,
                      glance='Three grades of one phenomenon, per connected pair: Management is the baseline (any connection at all); Power is added when the giving planet is itself in its own house, exaltation, or triplicity; Nature is added when the planet it connects with is the ruler')
            _finding(_gap, f"Reception — {CONNECTION_PROFILE} rule", None, reception_data,
                      glance='Who receives whom, on what dignity, which way round, and how strongly. The two authors differ on every one of those, so the Connection rule at the top of this page governs here too. Under Sahl\'s rule a pair refused by non-reception Kind II (the connection made from the receiver\'s fall) is not also listed as received -- refusal wins, as on Sahl\'s own chart (Questions Ch. 1, 63 with 40-41) -- and a pair of Kind IV (the receiver in its own fall) keeps its row marked brought down, which is 62\'s own word.',
                      notes='SAHL (Ch. 3, 49-55) runs one way only -- the connecting planet stands in a dignity of the planet it connects with, and so is received by it (52: the Moon in Aries connecting with Mars, "he receives her because Aries is his house"). House or exaltation is perfect reception; triplicity alone is expressly ranked below it (50); bound counts only paired with triplicity, which Sahl credits to Masha\'allah (54-55). Face never appears, and a connection is always required.\n\nABU MA\'SHAR (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in REVERSE where the accepting planet sits in the connector\'s dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).\n\nHe then classes reception a SECOND way, and under his rule the table shows both. DIGNITY QUALITY is 129-133, the local basis. OVERALL CLASS is 136-142: "a [2] middling reception is the planets\' reception of each other from the house, exaltation, bound, triplicity, or face" (140) -- house and exaltation included -- while "if two met [together] from this, or each one of them received its associate, it is a strong reception" (141); the natural acceptances of 134-135 are "[3] below that" (142); the Moon received by the Sun (137) and a planet received by Mercury from Virgo (139) are his named strong forms, and the Sun receiving the Moon from the opposition keeps his own word, "detestable" (137). A lone domicile reception is therefore the strongest basis AND globally middling: both are true, and they are different questions.\n\nSahl has two further forms, both under his profile only. 56, RECEPTION AT ONE REMOVE: "if the Moon was connecting with a planet and that planet was connecting with the lord of the house of the Moon or its exaltation, then the Moon is received" -- the note there calls it "like a transfer of light which indirectly allows for reception." Both legs are read in Sahl\'s directed sense of connecting (6: "going straightaway to ... going towards"), since separating is his separate term at 22.\n\n57, AFTER THE SIGN CHANGE: "if the Moon was empty in course, and then she passed over into the next sign and connected with the lord of her first sign, it is JUST LIKE RECEPTION; and if she connected with a planet OTHER than [that], IT UNDERMINES HER." Both halves appear -- the undermining is a finding, not a blank.\n\nAn empty table is NOT non-reception -- that is a separate set of hostile configurations, in the table below.')
            _finding(_gap, 'Non-reception', 'Sahl, The Introduction Ch. 3, 58-62', non_reception_data,
                      glance="Five named ways a connection is refused rather than received (Sahl, The Introduction Ch. 3, 58-62), a distinct finding from simply lacking reception; the Kind column numbers them and the notes spell each one out. Under Sahl's rule Kind II overrides any reception for the same pair (only a minor one is possible there; Questions Ch. 1, 63 with 40-41), and Kind IV marks the pair's reception brought down without removing it (62).",
                      notes="Sahl's A -> B model: A is the connecting (applying) planet, B the planet it connects with.\n\nKind I (58): B holds no essential dignity at all at A's position -- B is alien in A's sign, so A is not recognised.\n\nKind II (59-60): A stands in B's own sign of fall, \"like one who comes to it from the house of its enemies.\"\n\nKind III (61): A is in its OWN fall and B has no house or exaltation there to rescue it -- \"as though the one asking is offering defeat.\"\n\nKind IV (62): B is in its own fall, which brings the connection down whatever A's condition.\n\nKind V (62): B sits in A's own sign of fall.")
            _finding(_gap, 'Returning', 'Sahl, The Introduction Ch. 3, 65-69', returning_data,
                      glance='Manner I: a planet connects with a retrograde planet or one under the rays -- it "returns to it what it accepted," corrupting the question.',
                      notes='Manner II: an angular (faster) planet hands over to a cadent (slower) one -- the matter has a beginning but no end.')
            _absent(_gap)

    def sahl_prevented():
        # The Handy Tables give Lesson 17 ONE table here, headed
        # "Prevented connections" and listing blocking, resistance,
        # cutting #1, escape, revoking and cutting #2 together. This
        # showed them as separate tables, so a student could not lay
        # the app beside the course's own page. Merged on the shape
        # they share -- who is prevented, from what, by whom -- with
        # the source kept per row.
        prevented = []
        for r in blocking_data:
            # Sahl Ch.3, 35-48; VII.5, 90-94 -- cited in the caption.
            prevented.append({'Kind': r['Type'], 'Planet': r['Blocked'],
                               'Prevented From': r['From Reaching'],
                               'By': r['Blocked By'], 'Because': r.get('Standing', '')})
        for r in cutting_data:
            prevented.append({'Kind': 'Cutting ' + r['Type'], 'Planet': r['Planet'],
                               'Prevented From': r.get('Other Contact', ''),
                               'By': r.get('Yields To', ''),
                               # Types I and II are Abu Ma'shar's own (VII.5, 121-124);
                               # only Type III and the nullification are in Sahl
                               # (Ch.3, 31-34 and 44-48; VII.5, 120, 125). Both are
                               # cited in the table's caption.
                               'Because': r.get('Because', '')})
        # The Handy Tables' own "Prevented connections" also lists
        # revoking, resistance and escape -- but those are Abu
        # Ma'shar's (VII.5, 117-119), and pulling them in here would
        # put his material inside a Sahl group and undo the author
        # separation. They stay on his side, under Forward-looking
        # conditions. This is a deliberate divergence from the
        # course's single table, and the only one in this grouping.
        with st.container(border=True):
            st.markdown("**Prevented connections** — Ch. 3, 31-48, with Abu Ma'shar's two further cuttings")
            _finding(_gap, 'Prevented connections', "Sahl, The Introduction Ch. 3, 31-48; Gr. Intr. VII.5, 90-94 and 120-125", prevented,

                     glance="Ways of stopping a connection before it completes, in one table: Sahl's intervention, nullification and cutting, plus Abu Ma'shar's two further cuttings (VII.5, 121-124), which Sahl does not have. His revoking, resistance and escape are in his own section.")
            _finding(_gap, 'Banished', 'Sahl, The Introduction Ch. 3, 64', banishment_data,
                      glance='"The banished planet is the planet which none of the planets connects to" (64) -- a planet outside every live connection, whatever the signs are doing. Each row shows the nearest configured planet and why that is not a connection.',
                      notes='Sahl\'s definition is about CONNECTIONS (6-21), not signs: a planet can be in trine by sign with everyone and still be banished if no planet is inside a live connection with it, and it can hold an out-of-sign body connection (20-21) and not be banished at all. Abu Ma\'shar\'s later "wildness" (VII.5, 79-82) is a different, whole-sign test -- aversion to every planet -- and has its own table in his view. Dykes\' note on 64 calls Sahl\'s the earlier, less precise form; the two are kept apart rather than one served under both names.')
            _absent(_gap)

    def sahl_strength():
        with st.container(border=True):
            st.markdown("**Strength and weakness** — Ch. 3, 77-112")

            # Each tick grid, with its answer key, its notes and the
            # row detail a selection opens, is one @st.fragment:
            # selecting a row reruns that grid's block alone, the way
            # a wheel control reruns _wheel_block(). Everything the
            # fragment draws is drawn inside _tick_grid, inside its body.
            @st.fragment
            def _strength_grid_block():
                _tick_grid(_gap, 'Strength of the Planets', 'Sahl, The Introduction Ch. 3, 78-88', strength_data,
                           'Strength Testimonies', STRENGTH_COLUMNS,
                           glance="The eleven testimonies of a planet's strength at the time of judgment (Sahl, The Introduction Ch. 3, 78-88), one column per testimony; the answer key under the grid spells each one out in words.",
                           notes='Testimonies 78 and 83 look similar but are different measurements. 78 is whole-sign, narrowed to the six places that LOOK at the Ascendant. 83, advancing, is DYNAMIC -- read against the Alchabitius quadrant cusps, since the note on 83 says the word means "dynamically angular or succeedent, i.e. by primary motion with respect to the angular axes, and not by whole sign." A planet leaving an angle is withdrawing even while its whole sign is still angular, so the two disagree for about a third of placements.\n\n83 also carries Sahl\'s FIVE-DEGREE RULE: "the planet will not be falling from the stake unless it was 5 degrees distant from its rear -- I mean, if the stake was 10 degrees of Aries, then every planet which has less than 5 degrees between it and the stake is truly counted as being in the stake" (Fifty Aphorisms #44, 88), which he states again in On Nativities Ch. 1.22, 9. A planet a few degrees short of an angle is therefore angular, not cadent; the row says so when that is why it qualifies. It moves about 5% of placements, all of them cadent-to-angular. Sahl states the rule twice for the stakes and once for every house (On Nativities 1.18, 19: "and likewise in all of the houses"); this app reads that as the four stakes only, the course\'s reading, Lesson 3 §4-5, adopted here.\n\nDistinct from the Abu Ma\'shar-based Planetary Condition table, which scores a broader, later scheme.')

            @st.fragment
            def _weakness_grid_block():
                _tick_grid(_gap, 'Weakness of the Planets', 'Sahl, The Introduction Ch. 3, 91-100', weakness_data,
                           'Weakness Testimonies', WEAKNESS_COLUMNS,
                           glance="The ten testimonies of a planet's weakness at the time of judgment (Sahl, The Introduction Ch. 3, 91-100), one column per testimony; the answer key under the grid spells each one out in words.",
                           notes="The ten (91-100): falling and averse to the Ascendant (the 6th or 12th), retrograde, under the rays, connecting with an infortune by assembly, square or opposition, enclosed between both infortunes, in its own fall, connecting with a falling planet or separating from a would-be receiver, alien (no house, exaltation or triplicity where it sits), with the Node and no latitude, or inverted (in detriment). Distinct from the Abu Ma'shar-based Planetary Condition table in his view, which scores a broader, later scheme.")

            _strength_grid_block()
            _weakness_grid_block()
            _ab = ascensional_bands
            _finding(_gap, "The sect light's first triplicity lord by ascensional band -- and the app's generalisation",
                     "Sahl, On Nativities 2.13, 48-51 (fn 189: Carmen I.28, 1-6); Fifty Aphorisms #45, 90-92 with fn 57, as printed and not applied",
                     _ab['rows'] or [{'Refused': _ab['refused']}],
                     glance=("2.13, 48: \"if the first lord of the triplicity of the glowing one is in a stake or what follows it, "
                             "and that is the 15 degrees which follows it, by degrees of ascensions ... it indicates praise and good "
                             "fortune (and what is less [than that] in degrees is preferable)\"; 49 the second 15, \"below the "
                             "first\"; 50 the third, \"the middle of assets\"; 51 \"what is after that in degrees, up to the next "
                             "stake, is of the nativities of the poor\". Stated for ONE planet, the sect light's first triplicity "
                             "lord (fn 190), and applied to it in the last column"
                             + (f" -- here {_ab['first_lord']}: {_ab['judged']['judgment']}" if _ab['judged'] else '') + "."),
                     notes=("THE APP'S ANGULAR-PROXIMITY GRADE, GENERALISED FROM SAHL, ON NATIVITIES 2.13, 48-51: the per-planet column "
                            "applies 2.13's distances to every planet, which no text does -- an ordinal preference, no score; "
                            "Aphorism #45 with fn 57 is credited for the universal-band analogy and Carmen I.28 for \"the more that it "
                            "is closer to the degree of the stake, the more elevated\". APHORISM 45 AS PRINTED: \"every planet which "
                            "is [distant] from the stake in what follows it, by 15 degrees, is in the situation of one who is in the "
                            "stake; and if it increases [beyond that], then it does not have strength\" (90-92; the example 10 to 25 "
                            "Aries). Dykes, fn 57: \"misstated here\" -- the source (Carmen I.28, 1-7; 2.13, 48-51 \"repeated "
                            "correctly\") measures ascensions. Shown as printed in its own column, not applied; a different rule from "
                            "2.13 (every planet, angular strength, one band) and not harmonised with it; the editor's ascensional "
                            "correction of the aphorism is not applied. CONVENTIONS, "
                            "this app's: the stake a planet FOLLOWS (zodiacally behind it: 2.13 \"what follows it\", Introduction "
                            "2, 33 \"rising up to them\"); oblique ascension at the horizon (the setting degree by the oblique "
                            "descension) and right ascension at the meridian, a split Carmen's single rising instruction does not "
                            "state; the ecliptic degree, latitude ignored; bands end-inclusive at 15, 30 and 45, truncated by the "
                            "next actual stake; the five-degree allowance (Aphorism #44) lies on the other side of the stake and is "
                            "not inherited. Refused where the ascension has no inverse (above the polar circle). The printed Carmen I.28, 3-6 "
                            "(p. 108) has the same four parts band for band; Sahl says \"the first lord\", Carmen \"the lord\"."))
            _finding(_gap, 'Right-sidedness, "the spear-bearing of the planets"',
                     'Sahl, On Nativities 2.5, 1-3: a finding table, no score', right_sidedness,
                     standing="Display only",
                     glance=("2.5, 2: a pair in square or sextile, both in their exaltations or houses (or one in each, or one of "
                             "them in one of its shares), each casting rays upon the other -- \"a strong right-sidedness\"; 3: "
                             "not in their houses or exaltations but both of one sect -- \"also called right-sidedness (though it "
                             "is below [the first version])\"; 1: especially the diurnal planets by day and the nocturnal by night."),
                     notes=("Readings, the app's: \"casting rays upon its companion\" = the pair is Connected under the "
                            "Configurations page's connection rule; \"one of its shares\" = a triplicity, bound or face held by "
                            "the partner of a planet in its house or exaltation; \"of the sect of the day or ... night\" = both "
                            "planets of one sect, Mercury not counted. A second stated definition, the honor-guard of 10.2.1, "
                            "10-15, is the next table; no text in hand arbitrates between the two definitions, so both are "
                            "shown and neither enters a score. Rhetorius Chs. 23-25 (the doryphory in three kinds: an "
                            "angular planet in its house or exaltation looked at by another in its own; a planet of the "
                            "sect in another's house looking at an angular luminary, before the Sun and after the Moon; "
                            "the out-of-sect kind; the trine and square stronger than the sextile) and Ch. 53 (what each "
                            "planet's doryphory of the Sun gives) are witnesses to the doctrine and arbitrate neither."))
            _finding(_gap, 'The honor-guard, "and it is spear-bearing"',
                     'Ptolemy in Sahl, On Nativities 10.2.1, 10-15: a finding table, no score', honor_guard,
                     standing="Display only",
                     glance=("10: the planets \"formed an honor-guard for [the luminaries] (and that is if the planets were eastern "
                             "from the Sun and western from the Moon)\"; 10-15 read the luminaries' signs (male or female), their "
                             "stakes, the guards' stakes and whether they look at the luminaries, into ranks from \"an elevated "
                             "king\" to \"weak with toil\" -- the delineation is not pronounced here, the facts are shown."),
                     notes=("Readings, the app's: \"eastern from the Sun\" = rising before him (the solar phase's side); "
                            "\"western from the Moon\" = rising after her, by the shorter arc; \"in the stakes\" = the whole-sign "
                            "places 1, 4, 7, 10 (rank is a topic, so the sign-places); \"look at\" = the whole-sign aspect. "
                            "Examples in 10.2.7 are not reproduced."))
            _finding(_gap, 'Corruption of the Moon', 'Sahl, The Introduction Ch. 3, 103-112', moon_corruption_data,
                      glance="Sahl's own ten defects of the Moon, item [16] of his sixteen -- a different list from Abu Ma'shar's eleven corruptions in the Planetary Condition table.",
                      notes="Sahl's ten (103-112): burned within 12 degrees of the Sun; in her own fall or connecting with a planet in its own fall; approaching the Sun's opposition within 12 degrees; assembled with, square or opposed by an infortune, or enclosed between the two; with the Head or Tail in one sign under 12 degrees; in Gemini or in the sign's last bound; falling from the stakes or connecting with a planet that is; in the burned path, the end of Libra and beginning of Scorpio; wild, empty of course; slow, or waning in light.\n\nAbu Ma'shar's eleven (VII.6, 63-74) are not a variant of this list. He has eclipse, the twelfth-part of Saturn or Mars, southern latitude and the ninth house, none of which Sahl lists; Sahl has her own fall, connection with a fallen planet, and wildness, none of which appear there. His list is scored in the Planetary Condition table, this one is not scored anywhere.")
            _absent(_gap)

    def abu_condition():
        st.subheader('Planetary Condition', help="Each planet checked against Abu Ma'shar's conditions in Gr. Intr. VII.6, kept in his own four groups: good fortune (1-20), strength (21-29), weakness (30-46), misfortune (47-62), plus, for the Moon only, HIS OWN eleven corruptions (63-74).")
        st.caption("Gr. Intr. VII.6")
        _reading_radio("VII.6, 27/45 'eastern/western relative to the Sun'", EASTERN_RULE_OPTIONS,
                       "eastern_rule", "_eastern_rule",
                       help="'hemisphere': the whole half, excluding the rays (VII.2, 2; VII.6, 34). "
                            "'VII.2 band': only the easternizing and westernizing bands (VII.2, 14-31). "
                            "Affects: Planetary Condition (27, 45). Full text on the Sources page.")
        condition_list = []
        for p, cond in abu_mashar_condition.items():
            condition_list.append({
                "Planet": p,
                # VII.6's own four sections, kept apart: the chapter
                # enumerates these separately and never totals them.
                "Good Fortune": cond['Good Fortune'],
                "Strength": cond['Strength'],
                "Weakness": cond['Weakness'],
                "Misfortune": cond['Misfortune'],
                # str, not int-or-'': a column mixing the two is an
                # object column that Arrow rejects.
                "Moon Defects": str(cond['Moon Defects']) if cond['Moon Defects'] else '',
                "Good Fortune / Strength": ", ".join(cond['Positive Labels']) if cond['Positive Labels'] else "-",
                "Weakness / Misfortune": ", ".join(cond['Negative Labels']) if cond['Negative Labels'] else "-",
                # Last, and labelled app arithmetic in the caption:
                # VII.6 never totals its conditions.
                "Net": cond['Net'],
                "Verdict": cond['Condition'],
            })
        df_condition = pd.DataFrame(condition_list).sort_values(by="Net", ascending=False)
        st.dataframe(df_condition, hide_index=True, width='stretch', height=_rows_height(len(df_condition)))
        st.caption(
            ":orange[**Net and Verdict are this app's heuristic, not Abu Ma'shar's.**] He enumerates these "
            "conditions; he nowhere adds them up, and VII.6 gives no weighting and no tie rule. They are kept "
            "beside the Dignities page, which prints both the good and the bad Rhetorius/PN IV reading for each "
            "placement and chooses neither, showing this Net as a lean; a Net of zero is Indeterminate on both "
            "pages. Read the four counts and the labels themselves in preference to the single number."
        )
        with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
            st.markdown("The Moon's eleven corruptions (63-74) are shown as their own count rather than folded in with the rest. Sahl's ten (The Introduction Ch. 3, 103-112) are a different list, not a variant reading of this one, and have their own table, Corruption of the Moon, in the Sahl view: Abu Ma'shar has eclipse, the twelfth-part of Saturn or Mars, southern latitude and the ninth house, none of which Sahl lists; Sahl has her own fall, connection with a fallen planet, and wildness, none of which appear here.\n\nThe four counts and the labels are the report. NET and VERDICT are a convenience of this app and NOT Abu Ma'shar's: he enumerates the conditions but never totals them, and the chapter supplies no weighting and no rule for ties. They are kept because Topical Planets in Houses on the Dignities page prints both the good and the bad reading for every placement and chooses neither: this Net is shown there as a lean, and a Net of zero is Indeterminate in both places.\n\nTwo distortions in the raw count are corrected so that one fact cannot vote repeatedly: the Moon's eleven corruptions contribute a single entry (as their own checklist they had been dragging her to a Bad verdict about three times as often as any other planet), and multiple reception rows for one planet likewise count once.\n\nEnclosure here is Abu Ma'shar's own (56-62) -- by degree within 7 degrees either side counting rays as well as bodies, by sign in the 2nd and 12th, or separating from one encloser and connecting with the other -- and it can be DISSOLVED: the degree type when the Sun or a fortune casts a ray within 7 degrees of the enclosed planet (60), the sign type by any look from them (61). The standalone Enclosure table in the Connection group of the Sahl view is Sahl's separate version.\n\nThe by-sign type counts an encloser's RAYS as well as its body, which is what 58 says twice. Be aware that this makes it common: it fires on roughly 43% of placements, because a planet's rays reach eight of the twelve signs. A bodies-only variant at about 2% exists in the code (SIGN_ENCLOSURE_BODIES_ONLY) but is this project's own conjecture, not the text, so it is off.")

    def abu_natural():
        _finding(_gap, 'Natural connections', "Gr. Intr. VII.5, 53-77", natural_connections,
                  columns=['Pair', 'Family', 'Degrees', 'From exact', 'Motion', 'Affinity (76-77)', 'Ordinary aspect', 'Standing'],
                  glance='"Another type of connection and separation [even] without the planets\' looking at each other" (53): pairs standing in signs of equal ascensions (56) or of equal daylight (67-75), whose degrees correspond as complements within the sign -- 12 Gemini to 18 Capricorn (62). A relation of its own, not an aspect and not a dignity: the Ordinary aspect column keeps saying Aversion where that is what the signs are.',
                  notes='EQUAL ASCENSIONS (56): "Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and Sagittarius, Leo and Scorpio, and Virgo and Libra." EQUAL DAYLIGHT (67-75), the antiscia: Gemini-Cancer, Taurus-Leo, Aries-Virgo, Libra-Pisces, Sagittarius-Capricorn, exactly as he lists them -- Aquarius-Scorpio completes the standard scheme but is not enumerated here and is not added (see the coverage note on the Sources page).\n\nDEGREES: "when a planet is in the first degree of Aries, then it is in the nature of a planet which is at the last degree of Pisces" (57); "the planet which is in 12° of Gemini is in the nature of the degree of the planet which is in 18° of Capricorn: so when it passes beyond 12° of Gemini, then it has separated from it" (62). So the counterpart degree runs backwards as the planet runs forwards, and MOTION is read from both speeds together. He gives no orb: every planet in Aries is in the nature of some degree of Pisces, so every pair in a listed sign pair is shown with its distance from exact.\n\nAFFINITY: 76-77 single out four pairs of each family as bridging an ordinary aversion -- Gemini-Capricorn, Sagittarius-Cancer, Aries-Virgo, Libra-Pisces "is called a natural connection by opposition" (76); Gemini-Cancer, Virgo-Libra, Sagittarius-Capricorn, Pisces-Aries "the natural connection by sextile" (77). The notes there record that he omits Aries-Scorpio, Taurus-Libra and Aquarius-Capricorn; they are not added.\n\nThe same sign pairs are one of 134\'s four bases of acceptance, in the Reception table under his rule.')

    def abu_wildness():
        _finding(_gap, 'Wildness', "Gr. Intr. VII.5, 79-82", wildness_data,
                  glance='A planet in whole-sign Aversion to all six other classical planets -- "in a sign such that absolutely no planet looks at it" (79) -- though it may still be "reached" via the lord of whatever bound it occupies (80-81).',
                  notes='Whole-sign and independent of degree. Sahl\'s "banished" (Ch. 3, 64) is a different test, about live connections rather than signs, and has its own table in his view.')

    def abu_reflection():
        _finding(_gap, 'Reflection of Light', "Gr. Intr. VII.5, 87-89", reflections,
                  glance="Collection or Transfer specifically between two planets that are in Aversion to each other, not just unconnected -- since Aversion pairs can't see each other at all, a third planet is the only way their natures can interact.")

    def abu_favor():
        _finding(_gap, 'Favor & Recompense', "Gr. Intr. VII.5, 126-128", favor_recompense_data,
                  glance='A planet in its own Fall or a welled/pitted degree, pulled out of that weak condition by a connecting dispositor (Favor). Recompense is the same planet later returning the favor, found by simulating the chart forward.')

    def abu_rays():
        _finding(_gap, "Rays cast by ascensions (Ptolemy's method as reported by Abu Ma'shar, Gr. Intr. VII.7)",
                  "Gr. Intr. VII.7, 1-22", rays_by_ascension_data,
                  glance="Where each planet's sextile, square and trine rays fall once the ascensions of this latitude are taken into account, beside the zodiacal aspect the rest of these tables use. A static quantity of the chart, not a direction; VII.7, 1-2 attributes the method to Ptolemy. Nothing else reads it yet.",
                  notes="VII.7, 3-13: the planet's distance from the nearest stake in seasonal hours, from the right ascensions and the hourly times of its degree (or of the opposite degree on the nocturnal side). 14-15: two candidate ray positions, one from the right ascensions, one from the ascensions of the city (fn 252: the oblique ascensions). 16-19: when they differ, a sixth of the excess for every hour of distance is added to the candidate NEAREST the planet (left rays); 20-21: for right rays the same, to the more DISTANT candidate. The nearest/distant flip is in the text and unexplained; the function takes it as written and can be asked for either reading. 22: \"as for the opposition, [a planet] casts its ray into the opposition of its sign, in the same degree and minute.\" The tables the chapter presupposes (fn 250-251) are computed from the obliquity and the latitude.",
                  height=_rows_height(len(rays_by_ascension_data)))

    def abu_book_v():
        _finding(_gap, 'Book V degrees', "Gr. Intr. V.22, Figs. 63-64", book_v_degrees_data,
                  standing="Supplement · display only",
                  glance='Two degree tables from Book V that no condition in VII.6 reads: the seven "degrees increasing in good fortune" (for the Moon, the Lot of Fortune and the Ascendant) and the thirty-one "degrees of elevation and power" (for the Ascendant and the luminary of the sect). Shown when a named point falls in one; never scored. Sahl states the second rule with a table of his own (On Nativities 1.38, 39-41, Figure 57), eight signs to Figure 64\'s twelve, six of the eight disagreeing; his is on the Chart page, and both are on the Reference tables page.',
                  notes='V.22, 1-2: "when planets indicate the native\'s good fortune by means of their positions, and the Moon or the Lot of Fortune is in these degrees, or [these degrees] are exactly on the Ascendant, then they will increase in the native\'s good fortune. And if they indicate downfall, then these will instigate some motion towards high rank and power." V.22, 4: "if the Ascendant was one of these degrees ... or the Sun by day or the Moon by night was in one of them, and they were in an excellent position of the circle, and the planets of the root of the nativity indicated good fortune, then they will make him attain nobility and the houses of kings." Ordinal degrees, as in the wells. Leo 5 and Aquarius 20 are in both tables; Aquarius 17 is a degree of elevation and a well.')

    def abu_forward():
        # The horizon is the simulation's own, not a number retyped here:
        # every sentence on this finding -- including the one printed when
        # it has no rows at all (F07) -- says the same number the search
        # actually ran to.
        _horizon = int(sim['horizon_days'])
        _finding(_gap, 'Forward-Looking Conditions', f'Revoking, Resistance, Escape — next {_horizon} days', forward_looking_data,
                  absent=f"No qualifying event found within {_horizon} days of the chart; later events were not evaluated.",
                  glance=f'Conditions describing what happens as the chart moves forward in time (up to ~{_horizon} days), not the birth moment alone.',
                  notes=f'Each chapter prescribes an ORDERED SEQUENCE of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when. A condition not found inside {_horizon} days is reported as not found, never as a negative finding.\n\nREVOKING (117): "a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it." The window is now birth to the applicant\'s first station: perfection inside it means nothing was revoked.\n\nRESISTANCE (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one BY RETROGRADATION, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead. All five steps are required and timed.\n\nESCAPE (119): the planet being applied to leaves its sign first; the applicant then follows across the SAME boundary on its own next crossing, and is captured by a body it meets in the new sign. Dykes\' note on Fig. 139 is the picture: Mercury slips from Virgo into Libra, Venus follows, and Saturn\'s body catches her there.')

    def abu_block(parts):
        with st.container(border=True):
            st.markdown("**Gr. Intr. VII.5-6** (supplement)")
            for part in parts:
                part()
            _absent(_gap)

    # --- Five chapters, or four with the supplement laid beside the text ---
    # In the page's own order: the aspects and the connection group;
    # handing over and reception; the prevented connections; strength
    # and weakness. Abu Ma'shar's tables join the topic they belong to
    # when the depth says so -- his natural connections, wildness,
    # reflection and rays with the aspects; favor and recompense with
    # reception; revoking, resistance and escape with the prevented
    # connections (the Handy Tables' own grouping for Lesson 17, kept
    # in his own bordered block so the author separation stands); his
    # planetary condition and Book V degrees with strength and weakness.
    _labels = ["Aspects & Connections", "Handing Over & Reception", "Prevented Connections",
               "Strength & Weakness"] + ([] if supplement else ["Abu Ma'shar (Supplement)"])
    # Client-side tabs (owner, 2026-09-10, third pass): no key, no
    # rerun. A click switches instantly, and the frontend keeps the
    # chapter across reruns caused by other controls on the page;
    # leaving the page and coming back opens the first chapter. The
    # earlier version remembered the chapter across pages by rerunning
    # the whole script on every click, which the owner saw as a
    # flicker. To have the memory back at the price of the rerun:
    # key=, on_change set to rerun, default=_reading(...) and _persist().
    _tabs = st.tabs(_labels)
    with _tabs[0]:
        sahl_aspects()
        sahl_connection_group()
        if supplement:
            abu_block([abu_natural, abu_wildness, abu_reflection, abu_rays])
    with _tabs[1]:
        sahl_handing_over()
        if supplement:
            abu_block([abu_favor])
    with _tabs[2]:
        sahl_prevented()
        if supplement:
            abu_block([abu_forward])
    with _tabs[3]:
        sahl_strength()
        if supplement:
            abu_block([abu_condition, abu_book_v])
    if not supplement:
        # The Book V degrees stay behind the supplement (owner,
        # 2026-09-13): Sahl's own table of the second rule is on the
        # Chart page, and the tab here is the course text's.
        with _tabs[4]:
            abu_block([abu_condition, abu_natural, abu_wildness, abu_reflection, abu_favor, abu_rays,
                       abu_forward])
    _absent(_gap)

def page_lots():
    if not chart_ok:
        _recovery_panel("Lots")
        return
    st.header("Lots")
    _chart_strip()
    _sources_scope_line()
    _readings_note()
    st.subheader('Classical Lots', help='Lots: sect-dependent formulas combining two planets or points with the Ascendant to derive a new sensitive degree tied to a specific topic (e.g. Fortune = body/livelihood, Spirit = mind/action).')
    # Formula from the same LOT_DEFINITIONS text the Topical Lots
    # table carries (via calculate_topical_lots), so the two cannot
    # differ; Basis has no definition row and says so.
    formula_by_lot = {r['Lot']: r['Formula'] for r in topical_lots}
    classical_rows = []
    for r in classical_lots:
        row = {k: v for k, v in r.items() if k != 'Standing'}
        row['Formula'] = formula_by_lot[r['Lot Name']]
        row['Standing'] = r['Standing']
        classical_rows.append(row)
    st.dataframe(pd.DataFrame(classical_rows), hide_index=True, width='stretch', height=_rows_height(len(classical_rows)),
                 column_config=_wide_text_columns(pd.DataFrame(classical_rows)))
    with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
        st.markdown('Fortune and Exaltation are stated in Sahl. Spirit -- the Lot of the Invisible, which Sahl names -- is stated at Gr. Intr. VIII.3, 28-29: by day from the Moon to the Sun, by night the reverse, from the Ascendant. Basis is stated at Gr. Intr. VIII.4, 22-24 as "the Lot of firmness and survival, the Lot of the Ascendant\'s support" (fn 67: the Greek Basis): by day from Fortune to the Invisible, by night the contrary, from the Ascendant -- the same construction as Sahl\'s Lot of passion (7.1, 141) and Abu Ma\'shar\'s Lot of Venus, with which VIII.4, 24 says it coincides. All four carry their provenance under Provenance and standing per Lot, below the Topical Lots table.')
    st.subheader('Topical Lots (Sahl, On Nativities)' + ("; three rows of Abu Ma'shar's" if READING_DEPTH == READING_DEPTH_OPTIONS[1] else ''), help="Sahl's topical Lots, each with its own provenance. He gives several of them MORE THAN ONCE, with formulas that genuinely conflict, and Dykes's apparatus does not silently reconcile them -- so neither does this table.")
    _reading_radio("House-based Lots measure to the", LOT_HOUSE_CUSP_OPTIONS, "lot_house_cusp", "_lot_house_cusp",
                   help="'The second place', 'the degree of the eighth place', 'the ninth' (On Nativities 2.15, 1; "
                        "8.6, 1; Ch. 9, 9): the Ascendant's degree carried into that sign, or the Alchabitius cusp. "
                        "Affects: this table only. Full text on the Sources page.")
    # Fortune, Spirit and Exaltation are in the Classical Lots table
    # above, with the same Formula; the provenance columns are in the
    # expander so the table itself is the worksheet.
    # A row flagged Supplement (Abu Ma'shar's: a form of a Lot Sahl also
    # gives, or a Lot of his Sahl has not) is shown only under Course text and supplement.
    _lots_supplement = READING_DEPTH == READING_DEPTH_OPTIONS[1]
    _classical = ('Lot of Fortune', 'Lot of Spirit', 'Lot of Exaltation', 'Lot of Basis')
    topical_rows = [r for r in topical_lots if r['Lot'] not in _classical
                    and (_lots_supplement or not r['Supplement'])]
    st.dataframe(pd.DataFrame(topical_rows, columns=['Topic', 'Lot', 'Position', 'WS place', 'Lord', 'Formula', 'Active']),
                 hide_index=True, width='stretch', height=_rows_height(len(topical_rows)))
    # The four classical Lots keep their POSITIONS out of the table above --
    # they have their own table at the top of this page -- but their
    # provenance belongs here, which is where the classical note sends the
    # reader (F11), and their definitions carry the same three fields every
    # other Lot's does. Nothing new is written for them.
    provenance_rows = [r for r in topical_lots if r['Lot'] in _classical] + topical_rows
    with st.expander("Provenance and standing per Lot"):
        st.table(pd.DataFrame(provenance_rows, columns=['Topic', 'Lot', 'Standing', 'Source', 'Editor’s note']),
                 hide_index=True)

    with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
        st.markdown('The STANDING column records his editorial position in his own words where he states one.\n\nFour kinds of case. SAHL HIMSELF RULES: of the two sibling Lots, "both of the Lots are correct, so work with them both together" (3.11, 4) -- neither is subordinate. DYKES NAMES HIS CHOICE: of the three witnesses to the Lot of enemies, "I have used M here"; on the night reversal of the Saturn-Moon work Lot, "Paul instructs us to reverse it by night, but Abu Ma\'shar says not to. We should follow Paul." DYKES MARKS ONE STANDARD: on children, "the usual calculation ... is that of Hermes." DYKES ONLY TABULATES: three Lots for work, after noting that "Sahl quietly switches to Masha\'allah\'s treatise on Lots ... without telling us that the formula is different."\n\nEvery formula is taken from the running prose or a footnote, never from one of the summary tables.\n\nThe Lot of death is projected from Saturn: STATED by Abu Ma\'shar (Gr. Intr. VIII.4, 226; VIII.6, 69), and Sahl 8.6, 1 as printed agrees, his manuscripts reading the Ascendant (fn 89, with Masha\'allah\'s manuscripts and Dorotheus for Saturn). A stated rule with a manuscript variant, not an emendation.')
def page_victors():
    if not chart_ok:
        _recovery_panel("Lunation and victors")
        return
    st.header("Lunation and victors")
    _chart_strip()
    st.subheader('Prenatal Lunation (Syzygy)', help='The New or Full Moon before birth: its degree, its natal place, the five lords of the degree and the governor among them (Sahl, On Nativities 1.7, 3-7), with this app\'s approximation and the almuten beside it.')
    r = syzygy['rulers']
    triplicity_str = (
        f"{syzygy['active_triplicity_lord']}\u2605 ({syzygy['active_triplicity_label']}) \u00b7 "
        f"Day: {r['triplicity_day']} \u00b7 Night: {r['triplicity_night']} \u00b7 Part: {r['triplicity_participating']}"
    )
    syzygy_rows = [
        {"Metric": "Event Type", "Value": syzygy['event_label']},
        {"Metric": "Position", "Value": get_degree_string(syzygy['syzygy_longitude'])},
        {"Metric": "Natal House", "Value": f"House {syzygy['natal_house']}"},
        {"Metric": "Domicile Lord", "Value": r['domicile']},
        {"Metric": "Exaltation Lord", "Value": r['exaltation']},
        {"Metric": "Triplicity Lords", "Value": triplicity_str},
        {"Metric": "Term Lord", "Value": r['term']},
        {"Metric": "Face Lord", "Value": r['face']},
        {"Metric": "Governor of the syzygy degree (Sahl, On Nativities 1.7, 3-7)",
         "Value": f"{syzygy_governor['governor']} -- {syzygy_governor['how']}"},
        {"Metric": "This app's approximation of 1.7 (one point a listed condition)",
         "Value": syzygy_governor['model_how']},
        {"Metric": "Almuten by 5/4/3/2/1 points (al-Qabisi's weights, ITA I.18; a technique not in Sahl)",
         "Value": f"{syzygy['almuten']} (Score: {syzygy['almuten_score']})"},
    ]
    st.dataframe(pd.DataFrame(syzygy_rows), hide_index=True, width='stretch',
                 column_config=_wide_text_columns(pd.DataFrame(syzygy_rows)))
    with st.expander("Governor of the syzygy degree: the five lords under 1.7, 3-7"):
        st.dataframe(pd.DataFrame(syzygy_governor['rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(syzygy_governor['rows'])))
        st.caption("Sahl, On Nativities 1.7, 3: \"you will know the one in charge of that portion from five things: the "
                   "lord of the house, triplicity, exaltation, bound, and image, and the eastern one of them -- if [one] had "
                   "superior claims over the rest of them\"; 4: \"Then see which of them is stronger in its [own] place, and "
                   "is direct in course, looking at the sign of the meeting or opposition\"; 7: \"if they were both in power "
                   "equally, [then] whichever of them was in a stake or in its own house, triplicity, bound, or exaltation, "
                   "and had superiority over its associate in this respect, that is the governor.\" [Sahl I p. 265]. "
                   "THE VERDICT names a planet only where the text's clear subcases decide, and otherwise says "
                   "\"unresolved\" with each candidate's profile: the five lords of the degree (the sect's triplicity lord) "
                   "are the candidates; a retrograde one, or one not looking at the syzygy's sign (the same sign or a "
                   "whole-sign aspect), is not eligible (4, read as eligibility); 3's \"the eastern one\" is a preference "
                   "among the claim-holders, not a veto -- a western candidate is set aside only by an eastern one with at "
                   "least as many claims on the degree; the SUN is a claim-holder whose side relative to himself is not "
                   "applicable, so 3 neither prefers nor sets him aside, and a contest that only easternness would decide "
                   "against him is left unresolved; 7 is kept as a profile, not a score -- a candidate with a listed "
                   "advantage (a stake; own house, exaltation, triplicity or bound; the image is not in 7's list) beats one "
                   "with none, and two that each hold one are left unresolved, the text stating no ranking among them and "
                   "1.20, 2-4's ranking of the lords being stated for the house-master, not borrowed here. NOT MODELLED: "
                   + SAHL_1_7_UNMODELLED + ". READINGS: \"in a stake\" is read by the DIVISION (Alchabitius, the five "
                   "degrees at the four axial degrees), the convention Dykes proposes for strength language (ITA "
                   "Introduction §6, quadrant divisions for power; Alchabitius this app's choice among them) -- the text's own word "
                   "for the stakes is the counted sign, \"the sign of the Ascendant, the fourth, the seventh, and the "
                   "tenth\" (The Introduction Ch. 2, 31); the Moon's side is the same rising-before-the-Sun rule as the "
                   "planets', the texts not defining her easternness for this procedure (Gr. Intr. VII.2, 4 names her right "
                   "and left, not \"eastern\"; al-Qabisi bridges the two words, the superiors from the Sun's rays to his "
                   "opposition being called eastern and right, ITA II.10.1, al-Qabisi III.8); the target degree is the "
                   "lunation's and every condition is read in the "
                   "NATAL chart, extending the natal context of Dykes's comment to 3-7, whose moment the text does not "
                   "state. THE APPROXIMATION row is " + SAHL_1_7_MODEL_DISCLOSURE + "; the almuten row is the 5/4/3/2/1 "
                   "weighting al-Qabisi states (ITA I.18: the lord of the domicile five strengths, of the exaltation "
                   "four, of the triplicity three, of the bound two, of the face one; Dykes's fn 210 there, only the "
                   "primary triplicity lord scoring), a technique not in Sahl. Where the three differ, the difference "
                   "is the finding.")
    st.subheader('Victor of the Chart', help="Ibn Ezra's victor worksheet (his book is not in hand), reproduced cell for cell so it can be checked against a hand-filled sheet. The weights and the five places are al-Qabisi's -- ITA I.18, the five dignities' points, and ITA VIII.1.4 (al-Qabisi IV.7), the victor over the native from the Ascendant, the two luminaries, the Lot of Fortune and the prenatal syzygy; the worksheet's Day, Hour and Places rows are ibn Ezra's. Dykes's standing critique of the weighting (ITA I.18 fn 211): with the Dorothean triplicities and the Egyptian bounds, and only the primary triplicity lord scoring, the victor is always the domicile or the exaltation lord but for a few degrees of Pisces (Mars) and of Cancer (Venus). The seven planets are the columns.")
    st.caption("ibn Ezra's victor #1, 1485/1537")
    # The two same-tradition pairings are the grids a student fills
    # in; the two off-diagonal pairings are the cross-check.
    def _victor_grid(scheme_name, res):
        st.markdown(f"**{scheme_name}** — victor: **{res['victor']}** ({res['total']}), runner-up {res['runner_up']}"
                    + ("  \n:orange[Tied at the top — the sheet does not break ties.]" if res['tied'] else ""))
        st.dataframe(pd.DataFrame(res['grid']), hide_index=True, width='stretch', height=_rows_height(len(res['grid'])))
    for scheme_name, res in victors_data.items():
        if 'matched preset' in scheme_name:
            _victor_grid(scheme_name, res)
    with st.expander("Cross-check: the two unmatched weight/place pairings"):
        for scheme_name, res in victors_data.items():
            if 'matched preset' not in scheme_name:
                _victor_grid(scheme_name, res)

    with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
        st.markdown('The first five rows score each planet\'s essential-dignity claim AT THAT POINT\'S degree -- Sun, Moon, Ascendant, Lot of Fortune, and the prenatal New/Full Moon. Then Lord of the Day (+7), Lord of the Hour (+6) and Places are added ONCE each, not per point; Places is keyed the other way round, by the candidate planet\'s own whole-sign house. Every column is summed into Totals, and the single highest total is the chart\'s victor.\n\nTWO INDEPENDENT AXES, and all four combinations are shown. The dignity weights are Older (al-Tabari/Masha\'allah, Bound 3 > Triplicity 2) or Newer (al-Qabisi/Abu Ma\'shar, Triplicity 3 > Bound 2); the Places wheel is ibn Ezra\'s own or Masha\'allah\'s. The "Older" attribution is kept as its source prints it; the one passage in these texts that gives \'Umar\'s weights -- Abu Bakr, On Nativities II.5.14, through al-\'Anbas -- has triplicity 3 and bound 2, the "Newer" order; al-Qabisi knows the other order without naming its authors ("certain people put the bound before the triplicity", Introduction I.22), so only the attribution is unwitnessed here. Nothing in the source says which wheel goes with which weighting, so pairing each with the wheel of its own named tradition is a reading, not a fact -- those two are labelled "matched preset" and the two off-diagonal combinations, previously not computed at all, are shown beside them. Where all four agree the victor is robust; where they part, the disagreement is the finding. Ibn Ezra\'s later victor #2 (1507) replaces the two chronocrator rows with a Superiors row scored only for Saturn, Jupiter and Mars; its weight is stated in no text in hand, so it is not implemented rather than guessed.')
def page_timing():
    if not chart_ok:
        _recovery_panel("Timing")
        return
    st.header("Timing")
    _chart_strip()
    st.caption("Part 2: prediction. Every rule on this page comes from Abu Ma'shar, "
               "*On the Revolutions of the Years of Nativities* (*Persian Nativities* IV), "
               "cited as Book.chapter, sentence -- except the releaser and the house-master, which "
               "PN IV leaves to another book of Abu Ma'shar's: \"the book which we worked on concerning "
               "nativities\" (IX.8, 123), his *Book of the Judgments of Nativities* (Bodleian Hunt. 546, "
               "fn 315), not in hand, and not the *Great Introduction*, which has only the Lot of the "
               "releaser. They are taken from Sahl, *On Nativities* (the chapter named The Releaser, cited "
               "by that book's chapter and sentence). Al-Qabisi's own account of the releaser and the "
               "house-master (ITA VIII.1.3, al-Qabisi IV.4-6) is in hand and stands beside Sahl's in the "
               "Sources page's coverage table, not built. What neither book settles is listed at the foot of "
               "the page rather than filled in.")
    _sources_scope_line()

    # --- The year under examination (2026-09-10) ----------------------
    # The target lives here, where it is used, not in the sidebar with
    # the nativity. Its store keys are read at the top level (the
    # bundle is computed before this page runs); the widgets here
    # write them through _persist, as the readings do.
    st.subheader("The year under examination",
                 help="Every table on this page keys on completed civil anniversaries (II.3, 1: "
                      "\"for every year the native has completed\"). Set the year as an age or as a "
                      "date; the other is read back beside it. Remembered across pages and saved "
                      "with the chart.")
    t_mode, t_value, t_read = st.columns([1, 1.4, 2.6])
    with t_mode:
        _reading_radio("Target by", TARGET_MODE_OPTIONS, "target_mode", "_target_mode",
                       help="Age: the completed years, i.e. the birthday that opens the year. "
                            "Date: any civil date; its completed years are shown beside it.")
    with t_value:
        if target_mode == TARGET_MODE_OPTIONS[1]:
            # "Past the table" is a state the page reports, not an error, so
            # the ages run as far as the ephemeris does -- and no further
            # (H2): the box had no upper bound at all, and an age that
            # carried the birthday past the ephemeris raised before any page
            # was drawn. The bound is this chart's own, counted from its
            # birth year.
            st.session_state.setdefault("target_age", int(target_age))
            st.number_input("Age (completed years)", min_value=0, max_value=max_target_age(input_date),
                            step=1, key="target_age")
            _persist("target_age", "_target_age", target_age)
        else:
            st.session_state.setdefault("target_date", target_date.isoformat())
            st.text_input("Target date (YYYY-MM-DD)", key="target_date")
            _persist("target_date", "_target_date", target_date.isoformat())
            if parse_iso_date(st.session_state.get("target_date", target_date.isoformat())) is None:
                st.error(f"Not a YYYY-MM-DD date; keeping {target_date:%Y-%m-%d}.")
        # A target the ephemeris cannot reach, from either box: the last
        # valid one stands and this says so, where the target is set.
        if target_range_note:
            st.error(target_range_note)
    with t_read:
        _sr_dt = pn4_datetime_from_jd(pn4['jd_sr'])
        st.markdown(
            f"**{target_date:%Y-%m-%d}** -- age **{target_age}** completed "
            f"(born {input_date:%Y-%m-%d}; the {pn4_ordinal(target_age)} birthday opens this year).  \n"
            f"The revolution of the year fell on **{_sr_dt:%Y-%m-%d}** UT; the target is in month "
            f"**{pn4['month']}** of 12.")

    # --- Six chapters (2026-09-10, second pass; the sixth added the same
    # day). Twenty-two sections in the page's own order, the seven
    # indicators of the month moved up beside the days; the releaser
    # and the house-master, Sahl's apparatus and the page's one
    # exception to PN IV, in a chapter of their own after the
    # distribution they copy. Client-side tabs, as on Configurations:
    # a click switches instantly and reruns nothing; the chapter is
    # kept across reruns from the page's own controls, and the page
    # opens on the first chapter when returned to (owner, third pass:
    # the rerun that remembered the chapter across pages flickered).
    _tab_labels = ("The Revolution", "Indicators of the Year", "Distributions", "The Releaser",
                   "Days & Months", "Fardar, Ages & Reference Tables")
    tab_rev, tab_ind, tab_dist, tab_rel, tab_days, tab_lords = st.tabs(list(_tab_labels))
    with tab_rev:
        st.subheader("The revolution of the year",
                     help="I.2, 1: a revolution is the moment the Sun comes back to \"his position in which he was "
                          "at the root\". I.2, 4: derive its Ascendant and the twelve houses. The engine uses a "
                          "TRUE-Sun return; Abu Ma'shar computes a mean Sun and then applies the Hipparchan "
                          "tropical year (I.4, 23-31), which Dykes says plainly does not make sense.")
        st.dataframe(pd.DataFrame(pn4['revolution_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['revolution_rows'])),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['revolution_rows'])))

        # --- The charts, drawn (2026-09-10) ---------------------------------
        # I.6, 1-6 and IX.3, 4-8 describe images holding the root, the
        # revolution of the year and the revolution of the month on one
        # zodiac. Drawn as PN IV's editor draws them: the outer charts in
        # whole signs, the sign of the year shaded, the profection a
        # dashed arc, an Egyptian-bounds ring, the default points of p. 12.
        # The controls are readings of the page, kept across navigation.
        # One @st.fragment for the whole of this subheader's block
        # (item 9, 2026-09-15). Every one of its eight controls -- the
        # View selectbox, the Wheel layout radio and the five in the
        # Options popover -- used to rerun the whole script, which
        # redraws the 67 tables this page carries; a fragment reruns
        # only its own body on its own widgets' changes. The picture is
        # what the controls are for, so the picture, its download and
        # the caption that explains its conventions are inside it and
        # the direction strips and every table are outside.
        #
        # The revolution data is the top level's: pn4 and the charts it
        # carries are computed once per run, before this page's tabs,
        # and the fragment reads them from the enclosing scope. What
        # the fragment regenerates on its own rerun is the SVG, from
        # the values its own widgets hold -- including the theme, which
        # is taken from this block's own Dark wheel checkbox rather
        # than from the top level's WHEEL_THEME, that being a full
        # run's value and not one a fragment rerun moves.
        @st.fragment
        def _timing_wheel_block():
            st.subheader("The charts, drawn",
                         help="Year: the revolution alone (Figures 4, 26). Year over root: the image of the revolution "
                              "of the year, I.6, 3-6 (Figure 51 and fn 33; Figures 5 and 27 in Dykes's order). Month "
                              "over year and root: the image of the revolution of the month, IX.3, 4-8 (Figures 39 "
                              "and 109, fn 58). Month: the month's revolution alone. Profection: the natal wheel with "
                              "the sign of the year and the sign of the month (Figures 3, 15, 33). The Wide layout "
                              "adds a positions column per chart; hover the picture for the expand arrows.")
            st.session_state.setdefault("_timing_bounds", True)
            v_view, v_layout, v_opts = st.columns([2.2, 1.4, 0.9], vertical_alignment="bottom")
            with v_view:
                wheel_view = _reading_select("View", WHEEL_VIEW_OPTIONS, "timing_wheel_view", "_timing_wheel_view")
            with v_layout:
                _timing_layout = _reading_radio("Wheel layout", WHEEL_LAYOUT_OPTIONS, "wheel_layout", "_wheel_layout")
            with v_opts:
                with st.popover("Options", icon=":material/tune:", width="stretch"):
                    wheel_order = _reading_radio("Inner wheel", WHEEL_ORDER_OPTIONS, "wheel_order", "_wheel_order",
                                                 help="Dykes: \"Abu Ma'shar seems to prefer that the SR be the inner "
                                                      "wheel, but to me this seem unnatural and I only do it to "
                                                      "illustrate his instructions in Ch. I.6\" (p. 12). Figure 51 "
                                                      "follows Abu Ma'shar; every other figure in the book puts the "
                                                      "nativity in the centre. IX.3, 4-6 writes the month first, then "
                                                      "the year, then the root.")
                    wheel_bounds = _reading_checkbox("Bounds ring", "timing_bounds", "_timing_bounds",
                                                     help="The Egyptian bounds as a ring, as every PN IV wheel carries them.")
                    # Every control in this popover stands before the
                    # picture, so each one's own return is this
                    # fragment rerun's value -- no read-before-draw is
                    # needed here, as it is on the Chart page where the
                    # controls sit under the wheel. _persist still
                    # writes the store keys and the preferences file
                    # from inside the fragment, so the next full run's
                    # WHEEL_DARK and the rest read what was left here.
                    _timing_dark = _reading_checkbox("Dark wheel", "wheel_dark", "_wheel_dark", help=WHEEL_DARK_HELP)
                    want_lots = _reading_checkbox("Lots", "timing_lots", "_timing_lots",
                                                  help="I.6, 3-4: the Lots \"according to how you do it\" -- this app's, "
                                                       "beyond Fortune, as short ticks with their names.")
                    want_rays = _reading_checkbox("Rays", "timing_rays", "_timing_rays",
                                                  help="I.6, 3-4 and 8: the 98 rays, as ticks -- too many to letter; the "
                                                       "inventory table below lists each one.")
                    want_twelfths = _reading_checkbox("Twelfth-parts", "timing_twelfths", "_timing_twelfths",
                                                      help="I.6, 3-4 and 8: the 38 twelfth-parts of the planets and of the "
                                                           "house degrees, as ticks.")

            def _ring_extras(chart):
                out = []
                if want_lots:
                    for d in LOT_DEFINITIONS:
                        if d['id'] == 'fortune':
                            continue
                        lot_lon = lot_by_id(d['id'], chart['planetary_data'], chart['ascendant'], chart['houses'], chart['sect'])
                        if lot_lon is not None:
                            out.append((d['name'], lot_lon, d['name'].replace('Lot of ', '').replace('the ', '')[:9]))
                if want_rays:
                    for ray_lon, kind, who, aspect in pn4_bodies_and_rays(chart['planetary_data']):
                        if kind != 'body':
                            out.append((f"{who} by {aspect}", ray_lon, POINT_GLYPHS[who] + _ASPECT_GLYPH.get(aspect, '')))
                if want_twelfths:
                    for who, row in chart['planetary_data'].items():
                        if who in PLANET_SWE_IDS:
                            out.append((f"twelfth-part of {who}", pn4_twelfth_part(row['longitude']), '¹²' + POINT_GLYPHS[who]))
                    for i, cusp in enumerate(list(chart['houses'])[:12]):
                        out.append((f"twelfth-part of the degree of house {i + 1} ({get_degree_string(cusp)})",
                                    pn4_twelfth_part(cusp), f'¹²h{i + 1}'))
                return out

            _natal_when = f"{local_dt.day} {local_dt:%b} {local_dt.year} {local_dt:%H:%M} {tz_name}"
            natal_ring = {'label': 'Nativity', 'chart': chart_data, 'when': _natal_when}
            year_ring = {'label': f"Year, age {pn4['age']}", 'chart': pn4['sr'],
                         'when': f"{pn4_datetime_from_jd(pn4['jd_sr']):%d %b %Y %H:%M} UT"}
            month_ring = {'label': f"Month {pn4['month']} of 12", 'chart': pn4['mr'],
                          'when': f"{pn4_datetime_from_jd(pn4['jd_mr']):%d %b %Y %H:%M} UT"}
            year_sign = SIGN_ORDER.index(pn4['year']['sign'])
            _month_lon = next((r['longitude'] for r in pn4['monthly_indicators'] if r['number'] == 1), None)
            month_sign = None if _month_lon is None else int((_month_lon % 360.0) // 30)
            _cur = pn4['current']
            _distribution = None
            if _cur and pn4['segments']:
                _distribution = {'start': chart_data['ascendant'],
                                 'end': _pn4_seg_degree({'from': pn4['elapsed_years']}, chart_data['ascendant'], chart_data, lat)}
            _badges = {}
            for _planet, _letter in (((_cur or {}).get('distributor'), 'D'), ((_cur or {}).get('partner'), 'P'),
                                     ((pn4['fardar'] or {}).get('lord'), 'F'), ((pn4['fardar'] or {}).get('sub_lord'), 'f'),
                                     (pn4['orb'], 'O')):
                if _planet:
                    _badges[_planet] = (_badges.get(_planet, '') + '·' + _letter).strip('·')
            _dykes = wheel_order == WHEEL_ORDER_OPTIONS[0]
            _wide_t = _timing_layout == WHEEL_LAYOUT_OPTIONS[1]
            if wheel_view == WHEEL_VIEW_OPTIONS[0]:
                _rings, _kw = [year_ring], {}
            elif wheel_view == WHEEL_VIEW_OPTIONS[1]:
                _rings = [natal_ring, year_ring] if _dykes else [year_ring, natal_ring]
                _n = _rings.index(natal_ring)
                _kw = dict(shade_sign=year_sign, profection_from=chart_data['ascendant'], distribution=_distribution,
                           marks=[('TP', pn4['year']['longitude'], _n)], badges={_n: _badges})
            elif wheel_view == WHEEL_VIEW_OPTIONS[2]:
                _rings = [natal_ring, year_ring, month_ring] if _dykes else [month_ring, year_ring, natal_ring]
                _n = _rings.index(natal_ring)
                _kw = dict(shade_sign=year_sign, outline_sign=month_sign, profection_from=chart_data['ascendant'],
                           marks=[('TP', pn4['year']['longitude'], _n)], badges={_n: _badges})
            elif wheel_view == WHEEL_VIEW_OPTIONS[3]:
                _rings, _kw = [month_ring], {}
            else:
                _rings = [natal_ring]
                _kw = dict(shade_sign=year_sign, outline_sign=month_sign, profection_from=chart_data['ascendant'],
                           marks=[('TP', pn4['year']['longitude'], 0)])
            _extras = {i: _ring_extras(r['chart']) for i, r in enumerate(_rings)} if (want_lots or want_rays or want_twelfths) else None
            # The same rule the top level's WHEEL_THEME follows, read
            # from this fragment's own checkbox: the viewer's theme
            # when the preference is on, None when it is off. No
            # picture is handed the viewer's theme unfiltered.
            _timing_theme = VIEWER_THEME if _timing_dark else None
            svg_timing = generate_multiwheel_svg(_rings, chart_name, wide=_wide_t, bounds=wheel_bounds, extras=_extras,
                                                 theme=_timing_theme, **_kw)
            st.image(svg_timing, width='stretch' if _wide_t else 560)
            st.download_button("Download this wheel (SVG)", svg_timing, key="dl_timing_wheel",
                               file_name=f"{re.sub(r'[^A-Za-z0-9]+', '_', chart_name).strip('_') or 'chart'}_"
                                         f"{re.sub(r'[^A-Za-z0-9]+', '_', wheel_view).strip('_').lower()}_age{pn4['age']}.svg",
                               mime="image/svg+xml")
            st.caption("PN IV's own conventions, read from its figures: the nativity in the centre and the "
                       "revolution outside in every bi-wheel but Figure 51, where Dykes follows Abu Ma'shar's order of I.6 "
                       "and says so (p. 12); the outer charts in whole signs; \"the profected natal Ascendant "
                       "... which I have shaded in grey\" (fn 33) -- the sign of the terminal point of the year -- "
                       "with the profection drawn as a dashed arc from the natal Ascendant (Figures 3, 33); the month "
                       "as a tri-wheel, root, year, month (fn 58); a ring of the Egyptian bounds on its wheels "
                       "(Figures 1, 22, 25, 26; not the simplified Figure 51). "
                       "Default points are Dykes's (p. 12): the seven planets, the nodes, Fortune, the angles; "
                       "I.6, 3-4's Lots, rays and twelfth-parts are the toggles, and the inventory table below is "
                       "the authority the picture is held to. TP marks the terminal point of the year (I.6, 5); the "
                       "letters under a natal planet mark I.6, 6's time lords -- D distributor, P partner, F lord of "
                       "the fardar, f its divider, O lord of the orb; the solid arc from the natal Ascendant is the "
                       "distribution, ending on the degree reached now with its bound tinted (Figures 2, 65). Two "
                       "things the text asks for that the picture keeps as Dykes drew it: I.6, 2 has the houses "
                       "\"by their degrees and minutes ... the portions of hours and the ascensions of the right "
                       "circle\" -- the Alchabitius cusps this app computes -- and the wheel keeps whole signs, as "
                       "fn 33 says Figure 51 does \"to make the image easier to understand\"; and I.6, 5 profects the "
                       "terminal point \"from the Lot of Fortune of the root, and from the rest of the indicators\" "
                       "as well as from the Ascendant, where only the Ascendant's arc is drawn (the Lot of Fortune's "
                       "profection is in the month's indicators below).")
        _timing_wheel_block()


        st.subheader("The image of the revolution of the year: its points (I.6, 3-8)",
                     help="I.6, 3: the revolution's planets with their conditions, \"their rays and twelfth-parts, "
                          "and the twelfth-parts of the degrees of the houses\"; I.6, 4: the root's planets likewise, "
                          "\"and the Lots and Head and Tail\"; I.6, 5: the natal Ascendant and the terminal point; "
                          "I.6, 6: the endpoint of the distribution, the distributor and partner, the fardar lord "
                          "and its divider, and the lord of the orb, \"each of them in their signs and bounds\"; "
                          "I.6, 8 and Figure 52: 14 planets, 98 rays, the Head and Tail twice each, 38 "
                          "twelfth-parts -- 154 -- \"and the Lots according to how you do it\"; I.6, 9-10: within a "
                          "house, by degree.")
        image_rows, image_counts = pn4['image']
        st.markdown("The count: " + ", ".join(f"{k} {v}" for k, v in image_counts.items())
                    + f" -- I.6, 8 counts 154 without the Lots{' and the count agrees' if image_counts['total of I.6, 8'] == 154 else ', and this chart differs'}.")
        st.dataframe(pd.DataFrame(image_rows), hide_index=True, width='stretch', height=_rows_height(16),
                     column_config=_wide_text_columns(pd.DataFrame(image_rows)))
        st.caption("A table, not the wheel of I.6, 1: every point by the revolution's house cusps -- I.6, 2: "
                   "\"calculating the houses by their degrees and minutes, in the way that you calculate the houses by "
                   "the portions of hours and the ascensions of the right circle\" (the Alchabitius cusps this app "
                   "computes; Dykes drew Figure 51 by whole signs \"for clarity\", fn 33; Figure 52 is the count table), "
                   "ordered by degree within the house, with each "
                   "point's bound. The twelfth-part construction -- 2.5 degrees to a sign, beginning with the sign "
                   "itself -- is stated at Gr. Intr. V.18, 1-3 (Figure 57). The fixed stars of I.6, 7 are the table below. The Lots are this "
                   "engine's, \"many or few\"; the count line excludes them as I.6, 8 does.")
        _fs, _fsr = pn4['fixed_stars'], pn4['fixed_stars_revolution']
        st.markdown("**The fixed stars (I.6, 7 in the root; III.8, 9 in the revolution)** -- Sahl's list, *On Nativities* "
                    "2.2, in Dykes's identifications (the table at that chapter's end, with Rhetorius Ch. 58's natures); "
                    "PN IV names no stars of its own. \"The very degree\" and \"with\" are read as within one degree "
                    "of longitude; the planets \"in the stakes\" by whole-sign place; latitude ignored. Positions from "
                    "the Swiss Ephemeris star catalogue the app ships (ephe/sefstars.txt).")
        if _fs['refused']:
            st.warning(f"Not computed: {_fs['refused']}.")
        else:
            if _fs.get('missing'):
                st.warning(_fs['missing'])
            st.markdown("*In the root (I.6, 7):*")
            if _fs['rows']:
                st.dataframe(pd.DataFrame(_fs['rows']), hide_index=True, width='stretch', height=_rows_height(min(len(_fs['rows']), 8)))
            else:
                st.markdown("None of Sahl's stars stands within a degree of the Ascendant, the Midheaven, a luminary or an angular planet.")
            st.markdown("*In the revolution (III.8, 9):*")
            if _fsr['rows']:
                st.dataframe(pd.DataFrame(_fsr['rows']), hide_index=True, width='stretch', height=_rows_height(min(len(_fsr['rows']), 8)))
            else:
                st.markdown("None within a degree of the year's Ascendant, its tenth, the terminal point, the distribution's degree, their lords or the luminaries.")

        st.subheader("The reading checklist (I.7, 1-26)",
                     help="\"If you made the image of the revolution of the year, then understand:\" (I.7, 1) -- "
                          "twenty-six things. 2-6: the revolution's Ascendant -- its house in the root, who is in it "
                          "and looks at it in both times, who has a claim on it and where they stand, whether its "
                          "lord has one house or two and looks at them. 7-24: every planet -- motion, strength, "
                          "aversion and aspect, rays, connection, reception, support, friendship, domain, "
                          "twelfth-parts, returns, course, transits, the Lots, the stakes, the Sun. 25-26: \"its "
                          "indication will be according to its place and condition in the two times together.\"")
        st.markdown("**I.7, 2-6 -- the revolution's Ascendant:**")
        st.dataframe(pd.DataFrame(pn4['i7_ascendant']), hide_index=True, width='stretch', height=_rows_height(5),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['i7_ascendant'])))
        st.markdown("**I.7, 7-24 -- the planets, in both times** (the numbers are I.7's sentences):")
        st.dataframe(pd.DataFrame(pn4['i7_planets']), hide_index=True, width='stretch', height=_rows_height(14))
        st.caption("Facts from the app's own evaluators, run on the revolution's data as on the root's: the "
                   "pairwise configurations and the connection rule of the Configurations page, reception under "
                   "its rule, the domain of the accidental dignities, the solar phase, the twelfth-part (a "
                   "convention, as the image's caption says), and V.1, 2-3's grades for a return. Not read, and "
                   "said so: " + '; '.join(f"{n} \"{t}\" -- {why}" for n, t, why in PN4_I7_NOT_READ)
                   + ". I.7, 22, the Lots of the year, are in the image above. I.7, 25-26 is the principle the "
                   "II.3 section applies. No worked example exists; I.7 is a list.")

    with tab_ind:
        st.subheader("Indicators of the year, in Abu Ma'shar's order",
                     help="II.1, 5-24 ranks nineteen indicators of the year and II.1, 25 says \"each one in turn "
                          "is stronger in indication than the one which is after it\". The first five are computed "
                          "here; the rest are delineation material. Note the order: WITHIN A YEAR the lord of the "
                          "year outranks the distributor (II.1, 25; II.23, 1). Across several years the "
                          "distribution is the stronger (III.2, 2-3) -- PN IV ranks them by scope; Sahl's 1.23, 33 "
                          "and 1.24, 2 contradict each other as printed (the caption under the table).")
        st.dataframe(pd.DataFrame(pn4['year_rows']), hide_index=True, width='stretch',
                     column_config=_wide_text_columns(pd.DataFrame(pn4['year_rows'])))
        st.caption(PN4_YEAR_INDICATOR_SCOPE_NOTE)

        st.subheader("The sign of the terminal point and its lord, examined (II.3, 2-19)",
                     help="II.3, 2: examine the sign of the terminal point in the root -- which house of the circle, "
                          "whose house, exaltation and triplicity, which planets, Lots and twelfth-parts are in it, "
                          "who looks at it or casts rays at it and from where, and whether it is devoid of them. "
                          "II.3, 3: the same in the revolution, with where those planets were and are, and their "
                          "condition in each. II.3, 5-8: the lord of the year's condition in root and revolution "
                          "compared four ways (Figure 55); II.3, 9-18: reception, a stake of the revolution's "
                          "Ascendant under an infortune, aversion to the Ascendant.")
        ii3 = pn4['ii3']
        st.markdown(f"**The sign of the terminal point, {pn4['year']['sign']}, in the root (II.3, 2):**")
        st.dataframe(pd.DataFrame(ii3['root_rows']), hide_index=True, width='stretch', height=_rows_height(5),
                     column_config=_wide_text_columns(pd.DataFrame(ii3['root_rows'])))
        st.markdown("**In the revolution (II.3, 3):**")
        st.dataframe(pd.DataFrame(ii3['revolution_rows']), hide_index=True, width='stretch', height=_rows_height(5),
                     column_config=_wide_text_columns(pd.DataFrame(ii3['revolution_rows'])))
        st.markdown(f"**The lord of the year, {pn4['year']['lord']}: the factors of II.3, 5-6, per chart:**")
        st.dataframe(pd.DataFrame(ii3['lord_rows']), hide_index=True, width='stretch', height=_rows_height(6),
                     column_config=_wide_text_columns(pd.DataFrame(ii3['lord_rows'])))
        st.dataframe(pd.DataFrame(ii3['refinement_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(ii3['refinement_rows'])),
                     column_config=_wide_text_columns(pd.DataFrame(ii3['refinement_rows'])))
        st.markdown("**Figure 55 -- the four cases, in the book's words; which one holds is left to the reader:**")
        st.dataframe(pd.DataFrame(ii3['figure_55']), hide_index=True, width='stretch', height=_rows_height(4))
        st.caption("Facts, not a verdict. II.3, 5-6 name the factors of a suitable and a contrary condition and "
                   "give no rule for weighing them, so each factor is shown for each chart from the app's own "
                   "evaluators (essential and accidental dignity, solar phase, reception under the Configurations "
                   "page's rule), and Figure 55's cell is not chosen. \"Domain\" is read as sect (fn 46, 48); "
                   "\"westernization from the Sun\" is shown as the solar side (fn 47). Aspects to the sign and to "
                   "the lord are by whole sign. Also read: the twelfth-parts (Gr. Intr. V.18, 3) and fn 37-41's "
                   "classes of sign (VI.4, 4-6: loving, hating, hostile by aspect; IX.2, 33: matching in ascensions, in "
                   "daylight, or one belt) and of degree (V.20's bright, dusky, empty and dark degrees, the editor's "
                   "\"probably\"), as facts on rows [3] and [4-7]. "
                   "The delineations of II.4-II.21 are not built. No worked example exists; Figure 55 is Dykes's "
                   "table.")

        st.subheader("Indicators 6-19: the fact each one reads",
                     help="II.1, 11-24 list the remaining fourteen indicators, in II.1, 25's order of strength. "
                          "Each reads a fact from the root and the revolution and judges it in a chapter of its "
                          "own; the facts are computed here, the judgments are not. Nine are lookups on the two "
                          "charts. #7 is read from the Moon's connections in her sign (II.22, below). #15 needs "
                          "the house lords' connections read in the revolution, which the app's static test "
                          "does not do, and #16 and #17 follow the year's transits, which are not tracked -- "
                          "those three rows say so.")
        st.dataframe(pd.DataFrame(pn4['further_rows']), hide_index=True, width='stretch',
                     height=_rows_height(14),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['further_rows'])))
        st.caption("Facts, not judgments: the delineation chapters behind these rows (II.6-21, V.1-8, VI.3-6, "
                   "VII.9, VIII.1-15) are not built. #8 grades a transit as V.1, 2-3 does -- the degree, the "
                   "bound, or only the sign. #10 counts each lord from its own Ascendant (fn 128). #14 and #19 "
                   "count from the three places VI.5, 1 names. #12 and #13 read both the terminal sign and the "
                   "revolution's Ascendant, as VI.3-4 do.")

        st.subheader("The lord of the orb (VI.1)",
                     help="VI.1, 4: \"the lord of the hour in which the native was born\" is assigned to the "
                          "Ascendant and the first year; VI.1, 5-8: the next hour lord down the spheres to the "
                          "next house and the next year, and on past twelve -- \"the lord of the thirteenth hour "
                          "from it belongs to the Ascendant of the root and the thirteenth year\" -- so the loop "
                          "of seven runs on against the cycle of twelve and the pairing changes every twelve "
                          "years. Judged \"just as you judge by means of the lord of the year\" (VI.1, 12). "
                          "Row 5 above is this year's. The table here is VI.1, 18-19: six positions whose hour "
                          "lords are named by VI.1, 10 -- \"the lord of the hour of the house of assets\" is the "
                          "second hour lord from the natal one -- read as hour k for house k. VI.1, 10 fixes the "
                          "name to the first cycle; VI.1, 8's assignment (\"the lord of the thirteenth hour from it "
                          "belongs to the Ascendant of the root and the thirteenth year\") gives a different planet for "
                          "the same name from age 12 on; both are shown, neither is stated for 18-19, and the reset "
                          "Dykes proposes (Intro Sect. 13, \"my idea\") is a third answer, his own.")
        st.dataframe(pd.DataFrame(pn4['orb_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['orb_rows'])),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['orb_rows'])))
        st.caption("What PN IV presupposes here rather than states: the planetary hours. Their sequence from "
                   "the day lord at sunrise is Dykes's Figure 45 (Intro Sect. 13), which the Chart page's hour "
                   "lord follows with real sunrise and sunset, and with a flagged equal-hour approximation where "
                   "the Sun is circumpolar; Dykes notes that not everyone agrees on when the day begins. Dykes "
                   "also floats a single-cycle version in which each house keeps its first hour lord for life "
                   "(Intro Figure 48), on the thought that the loop is Abu Ma'shar's own error; VI.1, 8 states "
                   "the loop and the loop is built. His twelve-year \"reset\" of the named lords is, in his "
                   "words, his idea, and is not built. The delineations of VI.1, 12-17 are not built; the seven days the "
                   "lord of the orb grants (IX.7, 7-9) are method 2 of the Days tab (This week / Today / This hour).")

        st.subheader("The governor (IX.9, 1-10; IX.2, 4-7)",
                     help="IX.9, 1-9 name eight testimonies and IX.9, 10 the rule: \"if these eight indicators "
                          "would combine together in a single planet, then it alone would be the governor ... and "
                          "if one of them had [only] some of the testimonies, it will be more primary than the "
                          "others, and the rest of them will have a partnership with it.\" IX.2, 4 gives a second, "
                          "sign-level governor for the first month: five conditions on the natal Lot, the terminal "
                          "point, the revolution's Ascendant and Lot, and the sign's quadruplicity; fn 37: such a "
                          "sign governs the year too.")
        gov_rows, gov = pn4['governor']
        st.markdown(f"**IX.9:** {gov['text']}")
        st.dataframe(pd.DataFrame(gov_rows), hide_index=True, width='stretch', height=_rows_height(8),
                     column_config=_wide_text_columns(pd.DataFrame(gov_rows)))
        if pn4['governor_condition']:
            st.markdown(f"**IX.9, 11-13, the condition of the primary planet ({gov['primary'][0]}), as facts** -- the "
                        "conclusions quoted, not pronounced; 13's place half (\"in a stake or in what follows a stake\") is "
                        "judged by the Alchabitius DIVISION in the revolution, the five degrees at the four axial degrees -- "
                        "the unit is THIS APP'S CONVENTION (an adopted dynamic-fitness reading), not the text's; "
                        "the row states the three parts and the qualified confidence (IX.5, 4 fn 106).")
            st.dataframe(pd.DataFrame(pn4['governor_condition']), hide_index=True, width='stretch', height=_rows_height(3),
                         column_config=_wide_text_columns(pd.DataFrame(pn4['governor_condition'])))
        fm_rows, fm_verdict = pn4['first_month_governor']
        st.markdown(f"**IX.2, 4:** {fm_verdict}")
        st.dataframe(pd.DataFrame(fm_rows), hide_index=True, width='stretch', height=_rows_height(5),
                     column_config=_wide_text_columns(pd.DataFrame(fm_rows)))
        st.caption("Partial by nature, and said so per row. Testimony #3 and the releaser's half of #4 need the "
                   "longevity releaser, which PN IV does not supply (IX.8, 123); they are filled from the releaser's "
                   "distribution (Sahl, On Nativities 1.15, in The releaser chapter) when that finds one, #4 "
                   "counted only when the two distributions share one partner; #7 is "
                   "read from the Moon's connections in her sign (II.22, below). The tally runs over what is "
                   "available and names a governor ALONE only when all eight are counted and combine in one "
                   "planet, which is what IX.9, 10 reserves the word for. "
                   "\"The first lord\" of the revolution's Ascendant is read as its domicile lord (fn 324). The "
                   "IX.2 test is strict and most years fail it, so its five conditions are shown one by one; "
                   "Dykes's fn 39 (age 39, everything in Cancer, the Moon) is the case it is checked against. "
                   "IX.9, 11-13 are shown as facts above (12's 'harmonized by nature' not read; 13's place half by the "
                   "division, the convention Dykes proposes for strength language, ITA Introduction §6); IX.2, 8-11, "
                   "the delineations, are not built.")

        st.subheader("The Moon's connections in her sign, and the portions of the year (II.22)",
                     help="II.22, 1: \"the planet which the Moon connects with, so long as she is in her [current] "
                          "sign\"; II.22, 2: \"if it was two planets, the year is divided into two halves; and if "
                          "her connection in that sign of hers was with three planets, then that year is divided "
                          "into equal thirds; and if it increased beyond that, then the year is divided according "
                          "to their number\"; II.22, 3: each portion judged by \"the planet which owns the "
                          "portion\"; II.22, 4: \"if the Moon was empty in course ... the lord of her house, "
                          "whether it looked at her or not\". The revolution's Moon is followed by the ephemeris "
                          "until she leaves her sign, and every perfection of body or Ptolemaic ray before that is "
                          "a connection.")
        mn = pn4['moon']
        if mn['void']:
            st.markdown(f"The revolution's Moon at {get_degree_string(mn['moon_lon'])} leaves {mn['sign']} on day "
                        f"{mn['exit_day']:.2f} **without perfecting a connection**: empty in course, so the lord of "
                        f"her house, **{mn['house_lord']}**, stands in (II.22, 4).")
        else:
            st.markdown(f"The revolution's Moon at {get_degree_string(mn['moon_lon'])} leaves {mn['sign']} on day "
                        f"{mn['exit_day']:.2f}; before that she connects with **{len(mn['connections'])}** "
                        f"planet{'s' if len(mn['connections']) != 1 else ''}, so the year "
                        f"({pn4['year_days']:.2f} days to the next revolution) is divided into "
                        f"**{len(mn['connections'])}** portion{'s' if len(mn['connections']) != 1 else ''} "
                        f"(II.22, 2). This year's lord is **{pn4['year']['lord']}**; II.22 states the division "
                        f"for a year whose lord is the Moon, and it is computed here in every year.")
            st.dataframe(pd.DataFrame(pn4['moon_rows']), hide_index=True, width='stretch',
                         height=_rows_height(len(pn4['moon_rows'])))
            st.dataframe(pd.DataFrame(pn4['portion_rows']), hide_index=True, width='stretch',
                         height=_rows_height(len(pn4['portion_rows'])))
        st.caption("Read into the sentences: a connection is a perfection by degree, of the body or a Ptolemaic "
                   "ray, before she leaves the sign, with the whole-sign configuration re-checked at the moment of "
                   "perfection (VII.5, 14: no out-of-sign connection); the portions go to the planets in the order "
                   "she connects, which II.22 does not state; the division is stated for the Moon's year and is "
                   "shown every year with this year's lord named; \"empty in course\" is no such perfection "
                   "before she leaves the sign. II.22, 11's rays, Lots and twelfth-parts are not counted. The "
                   "same computation fills indicator #7 above and testimony #7 of the governor. The judgments of "
                   "II.22, 5-24 are not built. No worked example exists in PN IV.")

        st.subheader("When a luminary is lord of the year: the proxies (II.13, 1; II.14, 1; II.22, 1-5)",
                     help="II.13, 1: \"If the Sun was the lord of the year, then the majority of that judgment in "
                          "that year should be in accordance with the condition of [1] the lord of the sign in "
                          "which the distribution of the lifespan from the [longevity] releaser was ..., and "
                          "partnering with it in the indication is [2] the planet which is in Leo in the root of "
                          "the nativity or in the revolution, and [3] the planet to which the Sun hands over the "
                          "management (so long as it is in its sign), and then along with that you see [4] where "
                          "the Sun is, calling upon [that] as a witness.\" II.14, 1 adds the distributor; II.22, "
                          "1-5 give the Moon's list. Dykes's fn 237 reads these as proxies standing in for the "
                          "luminary.")
        if pn4['proxies'] is None:
            st.markdown(f"This year's lord is **{pn4['year']['lord']}**, absent from the revolution.")
        else:
            st.markdown(f"This year's lord is **{pn4['year']['lord']}**.")
            st.dataframe(pd.DataFrame(pn4['proxies']), hide_index=True, width='stretch',
                         height=_rows_height(len(pn4['proxies'])),
                         column_config=_wide_text_columns(pd.DataFrame(pn4['proxies'])))
        st.caption("The first proxy in every version is the sign the longevity releaser's distribution stands "
                   "in, which PN IV does not supply (IX.8, 123); it is filled from the releaser's distribution "
                   "(Sahl, On Nativities 1.15, in The releaser chapter) when that finds one, and reads "
                   "unavailable otherwise. The Sun's hand-over is read per fn 239 as the Sun's own "
                   "connections before he leaves his sign, in the revolution (fn 239 notes the book does not say "
                   "root or revolution), and \"hands over\" as the Sun being the applying body at the perfection; "
                   "\"where the Sun is\" is his sign and its lord per fn 241. The Moon's rows are the II.22 "
                   "computation above; her conditions are shown as facts and II.22, 6-10's judgment of them is "
                   "not built, nor are II.13, 2 - II.21. No worked example exists; fn 238 illustrates the missing "
                   "part.")

        st.subheader("The turning of the houses of the root (VI.2)",
                     help="VI.2, 1: \"every one of the seven planets, the twelve houses, and the twelve Lots, is "
                          "turned at the revolutions of years from its own position (a year for every sign), and "
                          "is directed from its degree (a year for every degree); and when any of them, by turning "
                          "or by direction, reaches a sign or planetary fortune or infortune, it produces the "
                          "indication of that sign or planet.\" VI.2, 2-17 say what each is turned for. Only the "
                          "TURNING is built: whole-sign profection from each point's own natal position, as for "
                          "the Ascendant. VI.2, 21-24: a quadrant cusp that falls in another sign is turned both "
                          "from its house by counting and from the sign its degree falls in, and such houses get "
                          "two rows.")
        st.markdown(f"Turned by **{pn4['age']}** completed years, a sign for each (VI.2, 1).")
        st.dataframe(pd.DataFrame(pn4['turning_rows']), hide_index=True, width='stretch',
                     height=_rows_height(min(len(pn4['turning_rows']), 16)),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['turning_rows'])))
        st.markdown("**The triplicity lords examined beside the turning (VI.2, 4-5)** -- the sect light's for assets "
                    "(4; fn 13), the lords of Mars's natal sign for siblings (5: the first the older, the second the "
                    "middle, the third the younger); each lord's condition in the root and in the revolution, as the "
                    "II.3 examination prints it. fn 14's age mapping is the editor's and is not applied.")
        st.dataframe(pd.DataFrame(pn4['turning_triplicity_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['turning_triplicity_rows'])),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['turning_triplicity_rows'])))
        st.caption("The direction \"a year for every degree\" is proportional semi-arcs, each row saying where it "
                   "stands at this age: for planets and Lots it is III.1, 12's third case (fn 16), for the cusps "
                   "VI.2, 21's \"portions of the hours and the right circle\" (fn 33) -- the point's degree "
                   "directed as the planets are in The distribution chapter (" + PN4_SEMIARCS_SOURCES + "). "
                   "The Ascendant's and the meridian's directions are the distributions above. Which \"twelve "
                   "Lots\" VI.2, 1 means is not stated; the formulas in fn 12-31 are Dykes's identifications from "
                   "Sahl and the Great Introduction, and the app's Lots are paired to them here, with the two "
                   "places they differ on the night reversal named in the row. \"Whichever had the shift in the "
                   "root\" for the parents (VI.2, 6, 8) is read as the sect planet, per fn 16 and 19. The "
                   "triplicity lords of VI.2, 4-5 are the table above; the delineations are not built. No worked example exists; "
                   "Figures 90-91 are Dykes's diagrams.")

    with tab_dist:
        st.subheader("The distribution from the Ascendant (the *jar bakhtar*)",
                     help="III.1, 12: the Ascendant is directed by the ascensions \"of the country in which the "
                          "native was born\" -- oblique ascensions of the birth latitude, one degree of ascension "
                          "to a year (III.1, 13). III.1, 11: the lord of the bound reached is the distributor, "
                          "\"whether it looked at [the bound] or not\". III.1, 15-16: the most recent body or ray "
                          "met is the partner, and it holds until another body or ray is met -- so there is always "
                          "exactly one, and a ray is a point with no orb. III.1, 14: the Persians gave this "
                          "particular distribution, and no other, the name *jar bakhtar*.")
        if pn4['segments'] is None:
            st.warning("Refused at this latitude. Above the polar circle some degrees never rise, the oblique "
                       "ascension has no unique inverse, and an arc of direction from the Ascendant is not "
                       "defined.")
        else:
            _strip = generate_distribution_strip_svg(pn4['segments'], pn4['elapsed_years'], 'years',
                                                     PN4_DISTRIBUTION_SPAN_YEARS, 'The distribution from the Ascendant',
                                                     theme=WHEEL_THEME)
            st.image(_strip, width='stretch')
            st.download_button("Download this strip (SVG)", _strip, key="dl_strip_asc", mime="image/svg+xml",
                               file_name="distribution_ascendant.svg")
            cur = pn4['current']
            if cur:
                st.markdown(
                    f"**Now** (age {pn4['age']}): distributor **{cur['distributor']}**, partner "
                    f"**{cur['partner'] or 'none -- the distributor acts alone'}**"
                    f" &nbsp;|&nbsp; this period runs from age {cur['from']:.2f} to {cur['to']:.2f}"
                    f" &nbsp;|&nbsp; partner met: {cur['partner_from']}")
            st.dataframe(pd.DataFrame(pn4['distribution_rows']), hide_index=True, width='stretch',
                         height=_rows_height(min(len(pn4['distribution_rows']), 16)))
            if pn4['turning_partner']:
                st.markdown(f"**Sahl, the year of the turning and the partner:** {pn4['turning_partner']['text']}")
            st.caption("III.1, 23-25: at birth the partner is whatever body or ray lies between the beginning of "
                       "the Ascendant's sign and its degree; if there is none, \"the distributor without a planet "
                       "partnering with her\". III.2, 103-104 ranks partners body > opposition > square > trine > "
                       "sextile -- hard aspects above soft ones, which is the reverse of the usual intuition.")

        st.subheader("The distribution analysed (III.2)",
                     help="III.2, 4-9: a checklist of questions about the bound the distribution stands in, answered "
                          "here as facts. III.2, 10-17: seven \"static\" types of distributor and partner, by "
                          "fortune and infortune (Figure 66). III.2, 55-86: twenty-four transitions that can occur "
                          "inside a year, by the natures of the outgoing and incoming bound lords and managers, and "
                          "87-101 their twelve indications, quoted here one sentence each. III.2, 102-104 rank the "
                          "three indicators: the distributor, then the partner by body, then by ray.")
        if pn4['iii2_type'] is None:
            st.markdown("No current distribution to analyse (refused at this latitude, or the age is past the table).")
        else:
            t_num, t_label, t_cite = pn4['iii2_type']
            cur = pn4['current']
            st.markdown(f"**Static type:** {'type ' + str(t_num) + ', ' if t_num else ''}{t_label} -- "
                        f"{cur['distributor']} distributing"
                        f"{', ' + cur['partner'] + ' partnering by ' + cur['partner_aspect'] if cur['partner'] else ', alone'} "
                        f"({t_cite}).")
            st.dataframe(pd.DataFrame(pn4['iii2_checklist']), hide_index=True, width='stretch', height=_rows_height(7))
            if pn4['iii2_transitions']:
                st.markdown(f"**Shifts inside this year of the distribution** (age {pn4['age']} to {pn4['age'] + 1}):")
                st.dataframe(pd.DataFrame(pn4['iii2_transitions']), hide_index=True, width='stretch',
                             height=_rows_height(len(pn4['iii2_transitions'])))
            else:
                st.markdown(f"**No shift of bound or management falls inside this year of the distribution** "
                            f"(age {pn4['age']} to {pn4['age'] + 1}); the twenty-four of III.2, 55-86 do not arise.")
        if pn4.get('bound_transits') is not None:
            st.markdown("**Transits into the bound, in the revolution** (III.2, 38, 43, 46-47, 54; III.8, 7):")
            st.dataframe(pd.DataFrame(pn4['bound_transits']), hide_index=True, width='stretch',
                         height=_rows_height(len(pn4['bound_transits'])))
        st.caption("Facts and classification, not judgment: the conditions III.2's delineation turns on -- \"in a "
                   "suitable condition in the root and in the revolution\" -- are not judged, and the prose of "
                   "III.2, 18-54 is not built. The Sun, Moon and Mercury are neither fortune nor infortune, and the "
                   "types and transitions speak only of fortunes and infortunes, so a distribution under one of "
                   "them reads \"no type by nature\" and a shift involving one \"not among the twenty-four\"; type 5 "
                   "turns on conditions and is never assigned. The transitions are read from the natal "
                   "distribution above, as III.2, 105 requires; a revolutionary planet entering the bound is the "
                   "table just above, each keyed by the static type to the one sentence that speaks of it (III.2, "
                   "38, 43, 46-47, 54; III.8, 7's condition on the two lords as facts), the Sun, Moon and Mercury "
                   "addressed by none, and 46-47 speaking of rays only. Every quoted indication that "
                   "mentions death carries III.2, 110-111's gate: death only in the years the longevity indicator "
                   "pointed out -- the years the house-master's direction reaches an infortune, in The "
                   "releaser chapter. No worked example by the author; "
                   "Figure 67 with fn 56 is Dykes's diagram of III.2, 33.")

        st.subheader("The distribution from the Midheaven and the fourth",
                     help="III.1, 12: \"what is in the Midheaven or the fourth is directed by the ascensions of "
                          "the right sphere\" -- right ascension, one degree to a year (III.1, 13), the lord of "
                          "the bound reached as distributor (III.1, 11) and the last body or ray met as partner "
                          "(III.1, 15-16), exactly as for the Ascendant. Fn 14 reads \"the fourth\" as the IC "
                          "degree itself. Right ascension has no latitude in it, so these two distributions are "
                          "defined at every latitude and are never refused.")
        for point in PN4_MERIDIAN_POINTS:
            m = pn4['meridian'][point]
            cur = m['current']
            _strip = generate_distribution_strip_svg(m['segments'], pn4['elapsed_years'], 'years',
                                                     PN4_DISTRIBUTION_SPAN_YEARS, f'The distribution from the {point}',
                                                     theme=WHEEL_THEME)
            st.image(_strip, width='stretch')
            st.download_button("Download this strip (SVG)", _strip, key=f"dl_strip_{point[:4].lower()}",
                               mime="image/svg+xml", file_name=f"distribution_{point[:4].lower()}.svg")
            if cur:
                st.markdown(
                    f"**{point}** at {get_degree_string(m['degree'])} -- **now** (age {pn4['age']}): distributor "
                    f"**{cur['distributor']}**, partner **{cur['partner'] or 'none -- the distributor acts alone'}**"
                    f" &nbsp;|&nbsp; this period runs from age {cur['from']:.2f} to {cur['to']:.2f}"
                    f" &nbsp;|&nbsp; opened standing on {get_degree_string(cur['from_lon'])}")
            else:
                st.markdown(f"**{point}** at {get_degree_string(m['degree'])} -- age {pn4['age']} is past the "
                            f"{PN4_DISTRIBUTION_SPAN_YEARS:g}-year table")
            st.dataframe(pd.DataFrame(pn4['meridian_rows'][point]), hide_index=True, width='stretch',
                         height=_rows_height(min(len(pn4['meridian_rows'][point]), 12)))
        st.caption("What PN IV does not supply here, stated rather than filled in. (1) Abu Ma'shar gives this "
                   "distribution no topic: \"actions, profession, and life projects\" is Dykes (Appendix A, "
                   "p. 673) and fn 4's al-Qabisi IV.12 -- editors' notes, not a sentence of the book. (2) It is "
                   "not among the year's indicators: II.2, 6-7 and 12-13 name the Ascendant's and the releaser's "
                   "distributions only, so it does not enter the indicators table above. (3) No worked example of "
                   "a meridian direction exists in PN IV -- III.1, 19-45 directs the Ascendant only -- so the "
                   "engine is checked by arithmetic and against the editor's four-minutes-a-degree animation "
                   "(Appendix A), not against the author's numbers. (4) The partner-at-birth rule of III.1, 23-25 "
                   "is worded for the Ascendant and is carried here by analogy. (5) III.1, 12 assigns \"the Ascendant "
                   "and the things in it\" to the oblique ascensions and \"what is in the Midheaven or the fourth\" to "
                   "the right ascensions: \"in\" is read as ON THE AXIAL DEGREE ITSELF, "
                   "recognised with a numerical tolerance (floating-point equality), not an astrological "
                   "orb -- no 3 degrees, no 5, no band; the Alchabitius division and the five-degree carry-over play no "
                   "part in choosing the method. A planet on one of the three degrees is directed as that degree is, "
                   "below; every other planet is \"what is not in these three positions\", the third case, "
                   "directed by proportional semi-arcs in the next section. The Descendant is not one of the three "
                   "positions (fn 15).")
        st.subheader("The planets, each with its measure under III.1, 12",
                     help="III.1, 12: \"the Ascendant and the things in it are directed by degrees of ascensions of the "
                          "country in which the native was born, while what is in the Midheaven or the fourth is "
                          "directed by the ascensions of the right sphere, and what is not in these three positions "
                          "is directed according to what we stated in our book [on that topic]\". A planet ON an axial degree is directed as that degree is. Every "
                          "other planet is the third case, whose method PN IV defers to a book it does not "
                          "reproduce: Ptolemy's method as Dykes identifies it (III.1, 12 fn 16; VI.2, 21 fn 33), "
                          "proportional semi-arcs, as al-Qabisi states it (Introduction IV, ITA VIII.2.2) and Dykes "
                          "works it (ITA Appendix E): the significator's distance from the meridian, in proportion "
                          "to its semi-arc, is carried to the promittor's semi-arc, and what the promittor has "
                          "still to travel is the arc -- PromMD - (SigMD / SigSA) * PromSA -- a degree of it a year "
                          "(III.1, 13). Here the planet's DEGREE is the significator (latitude 0, as the two other "
                          "cases direct degrees and as al-Qabisi's tables probably did (fn 27), Appendix E fn 27), the bound starts, "
                          "bodies and rays the promittors, the distributor and partner as in every distribution "
                          "(III.1, 10-11, 15-16). The meridian distance is signed, positive before the meridian in "
                          "primary motion; the meridian and the semi-arcs are those of the significator's side of "
                          "the horizon, the promittor's taken from the same meridian even when it stands on the "
                          "other side; a promittor already past the proportional place comes round after a "
                          "revolution and falls outside the table. Al-Qabisi's join across quarters (IV.12c) is "
                          "a different, approximate procedure and is not used; converse directions are not built.")
        for ap in pn4['angle_planets']:
            if ap['axis'] is None:
                st.markdown(f"**{ap['planet']}** at {get_degree_string(ap['degree'])}, {ap['where']}: its degree by "
                            f"{ap['how']}"
                            + (f" -- now: distributor **{ap['current']['distributor']}**, partner "
                               f"**{ap['current']['partner'] or 'none'}**" if ap['current'] else '') + ":")
            else:
                st.markdown(f"**{ap['planet']}** on the degree of {ap['where']}, by the {ap['how']}"
                            + (f" -- now: distributor **{ap['current']['distributor']}**, partner "
                               f"**{ap['current']['partner'] or 'none'}**" if ap['current'] else '') + ":")
            if ap['segments'] is None:
                st.warning(PN4_SEMIARCS_REFUSED if ap['axis'] is None
                           else "Refused at this latitude: the ascension has no unique inverse there.")
                continue
            st.dataframe(pd.DataFrame(ap['rows']), hide_index=True, width='stretch',
                         height=_rows_height(min(len(ap['rows']), 8)))
            if ap['terms']:
                st.markdown(f"The arc and its terms for {ap['planet']} ({PN4_SEMIARCS_SOURCES}):")
                st.dataframe(pd.DataFrame(ap['terms']), hide_index=True, width='stretch',
                             height=_rows_height(len(ap['terms'])))

    with tab_rel:
        # --- SAHL: the releaser and the house-master (2026-09-10) ---
        st.subheader("The releaser and the house-master (Sahl, *On Nativities* 1.15-1.16, 1.20)",
                     help="Not PN IV: Abu Ma'shar lists the five candidates (III.3, 1) and sends the reader to "
                          "another book for the choice (IX.8, 123). Nawbakht's procedure in Sahl, On Nativities "
                          "1.15: by day the Sun, then the meeting, then the Ascendant; by night the Moon, then "
                          "the fullness, then the Lot of Fortune, then the Ascendant. Each needs its place -- "
                          "by day \"the Ascendant, the Midheaven, the house of hope, or ... the stake of the "
                          "west, or ... the eighth\" (6), by night \"a stake or what follows a stake\" (11) -- "
                          "and \"the lord of the bound, house, exaltation, triplicity, or image looking at\" it "
                          "(11); \"that one ... which is looking at the releaser, is the house-master\" (13). "
                          "1.16: the Sun in Aries or Leo, the Moon in Taurus or Cancer, is both. 1.20, 2-4 rank "
                          "the lords: bound, house, exaltation, triplicity, image; two shares beat one; the "
                          "bound lord in the Ascendant with the releaser beats all.")
        rel = pn4['releaser']
        st.markdown(f"**{rel['verdict']}**")
        st.dataframe(pd.DataFrame(rel['candidates']), hide_index=True, width='stretch',
                     height=_rows_height(len(rel['candidates'])),
                     column_config=_wide_text_columns(pd.DataFrame(rel['candidates'])))
        if rel['ranking']:
            st.markdown("**The lords looking at the releaser, ranked** (1.15, 13; 1.20, 2-5) -- the first is the house-master:")
            st.dataframe(pd.DataFrame(rel['ranking']), hide_index=True, width='stretch',
                         height=_rows_height(len(rel['ranking'])))
        _sl = pn4['short_life']
        st.markdown(f"**The short-life testimonies (Sahl, *On Nativities* 1.18, 1-10, Masha'allah, fn 125): {_sl['count']} of "
                    f"the four counted** -- {_sl['sentence']}. Shown beside the releaser; they do not disqualify it here. "
                    f"5-7 are \"equivalent\" and not counted (fn 126, 129).")
        st.dataframe(pd.DataFrame(_sl['rows']), hide_index=True, width='stretch', height=_rows_height(7),
                     column_config=_wide_text_columns(pd.DataFrame(_sl['rows'])))
        if pn4['hm_years']:
            _y = pn4['hm_years']
            st.markdown(f"**The house-master's years** (Sahl, *On Nativities* 1.20, 7-34, Nawbakht -- the section "
                        f"1.23, 68, Masha'allah, sends the reader to): **{_y['text']}**. Placed by division "
                        f"{_y['division']} (the POWER unit). These are the years the infortunes may cut off (1.23, 53 and "
                        f"61) and the input PN IV III.2, 110-111's gate names (\"only if those years matched the years of "
                        f"the lifespan which his indicator in the root had already pointed out\").")
            for _f in _y['flags']:
                st.markdown(f"- {_f}")
            st.caption(_y['readings'])
            if _y['grade'] is None and pn4['hm_years_jn'] and READING_DEPTH == READING_DEPTH_OPTIONS[1]:
                _j = pn4['hm_years_jn']
                st.markdown(f"**Where 1.20 is silent, the supplement's ladder** ({_j['citation']}): **{_j['text']}**. "
                            f"The place: \"{_j['jn']}\"")
                for _step, _sent in _j['steps']:
                    st.markdown(f"- {_step}: \"{_sent}\"")
                if _j['table_note']:
                    st.markdown(f"- {_j['table_note']}")
                for _u in _j['umar']:
                    st.markdown(f"- {_u.replace('<', chr(92) + '<')}")
                st.caption(JN_YEARS_NOTE.replace('<', chr(92) + '<'))
            if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
                # JN Ch. 4's second half, display only (2026-09-15): one row a planet, no sum.
                _add = pn4['hm_years_additions']
                _finding([], "Additions and subtractions to the house-master's years (Abu 'Ali)",
                         JN_CH4_ADDITIONS_CITATION,
                         _add or [{'Planet': '-', 'Looks at the house-master': f"none of Saturn, Jupiter, Mars, Venus or Mercury is joined to {rel['house_master']} or looks at it by whole sign",
                                   'Ch. 4': '-', 'Its own lesser years': '-', 'If middling in strength': '-',
                                   'If more unsound': '-', 'Grade': '-', 'Reading': '-'}],
                         standing="Supplement · display only",
                         glance="What each planet joined to the house-master or looking at it would add to or subtract "
                                "from its years by Abu 'Ali's chapter: a fortune joined, trine or sextile adds its "
                                "lesser years, at one of three grades the chapter leaves undefined; a bad one joined, "
                                "square or opposite subtracts its lesser years; Mercury by Dykes's reading. Display "
                                "only: no sum is formed, and Sahl's grant above is not changed.",
                         notes=(f"Abu 'Ali, Judgments of Nativities Ch. 4, whole: \"{JN_CH4_SENTENCES['fortune']}\" \"{JN_CH4_SENTENCES['infortune']}\" "
                                f"\"{JN_CH4_SENTENCES['nothing']}\" \"{JN_CH4_SENTENCES['mercury']}\" \"{JN_CH4_SENTENCES['mars']}\" "
                                f"Fn 27 on \"rays\": \"{JN_CH4_SENTENCES['fn27']}\" Fn 28 on Mercury: \"{JN_CH4_SENTENCES['fn28']}\"\n\n"
                                f"{JN_CH4_ADDITIONS_NOTE}\n\n"
                                f"Abu Bakr, On Nativities I.15, a witness beside Abu 'Ali (not applied): \"{ABU_BAKR_I15_ADDITIONS['method']}\" "
                                f"He grades the aspecting planet by its place and condition where Abu 'Ali says \"middling\" and \"more unsound\": "
                                f"\"{ABU_BAKR_I15_ADDITIONS['grades']}\" And he differs on the bad one's trine and sextile and the fortune's square and "
                                f"opposition: \"{ABU_BAKR_I15_ADDITIONS['differs']}\" On Mercury: \"{ABU_BAKR_I15_ADDITIONS['mercury']}\"\n\n"
                                f"'Umar al-Tabari, Book of Nativities I.4.4, a witness (not applied): \"{TBN_I44_ADDITIONS['fortunes']}\" "
                                f"\"{TBN_I44_ADDITIONS['grades']}\" \"{TBN_I44_ADDITIONS['infortunes']}\" With Sahl 1.21, 8, and against Abu 'Ali, on the "
                                f"fortunes' square and opposition: \"{TBN_I44_ADDITIONS['squares']}\" And the Sun, whom Abu 'Ali does not name: "
                                f"\"{TBN_I44_ADDITIONS['sun']}\""))
        if rel['releaser'] is None:
            st.markdown("**The stand-in (Sahl, *On Nativities* 1.32, 11-14, al-Andarzaghar).** The Ascendant's "
                        "distribution in the tab \"from the Ascendant\" is \"the first of them\" (13); the Moon, "
                        "\"then the Moon\", directed from her natal degree to the infortunes and to burning by the "
                        "operation of 1.23, 2 (1.32, 12: \"if you directed the Sun or Moon in their courses to the "
                        "infortunes ... it kills, whichever of these four connects first with the infortune\"; 14: "
                        "\"if the fortunes are not looking at it\" -- the aspect of the fortunes is not judged here):")
            if pn4['standin_moon'] is None:
                st.warning("Refused at this latitude, as every direction by the oblique ascension is: it has no unique inverse there.")
            elif pn4['standin_moon']:
                st.dataframe(pd.DataFrame(pn4['standin_moon']), hide_index=True, width='stretch',
                             height=_rows_height(len(pn4['standin_moon'])))
            else:
                st.markdown("No target within the span for the Moon.")
        _syz = pn4['syzygies']
        st.markdown(f"The meeting (the last New Moon before birth) was at **{get_degree_string(_syz['meeting']['longitude'])}** "
                    f"on {pn4_datetime_from_jd(_syz['meeting']['jd']):%Y-%m-%d} UT; the fullness (the last Full Moon) at "
                    f"**{get_degree_string(_syz['fullness']['longitude'])}** on "
                    f"{pn4_datetime_from_jd(_syz['fullness']['jd']):%Y-%m-%d} UT, the degree of {_syz['fullness']['degree_of']}.")
        if rel['longitude'] is not None:
            st.markdown(f"**The releaser distributed** (1.15, 22; 1.18, 20-21): {rel['releaser']} at "
                        f"{get_degree_string(rel['longitude'])} directed through the bounds by the ascensions of the "
                        f"birth latitude, as the Ascendant is in the Distributions chapter"
                        + (" -- and here the releaser IS the Ascendant, so this is that distribution again." if rel['releaser'] == 'the Ascendant' else '.'))
            if pn4['releaser_segments'] is None:
                st.warning("Refused at this latitude, as the Ascendant's distribution is: the ascension has no unique inverse there.")
            else:
                _rstrip = generate_distribution_strip_svg(pn4['releaser_segments'], pn4['elapsed_years'], 'years',
                                                          PN4_DISTRIBUTION_SPAN_YEARS, 'The distribution from the releaser',
                                                          theme=WHEEL_THEME)
                st.image(_rstrip, width='stretch')
                st.download_button("Download this strip (SVG)", _rstrip, key="dl_strip_releaser", mime="image/svg+xml",
                                   file_name="distribution_releaser.svg")
                rcur = pn4['releaser_current']
                if rcur:
                    st.markdown(
                        f"**Now** (age {pn4['age']}): distributor **{rcur['distributor']}**, partner "
                        f"**{rcur['partner'] or 'none -- the distributor acts alone'}**, the direction standing in "
                        f"**{pn4['releaser_stand']['sign']}** (lord {pn4['releaser_stand']['lord']}) -- this feeds the "
                        f"governor's testimony #3 and the luminary proxies in the Indicators of the year chapter.")
                else:
                    st.markdown(f"Age {pn4['age']} is past the {PN4_DISTRIBUTION_SPAN_YEARS:g}-year table.")
                st.dataframe(pd.DataFrame(pn4['releaser_rows']), hide_index=True, width='stretch',
                             height=_rows_height(min(len(pn4['releaser_rows']), 12)))
        st.caption("Readings made here, each one Sahl leaves open. (1) THE PLACES: \"a stake or what follows a stake\" "
                   "(1.15, 6-16) is read as a test of the planet's POWER and counted by the Alchabitius divisions with the "
                   "five-degree allowance at the four axial degrees only -- a planet 0-5 degrees past the Ascendant, "
                   "Midheaven, setting degree or fourth into the cadent division keeps the stake's power, measured from "
                   "the axial degree, in longitude -- a proxy, though al-Qabisi's own unit: his rule reads \"five "
                   "equal degrees\", the zodiac's (ITA VIII.1.3, al-Qabisi IV.4). The warrant for the unit is the "
                   "translator's convention, adopted here: Dykes proposes it as his own solution -- whole signs for "
                   "topics, quadrant divisions for power (ITA Introduction §6) -- and Alchabitius, and the five degrees "
                   "at the four axial degrees only, are the course's (Lesson 3, A Chart Tour, §4-5; the Course Glossary "
                   "s.v. Advancement), Alchabitius being this app's choice among the quadrant systems he names; the texts "
                   "in hand give the dispatch: Carmen p. 108 fn 187, \"Dorotheus ... is using dynamic divisions to speak "
                   "of the planets' power, because one can only move from a stake to a decline by primary motion\"; "
                   "with fn 109 on 1.15, 6 agreeing (\"quadrant divisions, not whole signs\"). These texts' own "
                   "vocabulary counts SIGNS -- Introduction 2, 31-35 defines the stakes, \"what follows the stakes\" and "
                   "the falling places as counted signs, and 1.20, 10 says \"the sign of the west\" -- so the division "
                   "reading is the translator's, not Sahl's or Nawbakht's; 1.18, 19 (\"its strength will be in the "
                   "Ascendant ... and likewise in all of the houses\") is about strength and is read as the four "
                   "stakes; Aphorism #44 and 1.22, 9 witness the five degrees, not the house system. Al-Qabisi, in his own "
                   "releaser procedure, states the same five degrees for every house -- before the degree of the "
                   "Ascendant \"or any house\" (ITA VIII.1.3, al-Qabisi IV.4) -- and is the quadrant witness for that "
                   "procedure: he looks for the releaser in the angles and their followers as the twelve houses are "
                   "calculated through the degrees of the Ascendant's hours, a different author's method; here the five "
                   "degrees stay at the four stakes and the places are Sahl's. The Lot of Fortune "
                   "(a candidate by night, 1.15, 14) has no dynamic angularity and is tested by its whole-sign place. "
                   "The meeting's and the fullness's degrees (1.15, 6-8, 12) are neither planet nor Lot: the division is "
                   "used for them, an open reading. The day list is the five places 1.15, 6 names, the night list every "
                   "stake and succedent. (2) \"Looking\" is the whole-sign aspect, and a lord in the candidate's own "
                   "sign counts as looking (1.20, 4). (3) A candidate is not its own house-master except in 1.16's four "
                   "signs. (4) The triplicity lord is the lord of the sect. (5) The meeting is the last New Moon and the "
                   "fullness the last Full Moon before birth; the fullness's degree is the luminary that was above the "
                   "earth at the Full Moon: On Nativities 1.7, 2 (\"take the portion of whichever of the two luminaries "
                   "was above the earth\"), stated there for the Ascendant's degree and applied here by the same word, "
                   "\"portion\" (1.15, 12); when both or neither is above the earth the app takes the Moon's degree. "
                   "Al-Qabisi reports three opinions on the fullness's degree (ITA VIII.1.2, al-Qabisi IV.3): Ptolemy's, "
                   "the degree of the luminary that was above the earth; certain sages', that when one luminary is on "
                   "the eastern degree and the other on the western, the eastern degree is the prevention's; and "
                   "Valens's, the Moon's degree. The Moon default is Valens's; the sages' tie rule is named here and "
                   "not adopted. (6) \"In good places\" for the Ascendant's lord (1.15, 16): Sahl's seven praised "
                   "places (Introduction 2, 37-44: \"praised, powerful\"; 1.30, 71 names them; fn 372 calls them "
                   "\"good or advantageous\"), counted by whole-sign place; no sentence of Sahl's defines 16's phrase, so "
                   "the identification is an interpretation -- with Dykes's backing: the seven are the busy places of "
                   "Timaeus and Dorotheus, which he says Sahl \"explicitly uses\" in the Introduction, calling them "
                   "\"praiseworthy\" and \"stronger\" (ITA III.4, Dykes's comment; ITA Introduction §6). (7) The day "
                   "chart consults the "
                   "Sun, the meeting, then the "
                   "Ascendant (1.15, 9: \"if the meeting and the Sun were both falling, then the releaser at that time "
                   "will be the Ascendant\"); the night chart the Moon, the fullness, the Lot, then the Ascendant "
                   "(10-14). 1.15, 15 lists all five before the Ascendant and is read as the summary of the two lists; "
                   "read as a procedure it would consult the other sect's candidates first, which changes the releaser "
                   "in about one day chart in seven. The meeting's gate (1.15, 8) states a place test only; the "
                   "looking-lord test the app applies to it is supplied from 15's general wording (a reading). "
                   "Not applied, and named: "
                   + '; '.join(f"{c} ({t})" for c, t in SAHL_RELEASER_NOT_APPLIED) + ". "
                   "The YEARS the house-master grants are granted from On Nativities 1.20, 7-34 read in full, "
                   "above: On Times 4 is a question-chart chapter (\"in the hour of the "
                   "question\", 4, 2) and 1.23, 68 sends the reader to \"the section on the house-master\", so the "
                   "texts hold one natal grant, and the apparent disagreement was a tie between a horary rule and a "
                   "natal one; the Chart page's Planetary years table shows 1.20's grade for every planet and On "
                   "Times 4, 7 for comparison. On Times 4, 2-5's shorter list (victor by testimony, "
                   "seven candidates) and Masha'allah's ray in the Ascendant (1.23, 46-50) are the other two "
                   "procedures in these texts, not built. No worked example exists in Sahl.")

        st.subheader("The house-master directed (Sahl, *On Nativities* 1.23, 1-11)",
                     help="Masha'allah: \"look at the position of the governor [fn 181: the house-master] relative "
                          "to the Ascendant and its lord, and its position relative to burning and the infortunes; "
                          "then direct it to the conjunction of the infortunes and the degree of burning, and its "
                          "opposition and its square, a year for every degree of ascensions. Then calculate for "
                          "the revolution of that year in which the governor of the native corresponds to the "
                          "degree of the infortune ... for if your calculation of this and the revolution both "
                          "indicate burning, and then the governor is burned at the revolution, the native will "
                          "be destroyed; and if it is not burned at the revolution but it is burned in one of the "
                          "stakes of the Ascendant of the year, it indicates that as well; and it is worse for that "
                          "in the Ascendant itself\" (1.23, 2-4). This is the technique that needs no grant of "
                          "years -- Masha'allah's alternative, absent from PN IV and present in Sahl.")
        if not pn4['house_master']:
            st.markdown("No house-master to direct (see the section above).")
        else:
            for flag in pn4['hm_flags']:
                st.markdown(f"- {flag}")
            if pn4['hm_direction'] is None:
                st.warning("Refused at this latitude, as every direction by the oblique ascension is: it has no unique inverse there.")
            else:
                st.markdown(f"**{pn4['house_master']}**, the house-master, directed from its natal degree to the "
                            f"bodies, squares and oppositions of Saturn and Mars and to the Sun's degree, forward, "
                            f"a year to a degree of the birth latitude's ascensions, within {PN4_DISTRIBUTION_SPAN_YEARS:g} years:")
                if pn4['hm_direction']:
                    _hstrip = generate_hit_strip_svg(pn4['hm_direction'], pn4['elapsed_years'],
                                                     PN4_DISTRIBUTION_SPAN_YEARS, 'The house-master directed',
                                                     theme=WHEEL_THEME)
                    st.image(_hstrip, width='stretch')
                    st.download_button("Download this strip (SVG)", _hstrip, key="dl_strip_hm", mime="image/svg+xml",
                                       file_name="house_master_directed.svg")
                    st.dataframe(pd.DataFrame(pn4['hm_direction']), hide_index=True, width='stretch',
                                 height=_rows_height(len(pn4['hm_direction'])),
                                 column_config=_wide_text_columns(pd.DataFrame(pn4['hm_direction'])))
                else:
                    st.markdown("No target within the span.")
                if pn4['hm_this_year']:
                    st.markdown(f"**This year (age {pn4['age']}) is one the direction points out:** "
                                + '; '.join(f"{r['Target']} at {r['Degree']}, arc {r['Arc (years)']}" for r in pn4['hm_this_year'])
                                + ". 1.23, 3-4 now asks of the revolution:")
                else:
                    st.markdown(f"This year (age {pn4['age']}) is not one the direction points out. The revolution's "
                                f"facts for the house-master, for the record (1.23, 3-4):")
                st.dataframe(pd.DataFrame(pn4['hm_revolution']), hide_index=True, width='stretch',
                             height=_rows_height(len(pn4['hm_revolution'])),
                             column_config=_wide_text_columns(pd.DataFrame(pn4['hm_revolution'])))
            st.markdown(
                "**The join, and the denial beside it.** The house-master directed here is selected by NAWBAKHT'S "
                "rule (1.15, 13: the dignity lord looking at the releaser) and directed by MASHA'ALLAH'S operation "
                "(1.23, 2, \"direct it\" -- the governor); 1.23, 40 and 43 call Masha'allah's governor \"the "
                "house-master\" in Sahl's own words, but his governor is found by reception (1.23, 1), and the two "
                "rules name different planets in about a third of charts. The join is this app's; no sentence "
                "states it. Abu Ma'shar denies the direction: \"the indicator of the lifespan alone is turned in "
                "the signs, sign-by-sign, and is not directed degree-by-degree\" (PN IV IX.8, 32; fn 129: \"Some "
                "texts say that one can also distribute the house-master itself, but to me that seems like a "
                "misunderstanding\"). Shown as Sahl's, with the denial beside it. "
                "Two limits of the denial: IX.8, 32 restricts the "
                "ROLE -- the planet may still be directed in another capacity, since \"all of the planets and Lots "
                "are [also] directed\" (III.1, 5); and 1.16, 4 (direct the luminary \"even if a house-master is "
                "not looking\") is a provision the 1.16 exception built above does not cover. IX.8, 30's turning, "
                "the one operation Abu Ma'shar licenses for the indicator, follows as PN IV's:")
            if pn4['hm_turning']:
                st.dataframe(pd.DataFrame(pn4['hm_turning']), hide_index=True, width='stretch',
                             height=_rows_height(min(len(pn4['hm_turning']), 12)),
                             column_config=_wide_text_columns(pd.DataFrame(pn4['hm_turning'])))
            else:
                st.markdown("The turned sign reaches no cutter's body, opposition or square within the span.")
            st.caption(f"**{pn4['house_master']}** turned a year a sign from its natal sign (whole signs, as VI.2, 1), "
                       "the years in which the sign reaches a cutter's body, opposition or square: \"if the turning of "
                       "the years from any of the five releasers (or from the indicator of the lifespan) reached their "
                       "bodies, oppositions, or squares, then they also kill\" (PN IV IX.8, 30); \"the rest of the "
                       "rays' direction ... is a weak testimony\" (31) and is not shown. Read: \"their\" as Saturn's "
                       "and Mars's, the cutters the direction table targets.")
        st.caption("Readings: \"the degree of burning\" is the Sun's natal degree; \"a year for every degree of "
                   "ascensions\" is the oblique ascension of the birth latitude applied to the house-master's own "
                   "degree, as 1.15, 17, 1.16, 4 and 1.18, 21 apply \"the ascensions of that city\" to the "
                   "luminaries and the Ascendant alike, not PN IV III.1, 12's third case, the proportional "
                   "semi-arcs, which is Abu Ma'shar's assignment and not Sahl's); \"in the year of age\" is the "
                   "completed year the arc falls in. Facts, not judgment: "
                   "1.23, 4's verdict is quoted in the help and not pronounced. Not applied: 4.12, 6 (a retrograde "
                   "planet's rays directed conversely); 1.23, 5-11's further witnesses (the lord of the "
                   "revolution's Ascendant, the lord of the year, the profection reaching an infortune's sign), "
                   "which are the II.3 examination and the indicators in that chapter; 1.23, 13-14's redirection to the "
                   "lord of the Ascendant when the house-master is unsuitable is APPLIED below when a 1.23, 12 flag "
                   "fires; not applied: 1.23, 6; 1.23, 53-60's increase and "
                   "decrease of years; and the 1.21 additions. No worked example exists in Sahl.")
        if pn4['hm_redirect']:
            _rd = pn4['hm_redirect']
            st.markdown(f"**1.23, 13-14, the redirection** -- a 1.23, 12 flag stands on the house-master, so \"look at the "
                        f"coinciding of the lord of the Ascendant with the degree of the infortune (or its square or "
                        f"opposition), or its entrance into burning\" (13); the lord of the Ascendant here is "
                        f"**{_rd['lord']}**, directed in the house-master's stead; then the degree of the Ascendant (14). "
                        f"13's aggravation -- \"if the infortune was the lord of the house of the lord of the Ascendant, or "
                        f"the infortune was the lord of the house of the eighth\" -- holds for: "
                        f"{', '.join(_rd['aggravators']) or 'neither infortune'}.")
            for _lab, _tab in (("1.23, 13: the lord of the Ascendant, in the house-master's stead", _rd['lord_direction']),
                               ("1.23, 14: the degree of the Ascendant", _rd['ascendant_direction'])):
                st.markdown(f"*{_lab}*")
                if _tab is None:
                    st.warning("Refused at this latitude: the ascension has no unique inverse there.")
                elif _tab:
                    st.dataframe(pd.DataFrame(_tab), hide_index=True, width='stretch', height=_rows_height(min(len(_tab), 8)),
                                 column_config=_wide_text_columns(pd.DataFrame(_tab)))
                else:
                    st.markdown("No target within the span.")
        if pn4['father_lot']:
            _fl = pn4['father_lot']
            st.subheader("The father's Lot: its harmers and their direction (Sahl, *On Nativities* 4.20, 31-36)",
                         help="31: \"if the nativity was by day, the infortunes which harm his Lot are Mars and Saturn (and "
                              "Mercury, if he was unfortunate); and if it was by night, the infortunes which harm them are Mars "
                              "and Mercury (if he was unfortunate)\". 32: \"direct the degree of the Lot of the father and the "
                              "Sun by day, and by night the Lot and Saturn\". 33: \"if you found an infortune casting its rays "
                              "upon the Sun and upon the Lot ... it will kill the father when the direction reaches the "
                              "infortune which casts the rays\"; 34-35 rank two infortunes by enmity and power; 36: Saturn "
                              "\"from hostility\" is \"more harmful for some of the injuries\".")
            st.markdown(f"The Lot of the father stands at **{get_degree_string(_fl['lot'])}** (4.14, 1); the second point "
                        f"directed is **the {_fl['second']}** (32). fn 288 -- Dykes: Mars the main malefic in both sects, "
                        f"Saturn barred by night because he indicates the father, Mercury when made unfortunate -- is the "
                        f"editor's reading and is quoted, not applied; 31 is applied as printed.")
            st.dataframe(pd.DataFrame(_fl['harmers']), hide_index=True, width='stretch', height=_rows_height(len(_fl['harmers'])),
                         column_config=_wide_text_columns(pd.DataFrame(_fl['harmers'])))
            for _lab, _tab in (("From the degree of the Lot of the father (32), to the harmers' bodies, squares and oppositions", _fl['from_lot']),
                               (f"From the {_fl['second']} (32), to the same", _fl['from_second'])):
                st.markdown(f"*{_lab}*")
                if _tab is None:
                    st.warning("Refused at this latitude: the ascension has no unique inverse there.")
                elif _tab:
                    st.dataframe(pd.DataFrame(_tab), hide_index=True, width='stretch', height=_rows_height(min(len(_tab), 8)),
                                 column_config=_wide_text_columns(pd.DataFrame(_tab)))
                else:
                    st.markdown("No target within the span.")
            st.caption("Readings: \"casting its rays\" is met by the direction's targets, the harmers' bodies, squares and "
                       "oppositions (the same set as the house-master's direction; sextiles and trines are not directed); "
                       "the Sun is not a target here (4.20, 32 directs him). 33-35's choice between two infortunes is not made.")

    with tab_days:
        st.subheader("The small days: the revolution's Ascendant distributed round the year",
                     help="IX.7, 29: \"you look at the degree of the Ascendant of the revolution of the year, so "
                          "that you direct from it (for the knowledge of the conditions of the days), a day for "
                          "every 59' 08\", until it returns to the degree of the Ascendant at the end of the "
                          "year.\" IX.7, 30: a body or ray already in the bound of that degree manages until "
                          "another meets it; otherwise the bound lords, until a planet or ray is reached. IX.7, 31 "
                          "names it the small days. A second distribution, running inside the year at its own "
                          "rate; the Ascendant's distribution above runs across the years.")
        # IX.7, 31 / 27: the same two directions from any planet, house or Lot (order PN4R-4c-4)
        _sr_pd, _sr_ch = pn4['sr']['planetary_data'], pn4['sr']
        _day_points = {'the revolution\'s Ascendant (the table below)': None}
        _day_points.update({f"the revolution's {p_}": (_sr_pd[p_]['longitude'], f"the revolution's {p_}") for p_ in PN4_SEVEN if p_ in _sr_pd})
        _day_points.update({f"the revolution's house {i_ + 1} (cusp {get_degree_string(c_)})": (c_, f"the revolution's house {i_ + 1}")
                            for i_, c_ in enumerate(list(_sr_ch['houses'])[:12])})
        for _lr in calculate_topical_lots(_sr_pd, _sr_ch['ascendant'], _sr_ch['houses'], _sr_ch['sect']):
            if _lr['Supplement'] and READING_DEPTH != READING_DEPTH_OPTIONS[1]:
                continue
            _day_points[f"the revolution's {_lr['Lot']}"] = (lot_by_id(next(d['id'] for d in LOT_DEFINITIONS if d['name'] == _lr['Lot']),
                                                                      _sr_pd, _sr_ch['ascendant'], _sr_ch['houses'], _sr_ch['sect']),
                                                            f"the revolution's {_lr['Lot']}")
        # Through the store, like the View, Wheel layout and Inner wheel
        # controls beside it (M4 of the hostile pass of 2026-09-16): a plain
        # key is dropped by Streamlit the moment the page is not rendered,
        # so this one choice reset itself on every walk to another page and
        # back. The options are this revolution's own, so a stored choice
        # the current chart does not offer falls to the first option, which
        # is what _reading_select does with one.
        _day_choice = _reading_select("Also direct, for the small days (IX.7, 31) and the mighty days (IX.7, 27), from",
                                   list(_day_points), "pn4_day_point", "_pn4_day_point",
                                   help="IX.7, 31: \"you work like that with everything of the planets, Lots, and houses\". "
                                        "A READING: the \"houses\" are offered as the revolution's Alchabitius cusps, "
                                        "the degree this app computes for each house -- IX.7, 31 says \"houses\" and "
                                        "names no degree.")
        _extra = _day_points[_day_choice]
        if _extra is not None:
            _x_lon, _x_label = _extra
            _x_small = pn4_small_days(_sr_pd, _x_lon, _x_label)
            _x_cur = pn4_distribution_at_age(_x_small, pn4['day_of_year'])
            st.markdown(f"**Small days from {_x_label}** at {get_degree_string(_x_lon)} (IX.7, 31)"
                        + (f" -- now: distributor **{_x_cur['distributor']}**, partner **{_x_cur['partner'] or 'none'}**" if _x_cur else '') + ":")
            st.dataframe(pd.DataFrame(_pn4_distribution_rows(_x_small, _x_cur, unit='days', origin_jd=pn4['jd_sr'])),
                         hide_index=True, width='stretch', height=_rows_height(8))
            _x_prof = pn4_profect(_x_lon, pn4['age'])
            _x_mighty = pn4_mighty_days(_sr_pd, _x_prof, f"{_x_label}, profected")
            _x_mcur = pn4_distribution_at_age(_x_mighty, pn4['day_of_year'])
            st.markdown(f"**Mighty days from {_x_label} profected** to {get_degree_string(_x_prof)} (IX.7, 27: the "
                        f"point turned {pn4['age']} signs, its degree kept)"
                        + (f" -- now: distributor **{_x_mcur['distributor']}**, partner **{_x_mcur['partner'] or 'none'}**" if _x_mcur else '') + ":")
            st.dataframe(pd.DataFrame(_pn4_distribution_rows(_x_mighty, _x_mcur, unit='days', origin_jd=pn4['jd_sr'])),
                         hide_index=True, width='stretch', height=_rows_height(8))
        sd_cur = pn4['small_days_current']
        sr_asc = pn4['sr']['ascendant']
        _strip = generate_distribution_strip_svg(pn4['small_days'], pn4['day_of_year'], 'days', None, 'The small days',
                                                theme=WHEEL_THEME)
        st.image(_strip, width='stretch')
        st.download_button("Download this strip (SVG)", _strip, key="dl_strip_small", mime="image/svg+xml",
                           file_name="small_days.svg")
        if sd_cur:
            st.markdown(
                f"**Ascendant of the revolution** at {get_degree_string(sr_asc)} -- **now** (day "
                f"{pn4['day_of_year']:.1f} of the year): distributor **{sd_cur['distributor']}**, partner "
                f"**{sd_cur['partner'] or 'none -- the distributor acts alone'}**"
                f" &nbsp;|&nbsp; this period runs from day {sd_cur['from']:.1f} to {sd_cur['to']:.1f}"
                f" &nbsp;|&nbsp; opened standing on {get_degree_string(sd_cur['from_lon'])}")
        else:
            st.markdown(f"**Ascendant of the revolution** at {get_degree_string(sr_asc)} -- day "
                        f"{pn4['day_of_year']:.1f} is outside the year's circuit")
        st.dataframe(pd.DataFrame(pn4['small_days_rows']), hide_index=True, width='stretch',
                     height=_rows_height(min(len(pn4['small_days_rows']), 12)))
        st.caption("Zodiacal, by the sentence: 59' 08\" a day round the zodiac returns to the degree in 365.28 "
                   "days, the year to within an hour. Abu Ma'shar grades it himself -- \"there is an "
                   "approximation in it, but the correct [approach] is that this way of directing is like the "
                   "direction of the Sun every day ... [with] no harm in the work\" (IX.7, 32); that exact form "
                   "is not built, nor is Dykes's fn 178, which would direct by ascensions. What is read into the "
                   "sentence rather than stated by it: the bodies and rays are the revolution's; the days count "
                   "from the moment of the revolution (fn 161 leaves a \"day\" undefined); the partner already "
                   "in place is looked for behind the degree within its bound, the shape of III.1, 23-25 narrowed "
                   "to the window IX.7, 30 names, since the sentence does not say whether a body ahead in the "
                   "bound manages from the first day. The table below directs the revolution's Ascendant; IX.7, 31 "
                   "extends the method to every planet, Lot and house, and the selector above carries it out, "
                   "printing the small days from the point chosen and its profected mighty days beside them. "
                   "No worked example of it exists in PN IV.")

        st.subheader("The mighty days: the terminal degree of the year directed through the revolution",
                     help="IX.7, 23: \"you look in the revolution of the year at the degree of the sign which the "
                          "year terminated at, from the Ascendant of the root\" -- the terminal point -- and a body "
                          "or ray already in its bound manages until another meets it, else the lord of the bound "
                          "\"then the lord of the bound which follows it\" (IX.7, 24). IX.7, 25: the arc times "
                          "\"12 days, <4 hours>, 10 minutes, and 30 seconds (and that is 1/6 of a day and half a sixth "
                          "of a tenth of a day)\" -- the parenthetical's 12.175 d a degree is applied -- from the first day of the revolution; "
                          "IX.7, 28: thirty of them are the year, \"approximately\", and this is the mighty days. "
                          "The profected thirty degrees treated as a year, walked degree by degree.")
        md_cur = pn4['mighty_days_current']
        _strip = generate_distribution_strip_svg(pn4['mighty_days'], pn4['day_of_year'], 'days', None, 'The mighty days',
                                                theme=WHEEL_THEME)
        st.image(_strip, width='stretch')
        st.download_button("Download this strip (SVG)", _strip, key="dl_strip_mighty", mime="image/svg+xml",
                           file_name="mighty_days.svg")
        if md_cur:
            st.markdown(
                f"**Terminal point** at {get_degree_string(pn4['year']['longitude'])} -- **now** (day "
                f"{pn4['day_of_year']:.1f} of the year): distributor **{md_cur['distributor']}**, partner "
                f"**{md_cur['partner'] or 'none -- the distributor acts alone'}**"
                f" &nbsp;|&nbsp; this period runs from day {md_cur['from']:.1f} to {md_cur['to']:.1f}"
                f" &nbsp;|&nbsp; opened standing on {get_degree_string(md_cur['from_lon'])}")
        else:
            st.markdown(f"**Terminal point** at {get_degree_string(pn4['year']['longitude'])} -- day "
                        f"{pn4['day_of_year']:.1f} is outside the thirty degrees ({PN4_MIGHTY_DAYS_SPAN_DEGREES * PN4_MIGHTY_DAYS_PER_DEGREE:.2f} days)")
        st.dataframe(pd.DataFrame(pn4['mighty_days_rows']), hide_index=True, width='stretch',
                     height=_rows_height(min(len(pn4['mighty_days_rows']), 12)))
        st.caption("The rate. IX.7, 25 prints \"12 days, <4 hours>, 10 minutes, and 30 seconds (and that is 1/6 of "
                   "a day and half a sixth of a tenth of a day)\". Three figures stand in that sentence: the "
                   "manuscript's 12;10,30 days (10 minutes and 30 seconds as sexagesimal fractions OF A DAY, "
                   "12.175 d); the author's parenthetical, 12 + 1/6 + 1/120 = 12.175 d, thirty of which are "
                   "365 1/4 days exactly (IX.7, 28); and Dykes's hybrid 12 d 4 h 10 m 30 s (12.17396 d; thirty "
                   "of them 365 d 5 h 15 m), his \"<4 hours>\" supplied and the minutes read as clock time -- "
                   "fn 177 gives 12 d 4 h 12 m for a 365 1/4-day year, which is the author's fraction again. "
                   "APPLIED: the author's parenthetical, 12.175 d a degree. Zodiacal by construction -- "
                   "no ascension appears in the sentence; fn 175's report that ascensions would make more sense "
                   "is an editor's note. The direction does not stop at the end of the sign of the year: it "
                   "starts at the terminal degree and runs thirty degrees, so its last part lies in the bounds "
                   "of the next sign, which is what \"then to the lord of the bound which follows it\" "
                   "describes. Read into the sentence, as for the small days: the revolution's bodies and rays; "
                   "days from the moment of the revolution; the opening partner behind the degree within its "
                   "bound. IX.7, 27's extension to every planet, house and Lot is the selector above. "
                   "No worked example of it exists in PN IV.")

        st.subheader("The nine methods for the days and hours (IX.7, 1-72)",
                     help="\"The days and hours have nine indicators\" (IX.7, 1). 1: the days since birth in weeks "
                          "from the lord of the natal Ascendant (2-6). 2: seven days each from the lord of the orb "
                          "(7-9). 3: the year in greater and lesser sevenths from the lord of the revolution's "
                          "Ascendant (10-13). 4: the weeks to the signs (14-17). 5: the days to the signs by "
                          "twelves (18-20). 6 and 7: the mighty and small days above. 8: the month's days (34-39). "
                          "9: the ninth-parts, from the terminal sign, the revolution's Ascendant and the Moon "
                          "(43-72), worked at 57-69. IX.7, 56: all in equal hours. IX.7, 79 declines day and hour "
                          "charts and keeps these.")
        dm_rows, dm_month, dm_ninth = pn4['day_methods']
        st.dataframe(pd.DataFrame(dm_rows), hide_index=True, width='stretch', height=_rows_height(9),
                     column_config=_wide_text_columns(pd.DataFrame(dm_rows)))
        st.markdown("**8. The month's days** (IX.7, 34-39), from the four rooted monthly indicators (fn 181) and the month's Ascendant, Lot and Moon:")
        st.dataframe(pd.DataFrame(dm_month), hide_index=True, width='stretch', height=_rows_height(len(dm_month)),
                     column_config=_wide_text_columns(pd.DataFrame(dm_month)))
        st.markdown("**9. The ninth-parts** (IX.7, 43-72), from the three starts:")
        st.dataframe(pd.DataFrame(dm_ninth), hide_index=True, width='stretch', height=_rows_height(3),
                     column_config=_wide_text_columns(pd.DataFrame(dm_ninth)))
        st.caption("A \"day\" is a whole 24-hour period from the birth moment -- fn 161 says the book never says "
                   "whether from birth or from dawn -- and the moment read is the target date at noon. The "
                   "hours are equal (IX.7, 56): 3 3/7 apiece among seven (fn 164), 14 to a sign in a week (fn "
                   "173), two to a sign in a day (IX.7, 20), five to a sign in a sixty-hour slot (IX.7, 38). "
                   "Method 8's four rooted indicators are the monthly profections above (fn 181). Method 9's "
                   "partners are the domicile lords of the fifth and ninth signs from the ninth-part's, as the "
                   "worked example does (Capricorn, Taurus, Virgo: Saturn, Venus, Mercury); its month is 30 d "
                   "10 h 30 m and its ninth-part 3 d 9 h 10 m (IX.7, 54-55). Two of the example's printed "
                   "fractions are wrong, and are shown as printed: "
                   + '; '.join(f"{c} prints {p} for {e} ({fn})" for c, p, e, fn in PN4_IX7_EXAMPLE_ERRATA)
                   + ". The judgments of IX.7, 21-22 and 40-42 are not built.")

        st.subheader("The seven indicators of the month",
                     help="IX.1, 35-39. Five are \"rooted\" -- turned from the positions they hold at the "
                          "revolution of the year -- and two are not, being cast fresh from each monthly "
                          "revolution. They decrease in universality in the order given (IX.1, 39). The sign of "
                          "the year is itself month 1 (IX.1, 10), and months run from the revolution dates, not "
                          "the calendar.")
        PN4_MONTHLY_TURN_LOCAL = _reading_radio(
            "Monthly profections turn", list(PN4_MONTHLY_TURN_OPTIONS),
            "pn4_monthly_turn", "_pn4_monthly_turn",
            help="IX.1, 26-34: Abu Ma'shar turns the monthly indicators BACKWARDS when the sign is convertible, "
                 "and for a double-bodied sign forwards below 15°00' and backwards from it, because the first "
                 "half of a common sign is of the nature of the fixed sign before it and the second half of the "
                 "convertible sign after it (IX.1, 30). IX.1, 31 applies the test to each indicator's OWN sign, "
                 "individually. Indicator #2, the ninth-part, always runs forward (IX.1, 32). Dykes rejects the "
                 "whole rule as \"complicated, probably wrong\" and counts forward always; his reading is the "
                 "default here.")
        st.dataframe(pd.DataFrame(pn4['monthly_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['monthly_rows'])))
        st.caption(f"Month {pn4['month']} of 12. IX.1, 37: each is read against three positions -- the Ascendant "
                   "of the root (the column above), the sign of the terminal point, and the Ascendant of the "
                   "revolution. Indicator #2 is the lord of the first ninth-part of the sign of the year "
                   f"({pn4['ninth']['ninth_part_sign']}, lord {pn4['ninth']['lord']}); Abu Ma'shar himself "
                   "ignores it through most of Book IX (fn 15).")

    with tab_lords:
        st.subheader("Directing: which ascensions, and what a degree is worth")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**III.1, 12 -- the measure, by position**")
            st.dataframe(pd.DataFrame(PN4_ASCENSION_ROWS), hide_index=True, width='stretch')
            st.caption("The three cases do not stand alike. The **Ascendant** and the **meridian** are the "
                       "distributions above, each applied to the degree of its point and to a planet standing on "
                       "that degree itself (a numerical tolerance, no orb). The **third case** -- everything not on "
                       "one of the three degrees -- has no method in PN IV: III.1, 12 sends the reader to \"what we "
                       "stated in our book [on that topic]\", and Dykes's fn 16 (with VI.2, 21 fn 33) identifies it as "
                       "Ptolemy's proportional semi-arcs, which are applied from the texts that state the method "
                       "(" + PN4_SEMIARCS_SOURCES + "); no other ascension is substituted.")
            st.markdown("**III.1, 6 -- the unit, by level of chart**")
            st.dataframe(pd.DataFrame(PN4_UNIT_ROWS), hide_index=True, width='stretch')
        with c2:
            st.markdown("**III.1, 13 -- the rate ladder**")
            st.dataframe(pd.DataFrame(PN4_LADDER_ROWS), hide_index=True, width='stretch')
            st.caption("An idealised year of twelve 30-day months (fn 17). The bottom rung is **25 thirds**, a "
                       "sixtieth of a second of arc: 10″ is a day, so an hour is 10″/24 = 25‴ exactly. "
                       "(25″ would make an hour two and a half days long; the printed page, p. 288, has 25‴.)")

        st.subheader("The lords of the triplicity of the sect light, over the life",
                     help="Sahl, On Nativities 2.11, 1-2 (Theophilus; fn 148: Carmen I.24): \"If you found both of "
                          "the two lords of the triplicity of the luminary to be strong, they indicate high rank "
                          "from the beginning of his life to its end. And if one of the two was strong and the "
                          "other weak, his benefit will be in the time of the strong one of them, and his baseness "
                          "in the time of the one of them [that is falling]\"; 4: \"the partnering lord of the "
                          "triplicity supports them both in their elevation, through its strength (if it was "
                          "strong), and brings [them] down (if it was a falling [place])\". 2.13, 39: the first "
                          "lord \"indicates the end of the father's life, and the beginning of the native's "
                          "life\". 2.17, 5: \"if the third lord of the triplicity was in the house of marriage, he "
                          "will gain good fortune at the end of his lifespan\". PN IV VI.2, 4 names the same "
                          "lords \"at that time of his lifespan\".")
        st.dataframe(pd.DataFrame(pn4['life_lords_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['life_lords_rows'])),
                     column_config=_wide_text_columns(pd.DataFrame(pn4['life_lords_rows'])))
        st.caption("The three lords of the sect light's triplicity (the Sun's by day, the Moon's by night) in the "
                   "day-night-partner order for a day birth and night-day-partner for a night birth, each with its "
                   "natal condition. No text in hand assigns a number of years to any lord's stretch of the life, "
                   "so none is shown: fn 14 to VI.2, 4 (\"if the native was older, one would use the second "
                   "triplicity lord (or for many Persian- and Arabic-language astrologers, the third one)\") is "
                   "Dykes's gloss and gives no ages either. A split into three thirty-year stretches, as some "
                   "software prints, is stated nowhere.")
        if _reading_checkbox("Also show the Ascendant's triplicity lords, for comparison",
                             "life_lords_ascendant", "_life_lords_ascendant",
                             help="Some software divides the life by the lords of the ASCENDANT's triplicity. No "
                                  "text in hand does: the Ascendant's triplicity lords are the lords of upbringing "
                                  "(Sahl, On Nativities 1.29, 2-5; Appendix A, 9 fn 7), and every passage that "
                                  "gives a lord a time of the life keys it to the luminary. The rows are shown "
                                  "only so the difference can be seen."):
            st.dataframe(pd.DataFrame(pn4['life_lords_ascendant_rows']), hide_index=True, width='stretch',
                         height=_rows_height(len(pn4['life_lords_ascendant_rows'])))
        if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
            # al-Andarzaghar's per-house triplicity lords (coverage gap 9,
            # 2026-09-15): a separate table from Sahl's lords over the life
            # above; the sect order of first/second/third is al-Qabisi's own
            # (I.16, ITA I.7; 3.10 of the reconciliation, 2026-09-15).
            _andarzaghar_rows = evaluate_andarzaghar_triplicity_lords(chart_data['ascendant'], sect)
            _andarzaghar_first = ANDARZAGHAR_TRIPLICITY_LORDS[1]['text']
            _finding([], "The triplicity lords of the twelve houses, al-Andarzaghar",
                     "al-Qabisi I.57b-68 (al-Andarzaghar), in ITA I.13", _andarzaghar_rows,
                     standing="Supplement · display only",
                     glance="For each of the twelve houses, the three lords of its sign's triplicity beside what "
                            "al-Andarzaghar says each signifies, as al-Qabisi reports him house by house. Display "
                            "only; nothing scores it, and the lords' conditions are not read.",
                     notes="The lords are the Dorothean triplicity lords (day lord, night lord, partner) in the "
                           "chart's sect order -- by day the day lord first, by night the night lord first -- which "
                           "is the order al-Qabisi himself states for the lords of a triplicity (ITA I.7, al-Qabisi "
                           "I.16: by day the Sun and then Jupiter, by night Jupiter and then the Sun; Abu Ma'shar the "
                           "same at Gr. Intr. V.14, 6 and Abbr. I.86, and Sahl at On Nativities 10.2.7, 16), so his "
                           "own table reads al-Andarzaghar's \"first\", \"second\" and \"third\" Lord of "
                           "the triplicity; the house is the whole sign counted from the Ascendant. Each row's "
                           "words are al-Andarzaghar's as al-Qabisi reports them in the section named. For the "
                           f"first house (I.57b) whole: \"{_andarzaghar_first}\" (fn 158: \"the matter\" reads "
                           "with the Arabic for \"life\"). For the house of assets (I.58) he adds a rule this "
                           "table does not apply: \"see which one of them is stronger in being and place: you "
                           "will make this one deservedly the authority over assets and the significator of their "
                           "acquisition. Which if it were in the Mid-heaven, he will find this from the king; and "
                           "if it were in the house of faith, it will be better.\" The third house adds \"and "
                           "their worthiness will be according to their places\"; the seventh's \"uniting [with "
                           "others]\" is glossed \"partnerships and agreements\" (fn 172); the twelfth's "
                           "\"labors\" is \"or, 'suffering'\" in the Arabic (fn 192). Sahl's lords of the sect "
                           "light's triplicity over the life, above, are a different doctrine and are kept apart.",
                     height=_rows_height(len(_andarzaghar_rows)))

        st.subheader("The *fardar*",
                     help="IV.1, 2-4: the years are Sun 10, Venus 8, Mercury 13, Moon 9, Saturn 11, Jupiter 12, "
                          "Mars 7, Head 3, Tail 2 -- 75 in all. The order runs down the spheres from the light of "
                          "the sect: by day from the Sun, by night from the Moon. IV.7, 24: the Head and Tail come "
                          "LAST IN BOTH SECTS, \"whether the native was diurnal or nocturnal\" -- the point the "
                          "later tradition got wrong. IV.7, 25: after 75 the cycle returns to \"the luminary which "
                          "he began from at his birth\", not always to the Sun.")
        st.dataframe(pd.DataFrame(pn4['fardar_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['fardar_rows'])))
        st.caption("IV.1, 5-6: each planetary period divides into seven equal parts, the lord itself first, then "
                   "\"the planet which is below it in the celestial circle\". IV.1, 8: the Nodes have no "
                   "sub-periods, \"because they do not have houses\". I.8, 35 says the order follows the planets' "
                   "exaltations; it does not, and Book IV governs -- an inconsistency inside PN IV, recorded.")

        st.subheader("When a natal indication comes out (III.7, 32-42)",
                     help="A planet may distribute or manage more than once in a lifetime (III.7, 32), and this "
                          "chapter asks how often what it promised in the root actually manifests, and at what "
                          "ages. HOW OFTEN is keyed to the quadruplicity of its natal sign: fixed, \"in [only] a "
                          "single time\" (35); convertible, \"in [only] one of the times\" (39); double-bodied, "
                          "\"on an occasional basis\" (38). AT WHAT AGE: \"the number of ascensions of the sign in "
                          "which it was in the root, or the amount of one of its own years\" (42). What Abu "
                          "Ma'shar himself adds is the last column -- the effect is \"strong, evident, notable\" "
                          "when such an age falls where that same planet is the distributor or the manager.")
        st.dataframe(pd.DataFrame(pn4['activation_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['activation_rows'])))
        st.caption("**All three grades are shown and none is chosen.** III.7, 35 picks among the greater, middle "
                   "and lesser years \"in accordance with what its position in the rotation of the circle "
                   "indicated in the root\" -- and never states that rule. It is the same placement question "
                   "*On Times* 4, 7 and *On Nativities* 1.20 disagree about, which PN IV does not adjudicate. "
                   "**Two things in Dykes's fn 191 are also absent**: the SUM of the ascensions and the years, and "
                   "a third, a half and two-thirds of it, are introduced with \"if we follow Valens\" and appear "
                   "in no sentence of III.7; and his worked figure of 20.17 ascensional times for Taurus at 45N "
                   "is not reproduced, the exact computation giving 20.09. III.7, 35's \"once\" is for a fixed-sign "
                   "planet \"NOT looking at the position of the distribution\"; the looking is computed here as the "
                   "whole-sign aspect from the natal sign to the Ascendant's sign at birth (a planet in the sign counted "
                   "as looking) -- whether the position is the current bound's sign or its degree, and whether "
                   "co-presence counts, are silences -- and a looking fixed planet's row says III.7, 36 applies "
                   "\"whenever it distributes\" IF strong, which the chapter does not define, so no row is promoted. "
                   "The confirmation column (III.7, 42) is checked against the distributions of the Ascendant, the "
                   "Midheaven, the fourth and the releaser, each named; the planets' own semi-arc directions are "
                   "not among them, no sentence asking for a planet to confirm itself. "
                   "III.7, 37 exempts the manager, which \"will produce its indication\" whenever it manages.")

        st.subheader("The Ages of Man",
                     help="I.8, 10-26 and Figure 53 (PN IV): Ptolemy's seven ages, ordered by sphere from the lowest "
                          "upward -- not the quadrant scheme of Sahl, On Nativities 3.9. Each span is a planet's "
                          "lesser years, or a half or a tenth of its lesser or middle years (I.8, 9). The Moon's 4 "
                          "is a tenth of her middle years, 39 1/2 (I.8, 12) -- an independent witness for the "
                          "luminary construction of the middle years used elsewhere in this app.")
        st.dataframe(pd.DataFrame(pn4['age_rows']), hide_index=True, width='stretch',
                     height=_rows_height(len(pn4['age_rows'])))
        st.caption("The last age is open-ended: Figure 53 (PN IV) tabulates Saturn as 30 years and ages 68-97, but the "
                   "prose governs -- the seventh age runs \"until the end of his lifespan\" (I.8, 25). Abu Ma'shar "
                   "refuses to subdivide an age into sevenths the way a *fardar* is subdivided, so there is no "
                   "sub-lord here (I.8, 34-35).")

        st.subheader('Chronocrator Matrix', help='Two rows: the lord of the year by annual profection, and the Egyptian bound lord of the Ascendant directed symbolically at one degree per year -- which is not a distribution, as its label says. Abu Ma\'shar names the shortcut himself and grades it: "there is an approximation in it, but the correct [approach] is that this way of directing is like the direction of the Sun every day" (IX.7, 32). The ascensional method he prefers is the jar bakhtar table above.')
        st.dataframe(pd.DataFrame(time_lords_data), hide_index=True, width='stretch')
        # The one heading the short-headings branch left carrying its
        # own metadata: the citation and the standing move to a
        # caption under it, the shape _finding() prints, so the
        # heading is the table's name and nothing else.
        st.subheader("Planetary years",
                     help="The lesser, middle, greater and mighty years and the fardar of each planet, beside its placement, "
                          "the grade On Nativities 1.20, 7-34 would give it as house-master (placed by the division, the "
                          "POWER unit) and what On Times 4, 7 -- a question-chart rule, 4, 2 -- would "
                          "give it, for comparison. Applied to one planet only: the house-master the Timing page names "
                          "from On Nativities 1.15, whose grant is printed there with its sentence.")
        st.caption("Display only · Gr. Intr. VII.8, Figure 146")
        st.dataframe(pd.DataFrame(planetary_years_data), hide_index=True, width='stretch', height=_rows_height(len(planetary_years_data)))
        if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
            st.caption("The last column, beside each \"1.20 silent\" cell only: the class Abu 'Ali's ladder gives the "
                       "planet (JN Ch. 3), its count from Ch. 4's table, and the steps taken. "
                       + JN_YEARS_NOTE.replace('<', chr(92) + '<'))

    with st.expander("What Persian Nativities IV does not settle", icon=":material/help:"):
        st.markdown(
            "The Timing page leaves these items open. "
            "Each is absent because **the book does not answer it**, not because the work was skipped.\n\n"
            "**The releaser and the house-master.** PN IV names five releasers -- \"the Sun, Moon, Ascendant, "
            "Lot of Fortune, or the degree of the meeting or degree of the opposition\" (III.3, 1) -- and says "
            "all five are directed (III.1, 3). It never says **how to choose among them**, how many years the "
            "house-master grants, how increasers and decreasers are counted, or how to judge a planet that "
            "passes one test and fails another. Abu Ma'shar says so himself: those \"who look into it are "
            "wandering around in the dark; but a statement of the truth of that ... is found in the book which "
            "we worked on concerning nativities\" (IX.8, 123) -- a book not in hand. Two texts in hand do "
            "answer parts of it: al-Qabisi states the choice among the five and the house-master's order with "
            "its tie-breaks -- the lord stronger in the releaser's place that looks at it, going down the "
            "order until one does; equal claimants decided by the stronger in its own place, then the nearer "
            "degree; and if no lord looks at the releaser it is unfit and the next is taken (ITA VIII.1.3, "
            "al-Qabisi IV.4-6); Abu 'Ali states how the fortunes add and the infortunes subtract -- a fortune "
            "joined or in trine or sextile adds its lesser years, an infortune joined or in square or "
            "opposition subtracts its own, and the other rays of each add or subtract nothing (Judgments of "
            "Nativities Ch. 4). Both are stated in those texts, not built here; the choice stays Sahl's. Here "
            "the choice is made from **Sahl**, *On Nativities* 1.15 (Nawbakht), and the house-master is directed "
            "per 1.23, 2 (Masha'allah), in the chapter named The releaser, with every reading that step needed said "
            "there; the releaser's distribution feeds the governor's testimony #3 and the luminary proxies. "
            "The distribution **from the Ascendant** remains the *jar bakhtar* of II.2, 6-7.\n\n"
            "**Where the greater years are granted.** *On Nativities* "
            "1.20, 7-34 is the one natal grant in these texts -- *On Times* 4 is a question-chart chapter (\"in the hour "
            "of the question\", 4, 2) and 1.23, 68 sends the reader to \"the section on the house-master\" -- so "
            "the house-master's years are granted from 1.20 in The releaser chapter, placed by the division; the "
            "Planetary years table shows 1.20's grade for every planet and *On Times* 4, 7 for comparison; PN IV is "
            "silent (IX.8, 123) and III.2, 110-111's gate now has the input it names.\n\n"
            "**Directing anything that is not the Ascendant or the meridian.** III.1, 12 sends the reader to "
            "\"what we stated in our book [on that topic]\" for every other point, and PN IV never states it. "
            "Dykes's fn 16 identifies the method as Ptolemy's proportional semi-arcs; it is applied from the "
            "texts in hand that state it (" + PN4_SEMIARCS_SOURCES + "), and the page says which choices "
            "those texts leave open.\n\n"
            "**Revolutions of the day and the hour.** Defined in principle (I.3, 10-13) and then declined by "
            "the author: \"there is no need for us [to do] that, because these nine indicators ... are complete "
            "for everything needed\" (IX.7, 79).\n\n"
            "**The unit of a directed degree by sign type, strength or planet.** PN IV keys the unit to the "
            "level of the chart (III.1, 6) and answers a different question from the one the two authors' "
            "disagreements ask; it is not evidence on either side of them.\n\n"
            "**The Indian rule for the lord of the year** -- the lord of the first ninth-part of the sign of "
            "the year (III.10, 1-5), which would restrict the lord of the year to Mars, Venus, Saturn and the "
            "Moon. PN IV reports it without adopting it, so it is used here only as monthly indicator #2, "
            "which is where IX.1, 36 puts it. The ninth-parts themselves are al-Qabisi's and Abu Ma'shar's too "
            "-- each sign in nine divisions of 3 1/3 degrees, the first to the lord of the movable sign of the "
            "triplicity and the rest in the order of the signs (ITA VII.5, al-Qabisi IV.16-17 and Abbr. "
            "VII.22-23, Figure 110) -- but no other text in hand makes the first ninth-part's lord the lord of the year.")

    with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
        st.markdown(
            "**The rate ladder's bottom rung is 25‴** -- twenty-five thirds of a degree to the hour, III.1, 13 "
            "(25″ would make an hour two and a half days long; the arithmetic settles it) -- and **the *fardar* "
            "order is the prose's, IV.1, 2-4**, of which Figure 43 (p. 116) is the table.\n\n"
            "**One printed error is not reproduced.** Intro Sect. 2 (p. 7) puts the monthly "
            "revolutions at 12° **23′** when the natal Sun is at 12° **22′**. The page "
            "genuinely prints that, and it is contradicted by the rule in its own sentence, by IX.1, 23, by "
            "IX.3, 2, and by Dykes's own worked example at Intro Sect. 9 p. 95. The degree **and minute** are "
            "carried unchanged into every sign.\n\n"
            "**The lord of the year is the lord of the *sign* of the year** (II.3, 1), Persian *salkhudhah* "
            "-- not the lord of the revolution's Ascendant and not a victor. \"Governor\" (Ar. *mustawli*), "
            "the sign on which most of the year's indicators coincide (IX.9, 10), is a different term, and "
            "PN IV keeps \"Ascendant of the year\" and \"sign of the year\" carefully apart (Intro Sect. 8, "
            "p. 77) where Sahl's English does not.\n\n"
            "**Figure 146 (VII.8, p. 487)**, verified against the prose restatement at VII.8, 3-8 and the "
            "fardar total the text gives (\"that is 75 years\", VII.8, 3), agrees with PN IV's IV.1, 2 cell "
            "for cell. **On Times Ch. 4, 7:** \"if the ruler was in a stake, eastern, it grants its greater "
            "years; or if it was in what follows the stakes, it grants its middle years; and if it was "
            "falling, it grants its lesser years.\" **On Nativities 1.20, 10-17:** greater in the Ascendant, "
            "Midheaven, sign of the west or eleventh when enhanced (10), or under the earth, eastern, in a "
            "share, enhanced (11); middle in the second or eighth (16), or in the eleventh or fifth when not in a share "
            "and not eastern (17). The two disagree, PN IV does not adjudicate them, and no row is chosen; "
            "the house-master's years on the Releaser tab are Sahl's 1.20 in full, On Times 4, 7 being a "
            "question-chart rule.")

def page_sources():
    st.header("Sources and readings")
    _chart_strip()
    st.caption("What the app reads from, how it can be read, and what it does not cover.  \n"
               "**How citations are written.** A locator names its volume, never the author alone: "
               "*Sahl, The Introduction Ch. 3, 85* and *Sahl, On Nativities 1.22, 9*; *Gr. Intr. VII.6, 27* "
               "is Abu Ma'shar's Great Introduction (Dykes); *PN IV IX.1, 26* is his On the Revolutions of "
               "the Years of Nativities, Persian Nativities IV (Dykes) -- and on the Timing page, whose rules "
               "all come from that book, its locators are bare Book.chapter, sentence. Both of Abu Ma'shar's "
               "volumes have a Book VII, which is why his name alone no longer locates anything. *ITA I.22 "
               "(al-Qabisi)* is Dykes's Introductions to Traditional Astrology, its section and the author excerpted "
               "there (al-Qabisi's own numbering, *al-Qabisi IV.4*, where it is given); *Abu Bakr, On Nativities "
               "II.5.14*, *'Umar al-Tabari, Book of Nativities I.4.3*, *Masha'allah, Book of Aristotle III.1.8* and "
               "*Abu 'Ali al-Khayyat, Judgments of Nativities Ch. 4* are the four nativity treatises of Persian "
               "Nativities I and II (Dykes); *Abbr. II.27* is Abu Ma'shar's Abbreviation as ITA prints it.")
    # --- The readings in force (2026-09-10) ----------------------------
    st.subheader("Readings in force",
                 help="Every doctrinal switch, where it is set, what it says now and what the default "
                      "is. They are remembered between runs. Reset returns all of them to the defaults. "
                      "Sources shown is stored under the two names the table prints: Course text, which is "
                      "Sahl's course texts alone, and Course text and supplement, which is those texts with "
                      "Abu Ma'shar's beside them.")
    _reading_radio("Sources shown", READING_DEPTH_OPTIONS, "reading_depth", "_reading_depth",
                   format_func={READING_DEPTH_OPTIONS[0]: "Sahl's course texts",
                                READING_DEPTH_OPTIONS[1]: "With Abu Ma'shar's supplement"}.get,
                   help="Sahl's course texts: the tables of Sahl's Introduction and On Nativities alone, with "
                        "Abu Ma'shar's Great Introduction VII kept apart in its own tab on the Configurations "
                        "page and behind closed expanders elsewhere. With Abu Ma'shar's supplement: his tables "
                        "are laid beside Sahl's on the same topic -- further findings, three more topical "
                        "Lots, a reference table and the supplementary expanders open -- and the Configurations "
                        "page folds his tab into the topic blocks it belongs to.")
    _rows = [{'Reading': label, 'In force': str(_reading(wk, sk, default)), 'Default': str(default),
              'Set on': page, 'Differs': 'yes' if _reading(wk, sk, default) != default else ''}
             for label, wk, sk, default, page in READINGS_REGISTRY]
    st.dataframe(pd.DataFrame(_rows), hide_index=True, width='stretch', height=_rows_height(len(_rows)),
                 column_config=_wide_text_columns(pd.DataFrame(_rows)))
    if st.button("Reset every reading to the defaults", icon=":material/restart_alt:"):
        for _label, wk, sk, _default, _page in READINGS_REGISTRY:
            st.session_state.pop(wk, None)
            st.session_state.pop(sk, None)
            _forget(sk)
        st.rerun()
    # The full comparison of the two connection tests. It was the
    # Connection rule radio's tooltip; the radio (Configurations page)
    # now carries a one-line help and points here.
    st.subheader("Connection rule: Sahl and Abu Ma'shar")
    st.markdown(
        "Which author's rule decides whether a pair counts as Connected. The two agree that "
        "looking is sign-to-sign and connecting is degree-to-degree, but they part company at "
        "the sign boundary and on what activates a connection.\n\n"
        "**Sahl** (The Introduction Ch. 3, 6-21): the applying planet's OWN light governs "
        "(15/12/9/8/7 by planet), so the test is asymmetric. A planet at the end of a sign that "
        "is not connecting with anything, whose light strikes into the next sign, IS connected "
        "to the first planet there by body (20-21) -- even though the two do not see each other.\n\n"
        "A DISSENTING READING is recorded in the code but not implemented. Sahl 13 says that with "
        "15 degrees between THE SUN and a planet 'he has already shone his light, and he is connected "
        "with [the planet]' -- and the Sun is the HEAVIER body there -- while 18 closes the list of "
        "lights with 'they are connected ONE TO THE OTHER'. Against that, 19 states the test itself in "
        "terms of the mover ('it already struck WITH ITS OWN LIGHT'), and Abu Ma'shar, using the same "
        "orb table, needs the asymmetry: with Saturn and the Moon within 12 degrees 'Saturn is in the "
        "power of the Moon's body while the Moon is NOT YET in the power of Saturn's' (VII.4, 7). The "
        "asymmetric reading is kept; the reciprocal one would move about 5% of applying pairs, and only "
        "half of those involve the Sun.\n\n"
        "**Abu Ma'shar** (Gr. Intr. VII.4-5): two flat distances instead -- assembly "
        "within 15 degrees in one sign (VII.4, 3), aspects within 12 degrees of exact (VII.5, 27, "
        "since aspect rays have no bodies of their own). No out-of-sign connection at all: across "
        "a boundary the bodies merely 'mix their natures in a weak way' (VII.5, 14).\n\n"
        "This governs only the tables that deliberately present BOTH authors -- the aspect grid, "
        "reception, blocking, cutting. Each author's own tables are computed under "
        "that author's rule whatever this is set to; the Configurations page has its own "
        "control for which author you want to SEE."
    )
    # The five readings the sources leave open. Each control sits on
    # the page and table it changes with a one-line help; the full
    # text of each, as it stood in the sidebar, is here.
    st.subheader("Configurable readings")
    st.markdown(
        "**VII.6, 27/45 'eastern/western relative to the Sun'** (Configurations page, Planetary Condition) -- "
        "'hemisphere': the whole half, excluding the rays (VII.2, 2; VII.6, 34). 'VII.2 band': only "
        "the easternizing band 15/18 to 90 degrees (VII.2, 14-21) and the westernizing band 90 down to "
        "15 degrees (VII.2, 29-31). Superiors: 52% vs 25% of placements. "
        "Affects: Planetary Condition (27, 45).\n\n"
        "**Moon under the rays to 15 degrees (Sahl, On Nativities 1.19, 6)** (Chart page, Planetary Positions) -- "
        "Gr. Intr. VII.2, 61 and 72-73 give 12; Sahl gives 15 for the Moon's fitness as releaser. "
        "Affects: the Solar phase column of Planetary Positions; on the Configurations page, "
        "Weakness of the Planets (93), Planetary Condition and Corruption of the Moon.\n\n"
        "**Mars under the rays to 18 degrees west (Dykes's table in On Nativities 1.22, fn 175)** (Chart page, Planetary Positions) -- "
        "Gr. Intr. VII.2, 31 has Mars under the rays at 15 on the western side; Dykes's chapter-head table for "
        "Sahl, with fn 175 reading VII.2, 30's westernizing boundary into 18, has him at 18; Sahl's own sentences "
        "are silent on Mars west. Both agree on 18 east. Affects: the Solar phase column and every test that "
        "reads it; a 3-degree band on one planet.\n\n"
        "**Fitting infortune (Sahl, Choices Ch. 1, 12)** (Configurations page, beside the Connection test) -- "
        "\"the infortunes are perhaps more fitting for him, since [one] may be the lord of the original Ascendant\"; "
        "off by default because 1, 16-17 says the opposite. When on, the malefic ruling the Ascendant is not an "
        "infortune for any affliction test; it keeps its nature where that is what is meant.\n\n"
        "**Domain (hayz)** (Dignities page, Sect table) -- "
        "Gr. Intr. VII.1, 37 / VII.6, 13: sign gender fixed to the planet's own. Masha'allah, "
        "On Nativities 1.23, 17: a male planet by day above the earth in a male sign, by night under "
        "the earth in a FEMALE sign; feminine planets by hemisphere only. "
        "Affects: the Sect table and Dignity Evaluation on the Dignities page, and Planetary Condition (13) "
        "on the Configurations page.\n\n"
        "**House-based Lots measure to the** (Lots page, Topical Lots) -- "
        "'The second place', 'the degree of the eighth place', 'the ninth' (On Nativities 2.15, 1; "
        "8.6, 1; Ch. 9, 9). Whole-sign: the Ascendant's degree carried into that sign. Quadrant: the "
        "Alchabitius cusp. "
        "Affects: Topical Lots."
    )
    with st.expander("Coverage: what these sources contain that this app does not", expanded=False):
        st.caption(
            "Named explicitly so the absence is a stated scope limit rather than an "
            "implied claim of completeness."
        )
        st.dataframe(pd.DataFrame(
            [{'Passage': a, 'Not implemented': b} for a, b in NOT_IMPLEMENTED_COVERAGE]),
            hide_index=True, width='stretch')

# --- Reference tables (2026-09-10): the app's Handy Tables ---------------
# The course hands out the Handy Tables; the app holds every one of
# them as data and used to print them in five places. One static
# page, lesson-tagged, that reads no chart.
def page_reference():
    st.header("Reference tables")
    _chart_strip()
    st.caption("The reference tables, printed from the data this app computes with. Nothing on this "
               "page reads the chart in the sidebar.")
    _sources_scope_line()

    st.subheader("Dignities by sign",
                 help="Domicile, exaltation, the three triplicity lords (day, night, participating) "
                      "and the three faces of each sign, as the app holds them. The exaltation degrees are "
                      "the standard scheme (Gr. Intr. V.5, Figure 38) and are printed only here.")
    rows = []
    for i, sign in enumerate(SIGN_ORDER):
        exalted = next((p for p, signs in EXALTATIONS.items() if sign in signs), None)
        trip = TRIPLICITY[SIGN_ELEMENT[sign]]
        faces = [get_essential_rulers(i * 30 + d)['face'] for d in (5, 15, 25)]
        rows.append({'Sign': sign, 'Domicile': SIGN_TO_DOMICILE[sign],
                     'Exaltation': f"{exalted} ({EXALTATION_DEGREES[exalted]}°)" if exalted else '-',
                     'Triplicity, day': trip['Day'], 'Triplicity, night': trip['Night'],
                     'Participating': get_essential_rulers(i * 30 + 15)['triplicity_participating'],
                     'Faces (1st, 2nd, 3rd)': ' · '.join(faces)})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch', height=_rows_height(12))
    st.caption("Sources: Sahl, The Introduction Ch. 1; the exaltation degrees Gr. Intr. V.5 (Figure 38), the standard "
               "scheme -- Hermes's (V.7, Figure 39) differ only for Jupiter and Mercury, the 16th degree of Cancer and "
               "of Virgo against the 15th. "
               "Triplicity lords are Dorothean (Gr. Intr. V.14, 6-9; Figure 53 (Gr. Intr.)); Virgo's partner is "
               "Mercury 'in preference to' Mars (V.14, 7; fn 100). Faces are read at 5, 15 and 25 degrees of each sign.")

    st.subheader("Egyptian bounds",
                 help="The bounds every distribution of Part 2 runs through (III.1, 11). The "
                      "same table the app directs by; pinned against four independent witnesses.")
    bound_rows = []
    for sign in SIGN_ORDER:
        row, start = {'Sign': sign}, 0
        for n, (limit, lord) in enumerate(EGYPTIAN_TERMS[sign], 1):
            row[f'{pn4_ordinal(n)} bound'] = f"{lord} {start}°–{limit - 1}°59′"
            start = limit
        bound_rows.append(row)
    st.dataframe(pd.DataFrame(bound_rows), hide_index=True, width='stretch', height=_rows_height(12))

    st.subheader("Orders of the dignities, and the good places",
                 help="How Sahl ranks the dignities in three of his works, and which "
                      "places each of his schemes calls good.")
    st.dataframe(pd.DataFrame([{'Context': k, 'Order, strongest first': ' > '.join(v)} for k, v in DIGNITY_ORDER.items()]),
                 hide_index=True, width='stretch')
    st.dataframe(pd.DataFrame([{'Scheme': k, 'Places': (', '.join(f"{g}: {p}" for g, p in v.items()) if isinstance(v, dict) else str(v))}
                               for k, v in GOOD_PLACE_SCHEMES.items()]), hide_index=True, width='stretch')
    st.caption(SEVEN_PLACE_RANKING_NOTE)

    st.subheader("Planetary years",
                 help="The lesser, middle, greater and mighty years of each planet, with the "
                      "fardar period (PN IV IV.1, 2). A reference table: the one grant of years this app makes, "
                      "the house-master's from On Nativities 1.20, is on the Timing page's Releaser tab.")
    years = reference_planetary_years_rows()
    st.dataframe(pd.DataFrame(years), hide_index=True, width='content', height=_rows_height(len(years)))
    st.caption("Gr. Intr. VII.8, Figure 146; the fardar periods PN IV IV.1, 2. The "
               "middle years use two constructions, the ordinary mean for the planets and (least + great/2)/2 "
               "for the luminaries, which Valens VII.5 states outright: \"The sun has half of 120 years and hence "
               "receives 60; its minimum period is 19. The total is 79, half of which is 39 years, 6 months.\" "
               "The Moon's is the same, half of 108 with 25, 79 halved. So the luminaries' 39 1/2 has four "
               "witnesses in hand -- Valens VII.5; Gr. Intr. VII.8, 3-8 with Figure 146; Abu Bakr, On Nativities I.16, the same "
               "construction in prose (half the greater years added to the lesser, the sum halved); PN IV I.8, 12, "
               "the Moon's 4 as a tenth of her middle years -- and three against it that take the ordinary mean, "
               "the Sun 69 1/2 and the Moon 66 1/2: Masha'allah, Book of Aristotle III.1.8; Abu 'Ali al-Khayyat, "
               "Judgments of Nativities Ch. 4; and the Latin Great Introduction's table of the years as Dykes prints "
               "it (ITA VII.2, Figure 108). This app keeps 39 1/2, the Arabic Great Introduction's, the table it "
               "reads for the rest of the row. Valens's Venus is a complete period of 84 (half 46), not Figure "
               "146's 82 -- a variant not adopted.")

    st.subheader("Degrees of nobility and rank",
                 help="Sahl, On Nativities 1.38, 39-41 and Figure 57 of his volume: the degrees in which, with the "
                      "Ascendant or a luminary in one, \"he will reach exaltation and power, or he will rule many "
                      "lands\". The Chart page checks this chart's points against it.")
    _nob_rows = [{'Sign': sg, 'Sahl (On Nativities 1.38, 41)': ', '.join(str(d) for d in NOBILITY_DEGREES.get(sg, [])) or '-'}
                 for sg in SIGN_ORDER]
    if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
        for row in _nob_rows:
            row["Abu Ma'shar (Gr. Intr. V.22, 4)"] = ', '.join(str(d) for d in ELEVATION_DEGREES.get(row['Sign'], [])) or '-'
    st.dataframe(pd.DataFrame(_nob_rows), hide_index=True, width='content', height=_rows_height(12))
    st.caption("Sahl\'s figure prints bare degrees, read here as ordinals -- how Abu Ma\'shar\'s Figure 64 prints the same rule\'s degrees. "
               "Dykes resolves the ordinal to a point: on the inconsistency between cardinal and ordinal numbers in "
               "these tables his sense is that the authors meant the end of the nineteenth degree, that is 19° (ITA I.3 "
               "fn 23), the point at which the ordinal span tested here (18° to 19° for the nineteenth) ends. Al-Qabisi\'s own table of the same rule "
               "(al-Qabisi I.53, ITA VII.9, Figure 118) is a third list, printed as ordinals and disagreeing with both "
               "Sahl\'s and Abu Ma\'shar\'s; it is not tabled here. "
               + ("Abu Ma'shar's column is the supplement's: the same rule, stated at V.22, 4 with Figure 64's table, "
                  "twelve signs to Sahl's eight, six of the eight disagreeing; the text reconciles none of it."
                  if READING_DEPTH == READING_DEPTH_OPTIONS[1] else
                  "Abu Ma'shar states the same rule with a table of his own; Course text and supplement lays it beside this one."))

    if READING_DEPTH == READING_DEPTH_OPTIONS[1]:
        st.subheader("The natures of the planets (Gr. Intr. IV.1)",
                     help="Abu Ma'shar's report of what Ptolemy said of each planet's nature, hot or cold and "
                          "wet or dry (Gr. Intr. IV.1, 6-12), each sentence's words beside the reading. A "
                          "supplement table: this app computes with no planet's nature.")
        st.dataframe(pd.DataFrame(PLANET_NATURES_IV1), hide_index=True, width='content',
                     height=_rows_height(len(PLANET_NATURES_IV1)),
                     column_config=_wide_text_columns(pd.DataFrame(PLANET_NATURES_IV1)))
        st.caption("Display only: Abu Ma'shar's report of Ptolemy, \"this is what Ptolemy claimed about the "
                   "natures of the planets\" (Gr. Intr. IV.1, 13); his own objections follow at IV.1, 15-43 and "
                   "are not tabled. Nothing in this app reads a planet's nature.")

    st.subheader("The Ages of Man",
                 help="PN IV I.8, 10-26: the seven ages, each ruled by a planet for its lesser years in the "
                      "Chaldean order from the Moon. The Timing page marks the native's own age in it.")
    age_rows, from_year = [], 0
    for planet, years_, description in PN4_AGES_OF_MAN:
        age_rows.append({'Age': description, 'Ruler': planet, 'Years': years_,
                         'From': from_year, 'To': from_year + years_})
        from_year += years_
    st.dataframe(pd.DataFrame(age_rows), hide_index=True, width='stretch', height=_rows_height(len(age_rows)))

pages = {
    "Part 1: the nativity": [
        # The default page is served at the ROOT path, never at
        # /chart: Page.url_path returns "" when default is set, and
        # st.navigation registers that empty pathname, so /chart is not
        # a route and the browser falls back to root. url_path= stays
        # all the same, because Page._script_hash is calc_hash of the
        # PRIVATE _url_path, which keeps the string it was given: it is
        # the page's identity inside the app (and the string the
        # regression harness hashes to select this page). Dropping it
        # would rename the page to "page_chart" for no gain.
        st.Page(page_chart, url_path="chart", title="Chart", icon=":material/explore:", default=True),
        st.Page(page_dignities, url_path="dignities", title="Dignities and places", icon=":material/shield:"),
        st.Page(page_findings, url_path="findings", title="Findings", icon=":material/menu_book:"),
        st.Page(page_configurations, url_path="configurations", title="Configurations", icon=":material/hub:"),
        st.Page(page_lots, url_path="lots", title="Lots", icon=":material/functions:"),
        st.Page(page_victors, url_path="victors", title="Lunation and victors", icon=":material/trophy:"),
    ],
    "Part 2: prediction": [
        st.Page(page_timing, url_path="timing", title="Timing", icon=":material/schedule:"),
    ],
    "Reference": [
        st.Page(page_reference, url_path="reference", title="Reference tables", icon=":material/table_chart:"),
        st.Page(page_sources, url_path="sources", title="Sources and readings", icon=":material/menu_book:"),
    ],
}
# The page list is a header bar across the top, not the first thing in
# the sidebar: the sidebar is the nativity form, and it opens on the
# Date field with Save inside the fold. expanded= is read only when
# position="sidebar", so it goes with the move.
st.navigation(pages, position="top").run()
