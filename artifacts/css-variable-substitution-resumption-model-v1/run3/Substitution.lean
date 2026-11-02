import CompletedPrefix

namespace SubstitutionResumption
open CssSemantics CompletedPrefix

inductive Control (T : Type) where
  | eval (expression : VariableExpr T)
  | await (name : String) (fallback : Option (VariableExpr T))
  | value (tokens : Option (List T))
  deriving DecidableEq, Repr

inductive Frame (T : Type) where
  | left (right : VariableExpr T)
  | right (savedLeft : List T)
  deriving DecidableEq, Repr

structure Machine (T : Type) where
  control : Control T
  frames : List (Frame T)
  reads : List String
  deriving DecidableEq, Repr

inductive Reply (T : Type) where
  | next (machine : Machine T)
  | pending (name : String)
  | done (tokens : Option (List T))
  deriving DecidableEq, Repr

def tick (env : Bindings T) (m : Machine T) : Reply T :=
  match m.control with
  | .eval (.literal tokens) => .next {m with control := .value (some tokens)}
  | .eval (.reference name) => .next {m with control := .await name none}
  | .eval (.fallback name expression) => .next {m with control := .await name (some expression)}
  | .eval (.append left right) =>
      .next {m with control := .eval left, frames := .left right :: m.frames}
  | .await name fallback =>
      match env name with
      | none => .pending name
      | some tokens =>
          let control := match tokens, fallback with
            | none, some expression => Control.eval expression
            | _, _ => Control.value tokens
          .next {m with control, reads := m.reads ++ [name]}
  | .value tokens =>
      match m.frames with
      | [] => .done tokens
      | .left right :: rest =>
          match tokens with
          | none => .next {m with frames := rest}
          | some left => .next {m with control := .eval right, frames := .right left :: rest}
      | .right left :: rest =>
          .next {m with control := .value (tokens.map (left ++ ·)), frames := rest}

def poll (env : Bindings T) (m : Machine T) : Machine T :=
  match tick env m with
  | .next next => next
  | _ => m

def withReads (reads : List String) (r : Resolution T) : Resolution T :=
  ⟨r.tokens, reads ++ r.reads⟩

def continuation (env : Bindings T) : List (Frame T) → Option (List T) → Option (Resolution T)
  | [], tokens => some ⟨tokens, []⟩
  | .left _right :: rest, none => continuation env rest none
  | .left right :: rest, some left => do
      let r ← resolve env right
      (continuation env rest (r.tokens.map (left ++ ·))).map (withReads r.reads)
  | .right left :: rest, tokens => continuation env rest (tokens.map (left ++ ·))

def requestExpr (name : String) : Option (VariableExpr T) → VariableExpr T
  | none => .reference name
  | some expression => .fallback name expression

def remaining (env : Bindings T) (control : Control T) (frames : List (Frame T)) :
    Option (Resolution T) :=
  match control with
  | .value tokens => continuation env frames tokens
  | .eval expression => do
      let r ← resolve env expression
      (continuation env frames r.tokens).map (withReads r.reads)
  | .await name fallback => do
      let r ← resolve env (requestExpr name fallback)
      (continuation env frames r.tokens).map (withReads r.reads)

def completion (env : Bindings T) (m : Machine T) : Option (Resolution T) :=
  (remaining env m.control m.frames).map (withReads m.reads)

theorem prefix_composes (a b : List String) (r : Resolution T) :
    withReads a (withReads b r) = withReads (a ++ b) r := by
  cases r; simp [withReads, List.append_assoc]

