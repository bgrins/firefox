import MutationWitnesses
open PrimaryBit PrimaryBit.Witnesses PrimaryBit.MutationWitnesses
example : (beginOwn world 0).frames.pointer 0 = (ownProtocol world 0 0).frames.pointer 0 := by decide
