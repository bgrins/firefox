import Interaction
open SelectionInteraction
example : cycleFor (selectedReads [0]) (SelectedColor.possibleColor [.ident, .color]) = false := by decide
