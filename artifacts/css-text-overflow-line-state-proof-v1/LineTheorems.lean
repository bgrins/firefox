import LineModel
namespace LineModel

theorem reset_width (m : Marker) : (reset m).width = m.width := by rfl
theorem reset_intrinsic (m : Marker) : (reset m).intrinsic = m.intrinsic := by rfl
theorem canonical_width (m : Marker) : (canonical m).width = m.intrinsic := by rfl
theorem canonical_idempotent (m : Marker) : canonical (canonical m) = canonical m := by rfl
theorem canonical_reset (m : Marker) : canonical (reset m) = canonical m := by rfl
theorem canonical_cache (m : Marker) :
    ((canonical m).style,(canonical m).intrinsic,(canonical m).initialized) =
    (m.style,m.intrinsic,m.initialized) := by rfl
theorem entry_start_width (c : Config) (s : Pair) :
    (entry c s true).start.width = s.start.intrinsic := by rfl
theorem entry_end_width (c : Config) (s : Pair) :
    (entry c s true).finish.width = s.finish.intrinsic := by rfl
theorem entry_canonical_pair (c : Config) (s : Pair) :
    entry c (canonicalPair s) true = entry c s true := by rfl

structure Cache where
  style : Nat
  intrinsic : Int
  initialized : Bool
  deriving DecidableEq, Repr

def cache (m : Marker) : Cache := ⟨m.style,m.intrinsic,m.initialized⟩
def seed (c : Cache) : Marker :=
  {style := c.style,intrinsic := c.intrinsic,width := c.intrinsic,initialized := c.initialized}
def lineEntry (s : Pair) (startActive endActive : Bool) : Pair :=
  ⟨{canonical s.start with active := startActive},{canonical s.finish with active := endActive}⟩
def seedPair (s : Pair) : Pair := ⟨seed (cache s.start),seed (cache s.finish)⟩

theorem process_ordinary_preparation (c : Config) (l : Line) (n : Nat) (s : Pair)
    (ordinary : l.clamp = none) :
    prepare c l n s true =
      (lineEntry (seedPair s) (c.styles[0]!.kind != 0)
        (c.styles[s.finish.style]!.kind != 0),none) := by
  cases h : c.styles[s.finish.style]!.kind <;>
    simp [prepare,ordinary,entry,suppressed,lineEntry,seedPair,seed,cache,canonical,reset,h]

theorem seed_cache (m : Marker) : cache (seed (cache m)) = cache m := by rfl
theorem ordinary_entry_fresh (s : Pair) (a b : Bool) :
    lineEntry (seedPair s) a b = lineEntry s a b := by rfl

variable {L O : Type}
def ordinaryStep (active : L → Bool × Bool) (kernel : L → Pair → Pair × O)
    (l : L) (s : Pair) : Pair × O :=
  kernel l (lineEntry s (active l).1 (active l).2)
def seededStep (active : L → Bool × Bool) (kernel : L → Pair → Pair × O)
    (l : L) (s : Pair) : Pair × O :=
  kernel l (lineEntry (seedPair s) (active l).1 (active l).2)

theorem ordinary_step_fresh (active : L → Bool × Bool)
    (kernel : L → Pair → Pair × O) (l : L) (s : Pair) :
    ordinaryStep active kernel l s = seededStep active kernel l s := by rfl

def runLines (step : L → Pair → Pair × O) : List L → Pair → Pair × List O
  | [],s => (s,[])
  | l::ls,s =>
    let (next,output) := step l s
    let (last,outputs) := runLines step ls next
    (last,output::outputs)

theorem finite_ordinary_reuse_fresh (active : L → Bool × Bool)
    (deterministicKernel : L → Pair → Pair × O) (lines : List L) (s : Pair) :
    runLines (ordinaryStep active deterministicKernel) lines s =
    runLines (seededStep active deterministicKernel) lines s := by rfl

def Coherent (measure : Nat → Int) (s : Pair) : Prop :=
  (s.start.initialized = true → s.start.intrinsic = measure s.start.style) ∧
  (s.finish.initialized = true → s.finish.intrinsic = measure s.finish.style)

theorem entry_coherent (measure : Nat → Int) (s : Pair) (a b : Bool)
    (h : Coherent measure s) : Coherent measure (lineEntry s a b) := h

theorem finite_coherent (measure : Nat → Int) (active : L → Bool × Bool)
    (kernel : L → Pair → Pair × O)
    (kernelPreserves : ∀ l s, Coherent measure s → Coherent measure (kernel l s).1)
    (lines : List L) (s : Pair) (initialCoherent : Coherent measure s) :
    Coherent measure (runLines (ordinaryStep active kernel) lines s).1 := by
  induction lines generalizing s with
  | nil => exact initialCoherent
  | cons l ls ih =>
    simp only [runLines]
    apply ih
    exact kernelPreserves l _ (entry_coherent measure s _ _ initialCoherent)

def clippedWidth (intrinsic available : Int) := max 0 (min intrinsic available)
theorem clipped_width_bounds (intrinsic available : Int) (h : 0 ≤ intrinsic) :
    0 ≤ clippedWidth intrinsic available ∧ clippedWidth intrinsic available ≤ intrinsic := by
  unfold clippedWidth
  omega

theorem native_clip_assignment (intrinsic available : Int)
    (positive : 0 < available) (smaller : available < intrinsic) :
    clippedWidth intrinsic available = available ∧
      0 ≤ available ∧ available ≤ intrinsic := by
  unfold clippedWidth
  omega

def startPriority (both : Bool) (startWidth endWidth areaWidth : Int) :=
  both && !(startWidth + endWidth > areaWidth)
theorem end_priority (startWidth endWidth areaWidth : Int)
    (h : startWidth + endWidth > areaWidth) :
    startPriority true startWidth endWidth areaWidth = false := by
  simp [startPriority,h]

def clampRestore (saved current : Marker) (normalCompletion : Bool) :=
  if normalCompletion then saved else current
theorem clamp_normal_restore (saved current : Marker) :
    clampRestore saved current true = saved := by rfl

#print axioms reset_width
#print axioms reset_intrinsic
#print axioms canonical_width
#print axioms canonical_idempotent
#print axioms canonical_reset
#print axioms canonical_cache
#print axioms entry_start_width
#print axioms entry_end_width
#print axioms entry_canonical_pair
#print axioms process_ordinary_preparation
#print axioms seed_cache
#print axioms ordinary_entry_fresh
#print axioms ordinary_step_fresh
#print axioms finite_ordinary_reuse_fresh
#print axioms entry_coherent
#print axioms finite_coherent
#print axioms clipped_width_bounds
#print axioms native_clip_assignment
#print axioms end_priority
#print axioms clamp_normal_restore
end LineModel
