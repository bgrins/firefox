import CommentObservers
namespace Mutation
open CommentObservers CommentScan
def nativeWidth (b : Byte) : Nat :=
  if 128 ≤ b.val ∧ b.val ≤ 191 then 0 else if 240 ≤ b.val then 1 else 1
example : nativeWidth 240 ≠ CommentObservers.nativeWidth 240 := by decide
end Mutation
