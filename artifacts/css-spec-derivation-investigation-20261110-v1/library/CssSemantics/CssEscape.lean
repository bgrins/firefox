import Init
import Init.Data.Nat.ToString

namespace CssSemantics.CssEscape

def hex (c : Char) : Bool :=
  ('0' ≤ c && c ≤ '9') || ('A' ≤ c && c ≤ 'F') || ('a' ≤ c && c ≤ 'f')

def digitValue (c : Char) : Nat :=
  if c ≤ '9' then c.toNat - 48 else if c ≤ 'F' then c.toNat - 55 else c.toNat - 87

def magnitude (digits : List Char) : Nat := digits.foldl (fun value c => value * 16 + digitValue c) 0

def whitespace (c : Char) : Bool := c == ' ' || c == '\t' || c == '\n'

def decode (value : Nat) : Char :=
  if value = 0 ∨ (0xd800 ≤ value ∧ value ≤ 0xdfff) ∨ 0x10ffff < value then '�' else Char.ofNat value

def scanHex : Nat → List Char → List Char × List Char
  | 0, source => ([], source)
  | _ + 1, [] => ([], [])
  | budget + 1, c :: rest =>
      if hex c then
        let scanned := scanHex budget rest
        (c :: scanned.1, scanned.2)
      else ([], c :: rest)

inductive HexRun : Nat → List Char → List Char → List Char → Prop where
  | limit (source) : HexRun 0 source [] source
  | endOfInput (budget) : HexRun (budget + 1) [] [] []
  | boundary (budget c rest) : hex c = false → HexRun (budget + 1) (c :: rest) [] (c :: rest)
  | digit {budget c source digits rest} : hex c = true → HexRun budget source digits rest →
      HexRun (budget + 1) (c :: source) (c :: digits) rest

theorem HexRun.result {budget source digits rest} (parsed : HexRun budget source digits rest) :
    scanHex budget source = (digits, rest) := by
  induction parsed with
  | limit | endOfInput => rfl
  | boundary budget c rest nonhex => simp [scanHex, nonhex]
  | digit digit tail ih => simp [scanHex, digit, ih]

theorem scanHex_sound (budget : Nat) (source : List Char) :
    HexRun budget source (scanHex budget source).1 (scanHex budget source).2 := by
  induction budget generalizing source with
  | zero => exact .limit source
  | succ budget ih =>
      cases source with
      | nil => exact .endOfInput budget
      | cons c rest =>
          cases hc : hex c with
          | false => simpa [scanHex, hc] using HexRun.boundary budget c rest hc
          | true => simpa [scanHex, hc] using HexRun.digit hc (ih rest)

theorem scanHex_iff (budget : Nat) (source digits rest : List Char) :
    scanHex budget source = (digits, rest) ↔ HexRun budget source digits rest := by
  constructor
  · intro equal; simpa [equal] using scanHex_sound budget source
  · exact HexRun.result

theorem HexRun.decomposition {budget source digits rest} (parsed : HexRun budget source digits rest) :
    source = digits ++ rest := by
  induction parsed with
  | limit | endOfInput | boundary => rfl
  | digit digit tail ih => simp [ih]

theorem HexRun.digits_hex {budget source digits rest} (parsed : HexRun budget source digits rest) :
    ∀ c ∈ digits, hex c = true := by
  induction parsed with
  | limit | endOfInput | boundary => simp
  | digit digit tail ih => simpa using And.intro digit ih

theorem HexRun.length_le {budget source digits rest} (parsed : HexRun budget source digits rest) :
    digits.length ≤ budget := by
  induction parsed with
  | limit | endOfInput | boundary => simp
  | digit digit tail ih => simpa using Nat.succ_le_succ ih

def Boundary : List Char → Prop
  | [] => True
  | c :: _ => hex c = false

theorem HexRun.maximal {budget source digits rest} (parsed : HexRun budget source digits rest) :
    digits.length = budget ∨ Boundary rest := by
  induction parsed with
  | limit => exact Or.inl rfl
  | endOfInput => exact Or.inr True.intro
  | boundary budget c rest nonhex => exact Or.inr nonhex
  | digit digit tail ih =>
      rcases ih with filled | boundary
      · exact Or.inl (congrArg Nat.succ filled)
      · exact Or.inr boundary

theorem HexRun.characterization {budget source digits rest} : HexRun budget source digits rest ↔
    source = digits ++ rest ∧ (∀ c ∈ digits, hex c = true) ∧ digits.length ≤ budget ∧
      (digits.length = budget ∨ Boundary rest) := by
  constructor
  · intro parsed; exact ⟨parsed.decomposition, parsed.digits_hex, parsed.length_le, parsed.maximal⟩
  · rintro ⟨rfl, all, bounded, maximal⟩
    induction digits generalizing budget with
    | nil =>
        cases budget with
        | zero => exact .limit rest
        | succ budget =>
            have boundary : Boundary rest := maximal.resolve_left (by simp)
            cases rest with
            | nil => exact .endOfInput budget
            | cons c tail => exact .boundary budget c tail boundary
    | cons c digits ih =>
        cases budget with
        | zero => simp at bounded
        | succ budget =>
            apply HexRun.digit (all c (by simp))
            apply ih (fun d member => all d (by simp [member])) (by simpa using bounded)
            rcases maximal with full | boundary
            · exact Or.inl (by simpa using full)
            · exact Or.inr boundary

