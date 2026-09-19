"""Abu 'Ali's years ladder (JN Ch. 3-4, with 'Umar TBN I.4.3) as the
supplement fallback where Sahl 1.20 is silent (reconciliation decision 9):
every quoted sentence verbatim in the photographed pages; Sahl's grade never
overridden; the JN class what Ch. 3 says for the place and condition; the
1240 chart's Releaser tab renders at the supplement depth."""
import re
from pathlib import Path

import pytest

from conftest import assert_no_exception, make_app
from corpus_paths import CORPUS_DIR as CORPUS
from test_doctrine_fixtures import _sahl_chart

PN1 = CORPUS / "pn1" / "pn1_photographed.md"
PN2 = CORPUS / "pn2" / "pn2_photographed.md"
SAHL = CORPUS / "on_nativities.md"


def _prose(path, start, end):
    """A span of a photographed file as running prose: footnote lines, page
    markers and rules dropped, footnote superscripts removed (an ordinal's
    "th" kept), italics markers and HTML entities removed, whitespace
    collapsed."""
    if not path.exists():
        pytest.skip("corpus file not in hand")
    text = path.read_text(encoding="utf-8")
    span = text[text.index(start):text.index(end)]
    lines = [ln for ln in span.splitlines()
             if not ln.startswith("<sup>") and not ln.startswith("*[") and ln.strip() != "---"]
    prose = " ".join(lines)
    prose = re.sub(r"<sup>\d+</sup>", "", prose)
    prose = re.sub(r"</?sup>", "", prose).replace("*", "").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", prose)


@pytest.fixture(scope="module")
def jn_span():
    return _prose(PN1, "*[PN I p. 233]*", "*[PN I p. 236]*")


@pytest.fixture(scope="module")
def tbn_span():
    return _prose(PN2, "*[PN II p. 13]*", "*[PN II p. 16]*")


def test_the_ladder_is_verbatim_in_jn_ch_3_and_4(engine, jn_span):
    ladder = engine["JN_YEARS_LADDER"]
    assert [r[0] for r in ladder['places']] == ['angle', 'succedent', 'cadent']
    assert [r[1] for r in ladder['places']] == ['greater', 'middle', 'lesser']
    for _, _, sentence in ladder['places']:
        assert sentence in jn_span, sentence
    assert ladder['preface'] in jn_span
    assert [d[0] for d in ladder['demotions']] == ['not oriental', 'occidental and peregrine',
                                                    'occidental, peregrine, retrograde and burned up', 'one rule']
    for _, sentence in ladder['demotions']:
        assert sentence in jn_span, sentence
    assert ladder['ranks'] == ('greater', 'middle', 'lesser', 'months', 'days')
    assert engine["JN_CH4_ADDITIONS"] in jn_span
    # Ch. 4's table, row by row
    for planet, (g, m, l) in engine["JN_YEARS_TABLE"].items():
        def cell(v):
            return f"{int(v)} ½" if v != int(v) else str(int(v))
        assert re.search(rf"\| {planet}\s+\| {re.escape(cell(g))}\s+\| {re.escape(cell(m))}\s+\| {re.escape(cell(l))}\s+\|", jn_span), planet
    assert engine["JN_YEARS_TABLE_DIFFERS"] == {'Sun': (69.5, 39.5), 'Moon': (66.5, 39.5)}


def test_umar_and_sahl_are_verbatim(engine, tbn_span):
    assert engine["TBN_YEARS_RULE"] in tbn_span
    for key, note in engine["TBN_YEARS_DIFFERENCES"].items():
        for quote in re.findall(r'"([^"]+)"', note):
            assert quote in tbn_span, (key, quote)
    if SAHL.exists():
        sahl = SAHL.read_text(encoding="utf-8").replace("&lt;", "<").replace("&gt;", ">")
        assert engine["SAHL_1_21_8"] in re.sub(r"\s+", " ", sahl)
    for s in (engine["JN_YEARS_NOTE"], engine["JN_YEARS_CITATION"]):
        assert "Lesson" not in s and "Handy Tables" not in s and "Course Glossary" not in s
    assert engine["JN_CH4_ADDITIONS"] in engine["JN_YEARS_NOTE"] and engine["SAHL_1_21_8"] in engine["JN_YEARS_NOTE"]


