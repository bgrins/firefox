import Rebind
open ProviderRebind
example : (complete (invalidate .b pending)).node.installed.value = 56 := by decide +kernel
