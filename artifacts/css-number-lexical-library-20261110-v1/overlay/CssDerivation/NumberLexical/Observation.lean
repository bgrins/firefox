import CssDerivation.Examples.NumberDocumentExecution
import CssDerivation.NumberLexical.ByteAdapter

namespace CssNumberLexicalBridge
open CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer CssDerivation.ParserJson

structure Observation where
  consumed : List Nat
  rest : List Nat
  integerDigits : List Nat
  fractionDigits : List Nat
  exponentDigits : List Nat
  hasSign : Bool
  isInteger : Bool
  deriving DecidableEq, Repr

def observeParts (source : List Char) (parts : NumberShape.Value) (rest : List Char) : Observation :=
  ⟨codes (source.take (source.length - rest.length)), codes rest, codes parts.2.1,
    codes (parts.2.2.1.getD []), codes ((parts.2.2.2.map Prod.snd).getD []),
    parts.1.isSome, parts.2.2.1.isNone && parts.2.2.2.isNone⟩

def observeNative (result : NumericLexical.Result) : Observation :=
  ⟨result.text.map Fin.val, result.rest.map Fin.val, result.integralDigits.map Fin.val,
    result.fractionalDigits.map Fin.val, result.exponentDigits.map Fin.val,
    result.hasSign, result.isInteger⟩

def observeDocument (document : Lean.Json) (state : State) : Option Observation := do
  let (value, next) ← executeDocument NumberShape document state
  let parts ← value
  some (observeParts state.input parts next.input)

def admitted (source : List NumericDigits.Byte) : Prop :=
  NormalizedASCII source ∧ NumericEntry.nativeStart source = true

end CssNumberLexicalBridge
