import Encoder

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

def readDefinition (j : Json) (name : String) (head result : Ty) : Option (String × Ty × DataExpr) := do
  let source ← field j name
  let data ← readExprData [] source
  let _ ← TypedCodec.checkExpr [head] result data
  some (name, head, data)

def readDocument (j : Json) : Option (Stmt [] .scalar) := do
  if !fieldsExactly j ["schema", "definitions", "program", "source_map"] then none else do
    let schema ← field j "schema"
    if schema.getNat?.toOption != some 1 then none else do
      let definitions ← field j "definitions"
      if !fieldsExactly definitions ["hexExpr", "whitespaceExpr", "magnitudeExpr", "decodeExpr"] then none else do
        let hex ← readDefinition definitions "hexExpr" .scalar .bool
        let whitespace ← readDefinition definitions "whitespaceExpr" .scalar .bool
        let magnitude ← readDefinition definitions "magnitudeExpr" .chars .nat
        let decode ← readDefinition definitions "decodeExpr" .nat .scalar
        let sourceMap ← field j "source_map"
        let _ ← sourceMap.getObj?.toOption
        let program ← field j "program"
        checkStmtJson [hex, whitespace, magnitude, decode] [] .scalar program

def readDocumentText (text : String) : Option (Stmt [] .scalar) :=
  Json.parse text |>.toOption.bind readDocument

end CssDerivation.JsonSchema
