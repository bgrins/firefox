# CSS semantics in Lean

This is a standalone research library of explicitly scoped CSS models,
executable algorithms, and proofs connecting them. It has no Firefox, Stylo,
Bloom-filter, Aeneas, or Creusot dependency. The specification-to-model mapping
is manually reviewed; it is not itself mechanically proved.

## Start here

Install the Lean version in [lean-toolchain](lean-toolchain) and Python 3. From
this repository, run:

```sh
python3 check.py
```

The command builds the library, runs the ordered executable cases, checks the
axiom dependencies of the public theorem inventory, validates the coverage inventory, and
checks two deliberately invalid proofs are rejected for the intended reasons.
No additional Lean packages are required. Once Lean is installed, the proof run
does not require network access.

For an unpacked toolchain, pass its Lake executable explicitly:

```sh
python3 check.py --lake /path/to/lean/bin/lake
```

The result is [.lake/verification/report.json](.lake/verification/report.json),
with source fingerprints, commands, log hashes, ordered case outcomes and exact
axiom inventories. A failed run removes the previous acceptance report. Use the
counts in that report for the sources you checked; counts are not percentages of
CSS coverage. A proof run does not run the browser comparisons.

## What is checked

| Area | Representative result | Main boundary |
| --- | --- | --- |
| Selector matching | [`Selector.matchesBool_iff`](CssSemantics/Executable.lean) equates executable matching with the declarative relation. | The supplied forest and normalized selector profile must satisfy their input contracts. |
| Cascade | [`Cascade.winner_spec`](CssSemantics/Cascade.lean) proves the selected entry belongs to the candidates and is maximal under the modeled order. | Candidate applicability and cascade-key construction are separate obligations; this theorem alone does not model every cascade feature. |
| Computed values | [`Style.compute_sound`](CssSemantics/Style.lean) connects supported matching, cascade and literal defaulting/inheritance. | The property profile and host interpretation remain explicit. |
| Whole-source processing | [`CssContainerRun.run_iff`](CssSemantics/CssContainerRun.lean) characterizes the executable source pipeline against its admitted relation. | Strict supported syntax, resource outcomes, conditions and context restrictions remain. |
| Source provenance | [`CssContainerInputRun.actual_bound`](CssSemantics/CssContainerInputRun.lean) binds completed entries to supplied root or resource source text. | Supplied resource data is distinct from a proved browser acquisition mechanism. |
| Origin and rollback | [`OriginRollbackInterval`](CssSemantics/OriginRollbackInterval.lean) and [`OriginRollbackTraceLaws`](CssSemantics/OriginRollbackTraceLaws.lean) connect origin/layer removal to ordered winner histories. | Three static origins, per-origin layer order and author-only attached styles; no animation, transition or shadow-context cascade. |
| Extension compatibility | [`CssOriginCompiledEmbedding.compute`](CssSemantics/CssOriginCompiledEmbedding.lean) preserves successful author-only computation with empty user/UA inputs. | This does not equate failure behavior or arbitrary unavailable resource catalogs. |

The [coverage inventory](coverage.json) maps each checked fragment to its modules,
theorems, specification references and exclusions. The [coverage map](research/coverage-map.md)
summarizes larger algorithm families. The [specification inventory](research/current-spec-inventory.md)
records the dated drafts used by the models. These distinguish earlier normalized
models from later source-processing extensions; their profiles are not silently
combined into a claim about arbitrary CSS.

## Browser comparisons

Browser fixtures provide finite evidence about the interpretation and adapters.
They do not prove browser refinement. Fixture generation uses the checked Lean
model; browser measurements retain the actual source, DOM, CSSOM, resources,
executable identity and admission checks.

The earlier accepted named-container checkpoint is `7ef9ece`. Its proof checks were
reproduced from a source-only committed archive. The recorded browser comparison
has 113 agreements out of 115 visibility queries. The two false-supports
import/layer-order disagreements were subsequently reduced to one reproduced
Firefox defect, with normal and important manifestations. The
[investigation](research/import-layer-investigation-20261017/REPORT-v2.md) includes
standalone pages, a current specification trace and Firefox/Chrome comparisons.
The [recorded evidence](research/named-container-browser-evidence.json) and
[disagreement inventory](browser/named-container-discrepancies.json) preserve the
original actual and expected values. No production fix is included.

The origin extension adds ordered user-agent, user and author source roots,
separate layer registries, and source-derived `revert` and `revert-layer` for
`visibility` and `container-name`. Root URLs, imported sources, attached author
styles, rollback histories and successful author-only compatibility are explicit
parts of its model. It preserves the earlier named-container profile boundaries.

