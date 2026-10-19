import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 5000000
namespace Mutation
open CommentObservers
abbrev Byte := CommentScan.Byte

structure Stats where
 lines : Nat
 last : Nat
 deriving DecidableEq, Repr

def marks (b : Byte) (bs : List Byte) : Bool :=
 b == 10 || b == 12 || (b == 13)

def scan : List Byte → Nat → Stats → Stats
 | [], _, s => s
 | b::bs, index, s =>
   scan bs (index+1) (if marks b bs then ⟨s.lines+1,index⟩ else s)

def summary : List Byte → Stats
 | [] => ⟨0,0⟩
 | b::bs =>
   let r := summary bs
   ⟨r.lines + if marks b bs then 1 else 0,
    if r.lines>0 then r.last+1 else 0⟩


example : marks 13 [10] = true := by decide
end Mutation
