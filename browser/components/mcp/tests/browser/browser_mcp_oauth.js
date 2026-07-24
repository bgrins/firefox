/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPAuth } = ChromeUtils.importESModule(
  "moz-src:///browser/components/mcp/MCPAuth.sys.mjs"
);

const REDIRECT_URI = "http://127.0.0.1:9998/callback";

async function s256(verifier) {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verifier)
  );
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function form(obj) {
  return new URLSearchParams(obj).toString();
}

async function registerClient(port, name = "OAuth Test Agent") {
  const res = await rawHttpRequest(port, {
    method: "POST",
    path: "/register",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ redirect_uris: [REDIRECT_URI], client_name: name }),
  });
  Assert.equal(res.status, 201, "registration succeeds");
  return JSON.parse(res.body);
}

async function authorizeAndApprove(
  port,
  clientId,
  { scope, challenge, state = "st" }
) {
  const authorizePromise = rawHttpRequest(port, {
    method: "GET",
    path:
      `/authorize?response_type=code&client_id=${clientId}` +
      `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&state=${state}` +
      `&code_challenge=${challenge}&code_challenge_method=S256`,
  });
  await TestUtils.waitForCondition(
    () => MCPAuth.pendingRequests.length,
    "authorize request pending"
  );
  MCPAuth.approve(MCPAuth.pendingRequests[0].id, scope);
  const res = await authorizePromise;
  Assert.equal(res.status, 302, "authorize redirects back to the client");
  return new URL(res.headers.location);
}

function exchangeCode(port, { code, clientId, verifier }) {
  return rawHttpRequest(port, {
    method: "POST",
    path: "/token",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form({
      grant_type: "authorization_code",
      code,
      redirect_uri: REDIRECT_URI,
      client_id: clientId,
      code_verifier: verifier,
    }),
  });
}

add_setup(async function () {
  await SpecialPowers.pushPrefEnv({ set: [["browser.mcp.auth", "oauth"]] });
});

add_task(async function test_full_oauth_flow() {
  const tabA = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.com", "MCPOAuthA")
  );
  const tabB = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.org", "MCPOAuthB")
  );
  const port = await MCPServer.start({ port: -1 });
  Assert.equal(MCPServer.session, null, "no session before a grant");

  const unauth = await mcpRpc(port, "ping", {}, { token: null });
  Assert.equal(unauth.status, 401, "unauthenticated /mcp is rejected");
  Assert.ok(
    unauth.headers["www-authenticate"]?.includes("resource_metadata"),
    "401 advertises protected resource metadata"
  );

  const staticToken = await mcpRpc(
    port,
    "ping",
    {},
    { token: "bidi-bridge-dev" }
  );
  Assert.equal(staticToken.status, 401, "static bundle token is rejected");

  const prm = JSON.parse(
    (
      await rawHttpRequest(port, {
        method: "GET",
        path: "/.well-known/oauth-protected-resource",
      })
    ).body
  );
  Assert.equal(prm.resource, `http://127.0.0.1:${port}/mcp`);
  Assert.equal(prm.authorization_servers[0], `http://127.0.0.1:${port}`);

  const meta = JSON.parse(
    (
      await rawHttpRequest(port, {
        method: "GET",
        path: "/.well-known/oauth-authorization-server",
      })
    ).body
  );
  Assert.ok(meta.authorization_endpoint.endsWith("/authorize"));
  Assert.ok(meta.code_challenge_methods_supported.includes("S256"));

  const { client_id } = await registerClient(port);

  const verifier = "mochitest-verifier-0123456789-0123456789";
  const challenge = await s256(verifier);
  const scopeA = NavigableManager.getIdForBrowser(tabA.linkedBrowser);
  const redirect = await authorizeAndApprove(port, client_id, {
    scope: scopeA,
    challenge,
    state: "xyz",
  });
  Assert.equal(redirect.searchParams.get("state"), "xyz", "state round-trips");
  const code = redirect.searchParams.get("code");
  Assert.ok(code, "authorization code issued");

  const tokenRes = await exchangeCode(port, {
    code,
    clientId: client_id,
    verifier,
  });
  Assert.equal(tokenRes.status, 200, "token exchange succeeds");
  const { access_token, token_type } = JSON.parse(tokenRes.body);
  Assert.equal(token_type, "Bearer");

  const session = MCPServer.session;
  Assert.ok(session, "grant created a session");
  Assert.equal(
    session.token,
    access_token,
    "access token is the session token"
  );
  Assert.equal(session.clientInfo.name, "OAuth Test Agent");
  Assert.equal(session.scope, scopeA, "session is scoped to the granted tab");

  const pages = toolText(await callTool(port, "list_pages"));
  Assert.ok(pages.includes("MCPOAuthA"), `granted tab listed: ${pages}`);
  Assert.ok(!pages.includes("MCPOAuthB"), "other tab is not listed");

  MCPServer.stop();
  BrowserTestUtils.removeTab(tabA);
  BrowserTestUtils.removeTab(tabB);
});

