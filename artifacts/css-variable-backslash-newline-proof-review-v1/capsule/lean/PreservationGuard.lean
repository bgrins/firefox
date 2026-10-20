import ProtectedSpan
set_option autoImplicit false
namespace ProtectedSpan

theorem persistent_from (flag : Bool) (ts : List Token) :
    ts.foldl persistentStep flag =
      ((ts.filter (fun t => !white t)).getLast?.map Token.backslash).getD flag := by
  induction ts generalizing flag with
  | nil => rfl
  | cons t ts ih =>
    simp only [List.foldl_cons]
    rw [ih]
    cases hw : white t <;> cases hl : (ts.filter (fun t => !white t)).getLast? <;>
      simp [persistentStep,hw,List.filter,List.getLast?_cons,hl]

theorem split_head (ts : List Token) :
    (splitRev ts).1.head? = (ts.filter (fun t => !white t)).head? := by
  induction ts with
  | nil => rfl
  | cons t ts ih => cases h : white t <;> simp [splitRev,List.filter,h,ih]

theorem basePrefix_last (ts : List Token) :
    (basePrefix ts).getLast? = (ts.filter (fun t => !white t)).getLast? := by
  have h := split_head ts.reverse
  simpa [basePrefix,←List.head?_reverse,List.filter_reverse] using h

theorem persistent_prefix (ts : List Token) :
    persistent ts = ((basePrefix ts).getLast?.map Token.backslash).getD false := by
  rw [persistent,persistent_from,basePrefix_last]

theorem guard_with_suffix (ts : List Token) (nonempty : suffix ts ≠ []) :
    persistent ts = protect ts := by
  simp [protect,nonempty,persistent_prefix]

def NoTerminalBackslash (ts : List Token) : Prop :=
  ∀ t ∈ ts.getLast?, t.backslash=false

theorem standalone_guard (ts : List Token) (terminal : NoTerminalBackslash ts) :
    persistent ts = protect ts := by
  by_cases h : suffix ts=[]
  · have hp : basePrefix ts=ts := by simpa [h] using suffix_partition ts
    have value : ((basePrefix ts).getLast?.map Token.backslash).getD false=false := by
      rw [hp]
      cases hl : ts.getLast? with
      | none => simp [hl]
      | some t => simpa [hl] using terminal t (by simp [hl])
    simp [persistent_prefix,value,protect,h]
  · exact guard_with_suffix ts h

def startsNewline (raw : List UInt8) : Prop :=
  raw.head? = some 10 ∨ raw.head? = some 12 ∨ raw.head? = some 13

def Followed : List Token → Prop
  | [] => True
  | t::ts => (t.backslash=true → ∃ u rest, ts=u::rest ∧ white u=true ∧ startsNewline u.raw) ∧ Followed ts

theorem followed_terminal (ts : List Token) (h : Followed ts) : NoTerminalBackslash ts := by
  induction ts with
  | nil => simp [NoTerminalBackslash]
  | cons t ts ih =>
    cases ts with
    | nil =>
      intro u hu
      have eq : t=u := by simpa using hu
      subst u
      cases hb : t.backslash
      · rfl
      · obtain ⟨v,rest,impossible,_,_⟩ := h.1 hb
        contradiction
    | cons v vs =>
      have tail := ih h.2
      simpa [NoTerminalBackslash,List.getLast?_cons] using tail

theorem admitted_standalone_guard (ts : List Token) (h : Followed ts) :
    persistent ts = protect ts := standalone_guard ts (followed_terminal ts h)

theorem protected_extent_zero (ts : List Token) (co : coalesced ts.reverse)
    (hp : protect ts=true) : (scan {} ts).trailing=0 := by
  rw [←removed_extent ts co]
  simp [removed,hp,bytes]

theorem protected_bytes (ts : List Token) (co : coalesced ts.reverse)
    (hp : protect ts=true) : stored ts=bytes ts := by
  rw [exact_prefix ts co]
  simp [retained,hp]

theorem ordinary_reset (s : State) (t : Token) (h : t.backslash=false) :
    (step s t).previousBackslash=false := h

end ProtectedSpan
