# Isolate the getter dependency check

This version changes only the font-dependency scenario of the earlier eight-case conformance proposal. The first baseline reached four getter assertion failures and three control passes, but its animated-font case stopped at an earlier 10px-versus-15px setup assertion. That case is retained unchanged in v1 and investigated separately; it is not treated as a getter failure.

The replacement uses the existing relative-values CSS animation, changes the target's unanimated font to 20px, checks that computed font, and expects getter margins 20px/40px. This tests current dependency freshness without assuming animated-font sampling is already correct. The unused changing-font rule is removed. All other seven callbacks are unchanged. The fixed source/custom contexts, current Web Animations contract and specified-branch controls remain those reviewed in v1.

Node syntax checking passed. Browser execution and complete failure-stage review are pending. This is a diagnostic/regression proposal, not a counted or committed native fix. No live WPT or native source was changed.
