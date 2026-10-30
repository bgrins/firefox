import AliasGuard

namespace SelectedValue
open AliasGuard

def mark (source : Bool) (value : Value) : Value :=
  { value with animationTainted := source || value.animationTainted }

def selected (source : Bool) (replacement : Option Value) : Option Value :=
  replacement.map (mark source)

theorem selected_valid_preserves_payload (source : Bool) (v : Value) :
    (mark source v).token = v.token ∧
    (mark source v).attrTainted = v.attrTainted := by
  exact ⟨rfl, rfl⟩

theorem selected_absent_stays_absent (source : Bool) :
    selected source none = none := by rfl

theorem selected_taint_is_infectious (source : Bool) (v : Value) :
    (mark source v).animationTainted = true ↔
      source = true ∨ v.animationTainted = true := by
  cases source <;> cases v.animationTainted <;> simp [mark]

theorem repeated_selection_accumulates (a b : Bool) (v : Value) :
    mark a (mark b v) = mark (a || b) v := by
  cases a <;> cases b <;> rfl

theorem csswide_selection_rejects_at_sink (v : Value) (fallback : Expr) :
    eval false (.ref (.value (selected true (some v))) fallback) =
      eval false fallback := by
  simp [eval, selected, mark, allowed]

theorem csswide_selection_survives_alias (n : Nat) (v : Value)
    (inner outer : Expr) :
    eval false (.ref (chain n (mark true v) inner) outer) = eval false outer ∧
    eval true (chain n (mark true v) inner) = some (mark true v) := by
  simp [eval, chain_resolves_in_custom_context, allowed, mark]

def changed (old fresh : Option Value) : Bool := decide (old ≠ fresh)

def publish (old fresh : Option Value) : Option Value :=
  if changed old fresh then fresh else old

theorem publication_matches_fresh (old fresh : Option Value) :
    publish old fresh = fresh := by
  by_cases h : old = fresh
  · simp [publish, changed, h]
  · simp [publish, changed, h]

theorem silent_publication_preserves_semantics (old fresh : Option Value)
    (silent : changed old fresh = false) : old = fresh := by
  simpa [changed] using silent

theorem same_token_taint_change_notifies (token : Nat) (attr : Bool) :
    changed (some ⟨token, false, attr⟩) (some ⟨token, true, attr⟩) = true := by
  simp [changed]

def tokens (v : Option Value) : Option Nat := v.map Value.token

theorem token_comparison_misses_required_notification (token : Nat) (attr : Bool) :
    tokens (some ⟨token, false, attr⟩) = tokens (some ⟨token, true, attr⟩) ∧
    changed (some ⟨token, false, attr⟩) (some ⟨token, true, attr⟩) = true := by
  exact ⟨rfl, same_token_taint_change_notifies token attr⟩

theorem attr_only_change_still_notifies (token : Nat) (taint : Bool) :
    changed (some ⟨token, taint, false⟩) (some ⟨token, taint, true⟩) = true := by
  simp [changed]

def parent : Value := ⟨10, false, true⟩
def cleanFallback : Expr := .value (some ⟨30, false, false⟩)

theorem concrete_selected_and_outer_fallback_controls :
    selected true (some parent) = some ⟨10, true, true⟩ ∧
    eval false (.ref (.value (selected true (some parent))) cleanFallback) =
      some ⟨30, false, false⟩ ∧
    eval false (.ref (.value none)
      (.ref (.value (selected true (some parent))) (.value none))) = none := by
  decide

end SelectedValue
