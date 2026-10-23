import Hidden

namespace Subtree

inductive Tree where
  | node (id : Nat) (dirty hasDirtyChildren tableColumnGroup : Bool) (children : List Tree)
  deriving Repr

def dirty : Tree → Bool
  | .node _ d _ _ _ => d

def eligible : Tree → Bool
  | .node _ d h _ _ => d || h

mutual
  def allDirty : Tree → Bool
    | .node _ d _ _ cs => d && allDirtyList cs
  def allDirtyList : List Tree → Bool
    | [] => true
    | t :: ts => allDirty t && allDirtyList ts
end

def markDesc : Tree → Tree
  | .node id d h table cs =>
      if d || table then .node id d h table cs
      else .node id true h table (cs.map markDesc)

def markRoot : Tree → Tree
  | .node id d h table cs =>
      if d then .node id d h table cs
      else .node id true h table (cs.map markDesc)

mutual
  def barrierClosure : Tree → Bool
    | .node id d h table cs =>
      if d || table then allDirty (.node id d h table cs)
      else barrierClosures cs
  def barrierClosures : List Tree → Bool
    | [] => true
    | t :: ts => barrierClosure t && barrierClosures ts
end

def rootClosure : Tree → Bool
  | .node id d h table cs =>
      if d then allDirty (.node id d h table cs)
      else barrierClosures cs


def locate : List Nat → Tree → Option Tree
  | [], t => some t
  | n :: path, .node _ _ _ _ cs => cs[n]?.bind (locate path)

def eligibleAt (path : List Nat) (t : Tree) : Bool :=
  (locate path t).any eligible

def clearPath : List Nat → Tree → Bool
  | [], .node _ d _ table _ => d || !table
  | n :: path, .node _ d _ table cs =>
      !d && !table && (cs[n]?.any (clearPath path))

def clearRootPath : List Nat → Tree → Bool
  | [], _ => true
  | n :: path, .node _ d _ _ cs => !d && (cs[n]?.any (clearPath path))

def needsForce (hiddenAncestor : Bool) (t : Tree) : Bool :=
  eligible t && hiddenAncestor

structure World where
  ownDirty : Bool
  principal : List Tree
  otherLists : List Tree
  externalOutOfFlow : List Tree
  nextContinuation : List Tree
  deriving Repr

def markPrincipal (w : World) : World :=
  {w with principal := w.principal.map markRoot}

theorem treeInduction (P : Tree → Prop)
    (step : ∀ id d h table cs, (∀ t ∈ cs, P t) → P (.node id d h table cs)) :
    ∀ t, P t :=
  Tree.rec (motive_1 := P) (motive_2 := fun cs => ∀ t ∈ cs, P t)
    step (by simp) (by intro t ts ht hts x hx; simp only [List.mem_cons] at hx; rcases hx with rfl | hx; exact ht; exact hts x hx)

theorem root_is_dirty (t : Tree) : dirty (markRoot t) = true := by
  cases t with | node id d h table cs => cases d <;> simp [markRoot, dirty]

theorem root_is_eligible (t : Tree) : eligible (markRoot t) = true := by
  cases t with | node id d h table cs => cases d <;> simp [markRoot, eligible]

theorem dirty_root_unchanged (id : Nat) (h table : Bool) (cs : List Tree) :
    markRoot (.node id true h table cs) = .node id true h table cs := by simp [markRoot]

theorem dirty_descendant_unchanged (id : Nat) (h table : Bool) (cs : List Tree) :
    markDesc (.node id true h table cs) = .node id true h table cs := by simp [markDesc]

theorem table_descendant_unchanged (id : Nat) (d h : Bool) (cs : List Tree) :
    markDesc (.node id d h true cs) = .node id d h true cs := by simp [markDesc]

theorem has_dirty_children_does_not_block (id : Nat) (table : Bool) (cs : List Tree) :
    markRoot (.node id false true table cs) = .node id true true table (cs.map markDesc) := by simp [markRoot]

theorem root_idempotent (t : Tree) : markRoot (markRoot t) = markRoot t := by
  cases t with | node id d h table cs => cases d <;> simp [markRoot]

theorem descendant_idempotent (t : Tree) : markDesc (markDesc t) = markDesc t := by
  cases t with | node id d h table cs => cases d <;> cases table <;> simp [markDesc]

theorem allDirtyList_map (cs : List Tree)
    (ih : ∀ t ∈ cs, allDirty (markDesc t) = barrierClosure t) :
    allDirtyList (cs.map markDesc) = barrierClosures cs := by
  induction cs with
  | nil => rfl
  | cons t ts rest =>
    simp only [List.map_cons, allDirtyList, barrierClosures]
    rw [ih t (by simp), rest (by intro u hu; exact ih u (by simp [hu]))]

