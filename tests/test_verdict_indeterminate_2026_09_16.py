"""Owner's ruling of 2026-09-16 on the Planetary Condition table's app
heuristic: a net of zero is 'Indeterminate', as the Dignities page's Lean
already says, not 'Good'. A tie is not a favourable judgment."""
import pytest

from conftest import FLORENCE, LOCAL_TIME

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def _condition_table(engine, day):
    from datetime import date
    y, m, d = (int(x) for x in day.split("-"))
    jd = engine["civil_local_to_jd_ut"](y, m, d, LOCAL_TIME.hour + LOCAL_TIME.minute / 60.0, FLORENCE[1] / 15.0)
    chart = engine["calculate_traditional_chart_jd"](jd, *FLORENCE)
    p, sect = chart["planetary_data"], chart["sect"]
    essential = engine["evaluate_essential_dignities"](p, sect)
    accidental = engine["evaluate_accidental_dignities"](p, chart["houses"], sect, chart["julian_day"],
                                                         armc=chart["armc"], obliquity=chart["obliquity"], geo_lat=FLORENCE[0])
    sim = engine["_simulate_forward"](p, chart["julian_day"])
    return engine["evaluate_abu_mashar_condition"](p, chart["houses"], sect, essential, accidental,
                                                   chart["julian_day"], chart["ascendant"], sim)


def test_a_net_of_zero_is_indeterminate_and_the_signs_keep_good_and_bad(engine):
    seen = set()
    for day in ("1240-05-23", "1240-05-25", "1240-05-26", "1240-09-18", "1240-10-05", "1240-01-04"):
        for planet, row in _condition_table(engine, day).items():
            net = row["Net"]
            expected = "Indeterminate" if net == 0 else ("Good" if net > 0 else "Bad")
            assert row["Condition"] == expected, (day, planet, net, row["Condition"])
            seen.add(expected)
    assert seen == {"Indeterminate", "Good", "Bad"}, seen


def test_the_default_chart_has_a_tie_and_it_reads_indeterminate(engine):
    table = _condition_table(engine, "1240-05-23")
    ties = [p for p, r in table.items() if r["Net"] == 0]
    assert ties, {p: r["Net"] for p, r in table.items()}
    assert all(table[p]["Condition"] == "Indeterminate" for p in ties), ties
