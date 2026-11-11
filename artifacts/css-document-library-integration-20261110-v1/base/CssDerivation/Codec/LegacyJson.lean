import CssDerivation.Codec.DataLaws

namespace CssDerivation.TypedCodec
open FirstOrder Lean

structure Atom where
  natural : Option Nat := none
  boolean : Option Bool := none
  text : Option String := none
  expression : Option DataExpr := none
  statement : Option DataStmt := none

structure Layer where
  atom : Atom := {}
  arguments : Option (List Atom) := none

abbrev Aliases := List (String × Ty × DataExpr)

def expressionNode (aliases : Aliases) : String → List Atom → Option DataExpr
  | "nat", [a] => a.natural.map .nat
  | "scalar", [a] => do
      let n ← a.natural
      if n < 0xD800 ∨ (0xDFFF < n ∧ n < 0x110000) then some (.scalar (Char.ofNat n)) else none
  | "bool", [a] => a.boolean.map .bool
  | "var", [a] => a.natural.map .var
  | "nil", [] => some .nil
  | "unit", [] => some .unit
  | "use", [a] => do
      let name ← a.text
      let (_, head, body) ← aliases.find? (fun entry => entry.1 == name)
      some (.scope head body)
  | "code", [a] => do
      let a ← a.expression
      some (.code a)
  | "scalarOf", [a] => do
      let a ← a.expression
      some (.scalarOf a)
  | "add", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.add a b)
  | "sub", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.sub a b)
  | "mul", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.mul a b)
  | "leNat", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.leNat a b)
  | "ltNat", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.ltNat a b)
  | "eqNat", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.eqNat a b)
  | "leChar", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.leChar a b)
  | "eqChar", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.eqChar a b)
  | "and", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.and a b)
  | "or", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.or a b)
  | "cons", [a, b] => do
      let a ← a.expression
      let b ← b.expression
      some (.cons a b)
  | "ite", [a, b, c] => do
      let a ← a.expression
      let b ← b.expression
      let c ← c.expression
      some (.ite a b c)
  | "foldNat", [a, b, c] => do
      let a ← a.expression
      let b ← b.expression
      let c ← c.expression
      some (.foldNat a b c)
  | _, _ => none

def statementNode : String → List Atom → Option DataStmt
  | "ret", [e] => e.expression.map .ret
  | "letE", [e, next] => do
      let e ← e.expression
      let next ← next.statement
      some (.letE e next)
  | "read", [eof, next] => do
      let eof ← eof.statement
      let next ← next.statement
      some (.read eof next)
  | "scan", [budget, predicate, next] => do
      let budget ← budget.natural
      let predicate ← predicate.expression
      let next ← next.statement
      some (.scan budget predicate next)
  | "raiseError", [next] => next.statement.map .raiseError
  | "branch", [condition, yes, no] => do
      let condition ← condition.expression
      let yes ← yes.statement
      let no ← no.statement
      some (.branch condition yes no)
  | _, _ => none

def exactFields {α : Type} (expected : List String) (fields : List (String × α)) : Bool :=
  fields.length == expected.length && expected.all (fun key => fields.countP (fun e => e.1 == key) == 1)

def objectNode (aliases : Aliases) (fields : List (String × Layer)) : Layer :=
  let result : Option Atom := do
    if !exactFields ["op", "args"] fields then none else do
      let (_, op) ← fields.find? (fun f => f.1 == "op")
      let op ← op.atom.text
      let (_, args) ← fields.find? (fun f => f.1 == "args")
      let args ← args.arguments
      some { expression := expressionNode aliases op args, statement := statementNode op args }
  { atom := result.getD {} }

mutual
  def foldJson (aliases : Aliases) : Json → Layer
    | .null => {}
    | .bool b => { atom := { boolean := some b } }
    | .num n => { atom := { natural := (Json.num n).getNat?.toOption } }
    | .str text => { atom := { text := some text } }
    | .arr ⟨xs⟩ => { arguments := some ((foldArray aliases xs).map Layer.atom) }
    | .obj ⟨⟨tree⟩⟩ => objectNode aliases (foldObject aliases tree)

  def foldArray (aliases : Aliases) : List Json → List Layer
    | [] => []
    | x :: xs => foldJson aliases x :: foldArray aliases xs

  def foldObject (aliases : Aliases) :
      Std.DTreeMap.Internal.Impl String (fun _ => Json) → List (String × Layer)
    | .leaf => []
    | .inner _ key value left right =>
        foldObject aliases left ++ (key, foldJson aliases value) :: foldObject aliases right
end

def field (j : Json) (name : String) : Option Json := (j.getObjVal? name).toOption

def fieldsExactly (j : Json) (names : List String) : Bool :=
  match j with
  | .obj fields => exactFields names fields.toList
  | _ => false

def definition (j : Json) (name : String) (head result : Ty) : Option (String × Ty × DataExpr) := do
  let source ← field j name
  let data ← (foldJson [] source).atom.expression
  let _ ← checkExpr [head] result data
  some (name, head, data)

def decodeDocument (j : Json) : Option (Stmt [] .scalar) := do
  if !fieldsExactly j ["schema", "definitions", "program", "source_map"] then none else do
    let schema ← field j "schema"
    if schema.getNat?.toOption != some 1 then none else do
      let definitions ← field j "definitions"
      if !fieldsExactly definitions ["hexExpr", "whitespaceExpr", "magnitudeExpr", "decodeExpr"] then none else do
        let hex ← definition definitions "hexExpr" .scalar .bool
        let whitespace ← definition definitions "whitespaceExpr" .scalar .bool
        let magnitude ← definition definitions "magnitudeExpr" .chars .nat
        let decode ← definition definitions "decodeExpr" .nat .scalar
        let sourceMap ← field j "source_map"
        let _ ← sourceMap.getObj?.toOption
        let program ← field j "program"
        let data ← (foldJson [hex, whitespace, magnitude, decode] program).atom.statement
        checkStmt [] .scalar data

def decodeText (text : String) : Option (Stmt [] .scalar) :=
  Json.parse text |>.toOption.bind decodeDocument

end CssDerivation.TypedCodec
