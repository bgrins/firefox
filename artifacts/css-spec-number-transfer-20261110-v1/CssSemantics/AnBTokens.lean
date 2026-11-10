import CssSemantics.CommentScan
import Init.Data.Nat.ToString

namespace CssSemantics.AnBTokens

inductive Sign where
  | plus | minus
  deriving DecidableEq, BEq, Repr

structure IntegerToken where
  sign : Option Sign
  magnitude : Nat
  deriving DecidableEq, BEq, Repr

def IntegerToken.value (token : IntegerToken) : Int :=
  match token.sign with
  | some .minus => -(Int.ofNat token.magnitude)
  | _ => Int.ofNat token.magnitude

inductive Token where
  | space
  | ident (name : String)
  | delimPlus | delimMinus
  | number (integer : IntegerToken)
  | dimension (integer : IntegerToken) (unit : String)
  deriving DecidableEq, BEq, Repr

def digit (c : Char) : Bool := c.isDigit
def letter (c : Char) : Bool := ('a' ≤ c && c ≤ 'z') || ('A' ≤ c && c ≤ 'Z')
def identStart (c : Char) : Bool := letter c || c == '_'
def identChar (c : Char) : Bool := identStart c || digit c || c == '-'
def whitespace (c : Char) : Bool :=
  c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\x0c'

def startsIdent : List Char → Bool
  | '-' :: c :: _ => identStart c || c == '-'
  | c :: _ => identStart c
  | _ => false

def isIdent (name : String) : Bool :=
  startsIdent name.toList && name.toList.all identChar

def startsExponent : List Char → Bool
  | e :: rest =>
      if e == 'e' || e == 'E' then
        match rest with
        | '+' :: c :: _ | '-' :: c :: _ => digit c
        | c :: _ => digit c
        | _ => false
      else false
  | _ => false

def startsFraction : List Char → Bool
  | '.' :: c :: _ => digit c
  | _ => false

def Token.Valid : Token → Prop
  | .ident name => isIdent name = true
  | .dimension _ unit => isIdent unit = true ∧ startsExponent unit.toList = false
  | _ => True

def digitValue (c : Char) : Nat := c.toNat - 48
def magnitude (digits : List Char) : Nat :=
  digits.foldl (fun value c => value * 10 + digitValue c) 0

def Digits (source : String) (value : Nat) : Prop :=
  source.toList ≠ [] ∧ source.toList.all digit = true ∧ magnitude source.toList = value

def parseDigits (source : String) : Option Nat :=
  if source.toList ≠ [] ∧ source.toList.all digit = true then
    some (magnitude source.toList)
  else none

def renderMagnitude (value : Nat) : String := String.ofList (Nat.toDigits 10 value)

theorem parseDigits_iff (source : String) (value : Nat) :
    parseDigits source = some value ↔ Digits source value := by
  unfold parseDigits
  split
  next yes =>
    simp only [Option.some.injEq]
    exact ⟨fun h => ⟨yes.1, yes.2, h⟩, fun h => h.2.2⟩
  next no =>
    constructor
    · intro h; cases h
    · intro h; exact False.elim (no ⟨h.1, h.2.1⟩)

theorem magnitude_append_digit (digits : List Char) (c : Char) :
    magnitude (digits ++ [c]) = magnitude digits * 10 + digitValue c := by
  simp [magnitude, List.foldl_append]

theorem magnitude_toDigits (value : Nat) : magnitude (Nat.toDigits 10 value) = value := by
  induction value using Nat.strongRecOn with
  | ind value ih =>
      by_cases small : value < 10
      · rw [Nat.toDigits_of_lt_base small]
        simp [magnitude, digitValue, Nat.toNat_digitChar_sub_48_of_lt_ten small]
      · rw [Nat.toDigits_of_base_le (by decide) (by omega), magnitude_append_digit,
          ih (value / 10) (Nat.div_lt_self (by omega) (by decide))]
        have digitEq := Nat.toNat_digitChar_sub_48_of_lt_ten (Nat.mod_lt value (by decide : 0 < 10))
        simp only [digitValue, digitEq]
        omega

theorem parseDigits_renderMagnitude (value : Nat) :
    parseDigits (renderMagnitude value) = some value := by
  apply (parseDigits_iff _ _).mpr
  refine ⟨?_, ?_, ?_⟩
  · simp [renderMagnitude]
  · simp only [renderMagnitude, String.toList_ofList, List.all_eq_true]
    intro c member
    exact Nat.isDigit_of_mem_toDigits (by decide) (by decide) member
  · simpa [renderMagnitude] using magnitude_toDigits value

