import NumberDocumentLaws

namespace CssDerivation.ParserJson
open Lean ParserIR NumberTransfer
set_option cbv.warning false
set_option maxRecDepth 30000
set_option maxHeartbeats 4000000

def numberFixture : Json := json% {"program":{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[43],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[45],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"take"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[46],"op":"scalar"}],"op":"eqChar"}],"op":"take"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"}],"op":"nonempty"}],"op":"right"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[101],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[69],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"take"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[43],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[45],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"take"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"}],"op":"nonempty"}],"op":"pair"}],"op":"right"}],"op":"optional"}],"op":"pair"}],"op":"pair"}],"op":"pair"},"schema":"css-parser-ir-v1","source_map":{}}

def changedFixture : Json := json% {"program":{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[43],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[45],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"take"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[46],"op":"scalar"}],"op":"eqChar"}],"op":"take"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"}],"op":"nonempty"}],"op":"right"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[101],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[69],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"scan"},{"args":[{"args":[{"args":[{"args":[{"args":[{"args":[0],"op":"var"},{"args":[43],"op":"scalar"}],"op":"eqChar"},{"args":[{"args":[0],"op":"var"},{"args":[45],"op":"scalar"}],"op":"eqChar"}],"op":"or"}],"op":"take"}],"op":"optional"},{"args":[{"args":[{"args":[{"args":[{"args":[48],"op":"scalar"},{"args":[0],"op":"var"}],"op":"leChar"},{"args":[{"args":[0],"op":"var"},{"args":[57],"op":"scalar"}],"op":"leChar"}],"op":"and"}],"op":"scan"}],"op":"nonempty"}],"op":"pair"}],"op":"right"}],"op":"optional"}],"op":"pair"}],"op":"pair"}],"op":"pair"},"schema":"css-parser-ir-v1","source_map":{}}

theorem number_fixture_encoded : numberFixture = encodeDocument numberTree := by cbv

theorem changed_fixture_encoded : changedFixture = encodeDocument changedNumberTree := by cbv

theorem number_fixture_decoded : readDocument NumberShape numberFixture = some numberTree := by
  rw [number_fixture_encoded, document_json_roundtrip]

theorem number_fixture_relation (source : List Char) (oldError : Bool) (value : Exact) (rest : List Char) :
    numberValue numberFixture ⟨source, oldError⟩ = some (value, ⟨rest, oldError⟩) ↔
      NumericResult source value rest := by
  rw [number_fixture_encoded, fixed_number_relation]

end CssDerivation.ParserJson
