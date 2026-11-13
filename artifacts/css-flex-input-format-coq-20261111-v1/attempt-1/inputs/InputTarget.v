Require Import Reals ZArith List Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget ShareTarget Target ConversionTarget DistributionTarget.
Open Scope R_scope.
Definition Float32 := Binary.binary_float 24 128.
Definition value32 (factor : Float32) : R := Binary.B2R 24 128 factor.
Definition FactorInput (factor : Float32) : Prop :=
  Binary.is_finite 24 128 factor = true /\ 0 <= value32 factor.
Record WeightInput := {
  factor : Float32;
  base : Z;
  growing : bool
}.
Definition InputValid (input : WeightInput) : Prop :=
  FactorInput (factor input) /\
  (-2147483648 <= base input <= 2147483647)%Z /\
  (growing input = false -> (0 <= base input)%Z).
Definition inputWeight (input : WeightInput) : R :=
  if growing input then WeightTarget.rn (value32 (factor input))
  else WeightTarget.rn (WeightTarget.rn (value32 (factor input)) * WeightTarget.rn (IZR (base input))).
Definition PromotionTarget : Prop := forall factor,
  FactorInput factor -> FactorValid (value32 factor) /\ Representable (value32 factor).
Definition IntegerPromotionTarget : Prop := forall base,
  (-2147483648 <= base <= 2147483647)%Z -> Representable (IZR base).
Definition InputWeightTarget : Prop := forall input,
  InputValid input -> FiniteWeight (inputWeight input).
Definition InputListTarget : Prop := forall inputs,
  Forall InputValid inputs -> Forall FiniteWeight (map inputWeight inputs).
Definition InputDistributionTarget : Prop := forall free inputs input,
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  (Z.of_nat (length inputs) <= countLimit)%Z ->
  Forall InputValid inputs -> In input inputs ->
  EnvelopeZ free (finiteDelta free (map inputWeight inputs) (inputWeight input)) /\
  Fits64 (finiteDelta free (map inputWeight inputs) (inputWeight input)).
Definition InputWitnessTarget : Prop :=
  exists grow shrink, InputValid grow /\ InputValid shrink /\
  growing grow = true /\ growing shrink = false /\
  inputWeight grow = 1 /\ inputWeight shrink = 1.
Definition FullInputTarget : Prop := PromotionTarget /\ IntegerPromotionTarget /\
  InputWeightTarget /\ InputListTarget /\ InputDistributionTarget /\ InputWitnessTarget.
