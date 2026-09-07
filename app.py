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

# ==========================================
# 1. CORE CALCULATION ENGINE
# ==========================================

@st.cache_data(max_entries=32, show_spinner=False)
def calculate_traditional_chart(dt_utc, lat, lon):
    year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
    hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0

    # CRITICAL: Python's datetime is always proleptic Gregorian, and
    # swe.julday() defaults to the Gregorian calendar flag. For dates before
    # the Gregorian reform (Oct 15, 1582), professional astrological software
    # (Solar Fire, Astro.com, etc.) interprets the same y/m/d digits as a
    # JULIAN calendar date. Using the wrong flag silently mis-dates historical
    # charts by several days (7 days in the 1200s, growing further back),
    # which cascades into large positional errors — the Moon alone drifts
    # ~13°/day, so a 7-day calendar error looks like a ~90° Moon error.
    is_gregorian_date = (year, month, day) >= (1582, 10, 15)
    cal_flag = swe.GREG_CAL if is_gregorian_date else swe.JUL_CAL
    jd = swe.julday(year, month, day, hour, cal_flag)

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
            # conditions "in themselves" (Great Introduction VII.1) can be
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
    
    sun_long = planetary_data['Sun']['longitude']

    is_diurnal = (sun_long - ascendant) % 360 > 180.0
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
        'obliquity': swe.calc_ut(jd, swe.ECL_NUT)[0][0],
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
    longitude = longitude % 360.0
    sign = get_zodiac_sign(longitude)
    deg = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    return f"{deg:02d}° {sign[:3]} {minute:02d}'"

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
                        wide=False, chronocrats=None):
    size = WHEEL_SIZE
    cx = cy = size / 2.0
    asc = chart_data['ascendant']
    mc = chart_data['mc']
    cusps = chart_data['houses']
    asc_sign = int((asc % 360.0) // 30)
    angles = (asc, mc, (asc + 180.0) % 360.0, (mc + 180.0) % 360.0)

    def ang(longitude):
        # D1: the rising sign's boundary at 9 o'clock, zodiac counter-clockwise.
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

    def line(x0, y0, x1, y1, stroke, width, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>'

    def text(x, y, s, px, weight='normal', fill='#000', anchor='middle'):
        return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" '
                f'font-size="{px}" font-weight="{weight}" fill="{fill}">{s}</text>')

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
    for r, w in ((_R_RIM, 2.5), (_R_WS_IN, 1.2), (_R_SIGN_IN, 1.6), (_R_Q_OUT, 1.2), (_R_Q_IN, 1.6)):
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000000" stroke-width="{w}"/>')

    # 3. Alchabitius cusps, dashed as before but reaching the degree scale;
    #    the four stakes solid and coloured. House numbers at mid-house on
    #    the quadrant ring.
    for i, cusp_lon in enumerate(cusps):
        x0, y0 = xy(_R_Q_IN, ang(cusp_lon)); x1, y1 = xy(_R_SIGN_IN, ang(cusp_lon))
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
        x0, y0 = xy(_R_SIGN_IN, a_true); x1, y1 = xy(_R_SIGN_IN - 10, a_true)
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

# ==========================================
# 3. DIGNITY & ASPECT EVALUATORS
# ==========================================

# --- Shared classical dignity reference tables --------------------------
# Pulled out to module level so both evaluate_essential_dignities() and the
# prenatal syzygy engine (which needs to look up dignities at an arbitrary
# degree, not just at a planet's own position) can use the same data.
DOMICILES = {'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mercury': ['Gemini', 'Virgo'], 'Venus': ['Taurus', 'Libra'], 'Mars': ['Aries', 'Scorpio'], 'Jupiter': ['Sagittarius', 'Pisces'], 'Saturn': ['Capricorn', 'Aquarius']}
EXALTATIONS = {'Sun': ['Aries'], 'Moon': ['Taurus'], 'Mercury': ['Virgo'], 'Venus': ['Pisces'], 'Mars': ['Capricorn'], 'Jupiter': ['Cancer'], 'Saturn': ['Libra']}
DETRIMENTS = {'Sun': ['Aquarius'], 'Moon': ['Capricorn'], 'Mercury': ['Sagittarius', 'Pisces'], 'Venus': ['Scorpio', 'Aries'], 'Mars': ['Libra', 'Taurus'], 'Jupiter': ['Gemini', 'Virgo'], 'Saturn': ['Cancer', 'Leo']}
FALLS = {'Sun': ['Libra'], 'Moon': ['Scorpio'], 'Mercury': ['Pisces'], 'Venus': ['Virgo'], 'Mars': ['Cancer'], 'Jupiter': ['Capricorn'], 'Saturn': ['Aries']}
EGYPTIAN_TERMS = {'Aries': [(6, 'Jupiter'), (12, 'Venus'), (20, 'Mercury'), (25, 'Mars'), (30, 'Saturn')], 'Taurus': [(8, 'Venus'), (14, 'Mercury'), (22, 'Jupiter'), (27, 'Saturn'), (30, 'Mars')], 'Gemini': [(6, 'Mercury'), (12, 'Venus'), (17, 'Jupiter'), (24, 'Mars'), (30, 'Saturn')], 'Cancer': [(7, 'Mars'), (13, 'Venus'), (19, 'Mercury'), (26, 'Jupiter'), (30, 'Saturn')], 'Leo': [(6, 'Jupiter'), (11, 'Venus'), (18, 'Saturn'), (24, 'Mercury'), (30, 'Mars')], 'Virgo': [(7, 'Mercury'), (17, 'Venus'), (21, 'Jupiter'), (28, 'Mars'), (30, 'Saturn')], 'Libra': [(6, 'Saturn'), (14, 'Mercury'), (21, 'Jupiter'), (28, 'Venus'), (30, 'Mars')], 'Scorpio': [(7, 'Mars'), (11, 'Venus'), (19, 'Mercury'), (24, 'Jupiter'), (30, 'Saturn')], 'Sagittarius': [(12, 'Jupiter'), (17, 'Venus'), (21, 'Mercury'), (26, 'Saturn'), (30, 'Mars')], 'Capricorn': [(7, 'Mercury'), (14, 'Jupiter'), (22, 'Venus'), (26, 'Saturn'), (30, 'Mars')], 'Aquarius': [(7, 'Venus'), (13, 'Mercury'), (20, 'Jupiter'), (25, 'Mars'), (30, 'Saturn')], 'Pisces': [(12, 'Venus'), (16, 'Jupiter'), (19, 'Mercury'), (28, 'Mars'), (30, 'Saturn')]}
CHALDEAN_ORDER = ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter']
# The weighted five-fold dignity claim used wherever this file totals
# essential dignities at a degree: a planet's own score, the prenatal
# syzygy's almuten, and the newer victor scheme (al-Qabisi / Abu Ma'shar,
# triplicity above bound). The older victor scheme swaps bound and
# triplicity and is written out at VICTOR_WEIGHTS.
ESSENTIAL_DIGNITY_WEIGHTS = {'domicile': 5, 'exaltation': 4, 'triplicity': 3, 'term': 2, 'face': 1}

# Dorothean triplicity rulers, keyed by element, each with the Day/Night/
# Participating lord (classical reconstruction as used in medieval Abbasid
# practice — e.g. Dorotheus via al-Biruni/Abu Ma'shar).
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

# Masha'allah's delineations for a topical house's lord, keyed by
# [placed_in_house][lord_of_house] (i.e. outer key = the WSH house the lord
# is physically placed in, inner key = the topical house it rules).
MASHAALLAH_LORDS = {
    1: {1: "Respected in family (subject to other conditions)", 2: "Work with own hands, blessed without searching and need", 3: "Good for siblings from native", 4: "Master of his family and their livelihood; charitable to parents", 5: "Blessed with children in youth, happy with children", 6: "Illness of nature of that planet; death of animals and servants", 7: "Good from women, success from them", 8: "Long lifespan (if good condition); frustration in seeking necessities", 9: "Of fine religion, good soul, knowing the Sunnah", 10: "Associate of authorities, proficient in work, Sultan comes to him", 11: "Successful, good livelihood and condition, glad", 12: "Unhappy, enemies multiply and are victorious, tribulation, belligerent"},
    2: {1: "Will corrupt assets; but if received, gains from sign essence", 2: "Livelihood from known source; if looked at by infortune, ruin", 3: "Siblings compete for assets; they will seek the native", 4: "Prosperous parents; native inherits and is distinguished among siblings", 5: "Children will have good livelihood", 6: "Livelihood from what slaves produce, and animals; lowly benefits", 7: "Corrupts assets due to conflict", 8: "Inheritance; sometimes do work for government/authority", 9: "Assets from foreign country, benefit from travel", 10: "Livelihood from government/authority figure; accumulates assets", 11: "Benefit and assets from friends", 12: "Shameful work, bad character and livelihood, with deception"},
    3: {1: "Siblings suitable, dependent on native; good/wicked mind based on aspects", 2: "Gain from travels and siblings; religion/gain if a fortune", 3: "Siblings are well known, will protect him, love him", 4: "Parents have hardship from siblings; parents like native better", 5: "Native's children named after his siblings; successful in travels", 6: "Siblings have defects/illness, or do the work of slaves", 7: "Brother marries native's women; hostility; native marries relative", 8: "Siblings have defects, chronic illness, diminished condition", 9: "Siblings marry foreign women; moves to another country", 10: "Few siblings, siblings ruined; many travels", 11: "Well-known siblings, condition good, esp. in youth", 12: "Siblings hostile to native, hardship from them"},
    4: {1: "Reverent to parents; hardship from ruler; gains from fathers if received", 2: "Livelihood relates to ancestors; thriving childhood home; devotion", 3: "Siblings steal parents' assets; recognized as thieves", 4: "Parents well known, good reputation; short life if harmed", 5: "Native's children are wretches; encounters hardship due to them", 6: "Native is child of slaves or those doing slave work", 7: "Marries someone from own house, spouse is well known and good", 8: "Fathers are foreigners or have defects/illness, short lifespans", 9: "Parents have hidden illnesses, die outside homeland", 10: "Parents known to rulers; hardship from rulers", 11: "Father has chronic illness, short life, diminished condition", 12: "Parents/family hostile to native; native destroys/leaves childhood home"},
    5: {1: "Happy with children (if unharmed)", 2: "Children have status, will gain good", 3: "Native has siblings abroad who travel and have children", 4: "Prosperous parents see successive generations; good increases", 5: "Native has well-known children who are happy", 6: "Children's upbringing hard, children have defect", 7: "Native marries younger spouse, well-known and virtuous", 8: "Children die early, or have power over others due to Sultan", 9: "Has children in foreign country, delighted; children religious/educated", 10: "Abundance of children; illness/death if harmed; hardship from Sultan", 11: "Delightful children, blessed with good and comfort", 12: "Children debased, sick, from low-status; disobedient/hostile"},
    6: {1: "Miserable, slave work; illness if received; literal slave if Moon corrupted", 2: "Livelihood from 6th-place things; disaster/hardship if not received", 3: "Siblings are hostile and crave his ruin", 4: "Parents unknown in country; aspecting planet shows good/bad", 5: "Fortunate children, but defects will appear in them", 6: "Native healthy, if lord of Ascendant does not look", 7: "Native associates with slave girls or women with defects", 8: "Calamities in slaves and riding animals; not blessed by them", 9: "Blessed with slaves/animals; travel brings illness or corrupts slaves", 10: "Short lifespan, itinerant, enslaves free people", 11: "Bad condition in livelihood, little good, creating discord", 12: "Saddened by slaves and riding animals, no good in them"},
    7: {1: "Native very eager; subordinate to spouse", 2: "Lower-status women; gain/lose money in marriage", 3: "Marries a relative; brothers hostile or marry his women", 4: "Marries relative, good rank; father hostile to native", 5: "Younger spouse; children hostile; deluded about women; servant children", 6: "Sick/slave spouse; low-status spouse; bad reputation due to spouse", 7: "Suitable marriage; spouse has rank of maternal relatives; well-known", 8: "Will inherit from spouse; native dies in exile", 9: "Foreign spouse; good character/pious if a fortune", 10: "Esteemed, well-known spouse; higher-status and connected", 11: "Loving, happy spouse; children and benefit from spouse", 12: "Low-status or sick spouse; spouse is hostile"},
    8: {1: "A wicked soul, much distress, faint-hearted", 2: "Livelihood from inheritance/dead; generous; assets taken if connecting to 8th", 3: "Brother's women will not survive or get inheritance", 4: "Diminishes father's lifespan; fear for native, mother dies in childbirth", 5: "[UNCERTAIN -- the source reads '[illegible] they will survive and will be miscarried', an unresolved contradiction; do not rely on this cell]", 6: "Native healthy if lord of Ascendant does not look", 7: "Consumes inheritance of women; marries foreign woman", 8: "Native is healthy, illness insignificant, death will be light", 9: "Suffers robbery on journeys, eager in accumulating assets", 10: "Authority in youth, a follower who seeks leadership/boasts", 11: "Not well known/descended; does low work like commerce", 12: "Few enemies; many of native's slaves will die"},
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
    2: {'Saturn': {'Good': 'Slow increase, strong; unexpected source.', 'Bad': 'Loss, lazy, ill; abject sources.'}, 'Jupiter': {'Good': 'Good all around, inheritances; leisure.', 'Bad': 'Spending without enjoyment; distress.'}, 'Mars': {'Good': 'Military; enough; benefits from unexpected place.', 'Bad': 'Exile, dangers; squandering.'}, 'Sun': {'Good': 'Dignity, wealth; leisure.', 'Bad': 'Private property; negligence.'}, 'Venus': {'Good': 'Prosperous, pleasing, arts.', 'Bad': 'Disruption, corruption, stagnation.'}, 'Mercury': {'Good': 'Good at business/learning; partnerships.', 'Bad': 'Loss, downturn, blame, quarrels.'}, 'Moon': {'Good': 'Brilliant, conspicuous, extravagant.', 'Bad': 'Family/actions dispersed and divided.'}},
    3: {'Saturn': {'Good': 'Initiates, religious chiefs; travel for benefit.', 'Bad': 'Recluses, bad religious reputation, confused thinking.'}, 'Jupiter': {'Good': 'Balanced moderation; good religious reputation, delight in siblings.', 'Bad': 'Distress from siblings, negligence in religion.'}, 'Mars': {'Good': 'Glory with labor; strong in travel.', 'Bad': 'Bad death for father, evil reports, difficult travels.'}, 'Sun': {'Good': 'Good for marriage/religion; travel with good status.', 'Bad': 'Bad reputation, distress due to travel/relatives.'}, 'Venus': {'Good': 'Travel with good/status, benefit from brothers.', 'Bad': 'Bad reports/journeys, contention with brothers.'}, 'Mercury': {'Good': 'Divination, astrologers, good journeys/visions.', 'Bad': 'Priests, magicians; bad travels, religious doubts.'}, 'Moon': {'Good': 'Good religious activities (with Jupiter).', 'Bad': 'Ignoble mother; sacrilege.'}},
    4: {'Saturn': {'Good': 'Lots of wealth; owning property, building.', 'Bad': 'Destroys/threatens parents, illness; blamed.'}, 'Jupiter': {'Good': 'Commanders, jurists; respected, land/family assets.', 'Bad': 'Middling assets; worries from these topics.'}, 'Mars': {'Good': 'Generals, soldiers; successful, inspiring awe.', 'Bad': 'Sickly, surgery; misfortune for home/land.'}, 'Sun': {'Good': 'Increase in rank, commended, victory.', 'Bad': 'Annoyances, destroys livelihood.'}, 'Venus': {'Good': 'Fortunate over time, charming; delight in important people.', 'Bad': 'Loss of patrimony, widowhood; conflict in land/family.'}, 'Mercury': {'Good': 'Lots of money, initiates; status from Mercurial things/govt.', 'Bad': 'Forbidden mysteries; accusation, family quarrels.'}, 'Moon': {'Good': 'Honored mother, good living standard.', 'Bad': 'Lowborn mother, commerce.'}},
    5: {'Saturn': {'Good': 'Kingships/command over time; delight in friends.', 'Bad': 'Delayed, sluggish; distress from children/siblings.'}, 'Jupiter': {'Good': 'Fortunate, honored, healthy; blessed by children.', 'Bad': 'Lower-status activities; distressed by children.'}, 'Mars': {'Good': 'Good possessions, honor; increase in children/rank.', 'Bad': 'Harmful travel; distress/accidents in family/children.'}, 'Sun': {'Good': 'Honored, easy goals; delight/increase in children.', 'Bad': 'Moderate fortune, childless; distress due to children.'}, 'Venus': {'Good': 'Prize-fighters, victors; increase/delight in women/children.', 'Bad': 'Distress from women and children.'}, 'Mercury': {'Good': 'Wealth, managing money; befriend nobles, profit.', 'Bad': 'Squanders money; hostility, illness/death of children.'}, 'Moon': {'Good': 'Gracious, leaders, fortunate.', 'Bad': 'Foreign travel, parents estranged, orphans.'}},
    6: {'Saturn': {'Good': 'Moderate; slaves/animals recover.', 'Bad': 'No inheritance, dangers from slaves, chronic illness.'}, 'Jupiter': {'Good': 'Exposure, valuable materials; praise from subordinates.', 'Bad': 'Illnesses, distress from enemies/confinement.'}, 'Mars': {'Good': 'Healthy, victory over enemies.', 'Bad': 'Harms children, uneven life, illness.'}, 'Sun': {'Good': 'Mild-temperedness, safety; good fortune from parents.', 'Bad': 'Bad death for father; illness from heat, eye/head pain.'}, 'Venus': {'Good': 'Benefit from underclass/medicine.', 'Bad': 'Sex with low women, badly treated; pregnancy difficulties.'}, 'Mercury': {'Good': 'Advancement through speech/business.', 'Bad': 'Idle, evil; illness, arrested, confinement.'}, 'Moon': {'Good': 'Health and bodily stability.', 'Bad': 'Fluctuating health, bodily weakness.'}},
    7: {'Saturn': {'Good': 'Success after delay, long-lived; owning property.', 'Bad': 'Sickly, blamed/harmed.'}, 'Jupiter': {'Good': 'Long-lived, wealth later; praised, respected.', 'Bad': 'Moderate living; worries.'}, 'Mars': {'Good': 'Professions from fire/violence; successful, inspiring awe.', 'Bad': 'Violent, short-lived; illnesses, spending.'}, 'Sun': {'Good': 'Increase in rank/land; administrators.', 'Bad': 'Lower-status; harm, conflict.'}, 'Venus': {'Good': 'Age difference/delay in marriage; delight, increase in rank.', 'Bad': 'Lewdness; distress in sex/marriage.'}, 'Mercury': {'Good': 'Managing affairs of women; status from govt.', 'Bad': 'Accusation, loss in business, family quarrels.'}, 'Moon': {'Good': 'Changes, travel, better resources.', 'Bad': 'Foreign travel with dangers.'}},
    8: {'Saturn': {'Good': 'Assets over time/inheritance; good from dead.', 'Bad': 'Loss, bad death; squandering, distress.'}, 'Jupiter': {'Good': 'Acquisition, inheritance; leisure.', 'Bad': 'Spending without happiness; distress/fighting due to assets.'}, 'Mars': {'Good': 'Hot-heads, bright; benefit from dead/inheritance.', 'Bad': 'Patrimony spent, dangers; squandered assets.'}, 'Sun': {'Good': "Father's early death, healing; mild-temperedness.", 'Bad': 'Wealthy, benefit from death of women; negligence.'}, 'Venus': {'Good': 'Marry late; benefit from underclass/commerce.', 'Bad': 'STDs, seizures; negligence in assets, loss.'}, 'Mercury': {'Good': 'Money, management, inheritance; praised.', 'Bad': 'Ineffective, lazy; blamed, quarreling due to assets.'}, 'Moon': {'Good': 'Sudden inheritance, finding money.', 'Bad': 'Passive and sick.'}},
    9: {'Saturn': {'Good': 'Initiates, chief priests; travel for benefit.', 'Bad': 'Recluses, anger at gods; confused religious opinions.'}, 'Jupiter': {'Good': 'Predicting future, priesthood; good religious reputation.', 'Bad': 'Unsteady, false speech; negligence in religion.'}, 'Mars': {'Good': 'Glory, unpunished; strong in travel.', 'Bad': 'Evil reports, difficult travels, illness.'}, 'Sun': {'Good': 'Building sacred things, religious authority.', 'Bad': 'Harm in travels; bad reputation, distress.'}, 'Venus': {'Good': 'Divine men, gifts from temples; travel with status.', 'Bad': 'Demon-afflicted, illicit sex; bad reports/journeys.'}, 'Mercury': {'Good': 'Priests, wizards; good journeys, true visions.', 'Bad': 'Seers, sacrificers; defamed in religion, bad assets.'}, 'Moon': {'Good': 'Living abroad, notable; benefiting from temples.', 'Bad': 'Wandering and dangers; temple servants.'}},
    10: {'Saturn': {'Good': 'Leaders, farmers; agriculture, building.', 'Bad': 'Bunglers, sorrow; blamed, low work.'}, 'Jupiter': {'Good': 'Athletes, famous, trusted; celebrated, respected.', 'Bad': 'Handsome but unstable; decreased assets, worry.'}, 'Mars': {'Good': 'Unstable, fearsome leaders; successful, favored by Sultan.', 'Bad': 'No accomplishments, fugitives; misfortune, violence.'}, 'Sun': {'Good': 'Rulers, leaders, dignity; increased rank, victorious.', 'Bad': 'Success through violence; fear from Sultan.'}, 'Venus': {'Good': 'Honored, musicians; honored by Sultan, delight.', 'Bad': 'Blamed, burdened, indecent; bad reputation.'}, 'Mercury': {'Good': 'Admirable, trusted; status from writing.', 'Bad': 'Changes, living abroad; accusation, loss.'}, 'Moon': {'Good': 'Rulers, successful, trusted.', 'Bad': 'Hardship, unsteady, error.'}},
    11: {'Saturn': {'Good': 'Middling goods over time; delight in friends.', 'Bad': 'Distress from children/siblings.'}, 'Jupiter': {'Good': 'Fortunate, renowned, authority; good way of life.', 'Bad': 'Diminished effectiveness; worries, distressed by friends.'}, 'Mars': {'Good': 'Many goods, dignity; increase in children/rank.', 'Bad': 'Feuding with friends and brothers.'}, 'Sun': {'Good': 'Lucky, noble; good condition, delight in friends.', 'Bad': 'Harms children; distress due to friends.'}, 'Venus': {'Good': 'Powerful, trusted; increase/delight in friends.', 'Bad': 'Sterility, unusual sexuality; hostility to friends.'}, 'Mercury': {'Good': 'Ingenious, accounts; befriend nobles, profit.', 'Bad': 'Spending, agents; hostility from friends, illness of children.'}, 'Moon': {'Good': 'Rulers, favored, good from parents.', 'Bad': 'Living abroad, estrangements, orphanhood.'}},
    12: {'Saturn': {'Good': 'Victory over enemies.', 'Bad': 'Loss of inheritance, mental disturbance; hardship from prison.'}, 'Jupiter': {'Good': 'Praise from subordinates; fights against superiors.', 'Bad': 'Illnesses, distress from enemies/confinement.'}, 'Mars': {'Good': 'Safety from enemies.', 'Bad': 'Illness, injury, dangers from slaves/criminals; exile.'}, 'Sun': {'Good': 'Good reputation, safety.', 'Bad': 'Long illnesses, defects, slavery; distress due to enemies.'}, 'Venus': {'Good': 'Benefit from underclass.', 'Bad': 'Ruined by women; leisure time and illness, punishment.'}, 'Mercury': {'Good': 'Managing big affairs; benefit from low work.', 'Bad': 'Danger from slaves; arrested unfairly, confinement.'}, 'Moon': {'Good': 'Luckiness/authority (with fortunes).', 'Bad': 'Short life, humble; bad for patrimony/travel.'}}
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
# sixteen for the inferiors (35-57), sixteen for the Moon (58-74). Sahl
# gives the same breakpoints independently in On Nativities Ch.1.22, 1-8,
# and Dykes' table there reports al-Biruni SS481-82 agreeing as well, so
# these are not one author's idiosyncrasy:
#
#   Saturn, Jupiter  burned to 6 deg,  under the rays to 15 deg
#                    (VII.2, 11-13; On Nativities 1.22, 1 and 6)
#   Mars             burned to 10 deg, under the rays to 18 deg east
#                    (VII.2, 11-13; On Nativities 1.22, 3 and 6)
#   Venus, Mercury   burned to 7 deg,  under the rays to 12 deg east,
#                    15 deg west (VII.2, 40, 48, 51-52; On Nativities
#                    1.22, 7-8). VII.2, 37 is now legible in the OCR and
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

def solar_phase(planet, lon, sun_lon):
    """Where a planet stands relative to the Sun, per Abu Ma'shar VII.2 and
    Sahl, On Nativities Ch.1.22. Returns (phase, side, elongation) where
    phase is one of 'Cazimi', 'Burned', 'Under the rays', 'Degrees of
    setting' or None, and side is 'eastern' (rising before the Sun, a
    morning star) or 'western'."""
    if planet == 'Sun':
        return None, None, 0.0
    signed = ((lon - sun_lon + 180.0) % 360.0) - 180.0
    elongation = abs(signed)
    side = 'eastern' if signed < 0 else 'western'
    idx = 0 if side == 'eastern' else 1
    if elongation <= CAZIMI_ORB:
        return 'Cazimi', side, elongation
    burned = SOLAR_BURNED_ORB.get(planet, (8.5, 8.5))[idx]
    if elongation <= burned:
        return 'Burned', side, elongation
    rays = MOON_RAYS_ORB if planet == 'Moon' else SOLAR_RAYS_ORB.get(planet, (15.0, 15.0))[idx]
    if elongation <= rays:
        return 'Under the rays', side, elongation
    setting = SOLAR_SETTING_DEGREES.get(planet)
    if side == 'western' and setting is not None and elongation <= setting:
        return 'Degrees of setting', side, elongation
    return None, side, elongation

def evaluate_accidental_dignities(planetary_data, natal_houses, sect, jd=None):
    """Accidental dignity scoring: house angularity (Whole Sign, anchored to
    the Ascendant, with the 6/8/12 malefic-house override), planetary joys,
    domain/hayz, motion & speed, and solar phase.

    The point weights (+5 angular, -5 combust, and so on) are this app's own
    convenience for ranking, not anybody's doctrine -- no source in hand adds
    these conditions up. What IS sourced is the geometry each test uses, and
    each of those carries its citation at the point of use."""
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
        is_above_horizon = (lon - ascendant) % 360 > 180.0

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
        # VII.1, 37), and again at VII.6, 13. Al-Qabisi I.78 has the same
        # (Dykes' note on VII.6, 13). The chart's sect does NOT have to match
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
        # hemisphere". An earlier version flipped him on both tests, which
        # required him to be in feminine signs -- a reading no text states.
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

        # --- Solar phase (Abu Ma'shar VII.2; Sahl, On Nativities 1.22) --
        phase, side, elongation = solar_phase(planet, lon, sun_lon)
        is_cazimi = phase == 'Cazimi'
        is_combust = phase == 'Burned'
        is_under_beams = phase == 'Under the rays'
        if is_cazimi:
            score += 5
            labels.append("Cazimi/in the heart (+5)")
        elif is_combust:
            score -= 5
            labels.append(f"Burned, {side} ({elongation:.1f} deg) (-5)")
        elif is_under_beams:
            score -= 2
            labels.append(f"Under the rays, {side} ({elongation:.1f} deg) (-2)")
        elif phase == 'Degrees of setting':
            labels.append(f"In the degrees of setting ({elongation:.1f} deg)")

        results[planet] = {
            'Accidental Score': score, 'House': house_num, 'Joy': is_joy, 'Hayz': is_hayz,
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
# Abu Ma'shar, Great Introduction VII.3, Fig. 105 ("bodies or orbs of
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
        # (Great Introduction VII.3, 6-11; VII.4, 5-8), so "is A inside B's
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
            # Abu Ma'shar VII.5, 24: "sometimes at the assembly both of the
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
        # RETROGRADATION" (VII.5, 24). His Cutting the Light turns on it --
        # "the light one IN MORE DEGREES goes retrograde and connects with
        # the heavy one through its retrogradation" (VII.5, 120), reversing
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
    """Abu Ma'shar, Great Introduction VII.4-5. Two flat activation
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
    # So for Abu Ma'shar a connection ends essentially at the exact degree.
    # His activation distances below are approach windows, not two-sided
    # orbs, and this test previously applied them to separating pairs as
    # well -- treating a planet 10 degrees past exact as still connected,
    # which 34 denies outright. The residue he does allow is a mixing of
    # natures, which this file already reports separately as the body
    # overlap, never as a connection.
    if row['motion'] == 'Separating' and abs(row['deviation']) > (1.0 / 60.0):
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
    50-60) and Abu Ma'shar (Great Introduction VII.3-4): Sextile/Square/
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
    """Collection of light (Sahl Ch.3, 28-30; Abu Ma'shar VII.5, 86, Fig.
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
    """Abu Ma'shar's wildness (Great Introduction VII.5, 79-82, Fig. 125):
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

# --- Natural connections (Abu Ma'shar, VII.5, 53-77) ----------------------
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
    one phenomenon, not independent subtypes. Management (76, "any
    application or connection hands over management") is the unconditional
    baseline for every Connected pair. Power (70-72) is additionally
    granted when the applying planet is itself in its own house,
    exaltation, or triplicity at the time of connecting. Nature (73-74,
    confirmed by the worked example's own footnote -- "that is, in
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

# --- Forward simulation -- Great Introduction VII.5's motion-dependent
# conditions (Emptiness of Course, Revoking, Resistance, Escape, Returning's
# retrograde case, Recompense) describe what happens as the chart moves
# forward, not the birth moment alone. This steps the ephemeris ahead and
# records each planet's sign-exit and station days, shared by every
# detector below rather than recomputed per-condition.

def _bisect_crossing(test_fn, day_lo, day_hi, tol=0.02, max_iter=40):
    """Assumes exactly one transition of test_fn's boolean value inside
    [day_lo, day_hi]; returns the midpoint of the final bracket."""
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
            sign0 = int(lons[i] // 30)
            if int(lons[i + 1] // 30) != sign0:
                def _sign_test(day, _pid=pid, _sign0=sign0):
                    res, _ = swe.calc_ut(jd + day, _pid)
                    return int(res[0] // 30) == _sign0
                events[p]['sign_exits'].append(_bisect_crossing(_sign_test, days[i], days[i + 1]))
            if (speeds[i] > 0) != (speeds[i + 1] > 0):
                kind = 'first' if speeds[i] > 0 else 'second'
                def _speed_test(day, _pid=pid, _positive=(speeds[i] > 0)):
                    res, _ = swe.calc_ut(jd + day, _pid)
                    return (res[3] > 0) == _positive
                events[p]['stations'].append((_bisect_crossing(_speed_test, days[i], days[i + 1]), kind))

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
        if int(_lon_at(sim, planet, day + 0.02) // 30) == sign_idx % 12:
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
    """Revoking (Abu Ma'shar VII.5, 117, Fig. 137): "a planet is
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
            new_sign = int(_lon_at(sim, slow, exit_day + 0.02) // 30)
            # "when the one handing over changes [to THAT NEXT SIGN]" -- the
            # applicant follows it across the same boundary, which is what
            # Fig. 139 shows: Venus and Mercury are both in Virgo, Mercury
            # crosses into Libra, and Venus's own next crossing is into Libra
            # behind him. So it must be the applicant's NEXT sign change, not
            # any later arrival in that sign -- otherwise the Moon qualifies
            # against everything, since she re-enters every sign each month.
            next_exit = next((d for d in sim['events'][fast]['sign_exits'] if d > exit_day), None)
            if next_exit is None or int(_lon_at(sim, fast, next_exit + 0.02) // 30) != new_sign:
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
            if best is not None:
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

    ABU MA'SHAR (Great Introduction VII.5, 129-133). Wider on every axis.
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
# Whether the carryover applies at all twelve cusps or at the stakes only.
# Sahl states it twice for the stakes (Aphorism #44, 88; On Nativities
# 1.22, 9) and once for every house -- On Nativities 1.18, 19: "if there
# were 5 degrees between a planet and the degree of the Ascendant from
# behind it ... its strength will be in the Ascendant, and it will be fit
# for releasing; AND LIKEWISE IN ALL OF THE HOUSES" (Dykes: "This is
# Ptolemy's 5-degree rule"). The stakes reading stays the default because
# two of the three statements give it; the switch flips the advancing
# verdict of Sahl 83 for about 6% of placements, all succedent-to-cadent.
FIVE_DEGREE_ALL_CUSPS = False

def get_effective_house(longitude, cusps, angles_only=None):
    """Quadrant house with the five-degree carryover applied: a planet
    within 5 degrees before a cusp is counted as already in that house.

    MEASURED IN ECLIPTIC LONGITUDE, WHICH IS AN APPROXIMATION. Dykes' note
    on Fifty Aphorisms #44 says the five degrees are reckoned "AS MEASURED
    IN DIURNAL MOTION, hence Sahl's reference to the 'rear' of the stake" --
    that is, in right ascension along the diurnal circle, not in zodiacal
    degrees. The two coincide only near the equinoctial points and diverge
    with latitude and with the obliquity of the rising sign. Implementing
    it properly needs oblique-ascension geometry, which this file does not
    yet have; until then this is a longitude proxy and is named as one
    wherever it is reported. It affects Sahl 83 and Abu Ma'shar 39 and 42.

    Two of Sahl's three statements are about the stakes (Aphorism #44, 88;
    On Nativities 1.22, 9), and the transitions they describe (12th into
    1st, 3rd into 4th, 6th into 7th, 9th into 10th) are the cadent-to-
    angular ones, which is why the rule is phrased as not FALLING from the
    stake. The third, On Nativities 1.18, 19, ends "and likewise in all of
    the houses". angles_only defaults to the stakes reading via
    FIVE_DEGREE_ALL_CUSPS; the all-cusps reading is Sahl's too, not a later
    generalisation, and is one switch away.

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
        'triplicity_participating': triplicity['Participating'],
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
      'Preventional', and per medieval practice the Syzygy degree is taken
      from whichever luminary was above the horizon (in the diurnal
      hemisphere) at that prenatal Full Moon, defaulting to the Moon if
      that can't be determined.

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
    _, ascmc_syzygy = swe.houses(jd_syzygy, lat, lon, b'B')
    asc_syzygy = ascmc_syzygy[0]
    sun_above_horizon = (sun_lon - asc_syzygy) % 360 > 180.0
    moon_above_horizon = (moon_lon - asc_syzygy) % 360 > 180.0
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
def calculate_chronocrats(jd_utc, lat, lon, local_dt, utc_offset_hours=0.0):
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
        cycle_offset = local_dt.hour          # 0-23, one step per civil hour

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
#   DYKES ONLY TABULATES. Three Lots for work (his Fig. 63), after: "Sahl
#   quietly switches to Masha'allah's treatise on Lots ... and now he is
#   substituting another one WITHOUT TELLING US that the formula is
#   different! So we now have three different Lots, ostensibly for the same
#   topic." All three are shown.
#
# NOTE ON THE SOURCE TEXT. Every formula here is taken from the running
# prose or a footnote, never from one of the summary tables: the OCR
# mangles their glyph columns. Fig. 63's row for Ch. 10.2.5 renders as
# "Mercury -> Venus" where the body text at 10.2.5, 1 plainly reads "from
# Saturn to the Moon". Where prose and table disagree, the prose is used
# and the disagreement is noted.
#
# A point may be a planet, 'Ascendant', 'cuspN' (the Nth place -- see
# LOT_HOUSE_CUSP), 'lordN' (the domicile lord of the Nth whole-sign house),
# or another Lot by id. Lots that feed other Lots are listed before them.
#
# "The second place", "the degree of the eighth place", "the ninth" (2.15,
# 1; 8.6, 1; 9.1, 9): the text is whole-sign throughout, and Dykes' note 207
# on 4.14 glosses the assets Lot as "from the lord of the second to the
# second". In whole signs the degree of the Nth place is the Ascendant's
# own degree carried into the Nth sign; the quadrant cusp is the other
# reading, and was the only one computed until now. Sidebar switch.
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
              '73 and Ch. 11.1, 5 confirm the identity) but nowhere in the corpus states '
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
         note='"Taken by night and day." The note on Ch. 3.1.2, 1 adds that in Dorotheus '
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
         source='Sahl, On Nativities Ch. 5.2, 2 and 8',
         confidence='attested',
         note='A separate Lot for WHEN, not how many: "when Jupiter reaches this Lot in '
              'his course and transit."'),
    dict(id='marriage_men', topic='Marriage', name="Lot of men's marriage",
         start='Saturn', end='Venus', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 223 and Ch. 7.4, 44',
         confidence='settled', note='Stated twice, identically.'),
    dict(id='marriage_women', topic='Marriage', name="Lot of women's marriage",
         start='Venus', end='Saturn', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 7.1, 224 and Ch. 7.4, 44',
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
         source='Sahl, On Nativities Ch. 8.6, 1',
         confidence='settled',
         note='PROJECTED FROM SATURN, not the Ascendant: "taken by night and day from the '
              'Moon to the degree of the eighth place, AND CAST OUT FROM SATURN."'),
    dict(id='killer', topic='Death', name='Lot of the killer',
         start='lord1', end='Moon', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 8.2, 17',
         confidence='attested',
         note='"Taken from the lord of the Ascendant to the Moon by day (and by night the '
              'reverse), and is cast out from the Ascendant."'),
    dict(id='travel', topic='Travel', name='Lot of travel',
         start='lord9', end='cusp9', project='Ascendant', reverse_at_night=False,
         source='Sahl, On Nativities Ch. 9.1, 9',
         confidence='settled',
         note='"Taken by night and day from the lord of the ninth to the ninth."'),
    dict(id='work_action', topic='Work', name='Lot of work (action / praxis)',
         start='Mercury', end='Mars', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 10.1.1, 14',
         confidence='variant (one of three)',
         note="The Greek Lot of action. Dykes' Fig. 63 names it Work in Sahl and BA, "
              "\"managers, viziers, and Sultans\" in Abu Ma'shar VIII.4."),
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
         start='Sun', end='Saturn', project='Ascendant', reverse_at_night=False,
         source="Sahl, On Nativities Ch. 10.2.5, 4-14 (Masha'allah)",
         confidence='variant (one of three)',
         note='Sahl switches treatises mid-chapter without saying so. The note: '
              'Masha\'allah "defines this in the same way as the Lot of fathers '
              '(Sun-Saturn)". Identical in form to the Lot of the father; Fig. 63\'s glyph '
              'column reads Sun-Mercury, but the prose is followed here.'),
    dict(id='friends', topic='Friends', name='Lot of friends',
         start='Moon', end='Mercury', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 11.1, 5',
         confidence='settled',
         note='The note on Ch. 10.2.9 identifies it: "the Moon-Mercury Lot (projected from '
              'the Ascendant, reversed by night), which is identical to Dorotheus\'s Lot '
              'of friendship."'),
    dict(id='desire', topic='Friends', name='Lot of desire',
         start='fortune', end='spirit', project='Ascendant', reverse_at_night=True,
         source='Sahl, On Nativities Ch. 11.4, 5',
         confidence='attested; identical in form to the Lot of passion',
         note='"By day from the Lot of Fortune to the Lot of Spirituality ... and by night '
              'the converse."'),
    dict(id='necessity', topic='Friends', name='Lot of necessity',
         start='spirit', end='fortune', project='Ascendant', reverse_at_night=True,
         source="Sahl, On Nativities Ch. 11.5 (Dykes' note 62)",
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

def _lot_point(name, planetary_data, asc, cusps, sect, resolved):
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
        if LOT_HOUSE_CUSP == LOT_HOUSE_CUSP_OPTIONS[1]:
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
    a = _lot_point(start, planetary_data, asc, cusps, sect, resolved)
    b = _lot_point(end, planetary_data, asc, cusps, sect, resolved)
    p = _lot_point(d['project'], planetary_data, asc, cusps, sect, resolved)
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
                                         planetary_data['Sun']['longitude'])
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
                        + (f'  [{LOT_HOUSE_CUSP}]' if 'cusp' in (start, end, d['project'])
                           or start.startswith('cusp') or end.startswith('cusp') else '')),
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
    ("Abu Ma'shar VII.5, 29-31", "Priority among several planets connecting from a "
     "single degree and minute, decided by claims in the handing-over sign, with the "
     "bound lord breaking ties. Recovered with p. 452; computable, not yet built."),
    ("Abu Ma'shar VII.5, 38-52", "Connection by LATITUDE, in three kinds -- assembly "
     "at equal latitude with one eclipsing the other, and two further kinds. Recovered "
     "with pp. 452-453. Latitude is available in the chart data but unused for "
     "connection."),
    ("Abu Ma'shar VII.5, 67-77, the pairs the notes say he omits", "The natural "
     "connections are built from the sign pairs 56 and 67-75 enumerate. Three pairs "
     "the complete schemes contain are NOT in his lists and are not added: "
     "Aquarius-Scorpio (the antiscia family; 67-75 stops at five pairs), and the "
     "'agreeing in manner' affinities Aries-Scorpio, Taurus-Libra (note 163) and "
     "Aquarius-Capricorn (note 164). Adding them would be inference from the family, "
     "not from the text in hand."),
    ("Abu Ma'shar VII.5, 97-100", "Handing over TWO NATURES. The Sahl handing-over "
     "table is not a substitute."),
    ("Abu Ma'shar VII.5, 104-116", "The full returning tree, with its suitability and "
     "corruption grades. Only Sahl's two manners (Ch.3, 65-69) are implemented."),
    ("Abu Ma'shar VII.6, 13 and 36", "The masculine and feminine DEGREES, alongside "
     "the signs. No table for them in this corpus."),
    ("Abu Ma'shar VII.6, 52", "Each planet's OWN nodes (\"their own Dragons\"). Only "
     "the Moon's are computed."),
    ("Abu Ma'shar VII.7", "The casting of rays according to Ptolemy. The chapter "
     "begins on a page not photographed."),
    ("Abu Ma'shar VII.3, 2 / VI.26, 3", "The ADVANCING AND WITHDRAWING QUADRANTS as a "
     "condition in its own right (ASC to MC and DSC to IC advancing: primary motion "
     "toward the meridian). Read from the margin of the Figure 90 reshoot and Dykes' "
     "note on On Nativities 10.3; distinct from Sahl 83, which is his own Ch.3, 4. "
     "Recorded as ADVANCING_BY_QUADRANT_FIG90, not yet scored."),
    ("Abu Ma'shar VII.5, 32-33", "Mixing of natures BY RAY across a sign boundary "
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
     "Dykes' note 57)."),
    ("Sahl, On Nativities Ch. 2.2", "The THIRTY FIXED STARS for eminence, with "
     "positions for Sahl's epoch (needs precession)."),
    ("Sahl, On Nativities Ch. 2.6 and 4.9", "Uses of the TWELFTH-PARTS beyond the "
     "Moon's (luminaries, Ascendant, infortunes)."),
    ("Sahl, On Nativities: further Lots", "Constitution (1.34, 13, recovered p. 358, "
     "'foundation' uncertain); male/female (3.12, 20); Venus to the 7th place "
     "(7.1, 10 and 145); Sun to Moon projected from Venus (7.4, 8); religion "
     "(9.5, 3, identity disputed); riding animals (12.2 fn. 18)."),
]

# --- Special Degrees & Conditions ----------------------------------------

# Classical "wells" (pitted degrees) by sign, per Abu Ma'shar, The Great
# Introduction to Astrology V.21 (Dykes translation, Fig. 98).
WELLED_DEGREES = {
    'Aries': [6, 11, 17, 23],
    'Taurus': [5, 13, 18, 24, 25, 26],
    'Gemini': [2, 13, 17, 26, 30],
    'Cancer': [12, 17, 23, 26, 30],
    'Leo': [6, 13, 15, 22, 23, 28],
    'Virgo': [8, 13, 16, 21, 25],
    'Libra': [1, 7, 20, 30],
    'Scorpio': [9, 10, 17, 22, 23, 27],
    'Sagittarius': [7, 12, 15, 24, 27, 30],
    'Capricorn': [2, 7, 17, 22, 24, 28],
    'Aquarius': [1, 12, 17, 23, 29],
    'Pisces': [4, 9, 24, 27],
}

def evaluate_special_degrees(planetary_data):
    """Flags planets in the Via Combusta (15 Libra-15 Scorpio), a classical
    welled/pitted degree of their current sign, or one of Sahl's two
    sign-boundary conditions.

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

        if 195.0 <= lon <= 225.0:
            conditions.append("Via Combusta (external convention, not from these sources)")

        sign = get_zodiac_sign(lon)
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

# --- Abu Ma'shar's Planetary Condition -- Great Introduction VII.6 -------
# (with supporting data/mechanics from VII.3-4 and V.20)

FORTUNES = {'Jupiter', 'Venus'}
INFORTUNES = {'Saturn', 'Mars'}

# Great Introduction V.20, Figs. 60-61: bright/dusky/empty/dark degrees by
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

# Great Introduction VII.3, 19-20: for the five non-luminaries, the domicile
# in which their nature is "moderated" (simply fortunate) versus the other,
# "contrary" domicile (suitable, but of a lesser grade).
PREFERRED_DOMICILE = {'Saturn': 'Aquarius', 'Jupiter': 'Sagittarius', 'Mars': 'Scorpio', 'Venus': 'Taurus', 'Mercury': 'Virgo'}

# Great Introduction VI.26, 3-4, Fig. 90: quadrants alternate Advancing/
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
ADVANCING_BY_QUADRANT_FIG90 = {4, 5, 6, 10, 11, 12}   # Abu Ma'shar VII.3, 2 / VI.26, 3; not Sahl 83

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
    fortune direction, Great Introduction VII.6, 5)."""
    with doctrine(SAHL):
        rows = _pairwise_configurations(planetary_data)
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
        results = []
        for planet in planetary_data:
            if planet == 'North Node':
                continue
            for label, enclosing_set in (('Infortunes', INFORTUNES), ('Fortunes', FORTUNES)):
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
    the course glossary -- and takes this function's natal_houses argument.
    On a sample of 414 charts the two readings of advancement disagree for
    a third of all planet placements.

    Distinct from the existing Abu Ma'shar VII.6-based Planetary Condition
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
                and (({r['p1'], r['p2']} - {planet}) & INFORTUNES)
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
                # cadency. The Course Glossary's own Cadent entry says so:
                # "3rd, 6th, 9th, 12th. But see also FALLING AWAY FROM, WHICH
                # IS EQUIVALENT TO AVERSION" -- and its Aversion entry is the
                # 2nd, 6th, 8th and 12th. Sahl keeps the two apart himself at
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
            # the course glossary defines advancement as "moving by primary
            # motion toward an axial degree."
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
            # WILL NOT BE FIT"; Mars at 15 degrees (1.22, 3 and its note). The
            # Course Glossary's Eastern (2) is "outside the Sun's rays and
            # visible." An earlier version tested only which side of the Sun the
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

    Distinct from the existing Abu Ma'shar VII.6-based Planetary Condition
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
                if other in INFORTUNES and _is_connected(r):
                    _hit94.append(other)
            if _hit94:
                labels.append(f"Connecting with {' and '.join(sorted(_hit94))} by assembly, square, or opposition (94)")

            # (95) Enclosed between the two infortunes -- separating from one,
            # connecting with the other (Sahl's own Enclosure, 119-123).
            is_enc, severe, sep, con = _sahl_enclosed(planet, INFORTUNES, rows, blocking_pairs)
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
                    other_rulers = get_essential_rulers(planetary_data[other]['longitude'])
                    if planet in (other_rulers['domicile'], other_rulers['exaltation']):
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
                labels.append('With the Head or Tail, without latitude (99; 12 deg orb from Ch.3, 107 and On Nativities 1.21, 12)')

            # (100) Inverted: in the seventh sign from its own house (Detriment).
            if ess['Detriment']:
                labels.append('Inverted, in the seventh sign from its own house (100)')

            if labels:
                results.append({'Planet': planet, 'Weakness Testimonies': ', '.join(labels), 'Count': len(labels),
                                'Labels': labels})
        return results

def evaluate_abu_mashar_condition(planetary_data, natal_houses, sect, essential, accidental, jd, ascendant_lon, sim=None):
    """Planetary condition per Abu Ma'shar's Great Introduction VII.6: good
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

    Still not implemented, for want of a source in hand rather than by
    choice: the masculine and feminine DEGREES that 13 and 36 name
    alongside the signs (no table for them in the available material), and
    52's "their own Dragons" -- each planet's own nodes, where only the
    Moon's are computed here."""
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
            if averted_from(planet, INFORTUNES):
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
            _e_lim, _w_lim = SOLAR_RAYS_ORB.get(planet, (15.0, 15.0))
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
            # its current sign (Great Introduction VII.5, 78, Fig. 124),
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
                      if is_eastern_of_sun and SOLAR_BURNED_ORB[planet][0] <= abs(signed_from_sun) < SOLAR_RAYS_ORB[planet][0] else []) + \
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
                and ({r['p1'], r['p2']} - {planet}) & INFORTUNES
                and abs(r['deviation']) < bound_width
                for r in rows
            )
            if close_to_infortune:
                negative.append(f'Connected to an infortune, within a bound ({bound_width:.0f} deg) (47-48)')
            term_lord = get_essential_rulers(lon)['term']
            if SIGN_TO_DOMICILE.get(sign) in INFORTUNES or term_lord in INFORTUNES:
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
                if other in INFORTUNES and forward in (10, 11):
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
            is_enc, enc_kind, dissolver = _abu_mashar_enclosed(planet, INFORTUNES, planetary_data, rows)
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

    NOTE ON PROVENANCE: both authors USE twelfth-parts -- Abu Ma'shar makes
    the Moon's twelfth-part falling to Saturn or Mars her fifth corruption
    (VII.6, 68) and counts assembly with them among the ways planets meet
    (VII.4, 2), and Sahl devotes On Nativities Ch.2.6 to them -- but neither
    passage in hand states the formula. This is the standard Hellenistic and
    Arabic construction, supplied from convention rather than from the texts
    available to this project."""
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
        for infortune in sorted(INFORTUNES):
            row = next((r for r in rows if {r['p1'], r['p2']} == {'Moon', infortune}), None)
            if row and row['aspect_name'] != 'Aversion':
                labels.append(f"With or looked at by {infortune} (67)")
                break

        # [5] (68) In the twelfth-part of Saturn or Mars -- the twelfth-part
        # falling in a sign those two rule.
        tp_sign = _twelfth_part_sign(lon)
        tp_lord = SIGN_TO_DOMICILE.get(tp_sign)
        if tp_lord in INFORTUNES:
            labels.append(f'In the twelfth-part of {tp_lord} ({tp_sign}) (68)')

        # [6] (69) With the Head or Tail within 12 degrees.
        if node_dist <= 12.0:
            labels.append('With the Head or Tail, within 12 degrees (69)')

        # [7] (70) "Southern OR going down in the south" -- two states, as at 38.
        if lat < 0:
            labels.append('Going down in the south (70)' if moon.get('speed_in_lat', 0.0) < 0
                          else 'Southern in latitude (70)')

        # [8] (71) In the burned path, "and that is Libra and Scorpio" -- the
        # whole two signs here, wider than the 15 Libra to 15 Scorpio span the
        # Via Combusta table uses.
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
    numbered eleven-item list (Great Introduction VII.6, 63-74) without
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
               and (row['p1'] in INFORTUNES or row['p2'] in INFORTUNES)
               for row in rows):
            hit(106, 'Assembled with, square, or opposed by an infortune')
        blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
        is_enc, severe, _sep, _con = _sahl_enclosed('Moon', INFORTUNES, rows, blocking_pairs)
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

        # [8] (110) In the burned path -- Sahl's own wording narrows this to
        # the end of Libra and the beginning of Scorpio specifically (not the
        # full two signs), matching the alternate 19-Libra-to-3-Scorpio band
        # footnoted there.
        if HARSH_BURNED_PATH[0] <= lon < HARSH_BURNED_PATH[1]:
            hit(110, 'In the burned path, end of Libra/beginning of Scorpio')

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


def evaluate_house_lords(planetary_data, ascendant_lon):
    """For each Whole Sign topical house (1-12), find its domicile lord and
    the WSH house that lord is physically placed in, then look up
    Masha'allah's delineation for that [placed_in][ruled_house] pairing."""
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

        results.append({
            'Topical House': house_i,
            'Cusp Sign': cusp_sign,
            'Domicile Lord': domicile_lord,
            'Placed in (WS place)': placed_in,
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

def calculate_time_lords(ascendant_lon, birth_date, target_date):
    """Annual Profection (Lord of the Year) and a symbolic 1-degree-per-year
    direction of the Ascendant through the Egyptian bounds.

    The second of these was previously called a "Ptolemaic Distribution."
    It is not one -- see the note on the row it returns."""
    # Age in COMPLETED CIVIL ANNIVERSARIES, not elapsed days over a mean
    # year length. Profection turns on the birthday: dividing by 365.2425
    # let the sign advance up to a day early or late around it, and drifts
    # further the older the native is.
    days_alive = (target_date - birth_date).days
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

# --- Structure: the course's own order, with a lesson gate ----------------
# This was grouped by KIND OF COMPUTATION -- chart, then dignity, then
# connections -- while TNAC is taught by lesson, and sixteen of the
# thirty-one tables are Lesson 17 material sitting in a single subtab with
# no structure of their own. That mismatch is why the tables read as a wall
# rather than as a sequence.
#
# Pages follow the syllabus. The gate hides what the course has not reached,
# so the app grows alongside it; everything is still computed, and the gate
# defaults to the whole syllabus. Its stops are the pages: each label names
# the lessons a page covers, and the number is the threshold that page
# checks. Rendered first so it sits directly under the page navigation,
# which st.navigation always draws at the top of the sidebar.
LESSONS = [("Lessons 3-5: chart and calculation", 5),
           ("Lessons 9-13: dignities, sect, places", 9),
           ("Lessons 14-17: configurations", 14),
           ("Lesson 18: Lots", 18),
           ("Lessons 19-20: lunation and victors", 19),
           ("Part 2: timing", 99)]
gate = dict(LESSONS)[st.sidebar.selectbox(
    "Show material through", options=[l for l, _ in LESSONS], index=len(LESSONS) - 1,
    key="lesson_gate",
    help="A study aid, not a filter on correctness -- everything is still "
         "computed. It only hides what the course has not covered yet. Move "
         "it forward as you progress.")]

st.sidebar.header("Calculation Parameters")

if "saved_charts" not in st.session_state:
    st.session_state["saved_charts"] = load_saved_charts()

def _apply_selected_chart():
    """on_change callback: runs before the script reruns, so writing into
    these session_state keys here makes the widgets below pick up the
    loaded values on this same rerun."""
    name = st.session_state.get("chart_picker")
    if name and name != "-- New Chart --":
        entry = st.session_state["saved_charts"].get(name, {})
        if "date_string" in entry:
            st.session_state["date_input_key"] = entry["date_string"]
        if "time_string" in entry:
            try:
                h, m, s = (int(x) for x in entry["time_string"].split(":"))
                st.session_state["time_input_key"] = time(h, m, s)
            except (ValueError, KeyError):
                pass
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
load_col, del_col = st.sidebar.columns([3, 1])
load_col.selectbox("\U0001F4C2 Load Saved Chart", chart_options, key="chart_picker", on_change=_apply_selected_chart)
if del_col.button("\U0001F5D1", help="Delete the selected saved chart"):
    picked = st.session_state.get("chart_picker")
    if picked and picked != "-- New Chart --" and picked in st.session_state["saved_charts"]:
        del st.session_state["saved_charts"][picked]
        write_saved_charts(st.session_state["saved_charts"])
        st.rerun()

date_string = st.sidebar.text_input("Local Date (YYYY-MM-DD)", "1240-05-23", key="date_input_key")
try:
    parsed_datetime = datetime.strptime(date_string, "%Y-%m-%d")
    input_date = parsed_datetime.date()
except ValueError:
    st.sidebar.error("Invalid syntax. Enforce YYYY-MM-DD format (e.g., 1240-05-23).")
    st.stop()

input_time = st.sidebar.time_input("Local Time", time(14, 30), key="time_input_key")

time_standard = st.sidebar.selectbox(
    "Time standard",
    ["LMT (Local Mean Time)", "Standard time (pytz)"],
    help="Use LMT for historical charts prior to the late 19th century, when local mean time was the civil standard and modern timezone boundaries didn't yet exist. Standard time relies on a timezone's principal-city offset, which can be several minutes off from a birthplace's true solar longitude.",
)

st.sidebar.markdown("---")
st.sidebar.header("Location Data")

manual_coords = st.sidebar.checkbox("Manual Coordinate Entry", key="manual_coords_key")

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
    city_search = st.sidebar.text_input("City Search", default_loc, key="location_input_key")

    if city_search:
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

new_chart_name = st.sidebar.text_input("Chart Name (for saving)", value="", placeholder="e.g. Test Chart 1240")
if st.sidebar.button("\U0001F4BE Save This Chart"):
    trimmed_name = new_chart_name.strip()
    if trimmed_name:
        st.session_state["saved_charts"][trimmed_name] = {
            "date_string": date_string,
            "time_string": input_time.strftime("%H:%M:%S"),
            "location_query": location_query,
            "lat": lat,
            "lon": lon,
        }
        if write_saved_charts(st.session_state["saved_charts"]):
            st.sidebar.success(f"Saved '{trimmed_name}'.")
        else:
            st.sidebar.error("Could not write saved_charts.json to disk.")
    else:
        st.sidebar.warning("Enter a name before saving.")

st.sidebar.markdown("---")

target_date_string = st.sidebar.text_input("Target Date for Prediction (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
try:
    target_date = datetime.strptime(target_date_string, "%Y-%m-%d").date()
except ValueError:
    st.sidebar.error("Invalid Target Date syntax.")
    st.stop()

# --- Configurable readings: read here, set on the pages ------------------
# The Connection rule and the five readings the sources leave open are set
# by controls on the page and table each one affects (Configurations, Chart,
# Dignities, Lots), and remembered across navigation in a store key that
# _persist() keeps up to date. They are READ here, at the top level, because
# the engine functions below run before any page function does and read
# these globals at call time. The widget key is preferred when present: on
# the rerun a change triggers, the widget already carries the new value
# while the store still holds the old one.
def _reading(widget_key, store_key, default):
    return st.session_state.get(widget_key, st.session_state.get(store_key, default))

CONNECTION_PROFILE = _reading("connection_rule", "_connection_rule", "Sahl")
FIVE_DEGREE_ALL_CUSPS = _reading("five_degree_all_cusps", "_five_degree_all_cusps", False)
EASTERN_RULE = _reading("eastern_rule", "_eastern_rule", EASTERN_RULE_OPTIONS[0])
MOON_RAYS_ORB = 15.0 if _reading("moon_rays_15", "_moon_rays_15", False) else 12.0
DOMAIN_RULE = _reading("domain_rule", "_domain_rule", DOMAIN_RULE_OPTIONS[0])
LOT_HOUSE_CUSP = _reading("lot_house_cusp", "_lot_house_cusp", LOT_HOUSE_CUSP_OPTIONS[0])


if location_query and lat is not None and lon is not None:
    st.sidebar.success(f"**Resolved:** {lat:.4f}, {lon:.4f}")

    local_dt = datetime.combine(input_date, input_time)

    if time_standard == "LMT (Local Mean Time)":
        # 15 degrees of longitude = 1 hour of time. East is +, West is -.
        offset_hours = lon / 15.0
        dt_utc = local_dt - timedelta(hours=offset_hours)
        tz_name = "LMT"
        offset_str = (
            f"{'+' if offset_hours >= 0 else '-'}"
            f"{abs(int(offset_hours)):02d}:{int((abs(offset_hours) * 60) % 60):02d}:{int((abs(offset_hours) * 3600) % 60):02d}"
        )
        utc_offset_hours = offset_hours
        st.sidebar.info(f"**Time standard:** Exact LMT\n**UTC offset:** {offset_str}")
    else:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        if tz_name:
            local_tz = pytz.timezone(tz_name)
            # is_dst=None makes pytz RAISE on the two clock times a named
            # zone cannot resolve on its own: the hour that occurs twice at
            # a DST fall-back, and the hour that never occurs at spring
            # forward. Without it pytz silently picks one, which moves the
            # chart by an hour with no indication that a choice was made.
            try:
                localized_dt = local_tz.localize(local_dt, is_dst=None)
            except pytz.exceptions.AmbiguousTimeError:
                st.sidebar.error(
                    f"**{local_dt:%Y-%m-%d %H:%M}** happens twice in {tz_name} "
                    "(daylight-saving fall-back). Choose LMT, or enter a time "
                    "outside the repeated hour."
                )
                st.stop()
            except pytz.exceptions.NonExistentTimeError:
                st.sidebar.error(
                    f"**{local_dt:%Y-%m-%d %H:%M}** does not exist in {tz_name} "
                    "(the clocks jump over it at daylight-saving spring-forward). "
                    "Check the recorded time."
                )
                st.stop()
            dt_utc = localized_dt.astimezone(pytz.utc)
            # This is the OFFSET, not the UTC clock time -- an earlier
            # version printed dt_utc's own time under the label "UTC offset".
            _off = localized_dt.utcoffset()
            utc_offset_hours = _off.total_seconds() / 3600.0
            _sign = '+' if utc_offset_hours >= 0 else '-'
            _tot = int(abs(_off.total_seconds()))
            st.sidebar.info(
                f"**Timezone:** {tz_name}\n**UTC offset:** "
                f"{_sign}{_tot // 3600:02d}:{(_tot % 3600) // 60:02d}"
                f"\n**UTC time:** {dt_utc:%Y-%m-%d %H:%M:%S}"
            )

    if tz_name:
        chart_data = calculate_traditional_chart(dt_utc, lat, lon)
        p_data = chart_data['planetary_data']
        sect = chart_data['sect']

        essential = evaluate_essential_dignities(p_data, sect)
        accidental = evaluate_accidental_dignities(p_data, chart_data['houses'], sect, chart_data['julian_day'])
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
        chronocrats = calculate_chronocrats(chart_data['julian_day'], lat, lon, local_dt, utc_offset_hours)
        classical_lots = calculate_classical_lots(chart_data['ascendant'], p_data['Sun']['longitude'], p_data['Moon']['longitude'], sect)
        topical_lots = calculate_topical_lots(p_data, chart_data['ascendant'], chart_data['houses'], sect)
        special_degrees = evaluate_special_degrees(p_data)
        house_lords_data = evaluate_house_lords(p_data, chart_data['ascendant'])
        victors_data = evaluate_victors(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'],
                                         syzygy['syzygy_longitude'], sect, chronocrats)
        planets_in_houses_data = evaluate_planets_in_houses(p_data, abu_mashar_condition, chart_data['ascendant'])
        time_lords_data = calculate_time_lords(chart_data['ascendant'], input_date, target_date)

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
                                       chronocrats=chronocrats)
        svg_wide = generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, local_dt, tz_name,
                                       wide=True, chronocrats=chronocrats)

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
            """Render-independent memory for a page widget. Call AFTER the widget."""
            if widget_key in st.session_state:
                st.session_state[store_key] = st.session_state[widget_key]
            return st.session_state.get(store_key, default)

        def _reading_checkbox(label, widget_key, store_key, help=None):
            st.checkbox(label, value=st.session_state.get(store_key, False), key=widget_key, help=help)
            return _persist(widget_key, store_key, False)

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
            cap_col, lay_col = st.columns([3, 1], vertical_alignment="bottom")
            cap_col.caption("Lessons 3-5: chart identification, measurement, astronomy.")
            with lay_col:
                wheel_layout = _reading_radio(
                    "Wheel layout", WHEEL_LAYOUT_OPTIONS, "wheel_layout", "_wheel_layout",
                    help="Square: the wheel beside the header metrics. Wide: the wheel with a "
                         "positions panel across the page. Hover either and use the expand "
                         "arrows for a full-window view.")
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
            if wheel_layout == WHEEL_LAYOUT_OPTIONS[1]:
                st.image(svg_wide, width='stretch')
                side_col = st.container()
            else:
                wheel_col, side_col = st.columns([1, 1])
                with wheel_col:
                    st.image(svg_code, width=400)
            with side_col:
                st.caption(
                    "A TNAC study companion: work the homework by hand, then check it here and "
                    "see the doctrine applied to a real chart.  \n"
                    "Enter a chart in the sidebar; saved charts load from the top of it.  \n"
                    "Pages follow the course's lesson order. Sahl's *Introduction* is the course "
                    "text; Abu Ma'shar's *Great Introduction* VII is the supplement."
                )
                # Two metrics per row: three across truncates "Mercury".
                hdr1 = st.container()          # full width: the value is a long word
                hdr2, hdr3 = st.columns(2)
                hdr4, _ = st.columns(2)
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
                                  help="Sahl, On Nativities 1.19, 6 gives 15 degrees for the Moon; Abu Ma'shar VII.2, 61 "
                                       "and 72-73 give 12. Affects: the Solar phase column here, and on the Configurations "
                                       "page Weakness (93), Planetary Condition and Corruption of the Moon. Full text on the Sources page.")
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
                phase, side, elong = solar_phase(p, lon_p, p_data['Sun']['longitude'])
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
                      glance='Flags planets in the Via Combusta (15 Libra-15 Scorpio, a historically "burnt" span), a classical welled/pitted degree of their current sign (Abu Ma\'shar, Great Introduction V.21), or one of Sahl\'s two sign-boundary conditions.',
                      notes='ENTERING: "every planet which is at the beginning of a sign is weak until it is firmly established in it and comes to be 5 degrees within it" (Fifty Aphorisms #44, 87), repeated in On Nativities Ch.1.22, 9. This is the other half of the five-degree rule that also governs advancement.\n\nLEAVING: "if a planet came to be in the last degree of the sign, then its strength has already gone away from that sign, and its strength is in the next sign ... like a man putting his foot on the threshold of his door. And if a planet was in the twenty-ninth degree, then indeed the strength of the planet IS in that sign" (Fifty Aphorisms #15, 31-33) -- so the 29th degree still counts and only the 30th has left.')
            _absent(_gap)

        def page_dignities():
            st.header("Dignities and places")
            st.caption("Lessons 9-13: dignities and management, sect, places, lords of places.")
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
                               help="Abu Ma'shar VII.1, 37 / VII.6, 13: sign gender fixed to the planet's own; "
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
            st.caption("Sect: Sahl, The Introduction Ch.3, 85. Domain: Abu Ma'shar VII.1, 37 and VII.6, 13 "
                       "(or Masha'allah, On Nativities 1.23, 17, per the switch).")
            st.subheader('Topical Planets in Houses', help="Each planet's Whole-Sign house placement with BOTH Rhetorius/PN4 readings for that pairing, good and bad.")
            st.caption('Rhetorius & PN4')
            st.dataframe(pd.DataFrame(planets_in_houses_data, columns=['Planet', 'Placed in (WS place)', 'Lean']),
                         hide_index=True, width='content', height=_rows_height(len(planets_in_houses_data)))
            # The readings wrap in st.table; the structural columns stay above.
            with st.expander("Rhetorius / PN4 readings for these placements"):
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
            with st.expander("Masha'allah readings for lord placements"):
                st.table(pd.DataFrame(house_lords_data,
                                      columns=['Topical House', 'Domicile Lord', 'Placed in (WS place)', "Masha'allah Signification"]),
                         hide_index=True)
            with st.expander("Planetary Dignity Evaluation (Hellenistic/Rhetorius reconstruction)", expanded=False):
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
                    "follows Abu Ma'shar's walk through the synodic cycle (VII.2), which Sahl gives "
                    "independently in *On Nativities* 1.22 and al-Biruni corroborates: burned to "
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
            _gap = []
            show_col, rule_col = st.columns([2, 1])
            with show_col:
                view = st.segmented_control(
                    "Show", ["Sahl (course text)", "Abu Ma'shar (supplement)", "Both"],
                    default=st.session_state.get("_configurations_view", "Sahl (course text)"),
                    key="configurations_view",
                    help="Each author's tables are computed under that author's OWN rule "
                         "whatever this is set to -- it selects what is shown, not how it "
                         "is judged. The Connection rule beside this control governs the few "
                         "tables that deliberately present both authors.")
                view = _persist("configurations_view", "_configurations_view", "Sahl (course text)")
            with rule_col:
                # Governs only the dual-author tables; each author's own
                # tables pin their own rule (see doctrine()). The essay
                # comparing the two rules is on the Sources page.
                _reading_radio("Connection test used in the shared tables", CONNECTION_PROFILES.keys(),
                               "connection_rule", "_connection_rule",
                               help="Which author's test decides Connected in the aspects, reception and "
                                    "prevented-connections tables. Sahl: the applying planet's own light. "
                                    "Abu Ma'shar: 15° in one sign, 12° for aspects. Full comparison on the Sources page.")
            show_sahl = view in (None, "Sahl (course text)", "Both")
            show_abu = view in ("Abu Ma'shar (supplement)", "Both")
            if show_sahl:
                _finding(_gap, "Aspects, aversions and connections",
                         f"Sahl, The Introduction Ch.2, 50-60 and Ch.3, 6-21 — {CONNECTION_PROFILE} rule in force", aspects,
                          columns=['Light Planet', 'Aspect', 'Heavy Planet', 'Applying Planet', 'Motion', 'Orientation', 'Exact Orb Dist', 'Bodies', 'Strength', 'Connected', 'Rules differ'], height=_rows_height(len(aspects)),
                          glance='Four separate facts about each pair, kept apart rather than collapsed into one verdict. LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign.',
                          notes='MOTION and EXACT ORB DIST are the degree-to-degree approach. BODIES is whether each planet falls inside the other\'s sphere of power, which is asymmetric because the spheres differ in size: Abu Ma\'shar VII.4, 7 notes that Saturn sits inside the Moon\'s body from 12 degrees while she only enters his at a little under 9. CONNECTED is the active author\'s verdict -- switch the Connection rule at the top of this page to see where they disagree; RULES DIFFER marks the pairs where the two tests disagree.\n\nSTRENGTH is two different measures. For an assembly it is the source\'s own: whose body reaches whose (VII.4, 5-8) and whether they share a bound. For an aspect it is marked "(app scale)", because VII.5, 4 grades looking as a continuum with no cutoffs anywhere -- "the strongest thing there is in its looking is the degree related most closely by number to the degree of its own sign, and if the aspect was far from these degrees, its aspect will be weaker." The thirds are this app\'s own scanning aid; the measurement itself is the Exact Orb Dist column.\n\nLIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.\n\nAPPLYING PLANET is the separate, directed fact: which one is actually closing the aspect. Normally it is the lighter, and Ch.3, 6 assumes as much ("a light, quick star GOING STRAIGHTAWAY TO a heavy star ... FEWER IN DEGREES than the heavy one"). Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma\'shar VII.5, 24 ("the connection of one of them with the other ... will be BY RETROGRADATION"), VII.5, 120 ("the light one IN MORE DEGREES goes retrograde and connects with the heavy one"), and the note on VII.5, 130 (Saturn "could never be received because he is too slow to connect with anyone, UNLESS BY RETROGRADATION"). The cause is named in this column whenever the heavier planet is the one applying, which happens for about 4% of configured pairs. Reception, transfer, collection, returning, revoking, emptiness of course and enclosure all read this column, not the light/heavy one.')
                with st.container(border=True):
                    st.markdown("**Connection group** — Ch.3, 24-30 and 119-123")
                    _finding(_gap, 'Transfer of Light', "Sahl, The Introduction Ch.3, 24-27; Type II is Abu Ma'shar, Great Introduction VII.5, 84-85", transfers,
                              glance='A faster "carrier" planet separates from one planet and connects with another, carrying the first planet\'s nature to the second -- Type I is a direct hand-off, Type II is via an intermediate planet already connecting onward.')
                    _finding(_gap, 'Collection of Light', 'Sahl, The Introduction Ch.3, 28-30', collections,
                              glance='Two planets not connected to each other both connect with a single heavier planet, which "collects" their combined power -- often read as a third party or authority resolving/mediating between two unconnected significators.')
                    _finding(_gap, 'Enclosure', 'Sahl, The Introduction Ch.3, 119-123', enclosure_data,
                              glance='A planet separating from one of the two infortunes (or, per Abu Ma\'shar\'s extension, fortunes) and connecting with the other, with neither leg intercepted by a third planet\'s rays -- graded "more powerful/unfortunate" when both legs are within 7 degrees of exact.')
                    _absent(_gap)
                with st.container(border=True):
                    st.markdown("**Handing-over group** — Ch.3, 49-76")
                    _finding(_gap, 'Handing Over', 'Sahl, The Introduction Ch.3, 70-76', handing_over_data,
                              glance='Three grades of one phenomenon, per connected pair: Management is the baseline (any connection at all); Power is added when the giving planet is itself in its own house, exaltation, or triplicity; Nature is added when the planet it connects with is the ruler')
                    _finding(_gap, f"Reception — {CONNECTION_PROFILE} rule", None, reception_data,
                              glance='Who receives whom, on what dignity, which way round, and how strongly. The two authors differ on every one of those, so the Connection rule at the top of this page governs here too.',
                              notes='SAHL (Ch.3, 49-55) runs one way only -- the connecting planet stands in a dignity of the planet it connects with, and so is received by it (52: the Moon in Aries connecting with Mars, "he receives her because Aries is his house"). House or exaltation is perfect reception; triplicity alone is expressly ranked below it (50); bound counts only paired with triplicity, which Sahl credits to Masha\'allah (54-55). Face never appears, and a connection is always required.\n\nABU MA\'SHAR (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in REVERSE where the accepting planet sits in the connector\'s dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).\n\nHe then classes reception a SECOND way, and under his rule the table shows both. DIGNITY QUALITY is 129-133, the local basis. OVERALL CLASS is 136-142: "a [2] middling reception is the planets\' reception of each other from the house, exaltation, bound, triplicity, or face" (140) -- house and exaltation included -- while "if two met [together] from this, or each one of them received its associate, it is a strong reception" (141); the natural acceptances of 134-135 are "[3] below that" (142); the Moon received by the Sun (137) and a planet received by Mercury from Virgo (139) are his named strong forms, and the Sun receiving the Moon from the opposition keeps his own word, "detestable" (137). A lone domicile reception is therefore the strongest basis AND globally middling: both are true, and they are different questions.\n\nSahl has two further forms, both under his profile only. 56, RECEPTION AT ONE REMOVE: "if the Moon was connecting with a planet and that planet was connecting with the lord of the house of the Moon or its exaltation, then the Moon is received" -- the note there calls it "like a transfer of light which indirectly allows for reception." Both legs are read in Sahl\'s directed sense of connecting (6: "going straightaway to ... going towards"), since separating is his separate term at 22.\n\n57, AFTER THE SIGN CHANGE: "if the Moon was empty in course, and then she passed over into the next sign and connected with the lord of her first sign, it is JUST LIKE RECEPTION; and if she connected with a planet OTHER than [that], IT UNDERMINES HER." Both halves appear -- the undermining is a finding, not a blank.\n\nAn empty table is NOT non-reception -- that is a separate set of hostile configurations, in the table below.')
                    _finding(_gap, 'Non-reception', 'Sahl, The Introduction Ch.3, 58-62', non_reception_data,
                              glance="Five named ways a connection is refused rather than received (Sahl, The Introduction Ch.3, 58-62), a distinct finding from simply lacking reception; the Kind column numbers them and the notes spell each one out.",
                              notes="Sahl's A -> B model: A is the connecting (applying) planet, B the planet it connects with.\n\nKind I (58): B holds no essential dignity at all at A's position -- B is alien in A's sign, so A is not recognised.\n\nKind II (59-60): A stands in B's own sign of fall, \"like one who comes to it from the house of its enemies.\"\n\nKind III (61): A is in its OWN fall and B has no house or exaltation there to rescue it -- \"as though the one asking is offering defeat.\"\n\nKind IV (62): B is in its own fall, which brings the connection down whatever A's condition.\n\nKind V (62): B sits in A's own sign of fall.")
                    _finding(_gap, 'Returning', 'Sahl, The Introduction Ch.3, 65-69', returning_data,
                              glance='Manner I: a planet connects with a retrograde planet or one under the rays -- it "returns to it what it accepted," corrupting the question.',
                              notes='Manner II: an angular (faster) planet hands over to a cadent (slower) one -- the matter has a beginning but no end.')
                    _absent(_gap)
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
                    _finding(_gap, 'Prevented connections', "Sahl, The Introduction Ch.3, 31-48; Abu Ma'shar, Great Introduction VII.5, 90-94 and 120-125", prevented,

                             glance="Ways of stopping a connection before it completes, in one table as the Handy Tables give them: Sahl's intervention, nullification and cutting, plus Abu Ma'shar's two further cuttings (VII.5, 121-124), which Sahl does not have. His revoking, resistance and escape are in his own section.")
                    _finding(_gap, 'Banished', 'Sahl, The Introduction Ch.3, 64', banishment_data,
                              glance='"The banished planet is the planet which none of the planets connects to" (64) -- a planet outside every live connection, whatever the signs are doing. Each row shows the nearest configured planet and why that is not a connection.',
                              notes='Sahl\'s definition is about CONNECTIONS (6-21), not signs: a planet can be in trine by sign with everyone and still be banished if no planet is inside a live connection with it, and it can hold an out-of-sign body connection (20-21) and not be banished at all. Abu Ma\'shar\'s later "wildness" (VII.5, 79-82) is a different, whole-sign test -- aversion to every planet -- and has its own table in his view. Dykes\' note on 64 calls Sahl\'s the earlier, less precise form; the two are kept apart rather than one served under both names.')
                    _absent(_gap)
                with st.container(border=True):
                    st.markdown("**Strength and weakness** — Ch.3, 77-112")
                    _reading_checkbox("Five-degree carryover at all twelve cusps", "five_degree_all_cusps", "_five_degree_all_cusps",
                                      help="Sahl states the rule for the stakes twice (Aphorism #44, 88; On Nativities 1.22, 9) "
                                           "and once for every house (On Nativities 1.18, 19). Off = stakes only. "
                                           "Affects: Strength of the Planets, testimony 83. Full text on the Sources page.")
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
            if show_abu:
                with st.container(border=True):
                    st.markdown("**Abu Ma'shar, Great Introduction VII.5-6**")
                    st.subheader('Planetary Condition', help="Each planet checked against Abu Ma'shar's conditions in Great Introduction VII.6, kept in his own four groups: good fortune (1-20), strength (21-29), weakness (30-46), misfortune (47-62), plus, for the Moon only, HIS OWN eleven corruptions (63-74).")
                    st.caption("Abu Ma'shar VII.6")
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
                    _finding(_gap, 'Natural connections', "Abu Ma'shar, Great Introduction VII.5, 53-77", natural_connections,
                              columns=['Pair', 'Family', 'Degrees', 'From exact', 'Motion', 'Affinity (76-77)', 'Ordinary aspect', 'Standing'],
                              glance='"Another type of connection and separation [even] without the planets\' looking at each other" (53): pairs standing in signs of equal ascensions (56) or of equal daylight (67-75), whose degrees correspond as complements within the sign -- 12 Gemini to 18 Capricorn (62). A relation of its own, not an aspect and not a dignity: the Ordinary aspect column keeps saying Aversion where that is what the signs are.',
                              notes='EQUAL ASCENSIONS (56): "Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and Sagittarius, Leo and Scorpio, and Virgo and Libra." EQUAL DAYLIGHT (67-75), the antiscia: Gemini-Cancer, Taurus-Leo, Aries-Virgo, Libra-Pisces, Sagittarius-Capricorn, exactly as he lists them -- Aquarius-Scorpio completes the standard scheme but is not enumerated here and is not added (see the coverage note on the Sources page).\n\nDEGREES: "when a planet is in the first degree of Aries, then it is in the nature of a planet which is at the last degree of Pisces" (57); "the planet which is in 12° of Gemini is in the nature of the degree of the planet which is in 18° of Capricorn: so when it passes beyond 12° of Gemini, then it has separated from it" (62). So the counterpart degree runs backwards as the planet runs forwards, and MOTION is read from both speeds together. He gives no orb: every planet in Aries is in the nature of some degree of Pisces, so every pair in a listed sign pair is shown with its distance from exact.\n\nAFFINITY: 76-77 single out four pairs of each family as bridging an ordinary aversion -- Gemini-Capricorn, Sagittarius-Cancer, Aries-Virgo, Libra-Pisces "is called a natural connection by opposition" (76); Gemini-Cancer, Virgo-Libra, Sagittarius-Capricorn, Pisces-Aries "the natural connection by sextile" (77). The notes there record that he omits Aries-Scorpio, Taurus-Libra and Aquarius-Capricorn; they are not added.\n\nThe same sign pairs are one of 134\'s four bases of acceptance, in the Reception table under his rule.')
                    _finding(_gap, 'Wildness', "Abu Ma'shar, Great Introduction VII.5, 79-82", wildness_data,
                              glance='A planet in whole-sign Aversion to all six other classical planets -- "in a sign such that absolutely no planet looks at it" (79) -- though it may still be "reached" via the lord of whatever bound it occupies (80-81).',
                              notes='Whole-sign and independent of degree. Sahl\'s "banished" (Ch.3, 64) is a different test, about live connections rather than signs, and has its own table in his view.')
                    _finding(_gap, 'Reflection of Light', "Abu Ma'shar, Great Introduction VII.5, 87-89", reflections,
                              glance="Collection or Transfer specifically between two planets that are in Aversion to each other, not just unconnected -- since Aversion pairs can't see each other at all, a third planet is the only way their natures can interact.")
                    _finding(_gap, 'Favor & Recompense', "Abu Ma'shar VII.5, 126-128", favor_recompense_data,
                              glance='A planet in its own Fall or a welled/pitted degree, pulled out of that weak condition by a connecting dispositor (Favor). Recompense is the same planet later returning the favor, found by simulating the chart forward.')
                    _finding(_gap, 'Forward-Looking Conditions', 'Revoking, Resistance, Escape — next 200 days', forward_looking_data,
                              glance='Conditions describing what happens as the chart moves forward in time (up to ~200 days), not the birth moment alone.',
                              notes='Each chapter prescribes an ORDERED SEQUENCE of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when. A condition not found inside 200 days is reported as not found, never as a negative finding.\n\nREVOKING (117): "a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it." The window is now birth to the applicant\'s first station: perfection inside it means nothing was revoked.\n\nRESISTANCE (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one BY RETROGRADATION, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead. All five steps are required and timed.\n\nESCAPE (119): the planet being applied to leaves its sign first; the applicant then follows across the SAME boundary on its own next crossing, and is captured by a body it meets in the new sign. Dykes\' note on Fig. 139 is the picture: Mercury slips from Virgo into Libra, Venus follows, and Saturn\'s body catches her there.')

                    _absent(_gap)
            _absent(_gap)
        def page_lots():
            st.header("Lots")
            st.caption("Lesson 18.")
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
                                "8.6, 1; 9.1, 9): the Ascendant's degree carried into that sign, or the Alchabitius cusp. "
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
                st.markdown('The STANDING column records his editorial position in his own words where he states one.\n\nFour kinds of case. SAHL HIMSELF RULES: of the two sibling Lots, "both of the Lots are correct, so work with them both together" (3.11, 4) -- neither is subordinate. DYKES NAMES HIS CHOICE: of the three witnesses to the Lot of enemies, "I have used M here"; on the night reversal of the Saturn-Moon work Lot, "Paul instructs us to reverse it by night, but Abu Ma\'shar says not to. We should follow Paul." DYKES MARKS ONE STANDARD: on children, "the usual calculation ... is that of Hermes." DYKES ONLY TABULATES: three Lots for work, after noting that "Sahl quietly switches to Masha\'allah\'s treatise on Lots ... without telling us that the formula is different."\n\nEvery formula is taken from the running prose or a footnote, never from one of the summary tables, whose glyph columns the OCR mangles -- Fig. 63\'s row for Ch. 10.2.5 renders as Mercury-Venus where the body text plainly reads "from Saturn to the Moon."\n\nNote the Lot of death is projected FROM SATURN, not from the Ascendant.')
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
            st.caption("Part 2: prediction.")
            st.subheader('Chronocrator Matrix (Active Time Lords)', help='Two rows: the lord of the year by annual profection, and the Egyptian bound lord of the Ascendant directed symbolically at one degree per year -- which is not a distribution, as its label says.')
            st.dataframe(pd.DataFrame(time_lords_data), hide_index=True, width='stretch')

        def page_sources():
            st.header("Sources and coverage")
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
                "**Abu Ma'shar** (Great Introduction VII.4-5): two flat distances instead -- assembly "
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
                "**Five-degree carryover at all twelve cusps** (Configurations page, Strength of the Planets) -- "
                "Sahl states the rule for the stakes twice (Aphorism #44, 88; On Nativities 1.22, 9) "
                "and once for every house (On Nativities 1.18, 19: 'and likewise in all of the houses'). "
                "Off = stakes only. Flips the Sahl 83 verdict for about 6% of placements. "
                "Affects: Strength of the Planets, testimony 83.\n\n"
                "**VII.6, 27/45 'eastern/western relative to the Sun'** (Configurations page, Planetary Condition) -- "
                "'hemisphere': the whole half, excluding the rays (VII.2, 2; VII.6, 34). 'VII.2 band': only "
                "the easternizing band 15/18 to 90 degrees (VII.2, 14-21) and the westernizing band 90 down to "
                "15 degrees (VII.2, 29-31). Superiors: 52% vs 25% of placements. "
                "Affects: Planetary Condition (27, 45).\n\n"
                "**Moon under the rays to 15 degrees (Sahl, On Nativities 1.19, 6)** (Chart page, Planetary Positions) -- "
                "Abu Ma'shar VII.2, 61 and 72-73 give 12; Sahl gives 15 for the Moon's fitness as releaser. "
                "Affects: the Solar phase column of Planetary Positions; on the Configurations page, "
                "Weakness of the Planets (93), Planetary Condition and Corruption of the Moon.\n\n"
                "**Domain (hayz)** (Dignities page, Sect table) -- "
                "Abu Ma'shar VII.1, 37 / VII.6, 13: sign gender fixed to the planet's own. Masha'allah, "
                "On Nativities 1.23, 17: a male planet by day above the earth in a male sign, by night under "
                "the earth in a FEMALE sign; feminine planets by hemisphere only. "
                "Affects: the Sect table and Dignity Evaluation on the Dignities page, and Planetary Condition (13) "
                "on the Configurations page.\n\n"
                "**House-based Lots measure to the** (Lots page, Topical Lots) -- "
                "'The second place', 'the degree of the eighth place', 'the ninth' (On Nativities 2.15, 1; "
                "8.6, 1; 9.1, 9). Whole-sign: the Ascendant's degree carried into that sign. Quadrant: the "
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

        pages = [st.Page(page_chart, url_path="chart", title="Chart", icon=":material/explore:", default=True)]
        if gate >= 9:
            pages.append(st.Page(page_dignities, url_path="dignities", title="Dignities and places", icon=":material/shield:"))
        if gate >= 14:
            pages.append(st.Page(page_configurations, url_path="configurations", title="Configurations", icon=":material/hub:"))
        if gate >= 18:
            pages.append(st.Page(page_lots, url_path="lots", title="Lots", icon=":material/functions:"))
        if gate >= 19:
            pages.append(st.Page(page_victors, url_path="victors", title="Lunation and victors", icon=":material/trophy:"))
        if gate >= 99:
            pages.append(st.Page(page_timing, url_path="timing", title="Timing", icon=":material/schedule:"))
        pages.append(st.Page(page_sources, url_path="sources", title="Sources and coverage", icon=":material/menu_book:"))
        st.navigation(pages, position="sidebar").run()

    else:
        st.sidebar.error("Timezone boundary not found for coordinates.")
