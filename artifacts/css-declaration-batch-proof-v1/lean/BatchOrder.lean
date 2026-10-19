import BatchBase
import BatchIndices
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace BatchOrder
open AllOrder
open BatchBase (Comparator)
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]
local notation "E" => Entry ι ν

inductive Kind where
  | none | append | replace | move
  deriving DecidableEq, Repr

inductive Decision where
  | pending (seen : Bool)
  | found (kind : Kind)
  deriving DecidableEq, Repr

def planKind : Plan → Kind
  | .none => .none
  | .append => .append
  | .replace _ => .replace
  | .move _ => .move

def searchKind : Search → Decision
  | .pending b => .pending b
  | .found p => .found (planKind p)

def decisionScan (cmp : Comparator ι ν) (op : ι → ι → Bool) (new : E) : List E → Decision
  | [] => .pending false
  | old :: tail =>
    match decisionScan cmp op new tail with
    | .found k => .found k
    | .pending seen =>
      if old.id = new.id then .found (if seen then .move else if cmp.same old new then .none else .replace)
      else .pending (op new.id old.id || seen)

def decision (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E) : Kind :=
  match decisionScan cmp op new xs with
  | .pending _ => .append
  | .found k => k

theorem scan_erasure (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E) (n : Nat) :
    searchKind (BatchBase.scan cmp op new n xs) = decisionScan cmp op new xs := by
  induction xs generalizing n with
  | nil => rfl
  | cons old tail ih =>
    simp only [BatchBase.scan, decisionScan]
    have h := ih (n+1)
    cases hs : BatchBase.scan cmp op new (n+1) tail with
    | pending b =>
      simp only [hs, searchKind] at h
      rw [← h]
      by_cases he : old.id = new.id <;> cases b <;> by_cases hv : cmp.same old new = true <;>
        simp [hs, he, hv, searchKind, BatchBase.decideFound, planKind]
    | found p =>
      simp only [hs, searchKind] at h
      rw [← h]
      simp [hs, searchKind]

theorem planner_kind (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E) :
    planKind (BatchBase.planner cmp op xs new) = decision cmp op xs new := by
  have h := scan_erasure cmp op xs new 0
  cases hs : BatchBase.scan cmp op new 0 xs <;> simp [hs, searchKind] at h <;>
    simp [BatchBase.planner, hs, decision, ← h, planKind]

def relevant (cmp : Comparator ι ν) (op : ι → ι → Bool) (id : ι) (e : E) : Bool :=
  decide (e.id = id) || op id e.id

theorem decision_projection (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E) :
    decisionScan cmp op new (xs.filter (relevant cmp op new.id)) = decisionScan cmp op new xs := by
  induction xs with
  | nil => rfl
  | cons old tail ih =>
    by_cases he : old.id = new.id
    · simp [List.filter_cons, relevant, he, decisionScan, ih]
    · by_cases ho : op new.id old.id = true
      · simp [List.filter_cons, relevant, he, ho, decisionScan, ih]
      · have hf : op new.id old.id = false := by simpa using ho
        simp only [List.filter_cons, relevant, he, decide_false, hf, Bool.false_or, Bool.false_eq_true, ↓reduceIte]
        rw [ih]
        simp [decisionScan, he, hf]
        cases decisionScan cmp op new tail <;> rfl

