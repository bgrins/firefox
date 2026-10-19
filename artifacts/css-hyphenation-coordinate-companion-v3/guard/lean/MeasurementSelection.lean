import MeasurementClassification

namespace HyphenMeasurementSelection

structure Arithmetic (α : Type) where
  zero : α
  add : α → α → α
  sub : α → α → α
  le : α → α → Bool
  gt : α → α → Bool

inductive Priority where
  | none | wordWrap | normal
  deriving DecidableEq, Repr

structure Break (α : Type) where
  index : Nat
  trimCount : Nat
  trimAdvance : α
  hyphenated : Bool
  priority : Priority

structure State (α : Type) where
  width : α
  advance : α
  trimCount : Nat
  trimAdvance : α
  last : Option (Break α)
  candidate : Option (Break α)
  priority : Priority
  aborted : Bool

def initial (arith : Arithmetic α) (priority : Priority) : State α :=
  ⟨arith.zero,arith.zero,0,arith.zero,none,none,priority,false⟩

structure Opportunity where
  natural : Bool
  hyphenated : Bool
  autoWithManual : Bool
  wordWrap : Bool
  whitespaceWrap : Bool
  deriving DecidableEq, Repr

structure BreakInputs where
  suppressAll : Bool
  suppressInitial : Bool
  lineBreakBefore : Bool
  canWordWrap : Bool
  canWhitespaceWrap : Bool
  breakSpaces : Bool
  haveHyphenation : Bool
  glyphKind : Nat
  clusterStart : Bool
  previousWhitespace : Bool
  hyphenKind : HyphenMeasurementClassification.Kind
  deriving DecidableEq, Repr

def opportunity (start index : Nat) (priority : Priority) (input : BreakInputs) : Opportunity :=
  if input.suppressAll || (input.suppressInitial && index ≤ start) then
    ⟨false,false,false,false,false⟩
  else
    let natural := input.glyphKind == 1
    let optional := match input.hyphenKind with | .none | .explicit => false | _ => true
    let hyphenated := !natural && input.haveHyphenation && (!input.lineBreakBefore || index > start) && optional
    let autoManual := hyphenated && input.hyphenKind == .autoWithManual
    let wordWrap := (input.canWordWrap || (input.canWhitespaceWrap && input.glyphKind == 3)) &&
      input.clusterStart && priority != .normal
    let whitespaceWrap := index > start && input.breakSpaces && input.previousWhitespace
    ⟨natural,hyphenated,autoManual,wordWrap,whitespaceWrap⟩

def Opportunity.present (op : Opportunity) : Bool :=
  op.natural || op.hyphenated || op.wordWrap || op.whitespaceWrap

def atBreak (arith : Arithmetic α) (limit hyphenWidth : α) (index : Nat)
    (op : Opportunity) (state : State α) : State α := Id.run do
  if !op.present then return state
  let hyphenatedAdvance := if op.hyphenated then arith.add state.advance hyphenWidth else state.advance
  let mut result := state
  if result.last.isNone || arith.le (arith.sub (arith.add result.width hyphenatedAdvance) result.trimAdvance) limit then
    let priority := if op.natural || op.hyphenated || op.whitespaceWrap then Priority.normal else Priority.wordWrap
    result := {result with last := some ⟨index,result.trimCount,result.trimAdvance,op.hyphenated,priority⟩,priority := priority}
  result := {result with width := arith.add result.width result.advance,advance := arith.zero}
  if arith.gt (arith.sub result.width result.trimAdvance) limit then
    return {result with aborted := true}
  if op.wordWrap || !op.autoWithManual then
    result := {result with candidate := result.last.map (fun value => {value with priority := result.priority})}
  return result

def accumulate (arith : Arithmetic α) (charAdvance : α) (trimming isSpace : Bool) (state : State α) : State α :=
  {state with advance := arith.add state.advance charAdvance, trimCount := (if trimming then (if isSpace then state.trimCount+1 else 0) else state.trimCount), trimAdvance := (if trimming then (if isSpace then arith.add state.trimAdvance charAdvance else arith.zero) else state.trimAdvance)}

