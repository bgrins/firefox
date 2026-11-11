import CssDerivation.Codec.Json.Schema

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

mutual
  def readExpr (aliases : Aliases) (j : Json) : Option { e : DataExpr // ExprSchema aliases j e } :=
    match j with
    | .obj ⟨⟨.inner outer "op" (.str op) .leaf (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf)⟩⟩ => do
        let ⟨e, proof⟩ ← readExprArguments aliases op args
        some ⟨e, .node (.rightOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) .leaf (.inner inner "op" (.str op) .leaf .leaf)⟩⟩ => do
        let ⟨e, proof⟩ ← readExprArguments aliases op args
        some ⟨e, .node (.rightArgs outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "op" (.str op) (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf) .leaf⟩⟩ => do
        let ⟨e, proof⟩ ← readExprArguments aliases op args
        some ⟨e, .node (.leftOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) (.inner inner "op" (.str op) .leaf .leaf) .leaf⟩⟩ => do
        let ⟨e, proof⟩ ← readExprArguments aliases op args
        some ⟨e, .node (.leftArgs outer inner op args) proof⟩
    | _ => none
  termination_by sizeOf j

  def readExprArguments (aliases : Aliases) (op : String) (args : List Json) :
      Option { e : DataExpr // ExprArguments aliases op args e } :=
    match op, args with
    | "nat", [j] =>
      match h : j.getNat? with
      | .ok n => some ⟨.nat n, .nat h⟩
      | .error _ => none
    | "scalar", [j] =>
      match h : j.getNat? with
      | .ok n => if valid : scalarAllowed n then some ⟨.scalar (Char.ofNat n), .scalar h valid⟩ else none
      | .error _ => none
    | "bool", [.bool b] => some ⟨.bool b, .bool b⟩
    | "var", [j] =>
      match h : j.getNat? with
      | .ok n => some ⟨.var n, .var h⟩
      | .error _ => none
    | "nil", [] => some ⟨.nil, .nil⟩
    | "unit", [] => some ⟨.unit, .unit⟩
    | "use", [.str name] =>
      match h : aliases.find? (fun entry => entry.1 == name) with
      | none => none
      | some (found, head, body) =>
        if same : found = name then some ⟨.scope head body, .use (by simpa [same] using h)⟩ else none
    | "code", [ja] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        some ⟨.code a, .code ha⟩
    | "scalarOf", [ja] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        some ⟨.scalarOf a, .scalarOf ha⟩
    | "add", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.add a b, .add ha hb⟩
    | "sub", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.sub a b, .sub ha hb⟩
    | "mul", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.mul a b, .mul ha hb⟩
    | "leNat", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.leNat a b, .leNat ha hb⟩
    | "ltNat", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.ltNat a b, .ltNat ha hb⟩
    | "eqNat", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.eqNat a b, .eqNat ha hb⟩
    | "leChar", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.leChar a b, .leChar ha hb⟩
    | "eqChar", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.eqChar a b, .eqChar ha hb⟩
    | "and", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.and a b, .and ha hb⟩
    | "or", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.or a b, .or ha hb⟩
    | "cons", [ja, jb] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        some ⟨.cons a b, .cons ha hb⟩
    | "ite", [ja, jb, jc] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        let ⟨c, hc⟩ ← readExpr aliases jc
        some ⟨.ite a b c, .ite ha hb hc⟩
    | "foldNat", [ja, jb, jc] => do
        let ⟨a, ha⟩ ← readExpr aliases ja
        let ⟨b, hb⟩ ← readExpr aliases jb
        let ⟨c, hc⟩ ← readExpr aliases jc
        some ⟨.foldNat a b c, .foldNat ha hb hc⟩
    | _, _ => none
  termination_by sizeOf args

  def readStmt (aliases : Aliases) (j : Json) : Option { p : DataStmt // StmtSchema aliases j p } :=
    match j with
    | .obj ⟨⟨.inner outer "op" (.str op) .leaf (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf)⟩⟩ => do
        let ⟨p, proof⟩ ← readStmtArguments aliases op args
        some ⟨p, .node (.rightOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) .leaf (.inner inner "op" (.str op) .leaf .leaf)⟩⟩ => do
        let ⟨p, proof⟩ ← readStmtArguments aliases op args
        some ⟨p, .node (.rightArgs outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "op" (.str op) (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf) .leaf⟩⟩ => do
        let ⟨p, proof⟩ ← readStmtArguments aliases op args
        some ⟨p, .node (.leftOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) (.inner inner "op" (.str op) .leaf .leaf) .leaf⟩⟩ => do
        let ⟨p, proof⟩ ← readStmtArguments aliases op args
        some ⟨p, .node (.leftArgs outer inner op args) proof⟩
    | _ => none
  termination_by sizeOf j

  def readStmtArguments (aliases : Aliases) (op : String) (args : List Json) :
      Option { p : DataStmt // StmtArguments aliases op args p } :=
    match op, args with
    | "ret", [je] => do
      let ⟨e, he⟩ ← readExpr aliases je
      some ⟨.ret e, .ret he⟩
    | "letE", [je, jp] => do
      let ⟨e, he⟩ ← readExpr aliases je
      let ⟨p, hp⟩ ← readStmt aliases jp
      some ⟨.letE e p, .letE he hp⟩
    | "read", [ja, jb] => do
      let ⟨a, ha⟩ ← readStmt aliases ja
      let ⟨b, hb⟩ ← readStmt aliases jb
      some ⟨.read a b, .read ha hb⟩
    | "scan", [jn, je, jp] =>
      match hn : jn.getNat? with
      | .error _ => none
      | .ok n => do
        let ⟨e, he⟩ ← readExpr aliases je
        let ⟨p, hp⟩ ← readStmt aliases jp
        some ⟨.scan n e p, .scan hn he hp⟩
    | "raiseError", [jp] => do
      let ⟨p, hp⟩ ← readStmt aliases jp
      some ⟨.raiseError p, .raiseError hp⟩
    | "branch", [je, ja, jb] => do
      let ⟨e, he⟩ ← readExpr aliases je
      let ⟨a, ha⟩ ← readStmt aliases ja
      let ⟨b, hb⟩ ← readStmt aliases jb
      some ⟨.branch e a b, .branch he ha hb⟩
    | _, _ => none
  termination_by sizeOf args
end

def readExprData (aliases : Aliases) (j : Json) : Option DataExpr :=
  (readExpr aliases j).map Subtype.val

def readStmtData (aliases : Aliases) (j : Json) : Option DataStmt :=
  (readStmt aliases j).map Subtype.val

end CssDerivation.JsonSchema
