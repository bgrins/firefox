/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// harness-site://<name>/ serves agent-published sites from
// profile/harness/sites/<name>/ with real per-site origins. This proves the
// properties that make sites "real": distinct origins, isolated and
// persistent localStorage, same-origin fetch, injected CSP, secure context.

async function writeSite(name, files) {
  const root = PathUtils.join(
    PathUtils.profileDir,
    "harness",
    "workspace",
    "sites",
    name
  );
  await IOUtils.makeDirectory(root, { createAncestors: true });
  for (const [leaf, content] of Object.entries(files)) {
    await IOUtils.writeUTF8(PathUtils.join(root, leaf), content);
  }
}

const SITE_HTML = `<!DOCTYPE html><html><head><title>site</title></head><body>
<div id="status">loading</div>
<script>
  const el = document.getElementById("status");
  (async () => {
    let previous = "ls-error";
    let counter = "ls-error";
    try {
      previous = localStorage.getItem("counter") ?? "none";
      localStorage.setItem("counter", String(Number(previous == "none" ? 0 : previous) + 1));
      counter = localStorage.getItem("counter");
    } catch (e) {
      previous = counter = "ls-error:" + e.name;
    }
    let session = "ss-error";
    try {
      sessionStorage.setItem("s", "1");
      session = sessionStorage.getItem("s");
    } catch (e) {
      session = "ss-error:" + e.name;
    }
    let idb = "idb-error";
    try {
      idb = await new Promise((resolve, reject) => {
        const request = indexedDB.open("probe", 1);
        request.onupgradeneeded = () => request.result.createObjectStore("kv");
        request.onsuccess = () => { request.result.close(); resolve("idb-ok"); };
        request.onerror = () => reject(request.error);
      });
    } catch (e) {
      idb = "idb-error:" + (e?.name ?? e);
    }
    let fetched = "no-fetch";
    try {
      const response = await fetch("data.json");
      fetched = (await response.json()).value;
    } catch (e) {
      fetched = "fetch-error: " + e.message;
    }
    el.textContent = ["ok", previous, counter, fetched,
      window.isSecureContext, location.origin, session, idb].join("|");
  })();
</script></body></html>`;

