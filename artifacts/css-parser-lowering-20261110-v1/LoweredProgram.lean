import ParserLowering
import NumberTree

namespace CssParserLowering

open CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer

def resultOption (result : Option α × State) : Option (α × State) :=
  result.1.map fun value => (value, result.2)


def executeNumber (state : State) : Option (Exact × State) :=
  (resultOption (run (lower numberTree) state)).map fun (parts, next) => (project parts, next)


end CssParserLowering
