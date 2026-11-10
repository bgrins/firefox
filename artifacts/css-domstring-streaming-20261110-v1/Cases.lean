import Pipeline
import Adapters

namespace CssStreaming.Cases

def prepareValues (input : List (List Nat)) : Option (List Nat) :=
  (admittedChunks input).map fun chunks => (pipeline utf16 css chunks).map Char.toNat

def checks : List (String × Bool) := [
  ("no chunks", decide (decodeValues [] = some [])),
  ("empty chunks", decide (prepareValues [[], [], []] = some [])),
  ("split surrogate pair", decide (decodeValues [[0xd83d], [0xdca9]] = some [0x1f4a9])),
  ("pair across empty chunks", decide (decodeValues [[0xd83d], [], [], [0xdca9]] = some [0x1f4a9])),
  ("minimum pair", decide (decodeValues [[0xd800], [0xdc00]] = some [0x10000])),
  ("maximum pair", decide (decodeValues [[0xdbff], [0xdfff]] = some [0x10ffff])),
  ("isolated leading surrogate retained before CSS", decide (decodeValues [[0xd800]] = some [0xd800])),
  ("isolated leading surrogate replaced at CSS EOF", decide (prepareValues [[0xd800]] = some [0xfffd])),
  ("trailing surrogate is not carried", decide (decodeValues [[0xdc00]] = some [0xdc00])),
  ("reversed surrogates remain separate", decide (decodeValues [[0xdc00], [0xd800]] = some [0xdc00, 0xd800])),
  ("overlapping leading candidates", decide (decodeValues [[0xd800], [0xd801], [0xdc00]] = some [0xd800, 0x10400])),
  ("ordinary unit interrupts pairing", decide (decodeValues [[0xd83d], [0x61], [0xdca9]] = some [0xd83d, 0x61, 0xdca9])),
  ("split CRLF", decide (prepareValues [[13], [10]] = some [10])),
  ("CRLF across empty chunks", decide (prepareValues [[13], [], [10]] = some [10])),
  ("CR before ordinary unit", decide (prepareValues [[13], [0x61]] = some [10, 0x61])),
  ("trailing CR flushed", decide (prepareValues [[13]] = some [10])),
  ("CR CR LF", decide (prepareValues [[13], [13], [10]] = some [10, 10])),
  ("NUL and FF", decide (prepareValues [[0], [12]] = some [0xfffd, 10])),
  ("CR before split supplementary pair", decide (prepareValues [[13, 0xd83d], [], [0xdca9]] = some [10, 0x1f4a9])),
  ("pending CR then unpaired high at EOF", decide (prepareValues [[13], [0xd800]] = some [10, 0xfffd])),
  ("pair then trailing CR", decide (prepareValues [[0xd83d], [0xdca9, 13]] = some [0x1f4a9, 10])),
  ("LF interrupts surrogate pair", decide (prepareValues [[0xd83d], [10], [0xdca9]] = some [0xfffd, 10, 0xfffd])),
  ("out of range code unit rejected", decide (decodeValues [[0x10000]] = none)),
  ("supplementary point is not one unit", decide (prepareValues [[0x1f4a9]] = none)),
  ("upper code unit boundary", decide (decodeValues [[0xffff]] = some [0xffff])),
  ("ordinary unit emitted immediately", decide ((feed utf16 none [0x61]).output.map Fin.val = [0x61])),
  ("leading surrogate carried without emission", decide ((feed utf16 none [0xd800]).output = [])),
  ("empty feed preserves high carry", decide ((feed utf16 (some 0xd800) []).pending = some 0xd800)),
  ("paired carry cleared", decide ((feed utf16 (some 0xd800) [0xdc00]).pending = none)),
  ("CR carried without emission", decide ((feed css none [13]).output = [])),
  ("empty feed preserves CR carry", decide ((feed css (some 13) []).pending = some 13)),
  ("CRLF carry cleared", decide ((feed css (some 13) [10]).pending = none))
]

end CssStreaming.Cases
