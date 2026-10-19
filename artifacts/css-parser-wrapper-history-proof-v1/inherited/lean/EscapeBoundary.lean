import Boundary
namespace EscapeBoundary
open HexPrefix Escape Boundary

theorem whitespace_ascii (xs : List Byte) :
    ∀ b ∈ xs.take (nativeWhitespace xs), b.val < 128 := by
  cases xs with
  | nil => simp
  | cons c cs =>
    simp only [nativeWhitespace]
    split
    · simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
      intro b hb
      subst b
      omega
    · split
      · split
        · rename_i h
          cases cs with
          | nil => simp at h
          | cons d ds =>
            simp only [List.head?_cons,Option.some.injEq] at h
            simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
            intro b hb
            rcases hb with rfl | rfl
            · omega
            · simp [h.2,byte]
              decide
        · simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
          intro b hb
          subst b
          omega
      · simp

theorem whitespace_suffix (units : List Boundary.Unit) (xs : List Byte) (h : bytes units = xs) :
    ∃ rest : List Boundary.Unit, xs.drop (nativeWhitespace xs) = bytes rest := by
  apply ascii_prefix units (xs.take (nativeWhitespace xs)) _
  · simpa using h
  · exact whitespace_ascii xs

theorem native_suffix (units : List Boundary.Unit) :
    ∃ rest : List Boundary.Unit, (bytes units).drop (Escape.native (bytes units)).count = bytes rest := by
  cases units with
  | nil => exact ⟨[], rfl⟩
  | cons u us =>
    cases hd : nativeDigit u.first with
    | some d =>
      obtain ⟨next,hn⟩ := hex_suffix 6 (u::us) (bytes (u::us)) 0 rfl
      obtain ⟨last,hl⟩ := whitespace_suffix next (HexPrefix.run 6 (bytes (u::us)) 0).rest hn.symm
      refine ⟨last, ?_⟩
      have he := HexPrefix.exact_remainder 6 (bytes (u::us)) 0
      simp only [bytes,List.flatMap_cons,Unit.bytes,List.cons_append,Escape.native,hd]
      simp only [bytes,List.flatMap_cons,Unit.bytes,List.cons_append] at he hl
      rw [← List.drop_drop, ← he]
      exact hl
    | none =>
      by_cases hz : u.first.val = 0
      · have hr := unit_ascii_singleton u (by omega)
        exact ⟨us, by simp [bytes,Unit.bytes,Escape.native,hd,hz,hr]⟩
      · have hw := u.lengthWidth.symm
        refine ⟨us, ?_⟩
        simp [bytes,Unit.bytes,Escape.native,hd,hz,List.length_take,hw]
        rw [Nat.add_comm 1]
        simp

#print axioms whitespace_ascii
#print axioms whitespace_suffix
#print axioms native_suffix
end EscapeBoundary
