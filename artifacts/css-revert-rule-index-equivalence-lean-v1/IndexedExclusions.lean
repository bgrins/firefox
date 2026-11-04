import ColdMembership

namespace ShadowOrder.IndexedExclusions

abbrev Index (δ β : Type) := δ → Option β

def insertEntries [DecidableEq δ] (block : β) (entries : List δ) (index : Index δ β) :=
  entries.foldl (fun current entry query => if query = entry then some block else current query) index

theorem insert_entries_lookup [DecidableEq δ] (block : β) (entries : List δ)
    (index : Index δ β) (query : δ) :
    insertEntries block entries index query =
      if query ∈ entries then some block else index query := by
  induction entries generalizing index with
  | nil => rfl
  | cons entry rest ih =>
    simp only [insertEntries, List.foldl_cons] at ih ⊢
    rw [ih]
    by_cases a : query = entry <;> by_cases b : query ∈ rest <;> simp [a, b]

def UniqueOwner (entries : β → List δ) : Prop :=
  ∀ left right entry, entry ∈ entries left → entry ∈ entries right → left = right

def IndexFor (entries : β → List δ) (covered : List β) (index : Index δ β) : Prop :=
  ∀ query block, index query = some block ↔ block ∈ covered ∧ query ∈ entries block

theorem empty_index (entries : β → List δ) : IndexFor entries [] (fun _ => none) := by
  intro query block
  simp

