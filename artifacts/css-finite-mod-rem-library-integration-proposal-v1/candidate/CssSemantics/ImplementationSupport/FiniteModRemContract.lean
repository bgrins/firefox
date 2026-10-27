import CssSemantics.ImplementationSupport.Binary32Magnitude
import CssSemantics.ImplementationSupport.FiniteModRemTypes

namespace CssSemantics.ImplementationSupport.FiniteModRemContract
open RoundRemainderCapacity ModRemInfinity

def needsAdjustment (remainder divisor : Int) : Prop :=
  remainder ≠ 0 ∧ decide (remainder < 0) ≠ decide (divisor < 0)

instance (remainder divisor : Int) : Decidable (needsAdjustment remainder divisor) :=
  inferInstanceAs (Decidable (remainder ≠ 0 ∧ decide (remainder < 0) ≠ decide (divisor < 0)))

def adjust (remainder divisor : Int) : Int :=
  if needsAdjustment remainder divisor then remainder + divisor else remainder

def ExactInterval (divisor value : Int) : Prop :=
  if 0 < divisor then 0 ≤ value ∧ value < divisor else divisor < value ∧ value ≤ 0

def ModRelation (dividend divisor value : Int) : Prop :=
  ExactInterval divisor value ∧ ∃ multiple : Int, dividend = multiple * divisor + value

theorem adjustment_mod_relation (dividend divisor : Int) (nonzero : divisor ≠ 0) :
    ModRelation dividend divisor (adjust (dividend.tmod divisor) divisor) := by
  have equation := Int.tdiv_mul_add_tmod dividend divisor
  constructor
  · by_cases positive : 0 < divisor
    · have lower := Int.lt_tmod_of_pos dividend positive
      have upper := Int.tmod_lt_of_pos dividend positive
      by_cases rnegative : dividend.tmod divisor < 0
      · have rz : dividend.tmod divisor ≠ 0 := by omega
        simp [ExactInterval, positive, adjust, needsAdjustment, rnegative, rz,
          show ¬ divisor < 0 by omega]
        omega
      · simp [ExactInterval, positive, adjust, needsAdjustment, rnegative,
          show ¬ divisor < 0 by omega]
        omega
    · have negative : divisor < 0 := by omega
      have lower := Int.lt_tmod_of_pos dividend (b := -divisor) (by omega)
      have upper := Int.tmod_lt_of_pos dividend (b := -divisor) (by omega)
      rw [Int.tmod_neg] at lower upper
      by_cases rz : dividend.tmod divisor = 0
      · simp [ExactInterval, positive, adjust, needsAdjustment, rz, negative]
      · by_cases rnegative : dividend.tmod divisor < 0
        · simp [ExactInterval, positive, adjust, needsAdjustment, rnegative, negative]
          omega
        · simp [ExactInterval, positive, adjust, needsAdjustment, rnegative, rz, negative]
          omega
  · unfold adjust
    split
    · refine ⟨dividend.tdiv divisor - 1, ?_⟩
      rw [Int.sub_mul]
      omega
    · exact ⟨dividend.tdiv divisor, equation.symm⟩

def distance (x y : Int) : Int := if x ≤ y then y - x else x - y

def NearestProjection (exact projected : Int) : Prop :=
  SignedEncoding projected ∧ ∀ candidate : Int, SignedEncoding candidate →
    distance exact projected ≤ distance exact candidate

theorem encoded_zero : SignedEncoding 0 := by
  exact ⟨0, 0, by decide, by decide, by decide⟩

theorem nearest_closed_interval (divisor exact projected : Int)
    (divisorEncoding : SignedEncoding divisor) (interval : ExactInterval divisor exact)
    (nearest : NearestProjection exact projected) :
    (if 0 < divisor then 0 ≤ projected ∧ projected ≤ divisor
     else divisor ≤ projected ∧ projected ≤ 0) := by
  have zeroBound := nearest.2 0 encoded_zero
  have divisorBound := nearest.2 divisor divisorEncoding
  by_cases positive : 0 < divisor
  · have bounds : 0 ≤ exact ∧ exact < divisor := by simpa [ExactInterval, positive] using interval
    simp only [ite_eq_left positive]
    by_cases low : projected < 0
    · simp only [distance, ite_eq_right (show ¬ exact ≤ projected by omega)] at zeroBound
      split at zeroBound <;> omega
    · by_cases high : divisor < projected
      · simp [distance, show exact ≤ projected by omega, show exact ≤ divisor by omega] at divisorBound
        omega
      · omega
  · have bounds : divisor < exact ∧ exact ≤ 0 := by simpa [ExactInterval, positive] using interval
    simp only [ite_eq_right positive]
    by_cases low : projected < divisor
    · simp [distance, show ¬ exact ≤ projected by omega, show ¬ exact ≤ divisor by omega] at divisorBound
      omega
    · by_cases high : 0 < projected
      · simp [distance, show exact ≤ projected by omega, show exact ≤ 0 by omega] at zeroBound
        omega
      · omega

theorem nearest_self (value : Int) (encoded : SignedEncoding value) :
    NearestProjection value value := by
  refine ⟨encoded, ?_⟩
  intro candidate _
  simp only [distance]
  split <;> split <;> omega

