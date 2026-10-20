import Selection
namespace Fragmentation

def pointOffset (i : Input) (p : Opportunity) : Nat :=
  ((i.content.take p.cut).map Atom.extent).sum +
  (i.decorations.map (fun d => if d.cloned then 0 else d.startExtent)).sum

def RegionCandidateAdmitted (i : Input) (region : List Opportunity) : Prop :=
  ∀ p ∈ region, p ∈ i.opportunities ∧ 0 < p.cut ∧ p.cut < i.content.length

instance (i : Input) (region : List Opportunity) : Decidable (RegionCandidateAdmitted i region) := by
  unfold RegionCandidateAdmitted
  infer_instance

def noBelowTop (i : Input) (region : List Opportunity) : Bool :=
  region.all (fun p => pointOffset i p == 0)
def emergencyGuard (i : Input) (region : List Opportunity) : Bool :=
  noBelowTop i region && !finishFits .bothClone i

def available (i : Input) : Nat :=
  i.capacity - (i.decorations.map (decorationExtent .bothClone)).sum

def graphicSlice (i : Input) (region : List Opportunity) : Option Nat :=
  match i.content with
  | [{ kind := .graphic _, extent := remaining }] =>
    if emergencyGuard i region && decide (0 < available i) && decide (0 < remaining)
    then some (min remaining (available i)) else none
  | _ => none

inductive SliceHistory : Nat → List Nat → Prop where
  | finish : SliceHistory 0 []
  | step {remaining used rest} : 0 < used → used ≤ remaining →
      SliceHistory (remaining - used) rest → SliceHistory remaining (used :: rest)

end Fragmentation
