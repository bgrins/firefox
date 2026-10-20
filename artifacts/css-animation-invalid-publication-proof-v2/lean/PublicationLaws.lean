import PublicationModel
namespace InvalidPublication
set_option linter.unusedSectionVars false
variable {K D P : Type} [DecidableEq K]

theorem conversion_name (encode : P → D) (e : Endpoint K P) :
    (convert encode e).name = e.name := rfl

theorem conversion_roundtrip (env : Environment K D P) (preserve : PayloadPreserved env)
    (e : Endpoint K P) : fromDeclaration env (convert env.encode e) = some e := by
  cases e with
  | mk k v =>
    cases v with
    | none => rfl
    | some p => simp [fromDeclaration, convert, preserve p]

theorem inner_invalid_present (env : Environment K D P) (k : K) :
    fromDeclaration env (convert env.encode ⟨k, none⟩) = some ⟨k, none⟩ := rfl

theorem outer_absence_empty (encode : P → D) : publication (K := K) encode none = [] := rfl

theorem inner_invalid_nonempty (encode : P → D) (k : K) :
    publication encode (some ⟨k, none⟩) ≠ [] := by simp [publication]

theorem invalid_always_affects (env : Environment K D P) (k : K) :
    mayAffect env ⟨k, .invalid, true, true⟩ = true := rfl

theorem invalid_has_no_references : references (Action.invalid : Action D P) = false := rfl

theorem already_seen_suppressed (env : Environment K D P) (s : State K P)
    (e : Entry K D P) (h : s.seen e.name = true) : step env s e = s := by
  simp [step, h]

theorem disallowed_suppressed (env : Environment K D P) (s : State K P)
    (e : Entry K D P) (h : e.revertAllowed = false ∨ e.flagsIncluded = false) :
    step env s e = s := by
  rcases h with h | h <;> simp [step, h]

theorem invalid_step (env : Environment K D P) (s : State K P) (k : K)
    (h : s.seen k = false) :
    step env s ⟨k, .invalid, true, true⟩ = put (mark s k) (env.inherits k) k none := by
  simp [step, h, mayAffect, references]

theorem invalid_marks_before_remove (env : Environment K D P) (s : State K P) (k : K)
    (h : s.seen k = false) :
    (step env s ⟨k, .invalid, true, true⟩).seen k = true ∧
    selected env (step env s ⟨k, .invalid, true, true⟩) k = none ∧
    (step env s ⟨k, .invalid, true, true⟩).cycles = s.cycles := by
  rw [invalid_step env s k h]
  simp [selected, put, mark]

theorem other_name_frame (env : Environment K D P) (s : State K P)
    (e : Entry K D P) (k : K) (different : k ≠ e.name) (r : Bool) :
    (step env s e).values r k = s.values r k ∧ (step env s e).seen k = s.seen k := by
  unfold step
  split <;> try simp
  split <;> try simp
  split <;> try simp
  split
  · simp [mark, different]
  · cases e.action <;> simp [put, mark, unmark, different]

theorem seen_name_stable_step (env : Environment K D P) (s : State K P)
    (e : Entry K D P) (k : K) (h : s.seen k = true) (r : Bool) :
    (step env s e).values r k = s.values r k ∧ (step env s e).seen k = true := by
  by_cases eq : k = e.name
  · subst k; rw [already_seen_suppressed env s e h]; exact ⟨rfl, h⟩
  · have frame := other_name_frame env s e k eq r
    exact ⟨frame.1, frame.2.trans h⟩

theorem arbitrary_suffix_stability (env : Environment K D P) (suffix : List (Entry K D P))
    (s : State K P) (k : K) (h : s.seen k = true) (r : Bool) :
    (run env s suffix).values r k = s.values r k ∧ (run env s suffix).seen k = true := by
  induction suffix generalizing s with
  | nil => exact ⟨rfl, h⟩
  | cons e rest ih =>
    have first := seen_name_stable_step env s e k h r
    have later := ih (step env s e) first.2
    exact ⟨later.1.trans first.1, later.2⟩

