import CorrectedWitness
namespace ShadowOrder
inductive CutFamily where
 | origin
 | layer
 | special
 deriving DecidableEq, Repr
structure CutAtom where
 family : CutFamily
 threshold : Int
 deriving DecidableEq, Repr
structure CutCoordinates where
 coreOrigin : Int
 normalPriority : Int
 author : Bool
 attached : Bool
 deriving DecidableEq, Repr
structure CutIntersection where
 origin : Option Int
 layer : Option Int
 special : Option Int
 deriving DecidableEq, Repr

def familyAllows (candidate : CutCoordinates) (family : CutFamily) (threshold : Int) : Bool :=
 match family with
 | .origin => candidate.coreOrigin < threshold
 | .layer => candidate.normalPriority < threshold
 | .special => if candidate.author then !candidate.attached else candidate.normalPriority < threshold

def optionalAllows (candidate : CutCoordinates) (family : CutFamily) (threshold : Option Int) : Bool :=
 (threshold.map (familyAllows candidate family)).getD true

def intersectThreshold (prior : Option Int) (next : Int) : Option Int :=
 some (prior.map (min next) |>.getD next)

def addCut (state : CutIntersection) (atom : CutAtom) : CutIntersection :=
 match atom.family with
 | .origin => {state with origin := intersectThreshold state.origin atom.threshold}
 | .layer => {state with layer := intersectThreshold state.layer atom.threshold}
 | .special => {state with special := intersectThreshold state.special atom.threshold}

def intersectionAllows (state : CutIntersection) (candidate : CutCoordinates) : Bool :=
 optionalAllows candidate .origin state.origin && optionalAllows candidate .layer state.layer &&
 optionalAllows candidate .special state.special

theorem family_min_intersection (candidate : CutCoordinates) (family : CutFamily) (a b : Int) :
 familyAllows candidate family (min a b) =
 (familyAllows candidate family a && familyAllows candidate family b) := by
 cases family <;> simp only [familyAllows]
 · apply Bool.eq_iff_iff.mpr
   simp only [decide_eq_true_eq,Bool.and_eq_true]
   omega
 · apply Bool.eq_iff_iff.mpr
   simp only [decide_eq_true_eq,Bool.and_eq_true]
   omega
 · cases candidate.author <;> simp
   apply Bool.eq_iff_iff.mpr
   simp only [decide_eq_true_eq,Bool.and_eq_true]
   omega

theorem optional_intersection (candidate : CutCoordinates) (family : CutFamily)
 (prior : Option Int) (next : Int) :
 optionalAllows candidate family (intersectThreshold prior next) =
 (optionalAllows candidate family prior && familyAllows candidate family next) := by
 cases prior with
 | none => simp [optionalAllows,intersectThreshold]
 | some prior => simp [optionalAllows,intersectThreshold,family_min_intersection,Bool.and_comm]

theorem add_cut_intersection (state : CutIntersection) (atom : CutAtom) (candidate : CutCoordinates) :
 intersectionAllows (addCut state atom) candidate =
 (intersectionAllows state candidate && familyAllows candidate atom.family atom.threshold) := by
 cases atom with
 | mk family threshold =>
   cases family <;> simp [addCut,intersectionAllows,optional_intersection,
     Bool.and_assoc,Bool.and_left_comm,Bool.and_comm]

theorem arbitrary_cutoff_intersection (cuts : List CutAtom) (state : CutIntersection)
 (candidate : CutCoordinates) :
 intersectionAllows (cuts.foldl addCut state) candidate =
 (intersectionAllows state candidate && cuts.all (fun atom => familyAllows candidate atom.family atom.threshold)) := by
 induction cuts generalizing state with
 | nil => simp
 | cons atom rest ih =>
   simp only [List.foldl_cons,ih,add_cut_intersection,List.all_cons]
   simp [Bool.and_assoc]

