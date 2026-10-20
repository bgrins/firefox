import BaselineWitness
open MeasurementPadding
example : omitBlockStart (input 0) {(input 0) with borderPadding.blockStart := 1} = false := by decide +kernel
