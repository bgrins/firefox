import FlexViolationCaller.Selected
import FlexViolationCaller.Joint

namespace FlexViolationCaller

theorem universal_target : UniversalTarget :=
  ⟨initial_target, history_target, pass_target, selection_target,
    fallback_target, completion_target, delta_admission_target, joint_target⟩

end FlexViolationCaller
