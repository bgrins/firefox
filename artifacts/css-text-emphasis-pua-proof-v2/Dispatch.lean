import RunGeometry

namespace Emphasis.Dispatch

open Emphasis.Run

structure UnitCell where
  datum : Datum
  clusterEnd : Bool
  deriving DecidableEq, Repr

def encodeCluster : List Datum → List UnitCell
  | [] => []
  | [d] => [⟨d,true⟩]
  | d::e::rest => ⟨d,false⟩ :: encodeCluster (e::rest)

def fontLoop (mark : Int) : List UnitCell → Int → Int → Bool → Bool → Int × List Int
  | [], coordinate, _, _, _ => (coordinate, [])
  | cell::rest, coordinate, start, fresh, pending =>
    let d := cell.datum
    let begin := if fresh then coordinate + d.before else start
    let next := pending || charMay d.glyph
    let beforeAfter := coordinate + d.before + d.advance
    let events := if cell.clusterEnd && next then [beforeAfter + begin - mark] else []
    let tail := fontLoop mark rest (beforeAfter + d.after) begin cell.clusterEnd
      (if cell.clusterEnd then false else next)
    (tail.1, events ++ tail.2)

def clusterEndEvent (xs : List Datum) (coordinate start mark : Int) (pending : Bool) : List Int :=
  if pending || mayDraw xs then [coordinate + total xs - lastAfter xs + start - mark] else []

theorem one_cluster (xs : List Datum) (tail : List UnitCell) (coordinate start mark : Int)
    (pending : Bool) (nonempty : xs ≠ []) :
    fontLoop mark (encodeCluster xs ++ tail) coordinate start false pending =
      let next := fontLoop mark tail (coordinate + total xs) start true false
      (next.1, clusterEndEvent xs coordinate start mark pending ++ next.2) := by
  match xs with
  | [] => contradiction
  | [d] =>
    simp [encodeCluster, fontLoop, clusterEndEvent, mayDraw, total, lastAfter, Int.add_assoc]
    split <;> simp_all <;> omega
  | d::e::rest =>
    have ih := one_cluster (e::rest) tail (coordinate+d.before+d.advance+d.after)
      start mark (pending || charMay d.glyph) (by simp)
    simp only [encodeCluster, List.cons_append, fontLoop, Bool.false_eq_true,
      Bool.false_and, ↓reduceIte, List.nil_append]
    rw [ih]
    simp [clusterEndEvent, mayDraw, total, lastAfter, Int.add_assoc, Bool.or_assoc]
termination_by xs.length

theorem fresh_independent (cells : List UnitCell) (mark coordinate left right : Int) (pending : Bool) :
    fontLoop mark cells coordinate left true pending = fontLoop mark cells coordinate right true pending := by
  cases cells <;> simp [fontLoop]

theorem fresh_cluster (xs : List Datum) (tail : List UnitCell) (coordinate start mark : Int)
    (nonempty : xs ≠ []) :
    fontLoop mark (encodeCluster xs ++ tail) coordinate start true false =
      let next := fontLoop mark tail (coordinate + total xs) 0 true false
      (next.1, (if mayDraw xs then [directPositionTwice xs coordinate mark] else []) ++ next.2) := by
  have first : fontLoop mark (encodeCluster xs ++ tail) coordinate start true false =
      fontLoop mark (encodeCluster xs ++ tail) coordinate (coordinate + headBefore xs) false false := by
    match xs with
    | [] => contradiction
    | [d] => simp [encodeCluster, fontLoop, headBefore]
    | d::e::rest => simp [encodeCluster, fontLoop, headBefore]
  rw [first, one_cluster xs tail coordinate (coordinate + headBefore xs) mark false nonempty]
  rw [fresh_independent tail mark (coordinate + total xs) (coordinate + headBefore xs) 0 false]
  simp only [clusterEndEvent, Bool.false_or]
  congr 1
  split <;> simp_all [directPositionTwice] <;> omega

def encodedClusters (clusters : List (List Datum)) : List UnitCell := clusters.flatMap encodeCluster

