"""The one root every corpus-reading test resolves (owner's decision,
2026-09-16): CORPUS_DIR defaults to the consolidated_texts_final checkout
and is overridden by the CORPUS_DIR environment variable (used in CI,
where it is left unset and every corpus test skips, and to point a run at
a different checkout, e.g. the older consolidated_texts one)."""
from __future__ import annotations

import os
from pathlib import Path

CORPUS_DIR = Path(os.environ.get(
    "CORPUS_DIR", Path.home() / "Desktop" / "Fifty Aphorism OCR Project" / "consolidated_texts_final"))


def corpus_file(rel: str) -> Path:
    """CORPUS_DIR / rel, for a corpus-relative path such as
    'gr_intr/abu_mashar_great_introduction.md'."""
    return CORPUS_DIR / rel
