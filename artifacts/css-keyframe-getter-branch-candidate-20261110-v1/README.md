# Specified keyframe branch candidate

Copied candidate only; no live native edit, build, runtime result or accepted fix is claimed. The source gate is checked after the existing style flush: only an effect currently associated with CSSAnimation may invoke CSS keyframe generation. The generator result also preserves the existing setKeyframes opt-out. The same selection clears computedStyle before context-free specified serialization, preventing ordinary variable substitution on that branch.

The patch changes only KeyframeEffect::GetKeyframes and retains the proposed four-case WPT unchanged. It does not implement computed-value serialization for untouched CSS animations, modify rendering or add dependencies on the separate missing-pseudo work. Baseline exact assertion failures, independent source review and a real native comparison remain required.

The old preflush CSS check remains solely to decide whether to flush/get target style. The postflush association is checked again before selecting generated frames. This does not infer association from the CSS-derived C++ class after an effect is detached or transferred. Generated CSS endpoints and their existing base-value path remain selected for untouched associated CSS animations.
