import MutationWitnesses
open PrimaryBit PrimaryBit.Witnesses PrimaryBit.MutationWitnesses
example : (markAliasTarget one 1 3).bit 3 = (setPrimary layout one 1 (some 3)).bit 3 := by decide
