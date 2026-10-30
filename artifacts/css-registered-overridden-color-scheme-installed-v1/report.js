(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  const modes = ["color-no-loser", "color-literal", "color-normal-before-important", "color-normal-after-important", "color-normal-before-normal", "color-important-before-important", "length-no-loser", "length-literal", "length-normal-before-important"];
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = modes.map(mode => {
      const record = window.overriddenSchemeObservations?.find(row => row.caseName === mode) ?? null;
      const name = `Overridden registered dependency: ${mode}`;
      const test = tests.find(item => item.name === name);
      const collected = record !== null && record.phases.length === 2 && record.phases.every(phase => phase.samples.length === 4);
      complete &&= collected && test != null;
      const referenceChecks = [
        {name: "independent initial registration", passed: record !== null && record.initial === (mode.startsWith("length-") ? "0px" : "rgb(255, 0, 0)")},
        {name: "losing declaration grammar", passed: collected && record.phases.every(phase => phase.supportedLosingValue)},
        {name: "literal cascade winner", passed: collected && record.phases.every(phase => phase.computedWinner === phase.winner)},
        {name: "literal reference", passed: collected && record.phases.every(phase => phase.reference === phase.expected)},
      ];
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null}, referenceChecks,
        activeExpectation: {kind: mode.endsWith("-literal") || mode.endsWith("-no-loser") ? "control" : "overridden-dependency",
          matches: collected && record.phases.every(phase => phase.samples.every(value => value === phase.reference))}, policyVerdict: null};
    });
    const report = {schema: "registered-overridden-dependency-observation-v1", status: complete ? "complete" : "incomplete",
      userAgent: navigator.userAgent, policyVerdict: null, observations,
      harness: {status: harness.status, message: harness.message ?? null}};
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({run_id: query.get("run"), report}),
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  });
})();