def coordinates (candidate : Priority) : CutCoordinates :=
 ⟨simpleOrigin candidate.origin,priorityKey (unimportantPriority candidate),
   candidate.origin == 3,candidate.layer == 65535⟩

def classifyCut (cut : Priority) (kind : RevertKind) : Option CutAtom :=
 match kind with
 | .origin => some ⟨.origin,simpleOrigin cut.origin⟩
 | .layer => some ⟨if cut.important && cut.layer == 65535 then .special else .layer,
     priorityKey (unimportantPriority cut)⟩
 | .rule => none

theorem classification_preserves_predicate (cut candidate : Priority) (kind : RevertKind) :
 ((classifyCut cut kind).map fun atom => familyAllows (coordinates candidate) atom.family atom.threshold).getD true =
 repairedAllows cut candidate kind := by
 cases kind with
 | origin => simp [classifyCut,familyAllows,coordinates,repairedAllows,nativeAllows]
 | rule => simp [classifyCut,repairedAllows,nativeAllows]
 | layer =>
   cases important : cut.important <;> by_cases layer : cut.layer = 65535 <;>
     by_cases author : candidate.origin = 3 <;>
     by_cases attached : candidate.layer = 65535 <;>
     simp [classifyCut,familyAllows,coordinates,repairedAllows,nativeAllows,important,layer,author,attached] <;> first | rfl | simp only [bne,Bool.not_not]


def retainMinimum (key : α → Int) (prior : Option α) (next : α) : Option α :=
 match prior with
 | none => some next
 | some old => if key next < key old then some next else some old

theorem retained_minimum_projection (key : α → Int) (prior : Option α) (next : α) :
 (retainMinimum key prior next).map key = intersectThreshold (prior.map key) (key next) := by
 cases prior with
 | none => rfl
 | some old =>
   by_cases order : key next < key old
   · simp only [retainMinimum,order,↓reduceIte,Option.map_some,intersectThreshold,Option.getD_some]
     congr 1
     omega
   · have reverse : key old ≤ key next := by omega
     simp only [retainMinimum,order,↓reduceIte,Option.map_some,intersectThreshold,Option.getD_some]
     congr 1
     omega

def classifiedCuts (cuts : List (Priority × RevertKind)) : List CutAtom :=
 cuts.filterMap fun cut => classifyCut cut.1 cut.2

theorem classified_conjunction (cuts : List (Priority × RevertKind)) (candidate : Priority) :
 (classifiedCuts cuts).all (fun atom => familyAllows (coordinates candidate) atom.family atom.threshold) =
 cuts.all (fun cut => repairedAllows cut.1 candidate cut.2) := by
 induction cuts with
 | nil => rfl
 | cons cut rest ih =>
   have bridge := classification_preserves_predicate cut.1 candidate cut.2
   cases classified : classifyCut cut.1 cut.2 with
   | none =>
     simp only [classified,Option.map_none,Option.getD_none] at bridge
     simp [classifiedCuts,classified,← bridge] at ih ⊢
     exact ih
   | some atom =>
     simp only [classified,Option.map_some,Option.getD_some] at bridge
     simp only [classifiedCuts,List.filterMap_cons,classified,List.all_cons]
     rw [bridge]
     exact congrArg (fun result => repairedAllows cut.1 candidate cut.2 && result) ih

theorem raw_cutoff_intersection (cuts : List (Priority × RevertKind))
 (candidate : Priority) :
 intersectionAllows ((classifiedCuts cuts).foldl addCut ⟨none,none,none⟩) (coordinates candidate) =
 cuts.all (fun cut => repairedAllows cut.1 candidate cut.2) := by
 rw [arbitrary_cutoff_intersection,classified_conjunction]
 simp [intersectionAllows,optionalAllows]

#print axioms arbitrary_cutoff_intersection
#print axioms classification_preserves_predicate
#print axioms retained_minimum_projection
#print axioms raw_cutoff_intersection
end ShadowOrder
