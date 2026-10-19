import PublicNext
set_option autoImplicit false
namespace PublicHistory
open PublicCache
inductive Action where
 | fetch (stops : List Byte)
 | save
 | restore (index : Nat)
 deriving DecidableEq, Repr
structure Reference where
 cursor : Cursor
 saved : List Cursor
 observations : List Token
 deriving DecidableEq, Repr

def nativeStep (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) : Action → State
 | .fetch stops => (PublicNext.native bytes read stops.contains names s).state
 | .save => PublicCache.save s
 | .restore index => PublicCache.restore index s

def referenceStep (bytes : List Byte) (read : Nat → Lexeme) (r : Reference) : Action → Reference
 | .fetch stops =>
   let next := PublicNext.reference bytes read stops.contains r.cursor
   {r with cursor:=next.cursor,observations:=r.observations++next.observations}
 | .save => {r with saved:=r.cursor::r.saved}
 | .restore index => match r.saved[index]? with
                     | some cursor => {r with cursor:=cursor}
                     | none => r

structure Aligned (read : Nat → Lexeme) (names : List (List Byte)) (s : State) (r : Reference) : Prop where
 cursor_eq : s.cursor=r.cursor
 saved_eq : s.saved=r.saved
 cache_coherent : coherent read s
 mode_compatible : compatible names s.mode
 cache_seen : TrackingEpoch.Inv (project names s)
 seen_eq : seen s.mode = r.observations.any (relevant names)

def begin (names : List (List Byte)) (s : State) : State := {s with mode:=.looking names}
def initialReference (s : State) : Reference := ⟨s.cursor,s.saved,[]⟩

theorem begin_aligned (read : Nat → Lexeme) (names : List (List Byte)) (s : State)
 (hc : coherent read s) (hn : cacheRelevant names s=false) :
 Aligned read names (begin names s) (initialReference s) := by
 refine ⟨rfl,rfl,hc,Or.inl rfl,?_,rfl⟩
 intro h
 change cacheRelevant names s=true at h
 rw [hn] at h
 contradiction

theorem constructor_begin (read : Nat → Lexeme) (names : List (List Byte))
 (urls : CommentDirectives.URLs) :
 Aligned read names (begin names (constructor urls)) (initialReference (constructor urls)) :=
 begin_aligned _ _ _ (constructor_coherent _ _) rfl

theorem step_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (r : Reference) (a : Action) (h : Aligned read names s r) :
 Aligned read names (nativeStep bytes read names s a) (referenceStep bytes read r a) := by
 cases a with
 | fetch stops =>
   refine ⟨?_,?_,PublicNext.coherent_next _ _ _ _ _ h.cache_coherent,
     PublicNext.compatible_next _ _ _ _ _ h.mode_compatible,
     PublicNext.next_inv _ _ _ _ _ h.mode_compatible h.cache_seen,?_⟩
   · simpa [nativeStep,referenceStep,h.cursor_eq] using
       PublicNext.next_cursor bytes read stops.contains names s h.cache_coherent
   · simpa [nativeStep,referenceStep,h.saved_eq] using
       PublicNext.next_saved bytes read stops.contains names s
   · have seen := PublicNext.next_seen bytes read stops.contains names s h.cache_coherent
       h.mode_compatible h.cache_seen
     simpa [nativeStep,referenceStep,h.cursor_eq,h.seen_eq,List.any_append] using seen
 | save =>
   exact ⟨h.cursor_eq,by simp [nativeStep,referenceStep,PublicCache.save,h.cursor_eq,h.saved_eq],
     h.cache_coherent,h.mode_compatible,h.cache_seen,h.seen_eq⟩
 | restore index =>
   cases hs : s.saved[index]? with
   | none => simpa [nativeStep,referenceStep,PublicCache.restore,← h.saved_eq,hs] using h
   | some cursor =>
     simp only [nativeStep,referenceStep,PublicCache.restore,← h.saved_eq,hs]
     exact ⟨rfl,rfl,h.cache_coherent,h.mode_compatible,h.cache_seen,h.seen_eq⟩

theorem history_aligned (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (actions : List Action) (s : State) (r : Reference) (h : Aligned read names s r) :
 Aligned read names (actions.foldl (nativeStep bytes read names) s)
   (actions.foldl (referenceStep bytes read) r) := by
 induction actions generalizing s r with
 | nil => exact h
 | cons a rest ih =>
   simp only [List.foldl_cons]
   exact ih _ _ (step_aligned bytes read names s r a h)

theorem constructor_history (bytes : List Byte) (read : Nat → Lexeme)
 (names : List (List Byte)) (actions : List Action) (urls : CommentDirectives.URLs) :
 seen (actions.foldl (nativeStep bytes read names) (begin names (constructor urls))).mode =
   (actions.foldl (referenceStep bytes read) (initialReference (constructor urls))).observations.any (relevant names) :=
 (history_aligned _ _ _ _ _ _ (constructor_begin _ _ _)).seen_eq

def query (s : State) : Bool × State := (seen s.mode,{s with mode:=.off})

theorem query_after_history (bytes : List Byte) (read : Nat → Lexeme)
 (names : List (List Byte)) (actions : List Action) (s : State)
 (hc : coherent read s) (hn : cacheRelevant names s=false) :
 let final := actions.foldl (nativeStep bytes read names) (begin names s)
 (query final).1 = (actions.foldl (referenceStep bytes read) (initialReference s)).observations.any (relevant names) ∧
 (query final).2.mode=.off ∧ (query final).2.cache=final.cache ∧ (query final).2.urls=final.urls := by
 have h := history_aligned bytes read names actions _ _ (begin_aligned read names s hc hn)
 exact ⟨h.seen_eq,rfl,rfl,rfl⟩

theorem second_query_false (s : State) : (query (query s).2).1=false := rfl

theorem query_preserves_coherent (read : Nat → Lexeme) (s : State) (h : coherent read s) :
 coherent read (query s).2 := h

end PublicHistory
