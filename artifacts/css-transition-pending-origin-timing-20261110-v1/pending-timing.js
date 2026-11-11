"use strict";

async function runPendingTimingProbe(mode) {
  const modes = [
    "pending-cross",
    "pending-before",
    "running-cross",
    "held-cross",
  ];
  if (!modes.includes(mode)) {
    throw new TypeError("Unknown mode");
  }
  const result = {
    mode,
    checks: [],
    error: null,
    setupPassed: false,
    predictionMatches: false,
    samplingDisagreesWithOrdinaryTiming: false,
  };
  const check = (name, passed, actual) => {
    result.checks.push({ name, passed: !!passed, actual });
  };
  const target = document.createElement("div");
  target.style.marginLeft = "80px";
  document.body.append(target);
  let animation;
  try {
    check("unanimated base", getComputedStyle(target).marginLeft === "80px");
    animation = target.animate(
      { marginLeft: ["20px", "20px"] },
      { delay: 2000, duration: 10000, fill: "none" }
    );
    await animation.ready;
    check(
      "ready running animation has resolved start",
      !animation.pending &&
        animation.playState === "running" &&
        animation.startTime !== null,
      {
        pending: animation.pending,
        state: animation.playState,
        start: animation.startTime,
      }
    );
    const gap = mode === "pending-before" ? 1000 : 80;
    const seek = 2000 - gap;
    animation.currentTime = seek;
    if (mode !== "running-cross") {
      animation.pause();
    }
    if (mode === "held-cross") {
      animation.currentTime = seek;
    }
    const snapshot = () => ({
      timeline: document.timeline.currentTime,
      currentTime: animation.currentTime,
      startTime: animation.startTime,
      pending: animation.pending,
      playState: animation.playState,
      progress: animation.effect.getComputedTiming().progress,
      playbackRate: animation.playbackRate,
      performanceTime: performance.now(),
      targetMatches: animation.effect.target === target,
    });
    result.before = snapshot();
    const pending = mode === "pending-cross" || mode === "pending-before";
    check(
      "requested pending state",
      result.before.pending === pending,
      result.before
    );
    check(
      "ordinary timing is before active interval",
      result.before.progress === null && result.before.currentTime < 2000,
      result.before
    );
    check(
      "expected start-time representation",
      (result.before.startTime === null) === (mode === "held-cross"),
      result.before.startTime
    );
    const begin = performance.now();
    const wait = mode === "pending-before" ? 0 : 160;
    const deadline = Date.now() + 1000;
    while (performance.now() - begin < wait && Date.now() < deadline) {}
    check(
      "bounded wait completed",
      performance.now() - begin >= wait,
      performance.now() - begin
    );
    result.beforeStyle = snapshot();
    result.values = [
      getComputedStyle(target).marginLeft,
      getComputedStyle(target).marginLeft,
    ];
    result.after = snapshot();
    check(
      "timeline stayed fixed within the task",
      result.before.timeline === result.after.timeline,
      [result.before.timeline, result.after.timeline]
    );
    check(
      "ordinary progress remains null after style flush",
      result.after.progress === null,
      result.after.progress
    );
    check(
      "pending state survives style flush",
      result.after.pending === pending,
      result.after.pending
    );
    check(
      "start and current times are restored",
      result.before.startTime === result.after.startTime &&
        result.before.currentTime === result.after.currentTime,
      result.after
    );
    check(
      "target and rate preserved",
      result.after.targetMatches && result.after.playbackRate === 1,
      result.after
    );
    if (result.after.startTime !== null) {
      const wallTime =
        result.beforeStyle.performanceTime - result.after.startTime;
      result.approximateWallclockLocalTime = wallTime;
      check(
        "wallclock estimate reaches intended interval",
        mode === "pending-before"
          ? wallTime < 2000
          : wallTime > 2000 && wallTime < 12000,
        wallTime
      );
    }
    result.expectedStyle = mode === "pending-cross" ? "20px" : "80px";
    result.setupPassed = result.checks.every(row => row.passed);
    result.predictionMatches =
      result.setupPassed &&
      result.values.every(value => value === result.expectedStyle);
    result.samplingDisagreesWithOrdinaryTiming =
      result.setupPassed &&
      result.after.progress === null &&
      result.values.every(value => value === "20px");
  } catch (error) {
    result.error = {
      name: error.name,
      message: error.message,
      stack: error.stack,
    };
  } finally {
    animation?.cancel();
    target.remove();
  }
  return result;
}
