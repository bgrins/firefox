import ExactTraversalBounds
namespace IndependentBounds
open ExactTraversalBounds

def accumulate (origin : Int) (positions : List Int) : Int :=
  positions.foldl (fun n p => n + p) origin

theorem cumulative_source_shape (origin : Int) (positions : List Int) :
    accumulate origin positions = origin + positions.sum := by
  induction positions generalizing origin with
  | nil => simp [accumulate]
  | cons x xs ih =>
    simpa [accumulate, Int.add_assoc] using ih (origin + x)

theorem final_translation_for_arbitrary_finite_positions
    (origin : Int) (positions : List Int) (ho : Int32 origin)
    (hf : Int32 (accumulate origin positions)) :
    Difference33 positions.sum ∧ Int64 positions.sum := by
  exact translation_width origin positions.sum (accumulate origin positions)
    ho hf (cumulative_source_shape origin positions)

theorem sharp_positive_difference :
    Int32 (2147483647 : Int) ∧ Int32 (-2147483648 : Int) ∧
    (2147483647 : Int) - (-2147483648) = 4294967295 ∧
    ¬ Int32 (2147483647 - (-2147483648)) ∧
    Int64 (2147483647 - (-2147483648)) := by decide

theorem sharp_negative_difference :
    (-2147483648 : Int) - 2147483647 = -4294967295 ∧
    Int64 ((-2147483648 : Int) - 2147483647) := by decide

theorem final_bound_alone_does_not_bound_intermediate_translation :
    Int32 (accumulate 0 [2000000000,2000000000,2000000000,
      -2000000000,-2000000000,-2000000000]) ∧
    ¬ Difference33 (accumulate 0 [2000000000,2000000000,2000000000]) := by decide

theorem origin_bound_is_essential :
    Int32 (0 : Int) ∧ ¬ Difference33 ((0 : Int) - 6000000000) := by decide

#print axioms cumulative_source_shape
#print axioms final_translation_for_arbitrary_finite_positions
#print axioms sharp_positive_difference
#print axioms sharp_negative_difference
#print axioms final_bound_alone_does_not_bound_intermediate_translation
#print axioms origin_bound_is_essential
end IndependentBounds
