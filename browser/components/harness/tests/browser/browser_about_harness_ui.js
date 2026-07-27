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

add_task(async function test_empty_state_and_file_change_rendering() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    const empty = doc.getElementById("chat-empty");
    ok(empty, "empty state rendered on a fresh chat");
    const example = empty.querySelector(".example-prompt");
    example.click();
    is(
      doc.getElementById("chat-input").value,
      example.textContent,
      "example prompt fills the input"
    );

    // apply_patch fileChange items render kind badges and colored diffs.
    AgentService._emit({
      type: "item",
      phase: "completed",
      item: {
        type: "fileChange",
        id: "fc1",
        status: "completed",
        changes: [
          {
            path: "/workspace/app.js",
            kind: { type: "update", move_path: null },
            diff: "@@ -1 +1 @@\n-old\n+new\n",
          },
        ],
      },
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector(".file-change"),
      "file change row rendered"
    );
    ok(!doc.getElementById("chat-empty"), "empty state cleared by activity");
    is(
      doc.querySelector(".file-change .chip").textContent,
      "update",
      "kind badge rendered"
    );
    ok(
      doc
        .querySelector(".file-change-path")
        .textContent.includes("/workspace/app.js"),
      "path rendered"
    );
    const added = [...doc.querySelectorAll("pre.diff .diff-add")];
    const removed = [...doc.querySelectorAll("pre.diff .diff-del")];
    ok(
      added.some(span => span.textContent.includes("+new")),
      "added line highlighted"
    );
    ok(
      removed.some(span => span.textContent.includes("-old")),
      "removed line highlighted"
    );
    AgentService._emit({ type: "turnCompleted", status: "completed" });
  });
});

add_task(async function test_streamed_reasoning() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    AgentService._emit({
      type: "reasoningDelta",
      itemId: "r1",
      text: "Planning the",
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector(".activity-row.thinking"),
      "thinking row appears on first delta"
    );
    const row = doc.querySelector(".activity-row.thinking");
    ok(
      row.querySelector("summary").textContent.includes("Planning the"),
      "first delta streams into the summary line"
    );
    AgentService._emit({
      type: "reasoningDelta",
      itemId: "r1",
      text: " approach",
    });
    await TestUtils.waitForCondition(
      () => row.querySelector("div").textContent == "Planning the approach",
      "subsequent deltas append"
    );
    // The completed item replaces the streamed buffer in the same row.
    AgentService._emit({
      type: "item",
      phase: "completed",
      item: {
        type: "reasoning",
        id: "r1",
        summary: ["Planning the approach\n\nDone thinking."],
        content: [],
      },
    });
    await TestUtils.waitForCondition(
      () => row.querySelector("div").textContent.includes("Done thinking."),
      "completed item takes over the row"
    );
    is(
      doc.querySelectorAll(".activity-row.thinking").length,
      1,
      "streaming and completion share one row"
    );
    AgentService._emit({ type: "turnCompleted", status: "completed" });
  });
});

add_task(async function test_user_input_card() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    AgentService._emit({
      type: "userInputRequest",
      requestId: "ui-test-req",
      questions: [
        {
          id: "framework",
          header: "Framework",
          question: "Which framework should I use?",
          isOther: true,
          options: [
            { label: "Vanilla JS (Recommended)", description: "no deps" },
            { label: "React", description: "bundled via bun" },
          ],
        },
      ],
      autoResolutionMs: 120000,
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector(".user-input-question"),
      "question card rendered"
    );
    const card = doc.querySelector(".activity-row.user-input");
    is(
      card.querySelectorAll(".user-input-choices button").length,
      2,
      "both options rendered"
    );
    ok(card.querySelector("input[type=text]"), "free-form Other input present");
    ok(
      card.textContent.includes("continues automatically"),
      "auto-resolution note shown"
    );
    card.querySelector(".user-input-choices button").click();
    await TestUtils.waitForCondition(
      () => !card.querySelector("button"),
      "card collapses after answering"
    );
    ok(
      card.textContent.includes(
        "Which framework should I use? → Vanilla JS (Recommended)"
      ),
      "static summary shows the chosen answer"
    );

    // A second card retired by serverRequest/resolved (e.g. interrupt).
    AgentService._emit({
      type: "userInputRequest",
      requestId: "ui-test-req-2",
      questions: [
        {
          id: "q2",
          header: "Q2",
          question: "Still there?",
          isOther: true,
          options: [{ label: "Yes", description: "" }],
        },
      ],
      autoResolutionMs: null,
    });
    await TestUtils.waitForCondition(
      () => doc.querySelectorAll(".activity-row.user-input").length == 2,
      "second card rendered"
    );
    AgentService._emit({
      type: "serverRequestResolved",
      requestId: "ui-test-req-2",
      reason: "resolved",
    });
    const second = doc.querySelectorAll(".activity-row.user-input")[1];
    await TestUtils.waitForCondition(
      () => !second.querySelector("button"),
      "retired card loses its buttons"
    );
    ok(
      second.textContent.includes("no longer needed"),
      "retired card explains itself"
    );
    AgentService._emit({ type: "turnCompleted", status: "completed" });
  });
});

