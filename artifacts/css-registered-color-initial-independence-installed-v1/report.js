(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  const modes = ["red", "CanvasText", "light-dark(red, blue)"];
  add_completion_callback(async (tests, harness) => {
    let complete = true;
    const observations = modes.map(mode => {
      const record = window.registrationObservations?.find(row => row.initialValue === mode) ?? null;
      const name = `Registered color initial independence: ${mode}`;
      const test = tests.find(item => item.name === name);
      complete &&= record !== null && test != null;
      const expectedAcceptance = mode === "red";
      const expectedException = expectedAcceptance ? null : "SyntaxError";
      const matches = record !== null && record.accepted === expectedAcceptance &&
        (expectedAcceptance ? record.exception === null : record.exception?.name === expectedException);
      return {mode, record, wpt: {name, status: test?.status ?? null, message: test?.message ?? null},
        referenceChecks: [
          {name: "ordinary color syntax supported", passed: record?.syntaxSupported === true},
          {name: "independent red registration", passed: record !== null && record.controlInitial === record.literalRed},
        ],
        activeExpectation: {expectedAcceptance, expectedException, kind: expectedAcceptance ? "control" : "tentative-registration-rejection", matches},
        policyVerdict: null};
    });
    const report = {schema: "registered-initial-independence-observation-v1", status: complete ? "complete" : "incomplete",
      userAgent: navigator.userAgent, policyVerdict: null, observations,
      harness: {status: harness.status, message: harness.message ?? null}};
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({run_id: query.get("run"), report}),
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  });
})();
