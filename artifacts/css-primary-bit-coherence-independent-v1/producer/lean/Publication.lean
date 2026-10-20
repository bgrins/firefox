import PrimaryBit

namespace PrimaryBit

structure World where
  frames : State
  rememberedB : Content → Option Int
  rememberedI : Content → Option Int
  observed : Content → Bool
  animationUpdate : Bool

def removeRememberedB (w : World) (c : Content) : World :=
  { w with rememberedB := fun x => if x = c then none else w.rememberedB x }

def removeRememberedI (w : World) (c : Content) : World :=
  { w with rememberedI := fun x => if x = c then none else w.rememberedI x }

def unobserve (w : World) (c : Content) : World :=
  { w with observed := fun x => if x = c then false else w.observed x }

def ordinaryInit (w : World) (c : Content) : World :=
  unobserve (removeRememberedI (removeRememberedB
    { w with animationUpdate := true } c) c) c

theorem ordinary_init_projection (w : World) (c : Content) :
    (ordinaryInit w c).frames = w.frames := rfl

theorem ordinary_init_side_effects (w : World) (c : Content) :
    (ordinaryInit w c).rememberedB c = none ∧
    (ordinaryInit w c).rememberedI c = none ∧
    (ordinaryInit w c).observed c = false ∧
    (ordinaryInit w c).animationUpdate = true := by
  simp [ordinaryInit, unobserve, removeRememberedB, removeRememberedI]

def beginOwn (w : World) (f : Frame) : World :=
  { w with frames := writeBit w.frames f true }

def completeOwn (w : World) (c : Content) (f : Frame) : World :=
  { w with frames := publish w.frames c (some f) }

def ownProtocol (w : World) (c : Content) (f : Frame) : World :=
  let started := beginOwn w f
  let initialized := if w.frames.bit f then started else ordinaryInit started c
  completeOwn initialized c f

theorem own_protocol_is_setter (l : Layout) (w : World) (c : Content) (f : Frame)
    (owner : l.owner f = c) :
    (ownProtocol w c f).frames = setPrimary l w.frames c (some f) := by
  simp only [ownProtocol]
  split <;> simp [completeOwn, beginOwn, ordinaryInit, unobserve,
    removeRememberedI, removeRememberedB, setPrimary, beginSet, owner]

theorem own_protocol_stable (l : Layout) (w : World) (c : Content) (f : Frame)
    (coherent : Coherent l w.frames) (owner : l.owner f = c)
    (replace : w.frames.pointer c = none ∨ w.frames.pointer c = some f) :
    Coherent l (ownProtocol w c f).frames := by
  rw [own_protocol_is_setter l w c f owner]
  exact own_set_preserves l w.frames c f coherent owner replace

theorem own_same_skips_init (l : Layout) (w : World) (c : Content) (f : Frame)
    (coherent : Coherent l w.frames) (owner : l.owner f = c)
    (same : w.frames.pointer c = some f) :
    (ownProtocol w c f).rememberedB = w.rememberedB ∧
    (ownProtocol w c f).rememberedI = w.rememberedI ∧
    (ownProtocol w c f).observed = w.observed := by
  have bit : w.frames.bit f = true := by rw [coherent f, owner, same]; simp
  simp [ownProtocol, bit, completeOwn, beginOwn]

theorem publication_gap (l : Layout) (w : World) (c : Content) (f : Frame)
    (owner : l.owner f = c) (fresh : w.frames.pointer c = none) :
    (beginOwn w f).frames.bit f = true ∧
    (beginOwn w f).frames.pointer (l.owner f) = none ∧
    ¬ Coherent l (beginOwn w f).frames := by
  have b : (beginOwn w f).frames.bit f = true := by simp [beginOwn, writeBit]
  have p : (beginOwn w f).frames.pointer (l.owner f) = none := by
    simpa [beginOwn, writeBit, owner] using fresh
  refine ⟨b, p, ?_⟩
  intro h
  have := h f
  simp [b, p] at this

def CallbackFrame (before after : World) : Prop := after.frames = before.frames

theorem callback_then_publish (l : Layout) (w after : World) (c : Content) (f : Frame)
    (coherent : Coherent l w.frames) (owner : l.owner f = c)
    (replace : w.frames.pointer c = none ∨ w.frames.pointer c = some f)
    (callback : CallbackFrame (beginOwn w f) after) :
    Coherent l (completeOwn after c f).frames := by
  change Coherent l (publish after.frames c (some f))
  rw [callback]
  have result := own_set_preserves l w.frames c f coherent owner replace
  simpa [setPrimary, beginSet, owner, beginOwn] using result

theorem read_after_preserving_callback (l : Layout) (w after : World) (f : Frame)
    (coherent : Coherent l w.frames) (callback : CallbackFrame w after) :
    nativeDestroyRead l after.frames f = pointerDestroyRead l after.frames f := by
  rw [callback]
  exact destroy_read_agrees l w.frames f coherent

def areaRemoved (l : Layout) (s : State) (c : Content) (image : Frame) : State :=
  if s.pointer c = some image then setPrimary l s c none else s

theorem stale_image_removal_noop (l : Layout) (s : State) (c : Content)
    (oldImage currentImage : Frame) (different : oldImage ≠ currentImage)
    (current : s.pointer c = some currentImage) :
    areaRemoved l s c oldImage = s := by
  simp [areaRemoved, current, Ne.symm different]

theorem alias_does_not_mark_target (l : Layout) (s : State) (c : Content) (image : Frame)
    (area : l.area c = true) (foreignOwner : l.owner image ≠ c) :
    (setPrimary l s c (some image)).bit = s.bit := by
  simp [setPrimary, beginSet, area, foreignOwner, publish]

end PrimaryBit
