"""The wheel's own symbol font, embedded -- 2026-09-15.

Item 13 of `docs/UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` (brief
#8's second half), ruled on the same day: a symbol-font subset embedded in
every SVG the app draws, and nothing else -- no general-use font, no
`server.enableStaticServing`, no launcher change. `_WHEEL_FONT` (engine.py)
used to name three system fonts and hope one was installed; an SVG shown
through `st.image` or opened as a download cannot load a web font at all,
so the astrological glyphs depended on what each viewing machine happened
to have. This module is a data URI that makes every picture self-contained.

## The character list, and where it came from

The brief that authorised this build supplied a candidate list of 32
characters (31 symbols plus U+FE0E) and asked for it to be CONFIRMED by
scanning the four renderers rather than trusted -- every non-ASCII
character in `SIGN_GLYPHS`, `POINT_GLYPHS` and `_ASPECT_GLYPH` (engine.py),
plus any literal the renderers write into SVG text. That scan found a
different list from the one supplied:

- The candidate list's right arrow (U+2192) is NOT written by any of the
  four renderers. It is a table cell elsewhere in the file (the aspects
  page's "Connecting planet" column, `f"{applicant} -> {receiver}"`,
  `st.dataframe` text, not SVG) -- page text, out of this branch's scope
  under "no page text changes at all."
- Three characters the candidate list omitted ARE written into SVG text by
  the renderers and are not ASCII: the degree sign `deg` (U+00B0, e.g.
  `f'{d:02d}deg'` at the planet-degree label and the hub's lat/long line),
  the middle dot (U+00B7, the hub's "Whole sign : Alchabitius" line and the
  wide layout's "Lord of the day : Lord of the hour" line) and the en dash
  (U+2013, the wide positions panel's "no speed data" motion cell).

The confirmed list is 33 symbols plus U+FE0E (`_VS`, the text-presentation
selector engine.py already carries on every glyph so a font that also maps
these code points to an emoji-style presentation is not offered the choice
-- kept exactly as it is; this branch does not touch it):

    deg . - ... ' Rx (x) sq tri Sun NNode SNode Conj Opp
    Moon Mercury Venus Mars Jupiter Saturn
    Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius
    Capricorn Aquarius Pisces  sextile

(written here in ASCII because this docstring must stay page-text-clean of
the literal glyphs per docs/page-text-no-build-process conventions that
apply to engine.py generally; the exact code points are COVERED and
KNOWN_UNCOVERED below, and the source characters themselves are visible in
SIGN_GLYPHS / POINT_GLYPHS / _ASPECT_GLYPH in engine.py.)

## Coverage: two source files, and a real gap

The two files named in the brief, as shipped by Arch Linux's `noto-fonts`
package (version 1:2026.09.01-1, licence OFL-1.1-no-RFN per `pacman -Qi`):

    /usr/share/fonts/noto/NotoSansSymbols-Regular.ttf   "Noto Sans Symbols",   Version 2.003; ttfautohint (v1.8.4.7-5d5b)
    /usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf  "Noto Sans Symbols 2", Version 2.008

Checked per character with `fontTools.ttLib.TTFont.getBestCmap()` (and,
because a "symbol" TTF can carry a Symbol-platform (3,0) cmap instead of a
Unicode one, cross-checked against the union of every subtable in each
font's `cmap` -- same result both ways): between the two files, 26 of the
33 symbol code points are covered and 7 are not, in EITHER file:

    deg (U+00B0), . (U+00B7), - (U+2013), ... (U+2026),
    ' (U+2032, prime), Rx (U+211E), (x) (U+2297, circled times)

None of Sun/Moon/Mercury/.../Pisces/sextile/square/triangle is among the
seven -- the Sun symbol (U+2609) and the square and triangle used for the
square and trine aspects (U+25A1, U+25B3) live in Symbols2 and nowhere in
Symbols; the rest of the planets, the nodes, the twelve signs, the sextile,
conjunction and opposition glyphs live in Symbols and nowhere in Symbols2
-- which is why this is TWO embedded faces, not one, exactly the
contingency the brief named. But (x), the Lot of Fortune's own glyph in
POINT_GLYPHS, is in NEITHER file, and neither are six punctuation-like
marks the renderers also write (the degree sign, the middle dot, the en
dash, the truncation ellipsis, the prime used for minutes at the hub and
the wide panel, and the Rx retrograde mark). This is not a subsetting
choice -- `pyftsubset --unicodes=U+2297` on either file produces a font
with zero glyphs for it, because the character is not in the source. The
finding is reported in full in `docs/UI_CHANGES_2026-09-15_symbol_font.md`;
these seven code points are NOT embedded, KNOWN_UNCOVERED names them
exactly, and they keep depending on the system fallback stack that
`_WHEEL_FONT` already carried -- the exact behaviour they had before this
branch, no better and no worse. Six of the seven are common Latin-1/General
Punctuation characters present in nearly every installed sans-serif font;
only Rx and (x) share the fragility this branch exists to fix for the other
26, and nothing in the two named source files can be subset to supply them.

## The command

    uvx --from 'fonttools[woff]' pyftsubset \\
        /usr/share/fonts/noto/NotoSansSymbols-Regular.ttf \\
        --output-file=TAE-Symbols-Regular.woff2 \\
        --unicodes=U+260A,U+260B,U+260C,U+260D,U+263D,U+263F,U+2640,U+2642,U+2643,U+2644,\\
    U+2648,U+2649,U+264A,U+264B,U+264C,U+264D,U+264E,U+264F,U+2650,U+2651,U+2652,U+2653,U+26B9 \\
        --flavor=woff2 --no-hinting --desubroutinize --layout-features=

    uvx --from 'fonttools[woff]' pyftsubset \\
        /usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf \\
        --output-file=TAE-Symbols2-Regular.woff2 \\
        --unicodes=U+2609,U+25A1,U+25B3 \\
        --flavor=woff2 --no-hinting --desubroutinize --layout-features=

`fontTools` is not a runtime dependency of this app -- both subsetting runs
were one-off, through `uvx`, and only the two base64 WOFF2 blobs below are
committed. `--layout-features=` (empty) drops every GSUB/GPOS feature table
subsetting would otherwise keep (kerning pairs, ligatures) -- none of which
these fonts carry for dingbat code points, but the flag makes the omission
a decision rather than an accident. `--desubroutinize` and `--no-hinting`
shrink the glyf/CFF program to the minimum a symbol at fixed SVG sizes
needs. Verified after the fact (`fontTools.ttLib.TTFont` reopened on each
output, `fonttools[woff]` again for the brotli WOFF2 decoder): each
output's cmap is EXACTLY its intended code points, no more and no fewer.

Sizes: TAE-Symbols-Regular.woff2 is 2,800 bytes (23 glyphs), base64 3,736
characters; TAE-Symbols2-Regular.woff2 is 708 bytes (3 glyphs), base64 944
characters. 4,680 bytes of base64 land in every SVG this app draws.

## The licence

Both source files declare, in their own `name` table (ID 13, License
description, identical in both): "This Font Software is licensed under the
SIL Open Font License, Version 1.1. This license is available with a FAQ
at: https://scripts.sil.org/OFL" (ID 0, Copyright: "Copyright 2022 The Noto
Project Authors (https://github.com/notofonts/symbols)"). The FULL OFL 1.1
legal text was sought on this machine and not found where the brief
expected it: `pacman -Qi noto-fonts` reports "Licenses: OFL-1.1-no-RFN",
but the file the package actually ships at
`/usr/share/licenses/noto-fonts/LICENSE` is the Apache License, Version
2.0, verbatim -- a packaging mismatch, not the OFL text (three other
packages on this machine -- ttf-opensans, ttf-fantasque-nerd,
ttf-fira-sans -- do ship a correct `OFL.txt`, none of them Noto's).
`fonts/OFL.txt` in this repository therefore carries the font's own
name-table attestation above, verbatim, and says plainly that the full SIL
OFL 1.1 text (https://scripts.sil.org/OFL) still needs to be added to that
file to complete the notice -- follows the brief's own fallback ("or say it
must be added") rather than retyping 100-odd lines of licence text from
memory into a file whose entire purpose is to be exact.
"""
import base64

