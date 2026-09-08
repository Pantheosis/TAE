"""The decisions of synthesis/13_open_decisions.md, pinned one by one as
they were implemented on 2026-09-08. Each test names its item; the
document carries the passages and the reasoning, this file only holds the
engine to the answer.
"""
from __future__ import annotations

import pytest


def _lot(engine, lot_id):
    return next(d for d in engine["LOT_DEFINITIONS"] if d["id"] == lot_id)


# --- D-4: the Masha'allah work/authority Lot reverses at night ------------
def test_d4_work_authority_reverses_at_night(engine):
    row = _lot(engine, "work_authority")
    assert (row["start"], row["end"], row["project"]) == ("Sun", "Saturn", "Ascendant")
    assert row["reverse_at_night"] is True


def test_d4_control_the_unreversed_expedition_lot_is_untouched(engine):
    # Sahl's own text: "calculate BY DAY AND NIGHT from Saturn to the Moon"
    # (10.2.5, 1). D-4 is about the Sun-Saturn Lot only.
    assert _lot(engine, "work_expedition")["reverse_at_night"] is False


# --- D-11: the Lot of death stays projected from Saturn, labelled ---------
def test_d11_lot_of_death_is_projected_from_saturn_and_says_it_is_an_emendation(engine):
    row = _lot(engine, "death")
    assert row["project"] == "Saturn"
    assert "emendation" in row["confidence"] and "fn. 89" in row["note"]


# --- D-12: 12 degrees for either node, cited to the two sources that say so
def test_d12_node_orb_label_cites_ch3_107_and_vii6_52_not_nativities_1_21(engine):
    import re
    from conftest import engine_source
    m = re.search(r"With the Head or Tail, without latitude \(99;[^)]*\)", engine_source())
    assert m and "Ch.3, 107" in m.group(0) and "VII.6, 52" in m.group(0), m
    assert "1.21, 12" not in m.group(0)


# --- D-5 / C-04: Sahl's dark signs and his burned place without degrees --
def test_d5_dark_signs_are_libra_and_capricorn(engine):
    assert engine["DARK_SIGNS"] == {"Libra", "Capricorn"}


def test_d5_control_scorpio_is_not_a_dark_sign(engine):
    # Scorpio adjoins the burned place and is NOT a dark sign in either
    # witness; the two categories are separate (C-04).
    assert "Scorpio" not in engine["DARK_SIGNS"]


def _special(engine, lon):
    rows = engine["evaluate_special_degrees"]({"Sun": {"longitude": lon}})
    return rows[0]["Condition"] if rows else ""


def test_d5_burned_place_is_a_sign_label_with_no_degree_test(engine):
    # 2 Libra and 25 Scorpio both carry the label: Sahl's "end of Libra and
    # beginning of Scorpio" comes with no degrees, so none may be invented.
    assert "burned place" in _special(engine, 182.0)
    assert "burned place" in _special(engine, 235.0)
    assert "no degrees given" in _special(engine, 182.0)


def test_d5_control_abu_mashar_keeps_his_own_19_to_3_span(engine):
    # VII.6, 40's harsher band stays where the table is his.
    assert engine["HARSH_BURNED_PATH"] == (199.0, 213.0)
    assert "burned place" not in _special(engine, 100.0)


# --- D-7 / C-11: the contradicted sign categories, two readings by work ---
def test_d7_four_footed_differs_by_work(engine):
    assert "Leo" in engine["FOUR_FOOTED"]["On Nativities"]
    assert "Leo" not in engine["FOUR_FOOTED"]["Introduction"]
    assert "Capricorn" in engine["FOUR_FOOTED"]["Introduction"]
    assert "Capricorn" not in engine["FOUR_FOOTED"]["On Nativities"]


def test_d7_control_no_merged_four_footed_list_exists(engine):
    # No reading may contain BOTH Leo and Capricorn; that union is in
    # neither witness.
    for reading in engine["FOUR_FOOTED"].values():
        assert not {"Leo", "Capricorn"} <= set(reading)


