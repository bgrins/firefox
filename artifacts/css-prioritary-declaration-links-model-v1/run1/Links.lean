import Capacity

namespace DeclarationLinks
open DeclarationCapacity

def put (heap : Nat → Nat) (index value : Nat) : Nat → Nat :=
  fun i => if i = index then value else heap i

structure State where
  vector : List Declaration
  head : Nat
  tail : Nat
  next : Nat → Nat

def empty (sentinel : Nat) : State := ⟨[], sentinel, sentinel, fun _ => 0⟩

def note (sentinel target : Nat) (s : State) (d : Declaration) : State :=
  let n := s.vector.length
  let heap := put s.next n 0
  if d.property = target ∧ n < sentinel then
    if s.head = sentinel then ⟨s.vector ++ [d], n, n, heap⟩
    else ⟨s.vector ++ [d], s.head, n, put heap s.tail n⟩
  else ⟨s.vector ++ [d], s.head, s.tail, heap⟩

def build (sentinel target : Nat) (s : State) (ds : List Declaration) : State :=
  ds.foldl (note sentinel target) s

inductive Path (heap : Nat → Nat) : Nat → Nat → List Nat → Prop
  | one (endLink : heap i = 0) : Path heap i i [i]
  | more (link : heap i = j) (increasing : i < j)
      (rest : Path heap j last xs) : Path heap i last (i :: xs)

theorem path_first_le_last (p : Path heap first last xs) : first ≤ last := by
  induction p with
  | one => omega
  | more _ _ _ ih => omega

theorem path_length_bound (p : Path heap first last xs) : xs.length + first ≤ last + 1 := by
  induction p with
  | one => simp
  | more _ _ _ ih => simp only [List.length_cons]; omega

theorem path_nonempty (p : Path heap first last xs) : xs ≠ [] := by
  cases p <;> simp

theorem path_heap_agrees (p : Path heap first last xs)
    (same : ∀ i, i ≤ last → other i = heap i) : Path other first last xs := by
  induction p with
  | one h => exact .one (by rw [same _ (by omega)]; exact h)
  | more h lt rest ih =>
      exact .more (by rw [same _ (by have := path_first_le_last rest; omega)]; exact h)
        lt (ih same)

theorem path_append (p : Path heap first last xs) (fresh : last < n) :
    Path (put (put heap n 0) last n) first n (xs ++ [n]) := by
  induction p with
  | @one i h =>
      apply Path.more (j := n)
      · simp [put]
      · exact fresh
      · apply Path.one
        simp [put, show n ≠ i by omega]
  | @more i j last xs h lt rest ih =>
      have upper := path_first_le_last rest
      apply Path.more (j := j)
      · simpa [put, show i ≠ last by omega, show i ≠ n by omega] using h
      · exact lt
      · exact ih fresh

def Represents (sentinel : Nat) (s : State) (xs : List Nat) : Prop :=
  (xs = [] ∧ s.head = sentinel ∧ s.tail = sentinel) ∨
  (Path s.next s.head s.tail xs ∧ s.tail < s.vector.length ∧ s.tail < sentinel)

theorem empty_represents (sentinel : Nat) : Represents sentinel (empty sentinel) [] := by
  exact Or.inl ⟨rfl, rfl, rfl⟩

theorem note_vector (sentinel target : Nat) (s : State) (d : Declaration) :
    (note sentinel target s d).vector = s.vector ++ [d] := by
  simp only [note]; split <;> (try split) <;> rfl

