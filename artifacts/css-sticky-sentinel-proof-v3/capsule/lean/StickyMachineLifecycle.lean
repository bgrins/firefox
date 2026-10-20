import StickyIndexed

namespace StickyMachineLifecycle
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed

def machinePoint (p : Point) : Point := ⟨signed32 p.x, signed32 p.y⟩
def machinePlus (a b : Point) : Point :=
  ⟨signed32 (signed32 a.x + signed32 b.x), signed32 (signed32 a.y + signed32 b.y)⟩
def machineMinus (a b : Point) : Point :=
  ⟨signed32 (signed32 a.x - signed32 b.x), signed32 (signed32 a.y - signed32 b.y)⟩
def machineXMost (r : Rect) : Int := saturate32 (signed32 r.x + signed32 r.width)
def machineYMost (r : Rect) : Int := saturate32 (signed32 r.y + signed32 r.height)

def machinePosition (o : Option Margin) (n : Point) (s c : Rect) : Point :=
  let n := machinePoint n
  match o with
  | none => n
  | some v =>
    let p := if v.top != autoCode then
      {n with y := max n.y (min (signed32 s.y) (machineYMost c))} else n
    let p := if v.bottom != autoCode then
      {p with y := min p.y (max (machineYMost s) (signed32 c.y))} else p
    let p := if v.left != autoCode then
      {p with x := max p.x (min (signed32 s.x) (machineXMost c))} else p
    if v.right != autoCode then
      {p with x := min p.x (max (machineXMost s) (signed32 c.x))} else p

theorem machine_point_exact (p : Point) (h : PointSafe p) : machinePoint p = p := by
  simp only [machinePoint, signed32_identity _ h.1, signed32_identity _ h.2]

theorem machine_far_exact (r : Rect) (h : RectSafe r) :
    machineXMost r = xMost r ∧ machineYMost r = yMost r := by
  simp only [machineXMost, machineYMost, signed32_identity _ h.1,
    signed32_identity _ h.2.1, signed32_identity _ h.2.2.1,
    signed32_identity _ h.2.2.2.1]
  exact saturated_rect_edges_exact r h

theorem machine_position_exact (o : Option Margin) (n : Point) (s c : Rect)
    (hn : PointSafe n) (hs : RectSafe s) (hc : RectSafe c) :
    machinePosition o n s c = referencePosition o n s c := by
  have es := machine_far_exact s hs
  have ec := machine_far_exact c hc
  rw [← projection_refinement]
  simp only [machinePosition, machine_point_exact n hn,
    es.1, es.2, ec.1, ec.2, signed32_identity _ hs.1,
    signed32_identity _ hs.2.1, signed32_identity _ hc.1,
    signed32_identity _ hc.2.1]
  rfl

def ComputeSafe (w : World) (i : Nat) (space : Space) : Prop :=
  let n := w.nodes[i]!
  let g := providedGeometry n space
  PointSafe (observedNormal n) ∧ RectSafe g.stick ∧ RectSafe g.contain

theorem compute_projection_congr (p q : Projection) (repeatLookup : Bool)
    (i : Nat) (space : Space) (w : World)
    (h : p w.nodes[i]!.offsets (observedNormal w.nodes[i]!)
        (providedGeometry w.nodes[i]! space).stick (providedGeometry w.nodes[i]! space).contain =
      q w.nodes[i]!.offsets (observedNormal w.nodes[i]!)
        (providedGeometry w.nodes[i]! space).stick (providedGeometry w.nodes[i]! space).contain) :
    (StickyLifecycle.compute p repeatLookup i space).run w =
      (StickyLifecycle.compute q repeatLookup i space).run w := by
  cases repeatLookup <;>
    exact Prod.ext h rfl

theorem machine_compute_exact (repeatLookup : Bool) (i : Nat) (space : Space)
    (w : World) (h : ComputeSafe w i space) :
    (StickyLifecycle.compute machinePosition repeatLookup i space).run w =
      (StickyLifecycle.compute referencePosition repeatLookup i space).run w := by
  apply compute_projection_congr
  exact machine_position_exact _ _ _ _ h.1 h.2.1 h.2.2

def machineStep (d : Point) (i : Nat) : StateM World (Option Nat) := do
  let n ← normal i
  setPosition i (machinePlus n d)
  next i

