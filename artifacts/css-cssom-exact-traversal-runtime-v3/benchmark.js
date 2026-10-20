"use strict";

async function runRectangleBenchmark() {
  const params = new URLSearchParams(location.hash.slice(1));
  const integer = (name, fallback, min, max) => {
    const value = params.has(name) ? Number(params.get(name)) : fallback;
    if (!Number.isInteger(value) || value < min || value > max) {
      throw new Error(`Invalid ${name}`);
    }
    return value;
  };
  const config = {
    iterations: integer("iterations", 20000, 1000, 100000),
    samples: integer("samples", 7, 3, 15),
    warmup: integer("warmup", 3000, 1000, 20000),
    startupMs: integer("startupMs", 3000, 0, 30000),
    depths: [8, 128],
  };
  const cases = [];
  for (const depth of config.depths) {
    for (const mode of ["ordinary", "transform-near-leaf", "transform-near-root"]) {
      const fixture = document.createElement("div");
      fixture.className = "fixture";
      let parent = fixture;
      for (let index = 0; index < depth; index++) {
        const link = document.createElement("div");
        const transformed = (mode === "transform-near-root" && index === 0) ||
          (mode === "transform-near-leaf" && index === depth - 1);
        link.className = transformed ? "link transformed" : "link";
        parent.append(link);
        parent = link;
      }
      const subject = document.createElement("div");
      subject.className = "subject";
      parent.append(subject);
      document.body.append(fixture);
      const transformed = mode !== "ordinary";
      cases.push({
        name: `${mode}-${depth}`, depth, mode, subject,
        expected: {x: depth + (transformed ? 3 : 0),
          y: depth + (transformed ? 5 : 0), width: 20, height: 10},
        batches: [],
      });
    }
  }
  const rect = element => {
    const value = element.getBoundingClientRect();
    return {x: value.x, y: value.y, width: value.width, height: value.height};
  };
  const same = (a, b) => Object.keys(b).every(key => a[key] === b[key]);
  const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
  await pause(config.startupMs);
  await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 0)));
  for (const entry of cases) {
    entry.before = rect(entry.subject);
    if (!same(entry.before, entry.expected)) {
      throw new Error(`Calibration failed: ${entry.name}: ${JSON.stringify(entry.before)}`);
    }
  }
  function readBatch(element, iterations) {
    let checksum = 0;
    for (let index = 0; index < iterations; index++) {
      const value = element.getBoundingClientRect();
      checksum += value.x + value.y + value.width + value.height;
    }
    return checksum;
  }
  const visibility = [document.visibilityState];
  for (const entry of cases) {
    entry.warmupChecksum = readBatch(entry.subject, config.warmup);
  }
  const order = [];
  for (let sample = 0; sample < config.samples; sample++) {
    for (let slot = 0; slot < cases.length; slot++) {
      const entry = cases[(slot + sample) % cases.length];
      await pause(10);
      visibility.push(document.visibilityState);
      const start = performance.now();
      const checksum = readBatch(entry.subject, config.iterations);
      const elapsedMs = performance.now() - start;
      const expectedChecksum = Object.values(entry.expected).reduce((a, b) => a + b, 0) * config.iterations;
      entry.batches.push({sample, slot, calls: config.iterations, elapsedMs,
        nanosecondsPerCall: elapsedMs * 1e6 / config.iterations,
        checksum, expectedChecksum, checksumMatches: checksum === expectedChecksum});
      order.push(entry.name);
    }
  }
  for (const entry of cases) {
    entry.after = rect(entry.subject);
    entry.stable = same(entry.before, entry.after);
    entry.medianNanosecondsPerCall = entry.batches.map(batch => batch.nanosecondsPerCall)
      .sort((a, b) => a - b)[Math.floor(config.samples / 2)];
    delete entry.subject;
  }
  visibility.push(document.visibilityState);
  return {schema: 1, config, userAgent: navigator.userAgent,
    devicePixelRatio, viewport: {width: innerWidth, height: innerHeight},
    timeOrigin: performance.timeOrigin, visibility, order, cases,
    valid: visibility.every(value => value === "visible") &&
      cases.every(entry => entry.stable && entry.batches.every(batch => batch.checksumMatches && batch.elapsedMs > 0)),
    totalMeasuredCalls: cases.length * config.samples * config.iterations};
}

window.rectangleBenchmarkPromise = runRectangleBenchmark().then(result => {
  window.rectangleBenchmarkResults = result;
  document.getElementById("result").textContent = JSON.stringify(result, null, 2);
  return result;
}, error => {
  const result = {schema: 1, valid: false, error: String(error), stack: error.stack};
  window.rectangleBenchmarkResults = result;
  document.getElementById("result").textContent = JSON.stringify(result, null, 2);
  return result;
});
