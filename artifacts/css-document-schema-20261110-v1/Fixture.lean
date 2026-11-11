import DocumentLaws
import CssDerivation.Examples.EscapeDocument

namespace CssDerivation.DocumentSchema
open FirstOrder JsonSchema

theorem escape_fixture_decodes :
    readEscapeDocument TypedCodec.fixture = some escapeTree := by
  rw [escape_wrapper_equivalent]
  exact fixture_decodes

def runEscape (j : Lean.Json) (input : List Char) : Option Result :=
  (readEscapeDocument j).map (fun p => FirstOrder.execute p input)

theorem escape_fixture_execution (input : List Char) :
    runEscape TypedCodec.fixture input = some (FirstOrder.execute escapeTree input) := by
  simp [runEscape, escape_fixture_decodes]

theorem escape_fixture_relation (input : List Char) (result : Result) :
    runEscape TypedCodec.fixture input = some result ↔
      CssSemantics.CssEscape.Escaped input (toReference result) := by
  rw [escape_fixture_execution, Option.some.injEq]
  exact escape_relation input result

end CssDerivation.DocumentSchema
