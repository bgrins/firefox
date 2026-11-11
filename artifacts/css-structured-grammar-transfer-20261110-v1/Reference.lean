import Fixture

namespace CssGrammar

def resizeLanguage : List (List String) := [["none"], ["both"], ["horizontal"], ["vertical"], ["block"], ["inline"]]

def resizeGrammar : Grammar := (decode extractedProgram).getD (.keyword "INVALID")

theorem resize_decodes : decode extractedProgram = some resizeGrammar := by decide

theorem resize_json_decodes : readGrammar extractedJson = .ok resizeGrammar := by rfl

theorem resize_language : language resizeGrammar = resizeLanguage := by decide

theorem resize_accepts (words : List String) :
    accepts resizeGrammar words = true ↔ words ∈ resizeLanguage := by
  rw [accepts_language, resize_language]

end CssGrammar
