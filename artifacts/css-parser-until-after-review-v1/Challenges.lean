import AfterChallenges
set_option autoImplicit false
namespace IndependentAfter
open PublicCache

def read (bytes : List Byte) (p : Nat) : Lexeme :=
  UntilAfter.delimiterLexeme (bytes[p]?.getD 59) p

theorem progress_inhabited (bytes : List Byte) :
    PublicCleanup.Progress bytes.length (read bytes) := by
  intro p _
  simp [read, UntilAfter.delimiterLexeme]

theorem delimiter_law_inhabited (bytes : List Byte) :
    UntilAfter.DelimiterLaw bytes (read bytes) := by
  intro p b hb _
  simp [read, hb]

def initial : NestedControl.State :=
  ⟨PublicHistory.begin [] (constructor ⟨none,none⟩), [], 0, 75⟩
def initialRef : NestedControl.Reference :=
  ⟨PublicHistory.initialReference (constructor ⟨none,none⟩), [], 0, 75⟩
def body (_ : List Byte) : WrapperControl.Program := .callback [] (fun _ => true)

theorem admitted_full_refinement :
    (UntilAfter.native [59] (read [59]) [] [59] false body initial).1 =
      (UntilAfter.reference [59] (read [59]) [59] false body initialRef).1 ∧
    NestedControl.Aligned (read [59]) []
      (UntilAfter.native [59] (read [59]) [] [59] false body initial).2
      (UntilAfter.reference [59] (read [59]) [59] false body initialRef).2 := by
  apply UntilAfter.after_refines
  · exact ⟨PublicHistory.constructor_begin _ _ _, rfl, rfl, rfl⟩
  · exact progress_inhabited _
  · intro b hb
    have eq : b = 59 := by simpa using hb
    subst b
    exact Or.inr (Or.inl rfl)
  · exact delimiter_law_inhabited _

theorem admitted_path_actually_consumes :
    (UntilAfter.native [59] (read [59]) [] [59] false body initial).1 = true ∧
    (UntilAfter.native [59] (read [59]) [] [59] false body initial).2.core.cursor.position = 1 := by
  decide +kernel

def stuck (_ : Nat) : Lexeme := ⟨.other,⟨0,none⟩⟩
theorem missing_progress_defeats_boundary :
    RawRecovery.stopped [97,59] [59]
      (RawRecovery.recover [97,59] stuck [] [59] initial.core).cursor = false := by
  decide +kernel

theorem empty_requested_drains_to_eof :
    AfterChallenges.run [97,59] [] [] false 0 = (false,2,none,false) := by
  decide +kernel

theorem closing_is_not_an_admitted_requested_byte :
    ¬ UntilAfter.requested 41 ∧ ¬ UntilAfter.requested 93 ∧ ¬ UntilAfter.requested 125 := by
  unfold UntilAfter.requested
  decide +kernel

theorem duplicate_requested_has_set_semantics :
    AfterChallenges.run [59,97] [] [59,59] false 0 =
      AfterChallenges.run [59,97] [] [59] false 0 := by
  decide +kernel

theorem outer_curly_prevents_inner_annotation_walk :
    AfterChallenges.run [123,118,97,114,40,41,125] [123] [123] false 0 =
      (false,0,none,false) := by
  decide +kernel

theorem stop_success_still_consumes :
    (UntilAfter.native [59] (read [59]) [] [59] true body initial).1 = true ∧
    (UntilAfter.native [59] (read [59]) [] [59] true body initial).2.core.cursor.position = 1 := by
  decide +kernel

end IndependentAfter
#print axioms IndependentAfter.progress_inhabited
#print axioms IndependentAfter.delimiter_law_inhabited
#print axioms IndependentAfter.admitted_full_refinement
#print axioms IndependentAfter.admitted_path_actually_consumes
#print axioms IndependentAfter.missing_progress_defeats_boundary
#print axioms IndependentAfter.empty_requested_drains_to_eof
#print axioms IndependentAfter.closing_is_not_an_admitted_requested_byte
#print axioms IndependentAfter.duplicate_requested_has_set_semantics
#print axioms IndependentAfter.outer_curly_prevents_inner_annotation_walk
#print axioms IndependentAfter.stop_success_still_consumes
