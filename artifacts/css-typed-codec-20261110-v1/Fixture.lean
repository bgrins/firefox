import FixtureJson
import FOBridge

namespace CssDerivation.TypedCodec
open FirstOrder

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
theorem fixture_decodes : decodeDocument fixture = some escapeTree := by rfl

def runDocument (j : Lean.Json) (input : List Char) : Option Result :=
  (decodeDocument j).map (fun p => FirstOrder.execute p input)

theorem fixture_execution (input : List Char) :
    runDocument fixture input = some (FirstOrder.execute escapeTree input) := by
  simp [runDocument, fixture_decodes]

theorem fixture_relation (input : List Char) (result : Result) :
    runDocument fixture input = some result ↔
      CssSemantics.CssEscape.Escaped input (toReference result) := by
  rw [fixture_execution, Option.some.injEq]
  exact escape_relation input result

end CssDerivation.TypedCodec
