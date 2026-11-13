Require Import Reals ZArith Lia Psatz Gappa.Gappa_library.
Require Import Flocq.Core.Raux NativeFloatModel NativeOperations NativeBinaryFacts NativeBounds.
Require Import ReverseTarget WeightTarget.
Module NativeValues.
Open Scope R_scope.
Lemma zero_finite : NativeFloat.finite NativeFloat.zero = true.
Proof. reflexivity. Qed.
Lemma zero_value : NativeFloat.value NativeFloat.zero = 0.
Proof. reflexivity. Qed.
Lemma one_finite : NativeFloat.finite NativeFloat.one = true.
Proof. vm_compute. reflexivity. Qed.
Lemma one_value : NativeFloat.value NativeFloat.one = 1.
Proof. change (4503599627370496 * /4503599627370496 = 1). field. Qed.
Lemma half_finite : NativeFloat.finite NativeFloat.half = true.
Proof. vm_compute. reflexivity. Qed.
Lemma half_value : NativeFloat.value NativeFloat.half = /2.
Proof. change (4503599627370496 * /9007199254740992 = /2). field. Qed.
Lemma free_interval : forall free, FreeDomain free ->
  -bpow radix2 60 <= IZR free <= bpow radix2 60.
Proof.
  intros free H. change (IZR (-1152921504606846976) <= IZR free <= IZR 1152921504606846976).
  unfold FreeDomain in H. split; apply IZR_le; lia.
Qed.
Lemma integer_correct : forall free, FreeDomain free ->
  NativeFloat.value (NativeFloat.integer free) = WeightTarget.rn (IZR free) /\
  NativeFloat.finite (NativeFloat.integer free) = true.
Proof.
  intros free H. pose proof (free_interval free H) as I.
  assert (S : NativeOperations.NoOverflow (IZR free * bpow radix2 0)).
  { replace (IZR free*bpow radix2 0) with (IZR free) by (cbn; ring).
    apply (NativeBounds.interval_safe 60); [lia|exact I]. }
  pose proof (NativeOperations.normalize_correct free 0 false S) as C.
  replace (IZR free*bpow radix2 0) with (IZR free) in C by (cbn; ring).
  exact C.
Qed.
Lemma floor_value : forall x, NativeFloat.finite x = true ->
  NativeFloat.floorFinite x = Some (Zfloor (NativeFloat.value x)).
Proof.
  intros x F. assert (E : exists z, NativeFloat.floorFinite x = Some z).
  { destruct x; simpl in F; try discriminate; eexists; reflexivity. }
  destruct E as [z E]. pose proof (NativeBinaryFacts.floor_correct x z E) as [_ V].
  rewrite E,V. reflexivity.
Qed.
Print Assumptions zero_finite.
Print Assumptions zero_value.
Print Assumptions one_finite.
Print Assumptions one_value.
Print Assumptions half_finite.
Print Assumptions half_value.
Print Assumptions free_interval.
Print Assumptions integer_correct.
Print Assumptions floor_value.
End NativeValues.