def _both(engine, planet, sect="Nocturnal", **planets):
    """Scorpio rising, the cusps equal the signs (as the 1.20 fixtures)."""
    data, cusps = _sahl_chart(215.0, **{k: (v[0] if isinstance(v, tuple) else v) for k, v in planets.items()})
    for k, v in planets.items():
        if isinstance(v, tuple):
            data[k]['speed_in_lon'] = v[1]
    ess = engine["evaluate_essential_dignities"](data, sect)
    return (engine["sahl_house_master_years"](planet, data, cusps, sect, ess),
            engine["jn_years_fallback"](planet, data, cusps, sect, ess))


def test_where_sahl_grades_the_fallback_is_none(engine):
    """1.20, 10: Jupiter at 15 Taurus (the seventh, his own bound), eastern
    of a Sun at 10 Gemini, direct, not under the rays -- the greater years.
    Sahl grades, so the ladder is not consulted."""
    g, j = _both(engine, "Jupiter", Jupiter=45.0, Sun=70.0)
    assert (g["grade"], g["sentence"]) == ("greater", "1.20, 10") and j is None
    # 28: a falling place Sahl grades outright (Jupiter at 15 Aries, the sixth)
    g, j = _both(engine, "Jupiter", Jupiter=15.0, Sun=70.0)
    assert g["sentence"] == "1.20, 28" and j is None


def test_where_sahl_is_silent_the_class_is_ch_3s_for_the_place(engine):
    """The same Jupiter at 15 Taurus RETROGRADE and not under the rays: no
    sentence of 1.20, 10-34 reaches a retrograde unburned stake (21 wants
    burning, 20 wants direct) -- "1.20 silent". Ch. 3: an angle is the
    greater years; one impediment (retrograde) steps it to the middle,
    45 1/2, Ch. 4's table."""
    g, j = _both(engine, "Jupiter", Jupiter=(45.0, -0.1), Sun=70.0)
    assert g["grade"] is None and g["text"].startswith("1.20 silent")
    assert (j["place"], j["class"], j["count"], j["unit"], j["division"]) == ("angle", "middle", 45.5, "years", 7)
    assert [s for s, _ in j["steps"]] == ["retrograde"]
    assert j["jn"] == engine["JN_YEARS_LADDER"]["places"][0][2]
    assert j["citation"] == "Abu 'Ali, Judgments of Nativities Ch. 3 (with 'Umar, TBN I.4.3)"
    assert j["umar"] == [engine["TBN_YEARS_DIFFERENCES"]["angle"]]
    # A cadent place: Saturn at 15 Cancer (the ninth, no share), eastern of a
    # Sun at 10 Leo, direct -- 26 wants a share, 27 wants neither share nor
    # easternization: silent. Ch. 3: the cadents are the lesser years; peregrine
    # steps them to months, the lesser years' number (30).
    g, j = _both(engine, "Saturn", Saturn=105.0, Sun=130.0)
    assert g["grade"] is None
    assert (j["place"], j["class"], j["count"], j["unit"]) == ("cadent", "months", 30, "months")
    assert [s for s, _ in j["steps"]] == ["peregrine"]
    # A follower with every condition met by day: Jupiter at 15 Pisces (the
    # fifth, his domicile), eastern, direct, unburned -- 11's parenthesis
    # is by night only, so 1.20 is silent by day. Ch. 3: the middle years, no step.
    g, j = _both(engine, "Jupiter", "Diurnal", Jupiter=345.0, Sun=20.0)
    assert g["grade"] is None
    assert (j["place"], j["class"], j["count"], j["steps"]) == ("succedent", "middle", 45.5, [])
    assert j["umar"] == [engine["TBN_YEARS_DIFFERENCES"]["succedent"]]
    # The Sun takes no step for orientality, and Ch. 4's count is printed
    # where it differs: the Sun at 15 Aries in the eleventh (Gemini rising),
    # exalted -- silent (10 wants "eastern"); the middle years, 69 1/2.
    data, cusps = _sahl_chart(75.0, Sun=15.0)
    ess = engine["evaluate_essential_dignities"](data, "Diurnal")
    j = engine["jn_years_fallback"]("Sun", data, cusps, "Diurnal", ess)
    assert (j["class"], j["count"], j["steps"]) == ("middle", 69.5, [])
    assert "69.5" in j["table_note"] and "39.5" in j["table_note"]
    # The Moon's orientality is not borrowed from solar side. In the ninth,
    # eastern reaches Sahl's middle years while not eastern reaches the JN
    # ladder and its two-step days result.
    g, j = _both(engine, "Moon", Moon=105.0, Sun=100.0)
    assert isinstance(g["grade"], engine["UnresolvedResult"])
    assert [(value.number, value.unit) for _, value in j["result"].alternatives] == [(39.5, "years"), (25, "days")]
    west = j["alternative_routes"][1][1]
    assert [s for s, _ in west["steps"]] == ["not oriental", "burned up"]


