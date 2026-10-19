import SpacingPhases
import TabCacheConstruction

namespace HyphenTabValues

open HyphenSpacingValues HyphenSpacingPhases

structure Numeric (Value : Type) where
  arithmetic : Arithmetic Value
  nextTab : Value → Value
  roundedDifference : Value → Value → Value

structure Providers (Value : Type) where
  spacingWithoutTabs : Nat → Pair Value
  isTab : Nat → Bool
  isClusterStart : Nat → Bool
  clusterAdvance : Nat → Value

structure Cache (Value : Type) where
  entries : List (Tab Value)
  limit : Nat

inductive Event where
  | spacingWithoutTabs (index : Nat)
  | clusterAdvance (index : Nat)
  | allocateAndPublish
  | loadProperty
  | removeProperty
  deriving DecidableEq, Repr

structure State (Value : Type) where
  offset : Value
  cache : Option (Cache Value)
  analyzed : Nat
  events : List Event

def step (numeric : Numeric Value) (providers : Providers Value) (start index : Nat)
    (state : State Value) : State Value :=
  let spacing := providers.spacingWithoutTabs index
  let offset := numeric.arithmetic.add state.offset spacing.before
  let events := state.events ++ [.spacingWithoutTabs index]
  if providers.isTab index then
    let next := numeric.nextTab offset
    let entry : Tab Value := ⟨index-start,numeric.roundedDifference next offset⟩
    let cache := state.cache.getD ⟨[],0⟩
    let events := if state.cache.isNone then events++[.allocateAndPublish] else events
    {state with offset := numeric.arithmetic.add next spacing.after, cache := some {cache with entries := cache.entries++[entry]},events := events}
  else
    let offset := if providers.isClusterStart index then
      numeric.arithmetic.add offset (providers.clusterAdvance index) else offset
    let events := if providers.isClusterStart index then events++[.clusterAdvance index] else events
    {state with offset := numeric.arithmetic.add offset spacing.after,events := events}

def loop (numeric : Numeric Value) (providers : Providers Value) (start first finish : Nat)
    (state : State Value) : State Value :=
  if active : first < finish then
    loop numeric providers start (first+1) finish (step numeric providers start first state)
  else state
termination_by finish-first

def indexedReference (numeric : Numeric Value) (providers : Providers Value) (start first finish : Nat)
    (state : State Value) : State Value :=
  (List.range' first (finish-first)).foldl (fun state index => step numeric providers start index state) state

theorem complete_numeric_loop (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) :
    loop numeric providers start first finish state = indexedReference numeric providers start first finish state := by
  rw [loop]
  split
  next active =>
    rw [complete_numeric_loop]
    unfold indexedReference
    have length : finish-first = (finish-(first+1))+1 := by omega
    rw [length,List.range'_succ,List.foldl_cons]
  next done => simp [indexedReference,Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

def offsets (state : State Value) : List Nat :=
  ((state.cache.getD ⟨[],0⟩).entries).map Tab.offset

theorem step_offsets (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) :
    offsets (step numeric providers start index state) = offsets state ++
      (if providers.isTab index then [index-start] else []) := by
  unfold step
  split
  next tab => simp [offsets]
  next ordinary => simp [offsets]

def collectedOffsets (providers : Providers Value) (start first finish : Nat) : List Nat :=
  (List.range' first (finish-first)).filterMap fun index =>
    if providers.isTab index then some (index-start) else none

theorem loop_offsets (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) :
    offsets (loop numeric providers start first finish state) =
      offsets state ++ collectedOffsets providers start first finish := by
  rw [loop]
  split
  next active =>
    rw [loop_offsets,step_offsets]
    have length : finish-first = (finish-(first+1))+1 := by omega
    unfold collectedOffsets
    rw [length,List.range'_succ]
    by_cases tab : providers.isTab first = true <;> simp [tab,List.append_assoc]
  next done => simp [collectedOffsets,Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

def requestedIndices : List Event → List Nat := List.filterMap fun event =>
  match event with | .spacingWithoutTabs index => some index | _ => none

theorem step_requests (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) :
    requestedIndices (step numeric providers start index state).events =
      requestedIndices state.events ++ [index] := by
  unfold step
  split
  next tab =>
    split <;> simp [requestedIndices,List.filterMap_append]
  next ordinary =>
    split <;> simp [requestedIndices,List.filterMap_append]

theorem loop_requests (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) :
    requestedIndices (loop numeric providers start first finish state).events =
      requestedIndices state.events ++ List.range' first (finish-first) := by
  rw [loop]
  split
  next active =>
    rw [loop_requests,step_requests]
    have length : finish-first = (finish-(first+1))+1 := by omega
    rw [length,List.range'_succ]
    simp [List.append_assoc]
  next done => simp [Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

structure Context (Value : Type) where
  reflowing : Bool
  lineContainer : Bool
  start : Nat
  queryEnd : Nat
  savedProperty : Option (Cache Value)

def calculate (numeric : Numeric Value) (providers : Providers Value)
    (context : Context Value) (state : State Value) : State Value :=
  if state.cache.isNone && context.reflowing && !context.lineContainer then state else
  if state.cache.isNone && !context.reflowing then
    {state with cache := context.savedProperty,events := state.events++[.loadProperty]} else
  let first := (match state.cache with | none => state.analyzed | some cache => cache.limit) + context.start
  let computed := if first < context.queryEnd then
    let computed := loop numeric providers context.start first context.queryEnd state
    {computed with cache := computed.cache.map fun cache => {cache with limit := context.queryEnd-context.start}}
    else state
  if computed.cache.isNone then
    {computed with analyzed := max computed.analyzed (context.queryEnd-context.start),events := computed.events++[.removeProperty]}
  else computed

theorem intrinsic_early_return (numeric : Numeric Value) (providers : Providers Value)
    (context : Context Value) (state : State Value) (noCache : state.cache = none)
    (reflow : context.reflowing = true) (noContainer : context.lineContainer = false) :
    calculate numeric providers context state = state := by simp [calculate,noCache,reflow,noContainer]

theorem nonreflow_loads_property (numeric : Numeric Value) (providers : Providers Value)
    (context : Context Value) (state : State Value) (noCache : state.cache = none)
    (reflow : context.reflowing = false) :
    calculate numeric providers context state =
      {state with cache := context.savedProperty,events := state.events++[.loadProperty]} := by
  simp [calculate,noCache,reflow]

theorem tab_addition_order (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) (tab : providers.isTab index = true) :
    (step numeric providers start index state).offset =
      numeric.arithmetic.add
        (numeric.nextTab (numeric.arithmetic.add state.offset (providers.spacingWithoutTabs index).before))
        (providers.spacingWithoutTabs index).after := by simp [step,tab]

theorem ordinary_addition_order (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) (tab : providers.isTab index = false)
    (cluster : providers.isClusterStart index = true) :
    (step numeric providers start index state).offset =
      numeric.arithmetic.add
        (numeric.arithmetic.add (numeric.arithmetic.add state.offset (providers.spacingWithoutTabs index).before)
          (providers.clusterAdvance index)) (providers.spacingWithoutTabs index).after := by simp [step,tab,cluster]

end HyphenTabValues
