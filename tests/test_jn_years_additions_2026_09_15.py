"""Abu 'Ali's additions and subtractions to the house-master's years (JN
Ch. 4, second half; fn 27-28), DISPLAY ONLY at the supplement depth: every
quoted sentence verbatim in the photographed pages (Abu Bakr I.15 and 'Umar
I.4.4 as witnesses); a fortune's trine adds its lesser years at three
undecided grades, none defaulting to years; a bad one's square subtracts;
a fortune's square and a bad one's trine are the chapter's explicit zero with
the witnesses' different conditions beside; Mercury by fn 28 labelled a
conjecture, his four cases printed as ruled; the Sun's row 'Umar's and the
Moon's Abu Bakr's, always present; a planet in aversion gets no row; no sum
anywhere."""
import re
from pathlib import Path

import pytest

from conftest import assert_no_exception, make_app
from test_doctrine_fixtures import _sahl_chart
from test_years_ladder_2026_09_15 import PN1, PN2, _prose


# Ch. 4 runs from its heading on p. 235 to the p. 236 marker (p. 236 is Ch. 5;
# the file now carries Masha'allah III.1.8 before Abu 'Ali, so that heading
# no longer bounds the span).
JN_CH4 = ("### Chapter 4: How much the stars would add", "*[PN I p. 236]*")


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
    start, end = "[4.4: *Adding to and subtracting", "*[PN II p. 17]*"
    return _prose(PN2, start, end) + " " + _footnotes(PN2, start, end)


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
    assert set(by) == {'Jupiter', 'Saturn', 'Mars', 'Moon'}      # the Moon's row is always present (in aversion here)
    j = by['Jupiter']
    assert (j['aspect'], j['effect'], j['lesser_years']) == ('trine', 'adds', 12)
    assert [(text, n, unit) for text, n, unit in j['grades']] == [
        ("its own lesser years", 12, "years"),
        ("if [the fortune] were middling in strength, [it will give] so many months", 12, "months"),
        ("if it were more unsound, days or hours", 12, "days or hours")]
    assert j['sentence'] == engine["JN_CH4_SENTENCES"]['fortune']
    assert j['reading'] == "12 years; if middling, 12 months; if more unsound, 12 days or 12 hours -- strength grade not determined here"
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
    assert words['Jupiter']['Grade'].startswith("not determined")
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
    assert (m['aspect'], m['effect'], m['lesser_years'], m['grades'], m['literal']) == ('sextile', 'adds', 20, None, 'adds')
    assert m['reading'] == "Dykes fn 28 (conjectural interpretation): with or aspecting Venus, himself sextile to the house-master -- adds 20 years"
    assert m['sentence'] == engine["JN_CH4_SENTENCES"]['mercury']
    assert m['witnesses'] == engine["JN_CH4_WITNESSES"]['mercury']
    rows = {r['planet']: r for r in _rows(engine, "Sun", Sun=135.0, Mercury=225.0, Saturn=230.0, Venus=15.0, Jupiter=15.0, Mars=15.0)}
    assert (rows['Mercury']['aspect'], rows['Mercury']['effect'], rows['Mercury']['literal']) == ('square', 'subtracts', 'subtracts')
    assert 'Saturn' in rows['Mercury']['reading'] and rows['Mercury']['reading'].endswith("subtracts 20 years")
    # the house-master itself is not Mercury's company: Venus as house-master, Mercury sextile her, no other fortune
    rows = {r['planet']: r for r in _rows(engine, "Venus", Venus=135.0, Mercury=190.0, Sun=100.0, Jupiter=345.0, Saturn=345.0, Mars=345.0)}
    assert (rows['Mercury']['effect'], rows['Mercury']['literal']) == ('not specified', None)


def _mercury(engine, **planets):
    data, _ = _sahl_chart(215.0, **planets)
    words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Sun", data)}
    return {r['planet']: r for r in engine["evaluate_jn_years_additions"]("Sun", data)}['Mercury'], words['Mercury']


