import swisseph as swe
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, time, timedelta
from itertools import combinations
from xml.sax.saxutils import escape
from timezonefinder import TimezoneFinder
import pytz
from pathlib import Path
import math
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

def load_saved_charts():
    if not SAVED_CHARTS_PATH.exists() and _LEGACY_SAVED_CHARTS_PATH.exists():
        try:
            SAVED_CHARTS_PATH.write_text(_LEGACY_SAVED_CHARTS_PATH.read_text())
        except OSError:
            pass
    if SAVED_CHARTS_PATH.exists():
        try:
            return json.loads(SAVED_CHARTS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def write_saved_charts(charts):
    try:
        SAVED_CHARTS_PATH.write_text(json.dumps(charts, indent=2))
        return True
    except OSError:
        return False

# ==========================================
# 1. CORE CALCULATION ENGINE
# ==========================================

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

    targets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN, 'North Node': swe.MEAN_NODE
    }
    
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
    moon_long = planetary_data['Moon']['longitude']
    
    is_diurnal = (sun_long - ascendant) % 360 > 180.0
    sect = 'Diurnal' if is_diurnal else 'Nocturnal'
    
    lot_of_fortune = (ascendant + moon_long - sun_long) % 360 if is_diurnal else (ascendant + sun_long - moon_long) % 360

    return {
        'julian_day': jd,
        'planetary_data': planetary_data,
        'houses': cusps,
        'ascendant': ascendant,
        'descendant': descendant,
        'mc': mc,
        'ic': ic,
        'sect': sect,
        'lot_of_fortune': lot_of_fortune
    }

# ==========================================
# 2. HELPER FUNCTIONS & VARIATION-SELECTOR-FREE RENDERER
# ==========================================

