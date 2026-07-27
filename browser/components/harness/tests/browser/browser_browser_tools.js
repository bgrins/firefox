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
  is(specs.length, 4, "four tools");
  for (const spec of specs) {
    is(spec.type, "function", `${spec.name} is a function tool`);
    ok(spec.description.length, `${spec.name} has a description`);
    is(spec.inputSchema.type, "object", `${spec.name} has an object schema`);
  }
});

add_task(async function test_present_files() {
  const workspace = PathUtils.join(PathUtils.profileDir, "present-workspace");
  await IOUtils.makeDirectory(workspace, { ignoreExisting: true });
  // Minimal valid 1x1 PNG.
  const png = Uint8Array.from(
    atob(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQ" +
        "DwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    ),
    c => c.charCodeAt(0)
  );
  await IOUtils.write(PathUtils.join(workspace, "plot.png"), png);
  await IOUtils.writeUTF8(PathUtils.join(workspace, "report.txt"), "hi");
  await IOUtils.writeUTF8(
    PathUtils.join(workspace, "widget.html"),
    "<html><body>widget</body></html>"
  );

  const result = await HarnessBrowserTools.call(
    "present_files",
    {
      paths: ["/workspace/plot.png", "report.txt", "widget.html"],
      title: "Results",
    },
    { workspacePath: workspace }
  );
  ok(result.success, "present succeeded");
  is(result.present.title, "Results", "title carried through");
  is(result.present.files.length, 3, "three files");
  is(result.present.files[0].kind, "image", "png detected as image");
  is(result.present.files[1].kind, "file", "txt is a generic file");
  is(result.present.files[2].kind, "html", "html detected as widget");
  is(
    result.present.files[0].guestPath,
    "/workspace/plot.png",
    "guest path preserved"
  );
  ok(
    result.present.files[0].hostPath.endsWith("plot.png"),
    "host path resolved"
  );
  ok(
    result.contentItems[0].text.includes("plot.png"),
    "model reply names the files"
  );

  const missing = await HarnessBrowserTools.call(
    "present_files",
    { paths: ["/workspace/nope.png"] },
    { workspacePath: workspace }
  );
  ok(!missing.success, "missing file fails cleanly");

  const escape = await HarnessBrowserTools.call(
    "present_files",
    { paths: ["/workspace/../../../etc/hosts"] },
    { workspacePath: workspace }
  );
  ok(!escape.success, "path traversal denied");

  // Site paths present the live origin once, however many files are named.
  await IOUtils.makeDirectory(PathUtils.join(workspace, "sites", "demo"), {
    createAncestors: true,
  });
  await IOUtils.writeUTF8(
    PathUtils.join(workspace, "sites", "demo", "index.html"),
    "<html><body>demo</body></html>"
  );
  const site = await HarnessBrowserTools.call(
    "present_files",
    {
      paths: [
        "/workspace/sites/demo/index.html",
        "/workspace/sites/demo/app.js",
        "sites/demo",
      ],
    },
    { workspacePath: workspace }
  );
  ok(site.success, "site present succeeded");
  is(site.present.files.length, 1, "site deduped to one entry");
  is(site.present.files[0].kind, "site", "classified as site");
  is(site.present.files[0].url, "harness-site://demo/", "live origin url");

  const noIndex = await HarnessBrowserTools.call(
    "present_files",
    { paths: ["/workspace/sites/empty/whatever.js"] },
    { workspacePath: workspace }
  );
  ok(!noIndex.success, "site without index.html fails");
  ok(
    noIndex.contentItems[0].text.includes("index.html"),
    "error tells the agent what is missing"
  );

  // A guest-created symlink resolves against the HOST filesystem here; it
  // must not be presentable when it escapes the workspace.
  const link = PathUtils.join(workspace, "sneaky.png");
  await IOUtils.remove(link, { ignoreAbsent: true });
  const linkTarget = "/etc/hosts";
  const { Subprocess } = ChromeUtils.importESModule(
    "resource://gre/modules/Subprocess.sys.mjs"
  );
  const proc = await Subprocess.call({
    command: "/bin/ln",
    arguments: ["-s", linkTarget, link],
  });
  await proc.wait();
  const symlink = await HarnessBrowserTools.call(
    "present_files",
    { paths: ["/workspace/sneaky.png"] },
    { workspacePath: workspace }
  );
  ok(!symlink.success, "symlink escaping the workspace denied");
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

add_task(async function test_journal_roundtrip() {
  const id = "journal-test-conv";
  AgentService._conversations.set(id, { activeTurnId: null, persist: true });
  registerCleanupFunction(async () => {
    AgentService._conversations.delete(id);
    await IOUtils.remove(AgentService._journalPath(id), {
      ignoreAbsent: true,
    });
  });

  AgentService._maybeJournal({
    type: "userMessage",
    conversationId: id,
    text: "hi",
  });
  AgentService._maybeJournal({ type: "delta", conversationId: id, text: "x" });
  AgentService._maybeJournal({
    type: "item",
    phase: "started",
    conversationId: id,
    item: { type: "commandExecution", id: "c1" },
  });
  AgentService._maybeJournal({
    type: "item",
    phase: "completed",
    conversationId: id,
    item: { type: "commandExecution", id: "c1", command: "ls", exitCode: 0 },
  });
  AgentService._maybeJournal({
    type: "presentFiles",
    conversationId: id,
    title: "T",
    files: [],
  });
  AgentService._maybeJournal({
    type: "message",
    conversationId: id,
    text: "done",
  });
  AgentService._maybeJournal({ type: "turnCompleted", conversationId: id });
  await AgentService._journalWrites;

  const events = await AgentService._readJournal(id);
  Assert.deepEqual(
    events.map(e => e.type),
    ["userMessage", "item", "presentFiles", "message", "turnCompleted"],
    "deltas and in-progress items are not journaled; the rest replay in order"
  );
  is(events[1].item.command, "ls", "completed item payload preserved");
  ok(
    events.every(e => e.at),
    "events are timestamped"
  );

  // Temporary conversations and unknown conversation ids never journal.
  AgentService._conversations.set(id, { persist: false });
  AgentService._maybeJournal({
    type: "message",
    conversationId: id,
    text: "tmp",
  });
  AgentService._maybeJournal({
    type: "message",
    conversationId: "never-created",
    text: "stray",
  });
  await AgentService._journalWrites;
  is((await AgentService._readJournal(id)).length, 5, "persist:false skipped");
  is(
    (await AgentService._readJournal("never-created")).length,
    0,
    "unknown conversation skipped"
  );

  // A torn tail line (crash mid-append) is skipped, not fatal.
  await IOUtils.writeUTF8(AgentService._journalPath(id), '{"type":"mess', {
    mode: "appendOrCreate",
  });
  is((await AgentService._readJournal(id)).length, 5, "torn tail line ignored");
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
