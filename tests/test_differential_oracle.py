"""Seven pure lookups, pinned against an independently written implementation.

On 2026-09-09 a second implementation of sign, bound lord, face lord,
triplicity lord, dignity scoring, almuten and whole-sign house was written from
a specification by a model that never saw this code, and run over 4,348 inputs.
It agreed with the engine on every one. The fixture here keeps all 348 boundary
probes from that run plus 400 sampled random cases.

The boundary probes are the point. They sit on every Egyptian bound edge
exactly and at +/- 1e-9, on every sign and face edge, and across all 144
ascendant/target sign pairs -- the places a `<` that should be `<=` hides, and
that random longitudes essentially never reach.
"""
import json
import os

import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "differential_oracle.json")
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _cases():
    with open(FIXTURE) as fh:
        return json.load(fh)["cases"]


def _actual(engine, case):
    """Recompute one case from the live engine, in the fixture's shape."""
    lon, sect, asc = case["longitude"], case["sect"], case["ascendant"]
    rulers = engine["get_essential_rulers"](lon)
    weights = engine["ESSENTIAL_DIGNITY_WEIGHTS"]
    triplicity = rulers["triplicity_day"] if sect == "Diurnal" else rulers["triplicity_night"]
    scores = {p: 0 for p in PLANETS}
    for lord, key in ((rulers["domicile"], "domicile"), (rulers["exaltation"], "exaltation"),
                      (triplicity, "triplicity"), (rulers["term"], "term"), (rulers["face"], "face")):
        if lord in scores:
            scores[lord] += weights[key]
    top = max(scores.values())
    winners = [p for p, v in scores.items() if v == top]
    return {
        "sign": rulers["sign"],
        "bound_lord": rulers["term"],
        "face_lord": rulers["face"],
        "triplicity_lord": triplicity,
        "dignity_scores": scores,
        "almuten": winners[0] if len(winners) == 1 else None,
        "whole_sign_house": engine["get_wsh_house"](lon, asc),
    }


@pytest.mark.parametrize("field", ["sign", "bound_lord", "face_lord", "triplicity_lord",
                                   "dignity_scores", "almuten", "whole_sign_house"])
def test_differential_oracle_field(engine, field):
    """Every fixture case still agrees with the independent implementation."""
    bad = []
    for case in _cases():
        got = _actual(engine, case)[field]
        if got != case["expect"][field]:
            bad.append((case["id"], case["longitude"], case["sect"], case["why"],
                        case["expect"][field], got))
    assert not bad, "\n".join(
        f"id={i} lon={lon} sect={sect} [{why}]: expected {exp!r}, got {act!r}"
        for i, lon, sect, why, exp, act in bad[:10])


def test_the_boundary_probes_are_still_in_the_fixture():
    """Guards the fixture itself: a regeneration that dropped the boundary
    cases would leave a suite that passes on random longitudes alone."""
    why = [c["why"] for c in _cases()]
    assert sum(1 for w in why if w == "bound edge exact") == 48
    assert sum(1 for w in why if w == "bound edge minus 1e-9") == 48
    assert sum(1 for w in why if w == "bound edge plus 1e-9") == 48
    assert sum(1 for w in why if w == "wsh grid") == 144
    assert sum(1 for w in why if w != "random") == 348
