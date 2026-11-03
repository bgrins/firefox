import Links

namespace GlobalDeclarationLinks
open DeclarationCapacity (Declaration)
open DeclarationLinks (Path Represents put)

structure State where
  vector : List Declaration
  head : Nat → Nat
  tail : Nat → Nat
  next : Nat → Nat

def empty (sentinel : Nat) : State := ⟨[], fun _ => sentinel, fun _ => sentinel, fun _ => 0⟩

def view (s : State) (property : Nat) : DeclarationLinks.State :=
  ⟨s.vector, s.head property, s.tail property, s.next⟩

def note (mapping : Nat → Option Nat) (sentinel : Nat) (s : State) (d : Declaration) : State :=
  let n := s.vector.length
  let base := { s with vector := s.vector ++ [d], next := put s.next n 0 }
  match mapping d.property with
  | none => base
  | some p =>
      if n < sentinel then
        if s.head p = sentinel then
          { base with head := put s.head p n, tail := put s.tail p n }
        else { base with tail := put s.tail p n, next := put base.next (s.tail p) n }
      else base

def build (mapping : Nat → Option Nat) (sentinel : Nat) (s : State)
    (ds : List Declaration) : State := ds.foldl (note mapping sentinel) s

def Owned (mapping : Nat → Option Nat) (vector : List Declaration) (p : Nat)
    (xs : List Nat) : Prop :=
  ∀ i, i ∈ xs → ∃ d, vector[i]? = some d ∧ mapping d.property = some p

def Invariant (mapping : Nat → Option Nat) (sentinel : Nat) (s : State)
    (chains : Nat → List Nat) : Prop :=
  ∀ p, Represents sentinel (view s p) (chains p) ∧ Owned mapping s.vector p (chains p)

def advance (mapping : Nat → Option Nat) (sentinel n : Nat) (d : Declaration)
    (chains : Nat → List Nat) (p : Nat) : List Nat :=
  chains p ++ if mapping d.property = some p ∧ n < sentinel then [n] else []

theorem path_tail_member (path : Path heap first last xs) : last ∈ xs := by
  induction path with
  | one => simp
  | more _ _ _ ih => simp [ih]

theorem owned_indices_allocated (owned : Owned mapping vector p xs) (member : i ∈ xs) :
    i < vector.length := by
  obtain ⟨d, lookup, _⟩ := owned i member
  exact (List.getElem?_eq_some_iff.mp lookup).choose

theorem owned_chains_disjoint (left : Owned mapping vector p xs)
    (right : Owned mapping vector q ys) (different : p ≠ q) :
    ∀ i, i ∈ xs → i ∉ ys := by
  intro i hx hy
  obtain ⟨d, hd, hp⟩ := left i hx
  obtain ⟨e, he, hq⟩ := right i hy
  have same : d = e := by rw [hd] at he; exact Option.some.inj he
  subst e
  rw [hp] at hq
  exact different (Option.some.inj hq)

theorem owned_append (owned : Owned mapping vector p xs) (d : Declaration) :
    Owned mapping (vector ++ [d]) p xs := by
  intro i member
  obtain ⟨e, lookup, hp⟩ := owned i member
  refine ⟨e, ?_, hp⟩
  rw [List.getElem?_append_left (owned_indices_allocated owned member)]
  exact lookup

theorem owned_advance (owned : Owned mapping vector p (chains p)) :
    Owned mapping (vector ++ [d]) p (advance mapping sentinel vector.length d chains p) := by
  intro i member
  simp only [advance, List.mem_append] at member
  rcases member with old | new
  · exact owned_append owned d i old
  · split at new
    next admit =>
      simp only [List.mem_singleton] at new
      subst i
      exact ⟨d, by simp, admit.1⟩
    next => simp at new

theorem note_vector (mapping : Nat → Option Nat) (sentinel : Nat) (s : State) (d : Declaration) :
    (note mapping sentinel s d).vector = s.vector ++ [d] := by
  simp only [note]
  split <;> (try split) <;> (try split) <;> rfl

theorem initialized_rep (rep : Represents sentinel (view s p) xs) :
    Represents sentinel (view {s with vector := s.vector ++ [d],
      next := put s.next s.vector.length 0} p) xs := by
  rcases rep with ⟨hx, hh, ht⟩ | ⟨path, allocated, bounded⟩
  · exact Or.inl ⟨hx, hh, ht⟩
  · apply Or.inr
    refine ⟨DeclarationLinks.path_heap_agrees path ?_, ?_, bounded⟩
    · intro i hi
      change i ≤ s.tail p at hi
      change s.tail p < s.vector.length at allocated
      simp [view, put, show i ≠ s.vector.length by omega]
    · change s.tail p < (s.vector ++ [d]).length
      change s.tail p < s.vector.length at allocated
      simp only [List.length_append, List.length_singleton]; omega