def test_mercurys_four_cases_as_ruled(engine):
    """The Sun as house-master at 15 Leo. (1) Mercury at 10 Scorpio with
    Venus at 20 Scorpio, himself SQUARE the Sun: a pairing fn 28 does not
    state -- not decided under it, the sentence's literal reading (+20)
    beside. (2) Mercury at 10 Aries with Saturn at 20 Aries, himself TRINE
    the Sun: likewise, the literal reading -20. (3) Mercury at 10 Libra,
    the four in aversion to him: not specified, not an explicit zero.
    (4) Mercury at 10 Libra with Venus and Saturn there: mixed
    associations, unresolved. The 'Ch. 4' cell carries the fn 28 label in
    every case; Abu Bakr's Mercury sentence is the witness in every case.
    Joined to the house-master with a fortune is the unstated pairing too."""
    far = dict(Jupiter=345.0, Saturn=345.0, Mars=345.0, Venus=345.0)     # Pisces: averse to Aries and to Libra
    r, w = _mercury(engine, Sun=135.0, Mercury=220.0, Venus=230.0, Jupiter=75.0, Saturn=75.0, Mars=75.0)  # Gemini: averse to Scorpio
    assert (r['aspect'], r['effect'], r['literal']) == ('square', 'not decided', 'adds')
    assert w['Reading'] == ("not decided under fn 28: this pairing is unstated · Abu 'Ali's sentence read literally: adds 20 years "
                            "(if the fortune is one 'which add[s]')")
    r, w = _mercury(engine, Sun=135.0, Mercury=10.0, **{**far, 'Saturn': 20.0})
    assert (r['aspect'], r['effect'], r['literal']) == ('trine', 'not decided', 'subtracts')
    assert w['Reading'] == "not decided under fn 28: this pairing is unstated · Abu 'Ali's sentence read literally: subtracts 20 years"
    r, w = _mercury(engine, Sun=135.0, Mercury=190.0, **far)
    assert (r['aspect'], r['effect'], r['literal']) == ('sextile', 'not specified', None)
    assert w['Reading'] == "not specified; not an explicit zero"
    r, w = _mercury(engine, Sun=135.0, Mercury=190.0, **{**far, 'Venus': 195.0, 'Saturn': 200.0})
    assert (r['aspect'], r['effect'], r['literal']) == ('sextile', 'unresolved', None)
    assert w['Reading'] == "mixed associations: authorial result unresolved"
    assert w['Ch. 4'].startswith("Dykes fn 28: conjectural interpretation")
    assert w['Witnesses'] == engine["JN_CH4_WITNESSES"]['mercury']
    assert "not to be said about Mercury" in w['Witnesses'] and "increase the evil and misfortune" in w['Witnesses']
    assert w['Grade'] == "-" and w['Its own lesser years'] == "-"
    r, w = _mercury(engine, Sun=135.0, Mercury=140.0, **{**far, 'Venus': 145.0})
    assert (r['aspect'], r['effect'], r['literal']) == ('joined', 'not decided', 'adds')
    assert w['Reading'].startswith("not decided under fn 28") and w['Reading'].endswith("(if the fortune is one 'which add[s]')")


def test_the_zero_rows_print_the_explicit_zero_and_the_witnesses(engine):
    """Venus at 20 Scorpio squares the Sun at 15 Leo; Mars at 0 Aries
    trines him: Abu 'Ali's express zero in the 'Reading' cell, and beside
    it what 'Umar and Abu Bakr say of the same case, each with his own
    condition, in the 'Witnesses' cell."""
    data, _ = _sahl_chart(215.0, Sun=135.0, Venus=230.0, Mars=0.0, Jupiter=290.0, Saturn=290.0, Mercury=290.0, Moon=290.0)
    words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Sun", data)}
    for planet in ('Venus', 'Mars'):
        assert words[planet]['Ch. 4'] == "adds or subtracts nothing"
        assert words[planet]['Reading'] == "0 -- explicitly neither adds nor subtracts (Abu 'Ali, Ch. 4)"
        assert (words[planet]['Its own lesser years'], words[planet]['Grade']) == ("-", "-")
    assert words['Venus']['Witnesses'] == "'Umar I.4.4: adds its lesser years if not retrograde, burned up or impeded"
    assert words['Mars']['Witnesses'] == ("Abu Bakr I.15: adds its lesser years from a good place (to the significator of "
                                          "life, his term) · 'Umar I.4.4: subtracts if it seizes the house-master without a "
                                          "fortune's aspect (fn 87 reads 'seized' as besieged)")
    assert "significator of life" in words['Mars']['Witnesses']
    rows = {r['planet']: r for r in engine["evaluate_jn_years_additions"]("Sun", data)}
    assert rows['Venus']['effect'] == rows['Mars']['effect'] == 'nothing'
    assert rows['Venus']['sentence'] == rows['Mars']['sentence'] == engine["JN_CH4_ADDITIONS"]


