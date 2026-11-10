import Lean

namespace CssDerivation

def validEscape (first second third : Option Char) : Bool :=
  (if ((!(first == some (Char.ofNat 92)))) then false else (if ((second == some (Char.ofNat 10))) then false else true))

def observeValidEscape (source : List Char) : Bool × List Char :=
  (validEscape source.head? source.tail.head? source.tail.tail.head?, source)

end CssDerivation
