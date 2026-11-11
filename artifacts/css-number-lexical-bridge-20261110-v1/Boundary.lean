import Name
namespace Boundary
open HexPrefix Escape

 def marker (xs : List Byte) (n : Nat) : Prop :=
  n ≤ xs.length ∧ match xs[n]? with
    | none => True
    | some b => b.val < 128 ∨ 192 ≤ b.val

theorem name_return_marker (owned : Bool) (xs : List Byte) :
    marker xs (Name.run owned xs).count := by
  refine ⟨Name.consumed_bound owned xs, ?_⟩
  have h := Name.return_boundary owned xs
  rw [Name.exact_remainder] at h
  rw [← List.head?_drop]
  rcases h with h | ⟨b, bs, h, hb⟩
  · simp [h]
  · simp [h,hb]

structure Unit where
  first : Byte
  rest : List Byte
  headBoundary : first.val < 128 ∨ 192 ≤ first.val
  continuation : ∀ b ∈ rest, 128 ≤ b.val ∧ b.val < 192
  lengthWidth : 1 + rest.length = width first

def Unit.bytes (u : Unit) : List Byte := u.first :: u.rest

def bytes (units : List Unit) : List Byte := units.flatMap Unit.bytes

theorem unit_ascii_singleton (u : Unit) (h : u.first.val < 128) : u.rest = [] := by
  have hw := u.lengthWidth
  simp [width,h] at hw
  simpa using hw

theorem unit_nonempty (u : Unit) : u.bytes ≠ [] := by simp [Unit.bytes]

theorem complete_unit_marker (u : Unit) (tail : List Unit) :
    marker (bytes (u::tail)) u.bytes.length := by
  constructor
  · simp [bytes,Unit.bytes]
  · rw [← List.head?_drop]
    simp only [bytes,List.flatMap_cons,List.drop_left]
    cases tail with
    | nil => trivial
    | cons v vs =>
      simp only [List.flatMap_cons,Unit.bytes,List.cons_append,List.head?_cons]
      exact v.headBoundary

theorem ascii_step (units : List Unit) (b : Byte) (tail : List Byte)
    (h : bytes units = b :: tail) (hb : b.val < 128) :
    ∃ rest : List Unit, tail = bytes rest := by
  cases units with
  | nil => simp [bytes] at h
  | cons u us =>
    simp only [bytes,List.flatMap_cons,Unit.bytes,List.cons_append,List.cons.injEq] at h
    have hu : u.first.val < 128 := by simpa [h.1] using hb
    have hs := unit_ascii_singleton u hu
    refine ⟨us, ?_⟩
    simpa [hs,bytes] using h.2.symm

theorem ascii_prefix (units : List Unit) (pre tail : List Byte)
    (h : bytes units = pre ++ tail) (ha : ∀ b ∈ pre, b.val < 128) :
    ∃ rest : List Unit, tail = bytes rest := by
  induction pre generalizing units with
  | nil => exact ⟨units, by simpa using h.symm⟩
  | cons b bs ih =>
    obtain ⟨next, hn⟩ := ascii_step units b (bs ++ tail) h (ha b (by simp))
    exact ih next hn.symm (fun c hc => ha c (by simp [hc]))

theorem digit_ascii (b : Byte) (d : Nat) (h : nativeDigit b = some d) : b.val < 128 := by
  unfold nativeDigit at h
  split at h
  · omega
  · split at h
    · omega
    · split at h
      · omega
      · contradiction

theorem hex_suffix (fuel : Nat) (units : List Unit) (xs : List Byte) (initial : Nat)
    (h : bytes units = xs) :
    ∃ rest : List Unit, (HexPrefix.run fuel xs initial).rest = bytes rest := by
  induction fuel generalizing units xs initial with
  | zero => exact ⟨units, h.symm⟩
  | succ fuel ih =>
    cases xs with
    | nil => exact ⟨[], rfl⟩
    | cons b bs =>
      cases hd : nativeDigit b with
      | none => exact ⟨units, by simpa [HexPrefix.run,hd] using h.symm⟩
      | some d =>
        obtain ⟨next,hn⟩ := ascii_step units b bs h (digit_ascii b d hd)
        obtain ⟨last,hl⟩ := ih next bs (initial*16+d) hn.symm
        exact ⟨last, by simpa [HexPrefix.run,hd] using hl⟩

#print axioms ascii_prefix
#print axioms digit_ascii
#print axioms hex_suffix
#print axioms name_return_marker
#print axioms unit_ascii_singleton
#print axioms complete_unit_marker
#print axioms ascii_step
end Boundary
