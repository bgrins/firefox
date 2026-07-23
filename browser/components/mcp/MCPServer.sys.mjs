/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Lifecycle for the in-browser MCP server: wires the vendored firefox-devtools-mcp
 * bundle (vendor/fdm-core.mjs) to MCPBridge, mints a session per run, and
 * gates every HTTP request on the session's token and state.
 */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";
import { MCPBridge } from "moz-src:///browser/components/mcp/MCPBridge.sys.mjs";
import { MCPSessions } from "moz-src:///browser/components/mcp/MCPSessions.sys.mjs";
import {
  configure,
  startMcp,
  DEFAULT_PORT,
} from "moz-src:///browser/components/mcp/vendor/fdm-core.mjs";

const PORT_PREF = "browser.mcp.port";

// Must match DEV_TOKEN in vendor/fdm-core.mjs. The bundle's static token check
// is vestigial once the gate below has validated the real per-session token;
// we rewrite the Authorization header so the bundle accepts the request.
const INTERNAL_BUNDLE_TOKEN = "bidi-bridge-dev";

let configured = false;
let running = false;
let boundPort = null;
let session = null;

function httpGate(request) {
  if (request.path !== "/mcp" || request.method !== "POST") {
    return null;
  }
  const auth = request.headers.authorization ?? "";
  const token = auth.startsWith("Bearer ")
    ? auth.slice("Bearer ".length)
    : null;
  const gateSession = MCPSessions.findByToken(token);
  if (!gateSession) {
    return {
      status: 401,
      headers: { "Content-Type": "text/plain" },
      body: "bad or missing bearer token",
    };
  }
  let msg = null;
  try {
    msg = JSON.parse(request.body);
  } catch {
    // The bundle responds with a JSON-RPC parse error.
  }
  if (msg?.method === "initialize") {
    if (msg.params?.clientInfo) {
      MCPSessions.setClientInfo(gateSession, msg.params.clientInfo);
    }
    MCPSessions.recordActivity(gateSession, "initialize");
  } else if (msg?.method === "tools/call") {
    if (gateSession.state === "paused") {
      return {
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: msg.id ?? null,
          result: {
            content: [
              {
                type: "text",
                text: "Error: the user has paused this session. Wait and retry, or ask the user to resume from the MCP panel.",
              },
            ],
            isError: true,
          },
        }),
      };
    }
    MCPSessions.recordActivity(gateSession, msg.params?.name ?? "tools/call");
  }
  request.headers.authorization = `Bearer ${INTERNAL_BUNDLE_TOKEN}`;
  return null;
}

export const MCPServer = {
  get running() {
    return running;
  },

  get port() {
    return boundPort;
  },

  get session() {
    return session;
  },

  // True when the running server is restricted to a single tab.
  get scoped() {
    return MCPBridge.scope !== null;
  },

  async start({ port, scope } = {}) {
    if (running) {
      return boundPort;
    }
    if (!configured) {
      configure({
        bidi: MCPBridge,
        version: Services.appinfo.version,
        setTimeout,
        clearTimeout,
      });
      configured = true;
    }
    MCPBridge.setHttpGate(httpGate);
    if (scope) {
      MCPBridge.setScope(scope);
    } else {
      MCPBridge.clearScope();
    }
    session = MCPSessions.create({ scope: scope ?? null });
    const requested =
      port ?? Services.prefs.getIntPref(PORT_PREF, DEFAULT_PORT);
    try {
      boundPort = await startMcp(requested);
    } catch (e) {
      MCPSessions.revoke(session);
      session = null;
      MCPBridge.clearScope();
      throw e;
    }
    running = true;
    return boundPort;
  },

  stop() {
    if (session) {
      MCPSessions.revoke(session);
      session = null;
    }
    MCPBridge.stopServer();
    MCPBridge.clearScope();
    running = false;
  },
};
