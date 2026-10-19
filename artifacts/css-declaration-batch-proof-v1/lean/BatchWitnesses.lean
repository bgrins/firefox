import BatchInterface
namespace BatchWitnesses
open AllOrder BatchOrder BatchStorage BatchInterface
abbrev E := Entry Nat Nat

def cmp : BatchBase.Comparator Nat Nat := ⟨fun a b => decide (a=b), by intro a b h; exact of_decide_eq_true h⟩
def conservative : BatchBase.Comparator Nat Nat := ⟨fun _ _ => false, by intros; contradiction⟩
def op (a b : Nat) : Bool := decide ((a=400 ∨ a=399) ∧ b=394 ∨ a=394 ∧ (b=400 ∨ b=399))
def initial : List E := [⟨190,2001,true⟩,⟨400,2002,false⟩,⟨399,2003,true⟩,⟨394,2004,false⟩,⟨16,2005,true⟩,⟨438,2006,true⟩]
def actions : List E := [⟨400,2009,false⟩,⟨399,2009,false⟩,⟨190,2009,false⟩,⟨16,2009,false⟩]
def expected : List E := directRun op initial actions

def afterWith (fix : Plan → Plan) : List E → List E → List E
  | current, [] => current
  | current, new::rest => afterWith fix (execute current new (fix (BatchBase.planner cmp op initial new))) rest

def badRank (plus : Bool) : Plan → Plan
  | .replace n => .replace (if plus then n+(BatchIndices.earlierRemovals [2,1] n).length else n)
  | .move _ => .append
  | p => p

theorem native_case_admitted : unique initial ∧ unique actions ∧ compatible cmp op actions := by unfold unique compatible; decide

theorem candidate_native_case : numericBatch cmp op initial actions = expected :=
  numeric_batch_refinement cmp op initial actions native_case_admitted.1 native_case_admitted.2.1 native_case_admitted.2.2

theorem ascending_removal_witness :
    afterWith (corrected [2,1]) (BatchIndices.removeIndices initial [1,2]) actions ≠ expected := by decide

theorem omitted_rank_witness :
    afterWith (badRank false) (BatchIndices.removeIndices initial [2,1]) actions ≠ expected := by decide

theorem positive_rank_bounds_witness :
    let beforeLast := afterWith (badRank true) (BatchIndices.removeIndices initial [2,1]) (actions.take 3)
    badRank true (BatchBase.planner cmp op initial (⟨16,2009,false⟩ : E)) = .replace 6 ∧ beforeLast.length = 6 := by decide

def raw : Storage Nat Nat := ⟨initial.map payload,initial.map Entry.important,fun id => decide (id ∈ initial.map Entry.id)⟩
def missingBits : Storage Nat Nat :=
  ⟨BatchIndices.removeIndices raw.declarations [2,1],raw.importance,raw.present⟩

theorem missing_removal_bits_witness :
    let final := rawAfter cmp op initial [2,1] missingBits actions
    final.declarations.length ≠ final.importance.length := by decide

def wrongBitStep (raw : Storage Nat Nat) (new : E) (p : Plan) : Storage Nat Nat :=
  match p with
  | .replace _ => rawStep raw {new with important := !new.important} p
  | _ => rawStep raw new p

def wrongBitsAfter : Storage Nat Nat → List E → Storage Nat Nat
  | r, [] => r
  | r, new::rest => wrongBitsAfter (wrongBitStep r new (corrected [2,1] (BatchBase.planner cmp op initial new))) rest

theorem wrong_replacement_bit_witness :
    (wrongBitsAfter (rawRemove raw [2,1]) actions).importance ≠ expected.map Entry.important := by decide

theorem conservative_comparison_may_publish :
    let xs : List E := [⟨190,9,false⟩]
    anyChange conservative op xs xs = true ∧ numericBatch conservative op xs xs = xs := by
  dsimp only
  constructor
  · decide
  · rw [numeric_batch_refinement conservative op _ _ (by unfold unique; decide) (by unfold unique; decide) (by unfold compatible; decide)]
    decide

theorem mixed_source_mapping_exclusion :
    let xs : List E := [⟨400,9,false⟩,⟨394,9,false⟩]
    ¬compatible cmp op xs ∧ batchIdentity cmp op xs xs ≠ directRun op xs xs := by
  simp only [compatible]; decide

theorem duplicate_source_exclusion :
    let xs : List E := [⟨190,1,false⟩,⟨190,2,false⟩]
    ¬unique xs ∧ batchIdentity cmp op [] xs ≠ directRun op [] xs := by
  simp only [unique]; decide

end BatchWitnesses
