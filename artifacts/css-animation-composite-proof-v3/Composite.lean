import Std

namespace Composite

inductive Operation where
  | replace | add | accumulate
  deriving DecidableEq, Repr

inductive SpecOperation where
  | replace | add | accumulate | auto
  deriving DecidableEq, Repr

def resolve (fallback : Operation) : SpecOperation → Operation
  | .replace => .replace
  | .add => .add
  | .accumulate => .accumulate
  | .auto => fallback

inductive RangeName where
  | cover | contain | entry | exit | entryCrossing | exitCrossing
  deriving DecidableEq, Repr

inductive Offset where
  | percent (value : Rat)
  | range (name : RangeName) (value : Rat)
  deriving DecidableEq, Repr

structure Declaration where
  property : Nat
  value : Option Nat
  deriving DecidableEq, Repr

structure Frame where
  offset : Option Offset
  easing : Option Nat
  composite : SpecOperation
  properties : List Declaration
  deriving DecidableEq, Repr

structure RawDeclaration where
  property : Nat
  allocation : Option Nat
  deriving DecidableEq, Repr

structure RawFrame where
  offset : Option Offset
  easing : Option Nat
  composite : SpecOperation
  properties : List RawDeclaration
  ignoredComputed : Option Rat
  deriving DecidableEq, Repr

abbrev Ownership := Nat → Nat

def projectDeclaration (owner : Ownership) (d : RawDeclaration) : Declaration :=
  ⟨d.property, d.allocation.map owner⟩

def project (owner : Ownership) (f : RawFrame) : Frame :=
  ⟨f.offset, f.easing, f.composite, f.properties.map (projectDeclaration owner)⟩

def projection (owner : Ownership) (frames : List RawFrame) : List Frame :=
  frames.map (project owner)

def rawDeclarationEqual (owner : Ownership) (a b : RawDeclaration) : Bool :=
  decide (a.property = b.property) &&
    (if a.allocation = b.allocation then true
     else decide (a.allocation.map owner = b.allocation.map owner))

theorem declaration_equality (owner : Ownership) (a b : RawDeclaration) :
    rawDeclarationEqual owner a b = decide (projectDeclaration owner a = projectDeclaration owner b) := by
  cases a with | mk ap aa =>
  cases b with | mk bp ba =>
  simp only [rawDeclarationEqual, projectDeclaration, Declaration.mk.injEq]
  split <;> simp_all

def rawPropertiesEqual (owner : Ownership) : List RawDeclaration → List RawDeclaration → Bool
  | [], [] => true
  | a :: as, b :: bs => rawDeclarationEqual owner a b && rawPropertiesEqual owner as bs
  | _, _ => false

theorem properties_equality (owner : Ownership) (a b : List RawDeclaration) :
    rawPropertiesEqual owner a b = decide (a.map (projectDeclaration owner) = b.map (projectDeclaration owner)) := by
  induction a generalizing b with
  | nil => cases b <;> simp [rawPropertiesEqual]
  | cons a as ih =>
    cases b with
    | nil => simp [rawPropertiesEqual]
    | cons b bs => simp [rawPropertiesEqual, declaration_equality, ih]

def rawFrameEqual (owner : Ownership) (a b : RawFrame) : Bool :=
  decide (a.offset = b.offset) && decide (a.easing = b.easing) &&
  decide (a.composite = b.composite) &&
  rawPropertiesEqual owner a.properties b.properties

theorem frame_equality (owner : Ownership) (a b : RawFrame) :
    rawFrameEqual owner a b = decide (project owner a = project owner b) := by
  cases a; cases b
  simp [rawFrameEqual, properties_equality, project, Bool.and_assoc]

def nativeEqual (owner : Ownership) : List RawFrame → List RawFrame → Bool
  | [], [] => true
  | a :: as, b :: bs => rawFrameEqual owner a b && nativeEqual owner as bs
  | _, _ => false

theorem complete_equality (owner : Ownership) (a b : List RawFrame) :
    nativeEqual owner a b = decide (projection owner a = projection owner b) := by
  induction a generalizing b with
  | nil => cases b <;> simp [nativeEqual, projection]
  | cons a as ih =>
    cases b with
    | nil => simp [nativeEqual, projection]
    | cons b bs =>
      simp [nativeEqual, frame_equality, ih, projection]
      rfl

structure Geometry where
  start : Rat
  scale : Rat
  attachmentStart : Rat
  attachmentEnd : Rat
  deriving DecidableEq, Repr

structure Environment where
  animation : Bool
  relevant : Bool
  target : Bool
  style : Bool
  timeline : Bool
  geometry : List (RangeName × Geometry)
  styleVersion : Nat
  deriving DecidableEq, Repr

def ranged (f : Frame) : Bool := match f.offset with
  | some (.range _ _) => true
  | _ => false

