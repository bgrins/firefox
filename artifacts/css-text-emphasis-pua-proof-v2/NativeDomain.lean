import RawBridge
import SignedLigature

namespace Emphasis.NativeDomain
open Ligature Selection

def contiguous (length : Nat) : Nat → List Interval → Bool
  | first, [] => first == length
  | first, run::rest => run.first == first && first < run.pastEnd && run.pastEnd ≤ length &&
      contiguous length run.pastEnd rest


theorem contiguous_members (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) (run : Interval) (member : run ∈ runs) :
    first ≤ run.first := by
  induction runs generalizing first with
  | nil => simp at member
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    rcases List.mem_cons.mp member with same | tail
    · subst run; omega
    · have h := ih head.pastEnd valid.2 tail
      omega

theorem contiguous_ordered (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) : OrderedRuns runs := by
  induction runs generalizing first with
  | nil => intro i j a b order ia jb; simp at ia
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    intro i j a b order ia jb
    cases i with
    | zero =>
      simp only [List.getElem?_cons_zero,Option.some.injEq] at ia
      subst a
      cases j with
      | zero => simp only [List.getElem?_cons_zero,Option.some.injEq] at jb; subst b; exact Nat.le_refl _
      | succ j =>
        simp only [List.getElem?_cons_succ] at jb
        have h := contiguous_members length head.pastEnd rest valid.2 b (List.mem_of_getElem? jb)
        omega
    | succ i =>
      cases j with
      | zero => omega
      | succ j =>
        simp only [List.getElem?_cons_succ] at ia jb
        exact ih head.pastEnd valid.2 i j a b (by omega) ia jb

theorem contiguous_endpoint (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) :
    (runs.getLast?.map Interval.pastEnd).getD first = length := by
  induction runs generalizing first with
  | nil => simpa [contiguous] using valid
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    have tail := ih head.pastEnd valid.2
    cases rest with
    | nil => simpa using tail
    | cons second rest =>
      have e := List.getLast?_eq_some_getLast (l := second::rest) (by simp)
      simpa only [List.getLast?_cons_cons,e,Option.map_some,Option.getD_some] using tail

theorem contiguous_run_bounds (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) (run : Interval) (member : run ∈ runs) :
    run.first < run.pastEnd ∧ run.pastEnd ≤ length := by
  induction runs generalizing first with
  | nil => simp at member
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    rcases List.mem_cons.mp member with same | tail
    · subst run; omega
    · exact ih head.pastEnd valid.2 tail

theorem contiguous_adjacent (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) (index : Nat) (a b : Interval)
    (left : runs[index]? = some a) (right : runs[index+1]? = some b) : a.pastEnd = b.first := by
  induction runs generalizing first index with
  | nil => simp at left
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    cases index with
    | zero =>
      simp only [List.getElem?_cons_zero,Option.some.injEq] at left
      subst a
      cases rest with
      | nil => simp at right
      | cons next rest =>
        simp only [List.getElem?_cons_succ,List.getElem?_cons_zero,Option.some.injEq] at right
        subst b
        simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
        omega
    | succ index =>
      simp only [List.getElem?_cons_succ] at left right
      exact ih head.pastEnd valid.2 index left right

theorem contiguous_last (length first : Nat) (runs : List Interval)
    (valid : contiguous length first runs = true) (index : Nat) (a : Interval)
    (entry : runs[index]? = some a) (last : index+1 = runs.length) : a.pastEnd = length := by
  induction runs generalizing first index with
  | nil => simp at entry
  | cons head rest ih =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    cases index with
    | zero =>
      have empty : rest = [] := by
        have len : rest.length = 0 := by simp only [List.length_cons] at last; omega
        exact List.eq_nil_of_length_eq_zero len
      subst rest
      simp only [List.getElem?_cons_zero,Option.some.injEq] at entry
      subst a
      simpa [contiguous] using valid.2
    | succ index =>
      simp only [List.getElem?_cons_succ] at entry
      apply ih head.pastEnd valid.2 index entry
      simp only [List.length_cons] at last
      omega

theorem greatest_contains (length first : Nat) (runs : List Interval) (request : Interval)
    (valid : contiguous length first runs = true) (requestBound : request.first ≤ length)
    (index : Nat) (inBounds : index < runs.length)
    (yes : rawPredicate request runs index = true)
    (maximal : ∀ j, index < j → j < runs.length → rawPredicate request runs j = false) :
    ∃ a, runs[index]? = some a ∧ a.first ≤ request.first ∧ request.first ≤ a.pastEnd := by
  let a := runs[index]
  have entry : runs[index]? = some a := List.getElem?_eq_getElem inBounds
  have lower : a.first ≤ request.first := by simpa [rawPredicate,entry] using yes
  refine ⟨a,entry,lower,?_⟩
  by_cases next : index+1 < runs.length
  · let b := runs[index+1]
    have following : runs[index+1]? = some b := List.getElem?_eq_getElem next
    have no := maximal (index+1) (by omega) next
    have upper : request.first < b.first := by simpa [rawPredicate,following] using no
    have adjacent := contiguous_adjacent length first runs valid index a b entry following
    omega
  · have last := contiguous_last length first runs valid index a entry (by omega)
    omega

