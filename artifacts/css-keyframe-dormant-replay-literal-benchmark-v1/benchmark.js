"use strict";

(() => {
  const CONFIG = Object.freeze({
    counts: [100, 1000],
    selectorRules: [0, 200],
    properties: ["opacity", "transform"],
    modes: ["animate", "first-play", "replay", "registered-seek"],
    warmupBatches: 2,
    measuredBatches: 7,
    startupMs: 3000,
    yieldMs: 10,
    duration: 1000000,
  });
  let started = false;
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  function require(condition, message) {
    if (!condition) {
      throw new Error(message);
    }
  }
  function value(element, property) {
    const style = getComputedStyle(element);
    return property === "opacity" ? Number(style.opacity) : style.transform;
  }
  function matches(actual, property, animated) {
    return property === "opacity"
      ? actual === (animated ? 0.5 : 0.25)
      : actual === (animated ? "matrix(1, 0, 0, 1, 10, 0)" : "none");
  }
  function frames(property) {
    const v = property === "opacity" ? "0.5" : "translateX(10px)";
    return [{ [property]: v }, { [property]: v }];
  }
  function flush(targets, property, output) {
    for (let i = 0; i < targets.length; ++i) {
      output[i] = value(targets[i], property);
    }
  }
  function checkValues(values, property, animated, label) {
    require(values.every(v => matches(v, property, animated)), label);
  }
  async function batch(spec, round, warmup, result) {
    const scope = document.createElement("section");
    scope.className = "dormant-literal-scope";
    const style = document.createElement("style");
    const group = document.createElement("div");
    group.className = "group";
    const targets = [];
    const animations = [];
    const observed = new Array(spec.count);
    let cleanupError = null;
    let failure = null;
    let row = null;
    style.textContent = `
      .dormant-literal-scope { position: absolute; inset: 50px auto auto 0; }
      .dormant-literal-scope .target { display: inline-block; width: 1px;
        height: 1px; opacity: .25; transform: none; outline-offset: 0px; }
    ` + Array.from({ length: spec.rules }, (_, i) =>
      `.dormant-literal-scope .group > .target.t${i % 16}[data-kind="literal"] { outline-offset: ${i % 4}px; }`
    ).join("\n");
    for (let i = 0; i < spec.count; ++i) {
      const target = document.createElement("div");
      target.className = `target t${i % 16}`;
      target.dataset.kind = "literal";
      group.append(target);
      targets.push(target);
    }
    scope.append(style, group);
    document.body.append(scope);
    try {
      flush(targets, spec.property, observed);
      checkValues(observed, spec.property, false, "initial underlying literal");
      targets.forEach((target, i) => {
        require(target.getAnimations().length === 0, "initial empty effect set");
        require(getComputedStyle(target).outlineOffset === `${spec.rules ? i % 4 : 0}px`, "selector load applied");
      });
      if (spec.mode !== "animate") {
        for (const target of targets) {
          const effect = new KeyframeEffect(target, frames(spec.property), {
            duration: CONFIG.duration, fill: "none",
          });
          const animation = new Animation(effect, document.timeline);
          animation.playbackRate = 0;
          animations.push(animation);
        }
        require(animations.every(a => a.playState === "idle"), "initial idle effects");
        if (spec.mode === "replay" || spec.mode === "registered-seek") {
          animations.forEach(a => a.play());
          await Promise.all(animations.map(a => a.ready));
          flush(targets, spec.property, observed);
          checkValues(observed, spec.property, true, "pre-existing literal animation");
          if (spec.mode === "replay") {
            animations.forEach(a => a.cancel());
            flush(targets, spec.property, observed);
            checkValues(observed, spec.property, false, "cancelled underlying literal");
            require(targets.every(t => t.getAnimations().length === 0), "cancelled effect sets drained");
            require(animations.every(a => a.playState === "idle"), "cancelled idle state");
          }
        }
      }
      require(document.visibilityState === "visible", "visible before timing");
      const begin = performance.now();
      if (spec.mode === "animate") {
        for (const target of targets) {
          animations.push(target.animate(frames(spec.property), {
            duration: CONFIG.duration, fill: "none",
          }));
        }
      } else if (spec.mode === "registered-seek") {
        animations.forEach(a => { a.currentTime = 500000; });
      } else {
        animations.forEach(a => a.play());
      }
      const afterAPI = performance.now();
      flush(targets, spec.property, observed);
      const afterFlush = performance.now();
      row = {
        ...spec, round, warmup,
        apiMs: afterAPI - begin,
        flushMs: afterFlush - afterAPI,
        totalMs: afterFlush - begin,
      };
      result.rows.push(row);
      require([row.apiMs, row.flushMs, row.totalMs].every(x => Number.isFinite(x) && x >= 0), "finite timing");
      checkValues(observed, spec.property, true, "timed literal result");
      require(document.visibilityState === "visible", "visible after timing");
      for (let i = 0; i < targets.length; ++i) {
        require(animations[i].effect.target === targets[i], "retained target identity");
        const active = targets[i].getAnimations();
        require(active.length === 1 && active[0] === animations[i], "retained active animation identity");
      }
      row.correctness = "PASS";
    } catch (error) {
      failure = String(error.stack || error);
      if (row) {
        row.correctness = "FAIL";
        row.error = failure;
      }
    } finally {
      try {
        animations.forEach(a => a.cancel());
        flush(targets, spec.property, observed);
        checkValues(observed, spec.property, false, "cleanup underlying literal");
        require(targets.every(t => t.getAnimations().length === 0), "cleanup no active effects");
      } catch (error) {
        cleanupError = String(error.stack || error);
      } finally {
        scope.remove();
      }
      result.cleanup.push({ case: spec.id, round, warmup,
        removed: !scope.isConnected, error: cleanupError });
    }
    require(!failure, failure);
    require(!cleanupError, cleanupError);
  }
  window.runDormantLiteralBenchmark = (token, label) => {
    require(token === "DORMANT_LITERAL_TIMING_V1", "explicit activation token");
    require(["before", "candidate", "restored"].includes(label), "explicit build label");
    require(!started, "one invocation per document");
    started = true;
    const result = { schema: 1, label, config: CONFIG, rows: [], cleanup: [],
      userAgent: navigator.userAgent, valid: false, error: null };
    window.dormantLiteralBenchmarkResults = result;
    window.dormantLiteralBenchmarkPromise = (async () => {
      try {
        require(document.visibilityState === "visible", "visible document");
        await wait(CONFIG.startupMs);
        const cases = [];
        for (const count of CONFIG.counts) {
          for (const rules of CONFIG.selectorRules) {
            for (const property of CONFIG.properties) {
              for (const mode of CONFIG.modes) {
                cases.push({ id: `${mode}/${property}/${count}/${rules}`, mode, property, count, rules });
              }
            }
          }
        }
        result.caseOrder = cases.map(c => c.id);
        for (let round = 0; round < CONFIG.warmupBatches + CONFIG.measuredBatches; ++round) {
          for (let j = 0; j < cases.length; ++j) {
            await batch(cases[(j + round) % cases.length], round,
              round < CONFIG.warmupBatches, result);
            await wait(CONFIG.yieldMs);
          }
        }
        require(result.rows.length === 288 && result.cleanup.length === 288, "complete batches");
        result.valid = true;
      } catch (error) {
        result.error = String(error.stack || error);
      }
      return result;
    })();
    return window.dormantLiteralBenchmarkPromise;
  };
})();
