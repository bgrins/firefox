import Bridge

namespace CssDerivation

example : execute escape [] = ⟨'�', [], true⟩ := by decide
example : execute escape "z!".toList = ⟨'z', ['!'], false⟩ := by decide
example : execute escape "41Z".toList = ⟨'A', ['Z'], false⟩ := by decide
example : execute escape "41".toList = ⟨'A', [], false⟩ := by decide
example : execute escape "41  Z".toList = ⟨'A', [' ', 'Z'], false⟩ := by decide
example : execute escape "0000417".toList = ⟨'A', ['7'], false⟩ := by decide
example : execute escape "aB!".toList = ⟨'«', ['!'], false⟩ := by decide
example : execute escape "0!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escape "d7ff!".toList = ⟨Char.ofNat 0xd7ff, ['!'], false⟩ := by decide
example : execute escape "d800!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escape "dfff!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escape "e000!".toList = ⟨Char.ofNat 0xe000, ['!'], false⟩ := by decide
example : execute escape "10ffff!".toList = ⟨Char.ofNat 0x10ffff, ['!'], false⟩ := by decide
example : execute escape "110000!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escape ['4', '1', '\n', '\t'] = ⟨'A', ['\t'], false⟩ := by decide
example : execute escape ['4', '1', '\r', '!'] = ⟨'A', ['\r', '!'], false⟩ := by decide
example : execute escape (CssSemantics.CssInput.preprocess ['4', '1', '\r', '!']) =
    ⟨'A', ['!'], false⟩ := by decide
example : ¬ CallerReady ['\n'] := by
  simp [CallerReady, CssSemantics.CssEscape.ValidAfter]

end CssDerivation
