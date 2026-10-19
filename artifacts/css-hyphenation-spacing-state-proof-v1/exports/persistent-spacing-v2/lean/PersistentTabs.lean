import SpacingTabComposition

namespace PersistentTabs
open HyphenSpacingValues HyphenTabValues

def frontier (start : Nat) (state : State Value) : Nat :=
  (match state.cache with | none => state.analyzed | some cache => cache.limit) + start

def reflowQuery (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (state : State Value) : State Value :=
  calculate numeric providers ⟨true,true,start,finish,none⟩ state

theorem step_analyzed (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) :
    (step numeric providers start index state).analyzed = state.analyzed := by
  unfold step
  split <;> simp

theorem loop_analyzed (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) :
    (loop numeric providers start first finish state).analyzed = state.analyzed := by
  rw [loop]
  split
  next active => rw [loop_analyzed,step_analyzed]
  next inactive => rfl
termination_by finish-first

theorem step_cache_retained (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) (cached : state.cache.isSome = true) :
    (step numeric providers start index state).cache.isSome = true := by
  unfold step
  split
  next tab => rfl
  next ordinary => exact cached

theorem loop_cache_retained (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) (cached : state.cache.isSome = true) :
    (loop numeric providers start first finish state).cache.isSome = true := by
  rw [loop]
  split
  next active => exact loop_cache_retained _ _ _ _ _ _ (step_cache_retained _ _ _ _ _ cached)
  next inactive => exact cached
termination_by finish-first

theorem query_frontier (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (state : State Value) (bounded : start ≤ finish) :
    frontier start (reflowQuery numeric providers start finish state) =
      max (frontier start state) finish := by
  unfold reflowQuery calculate
  simp only [Bool.and_true,Bool.not_true,Bool.and_false,Bool.false_eq_true,↓reduceIte]
  change frontier start
    (let computed := if frontier start state < finish then
      let calculated := loop numeric providers start (frontier start state) finish state
      {calculated with cache := calculated.cache.map fun cache => {cache with limit := finish-start}}
      else state
    if computed.cache.isNone then
      {computed with analyzed := max computed.analyzed (finish-start), events := computed.events++[.removeProperty]}
    else computed) = _
  split
  next active =>
    have analyzed := loop_analyzed numeric providers start (frontier start state) finish state
    generalize computedEq : loop numeric providers start (frontier start state) finish state = computed
    rw [computedEq] at analyzed
    cases cache : computed.cache with
    | none =>
      have initialNone : state.cache = none := by
        cases initial : state.cache with
        | none => rfl
        | some old =>
          have retained := loop_cache_retained numeric providers start (frontier start state) finish state (by simp [initial])
          rw [computedEq,cache] at retained
          contradiction
      simp [cache,frontier,analyzed,initialNone] at active ⊢
      omega
    | some current =>
      simp [cache,frontier] at active ⊢
      omega
  next inactive =>
    cases cache : state.cache with
    | none => simp [cache,frontier] at inactive ⊢; omega
    | some current => simp [cache,frontier] at inactive ⊢; omega

theorem query_requests (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (state : State Value) :
    requestedIndices (reflowQuery numeric providers start finish state).events =
      requestedIndices state.events ++ List.range' (frontier start state) (finish-frontier start state) := by
  unfold reflowQuery calculate
  simp only [Bool.and_true,Bool.not_true,Bool.and_false,Bool.false_eq_true,↓reduceIte]
  change requestedIndices
    (let computed := if frontier start state < finish then
      let calculated := loop numeric providers start (frontier start state) finish state
      {calculated with cache := calculated.cache.map fun cache => {cache with limit := finish-start}}
      else state
    if computed.cache.isNone then
      {computed with analyzed := max computed.analyzed (finish-start), events := computed.events++[.removeProperty]}
    else computed).events = _
  split
  next active =>
    cases cache : (loop numeric providers start (frontier start state) finish state).cache with
    | none => simpa [cache,requestedIndices,List.filterMap_append] using loop_requests numeric providers start (frontier start state) finish state
    | some current => simpa [cache] using loop_requests numeric providers start (frontier start state) finish state
  next inactive =>
    have empty : finish-frontier start state = 0 := by omega
    cases cache : state.cache <;> simp [cache,empty,requestedIndices,List.filterMap_append]

def queries (numeric : Numeric Value) (providers : Providers Value) (start : Nat)
    (state : State Value) : List Nat → State Value
  | [] => state
  | finish::rest => queries numeric providers start (reflowQuery numeric providers start finish state) rest

def covered (initial : Nat) (ends : List Nat) : Nat := ends.foldl max initial

theorem covered_lower (initial : Nat) (ends : List Nat) : initial ≤ covered initial ends := by
  induction ends generalizing initial with
  | nil => simp [covered]
  | cons finish rest ih =>
    have next := ih (max initial finish)
    simp only [covered,List.foldl_cons] at next ⊢
    omega

theorem queries_frontier (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (state : State Value) (ends : List Nat)
    (bounded : ∀ finish ∈ ends, start ≤ finish) :
    frontier start (queries numeric providers start state ends) = covered (frontier start state) ends := by
  induction ends generalizing state with
  | nil => rfl
  | cons finish rest ih =>
    simp only [queries,covered,List.foldl_cons]
    rw [ih _ (by intro endpoint member; exact bounded endpoint (by simp [member])),
        query_frontier _ _ _ _ _ (bounded finish (by simp))]
    rfl

theorem adjacent_ranges (first middle last : Nat) (ordered : first ≤ middle) (orderedLast : middle ≤ last) :
    List.range' first (middle-first) ++ List.range' middle (last-middle) =
      List.range' first (last-first) := by
  have middleEq : middle = first + 1 * (middle-first) := by omega
  have sumEq : middle-first+(last-middle) = last-first := by omega
  have concat := List.range'_append (s:=first) (m:=middle-first) (n:=last-middle) (step:=1)
  rw [← middleEq,sumEq] at concat
  exact concat

theorem queries_requests (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (state : State Value) (ends : List Nat)
    (bounded : ∀ finish ∈ ends, start ≤ finish) :
    requestedIndices (queries numeric providers start state ends).events =
      requestedIndices state.events ++
        List.range' (frontier start state) (covered (frontier start state) ends - frontier start state) := by
  induction ends generalizing state with
  | nil => simp [queries,covered]
  | cons finish rest ih =>
    rw [queries,ih _ (by intro endpoint member; exact bounded endpoint (by simp [member])),query_requests,
      query_frontier _ _ _ _ _ (bounded finish (by simp)),List.append_assoc]
    have equation : finish-frontier start state = max (frontier start state) finish-frontier start state := by omega
    rw [equation,adjacent_ranges _ _ _ (by omega) (covered_lower _ _)]
    rfl

def initial (offset : Value) : State Value := ⟨offset,none,0,[]⟩

theorem constructor_frontier (start : Nat) (offset : Value) : frontier start (initial offset) = start := by
  simp [frontier,initial]

theorem constructor_requests (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (offset : Value) (ends : List Nat)
    (bounded : ∀ finish ∈ ends, start ≤ finish) :
    requestedIndices (queries numeric providers start (initial offset) ends).events =
      List.range' start (covered start ends-start) := by
  simpa [frontier,initial,requestedIndices] using queries_requests numeric providers start (initial offset) ends bounded

structure Values (Value : Type) where
  offset : Value
  entries : List (HyphenSpacingPhases.Tab Value)

def values (state : State Value) : Values Value :=
  ⟨state.offset,(state.cache.getD ⟨[],0⟩).entries⟩

def numericStep (numeric : Numeric Value) (providers : Providers Value) (start index : Nat)
    (input : Values Value) : Values Value :=
  let spacing := providers.spacingWithoutTabs index
  let before := numeric.arithmetic.add input.offset spacing.before
  if providers.isTab index then
    let next := numeric.nextTab before
    ⟨numeric.arithmetic.add next spacing.after,
      input.entries ++ [⟨index-start,numeric.roundedDifference next before⟩]⟩
  else
    let afterGlyph := if providers.isClusterStart index then numeric.arithmetic.add before (providers.clusterAdvance index) else before
    ⟨numeric.arithmetic.add afterGlyph spacing.after,input.entries⟩

theorem step_values (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) :
    values (step numeric providers start index state) = numericStep numeric providers start index (values state) := by
  unfold step numericStep values
  split <;> simp

def numericReference (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (input : Values Value) : Values Value :=
  (List.range' first (finish-first)).foldl (fun value index => numericStep numeric providers start index value) input

theorem loop_values (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value) :
    values (loop numeric providers start first finish state) = numericReference numeric providers start first finish (values state) := by
  rw [loop]
  split
  next active =>
    rw [loop_values,step_values]
    unfold numericReference
    have length : finish-first = (finish-(first+1))+1 := by omega
    rw [length,List.range'_succ,List.foldl_cons]
  next done => simp [numericReference,Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

theorem query_values (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (state : State Value) :
    values (reflowQuery numeric providers start finish state) =
      numericReference numeric providers start (frontier start state) finish (values state) := by
  unfold reflowQuery calculate
  simp only [Bool.and_true,Bool.not_true,Bool.and_false,Bool.false_eq_true,↓reduceIte]
  change values
    (let computed := if frontier start state < finish then
      let calculated := loop numeric providers start (frontier start state) finish state
      {calculated with cache := calculated.cache.map fun cache => {cache with limit := finish-start}}
      else state
    if computed.cache.isNone then
      {computed with analyzed := max computed.analyzed (finish-start), events := computed.events++[.removeProperty]}
    else computed) = _
  split
  next active =>
    have reference := loop_values numeric providers start (frontier start state) finish state
    generalize computedEq : loop numeric providers start (frontier start state) finish state = computed
    rw [computedEq] at reference
    cases cache : computed.cache <;> simpa [values,cache] using reference
  next inactive =>
    have empty : finish-frontier start state = 0 := by omega
    cases cache : state.cache <;> simp [cache,empty,values,numericReference]

theorem reference_chunks (numeric : Numeric Value) (providers : Providers Value)
    (start first middle finish : Nat) (input : Values Value)
    (ordered : first ≤ middle) (orderedLast : middle ≤ finish) :
    numericReference numeric providers start middle finish
      (numericReference numeric providers start first middle input) =
      numericReference numeric providers start first finish input := by
  unfold numericReference
  rw [← List.foldl_append,adjacent_ranges _ _ _ ordered orderedLast]

theorem queries_values (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (state : State Value) (ends : List Nat)
    (bounded : ∀ finish ∈ ends, start ≤ finish) :
    values (queries numeric providers start state ends) =
      numericReference numeric providers start (frontier start state)
        (covered (frontier start state) ends) (values state) := by
  induction ends generalizing state with
  | nil => simp [queries,covered,numericReference]
  | cons finish rest ih =>
    rw [queries,ih _ (by intro endpoint member; exact bounded endpoint (by simp [member])),
      query_frontier _ _ _ _ _ (bounded finish (by simp)),query_values]
    have headReference : numericReference numeric providers start (frontier start state) finish (values state) =
        numericReference numeric providers start (frontier start state) (max (frontier start state) finish) (values state) := by
      unfold numericReference
      have same : finish-frontier start state = max (frontier start state) finish-frontier start state := by omega
      rw [same]
    rw [headReference,reference_chunks _ _ _ _ _ _ _ (by omega) (covered_lower _ _)]
    rfl

theorem constructor_values (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (offset : Value) (ends : List Nat)
    (bounded : ∀ finish ∈ ends, start ≤ finish) :
    values (queries numeric providers start (initial offset) ends) =
      numericReference numeric providers start start (covered start ends) ⟨offset,[]⟩ := by
  simpa [frontier,initial,values] using queries_values numeric providers start (initial offset) ends bounded

theorem query_partition_values (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (offset : Value) (left right : List Nat)
    (leftBounded : ∀ finish ∈ left, start ≤ finish)
    (rightBounded : ∀ finish ∈ right, start ≤ finish)
    (sameCoverage : covered start left = covered start right) :
    values (queries numeric providers start (initial offset) left) =
      values (queries numeric providers start (initial offset) right) := by
  rw [constructor_values _ _ _ _ _ leftBounded,constructor_values _ _ _ _ _ rightBounded,sameCoverage]

theorem query_partition_requests (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (offset : Value) (left right : List Nat)
    (leftBounded : ∀ finish ∈ left, start ≤ finish)
    (rightBounded : ∀ finish ∈ right, start ≤ finish)
    (sameCoverage : covered start left = covered start right) :
    requestedIndices (queries numeric providers start (initial offset) left).events =
      requestedIndices (queries numeric providers start (initial offset) right).events := by
  rw [constructor_requests _ _ _ _ _ leftBounded,constructor_requests _ _ _ _ _ rightBounded,sameCoverage]

def exampleNumeric : Numeric Nat := ⟨⟨0,Nat.add⟩,fun x => (x/8+1)*8,Nat.sub⟩
def exampleProviders : Providers Nat := ⟨fun _ => ⟨0,0⟩,fun i => i==1,fun _ => true,fun _ => 1⟩
def goodExample : State Nat := queries exampleNumeric exampleProviders 0 (initial 0) [1,2,1,2]
def badSeed : State Nat := ⟨0,none,1,[]⟩
def badExample : State Nat := reflowQuery exampleNumeric exampleProviders 0 2 badSeed

theorem persistent_nonvacuity :
    goodExample.offset = 8 ∧ frontier 0 goodExample = 2 ∧
    (values goodExample).entries.map HyphenSpacingPhases.Tab.width = [7] ∧
    requestedIndices goodExample.events = [0,1] := by decide +kernel

theorem independently_seeded_state_counterexample :
    frontier 0 badSeed = 1 ∧
    (values badExample).entries.map HyphenSpacingPhases.Tab.width = [8] ∧
    (values goodExample).entries.map HyphenSpacingPhases.Tab.width ≠
      (values badExample).entries.map HyphenSpacingPhases.Tab.width := by decide +kernel

theorem resetting_repeats_requests :
    requestedIndices (reflowQuery exampleNumeric exampleProviders 0 1 (initial 0)).events ++
      requestedIndices (reflowQuery exampleNumeric exampleProviders 0 2 (initial 0)).events = [0,0,1] ∧
    requestedIndices goodExample.events = [0,1] := by decide +kernel

end PersistentTabs
