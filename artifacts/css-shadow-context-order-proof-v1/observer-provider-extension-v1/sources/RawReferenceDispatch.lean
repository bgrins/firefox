import ReferenceProviders
namespace ShadowOrder

def referenceDispatch (raw : RawProviderInput) (element : Nat) (pseudos : List Nat) : Option (List Entry) := do
 let target ← raw.elements[element]?
 let elementBacked := element != raw.element && pseudos.length == 1 &&
   (pseudos.head?.map fun p => raw.elementBackedPseudos.contains p).getD false
 let namedViewTransition :=
   (pseudos.head?.map fun p => raw.namedViewTransitionPseudos.contains p).getD false
 let uaStyles := localSort completeLocalKey
   ((if elementBacked then mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal []) else []) ++
     mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal pseudos))
 let dynamic := if namedViewTransition then raw.dynamicUa.map
   (fun block => plainRule 0 0 {block with layer := 65534,flags := 0}) else []
 let userStyles := if target.matchesContent then
   sortedMapRules 0 raw.user (pseudoMapLookup raw.user.normal pseudos) else []
 let defaults := originEntries 0 0 (uaStyles ++ dynamic) ++ originEntries 1 0 userStyles
 if raw.defaultOnly then return defaults
 let hints := originEntries 2 0 (if pseudos.isEmpty then raw.presentationHints.map
   (fun block => plainRule 0 0 {block with layer := 65534,flags := 0}) else [])
 if raw.authorEnabled then
   let author ← directAuthorReference raw target pseudos elementBacked maxOrder
   let tree := target.containingShadow.map (·+1) |>.getD 0
   let animated :=
     originEntries 5 tree (raw.smil.toList.map fun block => plainRule tree 0 {block with layer := 65534,flags := 0}) ++
     originEntries 6 tree (raw.animation.toList.map fun block => plainRule tree 0 {block with layer := 65534,flags := 0}) ++
     originEntries 7 tree (raw.transition.toList.map fun block => plainRule tree 0 {block with layer := 65534,flags := 0})
   return defaults ++ hints ++ author ++ animated
 else return defaults ++ hints

def directRawReference (raw : RawProviderInput) : Option (List Entry) := do
 let ancestry ← referencePseudo (rawPseudoNodes raw) (raw.elements.length+1) raw.element
 referenceDispatch raw ancestry.1 (raw.explicitPseudo.toList ++ ancestry.2)