def namedOffset (env : Environment) (name : RangeName) (p : Rat) : Option Rat := do
  if !env.animation || !env.timeline then none else do
    let g ← env.geometry.findSome? (fun (n,g) => if n = name then some g else none)
    let width := g.attachmentEnd - g.attachmentStart
    if width = 0 then none
    else some ((g.start + g.scale * p - g.attachmentStart) / width)

def specifiedPercent (f : Frame) : Option Rat := match f.offset with
  | some (.percent p) => some p
  | _ => none

def anchor (frames : List Frame) (i : Nat) : Option Rat := do
  let f ← frames[i]?
  match specifiedPercent f with
  | some p => some p
  | none => if i = 0 then some (if frames.length = 1 then 1 else 0)
            else if i + 1 = frames.length then some 1 else none

def ordinaryOffset (frames : List Frame) (i : Nat) : Rat :=
  match anchor frames i with
  | some p => p
  | none =>
    let indices := List.range frames.length
    let before := (indices.filter (fun j => j < i && (anchor frames j).isSome)).getLast?
    let after := (indices.filter (fun j => i < j && (anchor frames j).isSome)).head?
    match before, after with
    | some a, some b =>
      let left := (anchor frames a).getD 0
      let right := (anchor frames b).getD 1
      (left * (b-i : Nat) + right * (i-a : Nat)) / (b-a : Nat)
    | _, _ => 0

structure Derived where
  offsets : List (Option Rat)
  hasRange : Bool
  deriving DecidableEq, Repr

def derive (env : Environment) (frames : List Frame) : Derived :=
  let ordinary := frames.filter (fun f => !ranged f)
  ⟨frames.zipIdx |>.map (fun (f,i) => match f.offset with
     | some (.range name p) => namedOffset env name p
     | _ => some (ordinaryOffset ordinary ((frames.take i).filter (fun x => !ranged x)).length)),
   frames.any ranged⟩

structure Segment where
  property : Nat
  fromOffset : Rat
  toOffset : Rat
  fromValue : Option Rat
  toValue : Option Rat
  easing : Option Nat
  fromComposite : Operation
  toComposite : Operation
  deriving DecidableEq, Repr

structure Providers where
  computedValues : Nat → List Frame → List (List (Nat × Option Rat))
  base : Nat → List Segment → List (Nat × Rat)

structure Entry where
  property : Nat
  offset : Rat
  value : Option Rat
  easing : Option Nat
  composite : Operation
  deriving DecidableEq, Repr

def connect (a b : Entry) : Segment :=
  ⟨a.property, a.offset, b.offset, a.value, b.value, a.easing, a.composite, b.composite⟩

def initialSegment (b : Entry) : Segment :=
  ⟨b.property, 0, b.offset, none, b.value, none, .replace, b.composite⟩

def finalSegment (a : Entry) : Segment :=
  ⟨a.property, a.offset, 1, a.value, none, a.easing, a.composite, .replace⟩

def groupSegments (groups : List (List Entry)) : List Segment :=
  match groups with
  | [] => []
  | group :: rest =>
    let zeroLength := match group.head?, group.getLast? with
      | some first, some last =>
        if group.length > 1 && (first.offset = 0 || first.offset = 1)
        then [connect first last] else []
      | _, _ => []
    let next := match group.getLast?, rest.head?.bind List.head? with
      | some a, some b => [connect a b]
      | _, _ => []
    zeroLength ++ next ++ groupSegments rest

def insertEntry (entry : Entry) : List Entry → List Entry
  | [] => [entry]
  | first :: rest => if entry.offset ≤ first.offset then entry :: first :: rest
                     else first :: insertEntry entry rest

def insertProperty (property : Nat) : List Nat → List Nat
  | [] => [property]
  | first :: rest => if property ≤ first then property :: first :: rest
                     else first :: insertProperty property rest

def propertySegments (entries : List Entry) : List Segment :=
  let ordered := entries.foldr insertEntry []
  let groups := (ordered.map Entry.offset).eraseDups.map
    (fun offset => ordered.filter (fun entry => entry.offset = offset))
  let initial := match ordered.head? with
    | some first => if first.offset > 0 then [initialSegment first] else []
    | none => []
  let final := match ordered.getLast? with
    | some last => if last.offset < 1 then [finalSegment last] else []
    | none => []
  initial ++ groupSegments groups ++ final

def buildConsumer (p : Providers) (env : Environment) (frames : List Frame)
    (derived : Derived) (fallback : Operation) : List Segment :=
  let values := p.computedValues env.styleVersion frames
  let entries := frames.zipIdx |>.flatMap fun (frame,index) =>
    match (derived.offsets[index]?).bind id with
    | none => []
    | some offset => ((values[index]?).getD []).map fun (property,value) =>
        Entry.mk property offset value frame.easing (resolve fallback frame.composite)
  let properties := (entries.map Entry.property).eraseDups.foldr insertProperty []
  properties.flatMap fun property => propertySegments (entries.filter (fun entry => entry.property = property))