FAMILY = 'TAE Symbols'

# ---- Source ----------------------------------------------------------

SOURCE_FONTS = (
    {'file': 'NotoSansSymbols-Regular.ttf', 'family': 'Noto Sans Symbols',
     'version': 'Version 2.003; ttfautohint (v1.8.4.7-5d5b)',
     'package': 'noto-fonts 1:2026.09.01-1 (Arch Linux, extra), licence OFL-1.1-no-RFN'},
    {'file': 'NotoSansSymbols2-Regular.ttf', 'family': 'Noto Sans Symbols 2',
     'version': 'Version 2.008',
     'package': 'noto-fonts 1:2026.09.01-1 (Arch Linux, extra), licence OFL-1.1-no-RFN'},
)

SUBSET_COMMAND = (
    "uvx --from 'fonttools[woff]' pyftsubset /usr/share/fonts/noto/NotoSansSymbols-Regular.ttf "
    "--output-file=TAE-Symbols-Regular.woff2 "
    "--unicodes=U+260A,U+260B,U+260C,U+260D,U+263D,U+263F,U+2640,U+2642,U+2643,U+2644,"
    "U+2648,U+2649,U+264A,U+264B,U+264C,U+264D,U+264E,U+264F,U+2650,U+2651,U+2652,U+2653,U+26B9 "
    "--flavor=woff2 --no-hinting --desubroutinize --layout-features=",
    "uvx --from 'fonttools[woff]' pyftsubset /usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf "
    "--output-file=TAE-Symbols2-Regular.woff2 "
    "--unicodes=U+2609,U+25A1,U+25B3 "
    "--flavor=woff2 --no-hinting --desubroutinize --layout-features=",
)

