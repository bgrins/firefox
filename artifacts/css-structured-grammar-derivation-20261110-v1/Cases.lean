import CurrentReference
import JsonInput

namespace CssGrammar

theorem optional_absent : accepts (.optional (.keyword "x")) [] = true := by decide
theorem optional_once : accepts (.optional (.keyword "x")) ["x"] = true := by decide
theorem optional_not_twice : accepts (.optional (.keyword "x")) ["x", "x"] = false := by decide
theorem ordered_sequence : accepts (.seq (.keyword "safe") (.keyword "left"))
    ["left", "safe"] = false := by decide
theorem ambiguous_prefix : accepts (.alt (.keyword "a") (.seq (.keyword "a") (.keyword "b")))
    ["a", "b"] = true := by decide
theorem full_consumption : accepts (.keyword "a") ["a", "b"] = false := by decide
theorem stack_underflow : decode [.seq] = none := by decide
theorem stack_leftover : decode [.keyword "a", .keyword "b"] = none := by decide
theorem empty_program : decode [] = none := by decide
theorem wrong_arity : readOp (.arr #[.str "seq", .str "ignored"]) =
    .error "unknown opcode or arity" := by rfl
theorem unknown_opcode : readOp (.arr #[.str "run", .str "arbitrary code"]) =
    .error "unknown opcode or arity" := by rfl
theorem wrong_keyword_type : readOp (.arr #[.str "keyword", .bool true]) =
    .error "unknown opcode or arity" := by rfl

end CssGrammar