add_task(async function test_plan_checklist_rendering() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    AgentService._emit({
      type: "plan",
      explanation: "Build the app",
      plan: [
        { step: "write index.html", status: "inProgress" },
        { step: "add styling", status: "pending" },
      ],
    });
    await TestUtils.waitForCondition(
      () => doc.querySelector(".activity-row.plan"),
      "plan row rendered"
    );
    const row = doc.querySelector(".activity-row.plan");
    is(
      row.querySelector(".plan-title").textContent,
      "Build the app",
      "explanation shown"
    );
    is(row.querySelectorAll(".plan-step").length, 2, "two steps");
    ok(
      row.querySelector(".plan-step.inProgress").textContent.startsWith("[~]"),
      "in-progress marker"
    );

    // Updates replace the same row in place.
    AgentService._emit({
      type: "plan",
      explanation: "",
      plan: [
        { step: "write index.html", status: "completed" },
        { step: "add styling", status: "inProgress" },
      ],
    });
    await TestUtils.waitForCondition(
      () => row.querySelector(".plan-step.completed"),
      "step ticked over to completed"
    );
    is(
      doc.querySelectorAll(".activity-row.plan").length,
      1,
      "still a single plan row"
    );
    ok(
      row.querySelector(".plan-step.completed").textContent.startsWith("[x]"),
      "completed marker"
    );
    AgentService._emit({ type: "turnCompleted", status: "completed" });
  });
});

add_task(async function test_history_resume_replays_journal() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  const workspace = PathUtils.join(PathUtils.profileDir, "replay-workspace");
  await IOUtils.makeDirectory(workspace, { ignoreExisting: true });
  const png = Uint8Array.from(
    atob(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQ" +
        "DwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    ),
    c => c.charCodeAt(0)
  );
  const pngPath = PathUtils.join(workspace, "plot.png");
  await IOUtils.write(pngPath, png);

  const events = [
    { type: "userMessage", conversationId: "replay-conv", text: "make a plot" },
    {
      type: "item",
      phase: "completed",
      conversationId: "replay-conv",
      item: {
        type: "commandExecution",
        id: "c1",
        status: "completed",
        command: "uv run plot.py",
        exitCode: 0,
        aggregatedOutput: "saved plot.png",
      },
    },
    {
      type: "presentFiles",
      conversationId: "replay-conv",
      title: "Plot",
      files: [
        {
          name: "plot.png",
          guestPath: "/workspace/plot.png",
          hostPath: pngPath,
          kind: "image",
          size: png.length,
        },
      ],
    },
    { type: "message", conversationId: "replay-conv", text: "here you go" },
    {
      type: "turnCompleted",
      conversationId: "replay-conv",
      status: "completed",
    },
  ];
  const original = AgentService.resumeConversation;
  AgentService.resumeConversation = async () => ({
    conversationId: "replay-conv",
    model: "test-model",
    modelProvider: "test",
    turns: [],
    events,
  });
  registerCleanupFunction(() => {
    AgentService.resumeConversation = original;
  });

  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    const win = browser.contentWindow;
    const select = doc.getElementById("chat-history");
    const option = doc.createElement("option");
    option.value = "replay-conv";
    select.appendChild(option);
    select.value = "replay-conv";
    select.dispatchEvent(new win.Event("change"));

    await TestUtils.waitForCondition(
      () => doc.querySelector("#chat-log .artifact img"),
      "replayed artifact image rendered"
    );
    is(
      doc.querySelector("#chat-log .user")?.textContent,
      "make a plot",
      "user bubble replayed"
    );
    ok(
      [...doc.querySelectorAll("#chat-log .agent")].some(b =>
        b.textContent.includes("here you go")
      ),
      "agent message replayed"
    );
    const command = doc.querySelector(".activity-row.command");
    ok(command?.textContent.includes("uv run plot.py"), "command row replayed");
    ok(
      command
        ?.querySelector(".command-output pre")
        ?.textContent.includes("saved plot.png"),
      "command output replayed"
    );
    const activity = doc.querySelector("#chat-log .activity");
    ok(
      !activity.classList.contains("working"),
      "replayed activity is finalized, not spinning"
    );
    ok(
      doc.getElementById("chat-interrupt").hidden &&
        !doc.getElementById("chat-send").disabled,
      "controls usable after replay"
    );
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
