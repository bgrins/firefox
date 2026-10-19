# Independent URL native-state v2 review

## Verdict

**ACCEPT the bounded component and its corrected finite native correspondence evidence.** No substantive blocker remains in the reviewed scope. Root owns final acceptance. This is not acceptance of whole-tokenizer, public parser-history, compiler, heap or unrestricted machine correctness.

V1's negative verdict remains valid and immutable. V2 fixes its trace validator, without changing native behavior or any Lean model. The prior review and precise mutation causes are retained in `evidence/prior-review/`.

## Authentication and transfer

Authenticated externally supplied producer pins before execution/import:

- FREEZE `133a15bc867d76b46af31f55e3f9126c7d699b834278d82c95e6ae225a884549`
- MANIFEST `9776f7c0c24b18d7cae27b25fc8a1673472a57382516d1198ae32c25a3e64847`
- checker `f5256d82e1f034ce5339ecbb9b5210c4a7ac1cfb6b5fa529b50636f2ae5321b7`

All 442 inputs match a closed file/directory roster, with duplicate-key and symlink/path checks. `package/` is an exact relocated source copy. Independently compared against the authenticated v1 retained in the negative review: 421 old inputs unchanged, exactly seven changed, 14 added. All Lean modules, source bindings, Rust sources, wrappers, instrumentation and cases are unchanged; the changed files are four documents, top checker, native orchestrator and native state comparator. This supports transfer of the prior substantive model/source review, not transfer of the failed v1 trace-validation claim.

Also authenticated the separately sealed producer receipts (166 inputs), including the externally supplied FREEZE and MANIFEST. Acceptance here uses an additional fresh independent replay, not those receipts alone.

## Review of the correction

`reference_trace` receives only an original source string. It has no actual event/state argument and reads no expected trace file. It derives the identifier-like entry and URL-call eligibility; preserves quote rollback before bulk assignment; distinguishes empty URL, borrowed and owned execution; follows escape, trailing whitespace and bad-remnant branches; and publishes the helper seam separately from the final Function caller block bit. Local `position` is advanced by the reference control schedule. Metadata comes from the independent original-source scalar-prefix fold. Raw captures use original body start and current original-source position, never the decoded owned buffer.

I compared these branches directly with the complete retained `consume_unquoted_url`, its three nested loops, wrapper and source instrumentation. Borrowed allocation captures exactly before slash/NUL; owned completion omits that borrowed slice; invalid controls advance before bad recovery; bad recovery captures before close; paired slash-close/slash-slash skips both bytes; CRLF is consumed atomically. Leading bulk observations retain the moved cursor with preassignment line fields. The next helper's expected fields reflect the completed bulk update. This handles the real assignment boundary without inventing an extra recorded helper.

The final comparison is exact ordered list equality across all cases. It enforces source-derived presence, multiplicity, relative order, arguments, payloads and fields. Adjacent expected states follow the reference's own cursor; continuity is therefore not merely checked against individually plausible prefix fields. Separate schema checks reject unknown tags, noncanonical row encodings and wrong arities. Exact equality rejects unexpected numeric/payload spellings or values without relying on permissive integer parsing. Fixed aggregate totals are additional drift checks, not the oracle.

The Python name entry deliberately covers the fixed identifier-like first-token corpus. It is not a complete replacement for native next-token dispatch, arbitrary parser entry states or the independent Lean caller component. Likewise, this manually source-corresponding control interpreter is not universally verified by Lean. These limits are now explicit in `SOURCE-ADMISSION.md` and are acceptable for finite native admission.

## Fresh evidence

Fresh relocated isolated replay completed exit 0 at `/private/tmp/url-state-independent-replay-v2`. Retained evidence includes command receipts, proof logs, raw traces, semantic witnesses and mutation failures; generated binaries and olean files are excluded.

