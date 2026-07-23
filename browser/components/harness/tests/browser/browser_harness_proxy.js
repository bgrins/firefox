/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarnessProxy, parseClientHello } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessProxy.sys.mjs"
);
const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);
const { HttpServer } = ChromeUtils.importESModule(
  "resource://testing-common/httpd.sys.mjs"
);

function greBinPath(leaf) {
  const file = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

// Builds a minimal ClientHello byte-string with the given extensions.
function buildClientHello({ sni, ech = false } = {}) {
  const bytes = [];
  const push16 = value => bytes.push((value >> 8) & 0xff, value & 0xff);
  const extensions = [];
  if (sni) {
    const name = [...sni].map(c => c.charCodeAt(0));
    const list = [0x00, (name.length >> 8) & 0xff, name.length & 0xff, ...name];
    extensions.push(
      0x00,
      0x00,
      ((list.length + 2) >> 8) & 0xff,
      (list.length + 2) & 0xff,
      (list.length >> 8) & 0xff,
      list.length & 0xff,
      ...list
    );
  }
  if (ech) {
    extensions.push(0xfe, 0x0d, 0x00, 0x01, 0x00);
  }
  const body = [];
  body.push(0x03, 0x03); // version
  for (let i = 0; i < 32; i++) {
    body.push(0);
  }
  body.push(0); // session id
  body.push(0x00, 0x02, 0x13, 0x01); // one cipher suite
  body.push(0x01, 0x00); // compression
  body.push((extensions.length >> 8) & 0xff, extensions.length & 0xff);
  body.push(...extensions);
  const handshake = [0x01, 0x00, (body.length >> 8) & 0xff, body.length & 0xff];
  bytes.push(0x16, 0x03, 0x01);
  push16(handshake.length + body.length);
  bytes.push(...handshake, ...body);
  return String.fromCharCode(...bytes);
}

add_task(function test_clienthello_parser() {
  const hello = parseClientHello(buildClientHello({ sni: "example.com" }));
  is(hello.sni, "example.com", "SNI extracted");
  ok(!hello.hasEch, "no ECH flag");

  const withEch = parseClientHello(
    buildClientHello({ sni: "decoy.example", ech: true })
  );
  ok(withEch.hasEch, "ECH detected");

  const full = buildClientHello({ sni: "example.com" });
  is(parseClientHello(full.slice(0, 20)), null, "incomplete returns null");

  Assert.throws(
    () => parseClientHello("GET / HTTP/1.1\r\n\r\n"),
    /not a TLS handshake/,
    "non-TLS bytes rejected"
  );
});

add_task(function test_policy_matching() {
  const proxy = new HarnessProxy();
  const withList = list => {
    Services.prefs.setStringPref(
      "browser.harness.proxy.allowlist",
      JSON.stringify(list)
    );
  };
  registerCleanupFunction(() =>
    Services.prefs.clearUserPref("browser.harness.proxy.allowlist")
  );

  withList(["example.com", "*.trusted.example", "127.0.0.1:8080"]);
  ok(proxy.policy("example.com", 443).allowed, "exact host, default port");
  ok(proxy.policy("EXAMPLE.com", 80).allowed, "case-insensitive");
  ok(!proxy.policy("example.com", 8443).allowed, "non-default port denied");
  ok(!proxy.policy("evil-example.com", 443).allowed, "no substring match");
  ok(proxy.policy("a.trusted.example", 443).allowed, "wildcard subdomain");
  ok(!proxy.policy("trusted.example", 443).allowed, "wildcard needs subdomain");
  const explicit = proxy.policy("127.0.0.1", 8080);
  ok(explicit.allowed && explicit.explicit, "host:port literal is explicit");
  ok(!proxy.policy("127.0.0.1", 80).allowed, "literal port is exact");
  withList([]);
  ok(!proxy.policy("example.com", 443).allowed, "empty list denies all");
});

add_task(async function test_guest_egress_through_proxy() {
  requestLongerTimeout(3);
  if (!(await IOUtils.exists(greBinPath("libkrun.dylib")))) {
    todo(false, "harness VM deps not present; run setup-deps.sh");
    return;
  }
  for (let i = 0; !["stopped"].includes(HarnessVM.state) && i < 60; i++) {
    // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  const server = new HttpServer();
  server.registerPathHandler("/hello", (_request, response) => {
    response.setHeader("Content-Type", "text/plain");
    response.write("proxied-content");
  });
  server.start(-1);
  const port = server.identity.primaryPort;
  registerCleanupFunction(() => new Promise(resolve => server.stop(resolve)));

  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.enabled", true],
      ["browser.harness.proxy.enabled", true],
      [
        "browser.harness.proxy.allowlist",
        JSON.stringify([`127.0.0.1:${port}`]),
      ],
    ],
  });
  registerCleanupFunction(async () => {
    if (HarnessVM.state == "running") {
      await HarnessVM.stop();
    }
  });

  await HarnessVM.start();
  for (let i = 0; ; i++) {
    try {
      await HarnessVM.exec("true");
      break;
    } catch (e) {
      if (i > 40) {
        throw e;
      }
      // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
      await new Promise(resolve => setTimeout(resolve, 250));
    }
  }

  // Allowed host works through the preset http_proxy.
  const allowed = await HarnessVM.exec(
    `wget -q -O- http://127.0.0.1:${port}/hello`,
    { timeoutMs: 15000 }
  );
  is(allowed.exitCode, 0, "allowlisted fetch succeeds");
  is(allowed.stdout, "proxied-content", "content came through the proxy");

  // Non-allowlisted hosts are denied by the proxy.
  const denied = await HarnessVM.exec(
    "wget -q -O- -T 5 http://denied.invalid/ 2>&1; echo rc=$?",
    { timeoutMs: 15000 }
  );
  ok(denied.stdout.includes("rc=1"), "non-allowlisted fetch fails");

  // Without the proxy env there is no network path at all.
  const direct = await HarnessVM.exec(
    `unset http_proxy HTTP_PROXY; wget -q -O- -T 3 http://127.0.0.1:${port}/hello 2>&1; echo rc=$?`,
    { timeoutMs: 15000 }
  );
  ok(!direct.stdout.includes("proxied-content"), "direct access impossible");

  const proxy = HarnessVM.session().proxy;
  ok(
    proxy.auditLog.some(e => e.verdict == "allowed"),
    "proxy audited the allowed request"
  );
  ok(
    proxy.auditLog.some(e => e.verdict == "denied"),
    "proxy audited the denied request"
  );

  await HarnessVM.stop();
});
