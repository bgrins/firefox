import WrapperWhitespace
set_option autoImplicit false
namespace Mutation
open PublicCache

def native (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) : PublicCleanup.Output :=
 let pending : PublicCleanup.Output := ⟨s,[],true⟩
 ⟨WrapperWhitespace.run bytes (bytes.length+1) pending.state,pending.events,pending.complete⟩

structure Reference where
 cursor : Cursor
 observations : List Token
 writes : List Token
 deriving DecidableEq, Repr

def reference (bytes : List Byte) (read : Nat → Lexeme) (cursor : Cursor) : Reference :=
 let pending := PublicSourceOnly.pending bytes.length read cursor
 let scanned := WrapperWhitespace.reference bytes (bytes.length+1) pending.cursor.position
 ⟨{pending.cursor with position:=scanned.position},pending.tokens,
   pending.tokens++scanned.comments.map Token.comment⟩


def source : List Byte := [40,41]
def reader := ByteLex.read (fun _ _=>1) source
def opened := (PublicNext.native source reader (fun _=>false) [] (constructor ⟨none,none⟩)).state
example : (native source reader [] opened).state.cursor=⟨1,some .parenthesis⟩ := by decide
end Mutation
