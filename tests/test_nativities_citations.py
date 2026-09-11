"""Every 'On Nativities Ch. X.Y' citation in app.py must name a chapter that
exists in Sahl's On Nativities.

The 2026-09-08 audit (synthesis/10_on_nativities_citation_audit.md) found
four citations of chapters that do not exist -- "Ch. 11.5", "Ch. 10.2.9",
"Ch. 3.1.2" -- and several more that name a real chapter but the wrong
one (5.2 for 5.3, 7.4 for 7.2, 11.4 for 11.2, 3.12 for 3.13). Paragraph
numbers CAN be pinned mechanically -- an earlier version of this docstring
said they could not, and the 2026-09-10 read-through (process/
SAHL_READTHROUGH_FINDINGS_2026-09-10.md Sec. 1c) measured 154 of 187
citation instances carrying an explicit sentence number, against a corpus
that numbers its sentences in the body text. What defeats a naive matcher
is only that sentences run *inline* within a paragraph, so a line-leading
match finds roughly half; process/sahl_corpus.py is a working accessor.
This test nonetheless holds only the chapter number -- extending it to the
sentence is possible and has not been done.

CHAPTERS is vendored from the headings of on_nativities.md (173 headings:
12 chapter-level, 161 sub-level), extracted 2026-09-08, so the test runs in
CI without the corpus. With the corpus on disk, a second test re-derives
the list from the file and checks the vendored copy against it.
"""
import os
import re
from pathlib import Path

import pytest

from conftest import app_source, engine

CHAPTERS = frozenset("""
1 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 1.10 1.11 1.12 1.13 1.14 1.15 1.16 1.17
1.18 1.19 1.20 1.21 1.22 1.23 1.24 1.25 1.26 1.27 1.28 1.29 1.30 1.31 1.32
1.33 1.34 1.35 1.36 1.37 1.38
2 2.1 2.2 2.3 2.4 2.5 2.6 2.7 2.8 2.9 2.10 2.11 2.12 2.13 2.14 2.15 2.16 2.17
2.18 2.19 2.20 2.21 2.22
3 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13
4 4.1 4.2 4.3 4.4 4.5 4.6 4.7 4.8 4.9 4.10 4.11 4.12 4.13 4.14 4.15 4.16 4.17
4.18 4.19 4.20
5 5.1 5.2 5.3 5.4 5.5 5.6
6 6.1 6.2 6.3 6.3.1 6.3.2 6.3.3 6.3.4 6.3.5 6.3.6 6.3.7 6.3.8 6.3.9 6.3.10
6.4 6.5 6.6 6.7 6.8 6.9 6.10
7 7.1 7.2 7.3 7.4 7.5 7.6 7.7 7.8
8 8.1 8.2 8.3 8.4 8.5 8.6 8.7
9 9.1 9.2 9.3 9.4 9.5
10 10.1 10.1.1 10.1.2 10.1.3 10.1.4 10.1.5 10.1.6
10.2 10.2.1 10.2.2 10.2.3 10.2.4 10.2.5 10.2.6 10.2.7 10.3
11 11.1 11.2 11.3 11.4
12 12.1 12.2
""".split())

# "On Nativities Ch. 1.22, 9", "On Nativities 1.23, 17", "Nativities Ch.1.22",
# "On Nativities Ch. 1.20-1.23" (both ends of a range).
CITE = re.compile(r"Nativities,?\s*(?:Ch\.?\s*)?(\d+(?:\.\d+)*)(?:\s*-\s*(\d+(?:\.\d+)*))?")
# Inside a LOT_DEFINITIONS row whose source is Sahl, a bare "Ch. 9.5, 3" in
# the note is also a Nativities citation.
BARE_CH = re.compile(r"Ch\.\s*(\d+(?:\.\d+)*)")

CORPUS_DIR = Path(os.environ.get(
    "CORPUS_DIR", Path.home() / "Desktop" / "Fifty Aphorism OCR Project" / "consolidated_texts"))
CORPUS_FILE = CORPUS_DIR / "on_nativities.md"
HEADING = re.compile(r"\[?Chapter\s*\[?\s*(\d+(?:\.\s?\]?\s?\d+)*)")


def nativities_citations():
    """(line, chapter) for every chapter number cited to On Nativities."""
    out = []
    for n, line in enumerate(app_source().split("\n"), 1):
        if "Nativities" not in line:
            continue
        for m in CITE.finditer(line):
            out.extend((n, g) for g in m.groups() if g)
    return out


def lot_row_citations(engine):
    out = []
    for d in engine["LOT_DEFINITIONS"]:
        if "Nativities" not in d["source"]:
            continue
        for field in ("source", "note"):
            out.extend((d["id"], c) for c in BARE_CH.findall(d[field]))
    return out


def test_every_cited_nativities_chapter_exists():
    cites = nativities_citations()
    assert len(cites) > 80, f"only {len(cites)} citations found -- extractor broken?"
    bad = sorted({(n, c) for n, c in cites if c not in CHAPTERS})
    assert not bad, f"app.py cites On Nativities chapters that do not exist: {bad}"


def test_every_lot_row_chapter_exists(engine):
    cites = lot_row_citations(engine)
    assert len(cites) > 30, f"only {len(cites)} lot-row citations found -- extractor broken?"
    bad = sorted({(i, c) for i, c in cites if c not in CHAPTERS})
    assert not bad, f"LOT_DEFINITIONS rows cite On Nativities chapters that do not exist: {bad}"


def corpus_chapters():
    nums = set()
    for line in CORPUS_FILE.read_text(encoding="utf-8").split("\n"):
        s = re.sub(r"<[^>]*>", "", line).strip().lstrip("#").strip().lstrip("*").strip()
        m = HEADING.match(s)
        if m:
            nums.add(re.sub(r"[\[\]\s]", "", m.group(1)))
    return nums


@pytest.mark.skipif(not CORPUS_FILE.is_file(), reason="corpus not on this machine (CI): "
                    "the vendored CHAPTERS list above still guards the citations")
def test_vendored_chapter_list_matches_the_corpus_headings():
    """If the OCR is re-cut and a heading appears or disappears, the vendored
    list must be re-vendored deliberately rather than drift."""
    found = corpus_chapters()
    assert found == set(CHAPTERS), (
        f"only in corpus: {sorted(found - CHAPTERS)}; only vendored: {sorted(CHAPTERS - found)}")
