import Lean

namespace CssDerivation

def validEscape (first second : Option Char) : Bool :=
  if first != some (Char.ofNat 92) then false else
  if second == some (Char.ofNat 10) then false else
  true

end CssDerivation
