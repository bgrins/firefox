# CSS and Stylo verification plan

Updated 19 October 2026. Work stays local; the user owns pushing.

## Current status

- **68 committed native/WPT fixes.** The management index is
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md); exact commits, standalone alternatives
  and limits are in [CURRENT-COMMITS.json](CURRENT-COMMITS.json).
- **One tested candidate awaits its formal companion:** CSSOM `all` shorthand
  ordering. The candidate is applied locally and built. Its native/WPT commit
  will follow the proof/tooling commit after formal replay and review.
- **Latest accepted proof checkpoint:** URL providers, signed as
  `1a67c0ab4a65227222ce5d3e553b84a2c5914f56`. This does not close full native
  tokenizer verification or increase the bug count.
- Signing works. Nothing has been pushed or submitted externally.

[Historical checkpoints](PLAN-HISTORY-20261019.md) preserve the previous plan
verbatim. Their counts, signing blockers, agent states and “next” sections are
historical observations. The current schedule is below; historical open proof
obligations remain open unless a later acceptance record explicitly closes them.

## In progress

### 1. Finish the all shorthand ordering repair

The special `all` path bypassed the ordinary logical-group ordering planner.
The final WPT baseline has sixteen failures: eight value-changing assignments
and eight equal-value assignments requiring reordering. A shared per-declaration
planner and sequential all executor repair them. The rebuilt candidate passes
all 40 new and 61 existing subtests; the other 89 outcomes are unchanged.
The same two-file patch applies and reverses on retained upstream; an isolated
upstream runtime has not been run. Independent native and spec review pass.

The test compares opposing-mapping pair order with fresh all expansion. It does
not choose an absolute canonical expansion order, which CSSWG issue 5741 leaves
unresolved. The relational expectation assumes a fixed order for the same
shorthand/provider context. Source discovery and browser reproduction preceded
the formal companion.

Remaining gates:

1. Prove the reverse-scan planner refines the independent forward setter.
2. Prove concrete declaration-vector, importance-bit and membership transitions,
   including planner-derived index bounds and public-boundary uniqueness.
3. Prove sequential all refinement and opposing-pair convergence under a fixed
   unique expansion. Connect the initial preparation gate to existence of a
   changing step, without equating it to final serialization inequality.
4. Replay complete extracted native control flow with explicit storage, payload
   and metadata adapters; discriminate semantic mutations.
5. Authenticate and replay the final source-only companion independently and at
   root. Commit that companion, the two-file native/WPT fix, then its ledger entry.

Evidence checkpoint: `8e546da543b28a053c2830f51df51d4007c6d75e`.
Browser evidence: `../css-all-logical-order-final-browser-v1/PAIR-CHECK.json`.
Native review: `../css-all-logical-order-native-independent-v1/REPORT.md`.
Proof production: `../css-all-logical-order-proof-v1/`.

### 2. Derive native URL metadata and raw slice behavior

The accepted component proves URL/bad-URL algorithms over modeled inputs and
checks finite native correspondence. The next component derives actual mutable
helper updates through the complete loops and captures the native slice
endpoints, addressing two specific remaining bridges.

Model modulo-2^32 line-start storage: four-byte UTF8 intros intentionally wrap
that field. Preserve packed block bits and state explicit shift/addition
headroom. Compose ordinary, continuation, newline, escape, borrowed/owned,
whitespace-end and bad-remnant steps with independent raw-prefix observation.
Derive slice ranges from full-input/remaining-suffix invariants. Keep codec,
allocation/lifetime, machine-domain and compiler premises explicit.

Production: `../css-tokenizer-url-native-state-v1/PLAN.md`.
Add a native case only for a concrete gap, such as the previously untested
bad-URL escaped-close-at-EOF raw endpoint. No new browser bug is established.

## Next, in priority order

1. Complete the two active components above and their review/commit gates.
2. Prove ordinary declaration batching: actual generated source uniqueness and
   one mapping kind per logical group, descending removals, rank correction,
   aligned importance and identity membership. The all-specific proof does not
   supply this batched theorem. A separate bounded exploration agrees in
   1,962,610 abstract cases and retains counterexamples when source uniqueness or
   mapping uniformity is removed; the universal proof remains open. See
   [batch proof obligations](../css-declaration-batch-admission-root-v1/PLAN.md).
   Extend to actual push/extend/removal sequences.
3. Compose public parser histories: byte-to-event admission, cache/reset,
   enable/query epochs, nested blocks and recovery. Preserve the cached-Function
   and URL annotation counterexamples. Cold/non-Function entry is a proved
   component premise, not a whole-caller proof.
4. Continue cascade source/observer and hyphenation stateful consumer admission,
   including actual reflow-to-display cache association and lifetime. Retain
   cycle/animation, scope-ownership and uncovered-cache counterexamples.
5. Use ranked spec/implementation audits to choose further semantic extensions.
   Validate observable discrepancies with a spec-derived oracle; unsupported or
   ambiguous behavior stays explicit. Existing breadth audits do not survey all CSS.
6. Use the [full-proof closure checklist](FORMAL-CLOSURE-CHECKLIST.md) to track
   unresolved universal/native obligations. Finite corpora, theorem counts and
   passing browser pairs do not close broader requirements.

## Accepted checkpoints

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
  Query/disable composition and actual byte-parser event generation remain open.
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
