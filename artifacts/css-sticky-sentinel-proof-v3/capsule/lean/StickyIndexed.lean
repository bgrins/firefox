import StickyLifecycle

namespace StickyIndexed
open MaskedSticky StickyComposition StickyLifecycle

def shifted (delta : Point) (n : Node) : Node :=
  {n with current := plus (observedNormal n) delta}

def step (delta : Point) (i : Nat) : StateM World (Option Nat) := do
  let n ← normal i
  setPosition i (plus n delta)
  next i

theorem modify_same (a : Array Node) (i : Nat)
    (h : (shifted d a[i]!).current = a[i]!.current) :
    a.modify i (shifted d) = a := by
  apply Array.ext
  · simp
  · intro j hj hk
    rw [Array.getElem_modify]
    split
    · next he =>
        subst j
        have hi : i < a.size := by simpa using hj
        have he : plus (observedNormal a[i]) d = a[i].current := by
          simpa [shifted, getElem!_pos a i hi] using h
        simp [shifted, he]
    · rfl

theorem step_nodes (d : Point) (i : Nat) (w : World) :
    ((step d i).run w).2.nodes = w.nodes.modify i (shifted d) := by
  by_cases hn : w.nodes[i]!.hadNormal = true <;>
    by_cases hp : plus (observedNormal w.nodes[i]!) d = w.nodes[i]!.current
  all_goals
    dsimp [step, normal, node, emit, setPosition, next, StateT.run]
    simp [observedNormal, hn] at hp
    simp [hn, hp]
    dsimp [Functor.map, Bind.bind, Pure.pure, modify, MonadState.modifyGet, MonadStateOf.modifyGet, StateT.bind, StateT.pure, StateT.modifyGet]
  all_goals
    apply Array.ext
    · simp
    · intro j hj hk
      simp only [Array.getElem_modify]
      split
      · next hji =>
          subst j
          have hi : i < w.nodes.size := by simpa using hk
          simp only [getElem!_pos w.nodes i hi] at *
          generalize he : w.nodes[i] = n at *
          cases n
          simp_all [shifted, observedNormal]
      · rfl

theorem step_exhausted (d : Point) (i : Nat) (w : World) :
    ((step d i).run w).2.exhausted = w.exhausted := by
  by_cases hn : w.nodes[i]!.hadNormal = true <;>
    by_cases hp : plus (observedNormal w.nodes[i]!) d = w.nodes[i]!.current
  all_goals
    dsimp [step, normal, node, emit, setPosition, next, StateT.run]
    simp [observedNormal, hn] at hp
    simp [hn, hp]
    dsimp [Functor.map, Bind.bind, Pure.pure, modify, MonadState.modifyGet, MonadStateOf.modifyGet, StateT.bind, StateT.pure, StateT.modifyGet]
    all_goals rfl

theorem step_next (d : Point) (i : Nat) (w : World) (hi : i < w.nodes.size) :
    ((step d i).run w).1 = w.nodes[i]!.next := by
  by_cases hn : w.nodes[i]!.hadNormal = true <;>
    by_cases hp : plus (observedNormal w.nodes[i]!) d = w.nodes[i]!.current
  all_goals
    dsimp [step, normal, node, emit, setPosition, next, StateT.run]
    simp [observedNormal, hn] at hp
    simp [hn, hp]
    dsimp [Functor.map, Bind.bind, Pure.pure, modify, MonadState.modifyGet, MonadStateOf.modifyGet, StateT.bind, StateT.pure, StateT.modifyGet]
    all_goals simp [getElem!_pos, hi, Array.getElem_modify_self]

theorem move_succ (d : Point) (fuel i : Nat) (w : World) :
    ((moveChain d (fuel + 1) (some i)).run w) =
      (moveChain d fuel ((step d i).run w).1).run ((step d i).run w).2 := by
  rfl

def Chain (nodes : Array Node) : Option Nat → List Nat → Prop
  | none, [] => True
  | some i, j :: rest =>
      i = j ∧ i < nodes.size ∧ i ∉ rest ∧ Chain nodes nodes[i]!.next rest
  | _, _ => False

theorem chain_members (a : Array Node) (start : Option Nat) (ids : List Nat)
    (h : Chain a start ids) : ids.Nodup ∧ ∀ j ∈ ids, j < a.size := by
  induction ids generalizing start with
  | nil => simp
  | cons i rest ih =>
    cases start with
    | none => cases h
    | some k =>
      rcases h with ⟨rfl, hi, hn, ht⟩
      rcases ih _ ht with ⟨hd, hb⟩
      constructor
      · simp [List.nodup_cons, hn, hd]
      · intro j hj
        rcases List.mem_cons.mp hj with rfl | hj
        · exact hi
        · exact hb j hj

