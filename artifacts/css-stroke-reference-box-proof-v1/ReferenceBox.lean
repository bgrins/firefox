import Std
set_option autoImplicit false

namespace ReferenceBox

inductive Box where
  | fill | content | stroke | view | border
  deriving DecidableEq

inductive Kind where
  | content | border
  deriving DecidableEq

inductive Uses : Box → Kind → Prop where
  | fill : Uses .fill .content
  | content : Uses .content .content
  | stroke : Uses .stroke .border
  | view : Uses .view .border
  | border : Uses .border .border

inductive Alias : Box → Box → Prop where
  | fillContent : Alias .fill .content
  | strokeBorder : Alias .stroke .border
  | viewBorder : Alias .view .border
  | refl (a : Box) : Alias a a
  | symm {a b : Box} : Alias a b → Alias b a
  | trans {a b c : Box} : Alias a b → Alias b c → Alias a c

def cssPayload {α : Type} (b : Box) (content border : α) : α :=
  if b = .fill ∨ b = .content then content else border

def kindPayload {α : Type} (k : Kind) (content border : α) : α :=
  match k with
  | .content => content
  | .border => border

theorem selector_contract {α : Type} (b : Box) (k : Kind) (content border : α)
    (h : Uses b k) : cssPayload b content border = kindPayload k content border := by
  cases h <;> simp [cssPayload, kindPayload]

theorem alias_invariance {α : Type} (content border : α) {a b : Box}
    (h : Alias a b) : cssPayload a content border = cssPayload b content border := by
  induction h with
  | fillContent => simp [cssPayload]
  | strokeBorder => simp [cssPayload]
  | viewBorder => simp [cssPayload]
  | refl => rfl
  | symm _ ih => exact ih.symm
  | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂

theorem stroke_border {α : Type} (content border : α) :
    cssPayload .stroke content border = border := by simp [cssPayload]

theorem view_border {α : Type} (content border : α) :
    cssPayload .view content border = border := by simp [cssPayload]

theorem fill_content {α : Type} (content border : α) :
    cssPayload .fill content border = content := by simp [cssPayload]

def normalize {α : Type} (needed : Bool) (unzoom : α → α) (value : α) : α :=
  if needed then unzoom value else value

theorem normalized_alias {α : Type} (needed : Bool) (unzoom : α → α)
    (content border : α) {a b : Box} (h : Alias a b) :
    normalize needed unzoom (cssPayload a content border) =
      normalize needed unzoom (cssPayload b content border) :=
  congrArg (normalize needed unzoom) (alias_invariance content border h)

def resolve {α : Type} (svg needed : Bool) (b : Box) (unzoom : α → α)
    (content border : α) (svgProvider : Box → α) : α :=
  normalize needed unzoom (if svg then svgProvider b else cssPayload b content border)

theorem svg_opaque {α : Type} (needed : Bool) (b : Box) (unzoom : α → α)
    (content border : α) (provider : Box → α) :
    resolve true needed b unzoom content border provider = normalize needed unzoom (provider b) := rfl

theorem css_dispatch {α : Type} (needed : Bool) (b : Box) (unzoom : α → α)
    (content border : α) (provider : Box → α) :
    resolve false needed b unzoom content border provider = normalize needed unzoom (cssPayload b content border) := rfl

theorem no_unzoom {α : Type} (unzoom : α → α) (value : α) :
    normalize false unzoom value = value := rfl

structure Cache (α : Type) where
  cached : Bool
  value : α
  deriving DecidableEq

def ensure {α : Type} (state : Cache α) (resolved : α) : Cache α :=
  if state.cached then state else ⟨true, resolved⟩

theorem ensure_miss {α : Type} (old resolved : α) :
    ensure ⟨false, old⟩ resolved = ⟨true, resolved⟩ := rfl

theorem ensure_hit {α : Type} (old resolved : α) :
    ensure ⟨true, old⟩ resolved = ⟨true, old⟩ := rfl

theorem ensure_idempotent {α : Type} (state : Cache α) (resolved : α) :
    ensure (ensure state resolved) resolved = ensure state resolved := by
  cases state with
  | mk cached value => cases cached <;> rfl

theorem cache_alias_initialization {α : Type} (needed : Bool) (unzoom : α → α)
    (content border old : α) (provider : Box → α) {a b : Box} (h : Alias a b) :
    ensure ⟨false, old⟩ (resolve false needed a unzoom content border provider) =
      ensure ⟨false, old⟩ (resolve false needed b unzoom content border provider) := by
  simp only [ensure_miss, css_dispatch]
  rw [normalized_alias needed unzoom content border h]

theorem initial_value_irrelevant {α : Type} (old₁ old₂ resolved : α) :
    ensure ⟨false, old₁⟩ resolved = ensure ⟨false, old₂⟩ resolved := rfl

#print axioms selector_contract
#print axioms alias_invariance
#print axioms stroke_border
#print axioms view_border
#print axioms fill_content
#print axioms normalized_alias
#print axioms svg_opaque
#print axioms css_dispatch
#print axioms no_unzoom
#print axioms ensure_miss
#print axioms ensure_hit
#print axioms ensure_idempotent
#print axioms cache_alias_initialization
#print axioms initial_value_irrelevant
end ReferenceBox
