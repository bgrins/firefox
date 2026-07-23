/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { CodexAppServerClient } from "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs";

const lazy = {};

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
export const AgentService = {
  _client: null,
  _starting: null,
  _listeners: new Set(),
  _conversations: new Map(),

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
      this._starting = client.start().then(
        () => {
          this._client = client;
          this._starting = null;
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

  /**
   * @param {object} [options]
   * @param {string} [options.model] per-conversation model override
   * @param {string} [options.modelProvider] per-conversation provider override
   */
  async createConversation({ model, modelProvider } = {}) {
    const client = await this._ensureClient();
    const params = { ephemeral: true };
    if (model) {
      params.model = model;
    }
    if (modelProvider) {
      params.modelProvider = modelProvider;
    }
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
      case "item/completed":
        if (params.item?.type == "agentMessage") {
          this._emit({
            type: "message",
            conversationId,
            text: params.item.text,
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
    await client?.stop();
  },
};
