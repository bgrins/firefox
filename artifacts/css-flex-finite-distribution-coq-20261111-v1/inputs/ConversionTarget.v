Require Import Reals ZArith Gappa.Gappa_library Target.
Open Scope R_scope.

Definition integerDelta (free : Z) (choice : Choice) : Z :=
  match choice with
  | Zero => 0
  | Whole => free
  | Fraction share =>
      Raux.Zfloor (rn (rn (rn (IZR free) * share) + half))
  | Equal count =>
      Raux.Zfloor (rn (rn (rn (IZR free) / count) + half))
  end.

Definition Fits64 (value : Z) : Prop :=
  (-9223372036854775808 <= value <= 9223372036854775807)%Z.
Definition EnvelopeZ (free delta : Z) : Prop :=
  (Z.min free 0 - 1048576 <= delta <= Z.max free 0 + 1048576)%Z.

Definition FloorTarget : Prop := forall x,
  IZR (Raux.Zfloor (rn (x + half))) = integerRound x.
Definition CorrespondenceTarget : Prop := forall free choice,
  IZR (integerDelta free choice) = computeDelta (IZR free) choice.
Definition SafetyTarget : Prop := forall free choice,
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  ValidChoice choice ->
  EnvelopeZ free (integerDelta free choice) /\ Fits64 (integerDelta free choice).
Definition FactorIntegerTarget : Prop := forall free share,
  (-576460752303423488 <= free <= 576460752303423488)%Z ->
  0 <= share <= 1 ->
  (-576460752303423488 <= integerDelta free (Fraction share) <= 576460752303423488)%Z.
Definition OvershootTarget : Prop :=
  integerDelta 576460752303423487 (Equal 1) = 576460752303423488%Z.
Definition InhabitedTarget : Prop :=
  ValidChoice Zero /\ ValidChoice Whole /\
  ValidChoice (Fraction (1/2)) /\ ValidChoice (Equal 1).
Definition FullConversionTarget : Prop :=
  FloorTarget /\ CorrespondenceTarget /\ SafetyTarget /\
  FactorIntegerTarget /\ OvershootTarget /\ InhabitedTarget.