inductive Event where
  | compute | notify | update | effectSet | cumulative (property : Nat)
  | dirty | effectUpdated | restyle
  deriving DecidableEq, Repr

structure ConsumerInputs where
  frames : List Frame
  derived : Derived
  default : Operation
  environment : Environment
  deriving DecidableEq, Repr

structure BaseInputs where
  version : Nat
  properties : List Segment
  deriving DecidableEq, Repr

structure State where
  frames : List Frame
  derived : Derived
  properties : List Segment
  base : List (Nat × Rat)
  default : Operation
  environment : Environment
  events : List Event
  running : List Nat := []
  cumulative : List Nat := []
  computeCalls : Nat := 0
  offsetBasis : Environment := environment
  propertyBasis : Option ConsumerInputs := none
  baseBasis : Option BaseInputs := none
  pending : Bool := true
  deriving DecidableEq, Repr

def inputs (s : State) : ConsumerInputs :=
  ⟨s.frames, s.derived, s.default, s.environment⟩

def consumerAt (p : Providers) (input : ConsumerInputs) : List Segment :=
  if input.environment.target then
    buildConsumer p input.environment input.frames input.derived input.default else []

def propertiesAt (p : Providers) : Option ConsumerInputs → List Segment
  | none => []
  | some input => consumerAt p input

def baseAt (p : Providers) : Option BaseInputs → List (Nat × Rat)
  | none => []
  | some input => p.base input.version input.properties

def OffsetsFresh (s : State) : Prop := s.derived = derive s.environment s.frames
abbrev Valid := OffsetsFresh

instance (s : State) : Decidable (OffsetsFresh s) := inferInstanceAs (Decidable (s.derived = derive s.environment s.frames))

def CacheFresh (p : Providers) (s : State) : Prop :=
  s.properties = consumerAt p (inputs s) ∧
  (s.environment.target = true → s.base = p.base s.environment.styleVersion s.properties)

def Fresh (p : Providers) (s : State) : Prop := OffsetsFresh s ∧ CacheFresh p s

structure Invariant (p : Providers) (s : State) : Prop where
  offsets : s.derived = derive s.offsetBasis s.frames
  properties : s.properties = propertiesAt p s.propertyBasis
  base : s.base = baseAt p s.baseBasis
  current : s.pending = false → Fresh p s

def notification (env : Environment) : List Event :=
  if env.animation && env.relevant then [.notify] else []

def rebuild (p : Providers) (s : State) : State :=
  let next := consumerAt p (inputs s)
  let base := if s.environment.target then p.base s.environment.styleVersion next else s.base
  let nextState := {s with base := base, propertyBasis := some (inputs s), baseBasis := if s.environment.target then some ⟨s.environment.styleVersion,next⟩ else s.baseBasis, pending := !decide (OffsetsFresh s)}
  if next = s.properties then
    {nextState with events := s.events ++ [.update] ++
      (if base.any (fun entry => !s.base.contains entry) then [.restyle] else [])}
  else
    {nextState with properties := next, running := s.running.filter (fun property => (next.map Segment.property).contains property), cumulative := (next.map Segment.property).eraseDups, events := s.events ++ [.update,.effectSet] ++
        ((next.map Segment.property).eraseDups.map Event.cumulative) ++ [.dirty] ++
        (if s.environment.animation then [.effectUpdated] else []) ++ [.restyle]}

theorem rebuild_fields (p : Providers) (s : State) :
    (rebuild p s).frames = s.frames ∧ (rebuild p s).derived = s.derived ∧
    (rebuild p s).environment = s.environment ∧ (rebuild p s).default = s.default ∧
    (rebuild p s).offsetBasis = s.offsetBasis ∧ (rebuild p s).computeCalls = s.computeCalls := by
  unfold rebuild; dsimp only; split <;> simp

theorem rebuild_outputs (p : Providers) (s : State) :
    (rebuild p s).properties = consumerAt p (inputs s) ∧
    (rebuild p s).base = (if s.environment.target then p.base s.environment.styleVersion (consumerAt p (inputs s)) else s.base) ∧
    (rebuild p s).propertyBasis = some (inputs s) ∧
    (rebuild p s).baseBasis = (if s.environment.target then some ⟨s.environment.styleVersion,consumerAt p (inputs s)⟩ else s.baseBasis) ∧
    (rebuild p s).pending = !decide (OffsetsFresh s) := by
  unfold rebuild; dsimp only; split <;> simp_all

