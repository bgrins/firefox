import URLNativeLeadingBulk
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace Mutation
open URLNativeState
abbrev Byte := CommentScan.Byte
inductive Result where
 | function (state : State)
 | emptyURL (state : State)
 | body (value : URLNativeBorrowed.Entry)
 deriving DecidableEq, Repr

def scan : List Byte → Nat → URLWhitespace.Stats → State → Result
 | [], index, stats, s => .emptyURL (URLNativeLeadingBulk.apply index stats s)
 | b::bs, index, stats, s =>
   if URLScan.nativeWhitespace b then
     scan bs (index+1) (if URLWhitespace.marks b bs then ⟨stats.lines+1,index⟩ else stats) s
   else if URLLeading.quote b then .function (URLNativeLeadingBulk.apply index stats s)
   else if b==41 then .emptyURL (URLNativeLeadingBulk.apply (index+1) stats s)
   else .body (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.apply index stats s))

def run (xs : List Byte) (s : State) : Result := scan xs 0 ⟨0,0⟩ s


example : run [32,34] ⟨4,0,0⟩ = .function ⟨5,0,0⟩ := by decide
end Mutation
