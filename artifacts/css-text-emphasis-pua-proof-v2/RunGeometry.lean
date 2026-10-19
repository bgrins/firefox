import Emphasis

namespace Emphasis.Run

def leadingSkip : List Bool → Nat
  | [] => 0
  | true::_ => 0
  | false::rest => 1 + leadingSkip rest

theorem leading_bound (cuts : List Bool) : leadingSkip cuts ≤ cuts.length := by
  induction cuts with
  | nil => simp [leadingSkip]
  | cons b rest ih => cases b <;> simp [leadingSkip] <;> omega

theorem leading_excluded (cuts : List Bool) :
    (cuts.take (leadingSkip cuts)).all not = true := by
  induction cuts with
  | nil => simp [leadingSkip]
  | cons b rest ih =>
    cases b with
    | true => simp [leadingSkip]
    | false =>
      simp only [leadingSkip, Nat.add_comm 1, List.take_succ_cons, List.all_cons]
      exact ih

theorem leading_remainder (cuts : List Bool) :
    (cuts.drop (leadingSkip cuts)) = [] ∨ (cuts.drop (leadingSkip cuts)).head? = some true := by
  induction cuts with
  | nil => simp [leadingSkip]
  | cons b rest ih =>
    cases b with
    | true => simp [leadingSkip]
    | false =>
      simpa only [leadingSkip, Nat.add_comm 1, List.drop_succ_cons] using ih

theorem leading_direct (cuts : List Bool) : leadingSkip cuts = cuts.findIdx id := by
  induction cuts with
  | nil => simp [leadingSkip]
  | cons b rest ih => cases b <;> simp [leadingSkip, List.findIdx_cons, ih, Nat.add_comm]

def trailingSkip (cuts : List Bool) : Nat := leadingSkip cuts.reverse

theorem trailing_bound (cuts : List Bool) : trailingSkip cuts ≤ cuts.length := by
  simpa [trailingSkip] using leading_bound cuts.reverse

def shrink (start : Nat) (interior : List Bool) (endBoundary : Bool) : Nat × Nat :=
  let first := leadingSkip interior
  let remaining := interior.drop first
  let removed := if endBoundary then 0 else min remaining.length (1 + trailingSkip remaining)
  (start + first, start + interior.length - removed)

theorem shrink_bounds (start : Nat) (interior : List Bool) (endBoundary : Bool) :
    start ≤ (shrink start interior endBoundary).1 ∧
    (shrink start interior endBoundary).1 ≤ (shrink start interior endBoundary).2 ∧
    (shrink start interior endBoundary).2 ≤ start + interior.length := by
  have hf := leading_bound interior
  have ht := trailing_bound (interior.drop (leadingSkip interior))
  simp only [List.length_drop] at ht
  cases endBoundary <;> simp [shrink] <;> omega

def directShrink (start : Nat) (interior : List Bool) (endBoundary : Bool) : Nat × Nat :=
  let first := interior.findIdx id
  let lastRemoved := if endBoundary then 0 else min (interior.drop first).length (1 + (interior.drop first).reverse.findIdx id)
  (start + first, start + interior.length - lastRemoved)

theorem shrink_refinement (start : Nat) (interior : List Bool) (endBoundary : Bool) :
    shrink start interior endBoundary = directShrink start interior endBoundary := by
  simp [shrink, directShrink, trailingSkip, leading_direct]

structure Datum where
  glyph : Glyph
  before : Int
  advance : Int
  after : Int
  deriving DecidableEq, Repr

def total (xs : List Datum) : Int := (xs.map fun x => x.before + x.advance + x.after).sum

def advanceLoop : List Datum → Int → Int
  | [], coordinate => coordinate
  | x::rest, coordinate => advanceLoop rest (coordinate + x.before + x.advance + x.after)

theorem advance_refinement (xs : List Datum) (coordinate : Int) :
    advanceLoop xs coordinate = coordinate + total xs := by
  induction xs generalizing coordinate with
  | nil => simp [advanceLoop, total]
  | cons x xs ih =>
    rw [advanceLoop, ih]
    simp only [total, List.map_cons, List.sum_cons]
    omega