def get_zodiac_sign(longitude):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    return signs[int(longitude // 30)]

def get_glyph_degree_string(longitude):
    # \uFE0E (VS15) forces TEXT presentation on every glyph. Without it on all
    # twelve, most fonts/browsers fall back to colored emoji-style rendering
    # for the ones that lack the selector.
    signs_text = ['\u2648\uFE0E', '\u2649\uFE0E', '\u264A\uFE0E', '\u264B\uFE0E', '\u264C\uFE0E', '\u264D\uFE0E',
                  '\u264E\uFE0E', '\u264F\uFE0E', '\u2650\uFE0E', '\u2651\uFE0E', '\u2652\uFE0E', '\u2653\uFE0E']
    sign_idx = int(longitude // 30)
    deg = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    return f"{deg:02d}° {signs_text[sign_idx]} {minute:02d}'"

def get_degree_string(longitude):
    sign = get_zodiac_sign(longitude)
    deg = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    return f"{deg:02d}° {sign[:3]} {minute:02d}'"

def generate_hybrid_svg(chart_data, location_query, lat, lon, dt_local, tz_name):
    size = 900
    cx, cy = 450, 450
    r_outer = 410
    r_zodiac = 345
    r_houses = 210
    r_inner = 110
    
    asc = chart_data['ascendant']
    asc_sign_start = math.floor(asc / 30) * 30
    
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="100%" height="100%" style="background-color: #ffffff; color: #000000; font-family: \'Noto Sans Symbols\', \'Segoe UI Symbol\', \'DejaVu Sans\', sans-serif;">']
    
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#000000" stroke-width="3"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="none" stroke="#000000" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_houses}" fill="none" stroke="#000000" stroke-width="1.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>')

    def lon_to_angle(longitude):
        return (longitude - asc_sign_start + 180) % 360

    def polar_to_cartesian(r, angle_deg):
        rad = math.radians(angle_deg)
        return cx + r * math.cos(rad), cy - r * math.sin(rad)

    signs_text = ['\u2648\uFE0E', '\u2649\uFE0E', '\u264A\uFE0E', '\u264B\uFE0E', '\u264C\uFE0E', '\u264D\uFE0E',
                  '\u264E\uFE0E', '\u264F\uFE0E', '\u2650\uFE0E', '\u2651\uFE0E', '\u2652\uFE0E', '\u2653\uFE0E']

    # 1. Whole Sign Boundary Sectors with explicit text symbols
    for i in range(12):
        sign_start_lon = (asc_sign_start + i * 30) % 360
        angle_start = lon_to_angle(sign_start_lon)
        
        x1, y1 = polar_to_cartesian(r_houses, angle_start)
        x2, y2 = polar_to_cartesian(r_outer, angle_start)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="1.5"/>')

        mid_lon = sign_start_lon + 15
        mid_angle = lon_to_angle(mid_lon)
        
        lx, ly = polar_to_cartesian((r_outer + r_zodiac) / 2, mid_angle)
        sign_idx = int((sign_start_lon // 30))
        svg.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="central" font-size="16" font-weight="bold" fill="#000000">{signs_text[sign_idx]}</text>')

        hx_lab, hy_lab = polar_to_cartesian((r_houses + r_inner + 30) / 2, mid_angle)
        svg.append(f'<text x="{hx_lab}" y="{hy_lab}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="bold" fill="#000000">{i+1}</text>')

        for d in range(5, 30, 5):
            tick_lon = sign_start_lon + d
            t_angle = lon_to_angle(tick_lon)
            t1_x, t1_y = polar_to_cartesian(r_zodiac, t_angle)
            t2_x, t2_y = polar_to_cartesian(r_zodiac + 6, t_angle)
            svg.append(f'<line x1="{t1_x}" y1="{t1_y}" x2="{t2_x}" y2="{t2_y}" stroke="#000000" stroke-width="0.75"/>')

    # 2. Quadrant House Cusp Lines (Alchabitius)
    cusps = chart_data['houses']
    for i, cusp_lon in enumerate(cusps):
        c_angle = lon_to_angle(cusp_lon)
        hx, hy = polar_to_cartesian(r_inner, c_angle)
        hx_out, hy_out = polar_to_cartesian(r_houses, c_angle)
        svg.append(f'<line x1="{hx}" y1="{hy}" x2="{hx_out}" y2="{hy_out}" stroke="#a94442" stroke-width="1.5" stroke-dasharray="4"/>')
        
        px_t1, py_t1 = polar_to_cartesian(r_houses, c_angle)
        px_t2, py_t2 = polar_to_cartesian(r_houses - 6, c_angle)
        svg.append(f'<line x1="{px_t1}" y1="{py_t1}" x2="{px_t2}" y2="{py_t2}" stroke="#a94442" stroke-width="2"/>')

    glyph_map = {
        'Sun': '\u2609\uFE0E', 'Moon': '\u263D\uFE0E', 'Mercury': '\u263F\uFE0E', 'Venus': '\u2640\uFE0E',
        'Mars': '\u2642\uFE0E', 'Jupiter': '\u2643\uFE0E', 'Saturn': '\u2644\uFE0E', 'North Node': '\u260A\uFE0E',
        'Ascendant': 'Asc', 'Midheaven': 'MC', 'Descendant': 'Des', 'IC': 'IC',
        'Lot of Fortune': '\u2297\uFE0E'
    }

    p_data = chart_data['planetary_data']
    all_points = list({
        **p_data,
        'Ascendant': {'longitude': chart_data['ascendant'], 'speed_in_lon': 1.0},
        'Midheaven': {'longitude': chart_data['mc'], 'speed_in_lon': 1.0},
        'Descendant': {'longitude': chart_data['descendant'], 'speed_in_lon': 1.0},
        'IC': {'longitude': chart_data['ic'], 'speed_in_lon': 1.0},
        'Lot of Fortune': {'longitude': chart_data['lot_of_fortune'], 'speed_in_lon': 1.0}
    }.items())

    all_points.sort(key=lambda x: x[1]['longitude'])

    ANGLE_NAMES = {'Ascendant', 'Midheaven', 'Descendant', 'IC'}
    angle_colors = {'Ascendant': '#0000ff', 'Descendant': '#0000ff', 'Midheaven': '#228b22', 'IC': '#228b22'}

    # --- Anti-collision label layout --------------------------------------
    # Points within CLUSTER_GAP degrees of each other are grouped into a
    # cluster. Earlier this stacked members purely along the RADIUS — but
    # that barely separates labels near the Ascendant/Descendant side of
    # the wheel, where the ring runs almost horizontal on screen, so a 25px
    # radius change is nearly all sideways and almost no vertical (the
    # symptom: Asc's label piling directly on top of Lot of Fortune's).
    # Instead, each cluster's anchor member is placed at LAYER_TOP along
    # its true radial direction, and every subsequent member is stacked a
    # fixed number of *screen* pixels below the anchor — guaranteeing real
    # vertical separation no matter where on the ring the cluster sits.
    # Angles (Asc/MC/Des/IC) take priority for the anchor slot when they
    # share a cluster with a planet/node/Lot of Fortune, since they're
    # conventionally labeled right at the ring regardless of what else is
    # nearby.
    CLUSTER_GAP = 6.0
    LAYER_TOP = r_zodiac - 40
    STACK_DY = 30

    clusters = []
    for planet, data in all_points:
        lon_val = data['longitude']
        if clusters and (lon_val - clusters[-1][-1][1]['longitude']) < CLUSTER_GAP:
            clusters[-1].append((planet, data))
        else:
            clusters.append([(planet, data)])
    # Longitude wraps at 360°; merge the first/last cluster if they abut
    if len(clusters) > 1:
        first_lon = clusters[0][0][1]['longitude']
        last_lon = clusters[-1][-1][1]['longitude']
        if (first_lon + 360 - last_lon) < CLUSTER_GAP:
            clusters[0] = clusters[-1] + clusters[0]
            clusters.pop()

    label_pos = {}
    for cluster in clusters:
        cluster_sorted = sorted(cluster, key=lambda pd: 0 if pd[0] in ANGLE_NAMES else 1)
        anchor_angle = lon_to_angle(cluster_sorted[0][1]['longitude'])
        anchor_px, anchor_py = polar_to_cartesian(LAYER_TOP, anchor_angle)
        for i, (planet, data) in enumerate(cluster_sorted):
            label_pos[planet] = (anchor_px, anchor_py + i * STACK_DY)

    # Axis Highlights — stop just short of each label instead of running
    # the full way to the ring and straight through the text sitting on it.
    for pt_key, pt_lon, pt_color in [
        ('Ascendant', chart_data['ascendant'], angle_colors['Ascendant']),
        ('Midheaven', chart_data['mc'], angle_colors['Midheaven']),
        ('Descendant', chart_data['descendant'], angle_colors['Descendant']),
        ('IC', chart_data['ic'], angle_colors['IC']),
    ]:
        pt_angle = lon_to_angle(pt_lon)
        label_px, label_py = label_pos[pt_key]
        label_r = math.hypot(label_px - cx, label_py - cy)
        line_end_r = min(label_r + 20, r_zodiac)
        px1, py1 = polar_to_cartesian(r_inner, pt_angle)
        px2, py2 = polar_to_cartesian(line_end_r, pt_angle)
        svg.append(f'<line x1="{px1}" y1="{py1}" x2="{px2}" y2="{py2}" stroke="{pt_color}" stroke-width="2" stroke-dasharray="2"/>')

    for planet, data in all_points:
        lon_val = data['longitude']
        speed = data.get('speed_in_lon', 1.0)
        is_rx = speed < 0 and planet not in ({'Sun', 'Moon', 'North Node'} | ANGLE_NAMES)

        p_angle = lon_to_angle(lon_val)
        px, py = label_pos[planet]
        tz_x, tz_y = polar_to_cartesian(r_zodiac, p_angle)

        # Small dot marks the point's true position on the zodiac ring.
        # The leader line stops ~18px short of the label instead of
        # running all the way to it, so the line never cuts through text.
        svg.append(f'<circle cx="{tz_x}" cy="{tz_y}" r="3" fill="#000000"/>')
        dxv, dyv = px - tz_x, py - tz_y
        dist = math.hypot(dxv, dyv)
        if dist > 20:
            t = (dist - 18) / dist
            lx_end, ly_end = tz_x + dxv * t, tz_y + dyv * t
            svg.append(f'<line x1="{tz_x}" y1="{tz_y}" x2="{lx_end}" y2="{ly_end}" stroke="#999999" stroke-width="0.75" stroke-dasharray="2"/>')

        sign_idx = int(lon_val // 30) % 12
        deg = int(lon_val % 30)
        minute = int((lon_val % 1) * 60)
        rx_tag = " Rx" if is_rx else ""
        symbol = glyph_map.get(planet, planet[:3])

        if planet in ANGLE_NAMES:
            # Angle labels (Asc/MC/Des/IC) are short text abbreviations, not
            # single glyphs, so they get a modest size that matches the
            # planet glyphs visually instead of towering over them. They're
            # also nudged to the side of their own axis spoke (left-aligned,
            # offset right) rather than centered directly on top of it.
            label_color = angle_colors.get(planet, '#000000')
            svg.append(
                f'<text x="{px+10}" y="{py-6}" text-anchor="start" fill="{label_color}">'
                f'<tspan font-size="14" font-weight="bold">{symbol}</tspan></text>'
                f'<text x="{px+10}" y="{py+9}" text-anchor="start" fill="{label_color}">'
                f'<tspan font-size="11" font-weight="bold">{deg:02d}\u00b0 {signs_text[sign_idx]} {minute:02d}\'</tspan></text>'
            )
        else:
            # Two-line stacked label (glyph+degree over sign+minutes) is far
            # more compact than one long horizontal string, so clustered
            # points stay readable.
            svg.append(
                f'<text x="{px}" y="{py-6}" text-anchor="middle" fill="#000000">'
                f'<tspan font-size="19" font-weight="bold">{symbol}</tspan>'
                f'<tspan font-size="12" font-weight="bold" dx="3">{deg:02d}\u00b0</tspan></text>'
                f'<text x="{px}" y="{py+9}" text-anchor="middle" fill="#000000">'
                f'<tspan font-size="12" font-weight="bold">{signs_text[sign_idx]} {minute:02d}\'{rx_tag}</tspan></text>'
            )

    # Central Metadata Hub
    svg.append(f'<text x="{cx}" y="{cy - 55}" text-anchor="middle" font-size="13" font-weight="bold" fill="#000000">Whole-Sign Hybrid Chart</text>')
    # User-supplied text goes through XML escaping before it reaches the
    # markup. A place name containing & or < would otherwise produce
    # malformed XML and silently break the whole wheel, and the string is
    # free-form: it comes from the City Search box or a saved chart's
    # stored label.
    svg.append(f'<text x="{cx}" y="{cy - 35}" text-anchor="middle" font-size="11" fill="#000000">{escape(str(location_query))}</text>')
    svg.append(f'<text x="{cx}" y="{cy - 20}" text-anchor="middle" font-size="10" fill="#000000">Lat: {lat:.4f}° | Lon: {lon:.4f}°</text>')
    svg.append(f'<text x="{cx}" y="{cy - 5}" text-anchor="middle" font-size="10" fill="#000000">{dt_local.strftime("%Y-%m-%d %H:%M")} [{escape(str(tz_name))}]</text>')
    svg.append(f'<text x="{cx}" y="{cy + 15}" text-anchor="middle" font-size="10" font-weight="bold" fill="#000000">Sect: {chart_data["sect"]}</text>')
    svg.append(f'<text x="{cx}" y="{cy + 30}" text-anchor="middle" font-size="10" fill="#000000">Layout: Whole Sign + Alchabitius Cusps</text>')
    svg.append(f'<text x="{cx}" y="{cy + 45}" text-anchor="middle" font-size="10" fill="#000000">Zodiac: Tropical</text>')
    
    svg.append('</svg>')
    return "".join(svg)

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
    8: {1: "A wicked soul, much distress, faint-hearted", 2: "Livelihood from inheritance/dead; generous; assets taken if connecting to 8th", 3: "Brother's women will not survive or get inheritance", 4: "Diminishes father's lifespan; fear for native, mother dies in childbirth", 5: "Children premature or miscarried", 6: "Native healthy if lord of Ascendant does not look", 7: "Consumes inheritance of women; marries foreign woman", 8: "Native is healthy, illness insignificant, death will be light", 9: "Suffers robbery on journeys, eager in accumulating assets", 10: "Authority in youth, a follower who seeks leadership/boasts", 11: "Not well known/descended; does low work like commerce", 12: "Few enemies; many of native's slaves will die"},
    9: {1: "Remains in foreign land; travel; speaks knowledge; sensible if unharmed", 2: "Livelihood from travel, piety, religion", 3: "Siblings marry foreign women, live abroad", 4: "Unknown fathers who leave, with defects/bad death; bad faith", 5: "Has children abroad; they make native happy", 6: "Excellent intentions; illness while traveling, encounters hardship", 7: "Marries foreign woman given by her brother; native loves her", 8: "Bad thoughts and work; die in exile", 9: "Few journeys; upright in religion of fathers, good intention", 10: "Authority/leadership traveling abroad; offered the good", 11: "Good fortune abroad; happy until end of life", 12: "Siblings/native have hardship from enemies traveling; bad religion"},
    10: {1: "Interacting with Sultan, known by him, living due to Sultan", 2: "Livelihood from the Sultan", 3: "Death of siblings, jealousy and grudges", 4: "Fathers well known to Sultan", 5: "Defects and illnesses in children", 6: "Encounters hardship from the Sultan", 7: "Marriage to someone related to Sultan, fortunate woman, good from her", 8: "Native's ruin will be due to Sultan", 9: "Siblings marry better women or from Sultan's family; native is pious", 10: "Proficient in work, having influence, livelihood from work", 11: "Authority in friendship, Sultan will not be hostile", 12: "Hostility from Sultan and native's superiors; unhappy"},
    11: {1: "Good character, many friends, but harsh toward children/few children", 2: "Livelihood relates to friends/commerce; friends need native if Asc lord looks", 3: "Pious siblings known for that; reflects well on native", 4: "Short lifespan for father; bad condition unless received by fortune", 5: "Pleased by children and family; praise for him", 6: "Friends are not well known", 7: "Marries fertile woman, will love her, live in luxury because of her", 8: "Friends diminished; corrupts friendship; dies when condition is good", 9: "Pious friends, shared religious love; siblings marry foreign women", 10: "Friends benefit from native; child inherits assets from Sultan", 11: "Lives comfortable life, imputed with goodness, many friends, culture", 12: "Leaves goodness of friends; friends become enemies, unhappy"},
    12: {1: "Miserable, bad livelihood, enemies victorious; worse if bad connection", 2: "Life/livelihood from prisons, enemies; distressed and poor in soul", 3: "Hostile siblings; they get his authority and are superior", 4: "Parents are foreigners in exile; aspects show if good/bad for them", 5: "Children have defect/illness, will die; no children if unfortunate", 6: "Hostile to lower-status people; native sickly or ongoing health problems", 7: "Spouse has little esteem; hardship/hostility; secret relationships/cheating", 8: "Killing by enemies feared, or foolish people oppose him", 9: "Wicked intentions; corrupts religion, thinks he is right", 10: "Dispossessed by authorities; griefs; works with large animals/secrets", 11: "Little good, miserable life; few friends, many enemies", 12: "Few enemies, may not manifest; safe from them"}
}

# Delineations for a planet occupying a given Whole Sign House, keyed by
# [wsh_house][planet]['Good'|'Bad'] (Good/Bad selected by the planet's own
# net dignity score), synthesizing Rhetorius and PN4.
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

        score = (is_domicile * 5 + is_exalted * 4 + is_triplicity * 3 + is_term * 2 + is_face * 1
                 - is_detriment * 5 - is_fall * 4 - is_peregrine * 5)

        labels = []
        if is_domicile: labels.append("Dom (+5)")
        if is_exalted: labels.append("Exalt (+4)")
        if is_triplicity: labels.append("Trip (+3)")
        if is_term: labels.append("Term (+2)")
        if is_face: labels.append("Face (+1)")
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
DIURNAL_SECT_PLANETS = {'Sun', 'Jupiter', 'Saturn'}
NOCTURNAL_SECT_PLANETS = {'Moon', 'Venus', 'Mars'}
MASCULINE_SIGNS = {'Aries', 'Gemini', 'Leo', 'Libra', 'Sagittarius', 'Aquarius'}
FEMININE_SIGNS = {'Taurus', 'Cancer', 'Virgo', 'Scorpio', 'Capricorn', 'Pisces'}
# Mean daily motions (deg/day), used only to gauge "swift" vs. an average pace
AVERAGE_DAILY_MOTION = {'Sun': 0.9856, 'Moon': 13.1764, 'Mercury': 1.383, 'Venus': 1.2, 'Mars': 0.524, 'Jupiter': 0.083, 'Saturn': 0.034}
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
#                    15 deg west (VII.2, 37-53; On Nativities 1.22, 7-8)
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
# The seven-day setting allowance (VII.2, 30-31; On Nativities 1.22, 2-4).
SOLAR_SETTING_DEGREES = {'Saturn': 22.0, 'Jupiter': 22.0, 'Mars': 22.0}
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
    rays = SOLAR_RAYS_ORB.get(planet, (15.0, 15.0))[idx]
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
        # Mars's exception is handled by classing him with the nocturnal
        # planets, which is what "contrary to what we said" amounts to: he
        # is a masculine planet who takes the feminine side of both tests.
        is_hayz = contrary_domain = False
        if planet_is_diurnal is not None:
            if planet_is_diurnal:
                horizon_ok = is_above_horizon if is_diurnal_chart else not is_above_horizon
                gender_ok = current_sign in MASCULINE_SIGNS
            else:
                horizon_ok = not is_above_horizon if is_diurnal_chart else is_above_horizon
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
        is_stationary = abs(speed) <= 0.003
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
            row['sahl_body_connection'] = True
            row['body_connection_from'] = earlier
            row['body_connection_to'] = later

    return rows

# --- Connection profiles --------------------------------------------------
# Sahl and Abu Ma'shar agree that looking is sign-to-sign and connecting is
# degree-to-degree (Sahl Ch.3, 23), but they part company at the sign
# boundary and on what activates a connection. Rather than blend them into
# one Boolean, each author's rule is written out separately and one is made
# active; every downstream doctrine reads _is_connected(), which dispatches.
CONNECTION_PROFILE = 'Sahl'

def _is_connected_sahl(row):
    """Sahl, The Introduction Ch.3, 6-21. The applying planet's OWN light
    (19: "it already struck with its own light upon its degree") governs,
    so the test is asymmetric by design -- the orb belongs to the planet
    casting, not to the pair.

    Separation windows: same-sign, until the light one has departed by
    "one-half of its body -- and that is its light" (10-11); cross-sign, a
    full degree (9). PLANETARY_ORBS already stores those half-body radii.

    Also admits the out-of-sign connection by body of 20-21, precomputed
    onto the row by _pairwise_configurations()."""
    if row['aspect_name'] == 'Aversion':
        return row.get('sahl_body_connection', False)
    light = PLANETARY_ORBS.get(row['light_name'], 7.0)
    remaining = abs(row['deviation'])
    if row['motion'] == 'Applying':
        return remaining <= light
    if row['signs_apart'] == 0:
        return remaining <= light
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
    if row['assembly']:
        return row['dist'] <= 15.0
    return abs(row['deviation']) <= 12.0

CONNECTION_PROFILES = {'Sahl': _is_connected_sahl, "Abu Ma'shar": _is_connected_abu_mashar}

def _is_connected(row):
    """Whether the pair is Connected under the active author profile."""
    return CONNECTION_PROFILES[CONNECTION_PROFILE](row)

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

def _mixing_natures(row):
    """Abu Ma'shar's weak cross-sign case (VII.4, 13-14; VII.5, 14): the
    two bodies' spheres of power merge across a sign boundary, which is an
    indication but explicitly not a connection or an assembly."""
    return (not row['assembly']) and row['mutual_body']

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
            aspects.append({
                'Light Planet': light_name,
                'Aspect': 'Aversion',
                'Heavy Planet': heavy_name,
                'Motion': '\u2013',
                'Orientation': '\u2013',
                'Exact Orb Dist': '\u2013',
                'Bodies': _body_overlap_label(row),
                'Strength': note,
                'Connected': 'Yes' if _is_connected(row) else 'No',
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
            # Looking-strength (VII.5, 2-7, Fig. 111): "the strongest thing
            # is looking at the degree most closely related by number to
            # the degree of its own sign... if the aspect was far from
            # these degrees, its aspect will be weaker" -- graded, not
            # gated, using the pair's own orbs as the proximity scale
            # (no numeric cutoff is given in the source beyond this).
            combined_orb = PLANETARY_ORBS.get(row['p1'], 7.0) + PLANETARY_ORBS.get(row['p2'], 7.0)
            remaining = abs(row['deviation'])
            if remaining <= combined_orb / 3.0:
                strength = 'Strong'
            elif remaining <= combined_orb:
                strength = 'Moderate'
            else:
                strength = 'Weak'

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
        })

    return aspects

# --- Transfer & Collection of light -- Sahl, The Introduction Ch.3, 24-30 ----

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
    rows = _pairwise_configurations(planetary_data)
    # The carrier is the planet that MOVES between the other two -- "the
    # light planet separates from the heavy planet, and is connecting with
    # another" (Ch.3, 24). Keyed on the directed applicant rather than on
    # natural rank, so that a planet carrying light by retrogradation is
    # recognised as the carrier rather than as the thing carried.
    by_fast = {}
    for row in rows:
        if row['aspect_name'] == 'Aversion':
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
    rows = _pairwise_configurations(planetary_data)
    connected_lookup = {}
    applying_to = {}
    for row in rows:
        pair = frozenset({row['p1'], row['p2']})
        is_conn = row['aspect_name'] != 'Aversion' and _is_connected(row)
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

def evaluate_wildness(planetary_data):
    """Wildness. Sahl's own term for this is "banished" (مطرود, The
    Introduction Ch.3, 64): "the planet which none of the planets connects
    to." His wording doesn't explicitly frame this as whole-sign Aversion
    to everyone -- that sharper, "aversion to all other planets" definition
    is a later refinement (Dykes' footnote there, citing his own ITA
    III.10, calls Sahl's "banished" an early, less precise form of it) that
    Abu Ma'shar's Great Introduction VII.5, 79-82, Fig. 125 reflects, and
    which this function implements. Per VII.5, 80-81, a wild planet still
    counts as connected with the lord of whatever bound it currently
    occupies, noted here rather than negating the flag."""
    rows = _pairwise_configurations(planetary_data)
    planets = [p for p in planetary_data.keys() if p != 'North Node']
    aversion_count = {p: 0 for p in planets}
    for row in rows:
        if row['aspect_name'] == 'Aversion':
            aversion_count[row['p1']] += 1
            aversion_count[row['p2']] += 1
    results = []
    for p in planets:
        if aversion_count[p] == len(planets) - 1:
            lon = planetary_data[p]['longitude']
            results.append({'Planet': p, 'Bound Lord (residual connection)': get_essential_rulers(lon)['term']})
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
            reached_houses = sorted({
                get_wsh_house(planetary_data[r['p2'] if r['p1'] == collector else r['p1']]['longitude'], ascendant_lon)
                for r in rows
                if r['aspect_name'] != 'Aversion' and collector in (r['p1'], r['p2'])
                and (r['p2'] if r['p1'] == collector else r['p1']) not in collected
            })
            detail = f"{collector} collects {c['Collects']}"
            if reached_houses:
                detail += f", reflects toward house(s) {reached_houses}"
            reflections.append({'Reflection Type': 'I (Collection)', 'Detail': detail})
    return reflections

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
        r = row_for.get(frozenset({a, b}))
        return r is not None and r['aspect_name'] != 'Aversion' and r['motion'] == 'Applying'

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
            # on its way to the heavy one.
            if not applying(blocked, target):
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
        looking, heavy = row['light_name'], row['heavy_name']
        remaining_ray = abs(row['deviation'])
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
                            'Blocked By': uniting, 'From Reaching': heavy})
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
    rows = _pairwise_configurations(planetary_data)
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    results = []

    for r in rows:
        if r['aspect_name'] == 'Aversion' or not _is_connected(r):
            continue
        fast, slow = r['light_name'], r['heavy_name']
        fast_lon = planetary_data[fast]['longitude']
        fast_rulers = get_essential_rulers(fast_lon)
        fast_power_claims = {fast_rulers['domicile'], fast_rulers['exaltation'], fast_rulers[triplicity_key]} - {'-'}
        fast_own_dispositors = {fast_rulers['domicile'], fast_rulers['exaltation']} - {'-'}

        results.append({'Type': 'Management', 'Planet': fast, 'Hands Over To': slow})

        if fast in fast_power_claims:
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

def _simulate_forward(planetary_data, jd, horizon_days=200, step_days=1.0):
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
    rows = _pairwise_configurations(planetary_data)
    results = []
    for r in rows:
        if r['aspect_name'] == 'Aversion' or not _is_connected(r) or r['motion'] != 'Applying':
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
        if fast_house in ANGLE_HOUSES and slow_house in CADENT_HOUSES:
            results.append({'Manner': 'II (66-69)', 'Planet': fast, 'Returned By': slow})

    return results

def evaluate_revoking(planetary_data, sim):
    """Revoking (VII.5, 117, Fig. 137; the same sentence in Sahl Ch.3,
    117): "a planet is CONNECTING with a planet, but BEFORE IT REACHES IT,
    it retrogrades away from it, and its connection is nullified."

    "Before it reaches it" fixes the window: the only question is whether
    the aspect perfects between now and the applicant's first station. If
    it does, nothing was revoked; if it does not, the station is what
    stopped it. Searching the whole horizon instead, and accepting "no
    perfection found anywhere" as a positive, let a station on day 190
    revoke a connection that was never going to complete inside 200 days
    regardless -- a finding with no causal content."""
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

    Type III is ordered by Sahl's own PRECEDENCE (44 and its note, see
    _contact_rank()), not by nearness alone. Nearness only breaks ties
    within a rank. Sahl works the case out himself at 46-48, Figure 15:
    "the Moon is in 10 degrees of Taurus, and Mars in 20 degrees of Taurus,
    and the Moon is connecting with Venus (and Venus is in 15 degrees of
    Cancer). So her connection with Venus is PRIOR to her uniting with
    Mars, BUT the Moon is uniting [with Mars], and that is stronger than an
    aspect and a connection." The Venus sextile is 5 degrees from exact and
    the Mars union 10, so sorting by nearness alone produced the opposite
    of Sahl's stated verdict -- it had the Moon cut off from Mars.

    Note this is the SAME passage that was once misapplied in this project
    to third-party blocking. 42-43 (Fig. 14) is the third-party case, where
    Mars unites with Saturn and cuts the Moon's aspect to him; 45-48
    (Fig. 15) is the one-planet case handled here, where a single planet
    holds both a union and a connection and the union wins. They are
    consecutive and easy to conflate."""
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
            if _contact_rank(r) == 2 and win_rank != 0:
                # 44 gives only the uniting as cutting a bare aspect.
                continue
            results.append({
                'Type': 'III',
                'Planet': fast,
                'Cut Off From': r['receiver'] or r['heavy_name'],
                'Connects With Instead': winner['receiver'] or winner['heavy_name'],
                'Because': f'{_CONTACT_NAMES[win_rank]} outranks {_CONTACT_NAMES[_contact_rank(r)]}'
                            if win_rank != _contact_rank(r)
                            else f'nearer by {abs(r["deviation"]) - abs(winner["deviation"]):.1f} deg',
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
                    'Type': 'I', 'Planet': light, 'Cut Off From': heavy, 'Cut By': candidate,
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
                    'Type': 'II', 'Planet': light, 'Cut Off From': heavy, 'Cut By': onward,
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

def evaluate_reception(planetary_data, sect):
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

    Returns one row per reception found, naming the receiver, the planet
    received, which way round it runs, the dignities it rests on, its grade
    and whether it holds by connection or only by looking -- so the
    evidence is inspectable rather than reduced to a single flag. Mutual
    reception is reported as its own row.

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
        if 'house' in found or 'exaltation' in found:
            return 'Perfect' if sahl else 'Strongest (131)'
        if sahl:
            # 50 ranks triplicity below perfect; bound only counts paired
            # with triplicity, on Masha'allah's authority (54-55).
            if 'triplicity' in found and 'bound' in found:
                return "Complete, triplicity with bound (54-55, Masha'allah)"
            if 'triplicity' in found:
                return 'Lesser, triplicity alone (50)'
            return None                                   # bound alone is not reception for Sahl
        minors = [d for d in found if d in ('bound', 'triplicity', 'face')]
        return 'Complete (132)' if len(minors) >= 2 else 'Weak, one minor dignity alone (132)'

    for row in rows:
        if row['aspect_name'] == 'Aversion':
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
            g = grade(found) if found else None
            if not g:
                continue
            found_here.append(receiver)
            results.append({
                'Receiver': receiver, 'Received': received, 'Direction': direction,
                'Via': ', '.join(found), 'Grade': g, 'Mode': mode,
            })
        if len(found_here) == 2:
            results.append({
                'Receiver': f'{applicant} & {accepter}', 'Received': 'each other',
                'Direction': 'Mutual', 'Via': '–', 'Grade': 'Mutual reception',
                'Mode': mode,
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
    rows = _pairwise_configurations(planetary_data)
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    results = []

    for r in rows:
        if r['aspect_name'] == 'Aversion' or not _is_connected(r):
            continue
        a, b = r['light_name'], r['heavy_name']
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

def get_effective_house(longitude, cusps, angles_only=True):
    """Quadrant house WITH the five-degree carryover applied: a planet
    within 5 degrees before a cusp is counted as already in that house.

    Both source statements are about the stakes specifically -- neither
    says "any cusp" -- and the transitions they describe (12th into 1st,
    3rd into 4th, 6th into 7th, 9th into 10th) are exactly the cadent-to-
    angular ones, which is why the rule is phrased as not FALLING from the
    stake. So angles_only=True is the literal reading and the default;
    later authors generalise it to all twelve cusps, which the parameter
    allows without pretending Sahl said it.

    get_house_number() is deliberately left alone and still returns strict
    cusp membership. The two are separate facts and both are kept."""
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
    asc_sign_idx = int(ascendant_lon // 30)
    target_sign_idx = int(longitude // 30)
    return ((target_sign_idx - asc_sign_idx) % 12) + 1

def get_essential_rulers(longitude):
    """Look up the classical essential dignities (domicile, exaltation,
    triplicity, term, face) ruling an arbitrary zodiacal degree — not tied
    to any specific planet's own position, unlike evaluate_essential_
    dignities(). Used to profile the prenatal syzygy degree itself."""
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
    _add_score(rulers['domicile'], 5)
    _add_score(rulers['exaltation'], 4)
    _add_score(active_triplicity_lord, 3)
    _add_score(rulers['term'], 2)
    _add_score(rulers['face'], 1)
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
CHALDEAN_HOUR_ORDER = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']

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
        # No real sunrise/sunset exists at this date/location (polar day or
        # polar night) — there's no meaningful temporal-hour boundary to
        # anchor to, so fall back to the plain calendar weekday (no
        # astrological-day rollover correction) and an equal 2-hour
        # division of the 24-hour civil day, continuing the same 7-cycle.
        approximate = True
        day_lord = DAY_LORD_BY_WEEKDAY[_weekday_from_jd(jd_utc, utc_offset_hours)]
        cycle_offset = min(local_dt.hour // 2, 11)

    start_index = CHALDEAN_HOUR_ORDER.index(day_lord)
    hour_lord = CHALDEAN_HOUR_ORDER[(start_index + cycle_offset) % 7]

    return {'Day Lord': day_lord, 'Hour Lord': hour_lord, 'Approximate': approximate}

# --- Classical Lots (Arabic Parts) ---------------------------------------

def calculate_classical_lots(asc, sun, moon, sect):
    """Lots of Fortune, Spirit, Exaltation, and Basis, sect-flipped per
    medieval practice. Basis is placed the short angular distance between
    Fortune and Spirit away from the Ascendant."""
    is_diurnal = (sect == 'Diurnal')

    fortune = (asc + moon - sun) % 360.0 if is_diurnal else (asc + sun - moon) % 360.0
    spirit = (asc + sun - moon) % 360.0 if is_diurnal else (asc + moon - sun) % 360.0
    exaltation = (asc + 19.0 - sun) % 360.0 if is_diurnal else (asc + 33.0 - moon) % 360.0

    raw_dist = abs(fortune - spirit)
    dist = raw_dist if raw_dist <= 180.0 else 360.0 - raw_dist
    basis = (asc + dist) % 360.0

    lots = {
        'Lot of Fortune': fortune,
        'Lot of Spirit': spirit,
        'Lot of Exaltation': exaltation,
        'Lot of Basis': basis,
    }
    result = []
    for name, lon_val in lots.items():
        result.append({
            'Lot Name': name,
            'Position': get_degree_string(lon_val),
            'WSH House': get_wsh_house(lon_val, asc),
            'Sign Dispositor': SIGN_TO_DOMICILE.get(get_zodiac_sign(lon_val), '-'),
        })
    return result

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
            conditions.append("Via Combusta")

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
MASCULINE_QUADRANT_HOUSES = {4, 5, 6, 10, 11, 12}
FEMININE_QUADRANT_HOUSES = {1, 2, 3, 7, 8, 9}

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

    def ahead(rays):
        return any(0.0 < (d - lon) % 360.0 <= orb for d in rays)

    def behind(rays):
        return any(0.0 < (lon - d) % 360.0 <= orb for d in rays)

    kind = None
    if (ahead(a_rays) and behind(b_rays)) or (ahead(b_rays) and behind(a_rays)):
        kind = 'by degree (57)'
    else:
        # The second form of 57: separating from one, connecting with the
        # other -- Sahl's own shape, which Abu Ma'shar folds in here.
        for sep_t, con_t in ((members[0], members[1]), (members[1], members[0])):
            sep = any(r['light_name'] == planet and r['heavy_name'] == sep_t
                       and r['motion'] == 'Separating' and _is_connected(r) for r in rows)
            con = any(r['light_name'] == planet and r['heavy_name'] == con_t
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

    # 60: the Sun or a fortune casting a ray within 7 degrees breaks it.
    for breaker in ({'Sun'} | FORTUNES) - set(members) - {planet}:
        if breaker not in planetary_data:
            continue
        if any(abs(((d - lon + 180.0) % 360.0) - 180.0) < orb
               for d in _ray_degrees(planetary_data[breaker]['longitude'])):
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
        sep_row = next((r for r in rows if r['aspect_name'] != 'Aversion'
                         and (r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == sep_target
                         and r['motion'] == 'Separating' and _is_connected(r)), None)
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

SIGN_ORDER = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

FIXED_SIGNS = {'Taurus', 'Leo', 'Scorpio', 'Aquarius'}

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
        infortune_contact = any(
            r['aspect_name'] in ('Conjunction', 'Square', 'Opposition')
            and (r['p1'] in INFORTUNES or r['p2'] in INFORTUNES)
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
            if other_house in CADENT_HOUSES or other_sign in FALLS.get(other, []):
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
        if planet in ('Saturn', 'Jupiter', 'Mars'):
            sun_lon = planetary_data['Sun']['longitude']
            signed_from_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
            if signed_from_sun < 0:
                labels.append('Masculine planet, eastern of the Sun (84)')

        # (85) "In their own glow: that is, a masculine planet in the day,
        # and a feminine planet in the night." The translator's footnote
        # calls the gendered wording an error for DIURNAL/NOCTURNAL (Mars
        # being masculine but nocturnal), and Fig. 24 renders the row as
        # simply "of the sect" -- so this is bare sect agreement. An
        # earlier version reused accidental[]['Hayz'], which additionally
        # demands the right side of the horizon and a sign of matching
        # gender, and so under-reported the testimony.
        if planet == 'Mercury':
            sun_lon = planetary_data['Sun']['longitude']
            planet_is_diurnal = (((lon - sun_lon + 180.0) % 360.0) - 180.0) < 0
        elif planet in DIURNAL_SECT_PLANETS:
            planet_is_diurnal = True
        else:
            planet_is_diurnal = False
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

        # (88) Masculine/feminine quadrant and sign matching the planet's
        # own gender. This is Sahl's ELEVENTH testimony, not the tenth --
        # an earlier version numbered it (87) and omitted the heart of the
        # Sun entirely, leaving only ten of the eleven that 77 announces.
        gender = PLANET_GENDER.get(planet)
        if gender == 'Masculine' and house in MASCULINE_QUADRANT_HOUSES:
            labels.append('In a matching-gender (masculine) quadrant (88)')
        elif gender == 'Feminine' and house in FEMININE_QUADRANT_HOUSES:
            labels.append('In a matching-gender (feminine) quadrant (88)')
        if gender == 'Masculine' and sign in MASCULINE_SIGNS:
            labels.append('In a matching-gender (masculine) sign (88)')
        elif gender == 'Feminine' and sign in FEMININE_SIGNS:
            labels.append('In a matching-gender (feminine) sign (88)')

        if labels:
            results.append({'Planet': planet, 'Strength Testimonies': ', '.join(labels), 'Count': len(labels)})
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
        for r in rows:
            if r['aspect_name'] not in ('Conjunction', 'Square', 'Opposition') or planet not in (r['p1'], r['p2']):
                continue
            other = r['p2'] if r['p1'] == planet else r['p1']
            if other in INFORTUNES and _is_connected(r):
                labels.append(f'Connecting with {other} by assembly, square, or opposition (94)')

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
        for r in rows:
            if r['aspect_name'] == 'Aversion' or planet not in (r['light_name'], r['heavy_name']):
                continue
            other = r['heavy_name'] if r['light_name'] == planet else r['light_name']
            if _is_connected(r) and get_wsh_house(planetary_data[other]['longitude'], ascendant_lon) in CADENT_HOUSES:
                labels.append(f'Connecting with {other}, itself falling from the Ascendant (97)')
            if (r['applicant'] or r['light_name']) == planet and r['motion'] == 'Separating' and _is_connected(r):
                other_rulers = get_essential_rulers(planetary_data[other]['longitude'])
                if planet in (other_rulers['domicile'], other_rulers['exaltation']):
                    labels.append(f'Separating from {other}, which would have received it (97)')

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
            labels.append('With the Head or Tail, without latitude (99)')

        # (100) Inverted: in the seventh sign from its own house (Detriment).
        if ess['Detriment']:
            labels.append('Inverted, in the seventh sign from its own house (100)')

        if labels:
            results.append({'Planet': planet, 'Weakness Testimonies': ', '.join(labels), 'Count': len(labels)})
    return results

def evaluate_abu_mashar_condition(planetary_data, natal_houses, sect, essential, accidental, jd, ascendant_lon, sim=None):
    """Planetary condition per Abu Ma'shar's Great Introduction VII.6: good
    fortune (1-20), strength (21-29), weakness (30-46), misfortune (47-62)
    -- plus, for the Moon only, Sahl's own ten defects (The Introduction
    Ch.3, 103-112, via _corruption_of_the_moon_labels()) rather than
    VII.6's own, differently-numbered eleven-item version (63-74).
    Distinct from -- and the authoritative source for -- the Rhetorius/PN4
    delineation switch; the older Hellenistic net dignity score in
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
    rows = _pairwise_configurations(planetary_data)
    reception_rows = evaluate_reception(planetary_data, sect)
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
    moon_corruption_count = _corruption_of_the_moon(planetary_data, ascendant_lon, sect)

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
            (r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) in FORTUNES and r['motion'] == 'Separating' and _is_connected(r)
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
            positive.append('Aspects the (uncorrupted) Moon (8)')
        # 9 is a conjunction, not a synonym: "quick in motion, INCREASING IN
        # LIGHT and number." VII.1, 19-21 defines increasing in light as
        # falling from the apogee toward the earth, so geocentric distance
        # decreasing. "Number" is the equation-table term of VII.1, 23-25,
        # which Dykes' note there says has no direct astrological import, so
        # it is not required. An earlier version accepted swiftness alone.
        increasing_in_light = data.get('speed_in_dist', 0.0) < 0
        if acc['Swift'] and increasing_in_light:
            positive.append('Swift and increasing in light (9)')
        halb = ess['Domicile'] or ess['Exalt'] or ess['Triplicity'] or ess['Term'] or ess['Face'] or acc['Joy']
        if halb:
            positive.append('Halb (10)')
        brightness = _brightness_category(lon)
        if brightness == 'Bright':
            positive.append('Bright degree (11)')
        # Reception (Sahl, The Introduction Ch.3, 49-56, Fig. 16): a planet
        # connecting with a planet from its own house or exaltation has
        # "perfect reception, with truthful intention" (49); connecting
        # with a planet from its own triplicity is a lesser reception,
        # below that (50). Sahl's own definition doesn't extend to bound
        # (term) -- and deliberately excludes face: Dykes treats face as a
        # poor fit for this kind of technical judgment throughout,
        # considering its real utility to lie in astrological magic (per
        # the Picatrix) rather than rulership tests like this one -- so
        # this follows Sahl's narrower scope rather than Abu Ma'shar's
        # later five-dignity expansion (Great Introduction VII.5, 129-133).
        # 130 there does still supply the mutual/reverse case (the far
        # planet is itself in a dignity of the accepting planet's
        # placement), applied here under the same narrowed scope.
        rulers = get_essential_rulers(lon)
        triplicity_key_local = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
        # Reception is defined once, in evaluate_reception(), under the
        # active author profile; this row just reports what it found for
        # this planet. An earlier version reimplemented it inline and
        # blended the two authors -- Sahl's narrowed dignity scope with
        # Abu Ma'shar's paragraph numbering and his reverse case.
        received = any(rec['Received'] == planet or (rec['Direction'] == 'Mutual'
                                                      and planet in rec['Receiver'].split(' & '))
                        for rec in reception_rows)
        for rec in reception_rows:
            if rec['Direction'] == 'Mutual':
                if planet in rec['Receiver'].split(' & '):
                    positive.append(f"Mutual reception with {[x for x in rec['Receiver'].split(' & ') if x != planet][0]}")
            elif rec['Received'] == planet:
                positive.append(f"Received by {rec['Receiver']} ({rec['Grade'].split(' (')[0].lower()}, via {rec['Via']})")
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
        if planet in PLANET_SWE_IDS and abs(speed) <= 0.02:
            res_next, _ = swe.calc_ut(jd + 1.0, PLANET_SWE_IDS[planet])
            if res_next[3] > speed:
                station = 'second'
                positive.append('Second station (24)')
            elif res_next[3] < speed:
                station = 'first'
        # 25 is "GOING OUT of the rays of the Sun," a departure, not a
        # location: VII.2, 12 has the planet "begin in [its] advancement
        # towards easternization" at exactly this point. So the elongation
        # must be opening, not merely large. An earlier version credited
        # every planet anywhere outside the rays, including one sinking back
        # toward them.
        _signed_sun = ((lon - planetary_data['Sun']['longitude'] + 180.0) % 360.0) - 180.0
        elongation_opening = (
            planet != 'Sun'
            and (speed - planetary_data['Sun']['speed_in_lon']) * _signed_sun > 0
        )
        if not acc['Combust'] and not acc['UnderBeams'] and elongation_opening:
            positive.append('Going out of the rays (25)')
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
        if is_superior and is_eastern_of_sun:
            if configured_to(planet, {'Sun'}, {'Sextile'}):
                positive.append('Superior, eastern of the Sun, by sextile (27)')
            else:
                positive.append('Superior, eastern of the Sun (27)')
        in_masculine_quadrant = house in MASCULINE_QUADRANT_HOUSES
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
        is_slow = 0 <= speed < AVERAGE_DAILY_MOTION.get(planet, 1.0)
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
        in_harsh_burned_path = 199.0 <= lon < 213.0  # 19 Libra - 3 Scorpio
        if in_harsh_burned_path:
            negative.append('Burned path, harsh band (40)')
        elif in_burned_path:
            negative.append('Burned path (39/71)')
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
        if sim is not None:
            sign_exits = sim['events'][planet]['sign_exits']
            exit_day = sign_exits[0] if sign_exits else sim['horizon_days']
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
        if is_superior and not is_eastern_of_sun:
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
        inf_46 = ([ 'beginning of easternization' ]
                  if is_eastern_of_sun and abs(signed_from_sun) < SOLAR_RAYS_ORB[planet][0] else []) + \
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
        # 103-112) remain in Sahl's own tables under their own numbering --
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
        # her ten defects, each as its own vote. Over 325 sampled charts
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
    moon = planetary_data['Moon']
    lon, lat, speed = moon['longitude'], moon['latitude'], moon['speed_in_lon']
    sun_lon = planetary_data['Sun']['longitude']
    sign = get_zodiac_sign(lon)
    rows = _pairwise_configurations(planetary_data)
    labels = []

    signed_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
    elongation = abs(signed_sun)

    # [1] (64) Eclipsed. A lunar eclipse needs her near the Sun's exact
    # opposition AND near a node; a solar eclipse is the Moon's conjunction
    # under the same node condition. Swiss Ephemeris is asked directly when
    # a julian day is available, and the geometry is the fallback.
    north_node_lon = planetary_data['North Node']['longitude']
    node_dist = min(abs(((lon - north_node_lon + 180) % 360) - 180),
                    abs(((lon - (north_node_lon + 180.0) + 180) % 360) - 180))
    eclipsed = False
    if jd is not None:
        try:
            # retflag > 0 means an eclipse is in progress at this moment.
            eclipsed = swe.lun_eclipse_how(jd, [0.0, 0.0, 0.0])[0] > 0
        except Exception:
            eclipsed = False
    if not eclipsed:
        eclipsed = node_dist <= 12.0 and (elongation >= 168.0 or elongation <= 12.0)
    if eclipsed:
        labels.append('Eclipsed (64)')

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
    terms = EGYPTIAN_TERMS.get(sign, [])
    if terms and (lon % 30.0) >= terms[-2][0]:
        labels.append('In the last bound of the sign (72)')

    # [10] (73) Slow, "when she goes at less than her mean motion."
    if 0 <= speed < AVERAGE_DAILY_MOTION['Moon']:
        labels.append('Slow in motion (73)')

    # [11] (74) In the ninth house from the Ascendant.
    if get_wsh_house(lon, ascendant_lon) == 9:
        labels.append('In the ninth house (74)')

    return labels

def _corruption_of_the_moon_labels(planetary_data, ascendant_lon, sect):
    """The ten defects of the Moon (Sahl, The Introduction Ch.3, 102-113).
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

    Split from evaluate_abu_mashar_condition() so the count alone can be
    obtained up-front (for the "Moon fortunate" test in VII.6, 8) without
    recursion, and the full labels reused inside the main per-planet loop
    for the Moon's row."""
    moon = planetary_data['Moon']
    lon, speed = moon['longitude'], moon['speed_in_lon']
    sun_lon = planetary_data['Sun']['longitude']
    sign = get_zodiac_sign(lon)
    rows = _pairwise_configurations(planetary_data)
    labels = []

    def connected_row(other):
        return next((r for r in rows if {r['p1'], r['p2']} == {'Moon', other}), None)

    # [1] (103) Burned, within 12 degrees of the Sun, front or behind.
    sun_dist = abs(((lon - sun_lon + 180) % 360) - 180)
    if sun_dist <= 12.0:
        labels.append('Burned, within 12 degrees of the Sun (103)')

    # [2] (104) In the degrees of her own fall (Scorpio), or connecting
    # with a planet in ITS own fall.
    if sign in FALLS.get('Moon', []):
        labels.append('In her own fall, Scorpio (104)')
    for other in planetary_data:
        if other in ('Moon', 'North Node'):
            continue
        r = connected_row(other)
        if r and r['aspect_name'] != 'Aversion' and _is_connected(r):
            other_sign = get_zodiac_sign(planetary_data[other]['longitude'])
            if other_sign in FALLS.get(other, []):
                labels.append(f'Connecting with {other}, itself in its own fall (104)')

    # [3] (105) Opposed to the Sun, within 12 degrees, not yet having
    # reached the exact opposition (still approaching, not past it).
    opp_target = (sun_lon + 180.0) % 360.0
    signed_to_opp = ((opp_target - lon + 180) % 360) - 180
    if 0 <= signed_to_opp <= 12.0:
        labels.append("Approaching the Sun's opposition, within 12 degrees (105)")

    # [4] (106) Assembled with an infortune, or looking at it from a
    # square or opposition (sextile/trine don't count here) -- or enclosed
    # between the two infortunes (separating from one, connecting with the
    # other -- Sahl's own Enclosure test, 119-123).
    if any(row['aspect_name'] in ('Conjunction', 'Square', 'Opposition')
           and 'Moon' in (row['p1'], row['p2'])
           and (row['p1'] in INFORTUNES or row['p2'] in INFORTUNES)
           for row in rows):
        labels.append('Assembled with, square, or opposed by an infortune (106)')
    blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}
    is_enc, severe, _sep, _con = _sahl_enclosed('Moon', INFORTUNES, rows, blocking_pairs)
    if is_enc:
        labels.append('Enclosed between the two infortunes (106, 119-123)' + (', severe' if severe else ''))

    # [5] (107) With the Head or Tail, IN ONE SIGN, less than 12 degrees
    # between them -- same-sign co-presence (Sahl's own "connection" shape)
    # plus the Moon's own light-radius, not merely raw closeness in degree
    # regardless of sign boundary.
    north_node_lon = planetary_data['North Node']['longitude']
    south_node_lon = (north_node_lon + 180.0) % 360.0
    for node_lon in (north_node_lon, south_node_lon):
        if get_zodiac_sign(node_lon) == sign and abs(((lon - node_lon + 180) % 360) - 180) < 12.0:
            labels.append('With the Head or Tail, in one sign and under 12 degrees (107)')
            break

    # [6] (108) In the twelfth sign from her own house (Gemini, since her
    # house is Cancer), or in the LAST degrees of the sign specifically --
    # the final Egyptian-term division, which (per the table) is always
    # ruled by one of the two infortunes, not just any infortune-ruled
    # bound elsewhere in the sign (e.g. Aries' 20-25 degree bound is
    # Mars's but isn't the sign's last one).
    if sign == 'Gemini':
        labels.append("In Gemini, the twelfth sign from her own house (108)")
    sign_terms = EGYPTIAN_TERMS[sign]
    last_bound_start = sign_terms[-2][0] if len(sign_terms) > 1 else 0
    if (lon % 30) >= last_bound_start:
        labels.append("In the last degrees of the sign, the infortunes' bound (108)")

    # [7] (109) "Falling from the stakes, or connecting with a planet
    # falling from the stakes" -- a plain disjunction, verbatim. (A prior
    # edit replaced this with a cadent + averse-to-Ascendant + separating-
    # from-an-infortune predicate, which is Weakness 91/97 material and
    # appears nowhere in 109; reverted.)
    moon_house = get_wsh_house(lon, ascendant_lon)
    if moon_house in CADENT_HOUSES:
        labels.append('Falling from the stakes (109)')
    for other in planetary_data:
        if other in ('Moon', 'North Node'):
            continue
        r = connected_row(other)
        if r and r['aspect_name'] != 'Aversion' and _is_connected(r):
            if get_wsh_house(planetary_data[other]['longitude'], ascendant_lon) in CADENT_HOUSES:
                labels.append(f'Connecting with {other}, itself falling from the stakes (109)')

    # [8] (110) In the burned path -- Sahl's own wording narrows this to
    # the end of Libra and the beginning of Scorpio specifically (not the
    # full two signs), matching the alternate 19-Libra-to-3-Scorpio band
    # footnoted there.
    if 199.0 <= lon < 213.0:
        labels.append('In the burned path, end of Libra/beginning of Scorpio (110)')

    # [9] (111) Wild -- empty of course, not connecting with any planet.
    # Sahl's own present-tense definition (not Abu Ma'shar's later,
    # prospective sharpening used elsewhere in this file).
    if not any((row['applicant'] or row['light_name']) == 'Moon' and row['motion'] == 'Applying' and _is_connected(row) for row in rows):
        labels.append('Wild, empty of course (111)')

    # [10] (112) Slow in course, or waning in light (past full, heading
    # back toward new).
    if 0 <= speed < AVERAGE_DAILY_MOTION['Moon']:
        labels.append('Slow in course (112)')
    if 180.0 < ((lon - sun_lon) % 360.0) < 360.0:
        labels.append('Waning in light (112)')

    return labels

