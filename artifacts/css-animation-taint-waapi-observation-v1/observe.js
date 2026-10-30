"use strict";

const modes = ["waapi", "css", "literal"];
const report = window.waapiTaintObservations = {
  schema: "waapi-taint-observation-v1",
  status: "running",
  userAgent: navigator.userAgent,
  policyVerdict: null,
  observations: [],
};

function calibration(row) {
  const checks = [];
  const add = (name, passed) => checks.push({name, passed: Boolean(passed)});
  add("collection complete", row.error === null && row.stage === "complete");
  if (row.before) {
    add("ordinary variable before effect", row.before.variable === "vertical-rl");
  }
  if (row.active) {
    const value = row.active;
    add("active variable", value.variable === "horizontal-tb");
    add("held driver", value.timing.duration === 2000 &&
      value.timing.computedDuration === 2000 && value.timing.time === 750 &&
      Math.abs(value.timing.progress - .375) < .000001 && value.timing.state === "paused");
    add("active identity", value.effectSame && row.activeMembership?.count === 1 &&
      row.activeMembership.sameAnimation && row.activeMembership.sameEffect);
  }
  if (row.cancelled) {
    add("ordinary variable after cancellation", row.cancelled.variable === "vertical-rl");
    add("cancelled lifecycle", row.cancelled.timing.state === "idle" &&
      row.cancelled.timing.time === null && row.cancelled.effectSame &&
      row.cancelMembership?.count === 0);
  }
  if (row.mode === "literal") {
    const samples = [...row.activeSamples, ...row.cancelSamples];
    add("literal sink", row.before?.sink === "vertical-lr" &&
      row.active?.sink === "vertical-lr" && row.cancelled?.sink === "vertical-lr" &&
      samples.length === 8 && samples.every(value => value.sink === "vertical-lr"));
  }
  return checks;
}

async function observe(mode) {
  const row = {mode, stage: "setup", error: null, before: null,
    activeSamples: [], active: null, activeMembership: null,
    cancelSamples: [], cancelled: null, cancelMembership: null,
    referenceChecks: [], policyVerdict: null};
  report.observations.push(row);
  const frame = document.createElement("iframe");
  let animation;
  try {
    const loaded = new Promise(resolve => frame.onload = resolve);
    frame.srcdoc = `<!doctype html><style>
      .target { --v: vertical-rl; writing-mode: ${mode === "literal" ? "vertical-lr" : "var(--v, vertical-lr)"}; }
    </style><div class="target">sample</div>`;
    document.body.append(frame);
    await loaded;
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    const target = doc.querySelector(".target");
    const sink = () => win.getComputedStyle(target).writingMode;
    let effect;
    const details = () => {
      const style = win.getComputedStyle(target);
      const computed = effect?.getComputedTiming();
      return {sink: style.writingMode,
        variable: style.getPropertyValue("--v").trim(),
        timing: effect ? {duration: effect.getTiming().duration,
          computedDuration: computed.duration, progress: computed.progress,
          time: animation.currentTime, state: animation.playState} : null,
        effectSame: effect ? animation.effect === effect : null};
    };
    const membership = () => {
      const current = target.getAnimations();
      return {count: current.length, sameAnimation: current.includes(animation),
        sameEffect: animation.effect === effect};
    };
    const sample = async into => {
      into.push({phase: "first-read", sink: sink()});
      for (let i = 1; i <= 3; ++i) {
        await new Promise(resolve => win.requestAnimationFrame(resolve));
        into.push({phase: `passive-frame-${i}`, sink: sink()});
      }
    };
    row.before = details();
    row.stage = "create";
    if (mode === "css") {
      const sheet = doc.createElement("style");
      sheet.textContent = `@keyframes hold { from, to { --v: horizontal-tb; } }
        .target { animation: hold 2s linear both paused; }`;
      doc.head.append(sheet);
      const acquired = target.getAnimations();
      if (acquired.length !== 1) throw new Error("Expected one CSS driver");
      animation = acquired[0];
    } else {
      animation = target.animate([
        {"--v": "horizontal-tb"}, {"--v": "horizontal-tb"},
      ], {duration: 2000, fill: "both"});
      animation.pause();
    }
    effect = animation.effect;
    await animation.ready;
    animation.currentTime = 750;
    row.stage = "active samples";
    await sample(row.activeSamples);
    row.active = details();
    row.activeMembership = membership();
    row.stage = "cancel";
    animation.cancel();
    await sample(row.cancelSamples);
    row.cancelled = details();
    row.cancelMembership = membership();
    row.stage = "complete";
  } catch (error) {
    row.error = {name: error.name, message: error.message, stack: error.stack || ""};
  } finally {
    animation?.cancel();
    frame.remove();
    row.referenceChecks = calibration(row);
  }
}

(async () => {
  for (const mode of modes) await observe(mode);
  report.status = report.observations.every(row => row.error === null) ? "complete" : "incomplete";
  document.querySelector("#output").textContent = JSON.stringify(report, (_key, value) =>
    typeof value === "number" && !Number.isFinite(value) ? {nonfinite: String(value)} : value, 2);
})();
