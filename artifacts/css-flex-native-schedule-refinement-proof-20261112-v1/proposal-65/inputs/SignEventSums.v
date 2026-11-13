Require Import ZArith List Lia.
Require Import ReverseTarget SignModel SignSums.
Import ListNotations SignHistory.
Open Scope Z_scope.
Lemma sign_sum_zeros : forall (A : Type) (xs : list A),
  sumZ (map (fun _ => 0) xs) = 0.
Proof. exact sign_sum_constant_zero. Qed.
Lemma sign_indicator_absent : forall indices ordinal value,
  ~ In ordinal indices ->
  sumZ (map (fun i => if Nat.eqb ordinal i then value else 0) indices) = 0.
Proof.
  induction indices as [|i indices IH]; intros ordinal value Habsent; [reflexivity|].
  cbn [map sumZ fold_right].
  destruct (Nat.eqb ordinal i) eqn:Heq.
  - apply Nat.eqb_eq in Heq. subst i. exfalso. apply Habsent. left. reflexivity.
  - specialize (IH ordinal value ltac:(intro Hin; apply Habsent; right; exact Hin)).
    unfold sumZ in IH. lia.
Qed.
Lemma sign_indicator_once : forall indices ordinal value,
  NoDup indices -> In ordinal indices ->
  sumZ (map (fun i => if Nat.eqb ordinal i then value else 0) indices) = value.
Proof.
  induction indices as [|i indices IH]; intros ordinal value Hunique Hin; [contradiction|].
  inversion Hunique as [|? ? Habsent Htail]; subst.
  cbn [map sumZ fold_right]. destruct (Nat.eqb ordinal i) eqn:Heq.
  - apply Nat.eqb_eq in Heq. subst i.
    pose proof (sign_indicator_absent indices ordinal value Habsent). unfold sumZ in H. lia.
  - apply Nat.eqb_neq in Heq. destruct Hin as [Hequal|Hin]; [congruence|].
    specialize (IH ordinal value Htail Hin). unfold sumZ in IH. lia.
Qed.
Lemma sign_event_delta_sum : forall es indices,
  NoDup indices -> Forall (fun event => In (ordinal event) indices) es ->
  sumZ (map (fun i => sumZ (map (fun event => if Nat.eqb (ordinal event) i
    then delta event else 0) es)) indices) = eventSum es.
Proof.
  induction es as [|event es IH]; intros indices Hunique Hin.
  - cbn [map sumZ fold_right eventSum]. apply sign_sum_zeros.
  - apply Forall_cons_iff in Hin. destruct Hin as [Hevent Htail].
    change (sumZ (map (fun i => (if Nat.eqb (ordinal event) i then delta event else 0) +
      sumZ (map (fun e => if Nat.eqb (ordinal e) i then delta e else 0) es)) indices) =
      delta event + eventSum es).
    rewrite sign_sum_add, sign_indicator_once by assumption.
    rewrite IH by assumption. reflexivity.
Qed.
Lemma sign_delta_for_total : forall result n,
  Forall (fun event => (ordinal event < n)%nat) (events result) ->
  sumZ (map (fun i => deltaFor i result) (seq 0 n)) = eventSum (events result).
Proof.
  intros result n Hbounds. unfold deltaFor. apply sign_event_delta_sum.
  - apply seq_NoDup.
  - eapply Forall_impl; [|exact Hbounds]. intros event Hlt. apply in_seq. split; [apply Nat.le_0_l|exact Hlt].
Qed.
Lemma sign_indexed_first : forall xs,
  map fst (indexed xs) = seq 0 (length xs).
Proof.
  intro xs. unfold indexed.
  assert (Hgeneral : forall (ys : list Row) start,
    map fst (combine (seq start (length ys)) ys) = seq start (length ys)).
  { induction ys as [|y ys IH]; intro start; cbn [map length seq combine fst]; [reflexivity|].
    rewrite IH. reflexivity. }
  apply Hgeneral.
Qed.
Lemma sign_indexed_delta_total : forall result xs,
  Forall (fun event => (ordinal event < length xs)%nat) (events result) ->
  sumZ (map (fun pair => deltaFor (fst pair) result) (indexed xs)) = eventSum (events result).
Proof.
  intros result xs Hbound.
  replace (map (fun pair => deltaFor (fst pair) result) (indexed xs)) with
    (map (fun i => deltaFor i result) (map fst (indexed xs))) by (rewrite map_map; reflexivity).
  rewrite sign_indexed_first.
  apply sign_delta_for_total. exact Hbound.
Qed.
Print Assumptions sign_indicator_once.
Print Assumptions sign_event_delta_sum.
Print Assumptions sign_indexed_delta_total.
