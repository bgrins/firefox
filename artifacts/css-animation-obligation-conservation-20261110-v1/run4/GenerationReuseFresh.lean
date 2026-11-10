import Obligations
open AnimationObligations
example : (install (beginTraversal selected all) all).required animationKey = false := by decide +kernel