def skipWhitespace : List Char → List Char
  | c :: rest => if whitespace c then rest else c :: rest
  | [] => []

inductive Terminator : List Char → List Char → Prop where
  | endOfInput : Terminator [] []
  | consumed (c rest) : whitespace c = true → Terminator (c :: rest) rest
  | untouched (c rest) : whitespace c = false → Terminator (c :: rest) (c :: rest)

theorem skipWhitespace_iff (source rest : List Char) :
    skipWhitespace source = rest ↔ Terminator source rest := by
  constructor
  · intro equal
    cases source with
    | nil => subst rest; exact .endOfInput
    | cons c tail =>
        cases hc : whitespace c with
        | true => simp [skipWhitespace, hc] at equal; subst rest; exact .consumed c tail hc
        | false => simp [skipWhitespace, hc] at equal; subst rest; exact .untouched c tail hc
  · intro parsed
    cases parsed <;> simp_all [skipWhitespace]

structure Result where
  value : Char
  rest : List Char
  eofError : Bool
  deriving DecidableEq, Repr

def consume : List Char → Result
  | [] => ⟨'�', [], true⟩
  | c :: rest =>
      if hex c then
        let scanned := scanHex 5 rest
        ⟨decode (magnitude (c :: scanned.1)), skipWhitespace scanned.2, false⟩
      else ⟨c, rest, false⟩

inductive Escaped : List Char → Result → Prop where
  | eof : Escaped [] ⟨'�', [], true⟩
  | literal (c rest) : hex c = false → Escaped (c :: rest) ⟨c, rest, false⟩
  | hexadecimal {c source digits suffix rest} : hex c = true → HexRun 5 source digits suffix →
      Terminator suffix rest → Escaped (c :: source) ⟨decode (magnitude (c :: digits)), rest, false⟩

theorem Escaped.result {source result} (parsed : Escaped source result) : consume source = result := by
  cases parsed with
  | eof => rfl
  | literal c rest nonhex => simp [consume, nonhex]
  | hexadecimal first digits terminator =>
      simp [consume, first, digits.result, (skipWhitespace_iff _ _).mpr terminator]

theorem consume_sound (source : List Char) : Escaped source (consume source) := by
  cases source with
  | nil => exact .eof
  | cons c rest =>
      cases hc : hex c with
      | false => simpa [consume, hc] using Escaped.literal c rest hc
      | true =>
          simpa [consume, hc] using Escaped.hexadecimal hc (scanHex_sound 5 rest)
            ((skipWhitespace_iff _ _).mp rfl)

theorem consume_iff (source : List Char) (result : Result) : consume source = result ↔ Escaped source result :=
  ⟨fun equal => equal ▸ consume_sound source, Escaped.result⟩

theorem Escaped.unique {source left right} (hl : Escaped source left) (hr : Escaped source right) :
    left = right := hl.result.symm.trans hr.result

theorem Terminator.length_le {source rest} (parsed : Terminator source rest) : rest.length ≤ source.length := by
  cases parsed <;> simp

theorem Escaped.progress {source result} (parsed : Escaped source result) (nonempty : source ≠ []) :
    result.rest.length < source.length := by
  cases parsed with
  | eof => contradiction
  | literal => simp
  | hexadecimal first digits terminator =>
      have decomposition := digits.decomposition
      have length := terminator.length_le
      simp only [decomposition, List.length_cons, List.length_append]
      omega

theorem consume_eofError (source : List Char) : (consume source).eofError = true ↔ source = [] := by
  cases source with
  | nil => simp [consume]
  | cons c rest => simp [consume]; split <;> simp

def validAfter : List Char → Bool
  | '\n' :: _ => false
  | _ => true

def ValidAfter (source : List Char) : Prop := ∀ rest, source ≠ '\n' :: rest

theorem validAfter_iff (source : List Char) : validAfter source = true ↔ ValidAfter source := by
  cases source with
  | nil => simp [validAfter, ValidAfter]
  | cons c rest =>
      by_cases newline : c = '\n'
      · subst c; simp [validAfter, ValidAfter]
      · simp [validAfter, ValidAfter, newline]

def consumeValid (source : List Char) : Option Result :=
  if validAfter source then some (consume source) else none

def ValidEscaped (source : List Char) (result : Result) : Prop := ValidAfter source ∧ Escaped source result

