"""Affliction and fortification after Rhetorius, Astrological Compendium
Chs. 26-28, 41-42 (Holden): every condition's text is the corpus's own
sentence, and hand-built charts hit each tested condition once. Display
only; nothing scores the rows."""
import re
from datetime import datetime
from pathlib import Path

import pytest

from corpus_paths import corpus_file

CORPUS = corpus_file("rhetorius/rhetorius_holden_PROVISIONAL.md")
COLUMNS = ['Planet', 'Condition', 'By', 'Chapter', 'Text']


def _span():
    """Pages 21-24 of Holden's Rhetorius, italics and footnote marks stripped."""
    text = CORPUS.read_text(encoding="utf-8")
    start, end = text.index("*[Rhetorius p. 21]*"), text.index("*[Rhetorius p. 25]*")
    span = text[start:end]
    span = re.sub(r"<sup>\d+</sup>", "", span)
    return span.replace("*", "")


@pytest.fixture(scope="module")
def span():
    if not CORPUS.exists():
        pytest.skip("the corpus is not on this machine")
    return _span()


def test_every_condition_text_is_verbatim_from_the_corpus(engine, span):
    conditions = engine["RHETORIUS_AFFLICTION_CONDITIONS"]
    assert len(conditions) == 14
    ita = (CORPUS.parent.parent / 'ita' / 'ita_photographed.md').read_text(encoding='utf-8')
    for c in conditions:
        if c['key'] == 'enclosed by the fortunes':
            assert c['text'] in ita, c['key']   # Gr. Intr. VII.6 as ITA IV.4.2 quotes it
            continue
        assert c['text'] in span, c['key']
        assert c['chapter'].startswith('Rhetorius Ch. ') and ('(Holden)' in c['chapter'])
        assert c['family'] in ('Afflicted', 'Fortified', 'Dominated')
        assert (c.get('reading') is None) == ('untested' in c), c['key']
    for name in ('RHETORIUS_CH26', 'RHETORIUS_CH27', 'RHETORIUS_CH28', 'RHETORIUS_CH34', 'RHETORIUS_CH41', 'RHETORIUS_CH42'):
        assert engine[name] in span, name


def test_house_sets_are_the_chapters_lists(engine):
    assert set(engine["RHETORIUS_INEFFECTIVE_HOUSES"]) == {6, 3, 2, 8, 12}
    assert set(engine["RHETORIUS_EFFECTIVE_HOUSES"]) == {1, 4, 7, 10, 5, 9, 11}
    assert engine["RHETORIUS_BESIEGING_DEGREES"] == 7.0
    assert engine["RHETORIUS_KOLLESIS_DEGREES"] == 3.0


def _rows(engine, chart, asc=0.0):
    rows = engine["evaluate_rhetorius_affliction"](chart, asc, 'Diurnal')
    for r in rows:
        assert list(r) == COLUMNS
    return rows


def _of(rows, planet, key):
    return [r for r in rows if r['Planet'] == planet and r['Condition'].endswith(': ' + key)]


def test_besieged_per_ch_41(engine):
    """The Moon at 13 Libra between Saturn's opposition ray from 18 Aries
    (5 degrees ahead) and Mars's sextile ray from 10 Leo (3 degrees behind),
    nothing else between them."""
    chart = {'Moon': {'longitude': 193.0}, 'Saturn': {'longitude': 18.0}, 'Mars': {'longitude': 130.0},
             'Sun': {'longitude': 300.0}, 'Jupiter': {'longitude': 265.0}}
    rows = _rows(engine, chart, asc=100.0)
    siege = _of(rows, 'Moon', 'besieged')
    assert len(siege) == 1
    assert siege[0]['By'] == 'Mars (3.0° behind) and Saturn (5.0° ahead), by body or ray'
    assert siege[0]['Chapter'] == 'Rhetorius Ch. 27 with Ch. 41 (Holden); ITA IV.4.2'
    assert siege[0]['Text'] == 'besieged'
    # A fortune in the region loosens it and the row says so (ITA IV.4.2):
    # Venus's body at 15 Libra.
    chart['Venus'] = {'longitude': 195.0}
    rows2 = _rows(engine, chart, asc=100.0)
    assert _of(rows2, 'Moon', 'besieged')[0]['By'].endswith("loosened by Venus's body 2.0° off (ITA IV.4.2)")
    assert not _of(rows2, 'Moon', 'enclosed by the fortunes')
    # Mercury's body between does not: Rhetorius's "any third" is not the reading.
    del chart['Venus']; chart['Mercury'] = {'longitude': 195.0}
    assert 'loosened' not in _of(_rows(engine, chart, asc=100.0), 'Moon', 'besieged')[0]['By']


