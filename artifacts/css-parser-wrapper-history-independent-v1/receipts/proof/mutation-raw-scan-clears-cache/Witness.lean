import PublicEntry
set_option autoImplicit false
set_option maxHeartbeats 2000000
namespace Mutation
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


def sample : State := {constructor ⟨none,none⟩ with cache:=some ⟨0,⟨.colon,⟨1,none⟩⟩⟩}
example : (run [32] 2 sample).cache=none := by decide
end Mutation
