import StickyUpdate

namespace StickyJoined
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle StickyUpdate

def ActionSafe (w : World) (input : Input) (chains overs : Nat → List Nat) : Prop :=
  match input.action with
  | 0 => ComputeSafe w input.target .current
  | 1 => ComputeSafe w input.target .ignoreScroll
  | 2 => TranslationSafe w input.target
  | 3 => Chain w.nodes (some input.target) (chains input.target) ∧
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

theorem compute_ordered_exact (repeatLookup : Bool) (i : Nat) (space : Space)
    (w : World) (h : ComputeSafe w i space) :
    (StickyLifecycle.compute machinePosition repeatLookup i space).run w =
      (StickyLifecycle.compute orderedPosition repeatLookup i space).run w := by
  rw [projection_refinement]
  exact machine_compute_exact _ _ _ _ h

theorem all_entry_machine_refinement (repeatLookup : Bool) (input : Input)
    (w : World) (chains overs : Nat → List Nat) (h : ActionSafe w input chains overs) :
    (machineAction repeatLookup input).run w =
      (action orderedPosition repeatLookup input).run w := by
  unfold machineAction action
  split <;> simp_all only [ActionSafe]
  · next he =>
      have hc := compute_ordered_exact repeatLookup input.target .current w
        (by simpa [ActionSafe, he] using h)
      change (let p := (StickyLifecycle.compute machinePosition repeatLookup input.target .current).run w
              (some p.1, p.2)) = _
      rw [hc]
      rfl
  · next he =>
      have hc := compute_ordered_exact repeatLookup input.target .ignoreScroll w
        (by simpa [ActionSafe, he] using h)
      change (let p := (StickyLifecycle.compute machinePosition repeatLookup input.target .ignoreScroll).run w
              (some p.1, p.2)) = _
      rw [hc]
      rfl
  · next he =>
      have hc := machine_translation_exact repeatLookup input.target w
        (by simpa [ActionSafe, he] using h)
      change (let p := (machineTranslation repeatLookup input.target).run w
              (some p.1, p.2)) = _
      rw [hc]
      rfl
  · next he =>
      have hs : Chain w.nodes (some input.target) (chains input.target) ∧
          ContinuationSafe w input.target (chains input.target) := by simpa [ActionSafe, he] using h
      have hc := machine_continuations_exact repeatLookup input.target w _ hs.1 hs.2
      change (none, ((machineContinuations repeatLookup input.target).run w).2) = _
      rw [hc]
      rfl
  · next he =>
      have hs : ReadyList w.nodes input.reflow chains overs input.primaries ∧
          BatchSafe input.reflow chains w.nodes input.primaries := by simpa [ActionSafe, he] using h
      have hc := machine_update_exact repeatLookup input.reflow input.primaries w chains overs hs.1 hs.2
      change (none, ((machineUpdate repeatLookup input.reflow input.primaries).run w).2) = _
      rw [hc]
      rfl
  · next he =>
      have hc := machine_frame_exact repeatLookup input.target w
        (by simpa [ActionSafe, he] using h)
      change (let p := (machineFrame repeatLookup input.target).run w
              (some p.1, p.2)) = _
      rw [hc]
      rfl
  · next =>
      have hs : ComputeSafe w input.target .current := by
        exact h
      have hc := compute_ordered_exact repeatLookup input.target .current w hs
      change (let p := (StickyLifecycle.compute machinePosition repeatLookup input.target .current).run w
              let q := (normal input.target).run p.2
              (some (Point.mk (if p.1.y != q.1.y then 1 else 0) 0), q.2)) = _
      rw [hc]
      rfl

def machineRun (repeatLookup : Bool) (input : Input) : Option Point × World :=
  (machineAction repeatLookup input).run ⟨input.nodes, #[], false⟩

theorem full_run_machine_refinement (repeatLookup : Bool) (input : Input)
    (chains overs : Nat → List Nat)
    (h : ActionSafe ⟨input.nodes, #[], false⟩ input chains overs) :
    machineRun repeatLookup input = run orderedPosition repeatLookup input :=
  all_entry_machine_refinement repeatLookup input _ chains overs h

end StickyJoined
