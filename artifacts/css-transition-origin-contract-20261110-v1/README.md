# Current effects and insertion origins

This is a retrospective contract model of the observed transition/null-progress interaction. It proves conditional noninterference for a **proposed composition-only in-effect membership policy** and checks a counterexample for an all-registered property union. It does not resolve the specification question, discover another bug, prove a native fix, or derive semantics mechanically from CSS prose.

For arbitrary property/value types, value-combination functions and finite effect lists, inserting an effect anywhere preserves the composite if it supplies no sample. It also preserves the selected origin if the membership policy excludes it. Together these facts preserve the reduced-cascade result. No algebraic property of the supplied combination function is assumed.

`inEffect_noninterference` uses `registered && targets(property) && inEffect`. It requires both `inEffect = false` and an absent sample. `coherent_off_noninterference` instead takes an explicit premise that an out-of-effect snapshot supplies no samples. Neither theorem infers in-effect state from sample absence. A checked counterexample shows that an abstract in-effect record with no sample can still change the selected origin under this policy.

The origin selector has an independently stated existential relation (`HasClass`/`Selected`), with exact equivalence proved by `selectOrigin_spec`. The class selector abstracts fixed Transition-before-Animation composite ordering; it is not a generic maximum over arbitrary animation classes. This is distinct from cascade precedence: a Transition-origin value beats author-important, while author-important beats an Animation-origin value. These are separate functions and laws.

## Symbolic witness

Values are `transitionSample`, `animationSample`, `important`, and `ordinary`. No interpolation formula, opacity number or browser result is a correctness axiom.

| List/policy | Composite | Origin | Result with author-important |
| --- | --- | --- | --- |
| Transition only | transitionSample | Transition | transitionSample |
| Transition plus current non-filling effect; all registered | transitionSample | Animation | important |
| Same inputs; proposed in-effect policy | transitionSample | Transition | transitionSample |
| Effect cancelled; all registered | transitionSample | Transition | transitionSample |
| Active overlap | animationSample | Animation | important |

`delayed_joint_premises` proves registration, current status, out-of-effect status, absent samples and coherence simultaneously for a concrete record. `forwardNoFill` constructs it at time 0, delay 10 and duration 10 in a narrow positive-direction, resolved-time, fill:none snapshot model. The transition record is at time 5 of duration 10. This is a satisfiable timing-shaped model witness, not a browser timing-algorithm execution theorem. The separate browser experiment provides empirical reachability evidence.

Controls cover no-important behavior, an unrelated property, cancellation, active overlap, and an all-absent list inserting no value. The compositor guard is separate: `compositorGuardMask` always uses all registered animation properties. The delayed effect changes that conservative mask while the proposed rendering result is unchanged. Globally filtering the native shared set is not justified by this proof. A mutation that filters this guard fails its independent membership law.

## Boundaries

- Membership is proposed, not established as normative. Effect-value calculation aborts on unresolved progress, but the stack/origin text does not explicitly settle non-sampling membership. Both the phases summary and combining-effects introduction are non-normative. The source/spec verdict remains **INCONCLUSIVE**.
- Registration, target properties, class, sample availability and sample values are inputs. The list supplies composite order. Interpolation, additive composition semantics, creation and lifecycle are not derived.
- `Coherent` is an explicit input contract. Native eligibility and sampling must refer to the same time. The motivating experiment is paused and nonpending. Pending `Animation::ComposeStyle` can select a wallclock-derived hold time while ordinary `IsInEffect` observes different timing. That implementation bridge remains open.
- Only ordinary style composition is considered. Endpoint-inclusive `commitStyles`, cached-mask freshness, invalidation, pending tasks, pseudo-elements, replacement state, target validity and compositor execution are not proved.
- Cascade precedence is reduced to ordinary, author-important, Animation and Transition candidates. Other origins, specificity, layers and rollback are excluded. Existing canonical `Cascade` machinery was inspected; its origin datatype covers author/user/user-agent bands and would not discharge this separate animation-origin contract. No canonical code was copied or modified.

`inputs/native-excerpts.json` retains named excerpts from two files independently matched to Git revision `ec467c0219d3d5daf70f42fcc53677cf8a262173`. `inputs/spec-excerpts.json` retains webspec-index snapshot identities, anchors, exact text and hashes. The copied source review records the causal trace and open questions. The copied Firefox 158 result records 53 passing setup checks and 36 style reads. None of those evidence files supplies Lean axioms.

## Reproduce

```
python3 -I -B check.py --lean /path/to/pinned/lean --out /new/check-output
python3 -I -B replay.py --lean /path/to/pinned/lean --out /new/source-only-output
```

The source-only replay copies only manifest inputs. It compiles five modules, audits every named theorem, executes symbolic cases and runs three semantic mutations. Mutated implementations compile; unchanged laws fail at the targeted theorem, and kernel-checked witnesses establish the altered behavior. No additional axioms, sorry, native_decide or arbitrary fuel is used. Owned compiled output is removed.

The next step is resolving membership interpretation and testing a separately reviewed composition-only native mask, including pending-time and inclusive-endpoint cases. A future browser comparison would still not prove the specification interpretation.
