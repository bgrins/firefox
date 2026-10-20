import StickyMachineLifecycle

namespace StickyUpdate
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle

def OverflowPath (nodes : Array Node) : Option Nat → List Nat → Prop
  | none, [] => True
  | some i, j :: rest => i = j ∧ i ≤ nodes.size ∧ i ∉ rest ∧
      OverflowPath nodes (if i = nodes.size then none else nodes[i]!.next) rest
  | _, _ => False

def overflowStep (root i : Nat) : StateM World (Option Nat) := do
  emit s!"overflow:{i}"
  if i == root then
    emit s!"next:{i}:-1"
    return none
  else next i

theorem overflow_step_nodes (root i : Nat) (w : World) :
    ((overflowStep root i).run w).2.nodes = w.nodes ∧
    ((overflowStep root i).run w).2.exhausted = w.exhausted ∧
    ((overflowStep root i).run w).1 = if i = root then none else w.nodes[i]!.next := by
  by_cases h : i = root
  all_goals
    dsimp [overflowStep, emit, next, node, StateT.run]
    simp [h]
    exact ⟨rfl, rfl, rfl⟩

theorem overflow_succ (root fuel i : Nat) (w : World) :
    (overflowChain root (fuel + 1) (some i)).run w =
      (overflowChain root fuel ((overflowStep root i).run w).1).run
        ((overflowStep root i).run w).2 := by
  by_cases h : i = root
  all_goals
    dsimp [overflowChain, overflowStep, emit, StateT.run]
    simp [h]
    rfl

theorem overflow_path_members (a : Array Node) (start : Option Nat) (ids : List Nat)
    (h : OverflowPath a start ids) : ids.Nodup ∧ ∀ j ∈ ids, j ≤ a.size := by
  induction ids generalizing start with
  | nil => simp
  | cons i rest ih =>
    cases start with
    | none => cases h
    | some k =>
      rcases h with ⟨he, hi, hn, ht⟩
      subst k
      rcases ih _ ht with ⟨hd, hb⟩
      constructor
      · simp [List.nodup_cons, hn, hd]
      · intro j hj
        rcases List.mem_cons.mp hj with rfl | hj
        · exact hi
        · exact hb j hj

theorem overflow_path_length (a : Array Node) (start : Option Nat) (ids : List Nat)
    (h : OverflowPath a start ids) : ids.length ≤ a.size + 1 := by
  rcases overflow_path_members a start ids h with ⟨hn, hb⟩
  have hs : ids ⊆ List.range (a.size + 1) := by
    intro j hj
    apply List.mem_range.mpr
    have h := hb j hj
    omega
  simpa using hn.length_le_of_subset hs

theorem overflow_complete (root fuel : Nat) (start : Option Nat) (ids : List Nat)
    (w : World) (hr : root = w.nodes.size) (hc : OverflowPath w.nodes start ids)
    (hf : ids.length ≤ fuel) :
    let out := ((overflowChain root fuel start).run w).2
    out.nodes = w.nodes ∧ out.exhausted = w.exhausted := by
  induction ids generalizing start fuel w with
  | nil =>
    cases start with
    | none => cases fuel <;> exact ⟨rfl, rfl⟩
    | some i => cases hc
  | cons i rest ih =>
    cases start with
    | none => cases hc
    | some k =>
      rcases hc with ⟨he, hi, hn, ht⟩
      subst k
      cases fuel with
      | zero => simp at hf
      | succ fuel =>
        rw [overflow_succ]
        have hs := overflow_step_nodes root i w
        have path : OverflowPath ((overflowStep root i).run w).2.nodes
            ((overflowStep root i).run w).1 rest := by
          rwa [hs.1, hs.2.2, hr]
        have stepResult := ih fuel ((overflowStep root i).run w).1
          ((overflowStep root i).run w).2 (by simpa [hs.1] using hr) path
          (by simpa using hf)
        exact ⟨stepResult.1.trans hs.1, stepResult.2.trans hs.2.1⟩

theorem overflow_source_fuel (start : Option Nat) (ids : List Nat)
    (w : World) (hc : OverflowPath w.nodes start ids) :
    let out := ((overflowChain w.nodes.size (w.nodes.size + 1) start).run w).2
    out.nodes = w.nodes ∧ out.exhausted = w.exhausted :=
  overflow_complete _ _ start ids w rfl hc (overflow_path_length _ _ _ hc)

def refreshed (reflow : Bool) (i : Nat) (nodes : Array Node) : Array Node :=
  if reflow then nodes.modify i fun n => {n with offsets := n.recomputed} else nodes

