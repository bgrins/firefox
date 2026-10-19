import ProviderTraversal
namespace ShadowOrder

def rawBlockValid (block : RawStyleRule) : Bool :=
 block.layer < 65536 && block.flags < 4 &&
 decide ((block.declarations.map Declaration.property).Nodup)

def pseudoPathsClosed (paths : List (List Nat)) : Bool :=
 paths.all fun path => (List.range (path.length+1)).all fun length =>
   paths.contains (path.take length)

def rawMapValid (table : List RawStyleRule) (maps : PseudoMap) : Bool :=
 (decide ((maps.map Prod.fst).Nodup) && pseudoPathsClosed (maps.map Prod.fst)) &&
 maps.all (fun entry => entry.2.all (rawRuleAdmission table))

def rawPartMapValid (table : List RawStyleRule) (maps : PartPseudoMap) : Bool :=
 (decide ((maps.map Prod.fst).Nodup) && pseudoPathsClosed (maps.map Prod.fst)) && maps.all (fun entry =>
   decide ((entry.2.map Prod.fst).Nodup) &&
   entry.2.all (fun named => named.2.all (rawRuleAdmission table)))

def rawDataValid (data : RawCascadeData) : Bool :=
 data.normal.any (fun entry => entry.1.isEmpty) &&
 data.table.all (fun block => rawBlockValid block && block.layer < 65535) && rawMapValid data.table data.normal &&
 rawMapValid data.table data.host && rawMapValid data.table data.slotted &&
 rawPartMapValid data.table data.part

def validIndex (size : Nat) (index : Option Nat) : Bool :=
 index.toList.all (fun index => index < size)

def rawEdgesValid (raw : RawProviderInput) : Bool :=
 raw.element < raw.elements.length &&
 raw.elements.zipIdx.all (fun (element,identity) =>
   validIndex raw.elements.length element.originatingElement &&
   validIndex raw.elements.length element.assignedSlot &&
   validIndex raw.roots.length element.containingShadow &&
   validIndex raw.roots.length element.containingIgnoringSvgUse &&
   validIndex raw.roots.length element.ownShadow &&
   element.ownShadow.toList.all (fun root =>
     (raw.roots[root]?.map fun root => root.host == identity).getD false) &&
   decide ((element.exports.map Prod.fst).Nodup)) &&
 raw.roots.zipIdx.all (fun (root,identity) =>
   root.host < raw.elements.length &&
   (raw.elements[root.host]?.map fun element => element.ownShadow == some identity).getD false)

def normalOnlyBlock (block : RawStyleRule) : Bool :=
 block.declarations.all (fun declaration => !declaration.important)

def rawFieldsValid (raw : RawProviderInput) : Bool :=
 rawEdgesValid raw && rawDataValid raw.ua && rawDataValid raw.user && rawDataValid raw.document &&
 raw.roots.all (fun root => root.styleData.toList.all rawDataValid) &&
 (raw.dynamicUa ++ raw.presentationHints ++ raw.inlineStyle.toList ++ raw.smil.toList ++
   raw.animation.toList ++ raw.transition.toList).all rawBlockValid &&
 (raw.presentationHints ++ raw.smil.toList ++ raw.animation.toList ++ raw.transition.toList).all normalOnlyBlock

def normalizedBounds (normalized : RawInput) : Bool :=
 eligibleCount normalized.outerContexts ≤ maxOrder &&
 normalized.assignedSlots.length ≤ maxOrder &&
 (normalized.ownHostRules.isEmpty || normalized.assignedSlots.length < maxOrder)

def rawAdmitted (raw : RawProviderInput) : Bool :=
 rawFieldsValid raw &&
 ((normalizeRawProviders raw).map normalizedBounds).getD false

theorem admitted_has_normalization (raw : RawProviderInput) (h : rawAdmitted raw = true) :
 ∃ normalized, normalizeRawProviders raw = some normalized ∧ normalizedBounds normalized = true := by
 unfold rawAdmitted at h
 cases normalized : normalizeRawProviders raw with
 | none => simp [normalized] at h
 | some value =>
   simp [normalized] at h
   exact ⟨value,rfl,h.2⟩

theorem admitted_dispatch (raw : RawProviderInput) (h : rawAdmitted raw = true) :
 ∃ normalized,
   normalizeRawProviders raw = some normalized ∧
   rawProviderExecution raw = some (nativeCollected normalized) ∧
   nativeCollected normalized = referenceCollected normalized := by
 rcases admitted_has_normalization raw h with ⟨normalized,hn,hb⟩
 exact ⟨normalized,hn,by simp [rawProviderExecution,hn],raw_dispatch_refinement normalized⟩

def emptyRawData : RawCascadeData := ⟨[],[([],[])],[],[],[]⟩

def emptyRawElement : RawElement :=
 ⟨none,none,none,none,none,none,[],false,[],true⟩

def emptyRawProvider : RawProviderInput :=
 ⟨[emptyRawElement],[],0,none,emptyRawData,emptyRawData,emptyRawData,[],[],[],[],none,
   none,none,none,false,true⟩

theorem empty_provider_admitted : rawAdmitted emptyRawProvider = true := by decide

theorem empty_provider_execution : rawProviderExecution emptyRawProvider = some [] := by decide

#print axioms admitted_has_normalization
#print axioms admitted_dispatch
#print axioms empty_provider_admitted
#print axioms empty_provider_execution
end ShadowOrder
