import StringTransitions
namespace Mutation
open StringTransitions CommentScan
def owned (single : Bool) : List Byte → List Byte → Value
  | [], buffer => ⟨buffer,0,.eof⟩
  | b::bs, buffer =>
    match nativeClass single b with
    | .close => ⟨buffer,1,.closed⟩
    | .bad => ⟨buffer,1,.bad⟩
    | .nul => extend [] 1 (owned single bs (buffer++Escape.encode 65533))
    | .copy => extend [] 1 (owned single bs (buffer++[b]))
    | .escape =>
      let e := nativeEscape bs
      extend [] (1+e.count) (owned single (bs.drop e.count) (buffer++e.output))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega
example : owned false [10] [] ≠ StringTransitions.owned false [10] [] := by simp [owned,StringTransitions.owned,nativeClass,extend,Escape.encode,Escape.byte]
end Mutation
