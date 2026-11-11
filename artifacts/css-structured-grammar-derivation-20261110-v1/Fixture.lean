import ProgramLaws
import Laws
import JsonInput

namespace CssGrammar

def extractedProgram : List Op := [
  .keyword "normal",
  .keyword "space-between",
  .keyword "space-around",
  .alt,
  .keyword "space-evenly",
  .alt,
  .keyword "stretch",
  .alt,
  .alt,
  .keyword "unsafe",
  .keyword "safe",
  .alt,
  .optional,
  .keyword "center",
  .keyword "start",
  .alt,
  .keyword "end",
  .alt,
  .keyword "flex-start",
  .alt,
  .keyword "flex-end",
  .alt,
  .keyword "left",
  .alt,
  .keyword "right",
  .alt,
  .seq,
  .alt]

def extractedJson : Lean.Json := .arr #[
  .arr #[.str "keyword", .str "normal"],
  .arr #[.str "keyword", .str "space-between"],
  .arr #[.str "keyword", .str "space-around"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "space-evenly"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "stretch"],
  .arr #[.str "alt"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "unsafe"],
  .arr #[.str "keyword", .str "safe"],
  .arr #[.str "alt"],
  .arr #[.str "optional"],
  .arr #[.str "keyword", .str "center"],
  .arr #[.str "keyword", .str "start"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "end"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "flex-start"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "flex-end"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "left"],
  .arr #[.str "alt"],
  .arr #[.str "keyword", .str "right"],
  .arr #[.str "alt"],
  .arr #[.str "seq"],
  .arr #[.str "alt"]]

end CssGrammar