theorem tick_preserves_completion (env final : Bindings T) (stable : Extends env final)
    (m next : Machine T) (step : tick env m = .next next) :
    completion final m = completion final next := by
  cases m with
  | mk control frames reads =>
      cases control with
      | eval expression =>
          cases expression with
          | literal tokens =>
              simp only [tick, Reply.next.injEq] at step
              subst next; simp [completion, remaining, resolve, Option.map_map, Function.comp_def, withReads]
          | reference name =>
              simp only [tick, Reply.next.injEq] at step
              subst next; rfl
          | fallback name expression =>
              simp only [tick, Reply.next.injEq] at step
              subst next; rfl
          | append left right =>
              simp only [tick, Reply.next.injEq] at step
              subst next
              cases a : resolve final left with
              | none => simp [completion, remaining, resolve, a]
              | some first =>
                  cases value : first.tokens with
                  | none => simp [completion, remaining, resolve, a, value, continuation]
                  | some tokens =>
                      cases b : resolve final right with
                      | none => simp [completion, remaining, resolve, a, value, continuation, b]
                      | some second =>
                          simp [completion, remaining, resolve, a, value, continuation, b,
                            Option.map_map, Function.comp_def, prefix_composes]
      | await name fallback =>
          cases binding : env name with
          | none => simp [tick, binding] at step
          | some tokens =>
              have fixed := stable name tokens binding
              cases tokens with
              | none =>
                  cases fallback with
                  | none =>
                      simp only [tick, binding, Reply.next.injEq] at step
                      subst next
                      simp [completion, remaining, requestExpr, resolve, fixed,
                        Option.map_map, Function.comp_def, prefix_composes]
                  | some expression =>
                      simp only [tick, binding, Reply.next.injEq] at step
                      subst next
                      cases r : resolve final expression <;>
                        simp [completion, remaining, requestExpr, resolve, fixed, r,
                          Option.map_map, Function.comp_def, prefix_composes]
              | some values =>
                  simp only [tick, binding, Reply.next.injEq] at step
                  subst next
                  cases fallback <;>
                    simp [completion, remaining, requestExpr, resolve, fixed,
                      Option.map_map, Function.comp_def, prefix_composes]
      | value tokens =>
          cases frames with
          | nil => simp [tick] at step
          | cons frame rest =>
              cases frame with
              | left right =>
                  cases tokens with
                  | none =>
                      simp only [tick, Reply.next.injEq] at step
                      subst next; rfl
                  | some left =>
                      simp only [tick, Reply.next.injEq] at step
                      subst next; rfl
              | right left =>
                  simp only [tick, Reply.next.injEq] at step
                  subst next; rfl

theorem poll_preserves_completion (env final : Bindings T) (stable : Extends env final)
    (m : Machine T) : completion final (poll env m) = completion final m := by
  cases step : tick env m with
  | next next => simpa [poll, step] using (tick_preserves_completion env final stable m next step).symm
  | pending name => simp [poll, step]
  | done tokens => simp [poll, step]

def polls : List (Bindings T) → Machine T → Machine T
  | [], m => m
  | env :: rest, m => polls rest (poll env m)

theorem arbitrary_pauses_and_completions_preserve_result
    (environments : List (Bindings T)) (final : Bindings T) (m : Machine T)
    (stable : ∀ env ∈ environments, Extends env final) :
    completion final (polls environments m) = completion final m := by
  induction environments generalizing m with
  | nil => rfl
  | cons env rest ih =>
      simp only [polls]
      rw [ih (poll env m) (fun e h => stable e (by simp [h]))]
      exact poll_preserves_completion env final (stable env (by simp)) m

def start (expression : VariableExpr T) : Machine T := ⟨.eval expression, [], []⟩

theorem start_completion_is_existing_resolver (env : Bindings T) (expression : VariableExpr T) :
    completion env (start expression) = resolve env expression := by
  cases h : resolve env expression with
  | none => simp [completion, start, remaining, h]
  | some r => cases r; simp [completion, start, remaining, h, continuation, withReads]

theorem done_refines_existing_resolver (environments : List (Bindings T))
    (final : Bindings T) (expression : VariableExpr T) (tokens : Option (List T))
    (stable : ∀ env ∈ environments, Extends env final)
    (done : tick final (polls environments (start expression)) = .done tokens) :
    resolve final expression = some ⟨tokens, (polls environments (start expression)).reads⟩ := by
  have preserved := arbitrary_pauses_and_completions_preserve_result environments final (start expression) stable
  rw [start_completion_is_existing_resolver] at preserved
  generalize machine : polls environments (start expression) = m at done preserved ⊢
  cases m with
  | mk control frames reads =>
      cases control with
      | eval expression => cases expression <;> simp [tick] at done
      | await name fallback =>
          cases binding : final name <;> simp [tick, binding] at done
      | value value =>
          cases frames with
          | cons frame rest => cases frame <;> cases value <;> simp [tick] at done
          | nil =>
              simp only [tick, Reply.done.injEq] at done
              subst tokens
              simpa [completion, remaining, continuation, withReads] using preserved.symm

theorem pending_poll_preserves_entire_machine (env : Bindings T) (m : Machine T) (name : String)
    (waiting : tick env m = .pending name) : poll env m = m := by
  simp [poll, waiting]

