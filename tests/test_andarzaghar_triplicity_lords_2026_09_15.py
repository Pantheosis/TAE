"""al-Andarzaghar's triplicity lords of the twelve houses (al-Qabisi
I.57b-68, in ITA I.13, pp. 71-76): twelve entries, every quoted
signification verbatim in the corpus span, and the lords by sect order on
a hand-built chart."""
import re
from pathlib import Path

import pytest

from corpus_paths import corpus_file

ITA = corpus_file("ita/ita_photographed.md")
SPAN_START = "*[ITA p. 71]*"
SPAN_END = "*[ITA pp. 77-111 not photographed]*"


@pytest.fixture(scope="module")
def ita_span():
    """The I.13 span as running prose: footnote markers, footnote lines,
    page markers and rules removed, whitespace collapsed, and the two
    words the page break splits ("be-" / "ginning", p. 71-72) rejoined."""
    if not ITA.exists():
        pytest.skip("corpus file not in hand")
    text = ITA.read_text(encoding="utf-8")
    lo, hi = text.index(SPAN_START), text.index(SPAN_END)
    span = text[lo:hi]
    lines = [ln for ln in span.splitlines()
             if not ln.startswith("<sup>") and not ln.startswith("*[ITA") and ln.strip() != "---"]
    prose = re.sub(r"\s+", " ", re.sub(r"<sup>\d+</sup>", "", " ".join(lines)))
    return re.sub(r"(?<=\w)- (?=\w)", "", prose)


def test_twelve_entries_with_sections(engine):
    table = engine["ANDARZAGHAR_TRIPLICITY_LORDS"]
    assert sorted(table) == list(range(1, 13))
    assert [table[h]['section'] for h in range(1, 13)] == [
        'I.57b', 'I.58', 'I.59', 'I.60', 'I.61', 'I.62', 'I.63', 'I.64', 'I.65', 'I.66', 'I.67', 'I.68']
    for h in range(1, 13):
        assert set(table[h]) == {'section', 'house', 'first', 'second', 'third', 'text'}


def test_every_signification_is_verbatim_in_the_corpus(engine, ita_span):
    table = engine["ANDARZAGHAR_TRIPLICITY_LORDS"]
    for h in range(1, 13):
        for key in ('first', 'second', 'third', 'text'):
            quote = table[h][key]
            assert quote in ita_span, f"house {h} {key!r} is not verbatim: {quote!r}"
    # each house's sentence is where al-Qabisi reports al-Andarzaghar (the
    # first is italicised in the transcription: "*al-Andarzaghar* said")
    assert len(re.findall(r"Andarzaghar\*? said", ita_span)) == 12


def test_lords_by_sect_on_a_hand_built_chart(engine):
    day = engine["evaluate_andarzaghar_triplicity_lords"](0.0, 'Diurnal')
    assert len(day) == 12
    assert list(day[0]) == ['House', 'Sign', 'First lord', 'Second lord', 'Third lord',
                            'Signifies (1st / 2nd / 3rd)', 'Source']
    assert [r['House'] for r in day] == list(range(1, 13))
    assert [r['Sign'] for r in day] == engine["SIGN_ORDER"]
    h1, h4 = day[0], day[3]
    assert (h1['Sign'], h1['First lord'], h1['Second lord'], h1['Third lord']) == ('Aries', 'Sun', 'Jupiter', 'Saturn')
    assert (h4['Sign'], h4['First lord'], h4['Second lord'], h4['Third lord']) == ('Cancer', 'Venus', 'Mars', 'Moon')
    assert h1['Source'] == "al-Qabisi I.57b (al-Andarzaghar), in ITA I.13"
    assert h4['Source'] == "al-Qabisi I.60 (al-Andarzaghar), in ITA I.13"
    assert h4['Signifies (1st / 2nd / 3rd)'] == "fathers / cities and lands / the ends of matters and prisons"

    night = engine["evaluate_andarzaghar_triplicity_lords"](0.0, 'Nocturnal')
    n1, n4 = night[0], night[3]
    assert (n1['First lord'], n1['Second lord'], n1['Third lord']) == ('Jupiter', 'Sun', 'Saturn')
    assert (n4['First lord'], n4['Second lord'], n4['Third lord']) == ('Mars', 'Venus', 'Moon')


def test_houses_are_whole_signs_from_the_ascendant(engine):
    rows = engine["evaluate_andarzaghar_triplicity_lords"](275.5, 'Diurnal')      # 5 Capricorn rising
    assert rows[0]['Sign'] == 'Capricorn'
    assert rows[3]['Sign'] == 'Aries'
    assert rows[11]['Sign'] == 'Sagittarius'
