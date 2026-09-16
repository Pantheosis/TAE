"""Every 'VII.N, P' citation of Abu Ma'shar's Great Introduction Book VII in
app.py must name a chapter that exists and a paragraph the chapter has.

Book VII's OCR carries the paragraph pin that On Nativities' could not: its
sentence numbers are clean, run 1..max per chapter, and its footnotes are
numbered continuously across the book, so a bare "44" is never a footnote.
The 2026-09-08 audit (docs/synthesis/11_abu_mashar_citation_audit.md) found
"VII.3, 19-20" (VII.3 ends at 11) -- this pin would have caught it -- and
"VII.5, 120" for the Resistance sentence at 118, which no range pin can.

MAX_PARAGRAPH is vendored from the full volume gr_intr/abu_mashar_great_
introduction.md (derived by script, each value checked against the
reading); with the corpus on disk a third test re-derives it from the file.
"""
import os
import re
from pathlib import Path

import pytest

from conftest import app_source
from corpus_paths import corpus_file

MAX_PARAGRAPH = {
    "VII.1": 39, "VII.2": 75, "VII.3": 11, "VII.4": 109, "VII.5": 142,
    "VII.6": 74, "VII.7": 22, "VII.8": 8, "VII.9": 37,
}

# "VII.5, 27", "VII.2, 60-61 and 72-74", "VII.2, 40, 48, 51-52", "VII.6, 13 and 36".
# The paragraph list stops at the first token that is not a number or range.
CITE = re.compile(r"VII\.(\d)(?:,\s*((?:\d+(?:-\d+)?)(?:(?:,\s*|\s+and\s+)\d+(?:-\d+)?)*))?")

CORPUS_FILE = corpus_file("gr_intr/abu_mashar_great_introduction.md")


def vii_citations():
    """(line, chapter, paragraph) for every paragraph cited; paragraph is None
    for a bare chapter citation."""
    out = []
    for n, line in enumerate(app_source().split("\n"), 1):
        if "VII." not in line:
            continue
        for m in CITE.finditer(line):
            # PN IV has a Book VII too (VII.8 is the Moon by transit, cited by
            # the planets-in-houses table): a citation whose nearest preceding
            # book label on the line is "PN IV" is Abu Ma'shar's Revolutions,
            # not the Great Introduction, and is not pinned here.
            before = line[:m.start()]
            if before.rfind("PN IV") > before.rfind("Gr. Intr."):
                continue
            ch = f"VII.{m.group(1)}"
            if not m.group(2):
                out.append((n, ch, None))
                continue
            for tok in re.split(r",\s*|\s+and\s+", m.group(2)):
                for p in tok.split("-"):
                    out.append((n, ch, int(p)))
    return out


def test_every_cited_vii_chapter_exists():
    cites = vii_citations()
    assert len(cites) > 150, f"only {len(cites)} citations found -- extractor broken?"
    bad = sorted({(n, ch) for n, ch, _p in cites if ch not in MAX_PARAGRAPH})
    assert not bad, f"app.py cites Book VII chapters that do not exist: {bad}"


def test_every_cited_vii_paragraph_is_in_range():
    cites = [(n, ch, p) for n, ch, p in vii_citations() if p is not None and ch in MAX_PARAGRAPH]
    assert len(cites) > 100, f"only {len(cites)} paragraph citations found -- extractor broken?"
    bad = sorted({(n, ch, p) for n, ch, p in cites if not 1 <= p <= MAX_PARAGRAPH[ch]})
    assert not bad, f"app.py cites Book VII paragraphs the chapter does not have: {bad}"


def corpus_max_paragraphs():
    lines = CORPUS_FILE.read_text(encoding="utf-8").split("\n")
    heads = [(i, m.group(1)) for i, l in enumerate(lines)
             if (m := re.match(r"^### Chapter (VII\.\d)", l))]
    # In the full volume, VII.9 is Book VII's last chapter, so the next
    # "### Chapter" heading (any book) or the next Book-level heading,
    # whichever comes first, ends it -- not the end of the file, which
    # would run the chapter into Book VIII.
    boundaries = [i for i, l in enumerate(lines)
                  if re.match(r"^### Chapter ", l) or re.match(r"^#{1,2} ", l)]
    sentence = re.compile(r"(?:^|(?<=[.)\]:;] )|(?<=\*\*))(\d{1,3})(?:\*\*)? (?=[A-Z\[<])")
    out = {}
    for a, ch in heads:
        b = next((i for i in boundaries if i > a), len(lines))
        nums = []
        for line in lines[a:b]:
            s = re.sub(r"<sup>.*?</sup>", "", line)
            if s.startswith(("<sup>", "*[", "|")):
                continue
            nums.extend(int(m.group(1)) for m in sentence.finditer(s))
        out[ch] = max(nums) if nums else 0
    return out


@pytest.mark.skipif(not CORPUS_FILE.is_file(), reason="corpus not on this machine (CI): "
                    "the vendored MAX_PARAGRAPH above still guards the citations")
def test_vendored_paragraph_maxima_match_the_corpus():
    """If the OCR is re-cut and a chapter gains or loses sentences, re-vendor
    deliberately rather than drift."""
    found = corpus_max_paragraphs()
    assert found == MAX_PARAGRAPH, f"corpus: {found}; vendored: {MAX_PARAGRAPH}"
