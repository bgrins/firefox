import Prefix

namespace CompletedPrefix
open CssSemantics SelectedDeclaration PreparationStability

abbrev Bindings (T : Type) := String → Option (Option (List T))

def Extends (old newer : Bindings T) : Prop :=
  ∀ name value, old name = some value → newer name = some value

structure Resolution (T : Type) where
  tokens : Option (List T)
  reads : List String
  deriving DecidableEq, Repr

def resolve (env : Bindings T) : VariableExpr T → Option (Resolution T)
  | .literal tokens => some ⟨some tokens, []⟩
  | .reference name => (env name).map fun tokens => ⟨tokens, [name]⟩
  | .fallback name expression =>
      match env name with
      | none => none
      | some (some tokens) => some ⟨some tokens, [name]⟩
      | some none => (resolve env expression).map fun r => ⟨r.tokens, name :: r.reads⟩
  | .append left right => do
      let a ← resolve env left
      match a.tokens with
      | none => some a
      | some tokens =>
          let b ← resolve env right
          some ⟨b.tokens.map (tokens ++ ·), a.reads ++ b.reads⟩

theorem completed_resolution_stable (old newer : Bindings T)
    (preserved : Extends old newer) (expression : VariableExpr T)
    (r : Resolution T) (done : resolve old expression = some r) :
    resolve newer expression = some r := by
  induction expression generalizing r with
  | literal tokens => exact done
  | reference name =>
      cases h : old name with
      | none => simp [resolve, h] at done
      | some value => simpa [resolve, h, preserved name value h] using done
  | fallback name expression ih =>
      cases h : old name with
      | none => simp [resolve, h] at done
      | some value =>
          cases value with
          | some tokens => simpa [resolve, h, preserved name (some tokens) h] using done
          | none =>
              cases inner : resolve old expression with
              | none => simp [resolve, h, inner] at done
              | some result =>
                  simpa [resolve, preserved name none h, ih result inner] using
                    (show some ⟨result.tokens, name :: result.reads⟩ = some r by
                      simpa [resolve, h, inner] using done)
  | append left right ihLeft ihRight =>
      cases a : resolve old left with
      | none => simp [resolve, a] at done
      | some first =>
          have firstStable := ihLeft first a
          cases tokens : first.tokens with
          | none => simpa [resolve, firstStable, tokens] using
              (show some first = some r by simpa [resolve, a, tokens] using done)
          | some values =>
              cases b : resolve old right with
              | none => simp [resolve, a, tokens, b] at done
              | some second =>
                  simpa [resolve, firstStable, tokens, ihRight second b] using
                    (show some ⟨second.tokens.map (values ++ ·), first.reads ++ second.reads⟩ = some r by
                      simpa [resolve, a, tokens, b] using done)

def projected (env : Bindings T) (name : String) : Option (List T) :=
  (env name).join

theorem completed_resolution_matches_substitution (env : Bindings T)
    (expression : VariableExpr T) (r : Resolution T)
    (done : resolve env expression = some r) :
    expression.substitute (projected env) = r.tokens := by
  induction expression generalizing r with
  | literal tokens => simpa [resolve, VariableExpr.substitute] using congrArg (Option.map Resolution.tokens) done
  | reference name =>
      cases h : env name with
      | none => simp [resolve, h] at done
      | some value =>
          have result : r = ⟨value, [name]⟩ := by simpa [resolve, h] using done.symm
          subst r; simp [VariableExpr.substitute, projected, h]
  | fallback name expression ih =>
      cases h : env name with
      | none => simp [resolve, h] at done
      | some value =>
          cases value with
          | some tokens =>
              have result : r = ⟨some tokens, [name]⟩ := by simpa [resolve, h] using done.symm
              subst r; simp [VariableExpr.substitute, projected, h]
          | none =>
              cases inner : resolve env expression with
              | none => simp [resolve, h, inner] at done
              | some result =>
                  have eq : r = ⟨result.tokens, name :: result.reads⟩ := by
                    simpa [resolve, h, inner] using done.symm
                  subst r; simpa [VariableExpr.substitute, projected, h] using ih result inner
  | append left right ihLeft ihRight =>
      cases a : resolve env left with
      | none => simp [resolve, a] at done
      | some first =>
          cases tokens : first.tokens with
          | none =>
              have result : r = first := by simpa [resolve, a, tokens] using done.symm
              subst r; simp [VariableExpr.substitute, ihLeft first a, tokens]
          | some values =>
              cases b : resolve env right with
              | none => simp [resolve, a, tokens, b] at done
              | some second =>
                  have result : r = ⟨second.tokens.map (values ++ ·), first.reads ++ second.reads⟩ := by
                    simpa [resolve, a, tokens, b] using done.symm
                  subst r
                  simp only [VariableExpr.substitute, ihLeft first a, tokens, ihRight second b]
                  cases second.tokens <;> rfl

