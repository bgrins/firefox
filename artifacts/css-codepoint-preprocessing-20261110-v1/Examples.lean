import Refinement

namespace CssSemantics.CodePointInput

example : filterValues [] = some [] := by decide
example : filterValues [0x0d, 0x0a] = some ['\n'] := by decide
example : filterValues [0x0d] = some ['\n'] := by decide
example : filterValues [0x0c] = some ['\n'] := by decide
example : filterValues [0] = some ['�'] := by decide
example : filterValues [0xd800, 0xdbff, 0xdc00, 0xdfff] = some ['�', '�', '�', '�'] := by decide
example : filterValues [0xd7ff, 0xe000] = some [Char.ofNat 0xd7ff, Char.ofNat 0xe000] := by decide
example : filterValues [0xfdd0, 0xfffe, 0xffff, 0x10ffff] =
    some [Char.ofNat 0xfdd0, Char.ofNat 0xfffe, Char.ofNat 0xffff, Char.ofNat 0x10ffff] := by decide
example : filterValues [0x1f600] = some [Char.ofNat 0x1f600] := by decide
example : filterValues [0xd83d, 0xde00] = some ['�', '�'] := by decide
example : filterValues [0x0d, 0x0d, 0x0a] = some ['\n', '\n'] := by decide
example : filterValues [0x0d, 0x0a, 0x0a] = some ['\n', '\n'] := by decide
example : filterValues [0x0c, 0x0a] = some ['\n', '\n'] := by decide
example : filterValues [0x0a, 0x0d] = some ['\n', '\n'] := by decide
example : filterValues [0x0d, 0xd800, 0x0a] = some ['\n', '�', '\n'] := by decide
example : filterValues [0xdfff, 0x0d, 0x0a, 0] = some ['�', '\n', '�'] := by decide
example : filterValues [0xdbff, 0x41] = some ['�', 'A'] := by decide
example : filterValues [0x110000] = none := by decide
example : filterValues [0x41, 0x200000] = none := by decide
example : filterValues [0xfeff] = some [Char.ofNat 0xfeff] := by decide
example : filterValues [0x2028, 0x2029] = some [Char.ofNat 0x2028, Char.ofNat 0x2029] := by decide

end CssSemantics.CodePointInput
