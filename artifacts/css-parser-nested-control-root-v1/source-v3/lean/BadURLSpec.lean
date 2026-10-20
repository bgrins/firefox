import BadURLEscape
import StringUTF8
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace BadURLSpec
open BadURL BadURLEscape
abbrev Unit := Boundary.Unit
abbrev bytes := Boundary.bytes

def newline (xs : List Byte) : Bool := xs.head?.any (fun b => [10,12,13].contains b.val)

def reference : Nat → List Byte → End
 | 0, _ => ⟨0,false⟩
 | _+1, [] => ⟨0,false⟩
 | fuel+1, b::bs =>
   if b == 41 then ⟨1,true⟩
   else if b == 92 && !newline bs then
     let e := Escape.reference bs
     add (1+e.count) (reference fuel (bs.drop e.count))
   else
     let count := min (Escape.width b) (b::bs).length
     add count (reference fuel ((b::bs).drop count))

theorem ordinary_group (u : Unit) (us : List Unit) (notClose : u.first ≠ 41)
 (ordinary : u.first ≠ 92 ∨ newline (bytes us) = true) :
 native (bytes (u::us)) = add u.bytes.length (native (bytes us)) := by
 have plain (notSlash : u.first ≠ 92) : native (bytes (u::us)) = add u.bytes.length (native (bytes us)) := by
   have safe : ∀ b ∈ u.bytes, Safe b := by
     intro b hb
     rcases List.mem_cons.mp hb with rfl | hb
     · exact ⟨notClose,notSlash⟩
     · have hc := u.continuation b hb
       constructor
       · intro he; have hv := congrArg Fin.val he; change b.val = 41 at hv; omega
       · intro he; have hv := congrArg Fin.val he; change b.val = 92 at hv; omega
   exact safe_prefix u.bytes (bytes us) safe
 rcases ordinary with notSlash | nl
 · exact plain notSlash
 · by_cases hs : u.first = 92
   · have empty := Boundary.unit_ascii_singleton u (by rw [hs]; decide)
     have h41 : (bytes us).head? ≠ some 41 := by
       intro h; simp [newline,h] at nl; change 41=10 ∨ 41=12 ∨ 41=13 at nl; omega
     have h92 : (bytes us).head? ≠ some 92 := by
       intro h; simp [newline,h] at nl; change 92=10 ∨ 92=12 ∨ 92=13 at nl; omega
     have form : bytes (u::us) = 92::bytes us := by simp [Boundary.bytes,Boundary.Unit.bytes,hs,empty]
     rw [form]
     simp [native,h41,h92,Boundary.Unit.bytes,empty]
   · exact plain hs

theorem escape_group (units : List Unit) :
 native (92::bytes units) =
 add (1+(Escape.reference (bytes units)).count)
 (native ((bytes units).drop (Escape.reference (bytes units)).count)) := by
 rw [← Escape.native_reference]
 cases units with
 | nil => simp [Boundary.bytes,Escape.native,native,add]
 | cons u us => exact escape_grouping u us

