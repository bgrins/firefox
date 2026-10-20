# CSS and Stylo verification plan

Updated 20 October 2026. Work stays local; the user owns pushing.

## Current status

- **Translation carrier proof committed:** `63bf6c30eef0`. Nine Lean
  results and six independent checks bound translations for admitted cumulative
  coordinates without a frame-count limit. Corrected fresh replay passes; the
  original replay harness failure is retained with an erratum. The native
  checked64 successor still needs final review, browser tests and performance
  checks. [Numeric checkpoint](../css-cssom-exact-traversal-bounds-root-replay-v2/REPORT.md).
- **Destruction callback audit committed:** `6e53130a808e`. Fifty of 51 selected
  definitions match the live tree; the remaining difference is the committed
  cache-key value field. Property destruction can precede the second primary-bit
  read, and SVG observer dispatch can be synchronous. Actual selected-path
  reachability and lifetime safety remain open; this is no new native bug claim.
  [Callback checkpoint](../css-primary-destruction-callback-root-v1/REPORT.md).
- **Primary ownership component accepted and committed:** producer
  `885c94769ed3`, review `2c441db9213b`.
  Root replay passes 40 audits over 26 bound definitions; independent review adds
  12 kernel challenges and seven integrity controls. This proves admitted stable
  histories and selected initialization, with actual destructor callbacks and
  heap representation still open. The live constructor has a retained generated
  cleanup difference; no broad indexed-source lifecycle transfer is claimed.
  [Root acceptance](../css-primary-bit-coherence-root-v1/ACCEPTANCE.json).
- **Traversal v2 browser checks pass; native repair remains held on cost.**
  Signed evidence `c29fd817ebc3`, runtime `3ec270d944da`. Actual builds and formatting
  pass. The 23-file/74-subtest comparison fixes both untransformed large-edge
  failures, with all four new cases passing and all other outcomes unchanged.
  Six timing runs show deep ordinary medians of 400 ns versus 300–350 ns in surrounding
  baselines; near-root transforms at 450 ns versus 350–400 ns. Quantization and fixed
  phase order limit interpretation, but root and independent review recommend
  holding this version. Source/build restoration completed; no integer candidate
  remains installed. [Actual experiment](../css-cssom-exact-traversal-runtime-v2/REPORT.md),
  [independent review](../css-cssom-exact-traversal-runtime-review-v2/REPORT.md).
- **Next traversal optimization is artifact-only.** Select traversal mode once,
  simplify checked accumulator state with public SafeAdd and combine redundant
  guards. Preserve ancestor-context checks, v1 inclusion, v2's expanded exact
  domain and old-defined matrix behavior. A fresh review/build/browser/timing
  cycle is required; v2 results are not transferred to the untested v3 draft.
- **Allocation footprint proof is in development.** Model actual selected
  detach/delete order in one heap, including allocated empty arrays and raw
  dangling/repeated frame references. Root review required explicit allocation
  role checks; cache-type decoding and full callbacks/lifetime remain open.
- **DOMRect precision committed:** `c0e8c7fd1deb` preserves already calculated
  double coordinates. Its four-case WPT passes independently; selected existing
  regressions retain their outcomes. The bounded 26-audit numeric component has
  root and independent review, 53 native/reference cases per optimization mode,
  and 11 complete source bindings. Universal IEEE and full CSSOM claims remain open.
- **Integer-translation repair held:** correctness witnesses pass, but a deep
  transform-near-root microbenchmark repeatedly rises from 400 to 550 ns per call. The
  next design should carry exact translation through the existing traversal.
  Retain SVG/context/viewport/clipping guards and checked numeric bounds.
  [Performance decision](../css-cssom-rectangle-performance-runtime-v1/REPORT.md).
- **Full obligations continue:** numeric component acceptance does not close
  safe-origin F1–F12, allocation F1–F16/F11/F12, provider lifetimes or fragment
  observers. Signed table subtraction remains a separate investigation with
  no accepted native repair or established memory-corruption impact.
- **102 committed native/WPT fixes; no accepted repairs await signing.** The
  14-fix queue is complete, including its 34 preceding evidence/proof commits.
  All 48 signatures and exact native parent deltas were checked. See
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md) and
  [CURRENT-COMMITS.json](CURRENT-COMMITS.json) for management identifiers.
- **Earlier fixes:** leading-whitespace attribute origin (`ad608a212bd8`),
  trailing-whitespace token metadata (`bccea9c1fffc`) and escaped trailing
  whitespace (`fff2d758ef6b`). Each has a preceding evidence companion and
  a separate two-file native/WPT commit. All three also have signed standalone
  upstream alternatives; see the commit ledger. No isolated upstream runtime is claimed.
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
- **Backslash/newline repair committed:** `246f1ff43250` retains required
  newline whitespace after an actual backslash delimiter. Its final WPT has
  30 passes against a baseline subset with 16 failures and 14 passes. Root and
  independent proof review accept 53 audits plus 15 independent kernel challenges;
  lexical projection, EOF compatibility and reference bounds remain explicit.
  Signed standalone upstream alternative: `95b6a9b03c1c`.
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
  Nested-control v3 now has root and independent scoped acceptance: 39 audits,
  59 modules, 18 cases and 91 native/model snapshots in debug and release. Three
  native mutants differ in 10, 25 and five rows; five additional root kernel
  challenges demonstrate progress and callback-control limits.
  The revised capsule rejects pre-import shadowing and nonclosed file rosters.
  Universal callback grammar, native termination, full LinkParameters and
  whole-program annotation correspondence remain open.
- The [triage proposal](../css-bugfix-triage-20261019/README.md) groups the first 80
  committed fixes with exposure limits and standalone alternatives. A separate
  registered-animation WPT calibration correction is committed separately;
  it does not increase the native-fix count.
- Signing succeeded for the complete accepted queue. Signing stays enabled. Nothing has been pushed or submitted externally. Later signing-blocker statements describe earlier checkpoints.

[Historical checkpoints](PLAN-HISTORY-20261019.md) preserve the previous plan
verbatim. Their counts, signing blockers, agent states and “next” sections are
historical observations. The current schedule is below; historical open proof
obligations remain open unless a later acceptance record explicitly closes them.

## Current flex verification checkpoint

- **Scroll-container baseline provider repair accepted:** ordinary asymmetric
  borders expose a preexisting last-baseline coordinate error in release Firefox.
  The standalone two-file patch repairs 72 failures in 384 WPT cases;
  312 controls and all 38 focused regression files pass. Root accepts the
  conditional full-method companion after 48 fresh audits, 1,536 candidate
  cases, twelve independent reviewer audits and five root projection joins.
  Child baseline truth, geometry and lifecycle remain provider premises.
  [Acceptance](../css-scroll-baseline-provider-proof-root-v2/ACCEPTANCE.json).
- **Natural donor acceptance withdrawn:** a new calibrated 64-case probe
  finds six asymmetric scroll-border last-baseline failures in the candidate;
  installed release passes all 64. The conditional proof remains valid, but
  its native-provider premise is not established for these ordinary cases.
  The accepted provider repair removes those six failures, but the donor patch
  still depends on it semantically. Resolve independent landability before
  restoring donor acceptance; source commutation is insufficient.
  [Probe](../css-flex-scroll-baseline-border-probe-v1/probe.html).
- **Relative-position baseline repair accepted:** the separate two-file patch
  repairs 192 failures in 288 WPT cases and preserves 96 controls. Fresh root
  replay passes 29 kernel audits and 1,080 source/model cases per variant;
  eight independent checks and three rejected false claims pass. Property
  lifetime and full downstream/provider histories remain open. Its evidence,
  review and formal companions precede the native/WPT commit in the queue.
  [Acceptance](../css-flex-relative-baseline-proof-root-v1/ACCEPTANCE.json).
- **Packing v1 rejected:** the reviewer’s fragment-cancellation witness
  reproduces in the browser. Two large, calibrated multicolumn cases pass
  in release and fail in the candidate; two smaller controls pass in both.
  The earlier 432-case WPT and unfragmented controls remain useful evidence,
  but narrowing before consumed-fragment subtraction changes valid placement.
  V2 must preserve wide coordinates through fragment adjustments, line metrics
  and cumulative-size storage. The shared build still contains rejected v1.
  [Counterexample](../css-flex-packing-fragment-probe-v1/REPORT.md).
- Counts: **87 committed fixes and ten accepted repairs awaiting signing**.
  Latest user-requested signing retry failed; HEAD and the verified 297-file
  staged snapshot are unchanged. No pushes or external submissions.

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

