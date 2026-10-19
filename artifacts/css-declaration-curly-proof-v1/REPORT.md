# Whole-value curly validation companion

Date: 2026-10-19. This is a conditional component-level proof plus finite
extracted-helper agreement. It is not a proof of the whole CSS parser, all
native property parsers, or native compiler correctness.

## Result

- 27 Lean theorems compile and receive an explicit kernel axiom audit. No
  additional axioms, admitted goals or native decision oracle are used.
- The independent specification permits a noncustom declaration to have no
  top-level curly component, or to consist of exactly one such component.
  Arbitrary nested children are retained in the recursive component grammar.
- The native-shaped full scan satisfies that predicate for every finite
  projected component sequence. Rewinding validates the same whole value
  regardless of the complete component prefix consumed by the callback.
- A concrete suffix-only scan counterexample succeeds where the structural
  specification rejects. The repaired scan rejects it. Custom properties,
  whole-curly values and nested block contents retain their exceptions.
- Six compiled helper configurations execute 57 observations each: original,
  candidate and four semantic mutants. Eighteen forbidden gateways in the
  original become zero in the candidate. Four real executable differences have
  corresponding successful Lean counterexample witnesses.
- Exact candidate source is bound to root's final browser capsule: 24 failures
  become passes, all 89 subtests pass, 41 existing subtests are unchanged, and
  five harnesses report OK. Browser/build work was done by root.

Discovery came from static source inspection and browser confirmation. The
formal component followed discovery.

## Definitions and theorem boundary

`Component` distinguishes trivia, atoms, functions with child values and simple
blocks with delimiter kinds and child values. `significant` removes top-level
trivia and maps each remaining complete component to `Head.other` or
`Head.curly`; it never flattens children. `normalSpec` is independently defined
as a quantified absence of curly heads or exact singleton equality.

`scan` preserves the helper's starts-with-curly and at-start state, including
early rejection. `scan_false` and `scan_true_after` establish its state
invariants for arbitrary remaining lists. `full_refinement` proves both
directions against `normalSpec`; `component_refinement` lifts this to recursive
component lists. Projection concatenation/trivia and nested-content theorems
make the top-level distinction explicit.

`Recovery.consumed` and `Recovery.remaining` contain **complete projected
components**. They do not represent arbitrary byte cursors, cached tokens or a
partially traversed pending block. `arbitrary_recovery` and
`arbitrary_cursor_independence` quantify over these component partitions only.
The complete original value can be recovered regardless of the modeled split;
the native reset-to-saved-state connection is an admitted source bridge below.

`gateway_refinement` composes structural validation, a retained positive
substitution observation, and a separate arbitrary-value validity result.
`invalid_never_published` applies to this fallback gateway. It does not prove
complete property publication for arbitrary native callbacks. Ordinary callback
success needs the separate premise that the accepted property grammar meets
declaration-level syntax. `ordinary_success_unchanged` is only the unchanged
literal branch fact, not a proof of that provider premise.

`disabled_after_positive` and `failed_epoch` distinguish a saved positive query
from current tracking state. They prove Boolean retention, not byte-level cache
observation completeness. The separate accepted cache-epoch audit is relevant
prior work; it is not imported as a theorem about this new whole source hash.
Our assumptions remain explicit rather than silently reusing its source binding.

`scanSteps` follows the scan's invalid/early-return branches and counts modeled
top-level visits. `scan_step_bound` proves at most the number of significant
components. This is not a bound on native tokenizer steps, bytes, nested-block
visits, allocation or runtime. Reset adds a consumed-prefix rescan only on
error/fallback paths; normal successful parsing retains its early return.

## Exact source and native execution

The frozen static audit is copied and authenticated under `evidence/audit/`.
Its complete original helper is byte-identical to the helper retrieved through
Searchfox. All 128 vendored inputs matched the inspected tree, including the
accepted parser-depth recovery correction. The complete current cssparser
crate and dtoa, dtoa-short, itoa and smallvec are freshly compiled from retained
source; Cargo and prebuilt artifact libraries are not used.

The final full `properties/mod.rs` is retained as `candidate-properties.rs`.
Its SHA-256 is
`6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92`.
The checker verifies whole-file equality to the original with precisely the
new reset and related comment update. It also verifies equality with root's
final browser candidate. The complete helper is compiled in every variant;
mutants change the named semantic sites in that helper, not a replacement
implementation of it.

### Provider inventory and limits