def test_a_fortune_row_reads_at_three_grades_and_no_grade_defaults_to_years(engine):
    """Jupiter trine (12), Venus joined (8): the 'Reading' cell prints the
    count at all three grades and says the grade is not determined; the
    'Grade' column never reads "years"; 'Umar's months for a retrograde
    or burned fortune stand beside as his."""
    data, _ = _sahl_chart(215.0, Sun=135.0, Jupiter=250.0, Venus=140.0, Saturn=290.0, Mars=290.0, Mercury=290.0, Moon=290.0)
    words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Sun", data)}
    assert words['Jupiter']['Reading'] == "12 years; if middling, 12 months; if more unsound, 12 days or 12 hours -- strength grade not determined here"
    assert words['Venus']['Reading'] == "8 years; if middling, 8 months; if more unsound, 8 days or 8 hours -- strength grade not determined here"
    for planet in ('Jupiter', 'Venus'):
        assert words[planet]['Grade'].startswith("not determined") and "years" not in words[planet]['Grade']
        assert words[planet]['Witnesses'] == "'Umar I.4.4: months if retrograde or burned up"
    assert not any(r['Grade'] == "years" or r['Grade'].startswith("years") for r in words.values())


def test_the_sun_row_is_umars_in_each_of_his_cases_and_the_moons_abu_bakrs(engine):
    """Jupiter as house-master at 10 Sagittarius. The Sun by whole sign:
    at 15 Pisces square, at 15 Gemini opposite, at 15 Sagittarius joined
    -- 'Umar subtracts 19, with reception months or days (no unit); at 15
    Aries trine, at 15 Libra sextile -- adds 19; at 15 Capricorn, in
    aversion -- none of his cases. Attributed to 'Umar in the cell, never
    to Abu 'Ali; 'Ch. 4' says the chapter gives no luminary modifier. The
    Moon at 15 Gemini, opposite: the same 'Ch. 4' cell, Abu Bakr's
    sentence as witness, 'not specified'."""
    def sun(lon):
        data, _ = _sahl_chart(215.0, Jupiter=250.0, Sun=lon, Moon=75.0, Venus=290.0, Saturn=290.0, Mars=290.0, Mercury=290.0)
        words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Jupiter", data)}
        rows = {r['planet']: r for r in engine["evaluate_jn_years_additions"]("Jupiter", data)}
        return rows['Sun'], words['Sun'], words['Moon']
    for lon, aspect in ((345.0, 'square'), (75.0, 'opposition'), (255.0, 'joined')):
        r, w, _ = sun(lon)
        assert (r['aspect'], r['umar'], r['lesser_years']) == (aspect, 'subtracts', 19)
        assert w['Looks at the house-master'] == f"{aspect} (whole sign)"
        assert w['Reading'] == f"'Umar: subtracts 19 years ({aspect}); with reception, months or days (no unit chosen) -- reception not tested here"
    for lon, aspect in ((15.0, 'trine'), (195.0, 'sextile')):
        r, w, _ = sun(lon)
        assert (r['aspect'], r['umar']) == (aspect, 'adds')
        assert w['Reading'] == f"'Umar: adds 19 years ({aspect})"
    r, w, moon = sun(285.0)
    assert (r['aspect'], r['umar']) == (None, None)
    assert w['Looks at the house-master'] == "in aversion (whole sign)"
    assert w['Reading'] == "'Umar: none of his cases applies (in aversion)"
    assert w['Ch. 4'] == "no explicit luminary modifier specified here"
    assert w['Witnesses'] == ("'Umar I.4.4: subtracts his lesser years by conjunction, square or opposition; adds them by "
                              "trine or sextile; with reception in those three, months or days (no unit chosen) -- the 19 "
                              "is Ch. 4's table reused")
    assert "Abu 'Ali" not in w['Reading'] and "Abu 'Ali" not in w['Witnesses']
    assert (w['Its own lesser years'], w['Grade']) == ("-", "-")
    assert r['effect'] == 'not specified' and r['sentence'] == "no explicit luminary modifier specified here"
    assert moon['Ch. 4'] == "no explicit luminary modifier specified here" and moon['Reading'] == "not specified"
    assert moon['Looks at the house-master'] == "opposition (whole sign)"
    assert moon['Witnesses'] == ("Abu Bakr I.15: made unfortunate, the luminaries destroy and add to the infortunes in evil; "
                                 "in their dignity or with fortunes they remove evil (the antecedent of 'it' unclear as printed)")
    assert "kadukhudhāh" not in moon['Witnesses']     # fn 618's sentence is not used


