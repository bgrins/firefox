# Branch work checkpoint — 28 October 2026

Prepared at `a1f28b1578df604a67c45e2d23ab54f246941561`. All 144 accepted native fixes and two test-only repairs are committed. Fresh ancestry checks confirm all 318 distinct native, evidence and test-only commits recorded in the full ledger are ancestors of this HEAD. No new native acceptance is claimed.

| Area | Accepted fixes |
|---|---:|
| Selectors, Bloom filters and scoping | 10 |
| Cascade, layers and shorthands | 6 |
| Parsing, tokens and CSS math | 29 |
| Attributes and custom properties | 19 |
| Animations, timelines and transitions | 17 |
| Text and fonts | 16 |
| Layout, sizing and positioning | 23 |
| Container queries | 3 |
| Colors, images, SVG and shapes | 8 |
| CSSOM geometry and hidden layout | 13 |
| **Total** | **144** |

The [full table](../css-all-work-readout-20261028-v5/README.md) lists every repair and its native/WPT and evidence commits. IDs extend through 145 because held fix 120 is excluded. Separate commits may have prerequisites; this is not a claim of independent clean-upstream applicability.

| Other work | State |
|---|---|
| Original Bloom milestones 1–6 | Complete within declared selector profiles and assumptions; broader equivalence remains outside scope |
| CSS Lean library | Last recorded full check: 11,840 audited declarations, 12,438 executable cases and 173 expected-false cases; no percentage of CSS conformance claimed |
| Infinite-value Round investigation | Numeric baseline: 16 PASS, 8 FAIL; admission baseline: all 8 PASS. Held proposal is committed research, uncompiled and unaccepted |
| Combined contextual easing handoff | Six-source prototype and independent review complete; compilation and browser validation remain pending, parser guards closed |
| Configured typecheck runner | Prepared and disabled; not executed. Bound to pre-checkpoint HEAD and requires rebinding before use |
| Provider and other native prototypes | Unfinished; preserved in signed recovery snapshots, not accepted fixes |
| Untracked files | 563 expected paths: 68 project files match signed recovery copies; 495 unrelated names unchanged |

The new checkpoint archives completed research under artifacts rather than installing unfinished native changes. The held provider remains the only tracked source modification. The [untracked audit](../css-untracked-audit-checkpoint-20261028-v1/README.md) records exact scope. Final signing receipts provide the resulting commit and preservation verification. No push or Try run.
