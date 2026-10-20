import Placement
namespace Fragmentation

def stages : List Stage := [.strict, .lines, .avoid, .endClone, .bothClone]
def scan (i : Input) : List Stage → Option (Stage × Choice)
  | [] => none
  | s :: ss => match evaluate s i with
    | some c => some (s, c)
    | none => scan i ss

def GridCertificate (i : Input) (ss : List Stage) (s : Stage) (c : Choice) : Prop :=
  ∃ before after, ss = before ++ s :: after ∧
    (∀ earlier ∈ before, ¬ GridFeasible earlier i) ∧ ValidChoice s i c

theorem scan_certificate (i : Input) (ss : List Stage) (s : Stage) (c : Choice)
    (h : scan i ss = some (s, c)) : GridCertificate i ss s c := by
  induction ss with
  | nil => simp [scan] at h
  | cons a rest ih =>
    cases result : evaluate a i with
    | some v =>
      simp [scan, result] at h
      rcases h with ⟨rfl, rfl⟩
      exact ⟨[], rest, rfl, by simp, selected_sound a i v result⟩
    | none =>
      have tail : scan i rest = some (s, c) := by simpa [scan, result] using h
      rcases ih tail with ⟨before, after, eq, failed, valid⟩
      refine ⟨a :: before, after, ?_, ?_, valid⟩
      · simp [eq]
      · intro earlier hm
        rcases List.mem_cons.mp hm with same | old
        · subst earlier; exact (evaluator_none_iff a i).mp result
        · exact failed earlier old

theorem scan_none_iff (i : Input) (ss : List Stage) :
    scan i ss = none ↔ ∀ s ∈ ss, ¬ GridFeasible s i := by
  induction ss with
  | nil => simp [scan]
  | cons a rest ih =>
    cases result : evaluate a i with
    | none => simp [scan, result, ih, (evaluator_none_iff a i).mp result]
    | some c =>
      have possible : GridFeasible a i := by
        apply (grid_evaluator_iff a i).mp
        simp [result]
      simp [scan, result, possible]

def SufficiencyCorrespondence (i : Input) (specSufficient : Stage → Prop) : Prop :=
  ∀ s ∈ stages, specSufficient s ↔ GridFeasible s i

theorem conditional_failure_transfer (i : Input) (specSufficient : Stage → Prop)
    (admission : SufficiencyCorrespondence i specSufficient)
    (s : Stage) (member : s ∈ stages) (failed : evaluate s i = none) :
    ¬ specSufficient s := by
  intro h
  exact (evaluator_none_iff s i).mp failed ((admission s member).mp h)

theorem current_line_partition (b : Nat) (xs : List Atom) (cut : Nat) :
    lineCount b (xs.take cut) + lineCount b (xs.drop cut) = lineCount b xs := by
  have split := List.take_append_drop cut xs
  have sum : ∀ as bs : List Atom, lineCount b (as ++ bs) = lineCount b as + lineCount b bs := by
    intro as bs
    simp [lineCount]
  rw [← sum, split]

end Fragmentation
