# Reusable parser lowering with complete-state rollback

The existing typed parser IR now has a generic, checked lowering into an additive
effect backend. The theorem covers every parser shape and all seven constructors,
preserving returned values and complete state on success and restoring the
original state on failure. Consume-number is an instance of that theorem.

Here `State` consists of unread scalar input and the accumulated error flag.
The old backend and source IR remain unchanged. The new backend adds old-program
embedding, state read/write, and sequencing. Source parser trees remain data-only;
the lowering generates the backend's continuations.

The central contract is:

```lean
run (lower parser) state = observed state (ParserIR.run parser state)
```

`observed` maps source success to the same value and final state, and source
failure to `(none, state)`. Atomic failure is an explicit strengthening: the
source interpreter exposes no state on failure. `observable_lowering` separately
erases backend failure state and recovers the source interpreter's exact result.

`take`, `nonempty`, `pair`, and `right` use complete-state transactions. A failed
right-hand parser therefore rolls back earlier left-hand consumption. `optional`
uses the child's atomic failure contract to return successful absence with the
original state. An error raised inside a failed child is rolled back too, while
an already-set incoming error survives.

Maximal scans use the old bounded scanner with exactly the current input length,
connected by the existing maximal-scan and scanner-lowering lemmas. No independent
cap, arbitrary fuel, new loop instruction, or number-specific opcode is added.

## Number instance and limits

`number_parts` preserves the existing lexical parts, exact remainder and prior
error flag. `number_execute_equal` and `number_relation` connect the lowered result
to the original exact-number implementation and independent `NumericResult`
relation. `number_ready` retains the `StartsNumber` caller premise.

The numeric projection remains unchanged, separately proved ordinary Lean. Its
significand/scale, integer-versus-number type flag and optional sign are not
compiled into a new first-order arithmetic language. The type flag is not a
validity flag. Machine floating point, browser precision and native parser
refinement are outside this artifact.

This closes a previously missing reusable lowering edge. The previous number
interpreter already had a direct proof; there was no unchecked number compiler
to replace. JSON decoding/emission and the reviewed English-to-tree mapping
remain separate boundaries. The original translator refusal and declaration of
number as development material are retained.

## Validation

Lean 4.35.0-rc4 accepted 229 audited declarations, including 18 new laws. The
generic `lowering_correct` theorem depends only on standard `propext`; the complete
inventory admits only the standard `propext`, `Quot.sound`, and `Classical.choice`.
There are no admitted proofs or additional axioms.

Twenty-eight executable observations cover failed and successful reads, maximal
scans, complete error rollback, prefix-sensitive nested optionals, pair/right
ordering, old error effects and escape programs, exact number values and suffixes,
and explicit negative zero. Two observations are labeled off-domain total-model
behavior rather than valid CSS caller input.

Six type-correct mutations are rejected by the unchanged generic laws and exact
false semantic witnesses:

* Keep a child-raised error while rolling back the input.
* Omit pair-level rollback after left-side consumption.
* Cap a maximal scan at two characters.
* Clear the error flag when embedding an old effect.
* Treat optional failure as fatal.
* Invert the predicate-read condition.

The capped-scan and fatal-optional witnesses execute the lowered number instance;
the other witnesses isolate generic state/effect behavior. No witness imports a
failed new proof module. Three additional controls reject changes to the old
backend, source parser, and pinned CSS bytes.

The initial driver attempt classified an example label ending in `error:` as a
compiler diagnostic. The detector now recognizes actual diagnostic line syntax;
the successful model, proofs and expected observation vector were unchanged.

## Inputs and replay

Nineteen necessary Lean dependencies are copied unchanged from the number-transfer
artifact; `PRESERVED.json` and `ORIGIN-CHECK.json` bind them to their original bytes.
The dependency closure includes two previously generated escape programs as
pinned reference sources. No new source generation occurs here.

The unchanged [CSS Syntax snapshot](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs)
and its exact consume-number, digit and caller clauses remain pinned by
`SOURCE.json` and `CLAUSES.json`. Hash checks do not prove English interpretation.
`MAPPING.md` describes the lowering and source boundaries.

From the Firefox repository root:

```sh
python3 artifacts/css-parser-lowering-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-parser-lowering-20261110-v1/review-replay
```

The output directory must not exist. Replay copies exactly 36 source inputs into
a fresh temporary directory and removes its objects afterward. The canonical
library, previous artifacts, native sources, WPTs, browser, and Git state are
unchanged. No allocation, stack, performance, native-memory-safety, or broader
spec-coverage claim is made.
