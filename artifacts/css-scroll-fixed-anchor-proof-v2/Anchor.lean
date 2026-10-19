import Std

namespace Anchor

structure Obs where
  fixed : Bool
  sticky : Bool
  text : Bool
  continuation : Bool
  opted : Bool
  br : Bool
  chrome : Bool
  pseudo : Bool
  replaced : Bool
  inlineBox : Bool
  anon : Bool
  nested : Bool
  visible : Bool
  full : Bool
  deriving Repr, BEq, DecidableEq, Inhabited

inductive Decision where
  | exclude | pass | traverse | accept
  deriving Repr, BEq, DecidableEq, Inhabited

def early (repaired : Bool) (o : Obs) : Bool :=
  (o.text && o.continuation) || o.opted || o.sticky || (repaired && o.fixed) ||
  o.br || (o.chrome && !o.pseudo)

def descend (o : Obs) : Bool := !o.nested && !o.replaced

def classify (repaired : Bool) (o : Obs) : Decision :=
  if early repaired o then .exclude
  else if !o.text && ((o.inlineBox && !o.replaced) || o.anon) then
    if descend o then .pass else .exclude
  else if !o.visible then .exclude
  else if descend o && o.continuation then .pass
  else if o.full || !descend o then .accept
  else .traverse

theorem fixed_excluded (o : Obs) (h : o.fixed = true) :
    classify true o = .exclude := by simp [classify, early, h]

theorem sticky_excluded (r : Bool) (o : Obs) (h : o.sticky = true) :
    classify r o = .exclude := by simp [classify, early, h]

theorem nonfixed_classifier_preserved (o : Obs) (h : o.fixed = false) :
    classify true o = classify false o := by simp [classify, early, h]

theorem nonexcluded_safe (o : Obs) (h : classify true o ≠ .exclude) :
    o.fixed = false ∧ o.sticky = false := by
  constructor
  · cases hf : o.fixed
    · rfl
    · exact False.elim (h (fixed_excluded o hf))
  · cases hs : o.sticky
    · rfl
    · exact False.elim (h (sticky_excluded true o hs))

structure Pick where
  id : Nat
  obs : Obs
  deriving Repr, BEq, DecidableEq, Inhabited

inductive Plan where
  | nil
  | step (pick : Pick) (children rest : Plan)
  deriving Repr

def select (r : Bool) : Plan → Option Pick
  | .nil => none
  | .step p children rest =>
    match classify r p.obs with
    | .exclude => select r rest
    | .accept => some p
    | .pass => (select r children).orElse (fun _ => select r rest)
    | .traverse => (select r children).orElse (fun _ => some p)

def visits (r : Bool) : Plan → List Nat
  | .nil => []
  | .step p children rest =>
    p.id :: (match classify r p.obs with
    | .exclude => visits r rest
    | .accept => []
    | .pass => visits r children ++
        (if (select r children).isSome then [] else visits r rest)
    | .traverse => visits r children)

def allNonfixed : Plan → Prop
  | .nil => True
  | .step p children rest => p.obs.fixed = false ∧ allNonfixed children ∧ allNonfixed rest

theorem selected_safe (tree : Plan) (p : Pick) (h : select true tree = some p) :
    p.obs.fixed = false ∧ p.obs.sticky = false := by
  induction tree with
  | nil => simp [select] at h
  | step q children rest childIH restIH =>
    cases hd : classify true q.obs with
    | exclude => exact restIH (by simpa [select, hd] using h)
    | accept =>
      have eq : q = p := by simpa [select, hd] using h
      subst p
      exact nonexcluded_safe q.obs (by simp [hd])
    | pass =>
      cases hc : select true children with
      | none => exact restIH (by simpa [select, hd, hc] using h)
      | some v =>
        have eq : v = p := by simpa [select, hd, hc] using h
        subst p
        exact childIH hc
    | traverse =>
      cases hc : select true children with
      | none =>
        have eq : q = p := by simpa [select, hd, hc] using h
        subst p
        exact nonexcluded_safe q.obs (by simp [hd])
      | some v =>
        have eq : v = p := by simpa [select, hd, hc] using h
        subst p
        exact childIH hc

theorem nofixed_selection_preserved (tree : Plan) (h : allNonfixed tree) :
    select true tree = select false tree := by
  induction tree with
  | nil => rfl
  | step p children rest childIH restIH =>
    rcases h with ⟨hp, hc, hr⟩
    simp only [select, nonfixed_classifier_preserved p.obs hp, childIH hc, restIH hr]

