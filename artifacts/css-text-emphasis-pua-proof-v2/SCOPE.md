# Private-use text emphasis: proposed formal/native scope

Status: proposed for root approval before implementation. The completed animation artifact remains immutable and independent review may request a separate correction artifact.

## Objective

Prove the narrow detailed-Co repair through classification, code-unit flags and ordinary cluster/run draw-call eligibility. Do not infer painting correctness from a classifier lemma. Retain the full native functions required below; if a dependency prevents this closure, report the concrete issue and seek a scope revision before replacing it with a smaller claim.

The authoritative production candidate is the detailed-category guard under coarse `kOther`, with supplied `nsTextFrame.cpp` SHA-256 `3523242b65fc550fc741235cd37f467fcbe245f1679caa8df5b48caf23a10c2d`. Bind root's final original/candidate snapshots and the independently reviewed standalone WPT receipts before freeze. This worker owns only this artifact; root owns live source/WPT/build/browser/Git.

## Independent semantic model

1. Define Unicode scalar values, UTF-16 code units, detailed general categories and the CSS emphasis eligibility rule independently of Gecko's coarse switch. Read the current primary CSS Text Decoration specification and CSSWG punctuation resolution. Use the official Unicode version matching the actual generated ICU data, including complete category ranges and recursive NFKD decomposition data. Do not use the host Unicode library as an oracle or copy the native punctuation answer table as expected results.
2. Prove the candidate admits every Co scalar and preserves every other scalar classification result. Preserve Cc/Cf/Cn/separator exclusions and the independently derived punctuation/NFKD exceptions. Lone surrogate code units retain a separate legacy implementation contract; no CSS normative lone-surrogate rendering claim or widening to Cs.
3. Define Latin-1 and UTF-16 decoding/iteration over arbitrary finite buffers, typed valid lengths and indices. Well-formed pairs consume two units and rejection suppresses both units. Unpaired surrogate units have explicit single-unit behavior. Prove bounds, progress, no skipped or duplicated input, precise suppression fields and preservation of unrelated glyph/advance fields through simple-to-complex conversion.
4. Define a valid finite cluster partition and glyph-run partition as supplied shaping inputs. They must cover the admitted interval, remain ordered/disjoint, respect required surrogate/ligature relations and have explicit nonvacuous examples. A scalar is not assumed to equal a shaped cluster. Model ordinary complete-cluster eligibility as the fold over actual per-unit flags, and model exact ordered draw emissions at cluster boundaries. Prove one draw event per complete eligible cluster under the stated range/partition/spacing premises.
5. Extend this to the actual ordinary run dispatch, nonzero offsets, font-run subdivision, ligature-boundary shrinking, spacing and advance accumulation. Keep eligibility, draw-event identity/order, numeric geometry and rasterization distinct. The universal sequence/partition contract must not accept an expected draw-eligibility result as an input provider.

## Mandatory native extraction

Extract and compile complete definitions, with exact whole-body identities:

- `MayCharacterHaveEmphasisMark` and both Latin-1/UTF-16 `SetupTextEmphasisForTextRun` loops, including pair detection and all index increments.
- `GetGeneralCategory`, `GetGenCategory`, detailed/coarse category tables, `UnicodeProperties::CharType`, the actual ICU `u_charType`/lookup macros and generated trie data. Do not substitute the earlier Python trie interpretation for native execution.
- `gfxTextRun::SetNoEmphasisMark`, `EnsureComplexGlyph`, participating compressed-glyph setters/accessors, simple/complex record and detail allocation/update boundaries. Observe all unaffected flags, glyph IDs and advances through conversion.
- Complete `gfxFont::DrawEmphasisMarks` and complete `gfxTextRun::DrawEmphasisMarks`, including actual font-run iteration, range/spacing/ligature-boundary providers and the necessary participating helpers. Retain complete cluster accumulation and draw dispatch; downstream draw calls become an observer of actual emissions, never a supplied expected eligibility answer.
- Preserve source-only closure for effective-emphasis style gates, transformed text/run creation, update/draw entry points and the combined-upright alternative. The universal ordinary path excludes combined-upright drawing and transformed-text/shaping correctness unless separately closed.

Boundary adapters may supply typed immutable Unicode data, valid text/glyph buffers, valid shaping partitions, font metrics/advances/spacing, draw targets and paint resources. A boundary must be named, its input domain recorded and its outputs traced. Actual category answers, suppression flags, segment/run eligibility and final draw-event lists cannot be oracle inputs.

## Required native observations and domains

Compare independent raw-input expectations with original/candidate executions for full Unicode scalar classification and actual ICU category data, every 16-bit unit, Latin-1 values, well-formed surrogate pairs, malformed pairs, empty/singleton/mixed sequences, all Co boundaries, Cc/Cf/Cn/Cs and separator controls, every punctuation/NFKD exception and nearby nonexceptions.

Exercise simple and complex glyph records; preserve glyph IDs, advances and unrelated flags; observe both surrogate suppression bits and complete provider traces. Include multiple units per cluster, mixed eligible/ineligible units, all-ineligible clusters, multiple font runs, nonzero run intervals, spacing variations, ligature boundaries and explicitly invalid provider layouts. Invalid lengths/indices/ownership/partitions must be rejected diagnostically and must not be counted as semantic mutation kills.

The Unicode domain is finite and exhaustively checkable. Arbitrary buffer/partition lengths are the universal Lean claim under the explicit bridge premises; finite native rows are a separate result.

## Mutation, provenance and acceptance

Genuine semantic native mutants must compile and run successfully and exhibit concrete disagreements: original broad `kOther` rejection; acceptance of all `kOther`; a missing punctuation exception or added excluded character; wrong pair decoding; suppression of only one surrogate unit; skipped/doubled code-unit advancement; lost unrelated glyph fields during conversion; wrong cluster fold/eligibility; suppressed or duplicate draw emission; and incorrect run/ligature boundary handling where the complete extraction supports the claimed boundary. Match these with successful kernel-checked Lean counterexample witnesses. A crash, compile error or failed proof is not a semantic witness.

Deliver independently defined oracle, complete source/provider inventories, actual toolchain and Unicode/spec identities, pre-import-authenticated source-only replay, Lean axiom audit, genuine mutation receipts, honest operation counts and controlled costs. Preserve original/candidate separation and independent review. Root WPT supplies ordinary rendered and dynamic evidence; shaping, font loading, metric correctness, transforms, restyle/cache invalidation, compositor scheduling and glyph rasterization remain explicit external obligations.

No implementation begins until root approves this scope or an explicit revision.