Its recorded comparison has 138 agreements out of 141 visibility queries across
131 scenarios, with 1,310 container-name readbacks and 21 protocol controls.
The [origin evidence](research/origin-cascade-browser-evidence.json) and
[disagreement inventory](browser/origin-cascade-discrepancies.json) retain the
original import pair and a separate important-user-layer ordering mismatch.
Reduced controls also reproduce the latter behavior in agent-origin layers.
Normal user layers and important author layers pass those controls; there is no
claim of layer registration leaking across origins. See the
[specification trace and reduced controls](research/origin-important-layer-order-trace-20261017.md)
and [source explanation](research/origin-important-layer-source-20261017/REPORT-v1.md).

The local browser runner for this checkpoint is:

```sh
python3 origin_cascade_browser_check.py \
  --firefox "/Applications/Firefox Nightly.app/Contents/MacOS/firefox" \
  --binary-kind installed-nightly
```

Run `check.py` first. This installed-Nightly adapter requires that explicit macOS
executable path. It also accepts an explicitly identified local build through
`--binary-kind local-build`. Use `--lake` with the same toolchain when needed.
The runner creates a temporary browser profile and local HTTP server. It installs
user/agent sheets through Firefox's privileged per-document API, checks their
actual origin and CSSOM, and removes them after each scenario. It checks a finite
inventory of relevant built-in rules and layers; this is not a model of every
browser default. This browser procedure has been exercised on macOS only.

Read `protocol_status` and `model_agreement` separately in
`.lake/browser-check/origin-cascade-visibility/report.json`.
Exit zero means the acquisition/admission controls and recorded disagreement
inventory were reproduced. It does not mean every computed value agreed. A new
or changed disagreement fails the gate and needs investigation. The earlier
`named_container_browser_check.py` remains available for its historical profile.

## Raw `@scope` source extension

The separate scope facade parses explicit scope starts and optional limits,
enumerates matching root assignments for nested scopes, and computes selector
specificity and proximity for each assignment before applying the cascade.
A root cannot be its own limit. Scope proximity breaks ties after specificity;
it does not override origin, importance or layer precedence.

[`CssSourceScopeStyle.compute_iff`](CssSemantics/CssSourceScopeStyle.lean)
connects this executable source-to-visibility pipeline to its admitted relation.
[`CssScopeSelector`](CssSemantics/CssScopeSelector.lean) separates declarative
matching from executable matching; [`CssSourceScopeCandidates`](CssSemantics/CssSourceScopeCandidates.lean)
connects all root assignments to the candidate list. Source parsing, layer
registration, per-origin ordering, attached author declarations, supported
container metadata and rollback remain explicit stages and obligations.
These generic proofs are distinct from the finite kernel-checked examples and
browser fixtures.

This facade accepts explicit, nonempty scope starts; optional limits; standalone
`:scope` and `&` compounds in supported selector chains; and supported ordinary
selectors. Unsupported forms return unavailable. It excludes imports, omitted
scope starts, direct declarations in scope blocks, anchors inside functional
pseudo-classes or compound combinations, shadow trees and dynamic mutation.
The earlier origin/import facade remains available with its own profile.
The new profile does not silently combine every earlier extension.

The browser fixtures include nested-root proximity, strict descendant limits,
per-assignment specificity, layer registration, origins, attached declarations,
container metadata and rollback. The nested-proximity fixture encodes a bug
found during source inspection and model design; it was not discovered by a
Lean-generated counterexample. Agreement on a patched Firefox build is finite
adapter evidence, not a proof of Gecko refinement. In particular, the model uses
exact natural-number distances while Firefox clamps finite scope proximity at
65,534; these shallow fixtures do not validate that boundary.

After `check.py` passes, run the separate scope comparison against an explicitly
identified browser build:

```sh
python3 source_scope_browser_check.py \
  --firefox /absolute/path/to/firefox \
  --binary-kind local-build
```

Use `--lake /path/to/lean/bin/lake` when needed. Its report is
`.lake/browser-check/source-scope-visibility/report.json`. Check protocol
admission and model agreement separately; recorded historical origin results
are not replaced by this comparison.

Acceptance requires the integrated proof/axiom gate, independent fresh-source
verification, a native comparison bound to regenerated fixtures and the exact
browser executable and libraries, and committed source-archive reproduction.
The scope review entry records which gates completed for a given checkpoint.
Isolated results under `.lake/source-scope/` are development evidence, not a
substitute for those gates. Earlier browser disagreements remain preserved.

