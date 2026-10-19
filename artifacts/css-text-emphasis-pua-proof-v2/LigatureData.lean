import Dispatch
import RunSelection

namespace Emphasis.Ligature
open Run Dispatch Selection

structure Unit where
  glyph : Glyph
  before : Int
  after : Int
  deriving DecidableEq, Repr

def clusterStart (u : Unit) : Bool := (contents u.glyph).2.1.clusterStart
def ligatureStart (u : Unit) : Bool := (contents u.glyph).2.1.ligatureStart

def slice (units : List Unit) (a b : Nat) : List Unit := (units.drop a).take (b-a)

def nativeBounds (units : List Unit) (start : Nat) : Nat × Nat :=
  let backward := ((units.take (start+1)).reverse.map ligatureStart)
  let forward := ((units.drop (start+1)).map ligatureStart)
  (start-leadingSkip backward, start+1+leadingSkip forward)

def referenceBounds (units : List Unit) (start : Nat) : Nat × Nat :=
  (start-((units.take (start+1)).reverse.findIdx ligatureStart),
   start+1+(units.drop (start+1)).findIdx ligatureStart)

theorem boundary_search_refinement (units : List Unit) (start : Nat) :
    nativeBounds units start = referenceBounds units start := by
  simp only [nativeBounds,referenceBounds,leading_direct,List.findIdx_map]
  rfl

structure Counts where
  width : Int
  total : Nat
  before : Nat
  selected : Nat
  deriving DecidableEq, Repr

def zero : Counts := ⟨0,0,0,0⟩
def plus (a b : Counts) : Counts :=
  ⟨a.width+b.width,a.total+b.total,a.before+b.before,a.selected+b.selected⟩

def contribution (letter : Int) (first start finish index : Nat) (unit : Unit) : Counts :=
  let boundary := index == first || clusterStart unit
  ⟨glyphAdvance unit.glyph letter,
   if boundary then 1 else 0,
   if boundary && index < start then 1 else 0,
   if boundary && start ≤ index && index < finish then 1 else 0⟩

def nativeScan (letter : Int) (first start finish : Nat) : List Unit → Nat → Counts → Counts
  | [], _, state => state
  | unit::rest, index, state =>
    nativeScan letter first start finish rest (index+1)
      (plus state (contribution letter first start finish index unit))

def directScan (letter : Int) (first start finish : Nat) (units : List Unit) (offset : Nat) : Counts :=
  let indexed := units.zipIdx offset
  ⟨(units.map fun u => glyphAdvance u.glyph letter).sum,
   (indexed.filter fun (u,i) => i == first || clusterStart u).length,
   (indexed.filter fun (u,i) => (i == first || clusterStart u) && i < start).length,
   (indexed.filter fun (u,i) => (i == first || clusterStart u) && start ≤ i && i < finish).length⟩

theorem direct_scan_cons (letter : Int) (first start finish index : Nat) (unit : Unit) (rest : List Unit) :
    directScan letter first start finish (unit::rest) index =
      plus (contribution letter first start finish index unit)
        (directScan letter first start finish rest (index+1)) := by
  simp only [directScan,List.zipIdx_cons,contribution,plus,List.map_cons,List.sum_cons]
  congr 1 <;> simp [List.filter_cons] <;> split <;> simp_all <;> omega

theorem scan_refinement (letter : Int) (first start finish offset : Nat) (units : List Unit) (state : Counts) :
    nativeScan letter first start finish units offset state =
      plus state (directScan letter first start finish units offset) := by
  induction units generalizing offset state with
  | nil => cases state; simp [nativeScan,directScan,plus]
  | cons unit rest ih =>
    rw [nativeScan,ih,direct_scan_cons]
    simp [plus,Int.add_assoc,Nat.add_assoc]

inductive ProviderEvent where
  | letter (value : Int)
  | allocation (count : Nat)
  | allocationFailure
  | spacing (first pastEnd : Nat) (success : Bool)
  deriving DecidableEq, Repr

structure Provider where
  present : Bool
  spacingEnabled : Bool
  spacingSuccess : Nat → Nat → Bool
  allocationFailure : Nat → Bool
  letter : Int

def letterValue (p : Provider) : Int := if p.present then p.letter else 0

def nativePartial (policy : WidthPolicy) (p : Provider) (units : List Unit) (start finish : Nat) :
    Int × List ProviderEvent :=
  if finish ≤ start then (0,[])
  else
    let bounds := nativeBounds units start
    let count := nativeScan (letterValue p) bounds.1 start finish
      (slice units bounds.1 bounds.2) bounds.1 zero
    let raw := partialWidth policy count.width count.total count.selected (finish == bounds.2) 0 0
    let events := if p.present then [.letter p.letter] else []
    let beforeCall := p.present && p.spacingEnabled && start == bounds.1
    let afterCall := p.present && p.spacingEnabled && finish == bounds.2
    let before := if beforeCall && p.spacingSuccess start (start+1) then
      ((units[start]?).map Unit.before).getD 0 else 0
    let after := if afterCall && p.spacingSuccess (finish-1) finish then
      ((units[finish-1]?).map Unit.after).getD 0 else 0
    (raw+before+after, events ++
      (if beforeCall then [.spacing start (start+1) (p.spacingSuccess start (start+1))] else []) ++
      (if afterCall then [.spacing (finish-1) finish (p.spacingSuccess (finish-1) finish)] else []))

