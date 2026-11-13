Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativeClampModel NativeEarlyProof.
Import ListNotations.
Module NativeSelectionStructure.
Import NativeSchedule.
Definition FreshRows (rs : list Row) :=
  Forall (fun r => frozen r = false -> minFlag r = false /\ maxFlag r = false) rs.
Lemma frozen_fresh : forall rs, active rs = O -> FreshRows rs.
Proof.
  intros rs H. apply NativeEarlyProof.active_zero in H.
  induction H; constructor; [intro F; congruence|assumption].
Qed.
Lemma select_zero : forall rs final violation index count,
  NativeClamp.selectedRows (NativeClamp.select final violation O index count rs) = rs /\
  NativeClamp.frozenAfter (NativeClamp.select final violation O index count rs) = count.
Proof. intros [|r tail]; intros; split; reflexivity. Qed.
Lemma selection_fresh : forall rs final violation index count,
  FreshRows (NativeClamp.selectedRows
    (NativeClamp.select final violation (active rs) index count rs)).
Proof.
  induction rs as [|r tail IH]; intros final violation index count; [constructor|].
  destruct (frozen r) eqn:F.
  - assert (A : active (r::tail) = active tail) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. destruct (active tail) as [|k] eqn:K.
    + rewrite (proj1 (select_zero (r::tail) final violation index count)). apply frozen_fresh.
      exact A.
    + cbn [NativeClamp.select]; rewrite F; cbn.
      constructor; [intro G; congruence|]. specialize (IH final violation (S index) count).
      exact IH.
  - assert (A : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [NativeClamp.select]; rewrite F; cbn.
    constructor.
    + destruct (selectedFlags violation r), final; cbn; intro G; try discriminate; split; reflexivity.
    + apply IH.
Qed.
Lemma selection_balance : forall rs final violation index count,
  (NativeClamp.frozenAfter (NativeClamp.select final violation (active rs) index count rs) +
    active (NativeClamp.selectedRows (NativeClamp.select final violation (active rs) index count rs)) =
    count + active rs)%nat.
Proof.
  induction rs as [|r tail IH]; intros final violation index count; [cbn; lia|].
  destruct (frozen r) eqn:F.
  - assert (A : active (r::tail) = active tail) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. destruct (active tail) as [|k] eqn:K.
    + destruct (select_zero (r::tail) final violation index count) as [Rows Count].
      rewrite Rows, Count, A; lia.
    + cbn [NativeClamp.select]; rewrite F; cbn.
      rewrite ?F; cbn.
      specialize (IH final violation (S index) count); exact IH.
  - assert (A : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [NativeClamp.select]; rewrite F; cbn.
    specialize (IH final violation (S index)
      (if selectedFlags violation r || final then S count else count)).
    destruct (selectedFlags violation r), final; cbn in *;
      unfold active in *; cbn in *; rewrite ?F in *; cbn in *; lia.
Qed.
Print Assumptions frozen_fresh.
Print Assumptions select_zero.
Print Assumptions selection_fresh.
Print Assumptions selection_balance.
End NativeSelectionStructure.
