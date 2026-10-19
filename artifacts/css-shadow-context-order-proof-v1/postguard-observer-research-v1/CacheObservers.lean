import AttributeObservers
namespace PostGuardObservers

structure CertifiedCacheEntry where
 source : Nat
 value : Nat
 queries : List AttributeQuery

abbrev CertifiedCache := Nat → Option CertifiedCacheEntry

def cacheSupported (cache : CertifiedCache) (references : AttributeReferences) : Prop :=
 ∀ key entry, cache key = some entry → ∀ query ∈ entry.queries, supports references query

def insertCacheEntry (cache : CertifiedCache) (key : Nat) (entry : CertifiedCacheEntry) :=
 fun other => if other = key then some entry else cache other

def installParsedDeclarations (cache : CertifiedCache) (source : Nat)
 (queries : List AttributeQuery) : List (Nat × Nat) → CertifiedCache
 | [] => cache
 | (key,value)::rest =>
   installParsedDeclarations (insertCacheEntry cache key ⟨source,value,queries⟩) source queries rest

theorem cache_support_survives_attribute_queries (cache : CertifiedCache)
 (references : AttributeReferences) (valid : cacheSupported cache references)
 (queries : List AttributeQuery) : cacheSupported cache (recordQueries references queries) := by
 intro key entry found query member
 exact (record_query_history_membership references queries query).mpr (Or.inl (valid key entry found query member))

theorem insert_supported_entry (cache : CertifiedCache) (references : AttributeReferences)
 (valid : cacheSupported cache references) (key : Nat) (entry : CertifiedCacheEntry)
 (supported : ∀ query ∈ entry.queries, supports references query) :
 cacheSupported (insertCacheEntry cache key entry) references := by
 intro other found lookup
 by_cases same : other = key
 · simp [insertCacheEntry,same] at lookup
   subst found
   exact supported
 · exact valid other found (by simpa [insertCacheEntry,same] using lookup)

theorem install_parsed_declarations_supported (cache : CertifiedCache)
 (references : AttributeReferences) (valid : cacheSupported cache references)
 (source : Nat) (queries : List AttributeQuery)
 (supported : ∀ query ∈ queries, supports references query) (declarations : List (Nat × Nat)) :
 cacheSupported (installParsedDeclarations cache source queries declarations) references := by
 induction declarations generalizing cache with
 | nil => exact valid
 | cons declaration rest ih =>
   exact ih _ (insert_supported_entry cache references valid declaration.1
     ⟨source,declaration.2,queries⟩ supported)

structure CacheObserverState where
 cache : CertifiedCache
 references : AttributeReferences

inductive CacheObserverOperation where
 | fill (source : Nat) (queries : List AttributeQuery) (declarations : List (Nat × Nat))
 | queryOnly (queries : List AttributeQuery)
 | hit (key source : Nat)

def cacheObserverStep (state : CacheObserverState) : CacheObserverOperation → CacheObserverState
 | .fill source queries declarations =>
   ⟨installParsedDeclarations state.cache source queries declarations,
    recordQueries state.references queries⟩
 | .queryOnly queries => ⟨state.cache,recordQueries state.references queries⟩
 | .hit _ _ => state

def cacheObserverHistory (operations : List CacheObserverOperation) (state : CacheObserverState) :=
 operations.foldl cacheObserverStep state

theorem cache_step_preserves_support (state : CacheObserverState)
 (valid : cacheSupported state.cache state.references) (operation : CacheObserverOperation) :
 cacheSupported (cacheObserverStep state operation).cache (cacheObserverStep state operation).references := by
 cases operation with
 | fill source queries declarations =>
   apply install_parsed_declarations_supported
   · exact cache_support_survives_attribute_queries _ _ valid queries
   · intro query member
     exact (record_query_history_membership state.references queries query).mpr (Or.inr member)
 | queryOnly queries => exact cache_support_survives_attribute_queries _ _ valid queries
 | hit key source => exact valid

theorem arbitrary_cache_history_support (operations : List CacheObserverOperation)
 (state : CacheObserverState) (valid : cacheSupported state.cache state.references) :
 cacheSupported (cacheObserverHistory operations state).cache (cacheObserverHistory operations state).references := by
 induction operations generalizing state with
 | nil => exact valid
 | cons operation rest ih => exact ih _ (cache_step_preserves_support state valid operation)

theorem fresh_cache_history_support (operations : List CacheObserverOperation) :
 cacheSupported (cacheObserverHistory operations ⟨fun _ => none,fun _ => []⟩).cache
   (cacheObserverHistory operations ⟨fun _ => none,fun _ => []⟩).references := by
 apply arbitrary_cache_history_support
 intro key entry found
 contradiction

def lookupMatchingSource (cache : CertifiedCache) (key source : Nat) : Option CertifiedCacheEntry :=
 (cache key).filter fun entry => entry.source == source

theorem matching_cache_hit_preserves_attribute_consumer
 (target candidate : Nat → Nat → Option String) (state : CacheObserverState)
 (valid : cacheSupported state.cache state.references) (key source : Nat) (entry : CertifiedCacheEntry)
 (hit : lookupMatchingSource state.cache key source = some entry) :
 haveSameReferencedAttributes target candidate (recordQueries state.references entry.queries) ↔
 haveSameReferencedAttributes target candidate state.references := by
 have found : state.cache key = some entry := by
   unfold lookupMatchingSource at hit
   cases lookup : state.cache key with
   | none => simp [lookup] at hit
   | some actual =>
     simp only [lookup,Option.filter] at hit
     split at hit
     · cases hit; rfl
     · contradiction
 apply sharing_check_depends_only_on_support
 intro query
 rw [record_query_history_membership]
 constructor
 · rintro (old | member)
   · exact old
   · exact valid key entry found query member
 · exact Or.inl

def eraseCache (cache : CertifiedCache) (key : Nat) : Option (Nat × Nat) :=
 (cache key).map fun entry => (entry.source,entry.value)

theorem ghost_queries_do_not_change_cache_entry
 (cache : CertifiedCache) (key source value : Nat) (left right : List AttributeQuery) :
 eraseCache (insertCacheEntry cache key ⟨source,value,left⟩) =
 eraseCache (insertCacheEntry cache key ⟨source,value,right⟩) := by
 funext other
 by_cases same : other = key <;> simp [eraseCache,insertCacheEntry,same]

#print axioms arbitrary_cache_history_support
#print axioms fresh_cache_history_support
#print axioms matching_cache_hit_preserves_attribute_consumer
#print axioms ghost_queries_do_not_change_cache_entry
end PostGuardObservers
