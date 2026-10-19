import SegmentIdentity
namespace MapIdentity
open AnimationIdentity SegmentIdentity
variable {ι ν : Type} [DecidableEq ι]
abbrev Entries (ι ν : Type) := List (ι × Value ι ν)
def Coherent (xs : Entries ι ν) : Prop := ∀ k v, (k,v) ∈ xs → v.id = k
def Unique (xs : Entries ι ν) : Prop := (xs.map Prod.fst).Nodup

def lookup (key : ι) : Entries ι ν → Option (Value ι ν)
  | [] => none
  | (k,v)::rest => if key=k then some v else lookup key rest

def insert (key : ι) (v : Value ι ν) (xs : Entries ι ν) : Entries ι ν :=
  (key,v)::xs.filter (fun entry => decide (entry.1 ≠ key))

structure Action (ι ν : Type) where
  key : ι
  admitted : Bool
  segment : Segment ι ν
  last : Option (Value ι ν)
  base : Option (Value ι ν)
  iterationAccumulate : Bool
  count : Nat

def ActionId (a : Action ι ν) : Prop :=
  a.admitted=true → SegmentId a.key a.segment ∧ OptId a.key a.last ∧ OptId a.key a.base

def step (arith : Arithmetic ι ν) (xs : Entries ι ν) (a : Action ι ν) : Option (Entries ι ν) :=
  if !a.admitted then some xs else
  let needed := need a.segment a.last a.iterationAccumulate a.count
  let u := if needed then (lookup a.key xs).or a.base else none
  if needed && u.isNone then some xs else
  (compose arith a.segment u a.last a.iterationAccumulate a.count).map (fun value => insert a.key value xs)

def run (arith : Arithmetic ι ν) : Entries ι ν → List (Action ι ν) → Option (Entries ι ν)
  | xs, [] => some xs
  | xs, a::rest => (step arith xs a).bind (fun next => run arith next rest)

variable {arith : Arithmetic ι ν} {key : ι} {v : Value ι ν}

theorem lookup_id (xs : Entries ι ν) (h : Coherent xs) (key : ι) : OptId key (lookup key xs) := by
  induction xs with
  | nil => exact opt_none key
  | cons p rest ih =>
    obtain ⟨k,v⟩ := p
    by_cases he : key=k
    · subst k
      simpa [lookup,OptId] using h key v (by simp)
    · simpa [lookup,he] using ih (by intro k v hm;exact h k v (by simp [hm]))

theorem insert_coherent (xs : Entries ι ν) (h : Coherent xs) (hv : v.id=key) :
    Coherent (insert key v xs) := by
  intro k w hm
  simp only [insert,List.mem_cons,List.mem_filter] at hm
  rcases hm with he | ⟨hm,_⟩
  · cases he;exact hv
  · exact h k w hm

theorem insert_unique (xs : Entries ι ν) (h : Unique xs) (key : ι) (v : Value ι ν) :
    Unique (insert key v xs) := by
  unfold Unique insert
  rw [List.map_cons,List.nodup_cons]
  constructor
  · intro hm
    obtain ⟨⟨k,w⟩,hmem,heq⟩ := List.mem_map.mp hm
    have hn := (List.mem_filter.mp hmem).2
    simp only [decide_eq_true_eq] at hn
    exact hn heq
  · exact List.Sublist.nodup (List.filter_sublist.map _) h

theorem step_ready (xs : Entries ι ν) (a : Action ι ν) (hp : Preserves arith)
    (hx : Coherent xs) (hu : Unique xs) (ha : ActionId a) :
    ∃ next, step arith xs a = some next ∧ Coherent next ∧ Unique next := by
  cases had : a.admitted with
  | false => exact ⟨xs,by simp [step,had],hx,hu⟩
  | true =>
    have ha := ha had
    let needed := need a.segment a.last a.iterationAccumulate a.count
    let u := if needed then (lookup a.key xs).or a.base else none
    have ui : OptId a.key u := by
      dsimp [u]
      split
      · exact opt_or _ _ (lookup_id xs hx a.key) ha.2.2
      · exact opt_none _
    have stepEq : step arith xs a =
        (if needed && u.isNone then some xs else
          (compose arith a.segment u a.last a.iterationAccumulate a.count).map (fun v => insert a.key v xs)) := by
      simp only [step,had,Bool.not_true,Bool.false_eq_true,↓reduceIte]
      rfl
    by_cases stop : (needed && u.isNone)=true
    · exact ⟨xs,by rw [stepEq];simp only [stop,↓reduceIte],hx,hu⟩
    · have guard : needed=true → u.isSome=true := by
        intro hn
        cases ho : u with
        | none => simp [hn,ho] at stop
        | some v => rfl
      obtain ⟨v,hv,iv⟩ := compose_ready a.segment u a.last a.iterationAccumulate a.count hp ha.1 ui ha.2.1 guard
      refine ⟨insert a.key v xs,?_,insert_coherent xs hx iv,insert_unique xs hu a.key v⟩
      rw [stepEq]
      simp [stop,hv]

theorem finite_updates (xs : Entries ι ν) (actions : List (Action ι ν))
    (hp : Preserves arith) (hc : Coherent xs) (hu : Unique xs)
    (ha : ∀ a ∈ actions, ActionId a) :
    ∃ out, run arith xs actions=some out ∧ Coherent out ∧ Unique out := by
  induction actions generalizing xs with
  | nil => exact ⟨xs,rfl,hc,hu⟩
  | cons a rest ih =>
    obtain ⟨next,hn,hc',hu'⟩ := step_ready xs a hp hc hu (ha a (by simp))
    obtain ⟨out,ho,hco,huo⟩ := ih next hc' hu' (by intro a hm;exact ha a (by simp [hm]))
    exact ⟨out,by simp [run,hn,ho],hco,huo⟩

theorem from_empty (actions : List (Action ι ν)) (hp : Preserves arith)
    (ha : ∀ a ∈ actions, ActionId a) :
    ∃ out, run arith [] actions=some out ∧ Coherent out ∧ Unique out :=
  finite_updates [] actions hp (by simp [Coherent]) (by simp [Unique]) ha
theorem inadmissible_retains (xs : Entries ι ν) (a : Action ι ν)
    (h : a.admitted=false) : step arith xs a=some xs := by simp [step,h]

theorem missing_base_retains (xs : Entries ι ν) (a : Action ι ν)
    (hn : need a.segment a.last a.iterationAccumulate a.count=true)
    (hx : lookup a.key xs=none) (hb : a.base=none) : step arith xs a=some xs := by
  cases had : a.admitted <;> simp [step,had,hn,hx,hb]
end MapIdentity
