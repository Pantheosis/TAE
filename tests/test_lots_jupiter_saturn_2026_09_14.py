"""Abu Ma'shar's Lots of Jupiter and Saturn (Gr. Intr. VIII.3, 37-41; VIII.6,
13-14), added 2026-09-14 from the course-to-app coverage list. Supplement
rows: Sahl's Nativities has neither."""
import pytest
from datetime import datetime


def _lot(engine, lot_id):
    return next(d for d in engine["LOT_DEFINITIONS"] if d["id"] == lot_id)


def test_the_two_rows_carry_their_formulas_and_are_supplement_only(engine):
    jup = _lot(engine, "jupiter_prosperity")
    assert (jup["start"], jup["end"], jup["project"], jup["reverse_at_night"]) == ("spirit", "Jupiter", "Ascendant", True)
    assert jup["supplement"] is True and "VIII.3, 40-41" in jup["source"] and "VIII.6, 13" in jup["source"]
    sat = _lot(engine, "saturn_burdensome")
    assert (sat["start"], sat["end"], sat["project"], sat["reverse_at_night"]) == ("Saturn", "fortune", "Ascendant", True)
    assert sat["supplement"] is True and "VIII.3, 37-38" in sat["source"] and "VIII.6, 14" in sat["source"]
    # the seven planetary Lots of VIII.6, 7-14 are now all in the table
    ids = {d["id"] for d in engine["LOT_DEFINITIONS"]}
    assert {"fortune", "spirit", "desire", "necessity", "courage", "jupiter_prosperity", "saturn_burdensome"} <= ids


def test_the_two_lots_compute_from_the_invisible_and_from_saturn(engine):
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    p, asc, cusps, sect = chart["planetary_data"], chart["ascendant"], chart["houses"], chart["sect"]
    assert sect == "Diurnal"
    spirit = engine["lot_by_id"]("spirit", p, asc, cusps, sect)
    fortune = engine["lot_by_id"]("fortune", p, asc, cusps, sect)
    jup = engine["lot_by_id"]("jupiter_prosperity", p, asc, cusps, sect)
    sat = engine["lot_by_id"]("saturn_burdensome", p, asc, cusps, sect)
    # by day: from the Invisible to Jupiter; from Saturn to Fortune (VIII.3, 40; 37)
    assert jup == pytest.approx((asc + p["Jupiter"]["longitude"] - spirit) % 360.0)
    assert sat == pytest.approx((asc + fortune - p["Saturn"]["longitude"]) % 360.0)
    # by night both reverse
    night = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 1, 45), 43.7792, 11.2463)
    p2, asc2, cusps2, sect2 = night["planetary_data"], night["ascendant"], night["houses"], night["sect"]
    assert sect2 == "Nocturnal"
    spirit2 = engine["lot_by_id"]("spirit", p2, asc2, cusps2, sect2)
    fortune2 = engine["lot_by_id"]("fortune", p2, asc2, cusps2, sect2)
    assert engine["lot_by_id"]("jupiter_prosperity", p2, asc2, cusps2, sect2) == pytest.approx((asc2 + spirit2 - p2["Jupiter"]["longitude"]) % 360.0)
    assert engine["lot_by_id"]("saturn_burdensome", p2, asc2, cusps2, sect2) == pytest.approx((asc2 + p2["Saturn"]["longitude"] - fortune2) % 360.0)
