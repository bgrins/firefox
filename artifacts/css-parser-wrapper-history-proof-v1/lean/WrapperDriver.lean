import WrapperCases
import WrapperEntry
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

def snapshot (s : State) : String :=
 let cache := match s.cache with
  | none => "none"
  | some c => toString c.key++":"++token c.value.token++":"++toString c.value.cursor.position++":"++toString (block c.value.cursor.pending)
 String.intercalate "|" [toString s.cursor.position,toString (block s.cursor.pending),cache,mode s.mode,
 opt s.urls.source,opt s.urls.sourceMap,if s.saved.isEmpty then "none" else String.intercalate "," (s.saved.map fun c => toString c.position++":"++toString (block c.pending))]

def provider (family : ByteLex.Family) (xs : List Byte) : Nat :=
 match family with
 | .whitespace => (xs.takeWhile URLScan.nativeWhitespace).length
 | .punctuation => if xs.head?=some 59 then 1 else panic! "unadmitted punctuation"
 | _ => panic! "unadmitted provider"

def step (source : List Byte) (s : State) (op : String) : String × State :=
 if op=="fetch" || op=="stop" then
   let next := PublicNext.native source (ByteLex.read provider source) (fun b=>op=="stop" && b==59) [] s
   (match next.token with | none => "eof" | some t => token t,next.state)
 else if op=="next" || op=="nextstop" then
   let next := WrapperNext.native source (ByteLex.read provider source) (fun b=>op=="nextstop" && b==59) [] s
   (match next.token with | none => "eof" | some t => token t,next.state)
 else if op=="skip" then ("none",(WrapperSkip.native source (ByteLex.read provider source) [] s).state)
 else if op=="colon" then
   let result := WrapperEntry.expectColon source (ByteLex.read provider source) (fun _=>false) [] s
   (toString result.1,result.2)
 else if op=="save" then ("none",save s)
 else if op=="query" then let answer := PublicHistory.query s
                         (toString answer.1,answer.2)
 else if op.startsWith "reset:" then
   ("none",restore ((op.drop 6).toString.toNat!) s)
 else if op.startsWith "enable:" then
   ("none",PublicHistory.begin (((op.drop 7).toString.splitOn ",").map CommentDirectives.ascii) s)
 else ("INVALID",s)

def main : IO Unit := do
 let out ← IO.getStdout
 for ((source,ops), case) in WrapperCases.cases.zipIdx do
   let mut state := constructor ⟨none,none⟩
   out.putStrLn (toString case++"|0|init|none|"++snapshot state)
   for (op,index) in ops.zipIdx do
     let (result,next) := step source state op
     state := next
     out.putStrLn (toString case++"|"++toString (index+1)++"|"++op++"|"++result++"|"++snapshot state)
