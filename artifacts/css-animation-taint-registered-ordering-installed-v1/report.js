(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
function configuration(mode) {
  if (mode === "literal") return {flush: true, equal: false, opacity: true, literal: true};
  const match = /^flush([01])-equal([01])-opacity([01])$/.exec(mode);
  return {flush: match[1] === "1", equal: match[2] === "1", opacity: match[3] === "1", literal: false};
}

function referenceChecks(record) {
  const checks = [];
  const add = (name, passed) => checks.push({name, passed: Boolean(passed)});
  const config = record ? configuration(record.mode) : null;
  add("complete capture", record?.phases?.length === 2 && record?.calibration != null &&
    record?.registration != null && (!config.flush || record.before != null));
  add("registration initial/inheritance", record?.calibration?.initial === "horizontal-tb");
  add("registration syntax", record?.calibration?.multiIdent === "horizontal-tb");
  if (config?.flush) {
    add("ordinary underlying source", record?.before?.variable === (config.equal ? "vertical-rl" : "vertical-lr"));
  }
  for (const phase of record?.phases ?? []) {
    add(`${phase.label}: fixed driver and identity`, phase.cssDuration === "2s" &&
      phase.duration === 2000 && phase.currentTime === 750 && phase.playState === "paused" &&
      Math.abs(phase.progress - .375) <= .00001 && phase.sameAnimation && phase.sameEffect);
    add(`${phase.label}: active custom source`, phase.variable === "vertical-rl");
    add(`${phase.label}: opacity driver selection`, phase.opacity === (config.opacity ? "1" : "0.25"));
    if (config.literal) {
      add(`${phase.label}: literal sink`, phase.readings.length === 4 &&
        phase.readings.every(value => value === "vertical-lr"));
    }
  }
  return checks;
}
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = ["flush0-equal0-opacity0", "flush0-equal0-opacity1", "flush0-equal1-opacity0", "flush0-equal1-opacity1", "flush1-equal0-opacity0", "flush1-equal0-opacity1", "flush1-equal1-opacity0", "flush1-equal1-opacity1", "literal"].map(mode => {
      const record = window.registeredOrderingObservations?.[mode] ?? null;
      const name = `Registered keyframe ordering observation: ${mode}`;
      const test = tests.find(item => item.name === name);
      const phases = record?.phases ?? [];
      const captured = phases.length === 2 && record?.calibration != null && record?.registration != null && (!configuration(mode).flush || record?.before != null);
      complete &&= captured && test != null;
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null},
        referenceChecks: referenceChecks(record), activeExpectation: {expectedSink: "vertical-lr",
          kind: mode === "literal" ? "control" : "registered-ordering-observation",
          matches: captured && phases.every(phase => phase.readings.every(value => value === "vertical-lr"))}, policyVerdict: null};
    });
    const report = {schema: "registered-ordering-observation-v1", status: complete ? "complete" : "incomplete",
      userAgent: navigator.userAgent, policyVerdict: null, observations,
      harness: {status: harness.status, message: harness.message ?? null}};
    const body = JSON.stringify({run_id: query.get("run"), report}, (_key, value) =>
      typeof value === "number" && !Number.isFinite(value) ? {nonfinite: String(value)} : value);
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body,
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  });
})();