def test_the_years_table_carries_the_column_at_the_supplement_depth_only(engine):
    from datetime import datetime, timedelta
    dt = datetime(1240, 5, 23, 14, 30) - timedelta(hours=11.2463 / 15.0)
    c = engine["calculate_traditional_chart"](dt, 43.7792, 11.2463)
    p, sect = c["planetary_data"], c["sect"]
    ess = engine["evaluate_essential_dignities"](p, sect)
    plain = engine["evaluate_planetary_years_display"](p, c["houses"], c["ascendant"], sect, ess)
    col = "Where 1.20 is silent or conditional: Abu 'Ali, Judgments of Nativities Ch. 3 (with 'Umar, TBN I.4.3); the supplement"
    assert all(col not in r for r in plain)
    rows = engine["evaluate_planetary_years_display"](p, c["houses"], c["ascendant"], sect, ess, supplement=True)
    for r in rows:
        grant = r["On Nativities 1.20 grants (as house-master)"]
        needs_fallback = grant == "1.20 silent" or isinstance(grant, engine["UnresolvedResult"])
        assert (r[col] != "-") == needs_fallback, r
        if needs_fallback and not isinstance(r[col], engine["UnresolvedResult"]):
            assert r[col].split(",")[0].split(" ")[0] in engine["JN_YEARS_LADDER"]["ranks"]


def _timing_text(date, depth):
    """The releaser page's text (the Releaser tab of the Timing page until
    2026-09-17; the name stays with the callers)."""
    at = make_app(date=date, page="releaser")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"releaser {date} under {depth}")
    assert "The releaser" in [h.value for h in at.main.header]
    return " ".join(n.value for n in at.main.markdown) + " " + " ".join(n.value for n in at.main.caption)


def test_the_releaser_tab_renders_at_the_supplement_depth():
    """The 1240-05-23 chart: Jupiter, the house-master, is graded by 1.20, 20,
    so the ladder does not appear at either depth. 1240-02-02 (Florence,
    14:30): the Moon, house-master, is otherwise qualified in the eleventh;
    the page preserves the two lunar-orientality routes."""
    text = _timing_text("1240-05-23", "Course text and supplement")
    assert "The house-master's years" in text and "1.20, 20" in text
    assert "supplement's ladder" not in text
    for depth, shown in (("Course text", False), ("Course text and supplement", True)):
        text = _timing_text("1240-02-02", depth)
        assert "The supplied passages do not define the Moon’s orientality" in text
        assert "the greater years, 108 (Moon)" in text
        assert ("Sahl-first result" in text) == shown, depth
        if shown:
            assert "Abu 'Ali, Judgments of Nativities Ch. 3 (with 'Umar, TBN I.4.3)" in text
            assert "the lesser years, 25 (Moon), succedent by the division (11) -- not oriental (1 step down)" in text
            assert "add or subtract nothing" in text and "withhold years, but will even add" in text
            assert "This ladder is Abu 'Ali's, not Sahl's" in text