theorem insert_block_correct [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (covered : List β) (index : Index δ β)
    (valid : IndexFor entries covered index) (block : β) :
    IndexFor entries (block :: covered) (insertEntries block (entries block) index) := by
  intro query owner
  rw [insert_entries_lookup]
  by_cases member : query ∈ entries block
  · simp only [member, ↓reduceIte, Option.some.injEq]
    constructor
    · intro equal
      subst owner
      exact ⟨by simp, member⟩
    · intro found
      exact unique block owner query member found.2
  · simp only [member, ↓reduceIte]
    rw [valid query owner]
    constructor
    · intro found
      exact ⟨List.mem_cons_of_mem _ found.1, found.2⟩
    · intro found
      rcases List.mem_cons.mp found.1 with equal | prior
      · subst owner
        exact False.elim (member found.2)
      · exact ⟨prior, found.2⟩

theorem index_for_congr (entries : β → List δ) (left right : List β)
    (index : Index δ β) (same : ∀ block, block ∈ left ↔ block ∈ right)
    (valid : IndexFor entries left index) : IndexFor entries right index := by
  intro query block
  rw [valid query block, same block]

def buildIndex [DecidableEq β] [DecidableEq δ] (entries : β → List δ) :
    List β → List β → Index δ β → Index δ β
  | [], _, index => index
  | block :: rest, seen, index =>
      if block ∈ seen then buildIndex entries rest seen index
      else buildIndex entries rest (block :: seen) (insertEntries block (entries block) index)

theorem build_index_correct [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources seen : List β)
    (index : Index δ β) (valid : IndexFor entries seen index) :
    IndexFor entries (sources ++ seen) (buildIndex entries sources seen index) := by
  induction sources generalizing seen index with
  | nil => exact valid
  | cons block rest ih =>
    by_cases duplicate : block ∈ seen
    · simp only [buildIndex, duplicate, ↓reduceIte]
      apply index_for_congr entries (rest ++ seen) _ _ _ (ih seen index valid)
      intro b
      simp only [List.cons_append, List.mem_cons, List.mem_append]
      constructor
      · intro member
        exact Or.inr member
      · intro member
        rcases member with rfl | member
        · exact Or.inr duplicate
        · exact member
    · simp only [buildIndex, duplicate, ↓reduceIte]
      apply index_for_congr entries (rest ++ block :: seen) _ _ _
        (ih (block :: seen) _ (insert_block_correct entries unique seen index valid block))
      intro b
      simp [List.mem_append, or_left_comm]

def coldOwner [DecidableEq δ] (entries : β → List δ) (query : δ) : List β → Option β
  | [] => none
  | block :: rest => if query ∈ entries block then some block else coldOwner entries query rest

theorem cold_owner_correct [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (sources : List β) :
    IndexFor entries sources (fun query => coldOwner entries query sources) := by
  induction sources with
  | nil => exact empty_index entries
  | cons block rest ih =>
    intro query owner
    simpa only [coldOwner, insert_entries_lookup] using
      (insert_block_correct entries unique rest _ ih block query owner)

def freshIndex [DecidableEq β] [DecidableEq δ] (entries : β → List δ) (sources : List β) :=
  buildIndex entries sources [] (fun _ => none)

theorem fresh_index_correct [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (sources : List β) :
    IndexFor entries sources (freshIndex entries sources) := by
  simpa [freshIndex] using build_index_correct entries unique sources [] _ (empty_index entries)

theorem indexed_owner_matches_first_search [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources : List β) (query : δ) :
    freshIndex entries sources query = coldOwner entries query sources := by
  have agree : ∀ block, freshIndex entries sources query = some block ↔
      coldOwner entries query sources = some block := by
    intro block
    rw [fresh_index_correct entries unique sources query block,
      cold_owner_correct entries unique sources query block]
  cases indexed : freshIndex entries sources query <;>
    cases cold : coldOwner entries query sources <;> simp_all

theorem covered_lookup_total [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources : List β)
    (query : δ) (block : β) (covered : block ∈ sources) (member : query ∈ entries block) :
    freshIndex entries sources query = some block :=
  (fresh_index_correct entries unique sources query block).mpr ⟨covered, member⟩

theorem source_roster_support_suffices [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (left right : List β)
    (same : ∀ block, block ∈ left ↔ block ∈ right) (query : δ) :
    freshIndex entries left query = freshIndex entries right query := by
  have agree : ∀ block, freshIndex entries left query = some block ↔
      freshIndex entries right query = some block := by
    intro block
    rw [fresh_index_correct entries unique left query block,
      fresh_index_correct entries unique right query block, same block]
  cases l : freshIndex entries left query <;>
    cases r : freshIndex entries right query <;> simp_all

structure Key (π β : Type) where
  property : π
  priority : Priority
  block : β
  deriving DecidableEq

def makeKey (property : π) (priority : Priority) (block : β) : Key π β :=
  ⟨property, unimportantPriority priority, block⟩

def insertSet [DecidableEq κ] (stored : κ → Bool) (key : κ) (query : κ) :=
  decide (query = key) || stored query

def buildSet [DecidableEq κ] (keys : List κ) :=
  keys.foldl insertSet (fun _ => false)

theorem set_fold_membership [DecidableEq κ] (keys : List κ) (stored : κ → Bool) (query : κ) :
    keys.foldl insertSet stored query = (stored query || decide (query ∈ keys)) := by
  induction keys generalizing stored with
  | nil => simp
  | cons key rest ih =>
    simp only [List.foldl_cons, ih, insertSet, List.mem_cons]
    by_cases a : query = key <;> by_cases b : query ∈ rest <;> simp [a, b]

theorem built_set_membership [DecidableEq κ] (keys : List κ) (query : κ) :
    buildSet keys query = decide (query ∈ keys) := by
  simpa [buildSet] using set_fold_membership keys (fun _ => false) query

def coldExcluded [DecidableEq π] [DecidableEq δ] (entries : β → List δ)
    (keys : List (Key π β)) (property : π) (priority : Priority) (query : δ) : Bool :=
  keys.any (fun key => decide (key.property = property) &&
    decide (key.priority = unimportantPriority priority) && decide (query ∈ entries key.block))

theorem cold_exclusion_is_key_membership [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (owner : β)
    (member : query ∈ entries owner) :
    coldExcluded entries keys property priority query =
      decide (makeKey property priority owner ∈ keys) := by
  have exactOwner : ∀ block, query ∈ entries block ↔ block = owner := by
    intro block
    exact ⟨fun h => unique block owner query h member, fun h => h ▸ member⟩
  induction keys with
  | nil => rfl
  | cons key rest ih =>
    simp only [coldExcluded, List.any_cons] at ih ⊢
    rw [ih]
    cases key
    simp [exactOwner, makeKey, Key.mk.injEq, eq_comm, Bool.and_assoc]
    rfl

def indexedExcluded [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (sources : List β) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) : Bool :=
  match freshIndex entries sources query with
  | none => false
  | some block => buildSet keys (makeKey property priority block)

theorem indexed_exclusion_matches_cold [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources : List β)
    (keys : List (Key π β)) (property : π) (priority : Priority) (query : δ)
    (coverage : ∃ owner ∈ sources, query ∈ entries owner) :
    indexedExcluded entries sources keys property priority query =
      coldExcluded entries keys property priority query := by
  rcases coverage with ⟨owner, covered, member⟩
  rw [indexedExcluded, covered_lookup_total entries unique sources query owner covered member]
  change buildSet keys (makeKey property priority owner) = coldExcluded entries keys property priority query
  rw [built_set_membership,
    cold_exclusion_is_key_membership entries unique keys property priority query owner member]

theorem full_guard_equivalence [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources : List β)
    (keys : List (Key π β)) (property : π) (priority : Priority) (query : δ)
    (coverage : ∃ owner ∈ sources, query ∈ entries owner) (included fast cutoffAllows : Bool) :
    (included && !(fast && (!cutoffAllows || indexedExcluded entries sources keys property priority query))) =
    (included && !(fast && (!cutoffAllows || coldExcluded entries keys property priority query))) := by
  rw [indexed_exclusion_matches_cold entries unique sources keys property priority query coverage]

theorem shared_entry_counterexample :
    freshIndex (fun (_ : Nat) => [0]) [0, 1] 0 = some 1 ∧
    coldOwner (fun (_ : Nat) => [0]) 0 [0, 1] = some 0 := by
  decide

theorem uncovered_entry_is_absent :
    freshIndex (fun block : Nat => [block]) [0, 1] 2 = none := by
  decide

theorem key_retains_flags (property : π) (priority : Priority) (block : β)
    (flags : Nat) (different : flags ≠ priority.flags) :
    makeKey property {priority with flags := flags} block ≠ makeKey property priority block := by
  intro equal
  exact ColdMembership.full_priority_equality_retains_flags priority flags different
    (congrArg Key.priority equal)

theorem key_retains_physical_property (left right : π) (priority : Priority) (block : β)
    (different : left ≠ right) : makeKey left priority block ≠ makeKey right priority block := by
  intro equal
  exact different (congrArg Key.property equal)

#print axioms insert_entries_lookup
#print axioms insert_block_correct
#print axioms build_index_correct
#print axioms indexed_owner_matches_first_search
#print axioms covered_lookup_total
#print axioms source_roster_support_suffices
#print axioms built_set_membership
#print axioms cold_exclusion_is_key_membership
#print axioms indexed_exclusion_matches_cold
#print axioms full_guard_equivalence
#print axioms shared_entry_counterexample
#print axioms uncovered_entry_is_absent
#print axioms key_retains_flags
#print axioms key_retains_physical_property

end ShadowOrder.IndexedExclusions
