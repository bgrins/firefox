# Relative flex-item offsets affect exported baselines

The installed release and shared local browser return identical twelve-case observations: eight nonzero-offset mismatches and four zero-offset controls. Every input-size, item-offset, removal, and restoration calibration passes. A ten-pixel child offset moves the ancestor box ten pixels in the opposite direction through baseline alignment. Both first/last baselines and outer inline/flex alignment are affected.

The lead came from extending the retained-frame baseline proof and inspecting actual versus normal frame positions. It is independent of natural-donor selection: the release browser, without that repair, exhibits the same error. See SPEC-SOURCE-TRACE.md for the normative rule composition and RESULT.json for exact browser identities. Private browser profiles were removed after each run. This frozen artifact records discovery; repair evidence is in css-flex-relative-baseline-fix-v1.
