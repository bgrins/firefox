# Reproduced issues awaiting a repair

This supplements the 169-entry browser repair catalogue. Entries here have no
standalone repair commit and do not increase that repaired-work count.

| Issue | Relative priority | Evidence | Remaining work |
| --- | --- | --- | --- |
| Animation-tainted var() accepted in nonanimatable destinations | B: ordinary-size CSS interoperability; no demonstrated security impact | Same three current-text failures and one passing control in local browser and installed Nightly 162.0a1; see ../css-animation-taint-calibration-runtime-20261110-v1/README.md | Resolve acquisition/lifetime and inheritance policy, implement provenance without regressing attribute-taint, validate and deliver one source+WPT commit |
| Non-generated pseudo target omits animated computed style (known bug 1615083) | C: existing S4 CSSOM correctness issue; no demonstrated security impact | Fresh local target.html run: six matching expected failures, 17 passing controls, one unrelated placeholder failure; see ../css-pseudo-animation-admission-20261110-v1/README.md | Review prior patch; supply pseudo animation rules and fresh effect-property sets in lazy style resolution |

The inheritance expectation is under discussion in
[CSSWG issue 13933](https://github.com/w3c/csswg-drafts/issues/13933). Targeted prior-art review is complete in css-animation-taint-contract-review-20261110-v1; novelty is not established. The separate stale timeline
registry/recurrence hypotheses are not confirmed issues.

The style-query invalidation issue is now fixed as entry 170 by signed commit `90e0949346b5` for bug 2085413. Its two Rust files and one WPT are separate from the preceding research. The final exact WPT passes 13/13; the broader comparison passes 26/26 including twelve font controls. See ../css-all-work-readout-20261110-v17/README.md.
