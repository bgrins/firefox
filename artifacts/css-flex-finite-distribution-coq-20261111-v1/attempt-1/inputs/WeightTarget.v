Require Import Reals ZArith List Gappa.Gappa_library.
Open Scope R_scope.
Definition rn (x : R) := rounding_float rndNE 53 (-1074) x.
Definition factorLimit : R := 340282366920938463463374607431768211456.
Definition baseLimit : R := 2147483648.
Definition weightLimit : R := 730750818665451459101842416358141509827966271488.
Definition stride : R := 1461501637330902918203684832716283019655932542976.
Definition sumLimit : R := 6277101735386680763835789423207666416102355444464034512896.
Definition intermediateLimit : R := 12554203470773361527671578846415332832204710888928069025792.
Definition countLimit : Z := 4294967295.
Definition WeightValid (weight : R) := 0 <= weight <= weightLimit.
Definition FactorValid (factor : R) := 0 <= factor <= factorLimit.
Definition scaledWeight (factor base : R) := rn (factor*base).
Definition accumulate (weights : list R) (initial : R) :=
  fold_left (fun sum weight => rn (sum+weight)) weights initial.
Definition StepBound (sum weight : R) :=
  0 <= sum+weight <= intermediateLimit /\
  0 <= rn (sum+weight) <= intermediateLimit /\
  rn (sum+weight) <= sum+stride.
Definition ProductTarget : Prop := forall factor base,
  FactorValid factor -> 0 <= base <= baseLimit -> WeightValid (scaledWeight factor base).
Definition AdditionTarget : Prop := forall sum weight,
  0 <= sum <= sumLimit -> WeightValid weight -> StepBound sum weight.
Definition OrderedTarget : Prop := forall weights,
  (Z.of_nat (length weights) <= countLimit)%Z -> Forall WeightValid weights ->
  0 <= accumulate weights 0 <= IZR (Z.of_nat (length weights))*stride.
Definition PrefixTarget : Prop := forall weights count,
  (Z.of_nat (length weights) <= countLimit)%Z -> Forall WeightValid weights ->
  0 <= accumulate (firstn count weights) 0 <= sumLimit.
Definition FactorSumTarget : Prop := forall factors,
  (Z.of_nat (length factors) <= countLimit)%Z -> Forall FactorValid factors ->
  0 <= accumulate factors 0 <= sumLimit.
Definition FullWeightTarget : Prop :=
  ProductTarget /\ AdditionTarget /\ OrderedTarget /\ PrefixTarget /\ FactorSumTarget.
