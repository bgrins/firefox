import Demand
open ProviderDemand SelectedIndependence
example : CanCompute .unknown (fun _ => True) := by change False; decide +kernel
