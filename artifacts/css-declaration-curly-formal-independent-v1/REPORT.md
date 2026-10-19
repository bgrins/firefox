# Independent declaration component proof review

Date: 2026-10-19. Recommendation: accept the conditional component proof and
its bounded native bridge. No substantive blocker found. This is separate from
the accepted native/WPT repair and does not close the complete tokenizer or
declaration-parser proof scope.

## Selected theorem and independent reference

The model distinguishes recursive component values from their significant
top-level heads. Trivia is erased; a curly simple block projects to `curly`;
atoms, functions and other blocks project to `other`. Child lists are opaque
to this projection. That matches the selected structural question, including
curly blocks inside functions or square blocks, but it assumes correctly formed
component values have already been obtained from native input.

`normalSpec` is declarative: no top-level curly head, or exactly one curly head.
It is independent of the scanner's `starts` and `atStart` Booleans. `scan`
follows the existing helper's conditional checks and early rejection.
`full_refinement` proves equivalence for arbitrary finite head lists; the
recursive-component theorem composes this with projection. Empty values pass
this structural predicate, which is not a claim that an ordinary property
accepts an empty value.

The projection lemmas correctly keep trivia and child interiors irrelevant;
concatenation is preserved. Singleton curly, mixed curly, repeated curly and
custom-property exception theorems have the expected meanings. The custom
exception only concerns this structural gate, not validity of arbitrary custom
property contents.

## Recovery and native admission

`Recovery` contains a consumed list and a remaining list of complete projected
components. Its whole value is their concatenation. Rewind validates that whole
list and is independent of the chosen complete-component cut. The suffix-only
counterexample consumes `[other, curly]` and leaves nothing: the old suffix
check accepts but the structural reference rejects. The repaired rewind rejects.

This is not a theorem over every native byte cursor or pending-block state.
Native callbacks may stop inside a component or before pending-block cleanup.
The native source-to-component projection, reset equivalence, delimiter handling,
EOF/error recovery, and correspondence of a callback's native state with the
modeled Recovery remain admissions. The source pair and browser witness support
the selected repair; they do not discharge those universal byte-level premises.

## Observer gate and publication

The Boolean reference retains either a saved positive query or a current seen
flag. A positive saved value remains true after the native query disables
tracking, and an unsuccessful parse without such a saved value uses the active
seen flag. Gateway refinement combines that observer fact, structural validity,
and a separately supplied arbitrary-value validity result. The invalid-never-
published theorem concerns this modeled fallback gateway.

The epoch/cache history that produces the supplied Booleans is not derived by
this module. Actual helper reset does not reset the observer; the earlier cache
admission checkpoint is context, not automatically imported proof composition.
The ordinary success lemma only evaluates the fast-path Boolean. Its production
grammar validity remains an external provider contract. In particular, it does
not prove an arbitrary successful callback rejects forbidden curly syntax.

## Operational count

`scanSteps` mirrors the scanner's early rejection and charges one step per
visited significant top-level head. Its bound by list length is valid. It is
not a bound on byte tokenization, skipped child interiors, comments, native
allocations, or the cost of the property parser and subsequent substitution
parser. No machine performance theorem follows from this count.

## Mutation distinctions

The Lean module proves explicit concrete witnesses for omitted rewind,
rejecting a whole curly block, ignoring structure, and losing a saved positive
query. These are kernel-checked counterexamples about modeled alternatives.
The replay also compiles four modified complete native helper bodies and
compares their gateway observations to the candidate. These are separate
bounded native mutation gates, not universal native refinement or deliberately
failing Lean-mutant builds.

The positive-query native witness injects a callback that consumes all input
and reports success. It is a deliberate observer/control fixture, not a claimed
production font-family grammar path. Such a callback can ordinarily accept
invalid structures without a substitution and return through the unchanged
fast path. The suite checks fallback gateway safety; it must not be summarized
as complete declaration validity for those synthetic callbacks.

## Source and replay boundary

The complete original and final helper are bound to retained whole properties
sources. The only native delta is reset plus comment. The entire retained
cssparser and dependency source is rebuilt by the replay. The reduced callback,
CSS-wide keyword provider and accepting VariableValue adapter remain explicit.
Native rows and the independent browser review are different evidence layers.
Neither establishes compiler, heap, all generated property grammar, or full
substitution semantics.

