import CssDerivation.Codec.LegacyJson

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

def rightObject (outer inner : Nat) (first : String) (a : Json) (second : String) (b : Json) : Json :=
  .obj ⟨⟨.inner outer first a .leaf (.inner inner second b .leaf .leaf)⟩⟩

def leftObject (outer inner : Nat) (first : String) (a : Json) (second : String) (b : Json) : Json :=
  .obj ⟨⟨.inner outer first a (.inner inner second b .leaf .leaf) .leaf⟩⟩

inductive Node : Json → String → List Json → Prop where
  | rightOp (outer inner op args) :
      Node (rightObject outer inner "op" (.str op) "args" (.arr args.toArray)) op args
  | rightArgs (outer inner op args) :
      Node (rightObject outer inner "args" (.arr args.toArray) "op" (.str op)) op args
  | leftOp (outer inner op args) :
      Node (leftObject outer inner "op" (.str op) "args" (.arr args.toArray)) op args
  | leftArgs (outer inner op args) :
      Node (leftObject outer inner "args" (.arr args.toArray) "op" (.str op)) op args

def scalarAllowed (n : Nat) : Prop := n < 0xD800 ∨ (0xDFFF < n ∧ n < 0x110000)
instance (n : Nat) : Decidable (scalarAllowed n) := inferInstanceAs (Decidable (_ ∨ _))

mutual
  inductive ExprSchema (aliases : Aliases) : Json → DataExpr → Prop where
    | node {j op args e} : Node j op args → ExprArguments aliases op args e → ExprSchema aliases j e

  inductive ExprArguments (aliases : Aliases) : String → List Json → DataExpr → Prop where
    | nat {j n} : j.getNat? = .ok n → ExprArguments aliases "nat" [j] (.nat n)
    | scalar {j n} : j.getNat? = .ok n → scalarAllowed n →
        ExprArguments aliases "scalar" [j] (.scalar (Char.ofNat n))
    | bool (b) : ExprArguments aliases "bool" [.bool b] (.bool b)
    | var {j n} : j.getNat? = .ok n → ExprArguments aliases "var" [j] (.var n)
    | nil : ExprArguments aliases "nil" [] .nil
    | unit : ExprArguments aliases "unit" [] .unit
    | use {name head body} : aliases.find? (fun entry => entry.1 == name) = some (name, head, body) →
        ExprArguments aliases "use" [.str name] (.scope head body)
    | code {ja a} : ExprSchema aliases ja a →
        ExprArguments aliases "code" [ja] (.code a)
    | scalarOf {ja a} : ExprSchema aliases ja a →
        ExprArguments aliases "scalarOf" [ja] (.scalarOf a)
    | add {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "add" [ja, jb] (.add a b)
    | sub {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "sub" [ja, jb] (.sub a b)
    | mul {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "mul" [ja, jb] (.mul a b)
    | leNat {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "leNat" [ja, jb] (.leNat a b)
    | ltNat {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "ltNat" [ja, jb] (.ltNat a b)
    | eqNat {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "eqNat" [ja, jb] (.eqNat a b)
    | leChar {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "leChar" [ja, jb] (.leChar a b)
    | eqChar {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "eqChar" [ja, jb] (.eqChar a b)
    | and {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "and" [ja, jb] (.and a b)
    | or {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "or" [ja, jb] (.or a b)
    | cons {ja jb a b} : ExprSchema aliases ja a → ExprSchema aliases jb b →
        ExprArguments aliases "cons" [ja, jb] (.cons a b)
    | ite {ja jb jc a b c} : ExprSchema aliases ja a → ExprSchema aliases jb b → ExprSchema aliases jc c →
        ExprArguments aliases "ite" [ja, jb, jc] (.ite a b c)
    | foldNat {ja jb jc a b c} : ExprSchema aliases ja a → ExprSchema aliases jb b → ExprSchema aliases jc c →
        ExprArguments aliases "foldNat" [ja, jb, jc] (.foldNat a b c)
end

mutual
  inductive StmtSchema (aliases : Aliases) : Json → DataStmt → Prop where
    | node {j op args p} : Node j op args → StmtArguments aliases op args p → StmtSchema aliases j p

  inductive StmtArguments (aliases : Aliases) : String → List Json → DataStmt → Prop where
    | ret {je e} : ExprSchema aliases je e → StmtArguments aliases "ret" [je] (.ret e)
    | letE {je jp e p} : ExprSchema aliases je e → StmtSchema aliases jp p →
        StmtArguments aliases "letE" [je, jp] (.letE e p)
    | read {ja jb a b} : StmtSchema aliases ja a → StmtSchema aliases jb b →
        StmtArguments aliases "read" [ja, jb] (.read a b)
    | scan {jn je jp n e p} : jn.getNat? = .ok n → ExprSchema aliases je e → StmtSchema aliases jp p →
        StmtArguments aliases "scan" [jn, je, jp] (.scan n e p)
    | raiseError {jp p} : StmtSchema aliases jp p → StmtArguments aliases "raiseError" [jp] (.raiseError p)
    | branch {je ja jb e a b} : ExprSchema aliases je e → StmtSchema aliases ja a → StmtSchema aliases jb b →
        StmtArguments aliases "branch" [je, ja, jb] (.branch e a b)
end

end CssDerivation.JsonSchema
