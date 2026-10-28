namespace AdmissionProjection

def project {Bit : Type} (old requested : Bit → Bool) : Bit → Bool :=
  fun bit => old bit && requested bit

theorem exactly_agreed {Bit : Type} (old requested : Bit → Bool) (bit : Bit) :
    project old requested bit = true ↔ old bit = true ∧ requested bit = true := by
  simp [project]

theorem no_added_bit {Bit : Type} (old requested : Bit → Bool) (bit : Bit)
    (h : project old requested bit = true) : old bit = true :=
  (exactly_agreed old requested bit).mp h |>.1

theorem empty_stays_empty {Bit : Type} (requested : Bit → Bool) :
    project (fun _ => false) requested = (fun _ => false) := by
  funext bit
  simp [project]

inductive PositivePath {Node : Type} (edge : Node → Node → Prop) : Node → Node → Prop
  | single {a b} : edge a b → PositivePath edge a b
  | cons {a b c} : edge a b → PositivePath edge b c → PositivePath edge a c

def restrict {Node : Type} (original allowed : Node → Node → Prop) : Node → Node → Prop :=
  fun a b => original a b ∧ allowed a b

theorem positive_path_preserved {Node : Type} {original reduced : Node → Node → Prop}
    (subset : ∀ a b, reduced a b → original a b) {a b : Node}
    (path : PositivePath reduced a b) : PositivePath original a b := by
  induction path with
  | single edge => exact .single (subset _ _ edge)
  | cons edge path ih => exact .cons (subset _ _ edge) ih

def HasCycle {Node : Type} (edge : Node → Node → Prop) : Prop :=
  ∃ a, PositivePath edge a a

theorem restricted_cycle_was_original {Node : Type} (original allowed : Node → Node → Prop)
    (cycle : HasCycle (restrict original allowed)) : HasCycle original := by
  obtain ⟨a, path⟩ := cycle
  exact ⟨a, positive_path_preserved (fun _ _ h => h.1) path⟩

def unionMutant {Bit : Type} (old requested : Bit → Bool) : Bit → Bool :=
  fun bit => old bit || requested bit

def emptyGraph : Unit → Unit → Prop := fun _ _ => False
def addedLoop : Unit → Unit → Prop := fun _ _ => True

theorem added_loop_counterexample : HasCycle addedLoop ∧ ¬ HasCycle emptyGraph := by
  constructor
  · exact ⟨(), .single True.intro⟩
  · rintro ⟨a, path⟩
    cases path with
    | single edge => exact edge
    | cons edge _ => exact edge

end AdmissionProjection
