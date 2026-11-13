Require Import Reals ZArith List Gappa.Gappa_library.
Require Import WeightTarget.
Open Scope R_scope.
Definition Representable (x : R) := rn x = x.
Definition FiniteWeight (x : R) := WeightValid x /\ Representable x.
Definition share (weight denominator : R) := rn (weight / denominator).
Definition MonotoneTarget : Prop := forall x y, x <= y -> rn x <= rn y.
Definition IdempotentTarget : Prop := forall x, Representable (rn x).
Definition SumDominatesTarget : Prop := forall weights initial weight,
  0 <= initial -> Forall FiniteWeight weights -> In weight weights ->
  weight <= accumulate weights initial.
Definition ShareTarget : Prop := forall weights weight,
  (Z.of_nat (length weights) <= countLimit)%Z ->
  Forall FiniteWeight weights -> In weight weights -> 0 < weight ->
  0 < accumulate weights 0 <= sumLimit /\
  0 < weight / accumulate weights 0 <= 1 /\
  0 <= share weight (accumulate weights 0) <= 1 /\
  Representable (share weight (accumulate weights 0)).
Definition ScaledTarget : Prop := forall factor base,
  FactorValid factor -> 0 <= base <= baseLimit -> FiniteWeight (scaledWeight factor base).
Definition ZeroTarget : Prop := forall denominator,
  0 < denominator -> share 0 denominator = 0.
Definition WitnessTarget : Prop :=
  FiniteWeight 1 /\ accumulate (1 :: nil) 0 = 1 /\ share 1 1 = 1.
Definition FullShareTarget : Prop := MonotoneTarget /\ IdempotentTarget /\
  SumDominatesTarget /\ ShareTarget /\ ScaledTarget /\ ZeroTarget /\ WitnessTarget.
