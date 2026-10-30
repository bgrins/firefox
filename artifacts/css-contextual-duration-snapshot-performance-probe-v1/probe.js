"use strict";

function summarize(values) {
  if (!values.length) {
    return null;
  }
  const sorted = [...values].sort((a, b) => a - b);
  const quantile = p => {
    const index = (sorted.length - 1) * p;
    const lower = Math.floor(index);
    return sorted[lower] + (sorted[Math.ceil(index)] - sorted[lower]) * (index - lower);
  };
  return {count: values.length, min: sorted[0], p10: quantile(0.1), median: quantile(0.5),
    p90: quantile(0.9), p95: quantile(0.95), max: sorted.at(-1),
    mean: values.reduce((sum, value) => sum + value, 0) / values.length};
}

function readConfig(values) {
  const config = {label: String(values.label || "unlabelled").slice(0, 80)};
  for (const [name, min, max] of [["count", 1, 3000], ["iterations", 1, 500],
    ["warmup", 0, 100], ["rounds", 1, 10]]) {
    const value = Number(values[name]);
    if (!Number.isInteger(value) || value < min || value > max) {
      throw new Error(`${name} must be an integer from ${min} to ${max}`);
    }
    config[name] = value;
  }
  if (!["outline", "font"].includes(values.order) || !["yes", "no"].includes(values.mask)) {
    throw new Error("Invalid case order or font-animation setting");
  }
  if (config.count * (config.iterations + config.warmup) * config.rounds > 3000000) {
    throw new Error("Reduce settings to at most 3,000,000 element-iterations per case");
  }
  return {...config, order: values.order, mask: values.mask};
}