theorem font_partition_refinement (clusters : List (List Datum)) (mark coordinate start : Int)
    (valid : ∀ c ∈ clusters, c ≠ []) :
    fontLoop mark (encodedClusters clusters) coordinate start true false =
      nativeActions mark (clusters.map Action.cluster) coordinate := by
  induction clusters generalizing coordinate start with
  | nil => simp [encodedClusters, fontLoop, nativeActions]
  | cons c rest ih =>
    simp only [encodedClusters, List.flatMap_cons, List.map_cons, nativeActions]
    rw [fresh_cluster c _ coordinate start mark (valid c (by simp))]
    simp only [encodedClusters] at ih
    dsimp only
    rw [ih _ 0 (by intro x hx; exact valid x (by simp [hx]))]
    simp [advance_refinement, eligible_refinement, centered_position]

structure RawUnit where
  datum : Datum
  clusterStart : Bool
  deriving DecidableEq, Repr

def tagCluster : List Datum → List RawUnit
  | [] => []
  | d::rest => ⟨d,true⟩ :: rest.map (fun x => ⟨x,false⟩)

def nextBoundary : List RawUnit → Bool
  | [] => true
  | x::_ => x.clusterStart

def lookAhead : List RawUnit → List UnitCell
  | [] => []
  | x::rest => ⟨x.datum,nextBoundary rest⟩ :: lookAhead rest

def nativeFont (mark : Int) (raw : List RawUnit) (coordinate : Int) : Int × List Int :=
  fontLoop mark (lookAhead raw) coordinate 0 true false

theorem continuation_cells (xs : List Datum) (tail : List RawUnit)
    (boundary : nextBoundary tail = true) :
    lookAhead (xs.map (fun x => ⟨x,false⟩) ++ tail) =
      encodeCluster xs ++ lookAhead tail := by
  match xs with
  | [] => simp [encodeCluster]
  | [d] => simp [lookAhead, encodeCluster, boundary]
  | d::e::rest =>
    simp only [List.map_cons, List.cons_append, lookAhead, nextBoundary, encodeCluster]
    congr 1
    exact continuation_cells (e::rest) tail boundary
termination_by xs.length

theorem tag_cluster_cells (xs : List Datum) (tail : List RawUnit)
    (boundary : nextBoundary tail = true) :
    lookAhead (tagCluster xs ++ tail) = encodeCluster xs ++ lookAhead tail := by
  match xs with
  | [] => simp [tagCluster, encodeCluster]
  | [d] => simp [tagCluster, encodeCluster, lookAhead, boundary]
  | d::e::rest =>
    simp only [tagCluster, List.map_cons, List.cons_append, lookAhead, nextBoundary, encodeCluster]
    congr 1
    exact continuation_cells (e::rest) tail boundary

theorem tagged_head (clusters : List (List Datum)) (valid : ∀ c ∈ clusters, c ≠ []) :
    nextBoundary (clusters.flatMap tagCluster) = true := by
  cases clusters with
  | nil => rfl
  | cons c rest =>
    cases c with
    | nil => exact False.elim (valid [] (by simp) rfl)
    | cons d ds => simp [tagCluster, nextBoundary]

theorem raw_boundary_correspondence (clusters : List (List Datum))
    (valid : ∀ c ∈ clusters, c ≠ []) :
    lookAhead (clusters.flatMap tagCluster) = encodedClusters clusters := by
  induction clusters with
  | nil => rfl
  | cons c rest ih =>
    have tailValid : ∀ x ∈ rest, x ≠ [] := by intro x hx; exact valid x (by simp [hx])
    simp only [List.flatMap_cons, encodedClusters]
    rw [tag_cluster_cells c _ (tagged_head rest tailValid)]
    rw [ih tailValid]
    rfl

theorem raw_font_refinement (raw : List RawUnit) (clusters : List (List Datum))
    (valid : ∀ c ∈ clusters, c ≠ []) (flags : raw = clusters.flatMap tagCluster)
    (mark coordinate : Int) :
    nativeFont mark raw coordinate =
      let actions := clusters.map Action.cluster
      (coordinate + (actions.map actionAdvance).sum, directEvents mark coordinate actions) := by
  simp only [nativeFont, flags, raw_boundary_correspondence clusters valid]
  rw [font_partition_refinement clusters mark coordinate 0 valid]
  apply Prod.ext
  · exact final_coordinate _ _ _
  · exact exact_prefix_geometry _ _ _

