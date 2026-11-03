import Rebind
open ProviderRebind
example : expected { world with root := 24 } .b = expected world .b := by decide +kernel
