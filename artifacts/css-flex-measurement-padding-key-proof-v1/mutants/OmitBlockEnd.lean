import BaselineWitness
open MeasurementPadding
example : omitBlockEnd (input 0) {(input 0) with borderPadding.blockEnd := 1} = false := by decide +kernel
