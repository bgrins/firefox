import CssSemantics.Specificity

namespace CssSemantics

namespace CascadeKey

def Le : List Int → List Int → Prop
  | [], _ => True
  | _ :: _, [] => False
  | first :: rest, other :: tail => first < other ∨ first = other ∧ Le rest tail

def decLe : (left right : List Int) → Decidable (Le left right)
  | [], _ => isTrue trivial
  | _ :: _, [] => isFalse id
  | first :: rest, other :: tail =>
      letI := decLe rest tail
      inferInstanceAs (Decidable (first < other ∨ first = other ∧ Le rest tail))

instance (left right : List Int) : Decidable (Le left right) := decLe left right

theorem le_total (left right : List Int) : Le left right ∨ Le right left := by
  induction left generalizing right with
  | nil => exact Or.inl trivial
  | cons first rest ih =>
      cases right with
      | nil => exact Or.inr trivial
      | cons other tail =>
          by_cases hl : first < other
          · exact Or.inl (Or.inl hl)
          by_cases hr : other < first
          · exact Or.inr (Or.inl hr)
          have he : first = other := by omega
          rcases ih tail with h | h
          · exact Or.inl (Or.inr ⟨he, h⟩)
          · exact Or.inr (Or.inr ⟨he.symm, h⟩)

theorem le_refl (key : List Int) : Le key key := (le_total key key).elim id id

theorem le_trans {first second third : List Int}
    (h₁ : Le first second) (h₂ : Le second third) : Le first third := by
  induction first generalizing second third with
  | nil => trivial
  | cons a as ih =>
      cases second with
      | nil => exact False.elim h₁
      | cons b bs =>
          cases third with
          | nil => exact False.elim h₂
          | cons c cs =>
              rcases h₁ with hab | ⟨hab, hrest₁⟩
              · rcases h₂ with hbc | ⟨hbc, _⟩ <;> exact Or.inl (by omega)
              · rcases h₂ with hbc | ⟨hbc, hrest₂⟩
                · exact Or.inl (by omega)
                · exact Or.inr ⟨hab.trans hbc, ih hrest₁ hrest₂⟩

end CascadeKey

inductive CascadeOrigin where
  | userAgent | user | author
  deriving DecidableEq, Repr

def CascadeOrigin.band : CascadeOrigin → Bool → Int
  | .userAgent, false => 0
  | .user, false => 1
  | .author, false => 2
  | .author, true => 3
  | .user, true => 4
  | .userAgent, true => 5

structure CascadeEntry (Value : Type) where
  value : Value
  origin : CascadeOrigin := .author
  important : Bool := false
  attached : Bool := false
  layer : Option Nat := none
  specificity : Specificity := .zero
  sourceOrder : Nat := 0
  deriving DecidableEq, Repr

def CascadeEntry.key {Value : Type} (entry : CascadeEntry Value) : List Int :=
  let (layerKind, layerOrder) : Int × Int :=
    match entry.layer, entry.important with
    | none, false => (1, 0)
    | some rank, false => (0, rank)
    | none, true => (0, 0)
    | some rank, true => (1, -(rank : Int))
  [entry.origin.band entry.important, if entry.attached then 1 else 0,
    layerKind, layerOrder, entry.specificity.ids, entry.specificity.classes,
    entry.specificity.types, entry.sourceOrder]

def CascadeEntry.Le {Value : Type} (left right : CascadeEntry Value) : Prop :=
  CascadeKey.Le left.key right.key

instance {Value : Type} (left right : CascadeEntry Value) : Decidable (left.Le right) :=
  inferInstanceAs (Decidable (CascadeKey.Le _ _))

theorem CascadeEntry.le_total {Value : Type} (left right : CascadeEntry Value) :
    left.Le right ∨ right.Le left := CascadeKey.le_total _ _

theorem CascadeEntry.le_trans {Value : Type} {first second third : CascadeEntry Value}
    (h₁ : first.Le second) (h₂ : second.Le third) : first.Le third :=
  CascadeKey.le_trans h₁ h₂

def CascadeEntry.choose {Value : Type} (left right : CascadeEntry Value) : CascadeEntry Value :=
  if left.Le right then right else left

theorem CascadeEntry.choose_eq_or {Value : Type} (left right : CascadeEntry Value) :
    left.choose right = left ∨ left.choose right = right := by
  unfold choose
  split <;> simp

theorem CascadeEntry.le_choose_left {Value : Type} (left right : CascadeEntry Value) :
    left.Le (left.choose right) := by
  unfold choose
  split
  · assumption
  · exact CascadeKey.le_refl _

