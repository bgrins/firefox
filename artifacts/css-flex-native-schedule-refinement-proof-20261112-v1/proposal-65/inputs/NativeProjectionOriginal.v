Require Import NativeRefinementSpec NativeProjectionPoint NativeProjectionTotals.
Module NativeProjectionOriginal.
Lemma projection_target : NativeRefinementTarget.ProjectionTarget.
Proof.
  intros bytes line seeds info state result Admission History Step.
  cbn zeta. split.
  - exact (NativeProjectionTotals.total bytes line seeds info state result Admission History Step).
  - exact (NativeProjectionPoint.pointwise bytes line seeds info state result Admission History Step).
Qed.
Print Assumptions projection_target.
End NativeProjectionOriginal.
