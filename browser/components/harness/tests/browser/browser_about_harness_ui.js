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

  // A real 1x1 PNG so the inline image path can be verified end to end.
  const png = Uint8Array.from(
    atob(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQ" +
        "DwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    ),
    c => c.charCodeAt(0)
  );
  const pngPath = PathUtils.join(workspace, "chart.png");
  await IOUtils.write(pngPath, png);

  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
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
        {
          name: "chart.png",
          guestPath: "/workspace/chart.png",
          hostPath: pngPath,
          kind: "image",
          size: png.length,
        },
      ],
    });

    // Widget renders inline in a remote browser (about:harness is
    // allowlisted for remote frames in nsFrameLoader).
    await TestUtils.waitForCondition(
      () => doc.querySelector("#chat-log .artifact-widget"),
      "inline widget frame rendered"
    );
    const frame = doc.querySelector("#chat-log .artifact-widget");
    is(frame.localName, "browser", "widget is a browser element");
    await TestUtils.waitForCondition(
      () => frame.remoteType == "file",
      "widget runs in the file content process"
    );
    const verdict = await TestUtils.waitForCondition(async () => {
      try {
        const state = await SpecialPowers.spawn(
          frame.browsingContext,
          [],
          () => {
            const meta = content.document.querySelector(
              'meta[http-equiv="Content-Security-Policy"]'
            );
            return {
              out: content.document.getElementById("out")?.textContent,
              csp: meta?.content ?? "",
            };
          }
        );
        return state.out ? state : null;
      } catch (e) {
        return null;
      }
    }, "widget document reachable");
    is(verdict.out, "script-ran", "widget script executed out of process");
    ok(
      verdict.csp.includes("default-src 'none'"),
      "network-blocking CSP injected into the staged copy"
    );
    ok(
      doc.querySelector("#chat-log .artifact-file.widget button"),
      "open-in-tab button rendered"
    );

    // Inline image renders via blob URL (requires img-src blob: in the
    // page CSP; a broken load leaves naturalWidth at 0).
    const img = doc.querySelector("#chat-log .artifact img");
    ok(img, "image element rendered");
    await TestUtils.waitForCondition(
      () => img.complete && img.naturalWidth > 0,
      "inline image actually decoded"
    );
  });
});

add_task(async function test_present_files_site_card() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  const siteRoot = PathUtils.join(
    PathUtils.profileDir,
    "harness",
    "workspace",
    "sites",
    "carddemo"
  );
  await IOUtils.makeDirectory(siteRoot, { createAncestors: true });
  await IOUtils.writeUTF8(
    PathUtils.join(siteRoot, "index.html"),
    `<html><head></head><body><div id="live">site-live</div></body></html>`
  );

  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    AgentService._emit({
      type: "presentFiles",
      title: "Site",
      files: [
        {
          name: "carddemo",
          guestPath: "/workspace/sites/carddemo/",
          url: "harness-site://carddemo/",
          kind: "site",
          size: 0,
        },
      ],
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector("#chat-log .artifact-widget"),
      "site frame rendered"
    );
    const frame = doc.querySelector("#chat-log .artifact-widget");
    is(
      frame.getAttribute("src"),
      "harness-site://carddemo/",
      "embeds the live site origin"
    );
    const buttons = [
      ...doc.querySelectorAll("#chat-log .artifact-file.widget button"),
    ].map(button => button.textContent);
    ok(
      buttons.includes("Reload") && buttons.includes("Open in tab"),
      `site card has reload/open (${buttons})`
    );
    // The embedded site actually loads (out of process, served via actor).
    const live = await TestUtils.waitForCondition(async () => {
      try {
        return await SpecialPowers.spawn(
          frame.browsingContext,
          [],
          () => content.document.getElementById("live")?.textContent
        );
      } catch (e) {
        return null;
      }
    }, "site document reachable");
    is(live, "site-live", "live site content rendered in the card");
  });
});