def _corruption_of_the_moon(planetary_data, ascendant_lon, sect):
    return len(_corruption_of_the_moon_labels(planetary_data, ascendant_lon, sect))

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
            'Placed In (WSH)': placed_in,
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
    "Newer (Al-Qabisi/Abu Ma'shar)": {'domicile': 5, 'exaltation': 4, 'triplicity': 3, 'term': 2, 'face': 1},
}

# "Places" bonus wheels (Handy Tables Lesson 20): a candidate planet's own
# Whole-Sign-House placement adds this many points to its total, on top of
# its essential-dignity claim at the point being profiled. Both are
# permutations of 1-12; each is paired with the weighting scheme from the
# same named tradition -- ibn Ezra's own wheel with the newer/Al-Qabisi
# scheme (his worked table is the fuller, day/hour/places-bonus one this
# whole function generalizes), Masha'allah's wheel with the older/
# Masha'allah scheme. That pairing isn't stated outright in the source --
# it's the more coherent reading of two wheels each already tied to a named
# tradition, not an arbitrary choice.
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
    Which pairing to use is not stated in the source, so each scheme keeps
    the wheel of its own named tradition, as before.

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

    results = {}
    for scheme_name, weights in VICTOR_WEIGHTS.items():
        places_values = VICTOR_PLACES_VALUES[scheme_name]
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
        runners = sorted(columns, key=lambda p: -totals[p])
        tied = [p for p in columns if totals[p] == totals[victor]]
        results[scheme_name] = {
            'grid': grid,
            'victor': ' / '.join(tied) if len(tied) > 1 else victor,
            'total': totals[victor],
            'runner_up': f"{runners[1]} ({totals[runners[1]]})" if len(runners) > 1 else '-',
            'tied': len(tied) > 1,
        }
    return results

