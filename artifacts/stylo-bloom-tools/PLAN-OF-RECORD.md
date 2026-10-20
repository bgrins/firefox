# CSS and Stylo verification plan

Updated 19 October 2026. Work stays local; the user owns pushing.

## Current status

- **85 committed native/WPT fixes.** The management index is
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md); exact commits, standalone alternatives
  and limits are in [CURRENT-COMMITS.json](CURRENT-COMMITS.json).
- **Latest fixes:** leading-whitespace attribute origin (`ad608a212bd8`),
  trailing-whitespace token metadata (`bccea9c1fffc`) and escaped trailing
  whitespace (`fff2d758ef6b`). Each has a preceding evidence companion and
  a separate two-file native/WPT commit.
- URL native state/capture, ordinary batching, parser-priority winners, animation
  identity and primary parser-history admission are accepted within scope. Public
  parser wrappers and storage composition remain active.
- **Committed token-boundary repair:** registered-value token boundaries. The corrected 37-case
  baseline has 27 PASS / 10 FAIL across fonts, margins and token serialization.
  The repaired build passes 308 cases across 18 WPT files. Native/WPT review and
  standalone source packaging and bounded proof review pass. It is committed with its preceding evidence companion.
- **Committed animation repair:** animation publication converts guaranteed-invalid values to
  registered initial values. The three-file repair fixes ten reproduced failures;
  the 343-check matrix has 341 passes and two unchanged expected failures. Six
  added lower-priority suppression/valid-empty controls also pass. Independent
  native/WPT review, lint and standalone source packaging pass, with root replay.
  Root and independent review accept the v2 bounded Lean companion: 81 audits,
  including 42 new results, plus 14 independent boundary challenges. Separate signed
  evidence/native commits are complete.
- **Whitespace repairs committed:** the leading-origin bounds panic also
  reproduces without script in installed Firefox 158. Its 26 new tests pass;
  the accepted origin proof has 88 audits. Trailing token metadata repairs
  28 failures in a 40-case WPT. Escaped whitespace repairs 16 failures in a
  20-case WPT. Their shared terminal-span proof has 37 audits and 23 independent
  challenges. Tokenizer, EOF, native correspondence and caller premises remain
  explicit; these are bounded components, not complete serialization proofs.
- **New serialization candidate:** retain required newline whitespace after an
  actual backslash delimiter. Native review passes; final WPT has 30 passes,
  against a baseline subset with 16 failures and 14 passes. All 435 preceding
  outcomes remain unchanged in the earlier combined matrix. The bounded Lean
  extension is active; this candidate is excluded from the committed count.
- **Attribute-taint follow-up:** both bounded reviews are complete. Actual
  prohibited local image requests remain established for fix80; no new unknown
  value disclosure was found. Thirty-six calibrated registration observations
  preserve raw-string taint. Link-parameter provenance loss is source-confirmed,
  but current transport/resource restrictions block the proposed HTTP path.
  Epoch-aware provenance and link-env provider contracts remain open.
- **Anonymous-box provider:** root accepts the bounded 42-audit component after
  fresh replay and source review, with six model mutants and 50 passing browser
  states. Actual reflow-input/frame ancestry, numeric providers and dynamic
  reconstruction remain open. Completed root compiler outputs were removed.
- **Parser controls:** the earlier seven wrapper results remain accepted.
  Nested-control v3 now has independent scoped acceptance: 39 audits, 59 modules,
  18 cases and 91 native/model snapshots in debug and release. Three native
  mutants differ in 10, 25 and five rows. Root integration review is pending.
  The revised capsule rejects pre-import shadowing and nonclosed file rosters.
  Universal callback grammar, native termination, full LinkParameters and
  whole-program annotation correspondence remain open.
- The [triage proposal](../css-bugfix-triage-20261019/README.md) groups the first 80
  committed fixes with exposure limits and standalone alternatives. A separate
  registered-animation WPT calibration correction is committed separately;
  it does not increase the native-fix count.
