import RawLayers
namespace ShadowOrder

def directExportNames (exports : List (Nat × List Nat)) (parts : List Nat) : List Nat :=
 parts.flatMap fun name => ((exports.find? fun item => item.1 == name).map Prod.snd).getD []

def directPartRules (tree : Nat) (data : RawCascadeData) (pseudos parts : List Nat) : List Rule :=
 parts.flatMap fun name => ((partRules tree data pseudos).filter fun rule => rule.name == name).map PartRule.rule

def directOuterContribution (tree limit rank : Nat) (data : Option RawCascadeData)
 (pseudos parts : List Nat) : List Entry :=
 if (data.bind fun styles => partMapLookup styles.part pseudos).isSome && rank ≤ limit then
   atOrder rank (localSort completeLocalKey
     (parts.flatMap fun name => data.toList.flatMap fun styles =>
       ((partRules tree styles pseudos).filter fun rule => rule.name == name).map PartRule.rule))
 else []

def directOuterReference (raw : RawProviderInput) (pseudos : List Nat) :
 Nat → Nat → Nat → Nat → List Nat → Option (List Entry)
 | 0, _, _, _, _ => none
 | fuel+1, innerIdentity, limit, rank, parts => do
   let inner ← raw.roots[innerIdentity]?
   let host ← raw.elements[inner.host]?
   match host.containingShadow with
   | none =>
     return if parts.isEmpty then [] else directOuterContribution 0 limit rank (some raw.document) pseudos parts
   | some outerIdentity =>
     let outer ← raw.roots[outerIdentity]?
     let eligible := (outer.styleData.bind fun styles => partMapLookup styles.part pseudos).isSome
     let names := directExportNames host.exports parts
     let rest ← directOuterReference raw pseudos fuel outerIdentity limit (rank + if eligible then 1 else 0) names
     return if parts.isEmpty then [] else
       directOuterContribution (outerIdentity+1) limit rank outer.styleData pseudos parts ++ rest

theorem direct_document_contribution (raw : RawProviderInput) (pseudos parts : List Nat)
 (host : RawElement) (limit rank : Nat) :
 directOuterContribution 0 limit rank (some raw.document) pseudos parts =
 (if (documentOuterContext raw pseudos host).mapPresent && rank ≤ limit then
   atOrder rank (localSort completeLocalKey (matching (documentOuterContext raw pseudos host) parts)) else []) := by
 simp [directOuterContribution,documentOuterContext,matching]

theorem direct_shadow_contribution (pseudos parts : List Nat) (identity : Nat)
 (root : RawShadowRoot) (host : RawElement) (limit rank : Nat) :
 directOuterContribution (identity+1) limit rank root.styleData pseudos parts =
 (if (shadowOuterContext pseudos identity root host).mapPresent && rank ≤ limit then
   atOrder rank (localSort completeLocalKey (matching (shadowOuterContext pseudos identity root host) parts)) else []) := by
 cases data : root.styleData <;>
   simp [directOuterContribution,shadowOuterContext,matching,data]

theorem direct_outer_reference_refinement (raw : RawProviderInput) (pseudos parts : List Nat)
 (fuel identity limit rank : Nat) (contexts : List Context)
 (normalized : normalizeOuter raw pseudos fuel identity = some contexts) :
 directOuterReference raw pseudos fuel identity limit rank parts =
 some (physicalReference limit rank parts contexts) := by
 induction fuel generalizing identity contexts rank parts with
 | zero => simp [normalizeOuter] at normalized
 | succ fuel ih =>
   cases rootFound : raw.roots[identity]? with
   | none => simp [normalizeOuter,rootFound] at normalized
   | some inner =>
     cases hostFound : raw.elements[inner.host]? with
     | none => simp [normalizeOuter,rootFound,hostFound] at normalized
     | some host =>
       cases outside : host.containingShadow with
       | none =>
         simp [normalizeOuter,rootFound,hostFound,outside] at normalized
         subst contexts
         simp only [directOuterReference,rootFound,hostFound,bind,Option.bind_some,outside,pure,
           physicalReference,List.append_nil]
         rw [direct_document_contribution raw pseudos parts host limit rank]
         rfl
       | some outerIdentity =>
         cases outerFound : raw.roots[outerIdentity]? with
         | none => simp [normalizeOuter,rootFound,hostFound,outside,outerFound] at normalized
         | some outer =>
           cases tail : normalizeOuter raw pseudos fuel outerIdentity with
           | none => simp [normalizeOuter,rootFound,hostFound,outside,outerFound,tail] at normalized
           | some rest =>
             simp [normalizeOuter,rootFound,hostFound,outside,outerFound,tail] at normalized
             subst contexts
             have tailReference := ih (directExportNames host.exports parts) outerIdentity
               (rank + if (outer.styleData.bind fun styles => partMapLookup styles.part pseudos).isSome then 1 else 0) rest tail
             simp only [directOuterReference,rootFound,hostFound,bind,Option.bind_some,outside,outerFound,tailReference,pure,
               physicalReference]
             rw [direct_shadow_contribution pseudos parts outerIdentity outer host limit rank]
             rfl

#print axioms direct_outer_reference_refinement
end ShadowOrder
