import TabValues
import SpacingDecodedUnits

namespace HyphenSpacingTabComposition

open HyphenSpacingValues HyphenSpacingPhases HyphenTabValues

def withoutTabs (input : Input Value) : Result Value := native {input with ignoreTabs := true}

theorem ignore_tabs_has_no_tab_writes (input : Input Value) :
    tabWrites {input with ignoreTabs := true} = [] ∧
      hasTabPhase {input with ignoreTabs := true} = false := by simp [tabWrites,hasTabPhase]

theorem ignore_tabs_cache_independent (input : Input Value) (cache : Option (List (Tab Value))) :
    withoutTabs {input with tabCache := cache} = withoutTabs input := by
  simp [withoutTabs,native,ordinary,tabWrites,hasTabPhase]

theorem ignore_tabs_retains_justification (input : Input Value) (notCombined : input.textCombined = false) :
    (withoutTabs input).store = execute input.config.arithmetic (ordinary input).store
      (justificationEntries input.queryStart input.queryEnd input.justificationStart input.justification) := by
  simp [withoutTabs,native,notCombined,ordinary,tabWrites,execute]

def singletonSpacing (queries : Nat → Input Value) (index : Nat) : Pair Value :=
  let query := {queries index with queryStart := index,queryEnd := index+1,ignoreTabs := true}
  let answer := native query
  ⟨answer.store 0 .before,answer.store 0 .after⟩

def joinedProviders (queries : Nat → Input Value) (providers : Providers Value) : Providers Value :=
  {providers with spacingWithoutTabs := singletonSpacing queries}

theorem joined_before_and_after (queries : Nat → Input Value) (providers : Providers Value)
    (index : Nat) :
    (joinedProviders queries providers).spacingWithoutTabs index =
      ⟨(withoutTabs {queries index with queryStart := index,queryEnd := index+1}).store 0 .before,
       (withoutTabs {queries index with queryStart := index,queryEnd := index+1}).store 0 .after⟩ := rfl

theorem recursive_queries_ignore_tabs (queries : Nat → Input Value) (providers : Providers Value)
    (cache : Nat → Option (List (Tab Value))) :
    joinedProviders (fun index => {queries index with tabCache := cache index}) providers =
      joinedProviders queries providers := by
  have values : singletonSpacing (fun index => {queries index with tabCache := cache index}) = singletonSpacing queries := by
    funext index
    have independent := ignore_tabs_cache_independent
      {queries index with queryStart := index,queryEnd := index+1} (cache index)
    change withoutTabs {queries index with queryStart := index,queryEnd := index+1,tabCache := cache index} = _ at independent
    simpa only [singletonSpacing,withoutTabs] using
      congrArg (fun result : Result Value => Pair.mk (result.store 0 .before) (result.store 0 .after)) independent
  simp [joinedProviders,values]

theorem joined_query_chronology (numeric : Numeric Value) (queries : Nat → Input Value)
    (providers : Providers Value) (start first finish : Nat) (state : State Value) :
    requestedIndices (loop numeric (joinedProviders queries providers) start first finish state).events =
      requestedIndices state.events ++ List.range' first (finish-first) :=
  loop_requests _ _ _ _ _ _

def selectedEntries (cache : Cache Value) (offset : Nat) : List (Tab Value) :=
  let index := if offset = 0 then 0 else HyphenTabSpacingAdmission.binarySearch
    (fun i => (cache.entries[i]?).map Tab.offset |>.getD 0) offset 0 cache.entries.length
  cache.entries.drop index

def calculateAndApply (numeric : Numeric Value) (queries : Nat → Input Value)
    (providers : Providers Value) (context : Context Value) (state : State Value)
    (input : Input Value) : State Value × Result Value :=
  if input.textCombined || input.ignoreTabs || !input.tabWidthPositive then (state,native input)
  else
    let calculated := calculate numeric (joinedProviders queries providers) context state
    let applied := {input with tabCache := calculated.cache.map fun cache => selectedEntries cache input.tabFirst}
    (calculated,native applied)

theorem no_recursive_tab_calculation (numeric : Numeric Value) (queries : Nat → Input Value)
    (providers : Providers Value) (context : Context Value) (state : State Value) (input : Input Value) :
    calculateAndApply numeric queries providers context state {input with ignoreTabs := true} =
      (state,withoutTabs input) := by simp [calculateAndApply,withoutTabs]

theorem complete_joined_values (numeric : Numeric Value) (queries : Nat → Input Value)
    (providers : Providers Value) (context : Context Value) (state : State Value) (input : Input Value)
    (enabled : input.textCombined = false ∧ input.ignoreTabs = false ∧ input.tabWidthPositive = true)
    (index : Nat) (side : Side) :
    let calculated := calculate numeric (joinedProviders queries providers) context state
    let applied := {input with tabCache := calculated.cache.map fun cache => selectedEntries cache input.tabFirst}
    (calculateAndApply numeric queries providers context state input).2.store index side =
      (valuesAt (trace applied) index side).foldl input.config.arithmetic.add input.config.arithmetic.zero := by
  dsimp only
  simp only [calculateAndApply,enabled.1,enabled.2.1,enabled.2.2,Bool.not_true,Bool.false_or,Bool.false_eq_true,↓reduceIte]
  exact complete_pointwise _ _ _

end HyphenSpacingTabComposition
