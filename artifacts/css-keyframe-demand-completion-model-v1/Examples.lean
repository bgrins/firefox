import Demand

namespace DemandCompletion.Examples

def initial : Environment
  | .provider 0 => .known [20]
  | .provider 1 => .pending
  | .attribute 0 0 => .pending
  | .prioritary 0 => .pending
  | _ => .invalid

def completed : Environment := fillPending initial (fun _ => [40])

def unused : Expression :=
  .reference (.provider 0) (.reference (.provider 1) .invalid)

def taken : Expression :=
  .reference (.provider 2) (.reference (.provider 1) .invalid)

def invalidFirst : Expression :=
  .sequence (.reference (.provider 2) .invalid) (.reference (.provider 1) .invalid)

def pendingFirst : Expression :=
  .sequence (.reference (.provider 1) .invalid) (.reference (.provider 2) .invalid)

def stale : ProviderState :=
  ⟨fun key => key == .provider 1, fun _ => some [7]⟩

def pendingAsInvalid (env : Environment) : Environment :=
  fun key => match env key with
    | .pending => .invalid
    | ready => ready

def cachedFirst (state : ProviderState) (key : Key) : Slot :=
  match state.cached key with
  | some value => .known value
  | none => if state.pending key then .pending else .invalid

def eagerReference (env : Environment) (key : Key) (fallback : Expression) : Run :=
  match evaluate env fallback with
  | .demand request trace => .demand request trace
  | _ => evaluate env (.reference key fallback)

def changedInvalid : Environment := fun key =>
  if key == .provider 2 then .known [40] else initial key

example : lookup stale (.provider 1) = .pending := by decide +kernel

example : evaluate initial unused = .value [20] [.provider 0] := by decide +kernel

example : evaluate initial taken = .demand (.provider 1) [.provider 2, .provider 1] := by
  decide +kernel

example : evaluate initial (.reference (.provider 2) (.literal [7])) =
    .value [7] [.provider 2] := by decide +kernel

example : evaluate initial invalidFirst = .invalid [.provider 2] := by decide +kernel

example : evaluate initial pendingFirst = .demand (.provider 1) [.provider 1] := by
  decide +kernel

example : evaluate completed unused = evaluate initial unused := by decide +kernel

example : evaluate completed invalidFirst = evaluate initial invalidFirst := by decide +kernel

example : evaluate completed taken = .value [40] [.provider 2, .provider 1] := by
  decide +kernel

example : evaluate initial (.reference (.attribute 0 0) (.literal [7])) =
    .demand (.attribute 0 0) [.attribute 0 0] := by decide +kernel

example : evaluate initial (.reference (.attribute 0 1) (.literal [7])) =
    .value [7] [.attribute 0 1] := by decide +kernel

example : evaluate initial (.sequence (.literal [20]) (.reference (.prioritary 0) .invalid)) =
    .demand (.prioritary 0) [.prioritary 0] := by decide +kernel

example : evaluate initial (.sequence (.reference (.provider 0) .invalid)
    (.reference (.provider 0) .invalid)) =
    .value [20, 20] [.provider 0, .provider 0] := by decide +kernel

example : evaluate initial (.reference (.provider 2)
    (.sequence (.reference (.provider 0) .invalid) (.reference (.provider 3) .invalid))) =
    .invalid [.provider 2, .provider 0, .provider 3] := by decide +kernel

example : evaluate (pendingAsInvalid initial) (.reference (.provider 1) (.literal [7])) =
    .value [7] [.provider 1] := by decide +kernel

example : evaluate (cachedFirst stale) (.reference (.provider 1) (.literal [7])) =
    .value [7] [.provider 1] := by decide +kernel

theorem example_completion_coherent : Refines initial completed :=
  fillPending_refines initial _

theorem example_completion_ready : Complete completed :=
  fillPending_complete initial _

end DemandCompletion.Examples
