import Independence
open SelectedIndependence
example : compute (fun _ => 0) lostEvidence.value = compute (fun _ => 1) lostEvidence.value := by
  decide +kernel
