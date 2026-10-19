import Std
namespace ReplacedStretch

inductive Size where
  | auto | maxContent | minContent | fitContent | definite
  deriving DecidableEq
inductive Alignment where
  | stretch | normal | start
  deriving DecidableEq

structure Context where
  grid : Bool
  masonry : Bool
  definiteCB : Bool
  startAuto : Bool
  endAuto : Bool
  clamp : Bool
  alignment : Alignment
  deriving DecidableEq

structure Selection where
  stretch : Bool
  fillAvailable : Bool
  clamp : Bool
  explicitSize : Bool
  deriving DecidableEq

def natural (s : Size) : Bool := s == .auto || s == .maxContent

def native (s : Size) (c : Context) : Selection :=
  if !natural s then ⟨false, false, c.clamp, true⟩
  else if c.grid && !c.masonry then
    if c.definiteCB then
      let stretch := !c.startAuto && !c.endAuto && s == .auto && c.alignment == .stretch
      ⟨stretch, stretch || c.clamp, c.clamp, false⟩
    else ⟨false, false, false, false⟩
  else ⟨false, false, c.clamp, false⟩

def applicable (c : Context) : Prop :=
  c.grid = true ∧ c.masonry = false ∧ c.definiteCB = true

def selfStretch (s : Size) (c : Context) : Prop :=
  s = .auto ∧ c.alignment = .stretch ∧ c.startAuto = false ∧
  c.endAuto = false ∧ applicable c

instance (c : Context) : Decidable (applicable c) := inferInstanceAs (Decidable (_ ∧ _))
instance (s : Size) (c : Context) : Decidable (selfStretch s c) := inferInstanceAs (Decidable (_ ∧ _))

def spec (s : Size) (c : Context) : Selection :=
  ⟨decide (selfStretch s c),
   decide (selfStretch s c ∨ (s = .auto ∨ s = .maxContent) ∧ applicable c ∧ c.clamp = true),
   decide (c.clamp = true ∧ ¬ ((s = .auto ∨ s = .maxContent) ∧ c.grid = true ∧ c.masonry = false ∧ c.definiteCB = false)),
   decide (s ≠ .auto ∧ s ≠ .maxContent)⟩

theorem selection_refinement (s : Size) (c : Context) : native s c = spec s c := by
  cases c with | mk g m d a b k l =>
    cases s <;> cases g <;> cases m <;> cases d <;> cases a <;> cases b <;>
      cases k <;> cases l <;> decide

theorem stretch_iff (s : Size) (c : Context) :
    (native s c).stretch = true ↔ selfStretch s c := by
  rw [selection_refinement]
  simp [spec]

theorem nonauto_no_self_stretch (s : Size) (c : Context) (h : s ≠ .auto) :
    (native s c).stretch = false := by
  rw [selection_refinement]
  simp [spec, selfStretch, h]

theorem maxcontent_no_self_stretch (c : Context) :
    (native .maxContent c).stretch = false := by
  exact nonauto_no_self_stretch _ c (by decide)

theorem margins_disable (s : Size) (c : Context)
    (h : c.startAuto = true ∨ c.endAuto = true) : (native s c).stretch = false := by
  rw [selection_refinement]
  rcases h with h | h <;> simp [spec, selfStretch, h]

def oldNative (s : Size) (c : Context) : Selection :=
  if !natural s then ⟨false, false, c.clamp, true⟩
  else if c.grid && !c.masonry then
    if c.definiteCB then
      let stretch := !c.startAuto && !c.endAuto && c.alignment == .stretch
      ⟨stretch, stretch || c.clamp, c.clamp, false⟩
    else ⟨false, false, false, false⟩
  else ⟨false, false, c.clamp, false⟩

theorem auto_preserved (c : Context) : native .auto c = oldNative .auto c := by
  simp [native, oldNative]

theorem other_sizes_preserved (s : Size) (c : Context) (h : s ≠ .maxContent) :
    native s c = oldNative s c := by
  cases s <;> simp_all [native, oldNative, natural]

theorem clamp_flag_preserved (s : Size) (c : Context) :
    (native s c).clamp = (oldNative s c).clamp := by
  cases c with | mk g m d a b k l =>
    cases s <;> cases g <;> cases m <;> cases d <;> cases a <;> cases b <;>
      cases k <;> cases l <;> decide

theorem clamping_has_fill (s : Size) (c : Context) (h : natural s = true)
    (ha : applicable c) (hk : c.clamp = true) :
    (native s c).fillAvailable = true := by
  obtain ⟨hg, hm, hd⟩ := ha
  simp [native, h, hg, hm, hd, hk]

def witness : Context := ⟨true, false, true, false, false, false, .stretch⟩

theorem old_counterexample :
    (oldNative .maxContent witness).stretch = true ∧
    ¬ selfStretch .maxContent witness := by decide

theorem fixed_witness : native .maxContent witness = ⟨false, false, false, false⟩ := by decide

theorem auto_witness : native .auto witness = ⟨true, true, false, false⟩ := by decide

#print axioms selection_refinement
#print axioms stretch_iff
#print axioms nonauto_no_self_stretch
#print axioms maxcontent_no_self_stretch
#print axioms margins_disable
#print axioms auto_preserved
#print axioms other_sizes_preserved
#print axioms clamp_flag_preserved
#print axioms clamping_has_fill
#print axioms old_counterexample
#print axioms fixed_witness
#print axioms auto_witness
end ReplacedStretch
