"""Sahl's worked question chart -- On Questions Ch. 1, 53-65, Figures 33-34.

The corpus's only dated, located, fully worked chart, and the one place
Sahl states the positions, the method and the judgments together. Every
assertion here is one of his own sentences, run against the engine on the
longitudes HE gives (¶54), never on positions recomputed from the date:
Figure 34's reconstruction (5 July 824 JC, 03:18:10 LMT, Baghdad) is in a
Sassanian sidereal frame, and recomputing tropically would move every body
by ~3.6 degrees. Whole-sign relations are frame-independent, which is why
literal longitudes are the right input.

    "the Ascendant was Gemini, 20; and the Midheaven Pisces, the first
    degree; and the Sun in Cancer, 12; and the Moon in Virgo, 17; and
    Mercury in Gemini, 27; and Mars in Taurus, 8; and Venus in Leo, 3; and
    Jupiter in Pisces, in 20, stationing toward retrogradation; and Saturn
    in Gemini, in 6." (¶54)

Two provenance notes. ¶61's "stationing toward retrogradation" is a fact
Sahl states, not one derivable from the nine longitudes: it enters as
Jupiter's near-zero speed and is not asserted. ¶65's "Jupiter is with the
Tail" is likewise not derivable from ¶54 -- the nodes are not among his
figures -- so the Tail is hardcoded from Figure 34 (☋ 25 Pisces 46', the
TRUE node; the mean node would be 26 38'), and asserted at sign level only.

The 2026-09-07 bounds correction changes one lordship in this chart --
Saturn at 6 Gemini is now in Jupiter's bound, not Venus's -- and no
judgment Sahl draws touches it. Mercury at 27 Gemini is in Saturn's bound
under both tables.
"""
from __future__ import annotations

import pytest

from test_doctrine_fixtures import MARS, MERC, MOON, SAT, VENUS, pdata

ASC = 80.0            # Gemini 20
MC = 330.0            # Pisces, the first degree
TAIL_FIG34 = 330.0 + 25.0 + 46.0 / 60.0   # ☋ 25 Pisces 46', Figure 34 (true node, Sassanian frame)

# Venus: the manuscript's 3 Leo (¶54) and Figure 34's recomputed 9 Leo 06'
# (retrograde there). Sahl draws no judgment from her, so every test below
# runs at both values and must not notice.
VENUS_MS, VENUS_MODERN = 123.0, 129.1


def sahl_chart(venus=VENUS_MS, mercury=87.0):
    return pdata(Sun=(102.0, 1.0), Moon=(167.0, MOON), Mercury=(mercury, MERC), Mars=(38.0, MARS),
                 Venus=(venus, VENUS), Jupiter=(350.0, 0.001), Saturn=(66.0, SAT))


@pytest.fixture(params=[VENUS_MS, VENUS_MODERN], ids=["venus-ms-3-leo", "venus-modern-9-leo"])
def venus(request):
    return request.param


def _aspect_rows(engine, p):
    return {frozenset((r["Light Planet"], r["Heavy Planet"])): r for r in engine["evaluate_ptolemaic_aspects"](p)}


def test_the_chart_is_nocturnal(engine, venus):
    # The Sun at 12 Cancer is in the second sign from a Gemini Ascendant,
    # below the horizon. Sect is what makes Mars the water triplicity lord
    # in ¶63's reception question.
    assert engine["get_wsh_house"](102.0, ASC) == 2
    assert ((102.0 - ASC) % 360.0) <= 180.0


def test_56_mercury_lord_of_the_ascendant_in_the_ascendant_at_the_end_of_the_sign(engine, venus):
    # "the Ascendant was Gemini, the house of Mercury, and he was in the
    # Ascendant, at the end of the sign" (¶56). "End of the sign" is read as
    # the sign's final bound, the engine's own last-bound test.
    assert engine["get_essential_rulers"](ASC)["domicile"] == "Mercury"
    assert engine["get_wsh_house"](87.0, ASC) == 1
    assert engine["_in_last_bound"](87.0)
    assert engine["get_essential_rulers"](87.0)["term"] == "Saturn"


def test_56_jupiter_lord_of_the_sought_matter_in_the_midheaven(engine, venus):
    # "Jupiter, who was the lord of the house of the sought matter, [was] in
    # the Midheaven, in 20" (¶56): the tenth sign from Gemini is Pisces.
    assert engine["get_essential_rulers"](MC)["domicile"] == "Jupiter"
    assert engine["get_wsh_house"](350.0, ASC) == 10


def test_56_lord_of_the_ascendant_separated_from_the_lord_of_the_sought_matter(engine, venus):
    # "so I found the lord of the Ascendant separated from the lord of the
    # sought matter" (¶56): Mercury at 27 is past the square to 20.
    row = _aspect_rows(engine, sahl_chart(venus))[frozenset(("Mercury", "Jupiter"))]
    assert (row["Aspect"], row["Motion"]) == ("Square", "Separating"), row


