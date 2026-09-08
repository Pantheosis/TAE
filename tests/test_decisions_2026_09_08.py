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
