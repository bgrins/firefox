async () => {
  const key = "__cssFontHandoffStatisticsV1";
  if (Object.hasOwn(window, key)) throw new Error("Setup already exists");
  const count = 5000;
  const near = (value, expected) => Math.abs(parseFloat(value) - expected) < 0.06;
  const nextFrame = win => new Promise(resolve => win.requestAnimationFrame(resolve));
  const frame = document.createElement("iframe");
  const row = { count };
  let rootAnimation;
  let childAnimation;
  const state = { frame, ready: false, acted: false };
  window[key] = state;
  try {
    const loaded = new Promise(resolve => frame.onload = resolve);
    frame.srcdoc = `<!doctype html><html><style>
      html { font-size: 16px; }
      body, #leaves { font-size: 13px; line-height: 13px; }
      #target { font-size: 11px; line-height: 11px; }
      .leaf { display: block; font-size: 13px; line-height: 13px;
        width: 1px; height: 1px; }
    </style><body><div id="target">target</div><div id="leaves"></div>`;
    (document.body || document.documentElement).append(frame);
    await loaded;
    const win = frame.contentWindow;
    const doc = win.document;
    const root = doc.documentElement;
    const target = doc.getElementById("target");
    const leaves = doc.getElementById("leaves");
    const fragment = doc.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const leaf = doc.createElement("span");
      leaf.className = "leaf";
      fragment.append(leaf);
    }
    leaves.append(fragment);
    await doc.fonts.ready;
    await nextFrame(win);
    await nextFrame(win);
    row.pre = {
      standards: doc.compatMode === "CSS1Compat",
      root: win.getComputedStyle(root).fontSize,
      target: win.getComputedStyle(target).fontSize,
      leaves: leaves.children.length,
      fixedLeaves: Array.from(leaves.children).every(leaf =>
        win.getComputedStyle(leaf).fontSize === "13px"),
      animations: doc.getAnimations().length,
    };
    if (!row.pre.standards || !near(row.pre.root, 16) || !near(row.pre.target, 11) ||
        row.pre.leaves !== count || !row.pre.fixedLeaves || row.pre.animations !== 0) {
      throw new Error("Pre-styled fixed-pixel calibration failed");
    }
    rootAnimation = root.animate([{ fontSize: "16px" }, { fontSize: "32px" }],
      { duration: 1000, fill: "both", easing: "linear" });
    rootAnimation.pause();
    await rootAnimation.ready;
    rootAnimation.currentTime = 0;
    const initialRoot = win.getComputedStyle(root).fontSize;
    childAnimation = target.animate([{ fontSize: "1rem" }, { fontSize: "3rem" }],
      { duration: 1000, fill: "both", easing: "linear" });
    childAnimation.pause();
    await childAnimation.ready;
    childAnimation.currentTime = 500;
    const initialTarget = win.getComputedStyle(target).fontSize;
    row.animation = {
      initialRoot, initialTarget,
      count: doc.getAnimations().length,
      rootTarget: rootAnimation.effect.target === root,
      childTarget: childAnimation.effect.target === target,
      rootPseudo: rootAnimation.effect.pseudoElement,
      childPseudo: childAnimation.effect.pseudoElement,
      rootPaused: rootAnimation.playState === "paused",
      childPaused: childAnimation.playState === "paused",
      rootProgress: rootAnimation.effect.getComputedTiming().progress,
      childProgress: childAnimation.effect.getComputedTiming().progress,
    };
    if (!near(initialRoot, 16) || !near(initialTarget, 32) || row.animation.count !== 2 ||
        !row.animation.rootTarget || !row.animation.childTarget ||
        row.animation.rootPseudo !== null || row.animation.childPseudo !== null ||
        !row.animation.rootPaused || !row.animation.childPaused ||
        row.animation.rootProgress !== 0 || row.animation.childProgress !== 0.5) {
      throw new Error("Paused animation calibration failed");
    }
    Object.assign(state, { win, doc, root, target, leaves, rootAnimation, childAnimation,
      ready: true, calibration: row });
    return { schema: "root-font-handoff-statistics-setup-v1", ready: true,
      userAgent: navigator.userAgent, ...row };
  } catch (error) {
    rootAnimation?.cancel();
    childAnimation?.cancel();
    frame.remove();
    delete window[key];
    throw error;
  }
}
