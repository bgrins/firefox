# Admission correction: reference root is not the element context

This qualification supersedes any reading of `ADMISSION.md` that admits the sealed ownership model as a faithful declaring-root/context integration. The ownership trace results remain valid for their stipulated machine. Canonical semantic admission of the existing root interpretation should wait for an explicit separation of inputs.

`EffectOwnership.computed` evaluates `selection.parameters` at `environment selection.root`. `Selection.root` has only type `Nat`; the model contains no target element, lookup function, reference-root/selected-rule-root distinction, or relation establishing which element supplied `ownFont`, `parentFont`, `siblingIndex` and `siblingCount`. Its concrete `env` gives sibling index 2 to root 7 and 3 to root 9. Thus `independent_consumer_witness` changes both expression and numeric input while changing the root. It does not isolate a reference-root change with a fixed target context.

There is no logical inconsistency: the arbitrary environment can map both roots to the same target context. A safe interpretation of the existing `root` is a synthetic environment key associated with an externally supplied selection. However, the README's “selected root” and MAPPING's “selected-rule scope transport and context construction” can suggest that the declaring root supplies numeric element-relative inputs. That interpretation is unsupported. The proved ownership invariant is insensitive to this issue, because it treats CSS computation as a stipulated function whose results are shielded after an accepted override. Full-state rejection erasure is likewise independent of evaluator correctness.

## Concrete evidence

`css-contextual-easing-declaring-root-boundary-20261029-v1/REPORT.md` and `declaring-root-easing.tentative.html` keep the same shadow target and its fixed 16px font while toggling the winning `animation-name` declaration between the shadow tree and document `::part()`. The reference root changes rule selection. The contextual candidate uses `1em / 8px` versus `1 + 1em / 8px`, both evaluated using that same target font. Equal support and equal supported inputs therefore coexist with unequal selected expressions and results. This is exactly the distinction already anticipated by `ContextualEasing.field_support_does_not_identify_rule`; it is not a counterexample to `parameters_locality`, which fixes the expression list.

`css-keyframe-declaring-root-system-observation-v1/RESULT.json` records System Firefox 158.0 retaining `steps(2)`/opacity 0.5 in the literal collision's document-declaration phase, where the marker is green and the unique outer control gives `steps(3)`/opacity approximately 2/3. This reproduces the recorded known bug 1458189 witness. The contextual variant fails its initial syntax-support assertion before fixture creation. It provides no observation of contextual evaluation or numeric-input binding. The boundary REPORT's earlier “unexecuted” statement is superseded only for the literal observation by this separately saved result; contextual semantic readiness remains unestablished.

## Smallest principled successor

Keep the sealed model unchanged. In a separately named successor, distinguish:

* Reference root of the winning `animation-name` declaration.
* Selected keyframes rule identity/version and its defining root, plus declaration identity and complete parameter expressions.
* Target identity and its supplied current `ContextualEasing.Context` (or a target-keyed context environment).

For the current four-field fragment, define computation as `ContextualEasing.evaluate selection.parameters targetContext`. Reference and defining roots are provenance inputs to external rule selection, not numeric-context lookup keys. Keep selection correctness external until a real lookup relation is modeled. Substitution, tree-scoped numeric functions, pseudo binding and complete context acquisition remain separate obligations.

A discriminating witness should hold `targetContext` fixed, change the reference root and selected rule/expressions, and obtain parameters 2 then 3 (then 2 on restoration). A separate witness may change target context while holding selected expression fixed. Neither is a native refinement claim.

Reuse `ContextualEasing.parameters_locality` directly: for the same complete parameter list, agreement on its support gives equal evaluation. If selections are compared, transport through explicit parameter-list equality first. A conservative cache contract additionally requires selected-rule/declaration identity and version correspondence; equal name/support/supported values alone does not establish that premise. Reusing this theorem, or the existing support-versus-expression witness, adds no proof-discovery credit. Re-proving generic ownership induction for the separated state also transfers existing results rather than discovering new ones.

No successor Lean proof is necessary to resolve this semantic ambiguity: it is visible in the definitions and concrete fixture. No kernel command, sealed-model edit, canonical edit, native change, index update, build or browser operation was performed for this correction.
