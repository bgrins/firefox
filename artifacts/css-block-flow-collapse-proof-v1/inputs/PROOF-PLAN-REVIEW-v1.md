# Review of the proposed companion scope

The proposed signed-margin join, endpoint counterexample, late guard refinement and exact native capsule are appropriate. The separation between collected start margins and collapse-through output is essential: a positive block can still contribute its first child's start margin. Guard fixtures must therefore include a positive block with an empty first child that has a larger start margin, followed by a later outside sibling; a mutation that returns early must be detected by lost legitimate start membership.

One source-state distinction must be explicit. ComputeCollapsedBStartMargin initializes aBlockIsEmpty after the first block's normal lines. A subsequent nonempty overflow or next-in-flow line stops traversal, but its assignment to false is conditional on !setBlockIsEmpty. If the first normal-line pass already initialized true, that later line does not overwrite it. The function's result cannot be silently identified with a structural assertion that every line in every fragment is empty.

An exact full-function adapter must preserve this state transition. Include a fixture with empty normal lines and a nonempty overflow line, and another with a nonempty next-in-flow line. Record both the traversal stop and the returned emptiness value. This is an existing source behavior, potentially reflecting first-fragment semantics; this review does not classify it as a browser bug.

For the abstract finite-tree theorem, either state that its domain is ordinary normal-line trees without overflow/continuations, or explicitly define output-initialization/fragment semantics and prove that more detailed contract. The next-sibling admission theorem should use the child's actual returned eligibility; strengthening that premise to all-subtree emptiness requires a separate justification. Finite native tests with overflow/continuations do not prove that stronger theorem.

Provider assumptions should distinguish resolved whole-element content-box constraints from remaining fragment extent. NS_UNCONSTRAINEDSIZE is a tagged unknown in the model; the native bridge must use its exact numeric identity and ensure ordinary maximal finite values are represented consistently. The existing hidden-parent exemption is an explicit semantic branch, not a positive-size guard failure.

No full reflow, fragmentation, global IsSelfEmpty or source-to-ReflowInput provider theorem is implied. This plan review approves beginning the bounded companion after the provider controls; it is not a proof acceptance.
