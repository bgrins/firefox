/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarnessBrowserTools } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessBrowserTools.sys.mjs"
);
const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);
const { PlacesTestUtils } = ChromeUtils.importESModule(
  "resource://testing-common/PlacesTestUtils.sys.mjs"
);

add_task(function test_tool_specs() {
  const specs = HarnessBrowserTools.specs();
  is(specs.length, 3, "three tools");
  for (const spec of specs) {
    is(spec.type, "function", `${spec.name} is a function tool`);
    ok(spec.description.length, `${spec.name} has a description`);
    is(spec.inputSchema.type, "object", `${spec.name} has an object schema`);
  }
});

add_task(async function test_get_open_tabs() {
  await BrowserTestUtils.withNewTab(
    "data:text/html,<title>HarnessToolTab</title>hello",
    async () => {
      const result = await HarnessBrowserTools.call("get_open_tabs", {}, {});
      ok(result.success, "tabs listed");
      ok(
        result.contentItems[0].text.includes("HarnessToolTab"),
        "current tab appears in the listing"
      );
    }
  );
});

add_task(async function test_search_history() {
  await PlacesTestUtils.addVisits({
    uri: "https://harness-tool-test.example/page",
    title: "Harness Tool Test Page",
  });
  const result = await HarnessBrowserTools.call(
    "search_browsing_history",
    { query: "harness-tool-test" },
    {}
  );
  ok(result.success, "history search succeeded");
  ok(
    result.contentItems[0].text.includes("harness-tool-test.example"),
    "seeded visit found"
  );

  const empty = await HarnessBrowserTools.call(
    "search_browsing_history",
    { query: "definitely-not-in-history-zzz" },
    {}
  );
  ok(
    empty.contentItems[0].text.includes("no history results"),
    "empty result reported"
  );
});

add_task(async function test_get_page_content_stages_to_workspace() {
  const workspace = PathUtils.join(PathUtils.profileDir, "tools-workspace");
  await BrowserTestUtils.withNewTab(
    "data:text/html,<title>Staged</title><p>secret page body for staging</p>",
    async () => {
      const tabs = await HarnessBrowserTools.call("get_open_tabs", {}, {});
      const line = tabs.contentItems[0].text
        .split("\n")
        .find(l => l.includes("Staged"));
      const tabIndex = Number(line.split(":")[0]);
      const result = await HarnessBrowserTools.call(
        "get_page_content",
        { tabIndex },
        { workspacePath: workspace }
      );
      ok(result.success, "extraction succeeded");
      const text = result.contentItems[0].text;
      ok(
        text.includes("/workspace/.browser/") && text.includes("untrusted"),
        "result points at a staged sandbox file and warns"
      );
      const dir = PathUtils.join(workspace, ".browser");
      const children = await IOUtils.getChildren(dir);
      is(children.length, 1, "one staged file");
      const staged = await IOUtils.readUTF8(children[0]);
      ok(
        staged.includes("secret page body for staging"),
        "page text staged to the workspace"
      );
    }
  );

  const bad = await HarnessBrowserTools.call(
    "get_page_content",
    { tabIndex: 999 },
    { workspacePath: workspace }
  );
  ok(!bad.success, "invalid tab index fails cleanly");
});

add_task(async function test_stage_tab_for_attachment() {
  const workspace = PathUtils.join(PathUtils.profileDir, "attach-workspace");
  await BrowserTestUtils.withNewTab(
    "data:text/html,<title>AttachMe</title><p>attached body text</p>",
    async () => {
      const tab = AgentService.listOpenTabs().find(t =>
        t.title.includes("AttachMe")
      );
      ok(tab, "tab listed via AgentService");
      const staged = await AgentService.stageTab(null, tab.index);
      // Default-session workspace when no conversation exists yet.
      ok(staged.guestPath.startsWith("/workspace/.browser/"), "guest path");
      Assert.greater(staged.chars, 0, "content staged");

      const stagedDirect = await HarnessBrowserTools.stageTab(
        tab.index,
        workspace
      );
      const content = await IOUtils.readUTF8(
        PathUtils.join(
          workspace,
          ".browser",
          stagedDirect.guestPath.split("/").pop()
        )
      );
      ok(
        content.includes("attached body text"),
        "staged file holds the page text"
      );
    }
  );
});

add_task(async function test_agentservice_tool_dispatch() {
  const events = [];
  const listener = event => events.push(event);
  AgentService.addListener(listener);
  registerCleanupFunction(() => AgentService.removeListener(listener));

  const result = await AgentService._onServerRequest({
    id: 42,
    method: "item/tool/call",
    params: {
      threadId: "t-unknown",
      turnId: "turn",
      callId: "call-1",
      tool: "get_open_tabs",
      arguments: {},
    },
  });
  ok(result.success, "tool call dispatched through AgentService");
  ok(
    events.some(
      e =>
        e.type == "item" &&
        e.item.type == "browserTool" &&
        e.item.id == "call-1"
    ),
    "browserTool item events emitted for the UI"
  );

  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.browserTools.enabled", false]],
  });
  await Assert.rejects(
    Promise.resolve().then(() =>
      AgentService._onServerRequest({
        id: 43,
        method: "item/tool/call",
        params: { tool: "get_open_tabs", arguments: {} },
      })
    ),
    /disabled/,
    "tool calls rejected when pref is off"
  );
  await SpecialPowers.popPrefEnv();

  ok(
    HarnessBrowserTools.auditLog.some(e => e.tool == "get_open_tabs"),
    "tool calls are audited"
  );
});
