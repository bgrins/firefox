Require Import Reals ZArith List Psatz.
Require Import Target ConversionTarget PrefixTarget ReverseTarget ReverseSafety ReverseStructure.
Require Import EntryModel EntryTarget EntryAdjustment EntryFactors EntryCapture.
Import EntryAcquisition InitialEntryTarget.
Open Scope Z_scope.
Lemma entry_small_domain : forall value, SmallDomain value -> FreeDomain value.
Proof. unfold SmallDomain, FreeDomain. intros; lia. Qed.
Lemma entry_capture_small : forall original current,
  SmallDomain original -> SmallDomain current -> SmallDomain (capture original current).
Proof. intros original current Ho Hc. unfold capture. destruct (Z.eq_dec original 0); assumption. Qed.
Lemma entry_prepare_small : forall e line mode rounds original round,
  LineAdmitted e line -> History line mode rounds original -> RoundAdmitted line mode round ->
  SmallDomain (originalAfter (prepare line original round)) /\
  SmallDomain (entryFree (prepare line original round)).
Proof.
  intros e line mode rounds original round Hl Hh Hr.
  pose proof (entry_history_capture e line mode rounds original Hl Hh) as [Ho Hfirst].
  pose proof (entry_round_small e line mode round Hl Hr) as Hc.
  pose proof (entry_factor_target e line mode round Hl Hr) as [_ [_ [_ [Hf Hrest]]]].
  pose proof (entry_capture_small original (roundFree line round) Ho Hc) as Hsaved.
  unfold prepare. destruct (Z.eq_dec (roundFree line round) 0).
  - split; assumption.
  - destruct (Req_EM_T (total (run (items round))) 0).
    + split; assumption.
    + destruct (Rlt_dec (factorTotal (factorRun (items round))) 1).
      * split; [exact Hsaved|].
        exact (proj1 (proj2 (entry_adjustment_target (roundFree line round)
          (capture original (roundFree line round)) (factorTotal (factorRun (items round))) Hc Hsaved ltac:(lra)))).
      * split; assumption.
Qed.
Theorem entry_entry_target : EntryTarget.
Proof.
  intros e line mode rounds original round Hl Hh Hr.
  pose proof (entry_prepare_small e line mode rounds original round Hl Hh Hr) as [Ho Hc].
  pose proof (entry_factor_target e line mode round Hl Hr) as [_ [_ [_ [_ [_ Ha]]]]].
  exact (conj Ho (conj Hc (conj (entry_small_domain _ Hc) (conj (entry_small_fits _ Hc) Ha)))).
Qed.
Lemma entry_enters_nonzero : forall line original round,
  enters (prepare line original round)=true -> (total (run (items round))<>0)%R.
Proof.
  intros line original round. unfold prepare.
  destruct (Z.eq_dec (roundFree line round) 0); cbn [enters selectedBranch]; [discriminate|].
  destruct (Req_EM_T (total (run (items round))) 0) as [Hz|Hnz]; cbn [enters selectedBranch]; [discriminate|].
  intros _. exact Hnz.
Qed.
Theorem entry_composition_target : CompositionTarget.
Proof.
  intros e line mode rounds original round Hl Hh Hr.
  pose proof (entry_entry_target e line mode rounds original round Hl Hh Hr) as [_ [_ [Hd [Hfits Ha]]]].
  cbn zeta. unfold execute.
  destruct (enters (prepare line original round)) eqn:Hgo.
  - pose proof (entry_enters_nonzero line original round Hgo) as Hnonzero.
    pose proof (reverse_safety_target (items round) (entryFree (prepare line original round)) Ha Hd)
      as [Hevents [Hdomain Hresult]].
    pose proof (reverse_count_target (items round) (entryFree (prepare line original round))) as [Hleft [_ Hlen]].
    pose proof (reverse_order_target (items round) (entryFree (prepare line original round))) as Horder.
    destruct (Req_EM_T (total (run (items round))) 0); [contradiction|].
    exact (conj Hevents (conj Hdomain (conj Hresult
      (conj (trace_target _ _) (conj (conservation_target _ _) (conj Hleft (conj Horder Hlen))))))).
  - cbn [events finalFree reverseRemaining Chained eventSum map length].
    split; [constructor|]. split; [exact Hd|]. split; [exact Hfits|]. repeat split; try reflexivity. unfold eventSum. cbn. lia.
Qed.
Print Assumptions entry_small_domain.
Print Assumptions entry_capture_small.
Print Assumptions entry_prepare_small.
Print Assumptions entry_entry_target.
Print Assumptions entry_enters_nonzero.
Print Assumptions entry_composition_target.
