import Std

namespace RoundInterval

inductive Strategy where
  | nearest | up | down | toZero
  deriving DecidableEq, Repr

open Strategy

def choose (mode : Strategy) (value lower upper : Int) : Int :=
  match mode with
  | nearest => if value - lower < upper - value then lower else upper
  | up => upper
  | down => lower
  | toZero => if lower.natAbs < upper.natAbs then lower else upper

def roundExact (mode : Strategy) (value remainder lower upper : Int) : Int :=
  if remainder = 0 then value else choose mode value lower upper

theorem positive_reconstruction (value step remainder towardZero : Int)
    (decomposition : value = towardZero + remainder)
    (positive : 0 < remainder) (bounded : remainder < step) :
    towardZero < value ∧ value < towardZero + step ∧
      (towardZero + step) - towardZero = step := by
  omega

theorem negative_reconstruction (value step remainder towardZero : Int)
    (decomposition : value = towardZero + remainder)
    (negative : remainder < 0) (bounded : -step < remainder) :
    towardZero - step < value ∧ value < towardZero ∧
      towardZero - (towardZero - step) = step := by
  omega

theorem adjacent_positive_multiples (q step : Int) :
    q * step + step = (q + 1) * step := by
  simp [Int.add_mul]

theorem adjacent_negative_multiples (q step : Int) :
    q * step - step = (q - 1) * step := by
  simp [Int.sub_mul]

theorem no_intermediate_multiple (q k step : Int) (positiveStep : 0 < step) :
    ¬(q * step < k * step ∧ k * step < (q + 1) * step) := by
  intro interval
  have lower : q < k := (Int.mul_lt_mul_right positiveStep).mp interval.1
  have upper : k < q + 1 := (Int.mul_lt_mul_right positiveStep).mp interval.2
  omega

theorem positive_consecutive_bracket (value step remainder q : Int)
    (positiveStep : 0 < step)
    (decomposition : value = q * step + remainder)
    (positive : 0 < remainder) (bounded : remainder < step) :
    q * step < value ∧ value < (q + 1) * step ∧
      ∀ k : Int, ¬(q * step < k * step ∧ k * step < (q + 1) * step) := by
  have bracket := positive_reconstruction value step remainder (q * step)
    decomposition positive bounded
  refine ⟨bracket.1, ?_, fun k => no_intermediate_multiple q k step positiveStep⟩
  rw [← adjacent_positive_multiples q step]
  exact bracket.2.1

theorem negative_consecutive_bracket (value step remainder q : Int)
    (positiveStep : 0 < step)
    (decomposition : value = q * step + remainder)
    (negative : remainder < 0) (bounded : -step < remainder) :
    (q - 1) * step < value ∧ value < q * step ∧
      ∀ k : Int, ¬((q - 1) * step < k * step ∧ k * step < q * step) := by
  have bracket := negative_reconstruction value step remainder (q * step)
    decomposition negative bounded
  refine ⟨?_, bracket.2.1, ?_⟩
  · rw [← adjacent_negative_multiples q step]
    exact bracket.1
  · intro k
    simpa using no_intermediate_multiple (q - 1) k step positiveStep

theorem chooses_endpoint (mode : Strategy) (value lower upper : Int) :
    choose mode value lower upper = lower ∨ choose mode value lower upper = upper := by
  cases mode <;> simp only [choose]
  · split <;> simp_all
  · exact Or.inr True.intro
  · exact Or.inl True.intro
  · split <;> simp_all

theorem selected_endpoint_is_multiple (mode : Strategy) (value q step : Int) :
    ∃ k : Int, choose mode value (q * step) ((q + 1) * step) = k * step := by
  rcases chooses_endpoint mode value (q * step) ((q + 1) * step) with h | h
  · exact ⟨q, h⟩
  · exact ⟨q + 1, h⟩

