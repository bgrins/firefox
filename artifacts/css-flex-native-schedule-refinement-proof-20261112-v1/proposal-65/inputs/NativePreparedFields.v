Require Import Reals ZArith List Bool Lia.
Require Import InputTarget NativeState NativePassModel NativeProducerModel NativeEntryModel.
Require Import NativeResetProof NativeResetCorrespondence NativeProducerFields NativePassProtection.
Require Import NativeProducerSums NativeActiveInputs NativeSourceHistory NativeStructuralHistory NativeReverseEffects.
Import ListNotations.
Module NativePreparedFields.
Import NativeSchedule.
Open Scope Z_scope.
Definition Fields (before after : Row) :=
  seed after=seed before /\ frozen after=frozen before /\
  main after=NativeResetProof.currentSize before /\ minFlag after=minFlag before /\ maxFlag after=maxFlag before.
Lemma reset_fields : forall rs index free,
  Forall2 Fields rs (NativePass.resetRows (NativePass.reset index free rs)).
Proof.
  intros rs index free. rewrite NativeResetProof.reset_rows.
  induction rs as [|r tail IH]; cbn [map]; constructor; [|exact IH].
  unfold Fields,NativeResetProof.resetRow,NativeResetProof.currentSize.
  destruct (frozen r); repeat split; reflexivity.
Qed.
Lemma fields_share : forall a b c,
  Fields a b -> NativeProducerFields.ShareOnly b c -> Fields a c.
Proof.
  intros a b c F S. unfold NativeProducerFields.ShareOnly in S.
  rewrite S. unfold Fields in *; cbn; exact F.
Qed.
Lemma fields_trans : forall xs ys zs,
  Forall2 Fields xs ys -> Forall2 NativeProducerFields.ShareOnly ys zs -> Forall2 Fields xs zs.
Proof.
  intros xs ys zs H; revert zs. induction H; intros zs K; inversion K; subst; constructor.
  - eapply fields_share; eassumption.
  - apply IHForall2; assumption.
Qed.
Lemma prepare_fields : forall config state p,
  NativePass.prepare config state=Some p -> Forall2 Fields (rows state) (NativePass.preparedRows p).
Proof.
  intros config state p Prepared.
  destruct (NativePassProtection.prepare_output config state p Prepared) as [Rows Source].
  rewrite Rows. destruct (NativePass.producer p) as [prod|] eqn:P.
  - rewrite (Source prod eq_refl). eapply fields_trans.
    + apply reset_fields.
    + apply NativeProducerFields.loop_fields.
  - apply reset_fields.
Qed.
Lemma fields_fits : forall grow xs ys,
  Forall2 Fields xs ys -> NativeProducerSums.Valid grow xs -> Forall NativeReverseEffects.ActiveFits ys.
Proof.
  intros grow xs ys H; induction H as [|x y xs ys F Rest IH]; intros V.
  - constructor.
  - unfold NativeProducerSums.Valid in V. inversion V as [|head tail Head Tail]; subst.
    constructor.
    + destruct F as [Seed [Frozen [Main [Lo Hi]]]].
      unfold NativeReverseEffects.ActiveFits. intros Active. rewrite Frozen in Active.
      pose proof (proj1 (proj2 (Head Active))) as Range.
      rewrite Main. unfold NativeResetProof.currentSize. rewrite Active. exact Range.
    + apply IH. exact Tail.
Qed.
Lemma history_prepare_fits : forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state=Some p ->
  Forall NativeReverseEffects.ActiveFits (NativePass.preparedRows p).
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  eapply fields_fits; [eapply prepare_fields; exact Prepared|].
  exact (NativeActiveInputs.history_valid bytes line seeds info state Admission History).
Qed.
Print Assumptions reset_fields.
Print Assumptions fields_share.
Print Assumptions fields_trans.
Print Assumptions prepare_fields.
Print Assumptions fields_fits.
Print Assumptions history_prepare_fits.
End NativePreparedFields.