# The 26 code points actually embedded (Noto Sans Symbols' 23, Noto Sans
# Symbols 2's 3 -- disjoint; see the docstring). Every one of SIGN_GLYPHS,
# POINT_GLYPHS and _ASPECT_GLYPH's code points is in here EXCEPT the Lot of
# Fortune's (x), U+2297 -- see KNOWN_UNCOVERED. A code point added to one of
# those tables later that is not in COVERED and not in KNOWN_UNCOVERED is a
# NEW gap: tests/test_symbol_font_2026_09_15.py fails loudly on it rather
# than silently shipping a glyph no embedded face carries.
COVERED = frozenset({
    0x25A1, 0x25B3,                                             # square, triangle (Symbols 2)
    0x2609,                                                     # Sun (Symbols 2)
    0x260A, 0x260B, 0x260C, 0x260D,                              # N/S node, conjunction, opposition
    0x263D, 0x263F,                                             # Moon, Mercury
    0x2640, 0x2642, 0x2643, 0x2644,                              # Venus, Mars, Jupiter, Saturn
    0x2648, 0x2649, 0x264A, 0x264B, 0x264C, 0x264D,              # Aries .. Virgo
    0x264E, 0x264F, 0x2650, 0x2651, 0x2652, 0x2653,              # Libra .. Pisces
    0x26B9,                                                     # sextile
})

# The glyph-table code point neither source font contains, in either its
# Unicode cmap subtable or its Symbol-platform one (checked both ways,
# docstring above). Not a subsetting oversight: pyftsubset cannot retain
# what pyftsubset's own source file does not have.
KNOWN_UNCOVERED = frozenset({0x2297})   # (x), Lot of Fortune (POINT_GLYPHS)

# The other six non-ASCII characters the four renderers write into SVG
# text but which are not part of SIGN_GLYPHS / POINT_GLYPHS / _ASPECT_GLYPH
# (the degree sign, middle dot, en dash, ellipsis, prime and Rx mark) are
# ALSO absent from both source fonts. They are not in scope for the
# glyph-table completeness test (they are not glyph-table entries) but are
# recorded here for the one test that does check them directly.
OTHER_UNCOVERED_LITERALS = frozenset({0x00B0, 0x00B7, 0x2013, 0x2026, 0x2032, 0x211E})

