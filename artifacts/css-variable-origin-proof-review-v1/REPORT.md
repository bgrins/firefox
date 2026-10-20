# Independent origin proof review — v1

**Verdict: BLOCKED for fail-closed capsule acceptance; no mathematical defect found in the reviewed scoped proofs.** The frozen v1 checker lacks an explicit interpreter-mode guard and relies on assertions. The producer is preparing a separate v2; v1 source remains unchanged.

## Authentication and actual work

Externally authenticated FREEZE696a3692fd3fa7b8e13494b3ba08c88312b87580d51513a210eafbb413290881 and MANIFEST7c14f055f5310ae689fad40e1742a2c0517d1f1c8e74283a3fa11011fb29f5ba, all178 inputs and closed roster/no symlinks. Copied exactly that manifest plus seals into relocated-source, read all13 Lean modules (1233 lines), source/admission contracts, complete native harness/extractor/oracle and inspected native consumer bodies against retained source. Fresh intended-mode `python3 -I -S` replay passed88 exact axiom reports (propext, Quot.sound, Classical.choice only),22 complete extractions per variant plus explicitly partial provider/fallback function, and49 candidate native observations.

## Concrete blocker

`guard_challenge.py` intercepts subprocess dispatch before any tool runs and supplies existing `/usr/bin/true` as a deliberately wrong Lean executable. Normal isolated/no-site invocation rejects its hash and creates no output. Both -O and -OO suppress authentication assertions, create the output directory and attempt to dispatch that wrong executable. Raw results are guard-existing-tool-{normal,optimized,double-optimized}.json. This demonstrates reachable unchecked execution, not just a lexical concern. Earlier /bin/true attempt used an absent path; retained separately and not used as the hash-rejection evidence. The sentinel prevents actual Lean/Rust execution. Source v1's intended-mode proof replay remains useful historical evidence, but does not remedy this fail-open path.

## Substantive theorem assessment

`collect` performs cursor-origin arithmetic through a recursive component tree; `layout` independently constructs local endpoints. collector_layout handles arbitrary absolute origins with derived cursor order. Boundary proofs derive UTF-8 character boundaries and bounds from rendered character lists. ValidHeaders requires positive reference/header lengths and an actual single ASCII closing parenthesis for fallback-bearing references; it does not assume desired offset bounds. outerSpans excludes nested fallback references at the parent's traversal while retaining references inside ordinary blocks. Its ordering/separation and complete clean/reference/suffix scan safety are derived.

FallbackAt plus constructed_fallback_occurrence identifies an actual recursive body for each fallback; slice and embedding theorems connect local traversal to original-source offsets and `end-1`. ByteSlice is a total mathematical operation; its equality to a real substring is proved only under constructed boundaries. These are substantive joins, not merely assertions that supplied offsets are valid.

ReplacementReading is independently expressed through source decompositions. scanPieces uses byte offsets; successful correspondence joins it to output concatenation/range accumulation. Arbitrary replacement text and provenance bits remain external provider values. Nonempty tainted outputs are covered after separators and subsequent appends; empty tainted output retains aggregate provenance. Direct empty intervals are not claimed to overlap URLs. OutputSafe derives output-range safety; it is not a URL policy or confidentiality theorem. checkedAppend proves safety on success, not an overall size limit including separators or native failure/effect equivalence.

Important caller qualification: model directOutput starts at zero even in the generic nativeDispatch definition; actual native direct-return code pushes `(start, replacement.len())`. Native correspondence therefore requires the separately stated outer collector start0 and nested fallback collectorNone protocol. native_dispatch_safe alone does not establish arbitrary native nonzero-start range safety. The report/admissions already preserve this restriction. Similarly, EOF Repair proves algebra for an admitted append/delete operation, not parser selection of that operation. The initial maximal whitespace/provider parse, no pending block, fixed observer epoch and trailing-boundary compatibility remain admissions. The cache lemma is Boolean idempotence, not a general cache/history proof.

## Native agreement and challenge results

The full retained cssparser dependency closure is compiled, with exact constructor/scanner/chunk/push/taint bodies and declared facades. The lookup function is intentionally partial: two named synthetic providers plus exact missing-provider fallback tail. The restricted Python oracle derives expected text/offsets/output/ranges from fixed inputs rather than native output. It is not a general CSS parser; its limited name/quote/function grammar is admitted by the49-case roster.

Fresh candidate has49 exact matches. Original and late-origin mutant each have28 PANIC rows with out-of-range endpoints, including the required witness. Other compiled mutants expose exact lost var opener, dropped retained comment, and character7-versus-byte13 offset. These are genuine semantic discrepancies after successful compilation; no Lean mutation runs are claimed. Five independent oracle corruptions (missing/reordered rows, wrong fallback offset, wrong taint range, wrong aggregate bit) reject. Eight supplied integrity negatives also reject in normal mode, separately from the optimizer defect.

## Residual scope and version

This binds original18b611… and candidatee3c5f24… only. Later leading/trailing-related live changes cannot silently replace them. No universal parser-to-component-tree translation, provider/registry/namespace/attribute lookup, codec/compiler/heap/machine-overflow, token-class separator adequacy, arbitrary allocation/failure side effects, URL semantics, or dynamic browser publication closure is established. Lean executable identity is pinned; imported standard/runtime libraries are trusted rather than independently inventoried by this capsule. Browser evidence is separate and was not rerun.

Generated binaries/rlibs/oleans from this completed owned replay were removed after all logs/raw/generated source were retained; exact hashes/sizes in CLEANUP.json. No native/WPT/Git/Firefox-build/browser actions by this reviewer. Root should review a corrected immutable v2 before accepting the companion; mathematical scope need not change for the guard correction.
