import CssSemantics.ImplementationSupport.Binary32Magnitude
import CssSemantics.ImplementationSupport.FiniteModRemTypes

namespace CssSemantics.ImplementationSupport.FiniteModRemWitness
open Binary32Magnitude

def unit : Nat := 2^149
def a : BitVec 32 := BitVec.ofNat 32 0x4c000000
def b : BitVec 32 := BitVec.ofNat 32 0x40400000
def q : BitVec 32 := BitVec.ofNat 32 0x4b2aaaab
def r : BitVec 32 := BitVec.ofNat 32 0x40000000

def distance (x y : Nat) : Nat := x - y + (y - x)

theorem raw_strict (e f g h : Nat) (hf : f < 8388608)
    (order : e < g) : rawMagnitude e f < rawMagnitude g h := by
  have gp : g ≠ 0 := by omega
  have powpos : 0 < 2^(g - 1) := Nat.two_pow_pos _
  by_cases ep : e = 0
  · have bound := Nat.mul_le_mul_left 8388608 (Nat.one_le_two_pow (n := g - 1))
    have bigger := Nat.mul_le_mul_right (2^(g - 1)) (show 8388608 ≤ 8388608 + h by omega)
    simp [rawMagnitude, ep, gp]
    omega
  · have coeff : 8388608 + f < 16777216 := by omega
    have first := Nat.mul_lt_mul_of_pos_right coeff (Nat.two_pow_pos (e - 1))
    have ex : e = (e - 1) + 1 := by omega
    have step : 16777216 * 2^(e - 1) = 8388608 * 2^e := by
      conv => rhs; rw [ex, Nat.pow_succ]
      omega
    have power := Nat.pow_le_pow_right (by decide : 0 < 2) (show e ≤ g - 1 by omega)
    have second := Nat.mul_le_mul_left 8388608 power
    have third := Nat.mul_le_mul_right (2^(g - 1)) (show 8388608 ≤ 8388608 + h by omega)
    simp [rawMagnitude, ep, gp]
    omega

theorem q_spacing (bits : BitVec 32) :
    decode bits ≤ 11184810 * unit ∨ decode bits = 11184811 * unit ∨
    11184812 * unit ≤ decode bits := by
  let e := exponentField bits
  let f := fractionField bits
  have hf : f < 8388608 := Nat.mod_lt _ (by decide)
  change rawMagnitude e f ≤ _ ∨ rawMagnitude e f = _ ∨ _ ≤ rawMagnitude e f
  by_cases lo : e < 150
  · have h := raw_strict e f 150 0 hf lo
    have v : rawMagnitude 150 0 = 8388608 * unit := by decide +kernel
    rw [v] at h
    left
    omega
  · by_cases hi : 150 < e
    · have h := raw_strict 150 8388607 e f (by decide) hi
      have v : rawMagnitude 150 8388607 = 16777215 * unit := by decide +kernel
      rw [v] at h
      right; right
      omega
    · have eq : e = 150 := by omega
      rw [eq]
      simp only [rawMagnitude]
      change (8388608 + f) * unit ≤ _ ∨ (8388608 + f) * unit = _ ∨ _ ≤ (8388608 + f) * unit
      simp [unit] at *
      omega

theorem a_spacing (bits : BitVec 32) :
    decode bits ≤ 33554430 * unit ∨ decode bits = 33554432 * unit ∨
    33554436 * unit ≤ decode bits := by
  let e := exponentField bits
  let f := fractionField bits
  have hf : f < 8388608 := Nat.mod_lt _ (by decide)
  change rawMagnitude e f ≤ _ ∨ rawMagnitude e f = _ ∨ _ ≤ rawMagnitude e f
  by_cases lo : e < 151
  · have h := raw_strict e f 151 0 hf lo
    have v : rawMagnitude 151 0 = 16777216 * unit := by decide +kernel
    rw [v] at h
    left; omega
  · by_cases same : e = 151
    · rw [same]
      simp only [rawMagnitude]
      change (8388608 + f) * (2 * unit) ≤ _ ∨ _ ∨ _
      left
      simp [unit] at *
      omega
    · by_cases upper : e = 152
      · rw [upper]
        simp only [rawMagnitude]
        change (8388608 + f) * (4 * unit) ≤ _ ∨ _ ∨ _
        by_cases zero : f = 0
        · right; left; rw [zero]; decide +kernel
        · right; right
          simp [unit] at *
          omega
      · have h := raw_strict 152 0 e f (by decide) (by omega)
        have v : rawMagnitude 152 0 = 33554432 * unit := by decide +kernel
        rw [v] at h
        have h2 := raw_strict 152 1 e f (by decide) (by omega)
        have v2 : rawMagnitude 152 1 = 33554436 * unit := by decide +kernel
        rw [v2] at h2
        right; right; omega

theorem concrete_values :
    finite a ∧ finite b ∧ finite q ∧ finite r ∧
    decode a = 33554432 * unit ∧ decode b = 3 * unit ∧
    decode q = 11184811 * unit ∧ decode r = 2 * unit := by
  decide +kernel

def Nearest (numerator denominator : Nat) (result : BitVec 32) : Prop :=
  finite result ∧ ∀ candidate : BitVec 32, finite candidate →
    distance numerator (denominator * decode result) ≤
      distance numerator (denominator * decode candidate)

theorem quotient_strict (bits : BitVec 32) (other : decode bits ≠ decode q) :
    distance (decode a) (3 * decode q) < distance (decode a) (3 * decode bits) := by
  have values := concrete_values
  have spacing := q_spacing bits
  simp [distance, unit] at *
  omega

