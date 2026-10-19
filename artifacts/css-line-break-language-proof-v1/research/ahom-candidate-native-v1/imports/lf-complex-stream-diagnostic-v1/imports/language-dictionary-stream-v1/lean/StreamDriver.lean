import Lean
import Operations

open Lean LanguageBreak

private def field (j : Json) (name : String) : Except String Json := j.getObjVal? name
private def nat (j : Json) (name : String) : Except String Nat := do (← field j name).getNat?
private def readBool (j : Json) (name : String) : Except String Bool := do (← field j name).getBool?
private def numbers (j : Json) (name : String) : Except String (List Nat) := do
  let values ← (← field j name).getArr?
  values.toList.mapM Json.getNat?
private def bounded (n size : Nat) : Except String (Fin size) :=
  if h : n < size then .ok ⟨n,h⟩ else .error "bounded value out of range"
private def kind : Nat → Except String BreakKind
  | 0 => .ok .none | 1 => .ok .normal | 2 => .ok .hyphen | 3 => .ok .emergency
  | _ => .error "invalid break kind"
private def kindNat : BreakKind → Nat
  | .none => 0 | .normal => 1 | .hyphen => 2 | .emergency => 3
private def tag (j : Json) : Except String Tag := do
  if ← readBool j "absent" then return .absent
  return .atom (← nat j "tag_id") (← (← field j "tag").getStr?)
private def unusedPiece (j : Json) : Except String BufferedPiece := do
  let units ← (← numbers j "units").mapM (fun n => bounded n 65536)
  let ownerId ← nat j "owner"
  let hasSink ← readBool j "has_sink"
  let owner := if hasSink then some ownerId else none
  return ⟨← nat j "source_owner",← tag j,owner,← nat j "offset",units,
    ← readBool j "initial",← readBool j "inside",← readBool j "capitalization",← readBool j "hyphenation",
    ← nat j "chunk_offset",← nat j "identity",false⟩
private def ints (values : List Nat) : Json := toJson values
private def tagJson : Tag → Json
  | .absent => Json.null
  | .atom id text => Json.mkObj [("identity",toJson id),("text",toJson text)]
private def event : FlushEvent → Json
  | .segmentation units word line script => Json.mkObj [("kind",toJson "segment"),
      ("units",ints (units.map Fin.val)),("word",toJson word.val),("line",toJson line.val),("script",toJson script)]
  | .hyphenatorLookup t => Json.mkObj [("kind",toJson "lookup"),("tag",tagJson t)]
  | .hyphenation t units limits old => Json.mkObj [("kind",toJson "hyphenate"),("tag",tagJson t),
      ("units",ints (units.map Fin.val)),("limits",ints [limits.word.val,limits.start.val,limits.finish.val]),
      ("old",ints (old.map kindNat))]
  | .capitalization units => Json.mkObj [("kind",toJson "capitalize"),("units",ints (units.map Fin.val))]
  | .breaks identity owner offset values => Json.mkObj [("kind",toJson "B"),("identity",toJson identity),
      ("owner",toJson owner),("offset",toJson offset),("values",ints (values.map kindNat))]
  | .capitals identity owner offset values => Json.mkObj [("kind",toJson "C"),("identity",toJson identity),
      ("owner",toJson owner),("offset",toJson offset),("values",toJson values)]

private def readTag (j : Json) : Except String Tag := tag j
private def units (j : Json) (name : String) : Except String (List CodeUnit) := do
  (← numbers j name).mapM (fun n => bounded n 65536)
private def kinds (j : Json) (name : String) : Except String (List BreakKind) := do
  (← numbers j name).mapM kind
private def array (j : Json) (name : String) : Except String (List Json) := do
  return (← (← field j name).getArr?).toList
private def text (j : Json) (name : String) : Except String String := do
  (← field j name).getStr?

private def readChunk (j : Json) : Except String Chunk := do
  let values ← numbers j "units"
  let width ← nat j "width"
  let storage ← if width = 8 then
    StoredUnits.bytes <$> values.mapM (fun n => bounded n 256)
    else StoredUnits.utf16 <$> values.mapM (fun n => bounded n 65536)
  let flags ← nat j "flags"
  let owner ← nat j "owner"
  let present ← readBool j "has_sink"
  return ⟨← nat j "source_owner",← readTag j,if present then some owner else none,
    ← nat j "base",storage,flags%2==1,flags/2%2==1,flags/8%2==1,flags/16%2==1,
    0,← nat j "identity",flags/4%2==1⟩

private def readLimits (j : Json) : Except String AuxLimits := do
  return ⟨← bounded (← nat j "word") 256,← bounded (← nat j "start") 256,← bounded (← nat j "end") 256⟩

private def operation (j : Json) : Except String Operation := do
  match ← text j "op" with
  | "A" => return .append (← readChunk j)
  | "B" => return .word (← bounded (← nat j "value") 3)
  | "T" => return .line (← bounded (← nat j "value") 5)
  | "S" => return .limits (← readLimits j)
  | "C" => return .continuation (← readBool j "value")
  | "W" => return .whitespace (← readBool j "inside")
  | "R" => return .reset
  | _ => throw "unrecognized operation"