def evaluate_planets_in_houses(planetary_data, abu_mashar_condition, ascendant_lon):
    """For each of the 7 classical planets, determine its Whole Sign House
    placement, then look up the Rhetorius/PN4-derived delineation for that
    planet in that house under its Good/Bad condition -- per Abu Ma'shar's
    own VII.6 condition verdict (evaluate_abu_mashar_condition()), not the
    older Rhetorius/PN4 net dignity score."""
    results = []
    for planet, data in planetary_data.items():
        if planet == 'North Node': continue

        wsh_house = get_wsh_house(data['longitude'], ascendant_lon)
        condition_data = abu_mashar_condition[planet]
        condition = condition_data['Condition']
        delineation = PLANETS_IN_HOUSES[wsh_house][planet][condition]

        results.append({
            'Planet': planet,
            'Placed In (WSH)': wsh_house,
            'Net (heuristic)': condition_data['Net'],
            'Reading Selected': condition,
            'Classical Signification': delineation,
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

st.sidebar.markdown("---")
st.sidebar.header("Doctrine")
CONNECTION_PROFILE = st.sidebar.radio(
    "Connection rule",
    list(CONNECTION_PROFILES.keys()),
    help=(
        "Which author's rule decides whether a pair counts as Connected. The two agree that "
        "looking is sign-to-sign and connecting is degree-to-degree, but they part company at "
        "the sign boundary and on what activates a connection.\n\n"
        "**Sahl** (The Introduction Ch.3, 6-21): the applying planet's OWN light governs "
        "(15/12/9/8/7 by planet), so the test is asymmetric. A planet at the end of a sign that "
        "is not connecting with anything, whose light strikes into the next sign, IS connected "
        "to the first planet there by body (20-21) -- even though the two do not see each other.\n\n"
        "**Abu Ma'shar** (Great Introduction VII.4-5): two flat distances instead -- assembly "
        "within 15 degrees in one sign (VII.4, 3), aspects within 12 degrees of exact (VII.5, 27, "
        "since aspect rays have no bodies of their own). No out-of-sign connection at all: across "
        "a boundary the bodies merely 'mix their natures in a weak way' (VII.5, 14).\n\n"
        "Everything downstream -- transfer, collection, blocking, handing over, reception -- reads "
        "this setting."
    ),
)

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
        wildness_data = evaluate_wildness(p_data)
        reflections = evaluate_reflections_of_light(p_data, chart_data['ascendant'])
        blocking_data = evaluate_blocking(p_data)
        enclosure_data = evaluate_enclosure(p_data)
        handing_over_data = evaluate_handing_over(p_data, sect)
        reception_data = evaluate_reception(p_data, sect)
        non_reception_data = evaluate_non_reception(p_data, sect)
        strength_data = evaluate_strength_of_planets(p_data, essential, accidental, chart_data['ascendant'], sect, chart_data['houses'])
        weakness_data = evaluate_weakness_of_planets(p_data, essential, accidental, chart_data['ascendant'], sect)
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
        special_degrees = evaluate_special_degrees(p_data)
        house_lords_data = evaluate_house_lords(p_data, chart_data['ascendant'])
        victors_data = evaluate_victors(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'],
                                         syzygy['syzygy_longitude'], sect, chronocrats)
        planets_in_houses_data = evaluate_planets_in_houses(p_data, abu_mashar_condition, chart_data['ascendant'])
        time_lords_data = calculate_time_lords(chart_data['ascendant'], input_date, target_date)

        svg_code = generate_hybrid_svg(chart_data, location_query, lat, lon, local_dt, tz_name)

        st.title("Traditional Astrological Engine")

        tab_wheel, tab_metrics = st.tabs(["Chart Wheel (WSH)", "Tables & Metrics"])

        with tab_wheel:
            st.iframe(svg_code, height=720)

        with tab_metrics:
            tab_chart, tab_dignity, tab_connections = st.tabs(["Chart & Timing", "Dignity, Condition & Houses", "Connections & Corruption (Sahl Ch.3 / Abu Ma'shar VII.5)"])

            with tab_chart:
                hdr1, hdr2, hdr3, hdr4 = st.columns(4)
                hdr1.metric("Calculated JD", f"{chart_data['julian_day']:.4f}")
                hdr2.metric("Sect", sect)
                hdr3.metric("Lord of the Day", chronocrats['Day Lord'])
                hdr4.metric("Lord of the Hour", chronocrats['Hour Lord'])
                if chronocrats.get('Approximate'):
                    st.caption(
                        "\u26a0\ufe0f No sunrise/sunset exists for this date at this location (circumpolar "
                        "day/night) — Day and Hour Lord fall back to the plain calendar weekday and an "
                        "equal 2-hour division of the day, rather than true unequal temporal hours."
                    )

                st.subheader("Chronocrator Matrix (Active Time Lords)", help='The planets and signs ruling the current predictive period -- the year (profection), month, day, and hour -- each cycling to the next lord in zodiacal order as time passes.')
                st.dataframe(pd.DataFrame(time_lords_data), hide_index=True, width='stretch')

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Planetary Positions", help="The seven classical planets' ecliptic (tropical) longitude at the moment of birth, in sign and degree.")
                    # True planets only — angles, nodes, and Lot of Fortune
                    # now live in the "Calculated Points" table alongside it.
                    pos_list = [{"Planet": p, "Position": get_degree_string(d['longitude'])} for p, d in p_data.items() if p != 'North Node']
                    st.dataframe(pd.DataFrame(pos_list), hide_index=True, width='stretch')

                    st.subheader("Calculated Points", help="Non-planetary chart points: the four angles (Ascendant, Midheaven, Descendant, Imum Coeli), the Moon's Nodes, and the Lot of Fortune (a sect-dependent formula combining the Sun, Moon, and Ascendant).")
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
                    st.dataframe(pd.DataFrame(calc_list), hide_index=True, width='stretch')

                with col2:
                    st.subheader("Classical Lots", help='Arabic Parts: sect-dependent formulas combining two planets or points with the Ascendant to derive a new sensitive degree tied to a specific topic (e.g. Fortune = body/livelihood, Spirit = mind/action).')
                    st.dataframe(pd.DataFrame(classical_lots), hide_index=True, width='stretch')

                    st.subheader("House Cusps (Alchabitius)", help='The twelve quadrant house cusps computed by the Alchabitius (semi-arc) system -- shown alongside the Whole-Sign houses used everywhere else in this app, since some techniques call for quadrant division specifically.')
                    house_list = [{"House": i+1, "Alchabitius Cusp": get_degree_string(chart_data['houses'][i])} for i in range(12)]
                    st.dataframe(pd.DataFrame(house_list), hide_index=True, width='stretch')


            with tab_dignity:
                st.subheader("Planetary Condition (Abu Ma'shar VII.6)", help="Each planet checked against the conditions Abu Ma'shar lists in Great Introduction VII.6, kept in his own four groups -- good fortune (1-20), strength (21-29), weakness (30-46), misfortune (47-62) -- plus, for the Moon only, HIS OWN eleven corruptions of her (63-74) shown as their own count rather than folded in with the rest. Sahl's ten (The Introduction Ch.3, 103-112) are a different list, not a variant reading of this one, and stay in Sahl's own tables: Abu Ma'shar has eclipse, the twelfth-part of Saturn or Mars, southern latitude and the ninth house, none of which Sahl lists; Sahl has her own fall, connection with a fallen planet, and wildness, none of which appear here.\n\nThe four counts and the labels are the report. NET and VERDICT are a convenience of this app and NOT Abu Ma'shar's: he enumerates the conditions but never totals them, and the chapter supplies no weighting and no rule for ties. They exist because the Rhetorius/PN4 delineations in Topical Planets in Houses have to choose between a good and a bad reading.\n\nTwo distortions in the raw count are corrected so that one fact cannot vote repeatedly: the Moon's ten defects contribute a single entry (as their own checklist they had been dragging her to a Bad verdict about three times as often as any other planet), and multiple reception rows for one planet likewise count once.\n\nEnclosure here is Abu Ma'shar's own (56-62) -- by degree within 7 degrees either side counting rays as well as bodies, by sign in the 2nd and 12th, or separating from one encloser and connecting with the other -- and it can be DISSOLVED when the Sun or a fortune casts a ray within 7 degrees of the enclosed planet (60-61). The standalone Enclosure table under Connections & Corruption is Sahl's separate version.\n\nThe by-sign type counts an encloser's RAYS as well as its body, which is what 58 says twice. Be aware that this makes it common: it fires on roughly 43% of placements, because a planet's rays reach eight of the twelve signs. A bodies-only variant at about 2% exists in the code (SIGN_ENCLOSURE_BODIES_ONLY) but is this project's own conjecture, not the text, so it is off.")
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
                        "Net (heuristic)": cond['Net'],
                        "Verdict (heuristic)": cond['Condition'],
                        "Good Fortune / Strength": ", ".join(cond['Positive Labels']) if cond['Positive Labels'] else "-",
                        "Weakness / Misfortune": ", ".join(cond['Negative Labels']) if cond['Negative Labels'] else "-",
                    })
                df_condition = pd.DataFrame(condition_list).sort_values(by="Net (heuristic)", ascending=False)
                st.dataframe(df_condition, hide_index=True, width='stretch')
                st.caption(
                    ":orange[**Net and Verdict are this app's heuristic, not Abu Ma'shar's.**] He enumerates these "
                    "conditions; he nowhere adds them up, and VII.6 gives no weighting and no tie rule. They are kept "
                    "only because the Rhetorius/PN4 delineations below have to pick one of two readings. Read the four "
                    "counts and the labels themselves in preference to the single number."
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Lordship Mapping", help="The domicile, exaltation, triplicity, term (bound), and face ruler of each planet's OWN degree -- the five essential dignities, read at the planet's own position rather than another point.")
                    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
                    lordship_list = []
                    for p, data in p_data.items():
                        if p == 'North Node': continue
                        rulers = get_essential_rulers(data['longitude'])
                        lordship_list.append({
                            "Planet": p,
                            "Sign Dispositor": rulers['domicile'],
                            "Exaltation Lord": rulers['exaltation'],
                            "Triplicity Lord": rulers[triplicity_key],
                            "Term Lord": rulers['term'],
                            "Face Lord": rulers['face'],
                        })
                    st.dataframe(pd.DataFrame(lordship_list), hide_index=True, width='stretch')

                    st.subheader("Special Degrees & Conditions", help='Flags planets in the Via Combusta (15 Libra-15 Scorpio, a historically "burnt" span), a classical welled/pitted degree of their current sign (Abu Ma\'shar, Great Introduction V.21), or one of Sahl\'s two sign-boundary conditions.\n\nENTERING: "every planet which is at the beginning of a sign is weak until it is firmly established in it and comes to be 5 degrees within it" (Fifty Aphorisms #44, 87), repeated in On Nativities Ch.1.22, 9. This is the other half of the five-degree rule that also governs advancement.\n\nLEAVING: "if a planet came to be in the last degree of the sign, then its strength has already gone away from that sign, and its strength is in the next sign ... like a man putting his foot on the threshold of his door. And if a planet was in the twenty-ninth degree, then indeed the strength of the planet IS in that sign" (Fifty Aphorisms #15, 31-33) -- so the 29th degree still counts and only the 30th has left.')
                    if special_degrees:
                        st.dataframe(pd.DataFrame(special_degrees), hide_index=True, width='stretch')
                    else:
                        st.write("No planets in anomalous degrees.")

                with col2:
                    st.subheader("Prenatal Lunation (Syzygy)", help='The New or Full Moon exact before birth, its degree, natal house, and Almuten (victor) -- a key predictive point in Persian/Abbasid technique, thought to set the tone for the life or the period leading up to birth.')
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


                st.subheader("Victor of the Chart (ibn Ezra's victor #1, 1485/1537)", help="Ibn Ezra's worksheet reproduced cell for cell, so it can be checked against a hand-filled sheet. The seven planets are the columns. The first five rows score each planet's essential-dignity claim AT THAT POINT'S degree -- Sun, Moon, Ascendant, Lot of Fortune, and the prenatal New/Full Moon. Then Lord of the Day (+7), Lord of the Hour (+6) and Places are added ONCE each, not per point; Places is keyed the other way round, by the candidate planet's own Whole-Sign house. Every column is summed into Totals, and the single highest total is the chart's victor.\n\nTwo independent choices are shown side by side: the dignity weights (Older = al-Tabari/Masha'allah, Bound 3 > Triplicity 2; Newer = al-Qabisi/Abu Ma'shar, Triplicity 3 > Bound 2) and the Places wheel of the same named tradition. Ibn Ezra's later victor #2 (1507) replaces the two chronocrator rows with a Superiors row scored only for Saturn, Jupiter and Mars; its weight is not given in the course materials, so it is not implemented rather than guessed.")
                for scheme_name, res in victors_data.items():
                    st.markdown(f"**{scheme_name}** — victor: **{res['victor']}** ({res['total']}), runner-up {res['runner_up']}"
                                + ("  \n:orange[Tied at the top — the sheet does not break ties.]" if res['tied'] else ""))
                    st.dataframe(pd.DataFrame(res['grid']), hide_index=True, width='stretch')

                st.subheader("Topical Planets in Houses (Rhetorius & PN4)", help="Each planet's Whole-Sign house placement and the Rhetorius/PN4 delineation for it. Each pairing has a good and a bad reading, and the one shown is picked by that planet's Net score in the Planetary Condition table above -- which is this app's own heuristic, not Abu Ma'shar's. Treat the selected reading as a starting point, and check it against the four condition counts and the labels rather than trusting the switch.")
                st.dataframe(pd.DataFrame(planets_in_houses_data), hide_index=True, width='stretch')

                st.subheader("Topical House Lords (Masha'allah)", help='For each of the twelve topical houses, its domicile lord\'s own Whole-Sign placement, and Masha\'allah\'s delineation for that [placed-in, rules] pairing -- the classical way of reading what a house\'s ruler is "doing" elsewhere in the chart.')
                st.dataframe(pd.DataFrame(house_lords_data), hide_index=True, width='stretch')

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
                        "12° east / 15° west, and 12° respectively; in the heart within 16' "
                        "(VII.2, 7-9, from the Sun's own apparent diameter). Sahl elsewhere says one whole "
                        "degree for the heart, and that reading is used where his own testimonies are "
                        "scored. **Domain/hayz** is VII.1, 37-39 and VII.6, 13: the planet's own sect need "
                        "not match the chart's -- the hemisphere requirement is what flips with it."
                    )


            with tab_connections:
                st.subheader(f"Aspects, Aversions & Connections (Sahl, The Introduction Ch.2 50-60 & Ch.3 6-21) — {CONNECTION_PROFILE} rule", help="Four separate facts about each pair, kept apart rather than collapsed into one verdict. LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign. MOTION and EXACT ORB DIST are the degree-to-degree approach. BODIES is whether each planet falls inside the other's sphere of power, which is asymmetric because the spheres differ in size: Abu Ma'shar VII.4, 7 notes that Saturn sits inside the Moon's body from 12 degrees while she only enters his at a little under 9. CONNECTED is the active author's verdict -- switch the Connection rule in the sidebar to see where they disagree.\n\nLIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.\n\nAPPLYING PLANET is the separate, directed fact: which one is actually closing the aspect. Normally it is the lighter, and Ch.3, 6 assumes as much (\"a light, quick star GOING STRAIGHTAWAY TO a heavy star ... FEWER IN DEGREES than the heavy one\"). Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma'shar VII.5, 24 (\"the connection of one of them with the other ... will be BY RETROGRADATION\"), VII.5, 120 (\"the light one IN MORE DEGREES goes retrograde and connects with the heavy one\"), and the note on VII.5, 130 (Saturn \"could never be received because he is too slow to connect with anyone, UNLESS BY RETROGRADATION\"). The cause is named in this column whenever the heavier planet is the one applying, which happens for about 4% of configured pairs. Reception, transfer, collection, returning, revoking, emptiness of course and enclosure all read this column, not the light/heavy one.")
                if aspects:
                    st.dataframe(pd.DataFrame(aspects), hide_index=True, width='stretch')
                else:
                    st.write("No traditional aspects or aversions found.")

                st.subheader("Transfer of Light (Sahl, The Introduction Ch.3, 24-27)", help='A faster "carrier" planet separates from one planet and connects with another, carrying the first planet\'s nature to the second -- Type I is a direct hand-off, Type II is via an intermediate planet already connecting onward.')
                if transfers:
                    st.dataframe(pd.DataFrame(transfers), hide_index=True, width='stretch')
                else:
                    st.write("No transfers of light found.")

                st.subheader("Collection of Light (Sahl, The Introduction Ch.3, 28-30)", help='Two planets not connected to each other both connect with a single heavier planet, which "collects" their combined power -- often read as a third party or authority resolving/mediating between two unconnected significators.')
                if collections:
                    st.dataframe(pd.DataFrame(collections), hide_index=True, width='stretch')
                else:
                    st.write("No collections of light found.")

                st.subheader("Reflection of Light (Abu Ma'shar, Great Introduction VII.5, 87-89)", help="Collection or Transfer specifically between two planets that are in Aversion to each other, not just unconnected -- since Aversion pairs can't see each other at all, a third planet is the only way their natures can interact.")
                if reflections:
                    st.dataframe(pd.DataFrame(reflections), hide_index=True, width='stretch')
                else:
                    st.write("No reflections of light found.")

                st.subheader("Candidate Blocking Patterns (Sahl, The Introduction Ch.3, 31-48: Intervention & Nullification; Abu Ma'shar VII.5, 90-94)", help='A third planet gets to the heavy planet first, so the connection heading there does not complete. INTERVENTION: three planets in one sign, the heavy one at the highest degree, and the middle one stands between the lightest and its target until it passes by. NULLIFICATION: one planet aspects a heavy planet from another sign while a lighter planet already in that sign is joining it by body -- and arrives first. Where the ray has less arc left to travel than the body does, the ray prevails instead and no blocking is reported (Ch.3, 40; VII.5, 94).\n\nCalled CANDIDATE patterns because both authors are describing horary charts with a querent and a quesited already nominated. With no topical significators chosen, a row says the pattern exists between those three planets -- not that a particular sought matter is obstructed.\n\nSahl\'s own third blocking type, "Cutting the Light," is Type III of the Cutting the Light table below rather than shown here.')
                if blocking_data:
                    st.dataframe(pd.DataFrame(blocking_data), hide_index=True, width='stretch')
                else:
                    st.write("No candidate blocking patterns found.")

                st.subheader("Enclosure (Sahl, The Introduction Ch.3, 119-123)", help='A planet separating from one of the two infortunes (or, per Abu Ma\'shar\'s extension, fortunes) and connecting with the other, with neither leg intercepted by a third planet\'s rays -- graded "more powerful/unfortunate" when both legs are within 7 degrees of exact.')
                if enclosure_data:
                    st.dataframe(pd.DataFrame(enclosure_data), hide_index=True, width='stretch')
                else:
                    st.write("No enclosure configurations found.")

                st.subheader("Handing Over (Sahl, The Introduction Ch.3, 70-76)", help='Three grades of one phenomenon, per connected pair: Management is the baseline (any connection at all); Power is added when the giving planet is itself in its own house, exaltation, or triplicity; Nature is added when the planet it connects with is the ruler -- by house or exaltation -- of its own position (i.e. in reception).')
                if handing_over_data:
                    st.dataframe(pd.DataFrame(handing_over_data), hide_index=True, width='stretch')
                else:
                    st.write("No handing-over configurations found.")

                st.subheader(f"Reception — {CONNECTION_PROFILE} rule", help="Who receives whom, on what dignity, which way round, and how strongly. The two authors differ on every one of those, so the active Connection rule in the sidebar governs here too.\n\nSAHL (Ch.3, 49-55) runs one way only -- the connecting planet stands in a dignity of the planet it connects with, and so is received by it (52: the Moon in Aries connecting with Mars, \"he receives her because Aries is his house\"). House or exaltation is perfect reception; triplicity alone is expressly ranked below it (50); bound counts only paired with triplicity, which Sahl credits to Masha'allah (54-55). Face never appears, and a connection is always required.\n\nABU MA'SHAR (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in REVERSE where the accepting planet sits in the connector's dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).\n\nAn empty table is NOT non-reception -- that is a separate set of hostile configurations, in the table below.")
                if reception_data:
                    st.dataframe(pd.DataFrame(reception_data), hide_index=True, width='stretch')
                else:
                    st.write("No receptions found.")

                st.subheader("Non-reception (Sahl, The Introduction Ch.3, 58-62)", help='Five named ways a connection is refused rather than received -- a distinct finding from simply lacking reception: (I) the connected-to planet holds no dignity claim at all in the connecting planet\'s sign; (II) the connecting planet is in the other\'s sign of fall; (III) the connecting planet is in its OWN fall, and Kind I also applies; (IV) the connected-to planet is in its OWN fall; (V) the connected-to planet sits in the connecting planet\'s own sign of fall.')
                if non_reception_data:
                    st.dataframe(pd.DataFrame(non_reception_data), hide_index=True, width='stretch')
                else:
                    st.write("No non-reception configurations found.")

                st.subheader("Cutting the Light (Sahl, The Introduction Ch.3, 31-34: Type III; Abu Ma'shar VII.5, 120-125: Types I-II)", help='Type III is Sahl\'s own Blocking #1: among several planets a given one is applying to, one contact wins and cuts off the others.\n\nWhich one wins is decided by Sahl\'s own PRECEDENCE, not by nearness alone: "a connection does not nullify a uniting, but a uniting does NULLIFY a connection, while an aspect does not cut an aspect, and a uniting cuts an aspect" (Ch.3, 44). The note there ranks the three kinds -- (1) a uniting, i.e. a conjunction by degree; (2) a connection by degree from another sign; (3) an aspect by sign only -- and adds that degree-based connections can cut each other while aspects by sign cannot. Nearness only breaks ties within a rank, and the BECAUSE column says which applied.\n\nSahl works it himself at 46-48 (Fig. 15): Moon 10 Taurus, Mars 20 Taurus, Venus 15 Cancer. "Her connection with Venus is PRIOR to her uniting with Mars, but the Moon is uniting [with Mars], and that is stronger than an aspect and a connection." The Venus sextile is 5 degrees from exact against the Mars union\'s 10, so nearness alone gives the opposite of Sahl\'s verdict; the precedence rule changes the winner for about 7% of planets holding two or more applying contacts.\n\nTypes I and II are Abu Ma\'shar\'s later addition, and each requires its own full sequence of dated events.\n\nTYPE I (121-22): a planet in the SECOND SIGN from the applicant stations retrograde, re-enters the applicant\'s sign, and conjoins it BY DEGREE -- all before the applicant reaches its original target. The note on 121 reads that last verb as conjoining by degree, "rather than the looser assembling."\n\nTYPE II (123-24): the planet being applied to reaches a heavier planet first and moves on, leaving the applicant to land on that heavier planet instead. "Mercury wants to connect with Venus. But before he can do that, she connects with Mars and then continues on. Then Mercury is left with the conjunction of Mars, which was not what he wanted."')
                if cutting_data:
                    st.dataframe(pd.DataFrame(cutting_data), hide_index=True, width='stretch')
                else:
                    st.write("No cutting-the-light configurations found.")

                st.subheader("Favor & Recompense (Abu Ma'shar VII.5, 126-128)", help='A planet in its own Fall or a welled/pitted degree, pulled out of that weak condition by a connecting dispositor (Favor). Recompense is the same planet later returning the favor, found by simulating the chart forward.')
                if favor_recompense_data:
                    st.dataframe(pd.DataFrame(favor_recompense_data), hide_index=True, width='stretch')
                else:
                    st.write("No favor/recompense configurations found.")

                st.subheader("Wildness (Sahl, The Introduction Ch.3, 64: \"Banished\"; Abu Ma'shar VII.5, 79-82)", help='A planet in Aversion to all six other classical planets -- unable to be seen or aspected by anyone, though it may still be "reached" via the lord of whatever bound (term) it occupies. Sahl\'s own term is "banished"; this Aversion-based definition is a later refinement of it.')
                if wildness_data:
                    st.dataframe(pd.DataFrame(wildness_data), hide_index=True, width='stretch')
                else:
                    st.write("No wild planets found.")

                st.subheader("Returning (Sahl, The Introduction Ch.3, 65-69)", help='Manner I: a planet connects with a retrograde planet or one under the rays -- it "returns to it what it accepted," corrupting the question. Manner II: an angular (faster) planet hands over to a cadent (slower) one -- the matter has a beginning but no end.')
                if returning_data:
                    st.dataframe(pd.DataFrame(returning_data), hide_index=True, width='stretch')
                else:
                    st.write("No returning configurations found.")

                st.subheader("Forward-Looking Conditions (Revoking, Resistance, Escape — next 200 days)", help="Conditions describing what happens as the chart moves forward in time (up to ~200 days), not the birth moment alone. Each chapter prescribes an ORDERED SEQUENCE of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when. A condition not found inside 200 days is reported as not found, never as a negative finding.\n\nREVOKING (117): \"a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it.\" The window is now birth to the applicant's first station: perfection inside it means nothing was revoked.\n\nRESISTANCE (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one BY RETROGRADATION, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead. All five steps are required and timed.\n\nESCAPE (119): the planet being applied to leaves its sign first; the applicant then follows across the SAME boundary on its own next crossing, and is captured by a body it meets in the new sign. Dykes' note on Fig. 139 is the picture: Mercury slips from Virgo into Libra, Venus follows, and Saturn's body catches her there.")
                if forward_looking_data:
                    st.dataframe(pd.DataFrame(forward_looking_data), hide_index=True, width='stretch')
                else:
                    st.write("No forward-looking conditions found within the simulation horizon.")

                st.subheader("Strength of the Planets (Sahl, The Introduction Ch.3, 78-88)", help="The eleven testimonies of a planet's strength at the time of judgment -- excellent place, own dignity, direct, out of the whole-sign angles of an infortune, not tied to a fallen or falling planet, advancing, an eastern masculine planet, in its own glow, a fixed sign, in the heart of the Sun, and a gender-matching quadrant and sign.\n\nTestimonies 78 and 83 look similar but are different measurements. 78 is whole-sign, narrowed to the six places that LOOK at the Ascendant. 83, advancing, is DYNAMIC -- read against the Alchabitius quadrant cusps, since the note on 83 says the word means \"dynamically angular or succeedent, i.e. by primary motion with respect to the angular axes, and not by whole sign.\" A planet leaving an angle is withdrawing even while its whole sign is still angular, so the two disagree for about a third of placements.\n\n83 also carries Sahl's FIVE-DEGREE RULE: \"the planet will not be falling from the stake unless it was 5 degrees distant from its rear -- I mean, if the stake was 10 degrees of Aries, then every planet which has less than 5 degrees between it and the stake is truly counted as being in the stake\" (Fifty Aphorisms #44, 88), which he states again in On Nativities Ch.1.22, 9. A planet a few degrees short of an angle is therefore angular, not cadent; the row says so when that is why it qualifies. It moves about 5% of placements, all of them cadent-to-angular. Both source statements are about the STAKES specifically, so the carryover is applied at the four angles only, not at all twelve cusps as later authors generalise it.\n\nDistinct from the Abu Ma'shar-based Planetary Condition table, which scores a broader, later scheme.")
                if strength_data:
                    st.dataframe(pd.DataFrame(strength_data), hide_index=True, width='stretch')
                else:
                    st.write("No strength testimonies found.")

                st.subheader("Weakness of the Planets (Sahl, The Introduction Ch.3, 91-100)", help="The ten testimonies of a planet's weakness at the time of judgment -- falling and averse to the Ascendant (i.e. the 6th or 12th), retrograde, under the rays, connecting with an infortune by assembly/square/opposition, enclosed between both infortunes, in its own fall, connecting with a falling planet or separating from a would-be receiver, alien (no house/exaltation/triplicity where it sits), with the Node and no latitude, or inverted (in detriment). Distinct from the Abu Ma'shar-based Planetary Condition table above, which scores a broader, later scheme.")
                if weakness_data:
                    st.dataframe(pd.DataFrame(weakness_data), hide_index=True, width='stretch')
                else:
                    st.write("No weakness testimonies found.")
    else:
        st.sidebar.error("Timezone boundary not found for coordinates.")
