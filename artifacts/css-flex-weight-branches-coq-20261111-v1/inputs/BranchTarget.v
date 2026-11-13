Require Import Reals ZArith List Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget ShareTarget Target ConversionTarget DistributionTarget InputTarget.
Open Scope R_scope.
Definition sourceWeight (input : WeightInput) : R :=
  if growing input then value32 (factor input)
  else if Z.eqb (base input) 0 then 0
  else WeightTarget.rn (WeightTarget.rn (value32 (factor input)) * WeightTarget.rn (IZR (base input))).
Definition WeightEquivalenceTarget : Prop := forall input,
  InputValid input -> sourceWeight input = inputWeight input.
Definition EarlyZeroTarget : Prop := forall factor,
  sourceWeight {| InputTarget.factor := factor; base := 0; growing := false |} = 0.
Definition SourceFiniteTarget : Prop := forall input,
  InputValid input -> FiniteWeight (sourceWeight input).
Definition SourceDistributionTarget : Prop := forall free inputs input,
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  (Z.of_nat (length inputs) <= countLimit)%Z ->
  Forall InputValid inputs -> In input inputs ->
  EnvelopeZ free (finiteDelta free (map sourceWeight inputs) (sourceWeight input)) /\
  Fits64 (finiteDelta free (map sourceWeight inputs) (sourceWeight input)).
Definition NonfiniteControlTarget : Prop := exists factor,
  Binary.is_finite 24 128 factor = false /\ value32 factor = 0 /\
  ~ FactorInput factor /\
  sourceWeight {| InputTarget.factor := factor; base := 0; growing := false |} = 0.
Definition FullWeightBranchesTarget : Prop := WeightEquivalenceTarget /\ EarlyZeroTarget /\
  SourceFiniteTarget /\ SourceDistributionTarget /\ NonfiniteControlTarget.