theorem other_setter_preserves_relevant (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (target other : E)
    (hd : other.id ≠ target.id) (ho : op target.id other.id = false) :
    (reference op xs other).filter (relevant cmp op target.id) = xs.filter (relevant cmp op target.id) := by
  apply reference_filter
  · simp [relevant, hd, ho]
  · intro e he; simp [relevant, he, hd, ho]

theorem initial_decision_stable (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (target other : E)
    (hd : other.id ≠ target.id) (ho : op target.id other.id = false) :
    decision cmp op (reference op xs other) target = decision cmp op xs target := by
  unfold decision
  rw [← decision_projection cmp op (reference op xs other) target,
      other_setter_preserves_relevant cmp op xs target other hd ho,
      decision_projection cmp op xs target]

def compatible (cmp : Comparator ι ν) (op : ι → ι → Bool) (actions : List E) : Prop :=
  ∀ a ∈ actions, ∀ b ∈ actions, op a.id b.id = false


def replaceId (xs : List E) (new : E) : List E :=
  xs.map (fun old => if old.id = new.id then new else old)

def eraseId (xs : List E) (id : ι) : List E :=
  xs.filter (fun old => decide (old.id ≠ id))

def identityStep (xs : List E) (new : E) : Kind → List E
  | .none => xs
  | .append => xs ++ [new]
  | .replace => replaceId xs new
  | .move => eraseId xs new.id ++ [new]

theorem erase_absent (xs : List E) (id : ι) (h : absent id xs) : eraseId xs id = xs := by
  apply List.filter_eq_self.mpr
  intro e he; simp [h e he]

theorem replace_absent (xs : List E) (new : E) (h : absent new.id xs) : replaceId xs new = xs := by
  induction xs with
  | nil => rfl
  | cons e xs ih =>
    have he := h e (by simp)
    have ht : absent new.id xs := by intro x hx; exact h x (by simp [hx])
    change (if e.id = new.id then new else e) :: replaceId xs new = e :: xs
    rw [if_neg he, ih ht]

theorem identity_step_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : identityStep xs new (decision cmp op xs new) = reference op xs new := by
  rw [← planner_kind]
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
  · simp [BatchBase.planner, BatchBase.scan_absent cmp op new xs ha, planKind, identityStep, reference_absent op new xs ha]
  · rw [reference_split op new old pre post hp he]
    simp only [BatchBase.planner, BatchBase.scan_split cmp op new old pre post he hs]
    unfold BatchBase.decideFound
    split
    · change eraseId (pre ++ old :: post) new.id ++ [new] = pre ++ post ++ [new]
      have er : eraseId (pre ++ old :: post) new.id = pre ++ post := by
        unfold eraseId
        rw [List.filter_append]
        simp only [List.filter_cons, he, ne_self_iff_false, decide_false, Bool.false_eq_true, ite_false]
        change eraseId pre new.id ++ eraseId post new.id = pre ++ post
        rw [erase_absent pre new.id hp, erase_absent post new.id hs]
      rw [er]
    · split
      · next h => have heq := cmp.sound old new h; subst old; rfl
      · simp [planKind, identityStep, replaceId, he, List.map_append,
          show pre.map (fun e => if e.id = new.id then new else e) = pre from replace_absent pre new hp,
          show post.map (fun e => if e.id = new.id then new else e) = post from replace_absent post new hs]

def frozenRun (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) : List E → List E → List E
  | current, [] => current
  | current, new :: rest => frozenRun cmp op initial (identityStep current new (decision cmp op initial new)) rest

theorem frozen_run_refinement_aux (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current actions : List E)
    (hu : unique current) (hs : unique actions) (hc : compatible cmp op actions)
    (ha : ∀ new ∈ actions, decision cmp op current new = decision cmp op initial new) :
    frozenRun cmp op initial current actions = directRun op current actions := by
  induction actions generalizing current with
  | nil => rfl
  | cons new rest ih =>
    have hrest : unique rest := (List.nodup_cons.mp hs).2
    have hcompat : compatible cmp op rest := by
      intro a ha b hb; exact hc a (by simp [ha]) b (by simp [hb])
    have hagree : ∀ target ∈ rest,
        decision cmp op (reference op current new) target = decision cmp op initial target := by
      intro target ht
      have hd : new.id ≠ target.id := by
        intro h; exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨target,ht,h.symm⟩)
      rw [initial_decision_stable cmp op current target new hd (hc target (by simp [ht]) new (by simp))]
      exact ha target (by simp [ht])
    simp only [frozenRun]
    rw [← ha new (by simp), identity_step_refinement cmp op current new hu]
    change frozenRun cmp op initial (reference op current new) rest = directRun op (reference op current new) rest
    exact ih _ (reference_unique op current new hu) hrest hcompat hagree

theorem frozen_run_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) (hc : compatible cmp op actions) :
    frozenRun cmp op initial initial actions = directRun op initial actions :=
  frozen_run_refinement_aux cmp op initial initial actions hu hs hc (by intro _ _; rfl)


