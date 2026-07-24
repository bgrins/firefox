/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * In-process WebDriver BiDi bridge + loopback-only HTTP listener, consumed by the
 * vendored firefox-devtools-mcp bundle (vendor/fdm-core.mjs). Provides the same
 * surface the bundle's extension variant gets from its `browser.bidi` experiment:
 * send/subscribe/unsubscribe, startServer/stopServer/sendHttpResponse, getPref/setPref,
 * and onEvent/onHttpRequest listener registration.
 */

const lazy = {};
ChromeUtils.defineESModuleGetters(lazy, {
  setTimeout: "resource://gre/modules/Timer.sys.mjs",
  clearTimeout: "resource://gre/modules/Timer.sys.mjs",
  NavigableManager: "chrome://remote/content/shared/NavigableManager.sys.mjs",
  RootMessageHandler:
    "chrome://remote/content/shared/messagehandler/RootMessageHandler.sys.mjs",
  WebDriverSession: "chrome://remote/content/shared/webdriver/Session.sys.mjs",
});

const MAX_REQUEST_BYTES = 4 * 1024 * 1024;

// Commands permitted while the bridge is scoped to a single tab. Everything
// else (tab create/close, chrome-scoped getTree, webExtension, prefs, ...)
// is rejected outright.
const SCOPED_COMMANDS = new Set([
  "session.subscribe",
  "session.unsubscribe",
  "browsingContext.activate",
  "browsingContext.captureScreenshot",
  "browsingContext.getTree",
  "browsingContext.handleUserPrompt",
  "browsingContext.locateNodes",
  "browsingContext.navigate",
  "browsingContext.reload",
  "browsingContext.setViewport",
  "browsingContext.traverseHistory",
  "input.performActions",
  "input.setFiles",
  "script.callFunction",
  "script.evaluate",
]);

function bytesToString(bytes) {
  return new TextDecoder("utf-8").decode(
    Uint8Array.from(bytes, c => c.charCodeAt(0))
  );
}

function stringToByteString(str) {
  const encoded = new TextEncoder().encode(str);
  let out = "";
  for (const b of encoded) {
    out += String.fromCharCode(b);
  }
  return out;
}

/**
 * Parse one HTTP/1.1 request from an accumulated byte-string buffer.
 *
 * @param {string} buffer
 *   Accumulated socket bytes as a byte-string.
 * @returns {object | null}
 *   Parsed request, an { error } status, or null if incomplete.
 */
function tryParseHttpRequest(buffer) {
  const headerEnd = buffer.indexOf("\r\n\r\n");
  if (headerEnd === -1) {
    return buffer.length > MAX_REQUEST_BYTES ? { error: 431 } : null;
  }
  const head = buffer.slice(0, headerEnd).split("\r\n");
  const [method, path] = head[0].split(" ");
  const headers = {};
  for (const line of head.slice(1)) {
    const idx = line.indexOf(":");
    if (idx > 0) {
      headers[line.slice(0, idx).trim().toLowerCase()] = line
        .slice(idx + 1)
        .trim();
    }
  }
  if (headers["transfer-encoding"]) {
    return { error: 501 };
  }
  const clRaw = headers["content-length"] ?? "0";
  if (!/^\d+$/.test(clRaw)) {
    return { error: 400 };
  }
  const contentLength = parseInt(clRaw, 10);
  if (contentLength > MAX_REQUEST_BYTES) {
    return { error: 413 };
  }
  const total = headerEnd + 4 + contentLength;
  if (buffer.length < total) {
    return null;
  }
  return {
    method,
    path,
    headers,
    body: bytesToString(buffer.slice(headerEnd + 4, total)),
    byteLength: total,
  };
}

const STATUS_TEXT = {
  200: "OK",
  201: "Created",
  202: "Accepted",
  302: "Found",
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  405: "Method Not Allowed",
  413: "Payload Too Large",
  431: "Request Header Fields Too Large",
  500: "Internal Server Error",
  501: "Not Implemented",
  503: "Service Unavailable",
};