## Owner-derived implicit `@scope` roots

The separate [host facade](CssSemantics/CssOwnerScopeHostEvaluation.lean)
acquires static inline HTML style owners in actual tree order and parses their
own child text. Omitted scope starts use that owner's parent element. The
[public provenance](CssSemantics/CssOwnerScopeHostProvenance.lean) connects the
same acquired source and owner to scope assignments, candidates and retained
metadata/visibility traces. [Unavailable history](CssSemantics/CssOwnerScopePublicFailure.lean)
retains the offending source scope header, including empty blocks.

The bounded nested profile requires the owner parent inside every reached outer
scope. One incompatible assignment makes the whole observation unavailable;
it is not silently discarded. Above-outer omitted-root semantics remain an
unsettled specification interpretation. Imports, shadow/adopted ownership,
non-element tree-root fallback and ownerless implicit scopes are excluded.
Explicit-rule specialization is proved; blanket old parser/acquisition
compatibility is not claimed. See the [contract](research/owner-scope-contract.md)
and coverage inventory for host/CSP and syntax premises.

This package adds 61 modules, 270 audited laws and 61 executable checks. Its
finite browser corpus has 20 scenarios, 20 visibility comparisons, 240 metadata
readbacks and 15 controls. After the complete proof gate, run:

```sh
python3 owner_scope_browser_check.py \
  --firefox /absolute/path/to/firefox \
  --binary-kind local-build \
  --lake /absolute/path/to/pinned/lake
```

The report is `.lake/browser-check/owner-scope-visibility/report.json`.
Acceptance requires the main proof report, independent source-only fresh run,
producer-bound browser evidence and committed source-only archive reproduction.
Isolated development captures do not replace these gates; earlier evidence is
preserved separately.

## Accepted results and experiments

- `CssSemantics/`, `tests/`, `coverage.json` and the runners are the source artifact.
- The [review history](research/extension-review.md) records independent checks
  and the boundaries of each accepted checkpoint.
- `.lake/` contains generated builds, reports and isolated working experiments.
  It is excluded from source archives and is not required as an input to a clean
  proof build.
- Research notes may describe proposals, failed probes or partial feasibility.
  Those do not extend the accepted model or browser coverage.
- Origin checkpoint acceptance requires the integrated proof gate, an independent
  fresh-source run, the producer-bound native protocol, and reproduction from a
  committed archive outside the Firefox checkout. Research probes alone do not
  satisfy these gates. The retained early windowless acquisition failures remain
  setup-domain evidence, separate from the later rendered browser results.

The [README](README.md) retains the detailed development history. Historical
counts and exclusions there describe their individual checkpoints.

## Trust and limitations

Lean's kernel checks proof terms. The audit permits the standard foundations
`propext`, `Quot.sound` and `Classical.choice`; no admitted proof or new custom
axiom is accepted. Input contracts, manually chosen declarative relations,
specification interpretation, host adapters, compiler/runtime behavior and finite
browser observations remain distinct parts of the trust boundary.

This library does not establish all-CSS conformance, a mechanically translated
CSS specification, or correctness of Firefox. Layout, rendering and many other
families remain outside the supported profiles. See the coverage inventory for
the precise boundaries before applying an individual theorem.

## Updating a model

Record the specification revision and affected sections, state the supported
domain and unknown/error behavior, and review the declarative interpretation
independently. Add cases that distinguish the changed behavior, update the
coverage inventory, and run the proof gate. Where a browser adapter exists,
retain its previous expectations and explain each changed observation. An
accepted extension also needs fresh source-only reproduction and review of its
remaining assumptions.

## Ordinary imports and raw scopes

The bounded composition is exposed through [CssScopeImportHostEvaluation](CssSemantics/CssScopeImportHostEvaluation.lean). [InstanceRun](CssSemantics/CssScopeImportInstanceRun.lean) and [ExactEventSource](CssSemantics/CssScopeImportExactEventSource.lean) bind candidates and unavailable empty scope blocks to the same supplied root or selected imported resource. [ResourceOwner](CssSemantics/CssScopeImportResourceOwner.lean) derives imported ownerlessness; [FacadeTotality](CssSemantics/CssScopeImportFacadeTotality.lean) excludes internal unresolved states on actual runs.

