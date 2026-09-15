"""Morin's rules for aspects into good and bad houses (Astrologia Gallica
21.II.X, Holden pp. 105-106): the eight rule rows and the display-only
evaluator behind the Chart page's supplement finding."""
from datetime import datetime
from itertools import product

import pytest

# Morin's four governing sentences as the corpus has them (Holden, pp. 105-106).
SENTENCES = (
    "The distinction should be observed, however, that the favorable rays of benefic planets are "
    "more prone to good, and the unfavorable rays are less prone to evil, than is true for the "
    "malefic planets.",
    "Moreover, a benefic planet's favorable rays produce good with ease and in abundance, and cause "
    "good in the fortunate houses as well as prevent or mitigate evil in the unfortunate ones, but "
    "its unfavorable rays bring difficulties, hindrances, or misfortunes to be surmounted.",
    "On the other hand, a malefic planet's malefic rays are extremely harmful, causing evil in the "
    "unfortunate houses and preventing or spoiling the good in the fortunate ones, unless it rules "
    "over the location where the adverse aspect falls, for in that case the aspect produces good in "
    "fortunate houses, but this good will be accompanied by violence, evil, or misfortune.",
    "And again, the favorable rays indicate something good gained by difficult means;",
)
TEXT = " ".join(SENTENCES)


def test_eight_rule_rows_quote_the_text(engine):
    rules = engine["MORIN_ASPECT_RULES"]
    keys = set(product(("Fortune", "Infortune"), ("favorable", "adverse"), ("fortunate", "unfortunate")))
    assert set(rules) == keys and len(rules) == 8
    for key, phrase in rules.items():
        quoted = phrase.split('"')[1]
        # An ellipsis joins two stretches of the same sentence.
        for piece in quoted.split(" ... "):
            assert piece in TEXT, (key, piece)
        if "paraphrase" in phrase:
            assert key[0:2] in (("Fortune", "adverse"), ("Infortune", "favorable"))
    assert engine["MORIN_UNFORTUNATE_HOUSES"] == (6, 8, 12)
    assert set(engine["MORIN_FORTUNATE_HOUSES"]) | {6, 8, 12} == set(range(1, 13))


def test_house_column_is_the_aspected_planets_whole_sign_house(engine):
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    p_data, asc = chart["planetary_data"], chart["ascendant"]
    rows = engine["evaluate_morin_aspects"](p_data, chart["houses"], asc)
    assert rows, "the chart has no aspect from a Fortune or an Infortune"
    assert list(rows[0]) == ["Planet", "Aspect", "To", "House", "Rule"]
    for row in rows:
        caster = row["Planet"].split(" ")[0]
        assert caster in ("Jupiter", "Venus", "Saturn", "Mars")
        house = engine["get_wsh_house"](p_data[row["To"]]["longitude"], asc)
        kind = "unfortunate" if house in (6, 8, 12) else "fortunate"
        assert row["House"] == f"{house} ({kind})"
        aspect, ray = row["Aspect"].rstrip(")").split(" (")
        assert ray == ("favorable" if aspect in ("Trine", "Sextile") else "adverse")
        assert aspect in ("Trine", "Sextile", "Square", "Opposition")
        planet_kind = "Fortune" if caster in ("Jupiter", "Venus") else "Infortune"
        assert row["Rule"] == engine["MORIN_ASPECT_RULES"][(planet_kind, ray, kind)]
    # Every row is a configured pair of the app's own aspect table.
    table = {frozenset((r["Light Planet"], r["Heavy Planet"])): r["Aspect"]
             for r in engine["evaluate_ptolemaic_aspects"](p_data)}
    for row in rows:
        pair = frozenset((row["Planet"].split(" ")[0], row["To"]))
        assert table[pair] == row["Aspect"].split(" ")[0]