theorem descendant_coverage_exact (t : Tree) :
    allDirty (markDesc t) = barrierClosure t := by
  induction t using treeInduction with
  | step id d h table cs ih =>
    cases d <;> cases table <;> simp [markDesc, barrierClosure, allDirty, allDirtyList_map cs ih]

theorem root_coverage_exact (t : Tree) : allDirty (markRoot t) = rootClosure t := by
  cases t with
  | node id d h table cs =>
    cases d <;> simp [markRoot, rootClosure, allDirty, allDirtyList_map cs (by intro t ht; exact descendant_coverage_exact t)]

theorem sufficient_barrier_closure (t : Tree) (hc : rootClosure t = true) :
    allDirty (markRoot t) = true := by rw [root_coverage_exact, hc]

theorem no_hidden_ancestor_no_forcing (t : Tree) : needsForce false t = false := by simp [needsForce]

theorem marked_root_with_hidden_ancestor_forces (t : Tree) :
    needsForce true (markRoot t) = true := by simp [needsForce, root_is_eligible]

theorem principal_preserves_container (w : World) :
    (markPrincipal w).ownDirty = w.ownDirty := rfl

theorem principal_preserves_other_lists (w : World) :
    (markPrincipal w).otherLists = w.otherLists := rfl

theorem principal_preserves_external_oof (w : World) :
    (markPrincipal w).externalOutOfFlow = w.externalOutOfFlow := rfl

theorem principal_preserves_other_continuations (w : World) :
    (markPrincipal w).nextContinuation = w.nextContinuation := rfl

def leaf : Tree := .node 2 false false false []
def dirtyBarrier : Tree := .node 1 true false false [leaf]

theorem already_dirty_root_clean_leaf : eligibleAt [0] (markRoot dirtyBarrier) = false := by simp [eligibleAt, locate, markRoot, dirtyBarrier, leaf, eligible]

theorem already_dirty_descendant_clean_leaf :
    eligibleAt [0, 0] (markRoot (.node 0 false false false [dirtyBarrier])) = false := by simp [eligibleAt, locate, markRoot, markDesc, dirtyBarrier, leaf, eligible]

theorem table_barrier_clean_leaf :
    eligibleAt [0, 0] (markRoot (.node 0 false false false [.node 1 false false true [leaf]])) = false := by simp [eligibleAt, locate, markRoot, markDesc, leaf, eligible]

theorem clean_ordinary_leaf_marked :
    eligibleAt [0, 0] (markRoot (.node 0 false false false [.node 1 false false false [leaf]])) = true := by simp [eligibleAt, locate, markRoot, markDesc, leaf, eligible]

theorem dirty_children_flag_allows_leaf_marking :
    eligibleAt [0] (markRoot (.node 0 false true false [leaf])) = true := by simp [eligibleAt, locate, markRoot, markDesc, leaf, eligible]

theorem principal_table_root_is_marked :
    eligibleAt [] (markRoot (.node 0 false false true [])) = true := by simp [eligibleAt, locate, markRoot, eligible]

theorem clear_descendant_path_marks (path : List Nat) (t : Tree)
    (clear : clearPath path t = true) : eligibleAt path (markDesc t) = true := by
  induction path generalizing t with
  | nil =>
    cases t with
    | node id d h table cs =>
      cases d <;> cases table <;> simp_all [clearPath, eligibleAt, locate, markDesc, eligible]
  | cons n path ih =>
    cases t with
    | node id d h table cs =>
      cases d <;> cases table <;> simp only [clearPath, Bool.not_false, Bool.not_true,
        Bool.false_and, Bool.true_and, Bool.false_eq_true] at clear
      cases hc : cs[n]? with
      | none => simp [hc] at clear
      | some child =>
        have childClear : clearPath path child = true := by simpa [hc] using clear
        simpa [eligibleAt, locate, markDesc, List.getElem?_map, hc] using ih child childClear

theorem clear_root_path_marks (path : List Nat) (t : Tree)
    (clear : clearRootPath path t = true) : eligibleAt path (markRoot t) = true := by
  cases path with
  | nil => simpa [eligibleAt, locate] using root_is_eligible t
  | cons n path =>
    cases t with
    | node id d h table cs =>
      cases d <;> simp only [clearRootPath, Bool.not_false, Bool.not_true,
        Bool.false_and, Bool.true_and, Bool.false_eq_true] at clear
      cases hc : cs[n]? with
      | none => simp [hc] at clear
      | some child =>
        have childClear : clearPath path child = true := by simpa [hc] using clear
        simpa [eligibleAt, locate, markRoot, List.getElem?_map, hc] using clear_descendant_path_marks path child childClear

