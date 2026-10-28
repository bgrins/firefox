# Registered keyword readiness oracle

This is an unexecuted draft, separate from the active 29-page zoom experiment. It tests an acyclic provider-admission boundary identified by source inspection. It is not a reproduction claim or an accepted bug.

The pinned official drafts were fetched on 2026-10-27 in css-registered-writing-mode-cycle-policy-v1. This manual trace uses those existing captures; no new machine trace is claimed. HTML help anchors are checked directly because webspec-index was unavailable in the prior trace.

1. API `calculation-of-computed-values` requires parsing against the registered syntax. The ready primary `bogus` is present, so the unused `1vi` fallback is not selected. `bogus` matches neither `<length>` nor the two enumerated keywords. Under `the-registerproperty-function`, the invalid specified value resets to the registered initial value. The decisive captured text is: “and thus resets to the registered initial value”. All registrations are non-inherited; the initial keyword is vertical-rl.
2. API `substitution` requires a registered provider's computed value in var(). Thus writing-mode receives vertical-rl, not the invalid specified token `bogus`. The literal registered provider and used-keyword-fallback controls yield the same computed keyword. The direct literal writing-mode control bypasses provider consumption.
3. Values4 `viewport-relative-lengths` selects the inline axis using the element's writing-mode. In the fixed320x180 iframe, vertical-rl makes100vi equal180px. `lh` uses the fixed40/60/40px line-height; the registered length is220/240/220px. The ordinary literal-vertical control uses the identical calc expression independently.

Verdict: REACHED for these acyclic expected values. No selected logical unit occurs in the keyword provider, and no actual read from its value returns to writing-mode. This does not assign an oracle to genuine vi/if()/style() cycles.

Sixteen tests cover four modes, two declaration orders and two query orders. Each captures all three mutation states before assertions and retains specified provider/writing-mode text. Different names exercise some hash traversal variation, but declaration order is not a promise about native map iteration. Passing all16 does not prove every scheduling order safe. Query order is a robustness control, not a mechanism for forcing the internal traversal order.

Known source risk: LhUnits can call ensure_prioritary_property(WritingMode) before WM graph traversal admits its provider. Recursive substitution then supplies the still-unadmitted token sequence and may freeze inherited horizontal-tb via the ensured bit. Original/candidate browser outcomes are required to establish whether a concrete run reaches this path and whether behavior is pre-existing or changed.
