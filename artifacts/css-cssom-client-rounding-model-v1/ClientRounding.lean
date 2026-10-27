import Rounding

namespace CSSOMClientRounding

open CSSOMRounding

def biased (a : Int) : Int := a + if a ≥ 0 then 30 else -29
def round (a : Int) : Int := trunc60 (biased a)
def floorOracle (a : Int) : Int := (a + 30) / 60

theorem source_matches_floor (a : Int) : round a = floorOracle a := by
  unfold round trunc60 biased floorOracle
  split <;> split <;> omega

theorem bias_domain (a : Int) (h : input32 a) :
    -2147483677 ≤ biased a ∧ biased a ≤ 2147483677 := by
  unfold biased
  split <;> omega

theorem bias_fits64 (a : Int) (h : input32 a) : signed64 (biased a) := by
  have bounds := bias_domain a h
  omega

theorem quotient_domain (a : Int) (h : input32 a) :
    -35791394 ≤ round a ∧ round a ≤ 35791394 := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem result_fits32 (a : Int) (h : input32 a) : input32 (round a) := by
  have bounds := quotient_domain a h
  omega

theorem integral_identity (k : Int) : round (60 * k) = k := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem native_integral_identity (k : Int) (h : input32 (60 * k)) :
    signed64 (biased (60 * k)) ∧ input32 k ∧ round (60 * k) = k := by
  have result := result_fits32 (60 * k) h
  rw [integral_identity] at result
  exact ⟨bias_fits64 _ h, result, integral_identity k⟩

theorem half_tie (k : Int) : round (60 * k + 30) = k + 1 := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem negative_half_tie (k : Int) :
    round (-(60 * k + 30)) = -k := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem nearest_error (a : Int) :
    -30 ≤ a - 60 * round a ∧ a - 60 * round a ≤ 29 := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem monotone (a b : Int) (h : a ≤ b) : round a ≤ round b := by
  rw [source_matches_floor, source_matches_floor]
  unfold floorOracle
  omega

theorem zero_band (a : Int) : round a = 0 ↔ -30 ≤ a ∧ a ≤ 29 := by
  rw [source_matches_floor]
  unfold floorOracle
  omega

theorem offset_policy_difference (a : Int) :
    round a = CSSOMRounding.round a + if a < 0 ∧ (-a) % 60 = 30 then 1 else 0 := by
  rw [source_matches_floor, CSSOMRounding.source_matches_magnitude]
  unfold floorOracle CSSOMRounding.magnitudeOracle
  split <;> split <;> omega

theorem witnesses :
    round (-30) = 0 ∧ round 30 = 1 ∧ round (-90) = -1 ∧
    round 503316540 = 8388609 ∧ round (-503316540) = -8388609 ∧
    biased (-2147483648) = -2147483677 ∧
    round (-2147483648) = -35791394 ∧ round 2147483647 = 35791394 := by decide

end CSSOMClientRounding

#print axioms CSSOMClientRounding.source_matches_floor
#print axioms CSSOMClientRounding.bias_domain
#print axioms CSSOMClientRounding.bias_fits64
#print axioms CSSOMClientRounding.quotient_domain
#print axioms CSSOMClientRounding.result_fits32
#print axioms CSSOMClientRounding.integral_identity
#print axioms CSSOMClientRounding.native_integral_identity
#print axioms CSSOMClientRounding.half_tie
#print axioms CSSOMClientRounding.negative_half_tie
#print axioms CSSOMClientRounding.nearest_error
#print axioms CSSOMClientRounding.monotone
#print axioms CSSOMClientRounding.zero_band
#print axioms CSSOMClientRounding.offset_policy_difference
#print axioms CSSOMClientRounding.witnesses
