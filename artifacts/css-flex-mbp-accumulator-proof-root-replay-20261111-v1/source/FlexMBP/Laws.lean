import FlexMBP.Cases

namespace FlexMBP

theorem universal_target : UniversalTarget :=
  ⟨prefix_target, accumulator_target, old_compatibility_target,
    free_space_target, boundary_target, witness_target,
    compensated_family_target, boundary_coverage_target, joint_witness_target⟩

end FlexMBP