def partitionUnits : List RawUnit → List (List Datum)
  | [] => []
  | [x] => [[x.datum]]
  | x::y::rest =>
    if y.clusterStart then [x.datum] :: partitionUnits (y::rest)
    else match partitionUnits (y::rest) with
      | [] => [[x.datum]]
      | group::groups => (x.datum::group) :: groups

theorem partition_nonempty (raw : List RawUnit) (nonempty : raw ≠ []) :
    partitionUnits raw ≠ [] := by
  match raw with
  | [] => contradiction
  | [x] => simp [partitionUnits]
  | x::y::rest =>
    simp only [partitionUnits]
    split
    · simp
    · split <;> simp

theorem partition_valid (raw : List RawUnit) :
    ∀ group ∈ partitionUnits raw, group ≠ [] := by
  match raw with
  | [] => simp [partitionUnits]
  | [x] => simp [partitionUnits]
  | x::y::rest =>
    have ih := partition_valid (y::rest)
    simp only [partitionUnits]
    split
    · intro g hg
      simp only [List.mem_cons] at hg
      rcases hg with eq | member
      · simp [eq]
      · exact ih g member
    · split
      · simp
      next g gs eq =>
        intro h member
        simp only [List.mem_cons] at member
        rcases member with same | member
        · simp [same]
        · apply ih h
          simp [eq,member]
termination_by raw.length

theorem raw_partition_cells (raw : List RawUnit) :
    encodedClusters (partitionUnits raw) = lookAhead raw := by
  match raw with
  | [] => rfl
  | [x] => rfl
  | x::y::rest =>
    have ih := raw_partition_cells (y::rest)
    simp only [partitionUnits]
    split
    next boundary =>
      simp [encodedClusters,encodeCluster,lookAhead,nextBoundary,boundary] at ih ⊢
      exact ih
    next boundary =>
      split
      next empty => exact False.elim (partition_nonempty (y::rest) (by simp) empty)
      next group groups eq =>
        have nonempty := partition_valid (y::rest) group (by simp [eq])
        cases group with
        | nil => contradiction
        | cons d ds =>
          rw [eq] at ih
          simp only [encodedClusters,List.flatMap_cons] at ih ⊢
          simp only [encodeCluster,List.cons_append,lookAhead,nextBoundary]
          have no : y.clusterStart = false := by cases h : y.clusterStart <;> simp_all
          rw [no]
          congr 1
termination_by raw.length

theorem arbitrary_raw_font (raw : List RawUnit) (mark coordinate : Int) :
    nativeFont mark raw coordinate =
      let actions := (partitionUnits raw).map Action.cluster
      (coordinate + (actions.map actionAdvance).sum, directEvents mark coordinate actions) := by
  unfold nativeFont
  rw [← raw_partition_cells raw]
  rw [font_partition_refinement _ mark coordinate 0 (partition_valid raw)]
  apply Prod.ext
  · exact final_coordinate _ _ _
  · exact exact_prefix_geometry _ _ _

inductive WidthPolicy where
  | signed
  | legacyUnsigned32
  deriving DecidableEq, Repr

def quotient (policy : WidthPolicy) (width : Int) (count : Nat) : Int :=
  match policy with
  | .signed => width.tdiv count
  | .legacyUnsigned32 => ((width % 4294967296).toNat / count : Nat)

def product (policy : WidthPolicy) (count : Nat) (q : Int) : Int :=
  match policy with
  | .signed => count * q
  | .legacyUnsigned32 => (count * q) % 4294967296

def partialWidth (policy : WidthPolicy) (width : Int) (count selected : Nat)
    (final : Bool) (before after : Int) : Int :=
  let q := quotient policy width count
  product policy selected q +
    (if final then width - product policy count q else 0) + before + after

theorem whole_ligature_signed (width : Int) (count : Nat) :
    partialWidth .signed width count count true 0 0 = width := by
  simp only [partialWidth, product, ↓reduceIte, Int.add_zero]
  omega

theorem whole_ligature_legacy (width : Int) (count : Nat) :
    partialWidth .legacyUnsigned32 width count count true 0 0 = width := by
  simp only [partialWidth, ↓reduceIte, Int.add_zero]
  omega

theorem negative_legacy_is_not_signed :
    partialWidth .legacyUnsigned32 (-1500) 2 1 false 0 0 ≠
    partialWidth .signed (-1500) 2 1 false 0 0 := by decide +kernel

end Emphasis.Dispatch
