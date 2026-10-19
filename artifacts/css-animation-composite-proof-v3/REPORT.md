# Composite-only keyframe update companion v3

## Result and claim

The candidate changes one production comparison: specified per-keyframe composite participates in the unchanged-input decision. The original and candidate full source snapshots have SHA-256 identities `121eec5283f3d25bfb6b7c31ee6124f5dda3e95608bde77ed2204eb3d4ca3eda` and `e17ad778f6279f17eda31b764ea2d52edbe82de50aa44d69a1a995d4d51b75d8`. The unrelated DEBUG comparison remains unchanged and is not evidence of preservation.

The companion establishes two separate results:

1. Lean proves refinement of an optimized specified-state setter by an independent direct setter over arbitrary finite model action sequences. Frames are typed, declaration allocation is separate from immutable declaration contents, all four specified composite operations remain distinct, and computed offsets are derived state. The proof preserves history-certified property/base/offset caches through arbitrary finite actions, including explicitly pending invalidation states. Current freshness is concluded only when delivery has completed and offsets are valid. Admitted sequence refinement requires delivered readiness at every equal-input skip. The full invariant derives current offsets, properties and active base values at every such prefix, and proves the skip preserves them. Pending-style and missing-timeline diagnostics remain covered separately by native agreement and the all-actions history invariant. It includes concrete rational offset and endpoint/segment construction, property/base/event transitions, running-property retention and cumulative-property identities.
2. A finite source extraction executes complete native functions against admitted boundary adapters and agrees with an independent raw-input oracle. The corpus has 700 cases and 5,341 action observations. It compares stored raw fields, derived offsets, range flags, complete getter dictionary/property writes, consumer segments, base values, compositor flags, cumulative counts and ordered provider/event traces. These are action observations, not 5,341 independent full matching calls or browser tests. `NATIVE.json` gives the exact operation breakdown and original disagreements.

This is not a compiler-correctness proof, a universal IEEE arithmetic theorem, or a proof of parsing/layout/rendering. The bridge obligations and exact restrictions are in `BRIDGE.md`. The universal mathematical model and finite native agreement must not be merged into a stronger claim.

## V3 delivered-readiness correction

The v2 independent review accepted its authentication, null-provider and current-restyle corrections but withheld the full formal contract: an offset-valid equal setter could still be admitted while its property/base caches were pending. V3 strengthens admission to delivered readiness and proves current coherence at every admitted equal-setter prefix of arbitrary finite action sequences. This completes the original obligation without substituting historical cache validity for current coherence.

Generic dispatch theorems establish readiness after changed setters, changed defaults with delivered offsets, style updates from raw offset-input certificates, and offset delivery followed by style delivery. They assume actual dispatch gates and raw-input identity, not expected final cache equations. Kernel examples include ready skips, failures, defaults, absent target/style, offset-then-style delivery, rejection of pending equal skips, and rejection of style-only delivery while offsets remain stale.

The native readiness monitor consumes raw provider versions and complete native dispatch traces. It certifies 3,275 ready prefixes and 247 ready equal skips; 287 equal skips remain withheld pending diagnostics. Of 700 complete case sequences, 475 satisfy ready admission at every equal-setter step, including sequences with no equal step. The receipt separates nonvacuous counts. All cases still run and agree with the independent oracle. No case is deleted to obtain those admission counts. Readiness is established before independent current-output checks; the detailed raw keys, traces and classifications are retained in `DELIVERED-READINESS.json`.

All 691 v2 cases (5,265 actions), 29 complete definitions, 34 full native/provider source snapshots and all 20 mutation families are preserved. Nine additional cases contribute 76 actions. A deliberately unchanged-valued provider invalidation still withholds readiness until dispatch, demonstrating that correct-looking output caches do not admit a step. `V2-PRESERVATION.json` authenticates the unchanged source/generator/adapter/oracle/mutation closure and exact original action records. The specification, source, numeric and external-scheduler boundaries remain explicit in `READINESS-BRIDGE.md` and `BRIDGE.md`.

## Corrections from v1

The independent review rejected v1's executable closure, cache theorem boundary and null-value adapter, and identified a restyle witness that could use historical events. The preserved review and concrete diagnostics are under `evidence/v1-independent/`; v1 remains unchanged. These are artifact corrections, not additional Firefox defects.

V2 requires isolated Python startup, authenticates an exact inventory before project imports, rejects unlisted packages/modules and malformed paths, and copies authenticated source bytes into a fresh read-only source capsule. A second process reauthenticates that capsule before imports. Tamper cases invoke the normal replay path and must fail before creating outputs or executing a shadow package. The trusted checker and external manifest digest must be verified separately before execution; OS/compiler/library integrity and concurrent same-user filesystem attacks are not claimed to be proved.

