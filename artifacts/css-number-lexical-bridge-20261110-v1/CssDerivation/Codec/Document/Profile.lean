import CssDerivation.Codec.Json.TypedSchemaLaws
import CssDerivation.Codec.Json.Document

namespace CssDerivation.DocumentSchema
open Lean FirstOrder TypedCodec JsonSchema

structure Signature where
  name : String
  head : Ty
  result : Ty
  deriving DecidableEq, Repr

def Field (j : Json) (name : String) (value : Json) : Prop :=
  j.getObjVal? name = .ok value

def ExactKeys (j : Json) (names : List String) : Prop :=
  match j with
  | .obj fields => (fields.toList.map Prod.fst).Perm names
  | _ => False

def DefinitionSchema (signature : Signature) (definitions : Json)
    (alias : String × Ty × DataExpr) : Prop :=
  ∃ source, ∃ e : Expr [signature.head] signature.result,
    Field definitions signature.name source ∧
    ExprSchema [] source (encodeExpr e) ∧
    alias = (signature.name, signature.head, encodeExpr e)

inductive DefinitionListSchema (definitions : Json) : List Signature → Aliases → Prop where
  | nil : DefinitionListSchema definitions [] []
  | cons {signature rest alias aliases} : DefinitionSchema signature definitions alias →
      DefinitionListSchema definitions rest aliases →
      DefinitionListSchema definitions (signature :: rest) (alias :: aliases)

def DefinitionsSchema (signatures : List Signature) (definitions : Json)
    (aliases : Aliases) : Prop :=
  (signatures.map Signature.name).Nodup ∧
  ExactKeys definitions (signatures.map Signature.name) ∧
  DefinitionListSchema definitions signatures aliases

def readDefinitionList : List Signature → Json → Option Aliases
  | [], _ => some []
  | signature :: rest, definitions => do
      let alias ← readDefinition definitions signature.name signature.head signature.result
      let aliases ← readDefinitionList rest definitions
      some (alias :: aliases)

def readDefinitions (signatures : List Signature) (definitions : Json) : Option Aliases :=
  if (signatures.map Signature.name).Nodup then
    if fieldsExactly definitions (signatures.map Signature.name) then
      readDefinitionList signatures definitions
    else none
  else none

def outerKeys : List String := ["schema", "definitions", "program", "source_map"]

def readDocumentWith (signatures : List Signature) (result : Ty)
    (j : Json) : Option (Stmt [] result) := do
  if !fieldsExactly j outerKeys then none else do
    let schema ← field j "schema"
    if schema.getNat?.toOption != some 1 then none else do
      let definitions ← field j "definitions"
      let aliases ← readDefinitions signatures definitions
      let sourceMap ← field j "source_map"
      let _ ← sourceMap.getObj?.toOption
      let program ← field j "program"
      checkStmtJson aliases [] result program

def ObjectValue (j : Json) : Prop := ∃ fields, j = .obj fields

def DocumentSchema (signatures : List Signature) (result : Ty)
    (j : Json) (program : Stmt [] result) : Prop :=
  ∃ version definitions sourceMap source aliases raw,
    ExactKeys j outerKeys ∧
    Field j "schema" version ∧ version.getNat? = .ok 1 ∧
    Field j "definitions" definitions ∧ DefinitionsSchema signatures definitions aliases ∧
    Field j "source_map" sourceMap ∧ ObjectValue sourceMap ∧
    Field j "program" source ∧ StmtSchema aliases source raw ∧
    encodeStmt program = normalizeStmt raw

def escapeSignatures : List Signature :=
  [⟨"hexExpr", .scalar, .bool⟩, ⟨"whitespaceExpr", .scalar, .bool⟩,
   ⟨"magnitudeExpr", .chars, .nat⟩, ⟨"decodeExpr", .nat, .scalar⟩]

def readEscapeDocument := readDocumentWith escapeSignatures .scalar

end CssDerivation.DocumentSchema
