# Current infinite-step guard review

The current canonical RoundSpecialKnowledge source replays successfully with the pinned Lean 4.35.0-rc4 compiler. All four existing theorems report only propext. This rechecks previously accepted model evidence; it adds no declarations or canonical coverage. The canonical source and compiled outputs were not changed. The successful tool receipt is 90f4ae followed by 871f99, exit 0. LEAN-CHECK.json retains the two setup failures before compiler execution.

The model classifies resolved values. Its unresolved_value_no_constant law shows why upward rounding with an infinite step cannot replace an unknown positive-or-negative finite value with a single class. Its NaN-priority law supports the existing runtime prerequisite. These are not proofs of Rust refinement, parser admission, AST reachability, leaf sufficiency, or arbitrary finite arithmetic.

Root read the current three-line patch and historical 19-case WPT. Four additional finite-value mutation cases are required to cover negative, zero, positive, and recovered negative contextual inputs. The 16 observations in the separate infinite-value/unknown-step branch remain outside this patch. The original and candidate must retain identical ordinary-repeat and easing controls.

Fresh CSS Values 4 review supports the oracle: two infinite operands produce NaN; finite values with an infinite step depend on strategy and sign; intermediate NaN propagates until top-level censoring. Non-arithmetic function nodes simplify only when their children supply enough numeric information. Sources: https://drafts.csswg.org/css-values-4/#round-infinities and https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree .

The draft reversible-owner delta preserves the previously executed restoration and build flow, changes its checkpoint binding to v40, and checks the completed prior pair's process groups before execution. Root reviewed that code delta in ec2029. Final source/runner manifests, disk availability, live preservation checks, and actual browser results remain prerequisites. This report is not native acceptance.

Root also read the complete v4 WPT in 2e585d and the final runner code delta in dfe2d4. The policy and admission controls were checked in 9bcab0: 23 target subtests, 689 unchanged controls, ten pages, and no waived failures. The setter check rejects unsupported syntax; the four mutation tests observe calibrated sign, font, literal results, and repeated computed values. The new three-line source is unchanged from v3.
