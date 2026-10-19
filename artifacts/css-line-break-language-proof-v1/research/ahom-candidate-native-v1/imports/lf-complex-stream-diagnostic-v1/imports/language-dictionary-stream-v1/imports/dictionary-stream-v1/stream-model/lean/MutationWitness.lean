import WordWitness

namespace LanguageBreak

def staleImmediate (_p : Providers) (_cache : Cache) (word : WordLanguage) (_tag : Tag) : Bool := word.script

def omittedTail (_p : Providers) (cache : Cache) (old : WordLanguage) (first : Chunk) : TransportState :=
  ⟨cache,flushLanguage old,appendPiece {} (encodePiece first)⟩

def omittedContinuation (state : TransportState) (chunk : Chunk) : TransportState :=
  {state with buffer := appendPiece state.buffer (encodePiece chunk)}

def staleNull (p : Providers) (cache : Cache) (tag : Tag) : Bool :=
  if tag = .absent then cache.value else (resolve p cache tag).1

def jaTag : Tag := .atom 1 "ja"
def jaFirst : Chunk := witnessChunk 1 jaTag false 5

theorem stale_immediate_successful_counterexample :
    staleImmediate witnessProviders {} {} jaTag ≠
      (resolve witnessProviders {} jaTag).1 := by decide

theorem omitted_tail_successful_counterexample :
    (omittedTail witnessProviders {} {} jaFirst).language.script ≠
      (startWord witnessProviders {} {} jaFirst).language.script := by decide

def initialAbsent : TransportState :=
  startWord witnessProviders {} {} (witnessChunk 1 .absent false 5)

theorem omitted_continuation_successful_counterexample :
    (omittedContinuation initialAbsent jaFirst).language.script ≠
      (appendTransport witnessProviders initialAbsent jaFirst).language.script := by decide

def warmCache : Cache := (resolve witnessProviders {} jaTag).2

theorem stale_null_successful_counterexample :
    staleNull witnessProviders warmCache .absent ≠
      (resolve witnessProviders warmCache .absent).1 := by decide

def mutationResults : List (String × Bool × Bool) :=
  [("stale-immediate",staleImmediate witnessProviders {} {} jaTag,
      (resolve witnessProviders {} jaTag).1),
   ("omitted-byte-tail",(omittedTail witnessProviders {} {} jaFirst).language.script,
      (startWord witnessProviders {} {} jaFirst).language.script),
   ("omitted-byte-continuation",(omittedContinuation initialAbsent jaFirst).language.script,
      (appendTransport witnessProviders initialAbsent jaFirst).language.script),
   ("stale-null",staleNull witnessProviders warmCache .absent,
      (resolve witnessProviders warmCache .absent).1)]

end LanguageBreak

def main : IO Unit := do
  for (name,mutant,reference) in LanguageBreak.mutationResults do
    IO.println s!"{name} mutant={mutant} reference={reference}"
    if mutant == reference then throw (IO.userError "mutation survived")
