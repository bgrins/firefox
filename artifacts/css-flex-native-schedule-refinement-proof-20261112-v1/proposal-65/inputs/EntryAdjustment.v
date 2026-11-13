Require Import Reals ZArith List Psatz.
Require Import PrefixTarget ReverseTarget Target ConversionTarget Conversion EntryModel EntryTarget.
Import EntryAcquisition InitialEntryTarget.
Open Scope Z_scope.
Lemma entry_adjust_bound : forall current desired bound,
  0 <= bound -> -bound <= desired <= bound ->
  -bound <= adjustAvailable current desired <= bound.
Proof.
  intros current desired bound Hb Hd. unfold adjustAvailable.
  destruct (Z.ltb 0 current) eqn:Hc.
  - apply Z.ltb_lt in Hc. destruct (Z_le_dec current desired).
    + rewrite Z.min_l by lia. lia.
    + rewrite Z.min_r by lia. lia.
  - apply Z.ltb_ge in Hc. destruct (Z_le_dec current desired).
    + rewrite Z.max_r by lia. lia.
    + rewrite Z.max_l by lia. lia.
Qed.
Lemma entry_small_fits : forall value, SmallDomain value -> Fits64 value.
Proof. unfold SmallDomain, Fits64. intros; lia. Qed.
Theorem entry_adjustment_target : AdjustmentTarget.
Proof.
  intros current original factors Hcurrent Horiginal Hfactors.
  assert (Hd : SmallDomain (integerDelta original (Fraction factors))).
  { apply factor_integer_target; [exact Horiginal|lra]. }
  assert (Ha : SmallDomain (adjustAvailable current (integerDelta original (Fraction factors)))).
  { exact (entry_adjust_bound current (integerDelta original (Fraction factors)) 576460752303423488 ltac:(lia) Hd). }
  exact (conj Hd (conj Ha (entry_small_fits _ Ha))).
Qed.
Theorem entry_branch_target : BranchTarget.
Proof.
  split.
  - intros line original round Hzero. unfold execute, prepare. rewrite Hzero.
    destruct (Z.eq_dec 0 0); [|contradiction]. cbn [enters selectedBranch originalAfter entryFree events finalFree].
    repeat split; reflexivity.
  - split.
    + intros line original round Hfree Hweight. unfold execute, prepare.
      destruct (Z.eq_dec (roundFree line round) 0); [contradiction|].
      rewrite Hweight. destruct (Req_EM_T 0 0); [|contradiction].
      cbn [enters selectedBranch originalAfter entryFree events finalFree]. repeat split; reflexivity.
    + split.
      * intros line original round Hfree Hweight Hfactor. unfold prepare.
        destruct (Z.eq_dec (roundFree line round) 0); [contradiction|].
        destruct (Req_EM_T (total (run (items round))) 0); [contradiction|].
        destruct (Rlt_dec (factorTotal (factorRun (items round))) 1); [|lra].
        split; reflexivity.
      * intros line original round Hfree Hweight Hfactor. unfold prepare.
        destruct (Z.eq_dec (roundFree line round) 0); [contradiction|].
        destruct (Req_EM_T (total (run (items round))) 0); [contradiction|].
        destruct (Rlt_dec (factorTotal (factorRun (items round))) 1); [lra|].
        split; reflexivity.
Qed.
Print Assumptions entry_adjust_bound.
Print Assumptions entry_small_fits.
Print Assumptions entry_adjustment_target.
Print Assumptions entry_branch_target.