/**
 * Owns the WebDriver session, HTTP listener, and their connections.
 */
class Bridge {
  #session = null;
  #handler = null;
  #serverSocket = null;
  #pendingResponses = new Map(); // requestId -> connection
  #nextRequestId = 1;
  #httpRequestListener = null;
  // Inspects every parsed HTTP request before the vendored bundle sees it.
  // May mutate the request (e.g. rewrite Authorization) or return a response
  // {status, headers, body} to short-circuit.
  #httpGate = null;
  #eventListeners = new Set();
  #eventHookInstalled = false;
  // Strong references to live connections — without this the transport/streams can
  // be GC'd mid-request, which surfaces as "Empty reply from server".
  #liveConnections = new Set();
  // Navigable id of the single tab this bridge is allowed to touch, or null
  // for unrestricted access. See #enforceScope.
  #scope = null;

  // Create a REAL WebDriverSession (BiDi flavor, no connection) rather than a bare
  // RootMessageHandler: several BiDi paths call
  // getWebDriverSessionById(messageHandler.sessionId) and throw on a bare handler —
  // node serialization (breaks input.setFiles) and browsingContext's #onPromptOpened
  // (silently swallows userPromptOpened). The session also sets up the process actor
  // and navigable/window tracking.
  //
  // unhandledPromptBehavior "ignore": dialogs stay OPEN and emit userPromptOpened —
  // the policy is report-and-let-the-agent-decide, never silent auto-answer.
  #getHandler() {
    if (!this.#handler) {
      this.#session = new lazy.WebDriverSession(
        { unhandledPromptBehavior: { default: "ignore" } },
        new Set([lazy.WebDriverSession.SESSION_FLAG_BIDI])
      );
      this.#handler = this.#session.messageHandler;
    }
    return this.#handler;
  }

  destroy() {
    this.stopServer();
    this.#scope = null;
    this.#httpGate = null;
    this.#session?.destroy();
    this.#session = null;
    this.#handler = null;
    this.#eventHookInstalled = false;
    this.#eventListeners.clear();
  }

  get scope() {
    return this.#scope;
  }

  setScope(navigableId) {
    this.#scope = navigableId;
  }

  clearScope() {
    this.#scope = null;
  }

  #topLevelIdFor(contextId) {
    const browsingContext =
      lazy.NavigableManager.getBrowsingContextById(contextId);
    if (!browsingContext) {
      return null;
    }
    return lazy.NavigableManager.getIdForBrowsingContext(browsingContext.top);
  }

  #inScope(contextId) {
    return (
      this.#scope !== null && this.#topLevelIdFor(contextId) === this.#scope
    );
  }

  #assertInScope(contextId) {
    if (!this.#inScope(contextId)) {
      throw new Error(
        `Context ${contextId} is outside the tab granted to this MCP session`
      );
    }
  }

  // Validate (and where needed rewrite) a command against the granted tab.
  // Context params must resolve to the granted top-level navigable or one of
  // its descendant frames.
  #enforceScope(moduleName, commandName, params) {
    const command = `${moduleName}.${commandName}`;
    if (!SCOPED_COMMANDS.has(command)) {
      throw new Error(
        `Command ${command} is not allowed in a tab-scoped MCP session`
      );
    }
    switch (command) {
      case "session.subscribe":
        return { ...params, contexts: [this.#scope] };
      case "session.unsubscribe":
        return params;
      case "browsingContext.getTree":
        if (params["moz:scope"]) {
          throw new Error(
            "Chrome-scoped getTree is not allowed in a tab-scoped MCP session"
          );
        }
        if (params.root !== undefined) {
          this.#assertInScope(params.root);
        }
        return params;
      case "script.evaluate":
      case "script.callFunction": {
        const context = params.target?.context;
        if (!context) {
          throw new Error(
            "Tab-scoped MCP sessions require a context target for script commands"
          );
        }
        this.#assertInScope(context);
        return params;
      }
      default:
        this.#assertInScope(params.context);
        return params;
    }
  }

  async send(moduleName, commandName, params) {
    let effectiveParams = params ?? {};
    if (this.#scope !== null) {
      effectiveParams = this.#enforceScope(
        moduleName,
        commandName,
        effectiveParams
      );
    }
    const handler = this.#getHandler();
    const result = await handler.handleCommand({
      moduleName,
      commandName,
      params: effectiveParams,
      destination: { type: lazy.RootMessageHandler.type },
    });
    const cloned = JSON.parse(JSON.stringify(result ?? null));
    if (
      this.#scope !== null &&
      moduleName === "browsingContext" &&
      commandName === "getTree" &&
      Array.isArray(cloned?.contexts)
    ) {
      cloned.contexts = cloned.contexts.filter(c => this.#inScope(c.context));
    }
    return cloned;
  }

  subscribe(events, contexts) {
    const params = { events };
    if (contexts?.length) {
      params.contexts = contexts;
    }
    return this.send("session", "subscribe", params);
  }

  unsubscribe(events) {
    return this.send("session", "unsubscribe", { events });
  }

  #assertUnscoped() {
    if (this.#scope !== null) {
      throw new Error("Pref access is not allowed in a tab-scoped MCP session");
    }
  }

  getPref(name) {
    this.#assertUnscoped();
    switch (Services.prefs.getPrefType(name)) {
      case Services.prefs.PREF_BOOL:
        return { type: "boolean", value: Services.prefs.getBoolPref(name) };
      case Services.prefs.PREF_INT:
        return { type: "number", value: Services.prefs.getIntPref(name) };
      case Services.prefs.PREF_STRING:
        return { type: "string", value: Services.prefs.getStringPref(name) };
      default:
        return { type: "invalid", value: null };
    }
  }

  setPref(name, value) {
    this.#assertUnscoped();
    if (typeof value === "boolean") {
      Services.prefs.setBoolPref(name, value);
    } else if (typeof value === "number") {
      Services.prefs.setIntPref(name, value);
    } else {
      Services.prefs.setStringPref(name, String(value));
    }
  }

  onEvent = {
    addListener: cb => {
      this.#eventListeners.add(cb);
      if (!this.#eventHookInstalled) {
        this.#eventHookInstalled = true;
        this.#getHandler().on(
          "message-handler-protocol-event",
          (_eventName, wrappedEvent) => {
            let cloned;
            try {
              cloned = JSON.parse(JSON.stringify(wrappedEvent));
            } catch (e) {
              console.error("MCPBridge: failed to forward event", e);
              return;
            }
            // Subscriptions predating a handoff may be global — drop anything
            // that doesn't provably belong to the granted tab.
            if (this.#scope !== null) {
              const data = cloned?.data ?? {};
              const context = data.context ?? data.source?.context;
              if (!context || !this.#inScope(context)) {
                return;
              }
            }
            for (const listener of this.#eventListeners) {
              try {
                listener(cloned);
              } catch (e) {
                console.error("MCPBridge: event listener failed", e);
              }
            }
          }
        );
      }
    },
  };

  onHttpRequest = {
    // Last-wins: the vendored bundle owns the server.
    addListener: cb => {
      this.#httpRequestListener = cb;
    },
  };

  setHttpGate(fn) {
    this.#httpGate = fn;
  }

  sendHttpResponse(requestId, status, headers, body) {
    const connection = this.#pendingResponses.get(requestId);
    if (!connection) {
      throw new Error(`No pending HTTP request with id ${requestId}`);
    }
    this.#pendingResponses.delete(requestId);
    this.#respond(connection, status, headers ?? {}, body ?? "");
  }

  startServer(port) {
    if (this.#serverSocket) {
      return this.#serverSocket.port;
    }
    const socket = Cc["@mozilla.org/network/server-socket;1"].createInstance(
      Ci.nsIServerSocket
    );
    // loopbackOnly=true: only 127.0.0.1 can connect.
    socket.init(port, true, -1);
    socket.asyncListen({
      onSocketAccepted: (_socket, transport) => {
        try {
          this.#onSocketAccepted(transport);
        } catch (e) {
          console.error("MCPBridge: accept failed", e);
        }
      },
      onStopListening: () => {},
    });
    this.#serverSocket = socket;
    return socket.port;
  }

  stopServer() {
    this.#serverSocket?.close();
    this.#serverSocket = null;
    this.#pendingResponses.clear();
    for (const connection of [...this.#liveConnections]) {
      this.#closeConnection(connection);
    }
  }

  get serverPort() {
    return this.#serverSocket?.port ?? null;
  }

  #respond(connection, status, headers, body) {
    const statusText = STATUS_TEXT[status] ?? "OK";
    const bodyBytes = stringToByteString(body ?? "");
    const keepAlive = connection.keepAlive;
    const lines = [
      `HTTP/1.1 ${status} ${statusText}`,
      `Content-Length: ${bodyBytes.length}`,
      `Connection: ${keepAlive ? "keep-alive" : "close"}`,
    ];
    for (const [k, v] of Object.entries(headers ?? {})) {
      if (
        /[\r\n]/.test(k) ||
        /[\r\n]/.test(String(v)) ||
        /^(content-length|connection)$/i.test(k)
      ) {
        // header-injection / framing guard
        continue;
      }
      lines.push(`${k}: ${v}`);
    }
    const response = lines.join("\r\n") + "\r\n\r\n" + bodyBytes;
    try {
      // Output stream is opened OPEN_BLOCKING, so this writes fully or throws.
      connection.output.write(response, response.length);
    } catch (e) {
      console.error("MCPBridge: response write failed", e);
      this.#closeConnection(connection);
      return;
    }
    if (keepAlive) {
      connection.busy = false;
      this.#armIdleTimer(connection);
      // A pipelined follow-up request may already be fully buffered — parsing only
      // happens on new socket data otherwise, which would stall it until the idle
      // kill.
      this.#processBuffer(connection);
    } else {
      this.#closeConnection(connection);
    }
  }

  // Parse and dispatch at most one request from the connection's buffer.
  #processBuffer(connection) {
    if (connection.busy || !this.#liveConnections.has(connection)) {
      return;
    }
    const parsed = tryParseHttpRequest(connection.buffer);
    if (parsed == null) {
      return;
    }
    if (parsed.error) {
      connection.keepAlive = false;
      this.#respond(connection, parsed.error, {}, "");
      return;
    }
    connection.buffer = connection.buffer.slice(parsed.byteLength);
    connection.keepAlive =
      (parsed.headers.connection ?? "keep-alive").toLowerCase() !== "close";
    if (this.#httpGate) {
      let verdict;
      try {
        verdict = this.#httpGate(parsed);
      } catch (e) {
        console.error("MCPBridge: http gate failed", e);
        verdict = {
          status: 500,
          headers: { "Content-Type": "text/plain" },
          body: "internal error",
        };
      }
      if (verdict) {
        if (typeof verdict.then === "function") {
          // Deferred verdict (e.g. an /authorize request held until the user
          // decides). Extend the idle deadline so consent has time.
          connection.busy = true;
          connection.idleMs = 300000;
          this.#armIdleTimer(connection);
          const id = this.#nextRequestId++;
          this.#pendingResponses.set(id, connection);
          verdict.then(
            v => {
              connection.idleMs = null;
              try {
                this.sendHttpResponse(id, v.status, v.headers ?? {}, v.body);
              } catch {}
            },
            e => {
              console.error("MCPBridge: deferred gate response failed", e);
              connection.idleMs = null;
              try {
                this.sendHttpResponse(
                  id,
                  500,
                  { "Content-Type": "text/plain" },
                  "internal error"
                );
              } catch {}
            }
          );
          return;
        }
        this.#respond(
          connection,
          verdict.status,
          verdict.headers ?? {},
          verdict.body ?? ""
        );
        return;
      }
    }
    if (!this.#httpRequestListener) {
      this.#respond(
        connection,
        503,
        { "Content-Type": "text/plain" },
        "server not ready"
      );
      return;
    }
    connection.busy = true;
    // Re-arm on dispatch: the deadline bounds THIS request's handling, not time
    // since the previous response.
    this.#armIdleTimer(connection);
    const id = this.#nextRequestId++;
    this.#pendingResponses.set(id, connection);
    this.#httpRequestListener({
      id,
      method: parsed.method,
      path: parsed.path,
      headers: parsed.headers,
      body: parsed.body,
    });
  }

  #armIdleTimer(connection) {
    if (connection.idleTimer) {
      lazy.clearTimeout(connection.idleTimer);
    }
    connection.idleTimer = lazy.setTimeout(() => {
      for (const [id, pending] of this.#pendingResponses) {
        if (pending === connection) {
          this.#pendingResponses.delete(id);
        }
      }
      this.#closeConnection(connection);
    }, connection.idleMs ?? 65000);
  }

  #closeConnection(connection) {
    this.#liveConnections.delete(connection);
    // Sweep any map entries pointing at this connection (peer-close mid-request).
    for (const [id, pending] of this.#pendingResponses) {
      if (pending === connection) {
        this.#pendingResponses.delete(id);
      }
    }
    if (connection.idleTimer) {
      lazy.clearTimeout(connection.idleTimer);
      connection.idleTimer = null;
    }
    try {
      connection.input?.close();
    } catch {}
    try {
      connection.output?.close();
    } catch {}
  }

  #onSocketAccepted(transport) {
    const connection = {
      transport,
      input: null,
      output: null,
      idleTimer: null,
      idleMs: null,
      buffer: "",
      keepAlive: true,
      busy: false,
    };
    this.#liveConnections.add(connection);
    connection.input = transport
      .openInputStream(0, 0, 0)
      .QueryInterface(Ci.nsIAsyncInputStream);
    // OPEN_BLOCKING: write() completes fully or throws — avoids silent truncation
    // of large responses (screenshots) on a non-blocking socket stream.
    connection.output = transport.openOutputStream(
      Ci.nsITransport.OPEN_BLOCKING,
      0,
      0
    );
    const { input } = connection;
    const bin = Cc["@mozilla.org/binaryinputstream;1"].createInstance(
      Ci.nsIBinaryInputStream
    );
    bin.setInputStream(input);

    // Stalled clients must not leak connections forever.
    this.#armIdleTimer(connection);

    const readMore = () => {
      input.asyncWait(
        {
          onInputStreamReady: () => {
            try {
              let available;
              try {
                available = input.available();
              } catch {
                // Stream closed by peer.
                this.#closeConnection(connection);
                return;
              }
              if (available > 0) {
                connection.buffer += bin.readBytes(available);
              }
              // Cap applies even while busy — a client streaming bytes must not
              // grow the buffer unboundedly.
              if (connection.buffer.length > MAX_REQUEST_BYTES * 2) {
                this.#closeConnection(connection);
                return;
              }
              // Dispatch at most one request at a time per connection (streamable
              // HTTP clients pipeline sequentially; simpler and safe).
              this.#processBuffer(connection);
              if (this.#liveConnections.has(connection)) {
                readMore();
              }
            } catch (e) {
              console.error("MCPBridge: request handling failed", e);
              this.#closeConnection(connection);
            }
          },
        },
        0,
        0,
        Services.tm.currentThread
      );
    };
    readMore();
  }
}

export const MCPBridge = new Bridge();