1. Complete the separate view-transition type-mutation style-invalidation repair
   and its runtime/formal gates, then sticky H1/H2 obligations. Initial-type
   deduplication is committed as fix87. Preserve separate evidence and native/WPT commits. The [worktree audit](../css-native-worktree-reconciliation-v1/REPORT.md)
   records the remaining intentional native candidates and their gates.
   Continue epoch-aware attribute provenance and link-env providers. Close the next
   animation provenance boundary after fix80: audit actual
   fallback/composition/publication callers and derive one end-to-end observation
   from admitted constructors. Successful wrapper union is accepted, but it does
   not establish numeric providers or scheduler histories.
   [Accepted repair](../css-animation-interpolation-taint-final-root-v1/REVIEW.md).
   Keep the transition-retention lead INCONCLUSIVE: provenance equality remains
   unresolved, so no restart or refresh repair is justified.
   [Oracle](../css-transition-retention-taint-oracle-v1/REPORT.md).
2. Derive source-dispatch-specific progress or total admitted provider families.
   Root and independent review accept the five-theorem delimiter bridge and 12
   review results; its driver delimiter law does not establish global progress.
   Then extend URL annotation projection through represented callback programs,
   and compose the declaration helper's saved-query/short-circuit paths after the
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

## Nested parser control accepted

Root and independent v3 replays match all 91 snapshots and the three compiled
native mutation deltas. The source-bound model derives raw cache retention,
pending-none recovery, raw comment annotation writes and nested/until-before
control correspondence for represented callbacks. The six Link paths are finite
kernel facts, not a universal grammar proof. Root adds five premise challenges.
The independent package's 20 negative guards and intact positive passed.

Next: inspect and model parse_until_after's direct delimiter advance and curly
recovery; extend the represented callback grammar where it exposes real callers.
Lexical progress, native byte bounds, full annotations and Link value parsing
remain open. [Acceptance](../css-parser-nested-control-root-v1/ACCEPTANCE.json).

## Accepted until-after continuation

Root and independent review accept the [delimiter continuation component](../css-parser-until-after-root-v1/ACCEPTANCE.json):
22 general theorem audits, 11 root kernel challenges and ten independent checks
recompiled by root. Fresh manifest-only replays agree with exact-source cssparser
in debug and release across 27 histories and 138 snapshots. Six successfully
compiled native mutants are detected. The independent review adds six native
cases in both modes. Current parser/tokenizer bytes match the retained sources.

The proof connects direct byte advance to source-token consumption using explicit
progress and delimiter laws, preserves enclosing ownership and Stop/error state,
and covers curly recovery. Main alignment excludes URL annotations; separate
continuation write laws cover those effects. Full callback annotation composition,
arbitrary callbacks, omitted tokenizer providers and native machine correspondence
remain open. The predecessor renderer correction is recorded: all old 91 snapshots
had zero stop masks, while new tests exercise nonzero enclosing masks. No new
browser defect is counted.

The [accepted provider bridge](../css-parser-delimiter-provider-root-v1/ACCEPTANCE.json)
derives the delimiter law from ByteLex and a one-byte punctuation contract.
Fresh root and independent 59-module replays pass five general results and 12 review
results, including the exact driver law for arbitrary input and jointly inhabited
provider premises. Its global progress corollary cannot be applied to the actual
partial driver without further admissions; the explicit counterexample is retained.

## View-transition mutation invalidation lead

The calibrated loopback probe reports six discrepancies among 18 rows: successful
Add/Delete/Clear update public membership and direct selector matching but retain
stale computed root color and descendant width, both synchronously and after ready.
All before-state and forced-refresh calibrations pass; twelve no-op/completed/old
transition controls pass. No duplicate initial types are used. Source/binary pins
are stable. Evidence: `../css-view-transition-type-invalidation-v1/v2/runtime-v1/`.
Independent source/spec/native/WPT review is accepted. The paired 42-case WPT
now passes completely: six improvements, 36 unchanged. Warmed root/descendant
::before and ready-only transition-group opacity checks are included. Build,
scoped C++/WPT lint and exact four-file upstream apply/reverse pass. Formal
companion and independent mathematical review remain pending; no native commit
is counted yet. [Native acceptance](../css-view-transition-type-invalidation-root-v1/ROOT-NATIVE-ACCEPTANCE-v1.json).

## Initial view-transition type deduplication committed

Fix87 (`2db943802038`) contains only the Gecko startup repair and its 21-case WPT;
`baa7f955bacd` contains preceding evidence. Five baseline failures become passes.
Fresh root and independent formal replays accept 90 conditional audits and 1,755
cases; 12 independent challenges exercise provider boundaries. Exact upstream
source applicability is checked, without an isolated upstream browser claim.
[Acceptance](../css-view-transition-types-root-v1/ACCEPTANCE.json).

The distinct invalidation lead now also has a baseline WPT run: six failures
and 12 controls pass, with all 24 initial-type/existing mutable controls passing.
A separate calibrated probe confirms stale ordinary and transition pseudo-element
styles. The candidate native repair is now applied and its build, paired 42-pass WPT,
scoped lint and independent native/WPT review pass. The formal companion and
independent proof review remain pending. It is not counted as a committed repair.

Sticky H1/H2 formal implementation has resumed with all ten preserved obligations
and explicit rectangle, writing-mode, finite-sentinel, clamp and caller boundaries.
[Scope checkpoint](../css-view-transition-type-invalidation-root-v1/STICKY-SCOPE-CHECKPOINT.md). No acceptance or H3 repair is claimed.

The [triage addendum](../css-bugfix-triage-20261019-addendum-v1/README.md) covers
fixes81–87, prioritizing the minimal release bounds-panic reproduction in fix83.

## Type invalidation accepted; signing pending

The native repair, final 42-case paired WPT, source-only upstream packaging and
scoped lint are accepted. Root and independent fresh formal replays pass 39 audited
results, 15,234 cases and 51,702 snapshots. Root additionally compiled eight independent
kernel examples and two exact-mutant incoherence theorems. Two C++ mutants alter
production control; two alter substituted traversal/cache providers. Full native
resolver, traversal, scheduler and lifecycle correctness remain admitted.
[Acceptance](../css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json).

Configured 1Password signing failed with “failed to fill whole buffer”; the user
was notified. 297 evidence-only files remain staged for the exact retry recipe.
The three native files and WPT remain unstaged. There are 87 committed fixes and
one accepted repair awaiting its separate evidence/fix commits.

Final packaging found a generated Python bytecode cache inside the independent
review copy, outside the producer closed manifest. Mathematical/native replay
results remain valid; final review-artifact acceptance is reopened until a
corrected version authenticates the nested capsule and replays without it. The
original sealed review is preserved. Signing also remains pending.

## View-transition invalidation review correction accepted

Independent review v2 removes the generated cache from its copied producer capsule, independently checks the nested closed roster, and passes a fresh full replay and 19 negative controls. Root authenticated the seals, reran the review checker, and verified unchanged challenge sources against its previous successful compilation. The 39 audits, 15,234 cases, and 51,702 snapshots retain their conditional scope. Native evidence remains six failures to 42 passes. The repair is accepted pending its separate signed native/WPT commit. See `artifacts/css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json`.

## Collapsed-flex review and two runtime findings

Root authenticated and replayed the independent collapsed-flex native review:150 paired cases show78 improvements,240 additional candidate controls and82 existing checks are retained. Another420 focused overflow observations disprove the proposed strut-scroll regression. The full16-obligation formal scope was reviewed and implementation assigned; retained-frame consumer safety remains a required derivation, not a provider assumption. See `../css-flex-collapsed-alignment-root-v1/NATIVE-REVIEW.json`.

Two separate leads now reproduce in installedFirefox158 and the shared development build. Safe alignment in reversed scrollable flex containers loses reachable content:24 calibrated scroller discrepancies per280-row run, with the broader non-scroller spec/WPT conflict kept separate. The sticky proof's finite-sentinel boundary predicts unwanted movement of all-auto boxes beyond about8.95millionpx; calibrated42-row runs yield6sticky discrepancies and36matching rows. The latter's initial overlystrict precision oracle is preserved and corrected with ordinary controls. Reports: `../css-flex-safe-overflow-probe-v1/REPORT.md` and `../css-sticky-sentinel-probe-v1/REPORT.md`. Neither is counted as fixed.

The sticky sentinel WPT has a24-case baseline:4failures and20passes. A separate per-inset positional-clamp repair is being built; H1/H2 proofs remain tied to their earlier source snapshots, and range/timeline extreme behavior is not claimed repaired. Quote containment also has a new source/scope review in `../css-quote-scope-append-root-review-v1/SCOPE-REVIEW.md`; full proof remains pending. Signing remains unavailable; the exact297-file evidence checkpoint is preserved.

## Sticky repairs and formal checkpoints

