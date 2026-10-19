import Trace
import Grid
namespace Rlh

def rootOwner (epoch : Nat) : Owner := ⟨1,10,⟨epoch⟩⟩
def parentOwner (epoch : Nat) : Owner := ⟨1,11,⟨epoch⟩⟩
def initialOwner : Owner := ⟨1,0,0⟩
def zTwo (o : Owner) : Zoom o := ⟨2,by decide,by decide⟩
def zOne (o : Owner) : Zoom o := ⟨1,by decide,by decide⟩
def sample (role : Role) (base : Base) (form : Form) (epoch : Nat) : World :=
  let consumer := if role = .root then rootOwner epoch else ⟨1,20,⟨epoch⟩⟩
  {consumer,parent := parentOwner epoch,root := rootOwner epoch,initial := initialOwner,
   consumerZoom := zTwo consumer,parentZoom := zOne (parentOwner epoch),inheritanceZoom := 2,
   current := ⟨16,form,⟨semanticLine 16 form * 2⟩⟩,
   inherited := ⟨20,.absolute 24,⟨24*1⟩⟩,
   initialFont := 16,initialForm := .absolute 19,initialStored := ⟨19⟩,
   rootSemantic := semanticLine 16 form,cache := ⟨semanticLine 16 form⟩,
   role,base,coefficient := ⟨1/2⟩}

theorem sample_valid (r : Role) (b : Base) (f : Form) (e : Nat) : Valid (sample r b f e) := by
  refine ⟨rfl,rfl,?_,rfl,rfl,?_,?_,?_,?_⟩
  · simp [sample,zOne,zTwo,Rat.one_mul]
  · intro hr; change r = .root at hr; simp [sample,hr]
  · cases r <;> rfl
  · cases r <;> rfl
  · cases r <;> rfl

def sampleRoot (form : Form) (epoch : Nat) : RootRecord :=
  ⟨rootOwner epoch,zTwo (rootOwner epoch),⟨16,form,⟨semanticLine 16 form * 2⟩⟩,rfl⟩
def sampleRequest (r : Role) (b : Base) (f : Form) (e : Nat) : Request :=
  ⟨sample r b f e,sample_valid r b f e⟩

theorem published_sample_admitted (r : Role) (b : Base) (f : Form) (e : Nat) :
    requestAdmitted (publishReference (initial (sampleRoot f e))) (sampleRequest r b f e) := by
  refine ⟨rfl,rfl,?_,?_,?_⟩
  · intro _; rfl
  · intro _; rfl
  · intro _ _; rfl

theorem root_before_publication (b : Base) (f : Form) (e : Nat) :
    requestAdmitted (initial (sampleRoot f e)) (sampleRequest .root b f e) := by
  refine ⟨rfl,rfl,?_,?_,?_⟩
  · intro h; cases h
  · intro _; rfl
  · intro _ _; rfl

def refreshTrace : List Event :=
  [.read (sampleRequest .root .inherited (.absolute 20) 1),
   .publish,.read (sampleRequest .descendant .current (.absolute 20) 1),
   .foreignUpdate ⟨2,10,7⟩,
   .update (sampleRoot (.numeric (5/4)) 2),.publish,
   .read (sampleRequest .descendant .inherited (.numeric (5/4)) 2),
   .read (sampleRequest .media .current (.numeric (5/4)) 2)]

theorem refresh_trace_admitted : admittedTrace (initial (sampleRoot (.absolute 20) 1)) refreshTrace := by
  unfold refreshTrace
  simp only [admittedTrace]
  refine ⟨root_before_publication _ _ _,?_,?_,?_,?_,?_,?_,?_,trivial⟩
  · trivial
  · exact published_sample_admitted _ _ _ _
  · change (2:DocumentId) ≠ 1; decide
  · trivial
  · trivial
  · exact published_sample_admitted _ _ _ _
  · exact published_sample_admitted _ _ _ _

theorem concrete_refresh_refines :
    runNative (initial (sampleRoot (.absolute 20) 1)) refreshTrace =
    runReference (initial (sampleRoot (.absolute 20) 1)) refreshTrace :=
  finite_sequence_refinement _ _ (initial_invariant _) refresh_trace_admitted

theorem stale_read_rejected (r : RootRecord) (q : Request) (h : q.world.role = .descendant) :
    ¬ requestAdmitted (initial r) q := by
  intro a
  have bad := a.2.2.1 h
  cases bad

theorem wrong_version_rejected (s : State) (q : Request) (h : q.world.root.epoch ≠ s.root.owner.epoch) :
    ¬ requestAdmitted s q := by
  intro a
  exact h (congrArg Owner.epoch a.1)
theorem zero_zoom_excluded {o} (z : Zoom o) : z.value ≠ 0 := z.nonzero
theorem negative_zoom_excluded {o} (z : Zoom o) : ¬ z.value ≤ 0 := Rat.not_le.mpr z.positive
end Rlh
