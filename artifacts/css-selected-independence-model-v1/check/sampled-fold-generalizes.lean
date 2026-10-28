import Independence
open SelectedIndependence
example : compute (fun _ => 20) (sampledFold (fun _ => 10) nestedContainer) = compute (fun _ => 20) nestedContainer := by
  decide +kernel
