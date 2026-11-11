import ProgramLaws
import Laws
import JsonInput

namespace CssGrammar

def extractedProgram : List Op := [
  .keyword "none",
  .keyword "both",
  .alt,
  .keyword "horizontal",
  .alt,
  .keyword "vertical",
  .alt,
  .keyword "block",
  .alt,
  .keyword "inline",
  .alt]

def extractedJson : Lean.Json := .arr #[
  .arr #[.str "keyword", .str "none"],
  .arr #[.str "keyword", .str "both"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "horizontal"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "vertical"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "block"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "inline"],
  .arr #[.str "alt"]]

end CssGrammar
