import Std

namespace Recovery

inductive Kind where
  | paren | square | curly
  deriving DecidableEq, Repr

inductive Token where
  | open (kind : Kind)
  | close (kind : Kind)
  | atom (value : Nat)
  deriving DecidableEq, Repr

def advance : List Kind → Token → List Kind
  | stack, .open k => k :: stack
  | k :: stack, .close c => if c = k then stack else k :: stack
  | stack, _ => stack

theorem stack_empty_only_on_matching_last (k stack t) :
    advance (k :: stack) t = [] ↔ stack = [] ∧ t = .close k := by
  cases t with
  | «open» child => simp [advance]
  | atom value => simp [advance]
  | close child =>
    by_cases h : child = k
    · subst child; simp [advance]
    · simp [advance, h]

def run : List Kind → List Token → List Token
  | [], input => input
  | _ :: _, [] => []
  | k :: stack, t :: input => run (advance (k :: stack) t) input
termination_by structural _ input => input

inductive Leaf (owner : Kind) : Token → Prop where
  | atom (value) : Leaf owner (.atom value)
  | mismatch (other) (different : other ≠ owner) : Leaf owner (.close other)

inductive Body : Kind → List Token → Prop where
  | empty (owner) : Body owner []
  | leaf (owner token rest) : Leaf owner token → Body owner rest → Body owner (token :: rest)
  | nested (owner child inside rest) : Body child inside → Body owner rest →
      Body owner (.open child :: inside ++ .close child :: rest)

theorem leaf_advance (h : Leaf k t) (stack) : advance (k :: stack) t = k :: stack := by
  cases h with
  | atom => rfl
  | mismatch other different => simp [advance, different]

theorem grammar_cleanup (h : Body k body) :
    ∀ stack tail, run (k :: stack) (body ++ .close k :: tail) = run stack tail := by
  induction h with
  | empty owner => intro stack tail; simp [run, advance]
  | leaf owner token rest leaf _ ih =>
    intro stack tail
    simp only [List.cons_append, run, leaf_advance leaf]
    exact ih stack tail
  | nested owner child inside rest _ _ childIH restIH =>
    intro stack tail
    simp only [List.cons_append, List.append_assoc, run, advance]
    rw [childIH]
    exact restIH stack tail

theorem body_without_closer (h : Body k body) : ∀ stack, run (k :: stack) body = [] := by
  induction h with
  | empty owner => intro stack; rfl
  | leaf owner token rest leaf _ ih =>
    intro stack
    simp only [run, leaf_advance leaf]
    exact ih stack
  | nested owner child inside rest childBody _ _ restIH =>
    intro stack
    simp only [List.cons_append, run, advance]
    rw [grammar_cleanup childBody]
    exact restIH stack

inductive AtEOF : Kind → List Token → Prop where
  | outer (body) : Body k body → AtEOF k body
  | child (body child rest) : Body k body → AtEOF child rest →
      AtEOF k (body ++ .open child :: rest)

theorem body_prefix (h : Body k body) :
    ∀ stack tail, run (k :: stack) (body ++ tail) = run (k :: stack) tail := by
  induction h with
  | empty owner => intro stack tail; rfl
  | leaf owner token rest leaf _ ih =>
    intro stack tail
    simp only [List.cons_append, run, leaf_advance leaf]
    exact ih stack tail
  | nested owner child inside rest childBody _ _ restIH =>
    intro stack tail
    simp only [List.cons_append, List.append_assoc, run, advance]
    rw [grammar_cleanup childBody]
    exact restIH stack tail

theorem eof_cleanup (h : AtEOF k input) : ∀ stack, run (k :: stack) input = [] := by
  induction h with
  | outer body h => exact body_without_closer h
  | child body child rest h _ ih =>
    intro stack
    rw [body_prefix h]
    simp only [run, advance]
    exact ih (_ :: stack)

theorem remaining_suffix (input : List Token) (stack : List Kind) :
    ∃ consumed, input = consumed ++ run stack input := by
  induction input generalizing stack with
  | nil => cases stack <;> exact ⟨[], rfl⟩
  | cons t input ih =>
    cases stack with
    | nil => exact ⟨[], rfl⟩
    | cons k stack =>
      obtain ⟨consumed, h⟩ := ih (advance (k :: stack) t)
      exact ⟨t :: consumed, by simpa only [List.cons_append, run] using congrArg (List.cons t) h⟩

theorem remaining_length (input : List Token) (stack) : (run stack input).length ≤ input.length := by
  obtain ⟨consumed, h⟩ := remaining_suffix input stack
  have lengths := congrArg List.length h
  simp only [List.length_append] at lengths
  omega

