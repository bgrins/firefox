import Resolver

namespace LanguageBreak

structure WordLanguage where
  current : Tag := .absent
  mixed : Bool := false
  script : Bool := false
  deriving DecidableEq, Repr

def updateLanguage (p : Providers) (cache : Cache) (word : WordLanguage) (tag : Tag) : Cache × WordLanguage :=
  if word.current ≠ .absent ∧ word.current ≠ tag then
    (cache,{ word with mixed := true, script := false })
  else if word.current = .absent then
    let resolved := resolve p cache tag
    (resolved.2,{ word with current := tag, script := resolved.1 })
  else (cache,{ word with current := tag })

def flushLanguage (word : WordLanguage) : WordLanguage :=
  { word with current := .absent, mixed := false }

theorem flush_retains_script (word : WordLanguage) :
    (flushLanguage word).script = word.script := rfl

theorem flushed_first_correct (p : Providers) (cache : Cache) (word : WordLanguage) (tag : Tag)
    (valid : cache.Valid p) (stable : StableIdentity cache tag) :
    (updateLanguage p cache (flushLanguage word) tag).2.script = reference p tag := by
  simp only [updateLanguage,flushLanguage]
  simp only [ne_eq,not_true_eq_false,false_and,↓reduceIte]
  exact resolve_correct p cache tag valid stable

theorem known_mismatch (p : Providers) (cache : Cache) (word : WordLanguage) (tag : Tag)
    (known : word.current ≠ .absent) (different : word.current ≠ tag) :
    updateLanguage p cache word tag = (cache,{word with mixed := true,script := false}) := by
  simp [updateLanguage,known,different]

theorem current_same_preserves (p : Providers) (cache : Cache) (word : WordLanguage)
    (known : word.current ≠ .absent) :
    updateLanguage p cache word word.current = (cache,word) := by
  simp [updateLanguage,known]

theorem update_idempotent (p : Providers) (cache : Cache) (word : WordLanguage) (tag : Tag) :
    let next := updateLanguage p cache word tag
    updateLanguage p next.1 next.2 tag = next := by
  simp only [updateLanguage]
  split
  next mismatch => simp
  next noMismatch =>
    split
    next absent =>
      cases tag with
      | absent => simp [resolve]
      | atom id text => simp
    next known => simp_all

def updateMany (p : Providers) (tag : Tag) : Nat → Cache × WordLanguage → Cache × WordLanguage
  | 0,state => state
  | n+1,state => updateMany p tag n (updateLanguage p state.1 state.2 tag)

theorem nonempty_update_same (p : Providers) (tag : Tag) (n : Nat) (cache : Cache) (word : WordLanguage) :
    updateMany p tag (n+1) (cache,word) = updateLanguage p cache word tag := by
  induction n generalizing cache word with
  | zero => rfl
  | succ n ih =>
    simp only [updateMany]
    rw [show updateMany p tag n (updateLanguage p (updateLanguage p cache word tag).1 (updateLanguage p cache word tag).2 tag) =
        updateMany p tag n (updateLanguage p cache word tag) by rw [update_idempotent]]
    exact ih cache word

theorem mixed_flag_sticky (p : Providers) (cache : Cache) (word : WordLanguage) (tag : Tag)
    (mixed : word.mixed = true) : (updateLanguage p cache word tag).2.mixed = true := by
  unfold updateLanguage
  split
  next _ => rfl
  next _ => split <;> exact mixed

theorem native_width_update_equivalence (p : Providers) (cache : Cache) (word : WordLanguage)
    (tag : Tag) (additionalUnits : Nat) :
    updateLanguage p cache word tag = updateMany p tag (additionalUnits+1) (cache,word) :=
  (nonempty_update_same p tag additionalUnits cache word).symm

end LanguageBreak
