async () => {
  if (location.href !== "about:blank") {
    throw new Error("Expected the owned blank diagnostic tab");
  }
  document.title = "Shadow iframe move diagnostic";
  const results = [];
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
  async function ready(frame) {
    const end = performance.now() + 3000;
    while (performance.now() < end) {
      if (frame.contentDocument?.readyState === "complete" &&
          frame.contentDocument.getElementById("data")) {
        return;
      }
      await delay(20);
    }
    throw new Error("Iframe document readiness timeout");
  }
  const cases = [
    ["root", "self"], ["root", "cross-parent"],
    ["light-child", "self"], ["light-child", "cross-parent"],
    ["shadow-child", "none"], ["shadow-child", "self"],
    ["shadow-child", "cross-parent"], ["shadow-child", "appendChild"],
  ];
  for (const [shape, operation] of cases) {
    const fixture = document.createElement("section");
    const oldParent = document.createElement("div");
    const newParent = document.createElement("div");
    fixture.append(oldParent, newParent);
    document.body.append(fixture);
    try {
      const frame = document.createElement("iframe");
      frame.srcdoc = '<!doctype html><p id="data">initial</p>';
      let loads = 0;
      frame.addEventListener("load", () => loads++);
      const moving = shape === "root" ? frame : document.createElement("div");
      if (shape === "light-child") {
        moving.append(frame);
      } else if (shape === "shadow-child") {
        moving.attachShadow({mode: "open"}).append(frame);
      }
      oldParent.append(moving);
      await ready(frame);
      const originalDocument = frame.contentDocument;
      const originalWindow = frame.contentWindow;
      const root = frame.getRootNode();
      const marker = `${shape}:${operation}`;
      originalWindow.shadowMoveMarker = marker;
      originalDocument.getElementById("data").textContent = "edited";
      const sample = phase => ({
        phase, loads, connected: frame.isConnected,
        sameRoot: frame.getRootNode() === root,
        sameDocument: frame.contentDocument === originalDocument,
        sameWindow: frame.contentWindow === originalWindow,
        markerPreserved: frame.contentWindow?.shadowMoveMarker === marker,
        text: frame.contentDocument?.getElementById("data")?.textContent ?? null,
        documentReady: frame.contentDocument?.readyState ?? null,
        parent: moving.parentNode === oldParent ? "old" : "new",
      });
      const before = sample("before");
      if (!before.markerPreserved || before.text !== "edited" || before.loads !== 1) {
        throw new Error(`Uncalibrated initial state: ${JSON.stringify(before)}`);
      }
      if (operation === "self") {
        oldParent.moveBefore(moving, moving);
      } else if (operation === "cross-parent") {
        newParent.moveBefore(moving, null);
      } else if (operation === "appendChild") {
        newParent.appendChild(moving);
      }
      const immediate = sample("immediate");
      await ready(frame);
      await delay(120);
      const settled = sample("settled");
      results.push({shape, operation, before, immediate, settled});
    } catch (error) {
      results.push({shape, operation, setupOrObservationError: String(error)});
    } finally {
      fixture.remove();
    }
  }
  return {userAgent: navigator.userAgent, location: location.href,
    moveBeforeAvailable: typeof Element.prototype.moveBefore === "function",
    cases: results, remainingFixtures: document.querySelectorAll("section").length};
}
