import RawWords
import RunDispatch

namespace Emphasis.RawBridge
open Raw
set_option linter.unusedSimpArgs false

def flag (word : Word) (mask : Word) : Bool := word &&& mask != 0

theorem flag_bit17 (word : Word) : flag word 0x20000 = word.getLsbD 17 := by
  have masked : word &&& 0x20000 = (if word.getLsbD 17 then 0x20000 else 0) := by
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals split <;> simp_all [BitVec.getLsbD_and,BitVec.getLsbD_ofNat]
  unfold flag
  rw [masked]
  cases word.getLsbD 17 <;> simp

theorem flag_bit18 (word : Word) : flag word 0x40000 = word.getLsbD 18 := by
  have masked : word &&& 0x40000 = (if word.getLsbD 18 then 0x40000 else 0) := by
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals split <;> simp_all [BitVec.getLsbD_and,BitVec.getLsbD_ofNat]
  unfold flag
  rw [masked]
  cases word.getLsbD 18 <;> simp

theorem flag_bit22 (word : Word) : flag word 0x400000 = word.getLsbD 22 := by
  have masked : word &&& 0x400000 = (if word.getLsbD 22 then 0x400000 else 0) := by
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals split <;> simp_all [BitVec.getLsbD_and,BitVec.getLsbD_ofNat]
  unfold flag
  rw [masked]
  cases word.getLsbD 22 <;> simp

theorem flag_bit28 (word : Word) : flag word 0x10000000 = word.getLsbD 28 := by
  have masked : word &&& 0x10000000 = (if word.getLsbD 28 then 0x10000000 else 0) := by
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
    rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals split <;> simp_all [BitVec.getLsbD_and,BitVec.getLsbD_ofNat]
  unfold flag
  rw [masked]
  cases word.getLsbD 28 <;> simp

def nativeCluster (word : Word) : Bool := Raw.simple word || !flag word 0x20000
def nativeLigature (word : Word) : Bool := Raw.simple word || !flag word 0x40000
def nativeMay (word : Word) : Bool := !flag word 0x10000000 && (Raw.simple word || !flag word 0x400000)

def breakBits (word : Word) : Fin 4 :=
  ⟨(if word.getLsbD 29 then 1 else 0)+(if word.getLsbD 30 then 2 else 0),by
    cases word.getLsbD 29 <;> cases word.getLsbD 30 <;> decide⟩

def decode (word : Word) (details : List Detail) : Glyph :=
  let common : Common := ⟨breakBits word,word.getLsbD 28⟩
  if Raw.simple word then
    .simple common ⟨word.toNat%65536,Nat.mod_lt _ (by decide)⟩
      ⟨(word.toNat/65536)%4096,Nat.mod_lt _ (by decide)⟩
  else
    .complex common
      ⟨!word.getLsbD 17,!word.getLsbD 18,!word.getLsbD 16,
       word.getLsbD 20,word.getLsbD 21,word.getLsbD 23,word.getLsbD 19,word.getLsbD 22⟩ details

theorem cluster_accessor (word : Word) (details : List Detail) :
    (contents (decode word details)).2.1.clusterStart = nativeCluster word := by
  simp only [decode,nativeCluster,flag_bit17]
  split <;> simp_all [contents,simpleFlags]

theorem ligature_accessor (word : Word) (details : List Detail) :
    (contents (decode word details)).2.1.ligatureStart = nativeLigature word := by
  simp only [decode,nativeLigature,flag_bit18]
  split <;> simp_all [contents,simpleFlags]

theorem eligibility_accessor (word : Word) (details : List Detail) :
    charMay (decode word details) = nativeMay word := by
  simp only [decode,nativeMay,flag_bit28,flag_bit22]
  split <;> simp_all [charMay,contents,simpleFlags]

