(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  const modes = ["defined", "missing", "literal"];
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = modes.map(mode => {
      const record = window.unusedUnitFallbackObservations?.find(row => row.mode === mode) ?? null;
      const name = `Registered unused unit fallback: ${mode}`;
      const test = tests.find(item => item.name === name);
      const collected = record !== null && record.phases.length === 2 && record.phases.every(phase => phase.samples.length === 4);
      complete &&= collected && test != null;
      const referenceChecks = [
        {name: "independent initial registration", passed: record !== null && record.initial === "0px"},
        {name: "parent font calibration", passed: collected && record.phases.every(phase => phase.parentFont === `${phase.phase ? 17 : 11}px`)},
        {name: "primary input calibration", passed: collected && record.phases.every(phase => phase.size === (mode === "missing" ? "" : `${phase.phase ? 30 : 20}px`))},
      ];
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null}, referenceChecks,
        activeExpectation: {kind: mode === "literal" ? "control" : mode === "missing" ? "genuine-cycle" : "unused-unit-fallback",
          matches: collected && record.phases.every(phase => phase.samples.every(value => value === phase.expectedCustom) && phase.font === phase.expectedFont)}, policyVerdict: null};
    });
    const report = {schema: "registered-unused-unit-fallback-observation-v1", status: complete ? "complete" : "incomplete",
      userAgent: navigator.userAgent, policyVerdict: null, observations,
      harness: {status: harness.status, message: harness.message ?? null}};
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({run_id: query.get("run"), report}),
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  });
})();