theorem product_strict (bits : BitVec 32) (other : decode bits ≠ decode a) :
    distance (33554433 * unit) (decode a) <
      distance (33554433 * unit) (decode bits) := by
  have values := concrete_values
  have spacing := a_spacing bits
  simp [distance, unit] at *
  omega

theorem quotient_nearest : Nearest (decode a) 3 q := by
  refine ⟨concrete_values.2.2.1, ?_⟩
  intro bits _
  by_cases same : decode bits = decode q
  · rw [same]
    exact Nat.le_refl _
  · exact Nat.le_of_lt (quotient_strict bits same)

theorem product_nearest : Nearest (33554433 * unit) 1 a := by
  refine ⟨concrete_values.1, ?_⟩
  intro bits _
  simp only [Nat.one_mul]
  by_cases same : decode bits = decode a
  · rw [same]
    exact Nat.le_refl _
  · exact Nat.le_of_lt (product_strict bits same)

theorem quotient_unique (bits : BitVec 32) (h : Nearest (decode a) 3 bits) :
    decode bits = decode q := by
  by_cases eq : decode bits = decode q
  · exact eq
  · have strict := quotient_strict bits eq
    have reverse := h.2 q concrete_values.2.2.1
    omega

theorem product_unique (bits : BitVec 32) (h : Nearest (33554433 * unit) 1 bits) :
    decode bits = decode a := by
  by_cases eq : decode bits = decode a
  · exact eq
  · have strict := product_strict bits eq
    have reverse := h.2 a concrete_values.1
    simp only [Nat.one_mul] at reverse
    omega

def RoundingContract (round : Nat → Nat → BitVec 32) : Prop :=
  Nearest (decode a) 3 (round (decode a) 3) ∧
  Nearest (33554433 * unit) 1 (round (33554433 * unit) 1)

def roundedFormula (round : Nat → Nat → BitVec 32) : Int :=
  let quotient := round (decode a) 3
  let integralQuotient := decode quotient / unit
  let product := round (decode b * integralQuotient) 1
  (decode a : Int) - (decode product : Int)

theorem rounded_formula_zero (round : Nat → Nat → BitVec 32)
    (contract : RoundingContract round) : roundedFormula round = 0 := by
  have qvalue := quotient_unique _ contract.1
  have productvalue := product_unique _ contract.2
  have values := concrete_values
  have intq : decode (round (decode a) 3) / unit = 11184811 := by
    rw [qvalue, values.2.2.2.2.2.2.1]
    decide +kernel
  have productInput : decode b * (decode (round (decode a) 3) / unit) =
      33554433 * unit := by
    rw [intq, values.2.2.2.2.2.1]
    decide +kernel
  dsimp only [roundedFormula]
  rw [productInput, productvalue]
  omega

def SpecRemainder (value : Int) : Prop :=
  0 ≤ value ∧ value < 3 ∧ ∃ multiple : Int, 33554432 = 3 * multiple + value

theorem spec_remainder_unique (value : Int) : SpecRemainder value ↔ value = 2 := by
  constructor
  · rintro ⟨lower, upper, multiple, equation⟩
    omega
  · intro eq
    subst value
    exact ⟨by decide, by decide, 11184810, by decide⟩

theorem formula_disagrees (round : Nat → Nat → BitVec 32)
    (contract : RoundingContract round) : roundedFormula round ≠ (decode r : Int) := by
  rw [rounded_formula_zero round contract, concrete_values.2.2.2.2.2.2.2]
  decide +kernel

def localRound (numerator denominator : Nat) : BitVec 32 :=
  if numerator = decode a ∧ denominator = 3 then q else a

theorem rounding_contract_inhabited : RoundingContract localRound := by
  constructor
  · simpa [localRound] using quotient_nearest
  · have different : 33554433 * unit ≠ decode a := by
      rw [concrete_values.2.2.2.2.1]
      decide +kernel
    simpa [localRound, different] using product_nearest

theorem remainder_capacity_reused :
    ∃ bits : BitVec 32, finite bits ∧ decode bits = decode a % decode b := by
  apply remainder_has_bits a b concrete_values.1 concrete_values.2.1
  rw [concrete_values.2.2.2.2.2.1]
  decide +kernel

def numberOfGrid (value : Int) : ModRemInfinity.Number Nat :=
  if value = 0 then .finite (.zero false)
  else .finite (.nonzero (value < 0) value.natAbs)

theorem finite_agreement_impossible
    (round : Nat → Nat → BitVec 32) (rounding : RoundingContract round)
    (nativeArithmetic specArithmetic : ModRemInfinity.FiniteBackend Nat)
    (op : ModRemInfinity.Op)
    (nativeCorrespondence :
      nativeArithmetic op (.nonzero false (decode a)) false (decode b) =
        numberOfGrid (roundedFormula round))
    (specCorrespondence : ∃ value : Int, SpecRemainder value ∧
      specArithmetic op (.nonzero false (decode a)) false (decode b) =
        numberOfGrid (value * (unit : Int))) :
    ¬ (∀ operation input sign magnitude,
      nativeArithmetic operation input sign magnitude =
        specArithmetic operation input sign magnitude) := by
  intro agreement
  obtain ⟨value, spec, eq⟩ := specCorrespondence
  have value_eq := (spec_remainder_unique value).1 spec
  have same := agreement op (.nonzero false (decode a)) false (decode b)
  rw [nativeCorrespondence, eq, value_eq, rounded_formula_zero round rounding] at same
  simp [numberOfGrid, unit] at same

end CssSemantics.ImplementationSupport.FiniteModRemWitness
