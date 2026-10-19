import StringTransitions
namespace Mutation
open StringTransitions CommentScan
def nativeEscape (xs : List Byte) : Escape.Result :=
  if xs.isEmpty then ⟨Escape.encode 65533,0⟩
  else if nativeNewline xs then ⟨[],newlineCount xs⟩ else Escape.native xs
example : nativeEscape [] ≠ StringTransitions.nativeEscape [] := by decide
end Mutation
