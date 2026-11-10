import CssSemantics.CssStreamingPipeline
import CssSemantics.CssStreamingAdapters

namespace CssSemantics.StreamingExamples

open Streaming

def prepareValues (input : List (List Nat)) : Option (List Nat) :=
  (admittedChunks input).map fun chunks => (pipeline utf16 css chunks).map Char.toNat

def checks : List (String × Bool) := [
  ("streaming no chunks", decide (decodeValues [] = some [])),
  ("streaming empty chunks", decide (prepareValues [[], [], []] = some [])),
  ("streaming split surrogate pair", decide (decodeValues [[0xd83d], [0xdca9]] = some [0x1f4a9])),
  ("streaming pair across empty chunks", decide (decodeValues [[0xd83d], [], [], [0xdca9]] = some [0x1f4a9])),
  ("streaming minimum pair", decide (decodeValues [[0xd800], [0xdc00]] = some [0x10000])),
  ("streaming maximum pair", decide (decodeValues [[0xdbff], [0xdfff]] = some [0x10ffff])),
  ("streaming isolated leading surrogate retained before CSS", decide (decodeValues [[0xd800]] = some [0xd800])),
  ("streaming isolated leading surrogate replaced at CSS EOF", decide (prepareValues [[0xd800]] = some [0xfffd])),
  ("streaming trailing surrogate is not carried", decide (decodeValues [[0xdc00]] = some [0xdc00])),
  ("streaming reversed surrogates remain separate", decide (decodeValues [[0xdc00], [0xd800]] = some [0xdc00, 0xd800])),
  ("streaming overlapping leading candidates", decide (decodeValues [[0xd800], [0xd801], [0xdc00]] = some [0xd800, 0x10400])),
  ("streaming ordinary unit interrupts pairing", decide (decodeValues [[0xd83d], [0x61], [0xdca9]] = some [0xd83d, 0x61, 0xdca9])),
  ("streaming split CRLF", decide (prepareValues [[13], [10]] = some [10])),
  ("streaming CRLF across empty chunks", decide (prepareValues [[13], [], [10]] = some [10])),
  ("streaming CR before ordinary unit", decide (prepareValues [[13], [0x61]] = some [10, 0x61])),
  ("streaming trailing CR flushed", decide (prepareValues [[13]] = some [10])),
  ("streaming CR CR LF", decide (prepareValues [[13], [13], [10]] = some [10, 10])),
  ("streaming NUL and FF", decide (prepareValues [[0], [12]] = some [0xfffd, 10])),
  ("streaming CR before split supplementary pair", decide (prepareValues [[13, 0xd83d], [], [0xdca9]] = some [10, 0x1f4a9])),
  ("streaming pending CR then unpaired high at EOF", decide (prepareValues [[13], [0xd800]] = some [10, 0xfffd])),
  ("streaming pair then trailing CR", decide (prepareValues [[0xd83d], [0xdca9, 13]] = some [0x1f4a9, 10])),
  ("streaming LF interrupts surrogate pair", decide (prepareValues [[0xd83d], [10], [0xdca9]] = some [0xfffd, 10, 0xfffd])),
  ("streaming out of range code unit rejected", decide (decodeValues [[0x10000]] = none)),
  ("streaming supplementary point is not one unit", decide (prepareValues [[0x1f4a9]] = none)),
  ("streaming upper code unit boundary", decide (decodeValues [[0xffff]] = some [0xffff])),
  ("streaming ordinary unit emitted immediately", decide ((feed utf16 none [0x61]).output.map Fin.val = [0x61])),
  ("streaming leading surrogate carried without emission", decide ((feed utf16 none [0xd800]).output = [])),
  ("streaming empty feed preserves high carry", decide ((feed utf16 (some 0xd800) []).pending = some 0xd800)),
  ("streaming paired carry cleared", decide ((feed utf16 (some 0xd800) [0xdc00]).pending = none)),
  ("streaming CR carried without emission", decide ((feed css none [13]).output = [])),
  ("streaming empty feed preserves CR carry", decide ((feed css (some 13) []).pending = some 13)),
  ("streaming CRLF carry cleared", decide ((feed css (some 13) [10]).pending = none))
]

theorem checks_pass : checks.all Prod.snd = true := by decide +kernel

end CssSemantics.StreamingExamples