theorem nofixed_visits_preserved (tree : Plan) (h : allNonfixed tree) :
    visits true tree = visits false tree := by
  induction tree with
  | nil => rfl
  | step p children rest childIH restIH =>
    rcases h with ⟨hp, hc, hr⟩
    simp only [visits, nonfixed_classifier_preserved p.obs hp,
      nofixed_selection_preserved children hc, childIH hc, restIH hr]

theorem exclude_selection_barrier (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .exclude) :
    select r (.step p children rest) = select r rest := by simp [select, h]

theorem exclude_visit_barrier (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .exclude) :
    visits r (.step p children rest) = p.id :: visits r rest := by simp [visits, h]

theorem accept_first (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .accept) :
    select r (.step p children rest) = some p := by simp [select, h]

theorem accept_stops (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .accept) :
    visits r (.step p children rest) = [p.id] := by simp [visits, h]

theorem pass_empty_skips (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .pass) (hc : select r children = none) :
    select r (.step p children rest) = select r rest := by simp [select, h, hc]

theorem traverse_empty_falls_back (r : Bool) (p : Pick) (children rest : Plan)
    (h : classify r p.obs = .traverse) (hc : select r children = none) :
    select r (.step p children rest) = some p := by simp [select, h, hc]

theorem descend_prefers_child (r : Bool) (p q : Pick) (children rest : Plan)
    (h : classify r p.obs = .pass ∨ classify r p.obs = .traverse)
    (hc : select r children = some q) :
    select r (.step p children rest) = some q := by
  rcases h with h | h <;> simp [select, h, hc]

def containsId (id : Nat) : Plan → Prop
  | .nil => False
  | .step p children rest => id = p.id ∨ containsId id children ∨ containsId id rest

theorem selected_occurs (r : Bool) (tree : Plan) (p : Pick)
    (h : select r tree = some p) : containsId p.id tree := by
  induction tree with
  | nil => simp [select] at h
  | step q children rest childIH restIH =>
    simp only [containsId]
    cases hd : classify r q.obs with
    | exclude => exact Or.inr (Or.inr (restIH (by simpa [select, hd] using h)))
    | accept =>
      have eq : q = p := by simpa [select, hd] using h
      exact Or.inl (congrArg Pick.id eq.symm)
    | pass =>
      cases hc : select r children with
      | none => exact Or.inr (Or.inr (restIH (by simpa [select, hd, hc] using h)))
      | some v =>
        have eq : v = p := by simpa [select, hd, hc] using h
        subst p
        exact Or.inr (Or.inl (childIH hc))
    | traverse =>
      cases hc : select r children with
      | none =>
        have eq : q = p := by simpa [select, hd, hc] using h
        exact Or.inl (congrArg Pick.id eq.symm)
      | some v =>
        have eq : v = p := by simpa [select, hd, hc] using h
        subst p
        exact Or.inr (Or.inl (childIH hc))

theorem excluded_no_alternate_route (r : Bool) (p : Pick) (children rest : Plan)
    (id : Nat) (h : classify r p.obs = .exclude) (hr : ¬containsId id rest) :
    ∀ q, select r (.step p children rest) = some q → q.id ≠ id := by
  intro q hq eq
  have hs : select r rest = some q := by simpa [select, h] using hq
  exact hr (eq ▸ selected_occurs r rest q hs)

structure Gates where
  enabled : Bool
  disabled : Bool
  opted : Bool
  origin : Bool
  perspective : Bool
  deriving Repr

def maintain (g : Gates) : Bool := g.enabled && !g.disabled && !g.opted && !g.origin && !g.perspective

def publicSelect (g : Gates) (r : Bool) (tree : Plan) : Option Pick :=
  if maintain g then select r tree else none

theorem cannot_maintain_selects_none (g : Gates) (r : Bool) (tree : Plan)
    (h : maintain g = false) : publicSelect g r tree = none := by simp [publicSelect, h]

theorem public_selection_safe (g : Gates) (tree : Plan) (p : Pick)
    (h : publicSelect g true tree = some p) : p.obs.fixed = false ∧ p.obs.sticky = false := by
  unfold publicSelect at h
  split at h
  · exact selected_safe tree p h
  · simp at h

theorem public_nonfixed_preserved (g : Gates) (tree : Plan) (h : allNonfixed tree) :
    publicSelect g true tree = publicSelect g false tree := by
  simp [publicSelect, nofixed_selection_preserved tree h]

def flagTransitions (old new : Option Nat) : List (Nat × Bool) :=
  if old = new then [] else old.toList.map (·, false) ++ new.toList.map (·, true)

theorem unchanged_anchor_flags (old : Option Nat) : flagTransitions old old = [] := by
  simp [flagTransitions]

