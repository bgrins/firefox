import FlexMBP.Compensated

namespace FlexMBP

theorem witness_target : WitnessTarget := by
  unfold WitnessTarget
  decide

theorem joint_witness_target : JointWitnessTarget := by
  refine ⟨⟨?_, by decide⟩, ⟨?_, by decide⟩, ?_⟩
  · simp [Acquired, maxCount, Fits32, min32, max32]
  · simp [Acquired, maxCount, Fits32, min32, max32]
  · apply compensated_case 60000 60000 2 <;> simp [Fits32, min32, max32, maxCount]

theorem old_four_rejected :
    oldFold id (List.replicate 4 (-600000000 : Int)) = none :=
  boundary_target.2.2.2

theorem wide_four_exact :
    wideFold id (List.replicate 4 (-600000000 : Int)) = some (-2400000000) := by
  simpa using boundary_coverage_target.2.2.2.2.1

theorem free_four_exact :
    freeSpace id (fun _ => 600000000) 60000 0
      (List.replicate 4 (-600000000 : Int)) = some 60000 :=
  boundary_coverage_target.2.2.2.2.2

theorem preceding_35791_exact :
    oldFold id (List.replicate 35791 (-60000 : Int)) = some (-2147460000) := by
  simpa using boundary_target.1.1 35791 (by omega)

theorem old_domain_success_false :
    ¬ (∀ items : List Int, Acquired id items → oldFold id items = some (sum id items)) := by
  intro h
  have he := h (List.replicate 4 (-600000000)) boundary_coverage_target.2.2.1
  rw [old_four_rejected] at he
  cases he

theorem extreme_negative_prefix :
    Fits64 (-2147483648 * (4294967295 : Int)) := by
  apply range_from_count 4294967295
  · decide
  · simp [min32]
  · simp [max32]

theorem extreme_positive_prefix :
    Fits64 (2147483647 * (4294967295 : Int)) := by
  apply range_from_count 4294967295
  · decide
  · simp [min32]
  · simp [max32]

end FlexMBP
