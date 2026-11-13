Require Import Reals ZArith Psatz Gappa.Gappa_tactic.
Require Import WeightTarget ShareTarget Target ConversionTarget Conversion PrefixTarget ReverseTarget ReverseStructure.
Require Import SignTarget SignCases.
Open Scope R_scope.
Lemma sign_nonrepresentable_value : SignCases.nonrepresentableShare =
  1 - /1267650600228229401496703205376.
Proof.
  unfold SignCases.nonrepresentableShare.
  replace (2^100) with (1267650600228229401496703205376:R) by ring. reflexivity.
Qed.
Lemma sign_nonrepresentable_range : 0 < SignCases.nonrepresentableShare < 1.
Proof.
  rewrite sign_nonrepresentable_value.
  assert (Hp : 0 < /1267650600228229401496703205376) by (apply Rinv_0_lt_compat; lra).
  assert (Hu : /1267650600228229401496703205376 < 1).
  { apply (Rmult_lt_reg_r 1267650600228229401496703205376); [lra|].
    rewrite Rinv_l by lra. lra. }
  lra.
Qed.
Lemma sign_nonrepresentable_round : WeightTarget.rn SignCases.nonrepresentableShare = 1.
Proof. rewrite sign_nonrepresentable_value. unfold WeightTarget.rn. gappa. Qed.
Lemma sign_nonrepresentable_not_format : ~ Representable SignCases.nonrepresentableShare.
Proof.
  intro H. unfold Representable in H. rewrite sign_nonrepresentable_round in H.
  pose proof sign_nonrepresentable_range. lra.
Qed.
Lemma sign_forced_fraction_overshoot :
  integerDelta SignCases.huge (Fraction 1) = (SignCases.huge+1)%Z.
Proof.
  pose proof Conversion.overshoot_target as H.
  unfold OvershootTarget in H. change (integerDelta 576460752303423487 (Fraction 1) = 576460752303423488%Z).
  unfold integerDelta in *.
  replace (Target.rn (IZR 576460752303423487)/1) with (Target.rn (IZR 576460752303423487)) in H by field.
  rewrite Rmult_1_r. exact H.
Qed.
Lemma sign_nonrepresentable_overshoot :
  deltaAt SignCases.huge SignCases.nonrepresentableShare = (SignCases.huge+1)%Z.
Proof.
  pose proof sign_nonrepresentable_range as Hr. unfold deltaAt, shareChoice.
  destruct (Req_EM_T SignCases.nonrepresentableShare 1); [lra|].
  destruct (Rlt_dec 0 SignCases.nonrepresentableShare); [|lra].
  assert (Hp : Target.rn (Target.rn (IZR SignCases.huge)*SignCases.nonrepresentableShare) = 576460752303423488).
  { rewrite sign_nonrepresentable_value. unfold SignCases.huge, Target.rn. gappa. }
  assert (Hone : Target.rn (Target.rn (IZR SignCases.huge)*1) = 576460752303423488).
  { unfold SignCases.huge, Target.rn. gappa. }
  pose proof sign_forced_fraction_overshoot as H.
  unfold integerDelta in H |- *. rewrite Hone in H. rewrite Hp. exact H.
Qed.
Theorem sign_boundary_target : NativeHistorySignTarget.BoundaryTarget.
Proof.
  split; [unfold FreeDomain, SignCases.huge; lia|].
  split; [exact (proj1 (proj2 reverse_branches_target SignCases.huge))|].
  split; [exact sign_forced_fraction_overshoot|].
  split; [exact sign_nonrepresentable_range|].
  split; [exact sign_nonrepresentable_not_format|exact sign_nonrepresentable_overshoot].
Qed.
Print Assumptions sign_nonrepresentable_not_format.
Print Assumptions sign_forced_fraction_overshoot.
Print Assumptions sign_nonrepresentable_overshoot.
Print Assumptions sign_boundary_target.
