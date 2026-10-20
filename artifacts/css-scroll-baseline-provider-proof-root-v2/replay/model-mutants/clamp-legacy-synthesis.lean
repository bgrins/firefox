import Witnesses
open ScrollBaselineWitnesses ScrollBaselineDispatch ScrollBaselineProvider
example : (some (clamp 59 77) : Option Int) = (native { input with lineLayout := true }).value := by decide +kernel