def referencePartial (policy : WidthPolicy) (p : Provider) (units : List Unit) (start finish : Nat) :
    Int × List ProviderEvent :=
  if finish ≤ start then (0,[])
  else
    let (first,last) := referenceBounds units start
    let selected := slice units first last
    let count := directScan (letterValue p) first start finish selected first
    let raw := partialWidth policy count.width count.total count.selected (finish == last) 0 0
    let beforeCall := p.present && p.spacingEnabled && start == first
    let afterCall := p.present && p.spacingEnabled && finish == last
    let before := if beforeCall && p.spacingSuccess start (start+1) then
      ((units[start]?).map Unit.before).getD 0 else 0
    let after := if afterCall && p.spacingSuccess (finish-1) finish then
      ((units[finish-1]?).map Unit.after).getD 0 else 0
    (raw+before+after,
      (if p.present then [.letter p.letter] else []) ++
      (if beforeCall then [.spacing start (start+1) (p.spacingSuccess start (start+1))] else []) ++
      (if afterCall then [.spacing (finish-1) finish (p.spacingSuccess (finish-1) finish)] else []))

theorem partial_refinement (policy : WidthPolicy) (p : Provider) (units : List Unit) (start finish : Nat) :
    nativePartial policy p units start finish = referencePartial policy p units start finish := by
  simp only [nativePartial,referencePartial,boundary_search_refinement,scan_refinement]
  simp [zero,plus]

theorem contribution_counts (letter : Int) (first start finish index : Nat) (unit : Unit) :
    let c := contribution letter first start finish index unit
    c.before+c.selected ≤ c.total := by
  simp only [contribution]
  cases index == first || clusterStart unit
  · simp
  · by_cases before : index < start
    · simp [before,show ¬ start ≤ index by omega]
    · by_cases inside : index < finish <;>
        simp [before,inside,show start ≤ index by omega]

theorem scan_counts (letter : Int) (first start finish offset : Nat) (units : List Unit) (state : Counts)
    (valid : state.before+state.selected ≤ state.total) :
    let answer := nativeScan letter first start finish units offset state
    answer.before+answer.selected ≤ answer.total := by
  induction units generalizing offset state with
  | nil => exact valid
  | cons unit rest ih =>
    simp only [nativeScan]
    apply ih
    have c := contribution_counts letter first start finish offset unit
    simp only [plus]
    omega

theorem scan_total_monotone (letter : Int) (first start finish offset : Nat) (units : List Unit) (state : Counts) :
    state.total ≤ (nativeScan letter first start finish units offset state).total := by
  induction units generalizing offset state with
  | nil => exact Nat.le_refl _
  | cons unit rest ih =>
    simp only [nativeScan]
    exact Nat.le_trans (show state.total ≤ (plus state (contribution letter first start finish offset unit)).total by simp [plus])
      (ih (offset+1) (plus state (contribution letter first start finish offset unit)))

theorem nonempty_scan_positive (letter : Int) (first start finish : Nat) (units : List Unit)
    (nonempty : units ≠ []) :
    0 < (nativeScan letter first start finish units first zero).total := by
  cases units with
  | nil => contradiction
  | cons unit rest =>
    simp only [nativeScan]
    have h := scan_total_monotone letter first start finish (first+1) rest
      (plus zero (contribution letter first start finish first unit))
    simp [plus,zero,contribution] at h ⊢
    omega

theorem direct_counts_bounded (letter : Int) (first start finish offset : Nat) (units : List Unit) :
    let answer := directScan letter first start finish units offset
    answer.before+answer.selected ≤ answer.total ∧ answer.total ≤ units.length := by
  have counts := scan_counts letter first start finish offset units zero (by decide)
  rw [scan_refinement] at counts
  simp only [plus,zero,Nat.zero_add] at counts
  refine ⟨counts,?_⟩
  have h := List.length_filter_le (fun (u,i) => i == first || clusterStart u) (units.zipIdx offset)
  simpa [directScan] using h

theorem raw_bounds (units : List Unit) (start : Nat) (valid : start < units.length) :
    (nativeBounds units start).1 ≤ start ∧ start < (nativeBounds units start).2 ∧
    (nativeBounds units start).2 ≤ units.length := by
  have bound := leading_bound ((units.drop (start+1)).map ligatureStart)
  simp only [List.length_map,List.length_drop] at bound
  simp only [nativeBounds]
  omega

theorem bounds_slice_nonempty (units : List Unit) (start : Nat) (valid : start < units.length) :
    slice units (nativeBounds units start).1 (nativeBounds units start).2 ≠ [] := by
  have bounds := raw_bounds units start valid
  intro empty
  have len := congrArg List.length empty
  simp only [slice,List.length_take,List.length_drop,List.length_nil] at len
  omega

theorem raw_denominator_positive (units : List Unit) (start finish : Nat) (letter : Int)
    (valid : start < units.length) :
    let bounds := nativeBounds units start
    0 < (nativeScan letter bounds.1 start finish (slice units bounds.1 bounds.2) bounds.1 zero).total :=
  nonempty_scan_positive _ _ _ _ _ (bounds_slice_nonempty units start valid)

end Emphasis.Ligature
