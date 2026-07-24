/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// about:harness is allowlisted in nsFrameLoader::TryRemoteBrowserInternal
// (like aiWindow.html) so it can host remote <browser> frames for
// agent-generated widgets. This proves the embed initializes and runs
// out-of-process.
add_task(async function test_remote_widget_embed() {
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  const widgetPath = PathUtils.join(PathUtils.profileDir, "embed-widget.html");
  await IOUtils.writeUTF8(
    widgetPath,
    `<html><body><div id="out">static</div>
     <script>document.getElementById("out").textContent = "script-ran";</script>
     </body></html>`
  );
  const file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
  file.initWithPath(widgetPath);
  const fileUrl = Services.io.newFileURI(file).spec;

  await BrowserTestUtils.withNewTab("about:harness", async browser => {
    const doc = browser.contentDocument;
    const predicted = ChromeUtils.predictRemoteTypeForURI(fileUrl, {
      window: doc.defaultView,
    });
    info(`predicted remoteType: ${predicted}`);
    const frame = doc.createXULElement("browser");
    frame.setAttribute("type", "content");
    frame.setAttribute("disableglobalhistory", "true");
    frame.setAttribute("remote", "true");
    frame.setAttribute("remoteType", predicted);
    frame.setAttribute("src", fileUrl);
    frame.style.cssText = "width:200px; height:100px;";
    const loaderCreated = BrowserTestUtils.waitForEvent(
      frame,
      "XULFrameLoaderCreated"
    );
    doc.querySelector("#chat-log").appendChild(frame);
    frame.clientTop;
    await loaderCreated;
    isnot(frame.remoteType, null, `frame is remote (${frame.remoteType})`);
    isnot(
      frame.browsingContext.currentWindowGlobal?.osPid,
      Services.appinfo.processID,
      "widget runs out of the parent process"
    );
    const scriptRan = await TestUtils.waitForCondition(async () => {
      try {
        return await SpecialPowers.spawn(
          frame.browsingContext,
          [],
          () => content.document.getElementById("out")?.textContent
        );
      } catch (e) {
        return null;
      }
    }, "widget document reachable");
    is(scriptRan, "script-ran", "script executed in the embedded browser");
  });
});