theorem note_refines (rep : Represents sentinel s xs) :
    Represents sentinel (note sentinel target s d)
      (xs ++ if d.property = target ∧ s.vector.length < sentinel then [s.vector.length] else []) := by
  by_cases admit : d.property = target ∧ s.vector.length < sentinel
  · rcases rep with ⟨rfl, head, tail⟩ | ⟨path, allocated, bounded⟩
    · simp only [note, admit, ite_true, head, List.nil_append]
      exact Or.inr ⟨Path.one (by simp [put]), by simp, admit.2⟩
    · have upper := path_first_le_last path
      have head : s.head ≠ sentinel := by omega
      simp only [note, admit, ite_true, head, ite_false]
      exact Or.inr ⟨path_append path allocated, by simp, admit.2⟩
  · simp only [note, admit, ite_false, List.append_nil]
    rcases rep with ⟨hx, hh, ht⟩ | ⟨path, allocated, bounded⟩
    · exact Or.inl ⟨hx, hh, ht⟩
    · apply Or.inr
      refine ⟨path_heap_agrees path ?_, ?_, bounded⟩
      · intro i hi
        simp [put, show i ≠ s.vector.length by omega]
      · simp only [List.length_append, List.length_singleton]; omega

theorem build_vector (sentinel target : Nat) (s : State) (ds : List Declaration) :
    (build sentinel target s ds).vector = s.vector ++ ds := by
  induction ds generalizing s with
  | nil => simp [build]
  | cons d ds ih =>
      simpa [build, note_vector, List.append_assoc] using ih (note sentinel target s d)

theorem build_refines (rep : Represents sentinel s xs) (ds : List Declaration) :
    Represents sentinel (build sentinel target s ds)
      (xs ++ admitted sentinel target s.vector.length ds) := by
  induction ds generalizing s xs with
  | nil => simpa [build, admitted] using rep
  | cons d ds ih =>
      have step := note_refines (target := target) (d := d) rep
      have rest := ih step
      simpa [build, admitted, note_vector, List.append_assoc] using rest

def walk (heap : Nat → Nat) (current : Nat) : Nat → List Nat
  | 0 => []
  | fuel + 1 => current :: if heap current = 0 then [] else walk heap (heap current) fuel

def read (sentinel : Nat) (s : State) : List Nat :=
  if s.head = sentinel then [] else walk s.next s.head s.vector.length

theorem path_walk (p : Path heap first last xs) (enough : xs.length ≤ fuel) :
    walk heap first fuel = xs := by
  induction p generalizing fuel with
  | @one i h =>
      cases fuel with
      | zero => simp at enough
      | succ fuel => simp [walk, h]
  | @more i j last xs h lt rest ih =>
      cases fuel with
      | zero => simp at enough
      | succ fuel =>
          simp only [List.length_cons, Nat.succ_le_succ_iff] at enough
          simp [walk, h, show j ≠ 0 by omega, ih enough]

theorem represented_read (rep : Represents sentinel s xs) : read sentinel s = xs := by
  rcases rep with ⟨rfl, head, tail⟩ | ⟨path, allocated, bounded⟩
  · simp [read, head]
  · have upper := path_first_le_last path
    have head : s.head ≠ sentinel := by omega
    have length := path_length_bound path
    simp only [read, head, ite_false]
    exact path_walk path (by omega)

theorem fresh_read_admitted (sentinel target : Nat) (ds : List Declaration) :
    read sentinel (build sentinel target (empty sentinel) ds) = admitted sentinel target 0 ds := by
  have rep := build_refines (target := target) (empty_represents sentinel) ds
  simpa [empty] using represented_read rep

theorem bounded_read_complete (sentinel target : Nat) (ds : List Declaration)
    (bounded : ds.length ≤ sentinel) :
    read sentinel (build sentinel target (empty sentinel) ds) = fullProjection target 0 ds := by
  rw [fresh_read_admitted]
  exact admitted_complete sentinel target 0 ds (by simpa using bounded)

theorem all_vector_entries_retained (sentinel target : Nat) (ds : List Declaration) :
    (build sentinel target (empty sentinel) ds).vector = ds := by
  simpa [empty] using build_vector sentinel target (empty sentinel) ds

theorem zero_head_nonempty : read 3 (build 3 0 (empty 3) [font]) = [0] := by decide

theorem links_skip_unrelated :
    let s := build 5 0 (empty 5) [font, color, font]
    s.head = 0 ∧ s.tail = 2 ∧ s.next 0 = 2 ∧ s.next 2 = 0 ∧ read 5 s = [0, 2] := by decide

end DeclarationLinks