theorem invalid_wins_suffix (env : Environment K D P) (s : State K P) (k : K)
    (suffix : List (Entry K D P)) (h : s.seen k = false) :
    selected env (run env s (⟨k, .invalid, true, true⟩ :: suffix)) k = none ∧
    (run env s (⟨k, .invalid, true, true⟩ :: suffix)).seen k = true := by
  have first := invalid_marks_before_remove env s k h
  have later := arbitrary_suffix_stability env suffix (step env s ⟨k, .invalid, true, true⟩) k first.1 (env.inherits k)
  exact ⟨later.1.trans first.2.1, later.2⟩

theorem admitted_invalid_wins (env : Environment K D P) (s : State K P)
    (e : Entry K D P) (kind : e.action = .invalid) (gate : admitted s e)
    (suffix : List (Entry K D P)) :
    selected env (run env s (e :: suffix)) e.name = none := by
  cases e with
  | mk k a r f =>
    rcases gate with ⟨hr, hf, hs⟩
    simp only at hr hf hs kind
    subst a; subst r; subst f
    exact (invalid_wins_suffix env s k suffix hs).1

theorem invalid_opposite_partition (env : Environment K D P) (s : State K P) (k q : K)
    (h : s.seen k = false) :
    (step env s ⟨k, .invalid, true, true⟩).values (!env.inherits k) q = s.values (!env.inherits k) q := by
  rw [invalid_step env s k h]
  cases hr : env.inherits k <;> simp [put, mark, hr]

theorem publication_fallback (env : Environment K D P) (s : State K P) (k : K)
    (suffix : List (Entry K D P)) (h : s.seen k = false) (fallback : P) :
    referenceObservation (selected env (run env s
      (publication env.encode (some ⟨k, none⟩) ++ suffix)) k) = .fallback ∧
    fallbackResult fallback (selected env (run env s
      (publication env.encode (some ⟨k, none⟩) ++ suffix)) k) = fallback := by
  simp only [publication, convert, List.cons_append, List.nil_append]
  rw [(invalid_wins_suffix env s k suffix h).1]
  exact ⟨rfl, rfl⟩

theorem outer_absence_preserves (env : Environment K D P) (s : State K P) :
    run env s (publication env.encode none) = s := rfl

theorem explicit_initial_selected (env : Environment K D P) (s : State K P) (k : K)
    (fresh : s.seen k = false)
    (resetSeed : env.inherits k = false → selected env s k = env.initial k) :
    selected env (step env s ⟨k, .initial, true, true⟩) k = env.initial k := by
  cases hr : env.inherits k
  · simpa [step, fresh, mayAffect, hr, mark, selected] using resetSeed hr
  · simp [step, fresh, mayAffect, hr, selected, put, mark, references]

theorem original_invalid_uses_initial (env : Environment K D P) (s : State K P) (k : K)
    (fresh : s.seen k = false)
    (resetSeed : env.inherits k = false → selected env s k = env.initial k) :
    selected env (step env s (originalConvert env.encode ⟨k, none⟩)) k = env.initial k :=
  explicit_initial_selected env s k fresh resetSeed

theorem original_structured_failure_iff (env : Environment K D P) (s : State K P) (k : K)
    (fresh : s.seen k = false)
    (resetSeed : env.inherits k = false → selected env s k = env.initial k) :
    referenceObservation (selected env (step env s (originalConvert env.encode ⟨k, none⟩)) k)
      ≠ referenceObservation (none : Option P) ↔ env.initial k ≠ none := by
  rw [original_invalid_uses_initial env s k fresh resetSeed]
  cases env.initial k <;> simp [referenceObservation]

theorem valid_publication_preserved (env : Environment K D P) (preserve : PayloadPreserved env)
    (s : State K P) (k : K) (p : P) (fresh : s.seen k = false) :
    selected env (step env s (convert env.encode ⟨k, some p⟩)) k = some p := by
  simp [convert, step, fresh, mayAffect, selected, put, mark, preserve p]

theorem valid_conversion_unchanged (encode : P → D) (k : K) (p : P) :
    convert encode ⟨k, some p⟩ = originalConvert encode ⟨k, some p⟩ := rfl

end InvalidPublication