| Provider | Retained / executed boundary |
| --- | --- |
| cssparser parser/tokenizer/cache/block cleanup | Complete crate compiled. Fast-match optional features are disabled as in the seed capsule; core parser behavior is actual source. |
| Noncustom fallback helper | Complete byte-exact original/candidate function compiled with type adapters. |
| Property callback, single/comma modes | Identifier acceptance projection using actual `parse_entirely` / `parse_comma_separated`; real FontFamily and SingleFontFamily sources are retained but not compiled as complete Stylo types. |
| Successful callback mode | Injected callback consumes the stream and succeeds, explicitly exercising saved-query disabling. It does not establish a production property that reaches this branch. |
| VariableValue parser | Accepting facade. Native rows assert reaching the fallback gateway, not complete declaration acceptance. The real scanner is retained and inspected; browser tests bind the simple admitted values end to end. |
| CSS-wide keyword / declarations / namespaces / URL | Small named adapters. Only `initial` is recognized by the facade; declarations record markers. No whole native storage/serialization theorem. |
| Independent native syntax oracle | Counts top-level components through a fresh parser. It does not reuse the helper's error cursor or starts flag; tokenizer/block-skip implementation is a shared admitted provider. |
| Browser outcome oracle | CSS Syntax consume-declaration rule, CSSWG 9317, custom/whole-curly exceptions; original and candidate raw records pinned independently of the model. |

The compiler, standard libraries, OS, allocator and hardware are trusted
execution dependencies. Toolchain executable hashes are checked. This capsule
does not vendor or verify the compiler/toolchain libraries.

### Counts and mutants

There are 19 values in each of three callback modes, hence 57 harness rows per
variant and 342 total. Thirty-eight rows per variant use the single/comma
provider projections; 19 are injected successful-callback contract tests.
These are harness rows, not complete Stylo consumer invocations. Of the 18
original forbidden gateways, nine use the comma provider and nine the injected
success provider; none use the single parser. The candidate has zero.

| Compiled mutation | Concrete witness | Successful kernel witness |
| --- | --- | --- |
| Omit the new rewind | comma callback, `serif {var(--x)}` reaches forbidden fallback | `suffix_only_counterexample` |
| Reject every top-level curly | comma callback, `{var(--x)}` loses a legal gateway | `reject_whole_mutant_witness` |
| Ignore structural invalid flag | comma callback, `serif {var(--x)}` reaches forbidden fallback | `ignore_structure_mutant_witness` |
| Query but discard the positive result | injected success callback, `var(--x)` loses fallback classification | `lost_positive_query_mutant_witness` |

All four modified native helpers compile and run. Each row is compared with the
candidate and differs in the claimed gateway result. The Lean witnesses
successfully prove the counterexample rather than treating a type error or
unrelated failed compilation as a semantic kill. They concern the corresponding
abstract policy, not a mechanically proved compiler translation.

## Explicit admissions for a stronger native theorem

1. Native bytes/tokenizer output project to the finite recursive component
   grammar with the correct treatment of comments, whitespace, EOF, malformed
   closing tokens and nested delimiters.
2. `Parser::next` skips exactly one complete pending block and exposes the next
   top-level component; saved `start` is the post-initial-whitespace state.
   Reset restores position and pending-block state even after an error cleanup,
   while the enclosing parser retains its stop delimiter. This includes cursors
   inside a component. The model's partition theorem
   does not discharge this raw-state relation.
3. Tracker queries, resets, cache replay and production entry states provide the
   admitted saved/seen values. Our successful injected callback tests the helper
   branch but is not a universal tracking/provider proof.
4. The real `VariableValue::parse` supplies the independent arbitraryValid
   result; this must include malformed substitutions, bad tokens and nesting
   limits before claiming complete acceptance. The facade supplies no such proof.
5. Ordinary successful property callbacks satisfy syntax and publication
   premises; custom properties use the separate exempt path. CSS-wide keywords,
   importance validation and error scratch cleanup retain their real callers.

These admissions are exposed in the current scoped result. No full byte/native
lowering or complete CSS conformance is claimed. The prior audit gives source
inspection and negative findings beyond this narrow contract.

## Replay, closure and handoff

Authenticate MANIFEST and checker against the externally supplied FREEZE hash,
then run `python3 -I -S check.py --output /tmp/new-proof-output`.
All executable/source inputs are authenticated before executing helpers. The
isolated interpreter excludes sibling modules; exact-roster, duplicate/path
escape and symlink checks reject malformed capsules. Replay outputs must be
new and outside this artifact. `tamper.py` exercises changed-source, shadow
module, symlink, duplicate-record and path-escape rejection before replay starts.

Canonical and relocated source-only runs, axiom audit, native mutation receipts
and tamper results are retained under `receipts/`. No binary/rlib/olean is in the
commit roster. Commit all paths in MANIFEST plus MANIFEST and FREEZE. Frozen
earlier artifacts are unchanged; production/build/browser/Git remain root-owned.
