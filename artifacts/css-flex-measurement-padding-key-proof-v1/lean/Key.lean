import Std
namespace MeasurementPadding

structure Size where
  inlineSize : Int
  blockSize : Int
  deriving DecidableEq, Repr, BEq
structure Margin where
  inlineStart : Int
  inlineEnd : Int
  blockStart : Int
  blockEnd : Int
  deriving DecidableEq, Repr, BEq
structure Input where
  computed : Size
  minimumBlock : Int
  maximumBlock : Int
  availableBlock : Int
  borderPadding : Margin
  deriving DecidableEq, Repr
structure OldKey where
  computed : Size
  minimumBlock : Int
  maximumBlock : Int
  availableBlock : Int
  deriving DecidableEq, Repr, BEq
structure Key where
  original : OldKey
  borderPadding : Margin
  deriving DecidableEq, Repr, BEq

def oldKey (input : Input) : OldKey :=
  ⟨input.computed,input.minimumBlock,input.maximumBlock,input.availableBlock⟩
def key (input : Input) : Key := ⟨oldKey input,input.borderPadding⟩
def oldAccepts (cached current : Input) : Bool := decide (oldKey cached = oldKey current)
def accepts (cached current : Input) : Bool := decide (key cached = key current)

def OriginalInputsAgree (cached current : Input) : Prop :=
  cached.computed.inlineSize = current.computed.inlineSize ∧
  cached.computed.blockSize = current.computed.blockSize ∧
  cached.minimumBlock = current.minimumBlock ∧
  cached.maximumBlock = current.maximumBlock ∧
  cached.availableBlock = current.availableBlock

def PaddingInputsAgree (cached current : Input) : Prop :=
  cached.borderPadding.inlineStart = current.borderPadding.inlineStart ∧
  cached.borderPadding.inlineEnd = current.borderPadding.inlineEnd ∧
  cached.borderPadding.blockStart = current.borderPadding.blockStart ∧
  cached.borderPadding.blockEnd = current.borderPadding.blockEnd

theorem old_predicate_matches_independent_inputs (cached current : Input) :
    oldAccepts cached current = true ↔ OriginalInputsAgree cached current := by
  rcases cached with ⟨⟨ci,cb⟩,cmin,cmax,ca,cp⟩
  rcases current with ⟨⟨ni,nb⟩,nmin,nmax,na,np⟩
  simp [oldAccepts,oldKey,OriginalInputsAgree,OldKey.mk.injEq,Size.mk.injEq,and_assoc]

theorem candidate_matches_all_independent_inputs (cached current : Input) :
    accepts cached current = true ↔ OriginalInputsAgree cached current ∧ PaddingInputsAgree cached current := by
  rcases cached with ⟨⟨ci,cb⟩,cmin,cmax,ca,⟨cis,cie,cbs,cbe⟩⟩
  rcases current with ⟨⟨ni,nb⟩,nmin,nmax,na,⟨nis,nie,nbs,nbe⟩⟩
  simp [accepts,key,oldKey,OriginalInputsAgree,PaddingInputsAgree,Key.mk.injEq,
    OldKey.mk.injEq,Size.mk.injEq,Margin.mk.injEq,and_assoc]

theorem candidate_rejects_only_original_mismatch_or_padding (cached current : Input) :
    accepts cached current = (oldAccepts cached current && decide (cached.borderPadding = current.borderPadding)) := by
  simp [accepts,key,oldAccepts,Key.mk.injEq]

theorem accepted_key_derives_all_four_components (cached current : Input)
    (accepted : accepts cached current = true) : PaddingInputsAgree cached current :=
  ((candidate_matches_all_independent_inputs cached current).1 accepted).2

theorem unchanged_padding_preserves_original_decision (cached current : Input)
    (same : cached.borderPadding = current.borderPadding) :
    accepts cached current = oldAccepts cached current := by
  simp [candidate_rejects_only_original_mismatch_or_padding,same]

theorem original_rejection_remains_rejection (cached current : Input)
    (rejected : oldAccepts cached current = false) : accepts cached current = false := by
  simp [candidate_rejects_only_original_mismatch_or_padding,rejected]

theorem differing_padding_rejected (cached current : Input)
    (different : cached.borderPadding ≠ current.borderPadding) : accepts cached current = false := by
  simp [candidate_rejects_only_original_mismatch_or_padding,different]

def mayReuse (dirty cachedPresent : Bool) (cached current : Input) : Bool :=
  cachedPresent && !dirty && accepts cached current

theorem reached_reuse_derives_guards_and_key (dirty present : Bool) (cached current : Input)
    (reuse : mayReuse dirty present cached current = true) :
    dirty = false ∧ present = true ∧ OriginalInputsAgree cached current ∧ PaddingInputsAgree cached current := by
  simp only [mayReuse,Bool.and_eq_true,Bool.not_eq_true'] at reuse
  exact ⟨reuse.1.2,reuse.1.1,(candidate_matches_all_independent_inputs cached current).1 reuse.2⟩

end MeasurementPadding
