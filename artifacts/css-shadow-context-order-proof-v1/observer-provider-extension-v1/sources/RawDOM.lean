import PseudoNormalization
import RuleAdmission
namespace ShadowOrder

abbrev PseudoMap := List (List Nat × List RawSelectorResult)
abbrev PartPseudoMap := List (List Nat × List (Nat × List RawSelectorResult))

structure RawCascadeData where
 table : List RawStyleRule
 normal : PseudoMap
 host : PseudoMap
 slotted : PseudoMap
 part : PartPseudoMap
 deriving DecidableEq, Repr

structure RawElement where
 implementedPseudo : Option Nat
 originatingElement : Option Nat
 containingShadow : Option Nat
 containingIgnoringSvgUse : Option Nat
 ownShadow : Option Nat
 assignedSlot : Option Nat
 parts : List Nat
 hasPartAttribute : Bool
 exports : List (Nat × List Nat)
 matchesContent : Bool
 deriving DecidableEq, Repr

structure RawShadowRoot where
 host : Nat
 styleData : Option RawCascadeData
 deriving DecidableEq, Repr

structure RawProviderInput where
 elements : List RawElement
 roots : List RawShadowRoot
 element : Nat
 explicitPseudo : Option Nat
 ua : RawCascadeData
 user : RawCascadeData
 document : RawCascadeData
 elementBackedPseudos : List Nat
 namedViewTransitionPseudos : List Nat
 dynamicUa : List RawStyleRule
 presentationHints : List RawStyleRule
 inlineStyle : Option RawStyleRule
 smil : Option RawStyleRule
 animation : Option RawStyleRule
 transition : Option RawStyleRule
 defaultOnly : Bool
 authorEnabled : Bool
 deriving DecidableEq, Repr

def pseudoMapLookup (maps : PseudoMap) (pseudos : List Nat) : Option (List RawSelectorResult) :=
 (maps.find? fun entry => entry.1 == pseudos).map Prod.snd

def partMapLookup (maps : PartPseudoMap) (pseudos : List Nat) :
 Option (List (Nat × List RawSelectorResult)) :=
 (maps.find? fun entry => entry.1 == pseudos).map Prod.snd

def mapRules (tree : Nat) (data : RawCascadeData) (map : Option (List RawSelectorResult)) : List Rule :=
 map.toList.flatten.filterMap (materialize tree data.table)

def sortedMapRules (tree : Nat) (data : RawCascadeData) (map : Option (List RawSelectorResult)) : List Rule :=
 localSort completeLocalKey (mapRules tree data map)

def partRules (tree : Nat) (data : RawCascadeData) (pseudos : List Nat) : List PartRule :=
 (partMapLookup data.part pseudos).toList.flatten.flatMap fun named =>
   (mapRules tree data (some named.2)).map fun rule => ⟨named.1,rule⟩

def plainRule (tree sourceOrder : Nat) (source : RawStyleRule) : Rule :=
 ⟨tree,source.source,source.layer,0,65535,sourceOrder,source.flags,source.declarations⟩

def originEntries (origin _tree : Nat) (rules : List Rule) : List Entry :=
 rules.map fun rule => ⟨rule,origin,0⟩

def rawPseudoNodes (raw : RawProviderInput) : List PseudoNode :=
 raw.elements.map fun element => ⟨element.implementedPseudo,element.originatingElement⟩

def slotContext (pseudos : List Nat) (identity : Nat) (root : RawShadowRoot) : InnerContext :=
 ⟨identity+1,root.styleData.toList.flatMap (fun data =>
   sortedMapRules (identity+1) data (pseudoMapLookup data.slotted pseudos))⟩

def normalizeSlots (raw : RawProviderInput) (pseudos : List Nat) :
 Nat → Option Nat → Option (List InnerContext)
 | _, none => some []
 | 0, some _ => none
 | fuel+1, some identity => do
   let element ← raw.elements[identity]?
   let rootIdentity ← element.containingShadow
   let root ← raw.roots[rootIdentity]?
   let tail ← normalizeSlots raw pseudos fuel element.assignedSlot
   return slotContext pseudos rootIdentity root::tail

def documentOuterContext (raw : RawProviderInput) (pseudos : List Nat) (host : RawElement) : Context :=
 ⟨0,(partMapLookup raw.document.part pseudos).isSome,partRules 0 raw.document pseudos,host.exports⟩

def shadowOuterContext (pseudos : List Nat) (identity : Nat) (root : RawShadowRoot)
 (host : RawElement) : Context :=
 ⟨identity+1,(root.styleData.bind fun data => partMapLookup data.part pseudos).isSome,
   root.styleData.toList.flatMap (fun data => partRules (identity+1) data pseudos),host.exports⟩

def normalizeOuter (raw : RawProviderInput) (pseudos : List Nat) :
 Nat → Nat → Option (List Context)
 | 0, _ => none
 | fuel+1, innerRootIdentity => do
   let inner ← raw.roots[innerRootIdentity]?
   let host ← raw.elements[inner.host]?
   match host.containingShadow with
   | none =>
     return [documentOuterContext raw pseudos host]
   | some outerIdentity =>
     let outer ← raw.roots[outerIdentity]?
     let tail ← normalizeOuter raw pseudos fuel outerIdentity
     return shadowOuterContext pseudos outerIdentity outer host::tail

