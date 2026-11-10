# First-order typed IR: what assurance does it buy?

2026-11-10. This directory is an isolated successor to the checked stateful escape artifact committed as `191083fb76eb`. No earlier artifact, canonical library, Firefox code, shared objdir or Git index/history was changed.

## Result

The prototype provides a **data-only typed expression/statement syntax**, a direct interpreter and a lowering into the previous effect IR. Lean proves that lowering preserves the returned value and complete input/error state for **every well-typed program, environment and initial state**. Escape consumption is an instance, with a separate proof connecting it to the previously checked `CssEscape` relation.

This meaningfully reduces one trusted boundary: state and local-variable handling in lowering is now checked once for the whole admitted IR, instead of being justified only for one generated escape program. It does not eliminate the reviewed English-to-AST interpretation, the pure primitive semantics or the JSON emitter from the trusted workflow.

Both the ordinary run and a clean source replay passed. Twelve controls distinguish those boundaries, including a shared arithmetic defect for which the universal lowering theorem **still passes**, while the independent escape bridge and concrete witness fail. That result is expected and important: preservation of an interpreter's meaning does not establish that the meaning is CSS-correct.

## The bounded core

[FirstOrder.lean](FirstOrder.lean) defines five value types: natural numbers, Unicode scalars, Booleans, scalar lists and unit. Expressions contain literals, typed variable references, arithmetic/comparisons, conditionals, list construction and a natural-number fold. Statements return expressions, bind local values, read with EOF/present branches, scan a bounded prefix, raise an error, or branch.

No `Expr`, `Stmt` or `Var` constructor contains an arbitrary Lean function. A fold's step is another expression tree with two bound locals. Scan predicates are expression trees with a bound candidate scalar. Locals use typed de Bruijn references: the nearest binding is index zero, and a reference must carry the type present at its context position. The interpreter's environments contain values from the five admitted data types, not function values.

The backend still uses the earlier higher-order `Program` representation. The new `lower` function creates its continuations systematically; those continuations are no longer unconstrained payloads supplied by the generated AST. Its statement-level environment/state transformation is the object of the universal proof.

[Reusable.lean](Reusable.lean) contains small programs outside the escape template: reading a scalar's numeric code, summing the first two scalar codes, and shadowing a local while retaining the older value. A universal shadowing lemma and examples check empty/short input, residual input and an already-set error flag. These demonstrate basic reuse of the core, not generalization across the CSS specification.

There are no general loops, mutable maps, native pointers, exceptions or numeric-token semantics. Bounded scanning and folding over a finite list terminate by construction. The core is deliberately small rather than a general-purpose specification language.

## What is proved universally

[Lowering.lean](Lowering.lean) proves:

```lean
theorem lowering_correct (program : Stmt Γ t) (env : Env Γ) (state : State) :
  run (lower program env) state = interpret program env state
```

The theorem quantifies over arbitrary typed contexts and result types, not just closed scalar programs. The state includes unread input and the accumulated error flag; the theorem is not restricted to a fresh false flag. Its bounded-scan helper is proved for all budgets and scalar lists. The proof uses induction over statements and a separate scan induction. Its audited axiom dependency is standard `propext`.

Direct interpretation and lowering are distinct implementations of statement execution: one updates state/environments directly, while the other constructs effects interpreted by the older backend. Pure expression evaluation is deliberately shared. Consequently this is a statement-lowering theorem, not a proof of independent expression compilation, English interpretation, native execution or every possible optimization.

## The escape instance and the remaining boundaries

[generate.py](generate.py) reuses the pinned prior source recognizer and checks that its extracted parameters match the prior checked parameter record. It builds [generated/escape.json](generated/escape.json), a constructor tree with source mappings, then emits [GeneratedFirstOrder.lean](generated/GeneratedFirstOrder.lean). The emitted Lean contains only constructor expressions and named expression-tree aliases; it imports the new IR and contains no reference-parser calls or function payloads.

[FOBridge.lean](FOBridge.lean) separately proves the meanings of the generated class, fold and replacement expressions, then proves equality with the older escape program. The final relation is:

```lean
theorem escape_relation (source : List Char) (result : Result) :
  execute escapeTree source = result ↔
    CssSemantics.CssEscape.Escaped source (toReference result)
```

The preserved fields are the output character, exact remainder and EOF error. The lowered escape program has the same correspondence through the universal theorem. These instance proofs depend on standard `propext` and `Quot.sound`; the driver rejects unexpected audits, including `sorryAx`.

The English-to-tree mapping is still reviewed code. In particular, the meaning of maximal bounded scanning, one optional terminator, hexadecimal positional arithmetic, inclusive scalar bounds and error behavior comes from the earlier reviewed interpretation. The older relation belongs to the same research project and may share conceptual mistakes. Its separate construction and prior existence provide a useful comparison, not an independently normative formal specification.

The Python JSON emitter is also unverified. It accepts a fixed constructor schema and emits Lean data constructors; Lean checks the resulting types and scopes. A wrong *in-scope variable of the same type* still typechecks, so the semantic bridge remains necessary. The generic lowering theorem alone also accepts an incorrectly selected AST and faithfully preserves its wrong meaning.

