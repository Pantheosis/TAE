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


# --- D-3: the planetary years shown beside the two placement rules, applied to nothing
def test_d3_years_display_reads_both_rules_and_names_the_silence(engine):
    c = _fixture_chart(engine, "1240-05-23")
    p, sect = c["planetary_data"], c["sect"]
    ess = engine["evaluate_essential_dignities"](p, sect)
    rows = engine["evaluate_planetary_years_display"](p, c["houses"], c["ascendant"], sect, ess)
    assert [r["Planet"] for r in rows] == ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    for r in rows:
        assert r["On Times 4, 7 would grant"].startswith(("greater", "middle", "lesser", "in a stake but not eastern"))
        assert r["On Nativities 1.20 would grant"].startswith(("greater", "middle", "not stated"))
        assert (r["Lesser"], r["Greater"]) == (engine["PLANETARY_YEARS"][r["Planet"]]["lesser"], engine["PLANETARY_YEARS"][r["Planet"]]["greater"])


def test_d3_control_the_GRANTED_years_are_applied_by_nothing(engine):
    """D-3 was closed on 2026-09-10 and the timing apparatus was built from
    PN IV, so the control is no longer "nothing reads PLANETARY_YEARS" --
    pn4_fardar_sequence now reads it. What the control guards is narrower,
    and is still exactly true.

    The LESSER, MIDDLE, GREATER and MIGHTY years remain display-only. PN IV
    turned out not to say which planet is the house-master or how many
    years it grants -- Abu Ma'shar defers it to a book outside this corpus
    (IX.8, 123) -- so corpus disagreement #2 stays open on the merits and
    no row of that table is chosen by anything.

    The FARDAR column is a different kind of number: a period length, not
    a grant. IV.1, 2 gives it outright and it is implemented, so exactly
    one further reader of it is expected."""
    from conftest import engine_source, function_source
    import re
    src = engine_source()
    display = function_source("evaluate_planetary_years_display")
    fardar_seq = function_source("pn4_fardar_sequence")

    # (a) WHO may touch the constant at all. This is the coarse check the
    # test carried before D-3 closed, kept rather than traded away: it
    # catches a new reader however it spells the read -- .get("greater"),
    # a variable subscript, unpacking -- which the key-level check in (b)
    # cannot see.
    readers = [m.start() for m in re.finditer(r"PLANETARY_YEARS\b", src)]
    assert len(readers) == 3, (
        f"{len(readers)} mentions of PLANETARY_YEARS in the engine half; expected the "
        f"definition, evaluate_planetary_years_display and pn4_fardar_sequence. A new "
        f"reader must be justified here before it is allowed.")
    assert src.count("PLANETARY_YEARS") - display.count("PLANETARY_YEARS") \
           - fardar_seq.count("PLANETARY_YEARS") == 1, "the extra reader is not one of the two named"

    # (b) WHICH years they may read. No grant is read anywhere but the
    # display evaluator; a grant applied to a judgment is the thing D-3's
    # closure did NOT authorise.
    for key in ("lesser", "middle", "greater", "mighty"):
        pattern = r"\['" + key + r"'\]"
        assert len(re.findall(pattern, src)) == len(re.findall(pattern, display)) == 1, (
            f"the {key} years are read outside evaluate_planetary_years_display; "
            f"D-3's closure did not authorise applying a grant")
    assert len(re.findall(r"\['fardar'\]", src)) == 2
    assert len(re.findall(r"\['fardar'\]", fardar_seq)) == 1


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
