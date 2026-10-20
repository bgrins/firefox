import StickyGeometry
namespace StickyContinuations
structure Frame where
  identity : Nat
  current : Int
  storedNormal : Option Int
  border : StickyGeometry.Interval
  margin : StickyGeometry.Interval
  deriving Repr, DecidableEq

def normal (f : Frame) : Int := f.storedNormal.getD f.current

def setPosition (f : Frame) (target : Int) : Frame :=
  let delta := target-f.current
  {f with current := target, border := StickyGeometry.move f.border delta,
          margin := StickyGeometry.move f.margin delta}

def nativeLoop (translation : Int) : List Frame → List Frame × List Nat
  | [] => ([],[])
  | f::fs =>
      let moved := setPosition f (normal f+translation)
      let rest := nativeLoop translation fs
      (moved::rest.1, f.identity::rest.2)

def referenceMoved (f : Frame) (translation : Int) : Frame :=
  {f with current := normal f+translation,
          border := ⟨f.border.origin+normal f+translation-f.current,f.border.size⟩,
          margin := ⟨f.margin.origin+normal f+translation-f.current,f.margin.size⟩}

theorem one_frame_refines (f : Frame) (translation : Int) :
    setPosition f (normal f+translation) = referenceMoved f translation := by
  simp only [setPosition,referenceMoved,StickyGeometry.move]
  congr 2 <;> omega

theorem complete_loop_refines (fs : List Frame) (translation : Int) :
    nativeLoop translation fs =
      (fs.map (fun f => referenceMoved f translation), fs.map Frame.identity) := by
  induction fs with
  | nil => rfl
  | cons f fs ih => simp only [nativeLoop,ih,List.map_cons,one_frame_refines]

inductive Event where
  | computePosition
  | moved (identity : Nat)
  deriving Repr, DecidableEq

def nativeDispatch (target : Int) (fs : List Frame) : List Frame × List Event :=
  match fs with
  | [] => ([],[])
  | f::_ =>
      match f.storedNormal with
      | none => (fs,[])
      | some n =>
          let result := nativeLoop (target-n) fs
          (result.1, Event.computePosition :: result.2.map Event.moved)

def referenceDispatch (target : Int) (fs : List Frame) : List Frame × List Event :=
  match fs.head? >>= Frame.storedNormal with
  | none => (fs,[])
  | some n =>
      (fs.map (fun f => referenceMoved f (target-n)),
       Event.computePosition :: fs.map (fun f => Event.moved f.identity))

theorem complete_dispatch_refines (fs : List Frame) (target : Int) :
    nativeDispatch target fs = referenceDispatch target fs := by
  cases fs with
  | nil => rfl
  | cons f fs =>
    cases hn : f.storedNormal <;>
      simp [nativeDispatch,referenceDispatch,hn,complete_loop_refines,List.map_map]

theorem first_missing_normal_no_calls (f : Frame) (fs : List Frame) (target : Int)
    (missing : f.storedNormal = none) : nativeDispatch target (f::fs) = (f::fs,[]) := by
  simp [nativeDispatch,missing]

theorem normal_property_preserved (f : Frame) (target : Int) :
    (setPosition f target).storedNormal = f.storedNormal := rfl

theorem native_loop_ids (fs : List Frame) (translation : Int) :
    (nativeLoop translation fs).1.map Frame.identity = fs.map Frame.identity := by
  rw [complete_loop_refines]
  simp [List.map_map,referenceMoved]

theorem exact_move_events (fs : List Frame) (translation : Int) :
    (nativeLoop translation fs).2 = fs.map Frame.identity := by
  rw [complete_loop_refines]

theorem pairwise_normal_distance (a b : Frame) (translation : Int) :
    (referenceMoved a translation).current-(referenceMoved b translation).current =
      normal a-normal b := by simp only [referenceMoved]; omega
end StickyContinuations
