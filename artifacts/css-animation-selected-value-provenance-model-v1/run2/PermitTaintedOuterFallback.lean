import SelectedValue
open AliasGuard SelectedValue
example : eval false (.ref (.value none) (.ref (.value (selected true (some parent))) (.value none))) = selected true (some parent) := by decide
