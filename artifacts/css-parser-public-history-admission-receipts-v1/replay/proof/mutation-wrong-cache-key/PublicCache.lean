import TrackingEpoch
import CommentDirectives
set_option autoImplicit false
namespace PublicCache
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

theorem constructor_coherent (read : Nat → Lexeme) (urls : CommentDirectives.URLs) :
 coherent read (constructor urls) := by simp [coherent,constructor]

theorem fresh_coherent (read : Nat → Lexeme) (replace : Bool) (s : State)
 (h : coherent read s) : coherent read (fresh read replace s) := by
 cases replace
 · exact h
 · intro c hc
   simp only [fresh,↓reduceIte,Option.some.injEq] at hc
   cases hc
   rfl

theorem hit_coherent (read : Nat → Lexeme) (c : Cache) (s : State)
 (h : coherent read s) : coherent read (hit c s) := h

theorem save_coherent (read : Nat → Lexeme) (s : State)
 (h : coherent read s) : coherent read (save s) := h

theorem restore_coherent (read : Nat → Lexeme) (index : Nat) (s : State)
 (h : coherent read s) : coherent read (restore index s) := by
 unfold restore
 split <;> exact h

theorem matching_cache_fresh (read : Nat → Lexeme) (s : State) (c : Cache)
 (h : coherent read s) (hc : s.cache=some c) (hk : c.key=s.cursor.position) :
 c.value = read s.cursor.position := by rw [h c hc,hk]

theorem track_seen (names : List (List Byte)) (token : Token) (mode : Mode)
 (h : compatible names mode) :
 seen (track token mode) = (seen mode || relevant names token) := by
 rcases h with rfl | rfl
 · simp only [track,seen,Bool.false_or]
   cases relevant names token <;> rfl
 · rfl

theorem track_compatible (names : List (List Byte)) (token : Token) (mode : Mode)
 (h : compatible names mode) : compatible names (track token mode) := by
 rcases h with rfl | rfl
 · change compatible names (if relevant names token then .seen else .looking names)
   cases relevant names token <;> simp [compatible]
 · exact Or.inr rfl

theorem fresh_project (read : Nat → Lexeme) (names : List (List Byte))
 (replace : Bool) (s : State) (h : compatible names s.mode) :
 project names (fresh read replace s) = TrackingEpoch.nativeStep (project names s)
   (if replace then .fresh (relevant names (read s.cursor.position).token)
    else .raw (relevant names (read s.cursor.position).token)) := by
 cases replace <;>
   simp [project,fresh,cacheRelevant,TrackingEpoch.nativeStep,track_seen names _ _ h]

theorem hit_project (names : List (List Byte)) (c : Cache) (s : State) :
 project names (hit c s) = TrackingEpoch.nativeStep (project names s) .cached := rfl

theorem restore_project (names : List (List Byte)) (index : Nat) (s : State) :
 project names (restore index s) = TrackingEpoch.nativeStep (project names s) .reset := by
 unfold restore
 split <;> rfl

theorem raw_preserves_cache (read : Nat → Lexeme) (s : State) :
 (fresh read false s).cache=s.cache := rfl

theorem hit_preserves_effects (c : Cache) (s : State) :
 (hit c s).mode=s.mode ∧ (hit c s).urls=s.urls := ⟨rfl,rfl⟩

theorem restore_preserves_effects (index : Nat) (s : State) :
 (restore index s).mode=s.mode ∧ (restore index s).urls=s.urls := by
 unfold restore
 split <;> exact ⟨rfl,rfl⟩

end PublicCache
