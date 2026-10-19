import IdentifierStart
import Boundary
namespace Caller
open HexPrefix Escape

theorem original_ident_progress (owned : Bool) (xs : List Byte)
    (h : IdentifierStart.native (xs.map Fin.val) = true) :
    0 < (Name.run owned xs).count := by
  cases xs with
  | nil => simp [IdentifierStart.native] at h
  | cons b bs =>
    by_cases ho : Name.ordinary b = true
    · exact Name.positive_ordinary owned b bs ho
    · have hf : Name.ordinary b = false := by simpa using ho
      by_cases hz : b.val = 0
      · exact Name.positive_nul owned b bs hz
      · have ha : IdentifierStart.nativeAscii b.val = false := by
          simp [IdentifierStart.nativeAscii]
          simp [Name.ordinary,Name.simple,Name.continuation,Name.fourIntro] at hf
          omega
        have h45 : b.val ≠ 45 := by
          intro he
          simp [Name.ordinary,Name.simple,he] at ho
        have hb := Name.nonordinary_ascii b hf
        by_cases h92 : b.val = 92
        · have hn : Name.newlineAfter bs = false := by
            cases bs with
            | nil => rfl
            | cons c cs =>
              simpa [IdentifierStart.native,ha,h45,h92,IdentifierStart.newlineAt,
                IdentifierStart.newline,IdentifierStart.nativeAscii,Name.newlineAfter] using h
          exact Name.positive_escape owned b bs h92 hn
        · simp [IdentifierStart.native,ha,h45,h92,hb] at h

theorem original_ident_boundary (owned : Bool) (xs : List Byte)
    (h : IdentifierStart.native (xs.map Fin.val) = true) :
    0 < (Name.run owned xs).count ∧ Boundary.marker xs (Name.run owned xs).count :=
  ⟨original_ident_progress owned xs h, Boundary.name_return_marker owned xs⟩

#print axioms original_ident_progress
#print axioms original_ident_boundary
end Caller
