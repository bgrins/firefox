# Explicit sticky inset aliases the auto encoding

Runtime-confirmed separate lead; no patch or acceptance. The masked-clamp proof requires explicit inset values not to equal the reserved NS_AUTOOFFSET code. Source inspection found that ComputeStickySideOffset returns the numeric resolution directly after its actual-auto branch. This prompted a calibrated browser boundary probe.

Both installed Firefox158 and the shared build produce the exact same32rows:8failures and24matching controls. Near insets17895698px and1e9px act like auto on both physical axes, before and after100px scroll. Values up to17895697px remain active. The fixture measures100px scrollport,1000px containing block and10px target; actual scroll and non-auto computed inset are checked. Expected movement uses the containing-block-limited directed clamp. Thus the tree is small, although the explicit inset is extreme. Both runs keep stable binary/source/fixture hashes and remove their private profiles.

The likely cause is numeric resolution reaching nscoord_MAX, also NS_AUTOOFFSET. Exact length-resolution source confirmation is pending. This is distinct from the previously confirmed finite geometric-limit sentinel: the failure occurs before limit construction loses the original explicitness. The existing positional repair does not claim to fix this encoding issue.

A proposed separate repair reserves the auto code when storing an explicitly resolved side offset. Its exact clamp policy, provider range, all-side coverage, arithmetic consequences and independent proof still require review. No native file has changed for this lead; no fix count or security claim is added.

Specification basis: https://drafts.csswg.org/css-position-3/#stickypos-insets . Existing sentinel review retains the primary draft and per-side non-auto trace.
