import Dictionary
import RecordedFilter

namespace HyphenAstralWitness
open HyphenDictionary HyphenScalarFilter HyphenRecordedFilter

def points : List Nat := [0x10428,97,97,97,97,97]
def units : List Nat := [0xd801,0xdc28,97,97,97,97,97]
def byteMask (i : Nat) : Bool := i == 3
def unitMask (i : Nat) : Bool := (mapMask points byteMask).contains i

theorem provider_marks_pair_end : mapMask points byteMask = [1] := by decide

theorem filter_visits_skip_pair_end :
    (visits (fun _ => .other) (decode units) 0 0).map Visit.index = [0,2,3,4,5,6] := by
  simp [units, decode, high, low, visits, counted]

theorem opportunity_is_not_inside_pair :
    (mapMask points byteMask).map (·+1) = [2] := by decide

theorem mapped_opportunity_is_lost :
    (List.range units.length).map
      (nativeFilter (fun _ => .other) units 2 1 1 unitMask (fun _ => 0)) =
      [0,0,0,0,0,0,0] := by
  simp [nativeFilter, nativeReverseRestore, candidates, units, decode, high, low,
    visits, counted, count, unitMask, provider_marks_pair_end, recordWrites,
    rejectedSuffix, restoreRecorded]
  decide

#print axioms provider_marks_pair_end
#print axioms filter_visits_skip_pair_end
#print axioms opportunity_is_not_inside_pair
#print axioms mapped_opportunity_is_lost
end HyphenAstralWitness

def main : IO Unit := do
  IO.println s!"synthetic-provider-unit-mask={HyphenDictionary.mapMask HyphenAstralWitness.points HyphenAstralWitness.byteMask}"
  IO.println s!"filter-output={(List.range HyphenAstralWitness.units.length).map (HyphenRecordedFilter.nativeFilter (fun _ => .other) HyphenAstralWitness.units 2 1 1 HyphenAstralWitness.unitMask (fun _ => 0))}"
  IO.println "Provider/filter alignment counterexample; shipped-dictionary reachability and normative CSS violation are unproved."
