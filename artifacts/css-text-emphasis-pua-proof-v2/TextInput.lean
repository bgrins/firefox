import NativeDomain

namespace Emphasis.TextInput
open RawBridge NativeDomain

def setup (units : List Ligature.Unit) (flags : List Bool) : List Ligature.Unit :=
  List.zipWith flagUnit units flags

theorem flag_shape (unit : Ligature.Unit) (accepted : Bool) :
    projectShape (flagUnit unit accepted) = projectShape unit := by
  cases accepted <;> cases unit with
  | mk glyph before after => cases glyph <;> rfl

theorem flag_details (unit : Ligature.Unit) (accepted : Bool) :
    (contents (flagUnit unit accepted).glyph).2.2 = (contents unit.glyph).2.2 := by
  cases accepted <;> cases unit with
  | mk glyph before after => cases glyph <;> rfl

theorem setup_shape (units : List Ligature.Unit) (flags : List Bool)
    (sameLength : units.length = flags.length) :
    (setup units flags).map projectShape = units.map projectShape := by
  induction units generalizing flags with
  | nil => simp [setup]
  | cons unit rest ih =>
    cases flags with
    | nil => simp at sameLength
    | cons flag flags =>
      simp only [List.length_cons,Nat.add_right_cancel_iff] at sameLength
      simp [setup,flag_shape,show (List.zipWith flagUnit rest flags).map projectShape = rest.map projectShape from ih flags sameLength]

theorem setup_details (units : List Ligature.Unit) (flags : List Bool)
    (sameLength : units.length = flags.length) :
    (setup units flags).map (fun u => (contents u.glyph).2.2) =
      units.map (fun u => (contents u.glyph).2.2) := by
  induction units generalizing flags with
  | nil => simp [setup]
  | cons unit rest ih =>
    cases flags with
    | nil => simp at sameLength
    | cons flag flags =>
      simp only [List.length_cons,Nat.add_right_cancel_iff] at sameLength
      simp [setup,flag_details,show (List.zipWith flagUnit rest flags).map (fun u => (contents u.glyph).2.2) = rest.map (fun u => (contents u.glyph).2.2) from ih flags sameLength]


theorem flag_advance (unit : Ligature.Unit) (accepted : Bool) (letter : Int) :
    Run.glyphAdvance (flagUnit unit accepted).glyph letter = Run.glyphAdvance unit.glyph letter := by
  cases accepted <;> cases unit with
  | mk glyph before after => cases glyph <;> simp [flagUnit,applyFlag,suppress,Run.glyphAdvance,contents,simpleFlags] <;> rfl

theorem setup_advances (units : List Ligature.Unit) (flags : List Bool) (letter : Int)
    (sameLength : units.length = flags.length) :
    (setup units flags).map (fun u => Run.glyphAdvance u.glyph letter) =
      units.map (fun u => Run.glyphAdvance u.glyph letter) := by
  induction units generalizing flags with
  | nil => simp [setup]
  | cons unit rest ih =>
    cases flags with
    | nil => simp at sameLength
    | cons flag flags =>
      simp only [List.length_cons,Nat.add_right_cancel_iff] at sameLength
      simp [setup,flag_advance,show (List.zipWith flagUnit rest flags).map (fun u => Run.glyphAdvance u.glyph letter) = rest.map (fun u => Run.glyphAdvance u.glyph letter) from ih flags sameLength]

theorem setup_ligature_cuts (units : List Ligature.Unit) (flags : List Bool)
    (sameLength : units.length = flags.length) :
    (setup units flags).map Ligature.ligatureStart = units.map Ligature.ligatureStart := by
  have h := congrArg (List.map ShapeUnit.ligature) (setup_shape units flags sameLength)
  simp only [List.map_map] at h
  exact h

theorem setup_length_eq (units : List Ligature.Unit) (flags : List Bool)
    (sameLength : units.length = flags.length) : (setup units flags).length = units.length := by
  simp [setup,List.length_zipWith,sameLength]

