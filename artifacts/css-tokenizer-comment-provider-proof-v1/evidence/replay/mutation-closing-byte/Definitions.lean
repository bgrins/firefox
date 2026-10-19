import CommentScan
namespace Mutation
open CommentScan CommentScan
def stop (b : Byte) (bs : List Byte) : Bool := b == 42 && bs.head? == some 42
example : stop 42 [47] ≠ CommentScan.stop 42 [47] := by decide
end Mutation
