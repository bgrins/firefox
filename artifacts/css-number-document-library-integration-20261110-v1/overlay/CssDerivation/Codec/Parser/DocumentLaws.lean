import CssDerivation.Codec.Parser.Document
import CssDerivation.Codec.Parser.EncoderLaws

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR DocumentSchema

theorem string_option_spec (j : Json) (value : String) :
    j.getStr?.toOption = some value ↔ j.getStr? = .ok value := by
  cases j.getStr? <;> simp [Except.toOption]

theorem object_option_spec (j : Json) :
    (∃ value, j.getObj?.toOption = some value) ↔ ObjectValue j := by
  cases j <;> simp [Json.getObj?, Except.toOption, ObjectValue]
  exact ⟨_, rfl⟩

theorem envelope_keys_unique : envelopeKeys.Nodup := by decide

theorem document_spec {shape} (j : Json) (p : Parser shape) :
    readDocument shape j = some p ↔ EnvelopeSchema j p := by
  constructor
  · intro accepted
    by_cases keys : fieldsExactly j envelopeKeys = true
    · simp only [readDocument, keys, Bool.not_true, Bool.false_eq_true, ite_false,
        Option.bind_eq_bind, Option.bind_eq_some_iff] at accepted
      obtain ⟨version, versionField, accepted⟩ := accepted
      by_cases versionOk : version.getStr?.toOption = some "css-parser-ir-v1"
      · simp only [versionOk] at accepted
        change (field j "source_map").bind _ = some p at accepted
        simp only [Option.bind_eq_some_iff] at accepted
        obtain ⟨sourceMap, sourceMapField, map, sourceMapRead, source, sourceField, programRead⟩ := accepted
        exact ⟨version, sourceMap, source, (exact_keys_spec _ _ envelope_keys_unique).mp keys,
          (field_spec _ _ _).mp versionField, (string_option_spec _ _).mp versionOk,
          (field_spec _ _ _).mp sourceMapField, (object_option_spec _).mp ⟨map, sourceMapRead⟩,
          (field_spec _ _ _).mp sourceField, (decodeParser_spec _ _).mp programRead⟩
      · simp [versionOk] at accepted
    · simp [readDocument, keys] at accepted
  · rintro ⟨version, sourceMap, source, keys, versionField, versionOk,
      sourceMapField, sourceMapObject, sourceField, programSchema⟩
    obtain ⟨map, mapRead⟩ := (object_option_spec _).mpr sourceMapObject
    simp [readDocument, (exact_keys_spec _ _ envelope_keys_unique).mpr keys,
      (field_spec _ _ _).mpr versionField, (string_option_spec _ _).mpr versionOk,
      (field_spec _ _ _).mpr sourceMapField, mapRead,
      (field_spec _ _ _).mpr sourceField, (decodeParser_spec _ _).mpr programSchema]

theorem document_json_roundtrip {shape} (p : Parser shape) :
    readDocument shape (encodeDocument p) = some p := by
  change decodeParser shape (encodeParser p) = some p
  exact parser_json_roundtrip p

theorem document_lowering {shape} (j : Json) (p : Parser shape) (state : State)
    (schema : EnvelopeSchema j p) :
    executeDocument shape j state = some (CssParserLowering.observed state (ParserIR.run p state)) := by
  simp [executeDocument, (document_spec _ _).mpr schema, CssParserLowering.lowering_correct]

theorem document_failure_atomic {shape} (j : Json) (p : Parser shape) (state : State)
    (schema : EnvelopeSchema j p) (failed : ParserIR.run p state = none) :
    executeDocument shape j state = some (none, state) := by
  rw [document_lowering j p state schema, failed]
  rfl

theorem document_success_exact {shape} (j : Json) (p : Parser shape) (before after : State)
    (value : shape.Value) (schema : EnvelopeSchema j p)
    (success : ParserIR.run p before = some (value, after)) :
    executeDocument shape j before = some (some value, after) := by
  rw [document_lowering j p before schema, success]
  rfl

end CssDerivation.ParserJson