def test_d7_voice_virgo_flips_class_between_works(engine):
    assert "Virgo" in engine["VOICE"]["Introduction"]["half a voice"]
    assert "Virgo" in engine["VOICE"]["On Nativities"]["powerful voice"]
    for work, classes in engine["VOICE"].items():
        listed = [sg for signs in classes.values() for sg in signs]
        assert sorted(listed) == sorted(set(listed)) and len(listed) == 12, work


def test_d7_barren_lists_differ_and_the_reported_opinion_is_kept_apart(engine):
    b = engine["BARREN"]
    assert "Aries" in b["Introduction"] and "Aries" not in b["On Nativities"]
    assert "Sagittarius" in b["On Nativities"] and "Sagittarius" not in b["Introduction"]
    assert b["On Nativities (some scholars, 1.38, 17)"] == ["Capricorn", "Aquarius"]
    assert engine["MANY_CHILDREN"] == ["Cancer", "Scorpio", "Pisces"]


def test_d7_sign_categories_shows_both_readings_for_virgo(engine):
    row = engine["sign_categories"]("Virgo")
    assert row["Voice (Intro)"] == "half a voice" and row["Voice (Nat.)"] == "powerful voice"
    assert row["Barren (Intro)"] == "yes" and row["Barren (Nat.)"] == "yes"


# --- D-8 / C-20: two dignity orderings, never merged ----------------------
def test_d8_dignity_orderings_are_kept_separate_by_context(engine):
    order = engine["DIGNITY_ORDER"]
    q = next(v for k, v in order.items() if k.startswith("Questions Ch. 13, 7"))
    n = next(v for k, v in order.items() if k.startswith("On Nativities 1.20, 2"))
    assert q == ["house", "triplicity", "bound", "face"]
    assert n == ["bound", "house", "exaltation", "triplicity", "image"]


def test_d8_control_the_questions_chain_gains_no_exaltation_slot(engine):
    q = next(v for k, v in engine["DIGNITY_ORDER"].items() if k.startswith("Questions Ch. 13, 7"))
    assert "exaltation" not in q


# --- D-9 / C-09: the good-place schemes and the printed 7-place order -----
def test_d9_seven_place_ranking_is_the_printed_order_and_says_so(engine):
    schemes = engine["GOOD_PLACE_SCHEMES"]
    seven = next(v for k, v in schemes.items() if k.startswith("Seven praised places"))
    assert seven == [1, 10, 7, 4, 11, 9, 5]
    note = engine["SEVEN_PLACE_RANKING_NOTE"]
    assert "11, 5, 9" in note and "conflation" in note


def test_d9_control_the_other_schemes_are_not_merged_into_the_ranking(engine):
    schemes = engine["GOOD_PLACE_SCHEMES"]
    eight = next(v for k, v in schemes.items() if k.startswith("Eight places"))
    assert sorted(eight["stakes"] + eight["what follows the stakes"] + eight["falling from the stakes"]) == list(range(1, 13))
    six = next(v for k, v in schemes.items() if k.startswith("Six excellent"))
    assert set(six) == engine["EXCELLENT_PLACES"] == {1, 4, 5, 7, 10, 11}
    sun = next(v for k, v in schemes.items() if k.startswith("Excellent places for the Sun"))
    assert sorted(sun) == [1, 10, 11]


# --- D-6: Masha'allah's operating condition, as a column -----------------
def _chart(**lons):
    return {k: {"longitude": v, "latitude": 0.0, "speed": 1.0} for k, v in lons.items()}


def _real_chart(engine, **lons):
    """A fully-keyed planetary_data from the ephemeris, with the named
    longitudes overridden -- for evaluators that read speed, latitude and
    the rest, which the bare _chart() helper does not carry."""
    from datetime import datetime
    p = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 12, 0), 43.7792, 11.2463)["planetary_data"]
    for k, v in lons.items():
        p[k]["longitude"] = v
    return p


