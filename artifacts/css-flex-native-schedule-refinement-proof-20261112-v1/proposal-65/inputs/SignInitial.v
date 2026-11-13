Require Import Reals ZArith List Bool Lia.
Require Import EntryModel EntrySums SignModel SignBasics SignTarget.
Import ListNotations SignHistory.
Open Scope Z_scope.
Lemma sign_initial_balance : forall line seeds,
  balance line (initial line seeds) = fixed line + sumZ (map hypothetical seeds).
Proof.
  intros line seeds. unfold balance, initial. cbn [rows]. rewrite !map_map.
  f_equal. apply f_equal. apply map_ext. intro s.
  rewrite sign_early_main, sign_early_seed. cbn [build main seed].
  destruct (isFrozen (early (mode line seeds) (build s))); reflexivity.
Qed.
Lemma sign_initial_active : forall line seeds,
  Forall (ActiveBase (mode line seeds)) (rows (initial line seeds)).
Proof.
  intros line seeds. unfold initial. cbn [rows]. rewrite map_map.
  apply Forall_forall. intros row Hin. apply in_map_iff in Hin.
  destruct Hin as [s [Heq Hin]]. subst row.
  intro Hactive. exact ((proj2 (sign_early_active (mode line seeds) (build s) Hactive)) Hactive).
Qed.
Lemma sign_initial_balanced : forall line seeds,
  Balanced line (mode line seeds) (initial line seeds).
Proof.
  intros line seeds. unfold Balanced. rewrite sign_initial_balance.
  unfold mode. destruct (Z.ltb (fixed line + sumZ (map hypothetical seeds))
    (EntryAcquisition.inner line)) eqn:H.
  - apply Z.ltb_lt in H. lia.
  - apply Z.ltb_ge in H. exact H.
Qed.
Lemma sign_free_equation : forall line grow state,
  free line grow state = EntryAcquisition.inner line - fixed line - sumZ (map currentSize (rows state)).
Proof.
  intros. unfold free, EntryAcquisition.roundFree, asRound. cbn [EntryAcquisition.used].
  rewrite entry_fold_sub. reflexivity.
Qed.
Lemma sign_active_sum : forall grow xs,
  Forall (ActiveBase grow) xs ->
  if grow then sumZ (map currentSize xs) <=
    sumZ (map (fun row => if isFrozen row then main row else hypothetical (seed row)) xs)
  else sumZ (map (fun row => if isFrozen row then main row else hypothetical (seed row)) xs) <=
    sumZ (map currentSize xs).
Proof.
  intros grow xs H. induction H.
  - destruct grow; cbn [map sumZ fold_right]; lia.
  - unfold sumZ, currentSize in IHForall. cbn [map sumZ fold_right]. unfold currentSize.
    destruct grow; cbn in *; destruct (isFrozen x) eqn:Hf; try lia;
      specialize (H Hf); cbn in H; lia.
Qed.
Lemma sign_balance_direction : forall line grow state,
  Forall (ActiveBase grow) (rows state) -> Balanced line grow state ->
  Direction grow (free line grow state).
Proof.
  intros line grow state Hactive Hbalance.
  pose proof (sign_active_sum grow (rows state) Hactive) as Hsum.
  unfold Balanced, Direction, balance in *. rewrite sign_free_equation.
  destruct grow; lia.
Qed.
Theorem sign_initial_target : NativeHistorySignTarget.InitialTarget.
Proof.
  intros e line seeds Hvalid. split; [apply sign_initial_seeds|].
  split; [apply sign_initial_active|]. split; [apply sign_initial_balanced|].
  apply sign_balance_direction; [apply sign_initial_active|apply sign_initial_balanced].
Qed.
Print Assumptions sign_initial_balance.
Print Assumptions sign_initial_active.
Print Assumptions sign_initial_balanced.
Print Assumptions sign_free_equation.
Print Assumptions sign_active_sum.
Print Assumptions sign_balance_direction.
Print Assumptions sign_initial_target.
