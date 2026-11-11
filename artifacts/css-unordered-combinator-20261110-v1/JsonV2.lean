import JsonInput
import ProgramV2

namespace CssUnordered
open Lean CssGrammar

def readOp (json : Json) : Except String Op := do
  match json with
  | .arr args => match args.toList with
    | [.str "unordered", arity] => return .unordered (← arity.getNat?)
    | _ => return .legacy (← CssGrammar.readOp json)
  | _ => return .legacy (← CssGrammar.readOp json)

def readOps : List Json → Except String (List Op)
  | [] => .ok []
  | head :: tail => do return (← readOp head) :: (← readOps tail)

def readGrammar (json : Json) : Except String Grammar := do
  let code ← readOps (← json.getArr?).toList
  match decode code with
  | some grammar => return grammar
  | none => throw "invalid stack or unsupported nullable unordered operand"

end CssUnordered
