import AliasGuard
open AliasGuard
example : eval false (.ref (.value none) (.ref (.value (some leaf)) (.value none))) = some leaf := by decide