theorem chain_length (a : Array Node) (start : Option Nat) (ids : List Nat)
    (h : Chain a start ids) : ids.length ≤ a.size := by
  rcases chain_members a start ids h with ⟨hn, hb⟩
  have hs : ids ⊆ List.range a.size := by
    intro j hj
    exact List.mem_range.mpr (hb j hj)
  simpa using hn.length_le_of_subset hs

theorem chain_transfer (a b : Array Node) (hs : b.size = a.size)
    (hn : ∀ j, j < a.size → b[j]!.next = a[j]!.next)
    (start : Option Nat) (ids : List Nat) (h : Chain a start ids) :
    Chain b start ids := by
  induction ids generalizing start with
  | nil => cases start <;> exact h
  | cons i rest ih =>
    cases start with
    | none => cases h
    | some k =>
      rcases h with ⟨hki, hi, hu, ht⟩
      subst k
      refine ⟨rfl, by omega, hu, ?_⟩
      rw [hn i hi]
      exact ih _ ht

theorem modified_node (a : Array Node) (i j : Nat) (hj : j < a.size) :
    (a.modify i (shifted d))[j]! = if i = j then shifted d a[j]! else a[j]! := by
  have hb : j < (a.modify i (shifted d)).size := by simpa
  simp only [getElem!_pos (a.modify i (shifted d)) j hb, getElem!_pos a j hj, Array.getElem_modify]

theorem step_chain (d : Point) (i : Nat) (w : World) (start : Option Nat)
    (ids : List Nat) (h : Chain w.nodes start ids) :
    Chain ((step d i).run w).2.nodes start ids := by
  apply chain_transfer w.nodes _ (by rw [step_nodes]; simp) _ start ids h
  intro j hj
  rw [step_nodes, modified_node _ _ _ hj]
  split <;> rfl

theorem indexed_common_translation (d : Point) (ids : List Nat)
    (start : Option Nat) (fuel : Nat) (w : World)
    (hc : Chain w.nodes start ids) (hf : ids.length ≤ fuel) :
    let out := ((moveChain d fuel start).run w).2
    out.nodes.size = w.nodes.size ∧ out.exhausted = w.exhausted ∧
    ∀ j, j < w.nodes.size → out.nodes[j]! =
      if j ∈ ids then shifted d w.nodes[j]! else w.nodes[j]! := by
  induction ids generalizing start fuel w with
  | nil =>
    cases start with
    | none =>
      cases fuel <;> exact ⟨rfl, rfl, by intro j hj; rfl⟩
    | some i => cases hc
  | cons i rest ih =>
    cases start with
    | none => cases hc
    | some k =>
      rcases hc with ⟨hki, hi, hni, ht⟩
      subst k
      cases fuel with
      | zero => simp at hf
      | succ fuel =>
        rw [move_succ]
        let mid := ((step d i).run w).2
        have hn := step_next d i w hi
        have hm : mid.nodes.size = w.nodes.size := by dsimp [mid]; rw [step_nodes]; simp
        have hs : Chain mid.nodes ((step d i).run w).1 rest := by
          rw [hn]
          exact step_chain d i w _ rest ht
        have hf' : rest.length ≤ fuel := by simpa using hf
        rcases ih _ _ mid hs hf' with ⟨hz, he, hr⟩
        refine ⟨hz.trans hm, he.trans (step_exhausted d i w), ?_⟩
        intro j hj
        rw [hr j (by omega)]
        have heq : mid.nodes[j]! = if i = j then shifted d w.nodes[j]! else w.nodes[j]! := by
          dsimp [mid]; rw [step_nodes]; exact modified_node _ _ _ hj
        rw [heq]
        by_cases hij : i = j
        · subst j
          simp [hni]
        · simp [hij, List.mem_cons, Ne.symm hij]

theorem source_fuel_sufficient (d : Point) (ids : List Nat) (start : Option Nat)
    (w : World) (hc : Chain w.nodes start ids) :
    let out := ((moveChain d (w.nodes.size + 1) start).run w).2
    out.nodes.size = w.nodes.size ∧ out.exhausted = w.exhausted ∧
    ∀ j, j < w.nodes.size → out.nodes[j]! =
      if j ∈ ids then shifted d w.nodes[j]! else w.nodes[j]! := by
  apply indexed_common_translation d ids start _ w hc
  have h := chain_length w.nodes start ids hc
  omega

def Applied (d : Point) (ids : List Nat) (before after : World) : Prop :=
  after.nodes.size = before.nodes.size ∧ after.exhausted = before.exhausted ∧
  ∀ j, j < before.nodes.size → after.nodes[j]! =
    if j ∈ ids then shifted d before.nodes[j]! else before.nodes[j]!

def Graph (nodes : Array Node) (first : Nat) (ids : List Nat) : Prop :=
  Chain nodes (some first) ids ∧
  ∀ j ∈ ids, nodes[j]!.first = first ∧ nodes[j]!.parent = nodes[first]!.parent