See [the contract](research/import-scope-contract.md) for lexical imported-scope restrictions, synthetic registration-view boundaries, source-only compatibility and finite host assumptions. Reproduce its generated browser comparison with `python3 import_scope_browser_check.py --firefox /path/to/firefox --binary-kind local-build --lake /path/to/lake` after the proof check. Its report is `.lake/browser-check/import-scope-visibility/report.json`; 20 comparisons, 240 metadata records and 15 controls are finite observations, not a browser refinement proof.

## Relative color component observations

`RelativeColorChannels` models original missing-channel carry followed by
component substitution, with source preparation/conversion and a math evaluator
supplied. It distinguishes bare missing keywords from numeric-zero math operands,
retains remaining analogous sets, and distinguishes unresolved origin acquisition
from unavailable conversion. Literal or math component progress does not establish
full relative-color validity or readiness. The generic math environment is not an
integration with the CSS expression evaluator. Numeric color conversion, IEEE
rounding, epsilon classification, parsing, serialization and native correspondence
remain outside this partial Color4/5 fragment. Synthetic faulty providers belong
to `RelativeColorChannelsExamples`, not the core semantics.

## Counter representation provenance support

`ImplementationSupport.CounterProvenance` separates authored inline integers,
resolved boxed math, omitted defaults and raw computed-value inverse lifts.
Its five existing laws characterize explicit minimum normalization, preservation
of other signed32 values, parser-domain marker exclusion, raw numeric roundtrip
and the marker observation used by serialization. Raw mapped values can still
contain the reserved minimum; numeric roundtrip neither authenticates parser
provenance nor reconstructs an expression tree.

This is implementation-specific machine/representation support, not additional
normative CSS coverage. It does not evaluate CSS math, authenticate all producers,
repair mapped-reset aliases or prove the native counter pipeline. It is separate
from `CounterGrouping` element semantics and `CounterInitializerBounds` range
premises. The five reviewed results are registered once; six executable controls
in `CounterProvenanceExamples` distinguish these source domains and a deliberately
incorrect blanket-clamp adapter. No CSS feature or spec-coverage entry is added.

## Conditional numeric implementation support

`ImplementationSupport.IntegerRoundingDyadic` retains six reviewed support laws
for the integer conversion that widens before adding one half: exact rational
encodings, bounded dyadic coefficient capacity, and floor-cell preservation
under an explicit error bound. `ImplementationSupport.RoundRemainder` retains
six reviewed laws for positive-step directed rounding: a supplied truncating
remainder yields adjacent multiples, directed extrema, global nearest selection
with upper ties, toward-zero selection and exact rational comparison transfer.
The separate Examples modules retain the original proof witnesses and add six
executable controls per module. These 12 existing results are registered once;
registration adds no research theorem credit or normative CSS feature coverage.

This is conditional implementation support, not a complete IEEE or CSS round()
model. Native bit reinterpretation, binary64 correct rounding/error bounds, exact native
remainder, final binary32 projection, signed zero, special values, signed 32-bit
saturation and compiler/source refinement remain explicit external obligations.
The small-value theorem requires a strict error-versus-boundary margin; it does
not claim every promoted addition is exact. The remainder contract supplies an
unbounded integer quotient witness, not the potentially rounded native quotient.
The separate all-finite SMT result is not promoted to a Lean certificate.

Source correspondence as reviewed on 2026-10-24: the dyadic module supports the
promote-before-add expressions in `Integer::resolve` and
`Integer::to_computed_value` in `values/specified/number.rs`; the remainder module
supports finite nonzero-remainder bound reconstruction and strategy selection in
`values/generics/calc.rs`. These links identify conditional obligations, not proof
that native execution satisfies them. Existing `CssIntegerRounding` unit-step
semantics remain distinct. `coverage.json` is unchanged.

## Supplied subgrid line-list fragment

`SubgridLinePrefix`, `SubgridSequencePrefix` and `SubgridWholeAutofill` provide
bounded-prefix correspondence for fixed repetition sequences and one auto-fill,
whole-pattern maximality, and trailing unnamed-group padding. Inputs are supplied
line-name groups and line capacity; an unnamed group is one element, while an
empty pattern is not an admitted CSS repeat. The closed-form nonexhausted result
requires positive fixed counts and nonempty patterns. Twenty literal WPT oracles
exercise this fragment; they do not establish native or full Grid refinement.