The finite geometric-sentinel repair passes all 24 paired WPT cases (four improvements), a successful build, scoped native lint, 1,328 regression subtests and three reftests. Follow-up sticky/timeline tests retain eight passes, two pinned expected failures and one passing reftest. Its independent native review is accepted.

The combined positional companion now passes original and relocated replay: 59 audited declarations, 856 cases and 5,136 complete Lean/native comparisons of results, frame positions and caller traces. Seven native mutants and five executable lifecycle-model mutants are detected. Fifteen integrity controls and two forbidden-axiom controls pass. All 20 raw streams match after relocation. The replay pins 15,308 installed Lean files and 959 native header dependencies. Numerical projection substitution into the common lifecycle model is proved. Independent review v2 is now frozen with HOLD: actual indexed continuation/common-translation refinement, graph/fuel termination and executed machine-operation joins remain missing. Root authenticated all228 review files. Preserve the full original contract when implementing these joins; the existing theorem must not stand in for the missing caller semantics. Geometry/lifecycle providers remain explicit admissions. See [the frozen producer checkpoint](../css-sticky-sentinel-proof-v2/REPORT.md). Range/timeline sentinel collisions remain outside this positional repair.

The separate explicit-offset repair reserves NS_AUTOOFFSET after resolving an explicit value. The 80-case WPT improves from 32 FAIL/48 PASS to 80 PASS, with explicit opposite-edge zero to avoid depending on the automatic-inset repair. Build, scoped lint, 1,328 regression subtests and three reftests pass. The two-file patch applies and reverses on HEAD/upstream; no isolated upstream build is claimed. Its extended formal producer v2 passed replay, but independent review found the final formatted source duplicated in the browser-tested source role. The real tested snapshot remains in the native evidence. Native/WPT review passes; correct this source identity and replay all three genuine variants in a new immutable version before formal acceptance.

H1/H2's independent review is frozen with HOLD on the original full scope. All 106 existing audits and fresh native/model replay pass, but universal GetScrollRanges rectangle composition/bounds and Earliest/Latest signed32 caller joins are missing. Root authenticated all 599 outer and 268 nested files. V2 now supplies both components and root replay passes all 162 audits, 2,224 full absolute observers and 11,898 endpoint comparisons. Root review found R3: chosen-axis EntrySafe omits the other axis executed by ComputeStickyLimits and complete nsPoint subtraction. Three kernel witnesses and six UBSan runs confirm the gap, including coordinate-bounded inputs. Preserve the full contract and add the two-axis execution admission/derivation in v3. See [the v2 root verdict](../css-sticky-insets-proof-root-v2/VERDICT.json); the original [v1 verdict](../css-sticky-insets-proof-review-v1/VERDICT.json) remains historical evidence.

## Collapsed flex exported-baseline repair

The retained-frame observer audit exposed six mismatches in the same 20-case release/shared-browser roster. All ordinary, removal and restoration controls pass. The unconditional F11 baseline observer obligation is false for the frozen allocation candidate; the remaining allocation work continues under its original 16-obligation contract.

A separate native candidate now excludes struts from baseline donor selection and requests synthesis when there are no participants. The expanded WPT covers both column directions, both baseline groups and nowrap/wrap/wrap-reverse. Its directly paired result is 22 FAIL/38 PASS to 60 PASS, with all 38 other status/message pairs unchanged. Twenty-five existing files pass (23 reftests and three subtests). Builds and scoped native/WPT lint pass. The repaired local build was restored after the baseline experiment.

The exact two-file Gecko/WPT patch applies and reverses on HEAD and retained upstream without absorbing the allocation changes. Independent native/WPT review and the formal companion remain open. A row with a strut-only edge line exposes a specification ambiguity, even with zero gap; the candidate retains the existing no-donor numerical fallback and does not claim a normative resolution. Continuation synthesis-state publication also needs review because later fragments can bypass DoFlexLayout. These gates are not discharged by unfragmented WPT success. See [the candidate report](../css-flex-collapsed-baseline-fix-v1/REPORT.md).

## Signing and retained state

The latest user-requested signing retry again failed in 1Password with “failed to fill whole buffer”. HEAD remains 92a6fddf18e5828b17d7491a34663a0d5a9c12ad; all 297 staged evidence files were reauthenticated. The count remains 87 committed fixes and one accepted invalidation repair awaiting signed commits. Runtime/proof checkpoints do not increment that count. The formal companion's documentation pins track the newer unstaged roadmap/ledger; the staged evidence snapshot remains intact. Do not retry signing until the user indicates readiness.

Completed root native replay products were removed after matching the original and relocated results; recipes, sources and raw evidence remain. Temporary Lean products are removed by the runners. The main Firefox build remains available with the baseline and sticky candidates applied, including the new negative-inset arithmetic candidate. Root removed37.3MB of completed proof/native replay products; generated sources and raw receipts remain.

## New observable lead: opposing negative sticky insets

Review of the caller arithmetic domain led to a separate small-tree browser reproduction. Installed Firefox158 and the shared Firefox160 build produce the same60 observations:24 failures and36 passing controls, with all dimensions, scroll and static-reference checks passing. The standalone60-case WPT baseline reproduces24FAIL/36PASS. Huge opposing negative insets unexpectedly move a target200px; smaller or asymmetric negative controls pass.

The native candidate widens view-rectangle arithmetic and stores sticky limits as direct edges, since widening normalization alone can leave origin-plus-width overflow. Its initial build exposed two direct-field consumers; those now use accessors and build-v2 succeeds. The candidate passes all60 paired WPT cases,1408 regression subtests and3 reftests, plus scoped native/WPT lint. An exact three-file patch applies/reverses on HEAD and retained upstream without H1/H2/sentinel/alias changes. Twelve preliminary Lean integer results establish normalization identity, wide intermediate bounds, conditional stored-result bounds and concrete wide-interval witnesses; full source/provider/observer composition and independent native/formal review remain pending. Keep this separate from H1/H2, geometric sentinels and explicit-auto encoding. [Probe](../css-sticky-negative-inset-overflow-probe-v1/REPORT.md), [candidate evidence](../css-sticky-negative-inset-overflow-fix-v1/). No count increment.

## Current handoff: two accepted repairs pending signing

There are 87 committed fixes and two accepted repairs awaiting signed commits: view-transition invalidation and explicit sticky-inset encoding. The alias v3 source-role correction passes root review and fresh replay: 31 audits, 236 cases, six genuine-source native configurations, five paired mutations, 11 provider negatives, 33 integrity controls and two axiom controls. See [root review](../css-sticky-offset-alias-proof-root-v3/REPORT.md). Earlier source-role HOLD records remain historical evidence.

The latest user-requested signing retry again failed in 1Password; HEAD and the exact 297 staged files remain unchanged. The negative-inset standalone sticky source passes all 60 WPT cases; the combined source and successful build are restored. Its full proof and independent review remain pending. H1/H2 v3 is undergoing producer replay with full two-coordinate arithmetic admission; the geometric-sentinel lifecycle proof still needs its indexed-graph and machine-operation joins.

## H1/H2 full caller review accepted

The v3 correction retains the complete two-coordinate frame through core construction and displacement subtraction, with the real early-return guards. Root authenticated all1044 producer files and replayed17modules/191audits, all four2224-case source variants, existing range/endpoint calibration and mutants. All35 integrity/comparator controls pass. Nine additional root kernel checks and twelve extracted-native runs distinguish selected-continuation position/normal properties from canonical range geometry, including missing-property fallbacks and expected excluded overflows. The full stated conditional contract is accepted; H1 and H2 are two separate accepted repairs awaiting signed commits. See [root review](../css-sticky-insets-proof-root-v3/REPORT.md).

Current count:87committed,4accepted pending. Explicit-inset commit recipes are prepared; H1/H2 queue packaging is next. Root cleaned23.2MB of completed products. The geometric-sentinel agent is closing indexed lifecycle/termination and machine joins. The negative-inset agent is implementing the full companion after independent native/WPT acceptance, including the retained preexisting range-clamp witness. Collapsed allocation retains F11refuted and explicit incomplete F12native boundaries while its expanded source checkpoint is finalized. No count is assigned to those incomplete repairs.

H1/H2 native packaging now verifies both standalone patches on current HEAD and retained upstream. The context-adjusted H2-after-H1 patch reproduces the exact archived combined browser source and reverses cleanly. Each patch retains only one Gecko file and its WPT; all real index/worktree state is preserved. See [packaging](../css-sticky-insets-commit-v1/PACKAGING.json). The seven evidence/formal/native commit recipes are ready in `artifacts/css-sticky-insets-commit-v1/QUEUE.json`; each native repair retains its own WPT. Signing is being retried at the user’s request.

