"use strict";

const probeInput = JSON.parse(document.getElementById("probe-input").textContent);
const PROPERTY = "text-transform";
let latestResult = null;

function support(value) {
  try {
    return { value: CSS.supports(PROPERTY, value), error: null };
  } catch (error) {
    return { value: null, error: String(error) };
  }
}

function declaration(value, seed = null) {
  const style = document.createElement("span").style;
  try {
    if (seed !== null) {
      style.setProperty(PROPERTY, seed);
    }
    const before = style.getPropertyValue(PROPERTY);
    style.setProperty(PROPERTY, value);
    const properties = Array.from({ length: style.length }, (_, index) => style.item(index));
    return {
      before,
      present: properties.includes(PROPERTY),
      serialized: style.getPropertyValue(PROPERTY),
      priority: style.getPropertyPriority(PROPERTY),
      properties,
      cssText: style.cssText,
      error: null,
    };
  } catch (error) {
    return { before: null, present: null, serialized: null, priority: null,
      properties: null, cssText: null, error: String(error) };
  }
}

function runProbe() {
  const controls = ["none", "uppercase", "probe-invalid-token", ""].map(value => ({
    value,
    supports: support(value),
    fresh: declaration(value),
    seeded: declaration(value, "uppercase"),
  }));
  const rows = probeInput.rows.map(row => ({
    id: row.id,
    value: row.value,
    supports: support(row.value),
    style: declaration(row.value),
    removal: row.value === "" ? declaration("", "uppercase") : null,
  }));
  latestResult = {
    schema: 1,
    protocol: "css-text-transform-normalized-v1",
    inputSha256: probeInput.inputSha256,
    oracleSha256: probeInput.oracleSha256,
    modelManifestSha256: probeInput.modelManifestSha256,
    capturedAt: new Date().toISOString(),
    browser: {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      appVersion: navigator.appVersion,
      suppliedBuildLabel: document.getElementById("build-label").value,
      href: location.href,
    },
    controls,
    rows,
  };
  const differences = rows.filter((row, index) => {
    const expected = probeInput.rows[index].expected;
    return row.supports.error !== null || row.style.error !== null ||
      row.supports.value !== expected || row.style.present !== expected ||
      (row.removal !== null && (row.removal.error !== null || row.removal.before === "" || row.removal.present || row.removal.serialized !== ""));
  });
  document.getElementById("status").textContent = `${rows.length} cases; ${differences.length} differing rows. Save JSON for strict validation.`;
  document.getElementById("output").textContent = JSON.stringify(differences, null, 2);
  document.getElementById("download").disabled = false;
  return latestResult;
}

function downloadResult() {
  if (!latestResult) {
    return;
  }
  const url = URL.createObjectURL(new Blob([JSON.stringify(latestResult, null, 2) + "\n"], { type: "application/json" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "text-transform-observations.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

document.getElementById("run").addEventListener("click", runProbe);
document.getElementById("download").addEventListener("click", downloadResult);
window.textTransformProbe = { run: runProbe, result: () => latestResult };
