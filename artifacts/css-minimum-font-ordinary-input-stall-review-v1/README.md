# Minimum-font crash: ordinary input has no action

The actual diagnostic narrows this failure to an unsupported ordinary font-input publication branch. It does not show the hypothesized computed-size child-action failure. The native owner 82438 / launch 3a1253 / terminal f6b0fa exited 1 after minimum_off emitted zero callbacks and one CRASH ending. Nine unique diagnostic messages are copied from the closed raw stream into OBSERVATIONS; build COMMAND joins all three exact source hashes to the sealed logging candidate. Source/application restoration and independent audit remain separate root authorities.

## What the actual state proves

The retained root is Custom(metric), with exactly one registered frame at Publish, index=lowlink=0, no waiting target and an empty SCC stack. There is no current metric action, lookup, references record, size node, size facet, deferred size or finished root. FontSize, Family, Appearance, XLang, XTextScale, minimum ratio and Zoom are complete/ensured with no active/claimed bits. No readset rejection or drive-action progress diagnostic was emitted.

The exact call path constrains the final return:

1. `run_one` receives ComputationPending and stops because `pending_metric_action` is None.
2. `poll_frames` retains the frame and returns that result on `FrameStep::Pending(None)`.
3. In `TraversalFrame::step` at **Custom Publish**, the FontUnits-only computed-size path cannot run. `publish_closed` cannot return Pending for a custom node: only a prioritary node calls the possibly-pending native apply; custom Prepared/Substitute arms publish and return Ready.
4. Therefore this Custom Publish state returned `PublicationDemand::Unresolved` from `publication_readiness` / `font_publication_demand`. FontSize complete rules out that function's first Unresolved return. The remaining Unresolved arm is a metric demand with a next unprepared ordinary font input that `is_synthesis_longhand` does not support.

Metric or Synthesis returns would have installed an action; an unsuccessful drive would have printed its distinct progress diagnostic. Those alternatives do not match the complete raw diagnostic set. This is a source deduction from the recorded terminal state, not an instrumented observation of the exact longhand.

`next_unprepared_font_input` scans a wider set than the four synthesis longhands accepted by `is_synthesis_longhand`. The unchanged fixture explicitly supplies `font-kerning:none`, `font-optical-sizing:none`, and `font-variant-ligatures:none`; all three belong to the scan and none has an enabled preparation action. The fixture's registered `--metric:1ch` provides a font-metric consumer. Declaration order, shorthand expansion and the exact first blocked input are not logged, so this report does not choose one of the three as the observed first entry. The seven logged priorities also do not exhaust all priorities; the no-action branch itself constrains the intervening metric/orientation checks to have succeeded.

## Narrow policy reproduction

POLICY-EXTRACT.rs embeds the exact `font_publication_demand` and `is_synthesis_longhand` bodies and demand enums from the authenticated candidate. Minimal enum/set facades supply function inputs only. Ten controls check no-demand/computed-size readiness, missing FontSize, missing metric/orientation priorities, no remaining ordinary input, and all four existing synthesis actions. Three separate assertions require an enabled action for each fixture ordinary input when every priority is complete. All three fail with exit 101 because the actual function returns Unresolved. Compilation and controls succeed; owned scratch is removed.

This demonstrates the pure dispatch gap. It does not execute native Context, the real declaration scan, graph traversal, conversion, font metrics or a browser, and it is not a second native reproduction. No repaired candidate is included.

## Smallest faithful repair direction

Give unfinished ordinary metric inputs an explicit retained action, instead of producing an unowned Pending. Generalize the existing synthesis action's *role* to ordinary font-input preparation; keep target longhand, root/index/action identity, generation, flags, selected declaration cursor, parser, reply and completed-input ledger. Reuse `begin_font_preparation` / `resume_metric_preparation` / `publish_prepared_metric` and actual `apply_one_longhand`, extending their current synthesis-only admission consistently. Mark completion only after real selected-declaration application and resume the retained Custom Publish frame. Merely changing `font_publication_demand` is insufficient because `begin_font_preparation` and `perform_synthesis_action` also enforce the narrow predicate.

The immediate native regression should isolate `--metric:1ch` with each of the three literal ordinary inputs, then their combination, before testing the original minimum_off page. Compare the metric/geometry against same-style references, retain first-read and mutation checks, and verify successful completion without duplicate ordinary application. Add selection controls for winning literal versus losing dynamic declarations, revert/layer behavior, repeated consumers, and actual var()/attr() suspension before claiming a reusable ordinary-input producer.

Native obligations remain: each admitted ordinary input needs its real conversion/prerequisite readset and ordering; existing once-only effects and ordinary-pass seen/completion behavior must agree; invalidation cannot replay applied effects; retained requests must preserve owner identity; a true semantic cycle must remain distinct from a dependency wait. The wider scanner also lists other font and math properties whose dependencies cannot be approved by simply renaming the four synthesis cases. Conversely, excluding a property from a particular metric demand requires proof that its native getter cannot affect that metric—not deleting entries merely to avoid the stall. Keep unsupported work explicit during development, but do not call permanent Pending support for valid CSS.

## Relation to earlier child-action design

The sealed child-action reports describe a separate real ownership hazard involving singleton action/lookup/parser state. This run provides no evidence that a computed-size child was entered or that an outer lookup was lost. It instead terminates with no action to drive. Do not introduce the larger child-action design as the repair for this observed branch, and do not infer that fixing the ordinary-input dispatch makes the other hazard disappear.

No shared candidate, native source, app, index, canonical state, active runtime or browser was modified. Only this new artifact and removed policy-test scratch were written. This is a prototype scheduler defect; no released Firefox defect, accepted-fix increment or repaired browser result is claimed.
