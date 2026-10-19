import Anchor

namespace Traversal
open Anchor

inductive Pass where
  | first | absolute
  deriving Repr, BEq, DecidableEq

inductive Event where
  | enter (frame : Nat)
  | list (frame : Nat) (pass : Pass) (kind : Kind)
  | skip (frame : Nat) (kind : Kind)
  | resolve (slot target : Nat) (accepted : Bool)
  | decision (frame : Nat) (result : Decision)
  | descend (frame : Nat)
  | fallback (frame : Nat)
  | returned (source selected : Nat)
  | finish (frame : Nat) (selected : Option Nat) (exhausted : Bool)
  | final (selected : Option Nat)
  | exhausted (frame : Nat)
  deriving Repr, BEq, DecidableEq

structure Outcome where
  selected : Option Pick := none
  trace : List Event := []
  exhausted : Bool := false
  deriving Repr, BEq, DecidableEq

def prepend (events : List Event) (out : Outcome) : Outcome :=
  { out with trace := events ++ out.trace }

def finished (frame : Nat) (out : Outcome) : Outcome :=
  { out with trace := .enter frame :: out.trace ++
      [.finish frame (out.selected.map Pick.id) out.exhausted] }

def resolved (g : Graph) (slot : Nat) : Nat := (g slot).target.getD slot

def eligible (g : Graph) (slot : Nat) : Bool :=
  let real := resolved g slot
  real == slot || (g real).within

def resolution (g : Graph) (slot : Nat) : Event :=
  .resolve slot (resolved g slot) (eligible g slot)

inductive Program where
  | nil
  | exhausted (frame : Nat)
  | emit (event : Event) (rest : Program)
  | choice (first rest : Program)
  | frame (id : Nat) (body : Program)
  | candidate (pick : Pick) (children rest : Program)
  deriving Repr

def interpret (r : Bool) : Program → Outcome
  | .nil => {}
  | .exhausted id => ⟨none, [.exhausted id], true⟩
  | .emit event rest => prepend [event] (interpret r rest)
  | .choice first rest =>
    let out := interpret r first
    if out.exhausted || out.selected.isSome then out
    else prepend out.trace (interpret r rest)
  | .frame id body => finished id (interpret r body)
  | .candidate p children rest =>
    let d := classify r p.obs
    prepend [.decision p.id d] <|
      match d with
      | .exclude => interpret r rest
      | .accept => ⟨some p, [.returned p.id p.id], false⟩
      | .pass =>
        let out := interpret r children
        prepend [.descend p.id] <|
          if out.exhausted then out
          else match out.selected with
          | some q => { out with trace := out.trace ++ [.returned p.id q.id] }
          | none => prepend out.trace (interpret r rest)
      | .traverse =>
        let out := interpret r children
        prepend [.descend p.id] <|
          if out.exhausted then out
          else match out.selected with
          | some q => { out with trace := out.trace ++ [.returned p.id q.id] }
          | none => ⟨some p, out.trace ++ [.fallback p.id, .returned p.id p.id], false⟩

def compileSlots (g : Graph) (children : Nat → Program) : List Nat → Program
  | [] => .nil
  | slot :: rest =>
    .emit (resolution g slot) <|
      if eligible g slot then
        let id := resolved g slot
        .candidate ⟨id, (g id).obs⟩ (children id) (compileSlots g children rest)
      else compileSlots g children rest

def compileFirst (g : Graph) (children : Nat → Program) (parent : Nat) :
    List (Kind × List Nat) → Program
  | [] => .nil
  | (kind, ids) :: rest =>
    if ordinary kind then
      .choice (.emit (.list parent .first kind) (compileSlots g children ids))
        (compileFirst g children parent rest)
    else .emit (.skip parent kind) (compileFirst g children parent rest)

def compileBody (g : Graph) (children : Nat → Program) (parent : Nat) : Program :=
  .choice (compileFirst g children parent (g parent).lists)
    (.emit (.list parent .absolute .absolute)
      (compileSlots g children (absolutePass (g parent).lists)))

def compileFrame (g : Graph) : Nat → Nat → Program
  | 0, parent => .frame parent (.exhausted parent)
  | fuel + 1, parent => .frame parent (compileBody g (compileFrame g fuel) parent)

