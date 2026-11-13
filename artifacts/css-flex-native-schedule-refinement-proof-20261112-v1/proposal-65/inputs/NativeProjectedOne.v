Require Import ZArith Bool Lia.
Require Import NativeState NativeClampModel NativeClampFacts NativeProjectionAlgebra NativeProjectionFlags.
Module NativeProjectedOne.
Import NativeSchedule.
Open Scope Z_scope.
Lemma main_exact : forall r raw,
  0 <= minimum (seed r) <= maximum (seed r) -> maximum (seed r) <= 2147483647 ->
  main (fst (NativeClamp.one (NativeProjectionFlags.projected r raw))) = clamp (seed r) raw.
Proof.
  intros r raw Bounds Maximum.
  rewrite NativeClampFacts.one_main by (cbn [NativeProjectionFlags.projected]; lia).
  change (clamp (seed r) (project32 raw) = clamp (seed r) raw).
  apply NativeProjectionAlgebra.clamp_project32; assumption.
Qed.
Lemma correction_exact : forall r raw,
  0 <= minimum (seed r) <= maximum (seed r) -> maximum (seed r) <= 2147483647 ->
  (project32 raw-raw) + snd (NativeClamp.one (NativeProjectionFlags.projected r raw)) =
    clamp (seed r) raw-raw.
Proof.
  intros r raw Bounds Maximum.
  rewrite NativeClampFacts.one_difference, main_exact by assumption.
  change (project32 raw-raw + (clamp (seed r) raw-project32 raw) = clamp (seed r) raw-raw).
  lia.
Qed.
Lemma flags_exact : forall r raw,
  minFlag r = false -> maxFlag r = false ->
  0 <= minimum (seed r) <= maximum (seed r) -> maximum (seed r) <= 2147483647 ->
  minFlag (fst (NativeClamp.one (NativeProjectionFlags.projected r raw))) =
    Z.ltb raw (clamp (seed r) raw) /\
  maxFlag (fst (NativeClamp.one (NativeProjectionFlags.projected r raw))) =
    Z.ltb (clamp (seed r) raw) raw.
Proof.
  intros r raw Min Max Bounds Maximum.
  pose proof (NativeProjectionFlags.flags_exact r raw Min Max Bounds Maximum) as Flags.
  cbn zeta in Flags. rewrite main_exact in Flags by assumption. exact Flags.
Qed.
Print Assumptions main_exact.
Print Assumptions correction_exact.
Print Assumptions flags_exact.
End NativeProjectedOne.
