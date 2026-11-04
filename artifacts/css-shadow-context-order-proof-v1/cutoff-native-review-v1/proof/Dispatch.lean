import Collection
namespace ShadowOrder
set_option maxHeartbeats 800000
structure RawInput where
 limit : Nat
 parts : List Nat
 outerContexts : List Context
 assignedSlots : List InnerContext
 ownHostRules : List Rule
 ua : List Entry
 user : List Entry
 presHints : List Entry
 sameTree : List Entry
 document : List Entry
 inlineRules : List Entry
 animations : List Entry
 defaultOnly : Bool
 authorEnabled : Bool
 deriving DecidableEq, Repr

def nativeCollected (raw : RawInput) : List Entry :=
 raw.ua ++ raw.user ++
 if raw.defaultOnly then [] else
 raw.presHints ++ if !raw.authorEnabled then [] else
 hostCollector raw.limit raw.assignedSlots.length raw.ownHostRules ++
 reverseSlotCollector raw.limit 0 raw.assignedSlots ++
 raw.sameTree ++ raw.document ++ raw.inlineRules ++
 collectParts raw.limit 1 raw.parts raw.outerContexts ++ raw.animations

def referenceCollected (raw : RawInput) : List Entry :=
 let surrounding := raw.sameTree ++ raw.document ++ raw.inlineRules
 let inner := hostReference raw.limit raw.assignedSlots.length raw.ownHostRules ++
   (slotReference raw.limit 0 raw.assignedSlots).reverse.flatten
 let outer := physicalReference raw.limit 1 raw.parts raw.outerContexts
 let author := inner ++ surrounding ++ outer ++ raw.animations
 raw.ua ++ raw.user ++
 (if raw.defaultOnly then [] else raw.presHints ++ if raw.authorEnabled then author else [])

theorem raw_dispatch_refinement (raw : RawInput) :
 nativeCollected raw = referenceCollected raw := by
 simp only [nativeCollected,referenceCollected,parts_refinement,slots_refinement,host_refinement]
 cases raw.defaultOnly <;> cases raw.authorEnabled <;> simp [List.append_assoc]

structure GraphNode where
 context : Context
 next : Option Nat
 deriving DecidableEq, Repr

def graphWalk (nodes : List GraphNode) : Nat → Option Nat → Option (List Context)
 | _, none => some []
 | 0, some _ => none
 | fuel+1, some id => do
   let node ← nodes[id]?
   let rest ← graphWalk nodes fuel node.next
   return node.context::rest

inductive GraphPath (nodes : List GraphNode) : Option Nat → List Context → Prop
 | endPath : GraphPath nodes none []
 | step (id : Nat) (node : GraphNode) (rest : List Context)
   (found : nodes[id]? = some node) (tail : GraphPath nodes node.next rest) :
   GraphPath nodes (some id) (node.context::rest)

theorem graph_walk_sound (nodes : List GraphNode) (fuel : Nat)
 (start : Option Nat) (contexts : List Context)
 (h : graphWalk nodes fuel start = some contexts) : GraphPath nodes start contexts := by
 induction fuel generalizing start contexts with
 | zero =>
   cases start
   · simp [graphWalk] at h; subst contexts; exact GraphPath.endPath
   · simp [graphWalk] at h
 | succ fuel ih =>
   cases start with
   | none => simp [graphWalk] at h; subst contexts; exact GraphPath.endPath
   | some id =>
     simp only [graphWalk] at h
     cases hf : nodes[id]? with
     | none => simp [hf] at h
     | some node =>
       cases ht : graphWalk nodes fuel node.next with
       | none => simp [hf,ht] at h
       | some rest =>
         simp [hf,ht] at h
         subst contexts
         exact GraphPath.step id node rest hf (ih _ _ ht)

def fromGraph (nodes : List GraphNode) (start : Option Nat) (raw : RawInput) : Option RawInput := do
 let contexts ← graphWalk nodes (nodes.length+1) start
 return {raw with outerContexts := contexts}

def nativeGraph (nodes : List GraphNode) (start : Option Nat) (raw : RawInput) : Option (List Entry) :=
 (fromGraph nodes start raw).map nativeCollected

def referenceGraph (nodes : List GraphNode) (start : Option Nat) (raw : RawInput) : Option (List Entry) :=
 (fromGraph nodes start raw).map referenceCollected

theorem raw_graph_dispatch (nodes : List GraphNode) (start : Option Nat) (raw : RawInput) :
 nativeGraph nodes start raw = referenceGraph nodes start raw := by
 unfold nativeGraph referenceGraph
 congr 1
 funext r
 exact raw_dispatch_refinement r

#print axioms raw_dispatch_refinement
#print axioms graph_walk_sound
#print axioms raw_graph_dispatch
end ShadowOrder
