import Std

namespace CommitRefresh

variable {Effect Context Value : Type} [DecidableEq Effect]

abbrev Cache (Effect Value : Type) := Effect → Value → Value

def refresh (resolve : Context → Cache Effect Value) (context : Context) :
    List Effect → Cache Effect Value → Cache Effect Value
  | [], cache => cache
  | effect :: rest, cache =>
      refresh resolve context rest (fun other =>
        if other = effect then resolve context effect else cache other)

def compose : List Effect → Cache Effect Value → Value → Value
  | [], _, base => base
  | effect :: rest, cache, base => compose rest cache (cache effect base)

theorem refresh_at (resolve : Context → Cache Effect Value) (context : Context)
    (tasks : List Effect) (cache : Cache Effect Value) (effect : Effect) :
    refresh resolve context tasks cache effect =
      if effect ∈ tasks then resolve context effect else cache effect := by
  induction tasks generalizing cache with
  | nil => simp [refresh]
  | cons first rest ih =>
      simp only [refresh, ih, List.mem_cons]
      by_cases later : effect ∈ rest
      · simp [later]
      · by_cases same : effect = first <;> simp [later, same]

omit [DecidableEq Effect] in
theorem compose_agrees (stack : List Effect) (left right : Cache Effect Value)
    (base : Value) (agree : ∀ effect ∈ stack, left effect = right effect) :
    compose stack left base = compose stack right base := by
  induction stack generalizing base with
  | nil => rfl
  | cons effect rest ih =>
      simp only [compose]
      rw [agree effect (by simp)]
      apply ih
      intro next member
      exact agree next (by simp [member])

theorem refreshed_prefix_current (resolve : Context → Cache Effect Value)
    (current : Context) (stack tasks : List Effect) (cache : Cache Effect Value)
    (base : Value) (covered : ∀ effect ∈ stack, effect ∈ tasks) :
    compose stack (refresh resolve current tasks cache) base =
      compose stack (resolve current) base := by
  apply compose_agrees
  intro effect member
  rw [refresh_at]
  simp [covered effect member]

theorem refresh_context_transport (resolve : Context → Cache Effect Value)
    (supplied current : Context) (same : supplied = current)
    (stack tasks : List Effect) (cache : Cache Effect Value) (base : Value)
    (covered : ∀ effect ∈ stack, effect ∈ tasks) :
    compose stack (refresh resolve supplied tasks cache) base =
      compose stack (resolve current) base := by
  subst supplied
  exact refreshed_prefix_current resolve current stack tasks cache base covered

end CommitRefresh
