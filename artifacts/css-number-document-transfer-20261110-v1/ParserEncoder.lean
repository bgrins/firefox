import ParserReader

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR

def encodeType : Ty → Json
  | .nat => .str "nat"
  | .scalar => .str "scalar"
  | .bool => .str "bool"
  | .chars => .str "chars"
  | .unit => .str "unit"

def encodeParser : {shape : Shape} → Parser shape → Json
  | _, .legacy (t := t) p => nodeJson "legacy" [encodeType t, encodeStmtJson p]
  | _, .take predicate => nodeJson "take" [encodeExprJson predicate]
  | _, .scan predicate => nodeJson "scan" [encodeExprJson predicate]
  | _, .nonempty p => nodeJson "nonempty" [encodeParser p]
  | _, .pair a b => nodeJson "pair" [encodeParser a, encodeParser b]
  | _, .right a b => nodeJson "right" [encodeParser a, encodeParser b]
  | _, .optional p => nodeJson "optional" [encodeParser p]

end CssDerivation.ParserJson
