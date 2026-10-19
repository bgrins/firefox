import Std

namespace Timeline

structure Element where
  id : Nat := 0
  primary : Nat := 0
  kind : Nat := 0
  parent : Nat := 0
  isElement : Bool := true
  apzDisabled : Bool := false
  displayport : Bool := false
  pseudos : List Nat := []
  deriving Repr, BEq, DecidableEq, Inhabited

structure Frame where
  id : Nat := 0
  parent : Nat := 0
  content : Nat := 0
  scroll : Bool := false
  target : Nat := 0
  vertical : Bool := false
  reversed : Bool := false
  availableX : Bool := false
  availableY : Bool := false
  x : Int := 0
  y : Int := 0
  width : Int := 0
  height : Int := 0
  overflowX : Nat := 0
  overflowY : Nat := 0
  shell : Bool := false
  deriving Repr, BEq, DecidableEq, Inhabited

structure World where
  sourceType : Nat := 3
  host : Nat := 0
  pseudo : Nat := 0
  axis : Nat := 0
  root : Nat := 0
  scrolling : Nat := 0
  shell : Bool := false
  rootFrame : Nat := 0
  apz : Bool := false
  elements : List Element := []
  frames : List Frame := []
  subscribers : Nat := 0
  deriving Repr, BEq, DecidableEq, Inhabited

def element (w : World) (id : Nat) : Element :=
  (w.elements.find? (fun e => e.id == id)).getD {}
def frame (w : World) (id : Nat) : Frame :=
  (w.frames.find? (fun f => f.id == id)).getD {}
def pseudo (w : World) (id request : Nat) : Nat :=
  if request = 0 then id else (element w id).pseudos[request - 1]?.getD 0

def pair (w : World) (id : Nat) : Nat × Nat :=
  let e := element w id
  if e.kind = 7 then (w.root, 7)
  else if 1 ≤ e.kind ∧ e.kind ≤ 6 then (e.parent, e.kind)
  else (id, 0)

def isRootFrame (w : World) (f : Frame) : Bool :=
  f.content != 0 && (element w f.content).isElement && f.content == w.scrolling

def eligible (w : World) (f : Frame) : Bool :=
  f.content != 0 && (element w f.content).isElement && f.scroll

def chain (w : World) : Nat → Nat → List Frame
  | 0, _ => []
  | fuel + 1, id => if id = 0 then [] else frame w id :: chain w fuel (frame w id).parent

def chooseSpec (w : World) (xs : List Frame) : Nat × Nat :=
  match ((xs.takeWhile fun f => !(isRootFrame w f)).find? (eligible w)) with
  | none => (w.scrolling, 0)
  | some f => pair w f.content

def chooseNative (w : World) : Nat → Nat → Nat × Nat
  | 0, _ => (w.scrolling, 0)
  | fuel + 1, id =>
    if id = 0 then (w.scrolling, 0)
    else if isRootFrame w (frame w id) then (w.scrolling, 0)
    else if eligible w (frame w id) then pair w (frame w id).content
    else chooseNative w fuel (frame w id).parent

theorem choose_agrees (w : World) (fuel id : Nat) :
    chooseNative w fuel id = chooseSpec w (chain w fuel id) := by
  induction fuel generalizing id with
  | zero => simp [chooseNative, chain, chooseSpec]
  | succ fuel ih =>
    simp only [chooseNative, chain]
    split
    · simp_all [chooseSpec]
    · cases hr : isRootFrame w (frame w id) <;>
        cases he : eligible w (frame w id) <;>
        simp_all [chooseSpec, List.takeWhile_cons, List.find?_cons]

inductive Path (w : World) : Nat → List Frame → Prop where
  | nil : Path w 0 []
  | cons (id : Nat) (tail : List Frame) (nonzero : id ≠ 0)
      (rest : Path w (frame w id).parent tail) :
      Path w id (frame w id :: tail)

