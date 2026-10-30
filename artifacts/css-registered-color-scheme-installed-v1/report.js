(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  const modes = ["union-plain", "union-unused-attr", "color-first-unused-attr", "ident-unused-attr", "literal"];
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = modes.map(mode => {
      const record = window.colorSchemeDependencyObservations?.find(row => row.mode === mode) ?? null;
      const name = `Selected identifier color-scheme dependency: ${mode}`;
      const test = tests.find(item => item.name === name);
      const snapshots = record?.snapshots ?? [];
      const captured = snapshots.length === 2 && typeof record?.registeredInitial === "string";
      complete &&= captured && test != null;
      const matches = captured && snapshots.every(row => row.firstScheme === row.expected && row.custom === row.expected);
      const checks = [{name: "registration rejects multiple identifiers", passed: record?.registeredInitial === "normal"}];
      if (mode === "literal") checks.push({name: "literal and selected custom identifiers", passed: matches});
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null},
        referenceChecks: checks, activeExpectation: {expectedSink: ["light", "dark"],
          kind: mode === "literal" ? "control" : "selected-identifier-observation", matches}, policyVerdict: null};
    });
    const report = {schema: "color-scheme-dependency-observation-v1", status: complete ? "complete" : "incomplete",
      userAgent: navigator.userAgent, policyVerdict: null, observations,
      harness: {status: harness.status, message: harness.message ?? null}};
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({run_id: query.get("run"), report}),
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  });
})();
