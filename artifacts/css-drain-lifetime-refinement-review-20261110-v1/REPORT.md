# Independent lifetime-refinement review

Accepted for the stated conditional model claim. I found no remaining blocker after the joint transition and explicit boundary clarifications. This is not acceptance of native drain termination, complete task-mask admission, administrative progress, or a production change.

Independent source-only replay passed **366 author theorem audits, 25 executable observations and four false-claim rejection controls**. A separate compilation checked **eight additional boundary theorems** written during review. The final author source manifest is `efcde2aa7c4cfd3e8fe0ff8c730fea9ac4f3158b63df7ae522358951b6f86d91`. [replay/REPORT.json](replay/REPORT.json) records all copied input hashes, commands, theorem audit results and cleanup. Only standard `propext`, `Quot.sound` and `Classical.choice` are permitted by the replay; the eight additional boundary proofs use only `propext` and `Quot.sound` where needed. No compiled sources were reused in the acceptance replay, and all temporary source/build trees were removed.

## Causality and refinement

The same `normalJoint` transition uses the same pre-state target cell both to allocate its next logical lifetime and to request its supplied metadata obligation. `joint_normal_cause_and_request` connects a valid causal ticket to the admitted origin and the exact newly required, unsettled key. `joint_erases` projects the productive transition to `DrainLifetime.Step`; `step_erases` then projects it to the existing descending-phase theorem. This is an exact model-to-model refinement, rather than a loose analogy between two separately proved examples.

Clearing an already-absent cell does not mint another replacement ticket, and ensuring a present cell does not create another lifetime or obligation. Clearing preserves the current producer and only touches in-bounds strict descendants. `InitialOnly` supplies the separate initial-state condition that local validity and geometric causality alone lack. Its preservation theorem prevents reusing the initial credit along the modeled histories when that condition holds initially.

The ledger is indexed by logical target; each key also contains pseudo type, pseudo argument, cascade level, lifetime and generation. Old full-identity completion preserves the new key's settled status, including when the new key is already in flight. The recreated request is initially unsettled under the explicit `NoFuture` premise. Empty ledgers establish that premise, and `joint_no_future` preserves it across the two modeled productive transition forms. No equivalent preservation through arbitrary administrative operations is claimed.

The phase budget follows because every productive constructor requires an allowed dispatch. It does not prove that native producers satisfy this premise. No unsupported same-rank/upward producer may be renamed “external” merely to make the proof apply; the final mapping says this explicitly. The proof likewise does not rule out infinite administrative stuttering between productive steps.

## Independently checked limits

[Boundaries.lean](Boundaries.lean) establishes these distinctions directly:

- Local `Valid` and `Causal` permit an arbitrary later-lifetime initial ticket; `InitialOnly` excludes it.
- A quiet phase state can retain a dormant replacement ticket. Allocation authorization is not a request to allocate, and phase quiescence is not ledger readiness.
- Without freshness, the next lifetime's key can already be installed. That state violates `NoFuture`; full key inequality alone does not establish initial unsettledness.
- `Causal` checks strict-ancestor geometry and ignores the event number. Event authenticity requires modeled reachability/event correspondence, not that predicate alone.
- A recreation requests one supplied metadata key. Repeating normal processing after the cell becomes present does not admit a second cascade-level key. Complete simultaneous native task-mask admission remains a separate mapping obligation.

These are accepted boundary observations, not newly discovered native bugs. The final README/MAPPING accurately distinguish all five limitations.

## Controls and source provenance

The four author controls are deliberately false propositions, not implementation mutation tests: self-ancestor renewal, uncharged renewal lowering the phase rank, old completion settling new work, and lifetime-erasing completion being safe. Each replay fails with the required kernel false-proposition diagnostic. The lifetime-erasing helper itself compiles and demonstrably installs the wrong lifetime. An earlier stuck-reduction diagnostic was rejected by the checker and repaired before freeze; it is not counted as evidence.

During draft review, a delivery-module name collision was corrected by preserving the original dependency and moving the new code to `LifetimeDelivery`. The initially separate ledger helper was connected to the productive cell transition. A stale identity prototype was removed, and the model admission function was renamed so the proof-escape detector could remain enabled. The final clean replay authenticates the restored import closure and exact accounting namespace transformation.

This review authenticated **14 origin paths against the current filesystem and their pinned hashes**, not against Git objects or signed historical commits. I performed no Git/native/browser operations. `Accounting.original.lean` retains the exact newer ledger source; its checked copy changes only the namespace from `AnimationObligations` to `LifetimeLedger`. Every proof input is present in the copied source roster, so replay does not depend on the original paths being tracked historically. Root separately reports nine origins matching Git HEAD and five matching only preserved filesystem paths, recorded in the author's `ROOT-ORIGINS.json`; that historical-origin audit is additional evidence, not an operation performed by this reviewer.

Reproduce with:

```sh
python3 -I -B check_review.py --author /absolute/path/to/css-drain-lifetime-refinement-20261110-v1 --lean /absolute/path/to/lean --out /new/review-output
```

The remaining useful work is native correspondence for causes, epochs and complete required sets, plus delivery/administrative obligations. This artifact does not justify a fixed iteration cap, dropping work, or declaring the held drain change ready to land.