inductive Token where
  | absolute (value : Nat)
  | revert (state : Nat)
  | unsupported
  deriving DecidableEq, Repr

abbrev Decl := SizePrefix.Declaration Nat Nat String
abbrev Expressions := Decl → VariableExpr Token

def decode : Option (List Token) → Next Nat Nat
  | some [.absolute n] => .terminal (some n)
  | some [.revert state] => .rollback state
  | _ => .terminal none

def evaluate (env : Bindings Token) (expressions : Expressions)
    (_state : Nat) (d : Decl) : Evaluation Nat Nat String :=
  if d.dynamic then
    match resolve env (expressions d) with
    | none => ⟨.blocked, []⟩
    | some result => ⟨decode result.tokens, result.reads⟩
  else d.staticEvaluation

def literalReferenceCertificate (env : Bindings Token) (expression : VariableExpr Token) : Bool :=
  match expression with
  | .reference name =>
      match env name with
      | some (some [.absolute _]) => true
      | _ => false
  | _ => false

def dynamicCertificate (env : Bindings Token) (expression : VariableExpr Token) : Bool :=
  (resolve env expression).isSome

theorem admitted_dynamic_has_completed_resolution (env : Bindings Token)
    (expression : VariableExpr Token) (accepted : dynamicCertificate env expression = true) :
    ∃ r, resolve env expression = some r := by
  cases h : resolve env expression with
  | none => simp [dynamicCertificate, h] at accepted
  | some r => exact ⟨r, h⟩

theorem admitted_evaluation_stable (old newer : Bindings Token)
    (preserved : Extends old newer) (expressions : Expressions) (state : Nat) (d : Decl)
    (accepted : d.dynamic = false ∨ dynamicCertificate old (expressions d) = true) :
    evaluate newer expressions state d = evaluate old expressions state d := by
  rcases accepted with static | dynamic
  · simp [evaluate, static]
  · obtain ⟨r, done⟩ := admitted_dynamic_has_completed_resolution old (expressions d) dynamic
    simp [evaluate, done, completed_resolution_stable old newer preserved (expressions d) r done]

def certificate (base : Bool) (allows : Nat → Decl → Bool)
    (env : Bindings Token) (expressions : Expressions) (state : Nat) : List Decl → Bool
  | [] => true
  | d :: rest =>
      if d.needsBase then false else
      if SizePrefix.eligible base allows state d then
        if d.dynamic && !dynamicCertificate env (expressions d) then false else
        match (evaluate env expressions state d).next with
        | .rollback next => certificate base allows env expressions next rest
        | _ => true
      else certificate base allows env expressions state rest

theorem accepted_head_evaluation (base : Bool) (allows : Nat → Decl → Bool)
    (old newer : Bindings Token) (preserved : Extends old newer) (expressions : Expressions)
    (state : Nat) (d : Decl) (rest : List Decl)
    (accepted : certificate base allows old expressions state (d :: rest) = true)
    (yes : SizePrefix.eligible base allows state d = true) :
    evaluate newer expressions state d = evaluate old expressions state d := by
  apply admitted_evaluation_stable old newer preserved expressions state d
  cases gate : d.needsBase <;> simp_all [certificate]
  cases dynamic : d.dynamic <;> simp_all [certificate]

