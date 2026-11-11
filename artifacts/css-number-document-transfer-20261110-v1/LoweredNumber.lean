import LoweredProgram
import LoweringLaws
import NumberBridge

namespace CssParserLowering

open CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer


theorem observed_retraction (initial) (result : Option (α × State)) :
    resultOption (observed initial result) = result := by
  cases result with
  | none => rfl
  | some value => cases value; rfl

theorem observable_lowering (parser : Parser shape) (state) :
    resultOption (run (lower parser) state) = ParserIR.run parser state := by
  rw [lowering_correct, observed_retraction]

theorem failure_atomic (parser : Parser shape) (state)
    (failed : ParserIR.run parser state = none) :
    run (lower parser) state = (none, state) := by
  rw [lowering_correct, failed]
  rfl

theorem success_preserved (parser : Parser shape) (state value final)
    (success : ParserIR.run parser state = some (value, final)) :
    run (lower parser) state = (some value, final) := by
  rw [lowering_correct, success]
  rfl

theorem optional_full_rollback (parser : Parser shape) (state)
    (failed : ParserIR.run parser state = none) :
    run (lower (.optional parser)) state = (some none, state) := by
  rw [lowering_correct, ParserIR.optional_rollback parser state failed]
  rfl

theorem number_parts (state) :
    run (lower numberTree) state =
      (some (rawParts (CssSemantics.CssNumberSyntax.consume state.input).decimal),
        { state with input := (CssSemantics.CssNumberSyntax.consume state.input).rest }) := by
  rw [lowering_correct, number_run]
  rfl


theorem number_execute_equal (state) : executeNumber state = NumberTransfer.execute state := by
  unfold executeNumber
  rw [observable_lowering numberTree state]
  rfl

theorem number_relation (source : List Char) (oldError : Bool) (value : Exact) (rest : List Char) :
    executeNumber ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩) ↔
      NumericResult source value rest := by
  rw [number_execute_equal, execute_iff]

theorem number_ready (source : List Char) (ready : CssSemantics.CssNumberParts.StartsNumber source)
    (oldError : Bool) (value : Exact) (rest : List Char)
    (result : executeNumber ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩)) :
    CssSemantics.CssNumberParts.StartsNumber source ∧ NumericResult source value rest := by
  exact ⟨ready, (number_relation source oldError value rest).mp result⟩

end CssParserLowering
