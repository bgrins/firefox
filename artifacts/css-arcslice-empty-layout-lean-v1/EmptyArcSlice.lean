import Std

namespace EmptyArcSlice

def alignUp (size alignment : Nat) : Nat :=
  ((size + alignment - 1) / alignment) * alignment

structure Shape where
  countOffset : Nat
  allocationSizeOffset : Option Nat
  headerOffset : Nat
  lengthOffset : Nat
  tailOffset : Nat
  alignment : Nat
  referentSize : Nat
  allocationSize : Nat
  deriving DecidableEq, Repr

def shape (trackAllocationSize : Bool) (tailAlignment : Nat) : Shape :=
  let headerAlignment := max 8 tailAlignment
  let headerTailOffset := alignUp 16 tailAlignment
  let headerSize := alignUp headerTailOffset headerAlignment
  let dataOffset := alignUp (if trackAllocationSize then 16 else 8) headerAlignment
  let innerSize := alignUp (dataOffset + headerSize) headerAlignment
  { countOffset := 0
    allocationSizeOffset := if trackAllocationSize then some 8 else none
    headerOffset := dataOffset
    lengthOffset := dataOffset + 8
    tailOffset := dataOffset + headerTailOffset
    alignment := headerAlignment
    referentSize := innerSize
    allocationSize := alignUp innerSize tailAlignment }

def singletonShape (trackAllocationSize : Bool) : Shape :=
  let dataOffset := if trackAllocationSize then 16 else 8
  { countOffset := 0
    allocationSizeOffset := if trackAllocationSize then some 8 else none
    headerOffset := dataOffset
    lengthOffset := dataOffset + 8
    tailOffset := dataOffset + 16
    alignment := 8
    referentSize := dataOffset + 16
    allocationSize := dataOffset + 16 }

theorem smallExponent {k : Nat} (h : 2 ^ k ≤ 8) :
    k = 0 ∨ k = 1 ∨ k = 2 ∨ k = 3 := by
  have bound : k ≤ 3 := by
    by_cases hn : k ≤ 3
    · exact hn
    · have hk : 4 ≤ k := by omega
      have hp : 16 ≤ 2 ^ k := Nat.pow_le_pow_right (by decide : 0 < 2) hk
      omega
  omega

theorem singletonCompatible (track : Bool) {k : Nat} (h : 2 ^ k ≤ 8) :
    shape track (2 ^ k) = singletonShape track := by
  rcases smallExponent h with rfl | rfl | rfl | rfl <;> cases track <;> decide

theorem singletonIsSource (track : Bool) :
    shape track 8 = singletonShape track := by
  cases track <;> decide

theorem compatibleFieldsAndExtent (track : Bool) {k : Nat} (h : 2 ^ k ≤ 8) :
    shape track (2 ^ k) = shape track 8 := by
  rw [singletonCompatible track h, singletonIsSource track]

theorem baseAndTailAligned (track : Bool) {base k : Nat}
    (hbase : 8 ∣ base) (h : 2 ^ k ≤ 8) :
    2 ^ k ∣ base ∧ 2 ^ k ∣ base + (shape track (2 ^ k)).tailOffset := by
  rw [singletonCompatible track h]
  have hd : 2 ^ k ∣ 8 := by
    rcases smallExponent h with rfl | rfl | rfl | rfl <;> decide
  have hb := Nat.dvd_trans hd hbase
  refine ⟨hb, Nat.dvd_add hb ?_⟩
  rcases smallExponent h with rfl | rfl | rfl | rfl <;> cases track <;> decide

theorem highAlignmentChangesFieldsAndExtent (track : Bool) :
    (shape track 64).headerOffset = 64 ∧
    (shape track 64).lengthOffset = 72 ∧
    (shape track 64).tailOffset = 128 ∧
    (shape track 64).referentSize = 128 ∧
    (shape track 8).allocationSize < (shape track 64).referentSize := by
  cases track <;> decide

theorem alignedBaseDoesNotRepairSmallAllocation (track : Bool) :
    64 ∣ 4096 ∧
    ¬ ((shape track 64).referentSize ≤ (shape track 8).allocationSize) := by
  cases track <;> decide

#print axioms singletonCompatible
#print axioms compatibleFieldsAndExtent
#print axioms baseAndTailAligned
#print axioms highAlignmentChangesFieldsAndExtent
#print axioms alignedBaseDoesNotRepairSmallAllocation

end EmptyArcSlice
