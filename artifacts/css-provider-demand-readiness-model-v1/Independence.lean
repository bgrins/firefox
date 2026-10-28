import Admission

namespace SelectedIndependence

inductive Value where
  | literal (n : Nat)
  | contextual (key : Nat)
  | nested (child : Value)
  | nil
  | cons (first rest : Value)
  deriving DecidableEq, Repr

inductive Computed where
  | literal (n : Nat)
  | nested (child : Computed)
  | nil
  | cons (first rest : Computed)
  deriving DecidableEq, Repr

def compute (env : Nat → Nat) : Value → Computed
  | .literal n => .literal n
  | .contextual k => .literal (env k)
  | .nested v => .nested (compute env v)
  | .nil => .nil
  | .cons a b => .cons (compute env a) (compute env b)

def dependencies : Value → List Nat
  | .literal _ | .nil => []
  | .contextual k => [k]
  | .nested v => dependencies v
  | .cons a b => dependencies a ++ dependencies b

def Independent (v : Value) : Prop := dependencies v = []
instance (v : Value) : Decidable (Independent v) := inferInstanceAs (Decidable (_ = _))

theorem agreement_suffices (v : Value) (a b : Nat → Nat)
    (agree : ∀ k ∈ dependencies v, a k = b k) : compute a v = compute b v := by
  induction v with
  | literal n => rfl
  | contextual k => simp [compute, agree k (by simp [dependencies])]
  | nested v ih => simp only [compute]; exact congrArg Computed.nested (ih agree)
  | nil => rfl
  | cons x xs hx hxs =>
      simp only [compute]
      rw [hx (fun k hk => agree k (List.mem_append_left _ hk)),
        hxs (fun k hk => agree k (List.mem_append_right _ hk))]

theorem independent_stable (v : Value) (h : Independent v) (a b : Nat → Nat) :
    compute a v = compute b v := by
  apply agreement_suffices
  intro k hk
  change dependencies v = [] at h
  rw [h] at hk
  cases hk

theorem nested_independence (v : Value) : Independent (.nested v) ↔ Independent v := Iff.rfl

theorem list_independence (a b : Value) :
    Independent (.cons a b) ↔ Independent a ∧ Independent b := by
  simp [Independent, dependencies]

structure Attempt where
  parsed : Option Value
  inspected : List Nat
  deriving DecidableEq, Repr

def choose : List Attempt → Option Value
  | [] => none
  | a :: rest => match a.parsed with
      | some v => some v
      | none => choose rest

inductive Outcome where
  | syntaxFailure
  | dependent (selected : Value)
  | accepted (selected : Value)
  deriving DecidableEq, Repr

def validate : Option Value → Outcome
  | none => .syntaxFailure
  | some v => if Independent v then .accepted v else .dependent v

def register (attempts : List Attempt) : Outcome := validate (choose attempts)

theorem choice_append (xs ys : List Attempt) :
    choose (xs ++ ys) = match choose xs with
      | none => choose ys
      | some v => some v := by
  induction xs with
  | nil => rfl
  | cons a xs ih => cases hp : a.parsed <;> simp [choose, hp, ih]

theorem failed_prefix_ignored (xs ys : List Attempt) (h : choose xs = none) :
    register (xs ++ ys) = register ys := by
  simp [register, choice_append, h]

theorem successful_selection_no_retry (a : Attempt) (rest : List Attempt) (v : Value)
    (h : a.parsed = some v) : register (a :: rest) = validate (some v) := by
  simp [register, choose, h]

theorem dependent_selection_rejects (a : Attempt) (rest : List Attempt) (v : Value)
    (h : a.parsed = some v) (dep : ¬ Independent v) :
    register (a :: rest) = .dependent v := by
  simp [successful_selection_no_retry a rest v h, validate, dep]

theorem accepted_certificate {attempts : List Attempt} {v : Value}
    (h : register attempts = .accepted v) : choose attempts = some v ∧ Independent v := by
  unfold register validate at h
  split at h
  next => contradiction
  next w hw =>
    split at h
    next good => cases h; exact ⟨hw, good⟩
    next => contradiction

theorem accepted_context_stable {attempts : List Attempt} {v : Value}
    (h : register attempts = .accepted v) (a b : Nat → Nat) : compute a v = compute b v :=
  independent_stable v (accepted_certificate h).2 a b

