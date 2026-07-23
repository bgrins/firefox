# Spike: reusing Smart Window's VIEW layer in about:harness

Status: research spike, no code. Companion to `smartwindow-tools-spike.md`
(which covered Smart Window's TOOLS); this one covers the chat UI: message
rendering, markdown, streaming, tool/approval presentation, and the "smart
bar" compose input with @-tab-mentions. All paths/symbols verified against
this tree (branch `harness`).

## 1. How Smart Window's UI is put together

Everything is lit (`MozLitElement` from `chrome://global/content/lit-utils.mjs`)
plus two non-aiwindow building blocks. Three layers:

1. **Chrome orchestrator**: `<ai-window>` in
   `browser/components/aiwindow/ui/components/ai-window/ai-window.mjs`
   (~2950 lines). Runs in the chrome document (`ui/content/aiWindow.html` /
   sidebar). Owns a `ChatConversation`, creates the smartbar, and embeds a
   separate `<browser remoteType="privilegedabout" src="about:aichatcontent">`
   for the transcript.
2. **Transcript document**: `ui/content/aiChatContent.html` hosting
   `<ai-chat-content>` (`ui/components/ai-chat-content/ai-chat-content.mjs`,
   ~1570 lines). Parent and content talk through JSWindowActors
   (`ui/actors/AIChatContentParent.sys.mjs` / `AIChatContentChild.sys.mjs`).
   Crucially, the child actor's only job is to re-dispatch parent messages as
   DOM CustomEvents on the element (`aiChatContentActor:message`,
   `:seen-urls`, `:set-generating`, `:history-results`, ...) and relay
   content events back (`AIChatContent:DispatchAction`, `:OpenLink`,
   `:ToolUIUpdate`, ...). The element itself never touches actors.
3. **The smartbar**: `<moz-smartbar>` is `SmartbarInput` in
   `browser/components/urlbar/content/SmartbarInput.mjs` (~7730 lines) — a
   full urlbar variant (UrlbarView, providers, search modes, intent routing
   chat/search/navigate). Its *editor* is `<moz-multiline-editor>`
   (`browser/components/multilineeditor/multiline-editor.mjs`, ProseMirror,
   third_party bundle at
   `chrome://browser/content/multilineeditor/prosemirror.bundle.mjs`), wired
   up by `createEditor()` / `setupMentionsPlugin()` in
   `browser/components/urlbar/content/SmartbarInputUtils.mjs`.

Backend: `ai-window.mjs#fetchAIResponse` → `Chat.fetchWithHistory()`
(`aiwindow/models/Chat.sys.mjs`): an OpenAI chat-completions streaming loop
with locally executed tools, over `conversation.runWithGenerator()` backed by
`openAIEngine` (`models/openAIEngine.sys.mjs`, endpoint pref
`browser.smartwindow.endpoint`, built via
`models/PromptLoader.sys.mjs buildEngineForFeature`). `ChatConversation`
(`ui/modules/ChatConversation.sys.mjs`, extends `models/Conversation.sys.mjs`)
emits `chat-conversation:message-update` / `:message-complete` and persists
via `ui/modules/ChatStore.sys.mjs` (sqlite through `ChatSql.sys.mjs`).

## 2. Component inventory

Chrome URLs come from `browser/components/aiwindow/ui/jar.mn` (e.g.
`chrome://browser/content/aiwindow/components/ai-chat-message.mjs`). Most
components have `.stories.mjs` files, i.e. they render standalone.

| Component / module | File (under `browser/components/`) | Contract | Verdict |
| --- | --- | --- | --- |
| `parseMarkdown` | `aiwindow/ui/modules/ChatMarkdownParser.mjs` (62 lines) | pure function over MarkdownIt from the prosemirror bundle; wraps tables in `<ai-chat-table>` | **reusable now** |
| `<ai-chat-message>` | `aiwindow/ui/components/ai-chat-message/ai-chat-message.mjs` | plain props: `role`, `message`, `messageId`, `complete`, `seenUrls`, `historyResults`, `conversationId`; Sanitizer-gated `setHTML`; unseen-link unfurling; streaming-safe memoized render; emits `AIChatContent:OpenLink`; no Glean/l10n of its own | **reusable now** (history-grid + `mention:` chip paths are optional; pass empty `historyResults`) |
| `<ai-chat-table>` / `<ai-chat-card>` / `<ai-chat-grid>` | `aiwindow/ui/components/ai-chat-{table,card,grid}/` | plain lit widgets (table needs `aiwindow-copy-table` ftl strings) | **reusable now** |
| `<chat-assistant-loader>` / `<chat-assistant-error>` | `aiwindow/ui/components/ai-chat-content/chat-assistant-{loader,error}/` | presentational | **reusable now** |
| `<moz-multiline-editor>` + `createMentionsPlugin` | `multilineeditor/multiline-editor.mjs`, `multilineeditor/plugins/MentionsPlugin.mjs` | props: `placeholder`, `plugins`, `maxLength`; API: `plainText`, `insertMention()`, `getAllMentions()`, `posToTextOffset()`; mentions plugin takes `triggerChar: "@"`, `toDOM`/`nodeView`, `onEnter/onChange/onExit` callbacks — suggestion UI is caller-provided | **reusable now** (not aiwindow-owned at all) |
| `<smartwindow-panel-list>` | `aiwindow/ui/components/smartwindow-panel-list/` | anchored dropdown; `groups`/`anchor` props, `item-selected` / `panel-keydown` events | **reusable now** |
| `SmartbarMentionsPanelSearch` | `urlbar/SmartbarMentionsPanelSearch.sys.mjs` | `new (browserWindow)` then `search(query)` over open + recently-closed tabs | **reusable now** (needs a chrome window ref) |
| `<ai-website-chip>` | `aiwindow/ui/components/ai-website-chip/` | plain props (`label`, `href`, `iconSrc`, `type`); needs `page-icon:` in CSP img-src | **reusable now** |
| `<ai-chat-content>` | `aiwindow/ui/components/ai-chat-content/ai-chat-content.mjs` | fed purely by DOM CustomEvents (see above) with a `conversationState` sparse-array envelope (`{role, content, ordinal, isLastChunk, toolUIData, ...}`); but bakes in smart-window semantics: `#uiRenderMap` UI_TYPES (website/tab-group confirmation, action-result, retry), follow-ups, Glean `smartWindow.*`, `aiWindowContent.ftl` | **extractable with effort** — adopt its event protocol + message envelope, stub telemetry/l10n |
| `<ai-action-result>` / `ToolActionLog` rows | `aiwindow/ui/components/ai-action-result/`, `aiwindow/ui/modules/ToolActionLog.sys.mjs` | collapsible "N actions taken" with undo; plain props + `action-result-undo` event | **extractable with effort** (semantics are tab actions, not command approvals) |
| `<ai-website-confirmation>` / `<ai-website-select>` | `aiwindow/ui/components/ai-website-{confirmation,select}/` | confirmation card, but domain-specific (tab selection) and driven by `ToolUI.sys.mjs` state machine | **extractable with effort**; not a drop-in for codex exec approvals |
| `<moz-smartbar>` (`SmartbarInput`) | `urlbar/content/SmartbarInput.mjs` + `SmartbarInputController.mjs` + `SmartbarInputUtils.mjs` | subclass of the urlbar: providers, view, search service, ASRouter, gBrowser, intent classification, context chips, Glean | **entangled** — reuse its pieces (editor, mentions plugin, panel list), never the element |
| `<ai-window>` | `aiwindow/ui/components/ai-window/ai-window.mjs` | bound to `ChatConversation`, `ChatStore`, engines, actors, `AIWindowTabStatesManager`, memories, top sites | **entangled** |
| `ChatConversation` / `ChatStore` / `Chat.fetchWithHistory` | `aiwindow/ui/modules/`, `aiwindow/models/` | chat-completions streaming + local tool loop + sqlite persistence + SecurityProperties | **entangled** (this is the backend, see §3) |

## 3. The backend seam (for the long-term port direction)

Smart Window's "model client" seam today is
`conversation.runWithGenerator()` — a stateless chat-completions stream — and
there *is* a provider knob (`openAIEngine` custom endpoint pref), but the
whole loop above it (`Chat.fetchWithHistory`: local tool execution,
`TokenStreamParser.consumeStreamChunk`, SecurityProperties, URL tokens)
assumes that shape. The harness backend is the opposite shape: in
`harness/codex/AgentService.sys.mjs` the *sidecar owns the agent loop*
(thread-based; events `turnStarted`, `delta`, `item`
(reasoning/commandExecution/fileChange/browserTool), `message`,
`approvalRequest`, `turnCompleted`, `error`, `log`; approvals answered via
`AgentService.respondToApproval()`), with execution confined to the VM via
`CodexExecBridge`/`HarnessVM`.

So AgentService **cannot** implement the engine interface. The clean seam is
one level up — a **conversation driver** where `ai-window.mjs
#fetchAIResponse` currently hardcodes `Chat.fetchWithHistory`:

- Define a driver contract: `sendTurn(conversation, text, {signal})` that
  emits the existing neutral events `chat-conversation:message-update` /
  `:message-complete` (these are already the only currency `ai-window` →
  actor → `ai-chat-content` cares about).
- The existing path becomes `LocalCompletionsDriver` (Chat.sys.mjs).
- A `HarnessAgentDriver` wraps AgentService: `delta` → message-update on the
  streaming assistant message; `item` → `toolUIData` entries (a new
  `UI_TYPES.ACTION_LOG`-style renderer already exists in `ai-chat-content`'s
  `#uiRenderMap`); `approvalRequest` → one new confirmation UI type whose
  submit/close flows through the existing `AIChatContent:ToolUIUpdate` →
  `ToolUI.sys.mjs`-style resolution, answering `respondToApproval`.
- Persistence: codex owns the transcript (rollout files); `ChatStore` rows
  would only mirror titles/ids, or be bypassed for harness conversations.

## 4. Recommendation

Short term — upgrade about:harness in place, reusing leaf components
(about:harness is a system-principal chrome page —
`harness/AboutHarness.sys.mjs` maps it to
`chrome://browser/content/harness/aboutHarness.html` — so chrome:// module
imports and lit all work):

1. **Markdown message rendering**: replace the hand-rolled bubble text in
   `harness/content/aboutHarness.mjs` (`appendBubble`/delta appends) with
   `<ai-chat-message role="assistant" .message=... .complete=...>` and
   `parseMarkdown` from `ChatMarkdownParser.mjs`. Gets streaming-safe
   markdown, Sanitizer, tables, and unseen-link unfurling for free. Feed
   `seenUrls` from harness turn context (or an empty Set to unfurl
   everything, which is arguably right for an agent). Add `page-icon:` to
   the about:harness CSP img-src if chips are used.
2. **Compose box with @-tab mentions**: swap the harness `<textarea>` for
   `<moz-multiline-editor>` + `createMentionsPlugin({triggerChar:"@"})` +
   `<smartwindow-panel-list>` + `SmartbarMentionsPanelSearch` (mirroring
   `setupMentionsPlugin` in `urlbar/content/SmartbarInputUtils.mjs`, minus
   telemetry). On submit, `editor.getAllMentions()` → attach tab
   title/URL/content as context in the `AgentService.sendMessage` text (or
   as a dynamic tool per the tools spike).
3. **Keep** the hand-rolled activity `<details>` blocks and approval rows —
   they match AgentService's command-approval semantics, which
   `ai-website-confirmation` does not. Optionally restyle using
   `ai-action-result`'s look.
4. **Do not** try to reuse `<ai-chat-content>` or `<moz-smartbar>` in
   about:harness; both drag in smart-window state, telemetry, and l10n.

Switch to the full port (harness backend INTO smart window, §3 driver seam)
when any of these become requirements: persistent/resumable conversation
history UI, sidebar + fullpage surfaces, product-quality confirmation UI and
l10n, or shipping behind the smartwindow pref set. At that point the work is
in `ai-window.mjs` (driver selection), a new confirmation UI type in
`ai-chat-content`, and AgentService event mapping — not in about:harness.

## 5. Open questions

- **l10n**: reused components reference `aiWindowContent.ftl` /
  `aiwindow-copy-table` etc.; about:harness would need those `<link
  rel="localization">` includes or tolerate missing strings.
- **Glean**: `ai-chat-message` is clean, but `ai-chat-content` /
  smartbar-adjacent code records `Glean.smartWindow.*`; metrics exist
  build-wide (`aiwindow/metrics.yaml`) so calls won't throw, but recording
  smart-window telemetry from harness is wrong — stub or fork if those
  pieces get adopted.
- **Prosemirror bundle cost**: `multilineeditor` and `ChatMarkdownParser`
  both pull `prosemirror.bundle.mjs`; fine in a pref-gated page, worth
  checking load impact.
- **Mentions offsets across processes**: the persisted-mention format
  (`PersistedMention.textOffset`, see typedefs at the top of
  `ai-window.mjs`) matters only if harness persists drafts.
- **Driver seam buy-in**: does the aiwindow team accept a driver abstraction
  at `#fetchAIResponse`, or should the harness integration instead present
  itself as a custom endpoint speaking chat-completions (rejected here: it
  would forfeit VM-side tool execution and approvals)?