def test_d6_condition_is_met_when_nothing_afflicts_or_witnesses(engine):
    # Aries rising; the 3rd is Gemini, lord Mercury in Leo. Saturn and Mars
    # in Aries (sextile the house, trine the lord -- neither counts as an
    # affliction); Jupiter and Venus in Capricorn, averse to Gemini AND Leo.
    p = _chart(Mercury=125.0, Saturn=15.0, Mars=20.0, Jupiter=275.0, Venus=280.0, Sun=10.0, Moon=40.0)
    assert engine["mashaallah_condition"](3, "Mercury", p, 5.0) == ("met", "")


def test_d6_an_infortune_square_the_house_breaks_it_and_names_itself(engine):
    p = _chart(Mercury=125.0, Saturn=155.0, Mars=20.0, Jupiter=275.0, Venus=280.0, Sun=10.0, Moon=40.0)
    status, why = engine["mashaallah_condition"](3, "Mercury", p, 5.0)
    assert status == "not met" and why == "Saturn square the 3rd", why


def test_d6_a_fortune_witnessing_the_lord_by_trine_breaks_it(engine):
    # Jupiter in Sagittarius: opposite the house and trine its lord.
    p = _chart(Mercury=125.0, Saturn=15.0, Mars=20.0, Jupiter=245.0, Venus=280.0, Sun=10.0, Moon=40.0)
    status, why = engine["mashaallah_condition"](3, "Mercury", p, 5.0)
    assert status == "not met" and "Jupiter witnesses its lord Mercury (trine)" in why
    assert "Jupiter witnesses the 3rd (opposite)" in why


def test_d6_control_the_lord_is_not_counted_against_itself_and_rows_keep_the_reading(engine):
    # Scorpio's lord Mars: Mars is an infortune but not an affliction of his
    # own house. And the column is added beside the reading, not in place
    # of it -- the condition is a column, never a filter.
    # Saturn in Aries (averse to Scorpio), Jupiter in Sagittarius and Venus
    # in Libra (both averse to Scorpio, where house and lord sit).
    p = _chart(Mars=215.0, Saturn=15.0, Jupiter=245.0, Venus=185.0, Sun=10.0, Moon=40.0, Mercury=125.0)
    assert engine["mashaallah_condition"](8, "Mars", p, 5.0)[0] == "met"
    rows = engine["evaluate_house_lords"](p, 5.0)
    assert len(rows) == 12 and all("Masha'allah's condition" in r and "Masha'allah Signification" in r for r in rows)


# --- D-20 / D-21: the V.22 tables, display only, on the points the text names
def test_d20_fig63_reads_the_moon_fortune_and_ascendant_only(engine):
    p = _chart(Sun=100.0, Moon=44.5, Mercury=10.0, Venus=20.0, Mars=59.5, Jupiter=200.0, Saturn=250.0)
    # Moon at Taurus 15 (ordinal) hits; Mars at Taurus 30 does not count.
    rows = engine["evaluate_book_v_degrees"](p, 5.0, 35.0, "Diurnal")
    assert [r["Point"] for r in rows if "Fig. 63" in r["Table"]] == ["Moon"]


def test_d21_fig64_reads_the_ascendant_and_the_sect_luminary(engine):
    # Sun at Libra 3 by day hits; the same Sun by night does not, the Moon does.
    p = _chart(Sun=182.5, Moon=316.5, Mercury=10.0, Venus=20.0, Mars=100.0, Jupiter=200.0, Saturn=250.0)   # Moon at Aquarius 17
    day = engine["evaluate_book_v_degrees"](p, 5.0, 100.0, "Diurnal")
    night = engine["evaluate_book_v_degrees"](p, 5.0, 100.0, "Nocturnal")
    assert [r["Point"] for r in day if "Fig. 64" in r["Table"]] == ["Sun (luminary of the sect)"]
    assert [r["Point"] for r in night if "Fig. 64" in r["Table"]] == ["Moon (luminary of the sect)"]
    assert "also a well" in next(r for r in night if r["Point"].startswith("Moon"))["Caveat"]   # Aquarius 17


def test_d21_control_no_row_is_a_verdict(engine):
    p = _chart(Sun=182.5, Moon=44.5, Mercury=10.0, Venus=20.0, Mars=100.0, Jupiter=200.0, Saturn=250.0)
    for r in engine["evaluate_book_v_degrees"](p, 5.0, 100.0, "Diurnal"):
        assert set(r) == {"Point", "Position", "Table", "Caveat"} and r["Caveat"]


