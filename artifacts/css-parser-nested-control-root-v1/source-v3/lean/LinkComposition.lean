import LinkEmpty
set_option autoImplicit false
namespace LinkComposition
open PublicCache

def body (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (program : List Byte → WrapperControl.Program) (s : NestedControl.State) : Bool × NestedControl.State :=
  let result := WrapperControl.native bytes read names (program s.stops) s.core
  (result.1,{s with core := result.2})

theorem entirely_program (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (program : List Byte → WrapperControl.Program) (s : NestedControl.State) :
    LinkEmpty.entirely bytes read names (body bytes read names program) s =
      body bytes read names (fun stops => .entirely (program stops) stops) s := by
  cases h : (WrapperControl.native bytes read names (program s.stops) s.core).1 <;>
    simp [LinkEmpty.entirely,body,WrapperControl.native,h]

def success : NestedControl.Outcome → Bool
  | .parsed value => value
  | _ => false

theorem nested_program (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (program : List Byte → WrapperControl.Program) (s : NestedControl.State) :
    LinkEmpty.nested bytes read names (body bytes read names program) s =
      let result := NestedControl.native bytes read names program s
      (success result.1,result.2) := by
  cases hp : s.core.cursor.pending with
  | none => simp [LinkEmpty.nested,NestedControl.native,hp,success]
  | some block =>
    by_cases hg : (s.depth.val ≥ s.limit.val && s.limit.val != 0) = true
    · simp [LinkEmpty.nested,NestedControl.native,hp,hg,success]
    · simp [LinkEmpty.nested,NestedControl.native,hp,hg,entirely_program,body,success]

theorem until_program (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
    (extra : List Byte) (program : List Byte → WrapperControl.Program) (s : NestedControl.State) :
    LinkEmpty.untilBounded bytes read names extra (body bytes read names program) s =
      NestedControl.untilBefore bytes read names extra false program s := by
  simp only [LinkEmpty.untilBounded,entirely_program,body,NestedControl.untilBefore]
  rfl

end LinkComposition
