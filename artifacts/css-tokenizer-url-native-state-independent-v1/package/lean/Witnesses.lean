import SemanticName
import Caller
namespace Witnesses
open HexPrefix Escape

theorem temporary_interior :
    ([byte 195,byte 169,byte 32].takeWhile Name.simple).length = 1 ∧
    ¬ Boundary.marker [byte 195,byte 169,byte 32] 1 := by
  unfold Boundary.marker
  simp only [List.getElem?_cons_succ,List.getElem?_cons_zero]
  decide

theorem escaped_newline_zero_progress :
    Name.run false [byte 92,byte 10] = ⟨[],0,[byte 92,byte 10],true⟩ := by
  simp [Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,Name.newlineAfter,byte]
  decide

theorem hyphen_invalid_escape_partial :
    Name.run false [byte 45,byte 92,byte 10] = ⟨[byte 45],1,[byte 92,byte 10],true⟩ := by
  simp [Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,Name.newlineAfter,byte]
  decide

theorem nonascii_full_copy :
    Name.run false [byte 195,byte 169,byte 32] = ⟨[byte 195,byte 169],2,[byte 32],false⟩ := by
  simp [Name.run,Name.ordinary,Name.simple,Name.continuation,Name.fourIntro,Name.newlineAfter,byte]
  decide

theorem empty_name_zero_progress : Name.run false [] = ⟨[],0,[],false⟩ := by
  simp [Name.run]

#print axioms temporary_interior
#print axioms escaped_newline_zero_progress
#print axioms hyphen_invalid_escape_partial
#print axioms nonascii_full_copy
#print axioms empty_name_zero_progress
end Witnesses
