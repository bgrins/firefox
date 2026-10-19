import ConstructorIdentity
namespace IdentityWitnesses
open AnimationIdentity SegmentIdentity MapIdentity ConstructorIdentity
abbrev V := Value Nat Nat
def failArithmetic : Arithmetic Nat Nat := fun _ _ _ => none
def leftArithmetic : Arithmetic Nat Nat := fun _ a _ => some a
def wrongArithmetic : Arithmetic Nat Nat := fun _ _ _ => some ⟨9,90⟩
def s : Segment Nat Nat := ⟨some ⟨1,10⟩,some ⟨1,20⟩,.replace,.replace,false,false,true,123⟩
def a : Action Nat Nat := ⟨1,true,s,none,none,false,0⟩

theorem fail_provider_admitted : Preserves failArithmetic := by
  intro proc x y out _ h;cases h

theorem success_provider_admitted : Preserves leftArithmetic := by
  intro proc x y out _ h;cases h;rfl

theorem ordinary_ready_without_base : compose failArithmetic s none none false 0=some ⟨1,10⟩ := by decide

theorem interpolation_failure_right_fallback :
    compose failArithmetic {s with beforeHalf:=false} none none false 0=some ⟨1,20⟩ := by decide

theorem zero_length_ignores_bad_arithmetic :
    compose wrongArithmetic {s with equalKeys:=true,negativeTotal:=true} none none false 0=some ⟨1,10⟩ := by decide

theorem zero_length_nonnegative_chooses_to :
    compose wrongArithmetic {s with equalKeys:=true,negativeTotal:=false} none none false 0=some ⟨1,20⟩ := by decide

theorem missing_endpoint_uses_underlying :
    compose failArithmetic {s with fromValue:=none} (some ⟨1,30⟩) none false 0=some ⟨1,30⟩ := by decide

theorem addition_failure_uses_original :
    compose failArithmetic {s with fromMode:=.add} (some ⟨1,30⟩) none false 0=some ⟨1,10⟩ := by decide

theorem accumulation_failure_retains_composited :
    accumulate failArithmetic none (some ⟨1,30⟩) ⟨1,40⟩ 7=some (some ⟨1,30⟩) := by decide

theorem accumulation_failure_retains_original_selection :
    selected failArithmetic (some ⟨1,10⟩) none (some ⟨1,40⟩) true 7=some ⟨1,10⟩ := by decide

theorem active_missing_last_needs_base : need s none true 7=true := by decide

theorem inactive_missing_last_does_not_need_base : need s none true 0=false := by decide

theorem missing_base_skips_map_write : step failArithmetic [] {a with iterationAccumulate:=true,count:=7}=some [] := by decide

theorem existing_map_precedes_base :
    step failArithmetic [(1,⟨1,44⟩)] {a with segment:={s with fromValue:=none},base:=some ⟨1,55⟩}=
      some [(1,⟨1,44⟩)] := by decide

theorem arithmetic_admission_necessary :
    compose wrongArithmetic s none none false 0=some ⟨9,90⟩ := by decide

theorem underlying_readiness_necessary :
    compose failArithmetic {s with fromMode:=.add} none none false 0=none := by decide

theorem last_readiness_necessary : compose failArithmetic s none none true 7=none := by decide

theorem endpoint_identity_necessary :
    compose failArithmetic {s with fromValue:=some ⟨2,20⟩} none none false 0=some ⟨2,20⟩ := by decide

theorem key_value_coherence_necessary :
    ¬Valid (build (fun v : V => v) [(1,⟨2,20⟩)]) := by
  intro h
  have hm := h.2.2.1 1
  simpa [constructor_fields] using hm

theorem uncompute_identity_necessary :
    ¬Valid (build (fun _ : V => (⟨2,20⟩ : V)) [(1,⟨1,10⟩)]) := by
  intro h
  have hm := h.2.2.1 1
  simpa [constructor_fields] using hm

theorem enumeration_uniqueness_necessary :
    ¬Valid (build (fun v : V => v) [(1,⟨1,10⟩),(1,⟨1,20⟩)]) := by
  intro h
  have hu := h.1
  simpa [constructor_fields] using hu

theorem nonempty_history : run failArithmetic [] [a,a]=some [(1,⟨1,10⟩)] := by decide

theorem nonempty_constructor :
    build (fun v : V => v) [(1,⟨1,10⟩),(2,⟨2,20⟩)] =
      ⟨[⟨1,10⟩,⟨2,20⟩],[2,1],[false,false],true⟩ := by rfl
end IdentityWitnesses
