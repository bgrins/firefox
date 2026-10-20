# Development review checkpoint

No approval before the producer seal and resolution of the full-domain issues. Both issues are communicated to root and producer. `domain_challenges.py` checks the retained v1 helper's actual rect-relative prefix and endpoint bounds for two distinct cases; these are source-domain examples, not claimed browser inputs.

Initial source review finds the optional metadata cleared at entry, unsupported SVG/context/viewport/flag paths declined, and matrix cache reused on fallback. Existing callers omit the new optional parameter. Searchfox identifier discovery shows four calls to nsIFrame::GetTransformMatrix and seventeen calls to nsLayoutUtils::GetTransformToAncestor plus definitions/declarations; no function-pointer use appeared in those results. This is a bounded indexed discovery, not whole-program ABI validation.

BoxToRect avoids the wrapper for outer==relative, so helper self-route tests concern its local contract rather than a newly executed BoxToRect self path. Ancestor transforms are correctly excluded from relative coordinates; a transform before reaching the target forces matrix fallback. Existing flag semantics and matrix multiplication/projection order need final-byte recheck after arithmetic correction.

The extracted facade models affine scale/translation, frame/provider getters and cross-document traversal; it is not the actual complete GFX 3D/clipping implementation. Equality of facade trace rows cannot prove arbitrary perspective behavior. No performance or browser regression conclusion is available for this successor yet.