## Collapsed allocation checkpoint replay

Root authenticated the sealed source and durable replay manifests, then reproduced all 266 audits and 52,160 native/model cases. F11 remains refuted and F12 retains concrete source/provider and downstream arithmetic gaps; this is a successful checkpoint replay, not acceptance of the repair. The baseline candidate remains under independent review. Root removed 18.7 MB of completed replay products while retaining sources, commands and observations. See [checkpoint review](../css-flex-collapsed-allocation-proof-root-v1/REPORT.md).

## Flex baseline sum overflow: paired repair candidate

The F12 operation review found a separate observable arithmetic defect: independent baseline-edge maxima overflow a signed32 sum. A two-item probe reproduces zero height instead of 100px in installed Firefox 158 and the shared 160 build, even with max-height: 100px. The new 54-case WPT changes 12 failures to passes, with 42 unchanged. All 29 regression files pass; build/native/WPT lint pass. The exact two-file patch applies/reverses on HEAD and retained upstream. Six primitive kernel results and extracted-native UBSan comparisons accompany the repair. Independent review remains pending; counts stay 87 committed and 4 accepted pending. See [repair report](../css-flex-cross-baseline-overflow-fix-v1/REPORT.md).

The collapsed-baseline donor repair now has an authenticated independent native/WPT review. Full F11/F12 remain open; the agent is implementing versioned source/provider/frame/overflow joins in a new v2 component, preserving the original contract and earlier refutation. Its first audit found that the detached rectangle union model differs from the native both-empty case; no new browser defect is claimed from that distinction.

Signing retry still fails in 1Password. The 297-file staged evidence snapshot and HEAD remain unchanged. The shared local build now includes the separate cross-size sum repair; only whitespace formatting followed its successful build.

## Safe-scroll candidate and retained collapsed-frame overflow

Counts remain **87 committed fixes and 4 accepted pending**. Signing retry still fails in 1Password; HEAD and the authenticated297-file staged checkpoint are unchanged.

The own-scroller safe-flex repair is now a sealed native/WPT candidate:484 failures become passes across640cases, with156unchanged controls. A paired72-case ownership probe changes only four body-owned safe cases;14regression files pass798subtests and10reftests. The exact two-file patch is independent of other pending flex changes. Ten preliminary reachability lemmas pass, but complete formal/source joins and independent review remain open. See [candidate](../css-flex-safe-scroll-origin-fix-v1/REPORT.md).

Full F11 review found another observable retained-frame defect: a collapsed240px child with border/margin/descendants can enlarge a100px flex scrollport. Release and repaired builds have24identical observations, including12collapsed overflow cases. The plainzero-width control passes. Earlier420controls used shorter items and did not refute this case; their broad no-overflow conclusion is superseded. A kernel/source-extraction counterexample now preserves the full domain; a separate145-case WPT baseline is running. See [discovery](../css-flex-collapsed-tall-strut-root-v1/REPORT.md).

The negative-inset v2 complete conditional companion passed a fresh root replay:219audits,544Lean rows,2164genuine native observations,9semantic mutants and the retained clamp-UB exclusion. Independent review is active. Geometric-sentinel v3 is also sealed, with167audits and the formerly missing indexed/machine joins; independent review remains pending. No acceptance is inferred from successful replay alone.

Next: finish the collapsed-overflow repair and paired WPT; address the baseline-sum WPT numeric-range portability review; complete independent sticky reviews; build the safe-scroll source/consumer companion without narrowing its contract.

## Current accepted queue: six repairs pending signing

Counts: **87 committed fixes, 6 accepted pending**. The opposing-negative-inset repair now has accepted full conditional source/caller proof and native/WPT review. Root's219-audit replay,2,164genuine native observations and12fresh independent kernel checks are sealed in [root acceptance](../css-sticky-negative-inset-overflow-proof-root-v2/REPORT.md). Its original preexisting clamp-UB exclusion remains explicit.

The baseline cross-size sum repair also passes final review after a portability correction: the WPT explicitly marks unsupported extreme numeric ranges optional while retaining its unconditional100px oracle on admitted inputs. All54Gecko inputs are admitted;12failures become passes and42controls are unchanged. The native body/patch is identical to the accepted v1 arithmetic change. See [corrected package](../css-flex-cross-baseline-overflow-fix-v2/REPORT.md).

The new collapsed-frame overflow repair passes145paired cases (93improvements) and34regression files (29reftests,757subtests), plus build and lint. It retains a separate two-file patch; independent native review and full F11/F12 composition remain open. See [candidate](../css-flex-collapsed-scroll-overflow-fix-v1/REPORT.md). The safe-scroll candidate is undergoing independent native review and full formal-scope planning.

Geometric-sentinel v3 passed a fresh root replay with all30raw streams identical to canonical/relocated evidence. Root inspected indexed and machine joins; final sequential update/source review and independent challenges remain open. No acceptance promotion yet. Completed root proof/native products were cleaned:20.3MB for negative insets and2.47MB for the sentinel replay; the main Firefox build remains available with every repair restored.

Next priorities: finish collapsed-overflow and safe-scroll reviews; complete the original retained-frame/machine contracts; finish sentinel v3 review; prepare preceding evidence/formal commits for the two newly accepted fixes. Signed commits remain blocked by1Password; no new retry until user readiness.

## Prepared queues and native review decisions

Counts remain **87 committed fixes and 6 accepted pending**. The latest requested signing attempt failed with the same 1Password buffer error; HEAD and all 297 staged evidence files remain unchanged.

The [negative-inset queue](../css-sticky-negative-inset-overflow-commit-v1/QUEUE.json) and [baseline-sum queue](../css-flex-cross-baseline-overflow-commit-v1/QUEUE.json) are prepared. Each has preceding evidence/formal commits and a separate Gecko/WPT commit. Temporary-index checks verify both retained bases, the complete queued native order, exact three-file/two-file deltas, and inverse application. The negative-inset integration preserves earlier normalized-inset and logical-end fixes; its original standalone patch remains available. No production source, browser build, or real index was changed by packaging.

Independent native/WPT reviews now accept both [safe-scroll](../css-flex-safe-scroll-origin-review-v1/REPORT.md) and [collapsed-item overflow](../css-flex-collapsed-scroll-overflow-review-v1/REPORT.md). Root authenticated the sealed reviews and adopted their native decisions. Their full formal companions remain open, so neither increments the accepted-pending count yet.

Active work: implement the complete twelve-obligation safe-scroll source/consumer proof; finish collapsed allocation's F11/F12 joins with the separately accepted baseline-sum prerequisite; independently review sentinel v3's indexed lifecycle, machine arithmetic and sequential update joins. Producer self-review is not counted as independent review. The shared browser build remains restored with all repairs.

## Latest checkpoint: seven accepted repairs awaiting signed commits

Counts: **87 committed native/WPT fixes; 7 accepted pending**. The geometric
sticky-sentinel repair now has [root acceptance](../css-sticky-sentinel-proof-root-v3/ACCEPTANCE.json)
after independent v3 review: 167 producer audits, 10 independent kernel checks
and identical canonical, relocated and root replay streams. The original
conditional positional-consumer contract includes indexed sequential updates
and both-coordinate machine operations. Geometry/provider freshness, upstream
limit construction, compiler correspondence and actual overflow delivery remain
explicit premises; range/timeline consumers are separate.

The multiline flex cross-size sum candidate passes all 144 paired WPT cases
against 96 failures and 48 passes. Its regression run has 914 passing subtests,
20 passing reftests, six OK harnesses and one known-intermittent failure in
`content-height-with-scrollbars.html`; that file has no paired baseline result.
Build, scoped formatting and WPT lint pass. Independent review remains open,
so this candidate is excluded from the accepted count. Earlier per-item sums
and downstream packing arithmetic remain separate obligations.
[Candidate report](../css-flex-line-cross-sum-fix-v1/REPORT.md).

Collapsed-allocation v2 is a sealed producer checkpoint with 419 audits and 91
native cases; root adoption is pending. Full F11/F12 still have provider and
row-strut edge-policy gaps. Work continues in v3 without narrowing those targets.
The full twelve-obligation safe-scroll companion remains in progress.

The latest user-requested signing retry failed with `1Password: failed to fill whole buffer` (exit 128). HEAD remains `92a6fddf18e5828b17d7491a34663a0d5a9c12ad`; all 297 staged paths and content hashes still match the prepared recipe. Signing remains enabled.

## Latest checkpoint: eight accepted repairs; two new reproduced leads

