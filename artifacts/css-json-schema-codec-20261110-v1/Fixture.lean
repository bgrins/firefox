import Document
import TypedSchemaLaws
import FixtureJson
import FOBridge

namespace CssDerivation.JsonSchema
open FirstOrder

set_option cbv.warning false in
set_option maxRecDepth 30000 in
set_option maxHeartbeats 4000000 in
theorem fixture_decodes : readDocument TypedCodec.fixture = some escapeTree := by cbv

def runDocument (j : Lean.Json) (input : List Char) : Option Result :=
  (readDocument j).map (fun p => FirstOrder.execute p input)

theorem fixture_execution (input : List Char) :
    runDocument TypedCodec.fixture input = some (FirstOrder.execute escapeTree input) := by
  simp [runDocument, fixture_decodes]

theorem fixture_relation (input : List Char) (result : Result) :
    runDocument TypedCodec.fixture input = some result ↔
      CssSemantics.CssEscape.Escaped input (toReference result) := by
  rw [fixture_execution, Option.some.injEq]
  exact escape_relation input result

theorem canonical_fixture_roundtrip :
    checkStmtJson [] [] .scalar (encodeStmtJson escapeTree) = some escapeTree :=
  statement_json_roundtrip [] escapeTree

end CssDerivation.JsonSchema