def Boundary (predicate : Char → Bool) (rest : List Char) : Prop :=
  ∀ c cs, rest = c :: cs → predicate c = false

theorem boundary_drop (predicate : Char → Bool) (chars : List Char) :
    Boundary predicate (chars.dropWhile predicate) := by
  intro c cs same
  have h := List.head?_dropWhile_not predicate chars
  rw [same] at h
  exact h

theorem boundary_split (predicate : Char → Bool) (word rest : List Char)
    (all : ∀ c ∈ word, predicate c = true) (boundary : Boundary predicate rest) :
    (word ++ rest).takeWhile predicate = word ∧ (word ++ rest).dropWhile predicate = rest := by
  have stop : rest.takeWhile predicate = [] ∧ rest.dropWhile predicate = rest := by
    cases rest with
    | nil => simp
    | cons c cs => simp [boundary c cs rfl]
  simp [List.takeWhile_append_of_pos all, List.dropWhile_append_of_pos all, stop.1, stop.2]

inductive DigitRun : List Char → Nat → List Char → Prop where
  | run (word rest) : word ≠ [] → (∀ c ∈ word, digit c = true) → Boundary digit rest →
      DigitRun (word ++ rest) (magnitude word) rest

def scanDigits (input : List Char) : Option (Nat × List Char) :=
  let word := input.takeWhile digit
  if word = [] then none else some (magnitude word, input.dropWhile digit)

theorem scanDigits_sound {input rest : List Char} {value : Nat}
    (h : scanDigits input = some (value, rest)) : DigitRun input value rest := by
  dsimp only [scanDigits] at h
  split at h
  next empty => cases h
  next nonempty =>
    have eq : (magnitude (input.takeWhile digit), input.dropWhile digit) = (value, rest) := Option.some.inj h
    cases eq
    have result := DigitRun.run (input.takeWhile digit) (input.dropWhile digit) nonempty
      (List.all_eq_true.mp List.all_takeWhile) (boundary_drop digit input)
    simpa only [List.takeWhile_append_dropWhile] using result

theorem DigitRun.result {input rest : List Char} {value : Nat}
    (h : DigitRun input value rest) : scanDigits input = some (value, rest) := by
  cases h with
  | run word rest nonempty all boundary =>
      have split := boundary_split digit word rest all boundary
      simp [scanDigits, split.1, split.2, nonempty]

theorem scanDigits_iff (input rest : List Char) (value : Nat) :
    scanDigits input = some (value, rest) ↔ DigitRun input value rest :=
  ⟨scanDigits_sound, DigitRun.result⟩

theorem DigitRun.suffix_length_lt {input rest : List Char} {value : Nat}
    (h : DigitRun input value rest) : rest.length < input.length := by
  cases h with
  | run word rest nonempty _ _ => simp; have := List.length_pos_iff.mpr nonempty; omega

theorem DigitRun.boundary {input rest : List Char} {value : Nat}
    (h : DigitRun input value rest) : Boundary digit rest := by
  cases h with
  | run _ _ _ _ boundary => exact boundary

theorem DigitRun.head_digit {input rest : List Char} {value : Nat}
    (h : DigitRun input value rest) : ∃ c cs, input = c :: cs ∧ digit c = true := by
  cases h with
  | run word rest nonempty all _ =>
      cases word with
      | nil => exact False.elim (nonempty rfl)
      | cons c cs => exact ⟨c, cs ++ rest, rfl, all c (by simp)⟩

theorem digit_not_sign {c : Char} (h : digit c = true) : c ≠ '+' ∧ c ≠ '-' := by
  constructor <;> intro same <;> subst c <;> contradiction

inductive IntegerRun : List Char → IntegerToken → List Char → Prop where
  | unsigned {input value rest} : DigitRun input value rest → IntegerRun input ⟨none, value⟩ rest
  | plus {input value rest} : DigitRun input value rest → IntegerRun ('+' :: input) ⟨some .plus, value⟩ rest
  | minus {input value rest} : DigitRun input value rest → IntegerRun ('-' :: input) ⟨some .minus, value⟩ rest

def scanInteger : List Char → Option (IntegerToken × List Char)
  | '+' :: rest => (scanDigits rest).map fun (value, suffix) => (⟨some .plus, value⟩, suffix)
  | '-' :: rest => (scanDigits rest).map fun (value, suffix) => (⟨some .minus, value⟩, suffix)
  | input => (scanDigits input).map fun (value, suffix) => (⟨none, value⟩, suffix)

