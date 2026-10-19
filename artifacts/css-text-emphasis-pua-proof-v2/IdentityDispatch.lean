import ShrinkDispatch

namespace Emphasis.Identity
open Run Dispatch
set_option linter.unusedSimpArgs false

def eligibilityCell (cell : UnitCell) : Cell := ⟨charMay cell.datum.glyph,cell.clusterEnd⟩

def observedLoop (mark : Int) : List UnitCell → Int → Int → Bool → Bool → Nat → Int × List (Int × Nat)
  | [], coordinate, _, _, _, _ => (coordinate,[])
  | cell::rest, coordinate, start, fresh, pending, index =>
    let d := cell.datum
    let begin := if fresh then coordinate+d.before else start
    let next := pending || charMay d.glyph
    let beforeAfter := coordinate+d.before+d.advance
    let events := if cell.clusterEnd && next then [(beforeAfter+begin-mark,index)] else []
    let tail := observedLoop mark rest (beforeAfter+d.after) begin cell.clusterEnd
      (if cell.clusterEnd then false else next) (index+1)
    (tail.1,events++tail.2)

theorem observed_geometry (mark coordinate start : Int) (cells : List UnitCell)
    (fresh pending : Bool) (index : Nat) :
    let answer := observedLoop mark cells coordinate start fresh pending index
    (answer.1,answer.2.map Prod.fst) = fontLoop mark cells coordinate start fresh pending := by
  induction cells generalizing coordinate start fresh pending index with
  | nil => rfl
  | cons cell rest ih =>
    simp only [observedLoop,fontLoop]
    have h := ih (coordinate+cell.datum.before+cell.datum.advance+cell.datum.after)
      (if fresh then coordinate+cell.datum.before else start) cell.clusterEnd
      (if cell.clusterEnd then false else pending || charMay cell.datum.glyph) (index+1)
    cases e : cell.clusterEnd && (pending || charMay cell.datum.glyph) <;>
      simp [e,List.map_append] at h ⊢ <;> exact ⟨congrArg Prod.fst h,congrArg Prod.snd h⟩

theorem observed_identities (mark coordinate start : Int) (cells : List UnitCell)
    (fresh pending : Bool) (index : Nat) :
    (observedLoop mark cells coordinate start fresh pending index).2.map Prod.snd =
      streamDraw (cells.map eligibilityCell) pending index := by
  induction cells generalizing coordinate start fresh pending index with
  | nil => rfl
  | cons cell rest ih =>
    simp only [observedLoop,List.map_cons,streamDraw,eligibilityCell,List.map_append,ih]
    cases cell.clusterEnd <;> cases pending || charMay cell.datum.glyph <;> simp

theorem encoded_eligibility (units : List Datum) :
    (encodeCluster units).map eligibilityCell = encodedCluster (units.map fun u => charMay u.glyph) := by
  match units with
  | [] => rfl
  | [u] => rfl
  | u::v::rest =>
    simp only [encodeCluster,List.map_cons,eligibilityCell,encodedCluster]
    rw [encoded_eligibility (v::rest)]
    rfl
termination_by units.length

theorem raw_identity_refinement (raw : List RawUnit) (index : Nat) :
    streamDraw ((lookAhead raw).map eligibilityCell) false index =
      directDraw ((partitionUnits raw).map fun group => group.map fun u => charMay u.glyph) index := by
  rw [← raw_partition_cells raw]
  simp only [encodedClusters,List.map_flatMap,encoded_eligibility]
  rw [← List.flatMap_map]
  apply arbitrary_cluster_draws
  intro group member
  rcases List.mem_map.mp member with ⟨source,inside,rfl⟩
  simpa using partition_valid raw source inside

theorem simultaneous_raw_geometry_identity (raw : List RawUnit) (mark coordinate : Int) (index : Nat) :
    let answer := observedLoop mark (lookAhead raw) coordinate 0 true false index
    (answer.1,answer.2.map Prod.fst) =
      (coordinate+((partitionUnits raw).map (actionAdvance ∘ Action.cluster)).sum,
       directEvents mark coordinate ((partitionUnits raw).map Action.cluster)) ∧
    answer.2.map Prod.snd =
      directDraw ((partitionUnits raw).map fun group => group.map fun u => charMay u.glyph) index := by
  constructor
  · rw [observed_geometry]
    simpa [nativeFont,List.map_map] using arbitrary_raw_font raw mark coordinate
  · rw [observed_identities,raw_identity_refinement]

theorem raw_observed_coordinate (raw : List RawUnit) (mark coordinate : Int) (index : Nat) :
    (observedLoop mark (lookAhead raw) coordinate 0 true false index).1 =
      coordinate+((partitionUnits raw).map (actionAdvance ∘ Action.cluster)).sum :=
  congrArg Prod.fst (simultaneous_raw_geometry_identity raw mark coordinate index).1

theorem raw_observed_positions (raw : List RawUnit) (mark coordinate : Int) (index : Nat) :
    (observedLoop mark (lookAhead raw) coordinate 0 true false index).2.map Prod.fst =
      directEvents mark coordinate ((partitionUnits raw).map Action.cluster) :=
  congrArg Prod.snd (simultaneous_raw_geometry_identity raw mark coordinate index).1

theorem raw_observed_identities (raw : List RawUnit) (mark coordinate : Int) (index : Nat) :
    (observedLoop mark (lookAhead raw) coordinate 0 true false index).2.map Prod.snd =
      directDraw ((partitionUnits raw).map fun group => group.map fun u => charMay u.glyph) index :=
  (simultaneous_raw_geometry_identity raw mark coordinate index).2

end Emphasis.Identity
