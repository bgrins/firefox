Require Import Reals ZArith List Psatz Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget ShareTarget Share Target ConversionTarget DistributionTarget Distribution InputTarget InputProof BranchTarget.
Open Scope R_scope.

Theorem weight_equivalence_target : WeightEquivalenceTarget.
Proof.
  intros [factor base growing] Hvalid.
  destruct Hvalid as [Hfactor [Hbase Hshrink]].
  unfold sourceWeight, inputWeight. cbn [InputTarget.factor InputTarget.base InputTarget.growing].
  destruct growing.
  - symmetry. exact (proj2 (InputProof.promotion_target factor Hfactor)).
  - destruct (Z.eqb base 0) eqn:Hzero; [ | reflexivity].
    apply Z.eqb_eq in Hzero. subst base.
    change (0 = WeightTarget.rn (WeightTarget.rn (value32 factor)*WeightTarget.rn 0)).
    rewrite Share.rn_zero, Rmult_0_r, Share.rn_zero. reflexivity.
Qed.

Theorem early_zero_target : EarlyZeroTarget.
Proof. intro factor. reflexivity. Qed.

Theorem source_finite_target : SourceFiniteTarget.
Proof.
  intros input Hvalid. rewrite weight_equivalence_target by exact Hvalid.
  exact (InputProof.input_weight_target input Hvalid).
Qed.

Theorem source_distribution_target : SourceDistributionTarget.
Proof.
  intros free inputs input Hfree Hcount Hvalid Hin.
  apply Distribution.delta_target; [exact Hfree | ].
  split; [rewrite map_length; exact Hcount | ]. split.
  - induction Hvalid.
    + constructor.
    + cbn [map]. constructor; [apply source_finite_target; assumption | assumption].
  - apply in_map. exact Hin.
Qed.

Theorem nonfinite_control_target : NonfiniteControlTarget.
Proof.
  exists (Binary.B754_infinity 24 128 false). split; [reflexivity | ].
  split; [reflexivity | ]. split.
  - intros [Hfinite Hvalue]. discriminate.
  - apply early_zero_target.
Qed.

Theorem full_weight_branches_target : FullWeightBranchesTarget.
Proof.
  exact (conj weight_equivalence_target (conj early_zero_target (conj source_finite_target
    (conj source_distribution_target nonfinite_control_target)))).
Qed.

Print Assumptions weight_equivalence_target.
Print Assumptions early_zero_target.
Print Assumptions source_finite_target.
Print Assumptions source_distribution_target.
Print Assumptions nonfinite_control_target.
Print Assumptions full_weight_branches_target.
