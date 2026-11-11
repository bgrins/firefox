import CurrentFixture
import Reference

namespace CssGrammar

def currentLanguage : List (List String) := [["normal"], ["space-between"], ["space-around"], ["space-evenly"], ["stretch"], ["center"], ["start"], ["end"], ["flow-start"], ["flow-end"], ["flex-start"], ["flex-end"], ["left"], ["right"], ["unsafe", "center"], ["unsafe", "start"], ["unsafe", "end"], ["unsafe", "flow-start"], ["unsafe", "flow-end"], ["unsafe", "flex-start"], ["unsafe", "flex-end"], ["unsafe", "left"], ["unsafe", "right"], ["safe", "center"], ["safe", "start"], ["safe", "end"], ["safe", "flow-start"], ["safe", "flow-end"], ["safe", "flex-start"], ["safe", "flex-end"], ["safe", "left"], ["safe", "right"]]

def currentGrammar : Grammar := (decode currentProgram).getD (.keyword "INVALID")

theorem current_decodes : decode currentProgram = some currentGrammar := by decide

theorem current_json_decodes : readGrammar currentJson = .ok currentGrammar := by rfl

theorem current_language : language currentGrammar = currentLanguage := by decide

theorem current_accepts (words : List String) :
    accepts currentGrammar words = true ↔ words ∈ currentLanguage := by
  rw [accepts_language, current_language]

end CssGrammar
