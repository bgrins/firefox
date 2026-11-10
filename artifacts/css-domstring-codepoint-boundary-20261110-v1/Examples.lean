import ScalarChoice

namespace CssSemantics.DomStringExamples

open DomString

def decodeCases : List (String × List Nat × Option (List Nat)) := [
  ("empty", [], some []),
  ("BMP", [0x41, 0xd7ff, 0xe000, 0xffff], some [0x41, 0xd7ff, 0xe000, 0xffff]),
  ("minimum pair", [0xd800, 0xdc00], some [0x10000]),
  ("maximum pair", [0xdbff, 0xdfff], some [0x10ffff]),
  ("supplementary", [0xd83d, 0xde00], some [0x1f600]),
  ("pair arithmetic", [0xd801, 0xdc00], some [0x10400]),
  ("isolated leading", [0xd800], some [0xd800]),
  ("isolated trailing", [0xdfff], some [0xdfff]),
  ("reversed", [0xdc00, 0xd800], some [0xdc00, 0xd800]),
  ("leading leading trailing", [0xd800, 0xdbff, 0xdfff], some [0xd800, 0x10ffff]),
  ("pair trailing", [0xd800, 0xdc00, 0xdfff], some [0x10000, 0xdfff]),
  ("leading ASCII trailing", [0xd800, 0x41, 0xdc00], some [0xd800, 0x41, 0xdc00]),
  ("pair followed by ASCII", [0xd800, 0xdc00, 0x41, 0x42], some [0x10000, 0x41, 0x42]),
  ("two pairs", [0xd800, 0xdc00, 0xdbff, 0xdfff], some [0x10000, 0x10ffff]),
  ("CRLF untouched at boundary", [13, 10], some [13, 10]),
  ("out of unit domain", [0x10000], none),
  ("supplementary point is not a unit", [0x1f600], none),
  ("invalid suffix", [0x41, 0x110000], none)]

def decodeChecks := decodeCases.map fun (name, source, expected) =>
  ("decode " ++ name, decide (decodeValues source = expected))

def stepCases : List (String × List Nat × Option (Option (Nat × List Nat))) := [
  ("EOF", [], some none),
  ("singleton", [0xd800], some (some (0xd800, []))),
  ("pair exact suffix", [0xd800, 0xdc00, 13, 10, 0x41], some (some (0x10000, [13, 10, 0x41]))),
  ("unpaired exact suffix", [0xd800, 0x41, 0xdc00], some (some (0xd800, [0x41, 0xdc00]))),
  ("trailing exact suffix", [0xdc00, 0xd800, 0xdc00], some (some (0xdc00, [0xd800, 0xdc00]))),
  ("invalid is not EOF", [0x10000], none)]

def stepChecks := stepCases.map fun (name, source, expected) =>
  ("step " ++ name, decide (nextValues source = expected))

def filterCases : List (String × List Nat × Option (List Char)) := [
  ("pair survives", [0xd83d, 0xde00], some [Char.ofNat 0x1f600]),
  ("unpaired replaced", [0xd800, 0x41, 0xdfff], some ['�', 'A', '�']),
  ("CRLF", [13, 10], some ['\n']),
  ("CRCRLF", [13, 13, 10], some ['\n', '\n']),
  ("pair CRLF pair", [0xd800, 0xdc00, 13, 10, 0xdbff, 0xdfff],
    some [Char.ofNat 0x10000, '\n', Char.ofNat 0x10ffff]),
  ("surrogate separates CRLF", [13, 0xd800, 10], some ['\n', '�', '\n']),
  ("NUL FF", [0, 12], some ['�', '\n']),
  ("reversed surrogates", [0xdc00, 0xd800], some ['�', '�']),
  ("truncated pair", [0x41, 0xd83d], some ['A', '�']),
  ("invalid unit", [0x10000], none)]

def filterChecks := filterCases.map fun (name, source, expected) =>
  ("filter " ++ name, decide (prepareValues source = expected))

def checks := decodeChecks ++ stepChecks ++ filterChecks

theorem checks_pass : checks.all Prod.snd = true := by decide +kernel

example : decodeValues [0xd800] ≠ some [0xfffd] := by decide
example : prepareValues [0xd800] = prepareValues [0xfffd] := by decide
example : decodeValues [0xd800, 0xdc00] ≠ some [0xd800, 0xdc00] := by decide

end CssSemantics.DomStringExamples