def rangeBounds (length : Nat) (range : Interval) : Prop := range.first ≤ range.pastEnd ∧ range.pastEnd ≤ length

theorem next_runs_bounds (length : Nat) (request : Interval) (runs : List Interval)
    (requestValid : rangeBounds length request)
    (runsValid : ∀ run ∈ runs, rangeBounds length run) :
    ∀ result ∈ nextRuns request runs, rangeBounds length result := by
  induction runs with
  | nil => simp [nextRuns]
  | cons run rest ih =>
    simp only [nextRuns]
    split
    · simp
    next first =>
      split
      · simp
      next last =>
        intro result member
        rcases List.mem_cons.mp member with same | tail
        · subst result
          have bound := runsValid run (by simp)
          simp only [rangeBounds,clip] at requestValid bound ⊢
          omega
        · exact ih (by intro x hx; exact runsValid x (by simp [hx])) result tail

theorem selected_runs_bounds (length : Nat) (request : Interval) (runs : List Interval)
    (index : Nat) (a : Interval) (entry : runs[index]? = some a)
    (contains : a.first ≤ request.first ∧ request.first ≤ a.pastEnd)
    (requestValid : rangeBounds length request)
    (runsValid : ∀ run ∈ runs, rangeBounds length run) :
    ∀ result ∈ selectedRuns request runs index, rangeBounds length result := by
  unfold selectedRuns
  cases dropped : runs.drop index with
  | nil => simp
  | cons first rest =>
    have head : (runs.drop index).head? = some a := by simpa using entry
    simp only [dropped,List.head?_cons,Option.some.injEq] at head
    subst a
    intro result member
    rcases List.mem_cons.mp member with same | tail
    · subst result
      have bound := runsValid first (List.mem_of_mem_drop (i := index) (by simp [dropped]))
      simp only [rangeBounds,clip] at requestValid bound ⊢
      omega
    · apply next_runs_bounds length request rest requestValid _ result tail
      intro x hx
      exact runsValid x (List.mem_of_mem_drop (i := index) (by simp [dropped,hx]))

def edge (units : List Ligature.Unit) (index : Nat) (test : Ligature.Unit → Bool) : Bool :=
  index == units.length || ((units[index]?).map test).getD false

structure ShapeUnit where
  cluster : Bool
  ligature : Bool
  before : Int
  after : Int
  deriving DecidableEq, Repr

def projectShape (u : Ligature.Unit) : ShapeUnit := ⟨clusterStart u,ligatureStart u,u.before,u.after⟩

def shapeEdge (units : List ShapeUnit) (index : Nat) (test : ShapeUnit → Bool) : Bool :=
  index == units.length || ((units[index]?).map test).getD false

def shapeCore (units : List ShapeUnit) (runs : List Interval) (request : Interval) : Bool :=
  request.first ≤ request.pastEnd && request.pastEnd ≤ units.length && units.length < 4294967296 &&
  contiguous units.length 0 runs &&
  shapeEdge units 0 ShapeUnit.cluster && shapeEdge units 0 ShapeUnit.ligature &&
  shapeEdge units request.first ShapeUnit.cluster && shapeEdge units request.pastEnd ShapeUnit.cluster &&
  units.all (fun u => !u.ligature || u.cluster) &&
  runs.all (fun run => shapeEdge units run.first ShapeUnit.cluster && shapeEdge units run.first ShapeUnit.ligature) &&
  (units.zipIdx).all (fun (u,i) =>
    (u.ligature || u.before == 0) &&
    (shapeEdge units (i+1) ShapeUnit.ligature || u.after == 0))

def shapeValid (units : List Ligature.Unit) (runs : List Interval) (request : Interval) : Bool :=
  shapeCore (units.map projectShape) runs request


theorem shape_contiguous (units : List Ligature.Unit) (runs : List Interval) (request : Interval)
    (valid : shapeValid units runs request = true) : contiguous units.length 0 runs = true := by
  simp_all [shapeValid,shapeCore]

theorem contiguous_initial (length : Nat) (runs : List Interval)
    (valid : contiguous length 0 runs = true) :
    runs = [] ∨ ∃ first, runs[0]? = some first ∧ first.first = 0 := by
  cases runs with
  | nil => exact Or.inl rfl
  | cons head rest =>
    simp only [contiguous,Bool.and_eq_true,beq_iff_eq,decide_eq_true_eq] at valid
    exact Or.inr ⟨head,rfl,by omega⟩

