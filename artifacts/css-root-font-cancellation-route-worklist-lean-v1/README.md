# One scheduled normal obligation across a route

This separate bounded successor imports sealed explicit-conditions Delivery v1 (2b5e261c). It addresses only the missing route-visitation premise. It does not introduce a full Gecko tree scheduler, infer entry into normal traversal, or change native code.

The executable state has one pending node, a remaining finite route and the visited sequence. load schedules only the first node. One step visits that pending node and hands the obligation to the next route node. With forwardAll, forwarding does not depend on the next node's own font change or animation membership. If a restricted rule refuses the handoff, pending becomes empty while the unexplored suffix remains; later steps cannot conjure a task.

CancellationRoute.scheduled_route_visits_in_order proves by induction that executing exactly route.length steps from a scheduled route visits the entire route in order and finishes with no pending node. It permits any prior visited sequence. scheduled_target_visited derives actual target visitation for ancestors ++ [target]. completed_route_supplies_visitation constructs the prior Delivery model's reached witness from those derived visits. It therefore discharges the prior allVisited condition for this execution, rather than assuming it as a theorem premise.

This is a finite execution bound, not autonomous progress: the scheduling entry, correct route extraction and execution of those steps before the first observation remain external obligations. insufficient_dispatches_counterexample and no_scheduled_work_no_visitation make that boundary explicit. The normal obligation may still fail to be scheduled or drained natively.

## Concrete discriminating control

The route is root1 (font changed), fixed unanimated intermediate2 (font unchanged), animated dependent3 (font unchanged). Forwarding through every hop yields [1,2,3]. The deliberately restricted onlyAnimated handoff visits only root1 and leaves [2,3] stranded, even though the ultimate dependent is animated. The same restricted rule successfully handles the immediate [root1,dependent3] route. This isolates the hidden-descendant gap; it is not a claim that current Gecko implements onlyAnimated, nor a proposal to force every intermediate to recascade its own computed style.

Native correspondence must establish that an ancestor-font obligation is retained/forwarded through necessary structural routes, including fixed-font nodes, until affected consumers are reached. The exact seams are pre_traverse/element_needs_traversal, recalc_style_at propagated_hint and note_children. Visiting a hop here means enough normal traversal work to continue its branch. Dirty-bit eligibility, hint retirement, animation-only visits, subtree pruning and actual tree generation are not implemented by this model.

## Connection to delivery and pseudo identity

Use completed_route_supplies_visitation as allVisited in CancellationDelivery.complete_route_delivery. The remaining premises are still necessary: relevant exact-target membership, the hint at consumer admission, task delivery, correct node-to-host/pseudo normalization, and an available current provider. No theorem here removes them. The existing child's route and root-owned pseudo's generated-content route may differ. For ::before, the visited/queued node stays the generated node; Gecko_UpdateAnimations normalizes it to host+Before before EffectCompositor delivery. This model does not replace node identity with the host or prove that structural mapping. The instrumentation-v2 normalization event supplies the proposed observation point, with its documented lifetime/thread limitations.

Neither model proves endpoint interpolation, mProperties installation, final composition or getComputedStyle publication. A later root-metric invalidation can invalidate a completed rebuild. The concrete rem-base23 result in Delivery is not a proof of rendered46. Root's actual candidate34 first/settled64 motivates distinguishing entry/forwarding/delivery/provider failures; it does not select a cause.

## Validation

The same pinned Lean4.35.0-rc4 toolchain and six exact imported sources are used in owned scratch. New declarations receive axiom audits; six false controls must fail through decide proving the proposition false. One initial attempt rejected the reserved Lean token prefix; its source/logs are retained and not counted. Final receipt identifies the successful source. No browser, native build, scheduler instrumentation execution, nested-repository or live-state mutation occurred. No inherited theorem credit or generic framework is added.
