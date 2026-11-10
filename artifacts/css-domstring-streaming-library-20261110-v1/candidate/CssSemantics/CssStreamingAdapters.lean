import CssSemantics.CssStreamingPair
import CssSemantics.CssDomStringInputLaws

namespace CssSemantics.Streaming

open CssSemantics

def utf16 : Machine DomString.CodeUnit CodePointInput.CodePoint where
  holds := fun unit => decide (DomString.Leading unit)
  combine := fun first second =>
    if pair : DomString.Leading first ∧ DomString.Trailing second then
      some (DomString.pairPoint first second pair.1 pair.2)
    else none
  single := DomString.unitPoint
  unheld := by
    intro first notHeld second
    by_cases lead : DomString.Leading first
    · simp [lead] at notHeld
    · simp [lead]

def css : Machine CodePointInput.CodePoint Char where
  holds := fun point => point.val == 0x0d
  combine := fun first second =>
    if first.val = 0x0d ∧ second.val = 0x0a then some '\n' else none
  single := CodePointInput.point
  unheld := by
    intro first notHeld second
    simp only [beq_eq_false_iff_ne] at notHeld
    simp [notHeld]

def admittedChunks (input : List (List Nat)) : Option (List (List DomString.CodeUnit)) :=
  input.mapM fun chunk => chunk.mapM DomString.unitOfNat?

def decodeValues (input : List (List Nat)) : Option (List Nat) :=
  (admittedChunks input).map fun chunks => (stream utf16 chunks).map Fin.val

end CssSemantics.Streaming
