Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativeReverseModel.
Import ListNotations.
Module NativeReversePositions.
Import NativeSchedule.
Open Scope Z_scope.
Lemma loop_ordinals : forall rs grow finite largest left count free total reports out,
  NativeReverse.loop grow finite largest left count free total reports rs = Some out ->
  map fst (NativeReverse.indexedRows out) = map fst rs.
Proof.
  induction rs as [|[i r] tail IH]; intros grow finite largest left count free total reports out Run.
  - destruct left; inversion Run; reflexivity.
  - destruct left as [|k]; [inversion Run; reflexivity|].
    cbn [NativeReverse.loop] in Run. destruct (frozen r) eqn:Frozen.
    + destruct (NativeReverse.loop grow finite largest (S k) count free total reports tail)
        as [next|] eqn:Next; [|discriminate].
      inversion Run; subst out; cbn. f_equal. eapply IH; exact Next.
    + destruct (NativeReverse.deltaFor grow finite largest count free r) as [[delta remaining]|]
        eqn:Delta; [|discriminate].
      destruct (NativeReverse.loop grow finite largest k remaining (free-delta)
        (total+(project32 (main r+delta)-(main r+delta))) (updateReport i delta reports) tail)
        as [next|] eqn:Next; [|discriminate].
      inversion Run; subst out; cbn. f_equal. eapply IH; exact Next.
Qed.
Lemma loop_event_membership : forall rs grow finite largest left count free total reports out,
  NativeReverse.loop grow finite largest left count free total reports rs = Some out ->
  Forall (fun event => In (NativeReverse.ordinal event) (map fst rs)) (NativeReverse.events out).
Proof.
  induction rs as [|[i r] tail IH]; intros grow finite largest left count free total reports out Run.
  - destruct left; inversion Run; constructor.
  - destruct left as [|k]; [inversion Run; constructor|].
    cbn [NativeReverse.loop] in Run. destruct (frozen r) eqn:Frozen.
    + destruct (NativeReverse.loop grow finite largest (S k) count free total reports tail)
        as [next|] eqn:Next; [|discriminate].
      inversion Run; subst out; cbn. eapply Forall_impl; [|eapply IH; exact Next].
      intros event Member; right; exact Member.
    + destruct (NativeReverse.deltaFor grow finite largest count free r) as [[delta remaining]|]
        eqn:Delta; [|discriminate].
      destruct (NativeReverse.loop grow finite largest k remaining (free-delta)
        (total+(project32 (main r+delta)-(main r+delta))) (updateReport i delta reports) tail)
        as [next|] eqn:Next; [|discriminate].
      inversion Run; subst out; cbn. constructor; [left; reflexivity|].
      eapply Forall_impl; [|eapply IH; exact Next]. intros event Member; right; exact Member.
Qed.
Print Assumptions loop_ordinals.
Print Assumptions loop_event_membership.
End NativeReversePositions.
