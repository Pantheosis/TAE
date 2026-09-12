"""Every base lookup table in the engine half, pinned cell by cell against a
literal copy of its canonical authority (2026-09-08 audit, docs/synthesis/08).

The Egyptian bounds carried two transposed rows from the initial commit
through three audits and 748 tests, because no test compared the table to
its source -- only the code's own reading of it. These tests are the
missing comparison: each literal below was transcribed from the authority
named in its comment, not from app.py, and is compared entry by entry, so
a transposition anywhere in a table fails on the cell it is in.

Authorities, in the order the audit prefers: the corpus (Sahl and Abu
Ma'shar in consolidated_texts/), then the TNAC Handy Tables from Part 1
(Dykes 2023), then a stated convention. Tables with NO authority in either
are not pinned here; they are listed in docs/synthesis/08_base_table_audit.md.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

# The corpus is only on the owner's machine; the re-derivation tests below
# skip without it (same convention as test_abu_mashar_citations.py).
CORPUS_DIR = Path(os.environ.get(
    "CORPUS_DIR", Path.home() / "Desktop" / "Fifty Aphorism OCR Project" / "consolidated_texts"))
BOOK_VII = CORPUS_DIR / "abu_mashar_book_vii.md"

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANETS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']


# --- Dignities: Handy Tables p. 1, "Houses (inner), Exaltations (outer)" ---
# Corpus witnesses for the exaltation degrees: Abu Ma'shar VII.6, 40 "from
# 19 Libra up to 3 Scorpio, because those are the fall of the luminaries";
# Questions Ch. 1, 42 "3 of Scorpio (which is her fall)".
DOMICILES = {'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mercury': ['Gemini', 'Virgo'], 'Venus': ['Taurus', 'Libra'],
             'Mars': ['Aries', 'Scorpio'], 'Jupiter': ['Sagittarius', 'Pisces'], 'Saturn': ['Capricorn', 'Aquarius']}
EXALTATIONS = {'Sun': ['Aries'], 'Moon': ['Taurus'], 'Mercury': ['Virgo'], 'Venus': ['Pisces'],
               'Mars': ['Capricorn'], 'Jupiter': ['Cancer'], 'Saturn': ['Libra']}
# Handy p. 1 "Standard exaltations" column (the Hermes column differs by a degree for five planets).
EXALTATION_DEGREES_STANDARD = {'Saturn': ('Libra', 21), 'Jupiter': ('Cancer', 15), 'Mars': ('Capricorn', 28),
                               'Sun': ('Aries', 19), 'Venus': ('Pisces', 27), 'Mercury': ('Virgo', 15), 'Moon': ('Taurus', 3)}


def _opposite(sign):
    return SIGNS[(SIGNS.index(sign) + 6) % 12]


@pytest.mark.parametrize("planet", PLANETS)
def test_domicile_exaltation_detriment_fall_match_handy_p1(engine, planet):
    assert engine["DOMICILES"][planet] == DOMICILES[planet]
    assert engine["EXALTATIONS"][planet] == EXALTATIONS[planet]
    assert engine["DETRIMENTS"][planet] == [_opposite(s) for s in DOMICILES[planet]]
    assert engine["FALLS"][planet] == [_opposite(s) for s in EXALTATIONS[planet]]


def test_the_engine_uses_the_standard_exaltation_degrees_of_the_luminaries(engine):
    # The only exaltation degrees the engine uses are the sect light's, in
    # the Lot of Exaltation (On Nativities 4.1, 6): Sun 19 Aries, Moon 3 Taurus.
    assert engine["_lot_point"]("exaltation_degree", {}, 0.0, [], "Diurnal", {}) == 19.0
    assert engine["_lot_point"]("exaltation_degree", {}, 0.0, [], "Nocturnal", {}) == 30.0 + 3.0


# --- Triplicities: Sahl, Introduction Ch. 1, 35-41 and Figure 4; Handy p. 1 ---
TRIPLICITY = {'Fire': {'Day': 'Sun', 'Night': 'Jupiter', 'Participating': 'Saturn'},
              'Earth': {'Day': 'Venus', 'Night': 'Moon', 'Participating': 'Mars'},
              'Air': {'Day': 'Saturn', 'Night': 'Mercury', 'Participating': 'Jupiter'},
              'Water': {'Day': 'Venus', 'Night': 'Mars', 'Participating': 'Moon'}}
SIGN_ELEMENT = {'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire', 'Taurus': 'Earth', 'Virgo': 'Earth',
                'Capricorn': 'Earth', 'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
                'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'}


@pytest.mark.parametrize("element", list(TRIPLICITY))
def test_triplicity_lords_match_sahl_figure_4(engine, element):
    assert engine["TRIPLICITY"][element] == TRIPLICITY[element]


def test_sign_elements_match_introduction_ch1_14_17(engine):
    assert engine["SIGN_ELEMENT"] == SIGN_ELEMENT


# --- Faces: Gr. Intr. V.15, 1-7, Figure 54 (Aries from Mars, then down the spheres) ---
# Standard sequence from Aries 0: Mars, Sun, Venus, Mercury, Moon, Saturn,
# Jupiter, repeating. Derived in app.py from CHALDEAN_ORDER; pinned as the
# 36 lords it must produce so the derivation cannot drift.
CHALDEAN_FACES = ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter'] * 6


@pytest.mark.parametrize("index", range(36))
def test_face_lords_follow_the_chaldean_order_from_aries(engine, index):
    assert engine["get_essential_rulers"](index * 10 + 5.0)["face"] == CHALDEAN_FACES[index]


def test_chaldean_order_literal(engine):
    assert engine["CHALDEAN_ORDER"] == ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter']


# --- Degrees of brightness: Abu Ma'shar Figure 61 (V.20), corpus, verified
# cell by cell against the p. 306 photograph in the OCR pass. Ranges are
# 0-based degree-in-sign, inclusive; each width in the figure's code (e.g.
# "3K") equals end - start + 1.
BRIGHTNESS_FIG61 = {
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


@pytest.mark.parametrize("sign", SIGNS)
def test_brightness_degrees_match_figure_61_sign_by_sign(engine, sign):
    assert [tuple(t) for t in engine["BRIGHTNESS_DEGREES"][sign]] == BRIGHTNESS_FIG61[sign], sign
    spans = BRIGHTNESS_FIG61[sign]
    assert spans[0][0] == 0 and spans[-1][1] == 29
    assert all(spans[i + 1][0] == spans[i][1] + 1 for i in range(len(spans) - 1)), "gap or overlap"


# --- Wells: Abu Ma'shar Figure 62 (V.21), corpus, p. 308 of Abu Ma'shar's
# own volume (Great Introduction Book V, pp. 303-310, captured 2026-09-08).
# Ordinal degrees as the figure prints them ("the 6th, 11th, 17th ..."),
# which is what app.py tests with int(lon % 30) + 1. Until this pin the
# table was cited to Figure 98 (which is "Speed relative to apogee") and
# held three defects -- Aries lacked 29, Gemini had 13 for 12, Pisces
# lacked 28 -- that no test could see because nothing compared it to a
# source. Transcribed from the corpus table, not from app.py, and then
# verified cell by cell (62 cells) against the p. 308 photograph.
WELLS_FIG62 = {
    'Aries':       [6, 11, 17, 23, 29],
    'Taurus':      [5, 13, 18, 24, 25, 26],
    'Gemini':      [2, 12, 17, 26, 30],
    'Cancer':      [12, 17, 23, 26, 30],
    'Leo':         [6, 13, 15, 22, 23, 28],
    'Virgo':       [8, 13, 16, 21, 25],
    'Libra':       [1, 7, 20, 30],
    'Scorpio':     [9, 10, 17, 22, 23, 27],
    'Sagittarius': [7, 12, 15, 24, 27, 30],
    'Capricorn':   [2, 7, 17, 22, 24, 28],
    'Aquarius':    [1, 12, 17, 23, 29],
    'Pisces':      [4, 9, 24, 27, 28],
}

GLYPH_TO_SIGN = dict(zip('♈♉♊♋♌♍♎♏♐♑♒♓', SIGNS))


@pytest.mark.parametrize("sign", SIGNS)
def test_wells_match_figure_62_sign_by_sign(engine, sign):
    assert list(engine["WELLED_DEGREES"][sign]) == WELLS_FIG62[sign], sign


def test_wells_table_has_exactly_the_twelve_signs_in_ordinal_form(engine):
    table = engine["WELLED_DEGREES"]
    assert set(table) == set(SIGNS)
    for sign, degrees in table.items():
        assert degrees == sorted(set(degrees)), sign
        assert all(1 <= d <= 30 for d in degrees), sign


def parse_figure_62(text):
    """Figure 62 as the corpus prints it: a two-sided table of Sign |
    Ordinal | Cardinal, continuation rows carrying an empty sign cell.
    The ordinal and cardinal columns are cross-checked ("12th" must sit
    beside "11°-11°59'"), so a row whose two columns disagree fails here
    rather than being read one way or the other."""
    lines = text.splitlines()
    end = next(i for i, l in enumerate(lines) if l.startswith("Figure 62 (Gr. Intr.)"))
    start = max(i for i in range(end) if lines[i].startswith("| Sign | Ordinal | Cardinal | Sign"))
    table, current = {}, [None, None]
    for line in lines[start + 2:end]:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        assert len(cells) == 6, cells
        for side in (0, 1):
            sign, ordinal, cardinal = cells[3 * side:3 * side + 3]
            if sign:
                current[side] = GLYPH_TO_SIGN[sign]
                table.setdefault(current[side], [])
            if not ordinal:
                continue
            n = int(re.match(r"(\d+)", ordinal).group(1))
            lo, hi = re.match(r"0?(\d+)°-0?(\d+)°59'", cardinal).groups()
            assert int(lo) == int(hi) == n - 1, (current[side], ordinal, cardinal)
            table[current[side]].append(n)
    return table


@pytest.mark.skipif(not BOOK_VII.is_file(), reason="corpus not on this machine (CI): "
                    "the vendored WELLS_FIG62 literal is what the pin above uses")
def test_wells_literal_matches_the_corpus_figure_62():
    assert parse_figure_62(BOOK_VII.read_text()) == WELLS_FIG62


# --- Abu Ma'shar Figures 63 and 64 (V.22), corpus, p. 309, captured
# 2026-09-08. Ordinal degrees, as the figures print them; Figure 64's
# three ranged entries (Cancer 1st-3rd and 14th-15th, Capricorn 12th-14th,
# Aquarius 16th-17th) are expanded. Display-only tables (D-20, D-21).
GOOD_FORTUNE_FIG63 = {'Taurus': [15, 27, 30], 'Leo': [3, 5], 'Scorpio': [7], 'Aquarius': [20]}
ELEVATION_FIG64 = {
    'Aries': [19], 'Taurus': [3], 'Gemini': [11], 'Cancer': [1, 2, 3, 14, 15],
    'Leo': [5, 7, 17], 'Virgo': [2, 12, 20], 'Libra': [3, 5, 21], 'Scorpio': [12, 20],
    'Sagittarius': [13, 20], 'Capricorn': [12, 13, 14, 20], 'Aquarius': [7, 16, 17, 20], 'Pisces': [12, 20],
}


def test_good_fortune_degrees_match_figure_63(engine):
    assert engine["GOOD_FORTUNE_DEGREES"] == GOOD_FORTUNE_FIG63
    assert sum(len(v) for v in GOOD_FORTUNE_FIG63.values()) == 7


@pytest.mark.parametrize("sign", SIGNS)
def test_elevation_degrees_match_figure_64_sign_by_sign(engine, sign):
    assert list(engine["ELEVATION_DEGREES"][sign]) == ELEVATION_FIG64[sign], sign


def test_elevation_degrees_have_thirty_one_entries_and_the_two_collisions_the_text_leaves(engine):
    assert sum(len(v) for v in ELEVATION_FIG64.values()) == 31
    both = {(s, d) for s, ds in GOOD_FORTUNE_FIG63.items() for d in ds} & {(s, d) for s, ds in ELEVATION_FIG64.items() for d in ds}
    assert both == {("Leo", 5), ("Aquarius", 20)}
    assert 17 in engine["WELLED_DEGREES"]["Aquarius"] and 17 in ELEVATION_FIG64["Aquarius"]


def _ordinal_table(text, caption_prefix, header_prefix, sides):
    """A Sign | Ordinal | Cardinal table (one- or two-sided) as the corpus
    prints it, ordinal cross-checked against cardinal, ranges expanded."""
    lines = text.splitlines()
    end = next(i for i, l in enumerate(lines) if l.startswith(caption_prefix))
    start = max(i for i in range(end) if lines[i].startswith(header_prefix))
    table, current = {}, [None] * sides
    for line in lines[start + 2:end]:
        if not line.startswith("|") or re.match(r"^\|[-\s|]+$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        for side in range(sides):
            sign, ordinal, cardinal = cells[3 * side:3 * side + 3]
            if sign:
                current[side] = GLYPH_TO_SIGN[sign]
                table.setdefault(current[side], [])
            if not ordinal:
                continue
            n1, n2 = re.match(r"(\d+)\w{2}(?:-(\d+)\w{2})?", ordinal).groups()
            n1 = int(n1); n2 = int(n2) if n2 else n1
            lo, hi = map(int, re.match(r"0?(\d+)°-0?(\d+)°59'", cardinal).groups())
            assert (lo, hi) == (n1 - 1, n2 - 1), (current[side], ordinal, cardinal)
            table[current[side]].extend(range(n1, n2 + 1))
    return table


@pytest.mark.skipif(not BOOK_VII.is_file(), reason="corpus not on this machine (CI)")
def test_v22_literals_match_the_corpus_figures_63_and_64():
    text = BOOK_VII.read_text()
    assert _ordinal_table(text, "Figure 63 (Gr. Intr.)", "| Sign | Ordinal | Increasing", 1) == GOOD_FORTUNE_FIG63
    assert _ordinal_table(text, "Figure 64 (Gr. Intr.)", "| Sign | Ordinal | Cardinal | Sign", 2) == ELEVATION_FIG64


# --- Planetary years: Abu Ma'shar Figure 146 (VII.8), corpus, p. 487 ---
# Display only (D-3). The literal is checked against the corpus table and
# against the text's own checksum: the fardars total 75 years (VII.8, 3).
PLANETARY_YEARS_FIG146 = {
    'Saturn':  (11, 30, 43.5, 57, 265),
    'Jupiter': (12, 12, 45.5, 79, 427),
    'Mars':    (7, 15, 40.5, 66, 284),
    'Sun':     (10, 19, 39.5, 120, 1461),
    'Venus':   (8, 8, 45, 82, 1151),
    'Mercury': (13, 20, 48, 76, 480),
    'Moon':    (9, 25, 39.5, 108, 520),
}


@pytest.mark.parametrize("planet", PLANETS)
def test_planetary_years_match_figure_146(engine, planet):
    y = engine["PLANETARY_YEARS"][planet]
    assert (y['fardar'], y['lesser'], y['middle'], y['greater'], y['mighty']) == PLANETARY_YEARS_FIG146[planet], planet


def test_fardars_total_the_75_years_the_text_gives(engine):
    total = sum(v['fardar'] for v in engine["PLANETARY_YEARS"].values()) + sum(engine["NODE_FARDAR_YEARS"].values())
    assert total == 75 and engine["NODE_FARDAR_YEARS"] == {'Head': 3, 'Tail': 2}


@pytest.mark.skipif(not BOOK_VII.is_file(), reason="corpus not on this machine (CI)")
def test_planetary_years_literal_matches_the_corpus_figure_146():
    lines = BOOK_VII.read_text().splitlines()
    end = next(i for i, l in enumerate(lines) if l.startswith("**Figure 146 (Gr. Intr.)"))
    start = max(i for i in range(end) if lines[i].startswith("|      | *Fard"))
    glyph = dict(zip('♄♃♂☉♀☿☽', ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']))
    got, nodes = {}, {}
    for l in lines[start + 2:end]:
        if not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        def num(x):
            return float(x.replace(" 1/2", ".5")) if x else None
        if cells[0] in glyph:
            got[glyph[cells[0]]] = tuple(num(c) for c in cells[1:6])
        elif cells[0] in ("Head", "Tail"):
            nodes[cells[0]] = int(cells[1])
    assert got == PLANETARY_YEARS_FIG146 and nodes == {'Head': 3, 'Tail': 2}


# --- Joys, genders, quadruplicity, places: Sahl's Introduction ---
def test_joys_match_introduction_ch3_128(engine):
    # "Mercury rejoices in the Ascendant, the Moon rejoices in the third,
    # Venus rejoices in the fifth, Mars rejoices in the sixth, the Sun
    # rejoices in the ninth, Jupiter rejoices in the eleventh, and Saturn
    # rejoices in the twelfth."
    assert engine["JOY_HOUSES"] == {'Mercury': 1, 'Moon': 3, 'Venus': 5, 'Mars': 6, 'Sun': 9, 'Jupiter': 11, 'Saturn': 12}


def test_sign_genders_alternate_from_aries_introduction_ch1_2_3(engine):
    assert engine["MASCULINE_SIGNS"] == set(SIGNS[0::2])
    assert engine["FEMININE_SIGNS"] == set(SIGNS[1::2])


def test_fixed_signs_introduction_ch1_9(engine):
    assert engine["FIXED_SIGNS"] == {'Taurus', 'Leo', 'Scorpio', 'Aquarius'}


def test_excellent_places_are_the_six_of_introduction_ch3_78(engine):
    # "in the stakes or what follows them, of the places which look at the
    # Ascendant"; fn. 92: "allows only six good places, by leaving out the
    # ninth". The 2nd and 8th follow a stake but are in aversion.
    assert engine["EXCELLENT_PLACES"] == {1, 4, 5, 7, 10, 11}


def test_malefic_houses_introduction_ch2_46_47(engine):
    # 8th "intense misfortune"; 6th and 12th "the most bad of the places".
    assert engine["MALEFIC_HOUSES"] == {6, 8, 12}


def test_preferred_domiciles_introduction_ch3_129(engine):
    assert engine["PREFERRED_DOMICILE"] == {'Saturn': 'Aquarius', 'Jupiter': 'Sagittarius', 'Mars': 'Scorpio',
                                            'Venus': 'Taurus', 'Mercury': 'Virgo'}


def test_sect_of_the_planets(engine):
    assert engine["DIURNAL_SECT_PLANETS"] == {'Sun', 'Jupiter', 'Saturn'}
    assert engine["NOCTURNAL_SECT_PLANETS"] == {'Moon', 'Venus', 'Mars'}


# --- Bodies and weights ---
def test_planetary_orbs_match_sahl_ch3_13_17_and_handy_p28(engine):
    # "the body of the Sun is 30 ... 15 ... the light of the Moon is 12 ...
    # Saturn and Jupiter (each one) is 9 ... Mars is 8 ... Venus and Mercury
    # (each one of them) is 7".
    assert engine["PLANETARY_ORBS"] == {'Sun': 15.0, 'Moon': 12.0, 'Saturn': 9.0, 'Jupiter': 9.0,
                                        'Mars': 8.0, 'Venus': 7.0, 'Mercury': 7.0}


def test_weight_order_is_the_chaldean_order_heaviest_first(engine):
    assert engine["WEIGHT_ORDER"] == PLANETS


# Handy p. 2 "Average daily speeds", in degrees/minutes/seconds.
AVERAGE_DAILY_SPEED_HANDY = {'Saturn': (0, 2, 1), 'Jupiter': (0, 4, 59), 'Mars': (0, 31, 27), 'Sun': (0, 59, 8),
                             'Venus': (1, 12, 0), 'Mercury': (1, 23, 0), 'Moon': (13, 10, 36)}


@pytest.mark.parametrize("planet", PLANETS)
def test_average_daily_motion_matches_handy_p2_within_two_arcseconds(engine, planet):
    d, m, s = AVERAGE_DAILY_SPEED_HANDY[planet]
    assert abs(engine["AVERAGE_DAILY_MOTION"][planet] - (d + m / 60 + s / 3600)) <= 2 / 3600 + 1e-9


# --- Planetary days and hours: Handy p. 35 ---
def test_day_lords_match_handy_p35_hour_one(engine):
    # Python weekday(): Monday=0. Sunday Sun, Monday Moon, Tuesday Mars,
    # Wednesday Mercury, Thursday Jupiter, Friday Venus, Saturday Saturn.
    assert engine["DAY_LORD_BY_WEEKDAY"] == {0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 4: 'Venus', 5: 'Saturn', 6: 'Sun'}


HANDY_P35 = """Q R U S V T W|T W Q R U S V|S V T W Q R U|R U S V T W Q|W Q R U S V T|V T W Q R U S|U S V T W Q R|Q R U S V T W|T W Q R U S V|S V T W Q R U|R U S V T W Q|W Q R U S V T|V T W Q R U S|U S V T W Q R|Q R U S V T W|T W Q R U S V|S V T W Q R U|R U S V T W Q|W Q R U S V T|V T W Q R U S|U S V T W Q R|Q R U S V T W|T W Q R U S V|S V T W Q R U"""
GLYPH = {'Q': 'Sun', 'R': 'Moon', 'U': 'Mars', 'S': 'Mercury', 'V': 'Jupiter', 'T': 'Venus', 'W': 'Saturn'}
DAYS_SUNDAY_FIRST = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']


def test_planetary_hours_cycle_reproduces_handy_p35_all_168_cells(engine):
    # Hour n of a day is n-1 steps down the Chaldean order from the day
    # lord; the 24 rows of p. 35 (12 diurnal from sunrise, 12 nocturnal
    # from sunset) for all seven days.
    order = engine["CHALDEAN_HOUR_ORDER"]
    for h, row in enumerate(HANDY_P35.split("|")):
        for d, glyph in enumerate(row.split()):
            expected = order[(order.index(DAYS_SUNDAY_FIRST[d]) + h) % 7]
            assert GLYPH[glyph] == expected, (h + 1, DAYS_SUNDAY_FIRST[d])


# --- Solar phase orbs: Abu Ma'shar VII.2 ---
def test_solar_orbs_match_great_introduction_vii_2(engine):
    # 11: Saturn and Jupiter burned within 6, Mars within 10; 37/40: the
    # inferiors burned to 7; 60/74: the Moon to 6. 13: under the rays to
    # 15 (Sat/Jup) and 18 (Mars) in the east; 31: 15 in the west; 40/44:
    # inferiors 12 east; 48/51: 15 west; 61/72: Moon 12. 30: westernizing
    # until 22 (Sat/Jup) and 18 (Mars).
    assert engine["SOLAR_BURNED_ORB"] == {'Saturn': (6.0, 6.0), 'Jupiter': (6.0, 6.0), 'Mars': (10.0, 10.0),
                                          'Venus': (7.0, 7.0), 'Mercury': (7.0, 7.0), 'Moon': (6.0, 6.0)}
    assert engine["SOLAR_RAYS_ORB"] == {'Saturn': (15.0, 15.0), 'Jupiter': (15.0, 15.0), 'Mars': (18.0, 15.0),
                                        'Venus': (12.0, 15.0), 'Mercury': (12.0, 15.0), 'Moon': (12.0, 12.0)}
    assert engine["SOLAR_SETTING_DEGREES"] == {'Saturn': 22.0, 'Jupiter': 22.0, 'Mars': 18.0}
    assert engine["CAZIMI_ORB"] == 16.0 / 60.0            # VII.2, 7
    assert engine["HARSH_BURNED_PATH"] == (199.0, 213.0)   # VII.6, 40: 19 Libra to 3 Scorpio


# --- Natural connections: Abu Ma'shar VII.5 ---
def _pairs(*ps):
    return {frozenset(p) for p in ps}


def test_natural_connection_pairs_match_vii_5(engine):
    # 56 (equal ascensions), 68-73 (equal daylight), 76 (by opposition), 77 (by sextile).
    assert engine["EQUAL_ASCENSION_PAIRS"] == _pairs(('Aries', 'Pisces'), ('Taurus', 'Aquarius'), ('Gemini', 'Capricorn'),
                                                     ('Cancer', 'Sagittarius'), ('Leo', 'Scorpio'), ('Virgo', 'Libra'))
    assert engine["EQUAL_DAYLIGHT_PAIRS"] == _pairs(('Gemini', 'Cancer'), ('Taurus', 'Leo'), ('Aries', 'Virgo'),
                                                    ('Libra', 'Pisces'), ('Sagittarius', 'Capricorn'))
    assert engine["NATURAL_OPPOSITION_PAIRS"] == _pairs(('Gemini', 'Capricorn'), ('Sagittarius', 'Cancer'),
                                                        ('Aries', 'Virgo'), ('Libra', 'Pisces'))
    assert engine["NATURAL_SEXTILE_PAIRS"] == _pairs(('Gemini', 'Cancer'), ('Virgo', 'Libra'),
                                                     ('Sagittarius', 'Capricorn'), ('Pisces', 'Aries'))


# --- Structural guards on the two prose tables (their text is audited by
# hand against the TNAC Reference Guide; see docs/synthesis/08) ---
def test_prose_tables_have_full_shape(engine):
    ml, ph = engine["MASHAALLAH_LORDS"], engine["PLANETS_IN_HOUSES"]
    assert set(ml) == set(range(1, 13)) and all(set(ml[h]) == set(range(1, 13)) for h in ml)
    assert set(ph) == set(range(1, 13))
    assert all(set(ph[h]) == set(PLANETS) and all(set(v) == {'Good', 'Bad'} for v in ph[h].values()) for h in ph)


# --- Twelfth-parts: Gr. Intr. V.18, 1-3, Figure 57 (order PN4R-4n-2) ---------

@pytest.mark.parametrize("lon, expected", [(17.3, 207.6), (45.0, 210.0), (0.0, 0.0), (2.4, 28.8), (29.99, 359.88)])
def test_twelfth_part_is_v18_3s_calculation(engine, lon, expected):
    """V.18, 3: "you see how much there is from the beginning of the sign up
    to the degree and minute whose twelfth-part you want to know, and you
    multiply it by 12, and you cast out what it amounts to from the
    beginning of that sign, 30 for every sign"."""
    assert engine["pn4_twelfth_part"](lon) == pytest.approx((int(lon // 30) * 30 + (lon % 30) * 12) % 360)
    assert engine["pn4_twelfth_part"](lon) == pytest.approx(expected)


# --- Virgo's partner: Gr. Intr. V.14, 7, Figure 53 (Gr. Intr.), fn 100 (Astra C01) ---

@pytest.mark.parametrize("lon, partner", [(45.0, "Mars"), (165.0, "Mercury"), (285.0, "Mars")])
def test_earth_triplicity_partner_is_mercury_in_virgo_only(engine, lon, partner):
    """V.14, 7: the partner is Mars "except that Mercury acts as partner to
    them both in Virgo especially"; fn 100: "rather than (or in preference
    to) Mars". The day and night lords are untouched."""
    r = engine["get_essential_rulers"](lon)
    assert r["triplicity_participating"] == partner
    assert (r["triplicity_day"], r["triplicity_night"]) == ("Venus", "Moon")
