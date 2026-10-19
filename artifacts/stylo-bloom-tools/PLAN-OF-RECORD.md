# CSS and Stylo verification plan

Updated 19 October 2026. Work stays local; the user owns pushing.

## Current status

- **69 committed native/WPT fixes.** The management index is
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md); exact commits, standalone alternatives
  and limits are in [CURRENT-COMMITS.json](CURRENT-COMMITS.json).
- **Latest repair:** CSSOM all-shorthand ordering, signed as
  `074086719e445ca72d3056f7fbf793af5e69d6f6`, with preceding formal companion
  `bad8f7998dbbb3ad1fa88c0ca6892488f912e898`. Its two-file commit contains only
  the native patch and WPT.
- URL native-state review, ordinary declaration batching, and public storage
  composition are active.
- Signing works. Nothing has been pushed or submitted externally.

[Historical checkpoints](PLAN-HISTORY-20261019.md) preserve the previous plan
verbatim. Their counts, signing blockers, agent states and “next” sections are
historical observations. The current schedule is below; historical open proof
obligations remain open unless a later acceptance record explicitly closes them.

## In progress

### 1. Prove ordinary declaration batching

The all repair's sequential algorithm is accepted. The ordinary path plans all
actions against one initial destination, removes indices in descending order,
corrects surviving indices and executes source order. Its separate universal
refinement theorem remains open.

Root bounded exploration agrees with an independent sequential setter in
1,962,610 abstract cases. Removing source uniqueness or group mapping uniformity
produces counterexamples; neither fabricated source is a new browser bug. Three
initial kernel-checked helpers establish lower-lookup preservation and rank
subtraction bounds. These do not complete the batched theorem.

The producer reports a kernel-checked numeric batching refinement with descending
removals and index correction; independent review and native storage composition
remain pending. Its supplied comparator requires a true result to imply semantic
equality, while permitting conservative false results. The NaN source audit does
not establish a browser bug: CSSOM permits reporting an update when serialization
is unchanged. Native value equality must not silently become reflexive model
equality. [Audit](../css-cssom-nan-equality-static-v1/REPORT.md).

A root source audit checks all eight setter callers and the exact ordered metadata
for 94 ordinary shorthands. Five kernel-checked optional-publication lemmas preserve
unique identities, group compatibility and capacity; fresh local and relocated
replays pass. This does not mechanically compose the entire parser with batching.
Independent review accepted these limited claims after its own relocated replay.
Source interpretation, compiler behavior and callback stability remain explicit.
[Source admission](../css-declaration-source-admission-root-v1/REPORT.md).

Production now targets independent declaration/importance/membership storage
composition and native mutation checks, followed by review and scoped acceptance.

[Obligations](../css-declaration-batch-admission-root-v1/PLAN.md).
Production: `../css-declaration-batch-proof-v1/`.

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
The producer has sealed 17 new modules and actual native state/slice checks in
three modes. Independent review is running; root acceptance remains pending.
The fixed corpus adds only the escaped-close-at-EOF case and an unquoted leading
newline case required to reject a previously surviving bulk-field mutant. No
new browser bug is established.

### 3. Compose parsing, removal and clear

The root model now kernel-checks 26 lemmas for parser-priority push/extend,
separate storage operations, deletion target bounds, removal-loop safety, the
earliest-removal optimization, and arbitrary mixed parse/remove/clear histories.
Duplicate source identities are admitted for sequential extend. These histories
do not yet include CSSOM setting; native interpretation and caller stability
remain open. The immutable flag and changed-return bits are outside this model.

[Checkpoint and replay](../css-declaration-public-storage-proof-v1/PLAN.md).
Static caller review: `../css-declaration-public-operations-static-v1/`.

## Next, in priority order

1. Complete the active components above and their review/commit gates.
2. Extend declaration storage verification to actual push/extend/removal
   sequences. Bind parser output canonicality and source metadata to each public
   operation's premises; distinguish CSSOM setting from parsing priority rules.
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
