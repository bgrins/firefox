# Held C: current applicability and next experiment

C remains one held same-rule exclusion defect, not twenty bugs. Root reports the separate A+B+D comparison now passes all 80 callbacks with unchanged controls and restored inputs. That prerequisite result does not validate C. No C browser or native build was run in this triage.

## Exact candidate

- **C-only native overlay:** `artifacts/css-revert-rule-cold-membership-diagnostic-v1/native.patch`. It changes `properties/cascade.rs` and `stylist.rs` atop the exact A+B+D candidate. It is still a diagnostic implementation requiring native compilation.
- **Full cumulative package:** `artifacts/css-rollback-cold-c-current-patch-v1/native.patch`. It changes three Rust files and adds A16+B16+D64+C72+substitution20, totaling 188 callbacks. It must not be used as evidence that C alone is independent of A+B+D.
- Exact hashes and roles are in `CHECK.json` and pinned `INPUTS.json`. Full fixture callback names are copied unchanged into `ROSTER.json`.

| Native path suffix | Required C overlay preimage SHA256 | C candidate SHA256 |
|---|---|---|
| `properties/cascade.rs` | `f130a3db946de1f432918f28601d03b79c2fd0b10420a8d1b88f6fd6a94baa06` | `eeaa71b3921b605f8c88625ba6542e38e1baa051ac701d35039b5cc5f3c462e1` |
| `stylist.rs` | `1d31ff166603105b880aadbcd978f6dd3f41c7d2d4a9f6b6a7580ea19cd0cd21` | `fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3` |

The inherited A predicate remains required: `applicable_declarations.rs` must be A+B+D candidate `a81f348851baca75e68de9bd35c3d02f6731dba6cc57304ee5882cc44b0cca26`.

Current HEAD is `a6f39620516a4cf76a5dbf5208960adc79068cf1`. All three current native source bytes match the retained original baseline. In owned temporary copies, the full cumulative patch applied/reversed on those HEAD sources and the C overlay applied/reversed on the exact A+B+D sources, with zero fuzz/offset and exact candidate/restored hashes. Temporary copies were removed. All five WPT paths remain absent from HEAD; existing live untracked probes were neither staged nor edited. `cumulative-*.log` and `overlay-*.log` retain the operations.

## Smallest next runtime experiment

Compare **A+B+D versus A+B+D+C**, with explicit `layout.css.revert-rule.enabled=true` and fresh source/application/build bindings. Reuse the preceding A+B+D executable only if root has an authenticated retained build; otherwise rebuild that exact prerequisite. Do not compare C only against the original unpatched baseline and attribute all differences to C.

1. First run the unchanged **C72** page as the smallest practical discriminator. Historical no-C execution had 64 PASS / 8 FAIL; cold C is intended to make all 72 pass. Exact old failures are in `HISTORICAL-FAILURES.json`: four normal/important logical-last alias rows, two important-rollback/normal-physical rows, and two chained-rule rows. Wrong values were 5px or 7px instead of 37px. These are expectations for the new comparison, not fresh observations.
2. On the same build, run **substitution20** and **canvas2** before considering cold-source handling safe. Substitution20 distinguishes original declaration membership from substituted owned values and checks separate-rule preservation. Its eight same-rule rows are expected to expose the old exclusion problem by source reasoning, but have no retained native outcome here; do not count them as observed failures. The four font-size rows are separate-rule controls, not positive same-ID exclusions.
3. For broader acceptance, use the full **188 callback union plus canvas2** and existing four regression-control pages. D64 contributes sixteen C-boundary rows beyond already validated D48: twelve historically failed and four are masking controls. Those twelve failures and exact messages are also retained in `HISTORICAL-FAILURES.json`.

Canvas fixture: `artifacts/css-revert-rule-cold-membership-canvas-probe-v1/canvas-font-revert-rule-preservation.tentative.html`, with exact names in that capsule's `ROSTER.json`. It adds two preservation checks, not another defect. Literal Rule is early rejection; a missing-variable Rule fallback is predicted to reach the new direct-block membership path before late font rejection. Both should preserve the previous font and remain usable. Passing alone does not prove native membership was reached; the substituted normative integration remains an explicitly limited preservation oracle.

## Prerequisites and remaining risks

Cold C records the immutable original source block only when admitted Rule is encountered; no per-declaration pointer field is added. The direct-block caller supplies its actual guarded block; the custom-only constructor has no longhand source. Native type/lifetime checking across these calls, original-reference lookup after substitution, logical/physical mapping, source-block sharing and observation ordering remain prerequisites. Source scans can be quadratic on Rule-heavy inputs; no performance acceptance exists. Separate formal triage owns the limits of the block-identity/phase quotient.

After A+B+D lands, C can have its own production commit containing its two Rust files, necessary C/substitution WPT coverage, and the D48-to-D64 expansion. Supporting diagnostics/proofs precede it. The full base-relative package is an alternative materialization, not an extra fix to count. This note makes no new repaired-bug, universal proof or native acceptance claim.
