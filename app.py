import swisseph as swe
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, time, timedelta
from itertools import combinations
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
            'speed_in_lon': res[3]
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
    svg.append(f'<text x="{cx}" y="{cy - 35}" text-anchor="middle" font-size="11" fill="#000000">{location_query}</text>')
    svg.append(f'<text x="{cx}" y="{cy - 20}" text-anchor="middle" font-size="10" fill="#000000">Lat: {lat:.4f}° | Lon: {lon:.4f}°</text>')
    svg.append(f'<text x="{cx}" y="{cy - 5}" text-anchor="middle" font-size="10" fill="#000000">{dt_local.strftime("%Y-%m-%d %H:%M")} [{tz_name}]</text>')
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

def evaluate_accidental_dignities(planetary_data, natal_houses, sect):
    """Accidental dignity scoring: house angularity (Whole Sign, anchored to
    the Ascendant, with the 6/8/12 malefic-house override), planetary joys,
    sect/hayz, motion & speed, and solar phasing (cazimi/combust/under the
    beams)."""
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

        is_hayz = False
        if planet_is_diurnal is not None:
            sect_match = (planet_is_diurnal == is_diurnal_chart)
            if planet_is_diurnal:
                horizon_ok = is_above_horizon
                gender_ok = current_sign in MASCULINE_SIGNS
            else:
                horizon_ok = not is_above_horizon
                gender_ok = current_sign in FEMININE_SIGNS
            is_hayz = sect_match and horizon_ok and gender_ok
        if is_hayz:
            score += 3
            labels.append("Hayz (+3)")

        # --- Motion & speed -------------------------------------------
        is_stationary = abs(speed) <= 0.003
        is_retrograde = speed < 0 and not is_stationary and planet not in ('Sun', 'Moon')
        avg_motion = AVERAGE_DAILY_MOTION.get(planet, 1.0)
        is_swift = (not is_stationary) and (not is_retrograde) and speed > avg_motion
        if is_stationary:
            score -= 2
            labels.append("Stationary (-2)")
        elif is_retrograde:
            score -= 5
            labels.append("Retrograde (-5)")
        elif is_swift:
            score += 2
            labels.append("Swift (+2)")

        # --- Solar phase: Cazimi / Combust / Under the Beams -----------
        is_cazimi = is_combust = is_under_beams = False
        if planet != 'Sun':
            dist = abs(lon - sun_lon)
            dist = dist if dist <= 180 else 360 - dist
            if dist <= (17 / 60):
                is_cazimi = True
                score += 5
                labels.append("Cazimi (+5)")
            elif dist <= 8.5:
                is_combust = True
                score -= 5
                labels.append("Combust (-5)")
            elif dist <= 15.0:
                is_under_beams = True
                score -= 2
                labels.append("Under Beams (-2)")

        results[planet] = {
            'Accidental Score': score, 'House': house_num, 'Joy': is_joy, 'Hayz': is_hayz,
            'Stationary': is_stationary, 'Retrograde': is_retrograde, 'Swift': is_swift,
            'Cazimi': is_cazimi, 'Combust': is_combust, 'UnderBeams': is_under_beams,
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
    by_fast = {}
    for row in rows:
        if row['aspect_name'] == 'Aversion':
            continue
        by_fast.setdefault(row['light_name'], []).append(row)

    applying_connected_to = {
        fast: {r['heavy_name'] for r in fast_rows if r['motion'] == 'Applying' and _is_connected(r)}
        for fast, fast_rows in by_fast.items()
    }

    transfers = []
    for carrier, carrier_rows in by_fast.items():
        separating_from = [r['heavy_name'] for r in carrier_rows if r['motion'] == 'Separating']
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
        if is_conn and row['motion'] == 'Applying':
            applying_to.setdefault(row['light_name'], set()).add(row['heavy_name'])

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

def _perfection_day(sim, p1, p2, target, before_day=None):
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
        fast, slow = r['light_name'], r['heavy_name']
        acc_slow = accidental[slow]

        if acc_slow['Retrograde'] or acc_slow['Combust'] or acc_slow['UnderBeams']:
            results.append({'Manner': 'I (65)', 'Planet': fast, 'Returned By': slow})

        fast_house = get_wsh_house(planetary_data[fast]['longitude'], ascendant_lon)
        slow_house = get_wsh_house(planetary_data[slow]['longitude'], ascendant_lon)
        if fast_house in ANGLE_HOUSES and slow_house in CADENT_HOUSES:
            results.append({'Manner': 'II (66-69)', 'Planet': fast, 'Returned By': slow})

    return results

def evaluate_revoking(planetary_data, sim):
    """Revoking (VII.5, 117, Fig. 137): a planet applying toward a
    connection stations retrograde before reaching it, nullifying the
    connection."""
    if sim is None:
        return []
    rows = _pairwise_configurations(planetary_data)
    results = []
    for r in rows:
        if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
            continue
        fast, slow = r['light_name'], r['heavy_name']
        first_station = next((s for s in sim['events'][fast]['stations'] if s[1] == 'first'), None)
        if not first_station:
            continue
        exact_day = _perfection_day(sim, fast, slow, r['target'])
        if exact_day is None or first_station[0] < exact_day:
            results.append({'Planet': fast, 'Was Connecting To': slow, 'Stations Retrograde In (days)': round(first_station[0], 1)})
    return results

def evaluate_resistance(planetary_data, sim):
    """Resistance (VII.5, 118, Fig. 138): a light planet applying to a
    heavier one stations retrograde first; a third, even lighter planet
    that also wanted the light one ends up connecting with it after its
    retrogradation, instead of the light one ever reaching the original
    heavy target."""
    if sim is None:
        return []
    rows = _pairwise_configurations(planetary_data)
    results = []
    for r in rows:
        if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
            continue
        light, heavy = r['light_name'], r['heavy_name']
        first_station = next((s for s in sim['events'][light]['stations'] if s[1] == 'first'), None)
        if not first_station:
            continue
        exact_with_heavy = _perfection_day(sim, light, heavy, r['target'])
        if exact_with_heavy is not None and first_station[0] >= exact_with_heavy:
            continue
        for r2 in rows:
            if light not in (r2['p1'], r2['p2']) or r2['aspect_name'] == 'Aversion':
                continue
            other = r2['p2'] if r2['p1'] == light else r2['p1']
            if other == heavy or WEIGHT_ORDER.index(other) <= WEIGHT_ORDER.index(light):
                continue
            exact_with_other = _perfection_day(sim, light, other, r2['target'])
            if exact_with_other is not None and exact_with_other > first_station[0]:
                results.append({'Light Planet': light, 'Originally Heading To': heavy, 'Resisted, Now Connects With': other})
    return results

def evaluate_escape(planetary_data, sim):
    """Escape (VII.5, 119, Fig. 139): the planet being applied to changes
    sign before the connection completes, and a different, now-closer
    planet captures the connection instead."""
    if sim is None:
        return []
    rows = _pairwise_configurations(planetary_data)
    results = []
    for r in rows:
        if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
            continue
        fast, slow = r['light_name'], r['heavy_name']
        sign_exits = sim['events'][slow]['sign_exits']
        if not sign_exits:
            continue
        exit_day = sign_exits[0]
        if _perfection_day(sim, fast, slow, r['target'], before_day=exit_day) is not None:
            continue
        # Whichever still-configured planet the escapee actually perfects
        # with FIRST after the target has slipped away takes the
        # connection. An earlier version instead picked whichever planet
        # merely had the smallest deviation at the moment of the sign exit,
        # which asserts a capture without any connection ever perfecting.
        best, best_day = None, None
        for other in planetary_data:
            if other in (fast, slow, 'North Node'):
                continue
            target_then = _configuration_target_at(sim, fast, other, exit_day)
            if target_then is None:
                continue
            day = _perfection_day(sim, fast, other, target_then)
            if day is None or day < exit_day:
                continue
            if best_day is None or day < best_day:
                best, best_day = other, day
        if best is not None:
            results.append({'Planet': fast, 'Escaped': slow, 'Connected Instead With': best,
                             'Perfects In (days)': round(best_day, 1)})
    return results

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
    heavy target."""
    rows = _pairwise_configurations(planetary_data)
    results = []

    by_fast = {}
    for r in rows:
        if r['aspect_name'] != 'Aversion':
            by_fast.setdefault(r['light_name'], []).append(r)
    for fast, candidates in by_fast.items():
        applying = sorted((r for r in candidates if r['motion'] == 'Applying'), key=lambda r: abs(r['deviation']))
        if len(applying) >= 2:
            nearest = applying[0]['heavy_name']
            for r in applying[1:]:
                results.append({'Type': 'III', 'Planet': fast, 'Cut Off From': r['heavy_name'], 'Connects With Instead': nearest})

    if sim is not None:
        for r in rows:
            if r['aspect_name'] == 'Aversion' or r['motion'] != 'Applying':
                continue
            light, heavy = r['light_name'], r['heavy_name']
            exact_day = _perfection_day(sim, light, heavy, r['target'])
            if exact_day is None:
                continue
            for candidate in planetary_data:
                if candidate in (light, heavy, 'North Node'):
                    continue
                for station_day, kind in sim['events'][candidate]['stations']:
                    if kind != 'first' or station_day >= exact_day:
                        continue
                    for exit_day in sim['events'][candidate]['sign_exits']:
                        # The light planet's sign is read AT the crossing,
                        # not at birth -- it may itself have moved on by then.
                        if station_day < exit_day < exact_day and int(_lon_at(sim, candidate, exit_day) // 30) == int(_lon_at(sim, light, exit_day) // 30):
                            results.append({'Type': 'I', 'Planet': light, 'Cut Off From': heavy, 'Cut By': candidate})
    return results

def _find_recompense_day(sim, helper, helped):
    """Best-effort forward scan for Recompense (VII.5, 127): the helper
    planet later enters its own Fall or a Well while the originally-helped
    planet is positioned to connect with it -- the reciprocal payback.
    Returns the day found, or None -- not found within the 200-day horizon
    isn't treated as a hard "no," just omitted from the table."""
    helper_fall_signs = FALLS.get(helper, [])
    days = sim['series'][helper]['day']
    lons_helper, lons_helped = sim['series'][helper]['lon'], sim['series'][helped]['lon']
    for day, lh, lp in zip(days, lons_helper, lons_helped):
        sign = get_zodiac_sign(lh)
        degree_1_based = int(lh % 30) + 1
        if not (degree_1_based in WELLED_DEGREES.get(sign, []) or sign in helper_fall_signs):
            continue
        raw = abs(lh - lp)
        dist = raw if raw <= 180.0 else 360.0 - raw
        sign_h, sign_p = int(lh // 30), int(lp // 30)
        apart = min(abs(sign_h - sign_p), 12 - abs(sign_h - sign_p))
        if apart in ASPECT_BY_SIGN_COUNT and abs(dist - ASPECT_BY_SIGN_COUNT[apart][1]) < 5.0:
            return day
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

def calculate_chronocrats(jd_utc, lat, lon, local_dt):
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
        true_day_dt = local_dt - timedelta(days=time_since_sunrise)
        day_lord = DAY_LORD_BY_WEEKDAY[true_day_dt.weekday()]

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
        day_lord = DAY_LORD_BY_WEEKDAY[local_dt.weekday()]
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
    """Flags planets in the Via Combusta (15 Libra-15 Scorpio) and/or a
    classical welled/pitted degree of their current sign."""
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
                         and r['light_name'] == planet and r['heavy_name'] == sep_target
                         and r['motion'] == 'Separating' and _is_connected(r)), None)
        con_row = next((r for r in rows if r['aspect_name'] != 'Aversion'
                         and r['light_name'] == planet and r['heavy_name'] == con_target
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

def evaluate_strength_of_planets(planetary_data, essential, accidental, ascendant_lon, sect):
    """Strength of the Planets (Sahl, The Introduction Ch.3, 78-88): the
    eleven testimonies of a planet's strength at the time of judgment that
    77 announces, cross-checked against the author's own summary table
    (Fig. 24). An earlier version found only ten, having misread 87 (the
    tenth, "in the heart of the Sun") and renumbered 88 (the eleventh, the
    gender-matching quadrant and sign) as the tenth; the count discrepancy
    against 77 was noted at the time but resolved the wrong way.

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

        # (83) Advancing -- a stake or what follows it (Sahl's own master
        # definition of "advancement," Ch.3, 4, reapplied here).
        if house in ANGLE_HOUSES | SUCCEDENT_HOUSES:
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
            if r['light_name'] == planet and r['motion'] == 'Separating' and _is_connected(r):
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
    fortune, strength, weakness, misfortune, and enclosure -- plus, for the
    Moon only, Sahl's own ten defects (The Introduction Ch.3, 102-113,
    via _corruption_of_the_moon_labels()) rather than VII.6's own,
    differently-numbered eleven-item version. Distinct from -- and now the
    authoritative source for -- the Rhetorius/PN4 net dignity score in
    evaluate_essential_dignities()/evaluate_accidental_dignities(), which
    is retained separately as the older Hellenistic reconstruction."""
    rows = _pairwise_configurations(planetary_data)
    connected_lookup = {}
    configured_lookup = {}  # frozenset -> aspect name, for non-Connected "look"/assembly checks
    for row in rows:
        pair = frozenset({row['p1'], row['p2']})
        is_conn = row['aspect_name'] != 'Aversion' and _is_connected(row)
        connected_lookup[pair] = is_conn
        configured_lookup[pair] = row['aspect_name']
    blocking_pairs = {(row['Blocked'], row['From Reaching']) for row in evaluate_blocking(planetary_data)}

    def connected_to(planet, targets):
        return any(connected_lookup.get(frozenset({planet, t}), False) for t in targets if t != planet)

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
        if connected_to(planet, FORTUNES):
            positive.append('Aspect/assembly with a fortune (2)')
        if averted_from(planet, INFORTUNES):
            positive.append('Infortunes averted (3)')
        separating_infortune = any(
            r['light_name'] == planet and r['heavy_name'] in INFORTUNES and r['motion'] == 'Separating' and _is_connected(r)
            for r in rows
        )
        if separating_infortune and connected_to(planet, FORTUNES):
            positive.append('Separating infortune, connecting fortune (4)')
        is_enc, severe, _sep, _con = _sahl_enclosed(planet, FORTUNES, rows, blocking_pairs)
        if is_enc:
            positive.append('Enclosed between two fortunes (5, 119-123)' + (', severe' if severe else ''))
        if acc['Cazimi']:
            positive.append('Cazimi (6)')
        if configured_to(planet, {'Sun'}, {'Trine', 'Sextile'}):
            positive.append('Trine/sextile the Sun (7)')
        if planet != 'Moon' and configured_to(planet, {'Moon'}, {'Trine', 'Sextile'}) and moon_corruption_count == 0:
            positive.append('Aspects the (uncorrupted) Moon (8)')
        if acc['Swift']:
            positive.append('Swift, increasing in light (9)')
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
        reception_dispositors = {rulers['domicile'], rulers['exaltation'], rulers[triplicity_key_local]} - {'-'}
        received_via = {
            d for d in reception_dispositors
            if connected_to(planet, {d}) or configured_lookup.get(frozenset({planet, d})) not in (None, 'Aversion')
        }
        received = bool(received_via)
        mutual_received = False
        for r in rows:
            if planet not in (r['p1'], r['p2']) or r['aspect_name'] == 'Aversion':
                continue
            other = r['p2'] if r['p1'] == planet else r['p1']
            other_rulers = get_essential_rulers(planetary_data[other]['longitude'])
            other_reception_dispositors = {other_rulers['domicile'], other_rulers['exaltation'], other_rulers[triplicity_key_local]} - {'-'}
            if planet in other_reception_dispositors:
                mutual_received = True
                break
        if received:
            perfect = rulers['domicile'] in received_via or rulers['exaltation'] in received_via
            grade_label = 'perfect' if perfect else 'lesser'
            positive.append(f'Received (12), {grade_label}')
        if mutual_received:
            positive.append('Receives a connecting planet into its own dignity (130)')
        if acc['Hayz']:
            positive.append('Domain/hayz (13)')
        if planet in ('Sun', 'Moon'):
            fortune_dispositors = _dispositors(lon, sect) & FORTUNES
            if fortune_dispositors:
                positive.append(f"Luminary in a fortune's share (14): {', '.join(sorted(fortune_dispositors))}")

        # Good-fortune grade (15-20): count of essential-dignity claims, plus
        # which of a non-luminary's two domiciles it occupies.
        claims = sum([ess['Domicile'], ess['Exalt'], ess['Triplicity'], ess['Term'], ess['Face']])
        if claims >= 2:
            grade = 'Doubled good fortune (16-18)'
        elif planet in PREFERRED_DOMICILE and ess['Domicile'] and sign != PREFERRED_DOMICILE[planet]:
            grade = 'Below that / suitable (20)'
        elif claims == 1:
            grade = 'Fortunate (19)'
        else:
            grade = None
        if grade:
            positive.append(grade)

        # --- Strength (VII.6, 21-29) --------------------------------------
        if lat > 0:
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
        if not acc['Combust'] and not acc['UnderBeams']:
            positive.append('Out of the rays (25)')
        stake_or_following = house in ANGLE_HOUSES | SUCCEDENT_HOUSES
        if stake_or_following:
            positive.append('Stake or following (26)')
        is_superior = planet in {'Saturn', 'Jupiter', 'Mars'}
        is_inferior = planet in {'Venus', 'Mercury'}
        sun_lon = planetary_data['Sun']['longitude']
        signed_from_sun = ((lon - sun_lon + 180.0) % 360.0) - 180.0
        is_eastern_of_sun = signed_from_sun < 0  # rises before the Sun
        if is_superior and is_eastern_of_sun:
            positive.append('Superior, eastern of the Sun (27)')
        in_masculine_quadrant = house in MASCULINE_QUADRANT_HOUSES
        if is_superior and in_masculine_quadrant:
            positive.append('Superior, in a masculine quadrant (28)')
        if is_inferior and not is_eastern_of_sun:
            positive.append('Inferior, western of the Sun (29)')
        if is_inferior and not in_masculine_quadrant:
            positive.append('Inferior, in a feminine quadrant (29)')

        # --- Weakness (VII.6, 30-46) --------------------------------------
        is_slow = 0 <= speed < AVERAGE_DAILY_MOTION.get(planet, 1.0)
        if is_slow:
            negative.append('Slow in course (31)')
        if station == 'first':
            negative.append('First station (32)')
        if acc['Retrograde']:
            negative.append('Retrograde (33)')
        if acc['Combust'] or acc['UnderBeams']:
            negative.append('Under the rays (34)')
        if brightness == 'Dark':
            negative.append('Dark degree (35)')
        elif brightness in ('Dusky', 'Empty'):
            negative.append(f'{brightness} degree, minor (35)')
        if not acc['Hayz']:
            negative.append('Wrong domain (36-37)')
        if ess['Fall']:
            negative.append('Sign of fall (37)')
        if lat < 0:
            negative.append('Southern latitude (38)')
        cadent_no_override = house in CADENT_HOUSES
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
        connects_debilitated = any(
            connected_lookup.get(frozenset({planet, other}), False)
            and (essential[other]['Fall'] or accidental[other]['Retrograde'] or get_wsh_house(planetary_data[other]['longitude'], ascendant_lon) in CADENT_HOUSES)
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
                (row['light_name'] == planet and row['motion'] == 'Applying' and _is_connected(row))
                for row in rows
            )
        if ess['Peregrine']:
            negative.append('Exile/peregrine, empty of course (44)' if empty_of_course else 'Exile/peregrine (44)')
        if is_superior and not is_eastern_of_sun:
            negative.append('Superior, western of the Sun (45)')
        if is_superior and not in_masculine_quadrant:
            negative.append('Superior, in a feminine quadrant (45)')
        if is_inferior and is_eastern_of_sun and abs(signed_from_sun) < 15.0:
            negative.append('Inferior, beginning of easternization (46)')
        if is_inferior and in_masculine_quadrant:
            negative.append('Inferior, in a masculine quadrant (46)')

        # --- Misfortune (VII.6, 47-55) ------------------------------------
        if connected_to(planet, INFORTUNES):
            negative.append('Connected to an infortune (47-48)')
        term_lord = get_essential_rulers(lon)['term']
        if SIGN_TO_DOMICILE.get(sign) in INFORTUNES or term_lord in INFORTUNES:
            negative.append('In the bound/house of an infortune (49)')
        for other in planetary_data:
            if other in (planet, 'North Node'):
                continue
            other_lon = planetary_data[other]['longitude']
            other_idx = int(other_lon // 30)
            forward = (other_idx - sign_idx) % 12 + 1
            if other in INFORTUNES and forward in (9, 10, 11) and not received:
                negative.append('Overcome by an infortune (50)')
                break
        if configured_to(planet, {'Sun'}, {'Conjunction', 'Square', 'Opposition'}):
            negative.append('Assembly/square/opposition to the Sun (51)')
        north_node_lon = planetary_data['North Node']['longitude']
        south_node_lon = (north_node_lon + 180.0) % 360.0
        node_dist = min(abs(((lon - north_node_lon + 180) % 360) - 180), abs(((lon - south_node_lon + 180) % 360) - 180))
        if node_dist <= 12.0:
            negative.append('With the Head or Tail (52-55)')

        # --- Enclosure by the infortunes (Sahl, The Introduction Ch.3,
        # 119-123; Abu Ma'shar VII.6, 56-62 reuses the same concept) -------
        is_enc, severe, _sep, _con = _sahl_enclosed(planet, INFORTUNES, rows, blocking_pairs)
        if is_enc:
            negative.append('Enclosed by infortunes (56-62, 119-123)' + (', severe' if severe else ''))

        # --- Corruption of the Moon (VII.6, 63-74), Moon only -------------
        if planet == 'Moon':
            for label in _corruption_of_the_moon_labels(planetary_data, ascendant_lon, sect):
                negative.append(label)

        positive_count = len(positive)
        negative_count = len(negative)
        results[planet] = {
            'Positive Score': positive_count,
            'Negative Score': negative_count,
            'Net': positive_count - negative_count,
            'Condition': 'Good' if positive_count - negative_count >= 0 else 'Bad',
            'Positive Labels': positive,
            'Negative Labels': negative,
        }
    return results

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
    if not any(row['light_name'] == 'Moon' and row['motion'] == 'Applying' and _is_connected(row) for row in rows):
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

def evaluate_victors(planetary_data, ascendant_lon, lot_of_fortune, sect, chronocrats):
    """Victor (Almuten) of a significant point, per ibn Ezra's tables
    (1485/1537) -- for each of the Ascendant, Sun, Moon, and Lot of
    Fortune, scores every planet's essential-dignity claim AT THAT POINT'S
    degree (not the planet's own position) under both weighting traditions,
    plus each tradition's own Lord of the Day (+7), Lord of the Hour (+6),
    and Places (VICTOR_PLACES_VALUES, keyed by the CANDIDATE planet's own
    Whole-Sign-House placement, not the point's) bonuses, and reports
    whichever planet scores highest as that point's victor. This is a
    different question from the Planetary Dignity Evaluation table (a
    planet's OWN condition) or the Prenatal Syzygy's Almuten (a fifth
    point, already computed separately) -- it's the classical technique of
    finding the ruling planet OVER a specific place or degree, not a
    single whole-chart "victor." Masha'allah's Places wheel had four
    wedges (the succedent houses) with two competing values attributed to
    Masha'allah vs. Dorotheus; the Masha'allah value is used for each,
    matching the "Older (al-Tabari/Masha'allah)" scheme it's paired with."""
    triplicity_key = 'triplicity_day' if sect == 'Diurnal' else 'triplicity_night'
    points = {
        'Ascendant': ascendant_lon,
        'Sun': planetary_data['Sun']['longitude'],
        'Moon': planetary_data['Moon']['longitude'],
        'Lot of Fortune': lot_of_fortune,
    }
    day_lord = chronocrats.get('Day Lord')
    hour_lord = chronocrats.get('Hour Lord')

    results = []
    for point_name, lon in points.items():
        rulers = get_essential_rulers(lon)
        row = {'Point': point_name}
        for scheme_name, weights in VICTOR_WEIGHTS.items():
            places_values = VICTOR_PLACES_VALUES[scheme_name]
            places_bonus = {
                p: places_values[get_wsh_house(data['longitude'], ascendant_lon)]
                for p, data in planetary_data.items() if p != 'North Node'
            }
            scores = {}
            def add(planet, pts):
                if planet and planet != '-':
                    scores[planet] = scores.get(planet, 0) + pts
            add(rulers['domicile'], weights['domicile'])
            add(rulers['exaltation'], weights['exaltation'])
            add(rulers[triplicity_key], weights['triplicity'])
            add(rulers['term'], weights['term'])
            add(rulers['face'], weights['face'])
            add(day_lord, 7)
            add(hour_lord, 6)
            for planet, bonus in places_bonus.items():
                add(planet, bonus)
            victor = max(scores, key=scores.get) if scores else '-'
            row[scheme_name] = f"{victor} ({scores.get(victor, 0)})"
        results.append(row)
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
            'Net Score': condition_data['Net'],
            'Condition': condition,
            'Classical Signification': delineation,
        })
    return results

# --- Chronocrator Matrix (Time Lords): Profections & Distributions -------

def calculate_time_lords(ascendant_lon, birth_date, target_date):
    """Annual Profection (Lord of the Year) and a simple Ptolemaic
    Distribution (1 degree = 1 year, Egyptian-term ruler of the directed
    Ascendant) for the given target date."""
    days_alive = (target_date - birth_date).days
    fractional_age = days_alive / 365.2425
    integer_age = int(fractional_age)

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
            'Technique': 'Distribution (Ptolemaic)',
            'Active Point': f"{get_degree_string(directed_asc_lon)}",
            'Active Ruler': distributor,
            'Details': "Egyptian Term (1\u00b0 / Year)",
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
        st.sidebar.info(f"**Time standard:** Exact LMT\n**UTC offset:** {offset_str}")
    else:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        if tz_name:
            local_tz = pytz.timezone(tz_name)
            localized_dt = local_tz.localize(local_dt)
            dt_utc = localized_dt.astimezone(pytz.utc)
            st.sidebar.info(f"**Timezone:** {tz_name}\n**UTC offset:** {dt_utc.strftime('%H:%M:%S')} UTC")

    if tz_name:
        chart_data = calculate_traditional_chart(dt_utc, lat, lon)
        p_data = chart_data['planetary_data']
        sect = chart_data['sect']

        essential = evaluate_essential_dignities(p_data, sect)
        accidental = evaluate_accidental_dignities(p_data, chart_data['houses'], sect)
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
        non_reception_data = evaluate_non_reception(p_data, sect)
        strength_data = evaluate_strength_of_planets(p_data, essential, accidental, chart_data['ascendant'], sect)
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
        chronocrats = calculate_chronocrats(chart_data['julian_day'], lat, lon, local_dt)
        classical_lots = calculate_classical_lots(chart_data['ascendant'], p_data['Sun']['longitude'], p_data['Moon']['longitude'], sect)
        special_degrees = evaluate_special_degrees(p_data)
        house_lords_data = evaluate_house_lords(p_data, chart_data['ascendant'])
        victors_data = evaluate_victors(p_data, chart_data['ascendant'], chart_data['lot_of_fortune'], sect, chronocrats)
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
                st.subheader("Planetary Condition (Abu Ma'shar)", help="Each planet's overall condition per the Great Introduction VII.6: good fortune, strength, weakness, misfortune, and enclosure -- plus (Moon only) Sahl's own ten defects of the Moon (The Introduction Ch.3, 102-113, numbered 103-112 below rather than VII.6's paragraph numbers) -- each criterion checked and summed into a single Good/Bad verdict, used to select the delineation in Topical Planets in Houses below.")
                condition_list = []
                for p, cond in abu_mashar_condition.items():
                    condition_list.append({
                        "Planet": p,
                        "Net": cond['Net'],
                        "Condition": cond['Condition'],
                        "Good Fortune / Strength": ", ".join(cond['Positive Labels']) if cond['Positive Labels'] else "-",
                        "Weakness / Misfortune": ", ".join(cond['Negative Labels']) if cond['Negative Labels'] else "-",
                    })
                df_condition = pd.DataFrame(condition_list).sort_values(by="Net", ascending=False)
                st.dataframe(df_condition, hide_index=True, width='stretch')

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

                    st.subheader("Special Degrees & Conditions", help='Flags planets in the Via Combusta (15 Libra-15 Scorpio, a historically "burnt" span) or a classical welled/pitted degree of their current sign (Abu Ma\'shar, Great Introduction V.21).')
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

                    st.subheader("Victors of Significant Points (ibn Ezra)", help='The Victor (Almuten) of the Ascendant, Sun, Moon, and Lot of Fortune -- whichever planet holds the strongest essential-dignity claim, day/hour lordship, and house-position bonus at each point, under two parallel medieval weighting traditions.')
                    st.dataframe(pd.DataFrame(victors_data), hide_index=True, width='stretch')
                    st.caption(
                        "Scored under both weighted essential-dignity traditions Dykes gives (Older: al-Tabari/"
                        "Masha'allah, Bound > Triplicity; Newer: Al-Qabisi/Abu Ma'shar, Triplicity > Bound), each with "
                        "its own Lord of the Day (+7), Lord of the Hour (+6), and Places (house-position) bonus wheel."
                    )

                st.subheader("Topical Planets in Houses (Rhetorius & PN4)", help="Each planet's Whole-Sign house placement and its Rhetorius/PN4-derived delineation, selected by that planet's Good/Bad verdict from the Planetary Condition table above.")
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


            with tab_connections:
                st.subheader(f"Aspects, Aversions & Connections (Sahl, The Introduction Ch.2 50-60 & Ch.3 6-21) — {CONNECTION_PROFILE} rule", help="Four separate facts about each pair, kept apart rather than collapsed into one verdict. LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign. MOTION and EXACT ORB DIST are the degree-to-degree approach. BODIES is whether each planet falls inside the other's sphere of power, which is asymmetric because the spheres differ in size: Abu Ma'shar VII.4, 7 notes that Saturn sits inside the Moon's body from 12 degrees while she only enters his at a little under 9. CONNECTED is the active author's verdict -- switch the Connection rule in the sidebar to see where they disagree.\n\nLIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: the light planet gives and the heavy one accepts (Ch.3, 67), and the light planet's own light measures the connection (19). A planet slowing toward its station does not thereby become heavy.")
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

                st.subheader("Non-reception (Sahl, The Introduction Ch.3, 58-62)", help='Five named ways a connection is refused rather than received: (I) the connected-to planet holds no dignity claim at all in the connecting planet\'s sign; (II) the connecting planet is in the other\'s sign of fall; (III) the connecting planet is in its OWN fall, and Kind I also applies; (IV) the connected-to planet is in its OWN fall; (V) the connected-to planet sits in the connecting planet\'s own sign of fall.')
                if non_reception_data:
                    st.dataframe(pd.DataFrame(non_reception_data), hide_index=True, width='stretch')
                else:
                    st.write("No non-reception configurations found.")

                st.subheader("Cutting the Light (Sahl, The Introduction Ch.3, 31-34: Type III; Abu Ma'shar VII.5, 120-125: Types I-II)", help='Type III is Sahl\'s own Blocking #1: among several planets a given one is applying to, it connects with whichever is nearest by degree first, cutting off the more distant, originally-favored connection. Types I-II are Abu Ma\'shar\'s later addition: an intervening planet -- by retrograding into the path -- intercepts an applying connection before it reaches its original target.')
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

                st.subheader("Forward-Looking Conditions (Revoking, Resistance, Escape — next 200 days)", help="Conditions describing what happens as the chart moves forward in time (up to ~200 days), not the birth moment alone. Revoking: a planet applying toward a connection stations retrograde before reaching it, nullifying it. Resistance: a light planet stations retrograde before reaching its heavier target, and a third, even lighter planet ends up connecting with it after that instead. Escape: the planet being applied to changes sign before the connection completes, and a different, now-closer planet captures it instead.")
                if forward_looking_data:
                    st.dataframe(pd.DataFrame(forward_looking_data), hide_index=True, width='stretch')
                else:
                    st.write("No forward-looking conditions found within the simulation horizon.")

                st.subheader("Strength of the Planets (Sahl, The Introduction Ch.3, 78-88)", help="The eleven testimonies of a planet's strength at the time of judgment -- excellent place, own dignity, direct, out of the whole-sign angles of an infortune, not tied to a fallen or falling planet, advancing, an eastern masculine planet, in its own glow, a fixed sign, in the heart of the Sun, and a gender-matching quadrant and sign. Distinct from the Abu Ma'shar-based Planetary Condition table above, which scores a broader, later scheme.")
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
