import CssDerivation.Codec.Document.Profile

namespace CssDerivation.DocumentSchema.Examples
open Lean FirstOrder TypedCodec JsonSchema

def document (definitions program : Json) (sourceMap : Json := .mkObj []) : Json :=
  .mkObj [("schema", 1), ("definitions", definitions), ("program", program), ("source_map", sourceMap)]

def nextSignature : Signature := ⟨"next", .nat, .scalar⟩
def nextBody : Json := nodeJson "scalarOf" [nodeJson "add" [nodeJson "var" [0], nodeJson "nat" [1]]]
def nextDefinitions : Json := .mkObj [("next", nextBody)]
def nextProgram : Json := nodeJson "letE" [nodeJson "nat" [64], nodeJson "ret" [nodeJson "use" [.str "next"]]]
def nextDocument : Json := document nextDefinitions nextProgram

def emptyDocument : Json := document (.mkObj []) (nodeJson "ret" [nodeJson "scalar" [65]])
def duplicateProfile : List Signature := [nextSignature, nextSignature]
def duplicateExploit : Json := .mkObj [("next", nextBody), ("spare", nextBody)]
def wrongResultProfile : List Signature := [⟨"next", .nat, .nat⟩]

def foldBody : Json := nodeJson "foldNat" [
  nodeJson "cons" [nodeJson "scalar" [120], nodeJson "nil" []], nodeJson "nat" [3],
  nodeJson "add" [nodeJson "var" [1], nodeJson "var" [2]]]
def foldDocument : Json := document (.mkObj [("sum", foldBody)])
  (nodeJson "letE" [nodeJson "nat" [7], nodeJson "ret" [nodeJson "scalarOf" [nodeJson "use" [.str "sum"]]]])

def valueOf (signatures : List Signature) (j : Json) : Option Nat :=
  (readDocumentWith signatures .scalar j).map (fun p => (FirstOrder.execute p []).value.toNat)

end CssDerivation.DocumentSchema.Examples
