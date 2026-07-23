/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { CodexAppServerClient } from "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  CodexExecBridge:
    "moz-src:///browser/components/harness/codex/CodexExecBridge.sys.mjs",
  HarnessVM: "moz-src:///browser/components/harness/HarnessVM.sys.mjs",
  clearTimeout: "resource://gre/modules/Timer.sys.mjs",
  setTimeout: "resource://gre/modules/Timer.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "AgentService",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

/**
 * Narrow conversation API over the Codex sidecar for harness UI surfaces.
 * Only thread/start, turn/start and turn/interrupt are ever issued; no
 * host-execution app-server methods are reachable from here, and unsolicited
 * server requests keep the client's fail-closed default.
 *
 * Events: {type:"turnStarted"|"delta"|"message"|"turnCompleted"|"log"|"error",
 *          conversationId, ...}
 */
// Server->client approval requests surfaced to the UI; everything else stays
// fail-closed in CodexAppServerClient.
const APPROVAL_METHODS = new Set([
  "item/commandExecution/requestApproval",
  "item/fileChange/requestApproval",
]);
const APPROVAL_TIMEOUT_MS = 120000;

export const AgentService = {
  _client: null,
  _starting: null,
  _listeners: new Set(),
  _conversations: new Map(),
  _environmentId: null,
  _pendingApprovals: new Map(),

  addListener(listener) {
    this._listeners.add(listener);
  },

  removeListener(listener) {
    this._listeners.delete(listener);
  },

  _emit(event) {
    for (const listener of this._listeners) {
      try {
        listener(event);
      } catch (e) {
        console.error(e);
      }
    }
  },

  async _ensureClient() {
    if (this._client?.running) {
      return this._client;
    }
    if (!this._starting) {
      const client = new CodexAppServerClient();
      client.addListener(notification => this._onNotification(notification));
      client.onServerRequest = request => this._onServerRequest(request);
      this._starting = client.start().then(
        () => {
          this._client = client;
          this._starting = null;
          this._environmentId = null;
          return client;
        },
        e => {
          this._starting = null;
          throw e;
        }
      );
    }
    return this._starting;
  },

  // Every conversation runs against the micro-VM as an external exec-server
  // environment. This is a security invariant, not a convenience: without an
  // attached environment Codex falls back to running commands on the host
  // (in its own sandbox, but still the host). So the VM is auto-started and
  // conversation creation fails closed if it cannot run.
  async _ensureEnvironment(client) {
    // The VM must be up even when the environment is already registered
    // (it may have been stopped since the last conversation).
    if (lazy.HarnessVM.state == "stopped") {
      this._emit({ type: "log", message: "starting sandbox VM..." });
      await lazy.HarnessVM.start();
    }
    for (let i = 0; lazy.HarnessVM.state == "starting" && i < 120; i++) {
      await new Promise(resolve => lazy.setTimeout(resolve, 250));
    }
    if (lazy.HarnessVM.state != "running") {
      throw new Error(
        "sandbox VM is not running; refusing to start a conversation " +
          "(commands would execute on the host)"
      );
    }
    for (let i = 0; ; i++) {
      try {
        await lazy.HarnessVM.exec("true");
        break;
      } catch (e) {
        if (i >= 40) {
          throw new Error(`sandbox VM agent not responding: ${e.message}`);
        }
        await new Promise(resolve => lazy.setTimeout(resolve, 250));
      }
    }
    if (!this._environmentId) {
      await this._seedWorkspaceContext();
      const url = lazy.CodexExecBridge.start();
      // Stable id so threads resumed in a later sidecar instance still
      // resolve their recorded environment after we re-register it.
      const environmentId = "harness-vm";
      await client.request("environment/add", {
        environmentId,
        execServerUrl: url,
      });
      this._environmentId = environmentId;
      lazy.logConsole.log(`environment ${environmentId} -> ${url}`);
    }
    return this._environmentId;
  },

  // Codex reads AGENTS.md from the environment cwd, so this is how the agent
  // learns what this sandbox is and what Firefox data can appear in it.
  async _seedWorkspaceContext() {
    const content = `# Firefox Harness sandbox

You are running inside a small Alpine Linux micro-VM embedded in Firefox.

- Your working directory /workspace is a folder shared with the host
  Firefox; files you create here are visible to the user and vice versa.
- There is deliberately no network access.
- Available tools: busybox userland (sh, ls, grep, sed, awk, tar, wc, ...)
  and sqlite3.
- Firefox data arrives as snapshot files the user shares into /workspace:
  - places.sqlite: a consistent snapshot of Firefox history and bookmarks.
    Key tables: moz_places (urls, visit_count, last_visit_date in
    microseconds since epoch), moz_historyvisits, moz_bookmarks,
    moz_origins. Query it with: sqlite3 /workspace/places.sqlite '...'
  - If the user asks about browsing data and the snapshot is missing, ask
    them to click "Snapshot Places DB" under "Sandbox VM tools" on the
    about:harness page.
`;
    await IOUtils.makeDirectory(lazy.HarnessVM.workspacePath, {
      createAncestors: true,
      ignoreExisting: true,
    });
    await IOUtils.writeUTF8(
      PathUtils.join(lazy.HarnessVM.workspacePath, "AGENTS.md"),
      content
    );
  },

  // Starts the ChatGPT OAuth flow in the sidecar; the returned authUrl must
  // be opened in a browser tab, and the sidecar's local callback completes
  // the login (tokens land in auth.json inside our dedicated CODEX_HOME).
  async login() {
    const client = await this._ensureClient();
    return client.request("account/login/start", { type: "chatgpt" }, 120000);
  },

  async accountStatus() {
    const client = await this._ensureClient();
    return client.request("account/read", {});
  },

  // Restarts the sidecar so pref changes (provider/model) take effect; the
  // regenerated config.toml is written on next start.
  async applySettings() {
    await this.shutdown();
  },

  /**
   * @param {object} [options]
   * @param {string} [options.model] per-conversation model override
   * @param {string} [options.modelProvider] per-conversation provider override
   * @param {string} [options.approvalPolicy] untrusted | on-request |
   *   on-failure | never (Codex decides when to fire approval requests)
   * @param {boolean} [options.persist] false = ephemeral thread (no rollout
   *   file, cannot be resumed)
   */
  async createConversation(options = {}) {
    const { model, modelProvider, approvalPolicy, persist = true } = options;
    const client = await this._ensureClient();
    // Non-ephemeral threads are persisted by Codex itself (rollout files in
    // CODEX_HOME/sessions) and can be reopened via thread/list +
    // thread/resume; we deliberately do not keep our own chat store.
    const params = { ephemeral: !persist };
    if (model) {
      params.model = model;
    }
    if (modelProvider) {
      params.modelProvider = modelProvider;
    }
    if (approvalPolicy) {
      params.approvalPolicy = approvalPolicy;
    }
    const environmentId = await this._ensureEnvironment(client);
    params.environments = [{ environmentId, cwd: "/workspace" }];
    const result = await client.request("thread/start", params);
    const conversationId = result.thread.id;
    this._conversations.set(conversationId, { activeTurnId: null });
    lazy.logConsole.log(
      `conversation ${conversationId} (${result.modelProvider}/${result.model})`
    );
    return {
      conversationId,
      model: result.model,
      modelProvider: result.modelProvider,
    };
  },

  /**
   * @param {object} [options]
   * @param {number} [options.limit]
   * @returns {Promise<Array<{conversationId, preview, updatedAt}>>}
   */
  async listConversations(options = {}) {
    const { limit = 25 } = options;
    const client = await this._ensureClient();
    const result = await client.request("thread/list", { limit });
    return (result.data ?? []).map(thread => ({
      conversationId: thread.id,
      preview: thread.preview || thread.name || "(empty conversation)",
      updatedAt: thread.updatedAt,
    }));
  },

  /**
   * Reopens a Codex-persisted thread. Returns the recorded turns so the UI
   * can render the history.
   *
   * @param {string} conversationId
   */
  async resumeConversation(conversationId) {
    const client = await this._ensureClient();
    await this._ensureEnvironment(client);
    const result = await client.request("thread/resume", {
      threadId: conversationId,
      cwd: "/workspace",
    });
    this._conversations.set(conversationId, { activeTurnId: null });
    return {
      conversationId,
      model: result.model,
      modelProvider: result.modelProvider,
      turns: result.thread?.turns ?? [],
    };
  },

  async sendMessage(conversationId, text) {
    const conversation = this._conversations.get(conversationId);
    if (!conversation) {
      throw new Error(`unknown conversation ${conversationId}`);
    }
    const client = await this._ensureClient();
    const result = await client.request("turn/start", {
      threadId: conversationId,
      input: [{ type: "text", text }],
    });
    conversation.activeTurnId = result.turn.id;
    return { turnId: result.turn.id };
  },

  async interrupt(conversationId) {
    const conversation = this._conversations.get(conversationId);
    if (!conversation?.activeTurnId || !this._client) {
      return;
    }
    await this._client.request("turn/interrupt", {
      threadId: conversationId,
      turnId: conversation.activeTurnId,
    });
  },

  _onServerRequest(request) {
    if (!APPROVAL_METHODS.has(request.method)) {
      lazy.logConsole.warn(`denying server request ${request.method}`);
      throw new Error(`${request.method} not permitted`);
    }
    return new Promise(resolve => {
      const timer = lazy.setTimeout(() => {
        this._pendingApprovals.delete(request.id);
        lazy.logConsole.warn(`approval ${request.id} timed out; declining`);
        resolve({ decision: "decline" });
      }, APPROVAL_TIMEOUT_MS);
      this._pendingApprovals.set(request.id, { resolve, timer });
      this._emit({
        type: "approvalRequest",
        requestId: request.id,
        method: request.method,
        conversationId: request.params?.threadId,
        params: request.params,
      });
    });
  },

  /**
   * @param {string|number} requestId from an approvalRequest event
   * @param {string} decision accept | acceptForSession | decline | cancel
   */
  respondToApproval(requestId, decision) {
    const pending = this._pendingApprovals.get(requestId);
    if (!pending) {
      return;
    }
    this._pendingApprovals.delete(requestId);
    lazy.clearTimeout(pending.timer);
    pending.resolve({ decision });
  },

  _onNotification(notification) {
    const params = notification.params ?? {};
    const conversationId = params.threadId;
    switch (notification.method) {
      case "turn/started":
        if (this._conversations.has(conversationId)) {
          this._conversations.get(conversationId).activeTurnId = params.turn.id;
        }
        this._emit({ type: "turnStarted", conversationId });
        break;
      case "item/agentMessage/delta":
        this._emit({ type: "delta", conversationId, text: params.delta });
        break;
      case "item/started":
      case "item/updated":
        if (
          params.item &&
          !["agentMessage", "userMessage"].includes(params.item.type)
        ) {
          this._emit({
            type: "item",
            phase: notification.method.split("/")[1],
            conversationId,
            item: params.item,
          });
        }
        break;
      case "item/completed":
        if (params.item?.type == "agentMessage") {
          this._emit({
            type: "message",
            conversationId,
            text: params.item.text,
          });
        } else if (params.item && params.item.type != "userMessage") {
          this._emit({
            type: "item",
            phase: "completed",
            conversationId,
            item: params.item,
          });
        }
        break;
      case "turn/completed":
        if (this._conversations.has(conversationId)) {
          this._conversations.get(conversationId).activeTurnId = null;
        }
        this._emit({
          type: "turnCompleted",
          conversationId,
          status: params.turn.status,
        });
        break;
      case "warning":
        this._emit({ type: "log", conversationId, message: params.message });
        break;
      case "error":
        this._emit({
          type: "error",
          conversationId,
          message: params.error?.message ?? JSON.stringify(params),
        });
        break;
      case "sidecarExited":
        this._conversations.clear();
        this._emit({
          type: "error",
          message: `app-server exited (${params.exitCode})`,
        });
        break;
    }
  },

  async shutdown() {
    const client = this._client;
    this._client = null;
    this._conversations.clear();
    this._environmentId = null;
    lazy.CodexExecBridge.stop();
    await client?.stop();
  },
};