def prepareRemove (xs : List E) (new : E) : Kind → List E
  | .move => eraseId xs new.id
  | _ => xs

def afterStep (xs : List E) (new : E) : Kind → List E
  | .none => xs
  | .replace => replaceId xs new
  | .append | .move => xs ++ [new]

theorem split_identity_step (xs : List E) (new : E) (kind : Kind) :
    identityStep xs new kind = afterStep (prepareRemove xs new kind) new kind := by
  cases kind <;> rfl

theorem erase_replace_commute (xs : List E) (new : E) (id : ι) (hn : new.id ≠ id) :
    eraseId (replaceId xs new) id = replaceId (eraseId xs id) new := by
  induction xs with
  | nil => rfl
  | cons old tail ih =>
    by_cases he : old.id = new.id <;> by_cases hi : old.id = id <;>
      simp_all [eraseId, replaceId, List.filter_cons]

theorem erase_after_commute (xs : List E) (new : E) (kind : Kind) (id : ι)
    (hn : new.id ≠ id) : eraseId (afterStep xs new kind) id = afterStep (eraseId xs id) new kind := by
  cases kind with
  | none => rfl
  | replace => exact erase_replace_commute xs new id hn
  | append => simp [afterStep, eraseId, List.filter_append, hn]
  | move => simp [afterStep, eraseId, List.filter_append, hn]

def prepareAll (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) : List E → List E → List E
  | current, [] => current
  | current, new :: rest => prepareAll cmp op initial (prepareRemove current new (decision cmp op initial new)) rest

def afterRun (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) : List E → List E → List E
  | current, [] => current
  | current, new :: rest => afterRun cmp op initial (afterStep current new (decision cmp op initial new)) rest

def batchIdentity (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List E :=
  afterRun cmp op initial (prepareAll cmp op initial initial actions) actions

theorem prepareAll_after_commute (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial xs actions : List E)
    (new : E) (kind : Kind) (hn : absent new.id actions) :
    prepareAll cmp op initial (afterStep xs new kind) actions =
      afterStep (prepareAll cmp op initial xs actions) new kind := by
  induction actions generalizing xs with
  | nil => rfl
  | cons other rest ih =>
    have ho : new.id ≠ other.id := Ne.symm (hn other (by simp))
    have ht : absent new.id rest := by intro e he; exact hn e (by simp [he])
    simp only [prepareAll]
    have hc : prepareRemove (afterStep xs new kind) other (decision cmp op initial other) =
        afterStep (prepareRemove xs other (decision cmp op initial other)) new kind := by
      cases decision cmp op initial other <;> simp only [prepareRemove]
      exact erase_after_commute xs new kind other.id ho
    rw [hc, ih _ ht]

theorem batch_frozen_normal_form (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial xs actions : List E)
    (hs : unique actions) :
    frozenRun cmp op initial xs actions = afterRun cmp op initial (prepareAll cmp op initial xs actions) actions := by
  induction actions generalizing xs with
  | nil => rfl
  | cons new rest ih =>
    have ht : unique rest := (List.nodup_cons.mp hs).2
    have hn : absent new.id rest := by
      intro e he hi; exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨e,he,hi⟩)
    simp only [frozenRun, prepareAll, afterRun]
    rw [ih _ ht, split_identity_step, prepareAll_after_commute cmp op initial _ rest new _ hn]

theorem identity_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) (hc : compatible cmp op actions) :
    batchIdentity cmp op initial actions = directRun op initial actions := by
  rw [batchIdentity, ← batch_frozen_normal_form cmp op initial initial actions hs]
  exact frozen_run_refinement cmp op initial actions hu hs hc


def AtIdentity (xs : List E) (id : ι) (index : Nat) : Prop :=
  ∃ pre old post, xs = pre ++ old :: post ∧ pre.length = index ∧ old.id = id ∧
    absent id pre ∧ absent id post

