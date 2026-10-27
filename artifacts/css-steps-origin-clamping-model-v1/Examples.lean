import Steps

open StepsOrigin

example : calculation 4 .nan = .calculation (some 1) := by decide +kernel
example : calculation 4 (.finite ⟨0, false⟩) = .calculation (some 1) := by decide +kernel
example : calculation 4 (.finite ⟨1, false⟩) = .calculation (some 1) := by decide +kernel
example : repaired .jumpNone (calculation 4 .nan) = some 2 := by decide +kernel
example : old .jumpNone (calculation 4 .nan) = none := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨-10, false⟩)) = some 2 := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨7 / 5, false⟩)) = some 2 := by decide +kernel
example : repaired .jumpNone (calculation 4 (.finite ⟨3 / 2, false⟩)) = some 2 := by decide +kernel
example : repaired .ordinary (calculation 4 .nan) = some 1 := by decide +kernel
example : repaired .jumpNone (.literal 1) = none := by decide +kernel
example : repaired .jumpNone (.calculation none) = none := by decide +kernel

#print axioms literal_unchanged
#print axioms unresolved_unchanged
#print axioms retained_success
#print axioms resolved_result_bounded
#print axioms normalized_bounded
#print axioms calculation_nan_equals_zero
#print axioms exact_old_loss
#print axioms ordinary_calculation_unchanged
#print axioms repaired_jump_none_at_one

#print axioms repaired_nan
