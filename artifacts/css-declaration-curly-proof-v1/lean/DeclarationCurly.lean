import Std

namespace DeclarationCurly

inductive Delimiter where
  | curly | square | paren
  deriving DecidableEq, Repr

inductive Component where
  | trivia
  | atom (payload : String)
  | function (name : String) (children : List Component)
  | block (kind : Delimiter) (children : List Component)
  deriving Repr

inductive Head where
  | other | curly
  deriving DecidableEq, Repr

def project : Component → Option Head
  | .trivia => none
  | .block .curly _ => some .curly
  | _ => some .other

def significant (values : List Component) : List Head := values.filterMap project

def noCurly (xs : List Head) : Prop := ∀ x ∈ xs, x ≠ .curly

def normalSpec (xs : List Head) : Prop := noCurly xs ∨ xs = [.curly]

def declarationSpec (custom : Bool) (xs : List Head) : Prop := custom = true ∨ normalSpec xs

def startsCurly : List Head → Bool
  | .curly :: _ => true
  | _ => false

def scan (starts atStart : Bool) : List Head → Bool
  | [] => true
  | x :: xs =>
      let invalid := if x = .curly then !starts || !atStart else starts
      if invalid then false else scan starts false xs

def fullCheck (xs : List Head) : Bool := scan (startsCurly xs) true xs

theorem scan_false (atStart : Bool) (xs : List Head) :
    scan false atStart xs = true ↔ noCurly xs := by
  induction xs generalizing atStart with
  | nil => simp [scan, noCurly]
  | cons x xs ih =>
    cases x <;> simp [scan, noCurly, ih, noCurly] at *

theorem scan_true_after (xs : List Head) :
    scan true false xs = true ↔ xs = [] := by
  cases xs with
  | nil => simp [scan]
  | cons x xs => cases x <;> simp [scan]

theorem full_refinement (xs : List Head) :
    fullCheck xs = true ↔ normalSpec xs := by
  cases xs with
  | nil => simp [fullCheck, scan, normalSpec, noCurly]
  | cons x xs =>
    cases x with
    | other => simp [fullCheck, startsCurly, scan, scan_false, normalSpec, noCurly]
    | curly => simp [fullCheck, startsCurly, scan, scan_true_after, normalSpec, noCurly]

theorem component_refinement (values : List Component) :
    fullCheck (significant values) = true ↔ normalSpec (significant values) :=
  full_refinement _

theorem projection_append (a b : List Component) :
    significant (a ++ b) = significant a ++ significant b := by
  simp [significant]

theorem trivia_irrelevant (a b : List Component) :
    significant (a ++ .trivia :: b) = significant (a ++ b) := by
  simp only [significant, List.filterMap_append]
  rfl

theorem function_interior_irrelevant (name : String) (a b : List Component) :
    significant [.function name a] = significant [.function name b] := by
  rfl

theorem square_interior_irrelevant (a b : List Component) :
    significant [.block .square a] = significant [.block .square b] := by
  rfl

theorem curly_interior_irrelevant (a b : List Component) :
    significant [.block .curly a] = significant [.block .curly b] := by
  rfl

theorem whole_curly_valid (children : List Component) :
    fullCheck (significant [.block .curly children]) = true := by
  rfl

theorem mixed_curly_invalid (children : List Component) (atom : String) :
    fullCheck (significant [.atom atom, .block .curly children]) = false := by
  rfl

theorem repeated_curly_invalid (a b : List Component) :
    fullCheck (significant [.block .curly a, .block .curly b]) = false := by
  rfl

theorem custom_exception (xs : List Head) : declarationSpec true xs := by
  simp [declarationSpec]

structure Recovery where
  consumed : List Head
  remaining : List Head
  deriving Repr

def Recovery.whole (r : Recovery) := r.consumed ++ r.remaining

def suffixCheck (r : Recovery) : Bool :=
  scan (startsCurly r.whole) r.consumed.isEmpty r.remaining

