Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel.
Module NativeProjectionAlgebra.
Import NativeSchedule.
Open Scope Z_scope.
Lemma clamp_project32 : forall s raw,
  0 <= minimum s <= maximum s -> maximum s <= 2147483647 ->
  clamp s (project32 raw) = clamp s raw.
Proof.
  intros s raw B M. unfold clamp, project32.
  pose proof (Z.min_spec raw 2147483647) as A.
  pose proof (Z.max_spec (-2147483648) (Z.min raw 2147483647)) as C.
  pose proof (Z.min_spec (Z.max (-2147483648) (Z.min raw 2147483647)) (maximum s)) as D.
  pose proof (Z.max_spec (minimum s) (Z.min (Z.max (-2147483648) (Z.min raw 2147483647)) (maximum s))) as E.
  pose proof (Z.min_spec raw (maximum s)) as F.
  pose proof (Z.max_spec (minimum s) (Z.min raw (maximum s))) as G.
  intuition lia.
Qed.
Lemma corrected_difference : forall s raw,
  0 <= minimum s <= maximum s -> maximum s <= 2147483647 ->
  (project32 raw-raw) + (clamp s (project32 raw)-project32 raw) = clamp s raw-raw.
Proof. intros s raw B M. rewrite clamp_project32 by assumption. lia. Qed.
Lemma projection_correction_bound : forall base delta,
  -2147483648 <= base <= 2147483647 ->
  Z.abs (project32 (base+delta)-(base+delta)) <= Z.abs delta.
Proof.
  intros base delta B. unfold project32.
  pose proof (Z.min_spec (base+delta) 2147483647) as A.
  pose proof (Z.max_spec (-2147483648) (Z.min (base+delta) 2147483647)) as C.
  pose proof (Z.abs_spec delta) as D.
  pose proof (Z.abs_spec (Z.max (-2147483648) (Z.min (base+delta) 2147483647)-(base+delta))) as E.
  intuition lia.
Qed.
Print Assumptions clamp_project32.
Print Assumptions corrected_difference.
Print Assumptions projection_correction_bound.
End NativeProjectionAlgebra.