theorem normalized_reference_dispatch (raw : RawProviderInput) (normalized : RawInput)
 (pseudo : Nat × List Nat)
 (pseudoMade : nativePseudo (rawPseudoNodes raw) (raw.elements.length+1) raw.element raw.explicitPseudo.toList = some pseudo)
 (made : normalizeRawProviders raw = some normalized) :
 referenceDispatch raw pseudo.1 pseudo.2 = some (nativeCollected normalized) := by
 cases targetFound : raw.elements[pseudo.1]? with
 | none => simp [normalizeRawProviders,pseudoMade,targetFound] at made
 | some target =>
   cases defaults : raw.defaultOnly with
   | true =>
     simp [normalizeRawProviders,pseudoMade,targetFound,defaults] at made
     subst normalized
     simp [referenceDispatch,targetFound,defaults,nativeCollected,List.append_assoc]
   | false =>
     cases enabled : raw.authorEnabled with
     | false =>
       simp [normalizeRawProviders,pseudoMade,targetFound,defaults,enabled] at made
       subst normalized
       simp [referenceDispatch,targetFound,defaults,enabled,nativeCollected,List.append_assoc]
     | true =>
       let elementBacked := pseudo.1 != raw.element && pseudo.2.length == 1 &&
         (pseudo.2.head?.map fun p => raw.elementBackedPseudos.contains p).getD false
       cases slotsMade : normalizeSlots raw pseudo.2 (raw.elements.length+1) target.assignedSlot with
       | none => simp [normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade] at made
       | some slots =>
         cases hostMade : normalizeOwnHost raw pseudo.2 target elementBacked with
         | none =>
           simp only [elementBacked] at hostMade
           simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,
             Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade] at made
           contradiction
         | some host =>
           simp only [elementBacked] at hostMade
           cases containingMade : normalizeContaining raw pseudo.2 target with
           | none =>
             simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,
               Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade,containingMade] at made
             contradiction
           | some containing =>
             cases partFlag : target.hasPartAttribute with
             | false =>
               have refAuthor := direct_author_reference_refinement raw target pseudo.2 elementBacked maxOrder slots host containing []
                 slotsMade hostMade containingMade (by simp [outerProviderChoice,partFlag])
               simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,
                 Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag] at made
               subst normalized
               simp only [elementBacked] at refAuthor
               simp only [referenceDispatch,targetFound,bind,pure,Option.bind_some,defaults,enabled,↓reduceIte,refAuthor]
               cases doc : containing.2 <;>
                 simp [nativeCollected,normalizedAuthorGroups,doc,originEntries,Function.comp_def,List.append_assoc]
             | true =>
               cases outerRoot : target.containingShadow with
               | none =>
                 have refAuthor := direct_author_reference_refinement raw target pseudo.2 elementBacked maxOrder slots host containing []
                   slotsMade hostMade containingMade (by simp [outerProviderChoice,partFlag,outerRoot])
                 simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,
                   Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot] at made
                 subst normalized
                 simp only [elementBacked] at refAuthor
                 simp only [referenceDispatch,targetFound,bind,pure,Option.bind_some,defaults,enabled,↓reduceIte,refAuthor]
                 cases doc : containing.2 <;>
                   simp [nativeCollected,normalizedAuthorGroups,doc,originEntries,Function.comp_def,List.append_assoc,outerRoot]
               | some root =>
                 cases outerMade : normalizeOuter raw pseudo.2 (raw.roots.length+1) root with
                 | none =>
                   simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,
                     Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made
                   contradiction
                 | some contexts =>
                   have refAuthor := direct_author_reference_refinement raw target pseudo.2 elementBacked maxOrder slots host containing contexts
                     slotsMade hostMade containingMade (by simpa [outerProviderChoice,partFlag,outerRoot] using outerMade)
                   simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,
                     Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoMade,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made
                   subst normalized
                   simp only [elementBacked] at refAuthor
                   simp only [referenceDispatch,targetFound,bind,pure,Option.bind_some,defaults,enabled,↓reduceIte,refAuthor]
                   cases doc : containing.2 <;>
                     simp [nativeCollected,normalizedAuthorGroups,doc,originEntries,Function.comp_def,List.append_assoc,outerRoot]

theorem direct_raw_reference_normalized (raw : RawProviderInput) (normalized : RawInput)
 (made : normalizeRawProviders raw = some normalized) :
 directRawReference raw = some (nativeCollected normalized) := by
 have pseudo := pseudo_normalization (rawPseudoNodes raw) (raw.elements.length+1)
   raw.element raw.explicitPseudo.toList
 cases referenceMade : referencePseudo (rawPseudoNodes raw) (raw.elements.length+1) raw.element with
 | none =>
   rw [referenceMade] at pseudo
   simp only [Option.map_none] at pseudo
   simp [normalizeRawProviders,pseudo] at made
 | some ancestry =>
   rw [referenceMade] at pseudo
   simp only [Option.map_some] at pseudo
   have dispatch := normalized_reference_dispatch raw normalized
     (ancestry.1,raw.explicitPseudo.toList ++ ancestry.2) pseudo made
   simpa [directRawReference,referenceMade] using dispatch

theorem admitted_raw_reference_refinement (raw : RawProviderInput) (admitted : rawAdmitted raw = true) :
 rawProviderExecution raw = directRawReference raw := by
 rcases admitted_has_normalization raw admitted with ⟨normalized,made,bounds⟩
 rw [direct_raw_reference_normalized raw normalized made]
 simp [rawProviderExecution,made]

#print axioms normalized_reference_dispatch
#print axioms admitted_raw_reference_refinement
end ShadowOrder
