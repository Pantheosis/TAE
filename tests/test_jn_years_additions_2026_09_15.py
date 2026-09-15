"""Abu 'Ali's additions and subtractions to the house-master's years (JN
Ch. 4, second half; fn 27-28), DISPLAY ONLY at the supplement depth: every
quoted sentence verbatim in the photographed pages (Abu Bakr I.15 and 'Umar
I.4.4 as witnesses); a fortune's trine adds its lesser years at three
undecided grades; a bad one's square subtracts; Mercury by fn 28 marked as
Dykes's reading; a planet in aversion gets no row; no sum anywhere."""
import re
from pathlib import Path

import pytest

from conftest import assert_no_exception, make_app
from test_doctrine_fixtures import _sahl_chart
from test_years_ladder_2026_09_15 import PN1, PN2, _prose


JN_CH4 = ("### Chapter 4: How much the stars would add", "### Chapter III.1.8")


def _footnotes(path, start, end):
    """The footnote lines of a photographed span as prose, cleaned as _prose cleans."""
    if not path.exists():
        pytest.skip("corpus file not in hand")
    text = path.read_text(encoding="utf-8")
    span = text[text.index(start):text.index(end)]
    notes = [re.sub(r"^<sup>\d+</sup> ", "", ln) for ln in span.splitlines() if ln.startswith("<sup>")]
    return re.sub(r"\s+", " ", " ".join(notes).replace("*", ""))


@pytest.fixture(scope="module")
def jn_span():
    return _prose(PN1, *JN_CH4) + " " + _footnotes(PN1, *JN_CH4)


@pytest.fixture(scope="module")
def abu_bakr_span():
    return _prose(PN2, "*[PN II p. 129]*", "*[PN II p. 133]*")


@pytest.fixture(scope="module")
def tbn_span():
    return _prose(PN2, "[4.4: *Adding to and subtracting", "*[PN II p. 17]*")


def test_the_chapter_and_its_footnotes_are_verbatim(engine, jn_span):
    for key, sentence in engine["JN_CH4_SENTENCES"].items():
        assert sentence in jn_span, key
    for text, _ in engine["JN_CH4_GRADES"]:
        assert text in jn_span, text
    assert engine["JN_CH4_SENTENCES"]["nothing"] == engine["JN_CH4_ADDITIONS"]


def test_the_witnesses_are_verbatim(engine, abu_bakr_span, tbn_span, jn_span):
    for key, sentence in engine["ABU_BAKR_I15_ADDITIONS"].items():
        assert sentence in abu_bakr_span, key
    for key, sentence in engine["TBN_I44_ADDITIONS"].items():
        assert sentence in tbn_span, key
    for quote in re.findall(r'"([^"]+)"', engine["JN_CH4_ADDITIONS_NOTE"]):
        assert quote in tbn_span or quote in jn_span, quote


def test_page_strings_carry_no_course_citation(engine):
    for s in (engine["JN_CH4_ADDITIONS_NOTE"], engine["JN_CH4_ADDITIONS_CITATION"]):
        assert "Lesson" not in s and "Handy Tables" not in s and "Course Glossary" not in s
        assert not re.search(r"2026-\d\d-\d\d|\.md\b", s)
    assert "this app" in engine["JN_CH4_ADDITIONS_NOTE"]


def _rows(engine, house_master, **planets):
    """Scorpio rising, the cusps equal the signs (as the 1.20 fixtures)."""
    data, _ = _sahl_chart(215.0, **planets)
    return engine["evaluate_jn_years_additions"](house_master, data)


def test_a_fortunes_trine_adds_at_three_undecided_grades(engine):
    """The Sun as house-master at 15 Leo; Jupiter at 10 Sagittarius trines
    him by whole sign: "it will add its own lesser years" -- 12, and 12
    months, and 12 days or hours, no grade chosen. Saturn at 5 Scorpio
    squares him: "it will subtract its own lesser years" -- 30. Venus at
    20 Capricorn is in aversion: no row. Mars at 0 Aries trines: a bad
    one's trine "make[s] no addition nor diminution"."""
    rows = _rows(engine, "Sun", Sun=135.0, Jupiter=250.0, Saturn=215.0, Venus=290.0, Mars=0.0, Mercury=290.0, Moon=290.0)
    by = {r['planet']: r for r in rows}
    assert set(by) == {'Jupiter', 'Saturn', 'Mars'}
    j = by['Jupiter']
    assert (j['aspect'], j['effect'], j['lesser_years']) == ('trine', 'adds', 12)
    assert [(text, n, unit) for text, n, unit in j['grades']] == [
        ("its own lesser years", 12, "years"),
        ("if [the fortune] were middling in strength, [it will give] so many months", 12, "months"),
        ("if it were more unsound, days or hours", 12, "days or hours")]
    assert j['sentence'] == engine["JN_CH4_SENTENCES"]['fortune'] and j['reading'] is None
    s = by['Saturn']
    assert (s['aspect'], s['effect'], s['lesser_years'], s['grades']) == ('square', 'subtracts', 30, None)
    assert s['sentence'] == engine["JN_CH4_SENTENCES"]['infortune']
    assert (by['Mars']['effect'], by['Mars']['sentence']) == ('nothing', engine["JN_CH4_ADDITIONS"])
    # in words: the count at each grade, and the grade said to be undecided
    data, _ = _sahl_chart(215.0, Sun=135.0, Jupiter=250.0, Saturn=215.0, Venus=290.0, Mars=0.0, Mercury=290.0, Moon=290.0)
    words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Sun", data)}
    assert words['Jupiter']['Ch. 4'] == "adds its lesser years (12)"
    assert (words['Jupiter']['Its own lesser years'], words['Jupiter']['If middling in strength'],
            words['Jupiter']['If more unsound']) == ("12 years", "12 months", "12 days or hours")
    assert words['Jupiter']['Grade'].startswith("not decided")
    assert words['Saturn']['Ch. 4'] == "subtracts its lesser years (30)" and words['Saturn']['If middling in strength'] == "-"
    assert words['Mars']['Ch. 4'] == "adds or subtracts nothing"
    assert not any('sum' in r['Ch. 4'] for r in words.values())


