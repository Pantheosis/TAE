"""The pictures of the Timing page (built 2026-09-10, UI_CHART_INPUT_EVALUATION_2026-09-10.md §6).

Pure renderers in the engine half, exercised on every harness chart and
the owner's reference nativity: the multi-ring wheel (one to three charts
on one zodiac -- the year alone, the year over the root of I.6, the month
over both of IX.3, the profection), the Egyptian-bounds ring, and the
direction strips. Each must be well-formed XML and carry the points it
claims; the year-over-root wheel is held to the I.6 inventory table point
by point, house by house, as the brief demanded; the strips carry one bar
per segment and exactly one "now". The Timing page renders every view and
every toggle without exception, and the controls persist as readings.
"""
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

import pytest

from conftest import CHARTS, FLORENCE, LOCAL_TIME, assert_no_exception, make_app

SVG = "{http://www.w3.org/2000/svg}"
PETOSKEY = (45.37334, -84.95533)
REFERENCE_UTC = datetime(1982, 11, 19, 16, 44)
RULE = None


def _chart(engine, date_str=None):
    if date_str is None:
        return engine["calculate_traditional_chart"](REFERENCE_UTC, *PETOSKEY), PETOSKEY, REFERENCE_UTC.date()
    local = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), LOCAL_TIME)
    dt_utc = local - timedelta(hours=FLORENCE[1] / 15.0)
    return engine["calculate_traditional_chart"](dt_utc, *FLORENCE), FLORENCE, local.date()


def _bundle(engine, date_str=None, target=date(2026, 9, 10)):
    chart, latlon, birth = _chart(engine, date_str)
    rule = engine["PN4_MONTHLY_TURN_OPTIONS"][0]
    b = engine["pn4_timing_bundle"](chart, latlon[0], latlon[1], birth, target, rule,
                                    {"Hour Lord": "Venus", "Approximate": False})
    return chart, latlon, b


def _rings(engine, chart, b, n):
    natal = {"label": "Nativity", "chart": chart, "when": "birth"}
    year = {"label": f"Year, age {b['age']}", "chart": b["sr"], "when": "year"}
    month = {"label": f"Month {b['month']} of 12", "chart": b["mr"], "when": "month"}
    return [natal, year, month][:n]


def _groups(svg, cls):
    root = ET.fromstring(svg)
    return [g for g in root.iter(SVG + "g") if g.get("class") == cls]


# --- The multi-ring wheel ------------------------------------------------------

