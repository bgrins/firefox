import IncrementalIndex

namespace ShadowOrder.OwnerMapDedup

open IndexedExclusions IncrementalIndex

theorem first_entry_cached_iff_seen [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (seen : List β) (owners : Index δ β)
    (valid : IndexFor entries seen owners) (block : β) (first : δ) (rest : List δ)
    (nonempty : entries block = first :: rest) :
    (owners first).isSome = true ↔ block ∈ seen := by
  have member : first ∈ entries block := by simp [nonempty]
  constructor
  · intro cached
    cases hit : owners first with
    | none => simp [hit] at cached
    | some owner =>
      have found := (valid first owner).mp hit
      have equal := unique owner block first found.2 member
      simpa [equal] using found.1
  · intro visited
    rw [(valid first block).mpr ⟨visited, member⟩]
    rfl

theorem first_miss_implies_whole_block_absent [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (seen : List β)
    (owners : Index δ β) (valid : IndexFor entries seen owners) (block : β)
    (first : δ) (rest : List δ) (nonempty : entries block = first :: rest)
    (miss : owners first = none) (entry : δ) (member : entry ∈ entries block) :
    owners entry = none := by
  have unseen : block ∉ seen := by
    intro seenBlock
    have cached := (first_entry_cached_iff_seen entries unique seen owners valid block first rest nonempty).mpr seenBlock
    simp [miss] at cached
  cases hit : owners entry with
  | none => rfl
  | some owner =>
    have found := (valid entry owner).mp hit
    have equal := unique owner block entry found.2 member
    exact False.elim (unseen (equal ▸ found.1))

def visitOwners [DecidableEq δ] (entries : β → List δ)
    (node : Option β) (owners : Index δ β) : Index δ β :=
  match node with
  | none => owners
  | some block =>
    match entries block with
    | [] => owners
    | first :: _ =>
      if (owners first).isSome then owners
      else insertEntries block (entries block) owners

theorem visit_owners_equivalence [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (node : Option β)
    (seen : List β) (owners : Index δ β) (valid : IndexFor entries seen owners) :
    visitOwners entries node owners = (visit entries node seen owners).2 := by
  cases node with
  | none => rfl
  | some block =>
    cases shape : entries block with
    | nil =>
      by_cases duplicate : block ∈ seen <;> simp [visitOwners, visit, shape, duplicate, insertEntries]
    | cons first rest =>
      have firstSeen := first_entry_cached_iff_seen entries unique seen owners valid block first rest shape
      by_cases duplicate : block ∈ seen
      · have hit := firstSeen.mpr duplicate
        simp [visitOwners, visit, shape, duplicate, hit]
      · have miss : (owners first).isSome = false := by
          cases h : (owners first).isSome
          · rfl
          · exact False.elim (duplicate (firstSeen.mp h))
        simp [visitOwners, visit, shape, duplicate, miss]

structure OwnerCursor (δ β : Type) where
  remaining : List (Option β)
  owners : Index δ β

def erase (state : Cursor δ β) : OwnerCursor δ β := ⟨state.remaining, state.owners⟩

def ownerScan [DecidableEq δ] (entries : β → List δ) (query : δ) :
    List (Option β) → Index δ β → OwnerCursor δ β
  | remaining, owners =>
    match owners query with
    | some _ => ⟨remaining, owners⟩
    | none =>
      match remaining with
      | [] => ⟨[], owners⟩
      | node :: rest => ownerScan entries query rest (visitOwners entries node owners)

def ownerLookup [DecidableEq δ] (entries : β → List δ)
    (query : δ) (state : OwnerCursor δ β) : OwnerCursor δ β :=
  ownerScan entries query state.remaining state.owners

theorem scan_erasure_equivalence [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (query : δ)
    (remaining : List (Option β)) (seen : List β) (owners : Index δ β)
    (valid : IndexFor entries seen owners) :
    ownerScan entries query remaining owners = erase (scan entries query remaining seen owners) := by
  induction remaining generalizing seen owners with
  | nil => cases hit : owners query <;> simp [ownerScan, scan, erase, hit]
  | cons node rest ih =>
    cases hit : owners query with
    | some owner => simp [ownerScan, scan, erase, hit]
    | none =>
      simp only [ownerScan, scan, hit]
      rw [visit_owners_equivalence entries unique node seen owners valid]
      exact ih _ _ (visit_valid entries unique node seen owners valid)

def ownerQueries [DecidableEq δ] (entries : β → List δ)
    (queries : List δ) (state : OwnerCursor δ β) : OwnerCursor δ β :=
  queries.foldl (fun current query => ownerLookup entries query current) state

theorem arbitrary_history_equivalence [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (queries : List δ)
    (state : Cursor δ β) (valid : Valid entries state) :
    ownerQueries entries queries (erase state) = erase (queryMany entries queries state) := by
  induction queries generalizing state with
  | nil => rfl
  | cons query rest ih =>
    change ownerQueries entries rest (ownerLookup entries query (erase state)) =
      erase (queryMany entries rest (lookup entries query state))
    have step := scan_erasure_equivalence entries unique query state.remaining state.seen state.owners valid
    change ownerLookup entries query (erase state) = erase (lookup entries query state) at step
    rw [step]
    exact ih _ (scan_spec entries unique query state.remaining state.seen state.owners valid).1

theorem owner_lookup_covered [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (sources : List (Option β))
    (history : List δ) (query : δ) (block : β)
    (covered : block ∈ blocksOf sources) (member : query ∈ entries block) :
    (ownerLookup entries query (ownerQueries entries history (erase (initial sources)))).owners query = some block := by
  have all := arbitrary_history_equivalence entries unique (history ++ [query]) (initial sources)
    (empty_index entries)
  have result := congrArg (fun state => state.owners query) all
  have coveredResult := after_history_covered_lookup entries unique sources history query block covered member
  simp only [queryMany] at coveredResult
  simp only [ownerQueries, queryMany, List.foldl_append, List.foldl_cons, List.foldl_nil, erase] at result ⊢
  exact result.trans coveredResult

theorem empty_block_is_inert [DecidableEq δ] (entries : β → List δ)
    (block : β) (owners : Index δ β) (empty : entries block = []) :
    visitOwners entries (some block) owners = owners := by simp [visitOwners, empty]

def ownerCheck [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (keys : List (Key π β)) (property : π)
    (priority : Priority) (query : δ) (state : OwnerCursor δ β) : Bool × OwnerCursor δ β :=
  if prefixFold keys (prefixFor property priority) then
    let next := ownerLookup entries query state
    let answer := match next.owners query with
      | none => false
      | some block => buildSet keys (makeKey property priority block)
    (answer, next)
  else (false, state)

theorem exclusion_check_refines_incremental [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (state : Cursor δ β)
    (valid : Valid entries state) :
    ownerCheck entries keys property priority query (erase state) =
      ((check entries keys property priority query state).1,
        erase (check entries keys property priority query state).2) := by
  have step := scan_erasure_equivalence entries unique query state.remaining state.seen state.owners valid
  change ownerLookup entries query (erase state) = erase (lookup entries query state) at step
  unfold ownerCheck check
  split
  · rw [step]
    rfl
  · rfl

theorem exclusion_answer_matches_cold [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (state : Cursor δ β)
    (valid : Valid entries state)
    (coverage : prefixFold keys (prefixFor property priority) = true →
      ∃ owner ∈ support state, query ∈ entries owner) :
    (ownerCheck entries keys property priority query (erase state)).1 =
      coldExcluded entries keys property priority query := by
  rw [exclusion_check_refines_incremental entries unique keys property priority query state valid]
  exact prefix_gate_equivalence entries unique keys property priority query state valid coverage

def exampleEntries (block : Nat) := if block = 9 then [] else [2 * block, 2 * block + 1]
def exampleSources : List (Option Nat) := [some 9, some 0, none, some 1, some 9, some 0, some 2]

theorem repeated_empty_and_cached_blocks :
    let first := ownerLookup exampleEntries 2 ⟨exampleSources, fun _ => none⟩
    first.remaining = [some 9, some 0, some 2] ∧
      (ownerQueries exampleEntries [0, 5, 2] first).remaining = [] ∧
      (ownerQueries exampleEntries [0, 5, 2] first).owners 0 = some 0 := by decide

theorem partial_block_counterexample :
    let entries := fun (_ : Nat) => [0, 1]
    let owners := fun query : Nat => if query = 0 then some 0 else none
    (visitOwners entries (some 0) owners) 1 = none ∧
      (insertEntries 0 (entries 0) owners) 1 = some 0 := by decide

theorem shared_first_entry_counterexample :
    let entries := fun block : Nat => if block = 0 then [0] else [0, 1]
    let sources := [some 0, some 1]
    (ownerLookup entries 1 ⟨sources, fun _ => none⟩).owners 1 = none ∧
      (lookup entries 1 (initial sources)).owners 1 = some 1 := by decide

#print axioms first_entry_cached_iff_seen
#print axioms first_miss_implies_whole_block_absent
#print axioms visit_owners_equivalence
#print axioms scan_erasure_equivalence
#print axioms arbitrary_history_equivalence
#print axioms owner_lookup_covered
#print axioms empty_block_is_inert
#print axioms exclusion_check_refines_incremental
#print axioms exclusion_answer_matches_cold
#print axioms repeated_empty_and_cached_blocks
#print axioms partial_block_counterexample
#print axioms shared_first_entry_counterexample

end ShadowOrder.OwnerMapDedup
