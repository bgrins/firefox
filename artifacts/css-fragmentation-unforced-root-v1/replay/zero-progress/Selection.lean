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

def SufficiencyCorrespondence (i : Input) (specSufficient : Stage → Prop) : Prop :=
  ∀ s ∈ stages, specSufficient s ↔ GridFeasible s i

end Fragmentation