theorem cleared_anchor_flags (old : Nat) : flagTransitions (some old) none = [(old, false)] := by
  simp [flagTransitions]

theorem new_anchor_flags (new : Nat) : flagTransitions none (some new) = [(new, true)] := by
  simp [flagTransitions]

theorem changed_anchor_flags (old new : Nat) (h : old ≠ new) :
    flagTransitions (some old) (some new) = [(old, false), (new, true)] := by
  simp [flagTransitions, h]

inductive Kind where
  | principal | absolute | float | overflowFloats | fixed | other
  deriving Repr, BEq, DecidableEq, Inhabited

def ordinary (k : Kind) : Bool :=
  k != .absolute && k != .float && k != .overflowFloats

def firstPass (lists : List (Kind × List Nat)) : List Nat :=
  (lists.filter (fun item => ordinary item.1)).flatMap (·.2)

def absolutePass (lists : List (Kind × List Nat)) : List Nat :=
  ((lists.find? (fun item => item.1 == .absolute)).map (·.2)).getD []

def scheduled (lists : List (Kind × List Nat)) : List Nat :=
  firstPass lists ++ absolutePass lists

theorem skipped_absolute_first (ids : List Nat) (rest : List (Kind × List Nat)) :
    firstPass ((.absolute, ids) :: rest) = firstPass rest := by rfl

theorem skipped_float_first (ids : List Nat) (rest : List (Kind × List Nat)) :
    firstPass ((.float, ids) :: rest) = firstPass rest := by rfl

theorem skipped_overflow_float_first (ids : List Nat) (rest : List (Kind × List Nat)) :
    firstPass ((.overflowFloats, ids) :: rest) = firstPass rest := by rfl

theorem retained_principal_order (ids : List Nat) (rest : List (Kind × List Nat)) :
    firstPass ((.principal, ids) :: rest) = ids ++ firstPass rest := by rfl

theorem retained_fixed_list (ids : List Nat) (rest : List (Kind × List Nat)) :
    firstPass ((.fixed, ids) :: rest) = ids ++ firstPass rest := by rfl

theorem absolute_pass_present (ids : List Nat) (rest : List (Kind × List Nat)) :
    absolutePass ((.absolute, ids) :: rest) = ids := by rfl

theorem absolute_after_ordinary (lists : List (Kind × List Nat)) :
    scheduled lists = firstPass lists ++ absolutePass lists := rfl

structure Node where
  obs : Obs
  lists : List (Kind × List Nat)
  target : Option Nat
  within : Bool
  deriving Repr, Inhabited

abbrev Graph := Nat → Node

def resolveSlot (g : Graph) (id : Nat) : Option Nat :=
  match (g id).target with
  | none => some id
  | some real => if (g real).within then some real else none

theorem ordinary_slot (g : Graph) (id : Nat) (h : (g id).target = none) :
    resolveSlot g id = some id := by simp [resolveSlot, h]

theorem external_placeholder_rejected (g : Graph) (id real : Nat)
    (h : (g id).target = some real) (ho : (g real).within = false) :
    resolveSlot g id = none := by simp [resolveSlot, h, ho]

theorem local_placeholder_resolved (g : Graph) (id real : Nat)
    (h : (g id).target = some real) (hi : (g real).within = true) :
    resolveSlot g id = some real := by simp [resolveSlot, h, hi]

def successors (g : Graph) (id : Nat) : List Nat :=
  (scheduled (g id).lists).filterMap (resolveSlot g)

def unfoldGraph (g : Graph) : Nat → List Nat → Plan
  | 0, _ => .nil
  | fuel + 1, ids => ids.foldr
      (fun id rest => .step ⟨id, (g id).obs⟩ (unfoldGraph g fuel (successors g id)) rest) .nil

theorem unfolded_nonfixed (g : Graph) (h : ∀ id, (g id).obs.fixed = false)
    (fuel : Nat) (ids : List Nat) : allNonfixed (unfoldGraph g fuel ids) := by
  induction fuel generalizing ids with
  | zero => trivial
  | succ fuel ih =>
    induction ids with
    | nil => trivial
    | cons id rest restIH =>
      exact ⟨h id, ih _, restIH⟩

theorem graph_selected_safe (g : Graph) (fuel : Nat) (ids : List Nat) (p : Pick)
    (h : select true (unfoldGraph g fuel ids) = some p) :
    p.obs.fixed = false ∧ p.obs.sticky = false := selected_safe _ p h

theorem graph_nonfixed_preserved (g : Graph) (h : ∀ id, (g id).obs.fixed = false)
    (fuel : Nat) (ids : List Nat) :
    select true (unfoldGraph g fuel ids) = select false (unfoldGraph g fuel ids) :=
  nofixed_selection_preserved _ (unfolded_nonfixed g h fuel ids)

