import CommentUTF8
set_option maxRecDepth 4096
set_option maxHeartbeats 3000000
namespace CommentCodepoints
open CommentScan CommentObservers CommentUTF8

def unitStep (r : RefState) (u : Boundary.Unit) : RefState :=
  if u.first.val < 128 then referenceStep r u.first
  else ⟨⟨r.state.offset+u.bytes.length,r.state.line,
          r.state.column+(if Escape.width u.first = 4 then 2 else 1)⟩,false⟩

theorem continuation_step (r : RefState) (b : Byte)
    (h : 128 ≤ b.val ∧ b.val < 192) :
    referenceStep r b = ⟨⟨r.state.offset+1,r.state.line,r.state.column⟩,false⟩ := by
  have hc : ∀ c : Byte, 128 ≤ c.val ∧ c.val < 192 →
      c ≠ 13 ∧ c ≠ 10 ∧ c ≠ 12 ∧ referenceWidth c = 0 := by decide
  obtain ⟨h13,h10,h12,hw⟩ := hc b h
  simp [referenceStep,h13,h10,h12,hw]

theorem continuation_fold (bs : List Byte) (r : RefState) (pending : r.afterCR = false)
    (h : ∀ b ∈ bs, 128 ≤ b.val ∧ b.val < 192) :
    bs.foldl referenceStep r =
      ⟨⟨r.state.offset+bs.length,r.state.line,r.state.column⟩,false⟩ := by
  induction bs generalizing r with
  | nil => cases r; simp_all
  | cons b bs ih =>
    rw [List.foldl_cons,continuation_step r b (h b (by simp))]
    rw [ih _ rfl (fun c hc => h c (by simp [hc]))]
    simp [Nat.add_assoc,Nat.add_comm]

theorem unit_observer (r : RefState) (u : Boundary.Unit) :
    u.bytes.foldl referenceStep r = unitStep r u := by
  by_cases ha : u.first.val < 128
  · have hr := Boundary.unit_ascii_singleton u ha
    simp [Boundary.Unit.bytes,hr,unitStep,ha]
  · have hh : 192 ≤ u.first.val := by rcases u.headBoundary with h | h <;> omega
    have classifier : ∀ b : Byte, 192 ≤ b.val →
        b ≠ 13 ∧ b ≠ 10 ∧ b ≠ 12 ∧ referenceWidth b = (if Escape.width b = 4 then 2 else 1) := by decide
    obtain ⟨h13,h10,h12,hw⟩ := classifier u.first hh
    have hs : referenceStep r u.first =
        ⟨⟨r.state.offset+1,r.state.line,r.state.column+referenceWidth u.first⟩,false⟩ := by
      simp [referenceStep,h13,h10,h12]
    change u.rest.foldl referenceStep (referenceStep r u.first) = unitStep r u
    rw [hs,continuation_fold _ _ rfl u.continuation]
    simp [unitStep,ha,hw,Boundary.Unit.bytes,Nat.add_assoc,Nat.add_comm]

theorem raw_units_observer (units : List Boundary.Unit) (r : RefState) :
    (bytes units).foldl referenceStep r = units.foldl unitStep r := by
  induction units generalizing r with
  | nil => rfl
  | cons u us ih =>
    change (u.bytes ++ bytes us).foldl referenceStep r = _
    rw [List.foldl_append,unit_observer,ih]
    rfl

theorem native_units_observer (units : List Boundary.Unit) (s : State) :
    nativeObserve (bytes units) s = (units.foldl unitStep ⟨s,false⟩).state := by
  rw [native_reference]
  unfold referenceObserve
  rw [raw_units_observer]
end CommentCodepoints
