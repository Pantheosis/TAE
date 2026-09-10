"""The navigation in sections, the lesson gate retired, the Reference tables page
(2026-09-10, UI_REVIEW_2026-09-10.md §1 A and §3)."""
import pytest

from conftest import assert_no_exception, make_app, ui_source


def test_the_lesson_gate_is_gone_and_nothing_is_hidden():
    src = ui_source()
    assert "Show material through" not in src and "lesson_gate" not in src
    assert 'st.navigation(pages, position="sidebar", expanded=True)' in src
    for section in ('"Part 1: the nativity"', '"Part 2: prediction"', '"Reference"'):
        assert section in src
    at = make_app(page="chart").run()
    assert_no_exception(at, "chart")
    assert not [s for s in at.sidebar.selectbox if "material" in s.label.lower()]


def test_reference_page_prints_the_handy_tables_from_the_engines_data(engine):
    at = make_app(page="reference").run()
    assert_no_exception(at, "reference")
    heads = [h.value for h in at.main.subheader]
    assert heads == ["Dignities by sign", "Egyptian bounds", "Orders of the dignities, and the good places",
                     "Planetary years", "The Ages of Man"]
    tables = {}
    for df in at.main.dataframe:
        tables.setdefault(tuple(df.value.columns), df.value)
    dign = next(v for k, v in tables.items() if "Domicile" in k)
    assert list(dign["Sign"]) == engine["SIGN_ORDER"]
    assert dign[dign["Sign"] == "Libra"].iloc[0]["Exaltation"] == "Saturn (21°)"
    assert dign[dign["Sign"] == "Aries"].iloc[0]["Faces (1st, 2nd, 3rd)"] == "Mars · Sun · Venus"
    bounds = next(v for k, v in tables.items() if "1st bound" in k)
    assert len(bounds) == 12 and bounds.iloc[0]["1st bound"] == "Jupiter 0°–5°59′"
    assert bounds[bounds["Sign"] == "Pisces"].iloc[0]["5th bound"] == "Saturn 28°–29°59′"
    years = next(v for k, v in tables.items() if "Mighty" in k)
    for _, r in years.iterrows():
        y = engine["PLANETARY_YEARS"][r["Planet"]]
        assert (r["Lesser"], r["Middle"], r["Greater"], r["Mighty"], r["Fardar (years)"]) == \
            (y["lesser"], y["middle"], y["greater"], y["mighty"], y["fardar"])
    ages = next(v for k, v in tables.items() if "Ruler" in k)
    assert list(ages["Ruler"]) == [p for p, _y, _d in engine["PN4_AGES_OF_MAN"]]
    assert ages.iloc[-1]["To"] == sum(y for _p, y, _d in engine["PN4_AGES_OF_MAN"])


def test_the_static_tables_left_the_chart_page_for_the_reference_page():
    chart = make_app(page="chart").run()
    # (an expander with an icon is not typed as one by AppTest; read its caption)
    assert any("are on the Reference tables page" in c.value for c in chart.main.caption)
    assert "Sahl's sign categories for this chart's points" in ui_source()
    assert not [df for df in chart.main.dataframe if "Order, strongest first" in df.value.columns]
    ref = make_app(page="reference").run()
    assert [df for df in ref.main.dataframe if "Order, strongest first" in df.value.columns]
    assert [df for df in ref.main.dataframe if "Scheme" in df.value.columns]