def iteration (arith : Arithmetic α) (limit hyphenWidth charAdvance : α) (index rescanLimit : Nat)
    (op : Opportunity) (trimming isSpace : Bool) (state : State α) : State α :=
  let considered := atBreak arith limit hyphenWidth index op state
  if considered.aborted || index < rescanLimit then considered
  else accumulate arith charAdvance trimming isSpace considered

structure Result (α μ : Type) where
  fit : Nat
  usedHyphenation : Bool
  lastBreak : Nat
  priority : Priority
  trimCount : Nat
  trimAdvance : α
  metrics : μ

def selected (last : Break α) (candidate : Option (Break α)) : Break α :=
  match candidate with
  | none => last
  | some previous => if previous.index ≠ last.index then previous else last

def finalize (arith : Arithmetic α) (limit : α) (start maxLength incomingLast : Nat)
    (measure : Nat → Nat → μ) (state : State α) : Result α μ := Id.run do
  let width := if state.aborted then state.width else arith.add state.width state.advance
  let mut fit := maxLength
  let mut used := false
  let mut priority := state.priority
  let mut trimCount := state.trimCount
  let mut trimAdvance := state.trimAdvance
  let mut last := state.last
  if !(arith.le (arith.sub width state.trimAdvance) limit) then
    if let some remembered := state.last then
      let chosen := selected remembered state.candidate
      last := some chosen
      fit := chosen.index-start
      used := chosen.hyphenated
      priority := match state.candidate with
        | some previous => if previous.index ≠ remembered.index then previous.priority else priority
        | none => priority
      trimCount := chosen.trimCount
      trimAdvance := chosen.trimAdvance
  let lastOutput := if fit == maxLength then
      match last with | none => 4294967295 | some value => value.index-start
    else incomingLast
  return ⟨fit,used,lastOutput,priority,trimCount,trimAdvance,measure start (start+fit)⟩

def Bounded (start finish : Nat) (state : State α) : Prop :=
  (∀ value ∈ state.last, start ≤ value.index ∧ value.index < finish) ∧
  (∀ value ∈ state.candidate, start ≤ value.index ∧ value.index < finish)

theorem initial_bounded (arith : Arithmetic α) (priority : Priority) (start finish : Nat) :
    Bounded start finish (initial arith priority) := by simp [Bounded,initial]

theorem at_break_bounded (arith : Arithmetic α) (limit hyphenWidth : α) (index start finish : Nat)
    (op : Opportunity) (state : State α) (bounds : Bounded start finish state)
    (position : start ≤ index ∧ index < finish) :
    Bounded start finish (atBreak arith limit hyphenWidth index op state) := by
  simp only [atBreak,Id.run,Pure.pure]
  repeat first | exact bounds | split | (solve | simp_all [Bounded])

theorem accumulate_bounded (arith : Arithmetic α) (charAdvance : α) (trimming isSpace : Bool)
    (start finish : Nat) (state : State α) (bounds : Bounded start finish state) :
    Bounded start finish (accumulate arith charAdvance trimming isSpace state) := bounds

theorem iteration_bounded (arith : Arithmetic α) (limit hyphenWidth charAdvance : α)
    (index rescanLimit start finish : Nat) (op : Opportunity) (trimming isSpace : Bool)
    (state : State α) (bounds : Bounded start finish state) (position : start ≤ index ∧ index < finish) :
    Bounded start finish (iteration arith limit hyphenWidth charAdvance index rescanLimit op trimming isSpace state) := by
  have ready := at_break_bounded arith limit hyphenWidth index start finish op state bounds position
  dsimp only [iteration]
  split
  · exact ready
  · exact accumulate_bounded arith charAdvance trimming isSpace start finish _ ready