theorem chain_complete (w : World) (id : Nat) (xs : List Frame)
    (h : Path w id xs) (fuel : Nat) (enough : xs.length ≤ fuel) :
    chain w fuel id = xs := by
  induction h generalizing fuel with
  | nil => cases fuel <;> simp [chain]
  | cons id tail hn hp ih =>
    cases fuel with
    | zero => simp at enough
    | succ fuel =>
      simp only [chain, hn, ↓reduceIte, List.cons.injEq, true_and]
      exact ih fuel (by simpa using enough)

theorem ranked_selection_complete (w : World) (id : Nat) (xs : List Frame)
    (path : Path w id xs) (bound : xs.length ≤ w.frames.length + 1) :
    chooseNative w (w.frames.length + 1) id = chooseSpec w xs := by
  rw [choose_agrees, chain_complete w id xs path _ bound]

def nearestSpec (w : World) : Nat × Nat :=
  let subject := pseudo w w.host w.pseudo
  if (element w w.host).primary = 0 ∨ subject = 0 then (0, 0)
  else if subject = w.scrolling then (subject, 0)
  else if (element w subject).primary = 0 then (0, 0)
  else chooseSpec w (chain w (w.frames.length + 1)
    (frame w (element w subject).primary).parent)

def nearestNative (w : World) : Nat × Nat :=
  if (element w w.host).primary = 0 then (0, 0)
  else
    let subject := pseudo w w.host w.pseudo
    if subject = 0 then (0, 0)
    else if w.scrolling = subject then (w.scrolling, 0)
    else if (element w subject).primary = 0 then (0, 0)
    else chooseNative w (w.frames.length + 1)
      (frame w (element w subject).primary).parent

theorem nearest_agrees (w : World) : nearestNative w = nearestSpec w := by
  unfold nearestNative nearestSpec
  by_cases hp : (element w w.host).primary = 0
  · simp [hp]
  · by_cases hs : pseudo w w.host w.pseudo = 0
    · simp [hp, hs]
    · by_cases hr : pseudo w w.host w.pseudo = w.scrolling
      · simp [hp, hs, hr]
      · simp [hp, hs, hr, Ne.symm hr, choose_agrees]

def sourceSpec (w : World) : Nat × Nat :=
  if w.sourceType = 1 then (w.scrolling, 0)
  else if w.sourceType = 2 then nearestSpec w
  else (w.host, w.pseudo)

def sourceNative (w : World) : Nat × Nat :=
  if w.sourceType = 3 then (w.host, w.pseudo)
  else if w.sourceType = 2 then nearestNative w
  else if w.sourceType = 0 ∨ w.sourceType = 4 then (w.host, w.pseudo)
  else (w.scrolling, 0)

theorem source_agrees (w : World) (valid : w.sourceType ≤ 4) :
    sourceNative w = sourceSpec w := by
  have cases : w.sourceType = 0 ∨ w.sourceType = 1 ∨ w.sourceType = 2 ∨
      w.sourceType = 3 ∨ w.sourceType = 4 := by omega
  rcases cases with h|h|h|h|h <;> simp [sourceNative, sourceSpec, h, nearest_agrees]

def frameSpec (w : World) (source : Nat × Nat) : Nat :=
  let h := source.1
  let p := source.2
  let e := pseudo w h p
  let primary := (element w e).primary
  let selected := if e = w.root ∧ ((frame w primary).shell || w.shell) ∧ w.rootFrame ≠ 0
                  then w.rootFrame else primary
  if h = 0 then 0
  else if h = w.scrolling then if w.shell then w.rootFrame else 0
  else if e = 0 then 0
  else (frame w selected).target

def frameNative (w : World) (source : Nat × Nat) : Nat :=
  if source.1 = 0 then 0
  else if source.1 = w.scrolling then
    if w.shell then w.rootFrame else 0
  else
    let e := pseudo w source.1 source.2
    if e = 0 then 0
    else
      let initial := (element w e).primary
      let selected := if e = w.root then
          if ((frame w initial).shell || w.shell) && (w.rootFrame != 0)
          then w.rootFrame else initial
        else initial
      if selected = 0 then 0 else (frame w selected).target

