import WrapperHistory
set_option autoImplicit false
namespace WrapperAnnotations
open PublicCache PublicAnnotations

def referenceStep (bytes : List Byte) (read : Nat → Lexeme) (r : Reference) : WrapperHistory.Action → Reference
 | .skip => let skipped := WrapperSkip.reference bytes read r.cursor
            ⟨skipped.cursor,r.key,r.saved,applyTokens skipped.writes r.urls⟩
 | .next stops =>
   let skipped := WrapperSkip.reference bytes read r.cursor
   let fetched := PublicSourceOnly.ready bytes read stops.contains skipped.cursor
   ⟨fetched.cursor,readyKey bytes stops.contains skipped.cursor r.key,r.saved,
     applyTokens (WrapperNext.writes bytes read stops.contains r.cursor r.key) r.urls⟩
 | .primary stops => PublicAnnotations.referenceStep bytes read r (.fetch stops)
 | .save => PublicAnnotations.referenceStep bytes read r .save
 | .restore index => PublicAnnotations.referenceStep bytes read r (.restore index)

theorem step_projection (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (a : WrapperHistory.Action) (hc : coherent read s) :
 projection (WrapperHistory.nativeStep bytes read names s a)=referenceStep bytes read (projection s) a := by
 cases a with
 | skip =>
   apply Reference.ext
   · exact WrapperSkip.skip_cursor _ _ _ _
   · simp only [WrapperHistory.nativeStep,projection,referenceStep,key,WrapperSkip.skip_cache]
   · exact WrapperSkip.skip_saved _ _ _ _
   · exact WrapperSkip.skip_writes _ _ _ _
 | next stops =>
   simp only [WrapperHistory.nativeStep,WrapperNext.actual_fetch_join,projection,referenceStep]
   apply Reference.ext
   · rw [PublicSourceOnly.ready_cursor _ _ _ _ _ (WrapperSkip.skip_coherent _ _ _ _ hc),WrapperSkip.skip_cursor]
   · rw [ready_key,WrapperSkip.skip_cursor]
     simp only [key,WrapperSkip.skip_cache]
   · rw [PublicNext.ready_saved,WrapperSkip.skip_saved]
   · simpa only [WrapperNext.actual_fetch_join] using WrapperNext.next_writes bytes read stops.contains names s
 | primary stops => exact PublicAnnotations.step_projection bytes read names s (.fetch stops) hc
 | save => exact PublicAnnotations.step_projection bytes read names s .save hc
 | restore index => exact PublicAnnotations.step_projection bytes read names s (.restore index) hc

theorem step_coherent (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (a : WrapperHistory.Action) (hc : coherent read s) :
 coherent read (WrapperHistory.nativeStep bytes read names s a) := by
 cases a with
 | skip => exact WrapperSkip.skip_coherent _ _ _ _ hc
 | next stops => exact WrapperNext.next_coherent _ _ _ _ _ hc
 | primary stops => exact PublicNext.coherent_next _ _ _ _ _ hc
 | save => exact hc
 | restore index => exact restore_coherent _ _ _ hc

theorem history_projection (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List WrapperHistory.Action) (s : State) (hc : coherent read s) :
 projection (actions.foldl (WrapperHistory.nativeStep bytes read names) s) =
 actions.foldl (referenceStep bytes read) (projection s) := by
 induction actions generalizing s with
 | nil => rfl
 | cons a rest ih =>
   simp only [List.foldl_cons]
   rw [ih _ (step_coherent _ _ _ _ _ hc),step_projection _ _ _ _ _ hc]

theorem constructor_history (provider : ByteLex.Family → List Byte → Nat)
 (bytes : List Byte) (names : List (List Byte)) (actions : List WrapperHistory.Action)
 (urls : CommentDirectives.URLs) :
 projection (actions.foldl (WrapperHistory.nativeStep bytes (ByteLex.read provider bytes) names) (constructor urls)) =
 actions.foldl (referenceStep bytes (ByteLex.read provider bytes)) ⟨⟨0,none⟩,none,[],urls⟩ :=
 history_projection _ _ _ _ _ (constructor_coherent _ _)

end WrapperAnnotations
