import CssDerivation.NumberLexical.Observation

namespace CssNumberLexicalBridge
open Lean NumericDigits

def asciiBytes (source : String) : Option (List Byte) :=
  source.toList.mapM fun c =>
    if h : c.toNat < 128 then some ⟨c.toNat, Nat.lt_trans h (by decide)⟩ else none

def admittedBytes (source : String) : Option (List Byte) := do
  let bytes ← asciiBytes source
  if bytes.all (fun b => b.val != 0 && b.val != 13 && b.val != 12) && NumericEntry.nativeStart bytes
  then some bytes else none

def observationJson (value : Observation) : Json :=
  Json.arr #[toJson value.consumed, toJson value.rest, toJson value.integerDigits,
    toJson value.fractionDigits, toJson value.exponentDigits, toJson value.hasSign, toJson value.isInteger]

def readCases (path : String) : IO (Array (String × Bool)) := do
  let text ← IO.FS.readFile path
  let json ← IO.ofExcept (Json.parse text)
  IO.ofExcept (fromJson? json)

def refusalJson (source : String) (oldError : Bool) : Json :=
  Json.arr #[toJson source, toJson oldError, toJson "outside-normalized-ascii-number-entry"]

def resultJson (source : String) (oldError : Bool) (value : Observation) (newError : Bool) : Json :=
  Json.arr #[toJson source, toJson oldError, observationJson value, toJson newError]

end CssNumberLexicalBridge