theorem setup_ligature_bounds (units : List Ligature.Unit) (flags : List Bool) (start : Nat)
    (sameLength : units.length = flags.length) :
    Ligature.nativeBounds (setup units flags) start = Ligature.nativeBounds units start := by
  simp [Ligature.nativeBounds,setup_ligature_cuts units flags sameLength]


theorem flag_prefix_safe (unit : Ligature.Unit) (accepted : Bool) (letter : Int) :
    glyphPrefixesSafe (flagUnit unit accepted).glyph letter = glyphPrefixesSafe unit.glyph letter := by
  cases accepted <;> cases unit with
  | mk glyph before after => cases glyph <;> rfl

theorem setup_property (property : Ligature.Unit → Prop)
    (preserves : ∀ unit accepted, property unit → property (flagUnit unit accepted))
    (units : List Ligature.Unit) (flags : List Bool) (valid : ∀ unit ∈ units, property unit) :
    ∀ unit ∈ setup units flags, property unit := by
  induction units generalizing flags with
  | nil => simp [setup]
  | cons head rest ih =>
    cases flags with
    | nil => simp [setup]
    | cons flag flags =>
      intro unit member
      rcases List.mem_cons.mp member with same | tail
      · subst unit; exact preserves head flag (valid head (by simp))
      · exact ih flags (by intro u h; exact valid u (by simp [h])) unit tail

theorem setup_metric_safety (units : List Ligature.Unit) (flags : List Bool) (provider : Ligature.Provider)
    (sameLength : units.length = flags.length) (safe : metricInputsSafe units provider) :
    metricInputsSafe (setup units flags) provider := by
  constructor
  · apply setup_property _ _ units flags safe.1
    intro unit accepted h
    simpa only [flag_prefix_safe] using h
  · intro start inside
    dsimp only
    rw [setup_ligature_bounds units flags start sameLength]
    intro count countBound
    have length := setup_length_eq units flags sameLength
    have originalInside : start < units.length := by omega
    have originalCount : count ≤ (Ligature.slice units (Ligature.nativeBounds units start).1
        (Ligature.nativeBounds units start).2).length := by
      simpa only [Ligature.slice,List.length_take,List.length_drop,length] using countBound
    have h := safe.2 start originalInside count originalCount
    simpa [Ligature.slice,setup_advances units flags (Ligature.letterValue provider) sameLength] using h

def surrogateCompatible (text : List Emphasis.Unit) (shape : List ShapeUnit) : Bool :=
  (text.zipIdx).all fun (a,i) =>
    match text[i+1]?, shape[i+1]? with
    | some b, some unit => !pair a b || (!unit.cluster && !unit.ligature)
    | _, _ => true

theorem setup_surrogate_partition (units : List Ligature.Unit) (flags : List Bool)
    (text : List Emphasis.Unit) (sameLength : units.length = flags.length) :
    surrogateCompatible text ((setup units flags).map projectShape) =
      surrogateCompatible text (units.map projectShape) := by rw [setup_shape units flags sameLength]

def recordValid (record : Record) : Bool :=
  (if Raw.simple record.word then record.details.isEmpty
    else record.word.toNat%65536 == record.details.length) &&
  record.details.all (fun d => d.id < 4294967296 &&
    (-2147483648 ≤ d.advance && d.advance ≤ 2147483647))


theorem valid_record_advances (record : Record) (valid : recordValid record = true) :
    ∀ d ∈ (contents (decodeUnit record).glyph).2.2, SignedLigature.Int32 d.advance := by
  by_cases simple : Raw.simple record.word = true
  · simp only [decodeUnit,RawBridge.decode,simple,↓reduceIte,contents,List.mem_cons,List.not_mem_nil,or_false]
    intro d equal
    subst d
    have bound := Nat.mod_lt (record.word.toNat/65536) (by decide : 0 < 4096)
    simp only [SignedLigature.Int32]
    omega
  · have complex : Raw.simple record.word = false := Bool.eq_false_iff.mpr simple
    simp only [decodeUnit,RawBridge.decode,complex,Bool.false_eq_true,↓reduceIte,contents]
    intro d member
    simp only [recordValid,Bool.and_eq_true] at valid
    have accepted := List.all_eq_true.mp valid.2 d member
    simp only [Bool.and_eq_true,decide_eq_true_eq] at accepted
    exact accepted.2

