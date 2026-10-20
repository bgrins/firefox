import Std
namespace FlexRelativeBaseline

structure Point where
  x : Int
  y : Int
  deriving DecidableEq, Repr

inductive Mode where
  | horizontal | verticalLR | verticalRL
  deriving DecidableEq, Repr

structure Frame where
  identity : Nat
  actual : Point
  normalProperty : Option Point
  expectedNormal : Point
  size : Point
  firstAscent : Int
  lastAscent : Int
  deriving DecidableEq, Repr

structure NormalRead where
  point : Point
  hasProperty : Bool
  deriving DecidableEq, Repr

def readNormal (frame : Frame) : NormalRead :=
  match frame.normalProperty with
  | some position => ⟨position,true⟩
  | none => ⟨frame.actual,false⟩

def PropertyReady (frame : Frame) : Prop :=
  match frame.normalProperty with
  | some position => position = frame.expectedNormal
  | none => frame.actual = frame.expectedNormal

theorem normal_read_agrees_exactly_when_property_ready (frame : Frame) :
    (readNormal frame).point = frame.expectedNormal ↔ PropertyReady frame := by
  cases h : frame.normalProperty <;> simp [readNormal,PropertyReady,h]

def blockSize (mode : Mode) (size : Point) : Int :=
  match mode with
  | .horizontal => size.y
  | .verticalLR | .verticalRL => size.x

def logicalB (mode : Mode) (container size point : Point) : Int :=
  match mode with
  | .horizontal => point.y
  | .verticalLR => point.x
  | .verticalRL => container.x-size.x-point.x

def baselineDistance (last : Bool) (mode : Mode) (container : Point)
    (frame : Frame) (position : Point) : Int :=
  let start := logicalB mode container frame.size position+
    (if last then frame.lastAscent else frame.firstAscent)
  if last then blockSize mode container-start else start

def referenceDistance (last : Bool) (mode : Mode) (container : Point) (frame : Frame) : Int :=
  baselineDistance last mode container frame frame.expectedNormal

def correctedDistance (last : Bool) (mode : Mode) (container : Point) (frame : Frame) : Int :=
  baselineDistance last mode container frame (readNormal frame).point

def originalDistance (last : Bool) (mode : Mode) (container : Point) (frame : Frame) : Int :=
  baselineDistance last mode container frame frame.actual

theorem corrected_distance_refines_reference (last : Bool) (mode : Mode)
    (container : Point) (frame : Frame) (ready : PropertyReady frame) :
    correctedDistance last mode container frame = referenceDistance last mode container frame := by
  have h := (normal_read_agrees_exactly_when_property_ready frame).mpr ready
  simp [correctedDistance,referenceDistance,h]

def unset : Int := -1073741823
def donor (last reversed : Bool) (items : List Frame) : Option Frame :=
  (if last != reversed then items.reverse else items).head?

def fallback (distance : Frame → Int) (old : Int) (selected : Option Frame) : Int :=
  if old == unset then selected.map distance |>.getD old else old

def native (last reversed : Bool) (mode : Mode) (container : Point)
    (old : Int) (items : List Frame) : Int :=
  fallback (correctedDistance last mode container) old (donor last reversed items)

def propertyReads (last reversed : Bool) (old : Int) (items : List Frame) : List (Nat × Bool) :=
  if old == unset then
    ((donor last reversed items).map fun frame => (frame.identity,(readNormal frame).hasProperty)).toList
  else []

theorem no_property_read_for_established_ascent (last reversed : Bool) (old : Int)
    (items : List Frame) (established : old ≠ unset) :
    propertyReads last reversed old items = [] := by simp [propertyReads,established]

theorem property_read_is_exact_selected_donor (last reversed : Bool) (items : List Frame)
    (frame : Frame) (selected : donor last reversed items = some frame) :
    propertyReads last reversed unset items = [(frame.identity,(readNormal frame).hasProperty)] := by
  simp [propertyReads,selected]

theorem at_most_one_property_read_per_group (last reversed : Bool) (old : Int) (items : List Frame) :
    (propertyReads last reversed old items).length ≤ 1 := by
  unfold propertyReads
  split
  · cases donor last reversed items <;> simp
  · simp

def reference (last reversed : Bool) (mode : Mode) (container : Point)
    (old : Int) (items : List Frame) : Int :=
  match donor last reversed items with
  | none => old
  | some frame => if old = unset then referenceDistance last mode container frame else old

theorem selected_donor_belongs_to_raw_line (last reversed : Bool) (items : List Frame)
    (frame : Frame) (selected : donor last reversed items = some frame) : frame ∈ items := by
  unfold donor at selected
  split at selected <;> simp_all only [List.head?_eq_some_iff]
  all_goals rcases selected with ⟨tail,h⟩
  · have : frame ∈ items.reverse := by rw [h]; simp
    simpa using this
  · rw [h]; simp

