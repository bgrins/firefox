import URLNativeState
import BadURL
import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace Mutation
open URLNativeState
abbrev Byte := CommentScan.Byte
structure Result where
 state : State
 rawEnd : Nat
 closed : Bool
 count : Nat
 deriving DecidableEq, Repr

def add (n : Nat) (r : Result) : Result := {r with count:=n+r.count}

def run : List Byte → State → Result
 | [], s => ⟨s,s.position,false,0⟩
 | b::bs, s =>
   if b==41 then ⟨advance s 1,s.position+1,true,1⟩
   else if b==92 && (bs.head?==some 41 || bs.head?==some 92) then
     add 2 (run bs.tail (advance s 2))
   else if b==13 && bs.head?==some 10 then
     add 2 (run bs.tail (newline s 2))
   else if CommentObservers.isNewline b then
     add 1 (run bs (newline s 1))
   else add 1 (run bs (known s b))
termination_by xs => xs.length


example : (run [41] ⟨0,0,0⟩).rawEnd=1 := by simp [run,advance]
end Mutation
