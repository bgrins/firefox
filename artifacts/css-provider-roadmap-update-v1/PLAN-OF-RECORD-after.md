# CSS and Stylo verification plan

## Current state

Fix 139, registered-value zoom normalization, is committed as `0f40801f1418318e51f81b4e273c758a9a24b3e4`, with its research and validation in preceding commits. The standalone comparison repairs 56 of 70 focused assertions; 14 controls stay passing. The final cleaned build passes all 86 focused assertions. The 566 broad assertion signatures remain unchanged, including historical failures; six passing reftests have an exact diagnostic-port comparison. Container normalization follows CSSWG resolved intent with the remaining draft wording gap disclosed. Preserve this seven-file native change and its seven WPTs when restoring any parked prototype.

The separate registered-provider readiness discrepancy now reproduces in installed Firefox 158.0, BuildID 20261007201254, release SourceStamp `eb9a6e3a736802c8e080a76c44dc81f409d99d54`: 28 PASS and four FAIL across the original mixed16 and line-height-only16 fixtures. All 32 full assertion signatures match prior local observations. A provider computes to vertical-rl while its writing-mode consumer retains horizontal-tb. The run used current repository WPT preferences; it is not a stock-profile browser-tab observation. Source, application, index and temporary-process preservation passed. See [release evidence](../css-registered-provider-release-observation-runtime-1/REPORT.md).

The general provider-default repair remains unaccepted. The first recursive cycle-bit draft has a concrete counterexample: a cyclic provider can consume a newly defaulted acyclic fallback and escape with the wrong participant's initial. The repair must preserve actual cycle-participant marks across fallback evaluation and check them on unwind. The source review is backed by the normalized [cycle/default model](../css-registered-provider-cycle-default-model-v1/README.md), with 19 audited declarations and six rejected false claims. This is not a proof of native SCC construction or parser equivalence.

The expanded local baseline completed 775 assertions: 679 PASS and 96 FAIL, with 30 OK harness endings and six passing reftests. All prior 668 full assertion signatures are unchanged. The 34 missing-reference/cycle controls all pass and are regression gates, not newly discovered bugs. See [expanded baseline evidence](../css-registered-provider-expanded-observation-runtime-baseline-1/REPORT.md).

The separate JavaScript registration probe has 12 passing controls and nine failures: dependent container lengths, scheme-dependent colors and nested forms are accepted without SyntaxError. Symbolic currentcolor and equal-branch image controls pass. These are local observable leads; release confirmation and independent native fixes remain pending. The four @property color observations fail their initial calibration: ordinary invalid defaults follow the element scheme while cached no-declaration initials do not. Their conditional specification oracle and full snapshots must remain explicit when comparing the candidate.

## Next execution gates

1. Preserve the completed expanded provider baseline and the original mixed16, line-height-only16 and supplemental32 fixtures exactly. Add missing references, root/inherited defaults, typed-attribute cases, distinct-initial self/mutual cycles, the cyclic acyclic-fallback counterexample and nonparticipant consumers. Review every oracle before using it as a gate.
2. Finish the general provider-default implementation, compile it, and compare against the exact baseline. Preserve inherited values and taint, CSS-wide semantics, normal initial behavior, participant invalidation and registered-value zoom. A build or focused pass alone is insufficient acceptance.
3. Test registration-independence probes separately. Distinguish JavaScript registration from current @property wording, CSSWG proposals, symbolic computed values and genuinely dependent initial values. Fix confirmed admission defects independently, with their own WPTs.
4. Resume the parked numeric-admission repair and actual pending-provider collection after the readiness/default boundary is sound. Rebase over the accepted zoom fix; do not replay old prototype controllers onto the new accepted base. Preserve all 50 original prototype snapshots, the 140-entry recovery inventory and 74 unfinished project files.
5. Complete joint ordinary/animated/prioritary resolution with current-base freshness, selected dependency edges, correct cycles, endpoint isolation, effect publication and memory reporting. The callable typed-demand resolver has passed 20 native tests, but production integration remains unfinished.
6. Continue Bloom milestones 1–6 and broader specification correspondence. Keep every accepted native fix plus its relevant WPT in a standalone commit, with research/tooling preceding it. Commit research frequently and keep all work local.

## Accepted fixes

**138 accepted fixes: 138 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 19 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 15 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **138** | **0** |

Fix 121 now includes its validated one-block expectation correction. The signed history rewrite preserves the final tree; current commit IDs below come from the [new rewrite receipt](../../artifacts/css-integer-stored-range-history-publication-runtime-v1/RESULT.json). Historical signing receipts retain their original IDs. All 138 accepted fixes remain committed; held repair 120 stays excluded.

## Formal verification boundaries

The canonical Lean library remains at `162b20fb7c53a0ab89b20875a965baee98fb66bb`, with previously verified 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints. These counts have not been rerun or expanded by the readiness work.

The separate provider-readiness model has 11 audited declarations and two rejected false claims. It establishes a conditional stale-cache scheduling witness. The cycle/default model establishes participant-preserving publication laws under explicit classification premises. The separate exact A/B/C fallback witness adds seven checked declarations and three rejected false claims, formalizing the source-review counterexample to the scoped-bit draft. Earlier substitution, guard, bitflag, zoom-quantization and axis-provenance models retain their scoped claims. None establishes universal native correctness or complete CSS-spec coverage.

## Historical evidence

The prior plan text is preserved verbatim in [the readiness roadmap preimage](../css-provider-roadmap-update-v1/PLAN-OF-RECORD-before.md); it contains dated intermediate states that are no longer current. Earlier milestones remain in [the historical archive](PLAN-OF-RECORD-20261027-HISTORY.md) and signed Git history. Held repair 120 remains outside accepted counts.