| Gate | Result |
| --- | --- |
| Kernel replay / exact axiom roster | 51 modules, 388 reports; 17 new modules and 107 new reports over the accepted predecessor |
| Source extraction | 44 complete function bindings and five field/constant bindings regenerated exactly |
| Native modes | Debug, release and actual fast_match_byte release traces agree |
| Complete ordered trace | 59 cases, 503 events: 56 entries, 56 exits, 230 helpers, 56 slices, 46 bulk observations, 59 tokens |
| Uninstrumented control | First tokens and final fields equal filtered instrumented output |
| Separate Lean driver | 112 native entry/exit observations agree |
| Semantic mutations | Four native mutants compile and reject; four Lean definitions/witnesses compile and unchanged theorems reject |
| Trace challenges | 3,043 genuine corruption checks reject; nine historical v1 acceptances freshly reproduced |
| Five independent v1 counterexamples | Exact retained hashes independently rerun, all reject for intended reasons |
| Independent integrity challenges | Eight reject before output creation/compiler invocation |

The 3,043 count is operational rather than a theorem count: five modifications at each of 503 events (deletion, duplication, retag, extra field, missing field), 502 adjacent swaps, six whole-class deletions, three late moves, one entire seam deletion, two annotation Option changes, nine historical variants and five exact reviewer traces. I inspected those mutation operations. Assertions distinguish unexpected acceptance from rejection; syntax/infrastructure errors are not substituted for these trace comparisons.

The five independent old counterexamples fail at unknown-tag, arity, or ordered input-derived trace equality as appropriate. `evidence/old-five/` retains commands, exact bytes/hashes and actual rejection logs. These are executed separately from the producer's corruption loop.

## Semantic mutation causes

Fresh v2 rejection occurs earlier and more precisely than v1:

| Native mutant | First discrepant ordered event |
| --- | --- |
| Astral sign | Event 130, case 15: intro line start becomes 2 rather than 0 |
| Continuation sign | Event 129, case 15: continuation line start becomes 4294967295 rather than 1 |
| Bulk last newline | Event 493, case 58: next helper starts at line start 7 rather than 8 |
| Capture after close | Event 194, case 22: advance appears where preclose slice at offset 7 is required |

All are intended state or ordering failures, not missing rows or incidental exceptions. The old 58-case bulk-mutant survival remains reproduced; the retained 59th case discriminates it. Lean mutation definitions/witnesses are unchanged and compile freshly; failures remain the intro field relation/concrete false propositions, capture invariant, bulk metadata relation and quote rollback equality. Full fresh logs are retained.

## Mathematical scope and remaining admissions

The unchanged universal component derives stored-field relations through actual-shaped helper and loop transitions. It handles modulo-2^32 line start, including reachable astral underflow, while separately requiring packed-count/addition headroom and bounded exact source columns. Raw capture derives original full-source slicing from start assignment, loop endpoints and a genuine close/EOF marker. Whole-input structural UTF8 validity derives aligned body entry; internal TailValid does not silently replace public entry validity. CRLF escape-cut composition is proved.

The Function result is the URL helper delegation seam, not the completed spec string-token cursor or final caller state. V2's native oracle checks the later caller block-bit effect separately. Previously accepted value/name/escape/string helpers retain their versions and premises.

Still external: canonical Rust codec/str boundary behavior, usize and allocation bounds, unsafe slicing safety, normal return and allocation, standard library, compiler and machine implementation, and general initial annotation preservation. The finite corpus observes absent sourceURL/sourceMappingURL Options; it does not prove arbitrary annotation state histories. Public cache/reset history equivalence remains separate. No current-browser or live native modification was made or inferred by this review.

## Integrity and replay

Run `python3 -I -S -B check.py` for the closed independent evidence checker. To repeat full source-only replay, authenticate the externally pinned copied capsule and run `python3 -I -S -B package/check.py --run --output NEW_EXTERNAL_DIRECTORY`. The pinned Lean/Rust toolchains remain required. `integrity_challenges.py` reproduces eight rejection checks against a caller-selected disposable output directory. No live repository source or previous binary is required.
