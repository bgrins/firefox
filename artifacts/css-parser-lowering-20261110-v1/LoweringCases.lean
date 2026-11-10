import LoweredProgram

namespace CssParserLowering.Cases

open CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer

def character (c : Char) : Parser (.base .scalar) :=
  .take (.eqChar (.var .here) (.scalar c))

def errorThenEmpty : Parser (.base .chars) :=
  .nonempty (.legacy (.raiseError (.ret .nil)))

def pairAB : Parser (.pair (.base .scalar) (.base .scalar)) :=
  .pair (character 'a') (character 'b')

def nestedOptional : Parser (.pair (.base .scalar) (.optional (.pair (.base .scalar) (.base .scalar)))) :=
  .pair (character 'a') (.optional (.pair (character 'b') (character 'c')))

def checks : List (String × Bool) := [
  ("take success", decide (run (lower (character 'a')) ⟨"ab".toList, false⟩ = (some 'a', ⟨['b'], false⟩))),
  ("take mismatch restores cursor", decide (run (lower (character 'a')) ⟨"xb".toList, false⟩ = (none, ⟨"xb".toList, false⟩))),
  ("take EOF preserves error", decide (run (lower (character 'a')) ⟨[], true⟩ = (none, ⟨[], true⟩))),
  ("maximal scan exceeds small caps", decide (run (lower digitsTree) ⟨"12345px".toList, false⟩ = (some "12345".toList, ⟨"px".toList, false⟩))),
  ("empty maximal scan succeeds", decide (run (lower digitsTree) ⟨"px".toList, true⟩ = (some [], ⟨"px".toList, true⟩))),
  ("failed nonempty restores raised error", decide (run (lower errorThenEmpty) ⟨['x'], false⟩ = (none, ⟨['x'], false⟩))),
  ("failed nonempty preserves prior error", decide (run (lower errorThenEmpty) ⟨['x'], true⟩ = (none, ⟨['x'], true⟩))),
  ("pair order and suffix", decide (run (lower pairAB) ⟨"ab!".toList, false⟩ = (some ('a', 'b'), ⟨['!'], false⟩))),
  ("pair failure rewinds left consumption", decide (run (lower pairAB) ⟨"ax".toList, true⟩ = (none, ⟨"ax".toList, true⟩))),
  ("right returns right value", decide (run (lower (.right (character 'a') (character 'b'))) ⟨"ab!".toList, false⟩ = (some 'b', ⟨['!'], false⟩))),
  ("right failure rewinds left consumption", decide (run (lower (.right (character 'a') (character 'b'))) ⟨"ax".toList, false⟩ = (none, ⟨"ax".toList, false⟩))),
  ("optional failure becomes absent success", decide (run (lower (.optional (character 'a'))) ⟨['x'], false⟩ = (some none, ⟨['x'], false⟩))),
  ("optional success retains value", decide (run (lower (.optional (character 'a'))) ⟨"ab".toList, false⟩ = (some (some 'a'), ⟨['b'], false⟩))),
  ("optional restores full state", decide (run (lower (.optional errorThenEmpty)) ⟨['x'], false⟩ = (some none, ⟨['x'], false⟩))),
  ("nested rollback keeps earlier prefix consumed", decide (run (lower nestedOptional) ⟨"abx".toList, true⟩ = (some ('a', none), ⟨"bx".toList, true⟩))),
  ("truncated exponent rolls back", decide (run (lower (.optional exponentTree)) ⟨"e+".toList, true⟩ = (some none, ⟨"e+".toList, true⟩))),
  ("legacy preserves existing error", decide (run (lower (.legacy (.ret (.scalar '!')))) ⟨['x'], true⟩ = (some '!', ⟨['x'], true⟩))),
  ("legacy raises error", decide (run (lower (.legacy (.raiseError (.ret (.nat 5))))) ⟨['x'], false⟩ = (some 5, ⟨['x'], true⟩))),
  ("legacy escape instance", decide (run (lower (.legacy FirstOrder.escapeTree)) ⟨"41 ".toList, false⟩ = (some 'A', ⟨[], false⟩))),
  ("legacy escape EOF error", decide (run (lower (.legacy FirstOrder.escapeTree)) ⟨[], false⟩ = (some '�', ⟨[], true⟩))),
  ("integer with suffix", decide (executeNumber ⟨"123px".toList, false⟩ = some (⟨123, 0, false, none⟩, ⟨"px".toList, false⟩))),
  ("fraction and exponent", decide (executeNumber ⟨".5e+2%".toList, false⟩ = some (⟨5, 1, true, none⟩, ⟨['%'], false⟩))),
  ("negative zero keeps explicit sign", decide (executeNumber ⟨"-0".toList, false⟩ = some (⟨0, 0, false, some '-'⟩, ⟨[], false⟩))),
  ("number truncated exponent and old error", decide (executeNumber ⟨"1e+".toList, true⟩ = some (⟨1, 0, false, none⟩, ⟨"e+".toList, true⟩))),
  ("number trailing dot remains", decide (executeNumber ⟨"1.".toList, false⟩ = some (⟨1, 0, false, none⟩, ⟨['.'], false⟩))),
  ("signed decimal with negative exponent", decide (executeNumber ⟨"-12.30e-2!".toList, false⟩ = some (⟨-1230, -4, true, some '-'⟩, ⟨['!'], false⟩))),
  ("sign-only total model (off-domain)", decide (executeNumber ⟨['+'], false⟩ = some (⟨0, 0, false, some '+'⟩, ⟨[], false⟩))),
  ("empty total model (off-domain)", decide (executeNumber ⟨[], true⟩ = some (⟨0, 0, false, none⟩, ⟨[], true⟩)))
]

end CssParserLowering.Cases
