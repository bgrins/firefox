Require Import Reals ZArith List Psatz Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget Weights ShareTarget Share Target ConversionTarget Conversion DistributionTarget Distribution InputTarget.
Open Scope R_scope.

Theorem promotion_target : PromotionTarget.
Proof.
  intros factor [Hfinite Hnonnegative]. split.
  - unfold FactorValid. split; [exact Hnonnegative | ].
    pose proof (Binary.abs_B2R_lt_emax 24 128 factor) as Hbound.
    change (Rabs (value32 factor) < factorLimit) in Hbound.
    rewrite Rabs_pos_eq in Hbound by exact Hnonnegative. lra.
  - unfold Representable, WeightTarget.rn.
    apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
    pose proof (Binary.generic_format_B2R 24 128 factor) as Hformat.
    change (Generic_fmt.generic_format radix2 (FLT.FLT_exp (-149) 24) (value32 factor)) in Hformat.
    apply (Generic_fmt.generic_inclusion_mag radix2 (FLT.FLT_exp (-149) 24)
      (FLT.FLT_exp (-1074) 53) (value32 factor)); [ | exact Hformat].
    intro Hnonzero. unfold FLT.FLT_exp. apply Z.max_le_compat; lia.
Qed.

Theorem integer_promotion_target : IntegerPromotionTarget.
Proof.
  intros base Hbase. unfold Representable, WeightTarget.rn.
  apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  apply FLT.generic_format_FLT.
  apply (FLT.FLT_spec radix2 (-1074) 53 (IZR base) (Defs.Float radix2 base 0)).
  - change (IZR base = IZR base*1). lra.
  - change (Z.abs base < 9007199254740992)%Z. lia.
  - cbn. lia.
Qed.

Theorem input_weight_target : InputWeightTarget.
Proof.
  intros [factor base growing] [Hfactor [Hbase Hshrink]].
  destruct (promotion_target factor Hfactor) as [Hfactorbound Hfactorrepr].
  pose proof (integer_promotion_target base Hbase) as Hbaserepr.
  cbn [InputTarget.factor InputTarget.base InputTarget.growing] in *.
  unfold inputWeight. cbn [InputTarget.factor InputTarget.base InputTarget.growing].
  unfold Representable in Hfactorrepr, Hbaserepr.
  rewrite Hfactorrepr. destruct growing.
  - split.
    + unfold FactorValid in Hfactorbound.
      unfold WeightValid, weightLimit, factorLimit in *. lra.
    + exact Hfactorrepr.
  - rewrite Hbaserepr. apply Share.scaled_target; [exact Hfactorbound | ].
    assert (Hnonnegative : (0 <= base)%Z) by (apply Hshrink; reflexivity).
    unfold baseLimit. split; apply IZR_le; lia.
Qed.

Theorem input_list_target : InputListTarget.
Proof.
  intros inputs Hvalid. induction Hvalid.
  - constructor.
  - cbn [map]. constructor; [apply input_weight_target; assumption | assumption].
Qed.

Theorem input_distribution_target : InputDistributionTarget.
Proof.
  intros free inputs input Hfree Hcount Hvalid Hin.
  apply Distribution.delta_target; [exact Hfree | ].
  split; [rewrite map_length; exact Hcount | ].
  split; [apply input_list_target; exact Hvalid | apply in_map; exact Hin].
Qed.

Definition one32 : Float32 := Binary.B754_finite 24 128 false 8388608 (-23) eq_refl.

Lemma one_value : value32 one32 = 1.
Proof. change ((8388608:R) * /8388608 = 1). field. Qed.

Lemma one_input : FactorInput one32.
Proof. split; [reflexivity | rewrite one_value; lra]. Qed.

Definition growOne : WeightInput := {| factor := one32; base := -2147483648; growing := true |}.
Definition shrinkOne : WeightInput := {| factor := one32; base := 1; growing := false |}.

Theorem input_witness_target : InputWitnessTarget.
Proof.
  exists growOne, shrinkOne. split.
  - split; [exact one_input | ]. split; cbn; [lia | discriminate].
  - split.
    + split; [exact one_input | ]. split; cbn; lia.
    + split; [reflexivity | ]. split; [reflexivity | ]. split.
      * change (WeightTarget.rn (value32 one32) = 1). rewrite one_value. exact Share.rn_one.
      * change (WeightTarget.rn (WeightTarget.rn (value32 one32)*WeightTarget.rn 1) = 1).
        rewrite one_value, !Share.rn_one, Rmult_1_l. exact Share.rn_one.
Qed.

Theorem full_input_target : FullInputTarget.
Proof.
  exact (conj promotion_target (conj integer_promotion_target (conj input_weight_target
    (conj input_list_target (conj input_distribution_target input_witness_target))))).
Qed.

Print Assumptions promotion_target.
Print Assumptions integer_promotion_target.
Print Assumptions input_weight_target.
Print Assumptions input_list_target.
Print Assumptions input_distribution_target.
Print Assumptions input_witness_target.
Print Assumptions full_input_target.
