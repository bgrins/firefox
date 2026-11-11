import CssDerivation.Codec.Parser.Document
import CssDerivation.Examples.NumberBackend

namespace CssDerivation.ParserJson
open Lean ParserIR NumberTransfer

def projectRun (p : Parser NumberShape) (state : State) : Option Exact × State :=
  let result := CssParserLowering.run (CssParserLowering.lower p) state
  (result.1.map project, result.2)

def executeNumberDocument (j : Json) (state : State) : Option (Option Exact × State) :=
  (readDocument NumberShape j).map (fun p => projectRun p state)

def numberValue (j : Json) (state : State) : Option (Exact × State) :=
  (executeNumberDocument j state).bind CssParserLowering.resultOption

def changedNumberTree : Parser NumberShape :=
  .pair signTree (.pair digitsTree (.pair (.optional fractionTree)
    (.optional (.right (.scan exponentPredicate) (.pair signTree nonemptyDigitsTree)))))

end CssDerivation.ParserJson
