import Lean
import Timeline

namespace Timeline.Typed
open Lean
structure DocumentId where
  raw : Nat
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure ElementId where
  raw : Nat
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure FrameId where
  raw : Nat
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure HostId where
  element : ElementId
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure PseudoId where
  element : ElementId
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure PrimaryId where
  frame : FrameId
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson
structure ScrollId where
  frame : FrameId
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson

structure Element where
  id : ElementId
  owner : DocumentId
  primary : PrimaryId
  kind : Nat
  parent : ElementId
  isElement : Bool
  apzDisabled : Bool
  displayport : Bool
  pseudos : List PseudoId
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson

structure Frame where
  id : FrameId
  parent : FrameId
  content : ElementId
  scroll : Bool
  target : ScrollId
  vertical : Bool
  reversed : Bool
  availableX : Bool
  availableY : Bool
  x : Int
  y : Int
  width : Int
  height : Int
  overflowX : Nat
  overflowY : Nat
  shell : Bool
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson

structure World where
  document : DocumentId
  sourceType : Nat
  host : HostId
  pseudo : Nat
  axis : Nat
  root : HostId
  scrolling : HostId
  shell : Bool
  rootFrame : ScrollId
  apz : Bool
  elements : List Element
  frames : List Frame
  subscribers : Nat
  deriving Repr, BEq, DecidableEq, Inhabited, FromJson

structure Source where
  host : HostId
  pseudo : Nat
  deriving Repr, BEq, DecidableEq, Inhabited

def Source.erase (s : Source) : Nat × Nat := (s.host.element.raw,s.pseudo)
def Source.restore (s : Nat × Nat) : Source := ⟨⟨⟨s.1⟩⟩,s.2⟩
theorem source_roundtrip (s : Source) : Source.restore s.erase = s := by cases s; rfl

def Element.erase (e : Element) : Timeline.Element :=
  ⟨e.id.raw,e.primary.frame.raw,e.kind,e.parent.raw,e.isElement,e.apzDisabled,
    e.displayport,e.pseudos.map fun p => p.element.raw⟩
def Element.restore (owner : DocumentId) (e : Timeline.Element) : Element :=
  ⟨⟨e.id⟩,owner,⟨⟨e.primary⟩⟩,e.kind,⟨e.parent⟩,e.isElement,e.apzDisabled,
    e.displayport,e.pseudos.map fun p => ⟨⟨p⟩⟩⟩

def Frame.erase (f : Frame) : Timeline.Frame :=
  ⟨f.id.raw,f.parent.raw,f.content.raw,f.scroll,f.target.frame.raw,f.vertical,f.reversed,
    f.availableX,f.availableY,f.x,f.y,f.width,f.height,f.overflowX,f.overflowY,f.shell⟩
def Frame.restore (f : Timeline.Frame) : Frame :=
  ⟨⟨f.id⟩,⟨f.parent⟩,⟨f.content⟩,f.scroll,⟨⟨f.target⟩⟩,f.vertical,f.reversed,
    f.availableX,f.availableY,f.x,f.y,f.width,f.height,f.overflowX,f.overflowY,f.shell⟩

theorem element_roundtrip (e : Element) : Element.restore e.owner e.erase = e := by
  cases e
  simp [Element.restore,Element.erase,List.map_map,Function.comp_def]

theorem frame_roundtrip (f : Frame) : Frame.restore f.erase = f := by cases f; rfl

def World.erase (w : World) : Timeline.World :=
  ⟨w.sourceType,w.host.element.raw,w.pseudo,w.axis,w.root.element.raw,w.scrolling.element.raw,
    w.shell,w.rootFrame.frame.raw,w.apz,w.elements.map Element.erase,w.frames.map Frame.erase,w.subscribers⟩

def World.restore (doc : DocumentId) (w : Timeline.World) : World :=
  ⟨doc,w.sourceType,⟨⟨w.host⟩⟩,w.pseudo,w.axis,⟨⟨w.root⟩⟩,⟨⟨w.scrolling⟩⟩,
    w.shell,⟨⟨w.rootFrame⟩⟩,w.apz,w.elements.map (Element.restore doc),w.frames.map Frame.restore,w.subscribers⟩