theorem consumeValid_iff (source : List Char) (result : Result) :
    consumeValid source = some result ↔ ValidEscaped source result := by
  unfold consumeValid
  split
  next valid => simp [ValidEscaped, (validAfter_iff _).mp valid, ← consume_iff]
  next invalid => simp [ValidEscaped, ← validAfter_iff, invalid]

theorem digitChar_hex : ∀ digit : Fin 16, hex (Nat.digitChar digit.val) = true := by decide +kernel

theorem digitChar_value : ∀ digit : Fin 16, digitValue (Nat.digitChar digit.val) = digit.val := by decide +kernel

def renderHex : Nat → Nat → List Char
  | 0, _ => []
  | digits + 1, value => renderHex digits (value / 16) ++ [Nat.digitChar (value % 16)]

theorem renderHex_length (digits value : Nat) : (renderHex digits value).length = digits := by
  induction digits generalizing value with
  | zero => rfl
  | succ digits ih => simp [renderHex, ih]

theorem renderHex_hex (digits value : Nat) : ∀ c ∈ renderHex digits value, hex c = true := by
  induction digits generalizing value with
  | zero => simp [renderHex]
  | succ digits ih =>
      intro c member
      simp only [renderHex, List.mem_append, List.mem_singleton] at member
      rcases member with member | rfl
      · exact ih _ c member
      · exact digitChar_hex ⟨value % 16, Nat.mod_lt _ (by decide)⟩

theorem magnitude_append_digit (digits : List Char) (c : Char) :
    magnitude (digits ++ [c]) = magnitude digits * 16 + digitValue c := by
  simp [magnitude, List.foldl_append]

theorem renderHex_magnitude (digits value : Nat) (bounded : value < 16 ^ digits) :
    magnitude (renderHex digits value) = value := by
  induction digits generalizing value with
  | zero =>
      have zero : value = 0 := by simpa using bounded
      subst value
      rfl
  | succ digits ih =>
      have quotient : value / 16 < 16 ^ digits := by
        rw [Nat.div_lt_iff_lt_mul (by decide)]
        simpa [Nat.pow_succ] using bounded
      rw [renderHex, magnitude_append_digit, ih _ quotient,
        digitChar_value ⟨value % 16, Nat.mod_lt _ (by decide)⟩]
      change value / 16 * 16 + value % 16 = value
      omega

def render (value : Char) : List Char := renderHex 6 value.toNat ++ [' ']

theorem decode_char (value : Char) (nonzero : value ≠ '\x00') : decode value.toNat = value := by
  have valid := value.valid
  change value.toNat < 0xd800 ∨ (0xdfff < value.toNat ∧ value.toNat < 0x110000) at valid
  have nz : value.toNat ≠ 0 := by
    intro equal
    apply nonzero
    apply Char.toNat_inj.mp
    exact equal
  simp only [decode]
  rw [ite_eq_right (by omega), Char.ofNat_toNat]

theorem render_consumed (value : Char) (nonzero : value ≠ '\x00') (rest : List Char) :
    consume (render value ++ rest) = ⟨value, rest, false⟩ := by
  have bounded : value.toNat < 16 ^ 6 := by
    have valid := value.valid
    change value.toNat < 0xd800 ∨ (0xdfff < value.toNat ∧ value.toNat < 0x110000) at valid
    omega
  have digits := renderHex_hex 6 value.toNat
  have length := renderHex_length 6 value.toNat
  have numerical := renderHex_magnitude 6 value.toNat bounded
  cases exactDigits : renderHex 6 value.toNat with
  | nil => simp [exactDigits] at length
  | cons c tail =>
      rw [exactDigits] at digits length numerical
      apply Escaped.result
      have hexRun : HexRun 5 (tail ++ ' ' :: rest) tail (' ' :: rest) :=
        HexRun.characterization.mpr ⟨rfl, fun x member => digits x (by simp [member]), by simpa using Nat.le_of_eq length,
          Or.inl (by simpa using length)⟩
      have parsed := Escaped.hexadecimal (digits c (by simp)) hexRun (Terminator.consumed ' ' rest rfl)
      simpa [render, exactDigits, numerical, decode_char value nonzero] using parsed

theorem render_validAfter (value : Char) (rest : List Char) : ValidAfter (render value ++ rest) := by
  intro suffix equal
  have digits := renderHex_hex 6 value.toNat
  have length := renderHex_length 6 value.toNat
  cases exactDigits : renderHex 6 value.toNat with
  | nil => simp [exactDigits] at length
  | cons c tail =>
      have first := digits c (by simp [exactDigits])
      simp only [render, exactDigits, List.cons_append, List.cons.injEq] at equal
      rw [equal.1] at first
      contradiction

theorem render_validConsumed (value : Char) (nonzero : value ≠ '\x00') (rest : List Char) :
    consumeValid (render value ++ rest) = some ⟨value, rest, false⟩ := by
  apply (consumeValid_iff _ _).mpr
  exact ⟨render_validAfter value rest, (consume_iff _ _).mp (render_consumed value nonzero rest)⟩

end CssSemantics.CssEscape
