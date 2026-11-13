import FlexViolation.Selection
import FlexViolation.Cases

namespace FlexViolation

theorem universal_target : UniversalTarget :=
  ⟨prefix_target, difference_target, fold_target, selection_target,
    progress_target, compatibility_target, witness_target⟩

end FlexViolation
