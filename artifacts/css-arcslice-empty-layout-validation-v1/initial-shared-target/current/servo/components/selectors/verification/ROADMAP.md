# Stylo verification roadmap

This tracks the six milestones agreed for the local verification project.
A milestone is complete only when its stated evidence has been checked and its
implementation and claims have received independent agent review. Work stays
local; Try pushes and patch submission are outside the current authorization.

## Proposed roadmap: October 16, 2026

The recommended target is one complete production result: a successful match of
`section > span` cannot be falsely rejected by the ancestor Bloom filter under
explicit DOM, library and resource assumptions. Finish this composition before
expanding selector coverage. This proposal supersedes the earlier work sequences
retained below with their technical evidence.

### Current position

- Milestones 1, 2, 3 and 5 have checked checkpoints. Milestones 4 and 6 remain
  open: enumeration and both actual providers now have conditional acceptance;
  native recovery composition and actual matching's connection to the ancestor
  region remain incomplete.
- The two-event production callback experiment passes all 180 solver obligations
  across twenty models, under explicit primitive and spare-capacity contracts.
  Incorrect companion contracts fail acceptance; their timeouts are not
  counterexamples.
- The arbitrary finite-event candidate now has a complete conditional solver
  checkpoint: 220 obligations from the other models and all fifty induction and
  provider-use obligations pass. Fresh compilation reproduces all twenty-two
  models exactly. Both incorrect proof controls fail acceptance. Independent
  review confirms complete root and branch coverage; the earlier six timeouts
  remain recorded separately.
- Twelve isolated Lean bridge lemmas are checked. The newest three construct
  traces from indexed callback states and exact per-edge primitive results,
  without assuming a whole trace or vector-observer injectivity. Native
  observation correspondence and allocating pushes remain open. These experiments
  remain separate from the accepted 174-audit recovery checkpoint.
- The encoding bridge passes eleven additional axiom audits in a fresh guarded
  run and independent review. It preserves unsigned values, ordered append and
  all 4096 counters, including sequential saturation at coincident indices.
  Its adapter keeps complete native state separate from observations. Native
  observer meaning and coherent vector-push successors remain explicit; this
  is a mathematical encoding, not an imported Why3 theorem.
- Fresh compilation and model-equivalence audits now cover both the bounded and
  finite candidates, with source, tool and dependency inventories checked.
- An ordinary callback with the real allocating Vec operation passes eight
  normal-return proof obligations. Its terminating generic variant is rejected
  as expected. This provides a supported route for the debug provider without
  claiming allocation success or marking the operation ghost.
- A borrowed class/attribute callback fixture passes 38 obligations, with an
  incorrect returned-length contract failing acceptance. Independent review
  confirms captured-vector state and ordered callback propagation. A fresh
  non-Copy variant also passes 38 obligations without adding runtime owner
  copies or clones; its source, models and prelude guards pass independent
  review and the acceptance audit. Native atom representation and DOM
  correspondence remain open.
- The unchanged production enumeration and exclusion bodies now translate to
  seventeen models with the corrected borrowed wrapper interfaces. The guarded
  induction run passes all 195 main proof obligations, with forty helper
  obligations checked separately and all original roots accounted for. Fresh
  compilation reproduces all seventeen models apart from audited source-location
  paths. Independent reviews cover the positive proof and fresh compilation.
  Both deliberately false proof controls fail acceptance: one full-root timeout
  and two prefix timeouts. These are rejection checks, not counterexamples.
  The identity-based exclusion helper also passes its separate collision control.
  The combined acceptance audit and independent review pass, including checks
  that missing or malformed manifests remove stale acceptance output. This result
  is conditional on primitive DOM contracts and normal return; native/provider
  composition remains open. The earlier direct run's 59 successes and eight
  timeouts remain recorded.
- A combined fixture now contains the unchanged enumeration and both actual
  provider bodies. Fresh compilation produces 33 models; the original seventeen
  match apart from audited source paths, and all 195 enumeration obligations
  pass again. The fourteen new supporting models contribute 117 successful
  obligations and one explicitly empty refinement model.
- The combined provider acceptance audit and independent review now pass:
  425 successful obligations across 33 models, including 58 for insertion and
  fifteen for the debug vector. Insertion readiness follows from count and
  spare-capacity bounds. All four deliberately false controls fail acceptance;
  every unrelated obligation passes. One dependent debug-frame target is
  distinguished from the four primary false targets. Missing or malformed
  manifests remove stale acceptance output. Native recovery composition and
  allocation-enabled completion remain open.
- The scoped native atom classifier passes eight Lean audits and independent
  review. Its fixed source/model audit covers exactly three excluded-name
  comparisons and the two actual borrowed callback instantiations. It preserves
  raw hashes independently and explicitly rejects general atom-identity or
  equal-classifier/equal-hash claims. Native equality and lifetime meanings
  remain assumptions.
- Two coherent-vector bridge lemmas pass guarded Lean checks and independent
  review. They construct successive vector witnesses from a local primitive
  refinement, then obtain extracted callback calls and restoration from the
  existing bridge. The actual native transition trace and primitive refinement
  remain premises; the separate Rust candidate must carry those transitions
  through its actual callback before composition.
- The separate vector-transition candidate passes its scoped checkpoint and
  independent review: 27 actual push obligations, three callback/chain
  transition tasks and all 58 insertion replay tasks. The primitive relation is
  carried by the real callback. This is not full coverage of the new model set,
  a native primitive refinement, or a provider trace-witness proof. The separate
  public-trace candidate below closes the provider witness obligation.
- The public provider trace candidate now has conditional aggregate acceptance
  and independent review: 446 successful obligations across all 33 models,
  comprising 195 enumeration, 78 insertion, fifteen debug-vector and 158
  supporting obligations. Thirteen models are explicitly empty. The witness
  projects actual callback states and retains exact opaque vector endpoints.
  Both false trace/future controls fail only at their intended targets. Removing
  the primitive transition guarantee leaves only the actual push helper's
  transition obligation unproved. Missing or malformed manifests remove stale
  acceptance output. Native primitive interpretation and recovery composition
  remain open; this result does not prove allocation-enabled completion.
- The matcher gate has a concrete verifier limitation: a reduced context retaining
  the live dynamic callback, associated data and mutable cache borrow is rejected
  before model generation. Preserve this reproducer and scope the required
  verifier support separately; enumeration work can continue.
- A typed interpretation certificate now connects the exported provider-trace
  predicate to Lean, with four checked lemmas and seven rejected mutation
  controls. The generated predicate retains the exact witness and its opaque
  endpoints; this is a scoped interpretation, not a general verified importer.
- The conditional history application passes three guarded Lean checks and
  independent review. It derives callback calls, the represented final hash
  vector and high-water history from that same witness. A wrong-endpoint control
  fails at the intended representation obligation. Native continuation
  correspondence and primitive interpretation remain explicit open boundaries.
- The two production fixes now have separate signed commits containing only
  their production changes and WPTs, with opt-in Rust reproducers and supporting
  documentation in preceding commits. Both patches apply independently to the
  original base; all five rewritten prefixes pass their default Rust suites.
- The unchanged native storage push now has independently reviewed conditional
  observation coverage across 43 models: 194 supporting obligations and 286
  freshly checked provider obligations. The sealed container interface supports
  only the actual hash and element-record array types. Removing the independent
  element-capacity premise leaves the actual record push unproved. A separate
  trace-export candidate retains the provider witness with exact native vector
  endpoints; its 25 storage obligations pass, with 42 other models preserved
  apart from source locations. This gives 481 covered obligations using one
  proof strategy per model. Native primitive interpretation, the revised Lean
  bridge and recovery composition remain open.