-- Zero is the null frame; its defaults must not fabricate a scroll target.
def NullFrame (w : World) : Prop := (frame w 0).target = 0 ∧ (frame w 0).shell = false

theorem frame_agrees (w : World) (source : Nat × Nat) (hn : NullFrame w) :
    frameNative w source = frameSpec w source := by
  rcases hn with ⟨hnt, hns⟩
  by_cases h0 : source.1 = 0
  · simp [frameNative, frameSpec, h0]
  by_cases hr : source.1 = w.scrolling
  · simp [frameNative, frameSpec, h0, hr]
  by_cases he : pseudo w source.1 source.2 = 0
  · simp [frameNative, frameSpec, h0, hr, he]
  by_cases hre : pseudo w source.1 source.2 = w.root <;>
    by_cases hs : ((frame w (element w (pseudo w source.1 source.2)).primary).shell || w.shell) = true <;>
    by_cases hz : w.rootFrame = 0 <;>
    by_cases hp : (element w (pseudo w source.1 source.2)).primary = 0 <;>
    simp_all [frameNative, frameSpec]

structure Snapshot where
  source : Nat × Nat := (0,0)
  root : Bool := false
  active : Bool := false
  axis : Nat := 0
  available : Bool := false
  style : Nat := 0
  apz : Bool := false
  deriving Repr, BEq, DecidableEq, Inhabited

structure TimeData where
  position : Int := 0
  extent : Int := 0
  deriving Repr, BEq, DecidableEq, Inhabited

structure TimelineData where
  position : Int
  start : Int
  finish : Int
  deriving Repr, BEq, DecidableEq, Inhabited

def axisSpec (requested : Nat) (vertical : Bool) : Nat :=
  if requested = 0 then if vertical then 0 else 1
  else if requested = 1 then if vertical then 1 else 0
  else if requested = 2 then 0 else 1

def axisNative (requested : Nat) (vertical : Bool) : Nat :=
  if requested = 2 ∨ (vertical = false ∧ requested = 1) ∨
      (vertical = true ∧ requested = 0) then 0 else 1

theorem axis_agrees (a : Nat) (v : Bool) (ha : a ≤ 3) : axisNative a v = axisSpec a v := by
  have cases : a = 0 ∨ a = 1 ∨ a = 2 ∨ a = 3 := by omega
  rcases cases with h|h|h|h <;> subst a <;> cases v <;> rfl

def snapshotSpec (repaired : Bool) (w : World) : Snapshot :=
  let source := sourceSpec w
  let e := element w source.1
  let scroller := frameSpec w source
  let f := frame w scroller
  let vertical := if repaired then f.vertical else (frame w e.primary).vertical
  let axis := axisSpec w.axis vertical
  let root := source.1 != 0 && source.1 == w.scrolling
  if source.1 = 0 ∨ e.primary = 0 ∨ scroller = 0 then { source, root }
  else ⟨source, root, true, axis,
    (if axis = 0 then f.availableX else f.availableY),
    (if axis = 0 then f.overflowX else f.overflowY),
    w.apz && !e.apzDisabled && e.displayport⟩

def snapshotNative (repaired : Bool) (w : World) : Snapshot :=
  let source := sourceNative w
  let root := source.1 != 0 && source.1 == w.scrolling
  if source.1 = 0 then { source, root }
  else if (element w source.1).primary = 0 then { source, root }
  else
    let scroller := frameNative w source
    if scroller = 0 then { source, root }
    else
      let f := frame w scroller
      let vertical := if repaired then f.vertical else (frame w (element w source.1).primary).vertical
      let axis := axisNative w.axis vertical
      { source, root, active := true, axis,
        available := if axis = 0 then f.availableX else f.availableY,
        style := if axis = 0 then f.overflowX else f.overflowY,
        apz := w.apz && !(element w source.1).apzDisabled && (element w source.1).displayport }