## Authentication and fresh evidence

The final producer capsule has 222 authenticated inputs. External pins:

- FREEZE: `009cbbdf37ddaaffae96ecb226d2f8c529f5cc418b8656244cc5eed9314be847`
- MANIFEST: `1e173c8a0dd411d57ece94f5a2cbcf929bac5482a6e7b1678c5590b845dcfbdf`
- checker: `6e999f541a2241ef9f53e16dbcded37cba12751b645b611cdd51803a1aa014b7`

All manifest entries were authenticated before any producer script execution.
A manifest-only relocation under `/private/tmp/curly-formal-independent-v1`
then completed the full source-only replay with exit zero. It rebuilt the
actual retained cssparser and dependencies, compiled all six helpers, checked
all 27 exact theorem names, and produced standard-axiom audits only (`propext`
and `Quot.sound`, or no axioms). The source contains no added axioms, admitted
goals, `sorry`, or native decision oracle. All definitions and proofs were read.

The six native configurations each emitted 57 rows. Eighteen original forbidden
gateways become zero; nine original discrepancies use the comma callback and
nine use the synthetic success callback. The original single-parser controls
remain unchanged. All four compiled mutant witnesses differ in the intended
gateway result. In particular, losing the positive query still returns success
from the synthetic callback but loses fallback classification; it is not a
proof that native parsing should return an error in that fixture.

Five freshly executed tamper cases reject changed Lean source, a shadow module,
a symlink, duplicate manifest entries and path escape before replay output is
created. Their failures are integrity assertions, intentionally distinct from
the successful semantic counterexample proofs. The reviewer checker independently
validates the exact theorem inventory and audits, fixed-fixture structural
oracles and all four mutant observations from retained raw results.

The complete candidate properties source is
`6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92`.
It matches the final browser capsule and differs from the complete original
only by reset plus comment. The source wording was clarified before sealing:
reset restores tokenizer position and pending-block state; the enclosing parser
retains its stop delimiter. Stop state is not stored in ParserState. No theorem
change was needed for that clarification.

The native build uses direct rustc with optional fast-match features disabled.
This exercises the actual source fallback branches, not the Cargo default
configuration (which enables both fast-match features), and is not proof of
all crate feature combinations. Toolchain executables are hash pinned,
while their libraries, compiler behavior, OS, allocator and hardware remain
trusted. Python isolated/no-site execution and manifest authentication precede
all nested helpers. No production, browser, Mach or Git command was run here.

## Scope ledger and handoff

| Obligation | Review disposition |
| --- | --- |
| Full structural scan iff no curly or singleton curly | Proved over arbitrary finite projected head lists |
| Recursive children and trivia do not leak into top-level classification | Proved for supplied component grammar |
| Arbitrary complete-component prefix recovery | Proved; native partial-block and byte-state mapping admitted |
| Saved/query Boolean preservation and fallback publication | Proved conditional on supplied observer and arbitrary-value validity |
| Native tracker/cache histories and production entry | Source inspected; universal composition not established here |
| Ordinary-success grammar validity | External provider contract; fast-path literal fact only |
| Top-level early-return scan count | Proved; no tokenizer byte or machine-time bound |
| Complete actual helper and native mutations | Exact source compilation with explicit adapters; bounded observations |
| Actual VariableValue, generated property grammar and full storage | Retained source/browser evidence; not universally proved |
| Native/browser repair gate | Separately accepted in css-declaration-curly-independent-v1 |

No blocking gate remains for this component recommendation. Broader obligations
remain open with their original scope. Root owns final acceptance and commits.
`COMMIT-ROSTER.json` gives the exact producer and independent-review inventories;
temporary executables, rlibs and oleans are excluded. The producer already
contains its authenticated static audit and final browser closure, so those
copies need not be added again for this component.

Recheck: `python3 -I -S check.py`. Add `--replay /private/tmp/new-empty-path`
for a fresh manifest-only relocation and source replay. `--producer` selects the
authenticated producer directory when these capsules are relocated. The checker
does not read current live native sources or invoke a browser.
