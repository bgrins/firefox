import Demand
open ProviderDemand SelectedIndependence
example : compute (fun _ => 800) (.contextual 0) = compute (fun _ => 200) (.contextual 0) := by decide +kernel
