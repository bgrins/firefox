import Links
open DeclarationLinks
open DeclarationCapacity (font color)
example : let s := build 5 0 (empty 5) [font, color, font]; read 5 {s with head := s.tail} = [0, 2] := by decide
