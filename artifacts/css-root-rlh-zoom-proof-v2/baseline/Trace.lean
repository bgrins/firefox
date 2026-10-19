import Model
namespace Rlh
structure RootRecord where
  owner : Owner
  zoom : Zoom owner
  provider : Provider owner
  ready : provider.Valid zoom

def RootRecord.value (r : RootRecord) := semanticLine r.provider.font r.provider.form
structure CacheRecord where
  owner : Owner
  value : Rat
  deriving DecidableEq, Repr
structure State where
  root : RootRecord
  cache : Option CacheRecord
  published : Bool
  used : Bool

def invariant (s : State) : Prop :=
  s.published = true → s.cache = some ⟨s.root.owner, s.root.value⟩

def initial (r : RootRecord) : State := ⟨r, none, false, false⟩
def commit (s : State) (r : RootRecord) : State := {s with root := r, published := false}
def publishNative (s : State) : State :=
  {s with cache := some ⟨s.root.owner, s.root.provider.stored.value / s.root.zoom.value⟩,
          published := true}
def publishReference (s : State) : State :=
  {s with cache := some ⟨s.root.owner, s.root.value⟩, published := true}

theorem publication_value (r : RootRecord) :
    r.provider.stored.value / r.zoom.value = r.value := by
  rw [r.ready, Rat.mul_div_cancel r.zoom.nonzero]
  rfl
theorem publication_refinement (s : State) : publishNative s = publishReference s := by
  simp [publishNative, publishReference, publication_value]
theorem initial_invariant (r : RootRecord) : invariant (initial r) := by simp [invariant, initial]
theorem commit_invariant (s : State) (r : RootRecord) : invariant (commit s r) := by simp [invariant, commit]
theorem publish_invariant (s : State) : invariant (publishNative s) := by
  simp [invariant, publishNative, publication_value]
theorem publish_owner (s : State) : (publishNative s).cache.map CacheRecord.owner = some s.root.owner := by
  simp [publishNative]
theorem publication_unscaled (s : State) : (publishNative s).cache.map CacheRecord.value = some s.root.value := by
  simp [publishNative, publication_value]

structure Request where
  world : World
  structural : Valid { world with cache := ⟨world.rootSemantic⟩ }

def requestAdmitted (s : State) (q : Request) : Prop :=
  q.world.root = s.root.owner ∧ q.world.rootSemantic = s.root.value ∧
  (q.world.role = .descendant → s.published = true) ∧
  (q.world.role = .root → q.world.consumerZoom.value = s.root.zoom.value) ∧
  (q.world.role = .root → q.world.base = .current →
    semanticLine q.world.current.font q.world.current.form = s.root.value)

def actualWorld (s : State) (q : Request) : World :=
  {q.world with cache := ⟨(s.cache.map CacheRecord.value).getD 0⟩}

def readNative (s : State) (q : Request) : Observation := implementation (actualWorld s q)
def readReference (_s : State) (q : Request) : Observation := reference q.world

theorem reference_cache_independent (w : World) (value : Rat) :
    reference {w with cache := ⟨value⟩} = reference w := rfl

theorem valid_actual (s : State) (q : Request) (hi : invariant s)
    (ha : requestAdmitted s q) (hc : q.world.role = .descendant) : Valid (actualWorld s q) := by
  have cacheEq := hi (ha.2.2.1 hc)
  have h := q.structural
  refine ⟨h.current, h.inherited, h.transport, h.initial, ?_, h.rootOwner,
          h.sameDocument, h.parentDocument, h.initialDocument⟩
  simp [actualWorld, cacheEq, ha.2.1]

theorem noncached_cache_independent (w : World) (v : Rat) (h : w.role ≠ .descendant) :
    implementation {w with cache := ⟨v⟩} = implementation w := by
  cases hr : w.role <;> simp_all [implementation, builderValue]

theorem read_refinement (s : State) (q : Request) (hi : invariant s)
    (ha : requestAdmitted s q) : readNative s q = readReference s q := by
  unfold readNative readReference
  by_cases hc : q.world.role = .descendant
  · rw [candidate_refines_reference (actualWorld s q) (valid_actual s q hi ha hc)]
    rfl
  · have hcanon := candidate_refines_reference
        {q.world with cache := ⟨q.world.rootSemantic⟩} q.structural
    rw [noncached_cache_independent q.world q.world.rootSemantic hc] at hcanon
    rw [show actualWorld s q = {q.world with cache := ⟨(s.cache.map CacheRecord.value).getD 0⟩} from rfl]
    rw [noncached_cache_independent q.world _ hc, hcanon]
    rfl