theorem certificate_derives_reached_agreement
    (base : Bool) (allows : Nat → Decl → Bool) (old newer : Bindings Token)
    (preserved : Extends old newer) (expressions : Expressions)
    (state : Nat) (decls : List Decl)
    (accepted : certificate base allows old expressions state decls = true) :
    ∀ point ∈ visited (SizePrefix.eligible base allows) (evaluate old expressions) state decls,
      agreesAt (SizePrefix.eligible base allows) (SizePrefix.eligible true allows)
        (evaluate old expressions) (evaluate newer expressions) point := by
  induction decls generalizing state with
  | nil => simp [visited]
  | cons d rest ih =>
      have ungated : d.needsBase = false := by
        cases h : d.needsBase <;> simp_all [certificate]
      have sameEligible := SizePrefix.ungated_eligibility base allows state d ungated
      by_cases yes : SizePrefix.eligible base allows state d = true
      · have same := accepted_head_evaluation base allows old newer preserved expressions state d rest accepted yes
        have safe : (d.dynamic && !dynamicCertificate old (expressions d)) = false := by
          cases h : d.dynamic && !dynamicCertificate old (expressions d) <;> simp_all [certificate]
        intro point member
        cases outcome : (evaluate old expressions state d).next with
        | rollback next =>
            have tailAccepted : certificate base allows old expressions next rest = true := by
              simpa [certificate, ungated, yes, safe, outcome] using accepted
            have members : point = (state, d) ∨ point ∈ visited (SizePrefix.eligible base allows)
                (evaluate old expressions) next rest := by simpa [visited, yes, outcome] using member
            rcases members with head | tail
            · subst point; exact ⟨sameEligible, fun _ => same⟩
            · exact ih next tailAccepted point tail
        | terminal value =>
            have head : point = (state, d) := by simpa [visited, yes, outcome] using member
            subst point; exact ⟨sameEligible, fun _ => same⟩
        | blocked =>
            have head : point = (state, d) := by simpa [visited, yes, outcome] using member
            subst point; exact ⟨sameEligible, fun _ => same⟩
      · have no : SizePrefix.eligible base allows state d = false := Bool.eq_false_iff.mpr yes
        have tailAccepted : certificate base allows old expressions state rest = true := by
          simpa [certificate, ungated, no] using accepted
        intro point member
        have members : point = (state, d) ∨ point ∈ visited (SizePrefix.eligible base allows)
            (evaluate old expressions) state rest := by simpa [visited, no] using member
        rcases members with head | tail
        · subst point; exact ⟨sameEligible, by simp [no]⟩
        · exact ih state tailAccepted point tail

theorem checked_selection_and_reads_stable
    (base : Bool) (allows : Nat → Decl → Bool) (old newer : Bindings Token)
    (preserved : Extends old newer) (expressions : Expressions)
    (state : Nat) (decls : List Decl)
    (accepted : certificate base allows old expressions state decls = true) :
    scan (SizePrefix.eligible true allows) (evaluate newer expressions) state decls =
      scan (SizePrefix.eligible base allows) (evaluate old expressions) state decls := by
  apply scan_eq_of_reached_agreement
  exact certificate_derives_reached_agreement base allows old newer preserved expressions state decls accepted

theorem visited_eq_of_reached_agreement
    (eligible eligible' : S → D → Bool) (evaluate evaluate' : S → D → Evaluation S V E)
    (state : S) (decls : List D)
    (stable : ∀ point ∈ visited eligible evaluate state decls,
      agreesAt eligible eligible' evaluate evaluate' point) :
    visited eligible' evaluate' state decls = visited eligible evaluate state decls := by
  induction decls generalizing state with
  | nil => rfl
  | cons d rest ih =>
      obtain ⟨sameEligible, sameEvaluation⟩ := stable (state, d) (by simp [visited])
      by_cases yes : eligible state d = true
      · have same := sameEvaluation yes
        cases step : (evaluate state d).next with
        | terminal value => simp [visited, sameEligible, yes, same, step]
        | blocked => simp [visited, sameEligible, yes, same, step]
        | rollback next =>
            have tail : ∀ point ∈ visited eligible evaluate next rest,
                agreesAt eligible eligible' evaluate evaluate' point := by
              intro point member; exact stable point (by simp [visited, yes, step, member])
            simpa [visited, sameEligible, yes, same, step] using congrArg (List.cons (state, d)) (ih next tail)
      · have no : eligible state d = false := Bool.eq_false_iff.mpr yes
        have tail : ∀ point ∈ visited eligible evaluate state rest,
            agreesAt eligible eligible' evaluate evaluate' point := by
          intro point member; exact stable point (by simp [visited, no, member])
        simpa [visited, sameEligible, no] using congrArg (List.cons (state, d)) (ih state tail)

theorem checked_visited_rollback_trace_stable
    (base : Bool) (allows : Nat → Decl → Bool) (old newer : Bindings Token)
    (preserved : Extends old newer) (expressions : Expressions)
    (state : Nat) (decls : List Decl)
    (accepted : certificate base allows old expressions state decls = true) :
    visited (SizePrefix.eligible true allows) (evaluate newer expressions) state decls =
      visited (SizePrefix.eligible base allows) (evaluate old expressions) state decls := by
  apply visited_eq_of_reached_agreement
  exact certificate_derives_reached_agreement base allows old newer preserved expressions state decls accepted