theorem arbitrary_line_refinement (last reversed : Bool) (mode : Mode) (container : Point)
    (old : Int) (items : List Frame) (ready : ∀ frame ∈ items, PropertyReady frame) :
    native last reversed mode container old items = reference last reversed mode container old items := by
  unfold native reference
  cases selected : donor last reversed items with
  | none => simp [fallback]
  | some frame =>
    have h := corrected_distance_refines_reference last mode container frame
      (ready frame (selected_donor_belongs_to_raw_line last reversed items frame selected))
    simp [fallback,h]

theorem only_executed_donor_requires_property_readiness (last reversed : Bool) (mode : Mode)
    (container : Point) (old : Int) (items : List Frame)
    (ready : old = unset → ∀ frame, donor last reversed items = some frame → PropertyReady frame) :
    native last reversed mode container old items = reference last reversed mode container old items := by
  by_cases active : old = unset
  · unfold native reference
    cases selected : donor last reversed items with
    | none => simp [fallback]
    | some frame =>
      have h := corrected_distance_refines_reference last mode container frame (ready active frame selected)
      simp [fallback,h]
  · unfold native reference
    cases donor last reversed items <;> simp [fallback,active]

theorem established_ascent_is_preserved (distance : Frame → Int) (old : Int)
    (selected : Option Frame) (established : old ≠ unset) : fallback distance old selected = old := by
  simp [fallback,established]

theorem empty_line_preserves_unset (last reversed : Bool) (mode : Mode) (container : Point) :
    native last reversed mode container unset [] = unset := by
  simp [native,donor,fallback]

def visualShift (delta : Point) (frame : Frame) : Frame :=
  { frame with
    actual := ⟨frame.expectedNormal.x+delta.x,frame.expectedNormal.y+delta.y⟩
    normalProperty := some frame.expectedNormal }

theorem shifted_frame_has_derived_ready_property (delta : Point) (frame : Frame) :
    PropertyReady (visualShift delta frame) := by simp [visualShift,PropertyReady]

theorem arbitrary_shifted_distance_is_reference (last : Bool) (mode : Mode)
    (container delta : Point) (frame : Frame) :
    correctedDistance last mode container (visualShift delta frame) =
      referenceDistance last mode container frame := by
  simp [correctedDistance,referenceDistance,baselineDistance,visualShift,readNormal]

def selectedShift (delta : Nat → Point) (frame : Frame) : Frame := visualShift (delta frame.identity) frame

theorem donor_commutes_with_preserved_line_order (last reversed : Bool)
    (items : List Frame) (update : Frame → Frame) :
    donor last reversed (items.map update) = (donor last reversed items).map update := by
  unfold donor
  split <;> simp [List.head?_map]

theorem arbitrary_line_displacement_independence (last reversed : Bool) (mode : Mode)
    (container : Point) (old : Int) (items : List Frame) (a b : Nat → Point) :
    native last reversed mode container old (items.map (selectedShift a)) =
      native last reversed mode container old (items.map (selectedShift b)) := by
  unfold native
  rw [donor_commutes_with_preserved_line_order,donor_commutes_with_preserved_line_order]
  cases h : donor last reversed items <;>
    simp [fallback,selectedShift,arbitrary_shifted_distance_is_reference]

def blockDelta (mode : Mode) (delta : Point) : Int :=
  match mode with
  | .horizontal => delta.y
  | .verticalLR => delta.x
  | .verticalRL => -delta.x

theorem original_shift_changes_group_distance (last : Bool) (mode : Mode)
    (container delta : Point) (frame : Frame) :
    originalDistance last mode container (visualShift delta frame)-referenceDistance last mode container frame =
      if last then -blockDelta mode delta else blockDelta mode delta := by
  cases mode <;> cases last <;>
    simp [originalDistance,referenceDistance,baselineDistance,visualShift,logicalB,blockSize,blockDelta] <;> omega

def startBaseline (last : Bool) (mode : Mode) (container : Point) (distance : Int) : Int :=
  if last then blockSize mode container-distance else distance

theorem original_shift_changes_parent_placement (last : Bool) (mode : Mode)
    (container delta : Point) (frame : Frame) (parentBaseline : Int) :
    (parentBaseline-startBaseline last mode container (originalDistance last mode container (visualShift delta frame)))-
      (parentBaseline-startBaseline last mode container (referenceDistance last mode container frame)) =
        -blockDelta mode delta := by
  have h := original_shift_changes_group_distance last mode container delta frame
  cases last <;> simp [startBaseline] at * <;> omega

