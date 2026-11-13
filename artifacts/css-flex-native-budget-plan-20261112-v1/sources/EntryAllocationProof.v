Require Import Arith PeanoNat List ZArith Lia.
Require Import EntryAllocation EntryTarget EntryNumerals.
Import ListNotations.
Import EntryAllocation.EntryAllocation InitialEntryTarget.
Open Scope nat_scope.
Lemma entry_round_bounds : forall n, 1 < n ->
  n <= roundPowerTwo n /\ roundPowerTwo n <= 2*(n-1).
Proof.
  intros n Hn. pose proof (Nat.log2_spec (n-1) ltac:(lia)) as Hlog.
  unfold roundPowerTwo. replace (Nat.log2 (n-1)+1) with (S (Nat.log2 (n-1))) by lia.
  rewrite Nat.pow_succ_r'. rewrite Nat.pow_succ_r' in Hlog. nia.
Qed.
Lemma entry_request_product : forall e n, requestValid e n -> n*e <= 2147483647.
Proof. unfold requestValid. intros e n H.
  replace (2*n*e) with (2*(n*e)) in H by (entry_numerals; nia).
  remember (n*e) as product in *. entry_numerals. lia. Qed.
Lemma entry_grown_bounds : forall e old n, old<n -> requestValid e n ->
  headerBytes+n*e <= grownBytes e old n /\ grownBytes e old n < 2^32.
Proof.
  intros e old n Hlt Hr.
  pose proof (entry_request_product e n Hr) as Hp.
  assert (Hmul : old*e <= n*e) by (entry_numerals; nia).
  unfold grownBytes, headerBytes, mib.
  destruct (8+n*e <? 8*1048576) eqn:Hsmall.
  - apply Nat.ltb_lt in Hsmall.
    pose proof (entry_round_bounds (8+n*e) ltac:(lia)) as Hb. split; [exact (proj1 Hb)|]. apply (proj2 (entry_pow32_spec _)). entry_numerals. nia.
  - apply Nat.ltb_ge in Hsmall.
    pose proof (Nat.div_mod (8+old*e) 8 ltac:(lia)) as Hdiv.
    assert (Hmax : Nat.max (8+n*e) (8+old*e+(8+old*e)/8) <= 2415919111).
    { apply Nat.max_lub; entry_numerals; nia. }
    pose proof (Nat.le_max_l (8+n*e) (8+old*e+(8+old*e)/8)) as Hreq.
    set (x := Nat.max (8+n*e) (8+old*e+(8+old*e)/8)) in *.
    pose proof (Nat.div_mod (x+1048576-1) 1048576 ltac:(entry_numerals;lia)) as Hround.
    pose proof (Nat.mod_upper_bound (x+1048576-1) 1048576 ltac:(entry_numerals;lia)) as Hmod.
    split.
    + entry_numerals. nia.
    + apply (proj2 (entry_pow32_spec _)). entry_numerals. nia.
Qed.
Lemma entry_capacity_ge : forall e old n cap, 0<e -> Capacity e old n cap -> n<=cap.
Proof.
  intros e old n cap He H. destruct H as [old requested Hle|requested Hpos Hr|old requested Hpos Hlt Hr].
  - assumption.
  - lia.
  - apply Nat.div_le_lower_bound; [lia|].
    pose proof (entry_grown_bounds e old requested Hlt Hr) as Hg.
    unfold headerBytes in *. entry_numerals; nia.
Qed.
Lemma entry_capacity_bytes : forall e old n cap,
  Capacity e old n cap -> old*e < 2^32 -> cap*e < 2^32.
Proof.
  intros e old n cap H Hb. destruct H as [old requested Hle|requested Hpos Hr|old requested Hpos Hlt Hr].
  - exact Hb.
  - pose proof (entry_request_product e requested Hr) as Hp.
    apply (proj2 (entry_pow32_spec _)). entry_numerals. nia.
  - pose proof (entry_grown_bounds e old requested Hlt Hr) as [Hg Hlimit].
    pose proof (proj1 (entry_pow32_spec _) Hlimit) as Hbytes.
    apply (proj2 (entry_pow32_spec _)).
    destruct e as [|e].
    + rewrite Nat.mul_0_r. cbn [Z.of_nat]. lia.
    + pose proof (Nat.div_mod (grownBytes (S e) old requested-headerBytes) (S e) ltac:(lia)) as Hd.
      entry_numerals. nia.
Qed.
Definition EntryArrayInvariant e state :=
  length (tokens state) <= capacity state /\ capacity state*e < 2^32.
Lemma entry_array_step : forall e before after, 32<=e -> EntryArrayInvariant e before ->
  ArrayStep e before after -> EntryArrayInvariant e after.
Proof.
  intros e before after He [Hl Hb] H. destruct H; unfold EntryArrayInvariant; cbn [emptyArray tokens capacity] in *.
  - rewrite app_length. cbn [length]. split.
    + eapply entry_capacity_ge with (e:=e); [lia|eassumption].
    + eapply entry_capacity_bytes; eassumption.
  - rewrite app_length in Hl. cbn [length] in Hl. split; [lia|exact Hb].
  - split; [lia|].
    pose proof (proj1 (entry_pow32_spec _) Hb) as Hbytes.
    apply (proj2 (entry_pow32_spec _)). nia.
  - split; [cbn [length]; lia|]. apply (proj2 (entry_pow32_spec _)). cbn [Nat.mul Z.of_nat]. lia.
  - split; assumption.
Qed.
Lemma entry_array_invariant : forall e state, 32<=e -> Reachable e state -> EntryArrayInvariant e state.
Proof.
  intros e state He H. induction H.
  - unfold EntryArrayInvariant, emptyArray. cbn [tokens capacity length Nat.mul].
    split; [lia|]. apply (proj2 (entry_pow32_spec _)). cbn [Z.of_nat]. lia.
  - eapply entry_array_step; eassumption.
Qed.
Theorem entry_allocation_target : AllocationTarget.
Proof.
  intros e state He Hr. pose proof (entry_array_invariant e state He Hr) as [Hl Hb].
  pose proof (proj1 (entry_pow32_spec _) Hb) as Hbytes.
  split; [exact Hl|]. split.
  - apply (proj2 (entry_pow31_spec _)). nia.
  - split; [exact Hb|]. entry_numerals. nia.
Qed.
Theorem entry_transfer_target : TransferTarget.
Proof.
  split.
  - intros e a b a' b' He Ha Hb H. destruct H. split; [constructor|assumption].
  - intros e xs state He H. induction H.
    + split; [constructor|reflexivity].
    + destruct IHReconstruction as [Hr Hid]. split; [|reflexivity].
      eapply next; [exact Hr|]. apply append. assumption.
Qed.
Print Assumptions entry_round_bounds.
Print Assumptions entry_request_product.
Print Assumptions entry_grown_bounds.
Print Assumptions entry_capacity_ge.
Print Assumptions entry_capacity_bytes.
Print Assumptions entry_array_step.
Print Assumptions entry_array_invariant.
Print Assumptions entry_allocation_target.
Print Assumptions entry_transfer_target.