theorem descendant_preserves_eligible_path (path : List Nat) (t : Tree)
    (before : eligibleAt path t = true) : eligibleAt path (markDesc t) = true := by
  induction path generalizing t with
  | nil =>
    cases t with
    | node id d h table cs =>
      cases d <;> cases table <;> simp_all [eligibleAt, locate, markDesc, eligible]
  | cons n path ih =>
    cases t with
    | node id d h table cs =>
      cases d <;> cases table <;> simp only [markDesc, Bool.false_or, Bool.true_or,
        Bool.false_eq_true, ite_false, ite_true]
      · cases hc : cs[n]? with
        | none => simp [eligibleAt, locate, hc] at before
        | some child =>
          have childBefore : eligibleAt path child = true := by simpa [eligibleAt, locate, hc] using before
          simpa [eligibleAt, locate, List.getElem?_map, hc] using ih child childBefore
      all_goals exact before

theorem root_preserves_eligible_path (path : List Nat) (t : Tree)
    (before : eligibleAt path t = true) : eligibleAt path (markRoot t) = true := by
  cases path with
  | nil => simpa [eligibleAt, locate] using root_is_eligible t
  | cons n path =>
    cases t with
    | node id d h table cs =>
      cases d <;> simp only [markRoot, Bool.false_eq_true, ite_false, ite_true]
      · cases hc : cs[n]? with
        | none => simp [eligibleAt, locate, hc] at before
        | some child =>
          have childBefore : eligibleAt path child = true := by simpa [eligibleAt, locate, hc] using before
          simpa [eligibleAt, locate, List.getElem?_map, hc] using descendant_preserves_eligible_path path child childBefore
      · exact before

theorem selected_query_recovery (path : List Nat) (t target : Tree)
    (frame : Hidden.Frame) (layout : Hidden.Key → Hidden.Size) (key : Hidden.Key)
    (clear : clearRootPath path t = true)
    (found : locate path (markRoot t) = some target) :
    (Hidden.geometryQuery true layout key {frame with dirty := eligible target}).geometry = layout key := by
  have ready := clear_root_path_marks path t clear
  have targetReady : eligible target = true := by simpa [eligibleAt, found] using ready
  exact Hidden.dirty_query_uses_actual_provider layout key _ targetReady

theorem selected_query_completion (path : List Nat) (t target : Tree)
    (frame : Hidden.Frame) (layout : Hidden.Key → Hidden.Size) (key : Hidden.Key)
    (clear : clearRootPath path t = true)
    (found : locate path (markRoot t) = some target) :
    (Hidden.geometryQuery true layout key {frame with dirty := eligible target}).dirty = false := by
  have ready := clear_root_path_marks path t clear
  have targetReady : eligible target = true := by simpa [eligibleAt, found] using ready
  exact Hidden.dirty_query_completes_clean layout key _ targetReady

def forceAll : Tree → Tree
  | .node id _ h table cs => .node id true h table (cs.map forceAll)

theorem allDirtyList_force (cs : List Tree)
    (ih : ∀ t ∈ cs, allDirty (forceAll t) = true) :
    allDirtyList (cs.map forceAll) = true := by
  induction cs with
  | nil => rfl
  | cons t ts rest =>
    simp only [List.map_cons, allDirtyList]
    rw [ih t (by simp), rest (by intro u hu; exact ih u (by simp [hu]))]
    rfl

theorem producer_marks_every_bit (t : Tree) : allDirty (forceAll t) = true := by
  induction t using treeInduction with
  | step id d h table cs ih => simp [forceAll, allDirty, allDirtyList_force cs ih]

theorem all_dirty_satisfies_root_closure (t : Tree) (all : allDirty t = true) :
    rootClosure t = true := by
  cases t with
  | node id d h table cs =>
    cases d <;> simp_all [allDirty, rootClosure]

theorem producer_establishes_barrier_closure (t : Tree) : rootClosure (forceAll t) = true :=
  all_dirty_satisfies_root_closure (forceAll t) (producer_marks_every_bit t)

theorem helper_preserves_producer_coverage (t : Tree) :
    allDirty (markRoot (forceAll t)) = true :=
  sufficient_barrier_closure (forceAll t) (producer_establishes_barrier_closure t)


end Subtree
