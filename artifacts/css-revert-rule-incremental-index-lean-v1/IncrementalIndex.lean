import IndexedExclusions

namespace ShadowOrder.IncrementalIndex

open IndexedExclusions

structure Cursor (δ β : Type) where
  remaining : List (Option β)
  seen : List β
  owners : Index δ β

def blocksOf (nodes : List (Option β)) : List β := nodes.filterMap id

def support (state : Cursor δ β) : List β := blocksOf state.remaining ++ state.seen

def Valid (entries : β → List δ) (state : Cursor δ β) : Prop :=
  IndexFor entries state.seen state.owners

def visit [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (node : Option β) (seen : List β) (owners : Index δ β) : List β × Index δ β :=
  match node with
  | none => (seen, owners)
  | some block =>
      if block ∈ seen then (seen, owners)
      else (block :: seen, insertEntries block (entries block) owners)

theorem visit_valid [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (node : Option β) (seen : List β)
    (owners : Index δ β) (valid : IndexFor entries seen owners) :
    IndexFor entries (visit entries node seen owners).1 (visit entries node seen owners).2 := by
  cases node with
  | none => exact valid
  | some block =>
    by_cases member : block ∈ seen
    · simpa [visit, member] using valid
    · simpa [visit, member] using insert_block_correct entries unique seen owners valid block

theorem visit_support [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (node : Option β) (seen : List β) (owners : Index δ β) (block : β) :
    block ∈ (visit entries node seen owners).1 ↔ node = some block ∨ block ∈ seen := by
  cases node with
  | none => simp [visit]
  | some owner =>
    by_cases member : owner ∈ seen
    · simp only [visit, member, ↓reduceIte, Option.some.injEq]
      constructor
      · exact Or.inr
      · rintro (rfl | h)
        · exact member
        · exact h
    · simp [visit, member, eq_comm]

def scan [DecidableEq β] [DecidableEq δ] (entries : β → List δ) (query : δ) :
    List (Option β) → List β → Index δ β → Cursor δ β
  | remaining, seen, owners =>
    match owners query with
    | some _ => ⟨remaining, seen, owners⟩
    | none =>
      match remaining with
      | [] => ⟨[], seen, owners⟩
      | node :: rest =>
        let next := visit entries node seen owners
        scan entries query rest next.1 next.2

def lookup [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (query : δ) (state : Cursor δ β) : Cursor δ β :=
  scan entries query state.remaining state.seen state.owners

theorem step_support [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (node : Option β) (rest : List (Option β)) (seen : List β)
    (owners : Index δ β) (block : β) :
    block ∈ blocksOf rest ++ (visit entries node seen owners).1 ↔
      block ∈ blocksOf (node :: rest) ++ seen := by
  rw [List.mem_append, visit_support]
  cases node <;> simp [blocksOf, or_assoc, or_comm, eq_comm]

theorem scan_spec [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (query : δ) (remaining : List (Option β))
    (seen : List β) (owners : Index δ β) (valid : IndexFor entries seen owners) :
    let out := scan entries query remaining seen owners
    Valid entries out ∧
    (∀ block, block ∈ support out ↔ block ∈ blocksOf remaining ++ seen) ∧
    (∀ block, out.owners query = some block ↔
      block ∈ blocksOf remaining ++ seen ∧ query ∈ entries block) ∧
    (∃ consumed, remaining = consumed ++ out.remaining) := by
  induction remaining generalizing seen owners with
  | nil =>
    cases hit : owners query <;>
      simp only [scan, hit] <;>
      exact ⟨valid, fun _ => Iff.rfl, fun b => by simpa [blocksOf, hit] using valid query b,
        ⟨[], rfl⟩⟩
  | cons node rest ih =>
    cases hit : owners query with
    | some owner =>
      simp only [scan, hit]
      refine ⟨valid, fun _ => Iff.rfl, ?_, ⟨[], rfl⟩⟩
      intro block
      constructor
      · intro found
        have h := (valid query block).mp (hit.trans found)
        exact ⟨List.mem_append_right _ h.1, h.2⟩
      · intro found
        have owned := (valid query owner).mp hit
        have equal := unique owner block query owned.2 found.2
        simp [equal]
    | none =>
      simp only [scan, hit]
      have nextValid := visit_valid entries unique node seen owners valid
      rcases ih _ _ nextValid with ⟨v, s, a, consumed, split⟩
      refine ⟨v, ?_, ?_, ?_⟩
      · intro block
        exact (s block).trans (step_support entries node rest seen owners block)
      · intro block
        rw [a block, step_support entries node rest seen owners block]
      · exact ⟨node :: consumed, congrArg (List.cons node) split⟩

theorem scan_visited_projection [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (query : δ) (remaining : List (Option β))
    (seen : List β) (owners : Index δ β) :
    let out := scan entries query remaining seen owners
    ∃ consumed, remaining = consumed ++ out.remaining ∧
      ∀ block, block ∈ out.seen ↔ block ∈ blocksOf consumed ++ seen := by
  induction remaining generalizing seen owners with
  | nil =>
    cases h : owners query <;> simp only [scan, h] <;>
      exact ⟨[], rfl, fun _ => by simp [blocksOf]⟩
  | cons node rest ih =>
    cases h : owners query with
    | some owner =>
      simp only [scan, h]
      exact ⟨[], rfl, fun _ => by simp [blocksOf]⟩
    | none =>
      simp only [scan, h]
      rcases ih (visit entries node seen owners).1 (visit entries node seen owners).2 with
        ⟨consumed, split, same⟩
      exact ⟨node :: consumed, congrArg (List.cons node) split,
        fun b => (same b).trans (step_support entries node consumed seen owners b)⟩

theorem partial_domain_is_visited_prefix [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (query : δ)
    (state : Cursor δ β) (valid : Valid entries state) :
    let out := lookup entries query state
    ∃ consumed, state.remaining = consumed ++ out.remaining ∧
      ∀ entry block, out.owners entry = some block ↔
        block ∈ blocksOf consumed ++ state.seen ∧ entry ∈ entries block := by
  rcases scan_visited_projection entries query state.remaining state.seen state.owners with
    ⟨consumed, split, same⟩
  have result := (scan_spec entries unique query state.remaining state.seen state.owners valid).1
  refine ⟨consumed, split, ?_⟩
  intro entry block
  exact (result entry block).trans (and_congr_left (fun _ => same block))

theorem cached_query_does_not_advance [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (state : Cursor δ β) (query : δ) (owner : β)
    (hit : state.owners query = some owner) : lookup entries query state = state := by
  cases state with
  | mk remaining seen owners =>
    change owners query = some owner at hit
    cases remaining <;> simp only [lookup, scan, hit]

theorem lookup_matches_full_index [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (state : Cursor δ β)
    (valid : Valid entries state) (query : δ) :
    (lookup entries query state).owners query = freshIndex entries (support state) query := by
  have result := (scan_spec entries unique query state.remaining state.seen state.owners valid).2.2.1
  have agree : ∀ block, (lookup entries query state).owners query = some block ↔
      freshIndex entries (support state) query = some block := by
    intro block
    exact (result block).trans (fresh_index_correct entries unique (support state) query block).symm
  cases left : (lookup entries query state).owners query <;>
    cases right : freshIndex entries (support state) query <;> simp_all

theorem covered_lookup_succeeds [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (state : Cursor δ β)
    (valid : Valid entries state) (query : δ) (block : β)
    (covered : block ∈ support state) (member : query ∈ entries block) :
    (lookup entries query state).owners query = some block := by
  rw [lookup_matches_full_index entries unique state valid query]
  exact covered_lookup_total entries unique (support state) query block covered member

def initial (sources : List (Option β)) : Cursor δ β := ⟨sources, [], fun _ => none⟩

def queryMany [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (queries : List δ) (state : Cursor δ β) : Cursor δ β :=
  queries.foldl (fun current query => lookup entries query current) state

theorem sequential_invariant [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (unique : UniqueOwner entries) (queries : List δ) (state : Cursor δ β)
    (valid : Valid entries state) :
    Valid entries (queryMany entries queries state) ∧
    (∀ block, block ∈ support (queryMany entries queries state) ↔ block ∈ support state) ∧
    (∃ consumed, state.remaining = consumed ++ (queryMany entries queries state).remaining) := by
  induction queries generalizing state with
  | nil => exact ⟨valid, fun _ => Iff.rfl, ⟨[], rfl⟩⟩
  | cons query rest ih =>
    have step := scan_spec entries unique query state.remaining state.seen state.owners valid
    rcases ih (lookup entries query state) step.1 with ⟨v, s, consumed, split⟩
    refine ⟨v, fun b => (s b).trans (step.2.1 b), ?_⟩
    rcases step.2.2.2 with ⟨front, first⟩
    change state.remaining = front ++ (lookup entries query state).remaining at first
    refine ⟨front ++ consumed, ?_⟩
    change state.remaining = (front ++ consumed) ++ (queryMany entries rest (lookup entries query state)).remaining
    rw [first, split, List.append_assoc]

theorem scan_seen_monotone [DecidableEq β] [DecidableEq δ] (entries : β → List δ)
    (query : δ) (remaining : List (Option β)) (seen : List β) (owners : Index δ β)
    (block : β) (member : block ∈ seen) :
    block ∈ (scan entries query remaining seen owners).seen := by
  induction remaining generalizing seen owners with
  | nil => cases h : owners query <;> simpa [scan, h] using member
  | cons node rest ih =>
    cases h : owners query with
    | some owner => simpa [scan, h] using member
    | none =>
      simp only [scan, h]
      exact ih _ _ ((visit_support entries node seen owners block).mpr (Or.inr member))

theorem lookup_preserves_cached [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (state : Cursor δ β)
    (valid : Valid entries state) (query cached : δ) (owner : β)
    (hit : state.owners cached = some owner) :
    (lookup entries query state).owners cached = some owner := by
  have old := (valid cached owner).mp hit
  have next := (scan_spec entries unique query state.remaining state.seen state.owners valid).1
  exact (next cached owner).mpr
    ⟨scan_seen_monotone entries query state.remaining state.seen state.owners owner old.1, old.2⟩

theorem scan_miss_exhausts [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (query : δ) (remaining : List (Option β))
    (seen : List β) (owners : Index δ β)
    (miss : (scan entries query remaining seen owners).owners query = none) :
    (scan entries query remaining seen owners).remaining = [] := by
  induction remaining generalizing seen owners with
  | nil => cases h : owners query <;> simp [scan, h]
  | cons node rest ih =>
    cases h : owners query with
    | some owner => simp [scan, h] at miss
    | none =>
      simp only [scan, h] at miss ⊢
      exact ih _ _ miss

theorem after_history_covered_lookup [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries)
    (sources : List (Option β)) (history : List δ) (query : δ) (owner : β)
    (covered : owner ∈ blocksOf sources) (member : query ∈ entries owner) :
    (lookup entries query (queryMany entries history (initial sources))).owners query = some owner := by
  have invariant := sequential_invariant entries unique history (initial sources) (empty_index entries)
  apply covered_lookup_succeeds entries unique _ invariant.1 query owner _ member
  exact (invariant.2.1 owner).mpr (by simpa [support, initial] using covered)

abbrev Prefix (π : Type) := π × Priority

def prefixOf (key : Key π β) : Prefix π := (key.property, key.priority)

def prefixFor (property : π) (priority : Priority) : Prefix π :=
  (property, unimportantPriority priority)

def prefixFold [DecidableEq π] (keys : List (Key π β)) : Prefix π → Bool :=
  keys.foldl (fun stored key => insertSet stored (prefixOf key)) (fun _ => false)

theorem prefix_fold_projection [DecidableEq π] (keys : List (Key π β)) (p : Prefix π) :
    prefixFold keys p = decide (p ∈ keys.map prefixOf) := by
  have equal : prefixFold keys = buildSet (keys.map prefixOf) := by
    simp only [prefixFold, buildSet, List.foldl_map]
  rw [equal, built_set_membership]

theorem full_key_implies_prefix [DecidableEq π] [DecidableEq β]
    (keys : List (Key π β)) (key : Key π β) (member : buildSet keys key = true) :
    prefixFold keys (prefixOf key) = true := by
  rw [built_set_membership] at member
  rw [prefix_fold_projection]
  exact decide_eq_true (List.mem_map.mpr ⟨key, of_decide_eq_true member, rfl⟩)

theorem prefix_is_exact_projection [DecidableEq π] [DecidableEq β]
    (keys : List (Key π β)) (p : Prefix π) :
    prefixFold keys p = true ↔ ∃ key, buildSet keys key = true ∧ prefixOf key = p := by
  simp only [prefix_fold_projection, built_set_membership, decide_eq_true_eq, List.mem_map]

theorem cold_false_without_prefix [DecidableEq π] [DecidableEq δ]
    (entries : β → List δ) (keys : List (Key π β)) (property : π)
    (priority : Priority) (query : δ)
    (absent : prefixFor property priority ∉ keys.map prefixOf) :
    coldExcluded entries keys property priority query = false := by
  induction keys with
  | nil => rfl
  | cons key rest ih =>
    have split : prefixFor property priority ≠ prefixOf key ∧
        prefixFor property priority ∉ rest.map prefixOf := by simpa using absent
    rw [coldExcluded, List.any_cons]
    have restFalse := ih split.2
    simp only [coldExcluded] at restFalse
    rw [restFalse]
    cases key with
    | mk p v b =>
      by_cases a : p = property <;> by_cases c : v = unimportantPriority priority
      · exact False.elim (split.1 (by simp [prefixFor, prefixOf, a, c]))
      · simp [a, c]
      · simp [a, c]
      · simp [a, c]

def check [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (keys : List (Key π β)) (property : π)
    (priority : Priority) (query : δ) (state : Cursor δ β) : Bool × Cursor δ β :=
  if prefixFold keys (prefixFor property priority) then
    let next := lookup entries query state
    let answer := match next.owners query with
      | none => false
      | some block => buildSet keys (makeKey property priority block)
    (answer, next)
  else (false, state)

theorem absent_prefix_avoids_lookup [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (keys : List (Key π β)) (property : π)
    (priority : Priority) (query : δ) (state : Cursor δ β)
    (absent : prefixFold keys (prefixFor property priority) = false) :
    check entries keys property priority query state = (false, state) := by
  simp [check, absent]

theorem check_valid [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (state : Cursor δ β)
    (valid : Valid entries state) :
    Valid entries (check entries keys property priority query state).2 := by
  simp only [check]
  split
  · exact (scan_spec entries unique query state.remaining state.seen state.owners valid).1
  · exact valid

theorem prefix_gate_equivalence [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (state : Cursor δ β)
    (valid : Valid entries state)
    (coverage : prefixFold keys (prefixFor property priority) = true →
      ∃ owner ∈ support state, query ∈ entries owner) :
    (check entries keys property priority query state).1 =
      coldExcluded entries keys property priority query := by
  cases h : prefixFold keys (prefixFor property priority) with
  | false =>
    rw [absent_prefix_avoids_lookup entries keys property priority query state h]
    rw [prefix_fold_projection] at h
    exact (cold_false_without_prefix entries keys property priority query
      (of_decide_eq_false h)).symm
  | true =>
    simp only [check, h, ↓reduceIte]
    rw [lookup_matches_full_index entries unique state valid query]
    exact indexed_exclusion_matches_cold entries unique (support state) keys property priority query
      (coverage h)

theorem complete_gate_equivalence [DecidableEq π] [DecidableEq β] [DecidableEq δ]
    (entries : β → List δ) (unique : UniqueOwner entries) (keys : List (Key π β))
    (property : π) (priority : Priority) (query : δ) (state : Cursor δ β)
    (valid : Valid entries state)
    (coverage : prefixFold keys (prefixFor property priority) = true →
      ∃ owner ∈ support state, query ∈ entries owner) (included fast cutoffAllows : Bool) :
    (included && !(fast && (!cutoffAllows || (check entries keys property priority query state).1))) =
    (included && !(fast && (!cutoffAllows || coldExcluded entries keys property priority query))) := by
  rw [prefix_gate_equivalence entries unique keys property priority query state valid coverage]

def exampleEntries (block : Nat) := [2 * block, 2 * block + 1]
def exampleSources : List (Option Nat) := [some 0, none, some 1, some 0, some 2]

theorem stops_before_untouched_suffix :
    (lookup exampleEntries 2 (initial exampleSources)).remaining = [some 0, some 2] ∧
    (lookup exampleEntries 2 (initial exampleSources)).owners 3 = some 1 := by decide

theorem revisit_duplicate_exhaustion :
    let state := queryMany exampleEntries [2, 0, 5, 2] (initial exampleSources)
    state.remaining = [] ∧ (lookup exampleEntries 99 state).owners 99 = none ∧
      (lookup exampleEntries 0 state).owners 0 = some 0 ∧ state.seen = [2, 1, 0] := by decide

#print axioms scan_spec
#print axioms scan_visited_projection
#print axioms partial_domain_is_visited_prefix
#print axioms lookup_matches_full_index
#print axioms covered_lookup_succeeds
#print axioms sequential_invariant
#print axioms cached_query_does_not_advance
#print axioms lookup_preserves_cached
#print axioms scan_miss_exhausts
#print axioms after_history_covered_lookup
#print axioms prefix_fold_projection
#print axioms prefix_is_exact_projection
#print axioms full_key_implies_prefix
#print axioms cold_false_without_prefix
#print axioms absent_prefix_avoids_lookup
#print axioms check_valid
#print axioms prefix_gate_equivalence
#print axioms complete_gate_equivalence
#print axioms stops_before_untouched_suffix
#print axioms revisit_duplicate_exhaustion

end ShadowOrder.IncrementalIndex
