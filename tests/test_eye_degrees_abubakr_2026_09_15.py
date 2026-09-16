"""Abu Bakr's eye-degrees (On Nativities II.7.3, PN II p. 238) beside Sahl's
and Abu Ma'shar's in EYESIGHT_PLACES: the fifteen spans pinned row by row,
every quotation a substring of the photographed page, the evaluator on
hand-built charts, and the other two sources' row counts unchanged."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from corpus_paths import corpus_file
from test_doctrine_fixtures import pdata

SAHL = 'Sahl, On Nativities 6.2'
ABU = 'Gr. Intr. VI.20'
ABUBAKR = 'Abu Bakr, On Nativities II.7.3'
RULE = '"And it must be known that in some signs are some degrees which destroy vision:"'
CORPUS = corpus_file('pn2/pn2_photographed.md')

# (sign, lo, hi, dorotheus) -- ordinal degrees, half-open, read as Sahl's
# are: "the sixth" is 5.0-6.0, and neighbouring ordinals are one span.
EXPECTED = [
    ('Taurus', 5.0, 6.0, False),          # the sixth
    ('Taurus', 8.0, 10.0, False),         # ninth, tenth
    ('Cancer', 8.0, 15.0, False),         # from the ninth up to the fifteenth
    ('Leo', 17.0, 18.0, False),           # the eighteenth
    ('Leo', 26.0, 28.0, False),           # twenty-seventh, twenty-eighth
    ('Scorpio', 18.0, 19.0, False),       # the nineteenth
    ('Scorpio', 27.0, 28.0, False),       # the twenty-eighth
    ('Scorpio', 7.0, 10.0, True),         # Dorotheus: eighth, ninth, tenth
    ('Scorpio', 21.0, 22.0, True),        # Dorotheus: twenty-second
    ('Sagittarius', 0.0, 1.0, False),     # the first
    ('Sagittarius', 6.0, 9.0, False),     # seventh, eighth, ninth
    ('Capricorn', 25.0, 29.0, False),     # from the twenty-sixth up to the twenty-ninth
    ('Aquarius', 5.0, 6.0, False),        # the sixth
    ('Aquarius', 9.0, 10.0, False),       # the tenth
    ('Aquarius', 18.0, 19.0, False),      # the nineteenth
]


def _abubakr(engine):
    return [r for r in engine["EYESIGHT_PLACES"] if r['source'] == ABUBAKR]


def test_row_counts_per_source_are_pinned(engine):
    from collections import Counter
    c = Counter(r['source'] for r in engine["EYESIGHT_PLACES"])
    assert c == {SAHL: 32, ABU: 7, ABUBAKR: 15}
    assert len(engine["EYESIGHT_PLACES"]) == 54


def test_every_abubakr_span_is_pinned(engine):
    rows = _abubakr(engine)
    assert [(r['sign'], r['lo'], r['hi'], 'Dorotheus' in r['place']) for r in rows] == EXPECTED
    for r in rows:
        assert not r['closed'] and r['sentence'] == 'p. 238' and r['rule'].endswith(RULE)
        assert r['reading'].startswith('ordinal degree') and r['quote'].startswith('"') and r['quote'].endswith('."')
        assert ('according to Dorotheus' in r['printed']) == ('Dorotheus' in r['place'])
        assert ('Dorotheus' in r['quote']) == ('Dorotheus' in r['place'])
    # the Source column keeps the three lists apart
    assert {r['source'] for r in engine["EYESIGHT_PLACES"]} == {SAHL, ABU, ABUBAKR}


@pytest.mark.skipif(not CORPUS.exists(), reason="the photographed page is not on this machine")
def test_every_abubakr_quotation_is_verbatim(engine):
    text = CORPUS.read_text(encoding='utf-8')
    page = text[text.index('*[PN II p. 238]*'):]
    page = re.sub(r'<sup>\d+</sup>', '', page).replace('*', '')
    for q in {r['quote'] for r in _abubakr(engine)} | {RULE}:
        assert q.strip('"') in page, q


def test_moon_in_cancer_hits_abubakr_and_the_sahl_rows_that_share_the_span(engine):
    rows = engine["evaluate_eyesight_places"](pdata(Sun=200.0, Moon=90.0 + 9.5), 130.0)
    assert [r['Point'] for r in rows] == ['Moon'] * 3
    assert [r['Source'] for r in rows] == [f'{SAHL}, 55', f'{SAHL}, 65', f'{ABUBAKR}, p. 238']   # Nawbakht's 74 is the ninth degree only
    ab = rows[-1]
    assert ab['Place'] == "the nebula in Cancer (fn 1027) -- Cancer, from the ninth degree up to the fifteenth (ordinal degrees, 8°00'-15°00')"
    assert ab['Text'].startswith('p. 238: "In Cancer, from the ninth degree up to the fifteenth." Rule -- p. 238: "And it must be known')


def test_moon_in_leo_hits_abubakr_leo_row(engine):
    rows = engine["evaluate_eyesight_places"](pdata(Sun=200.0, Moon=120.0 + 27.5), 130.0)
    assert [r['Source'] for r in rows] == [f'{SAHL}, 61', f'{ABUBAKR}, p. 238']
    assert 'Leo, the twenty-seventh and twenty-eighth' in rows[-1]['Place']
    # 26°30' Leo: the twenty-seventh degree, Abu Bakr's alone
    rows = engine["evaluate_eyesight_places"](pdata(Sun=200.0, Moon=120.0 + 26.5), 130.0)
    assert [r['Source'] for r in rows] == [f'{ABUBAKR}, p. 238']


def test_dorotheus_rows_carry_his_name_and_stand_apart(engine):
    f = engine["evaluate_eyesight_places"]
    rows = [r for r in f(pdata(Sun=200.0, Moon=210.0 + 21.5), 130.0) if r['Source'].startswith(ABUBAKR)]
    assert len(rows) == 1 and 'according to Dorotheus' in rows[0]['Place'] and 'Dorotheus' in rows[0]['Text']
    rows = [r for r in f(pdata(Sun=200.0, Moon=210.0 + 18.5), 130.0) if r['Source'].startswith(ABUBAKR)]
    assert len(rows) == 1 and 'Dorotheus' not in rows[0]['Place']


def test_spans_are_half_open(engine):
    f = engine["evaluate_eyesight_places"]
    hits = lambda lon: [r for r in f(pdata(Sun=200.0, Moon=lon), 130.0) if r['Source'].startswith(ABUBAKR)]
    assert len(hits(30.0 + 5.0)) == 1 and hits(30.0 + 6.0) == [] and len(hits(30.0 + 8.0)) == 1 and hits(30.0 + 10.0) == []
    assert hits(90.0 + 15.0) == [] and len(hits(270.0 + 28.99)) == 1 and hits(270.0 + 29.0) == []


def test_page_names_the_three_lists():
    from conftest import app_source
    src = app_source()
    assert "'Sahl, On Nativities 6.2, 48-75; Gr. Intr. VI.20; Abu Bakr, On Nativities II.7.3'" in src
    assert 'does not reconcile them' in src and 'are not computed' in src
