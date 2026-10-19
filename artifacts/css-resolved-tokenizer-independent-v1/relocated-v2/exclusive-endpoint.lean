import Std

namespace ByteDispatch

abbrev Pattern := List (Nat × Nat)
abbrev Table := Nat → Option Nat

def covers (p : Pattern) (b : Nat) : Bool :=
  p.any fun (lo, hi) => decide (lo ≤ b ∧ b < hi)

def insert (t : Table) (id : Nat) (p : Pattern) : Table := fun b =>
  match t b with
  | some old => some old
  | none => if covers p b then some id else none

def build : List Pattern → Nat → Table → Table
  | [], _, t => t
  | p :: ps, id, t => build ps (id + 1) (insert t id p)

def first : List Pattern → Nat → Nat → Option Nat
  | [], _, _ => none
  | p :: ps, id, b => if covers p b then some id else first ps (id + 1) b

def prefer (a b : Option Nat) : Option Nat :=
  match a with | some n => some n | none => b

theorem table_refines_ordered_match (ps : List Pattern) (id : Nat) (t : Table) (b : Nat) :
    build ps id t b = prefer (t b) (first ps id b) := by
  induction ps generalizing id t with
  | nil => cases h : t b <;> simp [build, first, prefer, h]
  | cons p ps ih =>
    rw [build, ih]
    cases h : t b with
    | some n => simp [insert, prefer, h]
    | none => cases hc : covers p b <;> simp [insert, first, prefer, h, hc]

theorem fresh_table (ps : List Pattern) (b : Nat) :
    build ps 0 (fun _ => none) b = first ps 0 b := by
  simpa [prefer] using table_refines_ordered_match ps 0 (fun _ => none) b

theorem retained_entry (ps : List Pattern) (id : Nat) (t : Table) (b old : Nat)
    (h : t b = some old) : build ps id t b = some old := by
  simp [table_refines_ordered_match, prefer, h]

theorem selected_id_bound (ps : List Pattern) (id b chosen : Nat)
    (h : first ps id b = some chosen) : id ≤ chosen ∧ chosen < id + ps.length := by
  induction ps generalizing id with
  | nil => simp [first] at h
  | cons p ps ih =>
    simp only [first] at h
    split at h
    · cases h; simp
    · have z := ih (id + 1) h; simp only [List.length_cons]; omega

theorem selected_id_byte (ps : List Pattern) (b chosen : Nat)
    (len : ps.length ≤ 256) (h : first ps 0 b = some chosen) : chosen < 256 := by
  have := selected_id_bound ps 0 b chosen h
  omega

theorem inclusive_range (lo hi b : Nat) : covers [(lo, hi)] b = decide (lo ≤ b ∧ b ≤ hi) := by
  simp [covers]

def guardedExample (b : Nat) : Option Nat := if b = 97 ∧ False then some 0 else some 1
theorem guard_omission_counterexample : build [[(97,97)], [(0,255)]] 0 (fun _ => none) 97 ≠ guardedExample 97 := by decide
theorem exclusive_range_counterexample : build [[(97,99)], [(0,255)]] 0 (fun _ => none) 99 ≠ some 1 := by decide

#print axioms table_refines_ordered_match
#print axioms fresh_table
#print axioms retained_entry
#print axioms selected_id_bound
#print axioms selected_id_byte
#print axioms inclusive_range
#print axioms guard_omission_counterexample
#print axioms exclusive_range_counterexample
end ByteDispatch
