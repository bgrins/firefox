import PublicEntry
set_option autoImplicit false
set_option maxHeartbeats 2000000
namespace WrapperWhitespace
open PublicCache

structure Unit where
 count : Nat
 comment : Option (List Byte)
 deriving DecidableEq, Repr

def nativeUnit : List Byte → Option Unit
 | [] => none
 | b::bs =>
   if b=32 ∨ b=9 then some ⟨1,none⟩
   else if b=10 ∨ b=12 ∨ b=13 then
     some ⟨if b=13 ∧ bs.head?=some 10 then 2 else 1,none⟩
   else if b=47 ∧ bs.head?=some 42 then
     let c := CommentScan.scan bs.tail
     some ⟨2+c.count,some c.body⟩
   else none

def referenceUnit : List Byte → Option Unit
 | 32::_ | 9::_ => some ⟨1,none⟩
 | 13::10::_ => some ⟨2,none⟩
 | 10::_ | 12::_ | 13::_ => some ⟨1,none⟩
 | 47::42::tail =>
   let c := CommentScan.reference tail
   some ⟨2+c.count,some c.body⟩
 | _ => none

theorem unit_refines (xs : List Byte) : nativeUnit xs=referenceUnit xs := by
 cases xs with
 | nil => rfl
 | cons b bs =>
   by_cases h32 : b=32 <;> by_cases h9 : b=9 <;>
   by_cases h10 : b=10 <;> by_cases h12 : b=12 <;>
   by_cases h13 : b=13 <;> by_cases h47 : b=47 <;>
   cases bs with
   | nil => simp_all [nativeUnit,referenceUnit]
   | cons c cs =>
     by_cases hc10 : c=10 <;> by_cases hc42 : c=42 <;>
       simp_all [nativeUnit,referenceUnit,CommentScan.scan_reference]

theorem unit_positive (xs : List Byte) (u : Unit) (h : nativeUnit xs=some u) : 0<u.count := by
 cases xs with
 | nil => simp [nativeUnit] at h
 | cons b bs =>
   simp only [nativeUnit] at h
   split at h
   · cases h; decide
   · split at h
     · cases h; split <;> decide
     · split at h
       · cases h; simp; omega
       · contradiction

def advance (u : Unit) (s : State) : State :=
 { s with cache := none, cursor := {s.cursor with position:=s.cursor.position+u.count},
          urls := match u.comment with
                  | none => s.urls
                  | some body => CommentDirectives.nativeUpdate body s.urls }

def run (bytes : List Byte) : Nat → State → State
 | 0,s => s
 | fuel+1,s => match nativeUnit (bytes.drop s.cursor.position) with
               | none => s
               | some u => run bytes fuel (advance u s)

structure Prefix where
 position : Nat
 comments : List (List Byte)
 deriving DecidableEq, Repr

def reference (bytes : List Byte) : Nat → Nat → Prefix
 | 0,p => ⟨p,[]⟩
 | fuel+1,p => match referenceUnit (bytes.drop p) with
               | none => ⟨p,[]⟩
               | some u => let rest := reference bytes fuel (p+u.count)
                           ⟨rest.position,u.comment.toList++rest.comments⟩

def publish (comments : List (List Byte)) (urls : CommentDirectives.URLs) :=
 comments.foldl (fun state body => CommentDirectives.referenceUpdate body state) urls

theorem run_cursor (bytes : List Byte) (fuel : Nat) (s : State) :
 (run bytes fuel s).cursor =
 {s.cursor with position := (reference bytes fuel s.cursor.position).position} := by
 induction fuel generalizing s with
 | zero => rfl
 | succ fuel ih =>
   simp only [run,reference,← unit_refines]
   split
   · rfl
   · simpa [advance] using ih (advance _ s)

theorem run_cache (bytes : List Byte) (fuel : Nat) (s : State) :
 (run bytes fuel s).cache=s.cache := by
 induction fuel generalizing s with
 | zero => rfl
 | succ fuel ih => simp only [run]; split; rfl; exact ih _

theorem run_mode (bytes : List Byte) (fuel : Nat) (s : State) :
 (run bytes fuel s).mode=s.mode := by
 induction fuel generalizing s with
 | zero => rfl
 | succ fuel ih => simp only [run]; split; rfl; exact ih _

theorem run_saved (bytes : List Byte) (fuel : Nat) (s : State) :
 (run bytes fuel s).saved=s.saved := by
 induction fuel generalizing s with
 | zero => rfl
 | succ fuel ih => simp only [run]; split; rfl; exact ih _

theorem run_annotations (bytes : List Byte) (fuel : Nat) (s : State) :
 (run bytes fuel s).urls = publish (reference bytes fuel s.cursor.position).comments s.urls := by
 induction fuel generalizing s with
 | zero => rfl
 | succ fuel ih =>
   simp only [run,reference,← unit_refines]
   split
   · rfl
   · rename_i u hu
     rw [ih]
     cases hc : u.comment <;>
       simp [advance,hc,publish,CommentDirectives.update_reference]

theorem run_coherent (bytes : List Byte) (read : Nat → Lexeme) (fuel : Nat) (s : State)
 (h : coherent read s) : coherent read (run bytes fuel s) := by
 intro c hc
 exact h c (by simpa [run_cache] using hc)

theorem run_project (bytes : List Byte) (names : List (List Byte)) (fuel : Nat) (s : State) :
 project names (run bytes fuel s)=project names s := by
 simp [project,cacheRelevant,run_cache,run_mode]

theorem exhaustion (bytes : List Byte) (fuel : Nat) (s : State)
 (hf : bytes.length < s.cursor.position+fuel) :
 nativeUnit (bytes.drop (run bytes fuel s).cursor.position)=none := by
 induction fuel generalizing s with
 | zero =>
   have he : bytes.drop s.cursor.position=[] := List.drop_eq_nil_iff.mpr (by omega)
   simp [run,he,nativeUnit]
 | succ fuel ih =>
   simp only [run]
   split
   · assumption
   · rename_i u hu
     apply ih
     have hp := unit_positive _ _ hu
     simp only [advance]
     omega

end WrapperWhitespace
