import Stability

namespace PreparedPublication
open SelectedDeclaration PreparationStability

inductive Assignment (V : Type) where
  | initial
  | literal (value : V)
  deriving DecidableEq, Repr

structure Store (V A : Type) where
  value : V
  other : A
  publications : List V
  observations : List V
  deriving DecidableEq, Repr

inductive Action (V A : Type) where
  | unrelated (value : A)
  | publish (value : V)
  | observe
  deriving DecidableEq, Repr

def step (action : Action V A) (store : Store V A) : Store V A :=
  match action with
  | .unrelated value => {store with other := value}
  | .publish value => {store with value, publications := store.publications ++ [value]}
  | .observe => {store with observations := store.observations ++ [store.value]}

def run (actions : List (Action V A)) (store : Store V A) : Store V A :=
  match actions with
  | [] => store
  | action :: rest => run rest (step action store)

def isolated (actions : List (Action V A)) : Prop :=
  ∀ action ∈ actions, ∃ value, action = .unrelated value

theorem isolated_run_preserves_publication_state (actions : List (Action V A))
    (store : Store V A) (safe : isolated actions) :
    (run actions store).value = store.value ∧
    (run actions store).publications = store.publications ∧
    (run actions store).observations = store.observations := by
  induction actions generalizing store with
  | nil => exact ⟨rfl, rfl, rfl⟩
  | cons action rest ih =>
      obtain ⟨value, rfl⟩ := safe action (by simp)
      have tail : isolated rest := by
        intro action member
        exact safe action (by simp [member])
      exact ih (step (.unrelated value) store) tail

def resolved (initial : V) : Assignment V → V
  | .initial => initial
  | .literal value => value

def explicit (initial : V) (assignment : Assignment V) (store : Store V A) : Store V A :=
  step (.publish (resolved initial assignment)) store

def optimized (initial : V) (assignment : Assignment V) (store : Store V A) : Store V A :=
  match assignment with
  | .initial => {store with publications := store.publications ++ [initial]}
  | .literal value => step (.publish value) store

theorem optimized_eq_explicit_when_initial (initial : V) (assignment : Assignment V)
    (store : Store V A) (untouched : store.value = initial) :
    optimized initial assignment store = explicit initial assignment store := by
  cases assignment with
  | literal value => rfl
  | initial =>
      cases store
      simp_all [optimized, explicit, resolved, step]

theorem optimized_publication_trace (initial : V) (assignment : Assignment V)
    (store : Store V A) :
    (optimized initial assignment store).publications =
      store.publications ++ [resolved initial assignment] ∧
    (optimized initial assignment store).observations = store.observations := by
  cases assignment <;> exact ⟨rfl, rfl⟩

theorem stable_preparation_single_final_publication
    (eligible eligible' : S → D → Bool)
    (evaluate evaluate' : S → D → Evaluation S (Assignment V) E)
    (state : S) (decls : List D)
    (decode : Finish (Assignment V) → Assignment V)
    (initial : V) (store : Store V A) (actions : List (Action V A))
    (stable : ∀ point ∈ visited eligible evaluate state decls,
      agreesAt eligible eligible' evaluate evaluate' point)
    (safe : isolated actions) (untouched : store.value = initial)
    (unpublished : store.publications = []) :
    optimized initial (decode (scan eligible evaluate state decls).finish) (run actions store) =
      explicit initial (decode (scan eligible' evaluate' state decls).finish) (run actions store) ∧
    (optimized initial (decode (scan eligible evaluate state decls).finish)
      (run actions store)).publications =
        [resolved initial (decode (scan eligible' evaluate' state decls).finish)] ∧
    (optimized initial (decode (scan eligible evaluate state decls).finish)
      (run actions store)).observations = store.observations := by
  have selection := scan_eq_of_reached_agreement eligible eligible' evaluate evaluate' state decls stable
  rw [selection]
  obtain ⟨value, publications, observations⟩ := isolated_run_preserves_publication_state actions store safe
  have same := optimized_eq_explicit_when_initial initial
    (decode (scan eligible evaluate state decls).finish) (run actions store)
    (value.trans untouched)
  obtain ⟨published, observed⟩ := optimized_publication_trace initial
    (decode (scan eligible evaluate state decls).finish) (run actions store)
  exact ⟨same, by simpa [publications, unpublished] using published,
    observed.trans observations⟩

inductive Appearance where
  | none | base
  deriving DecidableEq, Repr

def clean : Store Appearance Nat := ⟨.none, 0, [], []⟩
def earlyBase := run [Action.publish Appearance.base, .observe] clean

def initialEvaluation (_ : Unit) (_ : Nat) : Evaluation Unit (Assignment Appearance) Nat :=
  ⟨.terminal (some .initial), []⟩

def decodeAppearance : Finish (Assignment Appearance) → Assignment Appearance
  | .terminal (some value) => value
  | _ => .initial

theorem stable_selection_alone_leaves_early_base (tail : List Nat) :
    (scan (fun _ _ => true) initialEvaluation () (0 :: tail)).finish =
      .terminal (some .initial) ∧
    (optimized Appearance.none
      (decodeAppearance (scan (fun _ _ => true) initialEvaluation () (0 :: tail)).finish)
      earlyBase).value = .base ∧
    (explicit Appearance.none .initial earlyBase).value = .none := by
  simp [scan, initialEvaluation, decodeAppearance, optimized, explicit, resolved,
    earlyBase, run, step, clean]

theorem resetting_final_value_does_not_repair_consumed_value :
    (explicit Appearance.none .initial earlyBase).value = .none ∧
    (explicit Appearance.none .initial earlyBase).observations = [.base] ∧
    (step .observe (explicit Appearance.none .initial clean)).observations = [.none] := by decide

def writesTarget : Action V A → Bool
  | .publish _ => true
  | _ => false

theorem no_target_writes_still_allows_premature_consumption :
    ([Action.observe] : List (Action Appearance Nat)).all (fun action => !writesTarget action) = true ∧
    (optimized Appearance.none (.literal .base) (run [.observe] clean)).observations = [.none] ∧
    (step .observe (optimized Appearance.none (.literal .base) clean)).observations = [.base] := by decide

theorem restored_target_does_not_erase_publication_history :
    (run [.publish .base, .publish .none] clean).value = .none ∧
    (optimized Appearance.none .initial (run [.publish .base, .publish .none] clean)).publications =
      [.base, .none, .none] := by decide

end PreparedPublication