theorem rebuild_preserves_frames (p : Providers) (s : State) : (rebuild p s).frames = s.frames := (rebuild_fields p s).1
theorem rebuild_preserves_derived (p : Providers) (s : State) : (rebuild p s).derived = s.derived := (rebuild_fields p s).2.1
theorem rebuild_preserves_environment (p : Providers) (s : State) : (rebuild p s).environment = s.environment := (rebuild_fields p s).2.2.1

theorem rebuild_invariant (p : Providers) (s : State) (h : Invariant p s) : Invariant p (rebuild p s) := by
  obtain ⟨hf,hd,he,ho,hb,hc⟩ := rebuild_fields p s
  obtain ⟨hp,hbase,hps,hbs,hpending⟩ := rebuild_outputs p s
  constructor
  · simpa [hf,hd,hb] using h.offsets
  · simp [hps,propertiesAt,hp]
  · rw [hbase,hbs]; split
    · rfl
    · exact h.base
  · intro ready
    have fresh : OffsetsFresh s := by simpa [hpending] using ready
    constructor
    · simpa [OffsetsFresh,hf,hd,he] using fresh
    · constructor
      · simpa [inputs,hf,hd,he,ho] using hp
      · intro target
        rw [he] at target
        simp [hbase,he,hp,target]

theorem rebuild_restores (p : Providers) (s : State) (h : Invariant p s)
    (offsets : OffsetsFresh s) : Fresh p (rebuild p s) ∧ (rebuild p s).pending = false := by
  have ready : (rebuild p s).pending = false := by simp [(rebuild_outputs p s).2.2.2.2,offsets]
  exact ⟨(rebuild_invariant p s h).current ready,ready⟩

def afterChanged (p : Providers) (s : State) (frames : List Frame) : State :=
  let next := {s with frames := frames, derived := derive s.environment frames, offsetBasis := s.environment, pending := true, events := s.events ++ [.compute] ++ notification s.environment, computeCalls := s.computeCalls + 1}
  if s.environment.target && s.environment.style then rebuild p next else next

def directSetter (p : Providers) (s : State) (frames : List Frame) : State :=
  if frames = s.frames then {s with frames := frames, derived := derive s.environment frames}
  else afterChanged p s frames

structure RawState where
  raw : List RawFrame
  state : State

def Represents (owner : Ownership) (r : RawState) : Prop := projection owner r.raw = r.state.frames

def optimizedSetter (owner : Ownership) (p : Providers) (s : RawState) (input : List RawFrame) : RawState :=
  if nativeEqual owner input s.raw then s
  else ⟨input, afterChanged p s.state (projection owner input)⟩

theorem unchanged_direct (p : Providers) (s : State) (valid : OffsetsFresh s) : directSetter p s s.frames = s := by
  simp [directSetter,OffsetsFresh] at *
  cases s; simp_all

