import URLTrace
import SemanticName
import Integration
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace Mutation
abbrev Byte := CommentScan.Byte

def lower (b : Byte) : Nat := if 65≤b.val ∧ b.val≤90 then b.val+32 else b.val

def nativeURL (name : List Byte) : Bool := name.map Fin.val == [117,114,108]
def referenceURL (name : List Byte) : Bool :=
 match name with
 | [a,b,c] => (a==117 || a==85) && (b==114 || b==82) && (c==108 || c==76)
 | _ => false


example : nativeURL [85,82,76] ≠ referenceURL [85,82,76] := by decide
end Mutation
