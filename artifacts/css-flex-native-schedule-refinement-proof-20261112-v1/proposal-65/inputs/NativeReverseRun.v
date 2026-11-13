Require Import Reals ZArith List Bool Lia.
Require Import WeightTarget PrefixTarget ReverseTarget ReverseStructure SignModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeRefinementSpec.
Require Import NativeProducerSums NativeProducerRun NativeProducerRows NativeItemProjection NativeReverseFinite.
Require Import NativeEarlyProof NativeProtection NativePhaseProtection NativeStructuralHistory.
Import ListNotations.
Module NativeReverseRun.
Import NativeSchedule.
Lemma project_combine : forall grow (indices : list nat) rs,
  map (fun p => (fst p,NativeItemProjection.item grow (snd p))) (combine indices rs) =
    combine indices (map (NativeItemProjection.item grow) rs).
Proof.
  intros grow indices; induction indices as [|i tail IH]; intros [|r rs]; cbn; try reflexivity.
  rewrite IH. reflexivity.
Qed.
Lemma project_indexed_reverse : forall grow rs,
  NativeReverseFinite.items grow (rev (combine (seq O (length rs)) rs)) =
    rev (ReverseTarget.positioned (map (NativeItemProjection.item grow) rs)).
Proof.
  intros grow rs. unfold NativeReverseFinite.items,ReverseTarget.positioned.
  rewrite map_rev,project_combine,map_length. reflexivity.
Qed.
Lemma run_matches : forall grow rs count free reports,
  NativeProducerSums.Valid grow rs -> (Z.of_nat (length rs) <= countLimit)%Z ->
  count = length (filter frozen rs) -> ReverseTarget.FreeDomain free ->
  (PrefixTarget.total (PrefixTarget.run (map (NativeItemProjection.item grow) rs)) <> 0)%R ->
  exists out,
    NativeReverse.run grow (NativeProducer.run grow rs count) count free reports = Some out /\
    NativeReverse.left out = O /\
    Forall2 NativeRefinementTarget.EventMatches (NativeReverse.events out)
      (ReverseTarget.events (ReverseTarget.reverseRun (map (NativeItemProjection.item grow) rs) free)) /\
    NativeReverse.finalFree out = ReverseTarget.finalFree
      (ReverseTarget.reverseRun (map (NativeItemProjection.item grow) rs) free).
Proof.
  intros grow rs count free reports Valid Length Counted Domain Nonzero.
  pose proof (NativeProducerRun.run_correspondence grow rs count Valid Length Counted) as Producer.
  cbn zeta in Producer.
  set (produced := NativeProducer.run grow rs count) in *.
  destruct Producer as [_ [Finite [_ [Rows [_ [_ Shared]]]]]].
  assert (Kept : Forall2 NativeProtection.NativeProtection.KeepFrozen rs (NativeProducer.producedRows produced)).
  { unfold produced,NativeProducer.run. apply NativePhaseProtection.producer_kept. }
  pose proof (NativeStructuralHistory.kept_length _ _ Kept) as ProducedLength.
  assert (Active : (length (NativeProducer.producedRows produced)-count)%nat = active rs).
  { rewrite ProducedLength,Counted. apply NativeEarlyProof.active_complement. }
  assert (SharedReverse : Forall (fun pair => NativeProducerRows.Shared (snd pair))
    (rev (combine (seq O (length (NativeProducer.producedRows produced))) (NativeProducer.producedRows produced)))).
  { apply Forall_rev. apply Forall_forall. intros [i r] Member.
    apply in_combine_r in Member. rewrite Forall_forall in Shared. exact (Shared r Member). }
  destruct (NativeReverseFinite.loop_correspondence
    (rev (combine (seq O (length (NativeProducer.producedRows produced))) (NativeProducer.producedRows produced)))
    grow (active rs) (NativeProducer.largest produced) (NativeProducer.ties produced) free 0%Z reports
    SharedReverse Domain) as [out [Run [Events [Final Left]]]].
  rewrite project_indexed_reverse,Rows in Events,Final,Left.
  rewrite <- (NativeItemProjection.active_items grow rs) in Events,Final,Left,Run.
  exists out. split.
  - unfold NativeReverse.run. rewrite Finite,Active. rewrite <- (NativeItemProjection.active_items grow rs). exact Run.
  - unfold ReverseTarget.reverseRun.
    destruct (Req_EM_T (PrefixTarget.total (PrefixTarget.run (map (NativeItemProjection.item grow) rs))) 0%R)
      as [Zero|NotZero]; [contradiction|].
    assert (Empty : ReverseTarget.reverseRemaining (ReverseTarget.reverseLoop
      (PrefixTarget.activeCount (map (NativeItemProjection.item grow) rs)) free
      (rev (ReverseTarget.positioned (PrefixTarget.rows (PrefixTarget.run (map (NativeItemProjection.item grow) rs)))))) = O).
    { pose proof (proj1 (reverse_count_target (map (NativeItemProjection.item grow) rs) free)) as Count.
      unfold ReverseTarget.reverseRun in Count.
      destruct (Req_EM_T (PrefixTarget.total (PrefixTarget.run (map (NativeItemProjection.item grow) rs))) 0%R);
        [contradiction|exact Count]. }
    split; [rewrite Left; exact Empty|]. split; assumption.
Qed.
Print Assumptions project_combine.
Print Assumptions project_indexed_reverse.
Print Assumptions run_matches.
End NativeReverseRun.
