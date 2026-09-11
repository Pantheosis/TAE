import swisseph as swe
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, time, timedelta
from itertools import combinations, product
from contextlib import contextmanager
from xml.sax.saxutils import escape
from timezonefinder import TimezoneFinder
import pytz
from pathlib import Path
import math
import re
import json
import sqlite3
import os
import sys

# ==========================================
# 0. SAVED CHART PERSISTENCE
# ==========================================
# Charts are saved as {name: {date_string, time_string, location_query}} in a
# small JSON file. Only the raw natal inputs are stored -- the full chart is
# cheaply recomputed on load rather than serialized.
#
# This lives in the OS's per-user data directory, NOT next to app.py: a
# packaged build's own folder (_internal) gets replaced whole by every new
# download, which used to silently wipe saved charts on every update unless
# the file was manually copied out and back in first.
def _user_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    path = Path(base) / "TraditionalAstrologyEngine"
    path.mkdir(parents=True, exist_ok=True)
    return path

SAVED_CHARTS_PATH = _user_data_dir() / "saved_charts.json"
# Where this file used to live -- checked once so anyone upgrading from
# before this change doesn't have to move it by hand.
_LEGACY_SAVED_CHARTS_PATH = Path(__file__).parent / "saved_charts.json"

def _validate_chart_mapping(charts):
    """The saved-charts file is {chart name: entry dict}. Valid JSON is not
    enough: '[]' parsed fine and then crashed the sidebar at .keys(). Only
    the shape the UI actually indexes is checked -- a mapping of string
    names to mapping entries -- so an older entry missing a field still
    loads."""
    if not isinstance(charts, dict):
        raise ValueError(f"saved charts root must be a mapping, got {type(charts).__name__}")
    for name, entry in charts.items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            raise ValueError(f"saved chart {name!r} is not a name -> mapping entry")
    return charts

def _read_chart_mapping(path):
    """The validated mapping in `path`, or None if it is unreadable,
    malformed, or the wrong shape."""
    try:
        return _validate_chart_mapping(json.loads(path.read_text()))
    except (json.JSONDecodeError, OSError, ValueError):
        return None

def _write_text_atomically(path, text):
    """Write to a sibling temp file and os.replace() it over the target, so
    a crash or full disk mid-write leaves the previous file intact rather
    than a truncated one that loses every saved chart."""
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(text)
    os.replace(tmp, path)

def load_saved_charts():
    if not SAVED_CHARTS_PATH.exists() and _LEGACY_SAVED_CHARTS_PATH.exists():
        legacy = _read_chart_mapping(_LEGACY_SAVED_CHARTS_PATH)
        if legacy is not None:
            try:
                _write_text_atomically(SAVED_CHARTS_PATH, json.dumps(legacy, indent=2))
            except OSError:
                pass
    if SAVED_CHARTS_PATH.exists():
        charts = _read_chart_mapping(SAVED_CHARTS_PATH)
        return {} if charts is None else charts
    return {}

def write_saved_charts(charts):
    try:
        _validate_chart_mapping(charts)
        _write_text_atomically(SAVED_CHARTS_PATH, json.dumps(charts, indent=2))
        return True
    except (OSError, ValueError):
        return False

# --- Preferences (2026-09-10) -------------------------------------------
# The readings and display choices, kept across runs in the same per-user
# directory as the saved charts (UI_REVIEW_2026-09-10.md §2). Streamlit's
# own persist_state lives only as long as the session, so a restart needs
# a file. Only the store keys listed here are kept, plus the name of the
# last chart loaded, which the app opens on. Missing or unknown keys are
# ignored on read, as the saved-charts loader ignores them. The harness
# sets ALMUTEN_NO_PREFERENCES=1 so a test can neither read a real file
# nor leak a reading into the next test.
PREFERENCES_PATH = _user_data_dir() / "preferences.json"
READING_DEPTH_OPTIONS = ("Course text", "Course text and supplement")
PREFERENCE_KEYS = (
    # doctrinal readings, each set on the page it affects
    '_connection_rule', '_eastern_rule', '_moon_rays_15', '_mars_west_18',   # '_five_degree_all_cusps' retired 2026-09-11
    '_fitting_infortune', '_domain_rule', '_lot_house_cusp', '_pn4_monthly_turn', '_reading_depth',
    # display
    '_wheel_layout', '_chart_bounds', '_timing_bounds', '_wheel_order', '_timing_lots', '_timing_rays',
    '_timing_twelfths', '_timing_wheel_view', '_target_mode',
)

PREFERENCE_RENAMES = (
    ('_pn4_monthly_turn', "Abu Ma'shar IX.1, 26-34", "PN IV IX.1, 26-34"),
    ('_wheel_order', "Revolution inside (Abu Ma'shar, I.6)", "Revolution inside (Abu Ma'shar's order, PN IV I.6)"),
)

def preferences_enabled():
    return os.environ.get("ALMUTEN_NO_PREFERENCES") != "1"

def load_preferences():
    """The stored preferences as a dict, keys limited to PREFERENCE_KEYS and
    'last_chart'; an empty dict when there is no file, or it is unreadable,
    or the harness has switched preferences off."""
    if not preferences_enabled() or not PREFERENCES_PATH.exists():
        return {}
    try:
        raw = json.loads(PREFERENCES_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}
    prefs = {k: v for k, v in raw.items() if k in PREFERENCE_KEYS or k == 'last_chart'}
    # Option values renamed by the citation convention of 2026-09-10 (a
    # locator names its volume, never the author alone); a file written
    # before it still loads.
    for key, old_value, new_value in PREFERENCE_RENAMES:
        if prefs.get(key) == old_value:
            prefs[key] = new_value
    return prefs

def write_preferences(prefs):
    if not preferences_enabled():
        return False
    try:
        _write_text_atomically(PREFERENCES_PATH, json.dumps(prefs, indent=2, sort_keys=True))
        return True
    except OSError:
        return False

# ==========================================
# 1. CORE CALCULATION ENGINE
# ==========================================

@st.cache_data(max_entries=32, show_spinner=False)
def _sin_altitude(ecl_lon, ecl_lat, distance, obliquity, armc, geo_lat):
    """Sine of a body's geocentric altitude above the horizon of geo_lat:
    sin(alt) = sin(phi) sin(delta) + cos(phi) cos(delta) cos(H), with the
    hour angle H = ARMC - RA and RA/delta from the body's actual ecliptic
    longitude, latitude and distance (swe.cotrans). No refraction, no
    parallax. Positive is above the horizon. This, not the ecliptic proxy
    (lon - Ascendant) % 360 > 180, decides sect and which luminary was up:
    the proxy inverts near the poles and on the horizon (fixed 2026-09-08)."""
    ra, decl, _r = swe.cotrans((ecl_lon, ecl_lat, distance), -obliquity)
    p, d, h = map(math.radians, (geo_lat, decl, armc - ra))
    return math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(h)

# --- The civil calendar ---------------------------------------------------
# ONE policy, in one place. The digits of a civil date are a JULIAN-calendar
# date before 1582-10-15 and a Gregorian one from that day on, as Solar Fire
# and astro.com read them; the Swiss Ephemeris manual (s. 9.1) keeps the two
# flags apart for exactly this reason. Using the wrong flag mis-dates a
# historical chart by days (seven in the 1200s), which the Moon turns into
# tens of degrees.
#
# Python's datetime is proleptic Gregorian and CANNOT HOLD a Julian-only day:
# 1300-02-29 exists in the Julian calendar and not in the Gregorian. So the
# carrier of a civil date in this file is CivilDate / CivilMoment below, and a
# shift by a UTC offset is done on the Julian Day, never by datetime
# arithmetic. The earlier adapter subtracted the offset with datetime,
# producing Gregorian components, and then read those digits back as Julian:
# local Julian 1300-03-01 00:30 at +02:00 came out a full day wrong (Astra
# audit 2026-09-11, F01). Rounding a moment to the second is done on the JD
# too, so that a carry across midnight is a date carry, not a clamp.
PN4_GREGORIAN_REFORM_JD = 2299160.5     # 1582-10-15 00:00 UT, the first Gregorian day
_MONTH_ABBR = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
_MONTH_NAME = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
               'September', 'October', 'November', 'December')

def civil_calendar(year, month, day):
    """swe.JUL_CAL or swe.GREG_CAL for a civil date's digits, by the policy above."""
    return swe.GREG_CAL if (int(year), int(month), int(day)) >= (1582, 10, 15) else swe.JUL_CAL

def civil_is_valid(year, month, day):
    """Whether the digits name a day in the calendar the policy assigns them:
    1300-02-29 is valid (Julian), 1900-02-29 is not (Gregorian)."""
    year, month, day = int(year), int(month), int(day)
    if not (1 <= year <= 9999 and 1 <= month <= 12 and 1 <= day <= 31):
        return False
    cal = civil_calendar(year, month, day)
    y, m, d, _h = swe.revjul(swe.julday(year, month, day, 0.0, cal), cal)
    return (int(y), int(m), int(d)) == (year, month, day)

def civil_to_jd(year, month, day, hour=0.0):
    """The Julian Day of a civil moment (UT hour, decimal), calendar by policy."""
    return swe.julday(int(year), int(month), int(day), float(hour), civil_calendar(year, month, day))

def civil_local_to_jd_ut(year, month, day, hour_local, utc_offset_hours):
    """A LOCAL civil moment to UT as a Julian Day: the calendar is decided by
    the local digits, the offset (east positive, hours) is subtracted on the
    JD. This is the sidebar's adapter for LMT and manual offsets."""
    return civil_to_jd(year, month, day, hour_local) - float(utc_offset_hours) / 24.0

def _format_civil(c, spec):
    """strftime's common directives for CivilDate / CivilMoment: %Y %m %d %b
    %B %H %M %S %%. Anything else is left in place."""
    if not spec:
        return c.isoformat()
    out, i = [], 0
    while i < len(spec):
        ch = spec[i]
        if ch == '%' and i + 1 < len(spec):
            d = spec[i + 1]
            rep = {'Y': f"{c.year:04d}", 'm': f"{c.month:02d}", 'd': f"{c.day:02d}",
                   'b': _MONTH_ABBR[c.month - 1], 'B': _MONTH_NAME[c.month - 1],
                   'H': f"{getattr(c, 'hour', 0):02d}", 'M': f"{getattr(c, 'minute', 0):02d}",
                   'S': f"{getattr(c, 'second', 0):02d}", '%': '%'}.get(d)
            if rep is not None:
                out.append(rep)
                i += 2
                continue
        out.append(ch)
        i += 1
    return ''.join(out)

class CivilDate:
    """A civil date as digits, read in the calendar civil_calendar() assigns
    them. Carries a birth or target date where datetime.date used to, and
    unlike it can hold a Julian-only day. Compares equal to anything with
    the same year, month and day (a datetime.date included)."""
    __slots__ = ('year', 'month', 'day')

    def __init__(self, year, month, day):
        self.year, self.month, self.day = int(year), int(month), int(day)

    @classmethod
    def of(cls, d):
        return d if isinstance(d, cls) else cls(d.year, d.month, d.day)

    @classmethod
    def from_jd(cls, jd):
        cal = swe.GREG_CAL if jd >= PN4_GREGORIAN_REFORM_JD else swe.JUL_CAL
        y, m, d, _h = swe.revjul(jd, cal)
        return cls(y, m, d)

    def tuple(self):
        return (self.year, self.month, self.day)

    def __eq__(self, other):
        try:
            return self.tuple() == (int(other.year), int(other.month), int(other.day))
        except (AttributeError, TypeError, ValueError):
            return NotImplemented

    def __lt__(self, other):
        return self.jd() < CivilDate.of(other).jd()

    def __hash__(self):
        return hash(self.tuple())

    def __sub__(self, other):
        # a timedelta (days) back, or the number of days between two dates
        if hasattr(other, 'days') and not hasattr(other, 'year'):
            return CivilDate.from_jd(self.jd() - other.days)
        return self.jd() - CivilDate.of(other).jd()

    def __add__(self, other):
        return CivilDate.from_jd(self.jd() + other.days)

    def jd(self, hour=0.0):
        return civil_to_jd(self.year, self.month, self.day, hour)

    def replace(self, **kw):
        return CivilDate(kw.get('year', self.year), kw.get('month', self.month), kw.get('day', self.day))

    def calendar_name(self):
        return 'Julian' if civil_calendar(self.year, self.month, self.day) == swe.JUL_CAL else 'Gregorian'

    def isoformat(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def __format__(self, spec):
        return _format_civil(self, spec)

    def __str__(self):
        return self.isoformat()

    def __repr__(self):
        return f"CivilDate({self.year}, {self.month}, {self.day})"

class CivilMoment(CivilDate):
    """A CivilDate with a time of day (whole seconds), UT or local as the
    caller says. from_jd rounds the JD to the second FIRST, so a moment a
    fraction of a second before midnight carries into the next day."""
    __slots__ = ('hour', 'minute', 'second')

    def __init__(self, year, month, day, hour=0, minute=0, second=0):
        super().__init__(year, month, day)
        self.hour, self.minute, self.second = int(hour), int(minute), int(second)

    @classmethod
    def from_jd(cls, jd):
        jd = round(float(jd) * 86400.0) / 86400.0
        cal = swe.GREG_CAL if jd >= PN4_GREGORIAN_REFORM_JD else swe.JUL_CAL
        y, m, d, hour = swe.revjul(jd, cal)
        total = min(int(round(hour * 3600.0)), 24 * 3600 - 1)
        return cls(y, m, d, total // 3600, (total % 3600) // 60, total % 60)

    def hour_decimal(self):
        return self.hour + self.minute / 60.0 + self.second / 3600.0

    def jd(self, hour=None):
        return civil_to_jd(self.year, self.month, self.day, self.hour_decimal() if hour is None else hour)

    def isoformat(self):
        return f"{super().isoformat()} {self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    def __repr__(self):
        return f"CivilMoment({self.year}, {self.month}, {self.day}, {self.hour}, {self.minute}, {self.second})"

def calculate_traditional_chart(dt_utc, lat, lon):
    """A chart from a UT moment given as anything with year, month, day,
    hour, minute and second (a datetime or a CivilMoment); the digits are
    read in the calendar the policy above assigns them."""
    jd = civil_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                     dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
    return calculate_traditional_chart_jd(jd, lat, lon)

def calculate_traditional_chart_jd(jd, lat, lon):
    """The chart at a Julian Day (UT). The sidebar arrives here directly, so
    a Julian-only date and an offset across midnight need no datetime."""
    # The seven planets' ephemeris ids are PLANET_SWE_IDS, defined once with
    # the VII.6 material; the chart adds the TRUE Node (owner's decision of
    # 2026-09-07, matching the reference charts; the mean node sat 1-2 degrees
    # off them). The true node's speed is carried like a planet's, and it is
    # not always retrograde: it has short direct spells, which the wheel
    # reports as they are rather than assuming the mean node's constant
    # backward motion.
    targets = {**PLANET_SWE_IDS, 'North Node': swe.TRUE_NODE}
    
    planetary_data = {}
    for name, obj_id in targets.items():
        res, _ = swe.calc_ut(jd, obj_id)
        planetary_data[name] = {
            'longitude': res[0],
            'latitude': res[1],
            'distance': res[2],
            'speed_in_lon': res[3],
            # Latitude and distance speeds are carried so that Abu Ma'shar's
            # conditions "in themselves" (Gr. Intr. VII.1) can be
            # told apart from their static counterparts: VII.6, 22 and 38
            # distinguish "RISING UP in the north" from merely "being
            # northern," and "GOING DOWN in the south" from being southern.
            'speed_in_lat': res[4],
            'speed_in_dist': res[5],
        }

    cusps, ascmc = swe.houses(jd, lat, lon, b'B')
    ascendant = ascmc[0]
    mc = ascmc[1]
    descendant = (ascendant + 180.0) % 360.0
    ic = (mc + 180.0) % 360.0
    
    # True obliquity of the ecliptic at the moment (Lesson 5 worksheet
    # line 15); computed here because sect needs it below.
    obliquity = swe.calc_ut(jd, swe.ECL_NUT)[0][0]

    # Sect from the Sun's ALTITUDE (_sin_altitude above), not from its
    # ecliptic longitude against the Ascendant. The old test, (Sun -
    # Ascendant) % 360 > 180, asked whether the Sun's ecliptic degree lies
    # in the eastern or western half-zodiac, which agrees with the horizon
    # at ordinary latitudes but not near the poles (2026-01-01 00:00 UT at
    # 70S: Sun three degrees up, read as Nocturnal) nor exactly on the
    # horizon, where the Sun's own ecliptic latitude decides. Fixed
    # 2026-09-08.
    sun = planetary_data['Sun']
    is_diurnal = _sin_altitude(sun['longitude'], sun['latitude'], sun['distance'], obliquity, ascmc[2], lat) > 0.0
    sect = 'Diurnal' if is_diurnal else 'Nocturnal'

    # From its LOT_DEFINITIONS row, like every other Lot in the file.
    lot_of_fortune = lot_by_id('fortune', planetary_data, ascendant, cusps, sect)

    return {
        'julian_day': jd,
        'planetary_data': planetary_data,
        'houses': cusps,
        'ascendant': ascendant,
        'descendant': descendant,
        'mc': mc,
        'ic': ic,
        'sect': sect,
        'lot_of_fortune': lot_of_fortune,
        # Lesson 5 worksheet lines 14 and 15: the right ascension of the
        # meridian from the same houses call, and the true obliquity of the
        # ecliptic at the moment. Read by the Chart page's Calculation table.
        'armc': ascmc[2],
        'obliquity': obliquity,
        # The place, so that evaluators needing the horizon (hayz: above or
        # below the earth by ALTITUDE, Astra F04) can be handed it from the
        # chart alone.
        'geo_lat': lat,
        'geo_lon': lon,
    }

# ==========================================
# 2. HELPER FUNCTIONS & VARIATION-SELECTOR-FREE RENDERER
# ==========================================

SIGN_ORDER = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_zodiac_sign(longitude):
    # Longitudes are circular: exactly 360.0 is 0 Aries, not a thirteenth
    # sign. Every public geometry helper normalises at its own door.
    return SIGN_ORDER[int((longitude % 360.0) // 30)]

def get_degree_string(longitude):
    """A longitude as DD° Sgn MM'. Display policy: whole arcminutes,
    TRUNCATED (12°27'40" prints 27'), with one tolerance -- a value within a
    millionth of a minute of a whole minute IS that minute. Binary floats
    put 30 + 1/60 a hair under 00° Tau 01' and int() printed 00' (Astra
    F13); an entered whole minute now survives display. The carry at 60',
    30° and 360° follows from working in total minutes. Nothing here
    rounds the longitude itself; bound and degree tests read the float."""
    total = (longitude % 360.0) * 60.0
    nearest = round(total)
    if abs(total - nearest) < 1e-6:
        total = nearest
    total = int(total) % (360 * 60)
    deg_total, minute = divmod(total, 60)
    return f"{deg_total % 30:02d}° {SIGN_ORDER[deg_total // 30][:3]} {minute:02d}'"

# ---- The chart wheel ---------------------------------------------------
# Redesigned 2026-09-07 (brief: WHEEL_REDESIGN_2026-09-07.md, decisions
# D1-D10). generate_hybrid_svg() is a pure function -- no Streamlit calls --
# returning an SVG string that the Chart page shows through st.image(), which
# wraps it in Streamlit's own fullscreen control, the same expand arrows the
# tables carry. Inside an <img> the SVG has no page CSS, web fonts or scripts,
# so everything here is attributes and system fonts.
#
# Rings, outside in: a rim band with the WHOLE-SIGN place numbers; the sign
# band with the glyphs, shaded by triplicity, and a one-degree scale on its
# inner edge; the planet zone, where each point's label runs radially --
# glyph, degree, sign, minute, and a black retrograde mark -- as the owner's
# reference charts draw it; a narrow ring with the ALCHABITIUS house numbers;
# and the hub, which names the chart. The rising sign's boundary sits at
# 9 o'clock (D1: the app's own convention, kept), so whole-sign places fall on
# the twelve clock positions. Alchabitius cusps stay dashed (the app's
# convention) and now run from the quadrant ring to the degree scale.
WHEEL_LAYOUT_OPTIONS = ('Square', 'Wide')
WHEEL_SIZE = 1000                     # viewBox of the square wheel
WHEEL_WIDE_WIDTH = 1760               # the wide variant: wheel plus a positions panel
_R_RIM, _R_WS_IN, _R_SIGN_IN = 492, 462, 402
_R_GLYPH, _R_DEG, _R_SIGN, _R_MIN, _R_RX = 344, 306, 272, 242, 214
_R_Q_OUT, _R_Q_IN = 152, 122
_R_BOUNDS_BAND = 24                   # the Egyptian-bounds ring, inside the degree scale, when drawn
LABEL_MIN_SEP = 10.5                  # degrees between neighbouring label stacks
LABEL_STAGGER = 30                    # px inward for alternate members of a crowded run
# One tint per triplicity (D3): fire, earth, air, water; sign i uses i % 4.
TRIPLICITY_TINT = ('#f7f7f7', '#dedede', '#ededed', '#cdcdcd')
_WHEEL_FONT = "'Noto Sans Symbols', 'Segoe UI Symbol', 'DejaVu Sans', sans-serif"
_CUSP_COLOUR = '#a94442'
_AXIS_COLOUR = {0: '#0000cc', 6: '#0000cc', 9: '#1e7b1e', 3: '#1e7b1e'}   # horizon blue, meridian green (D4)
_VS = '︎'                        # text-presentation selector: never an emoji
SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍',
               '♎', '♏', '♐', '♑', '♒', '♓']
POINT_GLYPHS = {'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀',
                'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄',
                'North Node': '☊', 'South Node': '☋', 'Lot of Fortune': '⊗'}


def _spread_labels(bearings, min_sep=LABEL_MIN_SEP):
    """Push neighbouring bearings apart on the circle until every adjacent
    pair is at least min_sep degrees apart. bearings are in ascending order
    around the circle; that circular order is preserved and the result
    comes back in the same order. Input already separated is unchanged.

    The sequence is unwrapped to a monotone one first and the gaps kept
    SIGNED, so a pair pushed apart cannot leapfrog its neighbours (a
    modular gap would read the overshoot as a wide gap and leave the order
    scrambled). A negative gap is a violation like any other and is pushed
    open on the next sweep."""
    n = len(bearings)
    if n < 2:
        return [b % 360.0 for b in bearings]
    min_sep = min(min_sep, 0.9 * 360.0 / n)       # n labels must fit the circle
    pos = [bearings[0] % 360.0]
    for b in bearings[1:]:
        b = b % 360.0
        while b < pos[-1]:
            b += 360.0
        pos.append(b)
    for _ in range(1000):
        moved = False
        for k in range(n):
            j = (k + 1) % n
            gap = (pos[j] + (360.0 if j == 0 else 0.0)) - pos[k]
            if gap < min_sep - 1e-6:
                push = (min_sep - gap) / 2.0
                pos[k] -= push
                pos[j] += push
                moved = True
        if not moved:
            break
    return [p % 360.0 for p in pos]


def _stagger_offsets(true_bearings, shown_bearings, step=LABEL_STAGGER):
    """Within each run of consecutive displaced labels, every other one
    steps inward by `step` px, as Solar Fire does for stellia."""
    displaced = [abs(((s - t + 180.0) % 360.0) - 180.0) > 0.05 for s, t in zip(shown_bearings, true_bearings)]
    offsets = [0] * len(displaced)
    k = 0
    while k < len(displaced):
        if displaced[k]:
            end = k
            while end < len(displaced) and displaced[end]:
                end += 1
            for n, idx in enumerate(range(k, end)):
                offsets[idx] = step if n % 2 else 0
            k = end
        else:
            k += 1
    return offsets


def _wheel_dm(longitude):
    """Degree and minute within the sign, minutes truncated exactly as
    get_degree_string() truncates them, so the wheel and the tables agree."""
    longitude = longitude % 360.0
    return int(longitude % 30), int((longitude % 1) * 60)


def generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, dt_local, tz_name,
                        wide=False, chronocrats=None, bounds=False):
    size = WHEEL_SIZE
    cx = cy = size / 2.0
    asc = chart_data['ascendant']
    mc = chart_data['mc']
    cusps = chart_data['houses']
    asc_sign = int((asc % 360.0) // 30)
    angles = (asc, mc, (asc + 180.0) % 360.0, (mc + 180.0) % 360.0)

    # D1: the rising sign's boundary at 9 o'clock, zodiac counter-clockwise.
    # The geometry and the two primitives are shared with the multi-ring
    # wheels of the Timing page (2026-09-10).
    ang, xy, sector, _arc = _wheel_geometry(asc_sign, cx, cy)
    line, text = _svg_line, _svg_text
    # An Egyptian-bounds ring inside the degree scale (2026-09-10): every
    # natal wheel in PN IV carries one (Figures 1, 22, 25, 26). It sits in
    # the leader zone, so the planet stack is not moved.
    r_planet_edge = _R_SIGN_IN - _R_BOUNDS_BAND if bounds else _R_SIGN_IN

    def sign_glyph(longitude):
        return SIGN_GLYPHS[int((longitude % 360.0) // 30)] + _VS

    width = WHEEL_WIDE_WIDTH if wide else size
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {size}" width="{width}" height="{size}" '
           f'style="font-family:{_WHEEL_FONT}">',
           f'<rect width="{width}" height="{size}" fill="#ffffff"/>']

    # 1. Sign band shaded by triplicity, sign glyphs, whole-sign place
    #    numbers on the rim, boundary spokes through both bands.
    for i in range(12):
        a0, a1 = ang(i * 30), ang(i * 30 + 30)
        svg.append(f'<path d="{sector(_R_SIGN_IN, _R_WS_IN, a0, a1)}" fill="{TRIPLICITY_TINT[i % 4]}"/>')
        svg.append(f'<path d="{sector(_R_WS_IN, _R_RIM, a0, a1)}" fill="#ffffff"/>')
        # An angle box (step 4) sits wherever the Ascendant or MC falls in its
        # sign; a glyph within 7 degrees of one steps 8 degrees aside.
        glyph_lon = i * 30 + 15
        for angle_lon in angles:
            gap = ((angle_lon - glyph_lon + 180.0) % 360.0) - 180.0
            if abs(gap) < 7.0:
                glyph_lon = i * 30 + 15 - (8 if gap > 0 else -8)
        gx, gy = xy((_R_SIGN_IN + _R_WS_IN) / 2, ang(glyph_lon))
        svg.append(text(gx, gy, SIGN_GLYPHS[i] + _VS, 30))
        hx, hy = xy((_R_WS_IN + _R_RIM) / 2, ang(i * 30 + 15))
        svg.append(text(hx, hy, str((i - asc_sign) % 12 + 1), 17, 'bold'))
        x0, y0 = xy(_R_SIGN_IN, a0); x1, y1 = xy(_R_RIM, a0)
        svg.append(line(x0, y0, x1, y1, '#000000', 1.2))

    # 2. Degree scale on the inner edge of the sign band: 1, 5 and 10 degrees.
    for d in range(360):
        ln = 14 if d % 10 == 0 else 10 if d % 5 == 0 else 5
        x0, y0 = xy(_R_SIGN_IN, ang(d)); x1, y1 = xy(_R_SIGN_IN + ln, ang(d))
        svg.append(line(x0, y0, x1, y1, '#000000', 0.9 if ln > 5 else 0.5))
    if bounds:
        svg.extend(_bounds_ring_svg(ang, xy, sector, r_planet_edge, _R_SIGN_IN, glyph_px=12))
    for r, w in ((_R_RIM, 2.5), (_R_WS_IN, 1.2), (_R_SIGN_IN, 1.6), (_R_Q_OUT, 1.2), (_R_Q_IN, 1.6)):
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000000" stroke-width="{w}"/>')

    # 3. Alchabitius cusps, dashed as before but reaching the degree scale;
    #    the four stakes solid and coloured. House numbers at mid-house on
    #    the quadrant ring.
    for i, cusp_lon in enumerate(cusps):
        x0, y0 = xy(_R_Q_IN, ang(cusp_lon)); x1, y1 = xy(r_planet_edge, ang(cusp_lon))
        if i in _AXIS_COLOUR:
            svg.append(line(x0, y0, x1, y1, _AXIS_COLOUR[i], 2.6))
        else:
            svg.append(line(x0, y0, x1, y1, _CUSP_COLOUR, 1.4, '6 4'))
        mid = cusp_lon + ((cusps[(i + 1) % 12] - cusp_lon) % 360.0) / 2.0
        mx, my = xy((_R_Q_OUT + _R_Q_IN) / 2, ang(mid))
        svg.append(text(mx, my, str(i + 1), 14, 'bold', _CUSP_COLOUR))

    # 4. Angle boxes on the sign band: degree over minute, in the axis colour.
    for angle_lon, colour in zip(angles, ('#0000cc', '#1e7b1e', '#0000cc', '#1e7b1e')):
        d, m = _wheel_dm(angle_lon)
        bx, by = xy((_R_SIGN_IN + _R_WS_IN) / 2, ang(angle_lon))
        svg.append(f'<rect x="{bx - 19:.1f}" y="{by - 17:.1f}" width="38" height="34" rx="3" '
                   f'fill="#ffffff" stroke="{colour}" stroke-width="1.2"/>')
        svg.append(text(bx, by - 8, f'{d:02d}°', 13, 'bold', colour))
        svg.append(text(bx, by + 8, f"{m:02d}'", 13, 'bold', colour))

    # 5. Points. The seven planets and the north node from the ephemeris, the
    #    south node opposite it with the same motion (D2), the Lot of Fortune
    #    with no motion. A retrograde mark goes on any point whose longitude
    #    speed is negative, nodes included (D9): the true node has direct
    #    spells and is shown as it moves.
    p_data = chart_data['planetary_data']
    node = p_data['North Node']
    points = [(name, d['longitude'], d.get('speed_in_lon', 0.0)) for name, d in p_data.items()]
    points.append(('South Node', (node['longitude'] + 180.0) % 360.0, node.get('speed_in_lon', 0.0)))
    points.append(('Lot of Fortune', chart_data['lot_of_fortune'], None))
    points.sort(key=lambda p: ang(p[1]))
    true_bearings = [ang(p[1]) for p in points]
    shown = _spread_labels(true_bearings)
    offsets = _stagger_offsets(true_bearings, shown)
    for (name, lon_val, speed), a_true, a_shown, off in zip(points, true_bearings, shown, offsets):
        # A tick on the ring at the true degree, a hairline from it to the glyph.
        x0, y0 = xy(r_planet_edge, a_true); x1, y1 = xy(r_planet_edge - 10, a_true)
        svg.append(line(x0, y0, x1, y1, '#000000', 1.6))
        x2, y2 = xy(_R_GLYPH - off + 22, a_shown)
        svg.append(line(x1, y1, x2, y2, '#666666', 0.8))
        d, m = _wheel_dm(lon_val)
        gx, gy = xy(_R_GLYPH - off, a_shown); svg.append(text(gx, gy, POINT_GLYPHS.get(name, name[:2]) + _VS, 34))
        dx_, dy_ = xy(_R_DEG - off, a_shown); svg.append(text(dx_, dy_, f'{d:02d}°', 18, 'bold'))
        sx, sy = xy(_R_SIGN - off, a_shown); svg.append(text(sx, sy, sign_glyph(lon_val), 19))
        mx, my = xy(_R_MIN - off, a_shown); svg.append(text(mx, my, f"{m:02d}'", 15))
        if speed is not None and speed < 0:
            rx, ry = xy(_R_RX - off, a_shown); svg.append(text(rx, ry, '℞' + _VS, 15))   # black (D6)

    # 6. Hub: the chart's name first (D5 supplies "Transits" when none was
    #    given), then when, where, and the systems in force. User strings
    #    are escaped: a name or place with & or < would otherwise break the
    #    whole wheel.
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{_R_Q_IN - 1}" fill="#ffffff"/>')
    name = str(chart_name)
    if len(name) > 30:
        name = name[:29] + '…'
    name_px = 17 if len(name) <= 16 else 14 if len(name) <= 22 else 11
    lat_s = f"{int(abs(lat))}°{int((abs(lat) % 1) * 60):02d}′{'N' if lat >= 0 else 'S'}"
    lon_s = f"{int(abs(lon))}°{int((abs(lon) % 1) * 60):02d}′{'E' if lon >= 0 else 'W'}"
    hub_lines = [
        (escape(name), name_px, 'bold'),
        (f'{dt_local.day} {dt_local:%b} {dt_local.year}  {dt_local:%H:%M}', 12, 'normal'),
        (escape(str(tz_name)), 11, 'normal'),
        (escape(str(location_query)), 12, 'normal'),
        (f'{lat_s}  {lon_s}', 11, 'normal'),
        (chart_data['sect'], 12, 'bold'),
        ('Whole sign · Alchabitius', 10, 'normal'),
        ('Tropical · True node', 10, 'normal'),
    ]
    y = cy - 7 * len(hub_lines)
    for s, px, w in hub_lines:
        svg.append(text(cx, y, s, px, w))
        y += 14

    # 7. The wide variant: a positions panel beside the wheel, so a full-
    #    window view uses the window's width as well as its height (D10).
    if wide:
        x0 = size + 40
        svg.append(text(x0, 60, 'Positions', 22, 'bold', anchor='start'))
        for dx, h in ((0, 'Point'), (150, 'Position'), (330, 'WS place'), (460, 'Quadrant'), (590, 'Motion')):
            svg.append(text(x0 + dx, 100, h, 15, 'bold', '#444444', anchor='start'))
        svg.append(line(x0, 112, x0 + 680, 112, '#000000', 1))
        y = 140
        for name_, lon_val, speed in sorted(points, key=lambda p: list(POINT_GLYPHS).index(p[0]) if p[0] in POINT_GLYPHS else 99):
            d, m = _wheel_dm(lon_val)
            if speed is None:
                motion = '–'
            else:
                motion = '℞' + _VS + ' retrograde' if speed < 0 else 'direct'
            svg.append(text(x0, y, POINT_GLYPHS.get(name_, '') + _VS, 22, anchor='start'))
            svg.append(text(x0 + 34, y, name_, 16, anchor='start'))
            svg.append(text(x0 + 150, y, f'{d:02d}° {sign_glyph(lon_val)} {m:02d}′', 16, anchor='start'))
            svg.append(text(x0 + 330, y, str(get_wsh_house(lon_val, asc)), 16, anchor='start'))
            svg.append(text(x0 + 460, y, str(get_effective_house(lon_val, cusps)), 16, anchor='start'))
            svg.append(text(x0 + 590, y, motion, 15, anchor='start'))
            y += 36
        y += 20
        svg.append(text(x0, y, 'Angles and cusps (Alchabitius)', 18, 'bold', anchor='start'))
        y += 34
        for i, cusp_lon in enumerate(cusps):
            d, m = _wheel_dm(cusp_lon)
            label = {0: 'Asc', 3: 'IC', 6: 'Des', 9: 'MC'}.get(i, '')
            col = x0 + (0 if i < 6 else 340)
            yy = y + (i % 6) * 32
            svg.append(text(col, yy, f'{i + 1:2d}', 15, 'bold', _CUSP_COLOUR, anchor='start'))
            svg.append(text(col + 40, yy, f'{d:02d}° {sign_glyph(cusp_lon)} {m:02d}′', 15, anchor='start'))
            if label:
                svg.append(text(col + 190, yy, label, 15, 'bold', _AXIS_COLOUR[i], anchor='start'))
        y += 6 * 32 + 20
        sect_line = f"Sect: {chart_data['sect']}"
        if chronocrats:
            sect_line += (f" · Lord of the day: {escape(str(chronocrats.get('Day Lord', '')))}"
                          f" · Lord of the hour: {escape(str(chronocrats.get('Hour Lord', '')))}")
        svg.append(text(x0, y, sect_line, 15, anchor='start'))

    svg.append('</svg>')
    return ''.join(svg)


# ---- Multi-ring wheels and direction strips for the Timing page (2026-09-10) ----
# Built from the book's own figures (UI_CHART_INPUT_EVALUATION_2026-09-10.md
# §6). The revolution over the root is PN IV I.6 (Figure 51, fn 33); the
# month over the year and the root is IX.3, 4-6 (Figures 39 and 109, fn 58);
# the profection is Figures 3, 15 and 33. What Dykes' wheels carry, read
# from the images: the outer charts in whole signs, the sign of the year
# shaded, the profection as a dashed arc from the natal Ascendant, an
# Egyptian-bounds ring, and "only the seven traditional planets, the Nodes,
# Lot of Fortune, and axial degrees" (p. 12) unless more is asked for. On
# the order: "Abu Ma'shar seems to prefer that the SR be the inner wheel,
# but to me this seem unnatural and I only do it to illustrate his
# instructions in Ch. I.6" (p. 12) -- the caller chooses; the page offers
# both. Pure functions, no Streamlit, SVG strings out; every point carries
# data- attributes so a test can hold the picture to the inventory table.

_M_RIM, _M_SIGN_IN, _M_BOUNDS_IN, _M_HUB_RING, _M_HUB = 478, 430, 408, 150, 118
WHEEL_RING_COLOURS = ('#000000', '#1f3a93', '#8b1a1a')     # inner, middle, outer ring text
WHEEL_SHADE = '#e2e2e2'                                    # the sign of the year (fn 33)
WHEEL_BOUND_TINT = '#ffe08a'                               # the bound the distribution stands in
WHEEL_ORDER_OPTIONS = ("Nativity inside (Dykes)", "Revolution inside (Abu Ma'shar's order, PN IV I.6)")
WHEEL_VIEW_OPTIONS = ("Year", "Year over root", "Month over year and root", "Month", "Profection")
_ASPECT_GLYPH = {'body': '☌', 'sextile': '⚹', 'square': '□', 'trine': '△', 'opposition': '☍'}


def _wheel_geometry(asc_sign, cx=500.0, cy=500.0):
    """ang/xy/sector for a wheel whose rising SIGN's boundary sits at
    9 o'clock (D1), the zodiac running counter-clockwise."""
    def ang(longitude):
        return (longitude - asc_sign * 30 + 180.0) % 360.0

    def xy(r, a):
        t = math.radians(a)
        return cx + r * math.cos(t), cy - r * math.sin(t)

    def sector(r_in, r_out, a0, a1):
        x0o, y0o = xy(r_out, a0); x1o, y1o = xy(r_out, a1)
        x0i, y0i = xy(r_in, a0); x1i, y1i = xy(r_in, a1)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        return (f'M{x0o:.1f},{y0o:.1f} A{r_out},{r_out} 0 {large} 0 {x1o:.1f},{y1o:.1f} '
                f'L{x1i:.1f},{y1i:.1f} A{r_in},{r_in} 0 {large} 1 {x0i:.1f},{y0i:.1f} Z')

    def arc(r, a0, a1):
        """An open arc from bearing a0 to a1 the zodiacal way round."""
        x0, y0 = xy(r, a0); x1, y1 = xy(r, a1)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        return f'M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 0 {x1:.1f},{y1:.1f}'

    return ang, xy, sector, arc


def _svg_line(x0, y0, x1, y1, stroke, width, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>'


def _svg_text(x, y, s, px, weight='normal', fill='#000', anchor='middle', rotate=None, cls=None):
    rot = f' transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"' if rotate is not None else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<text{c} x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-size="{px}" font-weight="{weight}" fill="{fill}"{rot}>{s}</text>')


def _svg_arrowhead(xy, r, a, colour, size=9, forward=True):
    """A small filled triangle at bearing a on radius r, pointing the
    zodiacal way (forward) along the circle."""
    tip_a = a + (1.2 if forward else -1.2) * (size * 0.5) * 57.2958 / r
    tx, ty = xy(r, tip_a)
    bx1, by1 = xy(r + size * 0.6, a)
    bx2, by2 = xy(r - size * 0.6, a)
    return f'<polygon points="{tx:.1f},{ty:.1f} {bx1:.1f},{by1:.1f} {bx2:.1f},{by2:.1f}" fill="{colour}"/>'


def _bounds_ring_svg(ang, xy, sector, r_in, r_out, highlight=None, glyph_px=12):
    """The Egyptian bounds as a ring, a cell per bound with its lord's
    glyph, as every PN IV wheel carries (Figures 1, 22, 25, 26, 109).
    `highlight` is a longitude whose bound is tinted -- the bound the
    distribution stands in. Every cell is class="bound"."""
    out = []
    for i, sign in enumerate(SIGN_ORDER):
        start = 0
        for limit, lord in EGYPTIAN_TERMS[sign]:
            a0, a1 = ang(i * 30 + start), ang(i * 30 + limit)
            tint = '#ffffff'
            if highlight is not None and int((highlight % 360.0) // 30) == i and start <= (highlight % 30.0) < limit:
                tint = WHEEL_BOUND_TINT
            out.append(f'<path class="bound" d="{sector(r_in, r_out, a0, a1)}" fill="{tint}" '
                       f'stroke="#000000" stroke-width="0.6"/>')
            mx, my = xy((r_in + r_out) / 2.0, ang(i * 30 + (start + limit) / 2.0))
            out.append(_svg_text(mx, my, POINT_GLYPHS[lord] + _VS, glyph_px, fill='#333333', cls='bound-lord'))
            start = limit
    return out


def _wheel_points(chart_data):
    """The points a wheel draws by default (p. 12): the seven planets, the
    nodes, the Lot of Fortune. (name, longitude, speed-or-None)."""
    p_data = chart_data['planetary_data']
    node = p_data['North Node']
    points = [(name, d['longitude'], d.get('speed_in_lon', 0.0)) for name, d in p_data.items()]
    points.append(('South Node', (node['longitude'] + 180.0) % 360.0, node.get('speed_in_lon', 0.0)))
    points.append(('Lot of Fortune', chart_data['lot_of_fortune'], None))
    return points


def _ring_layout(n, bounds):
    """(r_in, r_out) for n chart rings, inner to outer, between the hub
    ring and the bounds ring (or the degree scale)."""
    top = _M_BOUNDS_IN - 4 if bounds else _M_SIGN_IN - 4
    bottom = _M_HUB_RING
    if n == 1:
        return [(bottom, top)]
    if n == 2:
        split = bottom + (top - bottom) * 0.58
        return [(bottom, split), (split, top)]
    a = bottom + (top - bottom) * 0.40
    b = a + (top - bottom) * 0.30
    return [(bottom, a), (a, b), (b, top)]


def _draw_ring_points(svg, ang, xy, ring_idx, label, chart_data, r_in, r_out, colour, badges=None):
    """One chart's default points in its annulus: a tick at the true
    degree on the ring's outer edge, a hairline to a radial stack (glyph,
    degree, sign, minute, retrograde mark, badge letters), spread apart
    as the natal wheel spreads them. Each point is a <g class="pt"> with
    data-ring/data-chart/data-point/data-lon."""
    # The stack -- glyph, degree, sign, minute, retrograde, badge -- fits the
    # annulus: sizes scale with its width (capped at the natal wheel's),
    # the lines are laid out between the ring's edges, and the stagger
    # for crowded runs is used only where the ring is wide enough for it.
    width = r_out - r_in
    scale = max(0.42, min(1.0, width / 150.0))
    px_glyph, px_deg, px_sign, px_min, px_rx = (round(34 * scale), round(18 * scale), round(19 * scale),
                                                 round(15 * scale), round(14 * scale))
    r_glyph = r_out - 12 - px_glyph * 0.55
    span = min(r_glyph - (r_in + 8), 118.0 * scale + 12.0)
    step = span / 4.6
    r_deg, r_sign, r_min, r_rx = r_glyph - step, r_glyph - 2.0 * step, r_glyph - 2.9 * step, r_glyph - 3.7 * step
    r_badge = r_glyph - 4.6 * step
    points = sorted(_wheel_points(chart_data), key=lambda p: ang(p[1]))
    true_b = [ang(p[1]) for p in points]
    min_sep = max(4.0, (px_glyph + 6) * 57.2958 / r_glyph)
    shown = _spread_labels(true_b, min_sep)
    stagger = round(min(30.0 * scale, max(0.0, width - span - 22.0)))
    offsets = _stagger_offsets(true_b, shown, step=stagger) if stagger >= 8 else [0] * len(points)
    for (name, lon_val, speed), a_true, a_shown, off in zip(points, true_b, shown, offsets):
        d, m = _wheel_dm(lon_val)
        svg.append(f'<g class="pt" data-ring="{ring_idx}" data-chart="{escape(label)}" data-point="{escape(name)}" '
                   f'data-lon="{lon_val % 360.0:.6f}">')
        x0, y0 = xy(r_out, a_true); x1, y1 = xy(r_out - 8, a_true)
        svg.append(_svg_line(x0, y0, x1, y1, colour, 1.4))
        x2, y2 = xy(r_glyph - off + px_glyph * 0.6, a_shown)
        svg.append(_svg_line(x1, y1, x2, y2, '#777777', 0.7))
        gx, gy = xy(r_glyph - off, a_shown); svg.append(_svg_text(gx, gy, POINT_GLYPHS.get(name, name[:2]) + _VS, px_glyph, fill=colour))
        dx_, dy_ = xy(r_deg - off, a_shown); svg.append(_svg_text(dx_, dy_, f'{d:02d}°', px_deg, 'bold', colour))
        sx, sy = xy(r_sign - off, a_shown); svg.append(_svg_text(sx, sy, SIGN_GLYPHS[int((lon_val % 360.0) // 30)] + _VS, px_sign, fill=colour))
        mx, my = xy(r_min - off, a_shown); svg.append(_svg_text(mx, my, f"{m:02d}'", px_min, fill=colour))
        if speed is not None and speed < 0:
            rx, ry = xy(r_rx - off, a_shown); svg.append(_svg_text(rx, ry, '℞' + _VS, px_rx, fill=colour))
        if badges and badges.get(name):
            bx, by = xy(r_badge - off, a_shown)
            svg.append(_svg_text(bx, by, escape(badges[name]), px_rx, 'bold', '#b8860b', cls='badge'))
        svg.append('</g>')


def _draw_ring_extras(svg, ang, xy, ring_idx, label, extras, r_out, colour):
    """Optional points (Lots, rays, twelfth-parts): a short tick at the
    ring's outer edge and a tiny label, spread thinly. <g class="extra">."""
    if not extras:
        return
    items = sorted(extras, key=lambda e: ang(e[1]))
    true_b = [ang(e[1]) for e in items]
    shown = _spread_labels(true_b, 2.2)
    for item, a_true, a_shown in zip(items, true_b, shown):
        name, lon_val = item[0], item[1]
        short = item[2] if len(item) > 2 else (name if len(name) <= 6 else name[:6])
        svg.append(f'<g class="extra" data-ring="{ring_idx}" data-chart="{escape(label)}" '
                   f'data-point="{escape(name)}" data-lon="{lon_val % 360.0:.6f}">')
        x0, y0 = xy(r_out, a_true); x1, y1 = xy(r_out - 5, a_true)
        svg.append(_svg_line(x0, y0, x1, y1, colour, 0.8))
        tx, ty = xy(r_out - 12, a_shown)
        svg.append(_svg_text(tx, ty, escape(short) + _VS, 7, fill=colour, rotate=-(a_shown - 90.0) % 360.0 - 90.0))
        svg.append('</g>')


def generate_multiwheel_svg(rings, chart_name, wide=False, bounds=True, shade_sign=None, shade_label='Sign of year',
                            outline_sign=None, outline_label='Sign of month', profection_from=None,
                            distribution=None, marks=(), badges=None, extras=None, hub_lines=()):
    """One to three charts on one zodiac. `rings` are dicts inner to outer:
    {'label', 'chart' (a chart_data), 'when' (a short line for the hub)}.
    shade_sign / outline_sign: sign indices 0-11 (the sign of the year,
    the sign of the month). profection_from: a longitude whose sign the
    dashed arc starts from, ending at shade_sign (Figures 3, 33).
    distribution: {'start': lon, 'end': lon} draws the directed
    Ascendant's arc and tints the bound of `end` (Figures 2, 65). marks:
    (label, lon, ring_idx) degrees ticked on a ring's outer edge. badges:
    {ring_idx: {planet: letters}}. extras: {ring_idx: [(name, lon)]}."""
    rings = list(rings)
    assert 1 <= len(rings) <= 3
    size = WHEEL_SIZE
    cx = cy = size / 2.0
    inner = rings[0]['chart']
    asc_sign = int((inner['ascendant'] % 360.0) // 30)
    ang, xy, sector, arc = _wheel_geometry(asc_sign, cx, cy)
    width = WHEEL_WIDE_WIDTH if wide else size
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {size}" width="{width}" height="{size}" '
           f'style="font-family:{_WHEEL_FONT}">',
           f'<rect width="{width}" height="{size}" fill="#ffffff"/>']
    layout = _ring_layout(len(rings), bounds)
    r_top = layout[-1][1]

    # 0. The shaded sign of the year, under everything (fn 33).
    if shade_sign is not None:
        a0, a1 = ang(shade_sign * 30), ang(shade_sign * 30 + 30)
        svg.append(f'<path class="shade" data-sign="{shade_sign}" d="{sector(_M_HUB, _M_RIM, a0, a1)}" fill="{WHEEL_SHADE}"/>')
    # 1. Sign band, degree scale, spokes through every ring (whole signs are
    #    every chart's houses here, as Dykes draws them).
    for i in range(12):
        a0, a1 = ang(i * 30), ang(i * 30 + 30)
        fill = TRIPLICITY_TINT[i % 4] if shade_sign != i else WHEEL_SHADE
        svg.append(f'<path d="{sector(_M_SIGN_IN, _M_RIM, a0, a1)}" fill="{fill}"/>')
        gx, gy = xy((_M_SIGN_IN + _M_RIM) / 2.0 + 6, ang(i * 30 + 15))
        svg.append(_svg_text(gx, gy, SIGN_GLYPHS[i] + _VS, 26))
        x0, y0 = xy(_M_HUB, a0); x1, y1 = xy(_M_RIM, a0)
        svg.append(_svg_line(x0, y0, x1, y1, '#000000', 1.0))
    for d in range(360):
        ln = 12 if d % 10 == 0 else 8 if d % 5 == 0 else 4
        x0, y0 = xy(_M_SIGN_IN, ang(d)); x1, y1 = xy(_M_SIGN_IN + ln, ang(d))
        svg.append(_svg_line(x0, y0, x1, y1, '#000000', 0.8 if ln > 4 else 0.45))
    if bounds:
        svg.extend(_bounds_ring_svg(ang, xy, sector, _M_BOUNDS_IN, _M_SIGN_IN,
                                    highlight=(distribution or {}).get('end')))
    for r, w in ((_M_RIM, 2.2), (_M_SIGN_IN, 1.4), (_M_HUB_RING, 1.0), (_M_HUB, 1.4)):
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000000" stroke-width="{w}"/>')
    if outline_sign is not None:
        a0, a1 = ang(outline_sign * 30), ang(outline_sign * 30 + 30)
        svg.append(f'<path class="outline" data-sign="{outline_sign}" d="{sector(_M_HUB, _M_RIM, a0, a1)}" '
                   f'fill="none" stroke="#000000" stroke-width="2.2" stroke-dasharray="7 5"/>')

    # 2. The rings, inner to outer: separator, whole-sign numbers of that
    #    chart, its angles across its own annulus, its points.
    for idx, (ring, (r_in, r_out)) in enumerate(zip(rings, layout)):
        chart = ring['chart']
        colour = WHEEL_RING_COLOURS[idx if len(rings) > 1 else 0]
        if idx > 0:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in}" fill="none" stroke="#000000" stroke-width="1.0"/>')
        c_asc_sign = int((chart['ascendant'] % 360.0) // 30)
        num_r = (_M_HUB + _M_HUB_RING) / 2.0 if idx == 0 else r_out - 9
        for i in range(12):
            nx, ny = xy(num_r, ang(i * 30 + 15 if idx > 0 else i * 30 + 15))
            svg.append(_svg_text(nx, ny, str((i - c_asc_sign) % 12 + 1), 15 if idx == 0 else 10,
                                 'bold', colour, cls='house'))
        a_lo = _M_HUB if idx == 0 else r_in
        for lon_val, col, lab in ((chart['ascendant'], '#0000cc', 'As'), (chart['mc'], '#1e7b1e', 'Mc'),
                                  ((chart['ascendant'] + 180.0) % 360.0, '#0000cc', 'Ds'),
                                  ((chart['mc'] + 180.0) % 360.0, '#1e7b1e', 'Ic')):
            x0, y0 = xy(a_lo, ang(lon_val)); x1, y1 = xy(r_out, ang(lon_val))
            svg.append(_svg_line(x0, y0, x1, y1, col, 2.0 if idx == 0 else 1.5))
            lx, ly = xy(r_out - 9, ang(lon_val) + 2.5 * 57.2958 / r_out * 3)
            svg.append(_svg_text(lx, ly, lab, 9, 'bold', col, cls='angle'))
        _draw_ring_points(svg, ang, xy, idx, ring['label'], chart, r_in, r_out, colour,
                          badges=(badges or {}).get(idx))
        _draw_ring_extras(svg, ang, xy, idx, ring['label'], (extras or {}).get(idx), r_out, colour)

    # 3. Marks: named degrees on a ring's outer edge (the terminal point ...).
    for lab, lon_val, ring_idx in marks:
        r_in, r_out = layout[min(ring_idx, len(layout) - 1)]
        a = ang(lon_val)
        x0, y0 = xy(r_out, a); x1, y1 = xy(r_out - 14, a)
        svg.append(f'<g class="mark" data-point="{escape(lab)}" data-lon="{lon_val % 360.0:.6f}">')
        svg.append(_svg_line(x0, y0, x1, y1, '#b8860b', 2.2))
        tx, ty = xy(r_out - 22, a)
        svg.append(_svg_text(tx, ty, escape(lab), 9, 'bold', '#b8860b'))
        svg.append('</g>')

    # 4. The profection: a dashed arc outside the rim from the natal
    #    Ascendant's sign to the sign of the year, arrowhead at the end.
    if profection_from is not None and shade_sign is not None:
        s0 = int((profection_from % 360.0) // 30)
        if s0 != shade_sign:
            a0, a1 = ang(s0 * 30 + 15), ang(shade_sign * 30 + 15)
            svg.append(f'<path class="profection" d="{arc(_M_RIM + 11, a0, a1)}" fill="none" stroke="#000000" '
                       f'stroke-width="2.4" stroke-dasharray="9 6"/>')
            svg.append(_svg_arrowhead(xy, _M_RIM + 11, a1, '#000000'))
    # Sign labels run along the arc in the sign band's inner margin,
    # upright on either half of the wheel, as Dykes letters "Sign of year".
    def _tangential(r, lon_val, s, cls):
        a = ang(lon_val)
        rot = (90.0 - a) % 360.0
        if 180.0 < a % 360.0 < 360.0:
            rot += 180.0
        x, y = xy(r, a)
        return _svg_text(x, y, s, 10, 'bold', '#444444', rotate=rot, cls=cls)
    if shade_sign is not None:
        svg.append(_tangential(_M_SIGN_IN + 15, shade_sign * 30 + 15, shade_label, 'shade-label'))
    if outline_sign is not None:
        svg.append(_tangential(_M_SIGN_IN + 15 if outline_sign != shade_sign else _M_SIGN_IN + 26,
                               outline_sign * 30 + 15, outline_label, 'outline-label'))

    # 5. The distribution: the directed Ascendant from its degree to the
    #    degree reached now, solid, on the inner edge of the bounds ring.
    if distribution:
        r_arc = r_top + 1
        a0, a1 = ang(distribution['start']), ang(distribution['end'])
        svg.append(f'<path class="distribution" data-start="{distribution["start"] % 360.0:.6f}" '
                   f'data-end="{distribution["end"] % 360.0:.6f}" d="{arc(r_arc, a0, a1)}" fill="none" '
                   f'stroke="#0000cc" stroke-width="2.6"/>')
        svg.append(_svg_arrowhead(xy, r_arc, a1, '#0000cc', size=11))

    # 6. Hub: the name, then one line per ring, inner first.
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{_M_HUB - 1}" fill="#ffffff"/>')
    name = str(chart_name)
    if len(name) > 30:
        name = name[:29] + '…'
    lines = [(escape(name), 15 if len(name) <= 18 else 12, 'bold', '#000000')]
    for idx, ring in enumerate(rings):
        colour = WHEEL_RING_COLOURS[idx if len(rings) > 1 else 0]
        place = ('Inner', 'Middle', 'Outer')[idx] if len(rings) == 3 else ('Inner', 'Outer')[idx] if len(rings) == 2 else ''
        head = f"{place}: {ring['label']}" if place else ring['label']
        lines.append((escape(head), 11, 'bold', colour))
        if ring.get('when'):
            lines.append((escape(str(ring['when'])), 9, 'normal', colour))
    for s in hub_lines:
        lines.append((escape(str(s)), 9, 'normal', '#333333'))
    y = cy - 6.5 * (len(lines) - 1)
    for s, px, w, col in lines:
        svg.append(_svg_text(cx, y, s, px, w, col))
        y += 13

    # 7. Wide: a positions column per ring.
    if wide:
        col_w = (width - size - 60) / len(rings)
        for idx, ring in enumerate(rings):
            colour = WHEEL_RING_COLOURS[idx if len(rings) > 1 else 0]
            x0 = size + 40 + idx * col_w
            svg.append(_svg_text(x0, 60, escape(ring['label']), 18, 'bold', colour, anchor='start'))
            if ring.get('when'):
                svg.append(_svg_text(x0, 84, escape(str(ring['when'])), 11, fill=colour, anchor='start'))
            svg.append(_svg_line(x0, 98, x0 + col_w - 30, 98, '#000000', 1))
            chart = ring['chart']
            y = 122
            pts = sorted(_wheel_points(chart), key=lambda p: list(POINT_GLYPHS).index(p[0]) if p[0] in POINT_GLYPHS else 99)
            for name_, lon_val, speed in pts:
                d, m = _wheel_dm(lon_val)
                motion = '' if speed is None else ('℞' + _VS if speed < 0 else '')
                svg.append(_svg_text(x0, y, POINT_GLYPHS.get(name_, '') + _VS, 18, fill=colour, anchor='start'))
                svg.append(_svg_text(x0 + 30, y, f'{d:02d}° {SIGN_GLYPHS[int((lon_val % 360.0) // 30)]}{_VS} {m:02d}′ {motion}',
                                     14, fill=colour, anchor='start'))
                svg.append(_svg_text(x0 + col_w - 50, y, str(get_wsh_house(lon_val, chart['ascendant'])), 13, fill=colour))
                y += 28
            y += 10
            for lon_val, lab in ((chart['ascendant'], 'Asc'), (chart['mc'], 'MC')):
                d, m = _wheel_dm(lon_val)
                svg.append(_svg_text(x0, y, lab, 13, 'bold', colour, anchor='start'))
                svg.append(_svg_text(x0 + 30, y, f'{d:02d}° {SIGN_GLYPHS[int((lon_val % 360.0) // 30)]}{_VS} {m:02d}′',
                                     14, fill=colour, anchor='start'))
                y += 26
            svg.append(_svg_text(x0, y, f"Sect: {chart['sect']}", 12, fill=colour, anchor='start'))

    svg.append('</svg>')
    return ''.join(svg)


# ---- Direction strips --------------------------------------------------------
# The four distributions as timelines (evaluation B.4): one bar per bound
# tinted by its distributor, the distributor's glyph in it, a full-height
# line where the bound changes and a half tick where only the partner
# does, and the present as a red line. PN IV prints distributions as a
# table with dates (Figure 22) and as an arc on the wheel (Figures 2, 65);
# nothing in the book replaces a timeline, and a student needs one.
STRIP_WIDTH, STRIP_HEIGHT = 1600, 170
STRIP_TINT = {'Saturn': '#d9d9d9', 'Jupiter': '#cfe0f5', 'Mars': '#f5cdc7', 'Sun': '#fbe9a6',
              'Venus': '#d4efd0', 'Mercury': '#f8ddb8', 'Moon': '#e2d9f3'}


def generate_distribution_strip_svg(segments, now, unit='years', span=None, title=''):
    """segments as _pn4_distribute returns them (from/to/distributor/partner/
    partner_aspect); `now` in the strip's unit (completed years, or the day
    of the year) or None; span the bar's full length (120 years, 365 days
    ...). Each bar is <rect class="seg"> with data-from/to/distributor/
    partner; the present is <line class="now">."""
    if unit not in ('years', 'days'):
        raise ValueError(f"unit must be 'years' or 'days', not {unit!r}")
    segments = list(segments or [])
    if span is None:
        span = max((s['to'] for s in segments), default=1.0)
    span = float(span) or 1.0
    x_left, x_right = 60.0, STRIP_WIDTH - 40.0
    y_top, y_bot = 62.0, 122.0

    def x_of(v):
        return x_left + (x_right - x_left) * max(0.0, min(1.0, v / span))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {STRIP_WIDTH} {STRIP_HEIGHT}" width="{STRIP_WIDTH}" '
           f'height="{STRIP_HEIGHT}" style="font-family:{_WHEEL_FONT}">',
           f'<rect width="{STRIP_WIDTH}" height="{STRIP_HEIGHT}" fill="#ffffff"/>']
    if title:
        svg.append(_svg_text(x_left, 26, escape(str(title)), 18, 'bold', anchor='start'))
    prev = None
    for seg in segments:
        x0, x1 = x_of(seg['from']), x_of(seg['to'])
        w = max(0.0, x1 - x0)
        tint = STRIP_TINT.get(seg['distributor'], '#eeeeee')
        svg.append(f'<rect class="seg" x="{x0:.1f}" y="{y_top}" width="{w:.1f}" height="{y_bot - y_top}" fill="{tint}" '
                   f'stroke="#000000" stroke-width="0.4" data-from="{seg["from"]:.4f}" data-to="{seg["to"]:.4f}" '
                   f'data-distributor="{escape(str(seg["distributor"]))}" data-partner="{escape(str(seg["partner"]))}" '
                   f'data-aspect="{escape(str(seg["partner_aspect"]))}"/>')
        bound_change = prev is None or prev['distributor'] != seg['distributor']
        svg.append(_svg_line(x0, y_top if bound_change else y_top, x0, y_bot if bound_change else y_top + 16,
                             '#000000', 1.4 if bound_change else 1.0))
        if w >= 16:
            svg.append(_svg_text((x0 + x1) / 2.0, y_top + 22, POINT_GLYPHS.get(seg['distributor'], '') + _VS, 20))
        if w >= 26 and seg['partner']:
            svg.append(_svg_text((x0 + x1) / 2.0, y_bot - 14,
                                 _ASPECT_GLYPH.get(seg['partner_aspect'], '') + POINT_GLYPHS.get(seg['partner'], '') + _VS,
                                 13, fill='#333333'))
        prev = seg
    svg.append(_svg_line(x_left, y_bot, x_right, y_bot, '#000000', 1.2))
    tick = 10.0 if unit == 'years' else 30.0
    v = 0.0
    while v <= span + 1e-9:
        x = x_of(v)
        svg.append(_svg_line(x, y_bot, x, y_bot + 7, '#000000', 1.0))
        svg.append(_svg_text(x, y_bot + 20, f'{v:g}', 12))
        v += tick
    svg.append(_svg_text(x_right, y_bot + 40, 'age in completed years' if unit == 'years' else 'day of the year',
                         11, fill='#555555', anchor='end'))
    if now is not None and 0.0 <= now <= span:
        x = x_of(now)
        svg.append(f'<line class="now" x1="{x:.1f}" y1="{y_top - 14}" x2="{x:.1f}" y2="{y_bot + 8}" stroke="#c00000" '
                   f'stroke-width="2.4" data-now="{now:.4f}"/>')
        svg.append(_svg_text(x, y_top - 22, ('now: age ' if unit == 'years' else 'now: day ') + f'{now:g}', 12, 'bold', '#c00000'))
    svg.append('</svg>')
    return ''.join(svg)


def generate_hit_strip_svg(rows, now, span=None, title=''):
    """The house-master's direction (Sahl, On Nativities 1.23, 2) as a
    strip in the family of generate_distribution_strip_svg: the same
    0-to-span axis in completed years, one tick per target reached
    (<line class="hit"> with data-arc/data-target), labelled with the
    infortune's glyph and the aspect's, alternating above and below the
    axis so neighbours do not collide; the present as <line class="now">.
    `rows` are sahl_house_master_direction's rows (Target, Arc (years))."""
    rows = list(rows or [])
    if span is None:
        span = max((float(r['Arc (years)']) for r in rows), default=1.0)
    span = float(span) or 1.0
    x_left, x_right = 60.0, STRIP_WIDTH - 40.0
    y_axis = 100.0

    def x_of(v):
        return x_left + (x_right - x_left) * max(0.0, min(1.0, v / span))

    def label_of(target):
        m = re.match(r"(?:the )?(\w+)'s (body|opposition|square|degree)", target)
        if not m:
            return escape(target)
        planet, what = m.group(1), m.group(2)
        glyph = POINT_GLYPHS.get(planet, planet)
        return (glyph + _VS) if what == 'degree' else (_ASPECT_GLYPH.get(what, '') + glyph + _VS)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {STRIP_WIDTH} {STRIP_HEIGHT}" width="{STRIP_WIDTH}" '
           f'height="{STRIP_HEIGHT}" style="font-family:{_WHEEL_FONT}">',
           f'<rect width="{STRIP_WIDTH}" height="{STRIP_HEIGHT}" fill="#ffffff"/>']
    if title:
        svg.append(_svg_text(x_left, 26, escape(str(title)), 18, 'bold', anchor='start'))
    svg.append(_svg_line(x_left, y_axis, x_right, y_axis, '#000000', 1.2))
    v = 0.0
    while v <= span + 1e-9:
        x = x_of(v)
        svg.append(_svg_line(x, y_axis, x, y_axis + 7, '#000000', 1.0))
        svg.append(_svg_text(x, y_axis + 20, f'{v:g}', 12))
        v += 10.0
    svg.append(_svg_text(x_right, y_axis + 40, 'age in completed years', 11, fill='#555555', anchor='end'))
    for i, r in enumerate(sorted(rows, key=lambda r: float(r['Arc (years)']))):
        arc = float(r['Arc (years)'])
        if arc > span:
            continue
        x = x_of(arc)
        above = i % 2 == 0
        y0, y1 = (y_axis - 30, y_axis) if above else (y_axis, y_axis + 30)
        svg.append(f'<line class="hit" x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="#000000" '
                   f'stroke-width="1.6" data-arc="{arc:.4f}" data-target="{escape(str(r["Target"]))}"/>')
        svg.append(_svg_text(x, y_axis - 38 if above else y_axis + 46, label_of(str(r['Target'])), 18))
        svg.append(_svg_text(x, y_axis - 56 if above else y_axis + 62, f'{arc:.1f}', 11, fill='#333333'))
    if now is not None and 0.0 <= now <= span:
        x = x_of(now)
        svg.append(f'<line class="now" x1="{x:.1f}" y1="{y_axis - 66}" x2="{x:.1f}" y2="{y_axis + 8}" stroke="#c00000" '
                   f'stroke-width="2.4" data-now="{now:.4f}"/>')
        svg.append(_svg_text(x, 44, f'now: age {now:g}', 12, 'bold', '#c00000'))
    svg.append('</svg>')
    return ''.join(svg)


# ==========================================
# 3. DIGNITY & ASPECT EVALUATORS
# ==========================================

# --- Shared classical dignity reference tables --------------------------
# Pulled out to module level so both evaluate_essential_dignities() and the
# prenatal syzygy engine (which needs to look up dignities at an arbitrary
# degree, not just at a planet's own position) can use the same data.
DOMICILES = {'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mercury': ['Gemini', 'Virgo'], 'Venus': ['Taurus', 'Libra'], 'Mars': ['Aries', 'Scorpio'], 'Jupiter': ['Sagittarius', 'Pisces'], 'Saturn': ['Capricorn', 'Aquarius']}
EXALTATIONS = {'Sun': ['Aries'], 'Moon': ['Taurus'], 'Mercury': ['Virgo'], 'Venus': ['Pisces'], 'Mars': ['Capricorn'], 'Jupiter': ['Cancer'], 'Saturn': ['Libra']}
# The degrees of exaltation in the standard scheme, as the course's Handy
# Tables print them (Hermes' column differs by a degree for five of the
# seven). DISPLAY ONLY, for the Reference tables page (2026-09-10): nothing
# in this engine reads a degree of exaltation, and nothing may start to
# without a source in hand.
EXALTATION_DEGREES = {'Saturn': 21, 'Jupiter': 15, 'Mars': 28, 'Sun': 19, 'Venus': 27, 'Mercury': 15, 'Moon': 3}
DETRIMENTS = {'Sun': ['Aquarius'], 'Moon': ['Capricorn'], 'Mercury': ['Sagittarius', 'Pisces'], 'Venus': ['Scorpio', 'Aries'], 'Mars': ['Libra', 'Taurus'], 'Jupiter': ['Gemini', 'Virgo'], 'Saturn': ['Cancer', 'Leo']}
FALLS = {'Sun': ['Libra'], 'Moon': ['Scorpio'], 'Mercury': ['Pisces'], 'Venus': ['Virgo'], 'Mars': ['Cancer'], 'Jupiter': ['Capricorn'], 'Saturn': ['Aries']}
# Egyptian bounds (terms), as the course tables give them: TNAC Handy Tables
# from Part 1, p. 1, "Table of Egyptian bounds" (Dykes 2023), read cell by
# cell from a 300-dpi render on 2026-09-07 and pinned sign by sign in
# tests/test_doctrine_fixtures.py. Each entry is (upper limit, lord): a
# degree belongs to the first bound whose limit exceeds it.
#
# Gemini and Aquarius each had two adjacent lords transposed from the
# initial commit until 2026-09-07 -- Gemini 6-17 read Venus then Jupiter,
# Aquarius 0-13 read Venus then Mercury -- so every degree in those 24
# carried the wrong term lord in dignity scoring, the victor grids, the
# prenatal syzygy and distribution. Sahl is the independent witness for
# the correction: On Nativities Ch. 10.2.7, 21-22 has Mercury at Aquarius 5
# "in his own bound", and fn. 198 there gives Capricorn 0-7 to Mercury as
# this table does.
EGYPTIAN_TERMS = {
    'Aries':       [(6, 'Jupiter'), (12, 'Venus'),   (20, 'Mercury'), (25, 'Mars'),    (30, 'Saturn')],
    'Taurus':      [(8, 'Venus'),   (14, 'Mercury'), (22, 'Jupiter'), (27, 'Saturn'),  (30, 'Mars')],
    'Gemini':      [(6, 'Mercury'), (12, 'Jupiter'), (17, 'Venus'),   (24, 'Mars'),    (30, 'Saturn')],
    'Cancer':      [(7, 'Mars'),    (13, 'Venus'),   (19, 'Mercury'), (26, 'Jupiter'), (30, 'Saturn')],
    'Leo':         [(6, 'Jupiter'), (11, 'Venus'),   (18, 'Saturn'),  (24, 'Mercury'), (30, 'Mars')],
    'Virgo':       [(7, 'Mercury'), (17, 'Venus'),   (21, 'Jupiter'), (28, 'Mars'),    (30, 'Saturn')],
    'Libra':       [(6, 'Saturn'),  (14, 'Mercury'), (21, 'Jupiter'), (28, 'Venus'),   (30, 'Mars')],
    'Scorpio':     [(7, 'Mars'),    (11, 'Venus'),   (19, 'Mercury'), (24, 'Jupiter'), (30, 'Saturn')],
    'Sagittarius': [(12, 'Jupiter'), (17, 'Venus'),  (21, 'Mercury'), (26, 'Saturn'),  (30, 'Mars')],
    'Capricorn':   [(7, 'Mercury'), (14, 'Jupiter'), (22, 'Venus'),   (26, 'Saturn'),  (30, 'Mars')],
    'Aquarius':    [(7, 'Mercury'), (13, 'Venus'),   (20, 'Jupiter'), (25, 'Mars'),    (30, 'Saturn')],
    'Pisces':      [(12, 'Venus'),  (16, 'Jupiter'), (19, 'Mercury'), (28, 'Mars'),    (30, 'Saturn')],
}
CHALDEAN_ORDER = ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter']
# The weighted five-fold dignity claim used wherever this file totals
# essential dignities at a degree: a planet's own score, the prenatal
# syzygy's almuten, and the newer victor scheme (al-Qabisi / Abu Ma'shar,
# triplicity above bound). The older victor scheme swaps bound and
# triplicity and is written out at VICTOR_WEIGHTS.
ESSENTIAL_DIGNITY_WEIGHTS = {'domicile': 5, 'exaltation': 4, 'triplicity': 3, 'term': 2, 'face': 1}

# Dorothean triplicity rulers, keyed by element, each with the Day/Night/
# Participating lord: Gr. Intr. V.14, 6-9 and Figure 53 (Gr. Intr.), which
# state the four rows as they stand here. One exception the element key
# cannot hold: the earth triplicity's partner is Mars "except that Mercury
# acts as partner to them both in Virgo especially" (V.14, 7; the figure's
# earth row reads "Mars (and Mercury when in Virgo)"; fn 100: Mercury
# "rather than (or in preference to) Mars"). get_essential_rulers applies
# it per sign (Astra audit C01, 2026-09-11). The partner enters no score.
TRIPLICITY = {
    'Fire':  {'Day': 'Sun',   'Night': 'Jupiter', 'Participating': 'Saturn'},
    'Earth': {'Day': 'Venus', 'Night': 'Moon',    'Participating': 'Mars'},
    'Air':   {'Day': 'Saturn','Night': 'Mercury', 'Participating': 'Jupiter'},
    'Water': {'Day': 'Venus', 'Night': 'Mars',    'Participating': 'Moon'},
}
SIGN_ELEMENT = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}
# Inverse lookups: sign -> the single planet that has domicile/exaltation there
SIGN_TO_DOMICILE = {sign: planet for planet, signs in DOMICILES.items() for sign in signs}
SIGN_TO_EXALTATION = {sign: planet for planet, signs in EXALTATIONS.items() for sign in signs}

# PLANETS_IN_HOUSES below follows the Guide cell for cell except the
# 9th-house Mercury PN4 halves, which the Guide (p. 34) prints against its
# own headings (Good: "Bad reports and journeys ..."; Bad: "Good journeys,
# true visions ..."). The code keeps the evident content and
# tests/test_prose_tables.py pins it that way: decision D-16 (2026-09-08),
# content over columns, to be re-checked if PN4 itself enters the corpus.
# Masha'allah's delineations for a topical house's lord, keyed by
# [placed_in_house][lord_of_house] (i.e. outer key = the WSH house the lord
# is physically placed in, inner key = the topical house it rules).
# Source of the wording: TNAC Reference Guide for the Planets and Places,
# "The lords of other places in the Nth (Masha'allah)", pp. 16-39, which
# cites Sahl, On Nativities 1.36, 2.14, 3.10, 4.11, 5.1, 6.3.4, 7.1, 8.5,
# 9.4, 10.2.4, 11.1 and 12.1. Cell [8][5] (lord of the 5th in the 8th) was
# illegible in the OCR of Sahl and carried an [UNCERTAIN] marker from
# 2026-09-05 to 2026-09-08; the Guide (p. 31) reads it as "Children
# premature or miscarried." The OCR remains illegible -- the resolution is
# the course document's, not a re-reading of the scan.
MASHAALLAH_LORDS = {
    1: {1: "Respected in family (subject to other conditions)", 2: "Work with own hands, blessed without searching and need", 3: "Good for siblings from native", 4: "Master of his family and their livelihood; charitable to parents", 5: "Blessed with children in youth, happy with children", 6: "Illness of nature of that planet; death of animals and servants", 7: "Good from women, success from them", 8: "Long lifespan (if good condition); frustration in seeking necessities", 9: "Of fine religion, good soul, knowing the Sunnah", 10: "Associate of authorities, proficient in work, Sultan comes to him", 11: "Successful, good livelihood and condition, glad", 12: "Unhappy, enemies multiply and are victorious, tribulation, belligerent"},
    2: {1: "Will corrupt assets; but if received, gains from sign essence", 2: "Livelihood from known source; if looked at by infortune, ruin", 3: "Siblings compete for assets; they will seek the native", 4: "Prosperous parents; native inherits and is distinguished among siblings", 5: "Children will have good livelihood", 6: "Livelihood from what slaves produce, and animals; lowly benefits", 7: "Corrupts assets due to conflict", 8: "Inheritance; sometimes do work for government/authority", 9: "Assets from foreign country, benefit from travel", 10: "Livelihood from government/authority figure; accumulates assets", 11: "Benefit and assets from friends", 12: "Shameful work, bad character and livelihood, with deception"},
    3: {1: "Siblings suitable, dependent on native; good/wicked mind based on aspects", 2: "Gain from travels and siblings; religion/gain if a fortune", 3: "Siblings are well known, will protect him, love him", 4: "Parents have hardship from siblings; parents like native better", 5: "Native's children named after his siblings; successful in travels", 6: "Siblings have defects/illness, or do the work of slaves", 7: "Brother marries native's women; hostility; native marries relative", 8: "Siblings have defects, chronic illness, diminished condition", 9: "Siblings marry foreign women; moves to another country", 10: "Few siblings, siblings ruined; many travels", 11: "Well-known siblings, condition good, esp. in youth", 12: "Siblings hostile to native, hardship from them"},
    4: {1: "Reverent to parents; hardship from ruler; gains from fathers if received", 2: "Livelihood relates to ancestors; thriving childhood home; devotion", 3: "Siblings steal parents' assets; recognized as thieves", 4: "Parents well known, good reputation; short life if harmed", 5: "Native's children are wretches; encounters hardship due to them", 6: "Native is child of slaves or those doing slave work", 7: "Marries someone from own house, spouse is well known and good", 8: "Fathers are foreigners or have defects/illness, short lifespans", 9: "Parents have hidden illnesses, die outside homeland", 10: "Parents known to rulers; hardship from rulers", 11: "Father has chronic illness, short life, diminished condition", 12: "Parents/family hostile to native; native destroys/leaves childhood home"},
    5: {1: "Happy with children (if unharmed)", 2: "Children have status, will gain good", 3: "Native has siblings abroad who travel and have children", 4: "Prosperous parents see successive generations; good increases", 5: "Native has well-known children who are happy", 6: "Children's upbringing hard, children have defect", 7: "Native marries younger spouse, well-known and virtuous", 8: "Children die early, or have power over others due to Sultan", 9: "Has children in foreign country, delighted; children religious/educated", 10: "Abundance of children; illness/death if harmed; hardship from Sultan", 11: "Delightful children, blessed with good and comfort", 12: "Children debased, sick, from low-status; disobedient/hostile"},
    6: {1: "Miserable, slave work; illness if received; literal slave if Moon corrupted", 2: "Livelihood from 6th-place things; disaster/hardship if not received", 3: "Siblings are hostile and crave his ruin", 4: "Parents unknown in country; aspecting planet shows good/bad", 5: "Fortunate children, but defects will appear in them", 6: "Native healthy, if lord of Ascendant does not look", 7: "Native associates with slave girls or women with defects", 8: "Calamities in slaves and riding animals; not blessed by them", 9: "Blessed with slaves/animals; travel brings illness or corrupts slaves", 10: "Short lifespan, itinerant, enslaves free people", 11: "Bad condition in livelihood, little good, creating discord", 12: "Saddened by slaves and riding animals, no good in them"},
    7: {1: "Native very eager; subordinate to spouse", 2: "Lower-status women; gain/lose money in marriage", 3: "Marries a relative; brothers hostile or marry his women", 4: "Marries relative, good rank; father hostile to native", 5: "Younger spouse; children hostile; deluded about women; servant children", 6: "Sick/slave spouse; low-status spouse; bad reputation due to spouse", 7: "Suitable marriage; spouse has rank of maternal relatives; well-known", 8: "Will inherit from spouse; native dies in exile", 9: "Foreign spouse; good character/pious if a fortune", 10: "Esteemed, well-known spouse; higher-status and connected", 11: "Loving, happy spouse; children and benefit from spouse", 12: "Low-status or sick spouse; spouse is hostile"},
    8: {1: "A wicked soul, much distress, faint-hearted", 2: "Livelihood from inheritance/dead; generous; assets taken if connecting to 8th", 3: "Brother's women will not survive or get inheritance", 4: "Diminishes father's lifespan; fear for native, mother dies in childbirth", 5: "Children premature or miscarried.", 6: "Native healthy if lord of Ascendant does not look", 7: "Consumes inheritance of women; marries foreign woman", 8: "Native is healthy, illness insignificant, death will be light", 9: "Suffers robbery on journeys, eager in accumulating assets", 10: "Authority in youth, a follower who seeks leadership/boasts", 11: "Not well known/descended; does low work like commerce", 12: "Few enemies; many of native's slaves will die"},
    9: {1: "Remains in foreign land; travel; speaks knowledge; sensible if unharmed", 2: "Livelihood from travel, piety, religion", 3: "Siblings marry foreign women, live abroad", 4: "Unknown fathers who leave, with defects/bad death; bad faith", 5: "Has children abroad; they make native happy", 6: "Excellent intentions; illness while traveling, encounters hardship", 7: "Marries foreign woman given by her brother; native loves her", 8: "Bad thoughts and work; die in exile", 9: "Few journeys; upright in religion of fathers, good intention", 10: "Authority/leadership traveling abroad; offered the good", 11: "Good fortune abroad; happy until end of life", 12: "Siblings/native have hardship from enemies traveling; bad religion"},
    10: {1: "Interacting with Sultan, known by him, living due to Sultan", 2: "Livelihood from the Sultan", 3: "Death of siblings, jealousy and grudges", 4: "Fathers well known to Sultan", 5: "Defects and illnesses in children", 6: "Encounters hardship from the Sultan", 7: "Marriage to someone related to Sultan, fortunate woman, good from her", 8: "Native's ruin will be due to Sultan", 9: "Siblings marry better women or from Sultan's family; native is pious", 10: "Proficient in work, having influence, livelihood from work", 11: "Authority in friendship, Sultan will not be hostile", 12: "Hostility from Sultan and native's superiors; unhappy"},
    11: {1: "Good character, many friends, but harsh toward children/few children", 2: "Livelihood relates to friends/commerce; friends need native if Asc lord looks", 3: "Pious siblings known for that; reflects well on native", 4: "Short lifespan for father; bad condition unless received by fortune", 5: "Pleased by children and family; praise for him", 6: "Friends are not well known", 7: "Marries fertile woman, will love her, live in luxury because of her", 8: "Friends diminished; corrupts friendship; dies when condition is good", 9: "Pious friends, shared religious love; siblings marry foreign women", 10: "Friends benefit from native; child inherits assets from Sultan", 11: "Lives comfortable life, imputed with goodness, many friends, culture", 12: "Leaves goodness of friends; friends become enemies, unhappy"},
    12: {1: "Miserable, bad livelihood, enemies victorious; worse if bad connection", 2: "Life/livelihood from prisons, enemies; distressed and poor in soul", 3: "Hostile siblings; they get his authority and are superior", 4: "Parents are foreigners in exile; aspects show if good/bad for them", 5: "Children have defect/illness, will die; no children if unfortunate", 6: "Hostile to lower-status people; native sickly or ongoing health problems", 7: "Spouse has little esteem; hardship/hostility; secret relationships/cheating", 8: "Killing by enemies feared, or foolish people oppose him", 9: "Wicked intentions; corrupts religion, thinks he is right", 10: "Dispossessed by authorities; griefs; works with large animals/secrets", 11: "Little good, miserable life; few friends, many enemies", 12: "Few enemies, may not manifest; safe from them"}
}

# Delineations for a planet occupying a given Whole Sign House, keyed by
# [wsh_house][planet]['Good'|'Bad']; both readings are shown side by side
# (see evaluate_planets_in_houses()), synthesizing Rhetorius and PN4.
PLANETS_IN_HOUSES = {
    1: {'Saturn': {'Good': 'Eldest sibling; land ownership, building.', 'Bad': 'Sluggish, laborious; blamed.'}, 'Jupiter': {'Good': 'Glorious, in charge; celebrated, respected.', 'Bad': 'Decrease in assets, worries.'}, 'Mars': {'Good': 'Military, leader; successful, victorious.', 'Bad': 'Unstable, squandering; fugitive, misfortune.'}, 'Sun': {'Good': 'Noble, lucky; high rank, management.', 'Bad': 'Less noble, less benefit.'}, 'Venus': {'Good': 'Talented, friends of powerful; delight, clothing, sex.', 'Bad': 'Lustful, lower professions; disturbed life, quarrels.'}, 'Mercury': {'Good': 'Intellectual activities; status, praise.', 'Bad': 'Practical activities; loss in business.'}, 'Moon': {'Good': 'Increases of fortune, in charge.', 'Bad': 'Sailing, poor livelihood.'}},
    2: {'Saturn': {'Good': 'Slow increase, strong; unexpected source.', 'Bad': 'Loss, lazy, ill; abject sources.'}, 'Jupiter': {'Good': 'Good all around, inheritances; leisure.', 'Bad': 'Spending without enjoyment; distress.'}, 'Mars': {'Good': 'Military; enough; benefits from unexpected place.', 'Bad': 'Exile, dangers; squandering.'}, 'Sun': {'Good': 'Dignity, wealth; leisure.', 'Bad': 'Private property; negligence.'}, 'Venus': {'Good': 'Prosperous, pleasing, arts.', 'Bad': 'Disruption, corruption, stagnation.'}, 'Mercury': {'Good': 'Evening star by night: good at business; benefit from commerce, partnerships.', 'Bad': 'Morning star by night: obscure, bad, poor; evening star by day: good at learning, poor; loss, downturn in business, blame, quarrels.'}, 'Moon': {'Good': 'Brilliant, conspicuous, extravagant.', 'Bad': 'Family/actions dispersed and divided.'}},
    3: {'Saturn': {'Good': 'Initiates, religious chiefs; travel for benefit.', 'Bad': 'Recluses, bad religious reputation, confused thinking.'}, 'Jupiter': {'Good': 'Balanced moderation; good religious reputation, delight in siblings.', 'Bad': 'Distress from siblings, negligence in religion.'}, 'Mars': {'Good': 'Glory with labor; strong in travel.', 'Bad': 'Worse than by night?; evil reports, difficult travels, illness from heat, misfortune from wild animals.'}, 'Sun': {'Good': 'Bad death for father; serious in counsel, manages public things, religious honors; travel due to Sultan, good reputation from religion, good from relatives and brothers.', 'Bad': 'Bad reputation, distress due to travel/relatives.'}, 'Venus': {'Good': 'Travel with good/status, benefit from brothers.', 'Bad': 'Bad reports/journeys, contention with brothers.'}, 'Mercury': {'Good': 'Divination, astrologers, good journeys/visions.', 'Bad': 'Priests, magicians; bad travels, religious doubts.'}, 'Moon': {'Good': 'With Saturn: slow, unsuccessful, sacrilegious (Firmicus).', 'Bad': 'Ignoble or infamous mother; sacrilege with Mercury or Mars; but good religious activities if with Jupiter.'}},
    4: {'Saturn': {'Good': 'Lots of wealth; owning property, building.', 'Bad': 'Destroys/threatens parents, illness; blamed.'}, 'Jupiter': {'Good': 'Commanders, jurists; respected, land/family assets.', 'Bad': 'Middling assets; worries from these topics.'}, 'Mars': {'Good': 'Generals, soldiers; successful, inspiring awe.', 'Bad': 'Sickly, surgery; misfortune for home/land.'}, 'Sun': {'Good': 'Annoyances and interruptions in life, better in old age; increase in rank, gain good, commended, victory over enemies.', 'Bad': 'Destroys native, parents, and livelihood; little benefit, or harm, in enemies.'}, 'Venus': {'Good': 'Fortunate over time, charming; delight in important people.', 'Bad': 'Loss of patrimony, widowhood; conflict in land/family.'}, 'Mercury': {'Good': 'Lots of money, initiates; status from Mercurial things/govt.', 'Bad': 'Forbidden mysteries; accusation, family quarrels.'}, 'Moon': {'Good': 'Honored mother, good living standard.', 'Bad': 'Lowborn mother, commerce.'}},
    5: {'Saturn': {'Good': 'Kingships/command over time; delight in friends.', 'Bad': 'Delayed, sluggish; distress from children/siblings.'}, 'Jupiter': {'Good': 'Fortunate, honored, healthy; blessed by children.', 'Bad': 'Lower-status activities; distressed by children.'}, 'Mars': {'Good': 'Good possessions, honor; increase in children/rank.', 'Bad': 'Harmful travel; distress/accidents in family/children.'}, 'Sun': {'Good': 'Honored, easy goals; delight/increase in children.', 'Bad': 'Moderate fortune, childless; distress due to children.'}, 'Venus': {'Good': 'Prize-fighters, victors; increase/delight in women/children.', 'Bad': 'Distress from women and children.'}, 'Mercury': {'Good': 'Wealth, managing money; befriend nobles, profit.', 'Bad': 'Squanders money; hostility, illness/death of children.'}, 'Moon': {'Good': 'Gracious, leaders, fortunate.', 'Bad': 'Foreign travel, parents estranged, orphans.'}},
    6: {'Saturn': {'Good': 'Moderate; slaves/animals recover.', 'Bad': 'No inheritance, dangers from slaves, chronic illness.'}, 'Jupiter': {'Good': 'Exposure, valuable materials; praise from subordinates.', 'Bad': 'Illnesses, distress from enemies/confinement.'}, 'Mars': {'Good': 'Harms children, uneven life, illness (Firmicus); healthy, victory over enemies.', 'Bad': 'Worse than by night?; ailment from heat and moisture, disturbance of blood.'}, 'Sun': {'Good': 'With Jupiter and Venus, better than by night; mild-temperedness and safety.', 'Bad': 'Bad death or condemnation for father if no star in the 10th (with one, good fortune from parents and resources); illness from heat and dryness, pain in eyes and head.'}, 'Venus': {'Good': 'Sex with low-quality women, treated badly by wives unless a planet is in the 10th, or difficulties in pregnancy; with a planet in the 10th, charm and good fortune through women; benefit from the underclass and medicine.', 'Bad': 'See above; leisure time and illness.'}, 'Mercury': {'Good': 'Advancement through speech/business.', 'Bad': 'Idle, evil; illness, arrested, confinement.'}, 'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN4 cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]', 'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? for both the Rhetorius and PN4 cells of the Moon in the 6th; no sourced delineation exists; do not rely on this cell]'}},
    7: {'Saturn': {'Good': 'Success after delay, long-lived; owning property.', 'Bad': 'Sickly, blamed/harmed.'}, 'Jupiter': {'Good': 'Long-lived, wealth later; praised, respected.', 'Bad': 'Moderate living; worries.'}, 'Mars': {'Good': 'Professions from fire/violence; successful, inspiring awe.', 'Bad': 'Violent, short-lived; illnesses, spending.'}, 'Sun': {'Good': 'Increase in rank/land; administrators.', 'Bad': 'Lower-status activities; little benefit, or harm, in land, fathers, ancestors.'}, 'Venus': {'Good': 'Age difference/delay in marriage; delight, increase in rank.', 'Bad': 'Lewdness; distress in sex/marriage.'}, 'Mercury': {'Good': '(Diurnal) Bad with Venus or Mars: lewd, brothel-keepers, fugitives; status and rank from Mercurial things, serving the Sultan/govt, good reputation.', 'Bad': '(Nocturnal) Managing affairs of women, good fortune from sex, numbers, arts or writings; bad experiences from Mercurial things, accusation, loss in business, quarreling within the family.'}, 'Moon': {'Good': 'Changes, travel, better resources.', 'Bad': 'Foreign travel with dangers.'}},
    8: {'Saturn': {'Good': 'Assets over time/inheritance; good from dead.', 'Bad': 'Loss, bad death; squandering, distress.'}, 'Jupiter': {'Good': 'Acquisition, inheritance; leisure.', 'Bad': 'Spending without happiness; distress/fighting due to assets.'}, 'Mars': {'Good': 'Hot-heads, bright; benefit from dead/inheritance.', 'Bad': 'Patrimony spent, dangers; squandered assets.'}, 'Sun': {'Good': "Father's early death, healing; mild-temperedness.", 'Bad': 'See above; leisure but without benefit, poor way of life, negligence or laziness.'}, 'Venus': {'Good': 'Wealthy, benefit from death of women, easy death; benefit from underclass or base work, much spending.', 'Bad': 'Marry late, lower-quality women, STDs, seizures; negligence in assets, idleness, little benefit, fighting over assets.'}, 'Mercury': {'Good': 'Money, management, inheritance; praised.', 'Bad': 'Ineffective, lazy; blamed, quarreling due to assets.'}, 'Moon': {'Good': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN4 cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]', 'Bad': '[UNCERTAIN -- the TNAC Reference Guide (p. 32) prints ? for both the Rhetorius and PN4 cells of the Moon in the 8th; no sourced delineation exists; do not rely on this cell]'}},
    9: {'Saturn': {'Good': 'Initiates, chief priests; travel for benefit.', 'Bad': 'Recluses, anger at gods; confused religious opinions.'}, 'Jupiter': {'Good': 'Predicting future, priesthood; good religious reputation.', 'Bad': 'Unsteady, false speech; negligence in religion.'}, 'Mars': {'Good': 'Glory, unpunished; strong in travel.', 'Bad': 'Evil reports, difficult travels, illness.'}, 'Sun': {'Good': 'Building sacred things, religious authority.', 'Bad': 'Harm in travels; bad reputation, distress.'}, 'Venus': {'Good': 'Divine men, gifts from temples; travel with status.', 'Bad': 'Demon-afflicted, illicit sex; bad reports/journeys.'}, 'Mercury': {'Good': 'Priests, wizards; good journeys, true visions.', 'Bad': 'Seers, sacrificers; defamed in religion, bad assets.'}, 'Moon': {'Good': 'Living abroad, notable; benefiting from temples.', 'Bad': 'Wandering and dangers; temple servants.'}},
    10: {'Saturn': {'Good': 'Leaders, farmers; agriculture, building.', 'Bad': 'Bunglers, sorrow; blamed, low work.'}, 'Jupiter': {'Good': 'Athletes, famous, trusted; celebrated, respected.', 'Bad': 'Handsome but unstable; decreased assets, worry.'}, 'Mars': {'Good': 'Unstable, fearsome leaders; successful, favored by Sultan.', 'Bad': 'No accomplishments, fugitives; misfortune, violence.'}, 'Sun': {'Good': 'Rulers, leaders, dignity; increased rank, victorious.', 'Bad': 'Success through violence; fear from Sultan.'}, 'Venus': {'Good': 'Honored, musicians; honored by Sultan, delight.', 'Bad': 'Blamed, burdened, indecent; bad reputation.'}, 'Mercury': {'Good': 'Admirable, trusted; status from writing.', 'Bad': 'Changes, living abroad; accusation, loss.'}, 'Moon': {'Good': 'Rulers, successful, trusted.', 'Bad': 'Hardship, unsteady, error.'}},
    11: {'Saturn': {'Good': 'Middling goods over time; delight in friends.', 'Bad': 'Distress from children/siblings.'}, 'Jupiter': {'Good': 'Fortunate, renowned, authority; good way of life.', 'Bad': 'Diminished effectiveness; worries, distressed by friends.'}, 'Mars': {'Good': 'Many goods, dignity; increase in children/rank.', 'Bad': 'Feuding with friends and brothers.'}, 'Sun': {'Good': 'Lucky, noble; good condition, delight in friends.', 'Bad': 'Harms children; distress due to friends.'}, 'Venus': {'Good': 'Powerful, trusted; increase/delight in friends.', 'Bad': 'Sterility, unusual sexuality; hostility to friends.'}, 'Mercury': {'Good': 'Ingenious, accounts; befriend nobles, profit.', 'Bad': 'Spending, agents; hostility from friends, illness of children.'}, 'Moon': {'Good': 'Rulers, favored, good from parents.', 'Bad': 'Living abroad, estrangements, orphanhood.'}},
    12: {'Saturn': {'Good': 'Victory over enemies.', 'Bad': 'Loss of inheritance, mental disturbance; hardship from prison.'}, 'Jupiter': {'Good': 'Praise from subordinates; fights against superiors.', 'Bad': 'Illnesses, distress from enemies/confinement.'}, 'Mars': {'Good': 'Safety from enemies.', 'Bad': 'Illness, injury, dangers from slaves, criminals; something detestable from runaways, the confined, enemies.'}, 'Sun': {'Good': 'Good reputation, safety.', 'Bad': 'With infortunes, long illnesses, defects, slavery; confinement, distress due to enemies and the confined; exile.'}, 'Venus': {'Good': 'Benefit from underclass.', 'Bad': 'Ruined by women; leisure time and illness, punishment.'}, 'Mercury': {'Good': 'Managing big affairs; benefit from low work.', 'Bad': 'Danger from slaves; arrested unfairly, confinement.'}, 'Moon': {'Good': 'Luckiness/authority (with fortunes).', 'Bad': 'Short life, humble; bad for patrimony/travel.'}}
}

def evaluate_essential_dignities(planetary_data, sect):
    """Full 5-fold essential dignity hierarchy (Domicile/Exaltation/
    Triplicity/Term/Face) plus major debilities (Detriment/Fall) and
    Peregrine. Reuses get_essential_rulers() so the exact same lordship
    logic backs both a planet's own dignity score and the syzygy-degree
    lookup used elsewhere."""
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    results = {}
    for planet, data in planetary_data.items():
        if planet == 'North Node': continue

        lon = data['longitude']
        current_sign = get_zodiac_sign(lon)
        rulers = get_essential_rulers(lon)

        is_domicile = rulers['domicile'] == planet
        is_exalted = rulers['exaltation'] == planet
        is_triplicity = rulers[triplicity_key] == planet
        is_term = rulers['term'] == planet
        is_face = rulers['face'] == planet
        is_detriment = current_sign in DETRIMENTS.get(planet, [])
        is_fall = current_sign in FALLS.get(planet, [])

        has_positive = is_domicile or is_exalted or is_triplicity or is_term or is_face
        is_peregrine = not has_positive

        W = ESSENTIAL_DIGNITY_WEIGHTS
        score = (is_domicile * W['domicile'] + is_exalted * W['exaltation'] + is_triplicity * W['triplicity']
                 + is_term * W['term'] + is_face * W['face']
                 - is_detriment * 5 - is_fall * 4 - is_peregrine * 5)

        labels = []
        if is_domicile: labels.append(f"Dom (+{W['domicile']})")
        if is_exalted: labels.append(f"Exalt (+{W['exaltation']})")
        if is_triplicity: labels.append(f"Trip (+{W['triplicity']})")
        if is_term: labels.append(f"Term (+{W['term']})")
        if is_face: labels.append(f"Face (+{W['face']})")
        if is_detriment: labels.append("Detriment (-5)")
        if is_fall: labels.append("Fall (-4)")
        if is_peregrine: labels.append("Peregrine (-5)")

        results[planet] = {
            'Essential Score': score,
            'Domicile': is_domicile, 'Exalt': is_exalted, 'Triplicity': is_triplicity,
            'Term': is_term, 'Face': is_face, 'Detriment': is_detriment, 'Fall': is_fall,
            'Peregrine': is_peregrine, 'Essential Labels': labels,
        }
    return results

# --- Accidental dignity reference tables ---------------------------------
JOY_HOUSES = {'Mercury': 1, 'Moon': 3, 'Venus': 5, 'Mars': 6, 'Sun': 9, 'Jupiter': 11, 'Saturn': 12}
# Which author's domain (hayz) rule is in force. "Abu Ma'shar" is VII.1,
# 37 / VII.6, 13 (sign gender fixed to the planet's own). "Masha'allah" is
# On Nativities 1.23, 17: "in its own glow (and that is if the planet was
# male, by day above the earth in a male sign, and by night under the earth
# IN A FEMALE SIGN; and if it was feminine, by night it is above the earth
# and by day under the earth)" -- the sign's gender follows the hemisphere,
# and no sign is required of the feminine planets. Dykes' note there calls
# it "at odds with later accounts". Sidebar switch; Abu Ma'shar's is the
# default because the VII.6 table this feeds is his.
DOMAIN_RULE_OPTIONS = ("Abu Ma'shar", "Masha'allah")   # the sidebar radio and the test below share these
DOMAIN_RULE = DOMAIN_RULE_OPTIONS[0]
DIURNAL_SECT_PLANETS = {'Sun', 'Jupiter', 'Saturn'}
NOCTURNAL_SECT_PLANETS = {'Moon', 'Venus', 'Mars'}

def planet_sect_is_diurnal(planet, lon, sun_lon):
    """The planet's own sect. Mercury's follows his solar phase: west of the
    Sun (a morning riser) is diurnal, east of it nocturnal. This is the one
    test behind Strength testimony 85 and the Sect table on the Dignities
    page, so the two cannot disagree."""
    if planet == 'Mercury':
        return (((lon - sun_lon + 180.0) % 360.0) - 180.0) < 0
    return planet in DIURNAL_SECT_PLANETS
MASCULINE_SIGNS = {'Aries', 'Gemini', 'Leo', 'Libra', 'Sagittarius', 'Aquarius'}
FEMININE_SIGNS = {'Taurus', 'Cancer', 'Virgo', 'Scorpio', 'Capricorn', 'Pisces'}
# Mean daily motions (deg/day), used only to gauge "swift" vs. an average pace
AVERAGE_DAILY_MOTION = {'Sun': 0.9856, 'Moon': 13.1764, 'Mercury': 1.383, 'Venus': 1.2, 'Mars': 0.524, 'Jupiter': 0.083, 'Saturn': 0.034}
# A planet counts as stationary at or under this speed, in deg/day. One
# tolerance for the whole file: the Chart page's Motion column, the
# accidental scoring and the VII.6 station tests (24, 32) all read it. The
# VII.6 test used to carry its own 0.02, so a planet could be Direct on the
# Chart page and "First station (32)" on Configurations at the same moment.
# Neither source gives a figure; this is the app's own.
STATION_SPEED_TOLERANCE = 0.003
ANGLE_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
CADENT_HOUSES = {3, 6, 9, 12}
MALEFIC_HOUSES = {6, 8, 12}  # override to -5 regardless of their normal angularity group
HOUSE_ORDINAL = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th', 11: '11th', 12: '12th'}

# --- Solar phase: the sources' own orbs ----------------------------------
# Abu Ma'shar walks the whole synodic cycle planet by planet (Great
# Introduction VII.2): seventeen conditions for the superiors (6-34),
# sixteen for the inferiors (35-57), sixteen for the Moon (58-74). Sahl's
# On Nativities Ch.1.22, 1-8 (and Dykes' table there, which reports
# al-Biruni SS481-82 agreeing) gives the UNDER-THE-RAYS figures
# independently -- 15 for Saturn and Jupiter, 18 east for Mars, 12 east /
# 15 west for Venus and Mercury -- so those are not one author's
# idiosyncrasy. Sahl gives no "burned" boundary at all (his 6 is the
# nine-day "considered eastern" floor of 1.22, 1), and his table has Mars
# WESTERNIZING AT 18, not 15; the burn figures and Mars's 15 west are Abu
# Ma'shar's alone (synthesis/10_on_nativities_citation_audit.md):
#
#   Saturn, Jupiter  burned to 6 deg,  under the rays to 15 deg
#                    (VII.2, 11-13; the 15 also On Nativities 1.22, 1 and 6)
#   Mars             burned to 10 deg, under the rays to 18 deg east
#                    (VII.2, 11-13; the 18 also On Nativities 1.22, 3 and 6)
#   Venus, Mercury   burned to 7 deg,  under the rays to 12 deg east,
#                    15 deg west (VII.2, 40, 48, 51-52; the 12/15 also On
#                    Nativities 1.22, 7-8). VII.2, 37 is now legible in the OCR and
#                    states it outright: "called 'burned' until there comes
#                    to be up to 7 degrees between them and the Sun"; 40
#                    repeats it ("at a full 7 degrees in longitude, then
#                    they have passed beyond burning"). 44 gives 6 on the
#                    direct-eastern approach, which Dykes flags as probably
#                    an error for 7.
#   Moon             burned to 6 deg,  under the rays to 12 deg
#                    (VII.2, 60-61 and 72-74)
#
# Three things follow that the previous uniform 8.5 deg / 15 deg pair could
# not express. The orbs are PER PLANET, not one number for all. They are
# ASYMMETRIC about the Sun -- Mars reaches 18 deg easternizing but only
# 15 deg setting, Venus and Mercury 12 deg east against 15 deg west. And
# the burned band is much tighter than 8.5 deg for everything except Mars.
#
# Note what is deliberately NOT modelled. Abu Ma'shar's fifteenth condition
# for the superiors, "in the degrees of setting" (VII.2, 30-31), runs from
# 22 deg down to 15 deg, and Sahl 1.22, 2 likewise calls Saturn and Jupiter
# "considered western" from 22 deg. That is a seven-day allowance for a
# planet that is about to go under the rays, not a planet already under
# them: Abu Ma'shar only starts saying "under the rays" at 15 deg. It is
# reported as a label below, and scored at zero.
#
# (east, west) in degrees; the split is by which side of the Sun the planet
# stands, east = rising before him = a morning star.
SOLAR_BURNED_ORB = {
    'Saturn': (6.0, 6.0), 'Jupiter': (6.0, 6.0), 'Mars': (10.0, 10.0),
    'Venus': (7.0, 7.0), 'Mercury': (7.0, 7.0), 'Moon': (6.0, 6.0),
}
SOLAR_RAYS_ORB = {
    'Saturn': (15.0, 15.0), 'Jupiter': (15.0, 15.0), 'Mars': (18.0, 15.0),
    'Venus': (12.0, 15.0), 'Mercury': (12.0, 15.0), 'Moon': (12.0, 12.0),
}
# The Moon's 12 degrees is Abu Ma'shar's (VII.2, 61 and 72-73). Sahl gives
# 15 in On Nativities 1.19, 6: "if the Moon was under the rays, she will not
# be fit ... (and that is if there was 15 degrees between her and the Sun,
# in front of him and behind him)" -- On Nativities 1.22 covers only the
# five planets, so the Moon has two witnesses that disagree. Sidebar switch.
MOON_RAYS_ORB = 12.0
# Mars going under the rays on the WESTERN side: 15 degrees is Gr. Intr.
# VII.2, 31's ("in the degrees of setting until there come to be 15 degrees
# between them and the Sun"; the default). The 18 of the switch is DYKES'S
# chapter-head table in On Nativities 1.22 and his fn 175, which works
# VII.2, 30's westernizing boundary into an 18-degree "under the rays" --
# Sahl's own sentences are silent on Mars west (the label said "Sahl's
# table" until 2026-09-11; decision sheet row 10, DEC-D-15). Both give 18
# east. Chart-page switch like the Moon's. Rare: a 3-degree band on one planet.
MARS_WEST_RAYS_18 = False

def solar_rays_orb(planet):
    """(east, west) under-the-rays limits with both switches applied."""
    if planet == 'Moon':
        return (MOON_RAYS_ORB, MOON_RAYS_ORB)
    east, west = SOLAR_RAYS_ORB.get(planet, (15.0, 15.0))
    if planet == 'Mars' and MARS_WEST_RAYS_18:
        west = 18.0
    return (east, west)
# The seven-day setting allowance (VII.2, 30-31; On Nativities 1.22, 2-4).
# VII.2, 30 gives the two figures separately: the superiors do not cease
# to be "westernizing" "until there are 22 degrees between Saturn and
# Jupiter and [the Sun] in the west (AND 18 DEGREES BETWEEN MARS AND [THE
# SUN])", after which 31 puts them "in the degrees of setting" down to 15.
# Mars carried 22 here, which is his figure from Sahl's On Nativities 1.22
# table, not from the chapter this constant cites.
SOLAR_SETTING_DEGREES = {'Saturn': 22.0, 'Jupiter': 22.0, 'Mars': 18.0}
# How VII.6, 27 and 45 read "eastern/western relative to the Sun" for the
# superiors: 'hemisphere' (the half, excluding the rays) or 'VII.2 band'
# (the easternizing/westernizing bands VII.2, 14-21 and 29-31 name). Set
# from the sidebar; see the comment at the test.
EASTERN_RULE_OPTIONS = ('hemisphere', 'VII.2 band')   # the sidebar radio and the test share these
EASTERN_RULE = EASTERN_RULE_OPTIONS[0]
# "In the heart." Abu Ma'shar fixes this at 16', reasoning from the Sun's
# own apparent diameter of about 32' (VII.2, 7-9), and Dykes notes that
# al-Biruni has 16' as well. Sahl instead says "with him in one degree"
# (The Introduction Ch.3, 87; Fifty Aphorisms #40, 79), which is measured
# separately where Sahl's own testimony is scored. The 17' this once used
# is the later Lilly-era convention and belongs to neither.
CAZIMI_ORB = 16.0 / 60.0

def solar_phase(planet, lon, sun_lon, speed_in_lon=None):
    """Where a planet stands relative to the Sun, per Gr. Intr. VII.2 and
    Sahl, On Nativities Ch.1.22. Returns (phase, side, elongation) where
    phase is one of 'Cazimi', 'Burned', 'Under the rays', 'Degrees of
    setting' or None, and side is 'eastern' (rising before the Sun, a
    morning star) or 'western'.

    `speed_in_lon` matters for Venus and Mercury on the eastern side only:
    VII.2 gives the inferiors TWO eastern burned limits -- 7 degrees while
    they leave the Sun after the conjunction (37, 40) and, AS PRINTED, 6
    degrees when they have stationed, "go direct in the east" (43) and
    close on him again (44: "simply under the rays until there are 6
    degrees between them and [the Sun]", then 45 "burned under the rays").
    Dykes fn 43: "To me it seems this should be 7 as in 40, but this is
    what the text says." The text's 6 is applied to a direct eastern
    inferior (order CONV-SOLAR_BURNED_ORB, 2026-09-11); a retrograde one
    keeps 37/40's 7, the western side 47's 7. Without a speed the 7
    stands, a reading solar_phase_note says on the row."""
    if planet == 'Sun':
        return None, None, 0.0
    signed = ((lon - sun_lon + 180.0) % 360.0) - 180.0
    elongation = abs(signed)
    side = 'eastern' if signed < 0 else 'western'
    idx = 0 if side == 'eastern' else 1
    if elongation <= CAZIMI_ORB:
        return 'Cazimi', side, elongation          # VII.2, 7-9: 16' inclusive, both sides
    # Endpoint ownership differs by side (Astra F10). EAST: a planet leaves
    # burning, and later the rays, "when these three planets come to the
    # COMPLETION of these degrees" (VII.2, 12; 14; 40-41 for the inferiors:
    # "distant ... at a FULL 7 degrees ... they have passed beyond burning"),
    # so exactly 6 (10, 7) east is already "simply under the rays" and
    # exactly 15 (18, 12) east already easternizing. WEST: the phases are
    # entered AT their degrees -- "until there come to be 15 degrees ... and
    # when they come to these degrees they shift over" (VII.2, 31-32, 34) --
    # so the western bounds stay inclusive.
    within = (lambda x, lim: x < lim) if side == 'eastern' else (lambda x, lim: x <= lim)
    burned = SOLAR_BURNED_ORB.get(planet, (8.5, 8.5))[idx]
    if planet in ('Venus', 'Mercury') and side == 'eastern' and speed_in_lon is not None and speed_in_lon > 0:
        burned = INFERIOR_DIRECT_EASTERN_BURNED   # VII.2, 44 as printed; see the docstring
    if within(elongation, burned):
        return 'Burned', side, elongation
    rays = solar_rays_orb(planet)[idx]
    if within(elongation, rays):
        return 'Under the rays', side, elongation
    setting = SOLAR_SETTING_DEGREES.get(planet)
    if side == 'western' and setting is not None and elongation <= setting:
        return 'Degrees of setting', side, elongation
    return None, side, elongation

# VII.2, 44 as printed: the direct eastern inferior's burned limit. fn 43
# reads it as an error for 40's 7; the engine applies the printed 6 and
# labels the band where the two differ (6-7 degrees). CONV-SOLAR_BURNED_ORB.
INFERIOR_DIRECT_EASTERN_BURNED = 6.0

def solar_phase_note(planet, side, speed_in_lon, elongation):
    """The label suffix for the one band where VII.2, 44's printed 6 and
    fn 43's 7 disagree: a direct eastern Venus or Mercury 6-7 degrees from
    the Sun. Empty elsewhere. Without a speed the row says the 7 of 37/40
    was used."""
    if planet not in ('Venus', 'Mercury') or side != 'eastern':
        return ''
    if not (INFERIOR_DIRECT_EASTERN_BURNED <= elongation < SOLAR_BURNED_ORB[planet][0]):
        return ''
    if speed_in_lon is None:
        return " -- motion unknown: 37/40's 7 degrees used, not 44's printed 6"
    if speed_in_lon > 0:
        return " -- VII.2, 44 as printed (6 degrees), not 40's 7; Dykes fn 43: 'should be 7 as in 40'"
    return " -- retrograde in the east: 37/40's 7 degrees, not 44's 6"

def evaluate_accidental_dignities(planetary_data, natal_houses, sect, jd=None,
                                  armc=None, obliquity=None, geo_lat=None):
    """Accidental dignity scoring: house angularity (Whole Sign, anchored to
    the Ascendant, with the 6/8/12 malefic-house override), planetary joys,
    domain/hayz, motion & speed, and solar phase.

    The point weights (+5 angular, -5 combust, and so on) are this app's own
    convenience for ranking, not anybody's doctrine -- no source in hand adds
    these conditions up. What IS sourced is the geometry each test uses, and
    each of those carries its citation at the point of use.

    `armc`, `obliquity` and `geo_lat` are the chart's horizon. With them the
    domain's "above the earth / below the earth" (Gr. Intr. VII.1, 37;
    VII.6, 13) is decided by the planet's ALTITUDE from its full ecliptic
    position (_sin_altitude, as sect and the syzygy already are); without
    them it falls back to the ecliptic proxy (lon - Ascendant) % 360 > 180,
    which misplaces a body within a degree or two of the horizon and says
    so in the row ('Hemisphere by'). Astra audit F04, 2026-09-11."""
    sun_lon = planetary_data['Sun']['longitude']
    ascendant = natal_houses[0]
    is_diurnal_chart = (sect == 'Diurnal')
    results = {}

    for planet, data in planetary_data.items():
        if planet == 'North Node': continue
        lon, speed = data['longitude'], data['speed_in_lon']
        labels = []
        score = 0

        # --- House angularity (Whole Sign) --------------------------------
        house_num = get_wsh_house(lon, ascendant)
        if house_num in MALEFIC_HOUSES:
            house_pts, house_label = -5, f"Malefic {HOUSE_ORDINAL[house_num]} (-5)"
        elif house_num in ANGLE_HOUSES:
            house_pts, house_label = 5, f"Angular {HOUSE_ORDINAL[house_num]} (+5)"
        elif house_num in SUCCEDENT_HOUSES:
            house_pts, house_label = 3, f"Succedent {HOUSE_ORDINAL[house_num]} (+3)"
        else:
            house_pts, house_label = -3, f"Cadent {HOUSE_ORDINAL[house_num]} (-3)"
        score += house_pts
        labels.append(house_label)

        # --- Planetary joy -------------------------------------------------
        is_joy = JOY_HOUSES.get(planet) == house_num
        if is_joy:
            score += 3
            labels.append("Joy (+3)")

        # --- Sect / Hayz -----------------------------------------------
        # All three must hold: the planet's own sect matches the chart's
        # sect, it's on its sect-favored side of the horizon, and it's in
        # a sign of its sect-favored gender. Mercury's own sect is derived
        # from its solar phase (morning riser = diurnal, evening star =
        # nocturnal) rather than being fixed.
        current_sign = get_zodiac_sign(lon)
        if armc is not None and obliquity is not None and geo_lat is not None:
            is_above_horizon = _sin_altitude(lon, data.get('latitude', 0.0), data.get('distance', 1.0),
                                             obliquity, armc, geo_lat) > 0.0
            hemisphere_by = 'altitude'
        else:
            is_above_horizon = (lon - ascendant) % 360 > 180.0
            hemisphere_by = 'ecliptic proxy (no horizon supplied)'

        if planet == 'Mercury':
            signed = ((lon - sun_lon + 180.0) % 360.0) - 180.0
            planet_is_diurnal = signed < 0  # west of the Sun = morning star
        elif planet in DIURNAL_SECT_PLANETS:
            planet_is_diurnal = True
        elif planet in NOCTURNAL_SECT_PLANETS:
            planet_is_diurnal = False
        else:
            planet_is_diurnal = None

        # Abu Ma'shar states the condition twice, identically: "a male planet
        # by day is above the earth (AND BY NIGHT BELOW THE EARTH), in a male
        # sign; but if it was female, then by day it is below the earth (and
        # by night above the earth), in a female sign -- except for Mars
        # alone, because he is contrary to what we said" (Great Introduction
        # VII.1, 37), and again at VII.6, 13. Al-Qabisi I.78 has the
        # hemisphere-by-sect half only (Dykes' note 222 on VII.6, 10, glossing
        # halb; the note on 13 itself just points back to VII.1, 37-39). The
        # chart's sect does NOT have to match
        # the planet's: the HEMISPHERE requirement is what flips with it, so
        # a diurnal planet below the earth in a masculine sign is in its
        # domain in a nocturnal chart. An earlier version additionally
        # required the planet's own sect to match the chart's, which threw
        # away that entire second half of the rule.
        #
        # Mars's exception applies to the HEMISPHERE ONLY. He is masculine
        # in every source here, so the sign-gender half of the test is not
        # what "contrary to what we said" reverses -- and VII.6, 13 restates
        # the whole rule with no Mars exception at all. Dykes' note on
        # VII.1, 37 points the same way ("Mars will stand out because he is
        # a MALE, NOCTURNAL planet"), and the Course Glossary defines Domain
        # as "in a sign of ITS OWN GENDER and also in its preferred
        # hemisphere". Sahl's own glossary (Vol. I p. 777, Domain; p. 782,
        # Halb and Hayyiz) is a second witness in the corpus itself, and it
        # keeps the two conditions apart: HALB is "for diurnal planets, when
        # they are in the same hemisphere as the Sun ... for nocturnal
        # planets, when they are in the hemisphere opposite the Sun";
        # HAYYIZ/DOMAIN is "technically equivalent to halb, except that the
        # planet is also in a sign of its own gender". That split is what
        # DOMAIN_RULE_OPTIONS exposes. An earlier version flipped him on both
        # tests, which required him to be in feminine signs -- a reading no
        # text states.
        mars_is_masculine_but_nocturnal = (planet == 'Mars')
        is_hayz = contrary_domain = False
        if planet_is_diurnal is not None and DOMAIN_RULE == DOMAIN_RULE_OPTIONS[1]:
            # On Nativities 1.23, 17 (see DOMAIN_RULE). Gender, not sect:
            # Mars is male, with no exception stated.
            planet_is_male = mars_is_masculine_but_nocturnal or planet_is_diurnal
            if planet_is_male:
                horizon_ok = is_above_horizon if is_diurnal_chart else not is_above_horizon
                gender_ok = (current_sign in MASCULINE_SIGNS) if is_diurnal_chart else (current_sign in FEMININE_SIGNS)
            else:
                horizon_ok = not is_above_horizon if is_diurnal_chart else is_above_horizon
                gender_ok = True          # no sign condition is stated for the feminine planets
            is_hayz = horizon_ok and gender_ok
            contrary_domain = (not horizon_ok) and (not gender_ok)
        elif planet_is_diurnal is not None:
            if planet_is_diurnal:
                horizon_ok = is_above_horizon if is_diurnal_chart else not is_above_horizon
            else:
                horizon_ok = not is_above_horizon if is_diurnal_chart else is_above_horizon
            # Sign gender follows the PLANET'S OWN gender, not its sect.
            # They coincide for six of the seven; Mars is the one that
            # comes apart, and he keeps the masculine signs.
            if mars_is_masculine_but_nocturnal or planet_is_diurnal:
                gender_ok = current_sign in MASCULINE_SIGNS
            else:
                gender_ok = current_sign in FEMININE_SIGNS
            is_hayz = horizon_ok and gender_ok
            # VII.6, 36 spells out the opposite pole: "the male ones are in a
            # FEMALE sign ... by day, under the earth, and by night above the
            # earth." Both halves inverted, not either one -- VII.1, 39 keeps
            # the single-failure case as a separate, milder "it takes away
            # from the nature of balance."
            contrary_domain = (not horizon_ok) and (not gender_ok)
        if is_hayz:
            score += 3
            labels.append("Hayz/domain (+3)")
        elif contrary_domain:
            labels.append("Contrary to its domain")

        # --- Motion & speed -------------------------------------------
        # "Increasing in its rate of movement (with respect to the five
        # planets) is that it travels more than its mean motion" -- Great
        # Introduction VII.1, 29. But 30-31 immediately excepts the two
        # inferiors: "the mean motion of Venus and Mercury in one day at a
        # [particular] time is not like their mean travel for the day," so
        # for them the comparison is against the SUN's motion that day, not
        # their own mean. An earlier version measured all seven against
        # their own means.
        is_stationary = abs(speed) <= STATION_SPEED_TOLERANCE
        is_retrograde = speed < 0 and not is_stationary and planet not in ('Sun', 'Moon')
        if planet in ('Venus', 'Mercury'):
            pace = planetary_data['Sun']['speed_in_lon']
        else:
            pace = AVERAGE_DAILY_MOTION.get(planet, 1.0)
        is_swift = (not is_stationary) and (not is_retrograde) and speed > pace
        # Sahl separates the two stations sharply: stationing toward
        # retrogradation "indicates collapse in the matter, and disobedience
        # ... corruption, difficulty," while stationing toward direct motion
        # "indicates forward movement in that matter, with no difficulty ...
        # the suitability of the affair, and its strength" (Fifty Aphorisms
        # #48, 99-102). Abu Ma'shar likewise makes them separate conditions,
        # the seventh and the eleventh (VII.2, 23 and 27), and VII.6 counts
        # the first station a weakness (32) and the second a strength (24).
        # An earlier version scored both alike at -2.
        station = None
        if is_stationary and jd is not None and planet in PLANET_SWE_IDS:
            try:
                res_next, _ = swe.calc_ut(jd + 1.0, PLANET_SWE_IDS[planet])
                station = 'second' if res_next[3] > speed else 'first'
            except Exception:
                station = None
        if is_stationary:
            if station == 'second':
                score += 2
                labels.append("Second station, going direct (+2)")
            elif station == 'first':
                score -= 4
                labels.append("First station, turning retrograde (-4)")
            else:
                score -= 2
                labels.append("Stationary (-2)")
        elif is_retrograde:
            score -= 5
            labels.append("Retrograde (-5)")
        elif is_swift:
            score += 2
            labels.append("Swift (+2)")

        # --- Solar phase (Gr. Intr. VII.2; Sahl, On Nativities 1.22) --
        phase, side, elongation = solar_phase(planet, lon, sun_lon, speed)
        is_cazimi = phase == 'Cazimi'
        is_combust = phase == 'Burned'
        is_under_beams = phase == 'Under the rays'
        if is_cazimi:
            score += 5
            labels.append("Cazimi/in the heart (+5)")
        elif is_combust:
            score -= 5
            labels.append(f"Burned, {side} ({elongation:.1f} deg) (-5)" + solar_phase_note(planet, side, speed, elongation))
        elif is_under_beams:
            score -= 2
            labels.append(f"Under the rays, {side} ({elongation:.1f} deg) (-2)" + solar_phase_note(planet, side, speed, elongation))
        elif phase == 'Degrees of setting':
            labels.append(f"In the degrees of setting ({elongation:.1f} deg)")

        results[planet] = {
            'Accidental Score': score, 'House': house_num, 'Joy': is_joy, 'Hayz': is_hayz,
            'Above the earth': is_above_horizon, 'Hemisphere by': hemisphere_by,
            'ContraryDomain': contrary_domain, 'Station': station,
            'Stationary': is_stationary, 'Retrograde': is_retrograde, 'Swift': is_swift,
            'Cazimi': is_cazimi, 'Combust': is_combust, 'UnderBeams': is_under_beams,
            'SolarPhase': phase, 'SolarSide': side, 'Elongation': elongation,
            'Accidental Labels': labels,
        }
    return results

# Whole-sign configuration allowed by classical Ptolemaic doctrine: how many
# signs apart the two bodies must be for a given aspect, and its exact angle.
ASPECT_BY_SIGN_COUNT = {
    0: ('Conjunction', 0.0),
    2: ('Sextile', 60.0),
    3: ('Square', 90.0),
    4: ('Trine', 120.0),
    6: ('Opposition', 180.0),
}

# The two sign-distances left uncovered by ASPECT_BY_SIGN_COUNT: 1 sign
# apart (2nd/12th from each other) and 5 signs apart (6th/8th from each
# other). A place in either relationship to another is in Aversion to it --
# unconfigured, and unable to see it by the classical aspect scheme at all,
# regardless of how close the raw degree separation happens to land
# (Sahl, The Introduction Ch.2, 60).
AVERSION_SIGN_COUNTS = {1, 5}

# Each planet's own orb/"body" radius, front and behind (degrees) --
# Gr. Intr. VII.3, Fig. 105 ("bodies or orbs of
# planets"), identical to Sahl's "light" figures (The Introduction Ch.3,
# 12-18). One shared constant: used for Assembly-strength grading below,
# for the Connection engine, and for the Abu Ma'shar condition evaluator.
PLANETARY_ORBS = {'Sun': 15.0, 'Moon': 12.0, 'Saturn': 9.0, 'Jupiter': 9.0,
                   'Mars': 8.0, 'Venus': 7.0, 'Mercury': 7.0}

# The standing order of the planets by weight, heaviest (and so naturally
# slowest) first. This is the classical hierarchy the sources treat as
# fixed when they speak of "the light planet" and "the heavy planet", and
# it is the single definition of light/heavy used everywhere in this file:
# for the giver/accepter roles in _pairwise_configurations(), and for the
# heavier "collector" in evaluate_collections_of_light(). Instantaneous
# speed is a separate question, answered separately.
WEIGHT_ORDER = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']

def _format_orb(degrees):
    dd = int(degrees)
    mm = int(round((degrees - dd) * 60))
    if mm == 60:
        dd += 1
        mm = 0
    return f"{dd:02d}\u00b0 {mm:02d}'"

def _pairwise_configurations(planetary_data):
    """Shared per-pair raw data for every classical-planet combination:
    whole-sign gate (Sahl, The Introduction Ch.2, 50-60), the light/heavy
    roles, and (for configured pairs) the signed deviation from the exact
    (partile) aspect and its Applying/Separating motion. Consumed by
    evaluate_ptolemaic_aspects() and the Connection/Transfer/Collection
    evaluators so the gate & kinetics logic lives in exactly one place."""
    planets = [p for p in planetary_data.keys() if p != 'North Node']
    rows = []

    for p1, p2 in combinations(planets, 2):
        lon1, v1 = planetary_data[p1]['longitude'], planetary_data[p1]['speed_in_lon']
        lon2, v2 = planetary_data[p2]['longitude'], planetary_data[p2]['speed_in_lon']

        # --- 0. The light/heavy roles ------------------------------------
        # "Light" and "heavy" are the fixed classes both authors name as
        # nouns -- "the light planet", "the heavy planet" (Sahl Ch.3, 6-8,
        # 22, 67) -- so they are taken from the standing weight order,
        # NOT from instantaneous speed. The role decides who gives and who
        # accepts (67: "the one handing over is the light planet ... the
        # accepting one is the heavy planet"), whose light measures the
        # connection (19), and who casts the ray.
        #
        # An earlier version ranked by abs(speed_in_lon), which let a
        # transient reading flip the hierarchy: across an 860-year weekly
        # sample that disagrees with the standing order on 8% of pairs,
        # including Saturn/Jupiter on 23% and Saturn/Mercury on 2% --
        # i.e. it repeatedly made Saturn the LIGHT planet, which no source
        # allows. It also contradicted this same file, since Collection of
        # Light has always picked its heavier "collector" from WEIGHT_ORDER.
        #
        # Actual signed motion still decides everything kinetic below
        # (applying, separating, stationing, retrograde); the two are
        # simply no longer the same question. Note the Applying/Separating
        # result is invariant under this change: swapping the roles flips
        # the sign of both `s` and `delta_v`, and only their product is
        # used.
        if WEIGHT_ORDER.index(p1) > WEIGHT_ORDER.index(p2):
            light_name, fast_lon, light_speed = p1, lon1, v1
            heavy_name, slow_lon, heavy_speed = p2, lon2, v2
        else:
            light_name, fast_lon, light_speed = p2, lon2, v2
            heavy_name, slow_lon, heavy_speed = p1, lon1, v1

        # The kinetic facts, kept separate from the roles above.
        swifter_name = p1 if abs(v1) >= abs(v2) else p2
        light_retrograde = light_speed < 0
        heavy_retrograde = heavy_speed < 0

        raw_dist = abs(lon1 - lon2)
        dist = raw_dist if raw_dist <= 180.0 else 360.0 - raw_dist

        # --- 1. Whole-sign configuration gate ---------------------------
        # Reject any pair whose SIGNS aren't in a valid Ptolemaic relationship
        # (0/2/3/4/6 signs apart) -- this is what prohibits out-of-sign aspects
        # regardless of how close the raw degree separation happens to land.
        # A pair 1 or 5 signs apart is in Aversion instead: not configured,
        # and unable to form any aspect at all.
        sign_idx1 = int(lon1 // 30)
        sign_idx2 = int(lon2 // 30)
        raw_signs_apart = abs(sign_idx1 - sign_idx2)
        signs_apart = min(raw_signs_apart, 12 - raw_signs_apart)

        # --- 1b. Facts that are independent of the whole-sign gate -------
        # Each planet's body projects its own sphere of power outward
        # (Gr. Intr. VII.3, 6-11; VII.4, 5-8), so "is A inside B's
        # body" and "is B inside A's body" are separate questions with
        # separate answers, and the pair is only MUTUALLY merged when the
        # separation fits inside the smaller of the two. VII.4, 7 spells
        # this out: with Saturn and the Moon within 12 degrees, Saturn is
        # in the power of the Moon's body while the Moon is not yet in the
        # power of Saturn's, "until there is a little under 9 degrees
        # between them." (This is per-planet spheres, NOT a moiety --
        # nothing in either author averages the two orbs.)
        light_orb = PLANETARY_ORBS.get(light_name, 7.0)
        heavy_orb = PLANETARY_ORBS.get(heavy_name, 7.0)
        light_in_heavy_body = dist <= heavy_orb
        heavy_in_light_body = dist <= light_orb

        row = {
            'p1': p1, 'p2': p2, 'light_name': light_name, 'heavy_name': heavy_name,
            'light_speed': light_speed, 'heavy_speed': heavy_speed,
            'signs_apart': signs_apart, 'dist': dist,
            'swifter_name': swifter_name,
            'light_retrograde': light_retrograde,
            'heavy_retrograde': heavy_retrograde,
            # Gr. Intr. VII.5, 24: "sometimes at the assembly both of the
            # two planets will be retrograde, or one of them will be
            # retrograde and the other direct: the connection of one of
            # them with the other, and its separation from it, will be BY
            # RETROGRADATION." Neither author reassigns the light/heavy
            # roles in that case, so the roles stand and the fact is
            # surfaced instead of being silently resolved. Cf. the note on
            # VII.5, 130: Saturn "could never be received because he is too
            # slow to connect with anyone (unless by retrogradation)."
            'by_retrogradation': light_retrograde or heavy_retrograde,
            'assembly': signs_apart == 0,
            'light_orb': light_orb, 'heavy_orb': heavy_orb,
            'light_in_heavy_body': light_in_heavy_body,
            'heavy_in_light_body': heavy_in_light_body,
            'mutual_body': light_in_heavy_body and heavy_in_light_body,
            # Set by the post-pass below; only ever true on Aversion rows.
            'sahl_body_connection': False,
            # Directed agency, filled in for configured pairs at 2b below.
            # Distinct from light_name/heavy_name, which are the STANDING
            # ranks and never move.
            'applicant': None, 'receiver': None, 'application_cause': None,
            'applicant_is_heavier': False,
        }

        if signs_apart in AVERSION_SIGN_COUNTS:
            row.update(aspect_name='Aversion', deviation=None, motion=None, orientation=None)
            rows.append(row)
            continue

        aspect_name, target = ASPECT_BY_SIGN_COUNT[signs_apart]

        # --- 2. Kinetic direction: Applying (ittisal) vs Separating (insiraf)
        # s = signed position of the faster body relative to the receiver,
        # wrapped to (-180, 180]. deviation = dist - target is how far off
        # from the exact aspect we currently are; its time-derivative is
        # sign(s) * delta_v. Deviation shrinking toward zero => Applying.
        deviation = dist - target  # signed distance from partile (exact)
        s = ((fast_lon - slow_lon + 180.0) % 360.0) - 180.0
        sign_s = 1.0 if s >= 0 else -1.0
        delta_v = light_speed - heavy_speed
        rate = sign_s * delta_v
        motion = "Applying" if (deviation == 0 or deviation * rate < 0) else "Separating"

        # --- 2b. Who is actually approaching whom ------------------------
        # Natural rank (above) is one fact; DIRECTED AGENCY is another, and
        # the two come apart whenever the naturally heavier planet is the
        # one closing the gap.
        #
        # Sahl states the ordinary case: "connection is if a light, quick
        # star is GOING STRAIGHTAWAY TO a heavy star, and the light star is
        # FEWER IN DEGREES than the heavy one, as long as the [light] planet
        # is GOING TOWARDS the [heavy] planet" (Ch.3, 6), and "the one
        # handing over is the light planet ... the accepting one is the
        # heavy planet" (67). Both clauses assume forward motion, and in
        # forward motion the lighter planet is always the one that closes.
        #
        # Retrogradation breaks that assumption, and both authors say so
        # rather than leaving it to be inferred. Abu Ma'shar: "sometimes at
        # the assembly both of the two planets will be retrograde, or one of
        # them will be retrograde and the other direct: the connection of
        # one of them with the other, and its separation from it, will be BY
        # RETROGRADATION" (VII.5, 24). His Resistance turns on it --
        # "the light one IN MORE DEGREES goes retrograde and connects with
        # the heavy one through its retrogradation" (VII.5, 118), reversing
        # 6's fewer-degrees clause outright -- and Fig. 138's Resistance has
        # Venus retrograde connecting with Mercury, who is lighter than she
        # is. Dykes' note on VII.5, 130 makes the consequence explicit:
        # Saturn "could never be received because he is too slow to connect
        # with anyone (UNLESS BY RETROGRADATION)." And the note on Fifty
        # Aphorisms #19 says the same from the other side: "it would only be
        # possible for Saturn to be the one HANDING OVER if he is
        # retrograde."
        #
        # So the applicant is whichever planet's own motion is closing the
        # aspect, and the receiver is the one being approached. When both
        # move toward each other neither is fleeing, and 67's plain rule
        # stands: the naturally lighter planet is the one handing over.
        contrib_light = sign_s * light_speed   # d(deviation)/dt from the light planet alone
        contrib_heavy = -sign_s * heavy_speed  # ... and from the heavy one alone
        if deviation == 0:
            acting_light = acting_heavy = True
        elif motion == 'Applying':
            acting_light = deviation * contrib_light < 0
            acting_heavy = deviation * contrib_heavy < 0
        else:
            acting_light = deviation * contrib_light > 0
            acting_heavy = deviation * contrib_heavy > 0
        if acting_heavy and not acting_light:
            applicant, receiver = heavy_name, light_name
            cause = 'retrogradation' if heavy_retrograde else 'its own motion'
        elif acting_light and not acting_heavy:
            applicant, receiver = light_name, heavy_name
            cause = 'retrogradation' if light_retrograde else 'direct motion'
        else:
            applicant, receiver = light_name, heavy_name
            cause = 'mutual approach' if motion == 'Applying' else 'mutual recession'
        row.update(applicant=applicant, receiver=receiver, application_cause=cause,
                    applicant_is_heavier=(applicant == heavy_name))

        # --- 3. Dexter / Sinister orientation ----------------------------
        # Conjunction and Opposition have no handedness. Handedness is
        # reciprocal (if A's ray to B is dexter, B's to A is sinister), so
        # it needs a stated caster: here it is always the FASTER planet.
        # A dexter ("right") ray is cast against the order of signs, onto
        # EARLIER degrees; a sinister ("left") ray is cast with the order
        # of signs, onto LATER degrees. So a faster planet already ahead
        # of the receiver (s > 0) is casting backwards onto it = Dexter;
        # trailing it (s < 0) it casts forwards = Sinister. These two were
        # transposed in an earlier version.
        if aspect_name in ('Conjunction', 'Opposition'):
            orientation = "Direct"
        else:
            orientation = "Dexter" if s > 0 else "Sinister"

        row.update(aspect_name=aspect_name, target=target, deviation=deviation,
                    motion=motion, orientation=orientation)
        rows.append(row)

    # --- 4. Sahl's out-of-sign connection by body (Ch.3, 20-21) ---------
    # "And if a planet was at the end of a sign, NOT CONNECTING WITH
    # ANYTHING, and it has already struck into the next sign with its own
    # light, then whatever planet was the first in that light, it is
    # connected with it. 21 And if it was not in the sign, then it will not
    # see it." The translator's note on 21 is explicit: such a pair does
    # not SEE each other (the next sign is in aversion), yet they are still
    # CONNECTED -- "the sentence is emphasizing the existence of
    # out-of-sign conjunctions by body. But it does not support out-of-sign
    # aspects." So this applies only to adjacent signs, only forward (the
    # light strikes INTO the next sign), and only when the striking planet
    # has no other connection at all. Abu Ma'shar denies this case outright
    # -- see _is_connected_abu_mashar().
    already_connected = set()
    for row in rows:
        if row['aspect_name'] != 'Aversion' and _is_connected_sahl(row):
            already_connected.add(row['p1'])
            already_connected.add(row['p2'])
    # Candidates first, then ONE per striking planet: "whatever planet was
    # THE FIRST IN THAT LIGHT, it is connected with it" (20). An earlier
    # version flagged every planet inside the projected light, so a planet
    # at the end of Gemini with two planets early in Cancer came out
    # connected to both -- which 20 rules out in as many words, and which
    # also contradicts its own opening condition, since after the first
    # connection the striker is no longer "not connecting with anything."
    strikes = {}
    for row in rows:
        if row['aspect_name'] != 'Aversion' or row['signs_apart'] != 1:
            continue
        lon_a, lon_b = planetary_data[row['p1']]['longitude'], planetary_data[row['p2']]['longitude']
        # Order the pair so `earlier` is the one whose light would strike
        # forward across the boundary into the other's sign.
        if (lon_b - lon_a) % 360.0 < (lon_a - lon_b) % 360.0:
            earlier, later, gap = row['p1'], row['p2'], (lon_b - lon_a) % 360.0
        else:
            earlier, later, gap = row['p2'], row['p1'], (lon_a - lon_b) % 360.0
        if earlier in already_connected:
            continue
        if gap <= PLANETARY_ORBS.get(earlier, 7.0):
            strikes.setdefault(earlier, []).append((gap, later, row))

    for earlier, candidates in strikes.items():
        if earlier in already_connected:
            continue
        gap, later, row = min(candidates, key=lambda c: c[0])
        row['sahl_body_connection'] = True
        row['body_connection_from'] = earlier
        row['body_connection_to'] = later
        already_connected.add(earlier)
        already_connected.add(later)
        # These rows stay ASPECT_NAME 'Aversion', because 21 is explicit
        # that the two do not see each other -- not seeing and being
        # connected are both true here, which is the whole point of the
        # paragraph. But without kinetics the row was inert: every
        # downstream evaluator needs a motion and a direction, so the
        # connection was computed and then never used by anything.
        #
        # The gap closes when the later planet's motion falls behind the
        # earlier one's, and the applicant is whichever of the two is
        # closing it -- the same test the configured branch uses above.
        v_e = planetary_data[earlier]['speed_in_lon']
        v_l = planetary_data[later]['speed_in_lon']
        row['deviation'] = gap
        row['target'] = 0.0
        row['motion'] = 'Applying' if (v_l - v_e) < 0 else 'Separating'
        if v_e > 0 and v_l < v_e:
            row['applicant'], row['receiver'] = earlier, later
        elif v_l < 0:
            row['applicant'], row['receiver'] = later, earlier
        else:
            row['applicant'], row['receiver'] = earlier, later
        row['application_cause'] = 'out-of-sign body (20-21)'
        row['applicant_is_heavier'] = (
            WEIGHT_ORDER.index(row['applicant']) < WEIGHT_ORDER.index(row['receiver']))

    return rows

# --- Connection profiles --------------------------------------------------
# Sahl and Abu Ma'shar agree that looking is sign-to-sign and connecting is
# degree-to-degree (Sahl Ch.3, 23), but they part company at the sign
# boundary and on what activates a connection. Rather than blend them into
# one Boolean, each author's rule is written out separately and one is made
# active; every downstream doctrine reads _is_connected(), which dispatches.
CONNECTION_PROFILE = 'Sahl'

def _is_connected_sahl(row):
    """Sahl, The Introduction Ch.3, 6-21. The APPLYING planet's own light
    governs, so the test is asymmetric by design -- the orb belongs to the
    planet that acts, not to the pair.

    Separation windows: same-sign, until the light one has departed by
    "one-half of its body -- and that is its light" (10-11); cross-sign, a
    full degree (9). PLANETARY_ORBS already stores those half-body radii.

    Also admits the out-of-sign connection by body of 20-21, precomputed
    onto the row by _pairwise_configurations().

    A DISSENTING READING, recorded because it has real textual support and
    was raised in an independent audit of this file.

    For the asymmetric reading as implemented, three passages, of which the
    first is the one that actually defines the test:

        19: "if a planet looked at a planet [from another sign], and IT
        already struck WITH ITS OWN LIGHT upon its degree, then it is
        connected with it; and if it is NOT STRIKING WITH ITS OWN LIGHT,
        then it is moving toward the connection until it is connected."

        6: connection is the light planet "GOING STRAIGHTAWAY TO" the heavy
        one -- the action belongs to the mover.

        10: separation is measured by "the light one departs from the heavy
        one by one-half of ITS body."

    Against it, two lines in the list of the lights themselves:

        13: "if there was from a degree to 15 degrees between THE SUN and
        one of the planets, then HE has already shone HIS light, and HE is
        connected with [the planet]." In the standing weight order the Sun
        is HEAVIER than Venus, Mercury and the Moon, so here the heavier
        planet's light does the connecting.

        18, closing the list: "So by the extent of these lights, they are
        connected ONE TO THE OTHER."

    Two things were checked before settling this. First, whether 13 could
    be quarantined as a rule peculiar to the Sun, on the grounds that his
    15 degrees is the largest light and so the only one that could matter.
    IT CANNOT: over 5,405 applying configured pairs the two readings
    disagree on 288 (5.3%), and only 48% of those involve the Sun. The rest
    are Mercury to Jupiter, Venus to Saturn, Mars to Jupiter and the like --
    every case where the mover's light is smaller than the receiver's.

    Second, what Abu Ma'shar does with the same orb table (his Fig. 105 is
    13-17's numbers exactly). VII.4, 7: with Saturn and the Moon within 12
    degrees, "Saturn is in the power of the Moon's body WHILE THE MOON IS
    NOT YET IN THE POWER OF SATURN'S, until there is a little under 9
    degrees between them." That is explicitly directional and per-planet,
    and under a reciprocal reading it could not describe anything -- there
    would be no state in which one is inside the other's body and not the
    reverse. This file already implements that asymmetry as
    light_in_heavy_body / heavy_in_light_body.

    So 18's "one to the other" is read as naming the lights by which
    connection happens, not as saying either one suffices; and 13 is left
    standing as the genuine awkwardness it is. The asymmetric reading is
    kept because 19 is the paragraph that states the test. Switching would
    move about 5% of applying pairs."""
    if row['aspect_name'] == 'Aversion':
        return row.get('sahl_body_connection', False)
    remaining = abs(row['deviation'])

    # Each branch has its own owner, and each is named in its own
    # paragraph. This function previously used the NATURALLY LIGHTER
    # planet's orb for all three, while its own docstring said the applying
    # planet's -- true only while the two coincide, which is about 96% of
    # pairs. On the rest the file asserted the corrected doctrine and
    # implemented the superseded one.
    if row['motion'] == 'Applying':
        # 19: "if a planet looked at a planet, and IT already struck WITH
        # ITS OWN LIGHT upon its degree, then it is connected with it." The
        # actor is the planet approaching, which is the directed applicant
        # -- the naturally heavier one when it closes by retrogradation or
        # by overtaking a slower body.
        actor = row['applicant'] or row['light_name']
        return remaining <= PLANETARY_ORBS.get(actor, 7.0)
    if row['signs_apart'] == 0:
        # 10 names the owner explicitly for same-sign separation: "a planet
        # is not considered to be separated from a planet until THE LIGHT
        # ONE departs from the heavy one by one-half of ITS body." Sahl is
        # not contemplating a retrograde separation here, and the sentence
        # says "the light one", so the standing rank governs this branch.
        return remaining <= PLANETARY_ORBS.get(row['light_name'], 7.0)
    # 9 gives a flat degree across a sign boundary and names no owner:
    # "the planet does not cease to be counted as being connected until it
    # separates from the planet by a full degree."
    return remaining <= 1.0

def _is_connected_abu_mashar(row):
    """Gr. Intr. VII.4-5. Two flat activation
    distances rather than Sahl's per-planet lights:

    - Assembly is same-sign (VII.4, 3), and its power begins "if there were
      15 degrees and less between one of them and the other."
    - "The beginning of the power of the connection by aspect is when there
      are 12 degrees between the two planets" (VII.5, 27) -- one figure for
      every pair, since (per the note there) "aspect rays are not given
      specific orbs, because they are not bodies with a glow of power
      around them."

    And no out-of-sign connection of any kind: VII.4, 13 says planets in
    two different signs are "NOT said to be united ... because of the
    difference of their signs," and VII.5, 14 that few degrees across a
    boundary "is not counted as a connection by assembly, but they are both
    mixing their natures in a weak way." That weak mixing is reported
    separately (see row['mutual_body']), never as a connection."""
    if row['aspect_name'] == 'Aversion':
        return False
    # 34, recovered with p. 452: "in all of this, WHEN ONE OF THEM GOES
    # BEYOND ITS ASSOCIATE BY 1' OR LESS, THEN IT HAS ALREADY SEPARATED
    # FROM IT -- except that they will both be BLENDING IN NATURE."
    #
    # So for Abu Ma'shar a connection ends AT the exact degree: VII.5, 16
    # says the same of the assembly ("if the light one passed by the slow
    # one by one minute or by less than that, then it has already
    # SEPARATED"). "By 1' or less" is the amount that already counts as
    # separated, not a grace interval after exactness -- an earlier version
    # kept a pair connected for up to a minute past exact, inverting the
    # sentence it quoted (Astra F09). His activation distances below are
    # approach windows, not two-sided orbs. The residue he does allow is a
    # mixing of natures, which this file reports separately as the body
    # overlap, never as a connection. The 1e-9 degree is machine tolerance
    # at exactness, nothing doctrinal.
    if row['motion'] == 'Separating' and abs(row['deviation']) > 1e-9:
        return False
    if row['assembly']:
        return row['dist'] <= 15.0
    return abs(row['deviation']) <= 12.0

CONNECTION_PROFILES = {'Sahl': _is_connected_sahl, "Abu Ma'shar": _is_connected_abu_mashar}

def _is_connected(row):
    """Whether the pair is Connected under the doctrine currently in force."""
    return CONNECTION_PROFILES[CONNECTION_PROFILE](row)

def _rules_differ(row):
    """'Yes' where Sahl's and Abu Ma'shar's connection tests disagree on
    this pair -- the aspects table's way of making the rule switch visible."""
    return 'Yes' if _is_connected_sahl(row) != _is_connected_abu_mashar(row) else ''

def _is_separating_in_nature(row):
    """Abu Ma'shar's window for "separating from" a planet, which is NOT
    his connection window. VII.5, 34 ends a connection at 1' past exact, so
    under his profile _is_connected() is False for every separating pair --
    which left VII.6, 4 ("separating from a fortune and connecting with a
    fortune") and the separating/connecting form of VII.6, 57 unreachable:
    one hit in 1,680 sampled placements. His own text gives the window:
    after separating, "one of them will be 'in the nature' of its partner
    so long as it is in the sign in which they united" (VII.5, 17), and for
    rays, "the one of them will remain in the light of the other so long as
    the quick one is in that sign it is in" (VII.5, 35). A configured,
    separating pair at the chart moment is therefore still "separating
    from" until a sign changes, which is the same reading _sahl_enclosed()
    already takes for Sahl's Fig. 25."""
    return row['aspect_name'] != 'Aversion' and row['motion'] == 'Separating'

@contextmanager
def doctrine(author):
    """Pin the connection rule for the duration of one author's own table.

    The sidebar's Connection rule used to rewrite a module global that
    roughly thirty evaluators read, so a table headed "Sahl, The
    Introduction Ch.3, 24-27" could be running Abu Ma'shar's flat 12-degree
    orb -- the heading claiming one author while the arithmetic ran the
    other's. Under his profile Abu Ma'shar's 43 fired on 81% of placements
    against 8% under his own.

    An author's own evaluator now pins its own rule and restores whatever
    was in force. The sidebar selection still governs the genuinely dual
    tables -- the aspect grid, reception, blocking, cutting --
    which exist precisely to show both authors side by side, and which name
    the rule in force in their own headings.
    """
    global CONNECTION_PROFILE
    previous = CONNECTION_PROFILE
    CONNECTION_PROFILE = author
    try:
        yield
    finally:
        CONNECTION_PROFILE = previous

SAHL, ABU_MASHAR = 'Sahl', "Abu Ma'shar"

def _body_overlap_label(row):
    """How the two bodies' spheres of power overlap, reported on its own
    rather than folded into the Connected verdict (VII.4, 5-8)."""
    if row['mutual_body']:
        return 'Mutual'
    if row['heavy_in_light_body']:
        return f"{row['heavy_name']} in {row['light_name']}'s body"
    if row['light_in_heavy_body']:
        return f"{row['light_name']} in {row['heavy_name']}'s body"
    return '–'

def evaluate_ptolemaic_aspects(planetary_data):
    """Aspects, Aversions & Connections per Sahl (The Introduction Ch.2,
    50-60) and Abu Ma'shar (Gr. Intr. VII.3-4): Sextile/Square/
    Trine/Opposition are fully formed once whole-sign configured (50-56) --
    no degree orb gates them. Union (Assembly) is unconditional same-sign
    co-presence, graded Strong/Partial/Co-present by each planet's own orb
    (VII.4, 5-8). Connected (Ch.3) is layered on top as a per-pair
    refinement of how close an applying/separating pair currently is."""
    rows = _pairwise_configurations(planetary_data)
    aspects = []

    for row in rows:
        light_name, heavy_name = row['light_name'], row['heavy_name']

        if row['aspect_name'] == 'Aversion':
            # VII.4, 13-14: two planets in different (here, adjacent) signs
            # can still be "in the power of" each other's body by degree --
            # not an assembly (different signs), but a minor indication,
            # worth noting since it's the only case an Aversion pair can
            # still carry any classical significance at all.
            note = '\u2013'
            if row['signs_apart'] == 1 and (row['light_in_heavy_body'] or row['heavy_in_light_body']):
                note = 'In Power (out-of-sign)'
            if row['sahl_body_connection']:
                note = f"Body connection: {row['body_connection_from']} \u2192 {row['body_connection_to']} (Sahl 20-21)"
            # Same keys, same order, as the configured rows below: pandas
            # takes the first row's order, so a chart whose first pair was
            # an aversion used to get a different column order.
            aspects.append({
                'Light Planet': light_name,
                'Aspect': 'Aversion',
                'Heavy Planet': heavy_name,
                'Applying Planet': '\u2013',
                'Motion': '\u2013',
                'Orientation': '\u2013',
                'Exact Orb Dist': '\u2013',
                'Bodies': _body_overlap_label(row),
                'Strength': note,
                'Connected': 'Yes' if _is_connected(row) else 'No',
                'Rules differ': _rules_differ(row),
            })
            continue

        connected = _is_connected(row)

        if row['aspect_name'] == 'Conjunction':
            # Assembly strength (VII.4, 5-8): mutually strong if each
            # planet's own orb reaches the other; one-sided/weaker if only
            # the wider orb does; otherwise just nominal same-sign
            # co-presence. A shared bound (term) makes it more powerful still.
            if row['mutual_body']:
                strength = 'Strong'
            elif row['light_in_heavy_body'] or row['heavy_in_light_body']:
                strength = 'Partial'
            else:
                strength = 'Co-present'
            lon1 = planetary_data[row['p1']]['longitude']
            lon2 = planetary_data[row['p2']]['longitude']
            if get_essential_rulers(lon1)['term'] == get_essential_rulers(lon2)['term']:
                strength += ' (same bound)'
        else:
            # Looking-strength (VII.5, 4, Fig. 111): "the strongest thing
            # there is in its looking ... is the degree which is RELATED
            # MOST CLOSELY BY NUMBER to the degree of its own sign (such as
            # 60, 90, 120, and 180 degrees) ... and if the aspect was far
            # from these degrees, its aspect will be WEAKER."
            #
            # That is a continuum with no cutoffs anywhere in the chapter.
            # The thirds below are this app's own scale for scanning a
            # table quickly, and are marked as such in the cell rather than
            # presented as doctrine -- unlike the assembly grading above,
            # where the per-planet bodies and the shared bound are the
            # source's own (VII.4, 5-8). The measurement itself, the exact
            # distance from partile, is in its own column.
            combined_orb = PLANETARY_ORBS.get(row['p1'], 7.0) + PLANETARY_ORBS.get(row['p2'], 7.0)
            remaining = abs(row['deviation'])
            if remaining <= combined_orb / 3.0:
                strength = 'Strong (app scale)'
            elif remaining <= combined_orb:
                strength = 'Moderate (app scale)'
            else:
                strength = 'Weak (app scale)'

        aspects.append({
            'Light Planet': light_name,
            'Aspect': row['aspect_name'],
            'Heavy Planet': heavy_name,
            # Natural rank above, directed agency here. They coincide for
            # about 96% of configured pairs; the column exists for the rest,
            # where the naturally heavier planet is the one closing.
            'Applying Planet': (
                f"{row['applicant']} → {row['receiver']}"
                + (f" ({row['application_cause']})" if row['applicant_is_heavier'] else '')
            ) if row['applicant'] else '–',
            # VII.5, 24: with either planet retrograde the approach or
            # departure happens "by retrogradation" -- flagged rather than
            # allowed to quietly reassign the light/heavy roles.
            'Motion': row['motion'] + (' (by retrogradation)' if row['by_retrogradation'] else ''),
            'Orientation': row['orientation'],
            'Exact Orb Dist': _format_orb(abs(row['deviation'])),
            'Bodies': _body_overlap_label(row),
            'Strength': strength,
            'Connected': 'Yes' if connected else 'No',
            'Rules differ': _rules_differ(row),
        })

    return aspects

# --- Transfer & Collection of light -- Sahl, The Introduction Ch.3, 24-30 ----

def _sahl_body_row(row):
    """True for the out-of-sign body connection of Ch.3, 20-21.

    Such a row keeps aspect_name 'Aversion' -- 21 says outright that the
    two do not see each other -- while _is_connected_sahl() still reports
    it as connected. Every evaluator that gates on Aversion therefore
    dropped it before ever consulting the connection, so Sahl's own rule
    was computed and then thrown away by all of them. The evaluators that
    belong to Sahl's doctrine now admit it through this predicate; Abu
    Ma'shar's VII.6 table does not, because VII.5, 14 denies the case
    outright ("they mix their natures in a weak way", not a connection)."""
    return row.get('sahl_body_connection', False)

def evaluate_transfers_of_light(planetary_data):
    """Transfer of light: the core concept (a carrier separating from one
    planet and connecting to another) is Sahl's own (Ch.3, 24-27). The
    two-type breakdown below is Abu Ma'shar's addition (Great Introduction
    VII.5, 83-85, Fig. 126) -- Sahl does not distinguish a Type II.

    Type I: a "carrier" planet separates from one planet it is (or was) in
    aspect with, and connects with another, transferring the first
    planet's nature to the second. "Separates from" only requires the
    carrier to be the faster body, formerly-applying-now-past-exact
    (Motion == Separating) in a valid (non-Aversion) aspect -- not the
    tighter Connected threshold, which the book's own example (25-27)
    doesn't satisfy for Moon/Mercury (2 degrees past an exact Sextile,
    outside the 1-degree cross-sign Connected allowance) yet is still
    plainly described as "separating." "Connects to" does require
    Connected == True (24-25: "connecting with another... already
    connected with").

    Type II (84-85): a light planet connects with a slower one, which is
    itself already connecting onward with a third, even slower planet --
    the slow one shifts the light one's nature onto the third.

    The carrier must be the faster body in BOTH legs -- confirmed as a
    deliberate choice, not an oversight, after cross-checking a real chart
    (29 Oct 1990, 13:02 EST, Pontiac MI) against Janus's medieval module:
    Janus named the Sun as translating Mercury's light to Venus there, even
    though the Sun is slower than both (0.999 deg/day vs Mercury's 1.603
    and Venus's 1.254) -- the looser, more common modern/Lilly-style
    convention, where the carrier only needs its own angular gap to each
    to be independently shrinking/growing. Sahl's text ("the light, quick
    star... separates from the slow one, and connects with another")
    requires the SAME planet to be light/fast relative to both, which the
    Sun fails here on both counts -- so this implementation declines to
    name it a carrier, matching the sources this project is built on over
    the more permissive mainstream-software convention."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        # The carrier is the planet that MOVES between the other two -- "the
        # light planet separates from the heavy planet, and is connecting with
        # another" (Ch.3, 24). Keyed on the directed applicant rather than on
        # natural rank, so that a planet carrying light by retrogradation is
        # recognised as the carrier rather than as the thing carried.
        by_fast = {}
        for row in rows:
            if row['aspect_name'] == 'Aversion' and not _sahl_body_row(row):
                continue
            by_fast.setdefault(row['applicant'] or row['light_name'], []).append(row)

        def _other(r):
            return r['receiver'] or r['heavy_name']

        applying_connected_to = {
            fast: {_other(r) for r in fast_rows if r['motion'] == 'Applying' and _is_connected(r)}
            for fast, fast_rows in by_fast.items()
        }

        transfers = []
        for carrier, carrier_rows in by_fast.items():
            separating_from = [_other(r) for r in carrier_rows if r['motion'] == 'Separating']
            connecting_to = applying_connected_to.get(carrier, set())
            for a in separating_from:
                for b in connecting_to:
                    if a != b:
                        transfers.append({'Type': 'I', 'Carrier': carrier, 'Separates From': a, 'Connects To': b})

        for light, mediums in applying_connected_to.items():
            for medium in mediums:
                for onward in applying_connected_to.get(medium, set()):
                    if onward != light:
                        transfers.append({'Type': 'II', 'Carrier': light, 'Separates From': f"(via {medium})", 'Connects To': onward})

        return transfers

def evaluate_collections_of_light(planetary_data):
    """Collection of light (Sahl Ch.3, 28-30; Gr. Intr. VII.5, 86, Fig.
    127): two planets not connected to each other both connect with a
    single heavier planet, which collects their light. Reported per PAIR,
    matching Sahl's own pairwise framing (and how reference software such
    as Janus reports it) rather than bundled into one lumped group -- with
    more than two planets eligible under the same collector, each mutually-
    unconnected pair among them is its own valid collection fact. (An
    earlier version dropped a planet from the *entire* group the moment it
    was connected to any *other* member, which silently ate otherwise-valid
    pairs -- e.g. Sun and Venus both connecting to Jupiter alongside Mars
    would wrongly suppress "Jupiter collects Sun & Mars" just because Sun
    and Venus happened to also be connected to each other.)"""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        connected_lookup = {}
        applying_to = {}
        for row in rows:
            pair = frozenset({row['p1'], row['p2']})
            is_conn = (row['aspect_name'] != 'Aversion' or _sahl_body_row(row)) and _is_connected(row)
            connected_lookup[pair] = is_conn
            # Collection needs the light planets to be the ones APPLYING to the
            # collector, so the pair is keyed applicant -> receiver. 28's own
            # "heavier than they" is still enforced by natural rank below, so
            # both of the chapter's conditions are checked rather than one
            # standing in for the other.
            if is_conn and row['motion'] == 'Applying':
                applying_to.setdefault(row['applicant'] or row['light_name'], set()).add(
                    row['receiver'] or row['heavy_name'])

        collectors = {}
        for x, targets in applying_to.items():
            for z in targets:
                collectors.setdefault(z, set()).add(x)

        collections = []
        for z, lights in collectors.items():
            eligible = sorted(x for x in lights if WEIGHT_ORDER.index(z) < WEIGHT_ORDER.index(x))
            for x, y in combinations(eligible, 2):
                if not connected_lookup.get(frozenset({x, y}), False):
                    collections.append({'Collector': z, 'Collects': f'{x} & {y}'})
        return collections

def evaluate_sahl_banishment(planetary_data):
    """Sahl's "banished" planet (The Introduction Ch.3, 64): "the banished
    planet is the planet which NONE OF THE PLANETS CONNECTS TO." That is a
    statement about connections, not about signs: a planet can share a
    trine with every other body and still be banished if no one is inside
    a live connection with it, and it can hold an out-of-sign body
    connection (20-21) without being banished at all. Connection here is
    Sahl's own (6-21, _is_connected_sahl): a state of the pair, so a planet
    applying to another within its light is connected and neither side is
    banished.

    This is NOT Abu Ma'shar's wildness (VII.5, 79-82), which is whole-sign
    aversion to every planet -- see evaluate_abu_wildness(). An earlier
    version ran the aversion rule under both names, so Sahl's table showed
    his rule's absence as a fact about his text. Dykes' note on 64 calls
    Sahl's an early, less precise form of the later definition; the two are
    kept apart so the student can see where they disagree.

    Each row says how close the planet came, so an empty table and a
    near-miss look different."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        planets = [p for p in planetary_data.keys() if p != 'North Node']
        connected = set()
        for row in rows:
            if (row['aspect_name'] != 'Aversion' or _sahl_body_row(row)) and _is_connected(row):
                connected.update((row['p1'], row['p2']))
        results = []
        for p in planets:
            if p in connected:
                continue
            nearest = None
            for row in rows:
                if p not in (row['p1'], row['p2']) or row['aspect_name'] == 'Aversion':
                    continue
                if nearest is None or abs(row['deviation']) < abs(nearest['deviation']):
                    nearest = row
            if nearest is None:
                closest = 'in aversion to every planet'
            else:
                other = nearest['p2'] if nearest['p1'] == p else nearest['p1']
                # Name the test the near-miss fails: the applicant's own
                # light (19), half the light one's body in one sign (10),
                # or the full degree across signs (9).
                if nearest['motion'] == 'Applying':
                    actor = nearest['applicant'] or nearest['light_name']
                    why = f"outside {actor}'s light of {PLANETARY_ORBS.get(actor, 7.0):.0f}\u00b0 (19)"
                elif nearest['signs_apart'] == 0:
                    light = nearest['light_name']
                    why = f"past half of {light}'s body, {PLANETARY_ORBS.get(light, 7.0):.0f}\u00b0 (10)"
                else:
                    why = 'past the full degree of separation across signs (9)'
                closest = (f"{other}: {nearest['aspect_name'].lower()} by sign, {abs(nearest['deviation']):.1f}\u00b0 from exact "
                           f"and {nearest['motion'].lower()}, {why}")
            results.append({'Planet': p, 'Closest configured planet': closest})
        return results

def evaluate_abu_wildness(planetary_data):
    """Abu Ma'shar's wildness (Gr. Intr. VII.5, 79-82, Fig. 125):
    "if a planet is in a sign such that absolutely no planet looks at it,"
    which his own figure glosses as "in aversion to all other planets."
    Whole-sign, and independent of degree. Per 80-81, a wild planet still
    counts as connected with the lord of whatever bound it currently
    occupies, noted here rather than negating the flag.

    Distinct from Sahl's banishment (Ch.3, 64), which is about live
    connections and is in evaluate_sahl_banishment()."""
    rows = _pairwise_configurations(planetary_data)
    planets = [p for p in planetary_data.keys() if p != 'North Node']
    aversion_count = {p: 0 for p in planets}
    for row in rows:
        if row['aspect_name'] == 'Aversion':
            aversion_count[row['p1']] += 1
            aversion_count[row['p2']] += 1
    body_connected = {p for row in rows if row.get('sahl_body_connection')
                       for p in (row['p1'], row['p2'])}
    results = []
    for p in planets:
        if aversion_count[p] == len(planets) - 1:
            lon = planetary_data[p]['longitude']
            row = {'Planet': p, 'Bound Lord (residual connection)': get_essential_rulers(lon)['term']}
            # Whole-sign aversion to everything is not broken by an out-of-
            # sign body connection (Ch.3, 21: the two "will not see" each
            # other) -- but that connection means the planet is NOT banished
            # by Sahl's wording, and his own table will say so.
            if p in body_connected:
                row['Note'] = ("Wild by whole-sign aversion; holds an out-of-sign body connection "
                                "(Sahl Ch.3, 20-21), so it is not banished in Sahl's table")
            results.append(row)
    return results

# --- Natural connections (Gr. Intr. VII.5, 53-77) ----------------------
# "Another type of connection and separation [even] without the planets'
# looking at each other is said to be a 'natural connection and
# separation'" (53), "and it is of two types" (55). Each is a family of
# SIGN PAIRS whose degrees correspond, so that a planet in one sign "is
# in the nature of the degree of" a planet in the other, and connects or
# separates with it as the degrees meet or part. The corresponding degree
# is the complement within the sign: "when a planet is in the first
# degree of Aries, then it is in the nature of a planet which is at the
# last degree of Pisces" (57); "the planet which is in 12° of Gemini is
# in the nature of the degree of the planet which is in 18° of
# Capricorn" (62).
#
# Both lists are exactly as Abu Ma'shar enumerates them here. The
# equal-daylight family is the antiscia (note 162), which as a complete
# scheme also pairs Aquarius with Scorpio -- but 67-75 does not say so,
# and the notes on 76-77 record two further pairs he "omits". None of
# those is added: the standing rule of this file is the text in hand over
# what the family implies, and the coverage note names them as unbuilt.
EQUAL_ASCENSION_PAIRS = {                                  # 56
    frozenset({'Aries', 'Pisces'}), frozenset({'Taurus', 'Aquarius'}),
    frozenset({'Gemini', 'Capricorn'}), frozenset({'Cancer', 'Sagittarius'}),
    frozenset({'Leo', 'Scorpio'}), frozenset({'Virgo', 'Libra'}),
}
EQUAL_DAYLIGHT_PAIRS = {                                   # 67-75
    frozenset({'Gemini', 'Cancer'}), frozenset({'Taurus', 'Leo'}),
    frozenset({'Aries', 'Virgo'}), frozenset({'Libra', 'Pisces'}),
    frozenset({'Sagittarius', 'Capricorn'}),
}
# 76-77 name four of each family's pairs as bridging an ordinary aversion:
# "the connection of the planet which is in Gemini with the degree of the
# planet which is in Capricorn ... is called a 'natural connection by
# opposition'" (76); "the one in Gemini with the one in Cancer ... is
# called the 'natural connection by sextile'" (77).
NATURAL_OPPOSITION_PAIRS = {
    frozenset({'Gemini', 'Capricorn'}), frozenset({'Sagittarius', 'Cancer'}),
    frozenset({'Aries', 'Virgo'}), frozenset({'Libra', 'Pisces'}),
}
NATURAL_SEXTILE_PAIRS = {
    frozenset({'Gemini', 'Cancer'}), frozenset({'Virgo', 'Libra'}),
    frozenset({'Sagittarius', 'Capricorn'}), frozenset({'Pisces', 'Aries'}),
}

def _natural_family(sign_a, sign_b):
    """The natural-connection family of a sign pair, or None."""
    pair = frozenset({sign_a, sign_b})
    if pair in EQUAL_ASCENSION_PAIRS:
        return 'Equal ascensions (56-66)'
    if pair in EQUAL_DAYLIGHT_PAIRS:
        return 'Equal daylight (67-75)'
    return None

def _counterpart_degree(lon):
    """The degree of the partner sign that corresponds to `lon`'s degree in
    its own: the complement within the sign (57, 62). 0.0 pairs with 30.0,
    the sign's last degree at its far edge."""
    return 30.0 - (lon % 30.0)

def evaluate_abu_natural_connections(planetary_data):
    """Abu Ma'shar's natural connections (VII.5, 53-77) -- a relation of its
    own, neither a Ptolemaic aspect nor a dignity. Every pair standing in
    one of the enumerated sign pairs is reported, with how far the second
    planet stands from the first's counterpart degree, and whether the
    two are closing or parting.

    Motion follows 62 -- "so when it passes beyond 12° of Gemini, then it
    has separated from it and comes to be in the nature of the planet
    which is in less than 18° of Capricorn" -- so the counterpart degree
    moves AGAINST its planet's own motion, and the gap between the second
    planet and it closes at the SUM of the two speeds. Two direct planets
    are therefore applying only while the second is still short of the
    counterpart, and separating once past it; a retrograde planet reverses
    its own contribution.

    Abu Ma'shar gives no orb here: a planet in Aries is always in the
    nature of SOME degree of Pisces (57-59), and the connection completes
    where the degrees coincide. The row reports the distance and the
    student judges; nothing is suppressed by an invented window. The
    ordinary whole-sign relation is repeated on the row precisely so that
    an Aries/Pisces pair reads as both in natural connection and in
    aversion: 53 says "without the planets' looking at each other", and no
    out-of-sign aspect is created anywhere from this."""
    rows = _pairwise_configurations(planetary_data)
    results = []
    for row in rows:
        a, b = row['p1'], row['p2']
        lon_a, lon_b = planetary_data[a]['longitude'], planetary_data[b]['longitude']
        sign_a, sign_b = get_zodiac_sign(lon_a), get_zodiac_sign(lon_b)
        if sign_a == sign_b:
            continue
        family = _natural_family(sign_a, sign_b)
        if family is None:
            continue
        counterpart = SIGN_ORDER.index(sign_b) * 30.0 + _counterpart_degree(lon_a)
        deviation = ((lon_b - counterpart + 180.0) % 360.0) - 180.0
        rate = planetary_data[a]['speed_in_lon'] + planetary_data[b]['speed_in_lon']
        if abs(deviation) <= 1.0 / 60.0:
            motion = 'Exact'
        elif deviation * rate < 0:
            motion = 'Applying'
        else:
            motion = 'Separating'
        pair = frozenset({sign_a, sign_b})
        affinity = ('natural opposition (76)' if pair in NATURAL_OPPOSITION_PAIRS
                    else 'natural sextile (77)' if pair in NATURAL_SEXTILE_PAIRS else '')
        results.append({
            'Pair': f'{a} & {b}', 'Family': family,
            'Degrees': (f"{a} {lon_a % 30:.1f}\u00b0 {sign_a[:3]} \u2194 {_counterpart_degree(lon_a):.1f}\u00b0 {sign_b[:3]}; "
                        f"{b} at {lon_b % 30:.1f}\u00b0 {sign_b[:3]}"),
            'From exact': f'{abs(deviation):.1f}\u00b0', 'Motion': motion,
            'Affinity (76-77)': affinity,
            'Ordinary aspect': row['aspect_name'],
            'Standing': 'direct: sign pairs and degree rule as enumerated',
        })
    return results

def evaluate_reflections_of_light(planetary_data, ascendant_lon):
    """Reflection of light (VII.5, 87-89, Figs. 128-129): the Collection/
    Transfer patterns specifically for two planets that are themselves in
    Aversion to each other. Type II (89) is Transfer for an Aversion pair
    (footnote 170: "this kind of reflection is a transfer of light, but for
    two planets in aversion"). Type I (87-88) is Collection for an Aversion
    pair, with the collector "reflecting" the light onward via its own
    further aspects -- for a natal (non-topical) chart there's no "sought
    matter" to reflect toward, so this reports which Whole-Sign House(s)
    the collector's own further aspects reach, for the reader to interpret."""
    with doctrine(ABU_MASHAR):
        rows = _pairwise_configurations(planetary_data)
        aversion_pairs = {frozenset({r['p1'], r['p2']}) for r in rows if r['aspect_name'] == 'Aversion'}

        reflections = []
        for t in evaluate_transfers_of_light(planetary_data):
            if t['Type'] == 'I' and frozenset({t['Separates From'], t['Connects To']}) in aversion_pairs:
                reflections.append({
                    'Reflection Type': 'II (Transfer)',
                    'Detail': f"{t['Carrier']} reflects between {t['Separates From']} and {t['Connects To']}",
                })

        for c in evaluate_collections_of_light(planetary_data):
            collected = c['Collects'].split(' & ')
            if len(collected) == 2 and frozenset(collected) in aversion_pairs:
                collector = c['Collector']
                # The places the collector's OWN RAYS fall into. An earlier
                # version listed the whole-sign houses OCCUPIED BY OTHER
                # PLANETS that happened to aspect the collector, which is a
                # different set entirely -- it named where the collector is
                # looked at FROM, not where it looks TO, and it went silent
                # whenever no third planet happened to be configured to it.
                #
                # VII.5, 3: a planet "looks at every degree of the sign as well
                # as everything which is in it," so the reach is the seven
                # signs its rays fall in, independent of what occupies them.
                collector_lon = planetary_data[collector]['longitude']
                reached_houses = sorted({
                    get_wsh_house(d, ascendant_lon)
                    for d in _ray_degrees(collector_lon)[1:]   # skip its own body
                })
                detail = (f"{collector} collects {c['Collects']}, "
                           f"and its own rays reach houses {reached_houses}")
                reflections.append({'Reflection Type': 'I (Collection)', 'Detail': detail})
        return reflections

# How far outside the active author's own ray window Blocking Type II may
# still fire. Sahl's Fig. 14 / Abu Ma'shar's Fig. 131 needs one degree.
WORKED_FIGURE_TOLERANCE = 1.0

def _ray_activation_distance(row):
    """The active author's own approach window for this pair's ray: the
    applicant's light for Sahl (Ch.3, 13-19), a flat 12 degrees for Abu
    Ma'shar (VII.5, 27). The figure that connection would be measured
    against, before any tolerance is added."""
    if CONNECTION_PROFILE == SAHL:
        return PLANETARY_ORBS.get(row['applicant'] or row['light_name'], 7.0)
    return 12.0

def evaluate_blocking(planetary_data):
    """Blocking. Type I is Sahl's "Intervention" (The Introduction Ch.3,
    35-37), reused by Abu Ma'shar as his own Blocking Type I (Great
    Introduction VII.5, 91-92, footnote 172): three planets share a sign;
    the heaviest sits at the highest degree, and whichever of the other two
    sits at the middle degree blocks the lightest from reaching the
    heaviest until it passes by. Type II is Sahl's "Nullification" (The
    Introduction Ch.3, 38-48), reused by Abu Ma'shar as Blocking Type II
    (VII.5, 93-94, footnote 174): a light planet connects by aspect from
    another sign with a heavy one, while a third, lighter planet co-present
    with that heavy one is joining it by body and gets there first.

    Both types are reproduced against the authors' own worked figures --
    Fig. 13 (Moon 8, Mars 10, Saturn 12 Gemini: Mars intervenes) and
    Fig. 14 (Moon 10 Scorpio, Mars 15 and Saturn 23 Taurus: Mars cuts the
    Moon's aspect).

    An earlier version stated Type II as "a body connection categorically
    outranks an aspect connection regardless of relative degree closeness,"
    and so accepted ANY third planet sharing the heavy planet's sign, with
    no application and no exception. That conflated two different passages.
    Sahl 44-48 IS a flat precedence rule, but its subject is one planet
    holding both a union and an aspect of its own (45-48: the Moon uniting
    with Mars while aspecting Venus). The third-party blocking of 38-42 and
    VII.5, 93-94 is conditional, and both authors give it an escape: "if it
    goes beyond that, its connection is valid" (40), and "when the degrees
    of the one looking are closer to the connection than the degrees of the
    one joining by body, the connection belongs to the one looking" (94).
    Across ~3,600 sampled charts the correction removes 76% of reported
    blockings, nearly all of them third planets that were merely co-present
    and in fact SEPARATING from the heavy planet.

    Sahl's third blocking type, "Cutting the Light" (Ch.3, 31-34), is
    modeled as Type III of evaluate_cutting_the_light() rather than here,
    confirmed against Fig. 12's own numbers -- see that docstring.

    Note these are configurations, not verdicts about a matter: both
    authors are describing horary charts in which a querent and a quesited
    have already been identified. With no topical significators nominated,
    a row here says a blocking pattern exists between those three planets,
    not that any particular sought thing is obstructed."""
    rows = _pairwise_configurations(planetary_data)
    planets = [p for p in planetary_data.keys() if p != 'North Node']
    row_for = {frozenset({r['p1'], r['p2']}): r for r in rows}
    speed = {p: planetary_data[p]['speed_in_lon'] for p in planets}
    blocks = []

    def applying(a, b):
        """a is applying TO b, and the pair is actually connected under the
        active author's rule.

        Both halves were missing. Motion alone let a pair "block" while
        outside every activation window either author gives -- 12 or 15
        degrees for Abu Ma'shar, the actor's own light for Sahl -- and
        without checking direction, b applying to a counted as a applying
        to b."""
        r = row_for.get(frozenset({a, b}))
        if r is None or r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
            return False
        if (r['applicant'] or r['light_name']) != a:
            return False
        return _is_connected(r)

    # --- Type I: Intervention (Sahl 35-37, Fig. 13; VII.5, 91-92) -------
    # "Three planets are in a single sign, IN DIFFERENT DEGREES, and the
    # heavy one has more degrees than [the other] two, so that the middle
    # one blocks the one with the fewest degrees from connecting with the
    # heavy one, UNTIL IT PASSES BY IT."
    by_sign = {}
    for p in planets:
        by_sign.setdefault(int(planetary_data[p]['longitude'] // 30), []).append(p)
    for group in by_sign.values():
        if len(group) < 3:
            continue
        for combo in combinations(group, 3):
            trio = sorted(combo, key=lambda p: planetary_data[p]['longitude'] % 30)
            blocked, blocker, target = trio
            if len({round(planetary_data[p]['longitude'] % 30, 6) for p in trio}) < 3:
                continue  # "in different degrees"
            if target != min(combo, key=WEIGHT_ORDER.index):
                continue  # the heavy one must be the one holding the most degrees
            # "Until it passes by it" only describes forward motion, and
            # VII.5, 10 frames the connection by assembly as belonging to
            # planets "direct in motion".
            if speed[blocked] <= 0 or speed[blocker] <= 0:
                continue
            # There is nothing to block unless the light planet is actually
            # on its way to the heavy one ...
            if not applying(blocked, target):
                continue
            # ... and nothing does the blocking unless the MIDDLE body is
            # itself joining the target. 35 has the middle planet standing
            # between the other two on its own way to the heavy one, so
            # that the light one cannot reach past it "UNTIL IT PASSES BY
            # IT". A middle planet already separating from the target is
            # moving out of the way, not standing in it -- this was
            # unchecked, so a separating body still emitted a block.
            if not applying(blocker, target):
                continue
            blocks.append({'Type': 'I (Intervention)', 'Blocked': blocked,
                            'Blocked By': blocker, 'From Reaching': target})

    # --- Type II: Nullification (Sahl 38-48, Fig. 14; VII.5, 93-94) -----
    # "Two planets are in a single sign, and the light one is connecting
    # with the heavy one, and another, [third] planet connects with that
    # heavy one BY LOOKING, but by degree it is less than the light one
    # which is uniting: thus the one with it in its sign blocks the one
    # looking." An earlier version treated ANY third planet co-present in
    # the heavy planet's sign as a blocker -- with no application, no
    # degree condition and no exception -- which is the bulk of the
    # over-reporting.
    #
    # VII.5, 94 supplies the exception: "when the degrees of the one
    # looking are closer to the connection than the degrees of the one
    # joining by body, the connection belongs to the one looking, because
    # it connects with it before the one joining with it" -- Sahl's own 40
    # says the same ("if it goes beyond that, its connection is valid").
    # The test is the REMAINING ARC IN DEGREES, not time-to-perfection,
    # even though 94 phrases the reason temporally. Sahl's worked Fig. 14
    # settles it: Moon 10 Scorpio, Mars 15 Taurus, Saturn 23 Taurus, and
    # his verdict is that Mars cuts the Moon's aspect. Mars has 8 degrees
    # left to Saturn against the Moon's 23, so by arc Mars wins -- but the
    # Moon covers her 23 degrees in under two days against Mars's fifteen,
    # so by elapsed time she would perfect first and the verdict would
    # invert. Arc it is.
    for row in rows:
        if row['aspect_name'] in ('Aversion', 'Conjunction') or row['motion'] != 'Applying':
            continue
        # The planet being blocked is the one APPLYING by ray, and the
        # target is what it applies to -- directed, not standing rank.
        looking, heavy = row['applicant'] or row['light_name'], row['receiver'] or row['heavy_name']
        remaining_ray = abs(row['deviation'])
        # The ray leg is NOT held to the live-connection test, and the
        # reason is the worked figure itself: Fig. 14 puts the Moon 13
        # degrees from her opposition to Saturn, one degree outside her
        # own 12-degree light (Ch.3, 13-17), and both authors still call
        # it a connection about to be cut. That is an inconsistency in the
        # source, not a bug, and it is honoured by exactly the one degree
        # it needs. An earlier version had no bound at all, so a ray 29
        # degrees from exact -- no connection by anyone's measure -- still
        # produced a nullification.
        if _is_connected(row):
            standing = 'live connection'
        elif remaining_ray <= _ray_activation_distance(row) + WORKED_FIGURE_TOLERANCE:
            standing = (f'worked-figure tolerance: ray {remaining_ray:.1f}\u00b0 from exact, within '
                        f'{WORKED_FIGURE_TOLERANCE:.0f}\u00b0 of the light (Fig. 14 sits 13\u00b0 against the Moon\'s 12\u00b0)')
        else:
            continue
        heavy_lon = planetary_data[heavy]['longitude']
        heavy_sign = int(heavy_lon // 30)
        for uniting in planets:
            if uniting in (looking, heavy):
                continue
            if int(planetary_data[uniting]['longitude'] // 30) != heavy_sign:
                continue
            if WEIGHT_ORDER.index(uniting) <= WEIGHT_ORDER.index(heavy):
                continue  # it is "the LIGHT one which is uniting" with the heavy one
            if not applying(uniting, heavy):
                continue  # co-presence alone is not a joining
            remaining_body = abs(heavy_lon - planetary_data[uniting]['longitude'])
            if remaining_body > remaining_ray:
                continue  # 40 / 94: the ray arrives first, so the connection is its own
            blocks.append({'Type': 'II (Nullification)', 'Blocked': looking,
                            'Blocked By': uniting, 'From Reaching': heavy, 'Standing': standing})
    return blocks

def evaluate_handing_over(planetary_data, sect):
    """Handing Over (Sahl, The Introduction Ch.3, 70-76): three grades of
    one phenomenon, not independent subtypes. Management (76, "in signs other
    than these two, she only hands over management"; fn. 90: "any application
    or connection hands over management") is the unconditional
    baseline for every Connected pair. Power (70-72) is additionally
    granted when the applying planet is itself in its own house,
    exaltation, or triplicity at the time of connecting. Nature (73-74,
    confirmed by the worked example's own parenthesis at 74 -- "that is, in
    reception") is additionally granted when the applying planet is
    connecting with the dispositor -- by house or exaltation only,
    matching Reception's own "perfect" scope (49-50), not triplicity -- of
    its own position. (Abu Ma'shar's own "Two Natures" subtype, Great
    Introduction VII.5, 97-100, doesn't appear anywhere in Sahl and isn't
    modeled here.)

    All three grades run in ONE direction only: "the one handing over" is
    always the light/applying planet, "the accepting one" is always the
    heavy planet it connects with (67) -- Power and Nature are graded
    elaborations of that same fixed direction, not independently
    reversible. An earlier version of this function also let the heavy
    (slow) side "hand power/nature back" to the applicant whenever ITS OWN
    position happened to qualify -- an addition with no basis in the
    text, caught during a source-fidelity review and removed."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
        results = []

        for r in rows:
            if (r['aspect_name'] == 'Aversion' and not _sahl_body_row(r)) or not _is_connected(r):
                continue
            # Handing over is directed: 67 makes the ONE HANDING OVER the planet
            # that connects, and 76 the one that accepts. This read natural rank
            # while the docstring described the applicant.
            fast, slow = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            fast_lon = planetary_data[fast]['longitude']
            fast_rulers = get_essential_rulers(fast_lon)
            fast_power_claims = {fast_rulers['domicile'], fast_rulers['exaltation'], fast_rulers[triplicity_key]} - {'-'}
            fast_own_dispositors = {fast_rulers['domicile'], fast_rulers['exaltation']} - {'-'}

            results.append({'Type': 'Management', 'Planet': fast, 'Hands Over To': slow})

            # 70 names "house, exaltation, or triplicity"; 75-76 then restrict
            # the Moon: "if the Moon was in Taurus or Cancer, she hands over
            # power and management. And in signs other than these two, she
            # only hands over management." The narrower, later statement
            # governs her; the other six keep 70.
            moon_power_ok = (fast != 'Moon') or (fast in fast_own_dispositors)
            if fast in fast_power_claims and moon_power_ok:
                results.append({'Type': 'Power', 'Planet': fast, 'Hands Over To': slow})

            if slow in fast_own_dispositors:
                results.append({'Type': 'Nature', 'Planet': fast, 'Hands Over To': slow})

        return results

# --- Forward simulation -- Gr. Intr. VII.5's motion-dependent
# conditions (Emptiness of Course, Revoking, Resistance, Escape, Returning's
# retrograde case, Recompense) describe what happens as the chart moves
# forward, not the birth moment alone. This steps the ephemeris ahead and
# records each planet's sign-exit and station days, shared by every
# detector below rather than recomputed per-condition.

def _bisect_crossing(test_fn, day_lo, day_hi, tol=1e-4, max_iter=60):
    """Assumes exactly one transition of test_fn's boolean value inside
    [day_lo, day_hi]; returns the midpoint of the final bracket.

    tol is 1e-4 day (about nine seconds), the same order as the contact
    root-finder's, because an ingress found here is used as a HARD CUTOFF
    against contacts found there: at the old 0.02-day bracket (29 minutes)
    a sextile perfected three minutes before the Moon left her sign was
    placed after the recorded exit and lost (Astra F06; PN IV II.22, 1-4
    counts only what she connects with "so long as she is in her sign")."""
    val_lo = test_fn(day_lo)
    for _ in range(max_iter):
        if day_hi - day_lo < tol:
            break
        mid = (day_lo + day_hi) / 2.0
        if test_fn(mid) == val_lo:
            day_lo = mid
        else:
            day_hi = mid
    return (day_lo + day_hi) / 2.0

@st.cache_data(max_entries=32, show_spinner=False)
def _simulate_forward_pure(planet_names, jd, horizon_days, step_days):
    """The ephemeris half of _simulate_forward(), keyed only on values."""
    return _simulate_forward_uncached({p: None for p in planet_names}, jd,
                                       horizon_days, step_days)

def _simulate_forward(planetary_data, jd, horizon_days=200, step_days=1.0):
    """Forward simulation, with the ephemeris work cached.

    _lon_at() memoises into the dict this returns, so the cached value is
    copied and given a fresh memo rather than handed out directly."""
    names = tuple(p for p in planetary_data if p != 'North Node')
    base = _simulate_forward_pure(names, jd, horizon_days, step_days)
    return {'series': base['series'], 'events': base['events'],
            'jd': base['jd'], 'horizon_days': base['horizon_days']}

def _simulate_forward_uncached(planetary_data, jd, horizon_days=200, step_days=1.0):
    """Day-step swe.calc_ut for all 7 classical planets from jd out to
    horizon_days, returning per-planet daily (day, longitude, speed) series
    plus interpolated sign-exit and station event days. A near-term cutoff,
    not an indefinite search -- a condition not found within the horizon is
    reported as "none found," not chased further."""
    planets = [p for p in planetary_data.keys() if p != 'North Node']
    n_steps = int(horizon_days / step_days) + 1
    series = {p: {'day': [], 'lon': [], 'speed': []} for p in planets}
    for i in range(n_steps):
        day = i * step_days
        for p in planets:
            res, _ = swe.calc_ut(jd + day, PLANET_SWE_IDS[p])
            series[p]['day'].append(day)
            series[p]['lon'].append(res[0])
            series[p]['speed'].append(res[3])

    events = {p: {'sign_exits': [], 'stations': []} for p in planets}
    for p in planets:
        days, lons, speeds = series[p]['day'], series[p]['lon'], series[p]['speed']
        pid = PLANET_SWE_IDS[p]
        for i in range(len(days) - 1):
            # A station first: the longitude is monotonic on each side of
            # it and NOT across the whole step, so a planet can leave a sign
            # and come back inside one sample (Mercury stationing just past
            # 0 of the next sign) and show the same sign at both ends. The
            # step is split at the station and each monotonic piece searched
            # for its own crossing (Astra F07; Gr. Intr. VII.5, 117-119 and
            # Aphorism 48, 99-102 order stations and sign changes).
            pieces = [(days[i], lons[i]), (days[i + 1], lons[i + 1])]
            if (speeds[i] > 0) != (speeds[i + 1] > 0):
                kind = 'first' if speeds[i] > 0 else 'second'
                def _speed_test(day, _pid=pid, _positive=(speeds[i] > 0)):
                    res, _ = swe.calc_ut(jd + day, _pid)
                    return (res[3] > 0) == _positive
                station_day = _bisect_crossing(_speed_test, days[i], days[i + 1])
                events[p]['stations'].append((station_day, kind))
                station_lon = swe.calc_ut(jd + station_day, pid)[0][0]
                pieces.insert(1, (station_day, station_lon))
            for (d0, l0), (d1, l1) in zip(pieces, pieces[1:]):
                sign0 = int(l0 // 30)
                if int(l1 // 30) != sign0:
                    def _sign_test(day, _pid=pid, _sign0=sign0):
                        res, _ = swe.calc_ut(jd + day, _pid)
                        return int(res[0] // 30) == _sign0
                    events[p]['sign_exits'].append(_bisect_crossing(_sign_test, d0, d1))

    return {'series': series, 'events': events, 'jd': jd, 'horizon_days': horizon_days}

def _wrap180(degrees):
    """Fold an angle into (-180, 180]."""
    return ((degrees + 180.0) % 360.0) - 180.0

def _lon_at(sim, planet, day):
    """A planet's longitude at an arbitrary day inside the horizon, read
    straight from the ephemeris (memoized per simulation).

    Replaces an interpolation over the daily samples, which ran the
    straight line THROUGH the 0/360 seam: a planet at 359 deg followed by
    one at 1 deg interpolated backwards across 180 deg, so any event timed
    between those two samples was placed half a zodiac away."""
    cache = sim.setdefault('_lon_cache', {})
    key = (planet, round(day, 6))
    if key not in cache:
        res, _ = swe.calc_ut(sim['jd'] + day, PLANET_SWE_IDS[planet])
        cache[key] = res[0]
    return cache[key]

def _bisect_zero(fn, day_lo, day_hi, tol=1e-3, max_iter=60):
    """Bracketed root-find for a continuous fn known to change sign across
    [day_lo, day_hi]."""
    f_lo = fn(day_lo)
    for _ in range(max_iter):
        if day_hi - day_lo < tol:
            break
        mid = (day_lo + day_hi) / 2.0
        f_mid = fn(mid)
        if (f_mid < 0.0) == (f_lo < 0.0):
            day_lo, f_lo = mid, f_mid
        else:
            day_hi = mid
    return (day_lo + day_hi) / 2.0

def _configuration_target_at(sim, p1, p2, day):
    """The whole-sign aspect angle the pair is entitled to on a given day,
    or None if they are in aversion then."""
    s1 = int(_lon_at(sim, p1, day) // 30)
    s2 = int(_lon_at(sim, p2, day) // 30)
    raw_apart = abs(s1 - s2)
    apart = min(raw_apart, 12 - raw_apart)
    entry = ASPECT_BY_SIGN_COUNT.get(apart)
    return None if entry is None else entry[1]

def _sign_ingress_day(sim, planet, sign_idx, after_day=0.0, before_day=None):
    """Day the planet ENTERS the given sign, or None inside the horizon.

    sim['events'][p]['sign_exits'] records the moments a planet leaves the
    sign it was in; the sign it lands in is read just past the crossing."""
    for day in sim['events'][planet]['sign_exits']:
        if day <= after_day:
            continue
        if before_day is not None and day > before_day:
            break
        if int(_lon_at(sim, planet, day + 1e-3) // 30) == sign_idx % 12:
            return day
    return None

def _body_union_day(sim, a, b, after_day=0.0, before_day=None):
    """Day two planets conjoin BY DEGREE -- the "uniting" the sources treat
    as a distinct, stronger event than a ray perfecting (Sahl Ch.3, 44;
    VII.5, 121 and its note, which reads the verb as "conjoins" by degree
    "rather than the looser 'assembling'")."""
    return _perfection_day(sim, a, b, 0.0, after_day=after_day, before_day=before_day)

def _perfection_day(sim, p1, p2, target, before_day=None, after_day=None):
    """First day inside the horizon on which p1 and p2 actually perfect the
    given aspect, or None.

    Three things the previous implementation got wrong:

    (1) It tested `min_angular_distance - target`, which is confined to
    [0, 180]. For a conjunction (target 0) that residual is never negative
    and for an opposition (target 180) never positive, so NEITHER could
    ever cross zero -- perfection was silently undetectable for both, and
    callers that treat "no perfection found" as a positive result (notably
    Revoking) fired on every such pair. Here the pair's signed relative
    longitude is compared against +target and -target, each folded into
    (-180, 180], so every aspect including those two crosses zero cleanly.

    (2) It returned the sample day at which the sign flipped rather than
    the root, giving up to a full day of error; now bisected against the
    ephemeris directly.

    (3) It kept applying the natal aspect angle no matter how the chart had
    moved. A pair 3 signs apart at birth may be 4 apart by the time the
    90-degree hit arrives, and Abu Ma'shar permits no out-of-sign aspect
    (VII.5, 14: few degrees across a sign boundary is not a connection but
    a weak "mixing of natures"). The whole-sign configuration is now
    revalidated AT the moment of perfection, and a hit that no longer
    matches is discarded and the scan continues."""
    days = sim['series'][p1]['day']
    lons1, lons2 = sim['series'][p1]['lon'], sim['series'][p2]['lon']

    def residual(day, offset):
        return _wrap180(_lon_at(sim, p1, day) - _lon_at(sim, p2, day) - offset)

    for i in range(len(days) - 1):
        if before_day is not None and days[i] > before_day:
            break
        if after_day is not None and days[i + 1] < after_day:
            continue
        for offset in (target, -target):
            prev = _wrap180(lons1[i] - lons2[i] - offset)
            cur = _wrap180(lons1[i + 1] - lons2[i + 1] - offset)
            # A wrapped residual also "changes sign" when it rolls over the
            # +/-180 seam; a genuine root moves by far less than half a turn
            # in one step, so that guard rejects the seam artifact.
            if (prev < 0.0) == (cur < 0.0) or abs(cur - prev) >= 180.0:
                continue
            day = _bisect_zero(lambda d, _o=offset: residual(d, _o), days[i], days[i + 1])
            if before_day is not None and day > before_day:
                continue
            if after_day is not None and day < after_day:
                continue
            actual = _configuration_target_at(sim, p1, p2, day)
            if actual is not None and abs(actual - target) < 1e-9:
                return day
    return None

def evaluate_returning(planetary_data, accidental, ascendant_lon):
    """Returning (Sahl, The Introduction Ch.3, 65-69, Figs. 21-22): two
    distinct manners, not grades of one trigger, both present-tense --
    Sahl gives no forward-looking refinement for either.

    Manner I (65): a planet connects with a retrograde planet, or one
    under the rays -- either condition alone triggers it. "It returns to
    it what it accepted from it, and has already corrupted its
    management, and indicates that the question does not have a beginning
    nor end."

    Manner II (66-69): the light (handing-over, faster) planet is in a
    stake (angular house), connecting with a heavy (accepting) planet
    that is falling (cadent) -- "the sought thing has a beginning...
    but does not have an end because the accepting one is falling." NOTE:
    Sahl's own worked example (68: Moon in the 6th, Mars in the 12th --
    both cadent) doesn't actually satisfy this rule as stated (neither
    planet is angular); Dykes' own footnote there flags the same
    inconsistency in the source text, not a misreading here. Implemented
    per the rule as stated in 66-67, not the example."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        results = []
        for r in rows:
            if (r['aspect_name'] == 'Aversion' and not _sahl_body_row(r)) or not _is_connected(r) or r['motion'] != 'Applying':
                continue
            # Returning is directed: 65 has "a planet ... CONNECTING WITH a
            # retrograde planet or one under the rays," and 67 names the mover
            # as the one handing over. So the subject is the applicant and the
            # planet that returns the management is the one being approached --
            # which for a retrograde connection is not the naturally heavier of
            # the two. (Manner I would otherwise report the retrograde planet
            # as returning management to itself whenever it was the applicant.)
            fast, slow = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            acc_slow = accidental[slow]

            if acc_slow['Retrograde'] or acc_slow['Combust'] or acc_slow['UnderBeams']:
                results.append({'Manner': 'I (65)', 'Planet': fast, 'Returned By': slow})

            fast_house = get_wsh_house(planetary_data[fast]['longitude'], ascendant_lon)
            slow_house = get_wsh_house(planetary_data[slow]['longitude'], ascendant_lon)
            # 66's "falling away from the Ascendant" is aversion, not cadency:
            # Dykes' note there reads "That is, in aversion to it," and the Course
            # Glossary makes the same equivalence under Cadent.
            slow_averse = _averse_to_ascendant(planetary_data[slow]['longitude'], ascendant_lon)
            if fast_house in ANGLE_HOUSES and slow_averse:
                results.append({'Manner': 'II (66-69)', 'Planet': fast, 'Returned By': slow})

        return results

def evaluate_revoking(planetary_data, sim):
    """Revoking (Gr. Intr. VII.5, 117, Fig. 137): "a planet is
    CONNECTING with a planet, but BEFORE IT REACHES IT, it retrogrades away
    from it, and its connection is nullified."

    NOT Sahl Ch.3, 117, which an earlier version of this docstring also
    cited: that paragraph is "know that Saturn, in nativities of the day
    ... decreases harm." The two works' paragraph numbers collide.

    "Before it reaches it" fixes the window: the only question is whether
    the aspect perfects between now and the applicant's first station. If
    it does, nothing was revoked; if it does not, the station is what
    stopped it. Searching the whole horizon instead, and accepting "no
    perfection found anywhere" as a positive, let a station on day 190
    revoke a connection that was never going to complete inside 200 days
    regardless -- a finding with no causal content."""
    with doctrine(ABU_MASHAR):
        if sim is None:
            return []
        rows = _pairwise_configurations(planetary_data)
        results = []
        for r in rows:
            if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
                continue
            # 117 revokes the connection of "a planet ... connecting with a
            # planet" when IT retrogrades away before arriving, so the station
            # that matters is the applicant's, not the naturally lighter one's.
            fast, slow = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            first_station = next((s for s in sim['events'][fast]['stations'] if s[1] == 'first'), None)
            if not first_station:
                continue
            # "BEFORE IT REACHES IT, it retrogrades away from it." The only
            # window that matters is up to the station: if the aspect perfects
            # in it, nothing was revoked, and if it does not, the station is
            # what stopped it. An earlier version searched the whole 200-day
            # horizon and also accepted "no perfection found anywhere" as proof
            # -- so a station on day 190 revoked a connection that was never
            # going to complete inside the horizon in the first place, with the
            # station doing none of the work.
            station_day = first_station[0]
            if _perfection_day(sim, fast, slow, r['target'], before_day=station_day) is not None:
                continue
            results.append({
                'Planet': fast, 'Was Connecting To': slow,
                'Stations Retrograde In (days)': round(station_day, 1),
            })
        return results

def evaluate_resistance(planetary_data, sim):
    """Resistance (VII.5, 118, Fig. 138). The chapter prescribes an ordered
    sequence of events, and each step is now required rather than inferred:

    "RESISTANCE is if there was A LIGHT PLANET IN MANY DEGREES, and another
    planet HEAVIER THAN IT IN FEWER DEGREES, and A THIRD PLANET LIGHTER
    THAN THAT LIGHT ONE wanting a connection with the heavy one, so that
    the light one in more degrees GOES RETROGRADE and CONNECTS WITH THE
    HEAVY ONE THROUGH ITS RETROGRADATION -- and then GOES PAST IT and there
    is A CONNECTION OF THAT THIRD ONE with this retrograde one ... not with
    the heavy one."

    Dykes' note: "In Figure 138, Mercury wants to connect with Mars. But
    Venus, who is in a later degree, suddenly goes retrograde, passes by
    Mars, and connects with Mercury, resisting and obstructing his attempt
    to connect with Mars." So L = Venus, H = Mars, T = Mercury.

    Required, in order: T applying to H; L ahead of H by degree and lighter
    than it; L's first station; L's union with H after that station; T's
    connection with L after that; and T not reaching H first. An earlier
    version proved only the station and that some later connection existed,
    never that L actually reached H by retrogradation or that it did so
    before T arrived."""
    with doctrine(ABU_MASHAR):
        if sim is None:
            return []
        rows = _pairwise_configurations(planetary_data)
        row_for = {frozenset({r['p1'], r['p2']}): r for r in rows}
        planets = [p for p in planetary_data.keys() if p != 'North Node']
        results = []

        for heavy in planets:
            h_lon = planetary_data[heavy]['longitude']
            for light in planets:
                if light == heavy or WEIGHT_ORDER.index(light) <= WEIGHT_ORDER.index(heavy):
                    continue                       # L must be LIGHTER than H
                # "a light planet in many degrees, and another planet heavier
                # than it in fewer degrees" -- L ahead of H in the zodiac.
                if not 0.0 < (planetary_data[light]['longitude'] - h_lon) % 360.0 < 180.0:
                    continue
                station = next((s for s, k in sim['events'][light]['stations'] if k == 'first'), None)
                if station is None:
                    continue
                # "connects with the heavy one THROUGH ITS RETROGRADATION"
                union_lh = _body_union_day(sim, light, heavy, after_day=station)
                if union_lh is None:
                    continue
                for third in planets:
                    if third in (light, heavy):
                        continue
                    if WEIGHT_ORDER.index(third) <= WEIGHT_ORDER.index(light):
                        continue                   # T must be LIGHTER than L
                    r_th = row_for.get(frozenset({third, heavy}))
                    if r_th is None or r_th['aspect_name'] == 'Aversion' or r_th['motion'] != 'Applying':
                        continue                   # T must actually want H
                    # "and then goes past it and there is a connection of that
                    # third one with this retrograde one" -- after the union.
                    r_tl = row_for.get(frozenset({third, light}))
                    if r_tl is None or r_tl['aspect_name'] == 'Aversion':
                        continue
                    meet_tl = _perfection_day(sim, third, light, r_tl['target'], after_day=union_lh)
                    if meet_tl is None:
                        continue
                    # T must not have reached H first; otherwise nothing was
                    # obstructed.
                    reach_th = _perfection_day(sim, third, heavy, r_th['target'], before_day=meet_tl)
                    if reach_th is not None:
                        continue
                    results.append({
                        'Light Planet': light,
                        'Originally Heading To': heavy,
                        'Resisted, Now Connects With': third,
                        'Station (days)': round(station, 1),
                        'Reaches It Retrograde (days)': round(union_lh, 1),
                        'Third Planet Meets It (days)': round(meet_tl, 1),
                    })
        return results

def evaluate_escape(planetary_data, sim):
    """Escape (VII.5, 119, Fig. 139):

    "ESCAPE is if a planet is going towards the connection of a planet, but
    BEFORE IT REACHES IT, the one it is connecting with SHIFTS OVER TO THE
    NEXT SIGN, and WHEN THE ONE HANDING OVER CHANGES [to that next sign]
    there is one of the planets closer to it than [the first one], so its
    connection is with the other planet, and its connection with the first
    one is nullified."

    The second half is the part that was missing. Dykes' note spells out
    the picture: "Venus in Virgo had wanted to connect with Mercury, who
    was at the end of the sign. But before she could complete the
    connection, Mercury passed into Libra (and went past Saturn). BY THE
    TIME VENUS PASSES INTO LIBRA, SHE ENCOUNTERS THE BODY OF SATURN and
    connects with him, letting Mercury escape."

    So the applicant must itself follow the escapee into the new sign, and
    the capture is a body it meets there -- not merely whatever it happens
    to perfect with next anywhere in the chart. Both the ingress and the
    union are now required events with times, so a row asserts a capture
    only when one actually occurs.

    This makes Escape rare, which it should be: it needs two planets to
    cross the same sign boundary in sequence inside the horizon."""
    with doctrine(ABU_MASHAR):
        if sim is None:
            return []
        rows = _pairwise_configurations(planetary_data)
        results = []
        for r in rows:
            if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
                continue
            fast, slow = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            sign_exits = sim['events'][slow]['sign_exits']
            if not sign_exits:
                continue
            exit_day = sign_exits[0]
            # "before it reaches it, the one it is connecting with shifts over"
            if _perfection_day(sim, fast, slow, r['target'], before_day=exit_day) is not None:
                continue
            new_sign = int(_lon_at(sim, slow, exit_day + 1e-3) // 30)
            # "when the one handing over changes [to THAT NEXT SIGN]" -- the
            # applicant follows it across the same boundary, which is what
            # Fig. 139 shows: Venus and Mercury are both in Virgo, Mercury
            # crosses into Libra, and Venus's own next crossing is into Libra
            # behind him. So it must be the applicant's NEXT sign change, not
            # any later arrival in that sign -- otherwise the Moon qualifies
            # against everything, since she re-enters every sign each month.
            next_exit = next((d for d in sim['events'][fast]['sign_exits'] if d > exit_day), None)
            if next_exit is None or int(_lon_at(sim, fast, next_exit + 1e-3) // 30) != new_sign:
                continue
            ingress_day = next_exit
            # "there is one of the planets closer to it" -- the body it meets
            # in that sign once it arrives.
            best, best_day = None, None
            for other in planetary_data:
                if other in (fast, slow, 'North Node'):
                    continue
                day = _body_union_day(sim, fast, other, after_day=ingress_day)
                if day is None:
                    continue
                if int(_lon_at(sim, other, day) // 30) != new_sign:
                    continue
                if best_day is None or day < best_day:
                    best, best_day = other, day
            if best is None:
                continue
            # "there is one of the planets CLOSER to it than [the first one],
            # so its connection is with the other planet, and its connection
            # with the first one is nullified": the capture must come BEFORE
            # the original connection would have perfected in the new sign.
            # If the applicant reaches the escapee first, nothing is
            # nullified and there is no Escape (Astra F05; Sahl, Introduction
            # 3, 57 fn 77 says the same from the other side: crossing over
            # and connecting with B "before there is a connection with
            # another planet" completes the ORIGINAL situation).
            original = _perfection_day(sim, fast, slow, r['target'], after_day=ingress_day)
            if original is not None and original <= best_day:
                continue
            if True:
                results.append({
                    'Planet': fast, 'Escaped': slow, 'Connected Instead With': best,
                    'Escapee Leaves Sign (days)': round(exit_day, 1),
                    'Applicant Follows In (days)': round(ingress_day, 1),
                    'Meets Its Body (days)': round(best_day, 1),
                })
        return results

# Sahl's precedence among the three kinds of contact a planet can hold,
# stated at Ch.3, 44 and enumerated in Dykes' note there: "(1) 'uniting' or
# a conjunction by degree, (2) a connection by degree from another sign,
# (3) an aspect by sign. In other words, while degree-based connections can
# cut each other as in type #1, aspects by sign do not cut each other."
#
# The rule itself, at 44: "a connection does not nullify a uniting, but a
# uniting does NULLIFY a connection, while an aspect does not cut an aspect
# [but] hands over the sought thing, and a uniting cuts an aspect."
_CONTACT_NAMES = {0: 'a uniting', 1: 'a connection by degree', 2: 'an aspect by sign'}

def _contact_rank(row):
    if row['assembly'] and _is_connected(row):
        return 0
    if _is_connected(row):
        return 1
    return 2

def evaluate_cutting_the_light(planetary_data, sim):
    """Cutting the Light. Type III is Sahl's own Blocking #1, "Cutting the
    Light" (The Introduction Ch.3, 31-34, Fig. 12) -- confirmed against
    Fig. 12's own numbers (Ascendant Virgo, Mercury 10 Cancer applying by
    trine to Jupiter 15 Pisces, but Mars 13 Aries sits square to Mercury at
    only ~3 degrees from exact): Mercury completes the nearer connection to
    Mars before it ever reaches Jupiter, cutting off the original one --
    exactly this mechanism (among several planets a given one is applying
    to, it connects with whichever is nearest by degree first, cutting off
    the more distant, originally-favored connection). Abu Ma'shar reuses it
    as his own Type III when he moves "Cutting the Light" out of Sahl's
    three-way Blocking and into its own later, expanded category (Great
    Introduction VII.5, 120-125, Fig. 142). Types I-II (121-124, Figs.
    140-141, forward-sim) are Abu Ma'shar's own further elaboration, not
    found in Sahl: an intervening planet stations retrograde and enters the
    light planet's own sign before the light planet reaches its original
    heavy target.

    Contacts are ordered by Sahl's own PRECEDENCE (44 and its note, see
    _contact_rank()), not by nearness alone; nearness only breaks ties
    within a rank. But precedence decides which contact PREVAILS, and that
    is not the same question as which one is CUT.

    Two outcomes are therefore reported, not one:

    NULLIFICATION (44-48, Fig. 15). A single planet holds both a union and
    a connection. Sahl: "the Moon is in 10 degrees of Taurus, and Mars in
    20 degrees of Taurus, and the Moon is connecting with Venus (and Venus
    is in 15 degrees of Cancer). So her connection with Venus is PRIOR to
    her uniting with Mars, BUT the Moon is uniting [with Mars], and that is
    stronger than an aspect and a connection" (46-47). The note on 47:
    "EVEN THOUGH the connection by aspect may perfect first, the planet it
    is connecting to by body will still be the DOMINANT one." The note on
    48 then rules this out of the cutting category by name: "note that this
    is NOT A CASE OF 'CUTTING' ... and it is not exactly a case of blocking
    by nullification, because Venus is not one of the significators we want
    to join." An earlier version emitted it as "Moon cut off from Venus"
    and cited Fig. 15 in this docstring as confirmation of the sort order.
    The sort order was right; the verdict drawn from it was not.

    CUTTING (Sahl 31-34, Fig. 12; VII.5, 125, Fig. 142). A nearer
    degree-connection intercepts a more distant one. 32 defines it purely
    by order of arrival: "a planet between the lord of the Ascendant and
    the lord of the sought thing, IN FEWER DEGREES than one of them, so the
    connection with it is BEFORE the connection ... with the lord of the
    sought thing." Abu Ma'shar's Fig. 142 is the case the previous version
    could not detect: Mars 12 Aquarius wants Jupiter 29 Taurus by square,
    17 degrees off, and Saturn at 15 Taurus is 3 degrees off -- "he
    connects with Saturn first, WHO CUTS OFF HIS LIGHT from reaching
    Jupiter" (note on 125). A rank-2 exclusion, reasoned from 44's "an
    aspect does not cut an aspect", was discarding exactly this: 44
    withholds cutting from an ASPECT, and the note on 44 grants it to
    degree-based connections, which "can cut each other as in type #1".
    Only a bare sign-aspect cuts nothing.

    Note that 42-48 has been misread twice in this project. 42-43 (Fig. 14)
    is third-party blocking, handled in evaluate_blocking(); 45-48 (Fig.
    15) is the one-planet nullification above. They are consecutive."""
    rows = _pairwise_configurations(planetary_data)
    results = []

    by_fast = {}
    for r in rows:
        if r['aspect_name'] != 'Aversion':
            by_fast.setdefault(r['applicant'] or r['light_name'], []).append(r)
    for fast, candidates in by_fast.items():
        applying = sorted((r for r in candidates if r['motion'] == 'Applying'),
                           key=lambda r: (_contact_rank(r), abs(r['deviation'])))
        if len(applying) < 2:
            continue
        winner = applying[0]
        win_rank = _contact_rank(winner)
        if win_rank == 2:
            continue   # "an aspect does not cut an aspect" (44)
        for r in applying[1:]:
            lose_rank = _contact_rank(r)
            because = (f'{_CONTACT_NAMES[win_rank]} outranks {_CONTACT_NAMES[lose_rank]}'
                        if win_rank != lose_rank
                        else f'nearer by {abs(r["deviation"]) - abs(winner["deviation"]):.1f} deg')
            # A UNITING does not CUT: it DOMINATES. Dykes' note on 47 --
            # "EVEN THOUGH the connection by aspect may perfect first, the
            # planet it is connecting to by body will still be the DOMINANT
            # one" -- and his note on 48 rules the case out of this category
            # by name: "note that this is NOT A CASE OF 'CUTTING' which only
            # involves a connection from different signs; it is not a case
            # of 'intervention' ... and it is not exactly a case of blocking
            # by nullification, because Venus is not one of the
            # significators we want to join."
            #
            # An earlier version reported Fig. 15 as "Moon cut off from
            # Venus", and cited that figure in its own docstring as
            # CONFIRMATION of the sort order. The sort order is right; the
            # verdict drawn from it was not. 44's precedence says which
            # contact prevails, not which is severed.
            if win_rank == 0:
                results.append({
                    'Type': 'Nullification (44-48)',
                    'Planet': fast,
                    'Yields To': winner['receiver'] or winner['heavy_name'],
                    'Other Contact': r['receiver'] or r['heavy_name'],
                    'Because': because + '; the other perfects first but is not cut off',
                })
            else:
                results.append({
                    'Type': 'III',
                    'Planet': fast,
                    'Yields To': winner['receiver'] or winner['heavy_name'],
                    'Other Contact': r['receiver'] or r['heavy_name'],
                    'Because': because,
                })

    if sim is not None:
        for r in rows:
            if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
                continue
            light, heavy = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            exact_day = _perfection_day(sim, light, heavy, r['target'])
            if exact_day is None:
                continue
            light_sign = int(planetary_data[light]['longitude'] // 30)

            # --- Type I (121-122, Fig. 140) ---------------------------
            # "a planet wants a connection with a planet heavier than
            # itself, and IN THE SECOND SIGN FROM THE LIGHT ONE is a
            # planet, but before the light one reaches the connection with
            # the heavy one, the planet which is in the second [sign] from
            # it GOES RETROGRADE AND ENTERS ITS SIGN, AND CONJOINS with
            # it." The note on 121 reads that last verb as conjoining by
            # degree, "rather than the looser 'assembling'".
            #
            # Two of those four clauses were unchecked: the intervener had
            # to start in the second sign, and it had to actually reach the
            # light planet's body. An earlier version accepted any planet
            # that stationed and crossed into the light planet's sign,
            # whatever it did once there and wherever it started.
            for candidate in planetary_data:
                if candidate in (light, heavy, 'North Node'):
                    continue
                if int(planetary_data[candidate]['longitude'] // 30) != (light_sign + 1) % 12:
                    continue
                station = next((s for s, k in sim['events'][candidate]['stations']
                                 if k == 'first' and s < exact_day), None)
                if station is None:
                    continue
                ingress = _sign_ingress_day(sim, candidate, light_sign,
                                             after_day=station, before_day=exact_day)
                if ingress is None:
                    continue
                union = _body_union_day(sim, candidate, light,
                                         after_day=ingress, before_day=exact_day)
                if union is None:
                    continue
                results.append({
                    'Type': 'I', 'Planet': light, 'Yields To': candidate, 'Other Contact': heavy,
                    'Because': f'stations day {station:.0f}, enters the sign day {ingress:.0f}, '
                                f'conjoins day {union:.0f}, before perfection on day {exact_day:.0f}',
                })

            # --- Type II (123-124, Fig. 141) --------------------------
            # "a light planet is connecting with a planet heavier than
            # itself, and THAT PLANET HANDS OVER TO A HEAVY PLANET, but
            # before the light one reaches the degree of the planet which
            # is heavier than itself, that planet CONNECTS WITH THE HEAVY
            # PLANET AND GOES PAST IT, so there is a connection of the
            # light one WITH THE HEAVY ONE, while it nullifies its
            # connection with the first one." The note: "Mercury wants to
            # connect with Venus. But before he can do that, she connects
            # with Mars and then continues on. Then Mercury is left with
            # the conjunction of Mars, which was not what he wanted."
            # Not implemented at all before this.
            for onward in planetary_data:
                if onward in (light, heavy, 'North Node'):
                    continue
                r_mid = next((x for x in rows if {x['p1'], x['p2']} == {heavy, onward}), None)
                if r_mid is None or r_mid['aspect_name'] == 'Aversion' or r_mid['motion'] != 'Applying':
                    continue
                if (r_mid['applicant'] or r_mid['light_name']) != heavy:
                    continue          # the middle planet must be the one handing on
                mid_day = _perfection_day(sim, heavy, onward, r_mid['target'], before_day=exact_day)
                if mid_day is None:
                    continue          # it must get there FIRST
                r_far = next((x for x in rows if {x['p1'], x['p2']} == {light, onward}), None)
                if r_far is None or r_far['aspect_name'] == 'Aversion':
                    continue
                far_day = _perfection_day(sim, light, onward, r_far['target'], after_day=mid_day)
                if far_day is None or far_day >= exact_day:
                    continue          # ... and the light one must land on it
                                      # BEFORE reaching the one it wanted,
                                      # which is what "nullifies its
                                      # connection with the first one" means
                results.append({
                    'Type': 'II', 'Planet': light, 'Yields To': onward, 'Other Contact': heavy,
                    'Because': f'{heavy} reaches {onward} on day {mid_day:.0f} and moves on; '
                                f'{light} lands on {onward} instead on day {far_day:.0f}',
                })
    return results

def _find_recompense_day(sim, helper, helped):
    """Recompense (VII.5, 127): "[the first planet] will not cease to have
    favor for it until the planet which had bestowed the favor on it FALLS
    INTO ITS OWN WELL OR FALL, and the other [planet] CONNECTS WITH IT (or
    it connects with the other), and PULLS IT OUT of its well or fall."

    Two events, both required: the helper arriving in its own well or fall,
    and a connection actually perfecting there. An earlier version scanned
    the daily samples and accepted any pair whose separation sat within 5
    degrees of an aspect angle on one of those days -- a proximity this
    project invented, on a one-day grid, standing in for a perfection that
    was never computed. Now the aspect is perfected against the ephemeris
    and the helper must still be in the well or fall when it lands.

    Returns the day, or None. Not found inside the horizon is omitted from
    the table, not reported as a negative finding."""
    helper_fall_signs = FALLS.get(helper, [])

    def in_well_or_fall(lon):
        sign = get_zodiac_sign(lon)
        return (sign in helper_fall_signs
                or (int(lon % 30) + 1) in WELLED_DEGREES.get(sign, []))

    days = sim['series'][helper]['day']
    lons_helper = sim['series'][helper]['lon']
    for day, lh in zip(days, lons_helper):
        if not in_well_or_fall(lh):
            continue
        target = _configuration_target_at(sim, helper, helped, day)
        if target is None:
            continue
        perf = _perfection_day(sim, helped, helper, target, after_day=day)
        if perf is None:
            continue
        if in_well_or_fall(_lon_at(sim, helper, perf)):
            return perf
    return None

def evaluate_favor_and_recompense(planetary_data, essential, sect, sim):
    """Favor and Recompense (VII.5, 126-128, Fig. 143): a planet in its own
    Fall or a Well, pulled out by a connecting dispositor (Favor);
    Recompense is the reciprocal payback later, found via the forward
    simulation when available."""
    with doctrine(ABU_MASHAR):
        rows = _pairwise_configurations(planetary_data)
        results = []
        for r in rows:
            if r['aspect_name'] == 'Aversion' or not _is_connected(r):
                continue
            for helper, helped in ((r['p1'], r['p2']), (r['p2'], r['p1'])):
                lon = planetary_data[helped]['longitude']
                sign = get_zodiac_sign(lon)
                degree_1_based = int(lon % 30) + 1
                in_well = degree_1_based in WELLED_DEGREES.get(sign, [])
                in_fall = essential[helped]['Fall']
                if not (in_well or in_fall):
                    continue
                if helper not in _dispositors(lon, sect):
                    continue
                entry = {'Planet': helped, 'Condition': 'Fall' if in_fall else 'Well', 'Favored By': helper}
                if sim is not None:
                    recompense_day = _find_recompense_day(sim, helper, helped)
                    if recompense_day is not None:
                        entry['Recompense (days)'] = round(recompense_day, 1)
                results.append(entry)
        return results

def evaluate_reception(planetary_data, sect, sim=None):
    """Reception, under whichever author profile is active. The two differ
    in scope, in direction, and in what counts as strong, so they are
    written out separately rather than blended.

    SAHL (The Introduction Ch.3, 49-55). One direction only: the connecting
    planet sits in a dignity belonging to the planet it connects with, and
    so is received by it (52: "if the Moon is in Aries and she is
    connecting with Mars, then he receives her because Aries is his
    house"). House or exaltation is "perfect reception, with truthful
    intention" (49); triplicity alone is expressly ranked "below this
    reception" (50); bound counts only together with triplicity, which
    Sahl attributes to Masha'allah (54-55, and Abu Ma'shar's own note on
    132 confirms the attribution). Face never appears. A connection is
    required throughout.

    Under Sahl's profile a non-reception of Kind II for the same pair
    suppresses the reception row (refusal wins), and one of Kind IV marks
    it brought down (62's own word); see the note at the end of the
    function and synthesis/13_open_decisions.md D-2.

    Sahl gives two further forms after that, both previously unimplemented
    and both now here (they are his own, so they run under his profile
    only):

    56, RECEPTION AT ONE REMOVE. "If the Moon was connecting with a planet
    and that planet was connecting with the lord of the house of the Moon
    or its exaltation, then the Moon is received." The note glosses the
    second lord as "the exalted lord of the sign in which the Moon is," and
    calls the whole thing "like a transfer of light which indirectly allows
    for reception." Both legs are taken in Sahl's own directed sense of
    "connecting with" -- 6's "going straightaway to ... going towards," not
    mere proximity, since separating is his separate term at 22. On the
    loose reading this fired 1.93 times a chart, more often than direct
    reception; on the directed one, 0.20.

    57, RECEPTION OR UNDERMINING AFTER THE SIGN CHANGE. "If the Moon was
    empty in course, and then she passed over into the next sign and
    connected with the lord of her first sign (or its exaltation), IT IS
    JUST LIKE RECEPTION; and if she connected with a planet OTHER than the
    lord of her first sign or its exaltation, IT UNDERMINES HER." Both
    halves are reported: the second is a finding in its own right, not the
    absence of the first. Needs the forward simulation, which also means
    the slow planets exclude themselves -- Saturn takes years to change
    sign, well past the horizon.

    Sahl names the Moon in both, as he does throughout 49-57, but neither
    mechanism has anything lunar in it and 58 immediately widens the same
    shape to "the Moon or the lord of the Ascendant," so both are applied
    to any planet with the paragraph number on the row.

    ABU MA'SHAR (Gr. Intr. VII.5, 129-133). Wider on every axis.
    All five dignities count (129). Reception also runs in REVERSE: "a
    planet connects with a planet, and the one accepting the connection is
    in the house of the one handing over" (130) -- his own note explains
    why, since "Saturn could never be received because he is too slow to
    connect with anyone." House or exaltation is strongest (131); a single
    minor dignity alone is weak "unless it brings together the bound and
    triplicity, or the bound and face, or the triplicity and face: for that
    will be a complete reception" (132). And reception can hold by looking
    with no connection at all, "except that reception by connection is more
    powerful" (133).

    Abu Ma'shar grades on TWO AXES, and they are returned as two columns.
    129-133 grade the LOCAL BASIS: "the strongest of them is the lord of
    the house or exaltation" (131), a lone minor dignity "is weak unless it
    brings together the bound and triplicity, or the bound and face, or the
    triplicity and face: for that will be a complete reception" (132).
    136-142 then class reception GLOBALLY as strong, middling, or below,
    and there house and exaltation sit with the rest: "a [2] middling
    reception is the planets' reception of each other from the house,
    exaltation, bound, triplicity, or face" (140); "if two met [together]
    from this, or each one of them received its associate, it is a strong
    reception" (141); the natural acceptances of 134-135 are "[3] below
    that" (142), and 137 and 139 are named strong forms. So a lone domicile
    reception is the strongest local basis AND globally middling -- both
    true, and an earlier version wrote only the first as its Grade. The
    rows carry 'Dignity quality' (129-133) and 'Overall class' (136-142);
    Sahl's rows keep his one 'Grade' (49-55), which is his own scale.

    Returns one row per reception found, naming the receiver, the planet
    received, which way round it runs, the dignities it rests on, its
    class(es) and whether it holds by connection or only by looking -- so
    the evidence is inspectable rather than reduced to a single flag.
    Mutual reception is reported as its own row.

    Absence of a row here is NOT Sahl's non-reception: that is a set of
    specific hostile configurations (58-62), computed separately in
    evaluate_non_reception(). A pair can easily be neither received nor
    non-received."""
    rows = _pairwise_configurations(planetary_data)
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    sahl = CONNECTION_PROFILE == 'Sahl'
    results = []

    def claims(sitter, lord):
        """Which of `lord`'s dignities the `sitter` planet is standing in."""
        r = get_essential_rulers(planetary_data[sitter]['longitude'])
        found = []
        if r['domicile'] == lord: found.append('house')
        if r['exaltation'] == lord: found.append('exaltation')
        if r[triplicity_key] == lord: found.append('triplicity')
        if r['term'] == lord: found.append('bound')
        if not sahl and r['face'] == lord: found.append('face')   # Sahl never uses face
        return found

    def grade(found):
        """Sahl's single scale (49-55)."""
        if 'house' in found or 'exaltation' in found:
            return 'Perfect'
        # 50 ranks triplicity below perfect; bound only counts paired
        # with triplicity, on Masha'allah's authority (54-55).
        if 'triplicity' in found and 'bound' in found:
            return "Complete, triplicity with bound (54-55, Masha'allah)"
        if 'triplicity' in found:
            return 'Lesser, triplicity alone (50)'
        return None                                       # bound alone is not reception for Sahl

    def abu_axes(found):
        """Abu Ma'shar's two classifications of a dignity reception, as
        (dignity_quality per 129-133, overall_class per 136-142)."""
        majors = [d for d in found if d in ('house', 'exaltation')]
        minors = [d for d in found if d in ('bound', 'triplicity', 'face')]
        if majors:
            quality = f"Strongest basis, {' and '.join(majors)} (131)"
        elif len(minors) >= 2:
            quality = f"Complete, {' with '.join(minors)} (132)"
        else:
            quality = f"Weak, {minors[0]} alone (132)"
        # 140 lists all five dignities as middling; 141 promotes "two met
        # together from this" to strong. Which dignities makes no
        # difference to this axis -- that is what the other axis is for.
        overall = ('Strong (141): two dignities together' if len(found) >= 2
                   else 'Middling (140): one dignity')
        return quality, overall

    for row in rows:
        if row['aspect_name'] == 'Aversion' and not _sahl_body_row(row):
            continue
        connected = _is_connected(row)
        if sahl and not connected:
            continue                                      # Sahl requires the connection
        mode = 'By connection' if connected else 'By looking only (133)'
        # Reception is DIRECTED at the planet that is actually connecting,
        # not at the naturally lighter one. Sahl's own example is "the Moon
        # in Aries connecting with Mars, he receives her" -- she is received
        # because she is the one applying. Ordinarily the applicant is the
        # lighter planet and the two readings coincide; when the heavier is
        # closing (by retrogradation, or by overtaking a planet that is
        # slower still), they do not.
        #
        # Dykes' note on 130 makes this the explicit reason that paragraph
        # exists: "if the received planet always had to be the lighter
        # planet and connect with its own lord ... Saturn could never be
        # received because he is too slow to connect with anyone (UNLESS BY
        # RETROGRADATION)." Reading reception off natural rank threw away
        # the exception that note names. On a sample of ~8,000 configured
        # pairs the applicant is the heavier planet in 3.6% of them.
        light, heavy = row['light_name'], row['heavy_name']
        applicant = row['applicant'] or light
        accepter = row['receiver'] or heavy

        # 129: the connecting planet stands in the receiver's dignity.
        directions = [(accepter, applicant, 'Receives the connecting planet (129)')]
        if not sahl:
            # 130: the reverse, which Sahl does not have.
            directions.append((applicant, accepter, 'Receives the accepting planet (130)'))

        found_here = []
        for receiver, received, direction in directions:
            found = claims(received, receiver)
            if not found:
                continue
            row = {'Receiver': receiver, 'Received': received, 'Direction': direction,
                   'Via': ', '.join(found)}
            if sahl:
                g = grade(found)
                if not g:
                    continue
                row['Grade'] = g
            else:
                row['Dignity quality'], row['Overall class'] = abu_axes(found)
            row['Mode'] = mode
            found_here.append(receiver)
            results.append(row)
        if len(found_here) == 2:
            row = {'Receiver': f'{applicant} & {accepter}', 'Received': 'each other',
                   'Direction': 'Mutual', 'Via': '–'}
            if sahl:
                row['Grade'] = 'Mutual reception'           # Sahl does not name it
            else:
                # 141: "if ... each one of them received its associate, it
                # is a strong reception."
                row['Dignity quality'] = 'Each stands in a dignity of the other'
                row['Overall class'] = 'Strong (141): mutual'
            row['Mode'] = mode
            results.append(row)

    if not sahl:
        # --- 134-142: the recovered acceptance material ------------------
        # p. 477 was missing from the photographs until this revision. It
        # is Abu Ma'shar's OWN, and it is a different thing from 129-133:
        # the note on 134 says he "turns to a more general sense of the
        # Arabic word 'reception' which is NOT BASED ON DIGNITIES: namely,
        # that one planet will 'accept' the management of another if they
        # are in harmonious signs." Reported as its own basis so it cannot
        # be mistaken for a dignity reception.
        sign_of = {p: get_zodiac_sign(d['longitude']) for p, d in planetary_data.items()
                    if p != 'North Node'}
        for row in rows:
            a, b = row['p1'], row['p2']
            asp = row['aspect_name']

            # 137-138 come FIRST because they hold in aversion too: "he
            # receives her FROM ALL SIGNS, since her glow is from him". The
            # rest of this block needs a configuration; the Sun-Moon natural
            # reception does not, and skipping aversion rows before it lost
            # the row in 32% of charts.
            if {a, b} == {'Sun', 'Moon'}:
                if asp == 'Opposition':
                    # 137's own word, kept rather than forced onto the
                    # strong/middling/below ladder.
                    overall, via = 'Detestable (137): from the opposition', 'from the opposition'
                    quality = 'By nature, her glow is from him (137)'
                else:
                    sun_claims = _dispositors(planetary_data['Moon']['longitude'], sect) & {'Sun'}
                    doubled = bool(sun_claims)
                    overall = 'Strong (137)' + (', doubled by sign (138)' if doubled else '')
                    quality = 'By nature, her glow is from him (137)' + (' and by sign (138)' if doubled else '')
                    via = 'her glow is from him' + (', and he has a claim where she stands' if doubled else '')
                    if asp == 'Aversion':
                        via += ' (signs in aversion; 137 says from all signs)'
                results.append({
                    'Receiver': 'Sun', 'Received': 'Moon',
                    'Direction': 'Reception by nature (137-138)',
                    'Via': via, 'Dignity quality': quality, 'Overall class': overall,
                    'Mode': 'Natural, from all signs',
                })
            # 134: "if one of the two planets was in the TRINE of the other
            # (or in its SEXTILE), or in two signs of equal ascensions, or
            # in two signs whose length of the day is one [and the same],
            # or IN TWO SIGNS BELONGING TO ONE [and the same] PLANET, then
            # one of the two will 'receive' its associate due to the
            # agreement of the nature of these signs with each other."
            #
            # All four bases are computable: the equal-ascension and
            # equal-daylight sign pairs are enumerated in VII.5 itself (56
            # and 67-75; EQUAL_ASCENSION_PAIRS, EQUAL_DAYLIGHT_PAIRS). This
            # runs BEFORE the aversion skip, because 134 is acceptance
            # without looking -- the note on it: planets "in harmonious
            # signs" -- and most of these pairs do not look at each other:
            # Aries/Pisces, Gemini/Cancer and the same-lord pairs Aries/
            # Scorpio, Taurus/Libra and Capricorn/Aquarius are all in
            # aversion (note 157 on 53:
            # "some of the signs of equal ascensions below do look at each
            # other", i.e. most do not). An earlier version skipped aversion
            # first, which silently confined 134 to configured pairs.
            harmonious = []
            if asp in ('Trine', 'Sextile'):
                harmonious.append(f'{asp.lower()}')
            # "TWO signs belonging to one planet" -- Aries/Scorpio, Taurus/
            # Libra and so on. Equal lords with equal signs is an assembly,
            # which 134 does not list; without the inequality this fired on
            # every same-sign pair (26% of 134 rows in a sample).
            if (sign_of[a] != sign_of[b]
                    and SIGN_TO_DOMICILE.get(sign_of[a]) == SIGN_TO_DOMICILE.get(sign_of[b])):
                harmonious.append(f'both signs of {SIGN_TO_DOMICILE.get(sign_of[a])}')
            sign_pair = frozenset({sign_of[a], sign_of[b]})
            if sign_pair in EQUAL_ASCENSION_PAIRS:
                harmonious.append('signs of equal ascensions (56)')
            if sign_pair in EQUAL_DAYLIGHT_PAIRS:
                harmonious.append('signs of equal daylight (67-75)')
            if harmonious:
                results.append({
                    'Receiver': f'{a} & {b}', 'Received': 'each other',
                    'Direction': 'Acceptance by harmonious signs (134)',
                    'Via': ', '.join(harmonious),
                    'Dignity quality': 'Not a dignity basis: harmonious signs (134)',
                    'Overall class': 'Below middling (142)', 'Mode': 'Not a dignity reception',
                })
            if asp == 'Aversion':
                continue

            # 135: "the fortunes receive each other due to the moderation
            # of their natures, while Mars and Saturn each receive the
            # other from the assembly, sextile, and trine."
            if {a, b} == FORTUNES:
                results.append({
                    'Receiver': f'{a} & {b}', 'Received': 'each other',
                    'Direction': 'Acceptance by nature, the two fortunes (135)',
                    'Via': 'moderation of their natures',
                    'Dignity quality': 'Not a dignity basis: nature (135)',
                    'Overall class': 'Below middling (142)', 'Mode': 'Not a dignity reception',
                })
            if {a, b} == INFORTUNES and asp in ('Conjunction', 'Sextile', 'Trine'):
                results.append({
                    'Receiver': f'{a} & {b}', 'Received': 'each other',
                    'Direction': 'Acceptance, the two infortunes (135)',
                    'Via': f'{asp.lower()} only -- 135 allows assembly, sextile and trine',
                    'Dignity quality': 'Not a dignity basis: nature (135)',
                    'Overall class': 'Below middling (142)', 'Mode': 'Not a dignity reception',
                })

            # 137-138: "the majority of [strong reception] belongs to the
            # Moon relative to the Sun, because HE RECEIVES HER FROM ALL
            # SIGNS, since her glow is from him -- EXCEPT THAT HIS
            # RECEPTION OF HER FROM THE OPPOSITION IS DETESTABLE. But if
            # her connection with him is from a sign in which he has a
            # claim, that is TWO RECEPTIONS: a reception by nature, and a
            # reception by sign."
            # (137-138 handled at the top of the loop, before the aversion skip.)

            # 139: "if Mercury received a planet from out of Virgo, that is
            # also a strong reception." The note reads "from out of" as the
            # other planet being IN Virgo, where Mercury holds both house
            # and exaltation.
            for x, y in ((a, b), (b, a)):
                if x == 'Mercury' and sign_of[y] == 'Virgo':
                    results.append({
                        'Receiver': 'Mercury', 'Received': y,
                        'Direction': 'Reception in Virgo (139)',
                        'Via': 'house and exaltation together',
                        'Dignity quality': 'Strongest basis, house and exaltation (131)',
                        'Overall class': 'Strong (139)', 'Mode': 'By dignity',
                    })
        return results

    # --- 56: reception at one remove ---------------------------------
    # "And if the Moon was CONNECTING WITH A PLANET and THAT PLANET was
    # connecting with the lord of the house of the Moon or its exaltation,
    # then the Moon is received." The note on 56 glosses the second lord as
    # "the exalted lord of the sign in which the Moon is," and the note on
    # the sentence calls the whole thing "like a transfer of light which
    # indirectly allows for reception."
    #
    # Sahl names the Moon, as he does throughout 49-57; the mechanism has
    # nothing lunar in it, and 58 immediately widens the same shape to "the
    # Moon or the lord of the Ascendant," so it is applied to any planet
    # and the paragraph number is on the row.
    connected_pairs = {frozenset({r['p1'], r['p2']}): r for r in rows
                        if (r['aspect_name'] != 'Aversion' or _sahl_body_row(r)) and _is_connected(r)}

    def _connected(a, b):
        return frozenset({a, b}) in connected_pairs

    def _applies_to(a, b):
        """a is CONNECTING WITH b in Sahl's own directed sense: "a light,
        quick star GOING STRAIGHTAWAY TO a heavy star ... as long as the
        planet is GOING TOWARDS the [other] planet" (6). Separating is his
        separate term (22), so it does not satisfy "connecting with"."""
        r = connected_pairs.get(frozenset({a, b}))
        return (r is not None and r['motion'] == 'Applying'
                and (r['applicant'] or r['light_name']) == a)

    # 56 and 57 both name THE MOON, and both are restricted to her. 58's
    # subsequent "the Moon or the lord of the Ascendant" governs 58, not
    # the two paragraphs before it -- an earlier version generalised them
    # to every planet on the strength of that later sentence, which is the
    # weaker reading and was flagged as such at the time.
    for planet in ('Moon',):
        own_sign = get_zodiac_sign(planetary_data[planet]['longitude'])
        lords = {SIGN_TO_DOMICILE.get(own_sign)} | {
            p for p, s in EXALTATIONS.items() if s[0] == own_sign}
        lords.discard(None)
        lords.discard(planet)
        for middle in planetary_data:
            if middle in (planet, 'North Node') or middle in lords:
                continue          # middle == the lord is plain 49-52, not 56
            if not _applies_to(planet, middle):
                continue
            for lord in sorted(lords):
                if lord in planetary_data and _applies_to(middle, lord):
                    results.append({
                        'Receiver': lord, 'Received': planet,
                        'Direction': f'Received at one remove, via {middle} (56)',
                        'Via': f"lord of {own_sign}", 'Grade': 'Indirect reception (56)',
                        'Mode': 'By connection',
                    })

    # --- 57: reception, or undermining, after the sign change ---------
    # "And if the Moon was EMPTY IN COURSE, and then she PASSED OVER INTO
    # THE NEXT SIGN and connected with the lord of her first sign (or its
    # exaltation), IT IS JUST LIKE RECEPTION; and if she connected with a
    # planet OTHER than the lord of her first sign or its exaltation, IT
    # UNDERMINES HER." Both halves are reported: the second is a finding,
    # not the absence of one.
    if sim is not None:
        for planet in ('Moon',):
            if planet not in sim['events']:
                continue
            exits = sim['events'][planet]['sign_exits']
            if not exits:
                continue
            ingress = exits[0]
            # "EMPTY IN COURSE" is prospective, not a snapshot: no
            # perfection completes before she leaves the sign she is in.
            # The previous test asked only whether she was connected to
            # anything right now, which is Sahl's looser sense at 63 and
            # not what 57 needs.
            empty = True
            for other in planetary_data:
                if other in (planet, 'North Node'):
                    continue
                tgt = _configuration_target_at(sim, planet, other, 0.0)
                if tgt is None:
                    continue
                if _perfection_day(sim, planet, other, tgt, before_day=ingress) is not None:
                    empty = False
                    break
            if not empty:
                continue
            # And the search window is the NEXT SIGN ONLY -- "she passed
            # over into the next sign and connected with ..." An unbounded
            # search after the ingress could return a connection several
            # signs and months later and label it "after the sign change".
            second_exit = next((d for d in exits if d > ingress), sim['horizon_days'])
            first_lord = SIGN_TO_DOMICILE.get(get_zodiac_sign(planetary_data[planet]['longitude']))
            exalted = next((p for p, s in EXALTATIONS.items()
                             if s[0] == get_zodiac_sign(planetary_data[planet]['longitude'])), None)
            wanted = {first_lord, exalted} - {None, planet}
            best, best_day = None, None
            for other in planetary_data:
                if other in (planet, 'North Node'):
                    continue
                target = _configuration_target_at(sim, planet, other, ingress + 0.05)
                if target is None:
                    continue
                day = _perfection_day(sim, planet, other, target,
                                       after_day=ingress, before_day=second_exit)
                if day is not None and (best_day is None or day < best_day):
                    best, best_day = other, day
            if best is None:
                continue
            if best in wanted:
                results.append({
                    'Receiver': best, 'Received': planet,
                    'Direction': f'Just like reception, after the sign change (57)',
                    'Via': 'lord of the sign it left',
                    'Grade': f'Reached on day {best_day:.0f}', 'Mode': 'By connection',
                })
            else:
                results.append({
                    'Receiver': best, 'Received': planet,
                    'Direction': 'UNDERMINED after the sign change (57)',
                    'Via': f"connects with {best}, not the lord of the sign it left",
                    'Grade': f'Reached on day {best_day:.0f}', 'Mode': 'By connection',
                })
    if sahl and results:
        # REFUSAL WINS (decision D-2, 2026-09-08; scope settled from the
        # text the same day). Sahl's profile only -- Abu Ma'shar's Figure
        # 143 reads the same configurations as favor (VII.5, 126-128).
        #
        # Kind II (59-60), the connection made FROM the receiver's fall:
        # "like one who comes to it from the house of its enemies, NOT
        # ACCEPTING IT nor approaching it." A refusal, so the reception the
        # same pair would otherwise earn is not listed. It can only ever be
        # a minor one (triplicity with bound, 54-55): no planet has its
        # house or exaltation in the sign of its own fall. Sahl's own
        # chart: Mercury leaving Gemini "was connecting with Mars, and he
        # does not accept [Mercury]" (Questions Ch. 1, 63; fn. 27 -> Ch. 1,
        # 40, "connecting with Mars from Cancer"), although Mars is
        # Cancer's night triplicity lord and holds its first bound; and
        # Ch. 3, 51 on the contrary of reception: "he does not acknowledge
        # it, he does not accept it."
        #
        # Kind IV (62), the receiver in ITS OWN fall, is worded as a
        # diminution, not a refusal: "it brings it down and diminishes what
        # comes to it from that." The receiver may hold its house or
        # exaltation at the applicant's place (Venus in Virgo receiving the
        # Moon from Taurus), and 49's "perfect reception" is not revoked by
        # 62 -- so the row stays, marked brought down.
        #
        # Kind III (61) refuses too (decision D-22, 2026-09-08). The
        # applicant stands in its OWN fall and the receiver holds no house
        # or exaltation there: "it will not see it as fit for anything, as
        # though the one asking is offering defeat, and it will not be
        # recognized" (Ch. 3, 61), and in Sahl's other work "it DOES NOT
        # ACCEPT THEM ... his sought matter will not be accomplished"
        # (Questions Ch. 1, 41). Those are Kind II's verbs -- "not
        # recognized", "does not accept" -- not Kind IV's "brings it down",
        # so it suppresses rather than annotates. What it can suppress is
        # only ever minor: 61's own parenthesis exempts house and
        # exaltation, leaving the triplicity (50) with or without the bound
        # (54-55). Dykes' fn. 22 on Questions 1, 41 reads the exemption
        # wider -- "any dignity" -- on which Kind III would not fire here at
        # all; 61's parenthesis is followed instead, and the disagreement is
        # recorded in 13_open_decisions.md under D-22.
        non = evaluate_non_reception(planetary_data, sect)
        refused = {(r['Connecting'], r['With']) for r in non
                   if str(r['Kind']).startswith(('II ', 'III '))}
        brought_down = {(r['Connecting'], r['With']) for r in non if str(r['Kind']).startswith('IV ')}
        kept = []
        for r in results:
            pair = (r.get('Received'), r.get('Receiver'))
            if pair in refused:
                continue
            if pair in brought_down:
                r = {**r, 'Grade': f"{r.get('Grade', '')}; brought down, the receiver in its own fall (62)".lstrip('; ')}
            kept.append(r)
        results = kept
    return results

def evaluate_non_reception(planetary_data, sect):
    """Non-reception (Sahl, The Introduction Ch.3, 58-62, Fig. 18): five
    named ways a connection is refused rather than received, using the
    book's own A -> B model (A = the connecting/faster planet, B = the one
    it connects with).

    Kind I (58): B holds no essential-dignity claim (domicile, exaltation,
    triplicity, term, or face) at A's own position -- "B is alien in A's
    sign." Not recognized, not received.

    Kind II (59-60): A is in B's own sign of fall -- "like one who comes
    to it from the house of its enemies." Confirmed against Sahl's own
    five examples (Aries->Saturn, Cancer->Mars, Virgo->Venus, Capricorn->
    Jupiter, Libra->Sun) -- all exactly A-in-B's-fall.

    Kind III (61): A is in A's OWN fall, and B holds no share -- house or
    exaltation ONLY, per 61's own parenthetical ("that is, by house or
    exaltation") -- at A's position. Narrower than Kind I's test (which
    also allows triplicity/term/face to count): a self-fall specifically
    needs A's two major dignities, not a minor one, to rescue it -- "as
    though the one asking is offering defeat."

    Kind IV (62): B is in B's OWN fall -- brings the connection down
    regardless of A's own condition.

    Kind V (62): B sits in A's own sign of fall -- the planet A is
    connecting with has landed in the very sign that would ruin A."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
        results = []

        for r in rows:
            if (r['aspect_name'] == 'Aversion' and not _sahl_body_row(r)) or not _is_connected(r):
                continue
            # A is "the connecting planet" (58: "if the Moon or the lord of the
            # Ascendant CONNECTED WITH a planet"), which is the directed
            # applicant, not the standing lighter one. Reception already keys
            # this way; keying non-reception the other way made the two
            # disagree on the ~3.6% of pairs where the heavier planet is the
            # one closing.
            a, b = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']
            a_lon, b_lon = planetary_data[a]['longitude'], planetary_data[b]['longitude']
            a_sign, b_sign = get_zodiac_sign(a_lon), get_zodiac_sign(b_lon)
            a_rulers = get_essential_rulers(a_lon)
            b_alien_in_a_sign = b not in (a_rulers['domicile'], a_rulers['exaltation'], a_rulers[triplicity_key], a_rulers['term'], a_rulers['face'])
            b_no_major_share_in_a_sign = b not in (a_rulers['domicile'], a_rulers['exaltation'])
            a_in_own_fall = a_sign in FALLS.get(a, [])
            b_in_own_fall = b_sign in FALLS.get(b, [])
            a_in_b_fall = a_sign in FALLS.get(b, [])
            b_in_a_fall = b_sign in FALLS.get(a, [])

            if b_alien_in_a_sign:
                results.append({'Kind': 'I (58)', 'Connecting': a, 'With': b})
            if a_in_b_fall:
                results.append({'Kind': 'II (59-60)', 'Connecting': a, 'With': b})
            if a_in_own_fall and b_no_major_share_in_a_sign:
                results.append({'Kind': 'III (61)', 'Connecting': a, 'With': b})
            if b_in_own_fall:
                results.append({'Kind': 'IV (62)', 'Connecting': a, 'With': b})
            if b_in_a_fall:
                results.append({'Kind': 'V (62)', 'Connecting': a, 'With': b})

        return results

# --- Prenatal Lunation (Syzygy) — Abbasid / Medieval Method --------------

def get_house_number(longitude, cusps):
    """Given a longitude and 12 quadrant house cusps (in house-1..house-12
    order, as returned by swe.houses), return which house (1-12) it falls
    in. Each house spans from its own cusp forward to the next cusp."""
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        span = (end - start) % 360
        rel = (longitude - start) % 360
        if rel < span:
            return i + 1
    return 12

# Ptolemy's five-degree rule, in Sahl's own words. Fifty Aphorisms #44,
# 87-89: "the planet will NOT BE FALLING FROM THE STAKE unless it was 5
# degrees distant from its rear: I mean, if the stake was 10 degrees of
# Aries, then indeed every planet which has less than 5 degrees between it
# and the stake, is truly counted as BEING IN THE STAKE. And every planet
# which was in more than 5 degrees [from it] is not counted as being in the
# stake." Dykes' note there names it as Ptolemy's rule, "where the power of
# the stake or angle extends by 5 degrees beyond the cusp -- as measured in
# diurnal motion, hence Sahl's reference to the 'rear' of the stake."
#
# Sahl states it a second time, in a different work: "the planets will not
# fall from the stakes except after 5 degrees, and the planets do not become
# powerful in the sign [they are in] until they travel 5 degrees in it"
# (On Nativities Ch.1.22, 9, whose own footnote cross-references Aphorism
# #44). Two independent witnesses to the same rule.
FIVE_DEGREE_CARRYOVER = 5.0
ANGLE_CUSP_INDICES = (0, 3, 6, 9)  # the four stakes, in swe.houses order
# The carry-over applies at the FOUR STAKES ONLY. The owner's canon of
# 2026-09-11 (OWNER_RULING_PLACES_VS_DYNAMICS): the five-degree rule is a
# DYNAMICS rule and nothing else -- a planet that has passed one of the four
# axial degrees (Asc, MC, Dsc, IC) by 0 to 5 degrees inclusive keeps the
# stake's strength; it never applies at the eight intermediate cusps, never
# moves a planet between whole-sign places, never touches aspects, and Lots
# have no dynamic angularity. Sahl states it for the stakes twice (Aphorism
# #44, 88; On Nativities 1.22, 9); 1.18, 19 -- "if there were 5 degrees
# between a planet and the degree of the Ascendant from behind it ... its
# strength will be in the Ascendant, and it will be fit for releasing; and
# likewise in all of the houses" -- is READ AS THE FOUR STAKES, the course's
# reading (Lesson 3 §4-5; Glossary s.v. Angles, succeedents, cadents), not
# as an all-cusps form. The `five_degree_all_cusps` preference that offered
# the all-cusps form was retired the same day; the constant stays for the
# `angles_only` parameter's default and is no longer a reading.
FIVE_DEGREE_ALL_CUSPS = False

def get_effective_house(longitude, cusps, angles_only=None):
    """Quadrant house with the five-degree carryover applied: a planet
    within 5 degrees before a cusp is counted as already in that house.

    MEASURED IN ECLIPTIC LONGITUDE, BY CHOICE. Dykes' note on Fifty
    Aphorisms #44 says the five degrees are reckoned "AS MEASURED IN
    DIURNAL MOTION, hence Sahl's reference to the 'rear' of the stake" --
    that is, along the diurnal circle, not in zodiacal degrees. The two
    coincide only near the equinoctial points and diverge with latitude
    and with the obliquity of the rising sign. The oblique-ascension
    geometry exists in this file (_oblique_ascension, decision D-1) and is
    not used here: the five degrees stay in longitude, a proxy named as
    one wherever it is reported (the owner's ruling of 2026-09-11 keeps
    the proxy and its label). It affects Sahl 83 and Abu Ma'shar 39 and 42,
    and the releaser's places. Measured from the axial DEGREE, not "the
    last five degrees of the preceding sign": Ascendant 10 Aries, planet 28
    Pisces is 12 degrees away and not in the stake.

    Two of Sahl's three statements are about the stakes (Aphorism #44, 88;
    On Nativities 1.22, 9), and the transitions they describe (12th into
    1st, 3rd into 4th, 6th into 7th, 9th into 10th) are the cadent-to-
    angular ones, which is why the rule is phrased as not FALLING from the
    stake. The third, On Nativities 1.18, 19, ends "and likewise in all of
    the houses": 1.18, 19's "likewise in all of the houses" is read as the
    four stakes (the course's reading, adopted as canon 2026-09-11).
    angles_only defaults to True via FIVE_DEGREE_ALL_CUSPS; the all-cusps
    form is no longer offered as a reading.

    get_house_number() is deliberately left alone and still returns strict
    cusp membership. The two are separate facts and both are kept."""
    if angles_only is None:
        angles_only = not FIVE_DEGREE_ALL_CUSPS
    raw = get_house_number(longitude, cusps)
    next_idx = raw % 12                       # cusp that ENDS the raw house
    if angles_only and next_idx not in ANGLE_CUSP_INDICES:
        return raw
    to_next_cusp = (cusps[next_idx] - longitude) % 360.0
    if to_next_cusp <= FIVE_DEGREE_CARRYOVER:
        return next_idx + 1
    return raw

def get_wsh_house(longitude, ascendant_lon):
    """Whole Sign House: the Ascendant's sign is house 1 in its entirety,
    and each subsequent sign (in zodiacal order) is the next house — no
    quadrant cusp division within a sign."""
    asc_sign_idx = int((ascendant_lon % 360.0) // 30)
    target_sign_idx = int((longitude % 360.0) // 30)
    return ((target_sign_idx - asc_sign_idx) % 12) + 1

def get_essential_rulers(longitude):
    """Look up the classical essential dignities (domicile, exaltation,
    triplicity, term, face) ruling an arbitrary zodiacal degree — not tied
    to any specific planet's own position, unlike evaluate_essential_
    dignities(). Used to profile the prenatal syzygy degree itself."""
    longitude = longitude % 360.0
    sign = get_zodiac_sign(longitude)
    degree_in_sign = longitude % 30
    element = SIGN_ELEMENT[sign]
    triplicity = TRIPLICITY[element]
    term_lord = next((lord for limit, lord in EGYPTIAN_TERMS.get(sign, []) if degree_in_sign < limit), '-')
    face_lord = CHALDEAN_ORDER[int(longitude // 10) % 7]
    return {
        'sign': sign,
        'domicile': SIGN_TO_DOMICILE.get(sign, '-'),
        'exaltation': SIGN_TO_EXALTATION.get(sign, '-'),
        'triplicity_day': triplicity['Day'],
        'triplicity_night': triplicity['Night'],
        # Virgo's partner is Mercury "in preference to" Mars -- Gr. Intr. V.14,
        # 7 with Figure 53 (Gr. Intr.) and fn 100; Taurus and Capricorn keep Mars.
        'triplicity_participating': 'Mercury' if sign == 'Virgo' else triplicity['Participating'],
        'term': term_lord,
        'face': face_lord,
    }

def _sun_moon_signed_offset(jd, target_deg):
    """Sun/Moon longitudes and speeds at jd, plus the signed angular offset
    of (Moon - Sun) from target_deg, normalized to (-180, 180]. Positive
    means (Moon - Sun) has already passed target_deg going forward."""
    sun_res = swe.calc_ut(jd, swe.SUN)[0]
    moon_res = swe.calc_ut(jd, swe.MOON)[0]
    sun_lon, sun_speed = sun_res[0], sun_res[3]
    moon_lon, moon_speed = moon_res[0], moon_res[3]
    diff = (moon_lon - sun_lon) % 360
    offset = (diff - target_deg + 180) % 360 - 180
    rel_speed = moon_speed - sun_speed
    return sun_lon, moon_lon, offset, rel_speed

@st.cache_data(max_entries=32, show_spinner=False)
def calculate_prenatal_syzygy(jd_natal, lat, lon, natal_houses):
    """Find the most recent New or Full Moon before birth (the 'prenatal
    syzygy'), following the Abbasid/medieval method:

    - If the Moon is less than 180° ahead of the Sun at birth, the preceding
      syzygy was a conjunction (Coniunctio) — the birth is 'Conjunctional'.
    - Otherwise it was an opposition (Praeventio) — the birth is
      'Preventional', and the Syzygy degree is taken from whichever
      luminary was above the horizon at that prenatal Full Moon: Sahl, On
      Nativities 1.7, 2, "if it was after the opposition, then take the
      portion of whichever of the two luminaries was above the earth"
      (stated there for the Ascendant's degree; fn 33: the portion is the
      degree; Dykes's comment fixes "above the earth" at the lunation's
      moment). When both or neither is above the earth the Moon's degree
      is taken -- the engine's choice, no text says (FINAL-A6, 2026-09-11;
      the line here said "per medieval practice" and cited nothing).

    The exact moment is located by a Newton-style root search on the
    Sun/Moon ephemeris (not just an average-synodic-month estimate), then
    the resulting degree is profiled for essential dignities and placed
    into the natal Whole Sign houses (anchored to the natal Ascendant).
    """
    sun_lon0 = swe.calc_ut(jd_natal, swe.SUN)[0][0]
    moon_lon0 = swe.calc_ut(jd_natal, swe.MOON)[0][0]
    diff0 = (moon_lon0 - sun_lon0) % 360

    if diff0 < 180.0:
        target = 0.0
        event_type = 'Conjunctional'
        event_label = 'Conjunctional (New Moon)'
    else:
        target = 180.0
        event_type = 'Preventional'
        event_label = 'Preventional (Full Moon)'

    # Initial guess via the average relative Moon-Sun speed (~12.19 deg/day),
    # then refine with Newton's method against the true ephemeris speed.
    AVG_REL_SPEED = 12.19075
    delta_back_deg = (diff0 - target) % 360
    jd_guess = jd_natal - delta_back_deg / AVG_REL_SPEED

    sun_lon, moon_lon = sun_lon0, moon_lon0
    for _ in range(15):
        sun_lon, moon_lon, offset, rel_speed = _sun_moon_signed_offset(jd_guess, target)
        if abs(offset) < 1e-6:
            break
        if abs(rel_speed) < 1e-6:
            rel_speed = AVG_REL_SPEED
        jd_guess -= offset / rel_speed

    jd_syzygy = jd_guess

    # Ascendant/houses at the syzygy moment (same natal location), needed
    # to determine (a) which luminary was above the horizon for a
    # Preventional birth, and (b) the sect of the syzygy chart itself for
    # triplicity assignment.
    # Above the horizon by ALTITUDE (_sin_altitude), from each luminary's
    # full ecliptic position at the syzygy moment; the ecliptic proxy this
    # replaced could invert near the poles and, for the Moon, whose
    # ecliptic latitude reaches five degrees, within a few degrees of the
    # horizon at any latitude (fixed 2026-09-08, with the chart's sect).
    _, ascmc_syzygy = swe.houses(jd_syzygy, lat, lon, b'B')
    obliquity_syzygy = swe.calc_ut(jd_syzygy, swe.ECL_NUT)[0][0]
    sun_res = swe.calc_ut(jd_syzygy, swe.SUN)[0]
    moon_res = swe.calc_ut(jd_syzygy, swe.MOON)[0]
    sun_above_horizon = _sin_altitude(sun_res[0], sun_res[1], sun_res[2], obliquity_syzygy, ascmc_syzygy[2], lat) > 0.0
    moon_above_horizon = _sin_altitude(moon_res[0], moon_res[1], moon_res[2], obliquity_syzygy, ascmc_syzygy[2], lat) > 0.0
    is_diurnal_syzygy = sun_above_horizon

    if event_type == 'Conjunctional':
        syzygy_lon = sun_lon  # sun_lon == moon_lon at convergence
    else:
        if sun_above_horizon and not moon_above_horizon:
            syzygy_lon = sun_lon
        elif moon_above_horizon and not sun_above_horizon:
            syzygy_lon = moon_lon
        else:
            syzygy_lon = moon_lon  # ambiguous/edge case: default to the Moon

    natal_house = get_wsh_house(syzygy_lon, natal_houses[0])
    rulers = get_essential_rulers(syzygy_lon)

    active_triplicity_lord = rulers['triplicity_day'] if is_diurnal_syzygy else rulers['triplicity_night']
    active_triplicity_label = 'Day' if is_diurnal_syzygy else 'Night'

    # Almuten / Syzygy Lord: weighted score across the essential dignities
    # ruling this degree (only the sect-appropriate triplicity lord counts,
    # not the Participating ruler, matching standard almuten scoring).
    scores = {}
    def _add_score(planet, pts):
        if planet and planet != '-':
            scores[planet] = scores.get(planet, 0) + pts
    _add_score(rulers['domicile'], ESSENTIAL_DIGNITY_WEIGHTS['domicile'])
    _add_score(rulers['exaltation'], ESSENTIAL_DIGNITY_WEIGHTS['exaltation'])
    _add_score(active_triplicity_lord, ESSENTIAL_DIGNITY_WEIGHTS['triplicity'])
    _add_score(rulers['term'], ESSENTIAL_DIGNITY_WEIGHTS['term'])
    _add_score(rulers['face'], ESSENTIAL_DIGNITY_WEIGHTS['face'])
    almuten = max(scores, key=scores.get) if scores else '-'
    almuten_score = scores.get(almuten, 0)

    return {
        'jd_syzygy': jd_syzygy,
        'event_type': event_type,
        'event_label': event_label,
        'syzygy_longitude': syzygy_lon,
        'sect_diurnal': is_diurnal_syzygy,
        'natal_house': natal_house,
        'rulers': rulers,
        'active_triplicity_lord': active_triplicity_lord,
        'active_triplicity_label': active_triplicity_label,
        'almuten': almuten,
        'almuten_score': almuten_score,
    }

# --- Planetary Day & Hour (Chronocrats) ----------------------------------

DAY_LORD_BY_WEEKDAY = {0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 4: 'Venus', 5: 'Saturn', 6: 'Sun'}  # Python's date.weekday(): Monday=0..Sunday=6
# The Chaldean order of the planetary hours is the standing weight order,
# heaviest first -- the same list, under the name the chronocrator doctrine
# uses for it.
CHALDEAN_HOUR_ORDER = WEIGHT_ORDER

class _CircumpolarSunError(Exception):
    """Raised when swe.rise_trans reports no sunrise/sunset event exists
    for this date/location (res == -2: the Sun is circumpolar — polar day
    or polar night)."""
    pass

def _find_sun_event(jd_start, lat, lon, want_rise):
    """Wraps swe.rise_trans to find the next sunrise/sunset at or after
    jd_start. Signature confirmed directly against a real pyswisseph
    install (20230604): rise_trans(tjdut, body, rsmi, geopos, atpress=0.0,
    attemp=0.0, flags=FLG_SWIEPH) -> (res, tret), tret[0] = JD of event.
    res == -2 means the body is circumpolar (no event that day) -- this is
    a real condition for extreme-latitude locations, not just a hypothetical."""
    rsmi = swe.CALC_RISE if want_rise else swe.CALC_SET
    geopos = (lon, lat, 0.0)
    res, tret = swe.rise_trans(jd_start, swe.SUN, rsmi, geopos)
    if res != 0:
        raise _CircumpolarSunError(
            f"No {'sunrise' if want_rise else 'sunset'} event found near jd={jd_start:.4f} "
            f"at lat={lat}, lon={lon} (res={res}) — the Sun is circumpolar there on this date."
        )
    return tret[0]

def _weekday_from_jd(jd_ut, utc_offset_hours):
    """Local weekday (Monday=0, matching DAY_LORD_BY_WEEKDAY) taken from the
    Julian Day rather than from datetime.weekday().

    This matters for every chart before the Gregorian reform. The chart is
    computed with swe.JUL_CAL for pre-1582 dates, so the same digits denote
    a Julian-calendar date -- but datetime.weekday() reads those digits as
    PROLEPTIC GREGORIAN, and the two calendars had drifted ten days apart by
    1582. For 1582-10-04, a Thursday in the Julian calendar, datetime says
    Monday: a three-planet error in the Lord of the Day, and through the
    Chaldean order an error in the Lord of the Hour as well.

    The Julian Day count is continuous across the reform and knows nothing
    of either calendar, so it is the reliable source. The weekday wanted is
    the LOCAL one, so the UT day is shifted by the local offset first."""
    return int(math.floor(jd_ut + (utc_offset_hours / 24.0) + 0.5)) % 7

@st.cache_data(max_entries=32, show_spinner=False)
def calculate_chronocrats(jd_utc, lat, lon, local_hour, utc_offset_hours=0.0):
    """Planetary Day (from the astrological day, which begins at Sunrise —
    not the calendar weekday) and Planetary Hour (from the unequal/temporal
    hour system, bracketed by real sunrise/sunset times for this date and
    location). Falls back to calendar weekday + equal 2-hour divisions if
    the location has no sunrise/sunset that day (circumpolar)."""
    approximate = False
    try:
        # Bracket the birth moment with the nearest sunrise/sunset before
        # and after it. Forward-search from jd_utc for the "after" events,
        # then forward-search from just under 1.2 days before each "after"
        # event to find the immediately preceding one (a safe margin:
        # consecutive solar events are ~1.0 day apart, so 1.2 days
        # guarantees we land on exactly the previous one, not two cycles back).
        sunrise_after = _find_sun_event(jd_utc, lat, lon, True)
        sunset_after = _find_sun_event(jd_utc, lat, lon, False)
        sunrise_before = _find_sun_event(sunrise_after - 1.2, lat, lon, True)
        sunset_before = _find_sun_event(sunset_after - 1.2, lat, lon, False)

        # The astrological day strictly begins at Sunrise, not midnight. A
        # birth between midnight and sunrise still belongs to the PRECEDING
        # day's astrological date — e.g. 3:00 AM Wednesday is still ruled
        # by Tuesday's Day Lord. Step the local clock backward by the exact
        # elapsed time since the most recent sunrise to sample the correct
        # weekday.
        time_since_sunrise = jd_utc - sunrise_before
        day_lord = DAY_LORD_BY_WEEKDAY[_weekday_from_jd(jd_utc - time_since_sunrise, utc_offset_hours)]

        is_diurnal_hour = sunrise_before > sunset_before
        if is_diurnal_hour:
            period_start, period_end = sunrise_before, sunset_after
        else:
            period_start, period_end = sunset_before, sunrise_after

        temporal_hour = (period_end - period_start) / 12.0
        elapsed = jd_utc - period_start
        hour_number = int(elapsed / temporal_hour) + 1 if temporal_hour > 0 else 1
        hour_number = min(max(hour_number, 1), 12)

        # The 24 planetary hours (12 day + 12 night) are one continuous
        # cycle of 7, starting with the Day Lord at day-hour 1; night-hour
        # 1 is the 13th step in that same cycle.
        cycle_offset = (hour_number - 1) if is_diurnal_hour else (12 + hour_number - 1)
    except _CircumpolarSunError:
        # No real sunrise or sunset exists here on this date (polar day or
        # polar night). The temporal hour is DEFINED by the interval
        # between them, so it has no value at all in that case -- there is
        # no canonical technique to fall back on, and none of the sources
        # in hand contemplates the situation.
        #
        # What is returned is an explicitly modern approximation, flagged
        # as such: the civil day divided into 24 equal hours, continuing
        # the same Chaldean 7-cycle. An earlier version wrote
        # `min(hour // 2, 11)` -- twelve two-hour bins, so the cycle
        # advanced twelve steps across the day where the temporal-hour
        # branch above advances twenty-four. It did cover the whole day,
        # but at half the rate, so it was not "continuing the same 7-cycle"
        # as its comment claimed: the same civil moment landed on a
        # different lord depending on which branch had run.
        approximate = True
        day_lord = DAY_LORD_BY_WEEKDAY[_weekday_from_jd(jd_utc, utc_offset_hours)]
        cycle_offset = int(local_hour)        # 0-23, one step per civil hour

    start_index = CHALDEAN_HOUR_ORDER.index(day_lord)
    hour_lord = CHALDEAN_HOUR_ORDER[(start_index + cycle_offset) % 7]

    return {
        'Day Lord': day_lord, 'Hour Lord': hour_lord, 'Approximate': approximate,
        'Hour Basis': 'Equal civil hours (modern approximation; the Sun is '
                       'circumpolar here, so the temporal hour is undefined)'
                       if approximate else 'Temporal (unequal) hours',
    }

# --- Classical Lots (Arabic Parts) ---------------------------------------

def calculate_classical_lots(asc, sun, moon, sect):
    """The four Lots this app has always shown. Fortune and Exaltation are
    attested in Sahl; Spirit is named by Sahl but its formula is the course
    tables'. All three are computed from their own LOT_DEFINITIONS rows,
    which carry the provenance, so this table cannot disagree with the
    Topical Lots table below it.

    BASIS IS NOT. No Lot of Basis appears anywhere in the material this
    project has -- not in On Nativities, not in the Introduction, not in
    Abu Ma'shar Book VII -- and the construction below is a Hellenistic one
    from outside those texts. It also takes the UNSIGNED shorter arc
    between Fortune and Spirit, which discards the direction the pair
    actually stands in, so the same figure is produced whether Spirit
    leads Fortune or trails it. It is left computed and shown, because it
    has been in this table from the start, but it is marked as
    unattested here rather than presented as settled."""
    luminaries = {'Sun': {'longitude': sun}, 'Moon': {'longitude': moon}}
    fortune = lot_by_id('fortune', luminaries, asc, None, sect)
    spirit = lot_by_id('spirit', luminaries, asc, None, sect)
    exaltation = lot_by_id('exaltation', luminaries, asc, None, sect)

    raw_dist = abs(fortune - spirit)
    dist = raw_dist if raw_dist <= 180.0 else 360.0 - raw_dist
    basis = (asc + dist) % 360.0

    lots = {
        'Lot of Fortune': fortune,
        'Lot of Spirit': spirit,
        'Lot of Exaltation': exaltation,
        'Lot of Basis': basis,
    }
    # Standing is read from LOT_DEFINITIONS, the one place each Lot's
    # provenance is stated, so this table cannot disagree with the Topical
    # Lots table below it (it did: Spirit's formula is the course tables',
    # not Sahl's, and this string still said "attested in Sahl").
    standing_by_id = {d['id']: d['confidence'] for d in LOT_DEFINITIONS}
    classical_ids = {'Lot of Fortune': 'fortune', 'Lot of Spirit': 'spirit',
                     'Lot of Exaltation': 'exaltation'}
    result = []
    for name, lon_val in lots.items():
        result.append({
            'Lot Name': name,
            'Standing': ('EXTERNAL -- unattested in this corpus' if 'Basis' in name
                          else standing_by_id[classical_ids[name]]),
            'Position': get_degree_string(lon_val),
            'WS place': get_wsh_house(lon_val, asc),
            'Sign Dispositor': SIGN_TO_DOMICILE.get(get_zodiac_sign(lon_val), '-'),
        })
    return result

# --- Topical Lots ---------------------------------------------------------
# Every Lot carries its own provenance. Sahl's Nativities gives many of
# these more than once, with formulas that genuinely conflict, and Dykes'
# apparatus does not silently reconcile them -- so neither does this table.
# His editorial position is recorded on each row, in his own words where he
# states one, and the rivals stay visible beside the default.
#
# Four kinds of case, all of them his:
#
#   SAHL HIMSELF RULES. Of the two sibling Lots: "and they are both
#   applied ... And both of the Lots are correct, SO WORK WITH THEM BOTH
#   TOGETHER" (Ch. 3.11, 1-4). Neither is subordinate.
#
#   DYKES NAMES HIS CHOICE. On the three witnesses to Masha'allah's Lot of
#   enemies (his Fig. 71): "I HAVE USED M HERE, which adopts the 'Hermetic'
#   Lot of necessity ... the problem is that the end of 48 equates it with
#   the Lot of slaves, and that is not true." On the night reversal of the
#   Saturn-Moon Lot: "Paul instructs us to reverse it by night, but Abu
#   Ma'shar says not to. WE SHOULD FOLLOW PAUL."
#
#   DYKES MARKS ONE STANDARD. On children: "this view belongs to
#   Theophilus, whereas THE USUAL CALCULATION (from Jupiter to Saturn by
#   day, and reversed by night) is that of Hermes."
#
#   DYKES ONLY TABULATES. Three Lots for work (his Fig. 63 in Sahl's On
#   Nativities -- not Abu Ma'shar's Fig. 63, the V.22 degrees), after: "Sahl
#   quietly switches to Masha'allah's treatise on Lots ... and now he is
#   substituting another one WITHOUT TELLING US that the formula is
#   different! So we now have three different Lots, ostensibly for the same
#   topic." All three are shown.
#
# NOTE ON THE SOURCE TEXT. Every formula here is taken from the running
# prose or a footnote, never from one of the summary tables. An earlier
# OCR mangled their glyph columns; the current one (read 2026-09-08) has
# Sahl's Fig. 63 (On Nativities, Lots of action or work) reading
# Mercury->Mars, Saturn->Moon and Sun->Saturn, all marked
# (R), so the table agrees with the prose on the bodies and differs only
# in marking the Saturn-Moon Lot reversed where 10.2.5, 1 says "by day
# and night". Where prose and table disagree, the prose is used and the
# disagreement is noted.
#
# A point may be a planet, 'Ascendant', 'cuspN' (the Nth place -- see
# LOT_HOUSE_CUSP), 'lordN' (the domicile lord of the Nth whole-sign house),
# or another Lot by id. Lots that feed other Lots are listed before them.
#
# "The second place", "the ninth" (2.15, 1; Ch. 9, 9): Sahl's Lots count
# houses by sign, and Dykes' note 207 on 4.14 glosses the assets Lot as
# "from the lord of the second to the second". In whole signs the degree of
# the Nth place is the Ascendant's own degree carried into the Nth sign; the
# quadrant cusp is the other reading. Sidebar switch for the rows whose text
# names no construction. ONE ROW DECLARES ITS OWN: the Lot of death's eighth
# is "by equation" (Gr. Intr. VIII.4, 226; VIII.6, 69; VIII.3, 14-15), the
# calculated cusp -- Sahl's 8.6, 1 "the degree of the eighth place" names no
# construction, and an earlier line here cited it for "whole-sign
# throughout", which it does not say (owner, 2026-09-11; see the row).
LOT_HOUSE_CUSP_OPTIONS = ('whole-sign place', 'quadrant cusp')   # the sidebar radio and _lot_point share these
LOT_HOUSE_CUSP = LOT_HOUSE_CUSP_OPTIONS[0]
LOT_DEFINITIONS = [
    dict(id='fortune', topic='Fortune', name='Lot of Fortune',
         start='Sun', end='Moon', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 1.37, 1 (and throughout)',
         confidence='settled',
         note='"The Ascendant of the Moon" (1.37, 1); the Sun-to-Moon formula, reversed at '
              "night, is Dykes' note 494 on 1.37, 3 -- Sahl's own sentence 2 gives an "
              'hour-based construction instead.'),
    dict(id='spirit', topic='Spirit', name='Lot of Spirit',
         start='Moon', end='Sun', project='Ascendant', reverse_at_night=True,
         source='TNAC Handy Tables Lesson 18 (Moon to Sun, Asc, reversed by night); named in Sahl, On Nativities Ch. 11.2, 4-6',
         confidence='attested by name in Sahl; formula from the course tables',
         note='Sahl names it the Lot of the Invisible, later Spirituality (notes on Ch. 9.5, '
              '73 and Ch. 11, 5 -- the chapter preamble -- confirm the identity) but nowhere in the corpus states '
              'the formula; the Moon-to-Sun construction is the Handy Tables\'.'),
    # The night formula is not the day formula reversed: it changes BOTH
    # ends. "By day from the degree of the Sun to the degree of HIS
    # exaltation ... and by night from the degree of the MOON to the degree
    # of HER exaltation" (4.1, 6). The generic reversal produced
    # Asc + (Sun - 33) at night, using the wrong body and the wrong
    # direction, and disagreed with the Classical Lots table two rows above
    # it on every nocturnal chart. reverse_at_night is False because
    # _lot_point already swaps the luminary by sect.
    dict(id='exaltation', topic='Exaltation', name='Lot of Exaltation',
         start='sect_light', end='exaltation_degree', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 4.1, 6 (Theophilus)',
         confidence='settled',
         note='"By day from the degree of the Sun to the degree of his exaltation ... '
              'by night from the degree of the Moon to the degree of her exaltation."'),
    dict(id='assets_lord2', topic='Assets', name='Lot of assets (lord of the 2nd)',
         start='lord2', end='cusp2', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 2.15, 1',
         confidence='attested',
         note='"Count from the lord of the second to the second place, and add on top of '
              'that the degrees of the Ascendant."'),
    dict(id='assets_jupsat', topic='Assets', name='Lot of assets (Jupiter-Saturn)',
         start='Jupiter', end='Saturn', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 2.15, 17',
         confidence='variant',
         note='Sahl gives a second, unrelated formula for the same topic in the same '
              'chapter: "count from Jupiter to Saturn by day, and by night the reverse."'),
    dict(id='siblings_hermes', topic='Siblings', name='Lot of siblings (Hermes)',
         start='Saturn', end='Jupiter', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 3.11, 2',
         confidence='settled, used alongside the other',
         note='"For one who was born by day and night" -- no reversal. Sahl: "both of the '
              'Lots are correct, so work with them both together" (3.11, 4).'),
    dict(id='siblings_valens', topic='Siblings', name='Lot of siblings (Valens)',
         start='Mercury', end='Jupiter', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 3.11, 3',
         confidence='settled, used alongside the other',
         note='"Taken by night and day." Dykes\' note 121 on Ch. 3.11, 3 adds that in Dorotheus '
              'this one is specifically for the NUMBER of siblings.'),
    dict(id='father', topic='Father', name='Lot of the father',
         start='Sun', end='Saturn', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 4.14, 1',
         confidence='settled',
         note='"By day from the Sun to Saturn and by night from Saturn to the Sun."'),
    dict(id='father_burnt', topic='Father', name='Lot of the father (Saturn under the rays)',
         start='Mars', end='Jupiter', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 4.14, 2',
         confidence='conditional -- see the Active column',
         note='"Now if Saturn was under the rays, then count from Mars to Jupiter." This '
              'replaces the ordinary father Lot only while Saturn is actually under the '
              'rays; the row reports whether that condition holds in this chart.'),
    dict(id='mother', topic='Mother', name='Lot of the mother',
         start='Venus', end='Moon', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 4.14 (Dykes' note 198)",
         confidence='attested',
         note='"Taken by day from Venus to the Moon (and by night the contrary), and is '
              'projected from the Ascendant."'),
    dict(id='children_theophilus', topic='Children', name='Lot of children (Jupiter-Saturn, unreversed)',
         start='Jupiter', end='Saturn', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 5.1, 91',
         confidence='variant',
         note='Sahl gives it "by night and by day". The note: "According to Abu Ma\'shar, '
              'this view belongs to Theophilus."'),
    dict(id='children_hermes', topic='Children', name='Lot of children (Jupiter-Saturn, reversed)',
         start='Jupiter', end='Saturn', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 5.1, 91 (Dykes' note 51)",
         confidence='the usual calculation',
         note='"THE USUAL CALCULATION (from Jupiter to Saturn by day, and reversed by '
              'night) is that of Hermes." The only difference from the row above is the '
              'night reversal, which Sahl\'s text omits.'),
    dict(id='children_mercury', topic='Children', name='Lot of children (Mercury-Saturn)',
         start='Mercury', end='Saturn', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 5.1, 92',
         confidence='variant, attribution disputed',
         note='"And according to the method of Hermes, it is taken from Mercury to '
              'Saturn." Sahl assigns this to Hermes; the note on 91 assigns Hermes the '
              'Jupiter-Saturn form instead. The conflict is in the sources.'),
    dict(id='children_timing', topic='Children', name='Lot of the timing of children',
         start='Mars', end='Jupiter', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 5.3, 2 and 8',
         confidence='attested',
         note='A separate Lot for WHEN, not how many: "when Jupiter reaches this Lot in '
              'his course and transit."'),
    dict(id='marriage_men', topic='Marriage', name="Lot of men's marriage",
         start='Saturn', end='Venus', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 223 and Ch. 7.2, 44',
         confidence='settled', note='Stated twice, identically.'),
    dict(id='marriage_women', topic='Marriage', name="Lot of women's marriage",
         start='Venus', end='Saturn', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 224 and Ch. 7.2, 44',
         confidence='settled', note='Stated twice, identically.'),
    dict(id='passion', topic='Marriage', name='Lot of passion (Eros)',
         start='fortune', end='spirit', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 7.1, 141 (Dykes' note 11)",
         confidence='attested',
         note='"The Lot of Eros or love according to Valens, taken by day from Fortune to '
              'Spirit (and reversed at night)." Sahl\'s text says Fortune to the Lot of '
              'the Invisible, which is the Lot of Spirit.'),
    dict(id='chronic_illness', topic='Health', name='Lot of chronic illness',
         start='Saturn', end='Mars', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 6.3.4, 2 and Ch. 6.3.5, 1',
         confidence='settled',
         note='"Taken from Saturn to Mars by day, and by night the contrary." Stated twice.'),
    dict(id='slaves', topic='Slaves', name='Lot of slaves',
         start='Mercury', end='Moon', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 6.10, 20',
         confidence='settled',
         note='"Taken from Mercury to the Moon by day, and by night the reverse."'),
    dict(id='death', topic='Death', name='Lot of death',
         start='Moon', end='cusp8', project='Saturn', reverse_at_night=False,
         # This Lot's eighth degree is "by equation" (Gr. Intr. VIII.4, 226; VIII.6,
         # 69): the calculated cusp, whatever the shared LOT_HOUSE_CUSP switch says
         # for the Lots whose texts name no construction. Owner, 2026-09-11 (decision
         # sheet row 4 / FINAL-A12); the whole-sign carried degree is the row below.
         cusp_rule='quadrant cusp',
         source="Gr. Intr. VIII.4, 226 with fn 128; VIII.6, 69; VIII.3, 11 and 14-15 (\"by equation\"); "
                "Sahl, On Nativities 8.6, 1 as printed, Saturn being Dykes's reading for the MSS' \"Ascendant\" (fn 89)",
         confidence="stated (Gr. Intr. VIII.4, 226; VIII.6, 69); Sahl 8.6, 1 as printed agrees, its manuscripts read "
                    "the Ascendant (fn 89); the eighth's degree \"by equation\" is the Alcabitius cusp -- a declared "
                    "convention, no text naming the algorithm (owner, 2026-09-11)",
         note='"The Lot of death is taken by day and night from the degree of the Moon to the degree of the '
              'eighth house by equation, and to it is added what Saturn has traveled in his sign, and it is '
              'cast out from the beginning of Saturn\'s sign" (Gr. Intr. VIII.4, 226, Hermes\'s Lot, which 228 '
              'calls "more correct" than the Persians\'; VIII.6, 69 the same) -- projection from Saturn\'s degree, '
              'as VIII.3, 11 and fn 36 spell out. Sahl 8.6, 1 as printed: "taken by night and day from the Moon '
              'to the degree of the eighth place, and cast out from Saturn"; that "Saturn" is Dykes\'s emendation '
              'of Sahl\'s manuscripts -- fn 89: "Reading with the Masha\'allah MSS for \'Ascendant\'. This is the '
              'Lot as reported by Dorotheus (Carmen IV.3, 16)" -- so the emendation is a fact about Sahl\'s '
              'transmission, not about the rule. "By equation" is Abu Ma\'shar\'s own word for the cusp (VIII.3, '
              '14: "by counting is one of the signs, and by equation ... another house"; 15\'s example cannot be '
              'produced by a carried Ascendant degree); Sahl\'s "the degree of the eighth place" names no '
              'construction. The Saturn and Ascendant projections differ in sign on about 93% of charts; the '
              'cusp and the carried degree on about 12%.'),
    dict(id='death_ws', topic='Death', name='Lot of death (variant: whole-sign eighth)',
         start='Moon', end='cusp8', project='Saturn', reverse_at_night=False,
         cusp_rule='whole-sign place',
         source="Engine variant of the row above: the eighth's degree as the Ascendant's degree carried seven signs forward",
         confidence="not prescribed in any supplied passage -- Sahl 8.6, 1 leaves the construction unspecified, "
                    "Gr. Intr. VIII.4, 226 prescribes the cusp; shown for comparison (owner, 2026-09-11)",
         note='Same arc and projection as the row above; only the eighth\'s degree differs. Kept as a labelled '
              'variant so the earlier default (whole sign, a builder\'s reading of 2026-09-08) stays visible.'),
    dict(id='killer', topic='Death', name='Lot of the killer',
         start='lord1', end='Moon', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 8.2, 17',
         confidence='attested',
         note='"Taken from the lord of the Ascendant to the Moon by day (and by night the '
              'reverse), and is cast out from the Ascendant."'),
    dict(id='travel', topic='Travel', name='Lot of travel',
         start='lord9', end='cusp9', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 9, 9 (the chapter preamble; restated at 9.3, 4 and 9.4, 37)',
         confidence='settled',
         note='"Taken by night and day from the lord of the ninth to the ninth."'),
    dict(id='work_action', topic='Work', name='Lot of work (action / praxis)',
         start='Mercury', end='Mars', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 10.1.1, 14',
         confidence='variant (one of three)',
         note="The Greek Lot of action. Dykes' Fig. 63 in Sahl's On Nativities names it Work in Sahl and BA, "
              "\"managers, viziers, and Sultans\" in Gr. Intr. VIII.4."),
    dict(id='work_expedition', topic='Work', name='Lot of work (expedition)',
         start='Saturn', end='Moon', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 10.2.5, 1',
         confidence='variant (one of three); Sahl\'s text, unreversed',
         note='Sahl: "Calculate BY DAY AND NIGHT from Saturn to the Moon" -- no reversal, and '
              'Abu Ma\'shar agrees. Dykes\' note prefers Paul ("Paul instructs us to reverse it '
              'by night, but Abu Ma\'shar says not to. We should follow Paul"); the row below '
              'gives that reading, so both are visible.'),
    dict(id='work_expedition_paul', topic='Work', name='Lot of work (expedition, reversed by night -- Paul)',
         start='Saturn', end='Moon', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 10.2.5, 1 (Dykes' note 165)",
         confidence="Dykes' preference against Sahl's text",
         note='Identical to the row above by day; differs only at night.'),
    dict(id='work_authority', topic='Work', name="Lot of authority, work and craft (Masha'allah)",
         start='Sun', end='Saturn', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 10.2.5, 4-14 (Masha'allah); Dykes' fn. 166",
         confidence='variant (one of three); reversed at night by decision D-4 (2026-09-08)',
         note='Sahl switches treatises mid-chapter without saying so, and his text at 10.2.5, 4-14 '
              'gives no formula: the Sun-Saturn identification is Dykes\' fn. 166, Masha\'allah '
              '"defines this in the same way as the Lot of fathers (Sun-Saturn)". The father Lot '
              'reverses at night (4.14, 1) and Sahl\'s Fig. 63 (On Nativities) marks this one (R), '
              'so it reverses here too (synthesis/13_open_decisions.md D-4).'),
    dict(id='friends', topic='Friends', name='Lot of friends',
         start='Moon', end='Mercury', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 11, 5 (the chapter preamble) and Ch. 11.1, 29',
         confidence='settled',
         note='Dykes\' note 72 on Ch. 9.5, 3 identifies it: \"the Moon-Mercury Lot (projected from '
              'the Ascendant, reversed by night), which is identical to Dorotheus\'s Lot '
              'of friendship." In the Ch. 11 preamble the Moon-to-Mercury words are Dykes\' '
              'bracketed supplement; Sahl states the formula in his own words at 11.1, 29.'),
    dict(id='desire', topic='Friends', name='Lot of desire',
         start='fortune', end='spirit', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 11.2, 4-5',
         confidence='attested; identical in form to the Lot of passion',
         note='"By day from the Lot of Fortune to the Lot of Spirituality ... and by night '
              'the converse."'),
    dict(id='necessity', topic='Friends', name='Lot of necessity',
         start='spirit', end='fortune', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 11.4, 18 (Dykes' note 62)",
         confidence='attested',
         note='"This is the opposite of the Lot of Eros: by day from the Lot of Spirit to '
              'the Lot of Fortune (and by night the reverse)."'),
    dict(id='enemies_necessity', topic='Enemies', name='Lot of enemies (M: Mercury to Fortune)',
         start='Mercury', end='fortune', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 12.1, 48 (Dykes' Fig. 71)",
         confidence="Dykes' own choice of the three",
         note='"I HAVE USED M HERE, which adopts the \'Hermetic\' Lot of necessity (from '
              'Mercury to Fortune or \'the Lot of the Moon\', reversed by night). This Lot '
              'does have to do with enmity, but the problem is that the end of 48 equates '
              'it with the Lot of slaves, and that is not true."'),
    dict(id='enemies_slaves', topic='Enemies', name='Lot of enemies (E: Mercury to Moon)',
         start='Mercury', end='Moon', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 12.1, 49 (Dykes' Fig. 71)",
         confidence='variant; really the Lot of slaves',
         note="The second manuscript's reading. Dykes' table names its real identity as the "
              'Lot of slaves, which is why he did not adopt it.'),
    dict(id='enemies_hermes', topic='Enemies', name='Lot of enemies (Latin: lord of the 12th)',
         start='lord12', end='cusp12', project='Ascendant', reverse_at_night=False,
         source="Vat. Pal. lat. 1892, f. 103r (Dykes' Fig. 71)",
         confidence='variant; the Latin witness',
         note="Dykes' table names this one Enemies (Hermes) -- the only one of the three "
              'whose real identity is the topic it is used for.'),
    dict(id='courage', topic='Courage', name='Lot of courage (Hermetic)',
         start='Mars', end='fortune', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 10.3 (Dykes' note 214)",
         confidence='conjectural identification',
         note='"There seem to be two Lots used here ... for either of these the author '
              'might mean the Hermetic Lot of courage: by day from Mars to the Lot of '
              'Fortune (by night the reverse). ... However, I SUSPECT that one of them -- '
              'probably the Lot of valor -- is originally Dorotheus\'s Lot of expedition."'),
    dict(id='deception_men', topic='Deception', name="Lot of men's deception",
         start='Sun', end='Venus', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 220',
         confidence='attested', note='"By day and by night from the Sun to Venus."'),
    dict(id='deception_women', topic='Deception', name="Lot of women's deception",
         start='Moon', end='Mars', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 221',
         confidence='attested', note='"By day and by night from the Moon to Mars."'),
]

def _lot_point(name, planetary_data, asc, cusps, sect, resolved, cusp_rule=None):
    """Resolve one end of a Lot formula to a longitude, or None if the
    chart cannot supply it."""
    if name == 'Ascendant':
        return asc
    if name in planetary_data:
        return planetary_data[name]['longitude']
    if name in resolved:
        return resolved[name]
    if name == 'sect_light':
        return planetary_data['Sun' if sect == 'Diurnal' else 'Moon']['longitude']
    if name == 'exaltation_degree':
        # 4.1, 6 pairs the sect light with ITS OWN exaltation degree: the
        # Sun's is 19 Aries, the Moon's 3 Taurus.
        return 19.0 if sect == 'Diurnal' else 33.0
    if name.startswith('cusp'):
        n = int(name[4:])
        # The shared switch decides, unless the row declares its own rule (the
        # Lot of death: "by equation", Gr. Intr. VIII.4, 226), which wins.
        quadrant = LOT_HOUSE_CUSP == LOT_HOUSE_CUSP_OPTIONS[1]
        if cusp_rule is not None:
            quadrant = cusp_rule == LOT_HOUSE_CUSP_OPTIONS[1]
        if quadrant:
            return cusps[n - 1]
        return (asc + 30.0 * (n - 1)) % 360.0
    if name.startswith('lord'):
        house = int(name[4:])
        sign = get_zodiac_sign(((int(asc // 30) + house - 1) % 12) * 30.0 + 15.0)
        lord = SIGN_TO_DOMICILE.get(sign)
        return planetary_data[lord]['longitude'] if lord in planetary_data else None
    return None

def _lot_longitude(d, planetary_data, asc, cusps, sect, resolved):
    """One LOT_DEFINITIONS row at this chart: (longitude, start, end), or
    None if the chart cannot supply a point. The day formula reverses to
    end -> start at night where the row says so."""
    start, end = d['start'], d['end']
    if d['reverse_at_night'] and sect != 'Diurnal':
        start, end = end, start
    rule = d.get('cusp_rule')
    a = _lot_point(start, planetary_data, asc, cusps, sect, resolved, rule)
    b = _lot_point(end, planetary_data, asc, cusps, sect, resolved, rule)
    p = _lot_point(d['project'], planetary_data, asc, cusps, sect, resolved, rule)
    if a is None or b is None or p is None:
        return None
    return (p + b - a) % 360.0, start, end

def lot_by_id(lot_id, planetary_data, asc, cusps, sect):
    """A single Lot by its LOT_DEFINITIONS id, resolving the rows it feeds
    on first. The one place the chart-level Lot of Fortune and the
    Classical Lots table get their arithmetic -- the formula used to be
    written out three times, and the two Lots tables once disagreed on
    every night chart."""
    resolved = {}
    for d in LOT_DEFINITIONS:
        got = _lot_longitude(d, planetary_data, asc, cusps, sect, resolved)
        if got is not None:
            resolved[d['id']] = got[0]
        if d['id'] == lot_id:
            return resolved.get(lot_id)
    raise KeyError(lot_id)

def calculate_topical_lots(planetary_data, asc, cusps, sect):
    """Every Lot in LOT_DEFINITIONS, computed with its provenance attached.

    A Lot is projected_point + (end - start), and the day formula reverses
    to end -> start at night where the source says so. Lots that feed other
    Lots (Fortune and Spirit feed passion, desire, necessity, courage and
    one of the enemy variants) are resolved in table order."""
    is_diurnal = (sect == 'Diurnal')
    resolved = {}
    rows = []
    for d in LOT_DEFINITIONS:
        got = _lot_longitude(d, planetary_data, asc, cusps, sect, resolved)
        if got is None:
            continue
        lon, start, end = got
        resolved[d['id']] = lon
        arc = 'day' if is_diurnal else 'night'
        active = 'yes'
        if d['id'] == 'father_burnt':
            # Only replaces the ordinary father Lot while Saturn is in fact
            # under the rays (4.14, 2). Shown either way, but the row now
            # says whether its condition holds instead of leaving the
            # reader to check.
            _ph, _sd, _el = solar_phase('Saturn', planetary_data['Saturn']['longitude'],
                                         planetary_data['Sun']['longitude'], planetary_data['Saturn'].get('speed_in_lon'))
            active = 'yes' if _ph in ('Burned', 'Under the rays', 'Cazimi') else 'NO -- Saturn is not under the rays'
        rows.append({
            'Topic': d['topic'],
            'Lot': d['name'],
            'Active': active,
            'Position': get_degree_string(lon),
            'WS place': get_wsh_house(lon, asc),
            'Lord': SIGN_TO_DOMICILE.get(get_zodiac_sign(lon), '-'),
            'Formula': (f"{d['project']} + ({end} - {start})"
                        + ('' if not d['reverse_at_night'] else f'  [{arc} order]')
                        + ((f"  [{d['cusp_rule']}, this Lot's own rule]" if d.get('cusp_rule') else f'  [{LOT_HOUSE_CUSP}]')
                           if 'cusp' in (start, end, d['project']) or start.startswith('cusp') or end.startswith('cusp') else '')),
            'Standing': d['confidence'],
            'Source': d['source'],
            'Editor’s note': d['note'],
        })
    return rows

# --- Coverage: what these sources contain that this file does not ---------
# Named explicitly rather than left as silence, so the absence is a stated
# scope limit and not an implied claim of completeness. Each entry is a
# doctrine present in the corpus and not implemented here.
NOT_IMPLEMENTED_COVERAGE = [
    ("Gr. Intr. VII.5, 29-31", "Priority among several planets connecting from a "
     "single degree and minute, decided by claims in the handing-over sign, with the "
     "bound lord breaking ties. Sentences 29-31 are on pp. 450-451; 32-39 came with the "
     "p. 452 recovery. Computable, not yet built."),
    ("Gr. Intr. VII.5, 38-52", "Connection by LATITUDE, in three kinds -- assembly "
     "at equal latitude with one eclipsing the other, and two further kinds. Recovered "
     "with pp. 452-453. Latitude is available in the chart data but unused for "
     "connection."),
    ("Gr. Intr. VII.5, 67-77, the pairs the notes say he omits", "The natural "
     "connections are built from the sign pairs 56 and 67-75 enumerate. Three pairs "
     "the complete schemes contain are NOT in his lists and are not added: "
     "Aquarius-Scorpio (the antiscia family; 67-75 stops at five pairs), and the "
     "'agreeing in manner' affinities Aries-Scorpio, Taurus-Libra (note 163) and "
     "Aquarius-Capricorn (note 164). Adding them would be inference from the family, "
     "not from the text in hand."),
    ("Gr. Intr. VII.5, 97-100", "Handing over TWO NATURES. The Sahl handing-over "
     "table is not a substitute."),
    ("Gr. Intr. VII.5, 104-116", "The full returning tree, with its suitability and "
     "corruption grades. Only Sahl's two manners (Ch.3, 65-69) are implemented."),
    ("Gr. Intr. VII.6, 13 and 36", "The masculine and feminine DEGREES, alongside "
     "the signs. The table is Fig. 59 (V.19, p. 304 of Abu Ma'shar's volume, in the "
     "corpus since 2026-09-08); fn. 108 there says he takes no stance among three "
     "schemes. Not implemented by decision D-19 (2026-09-08): the table disagrees with "
     "the sign's gender on half the zodiac, the three schemes agree on a third of it, and "
     "reading 'or male degrees' into 13 and 36 would widen a vote the author would not "
     "commit to."),
    ("Sahl, On Questions Ch. 1, 18-20", "ADVANCEMENT MATCHED TO THE NATURE OF THE MATTER: "
     "'if the question was about the nature of retreating, such as travel, moving, a detained "
     "person's exit from his prison, and being released from sorrows, then look for these "
     "matters from the place of retreat and withdrawal.' Stated for questions and never "
     "restated for nativities; testimony 83 stays unconditional (Introduction Ch. 3, 83). "
     "Decision D-14 (2026-09-08): a note, not a topical modifier."),
    ("Sahl, On Questions Ch. 6, 2 and 7.7, 90-101 (Figures 37-41)", "PER-TOPIC REASSIGNMENT "
     "OF THE ANGLES -- 'the Ascendant indicates the doctor, the Midheaven indicates the sick "
     "person, the seventh sign indicates the illness, and the fourth sign indicates the "
     "medicine' -- and a twelve-house scheme for war. Horary, and in tension with the fixed "
     "house meanings of Introduction Ch. 2, 4-29, which no text reconciles. Decision D-17 "
     "(2026-09-08): caveat only; this engine's house meanings are one topic's assignment."),
    ("Gr. Intr. VII.6, 52", "Each planet's OWN nodes (\"their own Dragons\") are read since "
     "2026-09-11 (order GAP-39) from the ephemeris's MEAN nodes within 12 degrees; only the "
     "reading remains -- 52 does not say mean or true, and the chart's Moon's node is the TRUE "
     "one (owner, 2026-09-07), so the two node kinds differ."),
    ("Gr. Intr. VII.3, 2 / VI.26, 3", "The ADVANCING AND WITHDRAWING QUADRANTS as a "
     "condition in its own right (ASC to MC and DSC to IC advancing: primary motion "
     "toward the meridian). Read from the margin of the Figure 90 reshoot and Dykes' "
     "note on On Nativities 10.3; distinct from Sahl 83, which is his own Ch.3, 4. "
     "Recorded as ADVANCING_BY_QUADRANT_FIG90, not yet scored."),
    ("Gr. Intr. VII.5, 32-33", "Mixing of natures BY RAY across a sign boundary "
     "(Fig. 121: Moon 29 59' Aquarius, Saturn's trine ray at 1 Pisces). Only the "
     "body-to-body case of VII.4, 13-14 is reported."),
    ("Sahl, On Nativities Ch. 1.20-1.23", "The RELEASER and HOUSE-MASTER (hyleg and "
     "alcocoden), with 1.20, 2's ranking of the five lords -- \"the lord of the bound, "
     "then the lord of the house, then the lord of the exaltation, then the lord of "
     "the triplicity, then the lord of the image\" -- and the years granted."),
    ("Sahl, On Nativities Ch. 1.18, 20-22", "DISTRIBUTION through the bounds by "
     "ascensions: \"for each degree (of the degrees of ascensions) a year, and for "
     "every 5' a month, and for every 1' six days, and for every 10'' a day.\" The "
     "Timing page's 1 degree/year is labelled as not this."),
    ("Sahl, On Nativities Ch. 2.13, 48-51", "The three 15-degree ASCENSIONAL bands "
     "past a stake, grading good fortune; also Aphorism #45 (misstated there per "
     "Dykes' note 57). The ascensional apparatus now exists (VII.7, decision D-1: "
     "cast_rays_by_ascension and its helpers); neither consumer is built yet."),
    ("Sahl, On Nativities Ch. 2.2", "The THIRTY FIXED STARS for eminence, with "
     "positions for Sahl's epoch (needs precession)."),
    ("Sahl, On Nativities Ch. 2.6 and 4.9", "Uses of the TWELFTH-PARTS beyond the "
     "Moon's (luminaries, Ascendant, infortunes)."),
    ("Sahl, On Nativities: further Lots", "Constitution (1.34, 13, recovered p. 358, "
     "'foundation' uncertain); male/female (3.13, 20); Venus to the 7th place "
     "(7.1, 10 and 145); Sun to Moon projected from Venus (7.4, 8); religion "
     "(9.5, 3, identity disputed); riding animals (12.2 fn. 18)."),
]

# --- Special Degrees & Conditions ----------------------------------------

# Classical "wells" (pitted degrees) by sign, per Abu Ma'shar, The Great
# Introduction to Astrology V.21, Fig. 62 (Dykes translation, p. 308 of Abu
# Ma'shar's own volume -- the pagination is not Sahl's). Ordinal degrees as
# the figure prints them ("the 6th, 11th, 17th ..."); the code tests
# int(lon % 30) + 1 against them. Corrected 2026-09-08 against the owner's
# photographs of V.21 (p. 308), not the OCR capture: Aries gained 29,
# Gemini's 13 became 12, Pisces gained 28; confirmed a third time the same
# day against Fig. 62's own page image, all 64 cells -- PN IV's Figure
# 98 has 62, differing in three (CORPUS_MANIFEST). (The earlier text
# cited Fig. 98, which in Abu Ma'shar's volume is "Speed relative to
# apogee" -- but Persian Nativities IV's Fig. 98 IS the wells table, so
# name the volume before "correcting" this.) Pinned cell by cell in
# tests/test_base_tables.py.
WELLED_DEGREES = {
    'Aries': [6, 11, 17, 23, 29],
    'Taurus': [5, 13, 18, 24, 25, 26],
    'Gemini': [2, 12, 17, 26, 30],
    'Cancer': [12, 17, 23, 26, 30],
    'Leo': [6, 13, 15, 22, 23, 28],
    'Virgo': [8, 13, 16, 21, 25],
    'Libra': [1, 7, 20, 30],
    'Scorpio': [9, 10, 17, 22, 23, 27],
    'Sagittarius': [7, 12, 15, 24, 27, 30],
    'Capricorn': [2, 7, 17, 22, 24, 28],
    'Aquarius': [1, 12, 17, 23, 29],
    'Pisces': [4, 9, 24, 27, 28],
}

# Sahl's two sign categories, stated identically in two works (C-04):
# "of them are signs which are said to be dark, and they are Libra and
# Capricorn" (Introduction Ch. 1, 18; On Nativities 1.38, 8 the same), and
# "a place called the 'burned place,' and it is the end of Libra and the
# beginning of Scorpio" (Introduction Ch. 1, 19; On Nativities 1.38, 9).
# Sahl gives the burned place NO degrees; the 15 Libra-15 Scorpio span
# this app once flagged is in no source in hand, and the 19
# Libra-3 Scorpio span is Abu Ma'shar's own (VII.6, 40, HARSH_BURNED_PATH
# below, used only where the table is his). Decision D-5, 2026-09-08.
DARK_SIGNS = {'Libra', 'Capricorn'}
BURNED_PLACE_SIGNS = ('Libra', 'Scorpio')

# --- Sahl's sign categories where his two works disagree (C-11 / D-7) ----
# One reading per work, never a union: the union is in neither witness
# (synthesis/03_changes.md #2; decision D-7, 2026-09-08). Introduction =
# The Introduction Ch. 1; Nativities = On Nativities Ch. 1.38.
#   Four-footed. Intro 1, 13: "Aries, Taurus, and the beginning of
#   Capricorn, and the end of Sagittarius." Nat. 1.38, 1: "Aries, Leo,
#   Taurus have four feet; and the <first> half of Sagittarius has two
#   feet, and the other has four feet." Leo is in one, Capricorn in the
#   other. Values give the extent of the sign the text names.
FOUR_FOOTED = {
    'Introduction':  {'Aries': 'whole', 'Taurus': 'whole', 'Capricorn': 'the beginning', 'Sagittarius': 'the end'},
    'On Nativities': {'Aries': 'whole', 'Leo': 'whole', 'Taurus': 'whole', 'Sagittarius': 'the second half'},
}
#   Voice. Intro 1, 20-22, three classes; Nat. 1.38, 25-28, four. Virgo
#   is "half a voice" in one and "powerful voice" in the other.
VOICE = {
    'Introduction': {
        'full voice': ['Aries', 'Taurus', 'Gemini', 'Leo', 'Libra', 'Sagittarius'],
        'half a voice': ['Capricorn', 'Aquarius', 'Virgo'],
        'no voice': ['Cancer', 'Scorpio', 'Pisces'],
    },
    'On Nativities': {
        'powerful voice': ['Gemini', 'Virgo', 'Libra'],
        'balanced voice': ['Aries', 'Taurus', 'Leo', 'Sagittarius'],
        'weak voice': ['Capricorn', 'Aquarius'],
        'no voice': ['Cancer', 'Scorpio', 'Pisces'],       # "Cancer and its triplicity"
    },
}
#   Barren. Intro 1, 23: "signs of barrenness, few in children: and they
#   are Aries, Leo, and Virgo." Nat. 1.38, 16: "The barren ones: Leo,
#   Virgo, and Sagittarius"; 17: "Some scholars said that Capricorn and
#   Aquarius are barren" (a reported opinion, kept apart). Many children
#   agrees in both (Intro 1, 24; Nat. 1.38, 14): Cancer, Scorpio, Pisces.
BARREN = {
    'Introduction': ['Aries', 'Leo', 'Virgo'],
    'On Nativities': ['Leo', 'Virgo', 'Sagittarius'],
    'On Nativities (some scholars, 1.38, 17)': ['Capricorn', 'Aquarius'],
}
MANY_CHILDREN = ['Cancer', 'Scorpio', 'Pisces']
SIGN_CATEGORY_SOURCES = {
    'Four-footed': ('Introduction Ch. 1, 13', 'On Nativities 1.38, 1'),
    'Voice': ('Introduction Ch. 1, 20-22', 'On Nativities 1.38, 25-28'),
    'Barren': ('Introduction Ch. 1, 23', 'On Nativities 1.38, 16-17'),
    'Many children': ('Introduction Ch. 1, 24', 'On Nativities 1.38, 14'),
    'Dark': ('Introduction Ch. 1, 18', 'On Nativities 1.38, 8'),
    'Burned place': ('Introduction Ch. 1, 19', 'On Nativities 1.38, 9'),
}

def sign_categories(sign):
    """Every category label a sign carries, one column per work where the
    works disagree, so a reader sees both readings and no merged one."""
    def voice_class(work):
        return next((cls for cls, signs in VOICE[work].items() if sign in signs), '-')
    return {
        'Four-footed (Intro)': FOUR_FOOTED['Introduction'].get(sign, '-'),
        'Four-footed (Nat.)': FOUR_FOOTED['On Nativities'].get(sign, '-'),
        'Voice (Intro)': voice_class('Introduction'),
        'Voice (Nat.)': voice_class('On Nativities'),
        'Barren (Intro)': 'yes' if sign in BARREN['Introduction'] else '-',
        'Barren (Nat.)': ('yes' if sign in BARREN['On Nativities']
                          else 'some scholars' if sign in BARREN['On Nativities (some scholars, 1.38, 17)'] else '-'),
        'Many children (both)': 'yes' if sign in MANY_CHILDREN else '-',
        'Dark (both)': 'yes' if sign in DARK_SIGNS else '-',
        'Burned place, no degrees (both)': 'yes' if sign in BURNED_PLACE_SIGNS else '-',
    }

# --- Dignity orderings, kept apart by context (C-20 / D-8) ---------------
# "the triplicity is below the house, and likewise the bound below the
# triplicity, and the face below the bound" (Questions Ch. 13, 7 -- a
# planet's rank; exaltation is not placed). "the stronger of them is the
# lord of the bound, then the lord of the house, then the lord of the
# exaltation, then the lord of the triplicity, then the lord of the image"
# (On Nativities 1.20, 2 -- house-master selection). Glossary p. 777 lists
# domicile > exaltation > triplicity > bound > face. The bound is first in
# one and third in another; they answer different questions and are never
# merged (decision D-8). VICTOR_WEIGHTS (the almuten) is a fourth thing.
DIGNITY_ORDER = {
    'Questions Ch. 13, 7 (a planet\'s rank)': ['house', 'triplicity', 'bound', 'face'],
    'On Nativities 1.20, 2 (house-master selection)': ['bound', 'house', 'exaltation', 'triplicity', 'image'],
    'Glossary p. 777 (general listing)': ['house', 'exaltation', 'triplicity', 'bound', 'face'],
}

# --- Casting the rays by ascensions: Ptolemy's method as reported by Abu
# Ma'shar (Gr. Intr. VII.7, 1-22) -- decision D-1, 2026-09-08 ----
#
# A STATIC chart quantity: where a planet's sextile, square and trine rays
# fall at the moment of the chart once the ascensions of the birth latitude
# are taken into account, beside the zodiacal aspect VII.5 uses. Nothing
# here advances a point through time. The distributions are implemented
# separately, from Persian Nativities IV (section 3b below, D-3 closed
# 2026-09-10); the RELEASER is still deferred, because PN IV turned out
# not to state how one is chosen (IX.8, 123). VII.7, 1-2 says the
# tradition disagrees and that this is Ptolemy's account ("we will state
# what Ptolemy ... said"), so it is labelled his, not Abu Ma'shar's own.
#
# The chapter presupposes tables it does not give (fn. 250: the hourly
# times, "special tables in the Almagest"; fn. 251: the ascension-to-degree
# inverses), all computable from spherical astronomy and computed here:
# right ascension and declination of an ecliptic degree (swe.cotrans), the
# ascensional difference for the latitude, the oblique ascension RA - AD,
# and the diurnal hourly time (90 + AD) / 6 in degrees of right ascension
# per seasonal hour; the nocturnal hourly time is (90 - AD) / 6, derived
# from the SAME ascensional difference so the two semi-arcs close to 180
# exactly (computing the nocturnal one from the opposite degree is not
# exactly antisymmetric in floating point, and the sliver it left open
# once divided by a zero semi-arc; fixed 2026-09-08).
#
# Domain. The ascension-to-degree inverse is closed-form and unique only
# where every ecliptic degree rises and sets, |latitude| + obliquity < 90.
# Beyond that some degrees are circumpolar, the oblique ascension is not
# injective (at 70N three longitudes share OA = 0 and two of them never
# cross the horizon), and at the critical latitude itself the mapping has a
# flat interval. There _lon_with_oblique_ascension() returns None and the
# rays table says the method does not apply, in the file's [UNCERTAIN --]
# style, rather than printing a fabricated ray. Owner's call to overturn
# (2026-09-08).
#
# One thing the text leaves open: 18 adds the correction to the candidate
# position NEAREST the planet (left rays), 21 to the more DISTANT (right
# rays). Whether that flip is geometry or a copyist's is not said
# (01_abu_mashar_vii_7_to_9.md B5), so cast_rays_by_ascension() takes an
# anchor argument -- 'as written' (the default), 'nearest', 'distant' --
# and the tests hold all three. 22: the opposition needs none of this,
# "in the same degree and minute".
RAY_ASPECTS = (('Left sextile', 60.0), ('Left square', 90.0), ('Left trine', 120.0),
               ('Right sextile', -60.0), ('Right square', -90.0), ('Right trine', -120.0))
RAY_ANCHOR_OPTIONS = ('as written', 'nearest', 'distant')

def _ra_decl(lon, obliquity):
    """Right ascension and declination of an ecliptic degree (latitude 0)."""
    ra, decl, _r = swe.cotrans((lon % 360.0, 0.0, 1.0), -obliquity)
    return ra % 360.0, decl

def _ascensional_difference(decl, geo_lat):
    x = math.tan(math.radians(geo_lat)) * math.tan(math.radians(decl))
    return math.degrees(math.asin(max(-1.0, min(1.0, x))))

def _oblique_ascension(lon, obliquity, geo_lat):
    ra, decl = _ra_decl(lon, obliquity)
    return (ra - _ascensional_difference(decl, geo_lat)) % 360.0

def _semiarcs(lon, obliquity, geo_lat):
    """Diurnal and nocturnal semi-arcs of the degree, in degrees of right
    ascension, from ONE ascensional difference: 90 + AD and 180 - (90 + AD),
    so that they close to 180 exactly in floating point. A sixth of each is
    the hourly time (fn. 250), in degrees of right ascension per seasonal
    hour."""
    _ra, decl = _ra_decl(lon, obliquity)
    diurnal = 90.0 + _ascensional_difference(decl, geo_lat)
    return diurnal, 180.0 - diurnal

def _ascensional_method_applies(obliquity, geo_lat):
    """Where every ecliptic degree rises and sets, so the oblique ascension
    has a unique inverse (see the domain note above RAY_ASPECTS)."""
    return abs(geo_lat) + obliquity < 90.0

def _lon_with_right_ascension(ra, obliquity):
    """The ecliptic degree whose right ascension is ra (fn. 251's inverse)."""
    r = math.radians(ra % 360.0)
    return math.degrees(math.atan2(math.sin(r), math.cos(r) * math.cos(math.radians(obliquity)))) % 360.0

def _lon_with_oblique_ascension(oa, obliquity, geo_lat):
    """The ecliptic degree whose oblique ascension at this latitude is oa
    (fn. 251's inverse), in closed form:
        tan(lon) = sin(oa) / (cos(eps) cos(oa) - sin(eps) tan(phi)),
    exact to 2e-13 degrees over |phi| <= 65 (tests/test_spherical_math.py).
    Returns None outside the domain |phi| + eps < 90, where the inverse is
    not unique and sometimes does not exist. The scan-and-bisect this
    replaced assumed the 1-degree cell with the smallest sampled residual
    bracketed a sign change; above the polar circle it can miss a narrow
    branch and return a degree six degrees off (found 2026-09-08)."""
    if not _ascensional_method_applies(obliquity, geo_lat):
        return None
    a, e, p = math.radians(oa % 360.0), math.radians(obliquity), math.radians(geo_lat)
    return math.degrees(math.atan2(math.sin(a), math.cos(e) * math.cos(a) - math.sin(e) * math.tan(p))) % 360.0

def _hours_from_stake(lon, armc, obliquity, geo_lat):
    """VII.7, 3-13: the planet's quadrant and its distance in seasonal hours
    from the stake the text measures from. Returns (quadrant, stake, hours)."""
    ra, _decl = _ra_decl(lon, obliquity)
    # The day and night semi-arcs from one ascensional difference: "the
    # portions of the hours of the degree of the planet" and "of the degree
    # of the opposition of the planet", which are 90 + AD and 90 - AD. The
    # classification uses the semi-arcs themselves as boundaries.
    arc_day, arc_night = _semiarcs(lon, obliquity, geo_lat)
    h_day, h_night = arc_day / 6.0, arc_night / 6.0
    d = (ra - armc) % 360.0                                       # right circle of the planet less that of the Midheaven
    if d >= 360.0:                                                 # a tiny negative remainder rounds to exactly 360.0
        d = 0.0

    def hours(arc, hourly):
        # A zero semi-arc (a degree that never rises, or never sets, at this
        # latitude) is a quadrant of no extent: a planet classified into it
        # stands at its stake. Degenerate, and said so rather than divided.
        return 0.0 if hourly == 0.0 else arc / hourly

    if d < arc_day:                                                # 4-5: between the Midheaven and the Ascendant
        return 'Midheaven to Ascendant', 'Midheaven', hours(d, h_day)
    if d < 180.0:                                                  # 6-8: between the Ascendant and the stake of the earth
        return 'Ascendant to stake of the earth', 'Ascendant', hours(d - arc_day, h_night)
    d2 = d - 180.0                                                 # measured from the stake of the earth
    if d2 < arc_night:                                             # 9-10: between the stake of the earth and the setting
        return 'Stake of the earth to setting', 'Stake of the earth', hours(d2, h_night)
    return 'Setting to Midheaven', 'Stake of the setting', hours(d2 - arc_night, h_day)   # 11-13

def _circular_distance(a, b):
    return abs(((a - b + 180.0) % 360.0) - 180.0)

def cast_rays_by_ascension(lon, armc, obliquity, geo_lat, anchor='as written'):
    """VII.7, 14-22 for one planet. Each aspect gives a dict with the
    zodiacal ray, the two candidate positions (from the right ascensions,
    14, and from the ascensions of the city, 15), the hours of distance
    from the stake, and the ascensional ray: the two candidates when they
    agree (16), otherwise the anchor moved towards the other candidate by
    a sixth of their excess for every hour of distance (17-19, 21)."""
    quadrant, stake, hours = _hours_from_stake(lon, armc, obliquity, geo_lat)
    ra, _decl = _ra_decl(lon, obliquity)
    oa = _oblique_ascension(lon, obliquity, geo_lat)
    out = {}
    for name, arc in RAY_ASPECTS:
        from_ra = _lon_with_right_ascension(ra + arc, obliquity)
        from_oa = _lon_with_oblique_ascension(oa + arc, obliquity, geo_lat)
        if from_oa is None:
            # Outside the method's domain (see the note above RAY_ASPECTS):
            # no second candidate, so no ray. None, never a guessed degree.
            ray = None
        elif (excess := _circular_distance(from_ra, from_oa)) < 1e-9:
            ray = from_ra
        else:
            near, far = sorted((from_ra, from_oa), key=lambda x: _circular_distance(x, lon))
            use_nearest = {'as written': arc > 0, 'nearest': True, 'distant': False}[anchor]
            base, other = (near, far) if use_nearest else (far, near)
            step = (excess / 6.0) * hours
            direction = 1.0 if ((other - base) % 360.0) <= 180.0 else -1.0
            ray = (base + direction * min(step, excess)) % 360.0
        out[name] = {'zodiacal': (lon + arc) % 360.0, 'from right ascensions (14)': from_ra,
                     'from the city\'s ascensions (15)': from_oa, 'ascensional': ray,
                     'hours': hours, 'quadrant': quadrant, 'stake': stake}
    out['Opposition'] = {'zodiacal': (lon + 180.0) % 360.0, 'ascensional': (lon + 180.0) % 360.0,
                         'from right ascensions (14)': None, 'from the city\'s ascensions (15)': None,
                         'hours': hours, 'quadrant': quadrant, 'stake': stake}
    return out

RAYS_OUT_OF_DOMAIN = ("[UNCERTAIN -- Ptolemy's ascensional method does not apply at this latitude: "
                      "|latitude| + obliquity is 90 or more, so some ecliptic degrees never rise or set and "
                      "the ascensions of the city (VII.7, 15) have no unique inverse; no ray is given]")

def evaluate_rays_by_ascension(planetary_data, armc, obliquity, geo_lat, anchor='as written'):
    """One row per planet and aspect: the zodiacal ray beside Ptolemy's
    ascensional one, and how far apart they are. Outside the method's
    domain the ascensional cell carries RAYS_OUT_OF_DOMAIN; the opposition
    row (22, "in the same degree and minute") needs no ascensions and is
    given at every latitude."""
    rows = []
    for planet, data in planetary_data.items():
        if planet == 'North Node':
            continue
        cast = cast_rays_by_ascension(data['longitude'], armc, obliquity, geo_lat, anchor)
        for name, _arc in RAY_ASPECTS + (('Opposition', 180.0),):
            r = cast[name]
            if r['ascensional'] is None:
                ascensional, apart = RAYS_OUT_OF_DOMAIN, '--'
            else:
                ascensional = get_degree_string(r['ascensional'])
                apart = f"{_circular_distance(r['zodiacal'], r['ascensional']):.2f}°"
            rows.append({'Planet': planet, 'Ray': name, 'Zodiacal ray': get_degree_string(r['zodiacal']),
                         'Ascensional ray (VII.7)': ascensional, 'Apart': apart,
                         'Hours from stake': f"{r['hours']:.2f} from the {r['stake']}"})
    return rows

# --- Abu Ma'shar's two V.22 degree tables (decisions D-20, D-21) ----------
# Display only, labelled a supplement: nothing in Sahl and none of VII.6's
# conditions reads either table, so neither enters any verdict. Ordinal
# degrees as the figures print them, tested with int(lon % 30) + 1 like
# the wells. Pinned cell by cell in tests/test_base_tables.py.
#   Figure 63, V.22, 1-2: "when planets indicate the native's good fortune
#   by means of their positions, and the Moon or the Lot of Fortune is in
#   these degrees, or [these degrees] are exactly on the Ascendant, then
#   they will increase in the native's good fortune. And if they indicate
#   downfall, then these will instigate some motion towards high rank and
#   power." Seven degrees, 1.9% of the zodiac.
GOOD_FORTUNE_DEGREES = {'Taurus': [15, 27, 30], 'Leo': [3, 5], 'Scorpio': [7], 'Aquarius': [20]}
#   Figure 64, V.22, 4: "if the Ascendant was one of these degrees ... or
#   the Sun by day or the Moon by night was in one of them, and they were
#   in an excellent position of the circle, and the planets of the root of
#   the nativity indicated good fortune, then they will make him attain
#   nobility and the houses of kings." Thirty-one degrees, 8.6% of the
#   zodiac. The two preconditions cannot be tabulated and are shown as a
#   caveat. Aquarius 17 is also a well (V.21, Fig. 62); Leo 5 and
#   Aquarius 20 are in both tables. The text reconciles none of this.
ELEVATION_DEGREES = {
    'Aries': [19], 'Taurus': [3], 'Gemini': [11], 'Cancer': [1, 2, 3, 14, 15],
    'Leo': [5, 7, 17], 'Virgo': [2, 12, 20], 'Libra': [3, 5, 21], 'Scorpio': [12, 20],
    'Sagittarius': [13, 20], 'Capricorn': [12, 13, 14, 20], 'Aquarius': [7, 16, 17, 20], 'Pisces': [12, 20],
}

def evaluate_book_v_degrees(planetary_data, ascendant_lon, fortune_lon, sect):
    """The points each V.22 table names, checked against its degrees:
    Figure 63 for the Moon, the Lot of Fortune and the Ascendant; Figure 64
    for the Ascendant and the luminary of the sect. A row per hit, and no
    row is a verdict -- see GOOD_FORTUNE_DEGREES above."""
    luminary = 'Sun' if sect == 'Diurnal' else 'Moon'
    checks = [
        ('Moon', planetary_data['Moon']['longitude'], GOOD_FORTUNE_DEGREES, 'Increasing in good fortune (V.22, 1-2; Fig. 63)'),
        ('Lot of Fortune', fortune_lon, GOOD_FORTUNE_DEGREES, 'Increasing in good fortune (V.22, 1-2; Fig. 63)'),
        ('Ascendant', ascendant_lon, GOOD_FORTUNE_DEGREES, 'Increasing in good fortune (V.22, 1-2; Fig. 63)'),
        ('Ascendant', ascendant_lon, ELEVATION_DEGREES, 'Elevation and power (V.22, 4; Fig. 64)'),
        (f'{luminary} (luminary of the sect)', planetary_data[luminary]['longitude'], ELEVATION_DEGREES,
         'Elevation and power (V.22, 4; Fig. 64)'),
    ]
    results = []
    for point, lon, table, label in checks:
        sign = get_zodiac_sign(lon)
        degree_1_based = int(lon % 30) + 1
        if degree_1_based in table.get(sign, []):
            caveat = ('the text adds "in an excellent position of the circle" and a fortunate root, neither tabulated'
                      if table is ELEVATION_DEGREES else 'an amplifier of a good fortune already shown, not a testimony')
            if table is ELEVATION_DEGREES and degree_1_based in WELLED_DEGREES.get(sign, []):
                caveat += '; this degree is also a well (V.21)'
            results.append({'Point': point, 'Position': get_degree_string(lon), 'Table': label, 'Caveat': caveat})
    return results

def evaluate_special_degrees(planetary_data):
    """Flags planets in Sahl's dark signs, in the two signs of his burned
    place (no degrees -- see DARK_SIGNS above), in a classical welled
    degree of their current sign, or in one of Sahl's two sign-boundary
    conditions.

    The boundary pair is the other half of the five-degree rule and its
    mirror at the far end of the sign:

    ENTERING -- "every planet which is at the beginning of a sign is weak
    until it is firmly established in it and comes to be 5 degrees within
    it" (Fifty Aphorisms #44, 87), repeated as "the planets do not become
    powerful in the sign [they are in] until they travel 5 degrees in it"
    (On Nativities Ch.1.22, 9).

    LEAVING -- "if a planet came to be in the LAST degree of the sign, then
    its strength has already gone away from that sign, and its strength is
    in the next sign ... like a man putting his foot on the threshold of
    [his] door. And if a planet was in the twenty-ninth degree, then indeed
    the strength of the planet IS in that sign" (Fifty Aphorisms #15,
    31-33). So the 29th degree still counts, and only the 30th has left."""
    results = []
    for planet, data in planetary_data.items():
        if planet == 'North Node': continue
        lon = data['longitude']
        conditions = []

        sign = get_zodiac_sign(lon)
        if sign in DARK_SIGNS:
            conditions.append("Dark sign (Intro Ch. 1, 18; Nat. 1.38, 8)")
        if sign in BURNED_PLACE_SIGNS:
            conditions.append('In the burned place\'s signs -- "the end of Libra and the beginning of '
                              'Scorpio", no degrees given (Intro Ch. 1, 19; Nat. 1.38, 9)')
        degree_1_based = int(lon % 30) + 1
        if degree_1_based in WELLED_DEGREES.get(sign, []):
            conditions.append("Welled Degree")

        deg_in_sign = lon % 30.0
        if deg_in_sign < 5.0:
            conditions.append("Not yet established in the sign (Aph. #44, 87)")
        elif deg_in_sign >= 29.0:
            conditions.append("On the threshold; strength already in the next sign (Aph. #15, 31)")

        if conditions:
            results.append({
                'Planet': planet,
                'Position': get_degree_string(lon),
                'Condition': ", ".join(conditions),
            })
    return results

# --- Abu Ma'shar's Planetary Condition -- Gr. Intr. VII.6 -------
# (with supporting data/mechanics from VII.3-4 and V.20)

FORTUNES = {'Jupiter', 'Venus'}
INFORTUNES = {'Saturn', 'Mars'}

# Chart-relative infortune (C-15 / decision D-13, 2026-09-08). Choices Ch.
# 1, 12: "that infortune was good for him, because the infortunes are
# perhaps more fitting for him, since [one] may be the lord of the
# original Ascendant." Four sentences later Sahl says the opposite of the
# infortunes in general (1, 16-17: "unjust in nature ... there is no
# escape from their injustice"), so this is a SWITCH and it is OFF by
# default. When on, the malefic that rules the Ascendant is not counted
# as an infortune in the tests that read INFORTUNES as "an affliction by
# an infortune": Sahl's enclosure, strength gate and weakness 94-95, Abu
# Ma'shar's 3, 47-50 and enclosure, and the Moon's lists (67-68, 106 and
# her enclosure). It stays a malefic where its own nature is meant (the
# two infortunes accepting each other, 135; the Head/Tail polarity, 51).
# Sahl gives no partial grade, so the softening is whole: the fitting
# infortune is simply not an infortune for the chart.
FITTING_INFORTUNE = False
SOFTENED_INFORTUNE = None

def fitting_infortune(ascendant_lon):
    """The malefic that rules the Ascendant sign, or None."""
    lord = SIGN_TO_DOMICILE.get(get_zodiac_sign(ascendant_lon))
    return lord if lord in INFORTUNES else None

def effective_infortunes():
    """INFORTUNES less the fitting one, when the switch has named it."""
    return INFORTUNES - {SOFTENED_INFORTUNE} if SOFTENED_INFORTUNE else set(INFORTUNES)

# Gr. Intr. V.20, Figs. 60-61: bright/dusky/empty/dark degrees by
# sign, transcribed as (start, end, category) ranges (degree-in-sign, 0-29).
BRIGHTNESS_DEGREES = {
    'Aries':       [(0, 2, 'Dusky'), (3, 7, 'Dark'), (8, 15, 'Dusky'), (16, 19, 'Bright'), (20, 23, 'Dark'), (24, 28, 'Bright'), (29, 29, 'Dark')],
    'Taurus':      [(0, 2, 'Dusky'), (3, 9, 'Dark'), (10, 11, 'Empty'), (12, 19, 'Bright'), (20, 24, 'Empty'), (25, 27, 'Bright'), (28, 29, 'Dusky')],
    'Gemini':      [(0, 6, 'Bright'), (7, 9, 'Dusky'), (10, 14, 'Bright'), (15, 16, 'Empty'), (17, 22, 'Bright'), (23, 29, 'Dusky')],
    'Cancer':      [(0, 6, 'Dusky'), (7, 11, 'Bright'), (12, 13, 'Dusky'), (14, 17, 'Bright'), (18, 19, 'Dark'), (20, 27, 'Bright'), (28, 29, 'Dark')],
    'Leo':         [(0, 6, 'Bright'), (7, 9, 'Dusky'), (10, 15, 'Dark'), (16, 20, 'Empty'), (21, 29, 'Bright')],
    'Virgo':       [(0, 4, 'Dusky'), (5, 8, 'Bright'), (9, 10, 'Empty'), (11, 16, 'Bright'), (17, 20, 'Dark'), (21, 27, 'Bright'), (28, 29, 'Empty')],
    'Libra':       [(0, 4, 'Bright'), (5, 9, 'Dusky'), (10, 17, 'Bright'), (18, 20, 'Dusky'), (21, 27, 'Bright'), (28, 29, 'Empty')],
    'Scorpio':     [(0, 2, 'Dusky'), (3, 7, 'Bright'), (8, 13, 'Empty'), (14, 19, 'Bright'), (20, 21, 'Dark'), (22, 26, 'Bright'), (27, 29, 'Dusky')],
    'Sagittarius': [(0, 8, 'Bright'), (9, 11, 'Dusky'), (12, 18, 'Bright'), (19, 22, 'Dark'), (23, 29, 'Dusky')],
    'Capricorn':   [(0, 6, 'Dusky'), (7, 9, 'Bright'), (10, 14, 'Dark'), (15, 18, 'Bright'), (19, 20, 'Dusky'), (21, 24, 'Empty'), (25, 29, 'Bright')],
    'Aquarius':    [(0, 3, 'Dark'), (4, 8, 'Bright'), (9, 12, 'Dusky'), (13, 20, 'Bright'), (21, 24, 'Empty'), (25, 29, 'Bright')],
    'Pisces':      [(0, 5, 'Dusky'), (6, 11, 'Bright'), (12, 17, 'Dusky'), (18, 21, 'Bright'), (22, 24, 'Empty'), (25, 27, 'Bright'), (28, 29, 'Dusky')],
}

def _brightness_category(lon):
    sign = get_zodiac_sign(lon)
    degree_in_sign = int(lon % 30)
    for start, end, category in BRIGHTNESS_DEGREES[sign]:
        if start <= degree_in_sign <= end:
            return category
    return 'Bright'  # unreachable if the table is complete, kept as a safe default

# Gr. Intr. VII.6, 19-20: for the five non-luminaries, the domicile
# in which their nature is "moderated" (simply fortunate) versus the other,
# "contrary" domicile (suitable, but of a lesser grade).
PREFERRED_DOMICILE = {'Saturn': 'Aquarius', 'Jupiter': 'Sagittarius', 'Mars': 'Scorpio', 'Venus': 'Taurus', 'Mercury': 'Virgo'}

# Gr. Intr. VI.26, 3-4, Fig. 90: quadrants alternate Advancing/
# Masculine/Eastern vs. Withdrawing/Feminine/Western, diagonally opposite
# pairs sharing a designation. In Whole-Sign-House terms:
# Quadrant genders, VERIFIED against Abu Ma'shar's Figure 90 (VI.26, 3,
# "Advancing and withdrawing quadrants"). Reading the figure with the
# Ascendant on the left, the Midheaven on top and primary motion running
# clockwise, its four quadrants map onto house numbers as:
#
#   upper-left,  MC to Asc  = 10, 11, 12 -> Advancing, MALE, eastern, on right
#   upper-right, Desc to MC =  7,  8,  9 -> Withdrawing, FEMININE, western, on left
#   lower-left,  Asc to IC  =  1,  2,  3 -> Withdrawing, FEMININE, western, on left
#   lower-right, IC to Desc =  4,  5,  6 -> Advancing, MALE, eastern, on right
#
# which is exactly the assignment below. It was previously carried as an
# unsourced convention, because VII.6, 28 names the quadrants but defines
# them at IV.8, 16, outside this corpus, and the figure's image was
# missing until it was rephotographed.
MASCULINE_QUADRANT_HOUSES = {4, 5, 6, 10, 11, 12}
FEMININE_QUADRANT_HOUSES = {1, 2, 3, 7, 8, 9}

# RESOLVED (audit of 2026-09-06). Fig. 90 also labels the two masculine
# quadrants ADVANCING and the two feminine ones WITHDRAWING, which looked
# like a conflict with Sahl 83 (angular or succedent: 1, 2, 4, 5, 7, 8, 10,
# 11). It is not one; they are two different conditions sharing an English
# word.
#
# The reshoot of Fig. 90 is rotated 90 degrees, and its right margin carries
# the line-beginnings of VI.26, 3, which read (top to bottom): "3 Now |
# rants whic | Ascendan | heaven, | setting to | called "a | eastern, |
# while th | which ar | to the set | fourth t | are calle | feminine |
# left." 4 (" -- i.e. the quadrants from the Ascendant to midheaven and
# from the setting to the fourth are called "advancing ... eastern", those
# from the midheaven to the setting and from the fourth to the Ascendant
# "... feminine ... left". The figure's dashed arrows run ASC -> MC and
# DSC -> IC: primary motion carrying a planet TOWARD THE MERIDIAN. Dykes
# states the same criterion at On Nativities 10.3 fn. 231: "the eastern
# quarter from the Ascendant to the Midheaven is advancing, while the
# quarter from the Midheaven to the Descendant is declining or retreating."
#
# Abu Ma'shar lists the two as separate conditions himself -- VII.3, 2-5:
# "The first is if one is in the advancing and withdrawing quadrants of the
# circle. The second is if it is in one of the houses ... which are the
# stakes. The third ... follows a stake. The fourth ... the withdrawing
# houses." Sahl defines HIS word at Ch.3, 4, "advancement, it is if a
# planet was in a stake or what follows a stake", and his Figure 9 shades
# exactly sectors 1, 2, 4, 5, 7, 8, 10, 11 with the axes as boundaries. So
# 83 is right as implemented, and the quadrant set below is Abu Ma'shar's
# own condition (VII.3, 2), recorded for when it is scored in its own right.
#
# Sahl knew the quadrant scheme too, and names a rival to it. On Times
# Ch. 1, 10-11 gives the quadrants -- "a planet is in what is between the
# Ascendant and the Midheaven, and what is opposite that (and that is what
# is between the setting and the stake of the earth): and this position of
# the circle indicates quickness ... [the other two] slowness and delay,
# ACCORDING TO THE STATEMENT OF THE ANCIENTS" -- then 12-13 gives
# Masha'allah's HEMISPHERES, "he differs from them in that: he makes the
# quick place of the circle be what begins its rise ... (and it is what is
# from the degree of the fourth), [then] turned back towards the Midheaven",
# and 14 takes Masha'allah's side: "And that is the closest of the two
# statements, in [its] analogy" (fn. 7: "most appropriate, most resembling
# the truth"). Figure 44 draws both wheels. Sahl then USES the hemisphere
# division in another work, On Choices Ch. 6, 16-17: treat from the head
# to the navel "when the Moon is in what is between the stake of the earth,
# so rising up to the Midheaven ... the highest region of the circle", and
# below the navel when she is "between the tenth, declining towards the
# stake of the earth ... the lowest part of the circle". (Ch. 6, 30's
# "declining from the Midheaven toward the stake of the earth" shares the
# vocabulary only.)
#
# None of that moves 83 or the set below. On Times Ch. 1 is about the
# QUICKNESS OF TIMING and On Choices Ch. 6 about a bodily correspondence;
# neither says the hemisphere division governs advancing-as-strength, so
# it is recorded here as a third scheme in the sources, not scored. Where
# the 2026-09-07 review (synthesis/05, Tier 3) and the report it reviewed
# (synthesis/04, A4) differ, it is only on whether Ch. 6, 30 counts as a
# use of the scheme; this comment follows the review and cites 16-17 alone.
ADVANCING_BY_QUADRANT_FIG90 = {4, 5, 6, 10, 11, 12}   # Gr. Intr. VII.3, 2 / VI.26, 3; not Sahl 83

# Approximate geocentric distance range (AU) per planet, used only as a
# modern proxy for "rising up in the circle of the apogee" (VII.6, 23) --
# swisseph doesn't expose the classical deferent/epicycle apogee for
# non-lunar bodies, so this substitutes "farther from Earth than usual" for
# the true Ptolemaic concept. An approximation, flagged as such.
GEOCENTRIC_DISTANCE_RANGE = {
    'Moon': (0.0024, 0.0027), 'Mercury': (0.53, 1.45), 'Venus': (0.27, 1.73),
    'Sun': (0.983, 1.017), 'Mars': (0.37, 2.68), 'Jupiter': (3.95, 6.45), 'Saturn': (8.0, 11.1),
}

PLANET_SWE_IDS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
                   'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN}

def _dispositors(lon, sect):
    """The rulers of all five essential dignities at a degree -- used for
    the Received test (VII.6, 12)."""
    rulers = get_essential_rulers(lon)
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    return {rulers['domicile'], rulers['exaltation'], rulers[triplicity_key], rulers['term'], rulers['face']} - {'-'}

def _in_last_bound(lon):
    """Whether the degree lies in its sign's final Egyptian bound, which the
    table makes an infortune's in every sign -- the test both Moon lists
    share (Sahl Ch.3, 108; VII.6, 72)."""
    terms = EGYPTIAN_TERMS.get(get_zodiac_sign(lon), [])
    return bool(terms) and (lon % 30.0) >= (terms[-2][0] if len(terms) > 1 else 0)

def _current_bound_width(lon):
    """The width in degrees of the Egyptian bound the degree falls in --
    the measure VII.6, 48 uses for "less than the bound of [a single]
    planet between them and the infortunes"."""
    sign = get_zodiac_sign(lon)
    degree_in_sign = lon % 30
    lower = 0.0
    for limit, _lord in EGYPTIAN_TERMS.get(sign, []):
        if degree_in_sign < limit:
            return float(limit) - lower
        lower = float(limit)
    return 30.0 - lower

# VII.6, 58 says an encloser counts as present in the 2nd or 12th sign "by
# its body or rays." True (the default) is the literal text. False selects
# this project's own conservative variant -- see the note in
# _abu_mashar_enclosed().
SIGN_ENCLOSURE_BODIES_ONLY = False

def _ray_degrees(lon):
    """A planet's body plus the degrees into which it casts its rays."""
    return [(lon + a) % 360.0 for a in (0.0, 60.0, 90.0, 120.0, 180.0, 240.0, 270.0, 300.0)]

def _abu_mashar_enclosed(planet, enclosing_set, planetary_data, rows, orb=7.0):
    """Enclosure per Abu Ma'shar's own VII.6, 56-62 -- which is NOT simply
    Sahl's concept borrowed. He gives two types of his own:

    Type 1 by degree (57): the planet has one enclosing planet's body OR
    RAYS within orb in front of it and the other's behind it; or it is
    separating from one by assembly or aspect and connecting with the
    other (that second form IS Sahl's mechanism). The 7-degree orb is from
    the note on 57: "the rays or bodies of the enclosing planets must be 7
    degrees or less on either side of the enclosed planet."

    Confirmed against Figure 145: the Moon at 13 Libra is besieged by
    Saturn's opposition ray from 18 Aries (5 degrees ahead) and Mars's
    sextile ray from 10 Leo (3 degrees behind).

    Type 2 by sign (58): one enclosing planet, by body OR RAYS, is in the
    SECOND sign from the planet and the other is in the twelfth. Taken
    literally this fires on about 43 percent of placements, since a planet's
    rays reach eight of the twelve signs; SIGN_ENCLOSURE_BODIES_ONLY selects
    a bodies-only variant at about 2 percent. The literal text is the
    default -- a rule being common is not evidence that it was meant to be
    rare.

    Dissolution (60-61): "if the Sun or one of the fortunes looked at the
    enclosed planet, and there was less than 7 degrees between the planet
    and those rays, then it indicates the dissolving of that misfortune."
    An earlier version of this project removed a dissolution rule as an
    unsourced invention. It is sourced -- this is it.

    Returns (enclosed, kind, dissolved_by) with dissolved_by naming the
    planet whose rays break it, or None."""
    members = [m for m in enclosing_set if m != planet and m in planetary_data]
    if len(members) != 2:
        return False, None, None
    lon = planetary_data[planet]['longitude']
    a_rays = _ray_degrees(planetary_data[members[0]]['longitude'])
    b_rays = _ray_degrees(planetary_data[members[1]]['longitude'])

    # 57 confines the degree type to the planet's OWN SIGN: "a planet is in
    # a sign, and WITH IT IN ITS SIGN is an infortune or its rays in front
    # of it, and an infortune or its rays behind it." The windows below were
    # pure degree arithmetic and so reached across the sign boundary, where
    # 20% of type-1 hits were coming from. The by-sign type at 58 is the
    # construction that is allowed to look outside the sign, and it does so
    # on its own terms.
    own_sign = int(lon // 30)

    def ahead(rays):
        return any(0.0 < (d - lon) % 360.0 <= orb and int(d // 30) == own_sign
                    for d in rays)

    def behind(rays):
        return any(0.0 < (lon - d) % 360.0 <= orb and int(d // 30) == own_sign
                    for d in rays)

    kind = None
    if (ahead(a_rays) and behind(b_rays)) or (ahead(b_rays) and behind(a_rays)):
        kind = 'by degree (57)'
    else:
        # The second form of 57: separating from one, connecting with the
        # other -- Sahl's own shape, which Abu Ma'shar folds in here.
        for sep_t, con_t in ((members[0], members[1]), (members[1], members[0])):
            sep = any((r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == sep_t
                       and _is_separating_in_nature(r) for r in rows)
            con = any((r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == con_t
                       and r['motion'] == 'Applying' and _is_connected(r) for r in rows)
            if sep and con:
                kind = 'separating/connecting (57)'
                break
    if kind is None:
        # Type 2 by sign (58): one encloser in the second sign from the
        # planet "by its body or rays," the other in the twelfth.
        #
        # A previous pass restricted this to BODIES because the literal
        # reading fires on 41-44% of placements over 3,654 planet-checks
        # (a planet's rays reach eight of the twelve signs), against
        # 1.4-2.5% for bodies alone. That frequency argument is real but it
        # is not textual authority, and the text says "or rays" twice. The
        # literal reading is the default; SIGN_ENCLOSURE_BODIES_ONLY selects
        # the conservative variant, which is this project's own and is
        # labelled as such wherever it is shown.
        sign_idx = int(lon // 30)
        second = (sign_idx + 1) % 12
        twelfth = (sign_idx - 1) % 12
        if SIGN_ENCLOSURE_BODIES_ONLY:
            a_signs = {int(planetary_data[members[0]]['longitude'] // 30)}
            b_signs = {int(planetary_data[members[1]]['longitude'] // 30)}
            variant = 'bodies only, project variant'
        else:
            a_signs = {int(d // 30) for d in a_rays}
            b_signs = {int(d // 30) for d in b_rays}
            variant = 'body or rays'
        if ((second in a_signs and twelfth in b_signs)
                or (second in b_signs and twelfth in a_signs)):
            kind = f'by sign, 2nd and 12th, {variant} (58)'
    if kind is None:
        return False, None, None

    # 60: "in BOTH TYPES, if the Sun or one of the fortunes looked at the
    # enclosed planet, and there was less than 7 degrees between the planet
    # and those rays, then it indicates the dissolving of that misfortune."
    # Dykes' note on 60 restricts it: "Actually this only refers to the
    # degree-based type of enclosure, in 56."
    #
    # Both are honoured, because the disagreement is about the MEASURE, not
    # about whether a sign-based enclosure can be dissolved at all -- 61
    # gives a dissolution in the same breath for an enclosed sign, with no
    # degree condition ("if the enclosed thing was itself a sign, and the
    # fortunes or Sun looked at it, they will dissolve that misfortune").
    # So the degree type takes 60's 7-degree ray test, and the sign type
    # takes 61's bare look. Applying the 7-degree test to the sign type, as
    # an earlier version did, is the one reading the note rules out.
    by_sign = kind is not None and 'by sign' in kind
    for breaker in ({'Sun'} | FORTUNES) - set(members) - {planet}:
        if breaker not in planetary_data:
            continue
        breaker_lon = planetary_data[breaker]['longitude']
        if by_sign:
            raw = abs(int(breaker_lon // 30) - own_sign)
            if min(raw, 12 - raw) not in AVERSION_SIGN_COUNTS:
                return True, kind, breaker
        elif any(abs(((d - lon + 180.0) % 360.0) - 180.0) < orb
                  for d in _ray_degrees(breaker_lon)):
            return True, kind, breaker
    return True, kind, None

def _sahl_enclosed(planet, enclosing_set, rows, blocking_pairs):
    """Enclosure (Sahl, The Introduction Ch.3, 119-123, Fig. 25). The
    planet is separating from ONE member of enclosing_set and connecting
    with the OTHER, with neither leg itself intercepted by a third
    planet's rays -- "without another planet casting its rays between the
    two" (121), implemented by excluding either leg if it's already
    Blocked (evaluate_blocking()'s own output, passed in as
    blocking_pairs to avoid recomputing it per planet). Graded "more
    powerful and more unfortunate" when both legs are within 7 degrees of
    exact (121, confirmed against Fig. 25's own numbers: Moon separating
    from Mars by square, connecting to Saturn by opposition).

    Replaces an earlier version built from Abu Ma'shar's own VII.6, 56-59
    (a same-sign front/behind Connected test plus a separate sign-based
    2nd/12th-house test) which turned out not to match this mechanism at
    all -- Abu Ma'shar reuses Sahl's own concept rather than defining a
    new one.

    Returns (is_enclosed, is_severe, separating_from, connecting_to), or
    (False, False, None, None)."""
    members = [m for m in enclosing_set if m != planet]
    if len(members) != 2:
        return False, False, None, None
    for sep_target, con_target in ((members[0], members[1]), (members[1], members[0])):
        # The separating leg is NOT gated on the connection still being
        # live. 121 gives the base condition as "separating from one of
        # them [and] connecting with the other, without another planet
        # casting its rays between the two", and makes 7 degrees the
        # SEVERE grade, not the entry condition. Sahl's own Fig. 25 proves
        # it: "Mars is in 10 degrees of Cancer, and Saturn in 18 degrees of
        # Aries, and the Moon in 13 degrees of Libra. So the Moon is
        # separating from Mars from [his] second square, connecting with
        # Saturn from the opposition: at this time she is enclosed" (122).
        # She is 3 degrees past Mars ACROSS A SIGN BOUNDARY, and 9's
        # cross-sign separation window is a single degree -- so requiring
        # _is_connected here made the chapter's own worked figure return
        # nothing, and suppressed 82% of enclosures besides.
        #
        # This is the same distinction the Transfer evaluator already draws
        # for its own past leg (see its docstring): separating needs a
        # valid configuration and past-exact motion, not the tighter
        # Connected threshold.
        sep_row = next((r for r in rows if r['aspect_name'] != 'Aversion'
                         and (r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == sep_target
                         and r['motion'] == 'Separating'), None)
        con_row = next((r for r in rows if r['aspect_name'] != 'Aversion'
                         and (r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == con_target
                         and r['motion'] == 'Applying' and _is_connected(r)), None)
        if not sep_row or not con_row:
            continue
        if (planet, sep_target) in blocking_pairs or (planet, con_target) in blocking_pairs:
            continue
        severe = abs(sep_row['deviation']) <= 7.0 and abs(con_row['deviation']) <= 7.0
        return True, severe, sep_target, con_target
    return False, False, None, None

def evaluate_enclosure(planetary_data):
    """Enclosure (Sahl, The Introduction Ch.3, 119-123, Fig. 25): every
    planet enclosed between the two infortunes (misfortune), or the two
    fortunes (Abu Ma'shar's own extension of the same shape to a good-
    fortune direction, Gr. Intr. VII.6, 5)."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
        results = []
        for planet in planetary_data:
            if planet == 'North Node':
                continue
            for label, enclosing_set in (('Infortunes', effective_infortunes()), ('Fortunes', FORTUNES)):
                is_enc, severe, sep, con = _sahl_enclosed(planet, enclosing_set, rows, blocking_pairs)
                if is_enc:
                    results.append({
                        'Planet': planet, 'Enclosed By': label,
                        'Separating From': sep, 'Connecting To': con,
                        'Severity': 'More powerful/unfortunate (within 7°)' if severe else 'Standard',
                    })
        return results

FIXED_SIGNS = {'Taurus', 'Leo', 'Scorpio', 'Aquarius'}

# Sahl's narrow burned path, "the end of Libra and the beginning of Scorpio"
# (Ch.3, 110, with the 19 Libra to 3 Scorpio band footnoted there), which
# VII.6, 40 also uses as its harsh band inside the two whole signs.
HARSH_BURNED_PATH = (199.0, 213.0)

# Traditional planetary gender, for Strength/Weakness (87). Mercury is
# common/neutral and Sahl's own text doesn't address it here, so it's left
# unassigned rather than guessed.
PLANET_GENDER = {'Sun': 'Masculine', 'Moon': 'Feminine', 'Mercury': None,
                  'Venus': 'Feminine', 'Mars': 'Masculine', 'Jupiter': 'Masculine', 'Saturn': 'Masculine'}

def _averse_to_ascendant(lon, ascendant_lon):
    """Whether a degree's sign is in Aversion to the Ascendant's sign (2nd/
    12th or 6th/8th from it, Sahl, The Introduction Ch.2, 50-60) -- the
    planet-to-point analogue of the Aversion test _pairwise_configurations()
    already applies planet-to-planet."""
    sign_idx = SIGN_ORDER.index(get_zodiac_sign(lon))
    asc_idx = SIGN_ORDER.index(get_zodiac_sign(ascendant_lon))
    raw_apart = abs(sign_idx - asc_idx)
    signs_apart = min(raw_apart, 12 - raw_apart)
    return signs_apart in AVERSION_SIGN_COUNTS

# Sahl, The Introduction Ch.3, 78: the stakes and what follows them, but
# only "of the places which look at the Ascendant" -- which drops the 2nd
# and 8th (both in aversion to the Ascendant), leaving six. The author's
# own footnote to 78 confirms the count: "the definition here allows only
# six good places." Distinct from bare advancement (4, 83), which is every
# stake and succeedent place with no visibility qualifier.
EXCELLENT_PLACES = {1, 4, 5, 7, 10, 11}

# --- The good-place schemes, each labelled for what it is FOR (C-09 / D-9)
# Eight places, "for a planet in itself" (glossary p. 771): "Four of them
# are called the 'stakes' ... 33 four of them are said to be what follows
# the stakes ... 35 four of them are said to be falling from the stakes"
# (Introduction Ch. 2, 31-36, Fig. 5). Seven praised places, ranked, "for
# the native": Ascendant, Midheaven, seventh, fourth, eleventh, ninth,
# fifth (Ch. 2, 37-44, Figs. 6-7). Six excellent places: EXCELLENT_PLACES
# above (Ch. 3, 78). And Choices Ch. 9, 12: "in an excellent place, in the
# Ascendant, eleventh, or tenth" -- corroborating the glossary's hedge and
# demoting the 7th and 4th. Never merged into one house-strength number.
GOOD_PLACE_SCHEMES = {
    'Eight places, for a planet in itself (Intro Ch. 2, 31-36)': {
        'stakes': [1, 10, 7, 4], 'what follows the stakes': [2, 5, 8, 11], 'falling from the stakes': [3, 6, 9, 12]},
    'Seven praised places, ranked, for the native (Intro Ch. 2, 37-44)': [1, 10, 7, 4, 11, 9, 5],
    'Six excellent places (Intro Ch. 3, 78)': sorted(EXCELLENT_PLACES),
    'Excellent places for the Sun (Choices Ch. 9, 12)': [1, 11, 10],
}
# The tail of the ranking is a conflation (fn. 42): manuscript B reads
# "... 11, 5, 9"; H and L read "... 11, 9, 5"; the printed text takes H/L's
# order plus B's note that the ninth is the Sun's joy (42, itself B-only).
# Kept as printed, labelled (decision D-9, low-medium confidence).
SEVEN_PLACE_RANKING_NOTE = ("Printed order (manuscripts H and L: ... 11, 9, 5). Manuscript B reads ... 11, 5, 9; "
                            "the printed text takes H/L's order plus B's note that the ninth is the Sun's joy "
                            "(Introduction Ch. 2, 42, fn. 42) -- Dykes' conflation, kept as printed.")

def evaluate_strength_of_planets(planetary_data, essential, accidental, ascendant_lon, sect, natal_houses):
    """Strength of the Planets (Sahl, The Introduction Ch.3, 78-88): the
    eleven testimonies of a planet's strength at the time of judgment that
    77 announces, cross-checked against the author's own summary table
    (Fig. 24). An earlier version found only ten, having misread 87 (the
    tenth, "in the heart of the Sun") and renumbered 88 (the eleventh, the
    gender-matching quadrant and sign) as the tenth; the count discrepancy
    against 77 was noted at the time but resolved the wrong way.

    Note that 78 and 83 are NOT the same test, though an earlier version
    computed both from the same eight whole-sign houses. 78's "excellent
    place" is whole-sign and is narrowed by which places LOOK at the
    Ascendant (six of them, per its own footnote). 83's "advancing" is
    dynamic -- measured against the quadrant cusps, per the note on 83 and
    Sahl's glossary (Vol. I p. 771, Advancement: "dynamically angular or
    succeedent, i.e. moving by primary motion toward an axial degree"; the
    course glossary has the same entry) -- and takes this function's
    natal_houses argument.
    On a sample of 414 charts the two readings of advancement disagree for
    a third of all planet placements.

    Distinct from the existing Gr. Intr. VII.6-based Planetary Condition
    table, which scores a broader, differently-sourced strength/weakness
    scheme (21-46) built earlier in this project -- this is Sahl's own,
    narrower list, kept as its own table rather than merged into a later
    author's scheme (the project's standing practice: retain the original
    source's own definition when two sources diverge)."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        results = []
        for planet, data in planetary_data.items():
            if planet == 'North Node':
                continue
            lon = data['longitude']
            sign = get_zodiac_sign(lon)
            house = get_wsh_house(lon, ascendant_lon)
            # 83 is measured against the real angular axes rather than by sign
            # -- see the comment there. Both readings of the quadrant place are
            # kept: strict cusp membership, and the same with Sahl's own
            # five-degree carryover (Fifty Aphorisms #44, 87-89; On Nativities
            # Ch.1.22, 9). A planet a few degrees short of an angle is not
            # "falling from the stake" by either of those passages.
            quadrant_house_strict = get_house_number(lon, natal_houses)
            quadrant_house = get_effective_house(lon, natal_houses)
            ess, acc = essential[planet], accidental[planet]
            labels = []

            # (78) In an excellent place: a stake or what follows one, limited
            # to those that look at the Ascendant (see EXCELLENT_PLACES). An
            # earlier version used all eight angular+succeedent houses, which
            # wrongly admitted the 2nd and 8th.
            if house in EXCELLENT_PLACES:
                labels.append('In an excellent place from the Ascendant (78)')

            # (79) In something of its own share: house, exaltation, triplicity, bound, face, or joy.
            if ess['Domicile'] or ess['Exalt'] or ess['Triplicity'] or ess['Term'] or ess['Face'] or acc['Joy']:
                labels.append('In its own share of dignity (79)')

            # (80) Direct in course.
            if not acc['Retrograde']:
                labels.append('Direct in course (80)')

            # (81) No infortune "with it in its sign, connecting with it, or
            # looking at it FROM A SQUARE OR OPPOSITION" -- Fig. 24 renders
            # this as "not in whole-sign angles of infortune," so assembly,
            # square and opposition count and sextile/trine do not. (An
            # earlier version counted any non-Aversion configuration.)
            # The infortune must be the OTHER planet in the pair. Testing
            # "either member is an infortune" made Mars and Saturn fail 81
            # against any partner at all, since each is itself an infortune
            # -- 59% of their placements lost a testimony Sahl grants them.
            infortune_contact = any(
                r['aspect_name'] in ('Conjunction', 'Square', 'Opposition')
                and (({r['p1'], r['p2']} - {planet}) & effective_infortunes())
                for r in rows if planet in (r['p1'], r['p2'])
            )
            if not infortune_contact:
                labels.append('Not in the whole-sign angles of an infortune (81)')

            # (82) Not connecting with a planet falling from the ASC or in its
            # own fall, and not itself in its own fall.
            connects_weak_target = False
            for r in rows:
                if r['aspect_name'] == 'Aversion' or not _is_connected(r) or planet not in (r['light_name'], r['heavy_name']):
                    continue
                other = r['heavy_name'] if r['light_name'] == planet else r['light_name']
                other_house = get_wsh_house(planetary_data[other]['longitude'], ascendant_lon)
                other_sign = get_zodiac_sign(planetary_data[other]['longitude'])
                # Sahl's "falling away from the Ascendant" is AVERSION, not
                # cadency. Sahl's glossary (Vol. I p. 774, Cadent) says so:
                # "3rd, 6th, 9th, 12th. But see also FALLING AWAY FROM, WHICH
                # IS EQUIVALENT TO AVERSION" -- and its Aversion entry is the
                # 2nd, 6th, 8th and 12th (the Course Glossary carries the same
                # two entries verbatim). Sahl keeps the two apart himself at
                # 91, "falling from the stakes AND not looking at the
                # Ascendant: and that is in the sixth and the twelfth", which
                # this file already reads correctly. Reading it as cadency
                # admits the 3rd and 9th, which DO look at the Ascendant, and
                # misses the 2nd and 8th, which do not.
                if _averse_to_ascendant(planetary_data[other]['longitude'], ascendant_lon) \
                        or other_sign in FALLS.get(other, []):
                    connects_weak_target = True
                    break
            if not connects_weak_target and not ess['Fall']:
                labels.append('Not connecting with a falling/fallen planet, nor itself in its fall (82)')

            # (83) Advancing -- measured DYNAMICALLY, against the quadrant
            # cusps, not by whole sign. The note on 83 is explicit that the
            # word is the active participle of Form IV and so "means that it
            # is dynamically angular or succeedent, i.e. by primary motion
            # with respect to the angular axes, and not by whole sign"; Sahl's
            # own Figure 9 for 4-5 is captioned "understood dynamically," and
            # Sahl's glossary (Vol. I p. 771, Advancement) defines it as
            # "dynamically angular or succeedent, i.e. moving by primary
            # motion toward an axial degree" -- the course glossary's entry
            # is the same text.
            #
            # Primary motion carries a planet 1 -> 12 -> 11 -> 10: out of an
            # angle into the cadent house, moving AWAY from the axis it just
            # crossed, then into the succedent house, approaching the next
            # one. So "dynamically angular or succeedent" is the same set of
            # house numbers as the whole-sign test uses -- the difference is
            # entirely in which house system assigns the number, and on a
            # typical chart it moves most of the planets.
            #
            # Note this is deliberately NOT the same predicate as 78's
            # "excellent place", which is whole-sign: that one is defined by
            # which places LOOK at the Ascendant, and its own footnote counts
            # the six resulting places.
            if quadrant_house in ANGLE_HOUSES | SUCCEDENT_HOUSES:
                if quadrant_house != quadrant_house_strict:
                    labels.append(f'Advancing, by the five-degree rule into the {HOUSE_ORDINAL[quadrant_house]} (83)')
                else:
                    labels.append('Advancing (83)')

            # (84) A masculine planet (Saturn, Jupiter, Mars) eastern, arising at dawn.
            # 84 is "eastern, ARISING AT DAWN" -- visible, not merely on the
            # eastern side. Sahl gives the floors himself in On Nativities 1.22,
            # 1: with 6 degrees between Saturn or Jupiter and the Sun "they are
            # considered to be eastern ... BUT IF THEY WERE LESS THAN THAT, THEY
            # WILL NOT BE FIT"; Mars at 15 degrees (1.22, 3 and its note).
            # Sahl's glossary (Vol. I p. 778, Eastern and western) sense (2)
            # is "to be outside the Sun's rays and visible (eastern) or under
            # them and invisible (western)"; the Course Glossary's Eastern (2)
            # is the same entry. An earlier version tested only which side of the Sun the
            # planet stood on, so 11.5% of eastern superiors took this testimony
            # while burned or under the rays.
            if planet in ('Saturn', 'Jupiter', 'Mars'):
                sun_lon = planetary_data['Sun']['longitude']
                signed_from_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
                visible_floor = 15.0 if planet == 'Mars' else 6.0
                if signed_from_sun < 0 and abs(signed_from_sun) >= visible_floor:
                    # Not "risen": 6 degrees is On Nativities 1.22, 1's nine-day
                    # allowance ("considered to be eastern"), inside the 15
                    # degrees this same table calls under the rays (93). Mars's
                    # 15 is Dykes' inference at 1.22 fn. 174, not text.
                    labels.append(f'Masculine planet, eastern, {visible_floor:.0f}+ deg from the Sun '
                                  f'(84; "considered eastern", On Nativities 1.22, 1)')

            # (85) "In their own glow: that is, a masculine planet in the day,
            # and a feminine planet in the night." The translator's footnote
            # calls the gendered wording an error for DIURNAL/NOCTURNAL (Mars
            # being masculine but nocturnal), and Fig. 24 renders the row as
            # simply "of the sect" -- so this is bare sect agreement. An
            # earlier version reused accidental[]['Hayz'], which additionally
            # demands the right side of the horizon and a sign of matching
            # gender, and so under-reported the testimony.
            planet_is_diurnal = planet_sect_is_diurnal(planet, lon, planetary_data['Sun']['longitude'])
            if planet_is_diurnal == (sect == 'Diurnal'):
                labels.append('In its own glow, i.e. of the sect (85)')

            # (86) In a fixed sign.
            if sign in FIXED_SIGNS:
                labels.append('In a fixed sign (86)')

            # (87) In the heart of the Sun -- "when they are with him in one
            # degree." Sahl's own one-degree window, not the later 16-17
            # arcminute cazimi convention that accidental[]['Cazimi'] uses, so
            # it is measured here rather than reusing that flag.
            if planet != 'Sun':
                sun_lon = planetary_data['Sun']['longitude']
                if abs(((lon - sun_lon + 180.0) % 360.0) - 180.0) <= 1.0:
                    labels.append('In the heart of the Sun (87)')

            # (88) Masculine/feminine QUADRANT and sign matching the planet's
            # own gender. This is Sahl's ELEVENTH testimony, not the tenth --
            # an earlier version numbered it (87) and omitted the heart of the
            # Sun entirely, leaving only ten of the eleven that 77 announces.
            #
            # The quadrant clause is measured against the QUADRANT CUSPS. It
            # read the whole-sign house, which is a different place for 52.3% of
            # placements and flips the masculine/feminine verdict for 18.6% of
            # them. A quadrant is the span between two angles; a whole sign is
            # not, and the file computes the real one a few lines above.
            #
            # 88 announces ONE testimony with two clauses. Both are reported,
            # but as a single entry -- appending them separately gave one
            # paragraph two votes.
            gender = PLANET_GENDER.get(planet)
            _q88 = ((gender == 'Masculine' and quadrant_house in MASCULINE_QUADRANT_HOUSES)
                     or (gender == 'Feminine' and quadrant_house in FEMININE_QUADRANT_HOUSES))
            _s88 = ((gender == 'Masculine' and sign in MASCULINE_SIGNS)
                     or (gender == 'Feminine' and sign in FEMININE_SIGNS))
            if _q88 or _s88:
                _parts = (['quadrant'] if _q88 else []) + (['sign'] if _s88 else [])
                labels.append(f"In a matching-gender ({gender.lower()}) {' and '.join(_parts)} (88)")

            if labels:
                results.append({'Planet': planet, 'Strength Testimonies': ', '.join(labels), 'Count': len(labels),
                                'Labels': labels})
        return results

def evaluate_weakness_of_planets(planetary_data, essential, accidental, ascendant_lon, sect):
    """Weakness of the Planets (Sahl, The Introduction Ch.3, 91-100): the
    ten testimonies of weakness Sahl names as item [15] of his sixteen-item
    scheme (90: "the weakness of the planets, and their harms in nativities
    and questions, indeed that is in ten ways"), cross-checked against the
    author's own summary table (Fig. 24).

    Distinct from the existing Gr. Intr. VII.6-based Planetary Condition
    table's own, differently-sourced weakness scheme (30-46) -- kept
    separate per the project's standing practice of retaining the original
    source's own definition.

    94 and 95 are separate testimonies, not one: 94 is an ordinary harmful
    connection with a single infortune by assembly/square/opposition, 95 is
    enclosure between both of them. An earlier version merged the two into
    the enclosure test and so never flagged a single-infortune contact.

    97's two clauses ("connecting with a planet falling away from the
    Ascendant, AND it is separating from a planet receiving it") are
    reported independently, since the translator's own footnote says he is
    "not sure that these conditions must both exist at once" -- an open
    question in the source, so the permissive reading is used and flagged
    rather than silently settled."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
        results = []
        for planet, data in planetary_data.items():
            if planet == 'North Node':
                continue
            lon, lat = data['longitude'], data['latitude']
            sun_lon = planetary_data['Sun']['longitude']
            house = get_wsh_house(lon, ascendant_lon)
            ess, acc = essential[planet], accidental[planet]
            labels = []

            # (91) Falling from the stakes, and not looking at (averse to) the Ascendant.
            if house in CADENT_HOUSES and _averse_to_ascendant(lon, ascendant_lon):
                labels.append('Falling from the stakes, averse to the Ascendant (91)')

            # (92) Retrograde.
            if acc['Retrograde']:
                labels.append('Retrograde (92)')

            # (93, 99) Under the rays of the Sun. 99's first clause -- western,
            # "the Sun having already overtaken it (that is, if it was in front
            # of the Sun)" -- belongs to this testimony, not to 98; Fig. 24
            # pairs them as one "(93, 99) Under the rays" row.
            if acc['Combust'] or acc['UnderBeams']:
                signed_from_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
                western = signed_from_sun > 0
                labels.append('Under the rays of the Sun' + (', western/overtaken (93, 99)' if western else ' (93)'))

            # (94) Connecting with the infortunes from an assembly, opposition,
            # or square -- an ordinary harmful connection, and a testimony in
            # its own right. An earlier version folded this into 95's enclosure
            # and so never reported a single-infortune contact at all.
            # ONE testimony however many infortunes match -- 94 announces a
            # single item, and appending a label per matching planet let one
            # numbered testimony vote twice.
            _hit94 = []
            for r in rows:
                if r['aspect_name'] not in ('Conjunction', 'Square', 'Opposition') or planet not in (r['p1'], r['p2']):
                    continue
                other = r['p2'] if r['p1'] == planet else r['p1']
                if other in effective_infortunes() and _is_connected(r):
                    _hit94.append(other)
            if _hit94:
                labels.append(f"Connecting with {' and '.join(sorted(_hit94))} by assembly, square, or opposition (94)")

            # (95) Enclosed between the two infortunes -- separating from one,
            # connecting with the other (Sahl's own Enclosure, 119-123).
            is_enc, severe, sep, con = _sahl_enclosed(planet, effective_infortunes(), rows, blocking_pairs)
            if is_enc:
                labels.append(f'Enclosed between the infortunes, separating from {sep} and connecting to {con} (95, 119-123)')

            # (96) In its own fall.
            if ess['Fall']:
                labels.append('In its own fall (96)')

            # (97) Connecting with a planet falling from the Ascendant, or
            # separating from a planet that would have received it.
            # Likewise ONE testimony for 97, whose two clauses and any number of
            # matching planets previously produced a label each.
            _averse97, _sep97 = [], []
            for r in rows:
                if r['aspect_name'] == 'Aversion' or planet not in (r['light_name'], r['heavy_name']):
                    continue
                other = r['heavy_name'] if r['light_name'] == planet else r['light_name']
                if _is_connected(r) and _averse_to_ascendant(planetary_data[other]['longitude'], ascendant_lon):
                    _averse97.append(other)
                if (r['applicant'] or r['light_name']) == planet and r['motion'] == 'Separating' and _is_connected(r):
                    # "separating from a planet RECEIVING IT": the departed
                    # planet receives THIS one, so it must own the house or
                    # exaltation of THIS planet's degree (3, 52: Mars receives
                    # the Moon in Aries "because [Aries] is his house"). The
                    # earlier test looked the other way round -- whether this
                    # planet ruled the departed one's degree (Astra F08). fn 99
                    # ("I am not sure that these conditions must both exist
                    # at once") leaves the two clauses' conjunction open; the
                    # engine applies each clause on its own, a reading.
                    my_rulers = get_essential_rulers(planetary_data[planet]['longitude'])
                    if other in (my_rulers['domicile'], my_rulers['exaltation']):
                        _sep97.append(other)
            if _averse97 or _sep97:
                _parts = []
                if _averse97:
                    _parts.append(f"connecting with {' and '.join(sorted(_averse97))}, averse to the Ascendant")
                if _sep97:
                    _parts.append(f"separating from {' and '.join(sorted(_sep97))}, which would have received it")
                labels.append('; '.join(_parts).capitalize() + ' (97)')

            # (98) "In a house in which it did not have testimony (neither
            # house nor exaltation nor triplicity)" -- alien/peregrine, and a
            # standalone testimony. Two corrections here: the scope is those
            # three dignities only, so a bare term or face claim does NOT
            # rescue it (essential[]['Peregrine'] counts all five and is
            # therefore too lenient); and it carries no solar condition at all
            # -- an earlier version additionally required the planet to be
            # under the rays AND western, which is 99's clause, not 98's.
            alien_rulers = get_essential_rulers(lon)
            triplicity_key_local = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
            if planet not in (alien_rulers['domicile'], alien_rulers['exaltation'], alien_rulers[triplicity_key_local]):
                labels.append('Alien: no house, exaltation, or triplicity where it sits (98)')

            # (99) With the Head or Tail, without latitude.
            north_node_lon = planetary_data['North Node']['longitude']
            south_node_lon = (north_node_lon + 180.0) % 360.0
            node_dist = min(abs(((lon - north_node_lon + 180) % 360) - 180), abs(((lon - south_node_lon + 180) % 360) - 180))
            if node_dist < 12.0 and abs(lat) < 1.0:
                labels.append('With the Head or Tail, without latitude (99; 12 deg orb for either node, Ch.3, 107 and VII.6, 52)')

            # (100) Inverted: in the seventh sign from its own house (Detriment).
            if ess['Detriment']:
                labels.append('Inverted, in the seventh sign from its own house (100)')

            if labels:
                results.append({'Planet': planet, 'Weakness Testimonies': ', '.join(labels), 'Count': len(labels),
                                'Labels': labels})
        return results

def evaluate_abu_mashar_condition(planetary_data, natal_houses, sect, essential, accidental, jd, ascendant_lon, sim=None):
    """Planetary condition per Gr. Intr. VII.6: good
    fortune (1-20), strength (21-29), weakness (30-46), misfortune (47-62)
    -- plus, for the Moon only, Abu Ma'shar's OWN eleven corruptions of her
    (63-74, via _abu_mashar_moon_corruption()). Sahl's ten (The Introduction
    Ch.3, 103-112) are a different list, not a variant reading of this one,
    and have their own table, Corruption of the Moon, in the Sahl view.

    One reading to flag: 8's "while the Moon is made fortunate" is gated on
    zero of Abu Ma'shar's own eleven corruptions (63-74). Reading
    "fortunate" as "uncorrupted" is this app's own -- in this chapter's
    vocabulary being made fortunate means satisfying 1-14 -- and the Moon
    has no corruptions in under 1.5% of charts, so 8 almost never fires.
    Left as-is rather than replaced by another guess. The Rhetorius/PN4
    delineations downstream show both readings and take this table's Net
    only as a lean; the older Hellenistic net dignity score in
    evaluate_essential_dignities()/evaluate_accidental_dignities() is
    retained separately.

    This chapter was built early in the project from photographed pages
    that were later lost, and stayed unverifiable through several passes.
    It has now been checked line by line against the text. Corrected here:
    2 names its aspects (sextile, square, trine, or assembly) and excludes
    the opposition, which was being counted; 8 places no aspect restriction
    on the Moon's inspection, which had inherited 7's trine/sextile; 19's
    "merely fortunate" is the moderated own house (Saturn in Aquarius,
    Jupiter in Sagittarius, and so on), not any single dignity claim, so a
    bare face no longer earns it; 48 carries a degree condition ("less than
    the bound of a planet between them and the infortunes") that was absent
    entirely; 50 is the tenth or eleventh sign, where the ninth was also
    being admitted; and enclosure is now Abu Ma'shar's own two types with
    the dissolution of 60-61 -- see _abu_mashar_enclosed(), and note that a
    dissolution rule deleted earlier in this project as unsourced turns out
    to be exactly what 60 states.

    A second pass, once the OCR of the chapter replaced the photographs,
    closed every gap the first pass had recorded, since all of them were
    parentheses that the photographs had cropped or blurred: 14's reverse
    case (the fortunes in the luminaries' shares); 27's extra strength when
    a superior looks at the Sun from the sextile; the Sun-specific clauses
    in 28 and 45, including his exception for the ninth, "for it is his
    joy"; 33's harsher retrogradation for the inferiors, especially when
    also burned; 44's harsher form (empty in course, no fortune looking, not
    received); and 53's tighter 4-degree node orb for the Sun against the
    Moon's full 12.

    That pass also corrected three tests that had been reading only half of
    what the text says. 36 is the exact mirror of 13 and needs BOTH the
    sign's gender and the hemisphere inverted, where this had been firing on
    any planet not in its domain -- about 82 percent of placements, against
    28 percent for the real condition. 22 and 38 each name two states
    ("rising up in the north OR is northern"), now told apart by latitude
    speed. And 46's "beginning of easternization" is VII.2, 40-41's 12
    degrees for the inferiors, not a flat 15.

    Not implemented BY DECISION D-19 (2026-09-08; kept by the owner
    2026-09-11, decision sheet row 15): the masculine and feminine DEGREES
    that 13 and 36 name alongside the signs -- the table is in the corpus
    as Gr. Intr. V.19, Figure 59 (V.19, 7 with fn 108), and D-19's ground is
    that it disagrees with the sign's gender on half the zodiac and the
    three schemes agree on a third of it, so reading "or male degrees"
    into 13 and 36 would widen a vote the author does not commit to. (An
    earlier line here said "for want of a source in hand rather than by
    choice", which contradicted NOT_IMPLEMENTED_COVERAGE's D-19 entry.)
    52's "their own Dragons" -- each planet's own nodes -- IS read below
    since 2026-09-11 (order GAP-39), from the ephemeris's MEAN nodes: 52
    does not say mean or true, a reading declared on the label."""
    with doctrine(ABU_MASHAR):
        rows = _pairwise_configurations(planetary_data)
        reception_rows = evaluate_reception(planetary_data, sect, sim)
        connected_lookup = {}
        configured_lookup = {}  # frozenset -> aspect name, for non-Connected "look"/assembly checks
        for row in rows:
            pair = frozenset({row['p1'], row['p2']})
            is_conn = row['aspect_name'] != 'Aversion' and _is_connected(row)
            connected_lookup[pair] = is_conn
            configured_lookup[pair] = row['aspect_name']
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}

        def connected_to(planet, targets, aspects=None):
            for t in targets:
                if t == planet or not connected_lookup.get(frozenset({planet, t}), False):
                    continue
                if aspects is None or configured_lookup.get(frozenset({planet, t})) in aspects:
                    return True
            return False

        def configured_to(planet, targets, aspects=None):
            for t in targets:
                if t == planet:
                    continue
                name = configured_lookup.get(frozenset({planet, t}))
                if name and name != 'Aversion' and (aspects is None or name in aspects):
                    return True
            return False

        def averted_from(planet, targets):
            return all(configured_lookup.get(frozenset({planet, t})) == 'Aversion' for t in targets if t != planet)

        # Moon's own corruption count is needed (for §8's "Moon fortunate" test)
        # before the main per-planet loop, computed with no dependency on this
        # function's own output, to avoid recursion.
        # 8's "while the Moon is made fortunate" is judged on ABU MA'SHAR's
        # own eleven corruptions (63-74), not Sahl's ten. An Abu Ma'shar table
        # reaching into Sahl's list for its own paragraph was the last place
        # the two authors were still crossed. Note this is still a reading:
        # "made fortunate" in this chapter's vocabulary most naturally means
        # satisfying 1-14, and "uncorrupted" is the app's proxy for it.
        moon_corruption_count = len(_abu_mashar_moon_corruption(planetary_data, ascendant_lon, jd))

        results = {}
        for planet, data in planetary_data.items():
            if planet == 'North Node':
                continue
            lon, lat, speed = data['longitude'], data['latitude'], data['speed_in_lon']
            sign = get_zodiac_sign(lon)
            sign_idx = int(lon // 30)
            house = get_wsh_house(lon, ascendant_lon)
            ess, acc = essential[planet], accidental[planet]

            positive, negative = [], []

            # --- Good fortune (VII.6, 1-14) -----------------------------------
            # 2 names its aspects: "in the inspection of the fortunes from the
            # sextile, square, or trine, or are assembled with them" -- the
            # opposition is not among them, though an earlier version counted
            # any connected aspect. The note on 2 glosses "inspection" as an
            # aspect exact by degree, so the degree-based connection test is
            # the right gate.
            if connected_to(planet, FORTUNES, {'Conjunction', 'Sextile', 'Square', 'Trine'}):
                positive.append('Aspect/assembly with a fortune (2)')
            if averted_from(planet, effective_infortunes()):
                positive.append('Infortunes averted (3)')
            # 4: "Or they are separating from a FORTUNE and connecting with a
            # fortune" -- surrounded by benefics in time. An earlier version
            # tested separation from an INFORTUNE, which is the shape of 57's
            # enclosure (separating from one infortune, connecting with the
            # other) and belongs to the misfortune list, not this one.
            separating_fortune = any(
                (r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) in FORTUNES
                and _is_separating_in_nature(r)
                for r in rows
            )
            if separating_fortune and connected_to(planet, FORTUNES):
                positive.append('Separating fortune, connecting fortune (4)')
            # 5 / 62: "if the planet or sign was enclosed by the fortunes, then
            # that is of superior good fortune."
            is_enc_f, enc_kind_f, _diss = _abu_mashar_enclosed(planet, FORTUNES, planetary_data, rows)
            if is_enc_f:
                positive.append(f'Enclosed between the two fortunes, {enc_kind_f} (5, 62)')
            if acc['Cazimi']:
                positive.append('Cazimi (6)')
            # 7, like 2 and 8, says "in the INSPECTION of" -- and the note on 2
            # glosses inspection as an aspect exact by degree. This was the one
            # of the three still testing bare whole-sign configuration.
            if connected_to(planet, {'Sun'}, {'Trine', 'Sextile'}):
                positive.append('Trine/sextile the Sun (7)')
            # 8 puts no aspect restriction on the Moon's inspection, unlike 2
            # and 7 which name theirs; an earlier version limited it to the
            # trine and sextile borrowed from 7.
            if planet != 'Moon' and connected_to(planet, {'Moon'}) and moon_corruption_count == 0:
                positive.append('Aspects the Moon, uncorrupted by 63-74 (8)')
            # 9 is a conjunction, not a synonym: "quick in motion, INCREASING IN
            # LIGHT and number." VII.1, 19-21 defines increasing in light as
            # falling from the apogee toward the earth, so geocentric distance
            # decreasing. "Number" is the equation-table term of VII.1, 23-25,
            # which Dykes' note there says has no direct astrological import, so
            # it is not required. An earlier version accepted swiftness alone.
            #
            # For the MOON "increasing in light" is her glow, not her distance:
            # VII.2, 62-71 measure her conditions by "one-fourth of [her] glow",
            # and Sahl Ch.3, 112 has "decreasing in light (and that is [at] the
            # end of the [lunar] month)". The distance test agreed with waxing
            # in 47.5% of sampled charts -- chance. (VII.1, 22 allows the same
            # synodic sense for the superiors "in the manner that is said about
            # the Moon", but calls the apogee sense "the one agreed upon", so
            # the planets keep it.)
            if planet == 'Moon':
                increasing_in_light = 0.0 < (lon - planetary_data['Sun']['longitude']) % 360.0 < 180.0
            else:
                increasing_in_light = data.get('speed_in_dist', 0.0) < 0
            if acc['Swift'] and increasing_in_light:
                positive.append('Swift and increasing in light (9)')
            halb = ess['Domicile'] or ess['Exalt'] or ess['Triplicity'] or ess['Term'] or ess['Face'] or acc['Joy']
            if halb:
                positive.append('Halb (10)')
            brightness = _brightness_category(lon)
            if brightness == 'Bright':
                positive.append('Bright degree (11)')
            # Reception here is Abu Ma'shar's own. evaluate_reception() reads
            # the doctrine in force, and this function pins ABU_MASHAR above,
            # so the sidebar's Connection rule cannot reach it: all five
            # dignities count (VII.5, 129), reception runs in both directions
            # (130), and it holds by looking as well as by connection (133).
            # Under Sahl's narrower rule 43's "not received" fired on about
            # 81% of placements against about 8% under his own -- the case
            # that motivated doctrine().
            received = any(rec['Received'] == planet or (rec['Direction'] == 'Mutual'
                                                          and planet in rec['Receiver'].split(' & '))
                            for rec in reception_rows)
            for rec in reception_rows:
                if rec['Direction'] == 'Mutual':
                    if planet in rec['Receiver'].split(' & '):
                        positive.append(f"Mutual reception with {[x for x in rec['Receiver'].split(' & ') if x != planet][0]}")
                elif rec['Received'] == planet:
                    positive.append(f"Received by {rec['Receiver']} ({rec['Overall class'].split(':')[0].lower()}, via {rec['Via']})")
                elif rec['Receiver'] == planet:
                    positive.append(f"Receives {rec['Received']} into its own {rec['Via']}")
            if acc['Hayz']:
                positive.append('Domain/hayz (13)')
            # 14 runs in both directions: "if the luminaries were in the shares
            # of the two fortunes, for it is as though [the luminaries] are in
            # their own shares (AND LIKEWISE, IF THE TWO FORTUNES WERE IN THE
            # SHARES OF THE LUMINARIES)." The second clause was unreadable in
            # the photographs and went unimplemented; it is plain in the OCR.
            if planet in ('Sun', 'Moon'):
                fortune_dispositors = _dispositors(lon, sect) & FORTUNES
                if fortune_dispositors:
                    positive.append(f"Luminary in a fortune's share (14): {', '.join(sorted(fortune_dispositors))}")
            elif planet in FORTUNES:
                luminary_dispositors = _dispositors(lon, sect) & {'Sun', 'Moon'}
                if luminary_dispositors:
                    positive.append(f"Fortune in a luminary's share (14): {', '.join(sorted(luminary_dispositors))}")

            # Good-fortune grade (15-20), three types. [1] "doubled" is two or
            # more claims at once (16-18, Mercury in Virgo having house and
            # exaltation, and a third if also in his bound). [2] "merely
            # fortunate" is specifically the one of its own houses "in which
            # its nature is moderated and agrees with it" -- Saturn in
            # Aquarius, Jupiter in Sagittarius, Mars in Scorpio, Venus in
            # Taurus, and either luminary in its own house (19). [3] is the
            # other of its two houses (20).
            #
            # An earlier version awarded [2] for ANY single dignity claim, so a
            # bare face counted as being "merely fortunate"; 19 is about
            # domicile placement, and a lone minor claim fits none of the three
            # grades.
            claims = sum([ess['Domicile'], ess['Exalt'], ess['Triplicity'], ess['Term'], ess['Face']])
            if claims >= 2:
                grade = 'Doubled good fortune (16-18)'
            elif ess['Domicile'] and planet in PREFERRED_DOMICILE:
                grade = ('Fortunate (19)' if sign == PREFERRED_DOMICILE[planet]
                         else 'Below that / suitable (20)')
            elif ess['Domicile']:
                grade = 'Fortunate (19)'          # the luminaries have one house each
            else:
                grade = None
            if grade:
                positive.append(grade)

            n_good_fortune = len(positive)

            # --- Strength (VII.6, 21-29) --------------------------------------
            # 22: "RISING UP in the north or ARE northern" -- the stronger form
            # is northern latitude still increasing (VII.1, 34-35 puts the
            # maximum 90 deg past the planet's own Head), the weaker is simply
            # being on the northern side of its nodes.
            if lat > 0:
                if data.get('speed_in_lat', 0.0) > 0:
                    positive.append('Rising up in the north (22)')
                else:
                    positive.append('Northern latitude (22)')
            dist_range = GEOCENTRIC_DISTANCE_RANGE.get(planet)
            if dist_range and data['distance'] >= sum(dist_range) / 2.0:
                positive.append('Apogee circle, approximated (23)')
            station = None
            if planet in PLANET_SWE_IDS and abs(speed) <= STATION_SPEED_TOLERANCE:
                res_next, _ = swe.calc_ut(jd + 1.0, PLANET_SWE_IDS[planet])
                if res_next[3] > speed:
                    station = 'second'
                    positive.append('Second station (24)')
                elif res_next[3] < speed:
                    station = 'first'
            # 25 is "GOING OUT of the rays of the Sun" -- a specific station in
            # the synodic cycle, not "anywhere outside them". VII.2, 12 names it:
            # at the burnt limit "they have already gone past burning and shift
            # over to the third condition, and they are said to be simply 'under
            # the rays', and FROM THERE THEY BEGIN IN [THEIR] ADVANCEMENT TOWARDS
            # EASTERNIZATION, AND THEY ARE SUITABLE FOR GRANTING THEIR GREATER
            # YEARS AS WELL AS SPEAR-BEARING." VII.2 itself credits that band
            # with a benefit, and 32 denies the same benefit to the band on the
            # setting side ("they [are] not suitable for granting their greater
            # years"), so the departure is what carries the merit.
            #
            # So this is the under-the-rays band WITH the elongation opening.
            # It does overlap 34's weakness, necessarily -- both chapters say
            # what they say, and VII.6 lists strengths and weaknesses in
            # separate categories that can both hold. An earlier version
            # credited every planet anywhere outside the rays whose elongation
            # was opening, which is the whole eastern half of a superior's
            # cycle: 35% of placements, and a second vote alongside 27 for
            # every eastern superior.
            _signed_sun = ((lon - planetary_data['Sun']['longitude'] + 180.0) % 360.0) - 180.0
            elongation_opening = (
                planet != 'Sun'
                and (speed - planetary_data['Sun']['speed_in_lon']) * _signed_sun > 0
            )
            if acc['UnderBeams'] and elongation_opening:
                positive.append('Going out of the rays (25)')
            # 26 reads the WHOLE-SIGN place, while 39 below reads the quadrant
            # house with the five-degree carryover. Abu Ma'shar uses both
            # senses himself (42 names "falling or withdrawing" as two words)
            # and does not say which he means at 26, so the two readings are
            # left as they are and can both hold for one planet: in a
            # whole-sign stake yet dynamically cadent. An open reading,
            # recorded rather than resolved.
            stake_or_following = house in ANGLE_HOUSES | SUCCEDENT_HOUSES
            if stake_or_following:
                positive.append('Stake or following (26)')
            is_superior = planet in {'Saturn', 'Jupiter', 'Mars'}
            # "THE THREE inferior planets" (29, 46), against "the three
            # superiors" (27, 45). Venus and Mercury are only two: the third
            # inferior is the Moon, who is below the Sun in the same sense the
            # other two are. An earlier version left her out of both clauses,
            # so she was tested by neither the superior nor the inferior rule.
            is_inferior = planet in {'Venus', 'Mercury', 'Moon'}
            sun_lon = planetary_data['Sun']['longitude']
            signed_from_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
            is_eastern_of_sun = signed_from_sun < 0  # rises before the Sun
            # 27 carries a bonus that was unreadable in the photographs: "the
            # three superiors are eastern relative to the Sun (AND IF THEY LOOK
            # AT HIM FROM THE SEXTILE IT IS STRONGER FOR THEM)" -- cross-cited
            # to VII.2, 17-18, where the sextile is exactly the outer edge of
            # "proper, strong easternization."
            #
            # "Eastern relative to the Sun" is read as the hemisphere (VII.2, 2
            # calls the whole half "on the right side"), but never while under
            # the rays: VII.2, 14 reserves "easternizing" for after the 15/18
            # degrees are complete, and VII.6, 34 already counts the rays as
            # weakness. EASTERN_RULE = 'VII.2 band' narrows both 27 and 45 to
            # the bands VII.2 actually names (15/18 to 90 degrees eastern;
            # 90 down to 15 degrees western, 29-31). Hemisphere fires on 52% of
            # superior placements, the band on 25%.
            _e_lim, _w_lim = solar_rays_orb(planet)
            _elong = abs(signed_from_sun)
            if EASTERN_RULE == EASTERN_RULE_OPTIONS[1]:
                eastern_27 = is_eastern_of_sun and _e_lim <= _elong <= 90.0
                western_45 = (not is_eastern_of_sun) and _w_lim <= _elong <= 90.0
            else:
                eastern_27 = is_eastern_of_sun and _elong >= _e_lim
                western_45 = (not is_eastern_of_sun) and _elong >= _w_lim
            if is_superior and eastern_27:
                if configured_to(planet, {'Sun'}, {'Sextile'}):
                    positive.append('Superior, eastern of the Sun, by sextile (27)')
                else:
                    positive.append('Superior, eastern of the Sun (27)')
            # 28, 29, 45 and 46 all say QUADRANT. This read the whole-sign
            # house, which differs from the real quadrant for 52.3% of
            # placements and flips the gender verdict for 18.6%.
            quadrant_house = get_effective_house(lon, natal_houses)
            in_masculine_quadrant = quadrant_house in MASCULINE_QUADRANT_HOUSES
            if is_superior and in_masculine_quadrant:
                positive.append('Superior, in a masculine quadrant (28)')
            # 28's parenthesis covers the Sun, who is neither superior nor
            # inferior and so fell through both clauses: "and if the Sun was in
            # these two quadrants or in the male signs, then he is also strong,
            # UNLESS HE IS IN LIBRA" -- his own sign of fall.
            #
            # Note the shape: these are OR-clauses, so both halves matching is
            # still ONE condition satisfied. Each such paragraph contributes a
            # single entry, with the evidence named inside it, rather than one
            # vote per matching sub-clause.
            if planet == 'Sun' and sign != 'Libra':
                sun_28 = ([ 'masculine quadrant' ] if in_masculine_quadrant else []) + \
                         ([ 'masculine sign' ] if sign in MASCULINE_SIGNS else [])
                if sun_28:
                    positive.append(f"Sun, {' and '.join(sun_28)} (28)")
            inf_29 = ([ 'western of the Sun' ] if not is_eastern_of_sun else []) + \
                     ([ 'feminine quadrant' ] if not in_masculine_quadrant else [])
            if is_inferior and inf_29:
                positive.append(f"Inferior, {' and '.join(inf_29)} (29)")

            # --- Weakness (VII.6, 30-46) --------------------------------------
            # (negative starts here; everything before was good fortune/strength)
            # 31's "slow in course" takes VII.1, 30-31's exception like every
            # other speed test in this file: for Venus and Mercury the pace is
            # the SUN's motion that day, not their own mean. Measured against
            # their own means, Mercury read slow 32.2% of the time and Venus
            # 44.0%, against 18.3% and 17.1% correctly.
            _pace = (planetary_data['Sun']['speed_in_lon'] if planet in ('Venus', 'Mercury')
                     else AVERAGE_DAILY_MOTION.get(planet, 1.0))
            is_slow = 0 <= speed < _pace
            if is_slow:
                negative.append('Slow in course (31)')
            if station == 'first':
                negative.append('First station (32)')
            # 33's parenthesis, unreadable in the photographs: "(and the more
            # harmful retrogradation is the retrogradation of the two inferior
            # planets -- AND ESPECIALLY IF IN ADDITION TO THEIR RETROGRADATION
            # THEY ARE BURNED)."
            if acc['Retrograde']:
                if is_inferior and acc['Combust']:
                    negative.append('Retrograde, inferior and burned (33)')
                elif is_inferior:
                    negative.append('Retrograde, the harsher inferior kind (33)')
                else:
                    negative.append('Retrograde (33)')
            if acc['Combust'] or acc['UnderBeams']:
                negative.append(f"Under the rays, {acc['SolarSide']} (34)")
            # 35 names the dark degrees and nothing else. The dusky and empty
            # bands come from the separate brightness scheme of V.20 (Fig. 61);
            # an earlier version voted them here as extra "minor" negatives,
            # which is this app's invention, not 35's.
            if brightness == 'Dark':
                negative.append('Dark degree (35)')
            # 36 is the exact mirror of 13, and needs BOTH halves wrong: "the
            # male ones are in a FEMALE sign, or in the female degrees, by day
            # UNDER the earth, and by night above the earth." VII.1, 39 keeps a
            # single failure as the milder middle case ("it takes away from the
            # nature of balance"), reserving "the contrary of its domain" for
            # "if it was contrary to ALL of this." An earlier version fired this
            # on any planet merely not in its domain, which is most of them.
            if acc['ContraryDomain']:
                negative.append('Contrary to its domain (36)')
            if ess['Fall']:
                negative.append('Sign of fall (37)')
            # 38: "going DOWN in the south or IS southern" -- two conditions, as
            # 22 gives two on the northern side. Latitude speed separates them.
            if lat < 0:
                if data.get('speed_in_lat', 0.0) < 0:
                    negative.append('Going down in the south (38)')
                else:
                    negative.append('Southern latitude (38)')
            # 39, "falling from the stake or [from] what follows it." Dykes'
            # note reads this as dynamically cadent, while observing that Abu
            # Ma'shar might have meant a cadent whole sign, since he did not use
            # the word "withdrawing" here. Taken dynamically, against the
            # quadrant cusps, consistent with how Sahl's own "advancing" (Ch.3,
            # 83) is measured elsewhere in this file -- but see 42, which names
            # BOTH words and so gets both readings.
            #
            # And with the five-degree carryover, which is stated in exactly
            # this vocabulary: "the planet will NOT BE FALLING FROM THE STAKE
            # unless it was 5 degrees distant from its rear" (Fifty Aphorisms
            # #44, 88), "the planets will not fall from the stakes except after
            # 5 degrees" (On Nativities Ch.1.22, 9). A planet a few degrees
            # short of an angle was being called cadent here, which is the one
            # case both passages exist to rule out.
            quadrant_house = get_effective_house(lon, natal_houses)
            cadent_no_override = quadrant_house in CADENT_HOUSES
            if cadent_no_override:
                negative.append('Falling from the stake (39)')
            in_burned_path = 180.0 <= lon < 240.0
            in_harsh_burned_path = HARSH_BURNED_PATH[0] <= lon < HARSH_BURNED_PATH[1]
            if in_harsh_burned_path:
                negative.append('Burned path, harsh band (40)')
            elif in_burned_path:
                negative.append('Burned path (40)')
            if ess['Detriment']:
                negative.append('Opposition of own house / detriment (41)')
            # 42: "if it connects with a planet [that is] retrograde, corrupted,
            # in its own fall, or FALLING OR WITHDRAWING." Two separate words for
            # cadency, so both senses count -- dynamically cadent against the
            # quadrant cusps, or cadent by whole sign. An earlier version tested
            # whole sign alone.
            connects_debilitated = any(
                connected_lookup.get(frozenset({planet, other}), False)
                and (essential[other]['Fall'] or accidental[other]['Retrograde']
                     or get_wsh_house(planetary_data[other]['longitude'], ascendant_lon) in CADENT_HOUSES
                     or get_effective_house(planetary_data[other]['longitude'], natal_houses) in CADENT_HOUSES)
                for other in planetary_data if other not in (planet, 'North Node')
            )
            if connects_debilitated:
                negative.append('Connects to a debilitated planet (42)')
            if not received:
                negative.append('Not received (43)')
            # Emptiness of Course. Sahl's own base concept (The Introduction
            # Ch.3, 63, Fig. 19 -- illustrated there for the Moon, but item [10]
            # of his own 16-item list isn't restricted to her) is present-tense:
            # not currently connecting or uniting with any planet. Abu Ma'shar
            # sharpens this into the real, prospective definition used here --
            # no connection completes with ANY planet before this one leaves
            # its current sign (Gr. Intr. VII.5, 78, Fig. 124),
            # confirmed as his own addition by Dykes' footnote on 63 -- via the
            # forward simulation when available; falls back to Sahl's own
            # present-tense proxy (no currently-Applying-and-Connected pair)
            # when sim wasn't supplied.
            # A planet with no sign exit inside the horizon cannot be judged
            # prospectively -- the search is censored, not negative -- so it
            # takes the present-tense proxy instead of being called empty
            # because nothing perfected in 200 days.
            if sim is not None and sim['events'][planet]['sign_exits']:
                sign_exits = sim['events'][planet]['sign_exits']
                exit_day = sign_exits[0]
                empty_of_course = True
                for other in planetary_data:
                    if other in (planet, 'North Node'):
                        continue
                    raw_apart = abs(sign_idx - int(planetary_data[other]['longitude'] // 30))
                    signs_apart_other = min(raw_apart, 12 - raw_apart)
                    if signs_apart_other not in ASPECT_BY_SIGN_COUNT:
                        continue
                    target_angle = ASPECT_BY_SIGN_COUNT[signs_apart_other][1]
                    exact_day = _perfection_day(sim, planet, other, target_angle, before_day=exit_day)
                    if exact_day is not None and exact_day <= exit_day:
                        empty_of_course = False
                        break
            else:
                empty_of_course = not any(
                    ((row['applicant'] or row['light_name']) == planet and row['motion'] == 'Applying' and _is_connected(row))
                    for row in rows
                )
            # 44's parenthesis, unreadable in the photographs: "(and harsher
            # than that is if it was empty [in course], WITH NO FORTUNE LOOKING
            # AT IT OR PLANET BEING FAVORABLE TO IT)" -- three conditions
            # stacked, not just emptiness. "Favorable to it" is read as being
            # received by somebody, the same favor 43 measures.
            if ess['Peregrine']:
                unaided = empty_of_course and not configured_to(planet, FORTUNES) and not received
                if unaided:
                    negative.append('Exile, empty of course and unaided (44)')
                elif empty_of_course:
                    negative.append('Exile/peregrine, empty of course (44)')
                else:
                    negative.append('Exile/peregrine (44)')
            if is_superior and western_45:
                negative.append('Superior, western of the Sun (45)')
            if is_superior and not in_masculine_quadrant:
                negative.append('Superior, in a feminine quadrant (45)')
            # 45's parenthesis, the counterpart of 28's: "(and the weakness of
            # the Sun is if he is in the feminine signs or in these two quadrants
            # as well, UNLESS HE IS IN THE NINTH: FOR IT IS HIS JOY)." The Sun
            # previously fell through both the superior and inferior clauses and
            # so was never tested here at all. One entry per paragraph, as at 28.
            if planet == 'Sun' and house != 9:
                sun_45 = ([ 'feminine quadrant' ] if not in_masculine_quadrant else []) + \
                         ([ 'feminine sign' ] if sign in FEMININE_SIGNS else [])
                if sun_45:
                    negative.append(f"Sun, {' and '.join(sun_45)} (45)")
            # "The beginning of their easternization" is where VII.2, 40-41 puts
            # it: from leaving the burned band until strong easternization at
            # 12 deg, not the flat 15 deg an earlier version used.
            # VII.2, 40: the beginning is AFTER burning -- "when they are
            # distant from [the Sun] at a full 7 degrees ... they come to the
            # beginning of their advancement towards easternization" -- so the
            # burned band is excluded.
            inf_46 = ([ 'beginning of easternization' ]
                      if is_eastern_of_sun and SOLAR_BURNED_ORB[planet][0] <= abs(signed_from_sun) < solar_rays_orb(planet)[0] else []) + \
                     ([ 'masculine quadrant' ] if in_masculine_quadrant else [])
            if is_inferior and inf_46:
                negative.append(f"Inferior, {' and '.join(inf_46)} (46)")

            n_weakness = len(negative)

            # --- Misfortune (VII.6, 47-55) ------------------------------------
            # 48 attaches a degree condition: the planet is with the infortunes
            # by assembly, opposition, square, trine or sextile "and there are
            # LESS THAN THE BOUND OF [a single] PLANET between them and the
            # infortunes." The width of the bound the planet itself occupies is
            # used as that measure -- the text does not say whose bound, so this
            # is an interpretive choice, but it is at least derived from the
            # chart rather than assumed. An earlier version applied no degree
            # condition at all.
            bound_width = _current_bound_width(lon)
            # The infortune must be the OTHER planet in the pair. Testing
            # "either member is an infortune" made Mars and Saturn satisfy this
            # against any partner at all, since each is itself an infortune --
            # so both malefics were permanently near an infortune by definition.
            close_to_infortune = any(
                r['aspect_name'] != 'Aversion' and planet in (r['p1'], r['p2'])
                and ({r['p1'], r['p2']} - {planet}) & effective_infortunes()
                and abs(r['deviation']) < bound_width
                for r in rows
            )
            if close_to_infortune:
                negative.append(f'Connected to an infortune, within a bound ({bound_width:.0f} deg) (47-48)')
            term_lord = get_essential_rulers(lon)['term']
            if SIGN_TO_DOMICILE.get(sign) in effective_infortunes() or term_lord in effective_infortunes():
                negative.append('In the bound/house of an infortune (49)')
            for other in planetary_data:
                if other in (planet, 'North Node'):
                    continue
                other_lon = planetary_data[other]['longitude']
                other_idx = int(other_lon // 30)
                forward = (other_idx - sign_idx) % 12 + 1
                # 50: "elevated above them from the TENTH OR ELEVENTH from
                # their place (and it is bad for that in all of this IF THE
                # INFORTUNES WERE NOT RECEPTIVE OF THEM)" -- an earlier version
                # admitted the ninth, and read the reception clause as reception
                # by anybody, so being received by a fortune elsewhere in the
                # chart suppressed an overcoming by Saturn. The escape is that
                # THIS infortune receives it.
                if other in effective_infortunes() and forward in (10, 11):
                    received_by_other = any(
                        rec['Receiver'] == other and rec['Received'] == planet
                        or (rec['Direction'] == 'Mutual'
                            and {planet, other} <= set(rec['Receiver'].split(' & ')))
                        for rec in reception_rows
                    )
                    if not received_by_other:
                        negative.append(f'Overcome by {other}, unreceived (50)')
                        break
            if configured_to(planet, {'Sun'}, {'Conjunction', 'Square', 'Opposition'}):
                negative.append('Assembly/square/opposition to the Sun (51)')
            north_node_lon = planetary_data['North Node']['longitude']
            south_node_lon = (north_node_lon + 180.0) % 360.0
            head_dist = abs(((lon - north_node_lon + 180) % 360) - 180)
            tail_dist = abs(((lon - south_node_lon + 180) % 360) - 180)
            with_head = head_dist <= tail_dist
            node_dist = min(head_dist, tail_dist)
            # 52 sets the general orb at 12 deg. 53 then grades it: "the most
            # harmful they can be for the SUN is if there were 4 deg between him
            # and them ... and the most harmful they can be for the MOON is if
            # there were 12 deg between her and one of them." So the Sun's
            # damage concentrates in a narrow 4 deg, the Moon's spans the whole
            # 12 deg. An earlier version applied one flat 12 deg to everything.
            #
            # 54-55 add a polarity, which the earlier version collapsed by
            # taking the nearer node without recording which it was: "the Head's
            # nature is that of increase ... the nature of the Tail is decrease,"
            # so the Head is a fortune with the fortunes and an infortune with
            # the infortunes, and the Tail the reverse. Abu Ma'shar reports this
            # as the ancients' view rather than asserting it ("some of the
            # ancients claimed"), so it is named in the label and not scored
            # separately.
            if node_dist <= 12.0:
                node_name = 'Head' if with_head else 'Tail'
                if planet in FORTUNES:
                    polarity = 'increasing its good' if with_head else 'taking from its good'
                elif planet in INFORTUNES:
                    polarity = 'increasing its evil' if with_head else 'taking from its evil'
                else:
                    polarity = 'increase' if with_head else 'decrease'
                worst = ((planet == 'Sun' and node_dist <= 4.0)
                         or (planet == 'Moon' and node_dist <= 12.0))
                if planet == 'Sun' and not worst:
                    negative.append(f'With the {node_name}, {polarity} (52, 54-55)')
                elif worst:
                    negative.append(f'With the {node_name} at its worst, {polarity} (52-55)')
                else:
                    negative.append(f'With the {node_name}, {polarity} (52-55)')
            # 52's FIRST clause: "Or they are with the Heads of their OWN Dragons,
            # or with their Tails ... and between them are 12 degrees or less" --
            # each planet's own nodes, read from the ephemeris at the moment
            # (swe.nod_aps_ut). MEAN nodes: 52 does not say mean or true, a
            # reading said on the label; the Moon's node above is the chart's
            # TRUE node (owner, 2026-09-07). The luminaries have no nodes of
            # their own in this sense. Order GAP-39, 2026-09-11.
            if jd is not None and planet in PLANET_SWE_IDS and planet not in ('Sun', 'Moon'):
                try:
                    own = swe.nod_aps_ut(jd, PLANET_SWE_IDS[planet], swe.NODBIT_MEAN)
                    own_head, own_tail = own[0][0] % 360.0, own[1][0] % 360.0
                except Exception:
                    own_head = own_tail = None
                if own_head is not None:
                    d_head = abs(((lon - own_head + 180) % 360) - 180)
                    d_tail = abs(((lon - own_tail + 180) % 360) - 180)
                    if min(d_head, d_tail) <= 12.0:
                        negative.append(f"With its own {'Head' if d_head <= d_tail else 'Tail'} within 12 degrees "
                                        f"(52, \"their own Dragons\"; the mean node, a reading -- 52 does not say mean or true)")

            # --- Enclosure by the infortunes (VII.6, 56-62) -------------------
            # Abu Ma'shar's OWN two types, not Sahl's borrowed: see
            # _abu_mashar_enclosed(). The standalone Enclosure table elsewhere
            # remains Sahl's (Ch.3, 119-123); this is the VII.6 table, so it
            # uses VII.6's version, including the dissolution of 60-61 that an
            # earlier pass of this project deleted as unsourced.
            #
            # The dissolution is a positive entry belonging to the MISFORTUNE
            # section (56-62), not to Strength (21-29). It is appended after the
            # strength count has already been taken, so the boundary is recorded
            # here rather than inferred from list length -- an earlier version
            # inferred it, and filed every dissolved enclosure under Strength.
            n_positive_through_strength = len(positive)
            is_enc, enc_kind, dissolver = _abu_mashar_enclosed(planet, effective_infortunes(), planetary_data, rows)
            if is_enc:
                if dissolver:
                    positive.append(f'Enclosure by the infortunes dissolved by {dissolver} (60-61)')
                else:
                    negative.append(f'Enclosed by the infortunes, {enc_kind} (56-58)')

            # --- Corruption of the Moon (VII.6, 63-74), Moon only -------------
            # This is Abu Ma'shar's OWN eleven, which is what belongs in a table
            # that is otherwise wholly VII.6. Sahl's ten (The Introduction Ch.3,
            # 103-112) have their own table in the Sahl view, under their own numbering --
            # the two lists overlap only partly, and neither is a variant
            # reading of the other.
            moon_defects = _abu_mashar_moon_corruption(planetary_data, ascendant_lon, jd) if planet == 'Moon' else []

            # --- The Good/Bad verdict -----------------------------------------
            # NOT Abu Ma'shar's. He enumerates these conditions; he nowhere adds
            # them up, and no weighting or tie rule appears anywhere in VII.6.
            # Counting the labels and subtracting is this app's own convenience,
            # kept because the Rhetorius/PN4 delineations downstream have to
            # choose one of two readings, and labelled as a heuristic everywhere
            # it is shown.
            #
            # Two distortions in the raw count are corrected here, both of which
            # let one underlying fact vote many times:
            #
            # (1) The Moon was the only planet handed a SECOND full checklist,
            # her corruptions, each as its own vote. Over 325 sampled charts
            # that pushed her average negative tally to 10.1 against 6.5-7.9 for
            # every other planet, and she came out "Good" 24.9% of the time
            # against 40-61% for the rest -- an artifact of the arithmetic, not
            # a judgement about the Moon. Her defects still show in full below;
            # they now contribute one entry to the tally.
            #
            # (2) Reception can yield several rows for one planet (more so under
            # Abu Ma'shar's wider profile, which counts all five dignities and
            # runs in both directions), and each was voting separately. Received
            # or not received is one fact, so it counts once.
            reception_labels = [l for l in positive if l.startswith(('Received', 'Receives', 'Mutual reception'))]
            positive_votes = [l for l in positive if l not in reception_labels]
            if reception_labels:
                positive_votes.append(reception_labels[0])
            negative_votes = list(negative)
            if moon_defects:
                negative_votes.append(f'Corruption of the Moon ({len(moon_defects)} defects)')

            net = len(positive_votes) - len(negative_votes)
            results[planet] = {
                # The four sections VII.6 itself is organised into, reported
                # separately so the picture doesn't collapse to one number.
                'Good Fortune': n_good_fortune,
                'Strength': n_positive_through_strength - n_good_fortune,
                'Weakness': n_weakness,
                'Misfortune': (len(negative) - n_weakness) + (len(positive) - n_positive_through_strength),
                'Moon Defects': len(moon_defects),
                'Positive Score': len(positive),
                'Negative Score': len(negative) + len(moon_defects),
                'Net': net,
                'Condition': 'Good' if net >= 0 else 'Bad',
                'Positive Labels': positive,
                'Negative Labels': negative + moon_defects,
            }
        return results

def _twelfth_part_sign(lon):
    """The sign holding a point's twelfth-part. Each sign's 30 degrees are
    mapped onto the twelve signs in order, 2.5 degrees apiece, beginning
    with the sign itself.

    PROVENANCE: Gr. Intr. V.18, 1-3 (Figure 57) STATES the construction --
    each sign "divided ... into twelve divisions, so that each division is
    2 1/2 degrees" (1), "the first division of it is like the nature of the
    sign itself" (2), and the short calculation: take the degree and minute
    from the beginning of the sign, "multiply it by 12, and ... cast out
    what it amounts to from the beginning of that sign, 30 for every sign"
    (3). Both authors use it: the Moon's twelfth-part falling to Saturn or
    Mars is her fifth corruption (VII.6, 68), assembly with them is one of
    the ways planets meet (VII.4, 2), and Sahl devotes On Nativities 2.6 to
    them. An earlier note here said no text in hand stated the formula; it
    was written before Book V of the Great Introduction entered the corpus
    (Astra audit F14; work order PN4R-4n-2, 2026-09-11)."""
    sign_idx = int(lon // 30)
    step = int((lon % 30.0) // 2.5)
    return get_zodiac_sign(((sign_idx + step) % 12) * 30.0 + 15.0)

def _abu_mashar_moon_corruption(planetary_data, ascendant_lon, jd=None):
    """The ELEVEN corruptions of the Moon, Abu Ma'shar's own (Great
    Introduction VII.6, 63-74) -- announced at 63 as "in 11 ways" and
    enumerated one per paragraph through 74.

    Kept deliberately separate from Sahl's ten (The Introduction Ch.3,
    103-112, in _corruption_of_the_moon_labels()). They are not two
    transcriptions of one list: Abu Ma'shar has eclipse, the twelfth-part of
    Saturn or Mars, southern latitude and the ninth house, none of which
    appear in Sahl; Sahl has her own fall, connection with a fallen planet,
    and wildness, none of which appear here. The VII.6 condition table uses
    this list because that table is otherwise wholly VII.6; Sahl's tables
    keep Sahl's.

    64's "harsher" clause -- eclipsed in the natal sign or its trine or
    square -- needs a radix separate from the chart being judged and is not
    implemented for a natal chart, which IS the root."""
    with doctrine(ABU_MASHAR):
        moon = planetary_data['Moon']
        lon, lat, speed = moon['longitude'], moon['latitude'], moon['speed_in_lon']
        sun_lon = planetary_data['Sun']['longitude']
        sign = get_zodiac_sign(lon)
        rows = _pairwise_configurations(planetary_data)
        labels = []

        signed_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
        elongation = abs(signed_sun)

        # [1] (64) "If she is eclipsed." A LUNAR eclipse in progress at the
        # birth moment, asked of the ephemeris globally: lun_eclipse_when()
        # gives the next eclipse's contact times, and the Moon is eclipsed
        # while the moment lies inside them. The earlier version asked
        # lun_eclipse_how() at geoposition (0, 0, 0), which reports 0 whenever
        # the eclipse is below the horizon AT GREENWICH, and then fell back to
        # a 12-degree node/syzygy window that also counted SOLAR eclipses
        # (where she eclipses rather than is eclipsed) -- it labelled 3 of 240
        # sampled charts against 0 real eclipses. A penumbral-only passage is
        # reported as such rather than silently equated with the umbral kind.
        north_node_lon = planetary_data['North Node']['longitude']
        node_dist = min(abs(((lon - north_node_lon + 180) % 360) - 180),
                        abs(((lon - (north_node_lon + 180.0) + 180) % 360) - 180))
        if jd is not None:
            try:
                _r, _t = swe.lun_eclipse_when(jd - 3.0, swe.FLG_SWIEPH, 0, False)
                _umbral = bool(_t[2] and _t[3] and _t[2] <= jd <= _t[3])
                _penumbral = bool(_t[6] and _t[7] and _t[6] <= jd <= _t[7])
                if _umbral:
                    labels.append('Eclipsed (64)')
                elif _penumbral:
                    labels.append('Eclipsed, penumbral only (64)')
            except Exception:
                pass

        # [2] (65) Under the rays: 12 degrees between her and the Sun's body,
        # "in the front or in the rear."
        if elongation <= 12.0:
            labels.append('Within 12 degrees of the Sun (65)')

        # [3] (66) The same 12 degrees around the minute of his opposition,
        # "going towards his opposition or flowing away from it."
        if abs(elongation - 180.0) <= 12.0:
            labels.append('Within 12 degrees of the Sun\'s opposition (66)')

        # [4] (67) "With the infortunes or they were looking at her" -- assembly
        # or aspect, and the looking half is whole-sign by its own wording.
        for infortune in sorted(effective_infortunes()):
            row = next((r for r in rows if {r['p1'], r['p2']} == {'Moon', infortune}), None)
            if row and row['aspect_name'] != 'Aversion':
                labels.append(f"With or looked at by {infortune} (67)")
                break

        # [5] (68) In the twelfth-part of Saturn or Mars -- the twelfth-part
        # falling in a sign those two rule.
        tp_sign = _twelfth_part_sign(lon)
        tp_lord = SIGN_TO_DOMICILE.get(tp_sign)
        if tp_lord in effective_infortunes():
            labels.append(f'In the twelfth-part of {tp_lord} ({tp_sign}) (68)')

        # [6] (69) With the Head or Tail within 12 degrees.
        if node_dist <= 12.0:
            labels.append('With the Head or Tail, within 12 degrees (69)')

        # [7] (70) "Southern OR going down in the south" -- two states, as at 38.
        if lat < 0:
            labels.append('Going down in the south (70)' if moon.get('speed_in_lat', 0.0) < 0
                          else 'Southern in latitude (70)')

        # [8] (71) In the burned path, "and that is Libra and Scorpio" -- the
        # whole two signs here, wider than VII.6, 40's harsher 19 Libra to
        # 3 Scorpio band (HARSH_BURNED_PATH).
        if sign in ('Libra', 'Scorpio'):
            labels.append('In the burned path, Libra or Scorpio (71)')

        # [9] (72) At the end of the signs, "because at that time she will be in
        # the bounds of the infortunes" -- the reason names the test, so this is
        # the sign's LAST bound rather than a fixed number of degrees.
        if _in_last_bound(lon):
            labels.append('In the last bound of the sign (72)')

        # [10] (73) Slow, "when she goes at less than her mean motion."
        if 0 <= speed < AVERAGE_DAILY_MOTION['Moon']:
            labels.append('Slow in motion (73)')

        # [11] (74) In the ninth house from the Ascendant.
        if get_wsh_house(lon, ascendant_lon) == 9:
            labels.append('In the ninth house (74)')

        return labels

MOON_DEFECT_IDS = (103, 104, 105, 106, 107, 108, 109, 110, 111, 112)

def evaluate_corruption_of_the_moon(planetary_data, ascendant_lon, sect):
    """The ten defects of the Moon (Sahl, The Introduction Ch.3, 103-112).
    Replaces an earlier version built from Abu Ma'shar's own, differently-
    numbered eleven-item list (Gr. Intr. VII.6, 63-74) without
    cross-checking it against Sahl's own item [16] -- four of that
    version's items (eclipsed, the twelfth-part of an infortune, southern
    latitude, ninth house from the Ascendant) don't appear anywhere in
    Sahl's ten and have been dropped; several genuine gaps against Sahl's
    own list (Moon in her own fall, connecting with a planet in its own
    fall, falling from the stakes or connecting with a falling planet,
    wild/empty of course, waning in light) are added here for the first
    time.

    Re-verified against the source's full paragraph text (rather than
    partial photo transcriptions): items [5] and [6] were corrected --
    (107) requires the Node to be in the SAME sign as the Moon, not just
    within 12 degrees regardless of sign; (108) requires the LAST bound of
    the sign specifically (every sign's final Egyptian term is an
    infortune's, but not every infortune-ruled bound is the sign's last
    one -- the earlier version matched any of them). Item [7] (109) is a
    plain disjunction in the source and is implemented as one. Item [9]'s
    "wild" (111) is confirmed, on the full text, to be glossed there as
    "not connecting with any of the planets" -- the same present-tense
    wording as Emptiness of Course (63) -- so its existing implementation
    was left as-is.

    Shown as its own table, Corruption of the Moon, in the Sahl view of the
    Configurations page.

    Returns one record per numbered testimony, 103-112, so the count is
    "how many of Sahl's ten" and never "how many clauses matched". 104
    ("in her own fall, OR connecting with a star in its fall") and 109
    ("falling from the stakes, OR connecting with a planet falling") can
    each be satisfied by several planets at once, and 112 by slowness and
    waning together; an earlier version appended one label per match and
    counted the labels, so a list announced as ten defects could exceed
    ten and one paragraph could vote three times. Every clause is still
    reported, under its paragraph:

        {'testimonies': {103: {'matched': False, 'clauses': []},
                         104: {'matched': True, 'clauses': ['In her own fall, Scorpio',
                                                             'Connecting with Venus, itself in its own fall']},
                         ...},
         'unique_testimony_count': 3,      # of ten -- the only number to score with
         'matching_instances': 5,          # every clause that matched, for the record
         'labels': ['In her own fall, Scorpio (104)', ...]}"""
    with doctrine(SAHL):
        moon = planetary_data['Moon']
        lon, speed = moon['longitude'], moon['speed_in_lon']
        sun_lon = planetary_data['Sun']['longitude']
        sign = get_zodiac_sign(lon)
        rows = _pairwise_configurations(planetary_data)
        testimonies = {n: {'matched': False, 'clauses': []} for n in MOON_DEFECT_IDS}
        labels = []

        def hit(n, clause, cite=None):
            """Record one matching clause under testimony n. The label keeps
            the paragraph number for the table; the count does not read it."""
            testimonies[n]['matched'] = True
            testimonies[n]['clauses'].append(clause)
            labels.append(f'{clause} ({cite or n})')

        def connected_row(other):
            return next((r for r in rows if {r['p1'], r['p2']} == {'Moon', other}), None)

        # [1] (103) Burned, within 12 degrees of the Sun, front or behind.
        sun_dist = abs(((lon - sun_lon + 180) % 360) - 180)
        if sun_dist <= 12.0:
            hit(103, 'Burned, within 12 degrees of the Sun')

        # [2] (104) In the degrees of her own fall (Scorpio), or connecting
        # with a planet in ITS own fall.
        if sign in FALLS.get('Moon', []):
            hit(104, 'In her own fall, Scorpio')
        for other in planetary_data:
            if other in ('Moon', 'North Node'):
                continue
            r = connected_row(other)
            if r and r['aspect_name'] != 'Aversion' and _is_connected(r):
                other_sign = get_zodiac_sign(planetary_data[other]['longitude'])
                if other_sign in FALLS.get(other, []):
                    hit(104, f'Connecting with {other}, itself in its own fall')

        # [3] (105) Opposed to the Sun, within 12 degrees, not yet having
        # reached the exact opposition (still approaching, not past it).
        opp_target = (sun_lon + 180.0) % 360.0
        signed_to_opp = ((opp_target - lon + 180) % 360) - 180
        if 0 <= signed_to_opp <= 12.0:
            hit(105, "Approaching the Sun's opposition, within 12 degrees")

        # [4] (106) Assembled with an infortune, or looking at it from a
        # square or opposition (sextile/trine don't count here) -- or enclosed
        # between the two infortunes (separating from one, connecting with the
        # other -- Sahl's own Enclosure test, 119-123).
        if any(row['aspect_name'] in ('Conjunction', 'Square', 'Opposition')
               and 'Moon' in (row['p1'], row['p2'])
               and (row['p1'] in effective_infortunes() or row['p2'] in effective_infortunes())
               for row in rows):
            hit(106, 'Assembled with, square, or opposed by an infortune')
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
        is_enc, severe, _sep, _con = _sahl_enclosed('Moon', effective_infortunes(), rows, blocking_pairs)
        if is_enc:
            hit(106, 'Enclosed between the two infortunes' + (', severe' if severe else ''), cite='106, 119-123')

        # [5] (107) With the Head or Tail, IN ONE SIGN, less than 12 degrees
        # between them -- same-sign co-presence (Sahl's own "connection" shape)
        # plus the Moon's own light-radius, not merely raw closeness in degree
        # regardless of sign boundary.
        north_node_lon = planetary_data['North Node']['longitude']
        south_node_lon = (north_node_lon + 180.0) % 360.0
        for node_lon in (north_node_lon, south_node_lon):
            if get_zodiac_sign(node_lon) == sign and abs(((lon - node_lon + 180) % 360) - 180) < 12.0:
                hit(107, 'With the Head or Tail, in one sign and under 12 degrees')
                break

        # [6] (108) In the twelfth sign from her own house (Gemini, since her
        # house is Cancer), or in the LAST degrees of the sign specifically --
        # the final Egyptian-term division, which (per the table) is always
        # ruled by one of the two infortunes, not just any infortune-ruled
        # bound elsewhere in the sign (e.g. Aries' 20-25 degree bound is
        # Mars's but isn't the sign's last one).
        if sign == 'Gemini':
            hit(108, "In Gemini, the twelfth sign from her own house")
        if _in_last_bound(lon):
            hit(108, "In the last degrees of the sign, the infortunes' bound")

        # [7] (109) "Falling from the stakes, or connecting with a planet
        # falling from the stakes" -- a plain disjunction, verbatim. (A prior
        # edit replaced this with a cadent + averse-to-Ascendant + separating-
        # from-an-infortune predicate, which is Weakness 91/97 material and
        # appears nowhere in 109; reverted.)
        moon_house = get_wsh_house(lon, ascendant_lon)
        if moon_house in CADENT_HOUSES:
            hit(109, 'Falling from the stakes')
        for other in planetary_data:
            if other in ('Moon', 'North Node'):
                continue
            r = connected_row(other)
            if r and r['aspect_name'] != 'Aversion' and _is_connected(r):
                if get_wsh_house(planetary_data[other]['longitude'], ascendant_lon) in CADENT_HOUSES:
                    hit(109, f'Connecting with {other}, itself falling from the stakes')

        # [8] (110) "in the burned path, and that is at the end of Libra and
        # the beginning of Scorpio". SAHL GIVES NO DEGREES. The span tested,
        # 19 Libra to 3 Scorpio, is Abu Ma'shar's harsher band (Gr. Intr.
        # VII.6, 40: "harsher than that is if it was from 19 Libra up to 3
        # Scorpio"), the one fn 120 reports, BORROWED here as the only
        # author-stated region of the shape Sahl describes. Firing on the two
        # whole signs would over-read Sahl (early Libra is not "the end of
        # Libra"). Owner, 2026-09-11 (decision sheet row 9, DEC-D-5 as
        # implemented); an earlier comment claimed Sahl's wording "matches"
        # the band, which it does not state. Readings, not tests: 15 Libra to
        # 15 Scorpio is the definition "often" given (Dykes, Carmen p. 258 fn
        # 104; the Course Glossary); Dorotheus's own (Carmen p. 258, 6: the
        # equinoctial point taken southward) is a different construction.
        if HARSH_BURNED_PATH[0] <= lon < HARSH_BURNED_PATH[1]:
            hit(110, 'In the burned path, "the end of Libra and the beginning of Scorpio" -- Sahl gives no degrees; '
                     "the 19 Libra-3 Scorpio span is Gr. Intr. VII.6, 40's harsher band (fn 120), borrowed")

        # [9] (111) Wild -- empty of course, not connecting with any planet.
        # Sahl's own present-tense definition (not Abu Ma'shar's later,
        # prospective sharpening used elsewhere in this file).
        if not any((row['applicant'] or row['light_name']) == 'Moon' and row['motion'] == 'Applying' and _is_connected(row) for row in rows):
            hit(111, 'Wild, empty of course')

        # [10] (112) Slow in course, or waning in light (past full, heading
        # back toward new).
        if 0 <= speed < AVERAGE_DAILY_MOTION['Moon']:
            hit(112, 'Slow in course')
        if 180.0 < ((lon - sun_lon) % 360.0) < 360.0:
            hit(112, 'Waning in light')

        return {
            'testimonies': testimonies,
            'unique_testimony_count': sum(t['matched'] for t in testimonies.values()),
            'matching_instances': len(labels),
            'labels': labels,
        }

def _corruption_of_the_moon_labels(planetary_data, ascendant_lon, sect):
    """The flat label list, one per matching clause. For display; the
    testimony count is evaluate_corruption_of_the_moon()['unique_testimony_count']."""
    return evaluate_corruption_of_the_moon(planetary_data, ascendant_lon, sect)['labels']


def mashaallah_condition(house_i, lord, planetary_data, ascendant_lon):
    """Masha'allah's operating condition for his lord-of-the-Nth readings,
    stated at the end of every such section: "Work in this chapter if the
    lord of the third and the third [itself] were free of the infortunes,
    and the fortunes do not witness" (On Nativities 3.10, 14; likewise
    4.11, 24; 6.3.4, 24; 7.1, 217; 9.4, 35; 10.2.4, 13; 11.1, 28; 12.1, 47).
    Whole-sign, as the house is: an infortune is "on" the house or its lord
    by assembly, square or opposition (Sahl's own affliction set elsewhere,
    Ch. 3, 119-123 and 106); a fortune "witnesses" by any whole-sign aspect
    or assembly. The lord itself is not counted against itself. Returns
    ('met', '') or ('not met', why). Decision D-6, 2026-09-08: shown as a
    column, never used as a filter -- the condition holds on roughly one
    house-lord row in ten."""
    asc_idx = int(ascendant_lon // 30)
    house_idx = (asc_idx + house_i - 1) % 12
    lord_idx = int(planetary_data[lord]['longitude'] // 30)
    ordinal = {1: 'st', 2: 'nd', 3: 'rd'}.get(house_i if house_i < 20 else house_i % 10, 'th')
    house_name = f"the {house_i}{ordinal}"
    reasons = []
    for other, data in planetary_data.items():
        if other == 'North Node' or other == lord:
            continue
        other_idx = int(data['longitude'] // 30)
        if other in INFORTUNES:
            for target, name in ((house_idx, house_name), (lord_idx, f'its lord {lord}')):
                rel = (other_idx - target) % 12
                if rel in (0, 3, 6, 9):
                    how = {0: 'with', 3: 'square', 6: 'opposite', 9: 'square'}[rel]
                    reasons.append(f'{other} {how} {name}')
        elif other in FORTUNES:
            for target, name in ((house_idx, house_name), (lord_idx, f'its lord {lord}')):
                rel = (other_idx - target) % 12
                if rel not in (1, 5, 7, 11):
                    how = {0: 'with', 2: 'sextile', 3: 'square', 4: 'trine', 6: 'opposite', 8: 'trine', 9: 'square', 10: 'sextile'}[rel]
                    reasons.append(f'{other} witnesses {name} ({how})')
    return ('met', '') if not reasons else ('not met', '; '.join(reasons))

def evaluate_house_lords(planetary_data, ascendant_lon):
    """For each Whole Sign topical house (1-12), find its domicile lord and
    the WSH house that lord is physically placed in, then look up
    Masha'allah's delineation for that [placed_in][ruled_house] pairing,
    with his own operating condition (mashaallah_condition) beside it."""
    asc_idx = int(ascendant_lon // 30)
    results = []
    for house_i in range(1, 13):
        sign_idx = (asc_idx + house_i - 1) % 12
        cusp_sign = get_zodiac_sign(sign_idx * 30 + 15.0)  # mid-sign probe, sign is constant across the whole 30 deg
        domicile_lord = SIGN_TO_DOMICILE.get(cusp_sign)

        if domicile_lord not in ('Sun', 'Moon') and domicile_lord not in planetary_data:
            continue

        lord_lon = planetary_data[domicile_lord]['longitude']
        placed_in = get_wsh_house(lord_lon, ascendant_lon)
        text = MASHAALLAH_LORDS.get(placed_in, {}).get(house_i, '-')
        status, why = mashaallah_condition(house_i, domicile_lord, planetary_data, ascendant_lon)

        results.append({
            'Topical House': house_i,
            'Cusp Sign': cusp_sign,
            'Domicile Lord': domicile_lord,
            'Placed in (WS place)': placed_in,
            "Masha'allah's condition": status if not why else f'{status}: {why}',
            "Masha'allah Signification": text,
        })
    return results

# --- Victors (Almutens) of significant points -- ibn Ezra (1485/1537),
# TNAC Handy Tables Lesson 20 -- generalizing the same weighted essential-
# dignity lookup already used below for the Prenatal Syzygy's Almuten to
# the Ascendant, Sun, Moon, and Lot of Fortune. Two parallel weighting
# traditions are given directly in the source, disagreeing on whether
# Bound or Triplicity ranks higher, so both are computed side by side
# rather than silently picking one:
VICTOR_WEIGHTS = {
    "Older (al-Tabari/Masha'allah)": {'domicile': 5, 'exaltation': 4, 'triplicity': 2, 'term': 3, 'face': 1},
    "Newer (Al-Qabisi/Abu Ma'shar)": dict(ESSENTIAL_DIGNITY_WEIGHTS),
}

# "Places" bonus wheels (Handy Tables Lesson 20): a candidate planet's own
# Whole-Sign-House placement adds this many points to its total, on top of
# its essential-dignity claim at the point being profiled. Both are
# permutations of 1-12. Which wheel goes with which weighting scheme is not
# stated in the source, so evaluate_victors() computes all four combinations
# and marks the two same-tradition pairings (ibn Ezra's wheel with the
# newer/Al-Qabisi weights, Masha'allah's with the older) as the interpretive
# presets they are.
VICTOR_PLACES_VALUES = {
    "Older (al-Tabari/Masha'allah)": {1: 12, 2: 3, 3: 5, 4: 7, 5: 8, 6: 1, 7: 9, 8: 4, 9: 6, 10: 11, 11: 10, 12: 2},
    "Newer (Al-Qabisi/Abu Ma'shar)": {1: 12, 2: 6, 3: 3, 4: 9, 5: 7, 6: 1, 7: 10, 8: 4, 9: 5, 10: 11, 11: 8, 12: 2},
}

def evaluate_victors(planetary_data, ascendant_lon, lot_of_fortune, syzygy_lon, sect, chronocrats):
    """The victor of the chart, per ibn Ezra's victor #1 worksheet
    (1485/1537, Handy Tables Lesson 20).

    The worksheet is ONE table: the seven planets are its columns, and its
    rows are the five points -- Sun, Moon, Ascendant, Lot of Fortune, and
    the prenatal New/Full Moon -- followed by Lord of the Day (+7), Lord of
    the Hour (+6) and Places. Every column is then summed into a single
    Totals row, and the highest total is the victor. So this produces one
    aggregate victor per weighting scheme, and the output mirrors the
    worksheet grid so a student can check it cell by cell against a
    hand-filled sheet.

    Rebuilt from an earlier version that computed a SEPARATE victor for
    each of four points, omitted the prenatal syzygy row entirely, and
    added the Lord of the Day, Lord of the Hour and Places bonuses afresh
    to every one of those four tallies -- so the auxiliary rows, which
    appear once on the sheet, were counted four times over, and the four
    winners were reported where the sheet asks for one.

    The two axes are independent and are kept that way. The five dignity
    weights come from the older (Umar al-Tabari / Masha'allah: bound 3,
    triplicity 2) or newer (al-Qabisi / Abu Ma'shar: triplicity 3, bound 2)
    tradition; the Places wheel comes from ibn Ezra's own or Masha'allah's.
    Which pairing to use is not stated in the source, so all four
    combinations are computed, and the two same-tradition pairings are
    marked as presets.

    Dignity claims are read AT EACH POINT'S degree, not at the candidate
    planet's own position; the Places value is keyed the other way, by the
    CANDIDATE's own Whole-Sign house. Masha'allah's wheel gives two
    competing values on four wedges (Masha'allah vs. Dorotheus); the
    Masha'allah value is used, matching the scheme it is paired with.

    Ibn Ezra's victor #2 (1507) is not implemented: it drops the two
    chronocrator rows and adds a "Superiors" row scored only for Saturn,
    Jupiter and Mars (the worksheet blacks out the other four cells), but
    no available course document gives that row's weight, and guessing it
    would make the totals meaningless."""
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    points = {
        'Sun': planetary_data['Sun']['longitude'],
        'Moon': planetary_data['Moon']['longitude'],
        'Ascendant': ascendant_lon,
        'Lot of Fortune': lot_of_fortune,
        'Prenatal Syzygy': syzygy_lon,
    }
    columns = [p for p in WEIGHT_ORDER]           # worksheet column order
    day_lord = chronocrats.get('Day Lord')
    hour_lord = chronocrats.get('Hour Lord')

    # The two axes are genuinely independent, so all four combinations are
    # computed rather than the two diagonal pairings alone. Which wheel
    # goes with which weighting is nowhere stated in the source; pairing
    # each with the wheel of its own named tradition is a reading, and
    # hard-coding it hid the two off-diagonal cases entirely. The diagonal
    # pairings are marked as the interpretive presets they are.
    results = {}
    for (weight_name, weights), (places_name, places_values) in product(
            VICTOR_WEIGHTS.items(), VICTOR_PLACES_VALUES.items()):
        preset = ' (matched preset)' if weight_name == places_name else ''
        scheme_name = (f"{weight_name.split(' (')[0]} weights + "
                       f"{places_name.split(' (')[0]} places{preset}")
        totals = {p: 0 for p in columns}
        grid = []

        for point_name, lon in points.items():
            rulers = get_essential_rulers(lon)
            claims = {p: 0 for p in columns}
            for key, weight_key in (('domicile', 'domicile'), ('exaltation', 'exaltation'),
                                     (triplicity_key, 'triplicity'), ('term', 'term'), ('face', 'face')):
                lord = rulers[key]
                if lord in claims:
                    claims[lord] += weights[weight_key]
            for p in columns:
                totals[p] += claims[p]
            grid.append({'Row': point_name, **{p: str(claims[p]) if claims[p] else '' for p in columns}})

        # The three auxiliary rows appear ONCE on the sheet, not per point.
        for label, lord, pts in (('Lord of the Day (7)', day_lord, 7),
                                  ('Lord of the Hour (6)', hour_lord, 6)):
            row = {p: '' for p in columns}
            if lord in totals:
                totals[lord] += pts
                row[lord] = str(pts)
            grid.append({'Row': label, **row})

        places_row = {}
        for p in columns:
            if p in planetary_data:
                bonus = places_values[get_wsh_house(planetary_data[p]['longitude'], ascendant_lon)]
                totals[p] += bonus
                places_row[p] = str(bonus)
            else:
                places_row[p] = ''
        grid.append({'Row': 'Places', **places_row})
        grid.append({'Row': 'Totals', **{p: str(totals[p]) for p in columns}})

        victor = max(columns, key=lambda p: totals[p])
        tied = [p for p in columns if totals[p] == totals[victor]]
        # The runner-up is the first planet STRICTLY below the top score.
        # sorted()[1] used to hand back a co-winner whenever the top was
        # tied, so a tie read as "Saturn / Jupiter, runner-up Jupiter".
        lower = [p for p in sorted(columns, key=lambda p: -totals[p]) if totals[p] < totals[victor]]
        results[scheme_name] = {
            'grid': grid,
            'victor': ' / '.join(tied) if len(tied) > 1 else victor,
            'total': totals[victor],
            'runner_up': f"{lower[0]} ({totals[lower[0]]})" if lower else '-',
            'tied': len(tied) > 1,
        }
    return results

def evaluate_planets_in_houses(planetary_data, abu_mashar_condition, ascendant_lon):
    """Each planet's Whole Sign house placement and BOTH Rhetorius/PN4
    readings for that pairing, good and bad.

    Both are shown rather than one being chosen for the reader. The only
    thing available to choose with is the Net in the Planetary Condition
    table, and that number is this app's own arithmetic: Abu Ma'shar
    enumerates the VII.6 conditions and nowhere totals them, supplies no
    weighting, and gives no rule for ties. Letting an invented score
    silently pick one of two classical delineations turned a convenience
    into a verdict, and hid the fact that a chart can sit one label away
    from the opposite reading.

    The Net still appears, as a LEAN rather than a selection, and goes
    'Indeterminate' inside a margin of one -- the width of a single
    testimony, so the cases that could flip on one more source paragraph
    say so instead of committing."""
    results = []
    for planet, data in planetary_data.items():
        if planet == 'North Node': continue

        wsh_house = get_wsh_house(data['longitude'], ascendant_lon)
        condition_data = abu_mashar_condition[planet]
        net = condition_data['Net']
        if abs(net) <= 1:
            lean = 'Indeterminate'
        else:
            lean = f"leans {condition_data['Condition']}"

        results.append({
            'Planet': planet,
            'Placed in (WS place)': wsh_house,
            'Net': net,
            'Lean': lean,
            'Standing': 'app arithmetic, not a source verdict',
            'If Well Placed': PLANETS_IN_HOUSES[wsh_house][planet]['Good'],
            'If Badly Placed': PLANETS_IN_HOUSES[wsh_house][planet]['Bad'],
        })
    return results

# --- Chronocrator Matrix (Time Lords): Profections & Distributions -------

# --- The planetary years (Gr. Intr. VII.8, Figure 146) -- DISPLAY ONLY --
# Decision D-3 (2026-09-08): On Times stays under the Revolutions deferral
# for implementation, because every rule it gives is contradicted by
# another passage and PN IV is the only source that could break the ties.
# The one thing admitted now is this table with the two placement rules
# beside it, both labelled, neither applied to anything. Figure 146 was
# rebuilt 2026-09-07 and is doubly verified: every cell matches the prose
# restatement at VII.8, 3-8, and the fardar column sums to the 75 years
# the text itself totals (VII.8, 3). Pinned in tests/test_base_tables.py.
#
# THE MIDDLE COLUMN USES TWO CONSTRUCTIONS, which is why the luminaries look
# anomalous and must not be "corrected" to a single rule. The five planets take
# the ordinary mean of least and great -- Saturn (30+57)/2 = 43.5, Jupiter
# (12+79)/2 = 45.5, Mars (15+66)/2 = 40.5, Venus (8+82)/2 = 45, Mercury
# (20+76)/2 = 48. The two luminaries halve the great year first:
# (least + great/2)/2, giving the Sun (19+60)/2 = 39.5 and the Moon
# (25+54)/2 = 39.5, not the 69.5 and 66.5 an ordinary mean would give. The
# second construction is stated outright at Valens VII.5; established by an
# independent source reconstruction, 2026-09-09, after two earlier passes here
# had assumed one rule for all seven and read the luminaries as an error.
PLANETARY_YEARS = {
    'Saturn':  {'fardar': 11, 'lesser': 30, 'middle': 43.5, 'greater': 57,  'mighty': 265},
    'Jupiter': {'fardar': 12, 'lesser': 12, 'middle': 45.5, 'greater': 79,  'mighty': 427},
    'Mars':    {'fardar': 7,  'lesser': 15, 'middle': 40.5, 'greater': 66,  'mighty': 284},
    'Sun':     {'fardar': 10, 'lesser': 19, 'middle': 39.5, 'greater': 120, 'mighty': 1461},
    'Venus':   {'fardar': 8,  'lesser': 8,  'middle': 45,   'greater': 82,  'mighty': 1151},
    'Mercury': {'fardar': 13, 'lesser': 20, 'middle': 48,   'greater': 76,  'mighty': 480},
    'Moon':    {'fardar': 9,  'lesser': 25, 'middle': 39.5, 'greater': 108, 'mighty': 520},
}
NODE_FARDAR_YEARS = {'Head': 3, 'Tail': 2}

def reference_planetary_years_rows():
    """The planetary years as the course's Handy Tables print them (Lesson
    5: lesser, middle, greater, mighty) with the fardar period (PN IV IV.1,
    2), for the Reference tables page. DISPLAY ONLY, and a table rather
    than a grant: nothing here applies a planet's years to a judgment,
    which is what D-3 forbids -- see D3_GRANT_READERS in the tests."""
    return [{'Planet': p, 'Lesser': y['lesser'], 'Middle': y['middle'], 'Greater': y['greater'],
             'Mighty': y['mighty'], 'Fardar (years)': y['fardar']} for p, y in PLANETARY_YEARS.items()]

def evaluate_planetary_years_display(planetary_data, cusps, ascendant_lon, sect, essential):
    """Figure 146 beside each planet's placement, with what the two
    placement rules in the corpus would grant it -- shown, not applied.

    On Times Ch. 4, 7 (of the ruler of the releaser): "if the ruler was in
    a stake, eastern, it grants its greater years; or if it was in what
    follows the stakes, it grants its middle years; and if it was falling,
    it grants its lesser years." Stake/succedent/falling by the app's
    quadrant place with the five-degree carryover, as elsewhere.

    On Nativities 1.20 (of the house-master): 10 "in the Ascendant or in the
    Midheaven, or in the sign of the west, or the eleventh, enhanced by what
    I explained [7-9: in its own share, eastern, direct, of the sect] ...
    the greater years"; 11 "under the earth, eastern, in one of its shares,
    enhanced ... its greater years"; 16 "in the second or eighth ... its
    middle years"; 17 "in the house of hope or the fifth, and was not in
    something of its shares, and was not eastern ... its middle years".
    Whole signs, as 10 says "sign of the west". Where neither sentence
    reaches a placement the column says so rather than inventing a value.
    The two rules disagree on where the greater years are granted (04 §3
    #2), which is one reason D-3 keeps them on the page and out of the
    engine."""
    rows = []
    sun_lon = planetary_data['Sun']['longitude']
    for planet in ('Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon'):
        lon = planetary_data[planet]['longitude']
        years = PLANETARY_YEARS[planet]
        ws = get_wsh_house(lon, ascendant_lon)
        q = get_effective_house(lon, cusps)
        ess = essential.get(planet, {})
        in_share = any(ess.get(k) for k in ('Domicile', 'Exalt', 'Triplicity', 'Term', 'Face'))
        if planet == 'Sun':
            side = '-'
        else:
            side = solar_phase(planet, lon, sun_lon, planetary_data[planet].get('speed_in_lon'))[1] or '-'
        eastern = side == 'eastern'
        # On Times 4, 7
        if q in ANGLE_HOUSES:
            times = 'greater (in a stake, eastern; 4, 7)' if eastern else 'in a stake but not eastern: 4, 7 gives no value'
        elif q in SUCCEDENT_HOUSES:
            times = 'middle (follows the stakes; 4, 7)'
        else:
            times = 'lesser (falling; 4, 7)'
        # On Nativities 1.20
        under_earth = q in (1, 2, 3, 4, 5, 6)
        if ws in (1, 10, 7, 11):
            nat = 'greater if enhanced (1.20, 10)' + ('' if (in_share and eastern) else ' -- not enhanced here (7-9)')
            if ws == 11 and not in_share and not eastern:
                nat = 'middle (11th, not in a share, not eastern; 1.20, 17)'
        elif under_earth and eastern and in_share:
            nat = 'greater (under the earth, eastern, in a share; 1.20, 11)'
        elif ws in (2, 8):
            nat = 'middle (1.20, 16)'
        elif ws == 5 and not in_share and not eastern:
            nat = 'middle (5th, not in a share, not eastern; 1.20, 17)'
        else:
            nat = 'not stated in 1.20'
        rows.append({
            'Planet': planet, 'Lesser': years['lesser'], 'Middle': years['middle'], 'Greater': years['greater'],
            'Mighty': years['mighty'], 'Fardar': years['fardar'],
            'WS place': ws, 'Quadrant place': q, 'Side of the Sun': side, 'In a share': 'yes' if in_share else 'no',
            'On Times 4, 7 would grant': times, 'On Nativities 1.20 would grant': nat,
        })
    return rows

# =========================================================================
# 3b. PERSIAN NATIVITIES IV -- THE TIMING APPARATUS  (D-3 closed 2026-09-10)
# =========================================================================
#
# Abu Ma'shar, On the Revolutions of the Years of Nativities (Persian
# Nativities IV, tr. Dykes), read 2026-09-10 and answered in
# synthesis/04_timing_answers_2026-09-10.md. Citations are Book.chapter,
# sentence -- "III.1, 13" is Book III, chapter 1, sentence 13 -- and were
# re-checked against the corpus at blob 295eb22 before this code was
# written (see synthesis/15_pn4_implementation_2026-09-10.md).
#
# WHAT IS DELIBERATELY ABSENT, and why.
#
# The releaser/house-master/cutter chain is NOT implemented. PN IV names
# the five releasers -- "the Sun, Moon, Ascendant, Lot of Fortune, or the
# degree of the meeting or degree of the opposition" (III.3, 1) -- and
# gives the frame (the house-master is the distributor of the releaser's
# natal position, Dykes' Figure 50), but it never states how to CHOOSE
# among the five, how many years the house-master grants, or how
# increasers and decreasers are counted. Abu Ma'shar says so himself:
# those "who look into it are wandering around in the dark; but a
# statement of the truth of that ... is found in the book which we worked
# on concerning nativities" (IX.8, 123) -- a book outside this corpus.
#
# Nothing below depends on that choice. The distributions implemented here
# are the one taken FROM THE ASCENDANT, which II.2, 6-7 lists as an
# indicator separate from the one taken from the longevity releaser, and
# which III.1, 14 says the Persians alone called the "jar bakhtar"; and,
# since 2026-09-10, the ones taken FROM THE MERIDIAN -- the degrees of the
# Midheaven and the fourth, "directed by the ascensions of the right
# sphere" (III.1, 12; fn 14: "or rather, the IC itself"). What PN IV does
# NOT say about the meridian distribution, and the page says instead: it
# gives it no topic (the "profession" reading is fn 4, al-Qabisi IV.12,
# an editor's note), it does not list it among the year's indicators
# (II.2), it works no example of it (the III.1, 19-45 example directs the
# Ascendant only), and its partner-at-birth rule (III.1, 23-25) is worded
# for the Ascendant and carried to the meridian by analogy. Planets IN the
# Midheaven, which III.1, 12 also assigns to right ascension, are not
# directed.
#
# The third case of III.1, 12 -- everything that is neither the Ascendant
# nor the meridian, directed "according to what we stated in our book [on
# that topic]" -- is absent. PN IV defers the method to a book it
# does not reproduce; Dykes' fn 16 identifies it as Ptolemy's proportional
# semi-arcs, but that is an editor's note, not Abu Ma'shar's sentence, and
# the reconstructions of it differ. Named and refused rather than guessed.

PN4_SEVEN = ('Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon')

# The order of the spheres, highest first -- "according to the succession
# of their spheres" (IV.1, 3). CHALDEAN_ORDER above is the same cycle
# rotated to start at Mars for the planetary hours; written out again here
# because the fardar and its sub-periods both index into it by position,
# and a rotation whose starting point is incidental to another doctrine is
# not a safe thing to index.
PN4_DESCENDING_SPHERES = ('Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon')

PN4_NODE_ORDER = ('Head', 'Tail')

# Quadruplicity under PN IV's names. "Convertible" is Dykes' rendering of
# the cardinal signs; "having two bodies" of the common ones (IX.1, 26-30).
PN4_QUADRUPLICITY = {
    'Aries': 'convertible', 'Cancer': 'convertible', 'Libra': 'convertible', 'Capricorn': 'convertible',
    'Taurus': 'fixed', 'Leo': 'fixed', 'Scorpio': 'fixed', 'Aquarius': 'fixed',
    'Gemini': 'double-bodied', 'Virgo': 'double-bodied', 'Sagittarius': 'double-bodied', 'Pisces': 'double-bodied',
}

# --- III.1, 13: the rate ladder ------------------------------------------
# 1 deg = 1 year, 5' = 1 month, 1' = 6 days, 10" = 1 day, 25''' = 1 hour,
# on an idealised year of twelve 30-day months (fn 17). Matching Sahl,
# On Nativities 1.18, 21 exactly and extending it by one rung.
#
# The ladder is ONE conversion, not five: a degree is 360 idealised days
# and every rung follows from that. 25''' -- twenty-five THIRDS, a
# sixtieth of a second of arc -- is the rung that closes it, because 10"
# is a day and 10"/24 = 25''' exactly.
#
# The corpus reads `every 25" one hour`, which would make an hour two and
# a half days long. The page prints 25''' (photo-verified, p. 288:
# PN4_READTHROUGH_FINDINGS_2026-09-10.md, D-07). The arithmetic settles it
# without the photograph, and test_pn4_timing.py asserts both halves.
PN4_IDEALISED_DAYS_PER_YEAR = 360.0
PN4_IDEALISED_DAYS_PER_MONTH = 30.0

def pn4_arc_to_time(arc_degrees):
    """III.1, 13. An arc of direction in degrees -> Abu Ma'shar's years,
    months, days and hours on the idealised 360-day year."""
    total = float(arc_degrees) * PN4_IDEALISED_DAYS_PER_YEAR
    years, rem = divmod(total, PN4_IDEALISED_DAYS_PER_YEAR)
    months, rem = divmod(rem, PN4_IDEALISED_DAYS_PER_MONTH)
    days, rem = divmod(rem, 1.0)
    return {'years': int(years), 'months': int(months), 'days': int(days), 'hours': rem * 24.0}

def pn4_format_arc_time(arc_degrees):
    t = pn4_arc_to_time(arc_degrees)
    return f"{t['years']}y {t['months']}m {t['days']}d {t['hours']:.1f}h"

# III.1, 6: the unit of a directed degree is keyed to the LEVEL OF THE
# CHART, not to sign type, planetary strength, quadruplicity or speed.
# This is orthogonal to corpus disagreement #5, which asks a different
# question and stays open; PN IV must not be cited on any side of it.
PN4_DIRECTION_UNITS = {
    'root': 'years',
    'revolution of the year': 'months and days',
    'revolution of the month': 'days and hours',
}

def pn4_direction_unit(chart_level):
    """III.1, 6."""
    return PN4_DIRECTION_UNITS.get(chart_level)

# --- III.1, 12: which ascensions measure which point ----------------------
# III.1, 12, and the STATE of each of its three cases in this engine. The
# table must not flatten them: the first two cases are built, each for the
# DEGREE of its point and not for "the things in it"; the third case's
# method is not in PN IV at all, being deferred to a book he does not
# reproduce, so it is not buildable from this corpus without importing a
# reconstruction. The state strings are asserted verbatim by
# test_pn4_printed_reference_tables_derive_from_the_rules, so directing a
# planet on an angle, or building the third case, means changing them.
PN4_ASCENSION_RULE = {
    'Ascendant': ('oblique ascensions of the birth latitude', 'applied to the degree of the Ascendant'),
    'Midheaven': ('right ascensions', 'applied to the degrees of the Midheaven and the fourth'),
    'Fourth (IC)': ('right ascensions', 'applied to the degrees of the Midheaven and the fourth'),
    'anything else': ('proportional semi-arcs', 'method not stated in PN IV'),
}

def pn4_ascension_measure(point):
    """III.1, 12. Returns (measure, state) -- see PN4_ASCENSION_RULE."""
    return PN4_ASCENSION_RULE.get(point, PN4_ASCENSION_RULE['anything else'])

def _pn4_sentence_case(text):
    """Upper-case the first letter only. str.capitalize() would lower the
    rest and turn "PN IV" into "pn iv"."""
    return text[:1].upper() + text[1:]

# The three reference tables the Timing page prints beside the working
# ones, so a number on the page can be traced to the sentence that fixes
# it without leaving the app. Each is DERIVED from the rule above it
# rather than restating it, so the printed table cannot drift from the
# rule the engine applies.
PN4_LADDER_ROWS = [
    {'Arc': label, 'Is': f"{v} {unit}" if v != 1 else f"1 {unit.rstrip('s')}"}
    for label, arc, unit, v in (
        ('1\u00b0', 1.0, 'years', 1), ("5\u2032", 5 / 60, 'months', 1),
        ("1\u2032", 1 / 60, 'days', 6), ('10\u2033', 10 / 3600, 'days', 1),
        ('25\u2034', 25 / 216000.0, 'hours', 1))
    if pn4_arc_to_time(arc)[unit] == v            # each rung checked as it is printed
]
PN4_UNIT_ROWS = [{'Directed in the': label, 'A degree is': pn4_direction_unit(key)}
                 for key, label in (('root', 'Root of the nativity'),
                                    ('revolution of the year', 'Revolution of the year'),
                                    ('revolution of the month', 'Revolution of the month'))]
PN4_ASCENSION_ROWS = [
    {'Point directed': label, 'Measured in': _pn4_sentence_case(pn4_ascension_measure(point)[0]),
     'In this engine': pn4_ascension_measure(point)[1]}
    for point, label in (('Ascendant', 'Ascendant, and things in it'),
                         ('Midheaven', 'Midheaven, or the fourth'),
                         ('anything else', 'Anything else'))
]

def pn4_bound_lord(lon):
    """III.1, 11: the lord of the bound the directed degree stands in is
    the distributor, 'whether it looked at [the bound] or not'."""
    sign = get_zodiac_sign(lon)
    degree_in_sign = lon % 30.0
    return next((lord for limit, lord in EGYPTIAN_TERMS.get(sign, []) if degree_in_sign < limit), '-')

def pn4_bound_starts():
    """The longitude at which every Egyptian bound begins, once round the
    circle: (longitude, lord, sign). EGYPTIAN_TERMS stores each bound's
    END degree, so a bound starts where the previous one ended."""
    out = []
    for i, sign in enumerate(SIGN_ORDER):
        base, start = i * 30.0, 0.0
        for limit, lord in EGYPTIAN_TERMS[sign]:
            out.append((base + start, lord, sign))
            start = float(limit)
    return out

# I.7, 12 and III.1, 15: "the positions of the planets and their rays."
# The ray is a POINT, not a body with an orb -- the partner holds "until
# it encounters another planet by its body or rays" (III.1, 16), so there
# is always exactly one partner and never a contested overlap. Transit
# orbs (Figure 83, p. 397) belong to a different technique and must not be
# carried in here.
PN4_RAY_OFFSETS = ((60.0, 'sextile'), (90.0, 'square'), (120.0, 'trine'), (180.0, 'opposition'))

def pn4_bodies_and_rays(planetary_data):
    """Every body and ray a directed degree can meet, as
    (longitude, kind, planet, aspect). Both sides of each aspect, "right or
    left"; the opposition is one point, not two."""
    out = []
    for planet in PN4_SEVEN:
        row = planetary_data.get(planet)
        if not row:
            continue
        lon = row['longitude'] % 360.0
        out.append((lon, 'body', planet, 'body'))
        for offset, name in PN4_RAY_OFFSETS:
            out.append(((lon + offset) % 360.0, 'ray', planet, name))
            if offset != 180.0:
                out.append(((lon - offset) % 360.0, 'ray', planet, name))
    return out

# III.2, 103-104: the strength of a partner. Body first, then the rays in
# the order opposition > square > trine > sextile -- HARD ASPECTS ABOVE
# SOFT ONES, which is the reverse of the usual benefic intuition and is
# easy to get backwards.
PN4_PARTNER_RANK = {'body': 0, 'opposition': 1, 'square': 2, 'trine': 3, 'sextile': 4}

def pn4_partner_strength(aspect):
    return PN4_PARTNER_RANK.get(aspect)

PN4_DISTRIBUTION_SPAN_YEARS = 120.0

def _pn4_distribute(planetary_data, start_lon, measure, span_years, point_label,
                    opening_window='sign', epoch='birth'):
    """The bound-by-bound direction of III.1, 7-16, shared by every point
    this engine distributes: `start_lon` directed through the Egyptian
    bounds, naming at every moment a distributor -- the lord of the bound
    reached (III.1, 11) -- and a partner, the most recent body or ray the
    direction has met (III.1, 15-16). `measure` maps an ecliptic degree
    to the ascension the point is directed in (III.1, 12): the oblique
    ascension of the birth latitude for the Ascendant, the right ascension
    for the meridian. Callers choose it and own its domain.

    Returns a list of segments in age order, each
    {from, to, from_lon, distributor, partner, partner_aspect, ...}, where
    `from_lon` is the zodiacal degree the direction stands on as the
    segment opens.

    `span_years` is in units of the measure (degrees of arc); the caller
    converts to time. `opening_window` is where the partner already in
    place is looked for: 'sign' (III.1, 23-25, back to the beginning of the
    sign) or 'bound' (IX.7, 30, "in the bounds of the degree"). `epoch`
    names the moment the direction starts from in the row text.

    Time comes from the arc: one degree of ascension is one year
    (III.1, 13). Order comes from the longitudes: both measures increase
    with the longitude wherever they are defined, so "the next bound round
    the zodiac" and "the next arc of direction" are the same sequence.
    """
    start_lon %= 360.0
    m0 = measure(start_lon)
    meetings = pn4_bodies_and_rays(planetary_data)

    # III.1, 23-25: the partner AT BIRTH. Look back from the directed
    # degree to the beginning of its sign; the nearest body or ray behind
    # it is already the partner. "But since I did not find a planet nor
    # its rays from the beginning of the sign up to the degree of the
    # Ascendant, Venus became the distributor without a planet partnering
    # with her" -- the search does NOT run back past the start of the
    # sign. Worded for the Ascendant; the meridian gets it by analogy, and
    # the page says so.
    #
    # IX.7, 30 (the small days) names a narrower window, "in the bounds of
    # the degree of the Ascendant of the revolution": the same look-back,
    # stopping at the beginning of the BOUND. The sentence does not say
    # whether a body ahead of the degree within its bound manages from the
    # first day or from the day the degree reaches it; this reads it the
    # way III.1, 23-25 is worked, and the page says so.
    if opening_window == 'sign':
        window_start = (start_lon // 30.0) * 30.0
        alone_cite = 'III.1, 25'
    elif opening_window == 'bound':
        window_start = max(lon for lon, _lord, _sign in pn4_bound_starts() if lon <= start_lon)
        alone_cite = 'IX.7, 24 and 30'
    else:
        raise ValueError(f"opening_window must be 'sign' or 'bound', not {opening_window!r}")
    behind = [m for m in meetings if window_start <= m[0] <= start_lon]
    opening = max(behind, key=lambda m: m[0]) if behind else None

    # Everything the direction will meet, by arc from the starting point.
    events = [(lon, 'bound', lord, 'bound') for lon, lord, _sign in pn4_bound_starts()]
    events.extend(meetings)

    dated = []
    for lon, kind, who, aspect in events:
        arc = (measure(lon) - m0) % 360.0
        if 0.0 < arc <= span_years:
            dated.append((arc, lon, kind, who, aspect))
    dated.sort(key=lambda e: e[0])

    distributor = pn4_bound_lord(start_lon)
    partner = opening[2] if opening else None
    partner_aspect = opening[3] if opening else None
    partner_from = (f"{opening[2]} by {opening[3]} at {get_degree_string(opening[0])}, behind the {point_label}"
                    if opening else f'none: the distributor acts alone ({alone_cite})')
    opened_by = (f'at {epoch}: {partner} by {partner_aspect}' if opening
                 else f'at {epoch}: the distributor alone')

    segments, cursor, from_lon = [], 0.0, start_lon
    for arc, lon, kind, who, aspect in dated:
        if arc - cursor > 1e-9:
            segments.append({
                'from': cursor, 'to': arc, 'from_lon': from_lon, 'distributor': distributor,
                'partner': partner, 'partner_aspect': partner_aspect,
                'partner_from': partner_from, 'opened_by': opened_by,
            })
        if kind == 'bound':
            distributor = who
            opened_by = f"bound of {who} at {get_degree_string(lon)}"
        else:
            partner, partner_aspect = who, aspect
            partner_from = (f"{who} by body at {get_degree_string(lon)}" if aspect == 'body'
                            else f"{who} by {aspect} at {get_degree_string(lon)}")
            opened_by = partner_from
        cursor, from_lon = arc, lon
    if cursor < span_years:
        segments.append({
            'from': cursor, 'to': span_years, 'from_lon': from_lon, 'distributor': distributor,
            'partner': partner, 'partner_aspect': partner_aspect,
            'partner_from': partner_from, 'opened_by': opened_by,
        })
    return segments

def pn4_distribution_from_ascendant(planetary_data, ascendant_lon, obliquity, geo_lat,
                                    span_years=PN4_DISTRIBUTION_SPAN_YEARS):
    """The *jar bakhtar* (III.1, 14): the degree of the Ascendant directed
    through the bounds by the oblique ascensions of the birth latitude
    (III.1, 12). Segments as _pn4_distribute returns them, or None where
    the method has no domain.

    ABOVE THE POLAR CIRCLE THIS REFUSES, returning None, on the domain of
    D-23: where |latitude| + obliquity >= 90 some degrees never rise, the
    oblique ascension has no unique inverse, and an arc of direction from
    the Ascendant is not defined. Refusing is the decided behaviour for
    every method in this file that rests on the oblique ascension. The
    meridian distribution below does not rest on it, and does not refuse.
    """
    if not _ascensional_method_applies(obliquity, geo_lat):
        return None
    return _pn4_distribute(planetary_data, ascendant_lon,
                           lambda lon: _oblique_ascension(lon, obliquity, geo_lat),
                           span_years, 'Ascendant')

PN4_MERIDIAN_POINTS = ('Midheaven', 'Fourth (IC)')

def pn4_distribution_from_meridian(planetary_data, mc_lon, obliquity, point='Midheaven',
                                   span_years=PN4_DISTRIBUTION_SPAN_YEARS):
    """III.1, 12: "what is in the Midheaven or the fourth is directed by
    the ascensions of the right sphere" -- the degree of the Midheaven, or
    of the fourth (fn 14: "or rather, the IC itself", the point opposite
    it), directed through the bounds by RIGHT ASCENSION, one degree to a
    year (III.1, 13), with the same distributor and partner as any other
    direction (III.1, 10-11, 15-16). Built 2026-09-10.

    This never refuses. Right ascension has no latitude in it and the
    meridian crosses the ecliptic at every latitude, so the arc is defined
    everywhere; D-23's refusal is about inverting the OBLIQUE ascension,
    which this does not do.

    What the source does not supply, and the page admits: no worked
    example of a meridian direction exists in PN IV (the check is
    arithmetic, plus the editor's four-minutes-a-degree animation of
    Appendix A, p. 673); the partner-at-birth rule is worded for the
    Ascendant; the distribution is given no topic by Abu Ma'shar and is
    not among the year's indicators (II.2); planets IN the Midheaven are
    not directed, only its degree."""
    if point not in PN4_MERIDIAN_POINTS:
        raise ValueError(f"point must be one of {PN4_MERIDIAN_POINTS}, not {point!r}")
    start = mc_lon if point == 'Midheaven' else mc_lon + 180.0
    return _pn4_distribute(planetary_data, start, lambda lon: _ra_decl(lon, obliquity)[0],
                           span_years, point)

# --- IX.7, 29-31: "the small days" ---------------------------------------
# "you look at the degree of the Ascendant of the revolution of the year,
# so that you direct from it (for the knowledge of the conditions of the
# days), a day for every 59' 08", until it returns to the degree of the
# Ascendant at the end of the year" (IX.7, 29). The management is the
# distribution's -- a body or ray already in the bound, else the bound
# lords "in the way we have stated" until a planet or ray is reached
# (IX.7, 30; 24) -- and IX.7, 31 names it the small days.
#
# ZODIACAL, on purpose. The sentence gives a rate in degrees of the
# zodiac and promises a return to the same degree at the year's end, and
# 360 / 59'08" is 365.28 days -- the year to within an hour. Abu Ma'shar
# grades it himself: "there is an approximation in it, but the correct
# [approach] is that this way of directing is like the direction of the
# Sun every day ... between this sense which is by approximation and the
# exact one, the second one is easy, [with] no harm in the work"
# (IX.7, 32). The exact form he names -- the degree advancing by the
# Sun's real motion each day -- is not built; nor is Dykes' fn 178, which
# would have it by ascensions (an editor's view). Decided by the owner
# 2026-09-10 between the three, with the stated rate chosen.
#
# What is read into the sentence and said on the page: the bodies and
# rays are the REVOLUTION'S (the sentence sits inside the revolution);
# the days count from the moment of the revolution (fn 161 says a "day"
# is not defined); only the revolution's Ascendant is directed, though
# IX.7, 31 extends the method to "everything of the planets, Lots, and
# houses". No worked example of it exists in PN IV.
PN4_SMALL_DAYS_RATE = (59.0 * 60.0 + 8.0) / 3600.0      # degrees of the zodiac per day, IX.7, 29

def pn4_small_days_arc_to_days(arc_degrees):
    """IX.7, 29: a day for every 59' 08"."""
    return float(arc_degrees) / PN4_SMALL_DAYS_RATE

def pn4_small_days(sr_planetary_data, sr_ascendant_lon):
    """The revolution's Ascendant distributed round the revolution chart
    for one year (IX.7, 29-31). Segments in DAYS from the revolution, each
    {from, to, from_lon, distributor, partner, partner_aspect, ...}; the
    last ends at the full circuit, 360 / (59' 08"), about 365.28 days.
    Never refuses: the measure is the zodiac itself."""
    segments = _pn4_distribute(sr_planetary_data, sr_ascendant_lon, lambda lon: lon % 360.0,
                               360.0, 'Ascendant of the revolution',
                               opening_window='bound', epoch='the revolution')
    for seg in segments:
        seg['from'] = pn4_small_days_arc_to_days(seg['from'])
        seg['to'] = pn4_small_days_arc_to_days(seg['to'])
    return segments

# --- IX.7, 23-28: "the mighty days" --------------------------------------
# "you look in the revolution of the year at the degree of the sign which
# the year terminated at, from the Ascendant of the root of the nativity"
# (IX.7, 23) -- the terminal point, the natal Ascendant's degree carried
# into the sign of the year -- and direct it: a body or ray already "in
# the bounds of that degree" manages until another meets it, else the
# lord of the bound and the bounds that follow (IX.7, 23-24). The rate
# (IX.7, 25): "multiply by 12 days, <4 hours>, 10 minutes, and 30
# seconds ... from the first day of the revolution", because thirty of
# them "comes to 365 1/4 days, approximately the number of days of the
# year" (IX.7, 28) -- the profected thirty degrees treated as the year.
#
# THE AUTHOR'S OWN FRACTION. IX.7, 25 prints "12 days, <4 hours>, 10
# minutes, and 30 seconds (and that is 1/6 of a day and half a sixth of a
# tenth of a day)". Three figures stand in that sentence: (1) the
# manuscript's 12;10,30 days -- "10 minutes and 30 seconds" as sexagesimal
# fractions OF A DAY, 10/60 + 30/3600 = 0.175 d = 4 h 12 m; (2) the author's
# parenthetical, 1/6 + 1/120 = 0.175 d, the same number stated in words,
# thirty of which are 365 1/4 days EXACTLY (IX.7, 28's "approximately");
# (3) Dykes's hybrid 12 d 4 h 10 m 30 s = 12.17396 d, his pointed-bracket
# "<4 hours>" supplied and the manuscript's minutes and seconds read as
# clock time on top of it, thirty of which are 365 d 5 h 15 m -- fn 177
# then gives 12 d 4 h 12 m for a 365 1/4-day year, which is (1) and (2)
# again. APPLIED: (2), 12 + 1/6 + 1/120 = 12.175 d a degree. The owner's
# decision of 2026-09-11 (decision sheet row 13; order PN4R-4d-1),
# replacing the hybrid applied 2026-09-10 as "the printed rate". The page
# prints all three and says which is applied. Zodiacal by construction --
# there is no ascension anywhere in the sentence; fn 175's report that
# Birchfield would prefer ascensions is an editor's note.
#
# The direction does NOT stop at the end of the sign of the year: it
# starts at the terminal degree and runs thirty degrees, so its last
# part is in the bounds of the NEXT sign, which is what IX.7, 24's "then
# to the lord of the bound which follows it" describes. The same three
# readings as the small days are made and said on the page: the
# revolution's bodies and rays; days from the moment of the revolution;
# the opening partner behind the degree within its bound. IX.7, 27's
# extension to the Lots of the parents and every house and Lot is not
# built. No worked example exists in PN IV.
PN4_MIGHTY_DAYS_PER_DEGREE = 12.0 + 1.0 / 6.0 + 1.0 / 120.0   # IX.7, 25's parenthetical: 12.175 d; thirty = 365.25 d
PN4_MIGHTY_DAYS_SPAN_DEGREES = 30.0                                                # IX.7, 28: thirty degrees, the year

def pn4_mighty_days_arc_to_days(arc_degrees):
    """IX.7, 25's own fraction: 12 + 1/6 + 1/120 days a degree (12.175 d);
    see PN4_MIGHTY_DAYS_PER_DEGREE for the three figures in that sentence."""
    return float(arc_degrees) * PN4_MIGHTY_DAYS_PER_DEGREE

def pn4_mighty_days(sr_planetary_data, terminal_lon):
    """The terminal degree of the year directed through the revolution
    chart for the year (IX.7, 23-28). Segments in DAYS from the
    revolution, each {from, to, from_lon, distributor, partner, ...}; the
    last ends at thirty degrees, 365.22 days at the printed rate. Never
    refuses: the measure is the zodiac itself."""
    segments = _pn4_distribute(sr_planetary_data, terminal_lon, lambda lon: lon % 360.0,
                               PN4_MIGHTY_DAYS_SPAN_DEGREES, 'terminal point of the year',
                               opening_window='bound', epoch='the revolution')
    for seg in segments:
        seg['from'] = pn4_mighty_days_arc_to_days(seg['from'])
        seg['to'] = pn4_mighty_days_arc_to_days(seg['to'])
    return segments

def pn4_distribution_at_age(segments, age_years):
    """The segment covering an age, or None past the end of the span."""
    if not segments:
        return None
    for seg in segments:
        if seg['from'] <= age_years < seg['to']:
            return seg
    return None


# =========================================================================
# The releaser and the house-master, from SAHL (built 2026-09-10)
# =========================================================================
# NOT PN IV. Abu Ma'shar lists the candidates (III.3, 1) and defers the
# choice to "the book on the releaser" (IX.8, 123), which this corpus does
# not hold; the engine refused the step on that ground. The owner decided
# on 2026-09-10, on process/TIMING_SOURCES_REPORT_2026-09-10.md, to build
# it from Sahl instead: the RELEASER per Nawbakht, On Nativities 1.15
# (with 1.16 and the ranking of 1.20, 1-4), and the HOUSE-MASTER DIRECTED
# per Masha'allah, On Nativities 1.23, 2. The years the house-master would
# grant are still granted by nothing: On Times 4, 7 and On Nativities 1.20
# disagree on where the greater years fall (corpus disagreement #2), the
# D-3 control stands, and Masha'allah's direction needs no years.
#
# 1.15, 6-9 (day): "look ... at the Sun and the meeting: because if you
# found the Sun in the Ascendant, the Midheaven, the house of hope, or in
# the stake of the west, or in the eighth, then he will have a releaser
# ... But if you do not find the Sun in any of these places, or he was in
# one of them but the lord of his bound was not looking at him, nor that
# of his house, exaltation, triplicity, or face, then the Sun will not be
# the releaser. And with that you must look at the meeting ... if the
# meeting was in any of these five places, then the meeting is the
# releaser. But if the meeting and the Sun were both falling, then the
# releaser at that time will be the Ascendant." Fn 109: "The inclusion of
# the eighth suggests that these are quadrant divisions, not whole signs."
# 1.15, 10-14 (night): the Moon "in a stake or what follows a stake, with
# the lord of the bound, house, exaltation, triplicity, or image looking
# at her"; else the fullness, same test; else the Lot of Fortune, same
# test. 1.15, 13: "that one -- of any of these indicators -- which is
# looking at the releaser, is the house-master." 1.15, 15-16: else the
# Ascendant, "being looked at by the fortunes, and the lord of the
# Ascendant in its own house or exaltation, or in its own bound,
# triplicity, or image, in good places"; "and if there was nothing of
# what I have mentioned, then know that the native does not have a
# foundation for his lifespan." 1.16, 1-2: the Sun in Aries or Leo, the
# Moon in Taurus or Cancer, "becomes both the releaser and the
# house-master". 1.20, 2-4: bound, then house, exaltation, triplicity,
# image; "the one having two shares is stronger than the lord of only a
# single one"; the bound lord "in the Ascendant with the releaser, it is
# stronger than the others". 1.20, 5: a house-master under the rays "is
# deceptive, subtractive, corrupting" (a flag, not a disqualification).
#
# READINGS MADE HERE, each said on the page: (1) the places are quadrant
# houses with the engine's five-degree carry-over (fn 109; Aphorism 44;
# 1.22, 9), the same reckoning the years display uses; the day list is the
# five places named, the night list every stake and succedent. (2)
# "Looking" is the whole-sign aspect, and a lord in the candidate's own
# sign counts as looking (1.20, 4 treats the bound lord in the Ascendant
# with the releaser as the strongest of those looking). (3) A candidate is
# not its own house-master except in 1.16's four signs; a luminary that is
# its own bound, triplicity or face lord elsewhere is not counted as
# "looking at" itself. (4) The triplicity lord is the lord of the sect
# (day lord by day, night lord by night), as the engine reads it
# everywhere. (5) The meeting is the last New Moon before birth and the
# fullness the last Full Moon; the fullness's degree is the luminary above
# the horizon at that moment, the engine's standing convention for a
# preventional syzygy, since 1.15 does not say which. (6) "In good places"
# for the Ascendant's lord (1.15, 16) is a stake or succedent, the class
# every other candidate needs. (7) The day chart consults the Sun, the
# meeting and the Ascendant only, and the night chart the Moon, the
# fullness, the Lot and the Ascendant, as 6-14 order them; 1.15, 15's
# summary names all five before the Ascendant and is quoted, not applied.
# NOT APPLIED: 1.19, 6 (the Moon within 15 degrees of the Sun "will not
# be fit"), 1.20, 6 (an eastern lord with a share in the Ascendant may
# assume the house-mastership without looking), 1.18, 8-10 (the short-life
# testimonies weaken or void the releaser), and Dorotheus's feminized
# seventh (1.15, 5, which Nawbakht rejects) -- each is named on the page
# where it would bite. APPLIED since 2026-09-11 (FINAL-A7): 1.32, 11-13's
# stand-in in the empty case -- al-Andarzaghar's chapter "On the matter of
# survival for one who does not live" answers the question Nawbakht's "no
# foundation" leaves, a complement not a contradiction; "the first of them
# is the Ascendant, then the Moon" is 1.32, 13 as printed across the p.
# 346/347 break, so the Ascendant's distribution is labelled the stand-in
# and the Moon is directed after it (1.32, 12: whichever first connects
# with an infortune kills; 14: if no fortune looks).

SAHL_RELEASER_DAY_PLACES = (1, 10, 11, 7, 8)          # 1.15, 6 and 8, "these five places"
SAHL_RELEASER_NIGHT_PLACES = (1, 4, 7, 10, 2, 5, 8, 11)  # 1.15, 11-14, "a stake or what follows a stake"
SAHL_DIGNITY_RANK = ('bound', 'house', 'exaltation', 'triplicity', 'face')   # 1.20, 2
# 1.15, 16's "in good places" for the Ascendant's lord: Sahl's SEVEN praised
# places -- Introduction 2, 37-44 ranks the Ascendant, tenth, seventh,
# fourth, eleventh, ninth and fifth and closes "these seven places are
# praised, powerful"; 1.30, 71 names "the seven places (which are the stakes
# and the trines of the Ascendant, and the eleventh)"; fn 372 calls them
# "good or advantageous". No sentence defines 16's phrase, so the
# identification is an interpretation (the engine had used the eight-place
# stake-or-succedent class of 1.15, 11 as reading 6). Counted by WHOLE-SIGN
# PLACE: topic language, the canon of 2026-09-11. Owner, decision sheet row
# 12 (REL-2-6), corroborated blind (astra_2026-09-11/1.15_readings_ruling Q2).
SAHL_GOOD_PLACES = (1, 10, 7, 4, 11, 9, 5)
SAHL_BOTH_AT_ONCE = {'Sun': ('Aries', 'Leo'), 'Moon': ('Taurus', 'Cancer')}  # 1.16, 1-2
SAHL_RELEASER_NOT_APPLIED = (
    ('1.16, 4', 'al-Andarzaghar keeps a luminary "powerful in the places of the releaser" as releaser "even if a house-master '
                'is not looking"; Nawbakht\'s 1.15, 7 gate (no lord looking, not the releaser) is applied instead -- two '
                'chapters of one book, opposite rules'),
    ('1.19, 6', 'the Moon within 15 degrees of the Sun "will not be fit to take up the role of the manager"'),
    ('1.20, 6', 'an eastern lord with a share in the Ascendant may be house-master without looking at the releaser'),
    ('1.18, 8-10', 'one short-life testimony makes the releaser "weak and not fit, except through reception"; two, with no releaser, "one will not know his lifespan except by revolving his years"'),
    ('1.15, 5', "Dorotheus's releaser in the seventh in a feminine sign, which Nawbakht tested and rejected"),
)

def sahl_prenatal_meeting_and_fullness(jd_natal, lat, lon):
    """The last New Moon ("the meeting") and the last Full Moon ("the
    fullness") before birth, each found by the same Newton search as
    calculate_prenatal_syzygy, both always -- 1.15 consults the meeting by
    day and the fullness by night, whichever was nearer. The meeting's
    degree is the luminaries' common longitude; the fullness's is the
    luminary above the horizon at that moment -- On Nativities 1.7, 2,
    "take the portion of whichever of the two luminaries was above the
    earth", stated for the Ascendant's degree and applied to 1.15, 12 by
    the shared word "portion" (FINAL-A6) -- else the Moon's, the engine's
    choice where both or neither is up. Returns {'meeting': {...},
    'fullness': {...}} with 'longitude', 'jd' and 'degree_of'."""
    AVG_REL_SPEED = 12.19075
    sun0 = swe.calc_ut(jd_natal, swe.SUN)[0][0]
    moon0 = swe.calc_ut(jd_natal, swe.MOON)[0][0]
    diff0 = (moon0 - sun0) % 360.0
    out = {}
    for name, target in (('meeting', 0.0), ('fullness', 180.0)):
        jd_guess = jd_natal - ((diff0 - target) % 360.0) / AVG_REL_SPEED
        sun_lon, moon_lon = sun0, moon0
        for _ in range(15):
            sun_lon, moon_lon, offset, rel_speed = _sun_moon_signed_offset(jd_guess, target)
            if abs(offset) < 1e-6:
                break
            if abs(rel_speed) < 1e-6:
                rel_speed = AVG_REL_SPEED
            jd_guess -= offset / rel_speed
        if name == 'meeting':
            out[name] = {'longitude': sun_lon % 360.0, 'jd': jd_guess, 'degree_of': 'the luminaries together'}
        else:
            _, ascmc = swe.houses(jd_guess, lat, lon, b'B')
            obl = swe.calc_ut(jd_guess, swe.ECL_NUT)[0][0]
            s, m = swe.calc_ut(jd_guess, swe.SUN)[0], swe.calc_ut(jd_guess, swe.MOON)[0]
            sun_up = _sin_altitude(s[0], s[1], s[2], obl, ascmc[2], lat) > 0.0
            moon_up = _sin_altitude(m[0], m[1], m[2], obl, ascmc[2], lat) > 0.0
            if sun_up and not moon_up:
                out[name] = {'longitude': sun_lon % 360.0, 'jd': jd_guess, 'degree_of': 'the Sun, above the horizon'}
            else:
                out[name] = {'longitude': moon_lon % 360.0, 'jd': jd_guess,
                             'degree_of': 'the Moon, above the horizon' if moon_up else 'the Moon (neither above, the default)'}
    return out

def _sahl_dignity_lords(lon, sect):
    """The five lords of a degree in 1.20, 2's order, as (rank, planet);
    a rank with no lord (exaltation in a sign that has none) is left
    out. Triplicity by the sect (reading 4)."""
    r = get_essential_rulers(lon)
    pairs = (('bound', r['term']), ('house', r['domicile']), ('exaltation', r['exaltation']),
             ('triplicity', r['triplicity_day'] if sect == 'Diurnal' else r['triplicity_night']),
             ('face', r['face']))
    return [(rank, planet) for rank, planet in pairs if planet in PN4_SEVEN]

def _sahl_looks(from_lon, to_lon):
    """Whole-sign aspect from a planet's sign to a degree's sign: the
    aspect's name, 'in it' for the same sign, or None in aversion."""
    apart = (int(to_lon % 360.0 // 30) - int(from_lon % 360.0 // 30)) % 12
    apart = min(apart, 12 - apart)
    entry = ASPECT_BY_SIGN_COUNT.get(apart)
    if entry is None:
        return None
    return 'in it' if apart == 0 else entry[0].lower()

def _sahl_examine_candidate(label, lon, planetary_data, cusps, sect, places, self_planet=None):
    """One candidate of 1.15 against its two tests: the place, and a
    dignity lord looking. Returns the facts and the verdict."""
    place = get_effective_house(lon, cusps)
    in_places = place in places
    sign = get_zodiac_sign(lon)
    both = bool(self_planet and sign in SAHL_BOTH_AT_ONCE.get(self_planet, ()))
    lords, looking = [], []
    for rank, planet in _sahl_dignity_lords(lon, sect):
        if planet == self_planet:
            lords.append((rank, planet, 'itself' if both else 'itself -- not counted (reading 3)'))
            continue
        row = planetary_data.get(planet)
        aspect = _sahl_looks(row['longitude'], lon) if row else None
        lords.append((rank, planet, aspect or 'in aversion'))
        if aspect:
            looking.append((rank, planet, aspect))
    fit = in_places and (bool(looking) or both)
    if not in_places:
        why = f"falling: house {place} is not among the places (1.15, {'6' if places is SAHL_RELEASER_DAY_PLACES else '11-14'})"
    elif both:
        why = f"{self_planet} in {sign}: both releaser and house-master (1.16, 1-2)"
    elif looking:
        why = f"house {place}; looked at by " + ', '.join(f"{p} ({r}, {a})" for r, p, a in looking)
    else:
        why = f"house {place}, but no lord of its bound, house, exaltation, triplicity or face looks at it (1.15, 7, Nawbakht)"
        if self_planet in ('Sun', 'Moon'):
            # 1.16, 4 (al-Andarzaghar): a luminary "powerful in the places of
            # the releaser ... (even if a house-master is not looking, and it
            # [itself] is not the house-master)" is still directed as the
            # releaser. Two chapters of one book state opposite gates for this
            # case; Nawbakht's is applied, the other named (order REL-2-3).
            why += ("; al-Andarzaghar's 1.16, 4 would keep it as releaser \"even if a house-master is not "
                    "looking\" -- not applied")
    return {'candidate': label, 'longitude': lon % 360.0, 'place': place, 'in_places': in_places,
            'lords': lords, 'looking': looking, 'both_at_once': both, 'self_planet': self_planet,
            'fit': fit, 'why': why}

def _sahl_ascendant_candidate(planetary_data, ascendant_lon, cusps, sect):
    """1.15, 15-16: the Ascendant "being looked at by the fortunes, and
    the lord of the Ascendant in its own house or exaltation, or in its
    own bound, triplicity, or image, in good places"."""
    cand = _sahl_examine_candidate('the Ascendant', ascendant_lon, planetary_data, cusps, sect,
                                   SAHL_RELEASER_DAY_PLACES if sect == 'Diurnal' else SAHL_RELEASER_NIGHT_PLACES)
    fortunes = [(p, _sahl_looks(planetary_data[p]['longitude'], ascendant_lon))
                for p in ('Jupiter', 'Venus') if p in planetary_data]
    fortunes_looking = [(p, a) for p, a in fortunes if a]
    lord = SIGN_TO_DOMICILE.get(get_zodiac_sign(ascendant_lon))
    lord_row = planetary_data.get(lord)
    own = []
    lord_place = None
    if lord_row:
        own = [rank for rank, planet in _sahl_dignity_lords(lord_row['longitude'], sect) if planet == lord]
        lord_place = get_wsh_house(lord_row['longitude'], ascendant_lon)      # a PLACE, whole sign (see SAHL_GOOD_PLACES)
    good_place = lord_place in SAHL_GOOD_PLACES
    fit = bool(fortunes_looking) and bool(own) and good_place
    cand.update({
        'in_places': True, 'fit': fit,
        'why': (f"looked at by {', '.join(f'{p} ({a})' for p, a in fortunes_looking) or 'no fortune'}; its lord {lord} "
                f"{'in its own ' + ' and '.join(own) if own else 'in none of its own shares'}, whole-sign place {lord_place} "
                f"({'one of' if good_place else 'not one of'} Sahl's seven praised places, Introduction 2, 37-44; 1.30, 71 -- "
                f"an interpretation of 16's 'good places') (1.15, 16)"),
    })
    return cand

def _sahl_rank_house_master(cand, planetary_data, cusps):
    """1.15, 13 and 1.20, 2-5 over the lords looking at the chosen
    releaser: grouped by planet, ordered by shares then by the best rank,
    the bound lord in the Ascendant with the releaser first of all.
    Returns rows in order; the first is the house-master."""
    if cand['both_at_once']:
        return [{'Planet': cand['self_planet'], 'Shares': 'its own house or exaltation, and triplicity',
                 'Looks by': 'is the releaser', 'Rank': 'both releaser and house-master (1.16, 1-2)', 'Under the rays': '-'}]
    by_planet = {}
    for rank, planet, aspect in cand['looking']:
        d = by_planet.setdefault(planet, {'ranks': [], 'aspect': aspect})
        d['ranks'].append(rank)
    rows = []
    for planet, d in by_planet.items():
        best = min(SAHL_DIGNITY_RANK.index(r) for r in d['ranks'])
        in_asc_with = (cand['place'] == 1 and 'bound' in d['ranks']
                       and get_effective_house(planetary_data[planet]['longitude'], cusps) == 1)
        phase = solar_phase(planet, planetary_data[planet]['longitude'], planetary_data['Sun']['longitude'],
                            planetary_data[planet].get('speed_in_lon'))[0]
        rows.append({'Planet': planet, 'Shares': ', '.join(d['ranks']), 'Looks by': d['aspect'],
                     '_key': (0 if in_asc_with else 1, -len(d['ranks']), best),
                     'Rank': ('the bound lord in the Ascendant with the releaser: "stronger than the others" (1.20, 4)'
                              if in_asc_with else
                              f"{len(d['ranks'])} share{'s' if len(d['ranks']) != 1 else ''}; best {SAHL_DIGNITY_RANK[best]} (1.20, 2-3)"),
                     'Under the rays': (f"{phase}: \"deceptive, subtractive, corrupting\" (1.20, 5)"
                                        if phase in ('Burned', 'Under the rays') else 'no' if phase != 'Cazimi' else 'Cazimi')})
    rows.sort(key=lambda r: r['_key'])
    for r in rows:
        r.pop('_key')
    return rows

def sahl_releaser(planetary_data, ascendant_lon, cusps, sect, lot_of_fortune, meeting_lon, fullness_lon):
    """Nawbakht's selection (On Nativities 1.15, 6-16) with 1.16's
    exception and 1.20, 2-5's ranking of the house-master. Returns
    {'releaser', 'longitude', 'house_master', 'ranking', 'candidates',
    'verdict', 'sect'}; 'releaser' and 'house_master' are None when
    nothing qualifies ("the native does not have a foundation for his
    lifespan", 1.15, 16)."""
    day = sect == 'Diurnal'
    if day:
        order = [('the Sun', planetary_data['Sun']['longitude'], 'Sun'),
                 ('the meeting (the last New Moon)', meeting_lon, None)]
        places = SAHL_RELEASER_DAY_PLACES
    else:
        order = [('the Moon', planetary_data['Moon']['longitude'], 'Moon'),
                 ('the fullness (the last Full Moon)', fullness_lon, None),
                 ('the Lot of Fortune', lot_of_fortune, None)]
        places = SAHL_RELEASER_NIGHT_PLACES
    cands = [_sahl_examine_candidate(label, lon, planetary_data, cusps, sect, places, self_planet)
             for label, lon, self_planet in order]
    cands.append(_sahl_ascendant_candidate(planetary_data, ascendant_lon, cusps, sect))
    chosen = next((c for c in cands if c['fit']), None)
    ranking = _sahl_rank_house_master(chosen, planetary_data, cusps) if chosen else []
    house_master = ranking[0]['Planet'] if ranking else None
    rows = []
    for i, c in enumerate(cands):
        consulted = chosen is None or i <= cands.index(chosen)
        rows.append({'Candidate': c['candidate'], 'Degree': get_degree_string(c['longitude']),
                     'House (quadrant, carry-over)': c['place'],
                     'Lords of its degree': '; '.join(f"{r} {p}: {a}" for r, p, a in c['lords']),
                     'Verdict': ('THE RELEASER -- ' if c is chosen else '' if consulted else 'not consulted, an earlier candidate qualified -- ')
                                + c['why'],
                     'Source': ('1.15, 6-9' if day else '1.15, 10-14') if c['candidate'] != 'the Ascendant' else '1.15, 15-16'})
    if chosen is None:
        verdict = ('No releaser by Nawbakht\'s rule (1.15, 16: "the native does not have a foundation for his '
                   'lifespan"). For one who does not live, al-Andarzaghar directs the strongest of the four anyway '
                   '(1.32, 11), "the first of them is the Ascendant, then the Moon" (13): the Ascendant\'s distribution '
                   '(the tab "from the Ascendant") is that stand-in, and the Moon is directed after it, below; '
                   'whichever first connects with an infortune kills (12), if no fortune looks (14).')
    elif house_master is None:
        verdict = f"The releaser is {chosen['candidate']}; no house-master, nothing looks at it."
    else:
        verdict = (f"The releaser is {chosen['candidate']} at {get_degree_string(chosen['longitude'])}; the house-master is "
                   f"{house_master}" + (' (1.16: the luminary is both)' if chosen['both_at_once'] else
                                        f", {ranking[0]['Rank']}") + '.')
    return {'releaser': chosen['candidate'] if chosen else None,
            'longitude': chosen['longitude'] if chosen else None,
            'house_master': house_master, 'ranking': ranking, 'candidates': rows,
            'chosen': chosen, 'verdict': verdict, 'sect': sect}

def sahl_releaser_distribution(planetary_data, releaser_lon, obliquity, geo_lat,
                               span_years=PN4_DISTRIBUTION_SPAN_YEARS):
    """1.15, 22: "if you did find a releaser, then direct from it and from
    the degree in which it was"; 1.18, 20-21: "the lord of the bound of
    that releaser is the distributor of time ... direct the degrees from
    the degree in which the releaser is, by degrees of the ascensions of
    the signs in that city, for each degree ... a year". The same
    bound-by-bound direction as the Ascendant's, by the oblique ascension
    of the birth latitude; refuses at the poles as that does (D-23)."""
    if releaser_lon is None or not _ascensional_method_applies(obliquity, geo_lat):
        return None
    return _pn4_distribute(planetary_data, releaser_lon,
                           lambda lon: _oblique_ascension(lon, obliquity, geo_lat), span_years, 'releaser')

SAHL_INFORTUNES = ('Saturn', 'Mars')

def sahl_house_master_direction(planetary_data, house_master, obliquity, geo_lat,
                                span_years=PN4_DISTRIBUTION_SPAN_YEARS, origin_jd=None):
    """Masha'allah, On Nativities 1.23, 2: "look at the position of the
    governor [fn 181: the house-master] ... then direct it to the
    conjunction of the infortunes and the degree of burning, and its
    opposition and its square, a year for every degree of ascensions."
    The house-master's natal degree is directed forward by the oblique
    ascension of the birth latitude -- "the ascensions of that city",
    1.15, 17; 1.16, 4; 1.18, 21 -- to the bodies, squares and oppositions
    of Saturn and Mars and to the Sun's degree, read as "the degree of
    burning". One row per target within the span, in age order. Refuses
    at the poles (D-23). 1.23, 3-11's check of that year's revolution is
    sahl_house_master_in_revolution; 4.12, 6's converse direction of a
    retrograde planet is not applied."""
    if house_master not in planetary_data or not _ascensional_method_applies(obliquity, geo_lat):
        return None
    start = planetary_data[house_master]['longitude'] % 360.0
    oa0 = _oblique_ascension(start, obliquity, geo_lat)
    targets = []
    for p in SAHL_INFORTUNES:
        if p not in planetary_data:
            continue
        lon = planetary_data[p]['longitude'] % 360.0
        targets.append((f"{p}'s body", lon, '1.23, 2 "the conjunction of the infortunes"'))
        targets.append((f"{p}'s opposition", (lon + 180.0) % 360.0, '1.23, 2 "its opposition"'))
        targets.append((f"{p}'s square (right)", (lon - 90.0) % 360.0, '1.23, 2 "its square"'))
        targets.append((f"{p}'s square (left)", (lon + 90.0) % 360.0, '1.23, 2 "its square"'))
    if 'Sun' in planetary_data:
        targets.append(("the Sun's degree (burning)", planetary_data['Sun']['longitude'] % 360.0,
                        '1.23, 2 "the degree of burning" (reading: the Sun\'s natal degree)'))
    rows = []
    for label, lon, cite in targets:
        arc = (_oblique_ascension(lon, obliquity, geo_lat) - oa0) % 360.0
        if arc <= 1e-9 or arc > span_years:
            continue
        row = {'Target': label, 'Degree': get_degree_string(lon), 'Arc (years)': f"{arc:.2f}",
               'In the year of age': int(arc), 'Source': cite, '_arc': arc}
        if origin_jd is not None:
            row['Date'] = f"{pn4_datetime_from_jd(origin_jd + arc * PN4_DIRECTION_YEAR_DAYS):%Y-%m-%d}"
        rows.append(row)
    rows.sort(key=lambda r: r['_arc'])
    for r in rows:
        r.pop('_arc')
    return rows

def sahl_house_master_in_revolution(house_master, chart_data, sr):
    """1.23, 3-4: "calculate for the revolution of that year ... for if
    your calculation of this [by direction] and the revolution both
    indicate burning, and then the governor is burned at the revolution,
    the native will be destroyed; and if it is not burned at the
    revolution but it is burned in one of the stakes of the Ascendant of
    the year, it indicates that [as well]; and it is worse for that in the
    Ascendant [itself]." The facts for the house-master in the revolution:
    where it stands, its solar phase, its house from the revolution's
    Ascendant, and which infortune shares its sign. Judgment is not
    built; 1.23, 5-11's further witnesses are the II.3 examination."""
    rev = sr['planetary_data']
    if house_master not in rev:
        return []
    lon = rev[house_master]['longitude']
    phase, side, elong = solar_phase(house_master, lon, rev['Sun']['longitude'], rev[house_master].get('speed_in_lon'))
    house = get_wsh_house(lon, sr['ascendant'])
    with_infortune = [p for p in SAHL_INFORTUNES if p != house_master and p in rev
                      and get_zodiac_sign(rev[p]['longitude']) == get_zodiac_sign(lon)]
    natal_lon = chart_data['planetary_data'][house_master]['longitude']
    return [
        {'Fact': f"{house_master} in the revolution", 'Reads': f"{get_degree_string(lon)} (natal {get_degree_string(natal_lon)})", 'Source': '1.23, 3'},
        {'Fact': 'Burned at the revolution', 'Reads': (f"{phase}, {side}, {elong:.1f} from the Sun" if phase else f"no: {elong:.1f} from the Sun, {side}"), 'Source': '1.23, 4'},
        {'Fact': "In a stake of the Ascendant of the year", 'Reads': f"house {house} from the revolution's Ascendant" + (' -- a stake' if house in (1, 4, 7, 10) else '') + (' -- the Ascendant itself, "worse"' if house == 1 else ''), 'Source': '1.23, 4'},
        {'Fact': 'With an infortune in its sign', 'Reads': ', '.join(with_infortune) or 'none', 'Source': '1.23, 2-4'},
    ]

def sahl_house_master_turning(house_master, planetary_data, span_years=PN4_DISTRIBUTION_SPAN_YEARS):
    """PN IV IX.8, 30: "if the turning of the years from any of the five
    releasers (or from the indicator of the lifespan) reached their bodies,
    oppositions, or squares, then they also kill" -- the indicator of the
    lifespan (Sahl's house-master, 1.30, 35) TURNED a year a sign from its
    natal sign, which IX.8, 32 says is the only operation for it ("the
    indicator of the lifespan alone is turned in the signs, sign-by-sign,
    and is not directed degree-by-degree"). One row per year of age in
    which the turned sign holds a cutter's body or is its opposition or
    square sign; "their" is the cutters' -- Saturn and Mars, the infortunes
    the direction table already targets (IX.8, 6-19 name the cutters more
    widely; the two bodies and their rays are the ones both authors share).
    Whole-sign turning, as VI.2, 1's. PN IV's own rule, shown beside
    Sahl's direction (FINAL-A2, decision sheet row 2, 2026-09-11)."""
    if house_master not in planetary_data:
        return []
    start_idx = int(planetary_data[house_master]['longitude'] % 360.0 // 30)
    cutters = []
    for p in SAHL_INFORTUNES:
        if p in planetary_data and p != house_master:
            idx = int(planetary_data[p]['longitude'] % 360.0 // 30)
            cutters += [(idx, f"{p}'s body"), ((idx + 6) % 12, f"{p}'s opposition"),
                        ((idx + 3) % 12, f"{p}'s square (left)"), ((idx - 3) % 12, f"{p}'s square (right)")]
    rows = []
    for year in range(int(span_years)):
        sign_idx = (start_idx + year) % 12
        hits = [label for idx, label in cutters if idx == sign_idx]
        if hits:
            rows.append({'Year of age': year, 'Turned sign': SIGN_ORDER[sign_idx],
                         'Reaches': ', '.join(hits), 'Source': 'PN IV IX.8, 30'})
    return rows

def sahl_house_master_flags(house_master, planetary_data, cusps):
    """1.23, 12: "perhaps one will not be able to be guided by the
    governor ... if the governor is one of the infortunes, or it is the
    lord of the eighth"; 1.23, 53: "one should fear for the governor if it
    was retrograde or in its fall". Flags, shown; nothing redirected."""
    if not house_master or house_master not in planetary_data:
        return []
    flags = []
    eighth_sign = SIGN_ORDER[(SIGN_ORDER.index(get_zodiac_sign(cusps[0])) + 7) % 12]
    if house_master in SAHL_INFORTUNES:
        flags.append(f"{house_master} is an infortune: \"perhaps one will not be able to be guided by\" it (1.23, 12; fn 190)")
    if SIGN_TO_DOMICILE.get(eighth_sign) == house_master:
        flags.append(f"{house_master} is the lord of the eighth ({eighth_sign}) (1.23, 12)")
    row = planetary_data[house_master]
    if row.get('speed_in_lon', 1.0) < 0:
        flags.append(f"{house_master} is retrograde: \"one should fear for the governor\" (1.23, 53)")
    if get_zodiac_sign(row['longitude']) in FALLS.get(house_master, ()):
        flags.append(f"{house_master} is in its fall: \"one should fear for the governor\" (1.23, 53)")
    return flags


# --- III.7, 32-42: when a natal indication comes out ----------------------
# A planet may distribute or manage more than once in a lifetime (III.7,
# 32), and this chapter asks how often what it promised in the root
# actually manifests, and at what ages.
#
# HOW OFTEN, by the quadruplicity of the sign it holds in the ROOT:
#   fixed        -- "in [only] a single time" (III.7, 35)
#   convertible  -- "in [only] one of the times" (III.7, 39)
#   double-bodied-- "on an occasional basis" (III.7, 38)
# III.7, 36 raises this to "whenever it distributes" when the planet looks
# at the position of the distribution AND "is strong in [its] indication
# for that thing". The looking is computable; the strength is not defined
# anywhere in the chapter, so the engine reports the quadruplicity rule
# and does not silently promote a row. III.7, 37 exempts the MANAGER (the
# partner): not being an indicator in its own right, it "will produce its
# indication" whenever it manages.
#
# AT WHAT AGE -- III.7, 34 and 42 name two measures and gesture at a third:
#   (a) "the number of ascensions of the sign in which it was in the root"
#   (b) "the amount of one of its own years" (fn 190: "For example, its
#       lesser years"; III.7, 35 says "its greater, middle, or lesser")
#   (c) "the rest of the times which one employs as models" -- unquantified;
#       fn 191 guesses the fardars. Not invented here.
#
# WHAT ABU MA'SHAR ADDS, and the only part that is his: the effect is
# "strong, evident, notable" when such an age falls in a period where that
# same planet is the distributor or the manager (III.7, 42). That is what
# the "Confirmed by" column computes, against the jar bakhtar above.
#
# NOT IMPLEMENTED, deliberately, both from Dykes' fn 191:
#   * The SUM of (a) and (b), and 1/3, 1/2 and 2/3 of that sum, are
#     introduced with "IF WE FOLLOW VALENS". They are not Abu Ma'shar's
#     and no sentence of III.7 contains them. Corpus disagreement #4 over
#     Valens's year-tables is untouched and stays open.
#   * fn 191's worked figure for Taurus at 45N, 20.17 ascensional times,
#     is not reproduced: the exact computation gives 20.09, and Dykes'
#     own thirds are internally inconsistent with his 20.17 anyway
#     (he prints 2/3 = 26.75 where 20.17 gives 26.78). The engine computes
#     ascensions directly, as it does everywhere else.
#
# WHICH of the greater, middle and lesser years applies is chosen "in
# accordance with what its position in the rotation of the circle
# indicated in the root" (III.7, 35) -- a placement rule PN IV
# presupposes and never states. That is corpus disagreement #2, which
# PN IV does not adjudicate (IX.8, 123), so ALL THREE are shown and none
# is chosen, exactly as the planetary-years table does.

PN4_MANIFESTATION_BY_QUADRUPLICITY = {
    'fixed': ('once in the lifespan', 'III.7, 35'),
    'convertible': ('in one of the times', 'III.7, 39'),
    'double-bodied': ('on an occasional basis', 'III.7, 38'),
}

def pn4_sign_ascensions(sign, obliquity, geo_lat):
    """The ascensional times of a whole sign at the birth latitude: the
    arc of the equator that rises with it (III.7, 34, "the ascensions of
    its sign"). Returns None above the polar circle, where a sign may not
    rise at all -- the domain of D-23."""
    if not _ascensional_method_applies(obliquity, geo_lat):
        return None
    start = SIGN_ORDER.index(sign) * 30.0
    return (_oblique_ascension(start + 30.0, obliquity, geo_lat)
            - _oblique_ascension(start, obliquity, geo_lat)) % 360.0

def pn4_activation_ages(planetary_data, obliquity, geo_lat, segments=None,
                        max_age=PN4_DISTRIBUTION_SPAN_YEARS):
    """III.7, 32-42, one row per planet.

    `segments` is the output of pn4_distribution_from_ascendant; when it is
    given, each candidate age is checked against it for Abu Ma'shar's
    confirmation (III.7, 42) -- is this planet the distributor or the
    manager at that age?"""
    rows = []
    for planet in PN4_SEVEN:
        row = planetary_data.get(planet)
        if not row:
            continue
        sign = get_zodiac_sign(row['longitude'])
        kind = PN4_QUADRUPLICITY[sign]
        manifests, cite = PN4_MANIFESTATION_BY_QUADRUPLICITY[kind]
        ascensions = pn4_sign_ascensions(sign, obliquity, geo_lat)
        years = PLANETARY_YEARS[planet]

        candidates = {'ascensions of the sign': ascensions}
        for grade in ('lesser', 'middle', 'greater'):
            candidates[f'{grade} years'] = float(years[grade])

        confirmed = []
        for label, age in candidates.items():
            if age is None or not (0.0 < age <= max_age):
                continue
            seg = pn4_distribution_at_age(segments, age) if segments else None
            if seg and planet in (seg['distributor'], seg['partner']):
                role = 'distributor' if seg['distributor'] == planet else 'manager'
                confirmed.append(f"{label} ({age:.2f}, as {role})")

        rows.append({
            'Planet': planet, 'Natal sign': sign, 'Quadruplicity': kind,
            'Manifests': f"{manifests} ({cite})",
            'Ascensions of the sign': '-' if ascensions is None else f"{ascensions:.2f}",
            'Lesser': f"{years['lesser']:g}", 'Middle': f"{years['middle']:g}",
            'Greater': f"{years['greater']:g}",
            'Confirmed by the distribution': '; '.join(confirmed) if confirmed else 'none',
        })
    return rows

# --- IV.1 and IV.7: the fardar -------------------------------------------

def pn4_fardar_sequence(sect):
    """IV.1, 2-4 with IV.7, 24. The order is the descending order of the
    spheres, begun from the light of the sect and wrapped: by day from the
    Sun, by night from the Moon. The Head (3 years) and the Tail (2) come
    LAST IN BOTH SECTS -- "whether the native was diurnal or nocturnal"
    (IV.7, 24) -- which is the point the later tradition got wrong.

    Seven planets sum to 70 and the Nodes carry it to 75 (IV.1, 2, 8)."""
    light = 'Sun' if sect == 'Diurnal' else 'Moon'
    i = PN4_DESCENDING_SPHERES.index(light)
    order = [PN4_DESCENDING_SPHERES[(i + k) % 7] for k in range(7)]
    seq = [(p, float(PLANETARY_YEARS[p]['fardar'])) for p in order]
    seq += [(n, float(NODE_FARDAR_YEARS[n])) for n in PN4_NODE_ORDER]
    return seq

PN4_FARDAR_CYCLE_YEARS = 75.0

def pn4_fardar_subperiods(lord, years):
    """IV.1, 5-6: each planetary fardar divides into seven equal parts,
    the lord itself first, then "the planet which is below it in the
    celestial circle" and so on down the spheres.

    IV.1, 8: the Head and the Tail have NO sub-periods -- they "stand
    alone in the management of their years ... because they do not have
    houses". Returns []."""
    if lord in NODE_FARDAR_YEARS:
        return []
    i = PN4_DESCENDING_SPHERES.index(lord)
    part = float(years) / 7.0
    return [(PN4_DESCENDING_SPHERES[(i + k) % 7], part) for k in range(7)]

# --- VI.1: the lord of the orb -------------------------------------------
# "you look at the lord of the hour in which the native was born, and
# assign it to the Ascendant and to the first year from his birth"
# (VI.1, 4); "the lord of the second hour from it to the second house
# ... and to the second year" (5), and so on, "so that the lord of the
# twelfth hour from the lord of the hour in which the native was born,
# belongs to the twelfth house ... and the lord of the thirteenth hour
# from it belongs to the Ascendant of the root and the thirteenth year"
# (VI.1, 8) -- a CONTINUOUS loop of the seven hour lords against the
# twelve-year cycle of the profection, so the pairing changes every
# twelve years. Judged "just as you judge by means of the lord of the
# year" (VI.1, 12). Indicator #5 of the year (II.1, 10).
#
# The hour lords run down the spheres, "the planet which is below it in
# the circle" (IX.7, 3-5 and Dykes' Figure 45): after the natal hour lord
# comes the next in PN4_DESCENDING_SPHERES, cyclically. VI.1, 10 names
# each by the house its number matches -- "the lord of the hour of the
# house of assets" is the SECOND hour lord from the natal one -- and
# VI.1, 18-19 use those names for six fixed positions: the Ascendant,
# Midheaven and house of hope of the root, and the sign of the year with
# the tenth and eleventh from it. Those are read here by VI.1, 10's
# naming, hour k for house k, without the twelve-year "reset" Dykes
# proposes in Intro Sect. 13 and calls "my idea".
#
# What PN IV presupposes and does not state: the planetary hours
# themselves. The sequence from the day lord at sunrise is Dykes' Figure
# 45 (Intro Sect. 13), and the engine's calculate_chronocrats follows it,
# with real sunrise and sunset and a flagged equal-hour approximation
# where the Sun is circumpolar. Dykes floats a single-cycle alternative
# (each house keeping its first hour lord for life, Intro Figure 48) on
# the thought that the loop is Abu Ma'shar's own error; VI.1, 8 states
# the loop, and the owner chose it 2026-09-10. The delineations of VI.1,
# 12-17 are not built; the seven-day grant of IX.7, 7-9 IS -- method 2 of the
# days tab, pn4_ix7_weeks_from_orb (an earlier line here said it was not; order GAP-27).

def pn4_hour_lord_from_natal(natal_hour_lord, steps):
    """The lord of the hour `steps` hours after the natal one, down the
    spheres and round again (VI.1, 5-8)."""
    if natal_hour_lord not in PN4_DESCENDING_SPHERES:
        return None
    i = PN4_DESCENDING_SPHERES.index(natal_hour_lord)
    return PN4_DESCENDING_SPHERES[(i + int(steps)) % 7]

def pn4_lord_of_the_orb(natal_hour_lord, completed_years):
    """VI.1, 4-8: the lord of the orb for the year -- the natal hour lord
    at age 0, and one hour lord further down the spheres for every
    completed year, without reset."""
    return pn4_hour_lord_from_natal(natal_hour_lord, completed_years)

def pn4_hour_lord_of_house(natal_hour_lord, house):
    """VI.1, 10: "the lord of the hour of the house of X" is the hour lord
    numbered as the house, counted from the natal hour as the first."""
    return pn4_hour_lord_from_natal(natal_hour_lord, int(house) - 1)

def pn4_named_lords_of_the_orb(natal_hour_lord, completed_years):
    """VI.1, 18-19: the six named lords of the orb -- the hour lords of
    the Ascendant, Midheaven and house of hope of the root (18), and of
    the sign of the terminal point and the tenth and eleventh from it
    (19), each by VI.1, 10's naming."""
    k = int(completed_years) % 12 + 1              # the house of the sign of the year from the natal Ascendant
    positions = (
        ('Ascendant of the root', 1, 'VI.1, 18'),
        ('Midheaven of the root', 10, 'VI.1, 18'),
        ('House of hope of the root', 11, 'VI.1, 18'),
        ('Sign of the terminal point', k, 'VI.1, 19'),
        ('Tenth from the sign of the year', (k - 1 + 9) % 12 + 1, 'VI.1, 19'),
        ('Eleventh from the sign of the year', (k - 1 + 10) % 12 + 1, 'VI.1, 19'),
    )
    return [{'Position': label, 'House': house, 'Hour from the natal hour': house,
             'Lord of the hour': pn4_hour_lord_of_house(natal_hour_lord, house) or '-',
             'Source': cite} for label, house, cite in positions]

# --- VI.2, 1-26: the turning of the houses of the root ---------------------
# "every one of the seven planets, the twelve houses, and the twelve Lots,
# is turned at the revolutions of years from its own position (a year for
# every sign), and is directed from its degree (a year for every degree);
# and when any of them, by turning or by direction, reaches a sign or
# planetary fortune or infortune, it produces the indication of that sign
# or planet" (VI.2, 1). VI.2, 2-17 assign the points to topics; 18-20
# generalise to any indicator; 21-26 handle a quadrant cusp that falls in
# a different sign from its whole-sign house -- turned "in two ways",
# from the house by counting and from the sign the degree falls in
# (VI.2, 22), directed from its actual degree (21).
#
# ONLY THE TURNING IS BUILT. It is whole-sign profection from each point's
# own natal position, one sign a year, exactly as the Ascendant's. The
# direction "a year for every degree" is III.1, 12's third case for
# planets and Lots (method not stated in PN IV) and, for cusps, VI.2, 21's
# "portions of the hours and the right circle" -- a name for semi-arcs
# with no procedure -- so it stays refused, and the table says so per
# row. The Ascendant's and the meridian's directions are the two
# distributions on the page and the rows for houses 1, 10 and 4 point to
# them.
#
# What is read in and said on the page: which "twelve Lots" is not
# stated; the formulas in fn 12-31 are Dykes' identifications from Sahl
# and the Great Introduction, and the engine's Lots are paired to them
# below with the two places they differ on the night reversal named.
# "Whichever had the shift in the root" (VI.2, 6, 8) is the sect planet,
# per fn 16 and 19. The triplicity-lord examinations of VI.2, 4-5 and all
# the delineation are not built. No worked example exists; Figures 90-91
# are Dykes' diagrams.

PN4_TURNING_HOUSES = (
    (1, 'the body, with the Moon', 'VI.2, 3'),
    (2, 'assets, with the Lots of Fortune and assets', 'VI.2, 4'),
    (3, 'siblings, with its Lot', 'VI.2, 5'),
    (4, 'the fathers, with the Lot of the father', 'VI.2, 6'),
    (5, 'children, with its Lot', 'VI.2, 9'),
    (6, 'slaves, and illnesses, with their Lots', 'VI.2, 10-11'),
    (7, 'women, with its Lot', 'VI.2, 12'),
    (8, 'death and catastrophes, with its Lot', 'VI.2, 13'),
    (9, 'travel, with its Lot', 'VI.2, 14'),
    (10, 'authority and rank, with its Lot; the mother (VI.2, 8)', 'VI.2, 15'),
    (11, 'hope and friends, with its Lot', 'VI.2, 16'),
    (12, 'enemies and riding animals, with its Lot', 'VI.2, 17'),
)

# (lot id, what it is turned for, citation, note). The ids are the
# engine's LOT_DEFINITIONS rows; the pairing to VI.2's footnotes is Dykes'.
PN4_TURNING_LOTS = (
    ('fortune', 'assets', 'VI.2, 4', ''),
    ('assets_lord2', 'assets', 'VI.2, 4; fn 12', ''),
    ('siblings_hermes', 'siblings', 'VI.2, 5; fn 15',
     'fn 15 reverses it at night (Firmicus); the engine\'s Sahl row does not ("for one who was born by day and night")'),
    ('father', 'the fathers', 'VI.2, 6; fn 17', ''),
    ('mother', 'the mother', 'VI.2, 8; fn 20', ''),
    ('children_hermes', 'children', 'VI.2, 9; fn 22', ''),
    ('slaves', 'slaves', 'VI.2, 10; fn 24', ''),
    ('chronic_illness', 'illnesses', 'VI.2, 11; fn 25', ''),
    ('marriage_men', 'women (for men)', 'VI.2, 12; fn 26',
     'fn 26 reverses it at night; the engine\'s Sahl row does not'),
    ('marriage_women', 'women (for women)', 'VI.2, 12; fn 26',
     'fn 26 reverses it at night; the engine\'s Sahl row does not'),
    ('death', 'death and catastrophes', 'VI.2, 13; fn 27', ''),
    ('travel', 'travel', 'VI.2, 14; fn 28', ''),
    ('work_expedition_paul', 'authority and rank', 'VI.2, 15; fn 29', 'Gr. Intr. VIII.4, Saturn to the Moon, reversed at night'),
    ('work_action', 'authority and rank (action)', 'VI.2, 15; fn 29', 'the alternative fn 29 names'),
    ('friends', 'hope and friends', 'VI.2, 16; fn 30', ''),
    ('enemies_necessity', 'enemies', 'VI.2, 17; fn 31', 'one of fn 31\'s three'),
    ('enemies_slaves', 'enemies', 'VI.2, 17; fn 31', 'one of fn 31\'s three'),
    ('enemies_hermes', 'enemies', 'VI.2, 17; fn 31', 'one of fn 31\'s three'),
)

PN4_TURNING_DIRECTION_REFUSED = ("refused: a year for every degree needs III.1, 12's third case, "
                                 "whose method is not stated in PN IV")

def pn4_turning_planet_topics(sect):
    """VI.2, 2, 6 and 8: what each planet is turned for. The parents'
    indicators are the sect planets, "whichever one of the two had the
    shift in the root" (fn 16, 19)."""
    diurnal = sect == 'Diurnal'
    topics = {
        'Sun': 'rank, works, and authority (VI.2, 2)' + ('; the fathers (VI.2, 6)' if diurnal else ''),
        'Moon': 'the accidents of the body (VI.2, 2-3)' + ('' if diurnal else '; the mother (VI.2, 8)'),
        'Jupiter': 'assets (VI.2, 2)',
        'Venus': 'women, amusement, delight, and fornication (VI.2, 2)' + ('; the mother (VI.2, 8)' if diurnal else ''),
        'Saturn': 'what it indicates (VI.2, 2)' + ('' if diurnal else '; the fathers (VI.2, 6)'),
        'Mars': 'what it indicates (VI.2, 2)',
        'Mercury': 'what it indicates (VI.2, 2)',
    }
    return topics

def _pn4_natal_planets_in_sign(planetary_data, sign):
    """VI.2, 1: the "planetary fortune or infortune" a turned point
    reaches. Every natal planet in the sign, tagged."""
    found = []
    for planet in PN4_SEVEN:
        row = planetary_data.get(planet)
        if row and get_zodiac_sign(row['longitude']) == sign:
            tag = 'fortune' if planet in FORTUNES else 'infortune' if planet in INFORTUNES else 'neither'
            found.append(f"{planet} ({tag})")
    return ', '.join(found) if found else 'none'

def pn4_turned_sign(natal_lon, completed_years):
    """VI.2, 1: "a year for every sign", from the point's own position."""
    return get_zodiac_sign(pn4_profect(natal_lon, int(completed_years)))

def pn4_turning_rows(chart_data, completed_years):
    """The turning table of VI.2, 1-26 for one age: every planet, every
    house (with a displaced quadrant cusp turned a second way, VI.2, 22),
    and the Lots VI.2 names, each from its own natal position."""
    planetary = chart_data['planetary_data']
    asc, cusps, sect = chart_data['ascendant'], chart_data['houses'], chart_data['sect']
    age = int(completed_years)

    def row(point, natal_lon, topic, cite, directed):
        sign = pn4_turned_sign(natal_lon, age)
        return {
            'Point': point, 'For the knowledge of': topic,
            'Natal': f"{get_zodiac_sign(natal_lon)} ({get_degree_string(natal_lon)})",
            'Turned to': sign,
            'Its lord': SIGN_TO_DOMICILE.get(sign, '-'),
            'Natal planets there': _pn4_natal_planets_in_sign(planetary, sign),
            'Directed a year per degree': directed,
            'Source': cite,
        }

    rows = []
    topics = pn4_turning_planet_topics(sect)
    for planet in PN4_SEVEN:
        if planet in planetary:
            rows.append(row(planet, planetary[planet]['longitude'], topics[planet], 'VI.2, 1-2',
                            PN4_TURNING_DIRECTION_REFUSED))

    directed_at = {1: 'the distribution from the Ascendant, above (III.1, 12)',
                   10: 'the distribution from the Midheaven, above (III.1, 12)',
                   4: 'the distribution from the fourth, above (III.1, 12)'}
    for house, topic, cite in PN4_TURNING_HOUSES:
        ws_start = ((asc // 30.0) * 30.0 + 30.0 * (house - 1)) % 360.0
        directed = directed_at.get(house, "refused: VI.2, 21's \"portions of the hours and the right circle\" "
                                          "names semi-arcs and gives no procedure")
        rows.append(row(f'House {house} (by counting)', ws_start, topic, cite, directed))
        cusp = cusps[house - 1] if cusps and len(cusps) >= house else None
        if cusp is not None and get_zodiac_sign(cusp) != get_zodiac_sign(ws_start):
            rows.append(row(f'House {house} (its degree, {get_degree_string(cusp)}, in another sign)', cusp,
                            topic + ' -- the second turning, VI.2, 22 [2]', 'VI.2, 21-24', directed))

    for lot_id, topic, cite, note in PN4_TURNING_LOTS:
        d = next(x for x in LOT_DEFINITIONS if x['id'] == lot_id)
        lon = lot_by_id(lot_id, planetary, asc, cusps, sect)
        if lon is None:
            continue
        rows.append(row(d['name'] + (f' -- {note}' if note else ''), lon, topic, cite,
                        PN4_TURNING_DIRECTION_REFUSED))
    return rows

# --- II.1, 11-24: indicators 6-19 of the year, the FACT each one reads ----
# II.1, 5-24 list nineteen indicators and II.1, 25 ranks them. The first
# five are computed above. Of the rest, each READS a fact from the root
# and the revolution and then judges it in a chapter of its own; the
# facts are computed here, the judgments are not. Three kinds:
#   positional (6, 8, 9, 10, 12, 13, 14, 18, 19): a lookup on charts
#     already cast;
#   connection-dependent (7, 15): II.22, 1-4 wants the Moon's connection
#     to perfect "so long as she is in her own sign", and VI.6, 3-7 the
#     house lords' connections in the revolution; the engine's connection
#     test is a static one for the natal chart under the Configurations
#     page's rule and does not encode II.22's condition -- NOT computed,
#     and the row says so;
#   through the year (16, 17): continuous transits -- NOT tracked.
# Decided by the owner 2026-09-10 (positional nine, honest rows for the
# other four). Nothing here delineates.

def _pn4_transit_grade(sr_lon, natal_lon):
    """V.1, 2-3: a planet in the revolution "reaches its own rooted
    degree", or "the bound which it was in at the root", or "[only] that
    sign in which it was". None if not even the sign."""
    if get_zodiac_sign(sr_lon) != get_zodiac_sign(natal_lon):
        return None
    if abs((sr_lon - natal_lon + 180.0) % 360.0 - 180.0) < 1.0:
        return 'degree'
    if pn4_bound_lord(sr_lon) == pn4_bound_lord(natal_lon):
        return 'bound'
    return 'sign'

def _pn4_house_from(lon, from_lon):
    """Whole-sign house of `lon` counted from the sign of `from_lon`."""
    return get_wsh_house(lon, from_lon)

def pn4_further_indicators(chart_data, sr, year_lon, moon=None):
    """Indicators 6-19 of the year (II.1, 11-24): one row each, the fact
    it reads computed where it is a lookup on the root and the
    revolution, and stated as not computed where it is not."""
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    n_asc, r_asc = chart_data['ascendant'], sr['ascendant']
    year_sign = get_zodiac_sign(year_lon)
    lord = lambda lon: SIGN_TO_DOMICILE.get(get_zodiac_sign(lon), '-')
    places = (('natal Ascendant', n_asc), ('sign of the terminal point', year_lon),
              ('Ascendant of the revolution', r_asc))

    def planets_in_sign(data, sign):
        return [p for p in PN4_SEVEN if p in data and get_zodiac_sign(data[p]['longitude']) == sign]

    rows = []
    # 6
    rows.append({'#': 6, 'Indicator': 'The Ascendant of the revolution, and its lord',
                 'Reads': f"{get_zodiac_sign(r_asc)} ({get_degree_string(r_asc)}), lord {lord(r_asc)}",
                 'Source': 'II.1, 11; VI.3, 1-2'})
    # 7
    moon_lon = rev['Moon']['longitude']
    if moon is None:
        reads7 = (f"the revolution's Moon in {get_zodiac_sign(moon_lon)} ({get_degree_string(moon_lon)}), lord of her house "
                  f"{lord(moon_lon)}; her connections within the sign are NOT computed -- II.22, 1-4 need the "
                  f"connection to perfect before she leaves the sign, which the engine's static test does not encode")
    elif moon['void']:
        reads7 = (f"the revolution's Moon in {moon['sign']} ({get_degree_string(moon_lon)}) is empty in course -- she "
                  f"leaves the sign on day {moon['exit_day']:.2f} without perfecting a connection -- so the lord of her "
                  f"house, {moon['house_lord']}, stands in (II.22, 4)")
    else:
        reads7 = (f"the revolution's Moon in {moon['sign']} ({get_degree_string(moon_lon)}) connects, before leaving it on "
                  f"day {moon['exit_day']:.2f}, with " + '; '.join(
                      f"{c['planet']} by {c['aspect']} on day {c['day']:.2f}" for c in moon['connections'])
                  + " (II.22, 1-2; the portions of the year below)")
    rows.append({'#': 7, 'Indicator': 'The Moon and the planets she connects with in her sign; if void, the lord of her house',
                 'Reads': reads7, 'Source': 'II.1, 12; II.22, 1-4'})
    # 8
    transits = []
    for p in PN4_SEVEN:
        if p not in rev:
            continue
        for q in PN4_SEVEN:
            if q not in natal:
                continue
            grade = _pn4_transit_grade(rev[p]['longitude'], natal[q]['longitude'])
            if grade:
                transits.append(f"{p} on {'its own' if p == q else 'natal ' + q} place, by {grade}")
    rows.append({'#': 8, 'Indicator': "Transits over rooted positions, one planet's or another's",
                 'Reads': '; '.join(transits) if transits else 'none, even by sign',
                 'Source': 'II.1, 13; V.1, 1-3'})
    # 9
    ly = lord(year_lon)
    ly_lon = rev.get(ly, {}).get('longitude')
    # II.6, 1, the first chapter this row cites, names THREE Ascendants --
    # "one of the stakes of the Ascendant of the root, or of the terminal
    # point, or of the Ascendant of the revolution" -- so the house is read
    # from each, in row 14's format (order PN4R-4g-2; it read the
    # revolution's alone). Whole-sign places, the topic unit.
    rows.append({'#': 9, 'Indicator': 'The lord of the year in one of the twelve houses of the revolution',
                 'Reads': (f"{ly} ({get_zodiac_sign(ly_lon)}, {get_degree_string(ly_lon)}) in house "
                           + ' / '.join(str(_pn4_house_from(ly_lon, from_lon)) for _l, from_lon in places)
                           + " (from the natal Ascendant / the terminal sign / the revolution Ascendant)") if ly_lon is not None else '-',
                 'Source': 'II.1, 14; II.6, 1 (the three Ascendants); II.6, II.9, II.12, II.15, II.18, II.21'})
    # 10
    parts = []
    for label, from_lon in places:
        L = lord(from_lon)
        L_lon = rev.get(L, {}).get('longitude')
        if L_lon is not None:
            parts.append(f"lord of the {label} ({L}): house {_pn4_house_from(L_lon, from_lon)} from {get_zodiac_sign(from_lon)}")
    rows.append({'#': 10, 'Indicator': "The three lords relative to their own places, in the revolution",
                 'Reads': '; '.join(parts), 'Source': 'II.1, 15; VI.6, 1-2 (fn 128: relative to its own Ascendant)'})
    # 11
    rows.append({'#': 11, 'Indicator': 'The turning of the planets and the twelve houses',
                 'Reads': 'the turning table below', 'Source': 'II.1, 16; VI.2'})
    # 12
    h_year, h_rasc = _pn4_house_from(year_lon, n_asc), _pn4_house_from(r_asc, n_asc)
    in_year = planets_in_sign(rev, year_sign)
    in_rasc = planets_in_sign(rev, get_zodiac_sign(r_asc))
    rows.append({'#': 12, 'Indicator': "The terminal sign or the revolution's Ascendant on a natal house, with a revolution planet in it",
                 'Reads': (f"terminal sign {year_sign} = natal house {h_year}, revolution planets there: "
                           f"{', '.join(in_year) or 'none'}; revolution Ascendant {get_zodiac_sign(r_asc)} = natal house "
                           f"{h_rasc}, revolution planets there: {', '.join(in_rasc) or 'none'}; "
                           f"{'the two are ONE house (VI.3, 3)' if h_year == h_rasc else 'two different houses'}"),
                 'Source': 'II.1, 17; VI.3, 3-5'})
    # 13
    rows.append({'#': 13, 'Indicator': "The terminal sign or the revolution's Ascendant on a natal planet",
                 'Reads': (f"natal planets in the terminal sign {year_sign}: {', '.join(planets_in_sign(natal, year_sign)) or 'none'}; "
                           f"in the revolution's Ascendant {get_zodiac_sign(r_asc)}: "
                           f"{', '.join(planets_in_sign(natal, get_zodiac_sign(r_asc))) or 'none'}"),
                 'Source': 'II.1, 18; VI.4, 1-3'})
    # 14
    moves = []
    for p in PN4_SEVEN:
        if p in natal and p in rev:
            nh = _pn4_house_from(natal[p]['longitude'], n_asc)
            rh = [_pn4_house_from(rev[p]['longitude'], from_lon) for _l, from_lon in places]
            moves.append(f"{p}: natal {nh} -> {rh[0]} / {rh[1]} / {rh[2]}")
    rows.append({'#': 14, 'Indicator': 'A natal planet in another house in the revolution, from the three places',
                 'Reads': '; '.join(moves) + ' (natal house -> from the natal Ascendant / the terminal sign / the revolution Ascendant)',
                 'Source': 'II.1, 19; VI.5, 1-4'})
    # 15
    rows.append({'#': 15, 'Indicator': 'The connections of the lords of the houses with each other',
                 'Reads': "NOT computed: VI.6, 3-7 read the lords' connections in the revolution; the engine's connection "
                          "test is a static one for the natal chart under the Configurations page's rule",
                 'Source': 'II.1, 20; VI.6, 3-7'})
    # 16, 17
    rows.append({'#': 16, 'Indicator': "Each planet's shifting through the houses, bounds, bodies, rays, twelfth-parts and Lots during the year",
                 'Reads': 'NOT tracked: the year\'s transits are not followed', 'Source': 'II.1, 21; Books V, VI, VIII'})
    rows.append({'#': 17, 'Indicator': 'The connections of the planets with each other during the year',
                 'Reads': 'NOT tracked: the year\'s transits are not followed', 'Source': 'II.1, 22; VI.6; Book VII'})
    # 18
    dign = []
    for p in PN4_SEVEN:
        if p in rev:
            L, B = lord(rev[p]['longitude']), pn4_bound_lord(rev[p]['longitude'])
            dign.append(f"{p} in {get_zodiac_sign(rev[p]['longitude'])} ({'own house' if L == p else 'house of ' + L}; "
                        f"{'own bound' if B == p else 'bound of ' + B})")
    rows.append({'#': 18, 'Indicator': "Each planet in its own house or another's, its own bound or another's",
                 'Reads': '; '.join(dign), 'Source': 'II.1, 23; VIII.1-15'})
    # 19
    node = rev.get('North Node', {}).get('longitude')
    if node is not None:
        head = [str(_pn4_house_from(node, f)) for _l, f in places]
        tail = [str(_pn4_house_from(node + 180.0, f)) for _l, f in places]
        reads = (f"Head in {get_zodiac_sign(node)}, houses {' / '.join(head)}; Tail in "
                 f"{get_zodiac_sign(node + 180.0)}, houses {' / '.join(tail)} (from the natal Ascendant / the terminal "
                 f"sign / the revolution Ascendant)")
    else:
        reads = '-'
    rows.append({'#': 19, 'Indicator': 'The Head and Tail', 'Reads': reads, 'Source': 'II.1, 24; VII.9, 1'})
    return rows

# --- IX.9, 1-10 and IX.2, 4-7: the "governor" (mustawli) --------------------
# IX.9, 1-9 list "eight special indicators": the lord of the year; the
# distributor from the Ascendant; the distributor from the [longevity]
# releaser; "the partner to them both, by body and rays"; the lord of the
# fardar; the lord of the orb; "the one accepting the connection of the
# Moon, or the lord of her house"; "the first lord of the Ascendant of the
# revolution". IX.9, 10: "if these eight indicators would combine together
# in a single planet, then it alone would be the governor of the
# indication for the condition of the year; and if one of them had [only]
# some of the testimonies, it will be more primary than the others, and
# the rest of them will have a partnership with it".
#
# PARTIAL, on purpose, and the page says so per row. Testimony #3 and the
# releaser's half of #4 need the longevity releaser, which PN IV does not
# supply (IX.8, 123); since 2026-09-10 the bundle passes the releaser's
# distribution from Sahl (On Nativities 1.15) when one is found, and the
# rows read unavailable otherwise; #7 needs the Moon's
# connection read in the revolution (her house lord is the fallback only
# when she is void), which is not computed. The tally runs over the six
# that are available, names the primary among them, and NEVER prints a
# planet as governor "alone", which IX.9, 10 reserves for all eight. "The
# first lord" of the revolution's Ascendant is read as its domicile lord
# (fn 324; "the first one is stronger in indication"). Decided by the
# owner 2026-09-10.
#
# IX.2, 4 gives a second, sign-level governor for the first month: the
# natal Lot of Fortune in the natal Ascendant, so that the terminal point
# from the Ascendant and from the Lot "is one [and the same] sign", the
# revolution's Ascendant "is also that sign, and in it is the Lot of
# Fortune of the revolution, and that sign is convertible" -- five
# conditions, shown one by one, since most years fail one of them. Fn 37:
# such a sign governs the whole year too. Fn 39 is Dykes' worked case
# (age 39, everything in Cancer, the Moon), and is the fixture. IX.9,
# 11-13 and IX.2, 8-11, the judgments, are not built.

PN4_GOVERNOR_TESTIMONIES = (
    (1, 'The lord of the year', 'IX.9, 2'),
    (2, 'The distributor from the Ascendant', 'IX.9, 3'),
    (3, 'The distributor from the [longevity] releaser', 'IX.9, 4'),
    (4, 'The partner to them both, by body and rays', 'IX.9, 5'),
    (5, 'The lord of the fardar', 'IX.9, 6'),
    (6, 'The lord of the orb', 'IX.9, 7'),
    (7, "The one accepting the Moon's connection, or the lord of her house", 'IX.9, 8'),
    (8, "The first lord of the Ascendant of the revolution", 'IX.9, 9'),
)
PN4_GOVERNOR_RELEASER_REASON = ("unavailable: needs the longevity releaser's distribution, which was not supplied "
                                "(PN IV does not choose the releaser, IX.8, 123; the engine takes it from Sahl, "
                                "On Nativities 1.15, when that finds one)")
PN4_GOVERNOR_CONNECTION_REASON = ("unavailable: the Moon's connection is not read in the revolution, and her "
                                  "house lord stands in only when she is void, which is not determined")

def pn4_governor(year_lord, distributor, partner, distribution_note, fardar_lord, orb_lord, sr_ascendant_lon,
                 moon_testimony=None, moon_void=None, releaser_distributor=None, releaser_partner=None,
                 releaser_note=None):
    """IX.9, 1-10 over the testimonies this engine can supply.
    Returns (rows, summary): one row per testimony with the planet or the
    reason it is unavailable, and a summary with the tally, the primary
    planet(s) among the available testimonies, and how many of eight
    were counted. `distribution_note` explains a missing distributor
    (refused at the poles, or the age past the table). Testimony #3 is
    the distributor of the releaser's distribution (Sahl, On Nativities
    1.15, 22; 1.18, 20), passed in when there is one, else `releaser_note`
    says why not. #4, "the partner to them both", is counted only when
    the two distributions have the SAME partner (a reading); otherwise
    both partners are shown and the row is not counted."""
    releaser_reason = f"unavailable: {releaser_note}" if releaser_note else PN4_GOVERNOR_RELEASER_REASON
    if distributor and releaser_distributor:
        if partner and partner == releaser_partner:
            both = f"{partner}; partner to both distributions"
        else:
            both = (f"not one partner to both, not counted: the Ascendant's is {partner or 'none'}, the releaser's "
                    f"{releaser_partner or 'none'}")
    elif distributor:
        both = f"not counted: the Ascendant's partner is {partner or 'none'}; the releaser's {releaser_reason}"
    else:
        both = f"unavailable: {distribution_note}"
    got = {
        1: year_lord,
        2: distributor or f"unavailable: {distribution_note}",
        3: releaser_distributor or releaser_reason,
        4: both,
        5: fardar_lord or 'unavailable',
        6: orb_lord or 'unavailable: natal hour lord unavailable',
        7: ((f"{moon_testimony}; {'the lord of her house, she being empty in course' if moon_void else 'accepting her connection'} (II.22, 1-4)")
            if moon_testimony else PN4_GOVERNOR_CONNECTION_REASON),
        8: SIGN_TO_DOMICILE.get(get_zodiac_sign(sr_ascendant_lon), '-'),
    }
    rows, tally, counted = [], {}, 0
    for n, label, cite in PN4_GOVERNOR_TESTIMONIES:
        value = got[n]
        planet = value.split(';')[0] if isinstance(value, str) else None
        available = planet in PN4_SEVEN
        if available:
            counted += 1
            tally[planet] = tally.get(planet, 0) + 1
        rows.append({'#': n, 'Testimony': label, 'Planet': value,
                     'Counted': 'yes' if available else 'no', 'Source': cite})
    top = max(tally.values()) if tally else 0
    primary = sorted(p for p, c in tally.items() if c == top) if tally else []
    summary = {
        'tally': tally, 'counted': counted, 'primary': primary, 'top': top,
        'text': ((f"{primary[0]} ALONE is the governor: all eight testimonies combine in it (IX.9, 10).")
                 if counted == 8 and top == 8 else
                 (f"{primary[0] if len(primary) == 1 else ', '.join(primary[:-1]) + ' and ' + primary[-1]} "
                  f"{'is' if len(primary) == 1 else 'are'} primary with {top} of the "
                  f"{counted} testimonies available (of eight); the rest partner with "
                  f"{'it' if len(primary) == 1 else 'them'} (IX.9, 10). No planet is the governor ALONE here: "
                  + (f"that needs all eight, and {8 - counted} are unavailable." if counted < 8
                     else "that needs all eight to combine in one planet, and they do not."))) if primary else
                'no testimony available',
    }
    return rows, summary

def pn4_first_month_governor(natal_ascendant, natal_fortune, year_lon, sr_ascendant, sr_fortune):
    """IX.2, 4: the five conditions, one by one, and whether all hold."""
    year_sign = get_zodiac_sign(year_lon)
    asc_sign, lot_sign = get_zodiac_sign(natal_ascendant), get_zodiac_sign(natal_fortune)
    conditions = [
        ('The natal Lot of Fortune is in the natal Ascendant', lot_sign == asc_sign,
         f"Lot in {lot_sign}, Ascendant in {asc_sign}", 'IX.2, 4 [#1, #3]'),
        ('So the terminal point from the Ascendant and from the Lot is one sign', lot_sign == asc_sign,
         f"both reach {year_sign}" if lot_sign == asc_sign else 'they reach different signs', 'IX.2, 4; fn 35'),
        ("The Ascendant of the revolution is that sign", get_zodiac_sign(sr_ascendant) == year_sign,
         f"revolution Ascendant in {get_zodiac_sign(sr_ascendant)}", 'IX.2, 4 [#4]'),
        ("The Lot of Fortune of the revolution is in it", get_zodiac_sign(sr_fortune) == year_sign,
         f"revolution Lot in {get_zodiac_sign(sr_fortune)}", 'IX.2, 4 [#5]'),
        ('That sign is convertible, so its lord is also the lord of its first ninth-part',
         PN4_QUADRUPLICITY.get(year_sign) == 'convertible',
         f"{year_sign} is {PN4_QUADRUPLICITY.get(year_sign)}; ninth-part lord {pn4_first_ninth_part_lord(year_sign)['lord']}, "
         f"sign lord {SIGN_TO_DOMICILE.get(year_sign, '-')}", 'IX.2, 4 [#2]; fn 36'),
    ]
    rows = [{'Condition': c, 'Holds': 'yes' if ok else 'no', 'Reads': reads, 'Source': cite}
            for c, ok, reads, cite in conditions]
    holds = all(ok for _c, ok, _r, _s in conditions)
    verdict = (f"{year_sign} and its lord {SIGN_TO_DOMICILE.get(year_sign, '-')} govern the first month, and the "
               f"year with it (fn 37)" if holds else
               f"no governor: {sum(1 for _c, ok, _r, _s in conditions if not ok)} of the five conditions fail")
    return rows, verdict

# --- II.22, 1-4: the Moon's connections in her sign; the portions of the year
# "[4] the planet which the Moon connects with, so long as she is in her
# [current] sign. Now if in that sign she connected with not just one,
# then see how many there are: for if it was two planets, the year is
# divided into two halves; and if her connection in that sign of hers was
# with three planets, then that year is divided into equal thirds; and if
# it increased beyond that, then the year is divided according to their
# number. So, his condition in each one of the portions of the year ...
# will be in accordance with the condition of the planet which owns the
# portion. But if the Moon was empty in course, his situation will be in
# accordance with the condition of the lord of her house, whether it
# looked at her or not" (II.22, 1-4; the fallback again at 17). The
# connection is indicator #7 of every year (II.1, 12) and testimony #7 of
# the governor (IX.9, 8).
#
# READ INTO THE SENTENCES, and said on the page: "connects with" is a
# perfection by degree, of the body or a Ptolemaic ray, before the
# revolution's Moon leaves her sign -- found by the engine's forward
# simulation and _perfection_day, which revalidates the whole-sign
# configuration at the moment of perfection (VII.5, 14: no out-of-sign
# connection); the portions go to the planets in the ORDER she connects
# (not stated); the division is stated inside "If the Moon was the lord
# of the year" (II.22, 1) and is computed every year with the row saying
# whether this year's lord is the Moon (owner's decision 2026-09-10);
# "empty in course" is no such perfection before she leaves the sign.
# II.22, 11's rays, Lots and twelfth-parts are not counted. The
# judgments of II.22, 5-24 are not built. No worked example exists.
PN4_MOON_ASPECTS = ((0.0, 'body'), (60.0, 'sextile'), (90.0, 'square'), (120.0, 'trine'), (180.0, 'opposition'))

def _pn4_luminary_connections(sr_planetary_data, jd_sr, body, horizon_days, step_days, applying_only):
    """The planets a luminary of the revolution connects with before it
    leaves its sign, in day order. `applying_only` keeps a perfection only
    if the luminary is the faster body at that moment -- the one "handing
    over" (II.13, 1) rather than being handed to. The Moon is always the
    faster, so for her it changes nothing."""
    sim = _simulate_forward(sr_planetary_data, jd_sr, horizon_days=horizon_days, step_days=step_days)
    exit_day = next((d for d in sim['events'][body]['sign_exits'] if d > 0.0), None)
    lon0 = sr_planetary_data[body]['longitude'] % 360.0
    sign = get_zodiac_sign(lon0)
    found = []
    for planet in PN4_SEVEN:
        if planet == body or planet not in sr_planetary_data:
            continue
        for target, name in PN4_MOON_ASPECTS:
            day = _perfection_day(sim, body, planet, target, before_day=exit_day)
            if day is None or day <= 0.0:
                continue
            if applying_only:
                v_body = swe.calc_ut(jd_sr + day, PLANET_SWE_IDS[body])[0][3]
                v_planet = swe.calc_ut(jd_sr + day, PLANET_SWE_IDS[planet])[0][3]
                if not v_body > v_planet:
                    continue
            found.append({'day': day, 'planet': planet, 'aspect': name, 'moon_at': _lon_at(sim, body, day)})
    found.sort(key=lambda c: c['day'])
    return {'sign': sign, 'moon_lon': lon0, 'exit_day': exit_day, 'connections': found,
            'void': not found, 'house_lord': SIGN_TO_DOMICILE.get(sign, '-')}

def pn4_moon_connections(sr_planetary_data, jd_sr):
    """The planets the revolution's Moon connects with before she leaves
    her sign (II.22, 1), in the order she reaches them. Returns
    {sign, moon_lon, exit_day, connections: [{day, planet, aspect, moon_at}],
    void, house_lord}; days are from the revolution."""
    return _pn4_luminary_connections(sr_planetary_data, jd_sr, 'Moon', 6, 0.25, applying_only=False)

def pn4_sun_handover(sr_planetary_data, jd_sr):
    """II.13, 1 [3]: "the planet to which the Sun hands over the management
    (so long as it is in its sign)" -- read, with fn 239, as the Sun's
    own connections before he leaves his sign, and "hands over" as the
    Sun being the applying body at the perfection. Same shape as
    pn4_moon_connections; 'moon_at' is the Sun's longitude then."""
    return _pn4_luminary_connections(sr_planetary_data, jd_sr, 'Sun', 40, 1.0, applying_only=True)

def pn4_moon_portions(connections, year_days):
    """II.22, 2-3: the year divided by the number of planets she connects
    with, each portion owned by one of them, in the order of connection."""
    n = len(connections)
    if n == 0:
        return []
    size = float(year_days) / n
    return [{'portion': i + 1, 'of': n, 'planet': c['planet'], 'from_day': i * size, 'to_day': (i + 1) * size}
            for i, c in enumerate(connections)]

def pn4_moon_testimony(moon):
    """IX.9, 8 / II.1, 12: "the one accepting the connection of the Moon,
    or the lord of her house" -- the first planet she connects with in
    her sign, else her house lord."""
    if not moon:
        return None
    if moon['connections']:
        return moon['connections'][0]['planet']
    return moon['house_lord']

# --- III.2: the distribution analysed ------------------------------------
# Three stated pieces, and the prose between them left alone.
#   III.2, 4-9   a checklist of questions about the bound the distribution
#                stands in -- answered here as FACTS, not judged;
#   III.2, 10-17 seven "static" types of distributor and partner, by
#                fortune and infortune (Figure 66) -- delineated at 18-54
#                under conditions in root and revolution, which are not
#                judged here;
#   III.2, 55-86 twenty-four transitions inside a year, by the natures of
#                the outgoing and incoming bound lords and managers, and
#                III.2, 87-101 their twelve indications, one sentence
#                each, quoted verbatim on the page.
# III.2, 105: the twelve concern the manager by its ROOTED body or ray --
# the natal distribution table -- and a revolutionary planet entering the
# bound (43, 46-47, 54) is a different matter, not built. III.2, 110-111
# gate every death statement in the chapter on "the years of the lifespan
# which his [longevity] indicator in the root [had already] pointed out",
# which is the refused releaser: the quoted indications that mention
# death carry that gate on the page.
#
# The Sun, Moon and Mercury are neither fortune nor infortune, and the
# types and transitions speak only of fortunes and infortunes: a
# distribution under one of them reads "no type by nature", a transition
# involving one "not among the twenty-four". Type 5 turns on conditions
# (a corrupting infortune in the bound, a weak fortune) that are not
# judged, so it is never assigned. Decided by the owner 2026-09-10, with
# the indications quoted. No worked example by the author; Figure 67 /
# fn 56 is Dykes' diagram of III.2, 33 (Mars distributing with Venus's
# sextile: type 3), and pins the classification.

def pn4_nature(planet):
    """Fortune, infortune, or None for the Sun, Moon and Mercury."""
    if planet in FORTUNES:
        return 'fortune'
    if planet in INFORTUNES:
        return 'infortune'
    return None

PN4_III2_TYPES = {
    1: ('a fortune, acting alone in the distribution', 'III.2, 11; 18-24'),
    2: ('an infortune, acting alone in the distribution', 'III.2, 12; 25-29'),
    3: ('an infortune distributing, a fortune partnering', 'III.2, 13; 30-35'),
    4: ('a fortune distributing, an infortune partnering', 'III.2, 14; 36-39'),
    5: ('one of the planets, fortune or infortune, under a corrupting infortune -- a condition, not assigned here', 'III.2, 15; 40-43'),
    6: ('both infortunes', 'III.2, 16; 44-48'),
    7: ('both fortunes', 'III.2, 17; 49-54'),
}

def pn4_static_type(distributor, partner):
    """III.2, 10-17: which of the seven the current distribution is, by
    nature alone. Returns (number or None, label, cite)."""
    d, p = pn4_nature(distributor), pn4_nature(partner) if partner else None
    if d is None or (partner and p is None):
        who = distributor if d is None else partner
        return (None, f"no type by nature: {who} is neither fortune nor infortune, and III.2's seven types "
                      f"speak only of fortunes and infortunes", 'III.2, 10-17')
    if not partner:
        n = 1 if d == 'fortune' else 2
    elif d == 'fortune' and p == 'fortune':
        n = 7
    elif d == 'infortune' and p == 'infortune':
        n = 6
    elif d == 'infortune':
        n = 3
    else:
        n = 4
    return (n, PN4_III2_TYPES[n][0], PN4_III2_TYPES[n][1])

# The twenty-four (III.2, 58-86): number -> (kind, from, to, context nature).
_F, _I = 'fortune', 'infortune'
PN4_III2_TRANSITIONS = {
    1: ('bound', _F, _F, None), 2: ('bound', _F, _I, None), 3: ('bound', _I, _F, None), 4: ('bound', _I, _I, None),
    5: ('management', _F, _F, None), 6: ('management', _F, _I, None), 7: ('management', _I, _F, None), 8: ('management', _I, _I, None),
    9: ('bound', _F, _F, _F), 10: ('bound', _F, _F, _I), 11: ('bound', _F, _I, _F), 12: ('bound', _F, _I, _I),
    13: ('bound', _I, _F, _F), 14: ('bound', _I, _F, _I), 15: ('bound', _I, _I, _F), 16: ('bound', _I, _I, _I),
    17: ('management', _F, _F, _F), 18: ('management', _F, _F, _I), 19: ('management', _F, _I, _F), 20: ('management', _F, _I, _I),
    21: ('management', _I, _F, _F), 22: ('management', _I, _F, _I), 23: ('management', _I, _I, _F), 24: ('management', _I, _I, _I),
}

# The twelve indications (III.2, 87-101), quoted. (from, to) -> paired;
# (from, to, context) -> doubled. `death` marks the ones III.2, 110-111
# gate on the longevity indicator's years.
PN4_III2_PAIRED = {
    (_F, _F): ('III.2, 88', 'the duration of good fortune, and the shift from good fortune to good fortune', False),
    (_I, _F): ('III.2, 89', 'a shift from the bottom and humbleness to being raised up and greatness', False),
    (_F, _I): ('III.2, 90', 'a shift from good to bad, and a fear of death', True),
    (_I, _I): ('III.2, 91', 'a fluctuation in tribulations, and a shift from adversity to adversity, and from evil to evil, '
                          'and that indication of the fear of death will be more confirmed', True),
}
PN4_III2_DOUBLED = {
    (_F, _F, _F): ('III.2, 92', 'good fortune and surpassing good', False),
    (_F, _F, _I): ('III.2, 94', 'a suitability of condition, and the lastingness of good fortune, because the fortunes in it are '
                                'greater in testimony -- except that it will blend it with evil and something detestable due to '
                                'the nature of the infortune', False),
    (_I, _F, _F): ('III.2, 95', 'a shift from something detestable and evil to surpassing good fortune', False),
    (_I, _F, _I): ('III.2, 96', 'a middling [condition] in good and evil, and excellence and badness, even though the '
                                'indication of good is stronger', False),
    (_F, _I, _F): ('III.2, 97', 'a middling condition in suitability and corruption, and good and evil, even though the '
                                'indication of evil is stronger', False),
    (_F, _I, _I): ('III.2, 98', 'something detestable and much evil, and the encountering of tribulations and the fear of '
                                'death, and fluctuations in detestable things', True),
    (_I, _I, _F): ('III.2, 99', 'excessive adversity and the fear of death', True),
    (_I, _I, _I): ('III.2, 100', 'varieties of detestable things, evil, and death', True),
}
PN4_III2_DEATH_GATE = (' [death only in the years the longevity indicator pointed out, III.2, 110-111 -- see the '
                       'house-master directed, Sahl On Nativities 1.23, 2, in The releaser chapter]')

def pn4_transition_numbers(kind, frm, to, context):
    """The transition numbers a shift answers to: the isolated one (1-8)
    and, when the context planet has a nature, the qualified one (9-24)."""
    out = [n for n, (k, f, t, c) in PN4_III2_TRANSITIONS.items() if k == kind and f == frm and t == to and c is None]
    if context is not None:
        out += [n for n, (k, f, t, c) in PN4_III2_TRANSITIONS.items() if k == kind and f == frm and t == to and c == context]
    return out

def pn4_classify_shift(prev_seg, next_seg):
    """III.2, 55-101 for one boundary between two segments of the natal
    distribution: zero, one or two shifts (bound and/or management),
    each numbered and given its quoted indication, or explained as not
    among the twenty-four."""
    out = []
    bound_shift = prev_seg['distributor'] != next_seg['distributor']
    mgmt_shift = prev_seg['partner'] != next_seg['partner']
    if bound_shift:
        frm, to = pn4_nature(prev_seg['distributor']), pn4_nature(next_seg['distributor'])
        ctx = pn4_nature(next_seg['partner']) if next_seg['partner'] else None
        label = f"the distribution shifts from the bound of {prev_seg['distributor']} to the bound of {next_seg['distributor']}"
        out.append(_pn4_shift_row('bound', label, frm, to, ctx, next_seg['partner']))
    if mgmt_shift:
        frm = pn4_nature(prev_seg['partner']) if prev_seg['partner'] else None
        to = pn4_nature(next_seg['partner']) if next_seg['partner'] else None
        ctx = pn4_nature(next_seg['distributor'])
        label = (f"the management shifts from {prev_seg['partner'] or 'the distributor alone'} to "
                 f"{next_seg['partner'] or 'the distributor alone'}")
        out.append(_pn4_shift_row('management', label, frm, to, ctx, next_seg['distributor']))
    if bound_shift and mgmt_shift and len(out) == 2 and all(r['numbers'] for r in out):
        natures = {pn4_nature(prev_seg['distributor']), pn4_nature(next_seg['distributor']),
                   pn4_nature(prev_seg['partner']), pn4_nature(next_seg['partner'])}
        if natures == {_F}:
            out[0]['indication'] += ' -- and both shifting from a fortune to a fortune: "good fortune upon good fortune, and of good upon good; and it is the most powerful good fortune, and the most splendid in power, if the four of them were fortunes" (III.2, 93)'
        elif natures == {_I}:
            out[0]['indication'] += ' -- and both shifting from an infortune to an infortune: "of the greatest and harshest adversity if the four of them were infortunes" (III.2, 101)' + PN4_III2_DEATH_GATE
    return out

def _pn4_shift_row(kind, label, frm, to, ctx, context_planet):
    if frm is None or to is None:
        return {'kind': kind, 'label': label, 'numbers': [], 'cite': 'III.2, 58-86',
                'indication': 'not among the twenty-four: one side of the shift is neither fortune nor infortune, or the distributor acts alone'}
    numbers = pn4_transition_numbers(kind, frm, to, ctx)
    paired_cite, paired_text, paired_death = PN4_III2_PAIRED[(frm, to)]
    if ctx is not None:
        d_cite, d_text, d_death = PN4_III2_DOUBLED[(frm, to, ctx)]
        indication = (f'"{d_text}" ({d_cite}; the paired reading at {paired_cite})'
                      + (PN4_III2_DEATH_GATE if d_death else ''))
    else:
        indication = (f'"{paired_text}" ({paired_cite}); the qualified transition needs a fortune or infortune '
                      f'{"managing" if kind == "bound" else "distributing"}, and {context_planet or "none"} is neither'
                      + (PN4_III2_DEATH_GATE if paired_death else ''))
    return {'kind': kind, 'label': label, 'numbers': numbers,
            'cite': 'III.2, ' + ('58-62' if kind == 'bound' and ctx is None else '63-67' if ctx is None
                                 else '68-76' if kind == 'bound' else '77-85'),
            'indication': indication}

def pn4_year_transitions(segments, age):
    """The shifts of the natal distribution that fall inside this year of
    it, [age, age + 1) in years of arc (III.2, 55: "within one of the
    years")."""
    rows = []
    if not segments:
        return rows
    for prev_seg, next_seg in zip(segments, segments[1:]):
        if age <= next_seg['from'] < age + 1:
            for r in pn4_classify_shift(prev_seg, next_seg):
                rows.append({'At age': f"{next_seg['from']:.2f}", 'Shift': r['label'],
                             'Transition': ', '.join(f"#{n}" for n in r['numbers']) or '-',
                             'Indication': r['indication'], 'Source': r['cite']})
    return rows

def _pn4_bound_span(deg):
    """The Egyptian bound a degree stands in: (start, end)."""
    starts = pn4_bound_starts()
    idx = max(i for i, (lon, _l, _s) in enumerate(starts) if lon <= deg % 360.0)
    return starts[idx][0], (starts[idx + 1][0] if idx + 1 < len(starts) else 360.0)

# --- III.2, 38, 43, 46-47, 54; III.8, 7: transits into the bound ----------
# The twenty-four and the seven types read the NATAL distribution (III.2,
# 105); "when there is a planet in that bound in one of the years, either
# by its body or casting a ray to it, then its indication is not in the
# manner we have described" (106). Six sentences do describe it, each
# keyed to a type:
#   38  a fortune distributing with no rooted partner (type 1), and "in
#       the revolution the body or rays of an infortune was in it": "good
#       fortune ... [and] incidental adversity and harm"; worse under 39's
#       conditions;
#   43  in the type-5 discussion (40-42: a corrupting infortune in the
#       bound, a weak fortune -- conditions, not judged here): "the body
#       of a fortune or its rays" in the bound in the revolution "will
#       not have the power to repel death, but his death will be with
#       reverence";
#   46  both infortunes (type 6) and "in the revolution one of the
#       fortunes cast its ray to it": "he will not be freed from death but
#       he will be revered in his illness";
#   47  the same with "the ray of an infortune in it": hardship, "a bad
#       death"; 48: at home if the indicators are in their own places;
#   54  both fortunes (type 7) and "the body of an infortune or its rays"
#       in the bound in the revolution: "good fortune but he will be
#       unhappy with it";
#   III.8, 7  the lord of the year and the distributor both infortunes,
#       in the revolution "both not in their own shares, but a fortune was
#       with each one of them": "a little good" -- a condition on the two
#       lords, shown as facts.
# The death sentences carry III.2, 110-111's gate. The Sun, Moon and
# Mercury entering the bound are addressed by no sentence, and 46-47
# speak of rays, not bodies; both are said in the row. Decided by the
# owner 2026-09-10; no worked example (fn 56's Figure 67 has the
# revolutionary Saturn in the bound, one instance of the fact).

PN4_BOUND_TRANSIT_SENTENCES = {
    38: ('III.2, 38-39', 'because of the distribution of the fortunes it indicates good fortune, and due to the rays of the '
                        'revolutionary infortune it indicates incidental adversity and harm', False),
    43: ('III.2, 43', 'it will not have the power to repel death, but his death will be with reverence', True),
    46: ('III.2, 46', 'he will not be freed from death but he will be revered in his illness and his conditions, until the '
                     'time in which he dies', True),
    47: ('III.2, 47', 'before death he will encounter hardship, and will be tortured, and it will be burdensome for whoever '
                     'is tending to him, and he will die a bad death', True),
    54: ('III.2, 54', 'he will have good fortune but he will be unhappy with it, and distresses and anxieties will affect '
                     'him, in accordance with the indication of the infortune', False),
}

def pn4_bound_transit_sentence(type_number, entrant_nature, by_ray):
    """Which of the five III.2 sentences fits a revolutionary body or ray
    in the bound, given the static type. Returns (key or None, note)."""
    if entrant_nature is None:
        return None, 'no sentence of III.2 speaks of the Sun, the Moon or Mercury entering the bound'
    if type_number == 1 and entrant_nature == 'infortune':
        return 38, ''
    if type_number == 7 and entrant_nature == 'infortune':
        return 54, ''
    # 43's premise is 40's: "in that bound in the root is a powerful,
    # corrupting infortune or its rays" -- which types 4, 5 and 6 have (an
    # infortune distributing or partnering) and types 2 and 3 do not. An
    # earlier version keyed 43 to 2, 3 and None (order PN4R-4m-1, 2026-09-11).
    under_40 = "under III.2, 40-42's conditions -- a corrupting infortune in the bound, a weak fortune -- which are not judged here"
    if type_number == 6:
        if by_ray:
            return (46 if entrant_nature == 'fortune' else 47), ''
        if entrant_nature == 'fortune':
            return 43, under_40
        return None, 'III.2, 46-47 speak of a ray cast into the bound, not a body in it'
    if entrant_nature == 'fortune' and type_number in (4, 5):
        return 43, under_40
    return None, 'no sentence of III.2 pairs this entrant with this type'

def pn4_bound_transits(chart_data, sr, current, year_lord):
    """The revolution's bodies and rays in the current bound, each keyed
    to its sentence and quoted; then III.8, 7's condition on the lord of
    the year and the distributor, as facts."""
    if not current:
        return []
    rev = sr['planetary_data']
    b_start, b_end = _pn4_bound_span(current['from_lon'])
    t_num, _label, _cite = pn4_static_type(current['distributor'], current['partner'])
    rows = []
    for lon, kind, who, aspect in sorted(pn4_bodies_and_rays(rev), key=lambda m: m[0]):
        if not (b_start <= lon < b_end):
            continue
        key, note = pn4_bound_transit_sentence(t_num, pn4_nature(who), kind == 'ray')
        if key:
            cite, text, death = PN4_BOUND_TRANSIT_SENTENCES[key]
            sentence = f'"{text}" ({cite})' + (f' -- {note}' if note else '') + (PN4_III2_DEATH_GATE if death else '')
        else:
            cite, sentence = 'III.2, 105-106', note
        rows.append({'In the bound, in the revolution': f"{who} by {aspect} at {get_degree_string(lon)}",
                     'Nature': pn4_nature(who) or 'neither',
                     'With the type': f"type {t_num}" if t_num else 'no type by nature',
                     'Sentence': sentence, 'Source': cite})
    # III.8, 7
    dist = current['distributor']
    both_infortunes = pn4_nature(year_lord) == 'infortune' and pn4_nature(dist) == 'infortune'

    def share_and_company(planet):
        row = rev.get(planet)
        if not row:
            return '-'
        r = get_essential_rulers(row['longitude'])
        in_share = planet in (r['domicile'], r['exaltation'], r['triplicity_day'], r['triplicity_night'], r['face'], r.get('term'))
        sign = get_zodiac_sign(row['longitude'])
        with_fortune = [p for p in FORTUNES if p in rev and get_zodiac_sign(rev[p]['longitude']) == sign]
        return (f"{planet} in {sign}: {'in its own share' if in_share else 'not in its own share'}; "
                f"{'a fortune with it: ' + ', '.join(with_fortune) if with_fortune else 'no fortune with it'}")
    if both_infortunes:
        facts = share_and_company(year_lord) + ('' if year_lord == dist else '; ' + share_and_company(dist))
        sentence = f'if both are not in their own shares and a fortune is with each: "they will indicate a little good" (III.8, 7); the facts: {facts}'
    else:
        sentence = (f"III.8, 7 needs the lord of the year and the distributor both infortunes; they are "
                    f"{year_lord} ({pn4_nature(year_lord) or 'neither'}) and {dist} ({pn4_nature(dist) or 'neither'})")
    rows.append({'In the bound, in the revolution': 'The lord of the year and the distributor, in the revolution',
                 'Nature': f"{pn4_nature(year_lord) or 'neither'} / {pn4_nature(dist) or 'neither'}",
                 'With the type': f"type {t_num}" if t_num else 'no type by nature',
                 'Sentence': sentence, 'Source': 'III.8, 7'})
    return rows

def pn4_distribution_checklist(chart_data, sr, year_lon, current):
    """III.2, 4-9 as facts for the bound the distribution stands in now.
    Nothing here is judged: the conditions 5 and 8 ask about are shown
    as what they are (direct or retrograde, the solar phase) and the
    reader judges."""
    if not current:
        return []
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    n_asc, r_asc = chart_data['ascendant'], sr['ascendant']
    deg = current['from_lon'] % 360.0
    b_start, b_end = _pn4_bound_span(deg)
    lord = current['distributor']
    sign = get_zodiac_sign(b_start)

    def condition(data, planet):
        row = data.get(planet)
        if not row:
            return '-'
        motion = 'retrograde' if row.get('speed_in_lon', 1.0) < 0 else 'direct'
        phase, side, _el = solar_phase(planet, row['longitude'], data['Sun']['longitude'], row.get('speed_in_lon'))
        return f"{get_zodiac_sign(row['longitude'])}, {motion}, {side or '-'}{', ' + phase.lower() if phase else ''}"

    def in_bound(items):
        return [(lon, who, aspect) for lon, kind, who, aspect in items if b_start <= lon < b_end]

    rulers = get_essential_rulers(b_start)
    face = get_essential_rulers(deg)['face']
    trip = rulers['triplicity_day'] if chart_data['sect'] == 'Diurnal' else rulers['triplicity_night']
    natal_meet = in_bound(pn4_bodies_and_rays(natal))
    rev_meet = in_bound(pn4_bodies_and_rays(rev))
    fmt = lambda items: '; '.join(f"{who} by {aspect} at {get_degree_string(lon)}" for lon, who, aspect in items) or 'none'
    return [
        {'Question': '[1a] Whose bound is it', 'Reads': f"{lord}'s, {get_degree_string(b_start)} to {get_degree_string(b_end)}",
         'Source': 'III.2, 5'},
        {'Question': "[1b] Its lord's condition in the root and the revolution (not judged: the facts)",
         'Reads': f"root: {condition(natal, lord)}; revolution: {condition(rev, lord)}", 'Source': 'III.2, 5'},
        {'Question': '[2] Where the bound falls from the natal Ascendant / the terminal sign / the revolution Ascendant',
         'Reads': f"house {get_wsh_house(b_start, n_asc)} / {get_wsh_house(b_start, year_lon)} / {get_wsh_house(b_start, r_asc)}",
         'Source': 'III.2, 6'},
        {'Question': "[3] The sign's house, exaltation, triplicity and face",
         'Reads': f"{sign}: house of {rulers['domicile']}, exaltation of {rulers['exaltation'] if rulers['exaltation'] not in (None, '-', '') else 'none'}, triplicity of "
                  f"{trip} ({'day' if chart_data['sect'] == 'Diurnal' else 'night'}), face of {face} at {get_degree_string(deg)}",
         'Source': 'III.2, 7'},
        {'Question': '[4] Who is in that sign in the root; in the revolution',
         'Reads': f"root: {_pn4_natal_planets_in_sign(natal, sign)}; revolution: {_pn4_natal_planets_in_sign(rev, sign)}",
         'Source': 'III.2, 8'},
        {'Question': '[5] Who casts rays to the bound, and who is in it -- root',
         'Reads': fmt(natal_meet), 'Source': 'III.2, 9'},
        {'Question': '[5] The same in the revolution (a different matter from the twelve, III.2, 105-106)',
         'Reads': fmt(rev_meet), 'Source': 'III.2, 9; 43, 46-47, 54'},
    ]

# --- II.13, 1; II.14, 1; II.22, 1-5: the luminary proxies -----------------
# "If the Sun was the lord of the year, then the majority of that judgment
# in that year should be in accordance with the condition of [1] the lord
# of the sign in which the distribution of the lifespan from the
# [longevity] releaser was ..., and partnering with it in the indication
# is [2] the planet which is in Leo in the root of the nativity or in the
# revolution, and [3] the planet to which the Sun hands over the
# management (so long as it is in its sign), and then along with that you
# see [4] where the Sun is, calling upon [that] as a witness" (II.13, 1);
# II.14, 1 adds "the condition of the distributor"; II.22, 1-5 for the
# Moon: the distributor, the lord of the sign of the releaser's
# distribution, the planet in Cancer, the planet she connects with in her
# sign, her house lord if empty in course, and her own conditions.
#
# PARTIAL, on purpose: the first proxy in every version -- the sign the
# longevity releaser's distribution stands in, and its lord -- needs the
# releaser PN IV does not supply (IX.8, 123); since 2026-09-10 it is
# filled from the releaser's distribution (Sahl, On Nativities 1.15, 22)
# when one is found, else unavailable. The Sun's hand-over is read per fn 239 as
# the Sun's own connections in his sign, in the REVOLUTION (fn 239 notes
# the book does not say root or revolution), with "hands over" as the Sun
# being the applying body; "where the Sun is" is his sign and its lord
# per fn 241. Shown only in a year whose lord is the Sun or the Moon.
# The delineations (II.13, 2 - II.21; II.22, 5-24) are not built. No
# worked example exists; fn 238 illustrates the missing part.
# Decided by the owner 2026-09-10.
PN4_PROXY_RELEASER = ("unavailable: the sign the longevity releaser's distribution stands in needs the releaser's "
                      "distribution, which was not supplied (PN IV does not choose the releaser, IX.8, 123; the "
                      "engine takes it from Sahl, On Nativities 1.15, when that finds one)")

def pn4_luminary_proxies(year_lord, chart_data, sr, moon=None, sun=None, releaser=None):
    """The proxies for a year whose lord is the Sun or the Moon, or None
    for any other lord. Rows of {Proxy, Reads, Source}. `releaser`, when
    given, is {'distributor', 'sign', 'lord', 'note'} from the releaser's
    distribution (Sahl, On Nativities 1.15, 22), and fills the first
    proxy of each version; its 'note' explains an absence."""
    if year_lord not in ('Sun', 'Moon'):
        return None
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    r_dist = (releaser or {}).get('distributor')
    r_sign = (releaser or {}).get('sign')
    r_note = f"unavailable: {releaser['note']}" if releaser and releaser.get('note') else PN4_PROXY_RELEASER
    r_dist_text = f"{r_dist} (the releaser's distributor; Sahl, On Nativities 1.18, 20)" if r_dist else r_note
    r_sign_text = (f"{r_sign}, lord {(releaser or {}).get('lord', '-')} (the releaser's distribution stands there)"
                   if r_sign else r_note)

    def in_sign(data, sign):
        found = [p for p in PN4_SEVEN if p in data and p != year_lord and get_zodiac_sign(data[p]['longitude']) == sign]
        return ', '.join(found) or 'none'

    def handover(lum):
        if lum is None:
            return 'not computed'
        if lum['void']:
            return (f"none: leaves {lum['sign']} on day {lum['exit_day']:.2f} without a connection"
                    + (f"; the lord of the house, {lum['house_lord']}, stands in (II.22, 4)" if year_lord == 'Moon' else ''))
        return '; '.join(f"{c['planet']} by {c['aspect']} on day {c['day']:.2f}" for c in lum['connections'])

    rows = []
    if year_lord == 'Sun':
        rows.append({'Proxy': '[II.14] The distributor (probably of the longevity releaser, fn 249)',
                     'Reads': r_dist_text, 'Source': 'II.14, 1'})
        rows.append({'Proxy': "[1] The lord of the sign in which the distribution of the lifespan from the releaser is",
                     'Reads': r_sign_text, 'Source': 'II.13, 1; fn 238'})
        rows.append({'Proxy': '[2] The planet in Leo in the root; in the revolution',
                     'Reads': f"root: {in_sign(natal, 'Leo')}; revolution: {in_sign(rev, 'Leo')}", 'Source': 'II.13, 1'})
        rows.append({'Proxy': '[3] The planet to which the Sun hands over the management, so long as he is in his sign',
                     'Reads': handover(sun) + ' -- the revolution\'s Sun, applying (fn 239)', 'Source': 'II.13, 1; fn 239'})
        sun_lon = rev['Sun']['longitude']
        rows.append({'Proxy': '[4] Where the Sun is, as a witness',
                     'Reads': f"{get_zodiac_sign(sun_lon)} ({get_degree_string(sun_lon)}), lord "
                              f"{SIGN_TO_DOMICILE.get(get_zodiac_sign(sun_lon), '-')} (fn 241)", 'Source': 'II.13, 1; fn 241'})
    else:
        rows.append({'Proxy': '[1] The distributor (of the longevity releaser, fn 308)',
                     'Reads': r_dist_text, 'Source': 'II.22, 1; fn 308'})
        rows.append({'Proxy': "[2] The lord of the sign in which the distribution from the releaser is",
                     'Reads': r_sign_text, 'Source': 'II.22, 1; fn 309'})
        rows.append({'Proxy': '[3] The planet in Cancer in the root; in the revolution',
                     'Reads': f"root: {in_sign(natal, 'Cancer')}; revolution: {in_sign(rev, 'Cancer')}", 'Source': 'II.22, 1'})
        rows.append({'Proxy': '[4] The planet the Moon connects with, so long as she is in her sign',
                     'Reads': handover(moon), 'Source': 'II.22, 1-2'})
        rows.append({'Proxy': '[5] If she is empty in course, the lord of her house',
                     'Reads': (f"she is empty in course: {moon['house_lord']}" if moon and moon['void']
                               else 'not empty in course' if moon else 'not computed'), 'Source': 'II.22, 4'})
        m = rev['Moon']
        elong = (m['longitude'] - rev['Sun']['longitude']) % 360.0
        rows.append({'Proxy': "[6] Her conditions (facts; the judgment of II.22, 6-10 is not built)",
                     'Reads': (f"{'northern' if m.get('latitude', 0.0) >= 0 else 'southern'} in latitude "
                               f"({m.get('latitude', 0.0):+.2f}); {'increasing' if elong < 180.0 else 'decreasing'} in glow "
                               f"({elong:.1f} from the Sun); {m.get('speed_in_lon', 0.0):.2f} a day"),
                     'Source': 'II.22, 5-10'})
    return rows

# --- II.3, 2-19: the sign of the terminal point and its lord, examined ----
# II.3, 2: the sign of the terminal point in the ROOT -- which house of
# the circle ("the stakes or what follows them, or those falling from
# them"), whose house, exaltation and triplicity, which planets, Lots and
# twelfth-parts are in it, who looks at it or casts rays at it and from
# which sign and degree, to what bound, face and degree the rays fall,
# and whether it is devoid of them. II.3, 3: the same in the REVOLUTION,
# with where those planets were in the root and are now, and their
# condition in each. II.3, 5-8: the lord of the year's condition in root
# and revolution compared four ways (Figure 55), and 5-6 say what
# "suitable" is: direct, in its own domain (sect, fn 46), in its own
# glow, in a sign in which it has a claim, safe from the infortunes, in
# an excellent place from the three signs; the contrary: retrograde,
# burned or under the rays, exile, westernized from the Sun (fn 47),
# assembled with or inspected by the infortunes, out of sect. II.3, 9-18
# refine by reception, by a stake of the revolution's Ascendant under a
# non-receiving infortune's square or opposition, and by aversion to the
# Ascendant (the second, sixth, eighth and twelfth).
#
# FACTS, NOT A VERDICT. The book gives the factors and no rule for
# weighing them, so every factor is shown for each chart and Figure 55's
# four sentences are quoted with the cell left to the reader (owner's
# decision 2026-09-10). The engine's own evaluators supply the facts --
# essential and accidental dignity, solar phase, reception -- run on the
# revolution's data as they run on the root's. Not read: twelfth-parts;
# fn 37-41's classes of sign (helpful, hostile, matching in ascensions)
# and of degree (bright, dark, smoky). The delineations II.4-II.21 are
# not built. No worked example exists; Figure 55 is Dykes' table.

PN4_II3_FIGURE_55 = (
    ('suitable in the root, suitable in the revolution', 'II.3, 5',
     'the safety of the body for the owner of the revolution of the year, and the goodness of his soul, and his '
     'delighting in the things which the lord of the year indicates'),
    ('suitable in the root, contrary in the revolution', 'II.3, 6',
     'weakness in that year, and a decrease in everything we stated'),
    ('bad in the root, excellent in the revolution', 'II.3, 7',
     'his condition will improve somewhat in that year, and it will revive things for him in it, which he will delight in'),
    ('bad in both the root and the revolution', 'II.3, 8',
     'an excess of adversity in the category of what it indicates'),
)

def _pn4_house_class(house):
    """II.3, 2 [1]: "the stakes or what follows them, or those falling from
    them"."""
    return 'a stake' if house in (1, 4, 7, 10) else 'following a stake' if house in (2, 5, 8, 11) else 'falling from a stake'

def _pn4_tag(planet):
    n = pn4_nature(planet)
    return f"{planet} ({n or 'neither'})"

def _pn4_looks_at_sign(data, sign, exclude=()):
    """Whole-sign aspects to a sign from the planets of a chart: (planet,
    aspect name, the planet's longitude, the degree its ray reaches in the
    sign). A planet IN the sign is reported as 'in it'."""
    out = []
    target_idx = SIGN_ORDER.index(sign)
    for planet in PN4_SEVEN:
        if planet in exclude or planet not in data:
            continue
        lon = data[planet]['longitude'] % 360.0
        apart = (target_idx - int(lon // 30)) % 12
        apart = min(apart, 12 - apart)
        entry = ASPECT_BY_SIGN_COUNT.get(apart)
        if entry is None:
            continue
        name = 'in it' if apart == 0 else entry[0].lower()
        ray_deg = target_idx * 30.0 + (lon % 30.0)
        out.append((planet, name, lon, ray_deg))
    return out

def _pn4_lots_in_sign(chart, sign):
    names = []
    for d in LOT_DEFINITIONS:
        lon = lot_by_id(d['id'], chart['planetary_data'], chart['ascendant'], chart['houses'], chart['sect'])
        if lon is not None and get_zodiac_sign(lon) == sign:
            names.append(d['name'])
    return names

def pn4_ii3_examination(chart_data, sr, year, jd_sr):
    """II.3, 2-19 as facts. Returns {root_rows, revolution_rows, lord_rows,
    refinement_rows, figure_55}."""
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    n_asc, r_asc = chart_data['ascendant'], sr['ascendant']
    sign, year_lon, lord = year['sign'], year['longitude'], year['lord']
    rulers = get_essential_rulers(year_lon)
    trip = rulers['triplicity_day'] if chart_data['sect'] == 'Diurnal' else rulers['triplicity_night']

    # --- II.3, 2: the root ---
    h = get_wsh_house(year_lon, n_asc)
    looks = _pn4_looks_at_sign(natal, sign)
    rays = [(p, a, lon, deg) for p, a, lon, deg in looks if a != 'in it']
    root_rows = [
        {'Question': '[1] Which house of the circle it is', 'Reads': f"house {h} from the natal Ascendant, {_pn4_house_class(h)}",
         'Source': 'II.3, 2; VI.3'},
        {'Question': '[2] Whose house, exaltation and triplicity',
         'Reads': f"house of {_pn4_tag(rulers['domicile'])}; exaltation of "
                  f"{_pn4_tag(rulers['exaltation']) if rulers['exaltation'] not in (None, '-', '') else 'none'}; triplicity of "
                  f"{_pn4_tag(trip)} ({'day' if chart_data['sect'] == 'Diurnal' else 'night'})",
         'Source': 'II.3, 2'},
        {'Question': '[3] Which planets, Lots and twelfth-parts are in it in the root',
         'Reads': f"planets: {_pn4_natal_planets_in_sign(natal, sign)}; Lots: "
                  f"{', '.join(_pn4_lots_in_sign(chart_data, sign)) or 'none'}; twelfth-parts not computed",
         'Source': 'II.3, 2; VI.4'},
        {'Question': '[4-7] Who looks at it or casts rays at it, from which sign and degree, and to what bound and face',
         'Reads': ('; '.join(f"{_pn4_tag(p)} by {a} from {get_degree_string(lon)}, the ray at {get_degree_string(deg)} "
                             f"(bound of {pn4_bound_lord(deg)}, face of {get_essential_rulers(deg)['face']})"
                             for p, a, lon, deg in rays) or 'none'),
         'Source': 'II.3, 2; fn 37-41 (the classes of sign and degree are not read)'},
        {'Question': '[8] Whether it falls away from the view of the planets and their rays',
         'Reads': 'yes: devoid of them' if not looks else 'no', 'Source': 'II.3, 2'},
    ]

    # --- II.3, 3: the revolution ---
    r_looks = _pn4_looks_at_sign(rev, sign)
    r_in = [p for p, a, _l, _d in r_looks if a == 'in it']
    r_rays = [(p, a, lon, deg) for p, a, lon, deg in r_looks if a != 'in it']
    ess_n, ess_r = evaluate_essential_dignities(natal, chart_data['sect']), evaluate_essential_dignities(rev, sr['sect'])
    acc_n = evaluate_accidental_dignities(natal, chart_data['houses'], chart_data['sect'], chart_data.get('julian_day'),
                                          armc=chart_data.get('armc'), obliquity=chart_data.get('obliquity'), geo_lat=chart_data.get('geo_lat'))
    acc_r = evaluate_accidental_dignities(rev, sr['houses'], sr['sect'], jd_sr,
                                          armc=sr.get('armc'), obliquity=sr.get('obliquity'), geo_lat=sr.get('geo_lat'))

    def labels(planet, ess, acc):
        return ', '.join((ess.get(planet, {}).get('Essential Labels') or []) + (acc.get(planet, {}).get('Accidental Labels') or [])) or 'none'

    involved = [p for p, _a, _l, _d in r_looks]
    revolution_rows = [
        {'Question': '[1] Which revolution planets are in it (twelfth-parts not computed)',
         'Reads': ', '.join(_pn4_tag(p) for p in r_in) or 'none', 'Source': 'II.3, 3; VI.3'},
        {'Question': '[2, 4, 5] Who looks at it, and from what direction',
         'Reads': '; '.join(f"{_pn4_tag(p)} by {a} from {get_degree_string(lon)}" for p, a, lon, _d in r_rays) or 'none',
         'Source': 'II.3, 3'},
        {'Question': '[3] Whether it is devoid of their alighting in or looking at it',
         'Reads': 'yes: devoid' if not r_looks else 'no', 'Source': 'II.3, 3'},
        {'Question': '[6] Where those planets were in the root, and where they are in the revolution',
         'Reads': '; '.join(f"{p}: house {get_wsh_house(natal[p]['longitude'], n_asc)} -> {get_wsh_house(rev[p]['longitude'], n_asc)} "
                            f"from the natal Ascendant" for p in involved if p in natal) or 'none',
         'Source': 'II.3, 3; VI.5'},
        {'Question': '[7] Their condition in the root; in the revolution (the engine\'s labels, not a verdict)',
         'Reads': '; '.join(f"{p}: root {labels(p, ess_n, acc_n)} | revolution {labels(p, ess_r, acc_r)}" for p in involved) or 'none',
         'Source': 'II.3, 3-4; I.7'},
    ]

    # --- II.3, 5-6: the lord of the year's factors, per chart ---
    def factors(data, chart, ess, acc, asc_for_place):
        row = data.get(lord)
        if not row:
            return {}
        e, a = ess.get(lord, {}), acc.get(lord, {})
        phase, side, _el = solar_phase(lord, row['longitude'], data['Sun']['longitude'], row.get('speed_in_lon'))
        claim = [k for k in ('Domicile', 'Exalt', 'Triplicity', 'Term', 'Face') if e.get(k)]
        infortunes = [f"{p} by {asp}" for p, asp, _l, _d in _pn4_looks_at_sign(data, get_zodiac_sign(row['longitude']))
                      if p in INFORTUNES and p != lord]
        return {
            'motion': 'retrograde' if row.get('speed_in_lon', 1.0) < 0 else 'direct',
            'glow': (phase.lower() if phase else 'in its own glow') + (f", {side}" if side else ''),
            'domain': 'in its own domain (hayz)' if a.get('Hayz') else 'contrary to its domain' if a.get('ContraryDomain') else 'neither in nor contrary to its domain',
            'claim': ('a claim: ' + ', '.join(claim).lower()) if claim else ('exile (detriment)' if e.get('Detriment') else 'fall' if e.get('Fall') else 'peregrine'),
            'infortunes': ', '.join(infortunes) or 'none by whole sign',
            'place': f"house {get_wsh_house(row['longitude'], n_asc)} / {get_wsh_house(row['longitude'], year_lon)} / {get_wsh_house(row['longitude'], r_asc)}",
        }
    f_n, f_r = factors(natal, chart_data, ess_n, acc_n, n_asc), factors(rev, sr, ess_r, acc_r, r_asc)
    lord_rows = [
        {'Factor': label, 'Root': f_n.get(key, '-'), 'Revolution': f_r.get(key, '-'), 'Source': cite}
        for key, label, cite in (
            ('motion', 'Direct in course, or retrograde', 'II.3, 5-6'),
            ('glow', 'In its own glow, or burned / under the rays; eastern or western', 'II.3, 5-6; fn 47'),
            ('domain', 'In its own domain (sect), or the contrary', 'II.3, 5-6; fn 46, 48'),
            ('claim', 'In a sign in which it has a claim, or exile', 'II.3, 5-6'),
            ('infortunes', 'The infortunes assembled with it or inspecting it (whole sign)', 'II.3, 5-6'),
            ('place', 'Its place from the natal Ascendant / the terminal sign / the revolution Ascendant', 'II.3, 5'),
        )
    ]

    # --- II.3, 9-18: the refinements, as facts ---
    def received(data, sect):
        try:
            rows = evaluate_reception(data, sect)
        except Exception:
            return 'not computed'
        by = [r['Receiver'] for r in rows if r.get('Received') == lord or (r.get('Received') == 'each other' and lord in str(r.get('Receiver')))]
        return ('received by ' + ', '.join(sorted(set(by)))) if by else 'not received'

    r_lord = rev.get(lord)
    ref_rows = []
    ref_rows.append({'Refinement': 'Received, or not (root; revolution)',
                     'Reads': f"root: {received(natal, chart_data['sect'])}; revolution: {received(rev, sr['sect'])}",
                     'Source': 'II.3, 9-12 (under the Configurations page\'s reception rule)'})
    if r_lord:
        rh_rasc = get_wsh_house(r_lord['longitude'], r_asc)
        rh_nasc = get_wsh_house(r_lord['longitude'], n_asc)
        harming = [f"{p} by {asp}" for p, asp, _l, _d in _pn4_looks_at_sign(rev, get_zodiac_sign(r_lord['longitude']))
                   if p in INFORTUNES and p != lord and asp in ('square', 'opposition')]
        ref_rows.append({'Refinement': "In a stake of the revolution's Ascendant, and squared or opposed by an infortune",
                         'Reads': f"house {rh_rasc} from the revolution Ascendant ({_pn4_house_class(rh_rasc)}); "
                                  f"infortunes by square or opposition: {', '.join(harming) or 'none'}; whether the infortune "
                                  f"receives it is read from the row above",
                         'Source': 'II.3, 13-15'})
        ref_rows.append({'Refinement': 'Looking at the Ascendant, or in the four positions that do not (2, 6, 8, 12)',
                         'Reads': f"house {rh_nasc} from the natal Ascendant: "
                                  + ('does NOT look at the Ascendant -- the detestable thing hidden (II.3, 17)' if rh_nasc in (2, 6, 8, 12)
                                     else 'looks at the Ascendant' + (' from a stake' if rh_nasc in (1, 4, 7, 10) else ', not from a stake (II.3, 16)')),
                         'Source': 'II.3, 16-18'})
    figure_55 = [{'Lord of the year': case, 'Indicates': f'"{text}"', 'Source': cite} for case, cite, text in PN4_II3_FIGURE_55]
    return {'root_rows': root_rows, 'revolution_rows': revolution_rows, 'lord_rows': lord_rows,
            'refinement_rows': ref_rows, 'figure_55': figure_55}

# --- I.6, 1-11: the image of the revolution of the year, as an inventory ---
# "write down the planets of the revolution of the year, with their
# conditions ..., and their rays and twelfth-parts, and the twelfth-parts
# of the degrees of the houses" (I.6, 3); "the planets of the root of the
# nativity, with their conditions and rays and twelfth-parts, and the
# twelfth-parts of the signs, and the Lots and Head and Tail" (4); "the
# Ascendant of the root, and the position of the terminal point of the
# year" (5); "the endpoint of the distribution, the distributor and the
# one partnering with it in the management, and the lord of the fardar,
# and the one dividing [its fardar] with it, and the lord of the orb, each
# of them in their signs and bounds" (6); a fixed star on the natal
# Ascendant, Midheaven, a luminary or an angular planet (7). The count
# (8, Figure 52): 14 planets, 98 rays, the Head and Tail twice each, 38
# twelfth-parts (24 of the houses, 14 of the planets) -- 154 -- "and the
# Lots according to how you do it". Within a house, by degree (9-10).
#
# A TABLE, NOT THE WHEEL of I.6, 1: every point by whole-sign house from
# the revolution's Ascendant (fn 33: Dykes drew it that way for clarity;
# I.6, 2's quadrant cusps are listed as points of their own), ordered by
# degree within the house. The twelfth-part construction -- 2.5 degrees
# to a sign, beginning with the sign itself -- is Gr. Intr. V.18, 1-3's
# (Figure 57), as _twelfth_part_sign says. The fixed stars of I.6, 7 are
# not computed. The Lots are the
# engine's, "many or few" (I.6, 8). Decided by the owner 2026-09-10.

def pn4_twelfth_part(lon):
    """The twelfth-part of a degree, as a longitude: each 2.5 degrees of a
    sign maps to one whole sign in order, beginning with the sign itself,
    and the position inside the 2.5 is spread over that sign's 30.
    Gr. Intr. V.18, 3's own calculation (the degree and minute from the
    sign's beginning times 12, cast out from that sign's beginning); the
    sign agrees with _twelfth_part_sign."""
    lon %= 360.0
    sign_idx, within = int(lon // 30), lon % 30.0
    step = int(within // 2.5)
    return (((sign_idx + step) % 12) * 30.0 + (within - step * 2.5) * 12.0) % 360.0

def pn4_revolution_image(chart_data, sr, year, age, current, fardar, orb, lat, elapsed=None):
    """I.6, 3-8: every point of the image, as rows, and the count. `elapsed`
    is the elapsed years the distribution's endpoint is read at (I.6, 6);
    the integer `age` when not given."""
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    r_asc = sr['ascendant']
    rows = []

    def add(chart, kind, point, lon, cite):
        lon %= 360.0
        # I.6, 2: the image's houses are "calculat[ed] ... by their degrees
        # and minutes, in the way that you calculate the houses by the
        # portions of hours and the ascensions of the right circle" -- the
        # revolution's cusps (the Alcabitius set this engine computes), not
        # whole signs; fn 33's whole-sign Figure 51 was Dykes's simplification
        # "for clarity". Filed by whole sign until 2026-09-11 (order PN4R-4n-5).
        rows.append({'lon': lon, 'House': get_house_number(lon, sr['houses']), 'Chart': chart, 'Kind': kind, 'Point': point,
                     'Position': get_degree_string(lon), 'Bound': pn4_bound_lord(lon), 'Source': cite})

    counts = {'planets': 0, 'rays': 0, 'nodes': 0, 'twelfth-parts of houses': 0, 'twelfth-parts of planets': 0, 'Lots': 0}
    for label, chart, cite in (('revolution', sr, 'I.6, 3'), ('root', chart_data, 'I.6, 4')):
        data = chart['planetary_data']
        for lon, kind, who, aspect in pn4_bodies_and_rays(data):
            if kind == 'body':
                row = data[who]
                cond = ('retrograde' if row.get('speed_in_lon', 1.0) < 0 else 'direct')
                add(label, 'planet', f"{who} ({cond})", lon, cite)
                counts['planets'] += 1
                add(label, 'twelfth-part of a planet', f"twelfth-part of {who}", pn4_twelfth_part(lon), cite)
                counts['twelfth-parts of planets'] += 1
            else:
                add(label, 'ray', f"{who} by {aspect}", lon, cite)
                counts['rays'] += 1
        node = data.get('North Node')
        if node:
            add(label, 'node', 'Head', node['longitude'], cite)
            add(label, 'node', 'Tail', node['longitude'] + 180.0, cite)
            counts['nodes'] += 2
        for i, cusp in enumerate(list(chart['houses'])[:12]):
            add(label, 'twelfth-part of a house', f"twelfth-part of the degree of house {i + 1} ({get_degree_string(cusp)})",
                pn4_twelfth_part(cusp), cite + ' (fn 31: the quadrant cusps)')
            counts['twelfth-parts of houses'] += 1
        for d in LOT_DEFINITIONS:
            lon = lot_by_id(d['id'], data, chart['ascendant'], chart['houses'], chart['sect'])
            if lon is not None:
                add(label, 'Lot', d['name'], lon, 'I.6, 4; 8: "according to how you do it"')
                counts['Lots'] += 1
    add('root', 'point', 'Ascendant of the root', chart_data['ascendant'], 'I.6, 5')
    add('root', 'point', 'Terminal point of the year', year['longitude'], 'I.6, 5')
    if current:
        endpoint = _pn4_seg_degree({'from': float(age if elapsed is None else elapsed)}, chart_data['ascendant'], chart_data, lat)
        add('root', 'time lord', 'Endpoint of the distribution (the degree reached now)', endpoint, 'I.6, 6; fn 34')
        for name, planet in (('the distributor', current['distributor']), ('the partner in the management', current['partner'])):
            if planet and planet in natal:
                add('root', 'time lord', f"{planet}, {name}", natal[planet]['longitude'], 'I.6, 6')
    if fardar:
        for name, planet in (('lord of the fardar', fardar.get('lord')), ('dividing the fardar with it', fardar.get('sub_lord'))):
            if planet and planet in natal:
                add('root', 'time lord', f"{planet}, {name}", natal[planet]['longitude'], 'I.6, 6')
    if orb and orb in natal:
        add('root', 'time lord', f"{orb}, lord of the orb", natal[orb]['longitude'], 'I.6, 6')
    # by degree within the house, counted FROM ITS CUSP: a quadrant house
    # can straddle 0 Aries, where raw longitude would put its last degrees first.
    rows.sort(key=lambda r: (r['House'], (r['lon'] - sr['houses'][r['House'] - 1]) % 360.0))
    for r in rows:
        del r['lon']
    counts['total of I.6, 8'] = counts['planets'] + counts['rays'] + counts['nodes'] + counts['twelfth-parts of houses'] + counts['twelfth-parts of planets']
    return rows, counts

# --- I.7, 1-26: the reading checklist -------------------------------------
# "If you made the image of the revolution of the year, then understand:"
# (I.7, 1) -- twenty-six things. 2-6 concern the revolution's Ascendant:
# its house in the root, who is in it and looks at it in both times, who
# has a claim on it and where they stand (in a share or in exile), and
# whether its lord has one house or two and looks at them. 7-24 run over
# all the planets (fn 39): direct or retrograde (7); strong or weak (8);
# "rising and falling" (9); aversion (10); assembly and whole-sign aspect
# (11, fn 41); rays by degree (12, fn 42); connection and separation
# (13); reception (14); supporting or corrupting (15); hostile or
# friendly, harmonizing or contrary (16); domain (17); their
# twelfth-parts (18); returns to their rooted positions (19, fn 44);
# their course in the signs (20); their transits of the natal,
# revolution and monthly planets (21); the Lots of the year (22, fn 45);
# the stakes (23); the solar phase (24). 25-26: "its indication will be
# according to its place and condition in the two times together".
#
# FACTS, and six things named as not read. The facts (2-7, 10-14,
# 17-19, 22-24) come from the engine's evaluators run on each chart --
# the pairwise configurations and the connection rule the Configurations
# page uses, reception under its rule, accidental dignity's domain, the
# solar phase, the twelfth-part, the transit grade of V.1. NOT read: 8
# "strong or weak", 15 "supporting or corrupting", 16 "hostile or
# friendly" -- judgments the page does not make; 9 "rising and falling",
# which fn 32 could not settle; 20-21, the year's course and transits,
# which the engine does not track. 25-26 is the principle II.3's section
# already applies. Decided by the owner 2026-09-10; no worked example.

PN4_I7_NOT_READ = (
    ('8', 'the strong ones, and the weak', 'a judgment the page does not make'),
    ('9', 'those rising and falling in their direction', 'fn 32 could not settle what this means'),
    ('15', 'those supporting their associate or corrupting them', 'a judgment the page does not make'),
    ('16', 'those hostile to them and friendly towards them, and those harmonizing with others or being contrary to them', 'a judgment the page does not make'),
    ('20', 'their course in the twelve signs', "the year's transits are not tracked"),
    ('21', 'their transiting the planets of the root, the revolution, and the revolution of the months', "the year's transits are not tracked"),
)

def _pn4_share_or_exile(planet, lon):
    """I.7, 5: "in a position in which it has a share, or in the contrary
    of that (being in exile)"."""
    r = get_essential_rulers(lon)
    if planet in (r['domicile'], r['exaltation'], r['triplicity_day'], r['triplicity_night'], r.get('term'), r['face']):
        shares = [k for k, v in (('house', r['domicile']), ('exaltation', r['exaltation']), ('triplicity', r['triplicity_day']),
                                 ('triplicity', r['triplicity_night']), ('bound', r.get('term')), ('face', r['face'])) if v == planet]
        return 'a share: ' + ', '.join(dict.fromkeys(shares))
    sign = get_zodiac_sign(lon)
    if sign in DOMICILES.get(planet, []) or sign in EXALTATIONS.get(planet, []):
        return 'a share'
    opposite = get_zodiac_sign(lon + 180.0)
    if opposite in DOMICILES.get(planet, []):
        return 'exile (detriment)'
    return 'no share (peregrine)'

def pn4_i7_ascendant(chart_data, sr):
    """I.7, 2-6 for the revolution's Ascendant, as facts."""
    natal, rev = chart_data['planetary_data'], sr['planetary_data']
    n_asc, r_asc = chart_data['ascendant'], sr['ascendant']
    sign = get_zodiac_sign(r_asc)
    h = get_wsh_house(r_asc, n_asc)

    def contents(chart, data):
        planets = _pn4_natal_planets_in_sign(data, sign)
        lots = _pn4_lots_in_sign(chart, sign)
        twelfths = [p for p in PN4_SEVEN if p in data and get_zodiac_sign(pn4_twelfth_part(data[p]['longitude'])) == sign]
        return (f"planets: {planets}; Lots: {', '.join(lots) or 'none'}; twelfth-parts of planets falling in it: "
                f"{', '.join(twelfths) or 'none'}")

    def looking(data):
        return ', '.join(f"{p} by {a}" for p, a, _l, _d in _pn4_looks_at_sign(data, sign) if a != 'in it') or 'none'

    r = get_essential_rulers(r_asc)
    trip = r['triplicity_day'] if sr['sect'] == 'Diurnal' else r['triplicity_night']
    claimants = []
    for kind, lord in (('house', r['domicile']), ('exaltation', r['exaltation']), ('triplicity', trip), ('bound', r.get('term')), ('face', r['face'])):
        if lord in (None, '-', '') or lord not in rev:
            continue
        lon = rev[lord]['longitude']
        claimants.append(f"{lord} ({kind}): house {get_wsh_house(lon, r_asc)} from it, in {get_zodiac_sign(lon)}, {_pn4_share_or_exile(lord, lon)}")
    lord = r['domicile']
    houses = DOMICILES.get(lord, [])
    lord_lon = rev.get(lord, {}).get('longitude')
    parts = []
    if lord_lon is not None:
        lord_idx = int(lord_lon // 30)
        for hs in houses:
            idx = SIGN_ORDER.index(hs)
            apart = min((idx - lord_idx) % 12, (lord_idx - idx) % 12)
            entry = ASPECT_BY_SIGN_COUNT.get(apart)
            rel = 'in it' if apart == 0 else (f"looks at it by {entry[0].lower()}" if entry else 'does not look at it (aversion)')
            parts.append(f"{hs} (house {get_wsh_house(idx * 30.0 + 15.0, r_asc)} from the Ascendant): {lord} {rel}; "
                         f"{lord} is house {get_wsh_house(lord_lon, idx * 30.0)} from {hs}")
    return [
        {'I.7': '2', 'Question': "The revolution's Ascendant: which house it is in the root",
         'Reads': f"{sign} ({get_degree_string(r_asc)}) is house {h} from the natal Ascendant, {_pn4_house_class(h)} (fn 37)",
         'Source': 'I.7, 2'},
        {'I.7': '3', 'Question': 'Who was in it in the root; in the revolution',
         'Reads': f"root -- {contents(chart_data, natal)}; revolution -- {contents(sr, rev)}", 'Source': 'I.7, 3'},
        {'I.7': '4', 'Question': 'Who looks at it, in both times (whole sign)',
         'Reads': f"root: {looking(natal)}; revolution: {looking(rev)}", 'Source': 'I.7, 4; fn 41'},
        {'I.7': '5', 'Question': 'Who has a claim on it, where they are relative to it, and in a share or in exile (in the revolution)',
         'Reads': '; '.join(claimants) or '-', 'Source': 'I.7, 5; fn 38'},
        {'I.7': '6', 'Question': f"Its lord, {lord}: one house or two, does it look at them, and where each is relative to the other",
         'Reads': f"{len(houses)} house{'s' if len(houses) != 1 else ''}: " + ('; '.join(parts) or '-'), 'Source': 'I.7, 6'},
    ]

def pn4_i7_planets(chart_data, sr):
    """I.7, 7, 10-14, 17-19, 22-24 per planet, in the root and the
    revolution, from the engine's evaluators."""
    rows = []
    natal = chart_data['planetary_data']
    for label, chart in (('root', chart_data), ('revolution', sr)):
        data, asc, sect = chart['planetary_data'], chart['ascendant'], chart['sect']
        acc = evaluate_accidental_dignities(data, chart['houses'], sect, chart.get('julian_day'),
                                            armc=chart.get('armc'), obliquity=chart.get('obliquity'), geo_lat=chart.get('geo_lat'))
        pairs = _pairwise_configurations(data)
        try:
            receptions = evaluate_reception(data, sect)
        except Exception:
            receptions = None
        for planet in PN4_SEVEN:
            if planet not in data:
                continue
            row = data[planet]
            lon = row['longitude']
            a = acc.get(planet, {})
            phase, side, _el = solar_phase(planet, lon, data['Sun']['longitude'], data.get(planet, {}).get('speed_in_lon'))
            my_idx = int(lon // 30)
            assembled, looks, averse = [], [], []
            for other in PN4_SEVEN:
                if other == planet or other not in data:
                    continue
                o_idx = int(data[other]['longitude'] // 30)
                apart = min((o_idx - my_idx) % 12, (my_idx - o_idx) % 12)
                entry = ASPECT_BY_SIGN_COUNT.get(apart)
                if apart == 0:
                    assembled.append(other)
                elif entry:
                    looks.append(f"{other} ({entry[0].lower()})")
                else:
                    averse.append(other)
            by_degree = []
            for pr in pairs:
                if planet not in (pr['p1'], pr['p2']) or pr['aspect_name'] == 'Aversion':
                    continue
                other = pr['p2'] if pr['p1'] == planet else pr['p1']
                by_degree.append(f"{other} {pr['aspect_name'].lower()}, {str(pr.get('motion', '-')).lower()}"
                                 + (', connected' if _is_connected(pr) else ''))
            if receptions is None:
                received = 'not computed'
            else:
                by = sorted({r['Receiver'] for r in receptions if r.get('Received') == planet
                             or (r.get('Received') == 'each other' and planet in str(r.get('Receiver')))})
                received = ', '.join(by) or 'not received'
            h = get_wsh_house(lon, asc)
            if label == 'revolution' and planet in natal:
                grade = _pn4_transit_grade(lon, natal[planet]['longitude'])
                others = [q for q in PN4_SEVEN if q != planet and q in natal and _pn4_transit_grade(lon, natal[q]['longitude'])]
                returns = (f"on its own rooted place by {grade}" if grade else 'not on its rooted place') + \
                          (f"; on the rooted place of {', '.join(others)}" if others else '')
            else:
                returns = '-'
            rows.append({
                'Planet': planet, 'Chart': label,
                'Motion (7)': 'retrograde' if row.get('speed_in_lon', 1.0) < 0 else 'direct',
                'Whole sign (10-11)': (f"assembled with {', '.join(assembled)}; " if assembled else '') +
                                      (f"looks at {', '.join(looks)}; " if looks else '') +
                                      (f"in aversion to {', '.join(averse)}" if averse else '') or '-',
                'By degree (12-13)': '; '.join(by_degree) or 'none',
                'Received by (14)': received,
                'Domain (17)': 'in its own domain' if a.get('Hayz') else 'contrary to its domain' if a.get('ContraryDomain') else 'neither',
                'Twelfth-part (18)': get_degree_string(pn4_twelfth_part(lon)),
                'Return (19)': returns,
                'Stakes (23)': f"house {h}, {_pn4_house_class(h)}",
                'Sun (24)': (f"{side or '-'}" + (f", {phase.lower()}" if phase else ', in its own glow')),
            })
    return rows

# --- IX.7, 1-72: the nine methods for the days and hours ------------------
# "The days and hours have nine indicators" (IX.7, 1). Six and seven --
# the mighty days and the small days -- are built above. The other seven:
#   1 (2-6)   the days since birth "up to the year which has just been
#             completed", divided by seven: each week to a planet from the
#             lord of the natal Ascendant, "then the one below it in the
#             circle"; the remainder days say whose week opens the year and
#             how much of it is left; each day of a week to the planets in
#             the same order; each hour to them, 3 3/7 hours apiece (fn 164);
#   2 (7-9)   the lord of the orb of that year "grants 7 days" from the
#             first day of the revolution, then the planets below it, round
#             again; days and hours as in 1;
#   3 (10-13) the year, "365 1/4 minus 1/300 of a day", in seven "greater
#             sevenths" (52 d 4 h and a quarter) from the lord of the
#             revolution's Ascendant downward; each in seven "lesser
#             sevenths" (7 d 10 h and about 6/7 of an hour); days and hours
#             as in 1;
#   4 (14-17) the week count of 1, the cycles going to the SIGNS from the
#             natal Ascendant, "not the lord of the sign" (fn 171); a
#             week's 168 hours among the twelve signs, 14 apiece (fn 173);
#   5 (18-20) the days since birth cast out by twelves from the natal
#             Ascendant: the sign reached manages that day and "introduces
#             the year"; each sign then a day; two hours to a sign;
#   8 (34-39) the month's days from the four rooted monthly indicators
#             (fn 181) and the month's Ascendant, Lot and Moon: a day per
#             degree up to thirty, or a day per 12 degrees, 2 1/2 days and
#             then 5 hours to a sign, sixty hours for the twelve;
#   9 (43-72) the ninth-part method from three starts -- the terminal
#             sign, the revolution's Ascendant, the Moon's own ninth-part
#             and degree -- a sign a month of 30 d 10 h 30 m, each
#             ninth-part 3 d 9 h 10 m, subdivided into thirds among its
#             lord and the lords of the fifth and ninth signs from it, then
#             ninths, then thirds again (49-54); worked at 57-69.
# IX.7, 56: everything in equal hours. IX.7, 79 declines day and hour
# CHARTS; these nine are what the author uses instead.
#
# WHAT IS READ IN, and said on the page. A "day" is a whole 24-hour
# period from the birth moment (fn 161: the book does not say whether
# from birth or from dawn). The 'now' is the page's target date at noon.
# Method 8's four rooted indicators are the monthly profections of IX.1,
# 26 already on the page (fn 181). Method 9's subdivision partners, "the
# lord of the fifth sign from the sign of the lord of the ninth-part" and
# "the ninth", are the domicile lords of those signs, which is what the
# worked example does (Capricorn, then Taurus and Virgo: Saturn, Venus,
# Mercury). Two of the example's printed fractions are wrong and fn 195
# and 197 say so; the exact values are computed and the printed ones
# shown beside them as printed errata. The judgments of IX.7, 21-22 and
# 40-42 are not built. Decided by the owner 2026-09-10.
PN4_IX7_YEAR_DAYS = 365.25 - 1.0 / 300.0                 # IX.7, 10
PN4_IX7_GREATER_SEVENTH = PN4_IX7_YEAR_DAYS / 7.0        # 52 d 4 h and a quarter (fn 168)
PN4_IX7_LESSER_SEVENTH = PN4_IX7_GREATER_SEVENTH / 7.0   # 7 d 10 h and about 6/7 of an hour
PN4_IX7_MONTH_DAYS = 365.25 / 12.0                       # IX.7, 54-55: 30 d 10 h 30 m
PN4_IX7_NINTH_PART_DAYS = PN4_IX7_MONTH_DAYS / 9.0       # 3 d 9 h 10 m
PN4_IX7_EXAMPLE_ERRATA = (
    ('IX.7, 62', '7\' 25" 33""', '7\' 24" 26""', 'fn 195'),
    ('IX.7, 66', '2\' 28" 31""', '2\' 28" 09""', 'fn 197'),
)

def _pn4_sign_step(sign, steps):
    return SIGN_ORDER[(SIGN_ORDER.index(sign) + int(steps)) % 12]

def _pn4_hours_of_seven(day_fraction):
    """IX.7, 6: the day's 24 hours among the seven, 3 3/7 apiece."""
    return int((day_fraction * 24.0) // (24.0 / 7.0))

def pn4_ix7_weeks_from_birth(days_since_birth, asc_lord):
    """Method 1, IX.7, 2-6."""
    d = int(days_since_birth // 1)
    weeks, rem = d // 7, d % 7
    week = pn4_hour_lord_from_natal(asc_lord, weeks)
    day = pn4_hour_lord_from_natal(asc_lord, weeks + rem)
    hour = pn4_hour_lord_from_natal(day, _pn4_hours_of_seven(days_since_birth % 1.0))
    return {'weeks': weeks, 'remainder': rem, 'left_of_week': 7 - rem, 'week': week, 'day': day, 'hour': hour}

def pn4_ix7_weeks_from_orb(days_since_revolution, orb_lord):
    """Method 2, IX.7, 7-9."""
    if not orb_lord:
        return None
    d = int(days_since_revolution // 1)
    weeks, rem = d // 7, d % 7
    week = pn4_hour_lord_from_natal(orb_lord, weeks)
    day = pn4_hour_lord_from_natal(orb_lord, weeks + rem)
    hour = pn4_hour_lord_from_natal(day, _pn4_hours_of_seven(days_since_revolution % 1.0))
    return {'weeks': weeks, 'remainder': rem, 'week': week, 'day': day, 'hour': hour}

def pn4_ix7_sevenths(days_since_revolution, sr_asc_lord):
    """Method 3, IX.7, 10-13."""
    t = days_since_revolution
    g = int(t // PN4_IX7_GREATER_SEVENTH)
    within_g = t - g * PN4_IX7_GREATER_SEVENTH
    l = int(within_g // PN4_IX7_LESSER_SEVENTH)
    within_l = within_g - l * PN4_IX7_LESSER_SEVENTH
    greater = pn4_hour_lord_from_natal(sr_asc_lord, g)
    lesser = pn4_hour_lord_from_natal(greater, l)
    day = pn4_hour_lord_from_natal(lesser, int(within_l // 1))
    hour = pn4_hour_lord_from_natal(day, _pn4_hours_of_seven(within_l % 1.0))
    return {'greater_index': g, 'lesser_index': l, 'greater_seventh': greater, 'lesser_seventh': lesser, 'day': day, 'hour': hour}

def pn4_ix7_weeks_to_signs(days_since_birth, asc_sign):
    """Method 4, IX.7, 14-17: the cycles of weeks to the signs; 14 hours a
    sign within the week (fn 173)."""
    d = int(days_since_birth // 1)
    weeks, rem = d // 7, d % 7
    week_sign = _pn4_sign_step(asc_sign, weeks)
    hours_in_week = (days_since_birth - weeks * 7) * 24.0
    now_sign = _pn4_sign_step(week_sign, int(hours_in_week // 14.0))
    return {'weeks': weeks, 'remainder': rem, 'week': week_sign, 'now': now_sign}

def pn4_ix7_days_to_signs(days_since_birth, asc_sign):
    """Method 5, IX.7, 18-20: the days by twelves from the natal
    Ascendant; two hours a sign."""
    d = int(days_since_birth // 1)
    day_sign = _pn4_sign_step(asc_sign, d % 12)
    hour_sign = _pn4_sign_step(day_sign, int(((days_since_birth % 1.0) * 24.0) // 2.0))
    return {'day': day_sign, 'hour': hour_sign}

def pn4_ix7_month_days(days_since_month, starts):
    """Method 8, IX.7, 34-39, for each of the seven starts (name, lon):
    way [1] a day per degree; way [2] a day per twelve degrees, 2 1/2 days
    to a sign, five hours to a sign within that."""
    # IX.7, 39: past the thirtieth day "in the management of the days and
    # hours it will return to the position which it began from" -- both
    # ways wrap at 30 (order PN4R-4p-8; way [1] had run on into day 31).
    d = days_since_month % 30.0
    rows = []
    for name, lon in starts:
        way1 = (lon + d) % 360.0
        sign0 = get_zodiac_sign(lon)
        way2_sign = _pn4_sign_step(sign0, int(d // 2.5))
        hours_in_slot = (d % 2.5) * 24.0
        way2_hour = _pn4_sign_step(way2_sign, int(hours_in_slot // 5.0))
        rows.append({'Start': name, 'Position': get_degree_string(lon),
                     'Way 1: a day per degree, now at': f"{get_degree_string(way1)} (bound of {pn4_bound_lord(way1)})",
                     'Way 2: the day\'s sign': way2_sign, 'Way 2: this hour\'s sign': way2_hour,
                     'Source': 'IX.7, 35-39'})
    return rows

def pn4_ix7_ninth_parts(days_since_revolution, start_sign, start_offset_days=0.0):
    """Method 9, IX.7, 43-55: a sign a month from `start_sign`, the
    ninth-parts of each sign 3 d 9 h 10 m apiece, each in thirds among the
    lords of its own sign and the fifth and ninth from it, each third in
    ninths continuing the ninth-part sequence, each ninth in thirds again.
    `start_offset_days` places the Moon's own start within her ninth-part
    (IX.7, 71)."""
    N, M = PN4_IX7_NINTH_PART_DAYS, PN4_IX7_MONTH_DAYS
    third, ninth, third_of_ninth = N / 3.0, N / 27.0, N / 81.0
    t = days_since_revolution + start_offset_days
    m = int(t // M)
    u = t - m * M
    month_sign = _pn4_sign_step(start_sign, m)
    first = pn4_first_ninth_part_lord(month_sign)['ninth_part_sign']
    k = int(u // N)
    np_sign = _pn4_sign_step(first, k)
    w = u - k * N
    j = int(w // third)
    third_sign = _pn4_sign_step(np_sign, (0, 4, 8)[j])
    x = w - j * third
    i = int(x // ninth)
    ninth_sign = _pn4_sign_step(third_sign, i)
    y = x - i * ninth
    q = int(y // third_of_ninth)
    q_sign = _pn4_sign_step(ninth_sign, (0, 4, 8)[q])
    lord = lambda s: SIGN_TO_DOMICILE.get(s, '-')
    return {
        'month': m + 1, 'month_sign': month_sign,
        'ninth_part': k + 1, 'ninth_part_sign': np_sign, 'ninth_part_lord': lord(np_sign),
        'ninth_part_days': (m * M + k * N - start_offset_days, m * M + (k + 1) * N - start_offset_days),
        'third': j + 1, 'third_lord': lord(third_sign), 'third_sign': third_sign,
        'ninth': i + 1, 'ninth_lord': lord(ninth_sign), 'ninth_sign': ninth_sign,
        'third_of_ninth': q + 1, 'third_of_ninth_lord': lord(q_sign),
        'durations_hours': {'ninth-part': N * 24.0, 'third': third * 24.0, 'ninth of the third': ninth * 24.0,
                            'third of the ninth': third_of_ninth * 24.0},
    }

def pn4_ix7_moon_start(moon_lon):
    """IX.7, 71: the Moon begins "from that ninth-part and from that degree
    she is in" -- her sign, and the days into the month her degree stands
    for at the ninth-part's rate."""
    within = moon_lon % 30.0
    return get_zodiac_sign(moon_lon), within / (30.0 / 9.0) * PN4_IX7_NINTH_PART_DAYS

def pn4_day_methods(jd_birth, jd_sr, jd_mr, jd_now, natal_asc, sr_asc, orb_lord, year_sign, month_starts, sr_moon_lon):
    """The seven methods at `jd_now`, as rows for the page, with method
    8's and 9's own tables."""
    since_birth, since_rev, since_month = jd_now - jd_birth, jd_now - jd_sr, jd_now - jd_mr
    at_rev = int((jd_sr - jd_birth) // 1)
    asc_sign, asc_lord = get_zodiac_sign(natal_asc), SIGN_TO_DOMICILE.get(get_zodiac_sign(natal_asc), '-')
    sr_lord = SIGN_TO_DOMICILE.get(get_zodiac_sign(sr_asc), '-')
    m1_open = pn4_ix7_weeks_from_birth(float(at_rev), asc_lord)
    m1, m2 = pn4_ix7_weeks_from_birth(since_birth, asc_lord), pn4_ix7_weeks_from_orb(since_rev, orb_lord)
    m3, m4, m5 = pn4_ix7_sevenths(since_rev, sr_lord), pn4_ix7_weeks_to_signs(since_birth, asc_sign), pn4_ix7_days_to_signs(since_birth, asc_sign)
    rows = [
        {'Method': '1. The weeks of days from birth', 'Opens the year': f"{m1_open['week']}'s week, {m1_open['left_of_week']} of its days left ({at_rev} days from birth: {m1_open['weeks']} weeks and {m1_open['remainder']})",
         'This week': m1['week'], 'Today': m1['day'], 'This hour': m1['hour'], 'Source': 'IX.7, 2-6'},
        {'Method': '2. Seven days each from the lord of the orb', 'Opens the year': f"{orb_lord}, the lord of the orb, the first seven days" if orb_lord else 'natal hour lord unavailable',
         'This week': m2['week'] if m2 else '-', 'Today': m2['day'] if m2 else '-', 'This hour': m2['hour'] if m2 else '-', 'Source': 'IX.7, 7-9'},
        {'Method': '3. The greater and lesser sevenths of the year', 'Opens the year': f"{sr_lord}, lord of the revolution\'s Ascendant, the first greater seventh ({PN4_IX7_GREATER_SEVENTH:.3f} days)",
         'This week': f"greater {m3['greater_seventh']} (no. {m3['greater_index'] + 1}), lesser {m3['lesser_seventh']} (no. {m3['lesser_index'] + 1})", 'Today': m3['day'], 'This hour': m3['hour'], 'Source': 'IX.7, 10-13'},
        {'Method': '4. The weeks to the signs from the natal Ascendant', 'Opens the year': f"the week of {pn4_ix7_weeks_to_signs(float(at_rev), asc_sign)['week']}",
         'This week': m4['week'], 'Today': f"{m4['now']} (14 hours a sign, fn 173)", 'This hour': m4['now'], 'Source': 'IX.7, 14-17'},
        {'Method': '5. The days to the signs by twelves from the natal Ascendant', 'Opens the year': pn4_ix7_days_to_signs(float(at_rev), asc_sign)['day'],
         'This week': '-', 'Today': m5['day'], 'This hour': m5['hour'], 'Source': 'IX.7, 18-20'},
        {'Method': '6. The mighty days', 'Opens the year': 'the terminal point', 'This week': '-', 'Today': 'the mighty-days table above', 'This hour': '-', 'Source': 'IX.7, 23-28'},
        {'Method': '7. The small days', 'Opens the year': "the revolution's Ascendant", 'This week': '-', 'Today': 'the small-days table above', 'This hour': '-', 'Source': 'IX.7, 29-33'},
        {'Method': "8. The month's days", 'Opens the year': '-', 'This week': '-', 'Today': 'the table below', 'This hour': 'the table below', 'Source': 'IX.7, 34-39'},
        {'Method': '9. The ninth-parts', 'Opens the year': f"the first ninth-part of {year_sign}", 'This week': '-', 'Today': 'the table below', 'This hour': 'the table below', 'Source': 'IX.7, 43-72'},
    ]
    month_rows = pn4_ix7_month_days(since_month, month_starts)
    moon_sign, moon_offset = pn4_ix7_moon_start(sr_moon_lon)
    ninth_rows = []
    for label, start, offset, cite in (('the sign of the terminal point', year_sign, 0.0, 'IX.7, 44-48'),
                                        ("the revolution's Ascendant", get_zodiac_sign(sr_asc), 0.0, 'IX.7, 70'),
                                        ("the Moon, from her own ninth-part and degree", moon_sign, moon_offset, 'IX.7, 71')):
        r = pn4_ix7_ninth_parts(since_rev, start, offset)
        ninth_rows.append({'Start': label, 'Month': f"{r['month']}: {r['month_sign']}",
                           'Ninth-part (3 d 9 h 10 m)': f"{r['ninth_part']} of 9: {r['ninth_part_sign']}, {r['ninth_part_lord']}, days {r['ninth_part_days'][0]:.2f} to {r['ninth_part_days'][1]:.2f}",
                           'Third (27 h 3 m)': f"{r['third']}: {r['third_lord']} ({r['third_sign']})",
                           'Ninth of the third (3 h 0.4 m)': f"{r['ninth']}: {r['ninth_lord']} ({r['ninth_sign']})",
                           'Third of that (1 h 0.1 m)': f"{r['third_of_ninth']}: {r['third_of_ninth_lord']}",
                           'Source': cite})
    return rows, month_rows, ninth_rows

def pn4_fardar_at_age(age_years, sect):
    """The fardar lord and sub-lord at an age.

    IV.7, 25: "once 75 years are completed for the native, the
    distribution of the fardar returns to THE LUMINARY WHICH HE BEGAN FROM
    at his birth, in the original order" -- so the cycle restarts at the
    light of the sect, not always at the Sun. IV.1, 2's "then it returns
    to the Sun" is the diurnal case of that rule."""
    if age_years < 0:
        return None
    sequence = pn4_fardar_sequence(sect)
    cycles, within = divmod(float(age_years), PN4_FARDAR_CYCLE_YEARS)
    start = 0.0
    for lord, years in sequence:
        if within < start + years:
            offset = within - start
            subs = pn4_fardar_subperiods(lord, years)
            sub_lord, sub_from, sub_to = None, None, None
            if subs:
                each = years / 7.0
                # The sub-period is found against the SAME boundaries it
                # reports (start + k*each), not by offset // each: the
                # floating quotient of a returned sub_to fed back in came
                # out a hair under the next integer and named the expired
                # sub-period again (Astra F12). Half-open, like the main
                # periods: a sub-period does not own its own end.
                k = next((j for j in range(7) if within < start + (j + 1) * each), 6)
                sub_lord = subs[k][0]
                sub_from, sub_to = start + k * each, start + (k + 1) * each
            return {
                'lord': lord, 'years': years,
                'from': cycles * PN4_FARDAR_CYCLE_YEARS + start,
                'to': cycles * PN4_FARDAR_CYCLE_YEARS + start + years,
                'sub_lord': sub_lord,
                'sub_from': None if sub_from is None else cycles * PN4_FARDAR_CYCLE_YEARS + sub_from,
                'sub_to': None if sub_to is None else cycles * PN4_FARDAR_CYCLE_YEARS + sub_to,
                'cycle': int(cycles) + 1,
            }
        start += years
    return None

# --- I.8, 10-26: the Ages of Man -----------------------------------------
# Ptolemy's seven ages, ordered by sphere from the lowest upward, NOT the
# quadrant scheme of Sahl, On Nativities 3.9, 32-36. Each span is a
# planet's lesser years, or one-half or one-tenth of its lesser or middle
# years (I.8, 9): Moon 4 = a tenth of her middle years 39 1/2 (I.8, 12),
# Mercury 10 = half his lesser 20, and Venus 8, Sun 19, Mars 15,
# Jupiter 12, Saturn 30 are lesser years outright.
#
# Saturn's span is OPEN-ENDED. Figure 53 tabulates it as "30 / ages 68-97"
# and 30 is his lesser years, but the prose governs: the seventh age runs
# "until the end of his lifespan" (I.8, 25). A native of 100 is still in
# Saturn's age. I.8, 31-33 reports that some restart the cycle at the Moon
# after Saturn; Abu Ma'shar does not endorse it, so this does not restart.
#
# I.8, 34-35: he also refuses to subdivide an age into sevenths the way a
# fardar is subdivided -- "he will be in the nature of the planet itself,
# for the amount of those years". So there is no sub-lord here.
PN4_AGES_OF_MAN = (
    ('Moon', 4, 'Upbringing'), ('Mercury', 10, 'End of childhood'),
    ('Venus', 8, 'Beginning of youth'), ('Sun', 19, 'End of youth'),
    ('Mars', 15, 'Beginning of maturity'), ('Jupiter', 12, 'Maturity, transition to old age'),
    ('Saturn', 30, 'Old age'),
)

def pn4_age_of_man(age_years):
    """I.8, 10-26. The last age is open-ended (I.8, 25)."""
    if age_years < 0:
        return None
    start = 0.0
    for i, (planet, years, label) in enumerate(PN4_AGES_OF_MAN):
        last = i == len(PN4_AGES_OF_MAN) - 1
        if last or age_years < start + years:
            return {'planet': planet, 'from': start,
                    'to': None if last else start + years,
                    'label': label, 'nominal_years': years}
        start += years
    return None

# --- I.2 and IX.3: the revolutions ---------------------------------------

PN4_MEAN_SOLAR_DAY_MOTION = 0.9856

def _pn4_sun_offset(jd, target_lon):
    res = swe.calc_ut(jd, swe.SUN)[0]
    return ((res[0] - target_lon + 180.0) % 360.0) - 180.0, res[3]

def pn4_revolution_jd(target_lon, jd_guess):
    """Newton search for the moment the TRUE Sun stands at target_lon,
    from a guess within a few days, in the manner calculate_prenatal_syzygy
    searches for the syzygy.

    I.2, 1 defines the revolution as the Sun's return to "his position in
    which he was at the root". Abu Ma'shar computes it from a MEAN Sun and
    then applies the Hipparchan tropical year of 365;14,48 days
    (I.4, 23-31; IX.7, 10) -- Dykes says plainly that this does not make
    sense (Intro Sect. 1, p. 6), and it is not reproduced. This is a true-Sun
    return, which is what the definition actually asks for."""
    jd = float(jd_guess)
    for _ in range(30):
        offset, speed = _pn4_sun_offset(jd, target_lon)
        if abs(offset) < 1e-9:
            break
        if abs(speed) < 1e-6:
            speed = PN4_MEAN_SOLAR_DAY_MOTION
        jd -= offset / speed
    return jd

def pn4_solar_revolution_jd(jd_natal, natal_sun_lon, age):
    """The solar revolution opening the native's `age`-th completed year.
    Cast for the BIRTH LOCATION: PN IV never states the location for the
    annual revolution, but it does for the monthly ones -- "(And we will
    use the birthplace for the location)", Intro Sect. 9, p. 95 -- and the
    excess-of-revolution technique presupposes a fixed one. Dykes' reading;
    flagged as an assumption in the UI, not as Abu Ma'shar's sentence."""
    return pn4_revolution_jd(natal_sun_lon % 360.0,
                             jd_natal + float(age) * 365.2425)

def pn4_monthly_revolution_jd(jd_solar_revolution, natal_sun_lon, month):
    """IX.3, 2: month 1 IS the solar revolution (IX.1, 10; IX.2, 1-2).
    For month n the Sun stands in the n-th sign from his rooted place, "in
    the like degree AND MINUTE which he was in at the root".

    Intro Sect. 2 (p. 7) illustrates this with a natal Sun at 12 22' Gemini
    and then puts the monthly revolutions at 12 23' Cancer and 12 23' Leo.
    The page genuinely prints that; it is an error in Dykes' own book
    (PN4_READTHROUGH_FINDINGS_2026-09-10.md, P-01), contradicted by the
    rule in its own sentence, by IX.1, 23, by IX.3, 2 and by the worked
    example at Intro Sect. 9 p. 95. The degree and minute do not change."""
    month = int(month)
    if month <= 1:
        return jd_solar_revolution
    target = (natal_sun_lon + 30.0 * (month - 1)) % 360.0
    return pn4_revolution_jd(target, jd_solar_revolution + (month - 1) * 30.44)

# --- Profection: II.3, 1 and IX.1 ----------------------------------------

def pn4_profect(lon, steps, forward=True):
    """Move a point `steps` whole signs, keeping its degree within the
    sign. All profection in PN IV is sign-by-sign (IX.1; Intro Sect. 9 p. 90)."""
    idx = int(lon // 30.0)
    moved = (idx + steps) % 12 if forward else (idx - steps) % 12
    return moved * 30.0 + (lon % 30.0)

def pn4_sign_of_the_year(ascendant_lon, completed_years):
    """II.3, 1 and I.2, 5: "for every year the native has completed, cast
    out one sign from it: the sign which the intended year reaches is the
    'sign of the terminal point,' and its lord is the 'lord of the year'
    (and in Persian it is called the *salkhudhah*)."

    The lord of the year is the lord of the SIGN -- not the lord of the
    revolution's Ascendant, and not a victor (Q21). "Governor"
    (Ar. mustawli), the sign on which most of the year's indicators
    coincide (IX.9, 10; IX.2, 4-7), is a separate term."""
    lon = pn4_profect(ascendant_lon, int(completed_years))
    sign = get_zodiac_sign(lon)
    return {'longitude': lon, 'sign': sign, 'lord': SIGN_TO_DOMICILE.get(sign, '-')}

def pn4_first_ninth_part_lord(sign):
    """The lord of the first ninth-part of a sign -- monthly indicator #2
    (IX.1, 36), and the Indian rule for the lord of the year that PN IV
    reports without adopting (III.10, 1).

    The first ninth-part of a convertible sign is that sign; of a fixed
    sign, the ninth from it; of a double-bodied sign, the fifth from it.
    So the lord is always a lord of a convertible sign, which is why the
    Indian rule "restricts the lord of the year to four planets only".
    Verified against Abu Ma'shar's own three worked examples at III.10, 5:
    Taurus -> Saturn, Gemini -> Venus, Cancer -> the Moon.

    It is a function of the SIGN, not of the degree: "if the year
    terminated at 20 deg of Taurus (or less than that or more), then its
    lord would be Saturn" (III.10, 5)."""
    idx = SIGN_ORDER.index(sign)
    kind = PN4_QUADRUPLICITY[sign]
    step = {'convertible': 0, 'fixed': 8, 'double-bodied': 4}[kind]
    target = SIGN_ORDER[(idx + step) % 12]
    return {'ninth_part_sign': target, 'lord': SIGN_TO_DOMICILE.get(target, '-')}

# The direction of monthly profection. Abu Ma'shar's quadruplicity rule
# (IX.1, 26-34) reverses it for convertible signs and for the second half
# of a double-bodied one; Dykes rejects the rule as "complicated, probably
# wrong, and an over-zealous application of quadruplicities" (Intro
# Sect. 9 p. 102 and fn 95) and counts forward always. Owner's decision of
# 2026-09-10: ship both, default to Dykes.
PN4_MONTHLY_TURN_OPTIONS = ('Dykes: always forward', "PN IV IX.1, 26-34")

def pn4_monthly_turn_forward(lon, rule):
    """IX.1, 26-30, applied PER INDICATOR.

    IX.1, 31 is explicit that when the four rooted indicators fall in
    different quadruplicities "one turns EACH ONE OF THEM INDIVIDUALLY",
    so the direction is decided by the sign each indicator itself occupies
    -- not once, globally, by the sign of the year. (The two coincide for
    indicator #1, whose sign IS the sign of the year, and can differ for
    #3, #4 and #5.)

    The boundary in a double-bodied sign is 15 deg 00': forward "from the
    beginning of that sign up to 15 complete degrees" (28), backward "from
    the beginning of the sixteenth degree ... up to the end" (29), because
    the first half is of the nature of the preceding fixed sign and the
    second of the following convertible one (30)."""
    if rule != PN4_MONTHLY_TURN_OPTIONS[1]:
        return True
    kind = PN4_QUADRUPLICITY[get_zodiac_sign(lon)]
    if kind == 'fixed':
        return True
    if kind == 'convertible':
        return False
    return (lon % 30.0) < 15.0

# IX.1, 35-39: the seven monthly indicators, five rooted and two not.
# "Rooted" because they are turned from the positions they hold AT THE
# REVOLUTION OF THE YEAR (IX.1, 37); the last two are not, because each
# "indicates the condition of a single month, and [then] changes in the
# next month" (IX.1, 38). They decrease in universality in that order
# (IX.1, 39).
#
# fn 15 to IX.1, 26 notes that Abu Ma'shar himself "will ignore [#2] the
# ninth-part" through most of these chapters, and fn 3 to II.1, 5 notes
# that the Indian ninth-parts are absent from the nineteen indicators of
# the year. It is carried here because IX.1, 36 names it.
PN4_MONTHLY_INDICATOR_NAMES = (
    (1, 'Sign of the terminal point (profected natal Ascendant)', True),
    (2, "Lord of the month's sign's first ninth-part", True),
    (3, 'Profected natal Lot of Fortune', True),
    (4, 'Ascendant of the revolution of the year', True),
    (5, 'Lot of Fortune of the revolution of the year', True),
    (6, 'Ascendant of the revolution of the month', False),
    (7, 'Lot of Fortune of the revolution of the month', False),
)

def pn4_monthly_indicators(month, completed_years, sign_of_year_lon, natal_fortune_lon,
                           sr_ascendant_lon, sr_fortune_lon,
                           mr_ascendant_lon, mr_fortune_lon, rule):
    """The seven indicators of IX.1, 35-39 for month `month` (1-12).

    Each is first brought to its position for the YEAR, and only then
    turned month by month -- and the four are not brought there the same
    way, which is the thing to get right:

    * #1 is the natal Ascendant profected a sign a year (IX.1, 9).
    * #3 is the natal Lot of Fortune profected a sign a year in its own
      right: "you see where the Lot of Fortune is in the root of the
      nativity, and TURN FROM IT A SIGN FOR EVERY YEAR, up to the year
      which you want" (IX.1, 17-18). It is not the natal Lot itself.
    * #4 and #5 are NOT profected: the revolution's Ascendant and its Lot
      of Fortune are "assign[ed] to the first month" as they stand
      (IX.1, 20-21).
    * #6 and #7 are not turned at all -- they are read from the monthly
      revolution, which is cast afresh each month (IX.1, 38).

    #2 is a different shape from the rest. What turns is the sign of the
    terminal point, and the indicator is the lord of the FIRST ninth-part
    of whatever sign the turning reaches: "the lord of the first
    ninth-part belonging to the second sign from the sign of the terminal
    point ... is the indicator of the condition of the second month"
    (IX.1, 12-14). Abu Ma'shar works it at IX.1, 15-16 -- year at Cancer:
    Moon, then Leo -> Mars, Virgo -> Saturn, Libra -> Venus. It always
    turns forward, "without distinction, whether the sign of the terminal
    point is convertible, fixed, or having two bodies" (IX.1, 32), and it
    ignores the degree entirely (IX.1, 11: "so don't worry about which
    position in that sign is the terminal point of the year").
    """
    steps = max(int(month) - 1, 0)

    def _row(number, lon, direction):
        sign = get_zodiac_sign(lon)
        return {'number': number, 'name': PN4_MONTHLY_INDICATOR_NAMES[number - 1][1],
                'rooted': PN4_MONTHLY_INDICATOR_NAMES[number - 1][2],
                'longitude': lon, 'sign': sign,
                'lord': SIGN_TO_DOMICILE.get(sign, '-'), 'direction': direction}

    out = []
    # #1, #3, #4, #5: turned, each by the quadruplicity of its OWN sign.
    for number, base in ((1, sign_of_year_lon),
                         (3, pn4_profect(natal_fortune_lon, int(completed_years))),
                         (4, sr_ascendant_lon),
                         (5, sr_fortune_lon)):
        forward = pn4_monthly_turn_forward(base, rule)
        out.append(_row(number, pn4_profect(base, steps, forward=forward),
                        'forward' if forward else 'backwards'))

    # #2: the terminal point turns forward; the lord is that sign's first
    # ninth-part lord, so the row names the ninth-part sign it comes from.
    month_sign = get_zodiac_sign(pn4_profect(sign_of_year_lon, steps, forward=True))
    ninth = pn4_first_ninth_part_lord(month_sign)
    out.append({'number': 2, 'name': PN4_MONTHLY_INDICATOR_NAMES[1][1], 'rooted': True,
                'longitude': SIGN_ORDER.index(ninth['ninth_part_sign']) * 30.0,
                'sign': ninth['ninth_part_sign'], 'lord': ninth['lord'],
                'direction': f"forward (from {month_sign})"})

    for number, lon in ((6, mr_ascendant_lon), (7, mr_fortune_lon)):
        out.append(_row(number, lon, 'cast, not turned'))

    out.sort(key=lambda r: r['number'])
    return out

# II.1, 5-24 ranks NINETEEN indicators of the year and II.1, 25 says "each
# one in turn is stronger in indication than the one which is after it".
# The first four are implemented; the rest are delineation material.
#
# PN IV's own order is applied on the PN IV page and RANKS BY SCOPE. Within
# a single year the lord of the year outranks the distributor (II.1, 25;
# II.23, 1). Across several years the distribution is stronger, because
# "the indication of the lord of the terminal point is only over the
# condition of THAT YEAR: but as for the lord of the distribution,
# sometimes its indication ... is for SEVERAL YEARS", and the year's
# indicators are then read "as witnesses" to it (III.2, 2-3).
#
# This does not RESOLVE corpus disagreement #1 (an earlier comment said it
# did, "by scope"): Sahl's two consecutive chapters rank the pair in
# opposite orders AS PRINTED -- 1.23, 33 "the lord of the distribution is
# like a tender [of sheep], and the lord of the year like a hireling"
# (the distributor over the lord of the year) against 1.24, 2 "turning is
# the foundation of the work of the stars ... and it is stronger <than>
# the distributor of time" (the turning over the distributor); Dykes fn
# 245 emends the second ("stronger when combined with the distributor"),
# not adopted. Each of PN IV's two scoped rankings agrees with one Sahl
# sentence: II.1, 25 with 1.24, 2 within the year, III.2, 2-3 with 1.23,
# 33 across years. Both Sahl sentences are shown side by side on the page
# (PN4_YEAR_INDICATOR_SCOPE_NOTE; order GAP-3, 2026-09-11).
#
# Dykes' Introduction Sect. 3 (p. 21, point 3) states the opposite --
# distributions "tend to be more powerful than profections" -- and cites no
# Abu Ma'shar sentence for it. II.1, 25 governs here, not Intro Sect. 3.
PN4_YEAR_INDICATOR_SCOPE_NOTE = (
    "The order above is PN IV's, which ranks the lord of the year and the distributor BY SCOPE: within the year the "
    "lord of the year is the stronger (II.1, 25; II.23, 1), across several years the distribution (III.2, 2-3). "
    "Sahl's two consecutive chapters rank them in opposite orders as printed -- On Nativities 1.23, 33: \"the lord "
    "of the distribution is like a tender [of sheep], and the lord of the year like a hireling; so if the tender "
    "committed himself to his sheep in a powerful way, the hireling would have not power over harming the sheep\" "
    "(the distributor over the lord of the year); 1.24, 2: \"turning is the foundation of the work of the stars and "
    "[their] appointed time, and it is stronger <than> the distributor of time\" (the turning over the distributor). "
    "Dykes fn 245 emends the second (\"stronger when combined with the distributor\"), not adopted here. PN IV's "
    "within-the-year ranking agrees with 1.24, 2 and its across-years ranking with 1.23, 33; the disagreement stands "
    "recorded, not resolved."
)
PN4_YEAR_INDICATOR_ORDER = (
    'The sign of the terminal point, and its lord',
    'The distribution and the distributor',
    'The one partnering with the distributor',
    "The fardar lord and its sub-lord",
    'The lord of the orb',
)


# --- Assembling the page -------------------------------------------------

def pn4_datetime_from_jd(jd):
    """The UT civil moment of a Julian Day, as a CivilMoment (not a datetime,
    which cannot hold a Julian-only day such as 1300-02-29): the calendar
    is the one this file uses for that epoch, so feeding it back to
    calculate_traditional_chart -- which reads the digits by the same
    policy -- round-trips. The name is kept for its callers; it formats
    with the same %Y-%m-%d %H:%M:%S directives a datetime does."""
    return CivilMoment.from_jd(jd)

def pn4_completed_years(birth_date, target_date):
    """Age in COMPLETED CIVIL ANNIVERSARIES -- the count II.3, 1 asks for
    ("for every year the native has completed"). Not elapsed days over a
    mean year, which lets the sign turn a day either side of the birthday."""
    years = target_date.year - birth_date.year
    if (target_date.month, target_date.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(years, 0)

def pn4_birthday(birth_date, age):
    """The `age`-th civil anniversary of the birth: the first day on which
    pn4_completed_years(birth_date, day) == age. A 29 February birthday
    falls on 1 March in a common year, which is the first day the count
    of II.3, 1 turns."""
    year = birth_date.year + int(age)
    if civil_is_valid(year, birth_date.month, birth_date.day):
        return CivilDate(year, birth_date.month, birth_date.day)
    return CivilDate(year, 3, 1)

def pn4_ordinal(n):
    """1st, 2nd, 3rd, 4th ... 11th, 12th, 13th, 21st, 42nd."""
    n = int(n)
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

# --- The sidebar's parsers (pure, so the harness can pin them) -------------
TIME_STANDARD_OPTIONS = ("LMT (Local Mean Time)", "Standard time (pytz)", "Manual UTC offset")
TARGET_MODE_OPTIONS = ("Date", "Age")

def parse_iso_date(text):
    """A CivilDate from 'YYYY-MM-DD', or None. Years 1-9999; the digits are
    validated in the calendar civil_calendar() assigns them, so 1300-02-29
    (a Julian leap day) is a date and 1900-02-29 is not."""
    m = re.fullmatch(r"\s*(\d{1,4})-(\d{1,2})-(\d{1,2})\s*", str(text))
    if not m or not civil_is_valid(*m.groups()):
        return None
    return CivilDate(*m.groups())

def parse_lat_lon(text):
    """'45.37, -84.95' typed into the place box, as (lat, lon), or None if
    the text is not two numbers in range."""
    m = re.fullmatch(r"\s*([-+]?\d+(?:\.\d+)?)\s*[, ]\s*([-+]?\d+(?:\.\d+)?)\s*", str(text))
    if not m:
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    if abs(lat) > 90.0 or abs(lon) > 180.0:
        return None
    return lat, lon

def _pn4_seg_degree(segment, ascendant_lon, chart_data, geo_lat):
    """The zodiacal degree the direction stands on at the start of a
    segment: the arc is in oblique ascension, so the degree comes back
    through the inverse (fn 251's inverse, _lon_with_oblique_ascension)."""
    if not segment:
        return ascendant_lon
    oa = (_oblique_ascension(ascendant_lon, chart_data['obliquity'], geo_lat) + segment['from']) % 360.0
    got = _lon_with_oblique_ascension(oa, chart_data['obliquity'], geo_lat)
    return ascendant_lon if got is None else got

PN4_DIRECTION_YEAR_DAYS = 365.2425    # the year a degree of direction is worth, in days, for the Date column.
# Measured against PN IV Figure 22's eight printed dates (a Janus run): this
# mean year, from the birth in UT, reproduces all eight; 365.25 misses two
# (Oct 19 2024 and Dec 19 2026 fall a day late), and local civil time
# misses two the other way. It is also the year this file already uses for
# fractional ages (calculate_time_lords) and the revolution's first guess.

def _pn4_distribution_rows(segments, current, unit='years', origin_jd=None):
    """A distribution as the Timing page prints it, one row per segment,
    the same shape for the Ascendant, the meridian and the small days.
    `unit` is what the segment bounds are in: years (a degree of
    ascension a year, III.1, 13) or days (59' 08" a day, IX.7, 29).
    `origin_jd`, when given, adds the civil DATE each segment opens on, as
    PN IV Figure 22 prints a distribution (Arc, Date, Distributor,
    Partner): the birth for the year-long ones, the revolution for the
    day-long ones, a mean year of 365.2425 days from the moment in UT --
    the construction that reproduces that figure's dates -- in the
    calendar the epoch uses."""
    if unit == 'years':
        head, lasting = ('From age', 'To age'), lambda d: pn4_format_arc_time(d)
        per_unit = PN4_DIRECTION_YEAR_DAYS
    elif unit == 'days':
        head, lasting = ('From day', 'To day'), lambda d: f"{int(d)}d {(d - int(d)) * 24.0:.1f}h"
        per_unit = 1.0
    else:
        raise ValueError(f"unit must be 'years' or 'days', not {unit!r}")
    return [{
        head[0]: f"{seg['from']:.2f}", head[1]: f"{seg['to']:.2f}",
        **({'Date': f"{pn4_datetime_from_jd(origin_jd + seg['from'] * per_unit):%Y-%m-%d}"} if origin_jd is not None else {}),
        'Lasting': lasting(seg['to'] - seg['from']),
        'Distributor': seg['distributor'],
        'Partner': seg['partner'] or 'none',
        'By': seg['partner_aspect'] or '-',
        'Rank': ('-' if seg['partner_aspect'] is None
                 else f"{pn4_partner_strength(seg['partner_aspect']) + 1} of 5"),
        'Opened by': seg['opened_by'],
        'Now': 'yes' if current is not None and seg is current else '',
    } for seg in (segments or [])]

def pn4_timing_bundle(chart_data, lat, lon, birth_date, target_date, rule, chronocrats=None):
    """Everything the Timing page shows that comes from PN IV, computed
    once. Returns a dict of row-lists plus the raw pieces the captions
    need. Kept in the engine half so it is testable without Streamlit.
    `chronocrats` is calculate_chronocrats' result for the birth, read for
    the natal hour lord the lord of the orb (VI.1) starts from."""
    natal_sun = chart_data['planetary_data']['Sun']['longitude']
    ascendant = chart_data['ascendant']
    jd_target = civil_to_jd(target_date.year, target_date.month, target_date.day, 12.0)

    # THREE COUNTS OF THE YEAR, kept apart (Astra F02/F03):
    #  age     -- completed CIVIL anniversaries, II.3, 1's count for the
    #             profection ("for every year the native has completed"),
    #             the lord of the orb (VI.1, by year) and the age labels;
    #  cycle   -- completed SOLAR RETURNS, I.2, 1-3's year ("when he came
    #             back to his position ... a solar year will have been
    #             concluded"): the revolution, its months and its day
    #             clocks belong to the return that CONTAINS the target,
    #             return_n <= target < return_(n+1). Seeded from the civil
    #             age and then bracketed by the actual returns, so a target
    #             a few hours before this year's return is in the preceding
    #             cycle's twelfth month, not in a revolution still to come;
    #  elapsed -- ELAPSED years on the 365.2425-day mean year, the Fig. 22
    #             mapping this file already uses for the Date column: the
    #             fardar's sevenths (IV.1, 5-6; 11: "1 year, 5 months, 4
    #             days, and approximately 6 hours") and the distributions
    #             (III.1, 13: 5' a month, 1' six days) change at fractional
    #             boundaries, and Figure 22 changes a distributor mid-year.
    #             Feeding them the integer age froze every change until the
    #             next birthday.
    age = pn4_completed_years(birth_date, target_date)
    elapsed = (jd_target - chart_data['julian_day']) / PN4_DIRECTION_YEAR_DAYS

    # I.2, 1-4: the revolution of the year, cast for the birth location.
    cycle = age
    jd_sr = pn4_solar_revolution_jd(chart_data['julian_day'], natal_sun, cycle)
    while cycle > 0 and jd_sr > jd_target:
        cycle -= 1
        jd_sr = pn4_solar_revolution_jd(chart_data['julian_day'], natal_sun, cycle)
    jd_sr_next = pn4_solar_revolution_jd(chart_data['julian_day'], natal_sun, cycle + 1)
    while jd_sr_next <= jd_target:
        cycle += 1
        jd_sr, jd_sr_next = jd_sr_next, pn4_solar_revolution_jd(chart_data['julian_day'], natal_sun, cycle + 1)
    sr = calculate_traditional_chart_jd(jd_sr, lat, lon)

    # IX.1, 9-10: the sign of the year is also month 1, and the months run
    # from the revolution dates, not the calendar (Intro Sect. 9 p. 90).
    # Which month the target date falls in: the last monthly revolution at
    # or before it.
    month, jd_mr = 1, jd_sr
    for m in range(1, 13):
        jd_m = pn4_monthly_revolution_jd(jd_sr, natal_sun, m)
        if jd_m <= jd_target:
            month, jd_mr = m, jd_m
    mr = calculate_traditional_chart_jd(jd_mr, lat, lon)

    year = pn4_sign_of_the_year(ascendant, age)
    ninth = pn4_first_ninth_part_lord(year['sign'])
    fardar = pn4_fardar_at_age(elapsed, chart_data['sect'])
    ages = pn4_age_of_man(age)
    segments = pn4_distribution_from_ascendant(
        chart_data['planetary_data'], ascendant, chart_data['obliquity'], lat)
    current = pn4_distribution_at_age(segments, elapsed) if segments else None

    # III.1, 12: the meridian, by right ascension -- the Midheaven and the
    # fourth, each from its own degree. Never refuses (see the function).
    meridian = {}
    for point in PN4_MERIDIAN_POINTS:
        start_lon = chart_data['mc'] if point == 'Midheaven' else (chart_data['mc'] + 180.0) % 360.0
        segs = pn4_distribution_from_meridian(
            chart_data['planetary_data'], chart_data['mc'], chart_data['obliquity'], point)
        meridian[point] = {'degree': start_lon, 'segments': segs,
                           'current': pn4_distribution_at_age(segs, elapsed)}

    # --- The revolution of the year (I.2, 1-4; I.7, 2) ---
    revolution_rows = [
        {'Item': 'Count of the year',
         'Value': (f"{age} completed civil years (the profection's count); {cycle} solar returns completed "
                   f"(the revolution's cycle); {elapsed:.3f} years elapsed at 365.2425 days a year (the Figure 22 "
                   f"mapping, which the fardar and the distributions run on)"
                   + (" -- the civil birthday and the Sun's return fall either side of this date" if age != cycle else '')),
         'Source': 'II.3, 1; I.2, 1-3; IV.1, 5-6 and 11; III.1, 13'},
        {'Item': 'Moment of the revolution (UTC)', 'Value': f"{pn4_datetime_from_jd(jd_sr):%Y-%m-%d %H:%M:%S}",
         'Source': 'I.2, 1: the Sun returns to his rooted position'},
        {'Item': 'Ascendant of the year', 'Value': get_degree_string(sr['ascendant']),
         'Source': 'I.2, 4; vocabulary at Intro Sect. 8 p. 77'},
        {'Item': "Its house in the root", 'Value': f"House {get_wsh_house(sr['ascendant'], ascendant)}",
         'Source': 'I.7, 2: the first thing asked of the chart'},
        {'Item': 'Lot of Fortune of the year', 'Value': get_degree_string(sr['lot_of_fortune']),
         'Source': 'I.6, 3; monthly indicator #5 at IX.1, 36'},
        {'Item': 'Sect of the revolution', 'Value': sr['sect'], 'Source': 'I.6, 3'},
        {'Item': 'Location', 'Value': 'Birth location (assumed)',
         'Source': "Not stated for the year; stated for the months, Intro Sect. 9 p. 95"},
        {'Item': f'Revolution of the month ({month} of 12)', 'Value': f"{pn4_datetime_from_jd(jd_mr):%Y-%m-%d %H:%M:%S} UTC",
         'Source': 'IX.3, 2: the like degree AND minute in the n-th sign'},
        {'Item': 'Ascendant of the month', 'Value': get_degree_string(mr['ascendant']),
         'Source': 'IX.3, 2; monthly indicator #6'},
    ]

    # --- The year's indicators, in II.1, 5-9's order ---
    year_rows = [
        {'#': 1, 'Indicator': PN4_YEAR_INDICATOR_ORDER[0],
         'Active point': f"{year['sign']} ({get_degree_string(year['longitude'])})",
         'Ruler': year['lord'], 'Source': 'II.3, 1; I.2, 5'},
        {'#': 2, 'Indicator': PN4_YEAR_INDICATOR_ORDER[1],
         # I.6, 6 with fn 34: "the very degree which the distribution had
         # reached" -- the direction's degree AT the target, not the bound's
         # opening degree (Astra F11); the opening stands in the
         # distribution table's "Opened by".
         'Active point': ('refused above the polar circle' if segments is None
                          else (f"{get_degree_string(_pn4_seg_degree({'from': elapsed}, ascendant, chart_data, lat))}"
                                if current else
                                f"age {age} is past the {PN4_DISTRIBUTION_SPAN_YEARS:g}-year table")),
         'Ruler': (current or {}).get('distributor', '-') if segments is not None else '-',
         'Source': 'III.1, 11-13'},
        {'#': 3, 'Indicator': PN4_YEAR_INDICATOR_ORDER[2],
         'Active point': ((current or {}).get('partner_from', '-') if segments is not None and current
                          else '-'),
         'Ruler': (((current or {}).get('partner') or 'none -- the distributor alone')
                   if segments is not None and current else '-'),
         'Source': 'III.1, 15-16, 23-25'},
        {'#': 4, 'Indicator': PN4_YEAR_INDICATOR_ORDER[3],
         'Active point': (f"{elapsed:.2f} years elapsed: cycle {fardar['cycle']}, year "
                          f"{elapsed % PN4_FARDAR_CYCLE_YEARS:.2f} of 75" if fardar else '-'),
         'Ruler': (f"{fardar['lord']}" + (f" / {fardar['sub_lord']}" if fardar['sub_lord'] else " (no sub-period)")) if fardar else '-',
         'Source': 'IV.1, 2-8; II.1, 9'},
    ]

    # --- VI.1: the lord of the orb, indicator #5 (II.1, 10) ---
    natal_hour_lord = (chronocrats or {}).get('Hour Lord')
    hour_approximate = bool((chronocrats or {}).get('Approximate'))
    orb = pn4_lord_of_the_orb(natal_hour_lord, age)
    orb_rows = pn4_named_lords_of_the_orb(natal_hour_lord, age)
    year_rows.append({
        '#': 5, 'Indicator': PN4_YEAR_INDICATOR_ORDER[4],
        'Active point': (f"hour {age % 7 + 1} of 7 from the natal hour lord ({natal_hour_lord}"
                         f"{', by equal hours -- approximate' if hour_approximate else ''}); "
                         f"cycle {age // 12 + 1} of the profection" if orb else 'natal hour lord unavailable'),
        'Ruler': orb or '-',
        'Source': 'VI.1, 4-8; II.1, 10',
    })

    # --- The fardar cycle (IV.1, 2-8; IV.7, 24-25) ---
    fardar_rows, start = [], 0.0
    for lord, years in pn4_fardar_sequence(chart_data['sect']):
        subs = pn4_fardar_subperiods(lord, years)
        fardar_rows.append({
            'Lord': lord, 'Years': int(years),
            'From age': f"{start:g}", 'To age': f"{start + years:g}",
            'Sub-periods': ', '.join(s[0] for s in subs) if subs
                           else 'none -- "they do not have houses" (IV.1, 8)',
            'Active': 'yes' if fardar and fardar['lord'] == lord and fardar['cycle'] >= 1
                      and start <= (elapsed % PN4_FARDAR_CYCLE_YEARS) < start + years else '',
        })
        start += years

    # --- The seven monthly indicators (IX.1, 35-39) ---
    indicators = pn4_monthly_indicators(
        month, age, year['longitude'], chart_data['lot_of_fortune'],
        sr['ascendant'], sr['lot_of_fortune'], mr['ascendant'], mr['lot_of_fortune'], rule)
    monthly_rows = [{
        '#': row['number'], 'Indicator': row['name'],
        'Rooted': 'yes' if row['rooted'] else 'no',
        'Sign': row['sign'], 'Lord': row['lord'], 'Turned': row['direction'],
        'In the root': f"House {get_wsh_house(row['longitude'], ascendant)}",
    } for row in indicators]

    # --- Ages of Man (I.8, 10-26) ---
    age_rows, start = [], 0
    for planet, years, label in PN4_AGES_OF_MAN:
        last = planet == PN4_AGES_OF_MAN[-1][0]
        age_rows.append({
            'Planet': planet, 'Years': years,
            'Ages': f"{start}-{start + years - 1}" if not last else f"{start} onward",
            'Period of life': label,
            'Active': 'yes' if ages and ages['planet'] == planet else '',
        })
        start += years

    # --- III.7, 32-42: when each natal indication comes out ---
    activation_rows = pn4_activation_ages(
        chart_data['planetary_data'], chart_data['obliquity'], lat, segments)

    # --- the distributions, as forward tables (III.1, 11-16) ---
    distribution_rows = _pn4_distribution_rows(segments, current, origin_jd=chart_data['julian_day'])
    meridian_rows = {point: _pn4_distribution_rows(m['segments'], m['current'], origin_jd=chart_data['julian_day'])
                     for point, m in meridian.items()}

    # --- IX.7, 29-31: the small days, in days from the revolution ---
    small_days = pn4_small_days(sr['planetary_data'], sr['ascendant'])
    day_of_year = jd_target - jd_sr
    small_days_current = pn4_distribution_at_age(small_days, day_of_year)
    small_days_rows = _pn4_distribution_rows(small_days, small_days_current, unit='days', origin_jd=jd_sr)

    # --- II.22, 1-4: the Moon's connections in her sign, and the portions ---
    moon = pn4_moon_connections(sr['planetary_data'], jd_sr)
    year_days = jd_sr_next - jd_sr
    portions = pn4_moon_portions(moon['connections'], year_days)

    # --- SAHL: the releaser (On Nativities 1.15-1.16, 1.20), its distribution
    # (1.15, 22; 1.18, 20-21) and the house-master directed (1.23, 2) ---
    syzygies = sahl_prenatal_meeting_and_fullness(chart_data['julian_day'], lat, lon)
    releaser = sahl_releaser(chart_data['planetary_data'], ascendant, chart_data['houses'], chart_data['sect'],
                             chart_data['lot_of_fortune'], syzygies['meeting']['longitude'],
                             syzygies['fullness']['longitude'])
    releaser_segments = sahl_releaser_distribution(chart_data['planetary_data'], releaser['longitude'],
                                                   chart_data['obliquity'], lat)
    releaser_current = pn4_distribution_at_age(releaser_segments, elapsed) if releaser_segments else None
    releaser_rows = _pn4_distribution_rows(releaser_segments, releaser_current, origin_jd=chart_data['julian_day'])
    if releaser['longitude'] is None:
        releaser_note = 'no releaser by On Nativities 1.15 (the releaser section)'
    elif releaser_segments is None:
        releaser_note = 'refused above the polar circle'
    elif releaser_current is None:
        releaser_note = f"age {age} is past the {PN4_DISTRIBUTION_SPAN_YEARS:g}-year table"
    else:
        releaser_note = None
    releaser_stand = None
    if releaser_current:
        _deg = _pn4_seg_degree(releaser_current, releaser['longitude'], chart_data, lat)
        releaser_stand = {'distributor': releaser_current['distributor'], 'partner': releaser_current['partner'],
                          'sign': get_zodiac_sign(_deg), 'lord': SIGN_TO_DOMICILE.get(get_zodiac_sign(_deg), '-'),
                          'degree': _deg, 'note': None}
    # FINAL-A7: in the empty case the Moon is directed after the Ascendant
    # (1.32, 11-13), by the same operation as the house-master's.
    standin_moon = (sahl_house_master_direction(chart_data['planetary_data'], 'Moon', chart_data['obliquity'], lat,
                                                origin_jd=chart_data['julian_day'])
                    if releaser['releaser'] is None else None)
    house_master = releaser['house_master']
    hm_direction = sahl_house_master_direction(chart_data['planetary_data'], house_master, chart_data['obliquity'],
                                               lat, origin_jd=chart_data['julian_day']) if house_master else None
    hm_this_year = [r for r in (hm_direction or []) if r['In the year of age'] == age]
    hm_revolution = sahl_house_master_in_revolution(house_master, chart_data, sr) if house_master else []
    hm_flags = sahl_house_master_flags(house_master, chart_data['planetary_data'], chart_data['houses'])

    # --- II.13, 1; II.14, 1; II.22, 1-5: the luminary proxies ---
    sun = pn4_sun_handover(sr['planetary_data'], jd_sr) if year['lord'] == 'Sun' else None
    proxies = pn4_luminary_proxies(year['lord'], chart_data, sr, moon, sun,
                                   releaser_stand or {'note': releaser_note})

    # --- IX.7, 23-28: the mighty days, the terminal degree through the SR ---
    mighty_days = pn4_mighty_days(sr['planetary_data'], year['longitude'])
    mighty_days_current = pn4_distribution_at_age(mighty_days, day_of_year)
    mighty_days_rows = _pn4_distribution_rows(mighty_days, mighty_days_current, unit='days', origin_jd=jd_sr)

    return {
        'activation_rows': activation_rows,
        'distribution_rows': distribution_rows,
        'meridian': meridian, 'meridian_rows': meridian_rows,
        'small_days': small_days, 'small_days_current': small_days_current,
        'small_days_rows': small_days_rows, 'day_of_year': day_of_year,
        'mighty_days': mighty_days, 'mighty_days_current': mighty_days_current,
        'mighty_days_rows': mighty_days_rows,
        'orb': orb, 'orb_rows': orb_rows, 'natal_hour_lord': natal_hour_lord,
        'hour_approximate': hour_approximate,
        'turning_rows': pn4_turning_rows(chart_data, age),
        'further_rows': pn4_further_indicators(chart_data, sr, year['longitude'], moon),
        'governor': pn4_governor(
            year['lord'], (current or {}).get('distributor'), (current or {}).get('partner'),
            ('refused above the polar circle' if segments is None
             else f"age {age} is past the {PN4_DISTRIBUTION_SPAN_YEARS:g}-year table"),
            (fardar or {}).get('lord'), orb, sr['ascendant'],
            pn4_moon_testimony(moon), moon['void'],
            (releaser_stand or {}).get('distributor'), (releaser_stand or {}).get('partner'), releaser_note),
        'moon': moon, 'moon_portions': portions, 'year_days': year_days,
        'proxies': proxies, 'sun_handover': sun,
        'syzygies': syzygies, 'releaser': releaser, 'releaser_segments': releaser_segments,
        'releaser_current': releaser_current, 'releaser_rows': releaser_rows, 'releaser_note': releaser_note,
        'releaser_stand': releaser_stand, 'house_master': house_master, 'hm_direction': hm_direction,
        'hm_this_year': hm_this_year, 'hm_revolution': hm_revolution, 'hm_flags': hm_flags,
        'standin_moon': standin_moon,
        'hm_turning': sahl_house_master_turning(house_master, chart_data['planetary_data']) if house_master else [],
        'ii3': pn4_ii3_examination(chart_data, sr, year, jd_sr),
        'iii2_type': pn4_static_type(current['distributor'], current['partner']) if current else None,
        'iii2_checklist': pn4_distribution_checklist(chart_data, sr, year['longitude'], current),
        'iii2_transitions': pn4_year_transitions(segments, age),
        'bound_transits': pn4_bound_transits(chart_data, sr, current, year['lord']) if current else None,
        'image': pn4_revolution_image(chart_data, sr, year, age, current, fardar, orb, lat, elapsed=elapsed),
        'i7_ascendant': pn4_i7_ascendant(chart_data, sr),
        'i7_planets': pn4_i7_planets(chart_data, sr),
        'day_methods': pn4_day_methods(
            chart_data['julian_day'], jd_sr, jd_mr, jd_target, ascendant, sr['ascendant'], orb, year['sign'],
            [(f"#{r['number']} {r['name']}", r['longitude']) for r in indicators if r['number'] in (1, 3, 4, 5)]
            + [("the month's Ascendant", mr['ascendant']), ("the month's Lot of Fortune", mr['lot_of_fortune']),
               ("the month's Moon", mr['planetary_data']['Moon']['longitude'])],
            sr['planetary_data']['Moon']['longitude']),
        'moon_rows': [{'Day from the revolution': f"{c['day']:.2f}", 'Planet': c['planet'], 'By': c['aspect'],
                       'Moon at': get_degree_string(c['moon_at'])} for c in moon['connections']],
        'portion_rows': [{'Portion': f"{p['portion']} of {p['of']}", 'Owned by': p['planet'],
                          'From day': f"{p['from_day']:.1f}", 'To day': f"{p['to_day']:.1f}"} for p in portions],
        'first_month_governor': pn4_first_month_governor(
            ascendant, chart_data['lot_of_fortune'], year['longitude'], sr['ascendant'], sr['lot_of_fortune']),
        'age': age, 'cycle': cycle, 'elapsed_years': elapsed,
        'month': month, 'jd_sr': jd_sr, 'jd_sr_next': jd_sr_next, 'jd_mr': jd_mr, 'jd_target': jd_target,
        'sr': sr, 'mr': mr, 'year': year, 'ninth': ninth, 'fardar': fardar,
        'segments': segments, 'current': current, 'ages': ages,
        'revolution_rows': revolution_rows, 'year_rows': year_rows,
        'fardar_rows': fardar_rows, 'monthly_rows': monthly_rows, 'age_rows': age_rows,
        'monthly_indicators': indicators,
    }

def calculate_time_lords(ascendant_lon, birth_date, target_date):
    """Annual Profection (Lord of the Year) and a symbolic 1-degree-per-year
    direction of the Ascendant through the Egyptian bounds.

    The second of these was previously called a "Ptolemaic Distribution."
    It is not one -- see the note on the row it returns."""
    # Age in COMPLETED CIVIL ANNIVERSARIES, not elapsed days over a mean
    # year length. Profection turns on the birthday: dividing by 365.2425
    # let the sign advance up to a day early or late around it, and drifts
    # further the older the native is.
    days_alive = (civil_to_jd(target_date.year, target_date.month, target_date.day)
                  - civil_to_jd(birth_date.year, birth_date.month, birth_date.day))
    integer_age = target_date.year - birth_date.year
    if (target_date.month, target_date.day) < (birth_date.month, birth_date.day):
        integer_age -= 1
    integer_age = max(integer_age, 0)
    fractional_age = days_alive / 365.2425

    # --- Annual Profection ---------------------------------------------
    natal_sign_idx = int(ascendant_lon // 30)
    profected_sign_idx = (natal_sign_idx + integer_age) % 12
    profected_sign = get_zodiac_sign(profected_sign_idx * 30.0 + 15.0)  # mid-sign probe
    lord_of_year = SIGN_TO_DOMICILE.get(profected_sign, '-')

    # --- Distribution (Ptolemaic Egyptian Terms) ------------------------
    directed_asc_lon = (ascendant_lon + fractional_age) % 360.0
    directed_sign = get_zodiac_sign(directed_asc_lon)
    degree_in_sign = directed_asc_lon % 30.0
    distributor = next((lord for limit, lord in EGYPTIAN_TERMS.get(directed_sign, []) if degree_in_sign < limit), '-')

    return [
        {
            'Technique': 'Annual Profection',
            'Active Point': profected_sign,
            'Active Ruler': lord_of_year,
            'Details': f"Age {integer_age} (1 Sign / Year)",
        },
        {
            # NOT a distribution in either Sahl's or Ptolemy's sense, and no
            # longer labelled as one. Real distribution directs a releaser
            # through the bounds by PRIMARY motion, in ascensional degrees
            # for the birth latitude, and names both a distributor (the
            # bound lord) and a partner (the body or ray met on the way) --
            # Sahl, On Nativities Ch.2.13, 48-51 grades the result in three
            # 15-degree ascensional bands. Advancing zodiacal longitude at a
            # flat 1 degree per year is the schoolbook shortcut for that; it
            # reaches a different bound whenever the ascensions of the sign
            # in question are not 1 degree per year, which is most of the
            # time away from the equator.
            'Technique': 'Symbolic direction (1\u00b0/yr, NOT a distribution)',
            'Active Point': f"{get_degree_string(directed_asc_lon)}",
            'Active Ruler': distributor,
            'Details': "Egyptian bound of the symbolically directed Asc",
        },
    ]

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
# reading depth on the Sources page, which folds the supplement.

st.sidebar.header("Nativity")

if "saved_charts" not in st.session_state:
    st.session_state["saved_charts"] = load_saved_charts()

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

def _apply_selected_chart():
    """on_change callback: runs before the script reruns, so writing into
    these session_state keys here makes the widgets below pick up the
    loaded values on this same rerun. The chart loaded becomes the one the
    app opens on next time (preference 'last_chart', 2026-09-10)."""
    name = st.session_state.get("chart_picker")
    if name and name != "-- New Chart --":
        _restore_chart(name)
        _remember('last_chart', name)

def _restore_chart(name):
    """Write a saved chart's fields into the sidebar widgets' keys."""
    if True:
        entry = st.session_state["saved_charts"].get(name, {})
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
        if entry.get("utc_offset") is not None:
            st.session_state["utc_offset_key"] = float(entry["utc_offset"])
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
                    st.session_state[key] = int(entry["target_age"])
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
            st.session_state["manual_coords_key"] = True
            st.session_state["manual_lat_key"] = entry["lat"]
            st.session_state["manual_lon_key"] = entry["lon"]
            st.session_state["loaded_location"] = {
                "lat": entry["lat"],
                "lon": entry["lon"],
                "label": entry.get("location_query", ""),
            }
        elif "location_query" in entry:
            # Saved before lat/lon capture was added -- best effort only,
            # since atlas.db matching needs a raw city name, not the old
            # free-text/resolved-label value this field used to hold.
            st.session_state["manual_coords_key"] = False
            st.session_state["location_input_key"] = entry["location_query"]

chart_options = ["-- New Chart --"] + sorted(st.session_state["saved_charts"].keys())
# The app opens on the chart it was last working on (owner's decision
# 2026-09-10), unless something has already seeded the sidebar -- the
# harness does, and a fresh session has not.
if "_autoload_done" not in st.session_state:
    st.session_state["_autoload_done"] = True
    _last = st.session_state["_prefs"].get('last_chart')
    if _last in st.session_state["saved_charts"] and "date_input_key" not in st.session_state:
        st.session_state["chart_picker"] = _last
        _restore_chart(_last)
load_col, del_col = st.sidebar.columns([3, 1])
load_col.selectbox("\U0001F4C2 Load saved chart", chart_options, key="chart_picker", on_change=_apply_selected_chart)
if del_col.button("\U0001F5D1", help="Delete the selected saved chart"):
    picked = st.session_state.get("chart_picker")
    if picked and picked != "-- New Chart --" and picked in st.session_state["saved_charts"]:
        del st.session_state["saved_charts"][picked]
        write_saved_charts(st.session_state["saved_charts"])
        if st.session_state["_prefs"].get('last_chart') == picked:
            _forget('last_chart')
        st.rerun()

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
date_string = st.sidebar.text_input(
    "Date (YYYY-MM-DD)", "1240-05-23", key="date_input_key",
    help="The civil date of birth. Before 1582-10-15 the digits are read as a JULIAN-calendar date, "
         "as Solar Fire and astro.com read them; from that day on, Gregorian. Years before 1000 "
         "are typed with their leading zeros (0787-08-10).")
_parsed = parse_iso_date(date_string)
if _parsed is None:
    input_date = st.session_state.get("_date_last_good", CivilDate(1240, 5, 23))
    st.sidebar.error(f"Date must be YYYY-MM-DD, e.g. 1240-05-23. Showing {input_date:%Y-%m-%d}.")
else:
    input_date = _parsed
    st.session_state["_date_last_good"] = input_date
_cal_note = ("Julian calendar (before the reform of 1582-10-15)"
             if (input_date.year, input_date.month, input_date.day) < (1582, 10, 15) else "Gregorian calendar")

# To the second: the engine reads seconds, and a rectified time has them.
input_time = st.sidebar.time_input("Time", time(14, 30), key="time_input_key", step=timedelta(seconds=1))

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
    utc_offset_manual = st.sidebar.number_input(
        "UTC offset (hours, east positive)", min_value=-14.0, max_value=14.0, value=0.0, step=0.25,
        format="%.2f", key="utc_offset_key")
time_standard_box = st.sidebar.empty()
time_standard_box.caption(_cal_note)
if st.session_state.get("_loaded_without_standard"):
    st.sidebar.warning(f"'{st.session_state['_loaded_without_standard']}' was saved before the time "
                       "standard was stored with a chart. Check it, then save the chart again.")

st.sidebar.header("Birthplace")

# One control in effect (evaluation A.3): the search box also accepts a
# typed "latitude, longitude" pair; the toggle exposes the coordinate
# fields themselves, which is also how a saved chart is restored (the
# loader writes these three keys, as the harness does).
manual_coords = st.sidebar.toggle("Enter coordinates directly", key="manual_coords_key",
                                  help="Or type them into the search box as 'latitude, longitude'.")

if manual_coords:
    lat = st.sidebar.number_input("Latitude", value=43.7698, format="%.4f", key="manual_lat_key")
    lon = st.sidebar.number_input("Longitude", value=11.2556, format="%.4f", key="manual_lon_key")
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
    default_loc = st.session_state.get('location_input_key', 'Florence')
    city_search = st.sidebar.text_input("City, or latitude, longitude", default_loc, key="location_input_key",
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
                st.sidebar.warning("No matches found in offline atlas.")
                lat, lon, location_query = None, None, None
        else:
            st.sidebar.error("`atlas.db` not found. Please ensure it is in the root directory.")
            lat, lon, location_query = None, None, None
    else:
        lat, lon, location_query = None, None, None
location_box = st.sidebar.empty()

# --- The target of the Timing page: an age or a date -----------------------
# Set on the Timing page, where it is used (the owner's instinct, 2026-09-10),
# and remembered in store keys like the readings; read here because the
# bundle below is computed before the page runs. "Age 42" is the 42nd
# birthday; a date shows its completed years beside it on the page. Saved
# with the chart.
_today = CivilDate.of(datetime.now().date())
target_mode = _reading("target_mode", "_target_mode", TARGET_MODE_OPTIONS[0])
_date_target = parse_iso_date(_reading("target_date", "_target_date", _today.isoformat())) or _today
if target_mode == TARGET_MODE_OPTIONS[1]:
    target_age = max(0, int(_reading("target_age", "_target_age", pn4_completed_years(input_date, _date_target))))
    target_date = pn4_birthday(input_date, target_age)
    # The other reading follows, so switching the mode carries the target over.
    st.session_state["_target_date"] = target_date.isoformat()
else:
    target_date = _date_target
    target_age = pn4_completed_years(input_date, target_date)
    st.session_state["_target_age"] = target_age

new_chart_name = st.sidebar.text_input("Chart name (for saving)", value="", placeholder="e.g. Test Chart 1240")
if st.sidebar.button("\U0001F4BE Save this chart"):
    trimmed_name = new_chart_name.strip()
    if trimmed_name:
        st.session_state["saved_charts"][trimmed_name] = {
            "date_string": date_string,
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
        if write_saved_charts(st.session_state["saved_charts"]):
            st.session_state.pop("_loaded_without_standard", None)
            _remember('last_chart', trimmed_name)
            st.sidebar.success(f"Saved '{trimmed_name}'.")
        else:
            st.sidebar.error("Could not write saved_charts.json to disk.")
    else:
        st.sidebar.warning("Enter a name before saving.")

CONNECTION_PROFILE = _reading("connection_rule", "_connection_rule", "Sahl")
EASTERN_RULE = _reading("eastern_rule", "_eastern_rule", EASTERN_RULE_OPTIONS[0])
MOON_RAYS_ORB = 15.0 if _reading("moon_rays_15", "_moon_rays_15", False) else 12.0
MARS_WEST_RAYS_18 = bool(_reading("mars_west_18", "_mars_west_18", False))
FITTING_INFORTUNE = bool(_reading("fitting_infortune", "_fitting_infortune", False))
DOMAIN_RULE = _reading("domain_rule", "_domain_rule", DOMAIN_RULE_OPTIONS[0])
LOT_HOUSE_CUSP = _reading("lot_house_cusp", "_lot_house_cusp", LOT_HOUSE_CUSP_OPTIONS[0])
# Owner's decision 2026-09-10: ship Abu Ma'shar's quadruplicity turn (IX.1, 26-34)
# as a reading, defaulting to Dykes' plain forward count. Read only by the
# Timing page, so it is not in the Configurations cross-product.
PN4_MONTHLY_TURN = _reading("pn4_monthly_turn", "_pn4_monthly_turn", PN4_MONTHLY_TURN_OPTIONS[0])
# Owner's decision 2026-09-10: the natal wheel carries the Egyptian-bounds
# ring too, as every PN IV wheel does -- the course works the bounds by hand.
CHART_BOUNDS = bool(_reading("chart_bounds", "_chart_bounds", True))
# The reading depth (UI_REVIEW_2026-09-10.md §1 B): the course text alone,
# or with Abu Ma'shar's supplement laid beside it. Set on the Sources page.
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
    ("Reading depth", "reading_depth", "_reading_depth", READING_DEPTH_OPTIONS[0], "Sources and readings"),
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
    off = [(l, v) for l, v in _readings_off_default() if l != "Reading depth"]
    if off:
        st.caption("Readings in force that differ from the course defaults: "
                   + "; ".join(f"{l} = {v}" for l, v in off)
                   + ". They are remembered between runs; see Sources and readings to reset them.")


if location_query and lat is not None and lon is not None:
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
            try:
                _local_py = datetime(local_dt.year, local_dt.month, local_dt.day,
                                     local_dt.hour, local_dt.minute, local_dt.second)
            except ValueError:
                time_standard_box.error(
                    f"**{local_dt:%Y-%m-%d}** is a Julian-calendar date that no standard-time zone can "
                    "place. Choose LMT or a manual offset."
                )
                st.stop()
            # is_dst=None makes pytz RAISE on the two clock times a named
            # zone cannot resolve on its own: the hour that occurs twice at
            # a DST fall-back, and the hour that never occurs at spring
            # forward. Without it pytz silently picks one, which moves the
            # chart by an hour with no indication that a choice was made.
            try:
                localized_dt = local_tz.localize(_local_py, is_dst=None)
            except pytz.exceptions.AmbiguousTimeError:
                time_standard_box.error(
                    f"**{local_dt:%Y-%m-%d %H:%M}** happens twice in {tz_name} "
                    "(daylight-saving fall-back). Choose LMT or a manual offset, or enter a time "
                    "outside the repeated hour."
                )
                st.stop()
            except pytz.exceptions.NonExistentTimeError:
                time_standard_box.error(
                    f"**{local_dt:%Y-%m-%d %H:%M}** does not exist in {tz_name} "
                    "(the clocks jump over it at daylight-saving spring-forward). "
                    "Check the recorded time."
                )
                st.stop()
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
    location_box.success(f"**{escape(str(location_query))}**  \n{lat:.4f}, {lon:.4f}{zone_note}")

    if tz_name:
        chart_data = calculate_traditional_chart_jd(jd_ut, lat, lon)
        p_data = chart_data['planetary_data']
        sect = chart_data['sect']
        # D-13: named here, before any evaluator runs, since they read it.
        SOFTENED_INFORTUNE = fitting_infortune(chart_data['ascendant']) if FITTING_INFORTUNE else None

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
        # The cached function takes the local HOUR (an int Streamlit can
        # hash), not the CivilMoment; it reads nothing else of it.
        chronocrats = calculate_chronocrats(chart_data['julian_day'], lat, lon, local_dt.hour, utc_offset_hours)
        classical_lots = calculate_classical_lots(chart_data['ascendant'], p_data['Sun']['longitude'], p_data['Moon']['longitude'], sect)
        topical_lots = calculate_topical_lots(p_data, chart_data['ascendant'], chart_data['houses'], sect)
        special_degrees = evaluate_special_degrees(p_data)
        book_v_degrees_data = evaluate_book_v_degrees(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'], sect)
        rays_by_ascension_data = evaluate_rays_by_ascension(p_data, chart_data['armc'], chart_data['obliquity'], lat)
        house_lords_data = evaluate_house_lords(p_data, chart_data['ascendant'])
        victors_data = evaluate_victors(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'],
                                         syzygy['syzygy_longitude'], sect, chronocrats)
        planets_in_houses_data = evaluate_planets_in_houses(p_data, abu_mashar_condition, chart_data['ascendant'])
        time_lords_data = calculate_time_lords(chart_data['ascendant'], input_date, target_date)
        planetary_years_data = evaluate_planetary_years_display(p_data, chart_data['houses'], chart_data['ascendant'], sect, essential)
        pn4 = pn4_timing_bundle(chart_data, lat, lon, input_date, target_date, PN4_MONTHLY_TURN, chronocrats)

        # The hub names the chart: the saved chart picked in the sidebar, else
        # the name typed for saving, else "Transits" (owner's decision D5,
        # 2026-09-07: an unnamed chart cast for a date is a transit chart).
        # Loading a saved chart and then editing its date keeps the saved
        # name; accepted. Both wheel layouts are built here, since the page
        # picks one with a control of its own and the strings are cheap.
        _picked = st.session_state.get("chart_picker")
        chart_name = (_picked if _picked and _picked != "-- New Chart --"
                      else new_chart_name.strip() or "Transits")
        svg_code = generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, local_dt, tz_name,
                                       chronocrats=chronocrats, bounds=CHART_BOUNDS)
        svg_wide = generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, local_dt, tz_name,
                                       wide=True, chronocrats=chronocrats, bounds=CHART_BOUNDS)

        st.title("Traditional Astrology Engine")

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
        # A finding with nothing to report is not given a heading at all --
        # it is collected and named in one line at the foot of its group,
        # which is what turns seventeen "No X found" headings into four.
        def _finding(bucket, title, citation, data, glance=None, notes=None, columns=None, height=None):
            if not data:
                bucket.append(title)
                return
            st.subheader(title, help=glance)
            if citation:
                st.caption(citation)
            # columns= pins the order (pandas otherwise takes the first
            # row's); height= shows every row of a table meant to be read
            # whole, instead of st.dataframe's ten-row inner scroll.
            st.dataframe(pd.DataFrame(data, columns=columns), hide_index=True, width='stretch',
                         **({'height': height} if height is not None else {}))
            if notes:
                with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                    st.markdown(notes)

        def _absent(bucket):
            if bucket:
                st.caption("Not present in this chart: " + ", ".join(bucket) + ".")
                del bucket[:]

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

        def _reading_radio(label, options, widget_key, store_key, help=None):
            options = list(options)
            stored = st.session_state.get(store_key, options[0])
            st.radio(label, options, index=options.index(stored) if stored in options else 0,
                     key=widget_key, horizontal=True, help=help)
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
            st.dataframe(pd.DataFrame(grid), hide_index=True, width='stretch', height=_rows_height(len(grid)))
            with st.expander("Answer key: testimonies in words"):
                st.dataframe(pd.DataFrame(data, columns=['Planet', text_key, 'Count']),
                             hide_index=True, width='stretch', height=_rows_height(len(data)))
            if notes:
                with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                    st.markdown(notes)

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
            st.header("Chart")
            st.caption("Lessons 3-5: chart identification, measurement, astronomy.")
            _readings_note()
            _gap = []
            # Looking at the chart is the primary act, so the wheel comes first.
            # st.image shows the SVG through Streamlit's own fullscreen wrapper,
            # the same expand arrows the tables carry; the iframe it replaced
            # (2026-09-07) had none. The square wheel keeps the 400 px measured
            # on 2026-09-06 as the most that is fully visible on load at
            # 1280x720, with the orientation text and header metrics beside
            # it; the wide variant runs the full page width and scrolls, and
            # is there for the full-window view, which a square can only fill
            # to the window's height.
            #
            # The layout is read from the control's state BEFORE the control
            # is drawn, so the control can sit beside the square wheel rather
            # than above it (a row above the wheel pushed its foot 24 px below
            # the fold at 1280x720). The widget key holds the new value from
            # the start of the rerun that a click causes; the store key keeps
            # it across pages.
            def _layout_control():
                st.session_state.setdefault("_chart_bounds", True)
                layout = _reading_radio(
                    "Wheel layout", WHEEL_LAYOUT_OPTIONS, "wheel_layout", "_wheel_layout",
                    help="Square: the wheel beside the header metrics. Wide: the wheel with a "
                         "positions panel across the page. Hover either and use the expand "
                         "arrows for a full-window view.")
                _reading_checkbox("Bounds ring", "chart_bounds", "_chart_bounds",
                                  help="The Egyptian bounds, with their lords, as a ring inside the degree scale -- "
                                       "as every natal wheel in Persian Nativities IV carries them (Figures 1, 22, "
                                       "25, 26). Owner's choice, 2026-09-10.")
                st.download_button("Download the wheel (SVG)", svg_wide if layout == WHEEL_LAYOUT_OPTIONS[1] else svg_code,
                                   key="dl_chart_wheel", mime="image/svg+xml",
                                   file_name=f"{re.sub(r'[^A-Za-z0-9]+', '_', chart_name).strip('_') or 'chart'}_natal.svg")
                return layout
            wheel_layout = st.session_state.get(
                "wheel_layout", st.session_state.get("_wheel_layout", WHEEL_LAYOUT_OPTIONS[0]))
            if wheel_layout == WHEEL_LAYOUT_OPTIONS[1]:
                _layout_control()
                st.image(svg_wide, width='stretch')
                side_col = st.container()
            else:
                wheel_col, side_col = st.columns([1, 1])
                with wheel_col:
                    st.image(svg_code, width=400)
                with side_col:
                    _layout_control()
            with side_col:
                st.caption(
                    "A TNAC study companion: work the homework by hand, then check it here and "
                    "see the doctrine applied to a real chart.  \n"
                    "Enter a chart in the sidebar; saved charts load from the top of it.  \n"
                    "Pages follow the course's lesson order. Sahl's *Introduction* is the course "
                    "text; Abu Ma'shar's *Great Introduction* VII is the supplement."
                )
            # The four header metrics run in one row under the wheel, the full
            # page width (owner, 2026-09-07: stacked beside the wheel they left
            # the right-hand column mostly empty). The lunation column is
            # wider because its value is a long word: "Conjunctional" at the
            # metric size needs about 260 px, and an even quarter of the page
            # at 1280 px is less than that.
            hdr1, hdr2, hdr3, hdr4 = st.columns([1.5, 1, 1, 1])
            # Lesson 5 asks "conjunctional or preventional?"; the full
            # syzygy table stays on the victors page, gated at Lesson 19.
            # The label is "Preventional (Full Moon)": the first word is
            # the metric, the rest goes in the caption with the position
            # and place, since the value would otherwise be cut off.
            _event, _, _kind = syzygy['event_label'].partition(' ')
            hdr1.metric("Prenatal lunation", _event)
            hdr1.caption(f"{_kind} at {get_degree_string(syzygy['syzygy_longitude'])} · House {syzygy['natal_house']}")
            hdr2.metric("Sect", sect)
            hdr3.metric("Lord of the Day", chronocrats['Day Lord'])
            hdr4.metric("Lord of the Hour", chronocrats['Hour Lord'])
            if chronocrats.get('Approximate'):
                st.caption(
                    "⚠️ **The Lord of the Hour here is not a temporal hour.** No sunrise "
                    "or sunset exists for this date at this location (circumpolar day or night), and "
                    "the temporal hour is *defined* by the interval between them — so it has no "
                    "value at all, and no source in hand contemplates the case. What is shown is an "
                    "explicitly modern approximation: the civil day divided into 24 equal hours, "
                    "continuing the same Chaldean cycle. The Lord of the Day is still exact."
                )
            # The Lesson 5 worksheet's intermediate lines, so a hand
            # calculation can be checked line by line rather than only at
            # the Ascendant. GST is the Greenwich sidereal time at the UT of
            # birth; LST adds the longitude in hours; RAMC is the right
            # ascension of the meridian from the same swe.houses call that
            # produced the cusps.
            st.subheader('Calculation', help="The Lesson 5 worksheet's intermediate quantities, in the worksheet's order, so each line of a hand calculation can be checked against the app.")
            gst_hours = swe.sidtime(chart_data['julian_day'])
            lst_hours = (gst_hours + lon / 15.0) % 24.0
            calc_rows = [
                {"Quantity": "Local time", "Value": f"{local_dt:%Y-%m-%d %H:%M:%S}"},
                {"Quantity": "Time standard", "Value": tz_name},
                {"Quantity": "Universal time (line 8)", "Value": f"{dt_utc:%Y-%m-%d %H:%M:%S} UT"},
                {"Quantity": "Julian Day", "Value": f"{chart_data['julian_day']:.4f}"},
                {"Quantity": "Greenwich sidereal time at birth (line 11)", "Value": _hms(gst_hours)},
                {"Quantity": "Local sidereal time (line 13)", "Value": _hms(lst_hours)},
                {"Quantity": "RAMC (line 14)", "Value": _dms(chart_data['armc'])},
                {"Quantity": "Obliquity of the ecliptic (line 15)", "Value": _dms(chart_data['obliquity'])},
                {"Quantity": "MC", "Value": get_degree_string(chart_data['mc'])},
                {"Quantity": "Ascendant", "Value": get_degree_string(chart_data['ascendant'])},
            ]
            st.dataframe(pd.DataFrame(calc_rows), hide_index=True, width='content')
            st.caption("Matches the Lesson 5 worksheet: lines 8, 11, 13, 14, 15 and Step 2–3 results.")
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
                                       "(Weakness 93, Planetary Condition 27/34/45). Decision D-15.")
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
            st.dataframe(pd.DataFrame(pos_list), hide_index=True, width='stretch')
            st.caption("Quadrant column: Alchabitius house, advancing or retreating in Sahl's sense "
                       "(The Introduction Ch.3, 4-5): stake or succedent versus falling. "
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
                st.subheader('Quadrant divisions (Alchabitius)', help='The twelve quadrant house cusps computed by the Alchabitius (semi-arc) system -- shown alongside the Whole-Sign houses used everywhere else in this app, since some techniques call for quadrant division specifically.')
                house_list = [{"House": i+1, "Cusp": get_degree_string(chart_data['houses'][i])} for i in range(12)]
                st.dataframe(pd.DataFrame(house_list), hide_index=True, width='content', height=_rows_height(12))
            _finding(_gap, 'Special Degrees & Conditions', None, special_degrees,
                      glance='Flags planets in Sahl\'s dark signs (Libra, Capricorn), in the two signs of his burned place ("the end of Libra and the beginning of Scorpio" -- he gives no degrees; Abu Ma\'shar\'s 19 Libra-3 Scorpio is applied only in his own Planetary Condition table), in a welled degree of their sign (Abu Ma\'shar, Gr. Intr. V.21, Fig. 62), or in one of Sahl\'s two sign-boundary conditions.',
                      notes='ENTERING: "every planet which is at the beginning of a sign is weak until it is firmly established in it and comes to be 5 degrees within it" (Fifty Aphorisms #44, 87), repeated in On Nativities Ch.1.22, 9. This is the other half of the five-degree rule that also governs advancement.\n\nLEAVING: "if a planet came to be in the last degree of the sign, then its strength has already gone away from that sign, and its strength is in the next sign ... like a man putting his foot on the threshold of his door. And if a planet was in the twenty-ninth degree, then indeed the strength of the planet IS in that sign" (Fifty Aphorisms #15, 31-33) -- so the 29th degree still counts and only the 30th has left.')
            _absent(_gap)
            # The orders of the dignities and the good places -- static tables --
            # moved to the Reference tables page on 2026-09-10; what stays is
            # the one table that reads this chart.
            with st.expander("Sahl's sign categories for this chart's points", icon=":material/menu_book:"):
                st.caption("Where The Introduction and On Nativities disagree, both readings are shown and neither is merged "
                           "(decisions D-7, D-8, D-9). Sources: " + "; ".join(f"{k}: {a} / {b}" for k, (a, b) in SIGN_CATEGORY_SOURCES.items())
                           + ". The orders of the dignities and the good places are on the Reference tables page.")
                cat_rows = []
                for p, d in list(p_data.items()) + [('Ascendant', {'longitude': chart_data['ascendant']})]:
                    if p == 'North Node':
                        continue
                    sign_p = get_zodiac_sign(d['longitude'])
                    cat_rows.append({'Point': p, 'Sign': sign_p, **sign_categories(sign_p)})
                st.dataframe(pd.DataFrame(cat_rows), hide_index=True, width='stretch', height=_rows_height(len(cat_rows)))

        def page_dignities():
            st.header("Dignities and places")
            st.caption("Lessons 9-13: dignities and management, sect, places, lords of places.")
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
                st.dataframe(pd.DataFrame(sect_rows), hide_index=True, width='stretch', height=_rows_height(len(sect_rows)))
            st.caption("Sect: Sahl, The Introduction Ch.3, 85. Domain: Gr. Intr. VII.1, 37 and VII.6, 13 "
                       "(or Masha'allah, On Nativities 1.23, 17, per the switch).")
            st.subheader('Topical Planets in Houses', help="Each planet's Whole-Sign house placement with BOTH Rhetorius/PN4 readings for that pairing, good and bad.")
            st.caption('Rhetorius & PN4')
            st.dataframe(pd.DataFrame(planets_in_houses_data, columns=['Planet', 'Placed in (WS place)', 'Lean']),
                         hide_index=True, width='content', height=_rows_height(len(planets_in_houses_data)))
            # The readings wrap in st.table; the structural columns stay above.
            with st.expander("Rhetorius / PN4 readings for these placements", expanded=READING_DEPTH == READING_DEPTH_OPTIONS[1]):
                st.table(pd.DataFrame(planets_in_houses_data,
                                      columns=['Planet', 'Net', 'Standing', 'If Well Placed', 'If Badly Placed']),
                         hide_index=True)
            with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                st.markdown("Neither is chosen for you. The only thing available to choose with is the Net from the Planetary Condition table, and that number is this app's own arithmetic -- Abu Ma'shar enumerates the VII.6 conditions, never totals them, gives no weighting and no tie rule. An invented score silently picking one of two classical delineations turns a convenience into a verdict.\n\nThe Net is shown as a LEAN instead, and reads Indeterminate within a margin of one, which is the width of a single testimony: those charts sit one label away from the opposite reading, and should be judged on the condition counts and the labels rather than on the number.")
            st.subheader("Topical House Lords (Masha'allah)", help='For each of the twelve topical houses, its domicile lord\'s own Whole-Sign placement, and Masha\'allah\'s delineation for that [placed-in, rules] pairing -- the classical way of reading what a house\'s ruler is "doing" elsewhere in the chart.')
            # Averse: the lord sits in the 2nd, 6th, 8th or 12th sign from the
            # house it rules, so it does not see its own place.
            lords_rows = [{**{k: v for k, v in r.items() if k != "Masha'allah Signification"},
                           'Averse to its place': 'Yes' if (r['Placed in (WS place)'] - r['Topical House']) % 12 in (1, 5, 7, 11) else 'No'}
                          for r in house_lords_data]
            st.dataframe(pd.DataFrame(lords_rows), hide_index=True, width='content', height=_rows_height(len(lords_rows)))
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
            st.header("Configurations")
            st.caption("Lessons 14-17. Sahl's Introduction Ch.2-3 is the course text; "
                       "Abu Ma'shar's Great Introduction VII is supplementary.")
            _readings_note()
            _gap = []
            # The connection rule and the fitting infortune govern tables on every
            # tab, so they stay above the tabs. The three-way view control went on
            # 2026-09-10: the reading depth (Sources page) decides where Abu
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
                                       "94-95; Abu Ma'shar's 3, 47-50 and enclosure; the Moon's 67-68 and 106). Decision D-13.")
            if FITTING_INFORTUNE:
                st.caption(f"Fitting infortune in force: {SOFTENED_INFORTUNE} rules the Ascendant and is not counted as an infortune."
                           if SOFTENED_INFORTUNE else "Fitting infortune switched on, but no malefic rules this Ascendant -- nothing changes.")
            supplement = READING_DEPTH == READING_DEPTH_OPTIONS[1]

            def sahl_aspects():
                _finding(_gap, "Aspects, aversions and connections",
                         f"Sahl, The Introduction Ch.2, 50-60 and Ch.3, 6-21 — {CONNECTION_PROFILE} rule in force", aspects,
                          columns=['Light Planet', 'Aspect', 'Heavy Planet', 'Applying Planet', 'Motion', 'Orientation', 'Exact Orb Dist', 'Bodies', 'Strength', 'Connected', 'Rules differ'], height=_rows_height(len(aspects)),
                          glance='Four separate facts about each pair, kept apart rather than collapsed into one verdict. LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign.',
                          notes='MOTION and EXACT ORB DIST are the degree-to-degree approach. BODIES is whether each planet falls inside the other\'s sphere of power, which is asymmetric because the spheres differ in size: Abu Ma\'shar VII.4, 7 notes that Saturn sits inside the Moon\'s body from 12 degrees while she only enters his at a little under 9. CONNECTED is the active author\'s verdict -- switch the Connection rule at the top of this page to see where they disagree; RULES DIFFER marks the pairs where the two tests disagree.\n\nSTRENGTH is two different measures. For an assembly it is the source\'s own: whose body reaches whose (VII.4, 5-8) and whether they share a bound. For an aspect it is marked "(app scale)", because VII.5, 4 grades looking as a continuum with no cutoffs anywhere -- "the strongest thing there is in its looking is the degree related most closely by number to the degree of its own sign, and if the aspect was far from these degrees, its aspect will be weaker." The thirds are this app\'s own scanning aid; the measurement itself is the Exact Orb Dist column.\n\nLIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.\n\nAPPLYING PLANET is the separate, directed fact: which one is actually closing the aspect. Normally it is the lighter, and Ch.3, 6 assumes as much ("a light, quick star GOING STRAIGHTAWAY TO a heavy star ... FEWER IN DEGREES than the heavy one"). Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma\'shar VII.5, 24 ("the connection of one of them with the other ... will be BY RETROGRADATION"), VII.5, 118 ("the light one IN MORE DEGREES goes retrograde and connects with the heavy one"), and the note on VII.5, 130 (Saturn "could never be received because he is too slow to connect with anyone, UNLESS BY RETROGRADATION"). The cause is named in this column whenever the heavier planet is the one applying, which happens for about 4% of configured pairs. Reception, transfer, collection, returning, revoking, emptiness of course and enclosure all read this column, not the light/heavy one.')

            def sahl_connection_group():
                with st.container(border=True):
                    st.markdown("**Connection group** — Ch.3, 24-30 and 119-123")
                    _finding(_gap, 'Transfer of Light', "Sahl, The Introduction Ch.3, 24-27; Type II is Gr. Intr. VII.5, 84-85", transfers,
                              glance='A faster "carrier" planet separates from one planet and connects with another, carrying the first planet\'s nature to the second -- Type I is a direct hand-off, Type II is via an intermediate planet already connecting onward.')
                    _finding(_gap, 'Collection of Light', 'Sahl, The Introduction Ch.3, 28-30', collections,
                              glance='Two planets not connected to each other both connect with a single heavier planet, which "collects" their combined power -- often read as a third party or authority resolving/mediating between two unconnected significators.')
                    _finding(_gap, 'Enclosure', 'Sahl, The Introduction Ch.3, 119-123', enclosure_data,
                              glance='A planet separating from one of the two infortunes (or, per Abu Ma\'shar\'s extension, fortunes) and connecting with the other, with neither leg intercepted by a third planet\'s rays -- graded "more powerful/unfortunate" when both legs are within 7 degrees of exact.')
                    _absent(_gap)

            def sahl_handing_over():
                with st.container(border=True):
                    st.markdown("**Handing-over group** — Ch.3, 49-76")
                    _finding(_gap, 'Handing Over', 'Sahl, The Introduction Ch.3, 70-76', handing_over_data,
                              glance='Three grades of one phenomenon, per connected pair: Management is the baseline (any connection at all); Power is added when the giving planet is itself in its own house, exaltation, or triplicity; Nature is added when the planet it connects with is the ruler')
                    _finding(_gap, f"Reception — {CONNECTION_PROFILE} rule", None, reception_data,
                              glance='Who receives whom, on what dignity, which way round, and how strongly. The two authors differ on every one of those, so the Connection rule at the top of this page governs here too. Under Sahl\'s rule a pair refused by non-reception Kind II (the connection made from the receiver\'s fall) is not also listed as received -- refusal wins, as on Sahl\'s own chart (Questions Ch. 1, 63 with 40-41) -- and a pair of Kind IV (the receiver in its own fall) keeps its row marked brought down, which is 62\'s own word.',
                              notes='SAHL (Ch.3, 49-55) runs one way only -- the connecting planet stands in a dignity of the planet it connects with, and so is received by it (52: the Moon in Aries connecting with Mars, "he receives her because Aries is his house"). House or exaltation is perfect reception; triplicity alone is expressly ranked below it (50); bound counts only paired with triplicity, which Sahl credits to Masha\'allah (54-55). Face never appears, and a connection is always required.\n\nABU MA\'SHAR (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in REVERSE where the accepting planet sits in the connector\'s dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).\n\nHe then classes reception a SECOND way, and under his rule the table shows both. DIGNITY QUALITY is 129-133, the local basis. OVERALL CLASS is 136-142: "a [2] middling reception is the planets\' reception of each other from the house, exaltation, bound, triplicity, or face" (140) -- house and exaltation included -- while "if two met [together] from this, or each one of them received its associate, it is a strong reception" (141); the natural acceptances of 134-135 are "[3] below that" (142); the Moon received by the Sun (137) and a planet received by Mercury from Virgo (139) are his named strong forms, and the Sun receiving the Moon from the opposition keeps his own word, "detestable" (137). A lone domicile reception is therefore the strongest basis AND globally middling: both are true, and they are different questions.\n\nSahl has two further forms, both under his profile only. 56, RECEPTION AT ONE REMOVE: "if the Moon was connecting with a planet and that planet was connecting with the lord of the house of the Moon or its exaltation, then the Moon is received" -- the note there calls it "like a transfer of light which indirectly allows for reception." Both legs are read in Sahl\'s directed sense of connecting (6: "going straightaway to ... going towards"), since separating is his separate term at 22.\n\n57, AFTER THE SIGN CHANGE: "if the Moon was empty in course, and then she passed over into the next sign and connected with the lord of her first sign, it is JUST LIKE RECEPTION; and if she connected with a planet OTHER than [that], IT UNDERMINES HER." Both halves appear -- the undermining is a finding, not a blank.\n\nAn empty table is NOT non-reception -- that is a separate set of hostile configurations, in the table below.')
                    _finding(_gap, 'Non-reception', 'Sahl, The Introduction Ch.3, 58-62', non_reception_data,
                              glance="Five named ways a connection is refused rather than received (Sahl, The Introduction Ch.3, 58-62), a distinct finding from simply lacking reception; the Kind column numbers them and the notes spell each one out. Under Sahl's rule Kind II overrides any reception for the same pair (only a minor one is possible there; Questions Ch. 1, 63 with 40-41), and Kind IV marks the pair's reception brought down without removing it (62; decision D-2).",
                              notes="Sahl's A -> B model: A is the connecting (applying) planet, B the planet it connects with.\n\nKind I (58): B holds no essential dignity at all at A's position -- B is alien in A's sign, so A is not recognised.\n\nKind II (59-60): A stands in B's own sign of fall, \"like one who comes to it from the house of its enemies.\"\n\nKind III (61): A is in its OWN fall and B has no house or exaltation there to rescue it -- \"as though the one asking is offering defeat.\"\n\nKind IV (62): B is in its own fall, which brings the connection down whatever A's condition.\n\nKind V (62): B sits in A's own sign of fall.")
                    _finding(_gap, 'Returning', 'Sahl, The Introduction Ch.3, 65-69', returning_data,
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
                    st.markdown("**Prevented connections** — Ch.3, 31-48, the Handy Tables' own grouping for Lesson 17")
                    _finding(_gap, 'Prevented connections', "Sahl, The Introduction Ch.3, 31-48; Gr. Intr. VII.5, 90-94 and 120-125", prevented,

                             glance="Ways of stopping a connection before it completes, in one table as the Handy Tables give them: Sahl's intervention, nullification and cutting, plus Abu Ma'shar's two further cuttings (VII.5, 121-124), which Sahl does not have. His revoking, resistance and escape are in his own section.")
                    _finding(_gap, 'Banished', 'Sahl, The Introduction Ch.3, 64', banishment_data,
                              glance='"The banished planet is the planet which none of the planets connects to" (64) -- a planet outside every live connection, whatever the signs are doing. Each row shows the nearest configured planet and why that is not a connection.',
                              notes='Sahl\'s definition is about CONNECTIONS (6-21), not signs: a planet can be in trine by sign with everyone and still be banished if no planet is inside a live connection with it, and it can hold an out-of-sign body connection (20-21) and not be banished at all. Abu Ma\'shar\'s later "wildness" (VII.5, 79-82) is a different, whole-sign test -- aversion to every planet -- and has its own table in his view. Dykes\' note on 64 calls Sahl\'s the earlier, less precise form; the two are kept apart rather than one served under both names.')
                    _absent(_gap)

            def sahl_strength():
                with st.container(border=True):
                    st.markdown("**Strength and weakness** — Ch.3, 77-112")
                    _tick_grid(_gap, 'Strength of the Planets', 'Sahl, The Introduction Ch.3, 78-88', strength_data,
                               'Strength Testimonies', STRENGTH_COLUMNS,
                               glance="The eleven testimonies of a planet's strength at the time of judgment (Sahl, The Introduction Ch.3, 78-88), one column per testimony; the answer key under the grid spells each one out in words.",
                               notes='Testimonies 78 and 83 look similar but are different measurements. 78 is whole-sign, narrowed to the six places that LOOK at the Ascendant. 83, advancing, is DYNAMIC -- read against the Alchabitius quadrant cusps, since the note on 83 says the word means "dynamically angular or succeedent, i.e. by primary motion with respect to the angular axes, and not by whole sign." A planet leaving an angle is withdrawing even while its whole sign is still angular, so the two disagree for about a third of placements.\n\n83 also carries Sahl\'s FIVE-DEGREE RULE: "the planet will not be falling from the stake unless it was 5 degrees distant from its rear -- I mean, if the stake was 10 degrees of Aries, then every planet which has less than 5 degrees between it and the stake is truly counted as being in the stake" (Fifty Aphorisms #44, 88), which he states again in On Nativities Ch.1.22, 9. A planet a few degrees short of an angle is therefore angular, not cadent; the row says so when that is why it qualifies. It moves about 5% of placements, all of them cadent-to-angular. Sahl states the rule twice for the stakes and once for every house (On Nativities 1.18, 19: "and likewise in all of the houses"); the stakes reading is the default, and the "Five-degree carryover at all twelve cusps" switch beside this table selects the other, which flips the verdict for about 6% of placements.\n\nDistinct from the Abu Ma\'shar-based Planetary Condition table, which scores a broader, later scheme.')
                    _tick_grid(_gap, 'Weakness of the Planets', 'Sahl, The Introduction Ch.3, 91-100', weakness_data,
                               'Weakness Testimonies', WEAKNESS_COLUMNS,
                               glance="The ten testimonies of a planet's weakness at the time of judgment (Sahl, The Introduction Ch.3, 91-100), one column per testimony; the answer key under the grid spells each one out in words.",
                               notes="The ten (91-100): falling and averse to the Ascendant (the 6th or 12th), retrograde, under the rays, connecting with an infortune by assembly, square or opposition, enclosed between both infortunes, in its own fall, connecting with a falling planet or separating from a would-be receiver, alien (no house, exaltation or triplicity where it sits), with the Node and no latitude, or inverted (in detriment). Distinct from the Abu Ma'shar-based Planetary Condition table in his view, which scores a broader, later scheme.")
                    _finding(_gap, 'Corruption of the Moon', 'Sahl, The Introduction Ch.3, 103-112', moon_corruption_data,
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
                    "only because the Rhetorius/PN4 delineations on the Dignities page have to pick one of two readings. Read the four "
                    "counts and the labels themselves in preference to the single number."
                )
                with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                    st.markdown("The Moon's eleven corruptions (63-74) are shown as their own count rather than folded in with the rest. Sahl's ten (The Introduction Ch.3, 103-112) are a different list, not a variant reading of this one, and have their own table, Corruption of the Moon, in the Sahl view: Abu Ma'shar has eclipse, the twelfth-part of Saturn or Mars, southern latitude and the ninth house, none of which Sahl lists; Sahl has her own fall, connection with a fallen planet, and wildness, none of which appear here.\n\nThe four counts and the labels are the report. NET and VERDICT are a convenience of this app and NOT Abu Ma'shar's: he enumerates the conditions but never totals them, and the chapter supplies no weighting and no rule for ties. They exist because the Rhetorius/PN4 delineations in Topical Planets in Houses have to choose between a good and a bad reading.\n\nTwo distortions in the raw count are corrected so that one fact cannot vote repeatedly: the Moon's eleven corruptions contribute a single entry (as their own checklist they had been dragging her to a Bad verdict about three times as often as any other planet), and multiple reception rows for one planet likewise count once.\n\nEnclosure here is Abu Ma'shar's own (56-62) -- by degree within 7 degrees either side counting rays as well as bodies, by sign in the 2nd and 12th, or separating from one encloser and connecting with the other -- and it can be DISSOLVED: the degree type when the Sun or a fortune casts a ray within 7 degrees of the enclosed planet (60), the sign type by any look from them (61). The standalone Enclosure table in the Connection group of the Sahl view is Sahl's separate version.\n\nThe by-sign type counts an encloser's RAYS as well as its body, which is what 58 says twice. Be aware that this makes it common: it fires on roughly 43% of placements, because a planet's rays reach eight of the twelve signs. A bodies-only variant at about 2% exists in the code (SIGN_ENCLOSURE_BODIES_ONLY) but is this project's own conjecture, not the text, so it is off.")

            def abu_natural():
                _finding(_gap, 'Natural connections', "Gr. Intr. VII.5, 53-77", natural_connections,
                          columns=['Pair', 'Family', 'Degrees', 'From exact', 'Motion', 'Affinity (76-77)', 'Ordinary aspect', 'Standing'],
                          glance='"Another type of connection and separation [even] without the planets\' looking at each other" (53): pairs standing in signs of equal ascensions (56) or of equal daylight (67-75), whose degrees correspond as complements within the sign -- 12 Gemini to 18 Capricorn (62). A relation of its own, not an aspect and not a dignity: the Ordinary aspect column keeps saying Aversion where that is what the signs are.',
                          notes='EQUAL ASCENSIONS (56): "Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and Sagittarius, Leo and Scorpio, and Virgo and Libra." EQUAL DAYLIGHT (67-75), the antiscia: Gemini-Cancer, Taurus-Leo, Aries-Virgo, Libra-Pisces, Sagittarius-Capricorn, exactly as he lists them -- Aquarius-Scorpio completes the standard scheme but is not enumerated here and is not added (see the coverage note on the Sources page).\n\nDEGREES: "when a planet is in the first degree of Aries, then it is in the nature of a planet which is at the last degree of Pisces" (57); "the planet which is in 12° of Gemini is in the nature of the degree of the planet which is in 18° of Capricorn: so when it passes beyond 12° of Gemini, then it has separated from it" (62). So the counterpart degree runs backwards as the planet runs forwards, and MOTION is read from both speeds together. He gives no orb: every planet in Aries is in the nature of some degree of Pisces, so every pair in a listed sign pair is shown with its distance from exact.\n\nAFFINITY: 76-77 single out four pairs of each family as bridging an ordinary aversion -- Gemini-Capricorn, Sagittarius-Cancer, Aries-Virgo, Libra-Pisces "is called a natural connection by opposition" (76); Gemini-Cancer, Virgo-Libra, Sagittarius-Capricorn, Pisces-Aries "the natural connection by sextile" (77). The notes there record that he omits Aries-Scorpio, Taurus-Libra and Aquarius-Capricorn; they are not added.\n\nThe same sign pairs are one of 134\'s four bases of acceptance, in the Reception table under his rule.')

            def abu_wildness():
                _finding(_gap, 'Wildness', "Gr. Intr. VII.5, 79-82", wildness_data,
                          glance='A planet in whole-sign Aversion to all six other classical planets -- "in a sign such that absolutely no planet looks at it" (79) -- though it may still be "reached" via the lord of whatever bound it occupies (80-81).',
                          notes='Whole-sign and independent of degree. Sahl\'s "banished" (Ch.3, 64) is a different test, about live connections rather than signs, and has its own table in his view.')

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
                          notes="VII.7, 3-13: the planet's distance from the nearest stake in seasonal hours, from the right ascensions and the hourly times of its degree (or of the opposite degree on the nocturnal side). 14-15: two candidate ray positions, one from the right ascensions, one from the ascensions of the city (fn. 252: the oblique ascensions). 16-19: when they differ, a sixth of the excess for every hour of distance is added to the candidate NEAREST the planet (left rays); 20-21: for right rays the same, to the more DISTANT candidate. The nearest/distant flip is in the text and unexplained; the function takes it as written and can be asked for either reading. 22: \"as for the opposition, [a planet] casts its ray into the opposition of its sign, in the same degree and minute.\" The tables the chapter presupposes (fn. 250-251) are computed from the obliquity and the latitude. Decision D-1 (2026-09-08).",
                          height=_rows_height(len(rays_by_ascension_data)))

            def abu_book_v():
                _finding(_gap, 'Book V degrees (supplement, display only)', "Gr. Intr. V.22, Figs. 63-64", book_v_degrees_data,
                          glance='Two degree tables from Book V that no condition in VII.6 and nothing in Sahl reads: the seven "degrees increasing in good fortune" (for the Moon, the Lot of Fortune and the Ascendant) and the thirty-one "degrees of elevation and power" (for the Ascendant and the luminary of the sect). Shown when a named point falls in one; never scored.',
                          notes='V.22, 1-2: "when planets indicate the native\'s good fortune by means of their positions, and the Moon or the Lot of Fortune is in these degrees, or [these degrees] are exactly on the Ascendant, then they will increase in the native\'s good fortune. And if they indicate downfall, then these will instigate some motion towards high rank and power." V.22, 4: "if the Ascendant was one of these degrees ... or the Sun by day or the Moon by night was in one of them, and they were in an excellent position of the circle, and the planets of the root of the nativity indicated good fortune, then they will make him attain nobility and the houses of kings." Ordinal degrees, as in the wells. Leo 5 and Aquarius 20 are in both tables; Aquarius 17 is a degree of elevation and a well. Decisions D-20 and D-21 (2026-09-08), decided together.')

            def abu_forward():
                _finding(_gap, 'Forward-Looking Conditions', 'Revoking, Resistance, Escape — next 200 days', forward_looking_data,
                          glance='Conditions describing what happens as the chart moves forward in time (up to ~200 days), not the birth moment alone.',
                          notes='Each chapter prescribes an ORDERED SEQUENCE of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when. A condition not found inside 200 days is reported as not found, never as a negative finding.\n\nREVOKING (117): "a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it." The window is now birth to the applicant\'s first station: perfection inside it means nothing was revoked.\n\nRESISTANCE (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one BY RETROGRADATION, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead. All five steps are required and timed.\n\nESCAPE (119): the planet being applied to leaves its sign first; the applicant then follows across the SAME boundary on its own next crossing, and is captured by a body it meets in the new sign. Dykes\' note on Fig. 139 is the picture: Mercury slips from Virgo into Libra, Venus follows, and Saturn\'s body catches her there.')

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
                with _tabs[4]:
                    abu_block([abu_condition, abu_natural, abu_wildness, abu_reflection, abu_favor, abu_rays,
                               abu_book_v, abu_forward])
            _absent(_gap)

        def page_lots():
            st.header("Lots")
            st.caption("Lesson 18.")
            _readings_note()
            st.subheader('Classical Lots', help='Arabic Parts: sect-dependent formulas combining two planets or points with the Ascendant to derive a new sensitive degree tied to a specific topic (e.g. Fortune = body/livelihood, Spirit = mind/action).')
            # Formula from the same LOT_DEFINITIONS text the Topical Lots
            # table carries (via calculate_topical_lots), so the two cannot
            # differ; Basis has no definition row and says so.
            formula_by_lot = {r['Lot']: r['Formula'] for r in topical_lots}
            classical_rows = []
            for r in classical_lots:
                row = {k: v for k, v in r.items() if k != 'Standing'}
                row['Formula'] = formula_by_lot.get(r['Lot Name'],
                                                    'Ascendant + (shorter arc between Fortune and Spirit)  [not in the sources]')
                row['Standing'] = r['Standing']
                classical_rows.append(row)
            st.dataframe(pd.DataFrame(classical_rows), hide_index=True, width='stretch', height=_rows_height(len(classical_rows)))
            with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                st.markdown('Fortune and Exaltation are attested in Sahl; Spirit is named by Sahl (the Lot of the Invisible) but its Moon-to-Sun formula comes from the course tables, as its Standing says. All three carry their provenance in the Topical Lots table below. BASIS IS NOT: no Lot of Basis appears anywhere in the material this project has, and the construction used takes the unsigned shorter arc between Fortune and Spirit, discarding the direction the pair actually stands in. It is kept because it has always been here, and marked rather than presented as settled.')
            st.subheader('Topical Lots (Sahl, On Nativities)', help="Sahl's topical Lots, each with its own provenance. He gives several of them MORE THAN ONCE, with formulas that genuinely conflict, and Dykes' apparatus does not silently reconcile them -- so neither does this table.")
            _reading_radio("House-based Lots measure to the", LOT_HOUSE_CUSP_OPTIONS, "lot_house_cusp", "_lot_house_cusp",
                           help="'The second place', 'the degree of the eighth place', 'the ninth' (On Nativities 2.15, 1; "
                                "8.6, 1; Ch. 9, 9): the Ascendant's degree carried into that sign, or the Alchabitius cusp. "
                                "Affects: this table only. Full text on the Sources page.")
            # Fortune, Spirit and Exaltation are in the Classical Lots table
            # above, with the same Formula; the provenance columns are in the
            # expander so the table itself is the worksheet.
            topical_rows = [r for r in topical_lots if r['Lot'] not in ('Lot of Fortune', 'Lot of Spirit', 'Lot of Exaltation')]
            st.dataframe(pd.DataFrame(topical_rows, columns=['Topic', 'Lot', 'Position', 'WS place', 'Lord', 'Formula', 'Active']),
                         hide_index=True, width='stretch', height=_rows_height(len(topical_rows)))
            with st.expander("Provenance and standing per Lot"):
                st.table(pd.DataFrame(topical_rows, columns=['Topic', 'Lot', 'Standing', 'Source', 'Editor’s note']),
                         hide_index=True)

            with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                st.markdown('The STANDING column records his editorial position in his own words where he states one.\n\nFour kinds of case. SAHL HIMSELF RULES: of the two sibling Lots, "both of the Lots are correct, so work with them both together" (3.11, 4) -- neither is subordinate. DYKES NAMES HIS CHOICE: of the three witnesses to the Lot of enemies, "I have used M here"; on the night reversal of the Saturn-Moon work Lot, "Paul instructs us to reverse it by night, but Abu Ma\'shar says not to. We should follow Paul." DYKES MARKS ONE STANDARD: on children, "the usual calculation ... is that of Hermes." DYKES ONLY TABULATES: three Lots for work, after noting that "Sahl quietly switches to Masha\'allah\'s treatise on Lots ... without telling us that the formula is different."\n\nEvery formula is taken from the running prose or a footnote, never from one of the summary tables.\n\nNote the Lot of death is projected from Saturn by Dykes\' emendation (fn. 89, with Masha\'allah\'s manuscripts and Dorotheus); Sahl\'s own manuscripts read the Ascendant.')
        def page_victors():
            st.header("Lunation and victors")
            st.caption("Lessons 19-20.")
            st.subheader('Prenatal Lunation (Syzygy)', help='The New or Full Moon exact before birth, its degree, natal house, and Almuten (victor) -- a key predictive point in Persian/Abbasid technique, thought to set the tone for the life or the period leading up to birth.')
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
                {"Metric": "Syzygy Lord (Almuten)", "Value": f"{syzygy['almuten']} (Score: {syzygy['almuten_score']})"},
            ]
            st.dataframe(pd.DataFrame(syzygy_rows), hide_index=True, width='stretch')
            st.subheader('Victor of the Chart', help="Ibn Ezra's worksheet reproduced cell for cell, so it can be checked against a hand-filled sheet. The seven planets are the columns.")
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
                st.markdown('The first five rows score each planet\'s essential-dignity claim AT THAT POINT\'S degree -- Sun, Moon, Ascendant, Lot of Fortune, and the prenatal New/Full Moon. Then Lord of the Day (+7), Lord of the Hour (+6) and Places are added ONCE each, not per point; Places is keyed the other way round, by the candidate planet\'s own Whole-Sign house. Every column is summed into Totals, and the single highest total is the chart\'s victor.\n\nTWO INDEPENDENT AXES, and all four combinations are shown. The dignity weights are Older (al-Tabari/Masha\'allah, Bound 3 > Triplicity 2) or Newer (al-Qabisi/Abu Ma\'shar, Triplicity 3 > Bound 2); the Places wheel is ibn Ezra\'s own or Masha\'allah\'s. Nothing in the source says which wheel goes with which weighting, so pairing each with the wheel of its own named tradition is a reading, not a fact -- those two are labelled "matched preset" and the two off-diagonal combinations, previously not computed at all, are shown beside them. Where all four agree the victor is robust; where they part, the disagreement is the finding. Ibn Ezra\'s later victor #2 (1507) replaces the two chronocrator rows with a Superiors row scored only for Saturn, Jupiter and Mars; its weight is not given in the course materials, so it is not implemented rather than guessed.')
        def page_timing():
            st.header("Timing")
            st.caption("Part 2: prediction. Every rule on this page comes from Abu Ma'shar, "
                       "*On the Revolutions of the Years of Nativities* (*Persian Nativities* IV), "
                       "cited as Book.chapter, sentence -- except the releaser and the house-master, which "
                       "PN IV leaves to another book of Abu Ma'shar's: \"the book which we worked on concerning "
                       "nativities\" (IX.8, 123), his *Book of the Judgments of Nativities* (Bodleian Hunt. 546, "
                       "fn 315), not in this corpus and not the *Great Introduction*, which has only the Lot of the "
                       "releaser. They are taken from Sahl, *On Nativities* (the chapter named The Releaser, cited "
                       "by that book's chapter and sentence). What neither book settles is listed at the foot of "
                       "the page rather than filled in.")

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
                    # No upper bound: the default chart is 1240, and "past the
                    # table" is a state the page reports, not an error.
                    st.number_input("Age (completed years)", min_value=0, value=int(target_age), step=1,
                                    key="target_age")
                    _persist("target_age", "_target_age", target_age)
                else:
                    st.text_input("Target date (YYYY-MM-DD)", value=target_date.isoformat(), key="target_date")
                    _persist("target_date", "_target_date", target_date.isoformat())
                    if parse_iso_date(st.session_state.get("target_date", target_date.isoformat())) is None:
                        st.caption(f"Not a YYYY-MM-DD date; using {target_date:%Y-%m-%d}.")
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
                             height=_rows_height(len(pn4['revolution_rows'])))

                # --- The charts, drawn (2026-09-10) ---------------------------------
                # I.6, 1-6 and IX.3, 4-8 describe images holding the root, the
                # revolution of the year and the revolution of the month on one
                # zodiac. Drawn as PN IV's editor draws them: the outer charts in
                # whole signs, the sign of the year shaded, the profection a
                # dashed arc, an Egyptian-bounds ring, the default points of p. 12.
                # The controls are readings of the page, kept across navigation.
                st.subheader("The charts, drawn",
                             help="Year: the revolution alone (Figures 4, 26). Year over root: the image of the revolution "
                                  "of the year, I.6, 3-6 (Figure 51 and fn 33; Figures 5 and 27 in Dykes' order). Month "
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
                        want_lots = _reading_checkbox("Lots", "timing_lots", "_timing_lots",
                                                      help="I.6, 3-4: the Lots \"according to how you do it\" -- this engine's, "
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
                svg_timing = generate_multiwheel_svg(_rings, chart_name, wide=_wide_t, bounds=wheel_bounds, extras=_extras, **_kw)
                st.image(svg_timing, width='stretch' if _wide_t else 560)
                st.download_button("Download this wheel (SVG)", svg_timing, key="dl_timing_wheel",
                                   file_name=f"{re.sub(r'[^A-Za-z0-9]+', '_', chart_name).strip('_') or 'chart'}_"
                                             f"{re.sub(r'[^A-Za-z0-9]+', '_', wheel_view).strip('_').lower()}_age{pn4['age']}.svg",
                                   mime="image/svg+xml")
                st.caption("PN IV's own conventions, read from its figures: the nativity in the centre and the "
                           "revolution outside in every bi-wheel but Figure 51, where Dykes follows Abu Ma'shar's order of PN IV I.6 "
                           "order and says so (p. 12); the outer charts in whole signs; \"the profected natal Ascendant "
                           "... which I have shaded in grey\" (fn 33) -- the sign of the terminal point of the year -- "
                           "with the profection drawn as a dashed arc from the natal Ascendant (Figures 3, 33); the month "
                           "as a tri-wheel, root, year, month (fn 58); a ring of the Egyptian bounds on every wheel. "
                           "Default points are Dykes' (p. 12): the seven planets, the nodes, Fortune, the angles; "
                           "I.6, 3-4's Lots, rays and twelfth-parts are the toggles, and the inventory table below is "
                           "the authority the picture is held to. TP marks the terminal point of the year (I.6, 5); the "
                           "letters under a natal planet mark I.6, 6's time lords -- D distributor, P partner, F lord of "
                           "the fardar, f its divider, O lord of the orb; the solid arc from the natal Ascendant is the "
                           "distribution, ending on the degree reached now with its bound tinted (Figures 2, 65). The "
                           "outer charts' Alchabitius cusps are not drawn; Figure 51's are not either.")


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
                st.dataframe(pd.DataFrame(image_rows), hide_index=True, width='stretch', height=_rows_height(16))
                st.caption("A table, not the wheel of I.6, 1: every point by the revolution's house cusps -- I.6, 2: "
                           "\"calculating the houses by their degrees and minutes, in the way that you calculate the houses by "
                           "the portions of hours and the ascensions of the right circle\" (the Alcabitius cusps this engine "
                           "computes; Dykes drew Figure 51 by whole signs \"for clarity\", fn 33; Figure 52 is the count table), "
                           "ordered by degree within the house, with each "
                           "point's bound. The twelfth-part construction -- 2.5 degrees to a sign, beginning with the sign "
                           "itself -- is stated at Gr. Intr. V.18, 1-3 (Figure 57). The fixed stars of I.6, 7 are not computed. The Lots are this "
                           "engine's, \"many or few\"; the count line excludes them as I.6, 8 does.")

                st.subheader("The reading checklist (I.7, 1-26)",
                             help="\"If you made the image of the revolution of the year, then understand:\" (I.7, 1) -- "
                                  "twenty-six things. 2-6: the revolution's Ascendant -- its house in the root, who is in it "
                                  "and looks at it in both times, who has a claim on it and where they stand, whether its "
                                  "lord has one house or two and looks at them. 7-24: every planet -- motion, strength, "
                                  "aversion and aspect, rays, connection, reception, support, friendship, domain, "
                                  "twelfth-parts, returns, course, transits, the Lots, the stakes, the Sun. 25-26: \"its "
                                  "indication will be according to its place and condition in the two times together.\"")
                st.markdown("**I.7, 2-6 -- the revolution's Ascendant:**")
                st.dataframe(pd.DataFrame(pn4['i7_ascendant']), hide_index=True, width='stretch', height=_rows_height(5))
                st.markdown("**I.7, 7-24 -- the planets, in both times** (the numbers are I.7's sentences):")
                st.dataframe(pd.DataFrame(pn4['i7_planets']), hide_index=True, width='stretch', height=_rows_height(14))
                st.caption("Facts from the engine's own evaluators, run on the revolution's data as on the root's: the "
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
                st.dataframe(pd.DataFrame(pn4['year_rows']), hide_index=True, width='stretch')
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
                st.dataframe(pd.DataFrame(ii3['root_rows']), hide_index=True, width='stretch', height=_rows_height(5))
                st.markdown("**In the revolution (II.3, 3):**")
                st.dataframe(pd.DataFrame(ii3['revolution_rows']), hide_index=True, width='stretch', height=_rows_height(5))
                st.markdown(f"**The lord of the year, {pn4['year']['lord']}: the factors of II.3, 5-6, per chart:**")
                st.dataframe(pd.DataFrame(ii3['lord_rows']), hide_index=True, width='stretch', height=_rows_height(6))
                st.dataframe(pd.DataFrame(ii3['refinement_rows']), hide_index=True, width='stretch',
                             height=_rows_height(len(ii3['refinement_rows'])))
                st.markdown("**Figure 55 -- the four cases, in the book's words; which one holds is left to the reader:**")
                st.dataframe(pd.DataFrame(ii3['figure_55']), hide_index=True, width='stretch', height=_rows_height(4))
                st.caption("Facts, not a verdict. II.3, 5-6 name the factors of a suitable and a contrary condition and "
                           "give no rule for weighing them, so each factor is shown for each chart from the engine's own "
                           "evaluators (essential and accidental dignity, solar phase, reception under the Configurations "
                           "page's rule), and Figure 55's cell is not chosen. \"Domain\" is read as sect (fn 46, 48); "
                           "\"westernization from the Sun\" is shown as the solar side (fn 47). Aspects to the sign and to "
                           "the lord are by whole sign. Not read: twelfth-parts; fn 37-41's classes of sign and of degree. "
                           "The delineations of II.4-II.21 are not built. No worked example exists; Figure 55 is Dykes' "
                           "table.")

                st.subheader("Indicators 6-19: the fact each one reads",
                             help="II.1, 11-24 list the remaining fourteen indicators, in II.1, 25's order of strength. "
                                  "Each reads a fact from the root and the revolution and judges it in a chapter of its "
                                  "own; the facts are computed here, the judgments are not. Nine are lookups on the two "
                                  "charts. #7 is read from the Moon's connections in her sign (II.22, below). #15 needs "
                                  "the house lords' connections read in the revolution, which the engine's static test "
                                  "does not do, and #16 and #17 follow the year's transits, which are not tracked -- "
                                  "those three rows say so.")
                st.dataframe(pd.DataFrame(pn4['further_rows']), hide_index=True, width='stretch',
                             height=_rows_height(14))
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
                                  "second hour lord from the natal one -- read as hour k for house k.")
                st.dataframe(pd.DataFrame(pn4['orb_rows']), hide_index=True, width='stretch',
                             height=_rows_height(len(pn4['orb_rows'])))
                st.caption("What PN IV presupposes here rather than states: the planetary hours. Their sequence from "
                           "the day lord at sunrise is Dykes' Figure 45 (Intro Sect. 13), which the Chart page's hour "
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
                st.dataframe(pd.DataFrame(gov_rows), hide_index=True, width='stretch', height=_rows_height(8))
                fm_rows, fm_verdict = pn4['first_month_governor']
                st.markdown(f"**IX.2, 4:** {fm_verdict}")
                st.dataframe(pd.DataFrame(fm_rows), hide_index=True, width='stretch', height=_rows_height(5))
                st.caption("Partial by nature, and said so per row. Testimony #3 and the releaser's half of #4 need the "
                           "longevity releaser, which PN IV does not supply (IX.8, 123); they are filled from the releaser's "
                           "distribution (Sahl, On Nativities 1.15, in The releaser chapter) when that finds one, #4 "
                           "counted only when the two distributions share one partner; #7 is "
                           "read from the Moon's connections in her sign (II.22, below). The tally runs over what is "
                           "available and names a governor ALONE only when all eight are counted and combine in one "
                           "planet, which is what IX.9, 10 reserves the word for. "
                           "\"The first lord\" of the revolution's Ascendant is read as its domicile lord (fn 324). The "
                           "IX.2 test is strict and most years fail it, so its five conditions are shown one by one; "
                           "Dykes' fn 39 (age 39, everything in Cancer, the Moon) is the case it is checked against. "
                           "IX.9, 11-13 and IX.2, 8-11, the judgments of the governor's condition, are not built.")

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
                                  "1-5 give the Moon's list. Dykes' fn 237 reads these as proxies standing in for the "
                                  "luminary.")
                if pn4['proxies'] is None:
                    st.markdown(f"This year's lord is **{pn4['year']['lord']}**; the proxies apply only when the Sun or "
                                f"the Moon is lord of the year.")
                else:
                    st.markdown(f"This year's lord is **{pn4['year']['lord']}**.")
                    st.dataframe(pd.DataFrame(pn4['proxies']), hide_index=True, width='stretch',
                                 height=_rows_height(len(pn4['proxies'])))
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
                             height=_rows_height(min(len(pn4['turning_rows']), 16)))
                st.caption("The direction \"a year for every degree\" is not built and each row says so: for planets and "
                           "Lots it is III.1, 12's third case, whose method PN IV does not state; for the cusps VI.2, 21 "
                           "names \"the portions of the hours and the right circle\", semi-arcs, and gives no procedure. "
                           "The Ascendant's and the meridian's directions are the distributions above. Which \"twelve "
                           "Lots\" VI.2, 1 means is not stated; the formulas in fn 12-31 are Dykes' identifications from "
                           "Sahl and the Great Introduction, and the engine's Lots are paired to them here, with the two "
                           "places they differ on the night reversal named in the row. \"Whichever had the shift in the "
                           "root\" for the parents (VI.2, 6, 8) is read as the sect planet, per fn 16 and 19. The "
                           "triplicity lords of VI.2, 4-5 and the delineations are not built. No worked example exists; "
                           "Figures 90-91 are Dykes' diagrams.")

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
                               "defined (the domain of decision D-23).")
                else:
                    _strip = generate_distribution_strip_svg(pn4['segments'], pn4['elapsed_years'], 'years',
                                                             PN4_DISTRIBUTION_SPAN_YEARS, 'The distribution from the Ascendant')
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
                           "Figure 67 with fn 56 is Dykes' diagram of III.2, 33.")

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
                                                             PN4_DISTRIBUTION_SPAN_YEARS, f'The distribution from the {point}')
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
                           "is worded for the Ascendant and is carried here by analogy. (5) Only the two degrees are "
                           "directed; planets in the Midheaven, which III.1, 12 also assigns to right ascension, are not.")

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
                                  "bound lord in the Ascendant with the releaser beats all. Decided by the owner "
                                  "2026-09-10 on process/TIMING_SOURCES_REPORT_2026-09-10.md.")
                rel = pn4['releaser']
                st.markdown(f"**{rel['verdict']}**")
                st.dataframe(pd.DataFrame(rel['candidates']), hide_index=True, width='stretch',
                             height=_rows_height(len(rel['candidates'])))
                if rel['ranking']:
                    st.markdown("**The lords looking at the releaser, ranked** (1.15, 13; 1.20, 2-5) -- the first is the house-master:")
                    st.dataframe(pd.DataFrame(rel['ranking']), hide_index=True, width='stretch',
                                 height=_rows_height(len(rel['ranking'])))
                if rel['releaser'] is None:
                    st.markdown("**The stand-in (Sahl, *On Nativities* 1.32, 11-14, al-Andarzaghar).** The Ascendant's "
                                "distribution in the tab \"from the Ascendant\" is \"the first of them\" (13); the Moon, "
                                "\"then the Moon\", directed from her natal degree to the infortunes and to burning by the "
                                "operation of 1.23, 2 (1.32, 12: \"if you directed the Sun or Moon in their courses to the "
                                "infortunes ... it kills, whichever of these four connects first with the infortune\"; 14: "
                                "\"if the fortunes are not looking at it\" -- the aspect of the fortunes is not judged here):")
                    if pn4['standin_moon'] is None:
                        st.warning("Refused at this latitude, as every direction by the oblique ascension is (decision D-23).")
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
                        st.warning("Refused at this latitude, as the Ascendant's distribution is (decision D-23).")
                    else:
                        _rstrip = generate_distribution_strip_svg(pn4['releaser_segments'], pn4['elapsed_years'], 'years',
                                                                  PN4_DISTRIBUTION_SPAN_YEARS, 'The distribution from the releaser')
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
                st.caption("Readings made here, each one Sahl leaves open. (1) The places are quadrant houses with the "
                           "five-degree carry-over (fn 109: \"quadrant divisions, not whole signs\"; Aphorism 44; 1.22, 9), "
                           "the reckoning the Chart page's planetary-years table uses; the day list is the five places "
                           "1.15, 6 names, the night list every stake and succedent. (2) \"Looking\" is the whole-sign "
                           "aspect, and a lord in the candidate's own sign counts as looking (1.20, 4). (3) A candidate is "
                           "not its own house-master except in 1.16's four signs. (4) The triplicity lord is the lord of "
                           "the sect. (5) The meeting is the last New Moon and the fullness the last Full Moon before "
                           "birth; the fullness's degree is the luminary above the horizon at that moment, the engine's "
                           "convention for a preventional syzygy, since 1.15 does not say. (6) \"In good places\" for the "
                           "Ascendant's lord (1.15, 16) is a stake or succedent. (7) The day chart consults the Sun, the "
                           "meeting and the Ascendant only, the night chart the Moon, the fullness, the Lot and the "
                           "Ascendant, as 6-14 order them; 1.15, 15's summary names all five before the Ascendant and is "
                           "quoted, not applied. Not applied, and named: "
                           + '; '.join(f"{c} ({t})" for c, t in SAHL_RELEASER_NOT_APPLIED) + ". "
                           "The YEARS the house-master grants are granted by nothing: On Times 4, 7 and On Nativities "
                           "1.20 disagree on where the greater years fall (corpus disagreement #2) and the Chart page "
                           "shows both columns applied to no one. On Times 4, 2-5's shorter list (victor by testimony, "
                           "seven candidates) and Masha'allah's ray in the Ascendant (1.23, 46-50) are the other two "
                           "procedures in the corpus, not built. No worked example exists in Sahl.")

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
                                  "years -- corpus disagreement #3's \"Masha'allah alternative\", absent from PN IV and "
                                  "present in Sahl.")
                if not pn4['house_master']:
                    st.markdown("No house-master to direct (see the section above).")
                else:
                    for flag in pn4['hm_flags']:
                        st.markdown(f"- {flag}")
                    if pn4['hm_direction'] is None:
                        st.warning("Refused at this latitude, as every direction by the oblique ascension is (decision D-23).")
                    else:
                        st.markdown(f"**{pn4['house_master']}**, the house-master, directed from its natal degree to the "
                                    f"bodies, squares and oppositions of Saturn and Mars and to the Sun's degree, forward, "
                                    f"a year to a degree of the birth latitude's ascensions, within {PN4_DISTRIBUTION_SPAN_YEARS:g} years:")
                        if pn4['hm_direction']:
                            _hstrip = generate_hit_strip_svg(pn4['hm_direction'], pn4['elapsed_years'],
                                                             PN4_DISTRIBUTION_SPAN_YEARS, 'The house-master directed')
                            st.image(_hstrip, width='stretch')
                            st.download_button("Download this strip (SVG)", _hstrip, key="dl_strip_hm", mime="image/svg+xml",
                                               file_name="house_master_directed.svg")
                            st.dataframe(pd.DataFrame(pn4['hm_direction']), hide_index=True, width='stretch',
                                         height=_rows_height(len(pn4['hm_direction'])))
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
                                     height=_rows_height(len(pn4['hm_revolution'])))
                    st.markdown(
                        "**The join, and the denial beside it.** The house-master directed here is selected by NAWBAKHT'S "
                        "rule (1.15, 13: the dignity lord looking at the releaser) and directed by MASHA'ALLAH'S operation "
                        "(1.23, 2, \"direct it\" -- the governor); 1.23, 40 and 43 call Masha'allah's governor \"the "
                        "house-master\" in Sahl's own words, but his governor is found by reception (1.23, 1), and the two "
                        "rules name different planets in about a third of charts. The join is this engine's; no sentence "
                        "states it. Abu Ma'shar denies the direction: \"the indicator of the lifespan alone is turned in "
                        "the signs, sign-by-sign, and is not directed degree-by-degree\" (PN IV IX.8, 32; fn 129: \"Some "
                        "texts say that one can also distribute the house-master itself, but to me that seems like a "
                        "misunderstanding\"). Shown as Sahl's, with the denial beside it (owner, 2026-09-11, decision "
                        "sheet row 2). Two limits of the denial, from the second blind reading: IX.8, 32 restricts the "
                        "ROLE -- the planet may still be directed in another capacity, since \"all of the planets and Lots "
                        "are [also] directed\" (III.1, 5); and 1.16, 4 (direct the luminary \"even if a house-master is "
                        "not looking\") is a provision the 1.16 exception built above does not cover. IX.8, 30's turning, "
                        "the one operation Abu Ma'shar licenses for the indicator, follows as PN IV's:")
                    if pn4['hm_turning']:
                        st.dataframe(pd.DataFrame(pn4['hm_turning']), hide_index=True, width='stretch',
                                     height=_rows_height(min(len(pn4['hm_turning']), 12)))
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
                           "luminaries and the Ascendant alike (PN IV III.1, 12's third case, the semi-arcs, stays "
                           "refused); \"in the year of age\" is the completed year the arc falls in. Facts, not judgment: "
                           "1.23, 4's verdict is quoted in the help and not pronounced. Not applied: 4.12, 6 (a retrograde "
                           "planet's rays directed conversely); 1.23, 5-11's further witnesses (the lord of the "
                           "revolution's Ascendant, the lord of the year, the profection reaching an infortune's sign), "
                           "which are the II.3 examination and the indicators in that chapter; 1.23, 13-14's redirection to the "
                           "lord of the Ascendant when the house-master is unsuitable; 1.23, 53-60's increase and "
                           "decrease of years; and the 1.21 additions. No worked example exists in Sahl.")

            with tab_days:
                st.subheader("The small days: the revolution's Ascendant distributed round the year",
                             help="IX.7, 29: \"you look at the degree of the Ascendant of the revolution of the year, so "
                                  "that you direct from it (for the knowledge of the conditions of the days), a day for "
                                  "every 59' 08\", until it returns to the degree of the Ascendant at the end of the "
                                  "year.\" IX.7, 30: a body or ray already in the bound of that degree manages until "
                                  "another meets it; otherwise the bound lords, until a planet or ray is reached. IX.7, 31 "
                                  "names it the small days. A second distribution, running inside the year at its own "
                                  "rate; the Ascendant's distribution above runs across the years.")
                sd_cur = pn4['small_days_current']
                sr_asc = pn4['sr']['ascendant']
                _strip = generate_distribution_strip_svg(pn4['small_days'], pn4['day_of_year'], 'days', None, 'The small days')
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
                           "is not built, nor is Dykes' fn 178, which would direct by ascensions. What is read into the "
                           "sentence rather than stated by it: the bodies and rays are the revolution's; the days count "
                           "from the moment of the revolution (fn 161 leaves a \"day\" undefined); the partner already "
                           "in place is looked for behind the degree within its bound, the shape of III.1, 23-25 narrowed "
                           "to the window IX.7, 30 names, since the sentence does not say whether a body ahead in the "
                           "bound manages from the first day. Only the revolution's Ascendant is directed; IX.7, 31 "
                           "extends the method to every planet, Lot and house. No worked example of it exists in PN IV.")

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
                _strip = generate_distribution_strip_svg(pn4['mighty_days'], pn4['day_of_year'], 'days', None, 'The mighty days')
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
                           "APPLIED: the author's parenthetical, 12.175 d a degree (owner, 2026-09-11). Zodiacal by construction -- "
                           "no ascension appears in the sentence; fn 175's report that ascensions would make more sense "
                           "is an editor's note. The direction does not stop at the end of the sign of the year: it "
                           "starts at the terminal degree and runs thirty degrees, so its last part lies in the bounds "
                           "of the next sign, which is what \"then to the lord of the bound which follows it\" "
                           "describes. Read into the sentence, as for the small days: the revolution's bodies and rays; "
                           "days from the moment of the revolution; the opening partner behind the degree within its "
                           "bound. IX.7, 27's extension to the Lots of the parents and every house and Lot is not built. "
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
                st.dataframe(pd.DataFrame(dm_rows), hide_index=True, width='stretch', height=_rows_height(9))
                st.markdown("**8. The month's days** (IX.7, 34-39), from the four rooted monthly indicators (fn 181) and the month's Ascendant, Lot and Moon:")
                st.dataframe(pd.DataFrame(dm_month), hide_index=True, width='stretch', height=_rows_height(len(dm_month)))
                st.markdown("**9. The ninth-parts** (IX.7, 43-72), from the three starts:")
                st.dataframe(pd.DataFrame(dm_ninth), hide_index=True, width='stretch', height=_rows_height(3))
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
                         "default here, by the owner's decision of 2026-09-10.")
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
                               "distributions above, each applied to the degree of its point and not to the planets in "
                               "it. The **third case** "
                               "has no method in PN IV at all -- III.1, 12 sends the reader to \"what we stated in our "
                               "book [on that topic]\", and Dykes' fn 16 identifies it as Ptolemy's proportional "
                               "semi-arcs, which is an editor's note rather than a stated rule.")
                    st.markdown("**III.1, 6 -- the unit, by level of chart**")
                    st.dataframe(pd.DataFrame(PN4_UNIT_ROWS), hide_index=True, width='stretch')
                with c2:
                    st.markdown("**III.1, 13 -- the rate ladder**")
                    st.dataframe(pd.DataFrame(PN4_LADDER_ROWS), hide_index=True, width='stretch')
                    st.caption("An idealised year of twelve 30-day months (fn 17). The bottom rung is **25 thirds**, a "
                               "sixtieth of a second of arc: 10″ is a day, so an hour is 10″/24 = 25‴ exactly. "
                               "The OCR'd corpus reads 25″, which would make an hour two and a half days long; the "
                               "printed page has 25‴ (verified against the photograph of p. 288).")

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
                           "**Two things in Dykes' fn 191 are also absent**: the SUM of the ascensions and the years, and "
                           "a third, a half and two-thirds of it, are introduced with \"if we follow Valens\" and appear "
                           "in no sentence of III.7; and his worked figure of 20.17 ascensional times for Taurus at 45N "
                           "is not reproduced, the exact computation giving 20.09. III.7, 36 raises a row to \"whenever it "
                           "distributes\" when the planet looks at the position of the distribution and is \"strong in "
                           "[its] indication\" -- strength is nowhere defined in the chapter, so no row is promoted here. "
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

                st.subheader('Chronocrator Matrix (Active Time Lords)', help='Two rows: the lord of the year by annual profection, and the Egyptian bound lord of the Ascendant directed symbolically at one degree per year -- which is not a distribution, as its label says. Abu Ma\'shar names the shortcut himself and grades it: "there is an approximation in it, but the correct [approach] is that this way of directing is like the direction of the Sun every day" (IX.7, 32). The ascensional method he prefers is the jar bakhtar table above.')
                st.dataframe(pd.DataFrame(time_lords_data), hide_index=True, width='stretch')
                st.subheader("Planetary years (Gr. Intr. VII.8, Figure 146) -- display only",
                             help="The lesser, middle, greater and mighty years and the fardar of each planet, beside its placement and what "
                                  "the two placement rules in the corpus would grant it. Nothing here is applied: how many years the "
                                  "house-master grants is the question PN IV does not answer (IX.8, 123) and Sahl's two books answer "
                                  "differently; which planet it is, the Timing page now takes from On Nativities 1.15.")
                st.dataframe(pd.DataFrame(planetary_years_data), hide_index=True, width='stretch', height=_rows_height(len(planetary_years_data)))

            with st.expander("What Persian Nativities IV does not settle", icon=":material/help:"):
                st.markdown(
                    "The Timing page has been deliberately incomplete for weeks, and these items keep it so. "
                    "Each is absent because **the book does not answer it**, not because the work was skipped.\n\n"
                    "**The releaser and the house-master.** PN IV names five releasers -- \"the Sun, Moon, Ascendant, "
                    "Lot of Fortune, or the degree of the meeting or degree of the opposition\" (III.3, 1) -- and says "
                    "all five are directed (III.1, 3). It never says **how to choose among them**, how many years the "
                    "house-master grants, how increasers and decreasers are counted, or how to judge a planet that "
                    "passes one test and fails another. Abu Ma'shar says so himself: those \"who look into it are "
                    "wandering around in the dark; but a statement of the truth of that ... is found in the book which "
                    "we worked on concerning nativities\" (IX.8, 123) -- a book outside this corpus. Since 2026-09-10 "
                    "the choice is made from **Sahl**, *On Nativities* 1.15 (Nawbakht), and the house-master is directed "
                    "per 1.23, 2 (Masha'allah), in the chapter named The releaser, with every reading that step needed said "
                    "there; the releaser's distribution feeds the governor's testimony #3 and the luminary proxies. "
                    "The distribution **from the Ascendant** remains the *jar bakhtar* of II.2, 6-7.\n\n"
                    "**Where the greater years are granted** (*On Times* 4, 7 against *On Nativities* 1.20, 10-17). "
                    "PN IV is silent and Sahl's two books disagree, so the disagreement stays open, the Planetary years "
                    "table still chooses no row, and the house-master is directed instead of granting.\n\n"
                    "**Directing anything that is not the Ascendant or the meridian.** III.1, 12 sends the reader to "
                    "\"what we stated in our book [on that topic]\" for every other point. Dykes' fn 16 identifies the "
                    "method as Ptolemy's proportional semi-arcs, but that is an editor's note rather than Abu Ma'shar's "
                    "sentence, and the reconstructions differ; it is named rather than guessed.\n\n"
                    "**Revolutions of the day and the hour.** Defined in principle (I.3, 10-13) and then declined by "
                    "the author: \"there is no need for us [to do] that, because these nine indicators ... are complete "
                    "for everything needed\" (IX.7, 79).\n\n"
                    "**The unit of a directed degree by sign type, strength or planet.** PN IV keys the unit to the "
                    "level of the chart (III.1, 6) and answers a different question from the one the corpus "
                    "disagreements ask; it is not evidence on either side of them.\n\n"
                    "**The Indian rule for the lord of the year** -- the lord of the first ninth-part of the sign of "
                    "the year (III.10, 1-5), which would restrict the lord of the year to Mars, Venus, Saturn and the "
                    "Moon. PN IV reports it without adopting it, so it is used here only as monthly indicator #2, "
                    "which is where IX.1, 36 puts it.")

            with st.expander("Sources and editorial notes", icon=":material/menu_book:"):
                st.markdown(
                    "**Decision D-3 is closed** (2026-09-10). It asked whether Sahl's *On Times* fell under the "
                    "*Revolutions* deferral, and was decided \"for implementation, yes; for reading, no\" while "
                    "PN IV was unread. PN IV has now been read, and the deferral it named is lifted for everything "
                    "above.\n\n"
                    "**Two readings on this page come from the photograph rather than the OCR'd corpus.** "
                    "(1) The bottom rung of the rate ladder is **25‴**, twenty-five thirds; the corpus reads "
                    "25″, which would make an hour two and a half days long, and the arithmetic settles it "
                    "independently of the page. (2) The *fardar* order is taken from the prose of **IV.1, 2-4**, "
                    "which gives it complete; the corpus has dropped fifteen of the eighteen planet glyphs from "
                    "Figure 43 (p. 116), so the figure itself is not built from. Both are recorded in "
                    "`PN4_READTHROUGH_FINDINGS_2026-09-10.md` (D-07, D-05).\n\n"
                    "**One printed error is deliberately not reproduced.** Intro Sect. 2 (p. 7) puts the monthly "
                    "revolutions at 12° **23′** when the natal Sun is at 12° **22′**. The page "
                    "genuinely prints that, and it is contradicted by the rule in its own sentence, by IX.1, 23, by "
                    "IX.3, 2, and by Dykes' own worked example at Intro Sect. 9 p. 95. The degree **and minute** are "
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
                    "share (11); middle in the second or eighth (16), or in the eleventh or fifth when not in a share "
                    "and not eastern (17). The two disagree, PN IV does not adjudicate them "
                    "(synthesis/04_timing_open_questions.md Sect. 3 #2), and no row is chosen.")

        def page_sources():
            st.header("Sources and readings")
            st.caption("What the app reads from, how it can be read, and what it does not cover.  \n"
                       "**How citations are written.** A locator names its volume, never the author alone: "
                       "*Sahl, The Introduction Ch.3, 85* and *Sahl, On Nativities 1.22, 9*; *Gr. Intr. VII.6, 27* "
                       "is Abu Ma'shar's Great Introduction (Dykes); *PN IV IX.1, 26* is his On the Revolutions of "
                       "the Years of Nativities, Persian Nativities IV (Dykes) -- and on the Timing page, whose rules "
                       "all come from that book, its locators are bare Book.chapter, sentence. Both of Abu Ma'shar's "
                       "volumes have a Book VII, which is why his name alone no longer locates anything.")
            # --- The readings in force (2026-09-10) ----------------------------
            st.subheader("Readings in force",
                         help="Every doctrinal switch, where it is set, what it says now and what the course default "
                              "is. They are remembered between runs. Reset returns all of them to the defaults.")
            _reading_radio("Reading depth", READING_DEPTH_OPTIONS, "reading_depth", "_reading_depth",
                           help="Course text: Sahl's Introduction and On Nativities, the course's own texts, with Abu "
                                "Ma'shar's Great Introduction VII kept apart in its own tab on the Configurations page "
                                "and behind closed expanders elsewhere. Course text and supplement: his tables laid "
                                "beside Sahl's on the same topic, and the supplementary expanders open.")
            _rows = [{'Reading': label, 'In force': str(_reading(wk, sk, default)), 'Course default': str(default),
                      'Set on': page, 'Differs': 'yes' if _reading(wk, sk, default) != default else ''}
                     for label, wk, sk, default, page in READINGS_REGISTRY]
            st.dataframe(pd.DataFrame(_rows), hide_index=True, width='stretch', height=_rows_height(len(_rows)))
            if st.button("Reset every reading to the course defaults", icon=":material/restart_alt:"):
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
                "**Sahl** (The Introduction Ch.3, 6-21): the applying planet's OWN light governs "
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
                "**Five-degree carryover at all twelve cusps** -- RETIRED 2026-09-11 (owner's ruling, "
                "OWNER_RULING_PLACES_VS_DYNAMICS): the five-degree rule is a dynamics rule at the four axial "
                "degrees only and has no all-cusps form under the canon; On Nativities 1.18, 19's 'and likewise "
                "in all of the houses' is read as the four stakes (the course's reading, Lesson 3 §4-5). The "
                "switch is gone; a stored preference for it is ignored.\n\n"
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
                    "implied claim of completeness. Several of these became legible only when "
                    "the missing pages were rephotographed."
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
            st.caption("The course's Handy Tables, printed from the data this app computes with. Nothing on this "
                       "page reads the chart in the sidebar.")

            st.subheader("Dignities by sign",
                         help="Lesson 9. Domicile, exaltation, the three triplicity lords (day, night, participating) "
                              "and the three faces of each sign, as the engine holds them. The exaltation degrees are "
                              "the standard scheme of the Handy Tables and are printed only here.")
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
            st.caption("Sources: Sahl, The Introduction Ch. 1 and Handy Tables (Tables of Dignities). Exaltation degrees: "
                       "the standard scheme; Hermes' differ by a degree for Saturn, Mars, the Sun, Venus and the Moon. "
                       "Triplicity lords are Dorothean (Gr. Intr. V.14, 6-9; Figure 53 (Gr. Intr.)); Virgo's partner is "
                       "Mercury 'in preference to' Mars (V.14, 7; fn 100). Faces are read at 5, 15 and 25 degrees of each sign.")

            st.subheader("Egyptian bounds",
                         help="Lesson 9, and the bounds every distribution of Part 2 runs through (III.1, 11). The "
                              "same table the engine directs by; pinned against four independent witnesses.")
            bound_rows = []
            for sign in SIGN_ORDER:
                row, start = {'Sign': sign}, 0
                for n, (limit, lord) in enumerate(EGYPTIAN_TERMS[sign], 1):
                    row[f'{pn4_ordinal(n)} bound'] = f"{lord} {start}°–{limit - 1}°59′"
                    start = limit
                bound_rows.append(row)
            st.dataframe(pd.DataFrame(bound_rows), hide_index=True, width='stretch', height=_rows_height(12))

            st.subheader("Orders of the dignities, and the good places",
                         help="Lessons 9 and 11-12. How Sahl ranks the dignities in three of his works, and which "
                              "places each of his schemes calls good -- the tables that used to sit in an expander "
                              "on the Chart page.")
            st.dataframe(pd.DataFrame([{'Context': k, 'Order, strongest first': ' > '.join(v)} for k, v in DIGNITY_ORDER.items()]),
                         hide_index=True, width='stretch')
            st.dataframe(pd.DataFrame([{'Scheme': k, 'Places': (', '.join(f"{g}: {p}" for g, p in v.items()) if isinstance(v, dict) else str(v))}
                                       for k, v in GOOD_PLACE_SCHEMES.items()]), hide_index=True, width='stretch')
            st.caption(SEVEN_PLACE_RANKING_NOTE)

            st.subheader("Planetary years",
                         help="Lesson 5's table: the lesser, middle, greater and mighty years of each planet, with the "
                              "fardar period (PN IV IV.1, 2). Display only, by decision D-3: nothing in this app "
                              "applies a planet's years as a grant to a judgment.")
            years = reference_planetary_years_rows()
            st.dataframe(pd.DataFrame(years), hide_index=True, width='content', height=_rows_height(len(years)))
            st.caption("Gr. Intr. VII.8, Figure 146; the fardar periods PN IV IV.1, 2. The "
                       "middle years use two constructions, the ordinary mean for the planets and (least + great/2)/2 "
                       "for the luminaries, per Valens VII.5 (settled 2026-09-09).")

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
                st.Page(page_chart, url_path="chart", title="Chart", icon=":material/explore:", default=True),
                st.Page(page_dignities, url_path="dignities", title="Dignities and places", icon=":material/shield:"),
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
        st.navigation(pages, position="sidebar", expanded=True).run()

    else:
        st.sidebar.error("Timezone boundary not found for coordinates.")
