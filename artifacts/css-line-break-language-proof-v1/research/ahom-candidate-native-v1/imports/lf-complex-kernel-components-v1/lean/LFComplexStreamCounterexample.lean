import Operations

namespace LanguageBreak.LFComplexStream

def leadingUnits : List CodeUnit := [3585,55301,57088,3585]
def suffix : List CodeUnit := [19968,20108]
def text : List CodeUnit := leadingUnits ++ [10] ++ suffix

def segmentation (units : List CodeUnit) : List BreakKind :=
  if units = leadingUnits then [.normal,.normal,.none,.none]
  else if units = suffix then [.normal,.normal]
  else if units = text then [.normal,.normal,.none,.none,.none,.none,.none]
  else List.replicate units.length .none

def providers : StreamProviders :=
  ⟨⟨fun _ => .script .other⟩,
    ⟨fun _ => false,fun units _ _ _ => segmentation units,
      fun _ _ _ old => old,fun units => List.replicate units.length false⟩,
    fun _ => false⟩

def chunk (identity offset : Nat) (units : List CodeUnit) : Chunk :=
  ⟨identity,.atom 13 "th",some 0,offset,.utf16 units,
    false,false,false,false,0,identity,false⟩

def whole : List Operation := [.append (chunk 0 0 text),.reset]
def beforeLF : List Operation :=
  [.append (chunk 0 0 leadingUnits),.append (chunk 1 4 ([10] ++ suffix)),.reset]
def afterLF : List Operation :=
  [.append (chunk 0 0 (leadingUnits ++ [10])),.append (chunk 1 5 suffix),.reset]

def events (ops : List Operation) : List StreamEvent :=
  (runStream providers ⟨initialStream,[]⟩ ops).events

def calls (ops : List Operation) : List (List CodeUnit) :=
  (events ops).filterMap fun event => match event with
    | .segment _ units _ _ _ => some units
    | _ => none

def requests (ops : List Operation) : List (Encoding × List CodeUnit × Nat × Nat × Bool) :=
  (events ops).filterMap fun event => match event with
    | .segment width units word line script => some (width,units,word.val,line.val,script)
    | _ => none

def publish (storage : List BreakKind) (event : StreamEvent) : List BreakKind :=
  match event with
  | .effect (.breaks _ _ offset values) =>
    values.zipIdx.foldl (fun current (kind,index) =>
      if kind = .none then current else current.set (offset+index) kind) storage
  | _ => storage

def glyphs (ops : List Operation) : List BreakKind :=
  (events ops).foldl publish (List.replicate text.length .none)

theorem same_input_units_and_language :
    leadingUnits ++ ([10] ++ suffix) = text ∧
    (leadingUnits ++ [10]) ++ suffix = text ∧
    (chunk 0 0 leadingUnits).language = (chunk 1 4 ([10] ++ suffix)).language := by decide +kernel

theorem complete_provider_admission :
    calls whole = [leadingUnits,suffix] ∧ calls beforeLF = [text] ∧
    calls afterLF = [leadingUnits,suffix] := by decide +kernel

theorem complete_request_arguments :
    requests whole = [(.utf16,leadingUnits,0,0,false),(.utf16,suffix,0,0,false)] ∧
    requests beforeLF = [(.utf16,text,0,0,false)] ∧
    requests afterLF = requests whole := by
  constructor
  · decide +kernel
  constructor <;> decide +kernel

theorem exact_complete_publication :
    glyphs whole = [.none,.normal,.none,.none,.none,.none,.normal] ∧
    glyphs beforeLF = [.none,.normal,.none,.none,.none,.none,.none] ∧
    glyphs afterLF = glyphs whole := by decide +kernel

theorem difference_is_inside_next_line :
    text[4]? = some 10 ∧ text[5]? ≠ some 10 ∧
    (glyphs whole)[6]? ≠ (glyphs beforeLF)[6]? := by decide +kernel

theorem reference_word_provider_length (units : List CodeUnit) :
    (segmentation units).length = units.length := by
  unfold segmentation
  split
  next equal => subst units; rfl
  next different =>
    split
    next equal => subst units; rfl
    next different =>
      split
      next equal => subst units; rfl
      next other => simp

theorem distinct_sinks_share_one_run :
    (chunk 0 0 leadingUnits).sinkIdentity ≠ (chunk 1 4 ([10] ++ suffix)).sinkIdentity ∧
    (chunk 0 0 leadingUnits).sinkOwner = (chunk 1 4 ([10] ++ suffix)).sinkOwner ∧
    (chunk 0 0 leadingUnits).sinkOffset + leadingUnits.length = (chunk 1 4 ([10] ++ suffix)).sinkOffset := by decide +kernel

end LanguageBreak.LFComplexStream