theorem get_split (xs : List α) (index : Nat) (old : α) (h : xs[index]? = some old) :
    ∃ pre post, xs = pre ++ old :: post ∧ pre.length = index := by
  induction xs generalizing index with
  | nil => simp at h
  | cons e xs ih =>
    cases index with
    | zero =>
      have he : e = old := by simpa using h
      subst e; exact ⟨[],xs,rfl,rfl⟩
    | succ n =>
      have ht : xs[n]? = some old := by simpa using h
      obtain ⟨pre,post,hs,hl⟩ := ih n ht
      exact ⟨e::pre,post,by simp [hs],by simp [hl]⟩

theorem unique_lookup_identity (xs : List E) (index : Nat) (old : E)
    (hu : unique xs) (h : xs[index]? = some old) : AtIdentity xs old.id index := by
  obtain ⟨pre,post,rfl,hlen⟩ := get_split xs index old h
  have parts := unique_parts pre (old::post) hu
  refine ⟨pre,old,post,rfl,hlen,rfl,?_,?_⟩
  · intro e he hi
    exact parts.2.2 old.id (List.mem_map.mpr ⟨e,he,hi⟩) (by simp)
  · intro e he hi
    exact (List.nodup_cons.mp parts.2.1).1 (List.mem_map.mpr ⟨e,he,hi⟩)

theorem indexed_erase_identity (xs : List E) (id : ι) (n : Nat) (h : AtIdentity xs id n) :
    xs.eraseIdx n = eraseId xs id := by
  obtain ⟨pre,old,post,rfl,rfl,hi,hp,hs⟩ := h
  simp only [List.eraseIdx_eq_take_drop_succ]
  simp [List.drop_append]
  unfold eraseId
  rw [List.filter_append]
  simp only [List.filter_cons, hi, ne_self_iff_false, decide_false, Bool.false_eq_true, ite_false]
  have hz : pre.drop (pre.length+1) = [] := List.drop_eq_nil_of_le (by omega)
  rw [hz, List.nil_append]
  change pre ++ post = eraseId pre id ++ eraseId post id
  rw [erase_absent pre id hp, erase_absent post id hs]

theorem indexed_replace_identity (xs : List E) (new : E) (n : Nat)
    (h : AtIdentity xs new.id n) : execute xs new (.replace n) = replaceId xs new := by
  obtain ⟨pre,old,post,rfl,rfl,hi,hp,hs⟩ := h
  rw [execute_split_replace]
  simp [replaceId, List.map_append, hi,
    show pre.map (fun e => if e.id = new.id then new else e) = pre from replace_absent pre new hp,
    show post.map (fun e => if e.id = new.id then new else e) = post from replace_absent post new hs]

theorem removal_preserves_unique (xs : List E) (positions : List Nat) (hu : unique xs) :
    unique (BatchIndices.removeIndices xs positions) := by
  unfold unique
  rw [BatchIndices.map_remove_indices]
  exact BatchIndices.removal_preserves_nodup _ _ hu

theorem corrected_target_survives (xs : List E) (positions : List Nat) (n : Nat) (old : E)
    (hu : unique xs) (hd : positions.Pairwise (fun a b => b < a))
    (hn : n ∉ positions) (hg : xs[n]? = some old) :
    AtIdentity (BatchIndices.removeIndices xs positions) old.id
      (n - (BatchIndices.earlierRemovals positions n).length) := by
  apply unique_lookup_identity _ _ old (removal_preserves_unique xs positions hu)
  rw [BatchIndices.descending_rank_lookup xs positions n hd hn, hg]


theorem replace_preserves_absent (xs : List E) (new : E) (id : ι)
    (hn : new.id ≠ id) (ha : absent id xs) : absent id (replaceId xs new) := by
  intro e he
  obtain ⟨old,ho,he⟩ := List.mem_map.mp he
  split at he
  · next h => subst e; exact hn
  · next h => subst e; exact ha old ho

