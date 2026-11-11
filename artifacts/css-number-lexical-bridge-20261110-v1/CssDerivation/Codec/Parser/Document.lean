import CssDerivation.Codec.Parser.Encoder
import CssDerivation.Parser.LoweringLaws

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR DocumentSchema

def envelopeKeys : List String := ["schema", "program", "source_map"]

def readDocument (shape : Shape) (j : Json) : Option (Parser shape) := do
  if !fieldsExactly j envelopeKeys then none else do
    let version ← field j "schema"
    if version.getStr?.toOption != some "css-parser-ir-v1" then none else do
      let sourceMap ← field j "source_map"
      let _ ← sourceMap.getObj?.toOption
      let program ← field j "program"
      decodeParser shape program

def EnvelopeSchema {shape} (j : Json) (p : Parser shape) : Prop :=
  ∃ version sourceMap source,
    ExactKeys j envelopeKeys ∧
    Field j "schema" version ∧ version.getStr? = .ok "css-parser-ir-v1" ∧
    Field j "source_map" sourceMap ∧ ObjectValue sourceMap ∧
    Field j "program" source ∧ ParserSchema source p

def encodeDocument {shape} (p : Parser shape) : Json :=
  Json.mkObj [("schema", .str "css-parser-ir-v1"), ("program", encodeParser p),
    ("source_map", Json.mkObj [])]

def executeDocument (shape : Shape) (j : Json) (state : State) :
    Option (Option shape.Value × State) :=
  (readDocument shape j).map (fun p => CssParserLowering.run (CssParserLowering.lower p) state)

end CssDerivation.ParserJson
