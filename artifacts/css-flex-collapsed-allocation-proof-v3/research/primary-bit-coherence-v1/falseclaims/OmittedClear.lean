import MutationWitnesses
open PrimaryBit PrimaryBit.Witnesses PrimaryBit.MutationWitnesses
example : (clearPointerOnly one 0).bit 0 = (setPrimary layout one 0 none).bit 0 := by decide
