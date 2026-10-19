import RawLayers
namespace ShadowOrder

def authorOnlyEntries (raw : RawInput) : List Entry :=
 hostCollector raw.limit raw.assignedSlots.length raw.ownHostRules ++
 reverseSlotCollector raw.limit 0 raw.assignedSlots ++ raw.sameTree ++ raw.document ++
 raw.inlineRules ++ collectParts raw.limit 1 raw.parts raw.outerContexts

def AuthorConstructionProperty (raw : RawProviderInput) (P : List Entry → Prop) : Prop :=
 ∀ (target : RawElement) (pseudos : List Nat) (host : List Rule) (slots : List InnerContext)
   (containing : List Entry × Bool) (contexts : List Context) (elementBacked : Bool),
   normalizeOwnHost raw pseudos target elementBacked = some host →
   normalizeSlots raw pseudos (raw.elements.length+1) target.assignedSlot = some slots →
   normalizeContaining raw pseudos target = some containing →
   (contexts = [] ∨ ∃ root fuel, normalizeOuter raw pseudos fuel root = some contexts) →
   P (normalizedAuthorGroups raw target pseudos host slots containing contexts maxOrder)

theorem raw_author_normalization_property (raw : RawProviderInput) (normalized : RawInput)
 (P : List Entry → Prop) (empty : P []) (constructed : AuthorConstructionProperty raw P)
 (made : normalizeRawProviders raw = some normalized) : P (authorOnlyEntries normalized) := by
 cases pseudoResult : nativePseudo (rawPseudoNodes raw) (raw.elements.length+1)
     raw.element raw.explicitPseudo.toList with
 | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult] at made; contradiction
 | some pseudo =>
   cases targetFound : raw.elements[pseudo.1]? with
   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,normalizeRawProviders,pseudoResult,targetFound] at made; contradiction
   | some target =>
     cases defaults : raw.defaultOnly with
     | true =>
       simp only [bind,pure,Option.bind_some,Option.some.injEq,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults] at made
       subst normalized
       simpa [authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] using empty
     | false =>
       cases enabled : raw.authorEnabled with
       | false =>
         simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_false,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled] at made
         subst normalized
         simpa [authorOnlyEntries,hostCollector,inner,reverseSlotCollector,collectParts,atOrder,maxOrder] using empty
       | true =>
         let elementBacked := pseudo.1 != raw.element && pseudo.2.length == 1 &&
           (pseudo.2.head?.map fun p => raw.elementBackedPseudos.contains p).getD false
         cases slotsMade : normalizeSlots raw pseudo.2 (raw.elements.length+1) target.assignedSlot with
         | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade] at made; contradiction
         | some slots =>
           cases hostMade : normalizeOwnHost raw pseudo.2 target elementBacked with
           | none =>
             simp only [elementBacked] at hostMade
             simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade] at made; contradiction
           | some host =>
             simp only [elementBacked] at hostMade
             cases containingMade : normalizeContaining raw pseudo.2 target with
             | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade] at made; contradiction
             | some containing =>
               cases partFlag : target.hasPartAttribute with
               | false =>
                 have order := constructed target pseudo.2 host slots containing [] elementBacked
                   hostMade slotsMade containingMade (Or.inl rfl)
                 simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag] at made
                 subst normalized
                 cases doc : containing.2 <;>
                   simpa [authorOnlyEntries,normalizedAuthorGroups,doc,originEntries,List.append_assoc] using order
               | true =>
                 cases outerRoot : target.containingShadow with
                 | none =>
                   have order := constructed target pseudo.2 host slots containing [] elementBacked
                     hostMade slotsMade containingMade (Or.inl rfl)
                   simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot] at made
                   subst normalized
                   cases doc : containing.2 <;>
                     simpa [authorOnlyEntries,normalizedAuthorGroups,doc,originEntries,List.append_assoc,outerRoot] using order
                 | some root =>
                   cases outerMade : normalizeOuter raw pseudo.2 (raw.roots.length+1) root with
                   | none => simp only [bind,pure,Option.bind_some,Option.bind_none,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made; contradiction
                   | some contexts =>
                     have order := constructed target pseudo.2 host slots containing contexts elementBacked
                       hostMade slotsMade containingMade
                       (Or.inr ⟨root,raw.roots.length+1,outerMade⟩)
                     simp only [bind,pure,Option.bind_some,Option.some.injEq,Bool.not_true,Bool.false_eq_true,↓reduceIte,normalizeRawProviders,pseudoResult,targetFound,defaults,enabled,slotsMade,hostMade,containingMade,partFlag,outerRoot,outerMade] at made
                     subst normalized
                     cases doc : containing.2 <;>
                       simpa [authorOnlyEntries,normalizedAuthorGroups,doc,originEntries,List.append_assoc,outerRoot] using order

theorem raw_author_normalization_order (raw : RawProviderInput) (normalized : RawInput)
 (valid : rawFieldsValid raw = true)
 (made : normalizeRawProviders raw = some normalized) :
 (authorOnlyEntries normalized).Pairwise contextLayerLE := by
 apply raw_author_normalization_property raw normalized (fun entries => entries.Pairwise contextLayerLE)
   (by simp) _ made
 intro target pseudos host slots containing contexts elementBacked hostMade slotsMade containingMade outerMade
 exact raw_author_group_order raw target pseudos host slots containing contexts elementBacked
   (raw.elements.length+1) maxOrder valid hostMade slotsMade containingMade outerMade

#print axioms raw_author_normalization_order
end ShadowOrder
