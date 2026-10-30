# CSS and Stylo verification — V91

This revision adds the executed direct-attr comparison, focused WPT and isolated context model to [V90](../css-continuation-roadmap-20261030-v90/PLAN.md). The accepted fix count remains 149. Native session 46619 is still compiling affected C++ code after successful Rust compilation; no candidate browser result exists yet.

## New evidence

Installed Firefox 158 and portable Chrome 156 pass typed-attr literal support, untainted recursive substitution and all lifecycle/reference controls. Firefox outputs animated horizontal-tb for both tainted attribute-text var and direct var; Chrome outputs vertical-lr, matching the inner fallback prediction. Four samples per case agree. Outer attr fallback and inheritance are distinct vertical-rl. Both owned process groups and temporary profiles were independently verified absent. Raw reports and independent JavaScript replay are retained.

The spec trace retains the outer property context while typed attr adds an attribute guard. Connecting that stack to Variables' non-animatable-property guard is an explicit interpretation, not a proof of getter scheduling. Alias infection through fetched text remains inconclusive. This is animation-taint research, with no attr-security or exfiltration claim.

Frozen source review finds that attribute text is resolved without the consuming context and its inner fallback can be discarded. Copying metadata or rejecting the whole attr cannot recover that fallback. This is an additional candidate acceptance gate, not yet another independent accepted fix.

AttrContext final core run3 (79428/5d3490/0) compiled four audited results and rejected four false controls. Root read the full source and audit logs and confirmed compiled-source equality. The model distinguishes attr retaining context from custom Ref primary evaluation; proves specified arbitrary-depth alias-chain/nested-attr statements; and disproves a common final cache value and whole-attr rejection on the discriminator. It assumes finite acyclic expressions, supplied parse results and provenance semantics. Native parsing, cycles, invalidation, scheduling and alias-spec refinement are unproved; canonical coverage increment is zero. The initial run1 proof-script failure and prior run2 are retained. The separate controls-v2 replay (27947/c18099/0) tightens two negative expectations to match updated attr-security marking; all four controls still reject for the intended token decisions. It reaudits the same four proofs and adds no theorem count. All owned Lean scratch directories were verified absent.

The focused direct-attr WPT V2 is sealed, statically checked and peer reviewed: four callbacks on one page, active assertions only, exact executed calibration functions. V2 adds an explicit body before its asynchronous callbacks; V1 had a startup-order flaw and remains unexecuted historical preparation. V2 has not been run in the native WPT harness. Together with the six prepared inherited/fallback callbacks it adds ten callbacks across three pages; appended to the current suite this makes 116 callbacks across 15 pages.

## Work order

1. Poll existing session 46619; let the 106-case trial and restoration finish. Independently replay eight intended repairs versus 98 preservation/control callbacks and verify source/app restoration before native changes.
2. Admit the ten new callbacks against the restored original, then the candidate. Add script-producer coverage from V90. Do not accept the implementation based only on the original 106 cases.
3. Use actual candidate results to implement complete consuming-context attr evaluation. Preserve raw expression/fallback structure or use a proven sufficient context key. Resolve newly selected fallback dependencies and cycle guards before introducing recursion. Keep alias propagation's unresolved policy separate.
4. Retain V90's distinct duration/input-selection and performance obligations. Signing still fails through 1Password following V83. Preserve research and validated min/max/logarithm payloads, then make separate signed native+WPT commits when signing works and the overlay has restored. No retry of the completed failed owner or unsigned fallback.

Bloom milestones 1–6 and the accepted-fix ledger are unchanged. Neither all CSS nor native Stylo is formally verified. V12 remains the latest untracked inventory; new ignored research artifacts are outside it.

[Direct-attr evidence](../css-animation-taint-direct-attr-root-readout-v1/README.md) · [Context model](../css-animation-taint-attr-context-model-v1/README.md) · [All accepted fixes](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).
