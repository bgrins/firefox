import Lean
import FlushRange

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
private def piece (j : Json) : Except String BufferedPiece := do
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
private def execute (input : Json) : Except String Json := do
  let state ← field input "state"
  let units ← (← numbers state "units").mapM (fun n => bounded n 65536)
  let pieces ← (← (← field state "pieces").getArr?).toList.mapM piece
  let language : WordLanguage := ⟨← tag state,← readBool state "mixed",← readBool state "script"⟩
  let transport : TransportState := ⟨{},language,⟨pieces,units⟩⟩
  let policy : PolicyState := ⟨← nat state "breaker",transport,← bounded (← nat state "word") 3,
    ← bounded (← nat state "line") 5,← readBool state "break_here",← readBool state "after_space",
    ← readBool state "continuation",← readBool state "might"⟩
  let limits : AuxLimits := ⟨← bounded (← nat state "limit_word") 256,
    ← bounded (← nat state "limit_start") 256,← bounded (← nat state "limit_end") 256⟩
  let provider ← field input "providers"
  let segment ← (← numbers provider "segment").mapM kind
  let hyphen ← (← numbers provider "hyphen").mapM kind
  let caps ← (← (← field provider "caps").getArr?).toList.mapM Json.getBool?
  let present ← readBool provider "has_hyphenator"
  let providers : BreakProviders := ⟨fun _ => present,fun _ _ _ _ => segment,
    fun _ _ _ _ => hyphen,fun _ => caps⟩
  let result := flushBuffered providers policy limits
  return Json.mkObj [("id",← field input "id"),("events",toJson (result.events.map event)),
    ("cleared",toJson (result.state.transport.buffer.units.isEmpty && result.state.transport.buffer.pieces.isEmpty &&
      result.state.transport.language.current == .absent && !result.state.transport.language.mixed &&
      !result.state.mightBreak && !result.state.continuation)),
    ("script",toJson result.state.transport.language.script),
    ("after_space",toJson result.state.afterSpace),("break_here",toJson result.state.breakHere)]

def main (args : List String) : IO Unit := do
  let path := args.headD ""
  let contents ← IO.FS.readFile path
  let stdout ← IO.getStdout
  for line in contents.splitOn "\n" do
    if !line.isEmpty then
      match Json.parse line >>= execute with
      | .ok result => stdout.putStrLn result.compress
      | .error reason => throw (IO.userError reason)