def machineMoveChain (d : Point) : Nat → Option Nat → StateM World Unit
  | _, none => pure ()
  | 0, some _ => modify fun w => {w with exhausted := true}
  | fuel + 1, some i => do
    let n ← normal i
    setPosition i (machinePlus n d)
    machineMoveChain d fuel (← next i)

def LoopSafe (w : World) (ids : List Nat) (d : Point) : Prop :=
  PointSafe d ∧ ∀ i ∈ ids,
    PointSafe (observedNormal w.nodes[i]!) ∧
    PointSafe (plus (observedNormal w.nodes[i]!) d)

theorem machine_step_exact (i : Nat) (w : World)
    (hn : PointSafe (observedNormal w.nodes[i]!)) (hd : PointSafe d)
    (hs : PointSafe (plus (observedNormal w.nodes[i]!) d)) :
    (machineStep d i).run w = (step d i).run w := by
  have he : machinePlus (observedNormal w.nodes[i]!) d =
      plus (observedNormal w.nodes[i]!) d := addition_machine_exact _ _ hn hd hs
  dsimp [machineStep, step, normal, node, emit, StateT.run]
  change (do
      let _ ← setPosition i (machinePlus (observedNormal w.nodes[i]!) d)
      next i).run ((normal i).run w).2 =
    (do
      let _ ← setPosition i (plus (observedNormal w.nodes[i]!) d)
      next i).run ((normal i).run w).2
  rw [he]

theorem machine_move_succ (d : Point) (fuel i : Nat) (w : World) :
    (machineMoveChain d (fuel + 1) (some i)).run w =
      (machineMoveChain d fuel ((machineStep d i).run w).1).run
        ((machineStep d i).run w).2 := by rfl

theorem machine_indexed_refinement (d : Point) (ids : List Nat)
    (start : Option Nat) (fuel : Nat) (w : World)
    (hc : Chain w.nodes start ids) (hs : LoopSafe w ids d) :
    (machineMoveChain d fuel start).run w = (moveChain d fuel start).run w := by
  induction ids generalizing start fuel w with
  | nil =>
    cases start with
    | none => cases fuel <;> rfl
    | some i => cases hc
  | cons i rest ih =>
    cases start with
    | none => cases hc
    | some k =>
      rcases hc with ⟨he, hi, hn, ht⟩
      subst k
      cases fuel with
      | zero => rfl
      | succ fuel =>
        rw [machine_move_succ, move_succ]
        have hs0 := hs.2 i (List.mem_cons_self ..)
        rw [machine_step_exact i w hs0.1 hs.1 hs0.2]
        apply ih
        · rw [step_next d i w hi]
          exact step_chain d i w _ rest ht
        · refine ⟨hs.1, ?_⟩
          intro j hj
          have hji : i ≠ j := by intro e; subst j; exact hn hj
          have hb := (chain_members _ _ _ ht).2 j hj
          rw [step_nodes, modified_node _ _ _ hb, ite_eq_right hji]
          exact hs.2 j (List.mem_cons_of_mem i hj)

theorem machine_common_translation (d : Point) (ids : List Nat)
    (start : Option Nat) (w : World)
    (hc : Chain w.nodes start ids) (hs : LoopSafe w ids d) :
    Applied d ids w ((machineMoveChain d (w.nodes.size + 1) start).run w).2 := by
  rw [machine_indexed_refinement d ids start _ w hc hs]
  exact source_fuel_sufficient d ids start w hc

def computedReference (w : World) (i : Nat) (space : Space) : Point :=
  let n := w.nodes[i]!
  let g := providedGeometry n space
  referencePosition n.offsets (observedNormal n) g.stick g.contain

theorem prepared_machine_exact (repeatLookup : Bool) (i : Nat) (w : World)
    (h : ComputeSafe w i .current) :
    (prepared machinePosition repeatLookup i).run w =
      (prepared orderedPosition repeatLookup i).run w := by
  rw [projection_refinement]
  let q := (normal i).run w
  have he := machine_compute_exact repeatLookup i .current q.2 h
  change (let p := (StickyLifecycle.compute machinePosition repeatLookup i .current).run q.2;
          ((q.1, p.1), p.2)) =
    (let p := (StickyLifecycle.compute referencePosition repeatLookup i .current).run q.2;
          ((q.1, p.1), p.2))
  rw [he]

def machineContinuations (repeatLookup : Bool) (i : Nat) : StateM World Unit := do
  let q ← normal i
  let f ← node i
  if f.hadNormal then
    let p ← StickyLifecycle.compute machinePosition repeatLookup i .current
    let fuel := (← get).nodes.size + 1
    machineMoveChain (machineMinus p q) fuel (some i)