# --- D-15: Mars's western orb, 15 by default, 18 by switch ---------------
def test_d15_mars_west_orb_defaults_to_abu_mashars_15_and_switches_to_sahls_18(engine, monkeypatch):
    assert engine["MARS_WEST_RAYS_18"] is False
    assert engine["solar_rays_orb"]("Mars") == (18.0, 15.0)
    monkeypatch.setitem(engine, "MARS_WEST_RAYS_18", True)
    assert engine["solar_rays_orb"]("Mars") == (18.0, 18.0)


def test_d15_a_mars_16_degrees_west_changes_phase_only_under_the_switch(engine, monkeypatch):
    # Mars 16 degrees west of the Sun (rising after him): westernizing at
    # 15, under the rays at 18.
    off = engine["solar_phase"]("Mars", 116.0, 100.0)
    monkeypatch.setitem(engine, "MARS_WEST_RAYS_18", True)
    on = engine["solar_phase"]("Mars", 116.0, 100.0)
    assert off[1] == on[1] == "western"
    assert on[0] == "Under the rays" and off[0] != "Under the rays", (off, on)


def test_d15_control_the_eastern_orb_and_the_other_planets_are_untouched(engine, monkeypatch):
    monkeypatch.setitem(engine, "MARS_WEST_RAYS_18", True)
    assert engine["solar_rays_orb"]("Mars")[0] == 18.0
    assert engine["solar_rays_orb"]("Saturn") == (15.0, 15.0) and engine["solar_rays_orb"]("Venus") == (12.0, 15.0)


# --- D-13: the fitting infortune, a switch that is off by default ---------
def test_d13_fitting_infortune_names_the_malefic_ruling_the_ascendant(engine):
    assert engine["fitting_infortune"](275.0) == "Saturn"      # Capricorn rising
    assert engine["fitting_infortune"](215.0) == "Mars"        # Scorpio rising
    assert engine["fitting_infortune"](95.0) is None           # Cancer rising


def test_d13_control_off_by_default_and_the_full_set_stands(engine):
    assert engine["FITTING_INFORTUNE"] is False and engine["SOFTENED_INFORTUNE"] is None
    assert engine["effective_infortunes"]() == {"Saturn", "Mars"} == engine["INFORTUNES"]


def test_d13_when_named_the_fitting_infortune_leaves_the_moons_106_alone(engine, monkeypatch):
    # Capricorn rising; the Moon at 5 Aries is squared by Saturn at 5 Cancer.
    p = _real_chart(engine, Sun=100.0, Moon=5.0, Mercury=110.0, Venus=120.0, Mars=130.0, Jupiter=250.0, Saturn=95.0)
    before = engine["evaluate_corruption_of_the_moon"](p, 275.0, "Diurnal")["labels"]
    assert any("(106)" in l or "opposed by an infortune" in l for l in before), before
    monkeypatch.setitem(engine, "SOFTENED_INFORTUNE", "Saturn")
    after = engine["evaluate_corruption_of_the_moon"](p, 275.0, "Diurnal")["labels"]
    assert not any("opposed by an infortune" in l for l in after), after
    assert engine["effective_infortunes"]() == {"Mars"}


def test_d13_control_a_malefic_that_rules_nothing_is_never_softened(engine, monkeypatch):
    # The switch names the Ascendant's ruler only: with Cancer rising there
    # is nothing to soften, and Saturn's square still counts.
    p = _real_chart(engine, Sun=100.0, Moon=5.0, Mercury=110.0, Venus=120.0, Mars=130.0, Jupiter=250.0, Saturn=95.0)
    monkeypatch.setitem(engine, "SOFTENED_INFORTUNE", engine["fitting_infortune"](95.0))
    labels = engine["evaluate_corruption_of_the_moon"](p, 95.0, "Diurnal")["labels"]
    assert any("opposed by an infortune" in l for l in labels), labels