def mayDraw (xs : List Datum) : Bool := xs.any fun x => charMay x.glyph

def eligibleLoop (xs : List Datum) : Bool := nativeAny (xs.map fun x => charMay x.glyph) false

theorem eligible_refinement (xs : List Datum) : eligibleLoop xs = mayDraw xs := by
  simp [eligibleLoop, native_any_refinement, mayDraw, List.any_map]

def clusterAccumulator : List Datum → Bool → Int → Bool × Int
  | [], pending, coordinate => (pending,coordinate)
  | x::rest, pending, coordinate =>
    clusterAccumulator rest (pending || charMay x.glyph)
      (coordinate + x.before + x.advance + x.after)

theorem cluster_accumulator_refinement (xs : List Datum) (pending : Bool) (coordinate : Int) :
    clusterAccumulator xs pending coordinate =
      (nativeAny (xs.map fun x => charMay x.glyph) pending, advanceLoop xs coordinate) := by
  induction xs generalizing pending coordinate with
  | nil => rfl
  | cons x rest ih => simp [clusterAccumulator, nativeAny, advanceLoop, ih]

def headBefore (xs : List Datum) : Int := (xs.head?.map Datum.before).getD 0
def lastAfter (xs : List Datum) : Int := (xs.getLast?.map Datum.after).getD 0

def nativePositionTwice (xs : List Datum) (coordinate mark : Int) : Int :=
  let start := coordinate + headBefore xs
  let beforeLastSpacing := advanceLoop xs coordinate - lastAfter xs
  2 * beforeLastSpacing - (beforeLastSpacing - start + mark)

def directPositionTwice (xs : List Datum) (coordinate mark : Int) : Int :=
  2 * coordinate + total xs + headBefore xs - lastAfter xs - mark

theorem centered_position (xs : List Datum) (coordinate mark : Int) :
    nativePositionTwice xs coordinate mark = directPositionTwice xs coordinate mark := by
  simp only [nativePositionTwice, directPositionTwice, advance_refinement]
  omega

def clusterEmission (xs : List Datum) (coordinate mark : Int) : List Int :=
  let state := clusterAccumulator xs false coordinate
  let lastCoordinate := state.2 - lastAfter xs
  if state.1 then [2*lastCoordinate - (lastCoordinate-(coordinate+headBefore xs)+mark)] else []

theorem fused_cluster_emission (xs : List Datum) (coordinate mark : Int) :
    clusterEmission xs coordinate mark =
      if mayDraw xs then [directPositionTwice xs coordinate mark] else [] := by
  simp only [clusterEmission, cluster_accumulator_refinement]
  change (if eligibleLoop xs then [nativePositionTwice xs coordinate mark] else []) = _
  rw [eligible_refinement, centered_position]

theorem recenter_restores_coordinate (coordinate start mark : Int) :
    2*coordinate - (coordinate-start+mark) + (coordinate-start+mark) = 2*coordinate := by omega

inductive Action where
  | skip (advance : Int)
  | cluster (units : List Datum)
  deriving DecidableEq, Repr

def actionAdvance : Action → Int
  | .skip n => n
  | .cluster xs => total xs

def actionEvent (mark coordinate : Int) : Action → List Int
  | .skip _ => []
  | .cluster xs => if mayDraw xs then [directPositionTwice xs coordinate mark] else []

def nativeActions (mark : Int) : List Action → Int → Int × List Int
  | [], coordinate => (coordinate, [])
  | .skip n :: rest, coordinate => nativeActions mark rest (coordinate+n)
  | .cluster xs :: rest, coordinate =>
    let next := nativeActions mark rest (advanceLoop xs coordinate)
    (next.1, (if eligibleLoop xs then [nativePositionTwice xs coordinate mark] else []) ++ next.2)

def directEvents (mark coordinate : Int) (actions : List Action) : List Int :=
  (actions.zipIdx).flatMap fun (action, index) =>
    actionEvent mark (coordinate + ((actions.take index).map actionAdvance).sum) action

