# Computed-size child-action proof boundary

The saved minimum-font Pending contract is not yet explicit enough to prove a faithful child-action progress theorem. The missing premise is a native transition contract that lends computation to an inner action while retaining, authenticating, and restoring the outer action's complete continuation. A finite, enabled child computation is a separate necessary premise. No new Lean proof is claimed here: assuming a child `Done` transition or an always-ready readset would conceal the scheduler gap being investigated.

This is source analysis of the sealed integrated-v2 candidate, not identification of the native minimum_off crash branch. That stream ended with zero callbacks and a terminal assertion; the actual pending root/action/readset branch has not been logged. The existing diagnostic remains the way to distinguish nested scheduling from a readset rejection. Pending is neither CSS invalidity nor a semantic-cycle certificate.

## Concrete missing transitions

1. `poll_frames` returns an existing FontUnits `ComputationPending` unless `computed_size_ready` already succeeds. It does not start a new size request from that branch. For a newly reached pending frame, it installs its prerequisite only when `depth == 0`. Thus the outer lookup's nonzero-depth traversal does not return an actionable child request.
2. `metric_action_is_current` validates the single `metric_action` against the frame at `depth - 1`, requiring that frame to own the action and remain in Publish with pending publication. A size child targeting an earlier, already-pending FontUnits node cannot simply reuse the outer action's identity or owner. An explicit pending-node/depth authorization is missing.
3. `drive_metric_action` and `resolve_metric_lookup` share `metric_lookup`, `lookup_reply`, `metric_references`, and the current action slot. Child References/Lookup must not overwrite the suspended outer parser request. `resolve_metric_lookup` correctly puts the outer lookup back on any nonterminal outcome, but that retention alone supplies no child execution path.
4. `prepare_computed_size` clears `self.metric_action` when it publishes a facet. Calling it under the outer action without a changed ownership contract would clear the outer owner. Returning Published therefore does not currently establish that the outer continuation survived.
5. `can_start_computed_size` and the later selected readset checks can reject legitimate ownership conflicts or unsupported ordering. `prepare_computed_size` can return References, Lookup, Invalidated, or ComputedSizeReadset. A finite list of effects in the publication model does not establish that those native prerequisites terminate or may be applied while the outer request is retained.

## Smallest useful extension once the interface is fixed

Extend the existing `SizePublication` model by a single explicit suspended-action frame, not a second CSS evaluator. The retained outer record needs root/session identity, action and prerequisite identity, exact selected raw declaration and longhand, request identity, parser continuation, generation/flags, traversal depth and semantic floor, and the outstanding reply state. The native representation may retain these through owned existing structures rather than copying every field. The proof must state which slots are moved and which are shared.

A child authorization must join an exact computation-pending FontUnits node whose semantic closure is already established, its owning frame or deferred frame, the same root/session, and a waiting Unit consumer with exactly ComputedSize demand. It must also establish that the child's selected preparation and effect claims can coexist with the outer retained claims. The scheduling relation is not an additional CSS dependency edge. A foreign open semantic ancestor must retain the existing blocking boundary; no SCC is inferred from the child request.

The transition sequence should be observable in the eventual native interface:

```
outer lookup pending
  → suspend exact outer continuation; authorize child owner
  → advance retained child selection/lookup/effects, preserving outer record
  → publish size facet; retain whole FontUnits publication as Pending
  → deliver exact demand-tagged reply to the waiting Unit frame once
  → restore outer continuation and resume its original request
```

The last step does not imply that the outer lookup, outer action, or whole FontUnits node has completed. The resumed outer computation may legitimately wait on another prerequisite. A theorem should prove one child completion and one resumption handoff, not general scheduler termination.

The extension can reuse `step_preserves_safe` and `accepted_trace_preserves_safe` for publication/effect safety. It must additionally derive preservation of the suspended outer record from each executable child transition, reject replies with a different session/node/request or stronger demand, and consume the child handoff token exactly once. Whole-node completion and ordinary priority completion must remain distinct from the size facet. Reset or retirement must reject a retained child/outer continuation; invalidating a size certificate cannot repair a value already consumed.

Conditional progress needs a well-founded rank for an actual enabled child plan: finite retained selection and substitution steps under stable completed bindings, plus a finite ordered set of currently authorized native effects. Every successful internal step must lower that rank; a Pending reply must leave state intact and must not be counted as progress. The premise must exclude unresolved child prerequisites or explicitly provide their completed results. Merely assuming an accepted event trace, or assuming that a callback eventually returns Ready, would not prove this obligation. The current source gives neither a child-owner transition system nor such an enabled-plan certificate.

## Required discriminators

Future executable controls should cover the already-existing pending FontUnits node and a new node; an exact size-only consumer versus a metric consumer; unchanged outer raw/request/parser state through child suspension; wrong node/session/longhand replies; duplicate handoff; child publication that clears the outer action; blocked child lookup with unchanged rank; and an actual foreign semantic ancestor. An empty or unresolved child plan must not prove unconditional progress. Native minimum off/on forms and both root orders remain implementation tests, not consequences of an abstract ownership theorem.

The existing publication model's four effect names, Nat-valued size labels, and supplied effect outputs are abstractions. It proves safety of accepted effects, not native readset validity, selected-declaration eligibility, claim availability, minimum-font ordering, numeric conversion, or CSS cycle semantics. Extending it before the ownership interface is specified would require inventing the very transition that is absent. The reviewable milestone here is the exact source-backed gap and the narrow theorem boundary above; no source changes, browser runs, new model framework, or acceptance increment were made.