### Recommended sequence

These are the next work packages, distinct from the original six milestones.
The accepted 425-obligation provider checkpoint stays fixed alongside the new
446-obligation public-trace checkpoint.

| Priority | Work | Completion criterion |
| --- | --- | --- |
| 1 | Finish validation of the public provider trace — complete | Combined audit and independent review pass for all 446 obligations across 33 models, every original root and branch, false trace/future controls, primitive dependency control and stale-acceptance rejection checks. |
| 2 | Connect the actual provider trace to recovery | Bind the generated trace to the encoding and coherent-vector bridges, preserving exact initial/final vectors, hash order and duplicates. Derive the storage history and compose recovery under explicit native primitive, DOM-stability and resource premises. |
| 3 | Resolve the narrow matcher verifier limitation | Transport the actual borrowed dynamic callback, associated data and mutable caches through a minimal context. Either support invocation faithfully or require a failing safety obligation at unsupported calls and prove those calls unreachable. Check incorrect borrow/future contracts and unsupported logical uses. |
| 4 | Prove the first complete selector result | For actual matching of `section > span`, derive the real ancestor contribution and compose enumeration, recovery, collection, packing and lookup. Successful matching without Bloom rejection must imply that the separate Bloom check accepts. Publish the complete assumption list. |
| 5 | Make the result reproducible and reviewable | Provide a guarded local entry point for the accepted composition, pinned tools and inputs, and positive/negative checks. Separate production fixes, browser regressions, proofs and verifier support into sensible local commits when signing is available. |
| 6 | Expand coverage from demonstrated gaps | Add one supported domain at a time: descendant combinators, IDs/classes, selected attributes/namespaces, then relative selectors. Treat vector growth and allocation as a separate resource extension. Require a composed result and relevant regression coverage for each extension. |

The main dependency chain is 1 → 2 → 4 → 5 → 6. Package 3 can proceed alongside
1–2 and is also required for 4. Reproducibility work starts with each package;
package 5 is its final integration gate. These packages close the remaining
parts of milestones 4 and 6 before broadening the project.

### Immediate next work package

Package 1 is complete. Preserve its 446-obligation aggregate report, independent
review, reproduction commands and source/tool/dependency fingerprints. The
accepted 425-obligation checkpoint and failed experiments remain separate.

Package 2 has the original typed interpretation certificate and conditional
provider-history application, plus a separate native storage checkpoint under
a revised sealed container interface. The unchanged `Storage::push_internal`
body now establishes its recorded hash count, appended element record,
high-water update and preserved fields on normal return with independent
hash-vector and element-vector capacity. The trace-export extension retains
the existing provider relation through exact initial and final sink endpoints.

Creusot rejects separate extern specifications for the two SmallVec
instantiations. The new candidate therefore uses one sealed typed interface
restricted to `[u32; 64]` and `[PushedElement<E>; 16]`, with transparent hash
projections and checked concrete hash-contract specializations. All actual
provider models were reproved under this interface. The genuine `TElement: Copy`
bound removes two old enumeration drop obligations; the remaining goal
mapping and adapted proof coverage received independent review.

