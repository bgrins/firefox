/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Registry of agent sessions for the in-browser MCP server. Each session owns
 * a minted bearer token, the tab scope it was granted, its lifecycle state,
 * the client identity captured from the MCP initialize handshake, and a
 * recent activity log for the management UI.
 */

const MAX_ACTIVITY = 20;

let nextId = 1;
const sessions = new Map();
const listeners = new Set();

function notify(type, session) {
  for (const listener of [...listeners]) {
    try {
      listener(type, session);
    } catch (e) {
      console.error("MCPSessions: listener failed", e);
    }
  }
}

export const MCPSessions = {
  create({ scope = null } = {}) {
    const session = {
      id: nextId++,
      token: Services.uuid.generateUUID().toString().slice(1, -1),
      scope,
      state: "active",
      clientInfo: null,
      createdAt: Date.now(),
      activity: [],
    };
    sessions.set(session.id, session);
    notify("created", session);
    return session;
  },

  findByToken(token) {
    if (!token) {
      return null;
    }
    for (const session of sessions.values()) {
      if (session.token === token && session.state !== "revoked") {
        return session;
      }
    }
    return null;
  },

  setClientInfo(session, clientInfo) {
    session.clientInfo = {
      name: String(clientInfo?.name ?? ""),
      version: String(clientInfo?.version ?? ""),
      title: clientInfo?.title ? String(clientInfo.title) : null,
    };
    notify("updated", session);
  },

  recordActivity(session, label) {
    session.activity.push({ label, ts: Date.now() });
    if (session.activity.length > MAX_ACTIVITY) {
      session.activity.shift();
    }
    notify("activity", session);
  },

  pause(session) {
    if (session.state === "active") {
      session.state = "paused";
      notify("updated", session);
    }
  },

  resume(session) {
    if (session.state === "paused") {
      session.state = "active";
      notify("updated", session);
    }
  },

  revoke(session) {
    if (session.state !== "revoked") {
      session.state = "revoked";
      notify("updated", session);
    }
  },

  addListener(fn) {
    listeners.add(fn);
  },

  removeListener(fn) {
    listeners.delete(fn);
  },
};
