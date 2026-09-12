"""The decisions of docs/synthesis/13_open_decisions.md, pinned one by one as
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
def test_d11_lot_of_death_is_stated_by_abu_mashar_and_printed_in_sahl_with_the_cusp_by_equation(engine):
    """FINAL-A12 / decision sheet row 4 (owner, 2026-09-11): the projection
    from Saturn is a rule Gr. Intr. VIII.4, 226 and VIII.6, 69 state; Sahl
    8.6, 1 as printed agrees, his manuscripts reading the Ascendant (fn
    89) -- "emendation" describes Sahl's transmission and lives in the
    note, not the confidence field. The eighth's degree is "by equation"
    (VIII.3, 14-15), this Lot's own rule whatever the shared switch says;
    the whole-sign carried degree is a labelled variant row."""
    row = _lot(engine, "death")
    assert row["project"] == "Saturn" and row["cusp_rule"] == "quadrant cusp"
    assert "VIII.4, 226" in row["source"] and "VIII.6, 69" in row["source"]
    assert row["confidence"].startswith("stated (Gr. Intr. VIII.4, 226")
    assert "emendation" not in row["confidence"] and "fn 89" in row["note"] and "emendation" in row["note"]
    variant = _lot(engine, "death_ws")
    assert variant["cusp_rule"] == "whole-sign place" and "not prescribed in any supplied passage" in variant["confidence"]
    # the Lots page's STANDING paragraph says the same (review D4, 2026-09-11)
    from conftest import ui_source
    src = ui_source()
    assert "The Lot of death is projected from Saturn: STATED by Abu Ma\\'shar (Gr. Intr. VIII.4, 226; VIII.6, 69), and Sahl 8.6, 1 as printed agrees, his manuscripts reading the Ascendant (fn 89" in src
    assert "is projected from Saturn by Dykes" not in src
    # the two rows differ only in the eighth's degree: with equal cusps they coincide
    from datetime import datetime
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    p, asc, cusps, sect = chart["planetary_data"], chart["ascendant"], chart["houses"], chart["sect"]
    death = engine["lot_by_id"]("death", p, asc, cusps, sect)
    ws = engine["lot_by_id"]("death_ws", p, asc, cusps, sect)
    expected = (p["Saturn"]["longitude"] + cusps[7] - p["Moon"]["longitude"]) % 360.0
    assert death == pytest.approx(expected)
    assert ws == pytest.approx((p["Saturn"]["longitude"] + (asc + 210.0) - p["Moon"]["longitude"]) % 360.0)
    equal = tuple((asc + 30.0 * i) % 360.0 for i in range(12))
    assert engine["lot_by_id"]("death", p, asc, equal, sect) == pytest.approx(engine["lot_by_id"]("death_ws", p, asc, equal, sect))


# --- D-12: 12 degrees for either node, cited to the two sources that say so
def test_d12_node_orb_label_cites_ch3_107_and_vii6_52_not_nativities_1_21(engine):
    import re
    from conftest import engine_source
    m = re.search(r"With the Head or Tail, without latitude \(99;[^)]*\)", engine_source())
    assert m and "Ch. 3, 107" in m.group(0) and "VII.6, 52" in m.group(0), m
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
def test_d15_mars_west_orb_defaults_to_gr_intr_15_and_switches_to_dykess_18_for_sahl(engine, monkeypatch):
    """15 is Gr. Intr. VII.2, 31; the 18 of the switch is Dykes's table in
    On Nativities 1.22 with fn 175 (VII.2, 30's westernizing boundary read
    into an 18-degree 'under the rays'), Sahl's own sentences being silent
    on Mars west -- relabelled from "Sahl's table" on 2026-09-11 (decision
    sheet row 10). The constants do not change."""
    assert engine["MARS_WEST_RAYS_18"] is False
    assert engine["solar_rays_orb"]("Mars") == (18.0, 15.0)
    monkeypatch.setitem(engine, "MARS_WEST_RAYS_18", True)
    assert engine["solar_rays_orb"]("Mars") == (18.0, 18.0)
    # the switch's label on the page (review round, 2026-09-11: pinned)
    from conftest import ui_source
    src = ui_source()
    assert '"Mars under the rays to 18° west"' in src
    assert "Dykes's table for Sahl (the chapter head of On Nativities 1.22, with fn 175, which " in src
    assert "Gr. Intr. VII.2, 31 puts " in src and '"Sahl\'s table"' not in src


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


# --- D-2: refusal wins under Sahl only -- Kind II suppresses, Kind IV brings down
def _fixture_chart(engine, date):
    from datetime import datetime, timedelta
    y, m, d = map(int, date.split("-"))
    dt = datetime(y, m, d, 14, 30) - timedelta(hours=11.2463 / 15.0)
    return engine["calculate_traditional_chart"](dt, 43.7792, 11.2463)


def test_d2_fixture_1240_10_05_venus_in_her_fall_receives_the_moon_by_house_brought_down(engine):
    # Venus at 26 Virgo (her fall) receives the Moon from 22 Taurus by house
    # and triplicity -- a PERFECT reception (49) met by a Kind IV (62). 62
    # says "brings it down and diminishes", not "does not accept", so the
    # row stays and is marked. This pins the breadth: a major-dignity
    # reception is not deleted by Kind IV.
    c = _fixture_chart(engine, "1240-10-05")
    p, sect = c["planetary_data"], c["sect"]
    with engine["doctrine"](engine["SAHL"]):
        kinds = {(r["Kind"][:2].strip(), r["Connecting"], r["With"]) for r in engine["evaluate_non_reception"](p, sect)}
        rec = [r for r in engine["evaluate_reception"](p, sect) if (r.get("Received"), r.get("Receiver")) == ("Moon", "Venus")]
    assert ("IV", "Moon", "Venus") in kinds and ("II", "Moon", "Venus") not in kinds, kinds
    assert len(rec) == 1 and "house" in rec[0]["Via"], rec
    assert rec[0]["Grade"].startswith("Perfect") and "brought down" in rec[0]["Grade"] and "(62)" in rec[0]["Grade"], rec


def test_d2_kind_ii_suppresses_the_only_reception_it_can_meet_a_minor_one(engine):
    # Sahl's own case (Questions Ch. 1, 63): Mercury connecting with Mars
    # from Cancer, Mars's fall, where Mars holds triplicity and bound.
    # Kind II refuses; no reception row survives. (The same pair is held
    # in test_sahl_question_chart.py on the figure's own positions.)
    p = _real_chart(engine, Mercury=91.5, Mars=38.0, Sun=40.0, Moon=200.0, Venus=60.0, Jupiter=250.0, Saturn=300.0)
    with engine["doctrine"](engine["SAHL"]):
        kinds = {(r["Kind"][:2].strip(), r["Connecting"], r["With"]) for r in engine["evaluate_non_reception"](p, "Nocturnal")}
        rec = [(r.get("Received"), r.get("Receiver")) for r in engine["evaluate_reception"](p, "Nocturnal")]
    assert ("II", "Mercury", "Mars") in kinds, kinds
    assert ("Mercury", "Mars") not in rec, rec


def test_d2_control_no_planet_has_house_or_exaltation_in_its_own_fall(engine):
    # Why Kind II can only ever meet a minor reception: the fall sign is
    # never the receiver's house or exaltation.
    for planet, falls in engine["FALLS"].items():
        for sign in falls:
            assert planet != engine["SIGN_TO_DOMICILE"].get(sign), (planet, sign)
            assert engine["EXALTATIONS"].get(planet, ("",))[0] != sign, (planet, sign)


def test_d2_control_abu_mashars_profile_keeps_the_same_pair_received_unmarked(engine):
    # Figure 143 reads these configurations as favor, not refusal: his
    # doctrine, his profile, untouched by D-2.
    c = _fixture_chart(engine, "1240-10-05")
    p, sect = c["planetary_data"], c["sect"]
    with engine["doctrine"](engine["ABU_MASHAR"]):
        rec = [r for r in engine["evaluate_reception"](p, sect) if (r.get("Received"), r.get("Receiver")) == ("Moon", "Venus")]
    assert rec and not any("brought down" in str(v) for r in rec for v in r.values()), rec


# --- D-3: the planetary years beside 1.20's grade (the natal grant) and On Times 4, 7 (a question chart)
def test_d3_years_display_reads_1_20_in_full_by_the_division_and_on_times_for_comparison(engine):
    c = _fixture_chart(engine, "1240-05-23")
    p, sect = c["planetary_data"], c["sect"]
    ess = engine["evaluate_essential_dignities"](p, sect)
    rows = engine["evaluate_planetary_years_display"](p, c["houses"], c["ascendant"], sect, ess)
    assert [r["Planet"] for r in rows] == ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    for r in rows:
        assert r["On Times 4, 7 (a question chart, 4, 2): for comparison"].startswith(("greater", "middle", "lesser", "in a stake but not eastern"))
        assert r["On Nativities 1.20 grants (as house-master)"].startswith(
            ("greater (1.20", "middle (1.20", "lesser (1.20", "months (1.20", "days (1.20", "hours (1.20",
             "days and hours (1.20", "middle as months and days (1.20", "1.20 silent"))
        assert (r["Lesser"], r["Greater"]) == (engine["PLANETARY_YEARS"][r["Planet"]]["lesser"], engine["PLANETARY_YEARS"][r["Planet"]]["greater"])
        g = engine["sahl_house_master_years"](r["Planet"], p, c["houses"], sect, ess)
        assert g["division"] == r["Division (5 deg at the stakes)"]


# Who may read PLANETARY_YEARS, and which of its columns. Extending either
# set is a deliberate act: add the function AND say why in the commit.
D3_GRANT_READERS = {
    "evaluate_planetary_years_display",
    # Added 2026-09-10 with III.7, 32-42. It reads the years as a TIMING
    # measure -- the ages at which a natal indication comes out, "the
    # amount of one of its own years" (III.7, 42) -- and not as a grant of
    # lifespan to a house-master, which is the thing PN IV does not
    # license. Decisive for admitting it: III.7, 35 selects among the
    # greater, middle and lesser "in accordance with what its position in
    # the rotation of the circle indicated in the root" and never states
    # that rule, so pn4_activation_ages CHOOSES NONE OF THE THREE -- it
    # prints all three, as the display evaluator does. Disagreement #2 is
    # left exactly where it was.
    "pn4_activation_ages",
    # Added 2026-09-10 with the Reference tables page. It prints the four
    # years and the fardar period as the course's Handy Tables print them
    # (Lesson 5), a table and nothing else: no caller reads a row to grant
    # anything, and the page reads no chart. UI_REVIEW_2026-09-10.md §3.
    "reference_planetary_years_rows",
    # Added 2026-09-11 with FINAL-A1 (decision sheet row 1, the owner): the
    # house-master's years ARE granted, from Sahl, On Nativities 1.20, 7-34
    # read in full -- the corpus's one natal grant, On Times 4 being a
    # question-chart chapter (4, 2) and 1.23, 68 pointing to 1.20. The
    # reader applies a grant to ONE planet, the house-master 1.15 names,
    # prints the sentence it rests on, and places by the division (the
    # owner's unit). This is the thing the control used to forbid; it is
    # admitted by the owner's decision, not by a reading.
    "sahl_house_master_years",
}
D3_FARDAR_READERS = {"evaluate_planetary_years_display", "pn4_fardar_sequence",
                     "pn4_activation_ages", "reference_planetary_years_rows",
                     "sahl_house_master_years"}          # reads the grant keys only (FINAL-A1); listed because it reads the table
D3_GRANT_KEYS = ("lesser", "middle", "greater", "mighty")


def _functions_reading(pattern):
    """Top-level engine functions whose source matches `pattern`."""
    import ast, re
    from conftest import engine_source
    src = engine_source()
    hits = set()
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef):
            if re.search(pattern, ast.get_source_segment(src, node) or ""):
                hits.add(node.name)
    return hits


def test_d3_control_the_GRANTED_years_are_applied_by_nothing():
    """D-3 was closed on 2026-09-10 and the timing apparatus was built from
    PN IV, so this control is no longer "nothing reads PLANETARY_YEARS" --
    pn4_fardar_sequence now reads it. What it guards is narrower.

    The LESSER, MIDDLE, GREATER and MIGHTY years are applied by ONE reader
    only: sahl_house_master_years (FINAL-A1, owner 2026-09-11), which grants
    the house-master its years from Sahl, On Nativities 1.20, 7-34. PN IV
    does not say which planet is the house-master or how many years it
    grants (IX.8, 123); On Times 4, 7 is a question-chart rule; 1.20 is the
    corpus's one natal grant. Nothing else may choose a row of that table.
    The FARDAR column is a different kind of number, a period length rather
    than a grant, and IV.1, 2 gives it outright.

    TWO CHECKS, and they catch different things. The key-level one runs
    first so that a genuine attempt to apply a grant gets the doctrinal
    message rather than the generic one; the by-name one then catches any
    new reader however it spells the read -- .get("greater"), a variable
    subscript, unpacking -- which the key-level check cannot see.

    IF THIS FAILS ON WORK YOU BELIEVE IS CORRECT: no regex can tell
    "applies a grant to a judgment" from "derives a displayed quantity",
    and the sets above are the place that decision is recorded. Deriving
    the Ages of Man from I.8, 9's rule, or III.7, 32-42's activation ages,
    would both land here legitimately. Applying a house-master's years as
    a lifespan would not -- that is the thing PN IV does not license."""
    grant_readers = set()
    for key in D3_GRANT_KEYS:
        grant_readers |= _functions_reading(r"\['" + key + r"'\]")
    unexpected = grant_readers - D3_GRANT_READERS
    assert not unexpected, (
        f"{sorted(unexpected)} read the lesser/middle/greater/mighty years. PN IV does not "
        f"say who the house-master is or what it grants (IX.8, 123), so a grant must not "
        f"reach a judgment. If this is a DISPLAY quantity or a derivation Abu Ma'shar states "
        f"(e.g. I.8, 9's Ages), add it to D3_GRANT_READERS and say why in the commit.")

    fardar_readers = _functions_reading(r"PLANETARY_YEARS\b")
    unexpected = fardar_readers - D3_FARDAR_READERS
    assert not unexpected, (
        f"{sorted(unexpected)} read PLANETARY_YEARS. That may be fine -- the fardar is a "
        f"period length, not a grant -- but it is not fine by default: add it to "
        f"D3_FARDAR_READERS deliberately, having checked it reads no grant.")


# --- D-1: Ptolemy's casting of the rays by ascensions (VII.7), a static quantity
EPS = 23.44
ARMC = 100.0
LAT = 43.7792


def test_d1_inverse_lookups_recover_the_degree(engine):
    for lon in (5.0, 95.0, 187.5, 271.0, 359.0):
        ra, _d = engine["_ra_decl"](lon, EPS)
        assert abs(engine["_lon_with_right_ascension"](ra, EPS) - lon) < 1e-6
        oa = engine["_oblique_ascension"](lon, EPS, LAT)
        assert engine["_circular_distance"](engine["_lon_with_oblique_ascension"](oa, EPS, LAT), lon) < 1e-4


def test_d1_at_the_equator_the_two_candidates_agree_and_no_hours_are_needed(engine):
    # Oblique ascension equals right ascension at latitude 0, so 16 applies:
    # "the rays of the planet are in that degree and minute", whatever the
    # hours of distance and whichever anchor.
    for anchor in engine["RAY_ANCHOR_OPTIONS"]:
        cast = engine["cast_rays_by_ascension"](130.0, ARMC, EPS, 0.0, anchor)
        for name, arc in engine["RAY_ASPECTS"]:
            r = cast[name]
            assert abs(r["from right ascensions (14)"] - r["from the city's ascensions (15)"]) < 1e-6
            assert abs(r["ascensional"] - r["from right ascensions (14)"]) < 1e-6


def test_d1_the_opposition_is_exempt_in_the_same_degree_and_minute(engine):
    cast = engine["cast_rays_by_ascension"](130.25, ARMC, EPS, LAT)
    assert abs(cast["Opposition"]["ascensional"] - 310.25) < 1e-9
    assert cast["Opposition"]["ascensional"] == cast["Opposition"]["zodiacal"]


def test_d1_hours_lie_within_a_quadrant_and_the_stake_matches(engine):
    for lon in range(0, 360, 15):
        q, stake, hours = engine["_hours_from_stake"](float(lon), ARMC, EPS, LAT)
        assert 0.0 <= hours <= 6.0 + 1e-9, (lon, q, hours)
        assert (q, stake) in {("Midheaven to Ascendant", "Midheaven"), ("Ascendant to stake of the earth", "Ascendant"),
                              ("Stake of the earth to setting", "Stake of the earth"), ("Setting to Midheaven", "Stake of the setting")}


def test_d1_a_planet_on_the_midheaven_has_no_hours_and_keeps_the_anchor(engine):
    lon = engine["_lon_with_right_ascension"](ARMC, EPS)
    cast = engine["cast_rays_by_ascension"](lon, ARMC, EPS, LAT, "nearest")
    r = cast["Left square"]
    assert r["hours"] < 1e-6 and r["stake"] == "Midheaven"
    near = min((r["from right ascensions (14)"], r["from the city's ascensions (15)"]),
               key=lambda x: engine["_circular_distance"](x, lon))
    assert abs(r["ascensional"] - near) < 1e-9


def test_d1_as_written_is_nearest_for_left_rays_and_distant_for_right_rays(engine):
    lon = 130.0
    written = engine["cast_rays_by_ascension"](lon, ARMC, EPS, LAT, "as written")
    nearest = engine["cast_rays_by_ascension"](lon, ARMC, EPS, LAT, "nearest")
    distant = engine["cast_rays_by_ascension"](lon, ARMC, EPS, LAT, "distant")
    for name, arc in engine["RAY_ASPECTS"]:
        same = nearest if arc > 0 else distant
        assert written[name]["ascensional"] == same[name]["ascensional"], name
    # The two readings really differ somewhere at this latitude, which is
    # why the text's flip matters.
    assert any(abs(nearest[n]["ascensional"] - distant[n]["ascensional"]) > 0.01 for n, _a in engine["RAY_ASPECTS"])


def test_d1_control_the_ray_stays_within_the_span_of_its_two_candidates(engine):
    # The correction interpolates between the candidates; it never
    # overshoots the far one (17-19: a sixth of the excess per hour, and
    # hours never exceed six).
    for lon in range(0, 360, 20):
        cast = engine["cast_rays_by_ascension"](float(lon), ARMC, EPS, LAT)
        for name, _arc in engine["RAY_ASPECTS"]:
            r = cast[name]
            a, b, x = r["from right ascensions (14)"], r["from the city's ascensions (15)"], r["ascensional"]
            span = engine["_circular_distance"](a, b)
            assert engine["_circular_distance"](x, a) <= span + 1e-6 and engine["_circular_distance"](x, b) <= span + 1e-6


def test_d1_rows_cover_seven_planets_and_seven_rays(engine):
    c = _fixture_chart(engine, "1240-05-23")
    rows = engine["evaluate_rays_by_ascension"](c["planetary_data"], c["armc"], c["obliquity"], LAT)
    assert len(rows) == 49 and {r["Ray"] for r in rows} == {n for n, _a in engine["RAY_ASPECTS"]} | {"Opposition"}


# --- D-22 (decided 2026-09-08): Kind III refuses a coexisting reception -----
# Sahl's Kind III (Ch. 3, 61) uses Kind II's verbs -- "it will not be
# recognized", and in Questions Ch. 1, 41 "it does not accept them" -- not
# Kind IV's "brings it down". So it suppresses the reception the same pair
# would otherwise earn, rather than annotating it. What it can suppress is
# only ever minor: 61's parenthesis exempts house and exaltation, leaving
# the triplicity (50) with or without the bound (54-55).

def _reception_pairs(engine, date):
    from datetime import datetime
    y, m, d = (int(x) for x in date.split('-'))
    chart = engine["calculate_traditional_chart"](datetime(y, m, d, 12, 0), 51.5, -0.12)
    rows = engine["evaluate_reception"](chart['planetary_data'], chart['sect'])
    return {(r.get('Received'), r.get('Receiver')) for r in rows}


def _kind_pairs(engine, date, prefix):
    from datetime import datetime
    y, m, d = (int(x) for x in date.split('-'))
    chart = engine["calculate_traditional_chart"](datetime(y, m, d, 12, 0), 51.5, -0.12)
    rows = engine["evaluate_non_reception"](chart['planetary_data'], chart['sect'])
    return {(r['Connecting'], r['With']) for r in rows if str(r['Kind']).startswith(prefix)}


def test_d22_kind_three_suppresses_the_reception_it_refuses(engine):
    """1240-01-18: the Moon connects with Venus from her own fall, Venus
    holding neither house nor exaltation there but the triplicity. Before
    D-22 the engine listed 'Lesser, triplicity alone (50)' beside the
    refusal; it must not now."""
    assert ('Moon', 'Venus') in _kind_pairs(engine, '1240-01-18', 'III ')
    assert ('Moon', 'Venus') not in _reception_pairs(engine, '1240-01-18')


def test_d22_refusal_beats_the_kind_iv_annotation(engine):
    """1240-09-19 carries Kind III and Kind IV on the same pair. A refusal
    removes the row, so there is nothing left to mark 'brought down' -- the
    two rules must not both fire and leave an annotated row standing."""
    assert ('Moon', 'Venus') in _kind_pairs(engine, '1240-09-19', 'III ')
    assert ('Moon', 'Venus') in _kind_pairs(engine, '1240-09-19', 'IV ')
    assert ('Moon', 'Venus') not in _reception_pairs(engine, '1240-09-19')


def test_d22_leaves_non_kind_three_receptions_alone(engine):
    """The suppression is keyed to the refused pair, not to the chart. On
    1240-01-18 two other receptions stand, and 1240-10-05 -- a fixture chart
    with two Kind III rows of its own -- keeps its Moon/Venus reception
    because that pair is not one of them."""
    assert ('Moon', 'Mars') in _reception_pairs(engine, '1240-01-18')
    assert ('Venus', 'Jupiter') in _reception_pairs(engine, '1240-01-18')
    assert ('Moon', 'Venus') in _reception_pairs(engine, '1240-10-05')
    assert ('Moon', 'Venus') not in _kind_pairs(engine, '1240-10-05', 'III ')


# --- The five-degree switch retired (owner's ruling 2026-09-11, sheet row 3) ------------

def test_five_degree_all_cusps_is_no_longer_a_reading(engine):
    """The five-degree rule is a dynamics rule at the four stakes only; the
    all-cusps form has no place under the canon and its switch is gone. A
    stored preference for it is ignored on read."""
    assert engine["FIVE_DEGREE_ALL_CUSPS"] is False
    assert "_five_degree_all_cusps" not in engine["PREFERENCE_KEYS"]
    from conftest import ui_source
    assert "five_degree_all_cusps" not in ui_source().replace("'_five_degree_all_cusps' retired", "")
    cusps = tuple(range(0, 360, 30))
    assert engine["get_effective_house"](58.0, cusps) == 2            # 2 degrees before the third cusp: no carry-over
    assert engine["get_effective_house"](88.0, cusps) == 4            # 2 degrees before the fourth's cusp (a stake): carried


# --- GAP-39 (sheet row 15): VII.6, 52's own nodes read; D-19 kept and cited -----------

def test_vii_6_52_flags_a_planet_within_twelve_degrees_of_its_own_node(engine):
    """Gr. Intr. VII.6, 52: "Or they are with the Heads of their own Dragons,
    or with their Tails ... and between them are 12 degrees or less". Mars's
    mean ascending node at J2000 is near 7.7 Aries: Mars set at 10 Aries is
    flagged, with the mean/true reading named; Saturn, far from his own
    node (near 113 degrees), is not. The Moon's-node clause is untouched."""
    from datetime import datetime
    chart = engine["calculate_traditional_chart"](datetime(2000, 1, 1, 12), 0.0, 0.0)
    p = chart["planetary_data"]
    p["Mars"]["longitude"] = 10.0
    p["North Node"]["longitude"] = 200.0            # the Moon's node well away from both
    ess = engine["evaluate_essential_dignities"](p, chart["sect"])
    acc = engine["evaluate_accidental_dignities"](p, chart["houses"], chart["sect"], chart["julian_day"])
    out = engine["evaluate_abu_mashar_condition"](p, chart["houses"], chart["sect"], ess, acc,
                                                  chart["julian_day"], chart["ascendant"])
    mars = [l for l in out["Mars"]["Negative Labels"] if "its own" in l]
    assert mars and "52" in mars[0] and "mean node" in mars[0] and "does not say mean or true" in mars[0], mars
    assert not [l for l in out["Saturn"]["Negative Labels"] if "its own" in l]
    doc = engine["evaluate_abu_mashar_condition"].__doc__
    assert "Not implemented BY DECISION D-19" in doc and "V.19, 7" in doc