function setupPage() {
  const names = ["label", "count", "iterations", "warmup", "rounds", "order", "mask"];
  const fields = Object.fromEntries(names.map(name => [name, document.getElementById(name)]));
  const stage = document.getElementById("stage");
  const output = document.getElementById("output");
  const status = document.getElementById("status");
  const run = document.getElementById("run");
  const stop = document.getElementById("stop");
  const download = document.getElementById("download");
  const presets = [document.getElementById("small"), document.getElementById("large")];
  let stopped = false;
  let becameHidden = false;
  let running = false;
  let report = null;
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  const values = () => Object.fromEntries(names.map(name => [name, fields[name].value]));
  const setValues = incoming => {
    for (const name of names) {
      if (incoming[name] !== undefined) {
        fields[name].value = incoming[name];
      }
    }
  };
  setValues(Object.fromEntries(new URLSearchParams(location.hash.slice(1))));
  presets[0].addEventListener("click", () => setValues({count: 50, iterations: 20, warmup: 5, rounds: 2}));
  presets[1].addEventListener("click", () => setValues({count: 1000, iterations: 100, warmup: 20, rounds: 3}));
  stop.addEventListener("click", () => { stopped = true; });
  document.addEventListener("visibilitychange", () => {
    if (running && document.visibilityState !== "visible") {
      becameHidden = true;
    }
  });
  const checkRunning = () => {
    if (stopped || becameHidden || document.visibilityState !== "visible") {
      throw new Error(stopped ? "Stopped by operator" : "Tab became hidden");
    }
  };
  const finalValues = targets => {
    const histograms = {opacity: {}, fontSize: {}, outlineColor: {}, fadeDuration: {}, fadeProgress: {}};
    const examples = [];
    let held = 0;
    for (let index = 0; index < targets.length; index++) {
      const {element, animations, fade} = targets[index];
      const style = getComputedStyle(element);
      const value = {opacity: style.opacity, fontSize: style.fontSize, outlineColor: style.outlineColor,
        fadeDuration: fade.effect.getTiming().duration, fadeProgress: fade.effect.getComputedTiming().progress};
      for (const [name, item] of Object.entries(value)) {
        const key = String(item);
        histograms[name][key] = (histograms[name][key] || 0) + 1;
      }
      held += Number(animations.every(a => a.currentTime === 750 && a.playState === "paused"));
      if (index === 0 || index === targets.length - 1) {
        examples.push({index, ...value});
      }
    }
    return {count: targets.length, allAnimationsHeldAt750ms: held === targets.length,
      heldElementCount: held, histograms, examples};
  };
  async function oneCase(config, workload, round) {
    stage.className = config.mask === "no" ? "unmasked" : "";
    const fragment = document.createDocumentFragment();
    const elements = Array.from({length: config.count}, () => {
      const element = document.createElement("div");
      element.className = "target";
      fragment.append(element);
      return element;
    });
    stage.replaceChildren(fragment);
    const targets = elements.map(element => {
      const animations = element.getAnimations();
      const fade = animations.find(a => a.animationName === "fade");
      if (!fade || animations.length !== (config.mask === "yes" ? 2 : 1)) {
        throw new Error("Expected CSS animations were not created");
      }
      return {element, animations, fade};
    });
    await Promise.all(targets.flatMap(t => t.animations.map(a => a.ready)));
    for (const target of targets) {
      for (const animation of target.animations) {
        animation.currentTime = 750;
      }
    }
    await frame();
    await frame();
    checkRunning();
    const result = {workload, round, complete: false, warmupIterations: config.warmup,
      measuredIterations: config.iterations, samples: [], initial: finalValues(targets), final: null};
    report.cases.push(result);
    try {
      for (let index = 0; index < config.warmup + config.iterations; index++) {
        await frame();
        checkRunning();
        const enabled = index % 2 === 0;
        const start = performance.now();
        stage.classList.toggle(`${workload}-b`, enabled);
        const written = performance.now();
        const observedOpacity = getComputedStyle(elements.at(-1)).opacity;
        const flushed = performance.now();
        if (index >= config.warmup) {
          result.samples.push({index: index - config.warmup, enabled,
            mutationMs: written - start, styleReadMs: flushed - written,
            totalMs: flushed - start, observedOpacity});
        }
      }
      result.final = finalValues(targets);
      result.finalClassName = stage.className;
      result.complete = true;
    } finally {
      result.distributionsMs = Object.fromEntries(["mutationMs", "styleReadMs", "totalMs"].map(
        key => [key, summarize(result.samples.map(sample => sample[key]))]));
      stage.replaceChildren();
    }
  }
  document.getElementById("settings").addEventListener("submit", async event => {
    event.preventDefault();
    let config;
    try {
      config = readConfig(values());
    } catch (error) {
      status.textContent = error.message;
      return;
    }
    stopped = false;
    becameHidden = false;
    running = true;
    run.disabled = true;
    stop.disabled = false;
    download.disabled = true;
    for (const field of [...Object.values(fields), ...presets]) {
      field.disabled = true;
    }
    location.hash = new URLSearchParams(config).toString();
    report = {schema: 1, config, started: new Date().toISOString(), complete: false,
      userAgent: navigator.userAgent, platform: navigator.platform,
      hardwareConcurrency: navigator.hardwareConcurrency, devicePixelRatio,
      viewport: {width: innerWidth, height: innerHeight}, cases: [], error: null,
      measurement: "Batch class mutation and one explicit last-target opacity style read; frame waits, setup, warmup and final histograms excluded",
      limitations: "Local directional timing; style read is not proof of one internal flush or all target processing; no absolute threshold or native causality"};
    status.textContent = "Running. Keep this tab visible; Stop ends at the next frame boundary.";
    try {
      if (!CSS.supports("animation-duration", "calc(1em / 16px * 1s)")) {
        throw new Error("Contextual typed duration is unsupported");
      }
      for (let round = 0; round < config.rounds; round++) {
        const first = round % 2 ? (config.order === "outline" ? "font" : "outline") : config.order;
        for (const workload of [first, first === "outline" ? "font" : "outline"]) {
          await oneCase(config, workload, round);
        }
      }
      report.complete = true;
    } catch (error) {
      report.error = String(error);
    } finally {
      stage.replaceChildren();
      running = false;
      report.becameHidden = becameHidden;
      report.allReportedAnimationsHeld = report.cases.length > 0 && report.cases.every(c =>
        c.initial.allAnimationsHeldAt750ms && c.final?.allAnimationsHeldAt750ms);
      report.finished = new Date().toISOString();
      output.value = JSON.stringify(report, null, 2);
      status.textContent = report.complete ? "Complete. Save JSON and compare equal settings and final values." : `Incomplete: ${report.error}`;
      run.disabled = false;
      stop.disabled = true;
      download.disabled = false;
      for (const field of [...Object.values(fields), ...presets]) {
        field.disabled = false;
      }
    }
  });
  download.addEventListener("click", () => {
    if (!report) {
      return;
    }
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], {type: "application/json"}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `duration-cost-${report.config.label.replace(/[^a-z0-9_-]/gi, "_")}.json`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  });
}

if (typeof document !== "undefined") {
  setupPage();
}
