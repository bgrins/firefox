import FallbackSchedule
import QualifiedHistories
namespace FallbackPreparation
open QualifiedAttributes

def infoKey (info : Info) : Option Key :=
  match info.kind with
  | .typedAttr => resolveKey info.name info.ns
  | _ => none

structure PrepState (Value : Type) where
  cache : State Value
  attempts : List Key

abbrev Provider (Value : Type) := State Value → Info → Option Value

def prepareOne (provider : Provider Value) (state : PrepState Value) (ref : Ref) : PrepState Value :=
  match infoKey ref.info with
  | none => state
  | some key => if key ∈ state.cache.seen then state else
      ⟨preload state.cache key (provider state.cache ref.info), key :: state.attempts⟩

def prepareList (provider : Provider Value) (refs : List Ref) (state : PrepState Value) :=
  refs.foldl (prepareOne provider) state

def scanAndPrepare (provider : Provider Value) :
    List Ref → List (List Ref) → PrepState Value → List (List Ref) × PrepState Value
  | [], stack, state => (stack, state)
  | ref :: rest, stack, state =>
      scanAndPrepare provider rest (enqueue ref stack) (prepareOne provider state ref)

theorem inner_loop_factorization (provider : Provider Value) (refs : List Ref)
    (stack : List (List Ref)) (state : PrepState Value) :
    scanAndPrepare provider refs stack state =
      (scan refs stack, prepareList provider refs state) := by
  induction refs generalizing stack state with
  | nil => rfl
  | cons ref rest ih =>
    simp only [scanAndPrepare, scan, prepareList, List.foldl_cons]
    exact ih _ _

def execute (provider : Provider Value) :
    Nat → List (List Ref) → PrepState Value → List (List Ref) × PrepState Value
  | 0, stack, state => (stack, state)
  | _ + 1, [], state => ([], state)
  | fuel + 1, refs :: rest, state =>
      let pair := scanAndPrepare provider refs rest state
      execute provider fuel pair.1 pair.2

theorem actual_worklist_trace_composition (provider : Provider Value) (fuel : Nat)
    (stack : List (List Ref)) (state : PrepState Value) :
    execute provider fuel stack state =
      (pending fuel stack, prepareList provider (run fuel stack) state) := by
  induction fuel generalizing stack state with
  | zero => rfl
  | succ fuel ih =>
    cases stack with
    | nil => rfl
    | cons refs rest =>
      simp only [execute, inner_loop_factorization, ih, pending, run,
        prepareList, List.foldl_append]

theorem executed_worklist_finishes (provider : Provider Value) (fuel : Nat)
    (stack : List (List Ref)) (state : PrepState Value)
    (enough : stackCost stack ≤ fuel) :
    (execute provider fuel stack state).1 = [] := by
  rw [actual_worklist_trace_composition]
  exact finite_worklist_terminates fuel stack enough

theorem skipped_reference_still_queues_fallback (provider : Provider Value) (info : Info)
    (fallback : List Ref) (stack : List (List Ref)) (state : PrepState Value)
    (skip : infoKey info = none) :
    scanAndPrepare provider [.mk info (some fallback)] stack state = (fallback :: stack, state) := by
  simp [scanAndPrepare, enqueue, Ref.fallback, prepareOne, Ref.info, skip]

theorem duplicate_still_queues_fallback (provider : Provider Value) (info : Info)
    (fallback : List Ref) (stack : List (List Ref)) (state : PrepState Value)
    (key : Key) (key_eq : infoKey info = some key) (seen : key ∈ state.cache.seen) :
    scanAndPrepare provider [.mk info (some fallback)] stack state = (fallback :: stack, state) := by
  simp [scanAndPrepare, enqueue, Ref.fallback, prepareOne, Ref.info, key_eq, seen]

theorem var_outer_is_skipped (name : Nat) (ns : Option Nat) :
    infoKey ⟨.var, name, ns⟩ = none := rfl

theorem env_outer_is_skipped (name : Nat) (ns : Option Nat) :
    infoKey ⟨.env, name, ns⟩ = none := rfl

theorem untyped_outer_is_skipped (name : Nat) (ns : Option Nat) :
    infoKey ⟨.untypedAttr, name, ns⟩ = none := rfl

theorem unknown_namespace_outer_is_skipped (name : Nat) :
    infoKey ⟨.typedAttr, name, none⟩ = none := rfl