theorem scanInteger_sound {input rest : List Char} {integer : IntegerToken}
    (h : scanInteger input = some (integer, rest)) : IntegerRun input integer rest := by
  unfold scanInteger at h
  split at h
  all_goals obtain ⟨⟨value, suffix⟩, found, equal⟩ := Option.map_eq_some_iff.mp h
  all_goals cases equal
  · exact .plus (scanDigits_sound found)
  · exact .minus (scanDigits_sound found)
  · exact .unsigned (scanDigits_sound found)

theorem IntegerRun.result {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : scanInteger input = some (integer, rest) := by
  cases h with
  | unsigned digits =>
      obtain ⟨c, cs, shape, head⟩ := digits.head_digit
      obtain ⟨plus, minus⟩ := digit_not_sign head
      rw [shape] at digits ⊢
      simp [scanInteger, plus, minus, digits.result]
  | plus digits => simp [scanInteger, digits.result]
  | minus digits => simp [scanInteger, digits.result]

theorem scanInteger_iff (input rest : List Char) (integer : IntegerToken) :
    scanInteger input = some (integer, rest) ↔ IntegerRun input integer rest :=
  ⟨scanInteger_sound, IntegerRun.result⟩

theorem IntegerRun.suffix_length_lt {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : rest.length < input.length := by
  cases h with
  | unsigned digits => exact digits.suffix_length_lt
  | plus digits | minus digits => have := digits.suffix_length_lt; simp; omega

theorem IntegerRun.boundary {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : Boundary digit rest := by
  cases h <;> rename_i digits <;> exact digits.boundary

theorem startsIdent_takeWhile {input : List Char} (h : startsIdent input = true) :
    isIdent (String.ofList (input.takeWhile identChar)) = true := by
  have all : (input.takeWhile identChar).all identChar = true := List.all_takeWhile
  simp only [isIdent, String.toList_ofList, all, Bool.and_true]
  cases input with
  | nil => simp [startsIdent] at h
  | cons c cs =>
      by_cases minus : c = '-'
      · subst c
        cases cs with
        | nil => simp [startsIdent, identStart, letter] at h
        | cons d ds =>
            have hd : identChar d = true := by
              simp only [startsIdent, Bool.or_eq_true] at h
              rcases h with first | hyphen
              · simp [identChar, first]
              · simp [identChar, hyphen]
            simp only [List.takeWhile_cons, show identChar '-' = true from by decide, hd,
              ↓reduceIte]
            exact h
      · have first : identStart c = true := by simpa [startsIdent, minus] using h
        have hc : identChar c = true := by simp [identChar, first]
        simp [hc, startsIdent, minus, first]

theorem startsIdent_append {name rest : List Char} (h : startsIdent name = true) :
    startsIdent (name ++ rest) = true := by
  cases name with
  | nil => simp [startsIdent] at h
  | cons c cs =>
      by_cases minus : c = '-'
      · subst c
        cases cs with
        | nil => simp [startsIdent, identStart, letter] at h
        | cons d ds => simpa [startsIdent] using h
      · simpa [startsIdent, minus] using h

inductive NumericRun : List Char → Token → List Char → Prop where
  | number {input integer rest} : IntegerRun input integer rest →
      startsFraction rest = false → startsExponent rest = false → startsIdent rest = false →
      NumericRun input (.number integer) rest
  | dimension {input integer unit rest} : IntegerRun input integer (unit.toList ++ rest) →
      isIdent unit = true → Boundary identChar rest →
      startsFraction (unit.toList ++ rest) = false → startsExponent (unit.toList ++ rest) = false →
      NumericRun input (.dimension integer unit) rest

def scanNumeric (input : List Char) : Option (Token × List Char) := do
  let (integer, rest) ← scanInteger input
  if startsFraction rest || startsExponent rest then none
  else if startsIdent rest then
    some (.dimension integer (String.ofList (rest.takeWhile identChar)), rest.dropWhile identChar)
  else some (.number integer, rest)

theorem scanNumeric_sound {input rest : List Char} {token : Token}
    (h : scanNumeric input = some (token, rest)) : NumericRun input token rest := by
  cases integerFound : scanInteger input with
  | none => simp [scanNumeric, integerFound] at h
  | some pair =>
    obtain ⟨integer, suffix⟩ := pair
    simp only [scanNumeric, integerFound] at h
    change (if startsFraction suffix || startsExponent suffix then none
      else if startsIdent suffix then
        some (.dimension integer (String.ofList (suffix.takeWhile identChar)), suffix.dropWhile identChar)
      else some (.number integer, suffix)) = some (token, rest) at h
    split at h
    next bad => cases h
    next good =>
      have good' : startsFraction suffix = false ∧ startsExponent suffix = false := by
        simpa only [Bool.not_eq_true, Bool.or_eq_false_iff] using good
      split at h
      next ident =>
        cases h
        have parsed : IntegerRun input integer
            ((String.ofList (suffix.takeWhile identChar)).toList ++ suffix.dropWhile identChar) := by
          simpa using scanInteger_sound integerFound
        apply NumericRun.dimension parsed (startsIdent_takeWhile ident) (boundary_drop identChar suffix)
        · simpa using good'.1
        · simpa using good'.2
      next notIdent =>
        cases h
        exact .number (scanInteger_sound integerFound) good'.1 good'.2 (by simpa using notIdent)

theorem NumericRun.result {input rest : List Char} {token : Token}
    (h : NumericRun input token rest) : scanNumeric input = some (token, rest) := by
  cases h with
  | number integer fraction exponent ident => simp [scanNumeric, integer.result, fraction, exponent, ident]
  | @dimension integer unit rest parsed valid boundary fraction exponent =>
      have valid' : startsIdent unit.toList = true ∧ ∀ c ∈ unit.toList, identChar c = true := by
        simpa only [isIdent, Bool.and_eq_true, List.all_eq_true] using valid
      have split := boundary_split identChar unit.toList rest valid'.2 boundary
      simp [scanNumeric, parsed.result, fraction, exponent, startsIdent_append valid'.1,
        split.1, split.2]

theorem scanNumeric_iff (input rest : List Char) (token : Token) :
    scanNumeric input = some (token, rest) ↔ NumericRun input token rest :=
  ⟨scanNumeric_sound, NumericRun.result⟩

theorem NumericRun.suffix_length_lt {input rest : List Char} {token : Token}
    (h : NumericRun input token rest) : rest.length < input.length := by
  cases h with
  | number parsed _ _ _ => exact parsed.suffix_length_lt
  | dimension parsed _ _ _ _ => have := parsed.suffix_length_lt; simp at this; omega

def startsNumeric : List Char → Bool
  | '+' :: c :: _ | '-' :: c :: _ => digit c
  | c :: _ => digit c
  | _ => false

theorem whitespace_not_digit {c : Char} (h : whitespace c = true) : digit c = false := by
  simp only [whitespace, Bool.or_eq_true, beq_iff_eq] at h
  rcases h with (((rfl | rfl) | rfl) | rfl) | rfl <;> decide

theorem whitespace_not_identStart {c : Char} (h : whitespace c = true) : identStart c = false := by
  simp only [whitespace, Bool.or_eq_true, beq_iff_eq] at h
  rcases h with (((rfl | rfl) | rfl) | rfl) | rfl <;> decide

theorem digit_not_identStart {c : Char} (h : digit c = true) : identStart c = false := by
  simp [digit, Char.isDigit, identStart, letter, Char.le_def, UInt32.le_iff_toNat_le] at *
  constructor
  · omega
  · rintro rfl; simp at h

theorem digit_not_whitespace {c : Char} (h : digit c = true) : whitespace c = false := by
  cases ws : whitespace c
  · rfl
  · have := whitespace_not_digit ws; simp_all

theorem identStart_not_digit {c : Char} (h : identStart c = true) : digit c = false := by
  cases d : digit c
  · rfl
  · have := digit_not_identStart d; simp_all

theorem identStart_not_whitespace {c : Char} (h : identStart c = true) : whitespace c = false := by
  cases ws : whitespace c
  · rfl
  · have := whitespace_not_identStart ws; simp_all

theorem IntegerRun.starts {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : startsNumeric input = true := by
  cases h with
  | unsigned digits =>
      obtain ⟨c, cs, rfl, head⟩ := digits.head_digit
      obtain ⟨plus, minus⟩ := digit_not_sign head
      simp [startsNumeric, plus, minus, head]
  | plus digits | minus digits =>
      obtain ⟨c, cs, rfl, head⟩ := digits.head_digit
      exact head

theorem NumericRun.starts {input rest : List Char} {token : Token}
    (h : NumericRun input token rest) : startsNumeric input = true := by
  cases h <;> rename_i parsed _ _ _ <;> exact parsed.starts

def headWhitespace (input : List Char) : Bool := input.head?.any whitespace

inductive TokenRun : List Char → Token → List Char → Prop where
  | space (word rest) : word ≠ [] → (∀ c ∈ word, whitespace c = true) → Boundary whitespace rest →
      TokenRun (word ++ rest) .space rest
  | numeric {input token rest} : headWhitespace input = false →
      NumericRun input token rest → TokenRun input token rest
  | ident {name rest} : isIdent name = true → Boundary identChar rest →
      headWhitespace (name.toList ++ rest) = false → startsNumeric (name.toList ++ rest) = false →
      TokenRun (name.toList ++ rest) (.ident name) rest
  | plus (rest) : startsNumeric ('+' :: rest) = false → TokenRun ('+' :: rest) .delimPlus rest
  | minus (rest) : startsNumeric ('-' :: rest) = false → startsIdent ('-' :: rest) = false →
      TokenRun ('-' :: rest) .delimMinus rest

def scanToken (input : List Char) : Option (Token × List Char) :=
  if headWhitespace input then some (.space, input.dropWhile whitespace)
  else if startsNumeric input then scanNumeric input
  else if startsIdent input then
    some (.ident (String.ofList (input.takeWhile identChar)), input.dropWhile identChar)
  else match input with
    | '+' :: rest => some (.delimPlus, rest)
    | '-' :: rest => some (.delimMinus, rest)
    | _ => none

theorem headWhitespace_nonempty {input : List Char} (h : headWhitespace input = true) :
    input.takeWhile whitespace ≠ [] := by
  cases input with
  | nil => simp [headWhitespace] at h
  | cons c cs =>
      have head : whitespace c = true := h
      simp [head]

theorem scanToken_sound {input rest : List Char} {token : Token}
    (h : scanToken input = some (token, rest)) : TokenRun input token rest := by
  unfold scanToken at h
  split at h
  next space =>
    cases h
    have result := TokenRun.space (input.takeWhile whitespace) (input.dropWhile whitespace)
      (headWhitespace_nonempty space) (List.all_eq_true.mp List.all_takeWhile) (boundary_drop whitespace input)
    simpa only [List.takeWhile_append_dropWhile] using result
  next noSpace =>
    split at h
    next numeric => exact .numeric (by simpa using noSpace) (scanNumeric_sound h)
    next noNumeric =>
      split at h
      next ident =>
        cases h
        have result := TokenRun.ident (startsIdent_takeWhile ident) (boundary_drop identChar input)
          (by simpa using noSpace) (by simpa using noNumeric)
        simpa using result
      next noIdent =>
        split at h
        next suffix => cases h; exact .plus _ (by simpa using noNumeric)
        next suffix => cases h; exact .minus _ (by simpa using noNumeric) (by simpa using noIdent)
        next => cases h

theorem TokenRun.result {input rest : List Char} {token : Token}
    (h : TokenRun input token rest) : scanToken input = some (token, rest) := by
  cases h with
  | space word rest nonempty all boundary =>
      have split := boundary_split whitespace word rest all boundary
      have head : headWhitespace (word ++ rest) = true := by
        cases word with
        | nil => exact False.elim (nonempty rfl)
        | cons c cs => exact all c (by simp)
      simp [scanToken, head, split.2]
  | numeric noSpace parsed => simp [scanToken, noSpace, parsed.starts, parsed.result]
  | @ident name rest valid boundary noSpace noNumeric =>
      have valid' : startsIdent name.toList = true ∧ ∀ c ∈ name.toList, identChar c = true := by
        simpa only [isIdent, Bool.and_eq_true, List.all_eq_true] using valid
      have split := boundary_split identChar _ _ valid'.2 boundary
      simp [scanToken, noSpace, noNumeric, startsIdent_append valid'.1, split.1, split.2]
  | plus rest noNumeric =>
      simp [scanToken, noNumeric, headWhitespace, whitespace, startsIdent, identStart, letter]
  | minus rest noNumeric noIdent => simp [scanToken, noNumeric, noIdent, headWhitespace, whitespace]

theorem scanToken_iff (input rest : List Char) (token : Token) :
    scanToken input = some (token, rest) ↔ TokenRun input token rest :=
  ⟨scanToken_sound, TokenRun.result⟩

theorem TokenRun.suffix_length_lt {input rest : List Char} {token : Token}
    (h : TokenRun input token rest) : rest.length < input.length := by
  cases h with
  | space word rest nonempty _ _ => have := List.length_pos_iff.mpr nonempty; simp; omega
  | numeric _ parsed => exact parsed.suffix_length_lt
  | @ident name rest valid _ _ _ =>
      have nonempty : name.toList ≠ [] := by
        intro empty
        simp [isIdent, empty, startsIdent] at valid
      have := List.length_pos_iff.mpr nonempty
      simp; omega
  | plus | minus => simp

def commentBody : List Char → Option (List Char)
  | '/' :: '*' :: body => some body
  | _ => none

theorem commentBody_some {input body : List Char} (h : commentBody input = some body) :
    input = '/' :: '*' :: body := by
  unfold commentBody at h
  split at h
  · cases h; rfl
  · cases h

inductive Step : List Char → Option Token → List Char → Prop where
  | token {input token rest} : commentBody input = none → TokenRun input token rest →
      Step input (some token) rest
  | comment {body rest} : CommentScan.Ends body rest → Step ('/' :: '*' :: body) none rest

def scanStep (input : List Char) : Option (Option Token × List Char) :=
  match commentBody input with
  | some body => (CommentScan.consumeBody body).map fun rest => (none, rest)
  | none => (scanToken input).map fun (token, rest) => (some token, rest)

theorem scanStep_sound {input rest : List Char} {token : Option Token}
    (h : scanStep input = some (token, rest)) : Step input token rest := by
  cases comment : commentBody input with
  | none =>
      simp only [scanStep, comment, Option.map_eq_some_iff] at h
      obtain ⟨⟨found, suffix⟩, parsed, equal⟩ := h
      cases equal
      exact .token comment (scanToken_sound parsed)
  | some body =>
      have shape := commentBody_some comment
      simp only [scanStep, comment, Option.map_eq_some_iff] at h
      obtain ⟨suffix, parsed, equal⟩ := h
      cases equal
      rw [shape]
      exact .comment (CommentScan.consumeBody_sound _ _ parsed)

theorem Step.result {input rest : List Char} {token : Option Token}
    (h : Step input token rest) : scanStep input = some (token, rest) := by
  cases h with
  | token noComment parsed => simp [scanStep, noComment, parsed.result]
  | comment ended => simp [scanStep, commentBody, CommentScan.consumeBody_complete ended]

theorem scanStep_iff (input rest : List Char) (token : Option Token) :
    scanStep input = some (token, rest) ↔ Step input token rest :=
  ⟨scanStep_sound, Step.result⟩

theorem Step.suffix_length_lt {input rest : List Char} {token : Option Token}
    (h : Step input token rest) : rest.length < input.length := by
  cases h with
  | token _ parsed => exact parsed.suffix_length_lt
  | comment ended => have := ended.suffix_length_lt; simp; omega

inductive Lexes : List Char → List Token → Prop where
  | empty : Lexes [] []
  | step {input emitted rest tokens} : Step input emitted rest → Lexes rest tokens →
      Lexes input (emitted.toList ++ tokens)

def lex (input : List Char) : Option (List Token) :=
  if input = [] then some []
  else match _h : scanStep input with
    | none => none
    | some (emitted, rest) => (lex rest).map fun tokens => emitted.toList ++ tokens
termination_by input.length
decreasing_by exact (scanStep_sound _h).suffix_length_lt

def tokenize (source : String) : Option (List Token) := lex source.toList

theorem lex_sound (input : List Char) (tokens : List Token)
    (h : lex input = some tokens) : Lexes input tokens := by
  induction input using lex.induct generalizing tokens with
  | case1 =>
      have same : tokens = [] := by simpa only [lex.eq_def, ↓reduceIte, Option.some.injEq] using h.symm
      subst tokens
      exact .empty
  | case2 input nonempty failed =>
      rw [lex.eq_def] at h
      simp only [nonempty, ↓reduceIte] at h
      rw [failed] at h
      cases h
  | case3 input nonempty emitted rest found ih =>
      rw [lex.eq_def] at h
      simp only [nonempty, ↓reduceIte] at h
      rw [found] at h
      simp only [Option.map_eq_some_iff] at h
      obtain ⟨tail, accepted, rfl⟩ := h
      exact .step (scanStep_sound found) (ih tail accepted)

theorem Lexes.result {input : List Char} {tokens : List Token}
    (h : Lexes input tokens) : lex input = some tokens := by
  induction h with
  | empty => rw [lex.eq_def]; rfl
  | @step input emitted rest tokens parsed _ ih =>
      have nonempty : input ≠ [] := by
        intro empty
        have := parsed.suffix_length_lt
        simp [empty] at this
      rw [lex.eq_def]
      simp only [nonempty, ↓reduceIte]
      rw [parsed.result]
      change (lex rest).map (fun tail => emitted.toList ++ tail) = some (emitted.toList ++ tokens)
      rw [ih]
      rfl

theorem lex_iff (input : List Char) (tokens : List Token) :
    lex input = some tokens ↔ Lexes input tokens := ⟨lex_sound input tokens, Lexes.result⟩

theorem tokenize_iff (source : String) (tokens : List Token) :
    tokenize source = some tokens ↔ Lexes source.toList tokens := lex_iff _ _

theorem Lexes.unique {input : List Char} {left right : List Token}
    (a : Lexes input left) (b : Lexes input right) : left = right :=
  Option.some.inj (a.result.symm.trans b.result)

theorem identStart_not_delimiter {c : Char} (h : identStart c = true) :
    c ≠ '+' ∧ c ≠ '-' ∧ c ≠ '/' ∧ c ≠ '.' := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> intro same <;> subst c <;> contradiction

theorem startsIdent_properties {input : List Char} (h : startsIdent input = true) :
    startsNumeric input = false ∧ headWhitespace input = false ∧
    Boundary digit input ∧ commentBody input = none ∧ startsFraction input = false := by
  cases input with
  | nil => simp [startsIdent] at h
  | cons c cs =>
      by_cases minus : c = '-'
      · subst c
        cases cs with
        | nil => simp [startsIdent, identStart, letter] at h
        | cons d ds =>
            have hd : digit d = false := by
              simp only [startsIdent, Bool.or_eq_true] at h
              rcases h with start | same
              · exact identStart_not_digit start
              · have : d = '-' := by simpa using same
                subst d; decide
            simp [startsNumeric, hd, headWhitespace, whitespace, Boundary,
              commentBody, startsFraction, show digit '-' = false from by decide]
      · have start : identStart c = true := by simpa [startsIdent, minus] using h
        obtain ⟨plus, _, slash, dot⟩ := identStart_not_delimiter start
        have hd := identStart_not_digit start
        have ws := identStart_not_whitespace start
        simp [startsNumeric, plus, minus, hd, headWhitespace, ws, Boundary, commentBody, slash,
          startsFraction, dot]

theorem IntegerRun.noWhitespace {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : headWhitespace input = false := by
  cases h with
  | unsigned digits =>
      obtain ⟨c, cs, rfl, head⟩ := digits.head_digit
      exact digit_not_whitespace head
  | plus | minus => rfl

theorem IntegerRun.noComment {input rest : List Char} {integer : IntegerToken}
    (h : IntegerRun input integer rest) : commentBody input = none := by
  cases h with
  | unsigned digits =>
      obtain ⟨c, cs, rfl, head⟩ := digits.head_digit
      have slash : c ≠ '/' := by intro same; subst c; contradiction
      simp [commentBody, slash]
  | plus | minus => rfl

def marker (rest : List Char) : List Char := '/' :: '*' :: '*' :: '/' :: rest

theorem marker_boundary (predicate : Char → Bool) (slash : predicate '/' = false) (rest : List Char) :
    Boundary predicate (marker rest) := by
  intro c cs same
  cases same
  exact slash

theorem startsExponent_marker (name rest : List Char) :
    startsExponent (name ++ marker rest) = startsExponent name := by
  cases name with
  | nil => rfl
  | cons e es =>
      cases es with
      | nil => simp [startsExponent, marker, digit, Char.isDigit]
      | cons c cs =>
          by_cases plus : c = '+'
          · subst c; cases cs <;> simp [startsExponent, marker, digit, Char.isDigit]
          · by_cases minus : c = '-'
            · subst c; cases cs <;> simp [startsExponent, marker, digit, Char.isDigit]
            · cases cs <;> simp [startsExponent, marker, plus, minus]

theorem startsExponent_append {name : List Char} (h : startsExponent name = true)
    (rest : List Char) : startsExponent (name ++ rest) = true := by
  cases name with
  | nil => contradiction
  | cons e es =>
      cases es with
      | nil => simp [startsExponent] at h
      | cons c cs =>
          by_cases plus : c = '+'
          · subst c
            cases cs with
            | nil => simp [startsExponent, digit, Char.isDigit] at h
            | cons d ds => simpa [startsExponent] using h
          · by_cases minus : c = '-'
            · subst c
              cases cs with
              | nil => simp [startsExponent, digit, Char.isDigit] at h
              | cons d ds => simpa [startsExponent] using h
            · simpa [startsExponent, plus, minus] using h

theorem NumericRun.valid {input rest : List Char} {token : Token}
    (h : NumericRun input token rest) : token.Valid := by
  cases h with
  | number => trivial
  | dimension _ name _ _ exponent =>
      refine ⟨name, ?_⟩
      cases guard : startsExponent _ with
      | false => rfl
      | true => have := startsExponent_append guard rest; simp_all

theorem TokenRun.valid {input rest : List Char} {token : Token}
    (h : TokenRun input token rest) : token.Valid := by
  cases h with
  | space | plus | minus => trivial
  | ident name => exact name
  | numeric _ numeric => exact numeric.valid

theorem Step.valid {input rest : List Char} {token : Option Token}
    (h : Step input token rest) : ∀ t ∈ token.toList, t.Valid := by
  cases h with
  | token _ parsed => simpa using parsed.valid
  | comment => simp

theorem Lexes.valid {input : List Char} {tokens : List Token}
    (h : Lexes input tokens) : ∀ t ∈ tokens, t.Valid := by
  induction h with
  | empty => simp
  | step parsed _ ih =>
      intro t member
      rcases List.mem_append.mp member with emitted | tail
      · exact parsed.valid t emitted
      · exact ih t tail

theorem tokenize_valid {source : String} {tokens : List Token}
    (h : tokenize source = some tokens) : ∀ t ∈ tokens, t.Valid :=
  ((tokenize_iff _ _).mp h).valid

def IntegerToken.chars (integer : IntegerToken) : List Char :=
  (match integer.sign with | none => [] | some .plus => ['+'] | some .minus => ['-']) ++
    Nat.toDigits 10 integer.magnitude

theorem IntegerRun.render (integer : IntegerToken) (rest : List Char) (boundary : Boundary digit rest) :
    IntegerRun (integer.chars ++ rest) integer rest := by
  have digits := DigitRun.run (Nat.toDigits 10 integer.magnitude) rest Nat.toDigits_ne_nil
    (fun _ member => Nat.isDigit_of_mem_toDigits (by decide) (by decide) member) boundary
  rw [magnitude_toDigits] at digits
  cases integer with
  | mk sign magnitude =>
      cases sign with
      | none => simpa [IntegerToken.chars] using IntegerRun.unsigned digits
      | some sign =>
          cases sign
          · simpa [IntegerToken.chars] using IntegerRun.plus digits
          · simpa [IntegerToken.chars] using IntegerRun.minus digits

def Token.chars : Token → List Char
  | .space => [' ']
  | .ident name => name.toList
  | .delimPlus => ['+']
  | .delimMinus => ['-']
  | .number integer => integer.chars
  | .dimension integer unit => integer.chars ++ unit.toList

def serializeChars : List Token → List Char
  | [] => []
  | token :: rest => token.chars ++ marker (serializeChars rest)

def serializeTokens (tokens : List Token) : String := String.ofList (serializeChars tokens)

theorem Step.render (token : Token) (valid : token.Valid) (rest : List Char) :
    Step (token.chars ++ marker rest) (some token) (marker rest) := by
  cases token with
  | space =>
      apply Step.token rfl
      exact TokenRun.space [' '] (marker rest) (by decide) (by simp [whitespace])
        (marker_boundary _ (by decide) _)
  | ident name =>
      have start : startsIdent name.toList = true := (Bool.and_eq_true_iff.mp valid).1
      obtain ⟨numeric, ws, _, comment, _⟩ :=
        startsIdent_properties (startsIdent_append (rest := marker rest) start)
      exact Step.token comment (TokenRun.ident valid (marker_boundary _ (by decide) _) ws numeric)
  | delimPlus =>
      exact Step.token rfl (TokenRun.plus _ rfl)
  | delimMinus =>
      exact Step.token rfl (TokenRun.minus _ rfl rfl)
  | number integer =>
      have digits := IntegerRun.render integer (marker rest) (marker_boundary _ (by decide) _)
      exact Step.token digits.noComment (TokenRun.numeric digits.noWhitespace
        (NumericRun.number digits rfl rfl rfl))
  | dimension integer unit =>
      obtain ⟨name, exponent⟩ := valid
      have start : startsIdent unit.toList = true := (Bool.and_eq_true_iff.mp name).1
      obtain ⟨_, _, boundary, _, fraction⟩ :=
        startsIdent_properties (startsIdent_append (rest := marker rest) start)
      have digits := IntegerRun.render integer (unit.toList ++ marker rest) boundary
      have numeric := NumericRun.dimension digits name (marker_boundary _ (by decide) _)
        fraction ((startsExponent_marker _ _).trans exponent)
      simpa [Token.chars, List.append_assoc] using
        Step.token digits.noComment (TokenRun.numeric digits.noWhitespace numeric)

theorem Lexes.serialize (tokens : List Token) (valid : ∀ token ∈ tokens, token.Valid) :
    Lexes (serializeChars tokens) tokens := by
  induction tokens with
  | nil => exact .empty
  | cons token tokens ih =>
      have tail := ih (fun t member => valid t (List.mem_cons_of_mem _ member))
      have comment : Lexes (marker (serializeChars tokens)) tokens :=
        Lexes.step (Step.comment CommentScan.Ends.close) tail
      exact Lexes.step (Step.render token (valid token (by simp)) _) comment

theorem serialize_roundtrip (tokens : List Token) (valid : ∀ token ∈ tokens, token.Valid) :
    tokenize (serializeTokens tokens) = some tokens := by
  apply (tokenize_iff _ _).mpr
  simpa [serializeTokens, String.toList_ofList] using Lexes.serialize tokens valid

end CssSemantics.AnBTokens
