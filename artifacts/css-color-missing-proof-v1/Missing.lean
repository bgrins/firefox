import Init

namespace MissingComponents

abbrev Space := Fin 15
abbrev Channel := Fin 3
abbrev Mask := Fin 8

inductive Category where
  | red | green | blue | lightness | colorfulness | hue | opponentA | opponentB
  | whiteness | blackness
  deriving DecidableEq, Repr

-- Space numbering follows the authenticated ColorSpace declaration.
def category (space : Space) (channel : Channel) : Category :=
  match space.val, channel.val with
  | 1, 0 => .hue
  | 1, 1 => .colorfulness
  | 1, _ => .lightness
  | 2, 0 => .hue
  | 2, 1 => .whiteness
  | 2, _ => .blackness
  | 3, 0 | 4, 0 | 5, 0 | 6, 0 => .lightness
  | 3, 1 | 5, 1 => .opponentA
  | 3, _ | 5, _ => .opponentB
  | 4, 1 | 6, 1 => .colorfulness
  | 4, _ | 6, _ => .hue
  | _, 0 => .red
  | _, 1 => .green
  | _, _ => .blue

def missing (mask : Mask) (channel : Channel) : Bool :=
  mask.val / 2 ^ channel.val % 2 == 1

def analogous (source target : Space) (i j : Channel) : Prop :=
  category source i = category target j

instance (source target : Space) (i j : Channel) :
    Decidable (analogous source target i j) := inferInstanceAs
      (Decidable (category source i = category target j))

def residual (source target : Space) (i : Channel) : Prop :=
  ∀ j : Channel, ¬ analogous source target i j

instance (source target : Space) (i : Channel) :
    Decidable (residual source target i) := inferInstanceAs
      (Decidable (∀ j : Channel, ¬ analogous source target i j))

def specifiedTransfer (source target : Space) (mask : Mask) (j : Channel) : Prop :=
  (∃ i : Channel, analogous source target i j ∧ missing mask i = true) ∨
  (residual target source j ∧
    ∀ i : Channel, residual source target i → missing mask i = true)

instance (source target : Space) (mask : Mask) (j : Channel) :
    Decidable (specifiedTransfer source target mask j) := inferInstanceAs
      (Decidable ((∃ i : Channel, analogous source target i j ∧ missing mask i = true) ∨
        (residual target source j ∧
          ∀ i : Channel, residual source target i → missing mask i = true)))

def rgbLike (space : Space) : Bool :=
  match space.val with
  | 0 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 => true
  | _ => false

def patchedCarry (sourceMask convertedMask : Mask) (channel : Channel) : Bool :=
  missing convertedMask channel || missing sourceMask channel

def oldCarry (_sourceMask convertedMask : Mask) (channel : Channel) : Bool :=
  missing convertedMask channel

set_option maxRecDepth 4000 in
set_option maxHeartbeats 2000000 in
theorem rgb_transfer : ∀ (source target : Space) (mask : Mask) (j : Channel),
    rgbLike source = true → rgbLike target = true →
    (specifiedTransfer source target mask j ↔ missing mask j = true) := by decide

theorem native_rgb_refinement (source target : Space) (mask converted : Mask)
    (j : Channel) (hs : rgbLike source = true) (ht : rgbLike target = true) :
    patchedCarry mask converted j =
      (missing converted j || decide (specifiedTransfer source target mask j)) := by
  have h := rgb_transfer source target mask j hs ht
  simp [patchedCarry, h]

theorem converted_flags_preserved (mask converted : Mask) (j : Channel)
    (h : missing converted j = true) : patchedCarry mask converted j = true := by
  simp [patchedCarry, h]

theorem no_spurious_rgb_mask (mask converted : Mask) (j : Channel)
    (h : missing mask j = false) (hc : missing converted j = false) :
    patchedCarry mask converted j = false := by simp [patchedCarry, h, hc]

theorem old_branch_counterexample :
    oldCarry 1 0 0 = false ∧ patchedCarry 1 0 0 = true := by decide

inductive Outcome where
  | mix | useLeft | useRight | missing
  deriving DecidableEq, Repr

def nativeOutcome (leftMissing rightMissing : Bool) : Outcome :=
  match leftMissing, rightMissing with
  | true, true => .missing
  | true, false => .useRight
  | false, true => .useLeft
  | false, false => .mix

def specifiedOperands {α : Type} (left right : Option α) : Option (α × α) :=
  match left, right with
  | none, none => none
  | none, some r => some (r, r)
  | some l, none => some (l, l)
  | some l, some r => some (l, r)

def nativeOperands {α : Type} (left right : Option α) : Option (α × α) :=
  match nativeOutcome left.isNone right.isNone with
  | .missing => none
  | .useLeft => left.map (fun l => (l, l))
  | .useRight => right.map (fun r => (r, r))
  | .mix => left.bind (fun l => right.map (fun r => (l, r)))

theorem operand_refinement {α : Type} (left right : Option α) :
    nativeOperands left right = specifiedOperands left right := by
  cases left <;> cases right <;> rfl

theorem missing_left_copies {α : Type} (right : α) :
    nativeOperands none (some right) = some (right, right) := by rfl

theorem transferred_channel_copies {α : Type} (source converted : Mask)
    (j : Channel) (left right : α) (h : missing source j = true) :
    nativeOperands (if patchedCarry source converted j then none else some left)
      (some right) = some (right, right) := by
  simp [patchedCarry, h, nativeOperands, nativeOutcome]

theorem both_missing_preserved {α : Type} :
    nativeOperands (α := α) none none = none := by rfl

theorem rgb_counterexample :
    specifiedTransfer 0 7 1 0 ∧ ¬ specifiedTransfer 0 7 1 1 := by decide

theorem residual_counterexample :
    specifiedTransfer 3 4 6 1 ∧ specifiedTransfer 3 4 6 2 := by decide

theorem partial_residual_not_carried :
    ¬ specifiedTransfer 3 4 2 1 ∧ ¬ specifiedTransfer 3 4 2 2 := by decide

#print axioms rgb_transfer
#print axioms native_rgb_refinement
#print axioms converted_flags_preserved
#print axioms no_spurious_rgb_mask
#print axioms old_branch_counterexample
#print axioms operand_refinement
#print axioms missing_left_copies
#print axioms transferred_channel_copies
#print axioms both_missing_preserved
#print axioms rgb_counterexample
#print axioms residual_counterexample
#print axioms partial_residual_not_carried
end MissingComponents