private def stateJson (state : StreamState) : Json :=
  let p := state.policy
  let lang := p.transport.language
  let itemJson (piece : BufferedPiece) : Json := Json.mkObj [
    ("identity",if piece.sinkOwner.isSome then toJson piece.sinkIdentity else Json.null),
    ("owner",toJson piece.sinkOwner),("offset",toJson piece.sinkOffset),
    ("chunk_offset",toJson piece.chunkOffset),("length",toJson piece.units.length),
    ("flags",toJson ((if piece.suppressInitial then 1 else 0)+(if piece.suppressInside then 2 else 0)+
      (if piece.skipNoBreaks then 4 else 0)+(if piece.capitalization then 8 else 0)+(if piece.hyphenation then 16 else 0)))]
  Json.mkObj [("script",toJson lang.script),("mixed",toJson lang.mixed),("language",tagJson lang.current),
    ("might",toJson p.mightBreak),("continuation",toJson p.continuation),
    ("after_space",toJson p.afterSpace),("break_here",toJson p.breakHere),
    ("word",toJson p.wordPolicy.val),("line",toJson p.linePolicy.val),
    ("units",ints (p.transport.buffer.units.map Fin.val)),
    ("items",toJson (p.transport.buffer.pieces.map itemJson)),
    ("limits",ints [state.limits.word.val,state.limits.start.val,state.limits.finish.val])]

private def streamEvent : StreamEvent → Json
  | .resolve tag => Json.mkObj [("kind",toJson "resolve"),("tag",tagJson tag)]
  | .segment width units word line script => Json.mkObj [("kind",toJson "segment"),
      ("width",toJson (if width == .latin1 then 8 else 16)),("units",ints (units.map Fin.val)),
      ("word",toJson word.val),("line",toJson line.val),("script",toJson script)]
  | .effect value => event value

private def prepareProviders (input : Json) : Except String StreamProviders := do
  let locales ← (← array input "locales").mapM fun row => do
    let status ← text row "status"
    let script ← text row "script"
    let resolution : Resolution := if status = "invalid" then .invalid else if status = "error" then .providerError
      else .script (match script with | "Hans" => .hans | "Hant" => .hant | "Jpan" => .jpan | "Hrkt" => .hrkt | _ => .other)
    return (← text row "tag",resolution)
  let segments ← (← array input "segments").mapM fun row => do
    return ((← units row "units",← nat row "word",← nat row "line",← readBool row "script"),← kinds row "values")
  let hyphens ← (← array input "hyphens").mapM fun row => do
    return ((← readTag row,← units row "units",← readLimits row,← kinds row "old"),← kinds row "values")
  let capitals ← (← array input "capitals").mapM fun row => do
    let values ← (← array row "values").mapM Json.getBool?
    return (← units row "units",values)
  let nonbreakable ← numbers input "nonbreakable"
  let breaks : BreakProviders := {
    hasHyphenator := fun tag => match tag with | .atom _ text => text == "en" || text == "en-US" | _ => false
    segment := fun units word line script => ((segments.find? (fun row => row.1 == (units,word.val,line.val,script))).map Prod.snd).getD []
    hyphenate := fun tag units limits old => ((hyphens.find? (fun row => row.1 == (tag,units,limits,old))).map Prod.snd).getD []
    capitalize := fun units => ((capitals.find? (fun row => row.1 == units)).map Prod.snd).getD [] }
  return ⟨⟨fun text => ((locales.find? (fun row => row.1 == text)).map Prod.snd).getD .invalid⟩,
    breaks,fun unit => nonbreakable.contains unit.val⟩

private def execute (providers : StreamProviders) (cache : Cache) (input : Json) : Except String (Json × Cache) := do
  let ops ← (← array input "operations").mapM operation
  let mut state := initialStream cache
  let mut steps : List Json := []
  for op in ops do
    let next := stepStream providers state op
    state := next.state
    steps := steps ++ [Json.mkObj [("state",stateJson state),("events",toJson (next.events.map streamEvent))]]
  return (Json.mkObj [("id",← field input "id"),("steps",toJson steps)],state.policy.transport.cache)

def main (args : List String) : IO Unit := do
  let contents ← IO.FS.readFile (args.headD "")
  let input ← match Json.parse contents with | .ok j => pure j | .error e => throw (IO.userError e)
  let providers ← match prepareProviders input with | .ok p => pure p | .error e => throw (IO.userError e)
  let rows ← match array input "cases" with | .ok rows => pure rows | .error e => throw (IO.userError e)
  let mut cache : Cache := {}
  let stdout ← IO.getStdout
  for row in rows do
    match execute providers cache row with
    | .ok (result,next) => cache := next; stdout.putStrLn result.compress
    | .error e => throw (IO.userError e)
