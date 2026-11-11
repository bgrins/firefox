import CssDerivation.Parser.Syntax
import CssDerivation.Codec.Document.KeyLaws

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR

deriving instance DecidableEq for Shape

inductive TypeSchema : Json → Ty → Prop where
  | nat : TypeSchema (.str "nat") .nat
  | scalar : TypeSchema (.str "scalar") .scalar
  | bool : TypeSchema (.str "bool") .bool
  | chars : TypeSchema (.str "chars") .chars
  | unit : TypeSchema (.str "unit") .unit

mutual
  inductive ParserSchema : Json → {shape : Shape} → Parser shape → Prop where
    | node {j op args shape} {p : Parser shape} :
        Node j op args → ParserArguments op args p → ParserSchema j p

  inductive ParserArguments : String → List Json → {shape : Shape} → Parser shape → Prop where
    | legacy {jt jp t} {p : Stmt [] t} :
        TypeSchema jt t → StmtSchema [] jp (encodeStmt p) →
        ParserArguments "legacy" [jt, jp] (.legacy p)
    | take {j} {predicate : Predicate} : ExprSchema [] j (encodeExpr predicate) →
        ParserArguments "take" [j] (.take predicate)
    | scan {j} {predicate : Predicate} : ExprSchema [] j (encodeExpr predicate) →
        ParserArguments "scan" [j] (.scan predicate)
    | nonempty {j} {p : Parser (.base .chars)} : ParserSchema j p →
        ParserArguments "nonempty" [j] (.nonempty p)
    | pair {ja jb a b} {pa : Parser a} {pb : Parser b} :
        ParserSchema ja pa → ParserSchema jb pb → ParserArguments "pair" [ja, jb] (.pair pa pb)
    | right {ja jb a b} {pa : Parser a} {pb : Parser b} :
        ParserSchema ja pa → ParserSchema jb pb → ParserArguments "right" [ja, jb] (.right pa pb)
    | optional {j a} {p : Parser a} : ParserSchema j p →
        ParserArguments "optional" [j] (.optional p)
end

abbrev Parsed (j : Json) := Σ shape, {p : Parser shape // ParserSchema j p}
abbrev ParsedArguments (op : String) (args : List Json) :=
  Σ shape, {p : Parser shape // ParserArguments op args p}

def readType : (j : Json) → Option {t : Ty // TypeSchema j t}
  | .str "nat" => some ⟨.nat, .nat⟩
  | .str "scalar" => some ⟨.scalar, .scalar⟩
  | .str "bool" => some ⟨.bool, .bool⟩
  | .str "chars" => some ⟨.chars, .chars⟩
  | .str "unit" => some ⟨.unit, .unit⟩
  | _ => none

def certify {α : Type} {P : α → Prop} (result : Option α)
    (sound : ∀ value, result = some value → P value) : Option {value // P value} :=
  match result with
  | none => none
  | some value => some ⟨value, sound value rfl⟩

def readPredicate (j : Json) : Option {p : Predicate // ExprSchema [] j (encodeExpr p)} :=
  certify (checkExprJson [] [.scalar] .bool j)
    (fun p accepted => (alias_free_expression_json_spec j p).mp accepted)

def readLegacy (t : Ty) (j : Json) : Option {p : Stmt [] t // StmtSchema [] j (encodeStmt p)} :=
  certify (checkStmtJson [] [] t j)
    (fun p accepted => (alias_free_statement_json_spec j p).mp accepted)

end CssDerivation.ParserJson
