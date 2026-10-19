import Buffer

namespace LanguageBreak

structure SegmentKey where
  units : List CodeUnit
  wordPolicy : Nat
  linePolicy : Nat
  cjk : Bool
  deriving DecidableEq, Repr

structure CacheSlot where
  set : Fin 2048
  way : Bool
  deriving DecidableEq, Repr

structure SegmentEntry where
  key : SegmentKey
  answer : List BreakKind
  deriving DecidableEq, Repr

abbrev SegmentCache := CacheSlot → Option SegmentEntry

def SegmentCache.Valid (provider : SegmentKey → List BreakKind) (cache : SegmentCache) : Prop :=
  ∀ slot entry, cache slot = some entry → entry.answer = provider entry.key

def entryAnswer (key : SegmentKey) : Option SegmentEntry → Option (List BreakKind)
  | none => none
  | some entry => if entry.key.units ≠ [] ∧ entry.key = key then some entry.answer else none

def cacheLookup (locate : SegmentKey → Fin 2048) (cache : SegmentCache) (key : SegmentKey) : Option (List BreakKind) :=
  match entryAnswer key (cache ⟨locate key,false⟩) with
  | some result => some result
  | none => entryAnswer key (cache ⟨locate key,true⟩)

def cacheStore (cache : SegmentCache) (slot : CacheSlot) (entry : SegmentEntry) : SegmentCache :=
  fun query => if query = slot then some entry else cache query

theorem cache_store_valid (provider : SegmentKey → List BreakKind) (cache : SegmentCache)
    (slot : CacheSlot) (entry : SegmentEntry) (valid : cache.Valid provider)
    (correct : entry.answer = provider entry.key) :
    (cacheStore cache slot entry).Valid provider := by
  intro query value found
  simp only [cacheStore] at found
  split at found
  next same => cases found; exact correct
  next different => exact valid query value found

theorem entry_answer_correct (provider : SegmentKey → List BreakKind) (cache : SegmentCache)
    (slot : CacheSlot) (key : SegmentKey) (answer : List BreakKind)
    (valid : cache.Valid provider) (found : entryAnswer key (cache slot) = some answer) :
    answer = provider key := by
  cases value : cache slot with
  | none => simp [value,entryAnswer] at found
  | some entry =>
    simp only [value,entryAnswer] at found
    split at found
    next matched =>
      have correct := valid slot entry value
      cases found
      rw [matched.2] at correct
      exact correct
    next missed => contradiction

theorem cache_lookup_correct (provider : SegmentKey → List BreakKind) (cache : SegmentCache)
    (locate : SegmentKey → Fin 2048) (key : SegmentKey) (answer : List BreakKind)
    (valid : cache.Valid provider) (found : cacheLookup locate cache key = some answer) :
    answer = provider key := by
  unfold cacheLookup at found
  split at found
  next result first =>
    cases found
    exact entry_answer_correct provider cache ⟨locate key,false⟩ key answer valid first
  next first => exact entry_answer_correct provider cache ⟨locate key,true⟩ key answer valid found

def cacheCompute (provider : SegmentKey → List BreakKind) (locate : SegmentKey → Fin 2048)
    (evict : SegmentCache → SegmentKey → CacheSlot) (cache : SegmentCache) (key : SegmentKey) :
    List BreakKind × SegmentCache :=
  match cacheLookup locate cache key with
  | some answer => (answer,cache)
  | none => (provider key,cacheStore cache (evict cache key) ⟨key,provider key⟩)

theorem cache_compute_transparent (provider : SegmentKey → List BreakKind)
    (locate : SegmentKey → Fin 2048) (evict : SegmentCache → SegmentKey → CacheSlot)
    (cache : SegmentCache) (key : SegmentKey) (valid : cache.Valid provider) :
    (cacheCompute provider locate evict cache key).1 = provider key ∧
    (cacheCompute provider locate evict cache key).2.Valid provider := by
  unfold cacheCompute
  split
  next answer found => exact ⟨cache_lookup_correct provider cache locate key answer valid found,valid⟩
  next missed => exact ⟨rfl,cache_store_valid provider cache (evict cache key) ⟨key,provider key⟩ valid rfl⟩

def cacheRequests (provider : SegmentKey → List BreakKind) (locate : SegmentKey → Fin 2048)
    (evict : SegmentCache → SegmentKey → CacheSlot) (cache : SegmentCache) :
    List SegmentKey → List (List BreakKind) × SegmentCache
  | [] => ([],cache)
  | key::rest =>
    let next := cacheCompute provider locate evict cache key
    let tail := cacheRequests provider locate evict next.2 rest
    (next.1::tail.1,tail.2)

theorem arbitrary_cache_sequence (provider : SegmentKey → List BreakKind)
    (locate : SegmentKey → Fin 2048) (evict : SegmentCache → SegmentKey → CacheSlot)
    (cache : SegmentCache) (requests : List SegmentKey) (valid : cache.Valid provider) :
    (cacheRequests provider locate evict cache requests).1 = requests.map provider ∧
    (cacheRequests provider locate evict cache requests).2.Valid provider := by
  induction requests generalizing cache with
  | nil => exact ⟨rfl,valid⟩
  | cons key rest ih =>
    have step := cache_compute_transparent provider locate evict cache key valid
    have tail := ih (cacheCompute provider locate evict cache key).2 step.2
    exact ⟨by simp only [cacheRequests,List.map,step.1,tail.1],tail.2⟩

end LanguageBreak
