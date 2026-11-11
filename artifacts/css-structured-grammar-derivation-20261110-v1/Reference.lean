import Fixture

namespace CssGrammar

def referenceLanguage : List (List String) := [["normal"], ["space-between"], ["space-around"], ["space-evenly"], ["stretch"], ["center"], ["start"], ["end"], ["flex-start"], ["flex-end"], ["left"], ["right"], ["unsafe", "center"], ["unsafe", "start"], ["unsafe", "end"], ["unsafe", "flex-start"], ["unsafe", "flex-end"], ["unsafe", "left"], ["unsafe", "right"], ["safe", "center"], ["safe", "start"], ["safe", "end"], ["safe", "flex-start"], ["safe", "flex-end"], ["safe", "left"], ["safe", "right"]]

def extractedGrammar : Grammar := (decode extractedProgram).getD (.keyword "INVALID")

theorem extracted_decodes : decode extractedProgram = some extractedGrammar := by decide

theorem json_decodes : readGrammar extractedJson = .ok extractedGrammar := by rfl

theorem extracted_language : language extractedGrammar = referenceLanguage := by decide

theorem extracted_accepts (words : List String) :
    accepts extractedGrammar words = true ↔ words ∈ referenceLanguage := by
  rw [accepts_language, extracted_language]

end CssGrammar
