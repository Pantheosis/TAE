"""Every page renders without exception on every chart, and renders exactly
the tables the fixture says it does -- as a multiset of (heading, columns),
not a count. Counting st.dataframe calls is what passed commit 3dbf4af,
which lost two tables and duplicated two others.

To accept a deliberate change to the set of tables:

    UPDATE_TABLE_FIXTURE=1 .venv/bin/python -m pytest tests/test_pages_render.py

then read the diff of tests/fixtures/tables.json before committing it.
"""
import json
import os

import pytest

from conftest import (CHARTS, TABLES_FIXTURE, assert_no_exception, describe_table_diff, dump_fixture,
                      load_table_fixture, make_app, page_slots, slot_name, table_inventory)

UPDATE = os.environ.get("UPDATE_TABLE_FIXTURE") == "1"
_collected = {}


def _render(date, page, view):
    at = make_app(date=date, page=page, view=view).run()
    assert_no_exception(at, f"{date} {slot_name(page, view)}")
    return at


@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("page,view", page_slots(), ids=[slot_name(p, v) for p, v in page_slots()])
def test_page_renders_expected_tables(date, page, view):
    at = _render(date, page, view)
    slot = slot_name(page, view)
    actual = table_inventory(at)

    # The page header is the one element every page must have; a page that
    # rendered nothing at all would otherwise pass with an empty inventory.
    assert len(at.main.header) >= 1, f"{date} {slot}: no st.header rendered"
    # Structure, not values: _finding() suppresses empty findings and the
    # fixed tables are never empty, so a rendered table with no rows is a
    # table that lost its data.
    for (heading, _cols), df in zip(actual, at.main.dataframe):
        assert len(df.value) > 0, f"{date} {slot}: {heading!r} rendered with no rows"

    if UPDATE:
        _collected.setdefault(date, {})[slot] = [[h, c] for h, c in actual]
        return

    fixture = load_table_fixture()
    expected = [tuple(e) for e in fixture.get(date, {}).get(slot, [])]
    assert fixture.get(date, {}).get(slot) is not None, (
        f"no fixture entry for {date} {slot}; regenerate with UPDATE_TABLE_FIXTURE=1")
    diff = describe_table_diff(expected, actual)
    assert not diff, (
        f"{date} {slot}: the tables rendered do not match tests/fixtures/tables.json\n{diff}\n"
        f"  ({len(expected)} expected, {len(actual)} rendered)")


@pytest.fixture(scope="session", autouse=True)
def _write_fixture_at_end():
    yield
    if UPDATE and _collected:
        TABLES_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        ordered = {d: dict(sorted(v.items())) for d, v in sorted(_collected.items())}
        TABLES_FIXTURE.write_text(dump_fixture(ordered))
        print(f"\nwrote {TABLES_FIXTURE}")


# --- The Timing page's own reading (PN IV, IX.1, 26-34) ------------------
# This switch is NOT in conftest.SWITCHES: it is read only by page_timing,
# so putting it in the registry would double the Configurations
# cross-product (2**8 states x 6 charts) to prove nothing. It is covered
# instead by the doctrine fixtures, which pin the rule itself, and by
# these two renders, which prove both settings draw the page.

@pytest.mark.parametrize("date", list(CHARTS))
@pytest.mark.parametrize("turn", ["Dykes: always forward", "PN IV IX.1, 26-34"])
def test_timing_page_renders_under_both_monthly_turn_readings(date, turn):
    at = make_app(date=date, page="timing")
    at.session_state["_pn4_monthly_turn"] = turn
    at.run()
    assert_no_exception(at, f"{date} timing, monthly turn = {turn}")
    assert len(at.main.dataframe) > 0


def test_abu_mashars_turn_actually_reverses_a_convertible_indicator():
    """Not just "it renders": under Abu Ma'shar's rule at least one of the
    seven monthly indicators must be turned backwards on some chart, or
    the switch is inert. The default must leave every one forward."""
    def directions(turn):
        at = make_app(date="1240-05-23", page="timing")
        at.session_state["_pn4_monthly_turn"] = turn
        at.run()
        assert_no_exception(at, f"timing {turn}")
        for df in at.main.dataframe:
            if "Turned" in df.value.columns:
                return list(df.value["Turned"])
        pytest.fail("the monthly indicators table did not render")

    default = directions("Dykes: always forward")
    assert not any(d.startswith("backwards") for d in default), default
    assert any(d.startswith("backwards") for d in directions("PN IV IX.1, 26-34"))
