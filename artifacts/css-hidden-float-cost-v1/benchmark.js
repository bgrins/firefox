"use strict";
(async () => {
  let sequence = 0;
  async function progress(stage, detail = {}) {
    const response = await fetch("/progress", {method: "POST", body: JSON.stringify({sequence: sequence++, stage, ...detail})});
    if (!response.ok) throw new Error("progress rejected");
  }
  await progress("script-start");
  const config = await (await fetch("/CONFIG.json")).json();
  const label = new URL(location.href).searchParams.get("label");
  await progress("config-ready", {label});
  const configs = [];
  for (const kind of config.kinds) for (const state of config.states) for (const count of config.sizes) configs.push({kind, state, count});
  const active = new Set();
  const rows = [];
  const expected = (index, width) => [10 + (index % 2) * width / 2, 10 + Math.floor(index / 2) * 16, width / 2, 8];
  const rect = target => { const r = target.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
  const same = (a, b) => a.length === b.length && a.every((value, i) => value === b[i]);
  function construct(c) {
    const host = document.createElement("div");
    host.className = "host";
    host.innerHTML = '<div class="outer"><div class="subject"></div></div>';
    const outer = host.firstElementChild;
    const subject = outer.firstElementChild;
    const owner = c.kind === "direct" ? subject : document.createElement("span");
    if (c.kind === "inline-nested") {
      const wrapper = document.createElement("span");
      wrapper.append(owner);
      subject.append(wrapper);
    }
    const targets = [];
    for (let i = 0; i < c.count; ++i) {
      const root = document.createElement("div");
      root.className = "float-root";
      const leaf = document.createElement("div");
      leaf.className = "float-leaf";
      root.append(leaf);
      owner.append(root);
      targets.push(leaf);
    }
    active.add(host);
    document.body.append(host);
    return {host, outer, subject, targets};
  }
  function remove(f) { f.host.remove(); active.delete(f.host); }
  function calibrate(f, width) {
    if (!same(rect(f.outer), [10, 10, width, 64])) throw new Error("outer calibration");
    const values = f.targets.map(rect);
    if (values.some((r, i) => !same(r, expected(i, width)))) throw new Error("full geometry calibration");
    return values;
  }
  function hot(f, bucket, count) {
    const expectedRects = f.targets.map((_, i) => expected(i, 160));
    let checksum = 0, mismatches = 0, firstMismatch = null;
    const start = performance.now();
    for (let i = 0; i < config.hot_reads; ++i) {
      const index = bucket === "hotSame" ? count - 1 : i % count;
      const r = f.targets[index].getBoundingClientRect();
      const e = expectedRects[index];
      checksum += r.x + r.y + r.width + r.height;
      if (r.x !== e[0] || r.y !== e[1] || r.width !== e[2] || r.height !== e[3]) {
        ++mismatches;
        if (firstMismatch === null) firstMismatch = {iteration: i, index, rect: [r.x, r.y, r.width, r.height]};
      }
    }
    return {bucket, reads: config.hot_reads, elapsedMs: performance.now() - start, checksum, mismatches, firstMismatch};
  }
  let start;
  try {
    if (!CSS.supports("content-visibility", "hidden")) throw new Error("unsupported content visibility");
    await new Promise(resolve => setTimeout(resolve, config.startup_ms));
    await progress("fixture-start");
    start = performance.now();
    for (let round = -config.warmup_rounds; round < config.measured_rounds; ++round) {
      for (let slot = 0; slot < configs.length; ++slot) {
        if (performance.now() - start > config.fixture_deadline_ms) throw new Error("fixture deadline");
        const ordinal = (slot + round + config.warmup_rounds) % configs.length;
        const c = configs[ordinal];
        await progress("batch-begin", {round, slot, ordinal, ...c});
        const f = construct(c);
        const calibration = [];
        for (const width of [160, 168, 160]) {
          f.outer.classList.toggle("wide", width === 168);
          calibration.push({width, rects: calibrate(f, width)});
        }
        if (c.state === "hidden") f.subject.classList.add("hidden");
        const hiddenOuter = rect(f.outer);
        if (!same(hiddenOuter, [10, 10, 160, 64])) throw new Error("hidden outer calibration");
        const times = {prepare: [], first: [], repeat: []};
        const observations = [], outers = [];
        for (let iteration = 0; iteration < config.iterations; ++iteration) {
          const width = iteration % 2 === 0 ? 168 : 160;
          const begin = performance.now();
          f.outer.classList.toggle("wide", width === 168);
          const outer = rect(f.outer);
          times.prepare.push(performance.now() - begin);
          outers.push(outer);
          if (!same(outer, [10, 10, width, 64])) throw new Error("outer-only flush calibration");
          for (const bucket of ["first", "repeat"]) {
            const begin = performance.now();
            const value = rect(f.targets[c.count - 1]);
            times[bucket].push(performance.now() - begin);
            observations.push({bucket, iteration, index: c.count - 1, width, rect: value});
          }
        }
        f.subject.classList.remove("hidden");
        f.outer.classList.remove("wide");
        const restored = calibrate(f, 160);
        remove(f);
        const clean = construct(c);
        const cleanVisible = calibrate(clean, 160);
        if (c.state === "hidden") clean.subject.classList.add("hidden");
        const cleanReady = calibrate(clean, 160);
        const hotRows = [hot(clean, "hotSame", c.count), hot(clean, "hotCycle", c.count)];
        const cleanAfter = calibrate(clean, 160);
        remove(clean);
        if (round >= 0) rows.push({round, slot, ordinal, ...c, calibration, hiddenOuter, outers, times, observations, restored, cleanVisible, cleanReady, cleanAfter, hotRows});
        await progress("batch-end", {round, slot, ordinal, ...c});
      }
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    await progress("result-ready", {rows: rows.length});
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: true, label, config, elapsedMs: performance.now() - start, rows})});
  } catch (error) {
    for (const host of active) host.remove();
    await progress("fixture-error", {error: String(error)});
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: false, label, config, elapsedMs: start === undefined ? null : performance.now() - start, error: String(error), rows})});
  }
})();