theorem setter_refinement (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (input : List RawFrame)
    (admitted : nativeEqual owner input s.raw = true → OffsetsFresh s.state) :
    (optimizedSetter owner p s input).state = directSetter p s.state (projection owner input) := by
  unfold optimizedSetter
  split
  · rename_i equal
    have same := equal
    rw [complete_equality] at same
    simp only [decide_eq_true_eq] at same
    rw [same,representation]
    exact (unchanged_direct p s.state (admitted equal)).symm
  · rename_i different
    have unequal : projection owner input ≠ s.state.frames := by
      intro equal
      apply different
      simp [complete_equality,equal,representation.symm]
    simp [directSetter,unequal]

theorem changed_frames (p : Providers) (s : State) (frames : List Frame) : (afterChanged p s frames).frames = frames := by
  unfold afterChanged; dsimp only; split <;> simp [rebuild_preserves_frames]

theorem changed_computes_once (p : Providers) (s : State) (frames : List Frame) :
    (afterChanged p s frames).computeCalls = s.computeCalls + 1 := by
  unfold afterChanged; dsimp only; split
  · exact (rebuild_fields p _).2.2.2.2.2
  · rfl

theorem changed_invariant (p : Providers) (s : State) (h : Invariant p s) (frames : List Frame) :
    Invariant p (afterChanged p s frames) := by
  have next : Invariant p {s with frames := frames, derived := derive s.environment frames, offsetBasis := s.environment, pending := true, events := s.events ++ [.compute] ++ notification s.environment, computeCalls := s.computeCalls + 1} := by
    constructor
    · rfl
    · exact h.properties
    · exact h.base
    · simp
  unfold afterChanged; dsimp only; split
  · exact rebuild_invariant p _ next
  · exact next

theorem setter_represents (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (input : List RawFrame) :
    Represents owner (optimizedSetter owner p s input) := by
  unfold optimizedSetter; split
  · exact representation
  · exact (changed_frames p s.state (projection owner input)).symm

theorem setter_invariant (owner : Ownership) (p : Providers) (s : RawState)
    (h : Invariant p s.state) (input : List RawFrame) :
    Invariant p (optimizedSetter owner p s input).state := by
  unfold optimizedSetter; split
  · exact h
  · exact changed_invariant p s.state h _

theorem unchanged_skips_all_effects (owner : Ownership) (p : Providers) (s : RawState)
    (input : List RawFrame) (equal : nativeEqual owner input s.raw = true) : optimizedSetter owner p s input = s := by
  simp [optimizedSetter,equal]

def defaultSetter (p : Providers) (s : State) (value : Operation) : State :=
  if value = s.default then s else
  let next := {s with default := value, pending := true, events := s.events ++ notification s.environment}
  if s.environment.target && s.environment.style then rebuild p next else next

structure GeometryInputs where
  timeline : Bool
  geometry : List (RangeName × Geometry)
  deriving DecidableEq, Repr

def geometryEnvironment (env : Environment) (geometry : GeometryInputs) : Environment :=
  {env with timeline := geometry.timeline, geometry := geometry.geometry}

def geometryState (s : State) (geometry : GeometryInputs) : State :=
  {s with environment := geometryEnvironment s.environment geometry}

def resolvedGeometry (s : State) (geometry : GeometryInputs) : State :=
  let next := geometryState s geometry
  let derived := derive next.environment s.frames
  {next with derived := derived,offsetBasis := next.environment, pending := s.pending || decide (derived ≠ s.derived)}

def deferredGeometry (s : State) (geometry : GeometryInputs) : State :=
  let next := geometryState s geometry
  {next with pending := s.pending || !decide (OffsetsFresh next)}

def contextRefresh (p : Providers) (s : State) (geometry : GeometryInputs) : State :=
  let env := geometryEnvironment s.environment geometry
  if env.animation && env.timeline then
    let next := resolvedGeometry s geometry
    if next.derived ≠ s.derived && env.target && env.style then rebuild p next else next
  else deferredGeometry s geometry

def invalidateStyle (s : State) (version : Nat) (target style : Bool) : State :=
  {s with environment := {s.environment with styleVersion := version,target := target,style := style},pending := true}

def styleRefresh (p : Providers) (s : State) (version : Nat) : State :=
  rebuild p (invalidateStyle s version s.environment.target s.environment.style)

theorem default_frames (p : Providers) (s : State) (value : Operation) : (defaultSetter p s value).frames = s.frames := by
  unfold defaultSetter; split
  · rfl
  · dsimp only; split <;> simp [rebuild_preserves_frames]

theorem default_invariant (p : Providers) (s : State) (h : Invariant p s) (value : Operation) :
    Invariant p (defaultSetter p s value) := by
  have next : Invariant p {s with default := value,pending := true,events := s.events ++ notification s.environment} := by
    constructor
    · exact h.offsets
    · exact h.properties
    · exact h.base
    · simp
  unfold defaultSetter; split
  · exact h
  · dsimp only; split
    · exact rebuild_invariant p _ next
    · exact next

theorem invalidate_invariant (p : Providers) (s : State) (h : Invariant p s) (version : Nat) (target style : Bool) :
    Invariant p (invalidateStyle s version target style) := by
  constructor
  · exact h.offsets
  · exact h.properties
  · exact h.base
  · simp [invalidateStyle]

theorem style_frames (p : Providers) (s : State) (version : Nat) : (styleRefresh p s version).frames = s.frames := by
  simp [styleRefresh,rebuild_preserves_frames,invalidateStyle]

theorem style_invariant (p : Providers) (s : State) (h : Invariant p s) (version : Nat) :
    Invariant p (styleRefresh p s version) := rebuild_invariant p _ (invalidate_invariant p s h version _ _)

theorem cache_geometry (p : Providers) (s : State) (geometry : GeometryInputs) :
    CacheFresh p (geometryState s geometry) ↔ CacheFresh p s := Iff.rfl

theorem resolved_invariant (p : Providers) (s : State) (h : Invariant p s) (geometry : GeometryInputs) :
    Invariant p (resolvedGeometry s geometry) := by
  constructor
  · rfl
  · exact h.properties
  · exact h.base
  · intro ready
    obtain ⟨hp,hd⟩ := Bool.or_eq_false_iff.mp ready
    have eq : derive (geometryEnvironment s.environment geometry) s.frames = s.derived :=
      Classical.not_not.mp (of_decide_eq_false hd)
    constructor
    · rfl
    · have old := (h.current hp).2
      have eq' : derive (geometryEnvironment s.environment geometry) s.frames = s.derived := eq
      unfold resolvedGeometry geometryState
      dsimp only
      change CacheFresh p {s with environment := geometryEnvironment s.environment geometry, derived := derive (geometryEnvironment s.environment geometry) s.frames, offsetBasis := geometryEnvironment s.environment geometry, pending := s.pending || decide (derive (geometryEnvironment s.environment geometry) s.frames ≠ s.derived)}
      rw [eq']
      exact old

theorem deferred_invariant (p : Providers) (s : State) (h : Invariant p s) (geometry : GeometryInputs) :
    Invariant p (deferredGeometry s geometry) := by
  constructor
  · exact h.offsets
  · exact h.properties
  · exact h.base
  · intro ready
    have bits : s.pending = false ∧ OffsetsFresh (geometryState s geometry) := by
      simpa [deferredGeometry] using ready
    exact ⟨bits.2,(h.current bits.1).2⟩

theorem context_frames (p : Providers) (s : State) (geometry : GeometryInputs) :
    (contextRefresh p s geometry).frames = s.frames := by
  unfold contextRefresh
  dsimp only
  split
  · split <;> simp [rebuild_preserves_frames,resolvedGeometry,geometryState]
  · rfl

theorem context_invariant (p : Providers) (s : State) (h : Invariant p s) (geometry : GeometryInputs) :
    Invariant p (contextRefresh p s geometry) := by
  unfold contextRefresh
  dsimp only
  split
  · split
    · exact rebuild_invariant p _ (resolved_invariant p s h geometry)
    · exact resolved_invariant p s h geometry
  · exact deferred_invariant p s h geometry

theorem style_restores (p : Providers) (s : State) (h : Invariant p s)
    (offsets : OffsetsFresh s) (version : Nat) : Fresh p (styleRefresh p s version) := by
  apply (rebuild_restores p _ (invalidate_invariant p s h version _ _) ?_).1
  exact offsets

def offsetInputs (env : Environment) := (env.animation,env.timeline,env.geometry)

theorem derive_from_same_raw_inputs (a b : Environment) (frames : List Frame)
    (same : offsetInputs a = offsetInputs b) : derive a frames = derive b frames := by
  have fields : a.animation = b.animation ∧ a.timeline = b.timeline ∧ a.geometry = b.geometry := by
    simpa [offsetInputs] using same
  simp only [derive,namedOffset,fields.1,fields.2.1,fields.2.2]

theorem delivered_offsets_current (p : Providers) (s : State) (invariant : Invariant p s)
    (raw : offsetInputs s.offsetBasis = offsetInputs s.environment) : OffsetsFresh s :=
  invariant.offsets.trans (derive_from_same_raw_inputs s.offsetBasis s.environment s.frames raw)

theorem style_delivery_from_raw_inputs (p : Providers) (s : State) (invariant : Invariant p s)
    (raw : offsetInputs s.offsetBasis = offsetInputs s.environment) (version : Nat) :
    Fresh p (styleRefresh p s version) ∧ (styleRefresh p s version).pending = false := by
  apply rebuild_restores p _ (invalidate_invariant p s invariant version _ _)
  exact delivered_offsets_current p s invariant raw

theorem context_offset_delivery (p : Providers) (s : State) (geometry : GeometryInputs)
    (dispatch : (s.environment.animation && geometry.timeline) = true) :
    offsetInputs (contextRefresh p s geometry).offsetBasis =
      offsetInputs (contextRefresh p s geometry).environment := by
  unfold contextRefresh
  dsimp only
  split
  · split
    · rw [(rebuild_fields p _).2.2.1,(rebuild_fields p _).2.2.2.2.1]
      rfl
    · rfl
  · rename_i missing
    exact False.elim (missing dispatch)

theorem offset_then_style_delivery_ready (p : Providers) (s : State) (invariant : Invariant p s)
    (geometry : GeometryInputs) (dispatch : (s.environment.animation && geometry.timeline) = true)
    (version : Nat) :
    Fresh p (styleRefresh p (contextRefresh p s geometry) version) ∧
      (styleRefresh p (contextRefresh p s geometry) version).pending = false :=
  style_delivery_from_raw_inputs p _ (context_invariant p s invariant geometry)
    (context_offset_delivery p s geometry dispatch) version

theorem changed_setter_dispatch_ready (p : Providers) (s : State) (invariant : Invariant p s)
    (frames : List Frame) (dispatch : (s.environment.target && s.environment.style) = true) :
    Fresh p (afterChanged p s frames) ∧ (afterChanged p s frames).pending = false := by
  have h := changed_invariant p s invariant frames
  have ready : (afterChanged p s frames).pending = false := by
    unfold afterChanged
    simp only [dispatch,↓reduceIte]
    rw [(rebuild_outputs p _).2.2.2.2]
    simp [OffsetsFresh]
  exact ⟨h.current ready,ready⟩

theorem default_setter_dispatch_ready (p : Providers) (s : State) (invariant : Invariant p s)
    (value : Operation) (changed : value ≠ s.default)
    (dispatch : (s.environment.target && s.environment.style) = true)
    (raw : offsetInputs s.offsetBasis = offsetInputs s.environment) :
    Fresh p (defaultSetter p s value) ∧ (defaultSetter p s value).pending = false := by
  have h := default_invariant p s invariant value
  have offsets := delivered_offsets_current p s invariant raw
  have ready : (defaultSetter p s value).pending = false := by
    unfold defaultSetter
    simp only [changed,↓reduceIte,dispatch]
    rw [(rebuild_outputs p _).2.2.2.2]
    simp [OffsetsFresh] at offsets ⊢
    exact decide_eq_true offsets
  exact ⟨h.current ready,ready⟩

inductive Action where
  | success (input : List RawFrame)
  | failure
  | defaultValue (value : Operation)
  | context (geometry : GeometryInputs)
  | invalidate (version : Nat) (target style : Bool)
  | style (version : Nat)
  deriving Repr

def referenceStep (owner : Ownership) (p : Providers) (s : State) : Action → State
  | .success input => directSetter p s (projection owner input)
  | .failure => s
  | .defaultValue value => defaultSetter p s value
  | .context geometry => contextRefresh p s geometry
  | .invalidate version target style => invalidateStyle s version target style
  | .style version => styleRefresh p s version

def nativeStep (owner : Ownership) (p : Providers) (s : RawState) : Action → RawState
  | .success input => optimizedSetter owner p s input
  | .failure => s
  | .defaultValue value => {s with state := defaultSetter p s.state value}
  | .context geometry => {s with state := contextRefresh p s.state geometry}
  | .invalidate version target style => {s with state := invalidateStyle s.state version target style}
  | .style version => {s with state := styleRefresh p s.state version}

def Admitted (owner : Ownership) (s : RawState) : Action → Prop
  | .success input => nativeEqual owner input s.raw = true → s.state.pending = false
  | _ => True

theorem step_refinement (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (invariant : Invariant p s.state)
    (action : Action) (admitted : Admitted owner s action) :
    (nativeStep owner p s action).state = referenceStep owner p s.state action := by
  cases action <;> simp only [nativeStep,referenceStep]
  exact setter_refinement owner p s representation _ (fun equal => (invariant.current (admitted equal)).1)

theorem step_represents (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (action : Action) : Represents owner (nativeStep owner p s action) := by
  cases action with
  | success input => exact setter_represents owner p s representation input
  | failure => exact representation
  | defaultValue value => simpa [nativeStep,Represents,default_frames] using representation
  | context geometry => simpa [nativeStep,Represents,context_frames] using representation
  | invalidate version target style => exact representation
  | style version => simpa [nativeStep,Represents,style_frames] using representation

theorem step_invariant (owner : Ownership) (p : Providers) (s : RawState)
    (h : Invariant p s.state) (action : Action) : Invariant p (nativeStep owner p s action).state := by
  cases action with
  | success input => exact setter_invariant owner p s h input
  | failure => exact h
  | defaultValue value => exact default_invariant p s.state h value
  | context geometry => exact context_invariant p s.state h geometry
  | invalidate version target style => exact invalidate_invariant p s.state h version target style
  | style version => exact style_invariant p s.state h version

def nativeRun (owner : Ownership) (p : Providers) := List.foldl (nativeStep owner p)
def referenceRun (owner : Ownership) (p : Providers) := List.foldl (referenceStep owner p)

def AdmittedSequence (owner : Ownership) (p : Providers) (s : RawState) : List Action → Prop
  | [] => True
  | action :: rest => Admitted owner s action ∧ AdmittedSequence owner p (nativeStep owner p s action) rest

theorem finite_sequence_invariant (owner : Ownership) (p : Providers) (s : RawState)
    (h : Invariant p s.state) (actions : List Action) : Invariant p (nativeRun owner p s actions).state := by
  induction actions generalizing s with
  | nil => exact h
  | cons action rest ih => exact ih _ (step_invariant owner p s h action)

theorem finite_sequence_refinement (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (invariant : Invariant p s.state) (actions : List Action)
    (admitted : AdmittedSequence owner p s actions) :
    (nativeRun owner p s actions).state = referenceRun owner p s.state actions := by
  induction actions generalizing s with
  | nil => rfl
  | cons action rest ih =>
    simp only [nativeRun,referenceRun,List.foldl_cons]
    rw [← step_refinement owner p s representation invariant action admitted.1]
    exact ih _ (step_represents owner p s representation action) (step_invariant owner p s invariant action) admitted.2

theorem admitted_equal_skip_current (owner : Ownership) (p : Providers) (s : RawState)
    (invariant : Invariant p s.state) (input : List RawFrame)
    (admitted : Admitted owner s (.success input))
    (equal : nativeEqual owner input s.raw = true) :
    Fresh p s.state ∧ Fresh p (optimizedSetter owner p s input).state ∧
    (optimizedSetter owner p s input).state.pending = false ∧
    (optimizedSetter owner p s input).state = s.state := by
  have ready := admitted equal
  have current := invariant.current ready
  rw [unchanged_skips_all_effects owner p s input equal]
  exact ⟨current,current,ready,rfl⟩

theorem admitted_sequence_prefix (owner : Ownership) (p : Providers) (s : RawState)
    (before suffix : List Action) (admitted : AdmittedSequence owner p s (before ++ suffix)) :
    AdmittedSequence owner p (nativeRun owner p s before) suffix := by
  induction before generalizing s with
  | nil => exact admitted
  | cons action rest ih => exact ih _ admitted.2

theorem every_equal_prefix_current (owner : Ownership) (p : Providers) (s : RawState)
    (invariant : Invariant p s.state) (before suffix : List Action) (input : List RawFrame)
    (admitted : AdmittedSequence owner p s (before ++ .success input :: suffix))
    (equal : nativeEqual owner input (nativeRun owner p s before).raw = true) :
    Fresh p (nativeRun owner p s before).state ∧
    Fresh p (nativeStep owner p (nativeRun owner p s before) (.success input)).state ∧
    (nativeStep owner p (nativeRun owner p s before) (.success input)).state.pending = false ∧
    (nativeStep owner p (nativeRun owner p s before) (.success input)).state =
      (nativeRun owner p s before).state :=
  admitted_equal_skip_current owner p _ (finite_sequence_invariant owner p s invariant before)
    input (admitted_sequence_prefix owner p s before _ admitted).1 equal

theorem every_ready_prefix_current (owner : Ownership) (p : Providers) (s : RawState)
    (invariant : Invariant p s.state) (before suffix : List Action)
    (ready : (nativeRun owner p s before).state.pending = false) :
    Fresh p (nativeRun owner p s before).state ∧
    Invariant p (nativeRun owner p s (before ++ suffix)).state :=
  ⟨(finite_sequence_invariant owner p s invariant before).current ready,
    finite_sequence_invariant owner p s invariant (before ++ suffix)⟩

theorem finite_sequence_cache_contract (owner : Ownership) (p : Providers) (s : RawState)
    (h : Invariant p s.state) (actions : List Action)
    (ready : (nativeRun owner p s actions).state.pending = false) : Fresh p (nativeRun owner p s actions).state :=
  (finite_sequence_invariant owner p s h actions).current ready

theorem finite_sequence_delivered_style_restores (owner : Ownership) (p : Providers) (s : RawState)
    (h : Invariant p s.state) (actions : List Action)
    (offsets : OffsetsFresh (nativeRun owner p s actions).state) (version : Nat) :
    Fresh p (styleRefresh p (nativeRun owner p s actions).state version) :=
  style_restores p _ (finite_sequence_invariant owner p s h actions) offsets version

theorem every_style_delivery_prefix_current (owner : Ownership) (p : Providers) (s : RawState)
    (invariant : Invariant p s.state) (before : List Action)
    (raw : offsetInputs (nativeRun owner p s before).state.offsetBasis =
      offsetInputs (nativeRun owner p s before).state.environment) (version : Nat) :
    Fresh p (styleRefresh p (nativeRun owner p s before).state version) ∧
      (styleRefresh p (nativeRun owner p s before).state version).pending = false :=
  style_delivery_from_raw_inputs p _ (finite_sequence_invariant owner p s invariant before) raw version

theorem every_offset_style_prefix_current (owner : Ownership) (p : Providers) (s : RawState)
    (invariant : Invariant p s.state) (before : List Action) (geometry : GeometryInputs)
    (dispatch : ((nativeRun owner p s before).state.environment.animation && geometry.timeline) = true)
    (version : Nat) :
    Fresh p (styleRefresh p (contextRefresh p (nativeRun owner p s before).state geometry) version) ∧
      (styleRefresh p (contextRefresh p (nativeRun owner p s before).state geometry) version).pending = false :=
  offset_then_style_delivery_ready p _ (finite_sequence_invariant owner p s invariant before) geometry dispatch version

theorem failure_atomic (owner : Ownership) (p : Providers) (s : RawState) : nativeStep owner p s .failure = s := rfl

theorem getter_retention (owner : Ownership) (p : Providers) (s : RawState)
    (representation : Represents owner s) (input : List RawFrame) :
    (optimizedSetter owner p s input).state.frames = projection owner input := by
  unfold optimizedSetter
  split
  · rename_i h
    rw [complete_equality] at h
    simp only [decide_eq_true_eq] at h
    exact representation.symm.trans h.symm
  · exact changed_frames p s.state (projection owner input)

theorem auto_not_replace : SpecOperation.auto ≠ .replace := by decide
theorem auto_uses_default (value : Operation) : resolve value .auto = value := rfl
theorem explicit_ignores_default (a b : Operation) (op : SpecOperation) (h : op ≠ .auto) :
    resolve a op = resolve b op := by cases op <;> simp_all [resolve]

end Composite