theorem done_poll_is_idempotent (env : Bindings T) (m : Machine T) (tokens : Option (List T))
    (done : tick env m = .done tokens) : poll env (poll env m) = m := by
  simp [poll, done]

theorem tick_read_accounting (env : Bindings T) (m next : Machine T)
    (step : tick env m = .next next) :
    next.reads = m.reads ∨ ∃ name fallback, m.control = .await name fallback ∧
      next.reads = m.reads ++ [name] := by
  cases m with
  | mk control frames reads =>
      cases control with
      | eval expression =>
          cases expression <;> simp only [tick, Reply.next.injEq] at step <;>
            subst next <;> exact Or.inl rfl
      | await name fallback =>
          cases binding : env name with
          | none => simp [tick, binding] at step
          | some tokens =>
              simp only [tick, binding, Reply.next.injEq] at step
              subst next; exact Or.inr ⟨name, fallback, rfl, rfl⟩
      | value tokens =>
          cases frames with
          | nil => simp [tick] at step
          | cons frame rest =>
              cases frame with
              | left right =>
                  cases tokens <;> simp only [tick, Reply.next.injEq] at step <;>
                    subst next <;> exact Or.inl rfl
              | right left =>
                  simp only [tick, Reply.next.injEq] at step
                  subst next; exact Or.inl rfl

theorem consumed_request_moves_control (env : Bindings T) (name : String)
    (fallback : Option (VariableExpr T)) (frames : List (Frame T)) (reads : List String)
    (value : Option (List T)) (settled : env name = some value) :
    ∃ control, control ≠ Control.await name fallback ∧
      tick env ⟨.await name fallback, frames, reads⟩ =
        .next ⟨control, frames, reads ++ [name]⟩ := by
  cases value with
  | some tokens => exact ⟨.value (some tokens), by simp, by simp [tick, settled]⟩
  | none =>
      cases fallback with
      | none => exact ⟨.value none, by simp, by simp [tick, settled]⟩
      | some expression => exact ⟨.eval expression, by simp, by simp [tick, settled]⟩

def run (fuel : Nat) (env : Bindings T) (m : Machine T) : Machine T :=
  match fuel with
  | 0 => m
  | n + 1 => run n env (poll env m)

def env : Bindings Nat := fun name =>
  if name == "left" then some (some [20])
  else if name == "right" then some (some [30])
  else if name == "invalid" then some none
  else none
def leftOnly : Bindings Nat := fun name => if name == "left" then some (some [20]) else none
def pair : VariableExpr Nat := .append (.reference "left") (.reference "right")
def pausedRight : Machine Nat := ⟨.await "right" none, [.right [20]], ["left"]⟩
def pausedLeft : Machine Nat := ⟨.await "left" none, [.left (.reference "right")], []⟩
def fallback : VariableExpr Nat := .fallback "invalid" (.reference "right")

theorem pause_right_keeps_left_and_exact_log :
    run 6 leftOnly (start pair) = pausedRight ∧
    run 20 leftOnly pausedRight = pausedRight ∧
    run 6 env pausedRight = ⟨.value (some [20, 30]), [], ["left", "right"]⟩ := by decide

theorem pause_left_keeps_unvisited_right :
    run 20 (fun _ => none) (start pair) = pausedLeft := by decide

theorem fallback_wait_retains_negative_read :
    run 3 (fun name => if name == "invalid" then some none else none) (start fallback) =
      ⟨.await "right" none, [], ["invalid"]⟩ ∧
    run 10 env (start fallback) = ⟨.value (some [30]), [], ["invalid", "right"]⟩ := by decide

theorem pending_does_not_select_fallback :
    run 20 (fun _ => none) (start fallback) = ⟨.await "invalid" (some (.reference "right")), [], []⟩ := by decide

theorem alias_completion_resumes_same_request :
    let paused : Machine Nat := ⟨.await "alias" none, [.right [20]], ["left"]⟩
    run 20 env paused = paused ∧
    run 4 (complete env "alias" (some [30])) paused =
      ⟨.value (some [20, 30]), [], ["left", "alias"]⟩ := by decide

theorem unused_fallback_is_never_requested :
    run 10 env (start (.fallback "left" (.reference "unknown"))) =
      ⟨.value (some [20]), [], ["left"]⟩ := by decide

end SubstitutionResumption
