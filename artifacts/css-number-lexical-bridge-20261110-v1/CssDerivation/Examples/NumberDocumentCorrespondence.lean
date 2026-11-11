import CssDerivation.Examples.NumberDocumentExecution
import CssDerivation.Codec.Parser.DocumentLaws
import CssDerivation.Examples.NumberBackendCorrespondence

namespace CssDerivation.ParserJson
open Lean ParserIR NumberTransfer

theorem accepted_number_execution (j : Json) (p : Parser NumberShape) (state : State)
    (schema : EnvelopeSchema j p) :
    executeNumberDocument j state =
      some (let result := CssParserLowering.observed state (ParserIR.run p state)
        (result.1.map project, result.2)) := by
  simp only [executeNumberDocument, (document_spec _ _).mpr schema, Option.map_some, projectRun]
  rw [CssParserLowering.lowering_correct p state]

theorem fixed_number_value (state : State) :
    numberValue (encodeDocument numberTree) state = CssParserLowering.executeNumber state := by
  simp only [numberValue, executeNumberDocument, document_json_roundtrip,
    Option.map_some, Option.bind_some, projectRun, CssParserLowering.executeNumber]
  cases CssParserLowering.run (CssParserLowering.lower numberTree) state with
  | mk value final => cases value <;> rfl

theorem fixed_number_relation (source : List Char) (oldError : Bool) (value : Exact) (rest : List Char) :
    numberValue (encodeDocument numberTree) ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩) ↔
      NumericResult source value rest := by
  rw [fixed_number_value, CssParserLowering.number_relation]

theorem fixed_number_parts (state : State) :
    executeNumberDocument (encodeDocument numberTree) state =
      some (some (project (rawParts (CssSemantics.CssNumberSyntax.consume state.input).decimal)),
        {state with input := (CssSemantics.CssNumberSyntax.consume state.input).rest}) := by
  simp only [executeNumberDocument, document_json_roundtrip, Option.map_some, projectRun]
  rw [CssParserLowering.number_parts state]
  rfl

theorem fixed_number_ready (source : List Char)
    (ready : CssSemantics.CssNumberParts.StartsNumber source)
    (oldError : Bool) (value : Exact) (rest : List Char)
    (result : numberValue (encodeDocument numberTree) ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩)) :
    CssSemantics.CssNumberParts.StartsNumber source ∧ NumericResult source value rest :=
  ⟨ready, (fixed_number_relation source oldError value rest).mp result⟩

end CssDerivation.ParserJson
