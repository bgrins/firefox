import CommentDirectives
namespace Mutation
open CommentDirectives CommentScan
def nativeSpace (b : Byte) : Bool := b == 32 || b == 9 || b == 13 || b == 10
def referenceSpace (b : Byte) : Bool := ([9,10,12,13,32] : List Byte).contains b
example : nativeSpace 12 ≠ CommentDirectives.nativeSpace 12 := by decide
end Mutation