# ---- The subsets themselves, base64 WOFF2 -----------------------------

_SYMBOLS_WOFF2_B64 = (
    "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"
)

_SYMBOLS2_WOFF2_B64 = (
    "d09GMgABAAAAAALEAA4AAAAABZAAAAJyAAICDAAAAAAAAAAAAAAAAAAAAAAAAAAAGyAcIAZgAEQKgWiBXgE2AiQDEAsKAAQg"
    "BYNwByAXJBgKG4kEAJ4FdmvHkaIY7Ra2Rr0W+xvmeOgZc/9uqmmY5CVeFw+NJB47qYpGmmVKII79vJ2+izUmvwCjCoh/A41d"
    "7+oVHCZqGKm1a1cThLf7/eZhIskCjQss4nEYWGYZBjUDJXOzocvp49EPsLHxSR/0RdagselBF/1jYwEmmGXlExPIo4Cit6Z5"
    "g9ywhHR7Vfp7AnWz1Ihtt6oJOIow/QfQc7iYxpjRyCvbgCN/8zilRgGCT9zf3lFbSpyvrUZyGQkTkuKSPiAg58IGFtGQKGCI"
    "LjDEMAaqqpK1J2Irkvv/D2vbU99T7eMXEDBkEVRRwSZwWb2WlAqVQacrhhSXxAxHhyniW28dYsspeQeUGP9B+dQXCuMmaKFS"
    "ATFeDHgkAhjIO8nT7Tz2Ve5hHIe9ELobPnc5rPf+7P571HxVPmyqaymtyaSlauu0pA8orUfmcLKuVktB5I7k4mBaZ2dasLjY"
    "KgKCaSOkU0SgDw0KmdtrBhDIIjhthr33inV/HDr9Az6/PArwu998/vnfwfpnJABlCYK/9yu9A0xe1kCgfcXSpjcLpCU1oZHn"
    "IFCsR14QcKziGF1ULnAHYiasW2BS2wtTsOuCKdoIFVMyiqpHLxvHiELYmCAXs1EmHkiqZKlSIU1MhiE1MA8MqeOCWQwb5IHk"
    "8/IwwVzckGgmHh5j3HIlSTLKzMPEa0CiQZhdEseprxyBOXi4JXELshuA2bjF3Nxu1M/BHdl9ek6cqsGwUV6sn6tIlMzCbFql"
    "astS2tNMHaUSqRJmcfsqNM62GObiZoY5IO+Z7RsiOpKdLugGignx/0H/KK8zdTOvEciJai8Gozk8UQUA"
)

# ---- CSS ---------------------------------------------------------------

_FACES = (
    # unicode-range restricts the browser's per-glyph matching, within
    # 'TAE Symbols', to the code points each face actually carries -- so a
    # code point in neither range (the seven in KNOWN_UNCOVERED /
    # OTHER_UNCOVERED_LITERALS) skips 'TAE Symbols' entirely and reaches
    # the next family in _WHEEL_FONT's stack, exactly as it did before this
    # font existed. Without unicode-range a browser is free to commit to
    # one face for the whole family and never try the other.
    (_SYMBOLS_WOFF2_B64, 'U+260A-260D, U+263D, U+263F-2640, U+2642-2644, U+2648-2653, U+26B9'),
    (_SYMBOLS2_WOFF2_B64, 'U+25A1, U+25B3, U+2609'),
)


def font_face_css():
    """The @font-face rule(s) for FAMILY, both faces, srcs as data URIs.
    Called once per SVG, inside a <style> element right after the opening
    <svg> tag -- the only place any of the four renderers touch."""
    return ''.join(
        "@font-face{{font-family:'{family}';font-weight:normal;font-style:normal;"
        "unicode-range:{rng};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        .format(family=FAMILY, rng=rng, b64=b64)
        for b64, rng in _FACES
    )
