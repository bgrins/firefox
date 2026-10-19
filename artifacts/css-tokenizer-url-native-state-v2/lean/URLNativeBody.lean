import URLNativeEnd
import URLNativeEscape
import URLNativeAlignment
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeBody
open URLNativeState URLNativeEnd URLNativeAlignment
abbrev Byte := CommentScan.Byte

def run : List Byte → State → Result
 | [], s => ⟨s,none⟩
 | b::bs, s => match URLScan.nativeClass b with
   | .close => ⟨advance s 1,none⟩
   | .invalid => bad bs (advance s 1)
   | .space => URLNativeEnd.run (b::bs) s
   | .nul => run bs (advance s 1)
   | .copy => run bs (known s b)
   | .escape => if URLScan.newline bs then bad bs (advance s 1)
     else run (bs.drop (Escape.native bs).count) (URLNativeEscape.run bs (advance s 1))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

def Admitted : List Byte → State → Prop
 | [], _ => True
 | b::bs, s => match URLScan.nativeClass b with
   | .close => True
   | .invalid => URLNativeBadState.Admitted bs (advance s 1)
   | .space => URLNativeEnd.Admitted (b::bs) s
   | .nul => Admitted bs (advance s 1)
   | .copy => Admitted bs (known s b)
   | .escape => if URLScan.newline bs then URLNativeBadState.Admitted bs (advance s 1)
     else URLNativeEscape.Admitted bs (advance s 1) ∧
       Admitted (bs.drop (Escape.native bs).count) (URLNativeEscape.run bs (advance s 1))
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

theorem escape_byte : ∀ b : Byte, URLScan.nativeClass b=.escape → b=92 := by decide

theorem escape_position (bs : List Byte) (s : State) (hv : StringUTF8.Valid bs) :
 (URLNativeEscape.run bs (advance s 1)).position=s.position+1+(Escape.native bs).count := by
 obtain ⟨units,rfl⟩ := hv
 exact URLNativeEscape.position units (advance s 1)

theorem position (xs : List Byte) (s : State) (hv : TailValid xs) :
 (run xs s).state.position=s.position+(URLTrace.run xs).value.count := by
 induction xs,s using run.induct with
 | case1 s => simp [run,URLTrace.run]
 | case2 b bs s hc => simp [run,URLTrace.run,hc,advance]
 | case3 b bs s hc =>
   simpa [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using bad_position bs (advance s 1)
 | case4 b bs s hc => simpa [run,URLTrace.run,hc] using URLNativeEnd.position (b::bs) s
 | case5 b bs s hc ih =>
   simpa [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using ih (tail b bs hv)
 | case6 b bs s hc ih =>
   simpa [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,URLNativeBad.known_position,Nat.add_assoc] using ih (tail b bs hv)
 | case7 b bs s hc hn =>
   simpa [run,URLTrace.run,hc,hn,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using bad_position bs (advance s 1)
 | case8 b bs s hc hn ih =>
   have hb : b=92 := escape_byte b hc
   have hu := ascii_tail b bs hv (by rw [hb]; decide)
   have hi := ih (escape_rest bs hu)
   have hp := escape_position bs s hu
   have bound := Escape.consumption_bound bs
   simpa [run,URLTrace.run,hc,hn,URLTrace.add,URLScan.extend,List.length_take,Nat.min_eq_left bound,hp,Nat.add_assoc,Nat.add_comm 1] using hi

theorem capture (xs : List Byte) (s : State) (hv : TailValid xs) :
 (run xs s).rawEnd = if (URLTrace.run xs).value.kind=.bad then
  some (s.position+(URLTrace.run xs).value.count-if (URLTrace.run xs).closed then 1 else 0) else none := by
 induction xs,s using run.induct with
 | case1 s => simp [run,URLTrace.run]
 | case2 b bs s hc => simp [run,URLTrace.run,hc,advance]
 | case3 b bs s hc =>
   simp only [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,URLTrace.bad]
   have he := bad_capture bs (advance s 1)
   simp [advance,URLTrace.bad,Nat.add_assoc] at he ⊢
   exact he
 | case4 b bs s hc => simpa [run,URLTrace.run,hc] using URLNativeEnd.capture (b::bs) s
 | case5 b bs s hc ih =>
   simpa [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using ih (tail b bs hv)
 | case6 b bs s hc ih =>
   simpa [run,URLTrace.run,hc,URLTrace.add,URLScan.extend,URLNativeBad.known_position,Nat.add_assoc] using ih (tail b bs hv)
 | case7 b bs s hc hn =>
   simp only [run,URLTrace.run,hc,hn,↓reduceIte,URLTrace.add,URLScan.extend,URLTrace.bad]
   have he := bad_capture bs (advance s 1)
   simp [advance,URLTrace.bad,Nat.add_assoc] at he ⊢
   exact he
 | case8 b bs s hc hn ih =>
   have hb : b=92 := escape_byte b hc
   have hu := ascii_tail b bs hv (by rw [hb]; decide)
   have hi := ih (escape_rest bs hu)
   have hp := escape_position bs s hu
   have bound := Escape.consumption_bound bs
   simp [run,URLTrace.run,hc,hn,URLTrace.add,URLScan.extend,List.length_take,Nat.min_eq_left bound,hp,Nat.add_assoc,Nat.add_comm 1] at hi ⊢
   exact hi
end URLNativeBody
