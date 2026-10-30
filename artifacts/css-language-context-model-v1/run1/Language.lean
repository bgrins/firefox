import Std

namespace LanguageContext

abbrev Classifier := Nat → Option Bool
abbrev Cache := Option (Nat × Bool)

def ValidCache (classify : Classifier) (cache : Cache) : Prop :=
  ∀ key script, cache = some (key, script) → classify key = some script

def query (classify : Classifier) (cache : Cache) (key : Nat) : Option Bool × Cache :=
  match cache with
  | some (previous, script) =>
    if previous = key then (some script, cache)
    else match classify key with
      | none => (none, cache)
      | some value => (some value, some (key, value))
  | none => match classify key with
    | none => (none, none)
    | some value => (some value, some (key, value))

def queryAll (classify : Classifier) : Cache → List Nat → List (Option Bool) × Cache
  | cache, [] => ([], cache)
  | cache, key :: rest =>
    let first := query classify cache key
    let later := queryAll classify first.2 rest
    (first.1 :: later.1, later.2)

theorem query_correct (classify : Classifier) (cache : Cache) (key : Nat)
    (valid : ValidCache classify cache) :
    (query classify cache key).1 = classify key ∧
      ValidCache classify (query classify cache key).2 := by
  cases cache with
  | none =>
    cases h : classify key with
    | none => simp [query, h, ValidCache]
    | some value =>
      simp only [query, h, Prod.fst, Prod.snd, true_and]
      intro next script eq
      cases eq
      exact h
  | some pair =>
    rcases pair with ⟨previous, script⟩
    by_cases same : previous = key
    · subst previous
      simpa [query] using And.intro (valid key script rfl).symm valid
    · cases h : classify key with
      | none => simp [query, same, h, valid]
      | some value =>
        simp only [query, same, ↓reduceIte, h, Prod.fst, Prod.snd, true_and]
        intro next nextScript eq
        cases eq
        exact h

theorem queryAll_correct (classify : Classifier) (keys : List Nat) :
    ∀ cache, ValidCache classify cache →
      (queryAll classify cache keys).1 = keys.map classify ∧
        ValidCache classify (queryAll classify cache keys).2 := by
  induction keys with
  | nil => intro cache valid; exact ⟨rfl, valid⟩
  | cons key rest ih =>
    intro cache valid
    obtain ⟨first, nextValid⟩ := query_correct classify cache key valid
    obtain ⟨later, finalValid⟩ := ih _ nextValid
    exact ⟨by simp [queryAll, first, later], finalValid⟩

theorem failed_query_preserves_cache (classify : Classifier) (cache : Cache)
    (key : Nat) (valid : ValidCache classify cache) (failed : classify key = none) :
    (query classify cache key).2 = cache := by
  cases cache with
  | none => simp [query, failed]
  | some pair =>
    rcases pair with ⟨previous, script⟩
    have different : previous ≠ key := by
      intro same
      subst previous
      have found := valid key script rfl
      simp [failed] at found
    simp [query, different, failed]

def recordedLanguage (key : Nat) : Option Bool → Option Nat
  | none => none
  | some _ => some key

def scriptValue (result : Option Bool) : Bool := result.getD false

structure FreshState where
  language : Option Nat
  script : Bool
  deriving DecidableEq, Repr

def beginWord (_precedingScript : Bool) (key : Nat) (result : Option Bool) : FreshState :=
  ⟨recordedLanguage key result, scriptValue result⟩

theorem preceding_script_irrelevant (left right : Bool) (key : Nat) (result : Option Bool) :
    beginWord left key result = beginWord right key result := rfl

theorem failure_clears_script_without_committing_language (prior : Bool) (key : Nat) :
    beginWord prior key none = ⟨none, false⟩ := rfl

theorem valid_false_commits_language (prior : Bool) (key : Nat) :
    beginWord prior key (some false) = ⟨some key, false⟩ := rfl

theorem failure_cannot_be_quotiented_to_false (key : Nat) :
    ¬ ∃ record : Bool → Option Nat,
      ∀ result, record (scriptValue result) = recordedLanguage key result := by
  rintro ⟨record, correct⟩
  have failed := correct none
  have valid := correct (some false)
  simp [scriptValue, recordedLanguage] at failed valid
  rw [failed] at valid
  contradiction

end LanguageContext