def declarative (mark : Int) : List Action → Int → Int × List Int
  | [], coordinate => (coordinate, [])
  | action::rest, coordinate =>
    let next := declarative mark rest (coordinate + actionAdvance action)
    (next.1, actionEvent mark coordinate action ++ next.2)

theorem direct_events_cons (mark coordinate : Int) (a : Action) (rest : List Action) :
    directEvents mark coordinate (a::rest) =
      actionEvent mark coordinate a ++ directEvents mark (coordinate + actionAdvance a) rest := by
  simp only [directEvents, List.zipIdx_cons, List.flatMap_cons, List.take_zero,
    List.map_nil, List.sum_nil, Int.add_zero]
  rw [List.zipIdx_succ, List.flatMap_map]
  congr 1
  apply congrArg (fun f => rest.zipIdx.flatMap f)
  funext item
  rcases item with ⟨action,index⟩
  simp only [List.take_succ_cons, List.map_cons, List.sum_cons]
  congr 1
  omega

theorem declarative_prefix_events (mark coordinate : Int) (actions : List Action) :
    (declarative mark actions coordinate).2 = directEvents mark coordinate actions := by
  induction actions generalizing coordinate with
  | nil => simp [declarative, directEvents]
  | cons a rest ih =>
    rw [direct_events_cons]
    simp only [declarative]
    rw [ih]

theorem arbitrary_actions (mark : Int) (actions : List Action) (coordinate : Int) :
    nativeActions mark actions coordinate = declarative mark actions coordinate := by
  induction actions generalizing coordinate with
  | nil => rfl
  | cons a rest ih =>
    cases a with
    | skip n => simp [nativeActions, declarative, actionAdvance, actionEvent, ih]
    | cluster xs => simp [nativeActions, declarative, actionAdvance, actionEvent,
        advance_refinement, eligible_refinement, centered_position, ih]

theorem final_coordinate (mark : Int) (actions : List Action) (coordinate : Int) :
    (nativeActions mark actions coordinate).1 = coordinate + (actions.map actionAdvance).sum := by
  rw [arbitrary_actions]
  induction actions generalizing coordinate with
  | nil => simp [declarative]
  | cons a rest ih =>
    simp only [declarative, List.map_cons, List.sum_cons]
    rw [ih]
    omega

theorem exact_prefix_geometry (mark coordinate : Int) (actions : List Action) :
    (nativeActions mark actions coordinate).2 = directEvents mark coordinate actions := by
  rw [arbitrary_actions, declarative_prefix_events]

theorem native_actions_append (mark : Int) (before after : List Action) (coordinate : Int) :
    nativeActions mark (before ++ after) coordinate =
      let first := nativeActions mark before coordinate
      let second := nativeActions mark after first.1
      (second.1, first.2 ++ second.2) := by
  induction before generalizing coordinate with
  | nil => simp [nativeActions]
  | cons a rest ih =>
    cases a <;> simp [nativeActions, ih, List.append_assoc]

def partialLigatureWidth (width totalClusters selectedClusters : Nat)
    (isFinal : Bool) (before after : Nat) : Nat :=
  selectedClusters * (width / totalClusters) +
    (if isFinal then width - totalClusters * (width / totalClusters) else 0) + before + after

theorem final_partial_remainder (width count : Nat) (_nonzero : count > 0) :
    partialLigatureWidth width count count true 0 0 = width := by
  simp [partialLigatureWidth]
  have h : count * (width / count) ≤ width := Nat.mul_div_le width count
  omega

theorem intermediate_partial_exact (width count selected : Nat) :
    partialLigatureWidth width count selected false 0 0 = selected * (width / count) := by
  simp [partialLigatureWidth]

def glyphAdvance (glyph : Glyph) (letterSpacing : Int) : Int :=
  let (_,flags,details) := contents glyph
  (details.map Detail.advance).sum +
    (if flags.letterSpacing then (details.length - 1 : Nat) * letterSpacing else 0)

structure RawDatum where
  glyph : Glyph
  before : Int
  after : Int
  deriving DecidableEq, Repr

def directedDatum (direction : Int) (raw : RawDatum) : Datum :=
  ⟨raw.glyph, direction * raw.before, direction * glyphAdvance raw.glyph 0,
    direction * raw.after⟩

