Require Import EntryNumerals.
Require Import ZArith List Psatz.
Require Import EntryAllocation EntryModel EntryTarget ConversionTarget PrefixTarget EntrySums EntryAllocationProof.
Import EntryAcquisition InitialEntryTarget.
Open Scope Z_scope.
Lemma entry_prefix_length : forall (xs : list Z) n, (length (firstn n xs) <= length xs)%nat.
Proof. induction xs; intros [|n]; cbn; try lia. specialize (IHxs n). lia. Qed.
Lemma entry_line_count : forall e line, LineAdmitted e line ->
  (length (committedMBP line) <= 134217727)%nat.
Proof.
  intros e line [He [Hr [Hlen Hrest]]].
  pose proof (entry_allocation_target e (allocation line) He Hr) as [_ [_ [_ Hcount]]].
  rewrite Hlen. exact Hcount.
Qed.
Lemma entry_round_count : forall e line mode round,
  LineAdmitted e line -> RoundAdmitted line mode round ->
  (length (used round) <= 134217727)%nat /\ Forall Acquired32 (used round).
Proof.
  intros e line mode round Hl [Hids [Hpairs Hrest]].
  pose proof (entry_used_admitted _ _ Hpairs) as [Hused Hlen].
  pose proof (f_equal (@length nat) Hids) as Htokens. rewrite map_length in Htokens.
  pose proof (entry_line_count e line Hl) as Hcount.
  destruct Hl as [_ [_ [Hmbp _]]]. split; [lia|exact Hused].
Qed.
Lemma entry_bounded_sum : forall xs, (length xs <= 134217727)%nat -> Forall Acquired32 xs ->
  -288230374004228096 <= fold_right Z.add 0 xs <= 288230374004228096.
Proof.
  intros xs Hlen Hvalid. pose proof (entry_sum_range xs Hvalid) as Hrange. entry_numerals. lia.
Qed.
Theorem entry_acquisition_target : AcquisitionTarget.
Proof.
  intros e line mode round Hl Hr.
  pose proof (entry_line_count e line Hl) as Hcount.
  pose proof (entry_round_count e line mode round Hl Hr) as [Hucount Huvalid].
  destruct Hl as [_ [_ [_ [Hvalid [Hi Hg]]]]].
  pose proof (entry_bounded_sum _ Hcount Hvalid) as Hmbp.
  assert (Ht : mbpTotal line = fold_right Z.add 0 (committedMBP line)).
  { unfold mbpTotal. rewrite entry_fold_add. lia. }
  unfold Acquired32 in Hi, Hg.
  split.
  - intro k. rewrite entry_fold_add. apply Z.abs_le.
    pose proof (entry_prefix_length (committedMBP line) k) as Hlength.
    pose proof (entry_bounded_sum (firstn k (committedMBP line)) ltac:(lia)
      (entry_firstn_admitted _ _ Hvalid)) as Hrange. entry_numerals. lia.
  - split.
    + apply Z.abs_le. rewrite Ht. lia.
    + split.
      * apply Z.abs_le. unfold initialSpace. rewrite Ht. lia.
      * split.
        -- unfold Fits64. rewrite Ht. lia.
        -- split.
           ++ unfold Fits64. rewrite Ht. lia.
           ++ split.
              ** unfold Fits64, initialSpace. rewrite Ht. lia.
              ** split.
                 --- intro k. rewrite entry_fold_sub.
                     pose proof (entry_prefix_length (used round) k) as Hlength.
                     pose proof (entry_bounded_sum (firstn k (used round)) ltac:(lia)
                       (entry_firstn_admitted _ _ Huvalid)) as Hrange.
                     unfold initialSpace. rewrite Ht. split; unfold SmallDomain, Fits64; lia.
                 --- unfold roundFree, initialSpace. rewrite entry_fold_sub, Ht. reflexivity.
Qed.
Print Assumptions entry_prefix_length.
Print Assumptions entry_line_count.
Print Assumptions entry_round_count.
Print Assumptions entry_bounded_sum.
Print Assumptions entry_acquisition_target.
