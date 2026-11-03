# Cancellation: retained hint versus delivered rebuild

This small extension imports the exact sealed Admission and Provider models. It does not replace either model, edit their nested repository, or assert native scheduling reachability. It distinguishes a retained hint, a normal route to the consumer, an admitted queued node, delivery to the normalized animation target, and a rebuild using a current provider. The new state is deliberately a single-consumer pipeline, not a generic scheduler.

## Smallest native obligation

Before the first dependent resolved-style observation returns, every affected relevant consumer in the observed subtree must either already have a rebuild using the final root metrics or receive the following work: the applicable pending root-font obligation reaches its consumer through the normal traversal route, membership admission creates EFFECT_PROPERTIES work, the queued node is normalized to the exact host/pseudo target, and that effect's UpdateProperties rebuild uses the current same-document provider and installs the result. A later root-metric invalidation requires renewed work; completing an earlier generation is insufficient. This is a proposed refinement obligation, not a claim that native code stores model revisions or that every node needs a separate normal recascade.

A fixed-font intermediate is still part of the route to a descendant whose keyframes use rem. Its own unchanged font cannot by itself discharge that descendant's obligation. A route hop's normalVisited field means normal traversal processed that branch sufficiently to reach the next hop; it does not require recomputing the intermediate's own style. The model does not infer any hop from a retained hint or from a document flush request.

## Existing and new proof boundaries

FontUnitAdmission.registered_normal_hint_admitted already derives Boolean admission from actual model registry membership plus normal=true and hint=true, irrespective of the ordinary retained style flag. It does not establish normal traversal, task creation or delivery. RootFontProvider.provider_current already proves that an available modeled provider equals desired metrics; its invalidate/begin/finish rules are stipulated protocol transitions, not native Cancel callbacks.

CancellationDelivery.complete_route_delivery composes the imported admission theorem with explicit enqueue, deliver and rebuild operations. It is conditional on every route hop being visited, a retained hint, exact node-to-target normalization and an available provider. CancellationDelivery.rebuild_uses_current_provider reuses the imported provider validity theorem to establish that a rebuilt rem base is the desired metric. It proves a rem base observation (23 in the witness), not the interpolated 46px output, style installation, composition, or getComputedStyle timing.

The concrete finite traces separate the missing premises:

- retained_hint_counterexample: a true hint with a stopped normal route has no rebuilt result.
- admission_not_delivery: the actual imported admission condition and queued node can both hold without any rebuild.
- delivered_not_fresh: delivery to the correct pseudo target still produces no modeled value while the provider is unavailable.
- pseudo_mapping_is_required: treating generated node7 as ordinary host7 fails to deliver a rebuild to host1/Before.
- fixed_route_can_complete: explicitly visiting both fixed-font route hops, delivering the normalized node and using the refreshed provider produces the 23 rem-base observation.

fixed_fonts_do_not_shorten_route says only that the model's required route depends on visitation, not local font changes. That choice states the obligation under investigation; it is not a proof of Firefox traversal policy. animation_only_does_not_enqueue and unreached_route_does_not_enqueue expose missing progress; no fairness or eventual completion theorem is claimed. The traces use separate explicit calls, so there is also no theorem that an observation automatically runs them or prevents later invalidation.

## Native correspondence still to establish

| Model boundary | Exact native seam | Unproved part |
| --- | --- | --- |
| retained hint / route | finish_restyle, propagated_hint, note_children, element_needs_traversal, pre_traverse | cancellation publishes final root metric; normal route reaches the consumer despite fixed intermediates, animation-only passes and dirty-bit policy |
| enqueue | recalc_style_at admission, process_animations, SequentialTask::update_animations | admitted recascade actually produces/retains EFFECT_PROPERTIES before first observation |
| deliver | SequentialTask::execute, GeckoElement::update_animations, Gecko_UpdateAnimations, GetElementPseudoPair | task survives queue boundaries; generated pseudo node maps to its host/Before and current style |
| rebuild/provider | EffectCompositor::UpdateEffectProperties, KeyframeEffect::UpdateProperties/BuildProperties, Servo_GetComputedKeyframeValues, Device root-font reads | same-document current metric is read; endpoint changes install and affect the resolved observation |

For ordinary existing-child and root-owned ::before witnesses, delivery identity differs. The sealed instrumentation-v2 normalization event supplies input-node/host-node/pseudo correspondence; it does not prove unique lifetime/global ordering. Keep these witnesses separate. The proposed first-observation obligation additionally needs output installation and no intervening relevant invalidation, neither modeled here.

Root reports actual unchanged candidate34 (47f4de/9c6462): no-read child and root-pseudo are64 both first and settled, root-read/newchild46, rlh74. This motivates checking the first false route/provider/delivery premise; it supplies no provider value or causal proof. This package does not bind an unfinished runtime or promote that report to an independently authenticated browser result.

## Validation scope

The replay uses the same pinned Lean4.35.0-rc4 compiler and exact five imported sources in owned temporary storage. It audits all new theorem axioms and compiles six genuinely false claims, requiring decide to prove each false rather than a parser/name error. Historical failed local elaborations are retained in separate run directories; no failed attempt is counted as proof. Final receipt identifies successful source bytes. No native build, browser, live source/index/canonical or nested-repository mutation occurs.
