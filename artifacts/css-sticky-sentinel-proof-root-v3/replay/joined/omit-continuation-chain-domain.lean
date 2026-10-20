import StickyUpdate

namespace StickyJoined
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle StickyUpdate

def ActionSafe (w : World) (input : Input) (chains overs : Nat → List Nat) : Prop :=
  match input.action with
  | 0 => ComputeSafe w input.target .current
  | 1 => ComputeSafe w input.target .ignoreScroll
  | 2 => TranslationSafe w input.target
  | 3 => True ∧
      ContinuationSafe w input.target (chains input.target)
  | 4 => ReadyList w.nodes input.reflow chains overs input.primaries ∧
      BatchSafe input.reflow chains w.nodes input.primaries
  | 5 => FrameSafe w input.target
  | _ => ComputeSafe w input.target .current

def machineAction (repeatLookup : Bool) (input : Input) : StateM World (Option Point) := do
  match input.action with
  | 0 => return some (← StickyLifecycle.compute machinePosition repeatLookup input.target .current)
  | 1 => return some (← StickyLifecycle.compute machinePosition repeatLookup input.target .ignoreScroll)
  | 2 => return some (← machineTranslation repeatLookup input.target)
  | 3 => machineContinuations repeatLookup input.target; return none
  | 4 => machineUpdate repeatLookup input.reflow input.primaries; return none
  | 5 => return some (← machineFrame repeatLookup input.target)
  | _ =>
    let p ← StickyLifecycle.compute machinePosition repeatLookup input.target .current
    let q ← normal input.target
    return some ⟨if p.y != q.y then 1 else 0, 0⟩

def machineRun (repeatLookup : Bool) (input : Input) : Option Point × World :=
  (machineAction repeatLookup input).run ⟨input.nodes, #[], false⟩

end StickyJoined
