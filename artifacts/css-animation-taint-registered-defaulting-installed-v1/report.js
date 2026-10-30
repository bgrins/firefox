(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
function referenceChecks(record) {
  const checks = [];
  const add = (name, passed) => checks.push({name, passed: Boolean(passed)});
  add("complete capture", record?.phases?.length === 2 && record?.calibration != null && record?.before != null);
  add("registration initial/inheritance", record?.calibration?.initial === "horizontal-tb");
  add("registration syntax", record?.calibration?.multiIdent === "horizontal-tb");
  add("ordinary underlying source", record?.before?.variable === "vertical-rl");
  for (const phase of record?.phases ?? []) {
    add(`${phase.label}: fixed independent driver`, phase.cssDuration === "2s" &&
      phase.duration === 2000 && phase.currentTime === 750 && phase.playState === "paused" &&
      Math.abs(phase.progress - .375) <= .00001 && phase.opacity === "1" &&
      phase.sameAnimation && phase.sameEffect);
    if (record.mode !== "invalid") {
      add(`${phase.label}: valid animated source`, phase.variable === "vertical-rl");
    }
    if (record.mode === "literal") {
      add(`${phase.label}: literal sink`, phase.readings.length === 4 &&
        phase.readings.every(value => value === "vertical-lr"));
    }
  }
  return checks;
}
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = ["invalid", "valid", "literal"].map(mode => {
      const record = window.registeredDefaultingObservations?.[mode] ?? null;
      const name = `Registered keyframe defaulting observation: ${mode}`;
      const test = tests.find(item => item.name === name);
      const phases = record?.phases ?? [];
      const captured = phases.length === 2 && record?.calibration != null && record?.registration != null && record?.before != null;
      complete &&= captured && test != null;
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null},
        referenceChecks: referenceChecks(record), activeExpectation: {expectedSink: "vertical-lr",
          kind: mode === "literal" ? "control" : "registered-defaulting-observation",
          matches: captured && phases.every(phase => phase.readings.every(value => value === "vertical-lr"))}, policyVerdict: null};
    });
    const report = {schema: "registered-defaulting-observation-v1", status: complete ? "complete" : "incomplete",
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