Counts: **87 committed native/WPT fixes; 8 accepted pending signing**. The wrapped
line-size sum repair now has [root acceptance](../css-flex-line-cross-sum-root-v1/ACCEPTANCE.json):
21 freshly checked kernel results and three negative/axiom controls, plus root
recounting of all 144 paired WPT results and both standalone patch round trips.
The one metadata-known intermittent regression remains explicit. Both this fix
and the geometric sticky fix now have complete preceding evidence/formal and
separate two-file native commit recipes. The staged signing snapshot is intact.

Two distinct leads now reproduce identically in release and the shared build:

- [Cross-axis packing arithmetic](../css-flex-cross-packing-boundary-probe-v1/REPORT.md):
  ten failures among 48 calibrated rows. Safe alignment moves the first item far
  from its expected start when large lines or gaps overflow the packing budget.
  A 64-row follow-up preserves reverse-wrap controls; simple early lower clamping
  would break already-defined cancellation. The complete wide-coordinate design review is authenticated and recommends exact
  64-bit propagation; no native repair has been applied.
- [Natural-baseline donor selection](../css-flex-natural-baseline-donor-probe-v1/REPORT.md):
  eight failures among 24 rows, all removal/restoration and geometry controls
  passing. An ordinary 160x80px flex box shifts 34px when an empty 5px item masks
  a natural text baseline. This is separate from collapsed-item donor exclusion
  and the unresolved strut-only edge-line specification question.

Collapsed-allocation v2's 147 source inputs and 234 receipt files are authenticated
as a producer checkpoint. Full F11/F12 remain open; v3 continues the original
sixteen obligations. The safe-scroll proof retains all twelve obligations and
keeps the newly reproduced packing failure separate from its policy repair.
Next: review the relative-baseline companion, finish the scroll-provider proof/repair, and resolve the natural-donor prerequisite before restoring native acceptance,
finish the implemented wide packing candidate’s source/formal review, including
final-coordinate, sentinel and downstream fragmentation obligations, and continue the full twelve/sixteen-obligation consumer proofs.
The latest user-requested signing retry failed; no further retry is planned
without a change in signer readiness.

## Checkpoint: relative baseline formal acceptance

Counts: **87 committed native/WPT fixes; nine accepted pending signing**.
The relative-position baseline companion is accepted under its explicit provider,
property-lifetime and numeric premises. [Its commit queue](../css-flex-relative-baseline-commit-v1/QUEUE.json)
contains separate evidence, review and formal companions followed by the two-file
Gecko/WPT patch. Completed root compiler products (3,787,976 bytes) were removed.

Next: finish the scroll-provider source/theorem review and natural-donor prerequisite
resolution; complete packing v2 arithmetic across fragment coordinates, metrics
and cumulative storage. Full safe-scroll twelve-obligation and collapsed-allocation
sixteen-obligation work continues. The latest requested signing retry failed;
HEAD and the 297 staged evidence files remain unchanged.

## Checkpoint: scroll-provider formal acceptance

Counts: **87 committed native/WPT fixes; ten accepted pending signing**.
[Root acceptance](../css-scroll-baseline-provider-proof-root-v2/ACCEPTANCE.json)
covers the complete conditional scroll-provider method, including early legacy
synthesis, containment, absence, coordinate conversion, clamp and numeric bounds.
Its [commit queue](../css-scroll-baseline-provider-commit-v1/QUEUE.json) preserves
separate evidence/review/formal companions and one two-file native/WPT fix.
Completed root compiler outputs (5,015,200 bytes) were removed.

Next: finish packing v2 correlated fragment bounds and storage design, then
implement and replay the full regression/verification gates. The native consumed-size
provider uses unchecked signed32 accumulation; its actual range is an explicit
caller obligation, not an assumed saturating helper. The natural-donor patch
remains withdrawn until its semantic prerequisite and independent-landability
requirement are resolved. Full safe-scroll and allocation milestones continue.
Signing remains blocked, with the original297 staged snapshot intact.

## Checkpoint: forced-break final-fragment lead

Counts remain **87 committed native/WPT fixes; ten accepted pending signing**.
The latest user-requested retry again failed in1Password; HEAD and the297 staged
evidence files remain unchanged. There are now six unaccepted candidates/leads;
the new lead is not counted as a distinct accepted bug.

The [40-case fragment probe](../css-fragment-consumed-size-probe-v1/REPORT.md)
and WPT retain the rejected packingv1 failures (29PASS/11FAIL). Normative review
clarifies that flex's exact fragmentation algorithm is unspecified; do not turn
the informative sample algorithm into a universal exact-coordinate claim.

A [forced-break reduction](../css-fragment-forced-break-probe-v2/REPORT.md)
uses only80px items yet reproduces eight oversized final fragments and misplaced
following siblings among24 cases, identically in release and the shared build.
The focused WPT has16PASS/8FAIL and passes lint. Six kernel results establish
ideal cancellation and show why premature size caps are insufficient. Exact
consumed-size extraction reports signed overflow with the observed fragment
sizes atO0/O2; no full browser-state trace or repair is claimed. All generated
executables and temporary browser profiles are removed.

Next work, in order:

1. Join packingv2's fragment coordinate recurrence with the real consumed-size
   provider and final content-minus-consumed observer. Preserve all passing tiny-item
   forced-break cases as well as the original defined packing controls. The new
   observed failures remain a required integration gate, not a hidden out-of-domain
   exception. Do not cap cumulative totals before their cancellation.
2. Implement the reviewed representation only after its branch/API bounds are
   settled, then build and run paired WPT/targeted regression and source proofs.
   Preserve the original full packing obligation roster and independent patch scope.
3. Continue safe-scroll's twelve and allocation's sixteen obligations. Current
   agents are joining placement/overflow/snap and parent publication/frame-cache
   identity respectively; provider freshness and full F11/F12 remain open.
4. Resolve natural-donor semantic dependency/independent-landability before
   restoring native acceptance. Resume signed commits after signer readiness changes.

## Checkpoint: runtime fragmentation diagnosis and restoration

The [runtime trace](../css-flex-fragment-consumed-trace-v2/REPORT.md) confirms the
forced-break failure route on32 complete selected fragment reflows. Consumed
and cumulative sizes become negative; growth processing yields zero, and final
subtraction emits an oversized block size. Four DOM rows exactly match the
uninstrumented baseline. The temporary logging is removed and the original
source/build, HEAD and staged index are verified restored. The initial failed
logging compile is retained separately; both successfulv2 builds have zero
compiler warnings and the existing mach monitor exception remains explicit.

Seven new kernel results establish residual-size placement, update and optional
min/max translation identities, with two rejected false claims. These do not
yet close machine bounds or the complete emitted-size/cache recurrence. The
next repair design must preserve actual source metric ordering: row forced-break
processing may push an item after its extent contributed to child-end metrics.

The independent design agent is comparing normalized displacement with exact
portable wider accumulation, while deriving residual observer bounds. No native
implementation has been accepted. Safe-scroll's twelve obligations and allocation's
sixteen continue; the latter has a new parent-publication/cache-identity producer
checkpoint, with lifecycle and full F11/F12 still open. Counts remain87 committed
fixes, ten accepted pending signing, and six unaccepted candidates/leads.

## Checkpoint: independent publication replay and cache producer gap

The [root publication review](../css-flex-publication-root-review-v1/REPORT.md)
freshly compiled all60 checkpoint modules, checked60 exact standard-axiom audit
results and rejected four producer false claims. Fourteen independent kernel
checks and three rejected false claims cover cache ordering, publication status,
sentinel edges and cancellation. The completed31,422,768bytes of compiler
outputs were removed; all104 retained payload files are authenticated.

Source review found that final cache installation receives the actual child's
reflow-input padding and indefinite flag, while measuring-reflow reuse receives
item fields. The prior publication model had not derived equality of those
producers. The lifecycle agent is separating them before closing the stateful
interleaving proof. This is a model/source admission gap, not a new browser bug.
Full safe-scroll twelve-obligation and allocation sixteen-obligation targets
remain unchanged, with F11/F12 still open.

Packing design now has a tested portable128 exact-provider approach and a
separate justified cap for the child-growth observer under review. Integration
must read actual predecessor content sizes, skip true overflow containers before
cache lookup, preserve previous-continuation versus previous-in-flow semantics,
and keep tentative/final/physical conversion bounds explicit. No v2 production
patch is applied or accepted yet. Next: review the complete recommendation and
implement only once those source joins are settled.

Counts remain87 committed native/WPT fixes, ten accepted pending signing, six
unaccepted candidates/leads. The latest requested signed retry failed again;
HEAD and all297 staged paths/content pins remained unchanged.

## Checkpoint: writing-mode WPT and actual shared-provider reachability

