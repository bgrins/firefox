Require Import ZArith List Lia.
Require Import EntryModel EntryTarget EntryAcquisitionProof.
Import ListNotations EntryAcquisition InitialEntryTarget.
Open Scope Z_scope.
Lemma entry_round_small : forall e line mode round,
  LineAdmitted e line -> RoundAdmitted line mode round -> SmallDomain (roundFree line round).
Proof.
  intros e line mode round Hl Hr.
  pose proof (entry_acquisition_target e line mode round Hl Hr) as [_ [_ [_ [_ [_ [_ [Hp _]]]]]]].
  specialize (Hp (length (used round))). rewrite firstn_all in Hp. exact (proj1 Hp).
Qed.
Lemma entry_first_append : forall xs value,
  firstNonzero (xs++[value]) = capture (firstNonzero xs) value.
Proof.
  induction xs as [|head xs IH]; intro value.
  - cbn [app firstNonzero capture]. destruct (Z.eq_dec value 0); subst; reflexivity.
  - cbn [app firstNonzero]. destruct (Z.eq_dec head 0) as [Hz|Hnz].
    + exact (IH value).
    + unfold capture. destruct (Z.eq_dec head 0); [contradiction|reflexivity].
Qed.
Lemma entry_first_witness : forall line rounds,
  firstNonzero (map (roundFree line) rounds) <> 0 ->
  exists before round after, rounds=before++round::after /\
    Forall (fun r => roundFree line r=0) before /\
    roundFree line round=firstNonzero (map (roundFree line) rounds).
Proof.
  intros line rounds. induction rounds as [|round rounds IH]; intro H.
  - cbn [map firstNonzero] in H. contradiction.
  - cbn [map firstNonzero] in *.
    destruct (Z.eq_dec (roundFree line round) 0) as [Hz|Hnz].
    + destruct (IH H) as [before [chosen [after [Heq [Hbefore Hchosen]]]]].
      exists (round::before), chosen, after. split; [cbn; rewrite Heq; reflexivity|].
      split; [constructor; assumption|exact Hchosen].
    + exists [], round, rounds. repeat split; constructor.
Qed.
Lemma entry_history_capture : forall e line mode rounds original,
  LineAdmitted e line -> History line mode rounds original ->
  SmallDomain original /\ original=firstNonzero (map (roundFree line) rounds).
Proof.
  intros e line mode rounds original Hl H. induction H.
  - split; [unfold SmallDomain; lia|reflexivity].
  - destruct IHHistory as [Hsmall Heq]. split.
    + unfold capture. destruct (Z.eq_dec original 0).
      * eapply entry_round_small; eassumption.
      * exact Hsmall.
    + rewrite map_app. cbn [map]. rewrite entry_first_append, <-Heq. reflexivity.
Qed.
Theorem entry_capture_target : CaptureTarget.
Proof.
  intros e line mode rounds original Hl Hhistory.
  pose proof (entry_history_capture e line mode rounds original Hl Hhistory) as [Hsmall Heq].
  split; [exact Hsmall|]. split; [exact Heq|].
  intro Hnz. destruct (entry_first_witness line rounds ltac:(rewrite <-Heq; exact Hnz))
    as [before [round [after [Hsplit [Hbefore Hround]]]]].
  exists before, round, after. split; [exact Hsplit|]. split; [exact Hbefore|]. rewrite Heq. exact Hround.
Qed.
Print Assumptions entry_round_small.
Print Assumptions entry_first_append.
Print Assumptions entry_first_witness.
Print Assumptions entry_history_capture.
Print Assumptions entry_capture_target.
