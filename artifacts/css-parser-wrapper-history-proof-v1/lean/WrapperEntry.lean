import WrapperAnnotations
set_option autoImplicit false
namespace WrapperEntry
open PublicCache

def expectColon (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) : Bool × State :=
 let result := WrapperNext.native bytes read stop names s
 (result.token==some .colon,result.state)

theorem successful_colon_safe (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : (expectColon bytes read stop names s).1=true) :
 cacheRelevant names (expectColon bytes read stop names s).2=false := by
 have ht : (WrapperNext.native bytes read stop names s).token=some .colon := by
   simpa [expectColon] using h
 exact WrapperNext.colon_safe_entry _ _ _ _ _ ht

theorem cold_after_skip (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (urls : CommentDirectives.URLs) :
 cacheRelevant names (WrapperSkip.native bytes read names (constructor urls)).state=false := by
 rw [WrapperSkip.safe_entry_preserved]
 rfl

theorem declaration_entry (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (hc : coherent read s)
 (h : (expectColon bytes read stop names s).1=true) :
 let entry := (WrapperSkip.native bytes read names (expectColon bytes read stop names s).2).state
 PublicHistory.Aligned read names (PublicHistory.begin names entry) (PublicHistory.initialReference entry) := by
 apply PublicHistory.begin_aligned
 · exact WrapperSkip.skip_coherent _ _ _ _ (WrapperNext.next_coherent _ _ _ _ _ hc)
 · rw [WrapperSkip.safe_entry_preserved]
   exact successful_colon_safe _ _ _ _ _ h

theorem declaration_query (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (hc : coherent read s)
 (h : (expectColon bytes read stop names s).1=true) (actions : List WrapperHistory.Action) :
 let entry := (WrapperSkip.native bytes read names (expectColon bytes read stop names s).2).state
 let final := actions.foldl (WrapperHistory.nativeStep bytes read names) (PublicHistory.begin names entry)
 (PublicHistory.query final).1 =
   (actions.foldl (WrapperHistory.referenceStep bytes read) (PublicHistory.initialReference entry)).observations.any (relevant names) := by
 exact (WrapperHistory.histories_aligned _ _ _ _ _ _ (declaration_entry _ _ _ _ _ hc h)).seen_eq

end WrapperEntry