The [expanded reduction](../css-flex-fragment-writing-mode-probe-v1/REPORT.md)
now covers144 cases across three writing modes, both directions and row/column
flex layout. Release and project raw observations are identical. The expanded
WPT has96 PASS/48 FAIL with all failures at the following-sibling assertion;
lint is clean. Independent reference boxes preserve eight controls that would
otherwise be misclassified due to CSSOM rounding. Initial development runs and
the corrected numeric-origin calibration are retained.

The [new diagnostic trace](../css-flex-consumed-caller-trace-v1/REPORT.md) confirms
that the shared consumed-size helper overflows in a block ancestor before its
flex child. A flex-only bypass cannot eliminate that executed overflow. Both
logging/restoration builds succeed; eight DOMrows match the uninstrumented
baseline; original source/build/HEAD/index are restored.

The sealed [v3 design](../css-flex-cross-packing-design-proof-v3/REPORT.md) prefers
exact portable128 fragment totals. Root has authenticated its166 payloads/source
roles and reviewed the recommendation, without claiming a full root replay or
implementation acceptance. A real retained-source prototype is now comparing
a capped legacy signed32 prefix cache with a separate exact flex cache. The
cache-free child-walk option was falsified by quadratic read counts. Next: finish
actual source-slice/type calibration, compile a reversible candidate, and run the
144-case gate and full prior packing/fragmentation controls before acceptance.

Allocation lifecycle work has a new66-module/45-audit producer checkpoint; root
review remains pending. Safe-scroll's final machine/consumer composition and
closed replay are progressing. The original twelve/sixteen obligations remain
open. Counts stay87 committed fixes, ten accepted pending signing, six unaccepted
candidates/leads. No further signer retry without changed readiness.

## Checkpoint: percentage-padding measurement cache

The F11 freshness audit yielded a new ordinary-size browser failure: changing
a flex item’s percentage padding leaves its baseline alignment one update behind.
Release and project builds agree on four discrepancies among eighteen cases;
the new WPT reproduces fourteen passes and four failures. A focused cache-key
repair built successfully; candidate tests and a separate Lean companion are
in progress. See [repair evidence](../css-flex-padding-measurement-cache-fix-v1/REPORT.md).
Counts remain87 committed and ten accepted pending signing; seven unaccepted
candidates/leads are now tracked. Full twelve/sixteen-obligation work continues.

The latest user-requested signing retry failed with the same 1Password error;
HEAD and all297 staged file hashes remain unchanged. All36 queued recipes
passed preflight checks of15,335 file pins. No unsigned commit was attempted.

## Checkpoint: percentage-padding cache repair accepted

Counts: **87 committed native/WPT fixes; 11 accepted pending signing; six
unaccepted candidates/leads**. The new ordinary-size baseline repair adds actual
logical border/padding to the measuring cache key. Paired WPT results change
from 14 PASS / 4 FAIL to 18 PASS; the final formatted build passes 20 subtests
and seven reftests. The two-file patch applies independently to HEAD and the
retained upstream base. No isolated upstream runtime is claimed.

[Root acceptance](../css-flex-padding-key-root-review-v1/ACCEPTANCE.json) follows
independent native/WPT review and a fresh scoped Lean/native replay. The
[commit queue](../css-flex-padding-key-commit-v1/QUEUE.json) places evidence and
formal companions before the separate Gecko/WPT commit. Root removed 1,000,832
bytes of completed compiler products; the shared browser build remains.

The broader safe-scroll review found missing joins from actual child reflow
output sizes and from mixed-axis/definite-single construction. Its twelve
obligations remain open, with corrections proceeding in a new version. The
allocation sixteen-obligation effort also remains open; this cache-key fix
does not establish universal provider freshness. Next: build the sealed exact
fragment prototype, preserve all packing/fragmentation gates, and continue
those source/provider joins. Signing is still blocked; the staged snapshot
remains intact.

The expanded queue passes all 39 recipe checks and all 11 native patch
apply/reverse steps in a disposable index. HEAD and every hash in the real
297-file staged snapshot are unchanged.

## Checkpoint: exact fragment prototype clears observed regression

The first exact-fragment integration fixed final-size failures but introduced
24 vertical-rl item-position failures. A [revised local experiment](../css-flex-fragment-exact-build-v2/REPORT.md)
lower-bounds the temporary border-box block size at zero while preserving exact
cumulative arithmetic. All 634 core observations now pass, including all 144
forced-break cases. Across 48 files, the run passes 2,404 subtests and 27 reftests,
with 21 OK harnesses. Candidate and restoration builds succeed with zero compiler
warnings; the known mach monitor exception remains recorded. Original source,
shared browser build, HEAD and staged index are restored.

This is not native acceptance. Root freshly replayed the [physical review](../css-flex-fragment-physical-composition-review-v1/REPORT.md),
which keeps actual callback geometry, both-coordinate intermediate bounds,
relative/sticky offsets, finite sentinel handling, overflow containers and
placeholder/abspos observers open. Dedicated shifted-item and fragmentation
controls are next, alongside the full original packing/provider/cache obligations.
The existing abspos controls do not establish fragmented placeholder correctness.

The [independent safe-scroll review](../css-flex-safe-scroll-origin-proof-independent-v2/REPORT.md)
replays 49 modules and 386 exact axiom audits but holds full F1–F12 composition:
actual returned/current frame sizes must reach the observer, constructor and
mixed-axis branches need coverage, and the machine suffix must use the same
producer path. Corrective v3 work continues. Allocation's original sixteen
obligations remain open, including callback/dirty/cache coherence; protocol
counterexamples are not counted as browser bugs.

Counts remain **87 committed fixes; 11 accepted pending signing; six unaccepted
candidates/leads**. The latest explicitly requested signed retry again failed in
1Password; all 297 staged paths and hashes remain unchanged. No retry was made
during the fragment experiment. No unsigned commits or pushes occurred.

### Relative-position preservation and branch-calibration follow-up

The [paired relative-offset experiment](../css-flex-fragment-exact-build-v3/REPORT.md)
passes all 1,296 candidate observations: 144 baseline flow failures become passes,
and all 432 item-position plus 432 restoration controls remain passing. The full
candidate run covers 49 files with 3,700 passing subtests, 27 passing reftests and
22 OK harnesses. Both builds succeed; original source/build and staged snapshot
are restored. This adds relative-offset evidence without closing universal
physical arithmetic or the full fragmentation scope.

Two separate branch probes exposed an invalid test assumption: nested tiny
children did not each enter a new column, for either `always` or `column` break
values, including small controls. All release/project raw results match. The
[abspos](../css-abspos-fragment-cumulative-probe-v2/REPORT.md) and
[overflow-container](../css-flex-overflow-container-probe-v2/REPORT.md) capsules
retain those negative calibrations. They establish neither a new bug nor execution
of the intended overflow path. Next: trace the native fragmentation-state guards
and use a calibrated construction or tall unforced content. A separate abspos
cumulative signed32 source lead remains unconfirmed at runtime.

Allocation now has a 73-module producer checkpoint with clean-cache coherence
and whole-memory callback publication, while actual callback trace/getter/lifetime
and full F11/F12 obligations remain open. The agent removed 71,197,664 bytes of
superseded compiler products, retaining active dependencies. Counts are unchanged:
87 committed fixes, 11 accepted pending signing, six unaccepted candidates/leads.

### New ordinary-size overflow-container lead

Tall-content probes now reach a useful fragmentation shape. The
[16-row overflow-container probe](../css-flex-overflow-container-probe-v3/REPORT.md)
returns identical release/project observations: all eight horizontal controls
pass, while eight vertical-rl cases differ, including four with ordinary 160px
columns. Descendants are displaced by 160–560px in the small cases. Reference
geometry and restoration pass. The source's tentative versus final width accounts
for the small-case displacement; independent source/spec review and a standalone
repair/WPT are in progress. No fix is accepted yet.

The [48-row abspos probe](../css-abspos-fragment-cumulative-probe-v3/REPORT.md)
preserves all child rectangles but produces one extra fragment in twelve large
spanning cases. Attribution between shared consumed-size and distinct abspos
cumulative arithmetic remains open, so this is not yet counted separately from
the fragmentation lead. Earlier failed forced-break calibrations remain retained.

The [32-row actual-provider probe](../css-flex-actual-provider-probe-v1/REPORT.md)
disconfirms the predicted table residual-placement error in the repaired build.
The source audit must explain why the table's used size is already accounted for;
it must not assume flex basis equals actual output. Release's eight reverse-safe
failures match the previously known safe-origin issue, with 24 unchanged controls.

Counts: **87 committed fixes; 11 accepted pending signing; seven unaccepted
candidates/leads**. Source/build remain restored and all browser profiles are
removed. No new signer attempt, commit or push occurred.