def rejectInsideParse : List Attempt → Option Value
  | [] => none
  | a :: rest => match a.parsed with
      | none => rejectInsideParse rest
      | some v => if Independent v then some v else rejectInsideParse rest

def leakedDependencies : List Attempt → List Nat
  | [] => []
  | a :: rest => match a.parsed with
      | none => a.inspected ++ leakedDependencies rest
      | some v => a.inspected ++ dependencies v

def contaminatedAccepts (xs : List Attempt) : Bool :=
  (choose xs).isSome && (leakedDependencies xs).isEmpty

def canvasColor : Attempt := ⟨some (.contextual 1), [1]⟩
def canvasIdent : Attempt := ⟨some (.literal 42), []⟩
def failedColorPrefix : Attempt := ⟨none, [1]⟩
def nestedContainer : Value := .nested (.contextual 2)
def laterListMember : Value := .cons (.literal 5) (.cons nestedContainer .nil)

theorem canvas_color_first_rejects :
    register [canvasColor, canvasIdent] = .dependent (.contextual 1) := by decide +kernel

theorem canvas_ident_first_accepts :
    register [canvasIdent, canvasColor] = .accepted (.literal 42) := by decide +kernel

theorem preparse_rejection_changes_selection :
    rejectInsideParse [canvasColor, canvasIdent] = some (.literal 42) ∧
    choose [canvasColor, canvasIdent] = some (.contextual 1) := by decide +kernel

theorem failed_branch_flags_are_not_selected_dependencies :
    register [failedColorPrefix, canvasIdent] = .accepted (.literal 42) ∧
    contaminatedAccepts [failedColorPrefix, canvasIdent] = false := by decide +kernel

theorem later_nested_dependency_retained : dependencies laterListMember = [2] := by decide +kernel

theorem later_member_changes_computation :
    compute (fun _ => 10) laterListMember ≠ compute (fun _ => 20) laterListMember := by decide +kernel

structure Tracked where
  value : Value
  evidence : List Nat
  deriving DecidableEq, Repr

def Sound (t : Tracked) : Prop :=
  ∀ a b : Nat → Nat, (∀ k ∈ t.evidence, a k = b k) → compute a t.value = compute b t.value

def track (v : Value) : Tracked := ⟨v, dependencies v⟩

theorem track_sound (v : Value) : Sound (track v) := agreement_suffices v

theorem sound_empty_evidence_stable (t : Tracked) (sound : Sound t)
    (empty : t.evidence = []) (a b : Nat → Nat) : compute a t.value = compute b t.value := by
  apply sound
  intro k hk
  rw [empty] at hk
  cases hk

theorem simplification_preserves_certificate (before after : Tracked)
    (sound : Sound before) (sameEvidence : after.evidence = before.evidence)
    (sameComputation : ∀ env, compute env after.value = compute env before.value) : Sound after := by
  intro a b agree
  rw [sameComputation a, sameComputation b]
  apply sound
  simpa [sameEvidence] using agree

def lostEvidence : Tracked := ⟨nestedContainer, []⟩

theorem erased_evidence_is_unsound : ¬ Sound lostEvidence := by
  intro bad
  have impossible := bad (fun _ => 0) (fun _ => 1) (by simp [lostEvidence])
  have : Computed.nested (.literal 0) = Computed.nested (.literal 1) := impossible
  contradiction

def sampledFold (sample : Nat → Nat) : Value → Value
  | .contextual k => .literal (sample k)
  | .nested v => .nested (sampledFold sample v)
  | .cons a b => .cons (sampledFold sample a) (sampledFold sample b)
  | v => v

theorem sampled_fold_matches_only_sample :
    compute (fun _ => 10) (sampledFold (fun _ => 10) nestedContainer) =
      compute (fun _ => 10) nestedContainer ∧
    compute (fun _ => 20) (sampledFold (fun _ => 10) nestedContainer) ≠
      compute (fun _ => 20) nestedContainer := by decide +kernel

theorem imported_numeric_certificate (raw : RegisteredNumber.Raw)
    (h : RegisteredNumber.needsFont raw = false) (a b : Nat) :
    RegisteredNumber.eval a raw = RegisteredNumber.eval b raw :=
  RegisteredNumber.no_font_leaves_is_context_independent raw a b h

end SelectedIndependence