add_task(async function test_harness_site_scheme() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await writeSite("alpha.harness", {
    "index.html": SITE_HTML,
    "data.json": '{"value": "alpha-data"}',
  });
  await writeSite("beta.harness", {
    "index.html": SITE_HTML,
    "data.json": '{"value": "beta-data"}',
  });

  const read = browser =>
    SpecialPowers.spawn(browser, [], () =>
      ContentTaskUtils.waitForCondition(() => {
        const text = content.document.getElementById("status")?.textContent;
        return text?.startsWith("ok") ? text : null;
      }, "site script ran")
    );

  // Site alpha: storage works, fetch works, secure context, right origin.
  let first;
  await BrowserTestUtils.withNewTab(
    "harness-site://alpha.harness/",
    async browser => {
      first = (await read(browser)).split("|");
      info(`probe state: ${first.join(" | ")}`);
      is(first[6], "1", "sessionStorage works");
      is(first[7], "idb-ok", "indexedDB works (quota scheme allowlist)");
      // localStorage needs a valid window ClientInfo; dom/clients validation
      // compares MozURL origins, so the scheme is allowlisted in
      // netwerk/base/mozurl get_origin.
      is(first[1], "none", "localStorage first visit starts empty");
      is(first[2], "1", "localStorage write/read works (mozurl origin)");
      is(first[3], "alpha-data", "same-origin fetch works");
      is(first[4], "true", "secure context (URI_IS_POTENTIALLY_TRUSTWORTHY)");
      // WHATWG serializes non-special-scheme origins as opaque; the internal
      // principal origin is real (asserted below via the parent).
      todo_is(first[5], "harness-site://alpha.harness", "web-exposed origin");
      const principal =
        browser.browsingContext.currentWindowGlobal.documentPrincipal;
      is(
        principal.origin,
        "harness-site://alpha.harness",
        "principal origin is real"
      );
      ok(!principal.isNullPrincipal, "content principal, not null");
      isnot(
        browser.browsingContext.currentWindowGlobal.osPid,
        Services.appinfo.processID,
        "site loads out of the parent process"
      );
      const csp = await SpecialPowers.spawn(
        browser,
        [],
        () =>
          content.document.querySelector(
            'meta[http-equiv="Content-Security-Policy"]'
          )?.content ?? ""
      );
      ok(
        csp.includes("default-src 'self'"),
        `CSP injected (${csp.slice(0, 40)})`
      );
    }
  );

  // Second visit to alpha: localStorage persisted across the navigation.
  await BrowserTestUtils.withNewTab(
    "harness-site://alpha.harness/",
    async browser => {
      const again = (await read(browser)).split("|");
      is(again[1], "1", "localStorage persists across visits");
      is(again[2], "2", "counter increments on revisit");
    }
  );

  // Site beta: its own files, its own principal, isolated storage.
  await BrowserTestUtils.withNewTab(
    "harness-site://beta.harness/",
    async browser => {
      const beta = (await read(browser)).split("|");
      is(beta[3], "beta-data", "beta serves its own files");
      is(beta[1], "none", "beta's localStorage is isolated from alpha");
      is(
        browser.browsingContext.currentWindowGlobal.documentPrincipal.origin,
        "harness-site://beta.harness",
        "distinct principal origin per site"
      );
    }
  );

  // Dynamic-without-a-server patterns: WASM instantiation under the site
  // CSP, and data files re-read fresh from disk on every same-origin fetch.
  const dynRoot = PathUtils.join(
    PathUtils.profileDir,
    "harness",
    "workspace",
    "sites",
    "dyn.harness"
  );
  await IOUtils.makeDirectory(PathUtils.join(dynRoot, "data"), {
    createAncestors: true,
  });
  // Minimal valid (empty) wasm module: magic + version.
  await IOUtils.write(
    PathUtils.join(dynRoot, "mod.wasm"),
    Uint8Array.from([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
  );
  await IOUtils.writeUTF8(
    PathUtils.join(dynRoot, "data", "live.json"),
    '{"value": "v1"}'
  );
  await writeSite("dyn.harness", {
    "index.html": `<!DOCTYPE html><html><head></head><body>
<div id="wasm">pending</div><div id="data">pending</div>
<script>
  (async () => {
    try {
      await WebAssembly.instantiateStreaming(fetch("mod.wasm"));
      document.getElementById("wasm").textContent = "wasm-ok";
    } catch (e) {
      document.getElementById("wasm").textContent = "wasm-error:" + e.name;
    }
    setInterval(async () => {
      const data = await (await fetch("data/live.json")).json();
      document.getElementById("data").textContent = "data:" + data.value;
    }, 100);
  })();
</script></body></html>`,
  });
  await BrowserTestUtils.withNewTab(
    "harness-site://dyn.harness/",
    async browser => {
      const readState = id =>
        SpecialPowers.spawn(
          browser,
          [id],
          elementId => content.document.getElementById(elementId)?.textContent
        );
      await TestUtils.waitForCondition(
        async () => (await readState("wasm")) != "pending",
        "wasm attempt settled"
      );
      is(
        await readState("wasm"),
        "wasm-ok",
        "instantiateStreaming works (CSP wasm-unsafe-eval + clean MIME)"
      );
      await TestUtils.waitForCondition(
        async () => (await readState("data")) == "data:v1",
        "initial data file value fetched"
      );
      // The agent rewrites the data file; the open site sees it on its
      // next fetch with no server and no reload.
      await IOUtils.writeUTF8(
        PathUtils.join(dynRoot, "data", "live.json"),
        '{"value": "v2"}'
      );
      await TestUtils.waitForCondition(
        async () => (await readState("data")) == "data:v2",
        "rewritten data file served fresh to the open site"
      );
    }
  );

  // BiDi/webdriver can automate sites without system access (the scheme is
  // in webdriverSafeSchemes; agents QA their own published sites this way).
  const { isWebdriverSafeNavigationURL } = ChromeUtils.importESModule(
    "chrome://remote/content/shared/BrowsingContextUtils.sys.mjs"
  );
  ok(
    isWebdriverSafeNavigationURL(
      Services.io.newURI("harness-site://alpha.harness/"),
      gBrowser.selectedBrowser.browsingContext
    ),
    "harness-site navigation is webdriver-safe"
  );

  // Path traversal denied at the serving layer.
  const { HarnessSiteParent } = ChromeUtils.importESModule(
    "moz-src:///browser/components/harness/actors/HarnessSiteParent.sys.mjs"
  );
  await Assert.rejects(
    HarnessSiteParent.fetchSite(
      "harness-site://alpha.harness/../../../prefs.js"
    ),
    /traversal|NotFound/i,
    "traversal denied"
  );
  await Assert.rejects(
    HarnessSiteParent.fetchSite("harness-site://alpha.harness/nope.html"),
    /./,
    "missing file rejects"
  );
});
