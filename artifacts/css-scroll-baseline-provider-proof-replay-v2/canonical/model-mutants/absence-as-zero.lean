import Witnesses
open ScrollBaselineWitnesses ScrollBaselineDispatch ScrollBaselineProvider
example : (some 0 : Option Int) = (native { input with child := none }).value := by decide +kernel
