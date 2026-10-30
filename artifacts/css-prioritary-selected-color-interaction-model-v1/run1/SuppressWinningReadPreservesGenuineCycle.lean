import Interaction
open SelectionInteraction
example : cycleFor [] (SelectedColor.depends (SelectedColor.select [.color, .ident] .canvas)) = cycleFor winnerReads (SelectedColor.depends (SelectedColor.select [.color, .ident] .canvas)) := by decide
