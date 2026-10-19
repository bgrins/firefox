# Measurement coordinate repair review

Status: browser-reproduced by root; complete extracted native repair replay passes. This is separate from the accepted ownership candidate4. No production edits or browser execution were performed by this producer.

## Independent expected behavior

CSS Text 3 `hyphens: auto` gives conditional hyphens precedence over automatic opportunities in the same word. The exception permits additional automatic opportunities when a portion remains too long for a line. The exact authored fixture has 176 letters in `counterrevolutionaries` repeated eight times (22 letters each), and 180 in `characteristically` repeated ten times. SHY is after 110 letters. The portions are 110/66 and 110/70; even allowing a one-em hyphen, each fits the 120-em line. Earlier 168/58 arithmetic in messages was incorrect; fixture bytes did not change.

The twenty-letter preceding token and space leave only 99 em. The 110-letter first portion therefore moves to the next line at the existing natural break. Repeating `x ` 120 times before the same body fills two lines. Both suffixes begin at x=0; their line-relative glyph positions must agree. The probe calibrates those origins and the exact two-line displacement before comparing non-space/non-SHY glyph rectangles. Parent reports two failures, precisely auto+SHY, with six controls passing. Automatic-word eligibility has UA latitude; the actual pinned dictionary/provider admits opportunities for these exact words, and the same word/style/font is used on both sides. No cross-UA dictionary positions are asserted.

Normative evidence is retained in COORDINATE-SPEC.json and COORDINATE-SPEC-WEB.json. The retrieved section is https://drafts.csswg.org/css-text-3/#valdef-hyphens-auto. These initial records predate browser execution and preserve that chronology.

## Exact causal path and repair

`gfxTextRun::BreakAndMeasureText` sets `wordState.mostRecentBoundary = aStart`. `ClassifyAutoHyphenations` stores glyph indices `i` in this field, uses `i - aStart` only for buffer accesses, and asserts its boundary is at least aStart. The measurement refill sets `bufferRange.start = i`; `oldHyphenBufferLength` is a count relative to aStart. Comparing the absolute previous word boundary to that count suppresses a required rescan for nonzero aStart. A newly seen manual hyphen then changes earlier auto entries, but cached candidate-break state retains the earlier automatic opportunity.

Replace only `prevMostRecentWordBoundary < oldHyphenBufferLength` with `prevMostRecentWordBoundary < bufferRange.start`. Both operands are absolute glyph offsets. With the buffer-cover invariant, this is equivalent to comparing `prevMostRecentWordBoundary - aStart` with the old length. It avoids a new addition and preserves aStart=0 behavior. Keep oldHyphenBufferLength for the append destination. The rescan, range fetch, width accounting, classification, glyph and sink operations are otherwise unchanged.

The complete classifier and measurement bodies are retained and executed, including the existing rescanLimit handling. For an admitted refill, the previous boundary is inside the already fetched interval, and the repaired guard selects precisely a boundary earlier than the new chunk. It does not ask the provider for a different chunk on rescan. Existing unsigned predecessor/increment behavior and C++ allocation failure are not independently proved by a Nat arithmetic lemma.

## Replay

Command: `python3 artifacts/css-hyphenation-ownership-proof-v1/native/check-coordinate-repair.py`.

The script derives a full source candidate from the frozen complete gfxTextRun.cpp by a strict single replacement, checks exact function-body extraction, compiles the complete TransformText/skip/property-hyphenation/classifier/measurement bridge under UBSan, and replays both variants. Result and source hashes: development-build/full/coordinate-repair/RESULT.json. Minimal patch: development-build/full/coordinate-repair/repair.patch.

Sixteen dictionary-admitted fixture calls: only shifted auto+SHY calls change, from 98/99 to 21 consumed units. All eight origin/offset pairs now agree on measurement outputs. The 40,608 prior provider classification/measurement cases have no output differences. Actual dictionary outputs are retained inputs from the full range/provider/sink bridge; the native consumer still uses explicit unit-advance and spacing/font storage adapters. Root browser reproduction provides the concrete DOM/font/reflow witness; neither it nor this matrix proves universal shaping refinement or C++ memory safety.

## External browser receipt

`artifacts/css-hyphenation-measurement-offset-probe-v1/wpt-baseline-v1-receipt.json`, SHA256 `4ee6c581de161913aa20d5e20f78036fa3217f10b0b2379767caf1409be20b49`. Baseline reports 2 FAIL / 6 PASS / 1 OK with stable source/font/dictionary pins. This is root-owned evidence and is not silently substituted for frozen ownership candidate4. Root owns the production repair and candidate browser gate.