The next gate is a reviewed interpretation of the new typed observer symbols
and storage trace into Lean, including the separate ordered element-record
sequence. The old provider certificate cannot be applied unchanged to the new
opaque symbols. Preserve the exact vector endpoints and derive the storage
history from the same witness, recorded count and high-water equation. Then
compose those observations with recovery. The local evidence and independent
reviews are under
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-history`;
component coverage is distinct from an installed aggregate acceptance
certificate.

The existing `StoragePushProofs.ProviderCalls` premise includes exact backward
function correspondence. The new normal-return trace does not discharge that
premise, so it cannot be used as a shortcut to the existing recovery theorem.

Do not substitute an assumed whole-provider trace or infer native vector identity
from equal observed hash lists. Native prophetic borrow frames and the Lean
backward-restoration function need separate interpretation; their individual
proofs do not identify a full native backward function. Account separately for
hash storage and the element-record stack, and require stable hashing between
insertion and pop. Begin with normal return and sufficient capacity; native
unsafe-library semantics and allocation-enabled completion remain explicit open
boundaries.

The next major review point is a provider-to-recovery composition with a precise
assumption inventory. If the matcher experiment requires broad verifier changes,
preserve its smallest reproducer and scope that engineering separately. Continue
recovery composition and targeted bug finding while the matcher gate is open.

### Native interpretation gates

**Atom comparisons.** The fixture's u32 identity field is not a proved encoding
of arbitrary native atom identity. For this call graph, a four-way classification
(class, id, style or other) can preserve the three exclusion comparisons while
retaining each atom's exact raw hash. Audit every reachable equality use and the
actual borrowed callbacks before accepting that restricted interpretation.
Classifier equality must not imply native equality or equal hashes. General atom
equality would require a separate faithful identity model. This is a proof
boundary finding, not a confirmed Firefox bug.

**Exact vector transitions.** Equal hash lists do not identify complete vector
states. Carry an explicit primitive push relation through the actual insertion
callback and export its actual trace from the provider's public postcondition.
Construct successive Lean vector witnesses using a local library refinement
contract. Each successor must become the next push's predecessor. Apply the
existing trace and recovery theorems to that coherent sequence. Keep
unsafe library semantics and cross-tool interpretation assumptions explicit.

**DOM and resources.** Require the same hash policy throughout the interval from
insertion to pop, including the debug recomputation. Account separately for hash
storage and the element-record stack. Begin with sufficient capacity and normal
return; allocation success and unrestricted growth need later proofs.

### Matcher feasibility gate

First test transport of the real borrowed dynamic callback through a minimal
context retaining associated data and mutable caches. Preserve the existing
rejected reproducer and test incorrect future-state contracts. A transport-only
success does not establish dynamic invocation support: actual callback calls
need their own verifier semantics before proving the production matcher.

A reviewed alternative is to emit an explicit failing safety obligation at an
unsupported runtime callback call, allowing verification only when that call is
proved unreachable. Logical callable queries, trait contracts and casts need
separate admission checks; runtime reachability does not control their logical
axioms. This route has a bounded experiment plan but no qualified tool patch.

If the experiment requires broad verifier changes, retain the minimal failure
and propose that tool work separately. Continue native composition and targeted
bug finding while matching remains blocked.

### First composed result

Start with normal matching of `section > span` in a stable light-DOM snapshot.
Relate the matcher's parent relation to StyleBloom's traversal parent explicitly.
Derive semantic matching through the existing path without the Bloom rejection
check, then prove that the separate rejection check accepts. Using success after
that same check would make the claim circular.

Acceptance requires the actual matcher, enumeration, recovery, collector,
packing and lookup to compose with a real ancestor contribution. List every
remaining primitive, library, resource and tool assumption together. Helper
proofs and a synthetic matching relation do not meet this gate.

### Bug finding and maintenance throughout

Use concrete proof gaps to choose differential checks: empty and long hash
sequences, collisions and saturation, capacity boundaries, ancestor recovery,
and DOM mutations that affect hashes. Classify failures as implementation defects,
missing premises or verifier limitations before changing production code.

For every confirmed Firefox defect, retain a minimized regression that fails
before its fix and passes afterward. Use WPTs for observable web behavior,
crashtests for crashes, and mochitests for Gecko-specific setup. Repeat native
and browser tests when relevant implementation changes justify them.

Keep accepted proofs, experiments and tool limitations distinct. Package source,
tool and dependency fingerprints with reproduction commands, and organize local
commits into production fixes, regressions, proofs and tool support when signing
is available. Signing remains a packaging dependency. All execution stays local.

### Decision gates

Stop a verifier experiment if it requires general borrow-analysis or
representation work beyond its scoped case; preserve the reproducer and propose
that engineering separately. Continue useful differential and regression work.
Broader coverage follows the first composition, and completion estimates follow
the enumeration and matcher feasibility results.

## Baseline

At `44a48f048844`, the runner checks 23 Lean theorems, ten Rust regression tests,
and three differential tests including 27,661,824 comparisons. Two browser
regressions passed three local runs after a native rebuild. These establish
filter arithmetic, valid-history preservation, and conditional ancestor
rejection safety. They do not establish caller hash completeness or cache
lifetime correctness. See [README.md](README.md) for assumptions and reproduction.

## Milestones

| Milestone | Status | Required evidence |
| --- | --- | --- |
| 1. Strengthen differential checking | Complete (`c2c0c4afcc31`) | Adversarial hashes, deeper trees and nested selectors, automatic failure reduction, and instrumentation establishing filter execution. A controlled faulty hash provider must demonstrate that the oracle and reducer detect and retain a real mismatch. |
| 2. Close hash-normalization gap | Complete (`fc3af7e2b69a`) | Checked equivalence of raw and masked hashes for insertion, removal and lookup; a composed history/packing/rejection theorem using raw element hashes. |
| 3. Exercise Gecko state changes | Complete (`700d5df737ab`) | Local browser checks of class/ID/attribute mutation, reparenting, removal/reinsertion, namespaces/case, shadow roots and slot reassignment, with style flushes and independent expectations. Assess feasibility of a test-only filter bypass and document coverage limits. |
| 4. Prove StyleBloom recovery and clearing | Production storage, recovery and concrete provider composition checked in the integrated runner under the existing enumeration contract; conditional enumeration/providers accepted, native recovery composition open | An invariant connecting ancestor path, hash stack, filter contributions and saturation history; valid removals, required-hash retention, and empty state after clearing. Account for siblings, ancestors and separate roots; connect extracted production transitions to the invariant. |
| 5. Verify relative traversal and caching | Complete (`f77c6b0f6042`); combined extraction, 44 declaration audits, and independent review pass | Termination, region coverage and boundary preservation for the production walk; conservative handling of unavailable hashes and correct children/subtree cache reuse under explicit DOM/lifetime assumptions. |
| 6. Prove selector hash collection soundness | Recursive relative and whole ancestor collector contracts checked, plus conditional local-name and ancestor rejection; actual matching-to-region soundness open | A declared selector subset with a production connection: matching implies every collected rejection hash is represented in the appropriate DOM region. Extend through combinators, is/where and relative selectors; enumerate unsupported constructs. |

## Proposed next sequence

Recommendation: finish one production-connected no-false-rejection result for a
small, explicit selector subset, then expand coverage. Milestones 4 and 6 remain
open. The highest-value work is connecting actual DOM hash production and actual
selector matching to the checked filter operations.

### Recommended deliverables, in order

This proposal prioritizes closing the two remaining semantic gaps. The first
complete target is `section > span`, with a real ancestor hash contribution.
Each phase has an evidence gate; broader coverage follows only after composition
succeeds.

| Priority | Deliverable | Completion gate |
| --- | --- | --- |
| 0 | Preserve the current checkpoint | Retain validated tools, source fingerprints and evidence separately from experimental candidates. Working-space cleanup and the upstream retry are complete. Organize validated changes into signed local commits when signing is available. |
| 1 | Prove actual DOM hash enumeration | Extract the unchanged enumeration body with faithful borrowed DOM signatures. Prove the exact ordered hash sequence and both insertion/debug callback behaviors, then replace the whole-enumerator premise in recovery with explicit primitive DOM contracts. |
| 2 | Resolve the matcher extraction boundary | A minimal context round trip preserves dynamic callback lifetimes, mutable-cache restoration and live associated data. Either extract the actual matcher without erasing live fields or retain a precise reproducer and stop this workstream. |
| 3 | Compose one complete matching-to-rejection result | For `section > span`, successful actual matching implies that the ancestor hash is enumerated, retained, collected and accepted by the production filter, under listed DOM/library/resource assumptions. No assumed whole-matcher result or empty hash contribution. |
| 4 | Expand selector coverage and executable regressions | Extend the composed result to descendant combinators, IDs/classes, then supported attributes/namespaces and relative selectors. Every claimed Firefox defect has a minimized case that fails before its fix and passes afterward. |
| 5 | Package the result for continued local use | Fresh extraction and dependency audits reproduce the final claims; independent review checks assumptions; local commits separate tool fixes, production changes and proofs. Repeat runtime checks when production changes and check a second supported platform when available. |

The immediate deliverable is a reproducible capability checkpoint and an actual
callback/state correspondence proof using the qualified Creusot results.
Storage/provider composition already works under an enumeration contract.
Phase 2 has a separate tool
prerequisite and should remain a bounded feasibility investigation until its
minimal gate passes. Phase 3 depends on both. Phase 4 should not become a
substitute for either.
Signing trouble blocks commits, but does not block proof or regression work.

### Recommended next work package

1. Preserve the accepted proofs and tool candidates, and package the remaining
   failures as minimal reproducers with exact commands and expected outcomes.
   Keep experimental candidates separate from the default verification tools.
2. Use the isolated Creusot capability results to establish the actual borrowed
   callback's state correspondence before attempting full enumeration. Keep its
   checked callback-termination restrictions explicit. Existing full-value symbolic
   expansion cannot repair the demonstrated cycle because its required value
   is unavailable in the active backward function. Any future Aeneas correction
   must pass all eight nonrecursive repeated-specialization controls with
   unedited, type-correct Lean and exact callback-state restoration proofs.
   The live recursive-dictionary control must retain its explicit rejection.
3. Only after that gate passes, retry both actual DOM providers and prove their
   final insertion/debug states. Compose the exact enumeration policy with
   recovery to close milestone 4's enumeration obligation.
4. Investigate the matcher context separately, using a minimal lifetime/cache
   round trip before attempting the full matcher. Compose `section > span`
   only after both production connections are established.

If step 2 requires general borrow-analysis development, stop that work package
with its evidence intact and scope verifier engineering separately. Continue
targeted differential bug finding and browser regressions locally. Additional
helper proofs alone do not close either remaining milestone. Do not assign a
completion date to the full proof until these feasibility gates pass.

### Immediate checkpoint: actual enumeration proof

The provider integration is checked: fresh extraction passes 174 theorem audits,
seven tracked tool controls and 25 guard/source-audit tests. The native build,
42 browser checks and four Rust configurations pass. The faithful borrowed DOM
abstraction compiles and has received signature review.

The compatible upstream retry did not resolve enumeration. A subsequent bounded
correction to generic trait-method specialization now passes a strict local gate:

- Ten supported controls compile as unedited generated Lean, including distinct
  lifetimes, outer trait parameters, multiple closure shapes and trait/method
  identity collisions.
- Five unsupported cases reject explicitly. A sixth boundary case retains a
  genuinely live element dictionary and rejects its unsupported recursive
  dependency. It is not counted as a supported case.
- Seven semantic proofs cover exact callback effects, future borrow restoration,
  and the observable borrowed result of an actual trait-method call under an
  explicit primitive finite-enumeration contract.
- All seven existing provider controls pass with the candidate tools. Nine audit
  guard tests pass with Python assertions disabled. Exact source/tool/model/proof
  provenance and dependency audits pass independently.

The original dependency cycle was caused by an inherited, unused element
constraint in closure metadata. Existing unused-clause cleanup removes it while
retaining live callback and receiver dictionaries. A distinct-lifetime control
also required substituting the receiver's outer context before exact argument
reconstruction. The candidate retains the equality check. A separate, reproduced
Aeneas defect dropped the Unit output from ordinary FnMut implementation methods;
a narrow correction passes six reduced controls and five exact callback proofs.
Non-Unit and ordinary FnOnce generated models remain byte-identical to baseline.

Using this isolated tool pair, the unchanged production enumeration body now
extracts with no embedded Charon errors and emits Lean through Aeneas. The
borrowed DOM shim remains unchanged. This is an extraction result, not an
accepted enumeration theorem. The default and integrated recovery tools remain
unchanged.

Six checked helper lemmas now cover the actual atom wrappers, attribute
exclusions and class/attribute callbacks. Their dependency audit lists eight
abstract native interface declarations alongside the logical axioms. The
primitive contracts distinguish atom identity from hash equality and permit
collisions. These results do not yet establish whole-enumerator behavior or the
final state of the actual insertion callback.

The first concrete-provider retry exposed repeated specialization of an already
specialized DOM method. A further experimental candidate composes the recorded
substitutions while retaining receiver, signature and predicate checks. Both
actual insertion/debug roots now extract without embedded Charon errors, but
Aeneas rejects their nested borrowed callbacks during borrow restoration. Seven
of eight required nonrecursive repeated-specialization controls also fail native
translation; only the shared-capture control emits and typechecks. The ninth,
live recursive-dictionary control retains its expected rejection. The strict
acceptance gate therefore rejects this candidate. Its extraction progress does
not justify replacing the accepted tools or claiming either provider proof.

A minimal ordinary-function control reproduces the same borrow-restoration
failure using the accepted specialization candidate, without an element trait
or the repeated-specialization change. This isolates a nested mutable
closure-state translation limitation independently of the new method metadata.

A matched tuple/record experiment narrows this further: both two-reference-layer
controls extract and typecheck as unchanged Lean, while both three-layer
controls fail with the same restoration cycle. These cases contain no closures
or callback traits. Converting closure records to tuples is therefore
insufficient. Typechecking the successful controls is diagnostic evidence, not
a semantic proof of their external operation.

Independent trace review identifies a symbolic value borrowed at abstraction
level 1 and loaned at level 2. Ending level 2 requests level 1; level 1 first
requests its deeper level 2, producing the cycle. A bounded experiment
considered existing nonbranching symbolic expansion before scheduling the
entire abstraction. That approach is now rejected. Sequential diagnostics with
invariant checks establish empty projection histories, no forbidden child
projection and consistent original type metadata. However, the symbolic value
comes from input region 1 while synthesizing backward region 2. That event
introduces no full-value binding in the active backward function, and ordinary
expansion requires precisely that unavailable value. Moving expansion after
the event does not solve the problem. Only logging was changed; no semantic
patch or new model was accepted.

The failure also reproduces with direct assignment and an empty function body
having the same three-layer tuple input. These cases have no extracted calls.
An existing, unmodified compatible upstream Charon/Aeneas pair reproduces the
empty-function failure, independently of this project's tool patches.
Progress within Aeneas requires new projection-restoration and backward-binding
rules or a representation with proved correspondence. Further nested-ADT
translation limitations may remain after that work.

The experimental specialization source now also checks that each cached
predecessor Binder exactly matches the method in its final emitted owner.
A release build and replay of all 25 prior Charon controls preserve every
serialized LLBC field except the verified output filename. The check covers
all 36 generated methods. Eight fault-validation checks also pass: unchanged
baseline and no-fault output agree, and six deliberate signature, predicate,
binder-kind, metadata, name and missing-owner corruptions produce the intended
embedded extraction errors. The first missing-owner fixture failed before
injection and is retained separately, excluded from the successful checks.
The normal source is restored exactly. This guard does not resolve the
nested-borrow failure or make the candidate accepted.

### Alternative-verifier feasibility gate

Evaluate Creusot in an isolated installation before developing general Aeneas
projection/restoration support. Its documented prophecy-based mutable borrows
and closure contracts motivated the qualified local capability checkpoint
recorded below. Pin the source revision, compiler, proof libraries
and solvers; use documentation matching that revision. See
[Creusot mutable borrows](https://guide.creusot.rs/representation_of_types/mutable_borrows.html)
and its [closure support](https://github.com/creusot-rs/creusot/blob/master/CHANGELOG.md).
Verus is lower priority for this case because its
[closure documentation](https://verus-lang.github.io/verus/guide/exec_closures.html)
explicitly excludes mutable captures.

1. Prove observable final state for the triple-reference controls and nested
   FnMut callbacks, including repeated borrowing and preservation of unrelated
   fields. Deliberately incorrect postconditions must fail. Successful parsing
   or verification of an empty postcondition is insufficient.
2. Verify actual enumeration and provider bodies with audited proof annotations
   whose erasure preserves the executable source. Keep the borrowed DOM
   signatures, atom identity/hash distinction, duplicates, ordering and
   exclusion rules. Only the declared primitive interfaces may be assumed.
3. Establish completion under the existing finite-enumeration and resource
   premises. Creusot's default partial-correctness mode is insufficient for
   termination, and its standard-library contracts must be audited for
   omitted capacity/panic conditions. See its
   [termination guide](https://guide.creusot.rs/termination.html) and
   [check attribute documentation](https://doc.creusot.rs/creusot_std/macros/attr.check.html).
4. Define and check the cross-verifier specification bridge before investing
   in the full provider proof. It must align ordered hash events, final storage
   contents and counts, debug output, resource premises, and future-borrow
   restoration. A borrow's prophecy is not necessarily its value immediately
   after a function returns.

This gate does not replace the existing Lean claims. Adding a Lean axiom that
asserts an external verifier's conclusion would leave a new trust boundary.
A jointly verified result must explicitly identify the additional translation,
solver and specification-bridge assumptions; a claim of complete Lean checking
requires proof replay or import. No toy result or unchecked bridge closes
milestone 4, and the actual matcher obligation in milestone 6 remains separate.

#### Local capability checkpoint

The isolated Creusot v0.14.0 experiment is pinned to revision
`65349025c67e69fcd7479f1f420fa5904f69bc27`, with its specified Rust nightly,
Why3 revision and Z3 version. Original compiler/backend sources are unchanged.
All five nested-reference controls prove their helper and observer obligations:
no-op, assignment, later writes through a surviving borrow, repeated borrowing,
and preservation of an unrelated field. Termination and annotation-erasure
checks are enabled.

Two further callback controls prove with explicit qualifications. Nested
forwarding requires the checked `FnGhost` bound; repeated forwarding additionally
uses two checked adapter closures and an explicit `FnMut::call_mut` invocation.
The wrapper's standard-library contracts and compiler handling are part of the
trusted toolchain. These results do not resolve the original arbitrary-`FnMut`
termination rejection or the missing marker for a direct mutable reference to
the wrapper.

Across 36 emitted models, 73 verification conditions are valid. Seven deliberately
false observer postconditions time out after five seconds; their other conditions
are valid. This establishes nonacceptance of those false claims within the test
budget, not solver-generated counterexamples. The original seven-pair capability
gate therefore remains qualified, rather than passing unchanged. Evidence and
independent reviews are retained under `artifacts/stylo-bloom-tools/creusot-gate/`.

The next bounded obligation is the actual borrowed insertion callback's state
transition and its interpretation at the existing provider boundary. Establish
that connection before investing in full DOM enumeration. The existing
`Enumeration` premise equates all results for every initial sink; a successful
postcondition under capacity bounds cannot silently replace it. A joint proof
may instead derive the existing `ProviderModel` obligations, but must establish
their successful-call traces and arbitrary-future restoration correspondence.
Joint verification can meet the semantic milestone with an explicit trusted
toolchain and sound composition argument. The existing Lean checkpoint remains
conditional until its premise is discharged within Lean.

### Production enumeration completion gates

Proceed through these remaining gates, adapting extraction and dependency
audits to the accepted verifier while retaining the same semantic obligations:

1. Preserve the completed independent audit of the emitted declarations: opaque native atom
   primitives, transparent atom wrappers, exclusion helper, both callback bodies,
   and the unchanged enumeration body. Check the added DOM method declarations
   and their native-operation correspondence obligations.
2. Extract both actual provider callback instantiations, preserving insertion
   and debug behavior. Check these before relying on a generic theorem whose
   callback state is consumed at the return boundary.
3. Extend the checked atom interfaces with reviewed contracts for ordered
   class/attribute iteration. Connect original and specialized DOM methods to
   the same native operation. Compile generated Lean unchanged and audit every
   external dependency. Atom identity must remain distinct from hash equality,
   including collisions.
4. Prove the exact ordered hash policy, duplicates, optional ID handling and
   class/ID/style attribute exclusions. Establish both actual callback traces,
   then compose them with recovery. Do not assume the whole enumeration result
   as a primitive contract.

**Decision rule:** pursue a correction only while it remains narrow enough to
review against these controls. If a further boundary requires general recursive
dictionary or borrow-analysis development, preserve the reproducer and
conditional results, leave milestone 4 open, and package the existing work.
Treat broader verifier engineering as a separate proposed project with its own
scope.

### Subsequent priorities and dependencies

The actual matcher remains a separate feasibility gate. Its context includes a
live dynamic callback, mutable caches and associated data; existing extraction
cannot preserve all required loans. Resume that work only with a concrete plan
for a minimal context round trip that retains those constraints. An opaque
rendering token or removal of live fields cannot establish the required result.

Once both enumeration and matcher gates pass, compose the first complete result
for `section > span`: a successful actual match supplies a real ancestor hash,
actual enumeration emits it, recovery retains it, collection requests it and the
production filter accepts it. Record the nonzero contribution explicitly. Then
extend to descendants, IDs/classes, supported attributes/namespaces and relative
selectors, one supported family at a time.

Bug finding can continue independently of either extraction gate. Prioritize
concrete counterexamples involving hash production, case/namespace handling,
mutation epochs, recovery boundaries and saturation. Feed them through the
existing differential harness and reducer. Use WPT for observable matching/style
failures, crashtests for crashes, and mochitests when Gecko-specific setup is
required. Every claimed Firefox defect needs a minimized failure before its fix
and success afterward; a tool failure is not itself a Firefox defect.

At either a completed proof or a bounded tool limitation, produce a reviewable
checkpoint: reproducible evidence, an explicit assumptions/coverage report, and
local commits separating tool fixes, production changes and proofs when signing
is available. Repeat runtime checks when production changes. This packaging step
does not depend on completing milestones 4 and 6. All work remains local; no Try
push or patch submission is part of this proposal.

### Current checkpoint

- The recovery shim now preserves production's shared parent receiver,
  `traversal_parent(&self) -> Option<Self>`. Fresh extraction and all 174 proofs
  pass without theorem edits, as do twelve source-audit and thirteen provider
  guard tests. The prior evidence is retained. This removes an avoidable
  by-value receiver abstraction; native DOM correspondence remains a contract.
- The default pipeline checks 117 declarations: 115 theorems and two witness
  definitions. Its 73 core theorems use only standard logical axioms.
- Fresh integrated recovery extraction passes those 73 core theorems, 83 adapter
  theorems, 17 concrete provider theorems and one preserved-baseline equivalence
  theorem. Seven tracked native tool controls and 25 guard/source-audit tests
  pass. Actual storage operations and every recovery branch preserve the
  ancestor invariant under explicit enumeration, library, DOM and resource
  contracts.
- Fresh relative and matching collection runs pass 19 and 23 dependency audits.
  These cover recursive collection, termination, preserved array contents, zero
  padding and an actual local-name helper bridge. Full matcher semantics and
  Gecko hash alignment remain open.
- The fresh combined rejection runner passes 64 exact dependency audits and ten
  negative tests, composing local-name collection with Bloom packing and
  rejection under explicit matching, hash-alignment and history premises.
- The ancestor collector now extracts after a reviewed borrowing-helper refactor.
  Its fresh runner passes 49 audits and nine boundary tests. These cover iterator
  behavior and the whole recursive collector's termination, required-hash prefix,
  array frame and zero padding under explicit finite-depth component policies.
  Successful actual matching still needs to establish those policies.
- Fresh ancestor collection, packing and rejection composition passes 90 exact
  audits. The existing local-name composition still passes 64 after extracting
  the shared packing lemmas; seventeen tests check both combined runners' guards.
- The current storage and ancestor refactors pass four Rust configurations,
  differential checks, a native build and five browser tests repeated three
  times: 42 checks with no unexpected results. Signed local commits remain
  pending after the signing helper failed.

### 1. Preserve a reproducible local checkpoint

The combined rejection runner and its negative audit/freshness tests now pass,
with independent review of the composed theorem and its assumptions. Keep both
models regenerated from current source, compile their dependencies from source,
and record exact source, tool, model and theorem provenance. Preserve the original
default verifier alongside experimental native tools.

Organize the validated work into reviewable signed local commits: tool fixes and
reproducers, production storage extraction and proofs, and collection/matching
proofs. Resume commits when signing is available.

**Exit criterion:** a fresh invocation reproduces the reviewed local-name
collection-to-rejection result, rejects stale or unexpected proof evidence, and
clearly labels its matching and hash-alignment premises. Signing trouble may
block committing; it does not block verification work.

### 2. Close the actual DOM hash-provider gap (milestone 4)

Prove that the actual provider callback executes the finite insertion trace:
every emitted hash is inserted, appended and counted exactly once. Establish
completion under explicit allocation and resource bounds, and correspondence
with debug enumeration. Then connect the enumeration implementation to the
provider contract used by the recovery proof.

The initial tool obstacle was a closure capturing mutable state that itself
contains mutable references. The broad experimental Charon change regressed
shared captures and closures with unused lifetimes, so it was rejected. The
accepted candidate corrects the closure lifetime metadata, with controls for no
capture, shared capture, mutable capture, nested borrows and combined extraction.

A capture-specific metadata candidate now passes those controls in isolation;
its tools remain experimental. An isolated correction to Aeneas's custom Lean
elaborator also lets the proposed borrowed provider compile. Four reviewed
equivalence proofs preserve the original insertion results, mutation order and
borrow restoration. Six further artifact proofs check insertion-trace and debug
enumeration correspondence under explicit enumeration and library contracts.
The isolated runner now passes independent fresh regeneration, ten exact theorem
audits and thirteen audit tests. It checks source/tool fingerprints, embedded
source text, the patched Lean import inventory and compiled companion files, and
rejects unexpected axiom-bearing or axiom-free reports.

A fresh combined prototype now checks all 73 core and 83 adapter theorems plus
17 provider theorems. These establish actual callback traces, completion under
count/capacity/allocation bounds, the concrete provider dictionary contract, and
hash retention after actual rebuild and recovery. Both enumeration callbacks must
emit the same finite list for an element. A smaller proposal removes the unused
original insertion method and makes verification call the actual borrowed-view
operations. Independent review has passed, including an exact equivalence proof
covering failure, divergence and future borrow restoration. Its fresh combined
174-declaration gate passes, and the production files now match that verified
candidate exactly. The native build, five browser tests repeated three times
(42 checks), and ten Rust regressions in each of four configurations pass.
The official recovery runner now reproduces all 174 proofs and seven tracked
native controls; 25 guard/source-audit tests pass. Its Lean override is rebuilt
from the tracked patch and pinned original backend for every run. Preserve the
old Rust and generated proof baselines so equivalence checks cannot silently
compare the new code with itself.

An earlier separate gate included the actual element-hash enumeration body:
callbacks passed through generic trait methods produced an invalid specialized
trait reference. A six-line reproducer fails in both partial-specialization modes,
while the corresponding ordinary generic-function control passes. Reject
extraction output with its error flag set even when the tool exits successfully.

A further artifact gate keeps the production enumeration body unchanged and
models primitive class/attribute callbacks as loops over raw DOM value lists.
This would replace the whole-enumerator assumption with smaller primitive DOM
contracts covering order, duplicates, failures and snapshot stability. Partial
specialization still produces invalid callback trait references. Full
monomorphization produces valid LLBC but fails Aeneas region-hierarchy analysis
on the callback loop signature. No enumeration proof is accepted from this gate.

#### Upstream retry before broader tool development

A read-only upstream check on October 16 found relevant newer work. The
[Aeneas October 16 nightly](https://github.com/AeneasVerif/aeneas/releases/tag/nightly-2026.10.16-d95aeac)
uses commit `d95aeacab40f33e99e30c30955e36c072c5baf3a` and
[pins Charon `08d7c9d50144bd84848212c24701253585e90d1f`](https://github.com/AeneasVerif/aeneas/blob/d95aeacab40f33e99e30c30955e36c072c5baf3a/charon-pin).
Aeneas adds [static-region support](https://github.com/AeneasVerif/aeneas/pull/1438),
and Charon has new [higher-ranked clause handling](https://github.com/AeneasVerif/charon/pull/1531).
These changes are relevant candidates, not verified fixes for our failures.

Retry the minimal generic-callback case first with that compatible pair and
Lean 4.35.0, initially unmodified. Keep the existing tool snapshots and proof
evidence. Charon's [type-checker exception for mixed specialization](https://github.com/AeneasVerif/charon/pull/1490)
means a clean error flag alone cannot establish that the callback reference is
correct. Inspect the exact trait declaration, implementation, call target,
substitutions, bound regions and output type. Require retained callback bodies,
unchanged generated Lean typechecking, and a minimal invocation/state-restoration
proof before retrying actual enumeration. The partial-specialization pass itself
was unchanged in the inspected upstream version, so success is uncertain.

The unmodified pair now builds successfully after supplying the existing Rust
sysroot's LLVM library search path. Both partial-specialization modes emit LLBC
without an error flag and generate Lean, but independent inspection finds
incompatible callback dictionaries: a method returning updated captured state
is assigned to an ordinary `FnOnce` interface expecting `Unit`, and the `FnMut`
restoration shape also disagrees. The ordinary generic-function control has the
same mismatch. The captured mutable reference is still marked with unknown
lifetime mutability, so the previously failing specialization path was not
exercised. These generated models are not accepted proofs or evidence that the
original trait-specialization defect is fixed. The retained concrete
full-monomorphization diagnostic still fails region-hierarchy analysis.
The three existing closure-lifetime and specialized-function corrections apply
unchanged and both candidate tools build. They restore the original trait-method
specialization error in both partial modes; those LLBC outputs are rejected.
The concrete full-monomorphization route still fails region analysis. All seven
control LLBC files are error-free, but only four emit Lean; three need prior
naming prerequisites, and the ordinary function case needs a prior binder
correction. No new Lean result is accepted and no default tool is replaced.
Further prerequisite migration cannot fix either target failure, so this retry
stops here.

The subsequent bounded candidate handles abstract generic trait methods with
no extracted implementations, retaining original declarations and auditing each
specialized call. Its narrow acceptance gate and actual enumeration extraction
are recorded in the immediate checkpoint. General support would still need to
handle every concrete/default implementation and every call/dictionary. Alternatively, full monomorphization must preserve the distinct
lifetime binders and substitutions currently erased from callback signatures.
Suppressing consistency checks or ignoring region edges cannot satisfy either
obligation. Evaluate any proposed representation refinement against the actual
borrowed DOM interfaces and unchanged enumeration policy before pursuing it.

This retry does not resolve milestone 6: the inspected latest Aeneas still skips
dynamic-object regions and rejects live associated-data region arguments;
[associated-type support remains open](https://github.com/AeneasVerif/aeneas/issues/1112).

**Exit criterion:** actual provider code discharges its trace and completion
obligations in the production recovery theorem, and the actual enumeration body
establishes the emitted-hash list under explicit primitive DOM/container
contracts. Assuming an opaque enumeration function equals a finite callback fold
does not discharge the enumeration-body obligation. Any remaining container,
DOM, allocation or lifetime assumptions are enumerated explicitly.

**Stopping point:** if a narrow tool correction cannot pass the controls, retain
the minimized failure and conditional theorem, keep milestone 4 open, and advance
independent collection work. Do not spend an unbounded phase modifying the verifier.

### 3. Connect actual matching to local-name rejection (milestone 6)

Replace the current conjunction of local-name helper results with a result about
actual successful compound matching for a declared subset. Establish that the
Gecko element hash provider includes the corresponding local-name hashes,
including the relevant case and namespace behavior. Compose matching, collection,
packing and filter lookup in one checked result.

Choose a subset with an actual region contribution, such as a local-name child
or descendant selector (`section > span` or `section span`), or direct-child
`:has()`. A lone subject local name can produce an empty ancestor hash list;
that vacuous case does not meet this milestone. Record a supported instance with
a nonzero collected rejection hash and a matching DOM region.

A fresh extraction gate preserves the unchanged production matcher and all
18 real context fields, including mutable selector caches and live associated
data. Charon produces valid LLBC; Aeneas rejects the dynamic callback type in
`pseudo_element_matching_fn`. The existing unused-type eraser correctly refuses
the live associated-data projection. Six reduced diagnostic controls typecheck
in Lean, but do not establish matcher correctness. Supporting the real callback
representation and its context loans is the next extraction obligation; do not
erase live context fields to bypass it.

A bounded review considered carrying the shared dynamic callback as an opaque
logical token while preserving the original LLBC, context fields, mutable-cache
restoration, associated data, and reference/object lifetime constraints. Native
source inspection found that dynamic-object region analysis is currently skipped;
the live associated-data region arguments also independently exceed supported
signature translation. Independent review agreed that a rendering-only token
patch cannot meet the required loan semantics, so no candidate was accepted.

The missing enabling work is loan-aware dynamic-callback and associated-data
support, or an independently justified representation refinement. Any future
context round-trip gate must preserve all these constraints before retrying the
unchanged matcher. The selector proof must establish callback independence for
arbitrary presence and value, including indirect context operations. Unsupported
calls in retained branches may still block extraction; pruning those branches
based on the intended subset does not establish correctness. This exceeds the
bounded refactor/tool-patch phase; keep milestone 6 open.

**Exit criterion:** for the declared subset and stated DOM/resource assumptions,
a real successful match cannot be rejected by the production filter. The result
must identify the actual matching and enumeration code it covers.

### 4. Extend coverage through selector and DOM regions

Add IDs and classes, then supported attribute and namespace cases. Connect
combinators and singleton `:is()`/`:where()` matching to the appropriate ancestor
or relative region. Reuse the checked relative traversal/cache result, preserving
its stable-DOM and cache-epoch premises.

The ancestor outer-loop extraction failure is resolved by a reviewed production
refactor: a borrowing helper completes the subject scan before the final ancestor
collector takes ownership of the iterator. Whole-collector termination,
required-hash inclusion, preserved array contents and packing/rejection
composition are now checked under the explicit component policies. Discharge
these policies from actual matching next. Keep the supported selector subset
and remaining assumptions explicit after each extension.

**Exit criterion:** each added selector family has a matching-to-region inclusion
proof composed with actual collection and rejection. Unsupported constructs
remain listed; collection invariants alone do not complete milestone 6.

### 5. Turn failed obligations into executable bug checks

Throughout steps 2–4, classify failures as implementation defects, missing
preconditions or verifier limitations. Feed concrete candidate counterexamples
into the differential harness and reducer. Prioritize mismatched hash production,
case/namespace handling, mutation epochs, recovery boundaries and saturation.

For each confirmed Firefox defect, retain a minimized case that fails before the
fix and passes afterward. Add a WPT for observable matching or style behavior,
a crashtest for a crash, or a mochitest when Gecko-specific setup is needed.

**Exit criterion:** every claimed defect has an executable regression case.
Finding a new bug is a possible outcome, not a completion requirement for a proof.

### 6. Prepare the project for continued use and review

Regenerate all models from the final source and run exact dependency audits,
Rust regressions and the differential corpus. Repeat the native build and browser
checks after further production changes. Independently review proof assumptions
and runtime semantics. Record which guarantees are extracted-code proofs,
conditional contracts, bounded exploration and browser evidence.

Once milestones 4 and 6 meet their stated scope, prioritize reproducibility on a
second supported platform and reducing experimental tool patches. Broader
selector grammar and a browser filter-disable switch follow unless a concrete
counterexample requires them earlier.

**Exit criterion:** a reproducible, reviewable local commit stack and a concise
coverage/assumption report. A minimized tool limitation leaves the affected
milestone open. Work remains local; no Try push or patch submission.

## Review and revision log

- Initial execution: milestones 1 and 3 use independent implementation agents;
  the main agent works on milestone 2. A separate reviewer audits the six-part
  plan and the extraction boundaries for milestones 4–6.
- Plan review: the existing counter relation permits stale saturated slots even
  when the live multiset is empty. Milestone 4 therefore needs a stronger
  exactness invariant under the historical stack bound, not merely the existing
  no-false-negative relation.
- Plan review: distinguish selector-DOM parent/child links from StyleBloom's
  traversal-parent relation. Relative cache proofs require stable DOM contents
  and element identities within a cache epoch. Browser mutations must test new
  style/query epochs rather than assume that retained maps tolerate mutation.
- Keep mathematical models, extracted Rust guarantees, bounded exploration and
  browser evidence distinct. A model proof alone does not complete a production
  proof requirement.
- For each defect, retain a minimized reproducer and demonstrate failure before
  the fix and success afterward. Commit changes in independently reviewable pieces.

## Evidence recorded during implementation

- Milestone 2: thirteen additional theorems pass in the full extraction pipeline,
  for 36 audited theorems total. Exact Result equalities cover insert/remove/
  lookup masking for all states, history normalization preserves raw-hash
  histories, and packing/rejection composition accepts a live collected prefix
  with zero padding (including lengths zero through four). No new external axiom
  was allowed. Independent contract review found no blocking issue; the committed theorem
  covers every planned collection length.

- Milestone 1: the expanded harness adds five hash profiles and 24-node chain,
  branching and multi-root shapes, including nested selectors through depth 16.
  The release corpus comprises 33,450,624 comparisons. Controlled omitted-class
  hashing proves reduction preserves ancestor and warmed-cache relative failures.
  Independent review required counting successful hash collection separately
  from disabled baseline attempts and preserving class/ID attribute consistency;
  both changes are implemented and covered by passing debug/release checks.
- Milestone 3: three new WPTs exercise dynamic DOM, shadow/slot, and quirks-mode
  cases. Three local repetitions passed all 33 checks. A production bypass would
  require plumbing through both ancestor and relative matching; it is deferred.
  Computed-style checks establish observable behavior, not internal hit counts.
- Milestone 4 extraction gate: Charon extracts the caller adapter, but Aeneas
  fails on the hash-producing closure and AtomicRefMut operations. The actual
  high-water and clear operations now live in a shared production helper that
  extracts successfully. Full recovery remains required and is being investigated.
- Milestone 5 extraction gate: the pinned Aeneas cannot translate an outer-loop
  break inside the nested subtree walk. Splitting the existing successor walk
  into a production helper permits extraction. Replacing the cache closure with
  explicit occupied/vacant entry branches also permits extraction of the caller.
  Hashbrown map entry operations still require an explicit library contract.
  The traversal, entry-update, cache-epoch, and concrete Bloom bridge proofs now
  pass in the combined pipeline and have received independent review.

- Milestone 5 integration: the full runner passes 110 declaration audits
  (108 theorems and two concrete witness definitions), ten Rust regressions,
  and eight differential checks covering 33,450,624 comparisons. The matching
  production snapshot passed a native build and all five browser tests for
  three repetitions (42 checks). The relative audit rejects unexpected axioms
  and missing or duplicate reports; injected negative cases verify rejection.
  On case-insensitive filesystems, the main Lean directory must precede the
  relative directory to avoid its log directory shadowing generated modules.

- Clear-proof review identified an adapter obligation: production pushes append
  to the hash stack while logical insertion histories prepend. A permutation or
  reversal argument must connect the actual stack to the history before applying
  the clear theorem. This was resolved by making HighWaterHistory append in
  production order and proving that optimized clearing establishes a fresh
  empty/high-water-zero history. Thirteen caller-clear theorems now pass in the
  main runner, bringing its total to 49. The recovery and adapter obligations
  remain open.

- Recovery review found that an unconditional push contract could not describe
  the production containers. The checked contract now requires finite capacity
  and parent/root admissibility. Both recovery configurations pass under those
  conditions; production adapter extraction and hash-resource bounds remain
  required. Generated panic-message code introduced native evaluation axioms;
  equivalent explicit checks removed those dependencies instead of allowing them.

- Four additional storage-history lemmas connect append-order high-water
  histories to saturated-counter coverage and successful lookup at arbitrary
  historical maxima. They also establish the exact list and maximum after a
  batch of actual insertions. Independent review and the full pipeline pass:
  70 core theorems plus 44 relative declarations, or 114 audited declarations.
  Production storage/provider methods still need to establish these histories;
  milestone 4 remains open.

- The actual debug zero-check now uses an equivalent early-exit loop. Three
  checked theorems establish termination, the exact 4096-counter zero predicate,
  and success on a zero filter. The combined pipeline passes 117 declaration
  audits; all 73 core theorems now require only standard logical axioms. The
  relative audit also removes every iterator-external allowance. This closes
  the old unused-iterator maintenance item and supplies the zero-check fact
  required by the production storage adapter's debug assertion. A fresh native
  build including the collector iterator refactor (`ceaef3161627`) passes all
  five browser tests for three repetitions: 42 checks, no unexpected results.

- Milestone 6 checkpoint: the isolated helper runner regenerates production
  extraction, records source/model hashes, checks a generic exact policy
  theorem, and audits its dependencies. The theorem covers arbitrary atom
  types and policy/hash providers, not the mock implementation's concrete
  attribute rule. It does not establish matching-to-region inclusion or the
  recursive collector. Minimal tool reproducers distinguish naming, built-in
  representation, associated-type, and recursive-iterator gates. The default
  117-declaration verifier continues to use the original pinned tools.

- Production storage port: independent review found no runtime semantic blocker.
  The shared storage borrows the existing filter and buffers; insertion counts,
  mutation order, debug enumeration, and clear behavior are preserved. Debug and
  release Rust tests pass with and without the Gecko feature, as do the default
  117-declaration verifier, a native build, and all five WPTs repeated three times
  (42 checks, no unexpected results). These checks cover the pending refactor;
  its production adapter invariant and provider/container contracts remain open.

- Relative collection integration: fresh production extraction and Lean checking
  pass with four theorems (iterator initialization, step, exhaustion, and simple
  component equivalence) and three dependency-audited collector definitions.
  Thirteen boundary/freshness tests, including negative cases, pass. The runner checks the exact
  opaque method, external signatures, and representation source hashes. The
  immutable Arc/list representation contract and full matching-to-region theorem
  remain open obligations.

- Combined recovery extraction now preserves core names and checks all 73 core
  theorems unchanged in the same model as production storage. Six new
  hash-insertion lemmas prove successful finite-call accounting and history
  composition under explicit SmallVec semantics. Six pending-operation lemmas
  check exact forward/restoration behavior, and three clear lemmas establish
  empty filter/buffers, high-water zero, identity back, and restored history. Actual provider/closure
  correspondence and full storage contracts remain open. A minimized ordinary
  generic function with a loop reproduces the native specialization naming
  collision before its narrow naming correction and generates type-correct Lean
  afterward.

- Production operation checkpoint: fresh combined extraction checks all 73 core
  theorems and 30 adapter theorems, including queries, push, and terminating pop.
  Twelve source/proof audit tests pass. Seven further checked resource and
  invariant theorems connect the element records to the concatenated hash stack,
  preserve that relation through actual storage operations, and establish finite
  insertion traces under explicit count, hash-stack, and allocation bounds.
  These do not establish that the actual DOM provider executes such a trace.
  Generic-to-specialized recovery composition and provider extraction remain open.

- Rebuild composition: the production forward adapter satisfies the generic
  recovery contract under explicit, coherent library and provider assumptions.
  Separate proofs relate the actual generic and specialized rebuild loops,
  including accumulated restoration functions. Their composition establishes
  exact ancestor contents, empty pending state, validity, and lookup of each
  ancestor hash after actual rebuild. Fresh regeneration checks all 73 core and
  72 adapter theorems, with exact dependency audits and twelve audit tests.
  Targeted source and Python lint checks pass. Recovery's other
  loops and the actual provider boundary remain open.

- Collection progress: fresh relative extraction passes fourteen exact audits
  covering recursive collector invariants and dependencies. Matching extraction
  passes eighteen audits, adding the actual local-name helper and compound
  composition under explicit atom/hash alignment contracts. Thirteen relative
  and eight matching boundary tests pass. The compound premise is a conjunction
  of actual local-name helper results, not a full matcher theorem; broader
  selector semantics, Gecko provider alignment, and ancestor collection remain
  open.

- Full recovery composition: eight simulation theorems cover the actual trimming,
  target-ascent, common-ancestor, and duplicated/flush paths. Three production
  composition theorems instantiate the method relations and establish actual
  ancestor contents and hash retention in both recovery configurations. Fresh combined regeneration passes all 73 core and 83
  adapter theorems with exact dependency audits. The DOM provider contract remains open; the result retains explicit
  forest, equality, exact-depth, capacity, and root-admissibility premises.

- Collector frame checkpoint: the actual recursive collector preserves the
  existing prefix and every slot at or beyond the returned length. Its
  zero-initialized wrapper therefore retains zero padding, including through
  singleton recursion and early fullness. Fresh relative/matching runs pass
  nineteen/twenty-three exact audits and their thirteen/eight boundary tests.
  Connecting this result to packing and rejection is the next composition step.

- Rejection composition checkpoint: fresh core and matching models compile together
  from source, with 64 exact audits and ten negative tests. The result composes
  actual local-name helper matches, collection, masking, zero padding, packing
  and Bloom rejection. Actual full matching and Gecko hash alignment remain
  explicit open obligations.

- Ancestor extraction checkpoint: identical isolated baseline/candidate tools
  reproduce the original outer-loop failure and successfully extract the
  borrowing-helper refactor. Independent review found its control flow and
  mutations equivalent. Fresh production extraction passes 33 exact audits,
  including ten iterator theorems with only standard logical axioms. They prove
  skip termination, bounds, first-stop behavior and exact next-item transitions.
  Nine negative boundary tests pass. The generic wrapper avoids the concrete
  fixture's debug dependency. After the source refactor, fresh relative, matching
  and combined rejection runs pass 19, 23 and 64 audits; all 40 boundary tests
  pass. Rust configurations, differential checks, a native build and all five
  browser tests repeated three times pass (42 checks, no unexpected results).
  The initial browser attempt used an occupied port; an isolated-port rerun
  exercised all assertions successfully. Whole ancestor collector and matching
  soundness remain open.

- Whole ancestor collector checkpoint: sixteen further audited theorems compose
  exact iterator progress, subject scanning, phase transitions, recursive
  singleton collection and array preservation. Fresh extraction passes 49 audits
  and nine boundary tests. Independent review confirms that the finite-depth
  policies contain no collector postcondition; the wrapper establishes required
  prefix hashes and zero padding. Actual successful matching must still imply
  those policies. The current source and model fingerprints match the evidence.

- Actual compound-matcher feasibility gate: Charon accepts the original matcher
  with opaque simple matching and context interfaces, but Aeneas rejects a
  closure containing nested mutable borrows. An isolated move-capture variant
  passes that type boundary and then fails on nested borrows in the quirks-data
  branch. Moving that branch into a helper still fails during loan restoration.
  All three Charon outputs report `has_errors=false`. A related eight-line
  closure control fails with a borrowed context and Lean-checks with a moved
  context, but does not resolve the full matcher. No production matcher change
  or proof result is accepted from these experiments; preserve the failures
  while independent provider and rejection composition work continues.

- Ancestor rejection composition: the fresh isolated model checks 90 exact
  dependencies across the core filter, ancestor collector and packing bridge.
  The final theorem uses the actual ancestor wrapper, packing and lookup under
  `FullGood` and `ValidHistory`. The four shared packing theorem bodies are
  unchanged, independently compared with the retained original. Fresh local-name
  composition retains all 64 audits; seventeen combined-runner guard tests pass.
  Actual successful matching and DOM enumeration remain open, so milestone 6 is
  not complete.

## Maintenance

The unused iterator external dependency has been removed. Check another
supported platform when one is available. Preserve exact theorem/axiom auditing
and reproducible tool versions throughout all six milestones.
