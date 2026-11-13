import FlexPolicy.Model

namespace FlexPolicy

def UniversalTarget : Prop :=
  ∀ (α : Type) (size : α → Rat) threshold gap limit input,
    threshold < limit → patched size threshold gap limit input =
      FlexCollect.collect size threshold gap input

def WorkerTarget : Prop :=
  ∀ (α : Type) (size : α → Rat) threshold gap limit current total input,
    threshold < limit → Ready size threshold gap current →
    total = FlexCollect.span size gap current →
    loop size gap (patchedBreak threshold limit) current total input =
      FlexCollect.collect size threshold gap (current ++ input)

def CounterexampleTarget : Prop :=
  old id 100 0 1000 ([150, -50] : List Rat) = [[150, -50]] ∧
  patched id 100 0 1000 ([150, -50] : List Rat) = [[150], [-50]] ∧
  ¬FlexCollect.Collected id 100 0 ([150, -50] : List Rat)
    (old id 100 0 1000 [150, -50])

end FlexPolicy