def Owned (w : World) : Prop := ∀ e ∈ w.elements, e.owner = w.document

theorem world_roundtrip (w : World) (owned : Owned w) : World.restore w.document w.erase = w := by
  have elements : (w.elements.map Element.erase).map (Element.restore w.document) = w.elements := by
    rw [List.map_map]
    have h : w.elements.map (Element.restore w.document ∘ Element.erase) = w.elements.map id := by
      apply List.map_congr_left
      intro e he
      change Element.restore w.document e.erase = e
      rw [← owned e he]
      exact element_roundtrip e
    simpa using h
  have frames : (w.frames.map Frame.erase).map Frame.restore = w.frames := by
    simp [List.map_map,Function.comp_def,frame_roundtrip]
  cases w
  simp_all [World.restore,World.erase]

def element (w : World) (id : ElementId) : Element :=
  (w.elements.find? fun e => e.id == id).getD (Element.restore w.document {})
def frame (w : World) (id : FrameId) : Frame :=
  (w.frames.find? fun f => f.id == id).getD (Frame.restore {})
def primary (w : World) (id : ElementId) : PrimaryId := (element w id).primary
def pseudo (w : World) (id : HostId) (request : Nat) : ElementId :=
  if request = 0 then id.element else
    ((element w id.element).pseudos[request-1]?.getD ⟨⟨0⟩⟩).element
def target (w : World) (id : PrimaryId) : ScrollId := (frame w id.frame).target


theorem element_provider_commutes (w : World) (id : ElementId) :
    (element w id).erase = Timeline.element w.erase id.raw := by
  have find (xs : List Element) :
      ((xs.find? fun e => e.id == id).map Element.erase) =
      (xs.map Element.erase).find? (fun e => e.id == id.raw) := by
    induction xs with
    | nil => rfl
    | cons e xs ih =>
      have test : (e.id == id) = (e.erase.id == id.raw) := by cases e; cases id; rfl
      simp only [List.find?_cons,List.map_cons,← test]
      split <;> simp_all
  have get (s : Option Element) :
      (s.getD (Element.restore w.document {})).erase = (s.map Element.erase).getD {} := by
    cases s <;> rfl
  unfold element Timeline.element
  rw [get,find]
  rfl

theorem frame_provider_commutes (w : World) (id : FrameId) :
    (frame w id).erase = Timeline.frame w.erase id.raw := by
  have find (xs : List Frame) :
      ((xs.find? fun f => f.id == id).map Frame.erase) =
      (xs.map Frame.erase).find? (fun f => f.id == id.raw) := by
    induction xs with
    | nil => rfl
    | cons f xs ih =>
      have test : (f.id == id) = (f.erase.id == id.raw) := by cases f; cases id; rfl
      simp only [List.find?_cons,List.map_cons,← test]
      split <;> simp_all
  have get (s : Option Frame) :
      (s.getD (Frame.restore {})).erase = (s.map Frame.erase).getD {} := by
    cases s <;> rfl
  unfold frame Timeline.frame
  rw [get,find]
  rfl

theorem primary_provider_commutes (w : World) (id : ElementId) :
    (primary w id).frame.raw = (Timeline.element w.erase id.raw).primary := by
  exact congrArg Timeline.Element.primary (element_provider_commutes w id)

theorem target_provider_commutes (w : World) (id : PrimaryId) :
    (target w id).frame.raw = (Timeline.frame w.erase id.frame.raw).target := by
  exact congrArg Timeline.Frame.target (frame_provider_commutes w id.frame)


theorem pseudo_provider_commutes (w : World) (id : HostId) (request : Nat) :
    (pseudo w id request).raw = Timeline.pseudo w.erase id.element.raw request := by
  by_cases h : request = 0
  · simp [pseudo,Timeline.pseudo,h]
  simp only [pseudo,Timeline.pseudo,h,↓reduceIte]
  rw [← element_provider_commutes]
  cases lookup : (element w id.element).pseudos[request-1]? <;>
    simp [Element.erase,List.getElem?_map,lookup]

