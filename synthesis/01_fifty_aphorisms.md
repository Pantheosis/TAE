# Phase 1 — Sahl, *The Fifty Aphorisms* (complete)

Source: `fifty_aphorisms.md`, Sahl Vol. I pp. 76–88 (per the printed contents; the file carries no
page markers), sentences 1–107 in one continuous sequence, Figures 30–31, and a topic index table
at the head. Read end to end on 2026-09-08 before any `app.py` citation was opened. Companion:
`12_sahl_ch3_and_aphorisms_citation_audit.md`.

**Conventions.** Each aphorism is marked *"The Nth:"* inside the sentence that opens it; the
sentence numbers do **not** restart per aphorism. So "#44, 87–89" means aphorism 44, sentences
87–89. The aphorism→sentence map is vendored in `tests/test_sahl_citations.py`. Footnotes 1–63 run
continuously. Citation: **Aph. #N, S**.

**Dykes's own warning, verbatim** (`:3`): *"it is not always clear that all of the aphorisms are
mutually compatible; and some of them have absolute language that needs to be softened or moderated
by others, or by experience."* And on provenance: *"Most of these are probably taken or adapted from
some work of Māshā'allāh's, and many ultimately from other sources (several can be pretty reliably
traced to Theophilus)."*

**Standing policy** (`DOCTRINAL_CAVEATS.md`, decided 2026-09-07): **#45 is ascensional**, per
fn. 57, never the printed zodiacal wording; the engine abstains from it.

---

## 1. The map

| # | S | One line | Engine-relevant? |
|---|---|---|---|
| 1 | 2–7 | the Moon is *the* indicator; hands over to the first she connects with; "the bearer … the transferor" | context |
| 2 | 8–10 | infortunes restrained by reception (house/exaltation) or trine/sextile; fn. 2: being in a house ≠ reception | ✓ (reception) |
| 3 | 11 | fortunes good, infortunes bad | — |
| 4 | 12–16 | ★ unfortunate only when the infortune's rays strike the planet's **light** (fn. 4 → Ch. 3, 12–18); beyond the light it only "looks"; one full degree past = separated | ✓ |
| 5 | 17–19 | the "stakes of an infortune" (with, 4th, 7th, 10th from it); one full degree past ends the harm | ✓ (VII.6, 48–50 cognate) |
| 6 | 20 | Moon empty in course: "emptiness, idleness … corruption of all of [one's] purposes" | ✓ |
| 7–8 | 21–22 | the Moon's connection = the future; her separation = the past | — |
| 9 | 23 | own fall: "misfortune, worry, and confinement" | — |
| 10–12 | 24–26 | retrograde; stationary; infortunes | — |
| 13 | 27–29 | slow postpones; in Saturn's/Jupiter's houses likewise; in the light houses it hastens (fn. 14 → *On Times* Ch. 2, 2–3) | timing, recorded |
| 14 | 30 | after a completed connection, read the next | — |
| 15 | 31–34 | ★ last degree: strength gone to the next sign; **the 29th still counts**; three degrees of diffusion (fn. 16: Valens uses 3° either side) | ✓ |
| 16 | 35–37 | ★ escape by aspect (fn. 18) | ✓ |
| 17 | 38–39 | ★ escape by body; **"a connection does not nullify a uniting, while a uniting does nullify a connection, and an aspect does not cut off an aspect"** (fn. 21 → Ch. 3, 44–48) | ✓ |
| 18 | 40 | an eastern infortune in its own house/exaltation beats a retrograde benefic | — |
| 19 | 41–42 | infortunes as lords of the sought thing, hard by square/opposition "unless it was their house"; **better handing over than accepting** (fn. 24: Saturn can only hand over if retrograde) | ✓ |
| 20 | 43 | infortune in own house/exaltation refrains from evil unless retrograde in the Ascendant | — |
| 21 | 44–46 | a planet in a sign "of its own type"; water-and-oil vs water-and-milk (fn. 29) | — |
| 22–24 | 47–49 | fortunes lessen evil; infortunes by square/opposition lessen good; fortunes in aversion or retrograde "corrupting in the manner of the infortunes" | — |
| 25 | 50 | ⚠ received fortune stronger, received infortune "stronger for its harm" — fn. 30: *"I believe this is in error"*; Latin: *less* | — |
| 26–28 | 51–55 | alien infortunes worse; dignified angular infortune "like the strength of the fortunes"; fortunes with/without testimony | — |
| 29 | 56–57 | under the rays or opposing the Sun: "weak … the matters are base and small" | ✓ |
| 30 | 58 | own house/exaltation/triplicity converts evil to good | — |
| 31 | 59–60 | infortunes in the stakes of the Ascendant, or afflicting its lord by square/opposition, "the mightiest … for disaster"; fn. 35 marginal note on "stakes of the lord" | — |
| 32–33 | 61–63 | ★ glow = sect ("of the planets of the night and it is an indicator by day…"); a fortune out of its glow, alien, averse or under the rays "harms and is not beneficial" | ✓ |
| 34–35 | 64–68 | Jupiter loosens Saturn, Venus loosens Mars; handing over between fortunes/infortunes | — |
| 36 | 69–70 | fortunes by square dissolve; by trine "escape … and fall into another hardship" (fn. 42: the trine is in aversion to the square-placed malefic) — Fig. 30 | — |
| 37 | 71 | no dignity, no joy, falling: "no good in that planet" | — |
| 38 | 72–73 | ★ under the rays westernizing: "feeble"; retrograde: "difficult in all matters" | ✓ |
| 39 | 74 | ★ under the rays within **12°** weak, unless in the Sun's degree | ✓ |
| 40 | 75–79 | ★ eastern **12°** strong, **15°** strongest; western **7°–15°** "commences with weakness", 7° to the heart weakest; **in the heart = one degree** strong (fn. 44 → Heph. III.4, 5; cf. *Nativities* 1.22) — Fig. 31 | ✓ |
| 41 | 80–81 | exile is bad; not dignified but direct and in the 1st/10th/11th is excellent (fn. 47) | — |
| 42 | 82–84 | the acceptor western (in front of the Sun) weak; eastern "lively, strong" | ✓ |
| 43 | 85–86 | the eighth: a fortune gives nothing; infortunes' evil mighty | — |
| 44 | 87–89 | ★ **five degrees**: weak until 5° into a sign; not falling from a stake until 5° past it "from its rear"; fn. 56: *"as measured in diurnal motion"* | ✓ |
| 45 | 90–92 | ⚠ 15° after a stake "in the situation of one who is in the stake" — fn. 57: **misstated; ascensions, not zodiacal degrees**; correct at *Nativities* 2.13, 48–51 | abstained (policy) |
| 46–47 | 93–98 | quadruplicities: fixed = stability; two bodies = repetition; convertible = quick change | — |
| 48 | 99–102 | ★ station to retrograde = collapse; station to direct = "forward movement … with no difficulty" | ✓ |
| 49 | 103–104 | an unfortunate Moon on the day of the question; place from the Ascendant alters it (fn. 61 photo-confirmed reading) | — |
| 50 | 105–107 | the Moon's next connection; lord of the Ascendant in detriment = reluctance | — |

