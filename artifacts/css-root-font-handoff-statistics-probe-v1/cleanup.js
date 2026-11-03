() => {
  const key = "__cssFontHandoffStatisticsV1";
  const state = window[key];
  if (!state) return { present: false, cleanup: true };
  const report = { present: true, action: state.result ?? null };
  try {
    if (state.ready && state.result) {
      const { win, doc, root, target, leaves, rootAnimation, childAnimation } = state;
      report.post = {
        target: win.getComputedStyle(target).fontSize,
        root: win.getComputedStyle(root).fontSize,
        leaves: leaves.children.length,
        fixedLeaves: Array.from(leaves.children).every(leaf =>
          win.getComputedStyle(leaf).fontSize === "13px"),
        animations: doc.getAnimations().length,
        rootPaused: rootAnimation.playState === "paused",
        childPaused: childAnimation.playState === "paused",
        rootTime: rootAnimation.currentTime,
        childTime: childAnimation.currentTime,
      };
    }
  } catch (error) {
    report.error = String(error);
  } finally {
    state.rootAnimation?.cancel();
    state.childAnimation?.cancel();
    state.frame.remove();
    delete window[key];
    report.cleanup = !state.frame.isConnected && !Object.hasOwn(window, key);
  }
  return report;
}