theorem after_preserves_identity (xs : List E) (new : E) (kind : Kind) (id : ι) (n : Nat)
    (hn : new.id ≠ id) (h : AtIdentity xs id n) : AtIdentity (afterStep xs new kind) id n := by
  obtain ⟨pre,old,post,rfl,hlen,hi,hp,hs⟩ := h
  cases kind with
  | none => exact ⟨pre,old,post,rfl,hlen,hi,hp,hs⟩
  | replace =>
    refine ⟨replaceId pre new,old,replaceId post new,?_,?_,hi,
      replace_preserves_absent pre new id hn hp,replace_preserves_absent post new id hn hs⟩
    · have ho : old.id ≠ new.id := by intro he; exact hn (he.symm.trans hi)
      simp [afterStep, replaceId, List.map_append, ho]
    · simpa [replaceId] using hlen
  | append | move =>
    refine ⟨pre,old,post++[new],by simp [afterStep,List.append_assoc],hlen,hi,hp,?_⟩
    intro e he
    rcases List.mem_append.mp he with he | he
    · exact hs e he
    · have : e = new := by simpa using he
      subst e; exact hn

def corrected (positions : List Nat) : Plan → Plan
  | .replace n => .replace (n-(BatchIndices.earlierRemovals positions n).length)
  | .move _ => .append
  | p => p

def numericAfter (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) (positions : List Nat) : List E → List E → List E
  | current, [] => current
  | current, new::rest => numericAfter cmp op initial positions
      (execute current new (corrected positions (BatchBase.planner cmp op initial new))) rest

def TargetsReady (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current actions : List E) (positions : List Nat) : Prop :=
  ∀ new ∈ actions, ∀ n, BatchBase.planner cmp op initial new = .replace n →
    AtIdentity current new.id (n-(BatchIndices.earlierRemovals positions n).length)

theorem corrected_step_matches_after (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current : List E)
    (positions : List Nat) (new : E)
    (h : ∀ n, BatchBase.planner cmp op initial new = .replace n →
      AtIdentity current new.id (n-(BatchIndices.earlierRemovals positions n).length)) :
    execute current new (corrected positions (BatchBase.planner cmp op initial new)) =
      afterStep current new (decision cmp op initial new) := by
  rw [← planner_kind]
  cases hp : BatchBase.planner cmp op initial new with
  | none => rfl
  | append => rfl
  | move n => rfl
  | replace n => exact indexed_replace_identity current new _ (h n hp)

theorem numeric_after_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial current actions : List E)
    (positions : List Nat) (hs : unique actions) (hr : TargetsReady cmp op initial current actions positions) :
    numericAfter cmp op initial positions current actions = afterRun cmp op initial current actions := by
  induction actions generalizing current with
  | nil => rfl
  | cons new rest ih =>
    have ht : unique rest := (List.nodup_cons.mp hs).2
    have hnext : TargetsReady cmp op initial (afterStep current new (decision cmp op initial new)) rest positions := by
      intro target hm n hp
      have hn : new.id ≠ target.id := by
        intro he; exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨target,hm,he.symm⟩)
      exact after_preserves_identity current new _ target.id _ hn (hr target (by simp [hm]) n hp)
    simp only [numericAfter, afterRun]
    rw [corrected_step_matches_after cmp op initial current positions new (hr new (by simp))]
    exact ih _ ht hnext

def planPosition : Plan → Option Nat
  | .replace n | .move n => some n
  | _ => none