theorem interval_preserved (mode : Strategy) (value lower upper : Int)
    (ordered : lower ≤ upper) :
    lower ≤ choose mode value lower upper ∧ choose mode value lower upper ≤ upper := by
  rcases chooses_endpoint mode value lower upper with h | h <;> omega

theorem directed_strategies (value lower upper : Int)
    (lo : lower ≤ value) (hi : value ≤ upper) :
    choose down value lower upper ≤ value ∧ value ≤ choose up value lower upper := by
  simpa [choose] using And.intro lo hi

theorem nearest_minimizes_distance (value lower upper : Int)
    (lo : lower ≤ value) (hi : value ≤ upper) :
    0 ≤ value - lower ∧ 0 ≤ upper - value ∧
    ((choose nearest value lower upper = lower ∧ value - lower ≤ upper - value) ∨
     (choose nearest value lower upper = upper ∧ upper - value ≤ value - lower)) := by
  simp only [choose]
  split <;> omega

theorem nearest_tie_uses_upper (value lower upper : Int)
    (tie : value - lower = upper - value) :
    choose nearest value lower upper = upper := by
  simp only [choose]
  split <;> omega

theorem toward_zero_minimizes_endpoint_magnitude (value lower upper : Int) :
    (choose toZero value lower upper).natAbs ≤ lower.natAbs ∧
    (choose toZero value lower upper).natAbs ≤ upper.natAbs := by
  simp only [choose]
  split <;> omega

theorem exact_multiple_preserved (mode : Strategy) (value lower upper : Int) :
    roundExact mode value 0 lower upper = value := by
  simp [roundExact]

def witnessValue : Int := 33554432
def witnessStep : Int := 11184811
def witnessLower : Int := 2 * witnessStep
def witnessUpper : Int := 3 * witnessStep

theorem dyadic_witness_interval :
    witnessLower < witnessValue ∧ witnessValue < witnessUpper ∧
    witnessValue - witnessLower = 11184810 ∧ witnessUpper - witnessValue = 1 := by
  decide

theorem dyadic_four_strategy_controls :
    choose down witnessValue witnessLower witnessUpper = 22369622 ∧
    choose toZero witnessValue witnessLower witnessUpper = 22369622 ∧
    choose nearest witnessValue witnessLower witnessUpper = 33554433 ∧
    choose up witnessValue witnessLower witnessUpper = 33554433 := by
  decide

theorem negative_dyadic_controls :
    choose up (-witnessValue) (-witnessUpper) (-witnessLower) = -22369622 ∧
    choose toZero (-witnessValue) (-witnessUpper) (-witnessLower) = -22369622 ∧
    choose nearest (-witnessValue) (-witnessUpper) (-witnessLower) = -33554433 ∧
    choose down (-witnessValue) (-witnessUpper) (-witnessLower) = -33554433 := by
  decide

def quotientScale : Int := 8388608
def quotientValue : Int := witnessValue * quotientScale
def quotientLower : Int := (3 * quotientScale - 2) * witnessStep
def quotientUpper : Int := (3 * quotientScale) * witnessStep

theorem premature_quotient_rounds_up_to_three :
    quotientLower < quotientValue ∧ quotientValue < quotientUpper ∧
    choose nearest quotientValue quotientLower quotientUpper = quotientUpper ∧
    witnessUpper ≠ choose down witnessValue witnessLower witnessUpper := by
  decide

theorem final_product_rounds_back_to_one :
    choose nearest 33554433 33554432 33554436 = 33554432 := by
  decide

theorem rounded_quotient_pipeline_disagrees_with_down :
    choose nearest 33554433 33554432 33554436 = witnessValue ∧
    choose nearest 33554433 33554432 33554436 ≠
      choose down witnessValue witnessLower witnessUpper := by
  decide

theorem exact_quarter_control :
    roundExact down 33554432 0 33554432 41943040 = 33554432 ∧
    roundExact toZero 33554432 0 33554432 41943040 = 33554432 := by
  decide

end RoundInterval