def ContinuationSafe (w : World) (i : Nat) (ids : List Nat) : Prop :=
  w.nodes[i]!.hadNormal = true →
    ComputeSafe w i .current ∧ PointSafe (computedReference w i .current) ∧
    PointSafe (referenceDelta w i) ∧ LoopSafe w ids (referenceDelta w i)

theorem machine_continuations_enter (repeatLookup : Bool) (i : Nat) (w : World)
    (h : w.nodes[i]!.hadNormal = true) :
    (machineContinuations repeatLookup i).run w =
      let p := (prepared machinePosition repeatLookup i).run w
      (machineMoveChain (machineMinus p.1.2 p.1.1)
        (w.nodes.size + 1) (some i)).run p.2 := by
  dsimp [machineContinuations, prepared, normal, node, emit, StateT.run]
  simp [h]
  cases repeatLookup <;> rfl

theorem machine_continuations_exact (repeatLookup : Bool) (i : Nat) (w : World)
    (ids : List Nat) (hc : Chain w.nodes (some i) ids)
    (hs : ContinuationSafe w i ids) :
    (machineContinuations repeatLookup i).run w =
      (continuations orderedPosition repeatLookup i).run w := by
  by_cases hh : w.nodes[i]!.hadNormal = true
  · rcases hs hh with ⟨hp, hpos, hdelta, hloop⟩
    rw [machine_continuations_enter _ _ _ hh, continuations_enter _ _ _ _ hh,
      prepared_machine_exact _ _ _ hp]
    dsimp only
    have hv : ((prepared orderedPosition repeatLookup i).run w).1 =
        (observedNormal w.nodes[i]!, computedReference w i .current) := by
      rw [projection_refinement]
      cases repeatLookup <;> rfl
    rw [hv]
    have hd : machineMinus (computedReference w i .current) (observedNormal w.nodes[i]!) =
        referenceDelta w i := translation_machine_exact _ _ hpos hp.1 hdelta
    rw [hd]
    change (machineMoveChain (referenceDelta w i) _ _).run _ =
      (moveChain (referenceDelta w i) _ _).run _
    apply machine_indexed_refinement _ ids
    · rwa [prepared_nodes]
    · simpa only [LoopSafe, prepared_nodes] using hloop
  · dsimp [machineContinuations, continuations, normal, node, emit, StateT.run]
    simp [hh]

theorem complete_machine_continuations (repeatLookup : Bool) (i : Nat) (w : World)
    (ids : List Nat) (hg : Graph w.nodes i ids) (hs : ContinuationSafe w i ids) :
    let out := ((machineContinuations repeatLookup i).run w).2
    Applied (referenceDelta w i) (if w.nodes[i]!.hadNormal then ids else []) w out ∧
    out.nodes = continuationReference w i ids ∧ Graph out.nodes i ids := by
  rw [machine_continuations_exact _ _ _ _ hg.1 hs]
  exact ⟨actual_continuations _ _ _ _ hg.1,
    continuation_array_refinement _ _ _ _ hg.1,
    actual_continuations_preserve_graph _ _ _ _ hg⟩

def machineTranslation (repeatLookup : Bool) (i : Nat) : StateM World Point := do
  let first ← canonical i
  let p ← StickyLifecycle.compute machinePosition repeatLookup first .ignoreScroll
  let q ← normal first
  return machineMinus p q

def TranslationSafe (w : World) (i : Nat) : Prop :=
  let first := w.nodes[i]!.first
  ComputeSafe w first .ignoreScroll ∧ PointSafe (computedReference w first .ignoreScroll) ∧
    PointSafe (canonicalReference w i)