def nativeSlots (r : Bool) (g : Graph) (children : Nat → Outcome) : List Nat → Outcome
  | [] => {}
  | slot :: rest =>
    let id := resolved g slot
    let event := resolution g slot
    if !eligible g slot then prepend [event] (nativeSlots r g children rest)
    else
      let d := classify r (g id).obs
      match d with
      | .exclude => prepend [event, .decision id d] (nativeSlots r g children rest)
      | .accept => ⟨some ⟨id, (g id).obs⟩, [event, .decision id d, .returned id id], false⟩
      | .pass =>
        let child := children id
        if child.exhausted then prepend [event, .decision id d, .descend id] child
        else match child.selected with
        | none => prepend ([event, .decision id d, .descend id] ++ child.trace)
                    (nativeSlots r g children rest)
        | some q => ⟨some q, [event, .decision id d, .descend id] ++ child.trace ++
                      [.returned id q.id], false⟩
      | .traverse =>
        let child := children id
        if child.exhausted then prepend [event, .decision id d, .descend id] child
        else match child.selected with
        | none => ⟨some ⟨id, (g id).obs⟩,
                    [event, .decision id d, .descend id] ++ child.trace ++
                    [.fallback id, .returned id id], false⟩
        | some q => ⟨some q, [event, .decision id d, .descend id] ++ child.trace ++
                      [.returned id q.id], false⟩

def nativeFirst (r : Bool) (g : Graph) (children : Nat → Outcome) (parent : Nat) :
    List (Kind × List Nat) → Outcome
  | [] => {}
  | (kind, ids) :: rest =>
    if ordinary kind then
      let out := nativeSlots r g children ids
      if out.exhausted || out.selected.isSome then prepend [.list parent .first kind] out
      else prepend (.list parent .first kind :: out.trace) (nativeFirst r g children parent rest)
    else prepend [.skip parent kind] (nativeFirst r g children parent rest)

def nativeBody (r : Bool) (g : Graph) (children : Nat → Outcome) (parent : Nat) : Outcome :=
  let first := nativeFirst r g children parent (g parent).lists
  if first.exhausted || first.selected.isSome then first
  else prepend (first.trace ++ [.list parent .absolute .absolute])
    (nativeSlots r g children (absolutePass (g parent).lists))

def nativeFrame (r : Bool) (g : Graph) : Nat → Nat → Outcome
  | 0, parent => finished parent ⟨none, [.exhausted parent], true⟩
  | fuel + 1, parent => finished parent (nativeBody r g (nativeFrame r g fuel) parent)

theorem slots_agree (r : Bool) (g : Graph) (program : Nat → Program)
    (native : Nat → Outcome) (h : ∀ id, interpret r (program id) = native id)
    (ids : List Nat) : interpret r (compileSlots g program ids) = nativeSlots r g native ids := by
  induction ids with
  | nil => rfl
  | cons slot rest ih =>
    cases he : eligible g slot <;> simp only [compileSlots, he, Bool.false_eq_true,
      ↓reduceIte, interpret, nativeSlots, Bool.not_false, Bool.not_true, Bool.true_eq,
      ih]
    cases hd : classify r (g (resolved g slot)).obs <;>
      simp only [hd, prepend, h, ih]
    all_goals first
      | rfl
      | cases hc : native (resolved g slot) with
        | mk selected trace exhausted =>
          cases exhausted <;> cases selected <;>
            simp [prepend, List.append_assoc]

theorem first_agree (r : Bool) (g : Graph) (program : Nat → Program)
    (native : Nat → Outcome) (h : ∀ id, interpret r (program id) = native id)
    (parent : Nat) (lists : List (Kind × List Nat)) :
    interpret r (compileFirst g program parent lists) = nativeFirst r g native parent lists := by
  induction lists with
  | nil => rfl
  | cons item rest ih =>
    rcases item with ⟨kind, ids⟩
    cases hk : ordinary kind <;>
      simp [compileFirst, nativeFirst, hk, interpret, slots_agree r g program native h,
        ih, prepend, List.append_assoc]

theorem body_agree (r : Bool) (g : Graph) (program : Nat → Program)
    (native : Nat → Outcome) (h : ∀ id, interpret r (program id) = native id)
    (parent : Nat) : interpret r (compileBody g program parent) = nativeBody r g native parent := by
  simp only [compileBody, interpret, first_agree r g program native h,
    slots_agree r g program native h, nativeBody]
  split <;> simp [prepend, List.append_assoc]