def storedAdvancesValid (units : List Ligature.Unit) : Prop :=
  ∀ u ∈ units, ∀ d ∈ (contents u.glyph).2.2, SignedLigature.Int32 d.advance

def glyphPrefixesSafe (glyph : Glyph) (letter : Int) : Prop :=
  let (_,flags,details) := contents glyph
  let spacing := if flags.letterSpacing then (details.length-1 : Nat)*letter else 0
  ∀ count ≤ details.length, SignedLigature.Int32
    (spacing+((details.take count).map Detail.advance).sum)

def metricInputsSafe (units : List Ligature.Unit) (provider : Provider) : Prop :=
  (∀ u ∈ units, glyphPrefixesSafe u.glyph 0 ∧ glyphPrefixesSafe u.glyph (letterValue provider)) ∧
  (∀ start < units.length,
    let bounds := nativeBounds units start
    let ligature := slice units bounds.1 bounds.2
    ∀ count ≤ ligature.length, SignedLigature.Int32
      (((ligature.take count).map fun u => Run.glyphAdvance u.glyph (letterValue provider)).sum))

structure Admitted (units : List Ligature.Unit) (runs : List Interval) (request : Interval) : Prop where
  shape : shapeValid units runs request = true
  advances : storedAdvancesValid units

theorem singleton_ordered (range : Interval) : OrderedRuns [range] := by
  intro i j a b order ia jb
  cases i <;> cases j <;> simp_all

def simpleUnit : Ligature.Unit :=
  ⟨.simple ⟨⟨0,by decide⟩,false⟩ ⟨65,by decide⟩ ⟨10,by decide⟩,0,0⟩

theorem inhabited_single : Admitted [simpleUnit] [⟨0,1⟩] ⟨0,1⟩ := by
  constructor
  · decide +kernel
  · simp [storedAdvancesValid,simpleUnit,contents,SignedLigature.Int32]
    decide

theorem inhabited_empty : Admitted [] [] ⟨0,0⟩ := by
  constructor
  · decide +kernel
  · simp [storedAdvancesValid]

theorem admitted_complete_refinement (units : List Ligature.Unit) (runs : List Interval)
    (request : Interval) (valid : Admitted units runs request)
    (policy : Dispatch.WidthPolicy) (provider : Provider) (direction mark coordinate : Int) :
    Ordinary.nativeOrdinary policy provider units direction mark runs request coordinate =
      Ordinary.referenceOrdinary policy provider units direction mark runs request coordinate :=
  Ordinary.complete_raw_dispatch _ _ _ _ _ _ _ _
    (contiguous_ordered _ _ _ (shape_contiguous _ _ _ valid.shape))
    (contiguous_initial _ _ (shape_contiguous _ _ _ valid.shape))

theorem scanned_arithmetic_domain (units : List Ligature.Unit) (provider : Provider)
    (start finish : Nat) (inside : start < units.length) (safe : metricInputsSafe units provider) :
    let bounds := nativeBounds units start
    let count := nativeScan (letterValue provider) bounds.1 start finish
      (slice units bounds.1 bounds.2) bounds.1 zero
    0 < count.total ∧ count.before+count.selected ≤ count.total ∧
      SignedLigature.Int32 count.width ∧
      (SignedLigature.apportioned count.width count.total count.before).natAbs ≤ 2147483648 ∧
      (SignedLigature.apportioned count.width count.total count.selected).natAbs ≤ 2147483648 := by
  let bounds := nativeBounds units start
  let group := slice units bounds.1 bounds.2
  let count := nativeScan (letterValue provider) bounds.1 start finish group bounds.1 zero
  have positive : 0 < count.total := raw_denominator_positive units start finish (letterValue provider) inside
  have counts : count.before+count.selected ≤ count.total :=
    scan_counts (letterValue provider) bounds.1 start finish bounds.1 group zero (by decide)
  have width : SignedLigature.Int32 count.width := by
    have h := safe.2 start inside group.length (Nat.le_refl _)
    simpa [count,group,bounds,scan_refinement,plus,zero,directScan] using h
  have before := SignedLigature.magnitude_bound count.width count.total count.before (by omega)
  have selected := SignedLigature.magnitude_bound count.width count.total count.selected (by omega)
  have magnitude := SignedLigature.int32_magnitude count.width width
  exact ⟨positive,counts,width,Nat.le_trans before magnitude,Nat.le_trans selected magnitude⟩

def actualLengthSelection (length : Nat) (request : Interval) (runs : List Interval) : List Interval :=
  if runs.length ≤ 1 then selectedRuns request runs 0
  else if request.first = length then selectedRuns request runs (runs.length-1)
  else selectedRuns request runs (upperBound (rawPredicate request runs) 0 runs.length)

