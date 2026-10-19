import FlushRange

namespace LanguageBreak

inductive Encoding where
  | latin1 | utf16
  deriving DecidableEq, Repr

inductive StreamEvent where
  | resolve (tag : Tag)
  | segment (width : Encoding) (units : List CodeUnit) (word : Fin 3) (line : Fin 5) (script : Bool)
  | effect (event : FlushEvent)
  deriving DecidableEq, Repr

structure StreamProviders where
  locale : Providers
  breaks : BreakProviders
  nonbreakable : CodeUnit → Bool

structure StreamState where
  policy : PolicyState
  limits : AuxLimits
  deriving DecidableEq, Repr

structure StreamResult where
  state : StreamState
  events : List StreamEvent := []
  deriving DecidableEq, Repr

def flushEvent : FlushEvent → StreamEvent
  | .segmentation units word line script => .segment .utf16 units word line script
  | event => .effect event

def flushStream (providers : StreamProviders) (state : StreamState) : StreamResult :=
  let result := flushBuffered providers.breaks state.policy state.limits
  ⟨{state with policy := result.state},result.events.map flushEvent⟩

def updateStreamLanguage (providers : StreamProviders) (state : StreamState) (tag : Tag) : StreamResult :=
  let previous := state.policy.transport
  let updated := updateLanguage providers.locale previous.cache previous.language tag
  let events := if previous.language.current = .absent then [StreamEvent.resolve tag] else []
  ⟨{state with policy := {state.policy with transport := {previous with cache := updated.1,language := updated.2}}},events⟩

def repeatLanguage (providers : StreamProviders) (tag : Tag) : Nat → StreamResult → StreamResult
  | 0,result => result
  | n+1,result =>
    let next := updateStreamLanguage providers result.state tag
    repeatLanguage providers tag n ⟨next.state,result.events++next.events⟩

def asciiSpace (unit : CodeUnit) : Bool := unit.val == 9 || unit.val == 13 || unit.val == 32

def pieceOf (chunk : Chunk) (start length : Nat) : BufferedPiece :=
  { encodePiece chunk with units := (chunk.storage.decode.drop start).take length, chunkOffset := start,sinkOffset := chunk.sinkOffset+start }

def addBuffered (state : StreamState) (piece : BufferedPiece) : StreamState :=
  {state with policy := {state.policy with transport := {state.policy.transport with buffer := appendPiece state.policy.transport.buffer piece}}}

def setAt (values : List α) (offset : Nat) (value : α) : List α := values.set offset value

def replaceSlice (values : List α) (offset : Nat) (replacement : List α) : List α :=
  values.take offset ++ replacement ++ values.drop (offset+replacement.length)

structure Scan where
  state : StreamState
  position : Nat
  wordStart : Nat
  might : Bool := false
  breaks : List BreakKind
  caps : List Bool
  events : List StreamEvent := []
  finished : Bool := false
  deriving DecidableEq, Repr

def directHyphenate (providers : StreamProviders) (tag : Tag) (units : List CodeUnit)
    (limits : AuxLimits) (old : List BreakKind) : List BreakKind × List StreamEvent :=
  if providers.breaks.hasHyphenator tag then
    (providers.breaks.hyphenate tag units limits old,
      [.effect (.hyphenation tag units limits old)])
  else (old,[])