def refresh (reflow : Bool) (i : Nat) : StateM World Unit := do
  if reflow then
    emit s!"recompute:{i}"
    modify fun w => {w with nodes := refreshed true i w.nodes}

theorem refresh_nodes (reflow : Bool) (i : Nat) (w : World) :
    ((refresh reflow i).run w).2.nodes = refreshed reflow i w.nodes ∧
    ((refresh reflow i).run w).2.exhausted = w.exhausted := by
  cases reflow <;> exact ⟨rfl, rfl⟩

theorem refreshed_size (reflow : Bool) (i : Nat) (nodes : Array Node) :
    (refreshed reflow i nodes).size = nodes.size := by
  cases reflow <;> simp [refreshed]

theorem refreshed_links (reflow : Bool) (i j : Nat) (nodes : Array Node)
    (hj : j < nodes.size) :
    (refreshed reflow i nodes)[j]!.next = nodes[j]!.next ∧
    (refreshed reflow i nodes)[j]!.first = nodes[j]!.first ∧
    (refreshed reflow i nodes)[j]!.parent = nodes[j]!.parent := by
  cases reflow with
  | false => exact ⟨rfl, rfl, rfl⟩
  | true =>
    have hb : j < (refreshed true i nodes).size := by simpa [refreshed] using hj
    rw [getElem!_pos (refreshed true i nodes) j hb, getElem!_pos nodes j hj]
    simp only [refreshed, ite_true, Array.getElem_modify]
    split <;> exact ⟨rfl, rfl, rfl⟩

theorem refreshed_chain (reflow : Bool) (i : Nat) (nodes : Array Node)
    (hc : Chain nodes start ids) : Chain (refreshed reflow i nodes) start ids := by
  exact chain_transfer _ _ (refreshed_size _ _ _)
    (fun j hj => (refreshed_links reflow i j nodes hj).1) _ _ hc

def primary (project : Projection) (repeatLookup reflow : Bool)
    (root i : Nat) : StateM World Unit := do
  refresh reflow i
  continuations project repeatLookup i
  let parent := (← node i).parent
  let subtree := if reflow then some root else none
  if parent != subtree then overflowChain root (root + 1) parent

def primaryLoop (project : Projection) (repeatLookup reflow : Bool) (root : Nat) :
    List Nat → StateM World Unit
  | [] => pure ()
  | i :: rest => do
    primary project repeatLookup reflow root i
    primaryLoop project repeatLookup reflow root rest

def Linked (a b : Array Node) : Prop :=
  b.size = a.size ∧ ∀ j, j < a.size →
    b[j]!.next = a[j]!.next ∧ b[j]!.first = a[j]!.first ∧ b[j]!.parent = a[j]!.parent

theorem linked_refl (a : Array Node) : Linked a a := ⟨rfl, by simp⟩

theorem linked_trans (hab : Linked a b) (hbc : Linked b c) : Linked a c := by
  refine ⟨hbc.1.trans hab.1, ?_⟩
  intro j hj
  have h1 := hab.2 j hj
  have h2 := hbc.2 j (by rw [hab.1]; exact hj)
  exact ⟨h2.1.trans h1.1, h2.2.1.trans h1.2.1, h2.2.2.trans h1.2.2⟩

theorem refresh_linked (reflow : Bool) (i : Nat) (a : Array Node) :
    Linked a (refreshed reflow i a) :=
  ⟨refreshed_size _ _ _, fun j hj => refreshed_links _ _ _ _ hj⟩

theorem applied_linked (h : Applied d ids before after) : Linked before.nodes after.nodes := by
  refine ⟨h.1, ?_⟩
  intro j hj
  have r := applied_links h j hj
  exact ⟨r.1, r.2.1, r.2.2.1⟩

theorem linked_chain (h : Linked a b) (hc : Chain a start ids) : Chain b start ids :=
  chain_transfer a b h.1 (fun j hj => (h.2 j hj).1) start ids hc

theorem linked_overflow (h : Linked a b) (hc : OverflowPath a start ids) :
    OverflowPath b start ids := by
  induction ids generalizing start with
  | nil => cases start <;> exact hc
  | cons i rest ih =>
    cases start with
    | none => cases hc
    | some k =>
      rcases hc with ⟨he, hi, hn, ht⟩
      subst k
      refine ⟨rfl, by rw [h.1]; exact hi, hn, ?_⟩
      rw [h.1]
      by_cases hb : i = a.size
      · simp only [hb, ite_true] at ht ⊢
        exact ih ht
      · simp only [hb, ite_false] at ht ⊢
        rw [(h.2 i (by omega)).1]
        exact ih ht

