import DictionaryManagerSequence

namespace HyphenDictionaryResourceIdentity

open HyphenDictionaryManager HyphenDictionaryFallback

def CacheMatchesPatterns (state : State) : Prop :=
  ∀ key handle, state.cache key = some handle → state.patterns key = some handle.resource

theorem load_preserves_pattern_identity (valid : Resource → Bool) (state : State)
    (key : Key) (resource : Resource) (admitted : CacheMatchesPatterns state)
    (pattern : state.patterns key = some resource) (uncached : state.cache key = none) :
    CacheMatchesPatterns (load valid state key resource).state := by
  unfold load
  split
  · intro queried handle found
    dsimp only [replace] at found
    split at found
    next same =>
      subst queried
      cases found
      exact pattern
    · exact admitted queried handle found
  · intro queried handle found
    dsimp only [replace]
    split
    next same =>
      subst queried
      rw [uncached] at found
      cases found
    · exact admitted queried handle found

theorem get_preserves_pattern_identity (valid : Resource → Bool) (fallback : Key → Option Key)
    (fuel : Nat) (state : State) (key : Key) (admitted : CacheMatchesPatterns state) :
    CacheMatchesPatterns (nativeGet valid fallback fuel state key).state := by
  induction fuel generalizing key with
  | zero => exact admitted
  | succ fuel ih =>
    have selected := selection_admitted state key
    dsimp only [nativeGet]
    split
    · exact admitted
    next selectedKey resource found =>
      rw [found] at selected
      exact load_preserves_pattern_identity valid state selectedKey resource admitted selected.1 selected.2.1
    · split
      · exact admitted
      · exact ih _

theorem direct_pattern_result_identity (valid : Resource → Bool) (fallback : Key → Option Key)
    (fuel : Nat) (state : State) (key : Key) (resource : Resource) (handle : Handle)
    (admitted : CacheMatchesPatterns state) (pattern : state.patterns key = some resource)
    (returned : (nativeGet valid fallback (fuel+1) state key).answer = some handle) :
    handle.resource = resource := by
  cases cached : state.cache key with
  | some found =>
    have known := admitted key found cached
    have same : found.resource = resource := Option.some.inj (known.symm.trans pattern)
    simp only [nativeGet,select,cached] at returned
    cases returned
    exact same
  | none =>
    simp only [nativeGet,select,cached,pattern,load] at returned
    split at returned
    · cases returned
      rfl
    · cases returned

theorem arbitrary_manager_operations_preserve_identity
    (history : HyphenDictionarySequence.History)
    (ops : List (HyphenDictionarySequence.Operation × (Resource → Bool)))
    (admitted : CacheMatchesPatterns history.state) :
    CacheMatchesPatterns (HyphenDictionarySequence.run history ops).state := by
  induction ops generalizing history with
  | nil => exact admitted
  | cons op rest ih =>
    apply ih
    cases op with
    | mk action valid =>
      cases action with
      | get key => exact get_preserves_pattern_identity valid fallback _ history.state key admitted
      | pressure => intro key handle found;cases found
      | reload entries => intro key handle found;cases found
      | alias key target => exact admitted
      | preference key value => exact admitted

theorem constructed_cache_resource_identity
    (ops : List (HyphenDictionarySequence.Operation × (Resource → Bool))) :
    CacheMatchesPatterns (HyphenDictionarySequence.run ⟨HyphenDictionarySequence.initial,[],[]⟩ ops).state := by
  apply arbitrary_manager_operations_preserve_identity
  intro key handle found
  cases found

def parentDifferentResource : State :=
  {HyphenDictionarySequence.initial with patterns := replace (fun _ => none) [101,110] (some 1)}

theorem requested_uri_identity_requires_parent_association :
    (nativeGet (fun _ => true) fallback 3 parentDifferentResource [101,110]).answer = some ⟨1,false⟩ ∧
    (nativeGet (fun _ => true) fallback 3 parentDifferentResource [101,110]).answer ≠ some ⟨2,false⟩ := by decide

end HyphenDictionaryResourceIdentity
