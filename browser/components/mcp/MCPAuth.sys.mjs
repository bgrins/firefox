/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Minimal self-issued OAuth 2.1 authorization server for the in-browser MCP
 * server, per the MCP authorization spec: RFC 9728 protected resource
 * metadata, RFC 8414 AS metadata, RFC 7591 dynamic client registration
 * (loopback redirect URIs only), authorization code + PKCE (S256).
 *
 * /authorize responses are HELD (Promise verdicts through the MCPBridge http
 * gate) until the user approves or denies in chrome UI — consent must be
 * chrome-mediated, since any unauthenticated decision endpoint would let a
 * local process approve its own grant.
 */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";

const CODE_TTL_MS = 5 * 60 * 1000;
const PENDING_TTL_MS = 5 * 60 * 1000;

const clients = new Map();
const codes = new Map();
const pending = new Map();
const listeners = new Set();
let onGrantCallback = null;

function notify(type, data) {
  for (const listener of [...listeners]) {
    try {
      listener(type, data);
    } catch (e) {
      console.error("MCPAuth: listener failed", e);
    }
  }
}

function uuid() {
  return Services.uuid.generateUUID().toString().slice(1, -1);
}

function sha256Base64Url(input) {
  const hasher = Cc["@mozilla.org/security/hash;1"].createInstance(
    Ci.nsICryptoHash
  );
  hasher.init(Ci.nsICryptoHash.SHA256);
  const bytes = new TextEncoder().encode(input);
  hasher.update(bytes, bytes.length);
  return btoa(hasher.finish(false))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function json(status, obj) {
  return {
    status,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(obj),
  };
}

function oauthError(status, error, description) {
  return json(status, { error, error_description: description });
}

function isLoopbackRedirect(uri) {
  try {
    const url = new URL(uri);
    return (
      url.protocol === "http:" &&
      ["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)
    );
  } catch {
    return false;
  }
}

function redirectTo(redirectUri, params) {
  const url = new URL(redirectUri);
  for (const [k, v] of Object.entries(params)) {
    if (v != null) {
      url.searchParams.set(k, v);
    }
  }
  return { status: 302, headers: { Location: url.href }, body: "" };
}

function handleRegister(request) {
  let meta;
  try {
    meta = JSON.parse(request.body);
  } catch {
    return oauthError(400, "invalid_client_metadata", "body is not JSON");
  }
  const redirectUris = meta?.redirect_uris;
  if (!Array.isArray(redirectUris) || !redirectUris.length) {
    return oauthError(400, "invalid_client_metadata", "redirect_uris required");
  }
  if (!redirectUris.every(isLoopbackRedirect)) {
    return oauthError(
      400,
      "invalid_redirect_uri",
      "only http loopback redirect URIs are allowed"
    );
  }
  const client = {
    clientId: uuid(),
    clientName: String(meta.client_name ?? "Unknown agent"),
    redirectUris,
  };
  clients.set(client.clientId, client);
  return json(201, {
    client_id: client.clientId,
    client_name: client.clientName,
    redirect_uris: client.redirectUris,
    token_endpoint_auth_method: "none",
    grant_types: ["authorization_code"],
    response_types: ["code"],
  });
}

function handleAuthorize(request) {
  const params = new URL("http://localhost" + request.path).searchParams;
  const clientId = params.get("client_id");
  const redirectUri = params.get("redirect_uri");
  // Registrations are in-memory, so a client re-authorizing after a browser
  // restart presents an unknown client_id. Accept unknown ids as long as the
  // redirect URI is loopback: consent is still user-mediated per request and
  // the code can only be delivered to a loopback listener.
  const client = clients.get(clientId);
  if (client && !client.redirectUris.includes(redirectUri)) {
    return oauthError(400, "invalid_request", "unregistered redirect_uri");
  }
  if (!clientId || !isLoopbackRedirect(redirectUri)) {
    return oauthError(400, "invalid_request", "bad client_id or redirect_uri");
  }
  const state = params.get("state");
  if (
    params.get("response_type") !== "code" ||
    params.get("code_challenge_method") !== "S256" ||
    !params.get("code_challenge")
  ) {
    return redirectTo(redirectUri, {
      error: "invalid_request",
      error_description: "response_type=code with S256 PKCE is required",
      state,
    });
  }
  return new Promise(resolve => {
    const req = {
      id: uuid(),
      clientId,
      clientName: client?.clientName ?? "Unknown agent",
      redirectUri,
      state,
      codeChallenge: params.get("code_challenge"),
      resolve,
      timer: null,
    };
    req.timer = setTimeout(() => MCPAuth.deny(req.id), PENDING_TTL_MS);
    pending.set(req.id, req);
    notify("pending", req);
  });
}

function handleToken(request) {
  const params = new URLSearchParams(request.body);
  if (params.get("grant_type") !== "authorization_code") {
    return oauthError(400, "unsupported_grant_type", "");
  }
  const record = codes.get(params.get("code"));
  codes.delete(params.get("code"));
  if (
    !record ||
    record.expires < Date.now() ||
    record.clientId !== params.get("client_id") ||
    record.redirectUri !== params.get("redirect_uri")
  ) {
    return oauthError(400, "invalid_grant", "unknown or mismatched code");
  }
  const verifier = params.get("code_verifier");
  if (!verifier || sha256Base64Url(verifier) !== record.codeChallenge) {
    return oauthError(400, "invalid_grant", "PKCE verification failed");
  }
  const session = onGrantCallback({
    scope: record.scope,
    clientName: record.clientName,
  });
  return json(200, { access_token: session.token, token_type: "Bearer" });
}

export const MCPAuth = {
  get pendingRequests() {
    return [...pending.values()].map(({ id, clientName }) => ({
      id,
      clientName,
    }));
  },

  /**
   * Route an HTTP request to the OAuth endpoints.
   *
   * @param {object} request
   *   Parsed HTTP request ({method, path, headers, body}).
   * @param {object} options
   * @param {string} options.origin
   *   The server origin, e.g. "http://127.0.0.1:9339".
   * @param {Function} options.onGrant
   *   Called with {scope, clientName} when a token is issued; must return the
   *   created session.
   * @returns {object | Promise<object> | null}
   *   A response verdict, a Promise of one (held /authorize), or null if the
   *   request is not an OAuth endpoint.
   */
  handleRequest(request, { origin, onGrant }) {
    onGrantCallback = onGrant;
    const path = request.path.split("?")[0];
    if (path.startsWith("/.well-known/oauth-protected-resource")) {
      return json(200, {
        resource: `${origin}/mcp`,
        authorization_servers: [origin],
      });
    }
    if (path.startsWith("/.well-known/oauth-authorization-server")) {
      return json(200, {
        issuer: origin,
        authorization_endpoint: `${origin}/authorize`,
        token_endpoint: `${origin}/token`,
        registration_endpoint: `${origin}/register`,
        response_types_supported: ["code"],
        grant_types_supported: ["authorization_code"],
        code_challenge_methods_supported: ["S256"],
        token_endpoint_auth_methods_supported: ["none"],
      });
    }
    // OAuth endpoints must not be scriptable from web content.
    if (path === "/register" || path === "/token" || path === "/authorize") {
      if (request.headers.origin) {
        return {
          status: 403,
          headers: { "Content-Type": "text/plain" },
          body: "browser origins not allowed",
        };
      }
    }
    if (path === "/register" && request.method === "POST") {
      return handleRegister(request);
    }
    if (path === "/authorize" && request.method === "GET") {
      return handleAuthorize(request);
    }
    if (path === "/token" && request.method === "POST") {
      return handleToken(request);
    }
    return null;
  },

  approve(id, scope) {
    const req = pending.get(id);
    if (!req) {
      return;
    }
    pending.delete(id);
    clearTimeout(req.timer);
    const code = uuid();
    codes.set(code, {
      clientId: req.clientId,
      clientName: req.clientName,
      redirectUri: req.redirectUri,
      codeChallenge: req.codeChallenge,
      scope: scope ?? null,
      expires: Date.now() + CODE_TTL_MS,
    });
    notify("decided", req);
    req.resolve(redirectTo(req.redirectUri, { code, state: req.state }));
  },

  deny(id) {
    const req = pending.get(id);
    if (!req) {
      return;
    }
    pending.delete(id);
    clearTimeout(req.timer);
    notify("decided", req);
    req.resolve(
      redirectTo(req.redirectUri, { error: "access_denied", state: req.state })
    );
  },

  denyAll() {
    for (const id of [...pending.keys()]) {
      this.deny(id);
    }
  },

  addListener(fn) {
    listeners.add(fn);
  },

  removeListener(fn) {
    listeners.delete(fn);
  },
};
