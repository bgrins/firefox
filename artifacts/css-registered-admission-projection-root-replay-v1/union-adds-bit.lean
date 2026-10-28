import Projection
open AdmissionProjection
example : unionMutant (fun _ : Unit => false) (fun _ => true) () = false := by
  decide +kernel
