Require Import Reals ZArith List Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Target ConversionTarget.
Open Scope R_scope.

Definition storedShare (weights : list R) (weight : R) : R :=
  if Req_EM_T weight 0 then 0 else ShareTarget.share weight (WeightTarget.accumulate weights 0).
Definition finiteChoice (weights : list R) (weight : R) : Choice :=
  let portion := storedShare weights weight in
  if Req_EM_T portion 1 then Whole
  else if Rlt_dec 0 portion then Fraction portion else Zero.
Definition finiteDelta (free : Z) (weights : list R) (weight : R) : Z :=
  integerDelta free (finiteChoice weights weight).
Definition FiniteInputs (weights : list R) (weight : R) : Prop :=
  (Z.of_nat (length weights) <= countLimit)%Z /\
  Forall FiniteWeight weights /\ In weight weights.
Definition RoundingBridgeTarget : Prop := forall x, WeightTarget.rn x = Target.rn x.
Definition StoredTarget : Prop := forall weights weight,
  FiniteInputs weights weight -> 0 <= storedShare weights weight <= 1.
Definition ChoiceTarget : Prop := forall weights weight,
  FiniteInputs weights weight -> ValidChoice (finiteChoice weights weight).
Definition DeltaTarget : Prop := forall free weights weight,
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  FiniteInputs weights weight ->
  EnvelopeZ free (finiteDelta free weights weight) /\
  Fits64 (finiteDelta free weights weight).
Definition WholeTarget : Prop := forall free,
  FiniteInputs (1 :: nil) 1 /\ finiteDelta free (1 :: nil) 1 = free.
Definition ZeroDeltaTarget : Prop := forall free weights, finiteDelta free weights 0 = 0%Z.
Definition FullFiniteDistributionTarget : Prop :=
  RoundingBridgeTarget /\ StoredTarget /\ ChoiceTarget /\ DeltaTarget /\
  WholeTarget /\ ZeroDeltaTarget.
