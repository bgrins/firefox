import Std
namespace ShadowOrder
inductive Action where
 | value (token : Nat)
 | initial
 | inherit
 | unset
 | revertOrigin
 | revertLayer
 | revertRule
 | invalid
 deriving DecidableEq, Repr
structure Declaration where
 property : Nat
 important : Bool
 action : Action
 deriving DecidableEq, Repr
structure Rule where
 tree : Nat
 source : Nat
 layer : Nat
 specificity : Nat
 proximity : Nat
 sourceOrder : Nat
 flags : Nat
 declarations : List Declaration
 deriving DecidableEq, Repr
structure Entry where
 rule : Rule
 origin : Nat
 order : Int
 deriving DecidableEq, Repr
structure PartRule where
 name : Nat
 rule : Rule
 deriving DecidableEq, Repr
structure Context where
 identity : Nat
 mapPresent : Bool
 rules : List PartRule
 exports : List (Nat × List Nat)
 deriving DecidableEq, Repr

def exported (c : Context) (parts : List Nat) : List Nat :=
 parts.flatMap fun p => ((c.exports.find? fun e => e.1 == p).map Prod.snd).getD []

def matching (c : Context) (parts : List Nat) : List Rule :=
 parts.flatMap fun p => (c.rules.filter fun r => r.name == p).map PartRule.rule

def atOrder (order : Int) (rules : List Rule) : List Entry :=
 rules.map fun rule => ⟨rule,3,order⟩

end ShadowOrder
