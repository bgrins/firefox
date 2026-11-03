import Rebind
open ProviderRebind
example : (complete (refresh world (invalidate .b pending))).node.installed.value = 56 := by decide +kernel
