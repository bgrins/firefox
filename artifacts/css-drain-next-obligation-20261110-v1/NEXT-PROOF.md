# Concrete implementation: lifetime-to-phase refinement

Extend the existing obligation/descending-phase contract with explicit ElementData lifetime state. The new work is a refinement boundary, not another general termination proof or finite browser run.

Retain a finite stable ranked tree and full obligation identity (target, pseudo, cascade, generation). Track whether each target has style data, a logical lifetime serial, and an admission ticket. A ticket comes from finite initial work or a named strict-ancestor application that cleared its previous data. Pointer reuse does not merge tickets or generations.

Source-shaped transitions:

1. Clear descendants affects only strict descendants and only data that exists. The producer keeps its data. Each actual destruction may authorize one replacement lifetime, charged to this application cause. Re-clearing an absent target does not create another ticket.
2. Ensure data consumes the available ticket only when the target lacks data. Repeated ensuring of an existing target neither allocates another lifetime nor creates another normal obligation.
3. Installation or justified retirement resolves an obligation with its complete lifetime identity. Destroying data does not count as installation, and an old installation cannot discharge a recreated lifetime.

Prove producer preservation, idempotence of clear-absent/ensure-present, unique causal admission, and a bound on recreated admissions in terms of initial tickets plus actual ancestor-caused destructions. Connect this to the existing descending-phase theorem under its closed-cause premise. Do not assert the finite tree alone proves a bound on applications. Include an unrestricted-renewal counterexample/control and a control rejecting lifetime-erasing obligation identity.

The model epoch seals DOM/frame replacement and new sampling outside one StyleDocument call. This is supported for the inspected outer frame/post-traversal callsites; it is not a universal native theorem. Same-rank or upward management inside the drain must remain explicitly unsupported unless supplied with a separate proved budget. Calling it external is not permission to ignore an actual inner-loop caller.

Deliver a source-only Lean module, executable small-tree observations, exact false-control rejection, clean replay and a short mapping table to the pinned native functions. Reuse the prior phase/conservation contracts where practical. No native patch is necessary for this scoped refinement result.

A narrower production scheduler would additionally need cause-bearing work items: the current target/pseudo eligibility queues do not identify a certified font-only subset. A future phase-owned worklist must preserve all observable installation/retirement and retain the 164-case first-read gate. Neither a fixed traversal cap nor dropping unsupported work is an acceptable silent narrowing.
