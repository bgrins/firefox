# Independent scratch-publication formal review

Date: 2026-10-19. Recommendation: accept the conditional publication component.
No substantive blocker was found. The native/browser repair has a separate
independent review; this report does not enlarge either acceptance boundary.

## Authentication and fresh replay

Producer `css-declaration-publication-proof-v1` FREEZE is
`ccadac40732e9de66705ac9b6331af767be04b8e69a6d5ea5fd07123e478998d`;
MANIFEST is `2e8ed98ebbefbf49e2a4067a6544e1c0e96f2ffe44f57decaf06032dc282ee1e`.
All 235 input files were independently authenticated before producer execution.
The copied 201-file discovery closure retains its original seal and is separately
authenticated by the producer checker.

I read the complete model, all 29 proofs, exact theorem roster, source-generation
script, complete native facade and driver, source bindings, replay and integrity
checkers. A fresh manifest-only copy under /private/tmp replayed successfully:
29 exact standard-axiom audits; five Rust variants with 16 observations each;
four semantic mutation witnesses. All compile and execution commands succeeded.
The five independent shadow/model/symlink/duplicate/path-escape controls rejected
before output creation. Retained evidence records the actual failures, not only
producer assertions. The source closure contains no binary/rlib/olean inputs.

## What the universal proofs establish

`Scratch` separates ordered declarations from optional all-shorthand payload.
`repaired` follows the branch control of the helper, including abandoned ordinary
success. `direct` selects the accepted callback result without appending that
abandoned state. The reference therefore does not use repaired as its definition;
it shares the typed callback outcomes and fallback-acceptance provider boundary.
`refinement` proves the complete Outcome equality for every modeled Action.

This equality covers ordinary success without observation, CSS-wide success,
observed-success replacement, ordinary failure with fallback, and failed fallback
with cleared abandoned storage. Ordered declaration content and the all field
are preserved exactly for the chosen expansion. Empty append and the actual
clear of both fields justify the replacement proof; it is not merely a theorem
that declaration counts decrease.

`publication_exact` and `failure_unpublished` derive the published option.
`canonical_publication` and `every_publication_canonical` transfer the explicit
`admitted` premise: the chosen expansion has unique mapped identities and no
ordinary entries when all is present. They do not prove all generated callbacks
produce canonical expansions. The nonvacuous replacement example demonstrates
that this premise can hold with different abandoned and selected values.

Trace/history/prefix theorems quantify arbitrary finite lists of independent
actions. `runNative` stores the latest accepted transaction result and preserves
it on rejection. It does not model CSSOM merging, importance/logical ordering,
removeProperty, shared parser state, or mutable callback histories. No complete
native CSSOM invariant follows from the fold theorem alone.

The abstract drain atomically returns a complete snapshot and empty scratch.
Actual drain returns a borrowed iterator and moves the all field. Its native
witness consumes/drops that iterator before checking emptiness. The producer
explicitly added this distinction before sealing; partial-drain behavior, Rust
borrowing and ownership lifetime are outside the theorem.

## Source mapping and observations

Exact root candidate properties source is
`2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d`.
The extracted helper adds only clear after the successful callback's
no-observation early return. The independent native/WPT review establishes that
this is the root's tested source. Complete SourcePropertyDeclaration and its
implementation/drain record are now extracted, in addition to the complete
helper, LinkParameters and actual VariableValue providers. All 21 definition
records are preserved in the fresh replay.

Source admission is explicit: entry scratch is empty; longhand and generated
shorthand callbacks push only after successful parse_entirely; failure leaves
scratch empty; wide/fallback callbacks supply the chosen expansion; outer errors
do not publish. I inspected the relevant complete source and generated wrapper
paths in the separate native review. Fallback Option models observation,
structural validation and VariableValue success together. Their byte-level
correctness is not proved by this model.

The native gate has thirteen actual LinkParameters/VariableValue inputs, two
synthetic successful callbacks followed by real rejected var syntax, and a drain
fixture. Four real duplicate scratch outputs become a single fallback; nine
real controls are unchanged. The synthetic all state is deliberately not a
claim that the real all property can take that successful parser path. The
actual all callback always errors without mutating scratch.

The facade replaces ArrayVec with a capacity-128 Vec, declarations with tags,
and all payload with a marker. Its tested states fit capacity. Actual enum
layout, allocation, destruction, pointer ownership and real maximum expansion
are not verified. Atom/URL/Arc representations, ASCII DashedIdent and untyped
attr are supplied adapters; the derived from_ident mapping is handwritten.
Typed attr and general CSS-wide grammar are outside the fixture set. Direct
cssparser compilation disables fast_match_byte and fast_match_color; it is not
a feature-matrix proof. Compiler and standard-library behavior are trusted.

The full target source bodies are read and bound, but their model translation
is reviewed correspondence plus finite native evidence, not a machine-checked
Rust semantics refinement. Eighteen prior extraction records and three new
storage records are source-hash evidence. Mutated generated code intentionally
retains the baseline extraction provenance and is distinguished by variant;
those hashes do not falsely establish mutant bodies as unchanged production.

## Mutation adjudication

| Variant | Native observation | Kernel distinction |
| --- | --- | --- |
| omitted clear/original | Actual var parameter yields ordinary plus fallback | omission and noncanonical duplicate |
| declarations-only clear | Synthetic all callback plus actual fallback rejection leaves all | retained all differs from empty |
| fast-path clear | Actual none loses ordinary result | no-observation result must survive |
| after-publication clear | Actual var parameter loses accepted fallback | replacement must survive |

All native mutants compile and run successfully. Each witness compares semantic
outputs, not compilation errors. The Lean witnesses also compile successfully
as counterexample theorems; they are not failing Lean mutation builds. The
abstract same-ID payload and native representation tags are complementary
views of the same loss/duplication mechanism, not an executable equality of
these different representations.

## Remaining scope and packaging

This component closes the modeled exclusive-publication contract conditional
on its supplied outcomes. Full tokenizer/cache observation, every generated
property grammar, callback canonicality, ArrayVec allocation/drop semantics and
CSSOM storage lifecycle remain separate obligations. The original larger formal
project is not marked complete. No additional browser defect or security claim
is inferred from synthetic witnesses.

Run this review's `python3 -I -S check.py` after authenticating its freeze. It
checks both closed rosters, exact fresh proof audits, source/mutant observations
and tamper receipts without importing producer modules. For a fresh source
replay, authenticate producer and run its `python3 -I -S check.py --output
/absolute/new/output`. Rust/Lean executables are pinned; their installation and
standard libraries remain external toolchain dependencies.

COMMIT-INVENTORY.json lists the exact 237-file producer roster and review
roster. Producer embeds its discovery source closure; no temporary output or
mutable root directory is required. Native/WPT packaging remains the separate
two-file repair already independently reviewed.
