/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Lifecycle for the in-browser MCP server: wires the vendored firefox-devtools-mcp
 * bundle (vendor/fdm-core.mjs) to MCPBridge and gates every HTTP request.
 *
 * Auth modes (browser.mcp.auth):
 * - "oauth" (default): self-issued OAuth 2.1 via MCPAuth. Sessions are created
 *   when a token is granted; unauthenticated /mcp requests get 401 +
 *   WWW-Authenticate so spec-conformant clients drive the flow themselves.
 * - "none": no authentication; a session is created at server start.
 */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";
import { MCPAuth } from "moz-src:///browser/components/mcp/MCPAuth.sys.mjs";
import { MCPBridge } from "moz-src:///browser/components/mcp/MCPBridge.sys.mjs";
import { MCPSessions } from "moz-src:///browser/components/mcp/MCPSessions.sys.mjs";
import {
  configure,
  startMcp,
  DEFAULT_PORT,
} from "moz-src:///browser/components/mcp/vendor/fdm-core.mjs";

const lazy = {};
ChromeUtils.defineESModuleGetters(lazy, {
  AsyncShutdown: "resource://gre/modules/AsyncShutdown.sys.mjs",
});

const PORT_PREF = "browser.mcp.port";
const AUTH_PREF = "browser.mcp.auth";

// DevToolsActivePort-style discovery file in the profile directory so local
// tooling can find a running instance's endpoint. Contains pid: consumers
// must treat the file as stale if that process is gone (crash leaves it
// behind).
const DISCOVERY_FILE = "MCPActivePort.json";

// Must match DEV_TOKEN in vendor/fdm-core.mjs. The bundle's static token check
// is vestigial once the gate below has validated the request; we rewrite the
// Authorization header so the bundle accepts it.
const INTERNAL_BUNDLE_TOKEN = "bidi-bridge-dev";

let configured = false;
let running = false;
let boundPort = null;
let activeSession = null;

function authMode() {
  return Services.prefs.getCharPref(AUTH_PREF, "oauth");
}

function discoveryPath() {
  return PathUtils.join(PathUtils.profileDir, DISCOVERY_FILE);
}

let shutdownBlockerRegistered = false;

async function writeDiscoveryFile() {
  try {
    await IOUtils.writeJSON(discoveryPath(), {
      port: boundPort,
      endpoint: `${origin()}/mcp`,
      pid: Services.appinfo.processID,
      auth: authMode(),
    });
  } catch (e) {
    console.error("MCPServer: failed to write discovery file", e);
  }
  if (!shutdownBlockerRegistered) {
    shutdownBlockerRegistered = true;
    lazy.AsyncShutdown.profileBeforeChange.addBlocker(
      "MCPServer: remove discovery file",
      removeDiscoveryFile
    );
  }
}

async function removeDiscoveryFile() {
  try {
    await IOUtils.remove(discoveryPath(), { ignoreAbsent: true });
  } catch (e) {
    console.error("MCPServer: failed to remove discovery file", e);
  }
}

function origin() {
  return `http://127.0.0.1:${boundPort}`;
}

// One active session at a time: a new grant replaces (revokes) the previous
// one, matching handoff semantics — the bridge scope and the shared tool
// facade cannot isolate concurrent sessions.
function adoptGrantedSession({ scope = null, clientName = null } = {}) {
  if (activeSession) {
    MCPSessions.revoke(activeSession);
  }
  activeSession = MCPSessions.create({ scope });
  if (clientName) {
    MCPSessions.setClientInfo(activeSession, { name: clientName });
  }
  if (scope) {
    MCPBridge.setScope(scope);
  } else {
    MCPBridge.clearScope();
  }
  return activeSession;
}

function pausedVerdict(id) {
  return {
    status: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: id ?? null,
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

function httpGate(request) {
  const host = request.headers.host ?? "";
  if (![`127.0.0.1:${boundPort}`, `localhost:${boundPort}`].includes(host)) {
    // DNS-rebinding guard: only loopback hostnames may address this server.
    return {
      status: 403,
      headers: { "Content-Type": "text/plain" },
      body: "invalid host",
    };
  }

  const oauthVerdict = MCPAuth.handleRequest(request, {
    origin: origin(),
    onGrant: adoptGrantedSession,
  });
  if (oauthVerdict) {
    return oauthVerdict;
  }

  if (request.path !== "/mcp" || request.method !== "POST") {
    return null;
  }

  let gateSession;
  if (authMode() === "oauth") {
    const auth = request.headers.authorization ?? "";
    const token = auth.startsWith("Bearer ")
      ? auth.slice("Bearer ".length)
      : null;
    gateSession = MCPSessions.findByToken(token);
    if (!gateSession) {
      return {
        status: 401,
        headers: {
          "Content-Type": "text/plain",
          "WWW-Authenticate": `Bearer resource_metadata="${origin()}/.well-known/oauth-protected-resource"`,
        },
        body: "unauthorized",
      };
    }
  } else {
    if (!activeSession || activeSession.state === "revoked") {
      adoptGrantedSession({ scope: MCPBridge.scope });
    }
    gateSession = activeSession;
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
      return pausedVerdict(msg.id);
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
    return activeSession;
  },

  get authMode() {
    return authMode();
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
    const requested =
      port ?? Services.prefs.getIntPref(PORT_PREF, DEFAULT_PORT);
    boundPort = await startMcp(requested);
    running = true;
    if (scope) {
      MCPBridge.setScope(scope);
    } else {
      MCPBridge.clearScope();
    }
    if (authMode() === "none") {
      adoptGrantedSession({ scope: scope ?? null });
    }
    await writeDiscoveryFile();
    return boundPort;
  },

  // Revoke the current session but keep the server listening so a client can
  // re-run the OAuth flow.
  revokeSession() {
    if (activeSession) {
      MCPSessions.revoke(activeSession);
      activeSession = null;
    }
    MCPBridge.clearScope();
  },

  stop() {
    MCPAuth.denyAll();
    this.revokeSession();
    MCPBridge.stopServer();
    MCPBridge.clearScope();
    running = false;
    void removeDiscoveryFile();
  },
};