### Standalone overflow candidate and exact-size provider counterexample

The [standalone overflow-container candidate](../css-flex-overflow-container-fix-v1/REPORT.md)
passes all 336 paired WPT observations: 112 failures become passes and all 224
previous passes remain passing. Its two-file Gecko/WPT proposal applies and
reverses on retained HEAD independently of the wide cumulative arithmetic patch.
The [lifecycle diagnostic](../css-flex-overflow-lifecycle-runtime-v1/REPORT.md)
passes all eight candidate stages, correcting seven baseline failures through
normal/overflow transitions and continuation deletion/regrowth. No repair is
accepted on these results alone.

The [first branch trace](../css-flex-overflow-container-skip-trace-v1/REPORT.md)
contains 12 reflow visits and no skips. The [external resize trace](../css-flex-overflow-external-resize-trace-v1/REPORT.md)
then changes only an outer sibling's width. All eight candidate stages pass,
but all 24 eligible helper visits still reflow: exact frame identity joins show
column MarkSubtreeDirty reaching the flex parent, including 18 column children
that were clean before marking. This rules out that proposed clean-skip route;
it does not prove universal skip safety. Next are the remaining fragmentation
entry paths, source/formal ordering review, and focused regression gates.

The [24-row float round-trip probe](../css-flex-provider-roundtrip-runtime-v1/REPORT.md)
confirms a separate provider limitation. Fractional large reversed flex items
retain approximately 1 or 2 app units of origin residual even with the safe-origin
repair; explicit reversed flex-start controls show the same residual in release
and project builds. Integer controls are exact. This refutes the exact provider
join for those inputs and remains attached to the full safe-scroll F1–F12 work.
It is not yet an additional accepted spec bug. The goal remains exact containment;
a tolerance theorem does not close it. Next is preserving resolved app units
through sizing without changing aspect-ratio, table, fragment or min/max semantics.

Allocation's agent has sealed a 74-module ordinary callback checkpoint, with
actual source guards and native calibration; full F11/F12 remains open, especially
table ancestry, later special reflow, and cache freshness. Root review of this
new checkpoint remains pending. The agent removed 133,403,112 bytes of completed
compiler products while retaining active dependencies.

Counts remain **87 committed fixes; 11 accepted pending signing; seven unaccepted
candidates/leads**. The user-authorized signer retry v11 failed with the same
1Password error. All 39 prepared recipe inputs still match their pins; the exact
297-file staged snapshot and HEAD are unchanged. Both new native experiments
restored source and browser build; all temporary browser profiles are removed.
No unsigned commit, push, or new acceptance occurred.

## Overflow positioning acceptance and next validation (20 October)

**87 committed fixes; 12 accepted pending signing; seven unaccepted candidates/leads.**
The new accepted repair positions flex overflow-container children with the final
fragment size. Its 336-case WPT fixes 112 failures and preserves 224 passes;
34 existing regression file outcomes are unchanged (24 PASS, 10 expected FAIL).
Root replay, ordering review, actual-path formatting, WPT lint and final build
passed. The two-file native patch has separate preceding evidence and formal
recipes in [the queue](../css-flex-overflow-final-position-commit-v1/QUEUE.json).
The fix is installed in the local source and build.

[Root acceptance](../css-flex-overflow-root-review-v1/ACCEPTANCE.json) is bounded:
normalized list/continuation invariants remain source premises; universal clean
skip correctness, callback/geometry providers, wide arithmetic and full fragment
composition remain open. It does not accept the earlier wide packing prototype.

A separate initial relative-positioning defect is under paired native/WPT
validation. Fresh layout and a position-only update disagree at identical final
styles; independent ordinary horizontal controls reproduce it. The candidate
uses predecessor normal inline position and applies each continuation's own
relative offsets. Its 140-case WPT also tests nonzero-to-double and return-to-zero
updates. This candidate is not counted among accepted repairs yet.

The ordinary allocation component passed a fresh root 74-module replay, ten
audits, two semantic false claims, native cases and mutations. This closes a
conditional component only; full allocation F11/F12 remains open. The table
warm/fresh diagnostic passed all 24 cases in both browsers. Source inspection
explains why that probe changes its computed-size cache key; a caption variant
is ready to test a different path. The new table source checkpoint awaits root
review. See [ordinary root review](../css-flex-allocation-ordinary-root-v1/REPORT.md).
Completed root replay outputs were removed (36,110,328 bytes), with source,
commands, receipts and active build dependencies retained.

The latest requested signing retry (v12) failed with the same 1Password error.
HEAD and all 297 staged files remain pinned; no unsigned commit or push occurred.
Next: finish the relative-positioning browser pair and source/provider proof,
then review exact resolved-length transport and the table-caption cache probe.
Keep the original full verification requirements intact.

### New caption lead and relative-position candidate result

The separate relative-position candidate corrected **30 failures among 140 WPT subtests**
while preserving 110 passes. Thirty-five retained regression files were unchanged
(including all 336 final-size WPT subtests); both builds passed and source/build
were restored. RTL and non-flex caller regressions plus independent review are
running before acceptance. See [paired evidence](../css-overflow-relative-position-runtime-v1/REPORT.md).

The table-caption followup found **four discrepancies in 16 cases**, identical
in release and project browsers. Auto-height caption plus percentage table height
retains the old size after a containing flex height change; fixed-height caption
and literal table height controls pass. All initial, restoration and repeat
controls pass. This is a new unaccepted lead, with source/cache attribution and
repair pending: [evidence](../css-flex-table-caption-runtime-v1/REPORT.md).

Current counts: **87 committed; 12 accepted pending signing; eight unaccepted
candidates/leads.** All 42 prepared recipes were hash-checked, and all 12 accepted
native patches apply and reverse in order in a disposable index. The real staged
snapshot remains unchanged. The natural-donor queue remains blocked on its
semantic provider dependency; it is not part of the accepted stack.

## Accepted relative-position and table-caption repairs (20 October)

Current counts: **87 committed native/WPT fixes; 14 accepted pending signing;
six unaccepted candidates.** Each new repair has a separate two-file native/WPT
recipe preceded by evidence and formal commits:

- [Relative overflow positioning](../css-overflow-relative-position-commit-v1/QUEUE.json):
  30 failures corrected in the140-case standalone WPT; supplementary RTL suite
  corrects60 of280 cases, preserving prior passes. Existing35/61 file outcomes
  stay unchanged, with expected failures retained. Root fresh replay passes33
  kernel audits and source/native/mutant checks. The formatted patch changes only
  one tested argument-list line break. Full seven-part lifecycle scope stays open.
- [Captioned flex-table percentage height](../css-flex-table-caption-commit-v1/QUEUE.json):
  four failures corrected in16 WPT cases;354 other subtests pass, and sevenPASS/
  oneexpectedFAIL table reftest outcomes are unchanged. Root fresh replay passes19
  audits, four semantic falseclaims and384 native cases in15 runs. Actual
  containing-block size joins the measuring key. The two-stage stale-plan witness
  keeps fresh-provider assumptions explicit. Standalone upstream patch has no
  padding-key dependency; the queued stack patch has the same two additions and
  WPT with context reflecting the earlier padding-key repair.

Both passed independent native review, actual-path formatting and WPT lint.
The combined local install/build/four-WPT run is tracked in
[installed state](../css-overflow-caption-installed-v1/STATE.json); it restores
prior source/build on failure. No signed commit or push has occurred. The latest
signer retry remains v12, with HEAD and the297-file staged snapshot pinned.

The table observer component now has a fresh root manifest-only replay:23audits,
four semantic negatives,14bindings and646 native cases in3modes. It proves the
stated ancestry/scheduling/propagation component only. New root replay cleanup
removed1,401,112 bytes there and1,229,192 bytes for the caption key; source,
commands, raw output and active dependencies were retained. Producer caption
replays separately removed3,687,576 bytes of their owned terminal products.

Next: independently review exact app-unit override transport before full native
integration, then continue the actual cache-pointer/dirty-recovery lifetime join.
The exact-size prototype has seven files,30 kernel results and52 extracted checks;
its38-case WPT remains unexecuted. It preserves the existing coordinate cap and
costs16 additional bytes in the measured arm64 override bundle; full virtual-output,
fragment and ratio/min/max semantics remain review gates. No tolerance theorem
replaces the original exact safe-origin F1–F12 requirement. Full allocation
F1–F16/F11/F12 and full fragment observer composition remain open.

### Installed build checkpoint

