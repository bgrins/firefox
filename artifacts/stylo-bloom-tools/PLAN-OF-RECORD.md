# CSS and Stylo verification plan

Updated 19 October 2026. Work stays local; the user owns pushing.

## Current status

- **72 committed native/WPT fixes.** The management index is
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md); exact commits, standalone alternatives
  and limits are in [CURRENT-COMMITS.json](CURRENT-COMMITS.json).
- **Latest repair:** explicit inheritance of guaranteed-invalid registered values,
  signed as `3a01fc986c7974161aadf4bfafe65c234b036b07`, after evidence
  `2e0f9f6b9ee5450cd21ac9341ef116dd91a8119b`. Three failures repaired; the
  two-file commit contains only the Rust change and WPT.
- URL native state/capture, ordinary batching, parser-priority winners, animation
  identity and primary parser-history admission are accepted within scope. Public
  parser wrappers and storage composition remain active.
- Signing works. Nothing has been pushed or submitted externally.

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
enable sites. The wrapper producer is sealed (57 modules / 448 audits, 77 new) and independent
fresh replay/review is active; nested/depth/callback protocols and
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

1. Repair substituted-inherit restyle dependency tracking. Two numeric browser
   cases reproduce stale child values; direct-inherit and unset controls pass.
   Native review is active. Add an absent-parent transition control, run paired
   builds, and commit only the native change plus WPT after review.
2. Independently review the sealed skip/next wrapper proof and production entry
   model. Then compose the declaration helper's saved-query/short-circuit paths;
   metadata, providers, callbacks and compiler admissions remain explicit.
3. Audit persistent custom-property map iteration. A descendant-shadowing loop
   is a source lead, not yet an observable bug; derive chain reachability before
   adding a browser test or counting a repair.
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