theorem traversal_agreement (r : Bool) (g : Graph) (fuel parent : Nat) :
    interpret r (compileFrame g fuel parent) = nativeFrame r g fuel parent := by
  induction fuel generalizing parent with
  | zero => rfl
  | succ fuel ih => simp [compileFrame, nativeFrame, interpret, body_agree r g _ _ ih]

def SlotProperty (g : Graph) (ids : List Nat) (property : Nat → Prop) : Prop :=
  ∀ slot ∈ ids, eligible g slot = true → property (resolved g slot)

def FirstProperty (g : Graph) (lists : List (Kind × List Nat))
    (property : Nat → Prop) : Prop :=
  ∀ kind ids, (kind, ids) ∈ lists → ordinary kind = true → SlotProperty g ids property

structure Ranked (g : Graph) (rank : Nat → Nat) : Prop where
  first : ∀ parent, FirstProperty g (g parent).lists (fun child => rank child < rank parent)
  absolute : ∀ parent, SlotProperty g (absolutePass (g parent).lists)
    (fun child => rank child < rank parent)

theorem slots_congr (g : Graph) (left right : Nat → Program) (ids : List Nat)
    (h : SlotProperty g ids (fun id => left id = right id)) :
    compileSlots g left ids = compileSlots g right ids := by
  induction ids with
  | nil => rfl
  | cons slot rest ih =>
    have hr : SlotProperty g rest (fun id => left id = right id) := by
      intro id hi he
      exact h id (by simp [hi]) he
    cases he : eligible g slot <;> simp [compileSlots, he, ih hr]
    exact h slot (by simp) he

theorem first_congr (g : Graph) (left right : Nat → Program) (parent : Nat)
    (lists : List (Kind × List Nat))
    (h : FirstProperty g lists (fun id => left id = right id)) :
    compileFirst g left parent lists = compileFirst g right parent lists := by
  induction lists with
  | nil => rfl
  | cons item rest ih =>
    rcases item with ⟨kind, ids⟩
    have hr : FirstProperty g rest (fun id => left id = right id) := by
      intro k xs hm hk
      exact h k xs (by simp [hm]) hk
    cases hk : ordinary kind <;> simp [compileFirst, hk, ih hr]
    exact slots_congr g left right ids (h kind ids (by simp) hk)

theorem body_congr (g : Graph) (left right : Nat → Program) (parent : Nat)
    (hf : FirstProperty g (g parent).lists (fun id => left id = right id))
    (ha : SlotProperty g (absolutePass (g parent).lists) (fun id => left id = right id)) :
    compileBody g left parent = compileBody g right parent := by
  simp [compileBody, first_congr g left right parent _ hf, slots_congr g left right _ ha]

theorem ranked_program_stable (g : Graph) (rank : Nat → Nat) (h : Ranked g rank)
    (fuel parent : Nat) (bound : rank parent < fuel) :
    compileFrame g (fuel + 1) parent = compileFrame g fuel parent := by
  induction fuel generalizing parent with
  | zero => omega
  | succ fuel ih =>
    simp only [compileFrame]
    congr 1
    apply body_congr
    · intro kind ids hm hk slot hs he
      apply ih
      exact Nat.lt_of_lt_of_le (h.first parent kind ids hm hk slot hs he)
        (Nat.le_of_lt_succ bound)
    · intro slot hs he
      apply ih
      exact Nat.lt_of_lt_of_le (h.absolute parent slot hs he)
        (Nat.le_of_lt_succ bound)

theorem ranked_program_stable_add (g : Graph) (rank : Nat → Nat) (h : Ranked g rank)
    (fuel parent extra : Nat) (bound : rank parent < fuel) :
    compileFrame g (fuel + extra) parent = compileFrame g fuel parent := by
  induction extra with
  | zero => rfl
  | succ extra ih =>
    rw [Nat.add_succ, ranked_program_stable g rank h (fuel + extra) parent (by omega), ih]

def NoExhaustion : Program → Prop
  | .nil => True
  | .exhausted _ => False
  | .emit _ rest => NoExhaustion rest
  | .choice first rest => NoExhaustion first ∧ NoExhaustion rest
  | .frame _ body => NoExhaustion body
  | .candidate _ children rest => NoExhaustion children ∧ NoExhaustion rest

