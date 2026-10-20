import Witnesses
open ScrollBaselineWitnesses ScrollBaselineDispatch ScrollBaselineProvider
example : (none : Option Int) = (native { input with lineLayout := true, contain := true }).value := by decide +kernel