def test_a_fortune_joined_adds_and_its_square_adds_nothing(engine):
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Venus=140.0, Jupiter=45.0, Saturn=290.0, Mars=290.0, Mercury=290.0)}
    assert (rows['Venus']['aspect'], rows['Venus']['effect'], rows['Venus']['lesser_years']) == ('joined', 'adds', 8)
    assert (rows['Jupiter']['aspect'], rows['Jupiter']['effect']) == ('square', 'nothing')
    assert 'Saturn' not in rows and 'Mars' not in rows and 'Mercury' not in rows


def test_mercury_by_fn_28_is_dykess_reading(engine):
    """Mercury at 10 Libra with Venus at 20 Libra, himself sextile the Sun
    at 15 Leo: fn 28's "with or in aspect to a benefic, and he himself ...
    in a sextile or trine" -- adds his lesser years, 20, as Dykes's reading.
    With Saturn instead and square: subtracts. In neither company, or
    joined to the house-master: not decided."""
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Mercury=190.0, Venus=200.0, Jupiter=345.0, Saturn=345.0, Mars=345.0)}
    m = rows['Mercury']
    assert (m['aspect'], m['effect'], m['lesser_years'], m['grades']) == ('sextile', 'adds', 20, None)
    assert m['reading'].startswith("Dykes's reading (fn 28)") and 'Venus' in m['reading']
    assert m['sentence'] == engine["JN_CH4_SENTENCES"]['mercury']
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Mercury=225.0, Saturn=230.0, Venus=15.0, Jupiter=15.0, Mars=15.0)}
    assert (rows['Mercury']['aspect'], rows['Mercury']['effect']) == ('square', 'subtracts')
    assert 'Saturn' in rows['Mercury']['reading']
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Mercury=190.0, Venus=345.0, Jupiter=345.0, Saturn=345.0, Mars=345.0)}
    assert rows['Mercury']['effect'] == 'not decided' and 'neither' in rows['Mercury']['reading']
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Mercury=140.0, Venus=200.0, Jupiter=345.0, Saturn=345.0, Mars=345.0)}
    assert (rows['Mercury']['aspect'], rows['Mercury']['effect']) == ('joined', 'not decided')
    # the house-master itself is not Mercury's company: Venus as house-master, Mercury sextile her, no other fortune
    rows = {r['planet']: r for r in _rows(engine, "Venus", Venus=135.0, Mercury=190.0, Sun=100.0, Jupiter=345.0, Saturn=345.0, Mars=345.0)}
    assert rows['Mercury']['effect'] == 'not decided'


def test_no_house_master_no_rows_and_the_luminaries_have_none(engine):
    assert engine["evaluate_jn_years_additions"](None, {}) == []
    rows = _rows(engine, "Jupiter", Jupiter=250.0, Sun=130.0, Moon=190.0, Venus=290.0, Saturn=290.0, Mars=290.0, Mercury=290.0)
    assert [r['planet'] for r in rows] == []


def _timing_text(date, depth):
    at = make_app(date=date, page="timing")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"timing {date} under {depth}")
    text = " ".join(n.value for n in at.main.markdown) + " " + " ".join(n.value for n in at.main.caption)
    return text + " " + " ".join(n.value for n in at.main.subheader)


def test_the_finding_renders_at_the_supplement_depth_only():
    title = "Additions and subtractions to the house-master's years (Abu 'Ali)"
    for depth, shown in (("Course text", False), ("Course text and supplement", True)):
        text = _timing_text("1240-05-23", depth)
        assert "The house-master's years" in text
        assert (title in text) == shown, depth
        if shown:
            assert "Abu 'Ali, Judgments of Nativities Ch. 4 (fn 27-28), with Abu Bakr I.15 and 'Umar, TBN I.4.4" in text
            assert "no sum is formed" in text