theorem interpret_not_exhausted (r : Bool) (program : Program) (h : NoExhaustion program) :
    (interpret r program).exhausted = false := by
  induction program with
  | nil => rfl
  | exhausted id => exact False.elim h
  | emit event rest ih => exact ih h
  | frame id body ih => exact ih h
  | choice first rest firstIH restIH =>
    rcases h with ⟨hf, hr⟩
    cases hs : (interpret r first).selected <;>
      simp [interpret, firstIH hf, restIH hr, prepend, hs]
  | candidate p children rest childIH restIH =>
    rcases h with ⟨hc, hr⟩
    cases hd : classify r p.obs <;> simp [interpret, hd, childIH hc, restIH hr, prepend]
    all_goals cases hs : (interpret r children).selected <;> simp [hs, childIH hc, restIH hr, prepend]

theorem slots_no_exhaustion (g : Graph) (children : Nat → Program) (ids : List Nat)
    (h : SlotProperty g ids (fun id => NoExhaustion (children id))) :
    NoExhaustion (compileSlots g children ids) := by
  induction ids with
  | nil => trivial
  | cons slot rest ih =>
    have hr : SlotProperty g rest (fun id => NoExhaustion (children id)) := by
      intro id hi he
      exact h id (by simp [hi]) he
    cases he : eligible g slot <;> simp [compileSlots, he, NoExhaustion, ih hr]
    exact h slot (by simp) he

theorem first_no_exhaustion (g : Graph) (children : Nat → Program) (parent : Nat)
    (lists : List (Kind × List Nat))
    (h : FirstProperty g lists (fun id => NoExhaustion (children id))) :
    NoExhaustion (compileFirst g children parent lists) := by
  induction lists with
  | nil => trivial
  | cons item rest ih =>
    rcases item with ⟨kind, ids⟩
    have hr : FirstProperty g rest (fun id => NoExhaustion (children id)) := by
      intro k xs hm hk
      exact h k xs (by simp [hm]) hk
    cases hk : ordinary kind <;> simp [compileFirst, hk, NoExhaustion, ih hr]
    exact slots_no_exhaustion g children ids (h kind ids (by simp) hk)

theorem ranked_no_exhaustion (g : Graph) (rank : Nat → Nat) (h : Ranked g rank)
    (fuel parent : Nat) (bound : rank parent < fuel) : NoExhaustion (compileFrame g fuel parent) := by
  induction fuel generalizing parent with
  | zero => omega
  | succ fuel ih =>
    simp only [compileFrame, NoExhaustion, compileBody]
    constructor
    · apply first_no_exhaustion
      intro kind ids hm hk slot hs he
      apply ih
      exact Nat.lt_of_lt_of_le (h.first parent kind ids hm hk slot hs he)
        (Nat.le_of_lt_succ bound)
    · apply slots_no_exhaustion
      intro slot hs he
      apply ih
      exact Nat.lt_of_lt_of_le (h.absolute parent slot hs he)
        (Nat.le_of_lt_succ bound)

theorem ranked_native_not_exhausted (r : Bool) (g : Graph) (rank : Nat → Nat)
    (h : Ranked g rank) (fuel parent : Nat) (bound : rank parent < fuel) :
    (nativeFrame r g fuel parent).exhausted = false := by
  rw [← traversal_agreement]
  exact interpret_not_exhausted r _ (ranked_no_exhaustion g rank h fuel parent bound)

theorem ranked_native_stable (r : Bool) (g : Graph) (rank : Nat → Nat)
    (h : Ranked g rank) (fuel parent extra : Nat) (bound : rank parent < fuel) :
    nativeFrame r g (fuel + extra) parent = nativeFrame r g fuel parent := by
  rw [← traversal_agreement, ← traversal_agreement,
      ranked_program_stable_add g rank h fuel parent extra bound]

theorem ranked_complete_refinement (r : Bool) (g : Graph) (rank : Nat → Nat)
    (h : Ranked g rank) (parent : Nat) :
    interpret r (compileFrame g (rank parent + 1) parent) =
        nativeFrame r g (rank parent + 1) parent ∧
      (nativeFrame r g (rank parent + 1) parent).exhausted = false := by
  exact ⟨traversal_agreement r g _ parent,
    ranked_native_not_exhausted r g rank h _ parent (Nat.lt_succ_self _)⟩