theorem applied_links (h : Applied d ids before after) (j : Nat)
    (hj : j < before.nodes.size) :
    after.nodes[j]!.next = before.nodes[j]!.next ∧
    after.nodes[j]!.first = before.nodes[j]!.first ∧
    after.nodes[j]!.parent = before.nodes[j]!.parent ∧
    after.nodes[j]!.hadNormal = before.nodes[j]!.hadNormal ∧
    after.nodes[j]!.normal = before.nodes[j]!.normal ∧
    after.nodes[j]!.offsets = before.nodes[j]!.offsets := by
  rw [h.2.2 j hj]
  split <;> simp [shifted]

theorem applied_chain (h : Applied d ids before after)
    (hc : Chain before.nodes start chain) : Chain after.nodes start chain := by
  exact chain_transfer _ _ h.1 (fun j hj => (applied_links h j hj).1) _ _ hc

theorem chain_head_mem (h : Chain a (some i) ids) : i ∈ ids := by
  cases ids with
  | nil => cases h
  | cons j rest =>
    rcases h with ⟨rfl, _⟩
    exact List.mem_cons_self

theorem applied_graph (h : Applied d visited before after)
    (hg : Graph before.nodes first ids) : Graph after.nodes first ids := by
  refine ⟨applied_chain h hg.1, ?_⟩
  have bounds := (chain_members _ _ _ hg.1).2
  have hf := bounds first (chain_head_mem hg.1)
  intro j hj
  have fields := applied_links h j (bounds j hj)
  have firstFields := applied_links h first hf
  exact ⟨fields.2.1.trans (hg.2 j hj).1,
    fields.2.2.1.trans ((hg.2 j hj).2.trans firstFields.2.2.1.symm)⟩

def prepared (project : Projection) (repeatLookup : Bool) (i : Nat) :
    StateM World (Point × Point) := do
  let q ← normal i
  let p ← StickyLifecycle.compute project repeatLookup i .current
  return (q, p)

def referenceDelta (w : World) (i : Nat) : Point :=
  let n := w.nodes[i]!
  let g := providedGeometry n .current
  minus (referencePosition n.offsets (observedNormal n) g.stick g.contain)
    (observedNormal n)

theorem prepared_nodes (project : Projection) (repeatLookup : Bool)
    (i : Nat) (w : World) :
    ((prepared project repeatLookup i).run w).2.nodes = w.nodes := by
  cases repeatLookup <;> rfl

theorem prepared_exhausted (project : Projection) (repeatLookup : Bool)
    (i : Nat) (w : World) :
    ((prepared project repeatLookup i).run w).2.exhausted = w.exhausted := by
  cases repeatLookup <;> rfl

theorem prepared_delta (repeatLookup : Bool) (i : Nat) (w : World) :
    minus ((prepared orderedPosition repeatLookup i).run w).1.2
      ((prepared orderedPosition repeatLookup i).run w).1.1 = referenceDelta w i := by
  rw [projection_refinement]
  cases repeatLookup <;> rfl

theorem continuations_enter (project : Projection) (repeatLookup : Bool)
    (i : Nat) (w : World) (h : w.nodes[i]!.hadNormal = true) :
    ((continuations project repeatLookup i).run w) =
      let p := (prepared project repeatLookup i).run w
      (moveChain (minus p.1.2 p.1.1) (w.nodes.size + 1) (some i)).run p.2 := by
  dsimp [continuations, prepared, normal, node, emit, StateT.run]
  simp [h]
  cases repeatLookup <;> rfl

theorem continuations_no_normal (project : Projection) (repeatLookup : Bool)
    (i : Nat) (w : World) (h : w.nodes[i]!.hadNormal = false) :
    Applied ⟨0, 0⟩ [] w ((continuations project repeatLookup i).run w).2 := by
  dsimp [continuations, normal, node, emit, StateT.run]
  simp [h]
  exact ⟨rfl, rfl, by intro j hj; rfl⟩

theorem actual_continuations (repeatLookup : Bool) (i : Nat) (w : World)
    (ids : List Nat) (hc : Chain w.nodes (some i) ids) :
    Applied (referenceDelta w i) (if w.nodes[i]!.hadNormal then ids else [])
      w ((continuations orderedPosition repeatLookup i).run w).2 := by
  by_cases h : w.nodes[i]!.hadNormal = true
  · simp only [h, ite_true]
    rw [continuations_enter _ _ _ _ h]
    dsimp only
    rw [prepared_delta]
    have hp := prepared_nodes orderedPosition repeatLookup i w
    have he := prepared_exhausted orderedPosition repeatLookup i w
    have hl := chain_length w.nodes (some i) ids hc
    have hc' : Chain ((prepared orderedPosition repeatLookup i).run w).2.nodes
        (some i) ids := by rwa [hp]
    have result := indexed_common_translation (referenceDelta w i) ids (some i)
      (w.nodes.size + 1) ((prepared orderedPosition repeatLookup i).run w).2 hc' (by omega)
    simpa only [Applied, hp, he] using result
  · have hf : w.nodes[i]!.hadNormal = false := by simpa using h
    simp only [hf, Bool.false_eq_true, ite_false]
    have r := continuations_no_normal orderedPosition repeatLookup i w hf
    simpa [Applied] using r

