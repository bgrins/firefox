Preliminary paired-phase review. Restoration of session83213 is not yet authenticated; this is not acceptance or a terminal runtime seal.

Activated draft40cde4e016c37181d5e2b03f7496e0d2330ed887eb70bf53645431f95486e51b and proposalc307d6f14f06bfd83ea62de928f4f5ec9a42a8693b79952629df645423220da0 authenticate. The independent checker recounts raw events rather than trusting COMPARISON totals, verifies exact52 identities/six harness starts+OK ends, both successful builds, no recorded infrastructure faults, and cleanup group absence. Retained raw and RUN event bodies agree. Each phase's full405 source/resource/binary map is unchanged across WPT and joined to its built binaries.

| Group | Baseline | Candidate |
|---|---:|---:|
| Visible-resize getter/conversion, vw/vh, one/two iframe levels | 8FAIL | 8PASS |
| One-level hidden-only and hidden-resize | 8FAIL | 8PASS |
| Two-level hidden-resize | 4FAIL | 4PASS |
| Two-level hidden-only | 4PASS | 4PASS |
| Existing SVG length and CSSOM controls | 28PASS | 28PASS |
| Total | 32PASS/20FAIL | 52PASS |

Every baseline failure is the exact first-value assertion, after the fixture's initial iframe/root-size, parsed-unit, initial-value, host-visibility, pre-resize host-size, reveal-size and (for conversion) destination-unit checks. Values are copied before reveal. First failures prevent the later repeat assertion from running: baseline repeat values are not independently retained, so baseline repeat stability is not established. Candidate PASS covers both first and repeat assertions. The two-level fixture hides/resizes the outer owner only; it does not exhaust independently hidden levels or arbitrary embedding chains.

The eight visible-resize repairs overlap expanded114's source-context refresh problem. The twelve hidden repairs are additional to that visible class: one-level hide-only returns30/15 instead of24/12, one-level hidden-resize returns30/15 instead of46/26, and two-level hidden-resize returns24/12 instead of46/26. These source-conditioned values do not prove which native fallback branch executed; there was no native tracing in this campaign. The four two-level hide-only cases already pass baseline.

Independence scope: baseline source hashes are exact HEAD90 objects, with empty native diff recorded; all30 working modifications were normalized through33 saved paths. Candidate changes exactly five source roles from the reviewed standalone variant. The DOMSVGLength header remains HEAD, and accepted114/115 native overlays are absent; this is not the installed-overlay candidate. The guarded source map contains56 paths and both phases preserve the staged index identities. This establishes independence from pending114 and other pending native overlays for these tests. HEAD90 already contains105 committed fixes; it is not pristine upstream. The reviewed driver enforces the whole native modified-path inventory before/after each phase; we independently authenticate its code and recorded source maps rather than read the currently restoring native tree.

No phase evidence blocker found. Final restoration must still bind a terminal root receipt, original source/resource/index equality, eight installed test identities, owned-test removal and a successful rebuild with actual restored binary pins. Mixed-stack installed-overlay integration also remains a separate acceptance gate. PRELIMINARY-CHECK.json intentionally contains no guessed runtime FILES pin or restored binary claim.