theorem any_sufficient_fuel_agrees (r : Bool) (g : Graph) (rank : Nat → Nat)
    (h : Ranked g rank) (fuel parent : Nat) (bound : rank parent < fuel) :
    nativeFrame r g fuel parent = nativeFrame r g (rank parent + 1) parent := by
  have heq : rank parent + 1 + (fuel - (rank parent + 1)) = fuel := by omega
  rw [← heq]
  exact ranked_native_stable r g rank h (rank parent + 1) parent _ (Nat.lt_succ_self _)

def Nonfixed : Program → Prop
  | .nil | .exhausted _ => True
  | .emit _ rest => Nonfixed rest
  | .choice first rest => Nonfixed first ∧ Nonfixed rest
  | .frame _ body => Nonfixed body
  | .candidate p children rest => p.obs.fixed = false ∧ Nonfixed children ∧ Nonfixed rest

theorem nonfixed_full_outcome_preserved (program : Program) (h : Nonfixed program) :
    interpret true program = interpret false program := by
  induction program with
  | nil => rfl
  | exhausted id => rfl
  | emit event rest ih => simp [interpret, ih h]
  | frame id body ih => simp [interpret, ih h]
  | choice first rest firstIH restIH =>
    rcases h with ⟨hf, hr⟩
    simp [interpret, firstIH hf, restIH hr]
  | candidate p children rest childIH restIH =>
    rcases h with ⟨hp, hc, hr⟩
    simp only [interpret, nonfixed_classifier_preserved p.obs hp, childIH hc, restIH hr]

theorem slots_nonfixed (g : Graph) (h : ∀ id, (g id).obs.fixed = false)
    (children : Nat → Program) (hc : ∀ id, Nonfixed (children id)) (ids : List Nat) :
    Nonfixed (compileSlots g children ids) := by
  induction ids with
  | nil => trivial
  | cons slot rest ih =>
    cases he : eligible g slot <;> simp [compileSlots, he, Nonfixed, h, hc, ih]

theorem first_nonfixed (g : Graph) (h : ∀ id, (g id).obs.fixed = false)
    (children : Nat → Program) (hc : ∀ id, Nonfixed (children id))
    (parent : Nat) (lists : List (Kind × List Nat)) : Nonfixed (compileFirst g children parent lists) := by
  induction lists with
  | nil => trivial
  | cons item rest ih =>
    rcases item with ⟨kind, ids⟩
    cases hk : ordinary kind <;>
      simp [compileFirst, hk, Nonfixed, ih, slots_nonfixed g h children hc]

theorem compiled_nonfixed (g : Graph) (h : ∀ id, (g id).obs.fixed = false)
    (fuel parent : Nat) : Nonfixed (compileFrame g fuel parent) := by
  induction fuel generalizing parent with
  | zero => trivial
  | succ fuel ih =>
    simp only [compileFrame, Nonfixed, compileBody]
    exact ⟨first_nonfixed g h _ ih _ _, slots_nonfixed g h _ ih _⟩

theorem native_nonfixed_full_trace_preserved (g : Graph)
    (h : ∀ id, (g id).obs.fixed = false) (fuel parent : Nat) :
    nativeFrame true g fuel parent = nativeFrame false g fuel parent := by
  rw [← traversal_agreement, ← traversal_agreement]
  exact nonfixed_full_outcome_preserved _ (compiled_nonfixed g h fuel parent)

theorem specification_selected_safe (program : Program) (p : Pick)
    (h : (interpret true program).selected = some p) :
    p.obs.fixed = false ∧ p.obs.sticky = false := by
  induction program with
  | nil => simp [interpret] at h
  | exhausted id => simp [interpret] at h
  | emit event rest ih => exact ih h
  | frame id body ih => exact ih h
  | choice first rest firstIH restIH =>
    simp only [interpret] at h
    split at h
    · exact firstIH h
    · exact restIH h
  | candidate q children rest childIH restIH =>
    cases hd : classify true q.obs with
    | exclude => exact restIH (by simpa [interpret, hd, prepend] using h)
    | accept =>
      have eq : q = p := by simpa [interpret, hd, prepend] using h
      subst p
      exact nonexcluded_safe q.obs (by simp [hd])
    | pass =>
      simp only [interpret, hd, prepend] at h
      split at h
      · exact childIH h
      · cases hs : (interpret true children).selected with
        | none => exact restIH (by simpa [hs] using h)
        | some v =>
          have eq : v = p := by simpa [hs] using h
          subst p
          exact childIH hs
    | traverse =>
      simp only [interpret, hd, prepend] at h
      split at h
      · exact childIH h
      · cases hs : (interpret true children).selected with
        | none =>
          have eq : q = p := by simpa [hs] using h
          subst p
          exact nonexcluded_safe q.obs (by simp [hd])
        | some v =>
          have eq : v = p := by simpa [hs] using h
          subst p
          exact childIH hs

