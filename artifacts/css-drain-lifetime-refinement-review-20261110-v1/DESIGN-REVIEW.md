# Lifetime refinement review: initial findings

Scope: independent review of `css-drain-lifetime-refinement-20261110-v1`. The author artifact is still in progress. This note records review obligations, not final acceptance.

The existing `Lifetime.Step` requires an explicit `Dispatch` witness for the normal/application phase it consumes. `step_erases` maps that witness to the previously proved descending-phase step, and finite histories inherit its weight bound. The bound therefore applies to these modeled productive steps, not arbitrary native work, administrative stuttering, or all browser execution. No native closure argument is supplied merely by defining this relation.

The local cell accounting has the right idempotence shape. Clearing an absent cell leaves its existing ticket unchanged; ensuring an existing cell changes nothing; ensuring an absent valid cell increments its lifetime and consumes one ticket. A clearing application only touches strict descendants and preserves its own cell. The model's natural-number clock supplies distinct event numbers along a modeled history, without machine overflow assumptions.

The final review must distinguish three facts:

1. A causal ticket identifies a strict-ancestor producer. It does not by itself prove that all native causes are represented, that a particular application has published a particular value, or that the producer itself currently has a valid style cell. Those require mapping/reachability premises.
2. `Valid` and `Causal` are local invariants. They admit arbitrary states carrying an initial ticket at a later lifetime. A theorem saying that initial attribution occurs only once must use reachability from initial cells or a stronger invariant.
3. Application steps currently clear every strict-descendant cell while permitting an arbitrary projected dispatch choice mask. A ticket can therefore exist without the model guaranteeing its future scheduling/settlement. A finite productive-step bound is not a delivery-completeness or readiness theorem.

The full-identity ledger coupling is still being implemented. It must preserve target identity plus pseudo type, pseudo argument, cascade level, generation and lifetime. Old-lifetime completion must not settle a new request, and any freshness/no-future-key premise must remain visible rather than being treated as a derived native invariant.

The copied phase model already excludes same-node application-to-normal feedback. Any inner-loop producer outside the permitted descending relation remains unclassified; it cannot silently be declared an external event to recover termination. An outer request boundary or a different ranking proof must be established separately.

Further source review found two in-progress integration issues and notified the author. First, the new delivery module initially reused the preserved `Delivery.lean` name, which conflicts with the existing phase dependency chain and can create a cycle; it needs a distinct module name. Second, standalone `admit`/completion lemmas do not themselves connect ledger admission to the same normal-phase transition and cell whose ticket is consumed. A joint productive transition with a projection theorem, or an explicit unproved coupling limitation, is needed before claiming an end-to-end causal refinement.