- Signing resumed successfully. The coverage plan, two evidence/fix pairs and
  calibration evidence/test pair are committed. Signing stays enabled.
  Nothing has been pushed or submitted externally.

[Historical checkpoints](PLAN-HISTORY-20261019.md) preserve the previous plan
verbatim. Their counts, signing blockers, agent states and “next” sections are
historical observations. The current schedule is below; historical open proof
obligations remain open unless a later acceptance record explicitly closes them.

## In progress

### 1. Ordinary batching accepted; compose public operations

The indexed ordinary algorithm is accepted under explicit source/comparator/
storage premises. It composes initial planning, sorted descending removals,
ascending count/rank correction and source-order execution with separate raw
storage. Source uniqueness and mapping uniformity are proved by the optional
publication shape under the inspected metadata contract. Native parser lowering,
callback readiness, sort/container/compiler and value abstraction remain open.

The component has 172 audits (109 newly authored), 18 extracted-native
transactions per original/candidate variant and five distinguished compiled
mutations. Independent manifest-only relocated replay, complete proof/source
review and separate outcome checks passed. A supplied comparator allows false
negatives, preserving the NaN audit's distinction between publication and changed
serialization. No additional browser bug was found.

[Scoped acceptance](../css-declaration-batch-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
Next join this accepted component to legal mixed public operation histories and
actual caller readiness. A separate declarative parser-winner proof is accepted in
`../css-declaration-parse-winner-proof-v1/`: last important occurrence, otherwise
last occurrence, retained in original source order. Its producer is frozen with
46 new universal lemmas and nine kernel examples; independent fresh relocated
replay and complete proof review passed. It also characterizes push/extend return flags without equating a true
flag to a different final serialization. No new native execution is claimed.
[Scoped acceptance](../css-declaration-parse-winner-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

### 2. URL state accepted; continue public parser histories

The v2 state/capture component is accepted after independent model/source review,
fresh complete replay, root authentication and ordered-trace rechecking. It has
51 modules / 388 reports (17 new / 107), actual cssparser builds in three modes,
59 cases and 503 input-derived ordered events. It derives mutable metadata and
original-source capture; codec, machine headroom, allocation/compiler and public
history premises remain explicit.

V1's trace validator accepted five malformed traces. The sealed negative review
remains valid; v2 rejects those exact traces and 3,043 corruption checks. No Lean
theorem was refuted and no new browser bug was established.

[Scoped acceptance](../css-tokenizer-url-native-state-root-v1/ROOT-SCOPED-ACCEPTANCE-V2.json).
The primary public-history component is accepted in `1c787870e8f816d6610872d15d1f0d995de7b667`:
46 modules / 371 reports (108 new), constructor-derived cache coherence, raw
pending cleanup, fetch/save/reset and admitted enable/query histories. Independent
fresh replay agrees on 87 snapshots per debug/release mode; three Lean and four
native semantic mutations distinguish the modeled behavior. Metadata, provider,
machine and safe-entry premises remain explicit.
[Acceptance](../css-parser-public-history-root-acceptance-v1/ACCEPTANCE.json).

Next compose actual skip_whitespace/next wrappers and production cold/Colon entry.
The source audit finds no reachable late-enable defect in the two production
enable sites. The wrapper component is accepted in `ea0a06720982c8716a501fb58f8fbb95d7029ece`
(57 modules / 448 audits, 77 new), after independent fresh replay and full review; nested/depth/callback protocols and
the declaration helper's saved-query/short-circuit automaton remain separate.
[Source audit](../css-parser-entry-wrapper-static-v1/REPORT.md).

### 3. Compose parsing, removal and clear

The root model now kernel-checks 44 lemmas for parser-priority push/extend,
separate storage operations, deletion target bounds, removal-loop safety, the
earliest-removal query certificate, callback stability under unchanged ordered
IDs, and arbitrary mixed parse/remove/clear histories.
The first 35 results have independent review; nine new joins prove the native
membership shortcut and single-property early return and use them in the history.
Duplicate source identities are admitted for sequential extend. These histories
do not yet include CSSOM setting; native interpretation and caller stability
remain open. The immutable flag and changed-return bits are outside this model.

[Checkpoint and replay](../css-declaration-public-storage-proof-v1/PLAN.md).
Static caller review completed without a new bug. It retains native callback
stability and animation-map key/value identity coherence as provider premises.
[Audit](../css-declaration-public-operations-static-v1/REPORT.md).

The source-shaped changing-vector removal loop is now accepted in
`../css-declaration-native-removal-loop-v1/`. Its current-vector reads, separate
index/local length, termination, bounds and same-index-on-removal behavior
compose with the direct query and mixed histories. Independent replay passed
65 audits (44 inherited, 21 new including five examples), a semantic mutation
rejection and two integrity guards. Native containers/compiler/usize and actual
callback readiness remain open.
[Acceptance](../css-declaration-native-removal-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

Animation identity follow-up found no reachable key/value mismatch. Non-null
keyframe entries derive keys from computed values, base extraction uses the map
key, and transition replacement checks the owning property before assignment.
Segment grouping and generated layout remain provider obligations. The new
identity component derives option readiness from the map wrapper and proves
coherent finite composition histories under explicit arithmetic/provider premises. Non-NaN offset validity is required by the grouping
control flow. [Source audit](../css-declaration-animation-identity-static-v1/REPORT.md).
The endpoint/composition and separate map-constructor component is accepted after
full root model/source review and independent fresh replay: 49 audits and nine
integrity controls. It targets the frozen historical source and does not certify
the keyframe-substitution candidate or numeric payload correctness.
[Acceptance](../css-animation-identity-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Next, in priority order

1. Finish the independent reviews and constructor/range proof for the three new
   whitespace candidates, retaining separate evidence and native/WPT commits.
   Then continue epoch-aware attribute provenance and link-env providers. Close the next
   animation provenance boundary after fix80: audit actual
   fallback/composition/publication callers and derive one end-to-end observation
   from admitted constructors. Successful wrapper union is accepted, but it does
   not establish numeric providers or scheduler histories.
   [Accepted repair](../css-animation-interpolation-taint-final-root-v1/REVIEW.md).
   Keep the transition-retention lead INCONCLUSIVE: provenance equality remains
   unresolved, so no restart or refresh repair is justified.
   [Oracle](../css-transition-retention-taint-oracle-v1/REPORT.md).
2. Compose the declaration helper's saved-query/short-circuit paths after the
   accepted skip/next wrapper and production entry component;
   metadata, providers, callbacks and compiler admissions remain explicit.
3. Extend persistent-map caller admission. Count and actual iteration now compose
   through finite COW histories. Registration routing has a coherent-epoch source
   argument, but arbitrary lifecycle/scheduler and two-map disjointness remain open.
4. Continue the public declaration storage/CSSOM composition obligations above.
5. Continue cascade source/observer and hyphenation stateful consumer admission,
   including reflow-to-display cache association and lifetime. Preserve the
   cycle/animation, scope-ownership and uncovered-cache counterexamples.
6. Use ranked spec/implementation audits for further extensions, and the
   [closure checklist](FORMAL-CLOSURE-CHECKLIST.md) for unresolved obligations.
   Finite corpora and theorem counts do not establish whole-CSS coverage.

The same-effect animation dependency audit remains separate: overwriting skipped
CSS-wide defaults is not a general repair because keyframe dependencies use
current computed values.

The explicit-inherit repair has a separately accepted conditional component:
17 audits, four model mutants, and independent fresh replay. Readiness, root
parent absence, concrete map/flag APIs and native compilation semantics remain
admitted. It does not certify the substituted-inherit scheduler path.


## Accepted checkpoints

- **Custom-property count/iterator composition:** 32 new plus 105 inherited
  audits derive RawEnumeration, finite-history live count, exact indexed access,
  unique keys and nearest-owner values. Independent fresh replay and eleven
  semantic model mutants pass. Payload CompareSound is needed only for
  requested-update value equivalence; native representation/compiler/bounds and
  complete CSSOM lifecycle remain open.
  [Acceptance](../css-custom-properties-map-iterator-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

- **Direct declaration removal loop:** 21 new audits connect a changing-vector
  execution to query, singleton/shorthand removal and public operation histories.
  Actual callback stability and native runtime/provider premises remain open.
  [Acceptance](../css-declaration-native-removal-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Parser-priority winners:** 46 new universal lemmas connect arbitrary source
  histories to independent last-important/otherwise-last selection, source order,
  raw representation and exact return flags. Native interpretation and parser,
  provider, container and compiler premises remain open.
  [Acceptance](../css-declaration-parse-winner-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Ordinary declaration batching:** `bb029748eaa6f3aab43b3afa58a1ab0c594ddc2d`
  accepts indexed/scheduled batch refinement
  and optional-publication transfer under explicit native/source admissions.
  [Acceptance](../css-declaration-batch-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **URL mutable state and raw capture:** `e69ef82d29d9c3c9f9244a5174c46245634a3f89`
  accepts v2 and closes the selected model
  bridges with derived helper assignments and original-source endpoint proofs.
  Whole parser histories and codec/machine/heap/compiler premises remain open.
  [Acceptance](../css-tokenizer-url-native-state-root-v1/ROOT-SCOPED-ACCEPTANCE-V2.json).

- **All-shorthand ordering:** native `074086719e445ca72d3056f7fbf793af5e69d6f6`
  follows companion `bad8f7998dbbb3ad1fa88c0ca6892488f912e898`. Sixteen baseline
  failures are repaired; all 40 new and 61 existing subtests pass. Independent
  native/spec and formal review plus root replay accept 55 model theorem audits,
  3,042 candidate transactions and six compiled mutant witnesses. Actual raw
  declaration/importance/membership operations and arbitrary sequential all
  histories refine the forward setter under explicit admissions. The gate
  characterizes a changing intermediate step, not final cssText inequality.
  Pair order converges for any fixed unique expansion; absolute canonical order
  remains open. Ordinary batching and full native/provider/CSSOM lifecycle are
  not proved. [Acceptance](../css-all-logical-order-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Original Bloom milestones 1–6:** accepted within their declared selector,
  provider and native-interpretation scope. Historical M6 replay and the separate
  bounded cache-delta review are recorded in [CONTINUATION-20261017.md](CONTINUATION-20261017.md).
  The original source gate remains immutable; the historical replay explicitly
  does not claim current-source verification or cover changed cached dispatch.
- **Standalone CSS model:** `251269ad1a3b769828efc3321c41464bec50a18a`
  composes ordinary imports with explicit scopes through acquisition, scope,
  cascade and computed visibility. It is a bounded handwritten model with
  finite native comparisons, not full CSS conformance or mechanical spec translation.
- **Comment/string/numeric providers:** accepted component checkpoints retain
  codec, machine, compiler and caller admissions. The closure checklist records
  their exact boundaries and evidence. Native numeric repair is committed;
  full floating-point/library correctness remains open.
- **Parser tracking epoch:** `e9f6a83409e49efdd3018acc2263f247baf007e6`
  supplies ten conditional event-level lemmas and fourteen native observations.
  The later public-history checkpoint composes query/disable and selected byte
  providers under explicit safe-entry and provider premises; wrapper composition
  remains open.
- **Declaration structure/publication:** the top-level curly fallback and
  exclusive-publication repairs are committed as
  `095c5be548a2bddf5f3ff01e01da66c6098a8ee5` and
  `780495d90a85052cff69713f1086180253cb9730`. Their 27 and 29 conditional audits
  preserve parser/provider premises; independent transaction sequences do not
  prove state-dependent CSSOM destination merging. Link-parameters coverage
  enables its pref explicitly and makes no release-default exposure claim.
- **URL provider:** `1a67c0ab4a65227222ce5d3e553b84a2c5914f56`
  accepts 34 modules / 281 exact axiom reports (11 new modules / 96 new reports),
  44 complete native definitions and 57 fixed cases in three modes. Quoted
  Function cursor equality is false; completed string observation is proved
  under derived admission. Body metadata/raw slices, canonical codecs, native
  memory and public histories remain open. Acceptance:
  `../css-tokenizer-url-provider-root-v1/ROOT-ACCEPTANCE.json`.

## Working rules

- Each bugfix commit contains only its necessary native change and WPT/metadata.
  Proofs, tooling and research records precede it in separate commits.
- Record full hashes, paired results, standalone applicability and material limits
  in the bugfix index. Keep accepted source capsules immutable.
- Preserve failed runs and distinguish unsupported syntax, setup errors and
  semantic discrepancies. A fresh-DOM comparison alone is not a spec proof.
- Retain explicit unavailable results for unmodeled semantics. Historical proof
  replay does not certify changed native code; compiler/heap assumptions remain visible.
- Do not expand finite matrices without a concrete remaining risk. Once the
  required local gates pass, proceed to the accepted commit rather than repeat them.
- No pushes, Try jobs or external submissions.

## Build output retention

Retire task-owned generated build targets after their work is complete, active
process/open-file checks pass, and source plus required logs/receipts are retained.
Keep active Firefox object directories and ongoing independent replay outputs.
Record exact removed paths and verify retained evidence rather than deleting
entire research capsules.

## Whole-CSS library research

The user requested three parallel assessments of eventual complete CSS coverage.
Their outputs are kept under ../css-whole-spec-roadmap-research-v1/:

- Specification inventory, version policy, supersession and dependency closure.
- Lean semantic architecture, composition contracts and staged implementation.
- Spec-to-model interpretation, validation, maintenance and completion criteria.

This research does not replace the bug-fix queue or close existing assumptions.
Separate specification-model coverage, executable-model correctness and native
refinement. The existing standalone inventory's 127 fragment records overlap;
its line/audit counts are not coverage percentages. The [research synthesis](../css-whole-spec-roadmap-research-v1/README.md) proposes
a requirement-ledger and property-stage/dependency pilot, then box/layout and
animation integration. These are proposed library milestones; no new semantic
coverage or native refinement is claimed by the research.

The [second research pass](../css-whole-spec-feasibility-v2/README.md) makes the
inventory concrete with 19 provisional requirement records, adds a layout and
fragmentation protocol, distinguishes external inputs from unmodeled CSS
algorithms, and works through a historical CSSOM semantic change. Root reviewed
and authenticated all three tracks. No requirement is newly certified closed.
Next implement the source-lock/ledger validator and bind a complete custom-property
CSSOM slice; use the property/dependency pilot to reach an ordinary box/layout
observation before expanding independent families. The [third research pass](../css-whole-spec-feasibility-v3/README.md) is reviewed
and authenticated: versioned normative views, persistent permitted choices,
phase/owner-aware interfaces, observation-specific sampling and transitive
assumption closure. It adds research proposals, not coverage claims. Comparator-to-map-history composition is accepted after root and independent
fresh replay: nine new results and three compiled mutants connect payload and
taint to lookup and indexed observations of already-computed map updates.
Full native provider/COW and CSSOM routing admissions remain.
[Acceptance](../css-custom-properties-map-taint-history-root-v1/ACCEPTANCE.json).

## Animation endpoint retention accepted — 19 October 2026

Twenty-five audited results derive array/segment read readiness, independent
metadata-scan equivalence, exact added change decisions and finite/prefix
retention histories. Root replay and two compiled missing-endpoint mutants pass.
Native traversal,providers, publication, scheduler and payload/URL-data quotient
remain explicit admissions. This closes the local endpoint retention component,
not the whole animation path. See
[review](../css-animation-endpoint-final-root-v1/REVIEW.md).

Whole-CSS v4 research is producing an executable requirement-ledger prototype,
compiled phase/epoch interface experiments and independent acceptance examples.
Review these before adopting them as infrastructure; no new whole-spec coverage
claim follows from the prototypes.

## Whole-CSS source-ledger pilots — 19 October 2026

The [v4 research and executable prototypes](../css-whole-spec-feasibility-v4/README.md)
are committed in `bd7952da0a6585c32fb7d26e71b184ea25ae93ee`. The source importer
now passes root manifest-only relocated replay: three documents, 2,029,554 bytes,
75,626 lexical units and 16 rejected corruption/edit controls. Independent
fragmentation review matches the final importer and ledger exactly. Its thirteen
requirements and eight scenarios remain proposed interpretations.
[Root accounting review](../css-spec-source-ledger-root-v1/REVIEW.md).

The [architecture extension](../css-whole-spec-architecture-v5/REPORT.md) connects
existing library modules to proposed host-observation, content-continuation and
consumer-relative equality contracts. All new sketches are uncompiled. Next:
review a finite fragmentation domain and feasibility/escalation interfaces, then
implement a source-bound relation and executable selector. Reconcile HTML
style-block and font-cluster interpretations separately. Source bytes and theorem
counts are not a whole-CSS semantic coverage measure.

## Underlying animation base metadata — accepted

Fix 79 adds metadata comparison to the existing new-base-entry scan. The local
proof preserves original changed decisions and derives selected-entry metadata
agreement on no-change. It reasons about requesting a restyle, not actual queue
delivery. Provider identity, native representation, scheduling and full URL
observations remain open. See
[review](../css-animation-base-metadata-final-root-v1/REVIEW.md).

## Numeric interpolation provenance — accepted

Fix80 preserves both operands' attribute taint after a successful generic value
operation. Its 24-case WPT and one-line native patch are independent of earlier
repairs. Root and independent formal replay accept 15 results with 45 native
observations per variant. Numeric providers, admitted fixture observers and
native histories remain open. The whole-CSS coverage, architecture and evolution
agents have delivered the next integration assessment. Root accepts the
fragmentation rule/grid pilot within its stated conditional domain.
[Acceptance](../css-animation-interpolation-taint-final-root-v1/ACCEPTANCE.json).

## Fragmentation rule/grid pilot — accepted conditional component

Root and independent replays pass 34 audited results and nine compiled semantic
mutants. The independent reviewer adds seven kernel challenges and four integrity
controls. Rules, finite grid search, stage selection and conditional positive
slice progress are accepted. Natural-number extents and supplied layout inputs
remain the domain. No native fix or whole-fragmentation claim is added.

The next gate is normative admission: clarify sufficient break opportunities and
the emergency region, then construct actual flow/opportunity/continuation inputs
and prove that the chosen cut materializes permitted fragments. Forced events,
common decorations at all candidates and zero-size after-overflow handling must
remain visible. Do not import an uninstantiated SufficiencyCorrespondence as a
closed CSS premise. [Root acceptance](../css-fragmentation-unforced-root-v1/REVIEW.md).

## Whole-CSS next implementation decisions

The new three-agent [assessment](../css-whole-spec-next-assessment-v1/README.md)
uses the accepted fragmentation pilot as a composition test. Priority: reconcile
its interpreted requirement ledger and normative sufficiency/region frontier,
then derive a real opportunity/geometry/continuation provider and selected-cut
materialization bridge. Next add two independent fragment consumers and
persistent resource/sampling histories. The catalog/CSS2-residual/host universe
remains an explicit parallel accounting task; 127 historical library feature
records cannot serve as a coverage denominator.

The cloned-decoration correction exercise passes ten structural/arithmetic
checks, including stale binding and missing observer/assumption rejection.
Those inputs are supplied; this is not automated CSS interpretation. Standalone
specification, executable reference and Gecko-adapter claims remain separate.
No completion percentage or timeline is inferred from proof counts.

## Animation and fragmentation admission frontiers

The post-interpolation [source audit](../css-animation-post-interpolation-frontier-v1/REPORT.md)
finds no additional demonstrated metadata bug: failed iteration keeps the
already-composed endpoint, and final discrete fallback preserves the selected
whole value. Full segment composition provenance is now the next formal task;
an independent numeric/length provider oracle will establish a reachable branch
before browser testing. This is a correct-path proof target, not fix81.

Fragmentation [admission research](../css-fragmentation-admission-research-v1/REPORT.md)
leaves general sufficiency and emergency-region definitions unresolved. It
identifies a useful ordinary normal-flow sibling domain on initially empty
identical fragmentainers. A paragraph-only failure can miss a legal preceding
deferral; candidate-dependent decorations also defeat a naive shared list.
CSSWG history resolves the zero-after-overflow policy, while actual box/input
correspondence remains open. A requirements-ledger pilot is starting from the
existing174-unit window and explicit adjacent dependencies, before validator
implementation and independent review.

## Full segment composition provider — browser admission checkpoint

The independently derived mixed-number/length probe passes18 checks and one
harness on the unchanged fix80 candidate. Numeric10 retains underlying taint
after failed iteration accumulation; clean40px late selection and tainted32.5
same-type accumulation controls pass. Exact provider/keyframe/timing/grammar and
URL assertions are mandatory. This supports a reachable provider instance for
the next full-segment contributor proof; it is not a new bug or arbitrary native
history theorem. Producer and independent contributor/admission review are active.
[Runtime review](../css-animation-segment-provider-root-v1/REVIEW.md).

## Whole-CSS completion strategy and token-boundary candidate

The latest two-agent [completion assessment](../css-whole-spec-completion-strategy-v1/README.md)
adds a 17-family gap matrix, catalog/CSS2-residual completion gates, standalone
library boundaries and explicit soundness/availability/construction/preservation
obligations. Priorities remain a reviewed requirement ledger, a constructed flow
provider, actual selected fragments, distinct observations and versioned host
histories. A complete corpus inventory runs alongside the integration experiment.
The fragmentation requirement pilot now has independent bounded mapping review.
V3 corrects statement-extractor profile failures while preserving the 18 exact
claims and ten open providers; independent and root final replays pass. Accounting checks do
not establish complete semantic coverage.

Typed registered-value conversion exposed a new browser defect: a
length-percentage serialized as a dimension retains percentage boundary metadata;
a list also takes both boundary classes from its first component. The corrected
37-case fixture demonstrates ten failures with 27 passing controls. The patch
scans the already-serialized tokens and treats block closers explicitly. A first
compile attempt caught a parser-borrow lifetime error; the corrected build and
308-case candidate/regression run pass. Independent native/WPT review and
standalone two-file source apply/reverse pass. Dedicated WPT lint passes; the
general lint warning is the expected ESLint WPT exclusion. The formal producer
has completed 22 audited results and 24 native fixtures; independent and root
fresh replays pass. The bounded component and native/WPT repair are accepted
in their stated scopes. Native/WPT commit `34e4e755cb81332819e56457f5fb68b9b305c394`
follows evidence `76d4707974532db89589ffa39f2728db46527114`. The committed bug count is 82.

## Requirements-ledger review defect and segment replay

Independent review found a truncated `Emergency.graphic_slice_contract` claim in
fragmentation requirements v1. Its extractor selects the first `:=`, including
record-field assignments inside binders, so a partial statement incorrectly
passes. Root confirmed the exact source discrepancy. Keep v1 frozen and
unaccepted; correct extraction in a new version and reject this exact case.
The underlying accepted Lean theorem and lexical source accounting are intact.

Full segment provenance has passed root fresh replay: 45 new + 15 imported audits,
15 source bindings and 8 compiling model mutants. Independent review and root outcome reconciliation pass; this conditional
component is accepted. Publication and actual provider/caller histories remain
open. [Acceptance](../css-animation-segment-provenance-root-v1/ACCEPTANCE.json). Completed owned
root and agent compiler outputs have been removed after preserving receipts.
The whole-spec inventory has independent reconstruction and root replay of all
402 catalog occurrences and 841 CSS2 TOC entries. The 191 identities remain
provisional; none of these counts measures normative coverage. The next corpus
step has retained 26 full CSS2 chapter/appendix bodies, dated counterparts and
31 errata entries. Independent and root review accept bounded source spans,
heading reconciliation and the retained unapplied errata overlay. Packaging needs
the authenticated transitive closure, including two nested manifests omitted
from top-level FILES. Full normative requirement/dependency mapping remains open.
[Corpus acceptance](../css-css2-residual-corpus-root-v1/REVIEW.json).
[Fragmentation ledger acceptance](../css-fragmentation-requirements-root-v3/REVIEW.json).

## Animation publication repair accepted and committed

The selected endpoint's inner guaranteed-invalid value currently uncomputes to
CSS-wide initial, which can select a valid registration initial value. A revised
16-case browser fixture independently produces invalid underlying values rather
than relying on the earlier explicit-inheritance fix: ten failures, six controls.
The candidate introduces an internal GuaranteedInvalid declaration, marks it seen
and removes its routed map value. Explicit initial behavior remains distinct.

Build and the 343-case paired matrix pass, fixing precisely ten failures with
333 other status/message pairs unchanged. The final 22-case WPT additionally
checks suppression of valid underlying declarations/effects, cancellation and
valid-empty values; these six additions have candidate-only runtime evidence.
Root excluded an unrelated formatter signature change with an exact recorded
transfer. Independent native/WPT review, dedicated lint and standalone source
packaging pass; root freshly replays both review checkers. Root and independent
review accept the v2 publication/suppression proof: 81 audits (42 new), 29 source
bindings, five Lean mutants and three Rust mutants in debug/release. Fourteen
independent boundary theorems also pass. V1 mathematical replay passed, but its
checker was rejected because Python optimization disabled assertions; v2 rejects
optimized modes before dispatch. Native translation, providers and scheduling
remain admitted. [Acceptance](../css-animation-invalid-publication-final-v1/ACCEPTANCE.json).
The wider comparison combines contemporary and historical baselines;
neither standalone source package has an isolated browser run.

[Build and paired runtime](../css-animation-invalid-publication-fix-v1/RUN.json).
[Additional controls](../css-animation-invalid-publication-controls-v1/RUN.json).
[Proof scope](../css-animation-invalid-publication-proof-v1/SCOPE-PROPOSAL.md).

## Attribute-taint security investigation

The dedicated review reproduced a CSS-only URL-taint policy violation in installed
Firefox 158 with default CSS feature preferences. Script-free loopback testing
observed four forbidden image requests in release that disappear in the patched
shared build; ten literal/permitted controls remain. No arbitrary unknown-byte
extraction or incremental disclosure was demonstrated. The numeric selection
experiment also works through permitted static CSS. Fix 80 is the first candidate
for security triage; official severity remains unassigned. This comparison uses
an all-fixes development binary, not an isolated fix 80 build.

The formal target remains metadata-preserving optimization and the specified
URL boundary. Global network noninterference is stronger than that contract.
[Report](../css-attr-taint-security-review-v1/REPORT.md).
[Root review](../css-attr-taint-security-root-v1/REVIEW.json).
