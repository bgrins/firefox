import Lean

namespace CssDerivation

def numberStart (first second third : Option Char) : Bool :=
  (if ((first == some (Char.ofNat 43)) || (first == some (Char.ofNat 45))) then (if ((second.any (fun c => Char.ofNat 48 ≤ c && c ≤ Char.ofNat 57))) then true else (if ((second == some (Char.ofNat 46)) && (third.any (fun c => Char.ofNat 48 ≤ c && c ≤ Char.ofNat 57))) then true else false)) else (if ((first == some (Char.ofNat 46))) then (if ((second.any (fun c => Char.ofNat 48 ≤ c && c ≤ Char.ofNat 57))) then true else false) else (if ((first.any (fun c => Char.ofNat 48 ≤ c && c ≤ Char.ofNat 57))) then true else false)))

def observeNumberStart (source : List Char) : Bool × List Char :=
  (numberStart source.head? source.tail.head? source.tail.tail.head?, source)

end CssDerivation
