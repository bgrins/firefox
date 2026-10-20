import PublicFetch
set_option autoImplicit false
namespace PublicCleanup
open PublicCache

def clear (s : State) : State := { s with cursor := { s.cursor with pending := none } }
def closing : Token → Option Block
 | .close b => some b
 | _ => none

def stackAfter (stack : List Block) (value : Lexeme) : List Block :=
 match value.cursor.pending with
 | some b => b::stack
 | none => match closing value.token,stack with
           | some b,top::rest => if b=top then rest else stack
           | _,_ => stack

structure Output where
 state : State
 events : List TrackingEpoch.Event
 complete : Bool
 deriving DecidableEq, Repr

def done (length : Nat) (stack : List Block) (s : State) : Prop :=
 stack=[] ∨ length≤s.cursor.position
instance (length : Nat) (stack : List Block) (s : State) : Decidable (done length stack s) :=
 inferInstanceAs (Decidable (stack=[] ∨ length≤s.cursor.position))

def run (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) :
 Nat → List Block → State → Output
 | 0,stack,s => ⟨s,[],decide (done length stack s)⟩
 | fuel+1,stack,s =>
   if done length stack s then ⟨s,[],true⟩ else
   let value := read s.cursor.position
   let next := clear (fresh read false (clear s))
   let after := run length read names fuel (stackAfter stack value) next
   ⟨after.state,.raw (relevant names value.token)::after.events,after.complete⟩

def Progress (length : Nat) (read : Nat → Lexeme) : Prop :=
 ∀ position, position<length → position<(read position).cursor.position

theorem clear_coherent (read : Nat → Lexeme) (s : State) (h : coherent read s) :
 coherent read (clear s) := h

theorem clear_project (names : List (List Byte)) (s : State) :
 project names (clear s)=project names s := rfl

theorem complete_with_byte_fuel (length : Nat) (read : Nat → Lexeme)
 (names : List (List Byte)) (fuel : Nat) (stack : List Block) (s : State)
 (hp : Progress length read) (hf : length≤s.cursor.position+fuel) :
 (run length read names fuel stack s).complete=true := by
 induction fuel generalizing stack s with
 | zero =>
   have hd : done length stack s := Or.inr (by simpa using hf)
   simp [run,hd]
 | succ fuel ih =>
   simp only [run]
   split
   · rfl
   · rename_i hd
     have pos : s.cursor.position<length := by simp [done] at hd; omega
     have advance := hp s.cursor.position pos
     apply ih
     simp only [clear,fresh,Bool.false_eq_true,↓reduceIte]
     omega

theorem run_coherent (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) (h : coherent read s) :
 coherent read (run length read names fuel stack s).state := by
 induction fuel generalizing stack s with
 | zero => exact h
 | succ fuel ih =>
   simp only [run]
   split
   · exact h
   · exact ih _ _ (clear_coherent _ _ (fresh_coherent _ false _ (clear_coherent _ _ h)))

theorem run_compatible (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) (h : compatible names s.mode) :
 compatible names (run length read names fuel stack s).state.mode := by
 induction fuel generalizing stack s with
 | zero => exact h
 | succ fuel ih =>
   simp only [run]
   split
   · exact h
   · exact ih _ _ (track_compatible names _ _ h)

theorem run_project (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) (h : compatible names s.mode) :
 project names (run length read names fuel stack s).state =
   (run length read names fuel stack s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   simp only [run]
   split
   · rfl
   · have nh : compatible names (clear (fresh read false (clear s))).mode :=
       track_compatible names _ _ h
     rw [ih _ _ nh]
     rw [clear_project,fresh_project read names false (clear s) h,clear_project]
     rfl

theorem run_cache (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) :
 (run length read names fuel stack s).state.cache=s.cache := by
 induction fuel generalizing stack s with
 | zero => rfl
 | succ fuel ih =>
   simp only [run]
   split
   · rfl
   · exact ih _ _

def pending (length : Nat) (read : Nat → Lexeme) (names : List (List Byte)) (s : State) : Output :=
 match s.cursor.pending with
 | none => ⟨s,[],true⟩
 | some block => run length read names (length-s.cursor.position) [block] (clear s)

theorem pending_complete (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (hp : Progress length read) : (pending length read names s).complete=true := by
 unfold pending
 split
 · rfl
 · apply complete_with_byte_fuel _ _ _ _ _ _ hp
   simp only [clear]
   omega

theorem pending_coherent (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : coherent read s) : coherent read (pending length read names s).state := by
 unfold pending
 split
 · exact h
 · exact run_coherent _ _ _ _ _ _ h

theorem pending_compatible (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) : compatible names (pending length read names s).state.mode := by
 unfold pending
 split
 · exact h
 · exact run_compatible _ _ _ _ _ _ h

theorem pending_project (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (h : compatible names s.mode) :
 project names (pending length read names s).state =
   (pending length read names s).events.foldl TrackingEpoch.nativeStep (project names s) := by
 unfold pending
 split
 · rfl
 · exact run_project _ _ _ _ _ _ h

end PublicCleanup