## 2. ★ The sentences the engine rests on, verbatim

> "**12** And a planet is not said to be unfortunate until the infortune casts rays upon its light,
> according to what I described to you of their lights. **13** When it goes beyond the boundary of
> the light, it is said to be 'looking at' the infortune, and it does not have power over corruption.
> **14** And when the planet goes beyond the infortune by one full degree, it introduces anxieties
> which do not assault the body, and the infortune does not have power over more than that, because
> it is separating." — Aph. #4, 12–14 (`:33–43`)

> "**31** If a planet came to be in the last degree of the sign, then its strength has already gone
> away from that sign, and its strength is in the next sign. **32** And it is in the position of a
> man putting his foot on the threshold of [his] door, and on the verge of departing: so if the house
> falls, it will not harm him. **33** And if a planet was in the twenty-ninth degree, then indeed the
> strength of the planet is in that sign. **34** For every planet has three degrees in which its
> strength is diffused: in the degree it is in, and the degree in front of it, and the degree behind
> it." — Aph. #15, 31–34 (`:77`)

> "**39** And if connected with another [by aspect], it will not harm it, [like] when I described to
> you that a connection does not nullify a uniting, while a uniting does nullify a connection, and
> an aspect does not cut off an aspect: understand." — Aph. #17, 39 (`:97`)

> "**74** If planets were under the rays they would be weak in the whole of affairs: and it is like
> that if there were less than 12° between them and the Sun – unless a planet was in the degree of
> the Sun, for then it would be strong." — Aph. #39, 74 (`:209`)

> "**75** If a planet was at a distance from the Sun by 12° in its rising from the east in the early
> mornings, then indeed it is strong in every inception and work. **76** And if it was at a distance
> of 15°, then at that time the planet would be the strongest it [could] be. **77** And if the planet
> was in front of the Sun in the direction of the west (that is, if it is arising in the evenings in
> the west), and there were from 7° to 15° between it and the Sun, then indeed it commences with
> weakness. **78** And from 7° until it is in the heart of the Sun, the planet will be the weakest it
> [could] be. **79** And if it was in the heart, it is strong (by 'the heart' I mean that it is with
> the Sun in one degree)." — Aph. #40, 75–79 (`:211`)

