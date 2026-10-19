import Std

namespace HyphenDictionary

def utf16Width (point : Nat) : Nat := if point < 0x10000 then 1 else 2

def utf8Width (point : Nat) : Nat :=
  if point < 0x80 then 1 else if point < 0x800 then 2 else if point < 0x10000 then 3 else 4

structure Boundary where
  byteLast : Nat
  unitLast : Nat
  point : Nat
  unitStart : Nat
  deriving DecidableEq, Repr

def boundaries : List Nat → Nat → Nat → List Boundary
  | [], _, _ => []
  | point :: rest, byteStart, unitStart =>
    ⟨byteStart + utf8Width point - 1, unitStart + utf16Width point - 1, point, unitStart⟩ ::
      boundaries rest (byteStart + utf8Width point) (unitStart + utf16Width point)

def utf16Length (points : List Nat) : Nat := (points.map utf16Width).sum

def utf8Length (points : List Nat) : Nat := (points.map utf8Width).sum

theorem positive_width16 (point : Nat) : 0 < utf16Width point := by
  unfold utf16Width; split <;> omega

theorem positive_width8 (point : Nat) : 0 < utf8Width point := by
  unfold utf8Width; split <;> (try split) <;> (try split) <;> omega

theorem mapped_boundary_is_scalar_end (points : List Nat) (bytes units : Nat)
    (boundary : Boundary) (h : boundary ∈ boundaries points bytes units) :
    boundary.unitLast + 1 = boundary.unitStart + utf16Width boundary.point := by
  induction points generalizing bytes units with
  | nil => simp [boundaries] at h
  | cons p rest ih =>
    simp only [boundaries, List.mem_cons] at h
    rcases h with h | h
    · subst boundary
      have := positive_width16 p
      simp only
      omega
    · exact ih _ _ h

theorem astral_break_after_pair (points : List Nat) (bytes units : Nat)
    (boundary : Boundary) (h : boundary ∈ boundaries points bytes units)
    (astral : 0x10000 ≤ boundary.point) :
    boundary.unitLast + 1 = boundary.unitStart + 2 := by
  have := mapped_boundary_is_scalar_end points bytes units boundary h
  simpa [utf16Width, show ¬boundary.point < 0x10000 by omega] using this

theorem mapped_unit_bound (points : List Nat) (bytes units : Nat)
    (boundary : Boundary) (h : boundary ∈ boundaries points bytes units) :
    boundary.unitLast < units + utf16Length points := by
  induction points generalizing bytes units with
  | nil => simp [boundaries] at h
  | cons p rest ih =>
    simp only [boundaries, List.mem_cons] at h
    rcases h with h | h
    · subst boundary
      have hw := positive_width16 p
      simp only [utf16Length, List.map_cons, List.sum_cons]
      omega
    · have hb := ih _ _ h
      simp only [utf16Length, List.map_cons, List.sum_cons] at *
      omega

theorem mapped_byte_bound (points : List Nat) (bytes units : Nat)
    (boundary : Boundary) (h : boundary ∈ boundaries points bytes units) :
    boundary.byteLast < bytes + utf8Length points := by
  induction points generalizing bytes units with
  | nil => simp [boundaries] at h
  | cons p rest ih =>
    simp only [boundaries, List.mem_cons] at h
    rcases h with h | h
    · subst boundary
      have hw := positive_width8 p
      simp only [utf8Length, List.map_cons, List.sum_cons]
      omega
    · have hb := ih _ _ h
      simp only [utf8Length, List.map_cons, List.sum_cons] at *
      omega

def mapMask (points : List Nat) (mask : Nat → Bool) : List Nat :=
  ((boundaries points 0 0).filter fun boundary => mask boundary.byteLast).map Boundary.unitLast

theorem mapped_mask_has_scalar_end (points : List Nat) (mask : Nat → Bool)
    (index : Nat) (h : index ∈ mapMask points mask) :
    ∃ boundary ∈ boundaries points 0 0,
      boundary.unitLast = index ∧ mask boundary.byteLast = true ∧
      index + 1 = boundary.unitStart + utf16Width boundary.point := by
  simp only [mapMask, List.mem_map, List.mem_filter] at h
  obtain ⟨b, ⟨hb, hm⟩, hi⟩ := h
  exact ⟨b, hb, hi, hm, by rw [← hi]; exact mapped_boundary_is_scalar_end points 0 0 b hb⟩

def casingAllowed (lower : Nat → Nat) (capitalize : Bool) : List Nat → Bool
  | [] => true
  | first :: rest => (lower first == first || capitalize) && rest.all (fun p => lower p == p)

theorem internal_caps_reject (lower : Nat → Nat) (capitalize : Bool)
    (first changed : Nat) (rest : List Nat) (member : changed ∈ rest)
    (h : lower changed ≠ changed) : casingAllowed lower capitalize (first :: rest) = false := by
  simp only [casingAllowed, Bool.and_eq_false_iff]
  right
  apply Bool.eq_false_iff.mpr
  intro hall
  have hc := List.all_eq_true.mp hall changed member
  exact h (by simpa using hc)

theorem lower_width_preserves_positions (lower : Nat → Nat) (points : List Nat)
    (h : ∀ p ∈ points, utf16Width (lower p) = utf16Width p) :
    utf16Length (points.map lower) = utf16Length points := by
  unfold utf16Length
  rw [List.map_map]
  congr 1
  apply List.map_congr_left
  exact h

#print axioms mapped_boundary_is_scalar_end
#print axioms astral_break_after_pair
#print axioms mapped_unit_bound
#print axioms mapped_byte_bound
#print axioms mapped_mask_has_scalar_end
#print axioms internal_caps_reject
#print axioms lower_width_preserves_positions
end HyphenDictionary
