(() => {
  "use strict";
  const query = new URLSearchParams(location.search);
  const timer = setInterval(async () => {
    const report = window.waapiTaintObservations;
    if (!report || !["complete", "incomplete"].includes(report.status)) return;
    clearInterval(timer);
    const body = JSON.stringify({run_id: query.get("run"), report}, (_key, value) =>
      typeof value === "number" && !Number.isFinite(value) ? {nonfinite: String(value)} : value);
    const response = await fetch(`/report/${query.get("nonce")}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body,
    });
    if (!response.ok) throw new Error(`Report rejected: ${response.status}`);
  }, 50);
})();
