import Demand
open ProviderDemand SelectedIndependence
example : lookup 2 (.ready 1 800) = some 800 := by decide +kernel
