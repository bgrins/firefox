import Rebind
open ProviderRebind
example : badRebind.node.installed.value = expected changed badRebind.parent := by decide +kernel
