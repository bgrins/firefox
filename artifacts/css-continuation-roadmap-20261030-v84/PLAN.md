# CSS verification continuation

The four-depth comparison is complete. Both original and candidate fail all four first-read assertions. The candidate recovers at later frames for depths 1, 2 and 4; depth 8 remains stale through the three-frame observation window. Literal and initial calibration controls pass. These are results on our local builds, not release-browser or clean-upstream measurements. The duration candidate is not accepted.

| Intermediate nodes | Expected final opacity | Original: first read, frames 1–3 | Candidate: first read, frames 1–3 |
| ---: | ---: | --- | --- |
| 1 | 1 | 0, 0, 0, 0 | 0, 1, 1, 1 |
| 2 | 0 | 1, 1, 1, 1 | 1, 0, 0, 0 |
| 4 | 0 | 1, 1, 1, 1 | 1, 1, 0, 0 |
| 8 | 0 | 1, 1, 1, 1 | 1, 1, 1, 1 |

Root independently replayed the records and verified full source/application restoration. The retained 1,008,605,176-byte backup was verified and removed. No build or browser experiment remains active. The inherited assessment error mentioning 32 callbacks is inaccurate diagnostic wording; the actual roster, raw results and checks contain four. Sealed historical output is preserved.

A fresh user-requested untracked audit finds the same 563 paths: 53 WPT prototypes and 15 native/support files match their committed recovery copies byte for byte; the other 495 paths have unchanged recorded metadata. Their contents were not read. Staging is empty, the held custom_properties.rs integration is the only tracked modification, and the nested Lean checkout has only .DS_Store untracked. Ignored research artifacts are checked separately in the explicit checkpoint selection.

The isolated DAG completion model adds 23 theorem audits and six rejected false controls. It proves completion and uniqueness for a finite ranked graph with fixed rules and complete dependency notification, including incremental edits. It does not prove that Gecko's scheduling implements that model. Canonical CSS Lean coverage is unchanged.

Next actions:

1. Commit the completed research in fresh checkpoint V80, then publish the already validated min/max and logarithm fixes as separate native/WPT commits with their ledger entries. Preserve signing failures; never fall back to unsigned commits or publish unrelated prototypes.
2. Design and validate same-query completion for descendant timing dependencies. The depth failures and earlier late-Pending trace motivate this work. A fixed traversal count or later-frame recovery is insufficient; the native bridge must establish admission, complete dependency notification, progress and termination.
3. Resolve same-element timing-source policy before broadening the native repair. The existing base-style API removes animation origins but needs a separate timing input, correct invalidation and branch verification; wholesale replacement would also change keyframe/effect inputs. Root-unit caches and custom-property taint need explicit treatment. The exact specification bridge remains inconclusive.
4. Obtain an executed cross-engine comparison. Safari driver admission failed because remote automation is disabled, without changing settings. An official portable Chrome for Testing plan is reviewed, but no binaries have been downloaded or launched. Dependency, signature and feature-admission checks remain required before interpreting CSS outcomes.

Accepted native fixes remain 149. New research and candidate results do not increment that count. [Work table](WORK-TABLE.md), [paired depth interpretation](../css-contextual-duration-finite-depth-pair-interpretation-v1/README.md), [untracked audit](../css-untracked-user-recheck-20261030-v4.json), [previous roadmap](../css-continuation-roadmap-20261030-v83/PLAN.md).
