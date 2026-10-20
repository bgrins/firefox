import PublicEpochs
import ByteLexProgress
import FunctionMatching
import PublicAnnotations
set_option autoImplicit false
namespace PublicEntry
open PublicCache

theorem returned_cache (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (token : Token)
 (h : (PublicFetch.fetchReady bytes read stop names s).token=some token) :
 cacheRelevant names (PublicFetch.fetchReady bytes read stop names s).state=relevant names token := by
 cases hb : bytes[s.cursor.position]? with
 | none => simp [PublicFetch.fetchReady,hb] at h
 | some b =>
   cases hs : stop b with
   | true => simp [PublicFetch.fetchReady,hb,hs] at h
   | false =>
     cases hc : s.cache with
     | none =>
       simp [PublicFetch.fetchReady,hb,hs,hc,PublicFetch.freshOutput] at h
       simp [PublicFetch.fetchReady,hb,hs,hc,PublicFetch.freshOutput,fresh,cacheRelevant,h]
     | some c =>
       by_cases hk : c.key=s.cursor.position
       · simp [PublicFetch.fetchReady,hb,hs,hc,hk] at h
         simp [PublicFetch.fetchReady,hb,hs,hc,hk,cacheRelevant,hit,h]
       · simp [PublicFetch.fetchReady,hb,hs,hc,hk,PublicFetch.freshOutput] at h
         simp [PublicFetch.fetchReady,hb,hs,hc,hk,PublicFetch.freshOutput,fresh,cacheRelevant,h]

theorem next_nonrelevant_entry (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (token : Token)
 (h : (PublicNext.native bytes read stop names s).token=some token)
 (hn : relevant names token=false) :
 cacheRelevant names (PublicNext.native bytes read stop names s).state=false :=
 (returned_cache _ _ _ _ _ _ h).trans hn

theorem colon_entry (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State)
 (h : (PublicNext.native bytes read stop names s).token=some .colon) :
 cacheRelevant names (PublicNext.native bytes read stop names s).state=false :=
 next_nonrelevant_entry _ _ _ _ _ _ h rfl

theorem byte_constructor_history (provider : ByteLex.Family → List Byte → Nat)
 (bytes : List Byte) (names : List (List Byte)) (actions : List PublicHistory.Action)
 (urls : CommentDirectives.URLs) :
 PublicHistory.Aligned (ByteLex.read provider bytes) names
 (actions.foldl (PublicHistory.nativeStep bytes (ByteLex.read provider bytes) names)
   (PublicHistory.begin names (constructor urls)))
 (actions.foldl (PublicHistory.referenceStep bytes (ByteLex.read provider bytes))
   (PublicHistory.initialReference (constructor urls))) :=
 PublicHistory.history_aligned _ _ _ _ _ _ (PublicHistory.constructor_begin _ _ _)

theorem byte_constructor_annotations (provider : ByteLex.Family → List Byte → Nat)
 (bytes : List Byte) (names : List (List Byte)) (actions : List PublicHistory.Action)
 (urls : CommentDirectives.URLs) :
 PublicAnnotations.projection
   (actions.foldl (PublicHistory.nativeStep bytes (ByteLex.read provider bytes) names) (constructor urls)) =
 actions.foldl (PublicAnnotations.referenceStep bytes (ByteLex.read provider bytes)) ⟨⟨0,none⟩,none,[],urls⟩ :=
 PublicAnnotations.constructor_history _ _ _ _ _

end PublicEntry
