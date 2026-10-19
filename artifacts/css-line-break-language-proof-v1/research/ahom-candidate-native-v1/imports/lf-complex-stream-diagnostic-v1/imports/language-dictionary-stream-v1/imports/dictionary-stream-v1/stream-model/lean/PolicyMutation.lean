import Policy
import WordWitness

namespace LanguageBreak

def policyWitness : PolicyState :=
  ⟨7,startWord witnessProviders {} {} (witnessChunk 1 (.atom 1 "ja") false 0),
   ⟨0,by decide⟩,⟨1,by decide⟩,false,false,false,true⟩

def droppedLineFlush (state : PolicyState) (policy : Fin 5) : List FlushRequest × PolicyState :=
  ([],{state with linePolicy := policy})

theorem dropped_policy_flush_counterexample :
    (droppedLineFlush policyWitness ⟨3,by decide⟩).1 ≠
      (setLinePolicy policyWitness ⟨3,by decide⟩).1 := by decide

theorem pending_contents_counterexample :
    (droppedLineFlush policyWitness ⟨3,by decide⟩).2.transport.buffer.units ≠
      (setLinePolicy policyWitness ⟨3,by decide⟩).2.transport.buffer.units := by decide

end LanguageBreak

def main : IO Unit := do
  let mutant := LanguageBreak.droppedLineFlush LanguageBreak.policyWitness ⟨3,by decide⟩
  let correct := LanguageBreak.setLinePolicy LanguageBreak.policyWitness ⟨3,by decide⟩
  IO.println s!"dropped-policy-flush mutant={mutant.1.length} reference={correct.1.length}"
  if mutant.1 == correct.1 then throw (IO.userError "mutation survived")
