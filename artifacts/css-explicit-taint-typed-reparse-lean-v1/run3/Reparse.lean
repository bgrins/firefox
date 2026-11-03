import Taint

namespace ExplicitTaintReparse
open RetainedAggregateTaint

structure Universal where
  bytes : List UInt8
  innerExplicit : Bool
  wrapperTaint : Bool
  deriving DecidableEq, Repr

structure ReferenceFree where
  bytes : List UInt8
  explicitTaint : Bool
  deriving DecidableEq, Repr

structure Typed (α : Type) where
  payload : α
  tainted : Bool
  deriving DecidableEq, Repr

def wrap (c : Custom) : Universal := ⟨c.bytes, false, c.tainted⟩

def uncompute (u : Universal) : ReferenceFree :=
  if u.wrapperTaint && !u.innerExplicit then ⟨u.bytes, true⟩
  else ⟨u.bytes, u.innerExplicit⟩

def legacyNoReferences (d : ReferenceFree) : Custom := ⟨d.bytes, false⟩
def transportedNoReferences (d : ReferenceFree) : Custom := ⟨d.bytes, d.explicitTaint⟩

def parseTyped (parser : List UInt8 → Option α) (c : Custom) : Option (Typed α) :=
  (parser c.bytes).map (fun value => ⟨value, c.tainted⟩)

def legacyReparse (parser : List UInt8 → Option α) (u : Universal) :=
  parseTyped parser (legacyNoReferences (uncompute u))

def transportedReparse (parser : List UInt8 → Option α) (u : Universal) :=
  parseTyped parser (transportedNoReferences (uncompute u))

def payloadOnly (result : Option (Typed α)) : Option α := result.map Typed.payload
def withInitial (initial : Typed α) (result : Option (Typed α)) : Typed α :=
  result.getD initial

theorem uncompute_bytes (u : Universal) : (uncompute u).bytes = u.bytes := by
  simp only [uncompute]; split <;> rfl

theorem uncompute_provenance (u : Universal) :
    (uncompute u).explicitTaint = (u.innerExplicit || u.wrapperTaint) := by
  cases u with
  | mk bytes inner wrapper => cases inner <;> cases wrapper <;> rfl

theorem published_wrapper_roundtrip (c : Custom) :
    transportedNoReferences (uncompute (wrap c)) = c := by
  cases c with
  | mk bytes bit => cases bit <;> rfl

theorem parse_payload_erasure (parser : List UInt8 → Option α) (c : Custom) :
    payloadOnly (parseTyped parser c) = parser c.bytes := by
  cases h : parser c.bytes <;> simp [payloadOnly, parseTyped, h]

theorem legacy_payload_erasure (parser : List UInt8 → Option α) (u : Universal) :
    payloadOnly (legacyReparse parser u) = parser u.bytes := by
  simp [legacyReparse, parse_payload_erasure, legacyNoReferences, uncompute_bytes]

theorem transported_payload_erasure (parser : List UInt8 → Option α) (u : Universal) :
    payloadOnly (transportedReparse parser u) = parser u.bytes := by
  simp [transportedReparse, parse_payload_erasure, transportedNoReferences, uncompute_bytes]

theorem same_parse_decision_and_payload (parser : List UInt8 → Option α) (u : Universal) :
    payloadOnly (legacyReparse parser u) = payloadOnly (transportedReparse parser u) := by
  rw [legacy_payload_erasure, transported_payload_erasure]

theorem legacy_success_loses_bit (parser : List UInt8 → Option α) (u : Universal)
    (value : α) (success : parser u.bytes = some value) :
    legacyReparse parser u = some ⟨value, false⟩ := by
  simp [legacyReparse, parseTyped, legacyNoReferences, uncompute_bytes, success]

theorem transported_success_retains_bit (parser : List UInt8 → Option α) (u : Universal)
    (value : α) (success : parser u.bytes = some value) :
    transportedReparse parser u = some ⟨value, u.innerExplicit || u.wrapperTaint⟩ := by
  simp [transportedReparse, parseTyped, transportedNoReferences, uncompute_bytes,
    uncompute_provenance, success]

theorem admitted_dirty_handoff_differs (parser : List UInt8 → Option α) (u : Universal)
    (value : α) (success : parser u.bytes = some value)
    (dirty : (u.innerExplicit || u.wrapperTaint) = true) :
    legacyReparse parser u ≠ transportedReparse parser u := by
  rw [legacy_success_loses_bit parser u value success,
    transported_success_retains_bit parser u value success, dirty]
  simp

theorem rejected_parse_selects_initial (parser : List UInt8 → Option α) (u : Universal)
    (initial : Typed α) (rejected : parser u.bytes = none) :
    withInitial initial (legacyReparse parser u) = initial ∧
    withInitial initial (transportedReparse parser u) = initial := by
  simp [withInitial, legacyReparse, transportedReparse, parseTyped,
    legacyNoReferences, transportedNoReferences, uncompute_bytes, rejected]

theorem rejected_parse_stays_invalid (parser : List UInt8 → Option α) (u : Universal)
    (rejected : parser u.bytes = none) :
    legacyReparse parser u = none ∧ transportedReparse parser u = none := by
  simp [legacyReparse, transportedReparse, parseTyped, legacyNoReferences,
    transportedNoReferences, uncompute_bytes, rejected]

theorem successful_parse_does_not_take_initial (parser : List UInt8 → Option α)
    (u : Universal) (value : α) (initial : Typed α)
    (success : parser u.bytes = some value) :
    withInitial initial (transportedReparse parser u) =
      ⟨value, u.innerExplicit || u.wrapperTaint⟩ := by
  rw [transported_success_retains_bit parser u value success]
  rfl

theorem completed_origin_trace_transport (parser : List UInt8 → Option α)
    (chunks : List Chunk) (value : α)
    (success : parser (run initial chunks).bytes = some value) :
    transportedReparse parser (wrap (publish (run initial chunks))) =
      some ⟨value, !(provenance chunks).isEmpty⟩ := by
  unfold transportedReparse
  rw [published_wrapper_roundtrip]
  simp [parseTyped, publish, success]
  simpa [publish] using publication_conserves_trace chunks

theorem same_bytes_cannot_reconstruct_provenance (bytes : List UInt8) :
    ¬∃ recover : List UInt8 → Bool, ∀ bit,
      recover (uncompute (wrap ⟨bytes, bit⟩)).bytes =
        (uncompute (wrap ⟨bytes, bit⟩)).explicitTaint := by
  rintro ⟨recover, all⟩
  have clean := all false
  have dirty := all true
  change recover bytes = false at clean
  change recover bytes = true at dirty
  rw [clean] at dirty
  contradiction

def echo : List UInt8 → Option (List UInt8) := some
def quoted : List UInt8 := [34, 120, 34]
def dirty : Universal := ⟨quoted, false, true⟩
def clean : Universal := ⟨quoted, false, false⟩

theorem equal_payload_distinct_provenance :
    payloadOnly (transportedReparse echo dirty) = payloadOnly (transportedReparse echo clean) ∧
    transportedReparse echo dirty ≠ transportedReparse echo clean := by decide

theorem inner_explicit_also_survives :
    transportedReparse echo ⟨quoted, true, false⟩ = some ⟨quoted, true⟩ := by decide

theorem clean_input_stays_clean :
    transportedReparse echo clean = legacyReparse echo clean := by decide

theorem aggregate_empty_contribution_survives :
    transportedReparse echo (wrap (publish dirtyWitness)) =
      some ⟨dirtyWitness.bytes, true⟩ := by decide

end ExplicitTaintReparse
