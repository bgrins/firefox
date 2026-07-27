# Feature-gated codex tools: findings and plan

Deep dive into the codex tools that are feature-flagged or config-gated off
by default at the pinned rust-v0.145.0, and what's worth enabling for the
harness. Citations verified at the tag.

## How features are enabled

The `Feature` registry lives in `codex-rs/features/src/lib.rs` (enum at
line 83). Features are toggled by key in a **`[features]` table in
config.toml**; six features (`code_mode`, `multi_agent_v2`, `token_budget`,
`rollout_budget`, `current_time_reminder`, `network_proxy`) also accept a
config sub-table with an `enabled` field.

Two cross-cutting hazards:

- Most flags are `Stage::UnderDevelopment`; enabling one emits a `warning`
  notification that our UI renders in the chat. Set
  `suppress_unstable_features_warning = true` at config.toml top level.
- Our fail-closed server-request default degrades gracefully for the new
  request methods below: the app-server catches client errors and
  synthesizes an *empty* response rather than wedging the turn
  (`app-server/src/bespoke_event_handling.rs:1616-1647`, `:1831-1846`). No
  hang — but the model silently gets nothing, so don't enable a tool
  without handling its request. `serverRequest/resolved` fires when a
  pending request is resolved elsewhere (e.g. turn interrupt) — UI should
  dismiss its prompt on that.

Outgoing server→client requests are not filtered by the `experimentalApi`
capability; we already pass it on initialize.

## 1. request_user_input — enable now (implemented)

A blocking tool that pauses the turn and asks the user 1-3 structured
multiple-choice questions
(`core/src/tools/handlers/request_user_input_spec.rs`):

- `questions`: array of `{ id, header (<=12 chars), question, options:
  [{label, description}] }` — 2-3 mutually exclusive options per question;
  the model is told not to include an "Other" option because **the client
  is expected to add a free-form "Other" automatically** (the handler
  force-sets `is_other = true`, spec.rs:119-121).
- `autoResolutionMs` (optional, clamped 60-240s): for questions where
  "continue with best judgment" is acceptable.

Gating has three layers:

1. Config gate `[tools.experimental_request_user_input].enabled` —
   **defaults to TRUE when absent** (`core/src/config/mod.rs:2505-2510`),
   so the tool is already registered in our sessions.
2. Collaboration-mode gate — at this tag the tool is allowed in Plan mode
   only (`protocol/src/config_types.rs:648-650`); Default mode (ours) is
   added by `Feature::DefaultModeRequestUserInput`
   (`default_mode_request_user_input`) — **this flag is the real switch
   for us** (`tools/src/tool_config.rs:38-47`).
3. Root thread only; not experimental-API-gated on the wire.

Protocol flow:

1. Core emits the request and **waits with no core-side timeout**
   (auto-resolution is entirely the client's job,
   `core/src/session/mod.rs:2512-2547`).
2. Server→client request `item/tool/requestUserInput`
   (`app-server-protocol/src/protocol/v2/item.rs:1621-1629`):
   `{ threadId, turnId, itemId, questions: [{ id, header, question,
   isOther, isSecret, options: [{label, description}] }],
   autoResolutionMs }`.
3. Client responds `{ answers: { "<question_id>": { answers: ["<label or
   free text>", "...extra notes"] } } }`. Multiple strings per question
   allowed. The reference TUI auto-resolves with an **empty answers map**
   when the countdown expires.
4. Client error / denial → empty answers map → model continues with best
   judgment. Turn interrupt → tool errors "cancelled".

Config:

```toml
suppress_unstable_features_warning = true

[features]
default_mode_request_user_input = true
```

Client work: allow `item/tool/requestUserInput` in
`AgentService._onServerRequest`, render question cards with option
buttons + an "Other" free-text input, host-side timeout answering
`{answers:{}}`, journal the exchange for resume. Follow-ups: handle
`serverRequest/resolved` to retire stale cards; respect `isSecret`.

Verdict: **the single biggest UX gap** — the model currently asks
questions in prose and the turn just ends.

## 2. Token budget tools — enable now (implemented)

`[features.token_budget]` registers `new_context` and
`get_context_remaining` (`spec_plan.rs:712-715`); zero client work (no
server→client traffic).

- `get_context_remaining`: remaining tokens in the window, or null.
- `new_context`: deliberately starts a fresh context window without
  summarizing — the model is expected to have externalized state to files
  first, which our persistent `/workspace` supports well.
- Sub-config: `reminder_threshold_tokens` + `reminder_message_template`
  (`{n_remaining}`) inject a wrap-up reminder when remaining tokens cross
  the threshold.

```toml
[features.token_budget]
enabled = true
reminder_threshold_tokens = 16000
```

Verdict: cheapest win, especially for the 32k ollama configuration.

## 3. current_time / sleep — later

`[features.current_time_reminder]` registers `clock.curr_time` (UTC time
string + periodic time reminders in context) and, with `sleep_tool =
true`, `clock.sleep` (`duration_ms` up to 12h, interrupted by new input).
No client work with the default clock. **Never set `clock_source =
"external"`** — that makes the sidecar issue `currentTime/read`
server→client requests our fail-closed client would error, breaking both
tools.

Verdict: time-awareness is mildly useful (reasoning about "recent" against
places.sqlite timestamps); nothing needs sleep/polling semantics yet.

## 4. wait_for_environment (`deferred_executor`) — later

Lets turns start while an environment is still connecting; the model gets
`wait_for_environment` to block until ready. Would buy first-message
latency (start the turn while the VM boots), but our AgentService fully
boots the VM and polls `exec("true")` *before* `thread/start`, so
environments are never "starting". Enabling means re-plumbing a
security-sensitive path ("fail closed if VM can't run") for a
first-turn-only win.

## 5. request_permissions — never (current architecture)

Exists so a *sandboxed* codex can escalate filesystem/network permissions
without flipping approvalPolicy. Our threads run
`sandbox: "danger-full-access"` because the micro-VM is the boundary —
there is no codex-side sandbox left to widen, and VM network is governed
by the host proxy allowlist, which codex permissions don't touch. A
"request a new proxy allowlist entry" flow would be better built as a
harness dynamic tool.

## 6. Plugin / tool-suggest ecosystem — never

`tool_suggest`/`apps`/`plugins` are default-enabled Stable features, but
candidates only materialize with ChatGPT-account auth against OpenAI's
backend (`core/src/session/turn_context.rs:222-231`) plus OpenAI's
connector services. With OpenRouter/ollama + API-key auth the candidate
list is always empty and the tools are never registered. No config
changes this. Our equivalent extension point is `dynamicTools`, which we
already use.
