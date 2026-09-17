"""Nothing-lost check for a readability branch: every sentence and every
locator token in a base revision's page text must still be somewhere in
the working tree's page text.

Usage, from the repository root:

    python tests/tools/prose_preserved.py <base-ref> [--engine] [--summary]

The base corpus is ``git show <base-ref>:app.py`` (and ``engine.py`` too
with ``--engine``); the branch corpus is the working tree's app.py and
engine.py, always both. On each side every string constant the AST holds
is taken -- plain constants and the constant parts of f-strings --
except docstrings, which are not page text. Every string is normalised:
whitespace runs to one space, bold markers removed, blockquote markers
stripped from the head of each line, surrounding whitespace stripped.

Sentences come from the base side only. A paragraph break in the raw
string (two consecutive newlines) is a boundary; within a paragraph the
normalised text splits after sentence-ending punctuation followed by
whitespace and an upper-case letter, digit, quote or bracket. A sentence
of 25 or more characters must be a substring of the branch corpus, which
is every normalised branch string joined with newlines.

Locators are the citation forms the three citation-scan tests recognise;
their patterns are copied below. Every token they match in the base
corpus must occur in the branch corpus.

Output: one line per miss, ``SENTENCE: <sentence>`` or ``LOCATOR:
<token>``, nothing on success; exit status 1 on any miss, else 0.
``--summary`` prints the counts to stderr. This file is a script, not a
test: pytest does not collect it.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Copied from tests/test_sahl_citations.py, tests/test_nativities_citations.py
# and tests/test_abu_mashar_citations.py (in that order); keep in step with
# them. In turn: a chapter-and-sentence form for the Introduction's third
# chapter; an aphorism number with an optional sentence or range; a
# Nativities chapter (dotted) with an optional range; a bare dotted chapter
# after the chapter abbreviation; a Great Introduction book-seven section
# with an optional paragraph list.
LOCATOR_PATTERNS = (
    re.compile(r"Ch\.\s?3,\s*(\d+)(?:-(\d+))?"),
    re.compile(r"Aphorisms?\s+#(\d+)(?:,\s*(\d+)(?:-(\d+))?)?"),
    re.compile(r"Nativities,?\s*(?:Ch\.?\s*)?(\d+(?:\.\d+)*)(?:\s*-\s*(\d+(?:\.\d+)*))?"),
    re.compile(r"Ch\.\s*(\d+(?:\.\d+)*)"),
    re.compile(r"VII\.(\d)(?:,\s*((?:\d+(?:-\d+)?)(?:(?:,\s*|\s+and\s+)\d+(?:-\d+)?)*))?"),
)

MIN_SENTENCE = 25
PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
# Sentence-ending punctuation, any closing quotes or brackets, whitespace,
# then the start of the next sentence: an upper-case letter, a digit, an
# opening quote or an opening bracket. The closers stay with the sentence.
SENTENCE_BOUNDARY = re.compile(r"([.!?][)\"'”’\]]*)\s+(?=[A-Z0-9\"'“‘(\[])")
BLOCKQUOTE = re.compile(r"^\s*>\s?", re.MULTILINE)
WHITESPACE = re.compile(r"\s+")


def strings_of(source: str) -> list[str]:
    """Every string constant in the source, in order, docstrings excluded."""
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            first = node.body[0] if node.body else None
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return [node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings]


def normalise(text: str) -> str:
    text = BLOCKQUOTE.sub("", text)
    text = text.replace("**", "")
    return WHITESPACE.sub(" ", text).strip()


def sentences_of(raw: str) -> list[str]:
    """The sentences of one raw base string, normalised, of MIN_SENTENCE
    characters or more."""
    out = []
    for paragraph in PARAGRAPH_BREAK.split(raw):
        text = normalise(paragraph)
        if not text:
            continue
        parts = SENTENCE_BOUNDARY.split(text)
        # split() with one group alternates text, separator, text, ...
        pieces = [parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
                  for i in range(0, len(parts), 2)]
        out.extend(p.strip() for p in pieces if len(p.strip()) >= MIN_SENTENCE)
    return out


def locators_of(text: str) -> list[str]:
    found = []
    for pattern in LOCATOR_PATTERNS:
        found.extend(m.group(0) for m in pattern.finditer(text))
    return found


def base_source(ref: str, name: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{name}"],
                          check=True, capture_output=True, text=True).stdout


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base_ref", help="git revision the page text is compared against")
    parser.add_argument("--engine", action="store_true",
                        help="take the base corpus from engine.py as well as app.py")
    parser.add_argument("--summary", action="store_true",
                        help="print counts (base sentences, base locators, misses) to stderr")
    args = parser.parse_args(argv)

    base_files = ["app.py"] + (["engine.py"] if args.engine else [])
    base_strings = []
    for name in base_files:
        base_strings.extend(strings_of(base_source(args.base_ref, name)))
    branch_strings = []
    for name in ("app.py", "engine.py"):
        branch_strings.extend(strings_of((ROOT / name).read_text()))
    branch_text = "\n".join(normalise(s) for s in branch_strings)

    base_sentences, seen = [], set()
    for raw in base_strings:
        for sentence in sentences_of(raw):
            if sentence not in seen:
                seen.add(sentence)
                base_sentences.append(sentence)
    base_locators, seen = [], set()
    for token in locators_of("\n".join(normalise(s) for s in base_strings)):
        if token not in seen:
            seen.add(token)
            base_locators.append(token)

    misses = 0
    for sentence in base_sentences:
        if sentence not in branch_text:
            print(f"SENTENCE: {sentence}")
            misses += 1
    for token in base_locators:
        if token not in branch_text:
            print(f"LOCATOR: {token}")
            misses += 1
    if args.summary:
        print(f"base sentences: {len(base_sentences)}; base locators: {len(base_locators)}; "
              f"misses: {misses}", file=sys.stderr)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