def candidateGrid (op : Op) (project : Int → Int) (remainder divisor : Int) : Int :=
  match op with
  | .rem => remainder
  | .mod => if needsAdjustment remainder divisor then project (remainder + divisor) else remainder

def zeroSign (op : Op) (dividendSign divisorSign : Bool) : Bool :=
  match op with
  | .rem => dividendSign
  | .mod => divisorSign

def encode (sign : Bool) (value : Int) : Finite Nat :=
  if value = 0 then .zero sign else .nonzero (decide (value < 0)) value.natAbs

def candidate (op : Op) (project : Int → Int) (dividendSign divisorSign : Bool)
    (remainder divisor : Int) : Finite Nat :=
  encode (zeroSign op dividendSign divisorSign) (candidateGrid op project remainder divisor)

theorem zero_sign_preserved (op : Op) (project : Int → Int) (aSign bSign : Bool)
    (remainder divisor : Int) (zero : candidateGrid op project remainder divisor = 0) :
    candidate op project aSign bSign remainder divisor = .zero (zeroSign op aSign bSign) := by
  simp [candidate, encode, zero]

theorem exact_multiple_zero (op : Op) (project : Int → Int) (aSign bSign : Bool)
    (divisor : Int) :
    candidate op project aSign bSign 0 divisor = .zero (zeroSign op aSign bSign) := by
  cases op <;> simp [candidate, candidateGrid, needsAdjustment, encode]

theorem rem_exact (project : Int → Int) (dividend divisor supplied : Int)
    (rustRemainderCorrespondence : supplied = dividend.tmod divisor) :
    candidateGrid .rem project supplied divisor = dividend.tmod divisor := by
  exact rustRemainderCorrespondence

theorem mod_projected_relation (project : Int → Int) (dividend divisor supplied : Int)
    (aEncoding : SignedEncoding dividend) (bEncoding : SignedEncoding divisor)
    (nonzero : divisor ≠ 0)
    (rustRemainderCorrespondence : supplied = dividend.tmod divisor)
    (additionNearest : needsAdjustment supplied divisor →
      NearestProjection (supplied + divisor) (project (supplied + divisor))) :
    ∃ exact, ModRelation dividend divisor exact ∧
      NearestProjection exact (candidateGrid .mod project supplied divisor) := by
  subst supplied
  refine ⟨adjust (dividend.tmod divisor) divisor,
    adjustment_mod_relation dividend divisor nonzero, ?_⟩
  by_cases needed : needsAdjustment (dividend.tmod divisor) divisor
  · simpa [adjust, candidateGrid, needed] using additionNearest needed
  · simpa [adjust, candidateGrid, needed] using nearest_self (dividend.tmod divisor)
      (signed_truncating_remainder_capacity dividend divisor aEncoding bEncoding nonzero)

theorem mod_projected_closed_interval (project : Int → Int) (dividend divisor supplied : Int)
    (aEncoding : SignedEncoding dividend) (bEncoding : SignedEncoding divisor)
    (nonzero : divisor ≠ 0)
    (rustRemainderCorrespondence : supplied = dividend.tmod divisor)
    (additionNearest : needsAdjustment supplied divisor →
      NearestProjection (supplied + divisor) (project (supplied + divisor))) :
    (if 0 < divisor then
      0 ≤ candidateGrid .mod project supplied divisor ∧ candidateGrid .mod project supplied divisor ≤ divisor
     else divisor ≤ candidateGrid .mod project supplied divisor ∧ candidateGrid .mod project supplied divisor ≤ 0) := by
  obtain ⟨exact, relation, nearest⟩ := mod_projected_relation project dividend divisor supplied
    aEncoding bEncoding nonzero rustRemainderCorrespondence additionNearest
  exact nearest_closed_interval divisor exact _ bEncoding relation.1 nearest

theorem endpoint_predecessor_unrepresentable : ¬ SignedEncoding (33554431 : Int) := by
  rintro ⟨coefficient, exponent, hc, _, hv⟩
  change 33554431 = coefficient * 2 ^ exponent at hv
  cases exponent with
  | zero => simp at hv; omega
  | succ e =>
    rw [Nat.pow_succ, ← Nat.mul_assoc] at hv
    omega

theorem endpoint_projection : NearestProjection 33554431 33554432 := by
  refine ⟨⟨8388608, 2, by decide, by decide, by decide⟩, ?_⟩
  intro candidate encoded
  have different : candidate ≠ 33554431 := by
    intro eq
    subst candidate
    exact endpoint_predecessor_unrepresentable encoded
  simp only [distance]
  split <;> split <;> omega

theorem strict_projected_interval_false :
    ModRelation (-1) 33554432 33554431 ∧ NearestProjection 33554431 33554432 ∧
    ¬ ExactInterval 33554432 33554432 := by
  refine ⟨?_, endpoint_projection, by simp [ExactInterval]⟩
  exact adjustment_mod_relation (-1) 33554432 (by decide)

end CssSemantics.ImplementationSupport.FiniteModRemContract
