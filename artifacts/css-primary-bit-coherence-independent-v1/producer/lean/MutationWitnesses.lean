import Witnesses

namespace PrimaryBit.MutationWitnesses
open Witnesses

def clearPointerOnly (s : State) (c : Content) : State := publish s c none
def markAliasTarget (s : State) (c : Content) (f : Frame) : State :=
  publish (writeBit s f true) c (some f)

theorem omitted_clear_differs :
    (clearPointerOnly one 0).bit 0 = true ∧
    (setPrimary layout one 0 none).bit 0 = false := by decide

theorem missing_area_guard_differs :
    (markAliasTarget one 1 3).bit 3 = true ∧
    (setPrimary layout one 1 (some 3)).bit 3 = false := by decide

theorem omitted_publish_differs :
    (beginOwn world 0).frames.pointer 0 = none ∧
    (ownProtocol world 0 0).frames.pointer 0 = some 0 := by decide

end PrimaryBit.MutationWitnesses
