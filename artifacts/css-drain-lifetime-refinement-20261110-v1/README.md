# Style-data lifetime refinement

This capsule proves a conditional lifetime-to-phase refinement for the held animation drain. A strict-ancestor application can destroy descendant style data; a later normal step consumes the resulting ticket, advances a logical lifetime serial, and requests an obligation for that exact new lifetime. The coupled steps erase into the existing descending-phase model. This is a Lean model result, not a native termination proof or a production repair.

Validation: **366 theorem axiom audits, including 65 new declarations; 25 executable observations; four false-claim rejection controls.** `verification3/REPORT.json` records exact sources, commands and axiom sets. Only `propext`, `Classical.choice` and `Quot.sound` are permitted by the checker. There are no admitted proofs, declared axioms or native-decide escapes. `source-only/REPLAY.json` records the separate replay using only the copied source roster and pinned toolchain. Both runs compile every dependency afresh and remove temporary build products.

## Guarantees

- `clear` preserves the lifetime serial, only destroys present data, and grants one replacement ticket. Re-clearing missing data is idempotent. `ensure` consumes a ticket only for missing data, increments the serial, and is idempotent on existing data.
- `clearDescendants` changes only in-bounds strict descendants. It preserves the producer. Causal geometry and validity persist through modeled histories.
- `InitialOnly` holds for the initial cell and is preserved. This makes initial tickets available only before the first lifetime under the explicit initial-state premise; `Valid` plus `Causal` alone is insufficient.
- `joint_normal_cause_and_request` uses the same before-cell and target for allocation and ledger admission. A fresh new lifetime has its full-key request recorded and remains unsettled. Clearing does not count as delivery and leaves ledgers unchanged.
- `different_identity_completion_preserves` isolates target, pseudo type, pseudo argument, cascade level, lifetime and generation. `joint_old_completion_isolated` proves an old lifetime's completion cannot discharge recreated work.
- `empty_no_future` and `joint_no_future` establish and preserve the no-future-key freshness invariant across joint normal/application steps. This removes the need to assume fresh keys anew at every such step when starting with empty ledgers. It does not cover arbitrary administrative histories or arbitrary malformed in-flight keys.
- `recreated_lifetime_budget` bounds a target's lifetime serial by its initial clear count plus the initial descending-phase weight plus one. `closed_productive_budget` bounds productive phase steps, and `no_infinite_joint_productive_steps` rejects an infinite sequence composed entirely of these joint steps.

The generic theorems quantify over the finite ranked tree and modeled histories. The small-tree observations illustrate them; the observations do not prove the bounds.

## Explicit boundaries

Three kinds of state remain distinct: pending phase bits, dormant replacement tickets and required ledger requests. A ticket permits later allocation; it is not a demand to allocate. The example deliberately leaves one descendant absent with a valid ticket after all phase bits clear. Phase quiescence does not imply that all ledger requests have been settled either. Administrative delivery, fairness, retirement justification and complete native required-set admission remain separate obligations.

One normal recreation supplies one `Metadata` key to the ledger. The model isolates either cascade level but does not establish simultaneous animation/transition task-mask completeness, nor does it request new metadata on an already-present cell. Those are native mapping obligations, not consequences of quantification over metadata.

`Causal` validates strict-ancestor geometry; it ignores the event number. Modeled application steps create tickets with their actual pre-step clock, and histories advance that clock. Authentic attribution of a ticket to a past event therefore depends on modeled reachability, rather than `Causal` alone. A full native event-trace refinement is not proved.

Every productive constructor requires a dispatch admitted by the existing phase graph. The finite bound follows from this requirement. The module does not establish that all native producers meet it; it excludes neither arbitrary administrative stuttering nor external producer injection by theorem. The unrestricted-renewal diagnostic advances a lifetime without decreasing phase weight, showing why a finite tree alone is inadequate.

[MAPPING.md](MAPPING.md) identifies the source-shaped operations and missing native premises against revision `b1f13d1516967034ca17255bcb1634e9f166b54a`. No browser, WPT, native source, objdir, library or Git changes were made for this capsule. Keep #160 held until the native cause/epoch/required-set and delivery boundaries are established. No fixed iteration cap or dropped work is justified here.

## Files and reproduction

`Lifetime.lean` models tickets, clears, allocations and phase erasure. `LifetimeDelivery.lean` adds full-key ledgers and the joint productive transition. `Cases.lean` contains the finite observations and diagnostic lifetime-erasing completion. The four negative controls reject self-ancestor renewal, an uncharged renewal decreasing phase weight, old completion settling new work, and lifetime-erasing completion being safe. They are **false-claim rejection controls**, not implementation mutation tests; only the expected false-proposition diagnostic counts as success.

The copied import closure is authenticated by `IMPORTS.json`. Its original `Delivery.lean` is preserved. The older dependencies and the newer accounting capsule both used the namespace `AnimationObligations` for different structures. `Accounting.original.lean` preserves the latter exact bytes; `Accounting.lean` makes the sole mechanical change `AnimationObligations` → `LifetimeLedger`. The checker authenticates both the original hash and exact namespace-only replacement. No proof statement or implementation is changed by that transform.

From the Firefox repository root, use a new output directory each time:

```sh
python3 artifacts/css-drain-lifetime-refinement-20261110-v1/check.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --out /tmp/lifetime-check-new
python3 artifacts/css-drain-lifetime-refinement-20261110-v1/replay.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --out /tmp/lifetime-replay-new
```

`SOURCES.json` pins the replay inputs; `TOOLCHAIN.json` pins the compiler binary plus the `Std.lean` umbrella source and `Std.olean` object. Remaining toolchain components are trusted installation inputs; this is not a fully hermetic toolchain audit. `replay.py` copies only those source inputs into a fresh directory, without existing `.olean` files or native source, then runs the same complete checker. `SOURCE-CONTEXT.json` pins the prior source audit; it is documentary provenance, not an input to the Lean proof. `FILES.json` authenticates the final artifact files except itself.

Earlier failed validation attempts are retained: `verification1` correctly rejected the ordinary model identifier `admit` under the proof-escape check (renamed to `requestAdmission`); `verification2` rejected a control that got stuck reducing a well-founded path instead of proving the proposition false. The control now uses explicit definitional simplification before kernel decision. These failures are not counted as passing controls. Development compilation caches are removed after the successful source-only run.
