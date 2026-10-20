import NestedControl
set_option autoImplicit false
namespace LinkEmpty
open PublicCache NestedControl
abbrev Callback := NestedControl.State → Bool × NestedControl.State

def entirely (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (body : Callback) (s : NestedControl.State) : Bool × NestedControl.State :=
  let parsed := body s
  if parsed.1 then
    let checked := WrapperControl.expectExhausted bytes read names parsed.2.stops parsed.2.core
    (checked.1,{parsed.2 with core := checked.2})
  else parsed

def nested (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (body : Callback) (s : NestedControl.State) : Bool × NestedControl.State :=
  match s.core.cursor.pending with
  | none => (false,s)
  | some block =>
    let taken := PublicCleanup.clear s.core
    if s.depth.val ≥ s.limit.val && s.limit.val != 0 then
      (false,{s with core := consume bytes.length read names block taken})
    else
      let parsed := entirely bytes read names body
        {s with core := taken, stops := [closing block], depth := increment s.depth}
      (parsed.1,{parsed.2 with core := finish bytes read names block parsed.2.core, stops := s.stops, depth := decrement parsed.2.depth})

def untilBounded (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (body : Callback) (s : NestedControl.State) : Bool × NestedControl.State :=
  let combined := s.stops ++ extra
  let parsed := entirely bytes read names body {s with stops := combined}
  (parsed.1,{parsed.2 with stops := s.stops, core := RawRecovery.recover bytes read names combined parsed.2.core})

def next (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Option Token × NestedControl.State :=
  let fetched := WrapperNext.native bytes read s.stops.contains names s.core
  (fetched.token,{s with core := fetched.state})

def ident (bytes : List Byte) (s : NestedControl.State) : Option (List Byte) :=
  match s.core.cache with
  | none => none
  | some cache =>
    let input := bytes.drop cache.key
    let value := URLDispatch.native input false
    if ByteLex.selected input && value.kind == .ident then some value.payload else none

def expectIdent (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (accept : List Byte → Bool) (s : NestedControl.State) : Bool × NestedControl.State :=
  let fetched := next bytes read names s
  (fetched.1.isSome && ((ident bytes fetched.2).map accept).getD false,fetched.2)

def expectComma (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let fetched := next bytes read names s
  (fetched.1.isSome && ((fetched.2.core.cache.map fun c => bytes[c.key]? == some 44).getD false),fetched.2)

def emptyValue (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let peek := PublicNext.native bytes read s.stops.contains names s.core
  let whitespace := peek.token.isSome &&
    ((peek.state.cache.map fun c => (bytes[c.key]?.map URLScan.nativeWhitespace).getD false).getD false)
  let start := {s with core := if whitespace then peek.state else WrapperControl.rewind s.core.cursor peek.state}
  untilBounded bytes read names [33,59] (fun input =>
    let fetched := PublicNext.native bytes read input.stops.contains names input.core
    (fetched.token.isNone,{input with core := fetched.state})) start

def itemBody (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let name := expectIdent bytes read names (fun xs => ([45,45] : List Byte).isPrefixOf xs) s
  if !name.1 then name else
  let comma := expectComma bytes read names name.2
  if !comma.1 then comma else emptyValue bytes read names comma.2

def item (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let fetched := next bytes read names s
  let accepted := match fetched.1 with
    | some (.function name) => name.map URLDispatch.lower == [112,97,114,97,109]
    | _ => false
  if accepted then nested bytes read names (itemBody bytes read names) fetched.2
  else (false,fetched.2)

def commaLoop (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) :
    Nat → NestedControl.State → Bool × NestedControl.State
  | 0,s => (false,s)
  | fuel+1,s =>
    let skipped := {s with core := (WrapperSkip.native bytes read names s.core).state}
    let parsed := untilBounded bytes read names [44] (item bytes read names) skipped
    if !parsed.1 then parsed else
    let fetched := next bytes read names parsed.2
    if fetched.1.isNone then (true,fetched.2) else
      if ((fetched.2.core.cache.map fun c => bytes[c.key]? == some 44).getD false)
      then commaLoop bytes read names fuel fetched.2 else (false,fetched.2)

def parse (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (s : NestedControl.State) : Bool × NestedControl.State :=
  let none := expectIdent bytes read names (fun xs => xs.map URLDispatch.lower == [110,111,110,101]) s
  if none.1 then none else
    commaLoop bytes read names (bytes.length+1) {none.2 with core := WrapperControl.rewind s.core.cursor none.2.core}

end LinkEmpty
