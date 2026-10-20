import AfterCases
import UntilAfter
open PublicCache
def hx (xs : List Byte) : String := String.ofList (xs.flatMap fun b =>
 [Char.ofNat (if b.val/16<10 then 48+b.val/16 else 87+b.val/16),
  Char.ofNat (if b.val%16<10 then 48+b.val%16 else 87+b.val%16)])
def opt (xs : Option (List Byte)) : String := match xs with
 | none => "none"
 | some xs => "some:"++hx xs

def block : Option Block → Nat
 | none => 0
 | some .parenthesis => 1
 | some .square => 2
 | some .curly => 3

def token : Token → String
 | .function n => "f:"++hx n
 | .comment n => "c:"++hx n
 | .open b => "o:"++toString (block (some b))
 | .close b => "x:"++toString (block (some b))
 | .colon => "colon"
 | .other => "other"

def mode : Mode → String
 | .off => "off"
 | .seen => "seen"
 | .looking names => "looking:"++String.intercalate "," (names.map hx)

def coreSnapshot (s : PublicCache.State) : String :=
 let cache := match s.cache with
  | none => "none"
  | some c => toString c.key++":"++token c.value.token++":"++toString c.value.cursor.position++":"++toString (block c.value.cursor.pending)
 String.intercalate "|" [toString s.cursor.position,toString (block s.cursor.pending),cache,mode s.mode,
 opt s.urls.source,opt s.urls.sourceMap]


def snapshot (s : NestedControl.State) : String :=
 let bits := s.stops.foldl (fun n b => n + (if b==123 then 2 else if b==59 then 4 else if b==33 then 8 else if b==44 then 16 else if b==125 then 32 else if b==93 then 64 else if b==41 then 128 else 0)) 0
 coreSnapshot s.core++"|"++toString bits++"|"++toString s.depth.val++"|"++toString s.limit.val

def provider (family : ByteLex.Family) (xs : List Byte) : Nat :=
 match family with
 | .whitespace => (xs.takeWhile URLScan.nativeWhitespace).length
 | .punctuation => if [33,44,59].contains (xs.head?.getD 0) then 1 else panic! "unadmitted punctuation"
 | _ => panic! "unadmitted provider"

def mask (bits : Nat) : List Byte :=
 ([123,59,33,44,125,93,41] : List Byte).zipIdx |>.filterMap fun (byte,index) =>
   if bits / (2^(index+1)) % 2 == 1 then some byte else none

def step (source : List Byte) (names : List (List Byte)) (s : NestedControl.State) (op : String) : String × NestedControl.State :=
 let read := ByteLex.read provider source
 let args := op.splitOn ":"
 if op=="next" then
   let fetched := WrapperNext.native source read s.stops.contains names s.core
   (match fetched.token with | none => "eof" | some t => token t, {s with core := fetched.state})
 else if op=="enable" then ("none",{s with core := PublicHistory.begin names s.core})
 else if op=="query" then let result := PublicHistory.query s.core
                         (toString result.1,{s with core := result.2})
 else if op=="save" then ("none",{s with core := {s.core with saved := [s.core.cursor]}})
 else if op=="reset" then ("none",{s with core := PublicCache.restore 0 s.core})
 else if args.head! == "outer" then ("none",{s with stops := mask args[1]!.toNat!})
 else if args.head! == "limit" then ("none",{s with limit := Fin.ofNat 256 args[1]!.toNat!})
 else if args.head! == "depth" then ("none",{s with depth := Fin.ofNat 256 args[1]!.toNat!})
 else if args.head! == "after" then
   let result := UntilAfter.native source read names (mask args[1]!.toNat!) (args[4]! == "1")
     (fun stops => .callback (List.replicate args[2]!.toNat! (.next stops))
       (fun returned => returned.all Option.isSome && args[3]! == "1")) s
   (toString result.1,result.2)
 else (panic! "unadmitted operation", s)

def main : IO Unit := do
 let out ← IO.getStdout
 for ((source,ops), case) in AfterCases.cases.zipIdx do
   let mut state : NestedControl.State := ⟨constructor ⟨none,none⟩,[],0,75⟩
   let mut names : List (List Byte) := []
   out.putStrLn (toString case++"|0|init|none|"++snapshot state)
   for (op,index) in ops.zipIdx do
     if op=="enable" then names := [CommentDirectives.ascii "var",CommentDirectives.ascii "env",CommentDirectives.ascii "attr"]
     let (result,next) := step source names state op
     state := next
     out.putStrLn (toString case++"|"++toString (index+1)++"|"++op++"|"++result++"|"++snapshot state)