def test_no_witness_condition_gates_a_row_of_abu_alis(engine):
    """Rows stating Abu 'Ali are decided by the whole-sign look alone; the
    witnesses' conditions (retrograde, burned up, impeded, under the rays,
    reception, binding, a good place, seizure) live in the 'Witnesses'
    cell and in no other."""
    import ast, inspect
    src = inspect.getsource(engine["evaluate_jn_years_additions"])
    body = src[:src.index("# The luminaries, out of the loop")]
    for word in ("retro", "burn", "impeded", "rays", "reception", "binding", "good place", "seiz"):
        assert word not in body.replace("JN_CH4_WITNESSES", ""), word
    data, _ = _sahl_chart(215.0, Sun=135.0, Jupiter=250.0, Venus=230.0, Saturn=215.0, Mars=0.0, Mercury=290.0, Moon=290.0)
    words = {r['Planet']: r for r in engine["jn_years_additions_rows"]("Sun", data)}
    assert words['Saturn']['Witnesses'] == "-" and words['Saturn']['Reading'] == "the chapter's sentence"
    for planet in ('Jupiter', 'Venus', 'Mars'):
        assert "'Umar" not in words[planet]['Reading'] and "Abu Bakr" not in words[planet]['Reading']
        assert "'Umar" in words[planet]['Witnesses']


def test_no_house_master_no_rows_and_the_luminaries_always_have_theirs(engine):
    """Jupiter as house-master at 10 Sagittarius, the four in aversion to
    him: no planet row, but the Sun's and the Moon's rows all the same
    (the Sun at 10 Leo trine, the Moon at 10 Libra sextile). A luminary
    that is itself the house-master has no row."""
    assert engine["evaluate_jn_years_additions"](None, {}) == []
    rows = _rows(engine, "Jupiter", Jupiter=250.0, Sun=130.0, Moon=190.0, Venus=290.0, Saturn=290.0, Mars=290.0, Mercury=290.0)
    assert [r['planet'] for r in rows] == ['Sun', 'Moon']
    assert rows[0]['reading'] == "'Umar: adds 19 years (trine)" and rows[1]['aspect'] == 'sextile'
    rows = _rows(engine, "Sun", Sun=135.0, Moon=190.0, Jupiter=290.0, Venus=290.0, Saturn=290.0, Mars=290.0, Mercury=290.0)
    assert [r['planet'] for r in rows] == ['Moon']
    rows = _rows(engine, "Moon", Moon=135.0, Sun=190.0, Jupiter=290.0, Venus=290.0, Saturn=290.0, Mars=290.0, Mercury=290.0)
    assert [r['planet'] for r in rows] == ['Sun']


def test_the_note_declares_the_conjecture_and_the_conventions(engine):
    note = engine["JN_CH4_ADDITIONS_NOTE"]
    for phrase in ("conjectural", "implementation conventions", "explicitly contribute zero", "none defaults to years",
                   "no explicit numerical lunar modifier", "gate no row of Abu 'Ali's", "or were with it in one sign",
                   "in one sign or in any whole-sign aspect, as fn 28 has \"with or in aspect to\""):
        assert phrase in note, phrase
    assert "\u201c" not in note and "\u201d" not in note and "\u2019" not in note
    for s in list(engine["JN_CH4_WITNESSES"].values()) + [engine["JN_CH4_ZERO"], engine["JN_CH4_NO_LUMINARY"], engine["JN_CH4_FN28_LABEL"]]:
        assert not re.search(r"2026-\d\d-\d\d|\.md\b|Lesson|Handy Tables|Course Glossary", s), s


def _timing_text(date, depth):
    """The releaser page's text (the Releaser tab of the Timing page until
    2026-09-17; the name stays with the callers)."""
    at = make_app(date=date, page="releaser")
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"releaser {date} under {depth}")
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
            assert "no total is formed" in text and "conjectural interpretations" in text
            assert "no explicit numerical lunar modifier" in text