The mapping follows the retained Grid Level 2 source plus CSSWG's 2025-08-13
resolution of issue8493. The visible draft's auto-repeat paragraph had a remainder
ambiguity; this model does not claim that prose was already amended. Parsing,
name scope, box participation, placement, line-capacity acquisition and coordinates
remain external. Only the narrow supplied-list fragment is mapped in coverage.json.

`ImplementationSupport.SubgridCountTransport` and `SubgridGuardedConsumer` are
separate arithmetic support: capped products and sums preserve remaining capacity,
and full-width guarded subtraction bounds the narrowed result even for negative
native caps. These laws do not prove a layout capacity is valid. Cached-observer
correspondence requires capacity <= signedMax <= storageCap; machine arithmetic,
FFI layout, allocation behavior and compiler refinement remain unproved. The
old narrowing functions are explicit countermodels and not CSS definitions.

Nineteen already reviewed public results are registered exactly once, with 28
executable checks (20 WPT oracles, four support controls, four false claims).
This adds no new research theorem credit or overall CSS coverage percentage.

## Conditional counter descriptor representation support

`ImplementationSupport.CounterRangeRepresentation` separates inline, boxed-resolved
and unresolved integers from semantic finite/infinite endpoints. Its eight existing
results connect independent finite-bound validation and ordering to total, inclusive
resolved export. An infinite peer never licenses skipping finite-bound validation;
a successful short-circuited lookup does not establish the publication invariant.
`ImplementationSupport.AdditiveOrdering` imports that representation once and adds
three existing laws connecting a supplied resolved finite list to strict adjacent
ordering and representation-independent results. CSS admission requires a nonempty
list and nonnegative weights; the mathematical empty-list convention is not admission.
The negative example shows why supplied raw negative values cannot replace correct
nonnegative resolution. Parser/export must use the same resolution policy.

These modules are conditional implementation support, not new normative CSS feature
coverage. The independent reference functions `member`, `ordered` and `descending`
reflect CSS Counter Styles Level 3 range and additive-symbols rules (retained primary
sources reviewed 2026-10-24). `admitted` is an implementation publication invariant;
it does not prove that every contextual expression is normatively invalid. `inlineGet`,
`oldAdmitted` and `inlineGreater` are explicitly historical accessor/countermodels,
not CSS definitions. No machine rounding, saturation, expression evaluator, specified
serialization, native parse/FFI/lifetime correspondence or browser refinement is proved.
Stable supplied resolution and preservation by every publication/mutation route remain
external. Range-list union, fallback and additive symbol generation are outside scope.

Eleven previously reviewed results are registered once: eight range declarations plus
three ordering results; the eight imported declarations receive no duplicate credit.
Twenty-two anonymous proof examples and eight executable controls (two expected false)
are retained. `coverage.json` remains unchanged; no overall CSS coverage percentage or
new research theorem credit is claimed.

## Finite Round scalars and separate magnitude support

`CssFiniteRound` models the four traditional strategies on supplied exact rational
scalars with an explicit finite nonzero step. It proves adjacent-multiple bounds,
exact-input and zero-sign preservation, nearest upper ties, and general toward-zero
equivalence to minimum absolute bound selection. It reuses finite signed scalars,
extended reciprocal and clamp. This is partial Round coverage: line-width and
device-pixel snapping, omitted number-step defaults, units/types, parser admission,
nonfinite Round and native precision/refinement remain outside scope. None at zero
step marks exclusion. The infinite-step probe supplies a separate specified zero;
only seven of the eight observer cases execute this finite core.

`ImplementationSupport.RoundRemainderCapacity` and `Binary32Magnitude` separately
prove exact truncating-remainder magnitude capacity and a constructive finite
BitVec32 decoder equivalence on the common 2^-149 grid. Sign bits are deliberately
ignored by the magnitude decoder; exponent255 is excluded. Mathematical signed
tmod is distinct from Euclidean remainder and SMT fp.rem. Rust fmod/% correctness,
native bit reinterpretation, signed remainder-zero policy, f64 reconstruction,
final f32 projection and compiler/browser correspondence remain external.

Twenty-one existing declarations are registered once: capacity3, decoder7 and
finite Round11. The decoder imports the same capacity module, without duplicate
credit. Thirty-seven original anonymous examples are retained; twenty executable
controls include five expected-false observations. Integration adds zero research
theorem credit and no overall CSS coverage percentage. Only supplied finite Round
gets a narrow coverage entry; the machine-support modules add no CSS feature.


Conditional Round knowledge support adds four previously reviewed audits and eight controls (four expected false), with no normative coverage increment. See README for partial-classifier limitations and the appended installed counter source mapping. Historical proofs and mappings remain unchanged.


