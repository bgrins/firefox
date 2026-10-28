import Mapping
open LineHeightContext
example : genericMap (some exampleContext) (.percentage 1) = correctedMap exampleContext (.percentage 1) := by decide +kernel
