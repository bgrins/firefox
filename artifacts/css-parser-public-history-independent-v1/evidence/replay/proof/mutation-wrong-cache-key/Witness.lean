import TrackingEpoch
import CommentDirectives
set_option autoImplicit false
namespace Mutation
abbrev Byte := CommentScan.Byte
inductive Block where
 | parenthesis | square | curly
 deriving DecidableEq, Repr
inductive Token where
 | function (name : List Byte)
 | comment (body : List Byte)
 | open (block : Block)
 | close (block : Block)
 | colon | other
 deriving DecidableEq, Repr
structure Cursor where
 position : Nat
 pending : Option Block := none
 deriving DecidableEq, Repr
structure Lexeme where
 token : Token
 cursor : Cursor
 deriving DecidableEq, Repr
structure Cache where
 key : Nat
 value : Lexeme
 deriving DecidableEq, Repr
inductive Mode where
 | off | looking (names : List (List Byte)) | seen
 deriving DecidableEq, Repr
structure State where
 cursor : Cursor
 cache : Option Cache
 mode : Mode
 urls : CommentDirectives.URLs
 saved : List Cursor := []
 deriving DecidableEq, Repr

def lower (b : Byte) : Nat := if 65 ≤ b.val ∧ b.val ≤ 90 then b.val+32 else b.val
def relevant (names : List (List Byte)) : Token → Bool
 | .function name => names.any fun target => name.map lower == target.map lower
 | _ => false

def seen : Mode → Bool
 | .seen => true
 | _ => false

def track (token : Token) : Mode → Mode
 | .looking names => if relevant names token then .seen else .looking names
 | other => other

def annotate (token : Token) (urls : CommentDirectives.URLs) : CommentDirectives.URLs :=
 match token with
 | .comment body => CommentDirectives.nativeUpdate body urls
 | _ => urls

def compatible (names : List (List Byte)) (mode : Mode) : Prop :=
 mode = .looking names ∨ mode = .seen

def coherent (read : Nat → Lexeme) (s : State) : Prop :=
 ∀ c, s.cache = some c → c.value = read c.key

def constructor (urls : CommentDirectives.URLs) : State :=
 ⟨⟨0,none⟩,none,.off,urls,[]⟩

def fresh (read : Nat → Lexeme) (replace : Bool) (s : State) : State :=
 let value := read s.cursor.position
 { s with cursor := value.cursor,
          cache := if replace then some ⟨s.cursor.position+1,value⟩ else s.cache,
          mode := track value.token s.mode, urls := annotate value.token s.urls }

def hit (c : Cache) (s : State) : State := { s with cursor := c.value.cursor }
def save (s : State) : State := { s with saved := s.cursor::s.saved }
def restore (index : Nat) (s : State) : State :=
 match s.saved[index]? with
 | some cursor => { s with cursor := cursor }
 | none => s

def cacheRelevant (names : List (List Byte)) (s : State) : Bool :=
 match s.cache with
 | none => false
 | some c => relevant names c.value.token

def project (names : List (List Byte)) (s : State) : TrackingEpoch.State :=
 ⟨cacheRelevant names s,seen s.mode⟩


theorem counterexample : (fresh (fun _ => ⟨.colon,⟨1,none⟩⟩) true (constructor ⟨none,none⟩)).cache.map Cache.key=some 1 := rfl
end Mutation
