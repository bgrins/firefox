import Std
set_option autoImplicit false

namespace SigmaContext

structure Properties where
  cased : Bool
  ignorable : Bool
  deriving DecidableEq

def scan : List Properties → Bool
  | [] => false
  | p :: ps => if p.ignorable then scan ps else p.cased

def specified (xs : List Properties) : Bool :=
  ((xs.dropWhile (fun p => p.ignorable)).head?).any (fun p => p.cased)

theorem scan_eq_specified (xs : List Properties) : scan xs = specified xs := by
  induction xs with
  | nil => rfl
  | cons p ps ih =>
    cases h : p.ignorable <;> simp [scan, specified, List.dropWhile, h] at *
    exact ih

def finalSigma (before after : List Properties) : Bool :=
  scan before.reverse && !scan after

def specifiedFinalSigma (before after : List Properties) : Bool :=
  specified before.reverse && !specified after

theorem finalSigma_eq_specified (before after : List Properties) :
    finalSigma before after = specifiedFinalSigma before after := by
  simp [finalSigma, specifiedFinalSigma, scan_eq_specified]

theorem ignorable_invariance (p : Properties) (rest : List Properties)
    (h : p.ignorable = true) : scan (p :: rest) = scan rest := by
  simp [scan, h]

theorem overlap_without_base :
    finalSigma [{ cased := true, ignorable := true }] [] = false := rfl

theorem overlap_after_base :
    finalSigma [{ cased := true, ignorable := false },
                { cased := true, ignorable := true }] [] = true := rfl

theorem overlap_after :
    finalSigma [{ cased := true, ignorable := false }]
               [{ cased := true, ignorable := true }] = true := rfl

structure Character where
  properties : Properties
  masked : Bool
  deriving DecidableEq

def barrier : Properties := ⟨false, false⟩

def project (c : Character) : Properties :=
  if c.masked then barrier else c.properties

def maskedScan : List Character → Bool
  | [] => false
  | c :: cs => if c.masked then false
               else if c.properties.ignorable then maskedScan cs
               else c.properties.cased

theorem maskedScan_projection (xs : List Character) :
    maskedScan xs = scan (xs.map project) := by
  induction xs with
  | nil => rfl
  | cons c cs ih =>
    cases hm : c.masked <;> simp [maskedScan, project, hm, scan, barrier]
    cases hi : c.properties.ignorable <;> simp [ih]

def maskedFinal (before after : List Character) : Bool :=
  maskedScan before.reverse && !maskedScan after

theorem maskedFinal_specification (before after : List Character) :
    maskedFinal before after =
      specifiedFinalSigma (before.map project) (after.map project) := by
  simp [maskedFinal, specifiedFinalSigma, maskedScan_projection,
        scan_eq_specified, List.map_reverse]

theorem unmasked_projection (xs : List Properties) :
    (xs.map (fun p => Character.mk p false)).map project = xs := by
  simp [List.map_map, Function.comp_def, project]

theorem all_unmasked_reduction (before after : List Properties) :
    maskedFinal (before.map (fun p => Character.mk p false))
                (after.map (fun p => Character.mk p false)) =
      specifiedFinalSigma before after := by
  rw [maskedFinal_specification, unmasked_projection, unmasked_projection]

def replaceMasked (f : Properties → Properties) (c : Character) : Character :=
  if c.masked then ⟨f c.properties, true⟩ else c

theorem masked_replacement_projection (f : Properties → Properties)
    (xs : List Character) :
    (xs.map (replaceMasked f)).map project = xs.map project := by
  simp only [List.map_map]
  apply List.map_congr_left
  intro c _
  cases hm : c.masked <;> simp [replaceMasked, project, hm]

theorem masked_codepoint_independence (f g : Properties → Properties)
    (before after : List Character) :
    maskedFinal (before.map (replaceMasked f)) (after.map (replaceMasked g)) =
      maskedFinal before after := by
  rw [maskedFinal_specification, maskedFinal_specification,
      masked_replacement_projection, masked_replacement_projection]

def decisionAt (full : List Character) (i : Nat) : Bool :=
  maskedFinal (full.take i) (full.drop (i + 1))

theorem indexed_context_correct (before after : List Character) (current : Character) :
    decisionAt (before ++ current :: after) before.length =
      specifiedFinalSigma (before.map project) (after.map project) := by
  have hd : before.drop (before.length + 1) = [] := List.drop_eq_nil_of_le (by omega)
  simp only [decisionAt, List.take_append, List.take_length, Nat.sub_self,
             List.take_zero, List.append_nil, List.drop_append, hd]
  simp [maskedFinal_specification]

theorem context_slice_correct
    (full before left right after : List Character) (current : Character)
    (hfull : full = before ++ (left ++ current :: right) ++ after) :
    decisionAt full (before.length + left.length) =
      specifiedFinalSigma ((before ++ left).map project) ((right ++ after).map project) := by
  have h : full = (before ++ left) ++ current :: (right ++ after) := by
    simp [hfull, List.append_assoc]
  rw [h]
  simpa only [List.length_append] using indexed_context_correct (before ++ left) (right ++ after) current

theorem masked_predecessor_barrier (c : Character) (before after : List Character)
    (hm : c.masked = true) : maskedFinal (before ++ [c]) after = false := by
  simp [maskedFinal, List.reverse_append, maskedScan, hm]

theorem masked_successor_barrier (c : Character) (before after : List Character)
    (hm : c.masked = true) : maskedFinal before (c :: after) = maskedScan before.reverse := by
  simp [maskedFinal, maskedScan, hm]

#print axioms scan_eq_specified
#print axioms finalSigma_eq_specified
#print axioms ignorable_invariance
#print axioms overlap_without_base
#print axioms overlap_after_base
#print axioms overlap_after
#print axioms maskedScan_projection
#print axioms maskedFinal_specification
#print axioms unmasked_projection
#print axioms all_unmasked_reduction
#print axioms masked_replacement_projection
#print axioms masked_codepoint_independence
#print axioms indexed_context_correct
#print axioms context_slice_correct
#print axioms masked_predecessor_barrier
#print axioms masked_successor_barrier

end SigmaContext
