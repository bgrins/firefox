# Reproduced issues awaiting a repair

This supplements the 168-entry browser repair catalogue. Entries here have no
standalone repair commit and do not increase that repaired-work count.

| Issue | Relative priority | Evidence | Remaining work |
| --- | --- | --- | --- |
| Animation-tainted var() accepted in nonanimatable destinations | B: ordinary-size CSS interoperability; no demonstrated security impact | Same three current-text failures and one passing control in local browser and installed Nightly162.0a1; see ../css-animation-taint-calibration-runtime-20261110-v1/README.md | Resolve acquisition/lifetime and inheritance policy, implement provenance without regressing attribute-taint, validate and deliver one source+WPT commit |
| Animated custom-property changes fail to rematch container style queries ([bug 2085413](https://bugzilla.mozilla.org/show_bug.cgi?id=2085413)) | B when feature enabled; release exposure unverified | Named and unnamed color-only failures in local browser and installed Nightly, with two ordinary controls passing; explicit target matching repairs stale color | Two-file candidate passes 26 cases versus 17 baseline passes and nine failures, preserving twelve font controls; finish exact delivery WPT and commit source+test |

The inheritance expectation is under discussion in
[CSSWG13933](https://github.com/w3c/csswg-drafts/issues/13933). Existing-bug/WPT
prior-art review is ongoing; novelty is not claimed. The separate stale timeline
registry/recurrence hypotheses are not confirmed issues.
