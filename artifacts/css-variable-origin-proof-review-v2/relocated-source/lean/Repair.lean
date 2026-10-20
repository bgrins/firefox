import Origin

namespace VariableOrigin

@[simp] theorem backslash_bytes : '\\'.utf8Size = 1 := by decide

inductive TerminalRepair where
  | append (body closers : List Char)
  | dropBackslash (front closers : List Char)
  deriving Repr

def rawRepairInput : TerminalRepair → List Char
  | .append body _ => body
  | .dropBackslash front _ => front ++ ['\\']

def repairedText : TerminalRepair → List Char
  | .append body closers => body ++ closers
  | .dropBackslash front closers => front ++ closers

def addedClosers : TerminalRepair → List Char
  | .append _ closers | .dropBackslash _ closers => closers

def deletedBytes : TerminalRepair → Nat
  | .append _ _ => 0
  | .dropBackslash _ _ => 1

def withPrefix (prefixText : List Char) : TerminalRepair → TerminalRepair
  | .append body closers => .append (prefixText ++ body) closers
  | .dropBackslash front closers => .dropBackslash (prefixText ++ front) closers

theorem terminal_raw_prefix (front : List Char) (r : TerminalRepair) :
    rawRepairInput (withPrefix front r) = front ++ rawRepairInput r := by
  cases r <;> simp [rawRepairInput, withPrefix, List.append_assoc]

theorem terminal_repair_prefix (front : List Char) (r : TerminalRepair) :
    repairedText (withPrefix front r) = front ++ repairedText r := by
  cases r <;> simp [repairedText, withPrefix, List.append_assoc]

theorem repair_byte_length (r : TerminalRepair) :
    byteLength (repairedText r) =
      byteLength (rawRepairInput r) + byteLength (addedClosers r) - deletedBytes r := by
  cases r <;> simp [repairedText, rawRepairInput, addedClosers, deletedBytes, byteLength]

theorem repair_normalized_endpoint (base : Nat) (padding : List Char) (r : TerminalRepair) :
    base + byteLength padding + byteLength (rawRepairInput r) +
      byteLength (addedClosers r) - deletedBytes r - (base + byteLength padding) =
      byteLength (repairedText r) := by
  rw [repair_byte_length]
  cases r <;> simp [rawRepairInput, addedClosers, deletedBytes, byteLength] <;> omega

theorem no_padding_overlap (padding front : List Char) :
    byteLength padding ≤ byteLength (padding ++ front ++ ['\\']) - 1 := by
  simp [byteLength]

end VariableOrigin
