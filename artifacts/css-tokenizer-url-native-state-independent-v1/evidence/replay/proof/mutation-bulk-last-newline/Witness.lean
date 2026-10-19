import URLNativeBorrowed
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace Mutation
open URLNativeState
abbrev Byte := CommentScan.Byte

def apply (consumed : Nat) (stats : URLWhitespace.Stats) (s : State) : State :=
 let moved := {s with position:=s.position+consumed}
 if stats.lines>0 then
   advanceLine {moved with currentLineStart:=wrap (s.position+stats.last)} stats.lines
 else moved

def bulk (ws : List Byte) (s : State) : State :=
 apply ws.length (URLWhitespace.scan ws 0 ⟨0,0⟩) s


example : (apply 1 ⟨1,0⟩ ⟨4,0,0⟩).currentLineStart=4 := by decide
end Mutation
