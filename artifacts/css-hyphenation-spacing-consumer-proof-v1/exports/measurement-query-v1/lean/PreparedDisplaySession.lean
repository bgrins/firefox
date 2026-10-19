import PropertySession

namespace PreparedDisplaySession
open PropertySession HyphenTabValues

theorem covered_cache_unchanged (numeric : Numeric Value) (providers : Providers Value)
    (context : Context Value) (state : State Value) (cache : Cache Value)
    (loaded : state.cache = some cache) (covered : context.queryEnd ≤ cache.limit+context.start) :
    calculate numeric providers context state = state := by
  simp [calculate,loaded,show ¬cache.limit+context.start < context.queryEnd by omega]

theorem borrowed_query_unchanged (numeric : Numeric Value) (providers : Providers Value)
    (session : Session Value) (cache : Cache Value) (start finish : Nat)
    (loaded : session.tab.cache = some cache) (associated : Associated session)
    (covered : finish ≤ cache.limit+start) :
    query numeric providers ⟨start,finish,true,false,false⟩ session = session := by
  have same := associated cache loaded
  have calculated :=  covered_cache_unchanged numeric providers
    (⟨false,false,start,finish,session.property⟩ : Context Value) session.tab cache loaded covered
  simp [query,loaded,calculated,← same]

structure Call (Value : Type) where
  numeric : Numeric Value
  providers : Providers Value
  start : Nat
  finish : Nat

def execute (session : Session Value) : List (Call Value) → Session Value
  | [] => session
  | call::rest => execute (query call.numeric call.providers
      ⟨call.start,call.finish,true,false,false⟩ session) rest

theorem borrowed_history_unchanged (session : Session Value) (cache : Cache Value) (calls : List (Call Value))
    (loaded : session.tab.cache = some cache) (associated : Associated session)
    (covered : ∀ call ∈ calls, call.finish ≤ cache.limit+call.start) :
    execute session calls = session := by
  induction calls with
  | nil => rfl
  | cons call rest ih =>
    simp only [execute]
    rw [borrowed_query_unchanged call.numeric call.providers session cache call.start call.finish loaded associated (covered call (by simp))]
    exact ih (fun q h => covered q (by simp [h]))

theorem first_load_before_preparation_queries (numeric : Numeric Value) (providers : Providers Value)
    (frame run contentOffset start finish : Nat) (offset : Value) (cache : Cache Value) :
    (query numeric providers ⟨start,finish,true,false,false⟩
      (construct frame run contentOffset offset (some cache))).tab.cache = some cache := by
  simp [query,construct,PersistentTabs.initial,calculate]

theorem prepare_then_measure_keeps_borrow (numeric : Numeric Value) (providers : Providers Value)
    (frame run contentOffset start finish : Nat) (offset : Value) (cache : Cache Value)
    (preparation measurement : List (Call Value))
    (covered : ∀ call ∈ preparation ++ measurement, call.finish ≤ cache.limit+call.start) :
    let loaded := query numeric providers ⟨start,finish,true,false,false⟩
      (construct frame run contentOffset offset (some cache))
    execute loaded (preparation ++ measurement) = loaded := by
  dsimp only
  apply borrowed_history_unchanged _ cache _
  · exact first_load_before_preparation_queries _ _ _ _ _ _ _ _ _
  · exact query_associated _ _ _ _ (constructor_associated _ _ _ _ _)
  · exact covered

theorem tab_free_step_cache (numeric : Numeric Value) (providers : Providers Value)
    (start index : Nat) (state : State Value) (ordinary : providers.isTab index = false) :
    (step numeric providers start index state).cache = state.cache := by simp [step,ordinary]

theorem tab_free_extension_cache (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (state : State Value)
    (ordinary : ∀ index, first ≤ index → index < finish → providers.isTab index = false) :
    (loop numeric providers start first finish state).cache = state.cache := by
  rw [loop]
  split
  next active =>
    rw [tab_free_extension_cache numeric providers start (first+1) finish _ (by
      intro index low high
      exact ordinary index (by omega) high),tab_free_step_cache numeric providers start first state (ordinary first (by omega) active)]
  next done => rfl
termination_by finish-first

theorem loaded_query_preserves_entries_if_new_units_not_tabs (numeric : Numeric Value) (providers : Providers Value)
    (context : Context Value) (state : State Value) (cache : Cache Value)
    (loaded : state.cache = some cache)
    (ordinary : ∀ index, cache.limit+context.start ≤ index → index < context.queryEnd → providers.isTab index = false) :
    (calculate numeric providers context state).cache.map Cache.entries = some cache.entries := by
  unfold calculate
  simp only [loaded,Option.isNone_some,Bool.false_and,Bool.false_eq_true,ite_false]
  by_cases extend : cache.limit+context.start < context.queryEnd
  · have same := tab_free_extension_cache numeric providers context.start (cache.limit+context.start) context.queryEnd state ordinary
    simp [extend,same,loaded]
  · simp [extend,loaded]

def twoTabs : Providers Nat := ⟨fun _ => ⟨0,0⟩,fun i => i==0 || i==2,fun _ => true,fun _ => 1⟩
def shortReflow := PersistentTabs.queries PersistentTabs.exampleNumeric twoTabs 0 (PersistentTabs.initial 0) [2]
def display := construct 3 7 0 0 shortReflow.cache
def firstUncovered := query PersistentTabs.exampleNumeric twoTabs ⟨0,3,true,false,false⟩ display
def secondUncovered := query PersistentTabs.exampleNumeric twoTabs ⟨0,3,true,false,false⟩ firstUncovered
def completeReflow := PersistentTabs.queries PersistentTabs.exampleNumeric twoTabs 0 (PersistentTabs.initial 0) [3]

theorem uncovered_display_needs_caller_admission :
    (PersistentTabs.values shortReflow).entries.map HyphenSpacingPhases.Tab.width = [8] ∧
    (PersistentTabs.values firstUncovered.tab).entries.map HyphenSpacingPhases.Tab.width = [8] ∧
    (PersistentTabs.values secondUncovered.tab).entries.map HyphenSpacingPhases.Tab.width = [8,8] ∧
    (PersistentTabs.values completeReflow).entries.map HyphenSpacingPhases.Tab.width = [8,7] := by decide +kernel

end PreparedDisplaySession
