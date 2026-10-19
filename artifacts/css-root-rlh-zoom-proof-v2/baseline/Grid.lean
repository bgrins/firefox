import Model
namespace Rlh
structure ExactGrid where
  pixels : Rat
  appUnits : Int
  nonnegative : 0 ≤ appUnits
  bounded : appUnits ≤ 1048576
  exact : pixels * 60 = (appUnits : Rat)

def quantize (pixels : Rat) : Int := (pixels * 60 + 1/2).floor

theorem quantize_grid (g : ExactGrid) : quantize g.pixels = g.appUnits := by
  unfold quantize
  rw [g.exact, Rat.add_comm, Rat.floor_add_intCast]
  have h : ((1:Rat)/2).floor = 0 := by
    simp [Rat.div_def, Rat.inv_def, Rat.mul_def', Rat.floor_def, Rat.num_divInt, Rat.den_divInt, Rat.num_mkRat, Rat.den_mkRat, Int.sign]
  rw [h]
  simp

theorem appunit_roundtrip (g : ExactGrid) : (g.appUnits : Rat) / 60 = g.pixels := by
  rw [← g.exact, Rat.mul_div_cancel (by decide : (60:Rat) ≠ 0)]

structure Binary32Exact where
  value : Rat
  significand : Int
  exponent : Int
  significandBound : significand.natAbs < 16777216
  exponentLower : -126 ≤ exponent
  exponentUpper : exponent ≤ 100
  representation : value =
    if exponent ≥ 0 then (significand : Rat) * ((2^exponent.toNat : Nat) : Rat)
    else (significand : Rat) / ((2^(-exponent).toNat : Nat) : Rat)

structure ExactProvider (o : Owner) where
  zoom : Zoom o
  font : Rat
  form : Form
  unscaled : Binary32Exact
  scaled : Binary32Exact
  grid : ExactGrid
  semantic : unscaled.value = semanticLine font form
  scaling : scaled.value = unscaled.value * zoom.value
  appUnitInput : grid.pixels = scaled.value

def ExactProvider.appUnits {o} (p : ExactProvider o) : AppUnits o := ⟨quantize p.grid.pixels⟩

def ExactProvider.toProvider {o} (p : ExactProvider o) : Provider o :=
  ⟨p.font,p.form,⟨(p.appUnits.value : Rat) / 60⟩⟩

theorem exact_provider_valid {o} (p : ExactProvider o) :
    p.toProvider.Valid p.zoom := by
  unfold ExactProvider.toProvider ExactProvider.appUnits Provider.Valid
  rw [quantize_grid, appunit_roundtrip, p.appUnitInput, p.scaling, p.semantic]

theorem absolute_grid_provider {o} (p : ExactProvider o) (length : Rat)
    (h : p.form = .absolute length) : p.toProvider.stored.value = length * p.zoom.value := by
  have hv := exact_provider_valid p
  simpa [Provider.Valid, ExactProvider.toProvider, h, semanticLine] using hv

theorem numeric_grid_provider {o} (p : ExactProvider o) (factor : Rat)
    (h : p.form = .numeric factor) : p.toProvider.stored.value = p.font * factor * p.zoom.value := by
  have hv := exact_provider_valid p
  simpa [Provider.Valid, ExactProvider.toProvider, h, semanticLine] using hv

theorem percentage_grid_provider {o} (p : ExactProvider o) (percent : Rat)
    (h : p.form = .percentageComputed percent) : p.toProvider.stored.value = p.font * percent * p.zoom.value := by
  have hv := exact_provider_valid p
  simpa [Provider.Valid, ExactProvider.toProvider, h, semanticLine] using hv

structure ExactRead (o : Owner) where
  zoom : Zoom o
  input : Binary32Exact
  coefficient : Binary32Exact
  product : Binary32Exact
  productCorrect : product.value = input.value * coefficient.value
  exposed : Binary32Exact
  exposedCorrect : exposed.value = product.value / zoom.value

theorem exact_coefficient_observation {o} (r : ExactRead o) :
    r.exposed.value = (r.input.value * r.coefficient.value) / r.zoom.value := by
  rw [r.exposedCorrect, r.productCorrect]

def grid20 : ExactGrid := ⟨20,1200,by decide,by decide,by
  change ((20:Int):Rat)*((60:Int):Rat)=((1200:Int):Rat)
  rw [← Rat.intCast_mul]
  rfl⟩
theorem grid20_quantized : quantize grid20.pixels = 1200 := quantize_grid grid20
def half : Binary32Exact := ⟨1/2,1,-1,by decide,by decide,by decide,by simp⟩
theorem fractional_coefficient_exists : half.value = 1/2 := rfl
structure ProviderIndependentValid (w : World) : Prop where
  transport : w.parentZoom.value * w.inheritanceZoom = w.consumerZoom.value
  initial : w.initialStored.value = semanticLine w.initialFont w.initialForm
  cache : w.cache.value = w.rootSemantic
  rootOwner : w.role = .root → w.consumer = w.root
  sameDocument : w.consumer.document = w.root.document
  parentDocument : w.parent.document = w.consumer.document
  initialDocument : w.initial.document = w.consumer.document

theorem exact_grid_world_refinement (w : World)
    (current : ExactProvider w.consumer) (parent : ExactProvider w.parent)
    (hc : w.current = current.toProvider) (hp : w.inherited = parent.toProvider)
    (hcz : w.consumerZoom = current.zoom) (hpz : w.parentZoom = parent.zoom)
    (h : ProviderIndependentValid w) : implementation w = reference w := by
  apply candidate_refines_reference
  refine ⟨?_,?_,h.transport,h.initial,h.cache,h.rootOwner,h.sameDocument,
    h.parentDocument,h.initialDocument⟩
  · rw [hc,hcz]; exact exact_provider_valid current
  · rw [hp,hpz]; exact exact_provider_valid parent
end Rlh