def PrimaryReady (nodes : Array Node) (reflow : Bool) (i : Nat)
    (ids over : List Nat) : Prop :=
  i < nodes.size ∧ Chain nodes (some i) ids ∧
  (nodes[i]!.parent ≠ (if reflow then some nodes.size else none) →
    OverflowPath nodes nodes[i]!.parent over)

theorem ready_transfer (h : Linked a b) (hr : PrimaryReady a reflow i ids over) :
    PrimaryReady b reflow i ids over := by
  refine ⟨by rw [h.1]; exact hr.1, linked_chain h hr.2.1, ?_⟩
  rw [(h.2 i hr.1).2.2, h.1]
  intro he
  exact linked_overflow h (hr.2.2 he)

def primaryReference (nodes : Array Node) (reflow : Bool) (i : Nat)
    (ids : List Nat) : Array Node :=
  continuationReference ⟨refreshed reflow i nodes, #[], false⟩ i ids

def finishPrimary (reflow : Bool) (root i : Nat) : StateM World Unit := do
  let parent := (← node i).parent
  if parent != (if reflow then some root else none) then
    overflowChain root (root + 1) parent

theorem primary_decompose (project : Projection) (repeatLookup reflow : Bool)
    (root i : Nat) (w : World) :
    (primary project repeatLookup reflow root i).run w =
      (finishPrimary reflow root i).run
        ((continuations project repeatLookup i).run ((refresh reflow i).run w).2).2 := by
  rfl

theorem finish_primary (reflow : Bool) (i : Nat) (w : World) (over : List Nat)
    (hp : w.nodes[i]!.parent ≠ (if reflow then some w.nodes.size else none) →
      OverflowPath w.nodes w.nodes[i]!.parent over) :
    let out := ((finishPrimary reflow w.nodes.size i).run w).2
    out.nodes = w.nodes ∧ out.exhausted = w.exhausted := by
  by_cases h : w.nodes[i]!.parent = (if reflow then some w.nodes.size else none)
  · dsimp [finishPrimary, node, StateT.run]
    simp [h]
    exact ⟨rfl, rfl⟩
  · have r := overflow_source_fuel _ over w (hp h)
    dsimp [finishPrimary, node, StateT.run]
    simp [h]
    exact r

theorem actual_primary (repeatLookup reflow : Bool) (i : Nat) (w : World)
    (ids over : List Nat) (hr : PrimaryReady w.nodes reflow i ids over) :
    let out := ((primary orderedPosition repeatLookup reflow w.nodes.size i).run w).2
    out.nodes = primaryReference w.nodes reflow i ids ∧
    out.exhausted = w.exhausted ∧ Linked w.nodes out.nodes := by
  let a := ((refresh reflow i).run w).2
  let b := ((continuations orderedPosition repeatLookup i).run a).2
  have ha := refresh_nodes reflow i w
  have hla : Linked w.nodes a.nodes := by simpa only [a, ha.1] using refresh_linked reflow i w.nodes
  have hra := ready_transfer hla hr
  have hcont := actual_continuations repeatLookup i a ids hra.2.1
  have hlb := applied_linked hcont
  have hrb := ready_transfer hlb hra
  have hsize : b.nodes.size = w.nodes.size := hlb.1.trans hla.1
  have hf := finish_primary reflow i b over hrb.2.2
  rw [primary_decompose]
  change (((finishPrimary reflow w.nodes.size i).run b).2.nodes = _ ∧ _)
  rw [← hsize]
  refine ⟨hf.1.trans ?_, hf.2.trans (hcont.2.1.trans ha.2), ?_⟩
  · rw [applied_array hcont]
    change continuationReference a i ids = primaryReference w.nodes reflow i ids
    simp only [continuationReference, referenceDelta, primaryReference, a, ha.1]
  · rw [hf.1]
    exact linked_trans hla hlb

def updateReference (reflow : Bool) (chains : Nat → List Nat) :
    Array Node → List Nat → Array Node
  | nodes, [] => nodes
  | nodes, i :: rest => updateReference reflow chains
      (primaryReference nodes reflow i (chains i)) rest

def ReadyList (nodes : Array Node) (reflow : Bool) (chains overs : Nat → List Nat)
    (primaries : List Nat) : Prop :=
  ∀ i ∈ primaries, PrimaryReady nodes reflow i (chains i) (overs i)

