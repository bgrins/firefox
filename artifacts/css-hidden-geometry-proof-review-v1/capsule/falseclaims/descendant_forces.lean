import Hidden
open Hidden
example : let w : TwoFrames := ⟨⟨true, zero, none⟩, ⟨false, ⟨8, 9⟩, none⟩⟩; descendantQuery (fun _ => ⟨warm, warm⟩) w ≠ w := by decide
