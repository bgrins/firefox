import DictionaryManagerSequence

open HyphenDictionaryManager HyphenDictionaryFallback

def encodeKey (text : String) : Key := text.toUTF8.data.toList

def text (key : Key) : String := String.ofList (key.map fun byte => Char.ofNat byte.toNat)

structure Fixture where
  state : State := HyphenDictionarySequence.initial
  paths : List String := []
  validity : Resource → Bool := fun _ => false
  keysSeen : List Key := []
  gets : List String := []
  events : List Event := []

def remember (fixture : Fixture) (keys : List Key) : Fixture :=
  {fixture with keysSeen := (fixture.keysSeen++keys).eraseDups}

def evaluate (id : String) : List String → Fixture → Except String Fixture
  | [],fixture => .ok fixture
  | "P"::key::path::valid::rest,fixture =>
    let resource := fixture.paths.length
    let next : Fixture :=
      { fixture with
        paths := fixture.paths++[path]
        validity := fun queried => if queried = resource then valid = "1" else fixture.validity queried
        state := {fixture.state with patterns := replace fixture.state.patterns (encodeKey key) (some resource)} }
    evaluate id rest (remember next [encodeKey key])
  | "A"::key::alias::rest,fixture =>
    let next := {fixture with state := {fixture.state with aliases := replace fixture.state.aliases (encodeKey key) (some (encodeKey alias))}}
    evaluate id rest (remember next [encodeKey key,encodeKey alias])
  | "C"::key::value::rest,fixture =>
    evaluate id rest {fixture with state := {fixture.state with capitalized := (fun queried => if queried = encodeKey key then value = "1" else fixture.state.capitalized queried)}}
  | "M"::rest,fixture => evaluate id rest {fixture with state := pressure fixture.state}
  | "G"::key::rest,fixture =>
    let result := nativeGet fixture.validity fallback ((trimWildcard (encodeKey key)).length+1) fixture.state (encodeKey key)
    let returned := match result.answer with
      | none => "- 0"
      | some handle => fixture.paths[handle.resource]?.getD "BAD_RESOURCE" ++ " " ++ (if handle.capitalized then "1" else "0")
    let next := {fixture with state := result.state,events := fixture.events++result.events,gets := fixture.gets++[id++" GET "++key++" "++returned]}
    evaluate id rest (remember next (allKeys (encodeKey key)))
  | _,_ => .error "invalid fixture operation"

def summarize (id : String) (fixture : Fixture) : List String :=
  let loads := fixture.events.filterMap fun event => match event with
    | .load _ resource _ => some (fixture.paths[resource]?.getD "BAD_RESOURCE")
    | _ => none
  let prefs := fixture.events.filterMap fun event => match event with
    | .load key _ _ => some ("intl.hyphenate-capitalized."++text key)
    | _ => none
  let keys := (fixture.keysSeen.map text).mergeSort (fun a b => a ≤ b)
  let cached := keys.filter fun key => (fixture.state.cache (encodeKey key)).isSome
  let patterns := keys.filter fun key => (fixture.state.patterns (encodeKey key)).isSome
  fixture.gets++[String.intercalate " " ([id,"LOADS"]++loads++["PREFS"]++prefs++["CACHE"]++cached++["PATTERNS"]++patterns)]

def main (args : List String) : IO Unit := do
  let path ← match args with
    | [path] => pure path
    | _ => throw (IO.userError "expected fixed input path")
  let input ← IO.FS.readFile path
  for line in input.splitOn "\n" do
    if line.isEmpty then continue
    let tokens := line.splitOn " "
    match tokens with
    | [] => throw (IO.userError "missing case id")
    | id::rest =>
      match evaluate id rest {} with
      | .error message => throw (IO.userError message)
      | .ok fixture => for output in summarize id fixture do IO.println output