theorem active_progress (k stack t input) :
    (run (k :: stack) (t :: input)).length < (t :: input).length := by
  simpa only [run, List.length_cons] using Nat.lt_succ_of_le (remaining_length input (advance (k :: stack) t))

theorem empty_input (stack) : run stack [] = [] := by cases stack <;> rfl

def cleanup (kind : Kind) (input : List Token) := run [kind] input

theorem cleanup_exact_suffix (h : Body k body) (tail) :
    cleanup k (body ++ .close k :: tail) = tail := by
  simpa only [cleanup, run] using grammar_cleanup h [] tail

theorem cleanup_eof (h : AtEOF k input) : cleanup k input = [] := eof_cleanup h []

structure State where
  pending : Option Kind
  input : List Token
  depth : Nat
  limit : Nat
  stop : Option Kind
  deriving DecidableEq, Repr

inductive Error where
  | noOpener | tooDeep
  deriving DecidableEq, Repr

def rejected (s : State) : Except Error State :=
  match s.pending with
  | none => .error .noOpener
  | some k => .ok { s with pending := none, input := cleanup k s.input }

def rejectedOriginal (s : State) : Except Error State :=
  match s.pending with
  | none => .error .noOpener
  | some _ => .ok { s with pending := none }

def atLimit (s : State) : Prop := s.depth ≥ s.limit ∧ s.limit ≠ 0

structure RejectionResult where
  state : State
  error : Error
  deriving DecidableEq, Repr

def rejectAtLimit (s : State) : Option RejectionResult :=
  if s.depth ≥ s.limit ∧ s.limit ≠ 0 then
    match rejected s with
    | .error _ => none
    | .ok result => some ⟨result, .tooDeep⟩
  else none

theorem rejection_preserves_context (s result) (h : rejected s = .ok result) :
    result.depth = s.depth ∧ result.limit = s.limit ∧ result.stop = s.stop ∧ result.pending = none := by
  cases hp : s.pending with
  | none => simp [rejected, hp] at h
  | some k => simp [rejected, hp] at h; cases h; simp

theorem limit_zero_not_rejected (s : State) (h : s.limit = 0) : rejectAtLimit s = none := by
  simp [rejectAtLimit, h]

theorem limit_recovery (s : State) (limit : atLimit s) (pending : s.pending = some k)
    (body : Body k content) (input : s.input = content ++ .close k :: tail) :
    rejectAtLimit s = some ⟨{s with pending := none, input := tail}, .tooDeep⟩ := by
  simp only [rejectAtLimit, atLimit] at *
  rw [ite_eq_left limit]
  simp only [rejected, pending, input, cleanup_exact_suffix body]

theorem limit_eof_recovery (s : State) (limit : atLimit s) (pending : s.pending = some k)
    (eof : AtEOF k s.input) :
    rejectAtLimit s = some ⟨{s with pending := none, input := []}, .tooDeep⟩ := by
  simp only [rejectAtLimit, atLimit] at *
  rw [ite_eq_left limit]
  simp only [rejected, pending, cleanup_eof eof]

theorem parent_after_rejection (childBody : Body child inside) (parentBody : Body parent rest)
    (tail) :
    cleanup parent (cleanup child (inside ++ .close child :: rest ++ .close parent :: tail)) = tail := by
  rw [show inside ++ .close child :: rest ++ .close parent :: tail =
    inside ++ .close child :: (rest ++ .close parent :: tail) by simp [List.append_assoc]]
  rw [cleanup_exact_suffix childBody, cleanup_exact_suffix parentBody]

def witness : State := ⟨some .paren, [.atom 0, .close .paren, .atom 1, .atom 2, .close .paren, .atom 3], 75, 75, some .paren⟩

theorem old_parent_exposes_inner :
    (match rejectedOriginal witness with | .ok s => cleanup .paren s.input | _ => []) =
    [.atom 1, .atom 2, .close .paren, .atom 3] := by decide

theorem repaired_parent_hides_inner :
    (match rejected witness with | .ok s => cleanup .paren s.input | _ => []) = [.atom 3] := by decide

theorem mismatched_closer_not_a_stop :
    cleanup .square [.close .paren, .atom 1, .close .square, .atom 2] = [.atom 2] := by decide

theorem nested_semicolon_not_a_stop :
    cleanup .paren [.open .square, .atom 1, .close .square, .atom 2, .close .paren, .atom 3] = [.atom 3] := by decide

end Recovery
