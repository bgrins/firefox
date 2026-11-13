Require Import ZArith List Bool Lia.
Require Import NativeState NativeReverseModel NativeClampModel NativePassModel NativeProtection NativePhaseProtection.
Require Import NativeEarlyProof NativeStructuralHistory.
Import ListNotations.
Module NativeClampMap.
Import NativeSchedule.
Definition each (r : Row) := if frozen r then r else fst (NativeClamp.one r).
Lemma active_cons : forall r rs,
  active (r::rs) = if frozen r then active rs else S (active rs).
Proof. intros; unfold active; cbn; destruct (frozen r); reflexivity. Qed.
Lemma full_rows : forall rs index acc,
  NativeClamp.clampedRows (NativeClamp.loop (active rs) index acc rs) = map each rs.
Proof.
  induction rs as [|r tail IH]; intros index acc; [reflexivity|].
  rewrite active_cons. destruct (frozen r) eqn:F.
  - change (NativeClamp.clampedRows (NativeClamp.loop (active tail) index acc (r::tail)) =
      each r::map each tail).
    unfold each at 1; rewrite F. destruct (active tail) eqn:A.
    + cbn [NativeClamp.loop]. f_equal. rewrite <- (IH (S index) acc),A; reflexivity.
    + cbn [NativeClamp.loop]. rewrite F; cbn. rewrite <- A,IH; reflexivity.
  - cbn [NativeClamp.loop]. rewrite F; cbn. rewrite IH.
    unfold each at 1; rewrite F; reflexivity.
Qed.
Lemma finish_rows : forall config state prepared reversed,
  NativeStructuralHistory.Counted state ->
  Forall2 NativeProtection.NativeProtection.KeepFrozen (rows state)
    (match reversed with None => NativePass.preparedRows prepared | Some r => NativeReverse.restored r end) ->
  NativeClamp.clampedRows (NativePass.clamped (NativePass.finish config state prepared reversed)) =
    map each (match reversed with None => NativePass.preparedRows prepared | Some r => NativeReverse.restored r end).
Proof.
  intros config state prepared reversed Counted Kept.
  pose proof (NativeStructuralHistory.kept_length _ _ Kept) as Length.
  pose proof (NativeStructuralHistory.kept_active _ _ Kept) as Active.
  unfold NativeStructuralHistory.Counted in Counted.
  cbn [NativePass.finish]. rewrite Length,Counted,NativeEarlyProof.active_complement,<-Active.
  apply full_rows.
Qed.
Print Assumptions active_cons.
Print Assumptions full_rows.
Print Assumptions finish_rows.
End NativeClampMap.
