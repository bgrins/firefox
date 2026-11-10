# Substitution boundary

The pinned Variables Level 1 replacement algorithm is represented after name
parsing and custom-property computation. Names are natural-number identities;
`Binding.value = none` summarizes guaranteed-invalid. `Binding.animationTainted`
is an input, independently of the payload's attribute metadata. Payload tokens
are opaque natural numbers; no token grammar is claimed.

| Pinned clause | Model |
| --- | --- |
| Replacement step 2, computed value lookup | `Environment` supplies an already-computed binding. Name substitution/parsing, cycles and computation are preconditions outside this model. |
| Replacement step 3, tainted and not animatable | `available`; independent `Allowed` predicate in the declarative rules |
| Replacement step 4, invalid and fallback supplied | `evaluate` recurses only into a selected fallback; `Derives.fallback` states the independent rule |
| Replacement step 5, return result | Result value, with a diagnostic read trace added by the model |
| Infectious custom-property paragraph | `Infectious` closure parameterized by seeds and reference edges; no algorithm derives these inputs from CSS |
| Keyframe acquisition paragraph | Frozen boundary evidence only; deliberately not translated into an acquisition policy |

`Derives` is an inductive relation, not an equality to the executable function.
`evaluation_iff` proves correspondence in both directions for finite expressions.
The read trace witnesses which reference lookups the chosen fallback evaluation
visits; it is instrumentation, not a CSS API. Expressions cover literals and
nested var references in fallback positions, not concatenation or arbitrary
substitution functions. Empty literal tokens are valid and differ from invalid.

Attribute metadata is preserved as part of the opaque selected payload. The
animation gate does not inspect or clear it. No CSS Values attr-taint acquisition,
substring semantics, URL rejection, interpolation, or security theorem follows.

Unused fallback non-evaluation does not prove the containing custom property
untainted. The infectious paragraph has no explicit selected-branch qualifier;
`references` must be established independently. The model neither equates that
graph to the read trace nor maps it to syntactic var references. It also does not
prove the seed policy, inheritance policy, registration policy, keyframe/WAAPI/
transition scope, cascade retention, value cache identity, or a Stylo refinement.

`infectious_binding` states the missing producer obligation precisely: the
supplied bits must contain every seed and be closed under supplied reference
edges. `infectious_source_selects_fallback` then connects any infection-chain
witness to the nonanimatable substitution result. Neither theorem proves that
Stylo maintains those hypotheses or that a proposed edge policy is normative.

The full primary snapshot and three exact HTML excerpts are bound by SHA-256 and
byte offsets in SOURCE.json. check.py authenticates them before checking Lean.
This is a human-reviewed formalization of a limited algorithm boundary, not a
mechanical natural-language translation or proof of the entire CSS algorithm.
