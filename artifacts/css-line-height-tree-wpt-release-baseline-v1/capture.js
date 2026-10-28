async () => {
  const deadline = performance.now() + 15000;
  while (!window.__cssLineHeightResult && performance.now() < deadline) {
    await new Promise(resolve => setTimeout(resolve, 25));
  }
  if (!window.__cssLineHeightResult) throw new Error("WPT harness did not complete");
  return JSON.parse(JSON.stringify({
    url: location.href, userAgent: navigator.userAgent,
    result: window.__cssLineHeightResult,
    remainingFixtures: document.querySelectorAll("#container > *").length
  }));
}