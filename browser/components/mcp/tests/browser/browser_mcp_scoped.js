/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

async function withScopedServer(callback) {
  const tabA = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.com", "MCPPageA")
  );
  const tabB = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.org", "MCPPageB")
  );
  const scopeId = NavigableManager.getIdForBrowser(tabA.linkedBrowser);
  const otherId = NavigableManager.getIdForBrowser(tabB.linkedBrowser);
  const port = await MCPServer.start({ port: -1, scope: scopeId });
  try {
    await callback({ port, tabA, tabB, scopeId, otherId });
  } finally {
    MCPServer.stop();
    BrowserTestUtils.removeTab(tabA);
    BrowserTestUtils.removeTab(tabB);
  }
}

add_task(async function test_scoped_bridge_enforcement() {
  await withScopedServer(async ({ scopeId, otherId }) => {
    Assert.ok(MCPServer.scoped, "server is tab-scoped");
    Assert.equal(MCPBridge.scope, scopeId, "bridge scope is the granted tab");

    const tree = await MCPBridge.send("browsingContext", "getTree", {});
    Assert.equal(
      tree.contexts.length,
      1,
      "getTree only returns the granted tab"
    );
    Assert.equal(
      tree.contexts[0].context,
      scopeId,
      "getTree returns the granted tab"
    );

    await Assert.rejects(
      MCPBridge.send("browsingContext", "navigate", {
        context: otherId,
        url: "https://example.com/",
      }),
      /outside the tab/,
      "navigating another tab is denied"
    );

    await Assert.rejects(
      MCPBridge.send("browsingContext", "create", { type: "tab" }),
      /not allowed/,
      "creating a tab is denied"
    );

    await Assert.rejects(
      MCPBridge.send("browsingContext", "close", { context: scopeId }),
      /not allowed/,
      "closing the tab is denied"
    );

    await Assert.rejects(
      MCPBridge.send("browsingContext", "getTree", { "moz:scope": "chrome" }),
      /not allowed/,
      "chrome-scoped getTree is denied"
    );

    await Assert.rejects(
      MCPBridge.send("webExtension", "install", {}),
      /not allowed/,
      "extension install is denied"
    );

    Assert.throws(
      () => MCPBridge.getPref("browser.mcp.port"),
      /not allowed/,
      "pref reads are denied"
    );
    Assert.throws(
      () => MCPBridge.setPref("browser.mcp.port", 1234),
      /not allowed/,
      "pref writes are denied"
    );

    const evaluated = await MCPBridge.send("script", "evaluate", {
      expression: "document.domain",
      target: { context: scopeId },
      awaitPromise: false,
    });
    Assert.equal(
      evaluated.result.value,
      "example.com",
      "script evaluation works in the granted tab"
    );

    await Assert.rejects(
      MCPBridge.send("script", "evaluate", {
        expression: "1",
        target: { context: otherId },
        awaitPromise: false,
      }),
      /outside the tab/,
      "script evaluation in another tab is denied"
    );

    await Assert.rejects(
      MCPBridge.send("script", "evaluate", {
        expression: "1",
        target: { realm: "some-realm" },
        awaitPromise: false,
      }),
      /context target/,
      "realm-targeted script evaluation is denied"
    );
  });

  Assert.equal(MCPBridge.scope, null, "stop() clears the scope");
});

add_task(async function test_scoped_tool_surface() {
  await withScopedServer(async ({ port }) => {
    const pages = toolText(await callTool(port, "list_pages"));
    Assert.ok(pages.includes("MCPPageA"), `granted tab is listed: ${pages}`);
    Assert.ok(!pages.includes("MCPPageB"), "other tab is not listed");

    const newPage = await callTool(port, "new_page", {
      url: "https://example.org/",
    });
    Assert.ok(newPage.isError, "new_page fails in a scoped session");
    Assert.ok(
      toolText(newPage).includes("not allowed"),
      "new_page reports the scope restriction"
    );

    const prefs = await callTool(port, "get_firefox_prefs", {
      names: ["browser.mcp.port"],
    });
    Assert.ok(
      toolText(prefs).includes("not allowed"),
      "pref reads through the tool surface are denied"
    );

    const snapshot = await callTool(port, "take_snapshot", {});
    Assert.ok(!snapshot.isError, "take_snapshot works on the granted tab");
  });
});
