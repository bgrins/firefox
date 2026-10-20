import PropertyPhase

namespace Destruction.Ownership

abbrev Capacity := Address → Nat

def ArrayShape (capacity : Capacity) (buffer : Option Address) (length : Nat) : Prop :=
  match buffer with
  | none => length = 0
  | some address => length ≤ capacity address

def PropertyShape (capacity : Capacity) : Property → Prop
  | .itemCache _ => True
  | .fragment _ => True
  | .shared _ buffer lines =>
      ArrayShape capacity buffer lines.length ∧
        ∀ line ∈ lines, ArrayShape capacity line.buffer line.frames.length
  | .foreign _ => False

def TableShape (capacity : Capacity) (table : PropertyTable) : Prop :=
  ArrayShape capacity table.buffer table.entries.length ∧
    ∀ p ∈ table.entries, PropertyShape capacity p

def Represented (h : Heap) (capacity : Capacity) (table : PropertyTable) : Prop :=
  TableShape capacity table ∧ ∃ releases,
    tablePlan table = some releases ∧
    (releases.map Release.address).Nodup ∧ Allocated h releases

def AllRepresented (h : Heap) (capacity : Capacity) : Prop :=
  ∀ owner content bit table, h owner = some (.frame content bit table) →
    Represented h capacity table

def SeparatePlans (a b : List Release) : Prop :=
  ∀ x ∈ a, ∀ y ∈ b, x.address ≠ y.address

def OwnersSeparated (h : Heap) : Prop :=
  ∀ first second c d b e p q xs ys,
    h first = some (.frame c b p) → h second = some (.frame d e q) →
    first ≠ second → tablePlan p = some xs → tablePlan q = some ys →
    SeparatePlans xs ys

structure World (h : Heap) (capacity : Capacity) : Prop where
  represented : AllRepresented h capacity
  separated : OwnersSeparated h

theorem empty_shape (capacity : Capacity) : TableShape capacity emptyTable := by
  simp [TableShape, ArrayShape, emptyTable]

theorem represented_empty (h : Heap) (capacity : Capacity) :
    Represented h capacity emptyTable := by
  refine ⟨empty_shape capacity, [], ?_, ?_, ?_⟩
  · rfl
  · simp
  · intro x member; simp at member

theorem absent_nonempty_rejected (capacity : Capacity) (length : Nat)
    (nonempty : length ≠ 0) : ¬ ArrayShape capacity none length := by
  exact nonempty

theorem allocated_empty_admitted (capacity : Capacity) (address : Address) :
    ArrayShape capacity (some address) 0 := Nat.zero_le _

theorem over_capacity_rejected (capacity : Capacity) (address length : Nat)
    (over : capacity address < length) :
    ¬ ArrayShape capacity (some address) length := Nat.not_le.mpr over

theorem separate_symm (a b : List Release) (separate : SeparatePlans a b) :
    SeparatePlans b a := by
  intro x memberX y memberY
  exact Ne.symm (separate y memberY x memberX)

theorem separate_no_address (a b : List Release) (separate : SeparatePlans a b)
    (x : Release) (member : x ∈ b) : x.address ∉ a.map Release.address := by
  intro present
  obtain ⟨y, memberY, same⟩ := List.mem_map.mp present
  exact separate y memberY x member same

theorem cross_role_alias_rejected (a b : Address) (roleA roleB : Role)
    (same : a = b) : ¬ SeparatePlans [⟨a, roleA⟩] [⟨b, roleB⟩] := by
  intro separated
  exact separated ⟨a, roleA⟩ (by simp) ⟨b, roleB⟩ (by simp) same

theorem item_reference_renaming_preserves_shape (capacity : Capacity)
    (root : Address) (buffer : Option Address) (lines : List LinePayload)
    (rename : Address → Address) :
    PropertyShape capacity
      (.shared root buffer (lines.map fun line =>
        { line with frames := line.frames.map rename })) ↔
      PropertyShape capacity (.shared root buffer lines) := by
  simp [PropertyShape]

end Destruction.Ownership