theorem actual_primary_loop (repeatLookup reflow : Bool) (root : Nat)
    (primaries : List Nat) (w : World) (chains overs : Nat → List Nat)
    (hr : root = w.nodes.size) (hs : ReadyList w.nodes reflow chains overs primaries) :
    let out := ((primaryLoop orderedPosition repeatLookup reflow root primaries).run w).2
    out.nodes = updateReference reflow chains w.nodes primaries ∧
    out.exhausted = w.exhausted ∧ Linked w.nodes out.nodes := by
  induction primaries generalizing w with
  | nil => exact ⟨rfl, rfl, linked_refl _⟩
  | cons i rest ih =>
    have hs0 := hs i (List.mem_cons_self ..)
    have hp := actual_primary repeatLookup reflow i w (chains i) (overs i) hs0
    rw [← hr] at hp
    let mid := ((primary orderedPosition repeatLookup reflow root i).run w).2
    have hs' : ReadyList mid.nodes reflow chains overs rest := by
      intro j hj
      exact ready_transfer hp.2.2 (hs j (List.mem_cons_of_mem i hj))
    have hi := ih mid (hr.trans hp.2.2.1.symm) hs'
    change ((primaryLoop orderedPosition repeatLookup reflow root rest).run mid).2.nodes = _ ∧ _
    refine ⟨?_, hi.2.1.trans hp.2.1, linked_trans hp.2.2 hi.2.2⟩
    rw [hi.1, hp.1]
    rfl

def sourceFor (project : Projection) (repeatLookup reflow : Bool)
    (root : Nat) (primaries : List Nat) : StateM World Unit := do
  for i in primaries do primary project repeatLookup reflow root i

theorem for_loop_eq (project : Projection) (repeatLookup reflow : Bool)
    (root : Nat) (primaries : List Nat) :
    sourceFor project repeatLookup reflow root primaries =
      primaryLoop project repeatLookup reflow root primaries := by
  induction primaries with
  | nil => rfl
  | cons i rest ih =>
    simp only [sourceFor, List.forIn_cons, primaryLoop, bind_assoc, pure_bind] at *
    rw [← ih]

def updatePrefix (reflow : Bool) (primaries : List Nat) : StateM World Nat := do
  let root := (← get).nodes.size
  let subtree := if reflow then some root else none
  emit s!"subtree:{subtree.map Int.ofNat |>.getD (-1)}"
  emit (primaries.foldl (fun s i => s ++ ":" ++ toString i) "order")
  return root

theorem bind_conditional (p : Prop) [Decidable p] (a b : StateM World α)
    (f : α → StateM World β) :
    ((if p then a else b) >>= f) = if p then a >>= f else b >>= f := by
  split <;> rfl

theorem update_decompose (project : Projection) (repeatLookup reflow : Bool)
    (primaries : List Nat) (w : World) :
    (update project repeatLookup reflow primaries).run w =
      let pre := (updatePrefix reflow primaries).run w
      let body := (primaryLoop project repeatLookup reflow pre.1 primaries).run pre.2
      (emit "flush").run body.2 := by
  have h := for_loop_eq project repeatLookup reflow w.nodes.size primaries
  change (update project repeatLookup reflow primaries).run w =
    (emit "flush").run ((primaryLoop project repeatLookup reflow w.nodes.size primaries).run
      ((updatePrefix reflow primaries).run w).2).2
  rw [← h]
  simp only [update, sourceFor, primary, refresh, refreshed, updatePrefix,
    bind_assoc, bind_conditional, pure_bind]
  cases reflow <;> simp only [Bool.false_eq_true, ite_false, ite_true, bind_assoc,
    pure_bind, bind_conditional]
  all_goals rfl

theorem complete_update_reference (repeatLookup reflow : Bool)
    (primaries : List Nat) (w : World) (chains overs : Nat → List Nat)
    (hs : ReadyList w.nodes reflow chains overs primaries) :
    let out := ((update orderedPosition repeatLookup reflow primaries).run w).2
    out.nodes = updateReference reflow chains w.nodes primaries ∧
    out.exhausted = w.exhausted ∧ Linked w.nodes out.nodes := by
  rw [update_decompose]
  have hp := actual_primary_loop repeatLookup reflow w.nodes.size primaries
    ((updatePrefix reflow primaries).run w).2 chains overs rfl hs
  exact hp

def machinePrimary (repeatLookup reflow : Bool) (root i : Nat) : StateM World Unit := do
  refresh reflow i
  machineContinuations repeatLookup i
  finishPrimary reflow root i

def machinePrimaryLoop (repeatLookup reflow : Bool) (root : Nat) :
    List Nat → StateM World Unit
  | [] => pure ()
  | i :: rest => do
    machinePrimary repeatLookup reflow root i
    machinePrimaryLoop repeatLookup reflow root rest