def test_57_moon_in_the_stake_of_the_earth(engine, venus):
    # "So I looked at the Moon, and found her in the stake of the earth" (¶57).
    assert engine["get_wsh_house"](167.0, ASC) == 4


def test_57_moon_connecting_with_jupiter_from_an_opposition(engine, venus):
    # "connecting with Jupiter from an opposition: it indicated the
    # attainment of the sought matter with beseeching, in trouble" (¶57).
    # 17 Virgo applying to 20 Pisces: three degrees from exact.
    row = _aspect_rows(engine, sahl_chart(venus))[frozenset(("Moon", "Jupiter"))]
    assert (row["Aspect"], row["Motion"], row["Exact Orb Dist"], row["Connected"]) == \
        ("Opposition", "Applying", "03° 00'", "Yes"), row


def test_63_mercury_shifts_from_his_house_into_the_house_of_assets(engine, venus):
    # "because the lord of the Ascendant was shifting over from his house to
    # the house of assets" (¶63): the next sign, Cancer, is the second.
    assert engine["get_wsh_house"](90.5, ASC) == 2
    assert engine["get_zodiac_sign"](90.5) == "Cancer"


def test_63_on_leaving_mercury_connects_with_mars_who_does_not_accept_him(engine, venus):
    # "when [Mercury] went out from his sign, he was connecting with Mars,
    # and he does not accept [Mercury]" (¶63); fn. 27: "Mercury would be
    # connecting to Mars from the sign of Mars's fall (see 40 above)". Ch. 1,
    # 40's own example is this very pair -- "the lord of the Ascendant is
    # connecting with Mars from Cancer". The engine's name for it is
    # non-reception Kind II (Introduction Ch. 3, 59-60), whose five examples
    # include Cancer -> Mars. Mercury is placed just inside Cancer, within
    # his own 7-degree light of the sextile to Mars at 8 Taurus, since Sahl's
    # connection is by degree.
    p = sahl_chart(venus, mercury=91.5)
    assert "Cancer" in engine["FALLS"]["Mars"]
    with engine["doctrine"](engine["SAHL"]):
        kinds = {(r["Kind"], r["Connecting"], r["With"]) for r in engine["evaluate_non_reception"](p, "Nocturnal")}
    assert ("II (59-60)", "Mercury", "Mars") in kinds, kinds


def test_63_control_the_engine_does_not_also_report_mars_receiving_mercury(engine, venus):
    # Was a strict xfail from 2026-09-07 to 2026-09-08: for the same pair the
    # engine also listed 'Mars receives Mercury via triplicity, bound'
    # (Masha'allah's form, Introduction Ch. 3, 54-55), because Mars is the
    # night triplicity lord of Cancer and holds its first bound. Decision
    # D-2 (synthesis/13_open_decisions.md): refusal wins under Sahl's
    # profile -- his verdict on his own chart is "he does not accept
    # [Mercury]" (Questions Ch. 1, 63), and Ch. 1, 40-41 makes connection
    # from the receiver's fall a refusal. The xfail was un-marked
    # deliberately when evaluate_reception gained the precedence check.
    p = sahl_chart(venus, mercury=91.5)
    with engine["doctrine"](engine["SAHL"]):
        rec = [r for r in engine["evaluate_reception"](p, "Nocturnal")
               if (r.get("Receiver"), r.get("Received")) == ("Mars", "Mercury")]
    assert not rec, rec


def test_65_jupiter_is_with_the_tail(engine, venus):
    # "Jupiter is with the Tail" (¶65). Figure-derived, not prose-derived:
    # Figure 34 puts ☋ at 25 Pisces 46' with Jupiter at 20 Pisces 32'. Same
    # sign is all that is asserted; the Tail is never recomputed.
    assert engine["get_zodiac_sign"](TAIL_FIG34) == engine["get_zodiac_sign"](350.0) == "Pisces"


def test_venus_control_no_judgment_depends_on_her(engine):
    # Negative control. MS Venus 3 Leo and Figure 34's 9 Leo 06' Rx differ by
    # six degrees, and Sahl draws no judgment from Venus. Every aspect row
    # NOT involving Venus must be identical under both values, so nobody can
    # later hang an assertion on her without this test noticing.
    def rows_without_venus(v):
        return {k: (r["Aspect"], r["Motion"], r["Exact Orb Dist"], r["Connected"])
                for k, r in _aspect_rows(engine, sahl_chart(v)).items() if "Venus" not in k}
    assert rows_without_venus(VENUS_MS) == rows_without_venus(VENUS_MODERN)
    assert any("Venus" in k for k in _aspect_rows(engine, sahl_chart(VENUS_MS)))   # she is in the chart, just unused