def normalizeContaining (raw : RawProviderInput) (pseudos : List Nat) (target : RawElement) :
 Option (List Entry × Bool) := do
 if !target.matchesContent then return ([],false)
 match target.containingIgnoringSvgUse with
 | none => return ([],true)
 | some identity =>
   let root ← raw.roots[identity]?
   let rules := root.styleData.toList.flatMap fun data =>
     mapRules (identity+1) data (pseudoMapLookup data.normal pseudos) ++
     if target.hasPartAttribute then
       target.parts.flatMap fun name =>
         (partRules (identity+1) data pseudos).filterMap fun p =>
           if p.name == name then some p.rule else none
     else []
   return (originEntries 3 (identity+1) (localSort completeLocalKey rules),false)

def normalizeOwnHost (raw : RawProviderInput) (pseudos : List Nat) (target : RawElement) (elementBacked : Bool) :
 Option (List Rule) := do
 match target.ownShadow with
 | none => return []
 | some identity =>
   let root ← raw.roots[identity]?
   let rules := root.styleData.toList.flatMap fun data =>
     mapRules (identity+1) data (pseudoMapLookup data.host pseudos) ++
     if elementBacked then mapRules (identity+1) data (pseudoMapLookup data.normal []) else []
   return localSort completeLocalKey rules

def normalizeRawProviders (raw : RawProviderInput) : Option RawInput := do
 let normalized ← nativePseudo (rawPseudoNodes raw) (raw.elements.length+1)
   raw.element raw.explicitPseudo.toList
 let target ← raw.elements[normalized.1]?
 let pseudos := normalized.2
 let elementBacked := normalized.1 != raw.element && pseudos.length == 1 &&
   (pseudos.head?.map fun p => raw.elementBackedPseudos.contains p).getD false
 let namedViewTransition :=
   (pseudos.head?.map fun p => raw.namedViewTransitionPseudos.contains p).getD false
 let uaRules := (if elementBacked then mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal []) else []) ++
   mapRules 0 raw.ua (pseudoMapLookup raw.ua.normal pseudos)
 let dynamicUa := if namedViewTransition then raw.dynamicUa.map (fun rule => plainRule 0 0 {rule with layer := 65534,flags := 0}) else []
 let userRules := if target.matchesContent then
   sortedMapRules 0 raw.user (pseudoMapLookup raw.user.normal pseudos) else []
 let base : RawInput := {
   limit := maxOrder
   parts := target.parts
   outerContexts := []
   assignedSlots := []
   ownHostRules := []
   ua := originEntries 0 0 (localSort completeLocalKey uaRules ++ dynamicUa)
   user := originEntries 1 0 userRules
   presHints := []
   sameTree := []
   document := []
   inlineRules := []
   animations := []
   defaultOnly := raw.defaultOnly
   authorEnabled := raw.authorEnabled }
 if raw.defaultOnly then return base
 let hints := if pseudos.isEmpty then raw.presentationHints.map (fun rule => plainRule 0 0 {rule with layer := 65534,flags := 0}) else []
 let base := {base with presHints := originEntries 2 0 hints}
 if !raw.authorEnabled then return base
 let slots ← normalizeSlots raw pseudos (raw.elements.length+1) target.assignedSlot
 let ownHost ← normalizeOwnHost raw pseudos target elementBacked
 let containing ← normalizeContaining raw pseudos target
 let outer ← if target.hasPartAttribute then
   match target.containingShadow with
   | none => some []
   | some root => normalizeOuter raw pseudos (raw.roots.length+1) root
   else some []
 let documentRules := if containing.2 then
   sortedMapRules 0 raw.document (pseudoMapLookup raw.document.normal pseudos) else []
 let targetTree := target.containingShadow.map (·+1) |>.getD 0
 let inlineRules := raw.inlineStyle.toList.map fun rule =>
   plainRule targetTree 0 {rule with layer := 65535,flags := 0}
 let animationRules :=
   (raw.smil.toList.map fun rule => ⟨plainRule targetTree 0 {rule with layer := 65534,flags := 0},5,0⟩) ++
   (raw.animation.toList.map fun rule => ⟨plainRule targetTree 0 {rule with layer := 65534,flags := 0},6,0⟩) ++
   (raw.transition.toList.map fun rule => ⟨plainRule targetTree 0 {rule with layer := 65534,flags := 0},7,0⟩)
 return {base with
   outerContexts := outer
   assignedSlots := slots
   ownHostRules := ownHost
   sameTree := containing.1
   document := originEntries 3 0 documentRules
   inlineRules := originEntries 3 targetTree inlineRules
   animations := animationRules}

def rawProviderExecution (raw : RawProviderInput) : Option (List Entry) :=
 (normalizeRawProviders raw).map nativeCollected

def normalizedReferenceExecution (raw : RawProviderInput) : Option (List Entry) :=
 (normalizeRawProviders raw).map referenceCollected

theorem provider_dispatch_composition (raw : RawProviderInput) :
 rawProviderExecution raw = normalizedReferenceExecution raw := by
 unfold rawProviderExecution normalizedReferenceExecution
 cases normalized : normalizeRawProviders raw <;> simp [raw_dispatch_refinement]

#print axioms provider_dispatch_composition
end ShadowOrder
