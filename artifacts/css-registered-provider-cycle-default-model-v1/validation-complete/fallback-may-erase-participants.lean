import Defaults
open ProviderDefaults
open AttributeGuard (Key)
example : (publish 3 (.property 0) (fallback ⟨.missing, { poisoned := [.property 0] }⟩ (fun _ => ⟨.value 11, {}⟩))).outcome = .value 3 := by
  decide +kernel