The syntax is structurally serializable and an actual JSON representation/emitter is implemented. The driver tests a Python JSON encode/decode round trip and deterministic emission for this artifact. **There is no proved typed-AST serializer/deserializer round trip, and no verified JSON-to-Lean decoder.** JSON is an external, untyped representation until the emitted Lean constructors are checked. This distinction limits the claim of reduced lowering trust.

## Source traceability and caller obligations

The source snapshots and older proofs are retained under `prior/`, with hashes in [PRIOR.json](PRIOR.json). The pinned specifications remain [CSS Syntax at `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs) and [Infra at `c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a`](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs). No fresh draft or new held-out generalization is claimed.

[CLAUSES.json](CLAUSES.json) links seven selected operative clauses to AST JSON pointers and exact source-byte spans. [source_links.py](source_links.py) checks each target pointer and extracts each source match uniquely. The links themselves are manually chosen. Referenced character definitions retain their own source spans in the AST's `source_map`; the full body and parameters are retained too. These links make interpretation review easier; they are not semantic proofs.

The earlier metadata limitation remains: exact note/WPT-inventory checks cover the algorithm body, while dependency-definition note/WPT blocks are stripped generically from operative text. Their full source bytes are pinned, but unfamiliar definition metadata is not independently refused. The first-order syntax does not repair that source-recognition gap.

The caller-facing `ready_escape` theorem retains the prior `CallerReady` predicate: normalized scalar input and a validated escape observation. The input interface separately assumes that the backslash was already consumed; the predicate does not encode or prove that cursor history. An initial LF is excluded; EOF is permitted. Raw DOMString surrogates are outside the `Char` domain, so the scalar-list preprocessing model does not prove code-unit decoding/surrogate conversion. The current/next-input relation is an explicit list abstraction, not a proved native tokenizer cursor/reconsume adapter. Total behavior outside that caller domain remains model behavior rather than a CSS conformance claim.

## Controls and what each one establishes

[RESULT.json](RESULT.json) and [check.log](check.log) record the ordinary run. Nine escape examples, the reusable programs and the following twelve controls passed:

| Group | Change | Observed check |
| --- | --- | --- |
| Wrong but well-typed AST | Use the terminator local instead of the hex-digit local | Escape bridge and `41!` witness fail |
| Wrong but well-typed AST | Consume a seventh hex digit | Escape bridge and residual-input witness fail |
| Wrong but well-typed AST | Remove EOF error | Escape bridge and empty-input witness fail |
| Wrong but well-typed AST | Reject the inclusive Unicode maximum | Escape bridge and maximum-value witness fail |
| Wrong lowering | Lose the read effect | Universal theorem and generic read witness fail |
| Wrong lowering | Lose the error effect | Universal theorem and generic error witness fail |
| Shared primitive defect | Evaluate multiplication as addition | Universal theorem still passes; escape bridge and concrete witness fail |
| Ill-typed data | Out-of-scope variable | Lean refuses the tree |
| Ill-typed data | Natural-number result where scalar required | Lean refuses the tree |
| Unsupported serialization payload | Unknown constructor | Emitter refuses it |
| Unsupported serialization payload | Extra executable-text field | Emitter refuses it |
| Source drift | Changed pinned CSS bytes | Generator refuses before emission |

Every semantic mutant first compiles as an implementation or typed tree. Each failing semantic claim also has a concrete witness whose proposition Lean determines is false; failure is not inferred solely from a brittle proof script. Mutant witnesses do not import a stale successful instance bridge. The shared-primitive control rebuilds both lowering and generated data against the modified evaluator before checking their outcomes.

## Is further investment justified?

Yes, selectively. This core makes state/local lowering reusable and universally checked, constrains generated implementations to an inspectable data language, and exposes small semantic differences as AST edits. It buys assurance for a specific layer; it does not automatically improve faithfulness to CSS prose.

The most useful next step is to reuse the core for a second small real algorithm, while auditing the pure primitive meanings and source mappings independently. If external JSON becomes the main interchange format, a Lean decoder with a typed encode/decode theorem would reduce the remaining serialization/emission boundary. Neither requires building a broad DSL now.

Number consumption would additionally need a compound value/type/sign result, decimal/exponent accumulation, multi-scalar lookahead, input-decreasing unbounded loops, and an explicit exact-value versus floating-point interpretation. Those additions are documented needs, not implemented or measured coverage. No numerical parsing or held-out experiment was added here.

## Clean replay

From this directory with the existing Lean 4.35.0-rc4 toolchain:

```sh
python3 -I -B check.py --lean /absolute/path/to/lean
python3 -I -B replay.py --lean /absolute/path/to/lean
python3 -I -B source_links.py
```

The clean replay passed using the **22 files** listed with hashes in [SOURCE-ONLY.json](SOURCE-ONLY.json). That allowlist includes older generated Lean/parameter records as pinned reference source, but no newly generated first-order tree/Lean, compiled files or prior test results. It rebuilds the reference and new proofs, regenerates the AST, and repeats all controls. [REPLAY-RESULT.json](REPLAY-RESULT.json) records copied inputs and outcomes. An independent reviewer can copy just that allowlist into a fresh directory and run its `check.py` with the absolute toolchain path.

Successful owned build/replay directories are removed. Failure removes the old acceptance record and retains the failed copy for inspection. No browser/native builds or tests were run, no Firefox bug was found, and no commits were made.