def size (n : Nat) : Bindings Token := fun name =>
  if name == "--size" then some (some [.absolute n]) else none
def pending : Bindings Token := fun _ => none
def invalid : Bindings Token := fun _ => some none
def expr (_ : Decl) : VariableExpr Token := .reference "--size"
def fallback (_ : Decl) : VariableExpr Token := .fallback "--size" (.literal [.absolute 30])
def dynamic : Decl := ⟨false, true, true, ⟨.blocked, []⟩⟩
def literal (n : Nat) (gate : Bool := false) : Decl :=
  ⟨gate, true, false, ⟨.terminal (some n), ["literal"]⟩⟩
def rollback : Decl := ⟨false, true, false, ⟨.rollback 1, ["rollback"]⟩⟩
def allow (s : Nat) (d : Decl) : Bool := !(s == 1 && d.staticEvaluation.reads == ["skip"])
def skipped : Decl := ⟨false, true, true, ⟨.blocked, ["skip"]⟩⟩

theorem literal_variable_twenty_and_thirty :
    certificate false allow (size 20) expr 0 [dynamic] = true ∧
    certificate false allow (size 30) expr 0 [dynamic] = true ∧
    (scan (SizePrefix.eligible false allow) (evaluate (size 20) expr) 0 [dynamic]).finish = .terminal (some 20) ∧
    (scan (SizePrefix.eligible false allow) (evaluate (size 30) expr) 0 [dynamic]).finish = .terminal (some 30) := by decide

theorem pending_is_not_invalid_fallback :
    resolve pending (fallback dynamic) = none ∧
    resolve invalid (fallback dynamic) = some ⟨some [.absolute 30], ["--size"]⟩ := by decide

theorem narrow_literal_classifier_excludes_fallback_and_revert :
    literalReferenceCertificate (size 20) (fallback dynamic) = false ∧
    literalReferenceCertificate (fun _ => some (some [.revert 1])) (expr dynamic) = false := by decide

theorem static_rollback_keeps_dynamic_reads :
    certificate false allow (size 20) expr 0 [rollback, skipped, dynamic, literal 99 true] = true ∧
    (scan (SizePrefix.eligible false allow) (evaluate (size 20) expr) 0
      [rollback, skipped, dynamic, literal 99 true]).reads = ["rollback", "--size"] := by decide

theorem higher_gate_rejected_lower_gate_ignored :
    certificate false allow (size 20) expr 0 [literal 99 true, dynamic] = false ∧
    certificate false allow (size 20) expr 0 [dynamic, literal 99 true] = true := by decide

theorem changing_completed_binding_changes_selection :
    (scan (SizePrefix.eligible false allow) (evaluate (size 20) expr) 0 [dynamic]).finish ≠
      (scan (SizePrefix.eligible false allow) (evaluate (size 30) expr) 0 [dynamic]).finish := by decide

def rollbackEnv : Bindings Token := fun name =>
  if name == "--roll" then some (some [.revert 1])
  else if name == "--missing" then some none
  else if name == "--alias" then some (some [.absolute 30])
  else none

def rollbackExpr (d : Decl) : VariableExpr Token :=
  if d.staticEvaluation.reads == ["roll"] then .reference "--roll"
  else .fallback "--missing" (.reference "--alias")
def dynamicRoll : Decl := ⟨false, true, true, ⟨.blocked, ["roll"]⟩⟩

theorem dynamic_rollback_and_selected_fallback_trace :
    certificate false allow rollbackEnv rollbackExpr 0 [dynamicRoll, skipped, dynamic] = true ∧
    scan (SizePrefix.eligible false allow) (evaluate rollbackEnv rollbackExpr) 0
      [dynamicRoll, skipped, dynamic] =
      ⟨.terminal (some 30), [dynamicRoll, dynamic], ["--roll", "--missing", "--alias"]⟩ := by decide

theorem unused_fallback_can_remain_pending :
    dynamicCertificate (size 20) (.fallback "--size" (.reference "--unknown")) = true ∧
    resolve (size 20) (.fallback "--size" (.reference "--unknown")) =
      some ⟨some [.absolute 20], ["--size"]⟩ := by decide

end CompletedPrefix
