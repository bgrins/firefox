import SelectedValue
open AliasGuard SelectedValue
example : eval false (.ref (.value (selected true (some parent))) cleanFallback) = some parent := by decide