theorem valid_records_advances (records : List Record) (valid : records.all recordValid = true) :
    storedAdvancesValid (records.map decodeUnit) := by
  intro u member d belongs
  rcases List.mem_map.mp member with ⟨record,inside,rfl⟩
  exact valid_record_advances record (List.all_eq_true.mp valid record inside) d belongs

structure Admitted (records : List Record) (text : List Emphasis.Unit)
    (runs : List Selection.Interval) (request : Selection.Interval) : Prop where
  sameLength : records.length = text.length
  words : records.all recordValid = true
  shape : shapeValid (records.map decodeUnit) runs request = true
  surrogates : surrogateCompatible text ((records.map decodeUnit).map projectShape) = true

theorem setup_domain (units : List Ligature.Unit) (flags : List Bool)
    (sameLength : units.length = flags.length) (runs : List Selection.Interval)
    (request : Selection.Interval) (before : NativeDomain.Admitted units runs request) :
    NativeDomain.Admitted (setup units flags) runs request := by
  constructor
  · simpa only [shapeValid,setup_shape units flags sameLength] using before.shape
  · intro unit member detail detailMember
    have belongs : (contents unit.glyph).2.2 ∈ (setup units flags).map (fun u => (contents u.glyph).2.2) := List.mem_map_of_mem member
    rw [setup_details units flags sameLength] at belongs
    rcases List.mem_map.mp belongs with ⟨original,inside,equal⟩
    exact before.advances original inside detail (by simpa only [equal] using detailMember)

theorem original_input_complete_dispatch (records : List Record) (text : List Emphasis.Unit)
    (runs : List Selection.Interval) (request : Selection.Interval)
    (valid : Admitted records text runs request) (eligible : Nat → Bool)
    (policy : Dispatch.WidthPolicy) (provider : Ligature.Provider) (direction mark coordinate : Int) :
    let flags := loopFlags eligible text
    let after := (List.zipWith flagRecord records flags).map decodeUnit
    Ordinary.nativeRuns policy provider after direction mark
      (actualLengthSelection text.length request runs) coordinate =
    Ordinary.referenceOrdinary policy provider
      (setup (records.map decodeUnit) (directFlags eligible text)) direction mark runs request coordinate := by
  have length : (records.map decodeUnit).length = (loopFlags eligible text).length := by
    simpa only [List.length_map,flags_length] using valid.sameLength
  have before : NativeDomain.Admitted (records.map decodeUnit) runs request := ⟨valid.shape,valid_records_advances records valid.words⟩
  have after := setup_domain _ _ length runs request before
  dsimp only
  rw [buffer_flag_bridge]
  change Ordinary.nativeRuns policy provider (setup (records.map decodeUnit) (loopFlags eligible text)) direction mark
    (actualLengthSelection text.length request runs) coordinate = _
  have afterLength : (setup (records.map decodeUnit) (loopFlags eligible text)).length = text.length := by
    simp [setup,List.length_zipWith,List.length_map,flags_length,valid.sameLength]
  rw [← afterLength,actual_length_complete_dispatch _ _ _ after]
  rw [flags_refinement]

def exampleRecord : Record := ⟨0x800a0041,[],0,0⟩

theorem inhabited_original_input :
    Admitted [exampleRecord] [⟨65,by decide⟩] [⟨0,1⟩] ⟨0,1⟩ :=
  ⟨by decide +kernel,by decide +kernel,by decide +kernel,by decide +kernel⟩

theorem inhabited_original_empty : Admitted [] [] [] ⟨0,0⟩ :=
  ⟨by decide +kernel,by decide +kernel,by decide +kernel,by decide +kernel⟩

theorem inhabited_original_pair :
    Admitted [exampleRecord,⟨0x70000,[],0,0⟩] [⟨0xDB80,by decide⟩,⟨0xDC00,by decide⟩]
      [⟨0,2⟩] ⟨0,2⟩ :=
  ⟨by decide +kernel,by decide +kernel,by decide +kernel,by decide +kernel⟩

end Emphasis.TextInput
