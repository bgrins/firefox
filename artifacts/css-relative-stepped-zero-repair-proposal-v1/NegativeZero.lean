import Stepped
open RelativeStepped
example : observe 10 (operation .mod 0) = observe 10 (folded .mod 0) := by decide +kernel