def Valid (w : World) : Prop := w.sourceType ≤ 4 ∧ w.axis ≤ 3 ∧ NullFrame w

theorem snapshot_agrees (r : Bool) (w : World) (h : Valid w) :
    snapshotNative r w = snapshotSpec r w := by
  rcases h with ⟨ht, ha, hn⟩
  simp only [snapshotNative, snapshotSpec, source_agrees w ht, frame_agrees w _ hn,
    axis_agrees _ _ ha]
  split <;> simp_all
  split <;> simp_all

structure State where
  snapshot : Option Snapshot := none
  time : Option TimeData := none
  deriving Repr, BEq, DecidableEq, Inhabited

structure Observation where
  state : State
  changed : Bool
  notifications : List Nat
  data : Option TimelineData
  deriving Repr, BEq, DecidableEq, Inhabited

def dataSpec (time : Option TimeData) : Option TimelineData :=
  time.map fun t => ⟨t.position, 0, t.extent⟩
def dataNative (time : Option TimeData) : Option TimelineData :=
  match time with
  | none => none
  | some t => some ⟨t.position, 0, t.extent⟩

def noticeSpec (n : Nat) : List Nat := (List.range n).flatMap fun i => [2*i, 2*i+1]
def noticeNative : Nat → Nat → List Nat
  | 0, _ => []
  | n+1, i => 2*i :: (2*i+1) :: noticeNative n (i+1)

def notificationNeeded (old fresh : Option TimeData) : Bool :=
  match fresh, old with
  | none, _ => false
  | some _, none => true
  | some t, some p => t.extent != p.extent

def sampleSpec (r : Bool) (w : World) (old : State) : Observation :=
  let snap := snapshotSpec r w
  let f := frame w (frameSpec w snap.source)
  let value : TimeData := if snap.axis = 0 then ⟨f.x,f.width⟩ else ⟨f.y,f.height⟩
  let fresh := if snap.active && snap.available then some value else none
  {state := ⟨some snap, fresh⟩, changed := fresh != old.time,
   notifications := if notificationNeeded old.time fresh then noticeSpec w.subscribers else [],
   data := dataSpec fresh}

def sampleNative (r : Bool) (w : World) (old : State) : Observation :=
  let snap := snapshotNative r w
  if !snap.active || !snap.available then
    {state := ⟨some snap, none⟩, changed := old.time.isSome, notifications := [], data := none}
  else
    let f := frame w (frameNative w snap.source)
    let fresh : TimeData := ⟨if snap.axis = 0 then f.x else f.y,
                             if snap.axis = 0 then f.width else f.height⟩
    let notify := match old.time with
      | none => true
      | some prev => fresh.extent != prev.extent
    {state := ⟨some snap, some fresh⟩, changed := some fresh != old.time,
     notifications := if notify then noticeNative w.subscribers 0 else [],
     data := dataNative (some fresh)}

