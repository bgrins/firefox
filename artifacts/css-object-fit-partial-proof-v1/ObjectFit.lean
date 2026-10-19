import Std
set_option autoImplicit false

namespace ObjectFit

structure Size where
  width : Nat
  height : Nat
  deriving DecidableEq

inductive Fit where
  | fill | contain | cover | none | scaleDown
  deriving DecidableEq

def Within (a b : Size) : Prop := a.width ≤ b.width ∧ a.height ≤ b.height
instance (a b : Size) : Decidable (Within a b) :=
  inferInstanceAs (Decidable (a.width ≤ b.width ∧ a.height ≤ b.height))

def Partial (width height : Option Nat) : Prop := width = Option.none ∨ height = Option.none

instance (width height : Option Nat) : Decidable (Partial width height) :=
  inferInstanceAs (Decidable (width = Option.none ∨ height = Option.none))

def complete (constraint : Size) (width height : Option Nat) : Size :=
  ⟨width.getD constraint.width, height.getD constraint.height⟩

def minimum (a b : Size) : Size := ⟨min a.width b.width, min a.height b.height⟩

def smaller (a b : Size) : Size := if Within a b then a else b

def absentRatioSize (constraint : Size) (width height : Option Nat) : Fit → Size
  | .fill | .contain | .cover => constraint
  | .none => complete constraint width height
  | .scaleDown => minimum (complete constraint width height) constraint

theorem none_width (constraint : Size) (width : Nat) :
    absentRatioSize constraint (some width) Option.none .none = ⟨width, constraint.height⟩ := rfl

theorem none_height (constraint : Size) (height : Nat) :
    absentRatioSize constraint Option.none (some height) .none = ⟨constraint.width, height⟩ := rfl

theorem none_both (constraint : Size) (width height : Nat) :
    absentRatioSize constraint (some width) (some height) .none = ⟨width, height⟩ := rfl

theorem no_dimensions (constraint : Size) (fit : Fit) :
    absentRatioSize constraint Option.none Option.none fit = constraint := by
  cases constraint with
  | mk width height => cases fit <;> simp [absentRatioSize, complete, minimum]

theorem other_fits_constraint (constraint : Size) (width height : Option Nat) :
    absentRatioSize constraint width height .fill = constraint ∧
    absentRatioSize constraint width height .contain = constraint ∧
    absentRatioSize constraint width height .cover = constraint := ⟨rfl, rfl, rfl⟩

theorem partial_comparable (constraint : Size) (width height : Option Nat)
    (limited : Partial width height) :
    Within (complete constraint width height) constraint ∨
      Within constraint (complete constraint width height) := by
  rcases limited with hw | hh
  · subst width
    cases height with
    | none => exact Or.inl ⟨Nat.le_refl _, Nat.le_refl _⟩
    | some h =>
      rcases Nat.le_total h constraint.height with le | ge
      · exact Or.inl ⟨Nat.le_refl _, le⟩
      · exact Or.inr ⟨Nat.le_refl _, ge⟩
  · subst height
    cases width with
    | none => exact Or.inl ⟨Nat.le_refl _, Nat.le_refl _⟩
    | some w =>
      rcases Nat.le_total w constraint.width with le | ge
      · exact Or.inl ⟨le, Nat.le_refl _⟩
      · exact Or.inr ⟨ge, Nat.le_refl _⟩

theorem minimum_ordered (a b : Size) (comparable : Within a b ∨ Within b a) :
    minimum a b = smaller a b := by
  unfold smaller
  split
  · rename_i h
    cases a with
    | mk aw ah => cases b with
      | mk bw bh => simp [minimum, Nat.min_eq_left h.1, Nat.min_eq_left h.2]
  · rename_i h
    have reverse : Within b a := comparable.resolve_left h
    cases a with
    | mk aw ah => cases b with
      | mk bw bh => simp [minimum, Nat.min_eq_right reverse.1, Nat.min_eq_right reverse.2]

theorem scaledown_ordered_choice (constraint : Size) (width height : Option Nat)
    (limited : Partial width height) :
    absentRatioSize constraint width height .scaleDown =
      smaller (absentRatioSize constraint width height .none) constraint :=
  minimum_ordered _ _ (partial_comparable constraint width height limited)

theorem scaledown_is_candidate (constraint : Size) (width height : Option Nat)
    (limited : Partial width height) :
    absentRatioSize constraint width height .scaleDown = absentRatioSize constraint width height .none ∨
    absentRatioSize constraint width height .scaleDown = constraint := by
  rw [scaledown_ordered_choice constraint width height limited]
  unfold smaller
  split <;> simp_all

theorem scaledown_bounded (constraint : Size) (width height : Option Nat) :
    Within (absentRatioSize constraint width height .scaleDown) constraint ∧
    Within (absentRatioSize constraint width height .scaleDown) (complete constraint width height) := by
  exact ⟨⟨Nat.min_le_right _ _, Nat.min_le_right _ _⟩,
         ⟨Nat.min_le_left _ _, Nat.min_le_left _ _⟩⟩

theorem zero_width_distinct (constraint : Size) (positive : 0 < constraint.width) :
    absentRatioSize constraint (some 0) Option.none .none ≠
      absentRatioSize constraint Option.none Option.none .none := by
  intro equal
  have widths := congrArg Size.width equal
  simp [absentRatioSize, complete] at widths
  omega

theorem zero_height_distinct (constraint : Size) (positive : 0 < constraint.height) :
    absentRatioSize constraint Option.none (some 0) .none ≠
      absentRatioSize constraint Option.none Option.none .none := by
  intro equal
  have heights := congrArg Size.height equal
  simp [absentRatioSize, complete] at heights
  omega

def before {α : Type} (hasRatio : Bool) (fit : Fit) (constraint : α) (rest : Fit → α) : α :=
  if fit = .fill ∨ hasRatio = false then constraint else rest fit

def after {α : Type} (fit : Fit) (constraint : α) (rest : Fit → α) : α :=
  if fit = .fill then constraint else rest fit

theorem positive_ratio_preserved {α : Type} (fit : Fit) (constraint : α) (rest : Fit → α) :
    before true fit constraint rest = after fit constraint rest := by
  simp [before, after]

theorem fill_preserved {α : Type} (ratio : Bool) (constraint : α) (rest : Fit → α) :
    before ratio .fill constraint rest = after .fill constraint rest := by simp [before, after]

theorem incomparable_boundary :
    let constraint : Size := ⟨100, 100⟩
    let width : Option Nat := some 200
    let height : Option Nat := some 50
    ¬Partial width height ∧
    absentRatioSize constraint width height .scaleDown ≠ absentRatioSize constraint width height .none ∧
    absentRatioSize constraint width height .scaleDown ≠ constraint := by decide

#print axioms none_width
#print axioms none_height
#print axioms none_both
#print axioms no_dimensions
#print axioms other_fits_constraint
#print axioms partial_comparable
#print axioms minimum_ordered
#print axioms scaledown_ordered_choice
#print axioms scaledown_is_candidate
#print axioms scaledown_bounded
#print axioms zero_width_distinct
#print axioms zero_height_distinct
#print axioms positive_ratio_preserved
#print axioms fill_preserved
#print axioms incomparable_boundary
end ObjectFit
