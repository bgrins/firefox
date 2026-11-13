Require Import Reals ZArith Lia Gappa.Gappa_library.
Require Import Flocq.IEEE754.BinarySingleNaN.
Require Import WeightTarget ShareTarget Share NativeFloatModel.
Module NativeRepresentation.
Lemma value_representable : forall x, Representable (NativeFloat.value x).
Proof.
  intro x. unfold Representable,WeightTarget.rn.
  apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  exact (BinarySingleNaN.generic_format_B2R 53 1024 x).
Qed.
Print Assumptions value_representable.
End NativeRepresentation.
