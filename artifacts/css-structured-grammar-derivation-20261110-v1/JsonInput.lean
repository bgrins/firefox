import Lean
import Program

namespace CssGrammar
open Lean

def readOp : Json → Except String Op
  | .arr args => match args.toList with
    | [.str "keyword", .str word] => .ok (.keyword word)
    | [.str "alt"] => .ok .alt
    | [.str "seq"] => .ok .seq
    | [.str "optional"] => .ok .optional
    | _ => .error "unknown opcode or arity"
  | _ => .error "instruction must be an array"

def readOps : List Json → Except String (List Op)
  | [] => .ok []
  | head :: rest => do
    let op ← readOp head
    let tail ← readOps rest
    return op :: tail

def readGrammar (json : Json) : Except String Grammar := do
  let ops ← readOps (← json.getArr?).toList
  match decode ops with
  | some grammar => return grammar
  | none => throw "invalid stack shape"

def readWords (json : Json) : Except String (List String) := do
  (← json.getArr?).toList.mapM Json.getStr?

end CssGrammar