The cache model now separates geometry from style/target inputs and preserves certificates for pending caches until real dispatch. Native/oracle/model computed values retain null AnimationValues; synthesized missing endpoints are distinct entries with their actual endpoint operation. The base-only restyle kernel witness clears prior events, so its witness comes from the current rebuild. All original 662 cases and all 20 compiled semantic mutations are retained; 29 new cases add null endpoint and pending/restored-cache controls. Exact final counts, axioms and mutation witnesses are recorded by replay.

## Native closure

`generate.py` extracts complete definitions directly from authenticated full source snapshots. The generated extraction inventories identify every definition by source path, full marker, byte count and SHA-256. Entry logging is inserted immediately after selected opening braces; it does not replace or omit any body statements. Original and candidate extracted definitions are identical except the production comparison.

The closure includes the Keyframe, PropertyValuePair, offset, AnimationProperty and AnimationPropertySegment records; complete property-value equality and array comparison; both ordinary SetKeyframes overloads; complete GetKeyframes; ordinary GetComputedKeyframes; offset distribution, named-range normalization and refresh; SetComposite; BuildProperties; UpdateProperties; EnsureBaseStyles and EnsureBaseStyle; computed-value provider dispatch; endpoint operation resolution; stable sorting, segment construction and all missing-endpoint helpers.

The complete getter runs actual dictionary construction, typed-union branches, easing/offset/composite writes, CSS property naming, declaration/base serialization dispatch, property definition and error returns. Its typed JS adapter is a boundary for the JS engine and generated WebIDL conversion; it is not a handwritten replacement getter.

Full source snapshots retain parsing, Servo declaration equality/serialization, computed values, base styles, timeline geometry, constructors, CSSAnimationKeyframeEffect bookkeeping and the CSS shared caller. The compiled and traced/admitted portions are explicitly distinguished in `BRIDGE.md` and the provider inventory.

## Mutation evidence

Twenty native semantic mutants must compile successfully, execute successfully and produce a concrete state or trace disagreement. They cover omitted composite/offset/easing/properties, first/last-only or length-ignoring comparison, auto collapsing to replace, dropped storage, skipped offset recomputation, notification gate errors, skipped property/default/range updates, suppressed restyle/effect notifications, and lost endpoint operation resolution.

Each has a Lean counterexample checked by kernel reduction. An additional compiled adapter-regression diagnostic reinstates the old null-to-base substitution and must disagree with the corrected oracle; `null_is_not_base_value` is its kernel witness. No failed compilation, process crash, theorem elaboration error or native evaluation axiom counts as a witness. The skipped-recomputation mutant stops after the first setter observation, before an intentionally invalid cached offset could trigger a getter assertion. The original full source variant and omitted-composite mutant must produce identical observation rows.

The canonical Lean receipt lists all theorem names and their kernel axiom dependencies. The allowed standard axioms are `propext`, `Classical.choice` and `Quot.sound`; `sorryAx` and native-reduction axioms are rejected.

## Coverage and controls

The corpus covers all 16 specified operation transitions across target/style/animation/relevance combinations; empty, singleton and multi-frame arrays; first/interior/last changes; lengths and ordering; offset/easing/property changes; equal declarations in distinct allocations; unchanged raw derived fields; missing and duplicate offsets; named offsets outside the ordinary interval; unresolved/zero-attachment-range contexts; NaN-to-NaN refresh; successful and failing processing/getter paths; default/base/style changes; and preserved compositor-running flags. Ordinary specified offsets are finite and ordered; named offsets may resolve outside `[0,1]`.

Signed-zero controls record sign bits separately. Native equality treats `+0` and `-0` as equal and an unchanged-input skip retains the previous sign. A subsequent real specified-field change stores the new sign. The rational theorem quotients signed zero; it does not prove `Object.is` preservation for this corner. No additional browser defect is claimed from this control.

The bounded native geometry provider supplies affine maps and unresolved cases, records the requested range name, and the complete native resolver applies the actual attachment-range normalization. Native corpus geometry does not reconstruct layout or independently vary every named-range map. The Lean environment permits separate maps per range name. Missing/ranged mixing and unresolved NaN behavior are current implementation contracts with documented specification gaps, not newly asserted normative CSS behavior.

## Cost and external evidence

`COST.json` records 50 samples over five family sizes and changed/unchanged setters, with stable observable checksums. It times the candidate extracted core, supplied-record parsing copies, boundary providers and tracing. It excludes the browser, JS runtime parsing, layout, sampling and painting. It is a bounded implementation-cost receipt, not a browser performance comparison.

Root and the independent native reviewer own the browser evidence: 70 candidate new cases pass, compared with 52 failures and 18 passes on the original; 340 existing cases remain passing. The retained independent report and final native/WPT pins link that evidence. It is not rerun or counted as formal proof by this artifact.

No new bug was discovered by this companion. The composite omission was statically identified, then independently reproduced in a browser before this proof was built.
