import RuleObserverAlgebra
namespace PostGuardObservers

theorem erased_insert_congruence (left right : CertifiedCache)
 (same : eraseCache left = eraseCache right) (key : Nat) (entry : CertifiedCacheEntry) :
 eraseCache (insertCacheEntry left key entry) = eraseCache (insertCacheEntry right key entry) := by
 funext other
 by_cases hit : other = key
 · simp [eraseCache,insertCacheEntry,hit]
 · simpa [eraseCache,insertCacheEntry,hit] using congrFun same other

theorem erased_install_congruence (left right : CertifiedCache)
 (same : eraseCache left = eraseCache right) (source : Nat)
 (queries : List AttributeQuery) (declarations : List (Nat × Nat)) :
 eraseCache (installParsedDeclarations left source queries declarations) =
 eraseCache (installParsedDeclarations right source queries declarations) := by
 induction declarations generalizing left right with
 | nil => exact same
 | cons declaration rest ih =>
   exact ih _ _ (erased_insert_congruence left right same declaration.1
     ⟨source,declaration.2,queries⟩)

theorem query_history_support_congruence (left right : AttributeReferences)
 (same : ∀ query, supports left query ↔ supports right query) (queries : List AttributeQuery) :
 ∀ query, supports (recordQueries left queries) query ↔ supports (recordQueries right queries) query := by
 intro query
 simp only [record_query_history_membership,same]

theorem rule_observer_congruence (left right : RuleObserverState)
 (same : sameNativeObserverMeaning left right) (input : RuleObserverInput) :
 sameNativeObserverMeaning (recordRuleObservers left input) (recordRuleObservers right input) := by
 rcases same with ⟨cache,uncacheable,flag,support⟩
 refine ⟨cache,?_,?_,query_history_support_congruence _ _ support input.queries⟩
 · simp only [recordRuleObservers,uncacheable]
 · simp only [recordRuleObservers,flag]

inductive ObserverOperation where
 | rule (input : RuleObserverInput)
 | cache (operation : CacheObserverOperation)

def observerStep (state : RuleObserverState) : ObserverOperation → RuleObserverState
 | .rule input => recordRuleObservers state input
 | .cache operation =>
   let after := cacheObserverStep ⟨state.cache,state.references⟩ operation
   ⟨after.cache,after.references,state.uncacheable,state.displayOrContentDependsOnInherited⟩

def observerHistory (operations : List ObserverOperation) (state : RuleObserverState) :=
 operations.foldl observerStep state

theorem observer_step_congruence (left right : RuleObserverState)
 (same : sameNativeObserverMeaning left right) (operation : ObserverOperation) :
 sameNativeObserverMeaning (observerStep left operation) (observerStep right operation) := by
 cases operation with
 | rule input => exact rule_observer_congruence left right same input
 | cache operation =>
   rcases same with ⟨cache,uncacheable,flag,support⟩
   cases operation with
   | fill source queries declarations =>
     exact ⟨erased_install_congruence _ _ cache source queries declarations,uncacheable,flag,
       query_history_support_congruence _ _ support queries⟩
   | queryOnly queries => exact ⟨cache,uncacheable,flag,
       query_history_support_congruence _ _ support queries⟩
   | hit key source => exact ⟨cache,uncacheable,flag,support⟩

theorem arbitrary_common_continuation_congruence (operations : List ObserverOperation)
 (left right : RuleObserverState) (same : sameNativeObserverMeaning left right) :
 sameNativeObserverMeaning (observerHistory operations left) (observerHistory operations right) := by
 induction operations generalizing left right with
 | nil => exact same
 | cons operation rest ih => exact ih _ _ (observer_step_congruence left right same operation)

theorem repeated_rule_preserves_sharing_after_common_continuation
 (operations : List ObserverOperation) (state : RuleObserverState) (input : RuleObserverInput)
 (target candidate : Nat → Nat → Option String) :
 haveSameReferencedAttributes target candidate
   (observerHistory operations (recordRuleObservers (recordRuleObservers state input) input)).references ↔
 haveSameReferencedAttributes target candidate
   (observerHistory operations (recordRuleObservers state input)).references :=
 native_observer_meaning_preserves_sharing _ _
   (arbitrary_common_continuation_congruence operations _ _
     (rule_observer_idempotent_under_native_consumers state input)) target candidate

def erasedMatchingLookup (cache : CertifiedCache) (key source : Nat) : Option (Nat × Nat) :=
 (eraseCache cache key).filter fun entry => entry.1 == source

theorem repeated_rule_preserves_cache_lookup_after_common_continuation
 (operations : List ObserverOperation) (state : RuleObserverState) (input : RuleObserverInput)
 (key source : Nat) :
 erasedMatchingLookup
   (observerHistory operations (recordRuleObservers (recordRuleObservers state input) input)).cache key source =
 erasedMatchingLookup
   (observerHistory operations (recordRuleObservers state input)).cache key source := by
 have same := arbitrary_common_continuation_congruence operations _ _
   (rule_observer_idempotent_under_native_consumers state input)
 simp only [erasedMatchingLookup,same.1]

#print axioms arbitrary_common_continuation_congruence
#print axioms repeated_rule_preserves_sharing_after_common_continuation
#print axioms repeated_rule_preserves_cache_lookup_after_common_continuation
end PostGuardObservers
