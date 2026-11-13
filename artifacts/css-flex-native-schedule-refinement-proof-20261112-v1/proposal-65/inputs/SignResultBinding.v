Require Import Reals ZArith List Lia.
Require Import PrefixTarget ReverseTarget ReverseBinding EntryModel.
Require Import SignModel SignBasics SignInitial SignSums SignEventSums.
Import ListNotations SignHistory.
Open Scope Z_scope.
Lemma sign_distributed_binding : forall line grow state,
  Forall (EventBoundTo (itemRows grow state)) (events (distributed line grow state)).
Proof.
  intros. unfold distributed, EntryAcquisition.execute.
  destruct (EntryAcquisition.enters (EntryAcquisition.prepare line (saved state) (asRound grow state))).
  - apply event_binding_target.
  - constructor.
Qed.
Lemma sign_distributed_ordinals : forall line grow state,
  Forall (fun event => (ordinal event < length (rows state))%nat)
    (events (distributed line grow state)).
Proof.
  intros line grow state. eapply Forall_impl; [|apply sign_distributed_binding].
  intros event [before [x [after [y [Hxs [Hindex Hrest]]]]]].
  pose proof (f_equal (@length _) Hxs) as Hlength.
  unfold itemRows in Hlength. rewrite map_length, app_length in Hlength. cbn [length] in Hlength.
  rewrite Hindex. lia.
Qed.
Lemma sign_frozen_delta_zero : forall line grow state i row,
  nth_error (rows state) i = Some row -> isFrozen row = true ->
  deltaFor i (distributed line grow state) = 0.
Proof.
  intros line grow state i row Hnth Hf.
  assert (Hitem : nth_error (itemRows grow state) i = Some (asItem grow row)).
  { unfold itemRows. rewrite nth_error_map, Hnth. reflexivity. }
  assert (Hz : forall event, In event (events (distributed line grow state)) ->
    (if Nat.eqb (ordinal event) i then delta event else 0) = 0).
  { intros event Hin. destruct (Nat.eqb (ordinal event) i) eqn:Heq; [|reflexivity].
    apply Nat.eqb_eq in Heq.
    pose proof (sign_distributed_binding line grow state) as Hbindings.
    rewrite Forall_forall in Hbindings. specialize (Hbindings event Hin).
    destruct Hbindings as [before [x [after [y [Hxs [Hindex [Hxf Hrest]]]]]]].
    assert (Hx : nth_error (itemRows grow state) i = Some x).
    { rewrite <- Heq, Hindex, Hxs, nth_error_app2 by lia. rewrite Nat.sub_diag. reflexivity. }
    rewrite Hitem in Hx. inversion Hx; subst x. change (isFrozen row = false) in Hxf. congruence. }
  unfold deltaFor. transitivity (sumZ (map (fun _ : Event => 0) (events (distributed line grow state)))).
  - f_equal. apply map_ext_in. exact Hz.
  - apply sign_sum_constant_zero.
Qed.
Lemma sign_indexed_member : forall xs i row,
  In (i,row) (indexed xs) -> nth_error xs i = Some row.
Proof.
  intros xs i row Hin.
  assert (Hgeneral : forall (ys : list Row) start j value,
    In (j,value) (combine (seq start (length ys)) ys) ->
    exists before after, ys = before ++ value :: after /\ j = (start+length before)%nat).
  { induction ys as [|head ys IH]; intros start j value H; cbn [length seq combine] in H; [contradiction|].
    destruct H as [Heq|Htail].
    - inversion Heq; subst. exists [],ys. split; [reflexivity|cbn; lia].
    - destruct (IH (S start) j value Htail) as [before [after [Heq Hindex]]].
      exists (head::before),after. split; [cbn; rewrite Heq; reflexivity|cbn; lia]. }
  destruct (Hgeneral xs 0%nat i row Hin) as [before [after [Heq Hindex]]].
  cbn in Hindex. rewrite Hindex, Heq, nth_error_app2 by lia. rewrite Nat.sub_diag. reflexivity.
Qed.
Lemma sign_raw_sum : forall line grow state,
  sumZ (map (fun pair => rawAt (distributed line grow state) (fst pair) (snd pair)) (indexed (rows state))) =
  sumZ (map currentSize (rows state)) + eventSum (events (distributed line grow state)).
Proof.
  intros line grow state.
  assert (Heq : forall pair, In pair (indexed (rows state)) ->
    rawAt (distributed line grow state) (fst pair) (snd pair) =
      currentSize (snd pair) + deltaFor (fst pair) (distributed line grow state)).
  { intros [i row] Hin. cbn [fst snd]. unfold rawAt, currentSize.
    destruct (isFrozen row) eqn:Hf; [|reflexivity].
    rewrite (sign_frozen_delta_zero line grow state i row (sign_indexed_member _ _ _ Hin) Hf).
    lia. }
  transitivity (sumZ (map (fun pair => currentSize (snd pair) +
    deltaFor (fst pair) (distributed line grow state)) (indexed (rows state)))).
  - f_equal. apply map_ext_in. exact Heq.
  - rewrite sign_sum_add, sign_indexed_delta_total by apply sign_distributed_ordinals.
    f_equal.
    replace (map (fun pair : nat * Row => currentSize (snd pair)) (indexed (rows state))) with
      (map currentSize (map snd (indexed (rows state)))) by (rewrite map_map; reflexivity).
    rewrite sign_indexed_snd. reflexivity.
Qed.
Lemma sign_violation_difference : forall result state,
  violation result state =
    sumZ (map (fun pair => boundedAt result (fst pair) (snd pair)) (indexed (rows state))) -
    sumZ (map (fun pair => rawAt result (fst pair) (snd pair)) (indexed (rows state))).
Proof.
  intros result state. rewrite <- sign_sum_sub. unfold violation.
  f_equal. apply map_ext. intros [i row]. cbn [fst snd].
  destruct (isFrozen row) eqn:Hf; [|reflexivity].
  unfold boundedAt, rawAt. rewrite Hf. lia.
Qed.
Print Assumptions sign_distributed_binding.
Print Assumptions sign_frozen_delta_zero.
Print Assumptions sign_raw_sum.
Print Assumptions sign_violation_difference.
