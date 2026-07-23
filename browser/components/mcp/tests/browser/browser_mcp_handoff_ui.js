/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPUI } = ChromeUtils.importESModule(
  "moz-src:///browser/components/mcp/MCPUI.sys.mjs"
);

add_setup(async function () {
  await MCPUI.init();
  registerCleanupFunction(() => {
    MCPUI.uninit();
  });
});

add_task(async function test_handoff_and_revoke() {
  const tab = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.com", "MCPHandoffPage")
  );

  await MCPUI.handOffTab(tab);
  Assert.ok(MCPServer.running, "server started by handoff");
  Assert.ok(MCPServer.scoped, "server is scoped after handoff");
  Assert.equal(MCPUI.handoffTab, tab, "handoff tab is tracked");
  Assert.equal(
    tab.getAttribute("mcp-handoff"),
    "true",
    "handoff tab is badged"
  );

  const pages = toolText(await callTool(MCPServer.port, "list_pages"));
  Assert.ok(
    pages.includes("MCPHandoffPage"),
    `agent sees the handed-off tab: ${pages}`
  );

  MCPUI.revoke();
  Assert.ok(!MCPServer.running, "revoke stops the server");
  Assert.equal(MCPUI.handoffTab, null, "handoff tab is cleared");
  Assert.ok(!tab.hasAttribute("mcp-handoff"), "badge removed on revoke");

  BrowserTestUtils.removeTab(tab);
});

add_task(async function test_revoke_on_tab_close() {
  const tab = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    "https://example.com/"
  );
  await MCPUI.handOffTab(tab);
  Assert.ok(MCPServer.running, "server started by handoff");

  BrowserTestUtils.removeTab(tab);
  Assert.ok(!MCPServer.running, "closing the handed-off tab revokes access");
  Assert.equal(MCPUI.handoffTab, null, "handoff tab cleared on close");
});

add_task(async function test_context_menu_item() {
  const tab = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    "https://example.com/"
  );

  const menu = document.getElementById("tabContextMenu");
  const item = document.getElementById("context_mcpHandoff");
  Assert.ok(item, "handoff menu item exists in the tab context menu");

  let shown = BrowserTestUtils.waitForEvent(menu, "popupshown");
  EventUtils.synthesizeMouseAtCenter(tab, { type: "contextmenu", button: 2 });
  await shown;
  Assert.equal(
    item.getAttribute("label"),
    "Hand Off Tab to Agent",
    "menu offers handoff for a normal tab"
  );
  menu.hidePopup();

  await MCPUI.handOffTab(tab);

  shown = BrowserTestUtils.waitForEvent(menu, "popupshown");
  EventUtils.synthesizeMouseAtCenter(tab, { type: "contextmenu", button: 2 });
  await shown;
  Assert.equal(
    item.getAttribute("label"),
    "Revoke Agent Access to Tab",
    "menu offers revocation for the handed-off tab"
  );
  menu.hidePopup();

  MCPUI.revoke();
  BrowserTestUtils.removeTab(tab);
});
