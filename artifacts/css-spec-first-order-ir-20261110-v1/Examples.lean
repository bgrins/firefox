import FOBridge

namespace CssDerivation.FirstOrder

example : execute escapeTree [] = ⟨'�', [], true⟩ := by decide
example : execute escapeTree "z!".toList = ⟨'z', ['!'], false⟩ := by decide
example : execute escapeTree "41!".toList = ⟨'A', ['!'], false⟩ := by decide
example : execute escapeTree "0000417".toList = ⟨'A', ['7'], false⟩ := by decide
example : execute escapeTree "41  Z".toList = ⟨'A', [' ', 'Z'], false⟩ := by decide
example : execute escapeTree "0!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escapeTree "d800!".toList = ⟨'�', ['!'], false⟩ := by decide
example : execute escapeTree "10ffff!".toList = ⟨Char.ofNat 0x10ffff, ['!'], false⟩ := by decide
example : execute escapeTree "110000!".toList = ⟨'�', ['!'], false⟩ := by decide

end CssDerivation.FirstOrder
