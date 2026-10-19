import CutoffIntersection
namespace ShadowOrder
structure RevertRepresentatives where
 origin : Option Priority
 layer : Option Priority
 special : Option Priority
 deriving DecidableEq, Repr

def specialCut (p : Priority) : Bool := p.important && p.layer == 65535

def coreKey (p : Priority) : Int := simpleOrigin p.origin

def normalKey (p : Priority) : Int := priorityKey (unimportantPriority p)

def representativeAdd (s : RevertRepresentatives) (cut : Priority × RevertKind) : RevertRepresentatives :=
 match cut.2 with
 | .rule => s
 | .origin => {s with origin := retainMinimum coreKey s.origin cut.1}
 | .layer => if specialCut cut.1 then
     {s with special := retainMinimum normalKey s.special cut.1}
   else {s with layer := retainMinimum normalKey s.layer cut.1}

def representativeProjection (s : RevertRepresentatives) : CutIntersection :=
 ⟨s.origin.map coreKey,s.layer.map normalKey,s.special.map normalKey⟩

def representativeAllows (s : RevertRepresentatives) (p : Priority) : Bool :=
 (s.origin.map (fun cut => repairedAllows cut p .origin)).getD true &&
 (s.layer.map (fun cut => repairedAllows cut p .layer)).getD true &&
 (s.special.map (fun cut => repairedAllows cut p .layer)).getD true

def representativeValid (s : RevertRepresentatives) : Prop :=
 (∀ p ∈ s.layer, specialCut p = false) ∧ (∀ p ∈ s.special, specialCut p = true)

theorem retained_minimum_preserves (key : α → Int) (prior : Option α) (next : α)
 (P : α → Prop) (old : ∀ p ∈ prior, P p) (fresh : P next) :
 ∀ p ∈ retainMinimum key prior next, P p := by
 cases prior with
 | none => simpa [retainMinimum] using fresh
 | some prior =>
   by_cases order : key next < key prior
   · simpa [retainMinimum,order] using fresh
   · simpa [retainMinimum,order] using old prior (by simp)

theorem representative_add_valid (s : RevertRepresentatives) (cut : Priority × RevertKind)
 (valid : representativeValid s) : representativeValid (representativeAdd s cut) := by
 rcases valid with ⟨ordinary,special⟩
 cases kind : cut.2 with
 | rule => simpa [representativeAdd,kind,representativeValid] using And.intro ordinary special
 | origin => simpa [representativeAdd,kind,representativeValid] using And.intro ordinary special
 | layer =>
   cases branch : specialCut cut.1 with
   | false =>
     simp only [representativeValid,representativeAdd,kind,branch,Bool.false_eq_true,↓reduceIte]
     exact ⟨retained_minimum_preserves normalKey s.layer cut.1 _ ordinary branch,special⟩
   | true =>
     simp only [representativeValid,representativeAdd,kind,branch,↓reduceIte]
     exact ⟨ordinary,retained_minimum_preserves normalKey s.special cut.1 _ special branch⟩

theorem classify_layer (cut : Priority) : classifyCut cut .layer =
 some ⟨if specialCut cut then .special else .layer,normalKey cut⟩ := rfl

theorem representative_add_projection (s : RevertRepresentatives) (cut : Priority × RevertKind) :
 representativeProjection (representativeAdd s cut) =
 ((classifyCut cut.1 cut.2).map (addCut (representativeProjection s))).getD (representativeProjection s) := by
 cases kind : cut.2 with
 | rule => simp [representativeAdd,classifyCut,kind]
 | origin => simp [representativeAdd,classifyCut,kind,representativeProjection,
     retained_minimum_projection,addCut,coreKey]
 | layer =>
   cases branch : specialCut cut.1 <;>
     simp [representativeAdd,kind,classify_layer,representativeProjection,
       retained_minimum_projection,addCut,branch,normalKey]

theorem ordinary_representative_predicate (cut p : Priority) (ordinary : specialCut cut = false) :
 repairedAllows cut p .layer = familyAllows (coordinates p) .layer (normalKey cut) := by
 have h := classification_preserves_predicate cut p .layer
 simpa [classify_layer,ordinary,normalKey] using h.symm

theorem special_representative_predicate (cut p : Priority) (special : specialCut cut = true) :
 repairedAllows cut p .layer = familyAllows (coordinates p) .special (normalKey cut) := by
 have h := classification_preserves_predicate cut p .layer
 simpa [classify_layer,special,normalKey] using h.symm

theorem representative_predicate_projection (s : RevertRepresentatives) (p : Priority)
 (valid : representativeValid s) :
 representativeAllows s p = intersectionAllows (representativeProjection s) (coordinates p) := by
 rcases s with ⟨origin,layer,special⟩
 rcases valid with ⟨ordinary,specialValid⟩
 have originEq : (origin.map (fun cut => repairedAllows cut p .origin)).getD true =
   optionalAllows (coordinates p) .origin (origin.map coreKey) := by
   cases origin <;> simp [optionalAllows,repairedAllows,nativeAllows,familyAllows,coordinates,coreKey]
 have layerEq : (layer.map (fun cut => repairedAllows cut p .layer)).getD true =
   optionalAllows (coordinates p) .layer (layer.map normalKey) := by
   cases layer with
   | none => rfl
   | some cut => exact ordinary_representative_predicate cut p (ordinary cut (by simp))
 have specialEq : (special.map (fun cut => repairedAllows cut p .layer)).getD true =
   optionalAllows (coordinates p) .special (special.map normalKey) := by
   cases special with
   | none => rfl
   | some cut => exact special_representative_predicate cut p (specialValid cut (by simp))
 simp only [representativeAllows,representativeProjection,intersectionAllows]
 rw [originEq,layerEq,specialEq]

theorem representative_step_intersection (s : RevertRepresentatives)
 (cut : Priority × RevertKind) (p : Priority) (valid : representativeValid s) :
 representativeAllows (representativeAdd s cut) p =
 (representativeAllows s p && repairedAllows cut.1 p cut.2) := by
 rw [representative_predicate_projection _ _ (representative_add_valid s cut valid),
   representative_add_projection,representative_predicate_projection s p valid]
 have bridge := classification_preserves_predicate cut.1 p cut.2
 cases classified : classifyCut cut.1 cut.2 with
 | none => simp [classified] at bridge ⊢; simp [← bridge]
 | some atom => simp only [classified,Option.map_some,Option.getD_some] at bridge ⊢
                rw [add_cut_intersection,bridge]

theorem representative_fold_intersection (cuts : List (Priority × RevertKind))
 (s : RevertRepresentatives) (p : Priority) (valid : representativeValid s) :
 representativeAllows (cuts.foldl representativeAdd s) p =
 (representativeAllows s p && cuts.all (fun cut => repairedAllows cut.1 p cut.2)) := by
 induction cuts generalizing s with
 | nil => simp
 | cons cut rest ih =>
   rw [List.foldl_cons,ih _ (representative_add_valid s cut valid),
     representative_step_intersection s cut p valid]
   simp [Bool.and_assoc]

theorem empty_representatives_valid : representativeValid ⟨none,none,none⟩ := by
 simp [representativeValid]

theorem exact_representative_fold (cuts : List (Priority × RevertKind)) (p : Priority) :
 representativeAllows (cuts.foldl representativeAdd ⟨none,none,none⟩) p =
 cuts.all (fun cut => repairedAllows cut.1 p cut.2) := by
 rw [representative_fold_intersection cuts _ p empty_representatives_valid]
 simp [representativeAllows]

#print axioms exact_representative_fold
end ShadowOrder