theorem native_selected_safe (g : Graph) (fuel parent : Nat) (p : Pick)
    (h : (nativeFrame true g fuel parent).selected = some p) :
    p.obs.fixed = false ∧ p.obs.sticky = false := by
  rw [← traversal_agreement] at h
  exact specification_selected_safe _ p h

def Occurs (id : Nat) : Program → Prop
  | .nil | .exhausted _ => False
  | .emit _ rest => Occurs id rest
  | .choice first rest => Occurs id first ∨ Occurs id rest
  | .frame _ body => Occurs id body
  | .candidate p children rest => id = p.id ∨ Occurs id children ∨ Occurs id rest

theorem specification_selected_occurs (r : Bool) (program : Program) (p : Pick)
    (h : (interpret r program).selected = some p) : Occurs p.id program := by
  induction program with
  | nil => simp [interpret] at h
  | exhausted id => simp [interpret] at h
  | emit event rest ih => exact ih h
  | frame id body ih => exact ih h
  | choice first rest firstIH restIH =>
    simp only [interpret] at h
    split at h
    · exact Or.inl (firstIH h)
    · exact Or.inr (restIH h)
  | candidate q children rest childIH restIH =>
    simp only [Occurs]
    cases hd : classify r q.obs with
    | exclude => exact Or.inr (Or.inr (restIH (by simpa [interpret, hd, prepend] using h)))
    | accept =>
      have eq : q = p := by simpa [interpret, hd, prepend] using h
      exact Or.inl (congrArg Pick.id eq.symm)
    | pass =>
      simp only [interpret, hd, prepend] at h
      split at h
      · exact Or.inr (Or.inl (childIH h))
      · cases hs : (interpret r children).selected with
        | none => exact Or.inr (Or.inr (restIH (by simpa [hs] using h)))
        | some v =>
          have eq : v = p := by simpa [hs] using h
          subst p
          exact Or.inr (Or.inl (childIH hs))
    | traverse =>
      simp only [interpret, hd, prepend] at h
      split at h
      · exact Or.inr (Or.inl (childIH h))
      · cases hs : (interpret r children).selected with
        | none =>
          have eq : q = p := by simpa [hs] using h
          exact Or.inl (congrArg Pick.id eq.symm)
        | some v =>
          have eq : v = p := by simpa [hs] using h
          subst p
          exact Or.inr (Or.inl (childIH hs))

theorem excluded_invocation_barrier (r : Bool) (p : Pick) (children rest : Program)
    (h : classify r p.obs = .exclude) :
    interpret r (.candidate p children rest) = prepend [.decision p.id .exclude] (interpret r rest) := by
  simp [interpret, h]

theorem excluded_no_remaining_route (r : Bool) (p : Pick) (children rest : Program)
    (id : Nat) (h : classify r p.obs = .exclude) (hr : ¬Occurs id rest)
    (q : Pick) (hq : (interpret r (.candidate p children rest)).selected = some q) : q.id ≠ id := by
  intro eq
  rw [excluded_invocation_barrier r p children rest h] at hq
  have occurs := specification_selected_occurs r rest q hq
  exact hr (eq ▸ occurs)

theorem accept_returns_immediately (r : Bool) (p : Pick) (children rest : Program)
    (h : classify r p.obs = .accept) :
    interpret r (.candidate p children rest) =
      ⟨some p, [.decision p.id .accept, .returned p.id p.id], false⟩ := by
  simp [interpret, h, prepend]

theorem traverse_fallback_trace (r : Bool) (p : Pick) (children rest : Program)
    (h : classify r p.obs = .traverse) (hn : (interpret r children).selected = none)
    (he : (interpret r children).exhausted = false) :
    interpret r (.candidate p children rest) =
      ⟨some p, [.decision p.id .traverse, .descend p.id] ++ (interpret r children).trace ++
        [.fallback p.id, .returned p.id p.id], false⟩ := by
  simp [interpret, h, hn, he, prepend]

