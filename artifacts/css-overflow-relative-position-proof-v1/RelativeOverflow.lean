import Lean

namespace RelativeOverflow

structure Point where
  inlinePos : Int
  blockPos : Int
  deriving DecidableEq, Repr

def add (p o : Point) : Point := ⟨p.inlinePos + o.inlinePos, p.blockPos + o.blockPos⟩

structure Placed where
  normal : Point
  used : Point
  deriving DecidableEq, Repr

def repaired (previous : Placed) (offset : Point) : Placed :=
  let normal := Point.mk previous.normal.inlinePos 0
  ⟨normal, add normal offset⟩

def oldPlacement (previous : Placed) : Point := ⟨previous.used.inlinePos, 0⟩

def flagOnly (previous : Placed) (offset : Point) : Point :=
  add (oldPlacement previous) offset

def update (frame : Placed) (offset : Point) : Placed :=
  ⟨frame.normal, add frame.normal offset⟩

theorem stores_normal (previous : Placed) (offset : Point) :
    (repaired previous offset).normal = ⟨previous.normal.inlinePos, 0⟩ := rfl

theorem applies_each_offset (previous : Placed) (offset : Point) :
    (repaired previous offset).used =
      ⟨previous.normal.inlinePos + offset.inlinePos, offset.blockPos⟩ := by
  simp [repaired, add]

theorem update_matches_initial (previous : Placed) (initial next : Point) :
    update (repaired previous initial) next = repaired previous next := rfl

theorem return_zero (previous : Placed) (offset : Point) :
    (update (repaired previous offset) ⟨0, 0⟩).used =
      ⟨previous.normal.inlinePos, 0⟩ := by simp [update, repaired, add]

theorem same_inline_preserved (previous : Placed) (offset : Point)
    (h : previous.used.inlinePos = previous.normal.inlinePos + offset.inlinePos) :
    (repaired previous offset).used.inlinePos = (oldPlacement previous).inlinePos := by
  simpa [repaired, add, oldPlacement] using h.symm

theorem flag_only_doubles (normal offset : Int) :
    (flagOnly ⟨⟨normal, 0⟩, ⟨normal + offset, 0⟩⟩ ⟨offset, 0⟩).inlinePos =
      normal + 2 * offset := by simp [flagOnly, oldPlacement, add]; omega

def fromPhysical (reversed : Bool) (container size position : Int) : Int :=
  if reversed then container - size - position else position

def toPhysical (reversed : Bool) (container size logical : Int) : Int :=
  if reversed then container - size - logical else logical

theorem conversion_roundtrip (r : Bool) (c s p : Int) :
    toPhysical r c s (fromPhysical r c s p) = p := by
  cases r <;> simp [toPhysical, fromPhysical] <;> omega

theorem unequal_size_transfer (c previousSize size normal : Int) :
    toPhysical true c size (fromPhysical true c previousSize normal) =
      normal + previousSize - size := by simp [toPhysical, fromPhysical]; omega

theorem apply_physical_offset_roundtrip (r : Bool) (c s n delta : Int) :
    toPhysical r c s (fromPhysical r c s (toPhysical r c s n + delta)) =
      toPhysical r c s n + delta := conversion_roundtrip r c s _

def s32 (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647

theorem small_executed_bounds (c sp sc normal delta : Int)
    (hc : 0 ≤ c ∧ c ≤ 1000000) (hp : 0 ≤ sp ∧ sp ≤ 1000000)
    (hs : 0 ≤ sc ∧ sc ≤ 1000000) (hn : -1000000 ≤ normal ∧ normal ≤ 1000000)
    (hd : -1000000 ≤ delta ∧ delta ≤ 1000000) :
    s32 (c-sp) ∧ s32 (c-sc) ∧ s32 (c-sp-normal) ∧
    s32 (c-sc-(c-sp-normal)) ∧ s32 (c-sc-(c-sp-normal)+delta) ∧
    s32 (c-sc-(c-sc-(c-sp-normal)+delta)) := by
  simp only [s32]; omega

theorem old_block_counterexample :
    oldPlacement ⟨⟨0, 0⟩, ⟨0, 17⟩⟩ ≠ (repaired ⟨⟨0, 0⟩, ⟨0, 17⟩⟩ ⟨0, 17⟩).used := by decide

theorem missing_property_update_counterexample :
    add ⟨17, 0⟩ ⟨34, 0⟩ ≠ add ⟨0, 0⟩ ⟨34, 0⟩ := by decide

#print axioms stores_normal
#print axioms applies_each_offset
#print axioms update_matches_initial
#print axioms return_zero
#print axioms same_inline_preserved
#print axioms flag_only_doubles
#print axioms conversion_roundtrip
#print axioms unequal_size_transfer
#print axioms apply_physical_offset_roundtrip
#print axioms small_executed_bounds
#print axioms old_block_counterexample
#print axioms missing_property_update_counterexample

end RelativeOverflow
