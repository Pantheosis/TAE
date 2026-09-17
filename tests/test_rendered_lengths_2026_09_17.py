"""The plan's caption ceiling, applied to what is rendered rather than to
app.py's source: no st.caption on any page, at either reading depth, outside
a notes disclosure, is over 400 characters.

tests/test_text_lengths_2026_09_17.py measures the source by AST and sees a
subscript as 0, so a caption printed from a dict the engine fills
(`st.caption(_y['readings'])`, SAHL_1_20_READINGS at 1,850 characters, on
The releaser page until readability branch C's last round) was invisible to
it, as it was to the handoff's engine-constant table and the plan's list of
note constants. This test walks the rendered page instead: every caption
node under `at.main`, skipping the ones inside a notes disclosure (the book
icon or the help icon, as the table walker skips them) since a disclosure is
where long text is meant to live. The markdown paragraphs are not measured:
their length is the owner's call, not a rule.
"""
from __future__ import annotations

import pytest

from conftest import NOTES_EXPANDER_ICON, PAGES, READING_DEPTHS, assert_no_exception, make_app

CAPTION_CEILING = 400
DISCLOSURE_ICONS = (NOTES_EXPANDER_ICON, ":material/help:")


def _captions_outside_disclosures(node, out=None):
    out = [] if out is None else out
    for child in getattr(node, "children", {}).values():
        kind = getattr(child, "type", None)
        if kind in ("status", "expander") and getattr(child, "icon", None) in DISCLOSURE_ICONS:
            continue
        if kind == "caption":
            out.append(child.value)
        _captions_outside_disclosures(child, out)
    return out


@pytest.mark.parametrize("depth", READING_DEPTHS)
@pytest.mark.parametrize("page", PAGES)
def test_no_rendered_caption_outside_a_disclosure_is_over_the_ceiling(page, depth):
    at = make_app(page=page)
    at.session_state["_reading_depth"] = depth
    at.run()
    assert_no_exception(at, f"{page} under {depth}")
    captions = _captions_outside_disclosures(at.main)
    assert captions, page
    over = [(len(c), c[:80]) for c in captions if len(c) > CAPTION_CEILING]
    assert not over, f"{page} under {depth}: caption over {CAPTION_CEILING} characters outside a disclosure: {over}"