def rewindCheck (r : Recovery) : Bool := fullCheck r.whole

theorem arbitrary_recovery (r : Recovery) :
    rewindCheck r = true ↔ normalSpec r.whole := full_refinement _

theorem arbitrary_cursor_independence (r s : Recovery) (same : r.whole = s.whole) :
    rewindCheck r = rewindCheck s := by
  simp [rewindCheck, same]

theorem suffix_only_counterexample :
    suffixCheck ⟨[.other, .curly], []⟩ = true ∧
    ¬ normalSpec [.other, .curly] := by
  simp [suffixCheck, scan, normalSpec, noCurly]

theorem rewind_counterexample_repaired :
    rewindCheck ⟨[.other, .curly], []⟩ = false := by rfl

def rejectWholeMutant (xs : List Head) := scan false true xs

theorem reject_whole_mutant_witness :
    rejectWholeMutant [.curly] = false ∧ fullCheck [.curly] = true := by decide

def ignoreStructureMutant (_xs : List Head) := true

theorem ignore_structure_mutant_witness :
    ignoreStructureMutant [.other, .curly] = true ∧
    fullCheck [.other, .curly] = false := by decide

def queryRetained (saved seen : Bool) : Bool := saved || seen

theorem disabled_after_positive (freshScanSeen : Bool) :
    queryRetained true freshScanSeen = true := by simp [queryRetained]

theorem failed_epoch (seen : Bool) : queryRetained false seen = seen := by
  simp [queryRetained]

def gateway (r : Recovery) (saved seen arbitraryValid : Bool) : Bool :=
  queryRetained saved seen && rewindCheck r && arbitraryValid

theorem gateway_refinement (r : Recovery) (saved seen arbitraryValid : Bool) :
    gateway r saved seen arbitraryValid = true ↔
    queryRetained saved seen = true ∧ normalSpec r.whole ∧ arbitraryValid = true := by
  simp only [gateway, Bool.and_eq_true, arbitrary_recovery]
  exact and_assoc

theorem lost_positive_query_mutant_witness :
    gateway ⟨[.other], []⟩ true false true = true ∧
    gateway ⟨[.other], []⟩ false false true = false := by decide

theorem invalid_never_published (r : Recovery) (saved seen arbitraryValid : Bool)
    (bad : ¬ normalSpec r.whole) : gateway r saved seen arbitraryValid = false := by
  cases h : gateway r saved seen arbitraryValid with
  | false => rfl
  | true => exact False.elim (bad ((gateway_refinement r saved seen arbitraryValid).mp h).2.1)

def ordinaryFastPath (parserSuccess observed : Bool) : Bool := parserSuccess && !observed

theorem ordinary_success_unchanged : ordinaryFastPath true false = true := by rfl

def scanSteps (starts atStart : Bool) : List Head → Nat
  | [] => 0
  | x :: xs =>
      let invalid := if x = .curly then !starts || !atStart else starts
      1 + if invalid then 0 else scanSteps starts false xs

theorem scan_step_bound (starts atStart : Bool) (xs : List Head) :
    scanSteps starts atStart xs ≤ xs.length := by
  induction xs generalizing starts atStart with
  | nil => simp [scanSteps]
  | cons x xs ih =>
    have h0 := ih false false
    have h1 := ih true false
    cases x <;> cases starts <;> cases atStart <;> simp [scanSteps] <;> omega

theorem noCurly_append (a b : List Head) : noCurly (a ++ b) ↔ noCurly a ∧ noCurly b := by
  constructor
  · intro h
    exact ⟨fun x hx => h x (List.mem_append_left _ hx), fun x hx => h x (List.mem_append_right _ hx)⟩
  · rintro ⟨ha, hb⟩ x hx
    rcases List.mem_append.mp hx with h | h
    · exact ha x h
    · exact hb x h

end DeclarationCurly
