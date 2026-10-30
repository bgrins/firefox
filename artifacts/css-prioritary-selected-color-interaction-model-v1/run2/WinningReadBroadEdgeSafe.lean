import Interaction
open SelectionInteraction
example : cycleFor (selectedReads .light [0]) (SelectedColor.possibleColor [.ident, .color]) = false := by decide