def bounded (limit value : Int) : Prop := -limit ≤ value ∧ value ≤ limit
def pointBounded (limit : Int) (point : Point) : Prop := bounded limit point.x ∧ bounded limit point.y

theorem each_consumer_intermediate_is_in_range (mode : Mode) (limit : Int)
    (container size position : Point) (first last parent : Int)
    (nonnegative : 0 ≤ limit) (capacity : 6*limit ≤ 2147483647)
    (hc : pointBounded limit container) (hs : pointBounded limit size)
    (hp : pointBounded limit position) (hf : bounded limit first)
    (hl : bounded limit last) (hparent : bounded limit parent) :
    bounded 2147483647 (container.x-size.x) ∧
    bounded 2147483647 (container.y-size.y) ∧
    bounded 2147483647 (container.x-size.x-position.x) ∧
    bounded 2147483647 (container.y-size.y-position.y) ∧
    bounded 2147483647 (logicalB mode container size position+first) ∧
    bounded 2147483647 (logicalB mode container size position+last) ∧
    bounded 2147483647 (blockSize mode container-(logicalB mode container size position+last)) ∧
    bounded 2147483647 (parent-(logicalB mode container size position+first)) := by
  unfold pointBounded bounded at *
  cases mode <;> simp only [logicalB,blockSize] <;> omega

theorem strict_envelope_excludes_unset (last : Bool) (mode : Mode) (limit : Int)
    (container : Point) (frame : Frame)
    (nonnegative : 0 ≤ limit) (capacity : 5*limit < 1073741823)
    (hc : pointBounded limit container) (hs : pointBounded limit frame.size)
    (hp : pointBounded limit frame.expectedNormal)
    (hf : bounded limit frame.firstAscent) (hl : bounded limit frame.lastAscent) :
    referenceDistance last mode container frame ≠ unset := by
  unfold pointBounded bounded referenceDistance baselineDistance unset at *
  cases mode <;> cases last <;> simp only [logicalB,blockSize,Bool.false_eq_true,ite_false,ite_true] <;> omega

def exampleFrame : Frame := ⟨0,⟨0,20⟩,none,⟨0,0⟩,⟨40,50⟩,39,39⟩

theorem missing_property_does_not_establish_normality :
    ¬ PropertyReady exampleFrame ∧
    correctedDistance false .horizontal ⟨160,80⟩ exampleFrame = 59 ∧
    referenceDistance false .horizontal ⟨160,80⟩ exampleFrame = 39 := by
  unfold PropertyReady exampleFrame
  decide +kernel

theorem stale_property_still_leaks_a_position_error :
    correctedDistance false .horizontal ⟨160,80⟩ { exampleFrame with normalProperty := some ⟨0,10⟩ } = 49 ∧
    referenceDistance false .horizontal ⟨160,80⟩ exampleFrame = 39 := by decide +kernel

theorem property_dispatch_preserves_the_presence_observer :
    readNormal exampleFrame = ⟨⟨0,20⟩,false⟩ ∧
    readNormal { exampleFrame with normalProperty := some ⟨0,0⟩ } = ⟨⟨0,0⟩,true⟩ := by decide +kernel

theorem first_and_last_errors_agree_after_parent_conversion :
    originalDistance false .horizontal ⟨160,80⟩ (visualShift ⟨0,20⟩ exampleFrame) = 59 ∧
    originalDistance true .horizontal ⟨160,80⟩ (visualShift ⟨0,20⟩ exampleFrame) = 21 ∧
    correctedDistance false .horizontal ⟨160,80⟩ (visualShift ⟨0,20⟩ exampleFrame) = 39 ∧
    correctedDistance true .horizontal ⟨160,80⟩ (visualShift ⟨0,20⟩ exampleFrame) = 41 := by decide +kernel

theorem zero_shift_is_a_real_control (last : Bool) (mode : Mode) (container : Point) (frame : Frame) :
    originalDistance last mode container (visualShift ⟨0,0⟩ frame) = referenceDistance last mode container frame := by
  simp [originalDistance,referenceDistance,baselineDistance,visualShift]

theorem valid_property_alone_does_not_exclude_unset :
    PropertyReady { exampleFrame with
      actual := ⟨0,-1073741862⟩
      normalProperty := some ⟨0,-1073741862⟩
      expectedNormal := ⟨0,-1073741862⟩ } ∧
    referenceDistance false .horizontal ⟨160,80⟩
      { exampleFrame with expectedNormal := ⟨0,-1073741862⟩ } = unset := by
  unfold PropertyReady
  decide +kernel

end FlexRelativeBaseline
