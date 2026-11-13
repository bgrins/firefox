Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativeProducerModel NativeReverseModel NativeProtection NativeReportUpdate.
Import ListNotations.
Module NativeReverseProtection.
Import NativeSchedule NativeProtection.NativeProtection.
Open Scope Z_scope.
Lemma loop_kept : forall rs grow finite largest left largestCount free total reports result,
  NativeReverse.loop grow finite largest left largestCount free total reports rs = Some result ->
  Forall2 KeepFrozen (map snd rs) (map snd (NativeReverse.indexedRows result)).
Proof.
  induction rs as [|[i r] tail IH]; intros grow finite largest left largestCount free total reportRows result H.
  - destruct left; inversion H; constructor.
  - destruct left as [|k]; [inversion H; apply kept_refl|].
    cbn [NativeReverse.loop] in H. destruct (frozen r) eqn:F.
    + destruct (NativeReverse.loop grow finite largest (S k) largestCount free total reportRows tail)
        as [rest|] eqn:R; [|discriminate].
      inversion H; subst result. cbn. constructor; [apply keep_refl|eapply IH; exact R].
    + destruct (NativeReverse.deltaFor grow finite largest largestCount free r)
        as [[d nextLargest]|] eqn:D; [|discriminate].
      destruct (NativeReverse.loop grow finite largest k nextLargest (free-d)
        (total+(project32 (main r+d)-(main r+d))) (updateReport i d reportRows) tail)
        as [rest|] eqn:R; [|discriminate].
      inversion H; subst result. cbn. constructor.
      * split; [split; [reflexivity|congruence]|reflexivity].
      * eapply IH; exact R.
Qed.
Lemma kept_app : forall xs ys as_ bs,
  Forall2 KeepFrozen xs ys -> Forall2 KeepFrozen as_ bs ->
  Forall2 KeepFrozen (xs++as_) (ys++bs).
Proof. intros xs ys as_ bs H K; induction H; cbn; [exact K|constructor; assumption]. Qed.
Lemma kept_rev : forall xs ys, Forall2 KeepFrozen xs ys -> Forall2 KeepFrozen (rev xs) (rev ys).
Proof.
  intros xs ys H; induction H; cbn; [constructor|].
  apply kept_app; [assumption|constructor; [assumption|constructor]].
Qed.
Lemma indexed_rows : forall (xs : list Row) start,
  map snd (combine (seq start (length xs)) xs) = xs.
Proof. intro xs; induction xs; intro start; cbn; [reflexivity|f_equal; apply IHxs]. Qed.
Lemma run_kept : forall grow produced count free reportRows result,
  NativeReverse.run grow produced count free reportRows = Some result ->
  Forall2 KeepFrozen (NativeProducer.producedRows produced) (NativeReverse.restored result).
Proof.
  intros grow produced count free reportRows result H.
  apply loop_kept in H. apply kept_rev in H.
  rewrite map_rev, rev_involutive, indexed_rows in H.
  unfold NativeReverse.restored. rewrite map_rev. exact H.
Qed.
Print Assumptions loop_kept.
Print Assumptions kept_app.
Print Assumptions kept_rev.
Print Assumptions indexed_rows.
Print Assumptions run_kept.
End NativeReverseProtection.