def WellRanked (g : Graph) (rank : Nat → Nat) : Prop :=
  ∀ parent child, child ∈ successors g parent → rank child < rank parent

theorem descent_rank_decreases (g : Graph) (rank : Nat → Nat) (h : WellRanked g rank)
    (parent child : Nat) (hc : child ∈ successors g parent) : rank child < rank parent :=
  h parent child hc

theorem unfold_stable_with_rank (g : Graph) (rank : Nat → Nat) (h : WellRanked g rank)
    (fuel : Nat) (ids : List Nat) (bound : ∀ id ∈ ids, rank id < fuel) :
    unfoldGraph g (fuel + 1) ids = unfoldGraph g fuel ids := by
  induction fuel generalizing ids with
  | zero =>
    have empty : ids = [] := by
      apply List.eq_nil_iff_forall_not_mem.mpr
      intro id hi
      exact Nat.not_lt_zero _ (bound id hi)
    subst ids
    rfl
  | succ fuel ih =>
    induction ids with
    | nil => rfl
    | cons id rest restIH =>
      have childBound : ∀ child ∈ successors g id, rank child < fuel := by
        intro child hc
        have hp := bound id (by simp)
        exact Nat.lt_of_lt_of_le (h id child hc) (Nat.le_of_lt_succ hp)
      have hr : ∀ child ∈ rest, rank child < fuel + 1 := by
        intro child hc
        exact bound child (by simp [hc])
      change Plan.step ⟨id, (g id).obs⟩ (unfoldGraph g (fuel + 1) (successors g id))
        (unfoldGraph g (fuel + 1 + 1) rest) =
        Plan.step ⟨id, (g id).obs⟩ (unfoldGraph g fuel (successors g id))
        (unfoldGraph g (fuel + 1) rest)
      rw [ih _ childBound, restIH hr]

def setChain (ids : List Nat) (value : Bool) (flags : Nat → Bool) : Nat → Bool :=
  fun id => if id ∈ ids then value else flags id

theorem set_chain_member (ids : List Nat) (value : Bool) (flags : Nat → Bool)
    (id : Nat) (h : id ∈ ids) : setChain ids value flags id = value := by simp [setChain, h]

theorem set_chain_outside (ids : List Nat) (value : Bool) (flags : Nat → Bool)
    (id : Nat) (h : id ∉ ids) : setChain ids value flags id = flags id := by simp [setChain, h]

theorem new_chain_wins (old new : List Nat) (flags : Nat → Bool) (id : Nat)
    (h : id ∈ new) : setChain new true (setChain old false flags) id = true := by
  simp [setChain, h]

theorem old_only_chain_cleared (old new : List Nat) (flags : Nat → Bool) (id : Nat)
    (ho : id ∈ old) (hn : id ∉ new) : setChain new true (setChain old false flags) id = false := by
  simp [setChain, ho, hn]

theorem flags_outside_both_unchanged (old new : List Nat) (flags : Nat → Bool) (id : Nat)
    (ho : id ∉ old) (hn : id ∉ new) : setChain new true (setChain old false flags) id = flags id := by
  simp [setChain, ho, hn]

structure SelectionState where
  selected : Option Nat
  offset : Int
  dirty : Bool
  suboptimal : Bool
  deriving Repr

def selectionState (selected : Option Nat) (offset : Nat → Int) (dirtyChildren : Nat → Bool) : SelectionState :=
  ⟨selected, (selected.map offset).getD 0, false, (selected.map dirtyChildren).getD false⟩

theorem state_selection_recorded (selected : Option Nat) (offset : Nat → Int) (dirtyChildren : Nat → Bool) :
    (selectionState selected offset dirtyChildren).selected = selected := rfl

theorem state_selection_clean (selected : Option Nat) (offset : Nat → Int) (dirtyChildren : Nat → Bool) :
    (selectionState selected offset dirtyChildren).dirty = false := rfl

theorem no_anchor_zero_offset (offset : Nat → Int) (dirtyChildren : Nat → Bool) :
    (selectionState none offset dirtyChildren).offset = 0 := rfl

theorem anchor_provider_offset (id : Nat) (offset : Nat → Int) (dirtyChildren : Nat → Bool) :
    (selectionState (some id) offset dirtyChildren).offset = offset id := rfl

theorem anchor_suboptimal_observation (id : Nat) (offset : Nat → Int) (dirtyChildren : Nat → Bool) :
    (selectionState (some id) offset dirtyChildren).suboptimal = dirtyChildren id := rfl

end Anchor