theorem actual_continuations_preserve_graph (repeatLookup : Bool) (i : Nat)
    (w : World) (ids : List Nat) (hg : Graph w.nodes i ids) :
    Graph ((continuations orderedPosition repeatLookup i).run w).2.nodes i ids := by
  exact applied_graph (actual_continuations repeatLookup i w ids hg.1) hg

def referenceNodes (d : Point) (ids : List Nat) (nodes : Array Node) : Array Node :=
  nodes.mapIdx fun i n => if i ∈ ids then shifted d n else n

theorem applied_array (h : Applied d ids before after) :
    after.nodes = referenceNodes d ids before.nodes := by
  apply Array.ext
  · simpa [referenceNodes] using h.1
  · intro j hj hk
    have hb : j < before.nodes.size := by simpa [referenceNodes] using hk
    have ha := h.2.2 j hb
    simpa only [getElem!_pos after.nodes j hj, getElem!_pos before.nodes j hb,
      referenceNodes, Array.getElem_mapIdx] using ha

def continuationReference (w : World) (i : Nat) (ids : List Nat) : Array Node :=
  referenceNodes (referenceDelta w i) (if w.nodes[i]!.hadNormal then ids else []) w.nodes

theorem continuation_array_refinement (repeatLookup : Bool) (i : Nat)
    (w : World) (ids : List Nat) (hc : Chain w.nodes (some i) ids) :
    ((continuations orderedPosition repeatLookup i).run w).2.nodes =
      continuationReference w i ids :=
  applied_array (actual_continuations repeatLookup i w ids hc)

def canonicalReference (w : World) (i : Nat) : Point :=
  let first := w.nodes[w.nodes[i]!.first]!
  let geometry := providedGeometry first .ignoreScroll
  minus (referencePosition first.offsets (observedNormal first)
    geometry.stick geometry.contain) (observedNormal first)

theorem actual_canonical_translation (repeatLookup : Bool) (i : Nat) (w : World) :
    ((translation orderedPosition repeatLookup i).run w).1 = canonicalReference w i := by
  rw [translation_value, projection_refinement]
  rfl

theorem canonical_member_independence (repeatLookup : Bool) (a b : Nat) (w : World)
    (h : w.nodes[a]!.first = w.nodes[b]!.first) :
    ((translation orderedPosition repeatLookup a).run w).1 =
      ((translation orderedPosition repeatLookup b).run w).1 := by
  rw [actual_canonical_translation, actual_canonical_translation]
  simp only [canonicalReference, h]

def frameReference (w : World) (i : Nat) : Point :=
  let f := w.nodes[i]!
  if f.sticky && f.hasContainer then plus (observedNormal f) (canonicalReference w i)
  else f.fallback

theorem actual_frame_wrapper (repeatLookup : Bool) (i : Nat) (w : World) :
    ((ignoringScrollAndSticky orderedPosition repeatLookup i).run w).1 =
      frameReference w i := by
  rw [projection_refinement]
  cases hs : w.nodes[i]!.sticky <;> cases hc : w.nodes[i]!.hasContainer
  all_goals
    dsimp [ignoringScrollAndSticky, normal, translation, canonical, node, emit,
      frameReference, canonicalReference, observedNormal, StateT.run]
    simp [hs, hc]
    cases repeatLookup <;> rfl

theorem continuation_relative_displacement (repeatLookup : Bool) (i : Nat)
    (w : World) (ids : List Nat) (hc : Chain w.nodes (some i) ids)
    (hn : w.nodes[i]!.hadNormal = true) (a b : Nat) (ha : a ∈ ids) (hb : b ∈ ids) :
    let out := ((continuations orderedPosition repeatLookup i).run w).2
    minus out.nodes[a]!.current out.nodes[b]!.current =
      minus (observedNormal w.nodes[a]!) (observedNormal w.nodes[b]!) := by
  have r := actual_continuations repeatLookup i w ids hc
  have bounds := (chain_members _ _ _ hc).2
  dsimp only
  rw [r.2.2 a (bounds a ha), r.2.2 b (bounds b hb)]
  simp only [hn, ite_true, ha, hb, shifted, minus, plus, Point.mk.injEq]
  omega

end StickyIndexed