def nativeAdvance (word : Word) (details : List Detail) (letter : Int) : Int :=
  if Raw.simple word then ((word.toNat/65536)%4096 : Nat)
  else (details.map Detail.advance).sum +
    (if word.getLsbD 19 then (details.length-1 : Nat)*letter else 0)

theorem advance_accessor (word : Word) (details : List Detail) (letter : Int) :
    Run.glyphAdvance (decode word details) letter = nativeAdvance word details letter := by
  simp only [decode,nativeAdvance]
  split <;> simp [Run.glyphAdvance,contents,simpleFlags]

def suppressedDetails (word : Word) (details : List Detail) : List Detail :=
  if Raw.simple word then [⟨word.toNat%65536,(word.toNat/65536)%4096,0,0⟩] else details

theorem raw_suppression_refinement (word : Word) (details : List Detail) :
    decode (Raw.suppress word) (suppressedDetails word details) =
      Emphasis.suppress (decode word details) := by
  simp only [decode,Raw.suppressed_is_complex,Bool.false_eq_true,↓reduceIte]
  cases h : Raw.simple word with
  | false =>
    simp [h,Emphasis.suppress,suppressedDetails,Raw.suppress,Raw.setNoEmphasis,breakBits]
  | true =>
    simp [h,Emphasis.suppress,suppressedDetails,Raw.suppress,Raw.setNoEmphasis,
      Raw.convert,Raw.common,breakBits,simpleFlags]

structure Record where
  word : Word
  details : List Detail
  before : Int
  after : Int
  deriving DecidableEq, Repr

def decodeUnit (r : Record) : Ligature.Unit := ⟨decode r.word r.details,r.before,r.after⟩

def flagRecord (r : Record) (accepted : Bool) : Record :=
  if accepted then r else {r with word := Raw.suppress r.word,details := suppressedDetails r.word r.details}

def flagUnit (u : Ligature.Unit) (accepted : Bool) : Ligature.Unit :=
  {u with glyph := applyFlag u.glyph accepted}

theorem record_flag_bridge (record : Record) (accepted : Bool) :
    decodeUnit (flagRecord record accepted) = flagUnit (decodeUnit record) accepted := by
  cases accepted <;> simp [decodeUnit,flagRecord,flagUnit,applyFlag,raw_suppression_refinement]

theorem buffer_flag_bridge (records : List Record) (flags : List Bool) :
    (List.zipWith flagRecord records flags).map decodeUnit =
      List.zipWith flagUnit (records.map decodeUnit) flags := by
  induction records generalizing flags with
  | nil => simp
  | cons record rest ih =>
    cases flags with
    | nil => simp
    | cons flag flags => simp [record_flag_bridge,ih]

theorem setup_length (records : List Record) (eligible : Nat → Bool) (text : List Emphasis.Unit)
    (sameLength : records.length = text.length) :
    (List.zipWith flagRecord records (loopFlags eligible text)).length = records.length := by
  simp [List.length_zipWith,flags_length,sameLength]

theorem setup_through_complete_dispatch (records : List Record) (eligible : Nat → Bool)
    (text : List Emphasis.Unit) (policy : Dispatch.WidthPolicy) (provider : Ligature.Provider)
    (direction mark : Int) (runs : List Selection.Interval) (request : Selection.Interval)
    (coordinate : Int) (ordered : Selection.OrderedRuns runs)
    (initial : runs = [] ∨ ∃ first, runs[0]? = some first ∧ first.first = 0) :
    Ordinary.nativeOrdinary policy provider
      ((List.zipWith flagRecord records (loopFlags eligible text)).map decodeUnit)
      direction mark runs request coordinate =
    Ordinary.referenceOrdinary policy provider
      (List.zipWith flagUnit (records.map decodeUnit) (directFlags eligible text))
      direction mark runs request coordinate := by
  rw [buffer_flag_bridge,flags_refinement]
  exact Ordinary.complete_raw_dispatch _ _ _ _ _ _ _ _ ordered initial

end Emphasis.RawBridge
