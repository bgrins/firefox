import BaselineWitness
open MeasurementPadding
example : omitInlineStart (input 0) {(input 0) with borderPadding.inlineStart := 1} = false := by decide +kernel
