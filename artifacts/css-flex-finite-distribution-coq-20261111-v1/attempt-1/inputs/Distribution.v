Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget Weights ShareTarget Share Target ConversionTarget Conversion DistributionTarget.
Open Scope R_scope.

Theorem rounding_bridge_target : RoundingBridgeTarget.
Proof. intro x. reflexivity. Qed.

Theorem stored_target : StoredTarget.
Proof.
  intros weights weight [Hcount [Hvalid Hin]]. unfold storedShare.
  destruct (Req_EM_T weight 0) as [Hzero | Hnonzero]; [lra | ].
  assert (Hweight : FiniteWeight weight).
  { rewrite Forall_forall in Hvalid. exact (Hvalid weight Hin). }
  destruct Hweight as [[Hnonnegative Hbounded] Hrepr].
  pose proof (Share.share_target weights weight Hcount Hvalid Hin ltac:(lra)) as Hshare.
  exact (proj1 (proj2 (proj2 Hshare))).
Qed.

Theorem choice_target : ChoiceTarget.
Proof.
  intros weights weight Hinputs.
  pose proof (stored_target weights weight Hinputs) as Hrange.
  unfold finiteChoice.
  destruct (Req_EM_T (storedShare weights weight) 1).
  - exact I.
  - destruct (Rlt_dec 0 (storedShare weights weight)); [exact Hrange | exact I].
Qed.

Theorem delta_target : DeltaTarget.
Proof.
  intros free weights weight Hfree Hinputs.
  exact (Conversion.safety_target free (finiteChoice weights weight) Hfree
    (choice_target weights weight Hinputs)).
Qed.

Lemma singleton_share : storedShare (1 :: nil) 1 = 1.
Proof.
  unfold storedShare. destruct (Req_EM_T 1 0) as [Hbad | Hgood]; [lra | ].
  destruct Share.witness_target as [Hfinite [Hsum Hshare]].
  rewrite Hsum. exact Hshare.
Qed.

Theorem whole_target : WholeTarget.
Proof.
  intro free. split.
  - split; [cbn; unfold countLimit; lia | ]. split.
    + constructor; [exact (proj1 Share.witness_target) | constructor].
    + left. reflexivity.
  - unfold finiteDelta, finiteChoice. rewrite singleton_share.
    destruct (Req_EM_T 1 1) as [Hgood | Hbad]; [reflexivity | contradiction].
Qed.

Theorem zero_delta_target : ZeroDeltaTarget.
Proof.
  intros free weights. unfold finiteDelta, finiteChoice, storedShare.
  destruct (Req_EM_T 0 0) as [Hzero | Hbad]; [ | contradiction].
  destruct (Req_EM_T 0 1) as [Hbad | Hone]; [lra | ].
  destruct (Rlt_dec 0 0) as [Hbad | Hzero']; [lra | reflexivity].
Qed.

Theorem full_finite_distribution_target : FullFiniteDistributionTarget.
Proof.
  exact (conj rounding_bridge_target (conj stored_target (conj choice_target
    (conj delta_target (conj whole_target zero_delta_target))))).
Qed.

Print Assumptions rounding_bridge_target.
Print Assumptions stored_target.
Print Assumptions choice_target.
Print Assumptions delta_target.
Print Assumptions whole_target.
Print Assumptions zero_delta_target.
Print Assumptions full_finite_distribution_target.
