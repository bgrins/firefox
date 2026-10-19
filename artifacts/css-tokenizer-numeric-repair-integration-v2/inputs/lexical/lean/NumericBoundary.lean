import NumericToken
namespace NumericBoundary
open NumericDigits NumericEntry

theorem zero_marker (units : List Boundary.Unit) : Boundary.marker (Boundary.bytes units) 0 := by
  constructor
  · omega
  · cases units with
    | nil => trivial
    | cons u us => exact u.headBoundary

theorem lift_marker (pre xs : List Byte) (n : Nat) (h : Boundary.marker xs n) :
    Boundary.marker (pre ++ xs) (pre.length+n) := by
  constructor
  · simp only [List.length_append]; exact Nat.add_le_add_left h.1 _
  · rw [← List.head?_drop]
    have hs : (pre ++ xs).drop (pre.length+n) = xs.drop n := by
      rw [← List.drop_drop,List.drop_left]
    rw [hs,List.head?_drop]
    exact h.2

theorem lexical_suffix (units : List Boundary.Unit) (xs : List Byte)
    (h : Boundary.bytes units = xs) :
    ∃ rest : List Boundary.Unit, (NumericLexical.native xs).rest = Boundary.bytes rest := by
  apply Boundary.ascii_prefix units (NumericLexical.native xs).text
  · rw [h, NumericLexical.cover]
  · exact NumericLexical.consumed_ascii xs

theorem lexical_boundary (units : List Boundary.Unit) (xs : List Byte)
    (h : Boundary.bytes units = xs) :
    Boundary.marker xs (NumericLexical.native xs).text.length := by
  obtain ⟨rest,hr⟩ := lexical_suffix units xs h
  have hm := lift_marker (NumericLexical.native xs).text (NumericLexical.native xs).rest 0
    (hr ▸ zero_marker rest)
  simpa [NumericLexical.cover] using hm

theorem token_boundary (units : List Boundary.Unit) (xs : List Byte)
    (h : Boundary.bytes units = xs) : Boundary.marker xs (NumericToken.native xs).count := by
  have hc := NumericLexical.cover xs
  unfold NumericToken.native
  dsimp only
  split
  · rename_i hp
    obtain ⟨rest,hr⟩ := lexical_suffix units xs h
    cases he : (NumericLexical.native xs).rest with
    | nil => simp [he,NumericToken.percent] at hp
    | cons b bs =>
      have hb : b.val = 37 := by simpa [he,NumericToken.percent] using hp
      obtain ⟨last,hl⟩ := Boundary.ascii_step rest b bs (hr.symm.trans he) (by omega)
      have hm := lift_marker (NumericLexical.native xs).text (b::bs) 1 ?_
      · have hcov : (NumericLexical.native xs).text ++ b::bs = xs := by simpa only [he] using hc
        rw [hcov] at hm
        exact hm
      · constructor
        · simp
        · simpa [hl] using (zero_marker last).2
  · split
    · rename_i hi
      have hm := (Integration.repaired_ident_boundary false (NumericLexical.native xs).rest hi).2
      have ht := lift_marker (NumericLexical.native xs).text (NumericLexical.native xs).rest _ hm
      simpa [NumericLexical.cover] using ht
    · exact lexical_boundary units xs h

#print axioms zero_marker
#print axioms lift_marker
#print axioms lexical_suffix
#print axioms lexical_boundary
#print axioms token_boundary
end NumericBoundary
