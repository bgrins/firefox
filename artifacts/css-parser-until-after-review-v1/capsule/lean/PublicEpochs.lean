import PublicHistory
namespace PublicEpochs
open PublicCache PublicHistory
set_option autoImplicit false
structure Epoch where
 names : List (List Byte)
 actions : List Action
 deriving DecidableEq, Repr
structure Base where
 cursor : Cursor
 saved : List Cursor
 deriving DecidableEq, Repr

def nativeEpoch (bytes : List Byte) (read : Nat → Lexeme) (e : Epoch) (s : State) : Bool × State :=
 query (e.actions.foldl (nativeStep bytes read e.names) (begin e.names s))

def referenceEpoch (bytes : List Byte) (read : Nat → Lexeme) (e : Epoch) (r : Base) : Bool × Base :=
 let final := e.actions.foldl (referenceStep bytes read) ⟨r.cursor,r.saved,[]⟩
 (final.observations.any (relevant e.names),⟨final.cursor,final.saved⟩)

structure Related (read : Nat → Lexeme) (s : State) (r : Base) : Prop where
 cursor_eq : s.cursor=r.cursor
 saved_eq : s.saved=r.saved
 coherent : PublicCache.coherent read s

theorem epoch_refines (bytes : List Byte) (read : Nat → Lexeme) (e : Epoch)
 (s : State) (r : Base) (h : Related read s r) (safe : cacheRelevant e.names s=false) :
 (nativeEpoch bytes read e s).1=(referenceEpoch bytes read e r).1 ∧
 Related read (nativeEpoch bytes read e s).2 (referenceEpoch bytes read e r).2 := by
 have begin_h := begin_aligned read e.names s h.coherent safe
 have run_h := history_aligned bytes read e.names e.actions _ _ begin_h
 have initial_eq : initialReference s=⟨r.cursor,r.saved,[]⟩ := by
   simp [initialReference,h.cursor_eq,h.saved_eq]
 rw [initial_eq] at run_h
 exact ⟨run_h.seen_eq,run_h.cursor_eq,run_h.saved_eq,run_h.cache_coherent⟩

def native (bytes : List Byte) (read : Nat → Lexeme) : List Epoch → State → List Bool × State
 | [],s => ([],s)
 | e::es,s => let (answer,next) := nativeEpoch bytes read e s
              let (answers,final) := native bytes read es next
              (answer::answers,final)

def reference (bytes : List Byte) (read : Nat → Lexeme) : List Epoch → Base → List Bool × Base
 | [],r => ([],r)
 | e::es,r => let (answer,next) := referenceEpoch bytes read e r
              let (answers,final) := reference bytes read es next
              (answer::answers,final)

def Admitted (bytes : List Byte) (read : Nat → Lexeme) : List Epoch → State → Prop
 | [],_ => True
 | e::es,s => cacheRelevant e.names s=false ∧ Admitted bytes read es (nativeEpoch bytes read e s).2

theorem epochs_refine (bytes : List Byte) (read : Nat → Lexeme) (epochs : List Epoch)
 (s : State) (r : Base) (h : Related read s r) (safe : Admitted bytes read epochs s) :
 (native bytes read epochs s).1=(reference bytes read epochs r).1 ∧
 Related read (native bytes read epochs s).2 (reference bytes read epochs r).2 := by
 induction epochs generalizing s r with
 | nil => exact ⟨rfl,h⟩
 | cons e es ih =>
   have one := epoch_refines bytes read e s r h safe.1
   have rest := ih _ _ one.2 safe.2
   exact ⟨by simpa only [native,reference,one.1] using congrArg (List.cons (referenceEpoch bytes read e r).1) rest.1,
     rest.2⟩

theorem constructor_epochs (bytes : List Byte) (read : Nat → Lexeme) (epochs : List Epoch)
 (urls : CommentDirectives.URLs) (safe : Admitted bytes read epochs (constructor urls)) :
 (native bytes read epochs (constructor urls)).1=(reference bytes read epochs ⟨⟨0,none⟩,[]⟩).1 :=
 (epochs_refine _ _ _ _ _ ⟨rfl,rfl,constructor_coherent _ _⟩ safe).1

end PublicEpochs
