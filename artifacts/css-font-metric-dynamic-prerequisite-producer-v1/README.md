# Owned dynamic prerequisite preparation

This source successor builds on sealed ordinary-ownership `49c74e5a`, with the same provider `90acb505`. It adds a retained preparation route for reached dynamic Appearance and FontFamily declarations. It does not include either diagnostic overlay, change CSS semantic edges, or implement the computed-size facet needed for the full variable-length case. The foundation's separate native Cargo success does not compile or validate this successor.

## Production change

`ComputationStatus::Prepare(LonghandId)` carries an explicit preparation request. Longhand identity supports the existing equality contract without adding traits to PrioritaryPropertyId. The real ordinary recursion, the shared PriorityCompletion ordinary helper, and `publish_closed` all propagate any non-Ready status while unwinding ordinary active markers and retaining the popped publication payload.

The retained Context passes `prepare_dynamic=true`. After real generated prerequisites have returned Ready, a reached Appearance or FontFamily declaration chain containing dynamic declarations requests preparation before applying the target or setting its ensured bit. This is a conservative trigger: selection still follows eligibility and rollback, and a static winning declaration can complete without reading a dynamic loser. Existing claimed/active ownership checks remain before the ensured fast path.

A retained Publish frame forwards the request into the existing MetricAction/MetricDrain protocol. Both target allowlists now admit Appearance and FontFamily. The same declaration continuation, selected reference walk, semantic floor, owned Arc reply, local rollback state and single final publication are reused. The action and side walk do not invent a CSS edge from the suspended non-custom property to its scheduling prerequisite. A raw attribute reference back to the outer `len` waits at the existing boundary; it is not treated as invalid and does not select a fallback.

The ordinary final loop cannot suspend into this Context protocol. Its actual callsite passes `prepare_dynamic=false` and keeps its previous dynamic application behavior. This does not certify such dynamic values for retained consumers. The existing shared ownership checks remain unconditional; a pending/claimed conflict in the final loop still fails its Ready assertion. No general final-loop scheduler is introduced.

If applying Appearance changes included cascade flags, the action refreshes and clears global completion and returns Invalidated rather than importing a certificate from the previous context. The property has already been applied in this branch; its local drain completion prevents duplicate publication, but this slice does not restart or finish that context-changing path. Repeated action attempts remain invalidated. Supported progress here is limited to stable-context outcomes. A flags change during selected-reference preparation is independently rejected by the existing guard before publication.

## Saved tests

The extraction uses the actual generated nineteen-property dependency map, the real Context ordinary caller, real ordinary recursion, retained traversal/drain and final ordinary loop, and actual local servo_arc with its vendored dependency. PrioritaryPropertyId remains a distinct enum without Eq/PartialEq. Dependency memberships come exactly from data.py; the support enum discriminants and iteration order are reconstructed from that dictionary, not authenticated as the native generated enum order. CSS numeric conversion, typed parsing and final native property application are still controlled doubles; passing these tests is not a browser outcome or full native typecheck.

The 21 positive tests retain the 13 ownership cases and add eight cases covering:

- literal typed-attribute Appearance and FontFamily, and missing-attribute fallback: retained resume, one substitution/application and certified completion;
- raw attribute `var(--len)`: retained Pending before Appearance application, ensured marking or context flag change;
- rollback to another owned Arc, rejecting an old reply before consuming the new wait, and skipping a losing dynamic declaration;
- the actual extracted final ordinary loop without entering a retained graph;
- Prepare propagation through the shared ordinary ledger;
- invalidation after Appearance changes context flags, without certification or repeated publication.

Nine compiled false controls challenge swallowed Prepare, skipped owned preparation, forced preparation in the final caller, discarded preparation target, stale flag certification, consumed Pending payload, skipped reference walk, acceptance of an old Arc, and retaining raw input for a second substitution. Scratch outputs are removed.

The initial source integration test found the second allowlist in begin_metric_preparation still excluded the new targets; both allowlists are now updated. Two mutant-generator attempts had incorrect whitespace anchors and failed before compiling variants. The first exact-final-loop test omitted concatenating its extracted helper into the test crate; that test assembly error was corrected. Those initial logs are retained separately and are not successful evidence.

## Remaining boundary

The actual variable-length fixture still requires a computed-size/readiness separation: raw attr depends on `len`, which depends on FontSize, while generated scheduling reaches Appearance first. This capsule safely retains that wait and makes no claim to finish it. It does not drop XTextScale, family, language, minimum-size or genuine metric inputs, waive the dynamic completion guard, or certify an earlier ordinary effect retrospectively. Broader nested prerequisite actions, unsupported targets, context-changing outcomes and unresolved metric wait cycles remain explicit limitations. The root owns any future native check and browser validation.
