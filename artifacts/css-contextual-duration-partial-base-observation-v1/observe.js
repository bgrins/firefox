"use strict";

const cases = [
  {id: "contextual-24", mode: "contextual", finalFont: 24},
  {id: "literal-24", mode: "literal", finalFont: 24},
  {id: "contextual-32", mode: "contextual", finalFont: 32},
  {id: "literal-32", mode: "literal", finalFont: 32},
];

function referenceChecks(observation) {
  const checks = [];
  const add = (name, passed) => checks.push({name, passed});
  const near = (actual, expected) => typeof actual === "number" &&
    Number.isFinite(actual) && Math.abs(actual - expected) <= 0.0001;
  if (observation.error !== null) return [{name: "collection", passed: false}];
  const snapshots = [observation.initial, observation.beforeMembership,
                     observation.afterMembership];
  add("complete passive samples", observation.samples.length === 4 &&
    observation.samples.map(sample => sample.phase).join(",") ===
      "first-read,passive-frame-1,passive-frame-2,passive-frame-3");
  add("constant composed font", snapshots.every(s => s.font === "32px"));
  add("font duration", snapshots.every(s => s.timings[0].duration === 2000));
  add("held times and states", snapshots.every(s => s.timings.every(
    timing => timing.time === 750 && timing.state === "paused")));
  add("retained membership and effects", observation.membership.count === 2 &&
    observation.membership.held.length === 2 &&
    observation.membership.held.every(item => item.animation && item.effect));
  if (observation.mode === "literal") {
    add("literal initial duration", observation.initial.timings[1].duration === 1000);
    add("literal initial output", near(observation.initial.opacity, 0.75));
    const duration = observation.finalFont / 16 * 1000;
    const progress = 750 / duration;
    add("literal final duration", snapshots.slice(1).every(s => s.timings[1].duration === duration));
    add("literal final progress", snapshots.slice(1).every(s => near(s.timings[1].progress, progress)));
    add("literal final output", observation.samples.every(s => near(s.opacity, progress)) &&
      snapshots.slice(1).every(s => near(s.opacity, progress)));
  }
  return checks;
}

function frame(win) {
  return new Promise(resolve => win.requestAnimationFrame(resolve));
}

async function observe(config) {
  const result = {...config, authoredInitialFont: 16, stage: "loading", error: null,
    acquired: null, initial: null, samples: [], beforeMembership: null,
    membership: null, afterMembership: null};
  const iframe = document.createElement("iframe");
  try {
    const loaded = new Promise(resolve => iframe.onload = resolve);
    iframe.srcdoc = `<!doctype html><html><style>
      @keyframes constant-font { from { font-size: 32px; } to { font-size: 32px; } }
      @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
      .target { font-size: 16px; animation-name: constant-font, fade;
        animation-duration: 2s, calc(1em / 16px * 1s);
        animation-timing-function: linear; animation-fill-mode: both;
        animation-play-state: paused; }
      .literal { animation-duration: 2s, 1s; }
      .final { font-size: ${config.finalFont}px; }
      .literal.final { animation-duration: 2s, ${config.finalFont / 16}s; }
    </style><body><div class="target ${config.mode}"></div></body></html>`;
    document.body.insertBefore(iframe, document.getElementById("report"));
    await loaded;
    result.stage = "acquisition";
    const win = iframe.contentWindow;
    const target = iframe.contentDocument.querySelector(".target");
    const acquired = target.getAnimations();
    result.acquired = acquired.map(animation => ({name: animation.animationName,
      time: animation.currentTime, state: animation.playState}));
    const animations = ["constant-font", "fade"].map(
      name => acquired.find(animation => animation.animationName === name));
    if (acquired.length !== 2 || !animations.every(Boolean)) {
      throw new Error("Expected exactly the two named CSS animations");
    }
    const effects = animations.map(animation => animation.effect);
    result.stage = "ready-and-hold";
    for (const animation of animations) {
      await animation.ready;
      animation.currentTime = 750;
    }
    const details = () => {
      const opacity = Number(win.getComputedStyle(target).opacity);
      const font = win.getComputedStyle(target).fontSize;
      const cssDuration = win.getComputedStyle(target).animationDuration;
      const timings = animations.map(animation => {
        const duration = animation.effect.getTiming().duration;
        const computed = animation.effect.getComputedTiming();
        return {duration, computedDuration: computed.duration, progress: computed.progress,
          time: animation.currentTime, state: animation.playState};
      });
      return {opacity, font, cssDuration, timings};
    };
    result.stage = "initial";
    for (let index = 0; index < 3; index++) await frame(win);
    result.initial = details();
    result.stage = "intervention";
    target.classList.add("final");
    const readOpacity = () => Number(win.getComputedStyle(target).opacity);
    result.samples.push({phase: "first-read", opacity: readOpacity()});
    result.stage = "passive-samples";
    for (let index = 1; index <= 3; index++) {
      await frame(win);
      result.samples.push({phase: `passive-frame-${index}`, opacity: readOpacity()});
    }
    result.stage = "details-and-membership";
    result.beforeMembership = details();
    const current = target.getAnimations();
    result.membership = {count: current.length,
      currentNames: current.map(animation => animation.animationName),
      held: animations.map((animation, index) => ({name: animation.animationName,
        animation: current.includes(animation), effect: animation.effect === effects[index]}))};
    result.afterMembership = details();
    result.stage = "complete";
  } catch (error) {
    result.error = {name: error.name, message: String(error.message), stack: error.stack ?? null};
  } finally {
    iframe.remove();
  }
  result.referenceChecks = referenceChecks(result);
  result.contextualTimingVerdict = null;
  return result;
}

function publish(report) {
  const text = JSON.stringify(report, (_key, value) =>
    typeof value === "number" && !Number.isFinite(value) ? {nonfinite: String(value)} : value, 2);
  document.getElementById("observations").textContent = text;
  document.getElementById("report").textContent = text;
  window.partialBaseObservations = report;
}

async function run() {
  const report = {schema: "partial-base-observation-v1", status: "running",
    userAgent: navigator.userAgent, contextualTimingVerdict: null, observations: []};
  publish(report);
  for (const config of cases) {
    report.observations.push(await observe(config));
    publish(report);
  }
  report.status = report.observations.every(observation => observation.error === null)
    ? "complete" : "incomplete";
  publish(report);
}

window.addEventListener("load", run, {once: true});