theorem note_preserves (inv : Invariant mapping sentinel s chains) :
    Invariant mapping sentinel (note mapping sentinel s d)
      (advance mapping sentinel s.vector.length d chains) := by
  intro p
  refine ⟨?_, ?_⟩
  · cases mapped : mapping d.property with
    | none =>
        simpa [note, mapped, advance] using initialized_rep (d := d) (inv p).1
    | some q =>
        by_cases bound : s.vector.length < sentinel
        · by_cases same : p = q
          · subst p
            rcases (inv q).1 with ⟨hx, hh, ht⟩ | ⟨path, allocated, bounded⟩
            · change s.head q = sentinel at hh
              simp only [note, mapped, bound, ite_true, hh, advance, hx, List.nil_append]
              apply Or.inr
              refine ⟨?_, ?_, ?_⟩
              · apply Path.one
                simp [view, put]
              · simpa [view, put] using Nat.lt_succ_self s.vector.length
              · simpa [view, put] using bound
            · have upper := DeclarationLinks.path_first_le_last path
              have hh : s.head q ≠ sentinel := by change s.head q ≤ s.tail q at upper; change s.tail q < sentinel at bounded; omega
              simp only [note, mapped, bound, ite_true, hh, ite_false, advance]
              apply Or.inr
              refine ⟨?_, ?_, ?_⟩
              · simpa [view, put] using DeclarationLinks.path_append path allocated
              · simpa [view, put] using Nat.lt_succ_self s.vector.length
              · simpa [view, put] using bound
          · have pq : p ≠ q := same
            have qp : q ≠ p := Ne.symm pq
            have untouched := initialized_rep (d := d) (inv p).1
            by_cases head : s.head q = sentinel
            · simpa [note, mapped, bound, head, advance, pq, qp, view, put] using untouched
            · have outside : s.tail q ∉ chains p := by
                rcases (inv q).1 with ⟨_, hq, _⟩ | ⟨pathq, _, _⟩
                · exact False.elim (head hq)
                · exact owned_chains_disjoint (inv q).2 (inv p).2 qp _ (path_tail_member pathq)
              rcases untouched with ⟨hx, hh, ht⟩ | ⟨path, allocated, bounded⟩
              · simp only [note, mapped, bound, ite_true, head, ite_false, advance]
                simpa [view, put, pq, qp] using (Or.inl ⟨hx, hh, ht⟩ :
                  Represents sentinel (view {s with vector := s.vector ++ [d],
                    next := put (put s.next s.vector.length 0) (s.tail q) s.vector.length} p) (chains p))
              · simp only [note, mapped, bound, ite_true, head, ite_false, advance]
                have path' := DeclarationLinks.unrelated_heap_update (value := s.vector.length) path outside
                simpa [view, put, pq, qp] using
                  (Or.inr ⟨path', allocated, bounded⟩ :
                    Represents sentinel (view {s with vector := s.vector ++ [d],
                      next := put (put s.next s.vector.length 0) (s.tail q) s.vector.length} p) (chains p))
        · simpa [note, mapped, bound, advance] using initialized_rep (d := d) (inv p).1
  · rw [note_vector]
    exact owned_advance (inv p).2

def admitted (mapping : Nat → Option Nat) (sentinel p offset : Nat) : List Declaration → List Nat
  | [] => []
  | d :: ds => (if mapping d.property = some p ∧ offset < sentinel then [offset] else []) ++
      admitted mapping sentinel p (offset + 1) ds

def projection (mapping : Nat → Option Nat) (p offset : Nat) : List Declaration → List Nat
  | [] => []
  | d :: ds => (if mapping d.property = some p then [offset] else []) ++
      projection mapping p (offset + 1) ds

theorem build_vector (mapping : Nat → Option Nat) (sentinel : Nat) (s : State) (ds : List Declaration) :
    (build mapping sentinel s ds).vector = s.vector ++ ds := by
  induction ds generalizing s with
  | nil => simp [build]
  | cons d ds ih => simpa [build, note_vector, List.append_assoc] using ih (note mapping sentinel s d)

