# Reproduced issues awaiting a repair

This supplements the 168-entry browser repair catalogue. Entries here have no
standalone repair commit and do not increase that repaired-work count.

| Issue | Relative priority | Evidence | Remaining work |
| --- | --- | --- | --- |
| Animation-tainted var() accepted in nonanimatable destinations | B: ordinary-size CSS interoperability; no demonstrated security impact | Same three current-text failures and one passing control in local browser and installed Nightly162.0a1; see ../css-animation-taint-calibration-runtime-20261110-v1/README.md | Resolve acquisition/lifetime and inheritance policy, implement provenance without regressing attribute-taint, validate and deliver one source+WPT commit |

The inheritance expectation is under discussion in
[CSSWG13933](https://github.com/w3c/csswg-drafts/issues/13933). Existing-bug/WPT
prior-art review is ongoing; novelty is not claimed. The separate stale timeline
registry/recurrence hypotheses are not confirmed issues.