theorem machine_translation_exact (repeatLookup : Bool) (i : Nat) (w : World)
    (h : TranslationSafe w i) :
    (machineTranslation repeatLookup i).run w =
      (translation orderedPosition repeatLookup i).run w := by
  rw [projection_refinement]
  let pre := (canonical i).run w
  have hc := machine_compute_exact repeatLookup pre.1 .ignoreScroll pre.2 h.1
  change (let p := (StickyLifecycle.compute machinePosition repeatLookup pre.1 .ignoreScroll).run pre.2
          let q := (normal pre.1).run p.2
          (machineMinus p.1 q.1, q.2)) =
    (let p := (StickyLifecycle.compute referencePosition repeatLookup pre.1 .ignoreScroll).run pre.2
          let q := (normal pre.1).run p.2
          (minus p.1 q.1, q.2))
  rw [hc]
  dsimp only
  refine Prod.ext ?_ rfl
  have hv : ((StickyLifecycle.compute referencePosition repeatLookup pre.1 .ignoreScroll).run pre.2).1 =
      computedReference w w.nodes[i]!.first .ignoreScroll := by
    cases repeatLookup <;> rfl
  have hn : ((normal pre.1).run
      ((StickyLifecycle.compute referencePosition repeatLookup pre.1 .ignoreScroll).run pre.2).2).1 =
      observedNormal w.nodes[w.nodes[i]!.first]! := by
    cases repeatLookup <;> rfl
  dsimp only
  rw [hv, hn]
  exact translation_machine_exact _ _ h.2.1 h.1.1 h.2.2

def machineFrame (repeatLookup : Bool) (i : Nat) : StateM World Point := do
  let f ← node i
  if f.sticky then emit s!"container:{i}"
  if f.sticky && f.hasContainer then
    let q ← normal i
    let delta ← machineTranslation repeatLookup i
    return machinePlus q delta
  else
    emit s!"fallback:{i}"
    return f.fallback

def FrameSafe (w : World) (i : Nat) : Prop :=
  (w.nodes[i]!.sticky && w.nodes[i]!.hasContainer) = true →
    TranslationSafe w i ∧ PointSafe (observedNormal w.nodes[i]!) ∧
    PointSafe (plus (observedNormal w.nodes[i]!) (canonicalReference w i))

def framePrefix (i : Nat) : StateM World Point := do
  emit s!"container:{i}"
  normal i

theorem frame_machine_enter (repeatLookup : Bool) (i : Nat) (w : World)
    (hs : w.nodes[i]!.sticky = true) (hc : w.nodes[i]!.hasContainer = true) :
    (machineFrame repeatLookup i).run w =
      let q := (framePrefix i).run w
      let d := (machineTranslation repeatLookup i).run q.2
      (machinePlus q.1 d.1, d.2) := by
  dsimp [machineFrame, framePrefix, node, emit, StateT.run]
  simp [hs, hc]
  rfl

theorem frame_math_enter (repeatLookup : Bool) (i : Nat) (w : World)
    (hs : w.nodes[i]!.sticky = true) (hc : w.nodes[i]!.hasContainer = true) :
    (ignoringScrollAndSticky orderedPosition repeatLookup i).run w =
      let q := (framePrefix i).run w
      let d := (translation orderedPosition repeatLookup i).run q.2
      (plus q.1 d.1, d.2) := by
  dsimp [ignoringScrollAndSticky, framePrefix, node, emit, StateT.run]
  simp [hs, hc]
  rfl

theorem machine_frame_exact (repeatLookup : Bool) (i : Nat) (w : World)
    (h : FrameSafe w i) :
    (machineFrame repeatLookup i).run w =
      (ignoringScrollAndSticky orderedPosition repeatLookup i).run w := by
  by_cases hs : w.nodes[i]!.sticky = true
  · by_cases hc : w.nodes[i]!.hasContainer = true
    · rcases h (by simp [hs, hc]) with ⟨ht, hn, hp⟩
      rw [frame_machine_enter _ _ _ hs hc, frame_math_enter _ _ _ hs hc]
      dsimp only
      rw [machine_translation_exact repeatLookup i ((framePrefix i).run w).2 ht]
      refine Prod.ext ?_ rfl
      rw [actual_canonical_translation]
      exact addition_machine_exact _ _ hn ht.2.2 hp
    · dsimp [machineFrame, ignoringScrollAndSticky, node, emit, StateT.run]
      simp [hs, hc]
  · dsimp [machineFrame, ignoringScrollAndSticky, node, emit, StateT.run]
    simp [hs]

theorem complete_machine_frame (repeatLookup : Bool) (i : Nat) (w : World)
    (h : FrameSafe w i) :
    ((machineFrame repeatLookup i).run w).1 = frameReference w i := by
  rw [machine_frame_exact _ _ _ h]
  exact actual_frame_wrapper _ _ _

theorem complete_machine_translation (repeatLookup : Bool) (i : Nat) (w : World)
    (h : TranslationSafe w i) :
    ((machineTranslation repeatLookup i).run w).1 = canonicalReference w i := by
  rw [machine_translation_exact _ _ _ h]
  exact actual_canonical_translation _ _ _

end StickyMachineLifecycle
