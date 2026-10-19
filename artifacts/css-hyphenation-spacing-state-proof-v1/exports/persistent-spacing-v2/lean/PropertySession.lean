import PersistentTabs

namespace PropertySession
open HyphenTabValues

structure Session (Value : Type) where
  frame : Nat
  run : Nat
  contentOffset : Nat
  tab : State Value
  property : Option (Cache Value)

def Associated (session : Session Value) : Prop :=
  ∀ cache, session.tab.cache = some cache → session.property = some cache

def construct (frame run contentOffset : Nat) (offset : Value)
    (property : Option (Cache Value)) : Session Value :=
  ⟨frame,run,contentOffset,PersistentTabs.initial offset,property⟩

theorem constructor_associated (frame run contentOffset : Nat) (offset : Value)
    (property : Option (Cache Value)) : Associated (construct frame run contentOffset offset property) := by
  simp [Associated,construct,PersistentTabs.initial]

structure Request where
  start : Nat
  finish : Nat
  enabled : Bool
  reflowing : Bool
  lineContainer : Bool

def query (numeric : Numeric Value) (providers : Providers Value)
    (request : Request) (session : Session Value) : Session Value :=
  if !request.enabled then session else
  let context : Context Value := ⟨request.reflowing,request.lineContainer,request.start,request.finish,session.property⟩
  let tab := calculate numeric providers context session.tab
  if session.tab.cache.isNone && request.reflowing && !request.lineContainer then session else
  if session.tab.cache.isNone && !request.reflowing then {session with tab := tab} else
  {session with tab := tab,property := tab.cache}

theorem query_associated (numeric : Numeric Value) (providers : Providers Value)
    (request : Request) (session : Session Value) (associated : Associated session) :
    Associated (query numeric providers request session) := by
  unfold query
  split
  next disabled => exact associated
  next enabled =>
    split
    next intrinsic => exact associated
    next active =>
      split
      next load =>
        have facts : session.tab.cache = none ∧ request.reflowing = false := by simpa using load
        have noCache := facts.1
        have nonreflow := facts.2
        simp [Associated,calculate,noCache,nonreflow]
      next computed => simp [Associated]

theorem query_identity (numeric : Numeric Value) (providers : Providers Value)
    (request : Request) (session : Session Value) :
    (query numeric providers request session).frame = session.frame ∧
    (query numeric providers request session).run = session.run ∧
    (query numeric providers request session).contentOffset = session.contentOffset := by
  unfold query
  split
  next disabled => simp
  next enabled =>
    split
    next intrinsic => simp
    next active => split <;> simp

def history (numeric : Numeric Value) (providers : Providers Value)
    (session : Session Value) : List Request → Session Value
  | [] => session
  | request::rest => history numeric providers (query numeric providers request session) rest

theorem history_associated (numeric : Numeric Value) (providers : Providers Value)
    (session : Session Value) (requests : List Request) (associated : Associated session) :
    Associated (history numeric providers session requests) := by
  induction requests generalizing session with
  | nil => exact associated
  | cons request rest ih => exact ih _ (query_associated _ _ _ _ associated)

theorem reflow_tab (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (session : Session Value) :
    (query numeric providers ⟨start,finish,true,true,true⟩ session).tab =
      PersistentTabs.reflowQuery numeric providers start finish session.tab := by
  simp [query,PersistentTabs.reflowQuery,calculate]

theorem nonreflow_load (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (session : Session Value) (empty : session.tab.cache = none) :
    (query numeric providers ⟨start,finish,true,false,false⟩ session).tab.cache = session.property ∧
    (query numeric providers ⟨start,finish,true,false,false⟩ session).property = session.property := by
  simp [query,calculate,empty]

theorem intrinsic_preserves_stale_property (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (session : Session Value) (empty : session.tab.cache = none) :
    query numeric providers ⟨start,finish,true,true,false⟩ session = session := by
  simp [query,empty]

theorem reflow_history_tab (numeric : Numeric Value) (providers : Providers Value)
    (start : Nat) (session : Session Value) (ends : List Nat) :
    (history numeric providers session (ends.map fun finish => ⟨start,finish,true,true,true⟩)).tab =
      PersistentTabs.queries numeric providers start session.tab ends := by
  induction ends generalizing session with
  | nil => rfl
  | cons finish rest ih =>
    simp only [List.map_cons,history,PersistentTabs.queries]
    rw [ih,reflow_tab]

theorem query_tab (numeric : Numeric Value) (providers : Providers Value)
    (request : Request) (session : Session Value) :
    (query numeric providers request session).tab =
      if request.enabled then
        calculate numeric providers ⟨request.reflowing,request.lineContainer,request.start,request.finish,session.property⟩ session.tab
      else session.tab := by
  cases enabled : request.enabled <;> cases reflow : request.reflowing <;>
    cases container : request.lineContainer <;> cases cache : session.tab.cache <;>
    simp [query,calculate,enabled,reflow,container,cache]

theorem reflow_history_values (numeric : Numeric Value) (providers : Providers Value)
    (frame run contentOffset start : Nat) (offset : Value) (property : Option (Cache Value))
    (ends : List Nat) (bounded : ∀ finish ∈ ends, start ≤ finish) :
    PersistentTabs.values (history numeric providers (construct frame run contentOffset offset property)
      (ends.map fun finish => ⟨start,finish,true,true,true⟩)).tab =
      PersistentTabs.numericReference numeric providers start start (PersistentTabs.covered start ends) ⟨offset,[]⟩ := by
  rw [reflow_history_tab]
  exact PersistentTabs.constructor_values numeric providers start offset ends bounded

end PropertySession