theorem pass_empty_continues_trace (r : Bool) (p : Pick) (children rest : Program)
    (h : classify r p.obs = .pass) (hn : (interpret r children).selected = none)
    (he : (interpret r children).exhausted = false) :
    interpret r (.candidate p children rest) =
      prepend ([.decision p.id .pass, .descend p.id] ++ (interpret r children).trace)
        (interpret r rest) := by
  simp [interpret, h, hn, he, prepend]

def finalSelection (out : Outcome) : Outcome :=
  { out with trace := out.trace ++ [.final (out.selected.map Pick.id)] }

def specificationPublic (r : Bool) (g : Graph) (gates : Gates) (fuel parent : Nat) : Outcome :=
  finalSelection (if maintain gates then interpret r (compileFrame g fuel parent) else {})

def nativePublic (r : Bool) (g : Graph) (gates : Gates) (fuel parent : Nat) : Outcome :=
  finalSelection (if maintain gates then nativeFrame r g fuel parent else {})

theorem public_refinement (r : Bool) (g : Graph) (gates : Gates) (fuel parent : Nat) :
    specificationPublic r g gates fuel parent = nativePublic r g gates fuel parent := by
  simp [specificationPublic, nativePublic, traversal_agreement]

theorem public_cannot_maintain (r : Bool) (g : Graph) (gates : Gates) (fuel parent : Nat)
    (h : maintain gates = false) : nativePublic r g gates fuel parent = ⟨none, [.final none], false⟩ := by
  simp [nativePublic, h, finalSelection]

theorem public_full_trace_preserved (g : Graph) (gates : Gates) (fuel parent : Nat)
    (h : ∀ id, (g id).obs.fixed = false) :
    nativePublic true g gates fuel parent = nativePublic false g gates fuel parent := by
  simp [nativePublic, native_nonfixed_full_trace_preserved g h]

theorem reachable_nonfixed_preserved (g : Graph) (fuel parent : Nat)
    (h : Nonfixed (compileFrame g fuel parent)) :
    nativeFrame true g fuel parent = nativeFrame false g fuel parent := by
  rw [← traversal_agreement, ← traversal_agreement]
  exact nonfixed_full_outcome_preserved _ h

theorem public_selected_safe (g : Graph) (gates : Gates) (fuel parent : Nat) (p : Pick)
    (h : (nativePublic true g gates fuel parent).selected = some p) :
    p.obs.fixed = false ∧ p.obs.sticky = false := by
  simp only [nativePublic, finalSelection] at h
  split at h
  · exact native_selected_safe g fuel parent p h
  · simp at h

theorem identity_target_eligible (g : Graph) (slot : Nat) (h : resolved g slot = slot) :
    eligible g slot = true := by simp [eligible, h]

theorem zero_fuel_explicit (r : Bool) (g : Graph) (parent : Nat) :
    (nativeFrame r g 0 parent).exhausted = true := rfl

def optionCode (id : Option Nat) : Int := (id.map (fun n => (n : Int))).getD (-1)

def decisionCode : Decision → Nat
  | .exclude => 0 | .pass => 1 | .traverse => 2 | .accept => 3

def kindCode : Kind → Nat
  | .principal => 0 | .absolute => 1 | .float => 2
  | .overflowFloats => 3 | .fixed => 4 | .other => 5

def eventCode : Event → String
  | .enter id => s!"E{id}"
  | .list id pass kind => s!"L{id}:{if pass == .first then 0 else 1}:{kindCode kind}"
  | .skip id kind => s!"K{id}:{kindCode kind}"
  | .resolve slot real accepted => s!"R{slot}:{real}:{if accepted then 1 else 0}"
  | .decision id d => s!"D{id}:{decisionCode d}"
  | .descend id => s!"N{id}"
  | .fallback id => s!"B{id}"
  | .returned source selected => s!"U{source}:{selected}"
  | .finish id selected exhausted => s!"F{id}:{optionCode selected}:{if exhausted then 1 else 0}"
  | .final selected => s!"Z{optionCode selected}"
  | .exhausted id => s!"X{id}"

def traceCode (trace : List Event) : String := String.intercalate ";" (trace.map eventCode)

def resultCode (out : Outcome) : Int := optionCode (out.selected.map Pick.id)

end Traversal



