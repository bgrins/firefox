import SelectedValue
open AliasGuard SelectedValue
example : selected true none = some ⟨10, true, false⟩ := by decide
