# Scoped lookup cleanup

This inactive successor removes the now-unused private `lookup_element_dependent_at_rule` helper and moves its existing best-effort lookup warning to `lookup_keyframes_with_scope`. Searchfox and immutable HEAD 5d9487828523b7086f1b425ed18caa550f8b3b61 each contain only its definition and the former keyframes call. The scoped candidate replaced that call; no cfg-specific Gecko or Servo caller remains in the candidate source. The selected lookup implementation and winner order are unchanged.

The own-shadow assigned-slot walk now occurs only after an own shadow root with style data is found. Its only result is the scope supplied to that callback; when there is no such callback the previous result was unused. Slot traversal for slotted rules, part traversal, document fallback and callback order remain unchanged. This avoids the redundant extra walk for elements without own-shadow style data; cost for the remaining cases is unmeasured.

All six other candidate bodies and the corrected four-test fixture are byte-identical to scope-v2. The resolved failed-reference result remains one, with no zero-fallback repair prerequisite. No generic arithmetic or current source fallback changes. Parser guards remain closed. Existing declaring-root lookup, scope saturation/root identity, animated-input ordering, dependency invalidation, style sharing, Servo-only configuration and context-free API obligations remain open. This cleanup is not an activation or performance-neutrality claim.

Root's active eight-source check tests scope-v2, not this successor. No compilation or browser execution of this successor is claimed. The immutable predecessor records and failed serde evidence remain preserved.