abbrev RawCluster := List RawDatum
abbrev RawLigature := List RawCluster
abbrev RawFontRun := List RawLigature

def ligaturePlan (drawSpacing : Bool) (direction letterSpacing : Int) (first pastEnd : Nat)
    (ligature : RawLigature) : List Action :=
  let selected := (ligature.drop first).take (pastEnd-first)
  if first = 0 ∧ pastEnd = ligature.length then
    selected.map fun cluster => .cluster (cluster.map (fun raw => directedDatum direction (if drawSpacing then raw else {raw with before := 0, after := 0})))
  else if selected = [] then []
  else
    let width := ((ligature.flatten.map fun d => glyphAdvance d.glyph letterSpacing).sum).toNat
    let contentWidth := partialLigatureWidth width ligature.length selected.length
      (pastEnd == ligature.length) 0 0
    let before := if first = 0 then
      ((ligature.flatten.head?).map RawDatum.before).getD 0 else 0
    let after := if pastEnd = ligature.length then
      ((ligature.flatten.getLast?).map RawDatum.after).getD 0 else 0
    [.skip (direction * (contentWidth + before + after))]

def rangePlan (drawSpacing : Bool) (direction letterSpacing : Int) (first pastEnd : Nat) :
    List RawLigature → Nat → List Action
  | [], _ => []
  | ligature::rest, offset =>
    let begin := max first offset
    let finish := min pastEnd (offset+ligature.length)
    (if begin < finish then ligaturePlan drawSpacing direction letterSpacing
      (begin-offset) (finish-offset) ligature else []) ++
    rangePlan drawSpacing direction letterSpacing first pastEnd rest (offset+ligature.length)

def ordinaryPlan (runs : List RawFontRun) (drawSpacing : Bool) (direction letterSpacing : Int)
    (first pastEnd : Nat) : List Action :=
  rangePlan drawSpacing direction letterSpacing first pastEnd runs.flatten 0

def ValidShape (runs : List RawFontRun) : Prop :=
  (∀ run ∈ runs, run ≠ []) ∧
  (∀ run ∈ runs, ∀ ligature ∈ run, ligature ≠ []) ∧
  (∀ run ∈ runs, ∀ ligature ∈ run, ∀ cluster ∈ ligature, cluster ≠ [])

def unitOffset (runs : List RawFontRun) (clusterIndex : Nat) : Nat :=
  (((runs.flatten.flatten).take clusterIndex).map List.length).sum

theorem ordinary_run_refinement (runs : List RawFontRun) (drawSpacing : Bool) (direction letterSpacing : Int)
    (first pastEnd : Nat) (coordinate mark : Int) :
    let plan := ordinaryPlan runs drawSpacing direction letterSpacing first pastEnd
    nativeActions mark plan coordinate =
      (coordinate + (plan.map actionAdvance).sum, directEvents mark coordinate plan) := by
  dsimp
  apply Prod.ext
  · exact final_coordinate _ _ _
  · exact exact_prefix_geometry _ _ _

theorem empty_range_plan (ligatures : List RawLigature) (drawSpacing : Bool) (direction letterSpacing : Int)
    (position offset : Nat) : rangePlan drawSpacing direction letterSpacing position position ligatures offset = [] := by
  induction ligatures generalizing offset with
  | nil => rfl
  | cons ligature rest ih =>
    have h : ¬ max position offset < min position (offset + ligature.length) := by omega
    simp [rangePlan, h, ih]

theorem empty_range_no_events (runs : List RawFontRun) (drawSpacing : Bool) (direction letterSpacing : Int)
    (position : Nat) (coordinate mark : Int) :
    (nativeActions mark (ordinaryPlan runs drawSpacing direction letterSpacing position position) coordinate).2 = [] := by
  simp [ordinaryPlan, empty_range_plan, nativeActions]

theorem cluster_metrics_derived (direction : Int) (raw : RawDatum) :
    (directedDatum direction raw).advance = direction * glyphAdvance raw.glyph 0 := rfl

end Emphasis.Run
