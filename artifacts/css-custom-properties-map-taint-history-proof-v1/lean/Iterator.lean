import Std

namespace MapIterator

abbrev Entry (K V : Type) := K × Option V
abbrev Node (K V : Type) := List (Entry K V)
abbrev Chain (K V : Type) := List (Node K V)

variable {K V : Type} [DecidableEq K]

def owns (n : Node K V) (k : K) : Bool := n.any (fun e => e.1 == k)
def shadow (ds : Chain K V) (k : K) : Bool := ds.any (fun n => owns n k)
def visible (ds : Chain K V) (e : Entry K V) : Bool := !shadow ds e.1

def reference : Chain K V → Node K V
  | [] => []
  | n :: ps => n ++ (reference ps).filter (fun e => !owns n e.1)

structure Cursor (K V : Type) where
  current : Node K V
  suffix : Node K V
  parents : Chain K V
  descendants : Chain K V
deriving Repr, DecidableEq

def start : Chain K V → Cursor K V
  | [] => ⟨[], [], [], []⟩
  | n :: ps => ⟨n, n, ps, []⟩

def rank (s : Cursor K V) : Nat :=
  s.suffix.length + s.parents.foldr (fun n z => n.length + 1 + z) 0

inductive Action (K V : Type) where
  | done
  | skip (next : Cursor K V)
  | yield (entry : Entry K V) (next : Cursor K V)
deriving Repr, DecidableEq

def step (s : Cursor K V) : Action K V :=
  match s.suffix with
  | e :: rest =>
    let next := { s with suffix := rest }
    if shadow s.descendants e.1 then .skip next else .yield e next
  | [] => match s.parents with
    | [] => .done
    | p :: ps => .skip ⟨p, p, ps, s.descendants ++ [s.current]⟩

theorem step_rank (s t : Cursor K V)
    (h : step s = .skip t ∨ ∃ e, step s = .yield e t) : rank t < rank s := by
  rcases s with ⟨cur, suf, pars, ds⟩
  cases suf with
  | nil => cases pars <;> simp [step] at h
           case cons p ps => rcases h with rfl; simp [rank]
  | cons a rest =>
    simp only [step] at h
    split at h
    · rcases h with h | h
      · cases h; simp [rank]
      · rcases h with ⟨e,h⟩; cases h
    · rcases h with h | h
      · cases h
      · rcases h with ⟨e,h⟩; cases h; simp [rank]

def walk (ds : Chain K V) (cur suf : Node K V) (ps : Chain K V) : Node K V :=
  match suf with
  | e :: rest =>
    if shadow ds e.1 then walk ds cur rest ps
    else e :: walk ds cur rest ps
  | [] => match ps with
    | [] => []
    | p :: rest => walk (ds ++ [cur]) p p rest
termination_by (ps.length, suf.length)

def drain (s : Cursor K V) : Node K V := walk s.descendants s.current s.suffix s.parents

theorem shadow_append (a b : Chain K V) (k : K) :
    shadow (a ++ b) k = (shadow a k || shadow b k) := by
  simp [shadow]

theorem filter_nested (ds : Chain K V) (n xs : Node K V) :
    (xs.filter (fun e => !owns n e.1)).filter (visible ds) =
      xs.filter (visible (ds ++ [n])) := by
  simp only [List.filter_filter]
  congr 1
  funext e
  simp [visible, shadow, Bool.and_comm]

theorem walk_reference (ds : Chain K V) (cur suf : Node K V) (ps : Chain K V) :
    walk ds cur suf ps =
      suf.filter (visible ds) ++ (reference ps).filter (visible (ds ++ [cur])) := by
  induction ps generalizing ds cur suf with
  | nil =>
    induction suf with
    | nil => simp [walk, reference]
    | cons e rest ih =>
      rw [walk]
      simp only [reference, List.filter_nil, List.append_nil] at *
      by_cases h : shadow ds e.1 = true <;> simp_all [visible]
  | cons p ps ih =>
    induction suf with
    | nil =>
      rw [walk, ih]
      simp only [List.filter_nil, List.nil_append, reference, List.filter_append,
        filter_nested]
    | cons e rest ihs =>
      rw [walk]
      by_cases h : shadow ds e.1 = true <;> simp_all [visible]

theorem initialized_enumeration (c : Chain K V) : drain (start c) = reference c := by
  cases c with
  | nil => simp [drain, start, walk, reference]
  | cons n ps =>
    simp only [drain, start, walk_reference, reference]
    unfold visible shadow
    simp

theorem step_drain (s : Cursor K V) :
    match step s with
    | .done => drain s = []
    | .skip t => drain s = drain t
    | .yield e t => drain s = e :: drain t := by
  rcases s with ⟨cur,suf,ps,ds⟩
  cases suf with
  | nil => cases ps <;> simp [step, drain, walk]
  | cons e rest => by_cases h : shadow ds e.1 = true <;> simp [step, h, drain, walk]

inductive Runs : Cursor K V → Node K V → Prop where
  | done (h : step s = .done) : Runs s []
  | skip (h : step s = .skip t) (tail : Runs t out) : Runs s out
  | yield (h : step s = .yield e t) (tail : Runs t out) : Runs s (e :: out)

theorem runs_exact {s : Cursor K V} {out : Node K V} (h : Runs s out) : out = drain s := by
  induction h with
  | @done s h => have x := step_drain s; simp_all
  | @skip s t out h tail ih => have x := step_drain s; simp_all
  | @yield s e t out h tail ih => have x := step_drain s; simp_all

theorem terminates (s : Cursor K V) : Runs s (drain s) := by
  have h := step_drain s
  generalize hs : step s = a at h
  cases a with
  | done => rw [h]; exact .done hs
  | skip t => rw [h]; exact .skip hs (terminates t)
  | yield e t => rw [h]; exact .yield hs (terminates t)
termination_by rank s
decreasing_by
  · exact step_rank s t (Or.inl hs)
  · exact step_rank s t (Or.inr ⟨e, hs⟩)

theorem traversal_reference {c : Chain K V} {out : Node K V} (h : Runs (start c) out) : out = reference c := by
  rw [runs_exact h, initialized_enumeration]

end MapIterator
