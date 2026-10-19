import CacheObservers
namespace PostGuardObservers

structure RuleObserverState where
 cache : CertifiedCache
 references : AttributeReferences
 uncacheable : Bool
 displayOrContentDependsOnInherited : Bool

structure RuleObserverInput where
 inherited : Bool
 displayOrContent : Bool
 queries : List AttributeQuery

def recordRuleObservers (state : RuleObserverState) (input : RuleObserverInput) : RuleObserverState :=
 ⟨state.cache,recordQueries state.references input.queries,
  state.uncacheable || !input.inherited,
  state.displayOrContentDependsOnInherited || (!input.inherited && input.displayOrContent)⟩

def sameNativeObserverMeaning (left right : RuleObserverState) : Prop :=
 eraseCache left.cache = eraseCache right.cache ∧
 left.uncacheable = right.uncacheable ∧
 left.displayOrContentDependsOnInherited = right.displayOrContentDependsOnInherited ∧
 ∀ query, supports left.references query ↔ supports right.references query

theorem rule_observer_representation_can_differ (cache : CertifiedCache) :
 let state : RuleObserverState := ⟨cache,fun _ => [],false,false⟩
 let input : RuleObserverInput := ⟨false,false,[(1,2)]⟩
 (recordRuleObservers (recordRuleObservers state input) input).references 1 = [2,2] ∧
 (recordRuleObservers state input).references 1 = [2] := by
 simp [recordRuleObservers,recordQueries,recordQuery]

theorem rule_observer_idempotent_under_native_consumers
 (state : RuleObserverState) (input : RuleObserverInput) :
 sameNativeObserverMeaning (recordRuleObservers (recordRuleObservers state input) input)
   (recordRuleObservers state input) := by
 refine ⟨rfl,?_,?_,?_⟩
 · simp [recordRuleObservers]
 · simp [recordRuleObservers]
 · intro query
   simp [recordRuleObservers,record_query_history_membership]

theorem rule_observers_commute_under_native_consumers
 (state : RuleObserverState) (left right : RuleObserverInput) :
 sameNativeObserverMeaning (recordRuleObservers (recordRuleObservers state left) right)
   (recordRuleObservers (recordRuleObservers state right) left) := by
 refine ⟨rfl,?_,?_,?_⟩
 · simp only [recordRuleObservers]
   cases state.uncacheable <;> cases left.inherited <;> cases right.inherited <;> rfl
 · simp only [recordRuleObservers]
   cases state.displayOrContentDependsOnInherited <;>
     cases left.inherited <;> cases right.inherited <;>
     cases left.displayOrContent <;> cases right.displayOrContent <;> rfl
 · intro query
   simp only [recordRuleObservers,record_query_history_membership]
   simp [or_left_comm,or_comm]

theorem native_observer_meaning_preserves_sharing
 (left right : RuleObserverState) (same : sameNativeObserverMeaning left right)
 (target candidate : Nat → Nat → Option String) :
 haveSameReferencedAttributes target candidate left.references ↔
 haveSameReferencedAttributes target candidate right.references :=
 sharing_check_depends_only_on_support target candidate left.references right.references same.2.2.2

theorem rule_observation_preserves_cache_certificates (state : RuleObserverState)
 (valid : cacheSupported state.cache state.references) (input : RuleObserverInput) :
 cacheSupported (recordRuleObservers state input).cache (recordRuleObservers state input).references :=
 cache_support_survives_attribute_queries state.cache state.references valid input.queries

theorem repeated_rule_observation_preserves_future_cache_hit_observers
 (state : RuleObserverState) (valid : cacheSupported state.cache state.references)
 (input : RuleObserverInput) (key source : Nat) (entry : CertifiedCacheEntry)
 (hit : lookupMatchingSource state.cache key source = some entry)
 (target candidate : Nat → Nat → Option String) :
 let after := recordRuleObservers (recordRuleObservers state input) input
 haveSameReferencedAttributes target candidate (recordQueries after.references entry.queries) ↔
 haveSameReferencedAttributes target candidate (recordRuleObservers state input).references := by
 dsimp only
 have afterValid := rule_observation_preserves_cache_certificates _
   (rule_observation_preserves_cache_certificates state valid input) input
 have hitSafe := matching_cache_hit_preserves_attribute_consumer target candidate
   ⟨(recordRuleObservers (recordRuleObservers state input) input).cache,
    (recordRuleObservers (recordRuleObservers state input) input).references⟩
   afterValid key source entry hit
 exact hitSafe.trans (native_observer_meaning_preserves_sharing _ _
   (rule_observer_idempotent_under_native_consumers state input) target candidate)

#print axioms rule_observer_idempotent_under_native_consumers
#print axioms rule_observers_commute_under_native_consumers
#print axioms rule_observation_preserves_cache_certificates
#print axioms repeated_rule_observation_preserves_future_cache_hit_observers
end PostGuardObservers