add_task(async function test_oauth_validation() {
  const port = await MCPServer.start({ port: -1 });

  const badReg = await rawHttpRequest(port, {
    method: "POST",
    path: "/register",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      redirect_uris: ["https://evil.example.com/callback"],
      client_name: "Evil",
    }),
  });
  Assert.equal(badReg.status, 400, "non-loopback redirect URI is rejected");

  const { client_id } = await registerClient(port);
  const verifier = "another-verifier-0123456789-0123456789";
  const challenge = await s256(verifier);

  const denyPromise = rawHttpRequest(port, {
    method: "GET",
    path:
      `/authorize?response_type=code&client_id=${client_id}` +
      `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&state=d1` +
      `&code_challenge=${challenge}&code_challenge_method=S256`,
  });
  await TestUtils.waitForCondition(() => MCPAuth.pendingRequests.length);
  MCPAuth.deny(MCPAuth.pendingRequests[0].id);
  const denied = await denyPromise;
  Assert.equal(denied.status, 302);
  Assert.equal(
    new URL(denied.headers.location).searchParams.get("error"),
    "access_denied",
    "denial redirects with access_denied"
  );

  const redirect = await authorizeAndApprove(port, client_id, {
    scope: null,
    challenge,
  });
  const code = redirect.searchParams.get("code");

  const badToken = await exchangeCode(port, {
    code,
    clientId: client_id,
    verifier: "wrong-verifier-xxxxxxxxxxxxxxxxxxxxxxxx",
  });
  Assert.equal(badToken.status, 400, "bad PKCE verifier is rejected");
  Assert.equal(JSON.parse(badToken.body).error, "invalid_grant");

  const replay = await exchangeCode(port, {
    code,
    clientId: client_id,
    verifier,
  });
  Assert.equal(replay.status, 400, "codes are single-use");

  MCPServer.stop();
});

add_task(async function test_new_grant_replaces_session() {
  const port = await MCPServer.start({ port: -1 });
  const { client_id } = await registerClient(port);

  const v1 = "verifier-one-0123456789-0123456789";
  const r1 = await authorizeAndApprove(port, client_id, {
    scope: null,
    challenge: await s256(v1),
  });
  const t1 = JSON.parse(
    (
      await exchangeCode(port, {
        code: r1.searchParams.get("code"),
        clientId: client_id,
        verifier: v1,
      })
    ).body
  ).access_token;
  const firstSession = MCPServer.session;
  Assert.equal(firstSession.token, t1);

  const v2 = "verifier-two-0123456789-0123456789";
  const r2 = await authorizeAndApprove(port, client_id, {
    scope: null,
    challenge: await s256(v2),
  });
  const t2 = JSON.parse(
    (
      await exchangeCode(port, {
        code: r2.searchParams.get("code"),
        clientId: client_id,
        verifier: v2,
      })
    ).body
  ).access_token;

  Assert.equal(
    firstSession.state,
    "revoked",
    "old session revoked by new grant"
  );
  const stale = await mcpRpc(port, "ping", {}, { token: t1 });
  Assert.equal(stale.status, 401, "old token is rejected");
  const fresh = await mcpRpc(port, "ping", {}, { token: t2 });
  Assert.equal(fresh.status, 200, "new token works");

  MCPServer.stop();
});
