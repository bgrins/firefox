import Std

namespace CSSOMRounding

abbrev input32 (a : Int) : Prop := -2147483648 ≤ a ∧ a ≤ 2147483647
abbrev signed64 (a : Int) : Prop := -9223372036854775808 ≤ a ∧ a ≤ 9223372036854775807

def trunc60 (a : Int) : Int := if a < 0 then -((-a) / 60) else a / 60
def biased (a : Int) : Int := a + if a ≥ 0 then 30 else -30
def round (a : Int) : Int := trunc60 (biased a)
def magnitudeOracle (a : Int) : Int :=
  if a < 0 then -((-a + 30) / 60) else (a + 30) / 60
def remainderOracle (a : Int) : Int :=
  let magnitude := if a < 0 then -a else a
  let rounded := magnitude / 60 + if magnitude % 60 ≥ 30 then 1 else 0
  if a < 0 then -rounded else rounded

theorem bias_domain (a : Int) (h : input32 a) :
    -2147483678 ≤ biased a ∧ biased a ≤ 2147483677 := by
  unfold biased
  split <;> omega

theorem bias_fits64 (a : Int) (h : input32 a) : signed64 (biased a) := by
  have bounds := bias_domain a h
  omega

theorem source_matches_magnitude (a : Int) : round a = magnitudeOracle a := by
  unfold round trunc60 biased magnitudeOracle
  split <;> split <;> split <;> omega

theorem magnitude_matches_remainder (a : Int) : magnitudeOracle a = remainderOracle a := by
  unfold magnitudeOracle remainderOracle
  split <;> dsimp only <;> split <;> omega

theorem source_matches_remainder (a : Int) : round a = remainderOracle a := by
  rw [source_matches_magnitude, magnitude_matches_remainder]

theorem integral_identity (k : Int) : round (60 * k) = k := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

theorem quotient_domain (a : Int) (h : input32 a) :
    -35791394 ≤ round a ∧ round a ≤ 35791394 := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

theorem result_fits32 (a : Int) (h : input32 a) : input32 (round a) := by
  have bounds := quotient_domain a h
  omega

theorem odd_symmetry (a : Int) : round (-a) = -round a := by
  rw [source_matches_magnitude, source_matches_magnitude]
  unfold magnitudeOracle
  split <;> split <;> omega

theorem native_pair_symmetry (a : Int) (ha : input32 a) (hna : input32 (-a)) :
    input32 (round a) ∧ input32 (round (-a)) ∧ round (-a) = -round a := by
  exact ⟨result_fits32 a ha, result_fits32 (-a) hna, odd_symmetry a⟩

theorem nonnegative_result (a : Int) (h : 0 ≤ a) : 0 ≤ round a := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

theorem positive_half_tie (k : Int) (h : 0 ≤ k) : round (60 * k + 30) = k + 1 := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

theorem negative_half_tie (k : Int) (h : 0 ≤ k) : round (-(60 * k + 30)) = -(k + 1) := by
  rw [odd_symmetry, positive_half_tie k h]

theorem nearest_error (a : Int) :
    -30 ≤ a - 60 * round a ∧ a - 60 * round a ≤ 30 := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

theorem positive_remainder_split (q r : Int) (hq : 0 ≤ q) (hr : 0 ≤ r ∧ r < 60) :
    round (60 * q + r) = q + if r ≥ 30 then 1 else 0 := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> split <;> omega

theorem negative_remainder_split (q r : Int) (hq : 0 ≤ q) (hr : 0 ≤ r ∧ r < 60) :
    round (-(60 * q + r)) = -(q + if r ≥ 30 then 1 else 0) := by
  rw [odd_symmetry, positive_remainder_split q r hq hr]

theorem observed_integral_witness :
    round 503316540 = 8388609 ∧ round (-503316540) = -8388609 ∧
    round 536872800 = 8947880 ∧ round (-536872800) = -8947880 := by decide

theorem extreme_native_inputs :
    biased (-2147483648) = -2147483678 ∧
    biased 2147483647 = 2147483677 ∧
    round (-2147483648) = -35791394 ∧ round 2147483647 = 35791394 := by decide

theorem native_integral_identity (k : Int) (h : input32 (60 * k)) :
    signed64 (biased (60 * k)) ∧ input32 k ∧ round (60 * k) = k := by
  have result := result_fits32 (60 * k) h
  rw [integral_identity] at result
  exact ⟨bias_fits64 _ h, result, integral_identity k⟩

theorem monotone (a b : Int) (h : a ≤ b) : round a ≤ round b := by
  rw [source_matches_magnitude, source_matches_magnitude]
  unfold magnitudeOracle
  split <;> split <;> omega

theorem zero_band (a : Int) : round a = 0 ↔ -29 ≤ a ∧ a ≤ 29 := by
  rw [source_matches_magnitude]
  unfold magnitudeOracle
  split <;> omega

end CSSOMRounding

#print axioms CSSOMRounding.bias_domain
#print axioms CSSOMRounding.bias_fits64
#print axioms CSSOMRounding.source_matches_magnitude
#print axioms CSSOMRounding.magnitude_matches_remainder
#print axioms CSSOMRounding.source_matches_remainder
#print axioms CSSOMRounding.integral_identity
#print axioms CSSOMRounding.quotient_domain
#print axioms CSSOMRounding.result_fits32
#print axioms CSSOMRounding.odd_symmetry
#print axioms CSSOMRounding.native_pair_symmetry
#print axioms CSSOMRounding.nonnegative_result
#print axioms CSSOMRounding.positive_half_tie
#print axioms CSSOMRounding.negative_half_tie
#print axioms CSSOMRounding.nearest_error
#print axioms CSSOMRounding.positive_remainder_split
#print axioms CSSOMRounding.negative_remainder_split
#print axioms CSSOMRounding.observed_integral_witness
#print axioms CSSOMRounding.extreme_native_inputs
#print axioms CSSOMRounding.native_integral_identity
#print axioms CSSOMRounding.monotone
#print axioms CSSOMRounding.zero_band
