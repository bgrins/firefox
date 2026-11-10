import StatefulIR

namespace CssDerivation

def isHex (c : Char) : Bool := (Char.ofNat 48 ≤ c && c ≤ Char.ofNat 57) || (Char.ofNat 65 ≤ c && c ≤ Char.ofNat 70) || (Char.ofNat 97 ≤ c && c ≤ Char.ofNat 102)
def isWhitespace (c : Char) : Bool := c == Char.ofNat 10 || c == Char.ofNat 9 || c == Char.ofNat 32

def digitValue (c : Char) : Nat :=
  if c ≤ Char.ofNat 57 then c.toNat - 48
  else if c ≤ Char.ofNat 70 then c.toNat - 55
  else c.toNat - 87

def magnitude (digits : List Char) : Nat :=
  digits.foldl (fun value c => value * 16 + digitValue c) 0

def decode (value : Nat) : Char :=
  if value = 0 ∨ (55296 ≤ value ∧ value ≤ 57343) ∨ 1114111 < value then Char.ofNat 65533 else Char.ofNat value

def escape : Program Char :=
  .bind .read fun first =>
    match first with
    | none => .bind .raiseError fun _ => .pure (Char.ofNat 65533)
    | some c => .branch (isHex c)
        (.bind (.scan 5 isHex) fun digits =>
          .bind (.scan 1 isWhitespace) fun _ =>
            .pure (decode (magnitude (c :: digits))))
        (.pure c)

end CssDerivation
