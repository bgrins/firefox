import Links
open DeclarationLinks DeclarationCapacity
example : let s := build 5 0 (empty 5) [font, color, font]; read 5 {s with next := fun _ => 0} = [0, 2] := by decide