> "**87** Every planet which is at the beginning of a sign, is weak until it is firmly established in
> it and comes to be 5° within it. **88** And the planet will not be falling from the stake unless it
> was 5° distant from its rear: I mean, if the stake was 10° of Aries, then indeed every planet which
> has less than 5° between it and the stake, is truly counted as being in the stake. **89** And every
> planet which was in more than 5° [from it] is not counted as being in the stake." — Aph. #44,
> 87–89 (`:230–252`)

fn. 56: *"This is the famous 5° rule of Ptolemy, where the power of the stake or angle extends by 5°
beyond the cusp—as measured in diurnal motion, hence Sahl's reference to the 'rear' of the stake."*

> "**90** And every planet which is [distant] from the stake in what follows it, by 15°, is in the
> situation of one who is in the stake; and if it increases [beyond that], then it does not have
> strength. **91** An example of that is if the stake was 10° of Aries, then up to 25° of it, it is
> indeed in that stake. **92** And if it exceeded 15°, not." — Aph. #45, 90–92 (`:254`)

fn. 57: *"This statement is based on Carmen 1.28, 1-7 (and is repeated correctly in Sahl's Nativities
Ch. 2.13, 48-51), but is misstated here. The range of 15° is measured in ascensions, not in
zodiacal longitude."* With the project note appended there.

> "**99** If a planet was stationing towards retrogradation, it indicates collapse in the matter,
> and disobedience. **100** And if it was stationing towards direct motion, it indicates forward
> movement in that matter, with no difficulty. **101** And every planet which was an indicator and
> wanted to go direct, indicates the suitability of the affair, and its strength, and its forward
> movement." — Aph. #48, 99–101 (`:260`)

## 3. Internal disagreements and cross-work tensions, collected

| # | Item | Statements |
|---|---|---|
| 1 | #25 received infortunes | ¶50 "stronger for its harm" vs #2 ¶9 and #20 ¶43 (restrained); fn. 30: error, Latin has *less*; *Nativities* 1.23, 37 and 5.1, 64 agree with "less" |
| 2 | #45 fifteen degrees | zodiacal as printed vs ascensional (fn. 57); *Nativities* 2.13, 48–51 correct; **policy: ascensional, abstain** |
| 3 | #44 five degrees | zodiacal in the example vs "diurnal motion" (fn. 56); *Nativities* 1.22, 9 (stakes) and 1.18, 19 (all houses) |
| 4 | #40 eastern strength | strong at 12°, strongest at 15° vs *Nativities* 1.22, 1 (♄♃ "considered eastern" at 6°, easternize at 15°; ♂ 18°) and Abū Ma'shar VII.2, 12–14 |
| 5 | #39 twelve degrees under the rays | vs Ch. 3, 93 (no figure) and Abū Ma'shar's 15/18/12–15 bands |
| 6 | The heart | #40 ¶79 and Ch. 3, 87 "one degree" vs VII.2, 7 sixteen minutes; fn. 46: Rhetorius allows either adjacent degree |
| 7 | #4 "falling" | ¶16 "falling" vs "falling away from the Ascendant" (fn. 5) |
| 8 | #36 square vs trine | ¶69–70 the square dissolves, the trine only relocates the hardship (fn. 42) |
| 9 | #32–33 glow | sect here; Ch. 3, 85 gender (fn. 97) |
| 10 | #2 | "in the house of an infortune … it would receive it" vs Sahl's own rule that occupancy is not reception (fn. 2) |
| 11 | #17 vs #16 | body-escape "accomplished unless it unites with another prior"; aspect-escape "not accomplished if it connects with a different one" — asymmetric by design (fn. 19–20) |
| 12 | #19 fn. 24 | the "infortune handing over" case is only possible for Saturn when retrograde, "and one would have to overlook the rules for 'returning light'" |
| 13 | #21 | "suitable for it" — for whom? (fn. 29) |

## 4. What the engine takes from here, and what it leaves

Taken: #4 (light boundary), #15 (29th degree), #17/#19 (precedence, direction of handing over),
#39–40 (12°/15°/7°, one-degree heart, as Sahl's own values beside Abū Ma'shar's), #44 (five
degrees, both halves), #48 (stations). Left, by policy or by nature: #45 (ascensional; abstained),
#13 (timing keys — recorded in `04_timing_open_questions.md`), and the delineative aphorisms.
