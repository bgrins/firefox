import StickyNumeric
import WidenedInsets

namespace WideNormalization
open StickyNumeric StickyAxis

def wide (x : Int) : Int :=
  (x + 9223372036854775808) % 18446744073709551616 - 9223372036854775808

theorem wide_exact (x : Int) (h : WidenedInsets.In64 x) : wide x = x := by
  unfold wide WidenedInsets.In64 at *
  omega

def machineEnd (port box start ending : Int) : Int :=
  let first := wide (port - start)
  let extent := wide (first - ending)
  if box > extent then signed32 (wide (ending - wide (box - extent)))
  else signed32 ending

theorem machine_end_refines (p b s e : Int)
    (hp : InMachine p) (hb : InMachine b) (hs : InMachine s) (he : InMachine e)
    (hr : InMachine (WidenedInsets.nativeEnd p b s e)) :
    machineEnd p b s e = WidenedInsets.referenceEnd p b s e := by
  have h := WidenedInsets.all_wide_intermediates p b s e hp hb hs he
  simp only [WidenedInsets.view] at h
  dsimp only [machineEnd]
  rw [wide_exact _ h.1, wide_exact _ h.2.1]
  by_cases branch : b > p - s - e
  · simp only [branch, ↓reduceIte]
    rw [wide_exact _ h.2.2.1, wide_exact _ h.2.2.2]
    have result : InMachine (e - (b - (p-s-e))) := by
      simpa [WidenedInsets.nativeEnd,WidenedInsets.view,branch] using hr
    rw [signed32_exact _ result]
    rw [← WidenedInsets.end_refines]
    simp [WidenedInsets.nativeEnd,WidenedInsets.view,branch]
  · simp only [branch, ↓reduceIte]
    rw [signed32_exact e he, ← WidenedInsets.end_refines]
    simp [WidenedInsets.nativeEnd,WidenedInsets.view,branch]

def rawValue (modern : Bool) (v : Option Int) : Int :=
  v.getD (if modern then 0 else coordMax)

def active (modern : Bool) (v : Insets) : Bool :=
  if modern then v.near.isSome || v.far.isSome else v.near.isSome && v.far.isSome

def source (modern : Bool) (v : Insets) (port box : Int) (endFar : Bool) : Int × Int :=
  let a := rawValue modern v.near
  let b := rawValue modern v.far
  if active modern v then
    if endFar then (a,WidenedInsets.nativeEnd port box a b)
    else (WidenedInsets.nativeEnd port box b a,b)
  else (a,b)

def reference (modern : Bool) (v : Insets) (port box : Int) (endFar : Bool) : Int × Int :=
  let a := rawValue modern v.near
  let b := rawValue modern v.far
  if active modern v then
    if endFar then (a,min b (port-a-box))
    else (min a (port-b-box),b)
  else (a,b)

def machine (modern : Bool) (v : Insets) (port box : Int) (endFar : Bool) : Int × Int :=
  let a := rawValue modern v.near
  let b := rawValue modern v.far
  if active modern v then
    if endFar then (a,machineEnd port box a b)
    else (machineEnd port box b a,b)
  else (a,b)

def Safe (modern : Bool) (v : Insets) (p b : Int) (endFar : Bool) : Prop :=
  InMachine (rawValue modern v.near) ∧ InMachine (rawValue modern v.far) ∧
  (if active modern v then
    InMachine p ∧ InMachine b ∧
    InMachine (source modern v p b endFar).1 ∧ InMachine (source modern v p b endFar).2
   else True)

instance (m : Bool) (v : Insets) (p b : Int) (e : Bool) : Decidable (Safe m v p b e) := by
  unfold Safe; infer_instance

theorem source_reference (m : Bool) (v : Insets) (p b : Int) (e : Bool) :
    source m v p b e = reference m v p b e := by
  simp only [source,reference,WidenedInsets.end_refines,WidenedInsets.referenceEnd]

theorem machine_reference (m : Bool) (v : Insets) (p b : Int) (e : Bool)
    (safe : Safe m v p b e) : machine m v p b e = reference m v p b e := by
  rcases safe with ⟨ha,hb,h⟩
  unfold machine reference
  split
  · rename_i enabled
    simp only [enabled, ↓reduceIte] at h
    split
    · rename_i ending
      have out : InMachine (WidenedInsets.nativeEnd p b (rawValue m v.near) (rawValue m v.far)) := by
        simpa [source,enabled,ending] using h.2.2.2
      dsimp only
      rw [machine_end_refines _ _ _ _ h.1 h.2.1 ha hb out]
      rfl
    · rename_i ending
      have out : InMachine (WidenedInsets.nativeEnd p b (rawValue m v.far) (rawValue m v.near)) := by
        simpa [source,enabled,ending] using h.2.2.1
      dsimp only
      rw [machine_end_refines _ _ _ _ h.1 h.2.1 hb ha out]
      rfl
  · rfl

def ProviderBounds (m : Bool) (v : Insets) (p b : Int) : Prop :=
  (0 ≤ p ∧ p ≤ coordMax) ∧ (0 ≤ b ∧ b ≤ coordMax) ∧
  InCoordinate (rawValue m v.near) ∧ InCoordinate (rawValue m v.far)

theorem provider_bounds_supply_narrowing (m : Bool) (v : Insets) (p b : Int) (e : Bool)
    (h : ProviderBounds m v p b) : Safe m v p b e := by
  rcases h with ⟨hp,hb,hn,hf⟩
  have pn := coordinate_fits_machine _ hn
  have pf := coordinate_fits_machine _ hf
  have pp : InMachine p := by unfold InMachine machineMin machineMax coordMax at *; omega
  have pb : InMachine b := by unfold InMachine machineMin machineMax coordMax at *; omega
  refine ⟨pn,pf,?_⟩
  split
  · rename_i enabled
    refine ⟨pp,pb,?_⟩
    simp only [source,enabled,↓reduceIte]
    have hn' : WidenedInsets.InCoord (rawValue m v.near) := hn
    have hf' : WidenedInsets.InCoord (rawValue m v.far) := hf
    cases e
    · exact ⟨WidenedInsets.result_fits_storage _ _ _ _ hp hb hf' hn',pf⟩
    · exact ⟨pn,WidenedInsets.result_fits_storage _ _ _ _ hp hb hn' hf'⟩
  · trivial

theorem wide_negative_keeps_original :
    source true ⟨some (-1073741823),some (-1073741823)⟩ 6000 600 true =
      (-1073741823,-1073741823) ∧
    Safe true ⟨some (-1073741823),some (-1073741823)⟩ 6000 600 true := by
  decide +kernel

theorem storage_type_alone_insufficient :
    InMachine 2147483647 ∧
    ¬ InMachine (WidenedInsets.nativeEnd 0 2147483647 1073741823 0) := by
  decide +kernel

end WideNormalization