theorem known_namespace_has_qualified_key (name ns : Nat) :
    infoKey ⟨.typedAttr, name, some ns⟩ = some ⟨name, ns⟩ := rfl

theorem prepare_cache_at_key (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (key : Key) (key_eq : infoKey ref.info = some key) :
    (prepareOne provider state ref).cache =
      preload state.cache key (provider state.cache ref.info) := by
  by_cases seen : key ∈ state.cache.seen
  · simp [prepareOne, key_eq, seen, preload]
  · simp [prepareOne, key_eq, seen]

theorem prepare_seen_membership (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (key : Key) :
    key ∈ (prepareOne provider state ref).cache.seen ↔
      infoKey ref.info = some key ∨ key ∈ state.cache.seen := by
  cases key_eq : infoKey ref.info with
  | none => simp [prepareOne, key_eq]
  | some other =>
    rw [prepare_cache_at_key provider state ref other key_eq]
    rw [preload_seen_membership]
    simp [eq_comm]

theorem prepare_preserves_seen_value (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (key : Key) (seen : key ∈ state.cache.seen) :
    (prepareOne provider state ref).cache.values key = state.cache.values key := by
  cases key_eq : infoKey ref.info with
  | none => simp [prepareOne, key_eq]
  | some other =>
    by_cases same : key = other
    · subst key
      simp [prepareOne, key_eq, seen]
    · rw [prepare_cache_at_key provider state ref other key_eq]
      exact preload_preserves_other state.cache other key same _

theorem prepare_preserves_other_key (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (key : Key) (different : infoKey ref.info ≠ some key) :
    (prepareOne provider state ref).cache.values key = state.cache.values key := by
  cases key_eq : infoKey ref.info with
  | none => simp [prepareOne, key_eq]
  | some other =>
    rw [prepare_cache_at_key provider state ref other key_eq]
    apply preload_preserves_other
    intro same
    subst key
    exact different key_eq

theorem prepareList_seen_membership (provider : Provider Value) (refs : List Ref)
    (state : PrepState Value) (key : Key) :
    key ∈ (prepareList provider refs state).cache.seen ↔
      key ∈ state.cache.seen ∨ ∃ ref ∈ refs, infoKey ref.info = some key := by
  induction refs generalizing state with
  | nil => simp [prepareList]
  | cons ref rest ih =>
    simp only [prepareList, List.foldl_cons]
    rw [← prepareList, ih, prepare_seen_membership]
    simp only [List.mem_cons, exists_eq_or_imp]
    simp [or_assoc, or_comm]

theorem prepareList_preserves_seen_value (provider : Provider Value) (refs : List Ref)
    (state : PrepState Value) (key : Key) (seen : key ∈ state.cache.seen) :
    (prepareList provider refs state).cache.values key = state.cache.values key := by
  induction refs generalizing state with
  | nil => rfl
  | cons ref rest ih =>
    simp only [prepareList, List.foldl_cons]
    rw [← prepareList, ih _ ((prepare_seen_membership provider state ref key).mpr (Or.inr seen))]
    exact prepare_preserves_seen_value provider state ref key seen

theorem prepareList_preserves_untouched_key (provider : Provider Value) (refs : List Ref)
    (state : PrepState Value) (key : Key)
    (untouched : ∀ ref ∈ refs, infoKey ref.info ≠ some key) :
    (prepareList provider refs state).cache.values key = state.cache.values key := by
  induction refs generalizing state with
  | nil => rfl
  | cons ref rest ih =>
    simp only [prepareList, List.foldl_cons]
    rw [← prepareList, ih _ (fun x hx => untouched x (by simp [hx]))]
    exact prepare_preserves_other_key provider state ref key (untouched ref (by simp))

def AttemptsInvariant (state : PrepState Value) : Prop :=
  state.attempts.Nodup ∧ ∀ key ∈ state.attempts, key ∈ state.cache.seen

theorem prepare_preserves_attempts_invariant (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (valid : AttemptsInvariant state) :
    AttemptsInvariant (prepareOne provider state ref) := by
  cases key_eq : infoKey ref.info with
  | none => simpa [prepareOne, key_eq] using valid
  | some key =>
    by_cases seen : key ∈ state.cache.seen
    · simpa [prepareOne, key_eq, seen] using valid
    · have fresh : key ∉ state.attempts := fun h => seen (valid.2 key h)
      simp only [prepareOne, key_eq, seen, ↓reduceIte, AttemptsInvariant]
      constructor
      · exact List.nodup_cons.mpr ⟨fresh, valid.1⟩
      · intro other member
        rw [preload_seen_membership]
        rcases List.mem_cons.mp member with same | old
        · exact Or.inl same
        · exact Or.inr (valid.2 other old)

theorem arbitrary_preparation_attempts_are_unique (provider : Provider Value) (refs : List Ref)
    (state : PrepState Value) (valid : AttemptsInvariant state) :
    AttemptsInvariant (prepareList provider refs state) := by
  induction refs generalizing state with
  | nil => exact valid
  | cons ref rest ih =>
    exact ih _ (prepare_preserves_attempts_invariant provider state ref valid)

theorem failed_fresh_attempt_does_not_write (provider : Provider Value) (state : PrepState Value)
    (ref : Ref) (key : Key) (key_eq : infoKey ref.info = some key)
    (fresh : key ∉ state.cache.seen) (failed : provider state.cache ref.info = none) :
    (prepareOne provider state ref).cache.values = state.cache.values ∧
    (prepareOne provider state ref).attempts = key :: state.attempts := by
  simp [prepareOne, key_eq, fresh, failed, preload]

def withUsedEdges (provider : Provider Value) (refs : List Ref) (state : PrepState Value)
    (usedEdges : List Edge) := (prepareList provider refs state, usedEdges)

theorem preparation_does_not_select_used_edges (provider : Provider Value) (refs : List Ref)
    (state : PrepState Value) (usedEdges : List Edge) :
    (withUsedEdges provider refs state usedEdges).2 = usedEdges := rfl

def keyWeight (key : Key) (ref : Ref) : Nat :=
  if infoKey ref.info = some key then 1 else 0

theorem ownMass_positive_iff (weight : Ref → Nat) (refs : List Ref) :
    0 < ownMass weight refs ↔ ∃ ref ∈ refs, 0 < weight ref := by
  induction refs with
  | nil => simp [ownMass]
  | cons ref rest ih =>
    constructor
    · intro positive
      by_cases head : 0 < weight ref
      · exact ⟨ref, by simp, head⟩
      · have tail : 0 < ownMass weight rest := by
          simp only [ownMass] at positive
          omega
        obtain ⟨other, member, positive⟩ := ih.mp tail
        exact ⟨other, by simp [member], positive⟩
    · rintro ⟨other, member, positive⟩
      rcases List.mem_cons.mp member with same | tail
      · subst other
        simp only [ownMass]
        omega
      · have tailpos := ih.mpr ⟨other, tail, positive⟩
        simp only [ownMass]
        omega

theorem keyMass_positive_iff (key : Key) (refs : List Ref) :
    0 < ownMass (keyWeight key) refs ↔ ∃ ref ∈ refs, infoKey ref.info = some key := by
  rw [ownMass_positive_iff]
  have each (ref : Ref) : 0 < keyWeight key ref ↔ infoKey ref.info = some key := by
    by_cases h : infoKey ref.info = some key <;> simp [keyWeight, h]
  simp only [each]

theorem actual_worklist_seen_complete (provider : Provider Value) (fuel : Nat)
    (stack : List (List Ref)) (state : PrepState Value) (key : Key)
    (enough : stackCost stack ≤ fuel) :
    key ∈ (execute provider fuel stack state).2.cache.seen ↔
      key ∈ state.cache.seen ∨ 0 < stackMass (keyWeight key) stack := by
  rw [actual_worklist_trace_composition]
  change key ∈ (prepareList provider (run fuel stack) state).cache.seen ↔ _
  rw [prepareList_seen_membership, ← keyMass_positive_iff,
    run_complete fuel stack (keyWeight key) enough]

theorem actual_worklist_attempts_unique (provider : Provider Value) (fuel : Nat)
    (stack : List (List Ref)) (state : PrepState Value) (valid : AttemptsInvariant state) :
    AttemptsInvariant (execute provider fuel stack state).2 := by
  rw [actual_worklist_trace_composition]
  exact arbitrary_preparation_attempts_are_unique provider _ state valid

theorem actual_worklist_preserves_previously_seen (provider : Provider Value) (fuel : Nat)
    (stack : List (List Ref)) (state : PrepState Value) (key : Key)
    (seen : key ∈ state.cache.seen) :
    (execute provider fuel stack state).2.cache.values key = state.cache.values key := by
  rw [actual_worklist_trace_composition]
  exact prepareList_preserves_seen_value provider _ state key seen

end FallbackPreparation