theorem full_reference (fuel : Nat) (units : List Unit) (enough : (bytes units).length ≤ fuel) :
 reference fuel (bytes units) = native (bytes units) := by
 induction fuel generalizing units with
 | zero =>
   have empty : bytes units = [] := by simpa using enough
   simp [empty,reference,native]
 | succ fuel ih =>
   cases units with
   | nil => simp [reference,native,Boundary.bytes]
   | cons u us =>
     have form : bytes (u::us) = u.first::(u.rest++bytes us) := rfl
     by_cases close : u.first = 41
     · simp [form,reference,native,close]
     · by_cases escape : u.first = 92 ∧ newline (u.rest++bytes us) = false
       · have empty := Boundary.unit_ascii_singleton u (by rw [escape.1]; decide)
         have hx : bytes (u::us) = 92::bytes us := by simp [form,escape.1,empty]
         have valid := (StringUTF8.escape_valid us).2
         obtain ⟨rest,hr⟩ := valid
         change (bytes us).drop (Escape.native (bytes us)).count = bytes rest at hr
         have er : (Escape.reference (bytes us)).count = (Escape.native (bytes us)).count := by rw [Escape.native_reference]
         have bound : (bytes rest).length ≤ fuel := by
           rw [← hr]
           have hb := Escape.consumption_bound (bytes us)
           simp only [hx,List.length_cons] at enough
           simp only [List.length_drop]
           omega
         have recur := ih rest bound
         rw [← hr] at recur
         rw [hx,reference]
         simp only [BEq.rfl,Bool.true_and,Bool.not_eq_true',Bool.false_eq_true,↓reduceIte]
         have nl : newline (bytes us) = false := by simpa [empty] using escape.2
         simp only [nl,Bool.not_false,↓reduceIte]
         rw [er,recur]
         simpa only [er,show ((92:Byte)==41)=false by decide,Bool.false_eq_true,↓reduceIte] using (escape_group us).symm
       · have ordinary : u.first ≠ 92 ∨ newline (bytes us) = true := by
           by_cases hs : u.first = 92
           · have empty := Boundary.unit_ascii_singleton u (by rw [hs]; decide)
             right
             have hn : newline (bytes us) ≠ false := by simpa [hs,empty] using escape
             simpa using hn
           · exact Or.inl hs
         have count : min (Escape.width u.first) (bytes (u::us)).length = u.bytes.length := by
           have hw := u.lengthWidth
           simp only [Boundary.bytes,List.flatMap_cons,List.length_append,Boundary.Unit.bytes,List.length_cons]
           omega
         have drop : (bytes (u::us)).drop u.bytes.length = bytes us := by
           change (u.bytes++bytes us).drop u.bytes.length = bytes us
           simp
         have bound : (bytes us).length ≤ fuel := by
           simp only [form,List.length_cons,List.length_append] at enough
           omega
         have recur := ih us bound
         have ce : (u.first == 41) = false := by simpa using close
         have ee : (u.first == 92 && !newline (u.rest++bytes us)) = false := by simp_all
         rw [form,reference]
         simp only [ce,ee,↓reduceIte]
         rw [← form,count,drop,recur]
         exact (ordinary_group u us close ordinary).symm

theorem semantic_boundary (units : List Unit) :
 reference (bytes units).length (bytes units) = BadURL.reference (bytes units) := by
 rw [full_reference _ units (by omega),BadURL.native_reference]

theorem residual_valid (units : List Unit) :
 StringUTF8.Valid ((bytes units).drop (native (bytes units)).count) := by
 generalize heq : (bytes units).length = n
 induction n using Nat.strongRecOn generalizing units with
 | ind n ih =>
   cases units with
   | nil => simpa [Boundary.bytes,native] using StringUTF8.valid_nil
   | cons u us =>
     have shorter : (bytes us).length < n := by
       change (u.first::(u.rest++bytes us)).length = n at heq
       simp only [List.length_cons,List.length_append] at heq
       omega
     by_cases close : u.first=41
     · have empty := Boundary.unit_ascii_singleton u (by rw [close]; decide)
       simpa [Boundary.bytes,Boundary.Unit.bytes,empty,close,native] using (show StringUTF8.Valid (bytes us) from ⟨us,rfl⟩)
     · by_cases slash : u.first=92
       · have empty := Boundary.unit_ascii_singleton u (by rw [slash]; decide)
         have form : bytes (u::us)=92::bytes us := by simp [Boundary.bytes,Boundary.Unit.bytes,empty,slash]
         obtain ⟨remaining,hr⟩ := (StringUTF8.escape_valid us).2
         change (bytes us).drop (Escape.native (bytes us)).count = bytes remaining at hr
         have small : (bytes remaining).length < n := by rw [← hr,List.length_drop]; omega
         have ht := ih (bytes remaining).length small remaining rfl
         rw [← hr] at ht
         rw [form,escape_group,← Escape.native_reference]
         change StringUTF8.Valid ((92::bytes us).drop ((1+(Escape.native (bytes us)).count)+(native ((bytes us).drop (Escape.native (bytes us)).count)).count))
         rw [show (1+(Escape.native (bytes us)).count)+(native ((bytes us).drop (Escape.native (bytes us)).count)).count = ((Escape.native (bytes us)).count+(native ((bytes us).drop (Escape.native (bytes us)).count)).count)+1 by omega]
         simpa only [List.drop_succ_cons,← List.drop_drop] using ht
       · have ht := ih (bytes us).length shorter us rfl
         rw [ordinary_group u us close (Or.inl slash)]
         change StringUTF8.Valid ((u.bytes++bytes us).drop (u.bytes.length+(native (bytes us)).count))
         simpa [← List.drop_drop] using ht

end BadURLSpec
