import DictionaryFallback

namespace HyphenDictionarySequence

open HyphenDictionaryManager HyphenDictionaryFallback

def insertPatterns (table : Key → Option Resource) (entries : List (Key × Resource)) : Key → Option Resource :=
  entries.foldl (fun prior entry => replace prior entry.1 (some entry.2)) table

def reload (state : State) (entries : List (Key × Resource)) : State :=
  {state with patterns := insertPatterns (fun _ => none) entries,cache := fun _ => none}

inductive Operation where
  | get (key : Key)
  | pressure
  | reload (entries : List (Key × Resource))
  | alias (key target : Key)
  | preference (key : Key) (capitalized : Bool)

def step (valid : Resource → Bool) (state : State) : Operation → Result
  | .get key => nativeGet valid fallback ((trimWildcard key).length+1) state key
  | .pressure => ⟨pressure state,none,[]⟩
  | .reload entries => ⟨reload state entries,none,[]⟩
  | .alias key target => ⟨{state with aliases := replace state.aliases key (some target)},none,[]⟩
  | .preference key value => ⟨{state with capitalized := fun queried => if queried = key then value else state.capitalized queried},none,[]⟩

structure History where
  state : State
  events : List Event
  returned : List Handle

def run : History → List (Operation × (Resource → Bool)) → History
  | history,[] => history
  | history,(op,valid)::rest =>
    let result := step valid history.state op
    run ⟨result.state,history.events++result.events,history.returned++result.answer.toList⟩ rest

def Admitted (history : History) : Prop :=
  CacheProvenance history.events history.state ∧ ∀ handle ∈ history.returned, HasProvenance history.events handle

theorem step_provenance (valid : Resource → Bool) (state : State) (history : List Event)
    (op : Operation) (admitted : CacheProvenance history state) :
    let result := step valid state op
    CacheProvenance (history++result.events) result.state ∧
    (∀ handle, result.answer = some handle → HasProvenance (history++result.events) handle) := by
  cases op with
  | get key => exact get_provenance valid fallback _ state history key admitted
  | pressure =>
    refine ⟨?_,?_⟩
    · intro key handle found
      cases found
    · intro handle found
      cases found
  | reload entries =>
    refine ⟨?_,?_⟩
    · intro key handle found
      cases found
    · intro handle found
      cases found
  | alias key target =>
    refine ⟨by simpa [step,CacheProvenance] using admitted,?_⟩
    intro handle found
    cases found
  | preference key value =>
    refine ⟨by simpa [step,CacheProvenance] using admitted,?_⟩
    intro handle found
    cases found

theorem all_operation_provenance (history : History) (ops : List (Operation × (Resource → Bool)))
    (admitted : Admitted history) : Admitted (run history ops) := by
  induction ops generalizing history with
  | nil => exact admitted
  | cons op rest ih =>
    apply ih
    have next := step_provenance op.2 history.state history.events op.1 admitted.1
    refine ⟨next.1,?_⟩
    intro handle present
    rcases List.mem_append.mp present with old | new
    · exact provenance_append history.events _ handle (admitted.2 handle old)
    · cases found : (step op.2 history.state op.1).answer with
      | none => simp [found] at new
      | some value =>
        have same : handle = value := by simpa [found] using new
        subst handle
        exact next.2 value found

def initial : State := ⟨fun _ => none,fun _ => none,fun _ => none,fun _ => false⟩

theorem constructed_operation_provenance (ops : List (Operation × (Resource → Bool))) :
    Admitted (run ⟨initial,[],[]⟩ ops) := by
  apply all_operation_provenance
  refine ⟨?_,by simp⟩
  intro key handle found
  cases found

theorem cached_handle_ignores_new_preference (state : State) (key : Key) (handle : Handle)
    (found : state.cache key = some handle) (changed : Bool) (valid : Resource → Bool) :
    let updated := (step valid state (.preference key changed)).state
    (step valid updated (.get key)).answer = some handle ∧
    (step valid updated (.get key)).events = [] := by
  simp [step,nativeGet,select,found]

theorem reload_clears_cached_preferences (state : State) (entries : List (Key × Resource)) :
    ∀ key, (reload state entries).cache key = none := fun _ => rfl

theorem later_entry_wins (table : Key → Option Resource) (before : List (Key × Resource))
    (key : Key) (resource : Resource) :
    insertPatterns table (before++[(key,resource)]) key = some resource := by
  simp [insertPatterns,List.foldl_append,replace]

end HyphenDictionarySequence