def segmentImmediate (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (scan : Scan) (units : List CodeUnit) : Scan :=
  let resolved := resolve providers.locale scan.state.policy.transport.cache chunk.language
  let state := {scan.state with policy := {scan.state.policy with transport := {scan.state.policy.transport with cache := resolved.2}}}
  let values := providers.breaks.segment units state.policy.wordPolicy state.policy.linePolicy resolved.1
  let values := values.set 0 (scan.breaks[scan.wordStart]?.getD .none)
  {scan with state := state,breaks := replaceSlice scan.breaks scan.wordStart values,events := scan.events ++ [.resolve chunk.language,.segment width units state.policy.wordPolicy state.policy.linePolicy resolved.1]}

def completeImmediate (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (scan : Scan) : Scan :=
  let units := (chunk.storage.decode.drop scan.wordStart).take (scan.position-scan.wordStart)
  let segmented := if chunk.suppressInside then scan else
    if scan.state.policy.linePolicy.val = 4 then
      {scan with breaks := replaceSlice scan.breaks scan.wordStart (List.replicate units.length .normal)}
    else if scan.might then segmentImmediate providers width chunk scan units else scan
  let hyphenated := if !chunk.suppressInside && width == .utf16 && chunk.hyphenation && chunk.language != .absent then
    let old := (segmented.breaks.drop scan.wordStart).take units.length
    let result := directHyphenate providers chunk.language units scan.state.limits old
    {segmented with breaks := replaceSlice segmented.breaks scan.wordStart result.1,events := segmented.events++result.2}
    else segmented
  if !scan.state.policy.continuation && chunk.capitalization then
    {hyphenated with caps := replaceSlice hyphenated.caps scan.wordStart (providers.breaks.capitalize units),events := hyphenated.events++[.effect (.capitalization units)]}
  else hyphenated

def scanStep (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (scan : Scan) : Scan :=
  let units := chunk.storage.decode
  let unit := units[scan.position]?.getD ⟨0,by decide⟩
  let space := asciiSpace unit
  let breakableSpace := space && !chunk.suppressInside
  let current := scan.state.policy
  let initial : BreakKind := if current.breakHere || (current.afterSpace && !breakableSpace) ||
      current.wordPolicy.val == 1 || current.linePolicy.val == 4 then .normal else .none
  let values := if chunk.sinkOwner.isSome && (width == .latin1 || !noBreaks)
    then setAt scan.breaks scan.position initial else scan.breaks
  let next := {scan with breaks := values,state := {scan.state with policy := {current with breakHere := false,afterSpace := breakableSpace}}}
  if space || (width == .utf16 && unit.val == 10) then
    let completed := if scan.position > scan.wordStart && chunk.sinkOwner.isSome
      then completeImmediate providers width chunk next else next
    {completed with position := scan.position+1,wordStart := scan.position+1,might := false,state := {completed.state with policy := {completed.state.policy with continuation := false}}}
  else
    let might := scan.might || !providers.nonbreakable unit
    if scan.position+1 < units.length then
      {next with position := scan.position+1,might := might}
    else
      let piece := pieceOf chunk scan.wordStart (units.length-scan.wordStart)
      let state := addBuffered {next.state with policy := {next.state.policy with mightBreak := might}} piece
      let updated := updateStreamLanguage providers state chunk.language
      {next with state := updated.state,events := next.events++updated.events,position := scan.wordStart+1,might := might,finished := true}

def scanLoop (providers : StreamProviders) (width : Encoding) (chunk : Chunk) (noBreaks : Bool) :
    Nat → Scan → Scan
  | 0,scan => scan
  | n+1,scan =>
    if scan.finished || scan.position ≥ chunk.storage.decode.length then scan
    else scanLoop providers width chunk noBreaks n (scanStep providers width chunk noBreaks scan)

def lastSpaceStart (units : List CodeUnit) (start : Nat) : Nat :=
  ((List.range units.length).filter (fun i => start ≤ i && asciiSpace (units[i]?.getD ⟨0,by decide⟩))).getLast?.getD start

def publishImmediate (chunk : Chunk) (start : Nat) (noBreaks : Bool) (scan : Scan) : StreamResult :=
  let writes := match chunk.sinkOwner with
    | none => []
    | some owner =>
      let length := scan.position-start
      let breaks := if noBreaks then [] else
        [StreamEvent.effect (.breaks chunk.sinkIdentity owner (chunk.sinkOffset+start) ((scan.breaks.drop start).take length))]
      let caps := if chunk.capitalization then
        [StreamEvent.effect (.capitals chunk.sinkIdentity owner (chunk.sinkOffset+start) ((scan.caps.drop start).take length))] else []
      breaks++caps
  ⟨scan.state,scan.events++writes⟩

def scanRemainder (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (start : Nat) (input : StreamResult) : StreamResult :=
  let units := chunk.storage.decode
  let policy := input.state.policy
  let noBreaks := chunk.sinkOwner.isNone ||
    (chunk.suppressInitial && chunk.suppressInside && chunk.skipNoBreaks && !policy.breakHere && !policy.afterSpace)
  let needCaps := chunk.sinkOwner.isSome && chunk.capitalization
  let position := if noBreaks && !needCaps then lastSpaceStart units start else start
  let lookup := if width == .utf16 && chunk.hyphenation && !chunk.suppressInside && chunk.language != .absent
    then [StreamEvent.effect (.hyphenatorLookup chunk.language)] else []
  let initial : Scan := ⟨input.state,position,position,false,List.replicate units.length .none,
    List.replicate units.length false,input.events++lookup,false⟩
  let result := scanLoop providers width chunk noBreaks units.length initial
  publishImmediate chunk start noBreaks result

def extendPrefix (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) : StreamResult :=
  let leading := chunk.storage.decode.takeWhile (fun unit => !asciiSpace unit)
  if leading.isEmpty then ⟨state,[]⟩ else
    let buffered := addBuffered state (pieceOf chunk 0 leading.length)
    let buffered := {buffered with policy := {buffered.policy with mightBreak := state.policy.mightBreak || leading.any (fun unit => !providers.nonbreakable unit)}}
    let count := if width == .utf16 then leading.length else 1
    repeatLanguage providers chunk.language count ⟨buffered,[]⟩

def appendCore (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) : StreamResult :=
  let units := chunk.storage.decode
  if units.isEmpty then ⟨state,[]⟩
  else if state.policy.transport.buffer.units.isEmpty then
    scanRemainder providers width chunk 0 ⟨state,[]⟩
  else
    let leading := units.takeWhile (fun unit => !asciiSpace unit)
    let next := extendPrefix providers width chunk state
    if leading.length = units.length then next
    else
      let flushed := flushStream providers next.state
      scanRemainder providers width chunk leading.length ⟨flushed.state,next.events++flushed.events⟩

def appendStream (providers : StreamProviders) (chunk : Chunk) (state : StreamState) : StreamResult :=
  match chunk.storage with
  | .utf16 _ => appendCore providers .utf16 chunk state
  | .bytes _ => if chunk.capitalization || chunk.hyphenation
    then appendCore providers .utf16 chunk.widen state else appendCore providers .latin1 chunk state

end LanguageBreak
