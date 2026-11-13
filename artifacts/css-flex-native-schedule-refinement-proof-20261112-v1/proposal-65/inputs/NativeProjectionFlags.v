Require Import ZArith Bool Lia.
Require Import NativeState NativeClampModel NativeProjectionAlgebra NativeClampFacts.
Module NativeProjectionFlags.
Import NativeSchedule.
Open Scope Z_scope.
Definition projected (r : Row) (raw : Z) :=
  setFlags (replaceMain r (project32 raw))
    (minFlag r || Z.ltb raw (-2147483648)) (maxFlag r || Z.ltb 2147483647 raw).
Lemma flags_exact : forall r raw,
  minFlag r = false -> maxFlag r = false ->
  0 <= minimum (seed r) <= maximum (seed r) -> maximum (seed r) <= 2147483647 ->
  let result := fst (NativeClamp.one (projected r raw)) in
  minFlag result = Z.ltb raw (main result) /\ maxFlag result = Z.ltb (main result) raw.
Proof.
  intros r raw Lo Hi Bounds Maximum. unfold projected, NativeClamp.one; cbn.
  rewrite Lo, Hi; cbn.
  unfold project32.
  destruct (Z.min_spec raw 2147483647) as [[A M]|[A M]]; rewrite M;
    destruct (Z.max_spec (-2147483648) (Z.min raw 2147483647)) as [[B X]|[B X]];
    rewrite M in X, B; rewrite X.
  all: repeat (cbn; match goal with
    | |- context [Z.ltb ?x ?y] => let E := fresh "Test" in destruct (Z.ltb x y) eqn:E;
      [apply Z.ltb_lt in E|apply Z.ltb_ge in E]
    end); cbn; split; reflexivity || lia.
Qed.
Print Assumptions flags_exact.
End NativeProjectionFlags.
