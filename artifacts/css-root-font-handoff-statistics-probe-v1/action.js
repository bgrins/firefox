() => {
  const state = window.__cssFontHandoffStatisticsV1;
  if (!state?.ready || state.acted) throw new Error("Action requires unused ready setup");
  state.acted = true;
  const { win, rootAnimation, target } = state;
  const start = win.performance.now();
  rootAnimation.currentTime = 1000;
  const value = win.getComputedStyle(target).fontSize;
  const elapsedMs = win.performance.now() - start;
  state.result = { schema: "root-font-handoff-statistics-action-v1", count: 5000,
    currentTime: 1000, expected: 64, value, elapsedMs,
    valid: Math.abs(parseFloat(value) - 64) < 0.06 &&
      Number.isFinite(elapsedMs) && elapsedMs >= 0 };
  return state.result;
}
