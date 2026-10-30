(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = ["unregistered", "universal", "typed", "literal"].map(mode => {
      const record = window.registeredTaintObservations?.[mode] ?? null;
      const name = `Animation taint registered scope: ${mode}`;
      const test = tests.find(item => item.name === name);
      const registered = ["universal", "typed"].includes(mode);
      const phases = record?.phases ?? [];
      const captured = phases.length === 2 && record?.calibration != null && (!registered || record?.registration != null);
      complete &&= captured && test != null;
      const referenceChecks = [
        {name: "complete capture", passed: captured},
        {name: "initial and inheritance", passed: record?.calibration?.initial === (registered ? "horizontal-tb" : "vertical-lr")},
        {name: "syntax calibration", passed: record?.calibration?.multiIdent === (mode === "typed" ? "horizontal-tb" : "one two")},
      ];
      for (const phase of phases) {
        referenceChecks.push({name: `${phase.label}: active source and fixed lifecycle`, passed:
          phase.variable === "vertical-rl" && phase.cssDuration === "2s" && phase.duration === 2000 &&
          phase.currentTime === 750 && phase.playState === "paused" &&
          Math.abs(phase.progress - 0.375) <= 0.00001 && phase.sameAnimation && phase.sameEffect});
      }
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null},
        referenceChecks, activeExpectation: {expectedSink: "vertical-lr",
          kind: mode === "literal" ? "control" : "registered-scope-hypothesis",
          matches: captured && phases.every(phase => phase.readings.every(value => value === "vertical-lr"))}, policyVerdict: null};
    });
    const report = {schema: "registered-taint-observation-v1", status: complete ? "complete" : "incomplete",
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
