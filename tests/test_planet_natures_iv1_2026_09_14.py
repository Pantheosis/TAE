"""The natures of the planets after Ptolemy, Gr. Intr. IV.1, 6-12: a display-only
table on the Reference page at the supplement depth (2026-09-14). Seven rows in the
app's planet order, every 'As stated' string verbatim in the corpus."""
import pytest

from corpus_paths import corpus_file

CORPUS = corpus_file("gr_intr/abu_mashar_great_introduction.md")


def test_seven_rows_in_the_apps_order_each_sourced_to_iv1(engine):
    rows = engine["PLANET_NATURES_IV1"]
    assert len(rows) == 7
    assert [r['Planet'] for r in rows] == engine["WEIGHT_ORDER"]
    for r in rows:
        assert set(r) == {'Planet', 'Active (hot/cold)', 'Passive (wet/dry)', 'As stated', 'Source'}
        assert r['Source'].startswith("IV.1, ") and r['Source'][6:].isdigit()
        assert r['Active (hot/cold)'] and r['Passive (wet/dry)'] and r['As stated']


@pytest.mark.skipif(not CORPUS.exists(), reason="corpus not on this machine")
def test_each_sentence_is_quoted_verbatim_from_the_corpus(engine):
    text = CORPUS.read_text(encoding="utf-8")
    start = text.index("### Chapter IV.1:")
    chapter = text[start:text.index("### Chapter IV.2", start)]
    for r in engine["PLANET_NATURES_IV1"]:
        assert r['As stated'] in chapter, r['Planet']


def test_the_table_shows_only_under_course_text_and_supplement(engine):
    from conftest import assert_no_exception, make_app
    title = "The natures of the planets (Gr. Intr. IV.1)"
    plain = make_app(page="reference").run()
    assert_no_exception(plain, "reference")
    assert title not in [h.value for h in plain.main.subheader]
    full = make_app(page="reference", view="Full").run()
    assert_no_exception(full, "reference")
    assert title in [h.value for h in full.main.subheader]
    df = next(d.value for d in full.main.dataframe if "As stated" in d.value.columns)
    assert list(df["Planet"]) == engine["WEIGHT_ORDER"] and len(df) == 7