def plannedPositions (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List Nat :=
  actions.filterMap (fun new => planPosition (BatchBase.planner cmp op initial new))

def movePosition : Plan → Option Nat
  | .move n => some n
  | _ => none

def movePositions (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List Nat :=
  actions.filterMap (fun new => movePosition (BatchBase.planner cmp op initial new))

theorem planner_position_lookup (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E) (new : E)
    (hu : unique initial) (n : Nat) (h : planPosition (BatchBase.planner cmp op initial new) = some n) :
    ∃ old, initial[n]? = some old ∧ old.id = new.id := by
  have hv := BatchBase.planner_valid cmp op initial new hu
  cases hp : BatchBase.planner cmp op initial new <;> rw [hp] at hv h
  · simp [planPosition] at h
  · simp [planPosition] at h
  all_goals
    cases hv
    rename_i pre post old he hi
    have hn : pre.length = n := by simpa [planPosition] using h
    subst initial
    refine ⟨old,?_,hi⟩
    simp [← hn]

theorem planned_positions_unique (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) : (plannedPositions cmp op initial actions).Nodup := by
  induction actions with
  | nil => simp [plannedPositions]
  | cons new rest ih =>
    have ht : unique rest := (List.nodup_cons.mp hs).2
    simp only [plannedPositions, List.filterMap_cons]
    cases hp : planPosition (BatchBase.planner cmp op initial new) with
    | none => exact ih ht
    | some n =>
      apply List.nodup_cons.mpr
      refine ⟨?_,ih ht⟩
      intro hm
      obtain ⟨other,ho,hq⟩ := List.mem_filterMap.mp hm
      obtain ⟨x,hx,hi⟩ := planner_position_lookup cmp op initial new hu n hp
      obtain ⟨y,hy,hj⟩ := planner_position_lookup cmp op initial other hu n hq
      have hxy : x = y := Option.some.inj (hx.symm.trans hy)
      have hid : other.id = new.id := hj.symm.trans (hxy ▸ hi)
      exact (List.nodup_cons.mp hs).1 (List.mem_map.mpr ⟨other,ho,hid⟩)

theorem move_positions_sublist (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    (movePositions cmp op initial actions).Sublist (plannedPositions cmp op initial actions) := by
  induction actions with
  | nil => exact .slnil
  | cons new rest ih =>
    simp only [movePositions, plannedPositions, List.filterMap_cons]
    cases BatchBase.planner cmp op initial new <;> simp only [movePosition,planPosition]
    · exact ih
    · exact ih
    · exact ih.cons _
    · exact ih.cons₂ _

def descending (positions : List Nat) : List Nat := positions.mergeSort (fun a b => decide (b ≤ a))

theorem descending_permutation (positions : List Nat) : (descending positions).Perm positions :=
  List.mergeSort_perm _ _

theorem descending_strict (positions : List Nat) (hu : positions.Nodup) :
    (descending positions).Pairwise (fun a b => b < a) := by
  have sorted : (descending positions).Pairwise (fun a b => b ≤ a) := by
    have h := List.pairwise_mergeSort (le := fun a b : Nat => decide (b ≤ a))
      (by intro a b c hab hbc; simp at *; omega)
      (by intro a b; simp; omega) positions
    simpa [descending] using h
  have unique : (descending positions).Nodup := (descending_permutation positions).nodup_iff.mpr hu
  have strengthen : ∀ (xs : List Nat), xs.Pairwise (fun a b => b ≤ a) → xs.Nodup → xs.Pairwise (fun a b => b < a) := by
    intro xs hs hn
    induction xs with
    | nil => exact .nil
    | cons a rest ih =>
      refine List.pairwise_cons.mpr ⟨?_,ih (List.pairwise_cons.mp hs).2 (List.nodup_cons.mp hn).2⟩
      intro b hb
      have hle := (List.pairwise_cons.mp hs).1 b hb
      have hne : b ≠ a := by intro he; exact (List.nodup_cons.mp hn).1 (he ▸ hb)
      omega
  exact strengthen _ sorted unique

def removedIds (xs : List E) (positions : List Nat) : List ι :=
  positions.filterMap (fun p => (xs[p]?).map Entry.id)

def withoutIds (xs : List E) (ids : List ι) : List E :=
  xs.filter (fun e => decide (e.id ∉ ids))

theorem without_erase (xs : List E) (id : ι) (ids : List ι) :
    withoutIds (eraseId xs id) ids = withoutIds xs (id::ids) := by
  simp only [withoutIds, eraseId, List.filter_filter]
  congr 1
  funext e
  simp [Bool.and_comm]

theorem removed_ids_lower (xs : List E) (p : Nat) (positions : List Nat)
    (hl : ∀ q ∈ positions, q < p) :
    removedIds (xs.eraseIdx p) positions = removedIds xs positions := by
  induction positions with
  | nil => rfl
  | cons q rest ih =>
    simp only [removedIds, List.filterMap_cons]
    have ht := ih (by intro r hr; exact hl r (by simp [hr]))
    unfold removedIds at ht
    rw [List.getElem?_eraseIdx_of_lt (hl q (by simp)), ht]

theorem descending_removal_filter (xs : List E) (positions : List Nat)
    (hu : unique xs) (hd : positions.Pairwise (fun a b => b < a))
    (hb : ∀ p ∈ positions, p < xs.length) :
    BatchIndices.removeIndices xs positions = withoutIds xs (removedIds xs positions) := by
  induction positions generalizing xs with
  | nil =>
    simp only [BatchIndices.removeIndices, List.foldl_nil, removedIds, List.filterMap_nil, withoutIds]
    exact (List.filter_eq_self.mpr (by intros; simp)).symm
  | cons p rest ih =>
    have hp := (List.pairwise_cons.mp hd).1
    have ht := (List.pairwise_cons.mp hd).2
    have hpb := hb p (by simp)
    have hl : xs[p]? = some xs[p] := List.getElem?_eq_getElem hpb
    have hat := unique_lookup_identity xs p xs[p] hu hl
    have her := indexed_erase_identity xs xs[p].id p hat
    have hrb : ∀ q ∈ rest, q < (xs.eraseIdx p).length := by
      intro q hq
      have hqp := hp q hq
      simp only [List.length_eraseIdx, if_pos hpb]
      omega
    have hru : unique (xs.eraseIdx p) := by
      simpa [BatchIndices.removeIndices] using removal_preserves_unique xs [p] hu
    change BatchIndices.removeIndices (xs.eraseIdx p) rest = _
    rw [ih _ hru ht hrb, removed_ids_lower xs p rest hp, her, without_erase]
    simp [removedIds, hl]

theorem move_positions_unique (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) : (movePositions cmp op initial actions).Nodup :=
  (planned_positions_unique cmp op initial actions hu hs).sublist (move_positions_sublist cmp op initial actions)

theorem move_position_bounds (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) : ∀ p ∈ movePositions cmp op initial actions, p < initial.length := by
  intro p hp
  obtain ⟨new,_,hn⟩ := List.mem_filterMap.mp hp
  cases hplan : BatchBase.planner cmp op initial new <;> simp [hplan,movePosition] at hn
  subst p
  exact BatchBase.planner_index_bounds cmp op initial new hu _ (Or.inr hplan)

def moveIds (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List ι :=
  actions.filterMap (fun new => match BatchBase.planner cmp op initial new with
    | .move _ => some new.id
    | _ => none)

theorem removed_move_ids (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) : removedIds initial (movePositions cmp op initial actions) = moveIds cmp op initial actions := by
  induction actions with
  | nil => rfl
  | cons new rest ih =>
    simp only [movePositions, moveIds, List.filterMap_cons]
    cases hp : BatchBase.planner cmp op initial new <;> simp only [movePosition]
    · exact ih
    · exact ih
    · exact ih
    · rename_i n
      obtain ⟨old,hl,hi⟩ := planner_position_lookup cmp op initial new hu n (by simp [hp,planPosition])
      simpa [removedIds,moveIds,movePositions,movePosition,hl,hi] using congrArg (List.cons new.id) ih

theorem without_ids_append (xs : List E) (ids more : List ι) :
    withoutIds (withoutIds xs ids) more = withoutIds xs (ids++more) := by
  simp only [withoutIds, List.filter_filter]
  congr 1
  funext e
  simp [Bool.and_comm]

theorem prepare_filter (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial xs actions : List E) :
    prepareAll cmp op initial xs actions = withoutIds xs (moveIds cmp op initial actions) := by
  induction actions generalizing xs with
  | nil =>
    simp only [prepareAll, moveIds, List.filterMap_nil, withoutIds]
    exact (List.filter_eq_self.mpr (by intros; simp)).symm
  | cons new rest ih =>
    simp only [prepareAll]
    rw [ih]
    simp only [moveIds, List.filterMap_cons]
    rw [← planner_kind]
    cases BatchBase.planner cmp op initial new <;> simp only [planKind,prepareRemove]
    exact without_erase xs new.id _

theorem sorted_removal_prepare (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) :
    BatchIndices.removeIndices initial (descending (movePositions cmp op initial actions)) =
      prepareAll cmp op initial initial actions := by
  have hp := descending_permutation (movePositions cmp op initial actions)
  rw [descending_removal_filter initial _ hu
    (descending_strict _ (move_positions_unique cmp op initial actions hu hs))
    (by intro n hn; exact move_position_bounds cmp op initial actions hu n (hp.mem_iff.mp hn))]
  rw [prepare_filter]
  have hi : (removedIds initial (descending (movePositions cmp op initial actions))).Perm (moveIds cmp op initial actions) := by
    rw [← removed_move_ids cmp op initial actions hu]
    exact hp.filterMap _
  unfold withoutIds
  congr 1
  funext e
  simp only [hi.mem_iff]

theorem unique_id_injective (xs : List E) (hu : unique xs) (a b : E)
    (ha : a ∈ xs) (hb : b ∈ xs) (he : a.id = b.id) : a = b := by
  induction xs with
  | nil => simp at ha
  | cons first rest ih =>
    have hh := (List.nodup_cons.mp hu).1
    have ht := (List.nodup_cons.mp hu).2
    rcases List.mem_cons.mp ha with hae | har
    · subst first
      rcases List.mem_cons.mp hb with hbe | hbr
      · exact hbe.symm
      · exact False.elim (hh (List.mem_map.mpr ⟨b,hbr,he.symm⟩))
    · rcases List.mem_cons.mp hb with hbe | hbr
      · subst first
        exact False.elim (hh (List.mem_map.mpr ⟨a,har,he⟩))
      · exact ih ht har hbr

theorem replace_not_removed (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) (new : E) (hm : new ∈ actions)
    (n : Nat) (hp : BatchBase.planner cmp op initial new = .replace n) :
    n ∉ movePositions cmp op initial actions := by
  intro hn
  obtain ⟨other,ho,hq⟩ := List.mem_filterMap.mp hn
  cases hpo : BatchBase.planner cmp op initial other <;> simp [hpo,movePosition] at hq
  rename_i m
  subst m
  obtain ⟨x,hx,hi⟩ := planner_position_lookup cmp op initial new hu n (by simp [hp,planPosition])
  obtain ⟨y,hy,hj⟩ := planner_position_lookup cmp op initial other hu n (by simp [hpo,planPosition])
  have hxy : x = y := Option.some.inj (hx.symm.trans hy)
  have hid : other.id = new.id := hj.symm.trans (hxy ▸ hi)
  have he : other = new := unique_id_injective actions hs other new ho hm hid
  subst other
  rw [hp] at hpo
  contradiction

def numericBatch (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List E :=
  let positions := descending (movePositions cmp op initial actions)
  numericAfter cmp op initial positions (BatchIndices.removeIndices initial positions) actions

theorem numeric_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (hu : unique initial) (hs : unique actions) (hc : compatible cmp op actions) :
    numericBatch cmp op initial actions = directRun op initial actions := by
  have hr : TargetsReady cmp op initial
      (BatchIndices.removeIndices initial (descending (movePositions cmp op initial actions)))
      actions (descending (movePositions cmp op initial actions)) := by
    intro new hm n hp
    obtain ⟨old,hl,hi⟩ := planner_position_lookup cmp op initial new hu n (by simp [hp,planPosition])
    have hn := replace_not_removed cmp op initial actions hu hs new hm n hp
    have hsn : n ∉ descending (movePositions cmp op initial actions) := by
      simpa only [(descending_permutation _).mem_iff] using hn
    have h := corrected_target_survives initial _ n old hu
      (descending_strict _ (move_positions_unique cmp op initial actions hu hs)) hsn hl
    simpa [hi] using h
  unfold numericBatch
  rw [numeric_after_refinement cmp op initial _ actions _ hs hr,
    sorted_removal_prepare cmp op initial actions hu hs]
  exact identity_batch_refinement cmp op initial actions hu hs hc

end BatchOrder
