import Operations

namespace LanguageBreak

def unitOf (value : Nat) : CodeUnit := ⟨value % 65536,Nat.mod_lt value (by decide)⟩

def partitionProviders : StreamProviders :=
  ⟨⟨fun _ => .script .other⟩,
   ⟨fun _ => false,
    fun units word _ _ =>
      if units.map Fin.val = [65,10,65] then [.normal,.none,.normal]
      else if word.val = 1 then List.replicate units.length .normal
      else List.replicate units.length .none,
    fun _ _ _ old => old,fun units => List.replicate units.length false⟩,
   fun unit => 32 ≤ unit.val && unit.val ≤ 126⟩

def fixtureChunk (identity base : Nat) (values : List Nat) (flags : Nat) : Chunk :=
  ⟨identity,.atom 1 "en",some 0,base,.utf16 (values.map unitOf),flags%2==1,flags/2%2==1,
   flags/8%2==1,flags/16%2==1,0,identity,flags/4%2==1⟩

def storeEvent (storage : Coordinate → Glyph) : StreamEvent → Coordinate → Glyph
  | .effect (.breaks _ owner offset values) =>
    (values.zipIdx).foldl (fun result pair => applyAt result ⟨owner,offset+pair.2⟩ pair.1) storage
  | _ => storage

def streamBits (ops : List Operation) (length : Nat) : List BreakKind :=
  let result := runStream partitionProviders ⟨initialStream,[]⟩ ops
  let blank : Coordinate → Glyph := fun _ => ⟨.none,true,false⟩
  let storage := result.events.foldl storeEvent blank
  (List.range length).map fun offset => (storage ⟨0,offset⟩).kind

def lfWhole : List Operation := [.append (fixtureChunk 0 0 [65,10,65] 0),.reset]
def lfSplit : List Operation := [.append (fixtureChunk 0 0 [65] 0),.append (fixtureChunk 1 1 [10,65] 0),.reset]

def nowrapWhole : List Operation :=
  [.word ⟨1,by decide⟩,.append (fixtureChunk 0 0 [65,66,67,32,68] 6),.reset]
def nowrapSplit : List Operation :=
  [.word ⟨1,by decide⟩,.append (fixtureChunk 0 0 [65] 6),.append (fixtureChunk 1 1 [66,67,32,68] 3),.reset]

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem reachable_lf_partition_inequality :
    streamBits lfWhole 3 = [.none,.none,.none] ∧
    streamBits lfSplit 3 = [.none,.none,.normal] := by decide

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem reachable_nowrap_partition_inequality :
    streamBits nowrapWhole 5 = [.normal,.normal,.normal,.normal,.normal] ∧
    streamBits nowrapSplit 5 = [.normal,.none,.none,.normal,.normal] := by decide

end LanguageBreak

def main : IO Unit := do
  IO.println s!"LF whole={repr (LanguageBreak.streamBits LanguageBreak.lfWhole 3)} split={repr (LanguageBreak.streamBits LanguageBreak.lfSplit 3)}"
  IO.println s!"nowrap whole={repr (LanguageBreak.streamBits LanguageBreak.nowrapWhole 5)} split={repr (LanguageBreak.streamBits LanguageBreak.nowrapSplit 5)}"
