import Init

namespace DemandCompletion

inductive Key where
  | provider (name : Nat)
  | attribute (ns name : Nat)
  | prioritary (id : Nat)
  deriving DecidableEq, Repr

abbrev Value := List Nat

inductive Slot where
  | known (value : Value)
  | invalid
  | pending
  deriving DecidableEq, Repr

abbrev Environment := Key → Slot

structure ProviderState where
  pending : Key → Bool
  cached : Key → Option Value

def lookup (state : ProviderState) (key : Key) : Slot :=
  if state.pending key then .pending
  else match state.cached key with
    | some value => .known value
    | none => .invalid

inductive Expression where
  | literal (value : Value)
  | invalid
  | reference (key : Key) (fallback : Expression)
  | sequence (left right : Expression)
  deriving DecidableEq, Repr

inductive Run where
  | value (tokens : Value) (trace : List Key)
  | invalid (trace : List Key)
  | demand (key : Key) (trace : List Key)
  deriving DecidableEq, Repr

def Run.trace : Run → List Key
  | .value _ trace | .invalid trace | .demand _ trace => trace

def Run.settled : Run → Bool
  | .value .. | .invalid .. => true
  | .demand .. => false

def prepend (prior : List Key) : Run → Run
  | .value value trace => .value value (prior ++ trace)
  | .invalid trace => .invalid (prior ++ trace)
  | .demand key trace => .demand key (prior ++ trace)

def sequence (first : Run) (next : Unit → Run) : Run :=
  match first with
  | .invalid trace => .invalid trace
  | .demand key trace => .demand key trace
  | .value value trace =>
    match next () with
    | .value rest reached => .value (value ++ rest) (trace ++ reached)
    | .invalid reached => .invalid (trace ++ reached)
    | .demand key reached => .demand key (trace ++ reached)

def evaluate (env : Environment) : Expression → Run
  | .literal value => .value value []
  | .invalid => .invalid []
  | .reference key fallback =>
    match env key with
    | .known value => .value value [key]
    | .invalid => prepend [key] (evaluate env fallback)
    | .pending => .demand key [key]
  | .sequence left right => sequence (evaluate env left) (fun _ => evaluate env right)

def Refines (old current : Environment) : Prop :=
  ∀ key, old key ≠ .pending → current key = old key

def Complete (env : Environment) : Prop := ∀ key, env key ≠ .pending

def fillPending (env : Environment) (values : Key → Value) : Environment :=
  fun key => match env key with
    | .pending => .known (values key)
    | completed => completed

theorem fillPending_refines (env : Environment) (values : Key → Value) :
    Refines env (fillPending env values) := by
  intro key known
  cases state : env key <;> simp_all [fillPending]

theorem fillPending_complete (env : Environment) (values : Key → Value) :
    Complete (fillPending env values) := by
  intro key
  cases slot : env key <;> simp [fillPending, slot]

theorem pending_masks_cache (state : ProviderState) (key : Key)
    (pending : state.pending key = true) : lookup state key = .pending := by
  simp [lookup, pending]

theorem ready_uses_cache (state : ProviderState) (key : Key)
    (ready : state.pending key = false) :
    lookup state key = ((state.cached key).map Slot.known).getD .invalid := by
  cases cached : state.cached key <;> simp [lookup, ready, cached]

theorem prepend_trace (prior : List Key) (run : Run) :
    (prepend prior run).trace = prior ++ run.trace := by
  cases run <;> rfl

theorem prepend_settled (prior : List Key) (run : Run) :
    (prepend prior run).settled = run.settled := by
  cases run <;> rfl

theorem reference_pending (env : Environment) (key : Key) (fallback : Expression)
    (pending : env key = .pending) :
    evaluate env (.reference key fallback) = .demand key [key] := by
  simp [evaluate, pending]

theorem unused_fallback (env : Environment) (key : Key) (fallback : Expression)
    (value : Value) (known : env key = .known value) :
    evaluate env (.reference key fallback) = .value value [key] := by
  simp [evaluate, known]

theorem invalid_stops_sequence (env : Environment) (left right : Expression)
    (trace : List Key) (invalid : evaluate env left = .invalid trace) :
    evaluate env (.sequence left right) = .invalid trace := by
  simp [evaluate, sequence, invalid]

theorem demand_stops_sequence (env : Environment) (left right : Expression)
    (key : Key) (trace : List Key) (demand : evaluate env left = .demand key trace) :
    evaluate env (.sequence left right) = .demand key trace := by
  simp [evaluate, sequence, demand]

