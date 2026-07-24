/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);

add_task(async function test_markdown_rendering_and_sanitization() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;

    AgentService._emit({
      type: "message",
      text: "Hello **bold** with `inline code`\n\n- first\n- second",
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector("#chat-log .agent"),
      "agent bubble rendered"
    );
    const bubble = doc.querySelector("#chat-log .agent");
    is(bubble.querySelector("strong")?.textContent, "bold", "bold rendered");
    is(
      bubble.querySelector("code")?.textContent,
      "inline code",
      "inline code rendered"
    );
    is(bubble.querySelectorAll("li").length, 2, "list rendered");

    // Raw HTML in model output must never become live markup.
    AgentService._emit({
      type: "message",
      text: 'injection <img src="x" onerror="window.pwned=1"> attempt',
    });
    await TestUtils.waitForCondition(
      () => doc.querySelectorAll("#chat-log .agent").length == 2,
      "second bubble rendered"
    );
    const second = doc.querySelectorAll("#chat-log .agent")[1];
    ok(!second.querySelector("img"), "raw HTML stays inert");
    ok(
      second.textContent.includes("<img"),
      "raw HTML rendered as escaped text"
    );
    ok(!browser.contentWindow.wrappedJSObject?.pwned, "no script executed");

    // Streaming deltas re-render markdown incrementally.
    AgentService._emit({ type: "delta", text: "part **one" });
    AgentService._emit({ type: "delta", text: " two**" });
    await TestUtils.waitForCondition(
      () => doc.querySelectorAll("#chat-log .agent").length == 3,
      "streaming bubble rendered"
    );
    const streamed = doc.querySelectorAll("#chat-log .agent")[2];
    is(
      streamed.querySelector("strong")?.textContent,
      "one two",
      "markdown spanning deltas renders once complete"
    );
    AgentService._emit({ type: "turnCompleted", status: "completed" });
  });
});

add_task(async function test_present_files_html_widget() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  const workspace = PathUtils.join(PathUtils.profileDir, "widget-workspace");
  await IOUtils.makeDirectory(workspace, { ignoreExisting: true });
  const widgetPath = PathUtils.join(workspace, "widget.html");
  await IOUtils.writeUTF8(
    widgetPath,
    `<html><head></head><body><div id="out">static</div>
     <script>document.getElementById("out").textContent = "script-ran";</script>
     </body></html>`
  );

  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    const widgetTabPromise = BrowserTestUtils.waitForNewTab(
      gBrowser,
      url => url.startsWith("file://") && url.endsWith(".html"),
      true
    );
    AgentService._emit({
      type: "presentFiles",
      title: "Widget",
      files: [
        {
          name: "widget.html",
          guestPath: "/workspace/widget.html",
          hostPath: widgetPath,
          kind: "html",
          size: 100,
        },
      ],
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector("#chat-log .artifact-file.widget button"),
      "widget row with open button rendered"
    );

    // The first widget auto-opens in a tab (isolated file content process).
    const widgetTab = await widgetTabPromise;
    is(
      widgetTab.linkedBrowser.remoteType,
      "file",
      "widget runs in the file content process"
    );
    await SpecialPowers.spawn(widgetTab.linkedBrowser, [], async () => {
      await ContentTaskUtils.waitForCondition(
        () =>
          content.document.getElementById("out")?.textContent == "script-ran",
        "widget script executed"
      );
      const meta = content.document.querySelector(
        'meta[http-equiv="Content-Security-Policy"]'
      );
      Assert.ok(
        meta?.content.includes("default-src 'none'"),
        "network-blocking CSP injected into the staged copy"
      );
    });
    BrowserTestUtils.removeTab(widgetTab);
  });
});
