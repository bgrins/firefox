Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeClampFacts.
Import ListNotations.
Module NativeExecutionSums.
Import NativeSchedule.
Open Scope Z_scope.
Definition rowSum (rs : list Row) := fold_right (fun r acc => main r+acc) 0 rs.
Definition pairSum (rs : list (nat*Row)) := fold_right (fun p acc => main (snd p)+acc) 0 rs.
Definition deltaSum (es : list NativeReverse.Event) :=
  fold_right (fun e acc => NativeReverse.delta e+acc) 0 es.
Lemma row_sum_map : forall rs,
  rowSum rs = fold_right Z.add 0 (map main rs).
Proof. induction rs; cbn [rowSum map fold_right]; [reflexivity|rewrite IHrs; reflexivity]. Qed.
Lemma pair_sum_append : forall a b, pairSum (a++b) = pairSum a+pairSum b.
Proof. induction a as [|[i r] tail IH]; intro b; cbn [app pairSum]; [lia|rewrite IH; lia]. Qed.
Lemma pair_sum_reverse : forall rs, pairSum (rev rs) = pairSum rs.
Proof.
  induction rs as [|[i r] tail IH]; [reflexivity|].
  cbn [rev]. rewrite pair_sum_append,IH. cbn [pairSum]; lia.
Qed.
Lemma pair_sum_snd : forall rs, rowSum (map snd rs) = pairSum rs.
Proof. induction rs as [|[i r] tail IH]; cbn [map rowSum pairSum]; [reflexivity|rewrite IH; reflexivity]. Qed.
Lemma pair_sum_combine : forall (indices : list nat) rs,
  length indices = length rs -> pairSum (combine indices rs) = rowSum rs.
Proof.
  induction indices as [|i tail IH]; intros [|r rs] Length; cbn in Length; try discriminate.
  - reflexivity.
  - cbn [combine pairSum rowSum]. rewrite IH by lia. reflexivity.
Qed.
Lemma restored_sum : forall out,
  rowSum (NativeReverse.restored out) = pairSum (NativeReverse.indexedRows out).
Proof. intro out. unfold NativeReverse.restored. rewrite pair_sum_snd,pair_sum_reverse. reflexivity. Qed.
Lemma reverse_balance : forall rs grow finite largest left count free acc reports out,
  NativeReverse.loop grow finite largest left count free acc reports rs = Some out ->
  NativeReverse.violation out = acc+pairSum (NativeReverse.indexedRows out)-pairSum rs-
    deltaSum (NativeReverse.events out).
Proof.
  induction rs as [|[i r] tail IH]; intros grow finite largest left count free acc reports out Run.
  - destruct left; inversion Run; cbn [pairSum deltaSum]; lia.
  - destruct left as [|k]; [inversion Run; cbn [pairSum deltaSum]; lia|].
    cbn [NativeReverse.loop] in Run. destruct (frozen r) eqn:Frozen.
    + destruct (NativeReverse.loop grow finite largest (S k) count free acc reports tail)
        as [next|] eqn:Next; [|discriminate].
      pose proof (IH grow finite largest (S k) count free acc reports next Next) as Balance.
      inversion Run; subst out. cbn [pairSum deltaSum]. lia.
    + destruct (NativeReverse.deltaFor grow finite largest count free r)
        as [[delta remaining]|] eqn:Delta; [|discriminate].
      destruct (NativeReverse.loop grow finite largest k remaining (free-delta)
        (acc+(project32 (main r+delta)-(main r+delta))) (updateReport i delta reports) tail)
        as [next|] eqn:Next; [|discriminate].
      pose proof (IH grow finite largest k remaining (free-delta)
        (acc+(project32 (main r+delta)-(main r+delta))) (updateReport i delta reports) next Next) as Balance.
      inversion Run; subst out. cbn [pairSum deltaSum]. lia.
Qed.
Lemma reverse_run_balance : forall grow produced count free reports out,
  NativeReverse.run grow produced count free reports = Some out ->
  NativeReverse.violation out = rowSum (NativeReverse.restored out)-
    rowSum (NativeProducer.producedRows produced)-deltaSum (NativeReverse.events out).
Proof.
  intros grow produced count free reports out Run.
  pose proof (reverse_balance _ _ _ _ _ _ _ _ _ _ Run) as Balance.
  rewrite pair_sum_reverse,pair_sum_combine in Balance by apply seq_length.
  rewrite restored_sum. lia.
Qed.
Lemma clamp_balance : forall rs left index acc,
  NativeClamp.total (NativeClamp.loop left index acc rs) =
    acc+rowSum (NativeClamp.clampedRows (NativeClamp.loop left index acc rs))-rowSum rs.
Proof.
  induction rs as [|r tail IH]; intros left index acc.
  - destruct left; cbn [NativeClamp.loop rowSum]; lia.
  - destruct left as [|k]; [cbn [NativeClamp.loop rowSum]; lia|].
    cbn [NativeClamp.loop]. destruct (frozen r) eqn:Frozen.
    + cbn [rowSum]. rewrite IH. lia.
    + cbn [rowSum]. rewrite IH,NativeClampFacts.one_difference. lia.
Qed.
Lemma finish_no_reverse_balance : forall config state prepared,
  NativeClamp.total (NativePass.clamped (NativePass.finish config state prepared None)) =
    rowSum (NativeClamp.clampedRows (NativePass.clamped (NativePass.finish config state prepared None)))-
    rowSum (NativePass.preparedRows prepared).
Proof. intros. cbn [NativePass.finish]. rewrite clamp_balance. lia. Qed.
Lemma finish_reverse_balance : forall config state prepared produced reversed,
  NativeReverse.run (NativePass.growing config) produced (frozenCount state)
    (NativePass.entryFree prepared) (reports state) = Some reversed ->
  NativeClamp.total (NativePass.clamped (NativePass.finish config state prepared (Some reversed))) =
    rowSum (NativeClamp.clampedRows (NativePass.clamped (NativePass.finish config state prepared (Some reversed))))-
    rowSum (NativeProducer.producedRows produced)-deltaSum (NativeReverse.events reversed).
Proof.
  intros config state prepared produced reversed Run.
  pose proof (reverse_run_balance _ _ _ _ _ _ Run) as Balance.
  cbn [NativePass.finish]. rewrite clamp_balance. lia.
Qed.
Print Assumptions row_sum_map.
Print Assumptions pair_sum_append.
Print Assumptions pair_sum_reverse.
Print Assumptions pair_sum_snd.
Print Assumptions pair_sum_combine.
Print Assumptions restored_sum.
Print Assumptions reverse_balance.
Print Assumptions reverse_run_balance.
Print Assumptions clamp_balance.
Print Assumptions finish_no_reverse_balance.
Print Assumptions finish_reverse_balance.
End NativeExecutionSums.
