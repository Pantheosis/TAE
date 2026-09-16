"""Mars in his own domicile by the sect of the chart (Abu Bakr, On
Nativities II.1.0, PN II p. 142): the four sentences verbatim in the
photographed page, and the evaluator on hand-built charts -- by night the
soldier, by day the lazy one, in Saturn's domicile the fatty liver, in the
whole-sign tenth the Midheaven sentence as a second row, and one row
saying so when none reaches him."""
from pathlib import Path

import pytest

from corpus_paths import corpus_file
from test_doctrine_fixtures import pdata

PN2 = corpus_file("pn2/pn2_photographed.md")
SOURCE = 'Abu Bakr, On Nativities II.1.0'
COLUMNS = ['Mars', 'Sign', "Chart's sect", 'Case', 'Source', 'Text']


@pytest.fixture(scope="module")
def pn2_page_142():
    if not PN2.exists():
        pytest.skip("corpus file not in hand")
    text = PN2.read_text(encoding="utf-8")
    lo = text.index("*[PN II p. 142]*")
    return text[lo:text.index("*[PN II pp. 143-221 not photographed]*")]


def _mars(lon, sun):
    return pdata(Sun=sun, Moon=(sun + 180.0) % 360.0, Mars=lon)


def test_every_sentence_is_verbatim_in_the_page(engine, pn2_page_142):
    table = engine["ABU_BAKR_MARS_II_1_0"]
    for key in ('Nocturnal', 'Diurnal', 'Saturn', 'Midheaven'):
        assert table[key][1] in pn2_page_142, key
    assert table['Fortune'] in pn2_page_142
    # fn 652 is set in italics in the page; the words are the same
    assert table['fn652'].replace('Insanus', '*Insanus*') in pn2_page_142
    assert table['source'] == SOURCE


def test_mars_in_scorpio_by_night_is_the_soldier(engine):
    # Ascendant 100 (Cancer): Scorpio is the fifth sign, not the tenth
    rows = engine["evaluate_mars_abu_bakr"](_mars(225.0, 20.0), 'Nocturnal', 100.0)
    assert len(rows) == 1 and list(rows[0]) == COLUMNS
    assert rows[0]['Sign'] == 'Scorpio' and rows[0]["Chart's sect"] == 'Nocturnal' and rows[0]['Source'] == SOURCE
    assert rows[0]['Case'] == 'in his own domicile, in a nocturnal nativity'
    assert rows[0]['Text'] == engine["ABU_BAKR_MARS_II_1_0"]['Nocturnal'][1]
    assert 'a good soldier' in rows[0]['Text'] and 'always conquering' in rows[0]['Text']


def test_mars_in_aries_by_day_is_the_lazy_one(engine):
    rows = engine["evaluate_mars_abu_bakr"](_mars(15.0, 200.0), 'Diurnal', 130.0)   # Ascendant in Leo: Aries is the ninth
    assert len(rows) == 1
    assert rows[0]['Sign'] == 'Aries' and rows[0]['Case'] == 'in his own domicile, in a diurnal nativity'
    assert rows[0]['Text'].startswith(engine["ABU_BAKR_MARS_II_1_0"]['Diurnal'][1])
    assert 'lazy in those things in which he ought to make money' in rows[0]['Text']
    assert 'fn 652' in rows[0]['Text'] and 'Insanus' in rows[0]['Text']


def test_mars_in_capricorn_is_in_a_domicile_of_saturn(engine):
    for sect in ('Diurnal', 'Nocturnal'):
        rows = engine["evaluate_mars_abu_bakr"](_mars(280.0, 200.0), sect, 100.0)
        assert len(rows) == 1 and rows[0]['Case'] == 'in a domicile of Saturn'
        assert rows[0]['Text'] == engine["ABU_BAKR_MARS_II_1_0"]['Saturn'][1]
        assert 'a fatty liver' in rows[0]['Text']


def test_mars_in_gemini_has_no_sentence(engine):
    rows = engine["evaluate_mars_abu_bakr"](_mars(75.0, 200.0), 'Diurnal', 100.0)
    assert len(rows) == 1 and rows[0]['Sign'] == 'Gemini'
    assert rows[0]['Case'] == engine["ABU_BAKR_MARS_NO_SENTENCE"] and rows[0]['Text'] == ''
    assert 'no sentence of II.1.0 reaches him' in rows[0]['Case']


def test_the_midheaven_is_a_second_row(engine):
    # Ascendant in Cancer, Mars in Aries: his domicile and the whole-sign tenth
    rows = engine["evaluate_mars_abu_bakr"](_mars(15.0, 20.0), 'Nocturnal', 100.0)
    assert [r['Case'] for r in rows] == ['in his own domicile, in a nocturnal nativity', 'in the Midheaven (the whole-sign tenth)']
    assert rows[1]['Text'] == engine["ABU_BAKR_MARS_II_1_0"]['Midheaven'][1]
    # Ascendant in Virgo, Mars in Gemini: the tenth alone, no no-sentence row
    rows = engine["evaluate_mars_abu_bakr"](_mars(75.0, 200.0), 'Diurnal', 160.0)
    assert [r['Case'] for r in rows] == ['in the Midheaven (the whole-sign tenth)']
