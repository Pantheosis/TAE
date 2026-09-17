"""column_config on the tables (2026-09-15 second opinion, item 7).

Widths and help text only. The doctrine fixtures (tests/fixtures/tables.json)
compare a table's own DataFrame -- its values, its column names, its column
order -- and none of that is touched here: every DataFrame is built exactly
as it was, and column_config only says how a column already there is
displayed. These tests read the rendered element's own proto rather than the
source, so a column_config that failed to reach Streamlit's wire format
would be caught here even if the Python call that built it looked right.
"""
import json

import pytest

from conftest import PAGES, READING_DEPTHS, assert_no_exception, find_table, make_app


def _column_config(dataframe_element):
    return json.loads(dataframe_element.proto.columns)


# --- Every page still renders, at both reading depths ---------------------

@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("depth", READING_DEPTHS)
def test_every_page_still_renders_with_column_config_added(page, depth):
    at = make_app(page=page)
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"{page}, {depth}")


# --- The tick grids: the number moves from the header into its tooltip ----

def test_strength_grid_moves_the_sentence_number_into_the_tooltip():
    at = make_app(page="configurations")
    at.run()
    assert_no_exception(at, "configurations")
    config = _column_config(find_table(at, "Strength of the Planets"))
    assert config["78 excellent place"]["label"] == "excellent place"
    assert config["78 excellent place"]["help"] == "Sahl, The Introduction Ch. 3, 78"
    assert config["78 excellent place"]["width"] == "small"
    assert config["88 gender match"]["label"] == "gender match"
    assert config["88 gender match"]["help"] == "Sahl, The Introduction Ch. 3, 88"
    assert config["Planet"]["width"] == "small"
    assert config["Count"]["width"] == "small"


def test_weakness_grid_moves_the_sentence_number_into_the_tooltip():
    at = make_app(page="configurations")
    at.run()
    assert_no_exception(at, "configurations")
    config = _column_config(find_table(at, "Weakness of the Planets"))
    assert config["91 falling, averse ASC"]["label"] == "falling, averse ASC"
    assert config["91 falling, averse ASC"]["help"] == "Sahl, The Introduction Ch. 3, 91"
    assert config["91 falling, averse ASC"]["width"] == "small"
    assert config["Planet"]["width"] == "small"
    assert config["Count"]["width"] == "small"


# --- A wide Value/Text column, from _finding() -----------------------------

def test_a_finding_s_value_and_text_columns_are_wide():
    at = make_app(page="findings")
    at.run()
    assert_no_exception(at, "findings")
    config = _column_config(find_table(at, "The Moon on the third day (Sahl)"))
    assert config["Value"]["width"] == "large"
    assert config["Text"]["width"] == "large"
    assert config["Value"]["type_config"]["type"] == "text"


def test_a_direct_table_s_source_column_is_wide():
    """Not every wide column comes through _finding(): the Timing page's own
    tables call st.dataframe directly and get the same helper explicitly."""
    at = make_app(page="timing")
    at.run()
    assert_no_exception(at, "timing")
    config = _column_config(find_table(at, "The revolution of the year"))
    assert config["Value"]["width"] == "large"
    assert config["Source"]["width"] == "large"


# --- A Yes/No column: width only, still text, values untouched ------------

def test_a_yes_no_column_is_narrow_text_not_a_checkbox():
    at = make_app(page="dignities")
    at.run()
    assert_no_exception(at, "dignities")
    node = find_table(at, "Sect")
    config = _column_config(node)
    for col in ("Above horizon", "Domain (hayz)", "Of the chart's sect"):
        assert config[col]["width"] == "small"
        assert config[col]["type_config"]["type"] == "text"
        assert "CheckboxColumn" not in json.dumps(config[col])
    values = set(node.value["Above horizon"].unique().tolist()) | set(node.value["Of the chart's sect"].unique().tolist())
    assert values <= {"Yes", "No"}, "the ruling: values do not change on this branch"
