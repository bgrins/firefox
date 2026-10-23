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
  let activeHost;
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
        const queryCount = Math.min(c.count, config.query_limit);
        const indices = Array.from({length: queryCount}, (_, i) => queryCount === 1 ? 0 : Math.floor(i * (c.count - 1) / (queryCount - 1)));
        const constructStart = performance.now();
        const host = document.createElement("div");
        activeHost = host;
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
        const constructionMs = performance.now() - constructStart;
        const establishStart = performance.now();
        const outer = subject.getBoundingClientRect();
        if (outer.width !== 160 || outer.height !== 64) throw new Error("outer calibration");
        for (const index of indices) {
          const r = leaves[index].getBoundingClientRect();
          if (r.width !== 8 || r.height !== 8) throw new Error("visible leaf calibration");
        }
        if (c.state === "hidden") subject.classList.add("hidden");
        subject.getBoundingClientRect();
        const establishMs = performance.now() - establishStart;
        let outerChecksum = 0;
        const mutationStart = performance.now();
        for (let iteration = 0; iteration < config.iterations; ++iteration) {
          subject.classList.toggle("wide", iteration % 2 === 0);
          const r = subject.getBoundingClientRect();
          outerChecksum += r.width + r.height;
        }
        const mutationFlushMs = performance.now() - mutationStart;
        let recoveryPrepareMs = 0;
        let recoveryQueryMs = 0;
        let geometryChecksum = 0;
        let queryChecksum = 0;
        let mismatches = 0;
        const observedSizes = [];
        for (let iteration = 0; iteration < config.iterations; ++iteration) {
          const preparationStart = performance.now();
          subject.classList.toggle("wide", iteration % 2 === 0);
          subject.getBoundingClientRect();
          recoveryPrepareMs += performance.now() - preparationStart;
          const queryStart = performance.now();
          const values = indices.map(index => leaves[index].getBoundingClientRect());
          recoveryQueryMs += performance.now() - queryStart;
          for (let i = 0; i < values.length; ++i) {
            const r = values[i];
            geometryChecksum += r.width * 17 + r.height * 31;
            queryChecksum += (ordinal + 1) * (iteration + 1) * (indices[i] + 1);
            if (r.width !== 8 || r.height !== 8) ++mismatches;
            observedSizes.push([r.width, r.height]);
          }
        }
        if (round >= 0) rows.push({round, slot, ordinal, ...c, indices, constructionMs, establishMs, mutationFlushMs, recoveryPrepareMs, recoveryQueryMs, outerChecksum, queryChecksum, geometryChecksum, mismatches, observedSizes});
        host.remove();
        activeHost = null;
      }
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: true, label, config, elapsedMs: performance.now() - start, rows})});
  } catch (error) {
    if (activeHost) activeHost.remove();
    await fetch("/result", {method: "POST", body: JSON.stringify({complete: false, label, config, elapsedMs: start === undefined ? null : performance.now() - start, error: String(error), rows})});
  }
})();
