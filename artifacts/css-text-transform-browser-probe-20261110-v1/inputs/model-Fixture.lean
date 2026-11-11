import JsonV2

namespace CssUnordered

def textProgram : List Op := [
  (.legacy (.keyword "none")),
  (.legacy (.keyword "capitalize")),
  (.legacy (.keyword "uppercase")),
  (.legacy (.alt)),
  (.legacy (.keyword "lowercase")),
  (.legacy (.alt)),
  (.legacy (.keyword "full-width")),
  (.legacy (.keyword "full-size-kana")),
  .unordered 3,
  (.legacy (.alt))]

def textJson : Lean.Json := .arr #[.arr #[.str "keyword", .str "none"], .arr #[.str "keyword", .str "capitalize"], .arr #[.str "keyword", .str "uppercase"], .arr #[.str "alt"], .arr #[.str "keyword", .str "lowercase"], .arr #[.str "alt"], .arr #[.str "keyword", .str "full-width"], .arr #[.str "keyword", .str "full-size-kana"], .arr #[.str "unordered", Lean.toJson (3 : Nat)], .arr #[.str "alt"]]

def textGrammar : CssGrammar.Grammar := (decode textProgram).getD (.keyword "invalid")

def referenceWords : List (List String) := [["none"], ["capitalize"], ["uppercase"], ["lowercase"], ["full-width"], ["full-size-kana"], ["capitalize", "full-width"], ["full-width", "capitalize"], ["uppercase", "full-width"], ["full-width", "uppercase"], ["lowercase", "full-width"], ["full-width", "lowercase"], ["capitalize", "full-size-kana"], ["full-size-kana", "capitalize"], ["uppercase", "full-size-kana"], ["full-size-kana", "uppercase"], ["lowercase", "full-size-kana"], ["full-size-kana", "lowercase"], ["full-width", "full-size-kana"], ["full-size-kana", "full-width"], ["capitalize", "full-width", "full-size-kana"], ["capitalize", "full-size-kana", "full-width"], ["full-width", "capitalize", "full-size-kana"], ["full-width", "full-size-kana", "capitalize"], ["full-size-kana", "capitalize", "full-width"], ["full-size-kana", "full-width", "capitalize"], ["uppercase", "full-width", "full-size-kana"], ["uppercase", "full-size-kana", "full-width"], ["full-width", "uppercase", "full-size-kana"], ["full-width", "full-size-kana", "uppercase"], ["full-size-kana", "uppercase", "full-width"], ["full-size-kana", "full-width", "uppercase"], ["lowercase", "full-width", "full-size-kana"], ["lowercase", "full-size-kana", "full-width"], ["full-width", "lowercase", "full-size-kana"], ["full-width", "full-size-kana", "lowercase"], ["full-size-kana", "lowercase", "full-width"], ["full-size-kana", "full-width", "lowercase"]]

end CssUnordered
