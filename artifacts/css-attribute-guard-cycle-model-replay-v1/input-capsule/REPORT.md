# Attribute substitution guards and cycles

This standalone Lean artifact models the guarded-cycle distinction behind the missing/invalid non-type attribute fallback and nested raw-attribute cases. It adds explicit active contexts and cycle poisoning; it is not a renamed instance of the earlier acyclic demand-completion model. It is not a proof of Stylo, a parser, or browser conformance, and carries no canonical coverage or accepted-bug credit.

## Specification correspondence

The pinned CSS Values 5 ED is dated 27 October 2026. Its generic substitution algorithm guards a context, marks the contexts participating in a repeated-context cycle, and checks the cycle mark after replacement. Attribute replacement returns raw strings and valid primitive numeric/unit results before typed recursive substitution; missing/invalid primitives reach fallback substitution. Typed attribute substitution uses an attribute context. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [guards](https://drafts.csswg.org/css-values-5/#guarded), [attribute replacement](https://drafts.csswg.org/css-values-5/#attr-substitution).

The pinned Variables 1 ED dated 9 October 2026 requests a referenced property's computed value and substitutes its fallback only for a guaranteed-invalid primary. An inner fallback may produce tokens while its enclosing property remains marked cyclic; that enclosing guard must still reject the result. [var replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function).

`REFERENCES.json` binds the complete primary captures, both prior audits, the independent root trace, and the minimal non-type-fallback native proposal. The proposal supplies implementation motivation only; no refinement theorem connects the Lean evaluator to its Rust graph traversal.

## Executable model

`GuardCycle.lean` defines finite expressions for literal tokens, invalid values, variable lookup, raw/primitive/typed attribute replacement, and concatenation. The environment supplies property expressions and attribute records. Attribute records separately contain opaque raw text, a normalized expression representing parsed typed text, and the result of primitive parsing. Typed acceptance is another supplied predicate.

State contains an active context stack, persistent cycle marks, and a trace of attempted guards. Context keys distinguish properties from attributes even when their numeric name is equal. A repeated guard marks exactly the stack prefix through the nearest matching context. Earlier enclosing nonparticipants are not added. On normal return the guard restores its caller's stack and, independently of the inner returned tokens, rejects a marked context.

Raw reads produce one opaque string token and never inspect the supplied typed expression. Valid primitive reads likewise bypass typed recursion and fallback. Missing raw/primitive attributes and invalid primitive parses evaluate their explicit fallback in the existing enclosing context. Typed reads guard their expression, then apply the supplied acceptance predicate; failure selects the caller's fallback. The result type separates `value`, `invalid`, and `exhausted`, so a fuel limit cannot automatically activate a fallback.

The evaluator takes fuel to make recursive property/attribute environments executable without assuming acyclicity. General local laws quantify over fuel where applicable. Closed examples use fuel 64; their exact outcomes exclude exhaustion. This is not an unbounded termination or fuel-independence theorem.

Two non-default policy switches exist solely as faulty-machine controls: omitting the final guard check, and recursively interpreting raw contents. The specified model always uses the default policy. Eager fallback is represented by a separately changed expression, not silently enabled in the normal evaluator.

## Proof inventory

Thirteen general conditional laws cover:

- the exact cycle-participant slice and exact marking on reentry;
- invalidation on repeated context and on a final poison check;
- restoration of the caller's active stack;
- successful-value fallback exclusion and exhaustion distinct from invalid;
- present raw and valid primitive reads leaving guard state unchanged;
- missing raw and invalid primitive selection of the explicit fallback.

Twenty-three closed propositions use `decide +kernel`. They include missing-bare self and mutual property cycles; invalid and missing primitive fallbacks; all participants in a property/typed-attribute cycle; an independent outer consumer's permitted fallback; present raw and valid primitive exclusion of cyclic unused fallbacks; two nested typed attributes containing raw reads that remain literal; and typed-attribute-only cycles that do not poison an outer property. Separate counterexample theorems show the results produced by unchecked guard completion and eager raw traversal. A zero-fuel control returns exhaustion without inventing a cycle.

The audit prints axiom dependencies for all 36 declarations. The replay checks every expected declaration, permits only standard Lean axioms, and rejects warnings or sorryAx. Nine intentionally false claims must be rejected by kernel `decide` with its exact false-proposition diagnostic; parser errors or reduction failures do not count. Five diagnostic-gate controls test that rejection classifier itself. The companion replay's `CHECK.json` is the authoritative execution result and axiom inventory.

## Assumptions and limits

This is a normalized semantics. Nat names must be mapped coherently to an element's property and attribute identities; namespaces, dynamic names, shadow boundaries, and multiple elements are not independently implemented. The raw text and typed expression fields must represent the same underlying DOM attribute under the appropriate parse mode. Lean does not establish that correspondence. Opaque integer text codes in the examples stand for the concrete strings in the pinned traces; they are not CSS character codes or a serializer implementation.

Property inputs represent unregistered custom-property substitution values. The model does not implement registration, typed registered-value computation, inheritance/cascade/defaulting, animation taint, or pending keyframe providers. Attributes always have an explicit fallback expression in this subset; omitted-fallback defaults, first-argument parsing, spread syntax and malformed function argument grammars are outside it. Primitive and typed parsing results, tokenization, and immutable DOM/environment reads are supplied assumptions.

Attribute taint, URL provenance, resource loads, parser side effects, registration context conversion, and native attribute trackers are not represented. A native implementation must preserve those independently. The model's atomic property-guard boundary must correspond to the real computed-value/property-replacement route. Its explicit poison semantics need not match Stylo's SCC representation instruction-for-instruction; a future simulation/refinement proof would have to show equivalent participant invalidation and branch selection.

State is one substitution episode under a fixed environment. Cache reuse, changing DOM/registration state, concurrency, retries, and clearing marks between episodes are not proven. Lists encode sets of marks without requiring uniqueness; membership determines poisoning. The exact-slice theorem assumes no earlier matching key in the supplied prefix, as required for the nearest repeated active context.

These restrictions are deliberate and visible. The useful verified result is that the modeled guard discipline distinguishes a real fallback-mediated cycle from literal raw text, and that an inner successful fallback cannot rescue an enclosing poisoned context. It does not by itself certify the pending native repair.

## Replay

Use the pinned compiler through the wrapper, supplying the external digest of this artifact's `FILES.json`:

```sh
python3 -I -S -B artifacts/css-attribute-guard-cycle-model-v1/replay.py --manifest-sha256 <digest> --output /Users/bgrins/code/firefox/artifacts/css-attribute-guard-cycle-model-replay-v1
```

The output directory must not exist. The wrapper authenticates source/compiler/import/reference pins, compiles into its own temporary directory, records all positive and negative logs, audits axioms, and removes that scratch directory. It never uses the native objdir, edits canonical Lean, or runs a browser. The pinned compiler and direct Init import are trusted toolchain inputs; this is not a separately bootstrapped verification of the Lean toolchain.