def rolesValid (w : World) : Bool :=
  let hasElement := fun e => e.raw == 0 || w.elements.any (fun a => a.id == e)
  let hasFrame := fun f => f.raw == 0 || w.frames.any (fun a => a.id == f)
  let hasScroller := fun f => f.frame.raw == 0 || w.frames.any (fun a => a.id == f.frame && a.scroll)
  w.document.raw != 0 && w.sourceType ≤ 4 && w.axis ≤ 3 && w.pseudo ≤ 7 &&
  (w.sourceType == 0 || w.sourceType == 3 || w.host.element.raw != 0) &&
  (w.elements.map (fun e => e.id)).eraseDups.length == w.elements.length &&
  (w.frames.map (fun f => f.id)).eraseDups.length == w.frames.length &&
  w.elements.all (fun e => e.id.raw != 0 && e.owner == w.document &&
    hasFrame e.primary.frame && hasElement e.parent &&
    (e.pseudos.zipIdx.all fun (p,i) => p.element.raw == 0 ||
      p.element != e.id && w.elements.any (fun a => a.id == p.element &&
        a.parent == e.id && a.kind == i+1))) &&
  w.frames.all (fun f => f.id.raw != 0 && hasFrame f.parent && hasElement f.content && hasScroller f.target) &&
  hasElement w.host.element && hasElement w.root.element && hasElement w.scrolling.element &&
  hasScroller w.rootFrame

structure Admitted (w : World) : Prop where
  owned : Owned w
  roles : rolesValid w = true
  elementsUnique : (w.elements.map (fun e => e.id)).Nodup
  framesUnique : (w.frames.map (fun f => f.id)).Nodup
  identifiers : Timeline.Valid w.erase
  ranked : ∀ f ∈ w.erase.frames, ∃ xs, Timeline.Path w.erase f.id xs ∧ xs.length ≤ w.erase.frames.length + 1

def sourceSpec (w : World) : Source := Source.restore (Timeline.sourceSpec w.erase)
def sourceNative (w : World) : Source := Source.restore (Timeline.sourceNative w.erase)
def resolveSpec (w : World) (source : Source) : ScrollId := ⟨⟨Timeline.frameSpec w.erase source.erase⟩⟩
def resolveNative (w : World) (source : Source) : ScrollId := ⟨⟨Timeline.frameNative w.erase source.erase⟩⟩
def sampleSpec (r : Bool) (w : World) (old : Timeline.State) : Timeline.Observation :=
  Timeline.sampleSpec r w.erase old
def sampleNative (r : Bool) (w : World) (old : Timeline.State) : Timeline.Observation :=
  Timeline.sampleNative r w.erase old

theorem source_agrees (w : World) (valid : Admitted w) : sourceNative w = sourceSpec w := by
  unfold sourceNative sourceSpec
  rw [Timeline.source_agrees w.erase valid.identifiers.1]

theorem resolution_agrees (w : World) (s : Source) (valid : Admitted w) :
    resolveNative w s = resolveSpec w s := by
  unfold resolveNative resolveSpec
  rw [Timeline.frame_agrees w.erase s.erase valid.identifiers.2.2]

theorem sample_agrees (r : Bool) (w : World) (old : Timeline.State) (valid : Admitted w) :
    sampleNative r w old = sampleSpec r w old :=
  Timeline.sample_agrees r w.erase old valid.identifiers

theorem finite_resampling_agrees (r : Bool) (ws : List World) (old : Timeline.State)
    (valid : ∀ w ∈ ws, Admitted w) :
    Timeline.runNative r (ws.map World.erase) old = Timeline.runSpec r (ws.map World.erase) old := by
  apply Timeline.finite_resampling_agrees
  intro w hw
  obtain ⟨typed,hin,rfl⟩ := List.mem_map.mp hw
  exact (valid typed hin).identifiers

theorem shared_frame_roles (id : FrameId) :
    (PrimaryId.mk id).frame = (ScrollId.mk id).frame := rfl
end Timeline.Typed