theorem replay_reached (old current : Environment) (expression : Expression)
    (agree : ∀ key ∈ (evaluate old expression).trace, current key = old key) :
    evaluate current expression = evaluate old expression := by
  induction expression with
  | literal value => rfl
  | invalid => rfl
  | reference key fallback ih =>
    have reached : key ∈ (evaluate old (.reference key fallback)).trace := by
      cases slot : old key with
      | known value => simp [evaluate, slot, Run.trace]
      | pending => simp [evaluate, slot, Run.trace]
      | invalid => simp only [evaluate, slot, prepend_trace]; simp
    have same := agree key reached
    cases slot : old key with
    | known value => simp [evaluate, slot, same]
    | pending => simp [evaluate, slot, same]
    | invalid =>
      have child : ∀ name ∈ (evaluate old fallback).trace, current name = old name := by
        intro name member
        apply agree name
        simp [evaluate, slot, prepend_trace, member]
      simp [evaluate, slot, same, ih child]
  | sequence left right ihLeft ihRight =>
    cases first : evaluate old left with
    | invalid trace =>
      have child : ∀ key ∈ (evaluate old left).trace, current key = old key := by
        intro key member
        apply agree key
        simpa [evaluate, sequence, first, Run.trace] using member
      simp [evaluate, sequence, first, ihLeft child]
    | demand key trace =>
      have child : ∀ name ∈ (evaluate old left).trace, current name = old name := by
        intro name member
        apply agree name
        simpa [evaluate, sequence, first, Run.trace] using member
      simp [evaluate, sequence, first, ihLeft child]
    | value value trace =>
      have joined : (evaluate old (.sequence left right)).trace =
          trace ++ (evaluate old right).trace := by
        cases second : evaluate old right <;> simp [evaluate, sequence, first, second, Run.trace]
      have childLeft : ∀ key ∈ (evaluate old left).trace, current key = old key := by
        intro key member
        apply agree key
        rw [joined]
        simp only [first, Run.trace] at member
        exact List.mem_append_left _ member
      have childRight : ∀ key ∈ (evaluate old right).trace, current key = old key := by
        intro key member
        apply agree key
        rw [joined]
        exact List.mem_append_right _ member
      simp only [evaluate]
      rw [ihLeft childLeft, ihRight childRight]

theorem settled_reached_known (env : Environment) (expression : Expression)
    (settled : (evaluate env expression).settled = true) :
    ∀ key ∈ (evaluate env expression).trace, env key ≠ .pending := by
  induction expression with
  | literal value => simp [evaluate, Run.trace]
  | invalid => simp [evaluate, Run.trace]
  | reference key fallback ih =>
    cases slot : env key with
    | pending => simp [evaluate, slot, Run.settled] at settled
    | known value =>
      intro name member
      simp [evaluate, slot, Run.trace] at member
      subst name
      simp [slot]
    | invalid =>
      have childSettled : (evaluate env fallback).settled = true := by
        simpa [evaluate, slot, prepend_settled] using settled
      intro name member
      simp only [evaluate, slot, prepend_trace, List.singleton_append, List.mem_cons] at member
      rcases member with same | nested
      · subst name
        simp [slot]
      · exact ih childSettled name nested
  | sequence left right ihLeft ihRight =>
    cases first : evaluate env left with
    | demand key trace => simp [evaluate, sequence, first, Run.settled] at settled
    | invalid trace =>
      have leftSettled : (evaluate env left).settled = true := by simp [first, Run.settled]
      intro key member
      apply ihLeft leftSettled key
      simpa [evaluate, sequence, first, Run.trace] using member
    | value value trace =>
      have leftSettled : (evaluate env left).settled = true := by simp [first, Run.settled]
      have rightSettled : (evaluate env right).settled = true := by
        cases second : evaluate env right <;> simp_all [evaluate, sequence, Run.settled]
      have joined : (evaluate env (.sequence left right)).trace =
          (evaluate env left).trace ++ (evaluate env right).trace := by
        cases second : evaluate env right <;> simp [evaluate, sequence, first, second, Run.trace]
      intro key member
      rw [joined] at member
      rcases List.mem_append.mp member with before | after
      · exact ihLeft leftSettled key before
      · exact ihRight rightSettled key after

theorem settled_stable_with_trace (old current : Environment) (expression : Expression)
    (coherent : Refines old current) (settled : (evaluate old expression).settled = true) :
    evaluate current expression = evaluate old expression := by
  apply replay_reached
  intro key member
  exact coherent key (settled_reached_known old expression settled key member)

theorem complete_is_settled (env : Environment) (complete : Complete env)
    (expression : Expression) : (evaluate env expression).settled = true := by
  induction expression with
  | literal value => rfl
  | invalid => rfl
  | reference key fallback ih =>
    cases slot : env key with
    | known value => simp [evaluate, slot, Run.settled]
    | invalid => simpa [evaluate, slot, prepend_settled] using ih
    | pending => exact False.elim (complete key slot)
  | sequence left right ihLeft ihRight =>
    cases first : evaluate env left <;> cases second : evaluate env right <;>
      simp_all [evaluate, sequence, Run.settled]

theorem completion_order_independent (initial first second : Environment)
    (expression : Expression) (one : Refines initial first) (two : Refines initial second)
    (settled : (evaluate initial expression).settled = true) :
    evaluate first expression = evaluate second expression := by
  rw [settled_stable_with_trace initial first expression one settled,
    settled_stable_with_trace initial second expression two settled]

end DemandCompletion