The combined build completed successfully and all **510 subtests in four WPT
files passed**. Relative overflow positioning and captioned-table percentage
height are now installed alongside the earlier final-size and padding-key
repairs. [Integration evidence](../css-overflow-caption-installed-v1/REPORT.md)
pins the exact source/tests and binary. All14 accepted native patches applied
and reversed in order in a disposable index;48 recipes were checked. Signing
remains enabled, HEAD is unchanged, and the297 staged files still match their
original snapshot. Counts remain87 committed/14 accepted pending/six unaccepted.

## Exact-size transport and recovery checkpoint (20 October)

The first full seven-file exact-size prototype experiment passed: candidate build
exit0, draft38 cases26PASS/12FAIL→38PASS, and all510 existing subtests preserved.
The57 reftest outcomes remain44PASS/13expectedFAIL. Source and build were restored
successfully; the prototype is not installed or accepted for landing. See
[paired experiment](../css-exact-size-transport-runtime-v1/REPORT.md).

The independent recovery checkpoint passed root relocation:63modules,31audits,
three false claims,1,024 extracted native cases in three modes and three semantic
mutants. Recovery follows prior nested cache writes and invalidates in place.
Actual callback-path/heap representation, observer closure and owner survival
remain open. Root removed33,529,896 bytes of terminal replay products.
See [root review](../css-flex-cache-recovery-root-v1/REPORT.md).

Next in order:

1. Run the prepared144 supplemental browser diagnostics paired against the
   exact-size prototype, retaining all240 observed/fresh stage records. Calibrate
   signed-caption source-policy tests separately from normative alignment checks.
2. Complete signed table arithmetic and source-admitted caller bounds. Individually
   bounded negative margins can still exceed the subtraction domain; extracted
   witnesses alone do not establish actual browser reachability or a new bug.
3. Derive actual ordinary-block output and current/primary/continuation ownership
   relations, then extend to remaining frame families and observer paths.
4. Continue the original full safe-originF1–F12, allocationF1–F16/F11/F12 and
   fragment observer obligations. Coordinate caps and fragment cases remain in
   scope; successful transport or a conditional component does not close them.

The nonmeasuring table static audit found no new counterexample. Ordinary column
and orthogonal tables can still measure through automatic minimum sizing; absence
of a final-cache field alone is not a bug. The diagnostic remains unexecuted.

Counts remain87committed/14accepted pending signing/six unaccepted. Requested
signing retryv13 failed with the same1Password error; HEAD and the297-file staged
snapshot remain unchanged. No unsigned workaround, push or CI run occurred.

## Signed caption reachability and block output (20 October)

The signed-table domain correction passed fresh root replay:51 audits,34 native
rows per variant, semantic mutations and expected UBSan domain failures. It retains
signed occupancy and checks each executed intermediate, rather than treating
negative margins as natural numbers. Full caller/output coverage remains open.

Browser tracing now distinguishes two routes. Fixed-basis extreme negative-caption
fixtures never enter the reducer. Auto-basis flex growth does: actual720Mau minus
negative1.44Bau reaches mathematical2.16Bau, outside signed32, and the traced build
returns0. This matches the earlier extracted UBSan witness. A safe signed32 control
also returns a tiny table through a separate Q-as-auto conversion, so final geometry
alone is not an overflow oracle. The repair and a discriminating WPT remain open;
no new fix is accepted. See the [growth trace](../css-exact-size-signed-caption-grow-trace-runtime-v1/REPORT.md).

The ordinary-block output checkpoint passed independent root relocation:24 kernel
audits,867 native rows at each of O0/O2, four false claims and three semantic
mutations. It derives both returned dimensions for admitted unfragmented stretched
ordinary blocks. Actual dispatch, stable border/padding/cross policy and completed
child-state restrictions remain explicit. Non-stretched frames, other frame types,
cache/move paths, physical observers and full F1–F12 remain open. See
[root block review](../css-exact-block-output-root-v1/REPORT.md).

Independent cache-owner review identified a missing native relation: destruction
uses a cached primary-frame bit while the model tests content-primary pointer
equality. The twenty logical results remain valid conditionally; native admission
needs cached-bit/pointer coherence, including setter callbacks. Normalization and
continuation reparenting phase invariants remain active. Full F1–F16/F11/F12 is open.

The paired144 supplemental diagnostics plus38 original transport tests are running
in css-exact-size-supplement-runtime-v1. Baseline completed182 subtests with all48
fixture collections complete; final candidate/restoration results are pending.

Next: finish that paired run and inspect raw measurements; test a calibrated
observer for signed-caption repair; close primary-owner coherence and the next
ordinary-block caller admission. Preserve all original cap, fragmentation and
lifecycle requirements. Signing retryv14 failed; HEAD and297 staged files were
verified unchanged. Counts remain87 committed/14 accepted pending/six existing
unaccepted repair candidates, with the newly reached arithmetic finding separately
under investigation. No push or CI run occurred.

### Supplemental result and observer corrections

The paired experiment is terminal and the original source/build restored. Combined
results are122PASS/60FAIL→150PASS/32FAIL, with no PASS→FAIL transitions. All38
original cases pass. All48 supplemental calibration and48 fresh/update checks pass;
remaining failures are28 table diagnostics and4 image geometry checks. Each variant
retains240 stages,240 fresh peers,80 explicit references and96 small controls.
See [paired supplement](../css-exact-size-supplement-runtime-v1/REPORT.md).

Do not classify those32 outcomes as32 defects. Independent source review found the
original table reconstruction assumed an inner-table-only DOMRect, whereas Gecko
includes caption boxes in the bounding union. Correct that observer in a successor
while preserving these inputs/results. Every candidate image sample's main/cross
size and end coordinate exactly matches its explicit reference. A source-shaped
float-conversion calculation reproduces the residual with exact native geometry;
actual native integer path admission remains needed. Preserve the full exact
observer requirement rather than increasing tolerance or waiving remaining checks.

The signed-caption percentage observer produced14 identical rows in installed
Firefox and the restored project build. Auto/zero reference vectors coincide in
both profiles; this is negative calibration, not a regression oracle. The reached
signed subtraction remains established by the earlier trace. The25-audit widening
companion compares Q and INTMAX caps explicitly; independent review is running.
No arithmetic repair is installed or accepted. See
[observer calibration](../css-table-signed-reduction-observer-runtime-v1/REPORT.md).

Next priorities:

1. Bind CSSOM frame collection and float coordinate conversion to a correct
   observer; reduce a non-flex geometry case and trace native integer edges before
   proposing a separate repair. Keep table-caption union and replaced sizing distinct.
2. Finish independent review of widened subtraction/cap preservation and choose
   appropriate direct regression coverage; do not infer visual improvement from
   removing undefined arithmetic or treat Q as an ordinary finite size.
3. Review the normalization checkpoint and close cached-primary-bit/pointer
   coherence, pair-list readiness and actual callback ownership joins. The new18
   producer results exclude specific column/paginated interrupt paths conditionally,
   not all ways to reach a continuation state. Producer cleaned3,136,248 bytes.
4. Continue full safe-origin F1–F12, allocation F1–F16/F11/F12 and fragment observer
   obligations, including non-stretched and other frame classes. Earlier bounded
   block/output and recovery components remain components, not completion claims.

The48 recipes/14 accepted native patches passed the disposable-index check after
checkpoint updates. No new accepted fix or signed commit;87 committed/14 accepted
pending/six existing unaccepted repair candidates remain. Signer retryv14 is still
the latest attempt. The original297-file staged snapshot is preserved.

### Minimal rectangle discrepancy reproduced

The follow-up observer probe completed 56 identical records in installed Firefox
and the restored project build, with every ResizeObserver callback delivered.
Four small non-flex controls report an edge of 100px. Four large plain boxes
(horizontal/vertical, padded/unpadded) report a bounding edge of 100.015625px while
a zero-size marker at the same edge reports 100px. No flex, table, image or authored
transform is required. getBoxQuads is unavailable under defaults, so no corner-API
measurement is claimed. See [observer isolation](../css-exact-size-observer-runtime-v1/REPORT.md).

Source-shaped numerical replay reproduces the discrepancy from perfect native
geometry through float rectangle conversion. This supplies a concrete next repair
candidate, but complete ancestor/viewport/zoom/SVG admission and actual integer
path binding still precede native acceptance. A separate narrow repair/WPT proposal
is underway; no original exact observer requirement or failing assertion is waived.

The signed-reduction independent review accepts the bounded arithmetic component:
25 producer audits, 11 independent checks, native mutation/UBSan controls and eight
guards pass. It does not accept a production cap policy or observable CSS repair.
INTMAX preserves all old signed-defined publication arguments; source percentage
analysis supports the negative observer result while retaining internal zero/Q
branch differences. Full table, IEEE conversion and caller/lifecycle joins remain
open. All runtime source/build restoration is complete; signing/index state and
accepted-fix counts remain unchanged.
