import Std

namespace HyphenAdmission

structure Inputs where
  bidiEnabled : Bool
  embeddingEqual : Bool
  precedingControlAbsent : Bool
  writingModeEqual : Bool
  significantTerminalNewline : Bool
  parentContentEqual : Bool
  commonAncestor : Bool
  ancestorSVG : Bool
  separatingBoundary : Bool
  sameContent : Bool
  fluidContinuation : Bool
  sameStyle : Bool
  transformEqual : Bool
  wordBreakEqual : Bool
  lineBreakEqual : Bool
  fontEqual : Bool
  languageEqual : Bool
  shapingFlagsEqual : Bool
  firstLimits : Nat × Nat × Nat
  secondLimits : Nat × Nat × Nat
  deriving DecidableEq, Repr

def nativeAllowed (i : Inputs) : Bool :=
  if i.bidiEnabled && (!i.embeddingEqual || !i.precedingControlAbsent) then false else
  if !i.writingModeEqual then false else
  if i.significantTerminalNewline then false else
  if !i.parentContentEqual &&
      (!i.commonAncestor || i.ancestorSVG || i.separatingBoundary) then false else
  if i.sameContent && !i.fluidContinuation then false else
  if i.sameStyle then true else
  if !i.transformEqual || !i.wordBreakEqual || !i.lineBreakEqual then false else
  i.fontEqual && i.languageEqual && i.shapingFlagsEqual

def forbidden (i : Inputs) : List Bool :=
  [i.bidiEnabled && !i.embeddingEqual,
   i.bidiEnabled && !i.precedingControlAbsent,
   !i.writingModeEqual,
   i.significantTerminalNewline,
   !i.parentContentEqual && !i.commonAncestor,
   !i.parentContentEqual && i.ancestorSVG,
   !i.parentContentEqual && i.separatingBoundary,
   i.sameContent && !i.fluidContinuation,
   !i.sameStyle && !i.transformEqual,
   !i.sameStyle && !i.wordBreakEqual,
   !i.sameStyle && !i.lineBreakEqual,
   !i.sameStyle && !i.fontEqual,
   !i.sameStyle && !i.languageEqual,
   !i.sameStyle && !i.shapingFlagsEqual]

def referenceAllowed (i : Inputs) : Bool := !(forbidden i).any id

theorem admission_reference (i : Inputs) : nativeAllowed i = referenceAllowed i := by
  apply Bool.eq_iff_iff.mpr
  simp [nativeAllowed, referenceAllowed, forbidden]
  grind (splits := 40)

theorem changing_limits_preserves_admission (i : Inputs)
    (first second : Nat × Nat × Nat) :
    nativeAllowed { i with firstLimits := first, secondLimits := second } = nativeAllowed i := rfl

theorem shared_style_still_checks_fluidity (i : Inputs)
    (same : i.sameContent = true) (nonfluid : i.fluidContinuation = false) :
    nativeAllowed i = false := by
  simp [nativeAllowed, same, nonfluid]

theorem accepted_word_policy_uniform (i : Inputs)
    (accepted : nativeAllowed i = true) :
    i.sameStyle = true ∨ (i.wordBreakEqual = true ∧ i.lineBreakEqual = true) := by
  by_cases h : i.sameStyle = true
  · exact Or.inl h
  · right
    simp [nativeAllowed, h] at accepted
    exact ⟨accepted.2.2.2.2.2.1.1.2, accepted.2.2.2.2.2.1.2⟩

#print axioms admission_reference
#print axioms changing_limits_preserves_admission
#print axioms shared_style_still_checks_fluidity
#print axioms accepted_word_policy_uniform
end HyphenAdmission
