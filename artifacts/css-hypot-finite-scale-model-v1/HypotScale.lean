import CssSemantics.ImplementationSupport.Binary32Magnitude

namespace HypotScale
open CssSemantics.ImplementationSupport.Binary32Magnitude

def unit : Nat := 2^149
def zero : BitVec 32 := pack 0 0
def tiny : BitVec 32 := pack 47 0
def twiceTiny : BitVec 32 := pack 48 0
def large : BitVec 32 := pack 191 0
def twiceLarge : BitVec 32 := pack 192 0
def maximum : Nat := 16777215 * 2^253
def distance (a b : Nat) : Nat := a - b + (b - a)

def Nearest (numerator denominator : Nat) (result : BitVec 32) : Prop :=
  finite result ∧ ∀ candidate : BitVec 32, finite candidate →
    distance numerator (denominator * decode result) ≤
      distance numerator (denominator * decode candidate)

theorem zero_decode : decode zero = 0 := by decide +kernel

theorem zero_nearest (n d : Nat) (belowHalf : 2 * n < d) :
    Nearest n d zero := by
  refine ⟨by decide +kernel, ?_⟩
  intro bits _
  rw [zero_decode]
  by_cases hz : decode bits = 0
  · simp [hz]
  · have lower := Nat.mul_le_mul_left d (show 1 ≤ decode bits by omega)
    simp only [Nat.mul_one] at lower
    simp only [distance, Nat.mul_zero, Nat.sub_zero, Nat.zero_sub, Nat.add_zero]
    omega

theorem below_half_unique (n d : Nat) (belowHalf : 2 * n < d)
    (bits : BitVec 32) (nearest : Nearest n d bits) : decode bits = 0 := by
  have bound := nearest.2 zero (by decide +kernel)
  rw [zero_decode] at bound
  by_cases isZero : decode bits = 0
  · exact isZero
  · have lower := Nat.mul_le_mul_left d (show 1 ≤ decode bits by omega)
    simp only [Nat.mul_one] at lower
    simp only [distance, Nat.mul_zero, Nat.sub_zero, Nat.zero_sub, Nat.add_zero] at bound
    omega

theorem finite_bound (bits : BitVec 32) (h : finite bits) : decode bits ≤ maximum := by
  obtain ⟨m, e, hm, he, eq⟩ := decode_sound bits h
  rw [eq]
  exact Nat.mul_le_mul (by omega) (Nat.pow_le_pow_right (by decide) he)

theorem witness_encodings :
    finite tiny ∧ finite twiceTiny ∧ finite large ∧ finite twiceLarge ∧
    decode tiny = 2^69 ∧ decode twiceTiny = 2^70 ∧
    decode large = 2^213 ∧ decode twiceLarge = 2^214 := by
  decide +kernel

theorem tiny_square_below_half : 2 * (decode tiny * decode tiny) < unit := by
  decide +kernel

theorem tiny_square_rounds_zero : Nearest (decode tiny * decode tiny) unit zero :=
  zero_nearest _ _ tiny_square_below_half

theorem tiny_square_unique (bits : BitVec 32)
    (rounded : Nearest (decode tiny * decode tiny) unit bits) : decode bits = 0 :=
  below_half_unique _ _ tiny_square_below_half bits rounded

theorem large_square_out_of_range (bits : BitVec 32) (h : finite bits) :
    unit * decode bits < decode large * decode large := by
  have bound := Nat.mul_le_mul_left unit (finite_bound bits h)
  have strict : unit * maximum < decode large * decode large := by decide +kernel
  omega

theorem normalized_inputs :
    0 < decode tiny ∧ 2 * decode tiny = decode twiceTiny ∧
    0 < decode large ∧ 2 * decode large = decode twiceLarge := by
  decide +kernel

theorem exact_ratios :
    (decode tiny : Rat) / (decode twiceTiny : Rat) = (1 : Rat) / 2 ∧
    (decode large : Rat) / (decode twiceLarge : Rat) = (1 : Rat) / 2 := by
  decide +kernel

theorem squared_norm_with_zero (m : Nat) : m * m + 0 * 0 = m * m := by simp

end HypotScale