theorem selected_bounded (last : Break α) (candidate : Option (Break α)) (start finish : Nat)
    (lastBound : start ≤ last.index ∧ last.index < finish)
    (candidateBound : ∀ value ∈ candidate, start ≤ value.index ∧ value.index < finish) :
    start ≤ (selected last candidate).index ∧ (selected last candidate).index < finish := by
  cases candidate with
  | none => exact lastBound
  | some value =>
    have ready := candidateBound value (by simp)
    dsimp [selected]
    split <;> assumption

theorem final_fit_bounded (arith : Arithmetic α) (limit : α) (start maxLength incomingLast : Nat)
    (measure : Nat → Nat → μ) (state : State α) (bounds : Bounded start (start+maxLength) state) :
    (finalize arith limit start maxLength incomingLast measure state).fit ≤ maxLength := by
  have selectedFit : ∀ value, state.last = some value → (selected value state.candidate).index-start ≤ maxLength := by
    intro value member
    have ready := selected_bounded value state.candidate start (start+maxLength)
      (bounds.1 value (by simp [member])) bounds.2
    omega
  simp only [finalize,Id.run,Pure.pure]
  split <;> split <;> cases member : state.last <;> simp_all

theorem final_metric_range (arith : Arithmetic α) (limit : α) (start maxLength incomingLast : Nat)
    (measure : Nat → Nat → μ) (state : State α) :
    (finalize arith limit start maxLength incomingLast measure state).metrics =
      measure start (start+(finalize arith limit start maxLength incomingLast measure state).fit) := by
  simp only [finalize,Id.run,Pure.pure]
  repeat first | rfl | split

theorem rescan_skips_accumulation (arith : Arithmetic α) (limit hyphenWidth charAdvance : α)
    (index rescanLimit : Nat) (op : Opportunity) (trimming isSpace : Bool) (state : State α)
    (rescanning : index < rescanLimit) :
    iteration arith limit hyphenWidth charAdvance index rescanLimit op trimming isSpace state =
      atBreak arith limit hyphenWidth index op state := by
  simp [iteration,rescanning]

theorem suppressed_iteration (arith : Arithmetic α) (limit hyphenWidth charAdvance : α)
    (index rescanLimit : Nat) (trimming isSpace : Bool) (state : State α) :
    iteration arith limit hyphenWidth charAdvance index rescanLimit
      ⟨false,false,false,false,false⟩ trimming isSpace state =
      if state.aborted || index < rescanLimit then state
      else accumulate arith charAdvance trimming isSpace state := by
  simp [iteration,atBreak,Opportunity.present]

theorem suppressed_opportunity (start index : Nat) (priority : Priority) (input : BreakInputs)
    (suppressed : input.suppressAll = true ∨ (input.suppressInitial = true ∧ index ≤ start)) :
    opportunity start index priority input = ⟨false,false,false,false,false⟩ := by
  rcases suppressed with all | initial
  · simp [opportunity,all]
  · simp [opportunity,initial.1,initial.2]

theorem natural_excludes_hyphenation (start index : Nat) (priority : Priority) (input : BreakInputs) :
    (opportunity start index priority input).natural = true →
      (opportunity start index priority input).hyphenated = false := by
  unfold opportunity
  split
  · simp
  · intro natural
    simp only at natural
    simp_all

def integerArithmetic : Arithmetic Int :=
  ⟨0,(·+·),(·-·),fun left right => decide (left ≤ right),fun left right => decide (left > right)⟩

theorem fallback_and_last_output_witness :
    let old : Break Int := ⟨2,0,0,false,.normal⟩
    let later : Break Int := ⟨4,0,0,true,.normal⟩
    let state : State Int := ⟨9,0,0,0,some later,some old,.normal,false⟩
    let result := finalize integerArithmetic 5 0 8 77 (fun first last => last-first) state
    result.fit = 2 ∧ result.usedHyphenation = false ∧ result.lastBreak = 77 ∧ result.metrics = 2 := by decide

end HyphenMeasurementSelection
