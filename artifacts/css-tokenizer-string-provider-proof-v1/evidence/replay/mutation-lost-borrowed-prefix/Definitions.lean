import StringTransitions
namespace Mutation
open StringTransitions CommentScan
def borrowed (single : Bool) : List Byte → List Byte → NativeValue
  | [], pre => ⟨⟨pre,0,.eof⟩,false⟩
  | b::bs, pre =>
    match nativeClass single b with
    | .close => ⟨⟨pre,1,.closed⟩,false⟩
    | .bad => ⟨⟨pre,0,.bad⟩,false⟩
    | .copy => let r := borrowed single bs (pre++[b]); ⟨extend [] 1 r.value,r.allocated⟩
    | _ => ⟨owned single (b::bs) [],true⟩
example : borrowed false [0] [65] ≠ StringTransitions.borrowed false [0] [65] := by simp [borrowed,StringTransitions.borrowed,owned,nativeClass,extend,Escape.encode,Escape.byte]
end Mutation
