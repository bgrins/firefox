(() => {
  "use strict";

  const run = new URLSearchParams(location.search);
  const report = test => ({
    name: test.name,
    status: test.status,
    message: test.message ?? null,
    stack: test.stack ?? null,
  });

  add_completion_callback(async (tests, status) => {
    const payload = {
      run_id: run.get("run"),
      page: location.pathname,
      tests: tests.map(report),
      status: {
        status: status.status,
        message: status.message ?? null,
        stack: status.stack ?? null,
      },
      ua: navigator.userAgent,
      supports: {
        typed_duration: CSS.supports("animation-duration", "calc(1em / 16px * 1s)"),
        literal_duration: CSS.supports("animation-duration", "2s"),
        variables: CSS.supports("animation-duration", "var(--duration)"),
      },
    };
    const response = await fetch(`/report/${run.get("nonce")}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Observation acknowledgement failed: ${response.status}`);
    }
    const acknowledgement = await response.json();
    if (acknowledgement.next !== null) {
      location.assign(acknowledgement.next);
    }
  });
})();