Finite ModRem support transfers 28 existing audited declarations and retains 14 proof examples. The 24 appended executable cases include 11 expected-false controls. The two modules share the existing binary32 decoder/remainder capacity and four historical backend types, without duplicate proofs or research credit. Nearest projection permits a divisor endpoint and ties. Native remainder/addition, operand/sign and compiler correspondence remain assumptions; normative coverage is unchanged. README records the versioned accepted-patch mapping and limitations.


### Animation context and endpoint implementation support

Four support modules transfer the reviewed exact-rational common-context, finite-DAG cache/schedule and typed endpoint-history obligations. Canonical VariableExpr.substitute_congr and VariableProperty.compute/defaulting are reused rather than duplicated. Numeric initial/default metadata is distinct from missing var fallback: present empty and multi-token wrong types do not use that fallback. The single-token research fragment correspondence is separately proved in css-keyframe-token-list-adapter-v1.

Ranks, complete dependencies, winning operations, current provider context, registration profile and coherent sample remain supplied; no CSS-cycle/SCC, native arithmetic, scheduler, taint/URL, parser or whole-animation refinement is claimed. All are ImplementationSupport; normative coverage is unchanged. Copying proofs adds zero research theorem credit. Source mappings and deduplicated registrations are recorded in css-keyframe-animation-library-proposal-v1. Earlier negative-control reduction failures are distinguished from the newly decisive replay; actual canonical totals require a full check.

CommitStyles prefix refresh support (`ImplementationSupport.CommitRefresh`) transfers the already-reviewed covering-refresh theorem and its bridge to `KeyframeSchedule`. It preserves ordered per-property composition while refreshing every contributing effect against a supplied current provider context. Six audit declarations and nine executable cases (three deliberately false) are transferred research support, not new proof-discovery or normative coverage. Native context freshness, complete prefix selection, endpoint semantics, scheduling delivery and source refinement remain assumptions.


Endpoint source indices (`ImplementationSupport.KeyframeEndpointIndices`) transfer the reviewed finite-block prefix/recovery and conditional machine-bound model. Empty input blocks retain slots, and skipped outputs do not shift source declaration indices. Fourteen existing audits (eight primary lemmas, three helpers and three refutations) and eight executable cases (three deliberately false) are implementation support only, with zero new proof-discovery credit or normative CSS coverage. Stable prioritized traversal, immutable declarations, successful bounded storage and source correspondence are premises; input-block count has a separate machine bound from declaration count. The archived descriptor-v2 mapping and transfer accounting are recorded in `css-keyframe-endpoint-index-library-proposal-v1`; allocator behavior, native publication/lifetime, provider correctness and CSS semantics are not proved.


Computed property-name arguments (`GuardedNames`, `GuardedNamesExamples`) extend the existing guarded expression profile with normalized name-expression evaluation before target lookup. The static embedding preserves the complete value/mark-state result of `GuardedCompletion.resolve`; the old snapshot and guarded profiles and their audits remain unchanged. Name-evaluation marks survive decoding, lookup and fallback. The parser is supplied under `NameAdapter` exactness against a caller-defined acceptance relation; identifying that relation with raw CSS custom-property-name parsing is a separate unproved boundary. No escape/token parser, spread, registration, taint, native cache, active animation provider or animated-SCC correspondence is claimed. Twenty-five already-replayed standalone statements are transferred once, with fifteen executable controls (twelve true and three intentionally false). This is a normalized conditional profile, not a new full CSS feature or proof-discovery credit. See `css-variables-computed-name-library-proposal-v1` for source/preimage mappings and pending integration validation. Earlier profile exclusions remain accurate for those fixed-name modules; this additional adapter does not silently broaden their theorems.


Steps origin/range support (`StepsOrigin`, `StepsOriginExamples`) transfers ten reviewed consumer laws without changing their proof bodies. Eleven original proof examples remain, with fourteen executable observations including three same-claim false controls. The normalized calculation origin is preserved separately from authored literals; resolved calculations clamp to the position minimum while unresolved values retain rejection. Existing numeric censoring, integer rounding and bounded finalization are reused. This is a transfer with zero new proof-discovery or normative-coverage credit, not a parser or native refinement. Native origin classification, context-free resolution, positive normalization, IEEE conversion and machine bounds remain external premises. See `research/steps-origin-range.md` for the exact mapping and excluded behavior. Proposed totals require the later full canonical checker; this artifact does not update live results.
