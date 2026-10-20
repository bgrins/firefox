import StickyAxis
namespace StickyWritingMode
inductive Mode where
  | horizontal | verticalRl | verticalLr | sidewaysRl | sidewaysLr
  deriving Repr, DecidableEq
inductive Orientation where
  | mixed | upright | sideways
  deriving Repr, DecidableEq
inductive Side where
  | top | right | bottom | left
  deriving Repr, DecidableEq
inductive Logical where
  | blockStart | blockEnd | inlineStart | inlineEnd
  deriving Repr, DecidableEq
inductive Axis where
  | x | y
  deriving Repr, DecidableEq

def opposite : Side → Side
  | .top => .bottom | .bottom => .top | .left => .right | .right => .left

def vertical : Mode → Bool
  | .horizontal => false | _ => true

def effectiveRtl (m : Mode) (rtl : Bool) (o : Orientation) : Bool :=
  match m, o with
  | .verticalRl, .upright | .verticalLr, .upright => false
  | _, _ => rtl

def referenceBlockEnd : Mode → Side
  | .horizontal => .bottom
  | .verticalRl | .sidewaysRl => .left
  | .verticalLr | .sidewaysLr => .right

def referenceInlineEnd (m : Mode) (rtl : Bool) (o : Orientation) : Side :=
  let direction := effectiveRtl m rtl o
  match m with
  | .horizontal => if direction then .left else .right
  | .sidewaysLr => if direction then .top else .bottom
  | _ => if direction then .top else .bottom

def referenceSide (m : Mode) (rtl : Bool) (o : Orientation) : Logical → Side
  | .blockStart => opposite (referenceBlockEnd m)
  | .blockEnd => referenceBlockEnd m
  | .inlineStart => opposite (referenceInlineEnd m rtl o)
  | .inlineEnd => referenceInlineEnd m rtl o

def flags (m : Mode) (rtl : Bool) (o : Orientation) : Nat :=
  let base := if rtl then 16 else 0
  let wm := match m with
    | .horizontal => 0 | .verticalRl => 1 | .verticalLr => 13
    | .sidewaysRl => 33 | .sidewaysLr => 37
  let reversed := match m with | .sidewaysLr => !rtl | _ => rtl
  let raw := base + wm + (if reversed then 2 else 0)
  match m, o with
  | .verticalRl, .upright | .verticalLr, .upright =>
      raw + 128 - (if rtl then 18 else 0)
  | .verticalRl, .sideways | .verticalLr, .sideways => raw + 64
  | _, _ => raw

def blockTable : List Side := [.top,.bottom,.right,.left,.bottom,.top,.left,.right]
def inlineTable : List Side :=
  [.left,.right, .top,.bottom, .right,.left, .bottom,.top,
   .right,.left, .top,.bottom, .left,.right, .bottom,.top,
   .left,.right, .top,.bottom, .right,.left, .bottom,.top,
   .left,.right, .top,.bottom, .right,.left, .bottom,.top]

def nativeVertical (raw : Nat) : Bool := raw % 2 == 1

def nativeSide (raw : Nat) (side : Logical) : Side :=
  match side with
  | .blockStart => blockTable[(raw % 2 + (raw / 4 % 2) * 2) * 2]?.getD .top
  | .blockEnd => blockTable[(raw % 2 + (raw / 4 % 2) * 2) * 2 + 1]?.getD .top
  | .inlineStart => inlineTable[(raw % 16) * 2]?.getD .top
  | .inlineEnd => inlineTable[(raw % 16) * 2 + 1]?.getD .top

theorem css_provider_refines (m : Mode) (rtl : Bool) (o : Orientation) (s : Logical) :
    nativeSide (flags m rtl o) s = referenceSide m rtl o s := by
  cases m <;> cases rtl <;> cases o <;> cases s <;> decide +kernel

theorem css_vertical_refines (m : Mode) (rtl : Bool) (o : Orientation) :
    nativeVertical (flags m rtl o) = vertical m := by
  cases m <;> cases rtl <;> cases o <;> decide +kernel

theorem all_encoding_opposite (raw : Fin 256) :
    opposite (nativeSide raw .blockStart) = nativeSide raw .blockEnd ∧
    opposite (nativeSide raw .inlineStart) = nativeSide raw .inlineEnd := by
  revert raw
  decide +kernel

def selectedEnd (raw : Nat) (axis : Axis) : Side :=
  match axis with
  | .x => nativeSide raw (if nativeVertical raw then .blockEnd else .inlineEnd)
  | .y => nativeSide raw (if nativeVertical raw then .inlineEnd else .blockEnd)

def referenceEnd (m : Mode) (rtl : Bool) (o : Orientation) (axis : Axis) : Side :=
  match m, axis with
  | .horizontal, .x => referenceInlineEnd m rtl o
  | .horizontal, .y => referenceBlockEnd m
  | _, .x => referenceBlockEnd m
  | _, .y => referenceInlineEnd m rtl o

theorem end_selection_refines (m : Mode) (rtl : Bool) (o : Orientation) (axis : Axis) :
    selectedEnd (flags m rtl o) axis = referenceEnd m rtl o axis := by
  cases m <;> cases rtl <;> cases o <;> cases axis <;> decide +kernel

def isFar : Side → Bool
  | .right | .bottom => true
  | _ => false

def normalizeWithContainingMode (cb child : Nat) (i : StickyAxis.Insets)
    (port box : Int) (axis : Axis) : StickyAxis.Edges :=
  StickyAxis.nativeNormalize i port box (isFar (selectedEnd cb axis))

theorem child_mode_independent (cb child otherChild : Nat) (i : StickyAxis.Insets)
    (port box : Int) (axis : Axis) :
    normalizeWithContainingMode cb child i port box axis =
      normalizeWithContainingMode cb otherChild i port box axis := rfl

theorem composed_normalization_refines (m : Mode) (rtl : Bool) (o : Orientation)
    (child : Nat) (i : StickyAxis.Insets) (port box : Int) (axis : Axis) :
    normalizeWithContainingMode (flags m rtl o) child i port box axis =
      StickyAxis.referenceNormalize i port box (isFar (referenceEnd m rtl o axis)) := by
  unfold normalizeWithContainingMode
  rw [end_selection_refines, StickyAxis.normalization_refines]

theorem orthogonal_auto_case :
    normalizeWithContainingMode (flags .verticalRl false .mixed)
      (flags .horizontal false .mixed) ⟨some 20,none⟩ 100 200 .x = ⟨-100,0⟩ := by
  decide +kernel

theorem upright_changes_rtl_inline_end :
    referenceEnd .verticalRl true .mixed .y = .top ∧
    referenceEnd .verticalRl true .upright .y = .bottom := by decide +kernel
end StickyWritingMode