def test_enclosure_by_the_fortunes_is_its_own_fortified_row(engine):
    # Moon at 13 Libra between Jupiter's body at 10 Libra and Venus's trine ray from 18 Gemini.
    chart = {'Moon': {'longitude': 193.0}, 'Jupiter': {'longitude': 190.0}, 'Venus': {'longitude': 78.0},
             'Sun': {'longitude': 300.0}, 'Saturn': {'longitude': 335.0}, 'Mars': {'longitude': 265.0}}
    rows = _rows(engine, chart, asc=100.0)
    assert not _of(rows, 'Moon', 'besieged')
    good = _of(rows, 'Moon', 'enclosed by the fortunes')
    assert len(good) == 1 and good[0]['By'] == 'Jupiter (3.0° behind) and Venus (5.0° ahead), by body or ray'
    # a malefic's ray into the region breaks it (Dykes's comment): Mars's sextile from 15 Leo.
    chart['Mars'] = {'longitude': 135.0}
    assert 'broken by Mars' in _of(_rows(engine, chart, asc=100.0), 'Moon', 'enclosed by the fortunes')[0]['By']
    # And beyond 7 degrees there is no siege at all.
    chart['Venus'] = {'longitude': 240.0}
    chart['Saturn'] = {'longitude': 21.0}
    assert _of(_rows(engine, chart, asc=100.0), 'Moon', 'besieged') == []


def test_opposed_by_a_malefic_gives_both_rows(engine):
    chart = {'Sun': {'longitude': 45.0}, 'Saturn': {'longitude': 225.0}}
    rows = _rows(engine, chart, asc=45.0)
    assert _of(rows, 'Sun', 'opposed')[0]['By'] == 'Saturn by whole-sign opposition'
    assert _of(rows, 'Sun', 'aspected by malefics')[0]['By'] == 'Saturn by whole-sign opposition'
    # Saturn is opposed by the Sun too, but the Sun is no malefic.
    assert _of(rows, 'Saturn', 'opposed')[0]['By'] == 'Sun by whole-sign opposition'
    assert _of(rows, 'Saturn', 'aspected by malefics') == []


def test_disposed_by_a_lord_in_an_ineffective_house(engine):
    """Ascendant in Cancer; Venus in Aries, whose lord Mars stands in Sagittarius, the sixth."""
    chart = {'Venus': {'longitude': 10.0}, 'Mars': {'longitude': 250.0}}
    rows = _rows(engine, chart, asc=95.0)
    row = _of(rows, 'Venus', 'disposed by one in an ineffective house')
    assert len(row) == 1
    assert row[0]['By'] == 'Mars, lord of Aries, in the 6th house from the Ascendant'
    # Move Mars to Leo, the second: still ineffective; to Libra, the fourth: not.
    chart['Mars']['longitude'] = 130.0
    assert _of(_rows(engine, chart, asc=95.0), 'Venus', 'disposed by one in an ineffective house')[0]['By'].endswith('2nd house from the Ascendant')
    chart['Mars']['longitude'] = 190.0
    assert _of(_rows(engine, chart, asc=95.0), 'Venus', 'disposed by one in an ineffective house') == []


def test_applying_and_kollesis(engine):
    """The Moon at 10 Aries moving 13 a day toward Mars at 12 Aries: applying
    and, within three degrees, in kollesis; at 5 Aries applying only; past
    Mars, neither."""
    chart = {'Moon': {'longitude': 10.0, 'speed_in_lon': 13.0}, 'Mars': {'longitude': 12.0, 'speed_in_lon': 0.5}}
    rows = _rows(engine, chart)
    assert _of(rows, 'Moon', 'applying to a destructive star')[0]['By'] == 'Mars by conjunction, 2.0° short of exact'
    assert _of(rows, 'Moon', 'in kollesis')[0]['By'] == 'Mars, 2.0° ahead in Aries'
    chart['Moon']['longitude'] = 5.0
    rows = _rows(engine, chart)
    assert _of(rows, 'Moon', 'applying to a destructive star')[0]['By'] == 'Mars by conjunction, 7.0° short of exact'
    assert _of(rows, 'Moon', 'in kollesis') == []
    chart['Moon']['longitude'] = 14.0
    rows = _rows(engine, chart)
    assert _of(rows, 'Moon', 'applying to a destructive star') == []
    assert _of(rows, 'Moon', 'in kollesis') == []
    # Applying by square, whole sign, with no degree limit: 2 Cancer to 28 Aries.
    chart['Moon']['longitude'] = 92.0
    chart['Mars']['longitude'] = 28.0
    assert _of(_rows(engine, chart), 'Moon', 'applying to a destructive star')[0]['By'] == 'Mars by square, 26.0° short of exact'
    # Without a daily motion there is no row and no error.
    del chart['Moon']['speed_in_lon']
    assert _of(_rows(engine, chart), 'Moon', 'applying to a destructive star') == []


