import Std

namespace ChunkOwnership

structure Character where
  unit : Nat
  policy : Nat
  deriving DecidableEq, Repr

structure Native where
  pending : List Character
  captured : Option Nat
  deriving DecidableEq, Repr

def terminal : List Character → Option Nat
  | [] => none
  | [c] => some c.policy
  | _ :: c :: rest => terminal (c :: rest)

theorem terminal_cons_ne_none (c : Character) (cs : List Character) :
    terminal (c :: cs) ≠ none := by
  induction cs generalizing c with
  | nil => simp [terminal]
  | cons d ds ih => exact ih d

@[simp] theorem terminal_cons (c : Character) (cs : List Character) :
    terminal (c :: cs) = (terminal cs).or (some c.policy) := by
  induction cs with
  | nil => rfl
  | cons d ds ih =>
    cases ds with
    | nil => rfl
    | cons e es =>
      simp only [terminal]
      have h := terminal_cons_ne_none e es
      cases he : terminal (e :: es) <;> simp_all

theorem terminal_append (a b : List Character) :
    terminal (a ++ b) = (terminal b).or (terminal a) := by
  induction a with
  | nil => simp [terminal]
  | cons c cs ih =>
    simp only [List.cons_append, terminal_cons, ih]
    cases terminal b <;> cases terminal cs <;> rfl

def submit (s : Native) (characters : List Character) : Native :=
  ⟨s.pending ++ characters, (terminal characters).or s.captured⟩

def coherent (s : Native) : Prop := s.captured = terminal s.pending

theorem empty_cannot_capture (s : Native) : submit s [] = s := by
  cases s; simp [submit, terminal]

theorem coherent_submit (s : Native) (characters : List Character) (h : coherent s) :
    coherent (submit s characters) := by
  simpa [coherent, submit, terminal_append] using congrArg ((terminal characters).or) h

theorem submit_partition (s : Native) (a b : List Character) :
    submit (submit s a) b = submit s (a ++ b) := by
  simp only [submit, terminal_append, List.append_assoc]
  cases terminal a <;> cases terminal b <;> rfl

theorem arbitrary_chunks (s : Native) (chunks : List (List Character)) :
    chunks.foldl submit s = submit s chunks.flatten := by
  induction chunks generalizing s with
  | nil => exact (empty_cannot_capture s).symm
  | cons cs rest ih =>
    simp only [List.foldl_cons, List.flatten_cons]
    rw [ih, submit_partition]

theorem uniform_terminal (first : Character) (rest : List Character) (p : Nat)
    (uniform : ∀ c ∈ first :: rest, c.policy = p) :
    terminal (first :: rest) = some p := by
  induction rest generalizing first with
  | nil => simpa [terminal] using congrArg some (uniform first (by simp))
  | cons next rest ih =>
    simp only [terminal]
    apply ih next
    intro c hc
    exact uniform c (by simp_all)

theorem uniform_word_policy (chunks : List (List Character)) (first : Character)
    (rest : List Character) (p : Nat)
    (cover : chunks.flatten = first :: rest)
    (uniform : ∀ c ∈ first :: rest, c.policy = p) :
    (chunks.foldl submit ⟨[],none⟩).captured = some p := by
  rw [arbitrary_chunks, cover]
  simpa [submit] using uniform_terminal first rest p uniform

theorem mixed_word_uses_last :
    (submit (submit ⟨[],none⟩ [⟨101,5⟩]) [⟨120,100⟩]).captured = some 100 := rfl

theorem delimiter_policy_is_not_owner :
    (submit ⟨[⟨101,5⟩],some 5⟩ []).captured ≠ some 100 := by decide

#print axioms arbitrary_chunks
#print axioms coherent_submit
#print axioms uniform_word_policy
#print axioms mixed_word_uses_last
#print axioms delimiter_policy_is_not_owner
end ChunkOwnership
