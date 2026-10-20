import Std

namespace CssProtocol

inductive Phase where
  | intrinsic | used
  deriving DecidableEq, Repr

structure SizeKey where
  subject : Nat
  owner : Nat
  epoch : Nat
  phase : Phase
  deriving DecidableEq, Repr

inductive Basis where
  | initial
  | definite (px : Nat)
  deriving DecidableEq, Repr

structure SampleKey where
  timeline : Nat
  epoch : Nat
  deriving DecidableEq, Repr

inductive Request : Type → Type 1 where
  | size (key : SizeKey) : Request Basis
  | sample (key : SampleKey) : Request (Option Nat)

abbrev PackedRequest := Sigma Request
abbrev Provider := {α : Type} → Request α → α

inductive Plan (α : Type) : Type 1 where
  | done : α → Plan α
  | ask {β : Type} : Request β → (β → Plan α) → Plan α

def run (provider : Provider) : Plan α → α × List PackedRequest
  | .done value => (value, [])
  | .ask request next =>
    let reply := run provider (next (provider request))
    (reply.1, ⟨_, request⟩ :: reply.2)

def AgreesOn (left right : Provider) (trace : List PackedRequest) : Prop :=
  ∀ (α : Type) (request : Request α),
    (⟨α, request⟩ : PackedRequest) ∈ trace → left request = right request

theorem actual_footprint_sufficient (plan : Plan α) (left right : Provider)
    (agree : AgreesOn left right (run left plan).2) :
    run left plan = run right plan := by
  induction plan with
  | done value => rfl
  | @ask β request next ih =>
    have head : left request = right request := agree β request (by simp [run])
    have tail : AgreesOn left right (run left (next (left request))).2 := by
      intro γ query member
      exact agree γ query (by simp [run, member])
    have rest := ih (left request) tail
    simpa only [run, head] using congrArg (fun result => (result.1, ⟨β, request⟩ :: result.2)) rest

def bind (first : Plan α) (next : α → Plan β) : Plan β :=
  match first with
  | .done value => next value
  | .ask request continuation => .ask request (fun answer => bind (continuation answer) next)

theorem run_bind (first : Plan α) (next : α → Plan β) (provider : Provider) :
    run provider (bind first next) =
      ((run provider (next (run provider first).1)).1,
       (run provider first).2 ++ (run provider (next (run provider first).1)).2) := by
  induction first with
  | done value => simp [bind, run]
  | ask request continuation ih => simp [bind, run, ih]

end CssProtocol
