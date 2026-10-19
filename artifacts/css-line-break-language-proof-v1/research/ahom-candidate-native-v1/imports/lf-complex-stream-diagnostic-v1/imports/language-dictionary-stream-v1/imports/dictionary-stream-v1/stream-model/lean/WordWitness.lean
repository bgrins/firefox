import Words

namespace LanguageBreak

def witnessProviders : Providers := ⟨fun text =>
  if text = "ja" then .script .jpan
  else if text = "en" then .script .other
  else .invalid⟩

def witnessChunk (owner : Nat) (tag : Tag) (wide : Bool) (offset : Nat) : Chunk :=
  ⟨owner,tag,some (owner+10),offset,
   if wide then .utf16 [⟨65,by decide⟩,⟨176,by decide⟩]
   else .bytes [⟨65,by decide⟩,⟨176,by decide⟩],false,false,false,false,0,owner,false⟩

def witnessJob (owner : Nat) (tag : Tag) (leftWide rightWide : Bool) : WordJob :=
  ⟨owner,witnessChunk owner tag leftWide 5,
   [witnessChunk (owner+1) tag rightWide 7],0,1⟩

def witnessEvents (leftWide rightWide : Bool) : List WordEvent :=
  [.word (witnessJob 1 (.atom 1 "ja") leftWide rightWide),
   .foreign ⟨91,.atom 2 "en"⟩,
   .foreign ⟨92,.atom 3 "bad_tag"⟩,
   .foreign ⟨93,.absent⟩,
   .reset,
   .word (witnessJob 2 (.atom 2 "en") rightWide leftWide),
   .foreign ⟨94,.atom 1 "ja"⟩,
   .word (witnessJob 3 (.atom 1 "ja") leftWide rightWide)]

theorem four_transition_witnesses (leftWide rightWide : Bool) :
    AdmittedEvents witnessProviders {} (witnessEvents leftWide rightWide) := by
  cases leftWide <;> cases rightWide <;>
    simp [AdmittedEvents,witnessEvents,witnessJob,witnessChunk,WordJob.Admitted,UniformChunks,
      StableIdentity,stepWordEvent,runWord,transportChunks,startWord,appendTransport,
      updateLanguage,flushLanguage,resolve,witnessProviders,StoredUnits.decode,Script.isCjk]

theorem constructor_three_word_languages (leftWide rightWide : Bool) :
    ((runWordEvents witnessProviders {} (witnessEvents leftWide rightWide)).1.map WordCall.script) =
      [true,false,true] := by
  cases leftWide <;> cases rightWide <;> decide

theorem typed_offsets_nonvacuous (leftWide rightWide : Bool) :
    ((runWordEvents witnessProviders {} (witnessEvents leftWide rightWide)).1.map
      (fun call => call.pieces.map BufferedPiece.sinkOffset)) = [[5,7],[5,7],[5,7]] := by
  cases leftWide <;> cases rightWide <;> decide

theorem reset_does_not_clear_true_script :
    (stepWordEvent witnessProviders ⟨{},⟨.atom 1 "ja",false,true⟩⟩ .reset).2.language.script = true := rfl

end LanguageBreak