theorem build_preserves (inv : Invariant mapping sentinel s chains) (ds : List Declaration) :
    Invariant mapping sentinel (build mapping sentinel s ds)
      (fun p => chains p ++ admitted mapping sentinel p s.vector.length ds) := by
  induction ds generalizing s chains with
  | nil => simpa [build, admitted] using inv
  | cons d ds ih =>
      have rest := ih (note_preserves (d := d) inv)
      simpa [build, advance, admitted, note_vector, List.append_assoc] using rest

theorem empty_invariant (mapping : Nat → Option Nat) (sentinel : Nat) :
    Invariant mapping sentinel (empty sentinel) (fun _ => []) := by
  intro p
  refine ⟨Or.inl ⟨rfl, rfl, rfl⟩, ?_⟩
  intro i h
  simp at h

theorem fresh_global_invariant (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration) :
    Invariant mapping sentinel (build mapping sentinel (empty sentinel) ds)
      (fun p => admitted mapping sentinel p 0 ds) := by
  simpa [empty] using build_preserves (empty_invariant mapping sentinel) ds

theorem all_chains_read_admitted (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration) :
    ∀ p, DeclarationLinks.read sentinel (view (build mapping sentinel (empty sentinel) ds) p) =
      admitted mapping sentinel p 0 ds := by
  intro p
  exact DeclarationLinks.represented_read (fresh_global_invariant mapping sentinel ds p).1

theorem admitted_complete (bound : offset + ds.length ≤ sentinel) :
    admitted mapping sentinel p offset ds = projection mapping p offset ds := by
  induction ds generalizing offset with
  | nil => rfl
  | cons d ds ih =>
      have here : offset < sentinel := by simp only [List.length_cons] at bound; omega
      have rest : offset + 1 + ds.length ≤ sentinel := by simp only [List.length_cons] at bound; omega
      simp only [admitted, projection, here, and_true, ih rest]

theorem all_chains_complete (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration)
    (bound : ds.length ≤ sentinel) :
    ∀ p, DeclarationLinks.read sentinel (view (build mapping sentinel (empty sentinel) ds) p) =
      projection mapping p 0 ds := by
  intro p
  rw [all_chains_read_admitted]
  exact admitted_complete (by simpa using bound)

theorem final_chains_disjoint (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration)
    (different : p ≠ q) :
    ∀ i, i ∈ admitted mapping sentinel p 0 ds → i ∉ admitted mapping sentinel q 0 ds := by
  exact owned_chains_disjoint (fresh_global_invariant mapping sentinel ds p).2
    (fresh_global_invariant mapping sentinel ds q).2 different

theorem final_head_tail_bounds (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration) :
    ∀ p, let s := build mapping sentinel (empty sentinel) ds
      (s.head p = sentinel ∧ s.tail p = sentinel) ∨
      (s.head p ≤ s.tail p ∧ s.tail p < ds.length ∧ s.tail p < sentinel) := by
  intro p
  rcases (fresh_global_invariant mapping sentinel ds p).1 with ⟨_, hh, ht⟩ | ⟨path, allocated, bounded⟩
  · exact Or.inl ⟨hh, ht⟩
  · apply Or.inr
    refine ⟨DeclarationLinks.path_first_le_last path, ?_, bounded⟩
    simpa [view, build_vector, empty] using allocated

theorem all_vector_entries_retained (mapping : Nat → Option Nat) (sentinel : Nat) (ds : List Declaration) :
    (build mapping sentinel (empty sentinel) ds).vector = ds := by
  simpa [empty] using build_vector mapping sentinel (empty sentinel) ds

def testMapping (id : Nat) : Option Nat := if id = 2 then none else some id
def a : Declaration := ⟨0, 37⟩
def b : Declaration := ⟨1, 40⟩
def unrelated : Declaration := ⟨2, 0⟩
def fixture : State := build testMapping 8 (empty 8) [a, b, unrelated, a, b]

theorem interleaved_shared_heap :
    fixture.head 0 = 0 ∧ fixture.tail 0 = 3 ∧ fixture.next 0 = 3 ∧
    fixture.head 1 = 1 ∧ fixture.tail 1 = 4 ∧ fixture.next 1 = 4 ∧
    DeclarationLinks.read 8 (view fixture 0) = [0, 3] ∧
    DeclarationLinks.read 8 (view fixture 1) = [1, 4] := by decide

end GlobalDeclarationLinks
