Require Import Reals ZArith List Bool Lia.
Require Import Flocq.IEEE754.Binary Flocq.IEEE754.BinarySingleNaN.
Require Import InputTarget WeightTarget ConversionTarget.
Module NativeFloat.
Open Scope Z_scope.
Definition F64 := BinarySingleNaN.binary_float 53 1024.
Definition zero : F64 := @BinarySingleNaN.B754_zero 53 1024 false.
Definition infinity : F64 := @BinarySingleNaN.B754_infinity 53 1024 false.
Definition nan : F64 := @BinarySingleNaN.B754_nan 53 1024.
Definition value (x : F64) : R := @BinarySingleNaN.B2R 53 1024 x.
Definition finite (x : F64) := @BinarySingleNaN.is_finite 53 1024 x.
Definition normalize (m e : Z) (sign : bool) : F64 :=
  @BinarySingleNaN.binary_normalize 53 1024 ltac:(constructor; lia) ltac:(constructor; lia)
    BinarySingleNaN.mode_NE m e sign.
Definition integer (x : Z) : F64 := normalize x 0 false.
Definition one := integer 1.
Definition half := normalize 1 (-1) false.
Definition promote (x : Float32) : F64 :=
  match x with
  | @Binary.B754_zero _ _ sign => @BinarySingleNaN.B754_zero 53 1024 sign
  | @Binary.B754_infinity _ _ sign => @BinarySingleNaN.B754_infinity 53 1024 sign
  | @Binary.B754_nan _ _ _ _ _ => nan
  | @Binary.B754_finite _ _ sign mant exponent _ =>
      normalize (if sign then -Z.pos mant else Z.pos mant) exponent sign
  end.
Definition add (x y : F64) : F64 :=
  @BinarySingleNaN.Bplus 53 1024 ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y.
Definition multiply (x y : F64) : F64 :=
  @BinarySingleNaN.Bmult 53 1024 ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y.
Definition divide (x y : F64) : F64 :=
  @BinarySingleNaN.Bdiv 53 1024 ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y.
Definition equal (x y : F64) : bool :=
  match @BinarySingleNaN.Bcompare 53 1024 x y with Some Eq => true | _ => false end.
Definition less (x y : F64) : bool :=
  match @BinarySingleNaN.Bcompare 53 1024 x y with Some Lt => true | _ => false end.
Definition floorFinite (x : F64) : option Z :=
  match x with
  | @BinarySingleNaN.B754_zero _ _ _ => Some 0
  | @BinarySingleNaN.B754_finite _ _ sign mant exponent _ =>
    let signedMantissa := if sign then -Z.pos mant else Z.pos mant in
    Some (if Z.leb 0 exponent then signedMantissa * Z.pow 2 exponent
          else Z.div signedMantissa (Z.pow 2 (-exponent)))
  | _ => None
  end.
Definition roundInteger (x : F64) : option Z := floorFinite (add x half).
Definition scale (free : Z) (share : F64) := roundInteger (multiply (integer free) share).
Definition equally (free : Z) (count : nat) := roundInteger (divide (integer free) (integer (Z.of_nat count))).
Definition fractionDelta (free : Z) (share : F64) :=
  if equal share one then Some free else
  if less zero share then scale free share else Some 0.
End NativeFloat.
