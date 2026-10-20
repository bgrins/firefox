import PublicCache
set_option autoImplicit false
namespace PublicFetch
open PublicCache
structure Output where
 state : State
 events : List TrackingEpoch.Event
 token : Option Token
 deriving DecidableEq, Repr

def freshOutput (read : Nat → Lexeme) (names : List (List Byte)) (s : State) : Output :=
 ⟨fresh read true s,[.fresh (relevant names (read s.cursor.position).token)],
   some (read s.cursor.position).token⟩

def fetchReady (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) : Output :=
 match bytes[s.cursor.position]? with
 | none => ⟨s,[],none⟩
 | some b =>
   if stop b then ⟨s,[],none⟩ else
   match s.cache with
   | none => freshOutput read names s
   | some c =>
     if c.key=s.cursor.position then ⟨hit c s,[.cached],some c.value.token⟩
     else freshOutput read names s

def logical (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) : List Bool :=
 match bytes[s.cursor.position]? with
 | none => []
 | some b => if stop b then [] else [relevant names (read s.cursor.position).token]

theorem fresh_output_coherent (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : coherent read s) : coherent read (freshOutput read names s).state :=
 fresh_coherent read true s h

theorem fetch_coherent (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 coherent read (fetchReady bytes read stop names s).state := by
 unfold fetchReady
 split
 · exact h
 · split
   · exact h
   · split
     · exact fresh_output_coherent read names s h
     · split
       · exact h
       · exact fresh_output_coherent read names s h

theorem fresh_output_compatible (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) :
 compatible names (freshOutput read names s).state.mode :=
 track_compatible names _ _ h

theorem fetch_compatible (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : compatible names s.mode) :
 compatible names (fetchReady bytes read stop names s).state.mode := by
 unfold fetchReady
 split
 · exact h
 · split
   · exact h
   · split
     · exact fresh_output_compatible read names s h
     · split
       · exact h
       · exact fresh_output_compatible read names s h

theorem fresh_output_project (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) :
 project names (freshOutput read names s).state =
   (freshOutput read names s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 simpa [freshOutput] using fresh_project read names true s h

theorem fetch_project (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : compatible names s.mode) :
 project names (fetchReady bytes read stop names s).state =
   (fetchReady bytes read stop names s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 unfold fetchReady
 split
 · rfl
 · split
   · rfl
   · split
     · exact fresh_output_project read names s h
     · split
       · rfl
       · exact fresh_output_project read names s h

theorem fresh_output_emissions (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) :
 TrackingEpoch.reference (cacheRelevant names s) (freshOutput read names s).events =
 [relevant names (read s.cursor.position).token] := by
 simp [freshOutput,TrackingEpoch.reference,TrackingEpoch.emitted]

theorem fetch_emissions (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) :
 TrackingEpoch.reference (cacheRelevant names s) (fetchReady bytes read stop names s).events =
 logical bytes read stop names s := by
 unfold fetchReady logical
 split
 · rfl
 · split
   · rfl
   · split
     · exact fresh_output_emissions read names s
     · rename_i c hc
       split
       · rename_i hk
         have same := matching_cache_fresh read s c h hc hk
         simp [TrackingEpoch.reference,TrackingEpoch.emitted,cacheRelevant,hc,same]
       · exact fresh_output_emissions read names s

theorem fetch_fresh_token (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (h : coherent read s) (b : Byte)
 (hb : bytes[s.cursor.position]?=some b) (hs : stop b=false) :
 (fetchReady bytes read stop names s).token=some (read s.cursor.position).token := by
 simp only [fetchReady,hb,hs,Bool.false_eq_true,↓reduceIte]
 split
 · rfl
 · rename_i c hc
   split
   · rename_i hk
     have same := matching_cache_fresh read s c h hc hk
     simp [same]
   · rfl

theorem fetch_epoch_seen (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (hc : coherent read s)
 (ht : compatible names s.mode) (hi : TrackingEpoch.Inv (project names s)) :
 seen (fetchReady bytes read stop names s).state.mode =
   (seen s.mode || (logical bytes read stop names s).any id) := by
 have result := TrackingEpoch.execution (fetchReady bytes read stop names s).events
   (project names s) hi
 rw [← fetch_project bytes read stop names s ht] at result
 simpa [project,fetch_emissions bytes read stop names s hc] using result

theorem fetch_epoch_inv (bytes : List Byte) (read : Nat → Lexeme) (stop : Byte → Bool)
 (names : List (List Byte)) (s : State) (ht : compatible names s.mode)
 (hi : TrackingEpoch.Inv (project names s)) :
 TrackingEpoch.Inv (project names (fetchReady bytes read stop names s).state) := by
 rw [fetch_project bytes read stop names s ht]
 exact TrackingEpoch.prefix_inv _ _ hi

end PublicFetch