def test_dominance_follows_the_cancer_example(engine):
    """Cancer rising, a planet in Aries is superior to one in Cancer."""
    chart = {'Sun': {'longitude': 100.0}, 'Saturn': {'longitude': 10.0}, 'Venus': {'longitude': 340.0},
             'Jupiter': {'longitude': 40.0}}
    rows = _rows(engine, chart, asc=95.0)
    dom = _of(rows, 'Sun', 'dominated')
    assert len(dom) == 1
    assert dom[0]['Condition'] == 'Dominated: dominated'
    assert dom[0]['By'] == ('Saturn in the tenth sign, a square (the first kind); '
                            'Jupiter in the eleventh sign, a sextile; Venus in the ninth sign, a trine')
    assert _of(rows, 'Saturn', 'dominated') == []          # nothing stands to Aries's right in this chart


def test_fortified_per_ch_42(engine):
    """Mars at 3 Aries rising: its own domicile, its own bound, the first house."""
    chart = {'Mars': {'longitude': 3.0}, 'Sun': {'longitude': 20.0}}
    rows = _rows(engine, chart, asc=5.0)
    assert _of(rows, 'Mars', 'in its own domicile')[0]['By'] == 'Aries'
    assert _of(rows, 'Mars', 'in its own terms') == []      # 0-6 Aries is Jupiter's bound
    assert _of(rows, 'Mars', 'in one of the stronger houses')[0]['By'] == 'the 1st house from the Ascendant'
    assert _of(rows, 'Sun', 'in its own exaltation')[0]['By'] == 'Aries'
    assert _of(rows, 'Sun', 'in its own terms') == []
    chart['Mars']['longitude'] = 22.0                       # 20-25 Aries is Mars's bound
    assert _of(_rows(engine, chart, asc=5.0), 'Mars', 'in its own terms')[0]['By'] == '22° Ari 00\', its own bound'
    # The two untested conditions never give a row.
    assert not [r for r in rows if r['Condition'].endswith(('in proper phase', 'well-configured'))]


def test_the_1240_chart_runs(engine):
    chart = engine["calculate_traditional_chart"](datetime(1240, 5, 23, 13, 45), 43.7792, 11.2463)
    rows = engine["evaluate_rhetorius_affliction"](chart['planetary_data'], chart['ascendant'], chart['sect'])
    assert rows
    for r in rows:
        assert list(r) == COLUMNS
        assert r['Planet'] in ('Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon')
        assert r['Chapter'].startswith('Rhetorius Ch.')


def test_kollesis_is_the_same_sign_connection(engine):
    # Moon 29 Aries applying to Mars 1 Taurus: two degrees short but different
    # signs -- sun-aphe, not kollesis (Dykes, ITA p. 136): no row.
    pdata = {'Sun': {'longitude': 200.0, 'speed_in_lon': 1.0}, 'Moon': {'longitude': 29.0, 'speed_in_lon': 13.0},
             'Mars': {'longitude': 31.0, 'speed_in_lon': 0.5}, 'Saturn': {'longitude': 300.0, 'speed_in_lon': 0.1},
             'Jupiter': {'longitude': 250.0, 'speed_in_lon': 0.1}, 'Venus': {'longitude': 190.0, 'speed_in_lon': 1.2},
             'Mercury': {'longitude': 210.0, 'speed_in_lon': 1.3}}
    rows = engine["evaluate_rhetorius_affliction"](pdata, 120.0, 'Diurnal')
    assert not any(r['Planet'] == 'Moon' and r['Condition'] == 'Afflicted: in kollesis' for r in rows)
    # the same two degrees inside one sign: Moon 10 Aries, Mars 12 Aries.
    pdata['Moon']['longitude'] = 10.0; pdata['Mars']['longitude'] = 12.0
    rows = engine["evaluate_rhetorius_affliction"](pdata, 120.0, 'Diurnal')
    assert any(r['Planet'] == 'Moon' and r['Condition'] == 'Afflicted: in kollesis' for r in rows)