def BatchSafe (reflow : Bool) (chains : Nat → List Nat) : Array Node → List Nat → Prop
  | _, [] => True
  | nodes, i :: rest =>
    ContinuationSafe ⟨refreshed reflow i nodes, #[], false⟩ i (chains i) ∧
    BatchSafe reflow chains (primaryReference nodes reflow i (chains i)) rest

theorem machine_primary_exact (repeatLookup reflow : Bool) (root i : Nat)
    (w : World) (ids : List Nat) (hc : Chain w.nodes (some i) ids)
    (hs : ContinuationSafe ⟨refreshed reflow i w.nodes, #[], false⟩ i ids) :
    (machinePrimary repeatLookup reflow root i).run w =
      (primary orderedPosition repeatLookup reflow root i).run w := by
  rw [primary_decompose]
  let a := ((refresh reflow i).run w).2
  have ha := (refresh_nodes reflow i w).1
  have hc' : Chain a.nodes (some i) ids := by
    rw [show a.nodes = refreshed reflow i w.nodes from ha]
    exact refreshed_chain reflow i w.nodes hc
  have hs' : ContinuationSafe a i ids := by
    simpa only [ContinuationSafe, ComputeSafe, computedReference, referenceDelta,
      LoopSafe, a, ha] using hs
  have he := machine_continuations_exact repeatLookup i a ids hc' hs'
  change (finishPrimary reflow root i).run ((machineContinuations repeatLookup i).run a).2 = _
  rw [he]

theorem machine_primary_loop_exact (repeatLookup reflow : Bool) (root : Nat)
    (primaries : List Nat) (w : World) (chains overs : Nat → List Nat)
    (hr : root = w.nodes.size) (hg : ReadyList w.nodes reflow chains overs primaries)
    (hs : BatchSafe reflow chains w.nodes primaries) :
    (machinePrimaryLoop repeatLookup reflow root primaries).run w =
      (primaryLoop orderedPosition repeatLookup reflow root primaries).run w := by
  induction primaries generalizing w with
  | nil => rfl
  | cons i rest ih =>
    have hgi := hg i (List.mem_cons_self ..)
    have hm := machine_primary_exact repeatLookup reflow root i w (chains i) hgi.2.1 hs.1
    change (machinePrimaryLoop repeatLookup reflow root rest).run
      ((machinePrimary repeatLookup reflow root i).run w).2 =
      (primaryLoop orderedPosition repeatLookup reflow root rest).run
      ((primary orderedPosition repeatLookup reflow root i).run w).2
    rw [hm]
    let mid := ((primary orderedPosition repeatLookup reflow root i).run w).2
    have hp := actual_primary repeatLookup reflow i w (chains i) (overs i) hgi
    rw [← hr] at hp
    apply ih mid
    · exact hr.trans hp.2.2.1.symm
    · intro j hj
      exact ready_transfer hp.2.2 (hg j (List.mem_cons_of_mem i hj))
    · rw [show mid.nodes = primaryReference w.nodes reflow i (chains i) from hp.1]
      exact hs.2

def machineUpdate (repeatLookup reflow : Bool) (primaries : List Nat) : StateM World Unit := do
  let root ← updatePrefix reflow primaries
  machinePrimaryLoop repeatLookup reflow root primaries
  emit "flush"

theorem machine_update_exact (repeatLookup reflow : Bool) (primaries : List Nat)
    (w : World) (chains overs : Nat → List Nat)
    (hg : ReadyList w.nodes reflow chains overs primaries)
    (hs : BatchSafe reflow chains w.nodes primaries) :
    (machineUpdate repeatLookup reflow primaries).run w =
      (update orderedPosition repeatLookup reflow primaries).run w := by
  rw [update_decompose]
  have he := machine_primary_loop_exact repeatLookup reflow w.nodes.size primaries
    ((updatePrefix reflow primaries).run w).2 chains overs rfl hg hs
  change (emit "flush").run
      ((machinePrimaryLoop repeatLookup reflow w.nodes.size primaries).run
        ((updatePrefix reflow primaries).run w).2).2 = _
  rw [he]
  rfl

theorem complete_machine_update (repeatLookup reflow : Bool) (primaries : List Nat)
    (w : World) (chains overs : Nat → List Nat)
    (hg : ReadyList w.nodes reflow chains overs primaries)
    (hs : BatchSafe reflow chains w.nodes primaries) :
    let out := ((machineUpdate repeatLookup reflow primaries).run w).2
    out.nodes = updateReference reflow chains w.nodes primaries ∧
    out.exhausted = w.exhausted ∧ Linked w.nodes out.nodes := by
  rw [machine_update_exact _ _ _ _ chains overs hg hs]
  exact complete_update_reference _ _ _ _ chains overs hg

end StickyUpdate
