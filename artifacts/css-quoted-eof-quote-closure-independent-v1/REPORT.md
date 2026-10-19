# Independent terminal-quote closure review

**Recommendation: source/proof proposal approved for root integration and browser validation. Native acceptance remains open.** This patch distinguishes an escaped terminal quote from a real closing quote; parity and endpoint repair acceptance remain separate.

All 180 producer inputs were authenticated against the supplied freeze/manifest/checker pins before execution. I read both complete Lean modules, source deltas, parser/tokenizer methods, extracted native harness and declared facades, retained browser oracle and checker. Fresh relocated replay passed 19 exact theorem audits and every standalone, endpoint and combined source configuration. The independent checker derives its theorem-name inventory directly from declarations and checks all native result families.

## Source and semantics

An odd maximal backslash run before the final matching quote escapes that quote; it belongs to the string's contents. EOF then leaves the token unclosed. An even run leaves a genuine terminator. Appending a recovery quote only for the former preserves the decoded string and prevents a later property suffix from being swallowed. This follows the string algorithm's escape handling, not a raw CSSOM spelling preference. [CSS Syntax string consumption](https://drafts.csswg.org/css-syntax-3/#consume-string-token).

The source still tests the exact matching quote and `len() > 1` before evaluating the new slice. Short-circuiting ensures the removed final byte is an ASCII quote and the slice ends at a UTF-8 boundary. An opening quote alone never reaches that slice and remains an unclosed empty string. The reverse iterator counts only ASCII backslashes; the original opening quote stops an all-slash body. No allocation is introduced. Each quoted token gains constant work or a scan of its final slash run, bounded by the already-tokenized length. No performance measurement is claimed.

The patch changes only closure recognition. On the endpoint-based source, a newly recognized missing closer still has a quote as its final source byte, so `removed_backslash` remains false. Its synthesized quote contributes to the existing missing-closing suffix used for subsequent reference endpoints. The parity predicate and final pop are unchanged. This reviews the new change's interface with H1, not my own H1 implementation's independent correctness; H1 has its own reviewer.

The standalone proposal leaves the other two defects intact. The supplied adaptation on the formatted endpoint source changes the same predicate, and the parity/closure adaptations commute exactly. Both capsules retain identical combined source. Root must use the appropriate current-base adaptation rather than replacing unrelated branch content with a complete standalone snapshot.

## Proof and observations

`TerminalString.consume` parses from the front with explicit pairwise escapes. `ClosureRepair.genuine` classifies parity; the proofs derive closing classification, decoded raw content, recovered content preservation, closure before arbitrary following units and ordinary-prefix framing. The opening-only and original/overcorrection cases are distinguished. All 19 declared theorem names match the axiom audit, with only standard axioms.

This proof starts inside one valid quoted token before its maximal terminal run. It does not prove a complete tokenizer, arbitrary escaped prefix processing, hex escapes, Unicode conversion or preprocessing. The simplified `other` units denote restricted ordinary input. Source-to-byte/run correspondence, native metadata normal completion, usize/UTF-8/library/compiler/heap behavior remain explicit. The unrestricted suffix theorem is sound because the parser stops before that suffix; it does not claim to decode arbitrary CSS suffixes with this small grammar.

The independent reviewer front decoder agrees with all 22 native fixture expectations. The native driver then executes the actual full declaration parser and actual tokenizer, compares decoded values, and checks that appended `, serif` remains outside the recovered string. The broader copied substitution/provider facade is not exercised by these single-string fixtures and is not provider correctness evidence. Root's browser baseline uses 20 terminal-run cases plus two fallback controls; this native matrix instead uses two opening-only controls. No counts are conflated.

Original source has eight failures. Closure alone removes its four odd-run terminal-quote failures and retains all four even-run EOF failures, for standalone and endpoint configurations. Combined source passes all 22 rows. Native restored-original and always-append mutants compile and discriminate; the latter breaks the two genuinely closed zero-slash controls. The combined restored-original configuration removes both semantic repairs, so isolated attribution comes from standalone/endpoint runs. The Lean negative files reject false concrete assertions with `decide`, rather than mutating an entire definition and rerunning unchanged universal statements; no stronger mutation claim is made.

## Remaining gates

Root owns final formatting/source binding, Gecko compilation, exact paired WPT/browser validation and native+WPT packaging. A separately landable test should include this repair's four failures and shared controls, retaining the parity failures separately until parity lands. Full tokenizer/provider/cascade/recursive-offset/native-memory work remains open. This review neither claims browser candidate success nor closes those broader goals.
