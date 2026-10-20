# Independent nested-control v1 review

**Verdict: tooling acceptance blocked; no mathematical contradiction found in the scoped model.** The producer is preserving v1 and correcting runners/roster in a later immutable version. This review did not perform an expensive fresh proof/native replay after discovering the guard blocker; producer preflight receipts are inspected historical evidence, not independent execution.

## Authenticated inputs and concrete failures

All 264 manifest inputs, exact external FILES/FREEZE/checker pins and closed actual file roster were independently authenticated. The top checker imports pathlib and json before checking interpreter mode. Exact copied check.py invoked with `python3 -S` executes an injected json.py marker before rejecting the mode (UNSAFE-SHADOW.json). compile.py and native/build.py have the same ordering defect by inspection.

The file-roster check also ignores every file whose basename is FILES.json/FREEZE.json, wherever located, and ignores empty directories and nonregular entries. ROSTER-CHALLENGES.json records three concrete copies with unlisted native/FILES.json, FIFO, and empty directory: all reach compilation dispatch after output creation. A subprocess sentinel intercepts the dispatch before any compiler runs. These are actual accepted inputs, not inferred execution of the added files. Directory symlinks are also not explicitly rejected; no separate exploit claim is made.

## Substantive model review

Read all new RawRecovery, RawSafety, NestedControl, LinkEmpty, LinkComposition, LinkPaths, driver and fixture definitions/proofs, the imported cleanup/history/program contract, complete relevant retained parser bodies and source-derived callback facade.

Raw recovery compares source-shaped mutable cache/tracking operations to a separate source-only cursor/token history. Both consume the same supplied lexical provider and block classification; this proves control/observer refinement relative to that provider, not tokenizer semantics. RawSafety derives pending-none after each cleanup and recovery step. Cache retention and comment directive writes are separate proved observations. Byte-fuel completion explicitly requires strict provider progress; it does not prove the real native parser progresses or that positions stay within valid UTF-8 bounds. A nonprogressing provider can make the finite model stop early, so alignment alone is not completion.

Nested control clears the pending opener, tests the depth limit, replaces the stop set, runs entirely, cleans pending content, consumes the original block and restores stops/depth. Fin 256 increment/decrement matches the retained wrapping native arithmetic. Missing opener is a model sentinel but a native panic; normal correspondence requires an opener. Restoration holds for represented callbacks (WrapperControl.Program) that cannot change depth/limit/control ownership. It does not establish restoration for arbitrary native callbacks, exceptions or unwinding. The stop list is interpreted as a delimiter set; native realizability requires allowed bytes. The finite snapshot renderer sums delimiter masks, so duplicate lists are outside its calibration admission.

PublicHistory.Aligned includes cursor/saved state, coherent cache, compatible tracking mode, cached-token seen invariant and relevant-observation equality. It does not include sourceURL/sourceMappingURL equality. The raw recovery write theorem separately establishes those writes; nested_refines alone is not a full nested annotation or line-location theorem. Shared lexical provider/reference mechanics remain explicit; no correct observation trace is passed as an input.

LinkComposition bridges higher-order wrappers only when given the represented program body. The real LinkEmpty grammar uses a separate callback implementation and six kernel-reduced concrete paths. Its commaLoop fuel is input length plus one; no universal grammar termination/completeness theorem is provided. The six results are real concrete facts, not arbitrary-input theorems. Failure/no partial publication follows from native `?` before final ArcSlice construction; allocation/publication is not modeled.

## Source and finite evidence boundary

The retained full cssparser crate is compiled with actual parser/tokenizer and instrumentation wrappers. The LinkParameters callback is a translated empty-value projection, not compiled Stylo: identifier/function/comma checks and the empty VariableValue scanner path are copied conceptually, while owned values, nonempty recursive scanner, URL context and provenance are omitted. Independently checked all 18 JSON input/action cases exactly equal the separately encoded Lean fixture. Whitebox limit/depth setters calibrate wrap and limit controls without proving public-history reachability.

Inspected historical preflight: 39 audits, 59 compiled modules, 18 cases/91 snapshots; three compiled native mutants change 10/25/5 observations. Lean mutations change cache writing, stop restoration and a concrete expected result. First two fail application/goals involving the changed operations; the third rejects the wrong concrete assertion. They are proof-rejection controls, not three successfully compiled semantic-mutant executions. Later independent replay must verify exact causes again. The current checker accepts any Lean diagnostic containing error; that broad mechanism alone is not semantic discrimination.

## Remaining admissions

Retained parser/tokenizer versions, semantic codec/tokenizer/UTF-8/progress contracts, cache-entry safe tracking, callback source translation, byte/set realization, compiler/runtime/heap, lines/columns, returned values, parse_until_after, general Link grammar and security provenance remain open. No whole parser, Stylo grammar, termination, browser behavior or taint-security closure is claimed. Current repairs to VariableValue do not silently rebind historical source pins.

No production/Git/browser/Firefox-build changes. Temporary copied challenge capsules and empty outputs were removed; retained unsafe-shadow source is harmless diagnostic input and is not imported by the review checker. No compiler targets were generated by this negative review.
