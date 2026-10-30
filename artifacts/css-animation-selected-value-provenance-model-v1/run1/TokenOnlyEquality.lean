import SelectedValue
open AliasGuard SelectedValue
example : changed (some ⟨10, false, true⟩) (some ⟨10, true, true⟩) = false := by decide
