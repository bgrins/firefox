"use strict";
(async () => {
  const config = await (await fetch("/CONFIG.json")).json();
  const label = new URL(location.href).searchParams.get("label");
  const rows = [];
  const configs = [];
  for (const kind of config.kinds) {
    for (const state of config.states) {
      for (const count of config.sizes) configs.push({kind, state, count});
    }
  }
  const active = new Set();
  const rect = element => {
    const r = element.getBoundingClientRect();
    return [r.x, r.y, r.width, r.height];
  };
  const expected = (kind, index, width) => [kind === "oof" ? (width - 8) / 2 : index * 8, 0, 8, 8];
  function construct(c) {
    const host = document.createElement("div");
    active.add(host);
    host.className = "host";
    const subject = document.createElement("div");
    subject.className = `subject ${c.kind}`;
    const leaves = [];
    for (let i = 0; i < c.count; ++i) {
      const branch = document.createElement("div");
      branch.className = "branch";
      let parent = branch;
      for (let depth = 0; depth < config.depth; ++depth) {
        const level = document.createElement("div");
        level.className = "level";
        parent.append(level);
        parent = level;
      }
      leaves.push(parent);
      subject.append(branch);
    }
    host.append(subject);
    document.body.append(host);
    return {host, subject, leaves};
  }
  function remove(fixture) {
    fixture.host.remove();
    active.delete(fixture.host);
  }
  let start;
  try {
    if (!CSS.supports("content-visibility", "hidden")) throw new Error("unsupported content visibility");
    await new Promise(resolve => setTimeout(resolve, config.startup_ms));
    start = performance.now();
    for (let round = -config.warmup_rounds; round < config.measured_rounds; ++round) {
      for (let slot = 0; slot < configs.length; ++slot) {
        if (performance.now() - start > config.fixture_deadline_ms) throw new Error("fixture deadline");
        const ordinal = (slot + round + config.warmup_rounds) % configs.length;
        const c = configs[ordinal];
        const n = Math.min(c.count, config.query_limit);
        const indices = Array.from({length: n}, (_, i) => n === 1 ? 0 : Math.floor(i * (c.count - 1) / (n - 1)));
        const constructStart = performance.now();
        const target = construct(c);
        const peer = construct(c);
        const constructionMs = performance.now() - constructStart;
        const establishStart = performance.now();
        const calibration = [];
        for (const width of [160, 168]) {
          peer.subject.classList.toggle("wide", width === 168);
          if (JSON.stringify(rect(peer.subject)) !== JSON.stringify([0, 0, width, 64])) throw new Error("visible outer calibration");
          for (const index of indices) {
            const value = rect(peer.leaves[index]);
            calibration.push({width, index, rect: value});
            if (JSON.stringify(value) !== JSON.stringify(expected(c.kind, index, width))) throw new Error("visible full-rectangle calibration");
          }
        }
        const initial = indices.map(index => rect(target.leaves[index]));
        if (initial.some((value, i) => JSON.stringify(value) !== JSON.stringify(expected(c.kind, indices[i], 160)))) throw new Error("target initial calibration");
        remove(peer);
        if (c.state === "hidden") target.subject.classList.add("hidden");
        target.subject.getBoundingClientRect();
        const establishMs = performance.now() - establishStart;
        let outerChecksum = 0;
        const mutationStart = performance.now();
        for (let iteration = 0; iteration < config.iterations; ++iteration) {
          target.subject.classList.toggle("wide", iteration % 2 === 0);
          const r = target.subject.getBoundingClientRect();
          outerChecksum += r.width + r.height;
        }
        const mutationFlushMs = performance.now() - mutationStart;
        const times = {prepare: [], first: [], repeat: [], distinct: [], secondPass: [], noMutation: []};
        const observations = [];
        function measure(bucket, iteration, selected, width) {
          const begin = performance.now();
          const values = selected.map(index => rect(target.leaves[index]));
          times[bucket].push(performance.now() - begin);
          for (let i = 0; i < selected.length; ++i) observations.push({bucket, iteration, index: selected[i], width, rect: values[i]});
        }
        for (let iteration = 0; iteration < config.iterations; ++iteration) {
          const width = iteration % 2 === 0 ? 168 : 160;
          const begin = performance.now();
          target.subject.classList.toggle("wide", width === 168);
          target.subject.getBoundingClientRect();
          times.prepare.push(performance.now() - begin);
          measure("first", iteration, [indices[0]], width);
          measure("repeat", iteration, [indices[0]], width);
          measure("distinct", iteration, indices.slice(1), width);
          measure("secondPass", iteration, indices, width);
        }
        const finalWidth = (config.iterations - 1) % 2 === 0 ? 168 : 160;
        for (let iteration = 0; iteration < config.no_mutation_iterations; ++iteration) measure("noMutation", iteration, indices, finalWidth);
        if (round >= 0) rows.push({round, slot, ordinal, ...c, indices, constructionMs, establishMs, mutationFlushMs, outerChecksum, calibration, initial, times, observations});
        remove(target);
      }
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: true, label, config, elapsedMs: performance.now() - start, rows})});
  } catch (error) {
    for (const host of active) host.remove();
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: false, label, config, elapsedMs: start === undefined ? null : performance.now() - start, error: String(error), rows})});
  }
})();