@pytest.mark.parametrize("date_str", [None] + list(CHARTS), ids=["1982-petoskey"] + list(CHARTS))
@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("wide", [False, True], ids=["square", "wide"])
def test_multiwheel_is_well_formed_and_carries_every_ring(engine, date_str, n, wide):
    chart, latlon, b = _bundle(engine, date_str)
    rings = _rings(engine, chart, b, n)
    year_sign = engine["SIGN_ORDER"].index(b["year"]["sign"])
    svg = engine["generate_multiwheel_svg"](rings, "Test & Chart", wide=wide, bounds=True, shade_sign=year_sign,
                                            profection_from=chart["ascendant"])
    root = ET.fromstring(svg)
    width = engine["WHEEL_WIDE_WIDTH"] if wide else engine["WHEEL_SIZE"]
    assert root.get("viewBox") == f"0 0 {width} {engine['WHEEL_SIZE']}"
    pts = _groups(svg, "pt")
    # Ten points per ring: seven planets, two nodes, Fortune.
    assert len(pts) == 10 * n
    for i, ring in enumerate(rings):
        mine = [g for g in pts if g.get("data-ring") == str(i)]
        assert {g.get("data-point") for g in mine} == set(engine["POINT_GLYPHS"]), (i, ring["label"])
        assert all(g.get("data-chart") == ring["label"] for g in mine)
        p = ring["chart"]["planetary_data"]
        for g in mine:
            name = g.get("data-point")
            lon = (p[name]["longitude"] if name in p else
                   (p["North Node"]["longitude"] + 180.0) % 360.0 if name == "South Node" else ring["chart"]["lot_of_fortune"])
            assert float(g.get("data-lon")) == pytest.approx(lon % 360.0, abs=1e-5)
    texts = [t.text or "" for t in root.iter(SVG + "text")]
    assert "Test &amp; Chart" in svg and "Test & Chart" in texts
    for glyph in engine["SIGN_GLYPHS"]:
        assert any(t.rstrip("︎") == glyph for t in texts), glyph
    # The bounds ring: sixty cells, one per Egyptian bound, and the shade.
    assert len([p for p in root.iter(SVG + "path") if p.get("class") == "bound"]) == 60
    shade = [p for p in root.iter(SVG + "path") if p.get("class") == "shade"]
    assert len(shade) == 1 and shade[0].get("data-sign") == str(year_sign)
    # The profection arc exists whenever the sign of the year is not the rising sign.
    arcs = [p for p in root.iter(SVG + "path") if p.get("class") == "profection"]
    assert len(arcs) == (0 if int(chart["ascendant"] // 30) == year_sign else 1)
    # Every ring's twelve whole-sign numbers.
    houses = [t for t in root.iter(SVG + "text") if t.get("class") == "house"]
    assert len(houses) == 12 * n
    if wide:
        for ring in rings:
            assert ring["label"] in texts


def test_multiwheel_refuses_zero_or_four_rings(engine):
    chart, latlon, b = _bundle(engine)
    with pytest.raises(AssertionError):
        engine["generate_multiwheel_svg"]([], "x")
    with pytest.raises(AssertionError):
        engine["generate_multiwheel_svg"](_rings(engine, chart, b, 3) + [{"label": "x", "chart": chart}], "x")


def test_bounds_ring_tints_the_bound_the_distribution_stands_in(engine):
    chart, latlon, b = _bundle(engine)
    end = engine["_pn4_seg_degree"]({"from": float(b["age"])}, chart["ascendant"], chart, latlon[0])
    svg = engine["generate_multiwheel_svg"](_rings(engine, chart, b, 2), "x", bounds=True,
                                            distribution={"start": chart["ascendant"], "end": end})
    root = ET.fromstring(svg)
    tinted = [p for p in root.iter(SVG + "path") if p.get("class") == "bound" and p.get("fill") == engine["WHEEL_BOUND_TINT"]]
    assert len(tinted) == 1
    arc = [p for p in root.iter(SVG + "path") if p.get("class") == "distribution"]
    assert len(arc) == 1 and float(arc[0].get("data-end")) == pytest.approx(end % 360.0, abs=1e-5)
    # The tinted cell is the bound of the endpoint: its lord is the distributor now.
    assert b["current"]["distributor"] == engine["pn4_bound_lord"](end)


# --- The picture against the inventory table (I.6, 3-8) ------------------------

@pytest.mark.parametrize("date_str", [None] + list(CHARTS), ids=["1982-petoskey"] + list(CHARTS))
@pytest.mark.parametrize("dykes", [True, False], ids=["nativity-inside", "revolution-inside"])
def test_year_over_root_agrees_with_the_inventory_cell_for_cell(engine, date_str, dykes):
    """Every point the picture draws -- the default set and the three
    toggles' sets -- must be a row of pn4_revolution_image with the same
    position (to the printed minute) and the same whole-sign house from
    the revolution's Ascendant; and every planet, node, Fortune, ray and
    twelfth-part row of the inventory must be drawn. Lots the inventory
    lists with 'many or few' are checked one way: drawn implies listed."""
    chart, latlon, b = _bundle(engine, date_str)
    rows, _counts = b["image"]
    natal, year = _rings(engine, chart, b, 2)
    rings = [natal, year] if dykes else [year, natal]
    chart_of = {"Nativity": "root", year["label"]: "revolution"}

    def extras_for(c):
        out = []
        for d in engine["LOT_DEFINITIONS"]:
            if d["id"] == "fortune":
                continue
            lon = engine["lot_by_id"](d["id"], c["planetary_data"], c["ascendant"], c["houses"], c["sect"])
            if lon is not None:
                out.append((d["name"], lon))
        for lon, kind, who, aspect in engine["pn4_bodies_and_rays"](c["planetary_data"]):
            if kind != "body":
                out.append((f"{who} by {aspect}", lon))
        for who, row in c["planetary_data"].items():
            if who in engine["PLANET_SWE_IDS"]:
                out.append((f"twelfth-part of {who}", engine["pn4_twelfth_part"](row["longitude"])))
        for i, cusp in enumerate(list(c["houses"])[:12]):
            out.append((f"twelfth-part of the degree of house {i + 1} ({engine['get_degree_string'](cusp)})",
                        engine["pn4_twelfth_part"](cusp)))
        return out

    extras = {i: extras_for(r["chart"]) for i, r in enumerate(rings)}
    svg = engine["generate_multiwheel_svg"](rings, "x", extras=extras)
    r_asc = b["sr"]["ascendant"]
    table = {}
    for r in rows:
        table.setdefault((r["Chart"], r["Point"]), []).append(r)

    def inventory_name(point):
        return {"North Node": "Head", "South Node": "Tail"}.get(point, point)

    drawn = set()
    for cls in ("pt", "extra"):
        for g in _groups(svg, cls):
            which = chart_of[g.get("data-chart")]
            name = inventory_name(g.get("data-point"))
            lon = float(g.get("data-lon"))
            candidates = table.get((which, name)) or [r for (c, p), rs in table.items() for r in rs
                                                       if c == which and p.startswith(name + " (")]
            assert candidates, f"drawn but not in the inventory: {which} {name}"
            position = engine["get_degree_string"](lon)
            house = engine["get_wsh_house"](lon, r_asc)
            assert any(r["Position"] == position and r["House"] == house for r in candidates), (which, name, position, house)
            drawn.add((which, candidates[0]["Point"]))
    for r in rows:
        if r["Kind"] in ("planet", "ray", "node", "twelfth-part of a planet", "twelfth-part of a house"):
            assert (r["Chart"], r["Point"]) in drawn, f"in the inventory but not drawn: {r['Chart']} {r['Point']}"
        if r["Kind"] == "Lot":
            assert (r["Chart"], r["Point"]) in drawn, f"Lot not drawn: {r['Chart']} {r['Point']}"


# --- The natal wheel's bounds ring ------------------------------------------------

@pytest.mark.parametrize("bounds", [False, True])
def test_natal_wheel_bounds_ring_is_a_toggle(engine, bounds):
    chart, latlon, _ = _chart(engine)
    svg = engine["generate_hybrid_svg"](chart, "Ref", "Petoskey", latlon[0], latlon[1], datetime(1982, 11, 19, 11, 44),
                                        "EST", bounds=bounds)
    root = ET.fromstring(svg)
    cells = [p for p in root.iter(SVG + "path") if p.get("class") == "bound"]
    lords = [t for t in root.iter(SVG + "text") if t.get("class") == "bound-lord"]
    assert len(cells) == (60 if bounds else 0) and len(lords) == (60 if bounds else 0)
    # With the ring, the lord glyphs are the seven planets' only, five per sign.
    if bounds:
        planets = {"Saturn", "Jupiter", "Mars", "Venus", "Mercury"}
        assert {t.text.rstrip("︎") for t in lords} == {engine["POINT_GLYPHS"][p] for p in planets}


# --- The direction strips ------------------------------------------------------------

@pytest.mark.parametrize("date_str", [None] + list(CHARTS), ids=["1982-petoskey"] + list(CHARTS))
def test_strips_carry_one_bar_per_segment_and_one_now(engine, date_str):
    chart, latlon, b = _bundle(engine, date_str)
    strip = engine["generate_distribution_strip_svg"]
    cases = [(b["segments"], float(b["age"]), "years", engine["PN4_DISTRIBUTION_SPAN_YEARS"])]
    for point in engine["PN4_MERIDIAN_POINTS"]:
        cases.append((b["meridian"][point]["segments"], float(b["age"]), "years", engine["PN4_DISTRIBUTION_SPAN_YEARS"]))
    cases.append((b["small_days"], b["day_of_year"], "days", None))
    cases.append((b["mighty_days"], b["day_of_year"], "days", None))
    for segments, now, unit, span in cases:
        if segments is None:
            continue
        svg = strip(segments, now, unit, span, "A title & more")
        root = ET.fromstring(svg)
        bars = [r for r in root.iter(SVG + "rect") if r.get("class") == "seg"]
        assert len(bars) == len(segments)
        for bar, seg in zip(bars, segments):
            assert float(bar.get("data-from")) == pytest.approx(seg["from"], abs=1e-3)
            assert bar.get("data-distributor") == seg["distributor"]
            assert bar.get("data-partner") == str(seg["partner"])
        span_used = span if span is not None else max(s["to"] for s in segments)
        nows = [l for l in root.iter(SVG + "line") if l.get("class") == "now"]
        assert len(nows) == (1 if 0.0 <= now <= span_used else 0)
        assert "A title &amp; more" in svg


def test_strip_rejects_an_unknown_unit(engine):
    with pytest.raises(ValueError):
        engine["generate_distribution_strip_svg"]([], 0.0, "weeks")


@pytest.mark.parametrize("date_str", [None] + list(CHARTS), ids=["1982-petoskey"] + list(CHARTS))
def test_hit_strip_carries_one_tick_per_target_and_one_now(engine, date_str):
    """The house-master's direction drawn: one <line class="hit"> per row
    of sahl_house_master_direction with its arc and target, on the same
    0-120 axis as the distribution strips, the present marked once."""
    chart, latlon, b = _bundle(engine, date_str)
    rows = b["hm_direction"]
    if not rows:
        pytest.skip("no house-master direction for this chart")
    span = engine["PN4_DISTRIBUTION_SPAN_YEARS"]
    svg = engine["generate_hit_strip_svg"](rows, float(b["age"]), span, "Hits & more")
    root = ET.fromstring(svg)
    hits = [l for l in root.iter(SVG + "line") if l.get("class") == "hit"]
    assert len(hits) == len(rows)
    by_target = {h.get("data-target"): float(h.get("data-arc")) for h in hits}
    for r in rows:
        assert by_target[r["Target"]] == pytest.approx(float(r["Arc (years)"]), abs=1e-3)
    nows = [l for l in root.iter(SVG + "line") if l.get("class") == "now"]
    assert len(nows) == (1 if 0.0 <= float(b["age"]) <= span else 0)
    assert "Hits &amp; more" in svg
    texts = [t.text for t in root.iter(SVG + "text") if t.text]
    assert any(engine["POINT_GLYPHS"]["Saturn"] in t or engine["POINT_GLYPHS"]["Mars"] in t for t in texts)


# --- The Date column (Figure 22's shape) ------------------------------------------------

def test_distribution_rows_carry_the_date_each_segment_opens_on(engine):
    """PN IV Figure 22's eight printed dates, all of them: a mean year of
    365.2425 days from the birth in UT reproduces every one (365.25 puts
    Oct 19 2024 and Dec 19 2026 a day late; local civil time puts Jul 2
    and Aug 26 2020 a day early). The same on a Julian-calendar chart
    must stay in the Julian calendar."""
    lat, lon = 44 + 58 / 60 + 48 / 3600, -(93 + 15 / 60 + 49 / 3600)
    chart = engine["calculate_traditional_chart"](datetime(2019, 4, 27, 10, 13, 0), lat, lon)
    segs = engine["pn4_distribution_from_ascendant"](chart["planetary_data"], chart["ascendant"], chart["obliquity"], lat)
    rows = engine["_pn4_distribution_rows"](segs, None, origin_jd=chart["julian_day"])
    assert [r["Date"] for r in rows[:8]] == ["2019-04-27", "2020-07-02", "2020-08-26", "2021-08-24",
                                              "2023-08-20", "2024-10-19", "2025-01-30", "2026-12-19"]
    assert list(rows[0]) == ["From age", "To age", "Date", "Lasting", "Distributor", "Partner", "By", "Rank", "Opened by", "Now"]
    assert "Date" not in engine["_pn4_distribution_rows"](segs, None)[0]
    chart, latlon, b = _bundle(engine, "1240-05-23")
    assert b["distribution_rows"][0]["Date"] == "1240-05-23"
    assert b["small_days_rows"][0]["Date"] == f"{engine['pn4_datetime_from_jd'](b['jd_sr']):%Y-%m-%d}"


# --- The Timing page ---------------------------------------------------------------------

@pytest.mark.parametrize("view", ["Year", "Year over root", "Month over year and root", "Month", "Profection"])
def test_timing_page_draws_every_view(view):
    at = make_app(date="1240-05-23", page="timing")
    at.session_state["_timing_wheel_view"] = view
    at.session_state["_target_mode"] = "Age"
    at.session_state["_target_age"] = 43
    at.run()
    assert_no_exception(at, f"timing view {view}")
    assert at.main.selectbox(key="timing_wheel_view").value == view
    # Five pictures at least: the wheel and the four distributions' strips.
    assert len(at.main.image) >= 5, [i for i in at.main.image]
    assert [d for d in at.main.download_button if "wheel" in d.label]


def test_timing_page_toggles_and_order_render():
    for order in ["Nativity inside (Dykes)", "Revolution inside (Abu Ma'shar's order, PN IV I.6)"]:
        at = make_app(date="1240-05-26", page="timing")
        for key, value in {"_timing_wheel_view": "Year over root", "_wheel_order": order,
                           "_timing_lots": True, "_timing_rays": True, "_timing_twelfths": True,
                           "_timing_bounds": False, "_wheel_layout": "Wide",
                           "_target_mode": "Age", "_target_age": 30}.items():
            at.session_state[key] = value
        at.run()
        assert_no_exception(at, f"timing toggles, {order}")
        assert at.main.radio(key="wheel_order").value == order
        assert at.main.checkbox(key="timing_rays").value is True
        assert at.main.checkbox(key="timing_bounds").value is False


def test_chart_page_offers_the_bounds_ring_and_a_download():
    at = make_app(page="chart").run()
    assert_no_exception(at, "chart")
    assert at.main.checkbox(key="chart_bounds").value is True
    assert [d for d in at.main.download_button if "wheel" in d.label]
    off = make_app(page="chart")
    off.session_state["_chart_bounds"] = False
    off.run()
    assert_no_exception(off, "chart, bounds off")
    assert off.main.checkbox(key="chart_bounds").value is False


def test_timing_page_tabs_are_a_reading_that_survives_navigation():
    """Six chapters; the stored tab is the one selected on the next
    render, and every table is still reachable inside its tab."""
    at = make_app(date="1240-05-23", page="timing")
    at.session_state["_timing_tab"] = "Distributions"
    at.run()
    assert_no_exception(at, "timing, Distributions tab")
    labels = [t.label for t in at.main.tabs]
    assert labels == ["The revolution", "Indicators of the year", "Distributions", "The releaser",
                      "Days and months", "Fardar, ages and reference tables"]
    assert at.session_state["timing_tab"] == "Distributions"
    assert len(at.main.dataframe) >= 30
    # The wheel controls: a selectbox for the view, the rest behind the popover.
    assert at.main.selectbox(key="timing_wheel_view").value == "Year"
    assert at.main.radio(key="wheel_order").value.startswith("Nativity")
