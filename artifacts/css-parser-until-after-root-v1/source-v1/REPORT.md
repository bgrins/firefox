# Delimiter continuation: conditional model and native calibration

Status: source capsule prepared for independent review. No root or independent acceptance is claimed.

## What is established

`UntilAfter.lean` contains **22 general theorems**. Its `after_refines` joins the accepted until-before refinement with an independently expressed source-only continuation: an enclosing-owned delimiter stays unread; a requested-only delimiter is read as one source token; a curly opener delegates to the source-only block relation. The native-shaped branch instead uses direct byte advance plus raw block cleanup. Agreement requires explicit progress, delimiter-provider law, admitted requested masks and aligned incoming cache/history. The theorem does not assume its final output is correct.

The remaining theorems establish single-byte bounds/ASCII, coherent retained cache, pending cleanup on completed branches, Stop/error preservation, returned success preservation, control-field preservation, and continuation annotation/observation equations. `after_refines` uses the inherited `Aligned` projection; URL annotations are handled by separate write laws, not silently included in that relation. The accepted before-phase write relation and new continuation laws remain separate compositional facts.

**11 root-authored kernel challenges** comprise four counterexamples showing the need for provider/ownership/pending/mask premises and seven concrete successful paths. These are not 11 additional general refinement theorems. `AllAudit.lean` and `ALL-AUDIT-NAMES.json` enumerate exactly 33 checked declarations. The unchanged root files are pinned by `ROOT-OWNED-PINS.json`; 59 inherited Lean modules and 134 source/vendor files transfer byte-identically from the authenticated predecessor.

## Native evidence

`native/check.py` compiles the complete retained cssparser source and dependencies, not a translated tokenizer or until-after facade. Only the callback adapter and private-state observation are added. Its 27 histories produce **138 equal snapshots in debug and release**. The projection covers byte position, pending opener, cache key/token/end state, tracking mode, source/source-map URLs, delimiter mask, depth and limit, plus Boolean callback result/projected returned token.

All six native mutants compile and run successfully with the same row identity/arity roster. They differ in 25/41/22/7/11/5 rows respectively: outer ownership ignored, missing advance, missing curly cleanup, ignored Stop guard, cache overwrite, erased curly writes. They run in release so an intentionally violated debug assertion is not mistaken for semantic discrimination. No new Lean proof mutant is claimed; root kernel counterexamples and compiled native mutants serve distinct purposes.

The predecessor's snapshot renderer swapped the parenthesis/curly closing bits and omitted the opening-curly bit. Both authenticated old 91-row debug/release traces expose only zero stop masks. `native/RENDERER-CORRECTION.json` preserves that limitation and exact prior evidence. New nonzero-mask cases use the actual constants and distinguish enclosing ownership. Mathematical byte-list semantics and frozen predecessor files are unchanged.

## Admissions and limits

- **Tokens and source:** immutable UTF-8 source, valid native cursor/token boundary and source bounds; codec and all token-family implementation correctness are not proved here. The mathematical theorem admits byte lists, not a proof that every such list is a Rust string. Numeric/string/hash/at-keyword native/model providers remain unsupported by the fixture driver and fail closed with diagnostics. Whitespace and width-one punctuation are explicit restricted providers.
- **Progress and machine bounds:** `PublicCleanup.Progress` and `DelimiterLaw` are quantified premises. Finite replay does not discharge them universally. Remaining-byte fuel, natural-number positions and u8 controls require the named native source/machine correspondence; usize overflow, allocation failure, stack/memory safety and native compiler correctness remain external.
- **Callbacks and caller histories:** represented `WrapperControl.Program`, normal return, same-parser saved state, valid masks, coherent cache and enabled-name history admission. The native adapter makes zero or one next call then succeeds/fails; it is not a compiled Firefox caller. Arbitrary callbacks, reentrancy, panic/unwind, forged/cross-parser reset and host state mutation are excluded, not proved impossible.
- **Observation:** exact error kinds/payloads, token payloads collapsed by the projection, source line/column/packed metadata, borrowed lifetimes, allocations and browser scheduling are not covered. URL continuation writes and function tracking are checked explicitly within the projection. No whole tokenizer or parser API claim follows.
- **Toolchain:** Lean/rustc executable identities are pinned; installed Lean standard-library/runtime and Rust sysroot/runtime/linker remain trusted environment dependencies. Kernel checking verifies the Lean propositions; it does not establish spec fidelity or automatic Rust-to-Lean translation. The ten exact body bindings establish source identity only.

The historical custom-properties and LinkParameters sources are retained because they belong to the predecessor closure; this new component makes no LinkParameters or VariableValue correctness claim.

## Replay and integrity

Authenticate `FILES.json`, `FREEZE.json` and checker against externally supplied hashes, then run:

```
python3 -I -S check.py --output /absolute/new/external/output
```

The controller rejects unsafe Python modes before nonbuiltin imports, checks exact regular-file and inferred-directory rosters without following symlinks, rejects duplicate/path-escaping manifest entries, validates sizes/hashes/root seals, verifies protected root inputs and inherited source mappings, checks exact audit names/allowed axioms and proof diagnostics, and runs the finite native calibration. It reauthenticates the capsule afterward. Source-only relocation copies exactly manifest entries and the two root seals; no prior generated olean or native library is an input. The executable paths in TOOLCHAIN are explicit external dependencies.

`guard_capsule.py` runs targeted pre-output rejections using disposable copies. Reports/receipts from replay are kept outside this source capsule. Native debug/release and raw mutant outputs remain evidence; they are not a formal proof of the installed browser. Completed owned generated outputs are removed only after commands/raw results are retained.
