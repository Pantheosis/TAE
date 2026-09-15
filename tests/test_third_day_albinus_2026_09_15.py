"""The third day of the Moon counted as Firmicus counts it, from his worked
chart: in the nativity of Albinus (Mathesis II.29, 21-22 and 34; Figure 34)
"on the third day the Moon, being established in Leo, full of light, flung
herself into the rays of Mars". With the Moon at 14 58' Cancer and Mars at
11 18' Aquarius at the birth, the Moon stands on Mars's opposition ray in
Leo two days after the birth (14 Leo, 182 degrees from him), not three
(29 Leo, 196): the birth day is the first, so the third day is birth + 2.
Owner's ruling of 2026-09-15."""
import swisseph as swe

# Figure 34 as printed: Mar 14 303 AD JC, 10:43:13 PM, LMT -00:49:56, Rome
# 12e29 41n54. UT = local mean time plus the zone offset.
ALBINUS_UT = 22 + 43 / 60 + 13 / 3600 + (49 / 60 + 56 / 3600)
ALBINUS_JD = swe.julday(303, 3, 14, ALBINUS_UT, swe.JUL_CAL)


def _sep(a, b):
    return (a - b) % 360.0


def test_the_third_day_is_two_days_after_the_birth(engine):
    assert engine["MOON_THIRD_DAY_DAYS"] == 2.0


def test_albinus_natal_moon_and_mars_are_figure_34s(engine):
    moon = swe.calc_ut(ALBINUS_JD, swe.MOON)[0][0] % 360.0
    mars = swe.calc_ut(ALBINUS_JD, swe.MARS)[0][0] % 360.0
    assert engine["get_zodiac_sign"](moon) == 'Cancer' and abs(moon - (90 + 14 + 58 / 60)) < 1.0
    assert engine["get_zodiac_sign"](mars) == 'Aquarius' and abs(mars - (300 + 11 + 18 / 60)) < 1.0


def test_albinus_third_day_moon_in_leo_on_mars_opposition(engine):
    third = engine["third_day_positions"](ALBINUS_JD)
    assert third['jd'] == ALBINUS_JD + 2.0
    moon, mars = third['Moon'], third['Mars']
    assert engine["get_zodiac_sign"](moon) == 'Leo'
    # "flung herself into the rays of Mars": within 3 degrees of his opposition.
    assert abs(_sep(moon, mars) - 180.0) < 3.0
    # And the count is inclusive: one day on she is short of the ray, three days on past it.
    one = swe.calc_ut(ALBINUS_JD + 1.0, swe.MOON)[0][0] % 360.0
    three = swe.calc_ut(ALBINUS_JD + 3.0, swe.MOON)[0][0] % 360.0
    assert _sep(one, swe.calc_ut(ALBINUS_JD + 1.0, swe.MARS)[0][0]) < 172.0
    assert _sep(three, swe.calc_ut(ALBINUS_JD + 3.0, swe.MARS)[0][0]) > 190.0
    # The row says the count.
    rows = engine["moon_third_day_rows"](third, {'Saturn': 177.6, 'Mars': mars}, 228.75)
    assert 'two days after the birth, the birth day counted as the first' in rows[0]['Value']
    assert rows[0]['Value'].startswith(engine["get_degree_string"](moon))
