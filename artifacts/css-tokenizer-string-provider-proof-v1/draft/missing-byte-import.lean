import StringTransitions
namespace Mutation
open StringTransitions
def nativeClass (single : Bool) (b : Byte) : Action :=
  if b == 10 || b == 12 || b == 13 then .bad
  else if b == 34 then if single then .close else .close
  else if b == 39 then if single then .close else .copy
  else if b == 92 then .escape
  else if b == 0 then .nul else .copy
example : nativeClass true 34 ≠ StringTransitions.nativeClass true 34 := by decide
end Mutation
