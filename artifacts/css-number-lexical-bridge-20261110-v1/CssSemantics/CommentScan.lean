import Std

namespace CssSemantics.CommentScan

inductive Ends : List Char → List Char → Prop where
  | close {rest} : Ends ('*' :: '/' :: rest) rest
  | step {c chars rest} : (∀ tail, c :: chars ≠ '*' :: '/' :: tail) →
      Ends chars rest → Ends (c :: chars) rest

def consumeBody : List Char → Option (List Char)
  | [] => none
  | '*' :: '/' :: rest => some rest
  | _ :: rest => consumeBody rest

theorem consumeBody_sound (chars rest : List Char) (h : consumeBody chars = some rest) : Ends chars rest := by
  induction chars using consumeBody.induct generalizing rest with
  | case1 => simp [consumeBody] at h
  | case2 tail =>
    have eq : tail = rest := Option.some.inj h
    subst rest
    exact .close
  | case3 c chars no ih =>
    have guard : ∀ tail, c :: chars ≠ '*' :: '/' :: tail := by
      intro tail eq
      cases eq
      exact no tail rfl rfl
    apply Ends.step guard
    apply ih rest
    rw [consumeBody] at h
    · exact h
    · exact no

theorem consumeBody_complete {chars rest : List Char} (h : Ends chars rest) :
    consumeBody chars = some rest := by
  induction h with
  | close => rfl
  | step no h ih =>
    rw [consumeBody]
    · exact ih
    · intro tail hc hcs
      exact no tail (by simp [hc, hcs])

theorem consumeBody_iff (chars rest : List Char) : consumeBody chars = some rest ↔ Ends chars rest :=
  ⟨consumeBody_sound chars rest, consumeBody_complete⟩

theorem Ends.suffix_length_lt {chars rest : List Char} (h : Ends chars rest) : rest.length < chars.length := by
  induction h with
  | close => simp only [List.length_cons]; omega
  | step no h ih => simp only [List.length_cons]; omega

theorem Ends.unique {chars left right : List Char} (a : Ends chars left) (b : Ends chars right) : left = right :=
  Option.some.inj ((consumeBody_complete a).symm.trans (consumeBody_complete b))

end CssSemantics.CommentScan
