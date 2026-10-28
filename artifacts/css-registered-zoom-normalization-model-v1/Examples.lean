import Normalization
namespace RegisteredZoomExamples
def scaledTokens (scale canonical : Nat) := scale * canonical
def doubleCssom (scale canonical : Nat) := canonical / scale
def wrongScaleNormalization (usedScale laterScale canonical : Nat) :=
  usedScale * canonical / laterScale
example : (2 * 10) / 2 = 10 := by decide +kernel
example : 2 * ((2 * 10) / 2) = 20 := by decide +kernel
example : (2 * 10) / 4 = 5 := by decide +kernel
end RegisteredZoomExamples
