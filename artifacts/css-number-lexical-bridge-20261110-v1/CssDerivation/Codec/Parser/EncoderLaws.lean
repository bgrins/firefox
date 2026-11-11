import CssDerivation.Codec.Parser.Encoder
import CssDerivation.Codec.Parser.SchemaLaws

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR

theorem encodeType_schema (t : Ty) : TypeSchema (encodeType t) t := by
  cases t <;> constructor

theorem encodeParser_schema {shape} (p : Parser shape) : ParserSchema (encodeParser p) p := by
  induction p with
  | legacy p => exact .node (.rightArgs 2 1 _ _) (.legacy (encodeType_schema _) (encodeStmtJson_schema [] p))
  | take predicate => exact .node (.rightArgs 2 1 _ _) (.take (encodeExprJson_schema [] predicate))
  | scan predicate => exact .node (.rightArgs 2 1 _ _) (.scan (encodeExprJson_schema [] predicate))
  | nonempty p hp => exact .node (.rightArgs 2 1 _ _) (.nonempty hp)
  | pair a b ha hb => exact .node (.rightArgs 2 1 _ _) (.pair ha hb)
  | right a b ha hb => exact .node (.rightArgs 2 1 _ _) (.right ha hb)
  | optional p hp => exact .node (.rightArgs 2 1 _ _) (.optional hp)

theorem parser_json_roundtrip {shape} (p : Parser shape) :
    decodeParser shape (encodeParser p) = some p :=
  (decodeParser_spec _ p).mpr (encodeParser_schema p)

end CssDerivation.ParserJson