theorem CascadeEntry.le_choose_right {Value : Type} (left right : CascadeEntry Value) :
    right.Le (left.choose right) := by
  unfold choose
  split
  · exact CascadeKey.le_refl _
  · exact (le_total left right).resolve_left ‹¬ left.Le right›

def Cascade.winner {Value : Type} : List (CascadeEntry Value) → Option (CascadeEntry Value)
  | [] => none
  | first :: rest => some (match winner rest with
      | none => first
      | some other => first.choose other)

theorem Cascade.winner_none_iff {Value : Type} (entries : List (CascadeEntry Value)) :
    winner entries = none ↔ entries = [] := by
  cases entries <;> simp [winner]

theorem Cascade.winner_spec {Value : Type} (entries : List (CascadeEntry Value))
    (selected : CascadeEntry Value) (h : winner entries = some selected) :
    selected ∈ entries ∧ ∀ entry ∈ entries, entry.Le selected := by
  induction entries generalizing selected with
  | nil => simp [winner] at h
  | cons first rest ih =>
      cases hw : winner rest with
      | none =>
          have hr := (winner_none_iff rest).mp hw
          subst rest
          simp only [winner, Option.some.injEq] at h
          subst selected
          simp only [List.mem_cons, List.not_mem_nil, or_false]
          exact ⟨trivial, fun entry he => he ▸ CascadeKey.le_refl _⟩
      | some other =>
          have ⟨hm, hu⟩ := ih other hw
          simp only [winner, hw, Option.some.injEq] at h
          subst selected
          constructor
          · rcases first.choose_eq_or other with he | he
            · rw [he]
              exact List.mem_cons_self
            · rw [he]
              exact List.mem_cons_of_mem first hm
          · intro entry he
            rcases List.mem_cons.mp he with he | he
            · subst entry
              exact first.le_choose_left other
            · exact CascadeEntry.le_trans (hu entry he) (first.le_choose_right other)

namespace CascadeExamples

def rule (value : Nat) : CascadeEntry Nat := { value := value }

def cases : List (String × List (CascadeEntry Nat) × Option Nat) := [
  ("cascade empty", [], none),
  ("cascade importance before specificity", [
    { rule 1 with specificity := ⟨100, 0, 0⟩ }, { rule 2 with important := true }], some 2),
  ("cascade important user before author", [
    { rule 1 with important := true }, { rule 2 with origin := .user, important := true }], some 2),
  ("cascade normal author before user", [
    { rule 1 with origin := .user }, rule 2], some 2),
  ("cascade important UA before user", [
    { rule 1 with origin := .user, important := true },
    { rule 2 with origin := .userAgent, important := true }], some 2),
  ("cascade normal user before UA", [
    { rule 1 with origin := .userAgent }, { rule 2 with origin := .user }], some 2),
  ("cascade later normal layer", [
    { rule 1 with layer := some 1 }, { rule 2 with layer := some 2 }], some 2),
  ("cascade earlier important layer", [
    { rule 1 with layer := some 1, important := true },
    { rule 2 with layer := some 2, important := true }], some 1),
  ("cascade unlayered normal", [rule 1, { rule 2 with layer := some 1000000 }], some 1),
  ("cascade layered important", [
    { rule 1 with important := true },
    { rule 2 with layer := some 1000000, important := true }], some 2),
  ("cascade attached before specificity", [
    { rule 1 with attached := true }, { rule 2 with specificity := ⟨100, 0, 0⟩ }], some 1),
  ("cascade important before attached", [
    { rule 1 with attached := true }, { rule 2 with important := true }], some 2),
  ("cascade attached important before layer", [
    { rule 1 with attached := true, important := true },
    { rule 2 with important := true, layer := some 0 }], some 1),
  ("cascade layer before specificity", [
    { rule 1 with layer := some 1, specificity := ⟨100, 0, 0⟩ },
    { rule 2 with layer := some 2 }], some 2),
  ("cascade specificity before source order", [
    { rule 1 with specificity := ⟨1, 0, 0⟩ }, { rule 2 with sourceOrder := 100 }], some 1),
  ("cascade later source", [{ rule 1 with sourceOrder := 1 }, { rule 2 with sourceOrder := 2 }], some 2),
  ("cascade source survives enumeration reversal", [
    { rule 2 with sourceOrder := 2 }, { rule 1 with sourceOrder := 1 }], some 2)]

def checks : Bool := cases.all fun (_, entries, expected) =>
  ((Cascade.winner entries).map CascadeEntry.value) == expected

theorem checks_pass : checks = true := by decide

end CascadeExamples

end CssSemantics
