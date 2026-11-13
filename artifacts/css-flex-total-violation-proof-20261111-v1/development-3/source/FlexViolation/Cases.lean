import FlexViolation.Target

namespace FlexViolation

theorem positive_acquired : Acquired positiveWitness := by
  simp [Acquired, positiveWitness, ValidItem, Fits32, min32, max32, maxCount]

theorem subtraction_acquired : Acquired subtractionWitness := by
  simp [Acquired, subtractionWitness, ValidItem, Fits32, min32, max32, maxCount]

theorem positive_total : total positiveWitness = 2400000000 := by decide

theorem positive_selected : (frozen positiveWitness).map Item.identity = [1, 2, 3, 4] := by decide

theorem wrapped_positive_empty :
    positiveWitness.filter (selected (kind (wrap32 (total positiveWitness)))) = [] := by decide

theorem subtraction_total : total subtractionWitness = max32 := by decide

theorem subtraction_old_refuses : oldFold subtractionWitness = none := by decide

theorem subtraction_wide_succeeds : wideFold subtractionWitness = some max32 := by decide

theorem witness_target : WitnessTarget := by
  exact ⟨positive_acquired, positive_total, by decide, positive_selected,
    by decide, wrapped_positive_empty, subtraction_acquired, subtraction_total,
    subtraction_old_refuses, subtraction_wide_succeeds⟩

theorem empty_joint : Acquired [] ∧ oldFold [] = some 0 ∧ wideFold [] = some 0 ∧ frozen [] = [] := by
  constructor
  · simp [Acquired, maxCount]
  · decide

theorem negative_joint :
    Acquired [{identity := 3, before := 10, minimum := 0, maximum := 4}] ∧
    wideFold [{identity := 3, before := 10, minimum := 0, maximum := 4}] = some (-6) ∧
    (frozen [{identity := 3, before := 10, minimum := 0, maximum := 4}]).map Item.identity = [3] := by
  constructor
  · simp [Acquired, ValidItem, Fits32, min32, max32, maxCount]
  · decide

theorem mixed_zero_joint :
    Acquired [{identity := 3, before := 10, minimum := 0, maximum := 4},
      {identity := 3, before := 0, minimum := 6, maximum := 8}] ∧
    wideFold [{identity := 3, before := 10, minimum := 0, maximum := 4},
      {identity := 3, before := 0, minimum := 6, maximum := 8}] = some 0 ∧
    (frozen [{identity := 3, before := 10, minimum := 0, maximum := 4},
      {identity := 3, before := 0, minimum := 6, maximum := 8}]).map Item.identity = [3,3] := by
  constructor
  · simp [Acquired, ValidItem, Fits32, min32, max32, maxCount]
  · decide

end FlexViolation
