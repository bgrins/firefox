import MapIdentity
namespace ConstructorIdentity
open AnimationIdentity SegmentIdentity MapIdentity
variable {ι ν σ : Type} [DecidableEq ι]
structure Storage (ι σ : Type) where
  declarations : List (Value ι σ)
  membership : List ι
  importance : List Bool
  mutable : Bool

def pushEntry (uncompute : Value ι ν → Value ι σ) (s : Storage ι σ) (entry : ι × Value ι ν) : Storage ι σ :=
  {s with declarations := s.declarations ++ [uncompute entry.2], membership := entry.1::s.membership}

def build (uncompute : Value ι ν → Value ι σ) (xs : Entries ι ν) : Storage ι σ :=
  let state := xs.foldl (pushEntry uncompute) ⟨[],[],[],true⟩
  {state with importance := List.replicate xs.length false}

def Valid (s : Storage ι σ) : Prop :=
  (s.declarations.map Value.id).Nodup ∧
  s.importance.length=s.declarations.length ∧
  (∀ key, key∈s.membership ↔ key∈s.declarations.map Value.id) ∧
  (∀ bit∈s.importance, bit=false) ∧ s.mutable=true

variable {arith : Arithmetic ι ν}
variable {uncompute : Value ι ν → Value ι σ}
theorem loop_storage (xs : Entries ι ν) (s : Storage ι σ) :
    xs.foldl (pushEntry uncompute) s =
      ⟨s.declarations ++ xs.map (fun p => uncompute p.2),
       (xs.map Prod.fst).reverse ++ s.membership,s.importance,s.mutable⟩ := by
  induction xs generalizing s with
  | nil => simp
  | cons p rest ih =>
    rw [List.foldl_cons,ih]
    simp [pushEntry,List.append_assoc]

theorem constructor_fields (xs : Entries ι ν) :
    build uncompute xs =
      ⟨xs.map (fun p => uncompute p.2),(xs.map Prod.fst).reverse,List.replicate xs.length false,true⟩ := by
  simp [build,loop_storage]

theorem constructor_ids (xs : Entries ι ν) (hc : Coherent xs)
    (hi : ∀ v, (uncompute v).id=v.id) :
    ((build uncompute xs).declarations.map Value.id)=xs.map Prod.fst := by
  rw [constructor_fields]
  simp only [List.map_map]
  apply List.map_congr_left
  intro ⟨k,v⟩ hm
  exact (hi v).trans (hc k v hm)

theorem constructor_representation (xs : Entries ι ν) (hc : Coherent xs) (hu : Unique xs)
    (hi : ∀ v, (uncompute v).id=v.id) : Valid (build uncompute xs) := by
  have ids := constructor_ids xs hc hi
  unfold Valid
  refine ⟨?_,?_,?_,?_,?_⟩
  · rw [ids];exact hu
  · simp [constructor_fields]
  · intro key;rw [ids];simp [constructor_fields]
  · simp [constructor_fields]
  · simp [constructor_fields]

theorem map_history_constructor (actions : List (Action ι ν)) (hp : Preserves arith)
    (ha : ∀ a∈actions, ActionId a) (hi : ∀ v, (uncompute v).id=v.id) :
    ∃ xs, run arith [] actions=some xs ∧ Valid (build uncompute xs) ∧
      (build uncompute xs).declarations.map Value.id=xs.map Prod.fst := by
  obtain ⟨xs,hx,hc,hu⟩ := from_empty actions hp ha
  exact ⟨xs,hx,constructor_representation xs hc hu hi,constructor_ids xs hc hi⟩
end ConstructorIdentity
