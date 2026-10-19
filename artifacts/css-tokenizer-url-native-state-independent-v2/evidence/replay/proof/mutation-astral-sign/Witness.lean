import CommentObservers
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace Mutation
abbrev Byte := CommentScan.Byte
abbrev modulus : Nat := 4294967296
def wrap (n : Int) : Int := n % (modulus:Int)
structure State where
 position : Nat
 currentLineStart : Int
 packedLine : Nat
 deriving DecidableEq, Repr

def advance (s : State) (n : Nat) : State := {s with position:=s.position+n}
def intro (s : State) : State :=
 {s with position:=s.position+1,currentLineStart:=wrap (s.currentLineStart+1)}
def continuation (s : State) : State :=
 {s with position:=s.position+1,currentLineStart:=wrap (s.currentLineStart+1)}
def known (s : State) (b : Byte) : State :=
 if 240≤b.val then intro s
 else if 128≤b.val ∧ b.val≤191 then continuation s else advance s 1

def advanceLine (s : State) (count : Nat) : State :=
 {s with packedLine := (s.packedLine+(count*4)%modulus)%modulus}
def newline (s : State) (length : Nat) : State :=
 advanceLine {s with position:=s.position+length, currentLineStart:=wrap (s.position+length)} 1

def character (s : State) (bytes units : Nat) : State :=
 {s with position:=s.position+bytes, currentLineStart:=wrap (s.currentLineStart+(bytes-units:Nat))}

def Related (s : State) (r : CommentObservers.State) (block : Nat) : Prop :=
 s.position=r.offset ∧
 s.currentLineStart=wrap ((r.offset:Int)+1-r.column) ∧
 s.packedLine=4*r.line+block ∧ block<4

def location (s : State) : Nat × Int :=
 (s.packedLine/4,wrap ((s.position:Int)-s.currentLineStart+1))


example : intro ⟨0,0,0⟩ = ⟨1,1,0⟩ := by decide
end Mutation