inductive Event where
  | update (root : RootRecord)
  | publish
  | read (request : Request)
  | foreignUpdate (owner : Owner)

def admitted (s : State) : Event → Prop
  | .read q => requestAdmitted s q
  | .foreignUpdate o => o.document ≠ s.root.owner.document
  | _ => True

def stepNative (s : State) : Event → State × Option Observation
  | .update r => (commit s r, none)
  | .publish => (publishNative s, none)
  | .read q => ({s with used := s.used || (readNative s q).cacheUsed}, some (readNative s q))
  | .foreignUpdate _ => (s, none)

def stepReference (s : State) : Event → State × Option Observation
  | .update r => (commit s r, none)
  | .publish => (publishReference s, none)
  | .read q => ({s with used := s.used || (readReference s q).cacheUsed}, some (readReference s q))
  | .foreignUpdate _ => (s, none)

theorem step_refinement (s : State) (e : Event) (hi : invariant s) (ha : admitted s e) :
    stepNative s e = stepReference s e := by
  cases e with
  | update r => rfl
  | publish => simp [stepNative, stepReference, publication_refinement]
  | read q => simp only [admitted] at ha
              simp [stepNative, stepReference, read_refinement s q hi ha]
  | foreignUpdate _ => rfl

theorem step_invariant (s : State) (e : Event) (hi : invariant s) :
    invariant (stepNative s e).1 := by
  cases e with
  | update r => exact commit_invariant s r
  | publish => exact publish_invariant s
  | read q => exact hi
  | foreignUpdate _ => exact hi

def runNative (s : State) : List Event → State × List (Option Observation)
  | [] => (s, [])
  | e :: es =>
      let step := stepNative s e
      let rest := runNative step.1 es
      (rest.1, step.2 :: rest.2)

def runReference (s : State) : List Event → State × List (Option Observation)
  | [] => (s, [])
  | e :: es =>
      let step := stepReference s e
      let rest := runReference step.1 es
      (rest.1, step.2 :: rest.2)

def admittedTrace (s : State) : List Event → Prop
  | [] => True
  | e :: es => admitted s e ∧ admittedTrace (stepReference s e).1 es

theorem finite_sequence_refinement (events : List Event) (s : State)
    (hi : invariant s) (ha : admittedTrace s events) :
    runNative s events = runReference s events := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
      have hs := step_refinement s e hi ha.1
      have hn := step_invariant s e hi
      rw [hs] at hn
      simp only [runNative, runReference, hs]
      rw [ih (stepReference s e).1 hn ha.2]

theorem finite_sequence_invariant (events : List Event) (s : State) (hi : invariant s) :
    invariant (runNative s events).1 := by
  induction events generalizing s with
  | nil => exact hi
  | cons e es ih => exact ih _ (step_invariant s e hi)

theorem read_preserves_cache (s : State) (q : Request) :
    (stepNative s (.read q)).1.cache = s.cache := rfl
theorem read_preserves_root (s : State) (q : Request) :
    (stepNative s (.read q)).1.root = s.root := rfl
theorem foreign_document_noninterference (s : State) (o : Owner) :
    stepNative s (.foreignUpdate o) = (s, none) := rfl
theorem refresh_latest (s : State) (r : RootRecord) :
    (publishNative (commit s r)).cache = some ⟨r.owner,r.value⟩ := by
  simp [publishNative, commit, publication_value]
theorem repeated_publication (s : State) : publishNative (publishNative s) = publishNative s := rfl
def requestBool (s : State) (q : Request) : Bool :=
  decide (q.world.root = s.root.owner) && decide (q.world.rootSemantic = s.root.value) &&
  (decide (q.world.role ≠ .descendant) || s.published) &&
  (decide (q.world.role ≠ .root) || decide (q.world.consumerZoom.value = s.root.zoom.value)) &&
  (decide (q.world.role ≠ .root) || decide (q.world.base ≠ .current) ||
    decide (semanticLine q.world.current.font q.world.current.form = s.root.value))

theorem requestBool_sound (s : State) (q : Request) (h : requestBool s q = true) :
    requestAdmitted s q := by
  simp only [requestBool,Bool.and_eq_true,Bool.or_eq_true,decide_eq_true_eq] at h
  rcases h with ⟨⟨⟨⟨a,b⟩,c⟩,d⟩,e⟩
  refine ⟨a,b,?_,?_,?_⟩
  · intro hr; exact c.resolve_left (not_not_intro hr)
  · intro hr; exact d.resolve_left (not_not_intro hr)
  · intro hr hb
    exact (e.resolve_left (fun x => x.elim (fun x => x hr) (fun x => x hb)))
end Rlh