theorem notice_agrees_general (n i : Nat) :
    noticeNative n i = (List.range' i n).flatMap (fun j => [2*j,2*j+1]) := by
  induction n generalizing i with
  | zero => simp [noticeNative]
  | succ n ih => simp [noticeNative, List.range'_succ, ih]

theorem notice_agrees (n : Nat) : noticeNative n 0 = noticeSpec n := by
  simpa [noticeSpec, List.range_eq_range'] using notice_agrees_general n 0

theorem data_agrees (time : Option TimeData) : dataNative time = dataSpec time := by
  cases time <;> rfl

theorem sample_agrees (r : Bool) (w : World) (old : State) (valid : Valid w) :
    sampleNative r w old = sampleSpec r w old := by
  unfold sampleNative sampleSpec
  rw [snapshot_agrees r w valid]
  simp only [frame_agrees w _ valid.2.2]
  cases ha : (snapshotSpec r w).active <;>
    cases hv : (snapshotSpec r w).available <;>
    cases ht : old.time <;>
    simp [ha, hv, ht, notificationNeeded, dataNative, dataSpec, notice_agrees]
  all_goals first | rfl | (split <;> simp)

def runSpec (r : Bool) : List World → State → List Observation
  | [], _ => []
  | w::ws, old =>
    let current := sampleSpec r w old
    current :: runSpec r ws current.state

def runNative (r : Bool) : List World → State → List Observation
  | [], _ => []
  | w::ws, old =>
    let current := sampleNative r w old
    current :: runNative r ws current.state

theorem finite_resampling_agrees (r : Bool) (ws : List World) (old : State)
    (valid : ∀ w ∈ ws, Valid w) : runNative r ws old = runSpec r ws old := by
  induction ws generalizing old with
  | nil => rfl
  | cons w ws ih =>
    simp only [runNative, runSpec, sample_agrees r w old (valid w (by simp))]
    rw [ih _ (by intro v hv; exact valid v (by simp [hv]))]

theorem inactive_clears (r : Bool) (w : World) (old : State)
    (h : (snapshotSpec r w).active = false ∨ (snapshotSpec r w).available = false) :
    (sampleSpec r w old).state.time = none := by
  rcases h with h|h <;> simp [sampleSpec, h]

theorem clearing_reports_old_presence (r : Bool) (w : World) (old : State)
    (h : (snapshotSpec r w).active = false ∨ (snapshotSpec r w).available = false) :
    (sampleSpec r w old).changed = old.time.isSome ∧
    (sampleSpec r w old).notifications = [] := by
  rcases h with h|h <;> cases ht : old.time <;>
    simp [sampleSpec, h, ht, notificationNeeded] <;> rfl

theorem sample_ignores_previous_snapshot (r : Bool) (w : World)
    (oldTime : Option TimeData) (a b : Option Snapshot) :
    sampleSpec r w ⟨a,oldTime⟩ = sampleSpec r w ⟨b,oldTime⟩ := rfl

theorem reconstructed_time_ignores_previous_time (r : Bool) (w : World) (a b : State) :
    (sampleSpec r w a).state = (sampleSpec r w b).state := rfl

theorem snapshot_cached_at_sample (r : Bool) (w : World) (old : State) :
    (sampleSpec r w old).state.snapshot = some (snapshotSpec r w) := rfl

def getSnapshot (s : State) : Snapshot := s.snapshot.getD {}

theorem default_snapshot_inactive : (getSnapshot {}).active = false := rfl

theorem getSnapshot_after_sample (r : Bool) (w : World) (old : State) :
    getSnapshot (sampleSpec r w old).state = snapshotSpec r w := rfl

theorem data_absence_exact (time : Option TimeData) :
    dataSpec time = none ↔ time = none := by cases time <;> simp [dataSpec]

theorem data_preserves_record (t : TimeData) :
    dataSpec (some t) = some ⟨t.position, 0, t.extent⟩ := rfl

theorem change_exact (r : Bool) (w : World) (old : State) :
    (sampleSpec r w old).changed = ((sampleSpec r w old).state.time != old.time) := rfl

theorem notifications_exact (r : Bool) (w : World) (old : State) :
    (sampleSpec r w old).notifications =
      (if notificationNeeded old.time (sampleSpec r w old).state.time
       then noticeSpec w.subscribers else []) := rfl

theorem position_only_no_notification (a b : TimeData) (extent : a.extent = b.extent) :
    notificationNeeded (some a) (some b) = false := by
  simp [notificationNeeded, extent]

theorem newly_active_notifies (fresh : TimeData) :
    notificationNeeded none (some fresh) = true := rfl

theorem extent_change_notifies (a b : TimeData) (different : a.extent ≠ b.extent) :
    notificationNeeded (some a) (some b) = true := by
  simp [notificationNeeded, Ne.symm different]

theorem physical_x_mode_invariant (v : Bool) : axisSpec 2 v = 0 := rfl

theorem physical_y_mode_invariant (v : Bool) : axisSpec 3 v = 1 := rfl

theorem logical_axes_exchange (v : Bool) :
    axisSpec 0 v = axisSpec 1 (!v) ∧ axisSpec 1 v = axisSpec 0 (!v) := by
  cases v <;> decide

def RepairPreserved (w : World) : Prop :=
  w.axis = 2 ∨ w.axis = 3 ∨
  (frame w (frameSpec w (sourceSpec w))).vertical =
    (frame w (element w (sourceSpec w).1).primary).vertical

theorem snapshot_repair_preserved (w : World) (h : RepairPreserved w) :
    snapshotSpec true w = snapshotSpec false w := by
  rcases h with h|h|h <;> simp [snapshotSpec, h, axisSpec]

theorem sampling_repair_preserved (w : World) (old : State) (h : RepairPreserved w) :
    sampleSpec true w old = sampleSpec false w old := by
  simp only [sampleSpec, snapshot_repair_preserved w h]

theorem finite_repair_preserved (ws : List World) (old : State)
    (preserved : ∀ w ∈ ws, RepairPreserved w) :
    runSpec true ws old = runSpec false ws old := by
  induction ws generalizing old with
  | nil => rfl
  | cons w ws ih =>
    simp only [runSpec, sampling_repair_preserved w old (preserved w (by simp))]
    rw [ih _ (by intro v hv; exact preserved v (by simp [hv]))]

def progress (time : Option TimeData) : Option Rat :=
  time.map fun t => (t.position.natAbs : Rat) / (t.extent : Rat)

theorem progress_record_congruence (a b : Option TimeData) (h : a = b) :
    progress a = progress b := by rw [h]

theorem progress_repair_preserved (w : World) (old : State) (h : RepairPreserved w) :
    progress (sampleSpec true w old).state.time = progress (sampleSpec false w old).state.time := by
  rw [sampling_repair_preserved w old h]


def ModeMutation (w : World) (fs : List Frame) (id : Nat) (vertical : Bool) : Prop :=
  ∀ k, frame {w with frames := fs} k =
    {frame w k with vertical := if k = id then vertical else (frame w k).vertical}

theorem named_identity (w : World) (named : w.sourceType = 3) :
    sourceSpec w = (w.host, w.pseudo) := by simp [sourceSpec, named]

theorem named_source_exposure (w : World) (named : w.sourceType = 3) :
    (sourceSpec w).1 = w.host ∧ (sourceSpec w).2 = w.pseudo := by
  simp [named_identity w named]

theorem mode_mutation_resolves_same (w : World) (fs : List Frame) (id : Nat)
    (v : Bool) (source : Nat × Nat) (mutation : ModeMutation w fs id v) :
    frameSpec {w with frames := fs} source = frameSpec w source := by
  simp only [frameSpec, pseudo, element]
  simp only [ModeMutation] at mutation
  simp only [mutation]
  rfl

theorem named_host_mode_snapshot (w : World) (fs : List Frame) (v : Bool)
    (named : w.sourceType = 3)
    (mutation : ModeMutation w fs (element w w.host).primary v)
    (distinct : frameSpec w (w.host,w.pseudo) ≠ (element w w.host).primary) :
    snapshotSpec true {w with frames := fs} = snapshotSpec true w := by
  have names : sourceSpec {w with frames := fs} = (w.host,w.pseudo) := by
    simp [sourceSpec, named]
  simp only [snapshotSpec, names, named_identity w named,
    mode_mutation_resolves_same w fs _ v _ mutation, Bool.true_eq, ↓reduceIte]
  simp only [ModeMutation] at mutation
  simp only [mutation, element]
  simp only [element] at distinct
  simp only [distinct, ↓reduceIte]
  rfl

theorem named_host_mode_sample (w : World) (fs : List Frame) (v : Bool) (old : State)
    (named : w.sourceType = 3)
    (mutation : ModeMutation w fs (element w w.host).primary v)
    (distinct : frameSpec w (w.host,w.pseudo) ≠ (element w w.host).primary) :
    sampleSpec true {w with frames := fs} old = sampleSpec true w old := by
  simp only [sampleSpec, named_host_mode_snapshot w fs v named mutation distinct,
    mode_mutation_resolves_same w fs _ v _ mutation]
  simp only [ModeMutation] at mutation
  simp only [mutation]

theorem named_host_mode_progress (w : World) (fs : List Frame) (v : Bool) (old : State)
    (named : w.sourceType = 3)
    (mutation : ModeMutation w fs (element w w.host).primary v)
    (distinct : frameSpec w (w.host,w.pseudo) ≠ (element w w.host).primary) :
    progress (sampleSpec true {w with frames := fs} old).state.time =
    progress (sampleSpec true w old).state.time := by
  rw [named_host_mode_sample w fs v old named mutation distinct]

def Inactive (w : World) : Prop := (sourceSpec w).1 = 0 ∨
  (element w (sourceSpec w).1).primary = 0 ∨ frameSpec w (sourceSpec w) = 0

theorem inactive_repair_preserved (w : World) (h : Inactive w) :
    snapshotSpec true w = snapshotSpec false w := by
  change (sourceSpec w).1 = 0 ∨ (element w (sourceSpec w).1).primary = 0 ∨ frameSpec w (sourceSpec w) = 0 at h
  simp [snapshotSpec, h]

def RepairDomain (w : World) : Prop := Inactive w ∨ RepairPreserved w

theorem complete_sampling_preservation (w : World) (old : State) (h : RepairDomain w) :
    sampleSpec true w old = sampleSpec false w old := by
  rcases h with h|h
  · simp only [sampleSpec, inactive_repair_preserved w h]
  · exact sampling_repair_preserved w old h

theorem complete_finite_preservation (ws : List World) (old : State)
    (h : ∀ w ∈ ws, RepairDomain w) : runSpec true ws old = runSpec false ws old := by
  induction ws generalizing old with
  | nil => rfl
  | cons w ws ih =>
    simp only [runSpec, complete_sampling_preservation w old (h w (by simp))]
    rw [ih _ (by intro v hv; exact h v (by simp [hv]))]

theorem resolved_source_dimensions (w : World) (active : ¬ Inactive w) :
    let source := sourceSpec w
    let f := frame w (frameSpec w source)
    let axis := axisSpec w.axis f.vertical
    (snapshotSpec true w).source = source ∧
    (snapshotSpec true w).axis = axis ∧
    (snapshotSpec true w).available = (if axis = 0 then f.availableX else f.availableY) ∧
    (snapshotSpec true w).style = (if axis = 0 then f.overflowX else f.overflowY) := by
  simp [snapshotSpec, Inactive] at active ⊢
  simp [active.1, active.2.1, active.2.2]

theorem sample_uses_resolved_data (w : World) (old : State)
    (active : ¬ Inactive w) (available : (snapshotSpec true w).available = true) :
    let f := frame w (frameSpec w (sourceSpec w))
    let axis := axisSpec w.axis f.vertical
    (sampleSpec true w old).state.time =
      some (if axis = 0 then ⟨f.x,f.width⟩ else ⟨f.y,f.height⟩) := by
  simp [Inactive] at active
  simp [sampleSpec, snapshotSpec, active.1, active.2.1, active.2.2] at available ⊢
  simp [available]

def NumericDomain (t : TimeData) : Prop :=
  -2147483647 ≤ t.position ∧ t.position ≤ 2147483647 ∧
  0 < t.extent ∧ t.extent ≤ 2147483647

theorem rational_selected_progress (w : World) (old : State)
    (active : ¬ Inactive w) (available : (snapshotSpec true w).available = true) :
    let f := frame w (frameSpec w (sourceSpec w))
    let axis := axisSpec w.axis f.vertical
    progress (sampleSpec true w old).state.time = some
      ((if axis = 0 then f.x.natAbs else f.y.natAbs : Rat) /
       (if axis = 0 then f.width else f.height : Rat)) := by
  rw [sample_uses_resolved_data w old active available]
  simp only [progress, Option.map_some]
  split <;> rfl


theorem direction_does_not_exchange_axes (requested : Nat) (f : Frame) (reverse : Bool) :
    axisSpec requested ({f with reversed := reverse}.vertical) = axisSpec requested f.vertical := rfl

theorem sign_preserves_rational_magnitude (t : TimeData) :
    progress (some {t with position := -t.position}) = progress (some t) := by
  simp [progress, Int.natAbs_neg]

theorem numeric_domain_nonzero (t : TimeData) (valid : NumericDomain t) : t.extent ≠ 0 := by
  obtain ⟨_,_,h,_⟩ := valid
  omega

theorem chain_apz_independent (w : World) (enabled : Bool) (fuel id : Nat) :
    chain {w with apz := enabled} fuel id = chain w fuel id := by
  induction fuel generalizing id with
  | zero => rfl
  | succ n ih => simp only [chain, frame, ih]

theorem source_apz_independent (w : World) (enabled : Bool) :
    sourceSpec {w with apz := enabled} = sourceSpec w := by
  simp only [sourceSpec, nearestSpec, pseudo, element, frame, chain_apz_independent]
  have choose (xs : List Frame) : chooseSpec {w with apz := enabled} xs = chooseSpec w xs := by
    simp only [chooseSpec, isRootFrame, eligible, element, pair]
    rfl
  simp only [choose]
  rfl

theorem apz_enable_time_noninterference (r : Bool) (w : World) (old : State) (enabled : Bool) :
    (sampleSpec r {w with apz := enabled} old).state.time = (sampleSpec r w old).state.time := by
  have hf (source : Nat × Nat) : frameSpec {w with apz := enabled} source = frameSpec w source := rfl
  have he (id : Nat) : element {w with apz := enabled} id = element w id := rfl
  have hfr (id : Nat) : frame {w with apz := enabled} id = frame w id := rfl
  simp only [sampleSpec, snapshotSpec, source_apz_independent, hf, he, hfr]
  split <;> rfl


def HostModeStep (a b : World) : Prop := ∃ fs v,
  b = {a with frames := fs} ∧ a.sourceType = 3 ∧
  ModeMutation a fs (element a a.host).primary v ∧
  frameSpec a (a.host,a.pseudo) ≠ (element a a.host).primary

theorem host_mode_step_agrees (a b : World) (old : State) (h : HostModeStep a b) :
    sampleSpec true a old = sampleSpec true b old := by
  obtain ⟨fs,v,rfl,named,mutation,distinct⟩ := h
  exact (named_host_mode_sample a fs v old named mutation distinct).symm

inductive HostModeSequence : List World → List World → Prop where
  | nil : HostModeSequence [] []
  | cons {a b : World} {as bs : List World} (step : HostModeStep a b)
      (rest : HostModeSequence as bs) : HostModeSequence (a::as) (b::bs)

theorem finite_host_mode_noninterference (a b : List World) (old : State)
    (h : HostModeSequence a b) : runSpec true a old = runSpec true b old := by
  induction h generalizing old with
  | nil => rfl
  | @cons a b as bs step rest ih =>
    simp only [runSpec,host_mode_step_agrees a b old step]
    rw [ih]

theorem direct_source_identity (w : World)
    (kind : w.sourceType = 0 ∨ w.sourceType = 3 ∨ w.sourceType = 4) :
    sourceSpec w = (w.host,w.pseudo) := by
  rcases kind with h|h|h <;> simp [sourceSpec,h]

theorem generated_pair_identity (w : World) (id : Nat)
    (lo : 1 ≤ (element w id).kind) (hi : (element w id).kind ≤ 6) :
    pair w id = ((element w id).parent,(element w id).kind) := by
  have h : (element w id).kind ≠ 7 := by omega
  simp [pair,h,lo,hi]

theorem ordinary_pair_identity (w : World) (id : Nat) (h : (element w id).kind = 0) :
    pair w id = (id,0) := by simp [pair,h]

end Timeline
