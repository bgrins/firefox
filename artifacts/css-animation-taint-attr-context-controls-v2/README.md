# Marked-result negative-control correction

This check-only addendum preserves the sealed attr-context model V1. The model source is byte-identical; no theorem or semantic definition is added.

V1 run3 made the inner literal initially unmarked and marked it at Attr output. Two false expectations still named the unmarked inner literal, so their rejection could depend on an attr-provenance bit even if the erroneous token-selection behavior occurred. `ResolveCustomInOuter` and `IgnoreTypedParseFailure` now expect `some (markAttr innerValue)`: the intended wrong-context or ignored-parse-failure result has inner token 2 with attr taint set. The actual context case selects outer token 3, and the actual parse-failure case selects marked outer token 3. Thus the revised controls differ on the intended token decision; provenance alone cannot account for their rejection.

The exact two-string replay delta is retained. The same pinned isolated Lean runner recompiles the unchanged model, audits its existing four public theorems, and reruns four false controls. This is check-quality tightening, not four new proofs or a canonical coverage increment. Native/spec refinement limits remain those of V1. No native, browser, Git/index or canonical library operations are performed.
