import CssDerivation.Codec.Parser.Schema

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR

mutual
  def readParser (j : Json) : Option (Parsed j) :=
    match j with
    | .obj ⟨⟨.inner outer "op" (.str op) .leaf (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf)⟩⟩ => do
      let ⟨shape, p, proof⟩ ← readArguments op args
      some ⟨shape, p, .node (.rightOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) .leaf (.inner inner "op" (.str op) .leaf .leaf)⟩⟩ => do
      let ⟨shape, p, proof⟩ ← readArguments op args
      some ⟨shape, p, .node (.rightArgs outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "op" (.str op) (.inner inner "args" (.arr ⟨args⟩) .leaf .leaf) .leaf⟩⟩ => do
      let ⟨shape, p, proof⟩ ← readArguments op args
      some ⟨shape, p, .node (.leftOp outer inner op args) proof⟩
    | .obj ⟨⟨.inner outer "args" (.arr ⟨args⟩) (.inner inner "op" (.str op) .leaf .leaf) .leaf⟩⟩ => do
      let ⟨shape, p, proof⟩ ← readArguments op args
      some ⟨shape, p, .node (.leftArgs outer inner op args) proof⟩
    | _ => none
  termination_by sizeOf j

  def readArguments (op : String) (args : List Json) : Option (ParsedArguments op args) :=
    match op, args with
    | "legacy", [jt, jp] => do
      let ⟨t, typeProof⟩ ← readType jt
      let ⟨p, proof⟩ ← readLegacy t jp
      some ⟨.base t, .legacy p, .legacy typeProof proof⟩
    | "take", [j] => do
      let ⟨predicate, proof⟩ ← readPredicate j
      some ⟨.base .scalar, .take predicate, .take proof⟩
    | "scan", [j] => do
      let ⟨predicate, proof⟩ ← readPredicate j
      some ⟨.base .chars, .scan predicate, .scan proof⟩
    | "nonempty", [j] =>
      match readParser j with
      | some ⟨.base .chars, p, proof⟩ => some ⟨.base .chars, .nonempty p, .nonempty proof⟩
      | _ => none
    | "pair", [ja, jb] => do
      let ⟨a, pa, proofA⟩ ← readParser ja
      let ⟨b, pb, proofB⟩ ← readParser jb
      some ⟨.pair a b, .pair pa pb, .pair proofA proofB⟩
    | "right", [ja, jb] => do
      let ⟨a, pa, proofA⟩ ← readParser ja
      let ⟨b, pb, proofB⟩ ← readParser jb
      some ⟨b, .right pa pb, .right proofA proofB⟩
    | "optional", [j] => do
      let ⟨shape, p, proof⟩ ← readParser j
      some ⟨.optional shape, .optional p, .optional proof⟩
    | _, _ => none
  termination_by sizeOf args
end

def expectParser (shape : Shape) {j : Json} (parsed : Parsed j) :
    Option {p : Parser shape // ParserSchema j p} :=
  match parsed with
  | ⟨actual, p, proof⟩ => if h : actual = shape then some (h ▸ ⟨p, proof⟩) else none

def decodeParser (shape : Shape) (j : Json) : Option (Parser shape) :=
  ((readParser j).bind (expectParser shape)).map Subtype.val

end CssDerivation.ParserJson
