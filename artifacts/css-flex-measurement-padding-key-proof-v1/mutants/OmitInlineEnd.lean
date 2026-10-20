import BaselineWitness
open MeasurementPadding
example : omitInlineEnd (input 0) {(input 0) with borderPadding.inlineEnd := 1} = false := by decide +kernel
