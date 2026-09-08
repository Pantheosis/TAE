"""Every citation of Sahl's Introduction Ch. 3 and of the Fifty Aphorisms in
app.py must name a sentence the text has -- and, for the Aphorisms, a
sentence that belongs to the aphorism cited.

Ch. 3 runs sentences 2..132 in one sequence (sentence 99 is used twice in
the OCR, which does not affect a range check). The Aphorisms run 1..107 in
one sequence with each aphorism opening inside a numbered sentence, so
"#44, 87-89" can be checked against aphorism 44's own span (87..89), not
merely against 107. Both maps are vendored; with the corpus on disk they
are re-derived from the files.

Written 2026-09-08 with synthesis/12_sahl_ch3_and_aphorisms_citation_audit.md,
which found every citation of both texts supported.
"""
import os
import re
from pathlib import Path

import pytest

from conftest import app_source

CH3_MIN, CH3_MAX = 2, 132

# aphorism number -> (first sentence, last sentence)
APHORISM_SPANS = {
    1: (2, 7), 2: (8, 10), 3: (11, 11), 4: (12, 16), 5: (17, 19), 6: (20, 20),
    7: (21, 21), 8: (22, 22), 9: (23, 23), 10: (24, 24), 11: (25, 25),
    12: (26, 26), 13: (27, 29), 14: (30, 30), 15: (31, 34), 16: (35, 37),
    17: (38, 39), 18: (40, 40), 19: (41, 42), 20: (43, 43), 21: (44, 46),
    22: (47, 47), 23: (48, 48), 24: (49, 49), 25: (50, 50), 26: (51, 52),
    27: (53, 53), 28: (54, 55), 29: (56, 57), 30: (58, 58), 31: (59, 60),
    32: (61, 62), 33: (63, 63), 34: (64, 65), 35: (66, 68), 36: (69, 70),
    37: (71, 71), 38: (72, 73), 39: (74, 74), 40: (75, 79), 41: (80, 81),
    42: (82, 84), 43: (85, 86), 44: (87, 89), 45: (90, 92), 46: (93, 95),
    47: (96, 98), 48: (99, 102), 49: (103, 104), 50: (105, 107),
}

# "Ch.3, 6", "Ch. 3, 24-27", "Introduction Ch.3, 12-18" -- but not "Ch. 3.11, 2"
# (On Nativities), which has a dot after the 3 instead of a comma.
CH3_CITE = re.compile(r"Ch\.\s?3,\s*(\d+)(?:-(\d+))?")
# "Aphorism #44", "Aphorisms #44, 87-89", "Aphorism #45 (misstated"
APH_CITE = re.compile(r"Aphorisms?\s+#(\d+)(?:,\s*(\d+)(?:-(\d+))?)?")

CORPUS_DIR = Path(os.environ.get(
    "CORPUS_DIR", Path.home() / "Desktop" / "Fifty Aphorism OCR Project" / "consolidated_texts"))
CH3_FILE = CORPUS_DIR / "sahl_introduction_ch3.md"
APH_FILE = CORPUS_DIR / "fifty_aphorisms.md"


def ch3_citations():
    out = []
    for n, line in enumerate(app_source().split("\n"), 1):
        for m in CH3_CITE.finditer(line):
            out.append((n, int(m.group(1))))
            if m.group(2):
                out.append((n, int(m.group(2))))
    return out


def aphorism_citations():
    """(line, aphorism, sentence-or-None)"""
    out = []
    for n, line in enumerate(app_source().split("\n"), 1):
        for m in APH_CITE.finditer(line):
            a = int(m.group(1))
            if not m.group(2):
                out.append((n, a, None))
                continue
            out.append((n, a, int(m.group(2))))
            if m.group(3):
                out.append((n, a, int(m.group(3))))
    return out


def test_every_cited_ch3_sentence_exists():
    cites = ch3_citations()
    assert len(cites) > 60, f"only {len(cites)} Ch. 3 citations found -- extractor broken?"
    bad = sorted({(n, p) for n, p in cites if not CH3_MIN <= p <= CH3_MAX})
    assert not bad, f"app.py cites Introduction Ch. 3 sentences that do not exist: {bad}"


def test_every_cited_aphorism_and_sentence_exists():
    cites = aphorism_citations()
    assert len(cites) > 15, f"only {len(cites)} Aphorism citations found -- extractor broken?"
    bad_num = sorted({(n, a) for n, a, _s in cites if a not in APHORISM_SPANS})
    assert not bad_num, f"app.py cites aphorisms that do not exist: {bad_num}"
    bad_sent = sorted({(n, a, s) for n, a, s in cites
                       if s is not None and not APHORISM_SPANS[a][0] <= s <= APHORISM_SPANS[a][1]})
    assert not bad_sent, f"app.py cites sentences outside the aphorism's own span: {bad_sent}"


ORDINALS = {w: i for i, w in enumerate(
    "first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth "
    "thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth".split(), 1)}
TENS = {"twent": 20, "thirt": 30, "fort": 40, "fift": 50}


def ordinal_to_int(word):
    if word in ORDINALS:
        return ORDINALS[word]
    m = re.match(r"(twent|thirt|fort|fift)(?:ieth|y-(\w+))$", word)
    assert m, word
    return TENS[m.group(1)] + (ORDINALS[m.group(2)] if m.group(2) else 0)


def corpus_aphorism_spans():
    text = APH_FILE.read_text(encoding="utf-8")
    starts = [(int(m.group(1)), ordinal_to_int(m.group(2)))
              for m in re.finditer(r"\**(\d+)\**\s*\*The ([a-z-]+):\*", text)]
    last = max(int(m) for m in re.findall(r"(?:^|\s|\*)(\d{1,3})(?:\*\*)?\s+[A-Z\[]", text, re.M))
    spans = {}
    for (s, a), (s_next, _) in zip(starts, starts[1:] + [(last + 1, None)]):
        spans[a] = (s, s_next - 1)
    return spans


def corpus_ch3_max():
    text = CH3_FILE.read_text(encoding="utf-8").split("## Supplementary reference captures")[0]
    nums = [int(m) for m in re.findall(r"(?:^|\s|\*)(\d{1,3})(?:\*\*)?\s+[A-Z\[]", text, re.M)]
    return max(n for n in nums if n <= 200)


@pytest.mark.skipif(not (CH3_FILE.is_file() and APH_FILE.is_file()),
                    reason="corpus not on this machine (CI): the vendored maps still guard the citations")
def test_vendored_maps_match_the_corpus():
    assert corpus_ch3_max() == CH3_MAX
    assert corpus_aphorism_spans() == APHORISM_SPANS
