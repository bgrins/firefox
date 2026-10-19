import CommentDirectives
namespace Mutation
open CommentDirectives CommentScan
def nativeUpdate (body : List Byte) (old : URLs) : URLs :=
  let m := nativeDirective nativeMapKey body
  let u := nativeDirective nativeSourceKey body
  ⟨m.or old.sourceMap,u.or old.sourceMap⟩
example : nativeUpdate [] ⟨some [1],some [2]⟩ ≠ CommentDirectives.nativeUpdate [] ⟨some [1],some [2]⟩ := by decide
end Mutation
