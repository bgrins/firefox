# Parity bridge for the finite-depth diagnostic

This isolated extension imports the sealed Completion model unchanged. It proves an arithmetic encoding for the prepared finite-depth fixture; it does not re-prove the predecessor's queue/coverage/iteration theorems or claim a CSS/native refinement.

At 1500ms, the fixture's selected endpoint family has duration input×1000/16 milliseconds. With fill-both and step-end, input16 gives duration1000 and output32; input32 gives duration2000 and output16. Opacity uses the same timing but outputs1 or0. `exact_endpoints` checks those concrete integer calculations. Inputs are restricted by `metric` to16/32; integer division here is exact, not a model of arbitrary CSS floating-point computation.

`metric i b` decodes Boolean generation b by XOR with stage parity, yielding16 or32. Therefore advancing from stage i to i+1 at the same Boolean generation flips the metric. `parity_transfer` proves that relation for arbitrary i, and `selected_evaluation_is_metric_transfer` proves that the existing model's selected predecessor-copy evaluation is exactly this arithmetic transfer under decoding. It relies on the existing explicit evaluator, not on a premise asserting the desired new value. It does not equate native queue removal or posting with evaluation.

The fixture has depth D intermediate animated nodes plus an opacity leaf. `leaf_is_additional_edge` proves that evaluating opacity from stage D corresponds to stage D+1 in the Boolean encoding. The leaf's16/32 metric is only a virtual encoding of opacity0/1; it is not the leaf's actual computed font size or line-height. Root and intermediate metrics alternate actual font-size and explicit-pixel line-height by the fixture's authored topology.

`initial_encoding` joins the changed root32 and the old calibrated non-root outputs to Completion.initial: root generation true, all non-root generations false. The previous root16 calibration corresponds to generation false at every stage; parity_transfer supplies its consistent alternating values. No theorem certifies that browser acquisition/setup reaches this state—the fixture must calibrate it.

`completed_leaf` uses existing run_exact to give the expected leaf after D+1 snapshot rounds. `incomplete_leaf_witness` derives a stale leaf for every smaller round count; `bit_distinguishes_generations` prevents parity from hiding a stale generation. These round statements inherit Completion's fixed-input snapshot-frontier semantics. They are not claims about the number of Gecko traversals, flushes, frames, elements or queue drains required.

The checked table is (initial,final) opacity (0,1) at depth1 and (1,0) at depths2,4,8. Depth counts intermediate nodes; total dependency edges are2,3,5,9. Thus an off-by-one leaf count is observable rather than a naming convention silently absorbed by the proof.

## Actual kernel evidence

Final run2: launch a7921b, session77797, terminal d953ec/0. Nine named declarations audit successfully; four false controls reject the wrong odd endpoint, a missing leaf edge, the wrong even-depth opacity, and freshness at depth8 after only two model rounds. Audit axioms are standard propext/Classical.choice/Quot.sound only. No sorry or native reduction axiom. Source56ab0862… matches run2/CHECK.json. Both temporary scratch directories were removed. Run1's actual simplifier-name error is retained; run2 has no warnings.

Replay with a fresh output name:

```sh
python3 -I -B -S artifacts/css-contextual-duration-finite-depth-oracle-model-v1/replay.py independent-run
```

The script authenticates the unchanged Completion, QueueState and DispatchAttempt packages and pinned Lean executable, then compiles in temporary scratch. The fixture is prepared and unexecuted. Its resource/manifest/static-check pins are references, not evidence of browser behavior. Style resolution, interpolation integration, property ordering, currentTime semantics, inherited-metric correspondence, queue coverage and scheduler progress remain external obligations. No native acceptance, new bug count, cycle policy or canonical proof-coverage increment is claimed.
