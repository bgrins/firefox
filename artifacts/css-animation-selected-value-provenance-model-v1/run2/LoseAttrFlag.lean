import SelectedValue
open AliasGuard SelectedValue
example : selected true (some parent) = some ⟨10, true, false⟩ := by decide