theorem actual_length_selection_bridge (length : Nat) (request : Interval) (runs : List Interval)
    (valid : contiguous length 0 runs = true) :
    actualLengthSelection length request runs = nativeSelection request runs (rawPredicate request runs) := by
  simp only [actualLengthSelection,nativeSelection,contiguous_endpoint length 0 runs valid]

theorem actual_length_complete_dispatch (units : List Ligature.Unit) (runs : List Interval)
    (request : Interval) (valid : Admitted units runs request)
    (policy : Dispatch.WidthPolicy) (provider : Provider) (direction mark coordinate : Int) :
    Ordinary.nativeRuns policy provider units direction mark
      (actualLengthSelection units.length request runs) coordinate =
    Ordinary.referenceOrdinary policy provider units direction mark runs request coordinate := by
  rw [actual_length_selection_bridge _ _ _ (shape_contiguous _ _ _ valid.shape)]
  exact admitted_complete_refinement _ _ _ valid _ _ _ _ _

theorem actual_selected_ranges_bounded (length : Nat) (request : Interval) (runs : List Interval)
    (valid : contiguous length 0 runs = true) (requestValid : rangeBounds length request) :
    ∀ result ∈ actualLengthSelection length request runs, rangeBounds length result := by
  have runsValid : ∀ run ∈ runs, rangeBounds length run := by
    intro run member
    have h := contiguous_run_bounds length 0 runs valid run member
    exact ⟨Nat.le_of_lt h.1,h.2⟩
  have requestBound : request.first ≤ length := Nat.le_trans requestValid.1 requestValid.2
  unfold actualLengthSelection
  split
  next small =>
    cases runs with
    | nil => simp [selectedRuns]
    | cons head rest =>
      have empty : rest = [] := by
        have len : rest.length = 0 := by simp only [List.length_cons] at small; omega
        exact List.eq_nil_of_length_eq_zero len
      subst rest
      have endpoint := contiguous_last length 0 [head] valid 0 head rfl rfl
      have lower := contiguous_initial length [head] valid
      simp only [List.cons_ne_nil,false_or,List.getElem?_cons_zero,Option.some.injEq] at lower
      rcases lower with ⟨a,equal,zero⟩
      subst a
      exact selected_runs_bounds length request [head] 0 head rfl (by constructor <;> omega)
        requestValid runsValid
  next large =>
    split
    next atEnd =>
      have inside : runs.length-1 < runs.length := by omega
      let a := runs[runs.length-1]
      have entry : runs[runs.length-1]? = some a := List.getElem?_eq_getElem inside
      have endpoint := contiguous_last length 0 runs valid (runs.length-1) a entry (by omega)
      have bound := runsValid a (List.mem_of_getElem? entry)
      simp only [rangeBounds] at bound
      exact selected_runs_bounds length request runs (runs.length-1) a entry (by constructor <;> omega)
        requestValid runsValid
    next notEnd =>
      have first : rawPredicate request runs 0 = true := by
        rcases contiguous_initial length runs valid with empty | ⟨a,entry,zero⟩
        · subst runs; simp at large
        · simp [rawPredicate,entry,zero]
      have binary := upper_bound_valid (rawPredicate request runs) 0 runs.length
        (raw_predicate_ordered request runs (contiguous_ordered length 0 runs valid)) (by omega) first
      rcases greatest_contains length 0 runs request valid requestBound _ binary.2.1 binary.2.2.1 binary.2.2.2 with
        ⟨a,entry,lower,upper⟩
      exact selected_runs_bounds length request runs _ a entry ⟨lower,upper⟩ requestValid runsValid

theorem selected_shrink_bounds (units : List Ligature.Unit) (range : Interval)
    (valid : rangeBounds units.length range) :
    range.first ≤ (Ordinary.nativeShrunk units range).first ∧
    (Ordinary.nativeShrunk units range).first ≤ (Ordinary.nativeShrunk units range).pastEnd ∧
    (Ordinary.nativeShrunk units range).pastEnd ≤ range.pastEnd := by
  unfold Ordinary.nativeShrunk
  split
  · exact ⟨Nat.le_refl _,valid.1,Nat.le_refl _⟩
  next nonempty =>
    have length : ((slice units range.first range.pastEnd).map ligatureStart).length = range.pastEnd-range.first := by
      simp only [slice,List.length_map,List.length_take,List.length_drop]
      rcases valid with ⟨a,b⟩
      omega
    have h := Shrinking.index_shrink_bounds range.first
      ((slice units range.first range.pastEnd).map ligatureStart)
      (if range.pastEnd = units.length then true else ((units[range.pastEnd]?).map ligatureStart).getD false)
    rw [length] at h
    have endEq : range.first+(range.pastEnd-range.first) = range.pastEnd := by omega
    rw [endEq] at h
    exact h

end Emphasis.NativeDomain
