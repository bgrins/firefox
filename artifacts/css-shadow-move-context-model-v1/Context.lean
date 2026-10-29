import Std

namespace ShadowMove

structure Facts where
  localRoot : Nat
  originalParent : Option Nat
  document : Nat
  subtreeRootChanges : Bool
  inUncomposedDoc : Bool
  deriving DecidableEq, Repr

structure Context where
  isMove : Bool
  facts : Facts
  deriving DecidableEq, Repr

inductive Edge where
  | light
  | shadow (root : Nat) (parent : Option Nat) (document : Nat)
  deriving DecidableEq, Repr

def shadowFacts (root : Nat) (parent : Option Nat) (document : Nat) : Facts :=
  ⟨root, parent, document, false, false⟩

def enter (forward : Bool) (context : Context) : Edge → Context
  | .light => context
  | .shadow root parent document =>
      ⟨if forward then context.isMove else false, shadowFacts root parent document⟩

def walk (forward : Bool) (context : Context) : List Edge → Context
  | [] => context
  | edge :: rest => walk forward (enter forward context edge) rest

def walkFacts (facts : Facts) : List Edge → Facts
  | [] => facts
  | .light :: rest => walkFacts facts rest
  | .shadow root parent document :: rest =>
      walkFacts (shadowFacts root parent document) rest

theorem forwarded_move (context : Context) (path : List Edge) :
    (walk true context path).isMove = context.isMove := by
  induction path generalizing context with
  | nil => rfl
  | cons edge rest ih =>
      cases edge <;> simp [walk, enter, ih]

theorem ordinary_stays_ordinary (forward : Bool) (context : Context)
    (ordinary : context.isMove = false) (path : List Edge) :
    (walk forward context path).isMove = false := by
  induction path generalizing context with
  | nil => exact ordinary
  | cons edge rest ih =>
      apply ih
      cases edge <;> simp [enter, ordinary]

theorem facts_independent (forward : Bool) (context : Context) (path : List Edge) :
    (walk forward context path).facts = walkFacts context.facts path := by
  induction path generalizing context with
  | nil => rfl
  | cons edge rest ih =>
      cases edge <;> simp [walk, walkFacts, enter, ih]

theorem fresh_shadow_fields (context : Context) (root : Nat)
    (parent : Option Nat) (document : Nat) :
    enter true context (.shadow root parent document) =
      ⟨context.isMove, ⟨root, parent, document, false, false⟩⟩ := by
  rfl

inductive Reaction where
  | moved | disconnected | connected
  deriving DecidableEq, Repr

structure Callbacks where
  move : Bool
  disconnect : Bool
  connect : Bool
  deriving DecidableEq, Repr

def optional (present : Bool) (reaction : Reaction) : List Reaction :=
  if present then [reaction] else []

def fallback (callbacks : Callbacks) : List Reaction :=
  optional callbacks.disconnect .disconnected ++ optional callbacks.connect .connected

def reactions (unbindMove bindMove : Bool) (callbacks : Callbacks) : List Reaction :=
  (if unbindMove then [] else optional callbacks.disconnect .disconnected) ++
  (if bindMove then
    if callbacks.move then [.moved] else fallback callbacks
   else optional callbacks.connect .connected)

theorem moved_callback (unbind bind : Context) (path : List Edge)
    (u : unbind.isMove = true) (b : bind.isMove = true)
    (callbacks : Callbacks) (present : callbacks.move = true) :
    reactions (walk true unbind path).isMove (walk true bind path).isMove callbacks =
      [.moved] := by
  simp [forwarded_move, reactions, u, b, present]

theorem absent_callback_fallback (unbind bind : Context) (path : List Edge)
    (u : unbind.isMove = true) (b : bind.isMove = true)
    (callbacks : Callbacks) (absent : callbacks.move = false) :
    reactions (walk true unbind path).isMove (walk true bind path).isMove callbacks =
      fallback callbacks := by
  simp [forwarded_move, reactions, u, b, absent]

def retainedAnimation (move unchangedApplicableAnimation : Bool) (token : Nat) : Option Nat :=
  if move && unchangedApplicableAnimation then some token else none

theorem unchanged_animation_obligation (context : Context) (path : List Edge)
    (moving : context.isMove = true) (token : Nat) :
    retainedAnimation (walk true context path).isMove true token = some token ∧
    retainedAnimation (walk true context path).isMove false token = none := by
  simp [forwarded_move, retainedAnimation, moving]

def outer : Context := ⟨true, ⟨0, some 2, 1, true, true⟩⟩
def shadowPath : List Edge := [.light, .shadow 7 none 1, .light, .shadow 9 none 1]
def allCallbacks : Callbacks := ⟨true, true, true⟩

theorem shadow_loss_witness :
    (walk true outer shadowPath).facts = (walk false outer shadowPath).facts ∧
    (walk true outer shadowPath).facts.localRoot = 9 ∧
    (walk true outer shadowPath).isMove = true ∧
    (walk false outer shadowPath).isMove = false ∧
    reactions (walk true outer shadowPath).isMove
      (walk true outer shadowPath).isMove allCallbacks = [.moved] ∧
    reactions (walk false outer shadowPath).isMove
      (walk false outer shadowPath).isMove allCallbacks = [.disconnected, .connected] := by
  decide

end ShadowMove
